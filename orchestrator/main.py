from fastapi import FastAPI, Body
import requests
import time
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from shared.models import AskRequest, AskResponse
from shared.config import GOOGLE_API_KEY, GOOGLE_MODEL, TRANSFORMER_MODEL


# ----------------------------------------------------
# 1. CONFIG & SETUP
# ----------------------------------------------------
app = FastAPI()

urls = {
    "legal_node": "http://legal_node:8001/ask",
    "finance_node": "http://finance_node:8002/ask",
}

# Initialize Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(GOOGLE_MODEL)
model2 = genai.GenerativeModel("models/gemini-2.5-flash-lite")

NODE_TOPICS = {
    "legal_node": "Laws, regulations, compliance, GDPR, contracts, privacy, data transfer, third-country transfers, binding corporate rules, standard contractual clauses, SCCs, adequacy decisions, data portability, data subject rights",
    "finance_node": "Finance, investment, accounting, tax, budgets, revenues, EU financial regulation, ISO20022, payments, securities, financial messaging, payment messages, SEPA, SWIFT, financial instruments, capital markets",
}

# Load embedding model for routing
router_model = SentenceTransformer(TRANSFORMER_MODEL)

# ----------------------------------------------------
# 2. ROUTING LAYER
# ----------------------------------------------------
def route_question(question: str) -> List[str]:
    """
    Use LLM to classify question into relevant nodes.
    """
    allowed_nodes = ", ".join(NODE_TOPICS.keys())
    topics_str = "\n".join([f"- {k}: {v}" for k, v in NODE_TOPICS.items()])

    prompt = f"""
    You are an expert at classifying questions into specialized nodes.

    Here are the nodes and their topics:
    {topics_str}

    Given the user question below, return ONLY the node keys from this list:
    {allowed_nodes}

    Format: comma-separated list of node keys, without explanation.

    User question:
    {question}
    """

    try:
        llm_response = model2.generate_content(prompt)
        raw_response = llm_response.text.strip().lower()
        llm_nodes = [node.strip() for node in raw_response.split(",") if node.strip() in NODE_TOPICS.keys()]

        # Fallback: if the LLM didn’t match any valid node, default to all
        if not llm_nodes:
            llm_nodes = list(NODE_TOPICS.keys())

    except Exception as e:
        print(f"LLM routing failed: {e}")
        llm_nodes = list(NODE_TOPICS.keys())

    print(f"[DEBUG] LLM routing response: {llm_nodes}")
    return llm_nodes

# ----------------------------------------------------
# 3. NODE QUERY LAYER
# ----------------------------------------------------
def query_nodes(question: str, target_nodes: List[str]) -> List[Dict]:
    """
    Query selected nodes and return raw responses.
    """
    raw_responses = []

    for node in target_nodes:
        if node in urls:
            url = urls[node]
            print(f"[DEBUG] Sending request to {url} with question: {question}")
            try:
                response = requests.post(url, json={"question": question}, timeout=20)
                print(f"[DEBUG] {node} raw response: {response.text}")
                data = response.json()
                node_result = {
                    "response": data["response"],  # AskResponse dict
                    "query_embedding": data.get("query_embedding", []),
                    "chunk_embeddings": data.get("chunk_embeddings", []),
                }
                raw_responses.append(node_result)
            except Exception as e:
                print(f"[ERROR] Failed to get response from {node}: {e}")
                raw_responses.append({
                    "response": {
                        "answer": f"Error from {node}: {e}",
                        "confidence": 0.0,
                        "sources": [],
                        "node_id": node,
                        "status": "error",
                    },
                    "query_embedding": [],
                    "chunk_embeddings": []
                })

    return raw_responses


# ----------------------------------------------------
# 4. COMBINER LAYER
# ----------------------------------------------------
def combine_answers_with_llm(question: str, node_responses: List[Dict], nodes_hit: List[str]) -> AskResponse:
    """
    Use LLM to merge node answers into a single coherent answer.
    Returns AskResponse for API compatibility.
    """
    # Build context from node answers
    context = "\n\n".join(
        f"From {r['response']['node_id']}:\n{r['response']['answer']}"
        for r in node_responses
    )

    # Build dynamic assistant role
    domains = [NODE_TOPICS.get(node, node) for node in nodes_hit]
    role_description = " and ".join(domains)

    prompt = f"""
You are an assistant specialized in {role_description}.

User question:
{question}

Node answers:
{context}

Write a single, clear answer that integrates the information.
If one answer is incomplete, combine them logically.
Cite relevant principles when possible.
    """

    llm_response = model.generate_content(prompt)
    final_answer = llm_response.candidates[0].content.parts[0].text.strip()
    
    # Average confidence across nodes - could be refined to weighted average
    avg_conf = (
        sum(r["response"].get("confidence", 0) for r in node_responses) / len(node_responses)
        if node_responses else 0.0
    )

    return AskResponse(
        answer=final_answer,
        confidence=avg_conf,
        sources=[s for r in node_responses for s in r.get("sources", [])],
        node_id=nodes_hit[0] if nodes_hit else None,
        nodes_hit=nodes_hit,
        status="success",
    )


# ----------------------------------------------------
# 5. FASTAPI ROUTES
# ----------------------------------------------------
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


@app.post("/ask")
def ask_all_nodes(req: AskRequest = Body(...)):
    try:
        target_nodes = route_question(req.question)
        print(f"[DEBUG] Routed '{req.question}' → {target_nodes}")
    except Exception as e:
        print(f"[ERROR] Routing failed: {e}")
        return AskResponse(
            answer=f"Routing failed: {e}",
            confidence=0.0,
            sources=[],
            nodes_hit=[],
            status="error",
        )

    raw_responses = query_nodes(req.question, target_nodes)

    try:
        combined = combine_answers_with_llm(req.question, raw_responses, target_nodes)
        print(f"[DEBUG] Combined answer: {combined}")
        return {
            **combined.dict(), # Unpack AskResponse fields
            "raw_responses": raw_responses # Embeddings for analysis
        }
    except Exception as e:
        print(f"[ERROR] Combining answers failed: {e}")
        return AskResponse(
            answer=f"Combine failed: {e}",
            confidence=0.0,
            sources=[],
            nodes_hit=[r.get("node_id") for r in raw_responses],
            status="error",
        )
