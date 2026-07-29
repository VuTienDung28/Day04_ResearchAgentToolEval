# Spec thành viên 3 — Tool mới bắt buộc

- **Ngày:** 2026-07-29
- **Branch:** `team/new-tool`
- **Vai trò:** xây một tool mới độc lập, có documentation và direct smoke test; không đụng file tích hợp trung tâm.

## 1. Mục tiêu

Hoàn thành một tool mới đáp ứng yêu cầu lab: có thư mục riêng, implementation Python, `TOOL.md`, contract rõ ràng và chạy được độc lập trước khi leader đăng ký vào agent.

Tool phải phù hợp với research-agent domain, có phạm vi hẹp và demo được. Không tự làm thêm tool thứ hai khi tool đầu tiên chưa pass.

## 2. Bước bắt buộc trước khi code

Gửi leader một đề xuất ngắn gồm:

```text
model-visible name:
Python function name:
required arguments:
optional arguments/defaults:
return shape:
external API/dependency:
required env vars:
side effect:
confirmation required:
sample request:
```

Chỉ bắt đầu implementation sau khi leader xác nhận tên và signature. Tên phải không trùng `clarify`, `timeline`, `social_search`, `lookup`, `fetch`, `format`, `send`, `policy`, `papers`, `paper_text`.

## 3. Phạm vi file

### Được tạo/sửa

```text
starter_v0/tools/<agreed_tool_name>/TOOL.md
starter_v0/tools/<agreed_tool_name>/tool.py
```

### Không được sửa

```text
starter_v0/tools/__init__.py
starter_v0/artifacts/tools.yaml
starter_v0/requirements.txt
starter_v0/data/eval_base.json
starter_v0/data/eval_group.json
starter_v0/artifacts/REPORT.md
```

Leader sẽ tự nối registry và declaration. Điều này tránh conflict tại file dùng chung.

## 4. Implementation contract

### Function

Function public phải có tên/signature đúng contract đã freeze. Arguments phải là dữ liệu user-facing, không nhận secret hard-code.

### Result

Trả về JSON-serializable value, ưu tiên dict có shape ổn định:

```python
{
    "status": "ok" | "error" | "awaiting_user",
    "items": [...],
    "message": "...",
}
```

Nếu contract hiện tại của project yêu cầu shape khác, dùng shape đó và ghi rõ trong `TOOL.md`; không tạo adapter riêng cho leader.

### Boundary và security

- Không log API key, authorization header hoặc toàn bộ environment.
- Không tự thực hiện side effect nếu chưa có confirmation contract.
- URL/user input đi qua boundary phải được xử lý bằng thư viện hiện có và không ghép shell command.
- Timeout/request behavior phải phù hợp với các tool hiện tại.
- Dùng stdlib hoặc `requests` đã có trước khi đề xuất dependency mới.

### Error behavior

Lỗi phải trả về dạng JSON-serializable để loop có thể ghi vào `tool_results`. Không nuốt lỗi thành kết quả thành công.

## 5. `TOOL.md`

Ghi ngắn gọn:

1. Tool name.
2. Mục đích.
3. Khi nào dùng.
4. Khi nào không dùng.
5. Arguments và default.
6. Output shape.
7. Required env vars.
8. Side effect/confirmation boundary.
9. Một invocation an toàn.
10. Cách chạy direct smoke test.

Không mô tả capability tool vượt quá implementation.

## 6. Direct smoke test

Có thể dùng một đoạn Python một lần hoặc test nhỏ không framework. Test phải chứng minh:

- import được function;
- invocation với input hợp lệ không lỗi schema;
- output JSON-serializable;
- output có status/shape đúng;
- nếu thiếu credential thì báo lỗi rõ mà không lộ secret.

Không dùng mock để giả vờ API thật hoạt động. Nếu tool cần credential hoặc quota, ghi rõ đã test live hay chỉ test validation path.

## 7. Tiêu chí nghiệm thu

- [ ] Tool name/signature đã được leader freeze.
- [ ] Chỉ thêm đúng subtree tool mới.
- [ ] `TOOL.md` đầy đủ contract.
- [ ] Implementation chạy được và output ổn định.
- [ ] Direct smoke test pass.
- [ ] Không thêm dependency nếu `requests`/stdlib đủ.
- [ ] Không có secret trong source, log hoặc commit.
- [ ] Không tự sửa registry/YAML/eval/report.

## 8. Handoff cho leader

Gửi:

```text
branch:
commit:
tool-visible name:
Python import path:
function signature:
arguments:
return shape:
required env vars:
confirmation behavior:
smoke command:
smoke result:
live API limitations:
```

Leader sau đó sẽ import function, thêm `TOOL_FUNCTIONS[name]`, thêm declaration YAML và chạy smoke test qua registry.
