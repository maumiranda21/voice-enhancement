import streamlit as st
import soundfile as sf
import numpy as np
from scipy.signal import resample
import io
import os
import tempfile

def mejorar_audio_numpy(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False) as temp_in:
        temp_in.write(audio_bytes)
        temp_in_path = temp_in.name

    # Leer audio original
    data, samplerate = sf.read(temp_in_path, dtype="float32")

    # Normalizar amplitud
    data = data / np.max(np.abs(data))

    # Convertir a estéreo si es mono
    if len(data.shape) == 1:
        data = np.stack((data, data), axis=1)

    # Re-muestrear a 44.1 kHz
    target_rate = 44100
    num_samples = int(len(data) * target_rate / samplerate)
    data_resampled = resample(data, num_samples)

    # Aumentar volumen un poco
    data_resampled = np.clip(data_resampled * 1.2, -1.0, 1.0)

    os.remove(temp_in_path)
    return data_resampled, target_rate

# Interfaz Streamlit
st.title("🎙️ Mejora de Audios de WhatsApp")
st.write("Sube tus audios y conviértelos a mejor calidad.")

archivos = st.file_uploader(
    "Selecciona uno o varios archivos de audio",
    type=["mp3", "wav", "ogg", "opus", "m4a"],
    accept_multiple_files=True
)

if archivos:
    for archivo in archivos:
        try:
            mejorado, rate = mejorar_audio_numpy(archivo.read())

            # Guardar en buffer como WAV
            buffer_salida = io.BytesIO()
            sf.write(buffer_salida, mejorado, rate, format='WAV')
            buffer_salida.seek(0)

            nombre_salida = os.path.splitext(archivo.name)[0] + "_mejorado.wav"

            st.download_button(
                label=f"⬇️ Descargar {nombre_salida}",
                data=buffer_salida,
                file_name=nombre_salida,
                mime="audio/wav"
            )
        except Exception as e:
            st.error(f"Error procesando {archivo.name}: {e}")
