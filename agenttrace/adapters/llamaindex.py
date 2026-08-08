from typing import Any, Dict, Optional
from uuid import UUID
from .base import AgentAdapter
from ..recorder.core import TraceContext
class LlamaIndexCallbackAdapter(AgentAdapter):
    def __init__(self, trace_run: TraceContext):
        super().__init__(trace_run)
        self.active_events = {}
    def on_event_start(
        self,
        event_type: Any,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        event_name = str(event_type).split('.')[-1] if event_type else "unknown"
        context = self.trace_run.tool_call(
            name=f"llama_index.{event_name}", 
            input=payload if payload else {}
        )
        context.__enter__()
        self.active_events[event_id] = context
        return event_id
    def on_event_end(
        self,
        event_type: Any,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        if event_id in self.active_events:
            context = self.active_events.pop(event_id)
            context.complete(payload if payload else {})
            context.__exit__(None, None, None)