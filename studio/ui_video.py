"""Ролик в стиле Dark UI + Pixel Art: python3 ui_video.py OUT.mp4  (HDD или SSD, 19.5 с, 1080x1920, 30 fps)"""
import os, sys, math, subprocess, wave, random, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crab, voice
W, H, FPS, DUR = 1080, 1920, 30, 19.5
BG = (18, 18, 20); OR = (255, 85, 0); GR = (16, 185, 129); WHITE = (255, 255, 255); LG = (236, 238, 242); DK = (28, 28, 34); GRAY = (150, 154, 165)
HERE = os.path.dirname(os.path.abspath(__file__))
_fc = {}
def font(sz, wt=900):
    k = (int(sz), int(wt))
    if k not in _fc:
        f = ImageFont.truetype(HERE + '/Nunito.ttf', int(sz)); f.set_variation_by_axes([int(wt)]); _fc[k] = f
    return _fc[k]
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
def spring(u):  # с перелётом
    u = max(0, min(1, u)); return 1 - math.exp(-6 * u) * math.cos(14 * u)
def lerp(a, b, u): return a + (b - a) * u
def mix(c1, c2, u): return tuple(int(lerp(a, b, u)) for a, b in zip(c1, c2))

# ---- озвучка ----
LINES = [  # (старт, голос, текст)
    (0.4, 'ruslan', 'Жёсткий диск или эс-эс-ди?'),
    (3.2, 'irina', 'Оба хранят файлы без питания.'),
    (6.2, 'irina', 'У эс-эс-ди нет подвижных частей. Он быстрее и тише.'),
    (10.45, 'ruslan', 'А минусы?'),
    (11.5, 'irina', 'Дороже за гигабайт, ячейки изнашиваются.'),
    (14.3, 'irina', 'Выбирай под задачу.'),
    (16.5, 'ruslan', 'Подписывайся!'),
]
SR = 44100
def build_audio(path):
    vt = np.zeros(int(DUR * SR), np.float32); info = []
    for st, v, text in LINES:
        f = tempfile.mktemp(suffix='.wav'); d = voice.tts(text, f, 1.08, v)
        w = wave.open(f); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; sr = w.getframerate(); os.remove(f)
        x = np.interp(np.arange(int(len(x) * SR / sr)) / SR * sr, np.arange(len(x)), x).astype(np.float32)
        i = int(st * SR); vt[i:i + len(x)] += x[:max(0, len(vt) - i)][:len(x)]; info.append((st, st + len(x) / SR, v))
    for k in range(len(info) - 1):
        if info[k][1] > info[k + 1][0] - 0.05: print('ПЕРЕКРЫТИЕ реплик', k, info[k], info[k + 1])
    print('реплики:', [(round(a, 1), round(b, 1)) for a, b, _ in info])
    env = np.convolve(np.abs(vt), np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same'); env = np.minimum(1, env / 0.05)
    env = np.convolve(env, np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', '20', '-t', str(DUR + 1), '-i', HERE + '/music_lib/Syntheticity.mp3', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'])
    m = np.frombuffer(raw, np.float32).copy(); m = np.pad(m, (0, max(0, len(vt) - len(m))))[:len(vt)]
    m /= max(1e-6, np.abs(m).max()); m *= 0.38; fo = int(1.2 * SR); m[-fo:] *= np.linspace(1, 0, fo)
    out = np.tanh(m * (1 - 0.65 * env) + vt * 1.1); import music; music.save(out, path)
    return vt, info

# ---- графика ----
def grid():
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    c = mix(BG, WHITE, 0.15)
    for x in range(0, W, 40): d.line([(x, 0), (x, H)], fill=c)
    for y in range(0, H, 40): d.line([(0, y), (W, y)], fill=c)
    return im
GRID = grid()
def card(im, box, fill=WHITE, r=24, shadow=True):
    x0, y0, x1, y1 = [int(v) for v in box]
    if shadow:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 14, x1, y1 + 14], r, fill=(0, 0, 0, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(18)); im.paste(sh, (0, 0), sh)
    ImageDraw.Draw(im).rounded_rectangle([x0, y0, x1, y1], r, fill=fill)
def txt(im, xy, s, sz, fill=WHITE, wt=900, anchor='mm'):
    ImageDraw.Draw(im).text(xy, s, font=font(sz, wt), fill=fill, anchor=anchor)
def rich(im, cx, y, words, sz, base, hl=OR, wt=900):
    """строка слов; слова со звёздочкой подсвечены оранжевым"""
    f = font(sz, wt); parts = [(w.strip('*'), w.startswith('*')) for w in words.split()]
    sp = f.getlength(' '); tw = sum(f.getlength(p) for p, _ in parts) + sp * (len(parts) - 1); x = cx - tw / 2; d = ImageDraw.Draw(im)
    for p, h in parts: d.text((x, y), p, font=f, fill=hl if h else base, anchor='lm'); x += f.getlength(p) + sp
def mascot(im, cx, by, t, pose='idle', acc='none', u=11, flip=False):
    tmp = Image.new('RGBA', (u * 40, u * 32), (0, 0, 0, 0))
    crab.draw_crab(tmp, 0, 0, t, pose, u, (1, 0), acc)
    im.paste(tmp, (int(cx - u * 19), int(by - u * 29)), tmp)

# A: логотип из разлетающихся пикселей
def title_blocks():
    mask = Image.new('L', (W, 420), 0); d = ImageDraw.Draw(mask)
    d.text((W / 2, 110), 'HDD или', font=font(190, 900), fill=255, anchor='mm'); d.text((W / 2, 300), 'SSD?', font=font(230, 900), fill=255, anchor='mm')
    a = np.array(mask); B = 14; blocks = []; rnd = random.Random(3)
    for y in range(0, 420, B):
        for x in range(0, W, B):
            if a[y:y + B, x:x + B].mean() > 110:
                ang = rnd.uniform(0, 6.28); r = rnd.uniform(500, 1400)
                blocks.append((x, y + 640, x + math.cos(ang) * r, y + 640 + math.sin(ang) * r, rnd.uniform(0, 0.8), rnd.choice([OR, OR, WHITE, GR])))
    return blocks, B
BLOCKS, BS = title_blocks()
def scene_title(im, t):
    d = ImageDraw.Draw(im)
    for tx, ty, sx, sy, dl, col in BLOCKS:
        u = ease((t - dl) / 1.6)
        if t < dl: continue
        x = lerp(sx, tx, u); y = lerp(sy, ty, u)
        c = col if u < 0.97 else (WHITE if col == WHITE or (tx // BS + ty // BS) % 5 else OR)
        d.rectangle([x, y, x + BS - 2, y + BS - 2], fill=mix(BG, c, min(1, u * 2 + 0.3)))
    if t > 2.0: txt(im, (W / 2, 1080), 'что выбрать для компьютера', 44, GRAY, 700)

# B: плашка с волной -> окно файла
def scene_wave(im, t, amp):
    u = spring(t / 0.7); w = lerp(400, 940, min(1, u)); morph = ease((t - 1.3) / 0.6)
    top = lerp(760, 560, morph); bot = lerp(1140, 1420, morph)
    cx = W / 2; box = (cx - w / 2, top, cx + w / 2, bot)
    card(im, box, mix(WHITE, DK, morph))
    if morph < 0.5:
        n = 24; bw = (w - 120) / n
        for i in range(n):
            hh = 30 + 190 * amp * (0.35 + 0.65 * abs(math.sin(t * 7 + i * 0.7))) * (0.6 + 0.4 * math.sin(i * 0.5 + t * 2))
            col = [OR, GR, (80, 140, 255)][i % 3]
            x = cx - w / 2 + 60 + i * bw; ImageDraw.Draw(im).rounded_rectangle([x, 950 - hh, x + bw - 8, 950 + hh], 5, fill=col)
        txt(im, (cx, 1100), 'слушаем...', 36, GRAY, 800)
    else:
        d = ImageDraw.Draw(im); x0, y0 = cx - w / 2, top
        d.rounded_rectangle([x0, y0, x0 + w, y0 + 70], 24, fill=(46, 46, 56)); d.rectangle([x0, y0 + 40, x0 + w, y0 + 70], fill=(46, 46, 56))
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]): d.ellipse([x0 + 28 + i * 40, y0 + 24, x0 + 48 + i * 40, y0 + 44], fill=c)
        txt(im, (cx, y0 + 35), 'сравнение.txt', 30, GRAY, 800)
        lines = [('HDD', 'диски с вращающимися пластинами'), ('SSD', 'флеш-память, без подвижных частей')]
        for i, (a, b) in enumerate(lines):
            k = ease((t - 1.9 - i * 0.5) / 0.4)
            if k > 0:
                shown = b[:int(len(b) * k)]
                txt(im, (x0 + 50, y0 + 150 + i * 110), '> ' + a, 54, OR if a == 'HDD' else GR, 900, 'lm'); txt(im, (x0 + 50, y0 + 205 + i * 110), shown, 34, WHITE, 700, 'lm')
        if (t * 2) % 2 < 1: txt(im, (x0 + 50, y0 + 380), '_', 54, WHITE, 900, 'lm')
    mascot(im, cx, top + 10, t, 'talk', 'glasses', 12)

# C: стопка карточек + счётчик
CARDS = [('Нет *подвижных* частей', 'меньше механического износа'), ('Быстрее *доступ* к данным', 'ниже задержки'), ('Устойчив к *ударам*', 'не боится тряски'), ('Работает *тихо*', 'без шума вращения')]
ACCS = ['none', 'headphones', 'cap', 'glasses']
def scene_cards(im, t):
    n = int(min(len(CARDS), t / 1.0 + 0.0001)) if t < 4.0 else len(CARDS)
    cnt = min(len(CARDS), int(t / 1.0)) if t < 4 else 4
    txt(im, (W / 2, 330), 'ПЛЮСОВ SSD', 40, GRAY, 800)
    txt(im, (W / 2, 470), str(cnt), 190, OR if cnt < 4 else GR, 900)
    for i in range(len(CARDS)):  # нижние в стопке
        if i > min(cnt, 3): break
    idx = min(len(CARDS) - 1, int(t / 1.0))
    # стопка позади
    for k in (2, 1):
        card(im, (150 + k * 12, 700 + k * 22, 930 - k * 12, 1180 + k * 22), mix(LG, BG, 0.25 * k))
    ph = (t % 1.0); flip = ease(ph / 0.3)
    sx = abs(math.cos(flip * math.pi / 2)) if ph < 0.3 else 1.0
    w = 780 * max(0.04, 1 - 0 if ph >= 0.3 else sx); cx = W / 2
    if idx < len(CARDS):
        card(im, (cx - w / 2, 640, cx + w / 2, 1180), WHITE)
        if w > 500:
            rich(im, cx, 860, CARDS[idx][0], 54, DK); txt(im, (cx, 960), CARDS[idx][1], 36, GRAY, 700)
            txt(im, (cx - 330, 700), f'{idx + 1}/4', 34, GRAY, 800, 'lm')
    mascot(im, W / 2, 1520, t, 'talk', ACCS[idx % 4], 14)

# D: зелёный фон, маскот прыгает по баблам
def scene_bubbles(im, t, tt):
    g = ease(tt / 0.4); base = mix(BG, GR, g); d = ImageDraw.Draw(im); d.rectangle([0, 0, W, H], fill=base)
    gc = mix(base, WHITE, 0.15)
    for x in range(0, W, 40): d.line([(x, 0), (x, H)], fill=gc)
    for y in range(0, H, 40): d.line([(0, y), (W, y)], fill=gc)
    B = [('минусы', 540, 520, WHITE, DK), ('дороже за гигабайт', 330, 900, DK, WHITE), ('износ при записи', 760, 1260, WHITE, OR)]
    for i, (s, bx, by, bg, fg) in enumerate(B):
        k = spring((tt - 0.25 - i * 1.15) / 0.45)
        if k <= 0: continue
        f = font(52, 900); w = f.getlength(s) + 90; h = 120 * min(1, k)
        card(im, (bx - w * k / 2, by - h / 2, bx + w * k / 2, by + h / 2), bg, 60)
        if k > 0.7: txt(im, (bx, by), s, 52, fg)
    # прыжки по баблам
    pts = [(540, 520), (330, 900), (760, 1260), (540, 1560)]
    seg = min(2.999, max(0, (tt - 0.2) / 1.15)); i = int(seg); u = seg - i
    ax, ay = pts[i]; bx_, by_ = pts[i + 1]
    x = lerp(ax, bx_, ease(u)); y = lerp(ay, by_, u) - math.sin(u * math.pi) * 260 - 70
    mascot(im, x, y + 40, t, 'wow' if u < 0.8 else 'talk', ['headphones', 'cap', 'glasses'][i % 3], 12)

# E: штамп
def scene_stamp(im, t, tt):
    cx = W / 2; k = spring(tt / 0.5)
    card(im, (120, 520, 960, 1000), WHITE)
    rich(im, cx, 640, 'Системе и программам:', 46, DK); txt(im, (cx, 730), 'обычно SSD', 90, GR, 900)
    rich(im, cx, 860, 'Архивам и фильмам:', 46, DK); txt(im, (cx, 950), 'можно HDD', 90, OR, 900)
    if tt > 1.0:
        s = 2.4 - 1.4 * spring((tt - 1.0) / 0.35); ang = -9
        st = Image.new('RGBA', (900, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
        d.rounded_rectangle([6, 6, 894, 254], 26, outline=OR, width=14); d.text((450, 130), 'ВЫБИРАЙ ПО ЗАДАЧЕ', font=font(70, 900), fill=OR, anchor='mm')
        st = st.rotate(ang, expand=True, resample=Image.BICUBIC); st = st.resize((int(st.width * s), int(st.height * s)), Image.BICUBIC)
        im.paste(st, (int(cx - st.width / 2), int(1250 - st.height / 2)), st)
    mascot(im, cx, 1700, t, 'point', 'cap', 13)

# F: прогресс-бар
def scene_progress(im, t, tt):
    p = ease(tt / 2.4); x0, x1, y = 120, 960, 1000
    card(im, (x0, y - 40, x1, y + 40), (50, 50, 60), 40, False)
    ImageDraw.Draw(im).rounded_rectangle([x0, y - 40, x0 + max(80, (x1 - x0) * p), y + 40], 40, fill=OR if p < 1 else GR)
    txt(im, (W / 2, 560), f'{int(4 + 96 * p)}%', 170, WHITE, 900)
    mascot(im, x0 + 40 + (x1 - x0 - 80) * p, y - 50, t, 'wow', 'headphones', 11)
    if p >= 1:
        k = spring((tt - 2.4) / 0.4); w = 560 * k
        card(im, (W / 2 - w / 2, 1180, W / 2 + w / 2, 1320), GR, 70)
        if k > 0.7:
            d = ImageDraw.Draw(im); cx0 = W / 2 - 190; d.line([(cx0 - 22, 1252), (cx0 - 6, 1270), (cx0 + 24, 1226)], fill=WHITE, width=12, joint='curve')
            txt(im, (W / 2 + 30, 1250), 'досмотрено', 58, WHITE, 900)

def frame(t, amp):
    im = GRID.copy()
    if t < 3.0: scene_title(im, t)
    elif t < 6.0: scene_wave(im, t - 3.0, amp)
    elif t < 10.0: scene_cards(im, t - 6.0)
    elif t < 14.0: scene_bubbles(im, t, t - 10.0)
    elif t < 16.2: scene_stamp(im, t, t - 14.0)
    else: scene_progress(im, t, t - 16.2)
    return im

def main(out):
    tmpa = tempfile.mktemp(suffix='.wav'); vt, info = build_audio(tmpa)
    N = int(DUR * FPS); env = [float(np.abs(vt[int(i / FPS * SR):int((i + 1) / FPS * SR)]).mean()) for i in range(N)]
    mx = max(env) or 1; env = [min(1, e / mx * 1.6) for e in env]
    tmpv = tempfile.mktemp(suffix='.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmpv], stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i / FPS, env[i]).tobytes())
    p.stdin.close(); p.wait()
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmpv, '-i', tmpa, '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out])
    os.remove(tmpv); os.remove(tmpa)
if __name__ == '__main__': main(sys.argv[1])
