from typing import Any, Callable, Dict, List
from .base import AgentAdapter
from ..recorder.core import TraceContext
class OpenAIChatAdapter(AgentAdapter):
    def __init__(self, trace_run: TraceContext):
        super().__init__(trace_run)
    def wrap_client(self, client: Any) -> Any:
        original_create = client.chat.completions.create
        def wrapped_create(*args, **kwargs):
            with self.trace_run.tool_call(name="openai.chat.completions.create", input={"kwargs": kwargs}) as call:
                try:
                    response = original_create(*args, **kwargs)
                    resp_dict = response.model_dump() if hasattr(response, 'model_dump') else str(response)
                    call.complete(resp_dict)
                    if hasattr(response, 'choices') and response.choices:
                        message = response.choices[0].message
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            for tc in message.tool_calls:
                                self.trace_run.recorder.record_event(
                                    run_id=self.trace_run.run.id,
                                    parent_id=self.trace_run.current_event_id,
                                    type=self.trace_run.recorder.current_trace.run.status, 
                                    status="info", 
                                    metadata={
                                        "tool_name": tc.function.name,
                                        "input": tc.function.arguments,
                                        "type": "model_decision"
                                    }
                                )
                    return response
                except Exception as e:
                    call.fail(str(e))
                    raise
        client.chat.completions.create = wrapped_create
        return client