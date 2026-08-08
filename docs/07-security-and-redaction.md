# 7. Bảo mật và Che giấu dữ liệu (Security & Redaction)

Khi các AI Agent giao tiếp với các API bên ngoài, chúng thường xuyên phải trao đổi thông tin nhạy cảm như `OPENAI_API_KEY`, mật khẩu Database, hoặc Secret Tokens. 

Việc lưu các thông tin này vào cơ sở dữ liệu `agenttrace.db` tiềm ẩn nguy cơ lộ lọt dữ liệu. Do đó, AgentTrace tích hợp sẵn hệ thống **Security Redactor**.

## Cách Hoạt Động

Lớp `SecurityRedactor` nằm ở phần lõi (`agenttrace.security`) thực hiện việc chặn (intercept) mọi dữ liệu trước khi chúng được đưa xuống Storage Layer.
Nó sử dụng các biểu thức chính quy (Regex) kết hợp với thuật toán dò tìm để tự động phát hiện:
- API Keys (OpenAI, Anthropic, AWS, v.v...)
- Bearer Tokens
- Mật khẩu dạng chuỗi
- Email và các PII (Personal Identifiable Information) nếu được cấu hình.

Mọi chuỗi bị phát hiện sẽ được ghi đè bằng `[REDACTED]`.

## Cách Cấu Hình

Security Redactor được kích hoạt tự động theo mặc định. Tuy nhiên, bạn có thể tự thêm các mẫu (patterns) nhạy cảm riêng rẽ của ứng dụng:

```python
from agenttrace.security import SecurityRedactor
from agenttrace.core import Tracer

redactor = SecurityRedactor()
redactor.add_pattern(r"MY_COMPANY_SECRET_[a-zA-Z0-9]+")

# Truyền redactor vào Tracer
tracer = Tracer(db_path="secure_logs.db", redactor=redactor)
```

> [!IMPORTANT]
> AgentTrace tự động lọc trên cả bộ giá trị của JSON Input và Output, cho nên dù Tool trả về lỗi có chứa mã bảo mật, hệ thống vẫn đảm bảo an toàn.
