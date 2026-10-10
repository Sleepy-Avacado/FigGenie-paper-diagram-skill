#!/usr/bin/env python3
"""Regenerate every layout statistic quoted in references/layouts.md.

Reads the read-only corpus (lab/extracted/corpus_semantics.jsonl joined with
lab/extracted/corpus_index.csv on paper_id+fig) and keeps the 727 records whose
index row has type=='diagram' and subtype=='architecture'.

    python3 figgenie-paper-diagram/scripts/distill/layout_stats.py            # everything
    python3 .../layout_stats.py --section global
    python3 .../layout_stats.py --template pipeline
    python3 .../layout_stats.py --patterns pipeline                     # reusable_patterns / weaknesses
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
REPO = os.path.abspath(os.path.join(SKILL, os.pardir))
CORPUS_ROOT = os.path.join(REPO, "lab")   # the systems corpus; --corpus-root / set_corpus_root() point at another one
EXTRACTED = os.path.join(CORPUS_ROOT, "extracted")
INDEX_CSV = os.path.join(EXTRACTED, "corpus_index.csv")
SEMANTICS = os.path.join(EXTRACTED, "corpus_semantics.jsonl")


def set_corpus_root(root):
    """Read <root>/extracted/corpus_index.csv and corpus_semantics.jsonl instead of the systems corpus under lab/."""
    global CORPUS_ROOT, EXTRACTED, INDEX_CSV, SEMANTICS
    CORPUS_ROOT = os.path.abspath(root)
    EXTRACTED = os.path.join(CORPUS_ROOT, "extracted")
    INDEX_CSV = os.path.join(EXTRACTED, "corpus_index.csv")
    SEMANTICS = os.path.join(EXTRACTED, "corpus_semantics.jsonl")

TEMPLATES = [
    "pipeline", "layered", "two-panel", "control-data",
    "hub-spoke", "matrix", "other", "host-device",
]

# Keyword clusters used for the "pitfalls" tables. Each weakness string may match
# more than one cluster; counts are therefore per (figure, cluster) pairs.
WEAKNESS_CLUSTERS = {
    "dense / small text": r"\bdense|small (font|text)|tiny|hard to read|without zoom|crowded|packed|cramped|compress",
    "unexplained colour / icon": r"color coding|colour coding|no (in-figure )?legend|legend.*(missing|absent)|unexplained|not legended|\bno key\b|color mapping",
    "legend placement": r"legend .*(far|below|away|placed|small|outside)",
    "relies on caption / body text": r"rel(y|ies|ying) on the (caption|text|body)|only in the caption|cross-referenc|requires reading|explained (only )?in the (text|caption)|not defined in the figure|without reading",
    "unlabelled / ambiguous arrows": r"arrow.*(unlabel|no label|not labeled|ambiguo|direction|arrowhead)|no arrowheads|arrows (are )?(not|un)|missing arrow|no explicit arrows|arrow semantics",
    "abbreviations / notation": r"abbrevia|acronym|jargon|undefined (term|label)|notation",
    "repeated / duplicate labels": r"repeat|duplicate|identical label|same label|reus(e|ing) the label",
    "black box / omitted detail": r"black box|no internal detail|opaque|not shown|omits",
    "overlap / alignment": r"overlap|misalign|not aligned|collide|touching",
    "extreme aspect ratio": r"aspect ratio|very (wide|tall)|extremely (wide|tall)|too (wide|tall)",
    "too many panels": r"panels?\b.*(many|dense)|many (sub-?)?panels|multi-panel",
    "print / greyscale risk": r"greyscale|grayscale|print|colou?r-?blind|similar (shades|colors|colours)|low contrast|contrast",
    "raster content": r"raster|bitmap|screenshot|photo|pixel",
}

# Regexes used to size the ADDED templates in references/layouts.md. Matched against a
# figure's summary + key_idea + reading_order + reusable_patterns + tags + caption + emphasis
# + color_means + line_style_means. These are evidence counts, not a second classification:
# a figure can match several, and every match already has one of the eight corpus templates.
ENRICHED_PATTERNS = {
    "overview-with-inset": r"(zoom(ed|s|-in| in)?|inset|callout|call-out|magnif|blow[- ]up|exploded|expand(s|ed|ing) (a|the|one))",
    "baseline-vs-ours": r"((baseline|prior work|existing|traditional|conventional|naive|strawman|status quo|vanilla|before)\b[^|]{0,60}\b(vs\.?|versus|v\.s\.|compared (to|with)|and (our|ours|this work))|\bvs\.?\s*(our|ours|proposed|this work)|\(a\)[^|]{0,50}(existing|prior|baseline|traditional|current|today|now)|V\.S\.)",
    "control-loop": r"(feedback (loop|arrow|edge|path)|closed[- ]loop|control loop|loops? back|circular (loop|optimization|pipeline|arrangement)|cycl(e|ic|ical) (loop|arrangement|diagram)|iterat(e|es|ive) (loop|back)|back to (the )?(start|first|earlier|beginning))",
    "phase-lanes": r"(gantt|timeline|time ?axis|swim-?lane|over time.{0,40}(lane|row|band)|execution trace|time (flows|runs|axis|progress))",
    "replicated-grid": r"(ellips[ei]s|\bN-?1\b|worker [0-9].{0,30}worker N|\.\.\. *(to|denote|indicat|repeat)|(repeated|identical|replicated|homogeneous|stacked|offset) (boxes|instances|nodes|cores|units|tiles|columns|replicas|cards)|(denote|indicate|imply|suggest)s? (more|additional|repetition|scale-?out)|scale-?out|pool of)",
    "multi-tier": r"(client(s)?[^|]{0,40}server|multi-?tier|three-?tier|front-?end[^|]{0,30}back-?end|edge[^|]{0,20}cloud|user[- ]facing|API (server|gateway)|gateway)",
    "dataflow-dag": r"(computation graph|dataflow graph|data-?flow graph|operator graph|\bDAG\b|graph IR|subgraph|node-and-edge|graph of (operators|nodes|tasks)|task graph)",
    # added 2026-09-07 after the 736-figure type-discovery pass (templates I-M)
    "mirrored-pair": r"(mirror(ed|s|ing)?\b|symmetric(al)?\b|\btwin\b|two (identical|peer|symmetric|matching|parallel|side-by-side) (stacks|nodes|hosts|columns|sides|halves|pipelines|engines|structures|machines|domains)|sender[^|]{0,40}receiver|peer (nodes|hosts|stacks)|left and right (halves|sides|nodes|hosts|stacks))",
    "flanked-core": r"(central(ly)?[^|]{0,40}(engine|core|hub|box|component|scheduler|runtime|module|kernel)|(engine|core|runtime|scheduler|hub)[^|]{0,30}in the (middle|centre|center)|flank(ed|ing)?\b|sandwich(ed)?\b|(above|top)[^|]{0,50}(interfaces?|applications?|apis?|callers?|frontends?)[^|]{0,80}(below|bottom)[^|]{0,50}(hardware|kernel|devices?|substrate|backends?))",
    "block-floorplan": r"(floor-?plan|die (layout|photo|plan|area)|block diagram|systolic|on-chip (network|interconnect|memory|bus|buffer)|micro-?architectur|scratchpad|register file|(compute|tensor|dsp|simt|processing|systolic|mac) (array|cores?|units?|lanes?|elements?)|\b(l1|l2|l3|llc) cache|dram controller|memory controller|accelerator (block|tile|datapath|core)|datapath|crossbar|\bfsm\b|hardware (block|module|unit)s?)",
}

# n-panel-comparison / composite-figure are sized from `layout.panels` plus this regex, see section_enriched.
VARIANT_PANEL_RE = r"(variants?|strategies|strategy|alternatives?|configurations?|scenarios?|states?|designs?|schemes?|approaches|options?|cases?|modes?|phases?|steps?|stages?|snapshots?|before[^|]{0,20}after|same (mechanism|structure|skeleton|layout|vocabulary|system|pipeline|architecture))[^|]{0,60}(\(a\)|\(b\)|panels?|sub-?figures?|sub-?diagrams?|side-by-side|stacked|three|four)|(\(a\)|\(b\)|panels?|sub-?figures?|sub-?diagrams?|side-by-side|stacked|three|four)[^|]{0,60}(variants?|strategies|strategy|alternatives?|configurations?|scenarios?|states?|designs?|schemes?|approaches|options?|cases?|modes?|phases?|snapshots?)"


def load() -> list[dict]:
    csv.field_size_limit(10**9)
    index: dict[tuple[str, str], dict] = {}
    with open(INDEX_CSV, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            index[(row["paper_id"], str(row["fig"]))] = row
    recs = []
    with open(SEMANTICS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            row = index.get((rec["paper_id"], str(rec["fig"])))
            if row is None:
                continue
            if row["type"] != "diagram" or row["subtype"] != "architecture":
                continue
            rec["_idx"] = row
            recs.append(rec)
    return recs


def quantiles(values):
    v = sorted(values)
    if not v:
        return None
    n = len(v)
    return (v[0], v[int(n * 0.25)], statistics.median(v), v[int(n * 0.75)], v[int(n * 0.90)], v[-1])


def fmt_q(values, label):
    q = quantiles(values)
    if q is None:
        return f"  {label}: (none)"
    return (f"  {label}: min {q[0]} | q1 {q[1]} | median {q[2]} | q3 {q[3]} | p90 {q[4]} | max {q[5]}"
            f" | mean {sum(values)/len(values):.1f}")


def counts(items):
    return ", ".join(f"{k} {v}" for k, v in Counter(items).most_common())


def size_pt(rec):
    try:
        return json.loads(rec["_idx"]["style"])["size"]
    except Exception:
        return {}


def n_comp(rec):
    return len((rec.get("content") or {}).get("components") or [])


def n_flow(rec):
    return len((rec.get("content") or {}).get("flows") or [])


def crosstab(recs, title, keyfn):
    print(f"\n-- {title} x template")
    rows = defaultdict(Counter)
    for r in recs:
        rows[keyfn(r)][r["layout"]["template"]] += 1
    print(" " * 26 + "".join(t[:11].rjust(13) for t in TEMPLATES) + "    total")
    for k in sorted(rows, key=lambda k: -sum(rows[k].values())):
        line = "".join(str(rows[k][t]).rjust(13) for t in TEMPLATES)
        print(f"{str(k)[:25]:26}{line}{sum(rows[k].values()):9}")


def section_global(recs):
    print(f"\n=== GLOBAL  (n={len(recs)} architecture diagrams)")
    print("  templates:", counts(r["layout"]["template"] for r in recs))
    print("  tools:", counts(r["_idx"]["tool"] for r in recs))
    print("  venues:", counts(r["_idx"]["venue"] for r in recs))
    print("  confidence:", counts(r.get("confidence") for r in recs))
    print(fmt_q([n_comp(r) for r in recs], "components"))
    print(fmt_q([n_flow(r) for r in recs], "flows     "))
    print("  nesting_depth:", counts(r["layout"]["nesting_depth"] for r in recs))
    print("  lanes true:", sum(1 for r in recs if r["layout"]["lanes"] is True), f"/ {len(recs)}")
    print("  legend:", counts(r["layout"]["legend"] for r in recs))
    print("  step_markers:", counts(r["layout"]["step_markers"] for r in recs))
    print("  panels:", counts(r["layout"].get("panels") for r in recs))
    print("  column:", counts(r["layout"]["column"] for r in recs))
    print("  direction:", counts(r["layout"]["direction"] for r in recs))
    print("  text_density:", counts(r["layout"]["text_density"] for r in recs))
    for col in ("single", "double"):
        sel = [r for r in recs if r["layout"]["column"] == col]
        asp = [round(float(r["layout"]["aspect"]), 2) for r in sel if r["layout"].get("aspect")]
        w = [round(size_pt(r)["w"], 1) for r in sel if size_pt(r).get("w")]
        h = [round(size_pt(r)["h"], 1) for r in sel if size_pt(r).get("h")]
        print(f"  [{col}] n={len(sel)}")
        print(fmt_q(asp, f"  aspect[{col}]"))
        print(fmt_q(w, f"  width pt[{col}]"))
        print(fmt_q(h, f"  height pt[{col}]"))
        band = Counter("<1.0" if x < 1 else "1.0-1.5" if x < 1.5 else "1.5-2.0" if x < 2
                       else "2.0-3.0" if x < 3 else "3.0-4.5" if x < 4.5 else ">=4.5" for x in asp)
        print(f"    aspect bands[{col}]:", ", ".join(f"{k} {v}" for k, v in band.most_common()))
    nov = [sum(1 for c in (r["content"].get("components") or []) if c.get("novel")) for r in recs]
    frac = [a / b for a, b in zip(nov, [n_comp(r) for r in recs]) if b]
    print(f"  novel components: median {statistics.median(nov)}, median fraction {statistics.median(frac):.2f}")
    dash = sum(1 for r in recs if re.search(r"dash", (r.get("encoding", {}).get("line_style_means") or ""), re.I))
    print(f"  line_style_means mentions 'dashed': {dash} / {len(recs)}")
    nw = [len(r.get("encoding", {}).get("weaknesses") or []) for r in recs]
    print("  weaknesses per figure:", counts(nw))
    for depicts, group in sorted(
        defaultdict(list, {d: [r for r in recs if r["content"]["depicts"] == d]
                           for d in {r["content"]["depicts"] for r in recs}}).items(),
        key=lambda kv: -len(kv[1]),
    ):
        numbered = sum(1 for r in group if r["layout"]["step_markers"] != "none")
        print(f"  numbered when depicts={depicts:26} {numbered}/{len(group)} = {100*numbered/len(group):.0f}%")
    for lg in ("none", "inside", "below", "right"):
        pal = []
        for r in recs:
            if r["layout"]["legend"] != lg:
                continue
            try:
                pal.append(json.loads(r["_idx"]["style"])["palette"]["n"])
            except Exception:
                pass
        if pal:
            print(f"  palette size when legend={lg:7} median {statistics.median(pal)} (n={len(pal)})")


def section_crosstabs(recs):
    print("\n=== CROSS-TABS")
    crosstab(recs, "depicts", lambda r: r["content"]["depicts"])
    crosstab(recs, "abstraction", lambda r: r["system"]["abstraction"])
    crosstab(recs, "direction", lambda r: r["layout"]["direction"])
    crosstab(recs, "column", lambda r: r["layout"]["column"])
    crosstab(recs, "lanes", lambda r: r["layout"]["lanes"])
    crosstab(recs, "legend", lambda r: r["layout"]["legend"])
    crosstab(recs, "step_markers", lambda r: r["layout"]["step_markers"])
    crosstab(recs, "nesting_depth", lambda r: r["layout"]["nesting_depth"])
    crosstab(recs, "panels", lambda r: r["layout"].get("panels"))
    crosstab(recs, "text_density", lambda r: r["layout"]["text_density"])
    crosstab(recs, "n_components", lambda r: ("1-5" if n_comp(r) <= 5 else "6-10" if n_comp(r) <= 10
                                              else "11-15" if n_comp(r) <= 15 else "16-20" if n_comp(r) <= 20 else "21+"))


def section_per_template(recs, only=None):
    by = defaultdict(list)
    for r in recs:
        by[r["layout"]["template"]].append(r)
    for t in sorted(by, key=lambda t: -len(by[t])):
        if only and t != only:
            continue
        g = by[t]
        n = len(g)
        print(f"\n=== {t.upper()}  n={n} ({100*n/len(recs):.0f}% of {len(recs)})")
        print("  depicts:", counts(r["content"]["depicts"] for r in g))
        print("  abstraction:", counts(r["system"]["abstraction"] for r in g))
        dom = Counter()
        for r in g:
            for d in (r["system"].get("domain") or []):
                dom[d] += 1
        print("  domains(top8):", ", ".join(f"{k} {v}" for k, v in dom.most_common(8)))
        print("  direction:", counts(r["layout"]["direction"] for r in g))
        print(fmt_q([n_comp(r) for r in g], "components"))
        print(fmt_q([n_flow(r) for r in g], "flows     "))
        print("  nesting_depth:", counts(r["layout"]["nesting_depth"] for r in g))
        lanes = sum(1 for r in g if r["layout"]["lanes"] is True)
        print(f"  lanes true: {lanes}/{n} = {100*lanes/n:.0f}%")
        leg = sum(1 for r in g if r["layout"]["legend"] != "none")
        print(f"  legend present: {leg}/{n} = {100*leg/n:.0f}%  ({counts(r['layout']['legend'] for r in g)})")
        stp = sum(1 for r in g if r["layout"]["step_markers"] != "none")
        print(f"  step markers: {stp}/{n} = {100*stp/n:.0f}%  ({counts(r['layout']['step_markers'] for r in g)})")
        print("  panels:", counts(r["layout"].get("panels") for r in g))
        dbl = sum(1 for r in g if r["layout"]["column"] == "double")
        print(f"  column: double {dbl}/{n} = {100*dbl/n:.0f}%  ({counts(r['layout']['column'] for r in g)})")
        print("  text_density:", counts(r["layout"]["text_density"] for r in g))
        print("  confidence:", counts(r.get("confidence") for r in g))
        print("  tools:", counts(r["_idx"]["tool"] for r in g))
        for col in ("single", "double"):
            sel = [r for r in g if r["layout"]["column"] == col]
            asp = [round(float(r["layout"]["aspect"]), 2) for r in sel if r["layout"].get("aspect")]
            if asp:
                print(fmt_q(asp, f"  aspect[{col}] n={len(asp)}"))
                w = [round(size_pt(r)["w"], 1) for r in sel if size_pt(r).get("w")]
                h = [round(size_pt(r)["h"], 1) for r in sel if size_pt(r).get("h")]
                if w:
                    print(fmt_q(w, f"  width pt[{col}]"))
                    print(fmt_q(h, f"  height pt[{col}]"))


def section_patterns(recs, only=None, top=25):
    by = defaultdict(list)
    for r in recs:
        by[r["layout"]["template"]].append(r)
    print("\n=== WEAKNESS CLUSTERS (a weakness string may match several clusters)")
    tot = Counter()
    per = defaultdict(Counter)
    for r in recs:
        for w in (r.get("encoding", {}).get("weaknesses") or []):
            for name, pat in WEAKNESS_CLUSTERS.items():
                if re.search(pat, w.lower()):
                    tot[name] += 1
                    per[r["layout"]["template"]][name] += 1
    for name, c in tot.most_common():
        line = "  ".join(f"{t[:4]} {per[t][name]}" for t in TEMPLATES if per[t][name])
        print(f"  {c:4d}  {name:28} {line}")
    for t in sorted(by, key=lambda t: -len(by[t])):
        if only and t != only:
            continue
        print(f"\n=== {t.upper()} reusable_patterns (first {top} of "
              f"{sum(len(r.get('encoding', {}).get('reusable_patterns') or []) for r in by[t])})")
        seen = 0
        for r in by[t]:
            for p in (r.get("encoding", {}).get("reusable_patterns") or []):
                if seen >= top:
                    break
                print(f"  [{r['paper_id']}_fig{r['fig']}] {p}")
                seen += 1


def section_style(recs):
    """Style measurements taken at print size (index column `style`)."""
    def st(r):
        try:
            return json.loads(r["_idx"]["style"])
        except Exception:
            return {}

    def pick(path, group=None):
        out = []
        for r in (group or recs):
            v = st(r)
            for k in path:
                v = v.get(k) if isinstance(v, dict) else None
                if v is None:
                    break
            if isinstance(v, (int, float)):
                out.append(v)
        return out

    print("\n=== STYLE MEASURED AT PRINT SIZE")
    print(fmt_q(pick(["density", "shapes"]), "shapes per figure"))
    print(fmt_q(pick(["density", "text_boxes"]), "text boxes"))
    print(fmt_q(pick(["density", "per_100pt2"]), "elements per 100 pt^2"))
    print(fmt_q(pick(["palette", "n"]), "distinct fill colours"))
    print(fmt_q([round(100 * v) for v in pick(["palette", "gray_frac"])], "grey fraction x100"))
    print(fmt_q(pick(["stroke", "median"]), "median stroke pt"))
    print(fmt_q(pick(["stroke", "widths"]), "distinct stroke widths"))
    sizes = [st(r).get("font", {}).get("size") for r in recs]
    sizes = [s for s in sizes if isinstance(s, list) and len(s) >= 3]
    print(fmt_q([s[0] for s in sizes], "font size: smallest pt"))
    print(fmt_q([s[1] for s in sizes], "font size: median pt  "))
    print(fmt_q([s[2] for s in sizes], "font size: largest pt "))
    print("  corners:", counts(st(r).get("corners") for r in recs))
    print("  fill:", counts(st(r).get("fill") for r in recs))
    print("  font class:", counts(st(r).get("font", {}).get("cls") for r in recs))
    print("  uses dashed strokes:", sum(1 for r in recs if st(r).get("stroke", {}).get("dashed")), f"/ {len(recs)}")
    print("  has raster images:", sum(1 for r in recs if (st(r).get("icons", {}).get("images") or 0) > 0), f"/ {len(recs)}")
    print("  has vector glyph icons:", sum(1 for r in recs if (st(r).get("icons", {}).get("glyph_paths") or 0) > 0), f"/ {len(recs)}")
    print("  zero curved lines (orthogonal routing):",
          sum(1 for r in recs if (st(r).get("arrows", {}).get("curved") or 0) == 0), f"/ {len(recs)}")
    print(fmt_q(pick(["arrows", "heads"]), "arrowheads"))
    print("\n-- per template medians")
    print(f"  {'template':14}{'shapes':>9}{'text_bx':>9}{'colours':>9}{'font pt':>9}{'per100':>9}")
    by = defaultdict(list)
    for r in recs:
        by[r["layout"]["template"]].append(r)
    for t in TEMPLATES:
        g = by.get(t) or []
        if not g:
            continue

        def med(path):
            v = pick(path, g)
            return round(statistics.median(v), 1) if v else None

        fonts = [st(r).get("font", {}).get("size") for r in g]
        fonts = [f[1] for f in fonts if isinstance(f, list) and len(f) > 1]
        print(f"  {t:14}{str(med(['density','shapes'])):>9}{str(med(['density','text_boxes'])):>9}"
              f"{str(med(['palette','n'])):>9}{str(round(statistics.median(fonts),2) if fonts else None):>9}"
              f"{str(med(['density','per_100pt2'])):>9}")


def section_enriched(recs):
    """Evidence counts for the eight added templates in layouts.md."""
    def blob(r):
        e = r.get("encoding") or {}
        c = r.get("content") or {}
        return " || ".join(filter(None, [
            r.get("summary", ""), c.get("key_idea", ""), c.get("reading_order", ""),
            " ".join(e.get("reusable_patterns") or []), " ".join(r.get("tags") or []),
            r["_idx"].get("caption", "") or "", e.get("emphasis") or "",
            e.get("color_means") or "", e.get("line_style_means") or "",
        ]))

    print("\n=== ADDED-TEMPLATE EVIDENCE (text search; a figure may match several)")
    for name, pat in ENRICHED_PATTERNS.items():
        rx = re.compile(pat, re.I)
        hits = [r for r in recs if rx.search(blob(r))]
        print(f"\n  {name}: {len(hits)}/{len(recs)}")
        print("    by corpus template:", counts(r["layout"]["template"] for r in hits))
        print("    by depicts:", counts(r["content"]["depicts"] for r in hits))
    deep = [r for r in recs if (r["layout"]["nesting_depth"] or 0) >= 3]
    print(f"\n  nested-stack (nesting_depth >= 3): {len(deep)}/{len(recs)}")
    print("    by corpus template:", counts(r["layout"]["template"] for r in deep))
    print("    depth:", counts(r["layout"]["nesting_depth"] for r in deep))
    # panel-based templates (I, J): same vocabulary in >=3 panels vs heterogeneous sub-figures
    vrx = re.compile(VARIANT_PANEL_RE, re.I)
    multi = [r for r in recs if (r["layout"].get("panels") or 1) >= 2]
    npc = [r for r in multi if (r["layout"].get("panels") or 1) >= 3 and (r["content"]["depicts"] == "comparison" or vrx.search(blob(r)))]
    comp = [r for r in multi if r not in npc and r["content"]["depicts"] != "comparison"]
    two = [r for r in multi if r not in npc and r not in comp]
    print(f"\n  multi-panel figures (panels >= 2): {len(multi)}/{len(recs)}; panels:", counts(r["layout"]["panels"] for r in multi))
    print(f"  n-panel-comparison (panels >= 3 and comparison/variant wording): {len(npc)}/{len(recs)}")
    print("    by corpus template:", counts(r["layout"]["template"] for r in npc))
    print("    by depicts:", counts(r["content"]["depicts"] for r in npc))
    print("    panels:", counts(r["layout"]["panels"] for r in npc))
    print(f"  composite-figure (panels >= 2, not a comparison, heterogeneous sub-figures): {len(comp)}/{len(recs)}")
    print("    by corpus template:", counts(r["layout"]["template"] for r in comp))
    print("    by depicts:", counts(r["content"]["depicts"] for r in comp))
    print("    panels:", counts(r["layout"]["panels"] for r in comp))
    print(f"  remaining two-panel comparisons (panels == 2, comparison): {len(two)}/{len(recs)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--section",
                    choices=["global", "crosstabs", "templates", "patterns", "style", "enriched", "all"],
                    default="all")
    ap.add_argument("--template", help="restrict per-template output to one template id")
    ap.add_argument("--patterns", metavar="TEMPLATE", help="print reusable_patterns for one template")
    ap.add_argument("--corpus-root", default=CORPUS_ROOT, help="corpus root: <root>/extracted/corpus_index.csv + corpus_semantics.jsonl (default: the systems corpus, lab/)")
    args = ap.parse_args()
    set_corpus_root(args.corpus_root)

    recs = load()
    if len(recs) != 727:
        print(f"warning: expected 727 architecture diagrams, got {len(recs)}", file=sys.stderr)

    if args.patterns:
        section_patterns(recs, only=args.patterns)
        return 0
    if args.section in ("global", "all"):
        section_global(recs)
    if args.section in ("style", "all"):
        section_style(recs)
    if args.section in ("crosstabs", "all"):
        section_crosstabs(recs)
    if args.section in ("templates", "all"):
        section_per_template(recs, only=args.template)
    if args.section in ("enriched", "all"):
        section_enriched(recs)
    if args.section in ("patterns", "all"):
        section_patterns(recs, only=args.template)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
