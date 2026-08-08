import json
import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from ..models.base import Run, Event, RunStatus, EventType, EventStatus
from .base import Storage
from contextlib import closing
class LocalStorage(Storage):
    def __init__(self, db_path: str = "agenttrace.db"):
        self.db_path = db_path
        self._init_db()
    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    def _init_db(self):
        with closing(self._get_conn()) as conn:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    agent TEXT,
                    task TEXT,
                    status TEXT,
                    started_at TEXT,
                    ended_at TEXT,
                    duration REAL,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    run_id TEXT,
                    parent_id TEXT,
                    type TEXT,
                    timestamp TEXT,
                    duration REAL,
                    status TEXT,
                    metadata TEXT,
                    FOREIGN KEY(run_id) REFERENCES runs(id)
                )
            """)
            conn.commit()
    def create_run(self, run: Run) -> None:
        with closing(self._get_conn()) as conn:
            with conn:
                conn.execute(
                    "INSERT INTO runs (id, agent, task, status, started_at, ended_at, duration, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        run.id,
                        run.agent,
                        run.task,
                        run.status.value,
                        run.started_at.isoformat(),
                        run.ended_at.isoformat() if run.ended_at else None,
                        run.duration,
                        json.dumps(run.metadata)
                    )
                )
    def update_run(self, run: Run) -> None:
        with closing(self._get_conn()) as conn:
            with conn:
                conn.execute(
                    "UPDATE runs SET status = ?, ended_at = ?, duration = ?, metadata = ? WHERE id = ?",
                    (
                        run.status.value,
                        run.ended_at.isoformat() if run.ended_at else None,
                        run.duration,
                        json.dumps(run.metadata),
                        run.id
                    )
                )
    def get_run(self, run_id: str) -> Optional[Run]:
        with closing(self._get_conn()) as conn:
            row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
            if not row:
                return None
            return Run(
                id=row["id"],
                agent=row["agent"],
                task=row["task"],
                status=RunStatus(row["status"]),
                started_at=datetime.fromisoformat(row["started_at"]),
                ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
                duration=row["duration"],
                metadata=json.loads(row["metadata"])
            )
    def list_runs(self, limit: int = 100, offset: int = 0) -> List[Run]:
        runs = []
        with closing(self._get_conn()) as conn:
            rows = conn.execute("SELECT * FROM runs ORDER BY started_at DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
            for row in rows:
                runs.append(Run(
                    id=row["id"],
                    agent=row["agent"],
                    task=row["task"],
                    status=RunStatus(row["status"]),
                    started_at=datetime.fromisoformat(row["started_at"]),
                    ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
                    duration=row["duration"],
                    metadata=json.loads(row["metadata"])
                ))
        return runs
    def create_event(self, event: Event) -> None:
        with closing(self._get_conn()) as conn:
            with conn:
                conn.execute(
                    "INSERT INTO events (id, run_id, parent_id, type, timestamp, duration, status, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        event.id,
                        event.run_id,
                        event.parent_id,
                        event.type.value,
                        event.timestamp.isoformat(),
                        event.duration,
                        event.status.value,
                        json.dumps(event.metadata)
                    )
                )
    def get_events(self, run_id: str) -> List[Event]:
        events = []
        with closing(self._get_conn()) as conn:
            rows = conn.execute("SELECT * FROM events WHERE run_id = ? ORDER BY timestamp ASC", (run_id,)).fetchall()
            for row in rows:
                events.append(Event(
                    id=row["id"],
                    run_id=row["run_id"],
                    parent_id=row["parent_id"],
                    type=EventType(row["type"]),
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    duration=row["duration"],
                    status=EventStatus(row["status"]),
                    metadata=json.loads(row["metadata"])
                ))
        return events
    def delete_run(self, run_id: str) -> None:
        with closing(self._get_conn()) as conn:
            with conn:
                conn.execute("DELETE FROM events WHERE run_id = ?", (run_id,))
                conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
    def export_run(self, run_id: str) -> dict:
        run = self.get_run(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")
        events = self.get_events(run_id)
        event_dicts = [e.model_dump(mode='json') for e in events]
        events_by_id = {e["id"]: e for e in event_dicts}
        tree = []
        for e in event_dicts:
            e["children"] = []
        for e in event_dicts:
            if e["parent_id"] and e["parent_id"] in events_by_id:
                events_by_id[e["parent_id"]]["children"].append(e)
            else:
                tree.append(e)
        return {
            "run": run.model_dump(mode='json'),
            "events": event_dicts,
            "tree": tree
        }