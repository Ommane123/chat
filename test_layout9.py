import streamlit as st
from streamlit_mic_recorder import speech_to_text

st.set_page_config(layout="wide")

col1, col2, col3, col4 = st.columns([0.65, 0.2, 0.05, 0.1], vertical_alignment="bottom")
with col1:
    st.title("Test App 9")
with col2:
    st.selectbox("Language", ["English"], label_visibility="collapsed")
with col3:
    st.button("🔊", use_container_width=True)
with col4:
    voice_input = speech_to_text(language='en', start_prompt="🎙️ Voice", stop_prompt="⏹️ Stop", just_once=True, key='STT', use_container_width=True)

user_question = st.chat_input("Ask...")

if voice_input:
    st.write("Voice:", voice_input)
if user_question:
    st.write("Typed:", user_question)
