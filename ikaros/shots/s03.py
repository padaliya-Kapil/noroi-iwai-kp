"""S03  The tower on its cliff over the sea.  The camera climbs from the waves to the window where father and son are held; gulls wheel."""
from functools import lru_cache
from shotkit import *

PH = 2400; TX0, TX1, TOP, BASE = 1080, 1400, 300, 1640


def build(cv, h, w):
    bands(cv, [(None, 700, ST.engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c')), (640, 1300, PAL['sky_mid']), (1240, 2000, PAL['sky_lo'])], w, 12)
    sea(cv, 1960, w, h)
    cliff(cv, [(800, h + 60), (850, 1900), (900, 1820), (940, 1760), (1010, 1690), (1050, 1650), (1180, 1635), (1420, 1628), (1530, 1660), (1600, 1720), (1700, 1760), (1790, 1870), (1990, 1930), (1990, h + 60)], 70)
    masonry(cv, TX0, TOP, TX1, BASE, 71)
    for i in range(5):                                                         # crenellations
        x = TX0 - 14 + i * (TX1 - TX0 + 28) / 4.5
        cv.put(mask(lambda c, x=x: (c.rectangle(x, TOP - 52, 46, 56), c.fill())), paper(STONE[i % 5], 80 + i, mottle=.08), edge='torn', seed=80 + i, amp=2.5, rim=1.5, shadow=(3, 4, 2, .3))
    cv.put(mask(lambda c: (c.rectangle(TX0 - 18, TOP - 4, TX1 - TX0 + 36, 22), c.fill())), paper('#9b907c', 86), edge='torn', seed=86, amp=3, rim=2, shadow=(3, 5, 3, .35))
    wx, wy = (TX0 + TX1) / 2, 520
    arch = lambda c: (c.move_to(wx - 62, wy + 90), c.line_to(wx - 62, wy - 20), c.arc(wx, wy - 20, 62, math.pi, 2 * math.pi), c.line_to(wx + 62, wy + 90), c.close_path(), c.fill())
    cv.put(mask(arch), paper('#d6c39a', 87, mottle=.08), edge='cut', seed=87, shadow=(0, 0, 0, 0))
    for i, (x, flip, beard) in enumerate(((wx - 26, False, False), (wx + 26, True, True))):
        figure(cv, (x, wy + 96, D(-90), .3, flip), 610 + i, pose='stand', beard=beard, shadow=(2, 3, 2, .3), move=False)
    cv.put(mask(lambda c: (c.rectangle(wx - 76, wy + 86, 152, 16), c.fill())), paper('#a69a84', 88), edge='torn', seed=88, amp=2, rim=1.5, shadow=(3, 5, 3, .4))


@lru_cache(1)
def page(): return cached('s03', build, PH, W)


def draw(d):
    t = d / FPS; cy = (PH - H) * (1 - ease(.2, 4.6, t))
    cv = Canvas(view(page(), 0, cy), jitter=.45, drawing=d)
    with camera(0, cy):
        if cy > 700: crests(cv, t, [(2040, 170, 15), (2130, 190, 19), (2230, 210, 23)], x1=800)
        for i, (r, ph, h0, s) in enumerate(((330, 0., 520, .9), (420, 2.2, 700, .75), (260, 4.1, 380, .8), (520, 1.1, 1150, .7))):
            a = t * (.7 + .1 * i) + ph; x = (TX0 + TX1) / 2 + r * math.cos(a); y = h0 + r * .28 * math.sin(a)
            if -200 < y - cy < H + 200: gull(cv, x, y, s, t, 900 + i, flip=math.sin(a) > 0)
    return finish(cv, d)
