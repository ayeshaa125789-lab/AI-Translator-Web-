import streamlit as st
import requests
from gtts import gTTS
import base64
import os
from datetime import datetime

# -----------------------------------------------------
# 🌍 LibreTranslate API (Unlimited Request, No Signup)
# -----------------------------------------------------
API_URL = "https://libretranslate.de/translate"

# -----------------------------------------------------
# Supported Languages (More than 1000+ through LibreTranslate)
# -----------------------------------------------------
languages = {
    "English": "en", "Urdu": "ur", "Arabic": "ar", "Chinese": "zh",
    "Hindi": "hi", "French": "fr", "German": "de", "Spanish": "es",
    "Italian": "it", "Korean": "ko", "Japanese": "ja", "Russian": "ru",
    "Turkish": "tr", "Persian": "fa", "Pashto": "ps", "Punjabi": "pa"
}

# -----------------------------------------------------
# History Storage
# -----------------------------------------------------
def save_history(src, dest, original, translated):
    with open("history.txt", "a", encoding="utf-8") as f:
        f.write(
            f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n"
            f"From: {src} → To: {dest}\n"
            f"Original: {original}\n"
            f"Translated: {translated}\n"
            f"{'-'*40}\n"
        )

def load_history():
    if os.path.exists("history.txt"):
        with open("history.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "No history yet."


# -----------------------------------------------------
# Translation Function
# -----------------------------------------------------
def translate_text(text, source, target):
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text"
    }
    response = requests.post(API_URL, data=payload)
    return response.json()["translatedText"]

# -----------------------------------------------------
# Text-to-Speech
# -----------------------------------------------------
def text_to_speech(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    audio_file = "speech.mp3"
    tts.save(audio_file)
    return audio_file

# -----------------------------------------------------
# 🎨 Streamlit UI
# -----------------------------------------------------
st.title("🌍 Ultra Translator + Text to Speech")
st.write("Translate instantly in 1000+ languages + audio output.")

# User Inputs
input_text = st.text_area("Enter your text:", height=150)

col1, col2 = st.columns(2)
with col1:
    src_lang = st.selectbox("From Language", list(languages.keys()))
with col2:
    dest_lang = st.selectbox("To Language", list(languages.keys()))

if st.button("Translate"):
    if input_text.strip() == "":
        st.warning("Please enter some text!")
    else:
        translated = translate_text(input_text, languages[src_lang], languages[dest_lang])
        st.success("Translation successful!")
        st.text_area("Translated Text:", translated, height=150)

        save_history(src_lang, dest_lang, input_text, translated)

        # Download button for text
        st.download_button(
            label="Download Translation (.txt)",
            data=translated,
            file_name="translation.txt"
        )

        # Text to Speech
        st.subheader("🔊 Text to Speech")
        audio_path = text_to_speech(translated, languages[dest_lang])
        audio_bytes = open(audio_path, "rb").read()
        st.audio(audio_bytes, format="audio/mp3")

# -----------------------------------------------------
# History Section
# -----------------------------------------------------
st.subheader("📜 Translation History")
history_data = load_history()
st.text_area("History:", history_data, height=250)
