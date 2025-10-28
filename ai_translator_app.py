import streamlit as st
from deep_translator import GoogleTranslator, MyMemoryTranslator
from gtts import gTTS
import os, json
from datetime import datetime

# ----------------------------- #
# Load languages from file
# ----------------------------- #
LANG_FILE = "languages.txt"
if os.path.exists(LANG_FILE):
    with open(LANG_FILE, "r", encoding="utf-8") as f:
        ALL_LANGS = [line.strip() for line in f if line.strip()]
else:
    ALL_LANGS = ["english", "urdu", "chinese", "hindi", "spanish", "french"]

# ----------------------------- #
# Streamlit Config
# ----------------------------- #
st.set_page_config(page_title="🌍 AI Translator", page_icon="🌐")
st.title("🌍 AI Translator by Aisha")
st.write("Translate between **200+ languages** with **voice**, **smart Urdu detection**, and **offline safety** 🎙️")

# ----------------------------- #
# Login System
# ----------------------------- #
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def signup_page():
    st.subheader("🆕 Create Account")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if u in users:
            st.warning("⚠️ Username already exists")
        else:
            users[u] = p
            save_users(users)
            st.success("✅ Signup successful!")
            st.session_state.logged_in = True
            st.session_state.username = u
            st.rerun()

def login_page():
    st.subheader("🔐 Login to Continue")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Login"):
            if u in users and users[u] == p:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.success(f"✅ Welcome {u}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    with c2:
        if st.button("Create Account"):
            st.session_state["signup_mode"] = True
            st.rerun()

if not st.session_state.logged_in:
    if st.session_state.get("signup_mode"):
        signup_page()
    else:
        login_page()
    st.stop()

st.success(f"👋 Logged in as {st.session_state.username}")
st.markdown("---")

# ----------------------------- #
# Translation Section
# ----------------------------- #
text = st.text_area("✍️ Enter text to translate")
target_lang = st.selectbox("🎯 Choose target language", ALL_LANGS, index=0)

def detect_roman_urdu(txt):
    urdu_words = ["main", "tum", "ka", "ha", "kya", "mera", "apna", "tera", "nahi", "kyun", "mein"]
    count = sum(1 for w in urdu_words if w in txt.lower().split())
    return count > 1

def smart_translate(text, target):
    if not text.strip():
        return ""
    try:
        if detect_roman_urdu(text):
            return GoogleTranslator(source="ur", target=target).translate(text)
        try:
            return GoogleTranslator(source="auto", target=target).translate(text)
        except:
            return MyMemoryTranslator(source="auto", target=target).translate(text)
    except Exception as e:
        return f"[Error: {e}]"

def save_history(src, tgt, res):
    with open("Translator_History.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ({st.session_state.username})\n")
        f.write(f"Source: {src}\nTranslated ({tgt}): {res}\n")
        f.write("-"*60 + "\n")

if st.button("🌐 Translate"):
    result = smart_translate(text, target_lang)
    st.text_area("🈸 Translated Text", result, height=120)
    save_history(text, target_lang, result)

    try:
        tts = gTTS(text=result, lang=target_lang)
        tts.save("voice.mp3")
        st.audio("voice.mp3", format="audio/mp3")
        os.remove("voice.mp3")
    except:
        try:
            tts = gTTS(text=result, lang="en")
            tts.save("voice.mp3")
            st.audio("voice.mp3", format="audio/mp3")
            os.remove("voice.mp3")
        except:
            st.warning("🔇 Voice not available for this language")

# Logout
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()
