"""DOORS ачивки, часть 1: Not Five Stars. Monocraft, тени, безопасная зона TikTok."""
import sys, os, math
from news_pack3 import *
import news_pack as NP
OD = HERE + '/out_doors1'; os.makedirs(OD, exist_ok=True)
GREY = (150, 150, 180)

def sub(img, y, lines, col=GREY, sz=28):
    d = ImageDraw.Draw(img)
    for i, t in enumerate(lines): shadow_text(d, (80, y + i * (sz + 14)), t, sz, 600, col, off=3)
    return y + len(lines) * (sz + 14)

def tag(img, n=1):
    d = ImageDraw.Draw(img); t = f'DOORS · ЧАСТЬ {n}/4'
    shadow_text(d, (80, TOP - 42), t, 28, 800, GREY, off=3)

def c_req():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head3(img, 'Что нужно', 'сделать', 130); tag(img)
    rows(img, y + 60, [('Пройти Отель до конца', 0), ('Бонус модификаторов', 1), ('минимум 50%', 1), ('Работает и на приватке', 0)], 700, 112)
    sub(img, y + 60 + 4 * 112 + 30, ['Бонус считается по сумме', 'включённых модификаторов'])
    skin_floor(img, 'present', 900, 1640, 18); foot3(img); return img

MODS = [('Bad Electrical Work', '+10%'), ('Wet Floor', '+10%'), ('Bad Time', '+10%'), ('Wear And Tear', '+5%'), ('Gone Fishing', '+5%'), ('Tripped', '+5%'), ('Injuries', '+5%')]
def c_build(n=7):
    img = bg_grid(); glow(img, (830, 1100), 460, ACC, 0.20); y = head3(img, 'Сборка', 'на 50%', 130); tag(img)
    d = ImageDraw.Draw(img); y0 = y + 50
    for i, (nm, p) in enumerate(MODS[:n]):
        yy = y0 + i * 108; pill_row(img, 80, yy, 920, 92, nm, 0, ACC)
        shadow_text(d, (1000 - 40 - font(34, 900).getlength(p), yy + 62), p, 34, 900, AMBER, off=3)
    if n == 7: sub(img, y0 + 7 * 108 + 20, ['10+10+10+5+5+5+5 = 50', 'Сумма по гайду ProGameGuides'], AMBER, 28)
    foot3(img); return img

def c_steps():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head3(img, 'Как', 'пройти', 150); tag(img)
    rows(img, y + 60, [('1. Включи 7 модификаторов', 0), ('2. Проверь сумму: 50%', 0), ('3. Нажми старт', 0), ('4. Дойди до финала', 0), ('   и досмотри ролик', 0)], 900, 112)
    skin_floor(img, 'confident', 890, 1660, 17); foot3(img); return img

def c_tips():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head3(img, 'Советы', 'по сборке', 130); tag(img)
    rows(img, y + 60, [('Можно менять на равные', 0), ('по % модификаторы', 0), ('Лёгкие не бери: проще', 0), ('жить со страшными', 0), ('Проценты проверь в игре', 2)], 900, 112)
    sub(img, y + 60 + 5 * 112 + 20, ['Модификаторы открываются после', 'побега из Отеля. Список из гайдов 2024'], GREY, 26)
    foot3(img); return img

def c_series():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head3(img, 'Серия', 'из 4 частей', 130); tag(img)
    rows(img, y + 60, [('1. Not Five Stars', 1), ('2. Hotel Hell', 0), ('3. Rocky Road', 0), ('4. A Hard Place', 0)], 800, 118)
    sub(img, y + 60 + 4 * 118 + 30, ['Hotel Hell: Отель, бонус 150%', 'A Hard Place: Шахты, бонус 150%'], GREY, 28)
    skin_floor(img, 'wave', 900, 1660, 15); foot3(img); return img

def c_cta():
    img = bg_grid(); glow(img, (540, 700), 460, ACC, 0.30); d = ImageDraw.Draw(img)
    skin_floor(img, 'wave', 540, 1000, 19)
    t = 'Часть 2 скоро'; sz = fit_size([t], 940, 118); shadow_text(d, (540 - font(sz, 900).getlength(t) / 2, 1140), t, sz)
    shadow_text(d, (540 - font(42, 800).getlength('@' + BRAND) / 2, 1240), '@' + BRAND, 42, 800, ACC, off=4)
    t2 = 'Следующая: Hotel Hell'; shadow_text(d, (540 - font(32, 600).getlength(t2) / 2, 1320), t2, 32, 600, (170, 170, 200), off=3)
    soft_shadow(img, (300, 1390, 780, 1486), 38, blur=16, off=(0, 10), color=ACC, alpha=110)
    d.rounded_rectangle([300, 1390, 780, 1486], 38, fill=ACC); d.text((543, 1441), 'Подписаться', font=font(38, 800), fill=(20, 18, 60), anchor='mm'); d.text((540, 1438), 'Подписаться', font=font(38, 800), fill=WHITE, anchor='mm')
    return img

# ---- live cover ----
_b = {}
def base():
    if _b: return _b
    img = bg_grid(); glow(img, (830, 1200), 520, ACC, 0.20); d = ImageDraw.Draw(img)
    shadow_text(d, (80, TOP + 20), 'DOORS · ЧАСТЬ 1/4', 30, 800, GREY, off=3)
    a, b = 'Not Five', 'Stars'; sz = fit_size([a, b], 900, 190); y0 = TOP + 60 + 0.705 * sz; y1 = y0 + 0.95 * sz
    shadow_text(d, (80, y0), a, sz); shadow_text(d, (80, y1), b, sz, 900, ACC)
    shadow_text(d, (80, y1 + 70), 'Туториал по ачивке', 34, 700, (170, 170, 200), off=4)
    shadow_text(d, (80, y1 + 120), 'Отель, бонус 50%', 34, 700, (170, 170, 200), off=4)
    foot3(img)
    m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
    md.text((80, y0), a, font=font(sz, 900), fill=255, anchor='ls'); md.text((80, y1), b, font=font(sz, 900), fill=255, anchor='ls')
    bb = m.getbbox(); _b.update(img=img, mask=m.crop((0, bb[1] - 10, W, bb[3] + 10)), mtop=bb[1] - 10)
    return _b
TL, FP = 3.0, 30
def frame(k):
    c = base(); t = k / FP; ph = 2 * math.pi * t / TL; sn = math.sin(ph); s2 = math.sin(2 * ph)
    img = c['img'].copy(); glow(img, (800, 1150), 470 + 22 * sn, ACC, 0.18 + 0.05 * sn)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); rnd = np.random.default_rng(7)
    for i in range(14):
        bx = rnd.uniform(560, 1020); by = rnd.uniform(700, 1650); s = rnd.uniform(12, 30); sp = int(rnd.integers(1, 3)); phi = rnd.uniform(0, 6.28)
        yy = by - 22 * math.sin(sp * ph + phi); xx = bx + 10 * math.sin(ph + phi * 2); al = int(100 + 70 * math.sin(sp * ph + phi))
        od.rectangle([xx, yy, xx + s, yy + s], fill=ACC + (al,))
    img.paste(ov, (0, 0), ov)
    d = ImageDraw.Draw(img); bx0, by0 = 80, 1060 + 6 * sn
    soft_shadow(img, (bx0, by0, bx0 + 470, by0 + 150), 30, blur=22, off=(0, 14), color=ACC, alpha=int(90 + 40 * sn))
    d.rounded_rectangle([bx0, by0, bx0 + 470, by0 + 150], 30, fill=SURF, outline=ACC, width=4)
    shadow_text(d, (bx0 + 30, by0 + 62), 'БОНУС', 34, 800, (190, 190, 255), off=3)
    shadow_text(d, (bx0 + 30, by0 + 122), '50%+', 60, 900, WHITE, off=5)
    P = SK.POSES['present']; q = dict(P['pose']); q.update(turn=-12 + 7 * sn, bob=0.3 * s2)
    sk = SK.render(pose=q, yaw=-18 + 6 * sn, tilt=7, scale=27, size=(1100, 1220), floor=1450, ss=2); img.paste(sk, (850 - 550, 500), sk)
    mk = c['mask']; hh = mk.size[1]; cxb = -300 + (W + 600) * ((t / TL) % 1.0)
    band = Image.new('L', (W, hh), 0); bd = ImageDraw.Draw(band)
    for off in range(-120, 121, 6): bd.line([cxb + off + 90, 0, cxb + off - 90, hh], fill=int(255 * max(0, 1 - abs(off) / 120)), width=8)
    img.paste(Image.new('RGB', (W, hh), ACC), (0, c['mtop']), ImageChops.multiply(mk, band))
    return img

CARDS = [('02_need', c_req), ('03_build', c_build), ('04_steps', c_steps), ('05_tips', c_tips), ('06_series', c_series), ('07_cta', c_cta)]
if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'static':
        imgs = []
        for n, f in CARDS: im = f(); im.save(f'{OD}/{n}.png'); imgs.append(guides(im))
        im = frame(20); im.save(f'{OD}/01_live_poster.png'); imgs.insert(0, guides(im))
        sh = Image.new('RGB', (len(imgs) * 360, 640))
        for k, i in enumerate(imgs): sh.paste(i.resize((360, 640)), (k * 360, 0))
        sh.save(f'{OD}/_check.png')
    else:
        path = f'{OD}/01_live.mp4'; tmp = path + '.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FP), '-i', '-',
                              '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-f', 'mp4', tmp], stdin=subprocess.PIPE)
        for k in range(int(TL * FP)): p.stdin.write(frame(k).tobytes())
        p.stdin.close()
        if p.wait() == 0: os.replace(tmp, path)
