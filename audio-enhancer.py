import streamlit as st
import os
import librosa
import soundfile as sf
import numpy as np
from deepfilternet import enhance, init_df
import zipfile
import io
from datetime import datetime
import matplotlib.pyplot as plt

# Configuración inicial
st.set_page_config(page_title="Mejorador de Audio con IA", layout="wide")
st.title("Mejorador de Audio con IA")
st.markdown("Sube tus archivos de audio (MP3, WAV, OGG, FLAC, M4A) para mejorar su calidad automáticamente.")

# Inicializar modelo DeepFilterNet
@st.cache_resource
def load_model():
    model, df_state, _ = init_df()
    return model, df_state

model, df_state = load_model()

# Directorio temporal para archivos procesados
if not os.path.exists("temp"):
    os.makedirs("temp")

# Función para procesar un archivo de audio
def process_audio(file, sr=48000):
    try:
        # Cargar audio
        audio, sr_orig = librosa.load(file, sr=None)
        # Convertir a la frecuencia de muestreo requerida por DeepFilterNet
        if sr_orig != sr:
            audio = librosa.resample(audio, orig_sr=sr_orig, target_sr=sr)
        # Mejorar audio
        enhanced_audio = enhance(model, df_state, audio)
        # Guardar archivo mejorado
        output_path = f"temp/enhanced_{file.name}"
        sf.write(output_path, enhanced_audio, sr)
        return output_path, audio, enhanced_audio, sr
    except Exception as e:
        st.error(f"Error procesando {file.name}: {str(e)}")
        return None, None, None, None

# Función para generar visualización de forma de onda
def plot_waveform(audio, sr, title):
    fig, ax = plt.subplots(figsize=(10, 2))
    time = np.linspace(0, len(audio) / sr, num=len(audio))
    ax.plot(time, audio, color="#1f77b4")
    ax.set_title(title)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Amplitud")
    plt.tight_layout()
    return fig

# Interfaz de usuario
uploaded_files = st.file_uploader("Sube tus archivos de audio", type=["mp3", "wav", "ogg", "flac", "m4a"], accept_multiple_files=True)

if uploaded_files:
    st.write("Archivos subidos:")
    processed_files = []
    
    # Procesar cada archivo
    for file in uploaded_files:
        with st.spinner(f"Procesando {file.name}..."):
            output_path, original_audio, enhanced_audio, sr = process_audio(file)
            if output_path:
                processed_files.append((file.name, output_path, original_audio, enhanced_audio, sr))
    
    # Mostrar resultados
    for name, output_path, original_audio, enhanced_audio, sr in processed_files:
        st.subheader(f"Archivo: {name}")
        col1, col2 = st.columns(2)
        
        # Audio original
        with col1:
            st.write("Audio Original")
            st.audio(name, format=name.split('.')[-1])
            if original_audio is not None:
                fig = plot_waveform(original_audio, sr, "Forma de Onda Original")
                st.pyplot(fig)
                plt.close(fig)
        
        # Audio mejorado
        with col2:
            st.write("Audio Mejorado")
            st.audio(output_path, format=name.split('.')[-1])
            if enhanced_audio is not None:
                fig = plot_waveform(enhanced_audio, sr, "Forma de Onda Mejorada")
                st.pyplot(fig)
                plt.close(fig)
            st.download_button(
                label="Descargar Audio Mejorado",
                data=open(output_path, "rb").read(),
                file_name=f"enhanced_{name}",
                mime=f"audio/{name.split('.')[-1]}"
            )
    
    # Botón para descargar todos los archivos mejorados como ZIP
    if len(processed_files) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for name, output_path, _, _, _ in processed_files:
                zip_file.write(output_path, f"enhanced_{name}")
        zip_buffer.seek(0)
        st.download_button(
            label="Descargar Todos los Audios Mejorados (ZIP)",
            data=zip_buffer,
            file_name=f"enhanced_audios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )

# Limpiar directorio temporal
if st.button("Limpiar Archivos Temporales"):
    for file in os.listdir("temp"):
        os.remove(os.path.join("temp", file))
    st.success("Archivos temporales eliminados.")
