"""S07b  The foretelling.  By candlelight Daidalos shows the boy the future, painted as a frieze on a vase in the black-figure
manner: a winged figure climbs to the sun; the wax runs; the feathers scatter and he falls; feathers lie on the sea.
Then a father's hand on the boy's shoulder, and the boy's head goes down."""
from functools import lru_cache
from shotkit import *

FX0, FX1, FY0, FY1 = 660, 1860, 150, 640; PW = (FX1 - FX0) / 4
APPEAR = [.45 + 1.05 * k for k in range(4)]


def build(cv, h, w):
    cv.put(mask(lambda c: (c.rectangle(-20, -20, w + 40, h + 40), c.fill())), lines_print('#2b221c', '#120d09', seed=230, pitch=7, ang=-6, width=.4, ink=.45), edge='none', shadow=(0, 0, 0, 0))
    cv.put(mask(lambda c: (c.rectangle(-20, 960, w + 40, 140), c.fill())), lines_print('#3e2b1e', '#160f0a', seed=231, pitch=6, ang=2, width=.35, ink=.45), edge='torn', seed=231, amp=4, rim=2, shadow=(0, -6, 6, .4))
    cv.put(mask(lambda c: (c.rectangle(FX0 - 30, FY0 - 70, FX1 - FX0 + 60, FY1 - FY0 + 140), c.fill())), paper('#8f4a2c', 232, mottle=.06), edge='torn', seed=232, amp=8, rim=3, shadow=(10, 14, 10, .45))
    meander_band(cv, FY0 - 58, h=40, x0=FX0 - 20, x1=FX1 + 20, ang=0, seed=233)
    meander_band(cv, FY1 + 16, h=40, x0=FX0 - 20, x1=FX1 + 20, ang=0, seed=234)


@lru_cache(1)
def page(): return cached('s07b', build)


def panel(cv, k, tau):
    """Panel k, laid on the frieze tau seconds ago, and what it shows tau seconds in."""
    x0 = FX0 + k * PW + 8; x1 = x0 + PW - 16; drop = 10 if tau < .17 else 0
    cv.put(mask(lambda c: (c.rectangle(x0, FY0 - drop, x1 - x0, FY1 - FY0), c.fill())), paper(PAL['clay'], 240 + k, mottle=.05), edge='cut', seed=240 + k,
           shadow=(9, 13, 8, .42) if drop else (3, 5, 3, .35), wobble=.8, move=True)
    cx = (x0 + x1) / 2; u = min(1., tau / 1.4)
    if k == 0:
        sun(cv, x1 - 80, FY0 + 90, 46, seed=11, ring=False)
        winged(cv, (x0 + 70 + 110 * u, FY1 - 120 - 200 * u, D(-40), .27), 300, tau, period=.9, flap=14, bob=3, shadow=(3, 5, 3, .4))
    elif k == 1:
        sun(cv, cx + 40, FY0 + 105, 80, seed=12, ring=False)
        winged(cv, (cx - 50, FY0 + 300, D(-35), .27), 300, tau, period=1.4, flap=8, bob=3, melt=dict(skip=(15, 12, 14), drips=True, singe=.8), shadow=(3, 5, 3, .4))
        for j in range(6):
            yy = FY0 + 280 + ((tau * 160 + j * 47) % 180); cv.put(mask(lambda c, j=j, yy=yy: (c.arc(cx - 70 + j * 16, yy, 5, 0, 6.3), c.fill())), paper('#b8873e', 250 + j), edge='cut', seed=250 + j, shadow=(1, 2, 1, .3), move=True)
    elif k == 2:
        figure(cv, (cx, FY0 + 120 + 270 * u, D(-150 + 120 * u), .27), 300, pose='fall', shadow=(3, 5, 3, .4))
        for j in range(5):
            air_feather(cv, 70 + j, (cx - 100 + j * 50, FY0 + 110), D(30 + 40 * j), 34, tau, (j - 2) * 12, 40, 50, 10, j, scale=.4)
    else:
        cv.put(mask(lambda c: (c.rectangle(x0, FY1 - 200, x1 - x0, 200), c.fill())), slip(260), edge='cut', seed=260, shadow=(0, 0, 0, 0), wobble=.6,
               marks=[(mask(lambda c: [(c.set_line_width(4), c.arc(x0 + 36 + 62 * i + 31 * (r % 2), FY1 - 170 + r * 58, 20, D(200), D(340)), c.stroke()) for r in range(3) for i in range(4)]), CLAY, .9)])
        for j, (fx, fy) in enumerate(((cx - 80, FY1 - 195), (cx + 10, FY1 - 198), (cx + 95, FY1 - 194))):
            pts, sp = feather_pts((fx - 30, fy + 2 * math.sin(tau * 2 + j)), D(178 + 5 * math.sin(tau * 1.7 + j)), 62, 14, curve=.04)
            cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), paper('#e8dfc9', 262 + j), edge='cut', seed=262 + j, shadow=(2, 3, 2, .35), move=True,
                   marks=[(mask(lambda c, sp=sp: (c.set_line_width(1), poly(c, sp, close=False), c.stroke())), SEPIA, .5)])


POINT = dict(POSE['stand'], arm=((134, -6), (196, 66), (254, 136)), turn=math.pi / 2 - .25)
HOLD = dict(POSE['stand'], arm=((134, -6), (112, 80), (96, 168)), turn=math.pi / 2 + .25)
LOOK = dict(POSE['stand'], turn=math.pi / 2 - .3)
BOW = dict(POSE['stand'], turn=math.pi / 2 + .5)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    for k, t0 in enumerate(APPEAR):
        if t >= t0: panel(cv, k, t - t0)
    pd = POINT if t < 4.5 else pose_mix(POINT, HOLD, (t - 4.5) / .45)
    figure(cv, (300, 668, D(-90), 1.2), 200, pose=pd, beard=True, dress='chiton', shadow=(6, 9, 6, .4))
    pi = LOOK if t < 4.75 else pose_mix(LOOK, BOW, (t - 4.75) / .4)
    winged(cv, (500, 742, D(-90), .9), 300, t, flap=0, bob=0, pose=pi, folded=True, kick_amt=0, flutter=.02, shadow=(5, 8, 5, .38))
    fx, fy = candle(cv, 110, 960, t, d, s=1.1)
    glow(cv, fx, fy, 760, .95 + .1 * rng(d).normal())
    return finish(cv, d, desat=.08)
