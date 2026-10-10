# The figure brief — what the user confirms before anything is drawn

The brief is a short natural-language description of everything the figure will say. It is the
human-facing artifact: the user reads it, corrects it, and only then the agent derives the JSON spec
(`spec-schema.json`) and draws. Write it in the user's language; keep component labels exactly as they will
appear in the figure (usually English, as in the paper). Be complete rather than short: every component and every
flow that will be drawn gets its own clause (typically 200–500 words; a dense double-column figure may need more).
Lists are fine, JSON is not.

Why a brief and not the spec: people judge "is this the right figure?" from prose and a walkthrough far
faster than from field names, and a wrong brief costs one message while a wrong drawing costs a redraw.

## Sections (keep the order, drop a section only when it is truly empty)

1. **What this figure is** — one sentence: the system, what the figure shows (whole system / one subsystem /
   one request path / comparison / deployment), where it sits in the paper (e.g. §3 overview), single or
   double column.
2. **Components** — every box that will appear, in reading order, grouped by container / lane. For each:
   the label as it will be written, one clause on its job, and a tag: **new** (the paper's contribution),
   existing (reused, unmodified), external (another party's system), baseline (only in comparisons).
   Say what encloses what ("Host contains …; the Device side has …"). A picture the figure shows — a sample
   input or output, a photo, a screenshot, a rendered result — is a component too: say which file it is (the
   user's, or one you will produce) and where it came from; a picture found online is downloaded into the
   figure folder, never linked.
3. **Flows and the main path** — narrate the main path as numbered steps (① … ②…), each "from → to: what
   moves". Then the secondary flows in one or two sentences, and which of them are control / feedback /
   optional (these become dashed or dotted).
4. **The one point the figure argues** — what a reader should conclude in five seconds, and where the eye
   should start and travel.
5. **Layout and style intent** — the template and direction you will use and why (name the closest exemplar
   ids from `assets/exemplars/`: some of the template, some from the same field or drawing the same kind of
   objects, found with `scripts/find_exemplars.py`), palette family, whether there is a legend and step numbers, anything the
   user said about house style (fonts, colours, an existing figure to match). If they asked for a named style
   (`references/styles/`, e.g. "Charon 风格"), name it here and, for a series of figures, the identity colour
   of each component kind so later figures reuse it.
6. **Assumptions to confirm** — 3–5 yes/no items for what you inferred rather than read, each with its
   source ("§3.1 says 'we introduce', so Scheduler is new — right?"). These are the only questions the user
   must answer; everything else has a default.
7. **Caption draft** — one to three sentences the paper can use, including the walkthrough of the numbered
   steps if there are any.

## Rules

- Completeness beats brevity: if a box or an arrow will be in the SVG, it is in the brief. The user must be able
  to reconstruct the figure's content from the brief alone.

- Infer first, ask second. Read the paper / notes / chat before writing; mark what you inferred. Ask only
  where the inference would change the figure's structure and you cannot tell from the text.
- Never invent components or flows the source does not support; if the source is thin, say so in §6 and
  propose the smallest figure that is defensible.
- Budgets from the corpus (see `layouts.md`): typical figure 10 components, 6 flows; single column ≤ 13
  labelled boxes, double ≤ 20. If the brief is heavier, say what could be merged or moved to a second figure.
- Names in the brief must be the labels the SVG will carry; the spec ids are derived from them.
- After the user confirms, changes of *content* go into the brief first (then spec, then drawing);
  changes of *layout/style* go into the spec; both stay in the working folder next to the SVG.

## Example (from the minimal example figure)

> **What.** Figure 1 of the Example paper: a single-column request-path figure for §3.1, showing how a span
> travels from a client through the new parser to the pattern library and on to the backend.
>
> **Components.** Inside *Host*: **Client** (emits spans; existing), **Span Parser** (splits a span into a
> pattern and its parameters; **new**), **Pattern Library** (stores patterns; existing). Outside the host:
> **Backend** (external collector).
>
> **Flows.** Main path: ① Client → Span Parser: raw spans. ② Span Parser → Pattern Library: parsed patterns.
> Secondary: Pattern Library → Backend: periodic *sync* (control, dashed red).
>
> **Point.** The parser is the only new part and the only thing that touches every span.
>
> **Layout.** pipeline, left-to-right, single column (240 pt); palette blue-orange with the parser as the one
> accent; no legend (three roles are explained in the caption); one circled step. Closest exemplar:
> asplos26-132_fig6.
>
> **Confirm.** (a) Is Pattern Library existing infrastructure rather than part of the contribution?
> (b) Should Backend appear at all, or is it out of scope?
>
> **Caption.** Figure 1. Example pipeline. ① The client emits spans to the Span Parser (new), which ②
> updates the Pattern Library; the library syncs to the backend.

## Mechanism figures — the same brief, three sections read differently

A mechanism figure (`meta.kind: mechanism`) shows how *one part* works, and the reader's job is different: not
"what are the pieces and how are they wired" but "what is the difference / the order / the state / the shape I am
meant to see". Keep the seven sections; write §2–§4 like this, and keep the rest as above.

2. **What is drawn** — the structure(s) the figure shows (a component's internals, a data structure, a
   timeline of actors, a state machine, a table of values …), then what is **repeated** and what **differs**:
   "the same 4-slot buffer in three frames; only the occupied slots change", "two alternatives on one
   fwd / bwd / update template; ours adds the AllGather bar". Elements still get labels as they will be
   written and new / existing / baseline tags where that matters (a comparison usually has *ours* vs *baseline*
   instead of new vs existing).
3. **The story** — the path the reader follows, in whichever form the figure has: numbered steps along a
   structure (① … with what moves at each step), transitions with their guards ("on timeout → Candidate"),
   before → after deltas per frame ("frame 2: slot 3 evicted, slot 1 highlighted"), or the values of a worked
   example and where each one recurs (input → intermediate → result).
4. **The one point the figure argues** — what the reader must *see* in five seconds and where the eye goes
   first: "the two panels are identical except the red bar", "step ③ is where the copy happens", "the dashed
   states are the ones we add". If a verdict belongs in the figure (✓ / ✗, "ours"), say it here.
5. **Layout and style intent** — the group you lean on (comparison / evolution / logic / walkthrough / anatomy,
   `references/mechanism/layouts.md`), the drawn base (component, data-structure, timeline, state-machine,
   table …), the arrangement (one drawing, panels in a row / column / grid, frames, an inset) and why; the two or
   three closest exemplars from `assets/exemplars/mechanism/<group>/index.json` plus the nearest by domain and
   content from `scripts/find_exemplars.py` (named to learn from, not to
   reproduce — the layout follows this figure's needs); how the difference will be
   marked (colour on the changed element is the corpus default; ghost, strike, callout, badge are the
   alternatives) and whether there is a legend, step markers, a worked example. **"None of the five groups fits
   exactly" is a fine answer**: then describe the reading path in your own words and name the nearest
   exemplar anyway.

Budgets are label-distinct: a structure repeated in every panel counts once (`references/mechanism/style-rules.md`
§12). If a brief needs more than about 12 distinct labelled boxes in a single column, or more than four panels,
say what could be merged, elided (`…`, `×N`) or moved to a second figure.

### Example (from `assets/specs/examples/asplos25-006_fig1.json`)

> **What.** Figure 1 of the paper: a single-column mechanism figure for §2, contrasting two ways of training the
> same model — data parallelism with a full-parameter AllReduce versus the sharded ZeRO-3 / FSDP design.
>
> **What is drawn.** One template: two devices (Device 0 / Device 1, dashed boxes) each running *fwd → bwd →
> update* on a copy of the model, repeated in two stacked panels (a) baseline, (b) ours. What differs: in (b) each
> device holds only a shard, so an **AllGather** bar (new, blue) precedes fwd and bwd and a **ReduceScatter** bar
> replaces the AllReduce after bwd.
>
> **The story.** Read (a) left to right: fwd, bwd, then AllReduce of gradients (red label) across the two devices,
> then update. Read (b) the same way and notice the two added bars and the renamed collective; peak memory drops
> because the full parameters exist only during fwd / bwd.
>
> **Point.** Same pipeline, one added collective per phase — the extra communication is the price of the
> memory saving. The eye should land on the blue bars in (b).
>
> **Layout.** Group comparison, base component, arrangement panels-column (the template is a wide chain, so the
> alternatives stack), frame template aligned; difference marked by colour on the added elements; no legend
> (two colours, both named in the caption); no step numbers. Closest exemplars: `asplos25-038_fig1`,
> `osdi26-040_fig1`.
>
> **Confirm.** (a) Is the update step drawn in both panels, or only where it differs? (b) Should the panels be
> labelled (a)/(b) or by name ("DP", "FSDP")?
>
> **Caption.** Figure 1. Data parallelism (a) AllReduces full gradients after each backward pass; ZeRO-3 / FSDP
> (b) AllGathers the sharded parameters before forward and backward and ReduceScatters gradients, trading
> communication for peak memory.

