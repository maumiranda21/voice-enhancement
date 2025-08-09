# Voice Enhancement App

Pipeline avanzado que combina reducción de ruido (noisereduce) y pulido agresivo con FFmpeg y RNNoise.

## Características
- Reducción de ruido (noisereduce, RNNoise opcional)
- Pulido con filtros FFmpeg (HP/LP/EQ/Comp/afftdn/loudnorm)
- Fallbacks automáticos si algún filtro no está disponible
- Procesa múltiples archivos y devuelve ZIP con resultados

---

## Archivos principales
- `streamlit_app.py` — Interfaz principal (ejecuta el app)
- `audio_processor.py` — Motor DSP + wrappers FFmpeg/RNNoise
- `requirements.txt` — Paquetes Python requeridos
- `packages.txt` — Para instalar ffmpeg en Streamlit Cloud

---

## Requisitos

### Python
- Python 3.8+

### Paquetes Python
Instala los paquetes con:
```bash
pip install -r requirements.txt
```

### FFmpeg
Se requiere un build **completo** de FFmpeg con los siguientes filtros:
- `afftdn` (denoiser)
- `loudnorm` (normalización de loudness)
- `highpass`, `lowpass`, `equalizer`, `acompressor` (EQ/Comp)

En **Streamlit Cloud** se instala automáticamente con `packages.txt`, pero algunos filtros pueden faltar. Para builds completos en tu máquina:
- [Descarga FFmpeg estático aquí](https://www.gyan.dev/ffmpeg/builds/) (Windows) o instala vía Homebrew en Mac/Linux.

Verifica filtros disponibles:
```bash
ffmpeg -filters | grep afftdn
# Si no aparece, tu build de ffmpeg no tiene el filtro.
```

### RNNoise (opcional, para mejor denoise)
Se recomienda colocar el binario de RNNoise en `utils/rnnoise/`:
- `rnnoise_demo`, `rnnoise_cli`, o `rnnoise`
- Puedes compilarlo desde [xiph/rnnoise](https://github.com/xiph/rnnoise) o [descargar binarios aquí](https://github.com/GregorR/rnnoise-models)

---

## Deploy (Streamlit Community Cloud)

1. Sube el repo SIN archivos comprimidos (NO ZIP).
2. En Streamlit Cloud → New app → selecciona repo y `streamlit_app.py` como entrypoint.
3. Si ves errores de filtros en FFmpeg (en los logs), revisa qué filtros faltan y ajústalo, o consulta la sección de troubleshooting.

---

## Uso local

```bash
streamlit run streamlit_app.py
```

---

## Troubleshooting

- **"No se encontró ejecutable RNNoise":** Descarga o compila el binario y mételo en `utils/rnnoise/`.
- **Errores en filtros FFmpeg:** Verifica tu build con `ffmpeg -filters`. Si falta un filtro, busca un build más completo o elimina la opción agresiva.
- **App no inicia en Streamlit Cloud:** Asegúrate de que los archivos no están comprimidos y que `streamlit_app.py` existe en raíz.
- **Sin salida generada:** Puede deberse a algún error de filtros o formatos no soportados. Revisa los logs y asegúrate de que el audio sea compatible (wav, mp3, ogg, opus, m4a).

---

## Notas de rendimiento

- Para rendimiento óptimo usa un equipo con CPU potente.
- Para eliminar eco/reverberación fuerte, considera integrar Demucs u otro modelo IA.

---

## Debugging

- Si ves "FFmpeg polishing falló", copia los logs completos y pégalos en un GitHub Issue o en la sección de soporte para ayuda personalizada.

---

## Créditos

Autor: [@maumiranda21](https://github.com/maumiranda21)
