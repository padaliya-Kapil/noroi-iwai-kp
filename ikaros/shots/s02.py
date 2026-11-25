"""S02  Crete.  Three beats.  Daidalos, his boy beside him, builds the Labyrinth for King Minos, its stone walls rising
wall by wall (seen from above, as a collage may).  The Minotaur, bull-headed, is dropped into its heart and paces there.
Then the king turns on his builder: he points, and father and son turn to him and bow their heads; the tower is next."""
from functools import lru_cache
from shotkit import *

CX, CY, CELL, N = 1310, 520, 94, 7
WALLS = maze(N, 7)
BUILD = (.15, 3.1)          # the walls go up between these times (s); music.py times the taps from these
DROP = 3.3                  # the Minotaur lands
TURN, POINT_T, FACE, BOW = 3.7, 4.1, 4.55, 5.0


def wall_pts(w, grow=0.):
    (a, b), (c, e) = w; x0, y0 = CX - N * CELL / 2, CY - N * CELL / 2
    p, q = (x0 + a * CELL, y0 + b * CELL), (x0 + c * CELL, y0 + e * CELL); h = 11 + grow
    if p[1] == q[1]: return [(p[0] - h, p[1] - h), (q[0] + h, q[1] - h), (q[0] + h, q[1] + h), (p[0] - h, p[1] + h)]
    return [(p[0] - h, p[1] - h), (p[0] + h, p[1] - h), (q[0] + h, q[1] + h), (q[0] - h, q[1] + h)]


def build(cv, h, w):
    cv.put(mask(lambda c: (poly(c, rect_pts(0, 0, w, h)), c.fill())), ST.engraved(PAL['parch'], 3, pitch=6, ang=-3, width=.25, ink=.2), edge='none', shadow=(0, 0, 0, 0))
    s = N * CELL + 90
    cv.put(mask(lambda c: (poly(c, rect_pts(CX - s / 2, CY - s / 2, s, s, D(.8))), c.fill())), paper('#b7905e', 21, mottle=.07), edge='torn', seed=21, amp=8, rim=4, shadow=(8, 12, 8, .35))
    c0 = CX - CELL / 2 + 4                                                     # the heart of the maze, darker
    cv.put(mask(lambda c: (c.rectangle(c0, CY - CELL / 2 + 4, CELL - 8, CELL - 8), c.fill())), paper(PAL['clay'], 22, mottle=.08), edge='torn', seed=22, amp=3, rim=1.5, shadow=(0, 0, 0, 0))
    meander_band(cv, 1030, ang=.2)


@lru_cache(1)
def page(): return cached('s02', build)


KING_POINT = dict(POSE['stand'], arm=((134, -6), (120, 80), (104, 160)), turn=math.pi / 2 + .12)
KING_LOOK = dict(POSE['stand'], turn=math.pi / 2 + .12)
BOWED = dict(POSE['stand'], turn=math.pi / 2 + .55)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    k = int(len(WALLS) * ease(*BUILD, t))
    stone = lambda s_: paper('#cfc3a8', s_, mottle=.09)
    if k > 1:
        cv.put(mask(lambda c: [(poly(c, wall_pts(w)), c.fill()) for w in WALLS[:k - 1]]), stone(31), edge='torn', seed=31, amp=2, rim=1.5, shadow=(5, 8, 4, .45))
    if k >= 1 and t < BUILD[1] + .1:
        cv.put(mask(lambda c: (poly(c, wall_pts(WALLS[k - 1])), c.fill())), stone(32), edge='torn', seed=32 + k, amp=2, rim=1.5, shadow=(10, 14, 7, .45), move=True)
    # the Minotaur: dropped in from above, then pacing in the heart of the maze
    if t >= DROP - .25:
        fall = max(0., DROP - t) / .25; pace = math.sin((t - DROP) * 3.2) if t > DROP else 0.
        sc = .46 * (1 + .4 * fall)
        figure(cv, (CX + 10 * pace, CY + 110 - 160 * fall, D(-90), sc, pace < 0), 700, pose=dict(POSE['stand'], turn=math.pi / 2), bull=True,
               shadow=(int(4 + 20 * fall), int(6 + 26 * fall), 4 + 10 * fall, .45))
    # Daidalos and the boy at the corner of the work: building, then turning to the king
    if t < FACE:
        pd = pose_mix('stand', 'reach', .5 + .5 * math.sin(t * 4.5)) if t < BUILD[1] else 'stand'
        figure(cv, (860, 760, D(-90), .62), 200, pose=pd, beard=True, dress='chiton', shadow=(5, 8, 5, .34))
        figure(cv, (760, 776, D(-90), .46), 300, pose=dict(POSE['stand'], turn=math.pi / 2 - .15), shadow=(4, 6, 4, .34))
    else:
        bow = BOWED if t > BOW else 'stand'
        if BOW - .35 < t <= BOW: bow = pose_mix('stand', BOWED, (t - (BOW - .35)) / .35)
        figure(cv, (860, 760, D(-90), .62, True), 200, pose=bow, beard=True, dress='chiton', shadow=(5, 8, 5, .34))
        figure(cv, (790, 776, D(-90), .46, True), 300, pose=bow, shadow=(4, 6, 4, .34))
    # the king: watching, turning to his builder, pointing at him
    if t < TURN: pk = 'stand'
    elif t < POINT_T: pk = pose_mix('stand', KING_LOOK, (t - TURN) / .3)
    else: pk = pose_mix(KING_LOOK, KING_POINT, (t - POINT_T) / .35)
    figure(cv, (300, 830 + 3 * math.sin(t * 1.3), D(-90), 2.45), 600, pose=pk, beard=True, dress='robe', crown=True, shadow=(12, 18, 12, .4))
    return finish(cv, d)
