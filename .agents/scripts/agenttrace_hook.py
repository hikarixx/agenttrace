import os
import sys
import json
import uuid
import urllib.request
def main():
    event_phase = sys.argv[1] if len(sys.argv) > 1 else "pre_tool"
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
    event_id = str(uuid.uuid4())
    event_payload = {
        "id": event_id,
        "run_id": run_id,
        "parent_id": None,
        "metadata": {"tool_name": tool_name}
    }
    if event_phase == "pre_tool":
        try:
            sys.path.insert(0, ".") 
            from agenttrace.policy import PolicyEngine
            engine = PolicyEngine()
            is_allowed, reason = engine.check_tool(tool_name, tool_args)
            if not is_allowed:
                print(json.dumps({"decision": "deny", "reason": reason}))
                return
        except Exception as e:
            pass 
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
    if event_phase == "pre_tool":
        print(json.dumps({"decision": "allow"}))
    else:
        print(json.dumps({}))
if __name__ == "__main__":
    main()