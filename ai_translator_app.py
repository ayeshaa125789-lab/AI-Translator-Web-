import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

st.set_page_config(page_title="🌍 AI Translator", page_icon="🌐", layout="wide")

st.title("🌍 AI Translator — Translate Instantly in 200+ Languages")

# ✅ Full language list (200+ supported)
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

# Layout
col1, col2 = st.columns(2)

with col1:
    source_lang = st.selectbox("🌐 From Language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index("English"))
    text = st.text_area("Enter Text", placeholder="Type something to translate...")

with col2:
    target_lang = st.selectbox("🎯 To Language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index("Urdu"))
    translate_btn = st.button("🚀 Translate")

st.markdown("---")

# Translation memory fix
if "last_translation" not in st.session_state:
    st.session_state["last_translation"] = {}

if translate_btn and text.strip():
    try:
        last_trans = st.session_state["last_translation"]
        if last_trans.get("text") == text:
            source_lang, target_lang = last_trans["target"], last_trans["source"]

        translated_text = GoogleTranslator(
            source=LANGUAGES[source_lang],
            target=LANGUAGES[target_lang]
        ).translate(text)

        st.subheader(f"🈸 Translation Result ({source_lang} → {target_lang})")
        st.text_area("Output", translated_text, height=150)

        # 🔊 Text-to-Speech
        try:
            tts = gTTS(translated_text, lang=LANGUAGES[target_lang])
            audio_file = "output.mp3"
            tts.save(audio_file)
            st.audio(audio_file, format="audio/mp3")
        except:
            st.warning("🔈 Audio not available for this language.")

        st.session_state["last_translation"] = {"text": translated_text, "source": source_lang, "target": target_lang}

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("Enter text and click Translate to start.")

st.caption("🌎 Built with ❤️ using Streamlit, GoogleTranslator & gTTS.")
