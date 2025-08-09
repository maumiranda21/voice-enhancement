# Mejorador Agresivo — Voz estilo locutor (Código)

## Descripción
Pipeline avanzado que combina reducción de ruido (noisereduce) y pulido agresivo con FFmpeg:
- denoise (noisereduce)
- pulido con filtros FFmpeg (HP/LP/EQ/Comp/afftdn/loudnorm)
- fallbacks automatizados si algún filtro no está disponible
- procesa múltiples archivos y devuelve ZIP con resultados

## Archivos
- `streamlit_app.py` — interfaz Streamlit
- `audio_processor.py` — motor DSP + wrappers FFmpeg
- `requirements.txt`
- `packages.txt` (para instalar ffmpeg en Streamlit Cloud)

## Deploy (Streamlit Community Cloud)
1. Crear repo en GitHub con estos archivos (no ZIP).
2. En Streamlit Cloud → New app → seleccionar repo y `streamlit_app.py`.
3. Si hay errores de filtro en FFmpeg (logs en Streamlit), revisa qué filtros no están disponibles y comunica el log.

## Notas de rendimiento
- **Para mejor rendimiento y resultados reales (rápidos):** usa un servidor con más CPU o usa un endpoint IA (Demucs) si quieres eliminar reverberación/eco más agresivamente.
- **afftdn** y algunos filtros (e.g. `loudnorm`) pueden no estar presentes en todos los builds de ffmpeg; el código intenta fallbacks automáticos.

## Debugging
- Si ves "FFmpeg polishing falló", copia los logs completos y pégalos para que te ayude a ajustar la cadena de filtros.
