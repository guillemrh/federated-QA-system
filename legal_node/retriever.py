# legal_node/retriever.py

from sentence_transformers import SentenceTransformer
import faiss
from typing import List
import time
from shared.data_loader import load_text_chunks
from shared.config import TRANSFORMER_MODEL
import os

DIR_DATA = os.path.join(os.path.dirname(__file__), "data")

# Load text chunks from the specified directory
if not os.path.exists(DIR_DATA):
    raise FileNotFoundError(f"Data directory {DIR_DATA} does not exist.")
text_chunks = load_text_chunks(DIR_DATA)
if not text_chunks:
    raise ValueError("No text chunks found in the specified directory.")

# Load embedding model
model = SentenceTransformer(TRANSFORMER_MODEL)

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
