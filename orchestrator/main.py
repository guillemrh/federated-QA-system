from fastapi import FastAPI
import requests
import time
from shared.models import AskRequest, AskResponse
from fastapi import Body
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


app = FastAPI()
urls = {
    "legal_node":"http://legal_node:8001/ask",
    "finance_node":"http://finance_node:8002/ask"
}

NODE_TOPICS = {
    "legal_node": "Laws, regulations, compliance, GDPR, contracts, privacy",
    "finance_node": "Finance, investment, accounting, tax, budgets, revenues"
}

MODEL_NAME = "all-MiniLM-L6-v2" 
router_model = SentenceTransformer(MODEL_NAME)

# Precompute topic embeddings
node_embeddings = {
    node: router_model.encode(topic, normalize_embeddings=True)
    for node, topic in NODE_TOPICS.items()
}

# Function to route questions to appropriate nodes
# This function can be extended to include more complex routing logic as needed.
def route_question(question: str, top_k: int = 2, threshold: float = 0.2):
    """
    Select the most relevant nodes for a query using semantic similarity.
    """
    query_emb = router_model.encode(question, normalize_embeddings=True)

    similarities = {
        node: float(np.dot(query_emb, emb))  # cosine similarity
        for node, emb in node_embeddings.items()
    }
    
    print("Similarity scores:", similarities)

    # Sort by similarity
    ranked_nodes = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    # Filter by threshold
    selected = [node for node, score in ranked_nodes if score >= threshold]

    # If nothing passes threshold, pick top_k
    if not selected:
        selected = [node for node, _ in ranked_nodes[:top_k]]

    return selected

# Health check endpoint to ensure all nodes are reachable
@app.get("/healthcheck")
def check_all_nodes():
    for node_name, url in urls.items():
        for _ in range(10):
            try:
                r = requests.post(url, json={"question": "Test"})
                if r.status_code == 200:
                    return {"status": f"{node_name} node is up!"}
            except Exception as e:
                print(f"Waiting for {node_name}: {e}")
                time.sleep(2)
        return {"status": f"{node_name} node unavailable"}

# Endpoint to ask questions to all nodes
@app.post("/ask", response_model=List[AskResponse])
def ask_all_nodes(req: AskRequest = Body(...)):
    responses = []

    for node in route_question(req.question):
        if node in urls:
            url = urls[node]
            print(f"Sending request to {url} with question: {req.question}")
            try:
                response = requests.post(url, json=req.dict())
                data = response.json()
                data["node_id"] = node  # Add node identifier to response
                responses.append(data)
            except Exception as e:
                print(f"Failed to get response from {node}: {e}")
                responses.append(AskResponse(
                    answer=f"Error from {node}: {e}",
                    confidence=0.0,
                    sources=[],
                    node_id=node,
                    status="error"
                ))
    return responses

