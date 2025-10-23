import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os, json
from datetime import datetime

# -----------------------------
# User System (Login / Signup)
# -----------------------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

# -----------------------------
# App Layout + SEO Meta Tags
# -----------------------------
st.set_page_config(page_title="🌍 Free AI Translator | 100+ Languages", page_icon="🌍", layout="centered")

# ✅ SEO HTML meta tags (for Google search visibility)
st.markdown("""
<meta name="title" content="Free AI Translator | Translate Text in 100+ Languages">
<meta name="description" content="Translate any text between 100+ languages instantly with AI Translator. Free, fast, accurate translation with voice output and login system.">
<meta name="keywords" content="AI translator, free translator, language translator, text to speech, Urdu translator, English to Urdu, multilingual AI, Ashii translator, Streamlit AI app">
<meta name="author" content="Ashii">
<meta property="og:title" content="🌍 Free AI Translator | 100+ Languages">
<meta property="og:description" content="Translate text between 100+ languages with AI Translator — free, fast, and accurate. Built with Streamlit by Ashii.">
<meta property="og:type" content="website">
""", unsafe_allow_html=True)

st.title("🌍 Free AI Translator")
st.write("Translate between 100+ languages with voice output, login system, and translation history — totally **free**!")

# -----------------------------
# Login / Signup System
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def signup_page():
    st.subheader("🆕 Create Account")
    username = st.text_input("Enter username")
    password = st.text_input("Enter password", type="password")

    if st.button("Sign Up"):
        if username in users:
            st.warning("⚠️ Username already exists. Try another.")
        elif username.strip() == "" or password.strip() == "":
            st.warning("⚠️ Please enter valid details.")
        else:
            users[username] = password
            save_users(users)
            st.success("✅ Signup successful! Logging in...")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()

def login_page():
    st.subheader("🔐 Login to Continue")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"✅ Welcome back, {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")
    with col2:
        if st.button("Create Account"):
            st.session_state["signup_mode"] = True
            st.rerun()

if not st.session_state.logged_in:
    if st.session_state.get("signup_mode"):
        signup_page()
    else:
        login_page()
    st.stop()

# -----------------------------
# Translator Section
# -----------------------------
langs_list = GoogleTranslator(source='auto', target='en').get_supported_languages()
langs_codes = GoogleTranslator(source='auto', target='en').get_supported_languages(as_dict=True)
name_to_code = {v.lower(): k for k, v in langs_codes.items()}
sorted_langs = sorted(langs_list)

st.success(f"👋 Logged in as {st.session_state.username}")
st.markdown("---")

st.subheader("📝 Enter text to translate:")
text = st.text_area("Type or paste text here", height=100)

target_lang = st.selectbox(
    "🎯 Choose target language:",
    sorted_langs,
    index=sorted_langs.index("English") if "English" in sorted_langs else 0
)
target_code = name_to_code[target_lang.lower()]

# -----------------------------
# Save Translation History
# -----------------------------
def save_translation(src_text, target_lang, translated):
    with open("Translator_History.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ({st.session_state.username})\n")
        f.write(f"Source: {src_text}\nTranslated ({target_lang}): {translated}\n")
        f.write("-"*50 + "\n")

# -----------------------------
# Translate Button
# -----------------------------
if st.button("🌐 Translate"):
    if text.strip():
        translated = GoogleTranslator(source='auto', target=target_code).translate(text)
        st.text_area("🈸 Translated text:", translated, height=100)
        save_translation(text, target_lang, translated)

        # Voice Output
        try:
            tts = gTTS(text=translated, lang=target_code)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")
            os.remove("voice.mp3")
        except Exception:
            st.warning("⚠️ Voice not available for this language.")
    else:
        st.warning("⚠️ Please enter some text first.")

# -----------------------------
# Logout Button
# -----------------------------
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()
