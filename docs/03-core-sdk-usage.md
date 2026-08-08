# 3. Sử dụng Core SDK

Core SDK của AgentTrace cho phép bạn nhúng trực tiếp chức năng theo dõi vào bất kỳ ứng dụng Python nào.

## Khởi tạo và Quản lý Run

Một **Run** là điểm khởi đầu cho mọi quá trình theo dõi.

```python
from agenttrace.core import Tracer

# Khởi tạo Tracer
tracer = Tracer(db_path="my_logs.db")

# Tạo một Run mới
run_id = tracer.start_run(agent="MyCustomAgent", task="Summarize Document")

try:
    # Thực thi các logic của Agent
    pass
finally:
    # Kết thúc Run
    tracer.end_run(run_id, status="completed")
```

## Theo dõi Tool tự động bằng Decorator

Cách dễ nhất để theo dõi các công cụ là sử dụng decorator `@trace_tool`. 
Lưu ý: Bạn phải gọi `tracer.set_current_run(run_id)` để decorator biết nó đang chạy trong Run nào.

```python
from agenttrace.core import trace_tool

# Set run hiện tại
tracer.set_current_run(run_id)

@trace_tool
def fetch_data(url: str):
    """Giả lập hàm lấy dữ liệu từ mạng"""
    return {"status": 200, "data": "Some data..."}

# Khi gọi hàm, AgentTrace sẽ tự động ghi lại input và output!
result = fetch_data("https://api.example.com")
```

## Tạo Event thủ công

Trong trường hợp bạn muốn kiểm soát hoàn toàn việc ghi log, bạn có thể tạo Event bằng tay:

```python
event_id = tracer.start_event(
    run_id=run_id,
    event_type="tool.started",
    metadata={"tool_name": "manual_tool", "input": "test"}
)

# Kết thúc Event
tracer.end_event(event_id, status="completed", metadata={"output": "success"})
```

---

[Tiếp theo: Tích hợp với Adapters →](04-adapters-integration.md)
