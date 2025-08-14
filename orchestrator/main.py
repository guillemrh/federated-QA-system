from fastapi import FastAPI
import requests
import time
from shared.models import AskRequest, AskResponse
from fastapi import Body
from typing import List


app = FastAPI()
urls = {
    "legal_node":"http://legal_node:8001/ask",
    "finance_node":"http://finance_node:8002/ask"
}

# Function to route questions to appropriate nodes based on keywords
# This function can be extended to include more complex routing logic as needed.
def route_question(question: str) -> List[str]:
    """
    Reroute the question to the appropriate nodes based on the question content.
    This is a placeholder function that should contain logic to determine which nodes to query.
    """
    keywords = {
        "legal_node": ["law", "legal", "regulation", "compliance","GDPR", "privacy", "contract", "agreement"],
        "finance_node": ["finance", "financial", "investment", "accounting", "tax", "budget", "cost", "revenue"]
    }
    selected_nodes = []
    q_lower = question.lower()
    for node, keys in keywords.items():
        if any(key in q_lower for key in keys):
            selected_nodes.append(node)
    
    return selected_nodes or list(urls.keys())  # Default to all nodes if no keywords match

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

