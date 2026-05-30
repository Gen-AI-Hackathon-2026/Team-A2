"""
LLM Client for Synapse AI Tutor.
Connects to GPT-OSS 20B running on MacBook M4 via Ollama.
Uses OpenAI-compatible API calls.
"""

import requests
import json

# Ollama endpoint on MacBook M4
OLLAMA_BASE_URL = "http://192.168.29.145:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"

# Model name — adjust if your Ollama model name differs
DEFAULT_MODEL = "gpt-oss"


def check_connection() -> bool:
    """
    Check if the Ollama server is reachable.
    
    Returns:
        True if connection is successful
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_available_models() -> list:
    """
    Get list of available models on the Ollama server.
    
    Returns:
        List of model names
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
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
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt for context
        model: Model name (defaults to DEFAULT_MODEL)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text response
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
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("message", {}).get("content", "No response generated.")
        else:
            return f"Error: Server returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "⚠️ Could not connect to the LLM server. Please ensure Ollama is running on the MacBook at http://192.168.29.145:11434"
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. The model may be loading or processing a large request."
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"


def generate_tutoring_response(
    topic: str,
    level: str,
    knowledge_gaps: list,
    retrieved_chunks: list,
    student_question: str,
    model: str = None
) -> dict:
    """
    Generate a comprehensive tutoring response with adaptive behavior.
    
    Args:
        topic: The selected topic
        level: Student's proficiency level (Beginner/Intermediate/Advanced)
        knowledge_gaps: List of detected knowledge gaps
        retrieved_chunks: List of relevant chunks from RAG
        student_question: The student's question
        model: Model name
        
    Returns:
        Dictionary with explanation, analogy, example, and practice questions
    """
    # Build context from retrieved chunks
    context_text = ""
    for i, chunk in enumerate(retrieved_chunks[:5], 1):
        context_text += f"\n--- Source: {chunk['source']} (Page {chunk['page']}) ---\n"
        context_text += chunk['text'] + "\n"
    
    # Adaptive system prompt based on level
    level_instructions = _get_level_instructions(level)
    
    gaps_text = ""
    if knowledge_gaps:
        gaps_text = f"\nThe student has the following knowledge gaps: {', '.join(knowledge_gaps)}. Address these gaps when relevant.\n"
    
    system_prompt = f"""You are Synapse, an expert AI tutor specializing in {topic}.

Student Profile:
- Level: {level}
- Topic: {topic}
{gaps_text}

Teaching Style Guidelines:
{level_instructions}

Reference Material:
{context_text}

Your response MUST include ALL of the following sections, clearly labeled:

## 📖 Explanation
Provide a clear, detailed explanation adapted to the student's level.

## 🔄 Analogy
Create a relatable real-world analogy to help understand the concept.

## 💡 Worked Example
Provide a step-by-step worked example with code or mathematical notation where appropriate.

## ✏️ Practice Questions
Generate 2-3 practice questions for the student to test their understanding.

Be thorough, encouraging, and adaptive to the student's level."""

    response_text = generate_response(
        prompt=student_question,
        system_prompt=system_prompt,
        model=model,
        temperature=0.7,
        max_tokens=3000
    )
    
    # Parse the response into sections
    result = _parse_tutoring_response(response_text)
    result["raw_response"] = response_text
    result["sources"] = retrieved_chunks[:5]
    
    return result


def _get_level_instructions(level: str) -> str:
    """Get teaching style instructions based on student level."""
    if level == "Beginner":
        return """- Use simple, everyday language
- Explain jargon and technical terms when first introduced
- Use analogies and metaphors extensively
- Minimize mathematical notation; use intuitive explanations instead
- Break concepts into very small, digestible steps
- Provide encouraging feedback
- Use visual descriptions when possible"""
    
    elif level == "Intermediate":
        return """- Use technical language but explain complex terms
- Provide practical, hands-on examples with code
- Include moderate mathematical notation where helpful
- Connect concepts to real-world applications
- Reference industry best practices
- Balance theory with practical implementation"""
    
    else:  # Advanced
        return """- Use formal technical terminology freely
- Include mathematical formulations and proofs where relevant
- Discuss cutting-edge research and recent developments
- Provide deeper theoretical insights
- Discuss trade-offs, edge cases, and design decisions
- Reference academic papers and advanced resources
- Engage in nuanced technical discussion"""


def _parse_tutoring_response(response: str) -> dict:
    """Parse the LLM response into structured sections."""
    result = {
        "explanation": "",
        "analogy": "",
        "example": "",
        "practice_questions": "",
        "full_response": response
    }
    
    sections = {
        "explanation": ["## 📖 Explanation", "## Explanation", "**Explanation**"],
        "analogy": ["## 🔄 Analogy", "## Analogy", "**Analogy**"],
        "example": ["## 💡 Worked Example", "## Worked Example", "**Worked Example**"],
        "practice_questions": ["## ✏️ Practice Questions", "## Practice Questions", "**Practice Questions**"]
    }
    
    for section_key, markers in sections.items():
        for marker in markers:
            if marker in response:
                start = response.index(marker) + len(marker)
                # Find the next section marker
                end = len(response)
                for other_key, other_markers in sections.items():
                    if other_key != section_key:
                        for other_marker in other_markers:
                            if other_marker in response:
                                other_start = response.index(other_marker)
                                if other_start > start and other_start < end:
                                    end = other_start
                
                result[section_key] = response[start:end].strip()
                break
    
    # If parsing failed, put everything in explanation
    if not result["explanation"]:
        result["explanation"] = response
    
    return result
