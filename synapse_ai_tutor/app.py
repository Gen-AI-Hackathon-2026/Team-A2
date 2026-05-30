"""
Synapse AI Tutor -- Main Application Entry Point
An Adaptive AI Tutoring System with RAG-powered intelligent teaching.
"""

import streamlit as st
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from pages.login import render_login
from pages.topic_selection import render_topic_selection
from pages.assessment import render_assessment
from pages.tutor import render_tutor
from pages.dashboard import render_dashboard


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Synapse AI Tutor",
        page_icon="S",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def inject_global_styles():
    """Inject premium CSS styling."""
    st.markdown("""
    <style>
    /* ===== Import Google Fonts ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ===== Root Variables ===== */
    :root {
        --primary: #6C63FF;
        --primary-dark: #5A52D5;
        --primary-light: #8B83FF;
        --secondary: #00D2FF;
        --accent: #FF6B6B;
        --accent-warm: #FFB347;
        --success: #2ECC71;
        --warning: #F39C12;
        --danger: #E74C3C;
        --bg-dark: #0A0A1A;
        --bg-card: #12122A;
        --bg-card-hover: #1A1A3E;
        --text-primary: #FFFFFF;
        --text-secondary: #A0A0C0;
        --text-muted: #6B6B8D;
        --border: #2A2A4A;
        --glow-primary: rgba(108, 99, 255, 0.3);
        --glow-secondary: rgba(0, 210, 255, 0.3);
        --gradient-1: linear-gradient(135deg, #6C63FF, #00D2FF);
        --gradient-2: linear-gradient(135deg, #FF6B6B, #FFB347);
        --gradient-3: linear-gradient(135deg, #2ECC71, #00D2FF);
        --radius: 16px;
        --radius-sm: 10px;
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        --shadow-glow: 0 0 20px rgba(108, 99, 255, 0.2);
    }

    /* ===== Global Styles ===== */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* ===== Sidebar Styling ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D0D2B 0%, #12122A 100%) !important;
        border-right: 1px solid var(--border) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    /* ===== Card Styles ===== */
    .synapse-card {
        background: linear-gradient(145deg, #14142E, #1A1A3E);
        border: 1px solid rgba(108, 99, 255, 0.15);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow);
    }

    .synapse-card:hover {
        border-color: rgba(108, 99, 255, 0.4);
        box-shadow: var(--shadow-glow);
        transform: translateY(-2px);
    }

    /* ===== Topic Cards ===== */
    .topic-card {
        background: linear-gradient(145deg, #14142E, #1A1A3E);
        border: 1px solid rgba(108, 99, 255, 0.15);
        border-radius: var(--radius);
        padding: 1.5rem 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow);
        min-height: 160px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .topic-card:hover {
        border-color: rgba(108, 99, 255, 0.5);
        box-shadow: 0 0 30px rgba(108, 99, 255, 0.25);
        transform: translateY(-4px);
    }

    .topic-card .topic-icon {
        font-size: 2.2rem;
        margin-bottom: 0.6rem;
    }

    .topic-card .topic-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 0.3rem;
    }

    .topic-card .topic-desc {
        font-size: 0.72rem;
        color: #A0A0C0;
        line-height: 1.3;
    }

    /* ===== Gradient Text ===== */
    .gradient-text {
        background: linear-gradient(135deg, #6C63FF, #00D2FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    .gradient-text-warm {
        background: linear-gradient(135deg, #FF6B6B, #FFB347);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    /* ===== Header ===== */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #6C63FF 0%, #00D2FF 50%, #6C63FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .main-header p {
        color: #A0A0C0;
        font-size: 1.1rem;
        font-weight: 300;
    }

    /* ===== Stat Cards ===== */
    .stat-card {
        background: linear-gradient(145deg, #14142E, #1A1A3E);
        border: 1px solid rgba(108, 99, 255, 0.15);
        border-radius: var(--radius);
        padding: 1.2rem 1.5rem;
        text-align: center;
    }

    .stat-card .stat-value {
        font-size: 2rem;
        font-weight: 800;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stat-card .stat-label {
        font-size: 0.85rem;
        color: #A0A0C0;
        margin-top: 0.3rem;
    }

    /* ===== Badge Styles ===== */
    .badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .badge-beginner {
        background: rgba(46, 204, 113, 0.15);
        color: #2ECC71;
        border: 1px solid rgba(46, 204, 113, 0.3);
    }

    .badge-intermediate {
        background: rgba(243, 156, 18, 0.15);
        color: #F39C12;
        border: 1px solid rgba(243, 156, 18, 0.3);
    }

    .badge-advanced {
        background: rgba(108, 99, 255, 0.15);
        color: #8B83FF;
        border: 1px solid rgba(108, 99, 255, 0.3);
    }

    /* ===== Button Overrides ===== */
    .stButton > button {
        background: linear-gradient(135deg, #6C63FF, #5A52D5) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(108, 99, 255, 0.5) !important;
    }

    /* ===== Progress Bar ===== */
    .stProgress > div > div {
        background: var(--gradient-1) !important;
        border-radius: 10px !important;
    }

    /* ===== Chat Messages ===== */
    .stChatMessage {
        border-radius: var(--radius) !important;
        border: 1px solid rgba(108, 99, 255, 0.1) !important;
    }

    /* ===== Metric Cards ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #14142E, #1A1A3E);
        border: 1px solid rgba(108, 99, 255, 0.15);
        border-radius: var(--radius);
        padding: 1rem 1.2rem;
    }

    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
    }

    /* ===== Knowledge Gap Warning ===== */
    .gap-warning {
        background: rgba(243, 156, 18, 0.08);
        border-left: 4px solid #F39C12;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }

    .gap-warning .gap-icon {
        color: #F39C12;
        font-weight: 600;
    }

    /* ===== Source Citation ===== */
    .source-citation {
        background: rgba(0, 210, 255, 0.05);
        border: 1px solid rgba(0, 210, 255, 0.15);
        border-radius: var(--radius-sm);
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        font-size: 0.85rem;
    }

    .source-citation .source-book {
        color: #00D2FF;
        font-weight: 600;
    }

    .source-citation .source-page {
        color: #A0A0C0;
    }

    /* ===== Animations ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 15px rgba(108, 99, 255, 0.2); }
        50% { box-shadow: 0 0 25px rgba(108, 99, 255, 0.4); }
    }

    .animate-fade-in {
        animation: fadeInUp 0.6s ease-out;
    }

    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0A0A1A;
    }
    ::-webkit-scrollbar-thumb {
        background: #2A2A4A;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #3A3A6A;
    }

    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #14142E, #1A1A3E) !important;
        border: 1px solid rgba(108, 99, 255, 0.15) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(20, 20, 46, 0.5);
        border-radius: var(--radius-sm);
        border: 1px solid rgba(108, 99, 255, 0.1);
        padding: 8px 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.2), rgba(0, 210, 255, 0.1)) !important;
        border-color: rgba(108, 99, 255, 0.4) !important;
    }

    /* ===== Divider ===== */
    hr {
        border-color: rgba(108, 99, 255, 0.1) !important;
    }

    /* ===== Hide Streamlit Default ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "authenticated": False,
        "username": None,
        "current_page": "login",
        "selected_topic": None,
        "assessment_questions": None,
        "assessment_answers": [],
        "assessment_complete": False,
        "assessment_result": None,
        "current_question_idx": 0,
        "rag_pipeline": None,
        "rag_initialized": False,
        "topic_banks": None,
        "chat_history": [],
        "tutor_response": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """Render the navigation sidebar."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                <span style="background: linear-gradient(135deg, #6C63FF, #00D2FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">S</span>
            </div>
            <h2 style="margin: 0;">Synapse</h2>
            <p style="color: #A0A0C0; font-size: 0.85rem; margin-top: 0.2rem;">AI Tutor</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        if st.session_state.authenticated:
            st.markdown(f"""
            <div style="background: rgba(108, 99, 255, 0.08); border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 1rem;">
                <div style="color: #A0A0C0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">Logged in as</div>
                <div style="color: #FFFFFF; font-weight: 600; font-size: 1rem;">{st.session_state.username}</div>
            </div>
            """, unsafe_allow_html=True)

            # Navigation buttons
            pages = {
                "topic_selection": "Topics",
                "assessment": "Assessment",
                "tutor": "Tutor",
                "dashboard": "Dashboard",
            }

            for page_key, label in pages.items():
                is_current = st.session_state.current_page == page_key
                if st.button(
                    label,
                    key=f"nav_{page_key}",
                    use_container_width=True,
                    type="primary" if is_current else "secondary"
                ):
                    st.session_state.current_page = page_key
                    st.rerun()

            st.divider()

            # Current topic display
            if st.session_state.selected_topic:
                st.markdown(f"""
                <div style="background: rgba(0, 210, 255, 0.08); border-radius: 10px; padding: 0.8rem 1rem;">
                    <div style="color: #A0A0C0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">Current Topic</div>
                    <div style="color: #00D2FF; font-weight: 600; font-size: 0.95rem;">{st.session_state.selected_topic}</div>
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            # Logout button
            if st.button("Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

            # RAG status
            st.divider()
            if st.session_state.rag_initialized:
                rag = st.session_state.rag_pipeline
                status = rag.get_status()
                st.markdown(f"""
                <div style="font-size: 0.75rem; color: #A0A0C0; padding: 0.5rem;">
                    <div style="color: #2ECC71; font-weight: 600;">RAG Pipeline Active</div>
                    <div style="margin-top: 0.3rem;">{status['num_chunks']} chunks indexed</div>
                    <div>{status['num_vectors']} vectors</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="font-size: 0.75rem; color: #6B6B8D; padding: 0.5rem;">
                    RAG Pipeline: Initializing...
                </div>
                """, unsafe_allow_html=True)


def initialize_rag():
    """Initialize the RAG pipeline if not already done."""
    if not st.session_state.rag_initialized:
        from backend.rag import RAGPipeline

        with st.spinner("Initializing knowledge base... (first run may take a few minutes)"):
            try:
                rag = RAGPipeline()
                success = rag.initialize()

                if success:
                    st.session_state.rag_pipeline = rag
                    st.session_state.rag_initialized = True
                    st.toast("Knowledge base ready!", icon="*")
                else:
                    st.warning("Could not initialize knowledge base. Some features may be limited.")
            except Exception as e:
                st.warning(f"Knowledge base initialization error: {str(e)}")


def main():
    """Main application entry point."""
    configure_page()
    inject_global_styles()
    init_session_state()

    # Render sidebar (always present)
    render_sidebar()

    # Route to the appropriate page
    if not st.session_state.authenticated:
        render_login()
    else:
        # Initialize RAG when user first logs in
        initialize_rag()

        page = st.session_state.current_page

        if page == "topic_selection":
            render_topic_selection()
        elif page == "assessment":
            render_assessment()
        elif page == "tutor":
            render_tutor()
        elif page == "dashboard":
            render_dashboard()
        else:
            render_topic_selection()


if __name__ == "__main__":
    main()
