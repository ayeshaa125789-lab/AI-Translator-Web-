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
# App Layout + SEO
# -----------------------------
st.set_page_config(page_title="🌍 Free AI Translator | 100+ Languages", page_icon="🌍", layout="centered")

st.title("🌍 Free AI Translator by Ashii")
st.write("Translate between 100+ languages with **voice output**, **login system**, and **translation history** — totally free!")

# -----------------------------
# Login / Signup
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
            st.warning("⚠️ Username already exists.")
        elif username.strip() == "" or password.strip() == "":
            st.warning("⚠️ Enter valid details.")
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
try:
    langs_dict = GoogleTranslator(source='auto', target='en').get_supported_languages(as_dict=True)
    name_to_code = {v.lower(): k for k, v in langs_dict.items()}
    sorted_langs = sorted(langs_dict.values())
except Exception:
    st.error("⚠️ Unable to load languages. Check your internet connection.")
    st.stop()

st.success(f"👋 Logged in as {st.session_state.username}")
st.markdown("---")

st.subheader("📝 Enter text to translate:")
text = st.text_area("Type or paste text here", height=100)

target_lang = st.selectbox(
    "🎯 Choose target language:",
    sorted_langs,
    index=sorted_langs.index("English") if "English" in sorted_langs else 0
)

# ✅ Fix: Prevent KeyError (default = English)
target_code = name_to_code.get(target_lang.lower(), "en")

# -----------------------------
# Save Translation History
# -----------------------------
def save_translation(src_text, target_lang, translated):
    with open("Translator_History.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ({st.session_state.username})\n")
        f.write(f"Source: {src_text}\nTranslated ({target_lang}): {translated}\n")
        f.write("-"*60 + "\n")

# -----------------------------
# Translate Button
# -----------------------------
if st.button("🌐 Translate"):
    if text.strip():
        try:
            translated = GoogleTranslator(source='auto', target=target_code).translate(text)
            st.text_area("🈸 Translated text:", translated, height=100)
            save_translation(text, target_lang, translated)

            # Voice Output
            try:
                tts = gTTS(text=translated, lang=target_code)
                tts.save("voice.mp3")
                st.audio("voice.mp3", format="audio/mp3")
                os.remove("voice.mp3")
            except Exception:
                st.warning("🔇 Voice not available for this language.")
        except Exception as e:
            st.error(f"❌ Translation Error: {e}")
    else:
        st.warning("⚠️ Please enter text first.")

# -----------------------------
# Logout
# -----------------------------
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()
