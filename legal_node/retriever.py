import os
from typing import List, Dict
from shared.retriever import Retriever
from shared.config import TRANSFORMER_MODEL

# Path to legal node's data folder
DIR_DATA = os.path.join(os.path.dirname(__file__), "data")

# Build the retriever once for this node
retriever = Retriever(DIR_DATA, TRANSFORMER_MODEL).load_text().load_model().build_index()

def retrieve_relevant_chunks(question: str, k: int = 2) -> Dict[str, any]:
    """
    Node-level function to get relevant chunks and query embedding for a query.
    Returns:
    {
        "query_embedding": [...],
        "chunks": [ { "text": ..., "embedding": [...] }, ... ]
    }
    """
    _, results, query_emb = retriever.search(question, k, return_distances=True)

    return {
        "query_embedding": query_emb,
        "chunks": results  # these already carry their own "embedding"
    }
