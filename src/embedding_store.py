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

import os
import pickle

def save_vector_store(store, directory="vector_db"):
    """
    Saves the FAISS index and text chunks to disk.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Save the FAISS index
    faiss.write_index(store["index"], os.path.join(directory, "index.faiss"))
    
    # Save the chunks
    with open(os.path.join(directory, "chunks.pkl"), "wb") as f:
        pickle.dump(store["chunks"], f)

def load_vector_store(directory="vector_db"):
    """
    Loads the FAISS index and text chunks from disk, and initializes the model.
    Returns: dictionary containing 'index', 'chunks', and 'model', or None if not found.
    """
    index_path = os.path.join(directory, "index.faiss")
    chunks_path = os.path.join(directory, "chunks.pkl")
    
    if not os.path.exists(directory) or not os.path.exists(index_path) or not os.path.exists(chunks_path):
        return None
        
    try:
        index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            chunks = pickle.load(f)
            
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        return {
            "index": index,
            "chunks": chunks,
            "model": model
        }
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None
