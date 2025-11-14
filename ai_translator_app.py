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

# -----------------------------
# Optional JSON Files
# -----------------------------
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"

def load_json_safe(path, default):
    try:
        data = json.load(open(path, "r", encoding="utf-8"))
        return data
    except:
        return default

def save_json_safe(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except:
        pass  # ignore errors

users_data = load_json_safe(USERS_FILE, {})
if "users" not in users_data:
    users_data["users"] = {}

history_data = load_json_safe(HISTORY_FILE, {})

# -----------------------------
# Session State
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------
# Language List (200+)
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
# Authentication UI
# -----------------------------
def auth_ui():
    st.title("🌍 AI Translator")
    st.write("Login or Signup to continue.")
    users_db = users_data["users"]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔐 Login")
        lu = st.text_input("Username", key="login_user")
        lp = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if lu in users_db and users_db[lu]["password"] == lp:
                st.session_state.user = lu
                st.success(f"Welcome back, {lu}!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

    with col2:
        st.subheader("🆕 Signup")
        su = st.text_input("Choose username", key="signup_user")
        sp = st.text_input("Choose password", type="password", key="signup_pass")
        if st.button("Create account"):
            if not su or not sp:
                st.warning("Enter username and password.")
            elif su in users_db:
                st.warning("Username already exists.")
            else:
                users_db[su] = {"password": sp}
                users_data["users"] = users_db
                save_json_safe(USERS_FILE, users_data)
                st.success("Account created. You can now login.")

# -----------------------------
# Main App
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
                    # Roman Urdu detection
                    if any(word in text.lower() for word in ["tum", "mera", "kyun", "kaise", "nahi", "acha", "shukriya"]):
                        result = GoogleTranslator(source='ur', target=LANGUAGES[target_lang]).translate(text)
                    else:
                        result = GoogleTranslator(source=LANGUAGES[source_lang], target=LANGUAGES[target_lang]).translate(text)

                    st.subheader(f"🈸 Translation ({source_lang} → {target_lang})")
                    st.text_area("Output", result, height=150)

                    # Voice Output
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

                    # History in memory + optional save
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
                st.warning("Enter some text to translate.")

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
