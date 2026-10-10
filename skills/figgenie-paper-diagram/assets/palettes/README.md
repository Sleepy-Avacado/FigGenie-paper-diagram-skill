# Palette swatch cards

One 600x300 SVG per palette in [`../../references/palettes.json`](../../references/palettes.json).
Each card carries the 12 role swatches with their hex values plus a tiny sample diagram
(container, three module boxes, an accent box, a plain and an accent arrow, a lane, a
legend chip, a muted annotation) drawn in that palette, so the look can be judged without
opening an exemplar figure.

Regenerate after editing `palettes.json`:

```
python3 ../../scripts/distill/make_swatches.py
```

| card | palette | module / accent | figures | first exemplars |
| --- | --- | --- | --- | --- |
| [`blue-orange.svg`](blue-orange.svg) | Blue modules, orange accent | `#dae8fc` / `#ed7d31` | 39 (14.3%) | `asplos26-127_fig3`, `sosp25-053_fig4` |
| [`green-red.svg`](green-red.svg) | Green modules, red highlight | `#d8f3dc` / `#ff0000` | 36 (13.2%) | `nsdi26-087_fig3`, `asplos26-129_fig3` |
| [`cream-pastel.svg`](cream-pastel.svg) | Cream and pastel mix | `#fff2cc` / `#ed7d31` | 33 (12.1%) | `asplos26-077_fig3`, `asplos25-100_fig3` |
| [`greyscale.svg`](greyscale.svg) | Greyscale only | `#f2f2f2` / `#666666` | 27 (9.9%) | `asplos25-031_fig1`, `sosp23-013_fig3` |
| [`grey-scaffold.svg`](grey-scaffold.svg) | Grey scaffold with pastel tints | `#d9d9d9` / `#ed7d31` | 26 (9.6%) | `asplos25-039_fig3`, `nsdi24-023_fig3` |
| [`blue-mono.svg`](blue-mono.svg) | Blue monochrome | `#deebf7` / `#4472c4` | 23 (8.5%) | `sosp23-026_fig3`, `asplos26-076_fig2` |
| [`warm-bands.svg`](warm-bands.svg) | Warm container bands | `#e2f0d9` / `#f0a30a` | 22 (8.1%) | `sosp24-041_figtex8`, `osdi26-024_fig8` |
| [`high-contrast.svg`](high-contrast.svg) | High-contrast primaries | `#f2f2f2` / `#c00000` | 22 (8.1%) | `osdi25-012_fig3`, `asplos25-096_fig1` |
| [`multi-hue-categorical.svg`](multi-hue-categorical.svg) | Multi-hue categorical | `#d5e8d4` / `#b1001c` | 18 (6.6%) | `asplos26-141_fig2`, `asplos25-110_fig2` |
| [`amber-highlight.svg`](amber-highlight.svg) | Amber highlight on neutral | `#ffeed9` / `#cc9600` | 13 (4.8%) | `asplos25-082_fig1`, `asplos26-019_fig1` |
| [`cool-grey-cyan.svg`](cool-grey-cyan.svg) | Cool grey and cyan | `#e4f1f7` / `#156082` | 11 (4.0%) | `asplos26-036_fig8`, `nsdi26-127_fig6` |


### Ground families (added 2026-09-18)

Same roles; the difference is what sits behind the boxes. A dashed empty square in the `container` / `lane`
swatch (and a dashed sample container) means **no fill — outline only**; the `*-ground` cards fill it with a tint.

| card | palette | container / module / accent | figures | first exemplars |
| --- | --- | --- | --- | --- |
| [`blue-outline.svg`](blue-outline.svg) | Blue boxes, outline containers | — / `#dae8fc` / `#4472c4` | 97 (13.4%) | `osdi26-094_fig1`, `osdi24-032_fig9` |
| [`ink-outline.svg`](ink-outline.svg) | Near-white boxes, ink outlines, one accent | — / `#f2f2f2` / `#b1001c` | 90 (12.4%) | `nsdi26-091_fig4`, `sosp25-007_fig2` |
| [`pastel-outline.svg`](pastel-outline.svg) | Cream and pastel boxes, outline containers | — / `#fff2cc` / `#ffc000` | 87 (12.0%) | `asplos26-026_fig6`, `asplos26-080_fig5` |
| [`pastel-regions.svg`](pastel-regions.svg) | Each region its own pastel tint | `#fff2cc` / `#dae8fc` / `#d6b656` | 52 (7.2%) | `nsdi26-144_fig1`, `nsdi24-022_fig1` |
| [`green-outline.svg`](green-outline.svg) | Green boxes, outline containers | — / `#d8f3dc` / `#ff0000` | 45 (6.2%) | `osdi23-011_fig5`, `nsdi24-107_fig5` |
| [`blue-ground.svg`](blue-ground.svg) | Pale-blue ground, warm boxes | `#dceaf7` / `#fff2cc` / `#c00000` | 45 (6.2%) | `asplos26-096_fig6`, `nsdi24-064_fig3` |
| [`greyscale-outline.svg`](greyscale-outline.svg) | Greyscale, outline containers | — / `#cccccc` / `#ff0000` | 44 (6.1%) | `osdi23-032_fig5`, `osdi24-007_fig3` |
| [`cream-ground.svg`](cream-ground.svg) | Cream ground, blue boxes | `#fff2cc` / `#dae8fc` / `#f0a30a` | 26 (3.6%) | `asplos26-153_fig14`, `asplos25-034_fig8` |
| [`categorical-outline.svg`](categorical-outline.svg) | Categorical hues, outline containers | — / `#f8cecc` / `#a50040` | 25 (3.4%) | `asplos25-110_fig1`, `asplos26-127_fig2` |
| [`green-ground.svg`](green-ground.svg) | Pale-green ground, blue boxes | `#e2f0d9` / `#dae3f3` / `#ed7d31` | 25 (3.4%) | `nsdi26-087_fig3`, `asplos25-097_fig2` |

### Named styles (added 2026-10-09)

One paper's palette, measured from its figures; use it with `meta.style` set to the same id (`../../references/styles/`).

| card | palette | module / accent | from | exemplars |
| --- | --- | --- | --- | --- |
| [`charon.svg`](charon.svg) | Charon: ink outlines, identity pastels, grey headers | `#cddfff` / text `#178d6a` | Charon, MLSys 2026 | `mlsys26-charon_fig3`, `mlsys26-charon_fig5` |

Written by `scripts/distill/make_swatches.py`; the hue families come from
`scripts/distill/palette_cluster.py` over 272 architecture figures and the ground families from
`scripts/distill/palette_grounds.py` over the 726 good figures with semantic records. Label colours inside
each card are chosen by WCAG contrast, so a dark accent shows white text - the same rule
the drawing agent should apply. Plain SVG, no external references, no rendering required.
