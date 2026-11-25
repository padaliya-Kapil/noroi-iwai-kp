# ΙΚΑΡΟΣ (Ikaros)

An 85-second collage film of the Icarus myth, drawn, animated and scored entirely in code: no image files, no fonts, no samples, no found images.
1920×1080, 24 fps, drawn on twos (12 drawings a second), 16 shots of two bars each at 90 BPM. The score is instrumental.

The look is a paper collage: Attic black-figure puppets cut from black paper with incisions to the clay colour and brass fasteners at the joints,
torn and scissor-cut papers (parchment, bone, stone blue, fired clay, sepia engraving, an indigo sea), and gold leaf for the sun alone.

## The story

| Shot | |
|---|---|
| s01 | Title: the sun set in, the label laid, the letters ΙΚΑΡΟΣ dropped one by one |
| s02 | King Minos watches the Labyrinth laid wall by wall; Daidalos sets the walls |
| s03 | The tower on its cliff; the camera climbs to the window where father and son are held |
| s04 | A gull's feather drifts in; Ikaros catches it; Daidalos has the idea |
| s05 | The workbench by candlelight: feathers sorted into rows, smallest to largest |
| s06 | A wing built on its reed, feather by feather, each root pressed into wax |
| s07 | The warning: the sun above, the sea below, keep to the middle |
| s07b | The foretelling: by candlelight, the future painted on a vase (the climb, the running wax, the fall, feathers on the sea); a hand on the boy's shoulder |
| s08 | They leap from the tower and rise |
| s09 | Over the Aegean, islands sliding by, gulls alongside |
| s10 | Ikaros climbs towards a growing sun; Daidalos below |
| s11 | At the sun: the wax runs, feathers tear free |
| s12 | Close against the gold: the wing comes apart |
| s13 | The fall; the page itself comes apart into the dark |
| s14 | The splash; feathers settle on the water |
| s15 | Daidalos alone; the name is torn in two; the dark comes down |

## Build

```bash
pip install numpy opencv-python-headless scipy pillow pycairo     # and ffmpeg on the PATH
python ikaros/render.py all --jobs 4      # each shot to ikaros/out/shots/<id>.mp4 (static pages are cached in ikaros/out/cache)
python ikaros/music.py                    # the score and effects to ikaros/out/score.wav
python ikaros/render.py --assemble        # picture and sound to ikaros/dist/ikaros.mp4
python ikaros/render.py s07 --preview 0,20,40   # a contact sheet of some drawings of one shot
```

## What is where

| File | What it does |
|---|---|
| `film.py` | The timeline and the story, shot by shot |
| `collage.py` | The paper kit: torn and cut edges, papers, engraving, halftone, gold leaf, black-figure paper, shadows, a camera over larger pages, hand-placed jitter |
| `figure.py` | Black-figure puppets: modelled limbs, poses, turning heads, tunic and robe, crown; wings of cut-paper feathers on a reed, wax |
| `shotkit.py` | Shared pieces: winged and wingless figures, gulls, stone walls, cliff, the Labyrinth, candle and glow, splash, falling feathers, sea, sun, label |
| `shots/` | One module per shot: a cached static page and `draw(d)` for drawing d |
| `music.py` | Lyre, aulos, frame drum, finger cymbals, drone, and the sounds of paper, wings, wax, wind, sea and splash, timed from the shots |
| `render.py` | Parallel rendering, previews, assembly |
| `style_test.py`, `motion_test.py` | The first still and the three-second motion test |
