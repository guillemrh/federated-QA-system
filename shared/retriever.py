import os
import faiss
from sentence_transformers import SentenceTransformer
from shared.data_loader import load_text_chunks
from typing import List, Tuple, Dict


class Retriever:
    """
    Retriever for loading documents, building a FAISS index, and searching it.
    """

    def __init__(self, data_dir: str, model_name: str):
        """
        Initialize the retriever with:
        - data_dir: path to directory containing .txt files
        - model_name: name of the SentenceTransformer embedding model
        """
        self.data_dir = data_dir
        self.model_name = model_name
        self.text_chunks: List[Dict[str, str]] = []
        self.model: SentenceTransformer = None
        self.index: faiss.IndexFlatL2 = None

    def load_text(self) -> "Retriever":
        """
        Load all .txt files from the data directory into text_chunks.
        """
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Data directory {self.data_dir} does not exist.")
        self.text_chunks = load_text_chunks(self.data_dir)
        if not self.text_chunks:
            raise ValueError("No text chunks found in the specified directory.")
        return self

    def load_model(self) -> "Retriever":
        """
        Load the SentenceTransformer embedding model.
        """
        self.model = SentenceTransformer(self.model_name)
        return self

    def build_index(self) -> "Retriever":
        """
        Build a FAISS index from the loaded text chunks.
        """
        if not self.text_chunks:
            raise ValueError("Text chunks not loaded. Call load_text() first.")
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        texts = [chunk["text"] for chunk in self.text_chunks] # Extract text from chunks (list of dicts with "text" key)
        embeddings = self.model.encode(texts).astype('float32')
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

        print(f"FAISS index created with {self.index.ntotal} chunks.")
        return self

    def search(self, query: str, k: int = 2, return_distances: bool = True) -> Tuple[List[float], List[Dict[str, str]]]:
        """
        Search the FAISS index for the top k results for a given query.
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Adjust k to not exceed available chunks
        k = min(k, len(self.text_chunks))

        query_embedding = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)

        results = [self.text_chunks[idx] for idx in indices[0]]

        return (distances[0], results) if return_distances else (None, results)
