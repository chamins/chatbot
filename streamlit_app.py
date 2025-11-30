import streamlit as st
from openai import OpenAI

# Page configuration
st.set_page_config(page_title="🌟 롤모델 소개팅", layout="wide")

# Show title
st.title("🌟 롤모델 소개팅")
st.write("당신의 관심분야와 희망업무에 맞는 롤모델을 찾아보세요!")

# Get OpenAI API key from secrets
try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except (KeyError, AttributeError):
    st.error("⚠️ OpenAI API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.", icon="🔑")
    st.stop()

if not openai_api_key or openai_api_key == "":
    st.error("⚠️ OpenAI API 키가 비어있습니다. .streamlit/secrets.toml에 유효한 키를 입력해주세요.", icon="🔑")
    st.stop()

# Create an OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize session state variables
if "conditions_set" not in st.session_state:
    st.session_state.conditions_set = False

if "interest_field" not in st.session_state:
    st.session_state.interest_field = None

if "desired_job" not in st.session_state:
    st.session_state.desired_job = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# System prompt for role model matching
SYSTEM_PROMPT = """당신은 친절한 롤모델 추천 전문가입니다.
사용자의 관심분야와 희망업무에 맞는 롤모델을 YouTube 인터뷰 영상을 통해 소개해줍니다.

사용자가 조건을 선택하면, 해당 조건에 맞는 롤모델 3명을 YouTube 인터뷰 영상으로 추천합니다.

각 추천 시에는 다음 형식으로 응답하세요:

**당신을 위한 롤모델 추천:**

1. 🎯 롤모델: [이름]
   • 분야: [전문 분야]
   • 주요 성과: [주요 성과]
   • 추천 영상: [YouTube 인터뷰 제목]
   • 출연자/채널: [출연자 또는 채널명]
   • 추천 이유: [사용자 요구와 관련된 추천 이유]
   
2. 🎯 롤모델: [이름]
   • 분야: [전문 분야]
   • 주요 성과: [주요 성과]
   • 추천 영상: [YouTube 인터뷰 제목]
   • 출연자/채널: [출연자 또는 채널명]
   • 추천 이유: [사용자 요구와 관련된 추천 이유]

3. 🎯 롤모델: [이름]
   • 분야: [전문 분야]
   • 주요 성과: [주요 성과]
   • 추천 영상: [YouTube 인터뷰 제목]
   • 출연자/채널: [출연자 또는 채널명]
   • 추천 이유: [사용자 요구와 관련된 추천 이유]

**추가 정보:**
[관련된 조언이나 더 알아보면 좋을 정보]

이후 사용자와 자연스럽게 대화를 계속하며, 더 구체적인 추천이나 상담이 필요하면 질문하세요."""

# Sidebar for conditions selection
st.sidebar.header("📋 조건 선택")
st.sidebar.write("당신의 관심분야와 희망업무를 선택해주세요.")

# Interest field selection
interest_fields = [
    "기술/개발",
    "마케팅/영업",
    "디자인/창의성",
    "금융/투자",
    "교육/훈련",
    "경영/리더십",
    "의료/헬스케어",
    "미디어/콘텐츠",
    "제조/공학",
    "환경/지속가능성"
]

interest_field = st.sidebar.selectbox(
    "🎯 관심분야를 선택하세요:",
    options=interest_fields,
    index=None,
    placeholder="분야를 선택해주세요"
)

# Desired job selection
desired_jobs = [
    "창업가/기업가",
    "경영진/임원",
    "전문가/컨설턴트",
    "팀리더/매니저",
    "특화된 전문가",
    "연구원/개발자",
    "프리랜서/독립사업가",
    "사회활동가/NGO활동가"
]

desired_job = st.sidebar.selectbox(
    "💼 희망업무를 선택하세요:",
    options=desired_jobs,
    index=None,
    placeholder="업무를 선택해주세요"
)

# Apply conditions button
if st.sidebar.button("✅ 조건 적용", use_container_width=True):
    if interest_field and desired_job:
        st.session_state.conditions_set = True
        st.session_state.interest_field = interest_field
        st.session_state.desired_job = desired_job
        st.session_state.messages = []  # Reset messages when conditions change
        st.rerun()
    else:
        st.sidebar.error("관심분야와 희망업무를 모두 선택해주세요.")

# Reset conditions button
if st.sidebar.button("🔄 조건 초기화", use_container_width=True):
    st.session_state.conditions_set = False
    st.session_state.interest_field = None
    st.session_state.desired_job = None
    st.session_state.messages = []
    st.rerun()

# Main content area
if st.session_state.conditions_set:
    # Display selected conditions
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🎯 **관심분야:** {st.session_state.interest_field}")
    with col2:
        st.info(f"💼 **희망업무:** {st.session_state.desired_job}")
    
    st.divider()
    
    # Display the existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field
    if prompt := st.chat_input("롤모델에 대해 궁금한 점을 물어보세요!"):
        
        # Store and display the user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API
        conditions_context = f"""사용자의 관심분야: {st.session_state.interest_field}
사용자의 희망업무: {st.session_state.desired_job}"""

        messages_for_api = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": conditions_context}
        ] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_api,
            stream=True,
            temperature=0.7,
            max_tokens=2000
        )

        # Stream the response to the chat
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        
        # Store the assistant message in session state
        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    # Show message when conditions are not set
    st.info("👈 왼쪽 사이드바에서 관심분야와 희망업무를 선택한 후, '조건 적용' 버튼을 눌러주세요.", icon="ℹ️")
