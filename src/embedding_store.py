import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

def create_vector_store(text_chunks):
    """
    Creates an in-memory FAISS vector store from text chunks using sentence-transformers natively.
    Returns: dictionary containing 'index', 'chunks', and 'model'
    """
    if not text_chunks:
        return None
        
    # Initialize the embedding model locally
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Generate embeddings
    embeddings = model.encode(text_chunks)
    
    # Create FAISS Index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to the index
    index.add(np.array(embeddings).astype('float32'))
    
    return {
        "index": index,
        "chunks": text_chunks,
        "model": model
    }
