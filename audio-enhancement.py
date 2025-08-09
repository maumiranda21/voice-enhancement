import streamlit as st
from pydub import AudioSegment
import io
import os

# Asegurar que Pydub use ffmpeg en Streamlit Cloud
AudioSegment.converter = "/usr/bin/ffmpeg"

st.set_page_config(page_title="Mejora de Audios WhatsApp", layout="centered")
st.title("🎙️ Mejora de Audios a Calidad de Estudio")

st.write("Sube varios audios (por ejemplo, grabaciones de WhatsApp) y los convertiremos automáticamente a calidad mejorada.")

# Función para mejorar audio
def mejorar_audio(file_bytes, formato_original):
    audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=formato_original)
    audio = audio.set_frame_rate(44100) \
                 .set_channels(2) \
                 .normalize()
    output_bytes = io.BytesIO()
    audio.export(output_bytes, format="mp3", bitrate="192k")
    return output_bytes.getvalue()

# Subida de múltiples archivos
archivos = st.file_uploader("Selecciona tus audios", type=["mp3", "wav", "ogg", "m4a"], accept_multiple_files=True)

if archivos:
    for archivo in archivos:
        nombre_original, extension = os.path.splitext(archivo.name)
        formato = extension.replace(".", "").lower()

        st.write(f"Procesando: **{archivo.name}** ...")

        mejorado = mejorar_audio(archivo.read(), formato)
        
        st.download_button(
            label=f"⬇️ Descargar {nombre_original}_mejorado.mp3",
            data=mejorado,
            file_name=f"{nombre_original}_mejorado.mp3",
            mime="audio/mpeg"
        )
