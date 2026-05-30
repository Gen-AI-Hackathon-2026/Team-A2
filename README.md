# Synapse AI Tutor + Visual Engine

**Team A2 — Gen AI Hackathon 2026**

An adaptive AI-powered learning platform for Generative AI and Deep Learning,
featuring a GraphRAG retrieval system, personalised assessments, and an
interactive algorithm visualisation engine.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Apps](#apps)
  - [Synapse AI Tutor](#1-synapse-ai-tutor)
  - [Visual Engine](#2-visual-engine)
- [Tech Stack](#tech-stack)
- [Setup and Installation](#setup-and-installation)
- [Running the Applications](#running-the-applications)
- [Features](#features)
  - [GraphRAG Retrieval](#graphrag-retrieval)
  - [Adaptive Assessment](#adaptive-assessment)
  - [AI Tutor](#ai-tutor)
  - [Knowledge Visualizer](#knowledge-visualizer)
  - [PDF Chatbot](#pdf-chatbot)
  - [Progress Dashboard](#progress-dashboard)
- [Knowledge Graph](#knowledge-graph)
- [Backend Modules](#backend-modules)
- [Dataset and Books](#dataset-and-books)
- [Git Workflow](#git-workflow)

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

## Apps

### 1. Synapse AI Tutor

A full-stack adaptive learning platform built with **Streamlit**.

**Navigation pages:**

| Page | Description |
|---|---|
| Home | Welcome dashboard with quick-action cards |
| Topics | Select one or more AI/ML topics to study |
| Assessment | 15-question test (5 Easy + 5 Intermediate + 5 Hard, max 30 pts) |
| Tutor | GraphRAG-powered AI chat tutor, adaptive to your level |
| Chatbot | General AI assistant with optional PDF upload |
| Visualizer | Interactive knowledge graph + concept mastery map |
| Dashboard | Plotly mastery charts, radar, history, knowledge gaps |
| Resources | Curated videos, articles, and documentation per topic |

### 2. Visual Engine

A standalone Streamlit app for step-by-step algorithm animation.

**Supported visualisations:**

| Visualisation | Description |
|---|---|
| Neural Network | Forward pass animation with weight layers |
| Transformer | Self-attention, multi-head attention, positional encoding |
| RAG Pipeline | Retrieval-augmented generation flow |
| Linked List | Node traversal, insertion, deletion |
| Binary Search | Divide-and-conquer search animation |
| Recursion | Call-stack tree visualisation |

Features TTS narration via `gTTS` and crossfade frame transitions.

---

## Tech Stack

### Synapse AI Tutor

| Layer | Technology |
|---|---|
| UI Framework | Streamlit >= 1.30 |
| LLM Backend | Ollama (GPT-OSS 20B on MacBook M4 via LAN) |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` |
| Vector Search | FAISS (CPU) |
| Knowledge Graph | NetworkX 3.x |
| PDF Processing | PyMuPDF (`fitz`) |
| Charts | Plotly |
| Deep Learning | PyTorch (embedding model) |
| Progress Store | JSON file (`data/progress.json`) |

### Visual Engine

| Layer | Technology |
|---|---|
| UI Framework | Streamlit >= 1.32 |
| Graph Rendering | NetworkX + Matplotlib / graphviz |
| Animation | PIL / Pillow (crossfade blending) |
| TTS | gTTS (Google Text-to-Speech) |
| Charts | Plotly |

---

## Setup and Installation

### Prerequisites

- Python 3.11+
- pip
- Git
- *(Optional)* Ollama server running `gpt-oss:20b` for live LLM responses.
  The app works offline with textbook-content fallback if Ollama is unavailable.

### 1. Clone the Repository

```bash
git clone https://github.com/Gen-AI-Hackathon-2026/Team-A2.git
cd "Team-A2"
```

### 2. Install Synapse AI Tutor Dependencies

```bash
cd synapse_ai_tutor
pip install -r requirements.txt
```

### 3. Install Visual Engine Dependencies

```bash
cd ../visual_engine
pip install -r requirements.txt
```

> **Note:** `gTTS` requires internet access to generate audio. The visual engine
> works without it — audio is simply skipped if the network is unavailable.

---

## Running the Applications

### Run Synapse AI Tutor (port 8501)

```bash
cd synapse_ai_tutor
python -m streamlit run app.py --server.port 8501
```

Open: **http://localhost:8501**

### Run Visual Engine (port 8502)

```bash
cd visual_engine
python -m streamlit run main.py --server.port 8502
```

Open: **http://localhost:8502**

### Run Both Simultaneously

Open two terminals and run one command in each. Both apps are fully independent.

---

## Features

### GraphRAG Retrieval

The tutor uses a hybrid **Graph + FAISS** retrieval pipeline:

```
Student question
    │
    ▼
Knowledge Graph expansion (NetworkX)
    │  Identify matched concepts in the question
    │  Collect 1-2 hop neighbours from the graph
    │
    ▼
Expanded query = original + matched concepts + graph neighbours
    │
    ▼
FAISS vector search (all-MiniLM-L6-v2 embeddings)
    │  Fetch 2× k candidates
    │
    ▼
Concept reranking (boost chunks mentioning graph-expanded terms)
    │
    ▼
Top-k chunks → LLM context
```

**Example:**
- Question: *"What is self-attention?"*
- Matched: `Self-Attention`
- Graph expanded: `Attention Mechanisms`, `Multi-Head Attention`
- Expanded query: `"What is self-attention? Self-Attention Attention Mechanisms Multi-Head Attention"`

### Adaptive Assessment

- **15 questions** per topic: 5 Easy (1 pt) + 5 Intermediate (2 pts) + 5 Hard (3 pts)
- **Maximum score:** 30 points
- **Levels:** Beginner (0–42%), Intermediate (43–75%), Advanced (76–100%)
- Supports multi-topic assessment queues
- Full history with retake capability

### AI Tutor

- Level-adaptive responses (Beginner / Intermediate / Advanced teaching style)
- GraphRAG retrieval shown inline per response (matched + expanded concepts)
- Structured responses: **Explanation → Analogy → Worked Example → Practice Questions**
- Graceful fallback to textbook content when LLM is offline
- Source citations with book name and page number

### Knowledge Visualizer

- **Topic-level graph:** 10 AI/ML topics as nodes, edges show prerequisites
- **Concept-level graph:** Radial layout of all concepts per topic
  - Green = Mastered (≥ 76%)
  - Yellow = Partial (assessed, < 76%)
  - Red = Knowledge Gap
  - Grey = Not Assessed
- Recommended learning paths generated from graph traversal
- Plotly bar chart and skill radar chart

### PDF Chatbot

- Upload any PDF (research paper, textbook, notes)
- Text is chunked, embedded, and indexed in a per-session FAISS index
- Chat against your own document using the same retrieval pipeline
- Toggle between PDF knowledge base and main textbook corpus

### Progress Dashboard

- Per-topic mastery scores and levels
- Plotly radar chart (skill overview)
- Mastery bar chart
- Knowledge gaps per topic
- Assessment history (all attempts)
- Practice session log

---

## Knowledge Graph

Defined in `synapse_ai_tutor/data/knowledge_graph.json`.

**Stats:** 68 nodes · 82 edges · 10 topics · 58 concepts · True DAG

**Topics and key concepts:**

| Topic | Key Concepts |
|---|---|
| Neural Networks | Perceptrons, Backpropagation, Activation Functions, Loss Functions, Gradient Descent |
| CNNs | Convolution Operations, Pooling Layers, Feature Maps, Transfer Learning |
| RNNs | Hidden States, LSTM Gates, GRU Architecture, Vanishing Gradients |
| Transformers | Self-Attention, Multi-Head Attention, Positional Encoding, Query Key Value, Embeddings |
| LLMs | Pre-training, Context Windows, Scaling Laws, Emergent Abilities |
| Prompt Engineering | Few-Shot Learning, Chain-of-Thought, System Prompts |
| Generative AI Fundamentals | Latent Space, Sampling Methods, Generative vs Discriminative |
| GANs | Generator Network, Discriminator Network, Adversarial Training, Mode Collapse |
| Diffusion Models | Forward Diffusion, Reverse Process, Denoising, Noise Schedule, Latent Diffusion |
| Fine-Tuning and RAG | LoRA / QLoRA, Retrieval Pipeline, Embedding Models, Vector Databases |

Edge types: `prerequisite`, `contains`, `extends`, `specializes`, `uses`, `related`

---

## Backend Modules

| Module | Purpose |
|---|---|
| `auth.py` | User registration and login (JSON-backed) |
| `assessment.py` | Dataset loading, question categorisation, scoring |
| `chunking.py` | PDF → overlapping text chunks with metadata |
| `embeddings.py` | Sentence-transformer embedding, FAISS index build/load |
| `retriever.py` | FAISS nearest-neighbour search |
| `rag.py` | `RAGPipeline`: `search()`, `search_for_topic()`, `graph_rag_search()` |
| `knowledge_graph.py` | `build_knowledge_graph()`, `expand_query()`, `graph_learning_path()` |
| `graph_rag.py` | `graph_rag_retrieve()`, `get_gap_recommendations()`, `build_graph_context()` |
| `gap_detector.py` | Prerequisite map, knowledge gap detection per topic |
| `llm_client.py` | Ollama API client, `generate_tutoring_response()`, fallback handler |
| `progress_tracker.py` | Read/write mastery scores, session counts, assessment history |
| `resources.py` | Curated videos, articles, documentation per topic and level |

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

## Team

**Team A2 — Gen AI Hackathon 2026**

Repository: [github.com/Gen-AI-Hackathon-2026/Team-A2](https://github.com/Gen-AI-Hackathon-2026/Team-A2)
