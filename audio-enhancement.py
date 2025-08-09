import streamlit as st
from pydub import AudioSegment
import io
import numpy as np
from scipy.signal import resample
import tempfile
import os

# Función para mejorar audio sin usar audioop
def mejorar_audio_con_numpy(audio_bytes, formato):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{formato}") as temp_in:
        temp_in.write(audio_bytes)
        temp_in_path = temp_in.name

    # Abrir con pydub
    audio = AudioSegment.from_file(temp_in_path, format=formato)

    # Convertir a numpy array
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)

    # Normalizar a -1.0 / 1.0
    samples /= np.iinfo(audio.array_type).max

    # Re-muestrear a 44.1 kHz (sin audioop)
    target_rate = 44100
    num_samples = int(len(samples) * target_rate / audio.frame_rate)
    samples_resampled = resample(samples, num_samples)

    # Volver a escalar y convertir
    samples_resampled = np.int16(samples_resampled / np.max(np.abs(samples_resampled)) * 32767)

    # Crear nuevo AudioSegment desde numpy
    audio_mejorado = AudioSegment(
        samples_resampled.tobytes(),
        frame_rate=target_rate,
        sample_width=2,
        channels=audio.channels
    )

    os.remove(temp_in_path)  # Limpiar archivo temporal
    return audio_mejorado

# Interfaz Streamlit
st.title("🎙️ Mejora de Audios de WhatsApp")
st.write("Sube tus audios y conviértelos automáticamente a calidad cercana a estudio.")

archivos = st.file_uploader("Selecciona uno o varios archivos de audio", type=["mp3", "wav", "ogg", "opus", "m4a"], accept_multiple_files=True)

if archivos:
    for archivo in archivos:
        formato = archivo.name.split(".")[-1].lower()
        try:
            mejorado = mejorar_audio_con_numpy(archivo.read(), formato)

            # Guardar con mismo nombre pero .wav
            nombre_salida = os.path.splitext(archivo.name)[0] + "_mejorado.wav"
            buffer_salida = io.BytesIO()
            mejorado.export(buffer_salida, format="wav")
            buffer_salida.seek(0)

            st.download_button(
                label=f"⬇️ Descargar {nombre_salida}",
                data=buffer_salida,
                file_name=nombre_salida,
                mime="audio/wav"
            )
        except Exception as e:
            st.error(f"Error procesando {archivo.name}: {e}")
