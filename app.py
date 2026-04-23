import streamlit as st
import os
from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

load_dotenv()

from src.document_processor import process_uploaded_files
from src.embedding_store import create_vector_store
from src.chatbot import get_answer
from src.theme_manager import set_streamlit_theme
from src.database import update_user_profile

TRANSLATIONS = {
    "English": {
        "title": "🤖 AI-Powered Software Support Chatbot",
        "response_language": "Response Language",
        "toggle_read_aloud": "Toggle Read Aloud",
        "welcome_desc": "Upload your documentation and ask questions based on its content.",
        "new_chat": "➕ New Chat",
        "logout": "🚪 Logout",
        "settings": "⚙️ Settings",
        "your_documents": "Your Documents",
        "upload_desc": "Upload PDFs, TXT, or DOCX files",
        "process_docs": "Process Documents",
        "history": "📜 History",
        "no_past_chats": "No past chats available.",
        "ask_question": "Ask a question about your documents:",
        "thinking": "Thinking...",
        "please_upload": "Please upload and process documents with a valid OpenRouter token before asking questions.",
        "error_no_token": "Please provide an OpenRouter API Token first.",
        "error_no_docs": "Please upload at least one document.",
        "error_no_text": "No valid text found to process in the documents.",
        "success_processed": "Processed into {} text chunks.",
        "success_stored": "Documents stored in in-memory Vector DB.",
        "success_ready": "Conversational AI Ready!",
        "error_vector": "Error creating vector store.",
        "empty_chat": "Empty Chat",
        "manage_account": "Manage your account and preferences.",
        "danger_zone": "Danger Zone",
        "delete_desc": "Deleting your account is irreversible. All chat history and data will be erased.",
        "delete_account": "Delete Account",
        "are_you_sure": "Are you sure? This cannot be undone.",
        "yes_delete": "Yes, Delete",
        "cancel": "Cancel",
        "references": "References",
        "source": "Source",
        "profile": "Profile",
        "username": "Username",
        "email": "Email",
        "password": "New Password (leave blank to keep current)",
        "save_changes": "Save Changes",
        "theme": "Appearance (Theme)",
        "language": "Website Language",
        "light": "Light",
        "dark": "Dark",
        "changes_saved": "Profile updated successfully!",
        "error_username": "Username already exists."
    },
    "Marathi": {
        "title": "🤖 AI-संचलित सॉफ्टवेअर सपोर्ट चॅटबॉट",
        "response_language": "प्रतिसादाची भाषा",
        "toggle_read_aloud": "वाचन टॉगल करा",
        "welcome_desc": "तुमची कागदपत्रे अपलोड करा आणि त्याच्या आधारावर प्रश्न विचारा.",
        "new_chat": "➕ नवीन चॅट",
        "logout": "🚪 लॉगआउट",
        "settings": "⚙️ सेटिंग्ज",
        "your_documents": "तुमची कागदपत्रे",
        "upload_desc": "PDFs, TXT किंवा DOCX फाईल्स अपलोड करा",
        "process_docs": "कागदपत्रांवर प्रक्रिया करा",
        "history": "📜 इतिहास",
        "no_past_chats": "कोणतेही जुने चॅट्स उपलब्ध नाहीत.",
        "ask_question": "तुमच्या कागदपत्रांबद्दल एक प्रश्न विचारा:",
        "thinking": "विचार करत आहे...",
        "please_upload": "कृपया प्रश्न विचारण्यापूर्वी वैध OpenRouter टोकनसह कागदपत्रे अपलोड करा.",
        "error_no_token": "कृपया प्रथम OpenRouter API टोकन द्या.",
        "error_no_docs": "कृपया किमान एक कागदपत्र अपलोड करा.",
        "error_no_text": "प्रक्रिया करण्यासाठी कागदपत्रांमध्ये कोणताही वैध मजकूर सापडला नाही.",
        "success_processed": "{} मजकूर खंडांमध्ये प्रक्रिया केली.",
        "success_stored": "इन-मेमरी व्हेक्टर डीबी मध्ये कागदपत्रे साठवली.",
        "success_ready": "संवादात्मक AI तयार आहे!",
        "error_vector": "व्हेक्टर स्टोअर तयार करताना त्रुटी.",
        "empty_chat": "रिकामे चॅट",
        "manage_account": "तुमचे खाते आणि प्राधान्ये व्यवस्थापित करा.",
        "danger_zone": "धोकादायक क्षेत्र",
        "delete_desc": "तुमचे खाते हटवणे अपरिवर्तनीय आहे. सर्व चॅट इतिहास आणि डेटा पुसला जाईल.",
        "delete_account": "खाते हटवा",
        "are_you_sure": "तुमची खात्री आहे का? हे बदलता येणार नाही.",
        "yes_delete": "होय, हटवा",
        "cancel": "रद्द करा",
        "references": "संदर्भ",
        "source": "स्रोत",
        "profile": "प्रोफाइल",
        "username": "वापरकर्तानाव",
        "email": "ईमेल",
        "password": "नवीन पासवर्ड (सध्याचा ठेवण्यासाठी रिक्त सोडा)",
        "save_changes": "बदल जतन करा",
        "theme": "देखावा (थीम)",
        "language": "वेबसाइटची भाषा",
        "light": "प्रकाश",
        "dark": "अंधार",
        "changes_saved": "प्रोफाइल यशस्वीरित्या अद्यतनित केले!",
        "error_username": "वापरकर्तानाव आधीपासून अस्तित्वात आहे."
    },
    "Hindi": {
        "title": "🤖 AI-संचालित सॉफ्टवेयर सपोर्ट चैटबॉट",
        "response_language": "प्रतिक्रिया की भाषा",
        "toggle_read_aloud": "पढ़ना टॉगल करें",
        "welcome_desc": "अपने दस्तावेज़ अपलोड करें और उसके आधार पर प्रश्न पूछें।",
        "new_chat": "➕ नई चैट",
        "logout": "🚪 लॉगआउट",
        "settings": "⚙️ सेटिंग्स",
        "your_documents": "आपके दस्तावेज़",
        "upload_desc": "PDFs, TXT या DOCX फ़ाइलें अपलोड करें",
        "process_docs": "दस्तावेज़ संसाधित करें",
        "history": "📜 इतिहास",
        "no_past_chats": "कोई पिछली चैट उपलब्ध नहीं है।",
        "ask_question": "अपने दस्तावेज़ों के बारे में एक प्रश्न पूछें:",
        "thinking": "सोच रहा है...",
        "please_upload": "कृपया प्रश्न पूछने से पहले वैध OpenRouter टोकन के साथ दस्तावेज़ अपलोड करें।",
        "error_no_token": "कृपया पहले OpenRouter API टोकन प्रदान करें।",
        "error_no_docs": "कृपया कम से कम एक दस्तावेज़ अपलोड करें।",
        "error_no_text": "संसाधित करने के लिए दस्तावेज़ों में कोई वैध पाठ नहीं मिला।",
        "success_processed": "{} पाठ खंडों में संसाधित किया गया।",
        "success_stored": "इन-मेमोरी वेक्टर डीबी में दस्तावेज़ संग्रहीत।",
        "success_ready": "संवादात्मक AI तैयार है!",
        "error_vector": "वेक्टर स्टोर बनाने में त्रुटि।",
        "empty_chat": "खाली चैट",
        "manage_account": "अपना खाता और प्राथमिकताएं प्रबंधित करें।",
        "danger_zone": "खतरे का क्षेत्र",
        "delete_desc": "आपका खाता हटाना अपरिवर्तनीय है। सभी चैट इतिहास और डेटा मिटा दिया जाएगा।",
        "delete_account": "खाता हटाएं",
        "are_you_sure": "क्या आपको यकीन है? इसे पूर्ववत नहीं किया जा सकता।",
        "yes_delete": "हां, हटाएं",
        "cancel": "रद्द करें",
        "references": "संदर्भ",
        "source": "स्रोत",
        "profile": "प्रोफ़ाइल",
        "username": "उपयोगकर्ता नाम",
        "email": "ईमेल",
        "password": "नया पासवर्ड (वर्तमान रखने के लिए रिक्त छोड़ दें)",
        "save_changes": "परिवर्तन सहेजें",
        "theme": "दिखावट (थीम)",
        "language": "वेबसाइट की भाषा",
        "light": "रोशनी",
        "dark": "अंधेरा",
        "changes_saved": "प्रोफ़ाइल सफलतापूर्वक अपडेट की गई!",
        "error_username": "उपयोगकर्ता नाम पहले से मौजूद है।"
    }
}

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
    if "app_language" not in st.session_state:
        st.session_state.app_language = "English"
    if "app_theme" not in st.session_state:
        st.session_state.app_theme = "Dark" # Default or maybe read from config

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
    t = TRANSLATIONS[st.session_state.app_language]
    
    col1, col2, col3 = st.columns([0.7, 0.2, 0.1], vertical_alignment="bottom")
    with col1:
        st.title(t["title"])
    with col2:
        target_language = st.selectbox(
            t["response_language"], 
            ["English", "Hindi", "Marathi", "Gujarati", "Bengali", "Spanish", "French", "German", "Japanese"],
            label_visibility="collapsed"
        )
    with col3:
        icon = "🔊" if st.session_state.read_aloud else "🔈"
        st.button(icon, on_click=toggle_read_aloud, help=t["toggle_read_aloud"], use_container_width=True)
        
    welcome_text = st.empty()
    if not st.session_state.chat_history:
        welcome_text.markdown(t["welcome_desc"])
    
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
        st.button(t["new_chat"], help=t["new_chat"], on_click=handle_new_chat, use_container_width=True, type="primary")
        if st.button(t["logout"], use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
        if st.button(t["settings"], use_container_width=True):
            st.session_state.show_settings_page = True
            st.rerun()
        
        st.divider()
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        st.subheader(t["your_documents"])
        uploaded_files = st.file_uploader(
            t["upload_desc"], 
            type=["pdf", "txt", "docx"], 
            accept_multiple_files=True,
            key=f"file_uploader_{st.session_state.current_session_id}"
        )
        
        process_button = st.button(t["process_docs"])
        
        if process_button:
            if not api_key:
                st.error(t["error_no_token"])
            elif not uploaded_files:
                st.error(t["error_no_docs"])
            else:
                with st.spinner(t["thinking"]):
                    # 1. Process and chunk
                    text_chunks = process_uploaded_files(uploaded_files)
                    if not text_chunks:
                        st.error(t["error_no_text"])
                    else:
                        st.success(t["success_processed"].format(len(text_chunks)))
                        
                        # 2. Embed and store
                        vector_store = create_vector_store(text_chunks)
                        if vector_store:
                            st.session_state.vector_store = vector_store
                            st.success(t["success_stored"])
                            st.success(t["success_ready"])
                        else:
                            st.error(t["error_vector"])
                            
        st.divider()
        st.subheader(t["history"])
        from src.database import get_user_sessions, get_session_messages, delete_chat_session
        sessions = get_user_sessions(st.session_state.user["id"])
        
        if not sessions:
            st.info(t["no_past_chats"])
            
        for session_id in sessions:
            messages = get_session_messages(session_id)
            first_msg = messages[0]["content"] if messages else t["empty_chat"]
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
        st.header(t["settings"])
        st.write(t["manage_account"])
        
        # Profile Section
        with st.container(border=True):
            st.subheader(t["profile"])
            st.text_input(t["email"], value=st.session_state.user.get("email", ""), disabled=True)
            new_username = st.text_input(t["username"], value=st.session_state.user.get("username", ""))
            new_password = st.text_input(t["password"], type="password")
            
            if st.button(t["save_changes"]):
                pwd = new_password if new_password else None
                success = update_user_profile(st.session_state.user["id"], new_username, pwd)
                if success:
                    st.session_state.user["username"] = new_username
                    st.success(t["changes_saved"])
                else:
                    st.error(t["error_username"])
        
        # Appearance and Language
        with st.container(border=True):
            st.subheader(t["theme"])
            # The session state value for theme
            theme_opts = ["Light", "Dark"]
            theme_idx = theme_opts.index(st.session_state.app_theme) if st.session_state.app_theme in theme_opts else 1
            selected_theme = st.radio(t["theme"], theme_opts, index=theme_idx, horizontal=True, label_visibility="collapsed")
            if selected_theme != st.session_state.app_theme:
                st.session_state.app_theme = selected_theme
                set_streamlit_theme(selected_theme)
                st.rerun()
            
            st.subheader(t["language"])
            lang_opts = ["English", "Hindi", "Marathi"]
            lang_idx = lang_opts.index(st.session_state.app_language) if st.session_state.app_language in lang_opts else 0
            selected_lang = st.selectbox(t["language"], lang_opts, index=lang_idx, label_visibility="collapsed")
            if selected_lang != st.session_state.app_language:
                st.session_state.app_language = selected_lang
                st.rerun()
                
        # Danger Zone
        with st.container(border=True):
            st.subheader(t["danger_zone"])
            st.write(t["delete_desc"])
            
            if st.button(t["delete_account"], type="primary"):
                st.session_state.confirm_delete = True
                
            if st.session_state.get("confirm_delete", False):
                st.error(t["are_you_sure"])
                col_y, col_n = st.columns(2)
                with col_y:
                    if st.button(t["yes_delete"], type="primary", use_container_width=True):
                        from src.database import delete_user_account
                        delete_user_account(st.session_state.user["id"])
                        st.session_state.clear()
                        st.rerun()
                with col_n:
                    if st.button(t["cancel"], use_container_width=True):
                        st.session_state.confirm_delete = False
                        st.rerun()
        
        # Return to chat button
        if st.button("⬅️ Back to Chat"):
            st.session_state.show_settings_page = False
            st.rerun()
            
        return

    # Main Chat Area
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Input Area
    user_question = st.chat_input(t["ask_question"])
    
    if user_question:
        welcome_text.empty()
        
        if st.session_state.vector_store is None:
            st.warning(t["please_upload"])
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
            with st.spinner(t["thinking"]):
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
                        with st.expander(t["references"]):
                            for i, doc in enumerate(response["source_documents"]):
                                st.write(f"**{t['source']} {i+1}:**")
                                st.info(doc[:300] + "...")
                                
                    # Save assistant message
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    save_message(st.session_state.current_session_id, "assistant", answer)
                except Exception as e:
                    st.error(f"Generation error: {e}")

if __name__ == "__main__":
    main()
