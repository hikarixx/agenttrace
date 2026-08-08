# 1. Giới thiệu AgentTrace

Chào mừng bạn đến với **AgentTrace** - Hệ thống theo dõi và giám sát toàn diện dành cho các AI Agent (Hệ thống Trí tuệ nhân tạo Tác tử).

## Mục tiêu của AgentTrace

Khi các AI Agent ngày càng trở nên phức tạp, chúng thực hiện nhiều bước suy luận, sử dụng hàng loạt công cụ (Tools) và thực thi mã (Code) trong các môi trường khác nhau. Việc thiếu một công cụ giám sát hiệu quả sẽ dẫn đến:
- Không thể gỡ lỗi (debug) khi Agent đưa ra quyết định sai.
- Không thể kiểm soát các hành động nguy hiểm của Agent.
- Không biết Agent đang tiêu tốn bao nhiêu thời gian và tài nguyên cho mỗi tác vụ.

**AgentTrace** ra đời để giải quyết bài toán này. Nó hoạt động như một "hộp đen" (blackbox) ghi lại toàn bộ nhật ký chuyến bay của Agent.

## Các Tính Năng Nổi Bật

- **Event-Based Architecture**: Theo dõi các sự kiện theo dạng cây (Tree) giúp bạn dễ dàng xem được công cụ nào gọi công cụ nào (ví dụ: Agent gọi Tool A, Tool A gọi Tool B).
- **Security Redaction**: Tự động che giấu (redact) các thông tin nhạy cảm như API Key, mật khẩu, token trước khi lưu vào cơ sở dữ liệu.
- **Local-First SQLite Storage**: Toàn bộ dữ liệu được lưu cục bộ trên máy (Local) thông qua SQLite. Không yêu cầu cài đặt database phức tạp.
- **Dashboard Trực Quan**: Giao diện Web tích hợp sẵn để theo dõi tiến độ, xem chi tiết từng Run, và kiểm tra Execution Tree (cây thực thi).
- **Hỗ trợ đa nền tảng**: Dễ dàng tích hợp với các Framework phổ biến như LangChain, LlamaIndex, OpenAI, MCP, hoặc các IDE như Antigravity.

---

[Tiếp theo: Kiến trúc hệ thống (Architecture) →](02-architecture.md)
