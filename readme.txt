# Mejorador de Audio con IA

Una aplicación Streamlit que mejora la calidad de archivos de audio (como los recibidos por WhatsApp) utilizando DeepFilterNet3 para supresión de ruido y mejora de voz, logrando un sonido con calidad de estudio. Permite procesar múltiples archivos de audio en lote y descargar los resultados.

## Características
- Subida de múltiples archivos de audio (MP3, WAV, OGG, FLAC, M4A).
- Procesamiento automático con IA para eliminar ruido y mejorar la claridad.
- Vista previa de audios originales y mejorados con formas de onda.
- Descarga de audios mejorados individualmente o en un archivo ZIP.
- Interfaz web sencilla con Streamlit.

## Requisitos
- Python 3.8+
- Dependencias listadas en `requirements.txt`

## Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/<tu-usuario>/voice-enhancement.git
   cd voice-enhancement
