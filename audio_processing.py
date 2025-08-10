
import os, math, tempfile, subprocess, shutil
from pathlib import Path
import numpy as np
import soundfile as sf
import noisereduce as nr
import librosa
import librosa.display
from pydub import AudioSegment, effects
from concurrent.futures import ThreadPoolExecutor, as_completed

SUPPORTED_TYPES = {'wav','mp3','ogg','m4a','flac','aac','opus'}

def check_ffmpeg():
    # returns True if ffmpeg executable available
    return shutil.which('ffmpeg') is not None

def _convert_to_wav(in_path, target_sr=44100):
    """Use ffmpeg (via pydub) to convert to 16-bit WAV with target_sr."""
    out_path = str(Path(in_path).with_suffix('.wav'))
    audio = AudioSegment.from_file(in_path)
    audio = audio.set_frame_rate(target_sr).set_sample_width(2).set_channels(1)
    audio.export(out_path, format='wav')
    return out_path

def _apply_highpass(signal, sr, cutoff=80):
    # simple first-order high-pass filter via librosa's effects
    # we'll implement a butterworth high-pass
    from scipy.signal import butter, sosfilt
    sos = butter(2, cutoff, btype='highpass', fs=sr, output='sos')
    filtered = sosfilt(sos, signal)
    return filtered

def _boost_presence(signal, sr, gain_db=3):
    # apply a simple shelving EQ: boost above 3000 Hz
    # implement via FFT manipulation (simple)
    if gain_db == 0:
        return signal
    S = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), 1/sr)
    # calculate gain curve
    boost = 10**(gain_db/20)
    # apply a smooth ramp starting at 2000 Hz
    mask = np.clip((freqs - 2000) / (sr/2 - 2000), 0, 1)
    S = S * (1 + (boost - 1) * mask)
    out = np.fft.irfft(S, n=len(signal))
    return out

def _rms_normalize(signal, target_db=-20.0):
    # normalize to target RMS dBFS
    rms = np.sqrt(np.mean(signal**2))
    if rms == 0:
        return signal
    target_linear = 10 ** (target_db / 20)
    factor = target_linear / (rms + 1e-9)
    return signal * factor

def process_file(in_path, out_dir=None, target_sr=44100, preserve_name=True, nr_strength=0.6, hp_cut=80, clarity_gain_db=3):
    p = Path(in_path)
    if out_dir is None:
        out_dir = p.parent
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Convert to WAV mono
    try:
        wav_path = _convert_to_wav(in_path, target_sr=target_sr)
        y, sr = librosa.load(wav_path, sr=target_sr, mono=True)
    except Exception as e:
        # fallback: try to load directly
        y, sr = librosa.load(in_path, sr=target_sr, mono=True)

    # 1) Noise reduction (spectral gating)
    try:
        reduced = nr.reduce_noise(y=y, sr=sr, prop_decrease=nr_strength)
    except Exception:
        reduced = y

    # 2) High-pass filter to remove rumble
    try:
        hp = _apply_highpass(reduced, sr, cutoff=hp_cut)
    except Exception:
        hp = reduced

    # 3) Boost presence
    try:
        boosted = _boost_presence(hp, sr, gain_db=clarity_gain_db)
    except Exception:
        boosted = hp

    # 4) Normalize RMS
    normalized = _rms_normalize(boosted, target_db=-18.0)

    # 5) Export using soundfile then apply pydub for nice encoding options
    tmp_out = out_dir / (p.stem + "_studio.wav")
    sf.write(str(tmp_out), normalized, sr, subtype='PCM_16')

    # convert to mp3 and keep wav optionally
    final_out = out_dir / (p.stem + "_studio.mp3")
    audio_seg = AudioSegment.from_wav(str(tmp_out))
    audio_seg = effects.normalize(audio_seg)
    audio_seg.export(str(final_out), format='mp3', bitrate='192k')

    # Optionally return WAV too; for now return mp3 path
    return str(final_out)

def process_batch(file_paths, out_dir=None, target_sr=44100, preserve_names=True, n_jobs=2, nr_strength=0.6, hp_cut=80, clarity_gain_db=3, progress_callback=None):
    if out_dir is None:
        out_dir = tempfile.mkdtemp()
    os.makedirs(out_dir, exist_ok=True)
    results = []
    with ThreadPoolExecutor(max_workers=n_jobs) as ex:
        futures = {}
        for fp in file_paths:
            futures[ex.submit(process_file, fp, out_dir, target_sr, preserve_names, nr_strength, hp_cut, clarity_gain_db)] = fp
        for fut in as_completed(futures):
            try:
                res = fut.result()
                results.append(res)
            except Exception as e:
                # continue on errors
                print(f"Error processing {futures[fut]}: {e}")
    return results
