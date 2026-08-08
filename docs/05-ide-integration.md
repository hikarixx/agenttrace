# 5. Tích hợp IDE (Antigravity Hooks)

AgentTrace có thể hoạt động dưới dạng backend giám sát cho **Antigravity IDE** hoặc CLI. Bằng cách sử dụng cơ chế Lifecycle Hooks, AgentTrace có thể bắt được toàn bộ lịch sử sử dụng Tool của Agent mà không cần can thiệp vào mã nguồn IDE.

## Yêu cầu
Bạn phải chạy AgentTrace Server trước khi sử dụng IDE:
```bash
agenttrace serve --port 8000
```

## 1. Cấu hình `hooks.json`

Tạo thư mục `.agents/` ở thư mục gốc của project (nơi mở IDE), và tạo file `.agents/hooks.json` với nội dung chuẩn:

```json
{
  "agenttrace": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "py scripts/agenttrace_hook.py pre_tool"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "py scripts/agenttrace_hook.py post_tool"
          }
        ]
      }
    ]
  }
}
```

> [!WARNING]
> Mặc định IDE lấy thư mục chứa `hooks.json` (tức là `.agents/`) làm thư mục làm việc (working directory). Do đó lệnh command phải là `py scripts/...` chứ không phải `py .agents/scripts/...`.

## 2. Script Python xử lý Hook

Tạo file `.agents/scripts/agenttrace_hook.py`. Kịch bản này làm nhiệm vụ:
- Đọc JSON đầu vào từ `STDIN` do IDE truyền tới.
- Phân tách từng `stepIdx` thành các Run con.
- Đẩy HTTP request `POST /api/runs` và `POST /api/events` tới AgentTrace Server.
- Trả về JSON hợp lệ (`{"decision": "allow"}`) ra `STDOUT` cho IDE đi tiếp.

```python
import sys
import json
import uuid
import urllib.request

def main():
    event_phase = sys.argv[1] if len(sys.argv) > 1 else "pre_tool"

    # Đọc dữ liệu JSON do Antigravity truyền qua STDIN
    input_data = sys.stdin.read() if not sys.stdin.isatty() else "{}"
    try:
        context = json.loads(input_data)
    except:
        context = {}

    conv_id = context.get("conversationId", str(uuid.uuid4()))
    step_idx = context.get("stepIdx", "0")
    run_id = f"{conv_id[:8]}-step-{step_idx}"
    
    tool_call = context.get("toolCall", {})
    tool_name = tool_call.get("name", "unknown_tool")
    tool_args = tool_call.get("args", {})

    event_payload = {
        "id": str(uuid.uuid4()),
        "run_id": run_id,
        "parent_id": None,
        "metadata": {"tool_name": tool_name}
    }

    if event_phase == "pre_tool":
        event_payload["type"] = "tool.started"
        event_payload["status"] = "started"
        event_payload["metadata"]["input"] = tool_args
    elif event_phase == "post_tool":
        event_payload["type"] = "tool.completed"
        if "error" in context and context["error"]:
            event_payload["status"] = "failed"
            event_payload["metadata"]["error"] = context["error"]
        else:
            event_payload["status"] = "completed"

    # Đảm bảo Run tồn tại
    run_payload = {
        "id": run_id,
        "agent": "Antigravity IDE",
        "task": f"Conv {conv_id[:8]} - Step {step_idx}"
    }
    try:
        req_run = urllib.request.Request(
            "http://127.0.0.1:8000/api/runs",
            data=json.dumps(run_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req_run)
    except: pass

    # Đẩy Event
    try:
        req_event = urllib.request.Request(
            "http://127.0.0.1:8000/api/events", 
            data=json.dumps(event_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req_event)
    except: pass

    # Trả lời IDE qua STDOUT
    if event_phase == "pre_tool":
        print(json.dumps({"decision": "allow"}))
    else:
        print(json.dumps({}))

if __name__ == "__main__":
    main()
```

---

[Tiếp theo: CLI và Web Dashboard →](06-cli-and-dashboard.md)
