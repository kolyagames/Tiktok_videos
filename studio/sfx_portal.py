"""Звук для portal3d: python3 sfx_portal.py events.json out.wav"""
import json, sys, numpy as np, music
SR = music.SR
ev = json.load(open(sys.argv[1])); dur = ev['dur']; N = int(dur * SR); rng = np.random.default_rng(1)
out = np.zeros(N)
def add(x, st, g=1.0):
    i = int(st * SR); j = min(N, i + len(x));
    if i < N: out[i:j] += x[:j - i] * g
def thud(f0=140):
    n = int(0.35 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (f0 * np.exp(-t * 14) + 50) * t) * np.exp(-t * 11)
    click = rng.standard_normal(n) * np.exp(-t * 90) * 0.35
    return body + click
for i, e in enumerate(ev['events'][:-1]):
    add(thud(120 + 6 * i), e, 0.55)
    n = int(0.12 * SR); t = np.arange(n) / SR   # каменный «цок» с растущей высотой
    add(np.sin(2 * np.pi * (500 + 40 * i) * t) * np.exp(-t * 40) * 0.12, e)
# нарастание перед порталом
p = ev['portal']; rs = 0.9; n = int(rs * SR); t = np.arange(n) / SR
noise = rng.standard_normal(n); sweep = np.sin(2 * np.pi * (200 + 1800 * (t / rs) ** 2) * t)
add((noise * 0.25 + sweep * 0.4) * (t / rs) ** 2, p - rs, 0.5)
# удар открытия портала + гул
n = int(1.6 * SR); t = np.arange(n) / SR
boom = np.sin(2 * np.pi * (90 * np.exp(-t * 3) + 35) * t) * np.exp(-t * 2.2) + rng.standard_normal(n) * np.exp(-t * 6) * 0.3
add(boom, p, 0.9)
n = int((dur - p) * SR); t = np.arange(n) / SR
hum = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 110.7 * t) + 0.3 * np.sin(2 * np.pi * (220 + 30 * np.sin(t * 2)) * t))
add(hum * np.minimum(1, t / 0.8) * 0.18, p)
# вжух при влёте
n = int(1.2 * SR); t = np.arange(n) / SR; k = t / 1.2
w = rng.standard_normal(n) * np.sin(np.pi * k) ** 2
add(np.convolve(w, np.ones(12) / 12, 'same') * 0.5 + np.sin(2 * np.pi * (300 + 900 * k) * t) * 0.12 * k, dur - 1.5, 0.7)
out = np.tanh(out * 1.1)
m = music.gen(dur, 2); m = np.pad(m, (0, max(0, N - len(m))))[:N]
mix = np.tanh(out * 0.9 + m * 0.45)
f = int(0.5 * SR); mix[-f:] *= np.linspace(1, 0, f)
music.save(mix, sys.argv[2]); print('ok', len(mix) / SR)
