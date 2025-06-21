import requests

response = requests.post(
    "http://legal-node:8001/ask",
    json={"question": "What are the legal risks of X?"}
)

data = response.json()
print(data["answer"])
