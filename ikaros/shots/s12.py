"""S12  Close, against the gold: the wing comes apart feather after feather, the wax running in long drips."""
from functools import lru_cache
from shotkit import *

IK = (1005, 934, D(-25), 2.0)
ORDER = [16, 14, 13, 11, 10, 9, 8, 7, 6, 5, 4]


def build(cv, h, w):
    bands(cv, [(None, 400, PAL['sky_lo']), (360, 800, '#e2d2ac'), (760, 1200, PAL['sky_lo'])], w, 18)
    rays(cv, 1900, 420, n=16, seed=7, L=2600)
    sun(cv, 1900, 420, 1250, seed=5)


@lru_cache(1)
def page(): return cached('s12', build)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.5, drawing=d)
    times = [.3 + .4 * k for k in range(len(ORDER))]
    gone = tuple(i for i, t0 in zip(ORDER, times) if t >= t0)
    winged(cv, IK, 300, t, period=2.2, flap=6, bob=6, melt=dict(skip=(15, 12) + gone, skip_far=gone[::2] + tuple(range(17))[17 - int(12 * ease(1.0, 4.6, t)):], drips=True, singe=.9, shed=.85 * ease(1.4, 4.8, t)), flutter=.08, shadow=(16, 22, 12, .42))
    for j, (i, t0) in enumerate(zip(ORDER, times)):
        if t >= t0:
            F = winged(None, IK, 300, t0, period=2.2, flap=6, bob=6, dry=True); c, a, L = primary_pose(F, i)
            air_feather(cv, 40 + j, c, a, L, t - t0, -330 - 40 * (j % 3), 120, -90 + 40 * (j % 2), 30, j, singe=.9, grav=70, scale=2.)
    return finish(cv, d)
