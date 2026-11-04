"""Рендер майнкрафтовского скина (классика, 64x64) в заданной позе, с локтями и коленями.
Ортографическая проекция, painter's algorithm по текселям."""
import math
import numpy as np
from PIL import Image, ImageDraw

import os
SKIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skin.png')
_SKIN = None
def skin_img():
    global _SKIN
    if _SKIN is None:
        _SKIN = Image.open(SKIN_PATH).convert('RGBA')
    return _SKIN

def Rx(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

# (limb, uv базы, uv оверлея, (w,h,d), (x0,y0,z0), pivot сустава-плеча/бедра, группа, pivot локтя/колена)
LIMBS = [
    ('head',  (0, 0),   (32, 0),  (8, 8, 8),  (-4, 24, -4), (0, 24, 0),  'up', None),
    ('body',  (16, 16), (16, 32), (8, 12, 4), (-4, 12, -2), (0, 12, 0),  'up', None),
    ('rarm',  (40, 16), (40, 32), (4, 12, 4), (-8, 12, -2), (-6, 22, 0), 'up', (-6, 18, 0)),
    ('larm',  (32, 48), (48, 48), (4, 12, 4), (4, 12, -2),  (6, 22, 0),  'up', (6, 18, 0)),
    ('rleg',  (0, 16),  (0, 32),  (4, 12, 4), (-4, 0, -2),  (-2, 12, 0), 'low', (-2, 6, 0)),
    ('lleg',  (16, 48), (0, 48),  (4, 12, 4), (0, 0, -2),   (2, 12, 0),  'low', (2, 6, 0)),
]
HIP = np.array([0.0, 12.0, 0.0]); CENTER = np.array([0.0, 16.0, 0.0])
LIGHT = np.array([0.35, 0.65, 0.68]); LIGHT = LIGHT / np.linalg.norm(LIGHT)

DEFAULT = dict(nod=0, turn=0, roll=0, lean=0, twist=0, bob=0,
               rarm=(0, 5), larm=(0, 5), rleg=(0, 0), lleg=(0, 0))

def pad(t, n=4): return tuple(t) + (0,) * (n - len(t))

def limb_rot(limb, pose):
    """-> (R плеча/бедра, R локтя/колена или None)"""
    if limb == 'head': return Ry(pose['turn']) @ Rx(pose['nod']) @ Rz(pose['roll']), None
    if limb == 'body': return Ry(pose['twist']), None
    a, b, c, d = pad(pose[limb]); sign = -1 if limb.startswith('r') else 1
    Rs = Rz(sign * b) @ Rx(-a)
    if limb.endswith('arm'): Re = Rz(-sign * d) @ Rx(-c)   # c: сгиб вперёд, d: сгиб к телу
    else: Re = Rx(c)                                        # колено назад
    return Rs, Re

def faces(u, v, w, h, d):
    return {'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d), 'right': (u, v + d, d, h),
            'front': (u + d, v + d, w, h), 'left': (u + d + w, v + d, d, h), 'back': (u + 2 * d + w, v + d, w, h)}
NORMALS = {'front': (0, 0, 1), 'back': (0, 0, -1), 'right': (-1, 0, 0), 'left': (1, 0, 0), 'top': (0, 1, 0), 'bottom': (0, -1, 0)}

def face_points(name, b, tw, th):
    xa, xb, ya, yb, za, zb = b
    i = np.arange(tw + 1)[:, None] / tw; j = np.arange(th + 1)[None, :] / th
    I, J = np.broadcast_arrays(i, j)
    if name == 'front':  x = xa + (xb - xa) * I; y = yb - (yb - ya) * J; z = np.full_like(I, zb)
    elif name == 'back': x = xb - (xb - xa) * I; y = yb - (yb - ya) * J; z = np.full_like(I, za)
    elif name == 'right': z = za + (zb - za) * I; y = yb - (yb - ya) * J; x = np.full_like(I, xa)
    elif name == 'left':  z = zb - (zb - za) * I; y = yb - (yb - ya) * J; x = np.full_like(I, xb)
    elif name == 'top':   x = xa + (xb - xa) * I; z = za + (zb - za) * J; y = np.full_like(I, yb)
    else:                 x = xa + (xb - xa) * I; z = zb - (zb - za) * J; y = np.full_like(I, ya)
    return np.stack([x, y, z], -1)

def render(pose=None, yaw=0, tilt=8, scale=24, size=(900, 900), floor=None, ss=2, parts=None, overlay=True, offset=(0, 0)):
    """RGBA картинка size. Ступни по центру модели в (cx, floor)."""
    pose = {**DEFAULT, **(pose or {})}
    W, H = size
    cx = W / 2 + offset[0]; floor = (H * 0.92 if floor is None else floor) + offset[1]
    S = scale * ss
    tex = np.array(skin_img())
    Rg = Rx(tilt) @ Ry(yaw); Rlean = Rx(pose['lean'])
    items = []
    names = parts or [l[0] for l in LIMBS]

    def xf(P, n, piv, Rs, Re, elbow, seg, grp):
        if seg == 'l' and Re is not None:
            e = np.array(elbow, float); P = e + (P - e) @ Re.T; n = Re @ n
        P = piv + (P - piv) @ Rs.T; n = Rs @ n
        if grp == 'up': P = HIP + (P - HIP) @ Rlean.T; n = Rlean @ n
        P = P.copy(); P[..., 1] += pose['bob']
        P = CENTER + (P - CENTER) @ Rg.T; n = Rg @ n
        return P, n

    for limb, uv0, uv1, (w, h, d), (x0, y0, z0), piv, grp, elbow in LIMBS:
        if limb not in names: continue
        Rs, Re = limb_rot(limb, pose); piv = np.array(piv, float)
        segs = [None] if elbow is None else ['u', 'l']
        for seg in segs:
            for layer, (u, v) in enumerate((uv0, uv1)):
                if layer == 1 and not overlay: continue
                inf = 0.5 if layer == 1 else 0.0
                b = (x0 - inf, x0 + w + inf, y0 - inf, y0 + h + inf, z0 - inf, z0 + d + inf)
                for fname, (tu, tv, tw, th) in faces(u, v, w, h, d).items():
                    if seg == 'l' and fname == 'top': continue
                    if seg == 'u' and fname == 'bottom': continue
                    P = face_points(fname, b, tw, th)
                    Q, n = xf(P, np.array(NORMALS[fname], float), piv, Rs, Re, elbow, seg, grp)
                    if n[2] <= 0.02: continue
                    shade = 0.60 + 0.40 * max(0.0, float(n @ LIGHT))
                    sx = cx * ss + Q[..., 0] * S; sy = floor * ss - Q[..., 1] * S; sz = Q[..., 2]
                    for ti in range(tw):
                        for tj in range(th):
                            if fname not in ('top', 'bottom') and seg is not None:
                                if (seg == 'u') != (tj < th // 2): continue
                            r, g, bb, a = tex[tv + tj, tu + ti]
                            if a < 128: continue
                            xs = [sx[ti, tj], sx[ti + 1, tj], sx[ti + 1, tj + 1], sx[ti, tj + 1]]
                            ys = [sy[ti, tj], sy[ti + 1, tj], sy[ti + 1, tj + 1], sy[ti, tj + 1]]
                            dz = (sz[ti, tj] + sz[ti + 1, tj + 1]) / 2 + layer * 0.01
                            col = (int(min(255, r * shade)), int(min(255, g * shade)), int(min(255, bb * shade)), 255)
                            items.append((dz, list(zip(xs, ys)), col))
            if seg is not None:  # заглушка в месте сгиба, чтобы не было дырки
                ey = elbow[1]; xa, xb, za, zb = x0, x0 + w, z0, z0 + d
                corners = np.array([[xa, ey, za], [xb, ey, za], [xb, ey, zb], [xa, ey, zb]], float)
                Q, n = xf(corners, np.array((0, -1 if seg == 'u' else 1, 0), float), piv, Rs, Re, elbow, seg, grp)
                # средний цвет боковой строки у сгиба
                rows = [tex[uv0[1] + d + (h // 2 - 1 if seg == 'u' else h // 2), uv0[0] + d: uv0[0] + d + w]]
                rc = np.concatenate([r_[:, :3] for r_ in rows]).mean(0)
                shade = 0.55 + 0.25 * max(0.0, abs(float(n @ LIGHT)))
                col = tuple(int(c_ * shade) for c_ in rc) + (255,)
                items.append((Q[:, 2].mean() - 0.3, [(cx * ss + p[0] * S, floor * ss - p[1] * S) for p in Q], col))
    items.sort(key=lambda t: t[0])
    im = Image.new('RGBA', (W * ss, H * ss), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for _, poly, col in items:
        dr.polygon(poly, fill=col, outline=col)
    return im.reduce(ss) if ss > 1 else im

# ---------- ситуативные позы (каждая под свою карточку) ----------
# arm = (вперёд, в сторону, сгиб вперёд, сгиб к телу); leg = (вперёд, в сторону, колено)
POSES = {
    # обложка «A vs B»: раздумье — рука у подбородка, вторая подпирает локоть
    'think':     dict(pose=dict(turn=-12, roll=6, nod=5, twist=-6, rarm=(32, 6, 118, 0), larm=(52, 2, 70, 42), lean=2), yaw=-18, tilt=7),
    # Lunar (PvP-клиент): боевая стойка, кулаки у лица
    'guard':     dict(pose=dict(turn=-16, nod=6, lean=10, twist=-10, rarm=(62, 14, 105, 16), larm=(70, 6, 112, 22),
                                rleg=(-22, 4, 8), lleg=(26, 6, 24), bob=-0.7), yaw=42, tilt=8),
    # Laby (сто с лишним модов): показывает на список плашек, вторая рука на поясе
    'present':   dict(pose=dict(turn=-22, roll=-3, rarm=(10, 78, 6, 0), larm=(18, 34, 0, 112), lleg=(0, 3, 0), rleg=(0, 3, 0)), yaw=-8, tilt=7),
    # Modrinth (сборки): приседает и ставит блок
    'build':     dict(pose=dict(turn=-18, nod=10, lean=22, twist=-8, rarm=(58, 8, 52, 0), larm=(34, 20, 70, 34),
                                rleg=(48, 4, 82), lleg=(40, 6, 78), bob=-2.9), yaw=36, tilt=9),
    # «Как выглядит»: смотрит на окно, показывает на него
    'inspect':   dict(pose=dict(turn=-34, nod=-6, twist=-10, rarm=(24, 70, 14, 0), larm=(6, 4, 0, 0)), yaw=26, tilt=6),
    # «Мой выбор»: уверенная стойка, руки в боки, подбородок вверх
    'confident': dict(pose=dict(turn=-8, nod=-8, rarm=(18, 40, 0, 112), larm=(18, 40, 0, 112), rleg=(0, 9, 0), lleg=(0, 9, 0)), yaw=-14, tilt=7),
    # «Подписывайся»: машет рукой
    'wave':      dict(pose=dict(turn=-10, roll=5, rarm=(0, 96, 0, -76), larm=(0, 6, 0, 0)), yaw=-14, tilt=7),
}

def pose(name, **kw):
    p = POSES[name]
    return render(pose=p['pose'], yaw=p['yaw'], tilt=p['tilt'], **kw)

if __name__ == '__main__':
    import sys
    out = sys.argv[1]; names = list(POSES)
    sheet = Image.new('RGB', (len(names) * 330, 440), (240, 240, 248))
    for k, n in enumerate(names):
        im = pose(n, scale=10, size=(330, 440), floor=410)
        sheet.paste(im, (k * 330, 0), im)
        ImageDraw.Draw(sheet).text((k * 330 + 10, 8), n, fill=(0, 0, 0))
    sheet.save(out)
