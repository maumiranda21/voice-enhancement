import streamlit as st
from pydub import AudioSegment
import io
import os

# Ruta de ffmpeg en Streamlit Cloud
AudioSegment.converter = "/usr/bin/ffmpeg"

st.set_page_config(page_title="Mejora de Audios WhatsApp", layout="centered")
st.title("🎙️ Mejora de Audios a Calidad de Estudio")

st.write("Sube varios audios y los convertiremos automáticamente a calidad mejorada.")

# Función para mejorar audio usando ffmpeg
def mejorar_audio(file_bytes, formato_original):
    # Cargar audio original
    audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=formato_original)
    
    # Exportar a WAV con parámetros de calidad usando ffmpeg
    temp_wav = io.BytesIO()
    audio.export(temp_wav, format="wav", parameters=["-ar", "44100", "-ac", "2"])
    temp_wav.seek(0)
    
    # Volver a cargar y normalizar
    audio_mejorado = AudioSegment.from_wav(temp_wav).normalize()
    
    # Exportar a MP3 de alta calidad
    output_bytes = io.BytesIO()
    audio_mejorado.export(output_bytes, format="mp3", bitrate="192k")
    return output_bytes.getvalue()

# Subida múltiple
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
