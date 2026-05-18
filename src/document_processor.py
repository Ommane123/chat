import os
import tempfile
from pypdf import PdfReader
import docx2txt

def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks

def process_uploaded_files(uploaded_files):
    """
    Extracts text from uploaded files and splits it into manageable chunks natively.
    Returns a list of strings (the chunks).
    """
    if not uploaded_files:
        return []

    raw_text = ""
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    raw_text += extracted + "\n"
        elif uploaded_file.name.endswith(".txt"):
            raw_text += uploaded_file.getvalue().decode("utf-8") + "\n"
        elif uploaded_file.name.endswith(".docx"):
            text = docx2txt.process(uploaded_file)
            raw_text += text + "\n"

    # Chunk the combined text
    if raw_text.strip():
        text_chunks = chunk_text(raw_text, chunk_size=1000, chunk_overlap=200)
    else:
        text_chunks = []
        
    return text_chunks

def process_local_files(file_paths):
    """
    Extracts text from local files (PDF, TXT, DOCX) and splits it into manageable chunks.
    Returns a list of strings (the chunks).
    """
    if not file_paths:
        return []

    raw_text = ""
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        try:
            if file_path.lower().endswith(".pdf"):
                reader = PdfReader(file_path)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        raw_text += extracted + "\n"
            elif file_path.lower().endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_text += f.read() + "\n"
            elif file_path.lower().endswith(".docx"):
                text = docx2txt.process(file_path)
                raw_text += text + "\n"
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Chunk the combined text
    if raw_text.strip():
        text_chunks = chunk_text(raw_text, chunk_size=1000, chunk_overlap=200)
    else:
        text_chunks = []
        
    return text_chunks
