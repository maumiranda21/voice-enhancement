import streamlit as st
import tempfile
import subprocess
import os
import zipfile
import io
import time
import requests

st.set_page_config(page_title="Mejorador de Voz — Máxima Calidad", layout="wide")
st.title("🎙️ Mejorador de Voz — Modo: Máxima Calidad")

st.markdown(
    """
    Sube varios audios (WhatsApp, .opus, .ogg, .wav, .mp3).  
    El pipeline aplica: reducción de ruido, high-pass, EQ para presencia vocal, compresión y normalización LUFS.  
    - **Modo local (FFmpeg)**: usa filtros FFmpeg (rápido, requiere ffmpeg instalado en el host).  
    - **Modo remoto (IA)**: opcionalmente envía archivos a un endpoint de inferencia si tienes un servicio más avanzado (requiere API key).
    """
)

st.sidebar.header("Ajustes")
mode = st.sidebar.selectbox("Modo de mejora", ["FFmpeg - Máxima Calidad (recomendado)", "Usar endpoint externo (IA)"])
output_format = st.sidebar.selectbox("Formato de salida", ["mp3", "wav"])
bitrate = st.sidebar.selectbox("Bitrate (solo mp3)", ["192k", "256k", "320k"])

# Opcional: endpoint externo (si quieres usar HuggingFace / tu servidor)
st.sidebar.markdown("### Endpoint externo (opcional)")
api_url = st.sidebar.text_input("URL del endpoint (POST audio)", "")
api_key = st.sidebar.text_input("API Key (si aplica)", type="password")

uploads = st.file_uploader(
    "Sube uno o varios audios",
    type=["mp3", "wav", "ogg", "m4a", "opus"],
    accept_multiple_files=True
)

def run_ffmpeg_enhance(input_path, output_path, output_format="mp3", bitrate="192k", debug=False):
    """
    Pipeline FFmpeg (filtros avanzados):
      - highpass para quitar rumble
      - equalizer para realce de presencia (alrededor 2.5-4 kHz)
      - acompressor para control dinámico
      - loudnorm para normalización LUFS
    """
    # Cadena de filtros; puedes ajustar gains y parámetros según tus pruebas.
    filter_chain = (
        "highpass=f=80, "  # elimina graves muy bajos
        "equalizer=f=3000:width_type=h:width=200:g=3, "  # realce en presencia vocal
        "acompressor=threshold=-18dB:ratio=4:attack=10:release=200, "  # compresión vocal
        "dynaudnorm=g=5, "  # normalización dinámica (si disponible)
        "loudnorm=I=-14:TP=-1.5:LRA=11"  # normalización a -14 LUFS
    )

    # Comando base (forzamos sample rate y canales)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_path,
        "-af", filter_chain,
        "-ar", "48000",  # sample rate
        "-ac", "2",      # canales
    ]

    if output_format == "mp3":
        cmd += ["-b:a", bitrate, output_path]
    else:
        # WAV
        cmd += ["-sample_fmt", "s32", output_path]

    if debug:
        st.write("FFmpeg cmd:", " ".join(cmd))

    # Ejecutar y capturar errores
    try:
        subprocess.run(cmd, check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)

def call_external_endpoint(api_url, api_key, file_bytes, filename):
    """
    Envía el archivo al endpoint externo. El endpoint debe:
    - recibir multipart/form-data con campo 'file'
    - devolver el audio mejorado en el body (application/octet-stream) o JSON con URL.
    Ajusta según tu provider.
    """
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    files = {"file": (filename, file_bytes)}
    try:
        resp = requests.post(api_url, files=files, headers=headers, timeout=120)
        resp.raise_for_status()
        # Suponemos que la respuesta es el archivo binario (si devuelve JSON, adaptarlo)
        return True, resp.content, None
    except Exception as e:
        return False, None, str(e)

if uploads:
    st.info(f"Procesando {len(uploads)} archivos... esto puede tardar dependiendo del tamaño y del modo elegido.")
    progress = st.progress(0)
    timestamp = int(time.time())
    tmpdir = tempfile.mkdtemp(prefix=f"voice_enh_{timestamp}_")

    output_files = []
    total = len(uploads)
    for idx, up in enumerate(uploads, start=1):
        st.write(f"🔁 Procesando **{up.name}** ({idx}/{total})")
        try:
            # Guardar input temporal
            suffix = "." + up.name.split(".")[-1]
            tmp_in = os.path.join(tmpdir, f"in_{idx}{suffix}")
            with open(tmp_in, "wb") as f:
                f.write(up.read())

            if mode.startswith("FFmpeg"):
                out_basename = os.path.splitext(up.name)[0] + f"_mejorado.{output_format}"
                tmp_out = os.path.join(tmpdir, out_basename)

                ok, err = run_ffmpeg_enhance(tmp_in, tmp_out, output_format, bitrate)
                if not ok:
                    st.error(f"FFmpeg falló para {up.name}: {err}")
                    # intento fallback: procesar sin dynaudnorm / sin loudnorm
                    fallback_chain = "highpass=f=80, equalizer=f=3000:width_type=h:width=200:g=2, acompressor=threshold=-18dB:ratio=3"
                    cmd_fb = [
                        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                        "-i", tmp_in, "-af", fallback_chain, "-ar", "48000", "-ac", "2",
                        "-b:a", bitrate if output_format=="mp3" else None, tmp_out
                    ]
                    # limpiar cmd_fb None
                    cmd_fb = [c for c in cmd_fb if c is not None]
                    try:
                        subprocess.run(cmd_fb, check=True)
                        st.warning(f"Fallback aplicado para {up.name}.")
                    except Exception as e:
                        st.error(f"Fallback también falló para {up.name}: {e}")
                        continue

                output_files.append((out_basename, tmp_out))

            else:
                # Modo endpoint externo
                if not api_url:
                    st.error("No has configurado URL del endpoint en la barra lateral.")
                    break
                success, data, err = call_external_endpoint(api_url, api_key, open(tmp_in, "rb").read(), up.name)
                if not success:
                    st.error(f"Error en endpoint externo para {up.name}: {err}")
                    continue
                # Guardar respuesta
                out_basename = os.path.splitext(up.name)[0] + "_mejorado." + (output_format if output_format else "mp3")
                tmp_out = os.path.join(tmpdir, out_basename)
                with open(tmp_out, "wb") as f:
                    f.write(data)
                output_files.append((out_basename, tmp_out))

            progress.progress(int(idx/total * 100))
        except Exception as e:
            st.error(f"Error procesando {up.name}: {e}")

    # Empaquetar todos en un ZIP para descarga
    if output_files:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, path in output_files:
                zf.write(path, arcname=name)
        zip_buffer.seek(0)
        st.success("Procesado finalizado ✅")
        st.download_button("📥 Descargar ZIP con audios mejorados", zip_buffer, file_name="audios_mejorados.zip", mime="application/zip")
    else:
        st.warning("No se generaron archivos de salida.")
