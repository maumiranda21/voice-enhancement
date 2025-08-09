import streamlit as st
from pydub import AudioSegment, effects
import tempfile
import os
import librosa
import soundfile as sf
import noisereduce as nr
import numpy as np
from scipy.signal import sosfilt, butter

st.set_page_config(page_title="Mejorador de Voz (Prototype)", page_icon="🎙️", layout="centered")
st.title("🎙️ Mejora tus notas de voz — prototipo")
st.write("Sube una nota de voz (ej. .opus de WhatsApp) y obtén una versión más limpia y con mayor claridad.")

# Parámetros de usuario
st.sidebar.header("Ajustes de procesamiento")
agresividad = st.sidebar.slider("Reducción de ruido (agresividad)", 0.0, 1.0, 0.5, 0.05,
                                 help="0 = leve, 1 = máximo (más artefactos posibles)")
hp_cut = st.sidebar.slider("Corte High-pass (Hz)", 50, 300, 80, 5,
                           help="Elimina graves muy bajos (rumble). Útil para voz.")
normalize_db = st.sidebar.slider("Normalizar a (dBFS target)", -24, -3, -14, 1,
                                 help="Nivel objetivo post-procesado (más alto = sonido más cercano a 'profesional').")

uploaded = st.file_uploader("Sube un archivo de audio", type=["opus","mp3","wav","flac","m4a","ogg"])

def highpass_filter(y, sr, cutoff_hz):
    # Butterworth highpass (order 4) usando SOS para estabilidad
    sos = butter(4, cutoff_hz, btype='highpass', fs=sr, output='sos')
    filtered = sosfilt(sos, y)
    return filtered

def dbfs_to_amp_factor(target_dbfs, y):
    # Convertir dBFS objetivo a factor de amplificación (basado en RMS)
    # Normalizaremos por RMS para no subir a picos máximos
    rms = np.sqrt(np.mean(y**2)) + 1e-9
    current_dbfs = 20 * np.log10(rms)
    diff_db = target_dbfs - current_dbfs
    factor = 10 ** (diff_db / 20.0)
    return factor

if uploaded:
    # Guardar archivo subido en temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded.name.split(".")[-1]) as temp_in:
        temp_in.write(uploaded.read())
        ruta_entrada = temp_in.name

    st.info(f"Cargando y convirtiendo: {uploaded.name}")
    try:
        # 1) Convertir a WAV intermedio usando pydub (ffmpeg debe estar instalado)
        wav_temp = ruta_entrada + ".wav"
        audio = AudioSegment.from_file(ruta_entrada)
        audio.export(wav_temp, format="wav")

        # 2) Cargar WAV con librosa (float32)
        y, sr = librosa.load(wav_temp, sr=None)  # sr=None preserva sample rate original

        st.write(f"Sample rate: {sr} Hz — Duración: {len(y)/sr:.1f} s")

        # 3) Aplicar high-pass para limpieza de graves
        if hp_cut > 20:
            y = highpass_filter(y, sr, hp_cut)

        # 4) Estimar ruido: tomamos la sección inicial como 'ruido' si la hay (0-0.5s)
        noise_sample_duration = min(0.5, len(y)/sr)
        noise_sample = y[: int(noise_sample_duration * sr)]

        # 5) Reducción de ruido (noisereduce)
        st.write("Aplicando reducción de ruido...")
        y_denoised = nr.reduce_noise(y=y, sr=sr, y_noise=noise_sample,
                                     prop_decrease=agresividad, verbose=False)

        # 6) Normalización RMS simple al nivel objetivo en dBFS
        st.write("Normalizando nivel...")
        factor = dbfs_to_amp_factor(normalize_db, y_denoised)
        y_normalized = y_denoised * factor
        # Evitar clipping: si hay picos > 1.0 los reescalamos
        peak = np.max(np.abs(y_normalized)) + 1e-9
        if peak > 0.999:
            y_normalized = y_normalized / peak * 0.999

        # 7) Guardar WAV resultante
        salida_wav = os.path.join(tempfile.gettempdir(), os.path.splitext(uploaded.name)[0] + "_mejorado.wav")
        sf.write(salida_wav, y_normalized.astype(np.float32), sr, subtype='PCM_24')

        # 8) Ofrecer descarga
        with open(salida_wav, "rb") as f:
            st.download_button(
                label=f"⬇️ Descargar {os.path.basename(salida_wav)}",
                data=f,
                file_name=os.path.basename(salida_wav),
                mime="audio/wav"
            )

        st.success("✅ Procesamiento completado.")
    except Exception as e:
        st.error(f"❌ Error durante el procesamiento: {e}")
    finally:
        # Limpieza de temporales
        try:
            if os.path.exists(ruta_entrada):
                os.remove(ruta_entrada)
            if 'wav_temp' in locals() and os.path.exists(wav_temp):
                os.remove(wav_temp)
            # dejamos salida_wav para que el usuario pueda descargarla; si quieres limpiarla aquí, descomenta:
            # if 'salida_wav' in locals() and os.path.exists(salida_wav):
            #     os.remove(salida_wav)
        except Exception:
            pass

st.markdown("---")
st.caption("Prototipo: para resultados 'calidad estudio' se recomiendan modelos avanzados (Demucs, RNNoise o servicios especializados).")
