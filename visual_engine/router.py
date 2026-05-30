"""
Router — generate_visualization(payload)
Routes topic+operation to the correct visualizer module.
If no hardcoded visualizer exists, falls back to LLM-generated code via Groq.
Returns a list of frame dicts (image + caption).
"""
from visualizers import linked_list, binary_search, recursion, transformer, neural_network, rag_pipeline


# graph_renderer kept for future Graphviz-based visualizers — import lazily
def _render_graphviz(dot_graph):
    try:
        from renderers.graph_renderer import render_graphviz_to_pil
        return render_graphviz_to_pil(dot_graph)
    except Exception as e:
        raise RuntimeError(
            "Graphviz binary not found. Install from https://graphviz.org/download/ "
            "and add to PATH."
        ) from e


# ── topic aliases ─────────────────────────────────────────────────────────────
TOPIC_MAP = {
    # linked list
    "linked_list": "linked_list",
    "linkedlist": "linked_list",
    "reverse_linked_list": "linked_list",
    "reverse linked list": "linked_list",
    # binary search
    "binary_search": "binary_search",
    "binarysearch": "binary_search",
    "binary search": "binary_search",
    # recursion
    "recursion": "recursion",
    "factorial": "recursion",
    "fibonacci": "recursion",
    # transformer
    "transformer": "transformer",
    "attention": "transformer",
    "self_attention": "transformer",
    "transformer_attention": "transformer",
    "transformer attention": "transformer",
    # neural network
    "neural_network": "neural_network",
    "neuralnetwork": "neural_network",
    "neural network": "neural_network",
    "nn": "neural_network",
    # rag
    "rag": "rag_pipeline",
    "rag_pipeline": "rag_pipeline",
    "rag pipeline": "rag_pipeline",
    "retrieval": "rag_pipeline",
}


def _normalise_frames(raw_frames: list[dict]) -> list[dict]:
    """
    Ensure every frame has {'image': PIL.Image, 'caption': str}.
    Graphviz frames arrive with 'graph' key; render them here.
    """
    normalised = []
    for f in raw_frames:
        if "image" in f:
            normalised.append({"image": f["image"], "caption": f.get("caption", "")})
        elif "graph" in f:
            pil = _render_graphviz(f["graph"])
            normalised.append({"image": pil, "caption": f.get("caption", "")})
        else:
            continue
    return normalised


def _fallback_frames(payload: dict) -> list[dict]:
    """Return a single explanatory frame for unsupported topics (no API key)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import io
    from PIL import Image

    topic = payload.get("topic", "unknown")
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    ax.axis("off")
    ax.text(0.5, 0.65, f"⚠️  No visualizer for: '{topic}'", ha="center", va="center",
            fontsize=14, color="#f59e0b", fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.45,
            "To enable AI-generated visualizations for ANY topic:\n"
            "Set your GROQ_API_KEY in the sidebar or environment.",
            ha="center", va="center", fontsize=11, color="#9ca3af",
            fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.25,
            "Pre-built: linked_list · binary_search · recursion\n"
            "           transformer · neural_network · rag_pipeline",
            ha="center", va="center", fontsize=10, color="#64748b",
            fontfamily="monospace", transform=ax.transAxes)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="#0f1117")
    buf.seek(0)
    img = Image.open(buf).copy()
    plt.close(fig)
    return [{"image": img, "caption": f"Topic '{topic}' requires a GROQ_API_KEY for AI generation."}]


def _llm_generating_frames(payload: dict) -> list[dict]:
    """Return a 'generating...' placeholder frame."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import io
    from PIL import Image

    topic = payload.get("topic", "unknown")
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    ax.axis("off")
    ax.text(0.5, 0.55, f"🤖 AI is generating visualization for:\n'{topic}'",
            ha="center", va="center", fontsize=13, color="#a855f7",
            fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.3, "Powered by Llama 3.3 70B via Groq",
            ha="center", va="center", fontsize=10, color="#64748b",
            fontfamily="monospace", transform=ax.transAxes)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="#0f1117")
    buf.seek(0)
    img = Image.open(buf).copy()
    plt.close(fig)
    return [{"image": img, "caption": f"Generating AI visualization for '{topic}'..."}]


def generate_visualization(payload: dict) -> list[dict]:
    """
    Main entry point.

    Flow:
      1. Check if topic matches a hardcoded visualizer → use it (fast)
      2. Else → attempt LLM generation via Groq (any topic)
      3. Else → graceful fallback frame

    Parameters
    ----------
    payload : dict
        Keys: topic, operation, level, language, (+ visualizer-specific keys)

    Returns
    -------
    list[dict]
        Each dict: {'image': PIL.Image.Image, 'caption': str}
    """
    raw_topic = str(payload.get("topic", "")).lower().strip()
    canonical = TOPIC_MAP.get(raw_topic)

    # ── 1. Hardcoded visualizer ────────────────────────────────────────────
    if canonical is not None:
        if canonical == "linked_list":
            raw = linked_list.generate_frames(payload)
        elif canonical == "binary_search":
            raw = binary_search.generate_frames(payload)
        elif canonical == "recursion":
            raw = recursion.generate_frames(payload)
        elif canonical == "transformer":
            raw = transformer.generate_frames(payload)
        elif canonical == "neural_network":
            raw = neural_network.generate_frames(payload)
        elif canonical == "rag_pipeline":
            raw = rag_pipeline.generate_frames(payload)
        else:
            raw = None

        if raw:
            return _normalise_frames(raw)

    # ── 2. LLM-generated visualization (any topic) ─────────────────────────
    try:
        from generators.llm_generator import generate_with_llm, is_available
        import traceback

        available = is_available()
        print(f"[Router] LLM available: {available}, topic: '{raw_topic}'")

        if available:
            print(f"[Router] Calling LLM for topic: '{raw_topic}'")
            llm_frames = generate_with_llm(payload)
            if llm_frames and len(llm_frames) > 0:
                print(f"[Router] LLM generated {len(llm_frames)} frames successfully")
                return _normalise_frames(llm_frames)
            else:
                print(f"[Router] LLM returned empty/None frames")
        else:
            print("[Router] LLM not available — GROQ_API_KEY missing or groq not installed")
    except Exception as e:
        import traceback
        print(f"[Router] LLM generation failed: {e}")
        traceback.print_exc()

    # ── 3. Fallback ────────────────────────────────────────────────────────
    return _fallback_frames(payload)
