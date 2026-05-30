"""
LLM-Powered Visualization Generator
Calls Groq API to generate Matplotlib visualization code for any topic.
Falls back gracefully if API is unavailable.
"""
import io
import os
import re
import traceback
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from PIL import Image


# ── Groq client setup ─────────────────────────────────────────────────────────
def _load_env():
    """Load .env file from visual_engine directory if present."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_env()

def _get_groq_client():
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            print("[LLM-Gen] No API key found — set GROQ_API_KEY in .env or sidebar")
            return None
        return Groq(api_key=api_key)
    except ImportError as e:
        print(f"[LLM-Gen] groq package not installed: {e}")
        return None


# ── System prompt — instructs the LLM what code to generate ───────────────────

SYSTEM_PROMPT = textwrap.dedent("""\
You are an expert educational visualization engineer.

Your task: write a SINGLE Python function called `generate_frames(payload)` that creates
step-by-step animated educational frames for the given topic.

## Rules — STRICT
1. The function MUST be named `generate_frames` and accept one dict argument `payload`.
2. It MUST return a Python list of dicts. Each dict MUST have:
   - "image": a PIL.Image.Image (RGB) created via matplotlib
   - "caption": a string explaining that step (educational, beginner-friendly)
3. Return at LEAST 4 frames and at MOST 12 frames.
4. Use a dark theme: figure background "#0f1117", axes background "#0f1117".
5. Use these colors: blue="#3b82f6", purple="#a855f7", amber="#f59e0b",
   green="#22c55e", pink="#ec4899", text="#e2e8f0".
6. Use monospace fonts: fontfamily="monospace".
7. Each frame should show a DIFFERENT step/stage of the concept — animate progression.
8. Make it educational: a student should LEARN the concept from these frames.

## Available imports (ALREADY imported for you, do NOT re-import):
- matplotlib.pyplot as plt
- matplotlib.patches as mpatches
- numpy as np
- PIL.Image as Image
- io

## Helper function (ALREADY defined, use it):
```python
def _fig_to_pil(fig) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    img = Image.open(buf).copy()
    plt.close(fig)
    return img
```

## Output format
Write ONLY the function body. No imports. No markdown fences. No explanation text.
Start directly with `def generate_frames(payload):`.
""")


def _build_user_prompt(payload: dict) -> str:
    topic = payload.get("topic", "unknown")
    operation = payload.get("operation", "explain")
    level = payload.get("level", "beginner")

    return textwrap.dedent(f"""\
    Create an animated, step-by-step visualization for:

    Topic: {topic}
    Operation/Focus: {operation}
    Student Level: {level}

    The visualization should teach this concept visually with progressive frames.
    Each frame must build on the previous one.
    Use clear labels, annotations, and color-coding.
    Make the captions educational — explain WHAT is happening and WHY at each step.

    Write the generate_frames(payload) function now.
    """)


# ── Code execution sandbox ────────────────────────────────────────────────────

def _fig_to_pil(fig) -> Image.Image:
    """Helper that generated code can use to convert figures to PIL images."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    img = Image.open(buf).copy()
    plt.close(fig)
    return img


# Allowed names in the exec sandbox — nothing dangerous
_SAFE_GLOBALS = {
    "__builtins__": {
        "range": range, "len": len, "int": int, "float": float,
        "str": str, "list": list, "dict": dict, "tuple": tuple,
        "enumerate": enumerate, "zip": zip, "map": map,
        "max": max, "min": min, "sum": sum, "abs": abs,
        "round": round, "sorted": sorted, "reversed": reversed,
        "True": True, "False": False, "None": None,
        "print": print, "isinstance": isinstance, "type": type,
        "ValueError": ValueError, "TypeError": TypeError,
        "Exception": Exception,
    },
    "plt": plt,
    "mpatches": mpatches,
    "np": np,
    "Image": Image,
    "io": io,
    "_fig_to_pil": _fig_to_pil,
    "matplotlib": matplotlib,
}


def _extract_code(raw_response: str) -> str:
    """Strip markdown fences and extract just the Python code."""
    # Remove ```python ... ``` wrapping if present
    code = raw_response.strip()
    code = re.sub(r'^```(?:python)?\s*\n?', '', code)
    code = re.sub(r'\n?```\s*$', '', code)
    return code.strip()


def _execute_generated_code(code: str, payload: dict) -> list[dict] | None:
    """
    Execute LLM-generated code in a sandboxed namespace.
    Returns list of frame dicts or None on failure.
    """
    namespace = dict(_SAFE_GLOBALS)

    try:
        exec(code, namespace)
    except Exception as e:
        print(f"[LLM-Gen] Code exec error: {e}")
        traceback.print_exc()
        return None

    gen_func = namespace.get("generate_frames")
    if gen_func is None or not callable(gen_func):
        print("[LLM-Gen] No generate_frames function found in output")
        return None

    try:
        frames = gen_func(payload)
    except Exception as e:
        print(f"[LLM-Gen] Frame generation error: {e}")
        traceback.print_exc()
        return None

    # Validate output shape
    if not isinstance(frames, list) or len(frames) == 0:
        print("[LLM-Gen] Invalid output: not a list or empty")
        return None

    for f in frames:
        if not isinstance(f, dict) or "image" not in f:
            print(f"[LLM-Gen] Invalid frame format: {type(f)}")
            return None

    return frames


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_with_llm(payload: dict) -> list[dict] | None:
    """
    Generate visualization frames for any topic using Groq LLM.

    Returns list of {'image': PIL.Image, 'caption': str} or None on failure.
    """
    client = _get_groq_client()
    if client is None:
        return None

    user_prompt = _build_user_prompt(payload)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
            top_p=0.9,
        )
        raw_code = response.choices[0].message.content
    except Exception as e:
        print(f"[LLM-Gen] Groq API error: {e}")
        return None

    code = _extract_code(raw_code)

    if not code or "generate_frames" not in code:
        print("[LLM-Gen] LLM response did not contain generate_frames function")
        return None

    return _execute_generated_code(code, payload)


def is_available() -> bool:
    """Check if LLM generation is available (API key set + groq installed)."""
    return _get_groq_client() is not None
