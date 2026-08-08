# Chương 3: Hướng dẫn Lập trình Core SDK (Core SDK Usage)

Core SDK là trái tim của AgentTrace. Nếu bạn tự build một con AI Agent từ đầu bằng Python (không dùng LangChain hay LlamaIndex), đây là nơi bạn sẽ bắt đầu.

---

## 1. Khởi tạo & Cấu hình Storage

Để bắt đầu, bạn cần khởi tạo `Tracer`. Bạn có thể chọn lưu bằng SQLite nội bộ hoặc ném thẳng lên PostgreSQL.

```python
from agenttrace.core import Tracer
from agenttrace.storage.postgres import PostgresStorage

# Option 1: SQLite (Mặc định)
tracer_local = Tracer(db_path="local_logs.db")

# Option 2: Enterprise Postgres
pg_storage = PostgresStorage("postgresql://user:pass@localhost/agentdb")
tracer_pg = Tracer(storage=pg_storage)
```

---

## 2. Quản lý vòng đời (Lifecycle)

Mỗi lần user gửi một tin nhắn cho AI, bạn coi đó là một `Run`.

```python
# 1. Bắt đầu Run
run_id = tracer_local.start_run(
    agent="MySuperAgent", 
    task="Write a python snake game"
)

# 2. Quan trọng: Gắn ID vào Context
# Bước này giúp các hàm decorator phía sau tự động biết nó thuộc Run nào
tracer_local.set_current_run(run_id)

try:
    # ... Chạy logic của AI ở đây ...
    pass
except Exception as e:
    # 3. Đánh dấu lỗi nếu có
    tracer_local.end_run(run_id, status="failed")
    raise e
finally:
    # 4. Luôn phải kết thúc Run
    tracer_local.end_run(run_id, status="completed")
```

---

## 3. Theo dõi hàm bằng Decorator (Đỉnh cao của sự lười biếng)

Thay vì phải tự tạo Event rườm rà, AgentTrace tặng bạn 2 món bảo bối: `@trace_tool` (cho hàm thường) và `@async_trace_tool` (cho hàm async).

### A. Hàm đồng bộ (Sync)

```python
from agenttrace.core import trace_tool

@trace_tool
def fetch_weather(city: str):
    """Công cụ giúp LLM xem thời tiết."""
    import requests
    res = requests.get(f"https://wttr.in/{city}?format=j1")
    return res.json()

# Chỉ cần gọi hàm như bình thường, AgentTrace sẽ âm thầm ghi lại Input (city) 
# và toàn bộ JSON Output vào Database!
fetch_weather("Hanoi")
```

### B. Hàm bất đồng bộ (Async) - Dành cho High Performance

> [!TIP]
> Việc gọi các hàm API bên thứ 3 (như OpenAI) trong ứng dụng production LUÔN LUÔN nên dùng Async để tránh nghẽn luồng.

```python
import asyncio
from agenttrace.core.async_tracer import AsyncTracer, async_trace_tool

async_tracer = AsyncTracer(db_path="async_logs.db")
async_tracer.set_current_run(run_id)

@async_trace_tool
async def download_file_async(url: str):
    await asyncio.sleep(1) # Giả lập I/O delay
    return f"Downloaded 10MB from {url}"

# AgentTrace sẽ chờ (await) tool chạy xong mới ghi log
await download_file_async("https://example.com/data.csv")
```

---

## 4. Xử lý lỗi (Exception Handling) trong Tool

Điều tuyệt vời nhất của `@trace_tool` là nếu hàm của bạn văng ra lỗi (ví dụ: mất mạng, chia cho không), AgentTrace sẽ **tự động bẫy (catch)** lỗi đó, ghi vào Log với status là `FAILED` kèm theo `StackTrace` đầy đủ, rồi mới `raise` lại cho app của bạn.

Nhờ vậy, khi mở Dashboard lên, bạn sẽ thấy tool bị tô màu Đỏ và nguyên nhân chính xác vì sao Agent của bạn "chết lâm sàng".

---

[Tiếp theo: Chương 4 - Tích hợp Adapters →](04-adapters-integration.md)
