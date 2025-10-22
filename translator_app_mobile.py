import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from datetime import datetime
import tempfile
import os
import io

# ---------- Page config ----------
st.set_page_config(page_title="AI Translator + Voice", layout="wide", page_icon="🌍")
st.title("🌍 AI Translator + Voice")

# ---------- Load supported languages ----------
# deep-translator returns a dict mapping code -> language name
langs_dict = GoogleTranslator(source="auto", target="en").get_supported_languages(as_dict=True)
# Build lists for dropdown: show "Language (code)" for clarity
lang_items = [f"{name} ({code})" for code, name in langs_dict.items()]
# Keep mapping from displayed string to code and readable name
display_to_code = {f"{name} ({code})": code for code, name in langs_dict.items()}
display_to_name = {f"{name} ({code})": name for code, name in langs_dict.items()}

# ---------- Sidebar: History ----------
st.sidebar.header("📜 Translation History")
history_file = "Translator_History.txt"
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        history_text = f.read()
else:
    history_text = "No history yet."

st.sidebar.text_area("Saved history", value=history_text, height=300, key="history_area")

def append_history(src_text, src_lang, target_lang, result):
    line = (
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n"
        f"Source ({src_lang}): {src_text}\n"
        f"Translated ({target_lang}): {result}\n"
        + "-"*40 + "\n"
    )
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(line)

# Download history button
if os.path.exists(history_file):
    with open(history_file, "rb") as f:
        st.sidebar.download_button("⬇️ Download history", data=f, file_name="Translator_History.txt")

# ---------- Main UI ----------
st.markdown("**Type text below, pick a target language, then press Translate.**")
col1, col2 = st.columns([3,1])

with col1:
    text = st.text_area("📝 Enter text to translate", height=140, placeholder="Type or paste text here...")
with col2:
    st.markdown("🎯 **Target language**")
    target_display = st.selectbox("Choose language", options=sorted(lang_items), index=sorted(lang_items).index("English (en)") if "English (en)" in lang_items else 0)
    tts_checkbox = st.checkbox("🔊 Play audio after translation", value=True)
    translate_btn = st.button("Translate")
    reverse_btn = st.button("🔁 Reverse translate (to English)")

# Utility: clean code -> name
def display_to_langcode(display):
    return display_to_code.get(display)

def display_to_langname(display):
    return display_to_name.get(display)

# ---------- Translation & TTS ----------
translated_text = None
if translate_btn:
    if not text or not text.strip():
        st.warning("⚠️ Please enter text to translate.")
    else:
        try:
            target_code = display_to_langcode(target_display)
            target_name = display_to_langname(target_display)
            # Use deep-translator (auto source)
            translated_text = GoogleTranslator(source="auto", target=target_code).translate(text)
            st.success(f"➡️ **Translation ({target_name}):**")
            st.write(translated_text)
            append_history(text, "Auto-detected", target_name, translated_text)
            # Copy button
            st.code(translated_text)
            st.button("Copy translation")  # visual cue (Streamlit has no JS clipboard without components)
            # Audio (gTTS) - catch unsupported languages
            if tts_checkbox:
                try:
                    # gTTS expects language codes like 'en', 'ur', 'ps', etc.
                    tts = gTTS(text=translated_text, lang=target_code)
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tts.save(tmp.name)
                    st.audio(tmp.name, format="audio/mp3")
                    # remove temp file after usage when app re-runs; leave for server cleanup
                except Exception as e:
                    st.warning(f"⚠️ Audio not available for this language (gTTS error): {e}")
        except Exception as e:
            st.error(f"❌ Translation error: {e}")

if reverse_btn:
    if not text or not text.strip():
        st.warning("⚠️ Please enter text to translate first (reverse translates from a translated result).")
    else:
        try:
            target_code = display_to_langcode(target_display)
            # Translate to target then back to English
            translated_temp = GoogleTranslator(source="auto", target=target_code).translate(text)
            reverse_text = GoogleTranslator(source=target_code, target="en").translate(translated_temp)
            st.info("🔁 **Back to English:**")
            st.write(reverse_text)
            append_history(translated_temp, display_to_langname(target_display), "English", reverse_text)
            if tts_checkbox:
                try:
                    tts = gTTS(text=reverse_text, lang="en")
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tts.save(tmp.name)
                    st.audio(tmp.name, format="audio/mp3")
                except Exception as e:
                    st.warning(f"⚠️ Audio not available for English (gTTS error): {e}")
        except Exception as e:
            st.error(f"❌ Reverse translation error: {e}")

# ---------- Helpful tips and footer ----------
st.markdown("---")
st.markdown(
    "**Tips:**\n"
    "- If audio fails for a particular language, uncheck the 'Play audio' box or choose another language.\n"
    "- The app uses Deep Translator (Google) — internet is required for translation and TTS.\n"
)
st.caption("Built with ❤️ — Streamlit + deep-translator + gTTS")

# cleanup: optional (do not delete history)
