"""
Synapse AI Tutor -- Main Application Entry Point
Adaptive AI Tutoring System with RAG, GPT-OSS, and PDF Chat.
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pages.login import render_login
from pages.home import render_home
from pages.topic_selection import render_topic_selection
from pages.assessment import render_assessment
from pages.tutor import render_tutor
from pages.chatbot import render_chatbot
from pages.dashboard import render_dashboard
from pages.resources import render_resources
from pages.visualizer import render_visualizer


# ---------------------------------------------------------------------------
# Page config – must be first Streamlit call
# ---------------------------------------------------------------------------
def configure_page():
    st.set_page_config(
        page_title="Synapse AI Tutor",
        page_icon="S",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
def inject_global_styles():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base ──────────────────────────────────────────────────────────────────── */
:root {
    --primary: #6C63FF;
    --primary-dark: #5A52D5;
    --secondary: #00D2FF;
    --success: #2ECC71;
    --warning: #F39C12;
    --danger: #E74C3C;
    --bg: #0A0A1A;
    --bg-card: #12122A;
    --bg-card2: #1A1A3E;
    --text: #FFFFFF;
    --text-dim: #A0A0C0;
    --text-muted: #6B6B8D;
    --border: rgba(108,99,255,0.15);
    --radius: 14px;
    --radius-sm: 8px;
    --shadow: 0 6px 24px rgba(0,0,0,0.35);
    --nav-height: 56px;
}

html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit chrome ──────────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.stDeployButton { display: none !important; }

/* ── Top Navigation ─────────────────────────────────────────────────────────── */
.topnav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: var(--nav-height);
    background: #080816;
    border-bottom: 1px solid var(--border);
    box-shadow: 0 2px 16px rgba(0,0,0,0.4);
    z-index: 9999;
    display: flex;
    align-items: center;
    padding: 0 1.2rem;
    gap: 0.15rem;
}

.topnav-brand {
    font-size: 1rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #00D2FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-right: 1.8rem;
    white-space: nowrap;
    flex-shrink: 0;
}

/* ── Functional nav button strip ─────────────────────────────────────────────── */
.nav-strip {
    position: fixed;
    top: var(--nav-height);
    left: 0; right: 0;
    background: #0B0B1E;
    border-bottom: 1px solid rgba(108,99,255,0.1);
    z-index: 9998;
    display: flex;
    align-items: center;
    padding: 0 1rem;
    height: 42px;
    gap: 2px;
    overflow-x: auto;
}
.nav-strip::-webkit-scrollbar { display: none; }

/* Override Streamlit button in nav strip */
.nav-strip .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 6px !important;
    padding: 0.22rem 0.7rem !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #A0A0C0 !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    height: 30px !important;
    min-height: 30px !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s ease !important;
}
.nav-strip .stButton > button:hover {
    background: rgba(108,99,255,0.12) !important;
    color: #FFFFFF !important;
    border-color: rgba(108,99,255,0.3) !important;
    transform: none !important;
}
.nav-active .stButton > button {
    background: linear-gradient(135deg, rgba(108,99,255,0.35), rgba(0,210,255,0.15)) !important;
    border-color: rgba(108,99,255,0.5) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 8px rgba(108,99,255,0.2) !important;
}
.nav-logout .stButton > button {
    color: #FF6B6B !important;
    border-color: rgba(255,107,107,0.2) !important;
}
.nav-logout .stButton > button:hover {
    background: rgba(255,107,107,0.1) !important;
    border-color: rgba(255,107,107,0.4) !important;
    color: #FF8A8A !important;
}

/* ── Page content spacer ────────────────────────────────────────────────────── */
.page-spacer {
    height: calc(var(--nav-height) + 42px + 0.5rem);
}

/* ── Context bar ─────────────────────────────────────────────────────────────── */
.context-bar {
    background: rgba(108,99,255,0.04);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.55rem 1rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 1.8rem;
    flex-wrap: wrap;
}
.context-item-label {
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
    font-weight: 600;
}
.context-item-value {
    font-size: 0.8rem;
    color: var(--text);
    font-weight: 500;
}

/* ── Cards ────────────────────────────────────────────────────────────────────── */
.synapse-card {
    background: linear-gradient(145deg, var(--bg-card), var(--bg-card2));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    box-shadow: var(--shadow);
}

.stat-card {
    background: linear-gradient(145deg, var(--bg-card), var(--bg-card2));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.9rem 1rem;
    text-align: center;
}
.stat-value {
    font-size: 1.7rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #00D2FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label { font-size: 0.75rem; color: var(--text-dim); margin-top: 0.15rem; }

/* ── Topic cards ──────────────────────────────────────────────────────────────── */
.topic-card {
    background: linear-gradient(145deg, var(--bg-card), var(--bg-card2));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 0.7rem;
    text-align: center;
    min-height: 148px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.topic-card .topic-name { font-size: 0.85rem; font-weight: 600; color: var(--text); margin-bottom: 0.25rem; }
.topic-card .topic-desc { font-size: 0.67rem; color: var(--text-dim); line-height: 1.3; }

/* ── Badges ────────────────────────────────────────────────────────────────────── */
.badge { display: inline-block; padding: 0.18rem 0.6rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
.badge-beginner    { background: rgba(46,204,113,0.12); color: #2ECC71; border: 1px solid rgba(46,204,113,0.3); }
.badge-intermediate{ background: rgba(243,156,18,0.12); color: #F39C12; border: 1px solid rgba(243,156,18,0.3); }
.badge-advanced    { background: rgba(108,99,255,0.12); color: #8B83FF; border: 1px solid rgba(108,99,255,0.3); }

/* ── Global buttons ─────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #5A52D5) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: opacity 0.2s ease !important;
    box-shadow: 0 3px 12px rgba(108,99,255,0.25) !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: none !important;
    box-shadow: 0 3px 12px rgba(108,99,255,0.4) !important;
}

/* ── Other UI elements ───────────────────────────────────────────────────────── */
.gradient-text {
    background: linear-gradient(135deg, #6C63FF, #00D2FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}
.main-header { text-align: center; padding: 0.8rem 0 0.8rem 0; }
.main-header h1 {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #00D2FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem; letter-spacing: -0.02em;
}
.main-header p { color: var(--text-dim); font-size: 0.9rem; }

.gap-warning {
    background: rgba(243,156,18,0.07);
    border-left: 3px solid #F39C12;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
}
.source-citation {
    background: rgba(0,210,255,0.04);
    border: 1px solid rgba(0,210,255,0.15);
    border-radius: var(--radius-sm);
    padding: 0.6rem 0.9rem;
    margin: 0.3rem 0;
    font-size: 0.82rem;
}
.source-citation .source-book { color: #00D2FF; font-weight: 600; }
.source-citation .source-page { color: var(--text-dim); }
.fallback-warning {
    background: rgba(231,76,60,0.07);
    border-left: 3px solid #E74C3C;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
}

.stProgress > div > div {
    background: linear-gradient(135deg, #6C63FF, #00D2FF) !important;
    border-radius: 10px !important;
}
.stChatMessage {
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, var(--bg-card), var(--bg-card2));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.9rem 1rem;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0A0A1A; }
::-webkit-scrollbar-thumb { background: #2A2A4A; border-radius: 3px; }
hr { border-color: rgba(108,99,255,0.1) !important; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.fade-in { animation: fadeIn 0.4s ease-out; }
</style>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "authenticated": False,
        "username": None,
        "page": "Home",
        # Topics
        "selected_topics": [],
        "selected_topic": None,
        # Assessment
        "assessment_questions": None,
        "assessment_answers": [],
        "assessment_complete": False,
        "assessment_result": None,
        "current_question_idx": 0,
        "topic_banks": None,
        "topic_queue": [],
        "topic_queue_idx": 0,
        # RAG
        "rag_pipeline": None,
        "rag_initialized": False,
        # Tutor chat histories (per-topic)
        "chat_histories": {},
        # Chatbot
        "chatbot_history": [],
        "pdf_chunks": None,
        "pdf_index": None,
        "pdf_filename": None,
        "chatbot_use_pdf": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Navigation pages config
# ---------------------------------------------------------------------------
NAV_PAGES = [
    "Home",
    "Topics",
    "Assessment",
    "Tutor",
    "Chatbot",
    "Visualizer",
    "Dashboard",
    "Resources",
]

# Map display labels -> session-state page keys used in routing
PAGE_KEY = {
    "Home":       "Home",
    "Topics":     "Topics",
    "Assessment": "Assessment",
    "Tutor":      "Tutor",
    "Chatbot":    "Chatbot",
    "Visualizer": "Visualizer",
    "Dashboard":  "Dashboard",
    "Resources":  "Resources",
}


def _go(page: str):
    st.session_state.page = page
    st.rerun()


# ---------------------------------------------------------------------------
# Visual-only top bar (brand + user info, pure HTML)
# ---------------------------------------------------------------------------
def render_topnav_html():
    username = st.session_state.get("username", "")
    first = username[0].upper() if username else "?"
    st.markdown(
        f"""
<div class="topnav">
    <span class="topnav-brand">Synapse AI Tutor</span>
    <div style="margin-left:auto;display:flex;align-items:center;gap:0.7rem;">
        <div style="background:rgba(108,99,255,0.15);border:1px solid rgba(108,99,255,0.3);
                    border-radius:20px;padding:0.25rem 0.8rem 0.25rem 0.5rem;
                    display:flex;align-items:center;gap:0.45rem;">
            <div style="width:22px;height:22px;border-radius:50%;
                        background:linear-gradient(135deg,#6C63FF,#00D2FF);
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.68rem;font-weight:700;color:white;flex-shrink:0;">{first}</div>
            <span style="font-size:0.78rem;font-weight:600;color:#FFFFFF;">{username}</span>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Functional navigation strip (Streamlit buttons)
# ---------------------------------------------------------------------------
def render_nav_strip(current: str):
    st.markdown('<div class="nav-strip">', unsafe_allow_html=True)
    total = len(NAV_PAGES) + 1  # +1 for Logout
    cols = st.columns(total)

    for i, label in enumerate(NAV_PAGES):
        active_cls = "nav-active" if current == label else ""
        st.markdown(f'<div class="{active_cls}">', unsafe_allow_html=True)
        with cols[i]:
            if st.button(label, key=f"nav_{label}", use_container_width=False):
                _go(label)
        st.markdown("</div>", unsafe_allow_html=True)

    # Logout
    st.markdown('<div class="nav-logout">', unsafe_allow_html=True)
    with cols[len(NAV_PAGES)]:
        if st.button("Logout", key="nav_logout", use_container_width=False):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Context bar (user / topics / levels) — shown on every authenticated page
# ---------------------------------------------------------------------------
def render_context_bar():
    username = st.session_state.get("username", "")
    selected_topics = st.session_state.get("selected_topics", [])

    topics_display = ", ".join(selected_topics[:3]) if selected_topics else "None selected"
    if len(selected_topics) > 3:
        topics_display += f" +{len(selected_topics) - 3} more"

    try:
        from backend.progress_tracker import get_topic_progress
        lparts = []
        for t in selected_topics[:2]:
            p = get_topic_progress(username, t)
            lv = p.get("level", "Not Assessed")
            if lv != "Not Assessed":
                lc = {"Beginner": "#2ECC71", "Intermediate": "#F39C12", "Advanced": "#8B83FF"}.get(lv, "#A0A0C0")
                short = (t[:14] + "...") if len(t) > 14 else t
                lparts.append(f"<span style='color:{lc};font-weight:600;'>{short}: {lv}</span>")
        levels_html = " &nbsp;|&nbsp; ".join(lparts) if lparts else "<span style='color:#6B6B8D;'>Not assessed yet</span>"
    except Exception:
        levels_html = "<span style='color:#6B6B8D;'>-</span>"

    rag_ready = st.session_state.get("rag_initialized", False)
    rag_color = "#2ECC71" if rag_ready else "#F39C12"
    rag_label = "Ready" if rag_ready else "Loading"

    st.markdown(
        f"""
<div class="context-bar">
    <div>
        <div class="context-item-label">Logged in as</div>
        <div class="context-item-value" style="color:#8B83FF;font-weight:700;">{username}</div>
    </div>
    <div style="width:1px;height:26px;background:rgba(255,255,255,0.06);"></div>
    <div>
        <div class="context-item-label">Selected Topics</div>
        <div class="context-item-value" style="color:#00D2FF;">{topics_display}</div>
    </div>
    <div style="width:1px;height:26px;background:rgba(255,255,255,0.06);"></div>
    <div>
        <div class="context-item-label">Current Levels</div>
        <div style="font-size:0.8rem;">{levels_html}</div>
    </div>
    <div style="width:1px;height:26px;background:rgba(255,255,255,0.06);margin-left:auto;"></div>
    <div>
        <div class="context-item-label">Knowledge Base</div>
        <div class="context-item-value" style="color:{rag_color};">RAG {rag_label}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# RAG initialisation (cached)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _load_rag_pipeline():
    """Load and initialise RAG pipeline once per server session."""
    from backend.rag import RAGPipeline
    rag = RAGPipeline()
    rag.initialize()
    return rag


def initialize_rag():
    if not st.session_state.rag_initialized:
        try:
            rag = _load_rag_pipeline()
            if rag.is_ready:
                st.session_state.rag_pipeline = rag
                st.session_state.rag_initialized = True
        except Exception as e:
            st.warning(f"Knowledge base unavailable: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    configure_page()
    inject_global_styles()
    init_session_state()

    # ── Not logged in — show login
    if not st.session_state.authenticated:
        render_login()
        return

    # ── Logged in
    initialize_rag()
    render_topnav_html()

    current = st.session_state.get("page", "Home")
    render_nav_strip(current)

    # Spacer so content clears both fixed bars
    st.markdown('<div class="page-spacer"></div>', unsafe_allow_html=True)

    render_context_bar()

    # ── Route
    if current == "Home":
        render_home()
    elif current == "Topics":
        render_topic_selection()
    elif current == "Assessment":
        render_assessment()
    elif current == "Tutor":
        render_tutor()
    elif current == "Chatbot":
        render_chatbot()
    elif current == "Visualizer":
        render_visualizer()
    elif current == "Dashboard":
        render_dashboard()
    elif current == "Resources":
        render_resources()
    else:
        render_home()


if __name__ == "__main__":
    main()
