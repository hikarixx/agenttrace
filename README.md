<div align="center">
  <img src="https://via.placeholder.com/150x150.png?text=AgentTrace+Logo" alt="AgentTrace Logo" width="150" height="150" />
  <h1>AgentTrace Enterprise</h1>
  <p><em>Khung giám sát, ghi log và quản trị rủi ro toàn diện nhất dành cho Hệ sinh thái Trí tuệ nhân tạo Tác tử (AI Agents).</em></p>

  [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
  [![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
  [![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)]()
</div>

---

> [!IMPORTANT]
> AgentTrace không chỉ đơn thuần là một công cụ ghi log. Nó là một **Lớp bảo vệ (Shield)** và **Cỗ máy phân tích (Analytics Engine)** đặt giữa Agent của bạn và thế giới thực. Bất kể bạn đang sử dụng LLM framework nào, AgentTrace cung cấp khả năng hiển thị (visibility) xuyên suốt vòng đời của Agent.

## 🌟 Vì sao chọn AgentTrace?

Trong thế giới của AI Agent, các LLM liên tục gọi tool, sinh code, truy vấn database và duyệt web. Nếu không có AgentTrace:
- 🚫 Bạn không biết **tại sao** Agent lại đưa ra một quyết định sai lầm.
- 💸 Bạn không quản lý được **chi phí Token** đang đốt cháy tài khoản OpenAI/Anthropic.
- ☠️ Bạn đứng trước nguy cơ **lộ lọt dữ liệu** (API Keys) hoặc Agent vô tình chạy lệnh phá hoại (ví dụ `rm -rf`).

### Tính Năng Đỉnh Cao (Enterprise Features)
| Tính năng | Mô tả |
| :--- | :--- |
| **Bảo vệ Chủ động (Policy Engine)** | Chặn đứng mọi lệnh nguy hiểm (rm, mkfs, drop table) trước khi chúng kịp thi hành. |
| **Mã hóa Dữ liệu Nhạy cảm** | Tự động Redact (che giấu) API Key, Token, Mật khẩu khỏi Log. |
| **Đa Vũ Trụ Frameworks** | Sẵn sàng tương thích: *OpenAI, LangChain, LlamaIndex, CrewAI, AutoGen, MCP, Antigravity*. |
| **Đếm Tiền & Tokens** | Tích hợp biểu đồ Chart.js tính chi phí USD dựa trên số lượng Prompt/Completion Token. |
| **Kiến Trúc Bất Đồng Bộ (Async)** | Code không bị thắt cổ chai (bottleneck) khi phải xử lý hàng trăm request LLM đồng thời. |

---

## 🚀 Hướng Dẫn Cài Đặt Nhanh (Quick Start)

> [!TIP]
> Bạn có thể cài đặt AgentTrace trực tiếp từ mã nguồn hoặc qua môi trường ảo (Virtual Environment) để tránh xung đột thư viện.

**Bước 1: Cài đặt Core Package**
```bash
# Clone repository
git clone https://github.com/hikarixx/AgentTrace.git
cd AgentTrace

# Cài đặt qua pip (Editable mode)
pip install -e .
```

**Bước 2: Cài đặt Database Plugin (Tùy chọn)**
Nếu bạn muốn dùng PostgreSQL thay vì SQLite mặc định:
```bash
pip install psycopg2-binary
```

**Bước 3: Khởi động Web Dashboard**
```bash
agenttrace serve --port 8000
```
Truy cập `http://localhost:8000` trên trình duyệt để thưởng thức Giao diện Web siêu mượt mà!

---

## 📚 Mục lục Tài Liệu Chuyên Sâu (Deep-Dive Docs)

Khám phá toàn bộ quyền năng của AgentTrace qua bộ tài liệu chi tiết (được đầu tư kỹ lưỡng tới từng dòng code):

1. 📖 **[Giới thiệu & Triết lý thiết kế (Introduction)](docs/01-introduction.md)**
2. 🏗️ **[Kiến trúc Hệ thống Phân tán (Architecture)](docs/02-architecture.md)**
3. 💻 **[Hướng dẫn Lập trình Core SDK (Sync & Async)](docs/03-core-sdk-usage.md)**
4. 🔌 **[Tích hợp Multi-Agent Frameworks (Adapters)](docs/04-adapters-integration.md)**
5. 🛡️ **[Tích hợp Antigravity IDE & Hooks](docs/05-ide-integration.md)**
6. 📊 **[CLI, Báo cáo Kiểm toán (Audit) & Dashboard](docs/06-cli-and-dashboard.md)**
7. 🔒 **[Bảo mật, Policy Engine & Data Redaction](docs/07-security-and-redaction.md)**

---

<div align="center">
  <b>Được phát triển bằng ❤️ bởi Đội ngũ AgentTrace</b>
</div>
