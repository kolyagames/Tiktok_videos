"""Оригинальный пиксельный маскот: рак-отшельник с раковиной-микросхемой («Бит»).
draw_crab(im, x, y, t, pose='idle'|'talk'|'point'|'wow', u=14, look=(1,0))  — рисует в PIL-кадр, (x,y) = левый верх спрайта (38x30 клеток).
"""
import math
from PIL import Image, ImageDraw
TEAL = (43, 183, 166); TEAL_D = (28, 130, 120); TEAL_L = (110, 225, 205)
SHELL = (29, 43, 83); SHELL_L = (52, 74, 130); CY = (80, 230, 255); YL = (255, 214, 77); WH = (245, 248, 250); BK = (14, 16, 28); PK = (255, 140, 150)

def draw_crab(im, x, y, t, pose='idle', u=14, look=(1, 0), acc='none'):
    d = ImageDraw.Draw(im)
    def R(a, b, c, e, col):
        d.rectangle([x + a * u, y + b * u, x + (c + 1) * u - 1, y + (e + 1) * u - 1], fill=col)
    wow = pose == 'wow'
    jump = (-2 if (t % 1.3) < 0.2 else 0) if wow else 0
    y = y + (round(math.sin(t * 3.2)) + jump) * u // 2
    # ноги по бокам (шагают)
    for i, lx in enumerate((6, 8, 10, 19, 21, 23)):
        up = 1 if math.sin(t * 6 + i * 1.7) > 0.3 else 0
        R(lx, 21 - up, lx, 24 - up, TEAL_D); R(lx - (1 if lx < 15 else 0), 24 - up, lx + (0 if lx < 15 else 1), 24 - up, TEAL_D)
    # тело: широкий овал
    for gx in range(4, 27):
        for gy in range(11, 23):
            e = ((gx - 15) / 11.5) ** 2 + ((gy - 16.5) / 5.6) ** 2
            if e <= 1: R(gx, gy, gx, gy, TEAL_D if gy >= 21 or e > 0.86 else (TEAL_L if gy <= 12 and e < 0.8 else TEAL))
    # рюкзак-микросхема на спине (над телом)
    for px in range(12, 18, 2): R(px, 6, px, 7, (190, 195, 205))      # ножки микросхемы
    R(11, 8, 18, 13, SHELL); R(11, 8, 18, 8, SHELL_L); R(12, 10, 17, 10, CY); R(14, 9, 14, 12, CY)
    R(12, 9, 12, 9, YL); R(17, 9, 17, 9, YL); R(12, 12, 12, 12, YL) if int(t * 2) % 2 == 0 else R(17, 12, 17, 12, YL)
    # глаза на стебельках
    sway = round(math.sin(t * 2.1)); blink = (t % 3.4) < 0.12; top = 3 if not wow else 2
    for ex in (8, 21):
        R(ex, top + 3, ex, 13, TEAL_D)
        R(ex - 1, top, ex + 1, top + 2, WH if not blink else TEAL_L)
        if not blink:
            px = ex + (look[0] if look[0] else 0) * (1 if ex == 8 else 0) - (1 if look[0] > 0 and ex == 21 else 0)
            R(max(ex - 1, min(ex, px)), top + 1, max(ex - 1, min(ex, px)), top + 2, BK) if not wow else R(ex - 1, top, ex + 1, top + 2, BK) or R(ex, top + 1, ex, top + 1, WH)
    if acc == 'glasses':
        for ex in (8, 21):
            R(ex - 2, top - 1, ex + 2, top - 1, BK); R(ex - 2, top + 3, ex + 2, top + 3, BK); R(ex - 2, top, ex - 2, top + 2, BK); R(ex + 2, top, ex + 2, top + 2, BK)
        R(11, top + 1, 18, top + 1, BK)
    elif acc == 'cap':
        R(11, 3, 18, 5, (255, 85, 0)); R(11, 6, 18, 6, (170, 50, 0)); R(12, 4, 13, 4, (255, 160, 90))
    elif acc == 'headphones':
        R(10, 5, 19, 5, CY); R(10, 5, 10, 8, CY); R(19, 5, 19, 8, CY); R(9, 9, 10, 12, CY); R(19, 9, 20, 12, CY); R(9, 10, 9, 11, SHELL); R(20, 10, 20, 11, SHELL)
    # лицо
    R(12, 16, 12, 17, BK) if not blink else R(11, 17, 13, 17, TEAL_D)
    R(18, 16, 18, 17, BK) if not blink else R(17, 17, 19, 17, TEAL_D)
    R(10, 18, 10, 18, PK); R(20, 18, 20, 18, PK)
    talking = pose == 'talk' and int(t * 7) % 2 == 0
    if wow: R(14, 18, 16, 20, BK)
    elif talking: R(14, 18, 16, 19, BK)
    else: R(14, 19, 16, 19, SHELL)
    # клешни
    def claw(side, raise_, big=True):
        s_ = -1 if side == 'L' else 1
        ax = 4 if side == 'L' else 25
        ay = 18 - raise_
        for k in range(3): R(min(ax, ax + s_ * k), ay + 1 + (raise_ and 0), min(ax, ax + s_ * k), ay + 2, TEAL)  # рука
        cx0 = 0 if side == 'L' else 26
        R(cx0, ay - 4, cx0 + 3, ay + 1, TEAL); R(cx0, ay - 4, cx0 + 3, ay - 4, TEAL_L)
        R(cx0 + (1 if side == 'L' else 1), ay - 4, cx0 + (1 if side == 'L' else 2), ay - 2, BK) if False else None
        gx = cx0 + 1 if side == 'L' else cx0 + 2
        R(gx, ay - 4, gx, ay - 2, BK)    # щель между пальцами
        R(cx0, ay + 1, cx0 + 3, ay + 1, TEAL_D)
    lr = {'idle': 0, 'talk': 0, 'point': 0, 'wow': 5 + round(math.sin(t * 14))}[pose]
    rr = {'idle': 0, 'talk': 2 + round(2 * math.sin(t * 5)), 'point': 6, 'wow': 5 + round(math.sin(t * 14 + 1))}[pose]
    claw('L', lr); claw('R', rr)
    return im

if __name__ == '__main__':
    import subprocess, sys
    W = H = 560; out = sys.argv[1] if len(sys.argv) > 1 else 'crab_demo.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    seq = [('idle', 2), ('talk', 3), ('point', 2), ('wow', 2)]
    t = 0.0
    for pose, dur in seq:
        for _ in range(int(dur * 30)):
            im = Image.new('RGB', (W, H), (22, 24, 40)); ImageDraw.Draw(im).rectangle([0, 490, W, H], fill=(36, 40, 62))
            draw_crab(im, 20, 40, t, pose, 17, (1 if int(t * 0.8) % 2 == 0 else -1, 0)); p.stdin.write(im.tobytes()); t += 1 / 30
    p.stdin.close(); p.wait()
