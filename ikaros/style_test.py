"""Style test: Ikaros against the sun, the wax already running.  python ikaros/style_test.py [out.png]"""
import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
from collage import W, H, Canvas, mask, poly, rect_pts, paper, halftone, lines_print, gold, slip, rgb, rng
from figure import Flyer, wing_feathers, lay_feathers, feather_pts, feather_tex, FEATHER_PAPERS, wax, xform, lerp

D = math.radians
SUN, R = (1190, 400), 330
HORIZON = 772


def torn_band(cv, top, bot, col, seed, tex=None, **kw):
    """A sheet torn along both long edges: top and bot are lists of (x, y) running left to right."""
    m = mask(lambda c: (poly(c, top + bot[::-1]), c.fill()))
    cv.put(m, tex or paper(col, seed), edge='torn', seed=seed, **kw)


def wavy(y, a, seed, n=9, x0=-60, x1=W + 60):
    r = rng(seed); xs = np.linspace(x0, x1, n)
    return [(float(x), float(y + a * r.uniform(-1, 1))) for x in xs]


def sky(cv):
    torn_band(cv, [(-60, -60), (W + 60, -60)], wavy(250, 40, 2) [::-1][::-1], '#86a6b6', 11, amp=8, rim=5)
    torn_band(cv, wavy(232, 30, 3), wavy(470, 50, 4), '#a9c1c7', 12, amp=8, rim=5)
    torn_band(cv, wavy(440, 40, 5), wavy(HORIZON + 30, 10, 6), '#ead9b4', 13, amp=8, rim=5)
    # a scrap of printed sky, dots on cream, slipped in at the top left
    cv.put(mask(lambda c: (poly(c, rect_pts(-40, 170, 620, 210, D(-3))), c.fill())), halftone('#e9e1cd', '#4f7690', lambda h, w, y0, x0: .12 + .5 * np.clip((np.arange(h)[:, None] + y0 - 170) / 260., 0, 1) * np.ones((1, w)), cell=9, ang=15, seed=3),
           edge='torn', seed=21, amp=9, rim=5)
    # engraved cloud strip
    cv.put(mask(lambda c: (poly(c, rect_pts(1500, 610, 520, 70, D(2.5))), c.fill())), lines_print('#efe8d8', '#6b7d88', seed=4, pitch=6, width=.34, ink=.6), edge='torn', seed=22, amp=7)


def rays(cv):
    r = rng(5); cols = ['#e7a93c', '#d8742e', '#f0cf73', '#c4552f', '#e9b955']
    n = 15
    for i in range(n):
        a = D(i * 360 / n + r.uniform(-4, 4)); half = D(r.uniform(1.6, 3.)); L = 1500
        p0 = (SUN[0] + math.cos(a) * 120, SUN[1] + math.sin(a) * 120)
        pts = [p0, (SUN[0] + math.cos(a - half) * L, SUN[1] + math.sin(a - half) * L), (SUN[0] + math.cos(a + half) * L, SUN[1] + math.sin(a + half) * L)]
        col = cols[i % len(cols)]
        tex = halftone('#f3e4b8', '#d0662e', .42, cell=7, ang=30, seed=40 + i) if i % 5 == 3 else paper(col, 40 + i, mottle=.06)
        cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), tex, edge='torn', seed=60 + i, amp=6, rim=3.5)


def sun(cv):
    ring = lambda c: (c.arc(SUN[0], SUN[1], R + 64, 0, 2 * math.pi), c.fill())
    cv.put(mask(ring), halftone('#f4dea0', '#cf5a28', .5, cell=8, ang=45, seed=8), edge='torn', seed=81, amp=9, rim=6, shadow=(5, 8, 6, .3))
    cv.put(mask(lambda c: (c.arc(SUN[0] - 4, SUN[1] + 3, R + 16, 0, 2 * math.pi), c.fill())), paper('#b7432a', 9, mottle=.08), edge='cut', seed=82, wobble=3., shadow=(4, 7, 5, .3))
    cv.put(mask(lambda c: (c.arc(SUN[0], SUN[1], R, 0, 2 * math.pi), c.fill())), gold(seed=3, center=(SUN[0] - 90, SUN[1] - 110), radius=R * 1.4), edge='cut', seed=83, wobble=2.5, shadow=(6, 9, 6, .35))


def island(cv):
    pts = [(60, HORIZON + 30), (150, 742), (230, 690), (300, 676), (360, 694), (430, 668), (520, 720), (600, HORIZON + 30)]
    cv.put(mask(lambda c: (poly(c, pts), c.fill())), paper('#c89a5a', 31, mottle=.1), edge='torn', seed=31, amp=6, rim=3.5)
    cv.put(mask(lambda c: (poly(c, [(150, 750), (230, 700), (300, 688), (340, 712), (420, 690), (470, 728), (300, 760)]), c.fill())), lines_print('#7d7a48', '#3d3b22', seed=5, pitch=4, ang=-20, width=.3, ink=.55), edge='torn', seed=32, amp=5, rim=2.5)
    x, y = 302, 676
    def temple(c):
        poly(c, [(x - 34, y - 34), (x, y - 52), (x + 34, y - 34)]); c.fill()
        c.rectangle(x - 36, y - 36, 72, 5); c.fill(); c.rectangle(x - 38, y - 4, 76, 6); c.fill()
        for i in range(5): c.rectangle(x - 30 + i * 14, y - 31, 5, 28); c.fill()
    cv.put(mask(temple), paper('#f6f1e6', 33), edge='cut', seed=33, shadow=(2, 3, 2, .4), wobble=.4)


def sea(cv):
    torn_band(cv, wavy(HORIZON, 6, 41), wavy(870, 14, 42), '#2f6e92', 41, amp=6, rim=4)
    torn_band(cv, wavy(842, 12, 43), wavy(950, 14, 44), None, 43, tex=halftone('#5d9aaa', '#173c5c', .35, cell=7, ang=15, seed=43), amp=6, rim=4)
    torn_band(cv, wavy(918, 12, 45), wavy(1010, 12, 46), '#1f4c74', 45, amp=6, rim=4)
    r = rng(47); crests = []
    for row, (y0, n) in enumerate(((808, 6), (890, 7), (968, 8))):
        for i in range(n):
            crests.append((r.uniform(0, W), y0 + r.uniform(-14, 14), r.uniform(16, 30) * (1 + row * .25)))
    def cr(c):
        for x, y, s in crests:
            c.save(); c.translate(x, y); c.scale(1.9, 1); c.arc(0, 0, s, D(195), D(345)); c.arc_negative(s * .1, s * .32, s * .98, D(338), D(200)); c.close_path(); c.restore(); c.fill()
    cv.put(mask(cr), paper('#f4efe2', 48), edge='cut', seed=48, shadow=(2, 3, 2, .35), wobble=.5)
    torn_band(cv, wavy(990, 10, 49), [(-60, H + 60), (W + 60, H + 60)], '#163755', 49, amp=6, rim=4)


def meander(cv):
    y, h = 1022, 46; ang = D(-.35)
    band = rect_pts(-20, y, W + 40, h, ang)
    def key(c):
        c.save(); c.translate(W / 2, y + h / 2); c.rotate(ang); c.translate(-W / 2, -(y + h / 2)); c.set_line_width(4.5)
        c.move_to(-20, y + 5); c.line_to(W + 20, y + 5); c.stroke(); c.move_to(-20, y + h - 5); c.line_to(W + 20, y + h - 5); c.stroke()
        for u in range(-40, W + 40, 40):
            b, t = y + h - 10, y + 10
            poly(c, [(u, b), (u, t), (u + 30, t), (u + 30, b - 6), (u + 10, b - 6), (u + 10, t + 10), (u + 20, t + 10)], close=False); c.stroke()
            c.move_to(u, b); c.line_to(u + 40, b); c.stroke()
        c.restore()
    cv.put(mask(lambda c: (poly(c, band), c.fill())), paper('#c1643a', 51, mottle=.06), edge='cut', seed=51, wobble=1.5, shadow=(3, -4, 4, .35),
           marks=[(mask(key), '#201813', .93)])


def letters(cv):
    """ΙΚΑΡΟΣ cut from black paper and stuck on a torn label (strokes, not a font)."""
    lab = rect_pts(60, 58, 450, 120, D(-2.2))
    cv.put(mask(lambda c: (poly(c, lab), c.fill())), paper('#f2e8cf', 61), edge='torn', seed=61, amp=7, rim=5, shadow=(4, 6, 5, .33))
    x0, y0, hh = 92, 86, 66
    G = {'Ι': [[(.08, 0), (.08, 1)]], 'Κ': [[(0, 0), (0, 1)], [(.62, 0), (.05, .55)], [(.25, .38), (.66, 1)]], 'Α': [[(0, 1), (.36, 0), (.72, 1)], [(.17, .62), (.55, .62)]],
         'Ρ': [[(0, 1), (0, 0), (.4, 0), (.58, .12), (.58, .36), (.4, .48), (0, .48)]], 'Ο': 'ring', 'Σ': [[(.6, 0), (0, 0), (.36, .5), (0, 1), (.62, 1)]]}
    r = rng(62); x = x0
    for ch in 'ΙΚΑΡΟΣ':
        g = G[ch]; a = D(r.uniform(-5, 5)); wd = {'Ι': .16, 'Ο': .74, 'Ρ': .6}.get(ch, .72)
        def draw(c, g=g, x=x, a=a, wd=wd):
            c.translate(x + wd * hh / 2, y0 + hh / 2); c.rotate(a + D(-2.2)); c.translate(-wd * hh / 2, -hh / 2); c.set_line_width(hh * .17); c.set_line_cap(0); c.set_line_join(0)
            if g == 'ring': c.save(); c.translate(hh * .37, hh * .5); c.scale(1, 1.32); c.arc(0, 0, hh * .3, 0, 2 * math.pi); c.restore(); c.stroke(); return
            for s in g: poly(c, [(px * hh, py * hh) for px, py in s], close=False); c.stroke()
        cv.put(mask(draw), slip(70 + int(x)), edge='cut', seed=int(x), shadow=(2, 3, 2, .4), wobble=.6)
        x += wd * hh + 20
    tape(cv, 430, 36, 130, 38, D(32), 71); tape(cv, 22, 150, 130, 36, D(28), 72)


def tape(cv, x, y, w, h, a, seed):
    cv.put(mask(lambda c: (poly(c, rect_pts(x, y, w, h, a)), c.fill())), paper('#e9ddb2', seed, mottle=.05, fiber=.02), edge='torn', seed=seed, amp=3, rim=0,
           opacity=.55, shadow=(1, 1, 1, .1))


def flyer(cv, F, seed, melt, shadow, dim_far=.28, wax_scale=1.):
    xf = F.xf; lay = lambda fs, singe: lay_feathers(cv, fs, singe, shadow)
    lay(wing_feathers(F.lead(True), xf, seed + 1, dim=dim_far, Lmax=280, skip=melt.get('skip_far', ())), melt.get('singe', 0) * .6)
    F.lay_body(cv, 'far', shadow)
    lay(wing_feathers(F.lead(), xf, seed + 2, skip=melt.get('skip', ()), loose=melt.get('loose', ())), melt.get('singe', 0))
    F.lay_body(cv, 'near', shadow)
    F.lay_arm(cv, shadow)
    s, e, w, t = F.lead(); pts = [xform(xf, lerp(a, b, u)) for a, b in ((s, e), (e, w), (w, t)) for u in np.linspace(0, 1, 5)[:-1]]
    wax(cv, pts, seed + 3, drips=melt.get('drips', False), scale=wax_scale * xf[3])
    F.lay_brads(cv)


def falling(cv):
    r = rng(90)
    for i, (x, y, a, L) in enumerate([(905, 600, 150, 120), (842, 700, 205, 96), (960, 742, 110, 84), (790, 470, 240, 110), (700, 615, 60, 74), (1010, 860, 170, 80)]):
        col, kind = FEATHER_PAPERS[r.integers(len(FEATHER_PAPERS))]
        pts, sp = feather_pts((x, y), D(a), L, L * .22, curve=r.uniform(-.06, .08))
        cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), feather_tex(kind, col, 100 + i), edge='cut', seed=100 + i, shadow=(9, 13, 7, .32),
               marks=[(mask(lambda c, sp=sp: (c.set_line_width(1.2), poly(c, sp, close=False), c.stroke())), '#4b3a2a', .55)], singe=.6, wobble=.8)


def main(out):
    t = time.time()
    cv = Canvas(paper('#efe7d4', 1, mottle=.05)(H, W, 0, 0))
    sky(cv); rays(cv); island(cv)
    # Daidalos, lower and level, wings whole
    flyer(cv, Flyer((440, 560, D(-6), .46), seed=200, beard=True), 200, {}, shadow=(5, 8, 5, .34), dim_far=.35)
    sun(cv); sea(cv)
    # Ikaros at the sun: tips going, wax running
    flyer(cv, Flyer((1030, 548, D(-32), 1.1), seed=300), 300, dict(skip=(15, 12), loose=(14, 10), drips=True, singe=.9), shadow=(10, 15, 9, .4))
    falling(cv); meander(cv); letters(cv)
    im = cv.finish(seed=9)
    cv2.imwrite(out, cv2.cvtColor(im, cv2.COLOR_RGB2BGR)); print(out, '%.1fs' % (time.time() - t))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'style_test.png'))
