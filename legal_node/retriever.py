import os
from typing import List, Dict
from shared.retriever import Retriever
from shared.config import TRANSFORMER_MODEL

# Path to legal node's data folder
DIR_DATA = os.path.join(os.path.dirname(__file__), "data")

# Build the retriever once for this node
retriever = Retriever(DIR_DATA, TRANSFORMER_MODEL).load_text().load_model().build_index()

def retrieve_relevant_chunks(question: str, k: int = 2) -> List[Dict[str, str]]:
    """
    Node-level function to get relevant chunks for a query.
    Returns only the chunks, not distances.
    """
    _, results = retriever.search(question, k, return_distances=False)
    return results
