"""S01  Title.  The world in miniature (sky above, sea below); the sun is set in, the label laid, the letters dropped one by one,
the meander slid in beneath."""
from functools import lru_cache
from shotkit import *


def build(cv, h, w):
    bands(cv, [(None, 250, ST.engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c')), (210, 330, PAL['sky_mid'])], w, 11)
    sea(cv, 820, w, h)


@lru_cache(1)
def page(): return cached('s01', build)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    crests(cv, t, [(880, 170, 14), (960, 190, 17)])
    if t >= .35: sun(cv, 960, 230 - 40 * (1 - ease(.35, .7, t)), 92)
    if t >= .8: label(cv, 960, 560, 'ΙΚΑΡΟΣ', hh=110, n=int((t - 1.1) / .3) + 1 if t >= 1.1 else 0, move=True)
    mx = 2200 * (1 - ease(.1, 1.4, t)); meander_band(cv, 1018, x0=-20 + mx, x1=W + 20 + mx)
    return finish(cv, d)
