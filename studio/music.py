"""Оригинальная фоновая музыка (синтез, без чужих сэмплов): python3 music.py DURATION_SEC OUT.wav [seed]"""
import sys, wave, numpy as np
SR = 44100
def nf(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a=0.005, d=0.12, s=0.0, r=0.05):
    t = np.arange(n) / SR; e = np.exp(-t / d) * (1 - s) + s; e = e * np.minimum(1, t / a)
    rl = int(r * SR); e[-rl:] *= np.linspace(1, 0, rl) if n > rl else 1; return e
def tone(f, n, kind='tri'):
    t = np.arange(n) / SR; ph = (f * t) % 1
    if kind == 'sq': return np.sign(np.sin(2 * np.pi * ph)) * 0.5
    if kind == 'tri': return 2 * np.abs(2 * ph - 1) - 1
    return np.sin(2 * np.pi * f * t)
def gen(dur, seed=0):
    rng = np.random.default_rng(seed); bpm = [92, 96, 100, 104][seed % 4]; beat = 60 / bpm; N = int((dur + 1) * SR); out = np.zeros(N)
    prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    if seed % 2: prog = [[57, 60, 64], [55, 59, 62], [53, 57, 60], [52, 55, 59]]
    bar = beat * 4; nbars = int((dur + 1) / bar) + 1
    def add(x, st):
        i = int(st * SR); j = min(N, i + len(x))
        if i < N: out[i:j] += x[:j - i]
    for b in range(nbars):
        ch = prog[(b // 2) % 4]; st = b * bar
        n = int(bar * SR)
        for k, m in enumerate(ch):
            p = tone(nf(m - 12), n, 'sin') * 0.5 + tone(nf(m - 12) * 1.003, n, 'tri') * 0.25
            add(p * env(n, 0.3, 5, 0.6, 0.4) * 0.12, st)
        add(tone(nf(ch[0] - 24), n, 'sin') * env(n, 0.02, 1.5, 0.3, 0.2) * 0.22, st)
        for s in range(16):
            if s % 2 == 0 or rng.random() < 0.35:
                m = ch[(s // 2 + (s % 3)) % 3] + 12 * (1 + (s % 5 == 0)); nn = int(beat * 0.5 * SR)
                add(tone(nf(m), nn, 'sq') * env(nn, 0.003, 0.09, 0, 0.03) * 0.07, st + s * beat / 4)
        for q in range(4):
            nn = int(0.2 * SR); t = np.arange(nn) / SR; kick = np.sin(2 * np.pi * (110 * np.exp(-t * 18) + 45) * t) * np.exp(-t * 12)
            add(kick * 0.35, st + q * beat)
            hh = rng.standard_normal(int(0.04 * SR)) * np.exp(-np.arange(int(0.04 * SR)) / SR / 0.012)
            add(hh * 0.06, st + q * beat + beat / 2)
    out = out[:int((dur) * SR)]; fi = int(1.0 * SR); fo = int(2.5 * SR)
    out[:fi] *= np.linspace(0, 1, fi); out[-fo:] *= np.linspace(1, 0, fo)
    out = np.tanh(out * 1.6) / np.tanh(1.6); out = out / (np.abs(out).max() + 1e-9) * 0.5
    return out
def save(x, path):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
if __name__ == '__main__':
    save(gen(float(sys.argv[1]), int(sys.argv[3]) if len(sys.argv) > 3 else 0), sys.argv[2])
