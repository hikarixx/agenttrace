# AgentTrace

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**AgentTrace** là một framework mạnh mẽ giúp ghi log, theo dõi (trace) và giám sát hoạt động của các hệ thống AI Agent (LLMs). Nó hỗ trợ ghi lại quá trình Agent sử dụng công cụ (Tool Use), quản lý sự kiện theo dạng cây (Execution Tree) và bảo mật dữ liệu nhạy cảm.

## Tính năng chính

- Theo dõi tự động với Decorator.
- Hỗ trợ đa thư viện: **OpenAI**, **LangChain**, **LlamaIndex**, **MCP**.
- Hỗ trợ IDE: **Antigravity**.
- Storage cục bộ (Local SQLite) nhanh nhẹn.
- Giao diện Web Dashboard trực quan và CLI tiện lợi.

## Bắt đầu nhanh (Quick Start)

1. Cài đặt package:
```bash
pip install -e .
```

2. Khởi động Web Dashboard (cổng mặc định 8000):
```bash
agenttrace serve --port 8000
```

3. Mở trình duyệt và truy cập `http://localhost:8000`.

## Tài liệu chi tiết

Vui lòng tham khảo bộ tài liệu chi tiết trong thư mục `docs/`:

1. [Giới thiệu AgentTrace](docs/01-introduction.md)
2. [Kiến trúc hệ thống](docs/02-architecture.md)
3. [Sử dụng Core SDK](docs/03-core-sdk-usage.md)
4. [Tích hợp Adapters](docs/04-adapters-integration.md)
5. [Tích hợp IDE (Antigravity Hooks)](docs/05-ide-integration.md)
6. [CLI và Web Dashboard](docs/06-cli-and-dashboard.md)
7. [Bảo mật và Che giấu dữ liệu](docs/07-security-and-redaction.md)

---
*Dự án AgentTrace - Được thiết kế cho hệ sinh thái Agentic Coding.*
