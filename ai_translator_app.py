import streamlit as st
import argostranslate.package
from argostranslate.translate import get_installed_languages
from gtts import gTTS
import PyPDF2
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import tempfile
import os
import json
from datetime import datetime

# -------------------------
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"

# -------------------------
# JSON helpers
def load_json_safe(path, default):
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except:
        return default

def save_json_safe(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Failed to save data: {e}")

users_data = load_json_safe(USERS_FILE, {"users": {}})
history_data = load_json_safe(HISTORY_FILE, {})

# -------------------------
# Session state
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------
# Load installed Argos languages
installed_languages = get_installed_languages()
LANG_LIST = [lang.name for lang in installed_languages]

# -------------------------
# Signup/Login UI
def auth_ui():
    st.title("🌍 Offline AI Translator — Login / Signup")
    choice = st.radio("Select Option:", ["Login", "Signup"])
    users_db = users_data["users"]

    if choice == "Login":
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in users_db and users_db[username]["password"] == password:
                st.session_state.user = username
                st.success(f"Welcome back, {username}!")
                st.stop()
            else:
                st.error("Invalid username or password.")

    else:
        new_user = st.text_input("Choose username", key="signup_user")
        new_pass = st.text_input("Choose password", type="password", key="signup_pass")
        if st.button("Create Account"):
            if not new_user or not new_pass:
                st.warning("Enter username and password.")
            elif new_user in users_db:
                st.warning("Username already exists.")
            else:
                users_db[new_user] = {"password": new_pass}
                users_data["users"] = users_db
                save_json_safe(USERS_FILE, users_data)
                st.session_state.user = new_user
                st.success(f"Account created! Welcome, {new_user}! 🎉")
                st.stop()

if st.session_state.user is None:
    auth_ui()
else:
    st.sidebar.write(f"👋 Logged in as **{st.session_state.user}**")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.stop()

# -------------------------
# Helper: Translate text (offline, unlimited)
def translate_text(text, source_lang, target_lang):
    src_lang = next((l for l in installed_languages if l.name == source_lang), None)
    tgt_lang = next((l for l in installed_languages if l.name == target_lang), None)
    if not src_lang or not tgt_lang:
        raise ValueError("Language not installed")
    translation = src_lang.get_translation(tgt_lang)
    return translation.translate(text)

# -------------------------
# Helper: Create PDF
def create_translated_pdf_pages(translated_pages, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    for i, page_text in enumerate(translated_pages, start=1):
        paragraphs = page_text.split("\n\n")
        story.append(Paragraph(f"<b>--- Translated Page {i} ---</b>", normal_style))
        story.append(Spacer(1, 12))
        for para in paragraphs:
            para = para.strip()
            if para:
                story.append(Paragraph(para.replace("\n", "<br/>"), normal_style))
                story.append(Spacer(1, 6))
        story.append(Spacer(1, 24))

    doc.build(story)

# -------------------------
# Sidebar: Language Selection
if not LANG_LIST:
    st.error("⚠️ No Argos Translate language packages installed! Install languages first.")
    st.stop()

src = st.sidebar.selectbox("From Language", LANG_LIST)
dest = st.sidebar.selectbox("To Language", LANG_LIST)

# -------------------------
# Tabs
tab1, tab2 = st.tabs(["📄 Text Translator", "📕 PDF Translator"])

# -------------------------
# Text Translator
with tab1:
    st.subheader("✏️ Translate Text")
    text_input = st.text_area("Enter your text here:", height=300)

    if st.button("Translate Text"):
        if not text_input.strip():
            st.warning("Please enter some text.")
        else:
            try:
                translated = translate_text(text_input, src, dest)
                st.success("Translation Completed!")
                st.text_area("Translated Text:", translated, height=300)

                # Save history
                user = st.session_state.user
                if user not in history_data:
                    history_data[user] = []
                history_data[user].append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "text",
                    "input": text_input,
                    "output": translated
                })
                save_json_safe(HISTORY_FILE, history_data)

                # TTS (validate length)
                if len(translated) < 5000:
                    tts_file = "speech.mp3"
                    tts = gTTS(translated)
                    tts.save(tts_file)
                    st.audio(tts_file, format="audio/mp3")
                else:
                    st.warning("Text is too long for TTS, skipping voice output.")

                # Download text
                st.download_button("⬇️ Download Translation", translated, file_name="translation.txt")
            except Exception as e:
                st.error(f"Translation Failed: {e}")

# -------------------------
# PDF Translator
with tab2:
    st.subheader("📘 Translate PDF File")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_pdf is not None:
        if st.button("Translate PDF"):
            try:
                reader = PyPDF2.PdfReader(uploaded_pdf)
                pages_text = [page.extract_text() or "" for page in reader.pages]

                if not any(pages_text):
                    st.error("No text found in PDF (scanned/image PDFs not supported).")
                else:
                    translated_pages = []
                    for i, page_text in enumerate(pages_text):
                        if page_text.strip():
                            translated_pages.append(translate_text(page_text, src, dest))
                        else:
                            translated_pages.append("")
                        st.progress((i+1)/len(pages_text))  # Show progress bar

                    preview = "\n\n---\n\n".join([p[:1000] for p in translated_pages if p])
                    st.subheader(f"Translated PDF Preview → {dest}")
                    st.text_area("Preview (first part)", preview, height=300)

                    user = st.session_state.user
                    if user not in history_data:
                        history_data[user] = []
                    history_data[user].append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "pdf",
                        "filename": uploaded_pdf.name,
                        "output": translated_pages
                    })
                    save_json_safe(HISTORY_FILE, history_data)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                        create_translated_pdf_pages(translated_pages, tmp_pdf.name)
                        with open(tmp_pdf.name, "rb") as f:
                            st.download_button(
                                "⬇️ Download Translated PDF",
                                data=f,
                                file_name=f"translated_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
                                mime="application/pdf"
                            )
                        os.unlink(tmp_pdf.name)

            except Exception as e:
                st.error(f"Error processing PDF: {e}")

# -------------------------
# History
if st.checkbox("📜 Show History"):
    user_history = history_data.get(st.session_state.user, [])
    if user_history:
        for h in reversed(user_history[-10:]):
            st.markdown(f"**🕒 {h['time']} | Type: {h['type']}**")
            if h['type'] == 'text':
                st.write(f"**Input:** {h['input']}")
                st.write(f"**Output:** {h['output']}")
            else:
                st.write(f"**PDF Filename:** {h['filename']}")
                st.write(f"**Translated Pages Preview:** {[p[:200]+'...' for p in h['output']]}")
            st.markdown("---")
    else:
        st.info("No history yet.")
