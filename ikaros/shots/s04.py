"""S04  Inside, at the window.  A gull's feather drifts in; Ikaros catches it and holds it up; Daidalos sees what it could become."""
from functools import lru_cache
from shotkit import *

WX, WY0, WY1, WR = 960, 150, 800, 330


def arch(c):
    c.move_to(WX - WR, WY1); c.line_to(WX - WR, WY0 + WR); c.arc(WX, WY0 + WR, WR, math.pi, 2 * math.pi); c.line_to(WX + WR, WY1); c.close_path()


def build(cv, h, w):
    bands(cv, [(None, 360, ST.engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c')), (320, 560, PAL['sky_mid']), (520, 700, PAL['sky_lo'])], w, 13)
    sea(cv, 660, w, h)
    masonry(cv, 0, 0, w, 1000, 72, hole=arch, dim=.12, mortar='#7d7366')
    cv.put(mask(lambda c: (c.rectangle(WX - WR - 30, WY1 - 6, 2 * WR + 60, 34), c.fill())), paper('#a69a84', 89), edge='torn', seed=89, amp=3, rim=2, shadow=(4, 7, 4, .4))
    cv.put(mask(lambda c: (c.rectangle(-20, 990, w + 40, 120), c.fill())), lines_print('#6d5038', '#2a1d12', seed=90, pitch=6, ang=2, width=.35, ink=.45), edge='torn', seed=90, amp=4, rim=2, shadow=(0, -6, 6, .4))


@lru_cache(1)
def page(): return cached('s04', build)


IK = (470, 770, D(-90), .98); DA = (1480, 770, D(-90), .98, True)


def path(t):
    """The feather's drift from the top of the window to the boy's hand."""
    u = ease(.2, 3.3, t); x = 1100 - 500 * u + 60 * math.sin(t * 3.1); y = 270 + 400 * u + 16 * math.sin(t * 6.2)
    return x, y, D(-60) + D(40) * math.sin(t * 3.1)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    if t < 1.6: gull(cv, 1230 - 380 * t, 330 + 30 * math.sin(t * 2), .7, t, 911, flip=True)
    # Ikaros: stands, reaches for the feather, lifts it to show his father
    if t < 2.4: pi = 'stand'
    elif t < 3.5: pi = pose_mix('stand', 'reach', (t - 2.4) / .8)
    else: pi = pose_mix('reach', 'point_up', (t - 3.5) / .6)
    F = figure(cv, IK, 300, pose=pi)
    hand = xform(F.xf, F.arm[2])
    if t < 3.3: x, y, a = path(t)
    else: x, y, a = hand[0] + 6, hand[1] - 30, D(-80)
    pts, sp = feather_pts((x, y), a, 120, 26, curve=.05)
    cv.put(mask(lambda c: (poly(c, pts), c.fill())), paper('#ece5d4', 121, fiber=.1), edge='cut', seed=121, shadow=(8, 12, 7, .32), move=True,
           marks=[(mask(lambda c: (c.set_line_width(1.3), poly(c, sp, close=False), c.stroke())), SEPIA, .5)])
    # Daidalos turns to look, and the idea strikes
    pd = 'stand' if t < 1.5 else pose_mix('stand', dict(POSE['stand'], turn=math.pi / 2 + .35), (t - 1.5) / .5) if t < 4.0 else pose_mix(dict(POSE['stand'], turn=math.pi / 2 + .35), 'point_up', (t - 4.0) / .5)
    figure(cv, DA, 200, pose=pd, beard=True, dress='chiton')
    if t > 4.5:
        k = min(1., (t - 4.5) / .25)
        cv.put(mask(lambda c: (c.arc(1470, 420, 30 * k, 0, 6.3), c.fill())), gold(seed=12), edge='cut', seed=95, shadow=(4, 6, 4, .35), move=True)
    return finish(cv, d)
