"""
Knowledge Graph Module for Synapse AI Tutor.

Builds and manages a NetworkX-based knowledge graph of AI/ML topics and
concepts. Provides graph traversal, query expansion, and learning path
generation for GraphRAG retrieval.

Functions:
    build_knowledge_graph()   -- load/build the NetworkX graph
    expand_query()            -- expand a query using graph neighbours
    graph_learning_path()     -- find prerequisite study path for a concept
    get_concept_neighbours()  -- direct neighbour lookup
    concept_to_topic()        -- map a concept string to its parent topic
"""

import json
import os
import re
import networkx as nx
from functools import lru_cache

_GRAPH_JSON = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_graph.json"
)

# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_knowledge_graph() -> nx.DiGraph:
    """
    Load the knowledge graph from JSON and return a NetworkX DiGraph.

    The graph contains:
    * Topic nodes  (Neural Networks, Transformers, …)
    * Concept nodes (Self-Attention, Embeddings, …)
    * Directed edges with a 'relation' attribute
    """
    with open(_GRAPH_JSON, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    G = nx.DiGraph()

    for node in data["nodes"]:
        G.add_node(
            node["id"],
            node_type=node.get("type", "concept"),
            level=node.get("level", ""),
            topic=node.get("topic", ""),
        )

    for edge in data["edges"]:
        G.add_edge(
            edge["source"],
            edge["target"],
            relation=edge.get("relation", "related"),
        )

    return G


# Singleton – loaded once per process
@lru_cache(maxsize=1)
def _get_graph() -> nx.DiGraph:
    return build_knowledge_graph()


# ---------------------------------------------------------------------------
# Query expansion
# ---------------------------------------------------------------------------

def expand_query(question: str, topic: str, depth: int = 2) -> dict:
    """
    Expand a student question using the knowledge graph.

    Steps:
      1. Identify the best-matching concept node(s) in the question text.
      2. Collect neighbours up to *depth* hops in both directions.
      3. Return the expanded term list and metadata.

    Args:
        question: The raw student question string.
        topic:    The currently selected topic (used as anchor).
        depth:    How many hops from the matched concept(s) to include.

    Returns:
        {
            "original_query":   str,
            "expanded_query":   str,
            "matched_concepts": list[str],
            "neighbour_concepts": list[str],
            "expansion_path":   list[str],
        }
    """
    G = _get_graph()

    question_lower = question.lower()

    # 1. Match graph nodes whose names appear in the question
    matched = []
    for node in G.nodes():
        if node.lower() in question_lower:
            matched.append(node)

    # 2. Also include all concept nodes that belong to the selected topic
    topic_concepts = [
        n for n, d in G.nodes(data=True)
        if d.get("topic") == topic or n == topic
    ]

    if not matched:
        # Fall back to the topic node itself
        matched = [topic] if topic in G else []

    # 3. Collect neighbourhood
    neighbours = set()
    for concept in matched:
        if concept not in G:
            continue
        # Out-neighbours (concepts this concept leads to)
        for successor in nx.descendants(G, concept) if depth > 1 else G.successors(concept):
            neighbours.add(successor)
        # In-neighbours (prerequisites)
        for predecessor in G.predecessors(concept):
            neighbours.add(predecessor)

    # Remove the matched nodes themselves and pure topic nodes for cleaner terms
    expansion_concepts = list(neighbours - set(matched))
    expansion_concepts = [c for c in expansion_concepts if c != topic][:8]

    # 4. Build expanded query string
    all_terms = [question] + matched + expansion_concepts
    expanded_query = " ".join(dict.fromkeys(all_terms))  # dedup-preserving order

    return {
        "original_query":     question,
        "expanded_query":     expanded_query,
        "matched_concepts":   matched,
        "neighbour_concepts": expansion_concepts,
        "expansion_path":     matched + expansion_concepts,
    }


# ---------------------------------------------------------------------------
# Learning path
# ---------------------------------------------------------------------------

def graph_learning_path(concept: str, topic: str) -> list:
    """
    Return an ordered list of concepts the student should study to reach
    *concept* within *topic*.

    Uses shortest-path from the topic node to the concept node.
    If the concept is not directly reachable, falls back to prerequisite listing.

    Args:
        concept: Target concept string (e.g. "Self-Attention").
        topic:   The parent topic (e.g. "Transformers").

    Returns:
        List of concept/topic strings representing the study path.
    """
    G = _get_graph()

    if concept not in G:
        # Return prerequisite order from gap_detector data
        from backend.gap_detector import PREREQUISITE_MAP
        return PREREQUISITE_MAP.get(topic, {}).get("prerequisites", [])

    if topic not in G:
        return [concept]

    try:
        path = nx.shortest_path(G, source=topic, target=concept)
        return path
    except nx.NetworkXNoPath:
        # If no directed path, try undirected
        try:
            UG = G.to_undirected()
            path = nx.shortest_path(UG, source=topic, target=concept)
            return path
        except nx.NetworkXNoPath:
            return [topic, concept]
    except nx.NodeNotFound:
        return [concept]


# ---------------------------------------------------------------------------
# Neighbour lookup
# ---------------------------------------------------------------------------

def get_concept_neighbours(concept: str, max_hops: int = 1) -> list:
    """
    Return direct (1-hop) neighbours of a concept in the knowledge graph.

    Args:
        concept:  Node name.
        max_hops: Hop depth (1 = direct neighbours only).

    Returns:
        List of neighbour node names.
    """
    G = _get_graph()
    if concept not in G:
        return []

    if max_hops == 1:
        succs = list(G.successors(concept))
        preds = list(G.predecessors(concept))
        return list(dict.fromkeys(succs + preds))

    visited = set()
    frontier = {concept}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            next_frontier |= set(G.successors(node)) | set(G.predecessors(node))
        next_frontier -= visited | {concept}
        visited |= next_frontier
        frontier = next_frontier

    return list(visited)


# ---------------------------------------------------------------------------
# Concept → Topic resolution
# ---------------------------------------------------------------------------

def concept_to_topic(concept: str) -> str:
    """
    Return the parent topic for a given concept node.

    Args:
        concept: Concept name string.

    Returns:
        Topic string, or empty string if not found.
    """
    G = _get_graph()
    node_data = G.nodes.get(concept, {})
    topic = node_data.get("topic", "")
    if topic:
        return topic

    # Walk up in-edges to find a topic node
    for pred in G.predecessors(concept):
        pred_data = G.nodes.get(pred, {})
        if pred_data.get("node_type") == "topic":
            return pred
        # One more level
        for pred2 in G.predecessors(pred):
            if G.nodes.get(pred2, {}).get("node_type") == "topic":
                return pred2
    return ""


# ---------------------------------------------------------------------------
# Graph statistics (for UI display)
# ---------------------------------------------------------------------------

def get_graph_stats() -> dict:
    """Return summary statistics about the knowledge graph."""
    G = _get_graph()
    topics   = [n for n, d in G.nodes(data=True) if d.get("node_type") == "topic"]
    concepts = [n for n, d in G.nodes(data=True) if d.get("node_type") == "concept"]
    return {
        "total_nodes":    G.number_of_nodes(),
        "total_edges":    G.number_of_edges(),
        "num_topics":     len(topics),
        "num_concepts":   len(concepts),
        "is_dag":         nx.is_directed_acyclic_graph(G),
        "density":        round(nx.density(G), 4),
    }


def get_all_concepts_for_topic(topic: str) -> list:
    """Return all concept nodes belonging to a given topic."""
    G = _get_graph()
    return [
        n for n, d in G.nodes(data=True)
        if d.get("topic") == topic or (
            d.get("node_type") == "topic" and n == topic
        )
    ]


def get_topic_subgraph(topic: str) -> nx.DiGraph:
    """Return the induced subgraph containing the topic and all its concepts."""
    G   = _get_graph()
    nodes = [topic] + get_all_concepts_for_topic(topic)
    valid = [n for n in nodes if n in G]
    return G.subgraph(valid).copy()
