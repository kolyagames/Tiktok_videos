"""python3 make_video.py spec.json OUT.mp4 — собирает вертикальное видео 1080x1920 из JSON-спека (без озвучки)."""
import sys, json, subprocess, os
import steam_anim as SA
from steam_anim import *
POSES = ['think', 'present', 'confident', 'inspect', 'guard', 'wave']

def build(spec):
    T = spec['tag']; c = spec['cover']
    def cover():
        A, B = c['a'], c['b']; sz = fit_size([A, B], 900, 150); y0 = TOP + 60 + 0.705 * sz; y1 = y0 + 0.95 * sz
        def head(im):
            d = ImageDraw.Draw(im); shadow_text(d, (80, y0), A, sz); shadow_text(d, (80, y1), B, sz, 900, ACC)
        def sub(im):
            d = ImageDraw.Draw(im)
            for i, line in enumerate(c.get('sub', [])[:2]): shadow_text(d, (80, y1 + 70 + 50 * i), line, 34, 700, (170, 170, 200), off=4)
        return Scene(4.4, [(lambda im: SV.tag(im, c.get('tag', T)), 0, 'fade'), (head, 0.1, 'slide'), (sub, 0.9, 'fade')], ('guard', 850, 1640, 17))
    out = [cover()]
    for i, s in enumerate(spec['scenes']):
        rows = [(t, k) for t, k in s['rows']]
        out.append(mk(s['t1'], s.get('t2', ''), T, rows, s.get('foot', []), (s.get('pose', POSES[i % len(POSES)]), 890, 1660, 15), s.get('h', 130)))
    out.append(SA.cta(spec.get('cta', 'Сохрани, чтобы не потерять')))
    return out

def render(spec, outpath):
    SA.SC = build(spec); SC = SA.SC; FPS = 30; TR = 0.35
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
            if prev is not None and t < TR:
                x = ease(t / TR); off = int(W * x)
                canvas = Image.new('RGB', (W, H)); canvas.paste(prev, (-off, 0)); canvas.paste(im, (W - off, 0)); im = canvas
            p.stdin.write(im.tobytes()); gk += 1
        prev = s.frame(s.dur - 0.01, skins[i][0].copy() if i in skins else None)
    p.stdin.close(); return p.wait()

if __name__ == '__main__':
    sys.exit(render(json.load(open(sys.argv[1])), sys.argv[2]))
