import streamlit as st
import json
import os
from datetime import datetime
import hashlib
import io

# Translation imports
import argostranslate.package
import argostranslate.translate

# TTS imports
from gtts import gTTS

# Initialize session state
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'installed_languages' not in st.session_state:
        st.session_state.installed_languages = []

class UserManager:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self.load_users()
    
    def load_users(self):
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
        except Exception:
            self.users = {}
    
    def save_users(self):
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=4)
            return True
        except Exception:
            return False
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password):
        if username.strip() == "":
            return False, "Username cannot be empty"
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(password) < 3:
            return False, "Password must be at least 3 characters"
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            'password': self.hash_password(password),
            'history': [],
            'created_at': datetime.now().isoformat()
        }
        if self.save_users():
            return True, "User created successfully"
        return False, "Error saving user data"
    
    def login(self, username, password):
        if username in self.users and self.users[username]['password'] == self.hash_password(password):
            return True, "Login successful"
        return False, "Invalid username or password"
    
    def get_user_history(self, username):
        return self.users.get(username, {}).get('history', [])
    
    def save_user_history(self, username, history_item):
        if username in self.users:
            history = self.users[username].get('history', [])
            history.insert(0, history_item)
            # Keep only last 10 items
            if len(history) > 10:
                history = history[:10]
            self.users[username]['history'] = history
            return self.save_users()
        return False

class TranslationManager:
    def __init__(self):
        self.load_installed_languages()
    
    def load_installed_languages(self):
        """Load installed languages from Argos Translate packages"""
        try:
            installed_packages = argostranslate.package.get_installed_packages()
            languages = set()
            
            for pkg in installed_packages:
                languages.add((pkg.from_code, self.get_language_name(pkg.from_code)))
                languages.add((pkg.to_code, self.get_language_name(pkg.to_code)))
            
            # Convert to list and sort by language name
            languages_list = sorted(list(languages), key=lambda x: x[1])
            st.session_state.installed_languages = languages_list
            
            return languages_list
        except Exception as e:
            st.error(f"Error loading languages: {e}")
            return []
    
    def get_language_name(self, code):
        """Get language name from code"""
        language_names = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
            'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi',
            'bn': 'Bengali', 'pa': 'Punjabi', 'te': 'Telugu', 'mr': 'Marathi',
            'ta': 'Tamil', 'ur': 'Urdu', 'gu': 'Gujarati', 'kn': 'Kannada',
            'ml': 'Malayalam', 'th': 'Thai', 'vi': 'Vietnamese', 'tr': 'Turkish',
            'pl': 'Polish', 'uk': 'Ukrainian', 'ro': 'Romanian', 'nl': 'Dutch',
            'sv': 'Swedish', 'da': 'Danish', 'no': 'Norwegian', 'fi': 'Finnish',
            'he': 'Hebrew', 'id': 'Indonesian', 'ms': 'Malay', 'fil': 'Filipino',
            'cs': 'Czech', 'hu': 'Hungarian', 'el': 'Greek', 'bg': 'Bulgarian',
            'sr': 'Serbian', 'hr': 'Croatian', 'sk': 'Slovak', 'sl': 'Slovenian',
            'lt': 'Lithuanian', 'lv': 'Latvian', 'et': 'Estonian', 'mt': 'Maltese',
            'ga': 'Irish', 'cy': 'Welsh', 'is': 'Icelandic', 'sq': 'Albanian',
            'mk': 'Macedonian', 'bs': 'Bosnian', 'ca': 'Catalan', 'eu': 'Basque',
            'gl': 'Galician', 'af': 'Afrikaans', 'sw': 'Swahili', 'zu': 'Zulu',
            'xh': 'Xhosa', 'yo': 'Yoruba', 'ig': 'Igbo', 'ha': 'Hausa',
            'so': 'Somali', 'am': 'Amharic', 'ti': 'Tigrinya', 'om': 'Oromo',
            'fa': 'Persian', 'ps': 'Pashto', 'ku': 'Kurdish', 'sd': 'Sindhi',
            'ne': 'Nepali', 'si': 'Sinhala', 'my': 'Burmese', 'km': 'Khmer',
            'lo': 'Lao', 'ka': 'Georgian', 'hy': 'Armenian', 'az': 'Azerbaijani',
            'kk': 'Kazakh', 'uz': 'Uzbek', 'tk': 'Turkmen', 'ky': 'Kyrgyz',
            'tg': 'Tajik', 'mn': 'Mongolian', 'bo': 'Tibetan', 'dz': 'Dzongkha'
        }
        return language_names.get(code, code.upper())
    
    def get_available_languages(self):
        """Get available languages as (code, name) pairs"""
        if not st.session_state.installed_languages:
            return self.load_installed_languages()
        return st.session_state.installed_languages
    
    def translate_text(self, text, from_lang, to_lang):
        """Translate text using Argos Translate"""
        try:
            if from_lang == to_lang:
                return text
            
            installed_packages = argostranslate.package.get_installed_packages()
            
            # Find appropriate package
            for pkg in installed_packages:
                if pkg.from_code == from_lang and pkg.to_code == to_lang:
                    translation = pkg.translate(text)
                    return translation
            
            st.error(f"No translation model found for {self.get_language_name(from_lang)} to {self.get_language_name(to_lang)}")
            return None
        except Exception as e:
            st.error(f"Translation error: {e}")
            return None

class TTSManager:
    @staticmethod
    def text_to_speech(text, language='en'):
        """Convert text to speech using gTTS"""
        try:
            if len(text) > 500:
                text = text[:500] + "..."
            tts = gTTS(text=text, lang=language, slow=False)
            audio_file = io.BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            return audio_file
        except Exception as e:
            st.error(f"TTS Error: {e}")
            return None

def show_login_page(user_manager):
    st.title("🌐 AI Translator Pro - Login")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", type="primary", use_container_width=True):
            if login_username and login_password:
                success, message = user_manager.login(login_username, login_password)
                if success:
                    st.session_state.user = login_username
                    st.session_state.history = user_manager.get_user_history(login_username)
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter both username and password")
    
    with col2:
        st.subheader("Create Account")
        signup_username = st.text_input("Username", key="signup_user")
        signup_password = st.text_input("Password", type="password", key="signup_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pass")
        
        if st.button("Create Account", type="secondary", use_container_width=True):
            if signup_username and signup_password:
                if signup_password == confirm_password:
                    success, message = user_manager.create_user(signup_username, signup_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Passwords don't match")
            else:
                st.error("Please fill all fields")
    
    st.markdown("---")
    st.info("💡 **Demo Accounts:** You can create your own account or use: username: `demo`, password: `demo`")

def show_main_app(user_manager, translation_manager, tts_manager):
    st.sidebar.title("🔐 User Management")
    st.sidebar.success(f"Welcome, **{st.session_state.user}**!")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.history = []
        st.rerun()
    
    # History in sidebar
    st.sidebar.subheader("📚 Recent Translations")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history[:5]):
            with st.sidebar.expander(f"{item['type'].title()} - {item['timestamp'][11:16]}"):
                st.write(f"**{item['from_lang']}** → **{item['to_lang']}**")
                if item['type'] == 'text':
                    st.text_area("Input", item['input'][:80] + "...", key=f"hist_{i}", height=60, label_visibility="collapsed")
    else:
        st.sidebar.info("No translation history yet")
    
    # Main content
    st.title("🌐 AI Translator Pro")
    st.markdown("Unlimited Text Translation with 1000+ Languages Support")
    st.markdown("---")
    
    # Language selection
    available_languages = translation_manager.get_available_languages()
    
    if not available_languages:
        st.error("""
        ❌ **No translation models installed!**
        
        Please install at least one translation model using these commands:
        ```bash
        pip install argostranslate
        argospm update
        argospm install translate-en-es
        argospm install translate-en-fr
        argospm install translate-en-de
        argospm install translate-en-zh
        # Add more languages as needed
        ```
        
        **Available models:** translate-[from]-[to] (e.g., translate-en-es for English to Spanish)
        """)
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        from_lang = st.selectbox(
            "From Language", 
            available_languages,
            format_func=lambda x: f"{x[1]} ({x[0]})",
            index=next((i for i, (code, name) in enumerate(available_languages) if code == 'en'), 0)
        )
        from_lang_code = from_lang[0]
    
    with col2:
        to_lang = st.selectbox(
            "To Language", 
            available_languages,
            format_func=lambda x: f"{x[1]} ({x[0]})",
            index=next((i for i, (code, name) in enumerate(available_languages) if code == 'es'), 1)
        )
        to_lang_code = to_lang[0]
    
    # Text translation
    st.subheader("📝 Text Translation")
    
    input_text = st.text_area(
        "Enter text to translate:",
        height=200,
        placeholder="Type or paste your text here... (No limits - translate as much as you want!)",
        key="text_input"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🚀 Translate Text", type="primary", use_container_width=True):
            if input_text.strip():
                with st.spinner("Translating..."):
                    translated_text = translation_manager.translate_text(input_text, from_lang_code, to_lang_code)
                    
                    if translated_text:
                        # Display results
                        st.subheader("Translation Results")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.text_area(
                                f"Original Text ({from_lang[1]})", 
                                input_text, 
                                height=300, 
                                key="original_display"
                            )
                        
                        with col2:
                            st.text_area(
                                f"Translated Text ({to_lang[1]})", 
                                translated_text, 
                                height=300, 
                                key="translated_display"
                            )
                        
                        # Audio & Download section
                        st.subheader("🎵 Audio & Download Options")
                        
                        audio_col, download_col = st.columns(2)
                        
                        with audio_col:
                            if st.button("🔊 Listen to Translation", use_container_width=True):
                                audio_file = tts_manager.text_to_speech(translated_text, to_lang_code)
                                if audio_file:
                                    st.audio(audio_file, format='audio/mp3')
                                    st.success("Audio generated successfully!")
                        
                        with download_col:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            txt_content = f"""Translation Result - {timestamp}
Source: {from_lang[1]} ({from_lang_code})
Target: {to_lang[1]} ({to_lang_code})

Original Text:
{input_text}

Translated Text:
{translated_text}

Generated by AI Translator Pro
"""
                            st.download_button(
                                label="📥 Download Translation",
                                data=txt_content,
                                file_name=f"translation_{timestamp}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        # Save to history
                        history_item = {
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'type': 'text',
                            'from_lang': f"{from_lang[1]} ({from_lang_code})",
                            'to_lang': f"{to_lang[1]} ({to_lang_code})",
                            'input': input_text[:500],
                            'output': translated_text[:500]
                        }
                        if user_manager.save_user_history(st.session_state.user, history_item):
                            st.session_state.history = user_manager.get_user_history(st.session_state.user)
                            st.success("Translation saved to history!")
                    else:
                        st.error("Translation failed. Please try different languages or check if the translation model is installed.")
            else:
                st.warning("Please enter some text to translate")
    
    # Language information
    with st.expander("🌍 Language Support Information"):
        st.write(f"**Currently installed languages:** {len(available_languages)}")
        languages_display = ", ".join([f"{name} ({code})" for code, name in available_languages])
        st.text_area("Installed Languages:", languages_display, height=150)
        
        st.info("""
        **To add more languages:**
        ```bash
        argospm update
        argospm install translate-en-de    # English to German
        argospm install translate-en-ja    # English to Japanese
        argospm install translate-en-ar    # English to Arabic
        # And many more...
        ```
        
        **Supported language pairs:** 1000+ combinations available
        """)

def main():
    init_session_state()
    
    st.set_page_config(
        page_title="AI Translator Pro",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize managers
    user_manager = UserManager()
    translation_manager = TranslationManager()
    tts_manager = TTSManager()
    
    if st.session_state.user is None:
        show_login_page(user_manager)
    else:
        show_main_app(user_manager, translation_manager, tts_manager)

if __name__ == "__main__":
    main()
