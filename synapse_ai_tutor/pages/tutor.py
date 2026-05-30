"""
Tutor Page for Synapse AI Tutor.
Adaptive AI tutoring with full RAG source visibility,
persistent knowledge gap loading, fallback mode, and dynamic mastery updates.
"""

import streamlit as st
from backend.progress_tracker import (
    get_topic_progress, get_mastery_scores,
    update_knowledge_gaps, update_mastery_from_practice,
    update_session_access
)
from backend.gap_detector import detect_knowledge_gaps
from backend.llm_client import generate_tutoring_response, check_connection
from backend.resources import get_resources_for_level


def render_tutor():
    if not st.session_state.selected_topic:
        st.warning("Please select a topic first.")
        if st.button("Go to Topics"):
            st.session_state.page = "topic_selection"
            st.rerun()
        return

    topic = st.session_state.selected_topic
    username = st.session_state.username

    # Load persistent profile
    progress = get_topic_progress(username, topic)
    level = progress.get("level", "Beginner")
    mastery = progress.get("mastery", 0)
    if level == "Not Assessed":
        level = "Beginner"

    # Load & merge knowledge gaps
    saved_gaps = progress.get("knowledge_gaps", [])
    mastery_scores = get_mastery_scores(username)
    gap_analysis = detect_knowledge_gaps(topic, mastery_scores)
    dynamic_gaps = gap_analysis.get("gaps", [])
    all_gaps = list(dict.fromkeys(saved_gaps + dynamic_gaps))
    knowledge_gaps = all_gaps[:8]

    update_knowledge_gaps(username, topic, knowledge_gaps)
    update_session_access(username, topic)

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="animate-fade-in" style="margin-bottom:1rem;">
        <h1 class="gradient-text" style="font-size:2rem;margin-bottom:0.2rem;">AI Tutor</h1>
        <p style="color:#A0A0C0;font-size:0.9rem;">
            Adaptive companion for <strong style="color:#00D2FF;">{topic}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Info bar ──────────────────────────────────────────────────────────────
    icols = st.columns(4)
    lc = {"Beginner": "#2ECC71", "Intermediate": "#F39C12", "Advanced": "#8B83FF"}.get(level, "#A0A0C0")

    with icols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <div style="color:#A0A0C0;font-size:0.7rem;text-transform:uppercase;">Topic</div>
            <div style="color:#00D2FF;font-weight:700;font-size:0.88rem;margin-top:0.2rem;">{topic}</div>
        </div>""", unsafe_allow_html=True)

    with icols[1]:
        st.markdown(f"""
        <div class="stat-card">
            <div style="color:#A0A0C0;font-size:0.7rem;text-transform:uppercase;">Level</div>
            <div style="color:{lc};font-weight:700;font-size:0.88rem;margin-top:0.2rem;">{level}</div>
        </div>""", unsafe_allow_html=True)

    with icols[2]:
        st.markdown(f"""
        <div class="stat-card">
            <div style="color:#A0A0C0;font-size:0.7rem;text-transform:uppercase;">Mastery</div>
            <div style="color:#FFFFFF;font-weight:700;font-size:0.88rem;margin-top:0.2rem;">{mastery}%</div>
        </div>""", unsafe_allow_html=True)

    with icols[3]:
        try:
            connected = check_connection()
        except Exception:
            connected = False
        llm_color = "#2ECC71" if connected else "#E74C3C"
        llm_label = "Online" if connected else "Offline (Fallback)"
        st.markdown(f"""
        <div class="stat-card">
            <div style="color:#A0A0C0;font-size:0.7rem;text-transform:uppercase;">LLM</div>
            <div style="color:{llm_color};font-weight:700;font-size:0.88rem;margin-top:0.2rem;">{llm_label}</div>
        </div>""", unsafe_allow_html=True)

    # ── Knowledge Gaps ────────────────────────────────────────────────────────
    if knowledge_gaps:
        gap_str = " &nbsp;|&nbsp; ".join([
            f"<span style='color:#F39C12;'>{g}</span>" for g in knowledge_gaps[:5]
        ])
        st.markdown(f"""
        <div class="gap-warning" style="margin-top:0.8rem;">
            <div style="color:#F39C12;font-weight:600;font-size:0.88rem;margin-bottom:0.3rem;">
                Knowledge Gaps (loaded from your profile)
            </div>
            <div style="font-size:0.82rem;">{gap_str}</div>
            <div style="color:#6B6B8D;font-size:0.75rem;margin-top:0.3rem;">
                {gap_analysis.get('recommendation', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Multi-topic switcher ───────────────────────────────────────────────────
    selected_topics = st.session_state.get("selected_topics", [])
    if len(selected_topics) > 1:
        other_topics = [t for t in selected_topics if t != topic]
        with st.expander(f"Switch Topic (studying {len(selected_topics)} topics)"):
            scols = st.columns(min(len(other_topics), 4))
            for i, t in enumerate(other_topics[:4]):
                with scols[i]:
                    if st.button(t[:18], key=f"switch_{t}", use_container_width=True):
                        st.session_state.selected_topic = t
                        st.session_state.page = "tutor"
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chat Interface (full width) ───────────────────────────────────────────
    _render_chat(topic, level, mastery, knowledge_gaps, username)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Resources + Key Concepts (below chat, centered) ───────────────────────
    _render_resources_section(topic, level, knowledge_gaps, gap_analysis)

    # ── Practice Tracker ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    _render_practice_tracker(topic, username)


def _render_chat(topic, level, mastery, knowledge_gaps, username):
    st.markdown("""
    <div style="font-weight:600;color:#FFFFFF;font-size:0.95rem;margin-bottom:0.8rem;">
        Chat with Synapse
    </div>
    """, unsafe_allow_html=True)

    # Per-topic chat history
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = {}
    if topic not in st.session_state.chat_histories:
        st.session_state.chat_histories[topic] = []

    chat_history = st.session_state.chat_histories[topic]

    # Display existing messages
    for msg in chat_history:
        role = msg["role"]
        # Use only valid Streamlit avatar values
        avatar = "user" if role == "user" else "assistant"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["content"])

            # Show sources for assistant messages
            if role == "assistant" and msg.get("sources"):
                sources = msg["sources"]
                with st.expander(f"Sources ({len(sources)} textbook passages retrieved)", expanded=False):
                    for src in sources:
                        st.markdown(f"""
                        <div class="source-citation">
                            <div>
                                <span class="source-book">{src['source']}</span>
                                <span class="source-page"> — Page {src['page']}</span>
                            </div>
                            <div style="color:#6B6B8D;font-size:0.75rem;margin-top:0.3rem;line-height:1.4;font-style:italic;">
                                {src['text'][:280]}...
                            </div>
                        </div>""", unsafe_allow_html=True)

    # Chat input
    user_q = st.chat_input(f"Ask about {topic}...", key="tutor_input")

    if user_q:
        # Add user message
        chat_history.append({"role": "user", "content": user_q, "sources": []})
        st.session_state.chat_histories[topic] = chat_history

        with st.chat_message("user", avatar="user"):
            st.markdown(user_q)

        with st.chat_message("assistant", avatar="assistant"):
            with st.spinner("Thinking..."):
                # RAG retrieval
                retrieved = []
                if st.session_state.get("rag_initialized", False):
                    try:
                        rag = st.session_state.rag_pipeline
                        retrieved = rag.search_for_topic(topic, user_q, k=5)
                    except Exception:
                        retrieved = []

                # LLM call
                response = generate_tutoring_response(
                    topic=topic,
                    level=level,
                    knowledge_gaps=knowledge_gaps,
                    retrieved_chunks=retrieved,
                    student_question=user_q,
                    mastery=mastery,
                    model=None
                )

            full_text = response.get("full_response", response.get("explanation", ""))
            sources = response.get("sources", [])
            fallback = response.get("fallback_used", False)

            # Fallback banner
            if fallback:
                st.markdown("""
                <div class="fallback-warning">
                    <strong style="color:#E74C3C;">LLM Offline</strong>
                    <span style="color:#A0A0C0;font-size:0.85rem;"> — Showing textbook content.
                    AI explanations resume when the model server is back online.</span>
                </div>""", unsafe_allow_html=True)

            st.markdown(full_text)

            # Always show sources expanded for new responses
            if sources:
                with st.expander(f"Sources ({len(sources)} textbook passages retrieved)", expanded=True):
                    for src in sources:
                        st.markdown(f"""
                        <div class="source-citation">
                            <div>
                                <span class="source-book">{src['source']}</span>
                                <span class="source-page"> — Page {src['page']}</span>
                            </div>
                            <div style="color:#6B6B8D;font-size:0.78rem;margin-top:0.4rem;line-height:1.4;font-style:italic;">
                                {src['text'][:300]}...
                            </div>
                        </div>""", unsafe_allow_html=True)
            elif not st.session_state.get("rag_initialized", False):
                st.caption("RAG pipeline initializing — textbook sources unavailable.")

            # Save to history
            chat_history.append({
                "role": "assistant",
                "content": full_text,
                "sources": sources
            })
            st.session_state.chat_histories[topic] = chat_history

    # Suggestion buttons (only when empty)
    if not chat_history:
        st.markdown("""
        <div style="color:#6B6B8D;font-size:0.82rem;text-align:center;margin:1rem 0 0.5rem;">
            Try asking one of these:
        </div>""", unsafe_allow_html=True)
        suggestions = _get_suggestions(topic)
        scols = st.columns(len(suggestions))
        for i, (col, sug) in enumerate(zip(scols, suggestions)):
            with col:
                if st.button(sug, key=f"sug_{i}", use_container_width=True):
                    st.session_state.chat_histories[topic].append({
                        "role": "user", "content": sug, "sources": []
                    })
                    st.rerun()


def _render_resources_section(topic, level, knowledge_gaps, gap_analysis):
    """Render resources and key concepts in a centered, multi-column layout."""
    resources = get_resources_for_level(topic, level)
    key_concepts = gap_analysis.get("key_concepts", [])

    st.markdown("""
    <div style="text-align:center;margin-bottom:1.2rem;">
        <span style="font-weight:700;color:#FFFFFF;font-size:1.1rem;">Learning Resources</span>
        <p style="color:#A0A0C0;font-size:0.82rem;margin-top:0.3rem;">
            Curated content for your level — click to open
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 4-column layout: Key Concepts | Videos | Articles | Docs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div style="font-weight:600;color:#8B83FF;font-size:0.85rem;margin-bottom:0.6rem;
                    padding-bottom:0.3rem;border-bottom:2px solid rgba(139,131,255,0.3);">
            Key Concepts
        </div>""", unsafe_allow_html=True)
        if key_concepts:
            for concept in key_concepts:
                st.markdown(f"""
                <div style="padding:0.35rem 0.7rem;margin-bottom:0.25rem;
                            background:rgba(108,99,255,0.06);border-radius:6px;
                            border-left:3px solid #6C63FF;color:#A0A0C0;font-size:0.78rem;
                            line-height:1.3;">
                    {concept}
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#6B6B8D;font-size:0.78rem;'>No concepts listed.</div>",
                        unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="font-weight:600;color:#00D2FF;font-size:0.85rem;margin-bottom:0.6rem;
                    padding-bottom:0.3rem;border-bottom:2px solid rgba(0,210,255,0.3);">
            Videos
        </div>""", unsafe_allow_html=True)
        videos = resources.get("videos", [])
        if videos:
            for vid in videos[:3]:
                st.markdown(f"""
                <div style="padding:0.5rem 0.7rem;margin-bottom:0.35rem;
                            background:rgba(0,210,255,0.05);border-radius:8px;
                            border:1px solid rgba(0,210,255,0.12);">
                    <a href="{vid['url']}" target="_blank"
                       style="color:#00D2FF;font-size:0.78rem;text-decoration:none;font-weight:500;line-height:1.3;display:block;">
                        {vid['title'][:45]}{'...' if len(vid['title'])>45 else ''}
                    </a>
                    <div style="color:#6B6B8D;font-size:0.68rem;margin-top:0.2rem;">{vid['description'][:60]}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#6B6B8D;font-size:0.78rem;'>No videos available.</div>",
                        unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="font-weight:600;color:#FF6B6B;font-size:0.85rem;margin-bottom:0.6rem;
                    padding-bottom:0.3rem;border-bottom:2px solid rgba(255,107,107,0.3);">
            Articles
        </div>""", unsafe_allow_html=True)
        articles = resources.get("articles", [])
        if articles:
            for art in articles[:3]:
                st.markdown(f"""
                <div style="padding:0.5rem 0.7rem;margin-bottom:0.35rem;
                            background:rgba(255,107,107,0.05);border-radius:8px;
                            border:1px solid rgba(255,107,107,0.12);">
                    <a href="{art['url']}" target="_blank"
                       style="color:#FF6B6B;font-size:0.78rem;text-decoration:none;font-weight:500;line-height:1.3;display:block;">
                        {art['title'][:45]}{'...' if len(art['title'])>45 else ''}
                    </a>
                    <div style="color:#6B6B8D;font-size:0.68rem;margin-top:0.2rem;">{art['description'][:60]}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#6B6B8D;font-size:0.78rem;'>No articles available.</div>",
                        unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style="font-weight:600;color:#2ECC71;font-size:0.85rem;margin-bottom:0.6rem;
                    padding-bottom:0.3rem;border-bottom:2px solid rgba(46,204,113,0.3);">
            Documentation
        </div>""", unsafe_allow_html=True)
        docs = resources.get("documentation", [])
        if docs:
            for doc in docs[:3]:
                st.markdown(f"""
                <div style="padding:0.5rem 0.7rem;margin-bottom:0.35rem;
                            background:rgba(46,204,113,0.05);border-radius:8px;
                            border:1px solid rgba(46,204,113,0.12);">
                    <a href="{doc['url']}" target="_blank"
                       style="color:#2ECC71;font-size:0.78rem;text-decoration:none;font-weight:500;line-height:1.3;display:block;">
                        {doc['title'][:45]}{'...' if len(doc['title'])>45 else ''}
                    </a>
                    <div style="color:#6B6B8D;font-size:0.68rem;margin-top:0.2rem;">{doc['description'][:60]}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#6B6B8D;font-size:0.78rem;'>No docs available.</div>",
                        unsafe_allow_html=True)

    if resources.get("priority_note"):
        st.markdown(f"""
        <div style="text-align:center;color:#6B6B8D;font-size:0.75rem;margin-top:0.5rem;">
            {resources['priority_note']}
        </div>""", unsafe_allow_html=True)


def _render_practice_tracker(topic, username):
    """Allow user to log practice performance to dynamically update mastery."""
    with st.expander("Log Practice Performance (updates your mastery score)", expanded=False):
        st.markdown("""
        <div style="color:#A0A0C0;font-size:0.82rem;margin-bottom:0.8rem;">
            After answering the practice questions from Synapse, log your score here to update your mastery.
        </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            correct = st.number_input("Correct", min_value=0, max_value=20,
                                      value=0, step=1, key="prac_correct")
        with col2:
            total = st.number_input("Total", min_value=1, max_value=20,
                                    value=3, step=1, key="prac_total")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Update Mastery", use_container_width=True):
                update_mastery_from_practice(username, topic, correct, total)
                st.success(f"Mastery updated! Answered {correct}/{total} correctly.")
                st.rerun()


def _get_suggestions(topic: str) -> list:
    return {
        "Neural Networks":            ["What is backpropagation?", "Explain activation functions", "How do neurons learn?"],
        "CNNs":                       ["How do convolutions work?", "What is pooling?", "Explain feature maps"],
        "RNNs":                       ["What is vanishing gradient?", "How does LSTM work?", "Explain sequence modeling"],
        "Transformers":               ["Explain self-attention", "What is multi-head attention?", "How does positional encoding work?"],
        "LLMs":                       ["How do LLMs generate text?", "What are scaling laws?", "Explain tokenization"],
        "Prompt Engineering":         ["What is chain-of-thought?", "How to write system prompts?", "Explain few-shot prompting"],
        "Generative AI Fundamentals": ["What is generative AI?", "Explain latent space", "How are gen models trained?"],
        "GANs":                       ["How do GANs work?", "What is mode collapse?", "Explain adversarial training"],
        "Diffusion Models":           ["How does stable diffusion work?", "Explain the denoising process", "What is a noise schedule?"],
        "Fine-Tuning and RAG":        ["What is LoRA?", "How does RAG work?", "Explain fine-tuning vs RAG"],
    }.get(topic, ["Explain the basics", "Give me an example", "What are key concepts?"])
