# Filling the figure spec

The spec is the contract between *reading the paper* and *drawing the SVG*. It carries structure
and hints, never coordinates: the agent hand-draws from it, the user gives feedback, the feedback
edits the spec, the figure is redrawn.

- Fields, enums, defaults: [`spec-schema.json`](spec-schema.json) is authoritative — this file does
  not repeat it.
- Check before drawing: `python3 figgenie-paper-diagram/scripts/spec_validate.py spec.json`
  (errors exit 1; warnings are the style bands and are usually worth fixing).
- Worked examples: `assets/specs/examples/` holds three specs reverse-engineered from corpus exemplars. They are
  examples of spec syntax only, showing how the fields are filled for a real figure. Layout, colour, density and
  emphasis come from the exemplar library (`assets/exemplars/`: the figure each spec's `_source` points at, and
  the exemplars of your template) and from the references.

---

## 1. Intake → brief → confirm → spec

Do not run a questionnaire. Read what the user gave (paper sections, notes, an old figure, chat) and
**write the figure brief first** (`references/brief-template.md`: what the figure is, the components with
new / existing / external tags, the numbered main path and secondary flows, the one point it argues,
layout and style intent, assumptions to confirm, a caption draft). The user confirms or corrects the brief;
the spec is derived from the confirmed brief, never written first.

What a complete brief has to settle (an internal checklist, not questions to recite):

| the spec needs | usual source in the material | default when the source is silent |
|---|---|---|
| system name + one-liner | title, abstract | — (always available) |
| which boxes are **new** | "we propose / we introduce / our X", the design section | ask — this changes the figure |
| the **main path** | the walkthrough / running example / numbered list in the design section | ask if there are several candidates |
| existing vs external parts | "built on", "unmodified", named third-party systems | existing |
| figure kind (whole / subsystem / request path / comparison / deployment) | where the figure sits (§3 overview → whole system) | whole-system |
| column | component count (> 13 boxes → double), the venue's style | single |
| number of steps | the walkthrough (0 when nothing is ordered) | 0 |
| caption content | what the figure cannot show (protocol details, what "dashed" means) | generated from the brief |

Rules for asking:

- **Infer, then confirm.** Every inferred item goes into the brief's "assumptions to confirm" with its
  source quoted. Ask nothing that the text already answers.
- **Ask only what changes structure and cannot be inferred** — in practice "which parts are new" and
  "which path is the main one", occasionally "is this one figure or two". Bundle into one message, at most
  three points, each phrased as your best guess with the alternative ("I read Scheduler and Cache as new
  and Store as existing — right, or is Store new too?").
- **When a guess is not a coin flip, draw.** Deliver v1 with the brief's assumption list; a user corrects a
  drawing faster than they answer abstract questions.
- Everything you guessed also goes into `meta.open_questions` and the delivery note, so nothing is decided
  silently.

`figure_kind` maps to the corpus's `depicts` vocabulary: `whole-system`=whole-system architecture,
`subsystem`=one subsystem, `request-path`=one path/request flow, plus `comparison` and `deployment`.
It predicts numbering: request-path figures are numbered 52% of the time, deployment 0%.

The spec is a contract for the linter and for round-tripping feedback, not a cage: every object takes
`notes` and `x-*` fields, every kind has `other`, the template list has `custom`. When the paper's figure
does not fit the vocabulary, describe it in `notes` and draw what the paper needs.

---

## 2. Paper text → components, containers, flows

Read, in this order: the figure's own caption, the overview/design section it belongs to, and the
section headings (they name the contributed components). Then apply these rules.

| in the paper | in the spec |
|---|---|
| a named, capitalised component ("the Sub-Microbatch Partitioner") | a `node`, label spelled exactly as the paper spells it |
| "A **sends / returns / invokes / queries / writes** X to B" | an `edge` A→B with `label` = X |
| "A **consists of / contains / runs inside** B" | `nodes[B].parent = A`, not an edge |
| "A **uses / relies on** B" with no data named | `edge` with `kind: dependency`, `style: dotted` |
| a host / device / plane / trust / process boundary | a `container` — `solid` if physical, `dashed` if logical |
| named tiers or planes ("Control Plane / Serving Plane") | `lanes[]` with `kind: tier`, names verbatim |
| phases over time (offline/online, phase 1..3) | `lanes[]` with `kind: phase` (vertical), or two containers if there are only two |
| "each worker / N GPUs / a pool of" | **one** node with `multiplicity: "xN"` — never N nodes |
| a component introduced in its own §section | `role: novel` plus `section_ref` |
| an existing system by name (PyTorch, Linux, a peer service) | `role: existing` or `external` |
| data at rest / a table / a log | `kind: store` |
| a queue, a ring, a batch buffer | `kind: queue` |
| GPUs, accelerators, worker processes | `kind: compute` |
| a user, a tenant, a client program | `kind: actor` |
| a picture: a sample input or output, a photo, a screenshot, a rendered result, an icon | `kind: image` with `image: {src, content}` (a small picture or icon inside a box: `image` on that node) — the file, never a URL (§4 "Bitmaps") |

Four rules that decide most arguments:

1. **Every labelled box is a node; every node carries a label.** Two boxes with the same label is a
   recorded weakness — disambiguate in the spec, not in the caption.
2. **Edge endpoints are nodes by default.** When the prose names a group ("the planner sends to the
   workers"), retarget the edge at the representative node inside the group. When the whole group
   really is the endpoint (a control arrow onto a frame, three inputs into a planner box), the edge may
   end on the container or lane: the validator warns, and the linter checks the arrow against the frame.
   A node can never hold other boxes -- anything that contains boxes is a container.
3. **`role` before `emphasis`.** Half the boxes in a typical figure are the paper's own, so `novel`
   is not emphasis; `emphasis: accent` is the saturated fill and at most two boxes get it.
4. **Cut before you draw.** If the overview names more than ~13 boxes, keep the ones on the main
   path and nest or drop the rest (§6). The corpus's dominant failure is too much in too little space.

---

## 3. Choosing template, palette, encoding

- **Template** — work down the table in [`layouts.md`](layouts.md#choosing-a-template) and take the
  first match. The core frame goes in `meta.template`; the added patterns it composes with go in
  `meta.modifiers` (e.g. `layered` + `["replicated-grid", "overview-with-inset"]`). Two cheap checks:
  ≥7 ordered flows → `pipeline`/`control-loop`; ≤4 flows with ≥8 boxes → `matrix`/`layered`/
  `nested-stack`. Then read that template's section for arrangement, numbering and pitfalls.
- **Palette** — pick by `when_to_use` in [`palettes.json`](palettes.json). Shortcuts:
  `blue-orange` for a whole-system overview, `grey-scaffold` when the paper extends someone else's
  system, `warm-bands` when the *regions* are the message, `amber-highlight` for baseline-vs-ours,
  `greyscale` for print-first, `multi-hue-categorical` only with a legend; a named-style palette (`charon`) only
  together with `meta.style` of the same id. Then decide the **ground**: the
  `*-outline` twins (`blue-outline`, `ink-outline`, `pastel-outline`, `green-outline`, `greyscale-outline`,
  `categorical-outline`) draw containers as outlines with no fill — the corpus norm (49%) and the right choice
  with nesting ≥ 2; `blue-ground` / `cream-ground` / `green-ground` tint one dominant region, `pastel-regions`
  gives each region its own pale tint. Set `custom` only when
  the user gives hexes, and then fill `style_overrides.palette_roles`.
- **Encoding** — [`encoding.md`](encoding.md) Part D is the default table; do not re-derive it.
  `role`→fill, `emphasis`→accent, `edge.kind`→line style, `multiplicity`→stacked box + count.
  Dashed has **one** job per figure: group boundary, control flow, or optional edge — never two.
- **Legend** — leave `legend.mode: "none"` (78% of the corpus). Switch to `explicit` when more than
  4 semantic fills are in play, when line style or arrow colour carries meaning on *unlabelled*
  edges, or when a glyph is not self-explaining; then point the decoded elements at it with
  `legend_ref` so the linter can check the pairing. Place it `inside`, within a box-width of
  something it decodes.

---

## 4. The SVG contract

What the step-6 linter checks, and what makes a user's later edits round-trippable.

**Root element**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 246 208" width="246pt" height="208pt"
     font-family="Calibri, Carlito, 'Helvetica Neue', Arial, sans-serif" font-size="6.5"
     data-spec="dip-fig6" data-spec-version="1">
```

- `viewBox="0 0 <meta.width_pt> <height ≤ meta.max_height_pt>"`; **1 user unit = 1 pt**, so every
  number in the file is already a print measurement.
- The font stack is declared **once** on the root (`meta.font` resolves to it), not per `<text>`.
- Labels are real `<text>`; never outlined to paths. No gradients, no filters, no external references
  of any kind (no `@font-face` URLs, no cross-document `<use href>`, no CSS imports, no `<image>` linked
  to a URL). Arrowheads are `<marker>`s in a local `<defs>`. Bitmaps are allowed as content — see
  "Bitmaps" below.

**One `<g>` per spec element, wrapping its shape *and* its label**

| spec array | group id | required attributes |
|---|---|---|
| `nodes[]` | `n:<id>` | `data-kind="node"`, `data-role`, `data-parent` if it has one |
| `edges[]` | `e:<id>` | `data-kind="edge"`, `data-from`, `data-to`, `data-edge-kind`, `data-step` if numbered |
| `containers[]` | `c:<id>` | `data-kind="container"`, `data-role` |
| `lanes[]` | `l:<id>` | `data-kind="lane"`, `data-order` |
| `steps[]` | `s:<n>` | `data-kind="step"`, `data-attached-to` |
| `annotations[]` | `a:<id>` | `data-kind="annotation"`, `data-anchor` if it has one |
| `legend` | `legend` | `data-kind="legend"`; each row `legend:<item-id>` with `data-kind="legend-item"` |

```svg
<g id="n:span-parser" data-kind="node" data-role="novel" data-parent="agent">
  <rect x="12" y="30" width="64" height="18" rx="2"/>
  <text x="44" y="41" text-anchor="middle">Span Parser</text>
</g>
<g id="e:e-deploy" data-kind="edge" data-from="pipeline-schedule-searcher"
   data-to="gpu-training-workers" data-edge-kind="control" data-step="4">
  <path d="M120 96 V70 H176" marker-end="url(#arrow)"/>
  <text x="140" y="66">deploy schedules</text>
</g>
```

- **Paint order:** lanes → containers → edges → nodes → step markers → annotations → legend.
- **Replicas.** A node or container with `multiplicity` is drawn as two concrete copies plus an
  ellipsis. The second copy is `n:pim-ctrl~2` with `data-replica="2"`; the ellipsis is
  `n:pim-ctrl~ellipsis` with `data-kind="ellipsis"`. The count stays on the one spec entry.
- **Symbols.** Copy a library symbol's markup inline inside the node's group, keeping its
  `<g data-symbol="cylinder">` wrapper — never `<use>` an external file. The linter ignores the
  symbol's parts when it looks for the node's box and skips the label-centring check on icon + label
  nodes, so an icon-over-label actor needs no extra rectangle. **The library is a
  convenience, not a constraint: if a component has no symbol, draw it with plain shapes and leave
  `data-symbol` off.** `nodes[].symbol` may hold a free-text description instead of a library name.
- Helper shapes *inside* a group need no ids; nothing outside these groups should carry one.

**Placing labels, drawing to scale, labels beside their box**

- **Where a label goes.** `python3 scripts/place_text.py --font <key> --size 6.5 center --box x,y,w,h "Label"` prints
  the `<text>` with its baseline: the label's glyph ink (tallest glyph to lowest descender, read from the font) is
  centred on the box, the same model the linter checks with, so `centre.*` and `text.padding` agree with it. Add
  `--rotate -90` for a label turned up a narrow bar (it centres the label across the bar), `\n` for two lines.
  `place_text.py ... line --at x,baseline @badge:1 "text"` lays out a sentence or a legend entry with an inline
  step disc (`<g data-symbol="badge">`, whose digit may go 1 pt below the type floor like a step badge's). When a
  script generates the SVG (a `make_fig.py` that writes every box), import the same code instead of running the
  CLI per label: `from place_text import place, svg_text` (with `scripts/` on `sys.path`) — `place(text, (x, y, w,
  h), size, font, bold, rotate)` returns the baseline, the `rotate()` transform and whether the box leaves 1.5 pt;
  `_svgkit.ink_band(text, size, font, bold)` gives the ink above / below the baseline. Write `y` as the alphabetic
  baseline; a `dominant-baseline` other than `auto` is measured correctly but is harder to edit by hand.
- **`data-scale="data"`** on a group (a `p:` panel, a container, a node) whose geometry comes from numbers — bar
  lengths, Gantt rows, positions on a value axis. Two bars of 1,760 and 1,712 differ by a fraction of a point
  on purpose, so the linter gives no snapping advice (`align.*`) inside it; every other check still runs.
- **`data-label="outside"`** on a node group, or on one `<text>` of it: that label sits beside its box on
  purpose — a total at the end of a bar, a value next to a cell too narrow to hold it. `text.overflow` then only
  requires it to be wholly clear of the box, and the centring check leaves it out.

**Bitmaps**

Use a bitmap wherever the figure needs one — a sample input or output, a photo, a screenshot, a rendered
result, an icon or logo. 14.6 % of the good architecture figures carry a bitmap or photo panel, and bitmaps
are no quality signal either way (`encoding.md` A13, `style-rules.md` §6). What follows are the portability
and print rules that make one survive delivery.

```svg
<g id="n:input" data-kind="node" data-role="external">
  <image x="8" y="30" width="40" height="30" href="bitmap-input.png"/>
  <rect x="8" y="30" width="40" height="30" fill="none" stroke="#8c8c8c" stroke-width="0.6"/>
  <text x="28" y="69.5" text-anchor="middle" font-size="6.5">Input frame</text>
</g>
```

- **Where.** Inside the group of the spec element it shows: a node with `kind: image` (the picture is the
  node), or any box with a small picture in it. The spec names the file in `nodes[].image.src`.
- **The file** (portability and print rules, not style): PNG for screenshots, renders, icons and anything with
  flat colour or text; JPEG for photos; convert anything else first. Keep it in the figure folder and link it
  by a relative path in `href` — **never a URL** (`http(s)://`, `//…`): a figure must not depend on someone
  else's server. Download a picture found online first (check its licence, credit it in the caption). A
  `data:` URI works too.
- **Geometry.** Explicit `x y width height` in pt. Give the box the picture's aspect ratio (the default
  `preserveAspectRatio` shows the whole picture), or crop on purpose with `preserveAspectRatio="xMidYMid slice"`;
  never `none`, which stretches it. Pixels: ≥ 150 per inch at print size, 300 for photos — a picture 40 pt wide
  needs ≥ 84 px, better 167 px.
- **Frame and label.** A thin frame on the picture's box, in the box stroke weight, makes a photo or screenshot
  read as a panel (`layouts.md`, composite-figure). The label is a caption under or beside the picture, or a
  short label laid on it with enough contrast; the linter takes the picture as the node's box, accepts a caption
  outside it, flags a label straddling its edge (`text.overflow`) and skips the centring check.
- **Delivery.** `embed_fonts.py` inlines every bitmap into the SVG as a base64 data URI, byte for byte, the
  same way it embeds the fonts: the delivered file stands alone. It writes the link as `xlink:href` (declaring
  `xmlns:xlink`), the SVG 1.1 spelling Office, Illustrator and older Inkscape read, and refuses to deliver while
  an image is a URL, missing, or not PNG / JPEG. `render.py`, `lint.py`, `check.py`, `preview.py` and
  `export_pdf.py` load local files from the SVG's folder and never fetch a URL; `svg2pptx.py` turns each
  `<image>` into a native picture.
- **What `lint.py` checks.** Errors: `image.external` (a URL), `image.missing` (no file, undecodable),
  `image.format` (not PNG / JPEG), `image.box` (no width / height — SVG 1.1 viewers draw it at zero size),
  `image.xmlns` (`xlink:href` without `xmlns:xlink`). Warnings: `image.resolution` (< 150 ppi at print size),
  `image.aspect` (stretched, or letterboxed in its box), `image.orientation` (an EXIF rotation some viewers
  ignore), `spec.image` (the spec names a bitmap the group does not draw). Info: `image.heavy` (far more pixels
  than print needs), `image.aspect` for a deliberate slice, `spec.image` for a drawn bitmap the spec omits.

---

## 5. User feedback → which field changes

Content feedback ("that box is not new", "there is also a cache", "the main path goes through the
scheduler") lands in the **brief** first, then in the spec, then in the drawing. Layout and style feedback
("too crowded", "make it double column", "other colours") goes straight to the spec fields below. Keep the
brief, the spec and the SVG together in the working folder so the three never drift apart.

Apply the change to the spec, bump `meta.version`, redraw. Never patch the SVG without patching the
spec — the linter compares the two.

| the user says | change | how |
|---|---|---|
| 太挤 / 看不清 / too busy | `nodes[]`, `size_hint`, `max_height_pt` | merge or drop off-path boxes first, grow the canvas second (§6) |
| 看不出哪个是新的 | `nodes[].role`, `nodes[].emphasis` | everything reused → `existing` (grey); ≤2 boxes get `accent` |
| 主路径不清楚 | `edges[].weight`, `steps[]`, `meta.step_markers` | one contiguous `main` chain; 3–8 circled steps; list them in the caption |
| 改成双栏 | `meta.column`, `width_pt` 504, `max_height_pt` ~168 | also revisit `direction` (double column is a strip → left-right) and the `grid` hints |
| 换个配色 | `meta.palette` | only touch `style_overrides.palette_roles` if the user names hexes |
| 换成某篇论文的风格（如 Charon 风格） | `meta.style`, `meta.palette`, `meta.font` | only a style listed in `references/styles/README.md`; read its card, then redraw — weight, outlines and framing change, layout does not |
| 箭头太乱 | `edges[].route`, `from_side`/`to_side`, `route_hint`, `constraints[]` | orthogonal by default; feedback/bypass edges route along the opposite margin |
| 这两个应该挨着 | `constraints[]` `same-row`/`same-column`, or a shared `parent` | |
| 名字不对 / 术语要改 | `nodes[].label`, `meta.caption_draft` | labels are the paper's words, verbatim |
| 加个图例 | `legend.mode: "explicit"` + `legend_ref` on what it decodes | place `inside` unless it is shared by panels |
| 这个框是我们系统的边界 | `containers[].kind: "dashed"`, `role: "novel"` | then no other dashed meaning in the figure |
| 想看时间 / 并发 | `meta.modifiers: ["phase-lanes"]`, `lanes[]` | lanes = who (horizontal), phases = when (vertical rules) |
| 要和 baseline 对比 | `meta.template: "baseline-vs-ours"`, `panels: 2`, `role: "baseline"` | identical skeleton, one marked difference |
| 字太小 | `style_overrides.font_size_pt` | floor 6 pt; the real fix is almost always fewer boxes |
| 放一张样例图 / 照片 / 截图 / 渲染结果 | a node `kind: image`, `image.src` + `image.content` | the file goes in the figure folder (a web picture is downloaded first); PNG for screenshots, JPEG for photos; ≥ 150 ppi at print size (§4 "Bitmaps") |

---

## 6. Budgets

Everything below is measured; sources are [`style-rules.md`](style-rules.md) (size table, §9),
[`layouts.md`](layouts.md) (canvas, cross-template table) and
[`anti-patterns.md`](anti-patterns.md) §3. The validator warns on all of them.

| budget | single column | double column |
|---|---|---|
| `width_pt` | **240** target (245–252 typical, 210–309 outer) | **504** target (506–514 typical, 430–603 outer) |
| `max_height_pt` | median 153, soft max **257** | median 168, soft max **313** |
| labelled boxes (`nodes`+`containers`+`lanes`) | q3 **13**, p90 17, and ~1 box per 3,900 pt² of canvas | q3 20, p90 24, same area rule |
| minimum boxes | **6** — below that the figure reads as unfinished | 6 |
| edges | median 6, p90 **10** | up to 16 |
| lanes | 2–3 | 4 |
| steps | 3–**8** | 3–8 |
| `emphasis: accent` nodes | **≤2** | ≤2 |
| container nesting depth | **≤3** (61% of the corpus stops at 2) | ≤3 |
| distinct fills | 4–7 plus grey | 4–7 plus grey |
| aspect (`width_pt`/height) | 1.0–2.9, median 1.7 | 1.8–5.4, median 3.0 |
| font sizes | 6.5 pt body, 5 pt floor, largest ≤1.5× body | same — type does not scale with the canvas |

A 10-box figure that is not ~246 pt wide is either double column or too dense. Going wider is a page
constraint, not a quality lever: when a single-column figure will not fit, make it **taller**, or
cut boxes.

---

## 7. Mechanism figures (`meta.kind = "mechanism"`)

The second figure kind: how *one part* of the system works, not the whole system. Everything above still
applies (ids, the SVG contract, palettes, budgets by column) with these additions. The vocabulary is the
one of `references/mechanism/` and of the mechanism semantic records (`paper-figure-corpus/references/
semantics-schema-mechanism.md`); the reverse-engineered example is `assets/specs/examples/asplos25-006_fig1.json`.

The group, base and arrangement fields *describe* the figure you have decided to draw so the tools can help
(repeat panels, count budgets fairly, warn about missing pieces); they do not choose the figure for you. The
corpus vocabulary is a reference to lean on where it fits — `group: other`, `arrangement: other`,
`base: other` plus a `notes` line are the right values when it does not, and the validator only *warns* about
mechanism structure.

**Deciding the kind (brief stage).** A whole-system overview → architecture. Something that shows what
happens inside one component, one data structure, one exchange, one decision, or contrasts alternatives →
mechanism. Both at once → pick the one the caption leads with; the other becomes an inset or a second figure.

**`meta.mechanism`** — the five groups decide the plan (priority comparison > evolution > logic >
walkthrough > anatomy; `groups` lists the secondary ones):

| group | what is drawn | spec blocks it needs |
|---|---|---|
| `comparison` | the same template once per alternative | `panels[]` with `axis: alternatives`, `differs` / `deltas[]`, optional `verdict` |
| `evolution` | one instance in successive frames | `panels[]` with `axis: time`, `frame_template: identical`, `deltas[]` per frame |
| `logic` | a state machine or decision flow | nodes `kind: state` / `decision`, edges `kind: transition` with `guard` (every branch labelled) |
| `walkthrough` | one structure + numbered markers along a path | `steps[]` (with `carries` when one object is followed), `meta.step_markers` |
| `anatomy` | one structure opened up at one moment | nodes / containers / edges only; `base` picks the parts |

`worked_example: true` when the values are the content: list them in `values[]` (role input / intermediate /
result, `links` between the places one value recurs — the drawer gives linked values one colour and draws
results as "= result" cells). `base` names the drawn surface (component, data-structure, graph, tree,
timeline, topology, table, code, state-machine, flowchart, scene, circuit, or `other` with a note) and selects the parts library subset
(`assets/symbols/index.json` → `by_subtype.mechanism`, families under `by_family`). `arrangement` is the
mechanism counterpart of `meta.template` (`meta.template` is then `"mechanism"`): `panels-row` /
`panels-column` / `panels-grid` for alternatives, `frames-row` / `frames-column` for time, `inset` for a zoom,
`stacked-timeline` for lifelines over one axis.

**Panels and deltas.** Declare each panel or frame in `panels[]`; give panel-specific elements a `panel`
field; leave the shared template elements without one — the drawer repeats them in every panel, at the same
positions when `frame_template` is `identical`. Then say what each panel changes in `deltas[]`
(`added` / `removed` / `changed` / `highlighted` / `moved` / `replaced`, `with` = the new label or value,
`marking` = colour / bold-stroke / dashed-ghost / strike / callout / badge, defaulting to
`meta.mechanism.delta_marking`). An evolution figure is therefore *template + one delta list per frame*; a
comparison is *template + what each alternative does differently* — that discipline is what keeps repeated
panels aligned. Budgets count the template once: labels repeated across mirrored containers or panels count
as one box, and identical accent bars as one saturated fill.

**Timelines** (`base: timeline`): one `lanes[]` entry per actor with `kind: lifeline`, optionally one
`kind: time` ruler, messages as edges `kind: message` ordered top to bottom (their `order` is the time order);
phase brackets are `annotations[]` of kind `bracket`. **Data structures** (`base: data-structure`): slots and
cells are nodes `kind: slot` / `cell` with `grid` hints, references between them edges `kind: pointer`.

**SVG contract additions.** One `<g>` per panel `p:<id>` with `data-kind="panel"` wrapping that panel's
elements (template elements repeated inside a panel get `data-panel="<id>"` and an id suffix `@<panel>`,
e.g. `n:fwd@p-fsdp`); deltas need no group of their own — the changed element carries `data-delta="<delta id>"`;
values are `v:<id>` with `data-kind="value"` inside the node they sit in. Paint order inside a panel is the
usual one. What `lint.py` makes of this (all advisory — warn / info, never an error, because how the figure is
laid out is your call): `panel.missing` (a `panels[]` entry without its `p:` group), `panel.member` (an element
with a `panel` field drawn outside that panel), `panel.identical` (with `frame_template: identical`, a template
copy at a different offset in one panel), `panel.copy` (info: a template element missing from a panel),
`delta.target` / `delta.unmarked` (a delta whose element cannot be found / carries no `data-delta`),
`value.missing`, `guard.unlabelled` (an edge with a `guard` that draws no text). Budgets count distinct ids, so a
structure repeated in three panels is counted once.

**Feedback → field.** "这两栏要对齐" → `frame_template: aligned` (+ `constraints` same-row/same-column across
panels); "把变化的地方标红" → `meta.mechanism.delta_marking: colour`; "第 3 步不对" → the `steps[]` entry;
"加一个 before" → a new panel with `axis: time`, order 0, and deltas on the others; "这个值要突出" →
`values[].highlight`.

---

## 8. Composite figures: several kinds of drawing in one figure

**When.** The user asks for one overview figure that holds unlike drawings — a structure, numbers drawn to
scale, a timeline, a control loop — because together they tell one story (the "big Figure 2" of a paper: the
background figure of the Charon style exemplars, `assets/exemplars/styles/charon/`). If the drawings share no
component, they are two figures (`layouts.md`, composite-figure). The panels of a composite are not
alternatives or frames of one template, so `panels[]` alone cannot describe them; parts can.

**Spec.**
- `meta.kind` is the kind of the main story: `mechanism` when the parts explain how one thing works and carry
  values (most composites), `architecture` when a system overview dominates. Either kind may hold parts.
- One `panels[]` entry per lettered part: `axis: "part"`, `view` (`structure`, `values`, `timeline`, `loop`,
  `table`, `chart`, `other`), `panel_label: "(a)"`, `order` = reading order. `meta.panels` = number of parts.
- Inside a part, alternatives or frames are ordinary panels with `parent: "<part>"` (the four placements of a
  load chart, the two timelines). Nodes declared on the part (`panel: "<part>"`) are the template its sub-panels
  repeat (`n:<id>@<sub-panel>` copies); a node of one sub-panel declares that sub-panel.
- An element drawn in several parts — a step that appears in the structure *and* on the timeline — gets no
  `panel`; draw its copies with the `@<panel>` suffix.
- SVG: one `<g id="p:<part>" data-kind="panel">` per part, wrapping its sub-panels' `p:` groups; mark what is
  drawn to scale with `data-scale="data"` (the part, or just its scaled sub-panels).

**Reading across the parts.** One numbering for the whole figure (①… for steps that recur in several parts),
one legend, the same identity colour for the same thing in every part (the hot item is the same pink in the
structure, the chart and the timeline). Give what the parts share the same geometry: lanes of the same actors
in the same order and row height in parts that sit above each other, so the eye can run straight across.
Titles with letters under each part; parts in reading order (left → right, top → bottom); 8–12 pt gutters and no
connectors between parts, except the leader of a zoom.

**Budgets.** Each part is held to the single-column budget (§6; label-distinct in a mechanism figure); the
figure's total is reported, not judged. Double column at 504 pt, height up to the double-column soft max
(313 pt).

**When it does not fit and the user still wants one figure** — work down this list before proposing a split:
1. Draw what every lane does identically once: one tall box across the lanes (Attention on every GPU), or `×N`.
2. Take words out of boxes: a title and at most one line per box; rules, conditions and parameter lists go to
   the caption, labels on arrows only where the reader cannot do without them.
3. Put numbers in one values part (a small to-scale chart) or the caption, not in every box.
4. Collapse empty structure (spare slots, placeholders) into one dashed outline with a count.
5. Grow the figure taller rather than the type smaller: 6 pt stays the floor.
6. Only then propose two figures, cut where each keeps its own story (overview + detail, structure + numbers).
