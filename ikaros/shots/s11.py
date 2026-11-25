"""S11  At the sun: the style-test frame, alive.  The wax runs; one primary after another tears free and drifts away."""
from shotkit import *
import motion_test as MT

IK = (1030, 548, D(-32), 1.1); RELEASE = [(14, .6), (10, 2.0), (13, 3.3)]


def page(): return MT.page()


def draw(d):
    t = d / FPS; cv = Canvas(MT.page().copy(), jitter=.45, drawing=d)
    winged(cv, (440, 560, D(-6), .46), 200, t, period=1.0, flap=14, bob=5, beard=True, shadow=(5, 8, 5, .34), dim_far=.38, flutter=.03)
    crests(cv, t, [(812, 150, 15), (896, 170, 19), (974, 190, 23)])
    ST.torn_band(cv, ST.wavy(990, 10, 49), [(-60, H + 60), (W + 60, H + 60)], PAL['sea4'], 49, amp=6, rim=3)
    gone = tuple(i for i, t0 in RELEASE if t >= t0)
    winged(cv, IK, 300, t, melt=dict(skip=(15, 12) + gone, loose=(14, 10, 13), drips=True, singe=.75), flutter=.06)
    for i, (x, y, a, L, vx, vy, spin, sway, ph) in enumerate(MT.AIR):
        air_feather(cv, i, (x, y), D(a), L, t, vx, vy, spin, sway, ph)
    for j, (i, t0) in enumerate(RELEASE):
        if t >= t0:
            F = winged(None, IK, 300, t0, dry=True); c, a, L = primary_pose(F, i, extra=.28)
            air_feather(cv, 20 + j, c, a, L, t - t0, -110 + 30 * j, 95, -55 + 30 * j, 24, j * 1.3)
    return finish(cv, d, light='noon')
