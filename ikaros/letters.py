"""A cut-paper alphabet: Roman inscriptional capitals as monoline strokes, drawn by code (no font).
Each glyph is (width, strokes) in a box whose cap height is 1 (y down); a stroke is a polyline, or ('dot', x, y).
set_line(c, text, x, y, hh) draws one line into a cairo context; measure() gives its width."""
import math


def arc(cx, cy, rx, ry, a0, a1, n=14):
    """Points on an ellipse arc, angles in degrees, counter-clockwise as on paper (y up for the angle, y down on the page)."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy - ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


P = ('dot', .05, .93)
G = {
    'A': (.72, [[(0, 1), (.36, 0), (.72, 1)], [(.16, .62), (.56, .62)]]),
    'B': (.58, [[(.34, .47), (0, .47), (0, 0), (.32, 0)] + arc(.32, .235, .22, .235, 90, -90)[1:],
                [(0, .47), (.36, .47)] + arc(.36, .735, .24, .265, 90, -90)[1:] + [(0, 1), (0, .47)]]),
    'C': (.66, [arc(.38, .5, .36, .5, 42, 318, 22)]),
    'D': (.66, [[(0, 0), (0, 1), (.28, 1)] + arc(.28, .5, .36, .5, -90, 90, 18)[1:] + [(0, 0)]]),
    'E': (.52, [[(.52, 0), (0, 0), (0, 1), (.52, 1)], [(0, .5), (.42, .5)]]),
    'F': (.5, [[(.5, 0), (0, 0), (0, 1)], [(0, .5), (.4, .5)]]),
    'G': (.7, [arc(.38, .5, .36, .5, 42, 320, 22), [(.42, .58), (.72, .58), (.72, .9)]]),
    'H': (.64, [[(0, 0), (0, 1)], [(.64, 0), (.64, 1)], [(0, .5), (.64, .5)]]),
    'I': (.1, [[(.05, 0), (.05, 1)]]),
    'J': (.44, [[(.44, 0), (.44, .72)] + arc(.22, .72, .22, .28, 0, -180)[1:]]),
    'K': (.6, [[(0, 0), (0, 1)], [(.6, 0), (0, .58)], [(.2, .42), (.62, 1)]]),
    'L': (.5, [[(0, 0), (0, 1), (.5, 1)]]),
    'M': (.8, [[(0, 1), (0, 0), (.4, .72), (.8, 0), (.8, 1)]]),
    'N': (.64, [[(0, 1), (0, 0), (.64, 1), (.64, 0)]]),
    'O': (.78, [arc(.39, .5, .39, .5, 0, 360, 28)]),
    'P': (.56, [[(0, 1), (0, 0), (.32, 0)] + arc(.32, .25, .24, .25, 90, -90)[1:] + [(0, .5)]]),
    'Q': (.78, [arc(.39, .5, .39, .5, 0, 360, 28), [(.48, .74), (.82, 1.06)]]),
    'R': (.6, [[(0, 1), (0, 0), (.32, 0)] + arc(.32, .25, .24, .25, 90, -90)[1:] + [(0, .5)], [(.26, .5), (.6, 1)]]),
    'S': (.56, [arc(.28, .26, .27, .26, 25, 270, 16)[:-1] + arc(.28, .76, .28, .24, 90, -155, 16)]),
    'T': (.62, [[(0, 0), (.62, 0)], [(.31, 0), (.31, 1)]]),
    'U': (.62, [[(0, 0), (0, .7)] + arc(.31, .7, .31, .3, 180, 360)[1:] + [(.62, 0)]]),
    'V': (.66, [[(0, 0), (.33, 1), (.66, 0)]]),
    'W': (.92, [[(0, 0), (.23, 1), (.46, .28), (.69, 1), (.92, 0)]]),
    'X': (.62, [[(0, 0), (.62, 1)], [(.62, 0), (0, 1)]]),
    'Y': (.62, [[(0, 0), (.31, .5), (.62, 0)], [(.31, .5), (.31, 1)]]),
    'Z': (.58, [[(0, 0), (.58, 0), (0, 1), (.58, 1)]]),
    '.': (.1, [P]),
    ',': (.12, [P, [(.07, .95), (.02, 1.12)]]),
    ':': (.1, [('dot', .05, .38), P]),
    ';': (.12, [('dot', .06, .38), P, [(.07, .95), (.02, 1.12)]]),
    '!': (.1, [[(.05, 0), (.05, .7)], P]),
    '?': (.48, [arc(.24, .24, .24, .24, 160, -80, 12) + [(.24, .72)], ('dot', .24, .93)]),
    "'": (.08, [[(.05, 0), (.03, .24)]]),
    '-': (.4, [[(.04, .55), (.36, .55)]]),
    ' ': (.36, []),
}
GAP = .22                   # space between letters, in cap heights


def measure(text, hh):
    return sum((G[ch][0] + GAP) * hh for ch in text) - GAP * hh


def wrap(text, hh, width):
    lines, cur = [], ''
    for word in text.split():
        t = (cur + ' ' + word).strip()
        if measure(t, hh) > width and cur: lines.append(cur); cur = word
        else: cur = t
    return lines + [cur]


def set_line(c, text, x, y, hh, jitter=None, weight=.115):
    """Stroke text with its top-left at (x, y).  jitter(i) -> (dx, dy, rot rad) for letter i: the hand that cut and laid it."""
    c.set_line_width(hh * weight)
    for i, ch in enumerate(text):
        w, strokes = G[ch]
        dx, dy, rt = jitter(i) if jitter else (0, 0, 0)
        c.save(); c.translate(x + w * hh / 2 + dx, y + hh / 2 + dy); c.rotate(rt); c.translate(-w * hh / 2, -hh / 2)
        for s in strokes:
            if s[0] == 'dot': c.new_sub_path(); c.arc(s[1] * hh, s[2] * hh, hh * weight * .75, 0, 2 * math.pi); c.fill(); continue
            c.move_to(s[0][0] * hh, s[0][1] * hh)
            for px, py in s[1:]: c.line_to(px * hh, py * hh)
            c.stroke()
        c.restore()
        x += (w + GAP) * hh
