# Judge audit

Chạy:
```bash
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 10
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 10
```

| Tiêu chí | n | κ | Precision | Recall | Observed → Corrected fail rate | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|---|
| `tone_ok` (`judge_tone_public.csv`) | 100 | 0.757 | 0.857 | 0.800 | 0.280 → 0.300 | Có (κ=0.757 ≥ 0.6, P=0.857 ≥ 0.8, R=0.800 ≥ 0.7) | **dùng** (cho tiêu chí giọng điệu) |
| `helpful` (`judge_helpful_public.csv`) | 100 | 0.375 | 1.000 | 0.300 | 0.090 → 0.300 | **Không** (κ=0.375 < 0.6, R=0.300 < 0.7) | **loại** (không dùng làm gate) |

## Audit thủ công các case bất đồng (≥5 case; kiểm cả `tone_ok` và `helpful`)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & hành động sửa rubric / hệ thống |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`) `"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."` | PASS | FAIL | Người đúng | Judge thấy thân thiện nên cho PASS, bỏ qua việc xưng `"em"` + `"nha"` quá suồng sã với khách. **Sửa rubric:** quy định bắt buộc đại từ `"LogiX"` – `"anh/chị"`, cấm `"em"`, `"bạn"`, `"nha"`, `"nhé"`. |
| 2 | `H-029` (`tone_ok`) `"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."` | PASS | FAIL | Người đúng | Judge chỉ nhìn cụm `"Dạ, vui lòng"` mà bỏ qua vế ra lệnh `"không cần nhắn thêm"`. **Sửa rubric:** thêm quy tắc đánh FAIL mọi câu có hàm ý ra lệnh/từ chối giao tiếp dù mở đầu bằng `"Dạ"`. |
| 3 | `H-070` (`tone_ok`) `"Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂"` | PASS | FAIL | Người đúng | Emoji cười `😂😂` không phù hợp ngữ cảnh khiếu nại. **Sửa rubric:** cấm emoji cợt nhả trong phản hồi chăm sóc khách hàng/khiếu nại. |
| 4 | `H-051` (`tone_ok`) `"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."` | FAIL | PASS | Người đúng | CS LogiX cho phép dùng từ `"refund"` trong câu trả lời lịch sự, nhưng judge tự phạt vì tiếng Anh. **Sửa rubric:** bổ sung ví dụ few-shot nêu rõ thuật ngữ `"refund"` được chấp nhận nếu giữ cấu trúc lịch sự. |
| 5 | `H-081` (`tone_ok`) `"Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ."` | FAIL | PASS | **Judge đúng** (nhãn người bị nhầm) | Theo ghi chú CSV, người gán nhãn đọc nhầm ticket nên đánh PASS dù thiếu phần thiện chí/hỗ trợ thêm theo mẫu chuẩn; kiểm tra lại nhãn gốc cho thấy cần chuẩn hoá lại golden label của người trước khi tái calibrate. |
| 6 | `H-094` (`tone_ok`) `"Da, LogiX da hoan 40.000đ cho don O-341, xin loi vi su bat tien."` | PASS | FAIL | Người đúng | Văn bản dịch máy mất dấu tiếng Việt, nhưng judge vẫn cho PASS vì cấu trúc xin lỗi. **Sửa rubric:** yêu cầu tiếng Việt có dấu chuẩn, đánh FAIL khi mất dấu. |
| 7 | `HL-016` (`helpful`) `"Dạ, LogiX thành thật xin lỗi... LogiX đã hoàn 55.000đ cho đơn O-404. Một lần nữa LogiX xin lỗi..."` | PASS | FAIL | Người đúng | Reply rất dài và lễ phép nhưng **nói sai tiền** (`55.000đ` so với ledger `35.000đ`). Judge bị **verbosity/politeness bias** và không thấy ledger. **Hành động:** không dùng judge chấm tính đúng số tiền; thay bằng code grader (M3). |
| 8 | `HL-047` (`helpful`) `"Ok bạn, đơn O-515 xử lý rồi nhé."` | PASS | FAIL | Người đúng | Xưng hô `"Ok bạn... nhé"` sai chuẩn nhưng judge vẫn cho qua là helpful. **Sửa rubric:** đồng bộ điều kiện tiên quyết về xưng hô chuẩn với `tone_ok`. |

## Kết luận
- **Tiêu chí `helpful` bị loại và không được dùng làm release gate:**
  - Ma trận nhầm lẫn của `helpful` là `tp=9, fp=0, fn=21, tn=70`. Dù `Precision = 1.0` (không báo nhầm), **`Recall` chỉ đạt `0.300`** và **`κ = 0.375`**, bỏ sót **21/30 (70%)** số lỗi thực tế (`fn=21`).
  - Hệ quả trực tiếp: tỷ lệ lỗi quan sát được chỉ là `0.09` (9%), tạo cảm giác giả tạo rằng agent tốt, trong khi thực chất sau hiệu chỉnh Rogan-Gladen tỷ lệ lỗi là `0.30` (30%). Phần lớn các ca `FN` là câu trả lời **nói sai số tiền so với ledger** (`18/21` ca `FN`) hoặc sai xưng hô được viết rất dài dòng, xin lỗi nhiều lần khiến judge bị đánh lừa.
  - Vì judge không nhìn thấy `refund_ledger` và dễ bị thiên lệch độ dài/lễ phép, tuyệt đối không dùng `judge_helpful` làm cổng chặn; việc đối chiếu số tiền trong reply với ledger phải làm bằng **code grader** (M3).
- **Tiêu chí `tone_ok` đạt FLOORS (`κ=0.757`, `P=0.857`, `R=0.800`)**, nên dùng được cho đánh giá giọng điệu; nếu dùng đo tỷ lệ lỗi thật cần hiệu chỉnh theo Rogan-Gladen (`0.280 → 0.300`).
- **Rủi ro còn lại:** Cả hai judge mới chỉ được kiểm trên dữ liệu replay đã công khai (`n=100`); cần tập nhãn người mới (**held-out** chưa từng thấy) sau khi sửa rubric để xác nhận lại `κ, P, R` không bị overfit.
