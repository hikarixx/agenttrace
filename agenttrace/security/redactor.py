import re
from typing import Any, Dict, List, Union
class SecretRedactor:
    def __init__(self):
        self.redact_string = "[REDACTED]"
        self.patterns = [
            re.compile(r'(?i)(?:api_key|apikey|api-key|secret|password|passwd|pwd|token|bearer|jwt)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]+)["\']?'),
            re.compile(r'(?i)bearer\s+([a-zA-Z0-9_\-\.]+)'),
            re.compile(r'ey[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'), 
            re.compile(r'(?i)sk-[a-zA-Z0-9]{32,}') 
        ]
        self.sensitive_keys = {
            'password', 'secret', 'token', 'api_key', 'apikey', 'api-key',
            'access_token', 'refresh_token', 'auth', 'credentials', 'jwt'
        }
    def _redact_string(self, text: str) -> str:
        redacted_text = text
        for pattern in self.patterns:
            def replace_match(match):
                if match.groups():
                    full_match = match.group(0)
                    secret = match.group(1)
                    return full_match.replace(secret, self.redact_string)
                return self.redact_string
            redacted_text = pattern.sub(replace_match, redacted_text)
        return redacted_text
    def redact(self, data: Any) -> Any:
        if isinstance(data, str):
            return self._redact_string(data)
        elif isinstance(data, dict):
            return self._redact_dict(data)
        elif isinstance(data, list):
            return [self.redact(item) for item in data]
        return data
    def _redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        redacted = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_keys):
                redacted[key] = self.redact_string
            else:
                redacted[key] = self.redact(value)
        return redacted