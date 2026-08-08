from typing import Any, Dict, Optional, Union
from uuid import UUID
from .base import AgentAdapter
from ..recorder.core import TraceContext
class LangChainCallbackAdapter(AgentAdapter):
    def __init__(self, trace_run: TraceContext):
        super().__init__(trace_run)
        self.active_tool_calls: Dict[Union[str, UUID], Any] = {}
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        tool_name = serialized.get("name", "unknown_tool")
        context = self.trace_run.tool_call(
            name=tool_name, 
            input=inputs if inputs else {"input": input_str}
        )
        context.__enter__()
        self.active_tool_calls[run_id] = context
    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if run_id in self.active_tool_calls:
            context = self.active_tool_calls.pop(run_id)
            context.complete({"output": output})
            context.__exit__(None, None, None)
    def on_tool_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if run_id in self.active_tool_calls:
            context = self.active_tool_calls.pop(run_id)
            context.fail(str(error))
            context.__exit__(type(error), error, error.__traceback__)