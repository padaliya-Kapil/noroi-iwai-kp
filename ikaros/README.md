# ΙΚΑΡΟΣ (Ikaros): style test

A collage film of the Icarus myth, drawn entirely in code: no image files, no fonts, no found images. The score will be instrumental.

`style_test.jpg` is the first frame of the look: Ikaros at the sun, the wax running, Daidalos lower and level.

Palette: parchment and bone papers, faded stone blue, fired clay, black slip, sepia engraving, an indigo sea, and gold leaf for the sun alone. Wings are bound to a reed spar along each arm with leather straps and a chest harness; the feather roots are set in wax.

In motion the page (sky, rays, island, sun, the sea's sheets) is glued down and still. Everything animated is re-placed by hand each drawing, landing a fraction of a pixel off its mark; papers keep their grain as they move, and the exposure flickers slightly. Both flyers beat their wings and bob, feathers flutter (the loose ones most), the wax drips lengthen and let drops fall, one primary tears free of Ikaros's wing, cut feathers rock down to the sea, and the rows of wave crests slide against each other.

| File | What it does |
|---|---|
| `collage.py` | The paper kit: torn and scissor-cut edges, paper with fibres, halftone and engraved prints, gold leaf, black-figure paper, brass fasteners, shadows of pieces lifted off the page |
| `figure.py` | Black-figure puppets (limbs as separate pieces on brass fasteners, details incised to the clay colour), wings of single cut-paper feathers, wax |
| `style_test.py` | The test composition |
| `motion_test.py` | Three seconds of it as stop motion: 36 drawings at 12 a second, each held two frames at 24 fps → `motion_test.mp4` |

```bash
pip install numpy opencv-python-headless scipy pillow pycairo
python ikaros/style_test.py            # writes ikaros/out/style_test.png, about 6 s
python ikaros/motion_test.py --jobs 4  # writes ikaros/motion_test.mp4, about 1 min on 4 cores (needs ffmpeg)
```
