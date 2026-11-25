"""Black-figure paper puppets: a flyer cut from black paper as on an Attic vase, limbs as separate pieces joined
with brass fasteners, details incised through to the clay colour, and wings of single cut-paper feathers set in wax.

Local frame of a flyer: +x runs from the feet to the head, +y is the belly side.  The pelvis is the origin.
"""
import math
import numpy as np
from collage import mask, poly, paper, halftone, lines_print, slip, brass, rgb, rng, smooth, clip

CLAY = '#b4643c'                                                                # the fired clay that incisions show
SEPIA = '#4a3a2b'


def xform(xf, p):
    x, y, a, k = xf; ca, sa = math.cos(a), math.sin(a)
    return (x + k * (p[0] * ca - p[1] * sa), y + k * (p[0] * sa + p[1] * ca))


def limb_path(c, a, b, wa, wb):
    dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1.; nx, ny = -dy / l, dx / l
    poly(c, [(a[0] + nx * wa / 2, a[1] + ny * wa / 2), (b[0] + nx * wb / 2, b[1] + ny * wb / 2), (b[0] - nx * wb / 2, b[1] - ny * wb / 2), (a[0] - nx * wa / 2, a[1] - ny * wa / 2)]); c.fill()
    c.arc(a[0], a[1], wa / 2, 0, 2 * math.pi); c.fill(); c.arc(b[0], b[1], wb / 2, 0, 2 * math.pi); c.fill()


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


# ----------------------------------------------------------------------------------------------- feathers
def feather_pts(base, ang, L, wd, curve=.06, notches=(), quill=.07):
    """Outline of one feather as cut from paper: a short bare quill, a narrow leading vane, a wide trailing vane."""
    ca, sa = math.cos(ang), math.sin(ang); nx, ny = -sa, ca
    def P(s, off):
        bend = curve * L * s * s
        return (base[0] + ca * s * L + nx * (off + bend), base[1] + sa * s * L + ny * (off + bend))
    S = np.linspace(0, 1, 26); shape = lambda s: smooth(0., .22, s) * math.sqrt(max(0., 1 - s ** 3.2))
    left, right = [], []
    for s in S:
        kl = kr = 1.
        for ns, side in notches:
            if abs(s - ns) < .03: kl, kr = (.35, kr) if side < 0 else (kl, .35)
        left.append(P(s, -wd * .36 * shape(s) * kl - 1.2)); right.append(P(s, wd * .64 * shape(s) * kr + 1.2))
    q = [P(-quill, -1.6), P(-quill, 1.6)]
    return [q[0]] + left + right[::-1] + [q[1]], [P(s, 0) for s in np.linspace(-quill, .86, 12)]


FEATHER_PAPERS = [('#ece3cf', 'plain'), ('#e6dcc5', 'plain'), ('#ddd0b4', 'plain'), ('#d6d2c6', 'plain'), ('#e4d9bf', 'lines'),
                  ('#e9dfc8', 'plain'), ('#d9c7a2', 'plain'), ('#e8dec9', 'text'), ('#e2d5b8', 'lines')]          # ivory, bone, parchment, book pages, engravings


def text_print(col, seed):
    """Newsprint: grey bars standing for lines of type, set in a column (no letters, only their colour)."""
    base = paper(col, seed, mottle=.03); ink = rgb(SEPIA)
    def f(h, w, y0, x0):
        b = base(h, w, y0, x0); r = rng(seed); X = np.arange(w)[None, :] + x0; Y = np.arange(h)[:, None] + y0
        row = (Y // 9); on = ((Y % 9) >= 3) & ((Y % 9) <= 6)
        wl = (np.sin(row * 12.9898 + seed) * 43758.5453) % 1
        word = ((X + (row * 37) % 23) // 5 % 7 != 0) & (((X - x0) % 230) < 200 * (.55 + .45 * wl))
        k = (on & word).astype(np.float32)[..., None] * .55
        return b * (1 - k) + ink * k
    return f


def feather_tex(kind, col, seed):
    if kind == 'lines': return lines_print(col, SEPIA, seed=seed, pitch=4, ang=60 + seed % 40, width=.26, ink=.42)
    if kind == 'text': return text_print(col, seed)
    return paper(col, seed, mottle=.04, fiber=.09)


def wing_feathers(lead, xf, seed, rows=((1., 17, 0), (.56, 15, 1), (.3, 12, 2)), a0=(-1., .12), a1=(-.78, -.62), Lmin=95, Lmax=300,
                  skip=(), loose=(), dim=0.):
    """Feathers laid along a leading edge (shoulder, elbow, wrist, tip).  Returns [(mask, tex, quill mask, seed, singe)] bottom first."""
    seg = [math.dist(lead[i], lead[i + 1]) for i in range(len(lead) - 1)]; tot = sum(seg)
    def at(t):
        d = t * tot
        for i, s in enumerate(seg):
            if d <= s or i == len(seg) - 1: return lerp(lead[i], lead[i + 1], min(d / s, 1.))
            d -= s
    g0, g1 = math.atan2(a0[1], a0[0]), math.atan2(a1[1], a1[0])
    if g1 - g0 > math.pi: g1 -= 2 * math.pi
    if g0 - g1 > math.pi: g1 += 2 * math.pi
    r = rng(seed); out = []
    for k, n, row in rows:
        for i in range(n)[::-1]:
            t = (i + .5) / n if row else i / (n - 1) * .97 + .02
            if row == 0 and i in skip: continue
            L = (Lmin + (Lmax - Lmin) * t ** .9) * (1 - .38 * smooth(.86, 1., t)) * k
            ang = g0 + (g1 - g0) * t ** 1.15 + r.normal(0, .035)
            b = at(t); b = (b[0] - math.cos(ang) * 4 * (row == 0), b[1] - math.sin(ang) * 4 * (row == 0))
            if row == 0 and i in loose: ang += .28; b = (b[0] + math.cos(ang) * 14 - 6, b[1] + math.sin(ang) * 14 + 10)
            wd = min(max(.2 * L, 15), 40) * (1.15 if row else 1.)
            notch = [(r.uniform(.4, .8), r.choice([-1, 1]))] if r.random() < .5 and row == 0 else []
            pts, sp = feather_pts(b, ang, L, wd, curve=r.uniform(.02, .07), notches=notch)
            col, kind = FEATHER_PAPERS[r.integers(len(FEATHER_PAPERS))]
            if dim: col = '#' + ''.join('%02x' % int(v * 255) for v in clip(rgb(col) * (1 - dim) + rgb('#7d776c') * dim))
            s = int(r.integers(1 << 30))
            m = mask(lambda c, pts=pts: (poly(c, pts), c.fill()), xf)
            q = mask(lambda c, sp=sp, L=L: (c.set_line_width(max(1.1, L * .008)), poly(c, sp, close=False), c.stroke()), xf)
            out.append((m, feather_tex(kind, col, s), q, s, t * (row == 0)))
    return out


def lay_feathers(cv, feathers, singe_tip=0., shadow=(5, 7, 4., .3)):
    for m, tex, q, s, t in feathers:
        cv.put(m, tex, edge='cut', seed=s, shadow=shadow, marks=[(q, SEPIA, .5)], singe=singe_tip * smooth(.55, 1., t), wobble=.8)


# ----------------------------------------------------------------------------------------------- the flyer
class Flyer:
    def __init__(self, xf, seed=0, beard=False, arm=((132, -18), (150, -104), (226, -150)), arm_far=((124, -22), (132, -108), (200, -162)),
                 leg=((4, 8), (-96, 20), (-186, 4), (-226, 13)), leg_far=((4, 2), (-84, 26), (-140, 96), (-172, 113))):
        self.xf, self.seed, self.beard = xf, seed, beard
        self.arm, self.arm_far, self.leg, self.leg_far = arm, arm_far, leg, leg_far

    def M(self, draw):
        return mask(draw, self.xf)

    def lead(self, far=False):
        """Leading edge of a wing in the local frame: shoulder, elbow, wrist, fingertip."""
        s, e, w = self.arm_far if far else self.arm
        return [s, e, w, (w[0] + (w[0] - e[0]) * .38, w[1] + (w[1] - e[1]) * .38)]

    # each body part: (mask, incision mask)
    def arm_parts(self, far):
        s, e, w = self.arm_far if far else self.arm
        d = math.atan2(w[1] - e[1], w[0] - e[0]); hand = (w[0] + math.cos(d) * 22, w[1] + math.sin(d) * 22)
        def fore(c):
            limb_path(c, e, w, 22, 14); c.save(); c.translate(*hand); c.rotate(d); c.scale(1, .55); c.arc(0, 0, 17, 0, 2 * math.pi); c.restore(); c.fill()
            for k, (l, off) in enumerate(((26, -3), (22, 3))): limb_path(c, (hand[0] + math.cos(d) * 10, hand[1] + math.sin(d) * 10 + off), (hand[0] + math.cos(d) * l + math.cos(d + 1.57) * off, hand[1] + math.sin(d) * l + math.sin(d + 1.57) * off), 6, 5)
            limb_path(c, (w[0] + math.cos(d) * 8, w[1] + math.sin(d) * 8), (w[0] + math.cos(d - .9) * 20, w[1] + math.sin(d - .9) * 20), 7, 5)
        up = self.M(lambda c: limb_path(c, s, e, 32, 22)); fo = self.M(fore)
        return [(up, None), (fo, self.M(lambda c: (c.set_line_width(1.6), c.arc(*lerp(e, w, .25), 5, 0, 3.2), c.stroke())))]

    def leg_parts(self, far):
        h, k, a, t = self.leg_far if far else self.leg
        def thigh(c):
            limb_path(c, h, k, 48, 24); m = lerp(h, k, .35); c.save(); c.translate(*m); c.rotate(math.atan2(k[1] - h[1], k[0] - h[0])); c.scale(1, .52); c.arc(0, 0, 42, 0, 2 * math.pi); c.restore(); c.fill()
        def shin(c):
            limb_path(c, k, a, 24, 12); m = lerp(k, a, .3); c.save(); c.translate(*m); c.rotate(math.atan2(a[1] - k[1], a[0] - k[0])); c.scale(1, .5); c.arc(0, 0, 32, 0, 2 * math.pi); c.restore(); c.fill()
            limb_path(c, a, t, 13, 6)
        inc = lambda c: (c.set_line_width(1.5), c.arc(*k, 7, 1., 2.6), c.stroke(), c.arc(*lerp(h, k, .55), 13, 3.6, 4.6), c.stroke())
        return [(self.M(thigh), None), (self.M(shin), self.M(inc))]

    def torso(self):
        def body(c):
            c.scale(1, 1.35)
            c.move_to(-22, 2); c.curve_to(-26, -18, -6, -26, 30, -27); c.curve_to(80, -29, 120, -30, 150, -20); c.line_to(168, -10)
            c.line_to(170, 8); c.curve_to(150, 30, 120, 34, 96, 24); c.curve_to(70, 18, 40, 30, 8, 28); c.curve_to(-10, 26, -20, 18, -22, 2); c.fill()
            limb_path(c, (150, -6), (180, -4), 26, 22)
        def inc(c):
            c.scale(1, 1.35); c.set_line_width(1.4); c.move_to(150, 22); c.curve_to(132, 10, 118, 14, 110, 26); c.stroke()
            for x in (92, 76, 60): c.move_to(x, 24); c.curve_to(x - 4, 18, x - 2, 14, x - 8, 12); c.stroke()
            c.move_to(10, 26); c.curve_to(20, 14, 34, 8, 48, 12); c.stroke()
        return self.M(body), self.M(inc)

    def head(self):
        def h(c):
            c.arc(190, -14, 27, 0, 2 * math.pi); c.fill()
            c.move_to(200, -40); c.curve_to(214, -38, 220, -28, 222, -18); c.line_to(236, -4); c.line_to(226, -1)
            c.curve_to(229, 3, 226, 6, 224, 7); c.curve_to(228, 10, 226, 14, 222, 15); c.curve_to(224, 22, 216, 24, 208, 22)
            c.line_to(184, 14); c.line_to(186, -30); c.close_path(); c.fill()
            for (x, y, r) in ((166, -30, 13), (160, -14, 12), (172, -42, 11), (186, -44, 10), (156, 0, 10)): c.arc(x, y, r, 0, 2 * math.pi); c.fill()
            if self.beard:
                c.move_to(222, 6); c.curve_to(228, 22, 222, 38, 206, 44); c.curve_to(196, 34, 190, 24, 188, 12); c.close_path(); c.fill()
        def inc(c):
            c.set_line_width(1.6); c.save(); c.translate(211, -14); c.scale(1, .5); c.arc(0, 0, 6.5, 0, 2 * math.pi); c.restore(); c.stroke()
            c.arc(212, -14, 1.8, 0, 2 * math.pi); c.fill()
            c.move_to(200, -27); c.curve_to(207, -30, 214, -28, 218, -24); c.stroke()
            c.move_to(198, -38); c.curve_to(190, -36, 186, -26, 188, -10); c.curve_to(189, 0, 186, 8, 182, 12); c.stroke()
            for (x, y, r) in ((166, -30, 8), (160, -14, 7), (172, -42, 6), (186, -44, 5), (156, 0, 6)): c.arc(x, y, r, 0, 5.2); c.stroke()
            if self.beard:
                for i in range(4): c.move_to(218 - i * 6, 14 + i * 2); c.curve_to(216 - i * 6, 26, 212 - i * 5, 34, 206 - i * 4, 40); c.stroke()
        return self.M(h), self.M(inc)

    def joints(self):
        k = self.xf[3]
        return [xform(self.xf, p) for p in (self.arm[0], self.arm[1], self.leg[0], self.leg[1])], 6.5 * k / 1.15

    def lay_body(self, cv, part, shadow):
        s = self.seed
        if part == 'far':
            for i, (m, inc) in enumerate(self.leg_parts(True) + self.arm_parts(True)):
                cv.put(m, slip(s + i, '#2a221d'), edge='cut', seed=s + 40 + i, shadow=shadow, marks=[(inc, CLAY, .9)] if inc is not None else [])
        else:
            parts = self.leg_parts(False) + [self.torso(), self.head()]
            for i, (m, inc) in enumerate(parts):
                cv.put(m, slip(s + 10 + i), edge='cut', seed=s + 60 + i, shadow=shadow, marks=[(inc, CLAY, .92)] if inc is not None else [])

    def lay_arm(self, cv, shadow):
        for i, (m, inc) in enumerate(self.arm_parts(False)):
            cv.put(m, slip(self.seed + 30 + i), edge='cut', seed=self.seed + 80 + i, shadow=shadow, marks=[(inc, CLAY, .92)] if inc is not None else [])

    def lay_spar(self, cv, shadow, far=False):
        """A split reed along the leading edge, past the hand to the wing tip: the frame the feathers are bound to."""
        L = self.lead(far); tip = (L[3][0] + (L[3][0] - L[2][0]) * .9, L[3][1] + (L[3][1] - L[2][1]) * .9)
        pts = [(L[0][0] - 10, L[0][1] - 14), (L[1][0] - 12, L[1][1] - 16), (L[2][0] - 2, L[2][1] - 19), (tip[0], tip[1] - 14)]
        m = self.M(lambda c: (c.set_line_width(11), poly(c, pts, close=False), c.stroke()))
        cv.put(m, lines_print('#b39a6c' if not far else '#8a7656', '#3a2a1c', seed=self.seed + 5, pitch=3, ang=math.degrees(self.xf[2]) - 75, width=.3, ink=.35),
               edge='cut', seed=self.seed + 5, shadow=shadow, wobble=.5)

    def lay_harness(self, cv, shadow):
        s = self.arm[0]
        m = self.M(lambda c: (c.set_line_width(10), c.move_to(s[0] + 6, s[1] - 6), c.curve_to(128, 10, 112, 30, 100, 40), c.stroke()))
        cv.put(m, paper('#7a5636', self.seed + 6, mottle=.08), edge='cut', seed=self.seed + 6, shadow=(2, 3, 2, .4), wobble=.4,
               marks=[(self.M(lambda c: (c.set_line_width(1.), c.set_dash([3, 3]), c.move_to(s[0] + 6, s[1] - 6), c.curve_to(128, 10, 112, 30, 100, 40), c.stroke())), '#d8c49a', .7)])

    def lay_straps(self, cv, far=False):
        s, e, w = self.arm_far if far else self.arm
        def band(c, a, b, t, wd):
            p = lerp(a, b, t); dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy); nx, ny = -dy / l, dx / l; h = wd / 2 + 5
            c.set_line_width(7); c.move_to(p[0] + nx * h, p[1] + ny * h); c.line_to(p[0] - nx * h, p[1] - ny * h); c.stroke()
        m = self.M(lambda c: (band(c, s, e, .55, 26), band(c, e, w, .5, 17)))
        cv.put(m, paper('#7a5636' if not far else '#5e4630', self.seed + 7, mottle=.08), edge='cut', seed=self.seed + 7, shadow=(2, 3, 2, .45), wobble=.4)

    def lay_brads(self, cv):
        pts, r = self.joints()
        for x, y in pts:
            cv.put(mask(lambda c, x=x, y=y: (c.arc(x, y, r, 0, 2 * math.pi), c.fill())), brass(x, y, r), edge='cut', seed=int(x), shadow=(1.5, 2.5, 1.5, .45), wobble=.2)


# ----------------------------------------------------------------------------------------------- wax
def wax(cv, pts, seed, drips=True, scale=1.):
    """Beeswax pressed over the feather roots: translucent amber blobs, some running in drips (gravity is +y on the page)."""
    r = rng(seed); blobs = []; runs = []
    for p in pts:
        rr = r.uniform(5, 10) * scale; blobs.append((p[0] + r.normal(0, 3), p[1] + r.normal(0, 3), rr))
        if drips and r.random() < .55: runs.append((p[0] + r.normal(0, 4), p[1] + rr * .4, r.uniform(18, 75) * scale, r.uniform(4.5, 7.5) * scale))
    def draw(c):
        for x, y, rr in blobs:
            c.save(); c.translate(x, y); c.scale(1, .8); c.arc(0, 0, rr, 0, 2 * math.pi); c.restore(); c.fill()
        for x, y, l, w in runs:
            limb_path(c, (x, y), (x + w * .15, y + l), w, w * .55); c.arc(x + w * .15, y + l, w * .7, 0, 2 * math.pi); c.fill()
    hl = mask(lambda c: [(c.save(), c.translate(x - rr * .35, y - rr * .35), c.scale(1, .6), c.arc(0, 0, rr * .3, 0, 2 * math.pi), c.restore(), c.fill()) for x, y, rr in blobs]
              + [(c.arc(x - w * .2, y + l - w * .2, w * .22, 0, 2 * math.pi), c.fill()) for x, y, l, w in runs])
    cv.put(mask(draw), paper('#b8873e', seed, mottle=.12, fiber=0., grain=.02, cell=18), edge='cut', seed=seed, opacity=.8,
           shadow=(2, 3, 2., .35), marks=[(hl, '#f3e6c4', .7)], wobble=.6)
