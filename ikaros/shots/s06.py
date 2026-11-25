"""S06  Close on the bench: a wing is built on its reed, feather by feather, every root pressed into wax by Daidalos's hand."""
from functools import lru_cache
from shotkit import *

def fit():
    """Lay the wing flat across the sheet: rotate its leading edge level, then scale and centre it on the paper."""
    F = Flyer((0, 0, 0, 1.)); L = F.lead(); a = -math.atan2(L[3][1] - L[0][1], L[3][0] - L[0][0])
    pts = [p for m, *_ in [] ] or []
    xs, ys = [], []
    for i in range(17):
        tt = i / 16; ln = 95 + 205 * tt
        g = math.atan2(.12, -1.) + (math.atan2(-.62, -.78) + 2 * math.pi - math.atan2(.12, -1.)) * tt
        b = lerp(L[0], L[3], tt); e = (b[0] + math.cos(g) * ln, b[1] + math.sin(g) * ln)
        for p in (b, e):
            q = xform((0, 0, a, 1.), p); xs.append(q[0]); ys.append(q[1])
    k = min(1300 / (max(xs) - min(xs)), 780 / (max(ys) - min(ys)))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    return (990 - cx * k, 560 - cy * k, a, k)


XF = fit()


def build(cv, h, w):
    cv.put(mask(lambda c: (c.rectangle(-20, -20, w + 40, h + 40), c.fill())), lines_print('#8a6845', '#3a2716', seed=95, pitch=9, ang=1, width=.42, ink=.42, cell=80), edge='none', shadow=(0, 0, 0, 0))
    cv.put(mask(lambda c: (poly(c, rect_pts(240, 60, 1500, 960, D(-1.5))), c.fill())), paper('#e3d6b8', 96, mottle=.012), edge='torn', seed=96, amp=10, rim=5, shadow=(8, 12, 9, .4))


@lru_cache(1)
def page(): return cached('s06', build)


@lru_cache(1)
def wing():
    F = Flyer(XF, seed=300); return F, wing_feathers(F.lead(), XF, 402)


def draw(d):
    t = d / FPS; cv = Canvas(page().copy(), jitter=.45, drawing=d)
    F, fs = wing(); F.move = True
    F.lay_spar(cv, (6, 9, 6, .4))
    k = min(len(fs), int(len(fs) * ease(.2, 4.6, t)) + 1)
    for j, (m, tex, q, s, tt) in enumerate(fs[:k]):
        new = j == k - 1
        cv.put(m, tex, edge='cut', seed=s, shadow=(12, 17, 10, .4) if new else (5, 8, 5, .32), marks=[(q, SEPIA, .5)], wobble=.8, move=new)
    L = F.lead(); g0, g1 = math.atan2(.12, -1.), math.atan2(-.62, -.78) + 2 * math.pi; pts = []
    for (a, c), t0 in zip(((L[0], L[1]), (L[1], L[2]), (L[2], L[3])), (0., .4, .8)):
        for u in np.linspace(0, 1, 5)[:-1]:
            p = lerp(a, c, u); g = g0 + (g1 - g0) * (t0 + u * .4); pts.append(xform(XF, (p[0] + 26 * math.cos(g), p[1] + 26 * math.sin(g))))
    nw = int(len(pts) * k / len(fs))
    if nw: wax(cv, pts[:nw], 403, drips=False, scale=XF[3] * .8, move=False)
    # the hand that sets the newest feather
    m = fs[k - 1][0]; M = cv2.moments((m > .5).astype(np.uint8))
    if M['m00'] > 0 and k < len(fs):
        tx, ty = M['m10'] / M['m00'], M['m01'] / M['m00']
        a = math.atan2(ty - 1250, tx - 2050); hx, hy = tx - math.cos(a) * 20, ty - math.sin(a) * 20
        def arm(c):
            limb_path(c, (2150, 1300), (hx - math.cos(a) * 60, hy - math.sin(a) * 60), 92, 58)
            c.save(); c.translate(hx, hy); c.rotate(a); c.scale(1, .62); c.arc(0, 0, 46, 0, 6.3); c.restore(); c.fill()
            limb_path(c, (hx - math.cos(a) * 10, hy - math.sin(a) * 10), (hx + math.cos(a - .7) * 50, hy + math.sin(a - .7) * 50), 17, 13)
        cv.put(mask(arm), slip(97), edge='cut', seed=97, shadow=(14, 20, 12, .42), move=True)
    fx, fy = candle(cv, 150, 1040, t, d, s=1.5)
    glow(cv, fx, fy, 700, .7 + .08 * rng(d).normal())
    return finish(cv, d, desat=.08)
