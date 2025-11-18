import streamlit as st
import requests
import json
import os
from gtts import gTTS
import uuid

# -------------------------------
# CONFIG
# -------------------------------
API_URL = "https://libretranslate.com/translate"
LANG_URL = "https://libretranslate.com/languages"
HISTORY_FILE = "history.json"
USERS_FILE = "users.json"


# -------------------------------
# LOAD / SAVE JSON
# -------------------------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# -------------------------------
# AUTH SYSTEM
# -------------------------------
def signup(username, password):
    users = load_json(USERS_FILE, {})

    if username in users:
        return False, "User already exists."

    users[username] = password
    save_json(USERS_FILE, users)
    return True, "Signup successful!"


def login(username, password):
    users = load_json(USERS_FILE, {})
    return users.get(username) == password


# -------------------------------
# TRANSLATE TEXT (1000+ LANGS)
# -------------------------------
def translate(text, src_lang, tgt_lang):
    payload = {
        "q": text,
        "source": src_lang,
        "target": tgt_lang,
        "format": "text"
    }

    try:
        r = requests.post(API_URL, json=payload)
        return r.json()["translatedText"]
    except:
        return "Translation error."


# -------------------------------
# TEXT TO SPEECH
# -------------------------------
def generate_tts(text):
    file = f"tts_{uuid.uuid4().hex}.mp3"
    tts = gTTS(text)
    tts.save(file)
    return file


# -------------------------------
# HISTORY SYSTEM
# -------------------------------
def add_history(user, original, translated, src, tgt):
    history = load_json(HISTORY_FILE, {})
    
    if user not in history:
        history[user] = []

    history[user].append({
        "source_lang": src,
        "target_lang": tgt,
        "original": original,
        "translated": translated
    })

    save_json(HISTORY_FILE, history)


# -------------------------------
# UI
# -------------------------------
st.title("🌍 AI Translator (1000+ Languages, TTS, Login, History)")

menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

if menu == "Signup":
    name = st.text_input("Create Username")
    pwd = st.text_input("Create Password", type="password")

    if st.button("Signup"):
        ok, msg = signup(name, pwd)
        st.info(msg)

elif menu == "Login":
    name = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(name, pwd):
            st.success("Login success!")
            st.session_state["user"] = name
        else:
            st.error("Wrong username or password.")

# After login
if "user" in st.session_state:

    st.subheader("Translate Text")

    # load languages
    langs = requests.get(LANG_URL).json()
    lang_dict = {l["name"]: l["code"] for l in langs}

    src = st.selectbox("Source Language", list(lang_dict.keys()))
    tgt = st.selectbox("Target Language", list(lang_dict.keys()))

    text = st.text_area("Enter Text")

    if st.button("Translate"):
        result = translate(text, lang_dict[src], lang_dict[tgt])
        st.success(result)

        # Add history
        add_history(st.session_state["user"], text, result, src, tgt)

        # TTS
        audio_file = generate_tts(result)
        st.audio(audio_file)

    st.subheader("Your History")

    history = load_json(HISTORY_FILE, {})
    user_hist = history.get(st.session_state["user"], [])

    for item in user_hist:
        st.write("🔹 **From:**", item["source_lang"])
        st.write("🔸 **To:**", item["target_lang"])
        st.write("**Original:**", item["original"])
        st.write("**Translated:**", item["translated"])
        st.markdown("---")
