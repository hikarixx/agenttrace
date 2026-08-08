import json
import traceback
from typing import Any, Callable, Dict, Optional, TypeVar
from functools import wraps
from datetime import datetime
import time
from ..models.base import Run, Event, EventType, EventStatus, RunStatus, utc_now
from ..storage.base import Storage
from ..security.redactor import SecretRedactor
F = TypeVar('F', bound=Callable[..., Any])
class TraceContext:
    def __init__(self, recorder: 'Recorder', run: Run):
        self.recorder = recorder
        self.run = run
        self.current_event_id: Optional[str] = None
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.run.status = RunStatus.FAILED
            self.run.metadata['error'] = str(exc_val)
            self.run.metadata['traceback'] = "".join(traceback.format_tb(exc_tb))
        else:
            self.run.status = RunStatus.COMPLETED
        self.run.ended_at = utc_now()
        self.run.duration = (self.run.ended_at - self.run.started_at).total_seconds()
        self.recorder.storage.update_run(self.run)
        event_type = EventType.RUN_FAILED if exc_type else EventType.RUN_COMPLETED
        event_status = EventStatus.FAILED if exc_type else EventStatus.COMPLETED
        self.recorder.record_event(
            run_id=self.run.id,
            parent_id=None,
            type=event_type,
            status=event_status,
            metadata=self.run.metadata
        )
    def tool(self, name: str, input: dict, output: Optional[dict] = None, error: Optional[str] = None) -> None:
        metadata = {
            "tool_name": name,
            "input": self.recorder.redactor.redact(input)
        }
        if output:
            metadata["output"] = self.recorder.redactor.redact(output)
        if error:
            metadata["error"] = error
        status = EventStatus.FAILED if error else EventStatus.COMPLETED
        event_type = EventType.TOOL_FAILED if error else EventType.TOOL_COMPLETED
        self.recorder.record_event(
            run_id=self.run.id,
            parent_id=self.current_event_id,
            type=event_type,
            status=status,
            metadata=metadata
        )
    def tool_call(self, name: str, input: dict):
        return ToolCallContext(self, name, input)
class ToolCallContext:
    def __init__(self, trace_context: TraceContext, name: str, input: dict):
        self.trace = trace_context
        self.name = name
        self.input = input
        self.started_at = utc_now()
        self.event_id = None
        self.parent_id_before = self.trace.current_event_id
    def __enter__(self):
        event = self.trace.recorder.record_event(
            run_id=self.trace.run.id,
            parent_id=self.parent_id_before,
            type=EventType.TOOL_STARTED,
            status=EventStatus.STARTED,
            metadata={
                "tool_name": self.name,
                "input": self.trace.recorder.redactor.redact(self.input)
            }
        )
        self.event_id = event.id
        self.trace.current_event_id = self.event_id
        return self
    def complete(self, output: Any):
        self._finish(EventType.TOOL_COMPLETED, EventStatus.COMPLETED, {"output": self.trace.recorder.redactor.redact(output)})
        self._finished = True
    def fail(self, error: str):
        self._finish(EventType.TOOL_FAILED, EventStatus.FAILED, {"error": error})
        self._finished = True
    def _finish(self, event_type: EventType, status: EventStatus, extra_metadata: dict):
        ended_at = utc_now()
        duration = (ended_at - self.started_at).total_seconds()
        metadata = {
            "tool_name": self.name,
            "input": self.trace.recorder.redactor.redact(self.input)
        }
        metadata.update(extra_metadata)
        self.trace.recorder.record_event(
            run_id=self.trace.run.id,
            parent_id=self.parent_id_before,
            type=event_type,
            status=status,
            metadata=metadata,
            duration=duration
        )
        self.trace.current_event_id = self.parent_id_before
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            error_msg = str(exc_val)
            self.fail(error_msg)
        elif getattr(self, '_finished', False) is False:
            self.fail("Tool call context exited without completion")
        self.trace.current_event_id = self.parent_id_before
class Recorder:
    def __init__(self, storage: Storage, redactor: SecretRedactor):
        self.storage = storage
        self.redactor = redactor
        self.current_trace: Optional[TraceContext] = None
    def run(self, agent: str, task: str, metadata: Optional[dict] = None) -> TraceContext:
        run_obj = Run(
            agent=agent,
            task=task,
            metadata=self.redactor.redact(metadata) if metadata else {}
        )
        self.storage.create_run(run_obj)
        self.record_event(
            run_id=run_obj.id,
            parent_id=None,
            type=EventType.RUN_STARTED,
            status=EventStatus.STARTED,
            metadata={}
        )
        self.current_trace = TraceContext(self, run_obj)
        return self.current_trace
    def record_event(self, run_id: str, parent_id: Optional[str], type: EventType, status: EventStatus, metadata: dict, duration: Optional[float] = None) -> Event:
        event = Event(
            run_id=run_id,
            parent_id=parent_id,
            type=type,
            status=status,
            metadata=metadata,
            duration=duration
        )
        self.storage.create_event(event)
        return event
    def tool(self, name: str) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.current_trace:
                    return func(*args, **kwargs)
                safe_input = {}
                if args: safe_input["args"] = [str(a) for a in args]
                if kwargs: safe_input["kwargs"] = {k: str(v) for k, v in kwargs.items()}
                with self.current_trace.tool_call(name=name, input=safe_input) as call:
                    try:
                        result = func(*args, **kwargs)
                        try:
                            json.dumps(result)
                            safe_output = result
                        except (TypeError, ValueError):
                            safe_output = str(result)
                        call.complete(safe_output)
                        call._finished = True
                        return result
                    except Exception as e:
                        call._finished = True
                        raise
            return wrapper
        return decorator