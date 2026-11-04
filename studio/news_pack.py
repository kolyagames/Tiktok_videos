"""Полный пак новостных карточек (шрифт Monocraft, тени, тёмная тема). Карточка №1 - live (зацикленный mp4)."""
import os, sys, math
os.environ['THEME'] = 'dark'; os.environ['FONT'] = 'mc'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from news_card import *   # cards2 helpers + патч шрифта
OUTN = HERE + '/out_news'; os.makedirs(OUTN, exist_ok=True)
SRC = os.path.join(HERE, 'screens', 'news1.png')
RED = (214, 68, 68)

def head(img, a, b, size=150, acc=True, top=250):
    d = ImageDraw.Draw(img); sz = fit_size([a, b], 900, size)
    shadow_text(d, (80, top + 0.705 * sz), a, sz); shadow_text(d, (80, top + 0.705 * sz + 0.95 * sz), b, sz, 900, ACC if acc else INK)
    return top + 0.705 * sz + 0.95 * sz

def foot(img): shadow_text(ImageDraw.Draw(img), (80, 1862), '@' + BRAND, 38, 700, INK, off=4)

def stamp(img, y, label, color=AMBER, x=80):
    d = ImageDraw.Draw(img); pw = int(font(30, 800).getlength(label)) + 60
    d.rounded_rectangle([x, y, x + pw, y + 64], 24, fill=color)
    d.text((x + pw / 2 + 3, y + 35), label, font=font(30, 800), fill=(255, 214, 140) if color == AMBER else (255, 170, 170), anchor='mm')
    d.text((x + pw / 2, y + 32), label, font=font(30, 800), fill=(30, 22, 10) if color == AMBER else WHITE, anchor='mm')

def skin_floor(img, name, cx, fy, sc):
    floor_shadow(img, cx, fy, 300, 40); put_skin(img, name, cx, fy, sc)

def rows(img, y0, items, w=580, gap=118):
    for i, (lab, kind) in enumerate(items): pill_row(img, 80, y0 + i * gap, w, 92, lab, kind, ACC)

# ---------- 1: live-обложка ----------
TL, FP = 3.0, 30
_base = {}
def cover_base():
    if _base: return _base
    img = bg_grid(); glow(img, (830, 1200), 520, ACC, 0.20); d = ImageDraw.Draw(img)
    sz = fit_size(['Каналы', 'под угрозой'], 900, 170)
    shadow_text(d, (80, 250 + 0.705 * sz), 'Каналы', sz); shadow_text(d, (80, 250 + 0.705 * sz + 0.95 * sz), 'под угрозой', sz, 900, ACC)
    y = 250 + 0.705 * sz + 0.95 * sz + 70
    shadow_text(d, (80, y + 14), 'YouTube-каналы с флюгером', 36, 700, (170, 170, 200), off=4)
    shadow_text(d, (80, y + 74), 'со слов авторов', 36, 700, (170, 170, 200), off=4)
    foot(img)
    m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
    md.text((80, 250 + 0.705 * sz), 'Каналы', font=font(sz, 900), fill=255, anchor='ls'); md.text((80, 250 + 0.705 * sz + 0.95 * sz), 'под угрозой', font=font(sz, 900), fill=255, anchor='ls')
    bb = m.getbbox(); _base.update(img=img, mask=m.crop((0, bb[1] - 10, W, bb[3] + 10)), mtop=bb[1] - 10, y=y)
    return _base

def cover_frame(k):
    c = cover_base(); t = k / FP; ph = 2 * math.pi * t / TL; sn = math.sin(ph); s2 = math.sin(2 * ph)
    img = c['img'].copy(); glow(img, (800, 1250), 470 + 22 * sn, ACC, 0.18 + 0.05 * sn)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); rnd = np.random.default_rng(7)
    for i in range(14):
        bx = rnd.uniform(560, 1020); by = rnd.uniform(900, 1700); s = rnd.uniform(12, 30); sp = int(rnd.integers(1, 3)); phi = rnd.uniform(0, 6.28)
        yy = by - 22 * math.sin(sp * ph + phi); xx = bx + 10 * math.sin(ph + phi * 2); al = int(100 + 70 * math.sin(sp * ph + phi))
        od.rectangle([xx, yy, xx + s, yy + s], fill=ACC + (al,))
    img.paste(ov, (0, 0), ov)
    # пульсирующая плашка с датой
    d = ImageDraw.Draw(img); bx0, by0 = 80, 1180 + 6 * sn
    soft_shadow(img, (bx0, by0, bx0 + 470, by0 + 150), 30, blur=22, off=(0, 14), color=RED, alpha=int(90 + 40 * sn))
    d.rounded_rectangle([bx0, by0, bx0 + 470, by0 + 150], 30, fill=SURF, outline=RED, width=4)
    shadow_text(d, (bx0 + 30, by0 + 62), 'УДАЛЕНИЕ', 34, 800, (255, 150, 150), off=3)
    shadow_text(d, (bx0 + 30, by0 + 122), '7 НОЯБРЯ', 60, 900, WHITE, off=5)
    P = SK.POSES['think']; q = dict(P['pose']); q.update(turn=-12 + 7 * sn, roll=6 + 2 * s2, nod=5 + 3 * s2, rarm=(32 + 2 * s2, 6, 118 + 6 * sn, 0), larm=(52, 2, 70 + 3 * s2, 42), bob=0.3 * s2)
    sk = SK.render(pose=q, yaw=-18 + 6 * sn, tilt=7, scale=31, size=(1100, 1220), floor=1450, ss=2); img.paste(sk, (860 - 550, 560), sk)
    mk = c['mask']; hh = mk.size[1]; cxb = -300 + (W + 600) * ((t / TL) % 1.0)
    band = Image.new('L', (W, hh), 0); bd = ImageDraw.Draw(band)
    for off in range(-120, 121, 6): bd.line([cxb + off + 90, 0, cxb + off - 90, hh], fill=int(255 * max(0, 1 - abs(off) / 120)), width=8)
    img.paste(Image.new('RGB', (W, hh), ACC), (0, c['mtop']), ImageChops.multiply(mk, band))
    return img

def write_live(path):
    tmp = path + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FP), '-i', '-',
                          '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-f', 'mp4', tmp], stdin=subprocess.PIPE)
    for k in range(int(TL * FP)): p.stdin.write(cover_frame(k).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, path)

# ---------- 2: что случилось ----------
def c_what():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head(img, 'Что', 'случилось', 170)
    stamp(img, y + 40, 'ПО СКРИНШОТУ')
    rows(img, y + 150, [('5 предупреждений', 1), ('Авторские права', 0), ('Удаление: 7 ноября', 2), ('Канал можно спасти,', 0), ('если их снять', 0)], 560, 112)
    skin_floor(img, 'present', 915, 1560, 22); foot(img); return img

# ---------- 3: скриншот ----------
def c_shot():
    return news_card('Что', 'пишут авторы', 'Пост авторов каналов', SRC, 'Telegram: ТГК bro9i', ['Заявление авторов', 'каналов о страйках.', 'Независимо не', 'подтверждено.'], 'СО СЛОВ АВТОРОВ')

# ---------- 4: известно / не подтверждено ----------
def c_known():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head(img, 'Что', 'известно', 170)
    d = ImageDraw.Draw(img)
    shadow_text(d, (80, y + 90), 'Видно на скриншоте', 34, 800, (170, 170, 200), off=4)
    rows(img, y + 120, [('Уведомление YouTube', 0), ('Дата удаления: 7.11', 0)], 560, 112)
    y2 = y + 120 + 2 * 112 + 60
    shadow_text(d, (80, y2 + 30), 'Не подтверждено', 34, 800, AMBER, off=4)
    rows(img, y2 + 60, [('Кто подал страйки', 2), ('Были ли они законны', 2), ('Ответ Wild: не найден', 2)], 560, 112)
    skin_floor(img, 'think', 915, 1600, 22); foot(img); return img

# ---------- 5: что дальше ----------
def c_next():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head(img, 'Что', 'дальше', 170); d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 80, y + 60, 700, y + 330
    soft_shadow(img, (x0, y0, x1, y1), 30, blur=24, off=(0, 16), alpha=70)
    d.rounded_rectangle([x0, y0, x1, y1], 30, fill=SURF, outline=ACC, width=3)
    shadow_text(d, (x0 + 30, y0 + 62), '"Придётся уже идти', 32, 800, WHITE, off=3); shadow_text(d, (x0 + 30, y0 + 112), 'другим путём"', 32, 800, WHITE, off=3)
    shadow_text(d, (x0 + 30, y0 + 190), 'цитата из поста, ТГК bro9i', 26, 600, (150, 150, 180), off=3)
    rows(img, y1 + 50, [('Ждём ответ Wild', 2), ('7 ноября: дедлайн', 1), ('Обновим карточкой', 0)], 560, 112)
    skin_floor(img, 'confident', 915, 1600, 22); foot(img); return img

# ---------- 6: CTA ----------
def c_cta():
    img = bg_grid(); glow(img, (540, 640), 460, ACC, 0.30); d = ImageDraw.Draw(img)
    skin_floor(img, 'wave', 540, 840, 23)
    t = 'Подписывайся'; sz = fit_size([t], 940, 118); shadow_text(d, (540 - font(sz, 900).getlength(t) / 2, 1010), t, sz)
    shadow_text(d, (540 - font(42, 800).getlength('@' + BRAND) / 2, 1110), '@' + BRAND, 42, 800, ACC, off=4)
    t2 = 'Следим за этой историей'; shadow_text(d, (540 - font(32, 600).getlength(t2) / 2, 1190), t2, 32, 600, (170, 170, 200), off=3)
    soft_shadow(img, (300, 1260, 780, 1356), 38, blur=16, off=(0, 10), color=ACC, alpha=110)
    d.rounded_rectangle([300, 1260, 780, 1356], 38, fill=ACC); d.text((543, 1311), 'Подписаться', font=font(38, 800), fill=(20, 18, 60), anchor='mm'); d.text((540, 1308), 'Подписаться', font=font(38, 800), fill=WHITE, anchor='mm')
    return img

if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'static':
        for n, f in [('02_what', c_what), ('03_post', c_shot), ('04_known', c_known), ('05_next', c_next), ('06_cta', c_cta)]: f().save(f'{OUTN}/{n}.png')
    elif m == 'poster': cover_frame(int(sys.argv[2])).save(f'{OUTN}/01_live_poster.png')
    elif m == 'live': write_live(f'{OUTN}/01_live.mp4')
