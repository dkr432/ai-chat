import streamlit as st
from anthropic import Anthropic

# ──────────────────────────────────────────────
# 페이지 기본 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="🤖 Claude AI 질문하기",
    page_icon="🤖",
    layout="centered",
)

# ──────────────────────────────────────────────
# 커스텀 CSS (가독성 완전 개선)
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── 메인 영역 배경 ── */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }

    /* ★★★ 모든 텍스트 기본 색상을 밝게 ★★★ */
    .stApp, .stApp * {
        color: #f0f0f0 !important;
    }
    
    /* ★★★ 위젯 라벨 (selectbox, number_input, text_area 등) ★★★ */
    .stApp label,
    .stApp .stTextArea label,
    .stApp .stSelectbox label,
    .stApp .stNumberInput label,
    .stApp .stTextInput label,
    .stApp [data-testid="stWidgetLabel"],
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stWidgetLabel"] span,
    .stApp [data-testid="stWidgetLabel"] div {
        color: #ffffff !important;
        opacity: 1 !important;
    }

       /* ★★★ 입력 필드 내부 텍스트 (완전 강제) ★★★ */
    .stApp input,
    .stApp textarea,
    .stApp select,
    .stApp [data-baseweb="select"] span,
    .stApp [data-baseweb="input"] input,
    .stApp [data-baseweb="textarea"] textarea {
        color: #1a1a2e !important;
        background-color: rgba(255,255,255,0.95) !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #1a1a2e !important;
    }

    /* ★★★ number_input 전용 (완전 강제) ★★★ */
    .stApp .stNumberInput input,
    .stApp .stNumberInput [data-baseweb="input"] input,
    .stApp [data-testid="stNumberInput"] input,
    .stApp [data-baseweb="input"] input[type="number"],
    .stApp [data-baseweb="input"] input[inputmode="numeric"] {
        color: #1a1a2e !important;
        -webkit-text-fill-color: #1a1a2e !important;
        background-color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        opacity: 1 !important;
    }

    /* ★★★ selectbox 내부 텍스트도 진하게 ★★★ */
    .stApp [data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.95) !important;
    }
    .stApp [data-baseweb="select"] > div > div {
        color: #1a1a2e !important;
        -webkit-text-fill-color: #1a1a2e !important;
        font-weight: 600 !important;
    }

    /* ★★★ placeholder ★★★ */
    .stApp input::placeholder,
    .stApp textarea::placeholder {
        color: #888888 !important;
        -webkit-text-fill-color: #888888 !important;
        opacity: 1 !important;
    }
    }

    /* ★★★ placeholder 텍스트 ★★★ */
    .stApp input::placeholder,
    .stApp textarea::placeholder {
        color: #999999 !important;
        opacity: 1 !important;
    }

    /* ★★★ selectbox 드롭다운 텍스트 ★★★ */
    .stApp [data-baseweb="select"] {
        color: #ffffff !important;
    }
    .stApp [data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
    }
    
    /* ★★★ number input 버튼 ★★★ */
    .stApp [data-baseweb="input"] {
        background-color: rgba(255,255,255,0.1) !important;
    }
    .stApp button[kind="minimal"] {
        color: #ffffff !important;
    }

    /* ── 사이드바 ── */
    [data-testid="stSidebar"] {
        background: #1a1a2e !important;
    }
    [data-testid="stSidebar"] * {
        color: #f0f0f0 !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    /* ── 메인 타이틀 ── */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea, #a78bfa, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #cccccc !important;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* ── 모델 선택 카드 ── */
    .model-card {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }

    /* ── AI 답변 영역 ── */
    .answer-box {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(102,126,234,0.4);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
        color: #ffffff !important;
        line-height: 1.9;
        font-size: 1.05rem;
    }

    /* ── 토큰 사용량 카드 ── */
    .token-card {
        background: rgba(102,126,234,0.15);
        border: 1px solid rgba(102,126,234,0.4);
        border-radius: 12px;
        padding: 1.2rem;
        margin-top: 1rem;
    }
    .token-title {
        color: #a78bfa !important;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    .token-item {
        color: #e8e8e8 !important;
        font-size: 0.95rem;
        padding: 0.25rem 0;
    }
    .token-highlight {
        color: #f093fb !important;
        font-weight: 700;
        font-size: 1rem;
    }

    /* ── 사이드바: 누적 사용량 ── */
    .total-usage {
        text-align: center;
        background: rgba(167,139,250,0.15);
        border: 1px solid rgba(167,139,250,0.4);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 0.5rem;
    }
    .usage-title {
        color: #a78bfa !important;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.6rem;
    }
    .usage-detail {
        color: #ffffff !important;
        font-size: 0.95rem;
        line-height: 1.8;
    }
    .val-input {
        color: #7dd3fc !important;
        font-weight: 700;
    }
    .val-output {
        color: #f0abfc !important;
        font-weight: 700;
    }
    .val-total {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 1.05rem;
    }

    /* ── 대화 기록 ── */
    .history-q {
        background: rgba(102,126,234,0.25);
        border-left: 4px solid #667eea;
        border-radius: 0 10px 10px 0;
        padding: 0.8rem 1rem;
        margin: 0.6rem 0 0.3rem 0;
        color: #ffffff !important;
        font-size: 0.95rem;
        font-weight: 600;
    }
    .history-a {
        background: rgba(167,139,250,0.12);
        border-left: 4px solid #a78bfa;
        border-radius: 0 10px 10px 0;
        padding: 0.8rem 1rem;
        margin: 0 0 0.5rem 0;
        color: #e8e8e8 !important;
        font-size: 0.9rem;
        line-height: 1.7;
    }
    .history-tokens {
        font-size: 0.8rem;
        color: #b0b0b0 !important;
        margin-top: 0.4rem;
    }

    /* ── 경고 박스 ── */
    .warning-box {
        background: rgba(255, 193, 7, 0.12);
        border: 1px solid rgba(255, 193, 7, 0.4);
        border-radius: 10px;
        padding: 1rem;
        color: #ffd54f !important;
        text-align: center;
        margin: 2rem 0;
    }

    /* ── 구분선 색상 ── */
    .stApp hr {
        border-color: rgba(255,255,255,0.15) !important;
    }

    /* ── st.info, st.warning 등 알림 텍스트 ── */
    .stAlert p {
        color: #333333 !important;
    }

    /* ── 하단 정보 ── */
    .footer-info {
        text-align: center;
        color: #999999 !important;
        font-size: 0.8rem;
        padding: 1rem 0;
    }

    /* ── 버튼 텍스트 ── */
    .stApp button[kind="primary"] p,
    .stApp button[kind="primary"] span {
        color: #ffffff !important;
    }
    .stApp button p,
    .stApp button span {
        color: #ffffff !important;
    }
    
    /* ── markdown 내부 텍스트 ── */
    .stApp .stMarkdown p,
    .stApp .stMarkdown li,
    .stApp .stMarkdown h1,
    .stApp .stMarkdown h2,
    .stApp .stMarkdown h3,
    .stApp .stMarkdown h4,
    .stApp .stMarkdown code,
    .stApp .stMarkdown span {
        color: #f0f0f0 !important;
    }
    
    /* ── 코드블록 배경 ── */
    .stApp .stMarkdown pre {
        background: rgba(0,0,0,0.3) !important;
    }
    .stApp .stMarkdown pre code {
        color: #e0e0e0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# API 키 로드
# ──────────────────────────────────────────────
def get_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None

api_key = get_api_key()

# ──────────────────────────────────────────────
# 타이틀
# ──────────────────────────────────────────────
st.markdown('<div class="main-title">🤖 Claude AI에게 질문하기</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">당곡고등학교 AI 학습 도우미</div>', unsafe_allow_html=True)

if not api_key:
    st.markdown("""
    <div class="warning-box">
        ⚠️ API 키가 설정되지 않았습니다.<br>
        Streamlit Cloud의 <b>Secrets</b>에 <code>ANTHROPIC_API_KEY</code>를 추가해주세요.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🔧 설정 방법")
    st.code('ANTHROPIC_API_KEY = "sk-ant-api03-여기에_실제_키_입력"', language="toml")
    st.stop()

# ──────────────────────────────────────────────
# 클라이언트 초기화
# ──────────────────────────────────────────────
client = Anthropic(api_key=api_key)

# ──────────────────────────────────────────────
# 세션 상태
# ──────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "total_input" not in st.session_state:
    st.session_state.total_input = 0
if "total_output" not in st.session_state:
    st.session_state.total_output = 0

# ──────────────────────────────────────────────
# 모델 선택
# ──────────────────────────────────────────────
MODEL_OPTIONS = {
    "Claude Sonnet 4 (claude-sonnet-4-20250514)": "claude-sonnet-4-20250514",
    "Claude Opus 4 (claude-opus-4-20250514)": "claude-opus-4-20250514",
}

st.markdown('<div class="model-card">', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    selected_model_name = st.selectbox(
        "🧠 사용할 AI 모델 선택",
        options=list(MODEL_OPTIONS.keys()),
        index=0,
    )
with col2:
    max_tokens = st.number_input(
        "최대 토큰",
        min_value=100,
        max_value=8192,
        value=2048,
        step=100,
    )
st.markdown('</div>', unsafe_allow_html=True)

selected_model = MODEL_OPTIONS[selected_model_name]

# ──────────────────────────────────────────────
# 시스템 프롬프트
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """당신은 당곡고등학교 학생들의 학습을 돕는 친절하고 유능한 AI 도우미입니다.
학생들이 이해하기 쉽도록 명확하고 정확하게 설명해주세요.
필요하다면 예시를 들어 설명해주세요.
한국어로 답변해주세요."""

# ──────────────────────────────────────────────
# 질문 입력
# ──────────────────────────────────────────────
st.markdown("---")

question = st.text_area(
    "💬 질문을 입력하세요",
    height=120,
    placeholder="예: 피타고라스의 정리에 대해 설명해줘, 광합성 과정을 알려줘",
)

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    send_clicked = st.button("🚀 질문하기", use_container_width=True, type="primary")

# ──────────────────────────────────────────────
# API 호출
# ──────────────────────────────────────────────
if send_clicked and question.strip():
    with st.spinner("🤔 AI가 생각하고 있어요..."):
        try:
            response = client.messages.create(
                model=selected_model,
                max_tokens=max_tokens,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": question.strip()}],
            )

            answer = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            st.session_state.total_input += input_tokens
            st.session_state.total_output += output_tokens
            st.session_state.history.append({
                "question": question.strip(),
                "answer": answer,
                "model": selected_model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            })

            st.markdown("### 📝 AI 답변")
            st.markdown(answer)

            st.markdown(f"""
            <div class="token-card">
                <div class="token-title">📊 이번 질문 토큰 사용량</div>
                <div class="token-item">
                    🔵 입력(Input): <span class="token-highlight">{input_tokens:,}</span> 토큰
                </div>
                <div class="token-item">
                    🟣 출력(Output): <span class="token-highlight">{output_tokens:,}</span> 토큰
                </div>
                <div class="token-item">
                    ⚪ 합계: <span class="token-highlight">{input_tokens + output_tokens:,}</span> 토큰
                </div>
                <div class="token-item" style="margin-top:0.5rem; font-size:0.85rem; color:#aaa !important;">
                    사용 모델: {selected_model_name}
                </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ 오류 발생: {error_msg}")
            if "invalid_api_key" in error_msg or "authentication" in error_msg.lower():
                st.warning("API 키가 올바르지 않습니다.")
            elif "rate_limit" in error_msg.lower():
                st.warning("호출 한도 도달. 잠시 후 다시 시도하세요.")

elif send_clicked and not question.strip():
    st.warning("⚠️ 질문을 입력해주세요!")

# ──────────────────────────────────────────────
# 사이드바
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 누적 사용량")

    if st.session_state.history:
        total_in = st.session_state.total_input
        total_out = st.session_state.total_output

        st.markdown(f"""
        <div class="total-usage">
            <div class="usage-title">총 {len(st.session_state.history)}회 질문</div>
            <div class="usage-detail">
                🔵 총 입력: <span class="val-input">{total_in:,}</span> 토큰<br>
                🟣 총 출력: <span class="val-output">{total_out:,}</span> 토큰<br>
                ⚪ 총 합계: <span class="val-total">{total_in + total_out:,}</span> 토큰
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("아직 질문 기록이 없습니다.")

    st.markdown("---")
    st.markdown("## 📜 대화 기록")

    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history), 1):
            idx = len(st.session_state.history) - i + 1
            q_short = item["question"][:50] + ("..." if len(item["question"]) > 50 else "")
            a_short = item["answer"][:100] + ("..." if len(item["answer"]) > 100 else "")

            st.markdown(f"""
            <div class="history-q"><b>Q{idx}.</b> {q_short}</div>
            <div class="history-a">
                {a_short}
                <div class="history-tokens">
                    입력 {item['input_tokens']:,} / 출력 {item['output_tokens']:,} 토큰
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("질문을 하면 여기에 기록됩니다.")

    st.markdown("---")
    if st.button("🗑️ 대화 기록 초기화", use_container_width=True):
        st.session_state.history = []
        st.session_state.total_input = 0
        st.session_state.total_output = 0
        st.rerun()

st.markdown("---")
st.markdown("""
<div class="footer-info">
    💡 Anthropic Claude API 사용 | 당곡고등학교 AI 학습 도우미
</div>
""", unsafe_allow_html=True)
