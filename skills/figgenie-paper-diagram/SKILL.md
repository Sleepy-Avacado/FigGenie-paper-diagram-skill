---
name: figgenie-paper-diagram
description: >
  Draw publication-quality system architecture / overview figures as SVG for systems-conference papers
  (OSDI, NSDI, SOSP, ASPLOS style), distilled from 727 human-rated figures: intake → a natural-language
  brief the user confirms → figure spec → drawing plan → hand-drawn SVG that follows corpus layout
  templates, palettes, visual encodings and a parts library → render / lint / look-and-fix loop → SVG +
  caption draft, then iterate on feedback. Use whenever the user wants an architecture, overview, system,
  design or deployment figure for a paper or talk ("架构图", "系统总览图", "画一张 overview 图", "论文插图",
  "把这张图重画/改风格"), asks how such a figure should be laid out, coloured or annotated, or wants an
  existing architecture figure critiqued against top-venue conventions, or drawn in a named paper style the user
  asks for ("Charon 风格": ink-outlined pastel boxes, bold labels, framed panels). Figures that need the paper's own
  symbols get vector TeX formulas rendered into the SVG (only when needed); on request a finished figure is
  also exported as an editable PowerPoint deck ("转成可编辑的 PPT", native shapes and equations). Also draws
  **mechanism figures** — how one part of a system works: a walkthrough with numbered steps, before/after or
  step-by-step frames, a state machine or decision flow, alternatives side by side, the anatomy of one component
  or data structure, a worked example with real values ("机制图", "原理图", "示意图", "画一张 X 是怎么工作的图",
  "状态机 / 流程图", "before/after 对比图", "算例图"), distilled from 986 rated mechanism figures and 152 semantic
  records. Not for data plots or charts.
---

# figgenie-paper-diagram (FigGenie-Skill) — architecture and mechanism figures the way top systems papers draw them

You draw the SVG yourself. The scripts do not lay out for you; they measure text, render, lint and show you
the result so you can fix it. Everything is in **pt at print size**: a single-column figure is ≈ 240 pt wide,
a double-column one ≈ 504 pt, labels 6.5–7 pt, strokes ≈ 0.6 pt. Read the corpus numbers, then draw like the
exemplars, not like a slide.

**Reference, not recipe.** The corpus numbers, the templates, the exemplars and the parts library exist to
strengthen a layout you derive from the figure's own content — what it must make the reader see — never to
replace that derivation. When the material asks for something the references do not cover, draw it, and say
so in the plan. This matters most for mechanism figures, where no two good figures share a layout.

Two figure kinds share this workflow: **architecture** (the whole system, `meta.kind: architecture`, 20 layout
templates) and **mechanism** (how one part works, `meta.kind: mechanism`). Decide the kind while writing the
brief; the steps below are written for architecture figures, and everything a mechanism figure does differently
is collected in one section after the workflow — a menu with corpus frequencies, not a second rulebook.

## Workflow (gates in bold)

Work in a folder per figure: `brief.md`, `spec.json`, `plan.md`, `fig.svg`, and the outputs of `check.py`.

1. **Intake → brief.** Read what the user gave (paper sections, notes, an old figure, chat). Write the brief
   (`references/brief-template.md`): what the figure is, every component with new / existing / external tags
   and its container, the numbered main path and secondary flows, the one point the figure argues, layout and
   style intent with the closest exemplar ids (search them by domain and content as in step 3), 3–5 assumptions to confirm with their source, a caption draft.
   Infer first; ask only what changes the structure and cannot be read from the material (usually "which parts
   are new" and "which path is the main one"), at most three points in one message, each phrased as your guess
   plus the alternative (`references/spec-guide.md` §1). **Gate: the user confirms the brief.**
2. **Spec.** Derive `spec.json` from the confirmed brief (`references/spec-guide.md` §2–3, schema
   `references/spec-schema.json`). The three specs in `assets/specs/examples/` show how a filled-in spec is written
   and nothing else: take layout, colour and density from the exemplar library in step 3, never from them. Run
   `python3 scripts/spec_validate.py spec.json` and fix errors; read the warnings as advice. The spec is a
   contract for the linter, not a cage: `notes` and `x-*` fields are allowed everywhere, kinds have `other`,
   templates have `custom`.
3. **Template, exemplars, palette, encoding.** Pick the template with the decision table in
   `references/layouts.md` ("Choosing a template", then the one template section you need; 20 ids: 7 core +
   13 added). Then look at exemplars along two lines, because the template says how the corpus arranges a
   figure and the content says how this field draws its objects:
   - **by template**: two or three from `assets/exemplars/<template>/index.json` (starred = must-see, each with
     a one-line lesson);
   - **by domain, content and meaning**: `python3 scripts/find_exemplars.py --domain "<field, kind of system>"
     --content "<what is drawn: components, structures, objects>" --semantics "<the point the figure argues>"`
     with the words of the brief ranks all 485 exemplars of both kinds; open the top three to five whose systems
     resemble yours, whatever their template. This is where a field's habits come from — how LLM-serving papers
     draw KV blocks and instance pools, how storage papers draw tiers, how a quota service draws its buckets.
     Usually five to eight figures in all. When the matches are only generic words, the corpus has nothing from
     this field: say so in the plan and lean on the template exemplars.

   LOOK at each `assets/exemplars/figures/<id>/print.png` (or `preview.png`) and skim `semantics.json`; imitate
   their arrangement, density and restraint, and borrow the devices that make your content visible. Choose a palette from
   `references/palettes.json` (one accent, grey for existing parts, white canvas). The 20 templates are the
   arrangements the corpus uses most, not moulds: when the system's structure is something else, `custom` with a
   `notes` line is the right answer, and an exemplar is imitated for its restraint and density, not copied. Take the default encodings
   from `references/encoding.md` Part D (solid = data, dashed = one meaning per figure, thick = main path,
   circled numbers = the walkthrough, `×N` for repetition, red only for errors / bottlenecks).

   **Named style** — only when the user asks for one paper's look (today: `charon`, see
   `references/styles/README.md`): set `meta.style`, `meta.palette` and `meta.font` as its card says, read the
   card (`references/styles/<id>.md`) before the plan, and add two or three of its figures to the exemplars
   (`find_exemplars.py --style <id> …` lists them first). The style replaces weight, outlines, fill roles and
   framing; the template, the content search and every print floor (type ≥ 6 pt included) stay as above.
4. **Drawing plan.** Write `plan.md` (`references/drawing-plan.md`): canvas and grid, regions, per-node
   placement and size, routes, emphasis, legend, and a 4–6 item check list for the PNG. Size boxes from
   measured labels: `python3 scripts/measure_text.py --font <key> --size 7 "Label" …` (CJK runs are measured with the
   companion `--cjk` key; `--box` prints the box size; width + 8 pt,
   1.4 × size per line + 6 pt). Place labels with `python3 scripts/place_text.py --font <key> --size 6.5 center --box
   x,y,w,h [--rotate -90] "Label"` (baseline from the font, the linter's own centring model; `line` for text with an
   inline ① disc). If the plan does not fit at these numbers, the content is too much — go back to
   the brief and merge or split; never shrink type below 6 pt. Formulas, only when the figure carries the paper's
   symbols: measure them the same way with `python3 scripts/tex_measure.py --size 6.5 --box '<tex>'` (`--mixed '… $tex$ …'
   --emit` lays out a label with inline formulas and prints the elements to paste); see `references/formulas.md`.
5. **Draw the SVG** under the contract (`references/spec-guide.md` §4): `viewBox="0 0 W H"` in pt, the font
   stack from `assets/fonts/fonts.json` on the root, one `<g id="n:<id>" data-kind="node">` per node (shape +
   `<text>`), `e:` for edges (with `data-from`/`data-to`, `marker-end`), `c:` containers, `l:` lanes, `s:` step
   badges, `a:` annotations, `legend`. Text stays `<text>`; a formula is the one exception — a `<g data-symbol="tex" data-tex="…" data-x data-y data-size data-anchor/>`
   placeholder that `tex_fill.py` renders to paths (`references/formulas.md`); no gradients, filters or external refs.
   Mark a group drawn to scale from numbers (bars, Gantt rows) `data-scale="data"` and a label set beside its box on
   purpose `data-label="outside"` (spec-guide §4): the linter then stops asking you to snap data or centre that label.
   A bitmap — a sample input or output, a photo, a screenshot, a rendered result, an icon — is an `<image>` in its
   node's group: a PNG / JPEG in the figure folder linked by a relative path, never a URL (`references/spec-guide.md`
   §4 "Bitmaps").
   Reuse parts from `assets/symbols/` (`index.json`, `catalog-*.png`) by copying the inner `<g>` and recolouring
   by role — the library is a reference, not a limit: draw whatever the figure needs in the same line weight.
   Default strokes, arrowheads, containers, badges and legends: `references/parts-styles.md` §8.
6. **Self-check loop.** If the figure has formula placeholders, first `python3 scripts/tex_fill.py fig.svg --check`
   (renders them; reports formulas that leave their box or collide with labels; re-run after editing any `data-tex`).
   Then `python3 scripts/check.py fig.svg --spec spec.json` → validates, lints, renders
   `fig.png` and `fig.lint.png`, writes `fig.preview.html`. Then LOOK at `fig.png` with your image-viewing tool (Read in Claude Code, view_image in Codex) and go
   through `plan.md`'s check list and `references/anti-patterns.md` §3: overlaps, crossings, bleed, alignment,
   the accent being the loudest thing, labels readable at 100 %, arrows that mean what the brief says, arrowheads
   and tails clear of tier dividers, ×N stacks stepped evenly, container titles centred between the top edge and the
   first box, rotated gutter labels centred in their gutter (the linter checks these too). Fix the
   SVG (or the spec/plan if the layout was wrong) and re-run until the lint has 0 errors and every remaining
   warning is deliberate. Use `scripts/render.py --scale 6 --crop x0,y0,x1,y1` to zoom into a doubtful region,
   `scripts/svg_edit.py shift … --with-edges` to move a group and the edges that touch it, and `fig.preview.html`
   when you need exact coordinates.
7. **Deliver.** `python3 scripts/embed_fonts.py fig.svg -o fig.final.svg` (fonts embedded, subsetted; CJK companion
   included and glyph coverage reported; every bitmap inlined as a data URI the same way, so the file stands alone —
   it refuses while an image is a URL, missing, or not PNG / JPEG) and `python3 scripts/export_pdf.py fig.final.svg`
   for LaTeX/Pages. Hand over: the final SVG, the PDF, the PNG preview, the caption draft, the assumption list from
   the brief, and one line on how to edit (element ids match the spec). **Gate: the user reviews.**
8. **Iterate.** Content feedback → brief → spec → redraw; layout / style feedback → spec (`spec-guide.md` §5)
   → redraw; always re-run `check.py` and look again. Keep brief, spec, plan and SVG in sync.

## Mechanism figures (kind 2): what changes, step by step

Mechanism figures vary far more than architecture figures: the 152 good ones in the corpus fall into five
groups, but almost no two share a layout. So this section is deliberately loose. **The groups, arrangements,
default encodings and numbers below are what good figures did, with how often — they are a starting point,
not a template to fill.** When the figure's story needs something else, do it, and write the reason in the
plan and in the spec's `notes` so the reviewer sees a choice rather than an accident. Only print physics is
fixed: column width, type ≥ 6 pt, contrast, nothing outside the canvas. **To be explicit: the exemplars, the
five group plans, the arrangements and the parts are reference and reinforcement — the drawing itself is
decided by what this particular mechanism has to show the reader.** A good mechanism figure that looks like
none of the 146 exemplars is the expected outcome, not a failure.

- **Deciding the kind (step 1).** Whole-system overview → architecture. What happens inside one component, one
  data structure, one exchange, one decision, or how alternatives differ → mechanism. Both → the one the caption
  leads with; the other becomes an inset or a second figure (`references/spec-guide.md` §7). One overview figure
  that the user wants to hold unlike drawings (a structure, numbers to scale, a timeline, a loop) → a composite:
  its panels are parts (`axis: part`), each budgeted on its own (`references/spec-guide.md` §8).
- **Brief (step 1).** Same seven sections, three of them read differently (`references/brief-template.md`,
  "Mechanism figures"): §2 names the structure(s) that will be drawn and what is repeated versus what differs;
  §3 narrates the story the reader follows — steps along a path, transitions and their guards, before → after
  deltas, or the values of a worked example; §4 says what the reader must *see* in five seconds: the
  difference, the order, the state, the shape. Answer "which group?" last, and "none exactly" is an acceptable
  answer if the reading path is clear.
- **Spec (step 2).** `meta.kind: mechanism`, `meta.template: mechanism`, `meta.mechanism` with the group (as a
  reference point, secondary `groups` allowed), `base`, `arrangement` (`other` is a value), plus the blocks the
  story needs: `panels[]` + `deltas[]` for alternatives and frames, `steps[]` for a walkthrough, `state` /
  `decision` nodes with guarded `transition` edges for logic, `values[]` for a worked example — spec-guide §7 maps
  each group to its blocks. `spec_validate.py` only *warns* about mechanism structure; every warning is advice.
- **Group, base, arrangement, exemplars, encoding (step 3).** `references/mechanism/layouts.md` "Choosing the
  group, the base, the arrangement" (five questions, then one group section: drawing plan, numbers, variants
  with figure ids, pitfalls, and "Inventing an arrangement" when nothing fits). Open two or three starred
  exemplars of the group (`assets/exemplars/mechanism/<group>/index.json`), and three to five found by domain,
  content and meaning (`scripts/find_exemplars.py ... --kind mechanism --group <group>`, as in step 3 above: the
  structure being explained, its field, the difference or order the reader must see); LOOK at each
  `assets/exemplars/figures/<id>/print.png`. Read the exemplars to sharpen your own plan, not to pick one to reproduce — the group section's variants
  and pitfalls are there to widen the options, and `group: other` exists for a figure that is none of the five.
  Encoding defaults and when to leave them:
  `references/mechanism/encoding.md` Part E (one table: device, corpus share, deviate when). Palette: the same 21
  (`palettes.md` "Mechanism figures"): most mechanism figures draw on a bare canvas, colour says *state*
  (wrong / old / current / new) rather than *component kind* — with a legend once there are more than two.
- **Plan (step 4).** Three extra paragraphs (`references/drawing-plan.md` "Mechanism figures"): what repeats and
  where (the template, panel or frame count, identical positions), what differs and how it is marked (one
  marking style per figure), and the reading path (markers, arrows, panel order, how the caption walks it).
  Budgets by column: `references/mechanism/style-rules.md` §12 and the mechanism budgets in `spec_validate.py`
  (label-distinct: a structure repeated in every panel counts once).
- **Draw (step 5).** Contract additions from spec-guide §7: `p:<id>` groups per panel, `data-panel` + `@<panel>` id
  suffix for repeated template elements, `data-delta` on the changed element, `v:<id>` for values. Parts: the 2,261
  mechanism parts by theme (`assets/symbols/catalog-mech-<theme>.png`, `index.json` families) — ghosts, strikes,
  verdict glyphs, frame chevrons, lifelines, slot rows; `references/parts-styles.md` §9.
- **Check (step 6).** `check.py` as usual; then the self-check questions in `references/mechanism/anti-patterns.md`
  §6 (can a reader find the difference / the order / the state without the caption? is every branch labelled? is
  the changed thing the loudest thing? does anything need reading below 6 pt?), and its §1–§4 when something
  feels off. Mechanism lint rules are advisory (warn / info), never a gate.

## Optional add-on after delivery: an editable PowerPoint copy

Only when the user asks for a deck, or an editable / Word-native version of the figure. `python3 scripts/svg2pptx.py
fig.final.svg --spec spec.json` writes `fig.final.pptx`: one native shape per primitive at the same coordinates, one named
group per spec element, formulas as native equations, bitmaps as pictures, paint order as in the SVG; `python3 scripts/pptx_check.py
fig.final.pptx --svg fig.final.svg` confirms nothing was dropped or covered. Font mapping, what maps to what and the limits:
`references/pptx-export.md`. It never overwrites an existing deck (hand edits) without `--force`. The drawing workflow
above does not depend on it.

## Reading map (load only what the step needs)

| when | read | lines |
|---|---|---|
| writing the brief / asking | `references/brief-template.md`; `references/spec-guide.md` §1–2 | 70 / 100 |
| writing the spec | `references/spec-guide.md` §3–6; `references/spec-schema.json` on demand; `assets/specs/examples/*.json` for spec syntax only (style comes from `assets/exemplars/`) | 120 |
| choosing the template | `references/layouts.md` "Choosing a template" + "Cross-template conventions" (lines 1434–1535), then one template section | ~120 |
| colours | `references/palettes.md` (roles, the 11 hue families + 10 ground families, what not to do) and the matching entry in `palettes.json` | 161 |
| a composite figure (several kinds of drawing in one figure); what to cut when it does not fit | `references/spec-guide.md` §8 | 45 |
| placing a label exactly (centred, turned up a bar, with an inline ① disc); data drawn to scale; a label beside its box | `scripts/place_text.py`; `references/spec-guide.md` §4 "Placing labels, drawing to scale" | 15 |
| a named style the user asked for (`meta.style`, e.g. `charon`) | `references/styles/README.md`, then the card `references/styles/<id>.md`; its figures in `assets/exemplars/styles/<id>/` | 40 + 150 |
| deciding the kind; a mechanism brief / spec | `references/spec-guide.md` §7 (`meta.kind = mechanism`: groups, panels / deltas / values, SVG contract additions); `references/brief-template.md` "Mechanism figures" | 50 + 40 |
| mechanism: group, base, arrangement | `references/mechanism/layouts.md` "How to read this" + "Choosing the group, the base, the arrangement", then one group section (or "Inventing an arrangement") | 130 + ~100 |
| mechanism: what marks a difference / a step / a state | `references/mechanism/encoding.md` Part E table first (defaults + when to deviate), then the part the figure needs (A states, B markers, C colour / lines / shapes, D worked values) | 60–200 |
| mechanism: numbers while drawing | `references/mechanism/style-rules.md` §12 + its quick checklist; `references/drawing-plan.md` "Mechanism figures" | 80 |
| mechanism: before declaring done | `references/mechanism/anti-patterns.md` §6 self-check, §3 print legibility; §1–2 when a figure feels off | 40–300 |
| what dashed / bold / ①② mean | `references/encoding.md` Part D (default table, line 441); Part B for emphasis | 50–100 |
| numbers while drawing | `references/style-rules.md` "Quick checklist" + "Figure size table" (lines 375–457); `references/parts-styles.md` §8 defaults | 100 |
| before declaring done | `references/anti-patterns.md` §3 linter checklist; §1–2 when a figure feels off | 40–400 |
| formulas in the figure (only when it needs them) | `references/formulas.md`; `scripts/tex_measure.py`, `scripts/tex_fill.py` | 90 |
| a bitmap in the figure (sample, photo, screenshot, rendered result, icon) | `references/spec-guide.md` §4 "Bitmaps"; `references/encoding.md` A13 | 30 |
| an editable PowerPoint copy (optional, after delivery) | `references/pptx-export.md`; `scripts/svg2pptx.py`, `scripts/pptx_check.py` | 80 |
| parts | `assets/symbols/README.md`, `index.json` (search by name / tags / depicts; mechanism parts also by `family`, `theme`, `figure_kinds`, filter `subtype`), `catalog-icon|motif|shape.png` (architecture parts), `catalog-mech-<theme>.png` (mechanism parts by theme) | — |
| exemplars | `assets/exemplars/<template>/index.json` (architecture) or `assets/exemplars/mechanism/<group>/index.json` (mechanism), starred first with one-line lessons; `scripts/find_exemplars.py` searches all of them by domain, content and meaning; per figure `assets/exemplars/figures/<id>/` with `print.png`, `preview.png` (author render, when present), `source.svg`, `semantics.json`, `manifest.json` (`kind` says which). Reference and reinforcement only: borrow the device that serves your figure, never the layout wholesale | — |

## Rules that are not negotiable

- Units and canvas: pt, `viewBox="0 0 W H"`, W in the column band (single 210–309, target 240; double
  430–603, target 504); height ≈ 130–180 pt; nothing outside the canvas.
- Type: one sans family (key from `fonts.json`, default `helvetica` = TeX Gyre Heros; `arial`, `calibri`,
  `times`, `computer-modern` when matching a paper), ≤ 3 sizes, labels 6.5–7 pt, nothing below 6 pt except
  badge digits. Labels are the paper's own terms. Chinese (or any CJK) labels: Latin family first, the CJK
  companion second (`meta.font_cjk`, default `source-han-sans` = 思源黑体 with `source-sans`); never a glyph that no
  embedded face has (draw ⋮ as dots, arrows as markers) — `font.glyph` in the lint catches it.
- Colour: white canvas; ≤ 2 saturated fills, exactly one accent role; grey / pale fills for existing parts;
  red only for errors, bottlenecks or the highlighted path; text contrast readable (white text on dark accents).
- Lines: every directed edge has a head; dashed carries one meaning per figure; the main path is the heaviest
  line; orthogonal routes for structure, curves only for feedback; no line through a label.
- Structure: ≤ 3 nesting levels; containers never filled darker than their children; equal gaps in a row;
  edges of boxes snapped (the linter flags 0.3–2 pt misalignment); a legend when more than four fills, line
  styles or icons carry meaning; `×N` or an ellipsis instead of drawing N copies.
- Content: nothing the brief does not contain; every spec element appears in the SVG with its id; new
  components visibly distinct from existing ones; the walkthrough numbers match the caption.
- Bitmaps (a sample, a photo, a screenshot, a rendered result, an icon — wherever the figure needs one): PNG or JPEG
  from a local file, never a URL; inlined into the SVG at delivery like the fonts; ≥ 150 ppi at print size (300 for
  photos), drawn at its own aspect ratio.
- Never: gradients, 3D, drop shadows, rainbow categorical fills, a different shape per box,
  text converted to paths (formulas rendered by `tex_fill.py` inside `<g data-symbol="tex">` with their TeX kept are the
  exception), decisions taken silently (they go to the brief's assumptions / `meta.open_questions`).
- Mechanism figures: the print rules above (units and canvas, type, contrast, arrowheads, no line through a
  label, nothing invented) hold as written. The colour and structure rules bend where the story needs it: state
  colours may add a third and fourth hue (with a legend), the same structure is drawn once per panel, the accent
  is the *difference* rather than the new component, nesting follows the drawn base. Say in the plan which rule
  you bent and why.

## Numbers to keep in your head

From the 727 good architecture figures the references were distilled over (the corpus now holds 726;
details and evidence in `references/style-rules.md` and `layouts.md`):
median 11 components and 6 flows; 6 distinct fills, 1 saturated; label 6.5 pt; stroke 0.56 pt with 2 widths;
73 % have no legend (but matrix 42 %, host-device 38 % and control-data 36 % do); 35 % number their steps
(54 % of request-path figures, 4 % of deployments); pipeline is left-right 66 % of the time, layered is
top-down 79 %; double-column figures are twice as wide but not taller (aspect ≈ 3.1).

Mechanism figures, from the 152 semantic records (exemplar candidates — good figures a labeller picked, not
the population; `references/mechanism/layouts.md` "How to read this"): median 10 elements and 6 relations;
45 % are one drawing, 25 % a row of panels, 9 % a grid, 9 % a column; panels median 3; 82 % single column;
70 % have no legend; 61 % have no step markers (circled numbers 20 %, plain digits 7 %, letters 7 %); a
difference is marked by colour 53 %, callout 11 %, badge 7 %, not at all 26 %; 33 % are worked examples with
real values; 55 % have no container fill at all; 85 % of logic transitions carry a guard.

## Files

- `references/` — the distilled knowledge (all numbers come from the corpus; each file says how it was derived).
- `assets/exemplars/` — 485 published figures: 339 architecture figures filling 486 slots across the 20
  templates, and 146 mechanism figures filling 175 slots across the 5 groups (`mechanism/<group>/index.json`),
  chosen from the corpus and reviewed by hand; each figure stored once under `figures/<id>/` (author SVG, or the
  PDF-extracted SVG with text kept as text; print PNG; semantics; manifest with `kind`) and listed in its
  `index.json` with a one-line lesson: style reference only — to strengthen a layout derived from the figure's own
  needs, not to be reproduced; provenance in each `manifest.json`.
- `assets/symbols/` — 2,853 parts, standalone SVGs in pt with `data-symbol`: 592 for architecture figures
  (icons, motifs, shapes; 503 cut from corpus figures, 89 original line-art) and 2,261 for mechanism figures
  (`subtype: mechanism` in `index.json`; icons, motifs, shapes and `device` narrative devices cut from 705
  mechanism figures, grouped into 155 families under 11 themes); browse the catalog PNGs.
- `references/styles/` + `assets/exemplars/styles/` — named styles: one paper's look the user asked to reuse
  (`charon`: card, lint / validator JSON, palette, 7 exemplar figures). Used only when `meta.style` names one.
- `assets/palettes/` — swatch cards for the 21 corpus palettes + 1 named-style palette (11 hue families + 10 ground families: outline-only or tinted containers); `assets/fonts/` — open fonts + `fonts.json` map.
- `assets/specs/examples/` — four specs reverse-engineered from corpus exemplars (`asplos25-100_fig5`,
  `asplos25-167_fig1`, `asplos26-132_fig6`; `asplos25-006_fig1` is the mechanism one: a comparison with panels
  and deltas), kept only as examples of how a spec is written. For style, use the
  exemplar library, not these specs: each spec's `_source` points at the figure it was written from in
  `assets/exemplars/figures/`.
- `scripts/` — `find_exemplars.py`, `spec_validate.py`, `measure_text.py`, `place_text.py`, `render.py`, `lint.py`, `embed_fonts.py`, `export_pdf.py`,
  `svg_edit.py`, `preview.py`, `check.py` (see `scripts/README.md`); `scripts/distill/` re-derives the references from the corpus.
  Formulas: `tex_measure.py`, `tex_fill.py` (MathJax in `scripts/mathjax/`); PowerPoint export: `svg2pptx.py`, `pptx_check.py`.

Requirements: python3 with lxml, Pillow, playwright (`playwright install chromium`); `fontTools` optional. Optional:
`node` ≥ 18 for formulas (`scripts/mathjax`, `npm install` on first use); `python-pptx` and Microsoft Office's
`mathml2omml.xsl` for the PowerPoint export.
