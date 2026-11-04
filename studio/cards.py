import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import skin as SK

W, H = 1080, 1920
DARK = os.environ.get('THEME', 'light') == 'dark'
if DARK:
    BG = (8, 8, 14); GRID = (31, 31, 48); WHITE = (255, 255, 255); SURF = (15, 15, 24); SURF2 = (19, 19, 30)
    INK = (238, 238, 248); MUTED = (124, 124, 148); ACC = (130, 128, 255); ACC_SOFT = (38, 38, 78)
    BORDER = (40, 40, 60); FIELD = (25, 25, 39); LINE = (54, 54, 78); SHC = (0, 0, 0); SHC2 = (80, 72, 210)
else:
    BG = (246, 246, 251); GRID = (226, 226, 240); WHITE = (255, 255, 255); SURF = (255, 255, 255); SURF2 = (250, 250, 254)
    INK = (20, 20, 34); MUTED = (150, 150, 174); ACC = (110, 108, 255); ACC_SOFT = (234, 234, 255)
    BORDER = (233, 233, 245); FIELD = (243, 243, 250); LINE = (220, 220, 236); SHC = (80, 70, 170); SHC2 = (60, 50, 130)
BRAND = 'dobrl_almaznik'; NICK = 'Zudg.1'
OUT = HERE + '/out'; os.makedirs(OUT, exist_ok=True)

_fc = {}
def font(sz, wt=400):
    k = (int(sz), int(wt))
    if k not in _fc:
        f = ImageFont.truetype(HERE + '/Nunito.ttf', int(sz)); f.set_variation_by_axes([int(wt)]); _fc[k] = f
    return _fc[k]

def text(d, xy, s, sz, wt=400, fill=INK, anchor='mm'):
    d.text(xy, s, font=font(sz, wt), fill=fill, anchor=anchor)

def rich(d, cx, y, parts, sz):
    """parts: [(text, weight, color)] — центрированная строка с разным начертанием"""
    ws = [font(sz, w).getlength(t) for t, w, c in parts]
    x = cx - sum(ws) / 2
    for (t, w, c), wd in zip(parts, ws):
        d.text((x, y), t, font=font(sz, w), fill=c, anchor='lm'); x += wd

# ---------- фон ----------
def bg_grid():
    yy, xx = np.mgrid[0:H, 0:W]
    lines = (((xx + 20) % 96) < 2) | (((yy + 30) % 96) < 2)
    R = np.clip(1 - ((xx - W / 2) / (W * 0.72)) ** 2 - ((yy - H * 0.42) / (H * 0.5)) ** 2, 0, 1) ** 1.2
    base = np.array(BG, float); gr = np.array(GRID, float)
    out = base[None, None, :] - (base - gr)[None, None, :] * (lines * R)[..., None]
    return Image.fromarray(out.astype(np.uint8), 'RGB')

def glow(img, c, rad, color=ACC, a=0.30):
    x0, y0 = int(max(0, c[0] - rad)), int(max(0, c[1] - rad)); x1, y1 = int(min(W, c[0] + rad)), int(min(H, c[1] + rad))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    dd = np.clip(np.sqrt((xx - c[0]) ** 2 + (yy - c[1]) ** 2) / rad, 0, 1)
    al = ((1 - dd) ** 2.2 * a)[..., None]
    reg = np.array(img.crop((x0, y0, x1, y1)), float)
    reg = reg * (1 - al) + np.array(color, float)[None, None, :] * al
    img.paste(Image.fromarray(reg.astype(np.uint8), 'RGB'), (x0, y0))

def soft_shadow(img, box, r, blur=28, off=(0, 16), color=SHC, alpha=55):
    x0, y0, x1, y1 = box
    pad = blur * 3
    rx0, ry0 = int(max(0, x0 - pad)), int(max(0, y0 - pad)); rx1, ry1 = int(min(W, x1 + pad)), int(min(H, y1 + pad))
    sh = Image.new('L', (rx1 - rx0, ry1 - ry0), 0)
    ImageDraw.Draw(sh).rounded_rectangle([x0 - rx0 + off[0], y0 - ry0 + off[1], x1 - rx0 + off[0], y1 - ry0 + off[1]], r, fill=alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste(Image.new('RGB', sh.size, color), (rx0, ry0), sh)

def panel(img, box, r=44, fill=SURF, border=BORDER, shadow=True):
    if shadow: soft_shadow(img, box, r)
    ImageDraw.Draw(img).rounded_rectangle(box, r, fill=fill, outline=border, width=2)

# ---------- элементы ----------
def logo_mark(d, cx, cy, s=22):
    d.polygon([(cx - s, cy + s * 0.7), (cx - s * 0.55, cy - s * 0.8), (cx, cy + s * 0.05), (cx + s * 0.55, cy - s * 0.8), (cx + s, cy + s * 0.7), (cx + s * 0.5, cy + s * 0.7), (cx, cy + s * 0.25), (cx - s * 0.5, cy + s * 0.7)], fill=ACC)

def brand_chip(img, cx, cy, sz=30):
    d = ImageDraw.Draw(img)
    f = font(sz, 700); tw = f.getlength(BRAND); mw = sz * 1.5
    x0 = cx - (tw + mw + 14) / 2
    logo_mark(d, x0 + mw / 2, cy, sz * 0.62)
    d.text((x0 + mw + 14, cy), BRAND, font=f, fill=ACC, anchor='lm')

def avatar(size, radius=None):
    s = skin_img = SK.skin_img()
    face = s.crop((8, 8, 16, 16)); hat = s.crop((40, 8, 48, 16))
    face = Image.alpha_composite(face, hat).resize((size, size), Image.NEAREST)
    m = Image.new('L', (size, size), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius or size // 5, fill=255)
    face.putalpha(m); return face

def user_chip(img, right, cy):
    d = ImageDraw.Draw(img); av = avatar(60)
    nf = font(26, 800); sf = font(20, 600)
    tw = max(nf.getlength(NICK), sf.getlength('Minecraft'))
    x0 = right - tw - 76
    img.paste(av, (int(x0), int(cy - 30)), av)
    d.text((x0 + 76, cy - 11), NICK, font=nf, fill=INK, anchor='lm')
    d.text((x0 + 76, cy + 14), 'Minecraft', font=sf, fill=MUTED, anchor='lm')

def search_pill(img, x, y, w, h=64):
    d = ImageDraw.Draw(img); d.rounded_rectangle([x, y, x + w, y + h], h // 2.6, fill=FIELD)
    cx, cy = x + 38, y + h / 2
    d.ellipse([cx - 9, cy - 11, cx + 9, cy + 7], outline=ACC, width=3); d.line([cx + 7, cy + 5, cx + 14, cy + 13], fill=ACC, width=3)
    d.line([x + 66, y + 16, x + 66, y + h - 16], fill=LINE, width=2)
    text(d, (x + 88, cy), 'Search ...', 24, 600, MUTED, 'lm')

def dots(img, cx, y, n, cur):
    d = ImageDraw.Draw(img); gap = 26; wcur = 46
    tot = (n - 1) * gap + wcur; x = cx - tot / 2
    for i in range(n):
        if i == cur: d.rounded_rectangle([x, y - 7, x + wcur, y + 7], 7, fill=ACC); x += wcur + 10
        else: d.ellipse([x, y - 7, x + 14, y + 7], fill=(214, 214, 234)); x += gap - 2

def counter(d, x, y, i, n):
    text(d, (x, y), f'{i:02d} / {n:02d}', 26, 700, MUTED, 'rm')

def floor_shadow(img, cx, y, w=420, h=46, a=70):
    w = int(w); h = int(h); pad = 40; sh = Image.new('L', (w + pad * 2, h + pad * 2), 0)
    ImageDraw.Draw(sh).ellipse([pad, pad, pad + w, pad + h], fill=a)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    img.paste(Image.new('RGB', sh.size, SHC2), (int(cx - w / 2 - pad), int(y - h / 2 - pad)), sh)

def place(img, im, cx, floor_y, canvas=(900, 900), floor_in=860):
    img.paste(im, (int(cx - canvas[0] / 2), int(floor_y - floor_in)), im)

# ---------- мок интерфейса клиента ----------
def toggle(d, x, y, on=True):
    d.rounded_rectangle([x, y, x + 58, y + 32], 16, fill=ACC if on else (218, 218, 234))
    cx = x + (42 if on else 16); d.ellipse([cx - 12, y + 4, cx + 12, y + 28], fill=WHITE)

def color_picker(w, h):
    yy, xx = np.mgrid[0:h, 0:w]
    sat = xx / (w - 1); val = 1 - yy / (h - 1)
    hue = np.array(ACC, float)
    arr = ((255 * (1 - sat))[..., None] + hue[None, None, :] * sat[..., None]) * val[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')

def hue_bar(w, h):
    import colorsys
    row = [tuple(int(c * 255) for c in colorsys.hsv_to_rgb(x / (w - 1), 0.85, 1.0)) for x in range(w)]
    im = Image.new('RGB', (w, 1)); im.putdata(row); return im.resize((w, h))

def mock_ui(w, h):
    im = Image.new('RGB', (w, h), SURF); d = ImageDraw.Draw(im)
    sb = int(w * 0.24)
    d.rectangle([0, 0, sb, h], fill=SURF2); d.line([sb, 0, sb, h], fill=BORDER, width=2)
    text(d, (30, 44), '2D Render', 20, 700, MUTED, 'lm')
    for i, (nm, act) in enumerate([('Interface', True), ('Click GUI', False), ('Player', False), ('Visuals', False)]):
        y = 90 + i * 66
        if act: d.rounded_rectangle([18, y, sb - 18, y + 54], 16, fill=ACC_SOFT)
        d.rounded_rectangle([34, y + 14, 60, y + 40], 8, fill=ACC if act else (206, 206, 228))
        text(d, (76, y + 27), nm, 22, 700 if act else 600, INK if act else MUTED, 'lm')
    x0 = sb + 28
    search_pill(im, x0, 22, int((w - sb) * 0.52), 56)
    avs = avatar(46); im.paste(avs, (w - 28 - 150, 28), avs); text(d, (w - 28 - 94, 42), NICK, 20, 800, INK, 'lm'); text(d, (w - 28 - 94, 64), 'UID: 1', 16, 600, MUTED, 'lm')
    cw = (w - sb - 28 * 3) // 2
    mods = [('Module', 'Module description...', True), ('Module', 'Module description...', False), ('Module', 'Module description...', True), ('Module', 'Module description...', False)]
    for i, (a, b, on) in enumerate(mods):
        y = 110 + i * 96
        if y + 80 > h: break
        d.rounded_rectangle([x0, y, x0 + cw, y + 80], 18, fill=SURF2, outline=BORDER, width=2)
        text(d, (x0 + 22, y + 28), a, 22, 800, ACC, 'lm'); text(d, (x0 + 22, y + 55), b, 17, 600, MUTED, 'lm')
        toggle(d, x0 + cw - 82, y + 24, on)
    x1 = x0 + cw + 28
    d.rounded_rectangle([x1, 110, x1 + cw, 110 + 420], 18, fill=SURF2, outline=BORDER, width=2)
    text(d, (x1 + 22, 138), 'Module', 22, 800, ACC, 'lm'); text(d, (x1 + 22, 164), 'Module description...', 17, 600, MUTED, 'lm')
    text(d, (x1 + 22, 204), 'Color', 18, 700, MUTED, 'lm')
    cp = color_picker(cw - 44, 190); m = Image.new('L', cp.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cp.size[0] - 1, cp.size[1] - 1], 14, fill=255)
    im.paste(cp, (x1 + 22, 226), m)
    hb = hue_bar(cw - 44, 22); m = Image.new('L', hb.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, hb.size[0] - 1, 21], 11, fill=255)
    im.paste(hb, (x1 + 22, 438), m)
    d.ellipse([x1 + cw - 110, 262, x1 + cw - 88, 284], outline=WHITE, width=4)
    return im

def rounded_paste(img, im, xy, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    img.paste(im, (int(xy[0]), int(xy[1])), m)

# ---------- карточки ----------
TOTAL = 9
POSE_CARDS = [
    ('stand', 'Это мой скин', [('Как он выглядит в ', 400, MUTED), ('игре', 800, INK)]),
    ('walk',  'Идём дальше', [('Следующий ', 400, MUTED), ('клиент', 800, INK), (' в обзоре', 400, MUTED)]),
    ('run',   'Бегу за обновой', [('Свежие ', 400, MUTED), ('клиенты', 800, INK), (' и читы', 400, MUTED)]),
    ('point', 'Смотри сюда', [('Главное — в ', 400, MUTED), ('следующем', 800, INK), (' слайде', 400, MUTED)]),
    ('jump',  'Это топ!', [('Победитель ', 400, MUTED), ('сравнения', 800, INK)]),
    ('back',  'Что за спиной?', [('Минусы, о которых ', 400, MUTED), ('молчат', 800, INK)]),
]

def pose_card(idx, pose_name, title, sub):
    img = bg_grid(); d = ImageDraw.Draw(img)
    brand_chip(img, W // 2, 118)
    box = (60, 200, 1020, 1580); panel(img, box)
    search_pill(img, 100, 238, 430); user_chip(img, 980, 270)
    d = ImageDraw.Draw(img); d.line([100, 332, 980, 332], fill=BORDER, width=2)
    glow(img, (540, 820), 380, ACC, 0.30)
    floor_shadow(img, 540, 1236)
    sk = SK.pose(pose_name, scale=21, size=(900, 900), floor=860); place(img, sk, 540, 1236)
    d = ImageDraw.Draw(img)
    text(d, (540, 1352), title, 84, 600, INK)
    rich(d, 540, 1432, sub, 36)
    counter(d, 980, 372, idx, TOTAL)
    dots(img, 540, 1520, TOTAL, idx - 1)
    return img

def screenshot_card(idx):
    img = bg_grid(); brand_chip(img, W // 2, 118)
    box = (60, 200, 1020, 1580); panel(img, box)
    search_pill(img, 100, 238, 430); user_chip(img, 980, 270)
    d = ImageDraw.Draw(img); d.line([100, 332, 980, 332], fill=BORDER, width=2)
    # окно со «скриншотом»
    wx0, wy0, wx1, wy1 = 100, 372, 980, 940
    soft_shadow(img, (wx0, wy0, wx1, wy1), 28, blur=22, off=(0, 14), alpha=70)
    d.rounded_rectangle([wx0, wy0, wx1, wy1], 28, fill=SURF2, outline=BORDER, width=2)
    for k, c in enumerate([(255, 96, 92), (255, 189, 68), (0, 202, 78)]):
        d.ellipse([wx0 + 28 + k * 34, wy0 + 22, wx0 + 46 + k * 34, wy0 + 40], fill=c)
    shot_path = os.path.join(HERE, 'screens', 'shot1.png')
    if os.path.exists(shot_path):
        sh = Image.open(shot_path).convert('RGB'); sw, shh = wx1 - wx0 - 40, wy1 - wy0 - 76
        sh = sh.resize((sw, int(sh.size[1] * sw / sh.size[0]))).crop((0, 0, sw, shh))
    else:
        sh = mock_ui(wx1 - wx0 - 40, wy1 - wy0 - 76)
    rounded_paste(img, sh, (wx0 + 20, wy0 + 56), 18)
    d = ImageDraw.Draw(img)
    text(d, (100, 1040), 'Как выглядит', 76, 600, INK, 'lm')
    rich(d, 100 + font(36, 400).getlength('Интерфейс клиента изнутри') / 2, 1118, [('Интерфейс ', 400, MUTED), ('клиента', 800, INK), (' изнутри', 400, MUTED)], 36)
    glow(img, (810, 1150), 280, ACC, 0.22)
    floor_shadow(img, 810, 1420, 300, 38)
    sk = SK.pose('point', scale=19, size=(900, 900), floor=860); place(img, sk, 810, 1420)
    dots(img, 540, 1520, TOTAL, idx - 1)
    counter(ImageDraw.Draw(img), 980, 1040, idx, TOTAL)
    return img

def cta_card(idx):
    img = bg_grid(); brand_chip(img, W // 2, 118)
    box = (60, 200, 1020, 1580); panel(img, box)
    glow(img, (540, 700), 420, ACC, 0.32)
    av = avatar(360, 56); soft_shadow(img, (360, 520, 720, 880), 56, blur=26, off=(0, 20), alpha=80)
    img.paste(av, (360, 520), av)
    d = ImageDraw.Draw(img)
    text(d, (540, 1040), 'Подписывайся', 104, 600, INK)
    text(d, (540, 1130), '@' + BRAND, 46, 800, ACC)
    rich(d, 540, 1210, [('Новые сравнения ', 400, MUTED), ('клиентов', 800, INK)], 36)
    d.rounded_rectangle([340, 1280, 740, 1372], 36, fill=ACC)
    text(d, (540, 1326), 'Подписаться', 38, 800, WHITE)
    dots(img, 540, 1520, TOTAL, idx - 1)
    return img

# ---------- live photo (карточка №1) ----------
T = 3.0; FPSL = 30
_live = {}
def live_base():
    if 'base' in _live: return _live['base']
    img = bg_grid(); d = ImageDraw.Draw(img)
    brand_chip(img, W // 2, 212, 32)
    # заголовок (рисуем отдельно, чтобы получить маску для шиммера)
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    text(md, (540, 338), 'Minecraft Clients', 126, 300, 255)
    d.text((540, 338), 'Minecraft Clients', font=font(126, 300), fill=INK, anchor='mm')
    rich(d, 540, 448, [('Честные ', 400, MUTED), ('сравнения', 800, INK), (' клиентов и читов', 400, MUTED)], 38)
    # панель интерфейса снизу (обрезана краем кадра)
    ph = 760; px0, py0 = 60, 1330
    soft_shadow(img, (px0, py0, 1020, py0 + ph), 44)
    d.rounded_rectangle((px0, py0, 1020, py0 + ph), 44, fill=SURF, outline=BORDER, width=2)
    ui = mock_ui(960 - 40, ph - 40); rounded_paste(img, ui, (px0 + 20, py0 + 20), 30)
    _live['base'] = img; _live['mask'] = mask.crop((0, 260, W, 420))
    return img

def live_frame(k):
    t = k / FPSL; ph = 2 * math.pi * t / T
    img = live_base().copy()
    # свечение под скином (пульсирует)
    glow(img, (540, 880), 360 + 18 * math.sin(ph), ACC, 0.28 + 0.05 * math.sin(ph))
    bob = 0.5 * math.sin(2 * ph)
    floor_shadow(img, 540, 1245, 400 - 12 * math.sin(2 * ph), 44, 70)
    pose = dict(turn=-8 + 9 * math.sin(ph), roll=3 + 2 * math.sin(2 * ph), rarm=(0, 138 + 16 * math.sin(2 * ph)),
                larm=(0, 6 + 2 * math.sin(ph)), bob=bob, nod=2 * math.sin(2 * ph), rleg=(0, 0), lleg=(0, 0))
    sk = SK.render(pose=pose, yaw=-16 + 11 * math.sin(ph), tilt=8, scale=22, size=(900, 900), floor=860)
    img.paste(sk, (90, 1245 - 860), sk)
    # частицы
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    rnd = np.random.default_rng(5)
    for i in range(16):
        bx = rnd.uniform(110, 970); by = rnd.uniform(560, 1250); s = rnd.uniform(14, 34); sp = rnd.integers(1, 3); phi = rnd.uniform(0, 6.28)
        y = by - 26 * math.sin(sp * ph + phi) - 14 * math.sin(ph + phi); x = bx + 12 * math.sin(ph + phi * 2)
        al = int(110 + 70 * math.sin(sp * ph + phi))
        od.rounded_rectangle([x, y, x + s, y + s], s / 4, fill=ACC + (al,))
    img.paste(ov, (0, 0), ov)
    # шиммер по заголовку
    cxb = -300 + (W + 600) * ((t / T) % 1.0)
    band = Image.new('L', (W, 160), 0); bd = ImageDraw.Draw(band)
    for off in range(-120, 121, 6):
        bd.line([cxb + off + 80, 0, cxb + off - 80, 160], fill=int(255 * max(0, 1 - abs(off) / 120)), width=8)
    m = ImageChops.multiply(_live['mask'], band)
    img.paste(Image.new('RGB', (W, 160), ACC), (0, 260), m)
    return img

def write_live(path):
    tmp = path + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPSL),
                          '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-f', 'mp4', tmp],
                         stdin=subprocess.PIPE)
    n = int(T * FPSL)
    for k in range(n): p.stdin.write(live_frame(k).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, path)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'static':
        for i, (pn, title, sub) in enumerate(POSE_CARDS, start=2):
            pose_card(i, pn, title, sub).save(f'{OUT}/{i:02d}_{pn}.png')
        screenshot_card(8).save(f'{OUT}/08_screenshot.png'); cta_card(9).save(f'{OUT}/09_cta.png')
    elif mode == 'poster':
        live_frame(int(sys.argv[2])).save(f'{OUT}/01_live_poster.png')
    elif mode == 'live':
        write_live(f'{OUT}/01_live.mp4')
