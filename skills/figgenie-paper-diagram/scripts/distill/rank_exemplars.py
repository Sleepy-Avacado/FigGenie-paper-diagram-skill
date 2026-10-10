#!/usr/bin/env python3
"""Rank exemplar candidates per layout template from the full corpus (727 good architecture figures).

Produces an OVER-selected candidate list per template for a human review pass (the reviewer drops the
weak ones; `pick_exemplars.py` then copies the survivors into assets/exemplars/).

Candidate pools
  core templates (pipeline … host-device)      layout.template == T
  A-H added templates                          layout_stats.ENRICHED_PATTERNS text evidence
                                               (+ nesting_depth >= 3 for nested-stack)
  I-M new templates                            evidence regex OR type_discovery.json cluster member
                                               (n-panel-comparison / composite-figure: layout.panels rule)
Score (higher = better)
  +3 already an exemplar in the shipped selection      +2 confidence high / +1 medium
  +2 type-discovery cluster member (I-M) / core template match for A-H
  -1 per recorded weakness (max -3), -1 if text_density == dense. Figures whose SVG has no <text>
  (text outlined in the PDF itself) or no SVG at all are excluded and listed under summary.excluded.
  round-robin over venues so no venue takes more than ~40% of a template's slots, and at most
  one figure per paper per template.
Quota: pool >= 100 -> 30 candidates; 50-99 -> 25; < 50 -> min(pool, 30).

    python3 rank_exemplars.py --out <dir>   # writes candidates.json + candidates.csv
"""
import argparse, csv, json, os, re, sys, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
REPO = SKILL.parent
sys.path.insert(0, str(HERE))
import layout_stats as LS  # noqa: E402

CORE = ["pipeline", "layered", "two-panel", "control-data", "hub-spoke", "matrix", "host-device"]
ADDED = ["nested-stack", "baseline-vs-ours", "overview-with-inset", "control-loop", "phase-lanes",
         "replicated-grid", "multi-tier", "dataflow-dag"]
NEW = ["n-panel-comparison", "composite-figure", "mirrored-pair", "flanked-core", "block-floorplan"]
VENUE_CAP = 0.4


def blob(r):
    e = r.get("encoding") or {}
    c = r.get("content") or {}
    return " || ".join(filter(None, [
        r.get("summary", ""), c.get("key_idea", ""), c.get("reading_order", ""),
        " ".join(e.get("reusable_patterns") or []), " ".join(r.get("tags") or []),
        r["_idx"].get("caption", "") or "", e.get("emphasis") or "",
        e.get("color_means") or "", e.get("line_style_means") or ""]))


def fid(r):
    return f"{r['paper_id']}_fig{r['fig']}"


def svg_status(r):
    """('author'|'pdf'|'none', text_ok) — which SVG an exemplar would ship and whether its text is <text>."""
    row = r["_idx"]
    pid = row["paper_id"]
    src = (row.get("src_svgs") or "").split("|")[0].strip()
    pdf = (row.get("pdf_svg") or "").strip()
    for kind, rel in (("author", src), ("pdf", pdf)):
        if not rel:
            continue
        p = REPO / "lab" / "extracted" / pid / rel
        if p.is_file():
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            return kind, ("<text" in txt)
    return "none", False


def pools(recs, td):
    rx = {k: re.compile(v, re.I) for k, v in LS.ENRICHED_PATTERNS.items()}
    vrx = re.compile(LS.VARIANT_PANEL_RE, re.I)
    clusters = {k[4:]: set(v) for k, v in td.items() if k.startswith("new_")}
    out = collections.defaultdict(dict)  # template -> id -> evidence dict
    for r in recs:
        b = blob(r); i = fid(r); lay = r["layout"]; dep = r["content"]["depicts"]
        out[lay["template"]][i] = {"core": True} if lay["template"] in CORE else {}
        for t in ADDED + ["mirrored-pair", "flanked-core", "block-floorplan"]:
            if t in rx and rx[t].search(b):
                out[t].setdefault(i, {})["regex"] = True
        if (lay.get("nesting_depth") or 0) >= 3:
            out["nested-stack"].setdefault(i, {})["depth"] = lay.get("nesting_depth")
        panels = lay.get("panels") or 1
        if panels >= 3 and (dep == "comparison" or vrx.search(b)):
            out["n-panel-comparison"].setdefault(i, {})["panels"] = panels
        elif panels >= 2 and dep != "comparison":
            out["composite-figure"].setdefault(i, {})["panels"] = panels
        for t, members in clusters.items():
            if i in members:
                out[t].setdefault(i, {})["cluster"] = True
    out.pop("other", None)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--selection", default=str(HERE / "exemplar_selection.json"))
    ap.add_argument("--type-discovery", default=str(HERE / "type_discovery.json"))
    ap.add_argument("--quota", default="30,25,30", help="pool>=100, 50-99, <50 caps")
    ap.add_argument("--corpus-root", default=str(REPO / "lab"), help="corpus root (<root>/extracted/...); default: the systems corpus under lab/")
    a = ap.parse_args()
    LS.set_corpus_root(a.corpus_root)
    q_big, q_mid, q_small = [int(x) for x in a.quota.split(",")]
    recs = LS.load()
    byid = {fid(r): r for r in recs}
    shipped = collections.defaultdict(set)
    for e in json.load(open(a.selection))["exemplars"]:
        shipped[e["template"]].add(e["id"])
    td = json.load(open(a.type_discovery))
    P = pools(recs, td)
    status = {i: svg_status(r) for i, r in byid.items()}
    rows = []; summary = {}; excluded = collections.defaultdict(list)
    for t in CORE + ADDED + NEW:
        pool = P.get(t, {})
        scored = []
        for i, ev in pool.items():
            r = byid[i]; kind, text_ok = status[i]
            s = 0.0; why = []
            if i in shipped[t]: s += 3; why.append("shipped exemplar")
            conf = r.get("confidence"); s += {"high": 2, "medium": 1}.get(conf, 0)
            if ev.get("cluster"): s += 2; why.append("type-discovery cluster")
            if ev.get("core"): why.append("core template")
            if ev.get("regex"): why.append("text evidence")
            if ev.get("depth"): why.append(f"depth {ev['depth']}")
            if ev.get("panels"): why.append(f"{ev['panels']} panels")
            nw = len(r["encoding"].get("weaknesses") or []); s -= min(nw, 3)
            if r["layout"].get("text_density") == "dense": s -= 1
            if kind == "none" or not text_ok:  # hard exclusion: nothing to ship, or text outlined in the PDF itself
                excluded[t].append((i, "no SVG" if kind == "none" else "text as paths"))
                continue
            scored.append((s, i, r, kind, text_ok, why, nw))
        scored.sort(key=lambda x: (-x[0], x[1]))
        n_pool = len(scored)
        quota = q_big if n_pool >= 100 else q_mid if n_pool >= 50 else min(n_pool, q_small)
        cap = max(2, int(quota * VENUE_CAP + 0.999))
        chosen = []; per_venue = collections.Counter(); papers = set()
        for s, i, r, kind, text_ok, why, nw in scored:
            if len(chosen) >= quota: break
            v = re.sub(r"\d+$", "", r.get("venue", "")); pid = r["paper_id"]
            if pid in papers or per_venue[v] >= cap: continue
            chosen.append((s, i, r, kind, text_ok, why, nw)); per_venue[v] += 1; papers.add(pid)
        if len(chosen) < quota:  # relax the venue cap if needed
            for item in scored:
                if len(chosen) >= quota: break
                if item[1] not in {c[1] for c in chosen} and item[2]["paper_id"] not in papers:
                    chosen.append(item); papers.add(item[2]["paper_id"])
        summary[t] = {"pool": n_pool, "quota": quota, "chosen": len(chosen), "venues": dict(per_venue), "excluded": excluded[t]}
        for rank, (s, i, r, kind, text_ok, why, nw) in enumerate(chosen, 1):
            rows.append({"template": t, "rank": rank, "id": i, "score": s, "venue": r.get("venue"),
                         "corpus_template": r["layout"]["template"], "confidence": r.get("confidence"),
                         "weaknesses": nw, "text_density": r["layout"].get("text_density"),
                         "column": r["layout"].get("column"), "direction": r["layout"].get("direction"),
                         "svg": kind, "text_ok": text_ok, "why": "; ".join(why),
                         "one_liner": (r.get("system") or {}).get("one_liner", ""),
                         "pdf_png": str(REPO / "lab" / "extracted" / r["paper_id"] / (os.path.splitext(r["_idx"].get("pdf_svg") or "")[0] + ".png")) if r["_idx"].get("pdf_svg") else "",
                         "src_png": str(REPO / "lab" / "extracted" / r["paper_id"] / (os.path.splitext((r["_idx"].get("src_svgs") or "").split("|")[0])[0] + ".png")) if r["_idx"].get("src_svgs") else ""})
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    json.dump({"summary": summary, "candidates": rows}, open(out / "candidates.json", "w"), indent=1, ensure_ascii=False)
    with open(out / "candidates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    distinct = len({r["id"] for r in rows})
    print(f"{len(rows)} candidate slots over {len(summary)} templates, {distinct} distinct figures")
    for t, s in summary.items():
        print(f"  {t:22s} pool {s['pool']:4d}  quota {s['quota']:3d}  chosen {s['chosen']:3d}  venues {s['venues']}")


if __name__ == "__main__":
    main()
