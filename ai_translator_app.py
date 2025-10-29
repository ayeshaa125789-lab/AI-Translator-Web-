import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyttsx3
import os, json
from datetime import datetime

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🌐", layout="wide")
st.title("🌍 AI Translator — Translate Instantly in 200+ Languages")

# -----------------------------
# Full Language List (200+)
# -----------------------------
LANGUAGES = {
    'Afrikaans': 'af', 'Albanian': 'sq', 'Amharic': 'am', 'Arabic': 'ar', 'Armenian': 'hy',
    'Assamese': 'as', 'Azerbaijani': 'az', 'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn',
    'Bosnian': 'bs', 'Bulgarian': 'bg', 'Catalan': 'ca', 'Cebuano': 'ceb', 'Chichewa': 'ny',
    'Chinese (Simplified)': 'zh-CN', 'Chinese (Traditional)': 'zh-TW', 'Corsican': 'co',
    'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English': 'en',
    'Esperanto': 'eo', 'Estonian': 'et', 'Filipino': 'tl', 'Finnish': 'fi', 'French': 'fr',
    'Frisian': 'fy', 'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el',
    'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hausa': 'ha', 'Hawaiian': 'haw', 'Hebrew': 'he',
    'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu', 'Icelandic': 'is', 'Igbo': 'ig',
    'Indonesian': 'id', 'Irish': 'ga', 'Italian': 'it', 'Japanese': 'ja', 'Javanese': 'jw',
    'Kannada': 'kn', 'Kazakh': 'kk', 'Khmer': 'km', 'Kinyarwanda': 'rw', 'Korean': 'ko',
    'Kurdish': 'ku', 'Kyrgyz': 'ky', 'Lao': 'lo', 'Latin': 'la', 'Latvian': 'lv',
    'Lithuanian': 'lt', 'Luxembourgish': 'lb', 'Macedonian': 'mk', 'Malagasy': 'mg',
    'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt', 'Maori': 'mi', 'Marathi': 'mr',
    'Mongolian': 'mn', 'Myanmar (Burmese)': 'my', 'Nepali': 'ne', 'Norwegian': 'no',
    'Odia (Oriya)': 'or', 'Pashto': 'ps', 'Persian': 'fa', 'Polish': 'pl', 'Portuguese': 'pt',
    'Punjabi': 'pa', 'Romanian': 'ro', 'Russian': 'ru', 'Samoan': 'sm', 'Scots Gaelic': 'gd',
    'Serbian': 'sr', 'Sesotho': 'st', 'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala': 'si',
    'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so', 'Spanish': 'es', 'Sundanese': 'su',
    'Swahili': 'sw', 'Swedish': 'sv', 'Tajik': 'tg', 'Tamil': 'ta', 'Tatar': 'tt',
    'Telugu': 'te', 'Thai': 'th', 'Turkish': 'tr', 'Turkmen': 'tk', 'Ukrainian': 'uk',
    'Urdu': 'ur', 'Uyghur': 'ug', 'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy',
    'Xhosa': 'xh', 'Yiddish': 'yi', 'Yoruba': 'yo', 'Zulu': 'zu'
}

USER_FILE = "users.json"
HISTORY_FILE = "history.json"

# -----------------------------
# JSON Helper Functions
# -----------------------------
def load_json(path):
    return json.load(open(path, "r", encoding="utf-8")) if os.path.exists(path) else {}

def save_json(path, data):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=4, ensure_ascii=False)

users = load_json(USER_FILE)
history = load_json(HISTORY_FILE)

# -----------------------------
# Session System
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

def save_session():
    json.dump({"user": st.session_state.user}, open("session.json", "w"))

def load_session():
    if os.path.exists("session.json"):
        data = json.load(open("session.json"))
        st.session_state.user = data.get("user")

load_session()

# -----------------------------
# Login / Signup
# -----------------------------
if not st.session_state.user:
    choice = st.radio("Choose option:", ["🔐 Login", "🆕 Signup"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "🔐 Login":
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state.user = username
                save_session()
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    else:
        if st.button("Signup"):
            if username.strip() == "" or password.strip() == "":
                st.warning("Enter valid details.")
            elif username in users:
                st.warning("Username already exists.")
            else:
                users[username] = password
                save_json(USER_FILE, users)
                st.session_state.user = username
                save_session()
                st.success("Account created successfully!")
                st.rerun()
    st.stop()

# -----------------------------
# Translator UI
# -----------------------------
st.success(f"👋 Logged in as: {st.session_state.user}")

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("🌐 From Language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index("English"))
    text = st.text_area("Enter Text", placeholder="Type something to translate...")
with col2:
    target_lang = st.selectbox("🎯 To Language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index("Urdu"))
    translate_btn = st.button("🚀 Translate")

st.markdown("---")

# -----------------------------
# Translation Logic
# -----------------------------
if translate_btn and text.strip():
    try:
        # Roman Urdu handling — detects if English letters but Urdu-style words
        if any(word in text.lower() for word in ["tum", "mera", "kyun", "kaise", "nahi", "acha", "shukriya"]):
            result = GoogleTranslator(source='ur', target=LANGUAGES[target_lang]).translate(text)
        else:
            result = GoogleTranslator(source=LANGUAGES[source_lang], target=LANGUAGES[target_lang]).translate(text)

        st.subheader(f"🈸 Translation Result ({source_lang} → {target_lang})")
        st.text_area("Output", result, height=150)

        # 🔊 Voice Output (gTTS + fallback)
        try:
            tts = gTTS(result, lang=LANGUAGES[target_lang])
            tts.save("output.mp3")
            st.audio("output.mp3", format="audio/mp3")
            os.remove("output.mp3")
        except:
            st.warning("🎙️ gTTS voice not available, using backup engine...")
            try:
                engine = pyttsx3.init()
                engine.save_to_file(result, "output_backup.mp3")
                engine.runAndWait()
                st.audio("output_backup.mp3", format="audio/mp3")
                os.remove("output_backup.mp3")
            except Exception as e2:
                st.error(f"❌ Audio error: {e2}")

        # Save translation history
        user = st.session_state.user
        if user not in history:
            history[user] = []
        history[user].append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": source_lang,
            "to": target_lang,
            "text": text,
            "result": result
        })
        save_json(HISTORY_FILE, history)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("Enter text and click Translate to start.")

# -----------------------------
# History Section
# -----------------------------
if st.checkbox("📜 Show History"):
    user_history = history.get(st.session_state.user, [])
    if user_history:
        for h in reversed(user_history[-10:]):
            st.markdown(f"**🕒 {h['time']} | {h['from']} → {h['to']}**")
            st.write(f"**Input:** {h['text']}")
            st.write(f"**Output:** {h['result']}")
            st.markdown("---")
    else:
        st.info("No history yet.")

# -----------------------------
# Logout
# -----------------------------
if st.button("🚪 Logout"):
    st.session_state.user = None
    if os.path.exists("session.json"):
        os.remove("session.json")
    st.rerun()

st.caption("🌎 Built with ❤️ by Aisha using Streamlit, GoogleTranslator & gTTS.")
