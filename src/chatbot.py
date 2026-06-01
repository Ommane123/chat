import os
from openai import OpenAI
from deep_translator import GoogleTranslator

LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Bengali": "bn",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja"
}

def get_context_and_stream(user_question, chat_history, target_language="English", persona="Professional", status_callback=None):
    """
    Queries Ollama API directly with streaming (RAG and FAISS removed).
    Supports translation wrapper for non-English target languages.
    Provides status progress updates via status_callback.
    """
    
    if persona == "Explain Like I'm 5":
        persona_prompt = "You are a helpful customer support assistant explaining concepts to a 5-year-old. Use extremely simple terms, analogies, and keep it easy to understand."
    elif persona == "Summary Mode":
        persona_prompt = "You are a helpful customer support assistant. Provide only a concise bullet-point summary of the answer."
    else:
        persona_prompt = "You are a helpful customer support professional. Provide detailed and professional answers to customer inquiries."

    # Determine if we need translation
    target_lang_code = LANG_MAP.get(target_language, "en")
    should_translate = target_lang_code != "en"

    user_question_en = user_question
    chat_history_en = []

    if should_translate:
        try:
            # 1. Translate user question to English
            if status_callback:
                status_callback("Translating query to English...")
            user_question_en = GoogleTranslator(source="auto", target="en").translate(user_question)
            
            # 2. Translate history content to English in batch for performance
            if chat_history:
                if status_callback:
                    status_callback("Translating conversation history...")
                history_texts = [msg["content"] for msg in chat_history]
                translated_texts = GoogleTranslator(source="auto", target="en").translate_batch(history_texts)
                for msg, trans_text in zip(chat_history, translated_texts):
                    chat_history_en.append({"role": msg["role"], "content": trans_text})
            
            # Instruct the model to respond in English
            system_instruction = f"{persona_prompt}\n\nIMPORTANT: You MUST answer the user in English."
        except Exception as e:
            # Fallback if translation fails
            chat_history_en = chat_history
            system_instruction = f"{persona_prompt}\n\nIMPORTANT: You MUST answer the user in {target_language}."
            should_translate = False
    else:
        chat_history_en = chat_history
        system_instruction = f"{persona_prompt}\n\nIMPORTANT: You MUST answer the user in {target_language}."

    # Construct conversation messages natively
    messages = [
        {
            "role": "system", 
            "content": system_instruction
        }
    ]
    
    # Load past history into messages
    for msg in chat_history_en:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": user_question_en})
    
    # Call Ollama/Global API natively
    # Use environment variable for the URL so it can be configured on Streamlit Cloud
    api_base_url = os.getenv("GLOBAL_LLM_URL", "http://localhost:11434/v1")
    if not api_base_url.endswith("/v1") and not api_base_url.endswith("/v1/"):
        api_base_url = api_base_url.rstrip("/") + "/v1"
    
    client = OpenAI(
        base_url=api_base_url,
        api_key="none", # Key is usually ignored for self-hosted
        default_headers={"Bypass-Tunnel-Reminder": "true"} # Required to bypass localtunnel's warning screen
    )
    
    if status_callback and should_translate:
        status_callback("Querying support bot & generating response...")

    stream = client.chat.completions.create(
        model="supportbot",
        messages=messages,
        temperature=0.3,
        max_tokens=512,
        stream=True
    )
    
    if should_translate:
        # Non-English target language: consume stream, get full response in English, translate, and return complete text
        full_response_en = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response_en += chunk.choices[0].delta.content
        
        try:
            if status_callback:
                status_callback(f"Translating response to {target_language}...")
            translated_answer = GoogleTranslator(source="en", target=target_lang_code).translate(full_response_en)
            return {
                "answer": translated_answer
            }
        except Exception as e:
            # Fallback if final translation fails
            return {
                "answer": full_response_en
            }
    else:
        # English: stream directly
        def generate():
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        
        return {
            "stream": generate()
        }
