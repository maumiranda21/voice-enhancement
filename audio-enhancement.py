import streamlit as st
from pydub import AudioSegment
import io, zipfile
from utils import mejorar_audio

AudioSegment.converter = "/usr/bin/ffmpeg"

st.title("🎙️ Mejora de Audios de WhatsApp a Calidad de Estudio")
st.write("Sube uno o varios archivos de audio y conviértelos automáticamente a mejor calidad.")

archivos = st.file_uploader("Selecciona los audios", type=["mp3", "wav", "ogg", "opus", "m4a"], accept_multiple_files=True)

if archivos:
    memoria_zip = io.BytesIO()

    with zipfile.ZipFile(memoria_zip, mode="w") as zf:
        for archivo in archivos:
            try:
                formato = archivo.name.split(".")[-1]
                mejorado = mejorar_audio(archivo, formato)

                salida = io.BytesIO()
                mejorado.export(salida, format="mp3")
                salida.seek(0)

                # Guardar con el mismo nombre original pero en mp3
                nuevo_nombre = ".".join(archivo.name.split(".")[:-1]) + ".mp3"
                zf.writestr(nuevo_nombre, salida.read())

            except Exception as e:
                st.error(f"Error procesando {archivo.name}: {e}")

    memoria_zip.seek(0)
    st.download_button("⬇️ Descargar audios mejorados", memoria_zip, "audios_mejorados.zip", "application/zip")
