"""Набор карточек «A vs B»: композиция референса Riff vs Liner + дизайн UI-референса (Nunito, белая сетка, фиолетовый акцент).
Карточка №1 всегда live photo (зацикленный mp4)."""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import skin as SK
from cards import *   # helpers: bg_grid, glow, soft_shadow, font, text, rich, avatar, mock_ui, ...

OUT2 = HERE + ('/out_dark' if DARK else '/out2'); os.makedirs(OUT2, exist_ok=True)
SHADOW = (42, 42, 72) if DARK else (208, 208, 230)
LOGO = {'Lunar': (70, 160, 255), 'Laby': (175, 100, 255), 'Modrinth': (40, 200, 110)}

# ---------- кирпичики ----------
SKW, SKH, SKF = 1000, 1150, 1050   # большой холст: шапка/руки вверх не обрезаются
def put_skin(img, name, cx, floor_y, sc, pose_override=None, **kw):
    if pose_override is None: sk = SK.pose(name, scale=sc, size=(SKW, SKH), floor=SKF, **kw)
    else: sk = SK.render(pose=pose_override['pose'], yaw=pose_override['yaw'], tilt=pose_override['tilt'], scale=sc, size=(SKW, SKH), floor=SKF, **kw)
    img.paste(sk, (int(cx - SKW / 2), int(floor_y - SKF)), sk)
    return sk

def shadow_text(d, xy, s, sz, wt=900, fill=INK, off=9, anchor='ls'):
    f = font(sz, wt)
    d.text((xy[0] + off, xy[1] + off), s, font=f, fill=SHADOW, anchor=anchor)
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def fit_size(strings, maxw, start=250, wt=900):
    sz = start
    while sz > 60 and max(font(sz, wt).getlength(s) for s in strings) > maxw: sz -= 4
    return sz

def badge(img, cx, cy, key, d=116):
    ss = 3; D = d * ss
    c = Image.new('RGBA', (D, D), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
    lp = os.path.join(HERE, 'logos', key.lower() + '.png')
    if not os.path.exists(lp): return False   # нет настоящего лого - нет бейджа (никаких букв-заглушек)
    cd.ellipse([0, 0, D - 1, D - 1], fill=INK + (255,)); cd.ellipse([D * 0.06, D * 0.06, D * 0.94, D * 0.94], fill=(22, 22, 36, 255))
    lg = Image.open(lp).convert('RGBA'); lg.thumbnail((int(D * 0.60), int(D * 0.60)), Image.LANCZOS)
    if key.lower() == 'modrinth':   # иконка уже со своим тёмным фоном - обрезаем по кругу
        lg = lg.resize((int(D * 0.78),) * 2, Image.LANCZOS); mk = Image.new('L', lg.size, 0); ImageDraw.Draw(mk).ellipse([0, 0, lg.size[0] - 1, lg.size[1] - 1], fill=255)
        lg.putalpha(ImageChops.multiply(lg.getchannel('A'), mk))
    c.paste(lg, ((D - lg.size[0]) // 2, (D - lg.size[1]) // 2), lg)
    c = c.reduce(ss)
    sh = Image.new('L', (d + 60, d + 60), 0); ImageDraw.Draw(sh).ellipse([30, 38, 30 + d, 38 + d], fill=70); sh = sh.filter(ImageFilter.GaussianBlur(9))
    img.paste(Image.new('RGB', sh.size, SHC2), (int(cx - d / 2 - 30), int(cy - d / 2 - 30)), sh)
    img.paste(c, (int(cx - d / 2), int(cy - d / 2)), c)
    return True

def handle(img, x=80, y=1470):
    d = ImageDraw.Draw(img)
    d.text((x, y), '@' + BRAND, font=font(38, 700), fill=INK, anchor='lm')

def ui_card(img, x, y, w=470, h=250, fl=0):
    """плавающая карточка модуля — привет из UI-референса"""
    y += fl
    soft_shadow(img, (x, y, x + w, y + h), 30, blur=24, off=(0, 16), alpha=70)
    d = ImageDraw.Draw(img); d.rounded_rectangle([x, y, x + w, y + h], 30, fill=SURF, outline=BORDER, width=2)
    text(d, (x + 30, y + 40), 'Module', 28, 800, ACC, 'lm'); text(d, (x + 30, y + 74), 'Module description...', 20, 600, MUTED, 'lm')
    toggle(d, x + w - 92, y + 30, True)
    cp = color_picker(w - 60, 100); rounded_paste(img, cp, (x + 30, y + 108), 16)
    hb = hue_bar(w - 60, 18); rounded_paste(img, hb, (x + 30, y + 214), 9)

def title_block(img, a, b, left=80, top=250, maxw=700, start=250):
    """возвращает (маска заголовка, позиции для бейджей, y субтитра)"""
    sz = fit_size([a, b], maxw, start); vs = int(sz * 0.62)
    b1 = top + 0.705 * sz; b2 = b1 + 0.66 * sz; b3 = b2 + 0.24 * sz + 0.705 * sz
    d = ImageDraw.Draw(img); m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
    shadow_text(d, (left, b1), a, sz); shadow_text(d, (left, b2), 'vs', vs, 900, ACC, off=6); shadow_text(d, (left, b3), b, sz)
    for dd in (md,):
        dd.text((left, b1), a, font=font(sz, 900), fill=255, anchor='ls'); dd.text((left, b3), b, font=font(sz, 900), fill=255, anchor='ls')
    wa = font(sz, 900).getlength(a); wb = font(sz, 900).getlength(b)
    return m, dict(a=(left + wa + 26, b1 - 0.62 * sz), b=(left + wb + 26, b3 - 0.30 * sz), sub=b3 + 112, size=sz)

# ---------- карточка 1: VS-обложка (live photo) ----------
TL = 3.0; FP = 30
_c = {}
def cover_base(a='Lunar', b='Laby', sub='какой лучше?'):
    key = (a, b)
    if _c.get('key') == key: return _c
    img = bg_grid(); glow(img, (800, 1250), 520, ACC, 0.20)
    m, pos = title_block(img, a, b)
    d = ImageDraw.Draw(img)
    shadow_text(d, (80, pos['sub']), sub, 78, 800, INK, off=5)
    nd = ImageDraw.Draw(img)
    for i, ln in enumerate(['Оба бесплатные,', 'но нужен лицензионный', 'аккаунт Minecraft']):
        nd.text((80, 1250 + i * 50), ln, font=font(38, 700), fill=MUTED, anchor='ls')
    handle(img)
    bb = m.getbbox()
    _c.update(key=key, img=img, mask=m.crop((0, bb[1] - 10, W, bb[3] + 10)), mtop=bb[1] - 10, pos=pos, a=a, b=b)
    return _c

def cover_frame(k, a='Lunar', b='Laby'):
    c = cover_base(a, b); t = k / FP; ph = 2 * math.pi * t / TL
    img = c['img'].copy(); pos = c['pos']
    glow(img, (800, 1240), 470 + 22 * math.sin(ph), ACC, 0.18 + 0.05 * math.sin(ph))
    # частицы
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); rnd = np.random.default_rng(11)
    for i in range(14):
        bx = rnd.uniform(560, 1020); by = rnd.uniform(900, 1700); s = rnd.uniform(12, 30); sp = int(rnd.integers(1, 3)); phi = rnd.uniform(0, 6.28)
        y = by - 22 * math.sin(sp * ph + phi); x = bx + 10 * math.sin(ph + phi * 2); al = int(100 + 70 * math.sin(sp * ph + phi))
        od.rounded_rectangle([x, y, x + s, y + s], s / 4, fill=ACC + (al,))
    img.paste(ov, (0, 0), ov)
    # скин (крупный план, ноги за кадром)
    P = SK.POSES['think']; q = dict(P['pose']); sn = math.sin(ph); s2 = math.sin(2 * ph)
    q.update(turn=-12 + 7 * sn, roll=6 + 2 * s2, nod=5 + 3 * s2, rarm=(32 + 2 * s2, 6, 118 + 6 * sn, 0), larm=(52, 2, 70 + 3 * s2, 42), bob=0.3 * s2)
    sk = SK.render(pose=q, yaw=-18 + 6 * sn, tilt=7, scale=31, size=(1100, 1220), floor=1450, ss=2)
    img.paste(sk, (860 - 550, 560), sk)
    # бейджи
    badge(img, pos['a'][0] + 40, pos['a'][1] + 8 * math.sin(ph), c['a']); badge(img, pos['b'][0] + 40, pos['b'][1] + 8 * math.sin(ph + 2.1), c['b'])
    # шиммер по заголовку
    mk = c['mask']; hh = mk.size[1]; cxb = -300 + (W + 600) * ((t / TL) % 1.0)
    band = Image.new('L', (W, hh), 0); bd = ImageDraw.Draw(band)
    for off in range(-120, 121, 6): bd.line([cxb + off + 90, 0, cxb + off - 90, hh], fill=int(255 * max(0, 1 - abs(off) / 120)), width=8)
    img.paste(Image.new('RGB', (W, hh), ACC), (0, c['mtop']), ImageChops.multiply(mk, band))
    return img

def write_cover(path, a='Lunar', b='Laby'):
    tmp = path + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FP), '-i', '-',
                          '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-f', 'mp4', tmp], stdin=subprocess.PIPE)
    for k in range(int(TL * FP)): p.stdin.write(cover_frame(k, a, b).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, path)

# ---------- карточки 2..: клиенты, скриншоты, вердикт, CTA ----------
AMBER = (255, 176, 64)
CHIPS = {
    'Lunar': [('Бесплатный', 0), ('Нужна лицензия Minecraft', 2), ('Много модулей из коробки', 0), ('Минус: косметика грузит FPS', 1)],
    'Laby': [('Бесплатный', 0), ('Нужна лицензия Minecraft', 2), ('100+ встроенных модов', 0), ('Версии от 1.8.9 и новее', 0)],
    'Modrinth': [('Открытый код', 0), ('Официально: нужна лицензия', 2), ('Сборки за пару кликов', 0), ('Моды прямо с Modrinth', 0)],
}
NOTE = {'Modrinth': ['Неофициальные форки с офлайн-аккаунтом', 'делают сторонние люди, не Modrinth.', 'Ставишь на свой риск.']}
TAG = {'Lunar': 'Lunar Client', 'Laby': 'LabyMod', 'Modrinth': 'Modrinth App'}

def pill_row(img, x, y, w, h, label, kind=0, accent=ACC):
    d = ImageDraw.Draw(img)
    bad = kind == 1
    soft_shadow(img, (x, y, x + w, y + h), h // 2.6, blur=14, off=(0, 8), alpha=40)
    d.rounded_rectangle([x, y, x + w, y + h], h // 2.6, fill=(214, 68, 68) if bad else SURF, outline=None if bad else (AMBER if kind == 2 else BORDER), width=2)
    if not bad: d.ellipse([x + 26, y + h / 2 - 11, x + 48, y + h / 2 + 11], fill=AMBER if kind == 2 else accent)
    f = 33
    while font(f, 700).getlength(label) > w - (92 if not bad else 60) and f > 18: f -= 2
    d.text((x + (72 if not bad else 30), y + h / 2), label, font=font(f, 700), fill=WHITE if bad else INK, anchor='lm')

def client_card(key, pose_name, num, sx=855, sc=26, floor_y=1480):
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20)
    d = ImageDraw.Draw(img)
    sz = fit_size([key], 600, 220)
    shadow_text(d, (80, 250 + 0.705 * sz), key, sz)
    badge(img, 80 + font(sz, 900).getlength(key) + 70, 250 + 0.1 * sz, key)
    d.rounded_rectangle([80, 250 + 0.705 * sz + 40, 80 + 290, 250 + 0.705 * sz + 100], 22, fill=ACC)
    text(d, (80 + 145, 250 + 0.705 * sz + 70), f'ЛАУНЧЕР #{num}', 28, 800, WHITE)
    y0 = 250 + 0.705 * sz + 150
    for i, (lab, kind) in enumerate(CHIPS[key]):
        pill_row(img, 80, y0 + i * 118, 520, 92, lab, kind, LOGO[key])
    for i, ln in enumerate(NOTE.get(key, [])):
        d.text((80, y0 + 4 * 118 + 36 + i * 36), ln, font=font(27, 600), fill=MUTED, anchor='ls')
    floor_shadow(img, sx, floor_y, 330, 40)
    put_skin(img, pose_name, sx, floor_y, sc)
    handle(img); return img

def window(img, x0, y0, w, shot, title):
    d = ImageDraw.Draw(img); sw = w - 40
    s = shot.resize((sw, int(shot.size[1] * sw / shot.size[0])), Image.LANCZOS)
    y1 = y0 + 54 + s.size[1] + 22
    soft_shadow(img, (x0, y0, x0 + w, y1), 30, blur=24, off=(0, 18), alpha=75)
    d.rounded_rectangle([x0, y0, x0 + w, y1], 30, fill=SURF2, outline=BORDER, width=2)
    for k2, cc in enumerate([(255, 96, 92), (255, 189, 68), (0, 202, 78)]): d.ellipse([x0 + 28 + k2 * 34, y0 + 20, x0 + 46 + k2 * 34, y0 + 38], fill=cc)
    d.text((x0 + w - 28, y0 + 29), title, font=font(26, 700), fill=MUTED, anchor='rm')
    rounded_paste(img, s, (x0 + 20, y0 + 54), 18)
    return y1

def shot_card():
    img = bg_grid(); glow(img, (800, 1100), 480, ACC, 0.18); d = ImageDraw.Draw(img)
    shadow_text(d, (80, 250 + 0.705 * 120), 'Как выглядит', 120, 900, INK, off=7)
    parts = [('Меню ', 400, MUTED), ('клиентов', 800, INK), (' изнутри', 400, MUTED)]
    rich(d, 80 + sum(font(38, w).getlength(t) for t, w, c in parts) / 2, 470, parts, 38)
    mr = Image.open(os.path.join(HERE, 'screens', 'modrinth.png')).convert('RGB')
    lb = Image.open(os.path.join(HERE, 'screens', 'laby.png')).convert('RGB')
    y1 = window(img, 80, 540, 920, mr, 'Modrinth App')
    y2 = window(img, 80, y1 + 36, 600, lb, 'LabyMod')
    text(d, (80 + 300, y2 + 36), 'Lunar: скриншот добавлю позже', 26, 600, MUTED)
    floor_shadow(img, 850, 1830, 260, 36)
    put_skin(img, 'inspect', 850, 1830, 22)
    handle(img, y=1850); return img

def verdict_card():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.22); d = ImageDraw.Draw(img)
    shadow_text(d, (80, 250 + 0.705 * 150), 'Выбор за вами,', 150, 900, INK, off=7) if False else None
    shadow_text(d, (80, 250 + 0.705 * 170), 'Выбор', 170); shadow_text(d, (80, 250 + 0.705 * 170 + 0.95 * 170), 'за вами', 170)
    text(d, (80, 250 + 0.705 * 170 + 0.95 * 170 + 80), 'но я бы посоветовал:', 40, 700, MUTED, 'lm')
    rows = [('Моды и открытый код', 'Modrinth', True), ('Упор на PvP и друзей', 'Lunar', False), ('Много функций сразу', 'Laby', False)]
    for i, (a, b, rec) in enumerate(rows):
        y = 880 + i * 132; cl = LOGO[b]
        soft_shadow(img, (80, y, 640, y + 108), 38, blur=14, off=(0, 8), alpha=60 if rec else 40)
        d.rounded_rectangle([80, y, 640, y + 108], 38, fill=ACC_SOFT if rec else SURF, outline=ACC if rec else BORDER, width=4 if rec else 2)
        d.ellipse([104, y + 40, 132, y + 68], fill=cl)
        text(d, (150, y + 36), a, 26, 700, INK, 'lm'); text(d, (150, y + 76), b, 34, 900, cl, 'lm')
        if rec: d.rounded_rectangle([510, y + 30, 620, y + 78], 20, fill=ACC); text(d, (565, y + 54), 'мой топ', 22, 800, WHITE)
    floor_shadow(img, 905, 1600, 300, 40)
    put_skin(img, 'confident', 905, 1600, 22)
    handle(img, y=1780); return img

def cta_card():
    img = bg_grid(); glow(img, (540, 640), 460, ACC, 0.30); d = ImageDraw.Draw(img)
    floor_shadow(img, 540, 840, 300, 36)
    put_skin(img, 'wave', 540, 840, 23)
    shadow_text(d, (540 - font(118, 900).getlength('Подписывайся') / 2, 1010), 'Подписывайся', 118, 900)
    text(d, (540, 1120), '@' + BRAND, 46, 800, ACC)
    rich(d, 540, 1200, [('Новые сравнения ', 400, MUTED), ('клиентов', 800, INK)], 38)
    soft_shadow(img, (330, 1280, 750, 1376), 38, blur=16, off=(0, 10), color=ACC, alpha=110)
    d.rounded_rectangle([330, 1280, 750, 1376], 38, fill=ACC); text(d, (540, 1328), 'Подписаться', 38, 800, WHITE)
    return img

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'static':
        client_card('Lunar', 'guard', 1, sx=880, sc=24).save(f'{OUT2}/02_lunar.png'); client_card('Laby', 'present', 2, sx=915, sc=23).save(f'{OUT2}/03_laby.png')
        client_card('Modrinth', 'build', 3, sx=890, sc=23, floor_y=1500).save(f'{OUT2}/04_modrinth.png')
        shot_card().save(f'{OUT2}/05_screens.png'); verdict_card().save(f'{OUT2}/06_verdict.png'); cta_card().save(f'{OUT2}/07_cta.png')
    elif mode == 'poster': cover_frame(int(sys.argv[2])).save(f'{OUT2}/01_live_poster.png')
    elif mode == 'live': write_cover(f'{OUT2}/01_live.mp4')
