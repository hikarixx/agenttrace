# Chương 7: Bảo Mật, Policy Engine & Data Redaction

Hệ thống AgentTrace không đơn thuần chỉ ghi lại cái Agent làm. Nó đóng vai trò làm **Người bảo vệ (Guardian)** cho toàn bộ hệ thống của bạn trước những rủi ro bảo mật tàn khốc nhất.

---

## 1. Policy Engine (Lá Chắn Thời Gian Thực)

LLM có thể sinh ra "Ảo giác" (Hallucination). Chuyện gì xảy ra nếu bạn cấp quyền cho nó chạy Terminal và nó bỗng dưng gõ `rm -rf /`?

### Cách Policy Engine Hoạt Động
Policy Engine là một mô-đun chạy ở tầng **Pre-Tool** (Trước khi Tool chạy). Nó kiểm duyệt (Inspect) `tool_args`.

```mermaid
graph LR
    A[Agent Input] --> B(PolicyEngine)
    B -->|Check Rules| C{Is Safe?}
    C -- Yes --> D[Execute Tool]
    C -- No --> E((DENY & BLOCK))
    
    style E fill:#f00,stroke:#333,stroke-width:4px,color:#fff
```

### Các Bộ Luật (Rules) Có Sẵn

1. **`DangerousCommandRule`**:
   - Dùng Regex tìm các mẫu phá hoại trong Command Line.
   - Ví dụ cấm: `rm -rf`, `mkfs`, `reboot`, `shutdown`, `drop table`.
2. **`RestrictDomainRule`**:
   - Chỉ cho phép LLM gọi API (fetch) tới các Domain đã được cấp phép (Whitelist).
   - Ngăn chặn Agent vô tình tải mã độc từ một máy chủ vô danh.

---

## 2. Security Redactor (Che Dấu Dữ Liệu Nhạy Cảm)

Khi Agent gọi OpenAI, trong Header của Request luôn có một chuỗi `Bearer sk-xxxxxxxxxx`. Nếu bạn lưu nó vào DB `agenttrace.db`, và người khác (hoặc Hacker) lấy được DB đó, công ty bạn sẽ thiệt hại nặng nề.

> [!CAUTION]
> **Zero Trust Logging**
> AgentTrace mặc định coi MỌI luồng dữ liệu (Input, Output, Error Traceback) đều có thể chứa thông tin mật.

### Thuật toán Lọc (Redaction Algorithm)

`SecurityRedactor` nằm ở phần lõi (`agenttrace.security`). Thuật toán của nó:
1. Nạp sẵn 50+ Regex Pattern đại diện cho API Key của OpenAI, AWS, Anthropic, GCP, Stripe...
2. Chặn toàn bộ `Event.metadata` trước khi Serialize thành chuỗi JSON để đưa xuống Storage.
3. Duyệt đệ quy (Recursive Traverse) qua toàn bộ cây Dictionary.
4. Phát hiện chuỗi khớp -> Ghi đè bằng `[REDACTED]`.

**Ví dụ Code (Trước / Sau):**

```diff
  # Before Redaction (Bị Lộ)
  {
-     "authorization": "Bearer sk-proj-ABCD12345XYZ",
      "user_email": "ceo@company.com"
  }

  # After Redaction (An toàn)
  {
+     "authorization": "[REDACTED]",
      "user_email": "ceo@company.com"
  }
```

Bạn có thể tự định nghĩa thêm Regex độc quyền của công ty mình bằng cách gọi `redactor.add_pattern(r"MY_COMPANY_SECRET_[a-zA-Z0-9]+")`.

---
*Cảm ơn bạn đã đọc hết cẩm nang AgentTrace. Chúc bạn xây dựng được những Agent an toàn và siêu việt nhất!*
