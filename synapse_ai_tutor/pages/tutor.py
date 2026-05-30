"""
Tutor Page for Synapse AI Tutor.
The main AI tutoring interface with chat, RAG retrieval,
adaptive explanations, and resource recommendations.
"""

import streamlit as st
from backend.progress_tracker import get_topic_progress, get_mastery_scores, update_weak_areas
from backend.gap_detector import detect_knowledge_gaps
from backend.llm_client import generate_tutoring_response, check_connection, get_available_models
from backend.resources import get_resources_for_level


def render_tutor():
    """Render the tutor page."""

    # Check prerequisites
    if not st.session_state.selected_topic:
        st.warning("Please select a topic first.")
        if st.button("Go to Topics"):
            st.session_state.current_page = "topic_selection"
            st.rerun()
        return

    topic = st.session_state.selected_topic
    username = st.session_state.username

    # Get student profile
    progress = get_topic_progress(username, topic)
    level = progress.get("level", "Beginner")
    mastery = progress.get("mastery", 0)

    if level == "Not Assessed":
        level = "Beginner"

    # Detect knowledge gaps
    mastery_scores = get_mastery_scores(username)
    gap_analysis = detect_knowledge_gaps(topic, mastery_scores)
    knowledge_gaps = gap_analysis.get("gaps", [])

    # Update weak areas in progress
    update_weak_areas(username, topic, knowledge_gaps)

    # Header
    st.markdown(f"""
    <div class="animate-fade-in" style="margin-bottom: 1rem;">
        <h1 class="gradient-text" style="font-size: 2rem; margin-bottom: 0.3rem;">AI Tutor</h1>
        <p style="color: #A0A0C0; font-size: 0.95rem;">Your adaptive learning companion for <strong style="color: #00D2FF;">{topic}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Top info bar
    info_cols = st.columns(4)

    with info_cols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <div style="color: #A0A0C0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">Topic</div>
            <div style="color: #00D2FF; font-weight: 700; font-size: 0.95rem; margin-top: 0.3rem;">{topic}</div>
        </div>
        """, unsafe_allow_html=True)

    with info_cols[1]:
        level_color = {"Beginner": "#2ECC71", "Intermediate": "#F39C12", "Advanced": "#8B83FF"}.get(level, "#A0A0C0")
        st.markdown(f"""
        <div class="stat-card">
            <div style="color: #A0A0C0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">Level</div>
            <div style="color: {level_color}; font-weight: 700; font-size: 0.95rem; margin-top: 0.3rem;">{level}</div>
        </div>
        """, unsafe_allow_html=True)

    with info_cols[2]:
        st.markdown(f"""
        <div class="stat-card">
            <div style="color: #A0A0C0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">Mastery</div>
            <div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem; margin-top: 0.3rem;">{mastery}%</div>
        </div>
        """, unsafe_allow_html=True)

    with info_cols[3]:
        try:
            is_connected = check_connection()
        except Exception:
            is_connected = False
        llm_status = "Connected" if is_connected else "Offline"
        llm_color = "#2ECC71" if is_connected else "#E74C3C"
        st.markdown(f"""
        <div class="stat-card">
            <div style="color: #A0A0C0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">LLM Status</div>
            <div style="color: {llm_color}; font-weight: 700; font-size: 0.95rem; margin-top: 0.3rem;">{llm_status}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Knowledge Gaps warning
    if knowledge_gaps:
        gaps_display = " | ".join([f"* {gap}" for gap in knowledge_gaps[:5]])
        st.markdown(f"""
        <div class="gap-warning">
            <div class="gap-icon" style="margin-bottom: 0.5rem; font-size: 0.95rem; font-weight: 600;">
                Knowledge Gaps Detected
            </div>
            <div style="color: #A0A0C0; font-size: 0.85rem;">
                {gaps_display}
            </div>
            <div style="color: #6B6B8D; font-size: 0.8rem; margin-top: 0.5rem;">
                {gap_analysis.get('recommendation', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Main content area — two columns
    chat_col, info_col = st.columns([3, 1])

    with chat_col:
        _render_chat_interface(topic, level, knowledge_gaps)

    with info_col:
        _render_info_panel(topic, level, knowledge_gaps, gap_analysis)


def _render_chat_interface(topic, level, knowledge_gaps):
    """Render the chat/tutoring interface."""

    st.markdown("""
    <div style="font-weight: 600; color: #FFFFFF; font-size: 1rem; margin-bottom: 0.8rem;">
        Ask a Question
    </div>
    """, unsafe_allow_html=True)

    # Display chat history
    for msg in st.session_state.chat_history:
        role = msg["role"]
        avatar = "S" if role == "user" else "T"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["content"])

    # Chat input
    user_question = st.chat_input(f"Ask about {topic}...", key="tutor_chat_input")

    if user_question:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user", avatar="S"):
            st.markdown(user_question)

        # Generate response
        with st.chat_message("assistant", avatar="T"):
            with st.spinner("Thinking..."):
                # Retrieve relevant content
                retrieved_chunks = []
                if st.session_state.rag_initialized:
                    rag = st.session_state.rag_pipeline
                    retrieved_chunks = rag.search_for_topic(topic, user_question, k=5)

                # Check available models
                try:
                    available_models = get_available_models()
                except Exception:
                    available_models = []
                model = available_models[0] if available_models else None

                # Generate tutoring response
                response = generate_tutoring_response(
                    topic=topic,
                    level=level,
                    knowledge_gaps=knowledge_gaps,
                    retrieved_chunks=retrieved_chunks,
                    student_question=user_question,
                    model=model
                )

                st.session_state.tutor_response = response

                # Display the response
                full_response = response.get("full_response", response.get("explanation", ""))
                st.markdown(full_response)

                # Show sources
                sources = response.get("sources", [])
                if sources:
                    with st.expander("Sources Used", expanded=False):
                        for src in sources:
                            st.markdown(f"""
                            <div class="source-citation">
                                <span class="source-book">{src['source']}</span>
                                <span class="source-page"> -- Page {src['page']}</span>
                                <div style="color: #6B6B8D; font-size: 0.8rem; margin-top: 0.3rem;">
                                    {src['text'][:150]}...
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

        # Add assistant response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": full_response
        })

    # Initial prompt suggestions if no chat history
    if not st.session_state.chat_history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #6B6B8D; font-size: 0.85rem; text-align: center; margin-bottom: 1rem;">
            Try asking one of these:
        </div>
        """, unsafe_allow_html=True)

        suggestions = _get_suggestions(st.session_state.selected_topic)
        suggestion_cols = st.columns(len(suggestions))

        for i, (col, suggestion) in enumerate(zip(suggestion_cols, suggestions)):
            with col:
                if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": suggestion
                    })
                    st.rerun()


def _render_info_panel(topic, level, knowledge_gaps, gap_analysis):
    """Render the information panel."""

    # Key concepts
    key_concepts = gap_analysis.get("key_concepts", [])
    if key_concepts:
        st.markdown("""
        <div style="font-weight: 600; color: #FFFFFF; font-size: 0.95rem; margin-bottom: 0.8rem;">
            Key Concepts
        </div>
        """, unsafe_allow_html=True)

        for concept in key_concepts:
            st.markdown(f"""
            <div style="padding: 0.4rem 0.8rem; margin-bottom: 0.3rem; background: rgba(108, 99, 255, 0.06);
                        border-radius: 8px; border-left: 3px solid #6C63FF;
                        color: #A0A0C0; font-size: 0.82rem;">
                {concept}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # Recommended Resources
    resources = get_resources_for_level(topic, level)

    st.markdown("""
    <div style="font-weight: 600; color: #FFFFFF; font-size: 0.95rem; margin-bottom: 0.8rem;">
        Recommended Resources
    </div>
    """, unsafe_allow_html=True)

    if resources.get("priority_note"):
        st.markdown(f"""
        <div style="color: #6B6B8D; font-size: 0.8rem; margin-bottom: 0.8rem;">
            {resources['priority_note']}
        </div>
        """, unsafe_allow_html=True)

    # Videos
    if resources.get("videos"):
        st.markdown("**Videos**")
        for vid in resources["videos"][:2]:
            st.markdown(f"""
            <div style="padding: 0.5rem 0.7rem; margin-bottom: 0.3rem; background: rgba(0, 210, 255, 0.05);
                        border-radius: 8px; border: 1px solid rgba(0, 210, 255, 0.1);">
                <a href="{vid['url']}" target="_blank" style="color: #00D2FF; font-size: 0.82rem; text-decoration: none; font-weight: 500;">
                    {vid['title']}
                </a>
                <div style="color: #6B6B8D; font-size: 0.72rem; margin-top: 0.2rem;">{vid['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Articles
    if resources.get("articles"):
        st.markdown("**Articles**")
        for art in resources["articles"][:2]:
            st.markdown(f"""
            <div style="padding: 0.5rem 0.7rem; margin-bottom: 0.3rem; background: rgba(255, 107, 107, 0.05);
                        border-radius: 8px; border: 1px solid rgba(255, 107, 107, 0.1);">
                <a href="{art['url']}" target="_blank" style="color: #FF6B6B; font-size: 0.82rem; text-decoration: none; font-weight: 500;">
                    {art['title']}
                </a>
                <div style="color: #6B6B8D; font-size: 0.72rem; margin-top: 0.2rem;">{art['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Documentation
    if resources.get("documentation"):
        st.markdown("**Documentation**")
        for doc in resources["documentation"][:2]:
            st.markdown(f"""
            <div style="padding: 0.5rem 0.7rem; margin-bottom: 0.3rem; background: rgba(46, 204, 113, 0.05);
                        border-radius: 8px; border: 1px solid rgba(46, 204, 113, 0.1);">
                <a href="{doc['url']}" target="_blank" style="color: #2ECC71; font-size: 0.82rem; text-decoration: none; font-weight: 500;">
                    {doc['title']}
                </a>
                <div style="color: #6B6B8D; font-size: 0.72rem; margin-top: 0.2rem;">{doc['description']}</div>
            </div>
            """, unsafe_allow_html=True)


def _get_suggestions(topic: str) -> list:
    """Get suggested questions for a topic."""
    suggestions_map = {
        "Neural Networks": [
            "What is backpropagation?",
            "Explain activation functions",
            "How do neurons learn?"
        ],
        "CNNs": [
            "How do convolutions work?",
            "What is pooling?",
            "Explain feature maps"
        ],
        "RNNs": [
            "What is vanishing gradient?",
            "How does LSTM work?",
            "Explain sequence modeling"
        ],
        "Transformers": [
            "Explain self-attention",
            "What is multi-head attention?",
            "How does positional encoding work?"
        ],
        "LLMs": [
            "How do LLMs generate text?",
            "What are scaling laws?",
            "Explain tokenization"
        ],
        "Prompt Engineering": [
            "What is chain-of-thought?",
            "How to write system prompts?",
            "Explain few-shot prompting"
        ],
        "Generative AI Fundamentals": [
            "What is generative AI?",
            "Explain latent space",
            "How are gen AI models trained?"
        ],
        "GANs": [
            "How do GANs work?",
            "What is mode collapse?",
            "Explain adversarial training"
        ],
        "Diffusion Models": [
            "How does stable diffusion work?",
            "Explain the denoising process",
            "What is a noise schedule?"
        ],
        "Fine-Tuning and RAG": [
            "What is LoRA?",
            "How does RAG work?",
            "Explain fine-tuning vs RAG"
        ]
    }
    return suggestions_map.get(topic, ["Explain the basics", "Give me an example", "What are key concepts?"])
