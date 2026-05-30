"""
Assessment Engine for Synapse AI Tutor.
Loads questions from manus-dataset.jsonl, categorizes by topic,
builds question banks, and evaluates student proficiency.
"""

import json
import random
import os
import re

# Topic keywords for categorization
TOPIC_KEYWORDS = {
    "Neural Networks": [
        "neural network", "perceptron", "activation function", "backpropagation",
        "feedforward", "deep learning", "hidden layer", "weight", "bias",
        "gradient descent", "neuron", "multilayer", "deep neural", "ann",
        "artificial neural", "network architecture", "fully connected"
    ],
    "CNNs": [
        "cnn", "convolutional", "convolution", "pooling", "feature map",
        "kernel", "filter", "stride", "padding", "image classification",
        "object detection", "resnet", "vgg", "alexnet", "image recognition",
        "spatial", "feature extraction"
    ],
    "RNNs": [
        "rnn", "recurrent", "lstm", "gru", "sequence model", "time series",
        "hidden state", "vanishing gradient", "bidirectional", "seq2seq",
        "sequence to sequence", "temporal", "sequential data", "memory cell"
    ],
    "Transformers": [
        "transformer", "attention mechanism", "self-attention", "multi-head attention",
        "positional encoding", "encoder-decoder", "bert", "attention is all you need",
        "scaled dot-product", "cross-attention", "attention score", "query key value"
    ],
    "LLMs": [
        "large language model", "llm", "gpt", "language model", "token",
        "tokenization", "context window", "inference", "pre-training",
        "foundation model", "scaling law", "emergent", "few-shot",
        "zero-shot", "chain of thought", "reasoning"
    ],
    "Prompt Engineering": [
        "prompt engineering", "prompt", "few-shot prompt", "chain of thought",
        "system prompt", "prompt template", "instruction tuning",
        "prompt design", "in-context learning", "prompt optimization",
        "zero-shot", "prompt injection", "jailbreak"
    ],
    "Generative AI Fundamentals": [
        "generative ai", "generative model", "generation", "creative ai",
        "text generation", "image generation", "content generation",
        "synthetic data", "generative", "ai generated", "artificial intelligence",
        "responsible ai", "ai ethics", "ai safety", "agentic ai", "agent"
    ],
    "GANs": [
        "gan", "generative adversarial", "discriminator", "generator",
        "adversarial training", "mode collapse", "wasserstein", "stylegan",
        "dcgan", "conditional gan", "image synthesis", "adversarial network",
        "fake image", "deepfake"
    ],
    "Diffusion Models": [
        "diffusion model", "denoising", "noise schedule", "stable diffusion",
        "ddpm", "score matching", "latent diffusion", "diffusion process",
        "reverse process", "dall-e", "midjourney", "image diffusion",
        "noise prediction", "sampling", "probability", "stochastic"
    ],
    "Fine-Tuning and RAG": [
        "fine-tuning", "fine tuning", "rag", "retrieval augmented",
        "lora", "qlora", "adapter", "transfer learning", "domain adaptation",
        "retrieval", "vector database", "embedding", "knowledge base",
        "context retrieval", "document retrieval", "chunking"
    ]
}

# Level mapping based on score
LEVEL_MAPPING = {
    (0, 40): "Beginner",
    (41, 75): "Intermediate",
    (76, 100): "Advanced"
}


def get_level(score: int) -> str:
    """Determine proficiency level based on score."""
    if score <= 40:
        return "Beginner"
    elif score <= 75:
        return "Intermediate"
    else:
        return "Advanced"


def load_dataset(filepath: str = None) -> list:
    """
    Load the JSONL dataset from file.
    
    Args:
        filepath: Path to the JSONL file
        
    Returns:
        List of question dictionaries
    """
    if filepath is None:
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "manus-dataset.jsonl")
    
    questions = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    questions.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return questions


def categorize_questions(questions: list) -> dict:
    """
    Categorize questions into topics based on keyword matching.
    
    Args:
        questions: List of question dictionaries from dataset
        
    Returns:
        Dictionary mapping topic names to lists of questions
    """
    topic_banks = {topic: [] for topic in TOPIC_KEYWORDS}
    
    for q in questions:
        instruction = q.get("instruction", "").lower()
        response = q.get("response", "").lower()
        combined = instruction + " " + response
        
        best_topic = None
        best_score = 0
        
        for topic, keywords in TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in combined)
            if score > best_score:
                best_score = score
                best_topic = topic
        
        if best_topic and best_score > 0:
            topic_banks[best_topic].append(q)
    
    return topic_banks


def generate_mcq_from_question(question: dict, topic: str) -> dict:
    """
    Generate a multiple choice question from a dataset entry.
    Creates plausible options from the response text.
    
    Args:
        question: A question dictionary from the dataset
        topic: The topic this question belongs to
        
    Returns:
        MCQ dictionary with question, options, and correct answer
    """
    instruction = question.get("instruction", "")
    response = question.get("response", "")
    
    # Extract key concepts from the response for the correct answer
    sentences = [s.strip() for s in response.split('.') if len(s.strip()) > 20]
    
    if len(sentences) < 1:
        sentences = [response[:200]]
    
    correct_answer = sentences[0].strip() + "."
    
    # Generate distractors
    distractors = [
        f"This concept is not relevant to {topic} and has no practical applications.",
        f"It is a deprecated approach that has been replaced by newer methodologies.",
        f"This only applies to supervised learning and cannot be used in other contexts.",
        f"It requires quantum computing resources and is not feasible with current hardware.",
        f"This technique was proven incorrect in recent peer-reviewed research.",
        f"It is exclusively used in computer vision and has no NLP applications.",
    ]
    
    random.shuffle(distractors)
    selected_distractors = distractors[:3]
    
    options = selected_distractors + [correct_answer]
    random.shuffle(options)
    
    correct_index = options.index(correct_answer)
    
    return {
        "question": instruction,
        "options": options,
        "correct_index": correct_index,
        "correct_answer": correct_answer,
        "topic": topic
    }


def select_assessment_questions(topic_banks: dict, topic: str, num_questions: int = 5) -> list:
    """
    Randomly select questions for a topic assessment.
    
    Args:
        topic_banks: Dictionary of categorized questions
        topic: The topic to assess
        num_questions: Number of questions to select
        
    Returns:
        List of MCQ dictionaries
    """
    available = topic_banks.get(topic, [])
    
    if len(available) == 0:
        # Fallback: generate generic questions for the topic
        return generate_fallback_questions(topic, num_questions)
    
    selected = random.sample(available, min(num_questions, len(available)))
    
    mcqs = []
    for q in selected:
        mcq = generate_mcq_from_question(q, topic)
        mcqs.append(mcq)
    
    return mcqs


def generate_fallback_questions(topic: str, num_questions: int = 5) -> list:
    """Generate fallback questions if topic has insufficient data."""
    fallback_templates = [
        {
            "question": f"What is the primary purpose of {topic}?",
            "options": [
                f"{topic} is primarily used for creating adaptive learning systems that respond to student needs.",
                f"{topic} is only used for data visualization and has no ML applications.",
                f"{topic} is a hardware specification standard for GPU computing.",
                f"{topic} is exclusively a database management technique.",
            ],
            "correct_index": 0,
            "correct_answer": f"{topic} is primarily used for creating adaptive learning systems that respond to student needs.",
            "topic": topic
        },
        {
            "question": f"Which of the following best describes a key component of {topic}?",
            "options": [
                f"A fundamental building block that enables the core functionality of {topic}.",
                f"An outdated component that is no longer used in modern implementations.",
                f"A purely theoretical concept with no practical implementation.",
                f"A component exclusive to quantum computing architectures.",
            ],
            "correct_index": 0,
            "correct_answer": f"A fundamental building block that enables the core functionality of {topic}.",
            "topic": topic
        },
        {
            "question": f"What is a common challenge when working with {topic}?",
            "options": [
                f"Balancing complexity with performance while ensuring reliable results.",
                f"There are no challenges as {topic} is fully automated.",
                f"The only challenge is purchasing expensive hardware.",
                f"Finding enough storage space for the source code.",
            ],
            "correct_index": 0,
            "correct_answer": f"Balancing complexity with performance while ensuring reliable results.",
            "topic": topic
        },
        {
            "question": f"How does {topic} relate to modern AI systems?",
            "options": [
                f"{topic} is integral to advancing AI capabilities and enabling more sophisticated models.",
                f"{topic} has been completely replaced by newer technologies.",
                f"{topic} is only used in academic research and never in production.",
                f"{topic} is unrelated to AI and belongs to traditional software engineering.",
            ],
            "correct_index": 0,
            "correct_answer": f"{topic} is integral to advancing AI capabilities and enabling more sophisticated models.",
            "topic": topic
        },
        {
            "question": f"What is a best practice when implementing {topic}?",
            "options": [
                f"Following established patterns and iteratively testing for optimal results.",
                f"Implementing everything from scratch without using existing frameworks.",
                f"Avoiding documentation to save development time.",
                f"Using the largest possible model regardless of the task requirements.",
            ],
            "correct_index": 0,
            "correct_answer": f"Following established patterns and iteratively testing for optimal results.",
            "topic": topic
        },
    ]
    
    return fallback_templates[:num_questions]


def calculate_score(answers: list, questions: list) -> dict:
    """
    Calculate assessment score and determine level.
    
    Args:
        answers: List of selected answer indices
        questions: List of MCQ dictionaries
        
    Returns:
        Dictionary with score, level, and details
    """
    if not questions:
        return {"score": 0, "level": "Beginner", "correct": 0, "total": 0}
    
    correct = 0
    total = len(questions)
    
    for i, q in enumerate(questions):
        if i < len(answers) and answers[i] == q["correct_index"]:
            correct += 1
    
    score = int((correct / total) * 100)
    level = get_level(score)
    
    return {
        "score": score,
        "level": level,
        "correct": correct,
        "total": total
    }
