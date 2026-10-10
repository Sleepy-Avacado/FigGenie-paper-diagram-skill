#!/usr/bin/env python3
"""Distil the colour palettes of the systems-architecture figures into named families.

Input
-----
--semantics  lab/extracted/corpus_semantics.jsonl   one JSON record per figure; we use
             style.palette = [{"hex": "#4472c4", "used_for": "<free text>"}, ...]
--index      lab/extracted/corpus_index.csv         joined on (paper_id, fig); supplies
             type/subtype (we keep only diagram/architecture), tool, venue and a `style`
             JSON measured on the PDF-extracted SVG (palette.top, gray_frac, named).
--out        directory for the artefacts (default: scratchpad)

Pipeline
--------
(a) ROLE NORMALISATION.  `used_for` is free text ("light blue fill for the Scaling Plane
    container", "near-black text labels").  `normalise_roles()` maps it to the shared role
    vocabulary with ordered keyword rules; an entry may carry several roles (a dark neutral
    is genuinely both `stroke` and `text`), so we return a primary role plus secondaries.
    Rules were tuned by dumping the residue (`role_residue.txt`) and reading it -- see
    ROLE_RULES for the decisions that came out of that pass (panel-letter references such
    as "in panel (b)" are stripped so they do not read as containers; "section header" is
    text, not a container; "secondary"/"sub-box"/"variant" is module-alt; circled step
    numbers are accents).
(b) PER-FIGURE ROLE -> HEX.  Candidates per role are resolved with fixed rules: accent =
    highest chroma, container/lane/legend = lightest, stroke/text/arrow = darkest
    near-neutral, module = the least saturated non-grey (the "default box"); the remaining
    fills become module-alt (up to 3) and extra_fills.
(c) FEATURES + CLUSTERING.  Each figure becomes a vector of a 9-bin fill-hue histogram,
    weighted one-hots for the dominant and second *coarse* hue family, lightness/chroma
    statistics, grey share, distinct-family count, Office-theme share, pastel and
    monochrome flags, and the accent's family/lightness/chroma.  Ward agglomerative
    clustering over standardised features; k is swept and scored with silhouette, then
    under-sized clusters are merged into their nearest neighbour until 8-12 remain.
(d) REPRESENTATIVES + REPORTING.  Per cluster: medoid figure, then one hex per role -
    `module` and `accent` are the cluster's most common values for that role, the other
    roles take the medoid's value when it is usable for that role (ROLE_OK) and the
    cluster's modal usable value otherwise, with corpus-wide frequency as the tie-break.
    A coherence pass then guarantees the set reads as a palette (container separated from
    module, accent separated from module, lane distinct, monochrome families keep a grey
    accent); `rep_raw` keeps the pre-pass values so both are reported.  Finally WCAG
    contrast is audited and member counts / tools / venues / abstractions are summarised.
(e) CURATION (`CURATION`, `write_palettes`).  Hand-written names, descriptions and
    exemplars, matched to a cluster by exemplar overlap rather than by medoid id so the
    names survive small changes to the role rules.  `--palettes-out` emits
    references/palettes.json.

Outputs (in --out): figure_roles.json, role_residue.txt, role_multi.txt, role_stats.json,
clusters.json, cluster_report.md, k_sweep.txt.  With --palettes-out: references/palettes.json.

Re-runnable and deterministic:
    python3 palette_cluster.py --semantics lab/extracted/corpus_semantics.jsonl \
        --index lab/extracted/corpus_index.csv --out <scratch> \
        --palettes-out figgenie-paper-diagram/references/palettes.json
    python3 make_swatches.py          # redraws assets/palettes/*.svg from that JSON
"""
from __future__ import annotations

import argparse
import collections
import colorsys
import csv
import json
import os
import re

import numpy as np

# Repo root, used only to check that an exemplar's PNG really exists on disk.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
# Directory holding <paper_id>/ figure files; set_extracted_dir() points it at the corpus named by --index.
EXTRACTED_DIR = os.path.join(REPO_ROOT, "lab", "extracted")


def set_extracted_dir(path):
    global EXTRACTED_DIR
    EXTRACTED_DIR = os.path.abspath(path)


def rel_png(paper_id, svg_name):
    """Path of a figure's PNG preview, relative to the repo root when inside it (lab/extracted/... for the systems corpus)."""
    p = os.path.join(EXTRACTED_DIR, paper_id, (svg_name or "").replace(".svg", ".png"))
    rel = os.path.relpath(p, REPO_ROOT)
    return p if rel.startswith("..") else rel

# --------------------------------------------------------------------------------------
# Shared role vocabulary (must stay identical across the skill)
# --------------------------------------------------------------------------------------
ROLES = [
    "canvas", "container", "lane", "module", "module-alt", "accent",
    "stroke", "text", "text-muted", "arrow", "arrow-accent", "legend",
]

# Microsoft Office theme colours (same list as paper-figure-corpus/scripts/svg_features.py)
OFFICE = {
    "#4472c4", "#ed7d31", "#a5a5a5", "#ffc000", "#5b9bd5", "#70ad47", "#4f81bd",
    "#c0504d", "#9bbb59", "#8064a2", "#4bacc6", "#f79646", "#264478", "#9e480e",
    "#636363", "#997300", "#43682b",
}

# --------------------------------------------------------------------------------------
# (a) Role normalisation
# --------------------------------------------------------------------------------------

# Phrases that look like a role word but are not: figure-panel references ("in panel (b)",
# "(panel c)"), section numbers, and component names that merely contain "group"/"plane".
NOISE_RE = [
    re.compile(r"\(?\bpanels?\s*\(?[a-h]\)?[,)]?"),      # "panel (b)", "in panel c"
    re.compile(r"\bpanels?\s+[a-h]\b"),
    re.compile(r"\bsections?\s*\d[\d.]*"),                # "section 4.1"
]

# Ordered: the first matching rule gives the PRIMARY role, every match contributes a role.
ROLE_RULES = [
    # legend first -- an explicit mention always wins
    ("legend", r"\blegend"),
    # canvas: the page/figure background itself (rare -- style.background covers it)
    ("canvas", r"\b(page|figure|slide|canvas|whole[- ]figure)\s+background\b"
               r"|^\s*(plain\s+)?(white|off-white)\s+background\b"),
    # accent: emphasis of the contribution / the highlighted path / step badges
    ("accent", r"\bhighlight\w*|\baccent\w*|\bnovel\b|\bemphasi\w*|\bour\b|\bproposed\b"
               r"|\bcontribution\w*|\bkey insight\b|\bnew (component|module|box)\w*"
               r"|\bfocus (of|box)|\bcircled|\bstep[- ]numbers?\b|\bstep[- ]order\b"
               r"|\bcallout\b|\bmarking (the )?(the )?(paper|novel|new)\w*"),
    # lane: swimlanes, bands, zebra rows, timeline tracks
    ("lane", r"\bswim ?lanes?\b|\blanes?\b|\bbands?\b|\bstripes?\b|\bzebra\b"
             r"|\b(row|column)\s+(shading|background|panel|band)\b"
             r"|\b(header|zebra) rows?\b|\btracks?\b"),
    # container: outer group / region / plane / panel backgrounds
    ("container", r"\bcontainer\w*|\bpanels?\b|\bregions?\b|\bouter\b|\benclos\w*"
                  r"|\bgrouping\b|\bgroup (background|box|fill)|\bbackdrop\b"
                  r"|\bsurround\w*|\bwrapper\b|\bumbrella\b|\bbounding box\b"
                  r"|\b(plane|subsystem|module|node|host|system|cluster)s?\s+(background|container)\b"
                  r"|\bbackground(s)? (of|for|fill|shading|tint) the\b"),
    # module-alt: explicitly secondary / variant / sub-element fills
    ("module-alt", r"\bsecondary\b|\bsub-?box\w*|\bsub-?element\w*|\bvariant\b"
                   r"|\bsecond(ary)? (fill|colou?r)\b|\balternate\b|\bminor\b"),
    # arrow: connectors and flows ("line" only outside outline/pipeline/timeline/...)
    ("arrow", r"\barrow\w*|\bconnector\w*|\bflows?\b|\bdata ?flow\w*|\bedges?\b"
              r"|\blinks?\b|\bpaths?\b|\bconnecting lines?\b"
              r"|(?<!out)(?<!pipe)(?<!time)(?<!base)(?<!under)(?<!in)\blines?\b"),
    # stroke: outlines / borders
    ("stroke", r"\bborders?\b|\boutlines?\b|\bstrokes?\b|\bcontour\w*|\bfill/stroke\b"),
    # text-muted before text so "secondary text" lands in the right bucket
    ("text-muted", r"\b(secondary|muted|grey|gray|light|small|sub)[- ]?(text|labels?)\b"
                   r"|\bannotation text\b|\bsub-?labels?\b|\bitalic (text|annotation)\w*"),
    # text: labels, captions, titles, headers
    ("text", r"\btexts?\b|\blabel\w*|\bcaptions?\b|\bfonts?\b|\btitles?\b"
             r"|\bannotation\w*|\bheaders?\b|\bheading\w*|\bnumerals?\b|\btags?\b"),
]
ROLE_RULES_C = [(r, re.compile(p)) for r, p in ROLE_RULES]

# Manual overrides for phrases the keyword rules read wrongly (resolved by reading
# role_residue.txt / role_multi.txt).  Matched as a lowercase substring of `used_for`.
ROLE_OVERRIDES = [
    # "fill/stroke" is a box fill first, its outline second
    (r"\bfill/stroke\b", "module", ["stroke"]),
    # "X box/boxes" with an emphasis verb is an accent even without the word 'highlight'
    (r"\bmarking (boxes )?reused|prior work|\bunchanged\b|\bbaseline\b|\bexisting\b"
     r"|\boff-the-shelf\b", "module", []),
    # icons are drawn like modules, not like text
    (r"\bicons?\b(?!.*\blegend\b)", "module", []),
    # table/grid cells and matrix elements behave as modules
    (r"\b(table|grid|matrix)\s+cells?\b", "module", []),
]
ROLE_OVERRIDES_C = [(re.compile(p), pr, sec) for p, pr, sec in ROLE_OVERRIDES]


def normalise_roles(used_for: str):
    """Free text -> (primary_role, [all roles]).  Default primary role is `module`."""
    t = " " + (used_for or "").lower().strip() + " "
    for rx in NOISE_RE:
        t = rx.sub(" ", t)
    found = [r for r, c in ROLE_RULES_C if c.search(t)]
    if not found:
        for rx, pr, sec in ROLE_OVERRIDES_C:
            if rx.search(t):
                return pr, [pr] + sec
        return "module", ["module"]
    primary = found[0]
    # composite: an emphasised connector is arrow-accent, not two separate roles
    if "accent" in found and "arrow" in found:
        primary = "arrow-accent"
        found = ["arrow-accent"] + [f for f in found if f not in ("accent", "arrow")]
    # an entry that only says "border"/"text" for a coloured *fill* is still that role;
    # but a fill word present with a container word means the fill of the container
    # "light purple fill for the ... header" is a box fill that happens to mention a text
    # word; when a fill/background word is present the fill role wins the primary slot.
    if primary in ("stroke", "text") and re.search(r"\bfills?\b|\bbackground|\bshading\b", t):
        if "container" in found:
            primary = "container"
        elif "lane" in found:
            primary = "lane"
        elif "module-alt" in found:
            primary = "module-alt"
        elif not re.search(r"\b(border|outline|stroke|text|label)\w*\s+(only|colou?r)\b", t):
            primary = "module"
            found = ["module"] + found
    return primary, list(dict.fromkeys(found))


# --------------------------------------------------------------------------------------
# colour helpers
# --------------------------------------------------------------------------------------
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

HUE_BINS = ["red", "orange", "yellow", "green", "teal", "blue", "purple", "pink"]
HUE_EDGES = [(345, 15), (15, 45), (45, 70), (70, 160), (160, 200),
             (200, 255), (255, 290), (290, 345)]

# Coarse families used for the clustering one-hots: fine bins split near-identical blues
# and teals apart, which fragments the families a drawing agent actually cares about.
COARSE = ["red", "warm", "green", "cyan", "blue", "purple", "grey"]
COARSE_OF = {"red": "red", "pink": "red", "orange": "warm", "yellow": "warm",
             "green": "green", "teal": "cyan", "blue": "blue", "purple": "purple",
             "grey": "grey"}


def rgb(hexv):
    h = hexv.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hls(hexv):
    """(hue 0-360, lightness 0-1, chroma 0-1).

    We deliberately use *chroma* (max-min of RGB) rather than HLS saturation: HLS gives a
    pale peach such as #fbe5d6 a saturation of 0.83, which would let pastels win every
    "most saturated" tie-break.  Chroma ranks #fbe5d6 at 0.15 and #ff644a at 0.71, which
    matches how vivid the colours look on the page.
    """
    r, g, b = rgb(hexv)
    h, _l, _s = colorsys.rgb_to_hls(r, g, b)
    l = (max(r, g, b) + min(r, g, b)) / 2
    chroma = max(r, g, b) - min(r, g, b)
    return h * 360.0, l, chroma


def is_grey(hexv, chroma_thr=0.07):
    _, l, c = hls(hexv)
    return c < chroma_thr or l > 0.985 or l < 0.05


def is_neutral_dark(hexv):
    """A colour usable as an outline / body text: near-neutral and dark."""
    _, l, c = hls(hexv)
    return c < 0.18 and l < 0.55


def hue_family(hexv):
    h, l, s = hls(hexv)
    if is_grey(hexv):
        return "grey"
    for name, (a, b) in zip(HUE_BINS, HUE_EDGES):
        if a > b:
            if h >= a or h < b:
                return name
        elif a <= h < b:
            return name
    return "red"


def coarse_family(hexv):
    return COARSE_OF[hue_family(hexv)]


def rel_lum(hexv):
    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb(hexv))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def darken(hexv, factor=0.62):
    r, g, b = rgb(hexv)
    return "#%02x%02x%02x" % tuple(int(max(0, min(255, c * factor * 255))) for c in (r, g, b))


# --------------------------------------------------------------------------------------
# data loading
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# (e) Curation -- names, descriptions and exemplars for the families the clustering finds.
# Keyed by palette id and matched to a cluster by *exemplar overlap*, not by medoid: the
# medoid drifts when the role rules change, but a family keeps its members.  Every id,
# name, when_to_use and exemplar list below was written after looking at the exemplar PNGs
# (>=2 per family); the hexes all come from the data.
# --------------------------------------------------------------------------------------
CURATION = {
    "blue-orange": dict(
        id="blue-orange", name="Blue modules, orange accent",
        description="Light-blue component boxes on a light-grey ground, with one orange "
                    "box or arrow for the contribution; cream and pale-green as second "
                    "and third fills.",
        when_to_use="The default choice for a whole-system overview. Safest when the "
                    "figure has one obvious novel component and 6-15 boxes.",
        exemplars=["asplos26-127_fig3", "sosp25-053_fig4", "asplos25-157_fig2",
                   "sosp24-005_fig4", "osdi25-003_fig2"]),
    "green-red": dict(
        id="green-red", name="Green modules, red highlight",
        description="Pale-green component boxes with a mid-grey container; red is reserved "
                    "for the highlighted path, the error case or the outlined contribution.",
        when_to_use="Pipelines and layered stacks where one path (a failure, a fast path, "
                    "the paper's addition) has to jump out of an otherwise calm figure.",
        exemplars=["nsdi26-087_fig3", "asplos26-129_fig3", "asplos25-138_fig17",
                   "asplos26-066_fig6", "nsdi24-004_fig8"]),
    "cream-pastel": dict(
        id="cream-pastel", name="Cream and pastel mix",
        description="Cream default boxes with pale blue, green and pink alternates, dashed "
                    "grey containers, and a saturated orange only where emphasis is needed.",
        when_to_use="Dense figures with many small boxes of several kinds (encoder blocks, "
                    "queues, caches) where every box needs a fill but none may shout.",
        exemplars=["asplos26-077_fig3", "asplos25-100_fig3", "nsdi23-085_fig8",
                   "asplos26-026_fig6", "asplos26-080_fig5"]),
    "greyscale": dict(
        id="greyscale", name="Greyscale only",
        description="No hue at all: near-white boxes, a mid-grey container band, black "
                    "outlines and arrows; emphasis comes from weight and dashed outlines.",
        when_to_use="Print-first venues, figures that must survive a black-and-white "
                    "print-out, and figures whose message is structure rather than kind.",
        exemplars=["asplos25-031_fig1", "sosp23-013_fig3", "sosp24-040_fig1",
                   "sosp24-007_fig7", "osdi26-060_fig8"]),
    "grey-scaffold": dict(
        id="grey-scaffold", name="Grey scaffold with pastel tints",
        description="Grey is the default box and the container; cream, pale blue and pale "
                    "pink mark the few boxes that differ, with orange for the accent.",
        when_to_use="Figures that reuse an existing system: grey for what already exists, "
                    "a tint only where the paper adds or changes something.",
        exemplars=["asplos25-039_fig3", "nsdi24-023_fig3", "asplos26-129_fig5",
                   "osdi24-036_fig8", "asplos25-046_fig14"]),
    "blue-mono": dict(
        id="blue-mono", name="Blue monochrome",
        description="One blue family end to end -- pale blue fills, a mid blue for the "
                    "second tier and a strong Office blue for the accent and arrows.",
        when_to_use="Hardware and micro-architecture figures, and any figure where colour "
                    "should carry depth (light = outer, dark = inner) rather than category.",
        exemplars=["sosp23-026_fig3", "asplos26-076_fig2", "osdi26-018_fig7",
                   "asplos26-013_fig10", "asplos25-147_fig2"]),
    "warm-bands": dict(
        id="warm-bands", name="Warm container bands",
        description="Cream, peach and pale-green bands name the phases or planes; the "
                    "boxes inside stay pale, and a gold accent marks the key step.",
        when_to_use="Layered or two-plane figures where the *regions* are the message "
                    "(control plane vs data plane, offline vs online, per-section bands).",
        exemplars=["sosp24-041_figtex8", "osdi26-024_fig8", "sosp23-016_fig4",
                   "asplos25-098_fig2", "nsdi26-030_fig1"]),
    "high-contrast": dict(
        id="high-contrast", name="High-contrast primaries",
        description="Near-white boxes with heavy near-black outlines, a mid-grey container, "
                    "and fully saturated primaries (deep red, pure blue, orange) for the "
                    "few elements that matter.",
        when_to_use="Small single-column figures and TikZ figures that will be printed "
                    "small: maximum legibility, colour used sparingly and loudly.",
        exemplars=["osdi25-012_fig3", "asplos25-096_fig1", "sosp24-007_figtex6",
                   "nsdi26-082_fig2", "asplos26-013_fig2"]),
    "multi-hue-categorical": dict(
        id="multi-hue-categorical", name="Multi-hue categorical",
        description="Four to six distinct hues (green, pink, cream, blue) used as "
                    "categories rather than as decoration, a deep crimson accent, and "
                    "saturated chips from extra_fills for the legend swatches.",
        when_to_use="Figures where colour *is* the data: colour-coded flows, per-tenant "
                    "resources, heterogeneous engines. Always ship a legend with it.",
        exemplars=["asplos26-141_fig2", "asplos25-110_fig2", "asplos26-094_fig9",
                   "asplos25-110_fig1", "nsdi26-084_figtex4"]),
    "amber-highlight": dict(
        id="amber-highlight", name="Amber highlight on neutral",
        description="Neutral grey lanes and peach/white boxes, with a dark gold-amber fill "
                    "reserved for the one component or step the paper contributes.",
        when_to_use="Before/after and baseline-vs-ours figures: keep everything neutral and "
                    "let a single amber block carry the claim.",
        exemplars=["asplos25-082_fig1", "asplos26-019_fig1", "nsdi25-062_fig7",
                   "sosp25-047_fig3", "osdi26-046_fig8"]),
    "cool-grey-cyan": dict(
        id="cool-grey-cyan", name="Cool grey and cyan",
        description="Cool light-grey containers with pale cyan-blue boxes and a warm tan "
                    "counterpart, near-black outlines and a deep teal accent.",
        when_to_use="Orchestration and control-plane figures that need a quieter, cooler "
                    "look than blue-orange while still being in colour.",
        exemplars=["asplos26-036_fig8", "nsdi26-127_fig6", "asplos26-008_fig3",
                   "asplos26-019_fig4", "asplos25-151_fig1"]),
}

ROLE_VOCABULARY = {
    "canvas": "Page/figure background. White in 272/272 architecture figures -- never tint it.",
    "container": "Fill of an outer group or region box (a host, a plane, a subsystem).",
    "lane": "Fill of a swimlane / horizontal or vertical band (a phase, a tier, a timeline row).",
    "module": "Default component-box fill: the colour most boxes get.",
    "module-alt": "Second and third component fills, for a different *kind* of component.",
    "accent": "Fill that marks the novel component or the main path. At most 1-2 per figure.",
    "stroke": "Box outlines. Near-neutral and dark; 0.5-1pt in the corpus.",
    "text": "Primary label text. Near-black; never lighter than the module it sits on.",
    "text-muted": "Secondary text: annotations, units, greyed-out labels.",
    "arrow": "Default connector colour, usually the same neutral as `stroke`.",
    "arrow-accent": "Highlighted connector: the request path, the error, the new flow.",
    "legend": "Legend box background, when the legend sits inside the figure.",
}


def load(semantics_path, index_path, subtype="architecture"):
    csv.field_size_limit(10 ** 9)
    idx = {}
    with open(index_path, newline="") as f:
        for row in csv.DictReader(f):
            idx[(row["paper_id"], row["fig"])] = row
    figs = []
    with open(semantics_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            row = idx.get((rec["paper_id"], str(rec["fig"])))
            if row is None:
                continue
            if row["type"] != "diagram" or row["subtype"] != subtype:
                continue
            figs.append((rec, row))
    return figs


# --------------------------------------------------------------------------------------
# (b) per-figure role -> hex
# --------------------------------------------------------------------------------------
FILL_ROLES = ("container", "lane", "module", "module-alt", "accent", "legend")

# Is a hex usable for a role?  Applied when the cluster representative is chosen: a record
# may legitimately say "red box outlines", but a reusable palette needs a neutral `stroke`.
ROLE_OK = {
    "canvas":      lambda h: hls(h)[1] > 0.93,
    "container":   lambda h: hls(h)[1] > 0.80,
    "lane":        lambda h: hls(h)[1] > 0.82,
    "legend":      lambda h: hls(h)[1] > 0.82,
    "module":      lambda h: 0.40 < hls(h)[1] < 0.985,
    "accent":      lambda h: hls(h)[2] >= 0.25,
    "arrow-accent": lambda h: hls(h)[2] >= 0.28 and hls(h)[1] < 0.66,
    "stroke":      lambda h: is_neutral_dark(h),
    "text":        lambda h: hls(h)[1] < 0.32 and hls(h)[2] < 0.18,
    "text-muted":  lambda h: 0.28 < hls(h)[1] < 0.68 and hls(h)[2] < 0.14,
    "arrow":       lambda h: hls(h)[1] < 0.60 and hls(h)[2] < 0.25,
}
ROLE_DEFAULT = {
    "canvas": "#ffffff", "container": "#f2f2f2", "lane": "#f2f2f2", "legend": "#ffffff",
    "module": "#dae8fc", "accent": "#ed7d31", "arrow-accent": "#c00000",
    "stroke": "#404040", "text": "#1a1a1a", "text-muted": "#595959", "arrow": "#404040",
}


def figure_roles(rec, row, residue_sink, multi_sink=None):
    fid = f"{rec['paper_id']}_fig{rec['fig']}"
    cand = collections.defaultdict(list)   # role -> [hex]  (primary)
    cand2 = collections.defaultdict(list)  # role -> [hex]  (secondary)
    seen = []
    for p in rec["style"].get("palette") or []:
        hx = (p.get("hex") or "").strip().lower()
        if not HEX_RE.match(hx):
            residue_sink.append(f"{fid}\tBADHEX\t{hx}\t{p.get('used_for')}")
            continue
        seen.append(hx)
        primary, allr = normalise_roles(p.get("used_for", ""))
        if primary == "module" and not any(
                c.search(" " + (p.get("used_for") or "").lower() + " ")
                for _, c in ROLE_RULES_C):
            residue_sink.append(f"{fid}\t{hx}\tmodule(default)\t{p.get('used_for')}")
        if len(allr) > 1 and multi_sink is not None:
            multi_sink.append(f"{fid}\t{hx}\t{primary}<-{'+'.join(allr)}\t"
                              f"{p.get('used_for')}")
        cand[primary].append(hx)
        for r in allr:
            if r != primary:
                cand2[r].append(hx)

    def pick(role, key, pool=None):
        pool = pool if pool is not None else (cand.get(role) or cand2.get(role) or [])
        pool = list(dict.fromkeys(pool))
        return (sorted(pool, key=key)[0] if pool else None), pool

    roles = {}
    # canvas: style.background is "white" for the whole corpus
    bg = (rec["style"].get("background") or "").lower()
    roles["canvas"] = "#ffffff" if "white" in bg or not bg else "#ffffff"

    # accent = most saturated of the accent candidates
    roles["accent"], acc_pool = pick("accent", lambda h: (-hls(h)[2], hls(h)[1]))
    roles["arrow-accent"], _ = pick("arrow-accent", lambda h: (-hls(h)[2],))
    if roles["arrow-accent"] is None and roles["accent"]:
        roles["arrow-accent"] = roles["accent"]

    # container / lane / legend = lightest candidate
    for r in ("container", "lane", "legend"):
        roles[r], _ = pick(r, lambda h: (-hls(h)[1],))

    # stroke / text / arrow = darkest *neutral* candidate (coloured strokes exist in the
    # corpus but a reusable palette needs the neutral outline colour), else darkest.
    for r in ("stroke", "text", "arrow"):
        pool = list(dict.fromkeys((cand.get(r) or []) + (cand2.get(r) or [])))
        neutral = [h for h in pool if is_neutral_dark(h)]
        roles[r] = (sorted(neutral or pool, key=lambda h: hls(h)[1])[0] if pool else None)
    roles["text-muted"], _ = pick("text-muted", lambda h: (abs(hls(h)[1] - 0.45),))

    # module: least saturated *non-grey* fill (the default box), greys as fallback
    mod_pool = list(dict.fromkeys(
        (cand.get("module") or []) + (cand2.get("module") or [])))
    mod_pool = [h for h in mod_pool if h != roles.get("accent")]
    nongrey = [h for h in mod_pool if not is_grey(h)]
    if nongrey:
        roles["module"] = sorted(nongrey, key=lambda h: (hls(h)[2], -hls(h)[1]))[0]
    elif mod_pool:
        roles["module"] = sorted(mod_pool, key=lambda h: -hls(h)[1])[0]
    else:
        roles["module"] = None

    # module-alt: explicit alt candidates + the remaining module fills
    alt = list(dict.fromkeys(
        (cand.get("module-alt") or []) + (cand2.get("module-alt") or [])
        + [h for h in mod_pool if h != roles.get("module")]))
    alt = [h for h in alt if h not in (roles.get("module"), roles.get("accent"))]
    alt.sort(key=lambda h: -hls(h)[2])
    roles["module-alt"] = alt[:3]
    extra = alt[3:]

    # promote a saturated module fill to accent when the record named no accent
    if roles["accent"] is None:
        pool = [h for h in ([roles["module"]] if roles["module"] else []) + alt
                if h and not is_grey(h)]
        pool.sort(key=lambda h: -hls(h)[2])
        if pool and hls(pool[0])[2] >= 0.35 and pool[0] != roles["module"]:
            roles["accent"] = pool[0]
            roles["module-alt"] = [h for h in roles["module-alt"] if h != pool[0]]

    fills = list(dict.fromkeys(
        [h for r in FILL_ROLES for h in cand.get(r, [])]
        + [h for h in (cand.get("module-alt") or [])]))
    if not fills:  # figures whose every entry was text/stroke/arrow: fall back to all
        fills = list(dict.fromkeys(seen))
    return fid, roles, extra, seen, fills, {k: v for k, v in cand.items()}


# --------------------------------------------------------------------------------------
# (c) features
# --------------------------------------------------------------------------------------
def features(seen, fills, roles):
    """Feature vector emphasising the *hue vocabulary* of the fills.

    A raw 8-bin histogram spreads a figure that uses one blue and one orange over several
    bins and makes every multi-hue figure look alike, so the dominant and second coarse
    family are also encoded as (weighted) one-hots -- this is what makes the clusters
    nameable ("blue + orange", "grey only", "warm pastel").
    """
    v = []
    hist = np.zeros(len(HUE_BINS) + 1)
    coarse = collections.Counter()
    for h in fills:
        fam = hue_family(h)
        hist[-1 if fam == "grey" else HUE_BINS.index(fam)] += 1
        coarse[COARSE_OF[fam]] += 1
    n = max(1, hist.sum())
    v.extend((hist / n).tolist())                                  # 0-8  fine histogram
    tot = max(1, sum(coarse.values()))
    ranked = coarse.most_common()
    top1 = ranked[0][0] if ranked else "grey"
    top2 = ranked[1][0] if len(ranked) > 1 else "none"
    v.extend([1.0 if f == top1 else 0.0 for f in COARSE])          # 9-15  dominant family
    v.extend([1.0 if f == top2 else 0.0 for f in COARSE])          # 16-22 second family
    v.append(ranked[0][1] / tot if ranked else 0.0)                # dominance
    v.append(ranked[1][1] / tot if len(ranked) > 1 else 0.0)
    ng = [h for h in fills if not is_grey(h)]
    ls = [hls(h)[1] for h in ng] or [1.0]
    cs = [hls(h)[2] for h in ng] or [0.0]
    v.append(float(np.mean(ls)))                                   # mean lightness
    v.append(float(np.min(ls)))                                    # darkest coloured fill
    v.append(float(np.mean(cs)))                                   # mean chroma
    v.append(float(np.max(cs)))                                    # peak chroma
    v.append(len([h for h in fills if is_grey(h)]) / max(1, len(fills)))     # grey share
    v.append(len({coarse_family(h) for h in ng}) / 6.0)            # distinct families
    v.append(len([h for h in seen if h in OFFICE]) / max(1, len(seen)))      # Office share
    v.append(1.0 if ng and np.mean(ls) > 0.80 else 0.0)            # pastel
    v.append(1.0 if len({coarse_family(h) for h in ng}) <= 1 else 0.0)       # monochrome
    a = roles.get("accent")
    fam = coarse_family(a) if a else "grey"
    v.extend([1.0 if f == fam else 0.0 for f in COARSE])           # accent family
    if a and not is_grey(a):
        _h, l, c = hls(a)
        v.extend([l, c])
    else:
        v.extend([0.5, 0.0])
    return np.array(v, dtype=float)


FEATURE_NAMES = ([f"hue_{b}" for b in HUE_BINS] + ["hue_grey"]
                 + [f"top1_{f}" for f in COARSE] + [f"top2_{f}" for f in COARSE]
                 + ["top1_share", "top2_share", "fill_L_mean", "fill_L_min",
                    "fill_C_mean", "fill_C_max", "grey_share", "n_hue_fams",
                    "office_share", "pastel", "monochrome"]
                 + [f"acc_{f}" for f in COARSE] + ["acc_L", "acc_C"])
F = {n: i for i, n in enumerate(FEATURE_NAMES)}



def write_palettes(path, clusters, recs, k):
    """Emit references/palettes.json: the curated, directly usable form of the clusters."""
    by_id = {r["id"]: r for r in recs}
    n_all = len(recs)
    sat = [sum(1 for h in set(r["fills"]) if hls(h)[2] >= 0.40) for r in recs]
    # match each cluster to the curated family whose exemplars it actually contains
    taken, assign = set(), {}
    for c in sorted(clusters, key=lambda c: -c["n"]):
        mem = set(c["members"])
        best, best_score = None, 0
        for key, cur in CURATION.items():
            if key in taken:
                continue
            score = sum(1 for e in cur["exemplars"] if e in mem)
            if score > best_score:
                best, best_score = key, score
        if best:
            taken.add(best)
            assign[c["cluster"]] = best
    out_pals = []
    for c in sorted(clusters, key=lambda c: -c["n"]):
        cur = CURATION.get(assign.get(c["cluster"]))
        if cur is None:
            cur = dict(id=f"cluster-{c['cluster']}", name=f"Cluster {c['cluster']}",
                       description="", when_to_use="",
                       exemplars=[e["id"] for e in c["candidates"][:4]])
        rep = {r: c["rep"][r] for r in ROLES}
        notes = []
        for role in ROLES:
            if role in c["derived"] and role in c["rep_raw"] and \
                    c["rep_raw"][role] != c["rep"][role]:
                notes.append(f"{role}: corpus value {c['rep_raw'][role]} replaced by "
                             f"{c['rep'][role]} ({c['derived'][role]})")
        if rep["stroke"] and rep["module"] and contrast(rep["stroke"], rep["module"]) < 3.0:
            notes.append(f"stroke on module is "
                         f"{contrast(rep['stroke'], rep['module']):.1f}:1 - "
                         f"darken the outline to #404040 for small figures")
        for label, (fg, bg) in {"text on module": (rep["text"], rep["module"]),
                                "text on accent": (rep["text"], rep["accent"]),
                                "text on container": (rep["text"], rep["container"])}.items():
            if fg and bg and isinstance(bg, str):
                cr = contrast(fg, bg)
                if cr < 4.5:
                    notes.append(f"{label} is {cr:.1f}:1 ({fg} on {bg}) - "
                                 + ("use #ffffff for labels inside that box"
                                    if rel_lum(bg) < 0.4 else
                                    "keep the label short and bold, or move it outside"))
        order_ex = ([c["medoid"]] + [e for e in cur["exemplars"] if e != c["medoid"]]
                    if c["medoid"] in cur["exemplars"] else list(cur["exemplars"]))
        exemplars = []
        for eid in order_ex:
            r = by_id.get(eid)
            if r is None:
                continue
            # src_svgs can list several files separated by "|" (multi-part figures);
            # take the first that exists, else fall back to the PDF-extracted SVG
            cands = [rel_png(r['paper_id'], x) for x in (r["src_svgs"] or "").split("|") if x]
            cands.append(rel_png(r['paper_id'], r['pdf_svg'] or ''))
            png = next((x for x in cands
                        if os.path.exists(os.path.join(REPO_ROOT, x))), cands[0])
            exemplars.append(dict(id=eid, png=png, src_svg=png.replace(".png", ".svg"),
                                  tool=r["tool"], venue=r["venue"],
                                  in_cluster=eid in c["members"]))
        out_pals.append(dict(
            id=cur["id"], name=cur["name"], description=cur["description"],
            when_to_use=cur["when_to_use"],
            roles={r: rep[r] for r in ROLES},
            extra_fills=c["extra_fills"],
            contrast_notes=("; ".join(notes) if notes
                            else "every role pair clears 4.5:1 with the listed text colour"),
            stats=dict(n_figures=c["n"], share=round(c["n"] / n_all, 3),
                       mean_grey_frac=round(c["mean_gray"], 3),
                       pastel_share=c["pastel_share"], monochrome_share=c["mono_share"],
                       hue_families=c["rep"]["_families"],
                       tools=dict(c["tools"][:6]), venues=dict(c["venues"][:6]),
                       abstractions=dict(c["abstractions"][:6]),
                       templates=dict(c["templates"][:6])),
            exemplars=exemplars))
    doc = dict(
        role_vocabulary=ROLE_VOCABULARY,
        general_rules=dict(
            canvas="#ffffff - 272/272 architecture figures use a white page background.",
            distinct_fills_per_figure=dict(
                median=4, mean=4.2,
                note="median 5 distinct hexes overall (fills + strokes + text)"),
            saturated_fills_per_figure=dict(
                median=int(np.median(sat)), mean=round(float(np.mean(sat)), 2),
                distribution={str(v): n for v, n in
                              sorted(collections.Counter(sat).items())},
                note="chroma >= 0.40; 106/272 figures use none and 86 use exactly one - "
                     "treat 2 as the ceiling"),
            grey=dict(figures_using_grey=187, share=0.69,
                      median_grey_share_of_hexes=0.20,
                      note="grey marks existing/unchanged components; 113/272 "
                           "encoding.color_means strings mention grey"),
            accent=dict(figures_with_an_accent=200, share=0.74,
                        families={"warm (orange/gold)": 68, "red": 46, "blue": 34,
                                  "green": 18, "cyan": 17, "grey": 15, "purple": 2},
                        note="one accent per figure is the norm; a second one only for "
                             "the highlighted connector"),
            fill_style={"flat": 241, "hatch": 25, "mixed": 3, "none": 3},
            office_theme_hexes=dict(figures=33, share=0.12),
            text=dict(median_lightness=0.35,
                      note="near-black by default; 45 of 103 recorded text/module pairs "
                           "fall below 4.5:1 - do not copy that"),
        ),
        provenance=dict(figures=n_all, clusters=k,
                        source="lab/extracted/corpus_semantics.jsonl joined with "
                               "lab/extracted/corpus_index.csv "
                               "(type=diagram, subtype=architecture)",
                        generator="figgenie-paper-diagram/scripts/distill/palette_cluster.py"),
        palettes=out_pals)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(doc, f, indent=1)
    print("wrote", path, f"({len(out_pals)} palettes)")


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--semantics", required=True)
    ap.add_argument("--index", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--palettes-out", default=None,
                    help="also write the curated references/palettes.json here")
    ap.add_argument("--kmin", type=int, default=6)
    ap.add_argument("--kmax", type=int, default=14)
    ap.add_argument("--k", type=int, default=14,
                    help="number of clusters before the small-cluster merge; 0 = pick the "
                         "best silhouette in [8,12].  The distilled palettes use k=12: the "
                         "silhouette sweep peaks at k=9 (0.36) but k=14 (0.28) splits the "
                         "large warm/grey groups into nameable families (peach-tan, "
                         "grey-pastel, teal) and the merge step below removes the "
                         "fragments that over-splitting creates.")
    ap.add_argument("--subtype", default="architecture",
                    help="diagram subtype to cluster (architecture, or mechanism for the kind-2 records)")
    ap.add_argument("--min-size", type=int, default=8,
                    help="clusters smaller than this are merged into their nearest "
                         "neighbour (by centroid distance) until 8-12 families remain")
    args = ap.parse_args()
    set_extracted_dir(os.path.dirname(os.path.abspath(args.index)))
    os.makedirs(args.out, exist_ok=True)

    figs = load(args.semantics, args.index, args.subtype)
    print(f"{args.subtype} figures: {len(figs)}")

    residue, multi = [], []
    recs = []
    role_counts = collections.Counter()
    for rec, row in figs:
        fid, roles, extra, seen, fills, cand = figure_roles(rec, row, residue, multi)
        for r, v in roles.items():
            if v:
                role_counts[r] += 1
        style_meas = {}
        try:
            style_meas = json.loads(row["style"])
        except Exception:
            pass
        recs.append(dict(
            id=fid, paper_id=rec["paper_id"], fig=str(rec["fig"]),
            roles=roles, extra_fills=extra, seen=seen, fills=fills,
            tool=row.get("tool"), venue=row.get("venue"),
            abstraction=(rec.get("system") or {}).get("abstraction"),
            template=(rec.get("layout") or {}).get("template"),
            column=(rec.get("layout") or {}).get("column") or row.get("column"),
            confidence=rec.get("confidence"),
            color_means=(rec.get("encoding") or {}).get("color_means"),
            emphasis=(rec.get("encoding") or {}).get("emphasis"),
            tags=rec.get("tags") or [],
            fill_style=(rec.get("style") or {}).get("fill"),
            gray_frac=(style_meas.get("palette") or {}).get("gray_frac"),
            named=(style_meas.get("palette") or {}).get("named"),
            src_svgs=row.get("src_svgs"), pdf_svg=row.get("pdf_svg"),
        ))

    with open(os.path.join(args.out, "role_residue.txt"), "w") as f:
        f.write("\n".join(residue))
    with open(os.path.join(args.out, "role_multi.txt"), "w") as f:
        f.write("\n".join(multi))
    with open(os.path.join(args.out, "role_stats.json"), "w") as f:
        json.dump(dict(n_figures=len(recs), role_coverage=role_counts,
                       residue_lines=len(residue), multi_role_lines=len(multi)),
                  f, indent=2)

    X = np.array([features(r["seen"], r["fills"], r["roles"]) for r in recs])
    keep = np.array([len(r["fills"]) > 0 for r in recs])
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    Xs = StandardScaler().fit_transform(X)
    # hue histogram carries the family identity -> weight it up
    w = np.ones(Xs.shape[1])
    w[:9] = 0.7                                        # fine histogram: background signal
    for f in COARSE:
        w[F[f"top1_{f}"]] = 2.4                        # dominant family drives the family
        w[F[f"top2_{f}"]] = 1.3
        w[F[f"acc_{f}"]] = 0.9
    w[F["grey_share"]] = 1.5
    w[F["fill_L_mean"]] = 1.4
    w[F["monochrome"]] = 1.5
    w[F["n_hue_fams"]] = 1.2
    Xs = Xs * w

    sweep = []
    for k in range(args.kmin, args.kmax + 1):
        lab = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Xs[keep])
        sweep.append((k, float(silhouette_score(Xs[keep], lab)),
                      sorted(collections.Counter(lab).values(), reverse=True)))
    with open(os.path.join(args.out, "k_sweep.txt"), "w") as f:
        for k, s, sizes in sweep:
            f.write(f"k={k}\tsilhouette={s:.4f}\tsizes={sizes}\n")
            print(f"k={k} silhouette={s:.4f} sizes={sizes}")

    k = args.k or max((s for s in sweep if 8 <= s[0] <= 12), key=lambda t: t[1])[0]
    print("chosen k =", k)
    labels_all = np.full(len(recs), -1)
    labels_all[keep] = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Xs[keep])

    # merge fragments: repeatedly fold the smallest under-sized cluster into the cluster
    # whose centroid is closest, until every family is big enough (or only 8 remain)
    while True:
        sizes = collections.Counter(labels_all[labels_all >= 0])
        if len(sizes) <= 8:
            break
        small = [c for c, n in sizes.items() if n < args.min_size]
        if not small:
            break
        c = min(small, key=lambda c: sizes[c])
        cent = {cc: Xs[labels_all == cc].mean(0) for cc in sizes}
        tgt = min((cc for cc in sizes if cc != c),
                  key=lambda cc: float(np.linalg.norm(cent[cc] - cent[c])))
        print(f"merge cluster {c} (n={sizes[c]}) -> {tgt} (n={sizes[tgt]})")
        labels_all[labels_all == c] = tgt
    # renumber 0..K-1
    remap = {old: new for new, old in enumerate(sorted(set(labels_all[labels_all >= 0])))}
    labels_all = np.array([remap.get(l, -1) for l in labels_all])
    k = len(remap)
    print("final clusters:", k, sorted(collections.Counter(labels_all[labels_all >= 0]).values(), reverse=True))

    corpus_hex = collections.Counter(h for r in recs for h in r["seen"])
    clusters = []
    for c in range(k):
        members = [i for i in range(len(recs)) if labels_all[i] == c]
        M = Xs[members]
        centre = M.mean(0)
        d = np.linalg.norm(M - centre, axis=1)
        order = np.argsort(d)
        medoid = recs[members[int(order[0])]]
        # Family ranking of the cluster's fills -- the palette must read as the family it is
        # named after, so `module` / `module-alt` are drawn from the dominant hue families
        # rather than from whichever member figure happened to be the medoid.
        fam_cnt = collections.Counter(
            coarse_family(h) for i in members for h in recs[i]["fills"])
        fam_rank = [f for f, _ in fam_cnt.most_common()]
        nongrey_fams = [f for f in fam_rank if f != "grey"]
        all_fills = collections.Counter(h for i in members for h in recs[i]["fills"])

        def modal_in_family(fams, ok, exclude=()):
            for fam in fams:
                pool = [(h, n) for h, n in all_fills.most_common()
                        if coarse_family(h) == fam and ok(h) and h not in exclude]
                if pool:
                    return pool[0][0]
            return None

        # Representative hex per role: the medoid's colour if it is *usable* for that role,
        # otherwise the cluster's most common usable member colour (still a corpus hex),
        # otherwise the closest fallback -- flagged in `derived` so the caller can mark it.
        rep, derived = {}, {}
        for role in ROLES:
            if role == "module-alt":
                continue
            ok = ROLE_OK[role]
            vals = [recs[i]["roles"].get(role) for i in members]
            vals = [v for v in vals if isinstance(v, str) and v]
            good = [v for v in vals if ok(v)]
            mv = medoid["roles"].get(role)
            if isinstance(mv, str) and mv and ok(mv) and not (
                    role in ("stroke", "text") and good
                    and min(hls(h)[1] for h in good) < hls(mv)[1] - 0.12):
                rep[role] = mv
            elif good:
                gc = collections.Counter(good)
                if role in ("stroke", "text"):
                    # outlines and body text: the palette wants the darkest neutral the
                    # family uses, not the most frequent one (which can be a mid grey)
                    rep[role] = min(gc, key=lambda h: (hls(h)[1], -gc[h]))
                else:
                    rep[role] = max(gc.items(),
                                    key=lambda kv: (kv[1], corpus_hex[kv[0]]))[0]
                derived[role] = "cluster-modal (medoid value unusable for this role)"
            else:
                # widen: any usable colour anywhere in the cluster's palettes
                pool = collections.Counter(
                    h for i in members for h in recs[i]["seen"] if ok(h))
                if pool:
                    # ties inside the cluster are broken by how common the colour is in
                    # the whole corpus, so the fallback lands on a canonical hex
                    rep[role] = max(pool.items(),
                                    key=lambda kv: (kv[1], corpus_hex[kv[0]]))[0]
                    derived[role] = "cluster-wide modal (no member named this role)"
                else:
                    rep[role] = ROLE_DEFAULT[role]
                    derived[role] = "default (role absent from the cluster)"
        # module: the cluster's most common `module` hex.  Counting the hex directly (rather
        # than picking inside a hue family) reproduces the default box the family actually
        # uses; ties go to the dominant module hue family, then to the lighter colour.
        mod_pool = [recs[i]["roles"].get("module") for i in members]
        mod_pool = [h for h in mod_pool if isinstance(h, str) and h and ROLE_OK["module"](h)]
        mod_cnt = collections.Counter(mod_pool)
        mod_fam = collections.Counter(coarse_family(h) for h in mod_cnt.elements())
        fam0 = mod_fam.most_common(1)[0][0] if mod_fam else (
            nongrey_fams[0] if nongrey_fams else "grey")
        if mod_cnt:
            rep["module"] = max(mod_cnt.items(),
                                key=lambda kv: (kv[1], coarse_family(kv[0]) == fam0,
                                                hls(kv[0])[1]))[0]
        else:
            pick_h = modal_in_family([fam0] + fam_rank, ROLE_OK["module"])
            if pick_h:
                rep["module"] = pick_h
                derived["module"] = f"cluster-modal fill in the dominant family ({fam0})"
        # accent: same treatment -- most common accent hex, ties to the dominant accent family
        acc_cnt = collections.Counter(
            h for h in (recs[i]["roles"].get("accent") for i in members)
            if isinstance(h, str) and h and ROLE_OK["accent"](h))
        acc_fam = collections.Counter(coarse_family(h) for h in acc_cnt.elements())
        afam0 = acc_fam.most_common(1)[0][0] if acc_fam else "warm"
        if acc_cnt:
            rep["accent"] = max(acc_cnt.items(),
                                key=lambda kv: (kv[1], coarse_family(kv[0]) == afam0,
                                                -hls(kv[0])[1]))[0]
        # module-alt: the next families' most common usable fills.  In a light family a
        # fully saturated primary is an accent, not an alternative box fill, so we keep
        # alt fills light unless the family's fills really are dark (high-contrast).
        dark_family = float(np.mean([X[i][F["fill_L_mean"]] for i in members])) < 0.62
        alt_ok = (ROLE_OK["module"] if dark_family
                  else (lambda h: ROLE_OK["module"](h) and hls(h)[1] >= 0.55))
        alts, used = [], {rep.get("module"), rep.get("accent"), rep.get("container")}
        for fam in ([f for f in nongrey_fams if f != fam0] + ["grey"]):
            h = modal_in_family([fam], alt_ok, exclude=used)
            if h:
                alts.append(h); used.add(h)
            if len(alts) >= 3:
                break
        rep["module-alt"] = alts[:3]
        rep["_families"] = fam_rank[:4]
        rep_raw = dict(rep)   # snapshot before the coherence pass, so the report can show
                              # both the colour the corpus actually names and the adjusted one
        extra = collections.Counter()
        for i in members:
            for h in recs[i]["extra_fills"]:
                extra[h] += 1
        clusters.append(dict(
            cluster=c, n=len(members), rep=rep, rep_raw=rep_raw, derived=derived,
            extra_fills=[h for h, _ in extra.most_common(6)],
            medoid=medoid["id"],
            members=[recs[i]["id"] for i in members],
            tools=collections.Counter(recs[i]["tool"] for i in members).most_common(),
            venues=collections.Counter(recs[i]["venue"] for i in members).most_common(),
            abstractions=collections.Counter(recs[i]["abstraction"] for i in members).most_common(),
            templates=collections.Counter(recs[i]["template"] for i in members).most_common(),
            fill_styles=collections.Counter(recs[i]["fill_style"] for i in members).most_common(),
            mean_gray=float(np.mean([recs[i]["gray_frac"] or 0 for i in members])),
            hue_hist={b: round(float(np.mean([X[i][j] for i in members])), 3)
                      for j, b in enumerate(HUE_BINS + ["grey"])},
            coarse_top1=collections.Counter(
                COARSE[int(np.argmax([X[i][F[f"top1_{f}"]] for f in COARSE]))]
                for i in members).most_common(3),
            coarse_top2=collections.Counter(
                COARSE[int(np.argmax([X[i][F[f"top2_{f}"]] for f in COARSE]))]
                for i in members).most_common(3),
            fill_L_mean=round(float(np.mean([X[i][F["fill_L_mean"]] for i in members])), 3),
            fill_C_mean=round(float(np.mean([X[i][F["fill_C_mean"]] for i in members])), 3),
            n_hue_fams=round(float(np.mean([X[i][F["n_hue_fams"]] for i in members])) * 6, 2),
            office_share=round(float(np.mean([X[i][F["office_share"]] for i in members])), 3),
            pastel_share=round(float(np.mean([X[i][F["pastel"]] for i in members])), 3),
            mono_share=round(float(np.mean([X[i][F["monochrome"]] for i in members])), 3),
            candidates=[dict(id=recs[members[int(j)]]["id"],
                             conf=recs[members[int(j)]]["confidence"],
                             dist=round(float(d[int(j)]), 3),
                             n_roles=sum(1 for v in recs[members[int(j)]]["roles"].values() if v),
                             tool=recs[members[int(j)]]["tool"],
                             src=recs[members[int(j)]]["src_svgs"],
                             pdf=recs[members[int(j)]]["pdf_svg"],
                             paper_id=recs[members[int(j)]]["paper_id"],
                             color_means=recs[members[int(j)]]["color_means"])
                        for j in order[:18]],
        ))
        # Coherence pass: a palette must be readable as a set.  The container has to sit
        # behind the module (lighter and a different colour), and the accent has to be
        # distinguishable from the default module, otherwise "accent" means nothing.
        if rep["container"] == rep["module"] or (
                coarse_family(rep["container"]) == coarse_family(rep["module"])
                and abs(hls(rep["container"])[1] - hls(rep["module"])[1]) < 0.08):
            greys = [(h, n) for h, n in all_fills.most_common()
                     if is_grey(h) and 0.72 < hls(h)[1] < 0.995 and h != rep["module"]
                     and abs(hls(h)[1] - hls(rep["module"])[1]) >= 0.04]
            if greys:
                rep["container"] = max(greys, key=lambda kv: (kv[1], corpus_hex[kv[0]]))[0]
                derived["container"] = ("cluster-modal light neutral, kept >=0.08 lightness "
                                        "away from the module fill")
        # A monochrome family has no chromatic accent of its own: use the dark grey its
        # members actually reach for, and keep the borrowed red only for the accent arrow.
        if float(np.mean([X[i][F["monochrome"]] for i in members])) >= 0.9:
            greys = collections.Counter(
                h for i in members for h in recs[i]["seen"]
                if is_grey(h) and hls(h)[1] < 0.55)
            if greys:
                rep["accent"] = max(greys.items(),
                                    key=lambda kv: (kv[1], corpus_hex[kv[0]]))[0]
                derived["accent"] = ("monochrome family: darkest grey its members use for "
                                     "emphasis (borrow #c00000 only for a highlighted path)")

        def accent_reads(h):
            """An accent must be told apart from the default module box: either a different
            hue family, or clearly darker/lighter within the same family."""
            return (coarse_family(h) != coarse_family(rep["module"])
                    or abs(hls(h)[1] - hls(rep["module"])[1]) >= 0.18)

        if rep["accent"] and rep["module"] and not accent_reads(rep["accent"]):
            better = [h for h, _ in acc_cnt.most_common() if accent_reads(h)]
            if better:
                rep["accent"] = better[0]
                derived["accent"] = "cluster-modal accent that separates from the module fill"
        if rep["lane"] in (rep["container"], rep["module"], "#ffffff", None):
            lanes = [h for h, n in all_fills.most_common()
                     if ROLE_OK["lane"](h) and hls(h)[1] < 0.985
                     and h not in (rep["container"], rep["module"])]
            if lanes:
                rep["lane"] = lanes[0]
                derived["lane"] = "cluster-modal light fill distinct from the container"
        rep["module-alt"] = [h for h in rep["module-alt"]
                             if h not in (rep["module"], rep["accent"], rep["container"])]
        if len(rep["module-alt"]) < 2:   # top up after the coherence swaps consumed one
            used2 = set(rep["module-alt"]) | {rep["module"], rep["accent"],
                                              rep["container"], rep["lane"]}
            for h, _n in all_fills.most_common():
                if h not in used2 and alt_ok(h) and hls(h)[1] < 0.985:
                    rep["module-alt"].append(h); used2.add(h)
                if len(rep["module-alt"]) >= 2:
                    break

        # contrast audit
        notes = []
        for pair, (fg, bg) in {
            "text-on-module": (rep.get("text"), rep.get("module")),
            "text-on-accent": (rep.get("text"), rep.get("accent")),
            "text-on-container": (rep.get("text"), rep.get("container")),
            "stroke-on-module": (rep.get("stroke"), rep.get("module")),
        }.items():
            if fg and bg:
                cr = contrast(fg, bg)
                if cr < 4.5:
                    notes.append(f"{pair} {fg}/{bg} contrast {cr:.1f}")
        clusters[-1]["contrast_warnings"] = notes

    with open(os.path.join(args.out, "figure_roles.json"), "w") as f:
        json.dump(recs, f, indent=1)
    with open(os.path.join(args.out, "clusters.json"), "w") as f:
        json.dump(dict(k=k, feature_names=FEATURE_NAMES, clusters=clusters), f, indent=1)

    lines = [f"# palette clusters (k={k}, n={len(recs)})\n"]
    for c in sorted(clusters, key=lambda c: -c["n"]):
        lines.append(f"\n## cluster {c['cluster']}  n={c['n']}  medoid={c['medoid']}")
        lines.append(f"roles: {json.dumps(c['rep'])}")
        lines.append(f"extra: {c['extra_fills']}")
        lines.append(f"hues: { {k2: v for k2, v in c['hue_hist'].items() if v > 0.02} }")
        lines.append(f"top1={c['coarse_top1']} top2={c['coarse_top2']}")
        lines.append(f"L={c['fill_L_mean']} C={c['fill_C_mean']} hue_fams={c['n_hue_fams']}"
                     f" grey={round(c['mean_gray'],2)} office={c['office_share']}"
                     f" pastel={c['pastel_share']} mono={c['mono_share']}")
        lines.append(f"tools: {c['tools'][:5]}")
        lines.append(f"venues: {c['venues'][:4]}")
        lines.append(f"abstractions: {c['abstractions'][:4]}")
        lines.append(f"templates: {c['templates'][:4]}")
        lines.append(f"contrast: {c['contrast_warnings']}")
        lines.append("candidates:")
        for e in c["candidates"][:10]:
            lines.append(f"  {e['id']}  conf={e['conf']} d={e['dist']} tool={e['tool']}"
                         f" roles={e['n_roles']}  src={e['src']}")
    with open(os.path.join(args.out, "cluster_report.md"), "w") as f:
        f.write("\n".join(lines))
    if args.palettes_out:
        write_palettes(args.palettes_out, clusters, recs, k)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
