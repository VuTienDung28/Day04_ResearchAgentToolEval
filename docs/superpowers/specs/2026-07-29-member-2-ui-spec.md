# Spec thành viên 2 — UI và transcript

- **Ngày:** 2026-07-29
- **Branch:** `team/ui`
- **Vai trò:** xây UI demo tối thiểu, tái sử dụng agent loop hiện có và hiển thị evidence đủ để team khác test.

## 1. Mục tiêu

Tạo một UI chạy được trên máy local, cho phép nhập request, chạy Research Agent, xem response cuối, xem đầy đủ tool trace và lưu transcript. UI không được tạo agent loop hoặc routing logic thứ hai.

## 2. Phạm vi file

### Được sửa trực tiếp

```text
starter_v0/app.py
starter_v0/requirements.txt
```

### Có thể đọc nhưng không sửa

```text
starter_v0/chat.py
starter_v0/artifacts/system_prompt.md
starter_v0/artifacts/tools.yaml
starter_v0/tools/__init__.py
starter_v0/transcripts/
```

Không sửa `chat.py`, prompt, YAML, registry, eval hoặc report.

## 3. Input contract

UI đọc runtime:

- provider từ lựa chọn UI hoặc biến môi trường/config local;
- version từ input/selectbox, mặc định version hiện hành của nhóm;
- system prompt từ `artifacts/system_prompt.md`;
- declarations từ `artifacts/tools.yaml`;
- agent function `run_model_tool_loop` trong `chat.py`;
- model và `max_tool_rounds` theo config hiện có hoặc giá trị UI hợp lý.

UI không hard-code danh sách tool, prompt hoặc artifact hash.

## 4. Output contract

Mỗi lần chạy phải tạo kết quả tương đương:

```text
status
assistant_text
rounds[]
tool_events[]
artifact_version
provider
model
transcript path
```

Mỗi round cần nhìn được:

- số round;
- assistant text nếu có;
- danh sách tool calls;
- tool name;
- arguments;
- result hoặc error.

Mỗi transcript phải dùng JSON shape tương thích với `chat.py`, tối thiểu có:

- `transcript_id`;
- `artifact_version`, `prompt_hash`, `tools_hash`;
- `provider`, `model`;
- `system_prompt`, `tools`;
- `created_at`, `updated_at`;
- `turns[]` với request, status, rounds, tool events và final response.

## 5. Thiết kế UI tối thiểu

### Khu vực cấu hình

- Provider/model nếu project hiện tại cho phép chọn.
- Artifact version.
- Max tool rounds với default an toàn.

### Khu vực request

- Text area nhập request.
- Nút chạy agent.
- Không tự chạy request khi page reload.

### Khu vực kết quả

- Final response nổi bật.
- Status: `answered`, `waiting_for_user`, `max_tool_rounds`, hoặc `provider_error`.
- Artifact version/hash.
- Expandable trace cho từng round/tool event.
- Link hoặc path transcript đã lưu.

### Error display

Hiển thị lỗi provider/tool ở dạng dễ đọc, không hiển thị API key, request header hoặc secret environment value.

## 6. Golden path và edge cases

Kiểm tra tối thiểu:

1. Request research bình thường và có tool call.
2. Request thiếu thông tin và agent trả `waiting_for_user`.
3. Request meta/out-of-scope không gọi tool.
4. Tool trả error: UI vẫn render status/trace và không mất transcript.
5. Reload page không làm mất lịch sử file đã lưu.
6. Empty input không gọi provider.
7. Request dài vẫn không làm vỡ layout.

## 7. Dependencies

Chỉ thêm dependency UI cần thiết. Với Streamlit:

```text
streamlit>=1.30.0
```

Không thêm package mới cho logging, schema hoặc agent abstraction nếu stdlib và code hiện có đã đủ.

## 8. Kiểm tra branch

Từ `starter_v0/`:

```bash
python -m py_compile app.py
streamlit run app.py
```

Mở `http://localhost:8501`, chạy các scenario ở mục 6 và kiểm tra file transcript.

Nếu môi trường không có Streamlit, ghi rõ blocker trong handoff; không thay bằng agent loop giả.

## 9. Tiêu chí nghiệm thu

- [ ] `app.py` tồn tại và khởi động được.
- [ ] UI dùng `run_model_tool_loop` từ `chat.py`.
- [ ] Đọc prompt/YAML runtime.
- [ ] Hiển thị final response, status, rounds và tool trace.
- [ ] Hiển thị artifact version/hash và provider/model.
- [ ] Lưu transcript JSON tương thích với chat flow.
- [ ] Không lộ secret.
- [ ] Không sửa file ngoài ownership.
- [ ] `requirements.txt` chỉ có dependency thực sự cần.

## 10. Handoff

Gửi leader:

```text
branch:
commit:
start command:
framework:
files changed:
transcript location pattern:
manual scenarios tested:
known limitations:
```

Sau khi leader đổi prompt/YAML, UI phải đọc file runtime nên không cần sửa UI; chỉ chạy lại để xác nhận version mới hiển thị đúng.
