"""S03  The tower on its cliff over the sea.  The camera climbs from the waves past cloud and stone to the top, then pushes in
to the lit window where father and son are held.  Gulls wheel; a boat passes far out."""
from functools import lru_cache
from shotkit import *

PH = 2000; TX0, TX1, TOP, BASE = 1080, 1400, 300, 1460; SEA = 1720
WX, WY = (TX0 + TX1) / 2, 520


def build(cv, h, w):
    bands(cv, [(None, 600, ST.engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c')), (540, 1150, PAL['sky_mid']), (1100, SEA + 30, PAL['sky_lo'])], w, 12)
    for i, (x, y, cw, ch) in enumerate(((180, 230, 520, 90), (1500, 420, 460, 80), (300, 880, 620, 100), (1560, 1050, 380, 70), (620, 1330, 440, 80))):
        cv.put(mask(lambda c, x=x, y=y, cw=cw, ch=ch: (poly(c, [(x, y + ch), (x + cw * .15, y + ch * .3), (x + cw * .4, y), (x + cw * .7, y + ch * .2), (x + cw, y + ch)]), c.fill())),
               ST.engraved(PAL['parch'], 30 + i, pitch=5, ang=-2, width=.3, ink=.28) if i % 2 else paper('#e9e0cb', 30 + i, mottle=.02), edge='torn', seed=30 + i, amp=9, rim=4, shadow=(5, 8, 6, .25))
    isle = [(60, SEA + 20), (140, SEA - 40), (260, SEA - 70), (380, SEA - 46), (470, SEA + 20)]
    cv.put(mask(lambda c: (poly(c, isle), c.fill())), paper('#b4a07a', 40, mottle=.06), edge='torn', seed=40, amp=5, rim=2.5)
    sea(cv, SEA, w, h)
    cliff(cv, [(800, h + 60), (850, 1700), (900, 1620), (940, 1570), (1010, 1510), (1050, 1475), (1180, 1462), (1420, 1455), (1530, 1480), (1600, 1540), (1700, 1580), (1790, 1690), (1990, 1750), (1990, h + 60)], 70)
    masonry(cv, TX0, TOP, TX1, BASE, 71)
    for y in (760, 1000, 1240):                                               # arrow slits
        cv.put(mask(lambda c, y=y: (c.rectangle(WX - 9, y, 18, 70), c.fill())), slip(50 + y), edge='cut', seed=50 + y, shadow=(0, 0, 0, 0))
    for i in range(5):
        x = TX0 - 14 + i * (TX1 - TX0 + 28) / 4.5
        cv.put(mask(lambda c, x=x: (c.rectangle(x, TOP - 52, 46, 56), c.fill())), paper(STONE[i % 5], 80 + i, mottle=.08), edge='torn', seed=80 + i, amp=2.5, rim=1.5, shadow=(3, 4, 2, .3))
    cv.put(mask(lambda c: (c.rectangle(TX0 - 18, TOP - 4, TX1 - TX0 + 36, 22), c.fill())), paper('#9b907c', 86), edge='torn', seed=86, amp=3, rim=2, shadow=(3, 5, 3, .35))
    arch = lambda c: (c.move_to(WX - 62, WY + 90), c.line_to(WX - 62, WY - 20), c.arc(WX, WY - 20, 62, math.pi, 2 * math.pi), c.line_to(WX + 62, WY + 90), c.close_path(), c.fill())
    cv.put(mask(arch), paper('#d6c39a', 87, mottle=.05), edge='cut', seed=87, shadow=(0, 0, 0, 0))
    cv.put(mask(lambda c: (c.arc(WX, WY + 20, 70, 0, 6.3), c.fill())), paper('#f0dca8', 89, mottle=.03), edge='none', opacity=.35, shadow=(0, 0, 0, 0))
    for i, (x, flip, beard, pose) in enumerate(((WX - 24, False, False, 'stand'), (WX + 26, True, True, dict(POSE['stand'], turn=math.pi / 2 + .25)))):
        figure(cv, (x, WY + 96 - .3 * 4, D(-90), .3, flip), 610 + i, pose=pose, beard=beard, dress='chiton' if beard else None, shadow=(2, 3, 2, .3), move=False)
    cv.put(mask(lambda c: (c.rectangle(WX - 76, WY + 86, 152, 16), c.fill())), paper('#a69a84', 88), edge='torn', seed=88, amp=2, rim=1.5, shadow=(3, 5, 3, .4))


@lru_cache(1)
def page(): return cached('s03', build, PH, W, scale=2)


def cam(t):
    """Climb from the waves to the top (x fixed), then push in on the window."""
    u = ease(.1, 3.3, t); z = ease(3.2, 5.2, t)
    s = 1 + .9 * z
    x0, y0 = 0., (PH - H) * (1 - u)
    x1, y1 = WX - W / (2 * s), WY + 10 - H / (2 * s)
    return x0 + (x1 - x0) * z, y0 + (y1 - y0) * z, s


def boat(cv, x, y, t):
    hull = [(x - 46, y), (x + 46, y), (x + 34, y + 16), (x - 34, y + 16)]
    cv.put(mask(lambda c: (poly(c, hull), c.fill())), slip(60), edge='cut', seed=60, shadow=(2, 3, 2, .3), move=True)
    sail = [(x - 4, y - 4), (x - 4, y - 74 - 3 * math.sin(t * 2)), (x + 38, y - 10)]
    cv.put(mask(lambda c: (poly(c, sail), c.fill())), paper('#e6dbc2', 61), edge='cut', seed=61, shadow=(2, 3, 2, .3), move=True,
           marks=[(mask(lambda c: (c.rectangle(x - 4, y - 50, 40, 6), c.fill())), '#8a3b25', .8)])


def draw(d):
    t = d / FPS; x, y, s = cam(t)
    cv = Canvas(view(page(), x * 2, y * 2, s / 2), jitter=.45, drawing=d)
    with camera(x, y, s):
        if y > PH - H - 500:
            crests(cv, t, [(SEA + 70, 170, 15), (SEA + 160, 190, 19), (SEA + 250, 210, 23)], x1=800)
            boat(cv, 640 - 22 * t, SEA + 42, t)
        for i, (r, ph, h0, sc) in enumerate(((330, 0., 520, .9), (420, 2.2, 700, .75), (260, 4.1, 380, .8), (520, 1.1, 1150, .7), (380, 3.3, 1500, .75))):
            a = t * (.7 + .1 * i) + ph; gx = WX + r * math.cos(a); gy = h0 + r * .28 * math.sin(a)
            if y - 200 < gy < y + H / s + 200: gull(cv, gx, gy, sc, t, 900 + i, flip=math.sin(a) > 0)
    return finish(cv, d)
