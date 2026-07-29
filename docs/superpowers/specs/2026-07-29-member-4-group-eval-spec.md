# Spec thành viên 4 — Team-authored eval set

- **Ngày:** 2026-07-29
- **Branch:** `team/group-eval`
- **Vai trò:** thiết kế đúng 10 case Phase B để đo các lỗi nhóm quan tâm, không sửa fixed eval.

## 1. Mục tiêu

Hoàn thành `starter_v0/data/eval_group.json` với chính xác 10 case mới của nhóm:

- 5 single-turn sử dụng `query`;
- 5 multi-turn sử dụng `turns`.

Các case phải đo behavior/routing/arguments thật, không sao chép hai case ví dụ trong `samples/eval_group.schema.example.json` và không dùng kết quả mong muốn mơ hồ.

## 2. Phạm vi file

### Được sửa duy nhất

```text
starter_v0/data/eval_group.json
```

### Không được sửa

```text
starter_v0/data/eval_base.json
starter_v0/data/eval_research_extension.json
starter_v0/artifacts/tools.yaml
starter_v0/tools/__init__.py
starter_v0/artifacts/REPORT.md
```

Nếu muốn case dùng tool mới, phải nhận tên/schema đã freeze từ leader. Nếu chưa freeze, chỉ dùng tool core hiện có.

## 3. Schema bắt buộc

Top-level nên giữ các field starter:

```json
{
  "dataset_id": "...",
  "dataset_role": "group",
  "description": "...",
  "allowed_failure_types": [
    "wrong_tool",
    "wrong_arg_value",
    "wrong_boundary",
    "unnecessary_tool",
    "out_of_scope",
    "missing_info"
  ],
  "cases": []
}
```

Mỗi case phải có:

```json
{
  "id": "G01_unique_name",
  "phase": "B",
  "failure_type": "wrong_tool",
  "query": "...",
  "expect": {
    "tool_calls": [
      {"name": "lookup", "args": {"query": "..."}}
    ]
  },
  "metadata": {
    "what_it_tests": "Mô tả behavior cụ thể cần đo"
  }
}
```

Multi-turn dùng:

```json
{
  "id": "G06_multiturn_name",
  "phase": "B",
  "failure_type": "missing_info",
  "turns": [
    {"role": "user", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "expect": {"no_tool": true},
  "metadata": {"what_it_tests": "..."}
}
```

Với multi-turn, phần tử cuối cùng phải là user turn được chấm. `run_eval.py` dùng các turn trước làm context, không chạy tool cho các turn trước.

## 4. Phân bổ 10 case

### Single-turn: G01–G05

Nên phủ năm behavior khác nhau, ví dụ:

1. Chọn đúng tool giữa `lookup` và `social_search`.
2. Trích đúng argument như `limit`, `timeframe`, `search_type`.
3. Có URL cụ thể thì dùng `fetch`.
4. Thiếu thông tin thì dùng `clarify`.
5. Out-of-scope/meta thì `no_tool`.

### Multi-turn: G06–G10

Nên phủ:

1. Carry-over argument từ turn trước.
2. User correction đổi entity.
3. User correction đổi limit/timeframe.
4. Chuyển từ một tool sang tool khác.
5. Turn cuối không cần tool hoặc yêu cầu confirmation.

Mỗi case chỉ nên kiểm tra một failure chính. `metadata.what_it_tests` phải nói rõ dữ liệu nào được carry, đổi hoặc bỏ.

## 5. Expected args

`run_eval.py` chấm subset arguments. Chỉ đưa vào `expect.args` những giá trị cần kiểm tra và có thể xác định chắc chắn từ request.

Ví dụ:

```json
{"name": "lookup", "args": {"topic": "news", "timeframe": "day"}}
```

Không bắt model phải tạo query string chính xác nếu mục tiêu case không phải query normalization. Không yêu cầu thứ tự tool call nếu case có nhiều tool; evaluator đã xử lý matching theo tên/args.

## 6. Quy tắc chất lượng

- ID không trùng nhau.
- Đúng 5 case có `query` và đúng 5 case có `turns`.
- Không có case vừa `query` vừa `turns`.
- `phase` của tất cả case là `B`.
- `failure_type` thuộc allowlist.
- Tool trong expected phải tồn tại trong declaration/registry sau khi leader tích hợp.
- Case không phụ thuộc credential đặc biệt nếu không cần thiết.
- Case tiếng Việt rõ nghĩa, có behavior có thể chấm tự động.

## 7. Kiểm tra branch

Chạy parse JSON:

```bash
python -m json.tool data/eval_group.json
```

Có thể kiểm tra nhanh số lượng bằng Python stdlib:

```bash
python -c "import json; d=json.load(open('data/eval_group.json', encoding='utf-8')); c=d['cases']; assert len(c)==10; assert sum('query' in x for x in c)==5; assert sum('turns' in x for x in c)==5; assert all(x['phase']=='B' for x in c)"
```

Sau khi leader đã tích hợp tool declarations, chạy:

```bash
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

## 8. Tiêu chí nghiệm thu

- [ ] Có đúng 10 case.
- [ ] Có đúng 5 single-turn và 5 multi-turn.
- [ ] Mỗi case đủ `id`, `phase`, `failure_type`, `expect`, `metadata.what_it_tests`.
- [ ] Multi-turn có user turn cuối để chấm.
- [ ] Không sửa fixed eval.
- [ ] Expected tool names hợp lệ sau integration.
- [ ] JSON parse pass và group eval chạy được.
- [ ] Case không trùng mẫu ví dụ hoặc copy nguyên case base.

## 9. Handoff

Gửi leader:

```text
branch:
commit:
case IDs:
single-turn IDs:
multi-turn IDs:
failure_type coverage:
expected tools:
validation command/result:
known dependency on new tool:
```
