Mejorador de Audio con IA
Una aplicación Streamlit que mejora la calidad de archivos de audio (como los recibidos por WhatsApp) utilizando DeepFilterNet3 para supresión de ruido y mejora de voz, logrando un sonido con calidad de estudio. Permite procesar múltiples archivos de audio en lote y descargar los resultados.
Características

Subida de múltiples archivos de audio (MP3, WAV, OGG, FLAC, M4A).
Procesamiento automático con IA para eliminar ruido y mejorar la claridad.
Vista previa de audios originales y mejorados con formas de onda.
Descarga de audios mejorados individualmente o en un archivo ZIP.
Interfaz web sencilla con Streamlit.

Requisitos

Python 3.8+
Dependencias listadas en requirements.txt

Instalación

Clona el repositorio:git clone https://github.com/<tu-usuario>/audio_enhancer.git
cd audio_enhancer


Crea un entorno virtual (opcional, pero recomendado):python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate


Instala las dependencias:pip install -r requirements.txt


Ejecuta la aplicación:streamlit run app.py



Uso

Abre la aplicación en tu navegador (normalmente en http://localhost:8501).
Sube uno o más archivos de audio (MP3, WAV, OGG, FLAC, M4A).
La aplicación procesará automáticamente los archivos y mostrará una vista previa.
Descarga los audios mejorados individualmente o como un archivo ZIP.
Usa el botón "Limpiar Archivos Temporales" para eliminar archivos procesados.

Despliegue en Streamlit Cloud

Sube el repositorio a GitHub (ver instrucciones abajo).
Conecta tu cuenta de GitHub a Streamlit Cloud.
Crea una nueva app, selecciona el repositorio y el archivo app.py.
Configura la versión de Python (3.8 o superior) y asegúrate de que requirements.txt esté en el repositorio.
Despliega la aplicación.

Subir a GitHub

Crea un nuevo repositorio en GitHub.
En tu máquina local, inicializa un repositorio Git:git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/<tu-repositorio>.git
git push -u origin main


Verifica que los archivos app.py, requirements.txt y README.md estén en el repositorio.

Notas

Asegúrate de tener suficiente memoria y CPU para procesar múltiples archivos de audio.
DeepFilterNet3 requiere una instalación inicial que puede descargar modelos preentrenados.
Para formatos de audio específicos, asegúrate de tener los códecs necesarios instalados (por ejemplo, FFmpeg para M4A).

Licencia
MIT License
