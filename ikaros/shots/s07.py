"""S07  On the tower roof Daidalos warns the boy, wings already strapped on: not up to the sun, not down to the sea; the middle way."""
from functools import lru_cache
from shotkit import *

DA = (700, 650, D(-90), 1.0); IK = (1210, 650, D(-90), 1.0, True)
UP = dict(POSE['stand'], turn=math.pi / 2 - .5); DOWN = dict(POSE['stand'], turn=math.pi / 2 + .45)


def build(cv, h, w):
    bands(cv, [(None, 300, ST.engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c')), (250, 640, PAL['sky_mid']), (590, 1100, PAL['sky_lo'])], w, 14)


@lru_cache(1)
def page(): return cached('s07', build)


def keys(t, frames):
    """Pose at time t from [(t0, pose), ...], blending over a third of a second at each change."""
    for (t0, p), (t1, q) in zip(frames, frames[1:]):
        if t < t1: return p
        if t < t1 + .35: return pose_mix(p, q, (t - t1) / .35)
    return frames[-1][1]


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    if t > .9: sun(cv, 1560, -260 + 500 * ease(.9, 1.5, t), 150)
    if t > 2.5:
        top = 1100 - 290 * ease(2.5, 3.2, t); sea(cv, top, W, H, seed=44); crests(cv, t, [(top + 60, 170, 15), (top + 150, 190, 19)])
    cv.put(mask(lambda c: (poly(c, [(-20, 890), (W + 20, 880), (W + 20, 950), (-20, 960)]), c.fill())), paper('#a69a84', 98, mottle=.08), edge='torn', seed=98, amp=5, rim=3, shadow=(6, 10, 7, .4))
    pd = keys(t, [(0, 'stand'), (.9, 'point_up'), (2.5, 'point_down'), (4.0, 'reach')])
    figure(cv, DA, 200, pose=pd, beard=True, dress='chiton')
    pi = keys(t, [(0, 'stand'), (1.0, UP), (2.6, DOWN), (4.1, 'stand')])
    winged(cv, IK, 300, t, flap=0, bob=0, pose=pi, folded=True, kick_amt=0, flutter=.02, shadow=(6, 9, 6, .36))
    return finish(cv, d)
