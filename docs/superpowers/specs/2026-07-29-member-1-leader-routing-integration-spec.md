# Spec thành viên 1 — Leader: routing, versioning và integration

- **Ngày:** 2026-07-29
- **Branch:** `team/leader-routing`
- **Vai trò:** giữ các file trung tâm, chạy thí nghiệm tuần tự, tích hợp các branch khác và chịu trách nhiệm final gate.

## 1. Mục tiêu

Tạo evidence hợp lệ cho baseline `v0` và ba vòng cải thiện thật `v1`, `v2`, `v3`. Mỗi vòng phải có một thay đổi có chủ đích trong prompt/tool declaration, một hypothesis, một run JSON, metric trước/sau và một dòng trong version log.

Không chia `v1`, `v2`, `v3` cho các thành viên khác. Các vòng phụ thuộc vào failure của vòng trước và phải chạy tuần tự.

## 2. Phạm vi file

### Được sửa trực tiếp

```text
starter_v0/artifacts/system_prompt.md
starter_v0/artifacts/tools.yaml
starter_v0/artifacts/version_log.csv
starter_v0/tools/__init__.py
```

### Được tạo hoặc quản lý sau khi chạy

```text
starter_v0/runs/*.json
```

### Không tự sửa

```text
starter_v0/data/eval_base.json
starter_v0/data/eval_group.json
starter_v0/app.py
starter_v0/requirements.txt
starter_v0/artifacts/REPORT.md
starter_v0/tools/AGREED_TOOL_NAME/
```

Nếu cần thay đổi file người khác, gửi yêu cầu rõ ràng cho owner của file đó.

## 3. Input

- Provider/model và API key local từ nhóm.
- Starter baseline trong `starter_v0/artifacts/`.
- Fixed base eval trong `starter_v0/data/eval_base.json`.
- Contract tool mới do thành viên 3 bàn giao.
- 10 group cases do thành viên 4 bàn giao.
- UI/report không phải input để quyết định routing.

## 4. Output bắt buộc

1. `tools.yaml` chứa ít nhất 5 tool hợp lệ và declaration mới.
2. `tools/__init__.py` có mapping tên model-visible → function Python.
3. `version_log.csv` có header và ít nhất các version `v0`, `v1`, `v2`, `v3`.
4. Run JSON tương ứng với từng version.
5. Artifact hash trong run JSON và version log khớp nhau.
6. Kết quả group eval chạy trên version cuối.
7. Bản handoff gồm danh sách commit đã merge, run paths, metric và các điểm còn cần report cập nhật.

## 5. Quy trình thực hiện

### 5.1. Preflight

Từ `starter_v0/` chạy provider preflight và smoke test theo `TOOL-SETUP.md`. Không commit `.env` hoặc secret.

### 5.2. Baseline `v0`

Chạy:

```bash
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```

Giữ nguyên run JSON. Đọc tối thiểu:

- `summary.case_accuracy`
- `summary.tool_routing_accuracy`
- `summary.argument_accuracy`
- `summary.multiturn_accuracy`
- `summary.provider_error_cases`
- `summary.measured_cases`
- `results[*].result.failures`
- `results[*].result.observed_mismatch`

### 5.3. Tích hợp tool mới

Nhận từ thành viên 3:

- tool-visible name;
- function name và signature;
- argument schema;
- output schema;
- required environment variables;
- confirmation/side-effect behavior;
- direct smoke-test evidence.

Sau đó:

1. Import function trong `tools/__init__.py`.
2. Thêm đúng một key vào `TOOL_FUNCTIONS`.
3. Thêm declaration tương ứng trong `tools.yaml`.
4. Kiểm tra tên trong registry, YAML và eval khớp tuyệt đối.
5. Chạy direct smoke test và một eval case sử dụng tool nếu có.

Không rename các starter tools; rename sẽ lan sang fixed eval và report.

### 5.4. `v1`, `v2`, `v3`

Với mỗi version:

1. Đọc failure thật của version trước.
2. Viết một hypothesis ngắn.
3. Chỉ sửa một hướng: `system_prompt.md` hoặc `tools.yaml`.
4. Chạy đúng một base eval.
5. So sánh metric trước/sau.
6. Kiểm tra provider errors và tool execution errors.
7. Ghi ngay một dòng vào `version_log.csv`.

Ví dụ nguyên tắc thay đổi:

- Prompt: boundary khi thiếu thông tin, out-of-scope, confirmation trước action.
- YAML: tên tool, điều kiện dùng/không dùng, convention của arguments, default và enum.

Không tạo ba run giống hệt nhau chỉ để có nhãn version.

### 5.5. Group eval và final integration

Sau khi merge `data/eval_group.json`:

```bash
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

Sau khi merge UI và report, chạy smoke test cuối từ clean integration branch.

## 6. Quy tắc merge

Leader merge theo thứ tự:

1. tool mới;
2. registry/YAML do leader tự nối;
3. UI;
4. group eval;
5. report/evidence cuối.

Mỗi branch phải merge vào branch integration trước nếu cần kiểm tra. Chỉ leader merge integration vào `main` sau final gate.

## 7. Tiêu chí nghiệm thu

- [ ] Preflight provider pass.
- [ ] `v0`, `v1`, `v2`, `v3` đều có run JSON thật.
- [ ] `provider_error_cases == 0` cho run dùng trong report.
- [ ] `measured_cases == total_cases`.
- [ ] Mỗi version có hypothesis và artifact hash riêng hoặc thay đổi được chứng minh.
- [ ] `version_log.csv` khớp run JSON.
- [ ] Tool mới chạy được qua registry, không chỉ direct import.
- [ ] Base eval không bị sửa nội dung query/expected behavior.
- [ ] Group eval có đúng 10 cases khi nhận từ thành viên 4.
- [ ] Không có secret trong commit hoặc generated evidence.

## 8. Handoff cho leader/main

Gửi nhóm:

```text
provider/model:
merged branches:
v0 run:
v1 run:
v2 run:
v3 run:
group run:
artifact hashes:
metric table:
known tool execution errors:
remaining report/demo actions:
```
