
# StudioClean — Auto audio studio-quality (Streamlit app)

Este repositorio contiene una aplicación Streamlit simple que permite subir múltiples audios y procesarlos automáticamente para mejorar su calidad (reducción de ruido, ecualización, normalización). El objetivo es ofrecer una versión **open-source** aproximada de lo que hacen herramientas comerciales tipo *Adobe Podcast*.

## Estructura
- `app.py` — interfaz Streamlit
- `audio_processing.py` — funciones de procesamiento (librosa, noisereduce, pydub)
- `requirements.txt`

## Cómo desplegar (Streamlit Cloud / local)
1. Asegúrate de que `ffmpeg` esté instalado en el entorno y accesible desde PATH. Streamlit Cloud suele permitir añadir binarios, pero en entornos locales instala con tu package manager (`apt`, `brew` o similar).
2. Crea un repo en GitHub con estos archivos.
3. Conecta el repo en https://streamlit.io/cloud y despliega.

## Notas técnicas y recomendaciones
- Este proyecto usa `noisereduce` (spectral gating) + filtros y ecualización espectral simple. No es un reemplazo directo de modelos comerciales basados en deep learning (Demucs, RNNoise, Adobe), pero ofrece mejoras notables sin GPU.
- Para integración con modelos avanzados (por ejemplo RNNoise, Demucs o modelos basados en Torch), añade la lógica en `audio_processing.py` y adapta `requirements.txt` en consecuencia.
- Para mantener los mismos nombres de archivo, selecciona la opción en la UI; en caso de conflicto se añade un sufijo.

## Limitaciones
- Calidad depende de la grabación original. Grabaciones extremadamente ruidosas o con eco profundo requieren modelos más complejos.
- Algunas funciones requieren `ffmpeg` instalado.

## Licencia
MIT
