import sys, subprocess
from news_pack3 import *
import doors_pack as DP
OD = HERE + '/out_steam'; os.makedirs(OD, exist_ok=True)
GREY = (150, 150, 180)
def tag(img, t):
    shadow_text(ImageDraw.Draw(img), (80, TOP - 42), t, 28, 800, GREY, off=3)
def sub(img, y, lines, col=GREY, sz=28):
    d = ImageDraw.Draw(img)
    for i, t in enumerate(lines): shadow_text(d, (80, y + i * (sz + 14)), t, sz, 600, col, off=3)
def card(a, b, tg, items, notes=None, skin=None, hs=130, kinds=None, w=900):
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head3(img, a, b, hs); tag(img, tg)
    rows(img, y + 60, items, w, 112)
    if notes: sub(img, y + 60 + len(items) * 112 + 20, notes)
    if skin: skin_floor(img, *skin)
    foot3(img); return img

def s_cover():
    img = bg_grid(); glow(img, (830, 1100), 520, ACC, 0.22); d = ImageDraw.Draw(img)
    shadow_text(d, (80, TOP + 20), 'STEAM · БЕЗОПАСНОСТЬ', 30, 800, GREY, off=3)
    a, b = 'Не отдай', 'аккаунт'; sz = fit_size([a, b], 900, 170); y0 = TOP + 60 + 0.705 * sz; y1 = y0 + 0.95 * sz
    shadow_text(d, (80, y0), a, sz); shadow_text(d, (80, y1), b, sz, 900, ACC)
    shadow_text(d, (80, y1 + 70), '4 схемы мошенников', 34, 700, (170, 170, 200), off=4)
    shadow_text(d, (80, y1 + 120), 'и как защититься', 34, 700, (170, 170, 200), off=4)
    put = lambda: None
    skin_floor(img, 'guard', 850, 1640, 17); foot3(img); return img
def s_phish(): return card('Схема 1', 'Фишинг', 'STEAM · СХЕМЫ', [('Поддельный сайт входа', 2), ('Фейковые «турниры»', 2), ('Сканирование фейк-QR', 2)], ['Цель: украсть логин и', 'код Steam Guard'], ('think', 880, 1660, 16))
def s_api(): return card('Схема 2', 'API-скам', 'STEAM · СХЕМЫ', [('1. Ты шлёшь трейд', 0), ('2. Скамер с API-ключом', 2), ('   отменяет оффер', 2), ('3. Клон профиля шлёт', 2), ('   встречный оффер', 2), ('4. Ты принимаешь', 1)], ['Смотри уровень и дату', 'регистрации партнёра'], None, 120)
def s_fake(): return card('Схема 3', 'Фейк-поддержка', 'STEAM · СХЕМЫ', [('Пишут в ЛС от «Steam»', 2), ('Пугают баном', 2), ('«Срочно передай скины»', 1)], ['Поддержка не просит', 'передавать предметы'], ('present', 890, 1660, 16), 120)
def s_virus(): return card('Схема 4', 'Вирусы', 'STEAM · СХЕМЫ', [('.exe под видом читов', 2), ('Софт «для обхода»', 2), ('Крадёт сессии и пароли', 1)], ['Файлы с чужих ссылок', 'не запускай'], ('inspect', 890, 1660, 16))
def s_hacked(): return card('Если', 'взломали', 'STEAM · ЧТО ДЕЛАТЬ', [('1. Отозвать API-ключ', 0), ('2. Сменить пароли:', 0), ('   Steam и почта', 0), ('3. Выйти на всех устройствах', 0), ('4. Новая trade-ссылка', 0)], ['API-ключ: steamcommunity.com', '/dev/apikey'], None, 130)
def s_protect(): return card('Как', 'защититься', 'STEAM · ЗАЩИТА', [('Мобильный Steam Guard', 0), ('Проверяй адрес сайта', 0), ('Входи только на сайт', 0), ('   steampowered.com', 0), ('Не ставь файлы с читов', 0)], None, ('confident', 890, 1660, 15), 130)
def s_cta():
    img = bg_grid(); glow(img, (540, 700), 460, ACC, 0.30); d = ImageDraw.Draw(img)
    skin_floor(img, 'wave', 540, 1000, 19)
    t = 'Подписывайся'; sz = fit_size([t], 940, 118); shadow_text(d, (540 - font(sz, 900).getlength(t) / 2, 1140), t, sz)
    shadow_text(d, (540 - font(42, 800).getlength('@' + BRAND) / 2, 1240), '@' + BRAND, 42, 800, ACC, off=4)
    t2 = 'Сохрани, чтобы не потерять аккаунт'; shadow_text(d, (540 - font(28, 600).getlength(t2) / 2, 1320), t2, 28, 600, (170, 170, 200), off=3)
    soft_shadow(img, (300, 1390, 780, 1486), 38, blur=16, off=(0, 10), color=ACC, alpha=110)
    d.rounded_rectangle([300, 1390, 780, 1486], 38, fill=ACC); d.text((543, 1441), 'Подписаться', font=font(38, 800), fill=(20, 18, 60), anchor='mm'); d.text((540, 1438), 'Подписаться', font=font(38, 800), fill=WHITE, anchor='mm')
    return img

if __name__ == '__main__':
    D = [(s_cover, 4.0), (s_phish, 5.5), (s_api, 8.0), (s_fake, 6.0), (s_virus, 5.5), (s_hacked, 8.0), (s_protect, 7.0), (s_cta, 4.0)]
    FPS, FADE = 30, 8
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OD + '/steam_scam_video.mp4'], stdin=subprocess.PIPE)
    prev = None
    for f, dur in D:
        im = f(); 
        for k in range(int(dur * FPS)):
            o = Image.blend(prev, im, (k + 1) / FADE) if prev is not None and k < FADE else im
            p.stdin.write(o.tobytes())
        prev = im
    p.stdin.close(); print(p.wait())
