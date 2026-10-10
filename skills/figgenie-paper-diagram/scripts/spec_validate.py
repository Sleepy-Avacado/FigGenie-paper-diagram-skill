#!/usr/bin/env python3
"""Validate a figure spec against references/spec-schema.json.

Three passes:
  1. schema      -- JSON Schema (draft 2020-12) via `jsonschema` if importable,
                    otherwise a built-in subset checker (type/enum/required/
                    properties/items/$ref/pattern/min-max/minLength/minItems/
                    additionalProperties).
  2. references  -- what JSON Schema cannot express: unique ids across every
                    element array, dangling from/to/parent/attached_to/anchor/
                    legend_ref/targets, container cycles, edge endpoints on
                    containers or lanes (a warning: the linter checks the arrow
                    against the frame), a node used as a parent, steps without
                    a target, palette
                    and template ids that exist, bitmap files (nodes[].image.src:
                    a URL is an error -- a figure never depends on a remote
                    file; a missing file or a format other than PNG / JPEG is
                    a warning).
  3. style       -- warnings against the measured bands in style-rules.md,
                    layouts.md, encoding.md and anti-patterns.md.

Errors exit 1; warnings exit 0 (use --strict to fail on warnings too).

Usage:
  python3 scripts/spec_validate.py spec.json
  python3 scripts/spec_validate.py spec.json --palettes references/palettes.json \
                                             --schema   references/spec-schema.json
  python3 scripts/spec_validate.py spec.json --strict --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_SCHEMA = os.path.join(ROOT, "references", "spec-schema.json")
DEFAULT_PALETTES = os.path.join(ROOT, "references", "palettes.json")

TEMPLATES = [
    "pipeline", "layered", "two-panel", "control-data", "hub-spoke", "matrix",
    "host-device", "overview-with-inset", "control-loop", "phase-lanes",
    "multi-tier", "nested-stack", "baseline-vs-ours", "replicated-grid",
    "dataflow-dag", "n-panel-comparison", "composite-figure", "mirrored-pair",
    "flanked-core", "block-floorplan",
]

# ---------------------------------------------------------------- measured bands
# layouts.md "Canvas and typography" + style-rules.md figure size table / SS9.
AREA_PT2_PER_BOX = 3400          # ~1 labelled box per 3,400 pt^2 of canvas (727-figure corpus, 2026-09-07)
BOX_Q3 = {"single": 14, "double": 21}    # corpus q3 = 14 components (all columns)
BOX_P90 = {"single": 19, "double": 27}   # corpus p90 = 19 components
BOX_MIN = 6                      # style-rules SS9: don't ship < ~5-6 labelled boxes
EDGE_MAX = {"single": 11, "double": 23}  # flows p90 = 11, max observed 23
# meta.kind = mechanism: elements are counted per template panel, so a mechanism figure carries fewer
# labelled boxes than an overview. Bands from the 152 mechanism semantic records of the exemplar
# candidates (2026-09-20; 128 single / 24 double): elements q3 12 / 15, p90 14 / 17, q1 7 / 10;
# relations p90 11 / 12 (scripts/distill/mech_semantics_stats.py).
MECH_BOX_Q3 = {"single": 12, "double": 15}
MECH_BOX_P90 = {"single": 14, "double": 17}
MECH_EDGE_MAX = {"single": 11, "double": 12}
MECH_BOX_MIN = 5
MECH_GROUPS = ("comparison", "evolution", "logic", "walkthrough", "anatomy")
ACCENT_MAX = 2                   # palettes.json general_rules.saturated_fills
STEP_MAX = 8                     # encoding.md Part D: 3-8 steps
LANES_MAX_SINGLE = 3             # layouts.md phase-lanes
NESTING_WARN, NESTING_ERROR = 3, 4        # anti-patterns SS3 #20
WIDTH_BAND = {"single": (210, 309), "double": (430, 603)}   # p5-p95
HEIGHT_MAX = {"single": 257, "double": 313}                 # p95
ASPECT_BAND = (1.0, 4.0)         # anti-patterns SS3 #21
STROKE_BAND = (0.20, 1.35)       # style-rules SS3 p5-p95
FONT_FLOOR = 6.0                 # anti-patterns SS3 #1: warn below 6pt
FONT_CEIL = 10.0                 # anti-patterns SS3 #23
ENCODINGS_NEEDING_LEGEND = 4     # encoding.md Part C: "more than 4 semantic fills"


class Report:
    def __init__(self):
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.infos: list[tuple[str, str]] = []

    def error(self, where, msg):
        self.errors.append((where, msg))

    def warn(self, where, msg):
        self.warnings.append((where, msg))

    def info(self, where, msg):
        self.infos.append((where, msg))


# ------------------------------------------------------------------ schema pass
def _subset_check(node, schema, path, defs, rep):
    """Minimal JSON Schema subset checker used when `jsonschema` is missing."""
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref.startswith("#/$defs/"):
            merged = dict(defs.get(ref.split("/")[-1], {}))
            merged.update({k: v for k, v in schema.items() if k != "$ref"})
            schema = merged
    types = schema.get("type")
    if types is not None:
        types = [types] if isinstance(types, str) else list(types)
        ok = False
        for t in types:
            if t == "object":
                ok = ok or isinstance(node, dict)
            elif t == "array":
                ok = ok or isinstance(node, list)
            elif t == "string":
                ok = ok or isinstance(node, str)
            elif t == "integer":
                ok = ok or (isinstance(node, int) and not isinstance(node, bool))
            elif t == "number":
                ok = ok or (isinstance(node, (int, float)) and not isinstance(node, bool))
            elif t == "boolean":
                ok = ok or isinstance(node, bool)
            elif t == "null":
                ok = ok or node is None
        if not ok:
            rep.error(path, "expected type %s, got %s" % ("/".join(types), type(node).__name__))
            return
    if "enum" in schema and node not in schema["enum"]:
        rep.error(path, "%r is not one of %s" % (node, schema["enum"]))
        return
    if isinstance(node, str):
        if "pattern" in schema and not re.match(schema["pattern"], node):
            rep.error(path, "%r does not match %s" % (node, schema["pattern"]))
        if "minLength" in schema and len(node) < schema["minLength"]:
            rep.error(path, "must not be empty")
    if isinstance(node, (int, float)) and not isinstance(node, bool):
        if "minimum" in schema and node < schema["minimum"]:
            rep.error(path, "%s < minimum %s" % (node, schema["minimum"]))
        if "maximum" in schema and node > schema["maximum"]:
            rep.error(path, "%s > maximum %s" % (node, schema["maximum"]))
    if isinstance(node, dict):
        for key in schema.get("required", []):
            if key not in node:
                rep.error(path, "missing required property %r" % key)
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            pats = list(schema.get("patternProperties", {}).keys())
            for key in node:
                if key not in props and not any(re.match(pt, key) for pt in pats):
                    rep.error(path, "unknown property %r (the schema is closed; use notes or an x-/_ prefixed field)" % key)
        for key, sub in props.items():
            if key in node:
                _subset_check(node[key], sub, "%s.%s" % (path, key), defs, rep)
    if isinstance(node, list):
        if "minItems" in schema and len(node) < schema["minItems"]:
            rep.error(path, "needs at least %d item(s)" % schema["minItems"])
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(node):
                _subset_check(item, item_schema, "%s[%d]" % (path, i), defs, rep)


def schema_pass(spec, schema, rep):
    try:
        import jsonschema  # noqa
    except ImportError:
        rep.info("schema", "`jsonschema` not importable -- using the built-in subset checker")
        _subset_check(spec, schema, "$", schema.get("$defs", {}), rep)
        return
    import jsonschema
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(spec), key=lambda e: list(e.path)):
        where = "$" + "".join(
            "[%d]" % p if isinstance(p, int) else ".%s" % p for p in err.path
        )
        rep.error(where, err.message)


# -------------------------------------------------------------- reference pass
def collect(spec):
    """id -> ('node'|'container'|'lane'|'edge'|'annotation'|'panel'|'delta'|'value'|'legend-item', obj)"""
    kinds = {}
    for group, kind in (("containers", "container"), ("lanes", "lane"),
                        ("nodes", "node"), ("edges", "edge"),
                        ("annotations", "annotation"), ("panels", "panel"),
                        ("deltas", "delta"), ("values", "value")):
        for obj in spec.get(group) or []:
            if isinstance(obj, dict) and isinstance(obj.get("id"), str):
                kinds.setdefault(obj["id"], []).append((kind, obj))
    for obj in ((spec.get("legend") or {}).get("items") or []):
        if isinstance(obj, dict) and isinstance(obj.get("id"), str):
            kinds.setdefault(obj["id"], []).append(("legend-item", obj))
    return kinds


def reference_pass(spec, palettes, rep, base_dir=None):
    ids = collect(spec)
    for _id, entries in sorted(ids.items()):
        if len(entries) > 1:
            rep.error("ids", "%r is declared %d times (%s) -- ids must be unique "
                             "across every element array"
                      % (_id, len(entries), ", ".join(k for k, _ in entries)))
    kind_of = {k: v[0][0] for k, v in ids.items()}

    def resolve(where, ref, want, optional_msg=""):
        if ref in (None, ""):
            return None
        if ref not in kind_of:
            rep.error(where, "%r does not name anything in this spec%s" % (ref, optional_msg))
            return None
        if want and kind_of[ref] not in want:
            rep.error(where, "%r is a %s; expected %s"
                      % (ref, kind_of[ref], " or ".join(want)))
            return None
        return kind_of[ref]

    # parents
    for i, c in enumerate(spec.get("containers") or []):
        if not isinstance(c, dict):
            continue
        if c.get("parent") == c.get("id"):
            rep.error("containers[%d].parent" % i, "a container cannot be its own parent")
        elif kind_of.get(c.get("parent")) == "node":
            rep.error("containers[%d].parent" % i,
                      "%r is a node; a node cannot hold other boxes -- declare %r as a container "
                      "(a container may be an edge endpoint, so nothing is lost)" % (c["parent"], c["parent"]))
        else:
            resolve("containers[%d].parent" % i, c.get("parent"), ("container", "lane"))
    for i, n in enumerate(spec.get("nodes") or []):
        if not isinstance(n, dict):
            continue
        if kind_of.get(n.get("parent")) == "node":
            rep.error("nodes[%d].parent" % i,
                      "%r is a node; a node cannot hold other boxes -- declare %r as a container "
                      "(a container may be an edge endpoint, so nothing is lost)" % (n["parent"], n["parent"]))
        else:
            resolve("nodes[%d].parent" % i, n.get("parent"), ("container", "lane"))
        resolve("nodes[%d].legend_ref" % i, n.get("legend_ref"), ("legend-item",))

    # container / lane cycles
    parent = {}
    for c in spec.get("containers") or []:
        if isinstance(c, dict) and c.get("parent"):
            parent[c.get("id")] = c["parent"]
    reported = set()
    for start in list(parent):
        seen, cur = [start], parent.get(start)
        while cur in parent:
            if cur in seen:
                key = frozenset(seen[seen.index(cur):])
                if key not in reported:
                    reported.add(key)
                    rep.error("containers", "container cycle: %s"
                              % " -> ".join(seen[seen.index(cur):] + [cur]))
                break
            seen.append(cur)
            cur = parent[cur]

    # edges
    for i, e in enumerate(spec.get("edges") or []):
        if not isinstance(e, dict):
            continue
        for side in ("from", "to"):
            ref = e.get(side)
            if ref in (None, ""):
                continue
            if ref not in kind_of:
                rep.error("edges[%d].%s" % (i, side), "%r does not name anything in this spec" % ref)
            elif kind_of[ref] in ("container", "lane"):
                rep.warn("edges[%d].%s" % (i, side),
                         "%r is a %s; allowed -- the linter checks the arrow against its frame. When the "
                         "prose names a specific box inside it, prefer that node as the endpoint"
                         % (ref, kind_of[ref]))
            elif kind_of[ref] != "node":
                rep.error("edges[%d].%s" % (i, side),
                          "%r is a %s; edge endpoints must be nodes, containers or lanes" % (ref, kind_of[ref]))
        resolve("edges[%d].legend_ref" % i, e.get("legend_ref"), ("legend-item",))

    # steps
    seen_n = {}
    for i, s in enumerate(spec.get("steps") or []):
        if not isinstance(s, dict):
            continue
        resolve("steps[%d].attached_to" % i, s.get("attached_to"), ("edge", "node"),
                " -- every step needs a target edge or node to sit on")
        n = s.get("n")
        if n in seen_n:
            rep.error("steps[%d].n" % i, "step %r is declared twice" % n)
        seen_n[n] = i

    # annotations / constraints
    for i, a in enumerate(spec.get("annotations") or []):
        if isinstance(a, dict):
            resolve("annotations[%d].anchor" % i, a.get("anchor"),
                    ("node", "edge", "container", "lane", "panel"))
            resolve("annotations[%d].legend_ref" % i, a.get("legend_ref"), ("legend-item",))
    for i, c in enumerate(spec.get("constraints") or []):
        if isinstance(c, dict):
            for j, t in enumerate(c.get("targets") or []):
                resolve("constraints[%d].targets[%d]" % (i, j), t, ("node", "container", "lane"))

    # mechanism kind: panel membership, panels[], deltas[], values[]
    for group in ("containers", "lanes", "nodes", "edges", "annotations", "steps"):
        for i, obj in enumerate(spec.get(group) or []):
            if isinstance(obj, dict) and obj.get("panel"):
                resolve("%s[%d].panel" % (group, i), obj.get("panel"), ("panel",),
                        " -- declare the panel in panels[]")
    parent_of = {q.get("id"): q.get("parent") for q in (spec.get("panels") or []) if isinstance(q, dict)}
    for i, pnl in enumerate(spec.get("panels") or []):
        if not isinstance(pnl, dict):
            continue
        if pnl.get("template_of") == pnl.get("id"):
            rep.error("panels[%d].template_of" % i, "a panel cannot be its own template")
        else:
            resolve("panels[%d].template_of" % i, pnl.get("template_of"), ("panel",))
        if pnl.get("parent"):
            seen, q = {pnl.get("id")}, pnl.get("parent")
            while q and q not in seen and q in parent_of:
                seen.add(q); q = parent_of[q]
            if pnl.get("parent") == pnl.get("id") or (q and q in seen):
                rep.error("panels[%d].parent" % i, "panel %r sits in itself (parent chain loops)" % pnl.get("id"))
            else:
                resolve("panels[%d].parent" % i, pnl.get("parent"), ("panel",))
        if pnl.get("view") and pnl.get("axis", "alternatives") != "part":
            rep.info("panels[%d].view" % i, "view describes a part of a composite figure (axis part); %r is a %s panel"
                     % (pnl.get("id"), pnl.get("axis", "alternatives")))
    for i, dl in enumerate(spec.get("deltas") or []):
        if not isinstance(dl, dict):
            continue
        resolve("deltas[%d].panel" % i, dl.get("panel"), ("panel",))
        resolve("deltas[%d].target" % i, dl.get("target"),
                ("node", "edge", "container", "annotation", "value"))
    for i, v in enumerate(spec.get("values") or []):
        if not isinstance(v, dict):
            continue
        resolve("values[%d].at" % i, v.get("at"), ("node", "edge"))
        resolve("values[%d].panel" % i, v.get("panel"), ("panel",))
        for j, l in enumerate(v.get("links") or []):
            resolve("values[%d].links[%d]" % (i, j), l, ("value",))

    # bitmaps: nodes[].image.src is a local PNG / JPEG next to the spec (embed_fonts.py inlines it at delivery)
    for i, n in enumerate(spec.get("nodes") or []):
        if not isinstance(n, dict):
            continue
        img = n.get("image") if isinstance(n.get("image"), dict) else None
        if n.get("kind") == "image" and not img:
            rep.warn("nodes[%d].image" % i, "kind 'image' but no image.src -- name the PNG / JPEG file the node shows")
        src = (img or {}).get("src")
        if not isinstance(src, str) or not src.strip():
            continue
        src, where = src.strip(), "nodes[%d].image.src" % i
        if src[:5].lower() == "data:":
            rep.warn(where, "a data URI in the spec -- keep the bitmap as a file next to the spec and give its path")
            continue
        if re.match(r"(?:[A-Za-z][A-Za-z0-9+.-]+:|//)", src) and src[:5].lower() != "file:":
            rep.error(where, "%r is a link: a figure never depends on a remote file -- download it into the figure "
                             "folder (check its licence) and give the relative path; embed_fonts.py inlines it at "
                             "delivery" % src[:80])
            continue
        if not re.search(r"\.(png|jpe?g)$", src, re.I):
            rep.warn(where, "%r: bitmaps are PNG (screenshots, renders, icons) or JPEG (photos) -- convert it; the "
                            "linter rejects other formats" % src)
        if base_dir is not None:
            path = src[7:] if src[:7].lower() == "file://" else src
            path = path if os.path.isabs(path) else os.path.join(base_dir, path)
            if not os.path.isfile(path):
                rep.warn(where, "%r not found next to the spec (looked for %s); the linter fails on a missing "
                                "bitmap" % (src, path))

    # palette + template
    meta = spec.get("meta") or {}
    pal = meta.get("palette", "blue-orange")
    known = {p.get("id") for p in (palettes.get("palettes") or [])} if palettes else set()
    if pal == "custom":
        roles = ((spec.get("style_overrides") or {}).get("palette_roles") or {})
        missing = [r for r in ("module", "stroke", "text") if not roles.get(r)]
        if missing:
            rep.error("meta.palette",
                      "palette 'custom' needs style_overrides.palette_roles for %s"
                      % ", ".join(missing))
    elif known and pal not in known:
        rep.error("meta.palette", "%r is not a palette id in palettes.json (%s)"
                  % (pal, ", ".join(sorted(known))))
    style = meta.get("style", "corpus")
    if style != "corpus":                       # named style: references/styles/<style>.md + .json
        sp = os.path.join(ROOT, "references", "styles", "%s.json" % style)
        if not os.path.exists(sp):
            rep.error("meta.style", "%r has no references/styles/%s.json" % (style, style))
        else:
            sj = json.load(open(sp, encoding="utf-8"))
            if pal not in (sj.get("palette"), "custom"):
                rep.warn("meta.palette", "style %r is drawn with palette %r (or 'custom'); %r loses the style's "
                                         "identity fills" % (style, sj.get("palette"), pal))
            if sj.get("font") and meta.get("font", "arial") != sj["font"]:
                rep.warn("meta.font", "style %r uses font %r (bold); %r changes its look"
                         % (style, sj["font"], meta.get("font", "arial")))
    elif pal in {p.get("id") for p in (palettes.get("palettes") or []) if p.get("style")} if palettes else False:
        rep.warn("meta.palette", "palette %r belongs to a named style; set meta.style = %r to get its rules "
                                 "(references/styles/%s.md)" % (pal, pal, pal))
    if meta.get("template") and meta["template"] not in TEMPLATES and meta["template"] != "mechanism":
        rep.error("meta.template", "%r is not one of the 15 template ids in layouts.md" % meta["template"])
    if meta.get("template") == "mechanism" and meta.get("kind", "architecture") != "mechanism":
        rep.error("meta.template", "template 'mechanism' needs meta.kind = 'mechanism'")
    for m in meta.get("modifiers") or []:
        if m not in TEMPLATES:
            rep.error("meta.modifiers", "%r is not a template id in layouts.md" % m)

    # legend
    legend = spec.get("legend") or {}
    if legend.get("mode") == "explicit" and not legend.get("items"):
        rep.error("legend.items", "legend.mode is 'explicit' but no items are declared")
    return ids, kind_of


# ------------------------------------------------------------------ style pass
def nesting_depth(spec):
    parent = {}
    for c in spec.get("containers") or []:
        if isinstance(c, dict):
            parent[c.get("id")] = c.get("parent")
    for l in spec.get("lanes") or []:
        if isinstance(l, dict):
            parent.setdefault(l.get("id"), None)

    def depth_of(cid, chain=()):
        # cycle-safe: a parent cycle is reported by the reference pass, and must
        # not also show up here as a bogus depth.
        if not cid or cid not in parent or cid in chain:
            return 0
        return 1 + depth_of(parent.get(cid), chain + (cid,))

    deepest = 0
    for n in spec.get("nodes") or []:
        if isinstance(n, dict):
            deepest = max(deepest, 1 + depth_of(n.get("parent")))
    for c in spec.get("containers") or []:
        if isinstance(c, dict):
            deepest = max(deepest, depth_of(c.get("id")))
    return deepest


def distinct_encodings(spec):
    """Proxy for encoding.md Part C.

    Part C requires a legend for "more than 4 semantic fills, or any fill whose
    meaning is not written inside the box", for any meaningful line style or
    arrow colour, and for any non-universal glyph.  So an element that carries
    its own label decodes itself and does not count: only *unlabelled* edges and
    *unlabelled* glyphs are counted, alongside the distinct box fills.
    """
    enc = set()
    for n in spec.get("nodes") or []:
        if not isinstance(n, dict):
            continue
        enc.add(("fill", n.get("role", "existing"), n.get("emphasis", "none")))
        if n.get("symbol") and not (n.get("label") or "").strip():
            enc.add(("glyph", n["symbol"]))
    for e in spec.get("edges") or []:
        if not isinstance(e, dict):
            continue
        if not (e.get("label") or "").strip():
            enc.add(("line", e.get("kind", "data"), e.get("style", "solid")))
    for c in spec.get("containers") or []:
        if isinstance(c, dict) and c.get("kind") in ("band", "lane"):
            enc.add(("band", c.get("role", "existing")))
    return enc


def style_pass(spec, rep):
    meta = spec.get("meta") or {}
    col = meta.get("column", "single")
    col = col if col in ("single", "double") else "single"
    width = float(meta.get("width_pt", 240 if col == "single" else 504))
    height = float(meta.get("max_height_pt", 160))
    nodes = [n for n in (spec.get("nodes") or []) if isinstance(n, dict)]
    containers = [c for c in (spec.get("containers") or []) if isinstance(c, dict)]
    lanes = [l for l in (spec.get("lanes") or []) if isinstance(l, dict)]
    edges = [e for e in (spec.get("edges") or []) if isinstance(e, dict)]
    steps = [s for s in (spec.get("steps") or []) if isinstance(s, dict)]
    legend = spec.get("legend") or {}
    label_of = {n.get("id"): (n.get("label") or n.get("id")) for n in nodes}
    mech = meta.get("kind", "architecture") == "mechanism"

    # --- canvas -------------------------------------------------------------
    lo, hi = WIDTH_BAND[col]
    if not lo <= width <= hi:
        rep.warn("meta.width_pt", "%.0f pt is outside the %s-column band %d-%d pt "
                                 "(target %d)" % (width, col, lo, hi, 240 if col == "single" else 504))
    if height > HEIGHT_MAX[col]:
        rep.warn("meta.max_height_pt", "%.0f pt is above the %s-column p95 of %d pt"
                 % (height, col, HEIGHT_MAX[col]))
    aspect = width / height if height else 0
    if aspect and not ASPECT_BAND[0] <= aspect <= ASPECT_BAND[1]:
        rep.warn("meta", "aspect %.2f (width/max_height) is outside %.1f-%.1f; a figure this "
                         "%s is a recorded weakness"
                 % (aspect, ASPECT_BAND[0], ASPECT_BAND[1],
                    "tall" if aspect < 1 else "wide"))
    if meta.get("direction") == "bottom-up":
        rep.warn("meta.direction", "bottom-up appears 13/727 times in the corpus -- use it only "
                                   "for a memory hierarchy read from the device outward")
    if col == "double" and meta.get("template") == "layered":
        rep.warn("meta.template", "only 5% of layered figures are double column; a layered "
                                  "figure that will not fit at 240 pt should get taller, not wider")
    all_panels = [q for q in (spec.get("panels") or []) if isinstance(q, dict)]
    parts = [q for q in all_panels if q.get("axis") == "part"]
    if int(meta.get("panels", 1) or 1) >= 3:
        if parts:
            rep.info("meta.panels", "composite figure with %d parts (%s): each part is budgeted on its own, and the "
                                    "reader needs a shared legend, one numbering and the same identity colours in every "
                                    "part (spec-guide §8)" % (len(parts), ", ".join(str(q.get("id")) for q in parts)))
        else:
            rep.warn("meta.panels", "%s panels -- 'too many panels' is a recorded weakness; consider a chained "
                                    "drill-down, or, when the user wants one overview figure, declare the panels as the "
                                    "parts of a composite figure (panels[] axis 'part', spec-guide §8)" % meta.get("panels"))

    # --- density ------------------------------------------------------------
    box_q3, box_p90, edge_max, box_min = ((MECH_BOX_Q3, MECH_BOX_P90, MECH_EDGE_MAX, MECH_BOX_MIN) if mech
                                          else (BOX_Q3, BOX_P90, EDGE_MAX, BOX_MIN))
    if mech:
        # the mechanism semantic records count the elements of ONE panel by their label: mirrored devices,
        # repeated slots and per-panel copies count once, as they do in the corpus bands; borderless
        # `note` nodes are text, not boxes
        boxes = len({(n.get("label") or "").strip().lower() or "<%s>" % n.get("kind", "module")
                     for n in nodes if n.get("kind") != "note"}) \
            + len({c.get("label") or c.get("id") for c in containers}) + len(lanes)
        n_edges = len({(label_of.get(e.get("from"), e.get("from")), label_of.get(e.get("to"), e.get("to")),
                        e.get("kind", "data")) for e in edges})
    else:
        boxes = len(nodes) + len(containers) + len(lanes)
        n_edges = len(edges)
    budget = max(1, round(width * height / AREA_PT2_PER_BOX))
    if parts:
        # composite: several small figures in one frame -- hold each part to the single-column bands
        pid_parent = {q.get("id"): q.get("parent") for q in all_panels}
        def top(pid):
            seen = set()
            while pid and pid_parent.get(pid) and pid not in seen:
                seen.add(pid); pid = pid_parent[pid]
            return pid
        per = {}
        for n in nodes:
            if n.get("kind") == "note": continue
            key = ((n.get("label") or "").strip().lower() or n.get("id")) if mech else n.get("id")
            per.setdefault(top(n.get("panel")) or "(shared)", set()).add(key)
        for c in containers:
            if c.get("kind") != "panel":
                per.setdefault(top(c.get("panel")) or "(shared)", set()).add("c:" + str(c.get("label") or c.get("id")))
        for part, keys in sorted(per.items()):
            if len(keys) > box_p90["single"]:
                rep.warn("nodes", "part %s has %d labelled boxes, above the single-column p90 of %d that each part of a "
                                  "composite figure gets -- draw identical rows once (one tall box across the lanes), use "
                                  "xN, or move numbers into a values part or the caption (spec-guide §8)"
                         % (part, len(keys), box_p90["single"]))
        rep.info("nodes", "composite figure: %s labelled boxes per part" %
                 ", ".join("%s %d" % (k, len(v)) for k, v in sorted(per.items())))
    elif boxes > box_p90[col]:
        rep.warn("nodes", "%d labelled boxes (nodes+containers+lanes) exceeds the corpus p90 of "
                          "%d for %s column -- split the figure or nest sub-modules"
                 % (boxes, box_p90[col], col))
    elif boxes > box_q3[col]:
        rep.warn("nodes", "%d labelled boxes is above the corpus q3 of %d; check it still "
                          "reads at print size" % (boxes, box_q3[col]))
    if boxes > budget * 1.4 and not parts:
        rep.warn("nodes", "%d labelled boxes on a %.0fx%.0f pt canvas -- the area budget is "
                          "~%d boxes (1 per %d pt^2). Grow the canvas or merge components."
                 % (boxes, width, height, budget, AREA_PT2_PER_BOX))
    if boxes < box_min:
        rep.warn("nodes", "only %d labelled boxes; good figures carry >= %d (q1) and bad ones "
                          "median 6 -- add the components you elided, or say why it is this simple"
                 % (boxes, 7 if mech else 11))
    if n_edges > edge_max[col]:
        rep.warn("edges", "%d flows exceeds the corpus p90 of %d -- drop the edges that are not "
                          "load-bearing" % (n_edges, edge_max[col]))
    for i, n in enumerate(nodes):
        if not (n.get("label") or "").strip() and n.get("kind") not in ("port", "icon", "image"):
            rep.error("nodes[%d].label" % i, "empty label on a %r node -- only port / icon / image nodes may be unlabelled"
                      % n.get("kind", "module"))
    if mech:
        mechanism_pass(spec, rep)
    elif (spec.get("panels") and not parts) or spec.get("deltas") or meta.get("mechanism") or \
            (spec.get("values") and not parts):
        rep.warn("meta.kind", "panels[] / deltas[] / values[] / meta.mechanism are mechanism-figure "
                              "fields; set meta.kind = 'mechanism' or drop them (a composite figure of parts, "
                              "panels[] with axis 'part', may keep them in either kind)")

    depth = nesting_depth(spec)
    if depth > NESTING_ERROR:
        rep.error("containers", "nesting depth %d; the corpus stops at 4 and 61%% stop at 2" % depth)
    elif depth > NESTING_WARN:
        rep.warn("containers", "nesting depth %d -- shrink to <= 3 or split into drill-down "
                               "panels" % depth)

    # --- emphasis / colour --------------------------------------------------
    accents = [n["id"] for n in nodes if n.get("emphasis") == "accent"]
    if mech:
        # the ceiling is on saturated FILLS: four identical accent bars are one fill
        seen_acc = {}
        for n in nodes:
            if n.get("emphasis") == "accent":
                seen_acc.setdefault(((n.get("label") or "").strip().lower(), n.get("kind", "module")), n["id"])
        accents = list(seen_acc.values())
    if len(accents) > ACCENT_MAX:
        rep.warn("nodes[].emphasis", "%d accent nodes (%s); the ceiling is %d saturated fills "
                                     "per figure -- use role='novel' for the rest and let the "
                                     "module fill carry it"
                 % (len(accents), ", ".join(accents[:6]), ACCENT_MAX))
    main = [e["id"] for e in edges if e.get("weight") == "main"]
    if len(main) > 6:
        rep.warn("edges[].weight", "%d edges marked 'main'; the main path should be one "
                                   "contiguous chain" % len(main))
    if any(c.get("kind") == "dashed" for c in containers) and \
       any(e.get("style") == "dashed" for e in edges):
        rep.warn("style", "dashed is doing two jobs (group boundary AND edge style). Pick one "
                          "meaning per figure -- make the control edges dotted, or the group solid.")

    labels = {}
    for n in nodes:
        # a mechanism figure legitimately repeats a label across mirrored containers and panels
        # (fwd / bwd on Device 1 and Device 2): only same-parent, same-panel duplicates are ambiguous
        scope = (n.get("parent"), n.get("panel")) if mech else None
        labels.setdefault((n.get("label", "").strip().lower(), scope), []).append(n.get("id"))
    for (lab, _scope), who in labels.items():
        if lab and len(who) > 1:
            rep.warn("nodes[].label", "%d boxes share the label %r (%s) -- ambiguous labels are a "
                                      "recorded weakness" % (len(who), lab, ", ".join(who)))
    fam = {}
    for n in nodes:
        stem = re.sub(r"[-_ ]?\d+$", "", n.get("label", "").strip().lower())
        if stem:
            fam.setdefault(stem, []).append(n)
    # ids the spec points at one by one (edges, deltas, values, annotations, steps): such boxes are distinct items
    # the reader tracks (E0 ... E7 each with its own load), not copies to collapse into xN
    referenced = set()
    def collect(x):
        if isinstance(x, dict):
            for v in x.values(): collect(v)
        elif isinstance(x, list):
            for v in x: collect(v)
        elif isinstance(x, str):
            referenced.add(x)
    for arr in ("edges", "deltas", "values", "annotations", "steps"):
        collect(spec.get(arr) or [])
    worked = bool(((meta.get("mechanism") or {}).get("worked_example")))
    for stem, group in fam.items():
        tracked = sum(1 for g in group if g.get("id") in referenced)
        if worked or tracked >= 2:
            continue
        if len(group) >= 3 and not any(g.get("multiplicity") for g in group):
            rep.warn("nodes", "%d near-identical boxes named like %r -- draw two plus an "
                              "ellipsis and set multiplicity ('xN') on one node instead"
                     % (len(group), stem))

    # --- steps --------------------------------------------------------------
    ns = sorted(s.get("n") for s in steps if isinstance(s.get("n"), int))
    if ns and ns != list(range(1, len(ns) + 1)):
        rep.warn("steps", "step numbers %s are not contiguous from 1" % ns)
    if len(steps) > STEP_MAX:
        rep.warn("steps", "%d steps; a walkthrough should be 3-8 steps" % len(steps))
    if steps and meta.get("step_markers", "none") == "none":
        rep.warn("meta.step_markers", "steps[] is filled but step_markers is 'none' -- the "
                                      "markers will not be drawn")
    if not steps and meta.get("step_markers", "none") != "none":
        rep.warn("meta.step_markers", "step_markers is %r but steps[] is empty"
                 % meta.get("step_markers"))
    edge_steps = {e.get("step") for e in edges if e.get("step")}
    missing = sorted(s for s in edge_steps if s not in set(ns))
    if steps and missing:
        rep.warn("edges[].step", "edges carry step number(s) %s with no matching steps[] entry"
                 % missing)
    if steps and not (meta.get("caption_draft") or ""):
        rep.warn("meta.caption_draft", "numbered figures must decode their steps in the caption "
                                       "prose; caption_draft is empty")

    # --- legend -------------------------------------------------------------
    enc = distinct_encodings(spec)
    bare = [e for e in edges if not (e.get("label") or "").strip()]
    edge_kinds = {e.get("kind", "data") for e in bare}
    edge_styles = {e.get("style", "solid") for e in bare}
    line_carries_meaning = len(edge_kinds) > 1 and len(edge_styles) > 1
    roles = {n.get("role", "existing") for n in nodes}
    accent_vs_neutral_only = roles <= {"novel", "existing"} and not line_carries_meaning \
        and not any(n.get("symbol") for n in nodes)
    mode = legend.get("mode", "none")
    if mode == "none" and not accent_vs_neutral_only:
        if len(enc) > ENCODINGS_NEEDING_LEGEND:
            rep.warn("legend.mode", "%d distinct encodings in play (%s...) and no legend; "
                                    "encoding.md Part C requires one above %d"
                     % (len(enc), ", ".join("/".join(str(x) for x in e) for e in sorted(enc)[:3]),
                        ENCODINGS_NEEDING_LEGEND))
        elif line_carries_meaning:
            rep.warn("legend.mode", "line style carries meaning (%s over %s) but there is no "
                                    "legend" % ("/".join(sorted(edge_kinds)), "/".join(sorted(edge_styles))))
    if mode == "none" and legend.get("items"):
        rep.warn("legend.mode", "legend items are declared but mode is 'none'")
    if mode == "explicit":
        used = {n.get("legend_ref") for n in nodes} | {e.get("legend_ref") for e in edges} | \
               {a.get("legend_ref") for a in (spec.get("annotations") or []) if isinstance(a, dict)}
        used.discard(None)
        if used:
            for item in legend.get("items") or []:
                if isinstance(item, dict) and item.get("id") not in used:
                    rep.warn("legend.items", "item %r is referenced by no node, edge or annotation -- the "
                                             "step-6 linter cannot check it" % item.get("id"))

    # --- graph hygiene ------------------------------------------------------
    touched = set()
    for e in edges:
        touched.add(e.get("from"))
        touched.add(e.get("to"))
    # a box inside a container, or inside a panel / part (a bar of a values part, a block of a timeline, a band that
    # every lane crosses), has its context; only a box floating on its own reads as decoration
    orphans = [n.get("id") for n in nodes
               if n.get("id") not in touched and not n.get("parent") and not n.get("panel") and n.get("kind") != "note"]
    if orphans:
        rep.warn("nodes", "%d box(es) with no edge, no parent and no panel (%s%s) -- a labelled box with "
                          "degree 0 reads as decoration"
                 % (len(orphans), ", ".join(orphans[:5]),
                    ", ..." if len(orphans) > 5 else ""))
    for e in edges:
        if e.get("head") == "none" and e.get("kind") in ("data", "control", "feedback"):
            rep.warn("edges[%s].head" % e.get("id"), "a %s edge with no arrowhead; missing heads "
                                                     "are the #2 hard failure mode" % e.get("kind"))

    # --- lanes --------------------------------------------------------------
    if col == "single" and len([l for l in lanes if l.get("kind") != "phase"]) > LANES_MAX_SINGLE:
        rep.warn("lanes", "%d lanes at single column; 2-3 is the practical limit"
                 % len([l for l in lanes if l.get("kind") != "phase"]))
    if meta.get("template") == "phase-lanes" and not lanes:
        rep.warn("lanes", "template is 'phase-lanes' but no lanes are declared")
    if any(l.get("kind") == "phase" for l in lanes) and \
       any(l.get("kind") in ("lane", "tier") for l in lanes):
        phases = [l for l in lanes if l.get("kind") == "phase"]
        if any(l.get("orientation") == "horizontal" for l in phases):
            rep.warn("lanes", "phases are drawn as vertical rules, not horizontal bands -- "
                              "lanes (who) and phases (when) must not share a visual device")

    # --- style overrides ----------------------------------------------------
    so = spec.get("style_overrides") or {}
    for key, val in (so.get("font_size_pt") or {}).items():
        if isinstance(val, (int, float)):
            if val < FONT_FLOOR:
                rep.warn("style_overrides.font_size_pt.%s" % key,
                         "%.1f pt is below the %.0f pt print floor" % (val, FONT_FLOOR))
            if val > FONT_CEIL:
                rep.warn("style_overrides.font_size_pt.%s" % key,
                         "%.1f pt is above %.0f pt; the largest label should be <= 1.5x the body"
                         % (val, FONT_CEIL))
    for key, val in (so.get("stroke_width_pt") or {}).items():
        if isinstance(val, (int, float)) and not STROKE_BAND[0] <= val <= STROKE_BAND[1]:
            rep.warn("style_overrides.stroke_width_pt.%s" % key,
                     "%.2f pt is outside the measured band %.2f-%.2f pt"
                     % (val, STROKE_BAND[0], STROKE_BAND[1]))
    if (so.get("palette_roles") or {}).get("canvas", "#ffffff").lower() not in ("#ffffff", "#fff", ""):
        rep.warn("style_overrides.palette_roles.canvas",
                 "727/727 architecture figures use a white page background")

    # --- intake -------------------------------------------------------------
    if not (meta.get("caption_draft") or ""):
        rep.info("meta.caption_draft", "empty -- the caption is part of the deliverable")
    if not nodes:
        rep.error("nodes", "a spec with no nodes cannot be drawn")


# ------------------------------------------------------------ mechanism pass
def mechanism_pass(spec, rep):
    """Checks for meta.kind = mechanism: the group's own block is present and the panel structure is consistent
    (references/mechanism/, mech-prescreen/typedisc/types_v3.md)."""
    meta = spec.get("meta") or {}
    m = meta.get("mechanism") or {}
    group = m.get("group", "anatomy")
    panels = [p for p in (spec.get("panels") or []) if isinstance(p, dict)]
    deltas = [d for d in (spec.get("deltas") or []) if isinstance(d, dict)]
    values = [v for v in (spec.get("values") or []) if isinstance(v, dict)]
    steps = [s for s in (spec.get("steps") or []) if isinstance(s, dict)]
    nodes = [n for n in (spec.get("nodes") or []) if isinstance(n, dict)]
    edges = [e for e in (spec.get("edges") or []) if isinstance(e, dict)]
    arrangement = m.get("arrangement", "single")
    if group == "other":
        rep.info("meta.mechanism.group", "group 'other': none of the five groups is assumed, so only the arrangement / "
                                         "panel consistency checks below run -- say how the figure reads in notes")
    elif group not in MECH_GROUPS:
        rep.error("meta.mechanism.group", "%r is not a v3 group (%s) or 'other'" % (group, ", ".join(MECH_GROUPS)))
    parts = [p for p in panels if p.get("axis") == "part"]
    panels = [p for p in panels if p.get("axis") != "part"]                # parts repeat no template
    if group in ("comparison", "evolution"):
        if len(panels) < 2:
            rep.warn("panels", "%s figures draw the template two or more times -- declare one panels[] "
                               "entry per %s" % (group, "alternative" if group == "comparison" else "frame"))
        want_axis = "alternatives" if group == "comparison" else "time"
        off = [p.get("id") for p in panels if p.get("axis", "alternatives") not in (want_axis, "zoom")]
        if off:
            rep.info("panels", "%s panels usually vary along '%s'; %s declare another axis"
                     % (group, want_axis, ", ".join(map(str, off))))
        if group == "evolution" and panels and not deltas:
            rep.warn("deltas", "evolution frames without deltas[] -- say what changes in each frame, "
                               "the drawer keeps everything else identical")
        if group == "comparison" and panels and not deltas and not any(p.get("differs") for p in panels):
            rep.warn("panels", "comparison panels declare neither `differs` nor deltas[] -- the reader "
                               "must be told what to compare")
    if group == "walkthrough" and not steps:
        rep.warn("steps", "a walkthrough is a structure drawn once plus numbered markers along a path -- "
                          "steps[] is empty")
    if group == "logic":
        if not any(n.get("kind") in ("state", "decision") for n in nodes):
            rep.warn("nodes", "a logic figure draws states or decisions -- no node has kind 'state' or "
                              "'decision'")
        decision_ids = {n.get("id") for n in nodes if n.get("kind") == "decision"}
        bare = [e.get("id") for e in edges
                if (e.get("kind") == "transition" or e.get("from") in decision_ids) and not e.get("guard")]
        if bare:
            rep.warn("edges", "transitions / decision branches without a guard label: %s -- every edge "
                              "leaving a decision and every transition names its trigger or condition"
                     % ", ".join(map(str, bare[:8])))
    if m.get("worked_example") and not values:
        rep.warn("values", "worked_example is set but values[] is empty -- list the values the reader "
                           "checks, linked where one value recurs")
    if values and not m.get("worked_example"):
        rep.info("values", "values[] declared without meta.mechanism.worked_example -- fine for a few "
                           "annotated numbers, set the flag when the values are the content")
    if len(panels) + len(parts) >= 2 and arrangement == "single":
        rep.warn("meta.mechanism.arrangement", "%d panels declared but arrangement is 'single'" % (len(panels) + len(parts)))
    if len(panels) + len(parts) < 2 and arrangement.startswith(("panels-", "frames-")):
        rep.warn("meta.mechanism.arrangement", "arrangement %r needs two or more panels[]" % arrangement)
    if parts and int(meta.get("panels", 1) or 1) != len(parts):
        rep.info("meta.panels", "meta.panels = %s but the composite figure has %d parts" % (meta.get("panels"), len(parts)))
    elif not parts and panels and int(meta.get("panels", 1) or 1) != len(panels):
        rep.info("meta.panels", "meta.panels = %s but panels[] has %d entries" % (meta.get("panels"), len(panels)))
    templ = {p.get("id") for p in panels if not p.get("template_of")}
    for i, d in enumerate(deltas):
        if d.get("panel") in templ and len(panels) >= 2:
            rep.info("deltas[%d]" % i, "delta on the template panel %r -- deltas usually describe the "
                                       "other panels against the template" % d.get("panel"))
    per_panel = {}
    for n in nodes:
        if n.get("panel"):
            per_panel[n["panel"]] = per_panel.get(n["panel"], 0) + 1
    if panels and m.get("frame_template", "none") == "identical" and per_panel:
        rep.info("nodes", "frame_template is 'identical' yet %d nodes are panel-specific (%s) -- prefer "
                          "shared template nodes plus deltas[]"
                 % (sum(per_panel.values()), ", ".join("%s: %d" % kv for kv in sorted(per_panel.items()))))
    if group == "walkthrough" and steps and meta.get("step_markers", "none") == "none":
        rep.warn("meta.step_markers", "walkthrough steps need a marker style (circled-numbers / plain-numbers / "
                                      "letters / labelled-arrows / timeline-ticks)")


# ---------------------------------------------------------------------- driver
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="path to the figure spec JSON")
    ap.add_argument("--schema", default=DEFAULT_SCHEMA)
    ap.add_argument("--palettes", default=DEFAULT_PALETTES)
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    ap.add_argument("--json", action="store_true", dest="as_json", help="machine-readable report")
    args = ap.parse_args(argv)

    rep = Report()
    try:
        with open(args.spec, encoding="utf-8") as fh:
            spec = json.load(fh)
    except FileNotFoundError:
        print("spec_validate: no such file: %s" % args.spec, file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print("spec_validate: %s is not valid JSON: %s" % (args.spec, exc), file=sys.stderr)
        return 1

    schema = None
    try:
        with open(args.schema, encoding="utf-8") as fh:
            schema = json.load(fh)
    except OSError:
        rep.warn("schema", "could not read %s -- schema pass skipped" % args.schema)
    palettes = {}
    try:
        with open(args.palettes, encoding="utf-8") as fh:
            palettes = json.load(fh)
    except OSError:
        rep.warn("palettes", "could not read %s -- palette id not checked" % args.palettes)

    if not isinstance(spec, dict):
        rep.error("$", "the spec must be a JSON object")
    else:
        if schema:
            schema_pass(spec, schema, rep)
        reference_pass(spec, palettes, rep, base_dir=os.path.dirname(os.path.abspath(args.spec)))
        style_pass(spec, rep)

    if args.as_json:
        print(json.dumps({
            "spec": args.spec,
            "errors": [{"where": w, "message": m} for w, m in rep.errors],
            "warnings": [{"where": w, "message": m} for w, m in rep.warnings],
            "infos": [{"where": w, "message": m} for w, m in rep.infos],
        }, indent=2, ensure_ascii=False))
    else:
        print("spec: %s" % args.spec)
        for where, msg in rep.errors:
            print("  ERROR  %-34s %s" % (where, msg))
        for where, msg in rep.warnings:
            print("  WARN   %-34s %s" % (where, msg))
        for where, msg in rep.infos:
            print("  info   %-34s %s" % (where, msg))
        verdict = "FAIL" if rep.errors else ("PASS with warnings" if rep.warnings else "PASS")
        print("  --- %d error(s), %d warning(s): %s" % (len(rep.errors), len(rep.warnings), verdict))

    if rep.errors:
        return 1
    if args.strict and rep.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
