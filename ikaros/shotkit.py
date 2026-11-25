"""Shared pieces for the shots: cached pages, winged figures, gulls, tower and cliff, the Labyrinth, candle, splash, feathers."""
import os, math
import numpy as np, cv2
from collage import (CAM, W, H, Canvas, mask, poly, rect_pts, paper, lines_print, gold, slip, rgb, rng, smooth, clip, camera, surface, view)
from figure import (Flyer, POSE, wing_feathers, lay_feathers, feather_pts, feather_tex, FEATHER_PAPERS, wax, xform, lerp, limb_path, SEPIA, CLAY)
import style_test as ST

D = math.radians
PAL = ST.PAL
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'out', 'cache')
FPS = 12


def ease(a, b, t):
    return smooth(a, b, t)


def cached(name, build, h=H, w=W, scale=1):
    """A static page, built once inside a surface of its own size and kept on disk.
    scale 2 builds it at twice the resolution (page coordinates unchanged), for shots that zoom in."""
    p = os.path.join(CACHE, name + '.npy')
    if os.path.exists(p): return np.load(p, mmap_mode='r')
    os.makedirs(CACHE, exist_ok=True)
    with surface(h * scale, w * scale):
        CAM[:] = [0., 0., float(scale)]
        cv = Canvas(paper(PAL['page'], 1, mottle=.018, cell=260)(h * scale, w * scale, 0, 0)); build(cv, h, w)
    q = p + '.%d.npy' % os.getpid(); np.save(q, cv.im); os.replace(q, p); return cv.im


# the light of the day, as a grade over the whole page: (multiply r, g, b), lift towards a colour, desaturation
LIGHT = dict(
    dawn=((1.0, .94, .95), ('#f0b8a0', .06), .14),      # cool and rosy, the sun just up
    morning=((1.02, 1.0, .97), ('#f3dcb0', .03), .12),
    late=((1.05, 1.0, .9), ('#f5d79a', .05), .14),      # late morning: warming
    noon=((1.08, 1.03, .84), ('#fff0c8', .09), .22),    # white heat: bleached, blue burnt out of it
    hot=((1.1, 1.02, .8), ('#fff2cc', .12), .24),
    afternoon=((1.06, .98, .86), ('#f0c890', .05), .16),
    sunset=((1.06, .9, .88), ('#e8905a', .07), .1),
)


def finish(cv, d, desat=.12, light=None):
    if light:
        (mr, mg, mb), (lc, lk), desat = LIGHT[light]
        cv.im = cv.im * np.array([mr, mg, mb], np.float32) * (1 - lk) + rgb(lc) * lk
    return cv.finish(seed=9, desat=desat, flicker=.006)


def bands(cv, spec, w, seed, amp=7, rim=3):
    """Torn horizontal sheets: spec = [(top_y, bottom_y, colour or texture), ...] across width w."""
    for i, (y0, y1, col) in enumerate(spec):
        top = [(-60, -200)] if y0 is None else ST.wavy(y0, 26, seed + 2 * i, n=max(5, w // 220), x1=w + 60)
        bot = [(-60, y1)] if False else ST.wavy(y1, 26, seed + 2 * i + 1, n=max(5, w // 220), x1=w + 60)
        if y0 is None: top = [(-60, -200), (w + 60, -200)]
        cv.put(mask(lambda c, top=top, bot=bot: (poly(c, top + bot[::-1]), c.fill())), col if callable(col) else paper(col, seed + i, mottle=.022, cell=140),
               edge='torn', seed=seed + i, amp=amp, rim=rim)


def sea(cv, top, w, h, seed=41):
    E = ST.engraved
    spec = [(top, top + 100, E(PAL['sea1'], seed, pitch=4, width=.25, ink=.3, ink_col='#16242e')), (top + 70, top + 180, PAL['sea2']),
            (top + 150, top + 240, E(PAL['sea3'], seed + 1, pitch=5, width=.3, ink=.3, ink_col='#0f1a22')), (top + 220, h + 80, PAL['sea4'])]
    bands(cv, spec, w, seed, amp=6)


def crests(cv, t, rows, w=W, seed=47, speed=26, move=True, x1=None):
    """Cut paper wave crests: rows = [(y, gap, size), ...]; alternate rows slide against each other."""
    r = rng(seed); cr = []
    for row, (y0, gap, s) in enumerate(rows):
        shift = (1 if row % 2 else -1) * speed * t
        for i, x in enumerate(np.arange(-400 + row * 55, w + 400, gap)):
            cr.append((x + shift % gap - gap / 2 + r.uniform(-12, 12), y0 + r.uniform(-5, 5) + 10 * (i % 2) + 2.5 * math.sin(t * 4 + i), s * r.uniform(.9, 1.1)))
    def draw(c):
        for x, y, s in cr:
            if x1 is not None and x + s * 2.2 > x1: continue
            c.save(); c.translate(x, y); c.scale(2.2, 1); c.arc(0, 0, s, D(195), D(345)); c.arc_negative(s * .1, s * .34, s * .98, D(338), D(200)); c.close_path(); c.restore(); c.fill()
    cv.put(mask(draw), paper(PAL['foam'], 48), edge='cut', seed=48, shadow=(2, 3, 2, .35), wobble=.5, move=move)


def sun(cv, x, y, R, seed=3, ring=True, tint=None):
    disc = lambda rr, dx=0, dy=0: (lambda c: (c.arc(x + dx, y + dy, rr, 0, 2 * math.pi), c.fill()))
    if ring: cv.put(mask(disc(R * 1.19)), ST.engraved(PAL['parch'], 8, pitch=4, ang=-30, width=.28, ink=.3), edge='torn', seed=81, amp=8, rim=3.5, shadow=(5, 8, 6, .28))
    cv.put(mask(disc(R * 1.07, -3, 2)), paper(PAL['clay'], 9, mottle=.07), edge='cut', seed=82, wobble=2.5, shadow=(4, 7, 5, .3))
    cv.put(mask(disc(R * 1.022, -1, 1)), slip(10), edge='cut', seed=84, wobble=1.5, shadow=(2, 3, 3, .3))
    cv.put(mask(disc(R)), gold(seed=seed, center=(x - R * .28, y - R * .35), radius=R * 1.4), edge='cut', seed=83, wobble=2., shadow=(5, 8, 6, .35))
    if tint:                                                                    # a glaze over the leaf: rose at dawn, red at sunset
        cv.put(mask(disc(R * .99)), paper(tint[0], 85, mottle=.05), edge='none', opacity=tint[1], shadow=(0, 0, 0, 0))


def rays(cv, x, y, n=12, seed=5, L=2200):
    r = rng(seed); cols = [PAL['ochre'], PAL['straw'], PAL['sienna'], PAL['straw']]
    for i in range(n):
        a = D(i * 360 / n + 8 + r.uniform(-5, 5)); half = D(r.uniform(1.3, 2.3))
        pts = [(x + math.cos(a) * 120, y + math.sin(a) * 120), (x + math.cos(a - half) * L, y + math.sin(a - half) * L), (x + math.cos(a + half) * L, y + math.sin(a + half) * L)]
        tex = ST.engraved(PAL['parch'], 40 + i, pitch=4, ang=math.degrees(a), width=.3, ink=.4) if i % 4 == 1 else paper(cols[i % 4], 40 + i, mottle=.05)
        cv.put(mask(lambda c, pts=pts: (poly(c, pts), c.fill())), tex, edge='torn', seed=60 + i, amp=5, rim=2.5)


# ----------------------------------------------------------------------------------------------- figures
def rot(p, c, a):
    ca, sa = math.cos(a), math.sin(a); return (c[0] + (p[0] - c[0]) * ca - (p[1] - c[1]) * sa, c[1] + (p[0] - c[0]) * sa + (p[1] - c[1]) * ca)


def beat(t, period, phase=0.):
    return math.sin(2 * math.pi * t / period + phase)


def kick(leg, hip, knee, ankle):
    h, k, a, t = leg; k = rot(k, h, hip); a = rot(a, h, hip); t = rot(t, h, hip)
    a = rot(a, k, knee); t = rot(t, k, knee); t = rot(t, a, ankle); return (h, k, a, t)


def pose_mix(p, q, u):
    """Blend two poses (dicts of joint chains and turn)."""
    P, Q = POSE[p] if isinstance(p, str) else p, POSE[q] if isinstance(q, str) else q; u = smooth(0, 1, u); out = {}
    for k in ('arm', 'arm_far', 'leg', 'leg_far'):
        out[k] = tuple(lerp(a, b, u) for a, b in zip(P[k], Q[k]))
    out['turn'] = P.get('turn', 0.) * (1 - u) + Q.get('turn', 0.) * u
    return out


def figure(cv, xf, seed, pose='stand', shadow=(6, 9, 6, .36), move=True, **kw):
    """A wingless figure.  pose: a POSE name or a dict from pose_mix."""
    P = POSE[pose] if isinstance(pose, str) else pose
    F = Flyer(xf, seed=seed, arm=P['arm'], arm_far=P['arm_far'], leg=P['leg'], leg_far=P['leg_far'], turn=P.get('turn', 0.), **kw); F.move = move
    F.lay_body(cv, 'far', shadow); F.lay_body(cv, 'near', shadow); F.lay_arm(cv, shadow); F.lay_brads(cv)
    return F


def winged(cv, xf0, seed, t, period=1.5, flap=9, bob=8, pose='fly', melt=None, shadow=(10, 15, 9, .4), dim_far=.3, flutter=.05,
           beard=False, kick_amt=1., folded=False, wing_n=None, a0=None, a1=None, singe=None, wax_on=True, move=True, dry=False, **kw):
    """A flyer on its wing beat.  folded: wings hanging from lowered arms (standing).  wing_n: lay only the first n feathers (building)."""
    melt = melt or {}
    xf = (xf0[0], xf0[1] - bob * beat(t, period, 1.2), xf0[2] + D(1.4) * beat(t, period, .6) * (bob > 0), xf0[3]) + tuple(xf0[4:])
    P = POSE[pose] if isinstance(pose, str) else pose
    phi = D(flap) * beat(t, period)
    arm = (P['arm'][0], rot(P['arm'][1], P['arm'][0], phi), rot(P['arm'][2], P['arm'][0], phi * 1.25))
    arm_far = (P['arm_far'][0], rot(P['arm_far'][1], P['arm_far'][0], phi * .9), rot(P['arm_far'][2], P['arm_far'][0], phi * 1.15))
    leg = kick(P['leg'], D(2.) * kick_amt * beat(t, period, 2.4), D(3.) * kick_amt * beat(t, period, 3.), D(5.) * kick_amt * beat(t, period, 3.4))
    leg_far = kick(P['leg_far'], D(4.) * kick_amt * beat(t, period, .9), D(11.) * kick_amt * beat(t, period, 1.5), D(9.) * kick_amt * beat(t, period, 2.))
    F = Flyer(xf, seed=seed, beard=beard, arm=arm, arm_far=arm_far, leg=leg, leg_far=leg_far, turn=P.get('turn', 0.), **kw); F.move = move
    if dry: return F
    if folded: a0, a1 = a0 or (-1., -.35), a1 or (-.9, -.75)
    wk = dict(a0=a0 or (-1., .12), a1=a1 or (-.78, -.62))
    lay = lambda fs, sg: lay_feathers(cv, fs[:wing_n] if wing_n is not None else fs, sg, shadow, move=move)
    sg = melt.get('singe', 0) if singe is None else singe
    lay(wing_feathers(F.lead(True), xf, seed + 1, dim=dim_far, Lmax=280, flutter=(t, flutter), skip=melt.get('skip_far', ()), shed=melt.get('shed', 0.) * .9, **wk), sg * .6)
    F.lay_spar(cv, shadow, far=True); F.lay_body(cv, 'far', shadow); F.lay_straps(cv, far=True)
    lay(wing_feathers(F.lead(), xf, seed + 2, skip=melt.get('skip', ()), loose=melt.get('loose', ()), flutter=(t, flutter), shed=melt.get('shed', 0.), **wk), sg)
    F.lay_spar(cv, shadow); F.lay_body(cv, 'near', shadow); F.lay_harness(cv, shadow); F.lay_arm(cv, shadow); F.lay_straps(cv)
    if wax_on:
        L = F.lead(); g0 = math.atan2(wk['a0'][1], wk['a0'][0]); g1 = math.atan2(wk['a1'][1], wk['a1'][0])
        if g0 - g1 > math.pi: g1 += 2 * math.pi
        if g1 - g0 > math.pi: g1 -= 2 * math.pi
        pts = []
        for (a, c), t0 in zip(((L[0], L[1]), (L[1], L[2]), (L[2], L[3])), (0., .4, .8)):
            for u in np.linspace(0, 1, 4)[:-1]:
                p = lerp(a, c, u); g = g0 + (g1 - g0) * (t0 + u * .4); pts.append(xform(xf, (p[0] + 30 * math.cos(g), p[1] + 30 * math.sin(g))))
        wax(cv, pts[1:], seed + 3, drips=melt.get('drips', False), scale=xf[3], t=t if melt.get('drips') else None, move=move)
    F.lay_brads(cv)
    return F


def primary_pose(F, i, n=17, Lmin=95, Lmax=300, a0=(-1., .12), a1=(-.78, -.62), extra=0.):
    """Where primary i of a near wing sits (page coords): centre, angle, length.  Hands a feather from the wing to the air."""
    L = F.lead(); seg = [math.dist(L[k], L[k + 1]) for k in range(3)]; tot = sum(seg); tt = i / (n - 1) * .97 + .02; d = tt * tot
    for k, s in enumerate(seg):
        if d <= s or k == 2: base = lerp(L[k], L[k + 1], min(d / s, 1.)); break
        d -= s
    g0, g1 = math.atan2(a0[1], a0[0]), math.atan2(a1[1], a1[0])
    if g0 - g1 > math.pi: g1 += 2 * math.pi
    ang = g0 + (g1 - g0) * tt ** 1.15 + extra
    ln = (Lmin + (Lmax - Lmin) * tt ** .9) * (1 - .38 * smooth(.86, 1., tt))
    c = xform(F.xf, (base[0] + math.cos(ang) * ln * .55, base[1] + math.sin(ang) * ln * .55))
    return c, ang + F.xf[2], ln * F.xf[3]


def air_feather(cv, i, c, ang, L, tau, vx, vy, spin, sway, ph, tex=None, singe=.5, grav=20., move=True, scale=1.):
    """A cut feather falling: it drifts, sinks and rocks like a leaf."""
    if tex is None:
        col, kind = FEATHER_PAPERS[rng(500 + i).integers(len(FEATHER_PAPERS))]; tex = feather_tex(kind, col, 100 + i)
    s = math.sin(1.9 * tau * 2 * math.pi / 2.2 + ph)
    x, y = c[0] + vx * tau + sway * s, c[1] + vy * tau + grav * tau * tau
    a = ang + D(spin * tau) + D(24) * math.cos(1.9 * tau * 2 * math.pi / 2.2 + ph)
    pts, sp = feather_pts((x - math.cos(a) * L / 2, y - math.sin(a) * L / 2), a, L, min(L * .22, 44), curve=.04 + .03 * s)
    cv.put(mask(lambda cc: (poly(cc, pts), cc.fill())), tex, edge='cut', seed=100 + i, shadow=(int(9 * scale), int(13 * scale), 7 * scale, .32),
           marks=[(mask(lambda cc: (cc.set_line_width(1.2), poly(cc, sp, close=False), cc.stroke())), SEPIA, .5)], singe=singe, wobble=.8, move=move)
    return x, y


# ----------------------------------------------------------------------------------------------- creatures and things
def gull(cv, x, y, s, t, seed, flip=False, period=.7, move=True):
    """A gull cut from ivory paper, wing tips inked black, beak in ochre; wings beat about the shoulder."""
    f = -1 if flip else 1; ph = rng(seed).uniform(0, 6.3); b = math.sin(2 * math.pi * t / period + ph)
    P = lambda px, py: (x + f * px * s, y + py * s)
    up = D(-38) * b
    def wing(c, far):
        sh = P(-4, -6 if not far else -10); a = (-1.75 if not far else -1.9) + up * (1 if not far else .8)
        el = (sh[0] + f * math.cos(a) * 36 * s, sh[1] + math.sin(a) * 36 * s); a2 = a + (-.5 if b > 0 else .35)
        tip = (el[0] + f * math.cos(a2) * 46 * s, el[1] + math.sin(a2) * 46 * s)
        poly(c, [(sh[0] - f * 14 * s, sh[1]), el, tip, (el[0] + f * 10 * s, el[1] + 10 * s), (sh[0] + f * 14 * s, sh[1] + 4 * s)]); c.fill()
        return tip
    tips = []
    def far(c): tips.append(wing(c, True))
    cv.put(mask(far), paper('#cfc8b8', seed), edge='cut', seed=seed, shadow=(3, 5, 3, .3), wobble=.3, move=move,
           marks=[(mask(lambda c: [(c.arc(*tp, 13 * s, 0, 6.3), c.fill()) for tp in tips[:1]]), '#1d1714', .9)])
    def body(c):
        c.save(); c.translate(*P(0, 0)); c.scale(30 * s, 11 * s); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); c.fill()
        c.arc(*P(26, -6), 8.5 * s, 0, 2 * math.pi); c.fill(); poly(c, [P(-24, -4), P(-46, -10), P(-44, 6), P(-22, 6)]); c.fill()
    cv.put(mask(body), paper('#ece5d4', seed + 1), edge='cut', seed=seed + 1, shadow=(3, 5, 3, .3), wobble=.3, move=move,
           marks=[(mask(lambda c: (c.arc(*P(29, -8), 1.6 * s, 0, 6.3), c.fill())), '#1d1714', 1.),
                  (mask(lambda c: (poly(c, [P(32, -9), P(46, -4), P(33, -2)]), c.fill())), '#c99a43', 1.)])
    tips2 = []
    def near(c): tips2.append(wing(c, False))
    cv.put(mask(near), paper('#f0e9d8', seed + 2), edge='cut', seed=seed + 2, shadow=(4, 6, 3, .32), wobble=.3, move=move,
           marks=[(mask(lambda c: [(c.arc(*tp, 14 * s, 0, 6.3), c.fill()) for tp in tips2[:1]]), '#1d1714', .9)])


STONE = ['#b6ab95', '#a69a84', '#c2b7a1', '#9b907c', '#ada28c']


def masonry(cv, x0, y0, x1, y1, seed, row=46, shade_right=True, hole=None, dim=0., mortar=None):
    """A wall of torn stone blocks, coursed, each its own scrap of paper.  mortar: a backing sheet showing between the stones."""
    r = rng(seed); y = y0; k = 0
    if mortar:
        cv.put(mask(lambda c: (c.save(), c.rectangle(x0, y0, x1 - x0, y1 - y0), (c.set_fill_rule(1), hole(c)) if hole else None, c.fill(), c.restore())),
               paper(mortar, seed + 999, mottle=.05), edge='none', shadow=(0, 0, 0, 0))
    while y < y1:
        x = x0 - r.uniform(0, 60)
        while x < x1:
            bw = r.uniform(70, 125); col = STONE[r.integers(len(STONE))]
            if dim: col = '#' + ''.join('%02x' % int(v * 255 * (1 - dim)) for v in rgb(col))
            pts = rect_pts(x + 2, y + 2, bw - 4, row - 4, D(r.uniform(-1, 1)))
            def clipr(c):
                c.rectangle(x0, y0, x1 - x0, y1 - y0)
                if hole: c.set_fill_rule(1); hole(c)                            # even-odd: the window is cut out of the wall
                c.clip()
            cv.put(mask(lambda c, pts=pts: (c.save(), clipr(c), poly(c, pts), c.fill(), c.restore())),
                   paper(col, seed * 100 + k, mottle=.08), edge='torn', seed=seed * 100 + k, amp=2.5, rim=1.5, shadow=(2, 3, 2, .3))
            x += bw; k += 1
        y += row
    if shade_right and not hole:
        sh = [(x1 - (x1 - x0) * .28, y0), (x1, y0), (x1, y1), (x1 - (x1 - x0) * .28, y1)]
        cv.put(mask(lambda c: (poly(c, sh), c.fill())), lines_print('#3a3128', '#1d1714', seed=seed, pitch=5, ang=70, width=.5, ink=.6), edge='none', opacity=.28, shadow=(0, 0, 0, 0))


def cliff(cv, pts, seed, cols=('#9c8a6a', '#b39f7c', '#857458', '#a8936f', '#94825f')):
    """A crag: a jagged torn outline, laid in horizontal strata of different papers, with a shaded face."""
    r = rng(seed); jag = [pts[0]]
    for p, q in zip(pts, pts[1:]):
        for u in (.33, .66): jag.append((p[0] + (q[0] - p[0]) * u + r.normal(0, 14), p[1] + (q[1] - p[1]) * u + r.normal(0, 18)))
        jag.append(q)
    outline = lambda c: poly(c, jag)
    cv.put(mask(lambda c: (outline(c), c.fill())), paper(cols[0], seed, mottle=.07), edge='torn', seed=seed, amp=8, rim=3, shadow=(6, 9, 7, .35))
    top = min(p[1] for p in jag); bot = max(p[1] for p in jag); y = top + r.uniform(30, 60); k = 1
    while y < bot:
        hgt = r.uniform(50, 110); yy = y
        band = ST.wavy(yy, 10, seed + 10 * k, n=12, x0=0, x1=2000) + ST.wavy(yy + hgt, 10, seed + 10 * k + 1, n=12, x0=0, x1=2000)[::-1]
        col = cols[k % len(cols)]
        tex = lines_print(col, '#3b3226', seed=seed + k, pitch=5, ang=-12 + 9 * (k % 3), width=.28, ink=.35) if k % 2 else paper(col, seed + k, mottle=.08)
        cv.put(mask(lambda c, band=band: (c.save(), outline(c), c.clip(), poly(c, band), c.fill(), c.restore())), tex, edge='torn', seed=seed + k, amp=5, rim=2.5, shadow=(3, 5, 4, .3))
        y += hgt + r.uniform(-10, 25); k += 1
    xs = [p[0] for p in jag]; cx = (min(xs) + max(xs)) / 2
    cv.put(mask(lambda c: (c.save(), outline(c), c.clip(), c.rectangle(cx + 120, top - 50, 2000, 3000), c.fill(), c.restore())),
           lines_print('#2e261d', '#120d09', seed=seed + 99, pitch=5, ang=65, width=.5, ink=.6), edge='none', opacity=.25, shadow=(0, 0, 0, 0))


def maze(n, seed):
    """Wall segments (cell units) of a perfect maze on an n x n grid, ordered from the centre outwards."""
    r = rng(seed); seen = {(n // 2, n // 2)}; stack = [(n // 2, n // 2)]; open_ = set()
    while stack:
        x, y = stack[-1]; nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < n and 0 <= y + dy < n and (x + dx, y + dy) not in seen]
        if not nb: stack.pop(); continue
        q = nb[r.integers(len(nb))]; open_.add(frozenset(((x, y), q))); seen.add(q); stack.append(q)
    walls = []
    for x in range(n):
        for y in range(n):
            if x + 1 < n and frozenset(((x, y), (x + 1, y))) not in open_: walls.append(((x + 1, y), (x + 1, y + 1)))
            if y + 1 < n and frozenset(((x, y), (x, y + 1))) not in open_: walls.append(((x, y + 1), (x + 1, y + 1)))
    for i in range(n):
        if i != 0: walls.append(((i, 0), (i + 1, 0)))
        walls.append(((i, n), (i + 1, n)))
        walls.append(((0, i), (0, i + 1)))
        if i != n - 1: walls.append(((n, i), (n, i + 1)))
    c = n / 2; walls.sort(key=lambda w: max(abs((w[0][0] + w[1][0]) / 2 - c), abs((w[0][1] + w[1][1]) / 2 - c)) + rng(hash(w) & 0xffff).uniform(0, .4))
    return walls


def candle(cv, x, y, t, d, s=1.):
    """A tallow candle and its flame, the flame re-cut on every drawing; returns the flame tip for the glow."""
    cv.put(mask(lambda c: (c.rectangle(x - 13 * s, y - 120 * s, 26 * s, 120 * s), c.fill(), c.arc(x - 8 * s, y - 100 * s, 5 * s, 0, 6.3), c.fill())),
           paper('#e9dfc6', 301), edge='cut', seed=301, shadow=(4, 6, 4, .35))
    cv.put(mask(lambda c: (c.save(), c.translate(x, y), c.scale(1, .32), c.arc(0, 0, 44 * s, 0, 6.3), c.restore(), c.fill())), paper(PAL['clay'], 302), edge='cut', seed=302, shadow=(4, 6, 4, .35))
    r = rng(d * 13 + 7); lean = r.normal(0, .12) + .1 * math.sin(t * 5); h = (62 + r.normal(0, 4)) * s; base = (x, y - 122 * s)
    for k, (col, sc) in enumerate((('#b9772e', 1.), ('#e2b35a', .74), ('#f6ecd2', .45))):
        hh = h * sc; ww = 17 * s * sc; tip = (base[0] + math.sin(lean) * hh, base[1] - math.cos(lean) * hh)
        def fl(c, hh=hh, ww=ww, tip=tip):
            c.move_to(*tip); c.curve_to(base[0] + ww * 1.3, base[1] - hh * .45, base[0] + ww, base[1] + ww * .3, base[0], base[1] + ww * .45)
            c.curve_to(base[0] - ww, base[1] + ww * .3, base[0] - ww * 1.3, base[1] - hh * .45, *tip); c.close_path(); c.fill()
        cv.put(mask(fl), paper(col, 303 + k, mottle=.05), edge='torn', seed=303 + k + d * 3, amp=2, rim=0, shadow=(0, 0, 0, 0), opacity=.92)
    return (base[0] + math.sin(lean) * h * .5, base[1] - h * .45)


def glow(cv, x, y, r, k, col='#f2c46a'):
    """Warm light falling on the page around a flame (added, so it lifts the paper rather than painting it)."""
    X, Y = np.meshgrid(np.arange(cv.w, dtype=np.float32), np.arange(cv.h, dtype=np.float32))
    g = np.exp(-((X - x) ** 2 + (Y - y) ** 2) / (2 * r * r))[..., None]
    cv.im = cv.im * (1 - .35 * k + .35 * k * g) + rgb(col) * g * k * .22


def splash(cv, x, y, u, s=1., seed=0):
    """The splash as cut paper: a crown that rises (u 0..1) and sinks (u 1..2), drops thrown on arcs."""
    if u <= 0: return
    hgt = s * 260 * math.sin(math.pi * min(u, 2.) / 2) ** .7; wid = s * (140 + 120 * min(u, 2.) / 2)
    if hgt > 4:
        r = rng(seed); n = 9
        def crown(c):
            c.move_to(x - wid, y)
            for i in range(n + 1):
                px = x - wid + 2 * wid * i / n; peak = hgt * (.45 + .55 * math.sin(math.pi * i / n)) * r.uniform(.75, 1.1)
                c.curve_to(px - wid / n * .6, y - peak * .12, px - wid / n * .15, y - peak * .7, px + r.uniform(-6, 6), y - peak)
                c.curve_to(px + wid / n * .1, y - peak * .6, px + wid / n * .3, y - peak * .2, px + wid / n * .5, y - hgt * .1)
            c.curve_to(x + wid * .6, y + 26 * s, x - wid * .6, y + 26 * s, x - wid, y); c.close_path(); c.fill()
        cv.put(mask(crown), lines_print(PAL['foam'], '#41606f', seed=seed, pitch=5, ang=88, width=.3, ink=.35, local=True), edge='cut', seed=seed + 1, shadow=(5, 7, 5, .3))
    r = rng(seed + 9)
    def drops(c):
        for i in range(16):
            a = D(r.uniform(-160, -20)); v = r.uniform(250, 520) * s; tt = min(u, 2.) * .9
            px, py = x + math.cos(a) * v * tt, y + math.sin(a) * v * tt + 700 * s * tt * tt
            if py < y + 10: c.save(); c.translate(px, py); c.scale(1, 1.3); c.arc(0, 0, r.uniform(4, 9) * s, 0, 6.3); c.restore(); c.fill()
    cv.put(mask(drops), paper('#eee7d6', seed + 2), edge='cut', seed=seed + 2, shadow=(3, 5, 3, .3))
    if u > .25:
        k = (u - .25) / 1.75
        cv.put(mask(lambda c: [(c.save(), c.translate(x, y + 6), c.scale(1, .22), c.set_line_width(7 / .22 * .3), c.arc(0, 0, s * (160 + 380 * k) * f, 0, 6.3), c.restore(), c.stroke()) for f in (1., .7)]),
               paper(PAL['foam'], seed + 3), edge='cut', seed=seed + 3, shadow=(2, 3, 2, .3), opacity=max(0., 1 - k * .8))


def label(cv, x, y, text, hh=66, seed=61, ang=-2.2, tear=0., move=False, n=99):
    """A torn parchment label with cut black letters.  tear (0..1): the label torn in two, halves drifting apart."""
    G = {'Ι': [[(.08, 0), (.08, 1)]], 'Κ': [[(0, 0), (0, 1)], [(.62, 0), (.05, .55)], [(.25, .38), (.66, 1)]], 'Α': [[(0, 1), (.36, 0), (.72, 1)], [(.17, .62), (.55, .62)]],
         'Ρ': [[(0, 1), (0, 0), (.4, 0), (.58, .12), (.58, .36), (.4, .48), (0, .48)]], 'Ο': 'ring', 'Σ': [[(.6, 0), (0, 0), (.36, .5), (0, 1), (.62, 1)]]}
    WD = {'Ι': .16, 'Ο': .74, 'Ρ': .6}
    total = sum(WD.get(ch, .72) * hh + 20 for ch in text) + 40; lw, lh = total + 20, hh * 1.8
    lx, ly = x - lw / 2, y - lh / 2
    halves = [(lx - 8, lw / 2 + 8, -1), (x, lw / 2 + 8, 1)] if tear > 0 else [(lx, lw, 0)]
    for hx, hw, side in halves:
        off = side * 160 * tear; dy = abs(side) * (60 * tear * tear) * (1 if side > 0 else .6); rot_ = D(side * 7 * tear)
        def frame(c, off=off, dy=dy, rot_=rot_):
            c.translate(x + off, y + dy); c.rotate(D(ang) + rot_); c.translate(-x, -y)
        def lab(c, hx=hx, hw=hw):
            frame(c); poly(c, rect_pts(hx, ly, hw, lh)); c.fill()
        cv.put(mask(lab), paper(PAL['parch'], seed), edge='torn', seed=seed + (side + 1) * 7, amp=7, rim=3.5, shadow=(4, 6, 5, .33), move=move)
        r = rng(seed + 1); px = lx + 30
        for ci, ch in enumerate(text):
            if ci >= n: break
            g = G[ch]; a = D(r.uniform(-5, 5)); wd = WD.get(ch, .72)
            if side == 0 or (side < 0) == (px + wd * hh / 2 < x):
                def draw(c, g=g, px=px, a=a, wd=wd):
                    frame(c); c.translate(px + wd * hh / 2, y); c.rotate(a); c.translate(-wd * hh / 2, -hh / 2); c.set_line_width(hh * .17); c.set_line_cap(0); c.set_line_join(0)
                    if g == 'ring': c.save(); c.translate(hh * .37, hh * .5); c.scale(1, 1.32); c.arc(0, 0, hh * .3, 0, 2 * math.pi); c.restore(); c.stroke(); return
                    for st in g: poly(c, [(qx * hh, qy * hh) for qx, qy in st], close=False); c.stroke()
                cv.put(mask(draw), slip(70 + int(px)), edge='cut', seed=int(px), shadow=(2, 3, 2, .4), wobble=.6, move=move)
            px += wd * hh + 20


def meander_band(cv, y, h=46, x0=-20, x1=W + 20, ang=-.35, seed=51):
    a = D(ang)
    def key(c):
        c.save(); c.translate((x0 + x1) / 2, y + h / 2); c.rotate(a); c.translate(-(x0 + x1) / 2, -(y + h / 2)); c.set_line_width(4.5)
        c.move_to(x0, y + 5); c.line_to(x1, y + 5); c.stroke(); c.move_to(x0, y + h - 5); c.line_to(x1, y + h - 5); c.stroke()
        for u in range(int(x0) - 40, int(x1) + 40, 40):
            b, t = y + h - 10, y + 10
            poly(c, [(u, b), (u, t), (u + 30, t), (u + 30, b - 6), (u + 10, b - 6), (u + 10, t + 10), (u + 20, t + 10)], close=False); c.stroke()
            c.move_to(u, b); c.line_to(u + 40, b); c.stroke()
        c.restore()
    cv.put(mask(lambda c: (poly(c, rect_pts(x0, y, x1 - x0, h, a)), c.fill())), paper(PAL['clay'], seed, mottle=.06), edge='cut', seed=seed, wobble=1.5,
           shadow=(3, -4, 4, .35), marks=[(mask(key), '#1d1612', .93)])
