
import streamlit as st
from audio_processing import process_batch, check_ffmpeg, SUPPORTED_TYPES
from pathlib import Path
import tempfile, os, io

st.set_page_config(page_title="StudioClean — Auto audio studio-quality", layout="centered")

st.title("StudioClean — Auto audio studio-quality 🚀🎙️")
st.markdown(
    """Sube audios (WhatsApp, móviles, grabaciones) y procesa automáticamente:
- reducción de ruido
- ecualización suave (claridad / presencia)
- normalización y mejora de dinámica
- procesamiento por lotes y descarga en zip

**Nota**: el procesamiento usa librerías open-source (no es la IA propietaria de Adobe). Para resultados aún mejores puedes usar modelos avanzados (DN, Demucs) integrándolos después.
"""
)

st.header("1) Subir archivos")
uploaded = st.file_uploader("Sube uno o varios audios", accept_multiple_files=True, type=list(SUPPORTED_TYPES))

cols = st.columns(3)
with cols[0]:
    preserve_names = st.checkbox("Preservar nombres originales (si existe conflicto se añade sufijo)", value=True)
with cols[1]:
    target_sr = st.selectbox("Frecuencia muestreo de salida (Hz)", options=[16000, 22050, 32000, 44100], index=3)
with cols[2]:
    n_jobs = st.number_input("Procesos paralelos", min_value=1, max_value=8, value=2, step=1)

st.markdown("---")
st.header("2) Opciones de mejora (predeterminadas funcionan bien)")

nr_strength = st.slider("Fuerza reducción de ruido (más = más agresivo)", 0.0, 1.0, 0.6)
hp_cut = st.slider("Filtro High-pass (Hz) — elimina graves no deseados", 50, 400, 80)
clarity_gain = st.slider("Aumento de presencia/agudos (dB)", 0, 8, 3)

st.markdown("---")
st.header("3) Procesar y descargar")

if uploaded:
    st.write(f"Archivos cargados: {len(uploaded)}")
    if not check_ffmpeg():
        st.warning("ffmpeg no está disponible en el entorno. Algunas conversiones pueden fallar. Instala ffmpeg en el sistema o agrega el binario al PATH.")
    if st.button("Procesar ahora"):
        with st.spinner("Procesando audios..."):
            # save uploaded to temporary files
            tmpdir = tempfile.mkdtemp()
            file_paths = []
            for f in uploaded:
                p = Path(tmpdir) / f.name
                # ensure unique
                i = 1
                while p.exists():
                    p = Path(tmpdir) / f"{p.stem}_{i}{p.suffix}"
                    i += 1
                p.write_bytes(f.getbuffer())
                file_paths.append(str(p))
            # process batch
            results = process_batch(
                file_paths,
                out_dir=tmpdir,
                target_sr=int(target_sr),
                preserve_names=preserve_names,
                n_jobs=int(n_jobs),
                nr_strength=float(nr_strength),
                hp_cut=int(hp_cut),
                clarity_gain_db=float(clarity_gain),
                progress_callback=None
            )
            # results: list of output file paths
            # create zip
            zip_path = Path(tmpdir) / "studio_cleaned_outputs.zip"
            import zipfile
            with zipfile.ZipFile(zip_path, "w") as zf:
                for src in results:
                    arcname = Path(src).name
                    zf.write(src, arcname=arcname)
            st.success("Procesamiento completado 🎉")
            with open(zip_path, "rb") as fh:
                st.download_button("Descargar ZIP", data=fh, file_name="studio_cleaned_outputs.zip", mime="application/zip")
else:
    st.info("Sube archivos para habilitar el procesamiento")

st.markdown("---")
st.caption("Diseñado para ser desplegado en Streamlit Cloud o tu propio servidor. Revisa README para dependencias (ffmpeg requerido).")

