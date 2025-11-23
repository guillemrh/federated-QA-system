from .retriever import retrieve_relevant_chunks
from shared.models import AskResponse, Source, NodeResult
import os
from shared.config import GOOGLE_API_KEY, GOOGLE_MODEL
import google.generativeai as genai

# Initialize Google Generative AI with the API key and choose the model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(GOOGLE_MODEL)

def answer_question(question: str) -> NodeResult:
    """
    Use the retriever to get relevant chunks + embeddings, pass them to the LLM,
    and return a structured AskResponse.
    """
    # Retrieve context + embeddings
    retrieval = retrieve_relevant_chunks(question)
    query_embedding = retrieval["query_embedding"]
    chunks = retrieval["chunks"]

    # Build context string from chunk texts
    context = "\n\n".join(chunk["text"] for chunk in chunks)
    
    # Build chunk embeddings list from retrieved chunks
    chunk_embeddings = [chunk["embedding"] for chunk in chunks]

    # Build prompt for the LLM
    prompt = f"""You are a finance assistant. Use the following financial context to answer the user's question.

Context:
{context}

Question:
{question}

Answer in clear, accurate financial language.
If you don't know the answer, say "I don't know", but try to answer based on the context.
If the answer is not in the context, say "The provided context does not contain the answer to your question.
"""

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
            url=f"https://finance.ec.europa.eu//{chunk['source']}", # Needs to be updated with actual source URLs
            snippet=chunk["text"][:200]  # First 200 chars
        )
        for chunk in chunks
    ]
    
    # Create AskResponse (public API contract)
    ask_response = AskResponse(
        answer=answer_text,
        confidence=0.9,
        sources=sources,
        node_id="finance_node",
        status="success"
    )

    # Return NodeResult (internal structure)
    return NodeResult(
        response=ask_response,
        query_embedding=query_embedding,
        chunk_embeddings=chunk_embeddings
    )