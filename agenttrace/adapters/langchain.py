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
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        model_name = kwargs.get("invocation_params", {}).get("model_name", "unknown_llm")
        context = self.trace_run.tool_call(
            name=f"llm.{model_name}", 
            input={"prompts": prompts}
        )
        context.__enter__()
        self.active_tool_calls[run_id] = context
    def on_llm_end(
        self,
        response: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if run_id in self.active_tool_calls:
            context = self.active_tool_calls.pop(run_id)
            metrics = {}
            if hasattr(response, "llm_output") and response.llm_output:
                token_usage = response.llm_output.get("token_usage", {})
                if token_usage:
                    prompt_tokens = token_usage.get("prompt_tokens", 0)
                    completion_tokens = token_usage.get("completion_tokens", 0)
                    total_tokens = token_usage.get("total_tokens", 0)
                    cost = (prompt_tokens * 0.005 / 1000) + (completion_tokens * 0.015 / 1000)
                    metrics = {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "estimated_cost_usd": round(cost, 5)
                    }
            output_text = ""
            if hasattr(response, "generations") and response.generations:
                output_text = response.generations[0][0].text if len(response.generations[0]) > 0 else ""
            output_data = {"output": output_text}
            if metrics:
                output_data["metrics"] = metrics
            context.complete(output_data)
            context.__exit__(None, None, None)
    def on_llm_error(
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