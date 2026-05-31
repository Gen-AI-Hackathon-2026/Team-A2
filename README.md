# Synapse - Adaptive AI Tutor

> A premium, multi-modal Adaptive AI Tutoring System combining GraphRAG, local LLMs, and dynamic visual engines for a highly personalized learning experience.

The **Synapse Suite** is a unified product console that delivers an adaptive learning experience. It diagnoses knowledge gaps, adapts explanations to the student's proficiency level, visualizes complex concepts step-by-step, and personalizes the learning journey dynamically.

## Problem It Solves
Traditional education platforms offer one-size-fits-all content that doesn't adapt to individual learning paces or missing prerequisites. Synapse solves this by dynamically diagnosing each learner's exact knowledge gaps using a GraphRAG-powered Knowledge Graph, adapting its teaching policy in real-time (Beginner/Intermediate/Expert), and providing hands-free, voice-enabled multi-modal interactions alongside step-by-step interactive algorithm visualizations.

---

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.30%2B-red)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Apps](#apps)
  - [Synapse AI Tutor](#1-synapse-ai-tutor)
  - [Visual Engine](#2-visual-engine)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Roadmap / Future Improvements](#roadmap--future-improvements)
- [License](#license)
- [Contact / Author](#contact--author)

---

## Project Overview

**Synapse AI Tutor** is an end-to-end adaptive learning system that:

1. Assesses a student's knowledge level per topic (Beginner / Intermediate / Advanced)
2. Detects knowledge gaps using a NetworkX knowledge graph
3. Retrieves relevant textbook content using **GraphRAG** — graph-expanded FAISS retrieval
4. Generates personalised tutoring responses via a GPT-class LLM (Ollama)
5. Tracks mastery over time with a progress dashboard and visualiser

The **Visual Engine** is a companion Streamlit app that animates classic
algorithms (neural networks, transformers, RAG pipelines, linked lists, binary
search, recursion) step by step with optional text-to-speech narration.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Synapse AI Tutor                     │
│                                                         │
│  ┌──────────┐  ┌────────────┐  ┌────────────────────┐  │
│  │  Login   │  │  Topics    │  │    Assessment      │  │
│  └──────────┘  └────────────┘  └────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              GraphRAG Pipeline                   │   │
│  │  Question → Graph Expansion → FAISS → Rerank     │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────┐  ┌────────────┐  ┌────────────────────┐  │
│  │  Tutor   │  │  Chatbot   │  │    Visualizer      │  │
│  └──────────┘  └────────────┘  └────────────────────┘  │
│                                                         │
│  ┌──────────┐  ┌────────────┐                          │
│  │Dashboard │  │ Resources  │                          │
│  └──────────┘  └────────────┘                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Visual Engine                        │
│  Neural Network · Transformer · RAG Pipeline            │
│  Linked List · Binary Search · Recursion                │
│  Step-by-step animation + TTS narration                 │
└─────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
Gen AI Hack/
│
├── README.md                          ← this file
├── .gitignore
│
├── synapse_ai_tutor/                  ← Main learning platform
│   ├── app.py                         ← Entry point, routing, global CSS
│   ├── requirements.txt
│   │
│   ├── backend/
│   │   ├── auth.py                    ← Authentication
│   │   ├── assessment.py              ← Question loading, scoring
│   │   ├── chunking.py                ← PDF → text chunks
│   │   ├── embeddings.py              ← Sentence-transformer embeddings
│   │   ├── rag.py                     ← RAGPipeline (FAISS + GraphRAG)
│   │   ├── retriever.py               ← FAISS search
│   │   ├── knowledge_graph.py         ← NetworkX graph, expand_query()
│   │   ├── graph_rag.py               ← graph_rag_retrieve(), gap recs
│   │   ├── gap_detector.py            ← Knowledge gap detection
│   │   ├── llm_client.py              ← Ollama / GPT integration
│   │   ├── progress_tracker.py        ← Per-user mastery tracking
│   │   └── resources.py               ← Curated resource library
│   │
│   ├── pages/
│   │   ├── login.py                   ← Login / signup
│   │   ├── home.py                    ← Landing page
│   │   ├── topic_selection.py         ← Topic picker with mastery badges
│   │   ├── assessment.py              ← 15-question adaptive test
│   │   ├── tutor.py                   ← GraphRAG-powered AI tutor chat
│   │   ├── chatbot.py                 ← General AI chatbot + PDF upload
│   │   ├── dashboard.py               ← Plotly progress dashboard
│   │   ├── visualizer.py              ← Concept-level knowledge graph
│   │   └── resources.py               ← Curated learning resources
│   │
│   └── data/
│       ├── books/                     ← Source PDF textbooks
│       ├── chunks.pkl                 ← Cached text chunks
│       ├── faiss_index.bin            ← Cached FAISS vector index
│       ├── knowledge_graph.json       ← GraphRAG graph definition
│       └── progress.json              ← User progress store
│
└── visual_engine/                     ← Standalone visualisation app
    ├── main.py                        ← Streamlit entry point
    ├── router.py                      ← Visualisation dispatcher
    ├── requirements.txt
    ├── renderers/
    │   └── graph_renderer.py          ← Graph drawing utilities
    └── visualizers/
        ├── neural_network.py
        ├── transformer.py
        ├── rag_pipeline.py
        ├── linked_list.py
        ├── binary_search.py
        └── recursion.py
```

---

## Demo / Screenshots (Placeholder Section)

*Placeholder for demo links and screenshots.* 
- [Link to Live Demo](#)

### System Architecture
![Synapse - Adaptive AI Tutor Architecture](assets/architecture.png)

### App Previews
- **Screenshot 1**: `![Hub Workspace](assets/screenshot1.png)` - The premium Hub Workspace.
- **Screenshot 2**: `![Visual Engine](assets/screenshot2.png)` - Visual Engine animating a Transformer Attention layer.

---

## Tech Stack

### Frontend
- **UI Framework**: HTML5, Vanilla CSS3, Native JavaScript
- **App Engine**: Streamlit (v1.30+)
- **Visuals & Charts**: Plotly, Matplotlib, PIL (Python Imaging Library)

### Backend
- **Core Logic**: Python 3.11+
- **LLM Integration**: Ollama API (GPT-OSS on local network)
- **Vector Search & Embeddings**: FAISS (Facebook AI Similarity Search), `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Knowledge Graph**: NetworkX

### Database
- **Progress Tracking**: Local JSON-based storage (`data/progress.json`)
- **Vector Store**: Cached FAISS Binary Indices
- **Documents**: Processed PDF textbooks

### Tools & DevOps
- **Version Control**: Git
- **Dependency Management**: pip
- **TTS/STT**: gTTS, Whisper (Local integration)

---

## Project Structure

```text
Team-A2/
├── index.html                      # Premium unified Hub Workspace (Entry point)
├── README.md                       # Project Documentation
├── synapse_ai_tutor/               # Main Adaptive AI Tutor subsystem (Port 8501)
│   ├── app.py                      # Subsystem entry point and routing
│   ├── requirements.txt            
│   ├── backend/                    # Core ML, RAG, and logic modules
│   ├── pages/                      # Application views (Topics, Tutor, Dashboard, etc.)
│   └── data/                       # Cached embeddings, graphs, and PDFs
└── visual_engine/                  # Visual Animation Engine subsystem (Port 8502)
    ├── main.py                     # Subsystem entry point
    ├── requirements.txt
    ├── router.py                   # Maps topics to animation logic
    └── visualizers/                # Animation algorithms (Neural Nets, Transformers, etc.)
```

---

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Git
- (Optional) Local Ollama server running `gpt-oss:20b` or a similar model for live LLM responses. The app will fall back to local extraction if unavailable.

### Step-by-Step Installation Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Gen-AI-Hackathon-2026/Team-A2.git
   cd Team-A2
   ```

2. **Install dependencies for Synapse AI Tutor:**
   ```bash
   cd synapse_ai_tutor
   pip install -r requirements.txt
   cd ..
   ```

3. **Install dependencies for Visual Engine:**
   ```bash
   cd visual_engine
   pip install -r requirements.txt
   cd ..
   ```

### Environment Variables Setup
No strict `.env` file is required out of the box. Ensure your local Ollama server is running on `http://localhost:11434` (the default port). You can configure the Ollama host directly from the connection settings UI in the app if you are running it on a different IP or port.

---

## How to Run Locally

You must run both Streamlit subsystems simultaneously, then open the `index.html` hub to use the cohesive application environment.

1. **Start the Synapse AI Tutor (Terminal 1):**
   ```bash
   cd synapse_ai_tutor
   python -m streamlit run app.py --server.port 8501
   ```

2. **Start the Visual Engine (Terminal 2):**
   ```bash
   cd visual_engine
   python -m streamlit run main.py --server.port 8502
   ```

3. **Launch the Hub Workspace:**
   Open the `index.html` file in your preferred modern web browser (Chrome/Edge/Safari). The Hub will embed both running subsystems into a single visually appealing startup-grade UI.

---

## Usage

### Example Commands
Once the app is running:
- Navigate to **Topics** to select a module (e.g., Deep Learning).
- Use the **Assessment** tab to calibrate your initial proficiency level.
- Interact with the **Tutor** chat to ask conceptual questions (e.g., "Explain Self-Attention").
- Switch to the **Visual Engine** tab to see step-by-step architectural animations of what you just learned.

### API Documentation
*N/A - System is currently monolithic via Streamlit and direct Python imports. External API usage is limited to Ollama endpoints (`/api/generate`) which are handled internally by `backend/llm_client.py`.*

---

## Testing
To verify the system components:
1. **Knowledge Graph**: Check the knowledge graph structure using the in-app **Visualizer** page in the AI Tutor.
2. **Retrieval Engine**: Run local diagnostics on the FAISS index by verifying chunk responses in the **Chatbot** page.
3. **Animations**: Test TTS narration and rendering in the **Visual Engine** by selecting a complex topic (e.g. Transformer Attention) and toggling the audio checkbox.

*(Dedicated pytest suite coming soon)*

---

## Deployment
Synapse is designed to be easily containerised. 
1. Create a `Dockerfile` exposing ports `8501` (Tutor) and `8502` (Visual Engine).
2. Host `index.html` via a lightweight static server (e.g., Nginx) that points iframes to the exposed Streamlit ports.
3. Deploy to AWS EC2, Google Cloud Run, or any scalable container service.

---

## Contributing

We welcome contributions to the Synapse Suite!

### Contribution Guidelines
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).

### Pull Request Process
- Ensure code follows standard PEP 8 Python guidelines.
- Test your changes locally on both ports (8501 and 8502).
- Open a PR describing the problem solved and the implementation details. Wait for maintainers to review.

---

## Dataset and Books

The RAG pipeline is pre-indexed over three textbooks:

| Book | Description |
|---|---|
| `Generative AI Foundations in Python.pdf` | Practical GenAI with Python |
| `Hands-On Large Language Models.pdf` | LLM architecture and applications |
| `Understanding Deep Learning.pdf` | Comprehensive deep learning theory |

The assessment question bank uses `manus-dataset.jsonl` — a curated
multiple-choice dataset covering all 10 topics at three difficulty levels.

---

## Git Workflow

```
main
 ├── a5cb73e  initial commit
 ├── bd64131  update 1
 ├── eb1a366  added navigation bar on top
 ├── 036a724  Graphrag Added.
 ├── 1ee1a19  feat(visual-engine): add Visualization Engine subsystem  [merged from feature/visualization-engine]
 └── ce021c6  Merge feature/visualization-engine into main
```

**Branches:**
- `main` — stable, production-ready
- `feature/visualization-engine` — merged (Visual Engine subsystem)

---

## Contact / Author
**Team A2**  
Gen AI Hackathon 2026  
Repository: [https://github.com/Gen-AI-Hackathon-2026/Team-A2](https://github.com/Gen-AI-Hackathon-2026/Team-A2)
