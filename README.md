# Conversor y Mejorador de Voz — Prototipo Streamlit

Esta app es un prototipo para mejorar notas de voz (por ejemplo .opus de WhatsApp) aplicando:
- Conversión a WAV (ffmpeg + pydub)
- Reducción de ruido (noisereduce)
- High-pass para eliminar graves indeseados
- Normalización a un nivel objetivo

## Contenido del repo
- `streamlit_app.py` — código principal de la app (Streamlit)
- `requirements.txt` — dependencias de Python
- `packages.txt` — paquetes del sistema (solicitamos `ffmpeg`)
- `audioop.py` — stub para evitar `ModuleNotFoundError` en algunos entornos
- `runtime.txt` — fuerza Python 3.12 en Streamlit Cloud
- `.gitignore` — sugerencias para ignorar archivos locales

---

## Probar localmente (recomendado)
1. Instala `ffmpeg` en tu máquina:
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`
   - Windows: descarga un build estático desde https://ffmpeg.org/download.html y añade `\...\ffmpeg\bin` al PATH

2. Crea y activa un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate    # macOS / Linux
venv\Scripts\activate     # Windows
```

3. Instala dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta la app:
```bash
streamlit run streamlit_app.py
```
Abre `http://localhost:8501` en tu navegador.

---

## Subir a GitHub (pasos rápidos)
1. Crea un repo nuevo en GitHub (puede ser privado o público).
2. Desde la carpeta del proyecto en tu ordenador:
```bash
git init
git add .
git commit -m "Initial commit - audio enhancer prototype"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

(Sustituye la URL por la de tu repo.)

---

## Desplegar en Streamlit Community Cloud
1. Ve a https://share.streamlit.io e inicia sesión con GitHub.
2. Haz clic en **'New app'**.
3. Selecciona:
   - Repository: el repo que acabas de subir.
   - Branch: `main`
   - Main file path: `streamlit_app.py`
4. Haz clic en **'Deploy'** y espera.

### Si aparece error `ModuleNotFoundError: No module named 'audioop'`
- Este repo ya incluye `audioop.py` (stub) y `runtime.txt` con `3.12`. Si aun así falla:
  1. Ve al panel de tu app en Streamlit Cloud.
  2. En las opciones (⋮) selecciona **'Clear cache and redeploy'**.
  3. Si sigue fallando, revisa los logs en el panel (puedes abrir la consola de la app o ver los logs) y considera desplegar en Replit/Render si Streamlit Cloud no permite `audioop` en su build.

### Si `ffmpeg` no se instala correctamente en Streamlit Cloud
- `packages.txt` solicita `ffmpeg`, pero en raras ocasiones la instalación puede fallar en el entorno de Streamlit Cloud.
- Si fallara, opciones:
  - Usar **Replit** (es más flexible para binarios) o **Render**.
  - Ejecutar la app localmente (recomendado para pruebas).

---

## Sugerencias y siguientes pasos
- Para calidad "calidad de estudio" real, integrar modelos como **Demucs**, **RNNoise** o servicios externos (Adobe Podcast Enhance, Auphonic).
- Añadir selección manual de segmento de ruido (mejora la reducción de ruido).
- Añadir procesamiento en batch y generación de ZIP con múltiples archivos.
- Mejorar UI: waveform preview, barra de progreso, opciones de formato/bitrate.

---

Licencia: MIT
