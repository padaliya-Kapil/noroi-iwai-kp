"""S10  Ikaros climbs, higher and higher, towards a sun that grows; below, Daidalos calls after him."""
from functools import lru_cache
from shotkit import *

SX, SY = 1610, 190


def build(cv, h, w):
    bands(cv, [(None, 300, ST.engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c')), (260, 640, PAL['sky_lo']), (600, 960, '#e2d2ac')], w, 17)
    rays(cv, SX, SY, n=14, seed=6)
    sea(cv, 930, w, h, seed=46)


@lru_cache(1)
def page(): return cached('s10', build)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    sun(cv, SX, SY, 110 + 110 * ease(0, 5.3, t))
    crests(cv, t, [(985, 190, 16)], speed=60)
    winged(cv, (430, 800 - 20 * t, D(-18), .5), 200, t, period=1.2, flap=12, bob=6, beard=True, shadow=(6, 9, 6, .36))
    u = ease(0, 5.3, t)
    winged(cv, (880 + 380 * u, 680 - 330 * u, D(-28 - 14 * u), .78 - .1 * u), 300, t, period=1.1, flap=13, bob=8, singe=.3 * u, shadow=(10, 15, 9, .4))
    return finish(cv, d, light='late')
