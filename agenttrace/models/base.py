from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
def generate_uuid() -> str:
    return str(uuid.uuid4())
def utc_now() -> datetime:
    return datetime.now(timezone.utc)
class RunStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
class Run(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    agent: str
    task: str
    status: RunStatus = RunStatus.STARTED
    started_at: datetime = Field(default_factory=utc_now)
    ended_at: Optional[datetime] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
class EventType(str, Enum):
    RUN_STARTED = "run.started"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    TOOL_STARTED = "tool.started"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"
    DECISION_CREATED = "decision.created"
    FILE_READ = "file.read"
    FILE_WRITE = "file.write"
    COMMAND_STARTED = "command.started"
    COMMAND_COMPLETED = "command.completed"
    COMMAND_FAILED = "command.failed"
    API_REQUEST = "api.request"
    API_RESPONSE = "api.response"
    ERROR = "error"
    ARTIFACT_CREATED = "artifact.created"
class EventStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    INFO = "info"
class Event(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    run_id: str
    parent_id: Optional[str] = None
    type: EventType
    timestamp: datetime = Field(default_factory=utc_now)
    duration: Optional[float] = None
    status: EventStatus
    metadata: Dict[str, Any] = Field(default_factory=dict)
class ToolCall(BaseModel):
    tool_name: str
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    status: EventStatus = EventStatus.STARTED
    error: Optional[str] = None
class Decision(BaseModel):
    summary: str
    evidence: str
    next_action: str
class Error(BaseModel):
    message: str
    traceback: Optional[str] = None
class Artifact(BaseModel):
    type: str
    path: str
    hash: Optional[str] = None
    size: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)