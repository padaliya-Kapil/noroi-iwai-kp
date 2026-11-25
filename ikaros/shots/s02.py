"""S02  King Minos, a great robed and crowned black figure, watches the Labyrinth being laid strip by strip; Daidalos sets the last walls."""
from functools import lru_cache
from shotkit import *

CX, CY, CELL, N = 1300, 540, 92, 7
WALLS = maze(N, 7)


def wall_pts(w, grow=0.):
    (a, b), (c, e) = w; x0, y0 = CX - N * CELL / 2, CY - N * CELL / 2
    p, q = (x0 + a * CELL, y0 + b * CELL), (x0 + c * CELL, y0 + e * CELL); h = 9 + grow
    if p[1] == q[1]: return [(p[0] - h, p[1] - h), (q[0] + h, q[1] - h), (q[0] + h, q[1] + h), (p[0] - h, p[1] + h)]
    return [(p[0] - h, p[1] - h), (p[0] + h, p[1] - h), (q[0] + h, q[1] + h), (q[0] - h, q[1] + h)]


def build(cv, h, w):
    cv.put(mask(lambda c: (poly(c, rect_pts(0, 0, w, h)), c.fill())), ST.engraved(PAL['parch'], 3, pitch=6, ang=-3, width=.25, ink=.2), edge='none', shadow=(0, 0, 0, 0))
    s = N * CELL + 90
    cv.put(mask(lambda c: (poly(c, rect_pts(CX - s / 2, CY - s / 2, s, s, D(.8))), c.fill())), paper(PAL['clay'], 21, mottle=.07), edge='torn', seed=21, amp=8, rim=4, shadow=(8, 12, 8, .35))
    meander_band(cv, 1030, ang=.2)


@lru_cache(1)
def page(): return cached('s02', build)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    k = int(len(WALLS) * ease(.15, 4.4, t))
    if k > 1:
        cv.put(mask(lambda c: [(poly(c, wall_pts(w)), c.fill()) for w in WALLS[:k - 1]]), slip(31), edge='cut', seed=31, shadow=(3, 5, 3, .4), wobble=.6)
    if k >= 1:
        cv.put(mask(lambda c: (poly(c, wall_pts(WALLS[k - 1])), c.fill())), slip(32), edge='cut', seed=32 + k, shadow=(7, 10, 6, .4), move=True)
    # Daidalos at the corner of his work, reaching in to place the walls
    figure(cv, (830, 760, D(-90), .62), 200, pose=pose_mix('stand', 'reach', .5 + .5 * math.sin(t * 4.5)), beard=True, dress='chiton', shadow=(5, 8, 5, .34))
    # the king
    figure(cv, (300, 830 + 3 * math.sin(t * 1.3), D(-90), 2.45), 600, pose=pose_mix('stand', dict(POSE['stand'], turn=math.pi / 2 + .12), ease(1.5, 2.5, t)),
           beard=True, dress='robe', crown=True, shadow=(12, 18, 12, .4))
    return finish(cv, d)
