import sys, math, subprocess, numpy as np
from multiprocessing import Pool
from news_pack3 import *
import steam_video as SV
OD = HERE + '/out_steam'
SKW, SKH, SKF = 1100, 1220, 1450   # проверяется ниже
import cards2
SKW, SKH, SKF = cards2.SKW, cards2.SKH, cards2.SKF
def ease(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def back(x):
    x = max(0., min(1., x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

class Scene:
    def __init__(s, dur, elems, skin=None, base_fn=None):
        s.dur = dur; s.skin = skin; s.base = bg_grid(); s.elems = []
        base = s.base
        for (fn, t0, kind) in elems:
            tmp = base.copy(); fn(tmp)
            diff = ImageChops.difference(tmp, base).convert('L').point(lambda v: min(255, v * 10))
            bb = diff.getbbox()
            if not bb: continue
            bb = (0, max(0, bb[1] - 6), W, min(H, bb[3] + 6))
            s.elems.append(dict(img=tmp.crop(bb), mask=diff.crop(bb), y=bb[1], t0=t0, kind=kind))
        foot3(s.base)
    def skin_frame(s, k):
        name, cx, fy, sc = s.skin
        P = SK.POSES[name]; q = dict(P['pose']); ph = 2 * math.pi * (k % 60) / 60
        q.update(turn=q.get('turn', 0) + 6 * math.sin(ph), bob=0.3 * math.sin(2 * ph), nod=q.get('nod', 0) + 2 * math.sin(2 * ph))
        return SK.render(pose=q, yaw=P['yaw'] + 5 * math.sin(ph), tilt=P['tilt'], scale=sc, size=(SKW, SKH), floor=SKF, ss=2)
    def frame(s, t, skimg):
        img = s.base.copy(); ph = 2 * math.pi * t / 3
        glow(img, (800, 1150), 470 + 22 * math.sin(ph), ACC, 0.18 + 0.05 * math.sin(ph))
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); rnd = np.random.default_rng(7)
        for i in range(16):
            bx = rnd.uniform(40, 1040); by = rnd.uniform(500, 1650); sz = rnd.uniform(10, 26); sp = int(rnd.integers(1, 3)); phi = rnd.uniform(0, 6.28)
            yy = by - 30 * math.sin(sp * ph + phi) - 40 * t; yy = 400 + (yy - 400) % 1250; al = int(70 + 60 * math.sin(sp * ph + phi))
            od.rectangle([bx, yy, bx + sz, yy + sz], fill=ACC + (al,))
        img.paste(ov, (0, 0), ov)
        for e in s.elems:
            x = (t - e['t0']) / 0.45
            if x <= 0: continue
            a = ease(x * 1.4); dx = int(-140 * (1 - back(x))) if e['kind'] != 'fade' else 0
            if e['kind'] == 'shake' and 0 < t - e['t0'] < 1.2: dx += int(7 * math.sin((t - e['t0']) * 45) * (1 - (t - e['t0']) / 1.2))
            m = e['mask'].point(lambda v, a=a: int(v * a))
            img.paste(e['img'], (dx, e['y']), m) if dx == 0 else img.paste(e['img'].crop((max(0, -dx), 0, W - max(0, dx), e['img'].size[1])) if dx < 0 else e['img'], (max(0, dx), e['y']), (m.crop((max(0, -dx), 0, W - max(0, dx), m.size[1])) if dx < 0 else m))
        if s.skin and t > 0.3:
            x = ease((t - 0.3) / 0.6); dy = int(260 * (1 - x))
            a = skimg.split()[3].point(lambda v, x=x: int(v * x))
            skimg.putalpha(a); img.paste(skimg, (int(s.skin[1] - SKW / 2), int(s.skin[2] - SKF) + dy), skimg)
        return img

def pills(items, y0, w, t0, step=0.55, gap=112):
    out = []
    for i, (lab, kind) in enumerate(items):
        out.append((lambda im, i=i, lab=lab, kind=kind: pill_row(im, 80, y0 + i * gap, w, 92, lab, kind, ACC), t0 + i * step, 'shake' if kind == 1 else 'slide'))
    return out

def mk(a, b, tg, items, notes=None, skin=None, hs=130, w=900):
    sz = fit_size([a, b], 900, hs); y = TOP + 0.705 * sz + 0.95 * sz
    el = [(lambda im: SV.tag(im, tg), 0.0, 'fade'), (lambda im: head3(im, a, b, hs), 0.1, 'slide')]
    el += pills(items, y + 60, w, 0.7)
    tend = 0.7 + len(items) * 0.55 + 0.2
    if notes: el.append((lambda im: SV.sub(im, y + 60 + len(items) * 112 + 20, notes), tend, 'fade'))
    dur = tend + 2.2
    return Scene(dur, el, skin)

def cover():
    def head(im):
        d = ImageDraw.Draw(im); a, b = 'Не отдай', 'аккаунт'; sz = fit_size([a, b], 900, 170); y0 = TOP + 60 + 0.705 * sz; y1 = y0 + 0.95 * sz
        shadow_text(d, (80, y0), a, sz); shadow_text(d, (80, y1), b, sz, 900, ACC)
    def sub(im):
        d = ImageDraw.Draw(im); sz = fit_size(['Не отдай', 'аккаунт'], 900, 170); y1 = TOP + 60 + 0.705 * sz + 0.95 * sz
        shadow_text(d, (80, y1 + 70), '4 схемы мошенников', 34, 700, (170, 170, 200), off=4); shadow_text(d, (80, y1 + 120), 'и как защититься', 34, 700, (170, 170, 200), off=4)
    return Scene(4.2, [(lambda im: SV.tag(im, 'STEAM · БЕЗОПАСНОСТЬ'), 0, 'fade'), (head, 0.1, 'slide'), (sub, 0.9, 'fade')], ('guard', 850, 1640, 17))
def cta(txt='Сохрани, чтобы не потерять аккаунт'):
    def a(im):
        d = ImageDraw.Draw(im); t = 'Подписывайся'; sz = fit_size([t], 940, 118); shadow_text(d, (540 - font(sz, 900).getlength(t) / 2, 1140), t, sz)
        shadow_text(d, (540 - font(42, 800).getlength('@' + BRAND) / 2, 1240), '@' + BRAND, 42, 800, ACC, off=4)
    def b(im):
        d = ImageDraw.Draw(im); t2 = txt; shadow_text(d, (540 - font(28, 600).getlength(t2) / 2, 1320), t2, 28, 600, (170, 170, 200), off=3)
    def c(im):
        d = ImageDraw.Draw(im); soft_shadow(im, (300, 1390, 780, 1486), 38, blur=16, off=(0, 10), color=ACC, alpha=110)
        d.rounded_rectangle([300, 1390, 780, 1486], 38, fill=ACC); d.text((543, 1441), 'Подписаться', font=font(38, 800), fill=(20, 18, 60), anchor='mm'); d.text((540, 1438), 'Подписаться', font=font(38, 800), fill=WHITE, anchor='mm')
    return Scene(4.2, [(a, 0.5, 'slide'), (b, 0.9, 'fade'), (c, 1.3, 'slide')], ('wave', 540, 1000, 19))

def scenes():
    return [cover(),
        mk('Схема 1', 'Фишинг', 'STEAM · СХЕМЫ', [('Поддельный сайт входа', 2), ('Фейковые «турниры»', 2), ('Сканирование фейк-QR', 2)], ['Цель: украсть логин и', 'код Steam Guard'], ('think', 880, 1660, 16)),
        mk('Схема 2', 'API-скам', 'STEAM · СХЕМЫ', [('1. Ты шлёшь трейд', 0), ('2. Скамер с API-ключом', 2), ('   отменяет оффер', 2), ('3. Клон профиля шлёт', 2), ('   встречный оффер', 2), ('4. Ты принимаешь', 1)], ['Смотри уровень и дату', 'регистрации партнёра'], None, 120),
        mk('Схема 3', 'Фейк-поддержка', 'STEAM · СХЕМЫ', [('Пишут в ЛС от «Steam»', 2), ('Пугают баном', 2), ('«Срочно передай скины»', 1)], ['Поддержка не просит', 'передавать предметы'], ('present', 890, 1660, 16), 120),
        mk('Схема 4', 'Вирусы', 'STEAM · СХЕМЫ', [('.exe под видом читов', 2), ('Софт «для обхода»', 2), ('Крадёт сессии и пароли', 1)], ['Файлы с чужих ссылок', 'не запускай'], ('inspect', 890, 1660, 16)),
        mk('Если', 'взломали', 'STEAM · ЧТО ДЕЛАТЬ', [('1. Отозвать API-ключ', 0), ('2. Сменить пароли:', 0), ('   Steam и почта', 0), ('3. Выйти на всех устройствах', 0), ('4. Новая trade-ссылка', 0)], ['API-ключ: steamcommunity.com', '/dev/apikey'], None, 130),
        mk('Как', 'защититься', 'STEAM · ЗАЩИТА', [('Мобильный Steam Guard', 0), ('Проверяй адрес сайта', 0), ('Входи только на сайт', 0), ('   steampowered.com', 0), ('Не ставь файлы с читов', 0)], None, ('confident', 890, 1660, 15), 130),
        cta()]

SC = None
def _skin(a):
    i, k = a; return SC[i].skin_frame(k)
if __name__ == '__main__':
    SC = scenes(); FPS = 30; TR = 0.35
    with Pool(4) as pool:
        skins = {}
        for i, s in enumerate(SC):
            if s.skin: skins[i] = pool.map(_skin, [(i, k) for k in range(60)])
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OD + '/steam_anim.mp4'], stdin=subprocess.PIPE)
    prev = None; gk = 0
    for i, s in enumerate(SC):
        for k in range(int(s.dur * FPS)):
            t = k / FPS; sk = skins[i][gk % 60].copy() if i in skins else None
            im = s.frame(t, sk)
            if prev is not None and t < TR:
                x = ease(t / TR); off = int(W * x)
                canvas = Image.new('RGB', (W, H)); canvas.paste(prev, (-off, 0)); canvas.paste(im, (W - off, 0)); im = canvas
            p.stdin.write(im.tobytes()); gk += 1; last = im
        prev = s.frame(s.dur - 0.01, skins[i][0].copy() if i in skins else None)
    p.stdin.close(); print(p.wait())
