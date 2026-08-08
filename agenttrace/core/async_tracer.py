import asyncio
from functools import wraps
from typing import Callable, Any
from .tracer import Tracer

class AsyncTracer(Tracer):
    """
    Tracer hỗ trợ bất đồng bộ (async) cho các hệ thống LLM hiện đại.
    Mở rộng từ lớp Tracer gốc nhưng xử lý các hàm async an toàn.
    """
    
    async def record_event_async(self, run_id: str, event_type: str, metadata: dict = None) -> str:
        # Giả lập thao tác DB không đồng bộ (nếu storage hỗ trợ)
        # Tạm thời gọi hàm đồng bộ thông qua asyncio.to_thread
        return await asyncio.to_thread(self.start_event, run_id, event_type, metadata)

def async_trace_tool(func: Callable) -> Callable:
    """Decorator để trace các async tool"""
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
