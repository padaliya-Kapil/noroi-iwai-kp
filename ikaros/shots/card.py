"""Intertitles, as in a silent film: a black card laid on the page, a cream border and Greek key bands, the words cut from
cream paper and stuck on by hand.  The words are short passages of Ovid (Metamorphoses VIII), freely translated."""
from shotkit import *
import letters as LT

CREDIT = 'AFTER OVID, METAMORPHOSES VIII'
CARDS = {
    'c01': "DAEDALUS, MOST FAMOUS OF CRAFTSMEN, BUILT KING MINOS A HOUSE OF WINDING WALLS, TO HIDE A MONSTER: THE MINOTAUR, HALF BULL, HALF MAN.",
    'c02': "THE WORK DONE, MINOS WOULD NOT LET HIM GO. DAEDALUS AND HIS SON WERE SHUT IN BY THE SEA.",
    'c03': "'HE MAY BLOCK THE LAND AND THE WAVES,' SAID DAEDALUS, 'BUT THE SKY IS OPEN. WE WILL GO THAT WAY.'",
    'c04': "'KEEP TO THE MIDDLE WAY, ICARUS. FLY TOO LOW, AND THE SEA WILL WEIGH YOUR WINGS; TOO HIGH, AND THE SUN WILL BURN THEM.'",
    'c05': "AT DAWN THEY ROSE FROM THE TOWER. THE FISHERMAN AND THE SHEPHERD BELOW LOOKED UP, AND TOOK THEM FOR GODS.",
    'c06': "BUT THE BOY, DELIGHTING IN HIS BOLD FLIGHT, LEFT HIS FATHER AND CLIMBED TOWARDS THE SKY.",
    'c07': "THE NEARNESS OF THE FIERCE SUN SOFTENED THE FRAGRANT WAX THAT BOUND THE FEATHERS.",
    'c08': "HE BEAT HIS BARE ARMS, BUT THEY CAUGHT NO AIR. CALLING HIS FATHER'S NAME, HE FELL INTO THE DARK BLUE SEA.",
    'c09': "'ICARUS!' HE CRIED. 'ICARUS, WHERE ARE YOU?' HE SAW THE FEATHERS ON THE WAVES, AND CURSED HIS OWN ART.",
}
CX0, CY0, CW, CH = 130, 80, 1660, 920
HH, LEAD = 56, 1.95


def build_for(sid):
    seed = 400 + int(sid[1:]) * 10
    def build(cv, h, w):
        cv.put(mask(lambda c: (c.rectangle(-20, -20, w + 40, h + 40), c.fill())), ST.engraved(PAL['parch'], seed, pitch=6, ang=-3, width=.25, ink=.2), edge='none', shadow=(0, 0, 0, 0))
        border = mask(lambda c: (c.set_line_width(3), c.rectangle(CX0 + 26, CY0 + 26, CW - 52, CH - 52), c.stroke(), c.set_line_width(1.5), c.rectangle(CX0 + 36, CY0 + 36, CW - 72, CH - 72), c.stroke()))
        cv.put(mask(lambda c: (poly(c, rect_pts(CX0, CY0, CW, CH, D(-.4))), c.fill())), slip(seed + 1, '#1b1512'), edge='cut', seed=seed + 1, wobble=1.2, shadow=(10, 15, 12, .5),
               marks=[(border, '#d8cba9', .85)])
        meander_band(cv, CY0 + 52, h=36, x0=CX0 + 52, x1=CX0 + CW - 52, ang=0, seed=seed + 2)
        meander_band(cv, CY0 + CH - 88, h=36, x0=CX0 + 52, x1=CX0 + CW - 52, ang=0, seed=seed + 3)
        lines = LT.wrap(CARDS[sid], HH, CW - 300); top = CY0 + CH / 2 - (len(lines) * HH * LEAD - (LEAD - 1) * HH) / 2 - 24
        r = rng(seed + 4); jit = lambda i: (r.normal(0, .8), r.normal(0, 1.4), r.normal(0, .025))
        for k, ln in enumerate(lines):
            x = W / 2 - LT.measure(ln, HH) / 2; y = top + k * HH * LEAD
            cv.put(mask(lambda c, ln=ln, x=x, y=y: (c.set_line_cap(0), c.set_line_join(0), LT.set_line(c, ln, x, y, HH, jitter=jit))),
                   paper('#ebe1c8', seed + 10 + k, mottle=.03), edge='cut', seed=seed + 10 + k, shadow=(2, 3, 2, .55), wobble=.4)
        ch = 22; x = W / 2 - LT.measure(CREDIT, ch) / 2
        cv.put(mask(lambda c: LT.set_line(c, CREDIT, x, CY0 + CH - 140, ch, weight=.13)), paper(PAL['clay'], seed + 30), edge='cut', seed=seed + 30, shadow=(1, 2, 1, .5), wobble=.2)
    return build


def make(sid):
    def page(): return cached(sid, build_for(sid))
    def draw(d):
        t = d / FPS; base = page()
        if d < 3:                                                              # the card is laid down: it lands on the third drawing
            k = (3 - d) / 3.; s = 1 + .03 * k
            im = view(base, -W / 2 * (s - 1) / s + 8 * k, -H / 2 * (s - 1) / s - 14 * k, s)
        else: im = base.copy()
        cv = Canvas(im, jitter=0, drawing=d)
        return finish(cv, d, desat=.1)
    return page, draw
