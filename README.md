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
| **Phase 3** | Semantic router that selects the most relevant node(s) based on the query content | ✅ Done

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

benchmarks/
├── dataset.jsonl
├── evaluator.py
└── results/

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
- [x] Add **Finance Node** with same retriever structure as Legal Node
- [x] Implement **semantic router** in orchestrator
- [x] Aggregate results from multiple nodes with confidence scores
- [ ] Node metadata in responses (source, distances, etc.)

---

## 🔧 Potential Enhancements & Learning Challenges

Here’s a curated set of optional features to expand and deepen the system. Each one adds unique technical and learning value:

### ⚡ Model & Research Innovation

**Goal:** Move beyond relying only on Google’s gemini-1.5-flash-latest. Train, evaluate, and compare models for retrieval-augmented QA system.

**Tasks:**

- [x] Literature Review: Document how QA/RAG systems compare models (common metrics: F1, BLEU, ROUGE, accuracy, hallucination rate, etc.).
- [x] Dataset Creation: Collect or generate a benchmark dataset of legal, finance, and mixed questions.
- [ ] Train Embedding Model: Sentence-BERT fine-tuned on domain corpora.
- [ ] Optionally experiment with domain-adapted embeddings.
- [ ] Evaluation Pipeline: Implement scripts to compare Gemini vs your embedding model vs other local LLMs (Llama, Mistral, etc.).
- [ ] Log quantitative results (retrieval accuracy, precision@k, latency).
- [ ] Visualization: Generate charts of model performance over the benchmark dataset.
- [ ] Stretch Goal: Experiment with training a tiny transformer from scratch on narrow domain data just to showcase feasibility.

### 📊 Observability & Reliability

**Goal:** Make the system production-grade by adding observability, monitoring, and fault tolerance.

**Tasks:**

- [ ] Tracing (OpenTelemetry): Implement distributed tracing across orchestrator → nodes → aggregator.
- [ ] Metrics Collection: Expose Prometheus/Grafana metrics: 
  * Latency per node. 
  * Error rate.
  * Node uptime/availability.
- [ ] Structured Logging: Add JSON logs that include embedding similarity scores, routing decisions, and node responses.
- [ ] Chaos Mode: Simulate:
  * Node crashes.
  * High latency responses.
  * Node disconnections.
- [ ] Verify orchestrator handles failures gracefully.
- [ ] Alerts & SLOs: Define service-level objectives (e.g., “95% of answers within <2s”) and alerts for violations.

---

## 📚 What I aim

This project is not only about building something that works, but also about **growing as an engineer**. I want to:

- Reason about distributed systems and separation of concerns
- Learn to optimize semantic search pipelines
- Understand how to design modular, scalable AI services
- Practice debugging and maintaining multi-service environments
