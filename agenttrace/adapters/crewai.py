from typing import Any
from .base import AgentAdapter
from ..recorder.core import TraceContext

class CrewAIAdapter(AgentAdapter):
    """
    Adapter cho hệ sinh thái CrewAI.
    Chèn hooks vào các Agent và Task của CrewAI.
    """
    def __init__(self, trace_run: TraceContext):
        super().__init__(trace_run)

    def attach(self, crew_instance: Any):
        """
        Gắn callback vào Crew instance.
        crew_instance: Đối tượng Crew() từ crewai.
        """
        original_kickoff = crew_instance.kickoff
        
        def wrapped_kickoff(*args, **kwargs):
            with self.trace_run.tool_call(name="crewai.kickoff", input={"tasks": [t.description for t in crew_instance.tasks]}) as call:
                try:
                    result = original_kickoff(*args, **kwargs)
                    call.complete({"final_output": str(result)})
                    return result
                except Exception as e:
                    call.fail(str(e))
                    raise
                    
        crew_instance.kickoff = wrapped_kickoff
        return crew_instance
