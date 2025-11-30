import streamlit as st
from openai import OpenAI

# Page configuration
st.set_page_config(page_title="🎬 YouTube 인터뷰 추천 챗봇", layout="wide")

# Show title and description.
st.title("🎬 YouTube 인터뷰 추천 챗봇")
st.write(
    "이 챗봇은 당신의 관심사에 맞춰 YouTube 인터뷰 영상을 추천해드립니다. "
    "원하는 주제나 인물에 대해 물어보세요!"
)

# Get OpenAI API key from secrets
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("⚠️ OpenAI API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.", icon="🔑")
    st.stop()

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "interview_recommendations" not in st.session_state:
    st.session_state.interview_recommendations = None

# System prompt for YouTube interview recommendation
SYSTEM_PROMPT = """당신은 친절한 YouTube 인터뷰 영상 추천 전문가입니다.
사용자의 관심사, 요구사항, 또는 궁금한 주제에 대해 YouTube에서 볼 수 있는 인터뷰 영상 3개를 추천해야 합니다.

각 추천 시에는 다음 형식으로 응답하세요:

**인터뷰 영상 추천:**

1. 📺 제목: [영상 제목]
   • 출연자: [주요 출연자]
   • 내용: [간단한 설명]
   • 추천 이유: [사용자 요구와 관련된 추천 이유]
   
2. 📺 제목: [영상 제목]
   • 출연자: [주요 출연자]
   • 내용: [간단한 설명]
   • 추천 이유: [사용자 요구와 관련된 추천 이유]

3. 📺 제목: [영상 제목]
   • 출연자: [주요 출연자]
   • 내용: [간단한 설명]
   • 추천 이유: [사용자 요구와 관련된 추천 이유]

**추가 정보:**
[관련 내용이나 추가 조언]

추천 후에는 사용자와 자연스럽게 대화를 계속하며, 더 구체적인 추천이 필요하면 질문하세요.
사용자의 피드백에 따라 더 나은 추천을 제공할 수 있습니다."""

# Display the existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field
if prompt := st.chat_input("어떤 인터뷰 영상을 추천받고 싶으신가요?"):
    
    # Store and display the user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the OpenAI API
    messages_for_api = [
        {"role": "system", "content": SYSTEM_PROMPT}
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
