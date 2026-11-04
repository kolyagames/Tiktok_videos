"""Новостная карточка: заголовок, окно со скриншотом источника, плашка достоверности, скин."""
import os, sys
os.environ.setdefault('THEME', 'dark')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards, cards2
from cards2 import *
from PIL import ImageFont
_mc = {}
def mcfont(sz, wt=400):
    k = (int(max(sz, 8)), wt >= 700)
    if k not in _mc: _mc[k] = ImageFont.truetype(os.path.join(HERE, 'Monocraft-Bold.otf' if k[1] else 'Monocraft.otf'), k[0])
    return _mc[k]
if os.environ.get('FONT') == 'mc':
    cards.font = mcfont; cards2.font = mcfont; font = mcfont

def news_card(title_a, title_b, sub, shot_path, win_title, note_lines, pill, pose_name='inspect', out=None):
    img = bg_grid(); glow(img, (830, 1000), 460, ACC, 0.22); d = ImageDraw.Draw(img)
    sz = fit_size([title_a, title_b], 900, 170)
    shadow_text(d, (80, 250 + 0.705 * sz), title_a, sz); shadow_text(d, (80, 250 + 0.705 * sz + 0.95 * sz), title_b, sz, 900, ACC)
    y = 250 + 0.705 * sz + 0.95 * sz + 70
    shadow_text(d, (80, y + 14), sub, 38, 700, (170, 170, 200), off=4)
    shot = Image.open(shot_path).convert('RGB')
    y1 = window(img, 80, y + 50, 620, shot, win_title)
    pw = int(font(30, 800).getlength(pill)) + 60
    d.rounded_rectangle([80, y1 + 36, 80 + pw, y1 + 100], 24, fill=AMBER); d.text((80 + pw / 2 + 3, y1 + 69), pill, font=font(30, 800), fill=(255, 214, 140), anchor='mm'); d.text((80 + pw / 2, y1 + 66), pill, font=font(30, 800), fill=(30, 22, 10), anchor='mm')
    for i, ln in enumerate(note_lines): shadow_text(d, (80, y1 + 150 + i * 40), ln, 30, 600, (150, 150, 180), off=3)
    floor_shadow(img, 880, 1560, 300, 40); put_skin(img, pose_name, 880, 1560, 22)
    shadow_text(d, (80, 1862), '@' + BRAND, 38, 700, INK, off=4)
    if out: img.save(out)
    return img

if __name__ == '__main__':
    news_card('Каналы', 'под угрозой', 'Удаление назначено на 7 ноября', os.path.join(HERE, 'screens', 'news1.png'), 'Telegram: ТГК bro9i',
              ['Заявление авторов', 'каналов о страйках.', 'Независимо не', 'подтверждено.'], 'СО СЛОВ АВТОРОВ', out=OUT2 + ('/news_wild_mc.png' if os.environ.get('FONT') == 'mc' else '/news_wild.png'))
