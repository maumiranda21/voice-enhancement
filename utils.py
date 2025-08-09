import numpy as np
from pydub import AudioSegment
from scipy.signal import resample

def mejorar_audio(audio_bytes, formato):
    # Cargar audio desde bytes
    audio = AudioSegment.from_file_using_temporary_files(audio_bytes, format=formato)

    # Convertir a mono
    audio = audio.set_channels(1)

    # Resamplear a 44.1 kHz usando scipy
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    num_muestras_nuevo = int(len(samples) * 44100 / audio.frame_rate)
    resampled = resample(samples, num_muestras_nuevo)

    # Crear nuevo AudioSegment con la tasa de muestreo deseada
    audio_mejorado = AudioSegment(
        resampled.astype(np.int16).tobytes(),
        frame_rate=44100,
        sample_width=2,
        channels=1
    )

    # Normalizar
    audio_mejorado = audio_mejorado.apply_gain(-audio_mejorado.max_dBFS)

    return audio_mejorado
