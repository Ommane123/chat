import streamlit as st
import os
from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

load_dotenv()

from src.document_processor import process_uploaded_files
from src.embedding_store import create_vector_store
from src.chatbot import get_answer

def init_session_state():
    import uuid
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = str(uuid.uuid4())
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

def handle_new_chat():
    import uuid
    if st.session_state.chat_history:
        st.session_state.chat_sessions[st.session_state.current_session_id] = st.session_state.chat_history
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.chat_history = []

def main():
    load_dotenv()
    init_session_state()
    
    st.set_page_config(page_title="Support Chatbot", page_icon="🤖", layout="wide")
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.title("🤖 AI-Powered Software Support Chatbot")
    with col2:
        st.write("") # spacing
        st.write("")
        st.button("➕ New Chat", help="Start a new chat session", on_click=handle_new_chat)
        
    st.markdown("Upload your documentation and ask questions based on its content.")
    
    # Sidebar for document upload
    with st.sidebar:
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        st.subheader("Preferences")
        target_language = st.selectbox(
            "Response Language", 
            ["English", "Hindi", "Marathi", "Gujarati", "Bengali", "Spanish", "French", "German", "Japanese"]
        )
        read_aloud = st.checkbox("Read Responses Aloud (Audio)", value=False)
        
        st.subheader("Your Documents")
        uploaded_files = st.file_uploader(
            "Upload PDFs, TXT, or DOCX files", 
            type=["pdf", "txt", "docx"], 
            accept_multiple_files=True
        )
        
        process_button = st.button("Process Documents")
        
        if process_button:
            if not api_key:
                st.error("Please provide an OpenRouter API Token first.")
            elif not uploaded_files:
                st.error("Please upload at least one document.")
            else:
                with st.spinner("Processing documents..."):
                    # 1. Process and chunk
                    text_chunks = process_uploaded_files(uploaded_files)
                    if not text_chunks:
                        st.error("No valid text found to process in the documents.")
                    else:
                        st.success(f"Processed into {len(text_chunks)} text chunks.")
                        
                        # 2. Embed and store
                        vector_store = create_vector_store(text_chunks)
                        if vector_store:
                            st.session_state.vector_store = vector_store
                            st.success("Documents stored in in-memory Vector DB.")
                            st.success("Conversational AI Ready!")
                        else:
                            st.error("Error creating vector store.")
    tab_chat, tab_history = st.tabs(["💬 Chat", "📜 History"])
    
    with tab_chat:
        # Main Chat Area
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
            
        # Input Area
        user_question = st.chat_input("Ask a question about your documents:")
        
        if user_question:
            if st.session_state.vector_store is None:
                st.warning("Please upload and process documents with a valid OpenRouter token before asking questions.")
                st.stop()
                
            # Display user message
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = get_answer(
                            vector_store=st.session_state.vector_store,
                            user_question=user_question,
                            api_key=api_key,
                            chat_history=st.session_state.chat_history[:-1],  # Exclude current question 
                            target_language=target_language
                        )
                        answer = response.get("answer", "Sorry, I could not generate an answer.")
                        
                        st.markdown(answer)
                        
                        if read_aloud:
                            try:
                                lang_codes = {
                                    "English": "en", "Hindi": "hi", "Marathi": "mr", 
                                    "Gujarati": "gu", "Bengali": "bn", "Spanish": "es", 
                                    "French": "fr", "German": "de", "Japanese": "ja"
                                }
                                code = lang_codes.get(target_language, "en")
                                tts = gTTS(text=answer, lang=code, slow=False)
                                audio_fp = BytesIO()
                                tts.write_to_fp(audio_fp)
                                audio_fp.seek(0)
                                
                                import base64
                                audio_b64 = base64.b64encode(audio_fp.read()).decode("utf-8")
                                audio_html = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_b64}"></audio>'
                                st.markdown(audio_html, unsafe_allow_html=True)
                            except Exception as tts_e:
                                st.error(f"Text-to-Speech failed: {tts_e}")
                                
                        # Expandable sources
                        if "source_documents" in response and response["source_documents"]:
                            with st.expander("References"):
                                for i, doc in enumerate(response["source_documents"]):
                                    st.write(f"**Source {i+1}:**")
                                    st.info(doc[:300] + "...")
                                    
                        # Save assistant message
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Generation error: {e}")
                        
    with tab_history:
        st.header("Previous Chats")
        if not st.session_state.chat_sessions:
            st.info("No past chats available.")
            
        for session_id, history in list(st.session_state.chat_sessions.items()):
            first_msg = history[0]["content"] if history else "Empty Chat"
            with st.expander(f"Chat: {first_msg[:50]}..."):
                st.write("")
                if st.button("🗑️ Delete Chat", key=f"del_{session_id}"):
                    del st.session_state.chat_sessions[session_id]
                    st.rerun()
                for msg in history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

if __name__ == "__main__":
    main()
