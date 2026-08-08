import re
from typing import Dict, Any, List

class PolicyRule:
    def evaluate(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Trả về lý do (reason) nếu vi phạm, trả về rỗng nếu an toàn."""
        pass

class DangerousCommandRule(PolicyRule):
    def __init__(self):
        self.dangerous_patterns = [
            r"rm\s+-rf",
            r"mkfs",
            r"dd\s+if=",
            r"shutdown",
            r"reboot"
        ]

    def evaluate(self, tool_name: str, args: Dict[str, Any]) -> str:
        if tool_name == "run_command":
            cmd = args.get("CommandLine", "")
            for pattern in self.dangerous_patterns:
                if re.search(pattern, cmd):
                    return f"Lệnh chứa từ khóa nguy hiểm bị cấm: {pattern}"
        return ""

class RestrictDomainRule(PolicyRule):
    def __init__(self, allowed_domains: List[str] = None):
        self.allowed_domains = allowed_domains or ["api.openai.com", "localhost"]

    def evaluate(self, tool_name: str, args: Dict[str, Any]) -> str:
        if tool_name == "fetch_url":
            url = args.get("url", "")
            if not any(domain in url for domain in self.allowed_domains):
                return f"Domain không nằm trong danh sách cho phép (Whitelist)."
        return ""
