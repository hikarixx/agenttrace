from ..storage.local import LocalStorage
from ..security.redactor import SecretRedactor
from ..recorder.core import Recorder
class AgentTrace:
    def __init__(self, db_path: str = "agenttrace.db", enable_redaction: bool = True):
        self.storage = LocalStorage(db_path=db_path)
        self.redactor = SecretRedactor() if enable_redaction else None
        self.recorder = Recorder(storage=self.storage, redactor=self.redactor)
    def run(self, agent: str, task: str, metadata: dict = None):
        return self.recorder.run(agent=agent, task=task, metadata=metadata)
    def tool(self, name: str):
        return self.recorder.tool(name)