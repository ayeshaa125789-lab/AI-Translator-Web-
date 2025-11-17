import streamlit as st
from googletrans import Translator, LANGUAGES
from PyPDF2 import PdfReader
import io

# -------------------------
# Configuration and Initialization
# Initialize the Translator object
translator = Translator()

# Map official codes (used by Google) to readable names for the selectbox
# We reverse the standard LANGUAGES dict to get Name: Code for easy dropdown
LANG_NAME_TO_CODE = {name: code for code, name in LANGUAGES.items()}
# List of all supported language names, sorted for the dropdown
ALL_LANGUAGE_NAMES = sorted(LANG_NAME_TO_CODE.keys()) 

# -------------------------
# Session state & Authentication
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "users" not in st.session_state:
    st.session_state["users"] = {}

def signup():
    """Handles user signup and saves credentials to session state."""
    st.subheader("✍️ Signup")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Create Account"):
        if email in st.session_state["users"]:
            st.error("User already exists.")
        elif not email or not password:
            st.warning("Enter email and password.")
        else:
            st.session_state["users"][email] = password
            st.success("Account created! You can now log in.")

def login():
    """Handles user login and sets the logged_in state."""
    st.subheader("🔑 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if email in st.session_state["users"] and st.session_state["users"][email] == password:
            st.session_state["logged_in"] = True
            st.success("Logged in successfully!")
            st.rerun() # Rerun to hide the login screen
        else:
            st.error("Invalid email or password.")

# --- Authentication Gate ---
if not st.session_state["logged_in"]:
    st.title("🌐 Translator Login Gate")
    tab1, tab2 = st.tabs(["Login", "Signup"])
    with tab1: login()
    with tab2: signup()
    st.stop()
# -------------------------


# -------------------------
# Main Translator App
st.title("🚀 Global Unlimited Translator")
st.write(f"Supports **{len(ALL_LANGUAGE_NAMES)}** languages via Google Translate API.")

# -------------------------
# Language Selection
src_lang_name = st.selectbox("From Language:", ["Auto Detect"] + ALL_LANGUAGE_NAMES)
dest_lang_name = st.selectbox("To Language:", ALL_LANGUAGE_NAMES)

# Helper: translate text using googletrans
@st.cache_data(show_spinner=False) # Cache results to avoid re-translation on app interaction
def translate_text(text, dest_name, src_name=None):
    """Translates text using the googletrans library."""
    dest_code = LANG_NAME_TO_CODE[dest_name]
    
    if src_name == "Auto Detect":
        src_code = 'auto'
    else:
        # Get the source code only if it's not Auto Detect
        src_code = LANG_NAME_TO_CODE.get(src_name, 'auto') 
    
    # Perform the translation call
    translation = translator.translate(
        text,
        src=src_code, 
        dest=dest_code
    )
    return translation.text

# -------------------------
# Input Method Selection
input_method = st.radio("Choose Input Type:", ("Translate Text Directly", "Upload PDF File"))

translated_content = None
full_translated_text = ""

if input_method == "Upload PDF File":
    # -------------------------
    # PDF Upload and Processing
    pdf_file = st.file_uploader("Upload PDF to translate", type=["pdf"])

    if pdf_file:
        if st.button("Translate PDF"):
            st.info("Extracting and translating PDF pages... Please wait.")
            
            try:
                # Read the file from the uploaded object
                reader = PdfReader(io.BytesIO(pdf_file.read()))
                pages_text = [page.extract_text() or "" for page in reader.pages]
            except Exception as e:
                st.error(f"Error reading PDF: {e}")
                st.stop()
            
            translated_pages = []
            progress = st.progress(0)
            
            # Use global variable for download link
            global full_translated_text
            full_translated_text = ""

            for i, page_text in enumerate(pages_text):
                if page_text.strip():
                    try:
                        translated_text = translate_text(page_text, dest_lang_name, src_lang_name)
                        translated_pages.append(translated_text)
                        full_translated_text += translated_text + "\n\n"
                    except Exception as e:
                        st.error(f"Translation error on page {i+1}. Skipping. Error: {e}")
                        translated_pages.append("--- Translation Failed ---")
                else:
                    translated_pages.append("")
                
                progress.progress((i + 1) / len(pages_text))

            st.success("PDF translation completed!")
            translated_content = translated_pages

else:
    # -------------------------
    # Direct Text Input
    input_text = st.text_area("Enter Text to Translate:", height=300)

    if input_text:
        if st.button("Translate Text"):
            st.info("Translating text...")
            try:
                translated_text = translate_text(input_text, dest_lang_name, src_lang_name)
                st.success("Text translation completed!")
                translated_content = [translated_text] # Wrap in list for unified output
                global full_translated_text
                full_translated_text = translated_text
            except Exception as e:
                st.error(f"Translation Failed: {e}")

# -------------------------
# Display Output and Download
if translated_content:
    st.header(f"Results (Translated to {dest_lang_name})")
    
    # Display page-by-page preview for PDF or just the text
    for idx, content in enumerate(translated_content):
        if input_method == "Upload PDF File":
            title = f"Translated Content (Page {idx+1})"
        else:
            title = "Translated Content"
            
        st.text_area(title, 
                     content, height=200, key=f"translated_output_{idx}")

    # Download button for the complete text
    if full_translated_text:
        st.download_button(
            label="Download Full Translated Text",
            data=full_translated_text,
            file_name="translated_document.txt",
            mime="text/plain"
        )
