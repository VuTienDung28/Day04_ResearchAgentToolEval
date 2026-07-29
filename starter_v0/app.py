from __future__ import annotations

import html
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]
LANGUAGE_NAMES = {"vi": "Tiếng Việt", "en": "English"}
UI_TEXT = {
    "vi": {
        "language": "Ngôn ngữ",
        "light_mode": "Chế độ sáng",
        "control_plane": "Bảng điều khiển",
        "run_configuration": "Thiết lập phiên làm việc",
        "provider": "Nhà cung cấp mô hình",
        "model_override": "Model tùy chọn",
        "model_placeholder": "Để trống để dùng model mặc định",
        "artifact_version": "Phiên bản artifact",
        "history_window": "Số lượt hội thoại cần ghi nhớ",
        "max_tool_rounds": "Số vòng gọi công cụ tối đa",
        "configuration_note": "Khi đổi cấu hình, yêu cầu tiếp theo sẽ bắt đầu một transcript mới. Thông tin đăng nhập chỉ được đọc từ môi trường trên máy của bạn.",
        "configured_artifact": "Artifact đang sử dụng",
        "transcript": "Transcript",
        "chat_placeholder": "Bạn muốn tìm hiểu chủ đề, tài khoản hoặc đường dẫn nào?",
        "spinner": "Đang tìm hướng xử lý và kiểm tra nguồn…",
        "transcript_saved": "Đã lưu transcript",
        "trace": "Chi tiết xử lý",
        "turn": "lượt",
        "round": "Vòng",
        "call": "Gọi công cụ",
        "result": "Kết quả",
        "error": "Lỗi",
        "status.answered": "Đã trả lời",
        "status.waiting_for_user": "Cần thêm thông tin",
        "status.max_tool_rounds": "Đã đạt giới hạn xử lý",
        "status.provider_error": "Lỗi nhà cung cấp",
        "status.started": "Đang xử lý",
        "hero_eyebrow": "Hệ thống nghiên cứu dựa trên bằng chứng",
        "hero_title": "Mỗi câu trả lời đều có nguồn để kiểm chứng.",
        "hero_description": "Trợ lý nghiên cứu trực tiếp cho bạn thấy cách chọn công cụ, tham số đã dùng, kết quả nhận được và dấu vân tay artifact — không giấu mọi thứ sau một ô chat.",
        "signal_route": "định tuyến",
        "signal_execute": "thực thi",
        "signal_inspect": "kiểm tra",
        "signal_improve": "cải thiện",
    },
    "en": {
        "language": "Language",
        "light_mode": "Light mode",
        "control_plane": "Control plane",
        "run_configuration": "Run configuration",
        "provider": "Model provider",
        "model_override": "Model override",
        "model_placeholder": "Use the provider default",
        "artifact_version": "Artifact version",
        "history_window": "Conversation turns to remember",
        "max_tool_rounds": "Maximum tool rounds",
        "configuration_note": "Configuration changes start a new transcript on the next request. Credentials are read only from your local environment.",
        "configured_artifact": "Configured artifact",
        "transcript": "Transcript",
        "chat_placeholder": "Ask about a topic, account, or URL…",
        "spinner": "Routing the request and checking sources…",
        "transcript_saved": "Transcript saved",
        "trace": "Processing details",
        "turn": "turn",
        "round": "Round",
        "call": "Tool call",
        "result": "Result",
        "error": "Error",
        "status.answered": "Answered",
        "status.waiting_for_user": "Needs input",
        "status.max_tool_rounds": "Round limit reached",
        "status.provider_error": "Provider error",
        "status.started": "Running",
        "hero_eyebrow": "Evidence-driven research system",
        "hero_title": "Trace every answer to its source.",
        "hero_description": "A live research agent that exposes its routing decisions, tool arguments, execution results, and artifact fingerprint instead of hiding them behind a chat bubble.",
        "signal_route": "route",
        "signal_execute": "execute",
        "signal_inspect": "inspect",
        "signal_improve": "improve",
    },
}


def text(language: str, key: str) -> str:
    return UI_TEXT.get(language, UI_TEXT["en"]).get(key, UI_TEXT["en"].get(key, key))

APP_STYLES = """
<style>
:root {
    --ink: #07110f;
    --panel: #0c1916;
    --panel-soft: #11231e;
    --line: rgba(164, 255, 209, 0.16);
    --text: #e8f6ee;
    --muted: #91a99d;
    --acid: #8dffbd;
    --amber: #ffc66d;
    --danger: #ff7b72;
    --serif: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
    --mono: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(circle at 13% 8%, rgba(41, 130, 91, 0.18), transparent 27rem),
        radial-gradient(circle at 90% 32%, rgba(255, 198, 109, 0.08), transparent 24rem),
        linear-gradient(145deg, #06100e 0%, #091512 48%, #050b0a 100%);
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.22;
    background-image:
        linear-gradient(rgba(141, 255, 189, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(141, 255, 189, 0.035) 1px, transparent 1px);
    background-size: 42px 42px;
    mask-image: linear-gradient(to bottom, black, transparent 78%);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stAppViewContainer"] > .main {
    position: relative;
    z-index: 1;
}

.block-container {
    max-width: 1180px;
    padding-top: 2.2rem;
    padding-bottom: 7rem;
}

[data-testid="stSidebar"] {
    background: rgba(5, 13, 11, 0.92);
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    font-family: var(--serif) !important;
    letter-spacing: -0.025em !important;
}

p, label, [data-testid="stWidgetLabel"] {
    color: var(--text);
}

.hero {
    position: relative;
    overflow: hidden;
    padding: clamp(1.8rem, 5vw, 4.5rem);
    margin-bottom: 1.4rem;
    border: 1px solid var(--line);
    border-radius: 2px 2px 30px 2px;
    background:
        linear-gradient(110deg, rgba(10, 28, 23, 0.96), rgba(8, 19, 16, 0.75)),
        radial-gradient(circle at 80% 10%, rgba(141, 255, 189, 0.18), transparent 45%);
    box-shadow: 0 28px 80px rgba(0, 0, 0, 0.28);
    animation: reveal 520ms ease-out both;
}

.hero::after {
    content: "R/A — 04";
    position: absolute;
    right: -0.2rem;
    bottom: -1.65rem;
    color: rgba(141, 255, 189, 0.06);
    font: 700 clamp(4rem, 12vw, 9rem)/1 var(--mono);
    letter-spacing: -0.09em;
}

.eyebrow {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    color: var(--acid);
    font: 600 0.72rem/1.4 var(--mono);
    letter-spacing: 0.17em;
    text-transform: uppercase;
}

.eyebrow::before {
    content: "";
    width: 2rem;
    height: 1px;
    background: var(--acid);
}

.hero h1 {
    max-width: 760px;
    margin: 0.8rem 0 0.9rem;
    color: var(--text);
    font: 500 clamp(2.45rem, 7vw, 5.3rem)/0.95 var(--serif) !important;
}

.hero p {
    max-width: 650px;
    margin: 0;
    color: var(--muted);
    font-size: clamp(0.95rem, 2vw, 1.08rem);
    line-height: 1.7;
}

.signal-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    margin-top: 1.45rem;
}

.signal {
    padding: 0.44rem 0.72rem;
    border: 1px solid var(--line);
    background: rgba(141, 255, 189, 0.045);
    color: var(--muted);
    font: 500 0.68rem/1 var(--mono);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.signal strong {
    color: var(--acid);
    font-weight: 600;
}

.sidebar-mark {
    margin-bottom: 1.7rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--line);
}

.sidebar-mark .index {
    color: var(--acid);
    font: 600 0.68rem/1 var(--mono);
    letter-spacing: 0.18em;
    text-transform: uppercase;
}

.sidebar-mark h2 {
    margin: 0.45rem 0 0;
    font-size: 1.55rem;
}

.artifact-card {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.65rem 1rem;
    align-items: center;
    margin: 1rem 0 1.4rem;
    padding: 0.9rem 1rem;
    border-left: 3px solid var(--acid);
    background: rgba(17, 35, 30, 0.72);
}

.artifact-card .label {
    color: var(--muted);
    font: 600 0.66rem/1 var(--mono);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.artifact-card .value {
    overflow-wrap: anywhere;
    color: var(--text);
    font: 500 0.76rem/1.5 var(--mono);
}

[data-testid="stChatMessage"] {
    margin: 0.72rem 0;
    padding: 1rem 1.15rem;
    border: 1px solid var(--line);
    border-radius: 2px 18px 18px 18px;
    background: rgba(12, 25, 22, 0.78);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.13);
    animation: rise 300ms ease-out both;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    margin-left: clamp(0rem, 8vw, 5rem);
    border-color: rgba(255, 198, 109, 0.24);
    border-radius: 18px 2px 18px 18px;
    background: rgba(44, 36, 22, 0.42);
}

[data-testid="stChatMessageAvatarUser"] {
    background: var(--amber);
    color: var(--ink);
}

[data-testid="stChatMessageAvatarAssistant"] {
    background: var(--acid);
    color: var(--ink);
}

[data-testid="stExpander"] {
    margin-top: 0.85rem;
    border: 1px solid var(--line) !important;
    border-radius: 2px !important;
    background: rgba(4, 12, 10, 0.58);
}

[data-testid="stExpander"] summary {
    font-family: var(--mono);
    font-size: 0.77rem;
    letter-spacing: 0.03em;
}

[data-testid="stJson"] {
    border-left: 2px solid rgba(141, 255, 189, 0.3);
    background: rgba(2, 8, 7, 0.74);
    font-family: var(--mono);
}

.trace-round {
    margin: 0.85rem 0 0.45rem;
    color: var(--acid);
    font: 600 0.68rem/1.2 var(--mono);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.status-line {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    color: var(--muted);
    font: 500 0.72rem/1.4 var(--mono);
}

.status-dot {
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 50%;
    background: var(--acid);
    box-shadow: 0 0 0 4px rgba(141, 255, 189, 0.09), 0 0 14px rgba(141, 255, 189, 0.55);
}

[data-testid="stChatInput"] {
    border: 1px solid rgba(141, 255, 189, 0.28);
    border-radius: 2px 18px 18px 18px;
    background: rgba(8, 20, 17, 0.95);
    box-shadow: 0 16px 50px rgba(0, 0, 0, 0.35);
}

[data-testid="stChatInput"] textarea {
    font-family: var(--serif);
    font-size: 1rem;
}

.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    border: 1px solid var(--acid);
    border-radius: 2px;
    background: transparent;
    color: var(--acid);
    font-family: var(--mono);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    transition: background 160ms ease, color 160ms ease, transform 160ms ease;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background: var(--acid);
    color: var(--ink);
    transform: translateY(-1px);
}

input, textarea, [data-baseweb="select"] > div {
    border-radius: 2px !important;
}

[data-testid="stAlert"] {
    border-radius: 2px;
}

.footer-note {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font: 0.7rem/1.6 var(--mono);
}

@keyframes reveal {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes rise {
    from { opacity: 0; transform: translateY(7px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

@media (max-width: 700px) {
    .block-container { padding-top: 1rem; }
    .hero { padding: 1.45rem; border-radius: 2px 2px 20px 2px; }
    .hero::after { display: none; }
    [data-testid="stChatMessage"] { padding: 0.85rem; }
}
</style>
"""

LIGHT_STYLES = """
<style>
:root {
    --ink: #f6fbf8;
    --panel: #ffffff;
    --panel-soft: #edf7f1;
    --line: rgba(18, 74, 51, 0.18);
    --text: #14251e;
    --muted: #536b60;
    --acid: #087a48;
    --amber: #b76700;
}

.stApp {
    background:
        radial-gradient(circle at 13% 8%, rgba(65, 177, 119, 0.13), transparent 27rem),
        radial-gradient(circle at 90% 32%, rgba(214, 139, 31, 0.09), transparent 24rem),
        linear-gradient(145deg, #f8fcfa 0%, #eef7f2 48%, #ffffff 100%);
}

.stApp::before {
    opacity: 0.45;
    background-image:
        linear-gradient(rgba(8, 122, 72, 0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(8, 122, 72, 0.06) 1px, transparent 1px);
}

[data-testid="stSidebar"] {
    background: rgba(247, 252, 249, 0.96);
}

.hero {
    background:
        linear-gradient(110deg, rgba(255, 255, 255, 0.98), rgba(237, 247, 241, 0.9)),
        radial-gradient(circle at 80% 10%, rgba(8, 122, 72, 0.13), transparent 45%);
    box-shadow: 0 28px 80px rgba(25, 78, 54, 0.12);
}

.hero::after { color: rgba(8, 122, 72, 0.07); }
.signal { background: rgba(8, 122, 72, 0.05); }
.artifact-card { background: rgba(223, 241, 231, 0.82); }

[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.88);
    box-shadow: 0 12px 32px rgba(25, 78, 54, 0.09);
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    border-color: rgba(183, 103, 0, 0.25);
    background: rgba(255, 246, 229, 0.9);
}

[data-testid="stExpander"] { background: rgba(247, 252, 249, 0.9); }
[data-testid="stJson"] { background: rgba(237, 247, 241, 0.9); }

[data-testid="stBottom"] {
    background: linear-gradient(to top, #f8fcfa 75%, rgba(248, 252, 250, 0)) !important;
}

[data-testid="stBottomBlockContainer"] {
    background: transparent !important;
}

[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-baseweb="textarea"] {
    color: var(--text) !important;
    background: #ffffff !important;
    box-shadow: 0 16px 50px rgba(25, 78, 54, 0.14);
}

input, textarea, [data-baseweb="select"] > div {
    color: var(--text) !important;
    background-color: #ffffff !important;
}

input::placeholder,
textarea::placeholder {
    color: var(--muted) !important;
    opacity: 0.75 !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] svg {
    color: var(--text) !important;
    fill: var(--text) !important;
}
</style>
"""


def hero_html(language: str) -> str:
    return f"""
    <section class="hero">
        <div class="eyebrow">{text(language, "hero_eyebrow")}</div>
        <h1>{text(language, "hero_title")}</h1>
        <p>{text(language, "hero_description")}</p>
        <div class="signal-row">
            <span class="signal"><strong>01</strong> {text(language, "signal_route")}</span>
            <span class="signal"><strong>02</strong> {text(language, "signal_execute")}</span>
            <span class="signal"><strong>03</strong> {text(language, "signal_inspect")}</span>
            <span class="signal"><strong>04</strong> {text(language, "signal_improve")}</span>
        </div>
    </section>
    """


def inject_styles(light_mode: bool = False) -> None:
    styles = APP_STYLES + (LIGHT_STYLES if light_mode else "")
    if hasattr(st, "html"):
        st.html(styles)
    else:
        st.markdown(styles, unsafe_allow_html=True)


def redact_secrets(value: Any) -> Any:
    text = json.dumps(value, ensure_ascii=False, default=str)
    for name, secret in os.environ.items():
        upper_name = name.upper()
        if secret and any(marker in upper_name for marker in ("API_KEY", "TOKEN", "SECRET")):
            text = text.replace(secret, "[REDACTED]")
    return json.loads(text)


def create_transcript(
    *,
    provider_name: str,
    model: str | None,
    version: str,
    history_window: int,
    max_tool_rounds: int,
) -> tuple[dict[str, Any], Path]:
    artifact_version = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        safe_slug(version),
        safe_slug(provider_name),
        timestamp,
    ])
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, transcript_path


def render_trace(
    turn: dict[str, Any],
    language: str,
    *,
    expanded: bool = False,
) -> None:
    status = turn.get("status", "started")
    label = text(language, f"status.{status}")
    with st.expander(
        f"{text(language, 'trace')} · {text(language, 'turn')} {turn['turn_index']:02d} · {label}",
        expanded=expanded,
    ):
        st.markdown(
            f'<div class="status-line"><span class="status-dot"></span>{label}</div>',
            unsafe_allow_html=True,
        )
        for round_record in turn.get("rounds", []):
            st.markdown(
                f'<div class="trace-round">{text(language, "round")} {round_record["round"]:02d}</div>',
                unsafe_allow_html=True,
            )
            if round_record.get("assistant_text"):
                st.caption(round_record["assistant_text"])
            for call in round_record.get("tool_calls", []):
                st.markdown(f"**{text(language, 'call')} — `{call['name']}`**")
                st.json(call.get("args", {}), expanded=False)
            for event in round_record.get("tool_results", []):
                result = event.get("result", {})
                has_error = isinstance(result, dict) and bool(result.get("error"))
                marker = text(language, "error" if has_error else "result")
                st.markdown(f"**{marker} — `{event.get('tool', 'unknown')}`**")
                st.json(event, expanded=False)


def render_turn(turn: dict[str, Any], language: str) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        if turn.get("assistant_text"):
            st.markdown(turn["assistant_text"])
        elif turn.get("error"):
            st.error(turn["error"])
        render_trace(turn, language)


def initialize_state() -> None:
    defaults = {
        "agent_history": [],
        "transcript": None,
        "transcript_path": None,
        "config_key": None,
        "ui_language": "vi",
        "light_mode": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main() -> None:
    st.set_page_config(page_title="Research Agent", layout="wide")
    initialize_state()
    inject_styles(st.session_state.light_mode)

    language = st.session_state.ui_language
    with st.sidebar:
        language = st.selectbox(
            text(language, "language"),
            tuple(LANGUAGE_NAMES),
            format_func=lambda code: LANGUAGE_NAMES[code],
            key="ui_language",
        )
        st.toggle(text(language, "light_mode"), key="light_mode")
        st.markdown(
            f"""
            <div class="sidebar-mark">
                <div class="index">{text(language, "control_plane")}</div>
                <h2>{text(language, "run_configuration")}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        provider_name = st.selectbox(
            text(language, "provider"),
            PROVIDERS,
            index=0,
            key="provider_name",
        )
        model_override = st.text_input(
            text(language, "model_override"),
            value="",
            placeholder=text(language, "model_placeholder"),
            key="model_override",
        )
        version_input = st.text_input(
            text(language, "artifact_version"),
            value="v0",
            key="artifact_version_input",
        )
        history_window = st.slider(
            text(language, "history_window"),
            min_value=1,
            max_value=10,
            value=5,
            key="history_window",
        )
        max_tool_rounds = st.slider(
            text(language, "max_tool_rounds"),
            min_value=1,
            max_value=8,
            value=4,
            key="max_tool_rounds",
        )
        st.markdown(
            f'<div class="footer-note">{text(language, "configuration_note")}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(hero_html(language), unsafe_allow_html=True)

    version = version_input.strip() or "v0"
    artifact_version = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    st.markdown(
        f"""
        <div class="artifact-card">
            <div class="label">{text(language, "configured_artifact")}</div>
            <div class="value">{html.escape(artifact_version.artifact_version)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.transcript:
        for saved_turn in st.session_state.transcript["turns"]:
            render_turn(saved_turn, language)
        st.caption(f"{text(language, 'transcript')} · {st.session_state.transcript_path}")

    user_text = st.chat_input(text(language, "chat_placeholder"))
    if not user_text:
        return

    provider = make_provider(provider_name)
    selected_model = model_override.strip() or getattr(provider, "default_model", None)
    config_key = (
        provider_name,
        selected_model,
        artifact_version.artifact_version,
        history_window,
        max_tool_rounds,
    )

    if st.session_state.config_key != config_key:
        transcript, transcript_path = create_transcript(
            provider_name=provider_name,
            model=selected_model,
            version=version,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )
        st.session_state.transcript = transcript
        st.session_state.transcript_path = transcript_path
        st.session_state.agent_history = []
        st.session_state.config_key = config_key

    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    declarations = load_tool_declarations(TOOLS_PATH)
    tools = to_openai_tools(declarations)
    turn_index = len(st.session_state.transcript["turns"]) + 1
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.agent_history, history_window),
        {"role": "user", "content": user_text},
    ]

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner(text(language, "spinner")):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=tools,
                    model=selected_model,
                    max_tool_rounds=max_tool_rounds,
                )
                turn_record.update(redact_secrets(result))
                assistant_text = turn_record["assistant_text"]
                st.session_state.agent_history.extend([
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": assistant_text},
                ])
            except Exception as exc:
                error = redact_secrets(f"{type(exc).__name__}: {exc}")
                turn_record.update({"status": "provider_error", "error": error})

        if turn_record.get("assistant_text"):
            st.markdown(turn_record["assistant_text"])
        elif turn_record.get("error"):
            st.error(turn_record["error"])
        render_trace(turn_record, language, expanded=True)

    turn_record["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    st.caption(f"{text(language, 'transcript_saved')} · {st.session_state.transcript_path}")


if __name__ == "__main__":
    main()
