from typing import Dict, Any, Optional
from ..storage.local import LocalStorage

class ReplayEngine:
    """
    Cỗ máy thời gian (Time Machine) cho AgentTrace.
    Cho phép giả lập (mock) lại kết quả của các tool dựa trên lịch sử một Run cũ.
    """
    def __init__(self, run_id: str):
        self.storage = LocalStorage()
        self.run_id = run_id
        self.cached_events = self._load_run_events()

    def _load_run_events(self) -> Dict[str, Any]:
        """Tải toàn bộ events của run cũ vào bộ nhớ."""
        try:
            data = self.storage.export_run(self.run_id)
            event_map = {}
            for evt in data["events"]:
                if evt["type"] == "tool.completed":
                    # Tạo key bằng cách băm (hash) tool_name và input để match chính xác
                    meta = evt.get("metadata", {})
                    tool_name = meta.get("tool_name", "")
                    # Để đơn giản hóa trong bản MVP, chúng ta chỉ map theo tên tool
                    # Trong thực tế, cần hash cả arguments (input)
                    event_map[tool_name] = meta.get("output", {})
            return event_map
        except Exception:
            return {}

    def get_mock_result(self, tool_name: str, input_args: dict) -> Optional[Any]:
        """
        Lấy kết quả cũ từ Database. Trả về None nếu không tìm thấy (cache miss).
        """
        if tool_name in self.cached_events:
            print(f"[ReplayEngine] ⏪ Đã giả lập kết quả cho tool '{tool_name}' từ cache.")
            return self.cached_events[tool_name]
        return None
