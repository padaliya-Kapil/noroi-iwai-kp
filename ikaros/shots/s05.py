"""S05  The workbench by candlelight.  Daidalos on a low stool at the bench's edge; on the bench (seen from above, as a collage
may) the feathers are sorted into rows, smallest to largest, laid down one at a time among his tools."""
from functools import lru_cache
from shotkit import *

PX0, PY0, PX1, PY1 = 700, 60, 1860, 1000
ROWS = [(330, 120, 11), (600, 175, 9), (900, 245, 7)]                       # (base y, length, count)
FEATH = []
for ri, (by, L, n) in enumerate(ROWS):
    for i in range(n):
        r = rng(ri * 50 + i); FEATH.append((PX0 + 300 + (PX1 - PX0 - 360) * (i + .5) / n + r.normal(0, 6), by, L * r.uniform(.93, 1.05), D(-90 + r.normal(0, 4)), ri * 50 + i))


def tools(cv):
    """Laid on the bench in the left margin: a pot of wax, a spool of thread, split reeds, a knife."""
    cv.put(mask(lambda c: (c.arc(850, 230, 92, 0, 6.3), c.fill())), paper(PAL['clay'], 201, mottle=.07), edge='cut', seed=201, shadow=(8, 12, 8, .4),
           marks=[(mask(lambda c: (c.set_line_width(10), c.arc(850, 230, 80, 0, 6.3), c.stroke())), '#1d1612', .9)])
    cv.put(mask(lambda c: (c.arc(850, 230, 66, 0, 6.3), c.fill())), paper('#b8873e', 202, mottle=.12, cell=20), edge='cut', seed=202, shadow=(0, 0, 0, 0), opacity=.9,
           marks=[(mask(lambda c: (c.save(), c.translate(828, 206), c.scale(1, .55), c.arc(0, 0, 20, 0, 6.3), c.restore(), c.fill())), '#f3e6c4', .7)])
    cv.put(mask(lambda c: (c.rectangle(790, 420, 120, 64), c.fill())), lines_print('#e8dcc0', '#7a5a3c', seed=203, pitch=3, ang=90, width=.4, ink=.6), edge='cut', seed=203, shadow=(6, 9, 6, .4),
           marks=[(mask(lambda c: (c.rectangle(780, 410, 14, 84), c.fill(), c.rectangle(906, 410, 14, 84), c.fill())), '#7a5a3c', 1.)])
    for k in range(3):
        cv.put(mask(lambda c, k=k: (poly(c, rect_pts(760 + k * 6, 560 + k * 40, 230, 16, D(-8 + k * 4))), c.fill())),
               lines_print('#b39a6c', '#3a2a1c', seed=204 + k, pitch=3, ang=-8 + k * 4, width=.3, ink=.35), edge='cut', seed=204 + k, shadow=(5, 8, 5, .4))
    cv.put(mask(lambda c: (poly(c, [(780, 860), (930, 840), (948, 852), (930, 864)]), c.fill())), paper('#c9c4b8', 207), edge='cut', seed=207, shadow=(4, 6, 4, .4))
    cv.put(mask(lambda c: (poly(c, rect_pts(700 + 70, 845, 80, 26, D(-4))), c.fill())), lines_print('#6d5038', '#2a1d12', seed=208, pitch=4, ang=86, width=.4, ink=.5), edge='cut', seed=208, shadow=(4, 6, 4, .4))


def build(cv, h, w):
    masonry(cv, 0, 0, w, 1000, 73, dim=.38, mortar='#4a4138')
    cv.put(mask(lambda c: (c.rectangle(-20, 990, w + 40, 120), c.fill())), lines_print('#4e3726', '#1e140c', seed=91, pitch=6, ang=2, width=.35, ink=.45), edge='torn', seed=91, amp=4, rim=2, shadow=(0, -6, 6, .4))
    cv.put(mask(lambda c: (poly(c, rect_pts(PX0 - 16, PY0 - 16, PX1 - PX0 + 32, PY1 - PY0 + 32, D(.6))), c.fill())), slip(92), edge='cut', seed=92, shadow=(10, 14, 10, .45))
    cv.put(mask(lambda c: (poly(c, rect_pts(PX0, PY0, PX1 - PX0, PY1 - PY0, D(.6))), c.fill())), lines_print('#9a774f', '#4a3220', seed=93, pitch=8, ang=1, width=.36, ink=.32, cell=60), edge='cut', seed=93, shadow=(0, 0, 0, 0))
    tools(cv)
    cv.put(mask(lambda c: (c.rectangle(300, 846, 230, 26), c.fill(), c.rectangle(322, 870, 24, 120), c.fill(), c.rectangle(484, 870, 24, 120), c.fill())),
           lines_print('#7a5a3c', '#2e1f12', seed=94, pitch=5, ang=88, width=.35, ink=.4), edge='cut', seed=94, shadow=(6, 9, 6, .4))


@lru_cache(1)
def page(): return cached('s05', build)


WORK = dict(POSE['seated'], arm=((134, -6), (96, 106), (62, 200)), arm_far=((128, -12), (90, 98), (58, 190)), turn=math.pi / 2 + .45)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    k = int(len(FEATH) * ease(.25, 4.7, t)) + (1 if t > .25 else 0)
    for j, (x, by, L, a, sd) in enumerate(FEATH[:k]):
        col, kind = FEATHER_PAPERS[rng(sd + 7).integers(len(FEATHER_PAPERS))]
        new = j == k - 1; lift = 14 if new else 0
        pts, sp = feather_pts((x, by - lift), a, L, max(18, L * .21), curve=.04)
        cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), feather_tex(kind, col, 700 + sd), edge='cut', seed=700 + sd,
               shadow=(10, 14, 9, .4) if new else (4, 6, 4, .32), marks=[(mask(lambda c, sp=sp: (c.set_line_width(1.4), poly(c, sp, close=False), c.stroke())), SEPIA, .5)],
               wobble=.6, move=new)
    sway = .5 + .5 * math.sin(t * 2.6)
    reach = dict(WORK, arm=tuple(lerp(a, b, sway) for a, b in zip(WORK['arm'], ((134, -6), (112, 118), (88, 226)))))
    figure(cv, (420, 818, D(-90), 1.25), 200, pose=reach, beard=True, dress='chiton', shadow=(6, 9, 6, .4))
    fx, fy = candle(cv, 160, 990, t, d, s=1.15)
    glow(cv, fx, fy, 640, .9 + .1 * rng(d).normal())
    return finish(cv, d, desat=.08)
