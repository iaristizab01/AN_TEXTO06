import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Reconóceme esto",
    page_icon="🧠",
    layout="wide",
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    body {
        background-color: white;
        color: black;
    }
    .stApp {
        background-color: white !important;
        color: black !important;
        font-family: 'Helvetica', sans-serif;
    }
    .title {
        text-align: center;
        font-size: 3em;
        font-weight: 600;
        margin-top: 20px;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2em;
        color: #444;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: black;
        color: white;
        border-radius: 10px;
        padding: 0.6em 1.2em;
    }
    .stButton>button:hover {
        background-color: #444;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO NARRATIVO ---
st.markdown("<div class='title'>Reconóceme esto</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Experimento sobre cómo una red neuronal nombra el mundo</div>", unsafe_allow_html=True)

text = " "

# --- FUNCIONES ---
def text_to_speech(input_language, output_language, text, tld):
    translation = GoogleTranslator(source=input_language, target=output_language).translate(text)
    tts = gTTS(translation, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    if not os.path.exists("temp"):
        os.mkdir("temp")
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, translation


def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

remove_files(7)

# --- IMAGEN ---
st.write("### 📸 Carga una imagen o usa tu cámara")
col1, col2 = st.columns(2)
with col1:
    cam_ = st.checkbox("Usar cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una foto del mundo...")
else:
    img_file_buffer = None

with col2:
    bg_image = st.file_uploader("O carga una imagen:", type=["png", "jpg", "jpeg"])

if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Tu imagen fue observada por la máquina.', use_container_width=True)

    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())

    img_cv = cv2.imread(f'{uploaded_file.name}')
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.markdown("#### La red ve lo siguiente:")
    st.write(text)

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.markdown("#### La red interpreta:")
    st.write(text)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Parámetros de traducción")
    in_lang = st.selectbox("Idioma detectado:", ("Inglés", "Español", "Japonés", "Coreano", "Mandarín"))
    out_lang = st.selectbox("Traducir a:", ("Español", "Inglés", "Francés", "Alemán", "Portugués"))

    lang_map = {
        "Español": "es",
        "Inglés": "en",
        "Francés": "fr",
        "Alemán": "de",
        "Portugués": "pt",
        "Japonés": "ja",
        "Coreano": "ko",
        "Mandarín": "zh-cn"
    }

    input_language = lang_map[in_lang]
    output_language = lang_map[out_lang]

    accent = st.selectbox(
        "Acento para la voz:",
        ["Default", "India", "United Kingdom", "United States", "Canada", "Australia"]
    )

    accents = {
        "Default": "com",
        "India": "co.in",
        "United Kingdom": "co.uk",
        "United States": "com",
        "Canada": "ca",
        "Australia": "com.au"
    }

    tld = accents[accent]
    display_output_text = st.checkbox("Mostrar texto traducido")


# --- BOTÓN PRINCIPAL ---
st.markdown("---")
st.markdown("### 🪞 ¿Qué dice la máquina?")
if st.button("Traducir y hablar"):
    if text.strip() == "":
        st.warning("Por favor, toma o carga una imagen primero.")
    else:
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()

        st.audio(audio_bytes, format="audio/mp3")

        if display_output_text:
            st.markdown("#### Traducción interpretada por la red:")
            st.write(output_text)

st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:0.9em; color:#666;'>© 2025 — Proyecto experimental sobre visión y lenguaje · Desarrollado con Streamlit</p>",
    unsafe_allow_html=True
)
