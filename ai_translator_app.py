import streamlit as st
import json
import os
import tempfile
from datetime import datetime

# Offline Libraries
from argostranslate import get_installed_languages, install_language_pack
from gtts import gTTS

# --- Configuration ---
USERS_FILE = "users.json"
MAX_HISTORY = 10 

# -------------------------
# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "history" not in st.session_state:
    st.session_state["history"] = []

# -------------------------
# Data Persistence Functions (JSON)
def load_users():
    """Loads user data (including history) from JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users_data):
    """Saves user data back to JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

def load_user_data(email):
    """Loads history for the currently logged-in user."""
    users = load_users()
    if email in users and 'history' in users[email]:
        st.session_state["history"] = users[email]['history']
    else:
        st.session_state["history"] = []

def save_user_history():
    """Saves the current session history back to the user's data."""
    if st.session_state["current_user"]:
        users = load_users()
        if st.session_state["current_user"] in users:
            # Keep only the latest MAX_HISTORY entries
            users[st.session_state["current_user"]]['history'] = st.session_state["history"][:MAX_HISTORY]
            save_users(users)

# -------------------------
# Authentication UI
def signup():
    st.subheader("✍️ Signup")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Create Account"):
        users = load_users()
        if email in users:
            st.error("User already exists.")
        elif not email or not password:
            st.warning("Enter email and password.")
        else:
            users[email] = {'password': password, 'history': []}
            save_users(users)
            st.success("Account created! You can now log in.")

def login():
    st.subheader("🔑 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        users = load_users()
        if email in users and users[email]['password'] == password:
            st.session_state["logged_in"] = True
            st.session_state["current_user"] = email
            load_user_data(email) # Load user's history
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid email or password.")

def logout():
    save_user_history()
    st.session_state["logged_in"] = False
    st.session_state["current_user"] = None
    st.session_state["history"] = []
    st.rerun()

# -------------------------
# Language Loading (Offline Argos)
try:
    installed_languages = get_installed_languages()
    LANG_DICT = {lang.name: lang for lang in installed_languages}
    LANG_LIST = sorted(LANG_DICT.keys())
    if not LANG_LIST:
        st.warning("No Argos language models installed. Translation will not work. Please install language packs manually.")
except Exception as e:
    # This might happen if argostranslate is not fully set up
    LANG_LIST = ["Error Loading Languages"]
    st.error(f"Error loading Argos languages: {e}")

# Helper: Translate Text
def translate_text(text, src_name, dest_name):
    src = LANG_DICT.get(src_name)
    dest = LANG_DICT.get(dest_name)
    if not src or not dest:
        raise ValueError("Selected language model not found.")
        
    translation = src.get_translation(dest)
    return translation.translate(text)

# -------------------------
# --- Main Application Logic ---
# -------------------------

if not st.session_state["logged_in"]:
    st.title("🌐 Offline Translator Access")
    tab1, tab2 = st.tabs(["Login", "Signup"])
    with tab1: login()
    with tab2: signup()
    st.stop()

# --- Application Header and Sidebar ---
st.sidebar.title("👤 User Controls")
st.sidebar.write(f"Logged in as: **{st.session_state['current_user']}**")
if st.sidebar.button("🔓 Logout"):
    logout()

st.title("🗣️ Offline Text Translator")
st.write("Powered by Argos Translate & gTTS (Text-to-Speech).")

# -------------------------
# Language Selection
with st.sidebar:
    st.header("Language Settings")
    if LANG_LIST and LANG_LIST[0] != "Error Loading Languages":
        src_lang_name = st.selectbox("From Language:", LANG_LIST, key="src_lang")
        dest_lang_name = st.selectbox("To Language:", LANG_LIST, key="dest_lang")
    else:
        st.error("Cannot proceed without installed language models.")
        st.stop()

# -------------------------
# Translation Input/Output
input_text = st.text_area("📝 Enter Text Here (Unlimited):", height=200, placeholder="Start typing...")

if st.button("Translate Text"):
    if not input_text.strip():
        st.warning("Please enter text to translate.")
    elif src_lang_name == dest_lang_name:
        st.warning("Source and Target languages must be different.")
    else:
        with st.spinner(f"Translating from {src_lang_name} to {dest_lang_name}..."):
            try:
                translated_text = translate_text(input_text, src_lang_name, dest_lang_name)
                st.session_state["last_translation"] = translated_text
                
                # Add to history (newest first)
                history_entry = {
                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'input': input_text[:50] + "..." if len(input_text) > 50 else input_text,
                    'input_full': input_text,
                    'output': translated_text,
                    'type': 'Text',
                    'src': src_lang_name,
                    'dest': dest_lang_name
                }
                st.session_state["history"].insert(0, history_entry)
                save_user_history()
                st.success("Translation complete!")

            except Exception as e:
                st.error(f"Translation Error: {e}")

# -------------------------
# Display Output and TTS

translated_text = st.session_state.get("last_translation", "")

if translated_text:
    st.subheader("📖 Translation Output")
    st.text_area("Output:", translated_text, height=200, key="output_area")

    col_tts, col_download = st.columns([1, 1])
    
    with col_tts:
        if st.button("🔊 Generate & Play TTS"):
            with st.spinner("Generating Audio..."):
                try:
                    # gTTS requires the language code, so we infer it from the name
                    # This relies on gTTS supporting the same codes as Argos/common codes.
                    lang_code = next((code for name, code in LANGUAGES.items() if name == dest_lang_name), 'en')
                    
                    tts = gTTS(translated_text, lang=lang_code)
                    
                    # Save to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.write_to_fp(fp)
                        temp_file_name = fp.name
                    
                    st.audio(temp_file_name)
                    os.unlink(temp_file_name) # Clean up temp file
                except Exception as e:
                    st.error(f"TTS Error (Could not generate audio for {dest_lang_name}): {e}")

    with col_download:
        st.download_button(
            label="Download .TXT File",
            data=translated_text,
            file_name="translated_text.txt",
            mime="text/plain"
        )

# -------------------------
# History Tab
st.sidebar.markdown("---")
st.sidebar.subheader(f"History ({len(st.session_state['history'])})")

if st.session_state["history"]:
    for i, entry in enumerate(st.session_state["history"]):
        if i >= MAX_HISTORY: break
        with st.sidebar.expander(f"{entry['time']} ({entry['src']} -> {entry['dest']})"):
            st.caption(f"Input: {entry['input']}")
            st.caption(f"Output: {entry['output'][:50]}...")
            
            # Button to load this translation back to the main screen
            if st.button("Reload Output", key=f"hist_load_{i}"):
                st.session_state["last_translation"] = entry['output']
                st.session_state["input_text"] = entry['input_full']
                st.session_state["src_lang"] = entry['src']
                st.session_state["dest_lang"] = entry['dest']
                st.rerun()
else:
    st.sidebar.info("No translation history yet.")
