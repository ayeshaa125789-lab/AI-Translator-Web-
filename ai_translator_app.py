import streamlit as st
import json
import os
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
from langdetect import detect
from fuzzywuzzy import process
from streamlit_audiorecorder import audiorecorder
import speech_recognition as sr

# ------------------------------
# USER DATABASE HANDLING
# ------------------------------
DB_FILE = "users.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}}, f)


def load_users():
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ------------------------------
# UI SETTINGS
# ------------------------------
st.set_page_config(page_title="AI Translator", page_icon="🌍", layout="centered")

st.markdown("""
    <style>
        .title {text-align:center; font-size:40px; font-weight:800; margin-bottom:20px;}
        .subtitle {text-align:center; font-size:20px; opacity:0.7;}
        .box {padding:20px; border-radius:12px; background-color:#F7F7F9; margin-top:20px;}
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# LOGIN + SIGNUP PAGE
# ------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.markdown("<div class='title'>🌍 Multi-Language AI Translator</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Login or Create an Account</div>", unsafe_allow_html=True)

    option = st.radio("Select Option:", ["Login", "Signup"])

    users = load_users()["users"]

    if option == "Signup":
        st.subheader("Create Your Account")
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Sign Up"):
            if new_user in users:
                st.error("Username already exists!")
            else:
                users[new_user] = {"password": new_pass}
                save_users({"users": users})
                st.success("Account created! Now login.")

    if option == "Login":
        st.subheader("Login to Continue")
        user = st.text_input("Username")
        passwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if user in users and users[user]["password"] == passwd:
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.stop()

# ------------------------------
# DASHBOARD AFTER LOGIN
# ------------------------------

st.sidebar.title("Menu")
page = st.sidebar.radio("Navigate", ["Translator", "History", "Logout"])

st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")

if page == "Logout":
    st.session_state.logged_in = False
    st.rerun()

# ------------------------------
# TRANSLATOR PAGE
# ------------------------------
if page == "Translator":

    st.markdown("<div class='title'>🌎 AI Translator (200+ Languages)</div>", unsafe_allow_html=True)

    supported_langs = GoogleTranslator().get_supported_languages()

    col1, col2 = st.columns(2)

    with col1:
        source_lang = st.selectbox("From Language", supported_langs)
    with col2:
        target_lang = st.selectbox("To Language", supported_langs, index=supported_langs.index("english"))

    st.markdown("### Enter Text to Translate")
    text = st.text_area("Input Text", height=160)

    # ---------------- Voice Input ----------------
    st.subheader("🎤 Voice Input (Speak to Translate)")
    audio = audiorecorder("Start Recording", "Stop Recording")

    voice_text = ""

    if audio and len(audio) > 0:
        with open("voice_input.wav", "wb") as f:
            f.write(audio.tobytes())

        st.audio(audio.tobytes(), format="audio/wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile("voice_input.wav") as source:
            audio_data = recognizer.record(source)
            try:
                voice_text = recognizer.recognize_google(audio_data)
                st.success(f"Detected: {voice_text}")
            except:
                st.error("Sorry, couldn't detect your voice clearly.")

    final_input = text if text.strip() != "" else voice_text

    translated = ""

    if st.button("Translate Now"):
        if final_input.strip() == "":
            st.error("Enter text or use voice input first.")
        else:
            try:
                translated = GoogleTranslator(source=source_lang, target=target_lang).translate(final_input)
                st.success("Translation Successful!")
                st.write("### 🌐 Translated Text:")
                st.info(translated)
            except Exception as e:
                st.error("Translation failed.")

    # ---------------- TEXT TO SPEECH ----------------
    if translated:
        st.subheader("🔊 Listen to Translation")

        audio_file = BytesIO()
        tts = gTTS(translated, slow=False)
        tts.write_to_fp(audio_file)
        st.audio(audio_file.getvalue(), format="audio/mp3")

# ------------------------------
# HISTORY PAGE (DUMMY)
# ------------------------------
if page == "History":
    st.markdown("<div class='title'>📜 Translation History</div>", unsafe_allow_html=True)
    st.info("History feature can be connected to database if you want. For now, it's a placeholder.")
