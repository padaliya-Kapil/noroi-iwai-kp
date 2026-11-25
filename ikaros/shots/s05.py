"""S05  The workbench by candlelight.  Daidalos at his stool; on the bench (seen from above) the feathers are sorted into rows,
smallest to largest, laid down one at a time."""
from functools import lru_cache
from shotkit import *

PX0, PY0, PX1, PY1 = 720, 70, 1850, 1010
ROWS = [(250, 70, 13), (450, 110, 10), (660, 150, 8), (900, 195, 6)]          # (base y, length, count)
FEATH = []
for ri, (by, L, n) in enumerate(ROWS):
    for i in range(n):
        r = rng(ri * 50 + i); FEATH.append((PX0 + 90 + (PX1 - PX0 - 180) * (i + .5) / n + r.normal(0, 6), by, L * r.uniform(.92, 1.06), D(-90 + r.normal(0, 5)), ri * 50 + i))


def build(cv, h, w):
    masonry(cv, 0, 0, w, 1000, 73, dim=.38, mortar='#4a4138')
    cv.put(mask(lambda c: (c.rectangle(-20, 990, w + 40, 120), c.fill())), lines_print('#4e3726', '#1e140c', seed=91, pitch=6, ang=2, width=.35, ink=.45), edge='torn', seed=91, amp=4, rim=2, shadow=(0, -6, 6, .4))
    cv.put(mask(lambda c: (poly(c, rect_pts(PX0 - 16, PY0 - 16, PX1 - PX0 + 32, PY1 - PY0 + 32, D(.6))), c.fill())), slip(92), edge='cut', seed=92, shadow=(10, 14, 10, .45))
    cv.put(mask(lambda c: (poly(c, rect_pts(PX0, PY0, PX1 - PX0, PY1 - PY0, D(.6))), c.fill())), lines_print('#8a6845', '#3a2716', seed=93, pitch=7, ang=1, width=.4, ink=.4, cell=60), edge='cut', seed=93, shadow=(0, 0, 0, 0))
    cv.put(mask(lambda c: (c.rectangle(230, 615, 190, 26), c.fill(), c.rectangle(250, 640, 22, 350), c.fill(), c.rectangle(378, 640, 22, 350), c.fill())),
           lines_print('#7a5a3c', '#2e1f12', seed=94, pitch=5, ang=88, width=.35, ink=.4), edge='cut', seed=94, shadow=(6, 9, 6, .4))


@lru_cache(1)
def page(): return cached('s05', build)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    k = int(len(FEATH) * ease(.25, 4.7, t)) + (1 if t > .25 else 0)
    for j, (x, by, L, a, sd) in enumerate(FEATH[:k]):
        col, kind = FEATHER_PAPERS[rng(sd + 7).integers(len(FEATHER_PAPERS))]
        new = j == k - 1; lift = 14 if new else 0
        pts, sp = feather_pts((x, by - lift), a, L, max(14, L * .2), curve=.04)
        cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), feather_tex(kind, col, 700 + sd), edge='cut', seed=700 + sd,
               shadow=(9, 13, 8, .38) if new else (3, 5, 3, .3), marks=[(mask(lambda c, sp=sp: (c.set_line_width(1.2), poly(c, sp, close=False), c.stroke())), SEPIA, .5)],
               wobble=.6, move=new)
    sway = .5 + .5 * math.sin(t * 2.6)
    figure(cv, (318, 600, D(-90), .95), 200, pose=pose_mix('seated', dict(POSE['seated'], arm=((134, -6), (110, 70), (120, 160))), sway),
           beard=True, dress='chiton', shadow=(6, 9, 6, .4))
    fx, fy = candle(cv, 600, 990, t, d, s=1.15)
    glow(cv, fx, fy, 520, .9 + .1 * rng(d).normal())
    return finish(cv, d, desat=.08)
