# Day 04 Lab v2 Report — Research Agent

> Báo cáo gồm Phần A giới thiệu nhanh để dùng khi demo và Phần B là bằng chứng triển khai, eval và live chat.

## Team

- Team: Nhóm Research Agent
- Provider/model: OpenRouter / `openai/gpt-4o-mini`.

| STT | Họ và tên | Mã học viên |
|---:|---|---|
| 1 | Chu Nguyễn Tuấn Anh | `2A202601755` |
| 2 | Đào Thị Trang | `2A202601809` |
| 3 | Lê Minh Ngọc | `2A202601471` |
| 4 | Vũ Tiến Dũng | `2A202602009` |
| 5 | Nguyễn Đức Chung | `2A202601705` |

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ nghiên cứu web, tin tức, bài đăng mạng xã hội, bài báo khoa học, RSS và nguồn nội bộ. Agent có thể đọc nguồn đã có, làm sạch và tổ chức danh sách nguồn, định dạng trích dẫn, đồng thời giữ ngữ cảnh nhiều lượt và dừng để hỏi lại khi thiếu thông tin hoặc cần xác nhận trước hành động gửi ra ngoài.

**Link dùng thử:**

- Local demo: `http://localhost:8517`
- Public URL: chưa cấu hình; không mở tunnel trong evidence này.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại khi thiếu thông tin hoặc xin xác nhận trước side effect | Không |
| `timeline` | Lấy bài đăng gần đây từ một tài khoản mạng xã hội cụ thể | Không |
| `social_search` | Tìm bài đăng mạng xã hội theo chủ đề, từ nhiều tài khoản | Không |
| `lookup` | Tìm kiếm thông tin hoặc tin tức trên web | Không |
| `fetch` | Đọc nội dung từ URL cụ thể đã được cung cấp | Không |
| `format` | Định dạng các research item thành digest Markdown | Không |
| `send` | Gửi nội dung ra hệ thống bên ngoài sau khi có xác nhận | Không |
| `policy` | Tìm trong tài liệu nội bộ theo chủ đề chính sách | Không |
| `papers` | Tìm bài báo khoa học theo từ khóa | Không |
| `paper_text` | Lấy nội dung text của bài báo arXiv | Không |
| `deduplicate_sources` | Xóa nguồn trùng từ danh sách nguồn đã có | Có |
| `rss_reader` | Đọc các mục mới nhất từ RSS/Atom feed đã biết | Có |
| `source_diversity_audit` | Đo phân bố miền và mức độ tập trung của danh sách nguồn | Có |
| `timeline_builder` | Sắp xếp các item nghiên cứu đã có theo ngày | Có |
| `citation_formatter` | Tạo danh mục trích dẫn từ metadata nguồn đã có | Có |

Năm tool nhóm thêm đều là local formatter/reader không có side effect. Chúng không tự tìm nguồn mới khi input yêu cầu dữ liệu đã có.

## A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?`
2. `Cho tôi 1 bài đăng mới nhất của Sam Altman.`
3. `Đọc 3 mục mới nhất từ RSS feed https://hnrss.org/frontpage.`
4. `Kiểm tra mức độ tập trung tên miền của các nguồn [{"url":"https://a.com/1"},{"url":"https://a.com/2"},{"url":"https://b.org/3"}] với ngưỡng 0.6.`
5. `Tạo danh mục tài liệu kiểu APA từ nguồn [{"title":"Attention Is All You Need","url":"https://arxiv.org/abs/1706.03762","authors":["Ashish Vaswani"],"year":"2017"}].`

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Tin web và tin mạng xã hội trong cùng request | `lookup(query=AI, topic=news, timeframe=day)` và `social_search(query=AI, search_type=Latest)` | v0 gọi đúng hai tool nhưng chuẩn hóa web args chưa đúng; v3 giữ đúng query/topic/timeframe và v4 giữ kết quả sau khi thêm tool mới | `runs/v4_B_base_openrouter_20260729T124129230657.json`, case `R13_parallel_web_and_tweets` |
| Nguồn RSS và danh sách nguồn | `rss_reader(limit=3)`, `deduplicate_sources(match_by=url)`, `source_diversity_audit(concentration_threshold=0.6)` | v4 bổ sung các boundary cụ thể cho feed, dedup và diversity; không nhầm với `fetch` hoặc `lookup` | `runs/v4_B_group_openrouter_20260729T124219713003.json`, cases `G01`–`G03` |
| Tổ chức dữ liệu nghiên cứu | `timeline_builder(order=descending)` và `citation_formatter(style=apa)` | Tool mới chỉ xử lý dữ liệu đã có, không tự search/fetch; v4 kiểm tra đúng tham số và giữ side-effect bằng 0 | `runs/v4_B_group_openrouter_20260729T124219713003.json`, cases `G04`–`G05`; transcript `v4_openrouter_20260729T124418729681.transcript.json` |
| Hỏi lại và xác nhận trước khi gửi | `clarify(response_type=text)` khi thiếu handle/URL; `clarify(response_type=yes_no)` trước Telegram | v0 từng đoán handle, bịa URL và gọi `send`; prompt/declaration mới đặt boundary rõ ràng | `runs/v4_B_base_openrouter_20260729T124129230657.json`, cases `R10`–`R12`; transcript `v4_openrouter_20260729T124347939528.transcript.json` |

Khi demo nội dung mạng xã hội, chỉ nên trình bày trace tool, account, số lượng và link trả về; không nên khẳng định tiêu đề hoặc sự kiện từ một response live nếu chưa kiểm chứng thủ công.

---

# PHẦN B — Chi tiết / Bằng chứng

> Metric chỉ được xem là hợp lệ khi `provider_error_cases=0`, `measured_cases=total_cases`, và mọi `tool_results` có error đều đã được review. Các run v4 dưới đây thỏa cả ba điều kiện.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline starter, declaration và prompt còn mơ hồ | Starter chưa có boundary rõ sẽ bộc lộ lỗi routing, missing-info và side effect | `case_accuracy` | — | 0.70 | `runs/v0_B_base_openrouter_20260729T110342431867.json` |
| v1 | Cập nhật `artifacts/system_prompt.md` về scope, ambiguity và side-effect | Boundary rõ sẽ ngăn đoán bừa, gửi ngoài ý muốn và gọi tool cho yêu cầu ngoài phạm vi | `case_accuracy` | 0.70 | 0.95 | `runs/v1_B_base_openrouter_20260729T110549801963.json` |
| v2 | Cập nhật `artifacts/tools.yaml` để phân biệt `clarify` và `fetch` khi đã có URL | Contract exact-URL sẽ sửa routing đọc link trực tiếp | `case_accuracy` | 0.95 | 1.00 | `runs/v2_B_base_openrouter_20260729T110737849160.json` |
| v3 | Chuẩn hóa source routing, timeframe, search type và confirmation precedence | Declaration cụ thể sẽ cải thiện generalization mà không làm giảm base accuracy | `case_accuracy` | 1.00 | 1.00 | `runs/v3_B_base_openrouter_20260729T111152545286.json` |
| v4 | Tích hợp 5 tool nghiên cứu mới và declaration/prompt tương ứng | Thêm pipeline tool không được làm giảm routing base hoặc tạo provider error | `case_accuracy` | 1.00 | 1.00 | `runs/v4_B_base_openrouter_20260729T124129230657.json` |

**Run v4 cuối:**

- Base: 20/20, `case_accuracy=1.0`, `tool_routing_accuracy=1.0`, `argument_accuracy=1.0`, `multiturn_accuracy=1.0`.
- Group: 10/10, `case_accuracy=1.0`, `tool_routing_accuracy=1.0`, `argument_accuracy=1.0`, `multiturn_accuracy=1.0`.
- Cả hai run: `provider_error_cases=0`, `measured_cases=total_cases`.
- Artifact fingerprint: `v4+pb5f97c8cb0f3+t766e4d734e0a`.
- Provider/model: `openrouter` / `openai/gpt-4o-mini`.

`case_accuracy=1.0` ở đây chứng minh routing và subset arguments theo eval, không tự động chứng minh chất lượng nội dung cuối. Hai case ngoài phạm vi `R08` và `R14` đã ngừng gọi tool sai nhưng model vẫn trả lời trực tiếp thay vì từ chối/định hướng; đây là gap semantic cần review thủ công.

## B2. Failure analysis

Các lỗi dưới đây được lấy từ run v0, trước khi sửa prompt và tool declarations.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R08_out_of_scope` | `out_of_scope` | `send` | Câu hỏi tích phân không thuộc research nhưng bị đưa vào action tool | Prompt cấm action tool cho yêu cầu ngoài phạm vi; v4 không gọi tool |
| `R10_missing_handle` | `missing_info` | `timeline(screenname=sama)` | Agent đoán Sam Altman khi người dùng chưa nêu tài khoản | Prompt và declaration yêu cầu `clarify(response_type=text)` khi thiếu handle |
| `R11_missing_url` | `missing_info` | `fetch(url=https://example.com/article)` | Agent bịa URL thay vì xin link thật | Declaration `fetch` yêu cầu copy exact URL; prompt yêu cầu clarify |
| `R12_confirm_before_send` | `wrong_boundary` | `send` | Agent gọi gửi trước khi có xác nhận yes/no | Prompt đặt confirmation precedence; v4 gọi `clarify(response_type=yes_no)` |
| `R13_parallel_web_and_tweets` | `wrong_arg_value` | `lookup(query=AI news, timeframe=day)` và `social_search(query=AI)` | Web query bị thêm từ `news`, thiếu `topic=news` | Declaration `lookup` yêu cầu query tập trung và topic news cho tin tức |
| `R14_out_of_scope_coding` | `out_of_scope` | `send` | Code Python bị coi như nội dung cần gửi | Prompt cấm action tool cho yêu cầu coding ngoài research |

## B3. Team eval cases

`data/eval_group.json` có đúng 10 case bắt buộc: 5 single-turn và 5 multi-turn. Run cuối `runs/v4_B_group_openrouter_20260729T124219713003.json` cho kết quả 10/10 PASS.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_deduplicate_sources` | Xóa trùng URL từ danh sách đã có | `deduplicate_sources(match_by=url)` | PASS |
| `G02_rss_reader_limit` | Nhận diện RSS và giữ limit=3 | `rss_reader(limit=3)` | PASS |
| `G03_source_diversity_threshold` | Giữ ngưỡng tập trung 0.6 | `source_diversity_audit(concentration_threshold=0.6)` | PASS |
| `G04_timeline_builder_order` | Phân biệt timeline dữ liệu với timeline mạng xã hội | `timeline_builder(order=descending)` | PASS |
| `G05_citation_formatter_style` | Tạo bibliography APA từ metadata có sẵn | `citation_formatter(style=apa)` | PASS |
| `G06_carry_social_preferences` | Carry limit=6 và Top, thay chủ đề ở lượt cuối | `social_search(search_type=Top, limit=6)` | PASS |
| `G07_correct_web_entity` | Ghi đè Nvidia bằng AMD, giữ news và month | `lookup(query=AMD, topic=news, timeframe=month)` | PASS |
| `G08_correct_web_timeframe` | Đổi timeframe month thành week, giữ chủ đề | `lookup(topic=news, timeframe=week)` | PASS |
| `G09_switch_web_to_social` | Chuyển nguồn web sang Twitter, giữ EU AI Act | `social_search(search_type=Latest)` | PASS |
| `G10_confirm_before_telegram` | Chặn gửi ra ngoài trước khi có xác nhận | `clarify(response_type=yes_no)`, không `send` | PASS |

## B4. Live chat evidence

Các transcript đều là artifact v4, dùng cùng model và cùng fingerprint; token/key đã không được ghi vào transcript.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Bài đăng mới nhất của Sam Altman | v4 | `timeline(screenname=sama, limit=1)` | `transcripts/v4_openrouter_20260729T124325366445.transcript.json` | `answered`; tool trả 1 item. Nội dung trả về cần kiểm chứng thủ công trước khi trích dẫn |
| Thiếu tài khoản Twitter | v4 | Không gọi tool; assistant hỏi tên tài khoản | `transcripts/v4_openrouter_20260729T124339763542.transcript.json` | `answered` với câu hỏi bổ sung, không đoán account |
| Gửi bản tin lên Telegram | v4 | `clarify(response_type=yes_no)`; không gọi `send` | `transcripts/v4_openrouter_20260729T124347939528.transcript.json` | `waiting_for_user`; dừng đúng confirmation boundary |
| Định dạng APA | v4 | `citation_formatter(style=apa)` | `transcripts/v4_openrouter_20260729T124418729681.transcript.json` | `answered`; tool result `status=ok`, `citation_count=1` |

## B5. Tool capability evidence

UI là deliverable core và được triển khai trong `starter_v0/app.py`; bảng dưới đây chỉ phân loại tool theo yêu cầu của report.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: 3 tool mới đầu tiên | `tools/deduplicate_sources/TOOL.md`, `tools/rss_reader/TOOL.md`, `tools/source_diversity_audit/TOOL.md`, `runs/v4_B_group_openrouter_20260729T124219713003.json` | Deduplicate loại 1 URL trùng, RSS trả đúng 3 mục, diversity tính dominant share 66.7%; G01–G03 đều PASS | Không tự search/fetch hoặc đánh giá độ tin cậy; RSS chỉ nhận feed URL rõ ràng |
| Optional built-in | `tools/timeline/TOOL.md`, `tools/social_search/TOOL.md`, `tools/lookup/TOOL.md`, `runs/v4_B_base_openrouter_20260729T124129230657.json` | Web, news và social routing đạt base 20/20; RapidAPI timeline/social search đã chạy được với credentials local | Kết quả live có thể nhiễu hoặc cần kiểm chứng; không đưa key vào UI/report/transcript |
| Bonus: tool mới thứ 4–5 | `tools/timeline_builder/TOOL.md`, `tools/citation_formatter/TOOL.md`, `runs/v4_B_group_openrouter_20260729T124219713003.json` | Hai tool bonus được khai báo, đăng ký và routing/args đều PASS trong G04–G05 | Chỉ xử lý input đã có; không nhầm `timeline_builder` với social `timeline`, citation không tự bịa metadata |

## B6. Reflection

- **Fix nào thuộc `system_prompt.md`?** Scope research, xử lý missing handle/URL, cấm bịa identifier, confirmation trước side effect, không dùng action tool cho coding hoặc câu hỏi ngoài phạm vi, và boundary hẹp của năm tool mới.
- **Fix nào thuộc `tools.yaml`?** Mô tả khác biệt `timeline` với `social_search`, exact URL của `fetch`, mapping timeframe/topic/search type, tham số count và contract input đã có cho năm tool pipeline.
- **Failure nào cần manual review thay vì automatic grading?** Eval tự động chấm được tool name và subset args, nhưng không chứng minh nội dung kết quả đúng hoặc đáng tin. Đặc biệt, response mạng xã hội có thể có tiêu đề/summary bất thường; demo không nên trích dẫn như sự thật nếu chưa kiểm tra nguồn gốc.
- **Cải thiện tiếp theo?** Thêm một lớp kiểm chứng chất lượng nội dung nguồn và các test live ổn định hơn cho API biến động; nếu cần chia sẻ ngoài máy demo thì cấu hình tunnel riêng, kiểm tra lại bằng thiết bị khác và tuyệt đối không expose credentials.
