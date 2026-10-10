# Named styles

The skill's default look comes from the rated corpus (`style-rules.md`, `palettes.md`, `encoding.md`). A
**named style** is one paper's house look that the user asked to reuse. It sits on top of the defaults and
changes only what makes that look — weight, outlines, fill roles, framing — never the print floors (type ≥ 6 pt,
canvas inside the column band, contrast, no gradients) and never the workflow or the SVG contract.

| style | from | card | palette | exemplars |
|---|---|---|---|---|
| `charon` | Charon, MLSys 2026 (arXiv 2605.17164) — ink-outlined pastel boxes, bold labels, framed panels | [`charon.md`](charon.md) | `charon` | `assets/exemplars/styles/charon/` (7: 5 architecture, 2 mechanism) |

**Using one.** Only when the user asks for it (by name, by "like that paper", or by picking it in the brief).
Set `meta.style` to its id, `meta.palette` and `meta.font` to the ones its card names, read the card before the
drawing plan, and look at two or three of its exemplars next to the corpus exemplars the content search finds
(`scripts/find_exemplars.py --style <id> …` lists the style's figures first). The template, group and layout are
still chosen from the figure's content.

**What each style ships.**

- `references/styles/<id>.md` — the card: what the look is (measured at print size), which default rules it
  bends and which it keeps, how to assign its colours, SVG snippets, recipes seen in the paper, extra checks.
- `references/styles/<id>.json` — read by `lint.py` (advisory `style.*` checks, optional `max_saturated_fills`)
  and `spec_validate.py` (palette / font drift).
- a palette `<id>` in `palettes.json` with `"style": "<id>"` (and `assets/palettes/<id>.svg` from
  `scripts/distill/make_swatches.py`).
- `assets/exemplars/styles/<id>/` — the paper's figures as exemplars (same files as a corpus exemplar plus
  `style` / `origin: style-reference` in the manifest), built by `scripts/distill/build_style_exemplars.py <id>`
  from `scripts/distill/style_exemplars/<id>.json` (hand-written selection and semantic records) and the author
  figure PDFs under the repo's `external-styles/<id>/`. Kept apart from `assets/exemplars/figures/` because
  `build_exemplars.py --clean` regenerates that tree from the corpus.

**Adding another.** Get the author figures (arXiv source first: `https://arxiv.org/e-print/<id>`), measure them
at print size (fonts, stroke widths, fills by area, radii, padding — the numbers in `charon.md` §1 came from
PyMuPDF on the figure PDFs scaled to their printed width), write the selection JSON with a semantic record per
diagram (schema as the corpus records: `paper-figure-corpus/references/semantics-schema.md`), run
`build_style_exemplars.py`, then write the card, the JSON, the palette and a row in the table above. Check the
paper's licence and record it in the selection JSON: the exemplars ship with the skill.
