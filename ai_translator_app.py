import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyttsx3
import os
import json
from datetime import datetime

# -----------------------------
# Config
# -----------------------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🌐", layout="wide")
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"

# -----------------------------
# JSON helpers
# -----------------------------
def load_json_safe(path, default):
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except:
        return default

def save_json_safe(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except:
        pass

# -----------------------------
# Load data
# -----------------------------
users_data = load_json_safe(USERS_FILE, {})
if "users" not in users_data:
    users_data["users"] = {}

history_data = load_json_safe(HISTORY_FILE, {})

# -----------------------------
# Session state
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------
# Languages
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

# -----------------------------
# Auth function
# -----------------------------
def auth_ui():
    st.title("🌍 AI Translator — Login or Signup")
    choice = st.radio("Select Option:", ["Login", "Signup"])
    users_db = users_data["users"]

    if choice == "Login":
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in users_db and users_db[username]["password"] == password:
                st.session_state.user = username
                st.success(f"Welcome back, {username}!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

    else:  # Signup
        new_user = st.text_input("Choose username", key="signup_user")
        new_pass = st.text_input("Choose password", type="password", key="signup_pass")
        if st.button("Create Account"):
            if not new_user or not new_pass:
                st.warning("Enter username and password.")
            elif new_user in users_db:
                st.warning("Username already exists.")
            else:
                users_db[new_user] = {"password": new_pass}
                users_data["users"] = users_db
                save_json_safe(USERS_FILE, users_data)
                st.success("Account created! You can now login.")

    st.stop()

# -----------------------------
# Main
# -----------------------------
if st.session_state.user is None:
    auth_ui()
else:
    st.sidebar.write(f"👋 Logged in as {st.session_state.user}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.experimental_rerun()

    st.title("🌍 AI Translator — Translate Instantly")
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("🌐 From Language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index("English"))
        text = st.text_area("Enter Text", placeholder="Type something...")
    with col2:
        target_lang = st.selectbox("🎯 To Language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index("Urdu"))
        if st.button("🚀 Translate"):
            if text.strip():
                try:
                    result = GoogleTranslator(source=LANGUAGES[source_lang], target=LANGUAGES[target_lang]).translate(text)
                    st.subheader(f"🈸 Translation ({source_lang} → {target_lang})")
                    st.text_area("Output", result, height=150)

                    # Voice output
                    try:
                        tts = gTTS(result, lang=LANGUAGES[target_lang])
                        tts.save("output.mp3")
                        st.audio("output.mp3", format="audio/mp3")
                        os.remove("output.mp3")
                    except:
                        try:
                            engine = pyttsx3.init()
                            engine.save_to_file(result, "output_backup.mp3")
                            engine.runAndWait()
                            st.audio("output_backup.mp3", format="audio/mp3")
                            os.remove("output_backup.mp3")
                        except:
                            st.warning("Audio not supported for this language.")

                    # Save history
                    user = st.session_state.user
                    if user not in history_data:
                        history_data[user] = []
                    history_data[user].append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "from": source_lang,
                        "to": target_lang,
                        "text": text,
                        "result": result
                    })
                    save_json_safe(HISTORY_FILE, history_data)

                except Exception as e:
                    st.error(f"⚠️ Translation Error: {e}")
            else:
                st.warning("Enter text to translate.")

    # History
    if st.checkbox("📜 Show History"):
        user_history = history_data.get(st.session_state.user, [])
        if user_history:
            for h in reversed(user_history[-10:]):
                st.markdown(f"**🕒 {h['time']} | {h['from']} → {h['to']}**")
                st.write(f"**Input:** {h['text']}")
                st.write(f"**Output:** {h['result']}")
                st.markdown("---")
        else:
            st.info("No history yet.")
