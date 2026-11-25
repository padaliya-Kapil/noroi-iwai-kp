"""S09  Over the Aegean.  Islands slide past in layers, far ones slow and near ones fast; gulls keep pace; the boy rises and dips for joy."""
from functools import lru_cache
from shotkit import *

HZ = 640


def build(cv, h, w):
    bands(cv, [(None, 260, ST.engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c')), (220, 470, PAL['sky_mid']), (430, HZ + 30, PAL['sky_lo'])], w, 16)
    rays(cv, 1640, 250, n=14, seed=9, L=2400)
    sun(cv, 1640, 250, 78, seed=7, ring=False, tint=('#f0c080', .15))
    sea(cv, HZ, w, h, seed=45)


@lru_cache(1)
def page(): return cached('s09', build)


ISLES = [  # (layer speed px/s, base y, scale, colour, seed, spacing)
    (22, HZ + 8, .45, '#b4a07a', 1, 760), (70, HZ + 60, .85, PAL['ochre'], 2, 1300)]


def isle(cv, x, y, s, col, seed, move=True):
    r = rng(seed); n = 7; pts = [(x - 260 * s, y)]
    for i in range(1, n):
        pts.append((x - 260 * s + 520 * s * i / n, y - s * (60 + 110 * math.sin(math.pi * i / n)) * r.uniform(.7, 1.2)))
    pts.append((x + 260 * s, y))
    cv.put(mask(lambda c: (poly(c, pts), c.fill())), paper(col, seed, mottle=.08), edge='torn', seed=seed, amp=5, rim=2.5, shadow=(4, 6, 4, .3), move=move)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    for sp, y, s, col, sd, gap in ISLES:
        for k in range(-1, 4):
            x = (k * gap - sp * t) % (gap * 3) - gap * .5 + sd * 170
            if -400 < x < W + 400: isle(cv, x, y, s, col, sd * 10 + k % 3)
    crests(cv, t, [(HZ + 110, 170, 15), (HZ + 210, 190, 19), (HZ + 320, 210, 23)], speed=110)
    for i, (x0, y0, ph) in enumerate(((330, 300, 0.), (1650, 260, 1.7))):
        gull(cv, x0 + 30 * math.sin(t + ph), y0 + 20 * math.sin(t * 1.7 + ph), .75, t, 930 + i)
    winged(cv, (700, 520, D(-10), .72), 200, t, period=1.3, flap=12, bob=10, beard=True, shadow=(9, 14, 8, .4))
    winged(cv, (1180, 400 + 80 * math.sin(t * 1.3), D(-14 + 14 * math.cos(t * 1.3)), .6), 300, t, period=1.0, flap=14, bob=8, shadow=(9, 14, 8, .4))
    return finish(cv, d, light='morning')
