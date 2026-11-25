"""S14  The sea closes over him in a cut-paper splash; one by one the feathers come down and lie on the water."""
from functools import lru_cache
from shotkit import *

HZ, SX, SY = 300, 960, 640
LAND = [(560, 760, 2.0), (1320, 700, 1.6), (820, 900, 2.6), (1500, 860, 3.1), (380, 930, 3.5), (1100, 980, 2.3)]


def build(cv, h, w):
    bands(cv, [(None, 160, PAL['sky_hi']), (120, HZ + 30, PAL['sky_lo'])], w, 19)
    sea(cv, HZ, w, h, seed=47)


@lru_cache(1)
def page(): return cached('s14', build)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    crests(cv, t, [(HZ + 90, 150, 15), (HZ + 230, 170, 19), (HZ + 400, 190, 23), (HZ + 580, 210, 27)], speed=20)
    if t < .3: figure(cv, (SX, 160 + 1600 * t, D(95), .8), 300, pose=dict(POSE['fall'], turn=0.), shadow=(10, 15, 10, .4))
    u = 0. if t < .25 else min(1., (t - .25) / .5) if t < .75 else min(2., 1 + (t - .75) / 1.6)
    splash(cv, SX, SY, u, s=1.3, seed=160)
    for i, (x, yl, t0) in enumerate(LAND):
        tau = t - (t0 - 1.6)
        if tau <= 0: continue
        y = -120 + (yl + 120) * min(1., tau / 1.6); a = D(160 + 25 * math.sin(tau * 2.4 + i)) if tau < 1.6 else D(178 + 4 * math.sin(t * 2 + i))
        if tau >= 1.6: y = yl + 4 * math.sin(t * 2.2 + i)
        xx = x + (40 * math.sin(tau * 2.4 + i) if tau < 1.6 else 0)
        col, kind = FEATHER_PAPERS[rng(500 + i).integers(len(FEATHER_PAPERS))]
        pts, sp = feather_pts((xx - math.cos(a) * 55, y - math.sin(a) * 55), a, 110, 24, curve=.04)
        cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), feather_tex(kind, col, 170 + i), edge='cut', seed=170 + i,
               shadow=(9, 13, 7, .32) if tau < 1.6 else (2, 3, 2, .3), marks=[(mask(lambda c, sp=sp: (c.set_line_width(1.2), poly(c, sp, close=False), c.stroke())), SEPIA, .5)],
               singe=.5, wobble=.8, move=True)
    return finish(cv, d)
