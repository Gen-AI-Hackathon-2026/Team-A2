"""
Tutor Page for Synapse AI Tutor.
Adaptive AI tutoring with GraphRAG retrieval, source visibility,
knowledge gap loading, fallback mode, and dynamic mastery updates.

GraphRAG is the default retrieval method. Falls back to standard RAG
if the graph or index is unavailable.
"""

import streamlit as st
from backend.progress_tracker import (
    get_topic_progress, get_mastery_scores,
    update_knowledge_gaps, update_mastery_from_practice,
    update_session_access,
)
from backend.gap_detector import detect_knowledge_gaps
from backend.llm_client import generate_tutoring_response, check_connection
from backend.resources import get_resources_for_level

LEVEL_COLORS = {"Beginner": "#2ECC71", "Intermediate": "#F39C12", "Advanced": "#8B83FF"}


def _go(page: str):
    st.session_state.page = page
    st.rerun()


def render_tutor():
    selected_topic = st.session_state.get("selected_topic")
    if not selected_topic:
        st.warning("No topic selected. Please choose a topic first.")
        if st.button("Go to Topics", key="tutor_notopic"):
            _go("Topics")
        return

    topic    = selected_topic
    username = st.session_state.username

    # Load persistent profile
    progress = get_topic_progress(username, topic)
    level    = progress.get("level", "Beginner")
    mastery  = progress.get("mastery", 0)
    if level == "Not Assessed":
        level = "Beginner"

    # Load and merge knowledge gaps
    saved_gaps     = progress.get("knowledge_gaps", [])
    mastery_scores = get_mastery_scores(username)
    gap_analysis   = detect_knowledge_gaps(topic, mastery_scores)
    dynamic_gaps   = gap_analysis.get("gaps", [])
    all_gaps       = list(dict.fromkeys(saved_gaps + dynamic_gaps))
    knowledge_gaps = all_gaps[:8]

    update_knowledge_gaps(username, topic, knowledge_gaps)
    update_session_access(username, topic)

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        f"""
<div class="fade-in" style="margin-bottom:0.8rem;">
    <h1 class="gradient-text" style="font-size:1.9rem;margin-bottom:0.15rem;">AI Tutor</h1>
    <p style="color:#A0A0C0;font-size:0.88rem;">
        Adaptive companion for <strong style="color:#00D2FF;">{topic}</strong>
        &nbsp;|&nbsp;
        <span style="color:#8B83FF;font-size:0.78rem;font-weight:600;">GraphRAG Powered</span>
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    # ── Info bar ──────────────────────────────────────────────────────────────
    lc = LEVEL_COLORS.get(level, "#A0A0C0")
    try:
        connected = check_connection()
    except Exception:
        connected = False
    llm_color = "#2ECC71" if connected else "#E74C3C"
    llm_label = "Online"   if connected else "Offline (Fallback)"

    ic1, ic2, ic3, ic4 = st.columns(4)
    for col, (lbl, val, vc) in zip(
        [ic1, ic2, ic3, ic4],
        [
            ("Topic",    topic,     "#00D2FF"),
            ("Level",    level,     lc),
            ("Mastery",  f"{mastery}%", "#FFFFFF"),
            ("AI Model", llm_label, llm_color),
        ],
    ):
        with col:
            st.markdown(
                f'<div class="stat-card">'
                f'<div style="color:#A0A0C0;font-size:0.68rem;text-transform:uppercase;">{lbl}</div>'
                f'<div style="color:{vc};font-weight:700;font-size:0.85rem;margin-top:0.15rem;">{val}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Knowledge Gaps ────────────────────────────────────────────────────────
    if knowledge_gaps:
        # Get graph-based recommendations
        try:
            from backend.graph_rag import get_gap_recommendations
            gap_recs = get_gap_recommendations(knowledge_gaps[:3], topic)
        except Exception:
            gap_recs = []

        gap_str = " &nbsp;|&nbsp; ".join(
            f"<span style='color:#F39C12;'>{g}</span>" for g in knowledge_gaps[:5]
        )
        st.markdown(
            f"""
<div class="gap-warning" style="margin-top:0.7rem;">
    <div style="color:#F39C12;font-weight:600;font-size:0.85rem;margin-bottom:0.25rem;">Knowledge Gaps</div>
    <div style="font-size:0.8rem;">{gap_str}</div>
    <div style="color:#6B6B8D;font-size:0.72rem;margin-top:0.25rem;">{gap_analysis.get("recommendation", "")}</div>
""",
            unsafe_allow_html=True,
        )
        if gap_recs:
            for rec in gap_recs[:2]:
                path_str = " -> ".join(rec["path"])
                st.markdown(
                    f'<div style="color:#A0A0C0;font-size:0.72rem;margin-top:0.2rem;">'
                    f'Study path: <span style="color:#8B83FF;">{path_str}</span></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Multi-topic switcher ──────────────────────────────────────────────────
    sel_topics = st.session_state.get("selected_topics", [])
    if len(sel_topics) > 1:
        others = [t for t in sel_topics if t != topic]
        with st.expander(f"Switch Topic ({len(sel_topics)} topics selected)"):
            scols = st.columns(min(len(others), 4))
            for i, t in enumerate(others[:4]):
                with scols[i]:
                    if st.button(t[:18], key=f"switch_{t}"):
                        st.session_state.selected_topic = t
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chat Interface ────────────────────────────────────────────────────────
    _render_chat(topic, level, mastery, knowledge_gaps, username)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Resources ─────────────────────────────────────────────────────────────
    _render_resources_section(topic, level, knowledge_gaps, gap_analysis)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Practice Tracker ──────────────────────────────────────────────────────
    _render_practice_tracker(topic, username)


# ---------------------------------------------------------------------------
def _render_chat(topic, level, mastery, knowledge_gaps, username):
    st.markdown(
        '<div style="font-weight:600;color:#FFFFFF;font-size:0.92rem;margin-bottom:0.7rem;">Chat with Synapse</div>',
        unsafe_allow_html=True,
    )

    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = {}
    if topic not in st.session_state.chat_histories:
        st.session_state.chat_histories[topic] = []

    chat_history = st.session_state.chat_histories[topic]

    # Render existing messages
    for msg in chat_history:
        role = msg["role"]
        with st.chat_message(role, avatar="user" if role == "user" else "assistant"):
            st.markdown(msg["content"])

            # GraphRAG panel
            if role == "assistant" and msg.get("graph_data"):
                gd = msg["graph_data"]
                _render_graph_panel(gd)

            # Sources panel
            if role == "assistant" and msg.get("sources"):
                with st.expander(f"Sources ({len(msg['sources'])} passages)", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(
                            f'<div class="source-citation"><div>'
                            f'<span class="source-book">{src["source"]}</span>'
                            f'<span class="source-page"> - Page {src["page"]}</span></div>'
                            f'<div style="color:#6B6B8D;font-size:0.72rem;margin-top:0.25rem;'
                            f'font-style:italic;line-height:1.4;">{src["text"][:260]}...</div></div>',
                            unsafe_allow_html=True,
                        )

    user_q = st.chat_input(f"Ask about {topic}...", key="tutor_input")

    if user_q:
        chat_history.append({"role": "user", "content": user_q, "sources": [], "graph_data": None})
        st.session_state.chat_histories[topic] = chat_history

        with st.chat_message("user", avatar="user"):
            st.markdown(user_q)

        with st.chat_message("assistant", avatar="assistant"):
            with st.spinner("Retrieving with GraphRAG..."):
                graph_data  = {}
                retrieved   = []

                rag_ready = st.session_state.get("rag_initialized", False)
                if rag_ready:
                    rag = st.session_state.rag_pipeline
                    try:
                        # GraphRAG — default path
                        result = rag.graph_rag_search(user_q, topic, k=6)
                        retrieved  = result.get("chunks", [])
                        graph_data = {
                            "matched_concepts":   result.get("matched_concepts", []),
                            "neighbour_concepts": result.get("neighbour_concepts", []),
                            "expanded_query":     result.get("expanded_query", user_q),
                            "retrieval_method":   result.get("retrieval_method", "GraphRAG"),
                        }
                    except Exception:
                        # Fallback to standard search
                        retrieved  = rag.search_for_topic(topic, user_q, k=5)
                        graph_data = {"retrieval_method": "Standard RAG (graph unavailable)"}

                # Inject graph context into the LLM prompt via knowledge gaps
                if graph_data.get("matched_concepts") or graph_data.get("neighbour_concepts"):
                    try:
                        from backend.graph_rag import build_graph_context
                        graph_ctx = build_graph_context(
                            graph_data.get("matched_concepts", []),
                            graph_data.get("neighbour_concepts", []),
                            topic,
                        )
                        # Prepend graph context as an extra knowledge-gap entry
                        enhanced_gaps = [graph_ctx[:200]] + knowledge_gaps
                    except Exception:
                        enhanced_gaps = knowledge_gaps
                else:
                    enhanced_gaps = knowledge_gaps

            with st.spinner("Generating response..."):
                response = generate_tutoring_response(
                    topic=topic,
                    level=level,
                    knowledge_gaps=enhanced_gaps,
                    retrieved_chunks=retrieved,
                    student_question=user_q,
                    mastery=mastery,
                    model=None,
                )

            full_text  = response.get("full_response", response.get("explanation", ""))
            sources    = response.get("sources", [])
            fallback   = response.get("fallback_used", False)

            if fallback:
                st.markdown(
                    '<div class="fallback-warning"><strong style="color:#E74C3C;">AI Model Offline</strong>'
                    '<span style="color:#A0A0C0;font-size:0.82rem;"> Showing textbook content. '
                    'AI resumes when server is back online.</span></div>',
                    unsafe_allow_html=True,
                )

            # Show GraphRAG panel inline
            if graph_data:
                _render_graph_panel(graph_data)

            st.markdown(full_text)

            if sources:
                with st.expander(f"Sources ({len(sources)} passages retrieved)", expanded=True):
                    for src in sources:
                        st.markdown(
                            f'<div class="source-citation"><div>'
                            f'<span class="source-book">{src["source"]}</span>'
                            f'<span class="source-page"> - Page {src["page"]}</span></div>'
                            f'<div style="color:#6B6B8D;font-size:0.74rem;margin-top:0.25rem;'
                            f'line-height:1.4;font-style:italic;">{src["text"][:280]}...</div></div>',
                            unsafe_allow_html=True,
                        )

            chat_history.append({
                "role":       "assistant",
                "content":    full_text,
                "sources":    sources,
                "graph_data": graph_data,
            })
            st.session_state.chat_histories[topic] = chat_history

    # Suggestion prompts when chat is empty
    if not chat_history:
        suggestions = _get_suggestions(topic)
        st.markdown(
            '<div style="color:#6B6B8D;font-size:0.8rem;text-align:center;margin:0.8rem 0 0.5rem;">Try asking one of these:</div>',
            unsafe_allow_html=True,
        )
        scols = st.columns(len(suggestions))
        for i, (col, sug) in enumerate(zip(scols, suggestions)):
            with col:
                if st.button(sug, key=f"sug_{i}"):
                    st.session_state.chat_histories[topic].append(
                        {"role": "user", "content": sug, "sources": [], "graph_data": None}
                    )
                    st.rerun()


# ---------------------------------------------------------------------------
def _render_graph_panel(graph_data: dict):
    """Render the GraphRAG retrieval details panel."""
    method   = graph_data.get("retrieval_method", "GraphRAG")
    matched  = graph_data.get("matched_concepts", [])
    nbrs     = graph_data.get("neighbour_concepts", [])

    if not matched and not nbrs:
        return

    method_color = "#8B83FF" if "GraphRAG" in method else "#F39C12"

    matched_html = " &nbsp;".join(
        f'<span style="background:rgba(108,99,255,0.12);border:1px solid rgba(108,99,255,0.3);'
        f'border-radius:12px;padding:0.15rem 0.55rem;color:#8B83FF;font-size:0.7rem;">{c}</span>'
        for c in matched[:5]
    )
    nbr_html = " &nbsp;".join(
        f'<span style="background:rgba(0,210,255,0.07);border:1px solid rgba(0,210,255,0.2);'
        f'border-radius:12px;padding:0.15rem 0.55rem;color:#00D2FF;font-size:0.7rem;">{c}</span>'
        for c in nbrs[:6]
    )

    st.markdown(
        f"""
<div style="background:rgba(108,99,255,0.04);border:1px solid rgba(108,99,255,0.12);
            border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.7rem;">
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
        <div style="width:6px;height:6px;border-radius:50%;background:{method_color};"></div>
        <span style="color:{method_color};font-size:0.72rem;font-weight:700;
                     text-transform:uppercase;letter-spacing:0.8px;">{method}</span>
    </div>
    {"<div style='margin-bottom:0.35rem;'><span style='color:#6B6B8D;font-size:0.68rem;margin-right:0.5rem;'>Matched:</span>" + matched_html + "</div>" if matched_html else ""}
    {"<div><span style='color:#6B6B8D;font-size:0.68rem;margin-right:0.5rem;'>Graph Expanded:</span>" + nbr_html + "</div>" if nbr_html else ""}
</div>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
def _render_resources_section(topic, level, knowledge_gaps, gap_analysis):
    resources    = get_resources_for_level(topic, level)
    key_concepts = gap_analysis.get("key_concepts", [])

    st.markdown(
        '<div style="text-align:center;margin-bottom:1rem;">'
        '<span style="font-weight:700;color:#FFFFFF;font-size:1rem;">Learning Resources</span>'
        '<p style="color:#A0A0C0;font-size:0.78rem;margin-top:0.2rem;">Curated content for your level</p>'
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div style="font-weight:600;color:#8B83FF;font-size:0.82rem;margin-bottom:0.5rem;border-bottom:2px solid rgba(139,131,255,0.3);padding-bottom:0.25rem;">Key Concepts</div>', unsafe_allow_html=True)
        if key_concepts:
            for c in key_concepts:
                st.markdown(f'<div style="padding:0.3rem 0.6rem;margin-bottom:0.2rem;background:rgba(108,99,255,0.05);border-radius:5px;border-left:2px solid #6C63FF;color:#A0A0C0;font-size:0.75rem;">{c}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#6B6B8D;font-size:0.75rem;">None listed.</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="font-weight:600;color:#00D2FF;font-size:0.82rem;margin-bottom:0.5rem;border-bottom:2px solid rgba(0,210,255,0.3);padding-bottom:0.25rem;">Videos</div>', unsafe_allow_html=True)
        for vid in resources.get("videos", [])[:3]:
            st.markdown(f'<div style="padding:0.45rem 0.65rem;margin-bottom:0.3rem;background:rgba(0,210,255,0.04);border-radius:7px;border:1px solid rgba(0,210,255,0.12);"><a href="{vid["url"]}" target="_blank" style="color:#00D2FF;font-size:0.75rem;text-decoration:none;font-weight:500;line-height:1.4;display:block;">{vid["title"][:44]}{"..." if len(vid["title"])>44 else ""}</a><div style="color:#6B6B8D;font-size:0.65rem;margin-top:0.15rem;">{vid["description"][:55]}</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div style="font-weight:600;color:#FF6B6B;font-size:0.82rem;margin-bottom:0.5rem;border-bottom:2px solid rgba(255,107,107,0.3);padding-bottom:0.25rem;">Articles</div>', unsafe_allow_html=True)
        for art in resources.get("articles", [])[:3]:
            st.markdown(f'<div style="padding:0.45rem 0.65rem;margin-bottom:0.3rem;background:rgba(255,107,107,0.04);border-radius:7px;border:1px solid rgba(255,107,107,0.12);"><a href="{art["url"]}" target="_blank" style="color:#FF6B6B;font-size:0.75rem;text-decoration:none;font-weight:500;line-height:1.4;display:block;">{art["title"][:44]}{"..." if len(art["title"])>44 else ""}</a><div style="color:#6B6B8D;font-size:0.65rem;margin-top:0.15rem;">{art["description"][:55]}</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div style="font-weight:600;color:#2ECC71;font-size:0.82rem;margin-bottom:0.5rem;border-bottom:2px solid rgba(46,204,113,0.3);padding-bottom:0.25rem;">Documentation</div>', unsafe_allow_html=True)
        for doc in resources.get("documentation", [])[:3]:
            st.markdown(f'<div style="padding:0.45rem 0.65rem;margin-bottom:0.3rem;background:rgba(46,204,113,0.04);border-radius:7px;border:1px solid rgba(46,204,113,0.12);"><a href="{doc["url"]}" target="_blank" style="color:#2ECC71;font-size:0.75rem;text-decoration:none;font-weight:500;line-height:1.4;display:block;">{doc["title"][:44]}{"..." if len(doc["title"])>44 else ""}</a><div style="color:#6B6B8D;font-size:0.65rem;margin-top:0.15rem;">{doc["description"][:55]}</div></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
def _render_practice_tracker(topic, username):
    with st.expander("Log Practice Performance (updates mastery score)", expanded=False):
        st.markdown(
            '<div style="color:#A0A0C0;font-size:0.8rem;margin-bottom:0.7rem;">'
            "After answering practice questions, log your score here to update your mastery."
            "</div>",
            unsafe_allow_html=True,
        )
        pc1, pc2, pc3 = st.columns([1, 1, 2])
        with pc1:
            correct = st.number_input("Correct", min_value=0, max_value=20, value=0, step=1, key="prac_correct")
        with pc2:
            total = st.number_input("Total", min_value=1, max_value=20, value=3, step=1, key="prac_total")
        with pc3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Update Mastery", use_container_width=True, key="prac_update"):
                update_mastery_from_practice(username, topic, correct, total)
                st.success(f"Mastery updated. Answered {correct}/{total} correctly.")
                st.rerun()


# ---------------------------------------------------------------------------
def _get_suggestions(topic: str) -> list:
    return {
        "Neural Networks":            ["What is backpropagation?", "Explain activation functions", "How do neurons learn?"],
        "CNNs":                       ["How do convolutions work?", "What is pooling?", "Explain feature maps"],
        "RNNs":                       ["What is vanishing gradient?", "How does LSTM work?", "Explain sequence modelling"],
        "Transformers":               ["Explain self-attention", "What is multi-head attention?", "How does positional encoding work?"],
        "LLMs":                       ["How do LLMs generate text?", "What are scaling laws?", "Explain tokenisation"],
        "Prompt Engineering":         ["What is chain-of-thought?", "How to write system prompts?", "Explain few-shot prompting"],
        "Generative AI Fundamentals": ["What is generative AI?", "Explain latent space", "How are generative models trained?"],
        "GANs":                       ["How do GANs work?", "What is mode collapse?", "Explain adversarial training"],
        "Diffusion Models":           ["How does stable diffusion work?", "Explain the denoising process", "What is a noise schedule?"],
        "Fine-Tuning and RAG":        ["What is LoRA?", "How does RAG work?", "Explain fine-tuning vs RAG"],
    }.get(topic, ["Explain the basics", "Give me an example", "What are key concepts?"])
