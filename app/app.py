"""
app.py
Purpose: Streamlit web interface for the Agentic AI Professional Profile
Author: Gregory E. Schwartz (gregory.e.schwartz@gmail.com)
Date: 2026-01-06
"""

import streamlit as st
from pathlib import Path
import sys

# add app directory to path for imports
app_path = Path(__file__).parent
sys.path.insert(0, str(app_path))

from agent import AgenticProfileAgent
from tools import load_profile


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'agent' not in st.session_state:
        profile_path = app_path / "profile.yaml"
        st.session_state.agent = AgenticProfileAgent(str(profile_path))

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'lead_logged' not in st.session_state:
        st.session_state.lead_logged = False


def render_sidebar():
    """Render the sidebar with profile quick facts."""
    agent = st.session_state.agent
    profile = agent.profile

    st.sidebar.markdown("### Quick Facts")

    contact = profile.get('contact', {})
    st.sidebar.markdown(f"**Email:** {contact.get('email', 'N/A')}")
    st.sidebar.markdown(f"**Location:** {profile.get('location', 'N/A')}")
    st.sidebar.markdown(f"**GitHub:** [{contact.get('github', '')}](https://{contact.get('github', '')})")

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
        "Claude API (Anthropic)",
        "Streamlit",
        "Prompt Engineering",
        "Structured Outputs (JSON)",
        "Agentic AI Patterns",
        "Python"
    ]
    for skill in built_with:
        st.sidebar.markdown(f"- {skill}")

    st.sidebar.markdown("---")
    if st.sidebar.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.agent.reset_conversation()
        st.rerun()


def render_chat_history():
    """Render the chat history (without input - input must be outside columns)."""
    agent = st.session_state.agent

    st.markdown(f"### Chat with {agent.name}")
    st.markdown("*Ask about background, projects, skills, or express hiring interest*")

    # display chat history
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            st.chat_message("user").markdown(content)
        else:
            st.chat_message("assistant").markdown(content)


def render_example_questions():
    """Render example question buttons."""
    st.markdown("#### Example Questions")

    col1, col2 = st.columns(2)

    questions = [
        "Tell me about your background",
        "What projects have you worked on?",
        "Describe your RAG system work",
        "What's your experience with GNNs?",
        "Tell me about Ernst & Young project",
        "What are your key strengths?",
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
    /* Sidebar toggle button - larger and more visible */
    button[data-testid="stSidebarCollapseButton"] {
        font-size: 2rem !important;
        width: 3.5rem !important;
        height: 3.5rem !important;
        background-color: #A78BFA !important;
        border-radius: 8px !important;
        border: 2px solid #A78BFA !important;
    }
    button[data-testid="stSidebarCollapseButton"] svg {
        width: 2rem !important;
        height: 2rem !important;
        color: #0D1B2A !important;
        stroke: #0D1B2A !important;
    }
    button[data-testid="stSidebarCollapseButton"]:hover {
        background-color: #8B5CF6 !important;
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
    </style>
    """, unsafe_allow_html=True)

    init_session_state()

    agent = st.session_state.agent

    # header
    st.title(agent.name)
    st.markdown(f"*{agent.profile.get('headline', '')}*")

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
        - Answer questions about my background
        - Discuss technical projects in detail
        - Autonomously log leads to Google Sheets
        - Maintain conversation context

        Built with Claude API + Streamlit.
        """)

    # chat input must be outside columns
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        # show user message immediately
        with col_main:
            st.chat_message("user").markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.agent.chat(prompt)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


if __name__ == "__main__":
    main()
