from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.base import Run, Event
class Storage(ABC):
    @abstractmethod
    def create_run(self, run: Run) -> None:
        pass
    @abstractmethod
    def update_run(self, run: Run) -> None:
        pass
    @abstractmethod
    def get_run(self, run_id: str) -> Optional[Run]:
        pass
    @abstractmethod
    def list_runs(self, limit: int = 100, offset: int = 0) -> List[Run]:
        pass
    @abstractmethod
    def create_event(self, event: Event) -> None:
        pass
    @abstractmethod
    def get_events(self, run_id: str) -> List[Event]:
        pass
    @abstractmethod
    def delete_run(self, run_id: str) -> None:
        pass
    @abstractmethod
    def export_run(self, run_id: str) -> dict:
        pass