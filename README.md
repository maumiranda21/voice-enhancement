# Mejorador de Voz — Máxima Calidad (FFmpeg pipeline)

## Qué hace
Procesa notas de voz (WhatsApp, .opus, .ogg, .wav, .mp3) con un pipeline avanzado de FFmpeg:
- High-pass
- Ecualización (presencia vocal)
- Compresión dinámica
- Normalización LUFS (loudnorm)
- Salida a MP3/WAV de alta calidad

## Deploy (Streamlit Cloud)
1. Crea un repo en GitHub con estos archivos:
   - streamlit_app.py
   - requirements.txt
   - packages.txt
2. Ve a https://share.streamlit.io y crea una nueva app
   - Elige tu repo y `streamlit_app.py` como Main file
3. Deploy

## Nota sobre calidad "pro"
Para calidad *estudio* de verdad (eliminar reverberación, artefactos, reconstrucción de voz):
- Recomiendo usar **modelos IA especializados** (Demucs, VoiceFixer, RNNoise, etc.) ejecutados en un servidor con GPU, o usar un servicio de inferencia (Hugging Face Inference, Auphonic, Adobe Podcast API).
- En `streamlit_app.py` tienes la opción "Usar endpoint externo (IA)" para enviar archivos a un endpoint que retorne audio mejorado.

## Recomendaciones
- Para procesar muchos/archivos largos, usa un servidor con CPU potente o GPU.
- Si FFmpeg no soporta alguno de los filtros (varía por build), ajusta la cadena `-af` en la app.
