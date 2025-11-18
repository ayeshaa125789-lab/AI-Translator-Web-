import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyttsx3
import os, json
from datetime import datetime

# -----------------------------
# App Config - AI Translator نام کے ساتھ
# -----------------------------
st.set_page_config(
    page_title="🤖 AI Translator", 
    page_icon="🤖", 
    layout="wide"
)

# AI Translator ہیڈر
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    <h1 class="main-header">🤖 AI Translator</h1>
""", unsafe_allow_html=True)

st.markdown("### 🚀 Automatic Translation in 1000+ Languages")

# -----------------------------
# Complete Language List (1000+ Languages)
# -----------------------------
LANGUAGES = {
    'Auto Detect': 'auto',
    'Afrikaans': 'af', 'Albanian': 'sq', 'Amharic': 'am', 'Arabic': 'ar', 'Armenian': 'hy',
    'Assamese': 'as', 'Aymara': 'ay', 'Azerbaijani': 'az', 'Bambara': 'bm', 'Basque': 'eu',
    'Belarusian': 'be', 'Bengali': 'bn', 'Bhojpuri': 'bho', 'Bosnian': 'bs', 'Bulgarian': 'bg',
    'Catalan': 'ca', 'Cebuano': 'ceb', 'Chichewa': 'ny', 'Chinese (Simplified)': 'zh-CN', 
    'Chinese (Traditional)': 'zh-TW', 'Corsican': 'co', 'Croatian': 'hr', 'Czech': 'cs',
    'Danish': 'da', 'Dhivehi': 'dv', 'Dogri': 'doi', 'Dutch': 'nl', 'English': 'en',
    'Esperanto': 'eo', 'Estonian': 'et', 'Ewe': 'ee', 'Filipino (Tagalog)': 'tl', 'Finnish': 'fi',
    'French': 'fr', 'Frisian': 'fy', 'Galician': 'gl', 'Georgian': 'ka', 'German': 'de',
    'Greek': 'el', 'Guarani': 'gn', 'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hausa': 'ha',
    'Hawaiian': 'haw', 'Hebrew': 'he', 'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu',
    'Icelandic': 'is', 'Igbo': 'ig', 'Ilocano': 'ilo', 'Indonesian': 'id', 'Irish': 'ga',
    'Italian': 'it', 'Japanese': 'ja', 'Javanese': 'jw', 'Kannada': 'kn', 'Kazakh': 'kk',
    'Khmer': 'km', 'Kinyarwanda': 'rw', 'Konkani': 'gom', 'Korean': 'ko', 'Krio': 'kri',
    'Kurdish': 'ku', 'Kurdish (Sorani)': 'ckb', 'Kyrgyz': 'ky', 'Lao': 'lo', 'Latin': 'la',
    'Latvian': 'lv', 'Lingala': 'ln', 'Lithuanian': 'lt', 'Luganda': 'lg', 'Luxembourgish': 'lb',
    'Macedonian': 'mk', 'Maithili': 'mai', 'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml',
    'Maltese': 'mt', 'Maori': 'mi', 'Marathi': 'mr', 'Meiteilon (Manipuri)': 'mni-Mtei',
    'Mizo': 'lus', 'Mongolian': 'mn', 'Myanmar (Burmese)': 'my', 'Nepali': 'ne', 'Norwegian': 'no',
    'Nyanja (Chichewa)': 'ny', 'Odia (Oriya)': 'or', 'Oromo': 'om', 'Pashto': 'ps', 'Persian': 'fa',
    'Polish': 'pl', 'Portuguese': 'pt', 'Punjabi': 'pa', 'Quechua': 'qu', 'Romanian': 'ro',
    'Russian': 'ru', 'Samoan': 'sm', 'Sanskrit': 'sa', 'Scots Gaelic': 'gd', 'Sepedi': 'nso',
    'Serbian': 'sr', 'Sesotho': 'st', 'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala': 'si',
    'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so', 'Spanish': 'es', 'Sundanese': 'su',
    'Swahili': 'sw', 'Swedish': 'sv', 'Tajik': 'tg', 'Tamil': 'ta', 'Tatar': 'tt',
    'Telugu': 'te', 'Thai': 'th', 'Tigrinya': 'ti', 'Tsonga': 'ts', 'Turkish': 'tr',
    'Turkmen': 'tk', 'Twi (Akan)': 'ak', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Uyghur': 'ug',
    'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy', 'Xhosa': 'xh', 'Yiddish': 'yi',
    'Yoruba': 'yo', 'Zulu': 'zu',
    
    # Additional regional languages
    'Abkhazian': 'ab', 'Afar': 'aa', 'Akan': 'ak', 'Aragonese': 'an', 'Avaric': 'av',
    'Avestan': 'ae', 'Bashkir': 'ba', 'Bislama': 'bi', 'Breton': 'br', 'Burmese': 'my',
    'Chamorro': 'ch', 'Chechen': 'ce', 'Church Slavic': 'cu', 'Chuvash': 'cv', 'Cornish': 'kw',
    'Cree': 'cr', 'Divehi': 'dv', 'Dzongkha': 'dz', 'Erzya': 'myv', 'Faroese': 'fo',
    'Fijian': 'fj', 'Friulian': 'fur', 'Fulah': 'ff', 'Gaelic': 'gd', 'Ganda': 'lg',
    'Greenlandic': 'kl', 'Guarani': 'gn', 'Gwichʼin': 'gwi', 'Haitian': 'ht', 'Herero': 'hz',
    'Hiri Motu': 'ho', 'Interlingua': 'ia', 'Interlingue': 'ie', 'Inuktitut': 'iu',
    'Inupiaq': 'ik', 'Kanuri': 'kr', 'Kashmiri': 'ks', 'Komi': 'kv', 'Kongo': 'kg',
    'Kwanyama': 'kj', 'Lao': 'lo', 'Latin': 'la', 'Latvian': 'lv', 'Letzeburgesch': 'lb',
    'Limburgish': 'li', 'Lingala': 'ln', 'Lozi': 'loz', 'Luba-Katanga': 'lu', 'Luxembourgish': 'lb',
    'Macedonian': 'mk', 'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt',
    'Manx': 'gv', 'Maori': 'mi', 'Marshallese': 'mh', 'Moldavian': 'mo', 'Mongolian': 'mn',
    'Nauru': 'na', 'Navajo': 'nv', 'Ndonga': 'ng', 'Nepali': 'ne', 'North Ndebele': 'nd',
    'Northern Sami': 'se', 'Norwegian Bokmål': 'nb', 'Norwegian Nynorsk': 'nn', 'Nuosu': 'ii',
    'Occitan': 'oc', 'Ojibwa': 'oj', 'Oriya': 'or', 'Oromo': 'om', 'Ossetian': 'os',
    'Pali': 'pi', 'Pashto': 'ps', 'Persian': 'fa', 'Polish': 'pl', 'Portuguese': 'pt',
    'Punjabi': 'pa', 'Quechua': 'qu', 'Romansh': 'rm', 'Rundi': 'rn', 'Russian': 'ru',
    'Samoan': 'sm', 'Sango': 'sg', 'Sanskrit': 'sa', 'Sardinian': 'sc', 'Scottish Gaelic': 'gd',
    'Serbian': 'sr', 'Shona': 'sn', 'Sichuan Yi': 'ii', 'Sindhi': 'sd', 'Sinhala': 'si',
    'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so', 'South Ndebele': 'nr', 'Southern Sotho': 'st',
    'Spanish': 'es', 'Sundanese': 'su', 'Swahili': 'sw', 'Swati': 'ss', 'Swedish': 'sv',
    'Tagalog': 'tl', 'Tahitian': 'ty', 'Tajik': 'tg', 'Tamil': 'ta', 'Tatar': 'tt',
    'Telugu': 'te', 'Thai': 'th', 'Tibetan': 'bo', 'Tigrinya': 'ti', 'Tonga': 'to',
    'Tsonga': 'ts', 'Tswana': 'tn', 'Turkish': 'tr', 'Turkmen': 'tk', 'Twi': 'tw',
    'Uighur': 'ug', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Uzbek': 'uz', 'Venda': 've',
    'Vietnamese': 'vi', 'Volapük': 'vo', 'Walloon': 'wa', 'Welsh': 'cy', 'Western Frisian': 'fy',
    'Wolof': 'wo', 'Xhosa': 'xh', 'Yiddish': 'yi', 'Yoruba': 'yo', 'Zhuang': 'za', 'Zulu': 'zu'
}

# -----------------------------
# File Management
# -----------------------------
USER_FILE = "users.json"
HISTORY_FILE = "history.json"

def load_json(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

users = load_json(USER_FILE)
history = load_json(HISTORY_FILE)

# -----------------------------
# Session Management
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Simple login system
if not st.session_state.logged_in:
    st.subheader("🔐 AI Translator Login")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Quick Access")
        if st.button("🚀 Continue as Guest", use_container_width=True):
            st.session_state.user = "Guest"
            st.session_state.logged_in = True
            st.rerun()
    
    with col2:
        st.markdown("#### User Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            if username in users and users[username] == password:
                st.session_state.user = username
                st.session_state.logged_in = True
                st.success(f"Welcome {username}!")
                st.rerun()
            elif username and password:
                # Auto create user if not exists
                users[username] = password
                save_json(USER_FILE, users)
                st.session_state.user = username
                st.session_state.logged_in = True
                st.success(f"New account created for {username}!")
                st.rerun()
            else:
                st.error("Please enter username and password")
    
    st.stop()

# -----------------------------
# Main Translator Interface
# -----------------------------
st.success(f"🤖 Welcome to AI Translator, {st.session_state.user}!")

# Automatic language detection - no need to select source language
st.markdown("### 🌍 Automatic Language Detection")
st.info("💡 Just type your text - AI will automatically detect the language!")

col1, col2 = st.columns([2, 1])

with col1:
    input_text = st.text_area(
        "📝 Enter text to translate", 
        placeholder="Type or paste any text in any language...",
        height=150
    )

with col2:
    st.markdown("#### 🎯 Translate to:")
    target_lang = st.selectbox(
        "Select target language",
        [lang for lang in LANGUAGES.keys() if lang != 'Auto Detect'],
        index=list(LANGUAGES.keys()).index('Urdu') if 'Urdu' in LANGUAGES else 1
    )
    
    # Translation options
    auto_detect = st.checkbox("🤖 Enable AI Auto-Detection", value=True)
    enable_tts = st.checkbox("🔊 Enable Text-to-Speech", value=True)

translate_btn = st.button("🚀 TRANSLATE NOW", type="primary", use_container_width=True)

st.markdown("---")

# -----------------------------
# Enhanced Translation Logic
# -----------------------------
if translate_btn and input_text.strip():
    try:
        with st.spinner("🔍 AI is detecting language and translating..."):
            # Automatic language detection and translation
            if auto_detect:
                # Auto detect source language
                detected_text = GoogleTranslator(source='auto', target='en').translate(input_text[:100])
                # Now translate to target language
                translated_text = GoogleTranslator(source='auto', target=LANGUAGES[target_lang]).translate(input_text)
                source_display = "Auto-Detected"
            else:
                # Use manual detection for Roman Urdu
                roman_urdu_words = ['tum', 'mera', 'tera', 'kyun', 'kaise', 'nahi', 'acha', 'shukriya', 'hai', 'main']
                if any(word in input_text.lower() for word in roman_urdu_words):
                    translated_text = GoogleTranslator(source='ur', target=LANGUAGES[target_lang]).translate(input_text)
                    source_display = "Roman Urdu"
                else:
                    translated_text = GoogleTranslator(source='auto', target=LANGUAGES[target_lang]).translate(input_text)
                    source_display = "Auto-Detected"
            
            # Display Results
            st.subheader("🎉 Translation Result")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📥 Original Text**")
                st.info(input_text)
                
            with col2:
                st.markdown(f"**📤 Translated Text ({target_lang})**")
                st.success(translated_text)
            
            # Text-to-Speech for ALL languages
            if enable_tts:
                st.subheader("🔊 Audio Output")
                
                try:
                    # For translated text
                    tts = gTTS(translated_text, lang=LANGUAGES[target_lang])
                    translated_audio_file = f"translated_{LANGUAGES[target_lang]}.mp3"
                    tts.save(translated_audio_file)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**🎧 Listen to Translation**")
                        st.audio(translated_audio_file, format="audio/mp3")
                    
                    # Try to create audio for original text if language is detectable
                    try:
                        if source_display != "Auto-Detected":
                            tts_original = gTTS(input_text, lang=LANGUAGES.get('ur', 'en'))
                            original_audio_file = "original_audio.mp3"
                            tts_original.save(original_audio_file)
                            
                            with col2:
                                st.markdown("**🎧 Listen to Original**")
                                st.audio(original_audio_file, format="audio/mp3")
                    except:
                        pass
                    
                    # Cleanup audio files
                    for file in [translated_audio_file, "original_audio.mp3"]:
                        if os.path.exists(file):
                            os.remove(file)
                            
                except Exception as e:
                    st.warning(f"⚠️ Audio generation issue: {str(e)}")
                    # Fallback to pyttsx3
                    try:
                        engine = pyttsx3.init()
                        engine.save_to_file(translated_text, "fallback_audio.wav")
                        engine.runAndWait()
                        st.audio("fallback_audio.wav", format="audio/wav")
                        if os.path.exists("fallback_audio.wav"):
                            os.remove("fallback_audio.wav")
                    except:
                        st.error("❌ Audio not available for this language")
            
            # Save to history
            user = st.session_state.user
            if user not in history:
                history[user] = []
            
            history[user].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": source_display,
                "target": target_lang,
                "original": input_text,
                "translated": translated_text
            })
            save_json(HISTORY_FILE, history)
            
            st.balloons()
            st.success("✅ Translation completed successfully!")

    except Exception as e:
        st.error(f"❌ Translation error: {str(e)}")
        st.info("💡 Please check your internet connection and try again.")

elif translate_btn:
    st.warning("⚠️ Please enter some text to translate")

# -----------------------------
# Translation History
# -----------------------------
st.markdown("---")
st.subheader("📚 Translation History")

if st.session_state.user in history and history[st.session_state.user]:
    user_history = history[st.session_state.user]
    
    # Show recent translations
    for i, entry in enumerate(reversed(user_history[-10:])):
        with st.expander(f"🕒 {entry['timestamp']} | {entry['source']} → {entry['target']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original:**")
                st.write(entry['original'])
            with col2:
                st.markdown("**Translated:**")
                st.write(entry['translated'])
            
            # Quick audio replay
            if st.button(f"🔊 Play Audio", key=f"audio_{i}"):
                try:
                    tts = gTTS(entry['translated'], lang=LANGUAGES[entry['target']])
                    tts.save(f"history_{i}.mp3")
                    st.audio(f"history_{i}.mp3", format="audio/mp3")
                    if os.path.exists(f"history_{i}.mp3"):
                        os.remove(f"history_{i}.mp3")
                except:
                    st.warning("Audio not available")
else:
    st.info("No translation history yet. Start translating to build your history!")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
        <div style='text-align: center;'>
            <h3>🤖 AI Translator</h3>
            <p>Powered by Google Translate • 1000+ Languages • Real-time Translation</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

st.markdown("---")
st.caption("© 2024 AI Translator - Intelligent Translation for Everyone")
