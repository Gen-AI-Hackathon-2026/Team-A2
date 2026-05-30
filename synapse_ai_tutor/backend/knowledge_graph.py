"""
Knowledge Graph Builder for Synapse AI Tutor.
Constructs interactive knowledge graph visualizations using Cytoscape.js.
Shows prerequisite relationships, mastery levels, and connected concepts.
Rendered via CDN — zero pip dependencies required.
"""

from backend.gap_detector import PREREQUISITE_MAP
from backend.progress_tracker import get_user_progress


# ── Color Constants ───────────────────────────────────────────────────────────

MASTERY_COLORS = {
    "mastered": "#2ECC71",       # Green — mastery >= 76
    "in_progress": "#F39C12",    # Yellow/Orange — mastery 1-75
    "not_started": "#3A3A5C",    # Dark grey — mastery 0
    "prerequisite": "#6B6B8D",   # Lighter grey — prerequisite concepts
}


# ── Graph Data Builders ──────────────────────────────────────────────────────

def build_full_graph(username: str = None) -> dict:
    """
    Build the full curriculum knowledge graph.

    Returns:
        dict with:
            "nodes": [{"id", "label", "mastery", "level", "group", ...}]
            "edges": [{"source", "target", "label", ...}]
    """
    user_progress = {}
    if username:
        user_progress = get_user_progress(username)

    nodes = []
    edges = []
    seen_nodes = set()

    # Add all main topics
    for topic, data in PREREQUISITE_MAP.items():
        progress = user_progress.get(topic, {})
        mastery = progress.get("mastery", 0)
        level = progress.get("level", "Not Assessed")

        nodes.append({
            "id": _safe_id(topic),
            "label": topic,
            "mastery": mastery,
            "level": level,
            "group": "main",
        })
        seen_nodes.add(topic)

        # Add prerequisite edges
        for prereq in data.get("prerequisites", []):
            edges.append({
                "source": _safe_id(prereq),
                "target": _safe_id(topic),
                "label": "requires",
                "type": "prerequisite",
            })

            # Add prerequisite as node if not yet added
            if prereq not in seen_nodes:
                nodes.append({
                    "id": _safe_id(prereq),
                    "label": prereq,
                    "mastery": 0,
                    "level": "Prerequisite",
                    "group": "prerequisite",
                })
                seen_nodes.add(prereq)

        # Add related topic edges
        for related in data.get("related_topics", []):
            edges.append({
                "source": _safe_id(topic),
                "target": _safe_id(related),
                "label": "related",
                "type": "related",
            })

    return {"nodes": nodes, "edges": edges}


def build_topic_graph(topic: str, username: str = None) -> dict:
    """
    Build a focused knowledge graph for a single topic.
    Shows the topic + its prerequisites + related topics + key concepts.

    Args:
        topic: The specific topic to focus on
        username: Optional username for mastery coloring

    Returns:
        dict with "nodes" and "edges"
    """
    user_progress = {}
    if username:
        user_progress = get_user_progress(username)

    topic_data = PREREQUISITE_MAP.get(topic, {})
    if not topic_data:
        return {"nodes": [], "edges": []}

    nodes = []
    edges = []
    seen = set()

    # Central topic node
    progress = user_progress.get(topic, {})
    mastery = progress.get("mastery", 0)
    level = progress.get("level", "Not Assessed")
    nodes.append({
        "id": _safe_id(topic), "label": topic,
        "mastery": mastery, "level": level, "group": "main",
    })
    seen.add(topic)

    # Prerequisites
    for prereq in topic_data.get("prerequisites", []):
        if prereq not in seen:
            nodes.append({
                "id": _safe_id(prereq), "label": prereq,
                "mastery": 0, "level": "Prerequisite", "group": "prerequisite",
            })
            seen.add(prereq)
        edges.append({
            "source": _safe_id(prereq), "target": _safe_id(topic),
            "label": "requires", "type": "prerequisite",
        })

    # Key concepts
    for concept in topic_data.get("key_concepts", []):
        if concept not in seen:
            nodes.append({
                "id": _safe_id(concept), "label": concept,
                "mastery": 0, "level": "Concept", "group": "concept",
            })
            seen.add(concept)
        edges.append({
            "source": _safe_id(topic), "target": _safe_id(concept),
            "label": "teaches", "type": "concept",
        })

    # Related topics
    for related in topic_data.get("related_topics", []):
        if related not in seen:
            r_progress = user_progress.get(related, {})
            nodes.append({
                "id": _safe_id(related), "label": related,
                "mastery": r_progress.get("mastery", 0),
                "level": r_progress.get("level", "Not Assessed"),
                "group": "related",
            })
            seen.add(related)
        edges.append({
            "source": _safe_id(topic), "target": _safe_id(related),
            "label": "related", "type": "related",
        })

    return {"nodes": nodes, "edges": edges}


def _safe_id(name: str) -> str:
    """Convert a topic name to a safe CSS-compatible ID."""
    return name.lower().replace(" ", "_").replace("&", "and").replace("/", "_").replace("(", "").replace(")", "").replace(",", "")


# ── Cytoscape.js HTML Generation ─────────────────────────────────────────────

def generate_cytoscape_html(username: str = None, height: str = "650px", graph_data: dict = None) -> str:
    """
    Generate a self-contained HTML page with an interactive Cytoscape.js graph.
    Loads Cytoscape + layout extensions from CDN. Zero pip dependencies.

    Args:
        username: Optional username for mastery coloring
        height: CSS height of the graph container
        graph_data: Optional pre-built graph data dict. If None, builds full graph.

    Returns:
        HTML string to embed via st.components.v1.html()
    """
    if graph_data is None:
        graph_data = build_full_graph(username)

    # Build Cytoscape elements array
    elements_js = _build_elements_js(graph_data)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
    <script src="https://unpkg.com/layout-base@2.0.1/layout-base.js"></script>
    <script src="https://unpkg.com/cose-base@2.2.0/cose-base.js"></script>
    <script src="https://unpkg.com/cytoscape-cose-bilkent@4.1.0/cytoscape-cose-bilkent.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #0A0A1A; overflow: hidden; font-family: 'Inter', -apple-system, sans-serif; }}
        #cy {{
            width: 100%;
            height: {height};
            border: 1px solid rgba(108,99,255,0.15);
            border-radius: 16px;
            background: radial-gradient(ellipse at center, #12122A 0%, #0A0A1A 100%);
        }}
        #tooltip {{
            position: absolute;
            display: none;
            background: rgba(20, 20, 46, 0.95);
            border: 1px solid rgba(108,99,255,0.3);
            border-radius: 10px;
            padding: 10px 14px;
            color: #FFFFFF;
            font-size: 12px;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            pointer-events: none;
            z-index: 1000;
            max-width: 220px;
            backdrop-filter: blur(10px);
        }}
        #tooltip .tt-title {{ font-weight: 700; font-size: 13px; margin-bottom: 4px; }}
        #tooltip .tt-mastery {{ color: #00D2FF; font-size: 11px; }}
        #tooltip .tt-level {{ color: #A0A0C0; font-size: 11px; }}
        #controls {{
            position: absolute;
            top: 12px;
            right: 16px;
            display: flex;
            gap: 6px;
            z-index: 100;
        }}
        .ctrl-btn {{
            background: rgba(20, 20, 46, 0.85);
            border: 1px solid rgba(108,99,255,0.2);
            color: #A0A0C0;
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 11px;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s;
            backdrop-filter: blur(8px);
        }}
        .ctrl-btn:hover {{ background: rgba(108,99,255,0.2); color: #FFFFFF; border-color: rgba(108,99,255,0.4); }}
    </style>
</head>
<body>
    <div style="position:relative;">
        <div id="cy"></div>
        <div id="tooltip"></div>
        <div id="controls">
            <button class="ctrl-btn" onclick="cy.fit(40)">Fit</button>
            <button class="ctrl-btn" onclick="cy.zoom(cy.zoom()*1.3); cy.center()">+</button>
            <button class="ctrl-btn" onclick="cy.zoom(cy.zoom()*0.7); cy.center()">−</button>
            <button class="ctrl-btn" onclick="resetHighlight()">Reset</button>
        </div>
    </div>

    <script>
        var cy = cytoscape({{
            container: document.getElementById('cy'),
            elements: {elements_js},
            style: [
                {{
                    selector: 'node[group="main"]',
                    style: {{
                        'label': 'data(label)',
                        'width': 'mapData(mastery, 0, 100, 38, 65)',
                        'height': 'mapData(mastery, 0, 100, 38, 65)',
                        'background-color': function(ele) {{
                            var m = ele.data('mastery');
                            if (m >= 76) return '#2ECC71';
                            if (m > 0) return '#F39C12';
                            return '#3A3A5C';
                        }},
                        'border-width': 2.5,
                        'border-color': function(ele) {{
                            var m = ele.data('mastery');
                            if (m >= 76) return '#27AE60';
                            if (m > 0) return '#E67E22';
                            return '#2A2A4A';
                        }},
                        'color': '#FFFFFF',
                        'font-size': '10px',
                        'font-family': 'Inter, sans-serif',
                        'font-weight': '600',
                        'text-valign': 'bottom',
                        'text-margin-y': 8,
                        'text-wrap': 'wrap',
                        'text-max-width': '90px',
                        'text-outline-color': '#0A0A1A',
                        'text-outline-width': 2,
                        'shadow-blur': 15,
                        'shadow-color': function(ele) {{
                            var m = ele.data('mastery');
                            if (m >= 76) return 'rgba(46,204,113,0.4)';
                            if (m > 0) return 'rgba(243,156,18,0.3)';
                            return 'rgba(0,0,0,0.2)';
                        }},
                        'shadow-offset-x': 0,
                        'shadow-offset-y': 0,
                        'shadow-opacity': 1,
                        'overlay-opacity': 0,
                    }}
                }},
                {{
                    selector: 'node[group="prerequisite"]',
                    style: {{
                        'label': 'data(label)',
                        'width': 22,
                        'height': 22,
                        'background-color': '#6B6B8D',
                        'border-width': 1,
                        'border-color': '#4A4A6A',
                        'color': '#8888AA',
                        'font-size': '8px',
                        'font-family': 'Inter, sans-serif',
                        'text-valign': 'bottom',
                        'text-margin-y': 6,
                        'text-wrap': 'wrap',
                        'text-max-width': '75px',
                        'text-outline-color': '#0A0A1A',
                        'text-outline-width': 1.5,
                        'overlay-opacity': 0,
                    }}
                }},
                {{
                    selector: 'node[group="concept"]',
                    style: {{
                        'label': 'data(label)',
                        'width': 28,
                        'height': 28,
                        'background-color': '#2ECC71',
                        'border-width': 2,
                        'border-color': '#27AE60',
                        'color': '#FFFFFF',
                        'font-size': '9px',
                        'font-family': 'Inter, sans-serif',
                        'font-weight': '500',
                        'text-valign': 'bottom',
                        'text-margin-y': 7,
                        'text-wrap': 'wrap',
                        'text-max-width': '85px',
                        'text-outline-color': '#0A0A1A',
                        'text-outline-width': 1.5,
                        'shadow-blur': 10,
                        'shadow-color': 'rgba(46,204,113,0.3)',
                        'shadow-offset-x': 0,
                        'shadow-offset-y': 0,
                        'shadow-opacity': 1,
                        'overlay-opacity': 0,
                    }}
                }},
                {{
                    selector: 'node[group="related"]',
                    style: {{
                        'label': 'data(label)',
                        'width': 30,
                        'height': 30,
                        'background-color': '#00D2FF',
                        'border-width': 2,
                        'border-color': '#0099CC',
                        'color': '#FFFFFF',
                        'font-size': '9px',
                        'font-family': 'Inter, sans-serif',
                        'font-weight': '500',
                        'text-valign': 'bottom',
                        'text-margin-y': 7,
                        'text-wrap': 'wrap',
                        'text-max-width': '85px',
                        'text-outline-color': '#0A0A1A',
                        'text-outline-width': 1.5,
                        'shadow-blur': 10,
                        'shadow-color': 'rgba(0,210,255,0.3)',
                        'shadow-offset-x': 0,
                        'shadow-offset-y': 0,
                        'shadow-opacity': 1,
                        'overlay-opacity': 0,
                    }}
                }},
                {{
                    selector: 'edge[type="prerequisite"]',
                    style: {{
                        'width': 1.5,
                        'line-color': 'rgba(108, 99, 255, 0.35)',
                        'target-arrow-color': 'rgba(108, 99, 255, 0.5)',
                        'target-arrow-shape': 'triangle',
                        'arrow-scale': 0.8,
                        'curve-style': 'bezier',
                        'opacity': 0.7,
                    }}
                }},
                {{
                    selector: 'edge[type="related"]',
                    style: {{
                        'width': 1,
                        'line-color': 'rgba(0, 210, 255, 0.25)',
                        'line-style': 'dashed',
                        'target-arrow-shape': 'none',
                        'curve-style': 'bezier',
                        'opacity': 0.5,
                    }}
                }},
                {{
                    selector: 'edge[type="concept"]',
                    style: {{
                        'width': 1.2,
                        'line-color': 'rgba(46, 204, 113, 0.35)',
                        'target-arrow-color': 'rgba(46, 204, 113, 0.5)',
                        'target-arrow-shape': 'triangle',
                        'arrow-scale': 0.7,
                        'curve-style': 'bezier',
                        'opacity': 0.6,
                    }}
                }},
                /* Highlight states */
                {{
                    selector: 'node.highlighted',
                    style: {{
                        'border-color': '#6C63FF',
                        'border-width': 4,
                        'shadow-blur': 25,
                        'shadow-color': 'rgba(108,99,255,0.6)',
                        'z-index': 10,
                    }}
                }},
                {{
                    selector: 'node.faded',
                    style: {{
                        'opacity': 0.15,
                    }}
                }},
                {{
                    selector: 'edge.highlighted',
                    style: {{
                        'width': 3,
                        'opacity': 1,
                        'line-color': '#6C63FF',
                        'target-arrow-color': '#6C63FF',
                    }}
                }},
                {{
                    selector: 'edge.faded',
                    style: {{
                        'opacity': 0.06,
                    }}
                }},
            ],
            layout: {{
                name: 'cose-bilkent',
                quality: 'proof',
                nodeDimensionsIncludeLabels: true,
                idealEdgeLength: 160,
                nodeRepulsion: 6500,
                edgeElasticity: 0.45,
                nestingFactor: 0.1,
                gravity: 0.35,
                gravityRange: 3.8,
                numIter: 2500,
                tile: true,
                animate: 'end',
                animationDuration: 800,
                animationEasing: 'ease-out-cubic',
                fit: true,
                padding: 40,
                randomize: true,
            }},
            minZoom: 0.3,
            maxZoom: 3,
            wheelSensitivity: 0.3,
        }});

        // ── Tooltip ──────────────────────────────────────────────────────────
        var tooltip = document.getElementById('tooltip');

        cy.on('mouseover', 'node', function(e) {{
            var node = e.target;
            var d = node.data();
            var masteryColor = d.mastery >= 76 ? '#2ECC71' : (d.mastery > 0 ? '#F39C12' : '#6B6B8D');
            tooltip.innerHTML = '<div class="tt-title">' + d.label + '</div>'
                + '<div class="tt-mastery" style="color:' + masteryColor + '">Mastery: ' + d.mastery + '%</div>'
                + '<div class="tt-level">Level: ' + d.level + '</div>'
                + '<div class="tt-level">Group: ' + d.group + '</div>';
            tooltip.style.display = 'block';

            var pos = e.renderedPosition || e.cyRenderedPosition;
            tooltip.style.left = (pos.x + 15) + 'px';
            tooltip.style.top = (pos.y - 10) + 'px';
        }});

        cy.on('mouseout', 'node', function() {{
            tooltip.style.display = 'none';
        }});

        cy.on('mousemove', 'node', function(e) {{
            var pos = e.renderedPosition || e.cyRenderedPosition;
            tooltip.style.left = (pos.x + 15) + 'px';
            tooltip.style.top = (pos.y - 10) + 'px';
        }});

        // ── Click to highlight neighbors ─────────────────────────────────────
        cy.on('tap', 'node', function(e) {{
            var node = e.target;
            var neighborhood = node.closedNeighborhood();

            cy.elements().addClass('faded');
            neighborhood.removeClass('faded');
            node.addClass('highlighted');
            neighborhood.edges().addClass('highlighted');
            neighborhood.nodes().removeClass('faded');
        }});

        cy.on('tap', function(e) {{
            if (e.target === cy) {{
                resetHighlight();
            }}
        }});

        function resetHighlight() {{
            cy.elements().removeClass('faded highlighted');
        }}
    </script>
</body>
</html>"""


def _build_elements_js(graph_data: dict) -> str:
    """Build the Cytoscape.js elements JSON array."""
    elements = []

    for node in graph_data["nodes"]:
        elements.append({
            "data": {
                "id": node["id"],
                "label": node["label"],
                "mastery": node["mastery"],
                "level": node["level"],
                "group": node["group"],
            }
        })

    for edge in graph_data["edges"]:
        elements.append({
            "data": {
                "source": edge["source"],
                "target": edge["target"],
                "label": edge["label"],
                "type": edge["type"],
            }
        })

    import json
    return json.dumps(elements)


# ── Graph Statistics ──────────────────────────────────────────────────────────

def get_graph_stats(username: str = None) -> dict:
    """Get statistics about the knowledge graph."""
    graph_data = build_full_graph(username)

    main_nodes = [n for n in graph_data["nodes"] if n["group"] == "main"]
    prereq_nodes = [n for n in graph_data["nodes"] if n["group"] == "prerequisite"]
    mastered = [n for n in main_nodes if n["mastery"] >= 76]
    in_progress = [n for n in main_nodes if 0 < n["mastery"] < 76]

    return {
        "total_nodes": len(graph_data["nodes"]),
        "main_topics": len(main_nodes),
        "prerequisites": len(prereq_nodes),
        "total_edges": len(graph_data["edges"]),
        "mastered": len(mastered),
        "in_progress": len(in_progress),
        "not_started": len(main_nodes) - len(mastered) - len(in_progress),
    }
