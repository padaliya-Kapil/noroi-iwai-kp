"""S15  Sunset.  The feathers lie on the water; the sun goes down red into the sea; Daidalos flies home alone towards it,
smaller and smaller.  The name is laid down, and torn in two; the dark comes down like a sheet."""
from functools import lru_cache
from shotkit import *

HZ = 640; SX, SR = 1080, 165
FLOAT = [(420, 840), (640, 920), (880, 860), (1180, 960), (1440, 880), (760, 1010)]
DUSK = dict(hi='#3d4260', mid='#6f5468', low='#b8664a', glow='#de9655')


def build(cv, h, w):
    bands(cv, [(None, 240, ST.engraved(DUSK['hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#1c1f30')), (200, 420, DUSK['mid']), (380, 560, DUSK['low']), (520, HZ + 30, DUSK['glow'])], w, 20)
    rays(cv, SX, HZ, n=12, seed=10, L=2400)
    sun(cv, SX, HZ - 30, SR, seed=8, ring=False, tint=('#c4502e', .32))
    sea(cv, HZ, w, h, seed=48)
    for i in range(7):                                                         # the sun's last road on the water
        y = HZ + 26 + i * 46; wd = 360 - i * 38
        cv.put(mask(lambda c, y=y, wd=wd, i=i: (poly(c, rect_pts(SX - wd / 2 + ((i % 2) - .5) * 40, y, wd, 13)), c.fill())), paper('#d88a52', 310 + i), edge='torn', seed=310 + i, amp=3, rim=1.5, shadow=(0, 0, 0, 0), opacity=.85)
    pts = [(1500, HZ + 26), (1580, 606), (1660, 572), (1740, 560), (1820, 580), (1900, 612), (1990, HZ + 26)]
    cv.put(mask(lambda c: (poly(c, pts), c.fill())), paper('#3a2e2c', 171, mottle=.08), edge='torn', seed=171, amp=6, rim=3)


@lru_cache(1)
def page(): return cached('s15', build)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    crests(cv, t, [(HZ + 80, 160, 15), (HZ + 200, 180, 19), (HZ + 340, 200, 23)], speed=14)
    for i, (x, y) in enumerate(FLOAT):
        a = D(176 + 6 * math.sin(t * 1.6 + i)); y = y + 4 * math.sin(t * 2 + i)
        col, kind = FEATHER_PAPERS[rng(600 + i).integers(len(FEATHER_PAPERS))]
        pts, sp = feather_pts((x - math.cos(a) * 50, y - math.sin(a) * 50), a, 100, 22, curve=.04)
        cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), feather_tex(kind, col, 180 + i), edge='cut', seed=180 + i, shadow=(2, 3, 2, .3),
               marks=[(mask(lambda c, sp=sp: (c.set_line_width(1.2), poly(c, sp, close=False), c.stroke())), SEPIA, .5)], singe=.5, wobble=.8, move=True)
    u = ease(0, 4.2, t)                                                        # home, alone, into the sunset
    look = pose_mix(dict(POSE['fly'], turn=.5), 'fly', ease(.4, 1.6, t))
    winged(cv, (480 + 560 * u, 300 + 250 * u, D(4 + 6 * u), .62 - .38 * u), 200, t, period=1.6, flap=10, bob=6, beard=True, pose=look, shadow=(8, 12, 8, .4))
    if t > 2.3: label(cv, 960, 170, 'ΙΚΑΡΟΣ', hh=84, tear=ease(3.1, 4.3, t), move=True)
    if t > 4.4:
        v = ease(4.4, 5.15, t); yb = -60 + (H + 260) * v
        bot = ST.wavy(yb, 20, 190, n=10)
        cv.put(mask(lambda c: (poly(c, [(-60, -80), (W + 60, -80)] + bot[::-1]), c.fill())), paper('#1e1714', 191, mottle=.02, cell=200), edge='torn', seed=191, amp=9, rim=4, shadow=(0, 14, 12, .5), move=True)
    return finish(cv, d, light='sunset')
