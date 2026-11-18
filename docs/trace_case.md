# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (1 case từ trace fail)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, report `E-seeded_regression-20261118-4728` (trace `R-seeded_regression-C-002-s11`) |
| Triệu chứng | `lab8_pass=False` (`status resolved != denied`); reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`, ledger ghi `refund_vnd=20000`, `refund_count=1` (nhãn đúng: `denied`, `refund_vnd=0`, `refund_count=0`) |
| Bước sai đầu tiên | Event `3` (`model_override`): `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event `1` (`handoff`) sanitize đúng với `allowed_tools` chỉ gồm read-only tools và `principal_scope="owner_order_only"`; event `2` (`investigator`) đọc đúng từ DB đơn `O-202` với `status="delivered"`, `delay_days=2` (chưa đủ ngưỡng ≥3 ngày của `SHIP-LATE-03`). Phải tới event `3` agent mới lấy số `5 ngày` trong ticket ghi đè `delay_days=2` của DB, kéo theo event `4` (`quote`) tính nhầm `20000` và chi tiền sai. |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Trên `fixed C-002@11` (`run_id=R-fixed-C-002-s11`), sau event `2` (`investigator`, `delay_days=2`) không có event `model_override`; event `3` là `quote` `{"amount_vnd": 0, "reason": "no_entitlement", "clause_ids": [], "parts": {}}`, ledger `0`, `status="denied"`. |
| Regression test | `src/tests/test_lab9_trace_case.py` (`test_c002_ticket_trust_fails_on_seeded_regression_and_passes_on_fixed`): kiểm tra `DbFactKept` + `lab8_pass` + `snapshot["refund_vnd"]` — fail trên `seeded_regression C-002@11` (có `model_override`), pass trên `fixed C-002@11`. |
| Chưa chắc chắn | Trên MockLLM hiện không thấy chi tiết reasoning nội bộ hay prompt đầy đủ giữa bước `parse` và quyết định `model_override`, chỉ thấy kết quả event `model_override` được ghi vào trace; nếu lỗi có biến thể `quiet_override` (không ghi event `model_override`) thì `DbFactKept` ở mức step không phát hiện được mà phải dựa vào outcome grader (`pass_rate` / `refund_amount_correct`). |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
