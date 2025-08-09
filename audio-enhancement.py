# streamlit_app.py
import streamlit as st
import tempfile, os, io, zipfile, subprocess, time
from audio_processor import process_file_to_polished
from pathlib import Path

st.set_page_config(page_title="Mejora Agresiva - Voz Locutor", layout="wide")
st.title("🎙️ Mejora Agresiva — Voz estilo locutor")

st.markdown("""
Sube varios audios (wav/mp3/ogg/opus/m4a).  
Pipeline: **denoise (noisereduce)** → **polish FFmpeg (HP/LP/EQ/Comp/afftdn/loudnorm)** → export WAV/MP3.  
Si algún filtro FFmpeg falla, se aplica un fallback compatible.
""")

st.sidebar.header("Ajustes")
output_format = st.sidebar.selectbox("Formato final", ["wav", "mp3"])
mp3_bitrate = st.sidebar.selectbox("Bitrate mp3", ["192k", "256k", "320k"])
add_reverb = st.sidebar.checkbox("Añadir reverb sutil al final (no recomendado para locutor)", value=False)
aggressive_mode = st.sidebar.checkbox("Modo aún más agresivo (más EQ/comp)", value=True)

uploads = st.file_uploader("Sube uno o varios audios", accept_multiple_files=True,
                           type=["wav", "mp3", "ogg", "opus", "m4a"])

if uploads:
    tmproot = tempfile.mkdtemp(prefix="enh_")
    out_files = []
    total = len(uploads)
    progress = st.progress(0)
    status_box = st.empty()

    for i, up in enumerate(uploads, start=1):
        status_box.text(f"Procesando {up.name} ({i}/{total})")
        in_path = os.path.join(tmproot, f"input_{i}_" + Path(up.name).name)
        with open(in_path, "wb") as f:
            f.write(up.read())

        try:
            # process_file_to_polished returns path to final polished WAV (high quality)
            polished_wav = process_file_to_polished(
                in_path,
                tmpdir=tmproot,
                aggressive=aggressive_mode,
                add_reverb=add_reverb,
                st_log=lambda s: status_box.text(s)
            )
            if not polished_wav or not os.path.exists(polished_wav):
                st.error(f"No se generó salida para {up.name}")
                continue

            # Convert/export to requested format
            base = Path(up.name).stem
            if output_format == "wav":
                final_path = os.path.join(tmproot, f"{base}_mejorado.wav")
                # Ensure sample format (48k, s32)
                cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                       "-i", polished_wav, "-sample_fmt", "s32", "-ar", "48000", final_path]
                subprocess.run(cmd, check=True)
            else:
                final_path = os.path.join(tmproot, f"{base}_mejorado.mp3")
                cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                       "-i", polished_wav, "-b:a", mp3_bitrate, final_path]
                subprocess.run(cmd, check=True)

            out_files.append((os.path.basename(final_path), final_path))
            status_box.text(f"✅ {up.name} procesado")
        except Exception as e:
            st.error(f"Error procesando {up.name}: {e}")
        progress.progress(int(i/total*100))

    # Empaquetar y ofrecer descarga
    if out_files:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, path in out_files:
                zf.write(path, arcname=name)
        zip_buf.seek(0)
        st.success("Procesado completado ✅")
        st.download_button("📥 Descargar ZIP con audios mejorados", zip_buf, "audios_mejorados.zip", mime="application/zip")
    else:
        st.warning("No se generaron archivos de salida.")
