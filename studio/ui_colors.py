"""Ролик «Цвета на HDD» в стиле Dark UI + Pixel Art (маскот-скин). python3 ui_colors.py OUT.mp4"""
import os, sys, math, subprocess, wave, tempfile, random
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_video as U
from ui_video import *
U.MODE = 'skin'
DUR = 26.0; U.DUR = DUR
COLS = [  # имя, цвет, для чего (по обзору NAS Compares, 2018), реплика
    ('Blue', (46, 110, 255), ['Обычный компьютер', 'Повседневные задачи', 'Не для RAID'], 'Синий: для обычного компьютера.'),
    ('Red', (235, 55, 65), ['Сетевые хранилища NAS', 'Работа 24/7', 'RAID-массивы'], 'Красный: для сетевых хранилищ, круглосуточно.'),
    ('Black', (60, 60, 72), ['Быстрая работа', 'Видео и монтаж', 'Игровые ПК'], 'Чёрный: для быстрой работы.'),
    ('Purple', (150, 80, 235), ['Камеры наблюдения', 'Постоянная запись', 'Видеорегистраторы'], 'Фиолетовый: для камер наблюдения.'),
    ('Gold', (240, 180, 40), ['Дата-центры', 'Большие объёмы', 'Корпоративные задачи'], 'Золотой: для дата-центров.'),
]
T_COL = 6.0; PER = 3.2   # старт цветных сцен и длительность каждой
U.LINES = [
    (0.4, 'ruslan', 'Зачем диски разного цвета?'),
    (3.0, 'irina', 'Цвет это линейка диска.'),
] + [(T_COL + i * PER + 0.3, 'irina', c[3]) for i, c in enumerate(COLS)] + [
    (T_COL + 5 * PER + 0.3, 'ruslan', 'Но линейки меняются. Смотри на сайте производителя.'),
]

# заголовок пикселями
def tb():
    mask = Image.new('L', (W, 420), 0); d = ImageDraw.Draw(mask)
    d.text((W / 2, 110), 'Цвета', font=pfont(190), fill=255, anchor='mm'); d.text((W / 2, 300), 'на HDD', font=pfont(190), fill=255, anchor='mm')
    a = np.array(mask); B = 14; blocks = []; rnd = random.Random(5)
    for y in range(0, 420, B):
        for x in range(0, W, B):
            if a[y:y + B, x:x + B].mean() > 110:
                ang = rnd.uniform(0, 6.28); r = rnd.uniform(500, 1400)
                blocks.append((x, y + 640, x + math.cos(ang) * r, y + 640 + math.sin(ang) * r, rnd.uniform(0, 0.8), rnd.choice([ACC, ACC, WHITE, OR])))
    return blocks, B
U.BLOCKS, U.BS = tb()

def scene_intro(im, t):
    cx = W / 2; k = spring(t / 0.6)
    card(im, (cx - 440 * k, 700, cx + 440 * k, 1120), WHITE)
    if k > 0.8:
        rich(im, cx, 840, 'Одинаковые диски,', 54, DK); rich(im, cx, 920, 'а *цвета* разные?', 54, DK); txt(im, (cx, 1030), 'сейчас разберёмся', 36, GRAY, 700)
    for j, nm in enumerate(['Blue', 'Red', 'Black', 'Purple', 'Gold']):
        tt = t - 0.3 - j * 0.12
        if tt > 0: fly_hdd(im, nm, tt * 0.6 + 0.4, 3.2, 130 + j * 205, 1280 + 40 * math.sin(t * 3 + j), 250, fromx=W / 2)
    mascot(im, cx, 1600, t, 'talk', 'glasses', 14)

_HD = {}
def hdd_img(name, t, per, size):
    key = (name, size)
    n = 64; idx = min(n - 1, max(0, int(t / per * n)))
    if (name, idx) not in _HD:
        p = os.path.join(HDD_DIR, name.lower(), 'f%04d.png' % (idx + 1))
        _HD[(name, idx)] = Image.open(p).convert('RGBA') if os.path.exists(p) else None
    a = _HD[(name, idx)]
    return a.resize((size, size), Image.LANCZOS) if a else None
HDD_DIR = os.environ.get('HDD_DIR', '/tmp/claude-0/-home-claude/fdf4a6c8-c5e7-59e0-ac40-76d274e92168/scratchpad/hdd')
def fly_hdd(im, name, t, per, cx, cy, size, fromx=None):
    k = ease(t / 0.5)
    x = cx + ((fromx if fromx is not None else W + 300) - cx) * (1 - k)
    y = cy + 18 * math.sin(t * 3) - 140 * (1 - k)
    s = hdd_img(name, t, per, size)
    if s: im.paste(s, (int(x - size / 2), int(y - size / 2)), s)

def scene_color(im, t, i):
    name, col, rows, _ = COLS[i]
    tint = mix(BG, col, 0.28)
    u = ease(t / 0.35); base = mix(BG, tint, u)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, W, H], fill=base)
    gc = mix(base, WHITE, 0.13)
    for x in range(0, W, 40): d.line([(x, 0), (x, H)], fill=gc)
    for y in range(0, H, 40): d.line([(0, y), (W, y)], fill=gc)
    tag(im)
    txt(im, (140, 400), f'{i + 1}/5', 56, WHITE, 900)
    phead(im, (80, 250), 'WD ' + name, 78, col if name != 'Black' else WHITE, 6)
    k = spring((t - 0.15) / 0.5); cx = W / 2; w = 820 * min(1, k)
    card(im, (cx - w / 2, 480, cx + w / 2, 1160), WHITE)
    if k > 0.7:
        d.rounded_rectangle([cx - 380, 520, cx + 380, 560], 18, fill=col)
        txt(im, (cx, 640), 'Для чего:', 40, GRAY, 800)
        for j, r in enumerate(rows):
            kk = ease((t - 0.5 - j * 0.3) / 0.3)
            if kk > 0:
                y = 740 + j * 120; d.rounded_rectangle([cx - 350, y - 44, cx - 350 + 700 * kk, y + 44], 26, fill=LG)
                if kk > 0.9: d.ellipse([cx - 320, y - 10, cx - 300, y + 10], fill=col); txt(im, (cx - 270, y), r, 44, DK, 800, 'lm')
    source(im, 'Источник: NAS Compares, 2018. Линейки менялись.')
    fly_hdd(im, name, t, PER, W - 270, 330, 460)
    mascot(im, cx, 1640, t, 'talk', 'cap', 14)

def scene_end(im, t):
    phead(im, (80, 250), 'Запомни', 90, ACC, 6)
    cx = W / 2; k = spring(t / 0.5)
    card(im, (cx - 420 * k, 520, cx + 420 * k, 1100), WHITE)
    if k > 0.8:
        rich(im, cx, 680, 'Цвет = *линейка*', 64, DK); rich(im, cx, 790, 'а не стандарт', 64, DK)
        txt(im, (cx, 940), 'Смотри модель и назначение', 38, GRAY, 800); txt(im, (cx, 1010), 'на сайте производителя', 38, GRAY, 800)
    p = ease(t / 2.0); d = ImageDraw.Draw(im); d.rounded_rectangle([120, 1230, 960, 1290], 30, fill=(50, 50, 60)); d.rounded_rectangle([120, 1230, 120 + max(60, 840 * p), 1290], 30, fill=OR if p < 1 else GR)
    mascot(im, 120 + 840 * p * 0.85 + 60, 1210, t, 'wow', 'headphones', 12)
    if p >= 1:
        k2 = spring((t - 2.0) / 0.4); w = 560 * k2; card(im, (cx - w / 2, 1340, cx + w / 2, 1470), GR, 66)
        if k2 > 0.7:
            dd = ImageDraw.Draw(im); c0 = cx - 190; dd.line([(c0 - 22, 1402), (c0 - 6, 1420), (c0 + 24, 1376)], fill=WHITE, width=12, joint='curve'); txt(im, (cx + 30, 1405), 'досмотрено', 56, WHITE, 900)

def frame(t, amp):
    im = bg(t); tag(im)
    if t < 3.0: scene_title(im, t)
    elif t < T_COL: scene_intro(im, t - 3.0)
    elif t < T_COL + 5 * PER:
        i = int((t - T_COL) / PER); scene_color(im, t - T_COL - i * PER, i)
    else: scene_end(im, t - T_COL - 5 * PER)
    return im
U.frame = frame
if __name__ == '__main__':
    U.main(sys.argv[1])
