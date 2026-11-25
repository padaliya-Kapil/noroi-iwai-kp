"""S13  The fall.  Bare arms, broken reeds; the strips of sky rush upward past him, then the page itself comes apart into the dark."""
from functools import lru_cache
from shotkit import *

STRIPS = [PAL['sky_hi'], PAL['sky_mid'], PAL['parch'], PAL['sky_lo'], PAL['sky_mid'], '#e2d2ac', PAL['sky_hi'], PAL['sky_lo']]
SH = 240


def build(cv, h, w):
    cv.put(mask(lambda c: (c.rectangle(-20, -20, w + 40, h + 40), c.fill())), lines_print('#231b16', '#0f0b09', seed=130, pitch=7, ang=-8, width=.4, ink=.5), edge='none', shadow=(0, 0, 0, 0))


@lru_cache(1)
def page(): return cached('s13', build)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.5, drawing=d)
    n = len(STRIPS); span = n * SH
    for i, col in enumerate(STRIPS):
        y = (i * SH - 760 * t) % span - SH * .8
        t0 = 2.3 + .2 * ((i * 3) % n); tau = max(0., t - t0); side = -1 if i % 2 else 1
        if tau > 1.6: continue
        dx = side * 900 * tau * tau; rot_ = D(side * 28 * tau); dy = -260 * tau
        top = ST.wavy(y, 18, 140 + i, n=9); bot = ST.wavy(y + SH + 40, 18, 141 + i, n=9)
        def strip(c, top=top, bot=bot, dx=dx, dy=dy, rot_=rot_, y=y):
            c.translate(W / 2 + dx, y + SH / 2 + dy); c.rotate(rot_); c.translate(-W / 2, -(y + SH / 2)); poly(c, top + bot[::-1]); c.fill()
        cv.put(mask(strip), paper(col, 150 + i, mottle=.02) if i % 3 else ST.engraved(col, 150 + i, pitch=4, width=.24, ink=.25),
               edge='torn', seed=150 + i, amp=7, rim=3, shadow=(8, 12, 10, .45), move=tau > 0)
    for j in range(5):
        air_feather(cv, 60 + j, (700 + j * 140, 760 + 60 * j), D(40 * j), 90, t, 20 * (j - 2), -300 - 30 * j, 60, 30, j)
    y = 470 + max(0., t - 4.2) ** 2 * 1500
    F = figure(cv, (960 + 50 * math.sin(t * 1.3), y, D(-150 + 70 * t), .9), 300, pose='fall', shadow=(12, 18, 12, .45))
    F.lay_spar(cv, (8, 12, 8, .4))
    return finish(cv, d)
