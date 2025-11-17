import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import os
from datetime import datetime

# --------------------------------------------------
# 300+ Languages
# --------------------------------------------------
LANGUAGES = GoogleTranslator().get_supported_languages(as_dict=True)
LANG_LIST = list(LANGUAGES.keys())

# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🌐", layout="wide")
st.title("🌍 AI Translator — Translate Text & PDF in 300+ Languages")

st.markdown("#### Translate text or PDF instantly — supports 300+ global languages.")

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.header("🌐 Language Settings")
src = st.sidebar.selectbox("From Language", LANG_LIST, index=LANG_LIST.index("english"))
dest = st.sidebar.selectbox("To Language", LANG_LIST, index=LANG_LIST.index("urdu"))

# --------------------------------------------------
# Tabs
# --------------------------------------------------
tab1, tab2 = st.tabs(["📄 Text Translator", "📕 PDF Translator"])


# --------------------------------------------------
# TEXT TRANSLATION
# --------------------------------------------------
with tab1:
    st.subheader("✏️ Translate Text")

    text_input = st.text_area("Enter your text here:", height=200)

    if st.button("Translate Text"):
        if text_input.strip() == "":
            st.warning("Please enter some text.")
        else:
            translated = GoogleTranslator(source=src, target=dest).translate(text_input)
            st.success("Translation Completed!")
            st.text_area("Translated Text:", translated, height=250)

            # TTS Audio
            tts_file = "speech.mp3"
            tts = gTTS(translated)
            tts.save(tts_file)
            st.audio(tts_file, format="audio/mp3")

            # Download text
            st.download_button("⬇️ Download Translation", translated, file_name="translation.txt")


# --------------------------------------------------
# PDF TRANSLATION
# --------------------------------------------------
with tab2:
    st.subheader("📘 Translate PDF File")

    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_pdf is not None:
        if st.button("Translate PDF"):
            try:
                # Extract text from PDF
                reader = PyPDF2.PdfReader(uploaded_pdf)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text() + "\n"

                if full_text.strip() == "":
                    st.error("No text found in PDF (maybe scanned image PDF).")
                else:
                    # Translate extracted text
                    translated_pdf_text = GoogleTranslator(
                        source=src, target=dest
                    ).translate(full_text)

                    st.success("PDF Translated Successfully!")
                    st.text_area("Translated PDF Text:", translated_pdf_text, height=400)

                    # Download new translated PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                        c = canvas.Canvas(temp_pdf.name, pagesize=letter)
                        text_object = c.beginText(40, 750)
                        for line in translated_pdf_text.split("\n"):
                            text_object.textLine(line)
                        c.drawText(text_object)
                        c.save()

                        st.download_button(
                            "⬇️ Download Translated PDF",
                            open(temp_pdf.name, "rb"),
                            file_name="translated.pdf",
                            mime="application/pdf"
                        )

            except Exception as e:
                st.error(f"Error reading PDF: {e}")
