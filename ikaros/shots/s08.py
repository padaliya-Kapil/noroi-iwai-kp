"""S08  The leap, at dawn.  A wide view: the tower top high over the sea, the sun just up.  Father and son at the parapet,
the boy a head shorter.  Daidalos spreads his wings, runs and leaps out over the drop; the boy follows.  The camera pans
with them towards the sunrise."""
from functools import lru_cache
from shotkit import *

PW, PH = 3500, 1400
HZ = 1010; TX0, TX1, TOP = 420, 860, 560; SUNX = 3020
DAWN = dict(hi='#6d7889', mid='#ad999a', lo='#ddbfa0', glow='#ecd2ae')


def build(cv, h, w):
    bands(cv, [(None, 330, ST.engraved(DAWN['hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#2f3644')), (280, 640, DAWN['mid']), (590, 880, DAWN['lo']), (840, HZ + 30, DAWN['glow'])], w, 15)
    rays(cv, SUNX, HZ - 20, n=16, seed=8, L=2600)
    sun(cv, SUNX, HZ - 20, 120, seed=6, tint=('#e07a5a', .38))
    sea(cv, HZ, w, h, seed=42)
    for i in range(5):                                                         # the sun's path on the water
        y = HZ + 30 + i * 42; wd = 260 - i * 30
        cv.put(mask(lambda c, y=y, wd=wd, i=i: (poly(c, rect_pts(SUNX - wd / 2 + (i % 2) * 30, y, wd, 12)), c.fill())), paper('#e2a86e', 300 + i), edge='torn', seed=300 + i, amp=3, rim=1.5, shadow=(0, 0, 0, 0), opacity=.8)
    cliff(cv, [(-60, h + 60), (-60, 1080), (120, 1050), (260, 1000), (380, 980), (900, 985), (1020, 1040), (1160, 1120), (1300, 1250), (1380, h + 60)], 70)
    masonry(cv, TX0, TOP, TX1, 1000, 74)
    for i in range(6):
        x = TX0 - 14 + i * (TX1 - TX0 + 28) / 5.5
        cv.put(mask(lambda c, x=x: (c.rectangle(x, TOP - 46, 44, 50), c.fill())), paper(STONE[i % 5], 120 + i, mottle=.08), edge='torn', seed=120 + i, amp=2.5, rim=1.5, shadow=(3, 4, 2, .3))
    cv.put(mask(lambda c: (c.rectangle(TX0 - 18, TOP - 4, TX1 - TX0 + 36, 20), c.fill())), paper('#9b907c', 129), edge='torn', seed=129, amp=3, rim=2, shadow=(3, 5, 3, .35))


@lru_cache(1)
def page(): return cached('s08', build, PH, PW)


SPREAD = dict(POSE['stand'], arm=((134, -6), (176, -70), (240, -110)), arm_far=((128, -12), (166, -76), (226, -120)))


def leaper(cv, t, t0, x0, k, seed, beard, rise, vx):
    """Stand; spread the wings; two running steps; the leap and the first heavy beats out over the drop."""
    feet = TOP; tau = t - t0
    if tau < -.5:
        pose, ang, x, y, a0, a1, flap = 'stand', D(-90), x0, feet - 244 * k, (-1., -.35), (-.9, -.75), 0
    elif tau < 0:
        u = (tau + .5) / .5; pose = pose_mix('stand', SPREAD, u); ang = D(-90); x, y = x0, feet - 244 * k
        a0 = lerp((-1., -.35), (-1., .12), u); a1 = lerp((-.9, -.75), (-.78, -.62), u); flap = 0
    else:
        u = ease(0, .55, tau); pose = pose_mix(SPREAD, 'fly', u); ang = D(-90 + 70 * u)
        x = x0 + vx * tau + 60 * min(tau, .3); y = feet - 244 * k * (1 - .6 * u) + 70 * math.sin(min(tau / 1.1, 1) * math.pi) - rise * max(0., tau - .4)
        a0, a1 = (-1., .12), (-.78, -.62); flap = 15 * u
    winged(cv, (x, y, ang, k), seed, t, period=1.0, flap=flap, bob=0, pose=pose, a0=a0, a1=a1, kick_amt=.6 if tau > 0 else 0, flutter=.04, beard=beard, shadow=(7, 11, 7, .4))


def draw(d):
    t = d / FPS; u = ease(1.7, 5.3, t)
    cx, cy, s = 40 + 1180 * u, 50, .78 + .1 * u
    cv = Canvas(view(page(), cx, cy, s), jitter=.45, drawing=d)
    with camera(cx, cy, s):
        crests(cv, t, [(HZ + 80, 180, 15), (HZ + 190, 200, 19), (HZ + 310, 220, 23)], w=PW, speed=16)
        for i, (gx, gy, ph) in enumerate(((1300, 420, 0.), (1650, 300, 1.4))):
            gull(cv, gx + 90 * t, gy + 25 * math.sin(t * 1.4 + ph), .6, t, 940 + i)
        leaper(cv, t, 2.35, 600, .5, 300, False, rise=30, vx=380)            # the boy, a head shorter, a beat behind
        leaper(cv, t, 1.6, 760, .66, 200, True, rise=60, vx=330)
    return finish(cv, d, light='dawn')
