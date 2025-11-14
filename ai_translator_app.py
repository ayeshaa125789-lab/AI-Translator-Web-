import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyttsx3
import os
import json
from datetime import datetime
from fpdf import FPDF

# -----------------------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🌐", layout="wide")
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"

# JSON helpers
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

# Load data
users_data = load_json_safe(USERS_FILE, {})
if "users" not in users_data:
    users_data["users"] = {}

history_data = load_json_safe(HISTORY_FILE, {})

# Session state
if "user" not in st.session_state:
    st.session_state.user = None

# Languages
LANGUAGES = {
    'English': 'en', 'Urdu': 'ur', 'Spanish': 'es', 'French': 'fr', 'Arabic': 'ar',
    'Hindi': 'hi', 'Chinese (Simplified)': 'zh-CN', 'Russian': 'ru', 'German': 'de'
}

# -----------------------------
# Auth function
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
                st.stop()
                st.rerun()
            else:
                st.error("Invalid username or password.")

    else:
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
                st.session_state.user = new_user
                st.success(f"Account created! Welcome, {new_user}! 🎉")
                st.stop()
                st.rerun()

    if st.session_state.user is None:
        st.stop()

# -----------------------------
# Main App
if st.session_state.user is None:
    auth_ui()
else:
    st.sidebar.write(f"👋 Logged in as **{st.session_state.user}**")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.stop()
        st.rerun()

    st.title("🌍 AI Translator — Translate Instantly")

    col1, col2 = st.columns([3,1])
    with col1:
        text = st.text_area("Enter Text", placeholder="Type or paste text in any language...")

    with col2:
        target_lang = st.selectbox("🎯 Translate To", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index("Urdu"))

        if st.button("🚀 Translate"):
            if text.strip():
                try:
                    result = GoogleTranslator(source='auto', target=LANGUAGES[target_lang]).translate(text)
                    st.subheader(f"🈸 Translation → {target_lang}")
                    st.text_area("Output", result, height=150)

                    # Voice
                    try:
                        tts = gTTS(result, lang=LANGUAGES[target_lang])
                        tts.save("output.mp3")
                        st.audio("output.mp3")
                        os.remove("output.mp3")
                    except:
                        try:
                            engine = pyttsx3.init()
                            engine.save_to_file(result, "output_backup.mp3")
                            engine.runAndWait()
                            st.audio("output_backup.mp3")
                            os.remove("output_backup.mp3")
                        except:
                            st.warning("Audio not supported for this language.")

                    # Save History
                    user = st.session_state.user
                    if user not in history_data:
                        history_data[user] = []
                    history_data[user].append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "to": target_lang,
                        "text": text,
                        "result": result
                    })
                    save_json_safe(HISTORY_FILE, history_data)

                    # PDF Download
                    if st.button("📄 Download as PDF"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 8, f"Original Text:\n{text}\n\nTranslated Text ({target_lang}):\n{result}\n\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        pdf_file = f"translation_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                        pdf.output(pdf_file)
                        with open(pdf_file, "rb") as f:
                            st.download_button("Download PDF", f, file_name=pdf_file, mime="application/pdf")
                        os.remove(pdf_file)

                except Exception as e:
                    st.error(f"⚠️ Translation Error: {e}")
            else:
                st.warning("Enter text to translate.")

    # History
    if st.checkbox("📜 Show History"):
        user_history = history_data.get(st.session_state.user, [])
        if user_history:
            for h in reversed(user_history[-10:]):
                st.markdown(f"**🕒 {h['time']} | → {h['to']}**")
                st.write(f"**Input:** {h['text']}")
                st.write(f"**Output:** {h['result']}")
                st.markdown("---")
        else:
            st.info("No history yet.")
