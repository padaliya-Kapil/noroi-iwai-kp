# ΙΚΑΡΟΣ (Ikaros): style test

A collage film of the Icarus myth, drawn entirely in code: no image files, no fonts, no found images. The score will be instrumental.

`style_test.jpg` is the first frame of the look: Ikaros at the sun, the wax running, Daidalos lower and level.

Palette: parchment and bone papers, faded stone blue, fired clay, black slip, sepia engraving, an indigo sea, and gold leaf for the sun alone. Wings are bound to a reed spar along each arm with leather straps and a chest harness; the feather roots are set in wax.

| File | What it does |
|---|---|
| `collage.py` | The paper kit: torn and scissor-cut edges, paper with fibres, halftone and engraved prints, gold leaf, black-figure paper, brass fasteners, shadows of pieces lifted off the page |
| `figure.py` | Black-figure puppets (limbs as separate pieces on brass fasteners, details incised to the clay colour), wings of single cut-paper feathers, wax |
| `style_test.py` | The test composition |

```bash
pip install numpy opencv-python-headless scipy pillow pycairo
python ikaros/style_test.py            # writes ikaros/out/style_test.png, about 6 s
```
