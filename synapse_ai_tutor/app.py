"""
Synapse AI Tutor -- Main Application Entry Point
An Adaptive AI Tutoring System with RAG-powered intelligent teaching.
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pages.login import render_login
from pages.topic_selection import render_topic_selection
from pages.assessment import render_assessment
from pages.tutor import render_tutor
from pages.dashboard import render_dashboard
from pages.roadmap import render_roadmap
from pages.note_viewer import render_note_viewer
from pages.knowledge_vault import render_knowledge_vault
from pages.knowledge_graph_page import render_knowledge_graph


def configure_page():
    st.set_page_config(
        page_title="Synapse AI Tutor",
        page_icon="S",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def inject_global_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    :root {
        --primary: #6C63FF; --primary-dark: #5A52D5; --primary-light: #8B83FF;
        --secondary: #00D2FF; --accent: #FF6B6B; --accent-warm: #FFB347;
        --success: #2ECC71; --warning: #F39C12; --danger: #E74C3C;
        --bg-dark: #0A0A1A; --bg-card: #12122A; --bg-card-hover: #1A1A3E;
        --text-primary: #FFFFFF; --text-secondary: #A0A0C0; --text-muted: #6B6B8D;
        --border: #2A2A4A; --gradient-1: linear-gradient(135deg, #6C63FF, #00D2FF);
        --gradient-2: linear-gradient(135deg, #FF6B6B, #FFB347);
        --gradient-3: linear-gradient(135deg, #2ECC71, #00D2FF);
        --radius: 16px; --radius-sm: 10px;
        --shadow: 0 8px 32px rgba(0,0,0,0.3);
        --shadow-glow: 0 0 20px rgba(108,99,255,0.2);
    }
    .stApp { font-family: 'Inter', -apple-system, sans-serif !important; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D0D2B 0%, #12122A 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    .synapse-card {
        background: linear-gradient(145deg, #14142E, #1A1A3E);
        border: 1px solid rgba(108,99,255,0.15);
        border-radius: var(--radius); padding: 1.5rem; margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1); box-shadow: var(--shadow);
    }
    .synapse-card:hover { border-color: rgba(108,99,255,0.4); box-shadow: var(--shadow-glow); transform: translateY(-2px); }
    .topic-card {
        background: linear-gradient(145deg, #14142E, #1A1A3E);
        border: 1px solid rgba(108,99,255,0.15); border-radius: var(--radius);
        padding: 1.2rem 0.8rem; text-align: center; cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1); box-shadow: var(--shadow);
        min-height: 155px; display: flex; flex-direction: column;
        align-items: center; justify-content: center;
    }
    .topic-card:hover { border-color: rgba(108,99,255,0.5); box-shadow: 0 0 30px rgba(108,99,255,0.25); transform: translateY(-4px); }
    .topic-card .topic-name { font-size: 0.9rem; font-weight: 600; color: #FFFFFF; margin-bottom: 0.3rem; }
    .topic-card .topic-desc { font-size: 0.68rem; color: #A0A0C0; line-height: 1.3; }
    .gradient-text {
        background: linear-gradient(135deg, #6C63FF, #00D2FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;
    }
    .main-header { text-align: center; padding: 1.5rem 0 1rem 0; }
    .main-header h1 {
        font-size: 2.5rem; font-weight: 900;
        background: linear-gradient(135deg, #6C63FF 0%, #00D2FF 50%, #6C63FF 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem; letter-spacing: -0.02em;
    }
    .main-header p { color: #A0A0C0; font-size: 1rem; font-weight: 300; }
    .stat-card {
        background: linear-gradient(145deg, #14142E, #1A1A3E);
        border: 1px solid rgba(108,99,255,0.15); border-radius: var(--radius);
        padding: 1rem 1.2rem; text-align: center;
    }
    .stat-card .stat-value {
        font-size: 1.8rem; font-weight: 800;
        background: var(--gradient-1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stat-card .stat-label { font-size: 0.8rem; color: #A0A0C0; margin-top: 0.3rem; }
    .badge { display: inline-block; padding: 0.25rem 0.7rem; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
    .badge-beginner { background: rgba(46,204,113,0.15); color: #2ECC71; border: 1px solid rgba(46,204,113,0.3); }
    .badge-intermediate { background: rgba(243,156,18,0.15); color: #F39C12; border: 1px solid rgba(243,156,18,0.3); }
    .badge-advanced { background: rgba(108,99,255,0.15); color: #8B83FF; border: 1px solid rgba(108,99,255,0.3); }
    .stButton > button {
        background: linear-gradient(135deg, #6C63FF, #5A52D5) !important;
        color: white !important; border: none !important; border-radius: var(--radius-sm) !important;
        padding: 0.6rem 1.5rem !important; font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important; transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(108,99,255,0.3) !important;
    }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(108,99,255,0.5) !important; }
    .stProgress > div > div { background: var(--gradient-1) !important; border-radius: 10px !important; }
    .stChatMessage { border-radius: var(--radius) !important; border: 1px solid rgba(108,99,255,0.1) !important; }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #14142E, #1A1A3E);
        border: 1px solid rgba(108,99,255,0.15); border-radius: var(--radius); padding: 1rem 1.2rem;
    }
    .gap-warning {
        background: rgba(243,156,18,0.08); border-left: 4px solid #F39C12;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0; padding: 1rem 1.2rem; margin: 0.5rem 0;
    }
    .source-citation {
        background: rgba(0,210,255,0.05); border: 1px solid rgba(0,210,255,0.15);
        border-radius: var(--radius-sm); padding: 0.8rem 1rem; margin: 0.4rem 0; font-size: 0.85rem;
    }
    .source-citation .source-book { color: #00D2FF; font-weight: 600; }
    .source-citation .source-page { color: #A0A0C0; }
    .diff-easy { color: #2ECC71; }
    .diff-intermediate { color: #F39C12; }
    .diff-hard { color: #8B83FF; }
    .fallback-warning {
        background: rgba(231,76,60,0.08); border-left: 4px solid #E74C3C;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0; padding: 0.8rem 1rem; margin: 0.5rem 0;
    }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .animate-fade-in { animation: fadeInUp 0.6s ease-out; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0A0A1A; }
    ::-webkit-scrollbar-thumb { background: #2A2A4A; border-radius: 3px; }
    hr { border-color: rgba(108,99,255,0.1) !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    defaults = {
        "authenticated": False,
        "username": None,
        "current_page": "login",
        # Multi-topic support
        "selected_topics": [],           # List of selected topics
        "selected_topic": None,          # Current single topic being assessed/tutored
        # Assessment state (per topic)
        "assessment_questions": None,
        "assessment_answers": [],
        "assessment_complete": False,
        "assessment_result": None,
        "current_question_idx": 0,
        # RAG
        "rag_pipeline": None,
        "rag_initialized": False,
        # Question bank (shared across topics)
        "topic_banks": None,
        # Chat history (per-topic)
        "chat_histories": {},            # {topic: [msgs]}
        "tutor_response": None,
        # Topic queue for multi-topic flow
        "topic_queue": [],
        "topic_queue_idx": 0,
        # Roadmap & Notes
        "generated_notes": {},           # {topic: note_content}
        "current_roadmap": None,         # Current roadmap data
        "roadmap_topic": None,           # Topic the roadmap was generated for
        "_viewing_note": None,           # Currently viewing note topic
        "_vault_viewing": None,          # Vault note being viewed
        "_note_viewer_topic": None,      # Note viewer page topic
        "_graph_view": "full",           # Knowledge graph view mode
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0;">
            <div style="font-size:2rem;font-weight:900;background:linear-gradient(135deg,#6C63FF,#00D2FF);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">SYN</div>
            <div style="color:#FFFFFF;font-weight:700;font-size:1.1rem;margin-top:0.2rem;">Synapse</div>
            <div style="color:#A0A0C0;font-size:0.8rem;">Adaptive AI Tutor</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        if st.session_state.authenticated:
            st.markdown(f"""
            <div style="background:rgba(108,99,255,0.08);border-radius:10px;padding:0.8rem 1rem;margin-bottom:1rem;">
                <div style="color:#A0A0C0;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;">Logged in as</div>
                <div style="color:#FFFFFF;font-weight:600;">{st.session_state.username}</div>
            </div>
            """, unsafe_allow_html=True)

            pages = {
                "topic_selection": "Topics",
                "assessment": "Assessment",
                "tutor": "Tutor",
                "roadmap": "Roadmap",
                "knowledge_vault": "Vault",
                "knowledge_graph": "Graph",
                "dashboard": "Dashboard",
            }
            for page_key, label in pages.items():
                is_current = st.session_state.current_page == page_key
                if st.button(label, key=f"nav_{page_key}", use_container_width=True,
                             type="primary" if is_current else "secondary"):
                    st.session_state.current_page = page_key
                    st.rerun()

            st.divider()

            # Show selected topics
            if st.session_state.selected_topics:
                st.markdown("""
                <div style="color:#A0A0C0;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.4rem;">
                    Selected Topics
                </div>""", unsafe_allow_html=True)
                for t in st.session_state.selected_topics[:4]:
                    short = t[:20] + "..." if len(t) > 20 else t
                    st.markdown(f"""
                    <div style="color:#00D2FF;font-size:0.8rem;padding:0.2rem 0.5rem;
                                background:rgba(0,210,255,0.06);border-radius:6px;margin-bottom:0.2rem;">
                        {short}
                    </div>""", unsafe_allow_html=True)
                if len(st.session_state.selected_topics) > 4:
                    st.markdown(f"<div style='color:#6B6B8D;font-size:0.72rem;'>+{len(st.session_state.selected_topics)-4} more</div>", unsafe_allow_html=True)
                st.divider()

            if st.button("Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

            st.divider()
            if st.session_state.rag_initialized:
                rag = st.session_state.rag_pipeline
                status = rag.get_status()
                st.markdown(f"""
                <div style="font-size:0.72rem;color:#A0A0C0;padding:0.4rem;">
                    <div style="color:#2ECC71;font-weight:600;margin-bottom:0.3rem;">RAG Active</div>
                    <div>{status['num_chunks']} chunks | {status['num_vectors']} vectors</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="font-size:0.72rem;color:#6B6B8D;padding:0.4rem;">RAG: Initializing...</div>
                """, unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def _load_rag_pipeline():
    """
    Load and initialize the RAG pipeline ONCE per Streamlit server session.
    st.cache_resource keeps this in memory across all reruns and all users.
    The FAISS index + chunks are loaded from disk once and reused forever.
    """
    from backend.rag import RAGPipeline
    rag = RAGPipeline()
    rag.initialize()
    return rag


def initialize_rag():
    """Attach the cached RAG pipeline to session state if not already done."""
    if not st.session_state.rag_initialized:
        try:
            # _load_rag_pipeline() is only executed on first call;
            # every subsequent call returns the already-loaded object instantly.
            rag = _load_rag_pipeline()
            if rag.is_ready:
                st.session_state.rag_pipeline = rag
                st.session_state.rag_initialized = True
            else:
                st.warning("Knowledge base not ready. Tutor will work without textbook context.")
        except Exception as e:
            st.warning(f"Knowledge base error: {str(e)}")


def main():
    configure_page()
    inject_global_styles()
    init_session_state()
    render_sidebar()

    if not st.session_state.authenticated:
        render_login()
    else:
        initialize_rag()
        page = st.session_state.current_page

        if page == "topic_selection":
            render_topic_selection()
        elif page == "assessment":
            render_assessment()
        elif page == "tutor":
            render_tutor()
        elif page == "roadmap":
            render_roadmap()
        elif page == "note_viewer":
            render_note_viewer()
        elif page == "knowledge_vault":
            render_knowledge_vault()
        elif page == "knowledge_graph":
            render_knowledge_graph()
        elif page == "dashboard":
            render_dashboard()
        else:
            render_topic_selection()


if __name__ == "__main__":
    main()
