# Spec thành viên 5 — Report, demo và evidence

- **Ngày:** 2026-07-29
- **Branch:** `team/report-demo`
- **Vai trò:** chuẩn bị Report Part A trước demo, rehearsal 3–5 scenario, sau đó hoàn thiện Part B chỉ bằng log/transcript/run thật.

## 1. Mục tiêu

Đảm bảo team có tài liệu demo ngắn, dễ thử và report có thể truy ngược từng claim về artifact thật. Không tự tạo metric, run hoặc tool trace giả.

## 2. Phạm vi file

### Được sửa trực tiếp

```text
starter_v0/artifacts/REPORT.md
```

### Có thể tạo/quản lý nếu cần

```text
starter_v0/transcripts/*.transcript.json
starter_v0/analysis/*.csv
```

Transcript phát sinh từ chạy chat/UI; không sửa nội dung log để làm đẹp kết quả. `analysis/*.csv` chỉ là output parse từ run JSON.

### Không sửa

```text
starter_v0/artifacts/system_prompt.md
starter_v0/artifacts/tools.yaml
starter_v0/artifacts/version_log.csv
starter_v0/data/eval_base.json
starter_v0/data/eval_group.json
starter_v0/tools/__init__.py
starter_v0/chat.py
starter_v0/app.py
```

## 3. Giai đoạn A — hoàn thành trước 11:30

Điền các phần sau trong `REPORT.md`:

### Team

- Team name.
- Thành viên và vai trò.
- Provider/model.

### A1 — Agent capability

Viết 1–2 câu mô tả đúng capability hiện tại, không quảng cáo tool chưa tích hợp.

### A2 — Tool table

Mỗi tool một dòng:

- tên model-visible;
- chức năng;
- đánh dấu tool mới của nhóm hay built-in.

Tên phải khớp `artifacts/tools.yaml`.

### A3 — Sample questions

Đưa 3–5 request có thể chạy ngay. Nên có:

1. research bình thường;
2. routing giữa web/social;
3. thiếu thông tin;
4. URL cụ thể;
5. confirmation boundary nếu tool action được bật.

### A4 — Demo scenarios

Chuẩn bị 3–5 scenario. Mỗi dòng ghi:

- user request;
- tool trace cần thấy;
- câu chuyện cải thiện giữa version;
- fallback run/transcript.

Part A phải dùng được như tài liệu phụ trợ khi team khác thử agent.

## 4. Rehearsal scenarios

Tối thiểu chạy và lưu transcript cho:

1. Request research bình thường.
2. Request thiếu thông tin rồi bổ sung ở lượt sau.
3. Request có action nhạy cảm để kiểm tra hỏi xác nhận.

Nên thêm một scenario out-of-scope/no-tool nếu thời gian cho phép.

Khi rehearsal:

- ghi version đang chạy;
- ghi tool names và arguments;
- kiểm tra status;
- giữ fallback transcript có kết quả tốt;
- không chụp hoặc commit secret.

## 5. Giai đoạn B — hoàn thiện sau khi có evidence

### B1 — Version evidence

Lấy trực tiếp từ `artifacts/version_log.csv` và `runs/*.json`:

- v0, v1, v2, v3;
- thay đổi artifact;
- hypothesis;
- metric trước/sau;
- prompt/tools hash;
- run file.

Mọi path phải tồn tại và mọi metric phải khớp JSON.

### B2 — Failure analysis

Lấy từ `results[*].result.failures` và `observed_mismatch`:

- case ID;
- failure type;
- actual tool calls;
- lỗi cụ thể;
- fix tương ứng.

Không thay failure bằng mô tả chung như “model hiểu chưa tốt”.

### B3 — Team eval

Liệt kê đủ 10 case trong `data/eval_group.json`, gồm 5 single-turn và 5 multi-turn. Ghi đúng expected behavior và kết quả run.

### B4 — Live chat evidence

Dùng `transcripts/*.transcript.json`, ghi:

- scenario/turn;
- version;
- tool calls + args;
- transcript/run path;
- outcome.

### B5 — Tool capability evidence

Phân biệt:

- tool mới bắt buộc;
- optional built-in nếu nhóm thực sự dùng;
- bonus tool nếu có.

Không ghi Telegram/PDF nếu chưa chạy thật. UI là deliverable core, không đưa nhầm vào bonus tool table.

### B6 — Reflection

Trả lời bằng evidence cụ thể:

- fix nào thuộc system prompt;
- fix nào thuộc tools.yaml;
- failure nào cần manual review;
- bước cải thiện tiếp theo.

## 6. Tiêu chí report hợp lệ

Theo template, run dùng trong report phải thỏa:

- `provider_error_cases == 0`;
- `measured_cases == total_cases`;
- mọi `tool_results` có error được review thủ công.

Nếu không thỏa, ghi rõ tình trạng và không gọi metric đó là kết quả hợp lệ.

## 7. Tiêu chí nghiệm thu

- [ ] Part A hoàn thành trước 11:30.
- [ ] Có 3 scenario live đã rehearse.
- [ ] Mỗi scenario có fallback transcript/run.
- [ ] Part B có evidence v0–v3 thật.
- [ ] Report liệt kê đúng 10 group cases.
- [ ] Tool calls/args trong report khớp transcript.
- [ ] Run paths và transcript paths tồn tại.
- [ ] Không có claim không có evidence.
- [ ] Không lộ secret trong report, transcript, screenshot hoặc URL public.
- [ ] Link demo được kiểm tra từ máy/device khác nếu nhóm dùng tunnel.

## 8. Handoff và merge

Part A có thể gửi leader sớm để merge/review. Part B chỉ gửi commit cuối sau khi leader hoàn tất v3 và group eval.

Handoff cần nêu:

```text
branch:
commit Part A:
commit Part B:
provider/model:
demo URL hoặc localhost command:
scenario transcript paths:
v0-v3 run paths:
group run path:
known limitations:
secret scan result:
```
