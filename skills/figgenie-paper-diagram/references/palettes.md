# Palettes for systems-conference architecture diagrams

The eleven families were distilled from the **272** architecture figures that had author
sources (`type=diagram`, `subtype=architecture`; OSDI/NSDI/SOSP/ASPLOS 2023-2026); every
corpus-wide number below was refreshed on 2026-09-07 over all **727** good architecture figures,
covering **3,398** recorded palette entries and **1,162** distinct hexes. Machine-readable form: `palettes.json`.
Ten **ground families** were added on 2026-09-18 (see [The 10 ground families](#the-10-ground-families-added-2026-09-18)):
the first clustering keyed on the hue of the boxes and gave every family a grey container hex, although
in the corpus a grey ground is the minority — of the 726 good figures with records, 356 draw their
containers as **outlines only**, 41 have no containers, 161 fill them grey, 109 use one tint and 52
tint each region differently. Swatch cards: [`../assets/palettes/`](../assets/palettes/README.md). Regenerate with

```
python3 scripts/distill/palette_cluster.py --semantics lab/extracted/corpus_semantics.jsonl \
    --index lab/extracted/corpus_index.csv --out <scratch> --palettes-out references/palettes.json
python3 scripts/distill/palette_grounds.py --semantics lab/extracted/corpus_semantics.jsonl \
    --index lab/extracted/corpus_index.csv --out <scratch> --append-to references/palettes.json
python3 scripts/distill/make_swatches.py
```

## Roles

| role | meaning |
| --- | --- |
| `canvas` | Page background. `#ffffff` in **727/727** figures - never tint it. |
| `container` | Outer group / region box fill (a host, a plane, a subsystem). |
| `lane` | Swimlane or band fill (a phase, a tier, a timeline row). |
| `module` | Default component-box fill: the colour most boxes get. |
| `module-alt` | 2nd/3rd component fills, for a different *kind* of component. |
| `accent` | Fill marking the novel component or the main path. 1 per figure, 2 at most. |
| `stroke` | Box outlines. Near-neutral, dark, 0.5-1pt. |
| `text` | Primary label text. Near-black. |
| `text-muted` | Annotations, units, greyed-out labels. |
| `arrow` | Default connector, usually the same neutral as `stroke`. |
| `arrow-accent` | Highlighted connector: request path, error path, new flow. |
| `legend` | Legend box background when the legend sits inside the figure. |

## The 11 hue families

| id | look | when to use | n (share) | exemplars |
| --- | --- | --- | --- | --- |
| [`blue-orange`](../assets/palettes/blue-orange.svg) | Light-blue boxes on light grey, one orange accent | Default whole-system overview with one obvious novel component | 36 (13.2%) | `asplos26-127_fig3`, `sosp25-053_fig4`, `asplos25-157_fig2` |
| [`green-red`](../assets/palettes/green-red.svg) | Pale-green boxes, red reserved for the highlighted/error path | Pipelines and stacks where one path must jump out | 34 (12.5%) | `nsdi26-087_fig3`, `asplos26-129_fig3`, `asplos25-138_fig17` |
| [`high-contrast`](../assets/palettes/high-contrast.svg) | Near-white boxes, heavy near-black outlines, saturated primaries | Small single-column / TikZ figures printed small | 28 (10.3%) | `osdi25-012_fig3`, `asplos25-096_fig1`, `sosp24-007_figtex6` |
| [`cream-pastel`](../assets/palettes/cream-pastel.svg) | Peach/cream default box, pale blue and green alternates, grey containers | Dense figures, many small boxes of several kinds, none may shout | 27 (9.9%) | `asplos26-077_fig3`, `asplos25-100_fig3`, `nsdi23-085_fig8` |
| [`grey-scaffold`](../assets/palettes/grey-scaffold.svg) | Grey is the default box, tints only where it matters | Reusing an existing system: grey = unchanged, tint = the paper's addition | 27 (9.9%) | `asplos25-039_fig3`, `nsdi24-023_fig3`, `asplos26-129_fig5` |
| [`greyscale`](../assets/palettes/greyscale.svg) | No hue at all; near-white boxes, black outlines, mid-grey container | Print-first venues, B/W-safe figures, structure over kind | 27 (9.9%) | `asplos25-031_fig1`, `sosp23-013_fig3`, `sosp24-040_fig1` |
| [`blue-mono`](../assets/palettes/blue-mono.svg) | One blue family end to end, strong Office blue accent and arrows | Hardware / micro-architecture; colour carries depth, not category | 23 (8.5%) | `sosp23-026_fig3`, `asplos26-076_fig2`, `osdi26-018_fig7` |
| [`warm-bands`](../assets/palettes/warm-bands.svg) | Cream/peach/pale-green bands name the phases, boxes inside stay pale | Layered or two-plane figures where the *regions* are the message | 22 (8.1%) | `sosp23-016_fig4`, `sosp24-041_figtex8`, `osdi26-024_fig8` |
| [`multi-hue-categorical`](../assets/palettes/multi-hue-categorical.svg) | 4-6 distinct hues as categories + crimson accent + legend | Colour *is* the data: traffic classes, tenants, heterogeneous engines | 18 (6.6%) | `asplos26-141_fig2`, `asplos25-110_fig2`, `asplos26-094_fig9` |
| [`amber-highlight`](../assets/palettes/amber-highlight.svg) | Neutral grey lanes, peach/white boxes, one dark gold-amber block | Before/after and baseline-vs-ours: one amber block carries the claim | 16 (5.9%) | `asplos26-019_fig1`, `asplos25-082_fig1`, `nsdi25-062_fig7` |
| [`cool-grey-cyan`](../assets/palettes/cool-grey-cyan.svg) | Cool grey containers, pale cyan boxes with a warm tan counterpart | Orchestration / control-plane figures wanting a quieter cool look | 12 (4.4%) | `asplos26-036_fig8`, `nsdi26-127_fig6`, `asplos26-008_fig3` |

Totals: family sizes are from the 272-figure clustering that produced them (270 assigned, 2 empty
palettes). A re-clustering over all 727 figures (2026-09-07, k = 14, sizes 104 / 89 / 75 / 69 / 62 /
62 / 58 / 48 / 43 / 27 / 25 / 23 / 21 / 12; 9 records carry an empty `style.palette`) reproduced the
same families - warm-yellow, blue with a warm accent, grey scaffold, greyscale, blue-mono,
green-with-red, pale pastel, amber, red categorical, cyan, teal, grey-red high-contrast and a
small purple group - so the eleven ids were kept unchanged rather than renamed. Full role hexes, per-palette tool/venue/abstraction counts and
5 exemplars each are in `palettes.json`.

### Role hexes at a glance

| id | container | module | module-alt | accent | stroke | text | arrow-accent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `blue-orange` | `#f2f2f2` | `#dae8fc` | `#fff2cc` `#e2f0d9` `#f8cecc` | `#ed7d31` | `#36393d` | `#0d0d0d` | `#c00000` |
| `green-red` | `#ededed` | `#d8f3dc` | `#dae8fc` `#fff2cc` `#f8cecc` | `#ff0000` | `#262626` | `#191919` | `#ff0000` |
| `high-contrast` | `#d9d9d9` | `#f2f2f2` | `#0000ff` `#ffffbf` `#ff0000` | `#c00000` | `#191919` | `#191919` | `#c00000` |
| `cream-pastel` | `#d9d9d9` | `#fbe5d6` | `#dae8fc` `#d5e8d4` `#f8cecc` | `#ffc000` | `#4f4f4f` | `#333333` | `#ff0000` |
| `grey-scaffold` | `#f2f2f2` | `#d9d9d9` | `#fff2cc` `#dae8fc` `#f8cecc` | `#ed7d31` | `#231f20` | `#221815` | `#c00000` |
| `greyscale` | `#d9d9d9` | `#f2f2f2` | `#bfbfbf` `#cccccc` | `#666666` | `#000000` | `#000000` | `#ff0000` |
| `blue-mono` | `#f2f2f2` | `#deebf7` | `#ffffbf` `#c5e0b4` `#d65b47` | `#4472c4` | `#7f7f7f` | `#333333` | `#4472c4` |
| `warm-bands` | `#fff2cc` | `#e2f0d9` | `#fbe5d6` `#deebf7` `#ffbebd` | `#f0a30a` | `#231916` | `#231916` | `#c00000` |
| `multi-hue-categorical` | `#dae3f5` | `#d5e8d4` | `#f8cecc` `#fff2cc` `#b9d2b6` | `#b1001c` | `#231f20` | `#231f20` | `#c00000` |
| `amber-highlight` | `#d9d9d9` | `#ffeed9` | `#a7c0de` `#d3e2b7` `#ff7d94` | `#cc9600` | `#2c2c2e` | `#2c2c2e` | `#ff0000` |
| `cool-grey-cyan` | `#f2f2f2` | `#c5e5e5` | `#f4b183` `#bcbddc` `#db6965` | `#117788` | `#262626` | `#262626` | `#c00000` |

## The 10 ground families (added 2026-09-18)

Same roles, same corpus, one difference: the **ground**. `container` (and `lane`) is **`null` in the six
`*-outline` families**, meaning the group box gets **no fill at all** — a 0.5–0.75 pt outline on the white page,
solid for a physical enclosure and dashed for a logical one (encoding.md §A10), with the title inside its top-left
corner. That is how 356/726 good figures draw their containers, and dashed strokes are just as common there
(63% of those figures use one somewhere) as under a grey slab (60%). The four tinted families fill the container
with a colour instead of grey: one pale tint for the dominant region, or (`pastel-regions`) a different pale tint
per region, listed in `region_tints`. Each `*-outline` family is the transparent twin of a hue family above —
same boxes and accent, no grey ground — so choose the hue family first, then decide the ground.

| id | look | when to use | n (share of 726) | exemplars |
| --- | --- | --- | --- | --- |
| [`blue-outline`](../assets/palettes/blue-outline.svg) | Light-blue boxes, blue or orange accent, containers as outlines on white | Nested blue figures where stacked grey slabs would go muddy | 97 (13.4%) | `osdi26-094_fig1`, `osdi24-032_fig9`, `nsdi24-033_fig1` |
| [`ink-outline`](../assets/palettes/ink-outline.svg) | Near-white boxes, black outlines, one saturated fill, outline containers | Small single-column / TikZ-like figures printed small | 90 (12.4%) | `nsdi26-091_fig4`, `sosp25-007_fig2`, `asplos26-008_fig1` |
| [`pastel-outline`](../assets/palettes/pastel-outline.svg) | Cream/peach boxes with pastel alternates, amber accent, outline containers | Several kinds of boxes when the regions should not add another fill | 87 (12.0%) | `asplos26-026_fig6`, `asplos26-080_fig5`, `asplos25-100_fig3` |
| [`pastel-regions`](../assets/palettes/pastel-regions.svg) | Each region its own pale tint (cream, green, blue, pink), pale-blue boxes | The split into regions is the message and a region legend is unwanted | 52 (7.2%) | `nsdi26-144_fig1`, `nsdi24-022_fig1`, `nsdi26-124_fig1` |
| [`green-outline`](../assets/palettes/green-outline.svg) | Pale-green boxes, red reserved for the highlighted path, outline containers | Pipelines / stacks with one path to jump out, dashed host or trust boundaries | 45 (6.2%) | `osdi23-011_fig5`, `nsdi24-107_fig5`, `nsdi25-054_fig2` |
| [`blue-ground`](../assets/palettes/blue-ground.svg) | Pale-blue ground behind cream/orange boxes, crimson accent | One dominant region that must read as a unit | 45 (6.2%) | `asplos26-096_fig6`, `nsdi24-064_fig3`, `sosp25-002_fig1` |
| [`greyscale-outline`](../assets/palettes/greyscale-outline.svg) | No hue: grey or white boxes, black outlines, outline containers | B/W-safe nested figures where a grey slab would swallow the grey boxes | 44 (6.1%) | `osdi23-032_fig5`, `osdi24-007_fig3`, `osdi23-014_fig4` |
| [`cream-ground`](../assets/palettes/cream-ground.svg) | Cream/peach ground behind pale-blue boxes, amber accent | Warm print-friendly figures with one main region | 26 (3.6%) | `asplos26-153_fig14`, `asplos25-034_fig8`, `sosp25-009_fig6` |
| [`categorical-outline`](../assets/palettes/categorical-outline.svg) | 4–6 categorical hues, crimson accent, outline containers or panel frames | Colour is the data and the figure also has regions | 25 (3.4%) | `asplos25-110_fig1`, `asplos26-127_fig2`, `asplos26-134_fig1` |
| [`green-ground`](../assets/palettes/green-ground.svg) | Pale-green ground behind pale-blue boxes, orange accent | The trusted / secure region of a two-region figure; blue already taken by boxes | 25 (3.4%) | `nsdi26-087_fig3`, `asplos25-097_fig2`, `osdi25-017_fig7` |

Family sizes come from `palette_grounds.py`: the 397 transparent-ground figures were clustered on the same
features as the hue families (Ward, k = 8 by silhouette, fragments under 20 merged); the tinted-ground figures were
grouped by the hue of their ground (pink, teal, yellow and purple grounds were too few for a family of their own).

### Role hexes at a glance (ground families)

| id | container | lane | module | module-alt | accent | stroke | text | arrow-accent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `blue-outline` | — | — | `#dae8fc` | `#fff2cc` `#c5e0b4` `#f8cecc` | `#4472c4` | `#212121` | `#0d0d0d` | `#c00000` |
| `ink-outline` | — | — | `#f2f2f2` | `#fff2cc` `#dae8fc` `#c5e5e5` | `#b1001c` | `#010000` | `#010000` | `#b1001c` |
| `pastel-outline` | — | — | `#fff2cc` | `#dae8fc` `#e2f0d9` `#f8cecc` | `#ffc000` | `#030303` | `#030303` | `#c00000` |
| `pastel-regions` | `#fff2cc` | `#d5e8d4` | `#dae8fc` | `#fff2cc` `#d5e8d4` `#f8cecc` | `#d6b656` | `#0a0a0a` | `#0a0a0a` | `#c00000` |
| `green-outline` | — | — | `#d8f3dc` | `#dae8fc` `#f8cecc` `#fff2cc` | `#ff0000` | `#5e5e5e` | `#2c2c2c` | `#ff0000` |
| `blue-ground` | `#dceaf7` | `#dae8fc` | `#fff2cc` | `#dceaf7` `#82b366` `#fadbdf` | `#c00000` | `#4c4d4c` | `#0d0d0d` | `#6c8ebf` |
| `greyscale-outline` | — | — | `#cccccc` | `#d9d9d9` | `#ff0000` | `#000000` | `#000000` | `#ff0000` |
| `cream-ground` | `#fff2cc` | `#fbe5d6` | `#dae8fc` | `#fbe5d6` `#d5e8d4` `#ff7d94` | `#f0a30a` | `#231916` | `#231916` | `#ffc000` |
| `categorical-outline` | — | — | `#f8cecc` | `#dae8fc` `#ffe6cc` `#d5e8d4` | `#a50040` | `#231f20` | `#231f20` | `#c00000` |
| `green-ground` | `#e2f0d9` | `#d0dfe6` | `#dae3f3` | `#fff2cc` `#97d077` `#b1ddf0` | `#ed7d31` | `#666666` | `#1a1a1a` | `#c00000` |

`—` = no fill (outline only). `pastel-regions` also carries `region_tints`: `#fff2cc`, `#d5e8d4`, `#dae8fc`, `#f8cecc`, `#e1d5e7`.

## Named-style palettes (one paper, not a corpus family)

A named style (`styles/README.md`) brings its own palette, measured from that paper's figures. It is not a
cluster of the corpus, carries no corpus share, and is meant to be used with `meta.style` set to the same id —
its roles only make sense together with the style card's rules (outlines, bold type, text-colour accent).

| id | container | lane | module | module-alt | accent | stroke | text | arrow-accent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `charon` | — | `#fef3eb` | `#cddfff` | `#ffecd6` `#b5d8cb` `#ffc9c3` | `#6bb097` | `#042433` | `#000000` | `#178d6a` |

`charon` also carries `header` (`#d9d9d9`, grey title bars and structure), `identity_fills` (blue / peach /
mint / pink / grey, each with what it named in the paper), `region_tints`, `state_pairs` (solid / pale / line
for green, blue and red, used by mechanism figures for normal vs degraded) and `text_colours` (ours `#178d6a`,
baseline `#c00000`). Its accent is text colour, not a fill: see `styles/charon.md` §3.

## Mechanism figures (kind 2)

The same 21 families serve the mechanism figures. Matching each of the 154 good mechanism figures with a semantic
record to its nearest family by role hexes (module, accent, container, lane, alternates; CIELAB), 42% land within
15 and 81% within 25 of a family; the nearest families are `blue-outline` 22, `ink-outline` 18, `blue-orange` 15,
`pastel-regions` 14, `amber-highlight` 11, `blue-mono` 10, `pastel-outline` 9, `green-outline` 8 — the outline
families first, because the ground is even barer here: **84 of 154 (55%) draw no container at all**, 20 draw
outlines only, 20 use a grey slab, 30 a tint (7 with a different tint per region). A clustering of the mechanism
records alone (`palette_cluster.py --subtype mechanism`) reproduces these families and adds none.

What is different is what colour is *for*. A mechanism figure spends its colour on state, not on component kind
(the `mechanism.state_colours` block of `palettes.json`, from a keyword tally of the records' `used_for` text):

| meaning | records naming it | hue the corpus reaches for | start from |
| --- | --- | --- | --- |
| wrong / failed / removed / stale | 14 | red (11 of 19 uses), else grey | `#b85450`, `#ff7e79`, `#c00000` |
| old / inactive / before / ghost | 28 | grey (22 of 35 uses); dashed outline when the element is gone | `#d9d9d9`, `#cccccc`, `#7f7f7f` |
| current / active / selected / this step | 30 | yellow-amber, blue and red about equally | `#ffc000`, `#ffe699`, `#dae8fc` |
| correct / new / added / ours | 13 | green when a red case is present, otherwise the palette accent | `#70ad47`, `#006633`, `#3399cc` |

These are habits, not rules — mechanism figures vary far more than overviews, so pick the family for the drawn
structure first (`blue-outline` / `ink-outline` for most), then assign at most two state colours from this table
and say what they mean in the caption or a legend (`references/mechanism/encoding.md`).

## What the corpus does (with counts)

**Size of the palette.** Median **4** distinct fills and **5** distinct hexes per figure
(mean 4.2 / 5.0). The distribution of palette-entry counts peaks at 5 (96 figures) and
only 12 figures record more than 8.

**Saturation budget.** Saturated fills (chroma >= 0.40) per figure: **106 figures use
none, 86 use exactly one, 42 use two**; only 14 figures (5%) use four or more. The working
rule is *at most two saturated fills*, everything else pastel or grey.

**Grey does the heavy lifting.** **501/727 (69%)** figures use at least one grey; the
median grey share of a figure's distinct fills is **0.25** (measured `gray_frac` on the
PDF-extracted SVG has median 0.17). **323/727** `encoding.color_means` strings mention
grey, almost always as *existing / unchanged / baseline / off-the-shelf* components -
grey is a semantic choice, not a lack of one.

**One accent, and it means something.** **432/727 (59%)** figures name a colour whose job
is emphasis. Accent hue: warm orange/gold **159**, red **80**, blue **79**, green **41**,
grey **31**, cyan **29**, purple **13**. The most common accent hexes in the whole corpus
are `#ff0000` (17), `#ffc000` (16), `#c00000` (14), `#ed7d31` (11), `#4472c4` (10), `#ffe699`
(9), `#0070c0` (9). For the *accent arrow* the corpus is even more concentrated: `#c00000` (22)
and `#ff0000` (17) are the top two of 338 recorded values.

**Pastel fills with a dark outline.** 234/727 (32%) figures keep the mean lightness of their
coloured fills above L=0.80, and most of the rest are pastel except for the accent. Fill style is
**flat in 655/727 (90%)**, hatch in 60 (8%, mostly TikZ), gradient effectively absent.
Text sits at median lightness **0.36** - near-black, not grey.

**Canonical hexes.** The most-used colours across all 3,398 entries are `#fff2cc` (106),
`#f2f2f2` (81), `#d9d9d9` (65), `#c00000` (62), `#dae8fc` (55), `#4472c4` (54), `#ff0000` (49),
`#e2f0d9` (44), `#cccccc` (44), `#d5e8d4` (41). These are the draw.io and Office/PowerPoint
defaults; only **44/727 (6%)** figures use a strict Microsoft Office theme hex, but the *style*
is everywhere. Tools (where known): PowerPoint 206, OmniGraffle 83, TikZ 39, Quartz/Keynote 45,
draw.io 17, Inkscape 12; 281 figures have no identifiable tool.

**The ground is usually the page itself.** Classifying the 726 good figures with records by what sits behind
their boxes: **356 (49%) draw every container as an outline only** (nesting ≥ 2, no container or
lane fill), 41 (6%) have no containers at all, 7 fill them white, **161 (22%) grey**, 109 (15%) one
pale tint (blue 45, orange/cream 20, green 17, red/pink 10, teal 8, yellow 6, purple 3) and
52 (7%) a different tint per region. Among the figures that do name a container colour the top values
are still the light greys `#f2f2f2`, `#ededed`, `#e7e6e6`, `#d9d9d9` — but that is a quarter of the corpus, not the
default. The ground families above cover the other three quarters.

## What NOT to do

- **Do not exceed two saturated fills.** 71% of the corpus uses zero or one. Four or more
  saturated fills (14 figures) reliably produces a figure where nothing is emphasised.
- **Do not let the accent be the same hue family and lightness as `module`.** 2 of the 11
  families needed their most common recorded accent replaced for exactly this reason
  (`cream-pastel` recorded `#ffe699`, a pale yellow that vanishes on its cream/peach
  boxes; the palette ships `#ffc000` instead). 4 of 11 likewise needed a lighter
  `container` so it separates from `module` - `contrast_notes` names every swap.
- **Do not put dark text on a saturated accent fill.** 45 of the 103 text/module pairs
  recoverable from the corpus fall below WCAG 4.5:1, and 6 of the 11 palettes need a white
  label inside the accent box (`green-red`, `high-contrast`, `greyscale`, `blue-mono`,
  `multi-hue-categorical`, `cool-grey-cyan`). On `#c00000`, `#b1001c`, `#4472c4`,
  `#117788`, `#666666` or `#ff0000`, use `#ffffff` - `contrast_notes` says which.
- **Do not use red and green as the only distinction.** ~8% of male readers cannot
  separate them; the corpus's own `green-red` family always adds a shape, a dash pattern
  or a label. If colour carries meaning, repeat it in the text.
- **Do not put a grey slab behind every group by default.** Outline-only containers are the corpus norm
  (356/726); a filled ground is for one region that must read as a unit (`*-ground`) or for regions that must
  be told apart (`pastel-regions`, `warm-bands`). Nested grey slabs stack into mud — with nesting ≥ 2, use the
  `*-outline` twin of the hue family.
- **Do not tint the canvas.** All 727 figures are on white; a tinted page background
  fights the container fills and does not survive the venue's PDF pipeline.
- **Do not colour the default stroke.** Coloured outlines read as emphasis. Keep
  `stroke` near-neutral (chroma < 0.18) and spend colour on fills and the accent arrow.
- **Do not colour-code without a legend** in the `multi-hue-categorical` family: every
  exemplar there ships an inline legend mapping hue to category.
- **Do not rely on hue alone for grey-vs-tint semantics** without saying so. When grey
  means "existing", 323 figures state it in the caption or an inline legend.

## Caveats

- Roles are normalised from the free-text `used_for` field with keyword rules
  (`palette_cluster.py:ROLE_RULES`), so coverage is uneven: `module` 649/727, `accent`
  432, `arrow-accent` 338, `text` 321, `container` 290, `stroke` 273, `arrow` 235, `lane` 78,
  `legend` 55, `text-muted` 40 (`module-alt` reaches 519 by absorbing a figure's
  remaining fills). Roles the records rarely name (`lane`, `legend`,
  `text-muted`) are filled from the cluster's own colours and are the least reliable.
- The records mention a stroke colour mainly when it is *unusual*: only 42 of the 87
  recorded stroke colours are near-neutral. The default thin dark outline is described in
  `style.stroke` prose rather than in `style.palette`, so `stroke` here is reconstructed
  as "the darkest neutral the family uses".
- 640 of 1,357 entries carry no role keyword at all and default to `module`; spot-reading
  that residue (`role_residue.txt`) confirms it is almost entirely "\<component\> box
  fill", which is what `module` means.
- 225 entries match several roles at once ("near-black box outlines and body text
  throughout"). They contribute to every role they mention but only one gets the primary
  slot, by the priority in `ROLE_RULES`; `role_multi.txt` lists all of them with the
  choice made, and a fill/background word always wins the primary slot over a text or
  border word.
- The ground classes are read off the same role text: a figure counts as outline-only when no palette entry
  names a container or lane fill and `layout.nesting_depth` ≥ 2. A record that simply forgot to list a pale
  ground would be misclassified; the exemplars of every ground family were checked by eye (four to six per
  family) and hold, and `general_rules.ground` in `palettes.json` keeps the counts.
- The silhouette sweep peaks at k=9 (0.36); the shipped families use k=14 (0.28) plus a
  merge of anything under 8 members, because k=9 leaves one 65-figure warm/grey blob that
  no single palette can describe. In that 272-figure run 2 figures had an empty `style.palette`
  and the family sizes total 270; the 727-figure re-run (9 empty) is reported in `Totals` above.
