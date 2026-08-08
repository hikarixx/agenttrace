from typing import Any, Callable, Dict
from .base import AgentAdapter
from ..recorder.core import TraceContext
class MCPProxyAdapter(AgentAdapter):
    def __init__(self, trace_run: TraceContext):
        super().__init__(trace_run)
    def wrap_mcp_client(self, mcp_client: Any) -> Any:
        if not hasattr(mcp_client, "call_tool"):
            return mcp_client
        original_call_tool = mcp_client.call_tool
        def wrapped_call_tool(name: str, arguments: dict, **kwargs):
            with self.trace_run.tool_call(name=f"mcp.{name}", input=arguments) as call:
                try:
                    result = original_call_tool(name, arguments, **kwargs)
                    safe_result = result
                    if hasattr(result, "model_dump"):
                        safe_result = result.model_dump()
                    elif hasattr(result, "__dict__"):
                        safe_result = result.__dict__
                    call.complete(safe_result)
                    return result
                except Exception as e:
                    call.fail(str(e))
                    raise
        mcp_client.call_tool = wrapped_call_tool
        return mcp_client