# legal_node/retriever.py

from sentence_transformers import SentenceTransformer
import faiss
from typing import List
import time

# Example document chunks (in real case: read from file + chunk)
text_chunks = [
    "Processed lawfully, fairly and in a transparent manner in relation to the data subject.",
    "Collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes."
]

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode + store vectors
embeddings = model.encode(text_chunks).astype('float32')
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
print(f"FAISS index created with {index.ntotal} chunks.")

def retrieve_relevant_chunks(question: str, k: int = 2) -> List[str]:
    question_embedding = model.encode([question]).astype('float32')  # Batch of 1
    
    start_time = time.time()
    distances, indices = index.search(question_embedding, k)
    end_time = time.time()
    
    print(f"Search completed in {(end_time - start_time):.4f} seconds.")

    results = []
    for i in range(k):
        idx = indices[0][i]
        results.append(text_chunks[idx])
    
    return results
