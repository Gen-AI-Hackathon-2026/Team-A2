"""
Dashboard Page for Synapse AI Tutor.
Displays progress tracking, mastery charts, strengths,
weak areas, and completed topics using Plotly.
"""

import streamlit as st
import plotly.graph_objects as go
from backend.progress_tracker import (
    get_user_progress, get_overall_stats,
    get_strengths, get_weak_topics, get_completed_topics
)


# All topics for reference
ALL_TOPICS = [
    "Neural Networks", "CNNs", "RNNs", "Transformers", "LLMs",
    "Prompt Engineering", "Generative AI Fundamentals", "GANs",
    "Diffusion Models", "Fine-Tuning and RAG"
]


def render_dashboard():
    """Render the progress dashboard page."""

    username = st.session_state.username

    # Header
    st.markdown(f"""
    <div class="main-header animate-fade-in">
        <h1>Progress Dashboard</h1>
        <p>Track your learning journey, <strong style="color: #00D2FF;">{username}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Get data
    user_progress = get_user_progress(username)
    overall_stats = get_overall_stats(username)
    strengths = get_strengths(username)
    weak_topics = get_weak_topics(username)
    completed = get_completed_topics(username)

    # Top stats row
    st.markdown("<br>", unsafe_allow_html=True)
    stat_cols = st.columns(5)

    stats = [
        ("Topics Attempted", str(overall_stats["total_topics_attempted"]), "out of 10"),
        ("Completed", str(overall_stats["completed_topics"]), "mastery >= 75%"),
        ("Avg. Mastery", f"{overall_stats['average_mastery']}%", "across all topics"),
        ("Strongest", overall_stats["strongest_topic"] or "--", "your best topic"),
        ("Total Sessions", str(overall_stats["total_sessions"]), "learning sessions"),
    ]

    for col, (label, value, sublabel) in zip(stat_cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{value}</div>
                <div class="stat-label">{label}</div>
                <div style="color: #6B6B8D; font-size: 0.7rem; margin-top: 0.2rem;">{sublabel}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not user_progress:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: rgba(108, 99, 255, 0.05);
                    border-radius: 16px; border: 1px solid rgba(108, 99, 255, 0.1);">
            <h3 style="color: #FFFFFF; margin-bottom: 0.5rem;">No Progress Yet</h3>
            <p style="color: #A0A0C0;">Complete your first assessment to start tracking your learning journey!</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Start Learning", use_container_width=False):
            st.session_state.current_page = "topic_selection"
            st.rerun()
        return

    # Charts row
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        _render_mastery_radar(user_progress)

    with chart_col2:
        _render_mastery_bar(user_progress)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bottom section
    bottom_col1, bottom_col2, bottom_col3 = st.columns(3)

    with bottom_col1:
        _render_strengths(strengths)

    with bottom_col2:
        _render_weak_areas(weak_topics, user_progress)

    with bottom_col3:
        _render_completion_status(completed, user_progress)


def _render_mastery_radar(user_progress):
    """Render the radar/spider chart of topic mastery."""

    topics = []
    masteries = []

    for topic in ALL_TOPICS:
        topics.append(topic)
        if topic in user_progress:
            masteries.append(user_progress[topic].get("mastery", 0))
        else:
            masteries.append(0)

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=masteries + [masteries[0]],  # Close the shape
        theta=topics + [topics[0]],
        fill='toself',
        fillcolor='rgba(108, 99, 255, 0.15)',
        line=dict(color='#6C63FF', width=2),
        marker=dict(size=6, color='#8B83FF'),
        name='Mastery'
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.05)',
                linecolor='rgba(255,255,255,0.1)',
                tickfont=dict(size=9, color='#6B6B8D'),
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.05)',
                linecolor='rgba(255,255,255,0.1)',
                tickfont=dict(size=10, color='#A0A0C0'),
            ),
        ),
        title=dict(
            text="Mastery Overview",
            font=dict(size=16, color='#FFFFFF'),
            x=0.5
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=420,
        margin=dict(l=80, r=80, t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_mastery_bar(user_progress):
    """Render the horizontal bar chart of topic mastery."""

    topics = []
    masteries = []
    colors = []

    for topic in ALL_TOPICS:
        if topic in user_progress:
            mastery = user_progress[topic].get("mastery", 0)
            if mastery > 0:
                topics.append(topic)
                masteries.append(mastery)

                if mastery >= 76:
                    colors.append('#8B83FF')
                elif mastery >= 41:
                    colors.append('#F39C12')
                else:
                    colors.append('#2ECC71')

    if not topics:
        st.info("Complete assessments to see your mastery levels.")
        return

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=topics,
        x=masteries,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=0),
            cornerradius=5,
        ),
        text=[f"{m}%" for m in masteries],
        textposition='outside',
        textfont=dict(color='#A0A0C0', size=11),
    ))

    fig.update_layout(
        title=dict(
            text="Mastery by Topic",
            font=dict(size=16, color='#FFFFFF'),
            x=0.5
        ),
        xaxis=dict(
            range=[0, 110],
            gridcolor='rgba(255,255,255,0.03)',
            tickfont=dict(color='#6B6B8D'),
            title=None,
        ),
        yaxis=dict(
            tickfont=dict(color='#A0A0C0', size=11),
            title=None,
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=420,
        margin=dict(l=10, r=20, t=60, b=20),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_strengths(strengths):
    """Render the strengths section."""

    st.markdown("""
    <div style="font-weight: 600; color: #FFFFFF; font-size: 1.05rem; margin-bottom: 1rem;">
        Your Strengths
    </div>
    """, unsafe_allow_html=True)

    if not strengths:
        st.markdown("""
        <div style="color: #6B6B8D; font-size: 0.85rem; padding: 1rem; text-align: center;
                    background: rgba(255,255,255,0.02); border-radius: 12px;">
            Complete more assessments to identify your strengths!
        </div>
        """, unsafe_allow_html=True)
        return

    for item in strengths[:5]:
        mastery = item["mastery"]
        bar_color = "#8B83FF" if mastery >= 76 else "#2ECC71"

        st.markdown(f"""
        <div style="padding: 0.7rem 1rem; margin-bottom: 0.5rem;
                    background: rgba(46, 204, 113, 0.05); border-radius: 10px;
                    border: 1px solid rgba(46, 204, 113, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #FFFFFF; font-size: 0.9rem; font-weight: 500;">
                    {item['topic']}
                </span>
                <span style="color: {bar_color}; font-weight: 700; font-size: 0.9rem;">
                    {mastery}%
                </span>
            </div>
            <div style="background: rgba(255,255,255,0.05); border-radius: 4px; height: 4px;
                        margin-top: 0.5rem; overflow: hidden;">
                <div style="background: {bar_color}; width: {mastery}%; height: 100%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_weak_areas(weak_topics, user_progress):
    """Render the weak areas section."""

    st.markdown("""
    <div style="font-weight: 600; color: #FFFFFF; font-size: 1.05rem; margin-bottom: 1rem;">
        Areas to Improve
    </div>
    """, unsafe_allow_html=True)

    # Collect all weak areas across topics
    all_weak = []

    for topic, data in user_progress.items():
        weak_areas = data.get("weak_areas", [])
        mastery = data.get("mastery", 0)

        if mastery > 0 and mastery < 60:
            all_weak.append({"topic": topic, "mastery": mastery, "areas": weak_areas})

    if not all_weak:
        st.markdown("""
        <div style="color: #6B6B8D; font-size: 0.85rem; padding: 1rem; text-align: center;
                    background: rgba(255,255,255,0.02); border-radius: 12px;">
            No major weak areas detected. Keep learning!
        </div>
        """, unsafe_allow_html=True)
        return

    for item in all_weak[:5]:
        weak_areas_text = ""
        if item["areas"]:
            weak_areas_text = f"<div style='color: #6B6B8D; font-size: 0.75rem; margin-top: 0.3rem;'>Gaps: {', '.join(item['areas'][:3])}</div>"

        st.markdown(f"""
        <div style="padding: 0.7rem 1rem; margin-bottom: 0.5rem;
                    background: rgba(243, 156, 18, 0.05); border-radius: 10px;
                    border: 1px solid rgba(243, 156, 18, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #FFFFFF; font-size: 0.9rem; font-weight: 500;">
                    {item['topic']}
                </span>
                <span style="color: #F39C12; font-weight: 700; font-size: 0.9rem;">
                    {item['mastery']}%
                </span>
            </div>
            {weak_areas_text}
        </div>
        """, unsafe_allow_html=True)


def _render_completion_status(completed, user_progress):
    """Render the completion status section."""

    st.markdown("""
    <div style="font-weight: 600; color: #FFFFFF; font-size: 1.05rem; margin-bottom: 1rem;">
        Topic Status
    </div>
    """, unsafe_allow_html=True)

    for topic in ALL_TOPICS:
        if topic in user_progress:
            data = user_progress[topic]
            mastery = data.get("mastery", 0)

            if topic in completed:
                status_color = "#2ECC71"
                status_marker = "[Done]"
            elif mastery > 0:
                status_color = "#F39C12"
                status_marker = "[In Progress]"
            else:
                status_color = "#6B6B8D"
                status_marker = ""
        else:
            status_color = "#6B6B8D"
            status_marker = ""
            mastery = 0

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;
                    padding: 0.4rem 0.6rem; margin-bottom: 0.3rem;
                    background: rgba(255,255,255,0.02); border-radius: 8px;">
            <span style="color: {status_color}; font-size: 0.82rem;">
                {topic} <span style="font-size: 0.7rem;">{status_marker}</span>
            </span>
            <span style="color: #6B6B8D; font-size: 0.75rem;">
                {mastery}%
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Summary
    total_completed = len(completed)
    st.markdown(f"""
    <div style="text-align: center; margin-top: 1rem; padding: 0.8rem;
                background: rgba(108, 99, 255, 0.05); border-radius: 10px;
                border: 1px solid rgba(108, 99, 255, 0.1);">
        <div style="color: #8B83FF; font-weight: 700; font-size: 1.5rem;">{total_completed}/10</div>
        <div style="color: #A0A0C0; font-size: 0.8rem;">Topics Completed</div>
    </div>
    """, unsafe_allow_html=True)
