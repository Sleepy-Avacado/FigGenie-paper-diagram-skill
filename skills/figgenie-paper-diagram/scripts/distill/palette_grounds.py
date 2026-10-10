#!/usr/bin/env python3
"""Distil the palettes whose *ground* is not a grey box: transparent (outline-only or no containers) and tinted.

The 11 families in references/palettes.json were clustered on the hue vocabulary of the fills, and the
representative `container` colour of a cluster is its most common usable member value -- so a family whose
members mostly draw containers as bare outlines still gets a grey container hex, and every swatch card shows a
grey ground.  In the corpus that ground is the minority: of the 726 good architecture figures with semantic
records, 356 draw their containers as outlines only (nesting >= 2 but no container / lane fill), 41 have no
containers at all, 7 fill them white, 161 grey, 52 give each region its own tint and 109 use one tint (blue 45,
orange/cream 20, green 17, red/pink 10, teal 8, yellow 6, purple 3).

This script classifies every figure by ground, clusters the transparent set on the same features as
palette_cluster.py, groups the tinted set by the ground's hue family, and emits one palette per family with
`container` = null (transparent: outline only) or the modal tint.  Curated names live in CURATION below, matched
by exemplar overlap as in palette_cluster.py.

    python3 palette_grounds.py --semantics lab/extracted/corpus_semantics.jsonl \
        --index lab/extracted/corpus_index.csv --out <scratch> [--k 0] [--min-size 20] [--min-tint 20] \
        [--append-to figgenie-paper-diagram/references/palettes.json]

Outputs in --out: figures_ground.json (per-figure class + roles), clusters.json, report.md (one section per
candidate with its member hexes and exemplar PNG paths), candidates.json (the palette entries).  --append-to
appends the entries whose id is not already present (existing palettes are never modified) and records the
ground statistics under general_rules.ground; run make_swatches.py afterwards.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette_cluster as pc  # noqa: E402

ROLES = ["canvas", "container", "lane", "module", "module-alt", "accent", "stroke", "text",
         "text-muted", "arrow", "arrow-accent", "legend"]
WARM = {"orange", "yellow"}

# Curated names, matched to a cluster by exemplar overlap (ids are <pid>_fig<fig>); a cluster no entry
# matches keeps a generated id and is reported as uncurated.
CURATION = {
    "blue-outline": dict(
        id="blue-outline", name="Blue boxes, outline containers",
        description="Light-blue component boxes straight on the white page; groups and hosts are drawn as outlines only "
                    "(0.5-0.75 pt, solid or dashed, no fill), with a strong Office blue or an orange box for the contribution.",
        when_to_use="The transparent-ground twin of blue-orange / blue-mono: the same blue vocabulary when the figure has "
                    "several nested groups and a grey slab behind each would stack up muddy; the outline keeps nesting legible.",
        exemplars=["osdi26-094_fig1", "osdi24-032_fig9", "nsdi24-033_fig1", "asplos26-002_fig1"]),
    "pastel-outline": dict(
        id="pastel-outline", name="Cream and pastel boxes, outline containers",
        description="Cream / peach default boxes with pale-blue, pale-green and pink alternates for the other kinds of "
                    "component, an amber or red accent, and containers drawn as bare outlines on white.",
        when_to_use="Dense figures with several kinds of boxes (the cream-pastel look) when the regions should not add "
                    "yet another fill; the pastel fills already separate the kinds, the outline only delimits the region.",
        exemplars=["asplos26-026_fig6", "asplos26-080_fig5", "asplos25-100_fig3", "asplos25-056_fig3"]),
    "ink-outline": dict(
        id="ink-outline", name="Near-white boxes, ink outlines, one accent",
        description="White or near-white boxes with black 0.75-1 pt outlines, thin outline containers (often rounded or "
                    "dashed) and at most one saturated fill - crimson, orange or blue - on the box the paper adds.",
        when_to_use="Small single-column figures and TikZ-like drawings printed small: the transparent twin of "
                    "high-contrast. Everything reads in greyscale, colour is spent on one element.",
        exemplars=["nsdi26-091_fig4", "sosp25-007_fig2", "asplos26-008_fig1", "sosp23-011_fig3"]),
    "green-outline": dict(
        id="green-outline", name="Green boxes, outline containers",
        description="Pale-green component boxes with pale-blue / pink alternates, red reserved for the highlighted path, "
                    "containers as solid or dashed outlines on white.",
        when_to_use="Pipelines and stacks where one path must jump out (the green-red look) drawn without a grey ground, "
                    "typically with dashed host or trust boundaries.",
        exemplars=["osdi23-011_fig5", "nsdi24-107_fig5", "nsdi25-054_fig2", "nsdi23-027_fig4"]),
    "greyscale-outline": dict(
        id="greyscale-outline", name="Greyscale, outline containers",
        description="No hue at all: light-grey or white boxes, black outlines and text, containers as black or dashed "
                    "outlines on the white page; red or blue is used at most for a word or an arrow.",
        when_to_use="B/W-safe figures and print-first venues when the structure is nested: the transparent twin of "
                    "greyscale, where a mid-grey container slab would swallow the grey boxes.",
        exemplars=["osdi23-032_fig5", "osdi24-007_fig3", "osdi23-014_fig4", "osdi23-039_fig3"]),
    "categorical-outline": dict(
        id="categorical-outline", name="Categorical hues, outline containers",
        description="Four to six distinct hues used as categories (pink, blue, peach, green, lavender boxes), a crimson "
                    "or magenta accent, and containers or panel frames drawn as outlines on white.",
        when_to_use="Colour is the data (traffic classes, tenants, engine kinds) and the figure also has regions: the "
                    "transparent twin of multi-hue-categorical, so the categorical fills stay the only colour on the page.",
        exemplars=["asplos25-110_fig1", "asplos26-127_fig2", "asplos26-134_fig1", "nsdi26-084_figtex4"]),
    "pastel-regions": dict(
        id="pastel-regions", name="Each region its own pastel tint",
        description="Two to four regions (planes, hosts, phases) each filled with a different very light tint - cream, "
                    "pale green, pale blue, pink - with white or pale-blue boxes inside and a dark-gold or red accent. "
                    "`container`, `lane` and `legend` list the first three tints; `region_tints` has the full set.",
        when_to_use="Figures whose message is the split into regions (client / server, control / data plane, before / "
                    "after) when a legend for the regions should be avoided: the tint names the region.",
        exemplars=["nsdi26-144_fig1", "nsdi24-022_fig1", "nsdi26-124_fig1", "nsdi24-028_fig2"]),
    "blue-ground": dict(
        id="blue-ground", name="Pale-blue ground, warm boxes",
        description="A pale-blue container behind cream / orange component boxes (or pale-blue lanes behind white boxes), "
                    "dark outlines, a crimson or Office-blue accent.",
        when_to_use="One dominant region (a host, a chip, a runtime) that should read as a unit; the warm boxes pop "
                    "against the cool ground without any saturated fill.",
        exemplars=["asplos26-096_fig6", "nsdi24-064_fig3", "sosp25-002_fig1"]),
    "cream-ground": dict(
        id="cream-ground", name="Cream ground, blue boxes",
        description="A cream or peach container behind pale-blue component boxes, pale-green alternates and an amber "
                    "accent; warm-bands is the banded version of the same look.",
        when_to_use="Warm, print-friendly figures with one main region; the cool boxes separate cleanly from the warm "
                    "ground, and the amber accent stays in the same temperature.",
        exemplars=["asplos26-153_fig14", "asplos25-034_fig8", "sosp25-009_fig6"]),
    "green-ground": dict(
        id="green-ground", name="Pale-green ground, blue boxes",
        description="A pale-green container or band behind pale-blue boxes with cream alternates and an orange accent.",
        when_to_use="A quieter alternative to the blue ground when blue is already taken by the boxes; common for the "
                    "trusted / secure region (green = trusted) of a two-region figure.",
        exemplars=["nsdi26-087_fig3", "asplos25-097_fig2", "osdi25-017_fig7"]),
}


def ground_of(roles, depth, cand=None):
    g = roles.get("container") or roles.get("lane")
    if g is None:
        return ("outline-containers" if (depth or 0) >= 2 else "flat-on-canvas"), None
    # several region fills of different hues = each region carries its own pastel tint
    tints = {pc.hue_family(h) for r in ("container", "lane") for h in (cand or {}).get(r, [])
             if not pc.is_grey(h) and pc.hls(h)[1] <= 0.97}
    if len(tints) >= 2:
        return "multi-tint", g
    L = pc.hls(g)[1]
    if L > 0.97:
        return "white-container", g
    if pc.is_grey(g):
        return "grey-container", g
    return "tinted-" + pc.hue_family(g), g


def load_recs(semantics, index, subtype="architecture"):
    figs = [(rec, row) for rec, row in pc.load(semantics, index, subtype) if row["aesthetic"] == "good"]
    residue, multi, recs = [], [], []
    for rec, row in figs:
        fid, roles, extra, seen, fills, cand = pc.figure_roles(rec, row, residue, multi)
        depth = (rec.get("layout") or {}).get("nesting_depth")
        cls, ghex = ground_of(roles, depth, cand)
        tint_hexes = [h for r in ("container", "lane") for h in cand.get(r, []) if not pc.is_grey(h) and pc.hls(h)[1] <= 0.97]
        try:
            meas = json.loads(row["style"])
        except Exception:
            meas = {}
        recs.append(dict(
            id=fid, paper_id=rec["paper_id"], fig=str(rec["fig"]), ground=cls, ground_hex=ghex, depth=depth, tint_hexes=tint_hexes,
            roles=roles, extra_fills=extra, seen=seen, fills=fills, tool=row.get("tool"), venue=row.get("venue"),
            abstraction=(rec.get("system") or {}).get("abstraction"),
            template=(rec.get("layout") or {}).get("template"), fill_style=(rec.get("style") or {}).get("fill"),
            gray_frac=(meas.get("palette") or {}).get("gray_frac"),
            src_svgs=row.get("src_svgs"), pdf_svg=row.get("pdf_svg"),
            stroke_text=" ".join((p.get("used_for") or "") for p in (rec["style"].get("palette") or [])).lower()))
    return recs


def weighted_features(recs):
    from sklearn.preprocessing import StandardScaler
    X = np.array([pc.features(r["seen"], r["fills"], r["roles"]) for r in recs])
    Xs = StandardScaler().fit_transform(X)
    w = np.ones(Xs.shape[1])
    w[:9] = 0.7
    for f in pc.COARSE:
        w[pc.F[f"top1_{f}"]] = 2.4
        w[pc.F[f"top2_{f}"]] = 1.3
        w[pc.F[f"acc_{f}"]] = 0.9
    w[pc.F["grey_share"]] = 1.5
    w[pc.F["fill_L_mean"]] = 1.4
    w[pc.F["monochrome"]] = 1.5
    w[pc.F["n_hue_fams"]] = 1.2
    return X, Xs * w


def cluster(Xs, kmin, kmax, k_fixed, min_size, min_k, log):
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    sweep = []
    for k in range(kmin, min(kmax, len(Xs) - 1) + 1):
        lab = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Xs)
        sweep.append((k, float(silhouette_score(Xs, lab)), sorted(collections.Counter(lab).values(), reverse=True)))
        log.append(f"k={k}\tsilhouette={sweep[-1][1]:.4f}\tsizes={sweep[-1][2]}")
    k = k_fixed or max(sweep, key=lambda t: t[1])[0]
    labels = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Xs)
    while True:
        sizes = collections.Counter(labels)
        small = [c for c, n in sizes.items() if n < min_size]
        if not small or len(sizes) <= min_k:
            break
        c = min(small, key=lambda c: sizes[c])
        cent = {cc: Xs[labels == cc].mean(0) for cc in sizes}
        tgt = min((cc for cc in sizes if cc != c), key=lambda cc: float(np.linalg.norm(cent[cc] - cent[c])))
        log.append(f"merge cluster {c} (n={sizes[c]}) -> {tgt} (n={sizes[tgt]})")
        labels[labels == c] = tgt
    remap = {old: new for new, old in enumerate(sorted(set(labels)))}
    return np.array([remap[l] for l in labels]), sweep


def representative(members, recs, X, corpus_hex, transparent):
    """Per-role hex for one family: medoid value when usable, else the modal usable member value, else the
    cluster-wide modal usable colour, else the default -- as in palette_cluster.py, with the ground roles
    (container / lane) left null for the transparent families."""
    Xm = X[members]
    d = np.linalg.norm(Xm - Xm.mean(0), axis=1)
    medoid = recs[members[int(np.argmin(d))]]
    all_fills = collections.Counter(h for i in members for h in recs[i]["fills"])
    fam_cnt = collections.Counter(pc.coarse_family(h) for i in members for h in recs[i]["fills"])
    fam_rank = [f for f, _ in fam_cnt.most_common()]
    nongrey = [f for f in fam_rank if f != "grey"]
    rep, derived = {}, {}
    for role in ROLES:
        if role == "module-alt":
            continue
        if transparent and role in ("container", "lane"):
            vals = [recs[i]["roles"].get(role) for i in members]
            have = [v for v in vals if isinstance(v, str) and v]
            # a transparent family keeps lanes only when a clear minority of its members band the figure
            if role == "lane" and len(have) >= 0.4 * len(members):
                rep[role] = collections.Counter(have).most_common(1)[0][0]
                derived[role] = f"modal lane of the {len(have)} members that use bands"
            else:
                rep[role] = None
            continue
        ok = pc.ROLE_OK[role]
        vals = [recs[i]["roles"].get(role) for i in members]
        good = [v for v in vals if isinstance(v, str) and v and ok(v)]
        mv = medoid["roles"].get(role)
        if isinstance(mv, str) and mv and ok(mv) and not (
                role in ("stroke", "text") and good and min(pc.hls(h)[1] for h in good) < pc.hls(mv)[1] - 0.12):
            rep[role] = mv
        elif good:
            gc = collections.Counter(good)
            if role in ("stroke", "text"):
                rep[role] = min(gc, key=lambda h: (pc.hls(h)[1], -gc[h]))
            else:
                rep[role] = max(gc.items(), key=lambda kv: (kv[1], corpus_hex[kv[0]]))[0]
            derived[role] = "cluster-modal (medoid value unusable for this role)"
        else:
            pool = collections.Counter(h for i in members for h in recs[i]["seen"] if ok(h))
            if pool:
                rep[role] = max(pool.items(), key=lambda kv: (kv[1], corpus_hex[kv[0]]))[0]
                derived[role] = "cluster-wide modal (no member named this role)"
            else:
                rep[role] = pc.ROLE_DEFAULT[role]
                derived[role] = "default (role absent from the cluster)"
    mod_cnt = collections.Counter(h for h in (recs[i]["roles"].get("module") for i in members)
                                  if isinstance(h, str) and h and pc.ROLE_OK["module"](h))
    mod_fam = collections.Counter(pc.coarse_family(h) for h in mod_cnt.elements())
    fam0 = mod_fam.most_common(1)[0][0] if mod_fam else (nongrey[0] if nongrey else "grey")
    if mod_cnt:
        # the family's default box: the most common hex INSIDE the dominant module family (a draw.io default
        # lavender that repeats verbatim must not beat a warm family whose members vary their exact hex)
        rep["module"] = max(mod_cnt.items(), key=lambda kv: (mod_fam[pc.coarse_family(kv[0])], kv[1], pc.hls(kv[0])[1]))[0]
    acc_cnt = collections.Counter(h for h in (recs[i]["roles"].get("accent") for i in members)
                                  if isinstance(h, str) and h and pc.ROLE_OK["accent"](h))
    acc_fam = collections.Counter(pc.coarse_family(h) for h in acc_cnt.elements())
    afam0 = acc_fam.most_common(1)[0][0] if acc_fam else "warm"
    if acc_cnt:
        rep["accent"] = max(acc_cnt.items(), key=lambda kv: (kv[1], pc.coarse_family(kv[0]) == afam0, -pc.hls(kv[0])[1]))[0]
    dark_family = float(np.mean([X[i][pc.F["fill_L_mean"]] for i in members])) < 0.62
    alt_ok = pc.ROLE_OK["module"] if dark_family else (lambda h: pc.ROLE_OK["module"](h) and pc.hls(h)[1] >= 0.55)
    used = {rep.get("module"), rep.get("accent"), rep.get("container")}
    alts = []
    for fam in [f for f in nongrey if f != fam0] + ["grey"]:
        pool = [(h, n) for h, n in all_fills.most_common() if pc.coarse_family(h) == fam and alt_ok(h) and h not in used]
        if pool:
            alts.append(pool[0][0]); used.add(pool[0][0])
        if len(alts) >= 3:
            break
    rep["module-alt"] = alts[:3]
    extra = collections.Counter(h for i in members for h in recs[i]["extra_fills"])
    return rep, derived, medoid, fam_rank[:4], [h for h, _ in extra.most_common(6)], mod_fam, acc_fam


def png_of(r):
    cands = [pc.rel_png(r['paper_id'], x) for x in (r["src_svgs"] or "").split("|") if x]
    cands.append(pc.rel_png(r['paper_id'], r['pdf_svg'] or ''))
    return next((x for x in cands if os.path.exists(os.path.join(pc.REPO_ROOT, x))), cands[0])


def contrast_notes(rep, derived=None):
    notes = [v for k, v in (derived or {}).items() if "replaced by the neutral" in v]
    if rep["stroke"] and rep["module"] and pc.contrast(rep["stroke"], rep["module"]) < 3.0:
        notes.append(f"stroke on module is {pc.contrast(rep['stroke'], rep['module']):.1f}:1 - darken the outline to #404040 for small figures")
    for label, (fg, bg) in {"text on module": (rep["text"], rep["module"]), "text on accent": (rep["text"], rep["accent"]),
                            "text on container": (rep["text"], rep["container"])}.items():
        if fg and bg and isinstance(bg, str):
            cr = pc.contrast(fg, bg)
            if cr < 4.5:
                notes.append(f"{label} is {cr:.1f}:1 ({fg} on {bg}) - " + ("use #ffffff for labels inside that box" if pc.rel_lum(bg) < 0.4
                                                                            else "keep the label short and bold, or move it outside"))
    return "; ".join(notes) if notes else "every role pair clears 4.5:1 with the listed text colour"


def build_family(name_hint, members, recs, X, corpus_hex, transparent, n_all, ground_label, ground_hex=None):
    rep, derived, medoid, fams, extra, mod_fam, acc_fam = representative(members, recs, X, corpus_hex, transparent)
    if ground_hex:
        rep["container"] = ground_hex
    # a reusable palette keeps outlines, body text and plain arrows neutral: a family whose darkest recorded
    # value is a dark olive or navy (green-ground's text, for example) gets the corpus-wide neutral instead
    for role, dflt in (("text", "#1a1a1a"), ("stroke", "#404040"), ("arrow", "#404040")):
        h = rep.get(role)
        if h and pc.hls(h)[2] > 0.06:
            derived[role] = f"corpus value {h} is tinted (chroma {pc.hls(h)[2]:.2f}); replaced by the neutral {dflt}"
            rep[role] = dflt
    Xm = X[members]
    order = [members[i] for i in np.argsort(np.linalg.norm(Xm - Xm.mean(0), axis=1))]
    cands = []
    for i in order:
        r = recs[i]
        png = png_of(r)
        if os.path.exists(os.path.join(pc.REPO_ROOT, png)):
            cands.append(dict(id=r["id"], png=png, src_svg=png.replace(".png", ".svg"), tool=r["tool"], venue=r["venue"], in_cluster=True))
        if len(cands) >= 8:
            break
    stroke_kw = collections.Counter()
    for i in members:
        t = recs[i]["stroke_text"]
        for kw in ("dashed", "outline", "border", "rounded", "thin", "thick"):
            if kw in t:
                stroke_kw[kw] += 1
    return dict(
        key=name_hint, ground=ground_label, n=len(members), share=round(len(members) / n_all, 3),
        rep=rep, derived=derived, medoid=medoid["id"], families=fams, extra_fills=extra,
        module_families=dict(mod_fam.most_common()), accent_families=dict(acc_fam.most_common()),
        members=[recs[i]["id"] for i in members],
        tools=collections.Counter(recs[i]["tool"] for i in members).most_common(6),
        venues=collections.Counter(recs[i]["venue"] for i in members).most_common(6),
        abstractions=collections.Counter(recs[i]["abstraction"] for i in members).most_common(6),
        templates=collections.Counter(recs[i]["template"] for i in members).most_common(6),
        depth=collections.Counter(recs[i]["depth"] for i in members).most_common(4),
        stroke_keywords=dict(stroke_kw.most_common()),
        mean_gray=round(float(np.mean([recs[i]["gray_frac"] or 0 for i in members])), 3),
        pastel_share=round(float(np.mean([X[i][pc.F["pastel"]] for i in members])), 3),
        mono_share=round(float(np.mean([X[i][pc.F["monochrome"]] for i in members])), 3),
        candidates=cands)


def to_palette(c, cur):
    rep = {r: c["rep"].get(r) for r in ROLES}
    ex_ids = cur.get("exemplars") or [e["id"] for e in c["candidates"][:3]]
    by_id = {e["id"]: e for e in c["candidates"]}
    exemplars = [by_id[e] for e in ex_ids if e in by_id]
    return dict(
        id=cur["id"], name=cur["name"], description=cur.get("description", ""), when_to_use=cur.get("when_to_use", ""),
        ground=c["ground"], roles=rep, extra_fills=c["extra_fills"], contrast_notes=contrast_notes(rep, c["derived"]),
        stats=dict(n_figures=c["n"], share=c["share"], mean_grey_frac=c["mean_gray"], pastel_share=c["pastel_share"],
                   monochrome_share=c["mono_share"], hue_families=c["families"], tools=dict(c["tools"]),
                   venues=dict(c["venues"]), abstractions=dict(c["abstractions"]), templates=dict(c["templates"])),
        exemplars=exemplars, added="2026-09-18 ground extension (palette_grounds.py)",
        **({"region_tints": c["region_tints"]} if c.get("region_tints") else {}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--semantics", required=True); ap.add_argument("--index", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=0, help="transparent-set clusters before the small-cluster merge (0 = best silhouette in [4, 8])")
    ap.add_argument("--kmin", type=int, default=3); ap.add_argument("--kmax", type=int, default=9)
    ap.add_argument("--min-size", type=int, default=20)
    ap.add_argument("--min-tint", type=int, default=20, help="smallest tinted-ground family kept")
    ap.add_argument("--append-to", default=None, help="palettes.json to extend (existing entries untouched)")
    ap.add_argument("--subtype", default="architecture", help="diagram subtype (architecture or mechanism)")
    a = ap.parse_args()
    pc.set_extracted_dir(os.path.dirname(os.path.abspath(a.index)))
    os.makedirs(a.out, exist_ok=True)

    recs = load_recs(a.semantics, a.index, a.subtype)
    n_all = len(recs)
    ground_counts = collections.Counter(r["ground"] for r in recs)
    print(f"good architecture figures with records: {n_all}; ground classes: {ground_counts.most_common()}")
    with open(os.path.join(a.out, "figures_ground.json"), "w") as f:
        json.dump([{k: v for k, v in r.items() if k not in ("stroke_text",)} for r in recs], f, indent=0)
    corpus_hex = collections.Counter(h for r in recs for h in r["seen"])
    X, Xs = weighted_features(recs)
    log = []

    # transparent set: outline-only containers + no containers
    tr = [i for i, r in enumerate(recs) if r["ground"] in ("outline-containers", "flat-on-canvas") and r["fills"]]
    labels, sweep = cluster(Xs[tr], a.kmin, a.kmax, a.k or 0, a.min_size, 4, log)
    if not a.k:
        best = max((s for s in sweep if 4 <= s[0] <= 8), key=lambda t: t[1])
        log.append(f"chosen k={best[0]} (best silhouette in [4, 8])")
        labels, _ = cluster(Xs[tr], best[0], best[0], best[0], a.min_size, 4, log)
    fams = []
    for c in sorted(set(labels)):
        members = [tr[i] for i in range(len(tr)) if labels[i] == c]
        fams.append(build_family(f"transparent-{c}", members, recs, X, corpus_hex, True, n_all, "transparent"))

    # tinted set: by the ground's hue family (warm = orange + yellow; pink = red; green + teal together)
    def tint_group(r):
        if r["ground"] == "multi-tint":
            return "multi"
        fam = r["ground"].split("-", 1)[1]
        return "warm" if fam in WARM else ("green" if fam in ("green", "teal") else fam)
    groups = collections.defaultdict(list)
    for i, r in enumerate(recs):
        if (r["ground"].startswith("tinted-") or r["ground"] == "multi-tint") and r["fills"]:
            groups[tint_group(r)].append(i)
    for g, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if len(members) < a.min_tint:
            log.append(f"tinted ground {g}: only {len(members)} figures, skipped")
            continue
        if g == "multi":
            # the modal tint per hue family, lightest first: the palette lists them as container + lane + legend
            fam_hex = collections.defaultdict(collections.Counter)
            for i in members:
                for h in recs[i]["tint_hexes"]:
                    fam_hex[pc.coarse_family(h)][h] += 1
            ranked = sorted(fam_hex, key=lambda f: -sum(fam_hex[f].values()))
            tints = [fam_hex[f].most_common(1)[0][0] for f in ranked]
            fam = build_family("tinted-multi", members, recs, X, corpus_hex, False, n_all, "multi-tint", tints[0] if tints else None)
            if len(tints) > 1:
                fam["rep"]["lane"] = tints[1]
            if len(tints) > 2:
                fam["rep"]["legend"] = tints[2]
            fam["region_tints"] = tints[:5]
            fams.append(fam)
            continue
        ghex = collections.Counter(recs[i]["ground_hex"] for i in members).most_common(1)[0][0]
        fams.append(build_family(f"tinted-{g}", members, recs, X, corpus_hex, False, n_all, f"tinted-{g}", ghex))

    # curation match by exemplar overlap
    taken = set()
    for c in sorted(fams, key=lambda c: -c["n"]):
        best, score = None, 0
        for key, cur in CURATION.items():
            if key in taken:
                continue
            s = sum(1 for e in cur["exemplars"] if e in set(c["members"]))
            if s > score:
                best, score = key, s
        c["curation"] = best
        if best:
            taken.add(best)
    with open(os.path.join(a.out, "clusters.json"), "w") as f:
        json.dump(dict(log=log, families=fams), f, indent=1)

    pals = [to_palette(c, CURATION.get(c["curation"]) or dict(id=c["key"], name=c["key"])) for c in fams]
    with open(os.path.join(a.out, "candidates.json"), "w") as f:
        json.dump(pals, f, indent=1)
    md = [f"# Ground palettes -- {n_all} good architecture figures", "", "Ground classes: " +
          ", ".join(f"{k} {v}" for k, v in ground_counts.most_common()), "", "```", *log, "```", ""]
    for c, p in zip(fams, pals):
        md += [f"## {p['id']}  ({c['ground']}, n={c['n']}, {c['share']*100:.1f}%)  curated: {c['curation'] or 'NO'}", "",
               "roles: " + ", ".join(f"{r}={c['rep'].get(r)}" for r in ROLES), "",
               f"module families {c['module_families']}; accent families {c['accent_families']}; hue rank {c['families']}",
               f"nesting depth {c['depth']}; stroke keywords {c['stroke_keywords']}; tools {c['tools'][:4]}; templates {c['templates'][:4]}",
               f"derived: {c['derived']}", "", "candidates (nearest the centre first):"]
        md += [f"- {e['id']}  {e['png']}" for e in c["candidates"]]
        md.append("")
    with open(os.path.join(a.out, "report.md"), "w") as f:
        f.write("\n".join(md))
    print("families:", [(p["id"], c["n"]) for c, p in zip(fams, pals)])
    print("wrote", a.out)

    if a.append_to:
        doc = json.load(open(a.append_to))
        have = {p["id"] for p in doc["palettes"]}
        added = [p for p in pals if p["id"] not in have and not p["id"].startswith(("transparent-", "tinted-"))]
        doc["palettes"].extend(added)
        doc.setdefault("general_rules", {})["ground"] = dict(
            figures=n_all, classes=dict(ground_counts.most_common()),
            note=("How the outer group boxes are filled in the good architecture figures with semantic records: "
                  "outline-containers = nesting >= 2 but no container/lane fill (bare outlines, often dashed); "
                  "flat-on-canvas = no containers at all; the rest by the container fill. Grey grounds are a minority."))
        doc["provenance"]["ground_extension"] = dict(
            figures=n_all, added=[p["id"] for p in added], generator="figgenie-paper-diagram/scripts/distill/palette_grounds.py", date="2026-09-18")
        with open(a.append_to, "w") as f:
            json.dump(doc, f, indent=1)
        print(f"appended {len(added)} palettes to {a.append_to}: {[p['id'] for p in added]}"
              + ("" if len(added) == len(pals) else f" (uncurated or already present, skipped: {[p['id'] for p in pals if p not in added]})"))


if __name__ == "__main__":
    main()
