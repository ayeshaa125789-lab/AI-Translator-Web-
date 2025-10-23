import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# ---------- SEO META (for Streamlit Cloud SEO) ----------
st.set_page_config(
    page_title="Free AI Translator by Ashii 🌍",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="auto"
)

# ---------- MAIN TITLE ----------
st.title("🌐 Free AI Translator by Ashii")
st.markdown("#### Translate text instantly between 100+ languages — Fast, Offline-style & Simple UI 🚀")

# ---------- SIDEBAR ----------
st.sidebar.title("🌍 Choose Options")
source_lang = st.sidebar.selectbox("From Language:", ["auto", "english", "urdu", "hindi", "french", "arabic", "german", "chinese"])
target_lang = st.sidebar.selectbox("To Language:", ["english", "urdu", "hindi", "french", "arabic", "german", "chinese"])

# ---------- INPUT BOX ----------
text_to_translate = st.text_area("✏️ Enter text to translate:", placeholder="Type something here...")

# ---------- BUTTON ----------
if st.button("🔁 Translate Now"):
    if text_to_translate.strip() == "":
        st.warning("⚠️ Please enter some text first.")
    else:
        try:
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text_to_translate)
            st.success(f"✅ **Translated Text:** {translated}")

            # ---------- SPEECH OPTION ----------
            if st.checkbox("🔊 Play Translated Audio"):
                tts = gTTS(translated)
                tts.save("translated.mp3")
                st.audio("translated.mp3", format="audio/mp3")
                os.remove("translated.mp3")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("💡 Built with ❤️ by **Ashii** — AI Student Project (Free & Open Source)")
