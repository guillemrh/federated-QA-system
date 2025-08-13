from .retriever import retrieve_relevant_chunks
from shared.models import AskResponse, Source

import os
from shared.config import GOOGLE_API_KEY
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
def answer_question(question: str) -> AskResponse:
    chunks = retrieve_relevant_chunks(question)
    context = "\n\n".join(chunks)
    print("Chunks returned:", chunks)
    print("Type of chunks[0]:", type(chunks[0]))

    
    prompt = f"""You are a legal assistant. Use the following legal context to answer the user's question.

Context:
{context}

Question:
{question}

Answer in clear, accurate legal language."""

    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(prompt)

    answer_text = response.text
    
    return AskResponse(
    answer=answer_text,
    confidence=0.9,
    sources=[
        Source(
            name="Stub source (to be replaced by real doc metadata)",
            url="https://gdpr-info.eu/art-6-gdpr/"
        )
    ],
    node_id="legal_node",
    status="success"
    )