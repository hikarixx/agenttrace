import os
import sys
import json
import uuid
import urllib.request

def main():
    # Antigravity truyền event phase qua tham số dòng lệnh
    event_phase = sys.argv[1] if len(sys.argv) > 1 else "pre_tool"

    # Antigravity truyền dữ liệu context qua STDIN
    input_data = sys.stdin.read() if not sys.stdin.isatty() else "{}"
    try:
        context = json.loads(input_data)
    except:
        context = {}

    conv_id = context.get("conversationId", str(uuid.uuid4()))
    step_idx = context.get("stepIdx", "0")
    # Tạo Run ID mới cho mỗi step (thay vì gộp chung cả Conversation)
    run_id = f"{conv_id[:8]}-step-{step_idx}"
    
    # Lấy thông tin tool từ STDIN (Antigravity cung cấp trường toolCall)
    tool_call = context.get("toolCall", {})
    tool_name = tool_call.get("name", "unknown_tool")
    tool_args = tool_call.get("args", {})

    event_id = str(uuid.uuid4())
    event_payload = {
        "id": event_id,
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
        # Bắt lỗi nếu tool thất bại
        if "error" in context and context["error"]:
            event_payload["status"] = "failed"
            event_payload["metadata"]["error"] = context["error"]
        else:
            event_payload["status"] = "completed"
            
        # Lưu ý: Antigravity không gửi output của tool trong post_tool hook hiện tại.

    # Đảm bảo Run đã tồn tại
    run_payload = {
        "id": run_id,
        "agent": "Antigravity IDE",
        "task": "Conversation " + run_id[:8]
    }
    try:
        req_run = urllib.request.Request(
            "http://127.0.0.1:8000/api/runs",
            data=json.dumps(run_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req_run)
    except Exception:
        pass

    # Gửi Event tới AgentTrace Server
    try:
        req_event = urllib.request.Request(
            "http://127.0.0.1:8000/api/events", 
            data=json.dumps(event_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req_event)
    except Exception:
        pass

    # BẮT BUỘC: Trả về JSON hợp lệ cho Antigravity qua STDOUT
    if event_phase == "pre_tool":
        print(json.dumps({"decision": "allow"}))
    else:
        print(json.dumps({}))

if __name__ == "__main__":
    main()