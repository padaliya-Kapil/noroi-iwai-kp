"""S15  Daidalos alone above the feathers on the water.  The name is laid down, and torn in two; the dark comes down like a sheet."""
from functools import lru_cache
from shotkit import *

HZ = 640
FLOAT = [(520, 820), (760, 900), (1010, 840), (1240, 940), (1460, 870), (880, 1000)]


def build(cv, h, w):
    bands(cv, [(None, 260, ST.engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c')), (220, 470, PAL['sky_mid']), (430, HZ + 30, PAL['sky_lo'])], w, 20)
    sea(cv, HZ, w, h, seed=48)
    pts = [(1380, HZ + 26), (1470, 600), (1560, 560), (1650, 548), (1740, 572), (1840, 610), (1960, HZ + 26)]
    cv.put(mask(lambda c: (poly(c, pts), c.fill())), paper(PAL['ochre'], 171, mottle=.08), edge='torn', seed=171, amp=6, rim=3)


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
    winged(cv, (1240 - 60 * t, 300 + 14 * math.sin(t), D(180 + 8), .62, True), 200, t, period=1.8, flap=9, bob=8, beard=True, pose=dict(POSE['fly'], turn=.45), shadow=(9, 14, 8, .4))
    if t > 1.6: label(cv, 960, 520, 'ΙΚΑΡΟΣ', hh=92, tear=ease(2.8, 4.3, t), move=True)
    if t > 4.3:
        v = ease(4.3, 5.25, t); yb = -60 + (H + 160) * v
        bot = ST.wavy(yb, 20, 190, n=10)
        cv.put(mask(lambda c: (poly(c, [(-60, -80), (W + 60, -80)] + bot[::-1]), c.fill())), paper('#1e1714', 191, mottle=.02, cell=200), edge='torn', seed=191, amp=9, rim=4, shadow=(0, 14, 12, .5), move=True)
    return finish(cv, d)
