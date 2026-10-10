#!/usr/bin/env python3
"""Geometry / style / spec-consistency linter for figure SVGs drawn under the figgenie-paper-diagram contract.

  python3 scripts/lint.py fig.svg [--spec fig.json] [--report fig.lint.json] [--annotate fig.lint.svg] [--strict] [--quiet]

Measures the SVG in headless Chromium (exact boxes in pt), then checks, in this order:
  canvas     viewBox origin 0 0, width inside the single/double column band
  bleed      anything outside the viewBox                                            error
  fonts      font families that Chromium could not resolve                            warn
  text       size < 5 pt error, < 6 pt warn; > 3 distinct sizes warn; > 2 families warn
  overflow   a node's label leaves its box (or padding < 1.5 pt)                      error / warn
             (a label marked data-label="outside" sits beside its box on purpose: it only has to stay clear of it)
  overlap    node boxes intersect; text on text; text on a line it does not belong to error / error / warn
             (text is measured on its glyph ink, read from the font file -- about 0.75 em above the baseline, and
             below it only as far as its descenders reach (0.25 em for g/p/y, a comma less, none for 'Attention') -- not on
             Chromium's line box; step-badge digits are exempt from the text-on-line check)
  contain    node not inside its container (spec parent, or c:* box it visually sits in) error
  align      edges or centres of boxes within 0.3–2 pt of each other but not equal    warn
             (only boxes of the same panel are compared; text-only nodes and anything inside data-scale="data" --
             bars, Gantt rows drawn to scale -- are skipped; a row whose gaps differ by 2x or more, or that another
             box interrupts, is read as deliberate grouping)
  centre     label centre off the box centre by > 1 pt                                warn
  edges      dangling end (> 3 pt from any box), missing arrowhead, line crossing a box it does not connect  warn
  colour     > 12 distinct fills, > 2 saturated fills, > 3 stroke widths, width outside 0.3–2.5 pt  warn
  style      (spec meta.style set, references/styles/<style>.json): labels bold, every box outlined in dark ink,
             box stroke band; the style may raise the saturated-fill ceiling                           warn / info
  density    more labelled boxes than the column budget (q3 warn, p90 error-ish -> warn+); in a composite figure
             (panels[] with axis "part") each part is held to the single-column budget instead
  spec       every spec node/edge/container/lane/step/legend has its <g id="..">, labels match      error / warn
  glyphs     characters that no shipped / embedded / system-resolved face covers (needs fonttools)  warn
  heads      an arrowhead overlapping a line it does not connect (a tier divider, another edge);
             an edge tail starting within 3 pt of a foreign line                                    warn
  replicas   stacked copies (×N cards) whose visible ledges are not equal                           warn
  titles     a container title not centred between the top edge and its first content; a rotated
             rotated gutter label     not centred between the edge and the content                  warn
  images     bitmaps are allowed (2026-09-28). A link to a URL, a missing / undecodable file, a
             format other than PNG or JPEG, an <image> without width / height, xlink:href without
             xmlns:xlink                                                                           error
             < image_ppi_warn ppi at print size, a stretched or letterboxed picture, an EXIF rotation  warn
             far more pixels than print needs                                                      info
             A node whose box is a picture (or the frame drawn on it) takes the picture as its box: its
             label is a caption beside or under it (only a label straddling the picture's edge is
             text.overflow) and the centring check is skipped. Relative links resolve against the SVG's
             folder; URLs are never fetched.
  mechanism  (meta.kind = mechanism only; every finding is warn / info -- the drawing is the agent's call, the
             linter only checks that the SVG says what the spec says) each panels[] entry has its p:<id>
             group; elements with a panel field sit inside that panel; with frame_template identical, a
             template element keeps the same offset in every panel; deltas[] targets carry data-delta;
             values[] have v:<id>; edges with a guard draw it. Template copies n:<id>@<panel> satisfy the
             spec checks, budgets count distinct ids; column band from references/mechanism/style-thresholds.json.
Exit code: 1 when any error (or any warning with --strict), else 0.  --annotate writes an overlay SVG
(red = error, orange = warning) you can open in a browser or render with render.py.
"""
import argparse, colorsys, json, math, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _svgkit as K

SKILL = Path(__file__).resolve().parents[1]
DEFAULT_THRESH = SKILL / 'references' / 'style-thresholds.json'
SHAPES = ('rect', 'path', 'ellipse', 'circle', 'polygon')
LINES = ('path', 'line', 'polyline')
PREFIX = {'n:': 'node', 'e:': 'edge', 'c:': 'container', 'l:': 'lane', 's:': 'step', 'a:': 'annotation', 'p:': 'panel', 'v:': 'value'}
MECH_THRESH = SKILL / 'references' / 'mechanism' / 'style-thresholds.json'
MECH_NODE_BUDGET = {'single': {'q3': 12, 'p90': 14}, 'double': {'q3': 15, 'p90': 17}}   # label-distinct, spec_validate.py MECH_BOX_*


def kind_of(el):
    if el.get('kind'): return el['kind']
    i = el.get('id') or ''
    if i == 'legend' or i.startswith('legend:'): return 'legend'
    for p, k in PREFIX.items():
        if i.startswith(p): return k
    return None


def rgb(s):
    m = re.match(r'rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)', s or '')
    return (float(m.group(1)), float(m.group(2)), float(m.group(3))) if m else None


def is_grey(c):
    if not c: return True
    r, g, b = c; mx, mn = max(r, g, b), min(r, g, b)
    return (mx - mn) < 18 or mx < 30


def saturated(c):
    if not c: return False
    r, g, b = [v / 255 for v in c]; h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return s > 0.45 and v > 0.35


def box(el): return (el['x'], el['y'], el['x'] + el['w'], el['y'] + el['h'])
def inter(a, b): return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])
def overlap_area(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0]); h = min(a[3], b[3]) - max(a[1], b[1]); return max(0, w) * max(0, h)
def inside(a, b, pad=0.0): return a[0] >= b[0] + pad and a[1] >= b[1] + pad and a[2] <= b[2] - pad and a[3] <= b[3] - pad
def area(a): return max(0, a[2] - a[0]) * max(0, a[3] - a[1])
def dist_to_box(p, b):
    dx = max(b[0] - p[0], 0, p[0] - b[2]); dy = max(b[1] - p[1], 0, p[1] - b[3]); return math.hypot(dx, dy)


def seg_dist(p, a, b):
    """Distance from point p to segment a-b."""
    vx, vy = b[0] - a[0], b[1] - a[1]; L2 = vx * vx + vy * vy
    if L2 <= 1e-9: return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))


class Lint:
    def __init__(self, data, spec, thr, svg_text=None, base_dir=None):
        self.d = data; self.spec = spec or {}; self.thr = thr; self.f = []
        self.svg_text = svg_text or ''; self.markers = self._markers(); self.base_dir = base_dir
        els = [e for e in data['elements'] if e['w'] > 0 or e['h'] > 0 or e['tag'] == 'g']
        self.els = els
        self.groups = {e['id']: e for e in els if e['tag'] == 'g' and e.get('id')}
        self.by_kind = {}
        for gid, g in self.groups.items():
            k = kind_of(g)
            if k: self.by_kind.setdefault(k, {})[gid] = g
        self.children = {}
        for e in els:
            if e.get('parentGroup'): self.children.setdefault(e['parentGroup'], []).append(e)
        self.texts = [e for e in els if e['tag'] == 'text' and e.get('text')]
        self.W, self.H = data['W'], data['H']
        self.mech = ((self.spec.get('meta') or {}).get('kind') == 'mechanism')
        sp = [q for q in (self.spec.get('panels') or []) if isinstance(q, dict) and q.get('id')]
        self.panel_parent = {q['id']: q.get('parent') for q in sp}
        self.panel_axis = {q['id']: q.get('axis', 'alternatives') for q in sp}
        self.composite = any(a == 'part' for a in self.panel_axis.values())
        self.spec_panel = {}
        for arr, pre in (('nodes', 'n:'), ('containers', 'c:'), ('lanes', 'l:'), ('annotations', 'a:')):
            for x in self.spec.get(arr) or []:
                if isinstance(x, dict) and x.get('panel'): self.spec_panel[pre + x['id']] = x['panel']
        ckind = {f"c:{c['id']}": c.get('kind') for c in (self.spec.get('containers') or []) if isinstance(c, dict) and c.get('id')}
        self.panel_boxes = {}                                         # p:<id> groups and containers of kind 'panel'
        for gid in self.groups:
            if gid.startswith('p:') or (gid.startswith('c:') and ckind.get(gid) == 'panel'):
                self.panel_boxes[gid[2:]] = self.shape_of(gid)

    @staticmethod
    def base_id(gid):
        """n:cache@b -> n:cache (a template element repeated inside panel b)."""
        return gid.split('@', 1)[0]

    def copies(self, gid):
        """The drawn groups that stand for spec element gid: the plain id and/or its per-panel copies."""
        return [g for g in self.groups if g == gid or g.startswith(gid + '@')]

    def add(self, sev, code, msg, ids=(), bbox=None):
        self.f.append(dict(severity=sev, code=code, message=msg, elements=[i for i in ids if i], bbox=bbox))

    # ---- helpers
    def explicit_shape(self, gid):
        """Largest visible non-text, non-symbol child shape of a group (the box), or None. A bitmap counts: a picture
        node's box is the picture (the frame drawn on it coincides with it)."""
        best = None
        for e in self.children.get(gid, []):
            if e.get('inSymbol'): continue                                # icon parts never stand for the box
            if (e['tag'] in SHAPES and e['w'] > 1 and e['h'] > 1 and (e['fill'] != 'none' or e['stroke'] != 'none')) or \
               (e['tag'] == 'image' and e['w'] > 1 and e['h'] > 1):
                if best is None or area(box(e)) > area(box(best)): best = e
        return best

    def has_image(self, gid):
        return any(e['tag'] == 'image' for e in self.children.get(gid, []))

    def is_picture_box(self, gid):
        """True when the group's box is a bitmap or a frame drawn on one (within 1 pt): its label is then a caption
        beside or under the picture, or a label laid over it -- not a label that must sit inside a box."""
        best = self.explicit_shape(gid)
        if best is None: return False
        if best['tag'] == 'image': return True
        b = box(best)
        return any(e['tag'] == 'image' and max(abs(p - q) for p, q in zip(box(e), b)) <= 1.0 for e in self.children.get(gid, []))

    def shape_of(self, gid):
        """The group's box: its largest drawn shape, else the group's own bbox (icon + label composites)."""
        best = self.explicit_shape(gid)
        return box(best) if best else box(self.groups[gid])

    def band_of(self, gid):
        """A lane's band: its largest <rect> child even when unpainted (lanes are often fill="none" stroke="none"),
        else the usual shape_of."""
        best = None
        for e in self.children.get(gid, []):
            if e['tag'] == 'rect' and not e.get('inSymbol') and e['w'] > 1 and e['h'] > 1:
                if best is None or area(box(e)) > area(box(best)): best = e
        return box(best) if best else self.shape_of(gid)

    def frame_of(self, gid):
        """The box a container or lane stands for: a lane's band (band_of: its largest rect even when unpainted --
        a painted slot drawn inside the lane group must not become the lane), any other group's shape_of."""
        return self.band_of(gid) if kind_of(self.groups.get(gid, {})) == 'lane' else self.shape_of(gid)

    def panel_scope(self, gid):
        """The panel a node is drawn in, so that boxes of different panels are never compared with each other:
        data-panel / the @<panel> copy suffix, the p:<id> group it is nested in, the smallest panel box (p:<id> or
        a container of kind 'panel') around it, else its spec panel; None in a one-panel figure."""
        a = self.groups[gid].get('attrs') or {}
        if a.get('data-panel'): return a['data-panel']
        if '@' in gid: return gid.split('@', 1)[1]
        g = self.groups[gid].get('parentGroup')
        while g:
            if g.startswith('p:'): return g[2:]
            g = (self.groups.get(g) or {}).get('parentGroup')
        if self.panel_boxes:
            b = self.shape_of(gid)
            cands = [(area(pb), pid) for pid, pb in self.panel_boxes.items() if inside(b, pb, -0.5)]
            if cands: return min(cands)[1]
        return self.spec_panel.get(self.base_id(gid))

    def part_of(self, pid):
        """The top-level panel (a composite figure's part) that panel pid belongs to."""
        seen = set()
        while pid and self.panel_parent.get(pid) and pid not in seen:
            seen.add(pid); pid = self.panel_parent[pid]
        return pid

    def texts_of(self, gid):
        return [e for e in self.children.get(gid, []) if e['tag'] == 'text' and e.get('text')]

    def ink(self, e):
        """(above, below) pt of the text's glyph ink around its baseline: measured on the font file (K.ink_band) so a
        label without descenders gets no descender band; `text_ink_above_em` / `text_ink_below_em` (thresholds, default
        0.75 / 0.25 em) are the estimate when the face cannot be resolved."""
        t = self.thr.get('lint', {}); fs = e.get('fontSize') or 0
        fam = (e.get('fontFamily') or '').split(',')[0].strip('"\' ')
        key = K.resolve_font(fam, default=False) if fam else None
        w = str(e.get('fontWeight') or '400'); bold = w in ('bold', 'bolder') or (w.isdigit() and int(w) >= 600)
        return K.ink_band(e.get('text', ''), fs, key, bold, t.get('text_ink_above_em', 0.75), t.get('text_ink_below_em', 0.25))

    def tbox(self, e):
        """Ink box of a text element: its glyph band above and below the baseline (self.ink). Chromium's line box is
        font-dependent and tall (TeX Gyre Heros: 1.385 em), so measuring on it would flag every ordinary 1.15-1.2 em
        line pitch as an overlap and pad every box for ascender space that no glyph uses. Falls back to the raw box when
        the renderer recorded no baseline (old dumps)."""
        b = box(e); fs = e.get('fontSize') or 0; bl = e.get('baseline')
        if e.get('rotated') and fs and e.get('baselineX') is not None and abs(abs(e.get('angle') or 0) - 90) < 1:
            # text turned by ±90°: the ink band runs across x around the baseline line x = baselineX; glyph tops point
            # to -x for -90° (reading upwards) and to +x for +90°. Keep the measured extent along y (the advance).
            above, below = self.ink(e)
            bx = e['baselineX']
            x0, x1 = (bx - above, bx + below) if (e.get('angle') or 0) < 0 else (bx - below, bx + above)
            return (max(b[0], x0), b[1], min(b[2], x1), b[3]) if min(b[2], x1) > max(b[0], x0) else b
        if not fs or bl is None or e.get('rotated'): return b
        above, below = self.ink(e)
        asc = bl - b[1]
        if asc <= 0 or asc > 1.6 * fs: return b                      # rotated or oddly placed: keep the raw box
        h = b[3] - b[1]
        desc = (h - asc) if h < 1.7 * fs else 0.27 * asc              # single line: measured; multi-line: estimated
        top = max(b[1], bl - above); bottom = min(b[3], b[3] - desc + below)
        return (b[0], top, b[2], bottom) if bottom > top else b

    def has_symbol(self, gid):
        return any(c.get('inSymbol') or (c.get('attrs') or {}).get('data-symbol') for c in self.children.get(gid, []))

    def node_boxes(self):
        return {gid: self.shape_of(gid) for gid in self.by_kind.get('node', {})}

    # ---- checks
    def check_canvas(self):
        vb = self.d.get('viewBox')
        if not vb: self.add('error', 'canvas.viewbox', 'root <svg> has no viewBox; use viewBox="0 0 W H" in pt'); return
        if abs(vb[0]) > 1e-6 or abs(vb[1]) > 1e-6: self.add('error', 'canvas.origin', f'viewBox origin is {vb[0]},{vb[1]}; must be 0 0')
        W = vb[2]; cols = self.thr.get('columns', {})
        col = (self.spec.get('meta') or {}).get('column')
        if not col: col = 'double' if W >= 380 else 'single'
        band = cols.get(col, {}).get('width_p5_p95'); target = cols.get(col, {}).get('width_target')
        if band and not (band[0] - 2 <= W <= band[1] + 2):
            self.add('error', 'canvas.width', f'width {W:.0f} pt is outside the {col}-column band {band[0]:.0f}–{band[1]:.0f} pt (target {target} pt)')
        hmax = cols.get(col, {}).get('height_max_p95')
        if hmax and vb[3] > hmax * 1.15: self.add('warn', 'canvas.height', f'height {vb[3]:.0f} pt exceeds the {col}-column p95 height {hmax:.0f} pt; consider a wider, flatter layout')

    def check_bleed(self):
        vb = self.d.get('viewBox') or [0, 0, self.W, self.H]; page = (vb[0], vb[1], vb[0] + vb[2], vb[1] + vb[3])
        for e in self.els:
            if e['tag'] in ('g', 'svg') or (e['w'] == 0 and e['h'] == 0): continue
            b = box(e)
            if b[0] < page[0] - 0.5 or b[1] < page[1] - 0.5 or b[2] > page[2] + 0.5 or b[3] > page[3] + 0.5:
                self.add('error', 'bleed', f'<{e["tag"]}> {e.get("id") or e.get("text") or ""!s} extends outside the canvas ({b[0]:.1f},{b[1]:.1f})–({b[2]:.1f},{b[3]:.1f})', [e.get('id') or e.get('parentGroup')], b)

    def check_fonts(self):
        for fam, ok in (self.d.get('fonts') or {}).items():
            if not ok and fam.lower() not in ('sans-serif', 'serif', 'monospace', 'system-ui'):
                self.add('warn', 'font.unresolved', f'font family "{fam}" is not available/embedded; run embed_fonts.py or use a key from assets/fonts/fonts.json')

    def check_text(self):
        t = self.thr.get('lint', {}); err = t.get('font_min_error', 5.0); wrn = t.get('font_min_warn', 6.0)
        sizes, fams = set(), set()
        for e in self.texts:
            fs = e.get('fontSize') or 0; fams.add((e.get('fontFamily') or '').split(',')[0].strip('"\' '))
            in_badge = kind_of(self.groups.get(e.get('parentGroup') or '', {})) == 'step' or \
                (e.get('inSymbol') and len(e.get('text', '').strip()) <= 2)   # a digit in a badge glyph (place_text.py line @badge)
            if not in_badge: sizes.add(round(fs * 2) / 2)
            err, wrn = (t.get('font_min_error', 5.0) - 1.0, t.get('font_min_warn', 6.0) - 1.0) if in_badge else (t.get('font_min_error', 5.0), t.get('font_min_warn', 6.0))
            if fs < err: self.add('error', 'text.size', f'"{e["text"][:40]}" is {fs:.1f} pt (< {err} pt is unreadable in print)', [e.get('parentGroup')], box(e))
            elif fs < wrn: self.add('warn', 'text.size', f'"{e["text"][:40]}" is {fs:.1f} pt (< {wrn} pt floor)', [e.get('parentGroup')], box(e))
        if len(sizes) > 3: self.add('warn', 'text.sizes', f'{len(sizes)} distinct font sizes {sorted(sizes)}; keep to 3 levels (title / label / small)')
        if len(fams) > 2: self.add('warn', 'text.families', f'{len(fams)} font families {sorted(fams)}; use one sans (plus monospace for code at most)')

    def check_overflow(self):
        for gid in self.by_kind.get('node', {}):
            if self.explicit_shape(gid) is None: continue                # no drawn box: nothing to overflow or pad
            sb = self.shape_of(gid); picture = self.is_picture_box(gid)
            for e in self.texts_of(gid):
                tb = self.tbox(e)
                if e.get('labelOutside'):                                 # data-label="outside": beside the box on purpose
                    if inter(tb, (sb[0] + 0.5, sb[1] + 0.5, sb[2] - 0.5, sb[3] - 0.5)):
                        self.add('error', 'text.overflow', f'label "{e["text"][:40]}" of {gid} is marked data-label="outside" but '
                                 f'overlaps its box; move it clear of the box or drop the marker', [gid], tb)
                    continue
                if picture:                                               # a caption outside, or a label laid over it
                    if inter(tb, (sb[0] + 0.5, sb[1] + 0.5, sb[2] - 0.5, sb[3] - 0.5)) and not inside(tb, sb, -0.5):
                        self.add('error', 'text.overflow', f'label "{e["text"][:40]}" straddles the edge of the picture in {gid}; '
                                 f'put the caption clear of it or the label wholly on it', [gid], tb)
                    continue
                if not inside(tb, sb, -0.5):
                    self.add('error', 'text.overflow', f'label "{e["text"][:40]}" leaves its box {gid}', [gid], tb)
                elif not inside(tb, sb, 1.5):
                    self.add('warn', 'text.padding', f'label "{e["text"][:40]}" has < 1.5 pt padding inside {gid}', [gid], tb)

    def check_overlap(self):
        nb = self.node_boxes(); ids = list(nb)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = nb[ids[i]], nb[ids[j]]
                if inter(a, b) and overlap_area(a, b) > 0.5:
                    self.add('error', 'overlap.nodes', f'{ids[i]} and {ids[j]} overlap', [ids[i], ids[j]], (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])))
        cb = {gid: self.frame_of(gid) for gid in list(self.by_kind.get('container', {})) + list(self.by_kind.get('lane', {}))}
        cids = list(cb)
        for i in range(len(cids)):
            for j in range(i + 1, len(cids)):
                a, b = cb[cids[i]], cb[cids[j]]
                if inter(a, b) and not inside(a, b, -0.5) and not inside(b, a, -0.5):
                    ka, kb = kind_of(self.groups[cids[i]]), kind_of(self.groups[cids[j]])
                    if ka == 'lane' and kb == 'lane' or ka != kb: continue   # lanes tile; lanes and containers may cross
                    self.add('error', 'overlap.containers', f'{cids[i]} and {cids[j]} partially overlap (nest them or separate them)', [cids[i], cids[j]])
        T = self.texts
        for i in range(len(T)):
            for j in range(i + 1, len(T)):
                a, b = self.tbox(T[i]), self.tbox(T[j])
                if inter(a, b) and overlap_area(a, b) > 0.3:
                    self.add('error', 'overlap.text', f'"{T[i]["text"][:30]}" overlaps "{T[j]["text"][:30]}"', [T[i].get('parentGroup'), T[j].get('parentGroup')], a)
        # text vs lines it does not belong to
        lines = [e for e in self.els if e['tag'] in LINES and e.get('points') and e['stroke'] != 'none' and (e['tag'] in ('line', 'polyline') or e['fill'] in ('none', 'rgba(0, 0, 0, 0)'))]
        for t in T:
            if kind_of(self.groups.get(t.get('parentGroup') or '', {})) == 'step': continue   # digit inside a filled badge disc
            tb = self.tbox(t); tb2 = (tb[0] - 0.3, tb[1] - 0.3, tb[2] + 0.3, tb[3] + 0.3)
            for ln in lines:
                if ln.get('parentGroup') and ln['parentGroup'] == t.get('parentGroup'): continue
                if kind_of(self.groups.get(t.get('parentGroup'), {})) == 'node' and ln.get('parentGroup') == t.get('parentGroup'): continue
                hits = sum(1 for p in ln['points'] if tb2[0] <= p[0] <= tb2[2] and tb2[1] <= p[1] <= tb2[3])
                if hits >= 2:
                    self.add('warn', 'overlap.text-line', f'line {ln.get("parentGroup") or ln.get("id") or "(unnamed)"} runs through "{t["text"][:30]}"', [ln.get('parentGroup'), t.get('parentGroup')], tb)
                    break

    def check_contain(self):
        nb = self.node_boxes(); cb = {gid: self.shape_of(gid) for gid in self.by_kind.get('container', {})}
        lb = {gid: self.band_of(gid) for gid in self.by_kind.get('lane', {})}
        parent = {}
        for n in (self.spec.get('nodes') or []): parent[f"n:{n['id']}"] = n.get('parent')
        for c in (self.spec.get('containers') or []): parent[f"c:{c['id']}"] = c.get('parent')
        for gid, b in list(nb.items()) + list(cb.items()):
            p = parent.get(gid)
            if p:
                pb = cb.get(f'c:{p}') or lb.get(f'l:{p}')
                if pb is None: continue
                if not inside(b, pb, -0.5): self.add('error', 'contain.outside', f'{gid} is not inside its parent {p}', [gid, f'c:{p}'], b)
                elif not inside(b, pb, 2.0): self.add('warn', 'contain.padding', f'{gid} is < 2 pt from the border of {p}', [gid], b)
            else:
                for cid, pb in cb.items():
                    if cid == gid: continue
                    if inter(b, pb) and not inside(b, pb, -0.5) and not inside(pb, b, -0.5) and overlap_area(b, pb) > 0.25 * area(b):
                        self.add('error', 'contain.straddle', f'{gid} straddles the border of {cid}', [gid, cid], b)

    def check_align(self):
        # Snapping advice only makes sense between drawn boxes that a reader compares: skip text-only nodes (their
        # box is the text), anything drawn to scale from data (data-scale="data": bar lengths, Gantt rows), and
        # pairs from different panels (each panel is laid out on its own).
        allb = self.node_boxes()
        nb = {i: b for i, b in allb.items() if self.explicit_shape(i) is not None and not self.groups[i].get('scaleData')}
        ids = list(nb); scope = {i: self.panel_scope(i) for i in ids}
        seen = set()
        for axis, name in ((0, 'left'), (2, 'right'), (1, 'top'), (3, 'bottom')):
            vals = sorted((nb[i][axis], i) for i in ids)
            for (v1, i1), (v2, i2) in zip(vals, vals[1:]):
                d = v2 - v1
                if 0.3 < d <= 2.0 and (i1, i2, name) not in seen and scope[i1] == scope[i2]:
                    # only flag when the two boxes are in the same row/column (share extent on the other axis)
                    a, b = nb[i1], nb[i2]
                    same = (a[1] < b[3] and b[1] < a[3]) if axis in (0, 2) else (a[0] < b[2] and b[0] < a[2])
                    if same or d <= 1.0:
                        seen.add((i1, i2, name)); self.add('warn', 'align.edge', f'{name} edges of {i1} and {i2} differ by {d:.1f} pt (snap them)', [i1, i2])
        for axis, name in (('cx', 'horizontal centres'), ('cy', 'vertical centres')):
            vals = sorted(((nb[i][0] + nb[i][2]) / 2 if axis == 'cx' else (nb[i][1] + nb[i][3]) / 2, i) for i in ids)
            for (v1, i1), (v2, i2) in zip(vals, vals[1:]):
                d = v2 - v1
                if 0.3 < d <= 1.5 and scope[i1] == scope[i2]:
                    a, b = nb[i1], nb[i2]
                    same = (a[0] < b[2] and b[0] < a[2]) if axis == 'cx' else (a[1] < b[3] and b[1] < a[3])
                    if same: self.add('warn', 'align.centre', f'{name} of {i1} and {i2} differ by {d:.1f} pt', [i1, i2])
        # uneven gaps in a row of >=3 boxes that share the same panel and container / lane
        cb = {gid: self.frame_of(gid) for gid in list(self.by_kind.get('container', {})) + list(self.by_kind.get('lane', {}))}
        def holder(b):
            cands = [(area(cb[c]), c) for c in cb if inside(b, cb[c], -0.5)]
            return min(cands)[1] if cands else None
        rows = {}
        for i in ids: rows.setdefault((scope[i], holder(nb[i]), round((nb[i][1] + nb[i][3]) / 2 / 4)), []).append(i)
        for r, members in rows.items():
            if len(members) < 3: continue
            ms = sorted(members, key=lambda i: nb[i][0])
            # split the row where another box (a tall band, a box of another row) stands in the gap
            runs, cur = [], [ms[0]]
            for a, b in zip(ms, ms[1:]):
                gap = (nb[a][2], max(nb[a][1], nb[b][1]), nb[b][0], min(nb[a][3], nb[b][3]))
                if any(o not in (a, b) and gap[2] > gap[0] and inter(allb[o], gap) for o in allb): runs.append(cur); cur = [b]
                else: cur.append(b)
            runs.append(cur)
            for run in runs:
                if len(run) < 3: continue
                gaps = [nb[b][0] - nb[a][2] for a, b in zip(run, run[1:])]
                if all(g > 0 for g in gaps) and max(gaps) - min(gaps) > 3.0 and max(gaps) < 60 and max(gaps) < 2 * min(gaps):
                    self.add('warn', 'align.gaps', f'uneven gaps {[round(g, 1) for g in gaps]} pt between {", ".join(run)}', run)

    def check_centre(self):
        for gid in self.by_kind.get('node', {}):
            sb = self.shape_of(gid); ts = [t for t in self.texts_of(gid) if not t.get('labelOutside')]
            if not ts: continue
            if self.has_symbol(gid) or self.has_image(gid): continue       # icon / picture + label composites are not centred labels
            cx = (sb[0] + sb[2]) / 2; cy = (sb[1] + sb[3]) / 2
            bs = [self.tbox(t) for t in ts]
            tb = (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))
            tcx = (tb[0] + tb[2]) / 2; tcy = (tb[1] + tb[3]) / 2
            anchored_left = all((t.get('anchor') or 'start') == 'start' and abs(self.tbox(t)[0] - sb[0]) < 6 for t in ts)
            xtol = 1.2 if all(t.get('rotated') for t in ts) else 1.0      # across a turned label: same ink-band model and tolerance as centre.y
            if abs(tcx - cx) > xtol and not anchored_left: self.add('warn', 'centre.x', f'label of {gid} is {tcx - cx:+.1f} pt off the box centre horizontally', [gid], tb)
            if abs(tcy - cy) > 1.2 and len(ts) == 1 and sb[3] - sb[1] < 40: self.add('warn', 'centre.y', f'label of {gid} is {tcy - cy:+.1f} pt off the box centre vertically', [gid], tb)

    def check_edges(self):
        nb = self.node_boxes()
        allb = dict(nb); allb.update({g: self.frame_of(g) for g in list(self.by_kind.get('container', {})) + list(self.by_kind.get('lane', {}))})
        spec_edges = {f"e:{e['id']}": e for e in (self.spec.get('edges') or [])}
        for gid, g in self.by_kind.get('edge', {}).items():
            lines = [e for e in self.children.get(gid, []) if e['tag'] in LINES and e.get('points')]
            if not lines: self.add('warn', 'edge.empty', f'{gid} has no path/line', [gid]); continue
            main = max(lines, key=lambda e: e.get('length', 0)); pts = main['points']
            frm, to = g['attrs'].get('data-from'), g['attrs'].get('data-to')
            for end, p, want in (('start', pts[0], frm), ('end', pts[-1], to)):
                near = min(((dist_to_box(p, b), i) for i, b in allb.items()), default=(99, None))
                if near[0] > 3.0: self.add('warn', 'edge.dangling', f'{gid} {end} is {near[0]:.1f} pt from the nearest box ({near[1]})', [gid], (p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2))
                if want:
                    wb = allb.get(f'n:{want}') or allb.get(f'c:{want}') or allb.get(f'l:{want}')
                    if wb is not None and dist_to_box(p, wb) > 3.0:
                        self.add('warn', 'edge.endpoint', f'{gid} {end} should touch {want} but is {dist_to_box(p, wb):.1f} pt away', [gid, f'n:{want}'])
            has_head = any(e.get('markerEnd') or e.get('markerStart') for e in lines) or any(e['tag'] in ('path', 'polygon') and e['fill'] not in ('none', 'rgba(0, 0, 0, 0)') and e['w'] < 12 and e['h'] < 12 for e in self.children.get(gid, []))
            se = spec_edges.get(gid)
            if not has_head and (se is None or se.get('head', 'filled') != 'none'):
                self.add('warn', 'edge.nohead', f'{gid} has no arrowhead (marker-end or a small filled triangle)', [gid])
            # crossing boxes it does not connect
            for nid, b in nb.items():
                if nid in (f'n:{frm}', f'n:{to}'): continue
                inner = (b[0] + 1, b[1] + 1, b[2] - 1, b[3] - 1)
                if sum(1 for p in pts if inner[0] < p[0] < inner[2] and inner[1] < p[1] < inner[3]) >= 3:
                    self.add('warn', 'edge.crosses', f'{gid} runs through {nid}', [gid, nid], b)

    def check_colour(self):
        fills = {}; strokes = set(); widths = set()
        for e in self.els:
            if e['tag'] in SHAPES and e['fill'] not in ('none', 'rgba(0, 0, 0, 0)') and e['w'] > 2 and e['h'] > 2:
                c = rgb(e['fill'])
                if c and not (c[0] > 245 and c[1] > 245 and c[2] > 245): fills[tuple(int(v) for v in c)] = fills.get(tuple(int(v) for v in c), 0) + 1
            if e['tag'] in SHAPES + LINES and e['stroke'] != 'none' and e['strokeWidth'] > 0:
                widths.add(round(e['strokeWidth'] * 4) / 4)
        colours = [c for c in fills if not is_grey(c)]
        mx = self.thr.get('lint', {}).get('max_fill_colours', 12)
        if len(colours) > mx: self.add('warn', 'colour.count', f'{len(colours)} distinct non-grey fills (good figures: median 6, p95 {mx}); merge roles')
        sat = [c for c in colours if saturated(c)]
        msat = self.thr.get('lint', {}).get('max_saturated_fills', 2)       # a named style may allow more (references/styles/)
        if len(sat) > msat: self.add('warn', 'colour.saturated', f'{len(sat)} saturated fills {["#%02x%02x%02x" % c for c in sat]}; keep saturated colour for the accent only (≤ {msat})')
        if len(widths) > 3: self.add('warn', 'stroke.widths', f'{len(widths)} distinct stroke widths {sorted(widths)}; use 2 (box 0.5–0.75, main path 1–1.5)')
        for w in widths:
            if w < 0.3: self.add('warn', 'stroke.thin', f'stroke width {w} pt is hairline-thin (< 0.3 pt) and may vanish in print')
            if w > 2.5: self.add('warn', 'stroke.thick', f'stroke width {w} pt is heavy (> 2.5 pt)')

    def check_style(self):
        """Named style (spec meta.style, references/styles/<style>.json): advisory checks that the figure carries the
        style's signature -- bold labels, dark outlines on every box, box / frame stroke bands. Print floors are
        checked elsewhere and are never relaxed here."""
        st = self.thr.get('style')
        if not st: return
        name, t = st.get('style'), st.get('lint', {})
        summary = []
        texts = [e for e in self.texts if kind_of(self.groups.get(e.get('parentGroup') or '', {})) != 'step']
        if texts and t.get('bold_text_share_min'):
            def bold(e):
                w = str(e.get('fontWeight') or '400')
                return w in ('bold', 'bolder') or (w.isdigit() and int(w) >= 600)
            nb = sum(1 for e in texts if bold(e)); share = nb / len(texts)
            summary.append(f'labels bold {nb}/{len(texts)} ({"ok" if share >= t["bold_text_share_min"] else "below"} {t["bold_text_share_min"]:.0%})')
            if share < t['bold_text_share_min']:
                self.add('warn', 'style.weight', f'{share:.0%} of labels are bold; style {name} sets labels bold '
                         f'(≥ {t["bold_text_share_min"]:.0%}) -- font-weight="bold" on the root or the label groups')
        nodes = [g for g in self.by_kind.get('node', {}) if not self.is_picture_box(g)]
        shapes = [(g, self.explicit_shape(g)) for g in nodes]
        shapes = [(g, e) for g, e in shapes if e is not None and e['tag'] != 'image']
        if shapes and t.get('outlined_node_share_min'):
            lmax = t.get('outline_max_lightness', 0.35)
            def dark(e):
                c = rgb(e['stroke']) if e['stroke'] != 'none' and e['strokeWidth'] > 0 else None
                return c is not None and max(c) / 255 <= lmax + 0.25 and sum(c) / 765 <= lmax
            bare = [g for g, e in shapes if not dark(e)]
            ok_out = 1 - len(bare) / len(shapes) >= t['outlined_node_share_min']
            summary.append(f'boxes outlined in ink {len(shapes) - len(bare)}/{len(shapes)} ({"ok" if ok_out else "below"} {t["outlined_node_share_min"]:.0%})')
            if not ok_out:
                self.add('warn', 'style.outline', f'{len(bare)}/{len(shapes)} boxes have no dark outline; style {name} '
                         f'outlines every box in ink (palette stroke)', bare[:8])
        lo, hi = t.get('stroke_box_pt', (0, 99))
        odd = sorted({round(e['strokeWidth'], 2) for g, e in shapes if e['stroke'] != 'none' and not lo <= e['strokeWidth'] <= hi})
        if odd: self.add('info', 'style.stroke', f'box outlines {odd} pt; style {name} uses {lo}–{hi} pt (frames {t.get("stroke_frame_pt")})')
        # always say that the style was checked, so a clean run is visibly a checked one (check.py repeats it)
        self.add('info', 'style.checked', f'style {name}: ' + ('; '.join(summary) or 'nothing to check'))

    def check_density(self):
        n = len({self.base_id(g) for g in self.by_kind.get('node', {})} if self.mech else self.by_kind.get('node', {}))
        col = (self.spec.get('meta') or {}).get('column') or ('double' if self.W >= 380 else 'single')
        if self.composite:
            # a composite figure (panels[] with axis "part") is several figures in one frame: hold each part to the
            # single-column budget, which is roughly the area a part gets, instead of the whole figure to one budget
            bud = self.thr.get('lint', {}).get('node_budget', {}).get('single', {})
            per = {}
            for g in self.by_kind.get('node', {}):
                # mechanism bands count labels, not copies: identical rows (Attention on every GPU) count once
                lab = ' '.join(t['text'] for t in self.texts_of(g)).strip().lower() if self.mech else ''
                per.setdefault(self.part_of(self.panel_scope(g)) or '(none)', set()).add(lab or self.base_id(g))
            for part, ids in sorted(per.items()):
                if bud and len(ids) > bud.get('p90', 99):
                    self.add('warn', 'density.nodes', f'part {part} has {len(ids)} labelled boxes, above the single-column p90 {bud["p90"]} '
                             f'that each part of a composite figure gets; merge repeated boxes (one tall box for identical rows, ×N) or move numbers to the caption')
            self.add('info', 'density.nodes', f'composite figure: {n} labelled boxes in {len(per)} part(s) ' +
                     ', '.join(f'{k} {len(v)}' for k, v in sorted(per.items())))
            return
        bud = self.thr.get('lint', {}).get('node_budget', {}).get(col, {})
        if bud and n > bud.get('p90', 99): self.add('warn', 'density.nodes', f'{n} labelled boxes exceed the {col}-column p90 budget {bud["p90"]}; merge or split the figure')
        elif bud and n > bud.get('q3', 99): self.add('info', 'density.nodes', f'{n} labelled boxes is above the {col}-column q3 budget {bud["q3"]}')

    def check_spec(self):
        if not self.spec: return
        def has(gid): return gid in self.groups or (self.mech and bool(self.copies(gid)))
        for n in self.spec.get('nodes') or []:
            gid = f"n:{n['id']}"
            if not has(gid): self.add('error', 'spec.missing', f'spec node {n["id"]} has no <g id="{gid}">' + (' (nor a per-panel copy n:%s@<panel>)' % n['id'] if self.mech else ''), [gid]); continue
            lab = re.sub(r'\s+', ' ', n.get('label', '')).strip().lower()
            if not lab: continue
            for g in (self.copies(gid) if self.mech else [gid]):
                texts = ' '.join(t['text'] for t in self.texts_of(g)).lower()
                if lab not in texts and not all(w in texts for w in lab.split()):
                    self.add('warn', 'spec.label', f'{g} text "{texts[:40]}" does not match spec label "{n["label"]}"', [g])
        for c in self.spec.get('containers') or []:
            if not has(f"c:{c['id']}"): self.add('error', 'spec.missing', f'spec container {c["id"]} has no <g id="c:{c["id"]}">')
        for l in self.spec.get('lanes') or []:
            if not has(f"l:{l['id']}"): self.add('error', 'spec.missing', f'spec lane {l["id"]} has no <g id="l:{l["id"]}">')
        for e in self.spec.get('edges') or []:
            gid = f"e:{e['id']}"
            if not has(gid): self.add('error', 'spec.missing', f'spec edge {e["id"]} ({e.get("from")}→{e.get("to")}) has no <g id="{gid}">'); continue
            for gg in (self.copies(gid) if self.mech else [gid]):
                g = self.groups[gg]
                if g['attrs'].get('data-from') and g['attrs']['data-from'] != e.get('from'): self.add('warn', 'spec.edge', f'{gg} data-from={g["attrs"]["data-from"]} but spec says {e.get("from")}')
        for s in self.spec.get('steps') or []:
            if not has(f"s:{s['n']}"): self.add('error', 'spec.missing', f'spec step {s["n"]} has no <g id="s:{s["n"]}">')
        leg = (self.spec.get('legend') or {}).get('mode', 'none')
        if leg not in ('none', None) and not has('legend'): self.add('error', 'spec.missing', 'spec asks for a legend but there is no <g id="legend">')
        # bitmaps: a node whose spec names one (nodes[].image / kind image) draws an <image>; a drawn one is declared
        declared = set()
        for n in self.spec.get('nodes') or []:
            if not (isinstance(n, dict) and (n.get('image') or n.get('kind') == 'image')): continue
            declared.add(f"n:{n['id']}")
            for g in (self.copies(f"n:{n['id']}") if self.mech else [f"n:{n['id']}"]):
                if g in self.groups and not self.has_image(g):
                    self.add('warn', 'spec.image', f'spec node {n["id"]} shows a bitmap ({(n.get("image") or {}).get("src") or "kind image"}) '
                             f'but {g} draws no <image>', [g])
        for g in self.by_kind.get('node', {}):
            if self.has_image(g) and self.base_id(g) not in declared:
                self.add('info', 'spec.image', f'{g} draws an <image> that its spec node does not declare (nodes[].image with src and content)', [g])
        spec_ids = {f"n:{n['id']}" for n in self.spec.get('nodes') or []} | {f"e:{e['id']}" for e in self.spec.get('edges') or []} | \
                   {f"c:{c['id']}" for c in self.spec.get('containers') or []} | {f"l:{l['id']}" for l in self.spec.get('lanes') or []}
        extra = [g for g in self.groups if kind_of(self.groups[g]) in ('node', 'edge', 'container', 'lane') and self.base_id(g) not in spec_ids and '~' not in g]
        if extra: self.add('warn', 'spec.extra', f'{len(extra)} drawn elements are not in the spec: {extra[:8]}; add them to the spec or remove them')

    # ---- 2026-09-10 additions: glyph coverage, arrowhead / tail collisions, replica ledges, title & gutter centring
    def _markers(self):
        """marker id -> (markerWidth, markerUnits) from the SVG source, for arrowhead lengths."""
        out = {}
        for m in re.finditer(r'<marker\b([^>]*)>', self.svg_text):
            attrs = dict(re.findall(r'([\w:-]+)\s*=\s*"([^"]*)"', m.group(1)))
            if attrs.get('id'):
                try: mw = float(attrs.get('markerWidth', 3) or 3)
                except ValueError: mw = 3.0
                out[attrs['id']] = (mw, attrs.get('markerUnits', 'strokeWidth'))
        return out

    def _head_len(self, el, which):
        m = re.search(r'#([^)"\']+)', el.get(which) or '')
        mw, units = self.markers.get(m.group(1), (3.0, 'strokeWidth')) if m else (3.0, 'strokeWidth')
        return mw * (el.get('strokeWidth') or 1.0) if units != 'userSpaceOnUse' else mw

    def check_glyphs(self):
        if not self.svg_text: return
        try:
            unc, faces = K.glyph_coverage(self.svg_text)
        except Exception as ex:
            self.add('info', 'font.glyph', f'glyph coverage not checked: {ex!r}'); return
        if unc is None: self.add('info', 'font.glyph', 'glyph coverage not checked (pip install fonttools)'); return
        if unc:
            shown = ' '.join(f'{c}(U+{ord(c):04X})' for c in unc[:8]) + (' …' if len(unc) > 8 else '')
            self.add('warn', 'font.glyph', f'{len(unc)} character(s) are in no shipped/embedded face: {shown}; they fall back to a system font '
                     f'(different or missing elsewhere) — draw them as shapes (dots, arrows) or pick a face that has them')

    def check_heads(self):
        t = self.thr.get('lint', {}); clear = t.get('head_clear_pt', 0.4); tail_clear = t.get('tail_clear_pt', 3.0)
        lines = [e for e in self.els if e['tag'] in LINES and e.get('points') and e['stroke'] != 'none' and (e['tag'] in ('line', 'polyline') or e['fill'] in ('none', 'rgba(0, 0, 0, 0)'))]
        for gid, g in self.by_kind.get('edge', {}).items():
            mine = [e for e in self.children.get(gid, []) if e['tag'] in LINES and e.get('points')]
            if not mine: continue
            main = max(mine, key=lambda e: e.get('length', 0)); pts = main['points']
            frm, to = g['attrs'].get('data-from'), g['attrs'].get('data-to')
            own = {gid} | {f'{p}{x}' for x in (frm, to) if x for p in ('n:', 'c:', 'l:')}
            others = [ln for ln in lines if ln.get('parentGroup') not in own and ln is not main]
            heads = []
            if main.get('markerEnd'): heads.append(('head', pts[-1], pts[::-1], self._head_len(main, 'markerEnd')))
            if main.get('markerStart'): heads.append(('start head', pts[0], pts, self._head_len(main, 'markerStart')))
            for name, tip, seq, hl in heads:
                base, acc = tip, 0.0
                for a, b in zip(seq, seq[1:]):
                    d = math.hypot(b[0] - a[0], b[1] - a[1])
                    if acc + d >= hl:
                        f = (hl - acc) / d if d else 0.0; base = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f); break
                    acc += d; base = b
                # the head is a triangle from tip to base: a foreign line "overlaps" it when a sample point lies between
                # tip and base along the axis (5–97 %) and within the triangle's half-width there (+ clearance);
                # a line tangent to the base or beyond it is not a collision
                ax, ay = base[0] - tip[0], base[1] - tip[1]; L2 = ax * ax + ay * ay or 1e-9
                def in_head(q):
                    t = ((q[0] - tip[0]) * ax + (q[1] - tip[1]) * ay) / L2
                    if not 0.05 <= t <= 0.97: return False
                    d = seg_dist(q, tip, base)
                    return d <= 0.5 * hl * t + clear
                rad = 0.5 * hl + clear
                for ln in others:
                    hit = next((q for q in ln['points'] if in_head(q)), None)
                    if hit:
                        who = ln.get('parentGroup') or ln.get('id') or 'a line'
                        bb = (min(tip[0], base[0]) - rad, min(tip[1], base[1]) - rad, max(tip[0], base[0]) + rad, max(tip[1], base[1]) + rad)
                        self.add('warn', 'edge.head-overlap', f'{name} of {gid} overlaps {who} at ({hit[0]:.0f},{hit[1]:.0f}); move that rule or the box row so the head clears it', [gid, ln.get('parentGroup')], bb)
                        break
            tails = ([('tail', pts[0])] if not main.get('markerStart') else []) + ([('end', pts[-1])] if not main.get('markerEnd') else [])
            for name, p in tails:
                for ln in others:
                    dmin = min(math.hypot(q[0] - p[0], q[1] - p[1]) for q in ln['points'])
                    if dmin <= tail_clear:
                        who = ln.get('parentGroup') or ln.get('id') or 'a line'
                        self.add('warn', 'edge.tail-near-line', f'{name} of {gid} is {dmin:.1f} pt from {who}; start the edge on its box, clear of rules and other edges', [gid, ln.get('parentGroup')], (p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2))
                        break

    def check_replicas(self):
        tol = self.thr.get('lint', {}).get('replica_step_tol_pt', 0.35)
        for gid in self.by_kind.get('node', {}):
            rects = [e for e in self.children.get(gid, []) if e['tag'] == 'rect' and not e.get('inSymbol') and e['w'] > 4 and e['h'] > 4]
            if len(rects) < 2: continue
            big = max(rects, key=lambda e: area(box(e)))
            cards = [e for e in rects if abs(e['w'] - big['w']) <= max(1.5, 0.15 * big['w']) and abs(e['h'] - big['h']) <= max(1.5, 0.15 * big['h'])]   # near-copies (a 2 pt larger front card is the classic mistake)
            if len(cards) < 2: continue
            front = max(cards, key=lambda e: e['idx'])                   # drawn last = on top
            fb = box(front); probs = []
            for name, fn, beyond in (('right', lambda b: b[2], lambda b: b[2] > fb[2] + 0.2), ('bottom', lambda b: b[3], lambda b: b[3] > fb[3] + 0.2),
                                     ('left', lambda b: b[0], lambda b: b[0] < fb[0] - 0.2), ('top', lambda b: b[1], lambda b: b[1] < fb[1] - 0.2)):
                vis = [box(e) for e in cards if e is not front and beyond(box(e))]
                if not vis: continue
                vals = sorted([fn(fb)] + [fn(b) for b in vis]); steps = [round(abs(b - a), 2) for a, b in zip(vals, vals[1:])]
                if steps and max(steps) - min(steps) > tol: probs.append(f'{name} ledges {steps} pt')
            if probs:
                self.add('warn', 'replica.step', f'stacked copies in {gid} are unevenly offset: {"; ".join(probs)}; keep every card the same size and step them by one constant (dx, dy)', [gid], box(self.groups[gid]))

    def check_titles(self):
        t = self.thr.get('lint', {}); ttol = t.get('title_centre_tol_pt', 1.5); gtol = t.get('gutter_centre_tol_pt', 1.5)
        boxes = {gid: self.shape_of(gid) for gid in list(self.by_kind.get('node', {})) + list(self.by_kind.get('container', {}))}
        parent = {}
        for n in (self.spec.get('nodes') or []): parent[f"n:{n['id']}"] = n.get('parent')
        for c in (self.spec.get('containers') or []): parent[f"c:{c['id']}"] = c.get('parent')
        for gid in list(self.by_kind.get('container', {})) + list(self.by_kind.get('lane', {})):
            is_lane = kind_of(self.groups[gid]) == 'lane'; cb = self.band_of(gid) if is_lane else self.shape_of(gid); ts = self.texts_of(gid)
            if not ts: continue
            kids = []
            for k, b in boxes.items():
                if k == gid or inside(cb, b, -0.5): continue                  # skip itself and any box that contains it (its parent)
                if parent.get(k) == gid[2:]: kids.append(b); continue
                if is_lane:
                    ov = min(b[3], cb[3]) - max(b[1], cb[1])
                    if ov > 0 and (ov >= 0.5 * (b[3] - b[1]) or ov >= 0.5 * (cb[3] - cb[1])) and b[0] >= cb[0] - 0.5 and b[2] <= cb[2] + 0.5: kids.append(b)
                elif inside(b, cb, -0.5) and area(b) < 0.9 * area(cb): kids.append(b)
            if not kids: continue
            for tx in ts:
                tb = self.tbox(tx)
                rotated = bool(tx.get('rotated')) or ((tb[3] - tb[1]) > 1.8 * (tb[2] - tb[0]) and len(tx.get('text', '')) > 1)
                if rotated:
                    right = [b for b in kids if b[0] > tb[2] - 0.5]; left = [b for b in kids if b[2] < tb[0] + 0.5]
                    if right and len(right) == len(kids): lo, hi = cb[0], min(b[0] for b in right)
                    elif left and len(left) == len(kids): lo, hi = max(b[2] for b in left), cb[2]
                    else: continue
                    mid = (lo + hi) / 2; c = (tb[0] + tb[2]) / 2
                    if hi - lo >= 6 and abs(c - mid) > gtol:
                        self.add('warn', 'gutter.centre', f'rotated label "{tx["text"][:20]}" of {gid} sits {c - mid:+.1f} pt off the centre of its gutter ({lo:.0f}–{hi:.0f}); shift it by {mid - c:+.1f} pt', [gid], tb)
                else:
                    below = [b for b in kids if b[1] >= tb[3] - 0.5]
                    if below and len(below) == len(kids) and tb[1] >= cb[1] - 0.5:
                        lo, hi = cb[1], min(b[1] for b in below); mid = (lo + hi) / 2; c = (tb[1] + tb[3]) / 2
                        if hi - lo >= 6 and abs(c - mid) > ttol:
                            self.add('warn', 'title.centre', f'title "{tx["text"][:20]}" of {gid} sits {c - mid:+.1f} pt off the centre of its headroom ({lo:.0f}–{hi:.0f}); shift it by {mid - c:+.1f} pt', [gid], tb)

    # ---- 2026-09-28 bitmaps: allowed (a sample, photo, screenshot, rendered result, icon); the link must be local
    #      (embed_fonts.py inlines it at delivery) and the picture print-ready
    def check_images(self):
        refs = K.image_refs(self.svg_text)
        if not refs: return
        t = self.thr.get('lint', {}); ppi_min = t.get('image_ppi_warn', 150); ppi_heavy = t.get('image_ppi_heavy', 600)
        heavy_kb = t.get('image_heavy_kb', 200); tol = t.get('image_aspect_tol', 0.02)
        measured = {}
        for e in self.d['elements']:
            k = (e.get('attrs') or {}).get('data-img') if e['tag'] == 'image' else None
            if k is not None and k.isdigit(): measured[int(k)] = e
        root = K._SVG_OPEN.search(self.svg_text)
        if any(r['attr'] == 'xlink:href' for r in refs) and root and 'xmlns:xlink' not in root.group(0):
            self.add('error', 'image.xmlns', 'xlink:href is used but the root <svg> does not declare xmlns:xlink="http://www.w3.org/1999/xlink": '
                     'every XML tool (Inkscape, Office, the PowerPoint export) rejects the file -- declare it, or write plain href')
        for r in refs:
            e = measured.get(r['k']); name = r['name']; ids = [r['owner']]; bb = box(e) if e else None
            if r['kind'] == 'external':
                self.add('error', 'image.external', f'{name} links to {r["href"][:70]}: a figure never depends on a remote file -- download it '
                         f'into the figure folder (check its licence) and link it by a relative path; embed_fonts.py inlines it at delivery', ids, bb)
                continue
            try:
                data, _ = K.load_image(r['href'], self.base_dir)
            except K.ImageError as ex:
                self.add('error', 'image.missing', f'{name} {ex}', ids, bb); continue
            info = K.image_info(data); fmt = info['format']
            if fmt not in K.IMAGE_FORMATS:
                how = ('an SVG drawn as a picture is a sealed box (fonts not embedded, text not linted or editable): copy its elements into the figure'
                       if fmt == 'svg' else 'save it as PNG (screenshots, renders, icons, flat colour, text) or JPEG (photos); '
                       'other formats do not survive every SVG viewer or the PowerPoint export')
                self.add('error', 'image.format', f'{name} is {fmt.upper() if fmt else "not a known image format"}, not PNG or JPEG: {how}', ids, bb); continue
            if not info['w']:
                self.add('error', 'image.missing', f'{name} ({r["href"][:60]}) cannot be decoded as {fmt.upper()}', ids, bb); continue
            w_attr, h_attr = (float((K.NUM.match((r['attrs'].get(a) or '').strip()) or [0])[0]) for a in ('width', 'height'))
            if w_attr <= 0 or h_attr <= 0:
                self.add('error', 'image.box', f'{name} has no positive width / height: SVG 1.1 viewers (Office, older editors) draw it at zero size '
                         f'and newer ones at {info["w"]} × {info["h"]} pt -- give both, in pt', ids, bb); continue
            if info['orientation'] != 1:
                self.add('warn', 'image.orientation', f'{name} carries an EXIF rotation ({info["orientation"]}) that some viewers apply and some ignore; '
                         f'save it upright (Pillow: ImageOps.exif_transpose)', ids, bb)
            g = (e or {}).get('img') or {}
            pw, ph = (g.get('w') or w_attr) * (g.get('sx') or 1.0), (g.get('h') or h_attr) * (g.get('sy') or 1.0)   # print size in pt
            if pw <= 0 or ph <= 0: continue
            align, mode = K.parse_par(r['attrs'].get('preserveAspectRatio'))
            fx, fy = pw / info['w'], ph / info['h']                       # pt per pixel along each axis
            per_px = max(fx, fy) if align == 'none' else (min(fx, fy) if mode == 'meet' else max(fx, fy))
            ppi = 72.0 / per_px
            shown = f'{info["w"]} × {info["h"]} px in {pw:.0f} × {ph:.0f} pt'
            if ppi < ppi_min:
                self.add('warn', 'image.resolution', f'{name} is {ppi:.0f} ppi at print size ({shown}); below {ppi_min} ppi it prints soft or '
                         f'pixelated -- use a larger source or draw it smaller (aim for 300 ppi, photos especially)', ids, bb)
            elif ppi > ppi_heavy and len(data) > heavy_kb * 1024:
                self.add('info', 'image.heavy', f'{name} is {ppi:.0f} ppi at print size ({shown}, {len(data) / 1024:.0f} KB): 300 ppi is plenty; '
                         f'downsample it to keep the delivered SVG small', ids, bb)
            ratio = (info['w'] / info['h']) / (pw / ph)
            if abs(ratio - 1) > tol:
                pic = f'{info["w"]}:{info["h"]}'
                if align == 'none':
                    self.add('warn', 'image.aspect', f'{name} is stretched: the picture is {pic} but its box is {pw:.1f}:{ph:.1f} pt and '
                             f'preserveAspectRatio="none" distorts it -- give the box the picture\'s proportions', ids, bb)
                elif mode == 'meet':
                    self.add('warn', 'image.aspect', f'{name} fills only {min(ratio, 1 / ratio):.0%} of its box (the picture is {pic}, the box '
                             f'{pw:.1f}:{ph:.1f} pt), leaving empty bands inside the frame -- give the box the picture\'s proportions, '
                             f'or crop on purpose with preserveAspectRatio="xMidYMid slice"', ids, bb)
                else:
                    self.add('info', 'image.aspect', f'{name} is cropped to its box (slice): {1 - min(ratio, 1 / ratio):.0%} of the picture is hidden', ids, bb)

    # ---- 2026-09-20 mechanism figures (meta.kind = mechanism): SVG-vs-spec consistency only, all warn / info
    def check_mechanism(self):
        if not self.mech: return
        spec = self.spec
        panels = [p for p in (spec.get('panels') or []) if isinstance(p, dict) and p.get('id')]
        pbox = {}
        for p in panels:
            gid = f"p:{p['id']}"
            if gid not in self.groups:
                self.add('warn', 'panel.missing', f'spec panel {p["id"]} has no <g id="{gid}" data-kind="panel"> wrapping its elements', [gid]); continue
            pbox[p['id']] = self.shape_of(gid)
        def panel_of(g):
            a = self.groups[g].get('attrs') or {}
            return a.get('data-panel') or (g.split('@', 1)[1] if '@' in g else None)
        boxes = {g: (self.frame_of(g) if k == 'lane' else self.shape_of(g)) for k in ('node', 'container', 'lane') for g in self.by_kind.get(k, {})}
        spec_panel = {}
        for arr, pre in (('nodes', 'n:'), ('containers', 'c:'), ('lanes', 'l:'), ('annotations', 'a:')):
            for x in spec.get(arr) or []:
                if isinstance(x, dict) and x.get('panel'): spec_panel[pre + x['id']] = x['panel']
        for g, b in boxes.items():
            pid = spec_panel.get(self.base_id(g)) or panel_of(g)
            if pid and pid in pbox and not inside(b, pbox[pid], -0.5):
                self.add('warn', 'panel.member', f'{g} belongs to panel {pid} but is drawn outside p:{pid}', [g, f'p:{pid}'], b)
        ft = ((spec.get('meta') or {}).get('mechanism') or {}).get('frame_template')
        # panels that repeat one template: siblings under the same parent (top level: no parent) that are not the parts
        # of a composite figure. Template elements of a sibling group are the nodes declared on its parent panel (top
        # level: the nodes without a panel).
        sibs = {}
        for q in panels:
            if q['id'] in pbox and q.get('axis', 'alternatives') != 'part': sibs.setdefault(q.get('parent'), []).append(q['id'])
        for par, members in sibs.items():
            if len(members) < 2: continue
            mbox = {pid: pbox[pid] for pid in members}
            for n in spec.get('nodes') or []:
                if not isinstance(n, dict) or (n.get('panel') != par if par else n.get('panel')): continue
                tid = f"n:{n['id']}"
                cop = {panel_of(g): boxes[g] for g in boxes if self.base_id(g) == tid and panel_of(g) in mbox}
                if tid in boxes:
                    for pid, pb in mbox.items():
                        if inside(boxes[tid], pb, -0.5): cop.setdefault(pid, boxes[tid])
                if not cop: continue
                missing = [pid for pid in mbox if pid not in cop]
                if missing:
                    self.add('info', 'panel.copy', f'template element {tid} has no copy in panel(s) {missing} -- fine when those panels leave it out on purpose', [tid])
                if ft == 'identical' and len(cop) >= 2:
                    offs = {pid: (b[0] - mbox[pid][0], b[1] - mbox[pid][1]) for pid, b in cop.items()}
                    ref_pid, ref = next(iter(offs.items()))
                    for pid, o in offs.items():
                        if max(abs(o[0] - ref[0]), abs(o[1] - ref[1])) > 1.0:
                            self.add('warn', 'panel.identical', f'{tid} sits {o[0] - ref[0]:+.1f},{o[1] - ref[1]:+.1f} pt from where it is in panel {ref_pid}; frame_template is identical, so keep template elements at the same offset in every panel (or say aligned / free)', [f'{tid}@{pid}'], cop[pid])
        for d in spec.get('deltas') or []:
            if not isinstance(d, dict): continue
            tgt, pid = d.get('target'), d.get('panel')
            cands = [g for g in self.groups if self.base_id(g)[2:] == tgt and (panel_of(g) == pid or (panel_of(g) is None and spec_panel.get(self.base_id(g)) in (pid, None)))]
            if not cands:
                if d.get('change') != 'removed':
                    self.add('warn', 'delta.target', f'delta {d["id"]} ({d.get("change")} {tgt} in {pid}) has no drawn element: expected n:{tgt}@{pid} or n:{tgt} with panel {pid}')
            elif not any((self.groups[g].get('attrs') or {}).get('data-delta') for g in cands):
                self.add('warn', 'delta.unmarked', f'delta {d["id"]} ({d.get("change")} {tgt} in {pid}): {cands[0]} carries no data-delta="{d["id"]}"; tag the changed element so the change stays findable and editable', cands[:1])
        for v in spec.get('values') or []:
            if isinstance(v, dict) and v.get('id') and f"v:{v['id']}" not in self.groups:
                self.add('warn', 'value.missing', f'spec value {v["id"]} ("{v.get("text", "")}") has no <g id="v:{v["id"]}" data-kind="value">')
        for e in spec.get('edges') or []:
            if not isinstance(e, dict) or not e.get('guard'): continue
            want = re.sub(r'\s+', ' ', e['guard']).strip().lower()
            for g in self.copies(f"e:{e['id']}"):
                texts = ' '.join(x['text'] for x in self.texts_of(g)).lower()
                if want not in texts and not all(w in texts for w in want.split()):
                    self.add('warn', 'guard.unlabelled', f'{g} does not draw its guard "{e["guard"]}" (a <text> inside the edge group); unlabelled transitions and branches are the most common logic-figure fault', [g])

    def run(self):
        for fn in (self.check_canvas, self.check_bleed, self.check_fonts, self.check_glyphs, self.check_text, self.check_overflow, self.check_overlap,
                   self.check_contain, self.check_align, self.check_centre, self.check_edges, self.check_heads, self.check_replicas, self.check_titles,
                   self.check_images, self.check_colour, self.check_style, self.check_density, self.check_spec, self.check_mechanism):
            try: fn()
            except Exception as ex:  # a failing check must not hide the others
                self.add('info', 'lint.internal', f'{fn.__name__} failed: {ex!r}')
        order = {'error': 0, 'warn': 1, 'info': 2}
        self.f.sort(key=lambda x: (order[x['severity']], x['code']))
        return self.f


def annotate(svg_text, findings, out):
    vb = K.parse_viewbox(svg_text) or [0, 0, 300, 200]
    layer = ['<g id="lint-overlay" pointer-events="none" font-family="Arimo, Arial, sans-serif">']
    k = 0
    for f in findings:
        if not f.get('bbox'): continue
        b = f['bbox']; col = {'error': '#e00000', 'warn': '#ff8c00', 'info': '#2f7bd6'}[f['severity']]; k += 1
        layer.append(f'<rect x="{b[0] - 0.5:.2f}" y="{b[1] - 0.5:.2f}" width="{max(1, b[2] - b[0] + 1):.2f}" height="{max(1, b[3] - b[1] + 1):.2f}" fill="{col}" fill-opacity="0.12" stroke="{col}" stroke-width="0.6" stroke-dasharray="1.5 1"/>')
        ly = max(4, b[1] - 1) if k % 2 else min(vb[3] - 1, b[3] + 4)
        layer.append(f'<text x="{b[0]:.2f}" y="{ly:.2f}" font-size="3.5" fill="{col}">{k} {f["code"]}</text>')
    layer.append('</g>')
    out_svg = re.sub(r'</svg>\s*$', '\n'.join(layer) + '\n</svg>', svg_text.rstrip())
    Path(out).write_text(out_svg, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('svg'); ap.add_argument('--spec'); ap.add_argument('--thresholds', default=str(DEFAULT_THRESH))
    ap.add_argument('--report'); ap.add_argument('--annotate'); ap.add_argument('--strict', action='store_true'); ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    svg = Path(a.svg).read_text(encoding='utf-8')
    spec = json.loads(Path(a.spec).read_text(encoding='utf-8')) if a.spec else None
    thr = json.loads(Path(a.thresholds).read_text(encoding='utf-8')) if Path(a.thresholds).exists() else {}
    if (spec or {}).get('meta', {}).get('kind') == 'mechanism' and a.thresholds == str(DEFAULT_THRESH) and MECH_THRESH.exists():
        # mechanism figures: column bands from the mechanism corpus, lint parameters shared, budgets label-distinct
        mech = json.loads(MECH_THRESH.read_text(encoding='utf-8'))
        thr = dict(thr); thr['columns'] = mech.get('columns', thr.get('columns', {}))
        thr['lint'] = dict(thr.get('lint', {})); thr['lint']['node_budget'] = MECH_NODE_BUDGET
    style = ((spec or {}).get('meta') or {}).get('style')
    if style and style != 'corpus':                                      # named style: references/styles/<style>.json
        sp = SKILL / 'references' / 'styles' / f'{style}.json'
        if sp.exists():
            sj = json.loads(sp.read_text(encoding='utf-8'))
            thr = dict(thr); thr['style'] = sj
            thr['lint'] = dict(thr.get('lint', {}))
            if 'max_saturated_fills' in sj.get('lint', {}): thr['lint']['max_saturated_fills'] = sj['lint']['max_saturated_fills']
        else:
            print(f'lint: unknown style {style!r} (no {sp.relative_to(SKILL)}); linting with the default rules', file=sys.stderr)
    thr.setdefault('lint', {}).setdefault('node_budget', {'single': {'q3': 13, 'p90': 17}, 'double': {'q3': 20, 'p90': 24}})
    here = Path(a.svg).resolve().parent                                 # relative <image> links resolve against the SVG's folder
    data = K.measure(svg, base_dir=here)
    findings = Lint(data, spec, thr, svg_text=svg, base_dir=here).run()
    ne = sum(1 for f in findings if f['severity'] == 'error'); nw = sum(1 for f in findings if f['severity'] == 'warn')
    rep = dict(svg=str(a.svg), spec=a.spec, width=data['W'], height=data['H'], errors=ne, warnings=nw, findings=findings)
    if a.report: Path(a.report).write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding='utf-8')
    if a.annotate: annotate(svg, findings, a.annotate)
    if not a.quiet:
        print(f'{a.svg}: {data["W"]:.0f}×{data["H"]:.0f} pt, {len(data["elements"])} elements — {ne} error(s), {nw} warning(s)')
        for f in findings:
            if f['severity'] == 'info' and ne + nw > 25: continue
            print(f'  [{f["severity"]:5s}] {f["code"]:18s} {f["message"]}')
    sys.exit(1 if ne or (a.strict and nw) else 0)


if __name__ == '__main__':
    main()
