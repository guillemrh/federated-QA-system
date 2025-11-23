import json, time, requests, os, re
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
from shared.config import ORCHESTRATOR_URL, TRANSFORMER_MODEL
from rapidfuzz import fuzz
import numpy as np
from tabulate import tabulate

# ----------------------------------------------------
# 1. LOADING DATA
# ----------------------------------------------------

def load_dataset(path="benchmarks/dataset.json") -> List[Dict[str, Any]]:
    """
    Supports either:
    - a JSON array file
    - JSONL (one JSON object per line)
    """
    with open(path, "r", encoding="utf-8") as f:
        first_char = f.read(1)
        f.seek(0)
        if first_char == "[":
            return json.load(f)  # JSON array
        # assume JSONL
        return [json.loads(line) for line in f if line.strip()]

# ----------------------------------------------------
# 2. SEND QUESTION - latency measurement
# ----------------------------------------------------

def ask_orchestrator(question):
    """
    Send a question to the orchestrator, return the JSON response and latency.
    """
    start = time.time()
    response = requests.post(
        ORCHESTRATOR_URL,
        json={"question": question},
        timeout=60
    )
    latency = time.time() - start
    
    print("Raw response text:", response.text)
    
    return response.json(), latency

# ----------------------------------------------------
# 3. METRICS - overlap, similarity
# ----------------------------------------------------

def semantic_similarity(answer: str, ref: str) -> float:
    """
    Semantic similarity (cosine) between answer and reference
    """
    if answer.strip():
        ref_emb = model.encode(ref, convert_to_tensor=True)
        ans_emb = model.encode(answer, convert_to_tensor=True)
        sim = float(util.cos_sim(ref_emb, ans_emb)[0][0])
    else:
        sim = 0.0
    return sim

def retrieval_metrics(q_emb, chunk_embs, relevant_ids, retrieved_ids, k=5):
    """
    Compute precision@k and recall@k for retrieval.
    relevant_ids = ground-truth doc IDs (from dataset)
    retrieved_ids = actual top-k doc IDs from system
    """
    if not relevant_ids:
        return 0.0, 0.0

    retrieved_topk = set(retrieved_ids[:k])
    relevant = set(relevant_ids)

    hits = len(retrieved_topk & relevant)
    precision = hits / min(k, len(retrieved_topk))
    recall = hits / len(relevant)
    return precision, recall


# ----------------------------------------------------
# 4. EVALUATION LOOP
# ----------------------------------------------------

# Load embedding model for semantic similarity
model = SentenceTransformer(TRANSFORMER_MODEL)

def evaluate(dataset_path="benchmarks/dataset.json", out_path="benchmarks/results.json"):
    data = load_dataset(dataset_path)
    results: List[Dict[str, Any]] = []

    for item in data:
        q = item["question"]
        ref = item["answer"]
        qid = item.get("id")
        domain = item.get("domain")
        relevant_ids = item.get("relevant_chunks", [])  # ground truth

        try:
            output, latency = ask_orchestrator(q)
            
            answer = output.get("answer", "")

            # unpack embeddings
            node_results = output.get("raw_responses", [])
            q_emb = None
            chunk_embs = []

            for node in node_results:
                if not q_emb:  # take query embedding once
                    q_emb = node.get("query_embedding", [])
                chunk_embs.extend(node.get("chunk_embeddings", []))
                
            retrieved_ids = [s.get("id") for s in output.get("sources", []) if s.get("id")]
    
        except Exception as e:
            results.append({
                "id": qid,
                "domain": domain,
                "question": q,
                "reference": ref,
                "answer": "",
                "similarity": 0.0,
                "precision@5": 0.0,
                "recall@5": 0.0,
                "latency": None,
                "error": str(e)
            })
            continue

        # Metrics
        sim = semantic_similarity(answer, ref)
        precision, recall = retrieval_metrics(q_emb, chunk_embs, relevant_ids, retrieved_ids, k=5)

        results.append({
            "id": qid,
            "domain": domain,
            "question": q,
            "reference": ref,
            "answer": answer,
            "similarity": sim,
            "precision@5": precision,
            "recall@5": recall,
            "latency": latency,
            "error": None
        })
    # Table preview
    rows = [
        [r["id"], r["domain"], r["similarity"], r["precision@5"], r["recall@5"], r["latency"], r["error"]]
        for r in results
    ]
    print("\nResults table:")
    print(tabulate(rows, headers=["ID", "Domain", "Sim", "P@5", "R@5", "Latency (ms)", "Error"], tablefmt="github"))

    # Save per-example results
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved detailed results → {out_path}")

if __name__ == "__main__":
    evaluate()
    
