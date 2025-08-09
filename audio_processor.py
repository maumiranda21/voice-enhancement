# utils/rnnoise_wrapper.py
"""
Wrapper sencillo para usar un binario RNNoise (CLI) que procese WAV en->out WAV.
Este wrapper asume que existe un ejecutable llamado `rnnoise_demo` o `rnnoise_cli`
en la carpeta utils/rnnoise/ y que acepta:
  rnnoise_cli in.wav out.wav

Si no encuentras binarios para tu plataforma, en README indico cómo compilar o dónde descargar.
"""

import shutil
import subprocess
from pathlib import Path

RNNOISE_BINARIES = [
    Path("utils/rnnoise/rnnoise_demo"),   # ejemplo nombre común
    Path("utils/rnnoise/rnnoise_cli"),
    Path("utils/rnnoise/rnnoise"), 
]

def rnnoise_available():
    for p in RNNOISE_BINARIES:
        if p.exists() and p.is_file() and os.access(p, os.X_OK):
            return True
    # fallback: check if system has rnnoise in PATH
    return shutil.which("rnnoise_demo") is not None or shutil.which("rnnoise_cli") is not None or shutil.which("rnnoise") is not None

def find_rnnoise_executable():
    for p in RNNOISE_BINARIES:
        if p.exists() and p.is_file() and os.access(p, os.X_OK):
            return str(p.resolve())
    # try PATH
    for name in ["rnnoise_demo","rnnoise_cli","rnnoise"]:
        p = shutil.which(name)
        if p:
            return p
    return None

def denoise_with_rnnoise(input_wav, output_wav):
    exe = find_rnnoise_executable()
    if exe is None:
        raise RuntimeError("No se encontró ejecutable RNNoise. Coloca el binario en utils/rnnoise/ o instala en PATH.")
    # Call: rnnoise_cli input.wav output.wav
    subprocess.run([exe, str(input_wav), str(output_wav)], check=True)
