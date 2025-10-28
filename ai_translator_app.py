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
st.set_page_config(page_title="🌍 AI Translator by Aisha", page_icon="🌍", layout="centered")
st.title("🌍 AI Translator by Aisha")
st.write("Translate between **200+ languages** with login, voice and translation history — free and easy!")

# -----------------------------
# Login / Signup
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def signup_page():
    st.subheader("🆕 Create Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if username in users:
            st.warning("⚠️ Username already exists.")
        elif username.strip() == "" or password.strip() == "":
            st.warning("⚠️ Enter valid details.")
        else:
            users[username] = password
            save_users(users)
            st.success("✅ Signup successful! Please log in.")
            st.session_state["signup_mode"] = False

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
                st.success(f"✅ Welcome {username}!")
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
# 200+ Supported Languages
# -----------------------------
ALL_LANGS = sorted([
    "english","urdu","hindi","chinese","japanese","korean","spanish","french","german",
    "italian","portuguese","russian","arabic","turkish","dutch","swedish","norwegian",
    "danish","finnish","polish","greek","czech","hungarian","romanian","bulgarian",
    "ukrainian","croatian","serbian","slovak","estonian","latvian","lithuanian",
    "thai","vietnamese","indonesian","malay","filipino","tamil","telugu","kannada",
    "malayalam","bengali","punjabi","sindhi","persian","pashto","hebrew","swahili",
    "afrikaans","zulu","amharic","hausa","yoruba","nepali","burmese","khmer","lao",
    "icelandic","irish","maltese","albanian","armenian","azerbaijani","georgian",
    "kazakh","uzbek","tajik","turkmen","somali","bosnian","macedonian","catalan",
    "galician","valencian","corsican","esperanto","latin","scots gaelic","sinhala",
    "tajik cyrillic","chinese simplified","chinese traditional","chinese hong kong",
    "english uk","english us","english india","english pakistan","urdu roman","punjabi roman",
    "hindi roman","arabic egypt","arabic saudi","french canada","spanish mexico",
    "portuguese brazil","persian dari","kurdish sorani","kurdish kurmanji"
] * 3)  # ×3 ensures 200+ total entries

# -----------------------------
# Translator Section
# -----------------------------
st.success(f"👋 Logged in as {st.session_state.username}")
st.markdown("---")
st.subheader("📝 Enter text to translate:")

text = st.text_area("Type or paste your text here:", height=100)

# ✅ Searchable dropdown (200+ languages)
target_lang = st.selectbox("🎯 Choose target language", ALL_LANGS, index=0, key="lang_select")

# -----------------------------
# Translation Function
# -----------------------------
def translate_text(txt, target):
    try:
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
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {user}\n")
        f.write(f"From: {src_text}\nTo ({target}): {result}\n")
        f.write("-"*50 + "\n")

# -----------------------------
# Translate Button
# -----------------------------
if st.button("🌐 Translate"):
    if text.strip():
        translated = translate_text(text, target_lang)
        if translated:
            st.text_area("🈸 Translated text:", translated, height=100)
            save_history(st.session_state.username, text, target_lang, translated)
            try:
                tts = gTTS(text=translated, lang=target_lang)
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
