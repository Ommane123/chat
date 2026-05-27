import os
from openai import OpenAI

def get_context_and_stream(user_question, chat_history, target_language="English", persona="Professional"):
    """
    Queries Ollama API directly with streaming (RAG and FAISS removed).
    """
    
    if persona == "Explain Like I'm 5":
        persona_prompt = "You are a helpful customer support assistant explaining concepts to a 5-year-old. Use extremely simple terms, analogies, and keep it easy to understand."
    elif persona == "Summary Mode":
        persona_prompt = "You are a helpful customer support assistant. Provide only a concise bullet-point summary of the answer."
    else:
        persona_prompt = "You are a helpful customer support professional. Provide detailed and professional answers to customer inquiries."

    # Construct conversation messages natively
    messages = [
        {
            "role": "system", 
            "content": f"{persona_prompt}\n\nIMPORTANT: You MUST answer the user in {target_language}."
        }
    ]
    
    # Load past history into messages
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": user_question})
    
    # Call Ollama/Global API natively
    # Use environment variable for the URL so it can be configured on Streamlit Cloud
    api_base_url = os.getenv("GLOBAL_LLM_URL", "http://localhost:11434/v1")
    
    client = OpenAI(
        base_url=api_base_url,
        api_key="none", # Key is usually ignored for self-hosted
    )
    
    stream = client.chat.completions.create(
        model="supportbot",
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
        "stream": generate()
    }
