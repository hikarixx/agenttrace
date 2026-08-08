# Chương 6: Cẩm nang CLI & Web Dashboard

AgentTrace mang đến trải nghiệm UI/UX toàn diện: Cho cả những Dev thích "gõ cộc cộc" trên Terminal (CLI) và các Manager thích biểu đồ xanh đỏ (Dashboard).

---

## 1. Dòng Lệnh CLI (Command Line Interface)

Tất cả bắt đầu bằng lệnh `agenttrace`. Được viết trên nền tảng `Typer` kết hợp `Rich`, CLI của AgentTrace render các bảng màu và ASCII Art tuyệt đẹp.

### Bảng Tra Cứu Các Lệnh Phổ Biến

| Lệnh (Command) | Tham số (Args) | Công dụng (Description) |
| :--- | :--- | :--- |
| `agenttrace serve` | `--port 8000` | Khởi động Web Dashboard và API Server. |
| `agenttrace runs` | `--limit 50` | In ra bảng Terminal danh sách 50 phiên làm việc gần nhất (có tô màu Status). |
| `agenttrace show` | `<run_id>` | Hiển thị chi tiết thông tin Metadata của 1 Run. |
| `agenttrace tree` | `<run_id>` | In ra cây sự kiện dạng Text (ASCII Tree) giống lệnh `tree` của Linux. |
| `agenttrace export`| `<run_id> --output file.json` | Dump toàn bộ dữ liệu Run ra JSON để chia sẻ cho team debug. |

> [!TIP]
> **Tính năng Báo cáo Kiểm toán (Audit)**
> Mới được bổ sung gần đây! Bạn gõ `agenttrace audit <run_id>` để máy tự động đọc toàn bộ log, đếm số Token/Chi phí, soi lỗi bảo mật, và xuất ra một file `Markdown` báo cáo chuyên nghiệp.

---

## 2. Web Dashboard (Giao diện đồ họa)

Giao diện Web của AgentTrace là một Single Page Application (SPA) siêu nhẹ (Vanilla JS/HTML), không cần cài đặt Node.js hay npm.

### Giao Diện Hoạt Động Như Thế Nào?

Khi bạn truy cập `http://localhost:8000`, Dashboard cung cấp 3 lớp hiển thị:

1. **Bảng Danh Sách (Recent Runs)**
   - Cột ID thông minh: Chỉ hiển thị 8 ký tự đầu, nhưng nếu bạn rê chuột (Hover) hoặc ID chứa cụm `step`, nó sẽ mở rộng tự động qua CSS Tooltip.
   - Trạng thái `completed` (Xanh), `failed` (Đỏ), `started` (Vàng).

2. **Biểu Đồ Data Visualization (Mới cập nhật!)**
   - AgentTrace đã tích hợp **Chart.js** vào HTML.
   - Khi bạn bấm vào một Run, Dashboard sẽ tự động duyệt qua toàn bộ Event Metadata. Nếu nó thấy `prompt_tokens` và `completion_tokens`, nó lập tức vẽ lên màn hình một biểu đồ **Stacked Bar Chart**. Giúp sếp nhìn lướt qua là biết Tool nào đang ngốn tiền nhất!

3. **Cây Sự Kiện (Execution Tree)**
   - Hiển thị theo cấp bậc (cha - con).
   - Click vào từng Node để bung (Collapse/Expand) xem khối JSON nguyên gốc chứa Input/Output.

---

[Tiếp theo: Chương 7 - Security & Redaction →](07-security-and-redaction.md)
