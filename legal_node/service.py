from .retriever import retrieve_relevant_chunks
from shared.models import AskResponse, Source

def answer_question(question: str) -> AskResponse:
    chunks = retrieve_relevant_chunks(question)
    context = "\n\n".join(chunks)

    source = Source(
        name="Stub source (to be replaced by real doc metadata)",
        url="https://gdpr-info.eu/art-6-gdpr/",
        snippet=chunks[0] if chunks else "No content found"
    )

    return AskResponse(
        answer=f"Based on this:\n{context}\n\nI think the answer is: (stub)",
        confidence=0.75,
        sources=[source],
        node_id="legal_node",
        status="success"
    )
