from fastapi.testclient import TestClient
from legal_node.main import app 

client = TestClient(app)

def test_healthcheck():
    response = client.get("/ask/healthcheck")
    
    # Check status code
    assert response.status_code == 200

    # Check response content
    assert response.json() == {"status": "Legal node is healthy"}
    
def test_ask_endpoint():
    response = client.post("/ask/", json={"question": "What is my legal node id?"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"]
    assert data["node_id"] == "legal_node"    