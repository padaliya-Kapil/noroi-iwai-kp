"""Timeline.  90 BPM in 4/4 at 24 fps: 16 frames a beat, 64 a bar.  Drawn on twos: 12 drawings a second, 32 a bar.
Every shot is two bars; so is every intertitle card (c01..c09, between the scenes).  (id, first frame, frames, what happens)"""
BPM, FPS, ON = 90, 24, 2
BEAT = FPS * 60 // BPM                     # 16 frames
BAR = BEAT * 4                             # 64 frames
STORY = [
    # I.  Crete
    ('s01', 'Title. The label is laid on the page, the letters ΙΚΑΡΟΣ dropped onto it one by one, the meander slid in beneath.'),
    ('c01', 'Card: Daedalus built Minos a house of winding walls to hide the Minotaur, half bull, half man.'),
    ('s02', 'King Minos, a great black-figure head, watches the Labyrinth being laid strip by strip at his feet.'),
    ('c02', 'Card: the work done, Minos would not let him go; father and son shut in by the sea.'),
    # II.  The tower
    ('s03', 'A stone tower on a cliff over the sea; the camera climbs it to the window where father and son are held. Gulls wheel.'),
    ('s04', 'At the window: a gull feather drifts in. Ikaros catches it; Daidalos sees what it could be.'),
    ('c03', 'Card: "He may block the land and the waves, but the sky is open."'),
    # III.  The wings
    ('s05', 'The workbench by candlelight: feathers sorted into rows, smallest to largest, laid down one at a time.'),
    ('s06', 'A wing is built on its reed, feather by feather, each root pressed into wax.'),
    ('c04', 'Card: "Keep to the middle way, Icarus."'),
    # IV.  The warning
    ('s07', 'Daidalos straps on the boy\'s wings and warns him: the sun above, the sea below; keep to the middle.'),
    ('s07b', 'The foretelling: by candlelight he shows the boy the future painted on a vase: the climb, the running wax, the fall, the feathers on the sea.'),
    ('c05', 'Card: at dawn they rose from the tower; the fisherman and the shepherd took them for gods.'),
    # V.  Flight
    ('s08', 'From the top of the tower they leap; the wings catch, and they rise past the camera.'),
    ('s09', 'Over the Aegean: islands slide by in layers, gulls keep pace; father and son fly side by side.'),
    ('c06', 'Card: the boy, delighting in his bold flight, left his father and climbed.'),
    ('s10', 'Ikaros climbs, higher and higher; below, Daidalos reaches up after him.'),
    ('c07', 'Card: the fierce sun softened the fragrant wax that bound the feathers.'),
    # VI.  The sun
    ('s11', 'At the sun. The wax runs, the first feathers loosen and tear away.'),
    ('s12', 'Close: the wing comes apart against the gold, feather after feather.'),
    ('c08', "Card: he beat his bare arms, caught no air, and fell calling his father's name."),
    # VII.  The sea
    ('s13', 'He falls with bare arms through the strips of sky, and the page itself begins to come apart around him.'),
    ('s14', 'The sea closes over him in a white cut splash; feathers come to rest on the water.'),
    ('c09', 'Card: "Icarus, where are you?" He saw the feathers on the waves, and cursed his own art.'),
    ('s15', 'Daidalos alone above the feathers. The island is named for the boy; the label is torn in two.'),
]
SHOTS = [(s, i * 2 * BAR, 2 * BAR) for i, (s, _) in enumerate(STORY)]
START = {s: a for s, a, n in SHOTS}
LEN = {s: n for s, a, n in SHOTS}
N = SHOTS[-1][1] + SHOTS[-1][2]            # 3200 frames, 133.3 s: 16 scenes and 9 intertitles
