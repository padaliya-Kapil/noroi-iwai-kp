"""Collage kit: every piece is a sheet of paper, cut with scissors or torn by hand, laid on the page and lifted a little off it.

A piece is a coverage mask (drawn with cairo) plus a texture function tex(h, w, y0, x0) -> (h, w, 3) float RGB.
Canvas.put() tears or cuts the mask edge, lays a shadow under it, shows the white paper core along a torn edge,
and composites the texture.  Everything works on the piece's bounding box, so a page of a few hundred pieces stays fast.
"""
import math
import numpy as np, cv2, cairo

W, H = 1920, 1080
f32 = np.float32


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], f32) / 255.


def clip(x):
    return np.clip(x, 0., 1.)


def smooth(a, b, x):
    t = clip((x - a) / (b - a)); return t * t * (3 - 2 * t)


def rng(seed):
    return np.random.default_rng(int(seed) & 0xFFFFFFFF)


def noise(h, w, cell, seed, octaves=3):
    """Band-limited noise, zero mean and about unit deviation; `cell` is the size of the largest feature in pixels."""
    r = rng(seed); out = np.zeros((h, w), f32); a = 1.; var = 0.
    for _ in range(octaves):
        c = max(cell, 1.)
        gh, gw = int(math.ceil(h / c)) + 2, int(math.ceil(w / c)) + 2
        g = r.standard_normal((gh, gw)).astype(f32)
        out += a * cv2.resize(g, (int(gw * c), int(gh * c)), interpolation=cv2.INTER_CUBIC)[:h, :w]
        var += a * a; a *= .5; cell /= 2.
    return out / (.85 * math.sqrt(var))                                       # fixed scale, so a small crop is not stretched


def grid(h, w, y0=0, x0=0):
    return np.meshgrid(np.arange(w, dtype=f32) + x0, np.arange(h, dtype=f32) + y0)


def sdist(m):
    """Signed distance in pixels to the edge of a mask: positive inside."""
    b = (m > .5).astype(np.uint8)
    return cv2.distanceTransform(b, cv2.DIST_L2, 5) - cv2.distanceTransform(1 - b, cv2.DIST_L2, 5)


# ----------------------------------------------------------------------------------------------- masks
def mask(draw, xf=None, h=H, w=W):
    """Run draw(ctx) on an empty alpha surface; xf = (x, y, angle_rad, scale) places a local frame first."""
    s = cairo.ImageSurface(cairo.FORMAT_A8, w, h); c = cairo.Context(s)
    c.set_source_rgba(0, 0, 0, 1); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND)
    if xf:
        c.translate(xf[0], xf[1]); c.rotate(xf[2]); c.scale(xf[3], xf[3])
    draw(c); s.flush()
    return np.ndarray((h, s.get_stride()), np.uint8, s.get_data())[:, :w].astype(f32) / 255.


def poly(c, pts, close=True):
    c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    if close: c.close_path()


def rect_pts(x, y, w, h, ang=0., cx=None, cy=None):
    cx = x + w / 2 if cx is None else cx; cy = y + h / 2 if cy is None else cy; ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + (px - cx) * ca - (py - cy) * sa, cy + (px - cx) * sa + (py - cy) * ca) for px, py in ((x, y), (x + w, y), (x + w, y + h), (x, y + h))]


# ----------------------------------------------------------------------------------------------- papers
def fibers(h, w, r, density=1 / 650.):
    L = np.zeros((h, w), f32); n = int(h * w * density)
    if n == 0: return L
    xs, ys = r.uniform(0, w, n), r.uniform(0, h, n); an = r.uniform(0, math.pi, n); ln = r.uniform(3, 16, n); v = r.choice([-1., 1.], n) * r.uniform(.3, 1, n)
    for x, y, a, l, vv in zip(xs, ys, an, ln, v):
        dx, dy = math.cos(a) * l / 2, math.sin(a) * l / 2
        cv2.line(L, (int((x - dx) * 16), int((y - dy) * 16)), (int((x + dx) * 16), int((y + dy) * 16)), float(vv), 1, cv2.LINE_AA, 4)
    return cv2.GaussianBlur(L, (0, 0), .55)


def paper(col, seed=0, mottle=.045, fiber=.07, grain=.03, cell=80):
    col = rgb(col) if isinstance(col, str) else np.asarray(col, f32)
    def f(h, w, y0, x0):
        r = rng(seed * 7919 + 17)
        t = col[None, None, :] * (1 + mottle * noise(h, w, cell, seed + 1)[..., None])
        t = t * (1 + fiber * fibers(h, w, r)[..., None])
        g = cv2.GaussianBlur(r.standard_normal((h, w)).astype(f32), (0, 0), .7)
        return t * (1 + grain * (g / (g.std() + 1e-6))[..., None])
    return f


def halftone(paper_col, ink_col, tone, cell=8., ang=15., seed=0, ink=.9):
    """Printed paper: a dot screen over a sheet.  tone is a coverage (0..1) or a function (h, w, y0, x0) -> coverage."""
    base = paper(paper_col, seed, mottle=.03); ink_col = rgb(ink_col) if isinstance(ink_col, str) else ink_col
    def f(h, w, y0, x0):
        b = base(h, w, y0, x0); X, Y = grid(h, w, y0, x0); a = math.radians(ang)
        u = X * math.cos(a) + Y * math.sin(a); v = -X * math.sin(a) + Y * math.cos(a)
        d = np.hypot((u / cell) % 1 - .5, (v / cell) % 1 - .5) * cell
        t = tone(h, w, y0, x0) if callable(tone) else np.full((h, w), tone, f32)
        k = clip(cell * np.sqrt(clip(t) / math.pi) - d + .5 + .35 * noise(h, w, 3, seed + 5, 2))[..., None] * ink
        return b * (1 - k) + ink_col * k
    return f


def lines_print(paper_col, ink_col, seed=0, pitch=9, ang=0., width=.38, ink=.55, cell=120):
    """Engraved hatching: parallel lines whose weight follows a slow noise."""
    base = paper(paper_col, seed, mottle=.03); ink_col = rgb(ink_col)
    def f(h, w, y0, x0):
        b = base(h, w, y0, x0); X, Y = grid(h, w, y0, x0); a = math.radians(ang)
        v = (-X * math.sin(a) + Y * math.cos(a)) / pitch
        wt = width * (1 + .45 * noise(h, w, cell, seed + 3, 2))
        k = clip((wt * pitch / 2 - np.abs((v % 1) - .5) * pitch) + .5)[..., None] * ink
        return b * (1 - k) + ink_col * k
    return f


def gold(seed=0, sheet=128, center=None, radius=None):
    """Gold leaf: square leaves laid in staggered rows, overlapping seams, crinkled metal, cracks down to the red bole."""
    dark, mid, hi, bole = rgb('#7a5a26'), rgb('#bb9447'), rgb('#ead28e'), rgb('#7f3a22')
    def f(h, w, y0, x0):
        X, Y = grid(h, w, y0, x0)
        n = cv2.GaussianBlur(noise(h, w, 60, seed, 4), (0, 0), 2.)
        gx = cv2.Sobel(n, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(n, cv2.CV_32F, 0, 1, ksize=3)
        s = .6 + .17 * np.tanh(-(gx * .62 + gy * .78) * 2.2)
        iy = np.floor(Y / sheet); off = (iy % 2) * sheet * .43 + (iy % 3) * 11; ix = np.floor((X + off) / sheet)
        hsh = ((ix * 73856093.).astype(np.int64) ^ (iy * 19349663.).astype(np.int64)) % 1009 / 1009.
        fx = (X + off) / sheet - ix; fy = Y / sheet - iy
        e = np.minimum(np.minimum(fx, 1 - fx), np.minimum(fy, 1 - fy)) * sheet + noise(h, w, 7, seed + 2, 2) * 1.1
        seam = np.exp(-(e / 1.6) ** 2)
        s = clip(s * .85 + (hsh - .5) * .16 + .02 + .14 * seam - .06 * np.exp(-((e - 3.) / 1.3) ** 2))
        if center is not None:
            r = np.hypot(X - center[0], Y - center[1]) / radius; s = clip(s + .16 * (1 - r) - .1 * smooth(.75, 1., r))
        s3 = s[..., None]
        col = np.where(s3 < .5, dark + (mid - dark) * s3 * 2, mid + (hi - mid) * (s3 * 2 - 1))
        cr = noise(h, w, 46, seed + 4, 3); crack = np.exp(-(cr / .03) ** 2) * smooth(1.1, 1.6, noise(h, w, 140, seed + 6, 2))
        return col * (1 - crack[..., None] * .85) + bole * crack[..., None] * .85
    return f


def slip(seed=0, col='#1d1714'):
    """Black-figure: a glossy black paper with a faint warm sheen."""
    base = rgb(col)
    def f(h, w, y0, x0):
        n = noise(h, w, 60, seed, 3); n2 = noise(h, w, 9, seed + 1, 2)
        t = base * (1 + .2 * n[..., None]) + .035 * clip(n2 - .8)[..., None]
        return t + .012 * fibers(h, w, rng(seed))[..., None]
    return f


def brass(cx, cy, r):
    lo, mid, hi = rgb('#6d4c1c'), rgb('#b88a3a'), rgb('#fff0b8')
    def f(h, w, y0, x0):
        X, Y = grid(h, w, y0, x0); d = np.hypot(X - cx + r * .35, Y - cy + r * .4) / r
        s = clip(1 - d)[..., None]; e = clip(np.hypot(X - cx, Y - cy) / r)[..., None]
        return (mid * (1 - e * .5) + lo * e * .5) * (1 - s ** 3) + hi * s ** 3
    return f


# ----------------------------------------------------------------------------------------------- the page
class Canvas:
    def __init__(self, base):
        self.im = base.astype(f32)

    def put(self, m, tex, edge='torn', seed=0, amp=6., rim=3.5, rim_col='#f6f0e2', shadow=(4, 6, 4., .32), opacity=1.,
            marks=(), singe=0., wobble=1.2):
        """Lay one piece.  edge: 'torn' (ragged, white core showing) | 'cut' (scissors: clean, faintly wavering) | 'none'."""
        x, y, w, h = cv2.boundingRect((m > .01).astype(np.uint8))
        if w == 0: return
        dx, dy, sb, ss = shadow
        pad = int(amp * 3 + rim + sb * 3 + max(abs(dx), abs(dy)) + 6)
        x0, y0, x1, y1 = max(x - pad, 0), max(y - pad, 0), min(x + w + pad, W), min(y + h + pad, H)
        mc = m[y0:y1, x0:x1]; hh, ww = mc.shape
        if edge == 'none':
            body = outer = mc
        else:
            sd0 = sdist(mc); sd = sd0 - .5 * np.sign(sd0)
            part = (mc > .001) & (mc < .999); sd[part] = mc[part] - .5         # cairo's coverage gives the sub-pixel edge
            if edge == 'torn':
                n1 = noise(hh, ww, 36, seed, 3) * amp + noise(hh, ww, 3, seed + 7, 2) * amp * .22
                n2 = noise(hh, ww, 28, seed + 3, 3) * amp * .55 + noise(hh, ww, 2., seed + 9, 2) * amp * .12
                body = clip(sd + n1 - amp * .3 + .5); outer = np.maximum(clip(sd + n2 + rim - amp * .3 + .5), body)
            else:
                body = clip(sd + noise(hh, ww, 110, seed, 2) * wobble + .5); outer = body
        if ss > 0:
            sh = cv2.GaussianBlur(outer, (0, 0), sb) if sb > 0 else outer
            sh = cv2.warpAffine(sh, np.float32([[1, 0, dx], [0, 1, dy]]), (ww, hh))
            self.im[y0:y1, x0:x1] *= (1 - ss * opacity * sh)[..., None]
        t = tex(hh, ww, y0, x0)
        if edge != 'none':
            sdb = sdist(body)
            t = t * (1 - .07 * np.exp(-clip(sdb / 2.5) * 3))[..., None]
            if singe:
                a = (singe * np.exp(-np.maximum(sdb, 0) / 7.) * (.7 + .3 * noise(hh, ww, 10, seed + 11)))[..., None]
                t = t * (1 - clip(a)) + rgb('#5a2a10') * clip(a)
        for mk, col, al in marks:
            k = (mk[y0:y1, x0:x1] * al)[..., None]; c = rgb(col) if isinstance(col, str) else col
            t = t * (1 - k) + c * k
        im = self.im[y0:y1, x0:x1]
        if edge == 'torn' and rim > 0:
            ra = (cv2.GaussianBlur(clip(outer - body), (0, 0), .6) * clip(.9 + .1 * noise(hh, ww, 3, seed + 13, 1)) * opacity)[..., None]
            core = rgb(rim_col) * .7 + cv2.blur(t, (9, 9)) * .3                  # a torn sheet shows its pale core, tinted by its own colour
            im = im * (1 - ra) + core * ra
        ba = (body * opacity)[..., None]
        self.im[y0:y1, x0:x1] = im * (1 - ba) + t * ba

    def finish(self, seed=0, vig=.13, grain=.018, warm=(1.02, 1., .965), desat=0.):
        X, Y = grid(H, W)
        r = np.hypot((X - W * .55) / (W * .62), (Y - H * .45) / (H * .7))
        im = self.im * (1 - vig * smooth(.35, 1.25, r))[..., None] * np.array(warm, f32)
        if desat: im = im * (1 - desat) + (im @ np.array([.3, .59, .11], f32))[..., None] * desat
        g = cv2.GaussianBlur(rng(seed).standard_normal((H, W)).astype(f32), (0, 0), .6)
        im = im * (1 + grain * g / g.std())[..., None]
        return (clip(im) ** (1 / 1.0) * 255 + .5).astype(np.uint8)
