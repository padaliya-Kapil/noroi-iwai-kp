"""Style test: Ikaros against the sun, the wax already running.  python ikaros/style_test.py [out.png]

Palette, kept to what an Attic workshop and an old print room would hold: parchment and bone papers, faded stone blue,
fired clay, black slip, sepia engraving, an indigo sea, and gold leaf for the sun alone.
"""
import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
from collage import W, H, Canvas, mask, poly, rect_pts, paper, lines_print, gold, slip, rgb, rng, clip
from figure import Flyer, wing_feathers, lay_feathers, feather_pts, feather_tex, FEATHER_PAPERS, wax, xform, lerp, SEPIA

D = math.radians
SUN, R = (1190, 400), 318
HORIZON = 772
PAL = dict(page='#e6dcc4', sky_hi='#8d9a9b', sky_mid='#adb2a7', sky_lo='#d9ccad', parch='#e8dcc0', clay='#a9583a', clay_dk='#8a4129',
           ochre='#b8975e', straw='#d3c18f', sienna='#a87445', olive='#6c6844', sea1='#3b5866', sea2='#2d4756', sea3='#23394a', sea4='#1a2b38', foam='#e4dac3')


def torn_band(cv, top, bot, col, seed, tex=None, **kw):
    """A sheet torn along both long edges: top and bot are lists of (x, y) running left to right."""
    cv.put(mask(lambda c: (poly(c, top + bot[::-1]), c.fill())), tex or paper(col, seed), edge='torn', seed=seed, **kw)


def wavy(y, a, seed, n=9, x0=-60, x1=W + 60):
    r = rng(seed); return [(float(x), float(y + a * r.uniform(-1, 1))) for x in np.linspace(x0, x1, n)]


def engraved(col, seed, pitch=5, ang=0., width=.3, ink=.35, ink_col=SEPIA):
    return lines_print(col, ink_col, seed=seed, pitch=pitch, ang=ang, width=width, ink=ink)


def sky(cv):
    torn_band(cv, [(-60, -60), (W + 60, -60)], wavy(250, 40, 2), None, 11, tex=engraved(PAL['sky_hi'], 11, pitch=4, ang=-2, width=.22, ink=.22, ink_col='#38464c'), amp=7, rim=3)
    torn_band(cv, wavy(232, 30, 3), wavy(470, 50, 4), PAL['sky_mid'], 12, amp=7, rim=3)
    torn_band(cv, wavy(440, 40, 5), wavy(HORIZON + 30, 10, 6), PAL['sky_lo'], 13, amp=7, rim=3)
    # a strip of an old engraving's sky, slipped in at the top left
    cv.put(mask(lambda c: (poly(c, rect_pts(-40, 196, 640, 150, D(-3))), c.fill())), engraved(PAL['parch'], 3, pitch=5, ang=-3, width=.34, ink=.4, ink_col='#3c4a52'), edge='torn', seed=21, amp=8, rim=3)
    cv.put(mask(lambda c: (poly(c, rect_pts(1520, 612, 500, 64, D(2.5))), c.fill())), engraved('#e3d8bf', 4, pitch=5, width=.32, ink=.38), edge='torn', seed=22, amp=6, rim=3)


def rays(cv):
    r = rng(5); cols = [PAL['ochre'], PAL['straw'], PAL['sienna'], PAL['straw']]; n = 12
    for i in range(n):
        a = D(i * 360 / n + 8 + r.uniform(-5, 5)); half = D(r.uniform(1.3, 2.3)); L = 1500
        pts = [(SUN[0] + math.cos(a) * 120, SUN[1] + math.sin(a) * 120), (SUN[0] + math.cos(a - half) * L, SUN[1] + math.sin(a - half) * L), (SUN[0] + math.cos(a + half) * L, SUN[1] + math.sin(a + half) * L)]
        tex = engraved(PAL['parch'], 40 + i, pitch=4, ang=math.degrees(a), width=.3, ink=.4) if i % 4 == 1 else paper(cols[i % len(cols)], 40 + i, mottle=.05)
        cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), tex, edge='torn', seed=60 + i, amp=5, rim=2.5)


def sun(cv):
    disc = lambda rr, dx=0, dy=0: (lambda c: (c.arc(SUN[0] + dx, SUN[1] + dy, rr, 0, 2 * math.pi), c.fill()))
    cv.put(mask(disc(R + 62)), engraved(PAL['parch'], 8, pitch=4, ang=-30, width=.28, ink=.3), edge='torn', seed=81, amp=8, rim=3.5, shadow=(5, 8, 6, .28))
    cv.put(mask(disc(R + 22, -3, 2)), paper(PAL['clay'], 9, mottle=.07), edge='cut', seed=82, wobble=2.5, shadow=(4, 7, 5, .3))
    cv.put(mask(disc(R + 7, -1, 1)), slip(10), edge='cut', seed=84, wobble=1.5, shadow=(2, 3, 3, .3))
    cv.put(mask(disc(R)), gold(seed=3, center=(SUN[0] - 90, SUN[1] - 110), radius=R * 1.4), edge='cut', seed=83, wobble=2., shadow=(5, 8, 6, .35))


def island(cv):
    pts = [(60, HORIZON + 30), (150, 742), (230, 690), (300, 676), (360, 694), (430, 668), (520, 720), (600, HORIZON + 30)]
    cv.put(mask(lambda c: (poly(c, pts), c.fill())), paper(PAL['ochre'], 31, mottle=.08), edge='torn', seed=31, amp=6, rim=3)
    cv.put(mask(lambda c: (poly(c, [(150, 750), (230, 700), (300, 688), (340, 712), (420, 690), (470, 728), (300, 760)]), c.fill())),
           engraved(PAL['olive'], 5, pitch=4, ang=-20, width=.3, ink=.45, ink_col='#2e2c1c'), edge='torn', seed=32, amp=5, rim=2.5)
    x, y = 302, 676
    def temple(c):
        poly(c, [(x - 34, y - 34), (x, y - 52), (x + 34, y - 34)]); c.fill()
        c.rectangle(x - 36, y - 36, 72, 5); c.fill(); c.rectangle(x - 38, y - 4, 76, 6); c.fill()
        for i in range(5): c.rectangle(x - 30 + i * 14, y - 31, 5, 28); c.fill()
    cv.put(mask(temple), paper('#ece4d2', 33), edge='cut', seed=33, shadow=(2, 3, 2, .4), wobble=.4)


def sea(cv):
    torn_band(cv, wavy(HORIZON, 6, 41), wavy(870, 14, 42), None, 41, tex=engraved(PAL['sea1'], 41, pitch=4, width=.25, ink=.3, ink_col='#16242e'), amp=6, rim=3)
    torn_band(cv, wavy(842, 12, 43), wavy(950, 14, 44), PAL['sea2'], 43, amp=6, rim=3)
    torn_band(cv, wavy(918, 12, 45), wavy(1010, 12, 46), None, 45, tex=engraved(PAL['sea3'], 45, pitch=5, width=.3, ink=.3, ink_col='#0f1a22'), amp=6, rim=3)
    r = rng(47); crests = []
    for row, (y0, gap, s) in enumerate(((812, 150, 15), (896, 170, 19), (974, 190, 23))):
        for i, x in enumerate(np.arange(-40 + row * 55, W + 40, gap)):
            crests.append((x + r.uniform(-12, 12), y0 + r.uniform(-5, 5) + 10 * (i % 2), s * r.uniform(.9, 1.1)))
    def cr(c):
        for x, y, s in crests:
            c.save(); c.translate(x, y); c.scale(2.2, 1); c.arc(0, 0, s, D(195), D(345)); c.arc_negative(s * .1, s * .34, s * .98, D(338), D(200)); c.close_path(); c.restore(); c.fill()
    cv.put(mask(cr), paper(PAL['foam'], 48), edge='cut', seed=48, shadow=(2, 3, 2, .35), wobble=.5)
    torn_band(cv, wavy(990, 10, 49), [(-60, H + 60), (W + 60, H + 60)], PAL['sea4'], 49, amp=6, rim=3)


def meander(cv):
    y, h = 1022, 46; ang = D(-.35)
    def key(c):
        c.save(); c.translate(W / 2, y + h / 2); c.rotate(ang); c.translate(-W / 2, -(y + h / 2)); c.set_line_width(4.5)
        c.move_to(-20, y + 5); c.line_to(W + 20, y + 5); c.stroke(); c.move_to(-20, y + h - 5); c.line_to(W + 20, y + h - 5); c.stroke()
        for u in range(-40, W + 40, 40):
            b, t = y + h - 10, y + 10
            poly(c, [(u, b), (u, t), (u + 30, t), (u + 30, b - 6), (u + 10, b - 6), (u + 10, t + 10), (u + 20, t + 10)], close=False); c.stroke()
            c.move_to(u, b); c.line_to(u + 40, b); c.stroke()
        c.restore()
    cv.put(mask(lambda c: (poly(c, rect_pts(-20, y, W + 40, h, ang)), c.fill())), paper(PAL['clay'], 51, mottle=.06), edge='cut', seed=51, wobble=1.5,
           shadow=(3, -4, 4, .35), marks=[(mask(key), '#1d1612', .93)])


def letters(cv):
    """ΙΚΑΡΟΣ cut from black paper and stuck on a torn label (strokes, not a font)."""
    cv.put(mask(lambda c: (poly(c, rect_pts(60, 58, 450, 120, D(-2.2))), c.fill())), paper(PAL['parch'], 61), edge='torn', seed=61, amp=7, rim=3.5, shadow=(4, 6, 5, .33))
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
    cv.put(mask(lambda c: (poly(c, rect_pts(x, y, w, h, a)), c.fill())), paper('#ddd2b0', seed, mottle=.05, fiber=.02), edge='torn', seed=seed, amp=3, rim=0,
           opacity=.5, shadow=(1, 1, 1, .1))


def flyer(cv, F, seed, melt, shadow, dim_far=.3, wax_scale=1.):
    """Bottom to top: far wing, its spar, far limbs, its straps; near wing, spar, body, harness, arm, straps; wax at the feather roots; fasteners."""
    xf = F.xf; lay = lambda fs, singe: lay_feathers(cv, fs, singe, shadow)
    lay(wing_feathers(F.lead(True), xf, seed + 1, dim=dim_far, Lmax=280), melt.get('singe', 0) * .6)
    F.lay_spar(cv, shadow, far=True); F.lay_body(cv, 'far', shadow); F.lay_straps(cv, far=True)
    lay(wing_feathers(F.lead(), xf, seed + 2, skip=melt.get('skip', ()), loose=melt.get('loose', ())), melt.get('singe', 0))
    F.lay_spar(cv, shadow); F.lay_body(cv, 'near', shadow); F.lay_harness(cv, shadow); F.lay_arm(cv, shadow); F.lay_straps(cv)
    # wax sits just behind the arm, where the quills meet the reed
    L = F.lead(); g0, g1 = math.atan2(.12, -1.), math.atan2(-.62, -.78) + 2 * math.pi; pts = []   # back along the wing, wrapped the short way
    for (a, b), t0 in zip(((L[0], L[1]), (L[1], L[2]), (L[2], L[3])), (0., .4, .8)):
        for u in np.linspace(0, 1, 4)[:-1]:
            p = lerp(a, b, u); g = g0 + (g1 - g0) * (t0 + u * .4); pts.append(xform(xf, (p[0] + 30 * math.cos(g), p[1] + 30 * math.sin(g))))
    wax(cv, pts[1:], seed + 3, drips=melt.get('drips', False), scale=wax_scale * xf[3])
    F.lay_brads(cv)


def falling(cv):
    r = rng(90)
    for i, (x, y, a, L) in enumerate([(905, 600, 150, 120), (842, 700, 205, 96), (960, 742, 110, 84), (790, 470, 240, 110), (700, 615, 60, 74), (1010, 860, 170, 80)]):
        col, kind = FEATHER_PAPERS[r.integers(len(FEATHER_PAPERS))]
        pts, sp = feather_pts((x, y), D(a), L, L * .22, curve=r.uniform(-.06, .08))
        cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), feather_tex(kind, col, 100 + i), edge='cut', seed=100 + i, shadow=(9, 13, 7, .32),
               marks=[(mask(lambda c, sp=sp: (c.set_line_width(1.2), poly(c, sp, close=False), c.stroke())), SEPIA, .5)], singe=.5, wobble=.8)


def main(out):
    t = time.time()
    cv = Canvas(paper(PAL['page'], 1, mottle=.05)(H, W, 0, 0))
    sky(cv); rays(cv); island(cv)
    flyer(cv, Flyer((440, 560, D(-6), .46), seed=200, beard=True), 200, {}, shadow=(5, 8, 5, .34), dim_far=.38)   # Daidalos, lower and level
    sun(cv); sea(cv)
    flyer(cv, Flyer((1030, 548, D(-32), 1.1), seed=300), 300, dict(skip=(15, 12), loose=(14, 10), drips=True, singe=.7), shadow=(10, 15, 9, .4))   # Ikaros at the sun
    falling(cv); meander(cv); letters(cv)
    im = cv.finish(seed=9, desat=.12)
    cv2.imwrite(out, cv2.cvtColor(im, cv2.COLOR_RGB2BGR)); print(out, '%.1fs' % (time.time() - t))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'style_test.png'))
