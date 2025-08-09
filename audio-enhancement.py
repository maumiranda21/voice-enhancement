import streamlit as st
from pydub import AudioSegment
import io
import os

# Si estás en Streamlit Cloud, especifica la ruta de ffmpeg si es necesario
AudioSegment.converter = "/usr/bin/ffmpeg"

st.set_page_config(page_title="Mejora de Audios WhatsApp", layout="centered")
st.title("🎙️ Mejora de Audios a Calidad de Estudio")

st.write("Sube varios audios y los convertiremos automáticamente a calidad mejorada.")

def mejorar_audio(file_bytes, formato_original):
    try:
        # Cargar audio original
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=formato_original)

        # Forzar parámetros de calidad
        audio_mejorado = (
            audio.set_frame_rate(44100)  # Frecuencia
                 .set_channels(2)         # Estéreo
                 .normalize()             # Normalizar volumen
        )

        # Exportar como MP3 de alta calidad
        output_bytes = io.BytesIO()
        audio_mejorado.export(output_bytes, format="mp3", bitrate="192k")
        return output_bytes.getvalue()

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
        return None

# Subida múltiple
archivos = st.file_uploader("Selecciona tus audios", type=["mp3", "wav", "ogg", "m4a"], accept_multiple_files=True)

if archivos:
    for archivo in archivos:
        nombre_original, extension = os.path.splitext(archivo.name)
        formato = extension.replace(".", "").lower()

        st.write(f"Procesando: **{archivo.name}** ...")
        mejorado = mejorar_audio(archivo.read(), formato)

        if mejorado:
            st.download_button(
                label=f"⬇️ Descargar {nombre_original}_mejorado.mp3",
                data=mejorado,
                file_name=f"{nombre_original}_mejorado.mp3",
                mime="audio/mpeg"
            )
