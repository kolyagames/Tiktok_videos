"""Озвучка (русский голос Ruslan, Piper через sherpa-onnx). Модель качается с GitHub при первом запуске.
python3 voice.py "текст" out.wav [speed]   |  from voice import tts; tts(text, path, speed)
"""
import os, sys, tarfile, urllib.request, wave
import numpy as np
URL = 'https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-ru_RU-ruslan-medium.tar.bz2'
DIR = os.environ.get('VOICE_DIR', '/tmp/voice_ruslan'); M = os.path.join(DIR, 'vits-piper-ru_RU-ruslan-medium') + '/'
_tts = None
def _get():
    global _tts
    if _tts: return _tts
    import sherpa_onnx
    if not os.path.exists(M + 'tokens.txt'):
        os.makedirs(DIR, exist_ok=True); f = os.path.join(DIR, 'm.tar.bz2'); urllib.request.urlretrieve(URL, f)
        tarfile.open(f).extractall(DIR); os.remove(f)
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(
        model=M + 'ru_RU-ruslan-medium.onnx', tokens=M + 'tokens.txt', data_dir=M + 'espeak-ng-data'), num_threads=2))
    _tts = sherpa_onnx.OfflineTts(cfg); return _tts
def tts(text, path, speed=1.0):
    a = _get().generate(text, sid=0, speed=speed); x = np.array(a.samples)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(a.sample_rate); w.writeframes((x * 32767).astype(np.int16).tobytes())
    return len(x) / a.sample_rate
if __name__ == '__main__':
    print(tts(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0))
