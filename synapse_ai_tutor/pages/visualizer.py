"""
Visualizer Page for Synapse AI Tutor.
Interactive knowledge graph and mastery charts using Plotly.
"""

import streamlit as st
import plotly.graph_objects as go
import math
from backend.progress_tracker import get_user_progress, get_overall_stats

ALL_TOPICS = [
    "Neural Networks", "CNNs", "RNNs", "Transformers", "LLMs",
    "Prompt Engineering", "Generative AI Fundamentals", "GANs",
    "Diffusion Models", "Fine-Tuning and RAG",
]

TOPIC_EDGES = [
    ("Neural Networks", "CNNs"),
    ("Neural Networks", "RNNs"),
    ("Neural Networks", "Transformers"),
    ("Neural Networks", "GANs"),
    ("Neural Networks", "Diffusion Models"),
    ("RNNs", "Transformers"),
    ("Transformers", "LLMs"),
    ("LLMs", "Prompt Engineering"),
    ("LLMs", "Fine-Tuning and RAG"),
    ("Transformers", "Fine-Tuning and RAG"),
    ("Generative AI Fundamentals", "GANs"),
    ("Generative AI Fundamentals", "Diffusion Models"),
    ("Generative AI Fundamentals", "LLMs"),
]

TOPIC_COLORS = {
    "Neural Networks":            "#6C63FF",
    "CNNs":                       "#00D2FF",
    "RNNs":                       "#FF6B6B",
    "Transformers":               "#FFB347",
    "LLMs":                       "#2ECC71",
    "Prompt Engineering":         "#E74C3C",
    "Generative AI Fundamentals": "#9B59B6",
    "GANs":                       "#1ABC9C",
    "Diffusion Models":           "#3498DB",
    "Fine-Tuning and RAG":        "#F39C12",
}
LEVEL_COLORS = {
    "Beginner":    "#2ECC71",
    "Intermediate":"#F39C12",
    "Advanced":    "#8B83FF",
    "Not Assessed":"#6B6B8D",
}


def _get_positions() -> dict:
    inner = ["Neural Networks", "Transformers", "LLMs", "Generative AI Fundamentals"]
    outer = [t for t in ALL_TOPICS if t not in inner]
    pos = {}
    inner_xy = [(-0.38, 0.32), (0.38, 0.32), (0.38, -0.32), (-0.38, -0.32)]
    for i, t in enumerate(inner):
        pos[t] = inner_xy[i]
    for i, t in enumerate(outer):
        angle = (2 * math.pi * i) / len(outer) - math.pi / 2
        pos[t] = (0.85 * math.cos(angle), 0.85 * math.sin(angle))
    return pos


def _build_knowledge_graph(user_progress: dict) -> go.Figure:
    positions = _get_positions()
    edge_x, edge_y = [], []
    for src, dst in TOPIC_EDGES:
        x0, y0 = positions[src]
        x1, y1 = positions[dst]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    node_x, node_y, node_text, node_hover = [], [], [], []
    node_colors, node_sizes, node_borders = [], [], []

    for topic in ALL_TOPICS:
        x, y    = positions[topic]
        data    = user_progress.get(topic, {})
        mastery = data.get("mastery", 0)
        level   = data.get("level", "Not Assessed")
        gaps    = data.get("knowledge_gaps", [])
        node_x.append(x); node_y.append(y)
        short = (topic[:11] + "...") if len(topic) > 11 else topic
        node_text.append(short)
        gaps_str = "<br>".join(f"* {g}" for g in gaps[:3]) if gaps else "None"
        node_hover.append(f"<b>{topic}</b><br>Level: {level}<br>Mastery: {mastery}%<br>Gaps: {gaps_str}")
        node_colors.append(TOPIC_COLORS.get(topic, "#6C63FF"))
        node_sizes.append(28 + mastery * 0.22)
        node_borders.append(LEVEL_COLORS.get(level, "#6B6B8D"))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=1.1, color="rgba(108,99,255,0.18)"),
        hoverinfo="none", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=node_text, textposition="top center",
        textfont=dict(size=9, color="#FFFFFF"),
        hovertext=node_hover, hoverinfo="text",
        marker=dict(size=node_sizes, color=node_colors,
                    line=dict(color=node_borders, width=2.2), opacity=0.9),
        showlegend=False,
    ))
    fig.update_layout(
        title=dict(text="Knowledge Graph - Topic Relationships and Mastery",
                   font=dict(size=15, color="#FFFFFF"), x=0.5),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.15, 1.15]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.15, 1.15]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(14,14,30,0.35)",
        height=500, margin=dict(l=15, r=15, t=55, b=15),
        hoverlabel=dict(bgcolor="#1A1A3E", font_size=12, font_color="#FFFFFF",
                        bordercolor="rgba(108,99,255,0.4)"),
    )
    return fig


def _build_bar(user_progress: dict) -> go.Figure:
    masteries = [user_progress.get(t, {}).get("mastery", 0) for t in ALL_TOPICS]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ALL_TOPICS, y=masteries,
        marker=dict(
            color=masteries,
            colorscale=[[0, "#1A1A3E"], [0.35, "#6C63FF"], [0.7, "#00D2FF"], [1, "#2ECC71"]],
            showscale=True,
            colorbar=dict(title="Mastery %",
                          tickfont=dict(color="#A0A0C0"),
                          titlefont=dict(color="#A0A0C0")),
        ),
        text=[f"{m}%" for m in masteries], textposition="outside",
        textfont=dict(color="#A0A0C0", size=10),
        hovertemplate="<b>%{x}</b><br>Mastery: %{y}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Mastery by Topic", font=dict(size=14, color="#FFFFFF"), x=0.5),
        xaxis=dict(tickangle=-30, tickfont=dict(color="#A0A0C0", size=9),
                   gridcolor="rgba(255,255,255,0.03)"),
        yaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,0.03)",
                   tickfont=dict(color="#6B6B8D")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(14,14,30,0.35)",
        height=360, margin=dict(l=8, r=8, t=45, b=75), showlegend=False,
    )
    return fig


def _build_radar(user_progress: dict) -> go.Figure:
    masteries = [user_progress.get(t, {}).get("mastery", 0) for t in ALL_TOPICS]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=masteries + [masteries[0]], theta=ALL_TOPICS + [ALL_TOPICS[0]],
        fill="toself", fillcolor="rgba(108,99,255,0.12)",
        line=dict(color="#6C63FF", width=2), marker=dict(size=6, color="#8B83FF"),
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
        title=dict(text="Skill Radar", font=dict(size=14, color="#FFFFFF"), x=0.5),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=360, margin=dict(l=55, r=55, t=45, b=25),
    )
    return fig


def render_visualizer():
    username      = st.session_state.username
    user_progress = get_user_progress(username)
    stats         = get_overall_stats(username)

    st.markdown(
        """
<div class="main-header fade-in">
    <h1>Knowledge Visualizer</h1>
    <p>Explore your learning graph and mastery patterns</p>
</div>
""",
        unsafe_allow_html=True,
    )

    # Stats row
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, (val, label) in zip(
        [sc1, sc2, sc3, sc4],
        [
            (stats["total_topics_attempted"], "Topics Explored"),
            (f"{stats['average_mastery']}%",  "Avg Mastery"),
            (stats["completed_topics"],        "Completed"),
            (stats["total_sessions"],          "Sessions"),
        ],
    ):
        with col:
            st.markdown(
                f'<div class="stat-card"><div class="stat-value">{val}</div>'
                f'<div class="stat-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Legend
    st.markdown(
        """
<div style="display:flex;gap:1.2rem;flex-wrap:wrap;margin-bottom:0.7rem;
            padding:0.6rem 0.9rem;background:rgba(255,255,255,0.02);
            border-radius:9px;border:1px solid rgba(255,255,255,0.04);">
    <span style="color:#6B6B8D;font-size:0.72rem;font-weight:600;align-self:center;">Node border = Level:</span>
    <span style="color:#2ECC71;font-size:0.75rem;">Beginner</span>
    <span style="color:#F39C12;font-size:0.75rem;">Intermediate</span>
    <span style="color:#8B83FF;font-size:0.75rem;">Advanced</span>
    <span style="color:#6B6B8D;font-size:0.75rem;">Not Assessed</span>
    <span style="color:#A0A0C0;font-size:0.75rem;margin-left:0.8rem;">Node size = Mastery %</span>
</div>
""",
        unsafe_allow_html=True,
    )

    if not user_progress:
        st.info("Complete assessments to see your knowledge graph populated with mastery data.")

    st.plotly_chart(_build_knowledge_graph(user_progress), use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab_bar, tab_radar = st.tabs(["Mastery Bar Chart", "Skill Radar"])
    with tab_bar:
        st.plotly_chart(_build_bar(user_progress), use_container_width=True)
    with tab_radar:
        st.plotly_chart(_build_radar(user_progress), use_container_width=True)

    # Detail table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-weight:700;color:#FFFFFF;font-size:0.95rem;margin-bottom:0.7rem;">Topic Detail View</div>',
        unsafe_allow_html=True,
    )
    for topic in ALL_TOPICS:
        data    = user_progress.get(topic, {})
        mastery = data.get("mastery", 0)
        level   = data.get("level", "Not Assessed")
        gaps    = data.get("knowledge_gaps", [])
        color   = TOPIC_COLORS.get(topic, "#6C63FF")
        lc      = LEVEL_COLORS.get(level, "#6B6B8D")
        gaps_html = " | ".join(
            f"<span style='color:#F39C12;font-size:0.7rem;'>{g}</span>" for g in gaps[:3]
        ) if gaps else "<span style='color:#6B6B8D;font-size:0.7rem;'>None detected</span>"

        st.markdown(
            f"""
<div style="display:flex;align-items:center;gap:0.9rem;padding:0.5rem 0.9rem;
            margin-bottom:0.25rem;background:rgba(20,20,46,0.5);border-radius:9px;
            border-left:3px solid {color};">
    <span style="color:{color};font-weight:700;min-width:38px;font-size:0.78rem;">{mastery}%</span>
    <span style="color:#FFFFFF;font-weight:500;font-size:0.83rem;min-width:185px;">{topic}</span>
    <div style="background:rgba(255,255,255,0.05);border-radius:3px;height:5px;
                width:110px;overflow:hidden;flex-shrink:0;">
        <div style="background:{color};width:{mastery}%;height:100%;border-radius:3px;"></div>
    </div>
    <span style="color:{lc};font-size:0.73rem;font-weight:600;min-width:86px;">{level}</span>
    <div style="flex:1;">{gaps_html}</div>
</div>
""",
            unsafe_allow_html=True,
        )
