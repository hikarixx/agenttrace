# 6. CLI và Web Dashboard

AgentTrace đi kèm với một CLI (Giao diện dòng lệnh) mạnh mẽ và một Dashboard Web trực quan.

## AgentTrace CLI

Bạn có thể chạy công cụ CLI thông qua lệnh `agenttrace`.

### Khởi chạy Server
Để khởi động REST API và Web Dashboard:
```bash
agenttrace serve --port 8000
```
Sau đó truy cập `http://127.0.0.1:8000` trên trình duyệt.

### Xem danh sách Runs qua Terminal
```bash
agenttrace runs --limit 10
```
*(Hiển thị bảng danh sách các phiên chạy dưới dạng Text ASCII).*

### Xuất dữ liệu Run ra JSON
```bash
agenttrace export <RUN_ID> --output log.json
```

## AgentTrace Web Dashboard

Dashboard Web cung cấp 2 chế độ xem:
1. **Recent Runs**: Bảng thống kê các lần Agent hoạt động, kèm theo thời gian, ID và trạng thái (Started, Completed, Failed).
2. **Execution Tree**: Khi click vào một Run ID, bạn sẽ xem được cấu trúc phân cấp (Cây) của các Event/Tool. Bạn có thể click vào từng dòng sự kiện để xem chi tiết JSON metadata (Input/Output).

> [!TIP]
> Nếu dữ liệu mới không xuất hiện trên Web Dashboard sau khi thao tác với IDE, hãy thử Hard Refresh trình duyệt (`Ctrl + F5`) để xóa bộ nhớ đệm (Cache).

---

[Tiếp theo: Security & Redaction →](07-security-and-redaction.md)
