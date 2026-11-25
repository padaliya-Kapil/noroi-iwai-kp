"""Motion test: three seconds of the style test frame, animated as stop motion.
python ikaros/motion_test.py [--jobs 4]  ->  ikaros/motion_test.mp4

36 drawings at 12 a second, each held for two frames of a 24 fps film.  The page (sky, rays, island, sun, the sea's
sheets) is glued down and never moves; everything that is animated is re-placed by hand on each drawing, so it lands
a fraction of a pixel off its mark, and the exposure flickers a little.
"""
import sys, os, math, time, argparse, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, cv2
from collage import W, H, Canvas, mask, poly, paper, rng, smooth
from figure import Flyer, wing_feathers, lay_feathers, feather_pts, feather_tex, FEATHER_PAPERS, wax, xform, lerp, SEPIA
import style_test as ST

D = math.radians
FPS, DRAWINGS = 12, 36
OUT = os.path.join(HERE, 'out', 'motion')
BG = os.path.join(OUT, 'page.npy')


# ----------------------------------------------------------------------------------------------- the glued page
def page():
    if os.path.exists(BG): return np.load(BG)
    cv = Canvas(paper(ST.PAL['page'], 1, mottle=.05)(H, W, 0, 0))
    ST.sky(cv); ST.rays(cv); ST.island(cv); ST.sun(cv)
    torn = ST.torn_band; wavy = ST.wavy; P = ST.PAL; E = ST.engraved
    torn(cv, wavy(ST.HORIZON, 6, 41), wavy(870, 14, 42), None, 41, tex=E(P['sea1'], 41, pitch=4, width=.25, ink=.3, ink_col='#16242e'), amp=6, rim=3)
    torn(cv, wavy(842, 12, 43), wavy(950, 14, 44), P['sea2'], 43, amp=6, rim=3)
    torn(cv, wavy(918, 12, 45), wavy(1010, 12, 46), None, 45, tex=E(P['sea3'], 45, pitch=5, width=.3, ink=.3, ink_col='#0f1a22'), amp=6, rim=3)
    os.makedirs(OUT, exist_ok=True); np.save(BG, cv.im); return cv.im


# ----------------------------------------------------------------------------------------------- what moves
def rot(p, c, a):
    ca, sa = math.cos(a), math.sin(a); return (c[0] + (p[0] - c[0]) * ca - (p[1] - c[1]) * sa, c[1] + (p[0] - c[0]) * sa + (p[1] - c[1]) * ca)


def beat(t, period, phase=0.):
    return math.sin(2 * math.pi * t / period + phase)


def flyer(cv, xf0, seed, t, period, flap, bob, beard=False, melt=None, shadow=(10, 15, 9, .4), dim_far=.3, flutter=.05):
    """A flyer on its wing beat: the arms swing about the shoulders, the body rides up as the wings come down."""
    melt = melt or {}
    b = beat(t, period); xf = (xf0[0], xf0[1] - bob * beat(t, period, 1.2), xf0[2] + D(1.4) * beat(t, period, .6), xf0[3])
    F0 = Flyer(xf); phi = D(flap) * b
    arm = (F0.arm[0], rot(F0.arm[1], F0.arm[0], phi), rot(F0.arm[2], F0.arm[0], phi * 1.25))
    arm_far = (F0.arm_far[0], rot(F0.arm_far[1], F0.arm_far[0], phi * .9), rot(F0.arm_far[2], F0.arm_far[0], phi * 1.15))
    F = Flyer(xf, seed=seed, beard=beard, arm=arm, arm_far=arm_far); F.move = True
    lay = lambda fs, singe: lay_feathers(cv, fs, singe, shadow, move=True)
    lay(wing_feathers(F.lead(True), xf, seed + 1, dim=dim_far, Lmax=280, flutter=(t, flutter)), melt.get('singe', 0) * .6)
    F.lay_spar(cv, shadow, far=True); F.lay_body(cv, 'far', shadow); F.lay_straps(cv, far=True)
    lay(wing_feathers(F.lead(), xf, seed + 2, skip=melt.get('skip', ()), loose=melt.get('loose', ()), flutter=(t, flutter)), melt.get('singe', 0))
    F.lay_spar(cv, shadow); F.lay_body(cv, 'near', shadow); F.lay_harness(cv, shadow); F.lay_arm(cv, shadow); F.lay_straps(cv)
    L = F.lead(); g0, g1 = math.atan2(.12, -1.), math.atan2(-.62, -.78) + 2 * math.pi; pts = []   # back along the wing, wrapped the short way
    for (a, c), t0 in zip(((L[0], L[1]), (L[1], L[2]), (L[2], L[3])), (0., .4, .8)):
        for u in np.linspace(0, 1, 4)[:-1]:
            p = lerp(a, c, u); g = g0 + (g1 - g0) * (t0 + u * .4); pts.append(xform(xf, (p[0] + 30 * math.cos(g), p[1] + 30 * math.sin(g))))
    wax(cv, pts[1:], seed + 3, drips=melt.get('drips', False), scale=xf[3], t=t if melt.get('drips') else None, move=True)
    F.lay_brads(cv)
    return F


def loose_feather(F, i, n=17, Lmin=95, Lmax=300):
    """Where primary i of the near wing sits now (page coords): centre, angle, length.  Used to hand it over to the air."""
    L = F.lead(); seg = [math.dist(L[k], L[k + 1]) for k in range(3)]; tot = sum(seg); tt = i / (n - 1) * .97 + .02; d = tt * tot
    for k, s in enumerate(seg):
        if d <= s or k == 2: base = lerp(L[k], L[k + 1], min(d / s, 1.)); break
        d -= s
    g0, g1 = math.atan2(.12, -1.), math.atan2(-.62, -.78); g1 += 2 * math.pi if g0 - g1 > math.pi else 0.   # same wrap as the wing
    ang = g0 + (g1 - g0) * tt ** 1.15 + .28
    ln = (Lmin + (Lmax - Lmin) * tt ** .9) * (1 - .38 * smooth(.86, 1., tt))
    c = xform(F.xf, (base[0] + math.cos(ang) * ln * .55, base[1] + math.sin(ang) * ln * .55))
    return c, ang + F.xf[2], ln * F.xf[3]


# a feather in the air: (x, y, angle deg, length, drift x px/s, fall px/s, spin deg/s, sway px, sway phase)
AIR = [(905, 600, 150, 120, -30, 70, 14, 26, 0.), (842, 700, 205, 96, -22, 85, -10, 20, 1.3), (960, 742, 110, 84, -38, 64, 20, 18, 2.1),
       (790, 470, 240, 110, -26, 92, -16, 30, 3.0), (700, 615, 60, 74, -18, 76, 12, 16, 4.2), (1010, 860, 170, 80, -12, 10, 6, 6, .7)]


def air_feather(cv, i, c, ang, L, tex, tau, vx, vy, spin, sway, ph):
    """A cut feather falling: it drifts, sinks, and rocks like a leaf, its tilt following its swing."""
    s = math.sin(1.9 * tau * 2 * math.pi / 2.2 + ph)
    x, y = c[0] + vx * tau + sway * s, c[1] + vy * tau + 20 * tau * tau
    a = ang + D(spin * tau) + D(24) * math.cos(1.9 * tau * 2 * math.pi / 2.2 + ph)
    pts, sp = feather_pts((x - math.cos(a) * L / 2, y - math.sin(a) * L / 2), a, L, min(L * .22, 44), curve=.04 + .03 * s)
    cv.put(mask(lambda cc: (poly(cc, pts), cc.fill())), tex, edge='cut', seed=100 + i, shadow=(9, 13, 7, .32),
           marks=[(mask(lambda cc: (cc.set_line_width(1.2), poly(cc, sp, close=False), cc.stroke())), SEPIA, .5)], singe=.5, wobble=.8, move=True)


def crests(cv, t):
    r = rng(47); cr = []
    for row, (y0, gap, s) in enumerate(((812, 150, 15), (896, 170, 19), (974, 190, 23))):
        shift = (1 if row % 2 else -1) * 26 * t                              # rows slide against each other
        for i, x in enumerate(np.arange(-240 + row * 55, W + 240, gap)):
            cr.append((x + shift + r.uniform(-12, 12), y0 + r.uniform(-5, 5) + 10 * (i % 2) + 2.5 * math.sin(t * 4 + i), s * r.uniform(.9, 1.1)))
    def draw(c):
        for x, y, s in cr:
            c.save(); c.translate(x, y); c.scale(2.2, 1); c.arc(0, 0, s, D(195), D(345)); c.arc_negative(s * .1, s * .34, s * .98, D(338), D(200)); c.close_path(); c.restore(); c.fill()
    cv.put(mask(draw), paper(ST.PAL['foam'], 48), edge='cut', seed=48, shadow=(2, 3, 2, .35), wobble=.5, move=True)


def drawing(d):
    t = d / FPS; out = os.path.join(OUT, 'd%03d.png' % d)
    cv = Canvas(page().copy(), jitter=.45, drawing=d)
    flyer(cv, (440, 560, D(-6), .46), 200, t, period=1.0, flap=14, bob=5, beard=True, shadow=(5, 8, 5, .34), dim_far=.38, flutter=.03)   # Daidalos
    crests(cv, t)
    ST.torn_band(cv, ST.wavy(990, 10, 49), [(-60, H + 60), (W + 60, H + 60)], ST.PAL['sea4'], 49, amp=6, rim=3)
    RELEASE = .75                                                              # the loose primary lets go
    melt = dict(skip=(15, 12) + ((14,) if t >= RELEASE else ()), loose=(14, 10), drips=True, singe=.7)
    F = flyer(cv, (1030, 548, D(-32), 1.1), 300, t, period=1.5, flap=9, bob=8, melt=melt, flutter=.05)   # Ikaros
    r = rng(90)
    for i, (x, y, a, L, vx, vy, spin, sway, ph) in enumerate(AIR):
        col, kind = FEATHER_PAPERS[r.integers(len(FEATHER_PAPERS))]
        air_feather(cv, i, (x, y), D(a), L, feather_tex(kind, col, 100 + i), t, vx, vy, spin, sway, ph)
    if t >= RELEASE:
        if not hasattr(drawing, 'freed'):
            drawing.freed = loose_feather(flyer_probe(RELEASE), 14)
        c, a, L = drawing.freed
        air_feather(cv, 9, c, a, L, feather_tex('plain', '#e6dcc5', 109), t - RELEASE, -110, 95, -55, 24, 0.)
    ST.meander(cv); ST.letters(cv)
    im = cv.finish(seed=9, desat=.12, flicker=.006)
    cv2.imwrite(out, cv2.cvtColor(im, cv2.COLOR_RGB2BGR)); return d


def flyer_probe(t):
    """Ikaros's pose at time t without drawing him (same numbers as in drawing())."""
    xf0, period, flap, bob = (1030, 548, D(-32), 1.1), 1.5, 9, 8
    xf = (xf0[0], xf0[1] - bob * beat(t, period, 1.2), xf0[2] + D(1.4) * beat(t, period, .6), xf0[3])
    F0 = Flyer(xf); phi = D(flap) * beat(t, period)
    return Flyer(xf, arm=(F0.arm[0], rot(F0.arm[1], F0.arm[0], phi), rot(F0.arm[2], F0.arm[0], phi * 1.25)))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--jobs', type=int, default=4); ap.add_argument('--only', type=int); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); t0 = time.time(); page()
    if a.only is not None:
        drawing(a.only); print('drawing', a.only, '%.1fs' % (time.time() - t0)); sys.exit()
    with Pool(a.jobs) as p:
        for d in p.imap_unordered(drawing, range(DRAWINGS)): print('.', end='', flush=True)
    print(' %d drawings %.0fs' % (DRAWINGS, time.time() - t0))
    mp4 = os.path.join(HERE, 'motion_test.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', os.path.join(OUT, 'd%03d.png'), '-vf', 'fps=24,format=yuv420p',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-movflags', '+faststart', mp4], check=True)
    print(mp4, '%.1f MB' % (os.path.getsize(mp4) / 1e6))
