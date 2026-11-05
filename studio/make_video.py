"""python3 make_video.py spec.json OUT.mp4 — собирает вертикальное видео 1080x1920 из JSON-спека (без озвучки)."""
import sys, json, subprocess, os
import steam_anim as SA
from steam_anim import *
POSES = ['think', 'present', 'confident', 'inspect', 'guard', 'wave']

def build(spec):
    T = spec['tag']; c = spec['cover']; crab_mode = spec.get('mascot') == 'crab'
    if crab_mode: SA.foot3 = lambda img: None   # на втором аккаунте без ника основного
    def cover():
        A, B = c['a'], c['b']; sz = fit_size([A, B], 900, 150); y0 = TOP + 60 + 0.705 * sz; y1 = y0 + 0.95 * sz
        def head(im):
            d = ImageDraw.Draw(im); shadow_text(d, (80, y0), A, sz); shadow_text(d, (80, y1), B, sz, 900, ACC)
        def sub(im):
            d = ImageDraw.Draw(im)
            for i, line in enumerate(c.get('sub', [])[:2]): shadow_text(d, (80, y1 + 70 + 50 * i), line, 34, 700, (170, 170, 200), off=4)
        return Scene(4.4, [(lambda im: SV.tag(im, c.get('tag', T)), 0, 'fade'), (head, 0.1, 'slide'), (sub, 0.9, 'fade')], None if crab_mode else ('guard', 850, 1640, 17))
    out = [cover()]
    for i, s in enumerate(spec['scenes']):
        rows = [(t, k) for t, k in s['rows']]
        out.append(mk(s['t1'], s.get('t2', ''), T, rows, s.get('foot', []), None if crab_mode else (s.get('pose', POSES[i % len(POSES)]), 890, 1660, 15), s.get('h', 130)))
    if crab_mode:
        txt = spec.get('cta', 'Сохрани, чтобы не потерять')
        def a(im):
            d = ImageDraw.Draw(im); t = 'Подписывайся'; sz = fit_size([t], 940, 118); shadow_text(d, (540 - font(sz, 900).getlength(t) / 2, 760), t, sz)
        def b(im):
            d = ImageDraw.Draw(im); shadow_text(d, (540 - font(30, 600).getlength(txt) / 2, 930), txt, 30, 600, (170, 170, 200), off=3)
        def c(im):
            d = ImageDraw.Draw(im); soft_shadow(im, (300, 1020, 780, 1116), 38, blur=16, off=(0, 10), color=ACC, alpha=110)
            d.rounded_rectangle([300, 1020, 780, 1116], 38, fill=ACC); d.text((540, 1068), 'Подписаться', font=font(38, 800), fill=WHITE, anchor='mm')
        out.append(Scene(4.2, [(a, 0.5, 'slide'), (b, 0.9, 'fade'), (c, 1.3, 'slide')], None))
    else: out.append(SA.cta(spec.get('cta', 'Сохрани, чтобы не потерять')))
    return out

VOICE = []  # [(start_sec, np.array float32 @44100)]

def prep_voice(spec, SC):
    """Озвучка: у сцены может быть "say": [["ruslan","реплика"],["irina","реплика"]]. Длина сцены растягивается под речь."""
    import voice, wave, tempfile, numpy as np
    global VOICE; VOICE = []; sc = spec['scenes']; t0 = 0.0
    for i, s in enumerate(SC):
        say = spec['cover'].get('say') if i == 0 else (sc[i - 1].get('say') if i <= len(sc) else spec.get('cta_say'))
        pos = 0.35
        for v, text in (say or []):
            f = tempfile.mktemp(suffix='.wav'); voice.tts(text, f, spec.get('speed', 1.0), v)
            w = wave.open(f); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; sr = w.getframerate(); os.remove(f)
            x = np.interp(np.arange(int(len(x) * 44100 / sr)) / 44100 * sr, np.arange(len(x)), x).astype(np.float32)
            VOICE.append((t0 + pos, x, v)); pos += len(x) / 44100 + 0.3
        if say: s.dur = max(s.dur, pos + 0.4)
        t0 += s.dur

def add_voice_music(video, seed=0, spec=None):
    import music, tempfile, numpy as np
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video])); SR = 44100; N = int(d * SR)
    vt = np.zeros(N, np.float32)
    for st, x, _v in VOICE:
        i = int(st * SR); j = min(N, i + len(x)); vt[i:j] += x[:j - i]
    env = np.convolve(np.abs(vt), np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same'); env = np.minimum(1, env / 0.05)
    env = np.convolve(env, np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    mc = (spec or {}).get('music')
    if mc:   # готовый трек из studio/music_lib (CC BY / CC0)
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(mc.get('start', 0)), '-t', str(d + 1), '-i', os.path.join(os.path.dirname(__file__), 'music_lib', mc['file']), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'])
        m = np.frombuffer(raw, np.float32).copy(); m = np.pad(m, (0, max(0, N - len(m))))[:N]
        m /= max(1e-6, np.abs(m).max()); m *= mc.get('volume', 0.35); fo = int(1.5 * SR); m[-fo:] *= np.linspace(1, 0, fo)
        mix = np.tanh(m * (1 - 0.65 * env) + vt * 1.1)
    else:
        m = music.gen(d, seed); m = np.pad(m, (0, max(0, N - len(m))))[:N]
        mix = np.tanh(m * 0.5 * (1 - 0.7 * env) + vt * 1.1)
    wav = tempfile.mktemp(suffix='.wav'); music.save(mix, wav); tmp = video + '.tmp.mp4'
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', tmp])
    os.replace(tmp, video); os.remove(wav)

def crab_overlay(im, T, spec):
    import crab
    pose = 'idle'; look = (1, 0)
    for st, x, v in VOICE:
        if st <= T < st + len(x) / 44100: pose = 'talk'; look = (1, 0) if v in ('ruslan', 'denis', 'dmitri') else (-1, 0)
    if T < 1.2 and not VOICE: pose = 'wow'
    im = im.copy(); crab.draw_crab(im, 500, 1250, T, pose, 10, look); return im

def render(spec, outpath):
    SA.SC = build(spec); SC = SA.SC; FPS = 30; TR = 0.35
    if any(x.get('say') for x in spec['scenes']) or spec['cover'].get('say'): prep_voice(spec, SC)
    with Pool(4) as pool:
        skins = {}
        for i, s in enumerate(SC):
            if s.skin: skins[i] = pool.map(SA._skin, [(i, k) for k in range(60)])
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', outpath], stdin=subprocess.PIPE)
    prev = None; gk = 0
    for i, s in enumerate(SC):
        for k in range(int(s.dur * FPS)):
            t = k / FPS; sk = skins[i][gk % 60].copy() if i in skins else None
            im = s.frame(t, sk)
            if spec.get('mascot') == 'crab': im = crab_overlay(im, gk / FPS, spec)
            if prev is not None and t < TR:
                x = ease(t / TR); off = int(W * x)
                canvas = Image.new('RGB', (W, H)); canvas.paste(prev, (-off, 0)); canvas.paste(im, (W - off, 0)); im = canvas
            p.stdin.write(im.tobytes()); gk += 1
        prev = s.frame(s.dur - 0.01, skins[i][0].copy() if i in skins else None)
    p.stdin.close(); return p.wait()

def slides(spec, outdir):
    """JPEG-слайды 1080x1920 для фото-карусели TikTok (финальный кадр каждой сцены)."""
    os.makedirs(outdir, exist_ok=True); SA.SC = build(spec); n = 0
    for i, s in enumerate(SA.SC):
        sk = SA._skin((i, 0)) if s.skin else None
        im = s.frame(s.dur - 0.01, sk.copy() if sk is not None else None)
        n += 1; im.convert('RGB').save(f'{outdir}/{n:02d}.jpg', quality=92)
    return n

def add_music(video, seed=0):
    import music, tempfile
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video]))
    wav = tempfile.mktemp(suffix='.wav'); music.save(music.gen(d, seed), wav); tmp = video + '.tmp.mp4'
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', tmp])
    os.replace(tmp, video); os.remove(wav)

if __name__ == '__main__':
    # python3 make_video.py spec.json OUT.mp4 [--slides DIR] [--no-music]
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; a = sys.argv[3:]
    rc = render(spec, out)
    if rc == 0 and '--no-music' not in a:
        sd = sum(map(ord, os.path.basename(out))) % 4
        add_voice_music(out, sd, spec) if VOICE else add_music(out, sd)
    if '--slides' in a: print('slides:', slides(spec, a[a.index('--slides') + 1]))
    sys.exit(rc)
