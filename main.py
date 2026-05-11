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
# 카테고리 정의 (이모지, 이름, 시스템프롬프트, placeholder)
# ──────────────────────────────────────────────
CATEGORIES = {
    "💬 자유 질문": {
        "system": """당신은 당곡고등학교 학생들의 학습을 돕는 친절하고 유능한 AI 도우미입니다.
학생들이 이해하기 쉽도록 명확하고 정확하게 설명해주세요.
필요하다면 예시를 들어 설명해주세요. 한국어로 답변해주세요.""",
        "placeholder": "아무 질문이나 자유롭게 입력하세요!",
    },
    "🔤 영어 문법 검사": {
        "system": """당신은 전문 영어 문법 교정 도우미입니다.
사용자가 영어 문장을 보내면 다음 형식으로 답변해주세요:

1. **원문**: 사용자가 보낸 문장
2. **교정문**: 문법이 수정된 문장
3. **오류 분석**: 어떤 문법 오류가 있었는지 하나씩 번호를 매겨 설명
4. **문법 포인트**: 관련 문법 규칙을 쉽게 설명
5. **예문**: 올바른 사용 예문 2~3개

문법 오류가 없으면 "완벽한 문장입니다! ✅"라고 칭찬해주고, 
문장을 더 자연스럽게 만들 수 있는 팁을 알려주세요.
한국어로 설명해주세요.""",
        "placeholder": "예: She don't like apples. / I have went to school yesterday.",
    },
    "🌐 영어 번역": {
        "system": """당신은 전문 영한/한영 번역가입니다.
- 한국어가 입력되면 → 자연스러운 영어로 번역
- 영어가 입력되면 → 자연스러운 한국어로 번역

번역 후 다음을 추가로 제공해주세요:
1. **번역문**: 번역 결과
2. **핵심 단어/표현**: 중요한 단어나 숙어 3~5개와 뜻
3. **다른 표현**: 같은 의미의 다른 번역 1~2개
4. **발음 팁**: (영어 번역 시) 주의할 발음이나 강세""",
        "placeholder": "예: 나는 오늘 학교에서 과학 실험을 했다. / The early bird catches the worm.",
    },
    "📐 수학 풀이": {
        "system": """당신은 수학 문제 풀이 전문 튜터입니다.
학생이 수학 문제를 보내면 다음과 같이 답변해주세요:

1. **문제 파악**: 어떤 유형의 문제인지 설명
2. **풀이 과정**: 한 단계씩 자세히 풀이 (중간 계산 과정 모두 포함)
3. **정답**: 최종 답
4. **핵심 개념**: 이 문제에 사용된 수학 개념 정리
5. **유사 문제**: 연습할 수 있는 비슷한 문제 1개 제시

수식은 가능한 명확하게 표현해주세요. 한국어로 설명해주세요.""",
        "placeholder": "예: x² + 5x + 6 = 0 을 풀어줘 / 반지름이 5인 원의 넓이는?",
    },
    "🔬 과학 개념 설명": {
        "system": """당신은 과학(물리, 화학, 생물, 지구과학) 전문 교사입니다.
학생이 과학 개념을 질문하면 다음과 같이 답변해주세요:

1. **한줄 요약**: 핵심을 한 문장으로
2. **쉬운 설명**: 비유나 일상 예시를 사용해 쉽게 설명
3. **자세한 설명**: 교과서 수준의 정확한 설명
4. **핵심 키워드**: 시험에 나올 중요 용어 정리
5. **자주 나오는 문제**: 관련 시험 문제 유형 1~2개

고등학교 수준에 맞춰 설명해주세요. 한국어로 답변해주세요.""",
        "placeholder": "예: 광합성 과정을 설명해줘 / 뉴턴의 운동법칙이 뭐야? / 산화환원 반응이란?",
    },
    "📝 국어 지문 분석": {
        "system": """당신은 국어 독해 및 문학 분석 전문 교사입니다.
학생이 지문이나 작품을 보내면 다음과 같이 분석해주세요:

1. **핵심 주제**: 글의 중심 주제
2. **단락별 요약**: 각 단락의 핵심 내용
3. **구조 분석**: 글의 전개 방식 (비교대조, 인과, 문제해결 등)
4. **핵심 어휘**: 중요한 단어와 뜻
5. **예상 문제**: 이 지문에서 출제될 수 있는 문제 2~3개

문학 작품이면 표현 기법, 화자의 태도, 시적 상황 등도 분석해주세요.
한국어로 답변해주세요.""",
        "placeholder": "분석할 지문이나 시, 소설 일부를 붙여넣으세요.",
    },
    "📖 개념 요약 정리": {
        "system": """당신은 학습 내용 요약 전문가입니다.
학생이 주제나 내용을 보내면 시험 공부에 최적화된 형태로 요약해주세요:

1. **핵심 요약** (3~5줄)
2. **주요 개념** (표 형태로 정리)
3. **암기 포인트** (시험에 꼭 나오는 것)
4. **헷갈리기 쉬운 것** (주의할 점)
5. **암기 팁** (연상법이나 두문자어 등)

깔끔하고 보기 좋게 정리해주세요. 한국어로 답변해주세요.""",
        "placeholder": "예: 조선시대 신분제도 정리해줘 / 세포 분열 과정 요약해줘",
    },
    "💻 코드 도우미": {
        "system": """당신은 프로그래밍 교육 전문가입니다. (Python 중심)
학생이 코딩 관련 질문을 하면 다음과 같이 답변해주세요:

1. **설명**: 개념을 쉽게 설명
2. **전체 코드**: 실행 가능한 완전한 코드 제공
3. **코드 설명**: 주요 부분을 줄별로 설명
4. **실행 결과**: 예상 출력 결과
5. **응용**: 코드를 변형할 수 있는 아이디어

코드에는 반드시 한국어 주석을 달아주세요. 초보자도 이해할 수 있게 설명해주세요.""",
        "placeholder": "예: Python으로 구구단 프로그램 만들어줘 / 리스트와 딕셔너리의 차이점은?",
    },
}

# ──────────────────────────────────────────────
# 커스텀 CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ===== 메인 배경 ===== */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }

    /* ===== 전체 텍스트 기본 색상 ===== */
    .stApp p, .stApp span, .stApp div, .stApp label,
    .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
    .stApp td, .stApp th, .stApp caption {
        color: #f0f0f0 !important;
        -webkit-text-fill-color: #f0f0f0 !important;
    }

    /* ===== 위젯 라벨 ===== */
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stWidgetLabel"] span,
    .stApp [data-testid="stWidgetLabel"] label {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* ===== 입력 필드 ===== */
    .stApp input, .stApp textarea, .stApp select {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        background-color: #ffffff !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }

    /* ===== number_input ===== */
    .stApp .stNumberInput input,
    .stApp [data-testid="stNumberInput"] input,
    .stApp [data-baseweb="input"] input {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        background-color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        opacity: 1 !important;
    }
    .stApp [data-testid="stNumberInput"] button,
    .stApp .stNumberInput button {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        background-color: #e0e0e0 !important;
    }

    /* ===== selectbox ===== */
    .stApp [data-baseweb="select"] > div {
        background-color: #ffffff !important;
    }
    .stApp [data-baseweb="select"] span,
    .stApp [data-baseweb="select"] div {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        font-weight: 500 !important;
    }
    .stApp [data-baseweb="select"] svg {
        fill: #111111 !important;
    }

    /* ===== radio 버튼 (카테고리) ===== */
    .stApp .stRadio > div {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .stApp .stRadio > div > label {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
    }
    .stApp .stRadio > div > label:hover {
        background: rgba(167,139,250,0.2) !important;
        border-color: rgba(167,139,250,0.5) !important;
    }
    .stApp .stRadio > div > label[data-checked="true"],
    .stApp .stRadio > div > label:has(input:checked) {
        background: rgba(167,139,250,0.3) !important;
        border-color: #a78bfa !important;
    }
    .stApp .stRadio p,
    .stApp .stRadio span,
    .stApp .stRadio label {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* ===== placeholder ===== */
    .stApp input::placeholder, .stApp textarea::placeholder {
        color: #999999 !important;
        -webkit-text-fill-color: #999999 !important;
        opacity: 1 !important;
    }

    /* ===== 사이드바 ===== */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background: #16132b !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] li, [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] caption, [data-testid="stSidebar"] small {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] .stAlert,
    [data-testid="stSidebar"] .stAlert p,
    [data-testid="stSidebar"] .stAlert span,
    [data-testid="stSidebar"] .stAlert div,
    [data-testid="stSidebar"] [data-testid="stNotification"],
    [data-testid="stSidebar"] [data-testid="stNotification"] p {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background-color: rgba(102, 126, 234, 0.25) !important;
        border: 1px solid rgba(102, 126, 234, 0.4) !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] button p,
    [data-testid="stSidebar"] button span,
    [data-testid="stSidebar"] button div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background-color: rgba(167, 139, 250, 0.3) !important;
        border: 1px solid rgba(167, 139, 250, 0.5) !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(167, 139, 250, 0.5) !important;
    }

    /* ===== 메인 버튼 ===== */
    .stApp button[kind="primary"] p,
    .stApp button[kind="primary"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* ===== 메인 경고 박스 ===== */
    .stApp .stAlert p, .stApp .stAlert span {
        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;
    }

    /* ===== 구분선 ===== */
    .stApp hr {
        border-color: rgba(255,255,255,0.15) !important;
    }

    /* ===== 코드블록 ===== */
    .stApp pre {
        background: rgba(0,0,0,0.4) !important;
    }
    .stApp pre code {
        color: #e0e0e0 !important;
        -webkit-text-fill-color: #e0e0e0 !important;
    }
    .stApp code {
        color: #f093fb !important;
        -webkit-text-fill-color: #f093fb !important;
    }

    /* ===== 커스텀 클래스들 ===== */
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
        -webkit-text-fill-color: #cccccc !important;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .model-card {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .category-card {
        background: rgba(167,139,250,0.08);
        border: 1px solid rgba(167,139,250,0.25);
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .category-desc {
        background: rgba(102,126,234,0.12);
        border: 1px solid rgba(102,126,234,0.3);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-top: 0.5rem;
        color: #c5caf5 !important;
        -webkit-text-fill-color: #c5caf5 !important;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .token-card {
        background: rgba(102,126,234,0.15);
        border: 1px solid rgba(102,126,234,0.4);
        border-radius: 12px;
        padding: 1.2rem;
        margin-top: 1rem;
    }
    .token-title {
        color: #a78bfa !important;
        -webkit-text-fill-color: #a78bfa !important;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    .token-item {
        color: #e8e8e8 !important;
        -webkit-text-fill-color: #e8e8e8 !important;
        font-size: 0.95rem;
        padding: 0.25rem 0;
    }
    .token-highlight {
        color: #f093fb !important;
        -webkit-text-fill-color: #f093fb !important;
        font-weight: 700;
        font-size: 1rem;
    }
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
        -webkit-text-fill-color: #a78bfa !important;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.6rem;
    }
    .usage-detail {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 0.95rem;
        line-height: 1.8;
    }
    .val-input {
        color: #7dd3fc !important;
        -webkit-text-fill-color: #7dd3fc !important;
        font-weight: 700;
    }
    .val-output {
        color: #f0abfc !important;
        -webkit-text-fill-color: #f0abfc !important;
        font-weight: 700;
    }
    .val-total {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 700;
        font-size: 1.05rem;
    }
    .history-q {
        background: rgba(102,126,234,0.25);
        border-left: 4px solid #667eea;
        border-radius: 0 10px 10px 0;
        padding: 0.8rem 1rem;
        margin: 0.6rem 0 0.3rem 0;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
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
        -webkit-text-fill-color: #e8e8e8 !important;
        font-size: 0.9rem;
        line-height: 1.7;
    }
    .history-tokens {
        font-size: 0.8rem;
        color: #bbbbbb !important;
        -webkit-text-fill-color: #bbbbbb !important;
        margin-top: 0.4rem;
    }
    .history-cat {
        display: inline-block;
        background: rgba(167,139,250,0.25);
        border-radius: 6px;
        padding: 0.1rem 0.5rem;
        font-size: 0.75rem;
        color: #d4c5f5 !important;
        -webkit-text-fill-color: #d4c5f5 !important;
        margin-top: 0.3rem;
    }
    .warning-box {
        background: rgba(255, 193, 7, 0.12);
        border: 1px solid rgba(255, 193, 7, 0.4);
        border-radius: 10px;
        padding: 1rem;
        color: #ffd54f !important;
        -webkit-text-fill-color: #ffd54f !important;
        text-align: center;
        margin: 2rem 0;
    }
    .footer-info {
        text-align: center;
        color: #999999 !important;
        -webkit-text-fill-color: #999999 !important;
        font-size: 0.8rem;
        padding: 1rem 0;
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
# 카테고리 선택
# ──────────────────────────────────────────────
st.markdown("---")

st.markdown('<div class="category-card">', unsafe_allow_html=True)
selected_category = st.selectbox(
    "📂 카테고리 선택",
    options=list(CATEGORIES.keys()),
    index=0,
)

# 카테고리 설명 표시
CATEGORY_DESCRIPTIONS = {
    "💬 자유 질문": "어떤 질문이든 자유롭게! AI가 친절하게 답변해줍니다.",
    "🔤 영어 문법 검사": "영어 문장을 입력하면 문법 오류를 찾고 교정해줍니다.",
    "🌐 영어 번역": "한→영 또는 영→한 번역을 해줍니다. 핵심 표현도 알려줘요.",
    "📐 수학 풀이": "수학 문제를 단계별로 풀어줍니다. 풀이 과정을 자세히 설명해요.",
    "🔬 과학 개념 설명": "물리, 화학, 생물, 지구과학 개념을 쉽게 설명해줍니다.",
    "📝 국어 지문 분석": "지문이나 문학 작품을 분석하고 예상 문제를 만들어줍니다.",
    "📖 개념 요약 정리": "학습 내용을 시험 대비용으로 깔끔하게 요약해줍니다.",
    "💻 코드 도우미": "Python 등 코딩 질문에 답하고 전체 코드를 제공합니다.",
}

st.markdown(f"""
<div class="category-desc">
    💡 {CATEGORY_DESCRIPTIONS[selected_category]}
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 질문 입력
# ──────────────────────────────────────────────
cat_data = CATEGORIES[selected_category]

question = st.text_area(
    "💬 질문을 입력하세요",
    height=120,
    placeholder=cat_data["placeholder"],
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
                system=cat_data["system"],
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
                "category": selected_category,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            })

            st.markdown(f"### 📝 AI 답변 — {selected_category}")
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
                <div class="token-item" style="margin-top:0.5rem; font-size:0.85rem;">
                    {selected_model_name} | {selected_category}
                </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ 오류 발생: {error_msg}")

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
        st.markdown("""
        <div style="background:rgba(102,126,234,0.2); border:1px solid rgba(102,126,234,0.4);
                    border-radius:10px; padding:0.8rem 1rem; text-align:center;
                    color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">
            아직 질문 기록이 없습니다.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 📜 대화 기록")

    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history), 1):
            idx = len(st.session_state.history) - i + 1
            q_short = item["question"][:50] + ("..." if len(item["question"]) > 50 else "")
            a_short = item["answer"][:100] + ("..." if len(item["answer"]) > 100 else "")
            cat = item.get("category", "💬 자유 질문")

            st.markdown(f"""
            <div class="history-q">
                <b>Q{idx}.</b> {q_short}
                <div class="history-cat">{cat}</div>
            </div>
            <div class="history-a">
                {a_short}
                <div class="history-tokens">
                    입력 {item['input_tokens']:,} / 출력 {item['output_tokens']:,} 토큰
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="color:#cccccc !important; -webkit-text-fill-color:#cccccc !important;
                    font-size:0.9rem; padding:0.5rem 0;">
            질문을 하면 여기에 기록됩니다.
        </div>
        """, unsafe_allow_html=True)

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
