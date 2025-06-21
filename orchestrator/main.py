from fastapi import FastAPI
import requests
import time

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


@app.post("/ask")
def ask_legal_node():
    try:
        response = requests.post(
            "http://legal_node:8001/ask",
            json={"question": "What are the legal risks of X?"}
        )
        data = response.json()
        return {"answer": data["answer"]}
    except Exception as e:
        return {"error": str(e)}
