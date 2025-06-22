from fastapi import FastAPI
import requests
import time
from shared.models import AskRequest, AskResponse
from fastapi import Body


app = FastAPI()

# Endpoint que puedes consultar desde fuera
@app.get("/healthcheck")
def check_legal_node():
    url = "http://legal_node:8001/ask"
    for _ in range(10):
        try:
            r = requests.post(url, json={"question": "Test"})
            if r.status_code == 200:
                return {"status": "Legal node is up!"}
        except Exception as e:
            print(f"Waiting for legal_node: {e}")
            time.sleep(2)
    return {"status": "Legal node unavailable"}


@app.post("/ask", response_model=AskResponse)
def ask_legal_node(req: AskRequest = Body(...)):
    try:
        response = requests.post(
            "http://legal_node:8001/ask",
            json=req.dict()
        )
        data = response.json()
        return {"answer": data["answer"]}
    except Exception as e:
        return {"answer": f"Error: {e}"}

