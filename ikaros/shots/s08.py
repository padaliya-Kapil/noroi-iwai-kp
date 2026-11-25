"""S08  From the top of the tower they leap, Daidalos first; the wings open and catch, and the camera rises with them."""
from functools import lru_cache
from shotkit import *

PH = 2300; ROOF = 1650


def build(cv, h, w):
    bands(cv, [(None, 800, ST.engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c')), (740, 1500, PAL['sky_mid']), (1440, 2400, PAL['sky_lo'])], w, 15)
    masonry(cv, 560, ROOF, 1440, h, 74)
    for i in range(8):
        x = 540 + i * 118
        cv.put(mask(lambda c, x=x: (c.rectangle(x, ROOF - 60, 58, 64), c.fill())), paper(STONE[i % 5], 120 + i, mottle=.08), edge='torn', seed=120 + i, amp=2.5, rim=1.5, shadow=(3, 4, 2, .3))
    cv.put(mask(lambda c: (c.rectangle(540, ROOF - 6, 920, 24), c.fill())), paper('#9b907c', 129), edge='torn', seed=129, amp=3, rim=2, shadow=(3, 5, 3, .35))


@lru_cache(1)
def page(): return cached('s08', build, PH, W)


def flyer_at(cv, t, t0, x0, seed, beard, rise=200, vx=150, q=20):
    """Paths chosen so the two stay at least ~530 px apart and both in frame while the camera rises."""
    tau = t - t0; u = ease(0, .7, tau)
    if tau < 0: crouch = 0.
    else: crouch = max(0., 1 - abs(tau + .25) / .25) if tau < 0 else 0.
    pose = pose_mix('stand', 'fly', u)
    a0 = lerp((-1., -.35), (-1., .12), u); a1 = lerp((-.9, -.75), (-.78, -.62), u)
    T = max(tau, 0.); x = x0 + vx * T; y = ROOF - 244 * .9 - rise * T - q * T * T
    ang = D(-90 + 55 * u)
    winged(cv, (x, y, ang, .9), seed, t, period=1.1, flap=14 * u, bob=6 * u, pose=pose, a0=a0, a1=a1, kick_amt=u, flutter=.04, beard=beard, shadow=(9, 14, 8, .4))


def draw(d):
    t = d / FPS; cy = (ROOF - 860) * (1 - ease(1.8, 5.2, t))
    cv = Canvas(view(page(), 0, cy), jitter=.45, drawing=d)
    with camera(0, cy):
        flyer_at(cv, t, 2.2, 1160, 300, False, rise=140, vx=150)
        flyer_at(cv, t, 1.6, 620, 200, True, rise=235, vx=40)
    return finish(cv, d)
