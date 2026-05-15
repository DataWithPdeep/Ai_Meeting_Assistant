import streamlit as st
from dotenv import load_dotenv
import tempfile
import os

# =========================================================
# LOAD ENV
# =========================================================
load_dotenv()

# =========================================================
# IMPORT PROJECT MODULES
# =========================================================
from main import run_pipeline
from core.rag_engine import ask_question

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# PREMIUM RESPONSIVE UI
# =========================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, .stApp {
    overflow-x: hidden;
    font-family: 'DM Sans', sans-serif;
    background: #0d0d0f;
    color: #f3f4f6;
}

* {
    box-sizing: border-box;
}

/* =====================================================
   MAIN CONTAINER
===================================================== */

.block-container {
    max-width: 1250px !important;
    padding: clamp(1rem, 3vw, 2.5rem)
             clamp(1rem, 4vw, 3rem) !important;
}

/* =====================================================
   SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {
    background: #111114;
    border-right: 1px solid #222228;
    min-width: 230px !important;
    max-width: 300px !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding: 1.2rem 1rem;
}

[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    background: #c9a96e;
    border-radius: 8px;
    padding: 4px;
}

/* =====================================================
   HERO
===================================================== */

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    text-align: center;
    line-height: 1.1;
    margin-top: 0.3rem;
    margin-bottom: 0.5rem;
    color: white;
}

.hero-sub {
    text-align: center;
    color: #9ca3af;
    font-size: clamp(0.85rem, 2vw, 1rem);
    margin-bottom: 2rem;
    letter-spacing: 0.05em;
}

/* =====================================================
   METRICS
===================================================== */

[data-testid="metric-container"] {
    background: #16161a;
    border: 1px solid #2a2a30;
    padding: 1rem;
    border-radius: 16px;
}

/* =====================================================
   TABS
===================================================== */

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background: #16161a;
    border-radius: 12px;
    padding: 10px 18px;
    color: white;
    border: 1px solid #2a2a30;
}

.stTabs [aria-selected="true"] {
    background: #c9a96e !important;
    color: black !important;
}

/* =====================================================
   CARD
===================================================== */

.card {
    width: 100%;
    background: linear-gradient(180deg, #18181d 0%, #141418 100%);
    border: 1px solid #2a2a30;
    border-radius: 18px;
    padding: clamp(1rem, 2vw, 1.5rem);
    margin-bottom: 1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.22);
}

.card-title {
    color: #c9a96e;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.7rem;
}

.card-body {
    color: #f3f4f6;
    line-height: 1.8;
    white-space: pre-wrap;
    font-size: clamp(0.88rem, 1.5vw, 1rem);
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* =====================================================
   INPUTS
===================================================== */

.stTextInput input,
.stTextArea textarea {
    background: #16161a !important;
    color: white !important;
    border: 1px solid #2d2d34 !important;
    border-radius: 12px !important;
    padding: 0.8rem 1rem !important;
    min-height: 48px !important;
    font-size: 16px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #c9a96e !important;
    box-shadow: 0 0 0 2px rgba(201,169,110,0.15) !important;
}

/* =====================================================
   BUTTONS
===================================================== */

.stButton > button {
    width: 100%;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, #c9a96e 0%, #ddb978 100%);
    color: #0d0d0f;
    padding: 0.85rem 1rem;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    min-height: 50px;
}

.stButton > button:hover {
    transform: translateY(-2px);
}

/* =====================================================
   FILE UPLOADER
===================================================== */

[data-testid="stFileUploader"] {
    background: #16161a;
    border: 1.5px dashed #2d2d34;
    border-radius: 14px;
    padding: 0.5rem;
}

/* =====================================================
   CHAT
===================================================== */

.chat-user,
.chat-bot {
    padding: 0.9rem 1rem;
    border-radius: 16px;
    margin: 0.7rem 0;
    line-height: 1.7;
    font-size: 0.94rem;
}

.chat-user {
    background: #202026;
    border-bottom-right-radius: 5px;
}

.chat-bot {
    background: #16161a;
    border: 1px solid #2a2a30;
    border-bottom-left-radius: 5px;
}

/* =====================================================
   HIDE STREAMLIT BRANDING
===================================================== */

#MainMenu,
footer,
header {
    visibility: hidden;
}

/* =====================================================
   MOBILE
===================================================== */

@media (max-width: 768px) {

    section[data-testid="stSidebar"] {
        transform: translateX(0%) !important;
    }

    .block-container {
        padding: 1rem 0.9rem 2rem !important;
    }

    .hero-title {
        font-size: 2rem;
    }
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================================================
# HERO
# =========================================================

st.markdown(
    "<div class='hero-title'>Meeting Intelligence</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='hero-sub'>Transcribe • Summarize • Extract • Chat</div>",
    unsafe_allow_html=True
)

# =========================================================
# METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

col1.metric("AI Powered", "24/7")
col2.metric("Languages", "2")
col3.metric("Processing", "Fast")

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# INPUT TABS (BEST FOR MOBILE)
# =========================================================

tab1, tab2 = st.tabs(["📺 YouTube URL", "📁 Upload File"])

source = None

with tab1:

    yt_url = st.text_input(
        "Paste YouTube URL",
        placeholder="https://youtu.be/..."
    )

    if yt_url:
        source = yt_url.strip()

with tab2:

    uploaded_file = st.file_uploader(
        "Upload Audio / Video",
        type=["mp3", "wav", "mp4", "m4a", "webm"],
        help="Supported: MP3, WAV, MP4, M4A, WEBM"
    )

    if uploaded_file:

        suffix = os.path.splitext(uploaded_file.name)[1]

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        )

        temp_file.write(uploaded_file.read())
        temp_file.close()

        source = temp_file.name

# =========================================================
# OPTIONS
# =========================================================

language = st.selectbox(
    "Language",
    ["english", "hinglish"]
)

process_btn = st.button(
    "🚀 Run Pipeline",
    disabled=not source
)

# =========================================================
# RUN PIPELINE
# =========================================================

if process_btn and source:

    st.session_state.chat_history = []

    with st.spinner("🧠 AI is analyzing your meeting..."):

        try:

            result = run_pipeline(source, language)

            st.session_state.result = result

            st.success("✅ Processing Completed!")

        except Exception as e:

            st.error(f"❌ Error: {e}")

# =========================================================
# RESULTS
# =========================================================

if st.session_state.result:

    r = st.session_state.result

    st.markdown(f"""
        <div class='card'>
            <div class='card-title'>Meeting Title</div>
            <div class='card-body'>{r['title']}</div>
        </div>
    """, unsafe_allow_html=True)

    section = st.selectbox(
        "Select Section",
        [
            "Summary",
            "Action Items",
            "Key Decisions",
            "Open Questions",
            "Transcript"
        ]
    )

    content_map = {
        "Summary": r["summary"],
        "Action Items": r["action_items"],
        "Key Decisions": r["key_decisions"],
        "Open Questions": r["open_questions"],
        "Transcript": r["transcript"],
    }

    content = content_map[section]

    st.markdown(f"""
        <div class='card'>
            <div class='card-title'>{section}</div>
            <div class='card-body'>{content}</div>
        </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # CHAT
    # =====================================================

    st.markdown("""
    <div style='margin-top:2rem;margin-bottom:1rem;'>
        <h2 style='font-family:Syne,sans-serif;'>
            💬 AI Meeting Chat
        </h2>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:

        if msg["role"] == "user":

            st.markdown(
                f"<div class='chat-user'>🧑 {msg['content']}</div>",
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"<div class='chat-bot'>🤖 {msg['content']}</div>",
                unsafe_allow_html=True
            )

    with st.form("chat_form", clear_on_submit=True):

        user_input = st.text_input(
            "Ask anything about the meeting...",
            placeholder="e.g. Who was assigned the mobile task?"
        )

        send = st.form_submit_button("Send ➤")

        if send and user_input.strip():

            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })

            with st.spinner("Thinking..."):

                answer = ask_question(
                    r["rag_chain"],
                    user_input
                )

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()

# =========================================================
# EMPTY STATE
# =========================================================

else:

    st.info(
        "🎙️ Upload a meeting file or paste a YouTube URL to begin AI analysis."
    )