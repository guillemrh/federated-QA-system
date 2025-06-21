from fastapi.testclient import TestClient
from legal_node.main import app  # importa tu app de FastAPI

client = TestClient(app)

def test_healthcheck():
    response = client.get("/legal_questions/healthcheck")
    
    # Comprobamos el código de estado
    assert response.status_code == 200

    # Comprobamos que la respuesta es la esperada
    assert response.json() == {"status": "Legal node is healthy"}