#!/usr/bin/env python3
"""Turn the mechanism exemplar review (exemplar-review/mechanism/review.html decisions) into
exemplar_selection_mechanism.json for `build_exemplars.py --kind mechanism`.

    python3 mech_exemplar_selection.py --decisions decisions.json --notes doc_notes.jsonl notes_1.jsonl notes_2.jsonl ...
        [--ids ../../../mech-prescreen/semantics/candidate_ids.txt] [--out exemplar_selection_mechanism.json]
        [--no-secondary] [--doc layouts.md]

Inputs
  --decisions  the JSON copied from the review page: {"drop": {group: [ids]}, "star": {group: [ids]}, "move": {id: group}}
               (any key may be missing; an empty file or "{}" means "keep everything, star nothing").
  --doc        references/mechanism/layouts.md: its "### Exemplars" tables give what_to_learn for the figures
               the writing agent chose (the "what to learn" column); those rows are marked note_source "doc".
  --ids        the candidate list (default: every mechanism record in the corpus).

Rules
  * every candidate that is not dropped becomes a slot under its primary group -- the record's first group,
    overridden by "move" (a move also drops the old primary group from the figure's secondary list) -- starred
    when the reviewer starred it in ANY tab (stars follow the figure, not the tab);
  * unless --no-secondary, it also becomes an unstarred slot under each secondary group of the record
    (content.groups[1:]), so a figure that is both a comparison and a walkthrough is listed under both;
  * why_chosen / what_to_learn come from layouts.md when the figure is in its exemplar tables, otherwise from the
    record: why_chosen = content.key_idea (or subject), what_to_learn = encoding.reusable_patterns joined
    (note_source "record"); a later note-writing pass can overwrite them in the selection file.
Nothing under lab/ is written.
"""
import argparse, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
REPO = SKILL.parent
GROUPS = ["comparison", "evolution", "logic", "walkthrough", "anatomy"]
ID_RE = r"([a-z]+\d\d-\d{3,4}_fig(?:tex)?\d+[a-z]?)"   # osdi24-004_fig1, asplos25-006_figtex2, iclr25-0430_fig1


def doc_notes(path):
    """{id: {"what_to_learn": ..., "group": ..., "doc_star": bool}} from the '### Exemplars' tables of layouts.md."""
    out = {}
    text = Path(path).read_text(encoding="utf-8")
    group = None
    for line in text.split("\n"):
        m = re.match(r"^## (\w[\w-]*) ", line)
        if m and m.group(1) in GROUPS:
            group = m.group(1)
        if not line.startswith("|") or group is None:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        m = re.search(ID_RE, cells[0])
        if not m or cells[0].lower().startswith("id"):
            continue
        fid = m.group(1)
        # columns: id | base | arrangement | what to learn | png   (the doc's table)
        note = cells[3] if len(cells) >= 5 else cells[-1]
        out.setdefault(fid, {"what_to_learn": note, "group": group, "doc_star": "★" in cells[0]})
    return out


def clip(s, n=320):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--doc", default="", help="parse the '### Exemplars' tables of this layouts.md for notes (only sensible BEFORE "
                                              "update_exemplar_tables.py has rewritten them; afterwards the tables mirror this selection). "
                                              "The original 40 notes are kept in exemplar-review/mechanism/notes/doc_notes.jsonl -- pass that via --notes instead")
    ap.add_argument("--ids", default=str(REPO / "mech-prescreen" / "semantics" / "candidate_ids.txt"))
    ap.add_argument("--semantics", default=str(REPO / "lab" / "extracted" / "corpus_semantics.jsonl"))
    ap.add_argument("--corpus-root", default=None, help="corpus root (<root>/extracted/...): replaces the lab/ default of --semantics")
    ap.add_argument("--out", default=str(HERE / "exemplar_selection_mechanism.json"))
    ap.add_argument("--no-secondary", action="store_true", help="list each figure under its primary group only")
    ap.add_argument("--notes", nargs="*", default=[], help="JSONL files ({id, why_chosen?, what_to_learn, note_source?}) -- the layouts.md "
                                                          "writer's notes (doc_notes.jsonl, note_source doc) and the note agents' rewrites "
                                                          "(notes_N.jsonl, note_source agent by default); later files override earlier ones")
    a = ap.parse_args()
    if a.corpus_root and a.semantics == str(REPO / "lab" / "extracted" / "corpus_semantics.jsonl"):
        a.semantics = str(Path(a.corpus_root).resolve() / "extracted" / "corpus_semantics.jsonl")
    raw = Path(a.decisions).read_text(encoding="utf-8").strip()
    dec = json.loads(raw) if raw else {}
    drop = {i for v in (dec.get("drop") or {}).values() for i in v}
    star = {i for v in (dec.get("star") or {}).values() for i in v}
    move = dec.get("move") or {}
    want = None
    if a.ids and Path(a.ids).is_file():
        want = {x.strip() for x in Path(a.ids).read_text().replace("\n", ",").split(",") if x.strip()}
    notes = doc_notes(a.doc) if a.doc and Path(a.doc).is_file() else {}
    agent_notes = {}
    for nf in a.notes:
        for line in Path(nf).read_text(encoding="utf-8").splitlines():
            if line.strip():
                n = json.loads(line); agent_notes[n["id"]] = n
    recs = {}
    for line in open(a.semantics, encoding="utf-8"):
        if not line.strip(): continue
        r = json.loads(line)
        if r.get("kind") != "mechanism": continue
        fid = f"{r['paper_id']}_fig{r['fig']}"
        if want is None or fid in want:
            recs[fid] = r
    missing = sorted((want or set()) - set(recs))
    if missing:
        print(f"warning: {len(missing)} candidate ids have no mechanism record: {missing[:8]}", file=sys.stderr)
    bad_move = {i: g for i, g in move.items() if g not in GROUPS}
    if bad_move:
        print(f"warning: ignoring moves to unknown groups: {bad_move}", file=sys.stderr)
    entries = []
    n_doc = n_rec = n_agent = 0
    for fid in sorted(recs):
        if fid in drop:
            continue
        r = recs[fid]
        groups = [g for g in (r["content"].get("groups") or []) if g in GROUPS] or ["anatomy"]
        primary = move.get(fid) if move.get(fid) in GROUPS else groups[0]
        # a move says "not the group it was shown under": the record's old primary group is dropped, its other
        # secondary groups stay
        secondary = [] if a.no_secondary else [g for g in groups if g != primary and not (fid in move and g == groups[0])]
        if fid in agent_notes:
            n = agent_notes[fid]
            why = clip(n.get("why_chosen") or r["content"].get("key_idea") or r["content"].get("subject") or "")
            learn, src = clip(n["what_to_learn"], 400), n.get("note_source", "agent")
            if src == "doc": n_doc += 1
            else: n_agent += 1
        elif fid in notes:
            why = clip(r["content"].get("key_idea") or r["content"].get("subject") or "")
            learn, src = clip(notes[fid]["what_to_learn"], 400), "doc"
            n_doc += 1
        else:
            why = clip(r["content"].get("key_idea") or r["content"].get("subject") or "")
            pats = r.get("encoding", {}).get("reusable_patterns") or []
            learn, src = clip("; ".join(p.strip().rstrip(".") for p in pats if p.strip()), 400), "record"
            n_rec += 1
        for g, is_primary in [(primary, True)] + [(g, False) for g in secondary]:
            entries.append({"id": fid, "group": g, "star": bool(fid in star and is_primary), "primary": is_primary,
                            "why_chosen": why, "what_to_learn": learn, "note_source": src})
    order = {g: i for i, g in enumerate(GROUPS)}
    entries.sort(key=lambda e: (order[e["group"]], not e["star"], e["id"]))
    sel = {"_comment": ("mechanism selection (v3 groups, 2026-09-20): the exemplar candidates of mech-prescreen/semantics/candidates.json "
                        "(30 per group, human-rated good, semantic record written by an agent), reviewed by hand on "
                        "exemplar-review/mechanism/review.html (drops + stars + moves); what_to_learn from references/mechanism/"
                        "layouts.md for the figures its exemplar tables cite (note_source doc), else from the record's "
                        "reusable_patterns (note_source record), or rewritten by a note agent that looked at the figure (note_source agent). "
                        "A figure is listed under its primary group (starred there when "
                        "starred at all) and unstarred under its secondary groups."),
           "source": {"semantics": "lab/extracted/corpus_semantics.jsonl", "index": "lab/extracted/corpus_index.csv",
                      "filter": "record kind == 'mechanism' and index row diagram/mechanism/good; candidates = mech-prescreen/semantics/candidate_ids.txt",
                      "decisions": str(Path(a.decisions)), "n_candidates": len(recs), "n_dropped": len(drop & set(recs)),
                      "n_starred": len(star & set(recs)), "n_moved": len([i for i in move if i in recs])},
           "exemplars": entries}
    Path(a.out).write_text(json.dumps(sel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    by_g = {g: [e for e in entries if e["group"] == g] for g in GROUPS}
    print(f"wrote {a.out}: {len(entries)} slots for {len({e['id'] for e in entries})} figures "
          f"(dropped {len(drop & set(recs))}, starred {len(star & set(recs))}, moved {len([i for i in move if i in recs])}; "
          f"notes from agent {n_agent} / doc {n_doc} / record {n_rec})")
    for g in GROUPS:
        v = by_g[g]
        print(f"  {g:12s} {len(v):3d} slots  primary {sum(1 for e in v if e['primary']):3d}  stars {sum(1 for e in v if e['star'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
