from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from typing import List, Any
from ..storage.local import LocalStorage
from ..models.base import Run, Event
app = FastAPI(title="AgentTrace Dashboard")
storage = LocalStorage()
@app.post("/api/runs")
def create_run(run: Run):
    storage.create_run(run)
    return {"status": "success", "id": run.id}
@app.post("/api/events")
def create_event(event: Event):
    storage.create_event(event)
    return {"status": "success", "id": event.id}
@app.get("/api/runs")
def list_runs(limit: int = 100, offset: int = 0):
    runs = storage.list_runs(limit=limit, offset=offset)
    return [run.model_dump(mode='json') for run in runs]
@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run = storage.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.model_dump(mode='json')
@app.get("/api/runs/{run_id}/events")
def get_run_events(run_id: str):
    events = storage.get_events(run_id)
    return [event.model_dump(mode='json') for event in events]
@app.get("/api/runs/{run_id}/tree")
def get_run_tree(run_id: str):
    try:
        data = storage.export_run(run_id)
        return data["tree"]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
@app.get("/api/runs/{run_id}/export")
def export_run(run_id: str):
    try:
        return storage.export_run(run_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
@app.get("/")
def index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>AgentTrace Dashboard API</h1><p>Frontend not found. Make sure to build/copy static files.</p>")