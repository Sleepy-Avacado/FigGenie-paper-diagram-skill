# Exemplar figures (v2 layout, 2026-09-07)

Reference figures from published OSDI / NSDI / SOSP / ASPLOS papers, chosen from the human-rated
`good` architecture diagrams of the corpus, reviewed by hand (drops + stars) and annotated by review
agents after looking at every figure. Reproduced for style reference only: they are there to strengthen a
layout that comes from the figure's own content, not to be copied — a drawer borrows the device that serves
the figure at hand and keeps whatever that figure needs that no exemplar shows.

```
index.json                    everything: figures, template counts, total size
<template>/index.json         that template's exemplars in order (starred first): id, star,
                              why_chosen, what_to_learn, dir
figures/<id>/source.svg       author SVG when the paper shipped one, else the SVG extracted from the
                              published PDF (PyMuPDF; text kept as <text>, fonts embedded)
figures/<id>/preview.png      render of the author SVG (only when an author source exists)
figures/<id>/print.png        the figure as extracted from the published PDF, at print size
figures/<id>/semantics.json   full semantic record (components, flows, layout, style, encoding)
figures/<id>/manifest.json    provenance, layout fields, and every template this figure illustrates
```

Each figure is stored once and referenced from every template it illustrates (`manifest.json` →
`templates[]`). `star` marks the must-see exemplars that `references/layouts.md` lists in each
template's table. Rebuild from `scripts/distill/exemplar_selection.json` with
`python3 scripts/distill/build_exemplars.py --clean`; refresh the tables in layouts.md with
`python3 scripts/distill/update_exemplar_tables.py --max-rows 30`.

## Mechanism figures (kind 2, added 2026-09-20)

The same tree also holds the exemplars for **mechanism figures** (figures that show how one part works:
comparison / evolution / logic / walkthrough / anatomy, see `references/mechanism/layouts.md`). They were
chosen from the 152 exemplar candidates of the mechanism corpus (human-rated `good`, one semantic record
each, written by an agent that looked at the figure), reviewed by hand on
`exemplar-review/mechanism/review.html` (5 dropped, 73 starred, 1 moved) and built with
`python3 scripts/distill/build_exemplars.py --kind mechanism` from
`scripts/distill/exemplar_selection_mechanism.json` (made by `scripts/distill/mech_exemplar_selection.py`
from the review decisions).

```
index.json                       `mechanism` block: selection, n_figures, n_slots, by_group; the `figures`
                                 list carries every figure of both kinds (`kind` says which)
mechanism/<group>/index.json     that group's exemplars in order (starred first): id, star, why_chosen,
                                 what_to_learn, note_source (doc = written by the layouts.md author for its 40
                                 exemplars, agent = rewritten by a note agent that looked at the figure,
                                 record = the semantic record's reusable_patterns), primary, dir
figures/<id>/                    exactly as for architecture figures; manifest.json has `kind: "mechanism"`
                                 and the mechanism layout fields (base, arrangement, panel_count,
                                 frame_template, delta_marking, step_markers, worked_example, ...) plus
                                 `groups[]` = every group this figure is listed under, with its notes
```

Mechanism figures vary far more than architecture figures, so these exemplars are reference and
reinforcement in the strictest sense: the plan for a new figure is derived from what that mechanism has to
show, and an exemplar is opened to sharpen that plan, never to supply it.

A figure is listed under its **primary** group (the record's first group, or the group the reviewer moved
it to) -- starred there when starred at all -- and unstarred under the record's secondary groups, so
`walkthrough` holds 43 slots for 26 primary figures. 146 figures / 175 slots (one candidate,
`nsdi25-043_fig6`, is excluded because its PDF text is outlined). Refresh the tables in
`references/mechanism/layouts.md` with `python3 scripts/distill/update_exemplar_tables.py --kind mechanism`.
An architecture rebuild (`build_exemplars.py --clean`) keeps `mechanism/` and the mechanism figure dirs;
`--kind mechanism --clean` removes only those.

## Named styles (added 2026-10-09)

`styles/<style>/` holds the figures of one paper whose look the user asked to reuse (`styles/charon/`: 7
figures of the Charon paper, MLSys 2026). Same files per figure as above, plus `style` and
`origin: style-reference` in `manifest.json`; `styles/<style>/index.json` lists them with their templates /
groups and lessons. They are not rated corpus figures and are built by
`scripts/distill/build_style_exemplars.py`, not `build_exemplars.py` (whose `--clean` leaves `styles/` alone).
`scripts/find_exemplars.py` searches them together with the corpus; `--style <style>` lists them first. Read
`references/styles/<style>.md` for how to use the look.
