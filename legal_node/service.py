from .retriever import retrieve_relevant_chunks
from shared.models import AskResponse, Source
import os
from shared.config import GOOGLE_API_KEY
import google.generativeai as genai

# Initialize Google Generative AI with the API key and choose the model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    
def answer_question(question: str) -> AskResponse:
    """
    Use the retriever to get relevant chunks, pass them to the LLM,
    and return a structured AskResponse.
    """
    # Retrieve context
    chunks = retrieve_relevant_chunks(question)
    
    # Build context string from chunk texts
    context = "\n\n".join(chunk["text"] for chunk in chunks)
    
    print("Chunks returned:", chunks)
    print("Type of chunks[0]:", type(chunks[0]))

    # Build prompt for the LLM
    prompt = f"""You are a legal assistant. Use the following legal context to answer the user's question.

Context:
{context}

Question:
{question}

Answer in clear, accurate legal language."""

    try: 
        # Generate the response
        response = model.generate_content(prompt)
        # Extract the answer text from the response
        answer_text = response.text
    except Exception as e:
        answer_text = f"Error generating response: {str(e)}"
    
    # Build sources dynamically
    sources=[
        Source(
            name=chunk["source"],
            url=f"https://gdpr-info.eu/{chunk['source']}",
            snippet=chunk["text"][:100]  # Use the first 100 characters as a snippet
        )
        for chunk in chunks
    ]
    
    return AskResponse(
    answer=answer_text,
    confidence=0.9,
    sources=sources,
    node_id="legal_node",
    status="success"
    )