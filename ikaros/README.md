# ΙΚΑΡΟΣ (Ikaros): style test

A collage film of the Icarus myth, drawn entirely in code: no image files, no fonts, no found images. The score will be instrumental.

`style_test.jpg` is the first frame of the look: Ikaros at the sun, the wax running, Daidalos lower and level.

| File | What it does |
|---|---|
| `collage.py` | The paper kit: torn and scissor-cut edges, paper with fibres, halftone and engraved prints, gold leaf, black-figure paper, brass fasteners, shadows of pieces lifted off the page |
| `figure.py` | Black-figure puppets (limbs as separate pieces on brass fasteners, details incised to the clay colour), wings of single cut-paper feathers, wax |
| `style_test.py` | The test composition |

```bash
pip install numpy opencv-python-headless scipy pillow pycairo
python ikaros/style_test.py            # writes ikaros/out/style_test.png, about 6 s
```
