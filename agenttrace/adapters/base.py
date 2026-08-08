from abc import ABC
from ..recorder.core import TraceContext
class AgentAdapter(ABC):
    def __init__(self, trace_run: TraceContext):
        self.trace_run = trace_run
class ToolAdapter(ABC):
    pass