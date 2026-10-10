#!/usr/bin/env python3
"""Mine the visual-encoding vocabulary of systems-conference architecture figures.

Reads the per-figure semantic records (corpus_semantics.jsonl), joins them to the
corpus index (corpus_index.csv), keeps the rows the index calls
type=diagram / subtype=architecture, and turns the free-text `encoding` and
`style` fields into counted tables:

  variable_meanings.csv  visual variable -> meaning category, count, exemplars
  color_roles.csv        colour word -> meaning bucket (mined from "green = ..." clauses)
  emphasis.csv           emphasis technique, count, exemplars
  weaknesses.csv         weakness category, count, exemplars, quoted examples
  measured.csv           objective style facets from the index `style` JSON
  legend_steps.csv       legend placement / step markers / palette size crosstabs
  encoding_mine.json     all of the above in one blob

WHAT IS AUTOMATIC AND WHAT IS NOT
  * measured.csv is objective: those numbers were measured from the SVG at print
    size by the corpus builder and are only aggregated here.
  * legend_steps.csv is objective in the same sense (enumerated record fields).
  * Everything else is KEYWORD/REGEX MATCHING OVER MODEL-WRITTEN ENGLISH PROSE.
    Each rule is scoped to the record field where that variable is described, but
    still: one record can match several categories (rules are not exclusive), a
    convention the record does not mention is invisible (undercount), and
    phrasings the patterns miss are lost (undercount). Read the counts as "how
    often the corpus explicitly says X", not "how often X is drawn".
  * The recommended defaults, conflict rules and fix advice in
    ../../references/encoding.md and anti-patterns.md are a human synthesis on
    top of these tables. This script does not produce them.

Usage:
  python3 encoding_mine.py [--semantics PATH] [--index PATH] [--out DIR]
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import sys

DEF_SEM = "lab/extracted/corpus_semantics.jsonl"
DEF_IDX = "lab/extracted/corpus_index.csv"
DEF_OUT = "distill-out/step4"

# Field scopes a rule can be matched against.
F_COLOR = ("color_means",)
F_LINE = ("line_style_means",)
F_EMPH = ("emphasis",)
F_EMPH_PAT = ("emphasis", "reusable_patterns")
F_LINE_ARROW = ("line_style_means", "s_arrows")
F_ALL = ("color_means", "line_style_means", "emphasis", "reusable_patterns",
         "s_stroke", "s_arrows", "s_icons", "s_fill", "s_corners", "s_font")

C = r"[^.;|]{0,55}"   # short within-clause filler

# (variable, meaning, fields, regex)
RULES = [
    # ---------------- fill colour -------------------------------------------------
    ("fill colour", "novel / ours (accent fill)", F_COLOR,
     rf"(novel|new (module|component|logic|hardware|sublayer)|newly[- ]added|contribution|own (novel )?component|paper'?s own|proposed|augmentation|introduced by|added to support)"),
    ("fill colour", "existing / reused / baseline (gray or white)", F_COLOR,
     rf"(gray|grey|white|uncolou?red|transparent|plain|neutral|light gray)\b{C}\b(existing|unmodified|reused|baseline|prior[- ]work|conventional|standard|generic|background|passive|pre-existing|unchanged|untouched)"),
    ("fill colour", "component / module identity (which subsystem)", F_COLOR,
     rf"\b(component|module|subsystem|engine|unit|controller|scheduler|manager|planner|library|service|block|stage|allocator|optimizer|executor|collector|worker|frontend|backend)\b"),
    ("fill colour", "layer / tier / plane / phase membership", F_COLOR,
     rf"\b(layer|tier|plane|level|band|region|zone|swimlane|host[- ]side|device[- ]side|offline|online|control plane|data plane|user space|kernel space|prefill|decode)\b"),
    ("fill colour", "data kind / precision / state of a datum", F_COLOR,
     rf"\b(plaintext|ciphertext|fp\d|precision|hot|cold|guaranteed|oversubscribed|cached|dirty|clean|token|tensor|weight|activation|parameter|kv|queued|running|idle|allocated|unallocated|pruned|retained|drafted|accepted|rejected)\b"),
    ("fill colour", "status / outcome: red = error, green = ok", F_COLOR,
     rf"\b(red|pink|green)\b{C}\b(error|fail|failed|faulty|fault|violation|invalid|reject|bottleneck|stall|hang|miss|breakdown|overhead|success|accepted|valid|healthy|hit|pass)"),
    ("fill colour", "per-step / per-phase colour reused with the walkthrough", F_COLOR,
     rf"\b(phase|step)\b{C}\b\d|\b\d\b{C}\b(phase|step)|colou?r{C}(phase|step) coding"),
    ("fill colour", "entity tracking: same colour follows a task/tensor", F_COLOR,
     rf"(same|matching|consistent|carried|reused|tracked|tags?)\b{C}\b(colou?r|coding|tag)\b{C}\b(across|through|both|every|end[- ]to[- ]end|each|all)"),
    ("fill colour", "no colour semantics (monochrome / decorative)", F_COLOR,
     r"(monochrome|grayscale|greyscale|no semantic|carries almost no|not a fixed semantic|rather than encode a semantic|rather than novelty|individuate|decorative|^none$|not applicable)"),

    # ---------------- stroke / outline colour --------------------------------------
    ("stroke / outline colour", "coloured outline marks the contribution", F_ALL,
     rf"(red|blue|green|orange|thick|bold|black)[- ]?(outline|border|bordered|box|rectangle)\w*{C}\b(novel|new|our|contribution|highlight|singl\w+ out|isolat\w+|paper'?s)"),
    ("stroke / outline colour", "coloured outline marks a fault / example instance", F_ALL,
     rf"(red|dashed red)\b{C}\b(outline|border|box|highlight|x |cross)\b{C}\b(fail|faulty|fault|error|affected|example|removed)"),
    ("stroke / outline colour", "thick / bold border = focal box", F_ALL,
     r"(thick|bold|heavier|heavy)[- ]?(bordered?|border|outlined?|outline|stroke)"),
    ("stroke / outline colour", "outline only, no fill (structural boxes)", F_ALL,
     r"(no fill|carry no fill|unfilled|white/unfilled|transparent (box|fill)|line art)"),

    # ---------------- line style ---------------------------------------------------
    ("line style", "dashed = logical grouping / container boundary", F_LINE,
     rf"\b(dashed|dotted)\b{C}\b(group|grouping|delimit|delineat|demarcat|bound(ar|ing)|enclos|outlin|isolat|mark the|rounded rectangle|super-?group|region)"),
    ("line style", "dashed = region / plane / phase divider", F_LINE,
     rf"\b(dashed|dotted)\b{C}\b(divider|separat|split|divide|boundary between|vertical (line|rule)|horizontal (line|rule)|marks the .{{0,20}}boundary)"),
    ("line style", "dashed = control / metadata path (solid = data)", F_LINE,
     rf"\b(dashed|dotted)\b{C}\b(control|command|metadata|management|telemetry|signal|policy|config|coordination|context flow|qos)"),
    ("line style", "dashed = zoom / callout leader line", F_LINE,
     rf"\b(dashed|dotted)\b{C}\b(connect|connector|link|leader|callout|call-out|zoom|expand|magnif|inset)"),
    ("line style", "dashed = optional / conditional / speculative", F_LINE,
     rf"\b(dashed|dotted)\b{C}\b(optional|conditional|only|if |speculativ|candidate|possible|potential|future|placeholder|pruned)"),
    ("line style", "dashed = feedback / async / side path", F_LINE,
     rf"\b(dashed|dotted)\b{C}\b(feedback|async|asynchronous|loop|side[- ]effect|auxiliary|periodic|recurrent|back to)"),
    ("line style", "dashed = repetition / partition boundary", F_LINE,
     rf"\b(dashed|dotted)\b{C}\b(repeated|replicat|per[- ](worker|node|rank|request|instance|pu)|partition boundar|iteration boundar)"),
    ("line style", "solid = main data / request flow", F_LINE,
     rf"\bsolid\b{C}\b(data|main|forward|request|primary|structural|physical|always[- ]present|black arrows)"),
    ("line style", "dotted used as a third, weaker channel", F_LINE,
     rf"\bdotted\b{C}(vs\.?|versus|rather than|while|whereas|;)?{C}\bdash|\bdash{C}\bdotted\b"),
    ("line style", "no line-style distinction in this figure", F_LINE,
     r"^(none|not distinguished|not specified|no dashed|not applicable|no line)"),

    # ---------------- arrows -------------------------------------------------------
    ("arrows", "arrow colour encodes flow / link type", F_LINE_ARROW,
     rf"(arrow|line|edge)s?\b{C}\bcolou?r|colou?r(ed|-coded)?\b{C}\barrows?|arrow colou?r encodes"),
    ("arrows", "labelled arrow names the payload", F_LINE_ARROW,
     r"label(l)?ed[^.;|]{0,30}arrow|arrows?[^.;|]{0,30}label(l)?ed|named[^.;|]{0,20}arrow"),
    ("arrows", "double-headed = bidirectional protocol", F_ALL,
     r"(double[- ]headed|double arrows|bidirectional|bi-directional|paired up/down|two-way)[^.;|]{0,50}arrow|arrow[^.;|]{0,30}(bidirectional|double[- ]headed)"),
    ("arrows", "curved arrow = feedback / cross-cutting exchange", F_ALL,
     rf"curved{C}\barrows?|\barrows?{C}\bcurved"),
    ("arrows", "arrow thickness / size encodes volume", F_ALL,
     rf"(thick|size difference|width|bold)\b{C}\barrow{C}\b(volume|traffic|imbalance|bandwidth|main|taken)"),
    ("arrows", "fan-out / fan-in = one-to-many", F_ALL, r"fan[- ]?(out|in)"),
    ("arrows", "self-loop / loop-back = iteration", F_ALL,
     r"self[- ]loop|loop(ing)? (top )?arrow|loops? back|feedback (arrow|loop|path|line)"),
    ("arrows", "orthogonal (right-angle) routing named", F_ALL, r"orthogonal"),
    ("arrows", "arrowheads missing / direction unclear (flagged)", F_ALL,
     r"no arrowheads|omits directionality|no arrows|without arrowheads"),

    # ---------------- step markers -------------------------------------------------
    ("step markers", "circled numbers = ordered walkthrough", F_ALL,
     r"circled (step )?(number|digit)|numbered circle|circled [①1-9]|①|numbered step"),
    ("step markers", "letters (A/B/C) = variants or callout tags", F_ALL,
     r"(circled |lettered |roman[- ]numeral )(letter|A|a)|letter callout|lettered (step|callout|tag|loop)|A-B-C|A/B/C|roman[- ]numeral (tag|corner)"),
    ("step markers", "step colour matches the component it acts on", F_ALL,
     rf"(colou?r(ed|-coded)?)\b{C}\b(step|number)|numbered{C}colou?r"),
    ("step markers", "labelled arrows instead of numbers", F_ALL, r"label(l)?ed[- ]arrow"),
    ("step markers", "section tags (§x.y) tie boxes to the paper", F_ALL,
     r"§|section number|paper section|sec\.? ?\d|subsection"),

    # ---------------- shape idioms -------------------------------------------------
    ("shape idioms", "stacked / offset rectangles = N identical copies", F_ALL,
     r"stack(ed|ing)?[^.;|]{0,55}(rectangle|box|card|panel|sheet|replica|instance|copies|worker|unit)|stacked[- ](rectangle|card|layer|replica|repeated)|offset (rectangle|box|card|worker)"),
    ("shape idioms", "ellipsis (...) = elided repetition", F_ALL, r"ellips[ei]s|\.\.\.|…"),
    ("shape idioms", "cylinder / database / storage icon", F_ALL,
     r"cylinder|database icon|db icon|storage icon|disk icon|drum icon"),
    ("shape idioms", "diamond = decision / branch", F_ALL,
     r"diamond[^.;|]{0,55}(decision|yes/no|branch|split)|decision diamond"),
    ("shape idioms", "circle = operator / arithmetic unit", F_ALL,
     r"(circle|circular)[^.;|]{0,55}(operator|arithmetic|mac|multiply|add\b)|operator circles"),
    ("shape idioms", "grid of small cells = memory / tensor / matrix layout", F_ALL,
     r"grid (of|-based)|cells? (representing|grid)|crossbar|bitmap|matrix of|array of (cells|squares)|small (colou?red )?(grid )?cells"),
    ("shape idioms", "nested box-in-box = containment hierarchy", F_ALL,
     r"box[- ]in[- ]box|nested (box|container|boundar|dashed)|nesting"),
    ("shape idioms", "zoom / magnified callout panel", F_ALL,
     r"(zoom(ed|-in| in|ing)?|magnif\w+|exploded|drill[- ]down|inset)[^.;|]{0,55}(panel|callout|call-out|detail|view|inset|region)|callout[^.;|]{0,40}zoom|zoom[- ]in"),
    ("shape idioms", "status glyph (check / cross / star / lock / fire)", F_ALL,
     r"checkmark|check mark|red (x|cross)|green check|star (marker|icon)|red star|lock icon|fire icon|sad-face|happy-face|pickaxe|X marks"),
    ("shape idioms", "hatch / watermark / zebra shading", F_ALL,
     r"hatch|hatching|zebra|striped|watermark|diagonal (line|stripe)"),
    ("shape idioms", "swimlanes / tinted background bands", F_ALL,
     r"swimlane|lanes?\b|horizontal band|colou?red band|background band|tinted (background|group|band)|bands? (mark|distinguish|separate)"),
    ("shape idioms", "vector icons depicting actors / hardware", ("s_icons",),
     r"^\s*(vector|svg)|vector icon|icons?:? (vector|of|depict)|(?<!no )icons? (depict|show|represent|of )"),
    ("shape idioms", "no icons at all", ("s_icons",), r"^\s*none\b"),
    ("shape idioms", "bitmap / photo panel mixed in", ("s_icons",),
     r"bitmap|photo|micrograph|screenshot|raster"),

    # ---------------- connector routing (from style.arrows prose) ------------------
    ("connector routing", "orthogonal (right-angle) connectors", ("s_arrows",), r"orthogonal|right[- ]angle|elbow|manhattan"),
    ("connector routing", "straight / diagonal connectors", ("s_arrows",), r"straight|diagonal|direct line"),
    ("connector routing", "curved / spline connectors", ("s_arrows",), r"curved|curv\w+|spline|bezier|arc"),
    ("connector routing", "filled triangular arrowheads", ("s_arrows",), r"filled (triangular|solid|black)?\s*(arrow)?heads?|solid (triangular )?heads?|filled arrowheads?"),
    ("connector routing", "open / line (V-shaped) arrowheads", ("s_arrows",), r"open (arrow)?heads?|line heads?|v-shaped|thin heads?|stick arrow"),
    ("connector routing", "block / hollow arrows", ("s_arrows",), r"block arrow|hollow (block )?arrow|thick block"),
    ("connector routing", "no arrowheads on some connectors", ("s_arrows",), r"no (arrow)?heads?|headless|plain lines?|undirected|without arrowheads"),

    # ---------------- text styling -------------------------------------------------
    ("text styling", "bold = box / group titles", F_ALL,
     r"bold[^.;|]{0,55}(title|heading|group|box|label|name)|bold for"),
    ("text styling", "bold / coloured text = contribution term or callout", F_ALL,
     r"(bold|red|orange|blue|green|maroon|olive)[^.;|]{0,25}(text|label|annotation|callout)"),
    ("text styling", "italic = annotation / example value", F_ALL, r"italic"),
    ("text styling", "monospace = code / signal names", F_ALL,
     r"monospace|code snippet|command[- ]line|pseudocode|syntax[- ]highlight"),

    # ---------------- legend -------------------------------------------------------
    ("legend", "explicit in-figure legend decodes the coding", F_ALL,
     r"(explicit|in-figure|its own|figure'?s own|shared|dedicated|inline)[^.;|]{0,35}legend|legend[^.;|]{0,35}(decode|defin|explain|map)|per (the|its) (own )?legend|in-figure legend"),
    ("legend", "coding stated in the caption instead of a legend", F_ALL,
     r"(per|from|in|via) the caption|caption (text|convention|says|states)|relying on the caption|caption/(body )?text"),
]

EMPHASIS_RULES = [
    ("accent colour on the novel component", F_EMPH,
     r"(colou?r|green|blue|red|orange|yellow|pink|highlight|fill|shad)[^.;|]{0,70}(novel|new (module|component|logic)|contribution|our|paper'?s own|proposed|added)|(novel|contribution|new component|its own components)[^.;|]{0,60}(colou?r|highlight|fill|shad)"),
    ("gray / white / plain background for existing parts", F_EMPH,
     r"(gray|grey|white|uncolou?red|transparent|plain|neutral|otherwise)[^.;|]{0,70}(existing|baseline|unmodified|reused|conventional|generic|prior|background|uniform)"),
    ("numbered walkthrough (circled steps)", F_EMPH,
     r"circled (step )?(number|digit|letter)|numbered (step|walkthrough|arrow|circle)|(steps?|numbers?) \d+ ?[-–] ?\d+|①|\bnumbered\b"),
    ("bounding box marks 'this is our system'", F_EMPH,
     r"(dashed|solid|bold|thick|red|orange|green|outer)[^.;|]{0,40}(box|boundar|border|outline|bracket|rectangle)[^.;|]{0,70}(our|system|contribution|novel|separat|isolat|singl|group|mark)"),
    ("side-by-side comparison / before-after panels", F_EMPH,
     r"side[- ]by[- ]side|two[- ]panel|before/after|before and after|baseline vs|vs\.? (proposed|ours|the)|contrast\w*|compar\w*|mirror"),
    ("zoom callout into the block of interest", F_EMPH,
     r"zoom|magnif|callout|call-out|inset|exploded|drill[- ]down|expanded"),
    ("size / centrality (largest, central, anchoring box)", F_EMPH,
     r"largest|biggest|drawn large|most (detailed|saturated)|central|centre|center|anchor|centerpiece|centrepiece|foreground|innermost|prominent"),
    ("thick / bold border on the focal box", F_EMPH,
     r"(thick|bold|heavy)[- ]?(border|bordered|outline|outlined|stroke)"),
    ("red annotation / callout label", F_EMPH,
     r"red [^.;|]{0,35}(label|callout|annotation|text|x\b|cross|star|marker|highlight|dashed|overlay|arrow)|breakdown!|points to parent"),
    ("section-number tags (§) tie boxes to the text", F_EMPH,
     r"§|section number|paper section|sec\.? ?\d|subsection"),
    ("status glyph (check / cross / star / fire)", F_EMPH,
     r"checkmark|check mark|red (x|cross)|green check|star (marker|icon)|red star|fire icon|sad-face"),
    ("shaded region / tinted band behind the novel part", F_EMPH,
     r"shad(ed|ing)|tint(ed)?|background (panel|band|colou?r|shading)|colou?red band|colou?r-?(coded|blocked) (band|panel|row)"),
    ("explicit legend used as the emphasis device", F_EMPH,
     r"(explicit|in-figure|its own|dedicated|shared)[^.;|]{0,30}legend"),
    ("repetition / replication (N copies, ellipsis, stacking)", F_EMPH,
     r"repeat|replicat|identical|stacked|parallel column|\.\.\.|ellipsis|x ?N\b|×ᴺ|×N"),
    ("layout position (bands, symmetry, left-right split)", F_EMPH,
     r"(horizontal|vertical) (band|layer|split|layering)|symmetric|top-down|left-to-right|two-column|split into|separat\w+ (the|two)"),
    ("no emphasis: neutral background / motivation figure", F_EMPH,
     r"no (highlighted|emphasis)|background/motivation figure|this is background|not the paper'?s own"),
]

WEAKNESS_RULES = [
    ("text too small to read at print size",
     r"\bsmall (font|text|label|annotation)|small[- ]font|tiny|\d(\.\d)?[- ]?pt\b|illegible|hard to read|legibility|legible|font size|without zooming|at reduced (size|scale)|at (print|figure|small|normal|this) (size|scale)"),
    ("too dense / too many elements",
     r"dense|density|busy|crowd|cluttered|clutter|packed|\d{3,} shapes|many small|overwhelm|hard to (parse|take in|follow|trace|distinguish)|visual (load|complexity)|compress"),
    ("colour / icon coding with no legend",
     r"(no|not|without|lacks?|rather than an?)[^.;|]{0,55}(legend|explained|explicit legend|legend key|labeled|labelled|legended)|colou?r (coding|meaning|mapping)[^.;|]{0,45}not"),
    ("meaning only recoverable from the caption / body text",
     r"(caption|body text|prose|surrounding text|accompanying text|the text|section text)[^.;|]{0,45}(rely|relies|relying|require|need|to (decode|interpret|understand|explain|be understood|fully))|requires? the caption|relies on the caption|read the (caption|text)"),
    ("ambiguous or duplicated labels",
     r"(same|identical|repeated|reused|near[- ]identical)[^.;|]{0,45}(label|name)|ambiguous|share the (same|identical) (name|label)|hard to distinguish|generic label|reusing the label"),
    ("terse notation / unexplained abbreviations",
     r"abbreviat|terse|notation[^.;|]{0,45}(not explained|requires|demands|hard|parse)|math(ematical)? notation|domain familiarity|subscript|background knowledge"),
    ("legend placed far from what it explains",
     r"legend[^.;|]{0,60}(far|away|separated|below the|at the bottom|placed)"),
    ("arrows missing / connection or direction unclear",
     r"no arrows|no arrowheads|arrow direction|omits directionality|not visibly connect|no (explicit )?arrows? link|no connecting lines|easy to (miss|overlook)|visually disconnected|not visually explicit|only implied by proximity|infer(red)? (repetition|correspondence)"),
    ("colour-only distinction (fails in grayscale / print)",
     r"distinguishable only by|only by (fill )?colou?r|rely(ing)? entirely on fill|desaturat|grayscale|greyscale|monochrome|colou?r alone"),
    ("too many panels / mixed visual languages",
     r"(three|four|five|several|multiple) (different |distinct )?(visual (types|languages)|sub-?panels|panel types|panels)|mixe?s? (three|different|a )|combin(es|ing|ed)[^.;|]{0,45}(chart|diagram|photo|table|panel)|sub-?panels of different|packed into one figure"),
    ("implied repetition without a count",
     r"ellips[ei]s|\.\.\.[^.;|]{0,45}(compress|imply|rather than|unspecified)|partial outline|infer repetition|unspecified number|'\.\.\.'"),
    ("awkward aspect ratio for the column",
     r"aspect|very (tall|wide)|single-column layout makes|tall single-column|wide, short"),
    ("extraction / provenance artifact (not a design flaw)",
     r"(caption|context file|body paragraph|source svg|palette metadata|preview|paper paragraph)[^.;|]{0,70}(cut off|truncat|garbled|corrupt|not available|no (paper|body)|could not|not previewed|inferred|available)|only the .{0,35}sub-figure|read from the image alone|no section text"),
]

# colour words whose meaning we mine out of "<colour> = <phrase>" clauses
COLOR_WORDS = ["red", "green", "blue", "yellow", "orange", "gray", "grey", "purple",
               "pink", "white", "black", "gold", "teal", "cyan", "navy", "peach"]
COLOR_BUCKETS = [
    ("error / failure / bottleneck", r"error|fail|faulty|fault|violation|invalid|reject|bottleneck|stall|hang|miss\b|breakdown|overhead|defect|crash|removed|preempt|blocked|malicious|untrusted|wasted|straggler|imbalance|OOM|limit|cut|prune"),
    ("ok / success / valid / accepted", r"success|accepted|valid|healthy|hit\b|pass|correct|complete|approved|check"),
    ("novel / ours / contribution", r"novel|new |newly|contribution|our |own (novel )?comp|paper'?s own|proposed|added|augmentation|introduced|contributed"),
    ("existing / reused / baseline / passive", r"existing|unmodified|reused|baseline|prior|conventional|standard|generic|passive|background|unchanged|pre-existing|untouched|placeholder|neutral|other|surrounding"),
    ("highlight / focus / example", r"highlight|singled out|focus|emphasis|call(ed)?[- ]?out|example|selected|active|of interest|marks the"),
    ("component / module / subsystem", r"component|module|subsystem|engine|unit|controller|scheduler|manager|planner|library|service|block|core|node|worker|server|client|processor"),
    ("layer / tier / plane / region", r"layer|tier|plane|level|region|zone|band|host|device|cpu\b|gpu\b|dram|flash|kernel|user space|switch|memory|storage|network|cluster"),
    ("data / state / precision", r"data|tensor|token|weight|parameter|activation|cache|buffer|precision|fp\d|plaintext|ciphertext|hot\b|cold\b|dirty|clean|packet|request|message|entry|record|value|state"),
    ("phase / step / stage", r"phase|step\b|stage|round|iteration|offline|online|prefill|decode|forward|backward|train|inference"),
    ("flow / path / link type", r"flow|path|arrow|link|route|traffic|channel|edge|connection|bus|interconnect|nvlink|pcie"),
]


def load(semantics: str, index: str):
    csv.field_size_limit(10 ** 9)
    idx = {}
    with open(index, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            idx[(row["paper_id"], row["fig"])] = row
    recs = []
    with open(semantics, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            row = idx.get((d["paper_id"], str(d["fig"])))
            if row and row.get("type") == "diagram" and row.get("subtype") == "architecture":
                recs.append((d, row))
    return recs, idx


def eid(d) -> str:
    return f"{d['paper_id']}_fig{d['fig']}"


def fields(d) -> dict:
    e = d.get("encoding") or {}
    s = d.get("style") or {}
    out = {k: (e.get(k) or "").lower() for k in
           ("color_means", "line_style_means", "emphasis")}
    out["reusable_patterns"] = " | ".join(e.get("reusable_patterns") or []).lower()
    for k in ("stroke", "arrows", "icons", "fill", "corners", "font"):
        out["s_" + k] = str(s.get(k) or "").lower()
    return out


def run_rules(recs, rules):
    """rules: list of (group, category, field-tuple, regex). -> {(group,cat): [ids]}"""
    hits = collections.OrderedDict()
    for g, c, _f, _p in rules:
        hits.setdefault((g, c), [])
    for d, _row in recs:
        fx = fields(d)
        for g, c, fl, pat in rules:
            text = "\n".join(fx.get(k, "") for k in fl)
            if text.strip() and re.search(pat, text, re.I):
                if eid(d) not in hits[(g, c)]:
                    hits[(g, c)].append(eid(d))
    return hits


def mine_colors(recs):
    """Split color_means into '<colour> = <phrase>' clauses and bucket the phrase."""
    tbl = collections.defaultdict(collections.Counter)
    ex = collections.defaultdict(list)
    clause_re = re.compile(
        r"\b(" + "|".join(COLOR_WORDS) + r")\b[^,;=]{0,30}?(?:=|\bmeans?\b|\bmarks?\b|\bdenotes?\b|"
        r"\bhighlights?\b|\bindicates?\b|\bdistinguishes?\b|\bis\b|\bfor\b)\s*([^,;|]{3,90})", re.I)
    for d, _row in recs:
        txt = ((d.get("encoding") or {}).get("color_means") or "")
        for m in clause_re.finditer(txt):
            col = m.group(1).lower().replace("grey", "gray")
            phrase = m.group(2).lower()
            for bucket, pat in COLOR_BUCKETS:
                if re.search(pat, phrase, re.I):
                    tbl[col][bucket] += 1
                    if len(ex[(col, bucket)]) < 3:
                        ex[(col, bucket)].append(f"{eid(d)}: {col} = {phrase.strip()[:60]}")
                    break
    return tbl, ex


def weakness_hits(recs):
    hits = collections.defaultdict(list)
    quotes = collections.defaultdict(list)
    for d, _row in recs:
        for w in ((d.get("encoding") or {}).get("weaknesses") or []):
            for cat, pat in WEAKNESS_RULES:
                if re.search(pat, w, re.I):
                    if eid(d) not in hits[cat]:
                        hits[cat].append(eid(d))
                    if len(quotes[cat]) < 8:
                        quotes[cat].append(f"{eid(d)}: {w}")
    return hits, quotes


def measured(recs):
    agg, nums, n = collections.Counter(), collections.defaultdict(list), 0
    for _d, row in recs:
        try:
            st = json.loads(row.get("style") or "{}")
        except Exception:
            continue
        if not st:
            continue
        n += 1
        stroke, arrows = st.get("stroke") or {}, st.get("arrows") or {}
        steps, icons = st.get("steps") or {}, st.get("icons") or {}
        font, pal, dens = st.get("font") or {}, st.get("palette") or {}, st.get("density") or {}
        agg["corners=" + str(st.get("corners"))] += 1
        agg["fill=" + str(st.get("fill"))] += 1
        agg["any_dashed=" + str(bool(stroke.get("dashed")))] += 1
        agg["arrowheads=" + str((arrows.get("heads") or 0) > 0)] += 1
        agg["curved_arrows=" + str((arrows.get("curved") or 0) > 0)] += 1
        agg["circled_steps=" + str((steps.get("circled") or 0) > 0)] += 1
        agg["bitmap_icons=" + str((icons.get("images") or 0) > 0)] += 1
        agg["glyph_icons=" + str((icons.get("glyph_paths") or 0) > 0)] += 1
        agg["font_cls=" + str(font.get("cls"))] += 1
        agg["column=" + str((st.get("size") or {}).get("column"))] += 1
        agg["stroke_width_levels=" + str(stroke.get("widths"))] += 1
        for k, v in (("palette_n", pal.get("n")), ("gray_frac", pal.get("gray_frac")),
                     ("stroke_median", stroke.get("median"))):
            if isinstance(v, (int, float)):
                nums[k].append(v)
        if isinstance(font.get("size"), list) and len(font["size"]) == 3:
            for k, v in zip(("font_min", "font_med", "font_max"), font["size"]):
                if isinstance(v, (int, float)):
                    nums[k].append(v)
        for k in ("text", "shapes", "per_100pt2", "text_boxes"):
            if isinstance(dens.get(k), (int, float)):
                nums["density_" + k].append(dens[k])
        if isinstance((st.get("size") or {}).get("aspect"), (int, float)):
            nums["aspect"].append(st["size"]["aspect"])
    return n, agg, nums


def pct(a, b):
    return round(100.0 * a / b, 1) if b else 0.0


def quart(v):
    v = sorted(v)
    if not v:
        return {}
    q = lambda p: v[min(len(v) - 1, int(p * (len(v) - 1)))]
    return {"n": len(v), "min": v[0], "p10": q(.10), "p25": q(.25), "median": q(.5),
            "p75": q(.75), "p90": q(.90), "max": v[-1]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--semantics", default=DEF_SEM)
    ap.add_argument("--index", default=DEF_IDX)
    ap.add_argument("--out", default=DEF_OUT)
    ap.add_argument("--corpus-root", default=None, help="corpus root (<root>/extracted/...): replaces the lab/ defaults of --semantics and --index")
    a = ap.parse_args(argv)
    if a.corpus_root:
        root = os.path.abspath(a.corpus_root)
        if a.semantics == DEF_SEM: a.semantics = os.path.join(root, "extracted", "corpus_semantics.jsonl")
        if a.index == DEF_IDX: a.index = os.path.join(root, "extracted", "corpus_index.csv")
    os.makedirs(a.out, exist_ok=True)

    recs, _ = load(a.semantics, a.index)
    n = len(recs)
    print(f"architecture records: {n}", file=sys.stderr)
    out = {"n_records": n, "note": "non-measured tables are regex hits over model prose"}

    # ---- visual variables -------------------------------------------------
    hits = run_rules(recs, RULES)
    out["variables"] = {}
    with open(os.path.join(a.out, "variable_meanings.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["variable", "meaning", "count", "pct_of_%d" % n, "exemplars"])
        for (g, c), ids in hits.items():
            out["variables"].setdefault(g, {})[c] = {"count": len(ids), "exemplars": ids[:10]}
            w.writerow([g, c, len(ids), pct(len(ids), n), ";".join(ids[:6])])

    # ---- colour word -> meaning bucket ------------------------------------
    tbl, ex = mine_colors(recs)
    out["color_roles"] = {c: dict(v) for c, v in tbl.items()}
    with open(os.path.join(a.out, "color_roles.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["colour", "meaning_bucket", "clause_count", "share_of_colour", "examples"])
        for col in sorted(tbl, key=lambda c: -sum(tbl[c].values())):
            tot = sum(tbl[col].values())
            for bucket, cnt in tbl[col].most_common():
                w.writerow([col, bucket, cnt, pct(cnt, tot), " || ".join(ex[(col, bucket)][:2])])

    # ---- emphasis ----------------------------------------------------------
    emp = run_rules(recs, [("emphasis", c, f, p) for c, f, p in EMPHASIS_RULES])
    out["emphasis"] = {}
    with open(os.path.join(a.out, "emphasis.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["technique", "count", "pct_of_%d" % n, "exemplars"])
        for (_g, c), ids in sorted(emp.items(), key=lambda kv: -len(kv[1])):
            out["emphasis"][c] = {"count": len(ids), "exemplars": ids[:10]}
            w.writerow([c, len(ids), pct(len(ids), n), ";".join(ids[:6])])

    # derived: does the figure mark its novel part at all (colour OR emphasis prose)?
    pn = (r"novel|new (module|component|logic|hardware)|newly[- ]added|contribution|"
          r"own (novel )?component|paper'?s own|proposed|augmentation")
    marks = [eid(d) for d, _ in recs
             if re.search(pn, ((d.get("encoding") or {}).get("color_means") or "") + " " +
                          ((d.get("encoding") or {}).get("emphasis") or ""), re.I)]
    out["derived"] = {"marks_novel_component": {"count": len(marks), "pct": pct(len(marks), n),
                                                "exemplars": marks[:10]}}

    # ---- weaknesses --------------------------------------------------------
    wk, quotes = weakness_hits(recs)
    n_with = sum(1 for d, _ in recs if (d.get("encoding") or {}).get("weaknesses"))
    n_items = sum(len((d.get("encoding") or {}).get("weaknesses") or []) for d, _ in recs)
    out["weaknesses"] = {"_totals": {"records_with_weakness": n_with,
                                     "records_clean": n - n_with, "weakness_items": n_items}}
    with open(os.path.join(a.out, "weaknesses.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "figures", "pct_of_%d" % n, "exemplars", "quotes"])
        for cat, _p in sorted(WEAKNESS_RULES, key=lambda r: -len(wk.get(r[0], []))):
            ids = wk.get(cat, [])
            out["weaknesses"][cat] = {"count": len(ids), "exemplars": ids[:10],
                                      "quotes": quotes.get(cat, [])[:6]}
            w.writerow([cat, len(ids), pct(len(ids), n), ";".join(ids[:6]),
                        " || ".join(quotes.get(cat, [])[:3])])

    # ---- layout / legend crosstabs ----------------------------------------
    lay, pair, steps_leg = collections.Counter(), collections.Counter(), collections.Counter()
    for d, _row in recs:
        L = d.get("layout") or {}
        for k in ("legend", "step_markers", "lanes", "nesting_depth", "template", "text_density"):
            lay[f"{k}={L.get(k)}"] += 1
        pal = (d.get("style") or {}).get("palette") or []
        b = "1-3" if len(pal) <= 3 else ("4-6" if len(pal) <= 6 else ("7-9" if len(pal) <= 9 else "10+"))
        pair[(b, "legend" if L.get("legend") not in (None, "none") else "no legend")] += 1
        steps_leg[(str(L.get("step_markers")), "legend" if L.get("legend") not in (None, "none") else "no legend")] += 1
    out["layout"] = dict(lay)
    out["legend_by_palette_size"] = {f"{b}|{l}": v for (b, l), v in pair.items()}
    with open(os.path.join(a.out, "legend_steps.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["facet", "value", "count", "pct_of_%d" % n])
        for k, v in sorted(lay.items()):
            facet, val = k.split("=", 1)
            w.writerow([facet, val, v, pct(v, n)])
        w.writerow([])
        w.writerow(["palette_size(named hexes)", "legend?", "count", "pct_of_%d" % n])
        for (b, l), v in sorted(pair.items()):
            w.writerow([b, l, v, pct(v, n)])
        w.writerow([])
        w.writerow(["step_markers", "legend?", "count", "pct_of_%d" % n])
        for (s, l), v in sorted(steps_leg.items()):
            w.writerow([s, l, v, pct(v, n)])

    # ---- measured facets ---------------------------------------------------
    nm, agg, nums = measured(recs)
    out["measured"] = {"n_with_style": nm, "categorical": dict(agg),
                       "numeric": {k: quart(v) for k, v in nums.items()}}
    with open(os.path.join(a.out, "measured.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["facet", "value", "count", "pct_of_%d" % nm])
        for k, v in sorted(agg.items()):
            facet, val = k.split("=", 1)
            w.writerow([facet, val, v, pct(v, nm)])
        w.writerow([])
        w.writerow(["numeric_facet", "n", "min", "p10", "p25", "median", "p75", "p90", "max"])
        for k, v in sorted(out["measured"]["numeric"].items()):
            w.writerow([k, v["n"], v["min"], v["p10"], v["p25"], v["median"],
                        v["p75"], v["p90"], v["max"]])

    with open(os.path.join(a.out, "encoding_mine.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"wrote 6 files to {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
