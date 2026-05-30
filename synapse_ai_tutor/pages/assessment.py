"""
Assessment Page for Synapse AI Tutor.
15-question format: 5 Easy (1pt) + 5 Intermediate (2pt) + 5 Hard (3pt).
Max score = 30. Supports reuse and multi-topic queue.
"""

import streamlit as st
from backend.assessment import (
    load_dataset, categorize_questions,
    select_assessment_questions, calculate_score,
)
from backend.progress_tracker import (
    update_assessment_score, get_topic_progress,
    topic_is_assessed, update_knowledge_gaps,
)

DIFF_COLORS  = {"easy": "#2ECC71", "intermediate": "#F39C12", "hard": "#8B83FF"}
DIFF_LABELS  = {"easy": "Easy (1 pt)", "intermediate": "Intermediate (2 pts)", "hard": "Hard (3 pts)"}
LEVEL_COLORS = {"Beginner": "#2ECC71", "Intermediate": "#F39C12", "Advanced": "#8B83FF"}


def _hex_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


def _go(page: str):
    st.session_state.page = page
    st.rerun()


def _ensure_question_bank():
    if st.session_state.get("topic_banks") is None:
        with st.spinner("Loading question bank..."):
            questions = load_dataset()
            st.session_state.topic_banks = categorize_questions(questions)


def _ensure_assessment_questions(topic):
    if st.session_state.get("assessment_questions") is None:
        _ensure_question_bank()
        qs = select_assessment_questions(st.session_state.topic_banks, topic)
        st.session_state.assessment_questions  = qs
        st.session_state.assessment_answers    = [None] * len(qs)
        st.session_state.current_question_idx  = 0
        st.session_state.assessment_complete   = False


# ---------------------------------------------------------------------------
def render_assessment():
    selected_topic = st.session_state.get("selected_topic")
    if not selected_topic:
        st.warning("No topic selected. Please choose a topic first.")
        if st.button("Go to Topics", key="ass_notopic"):
            _go("Topics")
        return

    topic    = selected_topic
    username = st.session_state.username

    # Reuse gate
    if (
        topic_is_assessed(username, topic)
        and st.session_state.get("assessment_questions") is None
        and not st.session_state.get("assessment_complete", False)
    ):
        _render_existing_profile(topic, username)
        return

    st.markdown(
        f"""
<div class="main-header fade-in">
    <h1>Assessment</h1>
    <p>Topic: <strong style="color:#00D2FF;">{topic}</strong></p>
</div>
""",
        unsafe_allow_html=True,
    )

    queue = st.session_state.get("topic_queue", [])
    q_idx = st.session_state.get("topic_queue_idx", 0)
    if len(queue) > 1:
        st.markdown(
            f'<div style="text-align:right;color:#6B6B8D;font-size:0.78rem;margin-bottom:0.4rem;">'
            f'Topic {q_idx+1} of {len(queue)}: assessing <strong style="color:#00D2FF;">{topic}</strong>'
            f"</div>",
            unsafe_allow_html=True,
        )

    _ensure_assessment_questions(topic)
    questions = st.session_state.assessment_questions

    if st.session_state.get("assessment_complete", False):
        _render_results(topic, username)
    else:
        _render_questions(questions, topic)


# ---------------------------------------------------------------------------
def _render_existing_profile(topic, username):
    progress  = get_topic_progress(username, topic)
    mastery   = progress.get("mastery", 0)
    level     = progress.get("level", "Not Assessed")
    score     = progress.get("score", 0)
    max_score = progress.get("max_score", 30)
    gaps      = progress.get("knowledge_gaps", [])
    history   = progress.get("assessment_history", [])
    lc        = LEVEL_COLORS.get(level, "#A0A0C0")

    st.markdown(
        f"""
<div class="main-header fade-in">
    <h1>Assessment</h1>
    <p>Topic: <strong style="color:#00D2FF;">{topic}</strong></p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="synapse-card" style="text-align:center;padding:1.8rem;">
    <div style="color:#A0A0C0;font-size:0.82rem;margin-bottom:0.8rem;">Previous Assessment Result</div>
    <div style="display:flex;justify-content:center;gap:3rem;margin-bottom:1.2rem;">
        <div>
            <div style="font-size:2.2rem;font-weight:800;color:{lc};">{score}/{max_score}</div>
            <div style="color:#A0A0C0;font-size:0.76rem;">Score</div>
        </div>
        <div>
            <div style="font-size:2.2rem;font-weight:800;color:{lc};">{mastery}%</div>
            <div style="color:#A0A0C0;font-size:0.76rem;">Mastery</div>
        </div>
    </div>
    <div style="display:inline-block;padding:0.35rem 1.1rem;border-radius:20px;
                background:rgba({_hex_rgb(lc)},0.14);border:1px solid rgba({_hex_rgb(lc)},0.3);
                color:{lc};font-weight:700;font-size:0.95rem;">{level}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if gaps:
        st.markdown(
            '<div class="gap-warning"><div style="color:#F39C12;font-weight:600;margin-bottom:0.3rem;">Knowledge Gaps</div>',
            unsafe_allow_html=True,
        )
        for g in gaps[:6]:
            st.markdown(
                f"<div style='color:#A0A0C0;font-size:0.82rem;margin:0.1rem 0;'>* {g}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("No knowledge gaps detected for this topic.")

    if history:
        with st.expander(f"Assessment History ({len(history)} attempts)"):
            for i, h in enumerate(reversed(history[-5:]), 1):
                date_str = h.get("date", "")[:10]
                st.markdown(
                    f"""
<div style="display:flex;justify-content:space-between;padding:0.28rem 0.5rem;
            background:rgba(255,255,255,0.02);border-radius:6px;margin-bottom:0.15rem;">
    <span style="color:#A0A0C0;font-size:0.78rem;">Attempt {len(history)-i+1} ({date_str})</span>
    <span style="color:#FFFFFF;font-size:0.78rem;font-weight:600;">
        {h.get("score",0)}/{h.get("max_score",30)} — {h.get("level","")}
    </span>
</div>
""",
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Continue Learning", use_container_width=True, type="primary", key="ep_cont"):
            if topic not in st.session_state.chat_histories:
                st.session_state.chat_histories[topic] = []
            _go("Tutor")
    with c2:
        if st.button("Retake Assessment", use_container_width=True, key="ep_retake"):
            st.session_state.assessment_questions = None
            st.session_state.assessment_answers   = []
            st.session_state.assessment_complete  = False
            st.session_state.assessment_result    = None
            st.session_state.current_question_idx = 0
            st.rerun()
    with c3:
        if st.button("Choose Topics", use_container_width=True, key="ep_topics"):
            _go("Topics")


# ---------------------------------------------------------------------------
def _render_questions(questions, topic):
    total       = len(questions)
    current_idx = st.session_state.get("current_question_idx", 0)

    if current_idx < 5:
        diff, section_num = "easy", 1
    elif current_idx < 10:
        diff, section_num = "intermediate", 2
    else:
        diff, section_num = "hard", 3

    diff_color = DIFF_COLORS[diff]
    diff_label = DIFF_LABELS[diff]

    st.progress(current_idx / total, text=f"Question {current_idx+1} of {total}")

    st.markdown(
        f"""
<div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:0.8rem;margin-top:0.4rem;">
    <div style="padding:0.25rem 0.8rem;border-radius:20px;
                background:rgba({_hex_rgb(diff_color)},0.1);
                border:1px solid rgba({_hex_rgb(diff_color)},0.3);
                color:{diff_color};font-weight:600;font-size:0.76rem;">
        Section {section_num}/3 — {diff_label}
    </div>
    <div style="color:#6B6B8D;font-size:0.74rem;">Max score: 30 pts</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if current_idx < total:
        q   = questions[current_idx]
        pts = q.get("points", 1)

        st.markdown(
            f"""
<div class="synapse-card fade-in">
    <div style="display:flex;align-items:flex-start;gap:0.9rem;">
        <div style="background:linear-gradient(135deg,{diff_color},{diff_color}88);
                    border-radius:50%;width:36px;height:36px;display:flex;align-items:center;
                    justify-content:center;font-weight:700;color:white;flex-shrink:0;font-size:0.95rem;">
            {current_idx+1}
        </div>
        <div>
            <div style="color:#FFFFFF;font-size:0.95rem;font-weight:500;line-height:1.5;">
                {q["question"]}
            </div>
            <div style="color:{diff_color};font-size:0.7rem;margin-top:0.25rem;">
                {pts} point{"s" if pts > 1 else ""}
            </div>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        selected = st.radio(
            "Select your answer:",
            options=range(len(q["options"])),
            format_func=lambda x: q["options"][x],
            key=f"q_{current_idx}_{topic}",
            index=None,
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        bc1, _, bc3 = st.columns([1, 2, 1])

        with bc1:
            if current_idx > 0:
                if st.button("Previous", use_container_width=True, key="q_prev"):
                    st.session_state.current_question_idx -= 1
                    st.rerun()

        with bc3:
            if current_idx < total - 1:
                if st.button("Next", use_container_width=True, key="q_next"):
                    if selected is not None:
                        st.session_state.assessment_answers[current_idx] = selected
                    st.session_state.current_question_idx += 1
                    st.rerun()
            else:
                if st.button("Submit Assessment", use_container_width=True, type="primary", key="q_submit"):
                    if selected is not None:
                        st.session_state.assessment_answers[current_idx] = selected
                    _submit_assessment(questions, topic)

    # Question dot indicators
    st.markdown("<br>", unsafe_allow_html=True)
    ind_cols = st.columns(total)
    for i in range(total):
        with ind_cols[i]:
            if i == current_idx:
                c = DIFF_COLORS["easy" if i < 5 else "intermediate" if i < 10 else "hard"]
                brd = "2px solid"
            elif st.session_state.assessment_answers[i] is not None:
                c, brd = "rgba(46,204,113,0.4)", "1px solid #2ECC71"
            else:
                c, brd = "rgba(255,255,255,0.05)", "1px solid rgba(255,255,255,0.1)"
            st.markdown(
                f'<div style="width:100%;height:5px;background:{c};border-radius:3px;border:{brd};"></div>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
def _submit_assessment(questions, topic):
    username = st.session_state.username
    answers  = st.session_state.assessment_answers
    result   = calculate_score(answers, questions)
    gaps     = _compute_gaps(answers, questions, topic)

    update_assessment_score(
        username=username,
        topic=topic,
        score=result["score"],
        max_score=result["max_score"],
        level=result["level"],
        knowledge_gaps=gaps,
    )

    result["knowledge_gaps"] = gaps
    st.session_state.assessment_result   = result
    st.session_state.assessment_complete = True
    st.rerun()


def _compute_gaps(answers, questions, topic) -> list:
    from backend.gap_detector import PREREQUISITE_MAP
    prereqs      = PREREQUISITE_MAP.get(topic, {}).get("prerequisites", [])
    key_concepts = PREREQUISITE_MAP.get(topic, {}).get("key_concepts", [])

    incorrect_diffs = []
    for i, q in enumerate(questions):
        if i >= len(answers) or answers[i] is None or answers[i] != q["correct_index"]:
            incorrect_diffs.append(q.get("difficulty", "intermediate"))

    hard_wrong  = incorrect_diffs.count("hard")
    inter_wrong = incorrect_diffs.count("intermediate")
    easy_wrong  = incorrect_diffs.count("easy")

    gaps = []
    if hard_wrong >= 3:
        gaps += key_concepts[:3]
    if inter_wrong >= 3:
        gaps += prereqs[:3]
    elif easy_wrong >= 3:
        gaps += prereqs[:2]

    seen, unique = set(), []
    for g in gaps:
        if g not in seen:
            seen.add(g)
            unique.append(g)
    return unique


# ---------------------------------------------------------------------------
def _render_results(topic, username):
    result = st.session_state.get("assessment_result")
    if not result:
        return

    score      = result["score"]
    max_score  = result["max_score"]
    level      = result["level"]
    correct    = result["correct"]
    total      = result["total"]
    gaps       = result.get("knowledge_gaps", [])
    per_diff   = result.get("per_difficulty", {})
    lc         = LEVEL_COLORS.get(level, "#A0A0C0")

    msg = {
        "Beginner":    "You are getting started. The tutor will teach from the ground up with clear explanations.",
        "Intermediate":"Good foundation. The tutor will build with technical examples and practical applications.",
        "Advanced":    "Excellent mastery. The tutor will engage with advanced discussions and research-level insights.",
    }.get(level, "")

    st.markdown(
        f"""
<div class="synapse-card fade-in" style="text-align:center;padding:2rem;">
    <h2 style="color:#FFFFFF;margin-bottom:0.4rem;">Assessment Complete</h2>
    <p style="color:#A0A0C0;margin-bottom:1.5rem;">Topic: <strong style="color:#00D2FF;">{topic}</strong></p>
    <div style="display:flex;justify-content:center;gap:3rem;margin-bottom:1.2rem;">
        <div>
            <div style="font-size:2.5rem;font-weight:800;color:{lc};">{score}/{max_score}</div>
            <div style="color:#A0A0C0;font-size:0.78rem;">Raw Score</div>
        </div>
        <div>
            <div style="font-size:2.5rem;font-weight:800;color:{lc};">{correct}/{total}</div>
            <div style="color:#A0A0C0;font-size:0.78rem;">Correct</div>
        </div>
    </div>
    <div style="display:inline-block;padding:0.4rem 1.3rem;border-radius:25px;
                background:rgba({_hex_rgb(lc)},0.14);border:1px solid rgba({_hex_rgb(lc)},0.3);
                color:{lc};font-weight:700;font-size:1rem;">{level}</div>
    <p style="color:#A0A0C0;margin-top:1rem;font-size:0.86rem;max-width:460px;margin-left:auto;margin-right:auto;">{msg}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if per_diff:
        st.markdown("<br>", unsafe_allow_html=True)
        dcols = st.columns(3)
        for i, (diff, dc) in enumerate(per_diff.items()):
            if dc["total"] == 0:
                continue
            acc    = int((dc["correct"] / dc["total"]) * 100)
            dcolor = DIFF_COLORS.get(diff, "#A0A0C0")
            with dcols[i]:
                st.markdown(
                    f"""
<div class="stat-card" style="border-color:rgba({_hex_rgb(dcolor)},0.2);">
    <div style="color:{dcolor};font-size:0.68rem;text-transform:uppercase;font-weight:700;margin-bottom:0.2rem;">{diff}</div>
    <div style="font-size:1.5rem;font-weight:800;color:{dcolor};">{dc["correct"]}/{dc["total"]}</div>
    <div style="color:#A0A0C0;font-size:0.72rem;">{acc}% accuracy</div>
</div>
""",
                    unsafe_allow_html=True,
                )

    if gaps:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="gap-warning"><div style="color:#F39C12;font-weight:600;margin-bottom:0.3rem;">Knowledge Gaps Detected</div>',
            unsafe_allow_html=True,
        )
        for g in gaps:
            st.markdown(
                f"<div style='color:#A0A0C0;font-size:0.82rem;margin:0.1rem 0;'>* {g}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    queue   = st.session_state.get("topic_queue", [])
    q_idx   = st.session_state.get("topic_queue_idx", 0)
    has_next = (q_idx + 1) < len(queue)

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        if st.button("Start Tutoring", use_container_width=True, type="primary", key="res_tutor"):
            if topic not in st.session_state.chat_histories:
                st.session_state.chat_histories[topic] = []
            _go("Tutor")
    with rc2:
        if has_next:
            next_topic = queue[q_idx + 1]
            if st.button(f"Next: Assess {next_topic[:15]}", use_container_width=True, key="res_next"):
                st.session_state.topic_queue_idx      += 1
                st.session_state.selected_topic       = next_topic
                st.session_state.assessment_questions = None
                st.session_state.assessment_answers   = []
                st.session_state.assessment_complete  = False
                st.session_state.assessment_result    = None
                st.session_state.current_question_idx = 0
                st.rerun()
        else:
            if st.button("Retake Assessment", use_container_width=True, key="res_retake"):
                st.session_state.assessment_questions = None
                st.session_state.assessment_answers   = []
                st.session_state.assessment_complete  = False
                st.session_state.assessment_result    = None
                st.session_state.current_question_idx = 0
                st.rerun()
    with rc3:
        if st.button("Choose Topics", use_container_width=True, key="res_topics"):
            _go("Topics")
