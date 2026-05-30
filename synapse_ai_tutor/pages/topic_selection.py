"""
Topic Selection Page for Synapse AI Tutor.
"""

import streamlit as st
from backend.progress_tracker import get_topic_progress, topic_is_assessed

TOPICS = {
    "Neural Networks":            {"abbr": "NN", "description": "Perceptrons, backpropagation, activation functions", "color": "#6C63FF"},
    "CNNs":                       {"abbr": "CN", "description": "Convolutional nets for image processing",            "color": "#00D2FF"},
    "RNNs":                       {"abbr": "RN", "description": "Recurrent nets, LSTM, GRU, time series",             "color": "#FF6B6B"},
    "Transformers":               {"abbr": "TF", "description": "Self-attention, multi-head attention, BERT",         "color": "#FFB347"},
    "LLMs":                       {"abbr": "LM", "description": "GPT, scaling laws, tokenization, reasoning",         "color": "#2ECC71"},
    "Prompt Engineering":         {"abbr": "PE", "description": "Few-shot, chain-of-thought, templates",              "color": "#E74C3C"},
    "Generative AI Fundamentals": {"abbr": "GA", "description": "Latent space, evaluation, AI ethics",               "color": "#9B59B6"},
    "GANs":                       {"abbr": "GN", "description": "Generator, discriminator, adversarial training",     "color": "#1ABC9C"},
    "Diffusion Models":           {"abbr": "DM", "description": "DDPM, stable diffusion, denoising process",         "color": "#3498DB"},
    "Fine-Tuning and RAG":        {"abbr": "FR", "description": "LoRA, QLoRA, retrieval-augmented generation",        "color": "#F39C12"},
}


def _hex_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


def _go(page: str):
    st.session_state.page = page
    st.rerun()


def render_topic_selection():
    username = st.session_state.username

    st.markdown(
        """
<div class="main-header fade-in">
    <h1>Choose Your Topics</h1>
    <p>Select one or more topics to begin personalised learning</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if "selected_topics" not in st.session_state:
        st.session_state.selected_topics = []

    topics_list  = list(TOPICS.items())
    selected_set = set(st.session_state.selected_topics)

    for row in range(2):
        cols = st.columns(5)
        for ci in range(5):
            idx = row * 5 + ci
            if idx >= len(topics_list):
                break
            topic_name, meta = topics_list[idx]
            progress  = get_topic_progress(username, topic_name)
            mastery   = progress.get("mastery", 0)
            level     = progress.get("level", "Not Assessed")
            assessed  = topic_is_assessed(username, topic_name)
            selected  = topic_name in selected_set

            with cols[ci]:
                badge_html = ""
                if level == "Beginner":
                    badge_html = '<span class="badge badge-beginner">Beginner</span>'
                elif level == "Intermediate":
                    badge_html = '<span class="badge badge-intermediate">Intermediate</span>'
                elif level == "Advanced":
                    badge_html = '<span class="badge badge-advanced">Advanced</span>'

                mastery_bar = ""
                if mastery > 0:
                    mastery_bar = f"""
<div style="margin-top:0.4rem;">
    <div style="display:flex;justify-content:space-between;font-size:0.62rem;color:#A0A0C0;margin-bottom:0.12rem;">
        <span>Mastery</span><span>{mastery}%</span>
    </div>
    <div style="background:rgba(255,255,255,0.05);border-radius:3px;height:3px;overflow:hidden;">
        <div style="background:{meta['color']};width:{mastery}%;height:100%;border-radius:3px;"></div>
    </div>
</div>"""

                border_extra = (
                    f"border:2px solid {meta['color']};box-shadow:0 0 14px rgba({_hex_rgb(meta['color'])},0.3);"
                    if selected else ""
                )

                st.markdown(
                    f"""
<div class="topic-card" style="{border_extra}">
    <div style="font-size:1.1rem;font-weight:900;letter-spacing:-1px;
                background:linear-gradient(135deg,{meta['color']},{meta['color']}88);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin-bottom:0.25rem;">{meta['abbr']}</div>
    <div class="topic-name">{topic_name}</div>
    <div class="topic-desc">{meta['description']}</div>
    <div style="margin-top:0.35rem;">{badge_html}</div>
    {mastery_bar}
    {"<div style='font-size:0.6rem;color:#2ECC71;margin-top:0.25rem;'>Selected</div>" if selected else ""}
</div>
""",
                    unsafe_allow_html=True,
                )

                btn_label = "Deselect" if selected else ("Select" if not assessed else "Re-Select")
                if st.button(btn_label, key=f"sel_{topic_name}", use_container_width=True):
                    if selected:
                        st.session_state.selected_topics.remove(topic_name)
                    else:
                        if topic_name not in st.session_state.selected_topics:
                            st.session_state.selected_topics.append(topic_name)
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Action panel ──────────────────────────────────────────────────────────
    sel = st.session_state.selected_topics
    st.divider()

    if not sel:
        st.info("Select at least one topic above to continue.")
        return

    tags_html = " &nbsp;|&nbsp; ".join(f"<strong>{t}</strong>" for t in sel)
    st.markdown(
        f"""
<div style="background:rgba(108,99,255,0.06);border:1px solid rgba(108,99,255,0.14);
            border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:0.8rem;">
    <div style="color:#A0A0C0;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">
        {len(sel)} topic{"s" if len(sel) > 1 else ""} selected
    </div>
    <div style="color:#FFFFFF;font-weight:600;font-size:0.88rem;">{tags_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    already_assessed = [t for t in sel if topic_is_assessed(username, t)]
    not_assessed     = [t for t in sel if not topic_is_assessed(username, t)]

    ac1, ac2, ac3 = st.columns([2, 2, 1])

    with ac1:
        if not_assessed:
            if st.button(
                f"Start Assessment ({len(not_assessed)} new topic{'s' if len(not_assessed) > 1 else ''})",
                use_container_width=True,
                type="primary",
            ):
                st.session_state.topic_queue     = not_assessed[:]
                st.session_state.topic_queue_idx = 0
                _start_next_assessment()
        elif already_assessed:
            if st.button("Retake Assessments", use_container_width=True, type="primary"):
                st.session_state.topic_queue     = sel[:]
                st.session_state.topic_queue_idx = 0
                _start_next_assessment()

    with ac2:
        if already_assessed:
            first = already_assessed[0]
            if st.button(f"Continue Learning: {first[:20]}", use_container_width=True):
                st.session_state.selected_topic = first
                if first not in st.session_state.chat_histories:
                    st.session_state.chat_histories[first] = []
                _go("Tutor")

    with ac3:
        if st.button("Dashboard", use_container_width=True):
            _go("Dashboard")

    # ── Existing profiles ──────────────────────────────────────────────────────
    if already_assessed:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-weight:600;color:#FFFFFF;font-size:0.92rem;margin-bottom:0.7rem;">'
            "Existing Profile (previous sessions)</div>",
            unsafe_allow_html=True,
        )
        profile_cols = st.columns(min(len(already_assessed), 3))
        for i, tn in enumerate(already_assessed[:3]):
            prog    = get_topic_progress(username, tn)
            mastery = prog.get("mastery", 0)
            level   = prog.get("level", "Not Assessed")
            gaps    = prog.get("knowledge_gaps", [])
            lc      = {"Beginner": "#2ECC71", "Intermediate": "#F39C12", "Advanced": "#8B83FF"}.get(level, "#A0A0C0")
            gaps_html = "<br>".join(
                f"<span style='font-size:0.68rem;color:#F39C12;'>* {g}</span>" for g in gaps[:3]
            ) if gaps else "<span style='font-size:0.68rem;color:#6B6B8D;'>No gaps detected</span>"

            with profile_cols[i]:
                st.markdown(
                    f"""
<div class="synapse-card" style="text-align:center;padding:0.9rem;">
    <div style="color:#A0A0C0;font-size:0.68rem;margin-bottom:0.3rem;">{tn}</div>
    <div style="font-size:1.6rem;font-weight:800;color:{lc};">{mastery}%</div>
    <div style="color:{lc};font-weight:600;font-size:0.82rem;margin-bottom:0.4rem;">{level}</div>
    <div style="text-align:left;">{gaps_html}</div>
</div>
""",
                    unsafe_allow_html=True,
                )


def _start_next_assessment():
    idx = st.session_state.topic_queue_idx
    if idx < len(st.session_state.topic_queue):
        topic = st.session_state.topic_queue[idx]
        st.session_state.selected_topic        = topic
        st.session_state.assessment_questions  = None
        st.session_state.assessment_answers    = []
        st.session_state.assessment_complete   = False
        st.session_state.assessment_result     = None
        st.session_state.current_question_idx  = 0
        st.session_state.page = "Assessment"
        st.rerun()
