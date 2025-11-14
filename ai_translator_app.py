# app.py
"""
Upgraded AI Translator — Multi-user, Login/Signup, Admin, History, Auto-detect, Download audio.

Run: streamlit run app.py

Requirements (recommended):
- streamlit
- deep-translator
- gTTS
- pyttsx3 (optional fallback)
- fuzzywuzzy
- python-Levenshtein
- speechrecognition
- pydub
- langdetect
- (optional) openai-whisper for local STT
"""

import streamlit as st
import json, os, tempfile, io
from datetime import datetime
from deep_translator import GoogleTranslator
from gtts import gTTS

# Optional imports with graceful fallback
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except Exception:
    SR_AVAILABLE = False

try:
    from langdetect import detect as lang_detect
    LANGDETECT_AVAILABLE = True
except Exception:
    LANGDETECT_AVAILABLE = False

try:
    from fuzzywuzzy import process as fuzzy_process
    FUZZY_AVAILABLE = True
except Exception:
    FUZZY_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False

# -------------------------
# Files & Admin credentials
# -------------------------
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# Ensure files exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": {ADMIN_USER: {"password": ADMIN_PASS, "is_admin": True}}}, f, indent=2, ensure_ascii=False)

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2, ensure_ascii=False)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -------------------------
# Streamlit page config
# -------------------------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌍", layout="wide")
# small CSS for nicer look & auto-theme switch
st.markdown("""
<style>
body {font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;}
.container {max-width: 1100px; margin: auto;}
.panel {background: var(--color-bg-2); padding: 18px; border-radius: 12px; box-shadow: rgba(2,12,27,0.05) 0px 6px 24px;}
.header {text-align:center; margin-bottom:10px;}
.small-muted {color: var(--color-muted); font-size:14px;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Session state
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "theme_dark" not in st.session_state:
    st.session_state.theme_dark = False

# -------------------------
# Languages list (200+ via deep-translator supported names)
# We'll get supported languages from deep-translator and also build a display list.
# -------------------------
try:
    DL = GoogleTranslator()
    supported = DL.get_supported_languages(as_dict=False)
except Exception:
    # fallback small list if deep-translator call fails
    supported = ["english","urdu","hindi","arabic","french","spanish","german","chinese (simplified)"]

LANG_DISPLAY = supported[:]  # UI names

# Helper: fuzzy search language by approximate name
def find_lang_name(query):
    if not query or query.strip()=="":
        return None
    q = query.lower()
    if q in [x.lower() for x in LANG_DISPLAY]:
        # exact match ignoring case
        for x in LANG_DISPLAY:
            if x.lower() == q:
                return x
    if FUZZY_AVAILABLE:
        choice, score = fuzzy_process.extractOne(q, LANG_DISPLAY)
        if score >= 60:
            return choice
    # fallback: try simple substring match
    for x in LANG_DISPLAY:
        if q in x.lower():
            return x
    return None

# -------------------------
# Small helpers: TTS, STT
# -------------------------
def text_to_mp3_bytes(text, lang_code="en"):
    try:
        buf = io.BytesIO()
        tts = gTTS(text=text, lang=lang_code)
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        st.warning("gTTS failed to generate audio.")
        return None

def audiofile_bytes_to_text(file_bytes, filename_hint="audio.wav"):
    # Attempt Whisper if available, else use SpeechRecognition with Google
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename_hint)[1] if '.' in filename_hint else ".wav")
    try:
        tmp.write(file_bytes)
        tmp.close()
        path = tmp.name

        if WHISPER_AVAILABLE:
            try:
                model = whisper.load_model("base")
                res = model.transcribe(path)
                return res.get("text","")
            except Exception:
                pass

        if SR_AVAILABLE:
            r = sr.Recognizer()
            try:
                with sr.AudioFile(path) as source:
                    audio = r.record(source)
                text = r.recognize_google(audio)
                return text
            except Exception:
                return ""
        return ""
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

# -------------------------
# Authentication UI (Login/Signup)
# -------------------------
def auth_ui():
    st.title("🌍 AI Translator Pro")
    st.write("Login or Signup to continue — each user has their own history and dashboard.")
    st.markdown("---")
    col1, col2 = st.columns(2)

    users_db = load_json(USERS_FILE)["users"]

    with col1:
        st.subheader("🔐 Login")
        lu = st.text_input("Username", key="login_user")
        lp = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if lu in users_db and users_db[lu]["password"] == lp:
                st.session_state.user = lu
                st.session_state.is_admin = users_db.get(lu, {}).get("is_admin", False)
                st.success(f"Welcome back, {lu}!")
                st.experimental_rerun_called = True
                st.rerun()
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
                st.warning("Username already exists. Choose different.")
            else:
                users_db[su] = {"password": sp, "is_admin": False}
                save_json(USERS_FILE, {"users": users_db})
                st.success("Account created. You can now login.")
    st.markdown("---")
    st.caption("Tip: admin account pre-created. (admin / admin123)")

# -------------------------
# Admin panel UI
# -------------------------
def admin_ui():
    st.header("⚙️ Admin Panel")
    st.info("Manage users and view global history.")
    data = load_json(USERS_FILE)
    users_db = data["users"]

    st.subheader("👥 Users")
    for u, info in users_db.items():
        cols = st.columns([3,1,1])
        cols[0].write(f"**{u}**")
        if info.get("is_admin"):
            cols[1].write("Admin")
        else:
            if cols[1].button("Make Admin", key=f"makeadmin_{u}"):
                users_db[u]["is_admin"] = True
                save_json(USERS_FILE, {"users": users_db})
                st.experimental_rerun()
        if cols[2].button("Delete", key=f"del_{u}"):
            if u == ADMIN_USER:
                st.warning("Can't delete main admin.")
            else:
                users_db.pop(u)
                save_json(USERS_FILE, {"users": users_db})
                st.success(f"Deleted {u}")
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("📚 All Histories")
    histories = load_json(HISTORY_FILE)
    if not histories:
        st.info("No history yet.")
    else:
        for user, entries in histories.items():
            st.markdown(f"### {user} — {len(entries)} items")
            for e in reversed(entries[-20:]):
                st.write(f"**{e['time']}** — {e.get('from')} → {e.get('to')}")
                st.write("Input:"); st.write(e.get("input",""))
                st.write("Output:"); st.write(e.get("output",""))
                st.markdown("---")

    if st.button("Reset All Histories"):
        save_json(HISTORY_FILE, {})
        st.success("All histories cleared.")
        st.experimental_rerun()

# -------------------------
# Translator UI
# -------------------------
def translator_ui():
    st.header("🌎 Translator")
    st.markdown("Translate text between 200+ languages. Use auto-detect or choose language. Upload audio to transcribe.")
    col_a, col_b = st.columns([2,1])

    with col_b:
        # theme toggle
        theme_toggle = st.checkbox("Dark mode", value=st.session_state.theme_dark)
        st.session_state.theme_dark = theme_toggle

    with col_a:
        # Auto-detect checkbox
        autodetect = st.checkbox("Auto detect source language (use text or audio)", value=True)
        # source/target with fuzzy search box
        source_search = st.text_input("From (type to fuzzy-search) — leave blank for Auto", value="")
        target_search = st.text_input("To (type to fuzzy-search)", value="english")
        # find language names
        src_name = None
        if not autodetect:
            src_name = find_lang_name(source_search) if source_search.strip()!="" else None
        tgt_name = find_lang_name(target_search) if target_search.strip()!="" else find_lang_name("english")
        # show fallback values
        if not autodetect:
            st.write("From: ", src_name if src_name else "Not found (pick exact from list below)")
        st.write("To: ", tgt_name if tgt_name else "english")
        # show raw selection list (compact)
        show_picker = st.checkbox("Choose from full language list")
        if show_picker:
            src_name = st.selectbox("From language (picker) — choose 'auto' to detect", ["Auto"]+LANG_DISPLAY, index=0)
            if src_name == "Auto":
                autodetect = True
            tgt_name = st.selectbox("To language (picker)", LANG_DISPLAY, index=LANG_DISPLAY.index("english") if "english" in LANG_DISPLAY else 0)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        input_text = st.text_area("Enter text to translate", height=180)
        upload_audio = st.file_uploader("Or upload audio (.wav/.mp3/.m4a/.ogg)", type=["wav","mp3","m4a","ogg"])
        detected_text = ""
        if upload_audio is not None:
            audio_bytes = upload_audio.read()
            st.audio(audio_bytes)
            with st.spinner("Transcribing audio..."):
                trans = audiofile_bytes_to_text(audio_bytes, filename_hint=upload_audio.name)
                if trans:
                    detected_text = trans
                    st.success("Transcription ready.")
                    st.write(trans)
                else:
                    st.warning("Transcription returned empty. Try a clearer audio or type manually.")
    with col2:
        # preview and actions
        final_input = input_text.strip() if input_text.strip() != "" else detected_text
        st.markdown("### Preview")
        st.write(final_input if final_input else "No input yet.")
        if st.button("Translate Now"):
            if not final_input:
                st.warning("Provide text or upload audio to translate.")
            else:
                # determine source code
                if autodetect:
                    if LANGDETECT_AVAILABLE:
                        try:
                            src_code = lang_detect(final_input)
                        except Exception:
                            src_code = "auto"
                    else:
                        src_code = "auto"
                else:
                    # map name to code via deep-translator get_supported_languages(as_dict=True) if needed
                    src_code = None
                    # deep-translator accepts language names like 'english' or codes; we'll pass name
                    if src_name:
                        src_code = src_name
                    else:
                        src_code = "auto"
                tgt_code = tgt_name if tgt_name else "english"

                # perform translation
                try:
                    with st.spinner("Translating..."):
                        translated = GoogleTranslator(source=src_code if src_code!="auto" else "auto", target=tgt_code).translate(final_input)
                    st.success("Translated.")
                    st.markdown("### Result")
                    st.info(translated)

                    # Save history
                    hist = load_json(HISTORY_FILE)
                    user_hist = hist.get(st.session_state.user, [])
                    user_hist.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "from": src_code,
                        "to": tgt_code,
                        "input": final_input,
                        "output": translated
                    })
                    hist[st.session_state.user] = user_hist
                    save_json(HISTORY_FILE, hist)

                    # TTS and download
                    # choose lang code for gTTS: deep-translator uses names, but gTTS expects language code.
                    # We'll attempt to map simple names to codes via a small mapping, else default en
                    mapping_guess = {
                        "english":"en","urdu":"ur","hindi":"hi","arabic":"ar","french":"fr",
                        "spanish":"es","german":"de","chinese (simplified)":"zh-cn","chinese (traditional)":"zh-tw",
                        "portuguese":"pt","russian":"ru"
                    }
                    gtts_lang = mapping_guess.get(tgt_code.lower(), "en")
                    audio_bytes = text_to_mp3_bytes(translated, gtts_lang)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        st.download_button("⬇️ Download audio (MP3)", data=audio_bytes,
                                           file_name=f"translation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                                           mime="audio/mp3")
                    else:
                        st.warning("Audio could not be generated for this language (gTTS may not support it).")

                except Exception as e:
                    st.error(f"Translation error: {e}")

# -------------------------
# History UI
# -------------------------
def history_ui():
    st.header("📜 My Translation History")
    hist = load_json(HISTORY_FILE)
    my = hist.get(st.session_state.user, [])
    if not my:
        st.info("No history yet.")
        return
    for entry in reversed(my[-200:]):
        st.markdown(f"**{entry['time']}** — **{entry.get('from')} → {entry.get('to')}**")
        st.write("Input:"); st.write(entry.get("input",""))
        st.write("Output:"); st.write(entry.get("output",""))
        st.markdown("---")
    if st.button("Clear my history"):
        hist.pop(st.session_state.user, None)
        save_json(HISTORY_FILE, hist)
        st.success("Your history was cleared.")
        st.rerun()

# -------------------------
# Profile UI
# -------------------------
def profile_ui():
    st.header("👤 My Profile")
    users_db = load_json(USERS_FILE)["users"]
    info = users_db.get(st.session_state.user, {})
    st.write("Username:", st.session_state.user)
    if st.button("Delete my account (this will remove my history too)"):
        if st.session_state.user == ADMIN_USER:
            st.warning("Admin account can't be deleted here.")
        else:
            users_db.pop(st.session_state.user, None)
            save_json(USERS_FILE, {"users": users_db})
            hist = load_json(HISTORY_FILE)
            hist.pop(st.session_state.user, None)
            save_json(HISTORY_FILE, hist)
            st.success("Account deleted. Logging out...")
            st.session_state.user = None
            st.rerun()

# -------------------------
# Main routing (for logged in users)
# -------------------------
if not st.session_state.user:
    auth_ui()
else:
    # Sidebar
    st.sidebar.markdown(f"### 👋 {st.session_state.user}")
    menu = st.sidebar.radio("Navigation", ["Translator", "History", "Profile", "Admin" if st.session_state.is_admin else None, "Logout"], index=0)
    # remove None from sidebar display if not admin
    if menu is None:
        menu = "Translator"

    if menu == "Logout":
        st.session_state.user = None
        st.session_state.is_admin = False
        st.rerun()
    elif menu == "Translator":
        translator_ui()
    elif menu == "History":
        history_ui()
    elif menu == "Profile":
        profile_ui()
    elif menu == "Admin":
        if st.session_state.is_admin:
            admin_ui()
        else:
            st.error("Admin access required.")
