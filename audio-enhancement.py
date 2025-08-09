
import streamlit as st
import tempfile
import os
import zipfile
from pydub import AudioSegment
import noisereduce as nr
import numpy as np
import io

st.set_page_config(page_title="Mejora de Audios WhatsApp", page_icon="🎙️", layout="centered")
st.title("🎙️ Mejora de Audios de WhatsApp a Calidad de Estudio")
st.write("Sube varios audios y los mejoraremos automáticamente.")

uploaded_files = st.file_uploader("Sube tus audios (.opus, .mp3, .wav)", type=["opus", "mp3", "wav"], accept_multiple_files=True)

def mejorar_audio(audio_bytes, formato_salida="mp3"):
    # Guardar en archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".input") as tmp_in:
        tmp_in.write(audio_bytes)
        tmp_in_path = tmp_in.name
    
    # Cargar audio
    audio = AudioSegment.from_file(tmp_in_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    
    # Convertir a numpy array
    audio_np = np.array(audio.get_array_of_samples()).astype(np.float32)
    audio_np = audio_np / np.max(np.abs(audio_np))
    
    # Reducir ruido
    reduced_noise = nr.reduce_noise(y=audio_np, sr=16000)
    reduced_noise = (reduced_noise * 32767).astype(np.int16)
    
    # Crear AudioSegment final
    audio_final = AudioSegment(
        reduced_noise.tobytes(), 
        frame_rate=16000,
        sample_width=2, 
        channels=1
    )
    
    # Exportar a bytes
    output_bytes = io.BytesIO()
    audio_final.export(output_bytes, format=formato_salida)
    output_bytes.seek(0)
    return output_bytes

if uploaded_files:
    st.info("Procesando audios...")
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "audios_mejorados.zip")
    
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in uploaded_files:
            nombre_sin_ext = os.path.splitext(file.name)[0]
            mejorado = mejorar_audio(file.read(), "mp3")
            output_filename = f"{nombre_sin_ext}.mp3"
            temp_out_path = os.path.join(temp_dir, output_filename)
            with open(temp_out_path, "wb") as f:
                f.write(mejorado.read())
            zipf.write(temp_out_path, arcname=output_filename)
    
    with open(zip_path, "rb") as f:
        st.download_button("📥 Descargar todos los audios mejorados (ZIP)", f, file_name="audios_mejorados.zip")
