"""
app.py
Purpose: Streamlit web interface for the Agentic AI Professional Profile
Author: Gregory E. Schwartz (gregory.e.schwartz@gmail.com)
Date: 2026-04-17
"""

import base64
import streamlit as st
from pathlib import Path
import sys

# add app directory to path for imports
app_path = Path(__file__).parent
sys.path.insert(0, str(app_path))

from agent import AgenticProfileAgent
from tools import load_profile


PDF_PATH = app_path / "Gregory_Schwartz_CV_v41.pdf"
STATIC_DIR = app_path / "static"
LION_AVATAR = STATIC_DIR / "lion_avatar.png"
LION_HERO = STATIC_DIR / "lion_hero.png"
SEED_MESSAGE = (
    "Hi! I'm Gregory's CV. You can ask me about his work and download his "
    "formal PDF CV here."
)


def assistant_avatar():
    """Return avatar path (as str) for assistant chat bubbles, or None."""
    return str(LION_AVATAR) if LION_AVATAR.exists() else None


def pdf_bytes():
    """Return the PDF as bytes, or None if the file is missing."""
    if PDF_PATH.exists():
        return PDF_PATH.read_bytes()
    return None


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'agent' not in st.session_state:
        profile_path = app_path / "profile.yaml"
        st.session_state.agent = AgenticProfileAgent(str(profile_path))

    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": SEED_MESSAGE},
        ]

    if 'lead_logged' not in st.session_state:
        st.session_state.lead_logged = False


def render_sidebar():
    """Render the sidebar with profile quick facts."""
    agent = st.session_state.agent
    profile = agent.profile

    if LION_HERO.exists():
        st.sidebar.image(
            str(LION_HERO),
            use_column_width=True,
            caption="Your CV's workshop host — ask me anything.",
        )
        st.sidebar.markdown("---")

    st.sidebar.markdown("### Quick Facts")

    contact = profile.get('contact', {})
    st.sidebar.markdown(f"**Email:** {contact.get('email', 'N/A')}")
    st.sidebar.markdown(f"**Location:** {profile.get('location', 'N/A')}")
    st.sidebar.markdown(f"**GitHub:** [{contact.get('github', '')}](https://{contact.get('github', '')})")

    pdf = pdf_bytes()
    if pdf:
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            label="Download PDF CV (v41)",
            data=pdf,
            file_name="Gregory_Schwartz_CV_v41.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Education")
    for edu in profile.get('education', [])[:2]:
        st.sidebar.markdown(f"**{edu.get('degree', '')}**")
        if edu.get('department'):
            st.sidebar.markdown(f"{edu.get('department', '')}")
        if edu.get('school'):
            st.sidebar.markdown(f"{edu.get('school', '')}")
        if edu.get('university'):
            st.sidebar.markdown(f"{edu.get('university', '')}")
        st.sidebar.markdown(f"*{edu.get('grad_date', '')}*")
        st.sidebar.markdown("")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Built With")
    built_with = [
        "Claude Sonnet 4.5 + prompt caching",
        "Streaming responses",
        "Streamlit",
        "Structured lead-capture tag",
        "Agentic AI context-injection",
        "Python"
    ]
    for skill in built_with:
        st.sidebar.markdown(f"- {skill}")

    st.sidebar.markdown("---")
    if st.sidebar.button("Clear Conversation"):
        st.session_state.messages = [
            {"role": "assistant", "content": SEED_MESSAGE},
        ]
        st.session_state.agent.reset_conversation()
        st.rerun()


def render_chat_history():
    """Render the chat history (without input - input must be outside columns)."""
    agent = st.session_state.agent

    st.markdown(f"### Chat with {agent.name}")
    st.markdown("*Ask about background, projects, skills, or express hiring interest*")

    # display chat history
    avatar = assistant_avatar()
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            st.chat_message("user").markdown(content)
        else:
            st.chat_message("assistant", avatar=avatar).markdown(content)


def render_example_questions():
    """Render example question buttons."""
    st.markdown("#### Example Questions")

    col1, col2 = st.columns(2)

    questions = [
        "Tell me about your background",
        "What's GLASS Build Team?",
        "Describe your RAG system work",
        "How does the KG guardrails project work?",
        "Tell me about Ernst & Young",
        "What's Claude Governance Enforcer?",
        "Tell me about your publications",
        "What's your email?"
    ]

    for i, question in enumerate(questions):
        col = col1 if i % 2 == 0 else col2
        if col.button(question, key=f"q_{i}"):
            st.session_state.messages.append({"role": "user", "content": question})
            response = st.session_state.agent.chat(question)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()


def render_banner(agent):
    """Render the top banner with name, headline, and PDF download link."""
    st.title(agent.name)
    st.markdown(f"*{agent.profile.get('headline', '')}*")

    pdf = pdf_bytes()
    if pdf:
        b64 = base64.b64encode(pdf).decode()
        link = (
            f'<a href="data:application/pdf;base64,{b64}" '
            f'download="Gregory_Schwartz_CV_v41.pdf" '
            f'style="color:#A78BFA;font-weight:600;text-decoration:underline;">'
            f'download his formal PDF CV here</a>'
        )
        st.markdown(
            f"<div style='color:#A3B8CC;font-size:1rem;margin-top:0.25rem;'>"
            f"Hi! I'm Gregory's CV. You can ask me about his work and {link}."
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='color:#A3B8CC;font-size:1rem;margin-top:0.25rem;'>"
            f"{SEED_MESSAGE}"
            f"</div>",
            unsafe_allow_html=True,
        )


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Agentic Profile - Gregory Schwartz",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # custom styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #0D1B2A;
    }
    .stMarkdown {
        color: #A3B8CC;
    }
    .stChatMessage {
        background-color: #1a1a2e;
    }
    /* Main title and chat header - purple */
    h1, [data-testid="stHeadingWithActionElements"] h1 {
        color: #A78BFA !important;
    }
    h3 {
        color: #A78BFA !important;
    }
    /* Example Questions and About This Demo - lighter silver */
    h4 {
        color: #A3B8CC !important;
    }
    /* Make all example question buttons same size */
    [data-testid="column"] button {
        width: 100% !important;
        min-height: 4rem !important;
        height: auto !important;
    }
    /* Sidebar toggle button - bold and obvious */
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] button,
    section[data-testid="stSidebar"] + div button:first-child {
        font-size: 1.2rem !important;
        width: 2.4rem !important;
        height: 2.4rem !important;
        min-width: 2.4rem !important;
        min-height: 2.4rem !important;
        background-color: #A78BFA !important;
        border-radius: 10px !important;
        border: 3px solid #8B5CF6 !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.4) !important;
    }
    button[data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg {
        width: 1.5rem !important;
        height: 1.5rem !important;
        color: #0D1B2A !important;
        stroke: #0D1B2A !important;
        stroke-width: 3px !important;
    }
    button[data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="collapsedControl"] button:hover {
        background-color: #8B5CF6 !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(167, 139, 250, 0.6) !important;
    }
    /* Sidebar - light background with deep blue text */
    [data-testid="stSidebar"] {
        background-color: #F0F4F8;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] a {
        color: #0D1B2A !important;
    }
    /* Lion hero breathing animation — subtle scale pulse, 6s cycle */
    @keyframes lion-breathe {
        0%, 100% { transform: scale(1.00); }
        50%      { transform: scale(1.025); }
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        animation: lion-breathe 6s ease-in-out infinite;
        transform-origin: center;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    init_session_state()

    agent = st.session_state.agent

    render_banner(agent)

    # check api status
    if not agent.client:
        st.warning("Claude API not configured. Set ANTHROPIC_API_KEY in .env to enable chat.")
        st.info("You can still explore the profile structure in the sidebar.")

    render_sidebar()

    # main content - two column layout
    col_main, col_side = st.columns([3, 1])

    with col_main:
        render_chat_history()

    with col_side:
        render_example_questions()

        st.markdown("---")
        st.markdown("#### About This Demo")
        st.markdown("""
        This is an **agentic AI profile** that can:
        - Answer questions about my background in streaming real-time
        - Discuss technical projects in detail
        - Autonomously log hiring leads to Google Sheets
        - Maintain conversation context with prompt caching

        Built on Claude Sonnet 4.5 + Streamlit.
        """)

    # chat input must be outside columns
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.pending_prompt = prompt
        st.rerun()

    # handle any pending prompt AFTER the rerun-redraw of history
    if st.session_state.get("pending_prompt"):
        pending = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        with col_main:
            with st.chat_message("assistant", avatar=assistant_avatar()):
                placeholder = st.empty()
                accumulated = ""
                for chunk in st.session_state.agent.chat_stream(pending):
                    accumulated += chunk
                    placeholder.markdown(accumulated)
                response = accumulated
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
