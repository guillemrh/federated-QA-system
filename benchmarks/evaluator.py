import json, time, requests, os, re
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
from shared.config import ORCHESTRATOR_URL, TRANSFORMER_MODEL
from rapidfuzz import fuzz

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
# 3. METRICS - faithfulness, overlap, similarity
# ----------------------------------------------------

# Simple sentence/bullet splitter
def _split_units(text: str) -> List[str]:
    # split on end-of-sentence punctuation OR bullets/newlines/dashes
    parts = re.split(r'(?<=[\.\?\!])\s+|[\n\r]+|(?:^\s*[-•]\s+)', text)
    units = [p.strip() for p in parts if p and len(p.strip()) >= 5]
    return units

def faithfulness(answer: str, sources: List[Dict[str, Any]], threshold: float = 0.60) -> float:
    """
    Fraction of answer units (sentences/bullets) that are semantically supported by any source snippet (above the threshold).
    Uses SBERT cosine similarity in batch for speed.
    Returns a simple faithfulness score [0,1]
    """
    if not answer or not sources:
        return 0.0
    
    units = _split_units(answer)
    if not units:
        return 0.0

    source_texts = [src.get("snippet","") for src in sources if src.get("snippet")]
    if not source_texts:
        return 0.0
    print(f"snippets: {source_texts}")
    # Batch-encode (faster + consistent)
    unit_emb = model.encode(units, convert_to_tensor=True)
    src_emb = model.encode(source_texts, convert_to_tensor=True)

    sim_mat = util.cos_sim(unit_emb, src_emb)  # shape [num_units, num_sources]
    # Count units that have at least one supporting source above threshold
    supported = (sim_mat.max(dim=1).values >= threshold).sum().item()

    return supported / len(units)

_STOPWORDS = {
    "the","a","an","and","or","of","to","in","for","on","with","by","as","at",
    "is","are","was","were","be","being","been","that","this","it","its","from",
    "their","there","then","than","but","if","into","about","over","under"
}

def _tokens(text: str) -> set:
    """
    Simple regex tokenization, removes light stopwords.
    """
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in toks if t not in _STOPWORDS}

def keyword_overlap(a: str, b: str) -> float:
    """
    What fraction of reference keywords appear in the answer
    """
    A, B = _tokens(a), _tokens(b)
    if not A:
        return 0.0
    return len(A & B) / len(A)

def semantic_similiarity(answer: str, ref: str) -> float:
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

        try:
            output, latency = ask_orchestrator(q)
        except Exception as e:
            results.append({
                "id": qid,
                "domain": domain,
                "question": q,
                "reference": ref,
                "answer": "",
                "nodes_hit": [],
                "faithfulness": 0.0,   
                "overlap": 0.0,
                "similarity": 0.0,
                "latency": None,
                "error": str(e)
            })
            continue
        
        answer = output.get("answer", "")
        sources = output.get("sources", [])
        nodes_hit = output.get("nodes_hit", [])
        
        print("Chosen answer:", answer)
        print("Nodes hit:", nodes_hit)
        
        # Metrics
        faith = faithfulness(answer, sources)
        overlap = keyword_overlap(ref, answer)
        sim = semantic_similiarity(answer, ref)

        results.append({
            "id": qid,
            "domain": domain,
            "question": q,
            "reference": ref,
            "answer": answer,
            "nodes_hit": nodes_hit,
            "faithfulness": faith,
            "overlap": overlap,
            "similarity": sim,
            "latency": latency,
            "error": None
        })

    # Save per-example results
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Print quick summary (overall + by domain)
    def avg(vals): 
        vals = [v for v in vals if isinstance(v, (int, float))]
        return sum(vals) / len(vals) if vals else 0.0

    overall_faithfulness = avg([r["faithfulness"] for r in results])
    overall_sim = avg([r["similarity"] for r in results])
    overall_overlap = avg([r["overlap"] for r in results])
    overall_latency = avg([r["latency"] for r in results if r["latency"] is not None])

    print("\n=== Overall ===")
    print(f"Items: {len(results)}")
    print(f"Faithfulness: {overall_faithfulness:.3f}")
    print(f"Overlap:     {overall_overlap:.3f}")
    print(f"Similarity:  {overall_sim:.3f}")
    print(f"Latency(s):  {overall_latency:.3f}")

    # Domain splits
    by_domain: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        by_domain.setdefault(r.get("domain", "unknown"), []).append(r)

    for dom, rs in by_domain.items():
        d_faith = avg([x["faithfulness"] for x in rs])
        d_sim = avg([x["similarity"] for x in rs])
        d_overlap = avg([x["overlap"] for x in rs])
        d_lat = avg([x["latency"] for x in rs if x["latency"] is not None])
        print(f"\n=== {dom} ===")
        print(f"Items:     {len(rs)}")
        print(f"Faithfulness {d_faith:.3f} | Overlap {d_overlap:.3f} | Sim {d_sim:.3f} | Lat {d_lat:.3f}")

    print(f"\nSaved detailed results → {out_path}")

if __name__ == "__main__":
    evaluate()