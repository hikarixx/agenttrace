from typing import Dict, Any, Optional
from ..storage.local import LocalStorage
class ReplayEngine:
    def __init__(self, run_id: str):
        self.storage = LocalStorage()
        self.run_id = run_id
        self.cached_events = self._load_run_events()
    def _load_run_events(self) -> Dict[str, Any]:
        try:
            data = self.storage.export_run(self.run_id)
            event_map = {}
            for evt in data["events"]:
                if evt["type"] == "tool.completed":
                    meta = evt.get("metadata", {})
                    tool_name = meta.get("tool_name", "")
                    event_map[tool_name] = meta.get("output", {})
            return event_map
        except Exception:
            return {}
    def get_mock_result(self, tool_name: str, input_args: dict) -> Optional[Any]:
        if tool_name in self.cached_events:
            print(f"[ReplayEngine] ⏪ Đã giả lập kết quả cho tool '{tool_name}' từ cache.")
            return self.cached_events[tool_name]
        return None