#!/usr/bin/env python3
"""Build figgenie-paper-diagram/assets/exemplars/ from exemplar_selection.json (v2 layout, 2026-09-07; mechanism
figures added 2026-09-20).

Layout (each figure is stored ONCE and referenced from every template / group it illustrates):

    assets/exemplars/index.json                     everything: figures, templates, groups, counts
    assets/exemplars/<template>/index.json          architecture: ordered list for that template: id, star,
                                                    why_chosen, what_to_learn, path to the figure dir
    assets/exemplars/mechanism/<group>/index.json   mechanism: the same for one of the five v3 groups
    assets/exemplars/figures/<id>/source.svg        author SVG when the paper shipped one, otherwise the
                                                    PDF-extracted SVG (PyMuPDF export, text kept as <text>)
    assets/exemplars/figures/<id>/preview.png       render of the author SVG (only with an author source)
    assets/exemplars/figures/<id>/print.png         the figure as extracted from the published PDF, print size
    assets/exemplars/figures/<id>/semantics.json    the full semantic record
    assets/exemplars/figures/<id>/manifest.json     provenance, layout fields, `kind`, and the list of
                                                    templates (architecture) or groups (mechanism) this
                                                    figure illustrates, with their notes

exemplar_selection.json (v2): {"source": ..., "exemplars": [{"id", "template", "star": bool,
"why_chosen", "what_to_learn"}, ...]}; the same id may appear under several templates.
exemplar_selection_mechanism.json: the same with "group" (comparison / evolution / logic / walkthrough /
anatomy) instead of "template"; built with --kind mechanism (see mech_exemplar_selection.py).

    python3 build_exemplars.py [--kind architecture|mechanism] [--selection FILE] [--out DIR] [--dry-run] [--clean]

The two kinds share figures/ and the top-level index.json: an architecture build keeps the mechanism block
and figures it finds there (and vice versa); --clean removes only the tree of the kind being built --
for architecture that is the whole v1/v2 tree except mechanism/ and the mechanism-only figure dirs.
Nothing under lab/, workspace/ or paper-figure-corpus/ is ever written. The build is fully reproducible:
run the architecture build first, then the mechanism one.
"""
import argparse, csv, json, os, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
REPO = SKILL.parent
CORPUS_ROOT = REPO / "lab"                     # --corpus-root replaces it
EXTRACTED = CORPUS_ROOT / "extracted"
INDEX_CSV = EXTRACTED / "corpus_index.csv"
SEMANTICS = EXTRACTED / "corpus_semantics.jsonl"
DEFAULT_SELECTION = {"architecture": HERE / "exemplar_selection.json", "mechanism": HERE / "exemplar_selection_mechanism.json"}
DEFAULT_OUT = SKILL / "assets" / "exemplars"
TEMPLATE_ORDER = ["pipeline", "layered", "two-panel", "control-data", "hub-spoke", "matrix", "host-device",
                  "nested-stack", "baseline-vs-ours", "overview-with-inset", "control-loop", "phase-lanes",
                  "replicated-grid", "multi-tier", "dataflow-dag", "n-panel-comparison", "composite-figure",
                  "mirrored-pair", "flanked-core", "block-floorplan"]
GROUP_ORDER = ["comparison", "evolution", "logic", "walkthrough", "anatomy"]
SLOT_KEY = {"architecture": "template", "mechanism": "group"}      # the field that names a slot in the selection
SLOT_LIST = {"architecture": "templates", "mechanism": "groups"}   # the list of slot notes in manifest.json


def load_index():
    csv.field_size_limit(10**9)
    with open(INDEX_CSV, newline="", encoding="utf-8") as fh:
        return {(r["paper_id"], str(r["fig"])): r for r in csv.DictReader(fh)}


def load_semantics(index, kind="architecture"):
    """Records of one kind: index row diagram/<kind> AND the record's own `kind` (records without one are architecture)."""
    recs = {}
    with open(SEMANTICS, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            key = (rec["paper_id"], str(rec["fig"]))
            row = index.get(key)
            if row and row["type"] == "diagram" and row["subtype"] == kind and (rec.get("kind") or "architecture") == kind:
                recs[key] = rec
    return recs


def split_id(eid):
    pid, fig = eid.rsplit("_fig", 1)
    return pid, fig


def files_for(row):
    """Which corpus files this figure ships: author SVG + its PNG if present, else the PDF SVG; PDF PNG when present."""
    pid = row["paper_id"]
    src = (row.get("src_svgs") or "").split("|")[0].strip()
    pdf = (row.get("pdf_svg") or "").strip()

    def ex(rel):
        p = EXTRACTED / pid / rel if rel else None
        return p if p and p.is_file() else None

    src_svg, pdf_svg = ex(src), ex(pdf)
    src_png = ex(os.path.splitext(src)[0] + ".png") if src else None
    pdf_png = ex(os.path.splitext(pdf)[0] + ".png") if pdf else None
    out = {"source.svg": None, "source_kind": None, "preview.png": src_png, "print.png": pdf_png}
    if src_svg:
        out["source.svg"], out["source_kind"] = src_svg, "author"
    elif pdf_svg:
        out["source.svg"], out["source_kind"] = pdf_svg, "pdf"
    return out


def manifest_fields(kind, rec):
    """The layout / content fields worth showing in manifest.json, per kind."""
    lay, con = rec.get("layout", {}), rec.get("content", {})
    if kind == "architecture":
        return {"corpus_template": lay.get("template"), "direction": lay.get("direction"), "column": lay.get("column"),
                "aspect": lay.get("aspect"), "n_components": len(con.get("components") or []),
                "n_flows": len(con.get("flows") or []), "nesting_depth": lay.get("nesting_depth"), "lanes": lay.get("lanes"),
                "legend": lay.get("legend"), "step_markers": lay.get("step_markers"), "panels": lay.get("panels")}
    return {"groups_in_record": con.get("groups"), "worked_example": con.get("worked_example"), "base": con.get("base"),
            "subject": con.get("subject"), "arrangement": lay.get("arrangement"), "panel_count": lay.get("panel_count"),
            "frame_template": lay.get("frame_template"), "delta_marking": lay.get("delta_marking"),
            "direction": lay.get("direction"), "column": lay.get("column"), "aspect": lay.get("aspect"),
            "n_elements": len(con.get("elements") or []), "n_relations": len(con.get("relations") or []),
            "n_panels": len(con.get("panels") or []), "n_steps": len(con.get("steps") or []),
            "n_values": len(con.get("values") or []), "nesting_depth": lay.get("nesting_depth"), "lanes": lay.get("lanes"),
            "legend": lay.get("legend"), "step_markers": lay.get("step_markers"), "zoom_callout": lay.get("zoom_callout")}


def figure_summary(kind, eid, row, rec, f, notes):
    lay = rec.get("layout", {})
    d = {"id": eid, "kind": kind, "venue": row["venue"], "source_kind": f["source_kind"], "dir": f"figures/{eid}"}
    if kind == "architecture":
        d["corpus_template"] = lay.get("template"); d["templates"] = [x["template"] for x in notes]
    else:
        d["arrangement"] = lay.get("arrangement"); d["base"] = rec.get("content", {}).get("base")
        d["groups"] = [x["group"] for x in notes]
    return d


def read_existing_index(out):
    p = out / "index.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def mechanism_figure_dirs(out):
    """figures/<id> dirs whose manifest says kind == mechanism (or that appear only in the mechanism block)."""
    res = set()
    figdir = out / "figures"
    if not figdir.is_dir():
        return res
    for d in figdir.iterdir():
        m = d / "manifest.json"
        if d.is_dir() and m.is_file():
            try:
                if json.loads(m.read_text(encoding="utf-8")).get("kind") == "mechanism":
                    res.add(d.name)
            except Exception:
                pass
    return res


def clean_tree(out, kind):
    """--clean: architecture removes everything except mechanism/ and mechanism-only figure dirs; mechanism removes
    only mechanism/ and those figure dirs. Trees built by other scripts are never touched: ai/ (build_ai_exemplars.py)
    and styles/ (build_style_exemplars.py). A figure dir with kind == mechanism is mechanism-only by construction (a
    figure cannot be both kinds: the corpus record has exactly one kind)."""
    if not out.exists():
        return
    mech_dirs = mechanism_figure_dirs(out)
    if kind == "mechanism":
        shutil.rmtree(out / "mechanism", ignore_errors=True)
        for name in mech_dirs:
            shutil.rmtree(out / "figures" / name, ignore_errors=True)
        return
    for p in out.iterdir():
        if p.name in ("mechanism", "ai", "styles"):
            continue
        if p.name == "figures":
            for d in p.iterdir():
                if d.name not in mech_dirs:
                    shutil.rmtree(d) if d.is_dir() else d.unlink()
            continue
        shutil.rmtree(p) if p.is_dir() else p.unlink()


def main():
    global EXTRACTED, INDEX_CSV, SEMANTICS
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["architecture", "mechanism"], default="architecture")
    ap.add_argument("--corpus-root", default=str(CORPUS_ROOT), help="corpus root: <root>/extracted/corpus_index.csv, corpus_semantics.jsonl and the figure files (default: the systems corpus, lab/)")
    ap.add_argument("--selection", help="default: exemplar_selection.json / exemplar_selection_mechanism.json by --kind")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--clean", action="store_true", help="delete the existing exemplar tree of this kind first")
    a = ap.parse_args()
    EXTRACTED = Path(a.corpus_root).resolve() / "extracted"; INDEX_CSV = EXTRACTED / "corpus_index.csv"; SEMANTICS = EXTRACTED / "corpus_semantics.jsonl"
    kind = a.kind
    slot_key, slot_list = SLOT_KEY[kind], SLOT_LIST[kind]
    order = TEMPLATE_ORDER if kind == "architecture" else GROUP_ORDER
    selection = Path(a.selection) if a.selection else DEFAULT_SELECTION[kind]
    sel = json.load(open(selection, encoding="utf-8"))
    entries = sel["exemplars"]
    index = load_index(); sem = load_semantics(index, kind)
    out = Path(a.out)
    problems = []
    by_fig = {}  # id -> {"row","rec","files","notes":[...]}
    per_slot = {}
    for e in entries:
        eid = e["id"]
        slot = e.get(slot_key) or e.get("template") or e.get("group")
        if slot not in order:
            problems.append(f"{eid}: unknown {slot_key} {slot!r}"); continue
        key = split_id(eid)
        row, rec = index.get(key), sem.get(key)
        if row is None or rec is None:
            problems.append(f"{eid}: not a {kind}-diagram record"); continue
        f = files_for(row)
        if not f["source.svg"]:
            problems.append(f"{eid}: no SVG at all"); continue
        if f["source_kind"] == "pdf" and "<text" not in f["source.svg"].read_text(encoding="utf-8", errors="ignore"):
            problems.append(f"{eid}: PDF SVG has no <text> (text outlined in the PDF)"); continue
        entry = by_fig.setdefault(eid, {"row": row, "rec": rec, "files": f, "notes": []})
        note = {slot_key: slot, "star": bool(e.get("star")), "why_chosen": e.get("why_chosen", ""), "what_to_learn": e.get("what_to_learn", "")}
        if e.get("note_source"):
            note["note_source"] = e["note_source"]
        entry["notes"].append(note)
        per_slot.setdefault(slot, []).append({"id": eid, **note})
    if problems:
        print("problems:"); [print("  " + p) for p in problems]
    if a.dry_run:
        print(f"dry run ({kind}): {len(by_fig)} figures, {sum(len(v) for v in per_slot.values())} {slot_key} slots")
        for t in order:
            if t in per_slot:
                print(f"  {t:22s} {len(per_slot[t]):3d}  stars {sum(1 for x in per_slot[t] if x['star'])}")
        return 0
    existing = read_existing_index(out)
    if a.clean:
        clean_tree(out, kind)
    figdir = out / "figures"; figdir.mkdir(parents=True, exist_ok=True)
    fig_index = []
    for eid, entry in sorted(by_fig.items()):
        row, rec, f = entry["row"], entry["rec"], entry["files"]
        d = figdir / eid; d.mkdir(exist_ok=True)
        shutil.copyfile(f["source.svg"], d / "source.svg")
        if f["preview.png"]: shutil.copyfile(f["preview.png"], d / "preview.png")
        if f["print.png"]: shutil.copyfile(f["print.png"], d / "print.png")
        (d / "semantics.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest = {
            "id": eid, "kind": kind, "paper_id": row["paper_id"], "fig": row["fig"], "venue": row["venue"],
            "year": int(row["year"]) if str(row.get("year", "")).isdigit() else row.get("year"),
            "caption": row.get("caption"), **manifest_fields(kind, rec), "tool": row.get("tool"),
            "confidence": rec.get("confidence"), "source_kind": f["source_kind"],
            "files": {k: v for k, v in {
                "source.svg": "author source SVG (from the paper's arXiv/source bundle)" if f["source_kind"] == "author"
                              else "SVG extracted from the published PDF (PyMuPDF; text kept as <text>, fonts embedded)",
                "preview.png": "PNG render of the author SVG" if f["preview.png"] else None,
                "print.png": "the figure as extracted from the published PDF, at print size" if f["print.png"] else None,
                "semantics.json": "full semantic record for this figure", "manifest.json": "this file"}.items() if v},
            "original_paths": {k: (os.path.relpath(v, REPO) if v else None) for k, v in
                               {"source.svg": f["source.svg"], "preview.png": f["preview.png"], "print.png": f["print.png"]}.items()},
            slot_list: entry["notes"],
        }
        (d / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        fig_index.append(figure_summary(kind, eid, row, rec, f, entry["notes"]))
    slot_root = out if kind == "architecture" else out / "mechanism"
    rel_fig = "../figures" if kind == "architecture" else "../../figures"
    for t in order:
        if t not in per_slot: continue
        td = slot_root / t; td.mkdir(parents=True, exist_ok=True)
        items = sorted(per_slot[t], key=lambda x: (not x["star"], x["id"]))
        for x in items: x["dir"] = f"{rel_fig}/{x['id']}"
        (td / "index.json").write_text(json.dumps({slot_key: t, "n": len(items), "stars": sum(1 for x in items if x["star"]),
                                                   "how_to_read": f"open {rel_fig}/<id>/print.png (or preview.png) and manifest.json; star = must-see"
                                                                  + ("; these are references to strengthen a layout derived from your figure's own needs -- "
                                                                     "borrow the device that serves it, never the layout wholesale" if kind == "mechanism" else ""),
                                                   "exemplars": items}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # top-level index: this kind's block is rewritten, the other kind's block and figures are kept
    other = "mechanism" if kind == "architecture" else "architecture"
    kept_figs = [x for x in (existing or {}).get("figures", []) if (x.get("kind") or "architecture") == other] if existing else []
    if kept_figs and not (out / "figures" / kept_figs[0]["id"]).is_dir():
        kept_figs = []   # the other kind's tree is gone (e.g. a --clean of that kind); drop its stale entries
    total = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    block = {"selection": os.path.relpath(selection, SKILL), "corpus": sel.get("source"), "n_figures": len(fig_index),
             "n_slots": sum(len(v) for v in per_slot.values()),
             ("by_template" if kind == "architecture" else "by_group"): {t: len(per_slot[t]) for t in order if t in per_slot}}
    if existing and kept_figs:
        index_doc = dict(existing)
    else:
        index_doc = {}
    index_doc["generated_by"] = "figgenie-paper-diagram/scripts/distill/build_exemplars.py"
    if kind == "architecture":
        index_doc.update(block)
        index_doc.pop("architecture", None)
    else:
        index_doc["mechanism"] = block
        if not kept_figs:   # mechanism built into an empty tree: no architecture counts to keep
            for k in ("selection", "corpus", "n_figures", "n_slots", "by_template"):
                index_doc.pop(k, None)
    index_doc["layout"] = ("<template>/index.json lists that template's exemplars (architecture); mechanism/<group>/index.json "
                           "lists a v3 group's exemplars (mechanism); figures/<id>/{source.svg, preview.png?, print.png?, "
                           "semantics.json, manifest.json} holds each figure once, manifest.kind says which kind it is")
    index_doc["provenance"] = "Figures are reproduced from published OSDI/NSDI/SOSP/ASPLOS papers for style reference only."
    index_doc["total_bytes"] = total
    index_doc["figures"] = (kept_figs + fig_index) if kind == "mechanism" else (fig_index + kept_figs)
    (out / "index.json").write_text(json.dumps(index_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(fig_index)} {kind} figures / {block['n_slots']} slots to {out} ({total/1e6:.1f} MB total; "
          f"{len(kept_figs)} {other} figures kept)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
