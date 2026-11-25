"""The score, instrumental, made in code: lyre (plucked), aulos (double reed), tympanon (frame drum), kymbala (finger cymbals),
a drone, and the sounds of the page (paper laid and torn, wings, wax, wind, sea, the splash).
D Dorian while they are free; D Phrygian (the flattened second) from the sun to the end.  90 BPM, 30 bars, 80 s.
python ikaros/music.py  ->  ikaros/out/score.wav"""
import os, sys, math, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import film

SR = 44100; BEAT = 60 / film.BPM; BAR = 4 * BEAT; SHOT = 2 * BAR; LEN = film.N / film.FPS
TAIL = 3.; NS = int((LEN + TAIL) * SR)
R = np.random.default_rng(11)
DRY = np.zeros((2, NS)); WET = np.zeros((2, NS))


def hz(m): return 440. * 2 ** ((m - 69) / 12)
def bar(b, beat=0.): return b * BAR + beat * BEAT
def shot(i, t=0.): return (i - 1) * SHOT + t
def tt(n): return np.arange(n) / SR
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)


INSERT = 7 * SHOT          # the foretelling (s07b) was cut in here: everything written for later shots moves one shot on


def add(t0, sig, pan=0., gain=1., wet=.25, raw=False):
    if not raw and t0 >= INSERT - 1e-6: t0 += SHOT
    i = int(t0 * SR)
    if i >= NS or len(sig) == 0: return
    if i < 0: sig = sig[-i:]; i = 0
    sig = sig[:NS - i] * gain; l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    DRY[0, i:i + len(sig)] += sig * l * (1 - wet); DRY[1, i:i + len(sig)] += sig * r * (1 - wet)
    WET[0, i:i + len(sig)] += sig * l * wet; WET[1, i:i + len(sig)] += sig * r * wet


# ----------------------------------------------------------------------------------------------- instruments
def lyre(m, dur=2.5, vel=.6, bright=.5):
    """A gut-strung lyre: decaying harmonics, the high ones dying first, plucked near the end of the string, with a finger noise."""
    f = hz(m); n = int((dur + .5) * SR); t = tt(n); y = np.zeros(n)
    for k in range(1, 24):
        fk = f * k * (1 + .0004 * k * k)
        if fk > SR * .45: break
        a = (1 / k ** (1.35 - .5 * bright)) * abs(math.sin(k * math.pi * .17)); y += a * np.exp(-t * (1.1 + .45 * k)) * np.sin(2 * np.pi * fk * t + R.uniform(0, 6.3))
    y += bp(R.standard_normal(n), 1200, 5000) * np.exp(-t * 90) * .15
    y *= np.minimum(1, t / .002) * np.minimum(1, (dur + .5 - t) / .3)
    return y * vel * .5


def aulos(notes, vib=.004, breath=.04, bright=1.):
    """The double pipe: one continuous reed tone through a list of (start s, dur s, midi, vel) with legato glides between notes."""
    if not notes: return np.zeros(1), 0.
    t0 = notes[0][0]; t1 = max(s + d for s, d, *_ in notes); n = int((t1 - t0 + .4) * SR); t = tt(n)
    f = np.zeros(n); a = np.zeros(n)
    for s, d, m, *v in notes:
        i0, i1 = int((s - t0) * SR), int((s - t0 + d) * SR); vel = v[0] if v else .6
        f[i0:] = hz(m) if not isinstance(m, tuple) else 0
        if isinstance(m, tuple):                                               # a glide (m0, m1)
            g = np.linspace(m[0], m[1], i1 - i0); f[i0:i1] = 440 * 2 ** ((g - 69) / 12); f[i1:] = hz(m[1])
        env = np.ones(i1 - i0); att = min(len(env), int(.06 * SR)); rel = min(len(env), int(.08 * SR))
        env[:att] = np.linspace(.35, 1, att); env[-rel:] *= np.linspace(1, .55, rel); a[i0:i1] = np.maximum(a[i0:i1], env * vel)
    f = lp(f, 18); a = lp(a, 30)
    f = f * (1 + vib * np.sin(2 * np.pi * 5.3 * t) * np.minimum(1, t / .5))
    ph = 2 * np.pi * np.cumsum(f) / SR; y = np.zeros(n)
    for k in range(1, 18):
        fk = f * k; form = np.exp(-((fk - 780) / 380) ** 2) + .75 * np.exp(-((fk - 1650) / 520) ** 2) + .35 / k
        y += (1. if k % 2 else .55 * bright) * form * np.sin(k * ph) * (fk < SR * .45)
    y += bp(R.standard_normal(n), 900, 3500) * breath
    return y * a * .35, t0


def drum(kind='dum', vel=.7):
    n = int(.9 * SR); t = tt(n)
    if kind == 'dum':
        f = 52 + 95 * np.exp(-t * 28); y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5) + lp(R.standard_normal(n), 700) * np.exp(-t * 40) * .4
    elif kind == 'boom':
        f = 40 + 70 * np.exp(-t * 14); y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6) * 1.3 + lp(R.standard_normal(n), 400) * np.exp(-t * 12) * .6
    else:
        y = bp(R.standard_normal(n), 1800, 6000) * np.exp(-t * 45) + np.sin(2 * np.pi * 420 * t) * np.exp(-t * 60) * .3
    return y * vel


def kymbala(m=93, vel=.4, dur=3.):
    n = int(dur * SR); t = tt(n); f = hz(m); y = np.zeros(n)
    for r_, a, d in ((1, 1, 1.2), (2.76, .6, 2.), (5.4, .4, 3.), (8.93, .25, 4.5)):
        y += a * np.sin(2 * np.pi * f * r_ * t) * np.exp(-t * d)
    return y * vel * .3


def drone(m, dur, vel=.3, fade=1.):
    """A low reed drone with a slow beating second pipe."""
    n = int(dur * SR); t = tt(n); f = hz(m); y = np.zeros(n)
    for k in range(1, 10):
        y += (1 if k % 2 else .5) / k * (np.sin(2 * np.pi * f * k * t) + .6 * np.sin(2 * np.pi * f * 1.003 * k * t))
    env = np.minimum(1, t / fade) * np.minimum(1, (dur - t) / fade)
    return lp(y, 1400) * env * vel * .25


# ----------------------------------------------------------------------------------------------- the sounds of the page
def noise_env(n, lo, hi, env): return bp(R.standard_normal(n), lo, hi) * env


def tap(vel=.5):
    """A piece of paper laid down: a dry tick and a soft body thump."""
    n = int(.12 * SR); t = tt(n)
    return (noise_env(n, 1800, 5200, np.exp(-t * 160)) * .6 + np.sin(2 * np.pi * 170 * t) * np.exp(-t * 45) * .5) * vel


def whoosh(dur=.5, f0=300, f1=1400, vel=.4):
    n = int(dur * SR); x = R.standard_normal(n); y = np.zeros(n); s = 0.; t = tt(n)
    fc = f0 * (f1 / f0) ** (t / dur); a = 1 - np.exp(-2 * np.pi * fc / SR)
    for i in range(n): s += a[i] * (x[i] - s); y[i] = s
    return hp(y, 120) * np.sin(np.pi * t / dur) ** 2 * vel * 1.6


def tear(dur=.6, vel=.5):
    """Paper torn: a run of fibrous cracks."""
    n = int(dur * SR); t = tt(n); imp = (R.random(n) < 900 / SR) * R.uniform(.3, 1, n)
    y = bp(fftconvolve(imp, np.exp(-tt(300) * 3000) * R.standard_normal(300))[:n], 900, 7000) * 6
    y += noise_env(n, 2000, 8000, np.ones(n)) * .12
    return y * (np.minimum(1, t / .03) * np.minimum(1, (dur - t) / .1)) * vel


def sizzle(dur, vel=.3):
    n = int(dur * SR); imp = (R.random(n) < 300 / SR) * R.uniform(.2, 1, n)
    return hp(imp + R.standard_normal(n) * .02, 3000) * vel * np.minimum(1, tt(n) / .5) * np.minimum(1, (dur - tt(n)) / .5)


def sea(dur, vel=.3):
    n = int(dur * SR); t = tt(n); swell = .55 + .45 * np.sin(2 * np.pi * t / 5.5) ** 2
    return lp(R.standard_normal(n), 700) * swell * vel + hp(lp(R.standard_normal(n), 5000), 1500) * swell ** 3 * vel * .25


def wind(dur, vel=.3, rise=False):
    n = int(dur * SR); t = tt(n); env = (t / dur) ** 1.5 if rise else .6 + .4 * np.sin(2 * np.pi * t / 3.7)
    return (bp(R.standard_normal(n), 250, 900) + .5 * bp(R.standard_normal(n), 900, 2600) * env) * env * vel


def gull_cry(vel=.25):
    out = []
    for k in range(R.integers(2, 4)):
        n = int(.28 * SR); t = tt(n); f = 1700 - 700 * t / .28
        ph = 2 * np.pi * np.cumsum(f) / SR; y = (np.sin(ph) + .4 * np.sin(2 * ph) + .2 * np.sin(3 * ph)) * np.sin(np.pi * t / .28) ** .5
        out += [y, np.zeros(int(.08 * SR))]
    return np.concatenate(out) * vel


def splash_snd(vel=1.):
    n = int(3 * SR); t = tt(n); y = np.zeros(n); x = R.standard_normal(n); s = 0.
    fc = 5000 * np.exp(-t * 2.5) + 200; a = 1 - np.exp(-2 * np.pi * fc / SR)
    for i in range(n): s += a[i] * (x[i] - s); y[i] = s
    y *= np.exp(-t * 1.8) * 2.2; y += drum('boom', 1.) [:n] if n <= int(.9 * SR) else np.pad(drum('boom', 1.), (0, n - int(.9 * SR)))
    for k in range(18):                                                         # drops falling back
        i = int(R.uniform(.4, 2.2) * SR); m = int(.05 * SR); tm = tt(m)
        y[i:i + m] += np.sin(2 * np.pi * R.uniform(900, 2400) * (1 + tm * 6) * tm) * np.exp(-tm * 70) * .3
    return y * vel


# ----------------------------------------------------------------------------------------------- the score
def score():
    D, DP = [62, 64, 65, 67, 69, 71, 72], [62, 63, 65, 67, 69, 70, 72]
    motif = [50, 57, 62, 64, 65, 64, 62, 57, 48, 55, 60, 62, 64, 62, 60, 57]
    # I. Crete: the lyre alone, then the drone under the king
    for i, m in enumerate(motif * 2):
        add(bar(0, i * .5), lyre(m, 2.2, .55 - .1 * (i % 2)), pan=-.25, wet=.3)
    add(bar(2), drone(38, 2 * BAR + .5, .5), wet=.4); add(bar(2), drone(45, 2 * BAR + .5, .3), pan=.2, wet=.4)
    # II. The tower: the aulos theme, lyre broken chords, the sea
    themeA = [(4, 0, 1.5, 69), (4, 1.5, .5, 67), (4, 2, 2, 65), (5, 0, 1, 64), (5, 1, 1, 65), (5, 2, 2, 62),
              (6, 0, 1.5, 69), (6, 1.5, .5, 71), (6, 2, 1, 72), (6, 3, 1, 71), (7, 0, 2, 69), (7, 2, 1, 67), (7, 3, .9, 64)]
    y, t0 = aulos([(bar(b, s), d * BEAT, m, .55) for b, s, d, m in themeA]); add(t0, y, pan=.15, wet=.35)
    for b, ch in zip(range(4, 8), ([50, 57, 62, 65], [48, 55, 60, 64], [53, 57, 60, 65], [45, 52, 57, 60])):
        for k in range(4): add(bar(b, k), lyre(ch[k], 2., .4), pan=-.3, wet=.3)
    # III. The wings: a working ostinato on lyre and drum; the aulos joins for the wing
    ost = [50, 62, 57, 62, 60, 62, 57, 62]
    for b in range(8, 12):
        for i, m in enumerate(ost): add(bar(b, i * .5), lyre(m, 1.2, .42 if i % 2 else .5, bright=.3), pan=-.2, wet=.25)
        add(bar(b, 0), drum('dum', .55), wet=.15); add(bar(b, 2), drum('dum', .45), wet=.15)
        for k in (1, 3): add(bar(b, k + .5), drum('tek', .18), pan=.3, wet=.15)
    counter = [(10, 0, 1, 74), (10, 1, 1, 72), (10, 2, 2, 69), (11, 0, 1, 71), (11, 1, 1, 72), (11, 2, 1.8, 74)]
    y, t0 = aulos([(bar(b, s), d * BEAT, m, .45) for b, s, d, m in counter]); add(t0, y, pan=.2, wet=.35)
    # IV. The warning: the drone, a solemn phrase; a shimmer for the sun, a swell for the sea
    add(bar(12), drone(38, 2 * BAR, .55), wet=.4); add(bar(12), drone(45, 2 * BAR, .3), wet=.4)
    y, t0 = aulos([(bar(12, 0), 2 * BEAT, 62, .5), (bar(12, 2), 2 * BEAT, 65, .5), (bar(13, 0), 2 * BEAT, 64, .5), (bar(13, 2), 1.9 * BEAT, 62, .45)]); add(t0, y, wet=.4)
    for k in range(5): add(shot(7, .9 + k * .12), kymbala(93 + (k % 3) * 2, .35), pan=.5, wet=.5)
    add(shot(7, 2.5), drum('boom', .6), wet=.3); add(shot(7, 4.0), lyre(50, 3, .5) + lyre(57, 3, .4) + lyre(62, 3, .35), pan=-.2, wet=.35)
    # V. Flight: a gathering roll, the leaps, then the flight theme on everything
    for i in range(24): add(shot(8, i * 1.6 / 24), drum('tek', .08 + .25 * i / 24), pan=.2, wet=.2)
    add(shot(8, 1.6), drum('boom', .9), wet=.3); add(shot(8, 2.2), drum('boom', 1.), wet=.3)
    themeF = [(15, 0, .5, 74), (15, .5, .5, 76), (15, 1, 1, 77), (15, 2, .5, 76), (15, 2.5, .5, 74), (15, 3, 1, 72),
              (16, 0, 1.5, 74), (16, 1.5, .5, 69), (16, 2, 2, 74),
              (17, 0, .5, 77), (17, .5, .5, 79), (17, 1, 1, 81), (17, 2, .5, 79), (17, 2.5, .5, 77), (17, 3, 1, 76),
              (18, 0, 1, 77), (18, 1, 1, 79), (18, 2, 1, 81), (18, 3, 1, 83), (19, 0, 1, 84), (19, 1, 1, 83), (19, 2, 1, 84), (19, 3, 1, 86)]
    y, t0 = aulos([(bar(b, s), d * BEAT, m, .6) for b, s, d, m in themeF]); add(t0, y, pan=.15, wet=.3)
    chords = {15: [50, 57, 62, 65], 16: [48, 55, 60, 64], 17: [50, 57, 62, 65], 18: [53, 60, 65, 69], 19: [55, 62, 67, 71]}
    for b, ch in chords.items():
        for k in range(4):
            for j, m in enumerate(ch): add(bar(b, k) + j * .018, lyre(m, 1.4, .3, bright=.6), pan=-.3 + j * .05, wet=.25)
        for s, kind, v in ((0, 'dum', .7), (1, 'tek', .3), (1.5, 'tek', .22), (2, 'dum', .6), (3, 'tek', .3), (3.5, 'tek', .25)): add(bar(b, s), drum(kind, v), wet=.15)
    for b in (18, 19):
        for k in range(8): add(bar(b, k * .5), kymbala(88 + (k % 4) * 3 + (b - 18) * 5, .12 + .04 * k), pan=.4, wet=.5)
    # VI. The sun: Phrygian; trills against a clashing drone, a heartbeat; the climax as the wing comes apart
    add(bar(20), drone(38, 4 * BAR, .5), wet=.4); add(bar(20), drone(39, 4 * BAR, .25), pan=.3, wet=.4)
    tr = [(bar(20, i * .25), .25 * BEAT, 86 if i % 2 == 0 else 87, .45) for i in range(16)] + [(bar(21, 0), 2 * BEAT, (87, 89), .55), (bar(21, 2), 2 * BEAT, 89, .5)]
    y, t0 = aulos(tr, vib=.008); add(t0, y, pan=.15, wet=.35)
    for b in range(20, 24):
        for k in range(4): add(bar(b, k), drum('dum', .5), wet=.15); add(bar(b, k + .3), drum('dum', .3), wet=.15)
    for b in (20, 21):
        for i in range(16): add(bar(b, i * .25), lyre(62 if i % 2 else 63, .5, .2, bright=.8), pan=-.35, wet=.3)
    y, t0 = aulos([(bar(22), 2 * BAR - .2, (81, 93), .65)], vib=.012); add(t0, y, pan=.1, wet=.35)
    # VII. The fall: one long falling cry, then nothing; the sea; the lament
    y, t0 = aulos([(shot(13, 0), 4.2, (93, 50), .6)], vib=.02, breath=.08); add(t0, y, wet=.45)
    add(shot(14, 1.0), drone(38, 9.5, .35, fade=2.), wet=.5)
    add(shot(14, 1.5), lyre(50, 4, .5), pan=-.2, wet=.45); add(shot(14, 3.0), lyre(45, 4, .45), pan=-.2, wet=.45)
    lament = [50, 57, 62, 63, 65, 63, 62]
    for i, m in enumerate(lament): add(bar(28, i), lyre(m, 3.5 if i == 6 else 2.4, .5), pan=-.2, wet=.4)
    y, t0 = aulos([(bar(28, 0), 4 * BEAT, 62, .3), (bar(29, 0), 3.6 * BEAT, 57, .28)], vib=.003); add(t0, y, pan=.2, wet=.45)


def foretelling():
    """S07b, in film time: hushed; a drone, the lyre walking down the Phrygian scale, a chime and a soft drum as each panel is laid."""
    t0 = INSERT; A = [.45 + 1.05 * k for k in range(4)]
    add(t0, drone(38, SHOT, .45, fade=1.2), wet=.45, raw=True); add(t0, drone(39, SHOT * .8, .12, fade=1.5), pan=.3, wet=.45, raw=True)
    for k, (a, m) in enumerate(zip(A, (69, 67, 63, 62))):
        add(t0 + a, tap(.5), pan=.3, raw=True); add(t0 + a, drum('dum', .3), wet=.3, raw=True)
        add(t0 + a, kymbala(93 - 3 * k, .25), pan=.5, wet=.6, raw=True); add(t0 + a + .1, lyre(m, 3., .45), pan=-.2, wet=.45, raw=True)
    add(t0 + A[2] + .2, tear(.4, .2), pan=.4, wet=.3, raw=True)
    add(t0 + A[3] + .3, sea(1.4, .08), pan=.4, wet=.3, raw=True)
    add(t0 + 4.55, lyre(50, 3.5, .4) + lyre(57, 3.5, .3), pan=-.2, wet=.5, raw=True)
    add(t0 + 4.4, sizzle(.9, .03), pan=-.6, raw=True)                         # the candle


def effects():
    import importlib
    # the page
    add(shot(1, .1), whoosh(1.3, 200, 900, .3), pan=.6, wet=.2); add(shot(1, .35), tap(.6)); add(shot(1, .8), tap(.7))
    for j in range(6): add(shot(1, 1.1 + .3 * j), tap(.45), pan=-.3 + j * .12)
    s02 = importlib.import_module('shots.s02'); prev = 0
    for d in range(64):
        k = int(len(s02.WALLS) * s02.ease(.15, 4.4, d / 12))
        if k > prev: add(shot(2, d / 12), tap(.35), pan=.2 + .1 * math.sin(d)); prev = k
    s05 = importlib.import_module('shots.s05'); prev = 0
    for d in range(64):
        k = int(len(s05.FEATH) * s05.ease(.25, 4.7, d / 12)) + (1 if d / 12 > .25 else 0)
        if k > prev: add(shot(5, d / 12), tap(.3), pan=.4); prev = k
    prev = 0
    for d in range(64):
        k = min(44, int(44 * s05.ease(.2, 4.6, d / 12)) + 1)
        if k > prev: add(shot(6, d / 12), tap(.35), pan=.1); prev = k
    add(shot(4, 3.3), tap(.5), pan=-.4); add(shot(4, 4.5), kymbala(98, .45), pan=.5, wet=.5)
    for i in range(1, 7): add(shot(4, .2 + i * .5), whoosh(.6, 400, 900, .05), pan=.3)
    # sea and air
    add(shot(3), sea(SHOT, .22), wet=.3); add(shot(4), sea(SHOT, .1), wet=.3); add(shot(7, 2.5), sea(SHOT - 2.5, .2), wet=.3)
    for s in range(9, 13): add(shot(s), sea(SHOT, .12), wet=.3)
    add(shot(14), sea(2 * SHOT + TAIL, .26), wet=.3)
    for t0 in (.6, 2.4, 3.9): add(shot(3, t0), gull_cry(.15), pan=.5, wet=.4)
    for t0 in (.8, 3.1): add(shot(9, t0), gull_cry(.12), pan=-.5, wet=.4)
    add(shot(5), sizzle(2 * SHOT, .05), pan=-.5)                                # candle
    # wings
    for s, per, t0 in ((8, 1.1, 1.8), (9, 1.0, 0), (9, 1.3, .2), (10, 1.1, 0), (11, 1.5, 0), (12, 2.2, 0)):
        t = t0
        while t < SHOT: add(shot(s, t), whoosh(.45, 250, 1100, .16), pan=.2, wet=.2); t += per
    add(shot(8, 1.6), whoosh(.9, 150, 1600, .5), wet=.3); add(shot(8, 2.2), whoosh(.9, 150, 1600, .55), pan=.3, wet=.3)
    # wax and the wing coming apart
    add(shot(11), sizzle(2 * SHOT, .14), pan=.3)
    for t0 in (.6, 2.0, 3.3): add(shot(11, t0), tear(.35, .4), pan=.3); add(shot(11, t0), kymbala(96, .25), pan=.4, wet=.6)
    for k in range(11): add(shot(12, .3 + .4 * k), tear(.3, .45), pan=-.2 + .05 * k); add(shot(12, .3 + .4 * k), drum('boom', .35 + .03 * k), wet=.25)
    # the fall: wind and the page tearing
    add(shot(13), wind(4.3, .22, rise=True), wet=.3)
    for i in range(8): add(shot(13, 2.3 + .2 * ((i * 3) % 8)), tear(.7, .3), pan=(-1) ** i * .6, wet=.25)
    add(shot(14, .25), splash_snd(.9), wet=.35)
    for i, (_, _, t0) in enumerate([(560, 760, 2.0), (1320, 700, 1.6), (820, 900, 2.6), (1500, 860, 3.1), (380, 930, 3.5), (1100, 980, 2.3)]):
        add(shot(14, t0), lyre(86 + i % 3 * 2, .8, .08), pan=(i % 3 - 1) * .5, wet=.6)
    add(shot(15, 1.6), tap(.6)); add(shot(15, 2.8), tear(1.5, .5), wet=.3); add(shot(15, 4.3), whoosh(1., 120, 500, .4), wet=.3); add(shot(15, 5.25), drum('boom', .7), wet=.5)


def reverb(x, secs=2.6):
    n = int(secs * SR); t = tt(n); out = np.zeros_like(x)
    for ch in range(2):
        ir = R.standard_normal(n) * np.exp(-t * 6.9 / secs); ir = lp(ir, 5000); ir[:int(.02 * SR)] *= np.linspace(0, 1, int(.02 * SR))
        out[ch] = fftconvolve(x[ch], ir)[:x.shape[1]] / np.sqrt(np.sum(ir ** 2)) * .35
    return out


if __name__ == '__main__':
    score(); effects(); foretelling()
    mix = DRY + reverb(WET)
    mix = hp(mix, 30)
    # a gentle compressor (2:1 above -32 dB) that keeps the shape of the piece, loudness to about -18 dB RMS, a soft ceiling
    env = np.sqrt(lp(np.mean(mix ** 2, 0), 6, order=1).clip(1e-12)); th = 10 ** (-32 / 20)
    g = np.where(env > th, (env / th) ** (1 / 2 - 1), 1.); mix = mix * lp(g, 12, order=1)
    # the arc of the piece, in dB per shot: hushed in Crete, building through the flight, loudest as the wing comes apart
    arc = [-5, -5, -4, -4, -5, -4, -3, -5, -1, 0, 0, 1, 2, 0, -3, -5]
    centres = [(i + .5) * SHOT for i in range(len(film.SHOTS))]; tx = np.arange(mix.shape[1]) / SR
    mix *= 10 ** (np.interp(tx, centres, arc) / 20)
    mix *= 10 ** (-16 / 20) / np.sqrt(np.mean(mix[:, int(9 * SHOT * SR):int(13 * SHOT * SR)] ** 2))   # the flight sits at -16 dB
    mix = np.tanh(mix / .95) * .95
    end = int(LEN * SR); mix = mix[:, :end]; f = int(.4 * SR); mix[:, -f:] *= np.linspace(1, 0, f)
    out = os.path.join(HERE, 'out', 'score.wav'); os.makedirs(os.path.dirname(out), exist_ok=True)
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
    print(out, '%.1f s' % (mix.shape[1] / SR))
