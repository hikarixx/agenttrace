import sys
import json
import subprocess
import threading
import uuid
from typing import List
from ..core import Tracer
from ..policy import PolicyEngine

class MCPProxy:
    """
    Proxy cho giao thức Model Context Protocol (MCP).
    Đứng giữa Claude Desktop và Real MCP Server qua đường STDIO.
    """
    def __init__(self, command: List[str]):
        self.command = command
        self.tracer = Tracer()
        self.policy_engine = PolicyEngine()
        self.run_id = self.tracer.start_run(agent="Claude Desktop (MCP)", task="MCP Proxy Session")
        self.active_calls = {}

    def start(self):
        # Mở subprocess chạy real MCP server
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            bufsize=1
        )

        # Thread đọc từ MCP Server gửi lên Claude
        t1 = threading.Thread(target=self._forward_stdout, daemon=True)
        t1.start()

        # Main thread đọc từ Claude gửi xuống MCP Server
        self._forward_stdin()

    def _forward_stdin(self):
        """Đọc JSON-RPC từ Claude, kiểm duyệt, ghi log và gửi xuống MCP Server thật."""
        try:
            for line in sys.stdin:
                try:
                    payload = json.loads(line)
                    # Bắt sự kiện gọi Tool
                    if payload.get("method") == "tools/call":
                        req_id = payload.get("id")
                        params = payload.get("params", {})
                        tool_name = params.get("name", "unknown")
                        tool_args = params.get("arguments", {})

                        # 1. Kiểm duyệt bằng Policy Engine
                        is_allowed, reason = self.policy_engine.check_tool(tool_name, tool_args)
                        if not is_allowed:
                            error_response = {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "error": {
                                    "code": -32000,
                                    "message": f"Blocked by AgentTrace Policy: {reason}"
                                }
                            }
                            sys.stdout.write(json.dumps(error_response) + "\n")
                            sys.stdout.flush()
                            # Ghi log thất bại do policy
                            self.tracer.start_event(self.run_id, "tool.started", {"tool_name": tool_name, "input": tool_args, "status": "blocked_by_policy"})
                            continue

                        # 2. Ghi log hợp lệ
                        event_id = self.tracer.start_event(self.run_id, "tool.started", {"tool_name": tool_name, "input": tool_args})
                        self.active_calls[req_id] = event_id

                except json.JSONDecodeError:
                    pass

                # Forward xuống Subprocess
                self.process.stdin.write(line)
                self.process.stdin.flush()
        except KeyboardInterrupt:
            self.process.terminate()

    def _forward_stdout(self):
        """Đọc kết quả từ MCP Server thật, ghi log và gửi ngược lại Claude."""
        for line in self.process.stdout:
            try:
                payload = json.loads(line)
                req_id = payload.get("id")
                
                # Bắt kết quả của tool
                if req_id in self.active_calls:
                    event_id = self.active_calls.pop(req_id)
                    result_data = payload.get("result", {})
                    if "error" in payload:
                        self.tracer.end_event(event_id, "failed", {"error": payload["error"]})
                    else:
                        self.tracer.end_event(event_id, "completed", {"output": result_data})
            except json.JSONDecodeError:
                pass

            # Forward về Claude
            sys.stdout.write(line)
            sys.stdout.flush()
