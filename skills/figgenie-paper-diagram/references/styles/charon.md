# Style `charon` — ink-outlined pastel boxes, bold labels, framed panels

The look of the seven diagrams in *Charon: A Unified and Fine-Grained Simulator for Large-Scale LLM Training
and Inference* (Yang et al., MLSys 2026, arXiv 2605.17164, ByteDance Seed). Added on the user's request
(2026-10-09) because they find these figures handsome. It is **one paper's house style, not a corpus
average**: no rating or statistic of the corpus comes from it, and the numbers below are measured on those seven
figures at their printed size (PowerPoint exports; text Calibri / Aptos).

**When to use it.** Only when the user asks for it ("Charon 风格", "像 Charon 那样", "粗体描边那种", or picks it
in the brief). Then set, in the spec:

```json
"meta": { "style": "charon", "palette": "charon", "font": "calibri", ... }
```

`spec_validate.py` warns when the palette or font drifts from the style; `lint.py` reads
`references/styles/charon.json` and adds three advisory checks (`style.weight`, `style.outline`,
`style.stroke`) and lets up to four saturated fills pass (mechanism figures use one solid hue per resource).
Everything else in the skill applies unchanged — workflow, brief gate, SVG contract, templates, mechanism
groups. **Reference, not recipe:** the style decides how boxes, type, colour and frames look; the layout still
comes from what this figure must show. When the content wants something the seven figures never did, do it in
the style's materials (ink outline, bold type, identity pastel) and say so in the plan.

Exemplars: `assets/exemplars/styles/charon/index.json` (all seven, with lessons). Search them alongside the
corpus with `python3 scripts/find_exemplars.py --style charon --content "…"`. LOOK at `preview.png` (300 dpi)
for detail and `print.png` for how dense it really is at print size.

## 1. The signature, measured

| element | Charon | the corpus default it replaces |
|---|---|---|
| type | **every label bold** (Calibri Bold; Aptos Bold for some titles), one family; 6–7 pt in a single column, 6–7 pt in the double-column overview | regular weight, bold only for titles |
| box | rounded rectangle, radius 0.7–1.1 pt (up to 2.5 pt on wide boxes), **dark-ink outline `#042433` on every box**, 0.5–0.7 pt | outline optional; grey or no outline on pale boxes |
| box size | tight: about 1.5–2 pt between the label's glyph ink and the outline (Charon's 6 pt labels sit in 9–10 pt boxes); a 6.5 pt Carlito Bold label with a descender needs about 9 pt (`place_text.py` prints the minimum for each label), width ≈ label + 4–6 pt | height 1.4 × size + 6 pt, width + 8 pt |
| fill | four pastels that **name a kind of component** and keep that meaning in every figure of the paper: blue `#cddfff`, peach `#ffecd6`, mint `#b5d8cb`, pink `#ffc9c3`; grey `#d9d9d9` for structure | module fill + one saturated accent |
| accent | **no accent fill**. "Ours" vs "the old way" is said in **coloured bold text**: green `#178d6a` for ours / the result, red `#c00000` for the baseline / its cost | one saturated accent box |
| structure | grey **header bar** (filled `#d9d9d9`, ink outline) opening a subsystem; subsystem **title under its box**; flank titles above | container title at the top, no header bar |
| frames | a **black 1–1.3 pt frame** around the whole figure (overview) or around each panel; bold **(a) (b) (c)** in the panel's top-left corner; **dash-dot rules** split a panel into a diagram and its companion | no outer frame; panels separated by space |
| regions | a family of interchangeable steps sits in a **pale tinted region with a dotted outline** (`#fef3eb`, `#edf1f9`, `#fff2f1`); a whole subsystem may be one **identity-tinted panel** with white boxes inside | outline-only containers (49 %) |
| bookends | input and output of a pipeline as **tall grey bars with rotated bold text** at both ends | an input box on the left |
| arrows | short, straight, black, solid head; few of them; verbs on arrows only where a reader needs them (Profile, Lookup, Train) | — |
| icons | framework logos as bitmaps (Hugging Face, PyTorch, vLLM), GPU-card stacks, database cylinders, line icons for config; **tiny glyphs for what a stage produces**: node-link graphs with pastel nodes, timeline bars, a pruned tree | icons in 30 % of figures |
| lists | outputs and capabilities as **bold bullet lists** inside a framed card, one small glyph beside each item | — |

Mechanism figures in the style (Figures 6 and 12) keep the bold titles and black outlines but change the colour
logic: **one hue per resource or owner** (green NVLink / blue IB; blue request 1 / red request 2), **solid
saturated = normal, pale fill + dotted outline = degraded or not resident**, a shade ramp of one hue for an
index (chunk 1–4), values written inside the bars in regular weight, and the arithmetic beside the rows in the
resource's own colour. `palettes.json` → `charon.state_pairs` has the three hue pairs.

## 2. What it bends, what it keeps

Bends (say so in the plan; these are the style, not mistakes): bold everywhere; four identity pastels instead
of "one accent"; the accent carried by text colour; an outer frame; header bars; up to four saturated fills
in a mechanism figure; denser boxes than the corpus padding.

Keeps, unchanged: **type ≥ 6 pt** (Charon's single-column figures print some labels at 5–5.8 pt — copy their
structure, not their type size; the floor was kept on purpose when the style was added), white canvas, no gradients or shadows,
every box and edge carries its spec id, ≤ 3 sizes, contrast. Reach Charon's density at 6 pt by:

- **tight boxes** (1.5–2 pt between the glyph ink and the outline; `text.padding` warns below 1.5 pt, which for a
  6.5 pt bold label is a box of about 8 pt without descenders and 9 pt with them -- `place_text.py --font calibri
  --bold center --box ...` places the label and says when the box is too small) instead of smaller type — bold
  Carlito is about 3 % wider than regular, so measure with `measure_text.py --font calibri --size 6.5 --bold`;
- **fewer words**: Charon labels are 1–3 words; a stage's detail is a glyph (graph, bars, tree), not a sentence;
- **titles below** subsystems and **header bars** inside them, which saves a title row per box;
- in a **single-column** figure, going **taller** rather than wider (Figure 2 is 228 × 286 pt). This applies
  only when the column was not decided by the content or the user: a figure the user wants across both columns —
  a composite overview, say — keeps its width, and the three points above do the work.

## 3. Assigning the colours

1. List the figure's components by **kind** (engines, graph stages, data, hardware, results). Give the 3–4
   kinds that matter one identity pastel each; grey is structure (headers, platform card, bookends, existing
   framework parts). Leaves get the identity colour; their containers stay white (outlined) or take the
   region tint of the same family — never a darker fill than their children.
2. **Reuse the mapping across the paper's figures.** If the user is drawing a series, keep a small table in
   the brief (Charon: blue = profiling / forward / compute, peach = prediction / output, mint = analytical /
   communication / norm, pink = graph / backward / pruning) and reuse it; a later figure can refer back to a
   subsystem by a dotted box in its tint (Figure 5's fused engine).
3. Text colour is the only accent: green for ours, red for the baseline, and only on the few words that carry
   the claim. Step colours (blue forward, red backward, green update) may repeat in step labels and arrows.
4. A legend is rarely needed — the identity colours are named by the boxes themselves; add one when a
   mechanism figure's state encoding (solid vs pale-dotted) is not obvious (Figure 6 puts it above the axis as
   two arrow pairs).

## 4. Drawing it in SVG

Root and defaults (pt; font stack from `fonts.json` key `calibri`):

```xml
<svg viewBox="0 0 240 150" font-family="Carlito, Calibri, 'Segoe UI', Arimo, Arial, sans-serif"
     font-weight="bold" font-size="6.5" fill="#000">
  <!-- box: ink outline on every box -->
  <rect x=".." y=".." width=".." height="10" rx="1" fill="#cddfff" stroke="#042433" stroke-width="0.65"/>
  <!-- grey header bar opening a subsystem -->
  <rect ... height="10" rx="0.8" fill="#d9d9d9" stroke="#042433" stroke-width="0.65"/>
  <!-- outer / panel frame -->
  <rect x="0.65" y="0.65" width="W-1.3" height="H-1.3" fill="none" stroke="#000" stroke-width="1.3"/>
  <!-- dash-dot divider inside a panel -->
  <line ... stroke="#000" stroke-width="0.8" stroke-dasharray="4 1.5 1 1.5"/>
  <!-- pass-family region -->
  <rect ... rx="0" fill="#fef3eb" stroke="#042433" stroke-width="0.6" stroke-dasharray="1 1"/>
</svg>
```

Arrows: black, 0.8 pt, one solid 4 pt head for the whole figure (`parts-styles.md` §8 arrowheads); keep them
short — Charon puts boxes next to each other and lets adjacency carry the order inside a subsystem. Rotated
bookend text: `transform="rotate(-90 x y)"`, centred in the bar (the linter's `gutter.centre` checks it).
Glyphs worth reusing: node-link graph (4–8 pastel circles, 0.6 pt black links), GPU-card stack (three offset
outlined cards with "GPU"), database cylinder, timeline bars (a row of small pastel rectangles). Cylinders and
card stacks have default geometry in `parts-styles.md` §6–7; search `assets/symbols/index.json` (`gpu`,
`cylinder`, `graph`) for cut parts, then recolour to the identity fills and outline in ink. Logos are local PNGs (spec-guide §4 "Bitmaps") and only when the user supplies or
approves them.

## 5. Recipes seen in the seven figures (pick, adapt or ignore)

- **Flank–core–flank overview** (Figure 3, double column): inputs titled above on the left, one rounded frame
  holding 2–4 equal subsystems titled underneath, outputs as framed bullet cards on the right, all inside the
  black outer frame. In a single column, stack it: inputs on top, subsystems in a row, outputs below.
- **Subsystem as identity panels** (Figure 5): each engine a full-height tinted panel with white boxes inside;
  a decision chain at the end whose boxes repeat the tints, Y / N on the branches.
- **Pass pipeline** (Figure 4b): rotated grey bookends, three dotted tinted regions of white step boxes with a
  vertical ellipsis for "more passes", elbow arrows between regions.
- **Background in bands** (Figure 2): three framed panels stacked, each split by a dash-dot rule into a diagram
  and its companion (zoom, catalogue, chart).
- **Teaser** (Figure 1): system as a grey platform card of full-width capability bars, two framed side cards
  with one number each, red route vs green route into the same outputs.
- **Before/after timelines** (Figure 6) and **per-rank timelines coloured by owner** (Figure 12) for mechanism
  figures, ending in a dashed finish line and a labelled double arrow for the saving.

## 6. Extra checks before declaring done

- Are all labels bold and every box outlined in ink? (`style.weight`, `style.outline`)
- Does each pastel mean one kind of thing, the same thing everywhere in the figure (and the series)?
- Is the claim carried by at most a few green / red words, not by a coloured box?
- Is anything below 6 pt? Tighten boxes and cut words before shrinking type.
- Frame and panel letters present when there are panels; nothing touches the outer frame (≥ 3 pt inside).
