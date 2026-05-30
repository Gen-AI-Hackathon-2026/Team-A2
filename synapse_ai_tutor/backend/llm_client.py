"""
LLM Client for Synapse AI Tutor.
Connects to GPT-OSS 20B running on MacBook M4 via Ollama.
Enhanced with full adaptive prompting and graceful fallback mode.
"""

import requests

# Ollama endpoint on MacBook M4
OLLAMA_BASE_URL = "http://192.168.29.145:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"

# Model name
DEFAULT_MODEL = "gpt-oss:20b"

# Connection timeout (seconds)
CONNECT_TIMEOUT = 5
GENERATE_TIMEOUT = 120


def check_connection() -> bool:
    """Check if the Ollama server is reachable."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=CONNECT_TIMEOUT)
        return response.status_code == 200
    except Exception:
        return False


def get_available_models() -> list:
    """Get list of available models on the Ollama server."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=CONNECT_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    return []


def generate_response(
    prompt: str,
    system_prompt: str = None,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> str:
    """
    Generate a response from the LLM.
    Returns generated text or an error/fallback message string.
    """
    if model is None:
        model = DEFAULT_MODEL

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        response = requests.post(
            OLLAMA_CHAT_URL,
            json=payload,
            timeout=GENERATE_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("message", {}).get("content", "No response generated.")
        else:
            return f"__LLM_ERROR__: Server returned status {response.status_code}"

    except requests.exceptions.ConnectionError:
        return "__LLM_OFFLINE__"
    except requests.exceptions.Timeout:
        return "__LLM_TIMEOUT__"
    except Exception as e:
        return f"__LLM_ERROR__: {str(e)}"


def generate_tutoring_response(
    topic: str,
    level: str,
    knowledge_gaps: list,
    retrieved_chunks: list,
    student_question: str,
    mastery: int = 0,
    model: str = None,
    # ── Digital Twin injection (optional) — from student_memory.py —————————
    weak_topics: list | None = None,
    strong_topics: list | None = None,
    recent_mistakes: list | None = None,
    recent_context: list | None = None,
) -> dict:
    """
    Generate a comprehensive adaptive tutoring response.

    Injects topic, level, mastery, and knowledge gaps into the prompt.
    Falls back gracefully to RAG-only content if LLM is unavailable.

    Returns:
        dict with keys: explanation, analogy, example, practice_questions,
                        full_response, sources, llm_available, fallback_used
    """
    # Build context from retrieved chunks (always available)
    context_text = ""
    sources = []
    for i, chunk in enumerate(retrieved_chunks[:5], 1):
        context_text += f"\n--- Source {i}: {chunk['source']} (Page {chunk['page']}) ---\n"
        context_text += chunk['text'] + "\n"
        sources.append({
            "source": chunk['source'],
            "page": chunk['page'],
            "text": chunk['text'][:300]
        })

    # Level-adaptive system prompt
    level_instructions = _get_level_instructions(level)

    gaps_text = ""
    if knowledge_gaps:
        gaps_text = f"\nKnowledge Gaps to Address: {', '.join(knowledge_gaps[:6])}\n"

    mastery_text = f"\nCurrent Mastery: {mastery}%" if mastery > 0 else ""

    # ── Digital Twin section (only injected when data is available) ———————
    twin_lines: list[str] = []
    if weak_topics:
        twin_lines.append(
            f"Weak Topics (needs more reinforcement): {', '.join(weak_topics)}"
        )
    if strong_topics:
        twin_lines.append(
            f"Strong Topics (already mastered): {', '.join(strong_topics)}"
        )
    if recent_mistakes:
        twin_lines.append(
            f"Past Struggles (previously got wrong): {', '.join(recent_mistakes)}"
        )
    twin_section = (
        "\n=== Student Digital Twin ===\n" + "\n".join(twin_lines) + "\n"
        if twin_lines else ""
    )

    # ── Recent conversation context (last 4 turns) ——————————————————
    context_section = ""
    if recent_context:
        ctx_lines: list[str] = []
        for msg in recent_context[-4:]:
            speaker = "Student" if msg.get("role") == "user" else "Tutor"
            snippet = msg.get("content", "")[:200].replace("\n", " ")
            ctx_lines.append(f"{speaker}: {snippet}")
        if ctx_lines:
            context_section = (
                "\n=== Recent Conversation Context ===\n"
                + "\n".join(ctx_lines)
                + "\n"
            )

    system_prompt = f"""You are Synapse, an expert adaptive AI tutor.

=== Student Profile ===
Topic: {topic}
Level: {level}{mastery_text}{gaps_text}{twin_section}{context_section}

=== Adaptive Teaching Rules ===
{level_instructions}

=== Reference Material (from textbooks) ===
{context_text if context_text else "No textbook content retrieved for this query."}

=== Response Structure ===
Your response MUST include these four sections with exact headers:

## Explanation
A clear, level-appropriate explanation of the concept.

## Analogy
A relatable real-world analogy that makes the concept intuitive.

## Worked Example
A concrete step-by-step example (include code or math where appropriate for the level).

## Practice Questions
2-3 practice questions the student can answer to test understanding.

Be thorough, encouraging, and fully adapted to {level} level."""

    raw = generate_response(
        prompt=student_question,
        system_prompt=system_prompt,
        model=model,
        temperature=0.7,
        max_tokens=3000
    )

    # ── Fallback Handling ────────────────────────────────────────────────────
    fallback_used = False
    llm_available = True

    if raw.startswith("__LLM_OFFLINE__") or raw.startswith("__LLM_TIMEOUT__") or raw.startswith("__LLM_ERROR__"):
        llm_available = False
        fallback_used = True
        raw = _build_fallback_response(topic, level, knowledge_gaps, retrieved_chunks, student_question, raw)

    result = _parse_tutoring_response(raw)
    result["raw_response"] = raw
    result["sources"] = sources
    result["llm_available"] = llm_available
    result["fallback_used"] = fallback_used

    return result


def _build_fallback_response(topic, level, knowledge_gaps, chunks, question, error_code):
    """
    Build a RAG-only fallback response when the LLM is unavailable.
    Uses retrieved textbook content to answer the question.
    """
    reason = {
        "__LLM_OFFLINE__": "The AI model server is currently offline.",
        "__LLM_TIMEOUT__": "The AI model server timed out.",
    }.get(error_code.split(":")[0].strip(), "The AI model encountered an error.")

    retrieved_text = ""
    if chunks:
        retrieved_text = "\n\n".join([
            f"From {c['source']} (Page {c['page']}):\n{c['text'][:400]}"
            for c in chunks[:3]
        ])
    else:
        retrieved_text = "No textbook content was retrieved for this query."

    gaps_text = ""
    if knowledge_gaps:
        gaps_text = f"\n\n**Areas to review:** {', '.join(knowledge_gaps[:4])}"

    return f"""## Explanation
**Note:** {reason} Showing textbook content instead.

**Question:** {question}

Here is relevant content retrieved from your textbooks on **{topic}**:

{retrieved_text}
{gaps_text}

## Analogy
*The AI tutor is temporarily offline. Please review the textbook excerpts above.*

## Worked Example
*Please refer to the source books listed in the Sources panel for worked examples.*

## Practice Questions
1. Based on the retrieved content above, can you summarize what you understood about {topic}?
2. What aspect of {topic} would you like to explore further once the AI tutor is back online?
3. Can you identify any connections between this content and what you already know about {topic}?"""


def _get_level_instructions(level: str) -> str:
    """Get teaching style instructions based on student level."""
    if level == "Beginner":
        return """- Use simple, everyday language with no assumed knowledge
- Explain every technical term when first introduced
- Use analogies and metaphors extensively
- Avoid or minimize mathematical notation; favor intuitive explanations
- Break concepts into very small, digestible steps
- Be encouraging and patient
- Use real-world examples that anyone can relate to"""

    elif level == "Intermediate":
        return """- Use technical language but explain advanced concepts
- Provide practical, hands-on examples with code snippets
- Include moderate mathematical notation where it helps understanding
- Connect concepts to real-world applications and industry use cases
- Reference best practices and common patterns
- Balance theory with practical implementation"""

    else:  # Advanced
        return """- Use formal technical terminology freely and precisely
- Include mathematical formulations, proofs, and derivations where relevant
- Discuss cutting-edge research and recent advancements
- Provide deep theoretical insights and analysis
- Discuss trade-offs, edge cases, and design decisions
- Reference academic papers and advanced resources when appropriate
- Engage in nuanced, research-level technical discussion"""


def _parse_tutoring_response(response: str) -> dict:
    """Parse the LLM response into structured sections."""
    result = {
        "explanation": "",
        "analogy": "",
        "example": "",
        "practice_questions": "",
        "full_response": response
    }

    section_markers = {
        "explanation": ["## Explanation", "## 📖 Explanation", "**Explanation**"],
        "analogy": ["## Analogy", "## 🔄 Analogy", "**Analogy**"],
        "example": ["## Worked Example", "## 💡 Worked Example", "**Worked Example**"],
        "practice_questions": ["## Practice Questions", "## ✏️ Practice Questions", "**Practice Questions**"]
    }

    # Find all section positions
    section_positions = {}
    for key, markers in section_markers.items():
        for marker in markers:
            if marker in response:
                pos = response.index(marker)
                section_positions[key] = (pos, len(marker))
                break

    # Extract each section content
    sorted_keys = sorted(section_positions, key=lambda k: section_positions[k][0])
    for i, key in enumerate(sorted_keys):
        start_pos, marker_len = section_positions[key]
        content_start = start_pos + marker_len
        if i + 1 < len(sorted_keys):
            next_key = sorted_keys[i + 1]
            content_end = section_positions[next_key][0]
        else:
            content_end = len(response)
        result[key] = response[content_start:content_end].strip()

    # If no sections parsed, put everything in explanation
    if not result["explanation"] and not result["analogy"]:
        result["explanation"] = response

    return result
