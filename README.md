# 🧠 Federated QA System

A modular, multi-node architecture for question-answering over distributed corpora, built to explore semantic routing, information retrieval with vector databases, and LLM-powered answer synthesis.

---

## 🚀 Objective

Build a federated question-answering system in which information is split across independent nodes (each with their own corpus and semantic index). When a question is asked, it is intelligently routed by a central orchestrator node to the most relevant nodes. Each node answers based on its internal knowledge, and the orchestrator aggregates the results.

This project is meant as a personal portfolio to deepen my skills in:

- NLP: vector embeddings, chunking, retrieval, semantic routing
- Systems architecture: microservices, containerization, scalability
- LLM orchestration and prompt engineering
- Distributed systems reasoning and design

---

## 🧭 Project Overview

The MVP is built in 3 phases, gradually increasing complexity and modularity:

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Single-node QA over one corpus with retrieval + LLM answering | ✅ Done
| **Phase 2** | Multiple independent nodes, each with its own corpus, responding in parallel | ✅ Done
| **Phase 3** | Semantic router that selects the most relevant node(s) based on the query content | 🚧 In progress

After completion of the MVP, I will start enhancing the system (see below, stretch goals & potential enhancements section)

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
├── data/  
├── endpoints.py         # /ask endpoint for this node
├── service.py           # Retrieval + LLM answer composition
├── retriever.py         # Node-specific retrieval wrapper
├── main.py              # FastAPI app
└── tests/
    └── test_service.py

finance_node/
└── (same structure as legal_node)

shared/
├── models.py         # Abstract base node class
├── config.py         # Global config (model names, env vars)
├── data_loader.py    # Chunk loading logic
└── retriever.py      # Reusable FAISS retriever

.env                     # Store variables
docker-compose.yml       # Defines all services (orchestrator + nodes)
Dockerfile               # Base image for nodes and orchestrator
requirements.txt         # Common Python dependencies
README.md
```

---
## ✅ Current Features

- **Dockerized** orchestrator and nodes for easy multi-service spin-up
- **Local FAISS vector store** for each node
- **Reusable retriever class** for document loading, embedding, and search
- **Domain isolation** (each node has its own model + data)
- **Simple retrieval-based QA** with OpenAI or local LLMs
- **Extensible node structure** for quick domain additions

---

## 🚧 Next Milestones

### Short-term (Phase 3 Completion)
- [ ] Add **Finance Node** with same retriever structure as Legal Node
- [ ] Implement **semantic router** in orchestrator
- [ ] Aggregate results from multiple nodes with confidence scores
- [ ] Node metadata in responses (source, distances, etc.)

### Medium-term
- [ ] Automated **unit + integration testing** with `pytest`
- [ ] CLI tool for local queries
- [ ] Corpus ingestion pipeline (drag-and-drop files into node)
- [ ] Compare embedding models (`all-MiniLM-L6-v2` vs domain-specific)

### Stretch Goals
- [ ] **Dashboard** showing:
  - Node hit rate
  - Retrieval distances
  - Latency per request
- [ ] **Fine-tune an embedding model** on domain-specific Q/A pairs
- [ ] **Cross-encoder reranking** for improved retrieval accuracy
- [ ] **Streaming aggregation** (partial answers from multiple nodes in real-time)
- [ ] Multilingual routing + answering

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
- [ ] Let nodes use different LLMs (e.g. Gemini vs `llama3` via Ollama)
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
