# 🧠 Federated QA System

A modular, multi-node architecture for question-answering over distributed corpora, built to explore semantic routing, information retrieval with vector databases, and LLM-powered answer synthesis.

---

## 🚀 Objective

To build a federated question-answering system in which information is split across independent nodes (each with their own corpus and semantic index). When a question is asked, it is intelligently routed to the most relevant nodes. Each node answers based on its internal knowledge, and the system aggregates the results.

This project is meant as a personal portfolio to deepen my skills in:

- NLP: vector embeddings, chunking, retrieval, semantic routing
- Systems architecture: microservices, containerization, scalability
- LLM orchestration and prompt engineering
- Distributed systems reasoning and design

---

## 🧭 Project Overview

The system is built in 3 phases, gradually increasing complexity and modularity:

| Phase | Description |
|-------|-------------|
| **Phase 1** | Single-node QA over one corpus with retrieval + LLM answering |
| **Phase 2** | Multiple independent nodes, each with its own corpus, responding in parallel |
| **Phase 3** | Semantic router that selects the most relevant node(s) based on the query content |

---

## 📁 Project Structure
```
orchestrator/
├── endpoints.py         # FastAPI endpoints (e.g. /ask)
├── service.py           # Logic to route query to nodes and aggregate
├── config.py            # Node URLs, env vars
├── main.py              # FastAPI app runner
└── tests/
    └── test_service.py

legal_node/
├── endpoints.py         # /ask endpoint for this node
├── service.py           # Node-specific retrieval and response logic
├── config.py
├── main.py              # FastAPI app
└── tests/
    └── test_service.py

finance_node/
└── (same structure as legal_node)

shared/
├── base_node.py         # Abstract base node class
├── models.py
├── utils.py             # General helpers
└── generics/
    └── preprocessing.py # Optional: text cleaning, splitting, etc.

docker-compose.yml       # Defines all services (orchestrator + nodes)
Dockerfile               # Base image for nodes and orchestrator
requirements.txt         # Common Python dependencies
README.md
```

---

### 📦 Core Features – MVP & Beyond

#### ✅ Phase 1: Foundational System Setup
- [x] Docker-based environment setup (Orchestrator + Nodes)
- [x] API endpoint: `/ask` with question input (at node level)
- [x] Answer generation via OpenAI or local LLM (stub for now)
- [x] Multi-node system scaffold (orchestrator → node calls)
- [x] Healthcheck endpoint for orchestrator + nodes
- [x] Basic unit + integration tests using `pytest`

#### 🚧 Phase 2: Corpus and Node Expansion
- [ ] Basic document ingestion and chunking per domain
- [ ] Vector indexing (e.g. FAISS or ChromaDB)
- [ ] QA over one corpus (retrieval + generation)
- [x] Add second node (e.g. `finance_node`)
- [x] Route queries to correct node via orchestrator
- [ ] Modular corpus structure (plug & play domains)

#### 🔮 Phase 3: Federated Semantic Intelligence
- [ ] Semantic query routing (embedding + classification)
- [ ] Aggregated answers from multiple nodes
- [ ] Confidence scoring or provenance metadata per answer

---

## 🔧 Potential Enhancements & Learning Challenges

Here’s a curated set of optional features to expand and deepen the system. Each one adds unique technical and learning value:

### 🧪 Retrieval & NLP
- [ ] Compare different embedding models (e.g. `E5`, `Instructor`, `LegalBERT`)
- [ ] Chunk overlap vs non-overlap analysis
- [ ] Implement reranking of retrieved chunks using a cross-encoder
- [ ] Create an interface to visualize vector distances between queries and docs

### 🧠 LLM Interaction
- [ ] Prompt templates per domain
- [ ] Let nodes use different LLMs (e.g. OpenAI vs `llama3` via Ollama)
- [ ] Add conversational memory (simple history tracking)
- [ ] Create synthetic questions to evaluate answer quality

### 🌐 System Design
- [ ] Load balancing across nodes
- [ ] Streaming answers from multiple nodes (partial responses)
- [ ] Circuit breakers or fallbacks when nodes fail
- [ ] Semantic summarization of each corpus for efficient routing

### 🔐 Data Privacy / Ethics
- [ ] Node-level access control
- [ ] Fully local setup (no external APIs) for confidential corpora
- [ ] Detect hallucinations and annotate low-confidence answers

---

## 🧩 Future Ideas

- Create a CLI tool to interact with the system
- Add a basic dashboard for monitoring node responses
- Plug in LangChain/RAG pipelines to benchmark performance
- Adapt this system to work on multilingual corpora with routing by language

---

## 📚 What I aim

This project is not only about building something that works, but also about **growing as an engineer**. I want to:

- Reason about distributed systems and separation of concerns
- Learn to optimize semantic search pipelines
- Understand how to design modular, scalable AI services
- Practice debugging and maintaining multi-service environments
