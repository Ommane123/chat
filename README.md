# AI-Powered Software Support Chatbot

An intelligent document-based Q&A system built with Python and Streamlit. This application allows users to upload PDF, TXT, and DOCX files, processes their contents using locally-hosted FAISS vector caching, and leverages the OpenRouter API to provide highly accurate, context-aware answers to inquiries.

## Features
- **Document Uploader**: Natively extract and chunk data from PDFs, Word files, and plain text formats.
- **RAG Architecture**: Uses `sentence-transformers` for embedding tracking and `faiss-cpu` for extremely fast local similarity searches.
- **OpenRouter LLM Generation**: Uses the OpenAI standard Python SDK to connect seamlessly to OpenRouter models.
- **Text-to-Speech Accessibility**: Includes Google Text-to-Speech (`gTTS`) inline functionality, allowing conversational output to instantly be read out loud to the user in a native browser audio stream. Supports 9 different output languages!

## Setup and Installation

1. **Install Requirements**
```bash
pip install -r requirements.txt
```

2. **Configure API Key**
Create a `.env` file in the root directory that contains your OpenRouter API Token:
```env
OPENROUTER_API_KEY=your_api_key_here
```

3. **Run the Application**
```bash
streamlit run app.py
```
