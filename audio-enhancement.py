# streamlit_app.py
import streamlit as st
import tempfile
import os
import subprocess
import io
import zipfile
import time

# Optional heavy libs imported lazily (faster cold-start if not installed)
try:
    import torch
    from demucs.apply import apply_model
    from demucs.pretrained import get_model
    demucs_available = True
except Exception:
    demucs_available = False

import soundfile as sf
import numpy as np
import noisereduce as nr

st.set_page_config(page_title="Mejorador IA — Máxima Calidad", layout="wide")
st.title("🎙️ Mejorador de Voz con IA (Demucs) + DSP pro")

st.sidebar.header("Ajustes")
mode = st.sidebar.selectbox("Modo", ["Demucs (IA) + DSP (recomendado)", "Solo DSP (fallback)"])
output_format = st.sidebar.selectbox("Salida", ["mp3", "wav"])
bitrate = st.sidebar.selectbox("Bitrate (mp3)", ["192k", "256k", "320k"])
add_subtle_reverb = st.sidebar.checkbox("Añadir reverberación sutil", value=False)
use_external_endpoint = st.sidebar.checkbox("Enviar a endpoint externo (si tienes uno)", value=False)
api_url = st.sidebar.text_input("Endpoint URL (si aplica)")
api_key = st.sidebar.text_input("API Key (si aplica)", type="password")

uploads = st.file_uploader("Sube uno o varios audios (.wav .mp3 .ogg .opus .m4a)", accept_multiple_files=True, type=["wav","mp3","ogg","opus","m4a"])

# ---------- Helpers ----------
def run_ffmpeg_filters(in_path, out_path, out_format="mp3", bitrate="192k", reverb=False):
    # Construct FFmpeg filter chain
    filter_chain = [
        "highpass=f=80",  # cut rumble
        "equalizer=f=3000:width_type=h:width=200:g=3",  # presence boost
        "acompressor=threshold=-18dB:ratio=4:attack=10:release=200",  # compression
        "loudnorm=I=-14:TP=-1.5:LRA=11"  # LUFS normalization
    ]
    if reverb:
        # very subtle plate reverb via a convolution or simple aecho; here a light aecho
        filter_chain.append("aecho=0.8:0.9:1000:0.02")
    af = ",".join(filter_chain)

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", in_path, "-af", af, "-ar", "48000", "-ac", "2"]
    if out_format == "mp3":
        cmd += ["-b:a", bitrate, out_path]
    else:
        cmd += ["-sample_fmt", "s32", out_path]
    subprocess.run(cmd, check=True)

def demucs_enhance(input_path, output_path, model_name="tasnet_demucs", device="cpu"):
    # We'll try to use a pretrained demucs model; user can change model_name.
    # This function expects 'get_model' and 'apply_model' from demucs package.
    model = get_model(name="htdemucs") if demucs_available else None
    # apply_model writes output files; we return the vocal (or first source) path
    # For speech enhancement we can use the "demucs" model and take "vocals" or "drums" depending
    out_dir = os.path.dirname(output_path)
    apply_model(model, input_path, out_dir, device=device, progress=True, split=True)
    # Heuristic: find processed wav matching input basename and "vocals"
    basename = os.path.splitext(os.path.basename(input_path))[0]
    # Demucs output structure: out_dir/<model-name>/<basename>/vocals.wav (may vary)
    # Search for any matching wav in out_dir
    for root, dirs, files in os.walk(out_dir):
        for f in files:
            if f.endswith(".wav") and basename in f:
                # return first candidate
                return os.path.join(root, f)
    return None

def reduce_noise_numpy(y, sr):
    # y: numpy array float32 mono or stereo
    if y.ndim == 1:
        noise_sample = y[:int(min(len(y), sr*0.5))]
        reduced = nr.reduce_noise(y=y, sr=sr, y_noise=noise_sample, prop_decrease=1.0)
        return reduced
    else:
        # stereo: process channels separately
        ch0 = nr.reduce_noise(y=y[:,0], sr=sr, y_noise=y[:int(min(len(y), sr*0.5)),0], prop_decrease=1.0)
        ch1 = nr.reduce_noise(y=y[:,1], sr=sr, y_noise=y[:int(min(len(y), sr*0.5)),1], prop_decrease=1.0)
        return np.vstack((ch0,ch1)).T

# ---------- Main processing ----------
if uploads:
    st.info("Procesando... esto puede tardar (especialmente si usa Demucs sin GPU).")
    tmpdir = tempfile.mkdtemp(prefix="enh_")
    out_files = []
    total = len(uploads)
    progress = st.progress(0)
    device = "cuda" if (demucs_available and torch.cuda.is_available()) else "cpu"

    for i, up in enumerate(uploads, start=1):
        st.write(f"Procesando {up.name} ({i}/{total})")
        start = time.time()
        in_path = os.path.join(tmpdir, f"in_{i}_" + up.name.replace(" ", "_"))
        with open(in_path, "wb") as f:
            f.write(up.read())

        processed_path = None

        # 1) Try Demucs if requested and available
        if mode.startswith("Demucs") and demucs_available:
            st.write("Intentando Demucs (IA)... (puede tardar)")
            try:
                demucs_out = demucs_enhance(in_path, tmpdir, device=device)
                if demucs_out and os.path.exists(demucs_out):
                    # demucs_out should be a clean vocal wav; then apply ffmpeg filters to polish
                    tmp_polished = os.path.join(tmpdir, os.path.splitext(up.name)[0] + "_polished.wav")
                    run_ffmpeg_filters(demucs_out, tmp_polished, out_format="wav", reverb=add_subtle_reverb)
                    processed_path = tmp_polished
                else:
                    st.warning("Demucs no generó salida válida, usando fallback DSP.")
            except Exception as e:
                st.warning(f"Demucs falló: {e}. Usando fallback DSP.")
        # 2) Fallback DSP pipeline: noisereduce + ffmpeg filters
        if processed_path is None:
            try:
                # read with soundfile
                data, sr = sf.read(in_path, dtype="float32")
                # Apply NR
                denoised = reduce_noise_numpy(data, sr)
                # Save temporary WAV
                tmp_nr = os.path.join(tmpdir, os.path.splitext(up.name)[0] + "_denoised.wav")
                sf.write(tmp_nr, denoised, sr, format="WAV")
                # FFmpeg polishing
                tmp_polished = os.path.join(tmpdir, os.path.splitext(up.name)[0] + "_polished.wav")
                try:
                    run_ffmpeg_filters(tmp_nr, tmp_polished, out_format="wav", reverb=add_subtle_reverb)
                    processed_path = tmp_polished
                except Exception as e:
                    st.error(f"FFmpeg polishing falló: {e}. Intentando exportar denoised sin filtros.")
                    processed_path = tmp_nr
            except Exception as e:
                st.error(f"Error en pipeline DSP para {up.name}: {e}")
                continue

        # 3) Convert to requested output (mp3/wav)
        final_name = os.path.splitext(up.name)[0] + "_mejorado." + output_format
        final_path = os.path.join(tmpdir, final_name)
        try:
            if output_format == "mp3":
                # use ffmpeg to encode mp3 at chosen bitrate
                cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error","-i", processed_path, "-b:a", bitrate, final_path]
                subprocess.run(cmd, check=True)
            else:
                # wav already fine: convert sample format
                cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error","-i", processed_path, "-sample_fmt","s32", final_path]
                subprocess.run(cmd, check=True)
            out_files.append((final_name, final_path))
            st.success(f"Procesado {up.name} en {time.time()-start:.1f}s")
        except Exception as e:
            st.error(f"Error finalizando archivo {up.name}: {e}")

        progress.progress(int(i/total*100))

    # package ZIP
    if out_files:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, path in out_files:
                zf.write(path, arcname=name)
        zip_buf.seek(0)
        st.download_button("📥 Descargar ZIP con audios mejorados", zip_buf, "audios_mejorados.zip", "application/zip")
    else:
        st.warning("No se generaron archivos de salida.")
