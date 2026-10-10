#!/usr/bin/env python3
"""Aggregate the mechanism semantic records (kind == "mechanism" in corpus_semantics.jsonl) per v3 group.

    python3 mech_semantics_stats.py --semantics lab/extracted/corpus_semantics.jsonl \
        --index lab/extracted/corpus_index.csv --out <dir> [--labels mech-prescreen/typedisc/labels_v3_full.jsonl]

The mechanism counterpart of layout_stats.py / encoding_mine.py, kept deliberately simple: the records are
the vocabulary of references/semantics-schema-mechanism.md, so the aggregation is per field. Outputs in --out:

  stats.json   per primary group (and 'all'): counts and distributions of every enumerated field, element /
               relation / step / panel counts (median, q3, p90), logic sizes, palette sizes, index cross-tabs
               (column, tool, venue, author source)
  report.md    the same as tables, one section per field, groups as columns -- what the doc-writing step reads
  texts.md     every free-text field (subject, key_idea, reading_order, differs, state_means, marker_means,
               color_means, line_style_means, emphasis, reusable_patterns, weaknesses, values.linked_by) grouped by
               primary group with the figure id, for the layouts / encoding / anti-patterns writers
  exemplars.md one line per record: id, group(s), base, arrangement, panels, confidence, tool, source PNG path

Nothing outside --out is written.
"""
import argparse, collections, csv, json, os, statistics
from pathlib import Path

GROUPS = ["comparison", "evolution", "logic", "walkthrough", "anatomy"]
ENUM_FIELDS = {
    "layout": ["arrangement", "panel_count", "frame_template", "delta_marking", "direction", "nesting_depth", "lanes",
               "legend", "step_markers", "zoom_callout", "text_density", "column"],
    "content": ["base", "depicts", "worked_example"],
    "style": ["fill", "corners", "background", "icons"],
}
TEXT_FIELDS = [("content", "subject"), ("content", "key_idea"), ("content", "reading_order"), ("encoding", "color_means"),
               ("encoding", "line_style_means"), ("encoding", "state_means"), ("encoding", "marker_means"),
               ("encoding", "emphasis"), ("style", "stroke"), ("style", "font"), ("style", "arrows")]


def pct(xs, p):
    if not xs: return None
    xs = sorted(xs); k = (len(xs) - 1) * p / 100; lo = int(k); hi = min(lo + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 1)


def dist(values):
    c = collections.Counter(str(v) for v in values if v is not None and v != "")
    n = sum(c.values())
    return {k: {"n": v, "share": round(v / n, 3)} for k, v in c.most_common()} if n else {}


def numbers(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return {"n": len(xs), "mean": round(statistics.mean(xs), 1) if xs else None, "median": pct(xs, 50), "q3": pct(xs, 75),
            "p90": pct(xs, 90), "max": max(xs) if xs else None}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--semantics", required=True); ap.add_argument("--index", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--labels", default=None, help="labels_v3_full.jsonl: prior groups, to report how often the record corrected them")
    a = ap.parse_args()
    ext = os.path.dirname(os.path.abspath(a.index))   # <corpus>/extracted
    def rel_png(pid, svg):
        p = os.path.join(ext, pid, svg.replace(".svg", ".png")); r = os.path.relpath(p, os.getcwd())
        return p if r.startswith("..") else r
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    csv.field_size_limit(10 ** 9)
    idx = {f"{r['paper_id']}_fig{r['fig']}": r for r in csv.DictReader(open(a.index, encoding="utf-8"))}
    prior = {}
    if a.labels and os.path.exists(a.labels):
        for line in open(a.labels, encoding="utf-8"):
            if line.strip():
                r = json.loads(line); prior[r["id"]] = r
    recs = []
    for line in open(a.semantics, encoding="utf-8"):
        if not line.strip(): continue
        r = json.loads(line)
        if r.get("kind") != "mechanism": continue
        r["_id"] = f"{r['paper_id']}_fig{r['fig']}"; r["_row"] = idx.get(r["_id"], {})
        recs.append(r)
    by = {g: [r for r in recs if (r["content"].get("groups") or ["?"])[0] == g] for g in GROUPS}
    by["all"] = recs

    stats = {}
    for g, rs in by.items():
        s = {"n": len(rs)}
        for sec, fields in ENUM_FIELDS.items():
            for f in fields:
                s[f"{sec}.{f}"] = dist([(r.get(sec) or {}).get(f) for r in rs])
        s["content.groups_any"] = dist([x for r in rs for x in (r["content"].get("groups") or [])])
        s["content.secondary_groups"] = dist([x for r in rs for x in (r["content"].get("groups") or [])[1:]])
        s["elements_per_record"] = numbers([len(r["content"].get("elements") or []) for r in rs])
        s["relations_per_record"] = numbers([len(r["content"].get("relations") or []) for r in rs])
        s["panels_per_record"] = numbers([len(r["content"].get("panels") or []) for r in rs if r["content"].get("panels")])
        s["steps_per_record"] = numbers([len(r["content"].get("steps") or []) for r in rs if r["content"].get("steps")])
        s["element_kinds"] = dist([e.get("kind") for r in rs for e in (r["content"].get("elements") or []) if isinstance(e, dict)])
        s["element_highlighted_share"] = round(sum(1 for r in rs for e in (r["content"].get("elements") or []) if isinstance(e, dict) and e.get("highlighted"))
                                              / max(1, sum(len(r["content"].get("elements") or []) for r in rs)), 3)
        s["relation_kinds"] = dist([e.get("kind") for r in rs for e in (r["content"].get("relations") or []) if isinstance(e, dict)])
        s["relations_with_step_share"] = round(sum(1 for r in rs for e in (r["content"].get("relations") or []) if isinstance(e, dict) and e.get("step") is not None)
                                               / max(1, sum(len(r["content"].get("relations") or []) for r in rs)), 3)
        s["panel_axis"] = dist([p.get("axis") for r in rs for p in (r["content"].get("panels") or []) if isinstance(p, dict)])
        s["panels_with_verdict_share"] = round(sum(1 for r in rs for p in (r["content"].get("panels") or []) if isinstance(p, dict) and p.get("verdict"))
                                               / max(1, sum(len(r["content"].get("panels") or []) for r in rs)), 3)
        s["step_marker_style"] = dist([(r["content"].get("steps") or [{}])[0].get("marker", "")[:1].isdigit() and "digits" or "letters-or-other"
                                       for r in rs if r["content"].get("steps")])
        s["steps_with_carries_share"] = round(sum(1 for r in rs for st in (r["content"].get("steps") or []) if isinstance(st, dict) and st.get("carries"))
                                              / max(1, sum(len(r["content"].get("steps") or []) for r in rs)), 3)
        lg = [r["content"].get("logic") for r in rs if isinstance(r["content"].get("logic"), dict)]
        s["logic_records"] = len(lg)
        s["logic_states_per_record"] = numbers([len(l.get("states") or []) for l in lg])
        s["logic_transitions_per_record"] = numbers([len(l.get("transitions") or []) for l in lg])
        s["logic_with_decisions"] = sum(1 for l in lg if l.get("decisions"))
        s["logic_guard_share"] = round(sum(1 for l in lg for t in (l.get("transitions") or []) if isinstance(t, dict) and t.get("guard"))
                                       / max(1, sum(len(l.get("transitions") or []) for l in lg)), 3)
        vals = [r["content"].get("values") for r in rs if isinstance(r["content"].get("values"), dict)]
        s["values_records"] = len(vals)
        s["values_linked_by"] = dist([(v.get("linked_by") or "").split(" ")[0].strip(",;(") for v in vals])
        s["palette_entries_per_record"] = numbers([len(r["style"].get("palette") or []) for r in rs])
        s["reusable_patterns_per_record"] = numbers([len(r["encoding"].get("reusable_patterns") or []) for r in rs])
        s["weaknesses_per_record"] = numbers([len(r["encoding"].get("weaknesses") or []) for r in rs])
        s["records_with_weakness_share"] = round(sum(1 for r in rs if r["encoding"].get("weaknesses")) / max(1, len(rs)), 3)
        s["confidence"] = dist([r.get("confidence") for r in rs])
        s["index.column"] = dist([r["_row"].get("column") or "single" for r in rs])
        s["index.tool"] = dist([r["_row"].get("tool") for r in rs])
        s["index.venue"] = dist([r["_row"].get("venue") for r in rs])
        s["index.author_source_share"] = round(sum(1 for r in rs if r["_row"].get("src_svgs")) / max(1, len(rs)), 3)
        s["tags"] = dict(collections.Counter(t for r in rs for t in (r.get("tags") or [])).most_common(25))
        if prior:
            chg = [r for r in rs if r["_id"] in prior and (r["content"].get("groups") or []) != prior[r["_id"]]["groups"]]
            s["groups_changed_vs_prior"] = {"n": len(chg), "primary_changed": sum(1 for r in chg if (r["content"].get("groups") or ["?"])[0] != prior[r["_id"]]["primary"])}
        stats[g] = s
    json.dump(stats, open(out / "stats.json", "w"), indent=1, ensure_ascii=False)

    # report.md: one table per field, groups as columns
    cols = ["all"] + GROUPS
    md = [f"# Mechanism semantic records — {len(recs)} records", "",
          "| group | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols),
          "| n | " + " | ".join(str(stats[c]["n"]) for c in cols) + " |", ""]
    def is_dist(d):
        return isinstance(d, dict) and d and all(isinstance(v, dict) and "share" in v for v in d.values())
    for key in [k for k in stats["all"] if is_dist(stats["all"][k])]:
        values = sorted({v for c in cols for v in stats[c][key]}, key=lambda v: -stats["all"][key].get(v, {}).get("n", 0))
        if not values: continue
        md += [f"## {key}", "", "| value | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
        for v in values[:20]:
            md.append(f"| {v} | " + " | ".join(
                (f"{stats[c][key][v]['n']} ({stats[c][key][v]['share']*100:.0f}%)" if v in stats[c][key] else "–") for c in cols) + " |")
        md.append("")
    md += ["## counts per record (median / q3 / p90 / max)", "", "| measure | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for key in [k for k in stats["all"] if isinstance(stats["all"][k], dict) and "median" in stats["all"][k]]:
        md.append(f"| {key} | " + " | ".join(
            (f"{stats[c][key]['median']} / {stats[c][key]['q3']} / {stats[c][key]['p90']} / {stats[c][key]['max']} (n={stats[c][key]['n']})"
             if stats[c][key]["n"] else "–") for c in cols) + " |")
    md += ["", "## shares", "", "| measure | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for key in [k for k in stats["all"] if isinstance(stats["all"][k], (int, float))]:
        md.append(f"| {key} | " + " | ".join(str(stats[c][key]) for c in cols) + " |")
    md += ["", "## tags (all)", "", ", ".join(f"{t} {n}" for t, n in stats["all"]["tags"].items()), ""]
    (out / "report.md").write_text("\n".join(md), encoding="utf-8")

    # texts.md: the free text per group
    tx = [f"# Free-text fields of the mechanism records, by primary group ({len(recs)} records)", ""]
    for g in GROUPS:
        tx += [f"# {g} ({len(by[g])} records)", ""]
        for r in sorted(by[g], key=lambda r: r["_id"]):
            c, e = r["content"], r["encoding"]
            tx += [f"## {r['_id']}  [{', '.join(c.get('groups') or [])}; base {c.get('base')}; {r['layout'].get('arrangement')}"
                   f"{' x' + str(r['layout'].get('panel_count')) if (r['layout'].get('panel_count') or 1) > 1 else ''}; "
                   f"{'worked-example; ' if c.get('worked_example') else ''}{r.get('confidence')}]", ""]
            for sec, f in TEXT_FIELDS:
                v = (r.get(sec) or {}).get(f)
                if v: tx.append(f"- {f}: {v}")
            for p in c.get("panels") or []:
                if isinstance(p, dict) and (p.get("differs") or p.get("verdict")):
                    tx.append(f"- panel {p.get('label')!r} ({p.get('axis')}): {p.get('differs') or ''}{' -> ' + p['verdict'] if p.get('verdict') else ''}")
            if isinstance(c.get("values"), dict):
                tx.append(f"- values: {c['values'].get('what')} | linked by {c['values'].get('linked_by')} | results: {c['values'].get('result_cells')}")
            if isinstance(c.get("logic"), dict):
                l = c["logic"]; tx.append(f"- logic: {len(l.get('states') or [])} states, {len(l.get('transitions') or [])} transitions, {len(l.get('decisions') or [])} decisions")
            for p in e.get("reusable_patterns") or []: tx.append(f"- reusable: {p}")
            for w in e.get("weaknesses") or []: tx.append(f"- weakness: {w}")
            tx.append("")
    (out / "texts.md").write_text("\n".join(tx), encoding="utf-8")

    ex = ["| id | groups | base | arrangement | panels | worked | conf | column | tool | png |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(recs, key=lambda r: ((r["content"].get("groups") or ["?"])[0], r["_id"])):
        row = r["_row"]; c = r["content"]
        cands = [rel_png(row.get('paper_id', ''), x) for x in (row.get("src_svgs") or "").split("|") if x]
        if row.get("pdf_svg"): cands.append(rel_png(row.get('paper_id', ''), row['pdf_svg']))
        png = next((x for x in cands if os.path.exists(x)), "")
        ex.append(f"| {r['_id']} | {', '.join(c.get('groups') or [])} | {c.get('base')} | {r['layout'].get('arrangement')} | {r['layout'].get('panel_count')} | "
                  f"{'yes' if c.get('worked_example') else ''} | {r.get('confidence')} | {row.get('column') or 'single'} | {row.get('tool')} | {png} |")
    (out / "exemplars.md").write_text("\n".join(ex) + "\n", encoding="utf-8")
    print(f"{len(recs)} mechanism records: " + ", ".join(f"{g} {len(by[g])}" for g in GROUPS) + f"; wrote {out}/stats.json, report.md, texts.md, exemplars.md")


if __name__ == "__main__":
    main()
