"""
Topic Selection Page for Synapse AI Tutor.
Displays all available topics as interactive cards.
"""

import streamlit as st
from backend.progress_tracker import get_topic_progress


# Topic metadata with descriptions and colors
TOPICS = {
    "Neural Networks": {
        "icon": "NN",
        "description": "Foundations of deep learning -- perceptrons, activations, backpropagation",
        "color": "#6C63FF"
    },
    "CNNs": {
        "icon": "CN",
        "description": "Convolutional neural networks for image processing and computer vision",
        "color": "#00D2FF"
    },
    "RNNs": {
        "icon": "RN",
        "description": "Recurrent networks for sequential data -- LSTM, GRU, time series",
        "color": "#FF6B6B"
    },
    "Transformers": {
        "icon": "TF",
        "description": "Self-attention, multi-head attention, encoder-decoder architecture",
        "color": "#FFB347"
    },
    "LLMs": {
        "icon": "LM",
        "description": "Large language models -- GPT, pre-training, scaling laws, reasoning",
        "color": "#2ECC71"
    },
    "Prompt Engineering": {
        "icon": "PE",
        "description": "Crafting effective prompts -- few-shot, chain-of-thought, templates",
        "color": "#E74C3C"
    },
    "Generative AI Fundamentals": {
        "icon": "GA",
        "description": "Core concepts of generative models, latent spaces, and evaluation",
        "color": "#9B59B6"
    },
    "GANs": {
        "icon": "GN",
        "description": "Generative adversarial networks -- generators, discriminators, training",
        "color": "#1ABC9C"
    },
    "Diffusion Models": {
        "icon": "DM",
        "description": "Denoising diffusion -- forward process, reverse sampling, stable diffusion",
        "color": "#3498DB"
    },
    "Fine-Tuning and RAG": {
        "icon": "FR",
        "description": "LoRA, QLoRA, retrieval-augmented generation, domain adaptation",
        "color": "#F39C12"
    }
}


def render_topic_selection():
    """Render the topic selection page."""

    # Header
    st.markdown("""
    <div class="main-header animate-fade-in">
        <h1>Choose Your Topic</h1>
        <p>Select a topic to begin your personalized learning journey</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Topic grid -- 2 rows of 5
    topics_list = list(TOPICS.items())

    for row in range(2):
        cols = st.columns(5)
        for col_idx in range(5):
            topic_idx = row * 5 + col_idx
            if topic_idx < len(topics_list):
                topic_name, meta = topics_list[topic_idx]

                with cols[col_idx]:
                    # Get progress if available
                    progress = get_topic_progress(st.session_state.username, topic_name)
                    mastery = progress.get("mastery", 0)
                    level = progress.get("level", "Not Assessed")

                    # Level badge
                    if level == "Beginner":
                        badge_class = "badge-beginner"
                    elif level == "Intermediate":
                        badge_class = "badge-intermediate"
                    elif level == "Advanced":
                        badge_class = "badge-advanced"
                    else:
                        badge_class = ""

                    level_badge = ""
                    if level != "Not Assessed":
                        level_badge = f'<span class="badge {badge_class}">{level}</span>'

                    # Progress bar
                    progress_bar = ""
                    if mastery > 0:
                        progress_bar = f"""
                        <div style="margin-top: 0.6rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #A0A0C0; margin-bottom: 0.2rem;">
                                <span>Mastery</span>
                                <span>{mastery}%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.05); border-radius: 4px; height: 4px; overflow: hidden;">
                                <div style="background: {meta['color']}; width: {mastery}%; height: 100%; border-radius: 4px;
                                            transition: width 0.5s ease;"></div>
                            </div>
                        </div>
                        """

                    # Render card as HTML
                    st.markdown(f"""
                    <div class="topic-card" style="border-color: rgba({_hex_to_rgb(meta['color'])}, 0.15);">
                        <div class="topic-icon" style="background: linear-gradient(135deg, {meta['color']}, {meta['color']}88);
                                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                                    font-weight: 900; font-size: 1.5rem; letter-spacing: -1px;">{meta['icon']}</div>
                        <div class="topic-name">{topic_name}</div>
                        <div class="topic-desc">{meta['description']}</div>
                        <div style="margin-top: 0.5rem;">{level_badge}</div>
                        {progress_bar}
                    </div>
                    """, unsafe_allow_html=True)

                    # Button to select topic
                    if st.button(
                        f"Select",
                        key=f"select_{topic_name}",
                        use_container_width=True
                    ):
                        st.session_state.selected_topic = topic_name
                        st.session_state.assessment_questions = None
                        st.session_state.assessment_answers = []
                        st.session_state.assessment_complete = False
                        st.session_state.assessment_result = None
                        st.session_state.current_question_idx = 0
                        st.session_state.chat_history = []
                        st.session_state.tutor_response = None
                        st.session_state.current_page = "assessment"
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    # Info section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: rgba(108, 99, 255, 0.05);
                border-radius: 16px; border: 1px solid rgba(108, 99, 255, 0.1);">
        <p style="color: #A0A0C0; font-size: 0.9rem; margin: 0;">
            After selecting a topic, you'll take a quick <strong style="color: #8B83FF;">5-question assessment</strong>
            to determine your proficiency level. The AI tutor will then adapt its teaching style to match your needs.
        </p>
    </div>
    """, unsafe_allow_html=True)


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB string."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"{r}, {g}, {b}"
