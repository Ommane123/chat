import os
import numpy as np
from openai import OpenAI

def get_context_and_stream(vector_store, user_question, api_key, chat_history, target_language="English", persona="Professional"):
    """
    Retrieves context using native FAISS and queries OpenRouter API with streaming.
    """
    if not api_key:
        return {"answer": "Please provide an OpenRouter API Token.", "source_documents": []}
        
    # Extract native store components
    index = vector_store["index"]
    chunks = vector_store["chunks"]
    model = vector_store["model"]
    
    # 1. Embed the query
    query_embedding = model.encode([user_question]).astype('float32')
    
    # 2. Search FAISS index (retrieve top 3)
    k = 3
    distances, indices = index.search(query_embedding, k)
    
    # 3. Compile context from retrieved chunks
    retrieved_chunks = []
    context = ""
    for idx in indices[0]:
        # faiss returns -1 if there aren't enough chunks
        if idx != -1 and idx < len(chunks):
            retrieved_chunks.append(chunks[idx])
            context += chunks[idx] + "\n\n"
            
    if persona == "Explain Like I'm 5":
        persona_prompt = "You are a helpful assistant explaining concepts to a 5-year-old. Use extremely simple terms, analogies, and keep it easy to understand."
    elif persona == "Summary Mode":
        persona_prompt = "You are a helpful assistant. Provide only a concise bullet-point summary of the answer."
    else:
        persona_prompt = "You are a helpful professional assistant. Provide detailed and professional answers."

    # 4. Construct conversation messages natively
    messages = [
        {
            "role": "system", 
            "content": f"{persona_prompt} Use the provided context to answer the user's question accurately. If the answer is not contained in the context, do your best to answer accurately or state that you do not know based on the provided documents.\n\nIMPORTANT: You MUST answer the user in {target_language}.\n\nContext:\n" + context
        }
    ]
    
    # Load past history into messages
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": user_question})
    
    # 5. Call OpenRouter API natively
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    stream = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=messages,
        temperature=0.3,
        max_tokens=512,
        stream=True
    )
    
    def generate():
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    
    return {
        "stream": generate(),
        "source_documents": retrieved_chunks
    }
