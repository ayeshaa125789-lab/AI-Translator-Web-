# app.py
"""
Streamlit AI Translator — Pro (200+ langs, TTS, STT, history, login/signup)

Required (recommended) packages:
pip install streamlit deep-translator gTTS pyttsx3 langdetect speechrecognition pydub
Optional (better STT): pip install openai-whisper  (or 'whisper' package)
Optional (browser recorder widget): pip install streamlit-audiorecorder

Notes:
- gTTS uses Google's TTS voices for supported languages.
- Whisper (local) gives best STT; if missing, the app falls back to SpeechRecognition's Google recognizer.
- On some servers, pyttsx3 may not produce audio — gTTS is preferred.
"""

import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyttsx3
import json, os, io, base64, tempfile
from datetime import datetime

# Optional imports (wrapped in try/except for graceful fallback)
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except Exception:
    SR_AVAILABLE = False

# Optional in-browser recorder widget (nice UX). If not installed, user can upload audio files.
try:
    from streamlit_audiorecorder import audiorecorder
    RECORDER_AVAILABLE = True
except Exception:
    RECORDER_AVAILABLE = False

# Optional pydub for audio conversions
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except Exception:
    PYDUB_AVAILABLE = False

# -----------------------------
# App config
# -----------------------------
st.set_page_config(page_title="🌍 AI Translator Pro", page_icon="🌐", layout="wide")
st.title("🌍 AI Translator — Pro (200+ languages, STT, TTS, History)")

# -----------------------------
# 200+ languages mapping
# (Same list as provided earlier; keys for UI, values for translator/tts)
# -----------------------------
LANGUAGES = {
    'Afrikaans': 'af', 'Amharic': 'am', 'Arabic': 'ar', 'Assamese': 'as',
    'Aymara': 'ay', 'Azerbaijani': 'az', 'Bambara': 'bm', 'Bangla': 'bn',
    'Basque': 'eu', 'Belarusian': 'be', 'Bhojpuri': 'bho', 'Bosnian': 'bs',
    'Bulgarian': 'bg', 'Catalan': 'ca', 'Cebuano': 'ceb', 'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW', 'Chichewa': 'ny', 'Corsican': 'co',
    'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dhivehi': 'dv',
    'Dogri': 'doi', 'Dutch': 'nl', 'English': 'en', 'Esperanto': 'eo',
    'Estonian': 'et', 'Ewe': 'ee', 'Filipino': 'tl', 'Finnish': 'fi',
    'French': 'fr', 'Frisian': 'fy', 'Galician': 'gl', 'Georgian': 'ka',
    'German': 'de', 'Greek': 'el', 'Guarani': 'gn', 'Gujarati': 'gu',
    'Haitian Creole': 'ht', 'Hausa': 'ha', 'Hawaiian': 'haw', 'Hebrew': 'he',
    'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu', 'Icelandic': 'is',
    'Igbo': 'ig', 'Ilocano': 'ilo', 'Indonesian': 'id', 'Irish': 'ga',
    'Italian': 'it', 'Japanese': 'ja', 'Javanese': 'jw', 'Kannada': 'kn',
    'Kazakh': 'kk', 'Khmer': 'km', 'Kinyarwanda': 'rw', 'Konkani': 'gom',
    'Korean': 'ko', 'Krio': 'kri', 'Kurdish (Kurmanji)': 'ku',
    'Kurdish (Sorani)': 'ckb', 'Kyrgyz': 'ky', 'Lao': 'lo', 'Latin': 'la',
    'Latvian': 'lv', 'Lingala': 'ln', 'Lithuanian': 'lt', 'Luganda': 'lg',
    'Luxembourgish': 'lb', 'Macedonian': 'mk', 'Maithili': 'mai',
    'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt',
    'Maori': 'mi', 'Marathi': 'mr', 'Meiteilon (Manipuri)': 'mni-Mtei',
    'Mizo': 'lus', 'Mongolian': 'mn', 'Myanmar (Burmese)': 'my',
    'Nepali': 'ne', 'Norwegian': 'no', 'Odia (Oriya)': 'or',
    'Oromo': 'om', 'Pashto': 'ps', 'Persian': 'fa', 'Polish': 'pl',
    'Portuguese': 'pt', 'Punjabi': 'pa', 'Quechua': 'qu', 'Romanian': 'ro',
    'Russian': 'ru', 'Samoan': 'sm', 'Sanskrit': 'sa', 'Scots Gaelic': 'gd',
    'Serbian': 'sr', 'Sesotho': 'st', 'Shona': 'sn',
    'Sindhi': 'sd', 'Sinhala': 'si', 'Slovak': 'sk', 'Slovenian': 'sl',
    'Somali': 'so', 'Spanish': 'es', 'Sundanese': 'su', 'Swahili': 'sw',
    'Swedish': 'sv', 'Tamil': 'ta', 'Tatar': 'tt', 'Telugu': 'te',
    'Thai': 'th', 'Tigrinya': 'ti', 'Turkish': 'tr',
    'Turkmen': 'tk', 'Twi': 'ak', 'Ukrainian': 'uk', 'Urdu': 'ur',
    'Uyghur': 'ug', 'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy',
    'Wolof': 'wo', 'Xhosa': 'xh', 'Yiddish': 'yi', 'Yoruba': 'yo',
    'Zulu': 'zu'
}
LANG_NAMES = ["Auto-detect"] + list(LANGUAGES.keys())

# -----------------------------
# Storage files (simple JSON)
# -----------------------------
USER_FILE = "users.json"
HISTORY_FILE = "history.json"

def load_json(path):
    return json.load(open(path, "r", encoding="utf-8")) if os.path.exists(path) else {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_json(USER_FILE)
history = load_json(HISTORY_FILE)

# -----------------------------
# Session initialization (no shared session file)
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "model_whisper" not in st.session_state:
    st.session_state.model_whisper = None

# -----------------------------
# Helper: detect language (langdetect fallback)
# -----------------------------
def detect_language_of_text(text):
    # try deep_translator detect? it doesn't provide detect; use langdetect if installed
    try:
        from langdetect import detect
        code = detect(text)
        return code
    except Exception:
        # fallback simple heuristics: common words mapping (Urdu roman etc.)
        low = text.lower()
        if any(w in low for w in ["ki", "ka", "hai", "tum", "mera", "shukriya", "acha"]):
            return "ur"
        if any(w in low for w in ["the", "and", "is", "you", "thanks"]):
            return "en"
        return "en"

# -----------------------------
# Helper: STT (audio bytes -> text)
# Prefer whisper if available (local), else SpeechRecognition google
# -----------------------------
def audio_bytes_to_text(audio_bytes, filename_hint="audio.wav"):
    # save bytes to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename_hint)[1] if '.' in filename_hint else ".wav")
    try:
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()
        path = tmp.name

        # If pydub available and file is mp3, convert to wav for SR
        if PYDUB_AVAILABLE:
            ext = path.split('.')[-1].lower()
            if ext in ("mp3","m4a","aac","ogg"):
                wav_path = path + ".wav"
                AudioSegment.from_file(path).export(wav_path, format="wav")
                path = wav_path

        # Whisper path (best-quality offline)
        if WHISPER_AVAILABLE:
            try:
                if st.session_state.model_whisper is None:
                    st.session_state.model_whisper = whisper.load_model("small")  # change size as preferred
                model = st.session_state.model_whisper
                res = model.transcribe(path)
                return res.get("text", "")
            except Exception as e:
                st.warning("Whisper error, falling back to Google STT.")
                # continue to SR fallback

        # SpeechRecognition fallback (uses Google Web Speech API)
        if SR_AVAILABLE:
            r = sr.Recognizer()
            with sr.AudioFile(path) as source:
                audio = r.record(source)
            try:
                text = r.recognize_google(audio)
                return text
            except Exception as e:
                st.warning(f"Google STT failed: {e}")
                return ""
        else:
            st.warning("No speech-to-text engine available (install openai-whisper or speechrecognition).")
            return ""
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

# -----------------------------
# Helper: TTS (text -> audio bytes)
# gTTS preferred, pyttsx3 fallback
# -----------------------------
def text_to_speech_bytes(text, lang_code):
    # Try gTTS
    try:
        tts = gTTS(text, lang=lang_code)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read(), "mp3"
    except Exception as e:
        # fallback to pyttsx3 (may produce WAV)
        try:
            engine = pyttsx3.init()
            tmpf = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp_path = tmpf.name
            tmpf.close()
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            with open(tmp_path, "rb") as f:
                data = f.read()
            try:
                os.unlink(tmp_path)
            except:
                pass
            return data, "mp3"
        except Exception as e2:
            st.error("TTS not available on server. Install gTTS or configure pyttsx3.")
            return None, None

# -----------------------------
# Login / Signup UI
# -----------------------------
if not st.session_state.user:
    st.header("🔐 Login or Signup")
    col1, col2 = st.columns(2)
    with col1:
        login_user = st.text_input("Username (login)")
        login_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user in users and users[login_user] == login_pass:
                st.session_state.user = login_user
                st.success(f"Welcome back, {login_user}!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")
    with col2:
        new_user = st.text_input("New username")
        new_pass = st.text_input("New password", type="password")
        if st.button("Create account"):
            if not new_user.strip() or not new_pass.strip():
                st.warning("Enter valid username and password.")
            elif new_user in users:
                st.warning("Username exists — choose another.")
            else:
                users[new_user] = new_pass
                save_json(USER_FILE, users)
                st.session_state.user = new_user
                st.success("Account created and logged in!")
                st.experimental_rerun()
    st.stop()

# -----------------------------
# Main Dashboard for logged-in user
# -----------------------------
st.sidebar.success(f"Logged in as: {st.session_state.user}")
st.sidebar.markdown("## Dashboard")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.experimental_rerun()

# Primary translator UI
st.subheader("Translator")

col_left, col_right = st.columns([2,2])

with col_left:
    source_sel = st.selectbox("From language", LANG_NAMES, index=0)  # Auto-detect default
    input_mode = st.radio("Input mode:", ["Text", "Voice (record/upload)"], index=0)
    if input_mode == "Text":
        input_text = st.text_area("Enter text to translate", height=180)
        recorded_bytes = None
    else:
        # Voice mode
        st.markdown("### Voice input")
        recorded_bytes = None
        if RECORDER_AVAILABLE:
            st.info("Use your browser microphone to record (small recordings recommended).")
            audio_bytes = audiorecorder("Start/Stop", "Recording...")
            if audio_bytes:
                # audiorecorder returns WAV bytes in this package
                st.audio(audio_bytes)
                recorded_bytes = audio_bytes
        else:
            st.info("Recorder not installed. You can upload an audio file (wav/mp3/m4a).")
            uploaded = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a", "ogg", "flac"])
            if uploaded is not None:
                recorded_bytes = uploaded.read()
                st.audio(recorded_bytes)
        input_text = ""  # will be filled after STT if voice used

    target_sel = st.selectbox("To language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index("Urdu") if "Urdu" in LANGUAGES else 0)
    autodetect = (source_sel == "Auto-detect")
    translate_btn = st.button("🚀 Translate")

with col_right:
    st.markdown("### Output")
    output_text_area = st.empty()
    play_audio_button = st.empty()
    download_button_placeholder = st.empty()
    st.markdown("---")
    st.checkbox("Show history", key="show_history_checkbox")

# Translation flow
if translate_btn:
    # 1) If voice mode and recorded_bytes present -> convert to text via STT
    if input_mode == "Voice (record/upload)":
        if not recorded_bytes:
            st.warning("No audio recorded or uploaded.")
        else:
            with st.spinner("Converting speech to text..."):
                detected_text = audio_bytes_to_text(recorded_bytes, filename_hint="upload.wav")
                if not detected_text:
                    st.error("Speech recognition failed / returned empty text.")
                else:
                    input_text = detected_text
                    st.success("Transcription complete.")
                    st.write("**Transcribed text:**")
                    st.write(input_text)

    if not input_text or input_text.strip() == "":
        st.warning("No text to translate.")
    else:
        # 2) Detect source language if requested
        if autodetect:
            src_code = detect_language_of_text(input_text)
        else:
            src_code = LANGUAGES.get(source_sel)

        tgt_code = LANGUAGES.get(target_sel)
        if not src_code or not tgt_code:
            st.error("Language codes not found — please recheck selections.")
        else:
            try:
                with st.spinner("Translating..."):
                    translated = GoogleTranslator(source=src_code, target=tgt_code).translate(input_text)
                output_text_area.text_area("Translated text", translated, height=220)

                # 3) TTS for translated text
                with st.spinner("Generating voice..."):
                    audio_bytes, ext = text_to_speech_bytes(translated, tgt_code)
                if audio_bytes:
                    # Show player and download
                    st.audio(audio_bytes, format=f"audio/{ext}")
                    download_button_placeholder.download_button(
                        label="⬇️ Download audio",
                        data=audio_bytes,
                        file_name=f"translation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}",
                        mime=f"audio/{ext}"
                    )
                else:
                    st.warning("Audio generation failed for this language.")

                # 4) Save history (per-user)
                user = st.session_state.user
                if user not in history:
                    history[user] = []
                history[user].append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "from": source_sel if source_sel != "Auto-detect" else src_code,
                    "to": target_sel,
                    "input": input_text,
                    "output": translated
                })
                save_json(HISTORY_FILE, history)
                st.success("Saved to your history.")
            except Exception as e:
                st.error(f"Translation / TTS error: {e}")

# Show history if requested
if st.session_state.get("show_history_checkbox"):
    st.markdown("## Your Translation History")
    user_history = history.get(st.session_state.user, [])
    if not user_history:
        st.info("No history yet.")
    else:
        # show last 50 translations in reverse order
        for h in reversed(user_history[-50:]):
            st.markdown(f"**🕒 {h['time']}** — **{h.get('from','?')} → {h.get('to','?')}**")
            st.write("Input:")
            st.write(h.get("input", ""))
            st.write("Output:")
            st.write(h.get("output", ""))
            st.markdown("---")

# Footer / tips
st.markdown("---")
st.caption("Built with ❤️ — gTTS / pyttsx3 / Whisper (optional) / deep-translator. "
           "If voice or STT isn't working, install 'openai-whisper' or 'speechrecognition' and 'pydub' on the server.")
