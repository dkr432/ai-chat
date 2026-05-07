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
# 커스텀 CSS (깔끔한 UI)
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    
    /* 메인 타이틀 */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #aaa;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* 모델 선택 카드 */
    .model-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    
    /* 답변 영역 */
    .answer-box {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(102,126,234,0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
        color: #e0e0e0;
        line-height: 1.8;
        font-size: 1rem;
    }
    
    /* 토큰 사용량 카드 */
    .token-card {
        background: rgba(102,126,234,0.1);
        border: 1px solid rgba(102,126,234,0.3);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .token-title {
        color: #667eea;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .token-item {
        color: #ccc;
        font-size: 0.85rem;
        padding: 0.2rem 0;
    }
    .token-highlight {
        color: #f093fb;
        font-weight: 700;
    }
    
    /* 히스토리 아이템 */
    .history-q {
        background: rgba(102,126,234,0.15);
        border-left: 3px solid #667eea;
        border-radius: 0 8px 8px 0;
        padding: 0.7rem 1rem;
        margin: 0.5rem 0 0.3rem 0;
        color: #c5caf5;
        font-size: 0.9rem;
    }
    .history-a {
        background: rgba(118,75,162,0.1);
        border-left: 3px solid #764ba2;
        border-radius: 0 8px 8px 0;
        padding: 0.7rem 1rem;
        margin: 0 0 0.8rem 0;
        color: #d4c5e8;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* 누적 사용량 */
    .total-usage {
        text-align: center;
        background: rgba(240,147,251,0.08);
        border: 1px solid rgba(240,147,251,0.2);
        border-radius: 12px;
        padding: 0.8rem;
        margin-top: 0.5rem;
    }
    
    /* 경고 박스 */
    .warning-box {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 10px;
        padding: 1rem;
        color: #ffc107;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# API 키 로드 (Streamlit Secrets)
# ──────────────────────────────────────────────
def get_api_key():
    """Streamlit Cloud의 Secrets에서 API 키를 가져옵니다."""
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

# API 키 체크
if not api_key:
    st.markdown("""
    <div class="warning-box">
        ⚠️ API 키가 설정되지 않았습니다.<br>
        Streamlit Cloud의 <b>Secrets</b>에 <code>ANTHROPIC_API_KEY</code>를 추가해주세요.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔧 설정 방법")
    st.code("""
# Streamlit Cloud → 앱 Settings → Secrets에 아래 내용 입력:
ANTHROPIC_API_KEY = "sk-ant-api03-여기에_실제_키_입력"
    """, language="toml")
    
    st.markdown("""
    **로컬 테스트 시:** `.streamlit/secrets.toml` 파일을 만들어 같은 형식으로 입력하세요.
    """)
    st.stop()

# ──────────────────────────────────────────────
# Anthropic 클라이언트 초기화
# ──────────────────────────────────────────────
client = Anthropic(api_key=api_key)

# ──────────────────────────────────────────────
# 세션 상태 초기화
# ──────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []           # (질문, 답변, 모델, input_tokens, output_tokens)
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
    placeholder="예: 피타고라스의 정리에 대해 설명해줘, 광합성 과정을 알려줘, Python의 리스트와 튜플의 차이점은?",
)

# 전송 버튼
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    send_clicked = st.button("🚀 질문하기", use_container_width=True, type="primary")

# ──────────────────────────────────────────────
# API 호출 및 답변 생성
# ──────────────────────────────────────────────
if send_clicked and question.strip():
    with st.spinner("🤔 AI가 생각하고 있어요..."):
        try:
            response = client.messages.create(
                model=selected_model,
                max_tokens=max_tokens,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": question.strip()}
                ],
            )

            # 답변 추출
            answer = response.content[0].text

            # 토큰 사용량
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # 누적 토큰
            st.session_state.total_input += input_tokens
            st.session_state.total_output += output_tokens

            # 히스토리 저장
            st.session_state.history.append({
                "question": question.strip(),
                "answer": answer,
                "model": selected_model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            })

            # ── 답변 표시 ──
            st.markdown("### 📝 AI 답변")
            st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

            # ── 토큰 사용량 표시 ──
            st.markdown(f"""
            <div class="token-card">
                <div class="token-title">📊 이번 질문 토큰 사용량</div>
                <div class="token-item">
                    🔵 입력(Input) 토큰: <span class="token-highlight">{input_tokens:,}</span>
                </div>
                <div class="token-item">
                    🟣 출력(Output) 토큰: <span class="token-highlight">{output_tokens:,}</span>
                </div>
                <div class="token-item">
                    ⚪ 합계: <span class="token-highlight">{input_tokens + output_tokens:,}</span>
                </div>
                <div class="token-item" style="margin-top:0.3rem; color:#888; font-size:0.8rem;">
                    사용 모델: {selected_model_name}
                </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ 오류가 발생했습니다: {error_msg}")
            
            if "invalid_api_key" in error_msg or "authentication" in error_msg.lower():
                st.warning("API 키가 올바르지 않습니다. Secrets 설정을 확인해주세요.")
            elif "rate_limit" in error_msg.lower():
                st.warning("API 호출 한도에 도달했습니다. 잠시 후 다시 시도해주세요.")
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                st.warning("선택한 모델을 사용할 수 없습니다. 다른 모델을 선택해주세요.")

elif send_clicked and not question.strip():
    st.warning("⚠️ 질문을 입력해주세요!")

# ──────────────────────────────────────────────
# 누적 사용량 & 대화 기록 (사이드바)
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 누적 사용량")
    
    if st.session_state.history:
        total_in = st.session_state.total_input
        total_out = st.session_state.total_output
        
        st.markdown(f"""
        <div class="total-usage">
            <div style="color:#667eea; font-weight:700; margin-bottom:0.5rem;">
                총 {len(st.session_state.history)}회 질문
            </div>
            <div style="color:#ccc; font-size:0.85rem;">
                🔵 총 입력: <b style="color:#667eea">{total_in:,}</b> 토큰<br>
                🟣 총 출력: <b style="color:#f093fb">{total_out:,}</b> 토큰<br>
                ⚪ 총 합계: <b style="color:#fff">{total_in + total_out:,}</b> 토큰
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("아직 질문 기록이 없습니다.")
    
    st.markdown("---")
    st.markdown("## 📜 대화 기록")
    
    if st.session_state.history:
        # 최신순으로 표시
        for i, item in enumerate(reversed(st.session_state.history), 1):
            idx = len(st.session_state.history) - i + 1
            q_short = item["question"][:50] + ("..." if len(item["question"]) > 50 else "")
            a_short = item["answer"][:100] + ("..." if len(item["answer"]) > 100 else "")
            
            st.markdown(f"""
            <div class="history-q">
                <b>Q{idx}.</b> {q_short}
            </div>
            <div class="history-a">
                {a_short}
                <div style="font-size:0.7rem; color:#888; margin-top:0.3rem;">
                    입력 {item['input_tokens']:,} / 출력 {item['output_tokens']:,} 토큰
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("질문을 하면 여기에 기록됩니다.")
    
    st.markdown("---")
    
    # 기록 초기화 버튼
    if st.button("🗑️ 대화 기록 초기화", use_container_width=True):
        st.session_state.history = []
        st.session_state.total_input = 0
        st.session_state.total_output = 0
        st.rerun()

# ──────────────────────────────────────────────
# 하단 정보
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666; font-size:0.8rem; padding:1rem 0;">
    💡 이 앱은 Anthropic의 Claude API를 사용합니다.<br>
    학습 목적으로 활용해주세요. | 당곡고등학교 AI 학습 도우미
</div>
""", unsafe_allow_html=True)
