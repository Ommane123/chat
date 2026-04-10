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
