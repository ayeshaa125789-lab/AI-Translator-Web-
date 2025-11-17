import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import PyPDF2
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import tempfile
import os
from datetime import datetime

# -------------------------
# Languages
# -------------------------
LANGUAGES = GoogleTranslator().get_supported_languages(as_dict=True)
LANG_LIST = list(LANGUAGES.keys())

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🌐", layout="wide")
st.title("🌍 AI Translator — Translate Text & PDF in 300+ Languages")
st.markdown("Supports unlimited text and large PDFs with chunked translation.")

# -------------------------
# Sidebar: Language Selection
# -------------------------
st.sidebar.header("🌐 Language Settings")
src = st.sidebar.selectbox("From Language", LANG_LIST, index=LANG_LIST.index("english"))
dest = st.sidebar.selectbox("To Language", LANG_LIST, index=LANG_LIST.index("urdu"))

# -------------------------
# Tabs
# -------------------------
tab1, tab2 = st.tabs(["📄 Text Translator", "📕 PDF Translator"])

# -------------------------
# Helper: Chunked translation to avoid Google limits
# -------------------------
def translate_text_chunked(text, source_lang, target_lang, chunk_size=1000):
    """
    Splits text into chunks (default 1000 chars) and translates each chunk separately
    using translate_batch to avoid 'too many requests' errors.
    """
    text = text.replace("\n", " ")  # normalize newlines
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    translated_chunks = GoogleTranslator(source=source_lang, target=target_lang).translate_batch(chunks)
    return " ".join(translated_chunks)

# -------------------------
# Helper: Create PDF with paragraphs
# -------------------------
def create_translated_pdf_pages(translated_pages, output_path):
    """
    Creates a properly formatted PDF from translated pages using reportlab's Paragraphs.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    for i, page_text in enumerate(translated_pages, start=1):
        # split into paragraphs (double newline)
        paragraphs = page_text.split("\n\n")
        story.append(Paragraph(f"<b>--- Translated Page {i} ---</b>", normal_style))
        story.append(Spacer(1, 12))
        for para in paragraphs:
            para = para.strip()
            if para:
                story.append(Paragraph(para.replace("\n", "<br/>"), normal_style))
                story.append(Spacer(1, 6))
        story.append(Spacer(1, 24))  # space between pages

    doc.build(story)

# -------------------------
# Text Translator
# -------------------------
with tab1:
    st.subheader("✏️ Translate Text")
    text_input = st.text_area("Enter your text here:", height=200)

    if st.button("Translate Text"):
        if not text_input.strip():
            st.warning("Please enter some text.")
        else:
            translated = translate_text_chunked(text_input, src, dest)
            st.success("Translation Completed!")
            st.text_area("Translated Text:", translated, height=250)

            # TTS
            tts_file = "speech.mp3"
            tts = gTTS(translated)
            tts.save(tts_file)
            st.audio(tts_file, format="audio/mp3")

            # Download text
            st.download_button("⬇️ Download Translation", translated, file_name="translation.txt")

# -------------------------
# PDF Translator
# -------------------------
with tab2:
    st.subheader("📘 Translate PDF File")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_pdf is not None:
        if st.button("Translate PDF"):
            try:
                reader = PyPDF2.PdfReader(uploaded_pdf)
                pages_text = []
                for page in reader.pages:
                    pages_text.append(page.extract_text() or "")

                if not any(pages_text):
                    st.error("No text found in PDF (scanned/image PDFs not supported).")
                else:
                    translated_pages = []
                    for page_text in pages_text:
                        if page_text.strip():
                            translated_pages.append(translate_text_chunked(page_text, src, dest))
                        else:
                            translated_pages.append("")

                    # Show preview
                    preview = "\n\n---\n\n".join([p[:1000] for p in translated_pages if p])
                    st.subheader(f"Translated PDF Preview → {dest}")
                    st.text_area("Preview (first part)", preview, height=300)

                    # Create translated PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                        create_translated_pdf_pages(translated_pages, tmp_pdf.name)
                        st.download_button(
                            "⬇️ Download Translated PDF",
                            open(tmp_pdf.name, "rb"),
                            file_name=f"translated_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                        os.unlink(tmp_pdf.name)

            except Exception as e:
                st.error(f"Error processing PDF: {e}")
