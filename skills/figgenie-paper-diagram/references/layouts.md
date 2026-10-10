# Layout templates

How systems papers actually arrange architecture figures. Every number here is measured over the
**727 architecture diagrams** the corpus held when these numbers were computed (every human-rated
`good` architecture figure with a semantic record; statistics refreshed 2026-09-07 after the semantic
backfill; `sosp25-047_fig4` was reclassified to `mechanism` on 2026-09-09, leaving 726 — the counts
below were not re-run for that one figure) (`lab/extracted/corpus_semantics.jsonl` joined with
`corpus_index.csv`, keeping rows with `type=='diagram'` and `subtype=='architecture'`; venues
ASPLOS 25/26, NSDI 23-26, OSDI 23-26, SOSP 23-25). Regenerate any of it with:

```
python3 figgenie-paper-diagram/scripts/distill/layout_stats.py            # all sections
python3 .../layout_stats.py --section style                         # the style table below
python3 .../layout_stats.py --section enriched                      # sizes of the added templates
python3 .../layout_stats.py --section templates --template pipeline  # one template
```

Use this file in three steps:

1. Read **[Choosing a template](#choosing-a-template)** — map the figure spec's content structure to
   a template id.
2. Read that template's section — arrangement rules, numbering, legend, emphasis, pitfalls.
3. Open one or two of its **exemplars** before drawing: `assets/exemplars/<template-id>/index.json`
   lists them (starred = must-see, each with a one-line lesson); every figure is stored once under
   `assets/exemplars/figures/<id>/` — look at `print.png` (the figure as printed), then `manifest.json`
   and `source.svg`.

Twenty template ids: seven **core** (the corpus's own taxonomy) and thirteen **added** (recurring
sub-patterns and gaps, each with its own rules; I-M came from the type-discovery pass over all 727
good architecture figures). Added templates compose with core ones — a
`layered` figure can also be `replicated-grid` and `overview-with-inset`. Pick the core template for
the overall frame, then apply the added ones as modifiers.

---

## Canvas and typography (shared by every template)

Measured at print size, so these are the real constraints.

| | single column (593 figures, 82%) | double column (133 figures, 18%) |
| --- | --- | --- |
| width (pt) | median **246.4**, q1 244.8, q3 255.6 | median **510.0**, q1 505.1, q3 512.0 |
| height (pt) | median **153.2**, q1 123.4, q3 190.8, p90 230.9 | median **162.9**, q1 128.0, q3 201.7, p90 242.0 |
| aspect w/h | median **1.69**, q1 1.35, q3 2.05, p90 2.63 | median **3.08**, q1 2.52, q3 3.89, p90 4.57 |
| aspect bands | 1.5-2.0: 216, 1.0-1.5: 185, 2.0-3.0: 137, <1.0: 30, 3.0-4.5: 23, >=4.5: 2 | 3.0-4.5: 59, 2.0-3.0: 52, >=4.5: 14, 1.5-2.0: 6, 1.0-1.5: 2 |

- **Single column is 246 pt wide and about 155 pt tall.** Going below 1.0 aspect (taller than wide)
  happens 30/593 times and is always a deliberate tall stack (`asplos25-064_fig1` at 0.67,
  `nsdi24-072_fig9` at 0.78). Going above 2.5 at single column is a one-in-ten event (p90 = 2.63).
- **Double column is a strip, not a bigger square.** Height barely changes (median 162.9 vs 153.2 pt)
  while width doubles, so aspect roughly doubles to 3.08. If a double-column figure needs 250 pt of
  height it is probably two stacked single-column figures.

| measured style | value |
| --- | --- |
| components per figure | median **11** (q1 8, q3 14, p90 19, max 32) |
| flows (arrows) per figure | median **6** (q1 4, q3 9, p90 11, max 23) |
| distinct fill colours | median **6** (q1 4, q3 9, p90 13) |
| grey share of the palette | median **17%** (q1 2%, q3 45%) |
| body font size | median **6.5 pt** (q1 5.5, q3 7.5); smallest text median 5.5 pt; largest median 8.0 pt |
| stroke width | median **0.56 pt** (q1 0.40, q3 0.72); median **2** distinct widths per figure |
| shapes per figure | median 150 (q1 86, q3 299) |
| text boxes per figure | median 21 (q1 11, q3 35) |
| element density | median 47 per 100 pt² (q1 30, q3 75) |
| fill style | flat **655**/727, hatch 60, none 12 |
| corners | mixed 290, square 269, rounded 168 |
| type | sans **551**/727, serif 129, mixed 34 |
| dashed strokes used | **438**/727 (60%) |
| fully orthogonal routing (zero curved lines) | **453**/727 (62%) |

Derived rules of thumb (not corpus statistics — they follow from the numbers above):

- Budget roughly **1 component per 3,400 pt²** of single-column canvas: 11 boxes in 246×153 pt.
  An 11-component figure that is not 250 pt wide is either double column or too dense.
- Never set label text below **5 pt** and keep the body at **6.5-8 pt**; the largest label (a group
  title) should be at most **1.5×** the body size, matching the measured median (6.5 -> 8.0).
- Keep **two** stroke widths — 0.5 pt for boxes, 0.75-1.0 pt for arrows — and one dash pattern.
- Keep the palette at **4-7 fills** plus grey. Note that a bigger palette does *not* buy you a
  legend: the legend rate is 19% at ≤4 fills, 29% at 5-7, 29% at 8-10 and 34% above 10. Papers
  legend the *meaning* more than the colour count — so if a colour carries meaning, legend it whatever
  the palette size.

**Colour roles.** This file talks about layout; [`palettes.md`](palettes.md) supplies the hexes. The
layout objects below map onto its role ids one-to-one: a group/region box is `container`, a tier or
swimlane band is `lane`, an ordinary component box is `module` (a second *kind* of component is
`module-alt`), the contributed component or main path is `accent` / `arrow-accent`, ordinary
connectors are `arrow`, and an in-figure legend box is `legend`. Pick the template here, then pick
the palette there.

---

## Core templates

### 1. `pipeline` — 187 figures (26%)

Stages in a fixed order, each consuming the previous stage's output.

```
 ┌─────┐   ┌─────┐   ┌─────────────┐   ┌─────┐
 │ in  │──>│ S1  │──>│ ┌──┐  ┌──┐  │──>│ out │
 └─────┘   └─────┘   │ │a │->│b │  │   └─────┘
                     │ └──┘  └──┘  │
                     └──── S2 ─────┘
              <──────── feedback ────────
```

**When to use.** `depicts` = whole-system architecture 96, one subsystem 44, one path/request flow
43, comparison 4. Abstractions: distributed 34, ml-system 33, hardware 29, network 23, compiler 21,
runtime 15. Domains: ml-systems 90, networking 49, distributed-training 15, compilers 15. Component
count median **10** (q1 7, q3 13, max 27) — a wide usable range that absorbs most of the corpus's
small figures (19 of the 46 figures with ≤5 components are pipelines).
Flow count median **7**, tied with control-data for highest of the seven.

**Arrangement.**

- Direction: **left-right 124/187 (66%)**, mixed 40, top-down 23. Go left-right unless the stage names
  are long (>3 words), in which case go top-down and gain a left gutter for section tags.
- One row (or one column) of equal-height stage boxes on a shared centreline. Nesting depth 2 in
  116/187 — the stage is a container and its sub-modules sit inside it; depth 3 in 55, depth 1 in only 12.
- Lanes in 68/187 (36%), most of them left-right: lanes here mean *per-rank / per-GPU rows
  through the same stage sequence*, not swimlanes over time.
- Aspect: single column median **1.82** (q1 1.44, q3 2.23); double column median **3.32** (q1 2.72,
  q3 4.00, max 6.99). Matrix is now the most double-column-friendly template (35%); pipeline is a
  close second: **50/187 (27%)** run double column, vs 18% corpus-wide.
- Size: single 248×144 pt median; double 510×149 pt median.
- Text density dense 93, moderate 70, sparse 24. Median 166 shapes, 18 text boxes, 7 colours.

**Numbering and legend.** Step markers on **76/187 (41%)** — circled-numbers 54, letters 13,
labelled-arrows 8 — second-highest rate of the seven (host-device leads at 53%). Legend on only
36/187 (19%): inside 18, below 13, right 5. Stage titles go **inside** the stage box, in bold, at the top; group titles for a container
spanning several stages go on the container border (`asplos25-146_fig3`'s "Solver"). Section
references (§3, §4.1) go either in a left gutter (`asplos25-131_fig2`) or appended to the stage
title (`asplos25-094_fig6`).

**Main path and emphasis.** The main path is the straight centreline; everything else must leave it
alone. Feedback and bypass edges route along the opposite margin (`asplos25-131_fig2`,
`asplos25-041_fig1`'s residual line over the top). Emphasis is a dashed group box around the
contribution (`asplos25-157_fig7`'s DACO), or one accent-filled stage among grey ones.

**Variants seen in the corpus** (quoting `reusable_patterns`):

- "vertical pipeline of color-coded stage bands, each containing two named sub-components" — `asplos25-131_fig2`
- "vertical pipeline of stage boxes each annotated with a thumbnail illustration of its output artifact" — `asplos25-147_fig2`
- "encoder/decoder pipeline mirrored around a transmitted coded tensor" — `nsdi24-023_fig3`
- "stacked/offset boxes to denote a pool of homogeneous instances" — `osdi24-050_fig6`
- "two-phase pipeline diagram paired with an aligned execution timeline underneath" — `asplos25-082_fig3`
- "offline preparation phase feeding an online per-iteration control loop" — `asplos26-132_fig6`
- "horizontal compiler pipeline with a dashed, highlighted core-optimization sub-box" — `asplos25-157_fig7`
- "dashed callout expanding a block into its repeated sub-units" — `asplos26-088_fig11`
- **fork / merge**: two inputs merge into the spine, or the spine forks into two outputs — draw the
  merge as two arrows meeting the first stage, never as a fake stage (`asplos26-153_fig14`,
  `sosp24-043_fig5`, `osdi24-005_fig6`, `nsdi24-100_fig1`)
- **spine + satellite services**: the request path stays on the centreline and the loosely coupled
  services (prediction, training, inference servers) sit above/below it, connected by thin dashed
  edges (`osdi26-113_fig7`, `osdi26-078_fig1` with numbered plug-in slots, `nsdi23-067_fig4`)
- **fast path / slow path**: one entry, two lanes, the short lane returns directly and the long lane
  goes through the extra stages; label the lanes by cost, not by component (`nsdi24-006_fig2`,
  `osdi25-051_fig4`)
- **pipeline + attached device**: a stage hands lettered signals down to a device drawn under the
  pipeline; letters (a)-(g) index the prose, numbers would suggest order (`asplos26-100_fig6`)

**Pitfalls** (weakness clusters over the 187): dense/small text **73**, unexplained colour/icon 15,
abbreviations/notation 15, unlabelled/ambiguous arrows 11, relies on caption/body text 10, legend
placement 10, repeated/duplicate labels 9, print/greyscale risk 8, black box/omitted detail 8,
overlap/alignment 5, extreme aspect ratio 5, too many panels 4, raster content 3. Concretely:
"reusing the label 'Model' for three distinct boxes across phases relies on phase headers for
disambiguation" (`asplos26-026_fig4`); "no arrowheads on datapath lines reduces directional clarity".
Past the q3 of 13 components a pipeline stops reading as a line — split it into phases
(see `phase-lanes`) or nest sub-modules inside stage containers.

**Exemplars** (`assets/exemplars/pipeline/index.json` lists all 38; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-082_fig3` | Stack a structural diagram directly over a time axis sharing its horizontal alignment, so a highlighted timeline event reads as a direct consequence of the boxes above it; reserve red for the one failure case and use dashed brackets to group timeline phases. |
| `asplos25-131_fig2` | Put a narrow left gutter with section numbers (Sec 3, 4.1, 4.2, 4.3) beside the stage column and route the feedback arrow up the opposite margin so it never crosses the main path. |
| `asplos25-146_fig3` | Use a dashed box to group a multi-stage sub-pipeline as one unit distinct from the solid downstream stage, append section references directly onto stage titles, and use small coloured-bar card icons to encode variable-length data instead of prose. |
| `asplos25-147_fig2` | An output-artefact column beside the stage column turns abstract stage names into concrete data structures without any extra prose. |
| `asplos25-157_fig7` | At aspect >5 every stage must be one box-and-caption tall; wrap only the paper's contribution (here DACO) in a dashed group so the eye finds it in a long strip. |
| `asplos26-013_fig7` | When one upstream signal feeds two downstream decision paths in sequence, draw it as a linked pipeline with arrows carrying that signal forward, not as side-by-side comparison panels; let each stage keep its natural diagram type (block-matching grid, neural-net flowchart, point-cloud view) since forcing one shared vocabulary here would flatten real differences. |
| `asplos26-078_fig3` | Read this as a pipeline with parallel converging branches instead: three same-shaped signal-to-slowdown conversions run side by side under a dashed group box, then merge into one combined score; label the arrows themselves next time, since this figure leaves them unlabeled and relying on box-name adjacency. |
| `asplos26-088_fig11` | Dashed leader lines mean containment/zoom, solid arrows mean data flow; keeping the two line styles disjoint lets one figure carry both relations. |
| `asplos26-097_fig4` | The transferable move is pipeline's: run coloured dashed bands along the bottom naming which paper section documents each stage, and group the plugin-style services (S3, SQS, Pub/Sub) as small icons inside one stage rather than drawing each as a separate box. |
| `asplos26-132_fig6` | Split one-time setup from the per-iteration loop with a dashed group boundary, and number only the steps that repeat. |
| `nsdi23-045_fig2` | Keep the numbered main path as one row of plain boxes and drop expanded explanation into dashed callout boxes underneath, tied by leader lines and annotation text back to the numbered step they detail; finish a signal-processing pipeline with a rendered-output thumbnail, not just a label. |
| `nsdi24-023_fig3` | At double column, mirror the two halves around the one object that crosses between them, and park a two-entry legend in the empty top strip. |
| `nsdi24-043_fig1` | When a pipeline is really a whole-lifecycle map, arrange the numbered stages in a compact grid rather than one long row, nest each stage's own sub-steps inside it, and draw a periodic feedback relationship as one separate curved arrow in a second colour rather than reusing the numbered arrows. |
| `nsdi26-133_fig4` | Nest a fine-grained numbered sequence inside two or three coarse top-level containers rather than one box per step, highlight one concrete instance in an accent colour as it moves through every stage, and drop dashed leaders from bottom annotations up to the exact stage that consumes each field. |
| `osdi23-039_fig3` | Bookend a pipeline with explicit Input/Output panels rather than bare arrows at the edges, attach third-party tool names as small boxes above or below the stage they instrument instead of putting them on the main line, and mark the contribution with a dotted boundary plus one internal feedback arrow. |
| `osdi24-050_fig6` | A two-stage pipeline needs only a controller, two stage groups and one labelled hand-off arrow; stacked/offset boxes stand in for 'a pool of N identical instances' without drawing N of them. |
Starred 16 of 38; the other 22 are in `index.json` with one-line notes.
Starred 13 of 26; the other 13 are in `index.json` with one-line notes.

---

### 2. `layered` — 162 figures (22%)

Horizontal tiers, each depending only on the tier below.

```
 ┌───────────────────────────────┐
 │  application  │  ┌──┐ ┌──┐    │  <- tier label in left gutter
 ├───────────────────────────────┤
 │  control      │  ┌──┐ ┌──┐    │
 ├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┤  <- dashed = trust / network boundary
 │  hardware     │  ┌──┐ ┌──┐    │
 └───────────────────────────────┘
```

**When to use.** `depicts` = whole-system architecture **119/162 (73%)** — second-strongest signal of
the seven (hub-spoke now leads at 78%) — one subsystem 26, one path/request flow 8, deployment 5,
comparison 4. Abstractions: distributed 52, kernel 29, runtime 19, hardware 17. Domains: ml-systems 56,
storage 27, os-kernel 27, networking 25.
Component count median **13** (q1 9, q3 16, max 30) — the busiest template. Use it when the spec
names 3-5 tiers and the reader's question is "what sits on top of what".

**Arrangement.**

- Direction: **top-down 128/162 (79%)**, mixed 21, bottom-up 10, left-right 3. Bottom-up only for memory
  hierarchies read from the device outward (`osdi25-016_fig8`).
- Full-width tier bands of equal height; modules are equal-height boxes inside a band. Nesting depth
  3 in **79/162** and 4 in 11 — layered remains one of the deepest-nesting templates (56% at depth ≥3
  vs 42% overall), though host-device is now deepest at 60%.
- Lanes 69/162 (43%), most of them top-down: a lane here is a column *inside* a tier (per-worker,
  per-plane), giving a tier×column grid.
- Aspect: single column median **1.46** (q1 1.18, q3 1.79) — the tallest template. Only **9/162 (6%)**
  are double column, the lowest share of the seven; a layered figure that will not fit at 246 pt wide
  should get taller, not wider.
- Size: single 246×177 pt median (24 pt taller than the corpus median).
- Median 120 shapes, 21 text boxes, 6 colours, 39 elements per 100 pt² — the *least* dense template
  per unit area, because bands buy whitespace.

**Numbering and legend.** Step markers on 42/162 (26%): circled-numbers 34, labelled-arrows 5,
letters 3. Legend on 42/162 (26%) — fourth-lowest of the seven (pipeline is now lowest at 19%); tier
names do the work a legend would. **Tier names go in a gutter**, left (`osdi24-025_fig6`, `nsdi26-030_fig1`) or right
(`nsdi24-072_fig9`, `asplos25-038_fig3`), or as a bold header inside the band
(`asplos25-064_fig1`'s "Layer 1: Job Profile Layer (§3.1)"). Section references are attached to the
tier name, not to individual modules.

**Main path and emphasis.** There is usually no single path — the figure asserts structure. When
there is one, it is a numbered request descending and returning (`sosp25-020_fig3`,
`nsdi26-090_fig4`). Emphasis: a dashed accent box around the contributed tier or sub-tree
(`nsdi23-084_fig3`), or a tinted band among white ones (`nsdi24-072_fig9`'s green CASSINI band
between peach and yellow existing tiers).

**Variants.**

- "layered system stack with a labeled network boundary" — `osdi24-025_fig6`
- "numbered layer stack with icon + description per row" — `asplos25-064_fig1`
- "control-plane panel on top driving a homogeneous row of compute devices sharing a resource pool below" — `sosp24-041_fig5`
- "a new module inserted between an existing planner and its existing execution agents, color-coded by which parts are novel" — `nsdi24-072_fig9`
- "parallel replicated columns (one per worker/GPU) inside a single outer system boundary" — `nsdi23-047_fig7`
- "shared DRAM bus at top feeding parallel specialized engines below" — `asplos26-013_fig10`
- "three-tier software/hardware/network stack diagram" — `nsdi26-030_fig1`

**Pitfalls.** dense/small text **54**, unexplained colour/icon 11, abbreviations/notation 10, relies on
caption/body text 8, unlabelled/ambiguous arrows 6, overlap/alignment 5, legend placement 4,
print/greyscale risk 3, repeated/duplicate labels 2, raster content 2, too many panels 2, extreme
aspect ratio 1. Specific: "no arrows to indicate direction of dependency or data
flow between layers" (`nsdi26-030_fig1` — acceptable when the claim is only "these tiers exist");
"single-column layout makes the figure very tall (aspect 0.67)" (`asplos25-064_fig1`). With 30
components a layered figure needs the tier count held to 4-5 and modules capped at 4 per tier.

**Exemplars** (`assets/exemplars/layered/index.json` lists all 34; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-012_fig2` | When the tiers are literally computation layers of one repeated block, read them bottom-up with input at the floor and output at the ceiling, show repetition with a few offset background rectangles rather than N boxes, and distinguish a router's considered-but-not-taken paths, dashed, from its actual path, bold solid, in one colour. |
| `asplos25-028_fig2` | Put tier labels in a slim right gutter instead of inside the band, use two flat fills, white for logic and gray for state, to separate function from data within one tier, and draw the repeated bottom-tier devices once in full detail then abbreviate the rest to a label only. |
| `asplos25-074_fig7` | Use one dashed box per contribution, each carrying its own section number, scattered across whichever tier it actually belongs to, rather than one big accent region; keep a solid-versus-dotted line legend so control paths and data paths stay distinguishable across the whole cluster-to-hardware stack. |
| `asplos25-097_fig1` | Name the dashed boundary line itself instead of leaving it a bare rule, give each of the 3-4 tiers its own accent colour tied to the tier's own name, and put a small solid/dashed legend below the figure when line style carries a data-versus-control meaning. |
| `asplos26-013_fig10` | At double column a layered hardware figure becomes bus-on-top with engines hanging below; lettered callouts (A-I) index the prose instead of ordering a flow. |
| `asplos26-139_fig7` | Colour the two memory tiers, not just their contents, so DRAM versus flash is legible before reading labels, and represent a pool of same-role objects as a row of small identical boxes; the record flags thin curved feedback arrows as easy to miss, so make a feedback path as heavy as the path it answers. |
| `nsdi23-035_fig3` | When more than two colours carry role meaning, put a compact legend inside a free corner rather than relying on labels alone, and let one hardware box be jointly annotated by two different functional tiers, a long-term planner's output above and a short-term runtime's control below, to show both act on the same resource. |
| `nsdi23-047_fig4` | When a tier is really N replicated nodes, draw exactly two identical side-by-side boxes with a crossing arrow between them to stand for the whole replicated set, and reuse the same internal layout one tier below so the eye maps server-to-worker pairs straight down the page. |
| `nsdi23-084_fig3` | Wrap the contribution in a dashed accent-coloured box inside the stack, and use paired up/down arrows to show a config-down / telemetry-up interface in one place. |
| `nsdi23-085_fig8` | Draw redundant top-tier controllers with crossing arrows into every replica below to show any-to-any reachability without extra edges, give every role one flat colour so the internal stack reads at a glance, and let a single full-width bottom box stand for the one shared backing store beneath repeated node containers. |
| `nsdi24-072_fig9` | Band labels can live in a rotated right gutter instead of the left, freeing the left margin for the feedback arrow that closes the loop. |
| `nsdi25-054_fig2` | Split a middle tier into parallel same-size backend boxes, each its own colour, all resting on one shared dashed core box beneath them, and label the two interception arrows above and below that middle tier by name instead of leaving them bare, making the tier's two boundaries explicit. |
| `nsdi25-073_fig7` | The transferable move is layered's: highlight only the paper's own novel boxes in one accent colour, here purple on exactly four of twenty components, against plain white boxes, so contribution versus reused building block reads instantly even with no arrows at all. |
| `nsdi26-086_fig2` | When two parallel software stacks share one critical sub-path, draw them as two columns and recolour only the shared boxes that carry the argument, then number the request path across both columns so the highlighted path reads as one continuous route rather than two separate stacks. |
| `nsdi26-090_fig4` | A dashed labelled rule can express a deployment boundary (region, host, trust domain) inside an otherwise ordinary layered stack. |
| `osdi24-025_fig6` | Name tiers in the left margin, keep every module row the same height, and use a single dashed horizontal rule (labelled 'Internet') for the boundary that matters. |
| `osdi26-030_figtex2` | Draw a tier's artifact as a literal table, columns and all, rather than a plain box when the paper's contribution is the schema itself, and write command strings right on the arrow that triggers them; keep matching colour bands consistent between the table and the running-kernel bar they describe. |
| `osdi26-054_fig9` | Treat this as a control-loop figure instead: stack the three privilege bands top to bottom, and let one circled 1-5 sequence travel down through the fault handlers and back up, rather than expecting any part of it to show replicated peers. |
| `osdi26-060_fig8` | When colour is not carrying meaning, differentiate nested tiers by shading depth alone, darker gray for the outer container and lighter for inner boxes, and place matched request/response queue icons flanking the control boxes they feed so the master-to-worker path stays readable in one grayscale palette. |
| `osdi26-076_fig5` | Overlay circled step numbers straight onto the tier-to-tier arrows of a vertical stack to narrate one concrete request, split a single decision into two coloured branch labels rather than separate diagrams, and use hatching to mark which address ranges are currently backed by a cache block. |
| `sosp24-005_fig4` | Embed a small data object, such as a lookup table with one highlighted row, inside the tier that owns it rather than describing it in prose, and number the back-and-forth arrows between just two tiers in interaction order even when several arrows point the same direction, so the loop reads sequentially. |
| `sosp24-011_fig8` | Separate offline planning from online execution as two stacked full-width bands joined by one labelled arrow, draw the bottom tier as a row of otherwise identical worker boxes, and mark the one instance that misbehaves with a red dashed outline instead of a caption. |
| `sosp24-041_fig5` | The 'manager over devices over shared pool' sandwich: a dashed horizontal rule separates control plane from data plane and the shared pool is a full-width band. |
| `sosp25-020_fig3` | Colour is optional: white boxes for the traced path and gray for background components, plus dashed band separators, already carry a full layered architecture. |
| `sosp25-035_fig1` | Label the two sides of a dashed interface line with a short margin tag rather than titling each box separately, and draw a replicated stateless pool as one small sub-box holding numbered instances plus an ellipsis rather than drawing every replica full size. |
| `sosp25-060_fig5` | Give a shared upper stage one neutral colour pair and let it feed two side-by-side lower columns that each keep their own colour for the rest of the figure, down to the small square page icons at the very bottom, so colour alone tracks which allocator produced which output. |
Starred 26 of 34; the other 8 are in `index.json` with one-line notes.
Starred 24 of 29; the other 5 are in `index.json` with one-line notes.

---

### 3. `two-panel` — 105 figures (14%)

Two comparable sub-figures in one frame, side by side or stacked.

```
 ┌───────────────┬───────────────┐
 │      (a)      ┆      (b)      │   <- dashed rule or gap between
 │   ┌──┐ ┌──┐   ┆   ┌──┐ ┌──┐   │
 │   └──┘ └──┘   ┆   └──┘ └──┘   │
 └───────────────┴───────────────┘
   (a) Baseline       (b) Ours
   ▣ legend spanning both panels
```

**When to use.** `depicts` = comparison 35, whole-system architecture 32, one subsystem 22, one
path/request flow 9, deployment 7. It holds 35 of the corpus's 76 comparison figures — more than any
other template, though `matrix` has the higher internal share (16/31 = 52%). Abstractions: hardware 25,
distributed 21, network 14, ml-system 9, kernel 9. Component count median **11** (q1 8, q3 15).
Flow count median **5** — the second-lowest, because the argument is structural, not procedural.

**Arrangement.**

- Direction: left-right 61, mixed 27, top-down 16. Side by side when each panel is narrow; **stacked**
  when each panel is wide (`asplos25-051_fig1`, `osdi26-020_figtex8`, `nsdi23-004_fig1`).
- `panels` is recorded as 1 in **63/105** and 2 in 38: more than half of two-panel figures have no
  formal sub-figure frames, just two halves separated by a dashed rule or whitespace.
- The two halves must have **identical internal geometry**. Vary exactly one element; keep at least
  one component identical and in the same position as an anchor (`asplos25-110_fig1`'s Shared LLC).
- Nesting depth 2 in 60/105, 3 in 36. Lanes 38/105 (36%).
- Aspect: single median **1.82** (q1 1.48, q3 2.16); double median **3.20**. 23/105 (22%) double column.
- Median 162 shapes, 25 text boxes, 55 elements per 100 pt² — the **densest** core template per unit
  area, because two structures share one canvas.

**Numbering and legend.** Steps on 31/105 (30%): circled-numbers 23, labelled-arrows 4, letters 4.
Legend on 24/105 (23%): inside 17, right 5, below 2. **One legend for both panels, never two** — put it
below spanning the full width (`asplos25-100_fig9`), inside the first panel's empty corner
(`nsdi23-004_fig1`) or in a right-hand column (`nsdi26-017_fig5`).
Panel captions are `(a)`/`(b)` set **below** each panel, and the best ones name the claim rather than
the system: "(a) Now: Library+Sidecar" / "(b) Our Vision: RPC as a Managed Service".

**Main path and emphasis.** Emphasis is the *difference*: a red cross on what breaks in (a)
(`osdi23-003_fig4`), a shaded ground under your row, a bracket over the interval you save
(`osdi26-020_figtex8`'s "Speedup"), or a bold "V.S." between the halves (`asplos25-051_fig1`).

**Variants.**

- "side-by-side subfigure comparison of a naive mechanism (a) versus its fix (b)" — `osdi23-003_fig4`
- "mirrored two-panel diagram sharing a central control block to depict a mode switch" — `asplos25-157_fig3`
- "two stacked timelines sharing one time axis to contrast a new system's downtime against a baseline" — `osdi26-108_fig3`
- "annotated request/reply trace counting per-hop operations to make an efficiency argument" — `nsdi23-004_fig1`
- "numbered pipeline explained once, then reused as a sub-block inside two parallel loops" — `asplos26-013_fig2`
- "host/device box-and-cache motif repeated per participant" — `asplos26-033_fig4`
- "overview-plus-zoomed-detail two-panel layout" — `osdi25-003_fig2`

**Pitfalls.** dense/small text **32**, unlabelled/ambiguous arrows 9, unexplained colour/icon 8,
repeated/duplicate labels 7, abbreviations/notation 5, relies on caption/body text 3,
overlap/alignment 3, legend placement 2, print/greyscale risk 2, too many panels 2, extreme aspect
ratio 1, raster content 1. The template-specific failure is a missing connective: "no
explicit arrows link the left pipeline boxes to the right-hand comparison" — if the panels are
related, say how, with an arrow or a shared axis. Second failure: unequal panel geometry, which makes
readers compare shapes instead of contents.

**Exemplars** (`assets/exemplars/two-panel/index.json` lists all 27; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-051_fig1` | Stack the two designs vertically when each is wide; a centred 'V.S.' label plus a dashed 'focus of this paper' bracket replaces sub-captions. |
| `asplos25-052_fig1` | Label the two conditions with brackets above the shared boxes (Software-isolated / Hardware-isolated) instead of duplicating structure, but do add a legend line for the highlight colour: this exemplar's own weakness is leaving that yellow-vs-plain fill unexplained. |
| `asplos25-100_fig9` | When both panels use the same colour encoding, the legend goes below spanning the full width - never duplicated per panel. |
| `asplos25-177_fig1` | To map a software concept onto hardware, draw matching panels and colour-highlight the same instance (one row, one column) in both; label the two access dimensions on the hardware grid's axes. Add a numbered connector between panels: this exemplar leaves that link to the caption. |
| `asplos26-013_fig2` | Define a numbered sub-pipeline in the first panel, then reuse the same numbers inside the second panel's loops instead of renumbering. |
| `asplos26-102_fig3` | Skip the dividing rule: give each stage its own fill colour (green offline, blue online) so the two-panel split reads from colour alone, and use dashed arrows only for the feedback edges (Kernel Info back to the Profiler). |
| `osdi23-050_fig4` | Keep the same operator colours (blue MatMul, yellow Relu, gray Add) in both panels so a reader tracks exactly which pieces move from the CPU-side loop into accelerator-resident tasks; note panel (b)'s extra L0/L1/L2 tiers cost effort to map back to (a). |
| `osdi25-003_fig2` | When one panel is a zoomed slice of the other rather than a comparable structure, connect them with a single dashed callout instead of forcing a second full panel frame; watch the font size once nesting reaches DP/PP/Layer/CP/TP depth, since this exemplar's own weakness is text too small for its nested detail. |
| `osdi26-061_fig2` | The transferable move is two-panel's: stack a software layer directly above the hardware topology it runs on in panel (a), colour-code control/data/network traffic by one shared legend, then reuse the same component names in panel (b)'s separate threading-model view instead of drawing a zoom. |
| `osdi26-085_fig2` | When comparing two prior designs, redraw the same graph-index glyph and the same colour code (blue = visited path, red = top-k result, gray = unvisited) in each panel, changing only the storage medium each graph sits on. |
| `sosp25-043_fig6` | Divide the canvas with one plain vertical dashed rule instead of two boxed panels, bold the two side titles above it, and reserve colour (red RX, green TX) for the one distinction the case study is about. |
Starred 11 of 28; the other 17 are in `index.json` with one-line notes.
Starred 11 of 24; the other 13 are in `index.json` with one-line notes.

---

### 4. `control-data` — 78 figures (11%)

One structure carrying two or three distinguishable flow classes: data movement, control decisions,
and sometimes telemetry.

```
 ┌──────────── control plane ───────────┐
 │   ┌────────┐        ┌────────┐       │
 │   │scheduler│ ─ ─ ─>│ monitor│       │
 └───────│──────────────────▲───────────┘
 ─ ─ ─ ─ │─ ─ ─ ─ ─ ─ ─ ─ ─ │─ ─ ─ ─ ─ ─   <- plane divider
 ┌───────▼────┐         ┌───┴────┐
 │  ingress   │────────>│ egress │            ── data   ─ ─ control
 └────────────┘         └────────┘
```

**When to use.** `depicts` = whole-system architecture 52, one subsystem 15, one path/request flow 8,
deployment 2, comparison 1. Abstractions: distributed 34, network 13, hardware 10, kernel 7.
Component count median **10** (q1 7, q3 14) — no longer among the tightest spreads; `host-device`
now holds the tightest (q1 10, q3 14) of the seven. Choose it over `layered` when
the figure spec's flows have **≥2 distinct kinds** (data vs control, request vs telemetry,
functional vs instruction) and the paper's point depends on telling them apart.

**Arrangement.**

- Direction: mixed 30, left-right 25, top-down 23 — no dominant axis, because the axis is chosen by the
  planes. Two horizontal bands for a control-over-data split (`asplos25-109_fig4`,
  `asplos25-077_figtex1`); left-right when the data path itself is a pipeline (`asplos25-100_fig5`).
- Nesting depth 2 in 40/78, 3 in 28, 4 in 6, 1 in 3. Lanes 42/78 (54%).
- Aspect: single median **1.67** (q1 1.42, q3 1.99); only 5/78 (6%) double column.
- Median 144.5 shapes, 23 text boxes, 6 colours.

**Numbering and legend.** Legend on **28/78 (36%)** — third-highest of the seven, after
`matrix` (42%) and `host-device` (38%) — below 13, inside 12, right 3. This is the template where the legend
is nearly mandatory: it is what defines the flow classes. Steps on 26/78 (33%), circled-numbers 20.
**Cap the flow classes at three.** The corpus's clearest instance (`asplos25-100_fig5`) uses
exactly three, named in a "Legends" block: inter-device data (black solid), intra-device data
(blue solid), control (orange dashed).

**Main path and emphasis.** The data path is the spine and gets the heavier stroke; control edges are
dashed, thinner, and drawn *around* the spine rather than through it. `line_style_means` mentions
dashed in 441/727 records corpus-wide — dashed almost always means control, optional, or boundary.
Emphasis is the plane the paper contributes to (`asplos25-051_fig2` highlights the Central Scheduler
inside the switch).

**Variants.**

- "single-device block diagram with an explicit flow-type legend distinguishing control vs. data paths" — `asplos25-100_fig5`
- "abstract function-block model with a control-plane/data-plane split, borrowed from network-switch terminology" — `asplos25-077_figtex1`
- "side-by-side protocol stack columns with colored path overlays contrasting old vs. new data paths" — `asplos25-051_fig2`
- "dispatcher-to-typed-queues-to-typed-engines topology with a control-plane feedback loop" — `sosp25-032_fig4`
- "one element recolored/dashed among repeated identical elements to indicate the faulty instance" — `sosp23-013_fig3`
- "numbered steps overlaid on a control/data dual-channel diagram" — `asplos25-109_fig4`
- "explicit in-figure legend defining color and line-style semantics" — `asplos25-140_fig7`
- **a third flow class** (metrics / background / telemetry) gets the *dotted* line, keeping solid =
  data and dashed = control; a "critical path / background" pair uses stroke weight instead
  (`nsdi26-005_fig2`, `nsdi26-005_fig3`, `sosp24-025_fig4`, `nsdi26-042_fig8`)

**Pitfalls.** dense/small text **28**, abbreviations/notation 7, repeated/duplicate labels 7,
unexplained colour/icon 6, unlabelled/ambiguous arrows 5, relies on caption/body text 2, raster
content 2, legend placement 1, overlap/alignment 1, extreme aspect ratio 1, black box/omitted
detail 1. The named failure is exactly the one this template
exists to avoid: "no explicit color coding distinguishes data vs control signals", and "no explicit
legend distinguishing data path vs control path colors beyond small in-figure labels". If you use
colour to separate flow classes you must legend it in-figure — the caption is not enough.

**Exemplars** (`assets/exemplars/control-data/index.json` lists all 26; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-046_fig13` | Stack a cluster-level control tier above a per-server agent tier inside two dashed regions, and instead of a separate legend, resolve the color coding by mapping each memory band directly to a named example VM (GPVM1, CoachVM2) below; label bands in the box itself since this figure's colors are not otherwise legended. |
| `asplos25-077_figtex1` | Borrow switch terminology literally - label the margins 'control plane' / 'data plane' and let the divider do all the grouping work. (No PDF-extracted print.png; this is a TeX-only figure.) |
| `asplos25-097_fig2` | Draw a security module as a literal inline choke point on both Tx and Rx paths, not a side box, so nothing bypasses it; this figure legends six path classes below, more than the template's usual three-class cap, so only go that far if every class needs its own arrow style. |
| `asplos25-100_fig5` | Name every arrow class explicitly in an in-figure legend; three classes is the practical maximum and dashed should be reserved for control. |
| `asplos25-140_fig7` | At double column there is room for a full legend block that defines module colours and arrow line styles together; put it in the top-left corner before the flow starts. |
| `asplos26-036_fig8` | Name each control arrow with the verb it performs (Latency, Update, Plan, Compute) instead of a bare control/data label, tag each subsystem box with its own paper section number, and keep a tiny inline legend only for the one sub-panel (the timeline) that needs its own notation. |
| `nsdi26-092_fig6` | Draw two symmetric peers around a shared object in the middle, label its access rights (WO/RO) directly on the box, and run the mediating monitor as a full-width band underneath; if you mark denied access with a red X, add it to the legend, unlike this figure. |
| `nsdi26-124_fig4` | Use one dashed rule as the entire plane boundary, then letter (not number) the arrows that cross it when their meaning needs the body text rather than a self-contained legend; color the two control-plane phases (orange pre-profiling, green slowdown) so their converging arrows read as one pipeline. |
| `osdi24-001_fig9` | When two paths share the same component, skip separate plane boxes and instead run a colored bar (red control, green data) directly under the shared box, with circled numbers 1-4 tracing the single request across both paths. |
| `osdi26-047_fig5` | When one figure needs two kinds of legend, state (chunk fill/hatch) and flow type (solid vs dashed-red arrows), keep both inside the frame but in separate corners rather than merging them, and let the replicated instances below use a plain ellipsis so the control components above stay the visual anchor. |
| `osdi26-063_fig8` | Tinted dashed regions name the planes, circled numbers order the loop, and a plain device row anchors the bottom - all at single-column width. |
| `sosp23-013_fig3` | To show a failure or special case among N identical elements, restyle one instance (red dashed) instead of adding a callout. |
| `sosp24-027_fig4` | Group the replicated data-plane nodes in one dashed box separate from the small control-plane index/client pair, and use only two nodes plus an ellipsis rather than drawing every replica; avoid this figure's mistake of setting labels in a small serif font that hurts legibility. |
| `sosp25-032_fig4` | Draw the control plane as its own box under the data path with its own arrows, so 'who decides' is separable from 'what moves'. |
| `sosp25-053_fig4` | Box the data plane and control plane as two separate dashed regions, use an offset card stack (Pod 0/1/N) to show replication inside the data-plane box without drawing every pod, and put a two-color arrow legend below to name data flow versus control flow. |
Starred 15 of 26; the other 11 are in `index.json` with one-line notes.
Starred 15 of 23; the other 8 are in `index.json` with one-line notes.

---

### 5. `hub-spoke` — 40 figures (6%)

One coordinator surrounded by N peers of the same kind.

```
                  ┌────────────┐
                  │  Worker 0  │
 ┌───────────┐ ─> └────────────┘
 │ Scheduler │    ┌────────────┐
 │  (hub)    │ ─> │  Worker 1  │
 └───────────┘    └────────────┘
                        ⋮
                  ┌────────────┐
               ─> │ Worker N-1 │
                  └────────────┘
```

**When to use.** `depicts` = whole-system architecture **31/40 (78%)** — the highest concentration of
any template — one subsystem 4, one path/request flow 3, deployment 2. Abstraction **distributed
25/40 (62%)**; domains ml-systems 16, cloud 10, distributed-systems 8, networking 6. Component count
median **10** (q1 7, q3 13, max 29). Choose it when the spec has a named coordinator plus a set of
interchangeable workers/servers/shards.

**Arrangement.**

- Direction: mixed 21, left-right 11, top-down 7, bottom-up 1 — one of the least axis-bound templates
  (52% mixed; matrix is now the least axis-bound at 65% mixed), because the hub sits at a focal point
  rather than on a line. Practical default: hub left or top, spokes in a right-hand or lower column.
- **Draw two or three concrete spokes, then an ellipsis, then the last one labelled N or N-1.** None
  of the exemplars here draws more than three full replicas (`sosp23-016_fig4`: Worker 0, Worker 1,
  ⋯, Worker N-1; `sosp25-061_fig7`: Worker-0, ⋯, Worker-N; `osdi24-015_fig5`: three servers).
- Every spoke uses an **identical internal template**; only its contents vary. One spoke may be drawn
  expanded next to schematic ones to show scale-out (`osdi24-036_fig8`).
- Nesting depth 2 in 18/40, 3 in 17, 1 in 3, 4 in 2. Lanes only 9/40 (22%) — the lowest of the seven;
  `host-device` is now second-lowest at 30%.
- Aspect: single median **1.70** (q1 1.37, q3 2.06); 3/40 (8%) double column.
- Median 118 shapes (the sparsest core template), 23 text boxes, 7 colours.

**Numbering and legend.** Steps 14/40 (35%), legend 10/40 (25%). Because the hub-to-spoke arrows are
often several kinds at once (dispatch, migrate, report), a small legend distinguishing arrow classes
pays for itself (`osdi24-036_fig8`: orange solid = migration control, dashed = other control). Hub
title bold inside the hub box; spoke titles bold in the spoke's top-left.

**Main path and emphasis.** The eye starts at the hub. The client/request source enters from outside
the hub (`osdi23-003_fig5`'s clients cloud). Emphasis is fill on the hub, or on the one sub-component
of the hub the paper contributes (`osdi24-015_fig5`'s light-blue scheduler box).

**Variants.**

- "centralized manager coordinating a stack of repeated worker units with an ellipsis" — `sosp23-016_fig4`
- "hub controller box connected to multiple peer server boxes each showing a tiered storage stack" — `osdi24-015_fig5`
- "hub controller fanning out dotted control lines to per-node local controllers, with one node shown magnified" — `nsdi24-087_fig2`
- "two-level global/local scheduler hierarchy" / "one detailed instance expanded next to collapsed replica instances" — `osdi24-036_fig8`
- "NxN fully-connected mesh topology diagram paired with a zoomed single-node block diagram" — `asplos26-074_fig9`
- "numbered request path over a sharded replicated architecture with a shared table at top" — `osdi23-003_fig5`

**Pitfalls.** dense/small text **13**, unexplained colour/icon 4, abbreviations/notation 4,
repeated/duplicate labels 2, overlap/alignment 2, relies on caption/body text 1,
unlabelled/ambiguous arrows 1, black box/omitted detail 1. Watch for "many repeated boxes share the same label, making individual instances hard
to tell apart" — index the spokes (0, 1, N-1) rather than repeating one name. Also: at the group's
maximum of 29 components the hub itself has tiers, and `multi-tier` is usually the better frame.

**Exemplars** (`assets/exemplars/hub-spoke/index.json` lists all 24; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-039_fig3` | At double column a hub-spoke becomes three left-to-right zones (controller / topology / one-node detail) with the legend below. |
| `asplos25-052_fig5` | When N identical agents all talk to one shared coordinator, it can sit below them as a horizontal band instead of beside them as a box; keep every agent column visually identical and mark its two channels (Actions up, Reward down) the same way in each. |
| `asplos25-138_fig17` | At this scale, reserve one accent colour (red) purely for the paper's new contribution, here the two highlighted Instance Configurator boxes and their routing path, so the one novel mechanism stays findable inside 600 shapes and 72 text boxes of otherwise uniform infrastructure. |
| `asplos26-074_fig9` | For mesh/topology figures, panel (a) is the graph and panel (b) is a dashed-connected zoom of a single node; the shared HBM bar spans the bottom of (b). |
| `nsdi23-067_fig4` | A hub's spokes need not be identical: when two offload targets do genuinely different jobs, still draw them as parallel boxes at the same level, and colour-code the shared unit that threads through both, four packet flows here, so the reader can follow one flow out to its spoke and back. |
| `nsdi23-083_fig3` | Use a lighter dashed line for background catalog/status traffic into the hub and a solid line for the actual job request. This exemplar's weakness: with only two named clouds and no ellipsis, it does not visually confirm the broker scales beyond a pair. |
| `nsdi24-087_fig2` | Dotted curved lines are the right weight for 'the hub controls all of these'; magnify exactly one spoke to show what a controlled node contains. |
| `nsdi25-033_figtex7` | Run one continuous numbered path (0-7) from client through the hub's internal EDF queue, scheduler and dispatcher out to the workers and back, and let two colour-coded example queries (green, blue) walk the same numbered path to different spokes to show scheduling in action, not just structure. |
| `nsdi26-082_fig2` | Draw the hub as a thin horizontal bar rather than a box when its whole job is mediating traffic, and label every bidirectional arrow with the noun it exchanges in each direction, not just an arrowhead; keep the layout tight since this exemplar's weakness is a dense, icon-packed square. |
| `osdi23-003_fig5` | A replicated-store figure needs three things: a client source, one expanded server, and collapsed peers; the legend distinguishes operation classes by line style. |
| `osdi23-008_fig2` | A hub can both dispatch to and learn from its spokes: draw the return arrow (Per-Job Feedback) the same weight as the dispatch arrow (Resource Allocations) and label each with the concrete payload it carries, not with a generic loop. |
| `osdi24-015_fig5` | Give every spoke an identical internal template and vary only its contents; letters (A, B) then annotate which spoke holds what. |
| `osdi24-036_fig8` | One expanded instance beside two schematic ones communicates scale-out; the legend then only has to explain the one arrow class that matters. |
| `osdi26-005_fig3` | Tie each drawn mechanism to its paper section number right on the box, so the figure doubles as a reading index; but name what the ellipsis between group 0 and group n hides, since leaving it uncounted is this exemplar's own recorded weakness. |
| `sosp23-016_fig4` | Draw the first two spokes in full, then an ellipsis row, then the last one labelled N-1; never draw more than three concrete replicas. |
| `sosp25-064_fig5` | Give the hub a dashed boundary and colour its internal resource pools by type (orange SSD, teal NIC), then draw only Host 1 and Host N with an ellipsis between, each an identical Instance-plus-Engine box, and put the fan-out arrows in one bold accent colour. |
Starred 16 of 24; the other 8 are in `index.json` with one-line notes.
Starred 18 of 26; the other 8 are in `index.json` with one-line notes.

---

### 6. `matrix` — 31 figures (4%)

A grid whose rows and columns each carry meaning: small multiples, a design-space table, or a
resource map.

```
            column = variant / phase / category
          ┌──────────┬──────────┬──────────┐
 row =    │  ┌────┐  │  ┌────┐  │  ┌────┐  │
 approach │  └────┘  │  └────┘  │  └────┘  │
 / rank   ├──────────┼──────────┼──────────┤
          │  ┌────┐  │  ┌────┐  │  ┌────┐  │
          └──────────┴──────────┴──────────┘
            ▣ one legend below or above, shared
```

**When to use.** `depicts` = **comparison 16/31 (52%)**, whole-system architecture 9, one subsystem 5,
deployment 1. Abstractions: hardware 8, ml-system 5, kernel 5. Component count median **9** (q1
7, q3 12) and **flow count median 4** (q1 2, max 10) — by far the fewest arrows, because adjacency
replaces arrows. Choose it when the spec has ≥3 comparable things, or a two-dimensional key
(rank × stage, pool × resource, type × diagnosis).

**Arrangement.**

- Direction: **mixed 20/31** — a matrix has two axes, so "direction" is a poor fit; what matters is
  that rows and columns each mean something and both are labelled.
- `panels` ≥2 in **11/31 (35%)** (3 panels ×4, 4/5/6 panels ×2 each, 2 panels ×1) — no longer the
  highest multi-panel rate of the seven; `two-panel` has overtaken it at 40%. The other 20 are
  single-frame grids.
- All cells identical in size and internal layout; only content varies. Give the panel you are
  arguing for **more width or more detail** than its baselines (`nsdi26-143_fig1`, `osdi23-048_fig1`).
- Nesting depth 2 in 19/31, 3 in 7, 1 in 5. Lanes 17/31 (55%).
- Aspect: single median **1.67** (q1 1.42, q3 1.86, max 2.00 — the tightest range of any template);
  11/31 (35%) double column, and those go wide (max aspect 5.06).
- Median 238 shapes, 32 text boxes, and the **smallest palette of the seven at 5 colours** — a matrix
  reuses one colour vocabulary across every cell.

**Numbering and legend.** Steps on **10/31 (32%)** — no longer the lowest; `layered` now has the
lowest rate at 26% — a matrix has no inherent traversal order. Legend on **13/31 (42%)**: inside 7,
right 3, below 3. Because the same colour vocabulary repeats in
every cell, the legend is defined once, above (`asplos25-046_fig14`), below (`asplos26-142_fig4`) or
right (`osdi23-048_fig1`), and never per panel. Row and column headers are the primary labels; panel
letters `(a)`-`(f)` go under each cell.

**Main path and emphasis.** No path. Emphasis is a shaded row (`asplos26-019_fig1`'s "This Work"
row), a highlighted cell (`asplos25-046_fig14`), or a size difference between panels.

**Variants.**

- "small multiples of a layer stack annotated with feasibility icons" — `sosp24-007_fig7`
- "three-row before/prior-work/ours comparison diagram sharing the same prompt-to-image layout" — `asplos26-019_fig1`
- "N repeated identical columns feeding into one shared horizontal clearance band" — `osdi26-065_fig2`
- "three-column categorical breakdown with percentages and consistent color coding across columns" — `nsdi26-030_fig2`
- "small multiples (grid of near-identical sub-diagrams) showing successive steps of a physical process" — `asplos26-142_fig4`
- "rank-by-rank grid contrasting a replicated component against a per-rank-unique component" — `asplos25-082_fig1`
- "three-panel side-by-side hardware architecture comparison with numbered communication paths reused as labels throughout the paper" — `osdi23-048_fig1`

**Pitfalls.** dense/small text **17**, legend placement 2, overlap/alignment 2, unexplained
colour/icon 1, abbreviations/notation 1, print/greyscale risk 1, extreme aspect ratio 1, raster
content 1 — 26 weakness-cluster matches across the 31 figures (0.84 per figure, close to the corpus
mean of 0.80). The named failure is "legend is small and
placed away from the grids it explains". Second: a matrix whose cells are not actually comparable —
if the cells have different internal structures, use `two-panel` or `overview-with-inset` instead.

**Exemplars** (`assets/exemplars/matrix/index.json` lists all 29; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-004_figtex9` | Stack design-space alternatives as rows sharing one identical column skeleton so only the boxes that differ stand out, and put a compact legend inside the frame when colour marks buffer location and line style marks timing; the record warns that reusing one generic label for different colours invites confusion. |
| `asplos25-031_fig9` | Use one consistent colour-and-shape legend across a graph panel, a physical tile-grid panel, and a zoomed detail panel so a single leader line walks the reader from an abstract motif to the exact hardware block executing it; keep leader lines from crossing an unrelated middle panel, a flaw the record flags here. |
| `asplos25-046_fig14` | A matrix can have zero arrows: cells carry the state, the legend above defines cell colours, and one highlighted cell carries the point. |
| `asplos25-069_fig1` | Arrange a problem-then-solutions matrix as a top row stating the mismatch and a bottom row of lettered panels comparing candidate fixes, define component colours once in a shared legend at the right edge, and let one bold callout arrow, not a whole panel, carry the gap argument. |
| `asplos25-082_fig1` | When the point is which state is shared and which is per-instance, drop arrows entirely and let identical fill colour across a row say replicated while a distinct colour per row says unique per instance, repeating the same row layout in a second panel for a related kind of state. |
| `asplos25-132_fig5` | Build the grid so every cell keeps the identical buffer sketch and only the highlighted arrow colour and an enable/disable label change between cells, and put the one legend below the whole grid rather than repeating it per cell; six dense cells plus a separate schematic is already a lot, so keep individual cells sparse. |
| `asplos26-021_fig8` | Use a matrix of identical tile cells to depict physical placement of replicated hardware around one shared control block, and zoom from a single selected cell into an exploded detail panel rather than expanding every cell, keeping the grid itself uncluttered. |
| `nsdi26-030_fig2` | For a measurement taxonomy, use column headers as the schema and keep row colour constant across columns so categories track visually. |
| `nsdi26-143_fig1` | Panel size is an argument: keep baselines schematic and give the contribution the detail budget. |
| `osdi25-007_fig5` | Put the row categories once in a left-hand gutter shared by every column, use a dashed empty box to mean no interface exists here rather than omitting the cell, and recolour only the one column that is the paper's contribution to argue its analogy to an accepted precedent. |
| `osdi26-065_fig2` | Column-per-instance over a full-width shared band is the layout for 'per-X mechanics feeding one global step'; the dashed band border marks where they merge. |
| `sosp23-037_fig2` | Keep row labels in one left gutter shared by every column so structural simplification reads at a glance from box count alone; the record warns that a highlight colour used on only two small icons is easy to miss, so give an important cue more than a token-sized swatch. |
| `sosp24-024_fig4` | Assign each quadrant of a 2x2 grid its own colour family and its own subsection number so the reading order is announced by the numbers rather than position alone; many similar pastel colours without a legend get hard to tell apart at this density, so keep quadrant palettes visibly distinct. |
Starred 13 of 29; the other 16 are in `index.json` with one-line notes.
Starred 13 of 29; the other 16 are in `index.json` with one-line notes.

---

### 7. `host-device` — 47 figures (6%)

Two asymmetric sides — CPU/GPU, host/SmartNIC, client/server, real/simulated — separated by a named
interconnect.

```
 ┌──────────── Host ────────────┐
 │  ┌──────┐        ┌────────┐  │
 │  │ app  │        │ driver │  │
 └──────────────────────────────┘
 ══════ PCIe MMIO / DMA ══════════   <- named interconnect band
 ┌─────────── Device ───────────┐
 │  ┌──────┐        ┌────────┐  │
 │  │ core │        │  mem   │  │
 └──────────────────────────────┘
```

**When to use.** `depicts` = whole-system architecture 33/47 (70%), one subsystem 7, one path/request
flow 5, deployment 2. Abstractions: hardware 16, distributed 12, network 7, kernel 3 (no longer spread
evenly — hardware and distributed now dominate). Component count median **11** (q1 10, q3 14, min 5)
— tied with `control-data` for the highest *minimum* of the seven: this template needs at
least ~5 components to be worth the split. Choose it when two sides have different capabilities and
the interconnect between them is part of the argument.

**Arrangement.**

- Direction: **left-right 20/47 (43%)**, mixed 14, top-down 12. Left-right for client|server or CPU|GPU;
  top-down when the boundary is a stack boundary (`asplos25-167_fig1`).
- **The interconnect gets its own full-width band or lane**, labelled with its name and often its
  bandwidth ("NVLINK-C2C (900GB/s)", "PCIe MMIO/DMA"). It is a row, not an arrow.
- Mirror the two sides: the same tier count, same box heights, ideally the same module names where
  they exist on both sides.
- Nesting depth 3 in 27/47, 2 in 19. Lanes only 14/47 (30%).
- Aspect: single median **1.75** (q1 1.37, q3 1.99, max 3.69); 8/47 (17%) double column (aspect
  1.78-5.73, median 3.27).
- Text density leans healthier than average — **moderate 23, dense 20, sparse 4** — though
  host-device is no longer the only template where moderate outnumbers dense (`layered` and
  `control-data` do too, and `hub-spoke` ties). The group logs **34 weakness-cluster matches across
  47 figures — 0.72 per figure against a corpus mean of 0.80** — no longer the cleanest of the seven;
  `layered` now holds that spot at 0.67 per figure.

**Numbering and legend.** One of the most annotated templates: **legend on 18/47 (38%)** — second
only to `matrix` at 42% — (inside 9, below 5, right 4) and **step markers on 25/47 (53%)**, the
highest of the seven (circled-numbers 15, labelled-arrows 7, letters 3). Both rates are well above
the corpus average, because a two-sided figure has to say which side does what and in what order.
Side names are bold headers on each side's container.

**Main path and emphasis.** The main path crosses the boundary; number it, and let the numbering run
through a zoom if there is one (`asplos25-107_fig6`'s steps 1-6 span both the machines and the
zoomed SSD). Emphasis is the side (or the crossing) that the paper changes.

**Variants.**

- "layered host/device diagram split by an interconnect band in the middle" — `asplos25-167_fig1`
- "host-device split diagram with a labeled high-bandwidth interconnect in the middle and per-side optimization boxes" — `asplos26-014_fig5`
- "offline/online two-phase architecture with an explicit icon legend" + "host-device split connected via PCIe" — `sosp24-035_fig7`
- "client-server-storage system diagram with a numbered end-to-end data flow and an inset pseudocode box" — `asplos25-107_fig6`
- "GPU/CPU memory split annotated with a within-device vs. cross-device (PCIe) arrow legend" — `osdi25-031_fig6`
- "stacked container cards feeding a separate simulator box via color-coded event arrows" — `nsdi26-087_fig3`

**Pitfalls.** dense/small text **10**, relies on caption/body text 5, unexplained colour/icon 4,
repeated/duplicate labels 4, legend placement 3, abbreviations/notation 2, print/greyscale risk 2,
extreme aspect ratio 2, raster content 2 — 34 weakness-cluster matches across the 47 figures, spread
across more clusters than before: "nearly monochrome palette gives no color cue to distinguish
component types" (`asplos25-167_fig1`), "left context panel is visually disconnected from the main
diagram without an explicit linking arrow" (`osdi25-031_fig6`). The remaining risks are structural
rather than observed: an unnamed boundary (draw the band, name the protocol), asymmetric tier counts
that imply a hierarchy you did not intend, and putting the interconnect's bandwidth in the caption
instead of on the band.

**Exemplars** (`assets/exemplars/host-device/index.json` lists all 29; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-051_fig4` | When the interconnect is itself hardware worth showing, draw it as literal cabling with named ports (P0/P1) instead of a plain arrow, and mirror three color-coded node boxes (compute, switch, memory) with the same internal tier stack so the reader can compare them at a glance. |
| `asplos25-132_fig4` | Color each tile type in a heterogeneous accelerator mesh by function (red, gold, gray) so the reader sees the mix at a glance, and use dashed insets to zoom into one tile's internal datapath; cap the insets at one or two, since three competing zooms in this figure fight the main diagram for attention. |
| `asplos25-167_fig1` | Mirror the two sides around a named interconnect band; the band is a full-width row, not an arrow. |
| `asplos26-067_fig3` | Give two heterogeneous host domains their own protocol color (pink, purple) that stays constant from their private caches up to the shared bridge, draw the bridge as one dashed band straddling both domains rather than a separate box, and number every request/response arrow even though this traversal runs bottom-up. |
| `asplos26-100_fig3` | Color the device you are contributing green and the host structures it modifies yellow so the split is legible at a glance, then key each of its many wires into the host (pipeline, register file, CSRs, memory arbiter) with a letter cross-referenced in prose rather than crowding the figure with a legend. |
| `nsdi24-062_fig5` | Number every module consistently (M1-M5) so prose and figure cross-reference cleanly, dash exactly the one path the text calls asynchronous while keeping the main forwarding path's arrows solid, and put the two-or-three-color arrow legend inside the boundary box it explains rather than off to the side. |
| `nsdi26-021_fig10` | Mirror sender and receiver by swapping the internal order of their shared sub-boxes (Bifrost/AVS becomes AVS/Bifrost) so the drawing itself shows the protocol is symmetric, and key numbered steps to named optimizations plus a packet-format strip in one shared middle panel, accepting the reader must glance away from both diagrams to read it. |
| `nsdi26-087_fig3` | When the two sides exchange several kinds of event, encode the kind in arrow colour and put the legend above the whole figure. |
| `osdi24-034_fig6` | Put a small boxed legend that names dashed as the management path and solid as the data path, then honor it everywhere: dashed for the host-side software containers, solid for the on-chip hardware, and color the two traffic directions (blue send, red receive) only where they physically cross at the net port. |
| `osdi25-031_fig6` | At double column, stack GPU memory over CPU memory on the left and run the numbered mechanism left-to-right across both. |
| `osdi26-020_figtex7` | Circled numbers can be an index into a legend list instead of a temporal order; say which by where the numbers point. (No PDF-extracted print.png; TeX-only figure.) |
| `osdi26-040_fig6` | Tag two mechanisms that must be read together, one on the host side and one on the device side, with the same paper-section number and fill color so the eye links them without an arrow; don't leave a named band like Control Plane empty, or its role stays implicit as it does here. |
| `sosp25-002_fig1` | Give the interconnect itself a named box (Interconnect Simulator) between the two color-coded zones instead of a bare arrow, and label the crossing arrows with the actual interface name (MMIO Read/Write, DMA); but unlike here, draw an arrow, not just vertical adjacency, when one box is said to run inside another. |
Starred 13 of 29; the other 16 are in `index.json` with one-line notes.
Starred 13 of 29; the other 16 are in `index.json` with one-line notes.

*(A residual `other` bucket holds 77 figures. The 2026-09-07 type-discovery pass mapped those figures
onto templates I-M (`n-panel-comparison`, `composite-figure`, `mirrored-pair`, `flanked-core`,
`block-floorplan`) and onto variants of the added templates. Two of them are used as exemplars below —
`osdi26-018_fig7` under `baseline-vs-ours` and `sosp25-015_fig2` under `nested-stack`.)*

---

## Added templates

Thirteen patterns the corpus uses repeatedly but that its own taxonomy (the seven core ids plus an
`other` bucket) does not name. Each is
either a *modifier* on a core template (`overview-with-inset`, `replicated-grid`, `nested-stack`,
`control-loop`, `phase-lanes`) or a *sharper version* of one (`baseline-vs-ours` ⊂ two-panel/matrix,
`multi-tier` ⊂ layered, `dataflow-dag` ⊂ pipeline). Evidence counts come from text search over each
figure's summary, key idea, reading order, reusable patterns, tags, caption and encoding fields
(`layout_stats.py --section enriched`); a figure can match more than one.
Templates **I-M** were added on 2026-09-07 after the semantic backfill reached all 727 good architecture
figures: the 84 `other` records and 86 loose-fit records were reviewed by eye and grouped
(`scripts/distill/type_discovery.json` lists every assignment). All counts in this file are over the
727-figure corpus (statistics refreshed 2026-09-07).

### A. `nested-stack` — containment as the layout

**307/727 figures (42%) have nesting depth ≥3** (273 at depth 3, 31 at depth 4, 3 at depth 5); by core
template: layered 90, pipeline 59, two-panel 39, control-data 35, other 30, host-device 28, hub-spoke 19,
matrix 7.

Distinct from `layered` (tiers stack, they do not contain) and from `overview-with-inset` (the detail
is drawn *outside* and connected by leaders). Here the boxes are literally inside each other:
chip ⊃ core ⊃ unit, memory ⊃ buffer ⊃ region, cluster ⊃ node ⊃ process.

```
 ┌─ System ────────────────────────────┐
 │  ┌─ Engine ──────────────────────┐  │
 │  │   ┌─ Unit ──┐   ┌─ Unit ──┐   │  │
 │  │   │  ┌───┐  │   │  ┌───┐  │   │  │
 │  │   │  └───┘  │   │  └───┘  │   │  │
 │  │   └─────────┘   └─────────┘   │  │
 │  └───────────────────────────────┘  │
 └─────────────────────────────────────┘
```

**Rules.** Change exactly one visual property per level — tint, border dash, or padding — and never
all three. Shrink text by at most one step per level (7.5 → 6.5 → 5.5 pt), which caps the practical
depth at 4; the 34 figures at depth ≥4 are mostly distributed (11), hardware (6) and network (5) systems. Keep inner
padding constant (2-4 pt) so the levels read as containment, not as decoration. Direction is
irrelevant: **arrows are optional** — `sosp25-015_fig2` has 11 components and 0 flows. Reserve the
accent fill for the innermost novel unit. When four levels will not nest legibly, stack them as
lettered drill-down panels instead (`asplos25-043_fig5`).
Containment can be the *entire* frame: host ⊃ daemon ⊃ library with the inputs and outputs outside
the outer box (`sosp25-048_fig4`), a legend-coloured container split into dashed sub-regions
(`sosp24-017_fig1`), or a device box nested inside a host canvas and wired outward
(`nsdi26-028_fig3`, `nsdi26-142_fig4`).

**Exemplars** (`assets/exemplars/nested-stack/index.json` lists all 29; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-012_fig2` | Nest a sparse sub-block, router plus experts, one level inside the standard block it replaces so the substitution is visible as containment, and show which inner sibling was actually chosen with a bold solid arrow while untaken siblings keep only a dashed candidate arrow. |
| `asplos25-052_fig5` | Repeat the identical three-level column, agent over monitor-and-model, exactly N times for N replicated learners, and mark a box that is a logical tracking structure rather than a physical component with a dashed border, one level inside the shared infrastructure box it belongs to. |
| `asplos25-074_fig7` | Nest each contribution two levels deep inside its own dashed accent box carrying its section number, rather than flattening everything to one depth; keep the same dashed-border-plus-number treatment at every nesting point so a reader recognizes a paper's own module regardless of depth. |
| `asplos25-080_fig1` | Mirror the identical three-level containment, host box over processor core over program code and local APIC, on both communicating parties, and number the steps once across the whole nested structure so the sequence reads correctly despite duplicate box labels on each side. |
| `asplos25-146_fig3` | Make the outermost container a dashed logical grouping rather than a drawn system boundary, and change only the fill tint between nesting levels, dark-blue title bar to light-blue body, instead of also changing border style, keeping three levels of depth visually calm. |
| `asplos26-088_fig12` | Draw each level once, connect levels with dashed leaders, and reserve the accent fill for the innermost novel unit. |
| `nsdi23-047_fig4` | Repeat the identical three-level containment, machine over CPU-or-GPU over its inner engine or worker, in two side-by-side mirrored boxes rather than describing the replication in text, and keep one consistent fill per role across both copies so the eye reads them as the same structure twice. |
| `nsdi23-085_fig8` | Keep a replicated container's internal stack, scheduler over executors over object store, identical in both copies, and reserve one flat colour per role so containment reads correctly without a legend; let the outer dashed border, not colour, be the property that marks one node. |
| `nsdi25-054_fig2` | Use a dashed wrapper box to show an isolation boundary around the code it contains, and let a second dashed box one tier down hold the shared internal state that every parallel sibling box above it depends on, keeping padding consistent at both nesting points. |
| `nsdi26-109_fig3` | Nest a paper's own small contribution box one level inside its host's generic runtime box rather than drawing it as a sibling, and represent an internal data structure like a free list literally as a ring with Head and Tail pointers instead of a plain rectangle. |
| `osdi23-008_fig2` | Nest per-item boxes, one Performance Model per job, inside the shared learner container that produced them, and pick out the single configurable piece with its own inner accent-filled box one level deeper than its parent. |
| `osdi24-025_fig6` | Put the tier name in a left gutter even while nesting sub-boxes inside it, and mark a box that stands for many running copies with a stacked-rectangle offset icon behind it rather than drawing every instance, keeping that as the one extra property at that nesting level. |
| `osdi24-034_fig6` | Carry one indirection chain, table entry to resource, as boxes nested or linked one inside the next rather than a flat row, and put a boxed legend decoding dashed-versus-solid line meaning directly in the frame when both a management path and a data path are drawn. |
| `osdi24-041_fig3` | When one side of a two-panel figure is actually a deep hierarchy, let it nest, GPU pool over batching over base model over per-request adapters, while the other panel stays shallow; use one accent colour only for the cross-cutting controller that ties both panels together. |
| `osdi25-016_fig8` | Four levels only stay readable if each level changes exactly one visual property (fill tint, border dash, padding) and text shrinks by at most one step per level. |
| `osdi26-060_fig8` | When colour is not available to mark nesting, use shading depth alone, each level of containment one shade darker or lighter than its parent, and keep the innermost pair of boxes the same size so the reader reads them as siblings at the same depth. |
| `sosp23-013_fig3` | Nest a sub-engine's own two named components one level inside it rather than listing them beside it, and mark the one instance under discussion, a failing node, by swapping only its border to a red dashed line while every other repeated group keeps a plain solid border. |
| `sosp24-011_fig8` | Give every repeated leaf box, here each Executor, the same small inner icon grid so per-worker internal state reads identically across the row, and reserve the one exception, a red dashed outline on the failed Executor, for exactly the box that differs. |
| `sosp25-015_fig2` | A containment figure needs no arrows at all; repeat the innermost box in a grid to convey count, and magnify one instance for its contents. Note: the print.png carries the paper title line from PDF extraction; preview.png is clean. |
| `sosp25-035_fig1` | Wrap a replicated pool in its own labelled sub-box one level inside the service that owns it, rather than drawing the instances loose in the parent box, so containment alone tells the reader the pool is one interchangeable unit, not several separate services. |
| `sosp25-064_fig5` | Split a shared allocator into side-by-side same-shape sub-pools, each nesting the identical three-state vocabulary, free, allocated, failed, so the two resource types stay visually parallel, and reserve one bold colour for the control-path arrows leaving the whole nested block. |
Starred 21 of 29; the other 8 are in `index.json` with one-line notes.
Starred 22 of 29; the other 7 are in `index.json` with one-line notes.

### B. `baseline-vs-ours` — the contrastive comparison

**76/727 figures depict `comparison`** (two-panel 35, matrix 16, other 16, pipeline 4, layered 4,
control-data 1); **24/727 (3%)** carry explicit baseline-vs-ours phrasing (two-panel 14, pipeline 3,
other 3, matrix 2, control-data 1, layered 1). `depicts`: comparison 16, one subsystem 4,
whole-system 3, path 1.

A sharper contract than plain `two-panel`: the panels are not merely two things, they are *the same
thing under two designs*, and the figure's job is to make one difference unmissable.

```
 (a) Baseline                    (b) Ours
 ┌──────────────────┐            ┌──────────────────┐
 │ A → B → C → D    │            │ A → B ═> D       │
 │        ✗         │            │      saved       │
 └──────────────────┘            └──────────────────┘
 └──── same anchor box ────┘  └──── same anchor box ────┘
```

**Rules.** (1) Identical skeleton in both halves; (2) one anchor component identical and in the same
position; (3) exactly one difference, marked — a red ✗, a bracket over the saved interval, a shaded
ground under your half; (4) name the halves by *claim* ("Now: Library+Sidecar" / "Our Vision"), not
by system name; (5) if the halves are wide, stack them and put a bold `V.S.` or a horizontal rule
between; (6) N > 2 is allowed — Baseline / Prior work / Ours as three rows
(`asplos26-019_fig1`) or three stacked panels (`osdi26-018_fig7`). Legend, if any, spans both halves.
Numbering rate for `depicts=comparison` figures is 42% (32/76), usually to enumerate the
optimisations in your half only.

**Exemplars** (`assets/exemplars/baseline-vs-ours/index.json` lists all 16; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-052_fig1` | When only one of two panels carries the actual contrast, use labelled brackets plus a single highlight colour on the winning option inside that panel; but add a legend for the highlight color, since dropping it (as this figure does) leaves the meaning of the yellow fill unstated. |
| `asplos25-055_fig1` | Reuse the exact processor-block icon across both panels and add a small pictogram (a pickaxe) only on the box that changes, rather than redrawing the whole unit; pair dashed and dotted line styles to distinguish the ISA-level and microarchitecture-level check paths, and add a legend for the icons since none is given here. |
| `nsdi23-004_fig1` | Keep the client/app/kernel/NIC stack identical and in the same position in both panels, then let small repeated icons (the M/U marshal circles) along a bottom trace let the reader literally count the efficiency win; note the weakness that placing the legend far above the trace it explains hurts lookup. |
| `nsdi26-053_fig1` | Put a single legend of small coloured icons above all panels so it covers both the contrasted (a)/(b) topologies and a third detail panel; keep the icons visually distinct, since this figure's weakness is several similar small icons that need close reading. |
| `nsdi26-143_fig1` | Stack the baseline variants smaller on one side and draw the proposed design larger on the other; use two named link colors (brown for intra-island, navy for inter-island) labelled directly on the drawing instead of a separate legend. |
| `osdi23-003_fig4` | Keep sender icons, RNIC box, and the receive-buffer/CQ layout in the same position in both panels; mark the single failure point with a red X in the baseline panel, and let the working buffer geometry in the ours panel be the only visual difference. |
| `osdi23-050_fig4` | Repeat the loop-plus-kernels skeleton in both panels, but colour only the anchor box that changes (the separate CPU Loop) so the eye finds the fix immediately; add a small legend mapping the multi-level L0/L1/L2 hardware boxes back to the simple CPU/accelerator split in (a), a step this figure skips. |
| `osdi25-016_fig1` | Read this as a hub-with-fan-out figure instead: put the shared IR at the visual center with 'Semantic' and 'Metrics' callouts, contrast it against the disconnected prior-art pipeline on the left, and fan one Enables arrow out to three dashed example-tool boxes on the right rather than forcing any of it onto a time axis. |
| `sosp23-011_fig3` | Repeat the same privilege-level scaffold (L2/L1/L0) in identical positions in both panels and number the steps in both halves symmetrically, not just one; but cap step markers well below 32 total, since this figure's density makes the two mechanisms hard to compare at a glance. |
Starred 9 of 16; the other 7 are in `index.json` with one-line notes.
Starred 11 of 18; the other 7 are in `index.json` with one-line notes.

### C. `overview-with-inset` — zoom callout

**131/727 figures (18%)** describe a zoom, inset or callout, spread across every core template
(pipeline 35, layered 29, two-panel 20, other 20, control-data 8, matrix 7, hub-spoke 7,
host-device 5). `depicts`: whole-system 69, one subsystem 37, comparison 11, path 11, deployment 3.

```
 ┌───────────────┐        ┌ ─ ─ ─ ─ ─ ─ ─ ─ ┐
 │ ┌──┐ ┌██┐ ┌──┐│ ─ ─ ─   detail of ██
 │ └──┘ └██┘ └──┘│  ─ ─ ─ │ ┌───┐ ┌───┐     │
 │ ┌──┐ ┌──┐ ┌──┐│        │ └───┘ └───┘     │
 └───────────────┘        └ ─ ─ ─ ─ ─ ─ ─ ─ ┘
   overview                inset (dashed border)
```

**Rules.** The inset lives **outside** the overview and never overlaps it. Mark the source region in
the overview first (different border weight or fill), then connect with **two dashed leader lines**
from the region's corners to the inset's corners — this is the single most consistent convention in
the corpus, and dashed-for-containment must not collide with dashed-for-control in the same figure.
Give the inset a dashed border and its own title. Carry the accent colour across the boundary so the
same component reads as the same component at both scales (`asplos25-108_fig5`). At most **one**
inset per figure at single column, two at double column; three or more levels should become a chained
`(a)`→`(b)`→`(c)` panel sequence (`asplos25-157_fig2`, `asplos25-100_fig3`). Numbering may run
through the boundary (`asplos25-107_fig6`).
Three more shapes from the 727-figure corpus: **exploded stage** — one stage's internals drawn at full
size *beside* the pipeline, joined by a dashed wedge (`osdi24-046_fig2`, `osdi26-071_fig3`);
**annotation rail** — a stack or pipeline with a right-hand column of note boxes, one per tier, joined
by leaders or simple alignment (`osdi23-052_fig1`, `nsdi25-030_fig3`); **format inset** — a packet
header, record layout or formal model drawn as a small framed panel next to the architecture that
produces it (`nsdi26-041_fig2`, `asplos26-096_fig1`, `osdi24-046_fig11`).

**Exemplars** (`assets/exemplars/overview-with-inset/index.json` lists all 19; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-039_fig3` | Chain three different kinds of panel left to right (control logic, then a topology graph, then one zoomed node) rather than forcing one drawing to hold all three, and put a single legend below spanning all of them since node colour and the layer icon both need explaining. |
| `asplos25-100_fig3` | Progressive expansion left-to-right suits background/context figures; dashed brackets mark the xN repeated block so the expansion stays finite. |
| `asplos25-101_fig1` | A background/definitions figure can carry a small inset inside just one of several panels: zoom the repeated-block stack (Decoder 1...N) into its four internal kernel stages with a single dashed line, and leave the timeline panels beside it in a separate, unconnected visual grammar. |
| `asplos25-107_fig6` | Put the new instruction's pseudocode in its own framed inset below the architecture rather than inline in a box, connect it to the component that executes it, and keep the six circled step numbers running through both the main flow and the client/server/SSD colour bands. |
| `asplos25-108_fig5` | Carry the accent colour across the zoom boundary so the same component reads as the same component at both scales. |
| `asplos25-147_fig2` | Give every stage in a vertical pipeline its own small thumbnail icon of the concrete data structure it outputs, aligned in a right-hand rail, so an abstract stage name (Graph Contraction, Wavefront Scheduler) is anchored to a picture rather than left purely verbal. |
| `asplos25-157_fig2` | Chained zoom: each panel's leader lines start at a marked region of its predecessor, so the reader can follow core -> array -> cell without a caption. |
| `asplos26-021_fig8` | Highlight the source tile in the grid (different border/fill) before drawing the callout, so the reader knows which of the N tiles was expanded. |
| `asplos26-076_fig2` | For a hardware hierarchy with 3+ magnification levels, chain (a)(b)(c) panels left to right instead of one hub-spoke drawing, carry one highlight device across the boundary (the red X marking a bypassed core in (b), traced to a blue-outlined core in (c)), and let the mesh inside one panel, not radiating spokes, show replication. |
| `asplos26-094_fig9` | When lettered sub-panels each show a different, unique circuit block rather than the same block under different conditions, treat the figure as an overview with several distinct insets, not a comparison; keep one consistent colour-phase code (as this figure does) so each inset still maps back to its place in the main dataflow. |
| `nsdi25-033_figtex7` | When the thing you need to explain is a data-driven decision rather than a drawn component, inset an actual chart (a heatmap, a Pareto curve) next to the architecture instead of forcing it into a box; keep the figure's own colour-coded example queries walking through both the diagram and, implicitly, the chart's axes. |
| `nsdi26-054_fig1` | Zoom from a layer-level pipeline down into one layer's per-GPU detail below it, and spend your one accent colour (red) only on the operation the paper is actually about, so it reads as the reason for the whole figure rather than one more box. |
| `osdi25-003_fig2` | Mark the exact source of a zoom (one pipeline stage) before expanding it, and keep colour consistent across the boundary (navy/blue on the left reappears inside the right-hand CP/TP detail); budget bigger type than this exemplar did, since its own weakness is text too small for four nested levels. |
| `sosp24-035_fig1` | Insets sit outside the overview and connect back with dashed leader lines from the exact sub-box they expand - never overlap the overview. |
| `sosp25-015_fig2` | Colour-code each level of a hardware hierarchy consistently (yellow memory, blue TPC, orange SM, green SM-internals) from the overview straight into the magnified callout, so the reader never loses track of which level of the zoom they are looking at. |
Starred 15 of 19; the other 4 are in `index.json` with one-line notes.
Starred 16 of 20; the other 4 are in `index.json` with one-line notes.

### D. `control-loop` — an explicit cycle

**64/727 figures (9%)** describe a feedback loop, closed loop or return arrow (pipeline 27,
control-data 12, layered 8, hub-spoke 6, two-panel 6, other 4, host-device 1). `depicts`:
whole-system 46, path 9, subsystem 8, comparison 1.

```
   ┌───────┐    ①    ┌────────┐
   │ sense │────────>│ decide │
   └───▲───┘         └────┬───┘
       │ ③              ② │
       │            ┌─────▼───┐
       └────────────│   act   │
                    └─────────┘
```

**Rules.** Three shapes the corpus uses, in order of preference:
(1) **straight pipeline + one labelled return arrow** along the opposite edge — cheapest and clearest
(`asplos26-152_fig5`, `asplos26-028_fig2`); (2) **triangle/ring of 3-5 boxes** with numbered arrows
(`asplos26-080_fig5`, `nsdi24-043_fig1`); (3) **an optimizer box hanging off the side** that feeds
back into the spine (`osdi23-045_figtex1`, `asplos25-131_fig2`).
Always label the return arrow with **what it carries** ("the updated configuration", "performance
metrics"), never with "loop". Give the return path a distinct weight or colour so it is not read as
another stage. Number the cycle — control-loop figures number at a high rate because the loop has no
natural start otherwise. Separate one-time setup from the repeating loop with a group boundary and
number only the loop (`asplos26-132_fig6`).
A fourth shape, frequent in the 727-figure corpus: **an open pipeline feeding a boxed loop** — the
preprocessing stages run left-to-right into a container labelled as the loop, and only the container
carries return arrows (`sosp24-028_fig2`, `nsdi26-098_fig6` with a Stop? decision, `asplos26-125_fig4`
with an iterative scheduler core, `nsdi25-039_fig7` two engines handing a plan back and forth). A
pipeline whose every stage also touches a backward-flowing ring is drawn as two parallel rails, not as
N return arrows (`nsdi24-031_fig1`).

**Exemplars** (`assets/exemplars/control-loop/index.json` lists all 24; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-052_fig5` | When N identical agents each close their own loop with a shared hub, label both arrow directions distinctly (Actions down, Reward up) on every column rather than drawing one generic pair and implying the rest, and use a dashed border for a logical/tracking structure like the ghost superblock manager that is not a hard component. |
| `asplos25-131_fig2` | Put section numbers (Sec 3, 4.1...) in a left-margin gutter beside each stage band so the figure doubles as a map to the text, and give the return-to-scheduler arrow its own path along the right edge rather than overlapping the forward flow. |
| `asplos26-028_fig2` | At extreme width, run the forward path along the top edge and the backward path along the bottom edge of the same strip. |
| `asplos26-080_fig5` | A three-box loop needs no ring: place the boxes at triangle corners and number the arrows so the traversal order is unambiguous. |
| `asplos26-113_fig8` | Arrange more than 3-4 loop stages in a serpentine two-row layout instead of forcing a single wide ring, numbering each box (5.1-5.5) in reading order, and mark automatic accept/reject decisions inline with a green check or red cross rather than a separate results table. |
| `asplos26-132_fig6` | Put one-time setup in its own dashed container above the repeating loop and number only the loop's steps (here 1-4), not the setup; give shared dependencies (the training simulator both stages use) a distinct dotted style, but make it heavier than this figure's, whose light dotted 'uses' lines are easy to miss. |
| `nsdi23-025_fig4` | Embed a small inset chart (throughput vs load) beside the arrow it drives so the feedback signal is visible, not just implied, and give every drop point its own icon; route each to its own arrow rather than merging two distinct drop points into one dashed line, which here can read as a single point. |
| `nsdi24-004_fig8` | Use small coloured squares as tokens for orientations so rank order and selection show through colour and position, not labelled boxes, and draw both the fast local loop and the slower cross-tier retraining loop as separate labelled arrows; enclose grouped tokens in a light box, since unboxed grouping here is easy to misread. |
| `nsdi24-043_fig1` | Draw the cycle as a ring of boxes around the perimeter and give the return path its own distinct colour/weight so it does not read as another stage. |
| `nsdi24-095_fig2` | Draw an internal recurrent feedback loop (GRU to Memory and back) as a curved dashed arrow distinct from the straight solid feed-forward arrows around it, and put a legend below the figure naming any abbreviation (STE) the first time a coloured step appears. |
| `osdi23-008_fig2` | Label both halves of a loop with what they carry, not just the fact of a return path: 'Per-Job Feedback' going one way and 'Resource Allocations' the other, so a two-box optimizer-beside-the-spine loop reads correctly without needing numbers. |
| `osdi23-039_fig3` | Draw a dotted boundary around your own system's box to separate it from the off-the-shelf tools and inputs/outputs surrounding it, and confine the return arrow to the one internal stage that actually repeats (Refine back to Compute) rather than looping the whole pipeline. |
| `osdi23-045_figtex1` | Accent-colour only the box that closes the loop; the dashed system boundary then separates 'what we built' from the platform it runs on. |
| `sosp23-006_fig3` | Trace one concrete input change (the red-highlighted replica diff) all the way through the system, and use a small self-loop icon inside a controller box to mean 'reconciles repeatedly' instead of a full drawn cycle; but this figure's ellipsis boxes elide most of the actual loop, so show at least one full traversal too. |
| `sosp24-005_fig4` | Number every arrow in the server-client cycle in one continuous sequence, even where it re-enters the server (step 4's straggler notification), and colour the two tiers distinctly (blue server, green client) so the reader always knows which side owns each step. |
| `sosp24-028_fig2` | Bound the repeating search region with a shaded grey box labelled 'feedback loop' in plain words rather than leaving the reader to infer it, and give the iterative arrows a distinct thin bright colour against thick grey one-shot data arrows so the two kinds of flow never get confused. |
| `sosp25-032_fig4` | Split the spine into two colour-coded parallel paths (compute vs communication engines here) and hang the rebalancing controller underneath both, connected by double-headed arrows rather than a single looping line, when the feedback is continuous rebalancing rather than a discrete numbered cycle. |
Starred 17 of 24; the other 7 are in `index.json` with one-line notes.
Starred 17 of 22; the other 5 are in `index.json` with one-line notes.

### E. `phase-lanes` — swimlanes and timelines

**38/727 figures (5%)** describe a timeline, time axis, Gantt or swimlane (two-panel 10, pipeline 9,
other 9, layered 4, control-data 3, matrix 2, host-device 1); separately **286/727 (39%)** carry
`lanes: true`. `depicts`: whole-system 14, path 9, comparison 9, subsystem 6.

```
            │  phase 1  ┆  phase 2  ┆  phase 3
  lane A    │ ▓▓▓▓      ┆   ▓▓▓▓▓   ┆  ▓▓
  lane B    │   ▓▓▓▓▓▓  ┆ ▓▓        ┆    ▓▓▓▓
  ──────────┴───────────────────────────────────>  Time
```

**Rules.** Lanes (**who**) run horizontally with names in one gutter; phases (**when**) are dashed
vertical rules with headers above or brackets below. The two never share a visual device. One
horizontal `Time` arrow under the lanes; do not put a second axis on the figure. Blocks are aligned
to a common grid so vertical alignment means simultaneity — that is the whole point, and it is why
the timeline goes **directly under** the architecture it explains, column-aligned
(`asplos25-082_fig3`). Two to three lanes is the practical limit at single column
(`asplos26-088_fig14` uses 2, `sosp24-041_fig1` uses 3). Blank cells are meaningful — they show
pipeline fill and idle time, so do not compress them away. Compress the *middle* with an ellipsis if
you must, and accept that exact proportions are then lost (a recorded weakness on
`asplos26-088_fig14`).

**Exemplars** (`assets/exemplars/phase-lanes/index.json` lists all 22; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-082_fig3` | Stack the timeline directly under the architecture and align columns so a block on the timeline sits under the component that produced it. |
| `asplos25-094_fig6` | Expand only the phase that has interesting concurrency into lanes; the others stay as plain boxes. |
| `asplos25-100_fig9` | When only one stage of a bigger figure is genuinely sequential, don't force the whole thing into lanes: draw one small vertical time arrow beside the sequential boxes (Decoder 0, 1, 2...) and keep the rest of the figure as an ordinary architecture diagram. |
| `asplos25-101_fig1` | To contrast concurrency strategies, redraw the identical pipeline box two or three times and vary only how many token rows run through it in parallel, letting the row count itself, not new geometry, carry the difference between serial, batched, and speculative execution. |
| `asplos25-132_fig5` | When two execution modes need comparing across the same repeating rounds, draw a small Round-by-Round-times-Case grid instead of one long timeline, keep the same colored segments in every cell so the eye tracks what changes, and reuse one arrow color per data item (Block-1/2/3) to trace it across rounds. |
| `asplos26-013_fig13` | Draw the identical set of per-lane Gantt bars twice, once unbalanced and once rebalanced, so the reader compares idle-gap width directly instead of reading numbers; but keep labels at a readable size, since this figure's 2-3.5pt text is illegible without zooming. |
| `asplos26-036_fig8` | Expand only the one phase with interesting concurrency into a small lanes/Gantt device (rows for PL and D micro-batches, dashed sync lines, one Time arrow) nested inside a single box, rather than converting an entire control-loop figure into a timeline. |
| `nsdi26-052_fig7` | A phase-lanes device does not need boxes: a literal table works too, with each tracked item as a row (a lane) and each event time as a column (a phase); highlight the one row that matters (here, the earliest still-incomplete frame) instead of adding a separate callout. |
| `osdi26-020_figtex8` | Stack the before and after timelines directly on top of each other at the same horizontal scale, mark shared iteration boundaries with dotted verticals so the eye can compare like-for-like, number the optimization steps that shorten the new timeline, and close with one bracket that measures the total speedup. |
| `osdi26-043_fig1` | Name the lanes in a left gutter (Rollout Pool, Training Pool), keep every block aligned to one shared time grid so idle gaps are visible rather than compressed away, color the red idle blocks as the named defect ('Dependency Bubbles'), and put a measurement bracket under each timeline to state exactly what got shorter. |
| `osdi26-071_fig3` | Draw a coarse lifecycle timeline across the top, pick out the one stage your system owns in a distinct color, and drop a shaded wedge straight down from it into the detailed mechanism diagram, reusing numbered steps to walk sense-then-verify across a per-unit execution timeline inside that mechanism. |
| `osdi26-094_fig5` | Give each parallel scheduler its own named lane under one shared Time axis, mark exact insertion points on the Gantt blocks with tiny check/cross icons instead of prose, measure TTFT/TPOT as brackets directly on the bars, and draw a not-yet-existing lane as a dashed ghost copy to show elastic scale-out. |
| `sosp24-041_fig1` | Lanes (who) run horizontally with labels in one gutter; phases (when) are dashed vertical rules with brackets under the axis - the two never share a device. |
Starred 13 of 22; the other 9 are in `index.json` with one-line notes.
Starred 16 of 24; the other 8 are in `index.json` with one-line notes.

### F. `replicated-grid` — N identical nodes

**74/727 figures (10%)** describe replication with an ellipsis or "pool of / scale-out" language
(layered 17, pipeline 17, two-panel 10, control-data 9, other 9, hub-spoke 7, host-device 3,
matrix 2). `depicts`: whole-system 49, subsystem 13, comparison 5, path 5, deployment 2.

```
 ┌────────┐ ┌────────┐          ┌────────┐
 │ Node 0 │ │ Node 1 │   ⋯      │ Node N │
 │ ┌────┐ │ │ ┌────┐ │          │ ┌────┐ │
 │ └────┘ │ │ └────┘ │          │ └────┘ │
 └────────┘ └────────┘          └────────┘
 ╚══════════ shared resource ══════════════╝
```

**Rules.** Draw **two full replicas plus an ellipsis plus (optionally) the last one**; never three or
more concrete copies. Index them from 0 and label the last N or N-1 so the reader infers the range.
Three ways to signal replication, cheapest first: an **ellipsis** between two full boxes
(`sosp25-061_fig7`, `asplos26-060_fig8`), **offset stacked boxes** behind a single one
(`osdi24-050_fig6`, `osdi26-044_fig4`), and a **×N annotation** beside one instance
(`asplos25-100_fig5`'s "×16"). Replication belongs to exactly **one tier** — keep the tiers above and
below it singular, or the figure reads as N whole systems. Columns of replicas usually share a
resource band above or below them; that band is what makes the figure an argument rather than a list.
Use a dashed leader when you need to say something about one specific replica
(`osdi25-050_fig6`), or restyle one replica to mark a failure (`sosp23-013_fig3`).
**Coordinator over replicas** is the commonest frame in the 727-figure corpus: a scheduler / sequencer /
allocator row on top, N identical lanes (shards, workers, hosts) below it, and the resource band under
those; number the request in one lane only and let the ellipsis imply the rest (`osdi25-006_fig5`,
`sosp24-025_fig4`, `sosp24-022_fig4`, `osdi24-012_fig2`, `nsdi25-033_fig7`, `sosp25-064_fig5`).
Lanes that *converge* into one shared layer below (`sosp23-043_fig3`, `osdi25-007_fig2`) keep the
lanes equal-width and let the shared layer span them all.

**Exemplars** (`assets/exemplars/replicated-grid/index.json` lists all 25; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-012_fig2` | Nest two replication scales in one figure: an in-line ellipsis row (FFN 1, FFN 2, ..., FFN N) for experts inside a layer, and a background shadow stack for the layer itself repeating N times, then use dashed-vs-bold arrows from the router to show which single expert one example token actually takes. |
| `asplos25-036_fig3` | For a recursive/self-similar mechanism, draw the base stage full size and detailed, then draw the next stage smaller beside it repeating the same shapes, and elide any further recursion with a plain 'Stage N ⋯' label rather than nesting boxes indefinitely; label the one operator (here vector-matrix multiply) once in a foot legend. |
| `asplos25-046_fig14` | The transferable move is replicated-grid's: draw the same guaranteed-versus-oversubscribed split bar on every member, call out just one member's split in detail, then roll all members into one aggregate table below with the shared, scarce resource highlighted in its own colour, yellow for the oversubscribed pool here. |
| `asplos25-100_fig5` | For a very large, fixed replica count, skip the ellipsis and just draw one instance with a bold '×16' label beside it; keep the flow-type legend (inter-device solid black, intra-device solid blue, control dashed orange) inside the frame since it is what makes the single-device diagram legible. |
| `asplos26-060_fig8` | Replication lives in one tier only; keep the tiers above it singular so the figure does not read as N whole systems. |
| `asplos26-088_fig11` | Match the elision to the count: when a repeated unit list is long (sixteen sorting cores here), collapse it with an ellipsis, but when short enough to read at a glance (four rasterization cores), just enumerate every one, using dashed leader lines to expand either list beside the main diagram. |
| `nsdi23-047_fig7` | Replicas as columns share a horizontal resource above and below them; the legend then only needs to explain the link colours between columns. |
| `nsdi24-003_fig1` | Do not draw three or more full concrete replicas side by side as this figure does; collapse to two columns plus an ellipsis (or a Core N column) instead, while keeping its good idea of repeating the same colored Driver/Application/Monitoring bands identically in every column and fanning them back to one Aggregator. |
| `nsdi26-124_fig4` | Reserve lettered (a)(b)(c) tags for distinct panels, not for naming different arrow or relationship types inside one diagram, which just needs a legend instead; draw N simultaneous identical peers (here three pods) as a repeated unit feeding one shared control plane below a dashed divider, replicated-grid's job, not a panel-by-panel comparison. |
| `osdi23-008_fig2` | When replication is secondary to a feedback loop, keep it light: two named instances (Job 1, Job 2) plus trailing ellipsis dots is enough to imply the pool, while the closed loop between cluster feedback and the policy stays the visual main event. |
| `osdi24-025_fig6` | Keep replication confined to exactly one tier of a layered stack, here the bottom engine, by giving only that box a stacked-shadow icon; leave every tier above it as a single box so the figure still reads as one layered system, not N whole systems. |
| `osdi24-050_fig6` | Draw a pool of homogeneous instances as one box with an offset shadow stack behind it rather than an ellipsis row, reserve that device for exactly the two pools the paper's contribution separates, and use one labeled transfer arrow (not a generic pipeline arrow) to name the specific handoff between them. |
| `osdi26-061_fig2` | Number the last replica explicitly (1 ⋯ 8) instead of using N when the paper's real hardware has a fixed, known count, and repeat that same ellipsis device at a second scale, connections or queue pairs inside one thread, when the implementation panel needs it too. |
| `sosp23-013_fig3` | To show one failure among many identical peers, restyle just that single node red and dashed rather than adding a separate callout box or arrow; keep circled numbers 1-5 tracing the unrelated job-submission-to-recovery flow so the failure marker and the process flow do not compete. |
| `sosp23-016_fig4` | Index replicas from 0 and label the last one N-1 exactly as this figure does (Worker 0, Worker 1, ..., Worker N-1), stack them vertically to one side, and let a single coordinator box on the other side hold every piece of shared state (cache manager, block tables, allocators) so no worker box repeats it. |
| `sosp25-061_fig7` | Two full replicas with an ellipsis between them beats three partial ones; index them 0 and N so the reader infers the range. |
Starred 16 of 25; the other 9 are in `index.json` with one-line notes.
Starred 16 of 23; the other 7 are in `index.json` with one-line notes.

### G. `multi-tier` — client / service / backend

**66/727 figures (9%)** describe a client-server or multi-tier arrangement (layered 26,
pipeline 9, other 9, control-data 7, hub-spoke 5, two-panel 5, host-device 3, matrix 2). `depicts`:
whole-system 48, one subsystem 10, deployment 4, path 3, comparison 1.

A `layered` figure whose tiers are **processes on different machines** rather than software layers on
one. The distinction changes the rules: tiers may be named "planes", boundaries are network or trust
boundaries, and arrows crossing tiers are the point.

```
  clients   ┌──┐ ┌──┐ ┌──┐
            └─┬┘ └─┬┘ └─┬┘
  ─ ─ ─ ─ ─ ─ ┼ ─ ─┼ ─ ─┼ ─ ─  network boundary
  service   ┌─▼────▼────▼──┐        ① submit
            │   gateway    │        ② dispatch
            └──────┬───────┘
  backend   ┌──────▼───────┐
            │   workers    │
            └──────────────┘
```

**Rules.** Three to five tiers, top-down, each a full-width row. Name the tiers in a gutter; when the
paper uses plane vocabulary, use it verbatim ("Control Plane / Scaling Plane / Serving Plane",
`asplos25-038_fig3`). Draw the network/trust boundary as a **dashed labelled rule**, not as a gap.
Cross-tier arrows are numbered — a multi-tier figure that shows a lifecycle is a lifecycle, and 5
numbered dashed actions crossing three planes is the corpus's clearest instance. Tier fill can encode
a property of the tier (preemptible vs on-demand, `nsdi24-029_fig7`), not just identity. When your
system sits *beside* an existing platform rather than above it, use two tier columns and highlight
only the path that crosses between them (`nsdi26-086_fig2`). Overlapping labelled scope outlines let
one figure name two protocols over the same three tiers (`osdi24-009_fig4`).

**Exemplars** (`assets/exemplars/multi-tier/index.json` lists all 16; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-038_fig3` | Name the tiers as planes in a gutter and let numbered dashed arrows cross plane boundaries - crossing arrows are what makes it a lifecycle, not a stack. |
| `asplos25-107_fig6` | Nest a third tier inside the second (the SSD's controller and flash chips inside the Server Machine box) when the real system has a storage device with its own internal architecture, and number every cross-tier hop 1 through 6 so the client-to-flash-and-back round trip reads as one continuous path. |
| `nsdi23-027_fig1` | Split every tier into a dashed management column beside a solid programmable-infrastructure column so the same shape-code works at all three layers, and put one legend at the top mapping every line colour and box style used below, so the reader never has to guess a colour's meaning per layer. |
| `nsdi23-068_fig1` | Draw the network path itself as a series of thin vertical zone columns behind the two mirrored endpoint boxes, and give each of the two parallel channels its own consistent colour end to end; add a small legend naming HBC and LLC, since this figure leaves those abbreviations uncoded. |
| `nsdi24-029_fig7` | Tier fill can encode a property of the tier (here: preemptible vs on-demand), not just identity; tag each tier box with its section. |
| `nsdi26-086_fig2` | When your system sits beside an existing platform rather than above it, use two columns and highlight only the path that crosses between them. |
| `osdi23-003_fig5` | Number the write path only where it crosses a machine boundary (local append versus RDMA replication to the backup tier), and draw the routing/shard-map table as a small inset table above the tier stack rather than another full box, since compact tabular metadata reads faster there. |
| `osdi23-008_fig3` | Label every cross-tier arrow with the exact data it carries (Res-Perf Data, Load Data, confidence bounds, allocations) in red so the feedback loop reads without extra explanation, and nest each tier's internal modules inside a dashed sub-box; add a legend for the box-fill colours, since this figure leaves that coding unexplained. |
| `osdi24-015_fig1` | Label a background sub-system with one umbrella name (here 'Serverless Cluster') so a detail panel can sit beside it without seeming detached, and place each contribution as its own small box below with a dashed arrow pointing up into the exact component it modifies; enlarge label text well past this figure's 4.5-5.5pt, a listed weakness. |
| `osdi24-039_fig1` | Nest the repeated internal structure (VMs in the compute tier, GC/Snapshot workers in each block proxy) inside its tier's own box rather than flattening it, and name every tier once in a shared left margin; add one accent colour, since this figure's all-gray palette (a listed weakness) makes component roles hard to tell apart. |
| `osdi26-044_fig4` | A deep tier stack stays readable if each tier is a full-width row of equal height and the flow between rows uses hollow block arrows rather than thin lines. |
Starred 11 of 16; the other 5 are in `index.json` with one-line notes.
Starred 12 of 17; the other 5 are in `index.json` with one-line notes.

### H. `dataflow-dag` — a real graph, not a chain

**46/727 figures (6%)** involve a computation graph, operator graph, DAG or graph IR (pipeline 18,
layered 10, matrix 4, other 4, control-data 3, hub-spoke 3, two-panel 2, host-device 2). `depicts`:
whole-system 34, one subsystem 7, path 3, comparison 2.

Use it when nodes have **more than one predecessor or successor** — a chain is a `pipeline`, a fan-out
to identical workers is `hub-spoke`; only a genuine DAG needs this.

```
      ┌─┐        ┌─┐
   ┌─>│b│──┐  ┌─>│e│──┐
 ┌─┴┐ └─┘  ▼ ┌┴┐ └─┘  ▼ ┌─┐
 │a │      │d│        │f│
 └─┬┘ ┌─┐  ▲ └┬┘ ┌─┐  ▲ └─┘
   └─>│c│──┘  └─>│g│──┘
      └─┘        └─┘
```

**Rules.** Nodes are small — a circle, a rounded chip or a short pill, not a labelled box with
sub-modules; keep node text to 1-2 words and put the vocabulary in a legend. Lay out by
**topological level**, left-to-right or top-down, with all nodes of one level on a shared axis.
These are the one place the corpus abandons orthogonal routing: only **20 of the 46** DAG figures
have zero curved lines, against **453/727 (62%)** corpus-wide, so straight diagonals and gentle
curves are fine here. Colour encodes **node type**, and the same colour must mean the same type in
every panel. To show a graph transformation, draw the same DAG two or three times under **labelled
transformation arrows** and mark only what changed — do not re-lay-out the graph between panels
(`osdi26-017_fig12`). Dashed edges mean edges that do not exist at runtime (pruned, optional)
(`nsdi26-082_fig6`). A DAG can also be an inline glyph inside the box that consumes it, drawn
20-30 pt wide (`asplos25-025_fig3`, `nsdi24-087_fig2`).

**Exemplars** (`assets/exemplars/dataflow-dag/index.json` lists all 23; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-025_fig3` | A DAG can be an inline glyph: draw it small inside the box that consumes it rather than giving it its own panel. |
| `asplos25-031_fig9` | Group recurring three-node motifs in the dataflow graph with dashed outlines, then draw red leader lines from each motif straight to the physical ALU, router or ALSU tile that executes it, so the graph-to-hardware mapping needs no separate legend. |
| `asplos25-142_fig5` | Stack two or three small example graphs inside the box that produces them to show a family of possible transformations, using small filled and outlined circles for operators; label each of the three so a reader can tell which optimization pass produced which graph, since this exemplar leaves that unlabelled. |
| `asplos25-147_fig2` | When a DAG is only the trigger for a pipeline rather than the figure's subject, shrink it to a small multi-coloured icon (20-30pt) rather than drawing it at full scale, and let the rest of the figure show what consumes it. |
| `asplos26-014_fig5` | Annotate each node of a small operator graph with the cost it would incur on each of two heterogeneous processors, so the graph itself argues for offloading; keep that graph compact and separate from the larger host-device architecture it motivates below it. |
| `asplos26-113_fig8` | This is really control-loop's shape, not dataflow-dag's, but it still teaches a graph-editing device: shade the ambiguous subgraph region in one flat colour, then redraw the same nodes with green checkmarks or red crosses over each candidate fix so accept/reject reads at a glance. |
| `asplos26-154_fig9` | Draw a hierarchy that gets pruned as a tree with a red cut line across it marking the current frontier, colour each node by its reuse/cache state rather than its type, and put a 3-colour arrow legend at the top since this dense a figure otherwise relies entirely on it to separate three overlapping flows. |
| `osdi23-001_fig3` | Even a mostly-linear operator graph earns dataflow-dag treatment the moment two nodes merge into one, so draw that merge explicitly (two boxes, one arrowhead) rather than smoothing it into a chain, and carry a highlighted path in one colour (red) down through the memory-hierarchy bands it maps onto. |
| `osdi23-053_fig3` | To show a graph transformation, redraw the exact same operator graph two or three times under labelled derivation arrows and colour only the newly discovered operators red against unchanged tan ones. Qualify reused names like Matmul per panel, since bare repetition across panels can blur which instance is meant. |
| `osdi24-052_fig6` | Carry one small set of node-colour meanings across all six panels, and run a single shared example, SIS1, SIS2, CI Op, through every stage so a reader tracks one case end to end. Repeat the legend near the top too, since it sits only at the bottom here, far from the first panels. |
| `osdi25-009_fig3` | Draw the operator graph as small circular nodes beside the stage that consumes it, keep one colour per operator (blue A, orange B) as it moves through partitioning and onto heterogeneous execution units, and close the loop with a labelled Profiling arrow feeding measurements back into an earlier stage. |
| `osdi26-127_fig1` | Carry the same small coloured-square operator code through every stage, layer boxes to superproxy bars to DAG vertex boxes, so identity survives four transformations without a fresh legend each time; add a real legend regardless, since none decodes what the squares mean here. |
| `sosp25-013_fig5` | Show a transformation as the same small DAG twice, before plain and after recoloured, with an arrow between; match each recoloured node's fill to its named optimization label outside the graph, but add explicit callout lines since colour and adjacency alone leave that mapping implicit here. |
Starred 13 of 23; the other 10 are in `index.json` with one-line notes.
Starred 20 of 29; the other 9 are in `index.json` with one-line notes.

### I. `n-panel-comparison` — the same drawing three or more times

**39/727 figures (5%)** have ≥3 panels plus comparison or variant wording (other 18, matrix 7,
layered 5, pipeline 5, two-panel 3, control-data 1); panels: 3 in 30, 4 in 4, 5-8 in 5. `depicts`:
comparison 18, whole-system 9, one subsystem 8, path 2, deployment 2. Before the type-discovery pass 18
of these sat in `other`. It generalises `baseline-vs-ours` (N = 2, one difference) and is what `matrix` becomes when
every cell is a whole diagram: N designs, or N moments of one mechanism, drawn with one vocabulary.

```
 (a) tree DCN          (b) reconfigurable      (c) ours
 ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
 │  ▲   ▲   ▲  │       │  ▲ ─ ▲ ─ ▲  │       │  ▲═══▲═══▲  │
 │ ┌┴┐ ┌┴┐ ┌┴┐ │       │ ┌┴┐ ┌┴┐ ┌┴┐ │       │ ┌┴┐ ┌┴┐ ┌┴┐ │
 └─────────────┘       └─────────────┘       └─────────────┘
 ■ switch  ● endpoint  ── cable  ═ optical          <- one legend for all panels
```

**Rules.** Draw the first panel, then *copy* it — identical skeleton, scale, box sizes and positions
in every panel; the reader compares by eye and any drift reads as a difference. Letters `(a) (b) (c)`
below each panel with a 2-4 word title that names the *claim* (Traditional / Reconfigurable / OCS),
never the system name alone. One legend for all panels, below them or in the last panel's free
corner. Side-by-side when a panel is taller than wide; stacked as rows when each panel is a wide
strip (`nsdi26-120_fig7`, `nsdi25-036_fig19`). Mark the delta inside each panel — a red ✗, an
accent-filled box, a bracket — and keep everything unchanged grey, so the eye jumps between panels
along the differences. Temporal series (online / offline / restoring) go in time order and reuse the
same message icons (`nsdi26-120_fig7`). The panel that is *ours* comes last (rightmost or bottom) and
is the only one with the accent fill. Four panels is the single-column ceiling; beyond that, go
double column or a 2×2 grid with the shared legend in the middle row.

**Exemplars** (`assets/exemplars/n-panel-comparison/index.json` lists all 21; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-069_fig1` | When more than four panels are needed, arrange them as a labelled grid (here 2 rows of 3) with one qubit-colour legend on the side covering every panel, and let a bold callout arrow (the red 'Gap!') point between two panels to name the specific mismatch the rest of the figure resolves. |
| `asplos25-101_fig1` | Keep the comparison panels (here serial vs batched vs speculative decoding) at one shared scale and icon set even when an unlike architecture panel sits above them; but size and align comparison panels consistently, since this figure's four differently sized sub-panels are flagged as visually busy. |
| `asplos26-002_fig1` | Keep every box in the exact same position across the compared panels and change only the swapped-in stage's label and colour (here Spatial+Temporal versus Full attention); give the two swapped stages more distinct colours than a shared light-blue fill, since this figure's near-identical palette makes the difference easy to miss. |
| `asplos26-021_fig6` | Reuse the identical crossbar-array icon at the same visual scale across every alternative-design panel so the eye compares structure, not icon style, and letter the panels (a)(b)(c) with short claim titles naming each design; pair the figure with the performance numbers it motivates, since the panels alone (a listed weakness) omit that data. |
| `asplos26-102_fig1` | Stack a small pair of identical-skeleton scheduling-strategy panels (preemptible vs FIFO) beside a larger numbered hardware-path diagram so the reader sees both what the cost is and how scheduling choice repeats it; keep the hierarchy labels larger, since this figure's high shape density is a listed weakness. |
| `nsdi24-041_fig12` | Draw the same topology twice and change only which flow colours are highlighted to isolate one variable (interleaved vs orthogonal sharing), and attach a smaller generic-component inset for shared internals rather than repeating it inside each main panel; label every flow's endpoints directly, since this figure leaves them to be inferred from the text. |
| `nsdi25-054_fig4` | When three panels show one continuous scenario, number the steps once across all of them instead of restarting per panel, and reuse the same backend colour coding (red MPI, green POSIX) from the architecture figure so panels cross-reference cleanly; budget more room per step than this figure's dense twelve-step layout. |
| `nsdi26-065_fig1` | Repeat one simple visual grammar (a shared input fanning into separate coloured boxes) across several real-world vignettes to argue a problem is general, even when each vignette's icons differ; but label what the colours mean on the first panel, since leaving it unstated across all three forces the reader to guess. |
| `nsdi26-120_fig7` | Stack temporal-state panels top to bottom with an identical endpoint-shim-plane skeleton in each, changing only the buffer/log structure and the highlighted system call; number each panel's own steps locally if they are truly separate states, but say so, since this figure's reused 1-6 numbering across panels (a weakness) can look like one global sequence. |
| `osdi23-048_fig1` | Reuse the same numbered path labels (here 1-4) across every panel of a growing-complexity comparison so the numbers become the paper's stable vocabulary for referring back to specific communication paths later, and grow the skeleton by adding new boxes (the SoC) rather than redrawing it. |
| `osdi23-053_fig3` | Give every panel the same internal (i)/(ii)/(iii) numbering and one colour code (red for the paper's new operators, tan for predefined ones) so a novel rewrite and a textbook baseline sit side by side and compare step for step; qualify reused names per panel, since repeated labels (DLT, Matmul) without qualification is a listed weakness. |
| `osdi26-018_fig7` | Stack comparison panels as full-width rows, not side-by-side columns, when each panel is itself a wide strip, and keep the tile-to-signal-to-RS-unit layout pixel-identical across rows so only the swapped hardware resource (copy engine, specialized SM, co-located SM) catches the eye. |
| `osdi26-094_fig1` | Put the paper's own design last with one extra visible element (the dashed inter-instance scheduling arrow) beyond the baseline panels, while keeping the Scheduler-Instance-Model vocabulary and colour legend identical across all panels; place the legend next to the panel where colour matters most, since here it sits far from panel (c). |
Starred 13 of 21; the other 8 are in `index.json` with one-line notes.
Starred 20 of 28; the other 8 are in `index.json` with one-line notes.

### J. `composite-figure` — one overview plus unlike detail panels

**42/727 figures (6%)** have ≥2 panels that are *not* a comparison (two-panel 20, layered 6,
pipeline 6, matrix 3, other 3, hub-spoke 2, host-device 2); panels: 2 in 28, 3 in 8, 4-5 in 6.
`depicts`: whole-system 17, one subsystem 13, path 6, deployment 6. The type-discovery pass moved 18
more here from `other` and loose fits. Distinct from `two-panel` (two related panels of the same
kind) by mixing *kinds*: an architecture beside a workflow, a data structure, a timeline, a table or
a plot — the "design overview" figure of a systems paper.

```
 ┌─ (a) architecture ─────────────┐  ┌─ (b) I/O path ────────┐
 │  ┌────┐   ┌────┐   ┌────┐     │  │  ① → ② → ③ → ④        │
 │  │    │──>│ ██ │──>│    │     │  └───────────────────────┘
 │  └────┘   └────┘   └────┘     │  ┌─ (c) record layout ───┐
 │        ┌──────────┐           │  │ ┌──┬──┬──┬──┐          │
 │        │          │           │  │ └──┴──┴──┴──┘          │
 └────────────────────────────────┘  └───────────────────────┘
   dominant panel (≥50% of the area)   subordinate panels, same palette
```

**Rules.** One **dominant panel** — the architecture — takes at least half the area and defines the
palette; the detail panels reuse its colours for the same components and never introduce new ones.
Each panel is drawn with its own template (`pipeline`, `phase-lanes`, `dataflow-dag`, a table) but
under one font-size ladder. Letters `(a) (b) (c)` and a short caption line under every panel; the
reading order is overview first, then details in the order the text discusses them, and the layout
follows that order (left-to-right, then top-to-bottom). Join panels only with dashed leaders when a
detail panel expands a region of the overview (then it is an `overview-with-inset` inside the
composite, `osdi26-051_fig2`); otherwise leave a clear 8-12 pt gutter and no connectors. One legend
for the whole figure, under the dominant panel. A raster element (photo, plot) gets a thin frame so
it reads as a panel, not as decoration (`osdi23-008_fig12`, `nsdi25-030_fig1`). Three panels at
single column, four at double; if the panels share no component, it is two figures, not one. In the spec, declare the panels as the
figure's **parts** (`panels[]` with `axis: "part"` and a `view`; sub-panels name their part as `parent`): each part
is then budgeted on its own, and `spec-guide.md` §8 says how to keep the parts reading as one figure and what to
cut before splitting when the user wants everything in one.

**Exemplars** (`assets/exemplars/composite-figure/index.json` lists all 26; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-100_fig9` | Pair a coarse timeline/mapping overview with one detailed per-layer zoom, and carry a single two-colour legend (single-device vs multi-device placement) across both panels so the coarse view and the fine view never need separate keys. |
| `asplos25-114_fig5` | When three panels each use a different diagram type (a data-layout grid, a circuit diagram, a scheduling timeline) to explain complementary aspects of one system, file the figure as composite-figure with a dominant panel, not n-panel-comparison, which needs one shared drawing style repeated across the panels. |
| `asplos25-157_fig2` | Chain dashed zoom leaders panel to panel (core to array to cell) rather than drawing every level from scratch, and keep the same green-buffer/gray-blue-control/light-blue-array colour roles at every zoom level so a reader always knows which block is which even after three levels of nesting. |
| `asplos25-160_fig5` | Leave an explicit 8-12pt gutter (or a thin frame) between an architecture panel, a notation key, and a worked example even when they logically belong together, since merging three conceptually different sub-panels with no visible border, a listed weakness here, makes the figure read as one crowded panel instead of three legible ones. |
| `asplos25-168_fig11` | Pair a technical diagram with a small icon-based pros/cons box (a sad face for the limited baseline, a happy face for the improved design) placed right beside it, reusing the same cell-shading vocabulary so the emotional icon reads as a direct verdict on the adjacent architecture rather than a separate aside. |
| `asplos25-177_fig1` | Use matching colour underlines (green for the specific row or column each side accesses) across a software panel and a hardware grid panel to make an analogy visible without arrows connecting them; add at least one numbered pointer between the panels, since this purely motivational figure otherwise relies on the reader inferring the connection. |
| `asplos26-013_fig13` | Pair an identical-skeleton before/after timeline (same GPE lanes, same block width) with a separate hardware block-diagram panel that implements the fix, mixing a timeline kind with an architecture kind under one figure; keep font size well above this figure's illegible 2-3.5pt, a listed weakness. |
| `asplos26-026_fig5` | Put a measurement plot (here a roofline chart) beside the mechanism diagrams it justifies, and reuse the diagrams' own colour legend (prompt/drafted/accepted/rejected tokens) as the one legend for the whole figure so the plot and the diagrams read as one argument, not two attachments. |
| `asplos26-060_fig7` | Put the full pipeline as a labelled overview panel at the top, then stack detail zooms of each unit below it using consistent header-bar naming; keep the lettered panels (a)-(e) in reading order so the overview always comes first. |
| `asplos26-088_fig12` | Chain dashed zoom connectors through two levels (engine to core to sub-unit) and reserve one accent colour (light blue) for only the deepest, most novel block so the eye knows exactly which of several nested boxes is the actual contribution; label every symbol explicitly, since this figure's unlabelled '>' comparator relies on visual convention alone. |
| `asplos26-129_fig2` | Chain unlike panels left to right in the order the text argues them: problem, then insight, then contributions, and reuse one colour (here green) across panels to mark everything that is the paper's own idea, from the insight box to the C1-C3 contribution list. |
| `nsdi24-036_fig1` | Stack two structurally parallel chains directly above each other so a swapped module position jumps out without annotation; but unify panel styles with one shared palette, since packing an edge topology, chain diagrams and an ASIC block diagram with no common visual language is this figure's own listed weakness. |
| `nsdi25-081_fig4` | Link annotated source-code lines to the specific execution units running them with small labelled arrows (C1, C2, Cb), and share one Memory box with explicit R, W, R&W arrows across foreground and background cores; strengthen the loose visual link this figure leaves between its top pipeline row and bottom detail row. |
| `nsdi26-104_fig6` | Even when three unlike diagram idioms (byte table, layer stack, path mesh) share one colour thread across a mechanism, still give each panel its own frame or gutter and one shared legend, since this figure's absence of both, a listed weakness, makes the three parts read as unrelated at first glance. |
| `nsdi26-140_fig8` | Place the generic subsystem (a) and its generic memory layout (b) beside the paper's own scheduler (c) in one palette so the reader sees how little new logic Themis adds, and keep one inside legend (red data path, green dashed control path) for all three panels; avoid this figure's dense 4-5pt text. |
| `osdi23-008_fig12` | Give the dominant architecture panel over half the figure's area and let the two result plots (raw and smoothed) sit as clearly smaller subordinate panels; keep separate colour codes for structural role versus method identity fully apart, since sharing one figure without a divider (a listed weakness) risks a reader reading the wrong key. |
| `osdi26-051_fig2` | Number every hop of one request, ring doorbell, fetch, parse and slice, address translation, DMA, flash command, directly on its connecting arrows to turn a static three-panel architecture into a traceable walkthrough; watch the density, 135 text labels and 310 shapes across three panels, a listed weakness. |
| `osdi26-061_fig2` | Draw a layered software stack directly above the physical server hardware it runs on so flows can be colour-coded end to end (orange control, green data, blue network), and repeat that legend in the internal threading panel too, since this figure leaves it unstated there, a listed weakness. |
| `osdi26-098_fig2` | Reserve composite-figure for a dominant architecture plus lettered unlike-kind detail panels; a flat, unlettered sequence of small background-concept diagrams like this one (Transformer block, then quantization, then execution strategy) is closer to small multiples and needs no single anchor panel, only consistent bit-width labels and dashed cross-reference arrows tying each stage to the next. |
| `sosp25-035_fig2` | Let a small worked example's node/id labels (C, D, E, G) recur identically across the tree, the RPC-flow diagram, and the resulting database rows so a reader can trace one concrete write through every representation; but keep the cross-references few, since needing to match letters across three dense sub-panels, a listed weakness, adds real effort. |
Starred 20 of 26; the other 6 are in `index.json` with one-line notes.
Starred 17 of 21; the other 4 are in `index.json` with one-line notes.

### K. `mirrored-pair` — two identical peers around a shared middle

**83/727 figures (11%)** describe mirrored, symmetric or twin structures (layered 17, host-device 17,
pipeline 16, two-panel 14, control-data 9, other 4, hub-spoke 4, matrix 2). `depicts`:
whole-system 39, one subsystem 22, path 13, comparison 6, deployment 3. For 16 of them the pair *is*
the frame. Distinct from
`host-device` (the two sides are asymmetric) and from `two-panel` (the sides are unrelated): here the
two sides are the same stack, and the element on the axis between them — bridge, directory, switch,
network, shared memory, bitmap — is the paper's contribution.

```
 ┌─ Node A ──────┐                     ┌─ Node B ──────┐
 │ ┌───────────┐ │     ┌─────────┐     │ ┌───────────┐ │
 │ │   app     │ │  ①  │ shared  │  ④  │ │   app     │ │
 │ ├───────────┤ │────>│  ████   │────>│ ├───────────┤ │
 │ │  runtime  │ │<────│ middle  │<────│ │  runtime  │ │
 │ ├───────────┤ │  ③  └─────────┘  ②  │ ├───────────┤ │
 │ │   NIC     │ │                     │ │   NIC     │ │
 └───────────────┘                     └───────────────┘
        same boxes, same order, same sizes on both sides
```

**Rules.** Build one side and mirror it — same boxes, same order, same sizes; asymmetry is a
statement, so introduce it only where the design differs. The middle element sits on the axis of
symmetry and is the only accent-filled thing. Name the sides by role (sender / receiver, Intel node /
Arm node, copy side / sync side, primary / backup, client / replica), not by instance number. Flows
cross the middle and are numbered in one direction, out and back (①-④). When the two sides run the
same steps in lockstep, draw matching numbered rows and connect corresponding rows with dashed
"equivalent" links (`osdi26-054_fig7`). Double column when each side is a full
stack (`nsdi23-068_fig1`, `nsdi26-133_fig1`). With N > 2 members it is `replicated-grid`; with one
side a device it is `host-device`.

**Exemplars** (`assets/exemplars/mirrored-pair/index.json` lists all 17; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-051_fig2` | Align identical protocol-stack layers across parallel columns so a reader compares row by row, and put the paper's actual contribution (the scheduler) on the shared axis between the two mirrored sides, accent-filled, rather than folding it into a bottom hardware band. |
| `asplos25-080_fig1` | Put the one shared resource, here a UPID memory box, directly on the axis between two mirrored processor-core stacks, and number every step of a round trip 1 through 7 straight onto the arrows; disambiguate duplicate box labels (Processor Core, Program Code) with a Sender/Receiver header above each side rather than relabeling the boxes themselves. |
| `asplos25-157_fig3` | Use a mirrored pair to show one device in two operating modes, not just two devices: draw the exact same internal grid twice, side by side, and let one small accent-coloured block between them carry all the labelled signals that actually change between modes. |
| `asplos26-067_fig3` | Give two heterogeneous host domains the identical internal box sequence (private caches, local directory, coherence block) so they read as one mirrored stack, then draw the shared directory they both bridge into as the one gold-accented box on the axis, and number the request and response arrows in one round trip out and back. |
| `nsdi23-047_fig4` | Stack two double-column mirrored pairs vertically, storage servers over worker machines, keep each pair's internal boxes (Graph Store plus Samplers, Feature Cache Engine plus GPU Workers) identically arranged on both sides, and write the exact noun each crossing arrow carries, Cross-Partition Communication, Parameter Synchronization, directly on the arrow instead of leaving it implicit. |
| `nsdi23-068_fig1` | Place the mirrored pair at the two ends of a swimlane network path rather than side by side, reverse the internal stacking order on the far side (steerer-then-buffer becomes buffer-then-steerer) to mirror it visually, and label the two crossing channel arrows in the figure itself, since no legend explains HBC and LLC here. |
| `nsdi23-085_fig8` | Draw a crossing X of bidirectional arrows between a redundant top layer and the two mirrored containers below to show any-to-any reachability, keep each container's role colours (scheduler green, executor yellow, store light blue) identical on both sides, and let one wide shared-store box at the bottom serve as the axis of symmetry. |
| `nsdi24-023_fig3` | Mirror an encoder and decoder around one small icon standing in for the data actually transmitted between them, and apply one binary colour legend, orange for learned modules, blue for classical ones, to both chains identically so a reader sees at a glance how much of the traditional codec structure survives. |
| `nsdi24-107_fig5` | Keep the common base protocol stack identical on both end nodes and add only the role-specific boxes where the design differs, client-side tunnel wrapping, server-side rate control, then dedicate the entire middle box to the paper's own contribution with named sub-modules. Disambiguate repeated HTTP/QUIC/UDP labels by column position, since duplicates can confuse a fast reader. |
| `nsdi26-021_fig10` | Swap the internal stacking order of the mirrored receiver relative to the sender, hardware-then-software becomes software-then-hardware, so the eye still reads top-to-bottom as protocol flow on both sides, and key every circled step number to one shared legend panel placed between the two mirrored diagrams rather than beside either one. |
| `nsdi26-133_fig1` | Stack each mirrored side as gateway/pod over virtual switch over NIC, and colour the two kinds of crossing path differently, orange for inter-node, yellow for intra-node, so a reader sees at a glance which path a request re-traverses the network stack; keep the busy per-pod annotations and legend from crowding the main stack shape. |
| `osdi24-050_fig6` | Draw a pool of same-role instances as a small stack of offset boxes rather than one box, name the two mirrored pools by role (Prefill, Decoding) not by number, and put the one operation that crosses between them, KV Cache Transfer, on a single labelled arrow bridging the gap. |
| `osdi26-054_fig7` | Stack two identical multi-level structures, real above and shadow below, aligned column by column so vertical arrows can show exactly which levels sync and which do not, and mark the read-write versus read-only halves on either side of a single dashed midline instead of a caption note. |
Starred 13 of 18; the other 5 are in `index.json` with one-line notes.
Starred 16 of 20; the other 4 are in `index.json` with one-line notes.

### L. `flanked-core` — one engine between an interface band and a hardware band

**51/727 figures (7%)** describe a central engine, core or hub with something above and something
below it (hub-spoke 15, layered 11, pipeline 9, control-data 6, other 5, host-device 3, matrix 1,
two-panel 1). `depicts`: whole-system 38, one subsystem 5, path 4, comparison 3, deployment 1. For 9
the frame is exactly this shape. It is a `hub-spoke` whose spokes are
stratified — callers on top, hardware or kernel below, interchangeable plug-ins at the sides — the
shape of a runtime, LibOS, serving-engine or scheduler paper.

```
 ┌── Interface ─────────────────────────────────────────┐
 │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐         │
 └──└────────┘─└────────┘─└────────┘─└────────┘─────────┘
   ┌────────┐   ╔══════════════════════════╗   ┌────────┐
   │ model  │   ║  ┌──────┐   ┌──────┐     ║   │ kernel │
   ├────────┤ =>║  │      │   │      │     ║<= ├────────┤
   │ model  │   ║  └──────┘   └──────┘     ║   │ kernel │
   ├────────┤   ║        ENGINE            ║   ├────────┤
   │ model  │   ╚══════════════════════════╝   │ kernel │
   └────────┘                                  └────────┘
 ┌── Hardware ──────────────────────────────────────────┐
 │  ┌────────┐ ┌────────┐ ┌────────┐                    │
 └──└────────┘─└────────┘─└────────┘────────────────────┘
```

**Rules.** The core is the largest box and the only nested one — its 3-6 sub-modules sit inside it;
everything else is a single row or column of small boxes. Bands are full width, one row each, named
in the margin (Interface / Hardware, User space / Kernel space) and kept grey; the core gets the
accent tint. Side columns are optional and hold *interchangeable* things (models, kernels, policies)
drawn as a stack of equal pills. Connect bands to the core with **block arrows** or one shared bus,
not one arrow per module (`sosp25-013_fig5`); when the figure narrates one request, run a single
numbered path through the core instead (`sosp24-020_fig3`). A privilege or trust boundary is a dashed
rule across the figure, between the core and the bottom band (`sosp24-020_fig3`, `sosp25-010_fig1`).
At most three bands and two side columns; if the "callers" are themselves a system, the figure is
`multi-tier`.

**Exemplars** (`assets/exemplars/flanked-core/index.json` lists all 18; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos26-019_fig4` | Put the routing decision box above the shared resource pool it feeds and give the side monitor its own feedback arrow back into that pool rather than into the core; the weakness here is too many small labelled arrows crowd the scheduler, so budget space for routing labels before adding a monitor loop. |
| `nsdi23-077_fig6` | Place the caller band's repeated small boxes (four send queues here) in one row above the hardware band, then let a single mux-shaped core inside that band collect every event type by arrow direction alone rather than colour, so in and out of the core reads as the only code that matters. |
| `nsdi23-083_fig3` | Draw the coordinator as one wide box straddling its two backend boxes below to assert one design generalizes across them, and split the coordinator's own internals into two adjacent stacks (bookkeeping versus execution); the weakness is that only two backends are shown, so add an ellipsis if the claim is meant to scale further. |
| `nsdi24-064_fig3` | The real lesson is flanked-core's, not hub-spoke's: place the external caller interface above the engine, the executing agent below it, and a second interface beside it, then colour the engine's internal function-dispatch modules (orange) distinctly from its boundary (blue). |
| `nsdi26-072_fig8` | Use a stacked-paper icon behind a box to signal many concurrent instances without drawing them all, and route shared metadata into both the dispatcher and the engine's scheduler; the weakness is that the long wraparound arrow carrying it into the engine is easy to miss, so keep shared-state arrows short and direct. |
| `nsdi26-090_fig4` | Put the trust or region boundary as a dashed line directly between the core and the bottom band, exactly where the rule calls for it, and draw that bottom band as a row of three named service pills rather than one generic box; number the steps so cache-hit and cache-miss paths both stay traceable. |
| `nsdi26-092_fig6` | Mark a denied access path with one bold red X on the shared object rather than a caption, and give the figure a small top-right legend distinguishing solid data-path arrows from dashed control-path arrows; the weakness here is that the X itself has no legend entry, so give every ad hoc symbol one too. |
| `osdi23-021_fig4` | A flanked-core sandwich can appear at any scale: repeat the same left-core-right composition inside one band of a larger layered figure, colour that band and its neighbour differently, and orange-highlight the technique sub-boxes inside each; the weakness here is the central box's role is legible only from position, so add one line to it. |
| `osdi25-002_fig7` | Put the privilege boundary between the caller band and the core rather than lower down, give the core four labelled submodules so it reads as an engine, and let two kernel-side modules share the band below as equals instead of nesting one inside the other. |
| `osdi26-020_figtex7` | When several distributed hardware sources all feed one engine box, number each source and give it a matching entry in a compact legend column instead of writing the source name on every arrow; keep the engine's internal stages in a dashed sub-box like the DP Training region here. |
| `osdi26-060_fig8` | The flanked-core sandwich can nest inside a larger layered stack: draw the two queues as small pills on either side of the planning core rather than as generic arrows, and give the bottom hardware band its own internal grid of managers instead of a single box. |
| `sosp24-020_fig3` | Run a numbered path through the core's internal submodules and draw interchangeable scheduling policies as a stack of index-card pills beside it; but number branches only when they truly form one sequence; here steps 2/3 split from the scheduler while 4/5 arrive independently from hardware, so the numbering reads as separate paths, not one flow. |
| `sosp25-013_fig5` | Use large white block arrows on all four sides to funnel bands and side columns into the core, keep both side columns as plain stacked pills naming interchangeable models or kernels, and show the core's own transformation as a small before/after computation-graph icon rather than prose. |
Starred 13 of 18; the other 5 are in `index.json` with one-line notes.
Starred 17 of 22; the other 5 are in `index.json` with one-line notes.

### M. `block-floorplan` — hardware blocks placed like a die

**105/727 figures (14%)** use hardware-block vocabulary (caches, register files, systolic arrays,
crossbars, datapaths); **46** carry accelerator / FPGA / microarchitecture tags — 35 of them ASPLOS —
and had been filed as pipeline 27, two-panel 20, layered 15, host-device 12, control-data 11,
other 11, matrix 6, hub-spoke 3. Distinct from
`pipeline`: position means *physical placement and adjacency* (what shares a bus, what is on-chip),
not order, and many blocks have no arrows at all.

```
 ┌─ Accelerator (on-chip) ──────────────────────────────┐   ┌──────┐
 │ ┌────────┐  ┌──────────────────────┐   ┌──────────┐  │   │ DRAM │
 │ │ ctrl / │  │  ▦ ▦ ▦ ▦   compute   │   │ weight   │  │═══│      │
 │ │ FSM    │  │  ▦ ▦ ▦ ▦   array     │   │ buffer   │  │   └──────┘
 │ └────────┘  │  ▦ ▦ ▦ ▦             │   └──────────┘  │   ┌──────┐
 │ ┌────────┐  └──────────────────────┘   ┌──────────┐  │───│ host │
 │ │ scratch│  ═════════ on-chip bus ═════│ act. buf │  │   │ CPU  │
 │ └────────┘                             └──────────┘  │   └──────┘
 └──────────────────────────────────────────────────────┘
   compute in the middle, storage at the edges, control in a corner, memory and host outside
```

**Rules.** Draw the chip or board boundary first and put off-chip memory and the host *outside* it.
Compute blocks in the middle, storage (buffers, SRAM, register files) at the edges, control in a
corner — the reader assumes the drawing is a floorplan, so honour that. Adjacency is the connection:
blocks that talk share an edge or sit on the same bus; draw buses and queues as thick grey bars or
wide double lines, and reserve arrows for traffic that *crosses* something, with the traffic classes
legended (`asplos25-110_fig2`: main-memory / shared-memory / DMA). Repeat identical units as a small
grid plus an ellipsis (the ×N rule of `replicated-grid`). Labels are short hardware nouns (L1 I-Cache,
RF, DMA, PE) with the expansion in the caption; size boxes by importance, not by label length. Colour
by block *type* (compute / memory / control / interconnect) with a legend, novel hardware in the
accent, existing in grey. No reading direction — do not number unless one request is being traced.
Keep text at ≥5.5 pt: these are the densest figures in the corpus, and the recorded weaknesses are
almost all "small text at print size".

**Exemplars** (`assets/exemplars/block-floorplan/index.json` lists all 23; figures live in `assets/exemplars/figures/<id>/`):

| id | what to learn |
| --- | --- |
| `asplos25-110_fig2` | Cap the traffic-color legend at three classes exactly, put it in a free column on the right, and use dashed module outlines for hardware blocks that only exist in some evaluation configurations; expect this density (277 shapes) to require careful, uncluttered grouping into named regions (Tensor Core, Shared Memory, Gemmini). |
| `asplos26-029_fig9` | Tag only the truly novel sub-blocks in accent blue inside an otherwise grey conventional systolic pipeline, but skip this figure's weak repetition cue, a bare partial outline behind the core box, and draw a visible ellipsis or times-N label instead. |
| `asplos26-100_fig3` | Color the block you contribute green against yellow existing structures, then run a lettered tap (a)-(g) into every distinct point of the host pipeline it touches, cross-referencing each letter to a paragraph rather than crowding the figure with inline explanations of every wire. |
| `nsdi26-142_fig4` | When several distinct request types share one hardware block, give each its own number and colour and keep a compact legend inside a free corner near that block rather than redrawing it per path; keep the FPGA boundary as a dotted outline with the true off-chip resource drawn outside it. |
| `osdi24-046_fig2` | Draw the recurring block once at full size with its internals exploded, ALUs, tables, register arrays, next to the compact pipeline where it appears twice, then add arrowheads and a legend for its two colour shades; this figure's own recorded weakness is undirected lines and an unexplained second shade. |
| `sosp25-015_fig2` | Trust adjacency alone when the point is containment: no arrows are needed between a GPC's nested TPC/SM boxes, only consistent color per hardware type and position (memory at the edge, compute in the middle); zoom one representative unit into a dashed-leader callout instead of labeling every internal detail in place. |
Starred 6 of 23; the other 17 are in `index.json` with one-line notes.
Starred 6 of 23; the other 17 are in `index.json` with one-line notes.

---

## Choosing a template

Read the figure spec's structure, not its subject. Work down the table and take the first match.

| signal in the spec | template | corpus support |
| --- | --- | --- |
| Two halves that are *the same thing under two designs*; a "before/after", "baseline vs ours", or "(a) existing / (b) proposed" framing | `baseline-vs-ours` | 76/727 depict `comparison`; 24 with explicit baseline-vs phrasing |
| ≥3 panels showing *the same drawing* under different designs or at different moments, one shared legend | `n-panel-comparison` | 39/727 with ≥3 panels and comparison/variant wording |
| ≥3 comparable variants, or a two-dimensional key (rank × stage, pool × resource, type × diagnosis); few or no arrows | `matrix` | 31/727; comparison 16/31, flow median 4 |
| Two panels that are related but not contrastive (overview + detail, two stages of one thing) | `two-panel` | 105/727; 63 of them have no formal sub-figure frames |
| ≥2 panels of *different kinds* (architecture + workflow / data structure / timeline / plot), one dominant | `composite-figure` | 42/727 non-comparison multi-panel figures |
| One overview plus a magnified sub-block connected by dashed leaders | `overview-with-inset` | 131/727 mention a zoom/inset/callout |
| Components mostly ordered: A feeds B feeds C, most nodes have one predecessor | `pipeline` | 187/727; left-right 66%; flow median 7 |
| Same as above but with a return edge closing a cycle | `control-loop` | 64/727 |
| Nodes with several predecessors/successors; a computation or operator graph | `dataflow-dag` | 46/727 |
| 3-5 tiers where each depends only on the one below; software layers on one machine | `layered` | 162/727; whole-system 73%; top-down 79% |
| Same but the tiers are processes on different machines, with a network/trust boundary | `multi-tier` | 66/727 |
| Boxes literally inside boxes for ≥3 levels; hardware or memory hierarchy | `nested-stack` | 307/727 at nesting depth ≥3 |
| Hardware blocks whose position means placement and adjacency; buses instead of arrows; on-chip vs off-chip | `block-floorplan` | 46/727 carry accelerator/microarchitecture tags (35 ASPLOS); 105 use hardware-block vocabulary |
| Two asymmetric sides with a named interconnect between them (CPU/GPU, host/NIC, real/simulated) | `host-device` | 47/727; legend 38%, numbered 53% |
| Two *identical* stacks facing each other across a bridge, directory, switch or shared memory | `mirrored-pair` | 83/727 mention mirrored/symmetric/twin structures |
| One coordinator plus N interchangeable peers | `hub-spoke` | 40/727; whole-system 78%, distributed 62% |
| One engine box with callers above, hardware/kernel below, plug-in columns beside | `flanked-core` | 51/727 describe a central engine between bands |
| N identical units with an ellipsis, sharing a resource band | `replicated-grid` | 74/727 |
| Flows fall into ≥2 named classes (data vs control, request vs telemetry) and telling them apart is the point | `control-data` | 78/727; legend 36% |
| Concurrency or duration is the claim; blocks positioned along a time axis | `phase-lanes` | 38/727 timelines; 286/727 have lanes |

Two cheap sanity checks before you commit:

- **Count the flows.** ≥7 flows in reading order → `pipeline` or `control-loop`. ≤4 flows with ≥8
  components → `matrix`, `layered` or `nested-stack`; the structure is the message.
- **Count the panels.** 1 panel → any core template. 2 → `two-panel`/`baseline-vs-ours`, or
  `composite-figure` when the panels are of different kinds. ≥3 → `n-panel-comparison` (same drawing
  repeated), `composite-figure` (unlike panels), `matrix` or a chained `overview-with-inset`.

### Not an architecture layout

Nine figures that had been filed under architecture in the 736-figure selection were reclassified on
2026-09-07 (leaving 727; `sosp25-047_fig4` followed on 2026-09-09, leaving 726); they were memory layouts, an address-to-hash worked example,
sorted-array data structures, a state machine, a physical qubit layout; the corpus taxonomy calls
these `data-layout`, `mechanism` and `timeline`. When a brief
describes one, say so in the brief rather than forcing it into `pipeline` or `layered`, then borrow
the nearest template's conventions: a memory, packet or record layout → `matrix` cells or
`nested-stack` regions with field widths in a gutter; a worked example or a sequence of states →
`n-panel-comparison` with the states numbered; schedules, traces and message sequences →
`phase-lanes`; state machines and dependency graphs → `dataflow-dag`.

---

## Cross-template conventions

All counts over the 727 architecture diagrams. "legend %" and "numbered %" are the share of that
template's figures carrying any legend / any step marker.

| template | n | components (q1/med/q3) | flows med | nesting ≥3 | lanes | legend % | numbered % | double col % | aspect med (single) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `pipeline` | 187 | 7 / **10** / 13 | 7 | 59/187 (32%) | 36% | 19% | 41% | 27% | 1.82 |
| `layered` | 162 | 9 / **13** / 16 | 6 | 90/162 (56%) | 43% | 26% | **26%** | **6%** | **1.46** |
| `two-panel` | 105 | 8 / **11** / 15 | 5 | 39/105 (37%) | 36% | 23% | 30% | 22% | 1.82 |
| `control-data` | 78 | 7 / **10** / 14 | 7 | 35/78 (45%) | 54% | 36% | 33% | **6%** | 1.67 |
| `hub-spoke` | 40 | 7 / **10** / 13 | 6 | 19/40 (48%) | **22%** | 25% | 35% | 8% | 1.70 |
| `matrix` | 31 | 7 / **9** / 12 | **4** | 7/31 (23%) | 55% | **42%** | 32% | **35%** | 1.67 |
| `host-device` | 47 | 10 / **11** / 14 | 6 | **28/47 (60%)** | 30% | 38% | **53%** | 17% | 1.75 |
| *all 727* | 727 | 8 / **11** / 14 | 6 | 307 (42%) | 39% | 27% | 35% | 18% | 1.69 |

| convention | corpus behaviour |
| --- | --- |
| **Legend** | Absent in **532/727 (73%)**. When present: inside 101, below 54, right 40. Palette size predicts it only weakly (legend rate 19% at ≤4 fills, 29% at 5-7, 29% at 8-10, 34% above 10); the figures that legend are the ones where colour or line style *means* something, and their median palette is 7 when the legend sits below vs 6 with no legend. Put it inside a free corner for ≤3 entries, below (spanning the figure) for a shared multi-panel key, right for a per-row/per-state key. |
| **Step markers** | Absent in **471/727 (65%)**. Circled numbers 179, labelled arrows 38, letters 36, digits 3. Numbering tracks intent, not size: `one path/request flow` **54%** numbered, `comparison` 42%, `whole-system architecture` 34%, `one subsystem` 30%, `deployment` 4%. Flow count is barely a predictor (median 7 with numbers, 6 without). Letters are used when the markers index prose rather than order a traversal. |
| **Titles** | Component name inside its box, bold, top-aligned. Group/container title on the container's top edge or top-left. Tier and lane names in a margin gutter. Section references (§3.2) appended to group titles, never to leaf boxes. No figure-level title inside the canvas — that is the caption's job. |
| **Nesting** | Depth 2 is the norm (**370/727, 51%**); depth 3 is common in `layered` (79/162) and `hub-spoke` (17/40); depth 4 occurs 31 times, mostly hardware/memory hierarchies. Depth 1 (50 figures) is for pure tier stacks and matrices. |
| **Lanes** | 286/727 (39%). Left-right lanes = parallel instances through the same stages (pipeline 49); top-down lanes = columns inside a tier (layered 54). |
| **Panels** | 626/727 (86%) are single-frame. Sub-figure letters `(a)`, `(b)` go below each panel; a shared legend is defined once for all panels. |
| **Column** | 593 single (82%) / 133 double (18%). Double column is a strip: same height, double width, aspect median 3.08. `matrix` (35%) and `pipeline` (27%) go double most often; `layered` almost never (6%). |
| **Direction** | left-right 271, mixed 224, top-down 219, bottom-up 13. Bottom-up is essentially unused (13/727) — do not invent it. |
| **Emphasis** | Median 5 of 11 components are marked `novel` (median fraction 0.53) — more than half the boxes in a typical figure are the paper's own, so emphasis has to be selective. Three devices recur: an `accent` fill on contributed boxes (plus `arrow-accent` on the path they serve), a **dashed group box** around the contributed sub-tree, and colour-coding novel vs reused ("blue = new components, gray = existing"). 56/727 records state outright that colour separates the contribution from existing infrastructure. |
| **Line style** | Dashed strokes in **438/727 (60%)**; 441/727 records assign dashed a meaning — control flow, optional/pruned edges, or group boundaries. Pick **one** of those three meanings per figure. 453/727 (62%) route with zero curved lines; curves are for feedback edges and control fan-outs. |
| **Density** | Median 150 shapes, 21 text boxes, 47 elements per 100 pt². `layered` is the sparsest per unit area (39) and `two-panel` the densest (55). **346/727 (48%)** carry `text_density: dense`, and "dense or small text" is by far the most-recorded weakness (**255 matches**; the next cluster has 57), so treat these medians as ceilings, not targets. |

### The recurring failures, ranked

Weakness clusters over all 727 (a weakness string may match several clusters; 119 figures have none,
258 have one, 349 have two, 1 has three):

| # | cluster | worst templates |
| --- | --- | --- |
| 255 | dense or small text at print size | pipeline 73, layered 54, two-panel 32 |
| 57 | colour or icon coding with no in-figure legend | pipeline 15, layered 11, two-panel 8 |
| 51 | undefined abbreviations / notation | pipeline 15, layered 10, control-data 7 |
| 36 | relies on the caption or body text to be readable | pipeline 10, layered 8, other 7 |
| 34 | repeated or duplicate labels on distinct boxes | pipeline 9, two-panel 7, control-data 7 |
| 34 | unlabelled arrows or missing arrowheads | pipeline 11, two-panel 9, layered 6 |
| 26 | legend placed away from what it explains | pipeline 10, layered 4, other 4 |
| 19 | overlapping arrows or misaligned boxes | pipeline 5, layered 5, two-panel 3 |
| 18 | print / greyscale / low-contrast risk | pipeline 8, layered 3, two-panel 2 |
| 13 | extreme aspect ratio (too tall or too wide) | pipeline 5, other 2, host-device 2 |
| 13 | raster/photo content inside a vector figure | pipeline 3, layered 2, control-data 2 |
| 11 | a component drawn as a black box with no detail | pipeline 8, control-data 1, hub-spoke 1 |
| 11 | too many panels | pipeline 4, layered 2, two-panel 2 |

Read the top row as the governing constraint: **the corpus's dominant failure is putting too much in
too little space.** Before adding a component, an inset or a panel, check the medians above.
