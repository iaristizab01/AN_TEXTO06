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


text = " "

# Función para traducir y convertir texto en audio
def text_to_speech(input_language, output_language, text, tld):
    translation = GoogleTranslator(source=input_language, target=output_language).translate(text)
    tts = gTTS(translation, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, translation


# Función para limpiar archivos antiguos
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

remove_files(7)


# Interfaz Streamlit
st.title("🧠 Reconocimiento Óptico de Caracteres")
st.subheader("Elige la fuente de la imagen: cámara o archivo cargado")

cam_ = st.checkbox("Usar Cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.subheader("Procesamiento para Cámara")
    filtro = st.radio("Filtro para imagen con cámara", ('Sí', 'No'))


bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg", "jpeg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada.', use_container_width=True)
    
    # Guardar imagen temporalmente
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())
    
    st.success(f"Imagen guardada como {uploaded_file.name}")
    img_cv = cv2.imread(f'{uploaded_file.name}')
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write(text)


if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)
        
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write(text)


# --- Sidebar configuración de traducción ---
with st.sidebar:
    st.subheader("Parámetros de traducción")

    try:
        os.mkdir("temp")
    except:
        pass

    in_lang = st.selectbox(
        "Seleccione el idioma de entrada",
        ("Inglés", "Español", "Bengalí", "Coreano", "Mandarín", "Japonés"),
    )

    if in_lang == "Inglés":
        input_language = "en"
    elif in_lang == "Español":
        input_language = "es"
    elif in_lang == "Bengalí":
        input_language = "bn"
    elif in_lang == "Coreano":
        input_language = "ko"
    elif in_lang == "Mandarín":
        input_language = "zh-cn"
    elif in_lang == "Japonés":
        input_language = "ja"

    out_lang = st.selectbox(
        "Seleccione el idioma de salida",
        ("Inglés", "Español", "Bengalí", "Coreano", "Mandarín", "Japonés"),
    )

    if out_lang == "Inglés":
        output_language = "en"
    elif out_lang == "Español":
        output_language = "es"
    elif out_lang == "Bengalí":
        output_language = "bn"
    elif out_lang == "Coreano":
        output_language = "ko"
    elif out_lang == "Mandarín":
        output_language = "zh-cn"
    elif out_lang == "Japonés":
        output_language = "ja"

    english_accent = st.selectbox(
        "Seleccione el acento",
        (
            "Default",
            "India",
            "United Kingdom",
            "United States",
            "Canada",
            "Australia",
            "Ireland",
            "South Africa",
        ),
    )

    if english_accent == "Default":
        tld = "com"
    elif english_accent == "India":
        tld = "co.in"
    elif english_accent == "United Kingdom":
        tld = "co.uk"
    elif english_accent == "United States":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Ireland":
        tld = "ie"
    elif english_accent == "South Africa":
        tld = "co.za"

    display_output_text = st.checkbox("Mostrar texto traducido")


# --- Botón principal ---
if st.button("Convertir texto a audio"):
    if text.strip() == "":
        st.warning("Por favor, carga una imagen o toma una foto para reconocer texto primero.")
    else:
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()

        st.audio(audio_bytes, format="audio/mp3")

        if display_output_text:
            st.markdown("### Texto traducido:")
            st.write(output_text)
