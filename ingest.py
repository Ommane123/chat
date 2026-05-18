import os
import sys

# Ensure the root directory is in the sys.path so we can import src modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.document_processor import process_local_files
from src.embedding_store import create_vector_store, save_vector_store

def ingest_default_documents():
    input_dir = "company_docx"
    output_dir = "vector_db"
    
    if not os.path.exists(input_dir):
        print(f"Directory '{input_dir}' does not exist. Please create it and add documents.")
        return

    # Gather file paths
    file_paths = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith((".pdf", ".txt", ".docx")):
                file_paths.append(os.path.join(root, file))
                
    if not file_paths:
        print(f"No valid documents (PDF, TXT, DOCX) found in '{input_dir}'.")
        return
        
    print(f"Found {len(file_paths)} document(s) to process:")
    for fp in file_paths:
        print(f" - {fp}")
        
    print("\nProcessing documents...")
    text_chunks = process_local_files(file_paths)
    
    if not text_chunks:
        print("No valid text could be extracted from the documents.")
        return
        
    print(f"Extracted {len(text_chunks)} text chunks. Creating vector store...")
    vector_store = create_vector_store(text_chunks)
    
    if not vector_store:
        print("Failed to create vector store.")
        return
        
    print(f"Saving vector store to '{output_dir}'...")
    save_vector_store(vector_store, output_dir)
    print("Done! The default database is ready to use.")

if __name__ == "__main__":
    ingest_default_documents()
