import streamlit as st
import os
import json
from datetime import datetime

# Check and install missing packages
try:
    from deep_translator import GoogleTranslator
except ImportError:
    st.error("⚠️ deep-translator package not installed. Please install it using: pip install deep-translator")
    st.stop()

try:
    from gtts import gTTS
except ImportError:
    st.warning("gTTS not available. Audio features will be limited.")

try:
    import pyttsx3
except ImportError:
    st.warning("pyttsx3 not available. Backup audio features disabled.")

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="🌍 AI Translator", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🌍 AI Translator — Translate Instantly")

# -----------------------------
# Language List (Reduced for reliability)
# -----------------------------
LANGUAGES = {
    'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de', 
    'Italian': 'it', 'Portuguese': 'pt', 'Russian': 'ru', 'Chinese (Simplified)': 'zh-CN',
    'Japanese': 'ja', 'Korean': 'ko', 'Arabic': 'ar', 'Hindi': 'hi', 
    'Bengali': 'bn', 'Urdu': 'ur', 'Turkish': 'tr', 'Dutch': 'nl',
    'Greek': 'el', 'Hebrew': 'he', 'Thai': 'th', 'Vietnamese': 'vi',
    'Indonesian': 'id', 'Malay': 'ms', 'Filipino': 'tl', 'Swahili': 'sw'
}

# File paths
USER_FILE = "users.json"
HISTORY_FILE = "history.json"
SESSION_FILE = "session.json"

# -----------------------------
# Helper Functions
# -----------------------------
def load_json(path):
    """Safely load JSON file"""
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

def save_json(path, data):
    """Safely save JSON file"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def detect_roman_urdu(text):
    """Detect Roman Urdu text"""
    roman_urdu_words = ['tum', 'mera', 'tera', 'kyun', 'kaise', 'nahi', 'acha', 'shukriya']
    text_lower = text.lower()
    return any(word in text_lower for word in roman_urdu_words)

# -----------------------------
# Session Management
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

def load_session():
    """Load session from file"""
    session_data = load_json(SESSION_FILE)
    if session_data and "user" in session_data:
        st.session_state.user = session_data["user"]

def save_session():
    """Save session to file"""
    if st.session_state.user:
        session_data = {"user": st.session_state.user}
        save_json(SESSION_FILE, session_data)

load_session()

# Load user data
users = load_json(USER_FILE)
history_data = load_json(HISTORY_FILE)

# -----------------------------
# Authentication System
# -----------------------------
if not st.session_state.user:
    st.header("🔐 Login / Sign Up")
    
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])
    
    with tab1:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", key="login_btn"):
            if login_user in users and users[login_user] == login_pass:
                st.session_state.user = login_user
                save_session()
                st.success(f"Welcome back, {login_user}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        signup_user = st.text_input("Username", key="signup_user")
        signup_pass = st.text_input("Password", type="password", key="signup_pass")
        
        if st.button("Create Account", key="signup_btn"):
            if not signup_user or not signup_pass:
                st.warning("Please enter username and password")
            elif signup_user in users:
                st.warning("Username already exists")
            else:
                users[signup_user] = signup_pass
                if save_json(USER_FILE, users):
                    st.session_state.user = signup_user
                    save_session()
                    st.success("Account created successfully!")
                    st.rerun()
    
    st.stop()

# -----------------------------
# Main Translator Interface
# -----------------------------
st.success(f"👋 Welcome, {st.session_state.user}!")

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 Source")
    source_lang = st.selectbox("From Language", list(LANGUAGES.keys()), index=0)
    input_text = st.text_area("Enter text to translate", placeholder="Type your text here...", height=150)

with col2:
    st.subheader("🎯 Target")
    target_lang = st.selectbox("To Language", list(LANGUAGES.keys()), 
                              index=list(LANGUAGES.keys()).index('Urdu') if 'Urdu' in LANGUAGES else 1)
    
    # Translation button
    translate_btn = st.button("🚀 Translate", type="primary", use_container_width=True)

st.markdown("---")

# -----------------------------
# Translation Logic
# -----------------------------
if translate_btn and input_text.strip():
    try:
        with st.spinner("Translating..."):
            # Determine source language
            if detect_roman_urdu(input_text):
                source_code = 'ur'
                actual_source = "Roman Urdu"
            else:
                source_code = LANGUAGES[source_lang]
                actual_source = source_lang
            
            # Perform translation
            translated_text = GoogleTranslator(
                source=source_code, 
                target=LANGUAGES[target_lang]
            ).translate(input_text)
            
            # Display results
            st.subheader("📝 Translation Result")
            st.text_area("Translated Text", translated_text, height=150, key="result")
            
            # Audio output
            st.subheader("🔊 Audio")
            try:
                tts = gTTS(translated_text, lang=LANGUAGES[target_lang])
                audio_file = "translation_audio.mp3"
                tts.save(audio_file)
                st.audio(audio_file, format="audio/mp3")
                # Clean up
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except Exception as e:
                st.warning(f"Text-to-speech not available: {e}")
            
            # Save to history
            if st.session_state.user not in history_data:
                history_data[st.session_state.user] = []
            
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "source_lang": actual_source,
                "target_lang": target_lang,
                "original": input_text,
                "translated": translated_text
            }
            
            history_data[st.session_state.user].append(history_entry)
            save_json(HISTORY_FILE, history_data)
            
            st.success("Translation completed!")
            
    except Exception as e:
        st.error(f"Translation failed: {str(e)}")
        st.info("Please check your internet connection and try again.")

elif translate_btn:
    st.warning("Please enter some text to translate.")

# -----------------------------
# Translation History
# -----------------------------
st.markdown("---")
st.subheader("📜 History")

if st.session_state.user in history_data and history_data[st.session_state.user]:
    user_history = history_data[st.session_state.user]
    
    # Show last 5 translations
    for i, entry in enumerate(reversed(user_history[-5:])):
        with st.expander(f"Translation {len(user_history)-i} - {entry['source_lang']} → {entry['target_lang']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Original:**")
                st.write(entry['original'])
            with col2:
                st.write("**Translated:**")
                st.write(entry['translated'])
else:
    st.info("No translation history yet.")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    st.caption("Built with Streamlit • Google Translator • gTTS")

with col2:
    if st.button("🚪 Logout"):
        st.session_state.user = None
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        st.rerun()
