"""
Assessment Page for Synapse AI Tutor.
Conducts topic-specific assessments with MCQs,
displays progress, and determines student level.
"""

import streamlit as st
from backend.assessment import (
    load_dataset, categorize_questions,
    select_assessment_questions, calculate_score
)
from backend.progress_tracker import update_assessment_score


def _ensure_question_bank():
    """Load and categorize questions if not already done."""
    if st.session_state.topic_banks is None:
        with st.spinner("Loading question bank..."):
            questions = load_dataset()
            st.session_state.topic_banks = categorize_questions(questions)


def _ensure_assessment_questions():
    """Generate assessment questions for the selected topic."""
    if st.session_state.assessment_questions is None:
        _ensure_question_bank()
        topic = st.session_state.selected_topic
        st.session_state.assessment_questions = select_assessment_questions(
            st.session_state.topic_banks, topic, num_questions=5
        )
        st.session_state.assessment_answers = [None] * len(st.session_state.assessment_questions)
        st.session_state.current_question_idx = 0
        st.session_state.assessment_complete = False


def render_assessment():
    """Render the assessment page."""

    # Check if topic is selected
    if not st.session_state.selected_topic:
        st.warning("Please select a topic first.")
        if st.button("Go to Topics"):
            st.session_state.current_page = "topic_selection"
            st.rerun()
        return

    topic = st.session_state.selected_topic

    # Header
    st.markdown(f"""
    <div class="main-header animate-fade-in">
        <h1>Assessment</h1>
        <p>Topic: <strong style="color: #00D2FF;">{topic}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Generate questions
    _ensure_assessment_questions()
    questions = st.session_state.assessment_questions

    if st.session_state.assessment_complete:
        _render_results(topic)
    else:
        _render_questions(questions, topic)


def _render_questions(questions, topic):
    """Render the assessment questions one at a time."""

    total = len(questions)
    current_idx = st.session_state.current_question_idx

    # Progress bar
    progress = (current_idx) / total
    st.progress(progress, text=f"Question {current_idx + 1} of {total}")

    st.markdown("<br>", unsafe_allow_html=True)

    if current_idx < total:
        q = questions[current_idx]

        # Question card
        st.markdown(f"""
        <div class="synapse-card animate-fade-in">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="background: linear-gradient(135deg, #6C63FF, #00D2FF);
                            border-radius: 50%; width: 40px; height: 40px;
                            display: flex; align-items: center; justify-content: center;
                            font-weight: 700; font-size: 1.1rem; color: white; margin-right: 1rem;
                            flex-shrink: 0;">
                    {current_idx + 1}
                </div>
                <div style="color: #FFFFFF; font-size: 1.05rem; font-weight: 500; line-height: 1.5;">
                    {q['question']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Answer options
        selected = st.radio(
            "Select your answer:",
            options=range(len(q["options"])),
            format_func=lambda x: q["options"][x],
            key=f"q_{current_idx}_{topic}",
            index=None,
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if current_idx > 0:
                if st.button("Previous", use_container_width=True):
                    st.session_state.current_question_idx -= 1
                    st.rerun()

        with col3:
            if current_idx < total - 1:
                if st.button("Next", use_container_width=True):
                    if selected is not None:
                        st.session_state.assessment_answers[current_idx] = selected
                    st.session_state.current_question_idx += 1
                    st.rerun()
            else:
                # Last question -- submit
                if st.button("Submit Assessment", use_container_width=True, type="primary"):
                    if selected is not None:
                        st.session_state.assessment_answers[current_idx] = selected

                    # Calculate results
                    result = calculate_score(
                        st.session_state.assessment_answers,
                        questions
                    )

                    # Save progress
                    update_assessment_score(
                        st.session_state.username,
                        topic,
                        result["score"],
                        result["level"]
                    )

                    st.session_state.assessment_result = result
                    st.session_state.assessment_complete = True
                    st.rerun()

    # Question indicators at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    indicator_cols = st.columns(total)
    for i in range(total):
        with indicator_cols[i]:
            if i == current_idx:
                color = "#6C63FF"
                border = "2px solid #6C63FF"
            elif st.session_state.assessment_answers[i] is not None:
                color = "rgba(46, 204, 113, 0.3)"
                border = "1px solid #2ECC71"
            else:
                color = "rgba(255, 255, 255, 0.05)"
                border = "1px solid rgba(255, 255, 255, 0.1)"

            st.markdown(f"""
            <div style="width: 100%; height: 6px; background: {color};
                        border-radius: 3px; border: {border};"></div>
            """, unsafe_allow_html=True)


def _render_results(topic):
    """Render the assessment results."""
    result = st.session_state.assessment_result

    if not result:
        return

    score = result["score"]
    level = result["level"]
    correct = result["correct"]
    total = result["total"]

    # Level color
    if level == "Beginner":
        level_color = "#2ECC71"
        level_message = "You're just getting started! The AI tutor will explain concepts from the ground up with simple language and analogies."
    elif level == "Intermediate":
        level_color = "#F39C12"
        level_message = "Good foundation! The tutor will build on your knowledge with technical examples and practical applications."
    else:
        level_color = "#8B83FF"
        level_message = "Excellent mastery! The tutor will engage you with advanced discussions, formal terminology, and cutting-edge insights."

    # Result display
    st.markdown(f"""
    <div class="synapse-card animate-fade-in" style="text-align: center; padding: 2.5rem;">
        <h2 style="color: #FFFFFF; margin-bottom: 0.5rem;">Assessment Complete!</h2>
        <p style="color: #A0A0C0; margin-bottom: 2rem;">Topic: <strong style="color: #00D2FF;">{topic}</strong></p>

        <div style="display: flex; justify-content: center; gap: 3rem; margin-bottom: 2rem;">
            <div>
                <div style="font-size: 3rem; font-weight: 800; color: {level_color};">{score}%</div>
                <div style="color: #A0A0C0; font-size: 0.85rem;">Score</div>
            </div>
            <div>
                <div style="font-size: 3rem; font-weight: 800; color: {level_color};">{correct}/{total}</div>
                <div style="color: #A0A0C0; font-size: 0.85rem;">Correct</div>
            </div>
        </div>

        <div style="display: inline-block; padding: 0.5rem 1.5rem; border-radius: 25px;
                    background: rgba({_hex_to_rgb_inline(level_color)}, 0.15);
                    border: 1px solid rgba({_hex_to_rgb_inline(level_color)}, 0.3);
                    color: {level_color}; font-weight: 700; font-size: 1.2rem;
                    letter-spacing: 1px;">
            {level}
        </div>

        <p style="color: #A0A0C0; margin-top: 1.5rem; font-size: 0.95rem; max-width: 500px; margin-left: auto; margin-right: auto;">
            {level_message}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Start Tutoring", use_container_width=True, type="primary"):
            st.session_state.current_page = "tutor"
            st.rerun()

    with col2:
        if st.button("Retake Assessment", use_container_width=True):
            st.session_state.assessment_questions = None
            st.session_state.assessment_answers = []
            st.session_state.assessment_complete = False
            st.session_state.assessment_result = None
            st.session_state.current_question_idx = 0
            st.rerun()

    with col3:
        if st.button("Choose Another Topic", use_container_width=True):
            st.session_state.current_page = "topic_selection"
            st.rerun()


def _hex_to_rgb_inline(hex_color: str) -> str:
    """Convert hex color to RGB string for inline CSS."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"{r}, {g}, {b}"
