"""Пак v3: безопасная зона TikTok (фото-карусель). Контент между y=300 и y=1690: сверху строка поиска, снизу описание."""
import sys, os, shutil
from news_pack import *
from news_pack2 import S
O3 = HERE + '/out_news3'; os.makedirs(O3, exist_ok=True)
TOP, HANDLE_Y = 300, 1655

def head3(img, a, b, size=140):
    d = ImageDraw.Draw(img); sz = fit_size([a, b], 900, size)
    shadow_text(d, (80, TOP + 0.705 * sz), a, sz); shadow_text(d, (80, TOP + 0.705 * sz + 0.95 * sz), b, sz, 900, ACC)
    return TOP + 0.705 * sz + 0.95 * sz

def foot3(img): shadow_text(ImageDraw.Draw(img), (80, HANDLE_Y), '@' + BRAND, 38, 700, INK, off=4)

def c_what():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head3(img, 'Что', 'случилось')
    stamp(img, y + 40, 'ПО СКРИНШОТАМ')
    rows(img, y + 150, [('5 предупреждений', 1), ('Панель YouTube: 5 из 3', 0), ('Удаление: 7 ноября', 2), ('Канал можно спасти,', 0), ('если их снять', 0)], 560, 112)
    skin_floor(img, 'present', 915, 1560, 22); foot3(img); return img

def c_post():
    img = bg_grid(); glow(img, (830, 1100), 480, ACC, 0.20); y = head3(img, 'Что пишет', 'bro9i', 130)
    y1 = window(img, 80, y + 40, 840, S('bro9i_post.png'), 'Telegram: ТГК bro9i')
    stamp(img, y1 + 30, 'СО СЛОВ АВТОРА')
    rows(img, y1 + 120, [('Обвиняет Wild', 2), ('FunTime: не советует', 2)], 560, 106)
    skin_floor(img, 'inspect', 890, 1670, 16); foot3(img); return img

def c_yt():
    img = bg_grid(); glow(img, (830, 1100), 480, ACC, 0.20); d = ImageDraw.Draw(img); y = head3(img, 'Что видно', 'в YouTube', 130)
    y1 = window(img, 80, y + 40, 840, S('yt_notice.png'), 'Уведомление YouTube')
    y2 = window(img, 80, y1 + 30, 500, S('dash.png'), 'Панель канала')
    shadow_text(d, (80, y2 + 50), 'Скриншоты из поста авторов', 26, 600, (150, 150, 180), off=3)
    shadow_text(d, (80, y2 + 90), 'и чужого монтажа', 26, 600, (150, 150, 180), off=3)
    skin_floor(img, 'think', 890, 1670, 17); foot3(img); return img

def c_versions():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head3(img, 'Две', 'версии'); d = ImageDraw.Draw(img)
    stamp(img, y + 40, 'НЕ ПОДТВЕРЖДЕНО')
    rows(img, y + 150, [('bro9i: виноват Wild', 2), ('Флюгер: Delta ни при чём', 2), ('В уведомлении: Delta Client', 0), ('Кто подал: неизвестно', 1)], 600, 112)
    shadow_text(d, (80, y + 150 + 4 * 112 + 50), 'Delta Client указан как заявитель', 28, 600, (150, 150, 180), off=3)
    shadow_text(d, (80, y + 150 + 4 * 112 + 92), 'в уведомлении (по скриншоту).', 28, 600, (150, 150, 180), off=3)
    skin_floor(img, 'confident', 915, 1640, 21); foot3(img); return img

def c_ft():
    img = bg_grid(); glow(img, (830, 1100), 480, ACC, 0.20); d = ImageDraw.Draw(img); y = head3(img, 'Что слышно', 'про FunTime', 130)
    y1 = window(img, 80, y + 40, 760, S('ft_forward.png'), 'Пересланное сообщение')
    shadow_text(d, (80, y1 + 52), 'Оригинал и подлинность не проверены', 26, 600, AMBER, off=3)
    y2 = window(img, 80, y1 + 100, 760, S('ft_post2.png'), 'Пост без автора')
    shadow_text(d, (80, y2 + 52), 'Автор поста не указан', 26, 600, AMBER, off=3)
    stamp(img, y2 + 90, 'НЕ ПОДТВЕРЖДЕНО')
    skin_floor(img, 'think', 935, 1670, 18); foot3(img); return img

def c_next():
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.20); y = head3(img, 'Что', 'дальше'); d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 80, y + 50, 700, y + 320
    soft_shadow(img, (x0, y0, x1, y1), 30, blur=24, off=(0, 16), alpha=70)
    d.rounded_rectangle([x0, y0, x1, y1], 30, fill=SURF, outline=ACC, width=3)
    shadow_text(d, (x0 + 30, y0 + 62), '"Придётся уже идти', 32, 800, WHITE, off=3); shadow_text(d, (x0 + 30, y0 + 112), 'другим путём"', 32, 800, WHITE, off=3)
    shadow_text(d, (x0 + 30, y0 + 190), 'цитата из поста, ТГК bro9i', 26, 600, (150, 150, 180), off=3)
    rows(img, y1 + 40, [('Ждём ответ Wild', 2), ('Ждём ответ Delta', 2), ('7 ноября: дедлайн', 1), ('Обновим карточкой', 0)], 600, 108)
    skin_floor(img, 'confident', 915, 1640, 21); foot3(img); return img

def c_cta3():
    img = bg_grid(); glow(img, (540, 700), 460, ACC, 0.30); d = ImageDraw.Draw(img)
    skin_floor(img, 'wave', 540, 1000, 19)
    t = 'Подписывайся'; sz = fit_size([t], 940, 118); shadow_text(d, (540 - font(sz, 900).getlength(t) / 2, 1140), t, sz)
    shadow_text(d, (540 - font(42, 800).getlength('@' + BRAND) / 2, 1240), '@' + BRAND, 42, 800, ACC, off=4)
    t2 = 'Следим за этой историей'; shadow_text(d, (540 - font(32, 600).getlength(t2) / 2, 1320), t2, 32, 600, (170, 170, 200), off=3)
    soft_shadow(img, (300, 1390, 780, 1486), 38, blur=16, off=(0, 10), color=ACC, alpha=110)
    d.rounded_rectangle([300, 1390, 780, 1486], 38, fill=ACC); d.text((543, 1441), 'Подписаться', font=font(38, 800), fill=(20, 18, 60), anchor='mm'); d.text((540, 1438), 'Подписаться', font=font(38, 800), fill=WHITE, anchor='mm')
    return img

def guides(im):
    """контрольный вариант: красным закрашены зоны, которые перекрывает интерфейс TikTok"""
    g = im.convert('RGBA'); ov = Image.new('RGBA', g.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rectangle([0, 0, W, 290], fill=(255, 0, 0, 90)); od.rectangle([0, 1700, W, H], fill=(255, 0, 0, 90))
    return Image.alpha_composite(g, ov).convert('RGB')

if __name__ == '__main__':
    cards = [('02_what', c_what), ('03_post', c_post), ('04_youtube', c_yt), ('05_versions', c_versions), ('06_funtime', c_ft), ('07_next', c_next), ('08_cta', c_cta3)]
    imgs = []
    for n, f in cards:
        im = f(); im.save(f'{O3}/{n}.png'); imgs.append(guides(im))
    sh = Image.new('RGB', (len(imgs) * 360, 640))
    for k, im in enumerate(imgs): sh.paste(im.resize((360, 640)), (k * 360, 0))
    sh.save(f'{O3}/_check_safe_zone.png')
