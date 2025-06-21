from orchestrator.main import app
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests

client = TestClient(app)

@patch("orchestrator.main.requests.post")
def test_healthcheck_when_node_is_down(mock_post):
    mock_post.side_effect = requests.exceptions.ConnectionError("Legal node is unavailable")

    response = client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == {"status": "Legal node unavailable"}
