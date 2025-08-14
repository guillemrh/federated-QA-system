from fastapi.testclient import TestClient
from finance_node.main import app

client = TestClient(app)

def test_healthcheck():
    response = client.get("/ask/healthcheck")
    # Check status code
    assert response.status_code == 200
    # Check response content
    assert response.json() == {"status": "Finance node is healthy"}

def test_ask_endpoint():
    response = client.post("/ask/", json={"question": "What is MiFID?"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"]
    assert data["node_id"] == "financial_node"