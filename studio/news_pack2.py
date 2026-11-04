"""Пак v2: история с каналами bro9i/fluger - по новым скриншотам. Только 'со слов', без выводов."""
import sys, os, shutil
from news_pack import *
O2 = HERE + '/out_news2'; os.makedirs(O2, exist_ok=True)
S = lambda n: Image.open(os.path.join(HERE, 'screens', n)).convert('RGB')

def c_what2():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head(img, 'Что', 'случилось', 170)
    stamp(img, y + 40, 'ПО СКРИНШОТАМ')
    rows(img, y + 150, [('5 предупреждений', 1), ('Панель YouTube: 5 из 3', 0), ('Удаление: 7 ноября', 2), ('Канал можно спасти,', 0), ('если их снять', 0)], 560, 112)
    skin_floor(img, 'present', 915, 1560, 22); foot(img); return img

def c_post():
    img = bg_grid(); glow(img, (830, 1100), 480, ACC, 0.20); d = ImageDraw.Draw(img); y = head(img, 'Что пишет', 'bro9i', 150)
    y1 = window(img, 80, y + 50, 920, S('bro9i_post.png'), 'Telegram: ТГК bro9i')
    stamp(img, y1 + 36, 'СО СЛОВ АВТОРА')
    rows(img, y1 + 130, [('Обвиняет Wild', 2), ('FunTime: не советует', 2)], 600, 112)
    skin_floor(img, 'inspect', 880, 1840, 18); foot(img); return img

def c_yt():
    img = bg_grid(); glow(img, (830, 1100), 480, ACC, 0.20); d = ImageDraw.Draw(img); y = head(img, 'Что видно', 'в YouTube', 150)
    y1 = window(img, 80, y + 50, 920, S('yt_notice.png'), 'Уведомление YouTube')
    y2 = window(img, 80, y1 + 36, 520, S('dash.png'), 'Панель канала')
    shadow_text(d, (80, y2 + 56), 'Скриншоты из поста авторов', 28, 600, (150, 150, 180), off=3)
    shadow_text(d, (80, y2 + 98), 'и чужого монтажа', 28, 600, (150, 150, 180), off=3)
    skin_floor(img, 'think', 880, 1760, 20); foot(img); return img

def c_versions():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head(img, 'Две', 'версии', 170); d = ImageDraw.Draw(img)
    stamp(img, y + 40, 'НЕ ПОДТВЕРЖДЕНО')
    rows(img, y + 150, [('bro9i: виноват Wild', 2), ('Флюгер: Delta ни при чём', 2), ('В уведомлении: Delta Client', 0), ('Кто подал: неизвестно', 1)], 600, 112)
    shadow_text(d, (80, y + 150 + 4 * 112 + 50), 'Delta Client указан как заявитель', 28, 600, (150, 150, 180), off=3)
    shadow_text(d, (80, y + 150 + 4 * 112 + 92), 'в уведомлении (по скриншоту).', 28, 600, (150, 150, 180), off=3)
    skin_floor(img, 'confident', 915, 1650, 21); foot(img); return img

def c_ft():
    img = bg_grid(); glow(img, (830, 1100), 480, ACC, 0.20); d = ImageDraw.Draw(img); y = head(img, 'Что слышно', 'про FunTime', 140)
    y1 = window(img, 80, y + 50, 760, S('ft_forward.png'), 'Пересланное сообщение')
    shadow_text(d, (80, y1 + 56), 'Оригинал и подлинность не проверены', 26, 600, AMBER, off=3)
    y2 = window(img, 80, y1 + 110, 760, S('ft_post2.png'), 'Пост без автора')
    shadow_text(d, (80, y2 + 56), 'Автор поста не указан', 26, 600, AMBER, off=3)
    stamp(img, y2 + 100, 'НЕ ПОДТВЕРЖДЕНО')
    skin_floor(img, 'think', 910, 1840, 19); foot(img); return img

def c_next2():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head(img, 'Что', 'дальше', 170); d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 80, y + 60, 700, y + 330
    soft_shadow(img, (x0, y0, x1, y1), 30, blur=24, off=(0, 16), alpha=70)
    d.rounded_rectangle([x0, y0, x1, y1], 30, fill=SURF, outline=ACC, width=3)
    shadow_text(d, (x0 + 30, y0 + 62), '"Придётся уже идти', 32, 800, WHITE, off=3); shadow_text(d, (x0 + 30, y0 + 112), 'другим путём"', 32, 800, WHITE, off=3)
    shadow_text(d, (x0 + 30, y0 + 190), 'цитата из поста, ТГК bro9i', 26, 600, (150, 150, 180), off=3)
    rows(img, y1 + 50, [('Ждём ответ Wild', 2), ('Ждём ответ Delta', 2), ('7 ноября: дедлайн', 1), ('Обновим карточкой', 0)], 600, 112)
    skin_floor(img, 'confident', 915, 1650, 21); foot(img); return img

if __name__ == '__main__':
    for n, f in [('02_what', c_what2), ('03_post', c_post), ('04_youtube', c_yt), ('05_versions', c_versions), ('06_funtime', c_ft), ('07_next', c_next2), ('08_cta', c_cta)]:
        f().save(f'{O2}/{n}.png')
    for f in ('01_live.mp4', '01_live_motion.jpg'): shutil.copy(f'{OUTN}/{f}', O2)
    shutil.copy(f'{OUTN}/01_live_poster.png', O2)
