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
    from src.database import get_user_sessions, get_session_messages
    
    if "user" in st.session_state:
        if "current_session_id" not in st.session_state:
            st.session_state.current_session_id = str(uuid.uuid4())
                
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "read_aloud" not in st.session_state:
        st.session_state.read_aloud = False

def toggle_read_aloud():
    st.session_state.read_aloud = not st.session_state.read_aloud

def handle_new_chat():
    import uuid
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.chat_history = []
    st.session_state.vector_store = None
    st.session_state.show_settings_page = False

def main():
    load_dotenv()
    
    st.set_page_config(page_title="Support Chatbot", page_icon="🤖", layout="wide")
    
    if "user" not in st.session_state:
        from src.authentication import show_auth_screen
        show_auth_screen()
        return
        
    init_session_state()
    
    col1, col2, col3 = st.columns([0.7, 0.2, 0.1], vertical_alignment="bottom")
    with col1:
        st.title("🤖 AI-Powered Software Support Chatbot")
    with col2:
        target_language = st.selectbox(
            "Response Language", 
            ["English", "Hindi", "Marathi", "Gujarati", "Bengali", "Spanish", "French", "German", "Japanese"],
            label_visibility="collapsed"
        )
    with col3:
        icon = "🔊" if st.session_state.read_aloud else "🔈"
        st.button(icon, on_click=toggle_read_aloud, help="Toggle Read Aloud", use_container_width=True)
        
    welcome_text = st.empty()
    if not st.session_state.chat_history:
        welcome_text.markdown("Upload your documentation and ask questions based on its content.")
    
    # Sidebar for document upload
    with st.sidebar:
        st.markdown("""
            <style>
            div.stButton > button[kind="primary"] {
                height: 60px;
                font-size: 18px;
            }
            </style>
        """, unsafe_allow_html=True)
        st.button("➕ New Chat", help="Start a new chat session", on_click=handle_new_chat, use_container_width=True, type="primary")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.show_settings_page = True
            st.rerun()
        
        st.divider()
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        st.subheader("Your Documents")
        uploaded_files = st.file_uploader(
            "Upload PDFs, TXT, or DOCX files", 
            type=["pdf", "txt", "docx"], 
            accept_multiple_files=True,
            key=f"file_uploader_{st.session_state.current_session_id}"
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
                            
        st.divider()
        st.subheader("📜 History")
        from src.database import get_user_sessions, get_session_messages, delete_chat_session
        sessions = get_user_sessions(st.session_state.user["id"])
        
        if not sessions:
            st.info("No past chats available.")
            
        for session_id in sessions:
            messages = get_session_messages(session_id)
            first_msg = messages[0]["content"] if messages else "Empty Chat"
            col_a, col_b = st.columns([0.8, 0.2])
            with col_a:
                if st.button(f"{first_msg[:25]}...", key=f"load_{session_id}", use_container_width=True):
                    st.session_state.current_session_id = session_id
                    st.session_state.chat_history = messages
                    st.session_state.vector_store = None
                    st.session_state.show_settings_page = False
                    st.rerun()
            with col_b:
                if st.button("🗑️", key=f"del_{session_id}"):
                    delete_chat_session(session_id)
                    if st.session_state.current_session_id == session_id:
                        st.session_state.chat_history = []
                        import uuid
                        st.session_state.current_session_id = str(uuid.uuid4())
                        st.session_state.vector_store = None
                    st.rerun()
            st.markdown("---")

    if st.session_state.get("show_settings_page", False):
        st.header("⚙️ Settings")
        st.write("Manage your account and preferences.")
        
        with st.container(border=True):
            st.subheader("Danger Zone")
            st.write("Deleting your account is irreversible. All chat history and data will be erased.")
            
            if st.button("Delete Account", type="primary"):
                st.session_state.confirm_delete = True
                
            if st.session_state.get("confirm_delete", False):
                st.error("Are you sure? This cannot be undone.")
                col_y, col_n = st.columns(2)
                with col_y:
                    if st.button("Yes, Delete", type="primary", use_container_width=True):
                        from src.database import delete_user_account
                        delete_user_account(st.session_state.user["id"])
                        st.session_state.clear()
                        st.rerun()
                with col_n:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.confirm_delete = False
                        st.rerun()
        return

    # Main Chat Area
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Input Area
    user_question = st.chat_input("Ask a question about your documents:")
    
    if user_question:
        welcome_text.empty()
        
        if st.session_state.vector_store is None:
            st.warning("Please upload and process documents with a valid OpenRouter token before asking questions.")
            st.stop()
            
        # Display user message
        from src.database import save_message, create_chat_session
        create_chat_session(st.session_state.user["id"], st.session_state.current_session_id)
        
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        save_message(st.session_state.current_session_id, "user", user_question)
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
                    
                    if st.session_state.read_aloud:
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
                            # HTML audio element without 'controls' attribute hides the player
                            audio_html = f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}"></audio>'
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
                    save_message(st.session_state.current_session_id, "assistant", answer)
                except Exception as e:
                    st.error(f"Generation error: {e}")

if __name__ == "__main__":
    main()
