import os

# CHUNKING text files into manageable pieces for FAISS indexing
# SORTING files by name for deterministic order
# FILE SIZE and cleaning up empty files
# FLEXIBILITY for other data formats (pdf, docx)
def load_text_chunks(DATA_DIR: str, chunk_size: int=500) -> list:
    """
    Load text files from a directory and split them into smaller chunks.
    Returns a list of text chunks as strings.
    """
    chunks = []
    
    for filename in sorted(os.listdir(DATA_DIR)):  # deterministic        
        if filename.endswith(".txt"):
            file_path = os.path.join(DATA_DIR, filename)
            with open(file_path, "r", encoding="utf-8-sig") as f:
                text = f.read().strip()
                if not text:
                    continue  # skip empty files
                
                # Simple chunking by words
                words = text.split()
                for i in range(0, len(words), chunk_size):
                    chunk_text = " ".join(words[i:i+chunk_size])
                    # Return a dictionary with text and source (metadata)
                    chunks.append({
                        "text": chunk_text,
                        "source": filename
                    })
    return chunks