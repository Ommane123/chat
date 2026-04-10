import os
import numpy as np
from openai import OpenAI

def get_answer(vector_store, user_question, api_key, chat_history, target_language="English"):
    """
    Retrieves context using native FAISS and queries OpenRouter API.
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
            
    # 4. Construct conversation messages natively
    messages = [
        {
            "role": "system", 
            "content": f"You are a helpful assistant. Use the provided context to answer the user's question accurately. If the answer is not contained in the context, do your best to answer accurately or state that you do not know based on the provided documents.\n\nIMPORTANT: You MUST answer the user in {target_language}.\n\nContext:\n" + context
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
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=messages,
        temperature=0.3,
        max_tokens=512
    )
    
    answer = completion.choices[0].message.content
    
    return {
        "answer": answer,
        "source_documents": retrieved_chunks
    }
