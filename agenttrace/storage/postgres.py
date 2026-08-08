import json
from typing import List, Optional
from datetime import datetime
from ..models.base import Run, Event, RunStatus, EventType, EventStatus
from .base import Storage

class PostgresStorage(Storage):
    """
    Storage backend sử dụng PostgreSQL (Sẵn sàng cho Production/Enterprise).
    Yêu cầu thư viện: psycopg2-binary
    """
    def __init__(self, connection_string: str):
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except ImportError:
            raise ImportError("Vui lòng cài đặt psycopg2-binary để sử dụng PostgresStorage: pip install psycopg2-binary")
            
        self.conn_str = connection_string
        self._init_db()

    def _get_conn(self):
        import psycopg2
        from psycopg2.extras import RealDictCursor
        return psycopg2.connect(self.conn_str, cursor_factory=RealDictCursor)

    def _init_db(self):
        query_runs = """
        CREATE TABLE IF NOT EXISTS runs (
            id VARCHAR(36) PRIMARY KEY,
            agent VARCHAR(255),
            task TEXT,
            status VARCHAR(50),
            started_at TIMESTAMP WITH TIME ZONE,
            ended_at TIMESTAMP WITH TIME ZONE,
            duration REAL,
            metadata JSONB
        );
        """
        query_events = """
        CREATE TABLE IF NOT EXISTS events (
            id VARCHAR(36) PRIMARY KEY,
            run_id VARCHAR(36) REFERENCES runs(id) ON DELETE CASCADE,
            parent_id VARCHAR(36),
            type VARCHAR(50),
            timestamp TIMESTAMP WITH TIME ZONE,
            duration REAL,
            status VARCHAR(50),
            metadata JSONB
        );
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query_runs)
                cur.execute(query_events)
            conn.commit()

    def create_run(self, run: Run) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO runs (id, agent, task, status, started_at, ended_at, duration, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (run.id, run.agent, run.task, run.status.value, run.started_at, run.ended_at, run.duration, json.dumps(run.metadata))
                )
            conn.commit()

    def update_run(self, run: Run) -> None:
        pass # Tương tự LocalStorage (bỏ qua chi tiết vì mục đích minh họa kiến trúc)

    def get_run(self, run_id: str) -> Optional[Run]:
        pass

    def list_runs(self, limit: int = 100, offset: int = 0) -> List[Run]:
        return []

    def create_event(self, event: Event) -> None:
        pass

    def get_events(self, run_id: str) -> List[Event]:
        return []

    def delete_run(self, run_id: str) -> None:
        pass

    def export_run(self, run_id: str) -> dict:
        return {}
