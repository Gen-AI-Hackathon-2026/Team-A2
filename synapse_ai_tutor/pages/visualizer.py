"""
Visualizer Page for Synapse AI Tutor.
Interactive knowledge graph (concept-level) using GraphRAG graph data,
plus mastery bar and skill radar using Plotly.

Green  = mastered concepts
Yellow = partial mastery (assessed but < 76%)
Red    = knowledge gaps
Grey   = not yet assessed
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

# Status colours for the concept graph
STATUS_COLORS = {
    "mastered": "#2ECC71",
    "partial":  "#F39C12",
    "gap":      "#E74C3C",
    "unknown":  "#6B6B8D",
}


# ---------------------------------------------------------------------------
# Topic-level graph (existing)
# ---------------------------------------------------------------------------

def _get_topic_positions() -> dict:
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


TOPIC_EDGES = [
    ("Neural Networks", "CNNs"),
    ("Neural Networks", "RNNs"),
    ("Neural Networks", "Transformers"),
    ("Neural Networks", "GANs"),
    ("Neural Networks", "Diffusion Models"),
    ("Neural Networks", "Generative AI Fundamentals"),
    ("RNNs", "Transformers"),
    ("Transformers", "LLMs"),
    ("Transformers", "Fine-Tuning and RAG"),
    ("LLMs", "Prompt Engineering"),
    ("LLMs", "Fine-Tuning and RAG"),
    ("Generative AI Fundamentals", "GANs"),
    ("Generative AI Fundamentals", "Diffusion Models"),
    ("Generative AI Fundamentals", "LLMs"),
]


def _build_topic_graph(user_progress: dict) -> go.Figure:
    positions = _get_topic_positions()
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


# ---------------------------------------------------------------------------
# Concept-level GraphRAG graph
# ---------------------------------------------------------------------------

def _build_concept_graph(selected_topic: str, user_progress: dict) -> go.Figure:
    """
    Build an interactive concept-level graph for the selected topic,
    loaded from the knowledge graph JSON via the KG module.

    Nodes are coloured by mastery status:
      Green  = mastered
      Yellow = partial
      Red    = gap
      Grey   = unknown
    """
    try:
        from backend.knowledge_graph import get_all_concepts_for_topic, _get_graph
        import networkx as nx

        G = _get_graph()
        topic_data = user_progress.get(selected_topic, {})
        gaps       = set(topic_data.get("knowledge_gaps", []))
        mastery    = topic_data.get("mastery", 0)

        concepts = get_all_concepts_for_topic(selected_topic)
        concepts = [c for c in concepts if c in G and c != selected_topic]

        if not concepts:
            return None

        # Layout: radial around topic centre
        n = len(concepts)
        positions = {selected_topic: (0.0, 0.0)}
        for i, c in enumerate(concepts):
            angle = (2 * math.pi * i) / n
            positions[c] = (math.cos(angle) * 0.75, math.sin(angle) * 0.75)

        # Edges: topic -> concept + concept -> concept
        edge_x, edge_y = [], []
        edge_colors = []
        all_nodes = [selected_topic] + concepts
        for u in all_nodes:
            for v in G.successors(u):
                if v in positions:
                    x0, y0 = positions[u]
                    x1, y1 = positions[v]
                    edge_x += [x0, x1, None]
                    edge_y += [y0, y1, None]

        node_x, node_y, node_text, node_hover = [], [], [], []
        node_colors, node_sizes, node_borders = [], [], []

        def _concept_status(c):
            if c in gaps:
                return "gap"
            if c == selected_topic:
                if mastery >= 76:
                    return "mastered"
                if mastery > 0:
                    return "partial"
                return "unknown"
            # Check if concept name hints at mastery
            return "unknown"

        # Topic node (centre)
        status = _concept_status(selected_topic)
        node_x.append(0.0); node_y.append(0.0)
        short_t = (selected_topic[:12] + "...") if len(selected_topic) > 12 else selected_topic
        node_text.append(short_t)
        node_hover.append(f"<b>{selected_topic}</b> (Topic)<br>Mastery: {mastery}%")
        node_colors.append(TOPIC_COLORS.get(selected_topic, "#6C63FF"))
        node_sizes.append(40)
        node_borders.append(STATUS_COLORS[status])

        # Concept nodes
        for c in concepts:
            status = _concept_status(c)
            x, y   = positions[c]
            node_x.append(x); node_y.append(y)
            short_c = (c[:14] + "...") if len(c) > 14 else c
            node_text.append(short_c)
            nbrs    = list(G.successors(c)) + list(G.predecessors(c))
            nbrs    = [b for b in nbrs if b in positions]
            rel     = G.nodes[c].get("node_type", "concept")
            gap_tag = " [GAP]" if c in gaps else ""
            node_hover.append(
                f"<b>{c}</b>{gap_tag}<br>"
                f"Type: {rel}<br>"
                f"Connected to: {', '.join(nbrs[:3])}" + ("..." if len(nbrs) > 3 else "")
            )
            node_colors.append(STATUS_COLORS[status])
            node_sizes.append(22)
            node_borders.append("#FFFFFF" if c in gaps else TOPIC_COLORS.get(selected_topic, "#6C63FF"))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(width=1.0, color="rgba(255,255,255,0.08)"),
            hoverinfo="none", showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y, mode="markers+text",
            text=node_text, textposition="top center",
            textfont=dict(size=8, color="#FFFFFF"),
            hovertext=node_hover, hoverinfo="text",
            marker=dict(
                size=node_sizes, color=node_colors,
                line=dict(color=node_borders, width=1.8), opacity=0.92,
            ),
            showlegend=False,
        ))
        topic_color = TOPIC_COLORS.get(selected_topic, "#6C63FF")
        fig.update_layout(
            title=dict(
                text=f"Concept Graph - {selected_topic}",
                font=dict(size=14, color="#FFFFFF"), x=0.5,
            ),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.1, 1.1]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.1, 1.1]),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=f"rgba(14,14,30,0.4)",
            height=420, margin=dict(l=10, r=10, t=45, b=10),
            hoverlabel=dict(bgcolor="#1A1A3E", font_size=12, font_color="#FFFFFF",
                            bordercolor=f"rgba({int(topic_color[1:3],16)},{int(topic_color[3:5],16)},{int(topic_color[5:7],16)},0.4)"),
        )
        return fig

    except Exception as e:
        return None


# ---------------------------------------------------------------------------
# Bar and Radar charts
# ---------------------------------------------------------------------------

def _build_bar(user_progress: dict) -> go.Figure:
    topics, masteries, colors = [], [], []
    for t in ALL_TOPICS:
        m = user_progress.get(t, {}).get("mastery", 0)
        if m > 0:
            topics.append(t)
            masteries.append(m)
            colors.append("#8B83FF" if m >= 76 else "#F39C12" if m >= 43 else "#2ECC71")
    if not topics:
        return None
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


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

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

    # ── GraphRAG concept graph ─────────────────────────────────────────────────
    st.markdown(
        '<div style="font-weight:700;color:#FFFFFF;font-size:1rem;margin-bottom:0.5rem;">Concept Graph (GraphRAG)</div>',
        unsafe_allow_html=True,
    )

    # Topic selector for concept graph
    selected_topics = st.session_state.get("selected_topics", [])
    topic_options   = selected_topics if selected_topics else ALL_TOPICS
    chosen_topic    = st.selectbox(
        "Select topic to explore concepts",
        topic_options,
        key="viz_topic_selector",
        label_visibility="collapsed",
    )

    # Concept graph legend
    st.markdown(
        """
<div style="display:flex;gap:1.2rem;flex-wrap:wrap;margin-bottom:0.6rem;
            padding:0.5rem 0.9rem;background:rgba(255,255,255,0.02);
            border-radius:9px;border:1px solid rgba(255,255,255,0.04);">
    <span style="color:#6B6B8D;font-size:0.72rem;font-weight:600;align-self:center;">Concept Status:</span>
    <span style="color:#2ECC71;font-size:0.75rem;">Mastered</span>
    <span style="color:#F39C12;font-size:0.75rem;">Partial</span>
    <span style="color:#E74C3C;font-size:0.75rem;">Knowledge Gap</span>
    <span style="color:#6B6B8D;font-size:0.75rem;">Not Assessed</span>
    <span style="color:#A0A0C0;font-size:0.75rem;margin-left:0.8rem;">Centre = Topic | Outer = Concepts</span>
</div>
""",
        unsafe_allow_html=True,
    )

    concept_fig = _build_concept_graph(chosen_topic, user_progress)
    if concept_fig:
        st.plotly_chart(concept_fig, use_container_width=True)
    else:
        st.info("Concept graph not available. Ensure the knowledge graph JSON is loaded correctly.")

    # ── Learning Path ──────────────────────────────────────────────────────────
    topic_data = user_progress.get(chosen_topic, {})
    gaps       = topic_data.get("knowledge_gaps", [])
    if gaps:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-weight:600;color:#FFFFFF;font-size:0.9rem;margin-bottom:0.6rem;">Recommended Learning Path (GraphRAG)</div>',
            unsafe_allow_html=True,
        )
        try:
            from backend.graph_rag import get_gap_recommendations
            recs = get_gap_recommendations(gaps[:3], chosen_topic)
            for rec in recs:
                path_nodes = rec["path"]
                path_html  = " &rarr; ".join(
                    f'<span style="background:rgba(108,99,255,0.1);border:1px solid rgba(108,99,255,0.2);'
                    f'border-radius:5px;padding:0.1rem 0.45rem;color:#8B83FF;font-size:0.75rem;">{p}</span>'
                    for p in path_nodes
                )
                st.markdown(
                    f'<div style="padding:0.55rem 0.9rem;margin-bottom:0.4rem;'
                    f'background:rgba(243,156,18,0.05);border-radius:9px;'
                    f'border-left:3px solid #F39C12;">'
                    f'<div style="color:#F39C12;font-size:0.75rem;font-weight:600;margin-bottom:0.25rem;">Gap: {rec["gap"]}</div>'
                    f'<div>{path_html}</div>'
                    f'<div style="color:#6B6B8D;font-size:0.68rem;margin-top:0.2rem;">{rec["recommendation"]}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
        except Exception:
            pass

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Topic-level knowledge graph ────────────────────────────────────────────
    st.markdown(
        '<div style="font-weight:700;color:#FFFFFF;font-size:1rem;margin-bottom:0.5rem;">Topic-Level Knowledge Graph</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div style="display:flex;gap:1.2rem;flex-wrap:wrap;margin-bottom:0.6rem;
            padding:0.5rem 0.9rem;background:rgba(255,255,255,0.02);
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

    st.plotly_chart(_build_topic_graph(user_progress), use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────────
    tab_bar, tab_radar = st.tabs(["Mastery Bar Chart", "Skill Radar"])
    with tab_bar:
        fig_bar = _build_bar(user_progress)
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Complete assessments to see mastery levels.")
    with tab_radar:
        st.plotly_chart(_build_radar(user_progress), use_container_width=True)

    # ── Detail table ────────────────────────────────────────────────────────────
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

    # ── Graph stats panel ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        from backend.knowledge_graph import get_graph_stats
        gstats = get_graph_stats()
        st.markdown(
            f"""
<div style="background:rgba(108,99,255,0.04);border:1px solid rgba(108,99,255,0.12);
            border-radius:10px;padding:0.8rem 1.2rem;">
    <div style="color:#8B83FF;font-weight:700;font-size:0.82rem;margin-bottom:0.5rem;">GraphRAG Knowledge Graph Statistics</div>
    <div style="display:flex;gap:2rem;flex-wrap:wrap;">
        <div><div style="color:#6B6B8D;font-size:0.65rem;">Total Nodes</div>
             <div style="color:#FFFFFF;font-weight:700;">{gstats["total_nodes"]}</div></div>
        <div><div style="color:#6B6B8D;font-size:0.65rem;">Total Edges</div>
             <div style="color:#FFFFFF;font-weight:700;">{gstats["total_edges"]}</div></div>
        <div><div style="color:#6B6B8D;font-size:0.65rem;">Topic Nodes</div>
             <div style="color:#FFFFFF;font-weight:700;">{gstats["num_topics"]}</div></div>
        <div><div style="color:#6B6B8D;font-size:0.65rem;">Concept Nodes</div>
             <div style="color:#FFFFFF;font-weight:700;">{gstats["num_concepts"]}</div></div>
        <div><div style="color:#6B6B8D;font-size:0.65rem;">Is DAG</div>
             <div style="color:{'#2ECC71' if gstats['is_dag'] else '#E74C3C'};font-weight:700;">{'Yes' if gstats['is_dag'] else 'No'}</div></div>
        <div><div style="color:#6B6B8D;font-size:0.65rem;">Density</div>
             <div style="color:#FFFFFF;font-weight:700;">{gstats["density"]}</div></div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    except Exception:
        pass
