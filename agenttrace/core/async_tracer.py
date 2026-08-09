import asyncio
from functools import wraps
from typing import Callable, Any
from .tracer import Tracer
class AsyncTracer(Tracer):
    async def record_event_async(self, run_id: str, event_type: str, metadata: dict = None) -> str:
        return await asyncio.to_thread(self.start_event, run_id, event_type, metadata)
def async_trace_tool(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        tracer = getattr(self, "tracer", None)
        run_id = getattr(self, "current_run_id", None)
        if not tracer or not run_id:
            return await func(self, *args, **kwargs)
        event_id = tracer.start_event(run_id, "tool.started", {"tool_name": func.__name__, "args": args, "kwargs": kwargs})
        try:
            result = await func(self, *args, **kwargs)
            tracer.end_event(event_id, "completed", {"output": result})
            return result
        except Exception as e:
            tracer.end_event(event_id, "failed", {"error": str(e)})
            raise
    return wrapper