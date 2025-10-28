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
# Streamlit Config
# -----------------------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🌍", layout="centered")
st.title("🌍 AI Translator by Aisha")
st.write("Translate between **200+ supported languages**, with login, voice, and translation history — all free!")

# -----------------------------
# Login State
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -----------------------------
# Signup + Auto Login
# -----------------------------
def signup_page():
    st.subheader("🆕 Create Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if username in users:
            st.warning("⚠️ Username already exists. Try Login.")
        elif username.strip() == "" or password.strip() == "":
            st.warning("⚠️ Enter valid details.")
        else:
            users[username] = password
            save_users(users)
            st.success("✅ Account created successfully! Logging you in...")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state["signup_mode"] = False
            st.rerun()

# -----------------------------
# Login Page
# -----------------------------
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

# -----------------------------
# Authentication Control
# -----------------------------
if not st.session_state.logged_in:
    if st.session_state.get("signup_mode"):
        signup_page()
    else:
        login_page()
    st.stop()

# -----------------------------
# Supported Languages (Full Names)
# -----------------------------
SUPPORTED_LANGS = GoogleTranslator().get_supported_languages(as_dict=True)
LANG_MAP = {v: k for k, v in SUPPORTED_LANGS.items()}
LANG_NAMES = sorted(list(LANG_MAP.keys()))

# -----------------------------
# Translator Section
# -----------------------------
st.success(f"👋 Logged in as {st.session_state.username}")
st.markdown("---")
st.subheader("📝 Enter text to translate:")

text = st.text_area("Type or paste your text here:", height=100)

target_lang = st.selectbox(
    "🎯 Choose target language:",
    LANG_NAMES,
    index=LANG_NAMES.index("English") if "English" in LANG_NAMES else 0
)
target_code = LANG_MAP[target_lang]

# -----------------------------
# Smart Translation
# -----------------------------
def translate_text(txt, target):
    try:
        # Roman Urdu detection fix
        if target == "ur" and all(ch.isascii() for ch in txt):
            translated = GoogleTranslator(source='en', target='ur').translate(txt)
        # Roman Urdu to English (reverse fix)
        elif target == "en" and any(word in txt.lower() for word in ["tum", "mujhe", "mera", "kyu", "kyun", "kaise", "nahi"]):
            translated = GoogleTranslator(source='ur', target='en').translate(txt)
        else:
            translated = GoogleTranslator(source='auto', target=target).translate(txt)
        return translated
    except Exception as e:
        st.error(f"Translation Error: {e}")
        return None

# -----------------------------
# Save History
# -----------------------------
def save_history(user, src_text, target, result):
    with open("translation_history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ({user})\n")
        f.write(f"From: {src_text}\nTo ({target}): {result}\n")
        f.write("-"*50 + "\n")

# -----------------------------
# Translate Button
# -----------------------------
if st.button("🌐 Translate"):
    if text.strip():
        translated = translate_text(text, target_code)
        if translated:
            st.text_area("🈸 Translated text:", translated, height=100)
            save_history(st.session_state.username, text, target_lang, translated)
            try:
                tts = gTTS(text=translated, lang=target_code)
                tts.save("voice.mp3")
                st.audio("voice.mp3", format="audio/mp3")
                os.remove("voice.mp3")
            except:
                st.warning("🔇 Voice not available for this language.")
    else:
        st.warning("⚠️ Please enter some text first.")

# -----------------------------
# Logout
# -----------------------------
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()
