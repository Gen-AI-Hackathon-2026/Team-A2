"""
Dashboard Page for Synapse AI Tutor.
Per-topic mastery, levels, gaps, assessment history, and Plotly charts.
"""

import streamlit as st
import plotly.graph_objects as go
from backend.progress_tracker import (
    get_user_progress, get_overall_stats,
    get_strengths, get_weak_topics, get_completed_topics,
)

ALL_TOPICS = [
    "Neural Networks", "CNNs", "RNNs", "Transformers", "LLMs",
    "Prompt Engineering", "Generative AI Fundamentals", "GANs",
    "Diffusion Models", "Fine-Tuning and RAG",
]
LEVEL_COLORS = {
    "Beginner":    "#2ECC71",
    "Intermediate":"#F39C12",
    "Advanced":    "#8B83FF",
    "Not Assessed":"#6B6B8D",
}


def _go(page: str):
    st.session_state.page = page
    st.rerun()


def render_dashboard():
    username = st.session_state.username

    st.markdown(
        f"""
<div class="main-header fade-in">
    <h1>Progress Dashboard</h1>
    <p>Your learning journey, <strong style="color:#00D2FF;">{username}</strong></p>
</div>
""",
        unsafe_allow_html=True,
    )

    user_progress = get_user_progress(username)
    stats         = get_overall_stats(username)
    strengths     = get_strengths(username)
    completed     = get_completed_topics(username)

    # ── Stats Row ──────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    stat_cols = st.columns(5)
    for col, (label, value, sub) in zip(
        stat_cols,
        [
            ("Topics Attempted", str(stats["total_topics_attempted"]), "out of 10"),
            ("Completed",        str(stats["completed_topics"]),       "mastery >= 76%"),
            ("Avg Mastery",      f"{stats['average_mastery']}%",       "across topics"),
            ("Strongest",        (stats["strongest_topic"] or "--")[:14], "your best"),
            ("Sessions",         str(stats["total_sessions"]),         "total learning"),
        ],
    ):
        with col:
            st.markdown(
                f'<div class="stat-card"><div class="stat-value">{value}</div>'
                f'<div class="stat-label">{label}</div>'
                f'<div style="color:#6B6B8D;font-size:0.66rem;margin-top:0.15rem;">{sub}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    if not user_progress:
        st.markdown(
            '<div style="text-align:center;padding:2.5rem;background:rgba(108,99,255,0.04);'
            'border-radius:14px;border:1px solid rgba(108,99,255,0.1);">'
            '<h3 style="color:#FFFFFF;">No Progress Yet</h3>'
            '<p style="color:#A0A0C0;">Complete your first assessment to start tracking your learning journey.</p>'
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Start Learning", key="dash_start"):
            _go("Topics")
        return

    # ── Charts ────────────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        _render_radar(user_progress)
    with c2:
        _render_bar(user_progress)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "Knowledge Gaps", "Strengths and Weak Areas", "Assessment History", "Topic Status",
    ])
    with tab1:
        _render_knowledge_gaps_tab(user_progress)
    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            _render_strengths(strengths)
        with col_b:
            _render_weak_areas(user_progress)
    with tab3:
        _render_assessment_history(user_progress)
    with tab4:
        _render_topic_status(completed, user_progress)


# ---------------------------------------------------------------------------
def _render_radar(user_progress):
    topics    = ALL_TOPICS
    masteries = [user_progress.get(t, {}).get("mastery", 0) for t in topics]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=masteries + [masteries[0]],
        theta=topics + [topics[0]],
        fill="toself",
        fillcolor="rgba(108,99,255,0.12)",
        line=dict(color="#6C63FF", width=2),
        marker=dict(size=6, color="#8B83FF"),
        name="Mastery",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor="rgba(255,255,255,0.05)",
                            linecolor="rgba(255,255,255,0.08)",
                            tickfont=dict(size=8, color="#6B6B8D")),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.05)",
                             linecolor="rgba(255,255,255,0.08)",
                             tickfont=dict(size=9, color="#A0A0C0")),
        ),
        title=dict(text="Mastery Overview", font=dict(size=14, color="#FFFFFF"), x=0.5),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=380, margin=dict(l=65, r=65, t=45, b=25),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_bar(user_progress):
    topics, masteries, colors = [], [], []
    for t in ALL_TOPICS:
        m = user_progress.get(t, {}).get("mastery", 0)
        if m > 0:
            topics.append(t)
            masteries.append(m)
            colors.append("#8B83FF" if m >= 76 else "#F39C12" if m >= 43 else "#2ECC71")
    if not topics:
        st.info("Complete assessments to see mastery levels.")
        return
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=topics, x=masteries, orientation="h",
        marker=dict(color=colors, cornerradius=4),
        text=[f"{m}%" for m in masteries], textposition="outside",
        textfont=dict(color="#A0A0C0", size=10),
    ))
    fig.update_layout(
        title=dict(text="Mastery by Topic", font=dict(size=14, color="#FFFFFF"), x=0.5),
        xaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,0.03)",
                   tickfont=dict(color="#6B6B8D"), title=None),
        yaxis=dict(tickfont=dict(color="#A0A0C0", size=9), title=None),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=380, margin=dict(l=5, r=12, t=45, b=12), showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
def _render_knowledge_gaps_tab(user_progress):
    st.markdown(
        '<div style="font-weight:600;color:#FFFFFF;font-size:0.92rem;margin-bottom:0.7rem;">Knowledge Gaps by Topic</div>',
        unsafe_allow_html=True,
    )
    has_any = False
    for topic in ALL_TOPICS:
        data    = user_progress.get(topic, {})
        gaps    = data.get("knowledge_gaps", [])
        mastery = data.get("mastery", 0)
        level   = data.get("level", "Not Assessed")
        if gaps and mastery > 0:
            has_any = True
            with st.expander(f"{topic}  —  {level}  ({mastery}% mastery)", expanded=False):
                for g in gaps:
                    st.markdown(
                        f'<div style="padding:0.28rem 0.55rem;margin:0.18rem 0;'
                        f'background:rgba(243,156,18,0.05);border-radius:5px;'
                        f'border-left:3px solid #F39C12;color:#A0A0C0;font-size:0.8rem;">{g}</div>',
                        unsafe_allow_html=True,
                    )
    if not has_any:
        st.success("No knowledge gaps detected. Keep learning to track gaps here.")


def _render_strengths(strengths):
    st.markdown('<div style="font-weight:600;color:#FFFFFF;font-size:0.88rem;margin-bottom:0.7rem;">Your Strengths</div>', unsafe_allow_html=True)
    if not strengths:
        st.markdown('<div style="color:#6B6B8D;font-size:0.8rem;padding:0.9rem;text-align:center;background:rgba(255,255,255,0.02);border-radius:9px;">Complete more assessments to identify your strengths.</div>', unsafe_allow_html=True)
        return
    for item in strengths[:5]:
        m  = item["mastery"]
        bc = "#8B83FF" if m >= 76 else "#2ECC71"
        st.markdown(
            f'<div style="padding:0.55rem 0.85rem;margin-bottom:0.35rem;'
            f'background:rgba(46,204,113,0.04);border-radius:9px;'
            f'border:1px solid rgba(46,204,113,0.1);">'
            f'<div style="display:flex;justify-content:space-between;">'
            f'<span style="color:#FFFFFF;font-size:0.83rem;font-weight:500;">{item["topic"]}</span>'
            f'<span style="color:{bc};font-weight:700;font-size:0.83rem;">{m}%</span></div>'
            f'<div style="background:rgba(255,255,255,0.05);border-radius:3px;height:3px;margin-top:0.35rem;overflow:hidden;">'
            f'<div style="background:{bc};width:{m}%;height:100%;border-radius:3px;"></div></div>'
            f"</div>",
            unsafe_allow_html=True,
        )


def _render_weak_areas(user_progress):
    st.markdown('<div style="font-weight:600;color:#FFFFFF;font-size:0.88rem;margin-bottom:0.7rem;">Areas to Improve</div>', unsafe_allow_html=True)
    weak = [
        {"topic": t, "mastery": d.get("mastery", 0), "gaps": d.get("knowledge_gaps", [])}
        for t, d in user_progress.items() if 0 < d.get("mastery", 0) < 50
    ]
    if not weak:
        st.markdown('<div style="color:#6B6B8D;font-size:0.8rem;padding:0.9rem;text-align:center;background:rgba(255,255,255,0.02);border-radius:9px;">No major weak areas. Keep learning.</div>', unsafe_allow_html=True)
        return
    for item in weak[:5]:
        gaps_text = f"Gaps: {', '.join(item['gaps'][:2])}" if item["gaps"] else ""
        st.markdown(
            f'<div style="padding:0.55rem 0.85rem;margin-bottom:0.35rem;'
            f'background:rgba(243,156,18,0.04);border-radius:9px;'
            f'border:1px solid rgba(243,156,18,0.1);">'
            f'<div style="display:flex;justify-content:space-between;">'
            f'<span style="color:#FFFFFF;font-size:0.83rem;font-weight:500;">{item["topic"]}</span>'
            f'<span style="color:#F39C12;font-weight:700;font-size:0.83rem;">{item["mastery"]}%</span></div>'
            + (f'<div style="color:#6B6B8D;font-size:0.7rem;margin-top:0.15rem;">{gaps_text}</div>' if gaps_text else "")
            + "</div>",
            unsafe_allow_html=True,
        )


def _render_assessment_history(user_progress):
    st.markdown('<div style="font-weight:600;color:#FFFFFF;font-size:0.88rem;margin-bottom:0.7rem;">Assessment History</div>', unsafe_allow_html=True)
    has_history = False
    for topic in ALL_TOPICS:
        data     = user_progress.get(topic, {})
        history  = data.get("assessment_history", [])
        practice = data.get("practice_history", [])
        if history or practice:
            has_history = True
            with st.expander(f"{topic} ({len(history)} assessments, {len(practice)} practice sessions)"):
                if history:
                    st.markdown("**Assessments:**")
                    for h in reversed(history[-5:]):
                        date_str = h.get("date", "")[:10]
                        score    = h.get("score", 0)
                        max_s    = h.get("max_score", 30)
                        level    = h.get("level", "")
                        lc       = LEVEL_COLORS.get(level, "#A0A0C0")
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;padding:0.22rem 0.45rem;'
                            f'background:rgba(255,255,255,0.02);border-radius:5px;margin-bottom:0.12rem;">'
                            f'<span style="color:#A0A0C0;font-size:0.76rem;">{date_str}</span>'
                            f'<span style="color:{lc};font-size:0.76rem;font-weight:600;">{score}/{max_s} — {level}</span></div>',
                            unsafe_allow_html=True,
                        )
                if practice:
                    st.markdown("**Practice Sessions:**")
                    for p in reversed(practice[-5:]):
                        date_str = p.get("date", "")[:10]
                        acc      = int(p.get("accuracy", 0) * 100)
                        delta    = p.get("delta", 0)
                        dc       = "#2ECC71" if delta >= 0 else "#E74C3C"
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;padding:0.22rem 0.45rem;'
                            f'background:rgba(255,255,255,0.02);border-radius:5px;margin-bottom:0.12rem;">'
                            f'<span style="color:#A0A0C0;font-size:0.76rem;">{date_str} — {acc}% accuracy</span>'
                            f'<span style="color:{dc};font-size:0.76rem;font-weight:600;">Mastery {("+" if delta >= 0 else "")}{delta}%</span></div>',
                            unsafe_allow_html=True,
                        )
    if not has_history:
        st.info("No assessment or practice history yet.")


def _render_topic_status(completed, user_progress):
    st.markdown('<div style="font-weight:600;color:#FFFFFF;font-size:0.88rem;margin-bottom:0.7rem;">All Topics</div>', unsafe_allow_html=True)
    for topic in ALL_TOPICS:
        data    = user_progress.get(topic, {})
        mastery = data.get("mastery", 0)
        level   = data.get("level", "Not Assessed")
        if topic in completed:
            sc, marker = "#2ECC71", "Done"
        elif mastery > 0:
            sc, marker = "#F39C12", "In Progress"
        else:
            sc, marker = "#6B6B8D", "Not Started"
        lc = LEVEL_COLORS.get(level, "#6B6B8D")
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:0.38rem 0.65rem;margin-bottom:0.25rem;'
            f'background:rgba(255,255,255,0.02);border-radius:7px;">'
            f'<div><span style="color:{sc};font-size:0.8rem;font-weight:500;">{topic}</span>'
            f'<span style="color:#6B6B8D;font-size:0.68rem;margin-left:0.35rem;">[{marker}]</span></div>'
            f'<div><span style="color:{lc};font-size:0.76rem;font-weight:600;">{level}</span>'
            f'<span style="color:#6B6B8D;font-size:0.7rem;margin-left:0.45rem;">{mastery}%</span></div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    total_done = len(completed)
    st.markdown(
        f'<div style="text-align:center;margin-top:0.8rem;padding:0.7rem;'
        f'background:rgba(108,99,255,0.05);border-radius:9px;'
        f'border:1px solid rgba(108,99,255,0.1);">'
        f'<div style="color:#8B83FF;font-weight:700;font-size:1.3rem;">{total_done}/10</div>'
        f'<div style="color:#A0A0C0;font-size:0.75rem;">Topics Completed</div></div>',
        unsafe_allow_html=True,
    )
