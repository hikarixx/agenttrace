from typing import List, Dict, Any, Tuple
from .rules import PolicyRule, DangerousCommandRule
class PolicyEngine:
    def __init__(self, rules: List[PolicyRule] = None):
        self.rules = rules or [DangerousCommandRule()]
    def check_tool(self, tool_name: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        for rule in self.rules:
            violation = rule.evaluate(tool_name, args)
            if violation:
                return False, violation
        return True, ""