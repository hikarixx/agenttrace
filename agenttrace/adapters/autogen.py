from typing import Any
from .base import AgentAdapter
from ..recorder.core import TraceContext

class AutoGenAdapter(AgentAdapter):
    """
    Adapter cho Microsoft AutoGen.
    Theo dõi quá trình giao tiếp (chat) giữa các Agents.
    """
    def __init__(self, trace_run: TraceContext):
        super().__init__(trace_run)

    def attach(self, agent: Any):
        """
        Gắn hook vào hàm initiate_chat của AutoGen UserProxyAgent / AssistantAgent
        """
        original_initiate = agent.initiate_chat
        
        def wrapped_initiate_chat(recipient, message=None, **kwargs):
            with self.trace_run.tool_call(name="autogen.initiate_chat", input={"recipient": recipient.name, "message": message}) as call:
                try:
                    result = original_initiate(recipient, message=message, **kwargs)
                    # AutoGen thường trả về ChatResult
                    call.complete({"chat_history_summary": str(result.summary) if hasattr(result, "summary") else str(result)})
                    return result
                except Exception as e:
                    call.fail(str(e))
                    raise
                    
        agent.initiate_chat = wrapped_initiate_chat
        return agent
