import streamlit as st
import json
import os
from datetime import datetime
import tempfile
import hashlib

# Translation imports
import argostranslate.package
import argostranslate.translate

# PDF imports
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# TTS imports
from gtts import gTTS
import io

# Initialize session state
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'installed_models' not in st.session_state:
        st.session_state.installed_models = []

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
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            'password': self.hash_password(password),
            'history': []
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
        self.load_models()
    
    def load_models(self):
        try:
            installed_packages = argostranslate.package.get_installed_packages()
            languages = set()
            for pkg in installed_packages:
                languages.add(pkg.from_code)
                languages.add(pkg.to_code)
            st.session_state.installed_models = sorted(list(languages))
        except Exception as e:
            st.session_state.installed_models = []
            st.error(f"Error loading translation models: {e}")
    
    def get_available_languages(self):
        return st.session_state.installed_models
    
    def translate_text(self, text, from_lang, to_lang):
        try:
            if from_lang == to_lang:
                return text
            
            installed_packages = argostranslate.package.get_installed_packages()
            for pkg in installed_packages:
                if pkg.from_code == from_lang and pkg.to_code == to_lang:
                    return pkg.translate(text)
            
            st.error(f"No translation model found for {from_lang} to {to_lang}")
            return None
        except Exception as e:
            st.error(f"Translation error: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            return text.strip() if text else None
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return None
    
    def create_translated_pdf(self, translated_text, filename):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                doc = SimpleDocTemplate(tmp_file.name, pagesize=letter)
                styles = getSampleStyleSheet()
                
                translated_style = ParagraphStyle(
                    'TranslatedStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=14,
                    spaceAfter=12
                )
                
                story = []
                header_style = ParagraphStyle(
                    'HeaderStyle',
                    parent=styles['Heading1'],
                    fontSize=14,
                    spaceAfter=18
                )
                
                story.append(Paragraph(f"Translated Document - {datetime.now().strftime('%Y-%m-%d %H:%M')}", header_style))
                story.append(Spacer(1, 0.2*inch))
                
                paragraphs = translated_text.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), translated_style))
                        story.append(Spacer(1, 0.1*inch))
                
                doc.build(story)
                
                with open(tmp_file.name, 'rb') as f:
                    pdf_data = f.read()
                
                os.unlink(tmp_file.name)
                return pdf_data
        except Exception as e:
            st.error(f"Error creating PDF: {e}")
            return None

class TTSManager:
    @staticmethod
    def text_to_speech(text, language='en'):
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
    st.title("🔐 AI Translator Pro - Login")
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
                    st.write(f"📄 {item.get('filename', 'document.pdf')}")
    else:
        st.sidebar.info("No translation history yet")
    
    # Main content
    st.title("🌐 AI Translator Pro")
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
        ```
        """)
        return
    
    col1, col2 = st.columns(2)
    with col1:
        from_lang = st.selectbox("From Language", available_languages, 
                               index=available_languages.index('en') if 'en' in available_languages else 0)
    with col2:
        to_lang = st.selectbox("To Language", available_languages, 
                             index=available_languages.index('es') if 'es' in available_languages else 1)
    
    # Translation type
    translation_type = st.radio(
        "Choose translation type:",
        ["📝 Text Translation", "📄 PDF Translation"],
        horizontal=True
    )
    
    if translation_type == "📝 Text Translation":
        handle_text_translation(user_manager, translation_manager, tts_manager, from_lang, to_lang)
    else:
        handle_pdf_translation(user_manager, translation_manager, tts_manager, from_lang, to_lang)
    
    # Settings
    with st.sidebar.expander("⚙️ Settings & Info"):
        st.write("**Installed Languages:**")
        st.write(", ".join(available_languages) if available_languages else "None")
        st.markdown("---")
        st.write("**Install more models:**")
        st.code("argospm install translate-en-de\nargospm install translate-en-zh\n# etc.")

def handle_text_translation(user_manager, translation_manager, tts_manager, from_lang, to_lang):
    st.subheader("📝 Text Translation")
    
    input_text = st.text_area(
        "Enter text to translate:",
        height=150,
        placeholder="Type or paste your text here...",
        key="text_input"
    )
    
    if st.button("🚀 Translate Text", type="primary", use_container_width=True):
        if input_text.strip():
            with st.spinner("Translating..."):
                translated_text = translation_manager.translate_text(input_text, from_lang, to_lang)
                
                if translated_text:
                    # Display results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Original Text")
                        st.text_area("", input_text, height=200, key="original_display")
                    with col2:
                        st.subheader("Translated Text")
                        st.text_area("", translated_text, height=200, key="translated_display")
                    
                    # Audio & Download
                    st.subheader("🎵 Audio & Download")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🔊 Listen to Translation", use_container_width=True):
                            audio_file = tts_manager.text_to_speech(translated_text, to_lang)
                            if audio_file:
                                st.audio(audio_file, format='audio/mp3')
                    
                    with col2:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        txt_content = f"Original ({from_lang}):\n{input_text}\n\nTranslated ({to_lang}):\n{translated_text}"
                        st.download_button(
                            label="📥 Download TXT",
                            data=txt_content,
                            file_name=f"translation_{timestamp}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    # Save history
                    history_item = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'type': 'text',
                        'from_lang': from_lang,
                        'to_lang': to_lang,
                        'input': input_text[:500],
                        'output': translated_text[:500]
                    }
                    if user_manager.save_user_history(st.session_state.user, history_item):
                        st.session_state.history = user_manager.get_user_history(st.session_state.user)
                else:
                    st.error("Translation failed. Please try different languages.")
        else:
            st.warning("Please enter some text to translate")

def handle_pdf_translation(user_manager, translation_manager, tts_manager, from_lang, to_lang):
    st.subheader("📄 PDF Translation")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'], key="pdf_uploader")
    
    if uploaded_file is not None:
        if st.button("🚀 Translate PDF", type="primary", use_container_width=True):
            with st.spinner("Processing PDF..."):
                original_text = translation_manager.extract_text_from_pdf(uploaded_file)
                
                if original_text:
                    translated_text = translation_manager.translate_text(original_text, from_lang, to_lang)
                    
                    if translated_text:
                        # Preview
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Original Content Preview")
                            preview_original = original_text[:800] + "..." if len(original_text) > 800 else original_text
                            st.text_area("", preview_original, height=250, key="pdf_original_preview")
                        with col2:
                            st.subheader("Translated Content Preview")
                            preview_translated = translated_text[:800] + "..." if len(translated_text) > 800 else translated_text
                            st.text_area("", preview_translated, height=250, key="pdf_translated_preview")
                        
                        # Download PDF
                        st.subheader("📥 Download Translated PDF")
                        pdf_data = translation_manager.create_translated_pdf(translated_text, uploaded_file.name)
                        
                        if pdf_data:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            st.download_button(
                                label="📥 Download Translated PDF",
                                data=pdf_data,
                                file_name=f"translated_{uploaded_file.name}_{timestamp}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        # Audio preview
                        st.subheader("🎵 Audio Preview")
                        if st.button("🔊 Listen to Translation Preview", use_container_width=True):
                            audio_file = tts_manager.text_to_speech(translated_text[:400], to_lang)
                            if audio_file:
                                st.audio(audio_file, format='audio/mp3')
                        
                        # Save history
                        history_item = {
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'type': 'pdf',
                            'from_lang': from_lang,
                            'to_lang': to_lang,
                            'filename': uploaded_file.name,
                            'input': original_text[:300],
                            'output': translated_text[:300]
                        }
                        if user_manager.save_user_history(st.session_state.user, history_item):
                            st.session_state.history = user_manager.get_user_history(st.session_state.user)
                    else:
                        st.error("PDF translation failed.")
                else:
                    st.error("""
                    ❌ Could not extract text from PDF. 
                    
                    Please ensure:
                    - It's a text-based PDF (not scanned images)
                    - The PDF is not password protected
                    - The PDF contains readable text
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
