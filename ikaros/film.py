"""Timeline.  90 BPM in 4/4 at 24 fps: 16 frames a beat, 64 a bar.  Drawn on twos: 12 drawings a second, 32 a bar.
Every shot is two bars.  (id, first frame, frames, what happens)"""
BPM, FPS, ON = 90, 24, 2
BEAT = FPS * 60 // BPM                     # 16 frames
BAR = BEAT * 4                             # 64 frames
STORY = [
    # I.  Crete
    ('s01', 'Title. The label is laid on the page, the letters ΙΚΑΡΟΣ dropped onto it one by one, the meander slid in beneath.'),
    ('s02', 'King Minos, a great black-figure head, watches the Labyrinth being laid strip by strip at his feet.'),
    # II.  The tower
    ('s03', 'A stone tower on a cliff over the sea; the camera climbs it to the window where father and son are held. Gulls wheel.'),
    ('s04', 'At the window: a gull feather drifts in. Ikaros catches it; Daidalos sees what it could be.'),
    # III.  The wings
    ('s05', 'The workbench by candlelight: feathers sorted into rows, smallest to largest, laid down one at a time.'),
    ('s06', 'A wing is built on its reed, feather by feather, each root pressed into wax.'),
    # IV.  The warning
    ('s07', 'Daidalos straps on the boy\'s wings and warns him: the sun above, the sea below; keep to the middle.'),
    # V.  Flight
    ('s08', 'From the top of the tower they leap; the wings catch, and they rise past the camera.'),
    ('s09', 'Over the Aegean: islands slide by in layers, gulls keep pace; father and son fly side by side.'),
    ('s10', 'Ikaros climbs, higher and higher; below, Daidalos reaches up after him.'),
    # VI.  The sun
    ('s11', 'At the sun. The wax runs, the first feathers loosen and tear away.'),
    ('s12', 'Close: the wing comes apart against the gold, feather after feather.'),
    # VII.  The sea
    ('s13', 'He falls with bare arms through the strips of sky, and the page itself begins to come apart around him.'),
    ('s14', 'The sea closes over him in a white cut splash; feathers come to rest on the water.'),
    ('s15', 'Daidalos alone above the feathers. The island is named for the boy; the label is torn in two.'),
]
SHOTS = [(s, i * 2 * BAR, 2 * BAR) for i, (s, _) in enumerate(STORY)]
START = {s: a for s, a, n in SHOTS}
LEN = {s: n for s, a, n in SHOTS}
N = SHOTS[-1][1] + SHOTS[-1][2]            # 1920 frames, 80 s
