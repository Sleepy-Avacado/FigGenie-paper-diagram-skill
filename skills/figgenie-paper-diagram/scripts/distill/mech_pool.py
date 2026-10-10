#!/usr/bin/env python3
"""Build a mechanism-figure PARTS-MINING package for the reviewing sub agents (mechanism kind, step 5b).

The architecture library was mined by detectors (extract_parts.py) and then reviewed. Mechanism figures
carry mostly *narrative devices* (ghost copies, frame arrows, delta highlights, slot arrays, guarded
edges ...) that no detector finds reliably, so here the agent drives: it looks at every figure on a
print-pt GRID render and asks cut_parts.py for the regions it wants. This script prepares everything
the agent needs, one directory per figure:

  <out>/figs/<fig_id>/info.json          caption, v3 groups, prescreen attributes, files + print scale
  <out>/figs/<fig_id>/render_<k>.png     source file k rendered at print size with a labelled pt grid
  <out>/figs/<fig_id>/candidates_N.png   (optional) detector candidates found in this figure, numbered
  <out>/figs/<fig_id>/candidates.json    tile number -> candidate id / svg / thumb
  <out>/pool/                            the raw extract_parts.py pool (candidates.jsonl, svg/, thumbs/)
  <out>/agents/agent_<n>/figures.json    the figures assigned to each agent (stratified by base + tool)
  <out>/figures.json                     every selected figure with its assignment

Coordinates: every grid label and every bbox handed to cut_parts.py is in PRINT POINTS of that source
file, origin at the top-left corner of the file's `frame_src` (the ink bbox + 2 pt; x_pt = (x_src -
frame_x0) * scale). Multi-file figures have one render and one coordinate frame per file. The print
scale comes from matching label positions against the print-size PDF export of the same figure
(`text-match`), else from fitting the ink box to the printed size, else from extract_parts.pick_scale.

  python3 scripts/distill/mech_pool.py --group evolution --source src --out mech-parts/pilot-evolution --agents 2
  flags: --labels mech-prescreen/typedisc/labels_v3.jsonl  --prescreen mech-prescreen/prescreen.jsonl
         --any-group (membership instead of primary group)  --ids a,b  --limit N  --no-extract  --no-render
"""
import argparse, collections, csv, json, math, os, re, subprocess, sys, time
from pathlib import Path
from lxml import etree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import extract_parts as X          # noqa: E402  (geometry, scale inference, sheets)
import _svgkit as K                # noqa: E402  (fonts + html wrapper)

csv.field_size_limit(10 ** 9)
SVG_NS = 'http://www.w3.org/2000/svg'
ROOT = HERE.parents[2]             # repo root (figgenie-paper-diagram/scripts/distill -> repo)
FLAGS = ('check_cross', 'ghost_copy', 'delta_highlight', 'example_values', 'time_axis', 'before_after')


def load_inputs(a):
    labels = {}
    for line in open(a.labels, encoding='utf-8'):
        if line.strip():
            r = json.loads(line); labels[r['id']] = r
    pre = {}
    for line in open(a.prescreen, encoding='utf-8'):
        if line.strip():
            r = json.loads(line); pre[r['id']] = r
    index = {}
    for r in csv.DictReader(open(a.index, encoding='utf-8')):
        index['%s_fig%s' % (r['paper_id'], r['fig'])] = r
    return labels, pre, index


def select_ids(a, labels, index):
    want = set(x.strip() for x in a.ids.split(',') if x.strip()) if a.ids else None
    out = []
    for fid, r in labels.items():
        if want is not None and fid not in want: continue
        if a.group != 'all':
            ok = (a.group in r['groups']) if a.any_group else (r['primary'] == a.group)
            if not ok: continue
        row = index.get(fid)
        if not row: continue
        has_src = bool(row['src_svgs'].strip()); has_pdf = bool(row['pdf_svg'].strip())
        if a.source == 'src' and not has_src: continue
        if a.source == 'pdf' and (has_src or not has_pdf): continue
        if a.source == 'any' and not (has_src or has_pdf): continue
        out.append(fid)
    out.sort()
    return out[:a.limit] if a.limit else out


def figure_files(fid, row, extracted, source):
    """-> [(rel, path)], scale, note, source_kind  (mirrors extract_parts.select_figures)."""
    has_src = bool(row['src_svgs'].strip())
    if has_src and source != 'pdf':
        files = [f.strip() for f in row['src_svgs'].split('|') if f.strip()]; kind = 'src'
    else:
        files = [row['pdf_svg'].strip()]; kind = 'pdf'
    keep = [(f, os.path.join(extracted, row['paper_id'], f)) for f in files]
    keep = [(f, p) for f, p in keep if os.path.exists(p)]
    if not keep: return [], 1.0, 'missing', kind
    try: st = json.loads(row['style']) if row.get('style') else {}
    except json.JSONDecodeError: st = {}
    pw = (st.get('size') or {}).get('w'); ph = (st.get('size') or {}).get('h')
    if kind == 'pdf': return keep, 1.0, 'pdf', kind
    scale, note = X.pick_scale(pw, ph, [X.svg_size(p) for _f, p in keep])
    return keep, scale, note, kind


def source_viewbox(path):
    """(ox, oy, W, H) of the source root in its own user units."""
    head = open(path, encoding='utf-8', errors='replace').read(4000)
    m = X.VB_RE.search(head)
    if m:
        v = [float(x) for x in X.NUM_TOKEN.findall(m.group(1))]
        if len(v) >= 4 and v[2] > 0 and v[3] > 0: return v[0], v[1], v[2], v[3]
    w, h = X.svg_size(path)
    return 0.0, 0.0, w, h


def parse_elements(path):
    raw = open(path, 'rb').read()
    root = etree.fromstring(raw, parser=etree.XMLParser(recover=True, huge_tree=True, remove_comments=True))
    if root is None: return []
    return X.walk(root, {n.get('id'): n for n in root.iter() if n.get('id')})


def content_bbox(els, vb):
    """Union bbox of the INK (text, non-white fills, strokes); PowerPoint/Keynote exports carry a slide-sized
    white background and content that sits in one corner of it, so the viewBox is a poor frame."""
    canvas = (vb[0], vb[1], vb[0] + vb[2], vb[1] + vb[3])
    ink = [e for e in els if e.tag == 'text' or (e.fill not in (None, 'none', '#ffffff')) or (e.stroke and e.stroke != 'none')]
    # slide exports keep neighbouring slide content OUTSIDE the viewBox (clipped by every renderer): ignore it
    ink = [e for e in ink if frac_inside(e.bbox, canvas) >= 0.5]
    if not ink: return canvas
    bb = ink[0].bbox
    for e in ink[1:]: bb = X.bbox_union(bb, e.bbox)
    return (max(bb[0], canvas[0]), max(bb[1], canvas[1]), min(bb[2], canvas[2]), min(bb[3], canvas[3]))


def frac_inside(bb, box):
    w, h = max(bb[2] - bb[0], 1e-6), max(bb[3] - bb[1], 1e-6)
    ix = max(0.0, min(bb[2], box[2]) - max(bb[0], box[0])); iy = max(0.0, min(bb[3], box[3]) - max(bb[1], box[1]))
    return (ix * iy) / (w * h)


def _norm_text(s):
    return re.sub(r'\s+', ' ', (s or '')).strip().lower()


def scale_by_text(src_els, pdf_els):
    """Print pt per source unit from labels that appear once in both the author SVG and the PDF-extracted SVG
    (which is at print size): the median ratio of pairwise label-centre distances. None when < 3 labels match
    or the ratios disagree (different panel, outlined text, re-wrapped labels)."""
    def centres(els):
        d = collections.defaultdict(list)
        for e in els:
            if e.tag == 'text' and e.text and len(_norm_text(e.text)) >= 2:
                d[_norm_text(e.text)].append(((e.bbox[0] + e.bbox[2]) / 2, (e.bbox[1] + e.bbox[3]) / 2))
        return d
    a, b = centres(src_els), centres(pdf_els)
    keys = [k for k in a if k in b and len(a[k]) == 1 and len(b[k]) == 1]
    if len(keys) < 3: return None, len(keys)
    pts = [(a[k][0], b[k][0]) for k in keys]
    ratios = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            da = math.hypot(pts[i][0][0] - pts[j][0][0], pts[i][0][1] - pts[j][0][1])
            db = math.hypot(pts[i][1][0] - pts[j][1][0], pts[i][1][1] - pts[j][1][1])
            if da > 1e-6 and db > 4.0: ratios.append(db / da)
    if len(ratios) < 3: return None, len(keys)
    ratios.sort(); med = ratios[len(ratios) // 2]
    q1, q3 = ratios[len(ratios) // 4], ratios[(3 * len(ratios)) // 4]
    if med <= 0 or (q3 - q1) / med > 0.12: return None, len(keys)
    return med, len(keys)


# ---------------------------------------------------------------------------
# grid render
# ---------------------------------------------------------------------------
MARGIN = 26.0        # pt reserved for the axis labels (top + left)


def grid_svg(path, scale, frame):
    """Wrap the source SVG (nested, scaled to print pt) in an outer SVG that draws a labelled grid.
    `frame` = (x0, y0, x1, y1) in source units: the region shown; (MARGIN, MARGIN) == its top-left corner."""
    raw = open(path, 'rb').read()
    root = etree.fromstring(raw, parser=etree.XMLParser(recover=True, huge_tree=True, remove_comments=True))
    ox, oy, W, H = frame[0], frame[1], frame[2] - frame[0], frame[3] - frame[1]
    Wp, Hp = W * scale, H * scale
    inner = etree.Element('{%s}svg' % SVG_NS)
    for k, v in root.attrib.items():
        if k in ('width', 'height', 'x', 'y', 'viewBox', 'preserveAspectRatio', 'style'): continue
        inner.set(k, v)
    inner.set('x', '%.3f' % MARGIN); inner.set('y', '%.3f' % MARGIN)
    inner.set('width', '%.3f' % Wp); inner.set('height', '%.3f' % Hp)
    inner.set('viewBox', '%g %g %g %g' % (ox, oy, W, H)); inner.set('preserveAspectRatio', 'none')
    inner.set('overflow', 'hidden')      # the frame never exceeds the source viewBox; off-canvas content stays hidden
    for child in list(root): inner.append(child)
    out = etree.Element('{%s}svg' % SVG_NS, nsmap={None: SVG_NS})
    TW, TH_ = Wp + MARGIN + 6, Hp + MARGIN + 6
    out.set('viewBox', '0 0 %.3f %.3f' % (TW, TH_)); out.set('width', '%.3f' % TW); out.set('height', '%.3f' % TH_)
    bg = etree.SubElement(out, '{%s}rect' % SVG_NS)
    bg.set('x', '0'); bg.set('y', '0'); bg.set('width', '%.3f' % TW); bg.set('height', '%.3f' % TH_); bg.set('fill', '#ffffff')
    out.append(inner)
    g = etree.SubElement(out, '{%s}g' % SVG_NS)
    g.set('style', 'pointer-events:none;font-family:Helvetica,Arial,sans-serif')
    step_minor, step_major = 10, 50
    if max(Wp, Hp) > 700: step_minor, step_major = 20, 100
    def line(x1, y1, x2, y2, major):
        l = etree.SubElement(g, '{%s}line' % SVG_NS)
        l.set('x1', '%.2f' % x1); l.set('y1', '%.2f' % y1); l.set('x2', '%.2f' % x2); l.set('y2', '%.2f' % y2)
        l.set('stroke', '#1f6fe0' if major else '#7fb0ee'); l.set('stroke-width', '0.45' if major else '0.18')
        l.set('opacity', '0.55' if major else '0.45')
    def label(x, y, s, anchor):
        t = etree.SubElement(g, '{%s}text' % SVG_NS)
        t.set('x', '%.2f' % x); t.set('y', '%.2f' % y); t.set('font-size', '6.5'); t.set('fill', '#1f4fa0')
        t.set('text-anchor', anchor); t.set('font-weight', 'bold'); t.text = s
    x = 0
    while x <= Wp + 0.01:
        major = (x % step_major == 0)
        line(MARGIN + x, MARGIN, MARGIN + x, MARGIN + Hp, major)
        if major or step_major >= 100 and x % 50 == 0: label(MARGIN + x, MARGIN - 4, '%d' % x, 'middle')
        x += step_minor
    y = 0
    while y <= Hp + 0.01:
        major = (y % step_major == 0)
        line(MARGIN, MARGIN + y, MARGIN + Wp, MARGIN + y, major)
        if major or step_major >= 100 and y % 50 == 0: label(MARGIN - 3, MARGIN + y + 2.3, '%d' % y, 'end')
        y += step_minor
    frame = etree.SubElement(g, '{%s}rect' % SVG_NS)
    frame.set('x', '%.3f' % MARGIN); frame.set('y', '%.3f' % MARGIN); frame.set('width', '%.3f' % Wp); frame.set('height', '%.3f' % Hp)
    frame.set('fill', 'none'); frame.set('stroke', '#d03030'); frame.set('stroke-width', '0.6'); frame.set('stroke-dasharray', '3 2')
    label(MARGIN + 2, MARGIN + Hp + 5.5, 'print size %.0f x %.0f pt   grid %d / %d pt   (0,0) = top-left corner of the red frame'
          % (Wp, Hp, step_minor, step_major), 'start')
    return etree.tostring(out, encoding='unicode'), Wp, Hp


def render_grids(jobs, quiet=False):
    """jobs: [(svg_text, out_png, px_per_pt)] rendered in one Chromium."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--force-color-profile=srgb'])
        for i, (svg, out_png, pxpt) in enumerate(jobs):
            try: css = K._embed_css(svg)
            except Exception: css = ''      # noqa: BLE001  (font map problems must not stop the render)
            # not K._html_for: its width/height regex (count=2) also strips the NESTED <svg>'s width, which then
            # defaults to 100 % and stretches the figure horizontally against the grid. The outer SVG is sized already.
            vb = K.parse_viewbox(svg) or [0, 0, 300, 200]
            W, H = vb[2], vb[3]
            html = ('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#fff}'
                    'svg{display:block}%s</style></head><body>%s</body></html>' % (css, svg))
            pg = b.new_page(viewport={'width': int(W) + 2, 'height': int(H) + 2}, device_scale_factor=pxpt)
            pg.set_default_timeout(180000)
            try:
                pg.set_content(html, wait_until='load', timeout=60000)
                pg.evaluate('document.fonts.ready.then(()=>1)'); pg.wait_for_timeout(150)
                pg.locator('svg').first.screenshot(path=str(out_png))
            except Exception as exc:        # noqa: BLE001
                print('  render failed %s: %s' % (out_png, exc), file=sys.stderr)
            pg.close()
            if not quiet and (i + 1) % 10 == 0: print('  rendered %d/%d' % (i + 1, len(jobs)), flush=True)
        b.close()


# ---------------------------------------------------------------------------
# detector pool (extract_parts.py) -> per-figure candidate sheets
# ---------------------------------------------------------------------------
def run_extract(a, ids, index, pool_dir):
    toks = ','.join('%s:%s' % (index[f]['paper_id'], index[f]['fig']) for f in ids)
    cmd = [sys.executable, str(HERE / 'extract_parts.py'), '--index', a.index, '--semantics', a.semantics,
           '--extracted-dir', a.extracted_dir, '--select', 'diagram-src', '--ids', toks, '--out', str(pool_dir),
           '--jobs', str(a.jobs)]
    print('extract_parts:', ' '.join(cmd[:8]), '... (%d figures)' % len(ids), flush=True)
    subprocess.run(cmd, check=True)


def per_figure_sheets(pool_dir, figs_dir, ids):
    reps = [json.loads(l) for l in open(pool_dir / 'candidates.jsonl', encoding='utf-8') if l.strip()]
    by_fig = collections.defaultdict(list)
    for r in reps:
        seen = set()
        for cid in r.get('group_geom') or [r['candidate_id']]:
            fid = cid.rsplit('_', 1)[0]
            if fid in seen: continue
            seen.add(fid); by_fig[fid].append(r)
    n_tiles = 0
    for fid in ids:
        rows = by_fig.get(fid) or []
        rows.sort(key=lambda r: (X.HEURISTIC_ORDER.index(r['heuristic']) if r['heuristic'] in X.HEURISTIC_ORDER else 99,
                                 -r['occurrences'], -(r['w_pt'] * r['h_pt'])))
        d = figs_dir / fid
        for old in d.glob('candidates*'): old.unlink()
        meta = {'figure': fid, 'n': len(rows), 'sheets': [], 'tiles': {}}
        per = X.SHEET_COLS * X.SHEET_ROWS
        for s in range(0, len(rows), per):
            batch = rows[s:s + per]; n = s // per + 1
            png = d / ('candidates_%d.png' % n)
            X.draw_sheet(batch, str(pool_dir / 'thumbs'), str(png),
                         '%s  detector candidates %d-%d of %d (optional aid: adopt by id or ignore)' % (fid, s + 1, s + len(batch), len(rows)))
            meta['sheets'].append(png.name)
            for k, r in enumerate(batch):
                meta['tiles']['%d.%d' % (n, k + 1)] = {
                    'candidate_id': r['candidate_id'], 'heuristic': r['heuristic'], 'size_pt': r['size_pt'],
                    'n_elements': r['n_elements'], 'occurrences': r['occurrences'], 'hint_text': r.get('hint_text'),
                    'from_this_figure': r['candidate_id'].rsplit('_', 1)[0] == fid,
                    'svg': str(pool_dir / r['svg_path']), 'thumb': str(pool_dir / r['thumb_path'])}
        (d / 'candidates.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
        n_tiles += len(rows)
    return n_tiles


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--group', default='evolution', help='v3 group or all')
    ap.add_argument('--any-group', action='store_true', help='select by membership, not primary group')
    ap.add_argument('--source', default='src', choices=('src', 'pdf', 'any'))
    ap.add_argument('--labels', default=str(ROOT / 'mech-prescreen/typedisc/labels_v3.jsonl'))
    ap.add_argument('--prescreen', default=str(ROOT / 'mech-prescreen/prescreen.jsonl'))
    ap.add_argument('--index', default=str(ROOT / 'lab/extracted/corpus_index.csv'))
    ap.add_argument('--semantics', default=str(ROOT / 'lab/extracted/corpus_semantics.jsonl'))
    ap.add_argument('--extracted-dir', default=str(ROOT / 'lab/extracted'))
    ap.add_argument('--corpus-root', default=None, help='corpus root (<root>/extracted/...): replaces the lab/ defaults of --index, --semantics and --extracted-dir')
    ap.add_argument('--out', required=True)
    ap.add_argument('--agents', type=int, default=2)
    ap.add_argument('--ids', default=None); ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--no-extract', action='store_true'); ap.add_argument('--no-render', action='store_true')
    ap.add_argument('--render-only', action='store_true', help='re-render the grid images of an existing package from its figures.json')
    a = ap.parse_args()
    if a.corpus_root:
        cr = Path(a.corpus_root).resolve()
        if a.index == str(ROOT / 'lab/extracted/corpus_index.csv'): a.index = str(cr / 'extracted' / 'corpus_index.csv')
        if a.semantics == str(ROOT / 'lab/extracted/corpus_semantics.jsonl'): a.semantics = str(cr / 'extracted' / 'corpus_semantics.jsonl')
        if a.extracted_dir == str(ROOT / 'lab/extracted'): a.extracted_dir = str(cr / 'extracted')
    t0 = time.time()
    out = Path(a.out); figs_dir = out / 'figs'; pool_dir = out / 'pool'; figs_dir.mkdir(parents=True, exist_ok=True)
    if a.render_only:
        jobs = []
        for f in json.load(open(out / 'figures.json', encoding='utf-8')):
            if a.ids and f['id'] not in set(a.ids.split(',')): continue
            for fi in f['files']:
                svg, _w, _h = grid_svg(fi['path'], fi['scale_pt_per_unit'], fi['frame_src'])
                jobs.append((svg, Path(f['dir']) / fi['render'], fi['render_px_per_pt']))
        print('re-rendering %d grid images' % len(jobs), flush=True)
        render_grids(jobs)
        print('done in %.1f min' % ((time.time() - t0) / 60))
        return
    labels, pre, index = load_inputs(a)
    ids = select_ids(a, labels, index)
    print('selected %d figures (group=%s%s, source=%s)' % (len(ids), a.group, ' any' if a.any_group else '', a.source), flush=True)

    figures, grid_jobs = [], []
    for fid in ids:
        row, lab, p = index[fid], labels[fid], pre.get(fid, {})
        files, scale0, note0, kind = figure_files(fid, row, a.extracted_dir, a.source)
        d = figs_dir / fid; d.mkdir(exist_ok=True)
        finfo = []
        pdf_path = os.path.join(a.extracted_dir, row['paper_id'], row['pdf_svg']) if row['pdf_svg'] else ''
        pdf_els = None
        try: st = json.loads(row['style']) if row.get('style') else {}
        except json.JSONDecodeError: st = {}
        pw, ph = (st.get('size') or {}).get('w'), (st.get('size') or {}).get('h')
        for k, (rel, path) in enumerate(files):
            vb = source_viewbox(path)
            els = parse_elements(path)
            cb = content_bbox(els, vb)
            scale, note = scale0, note0
            if kind == 'src':
                # 1st choice: label matching against the print-size PDF export (exact, per file)
                if pdf_els is None and pdf_path and os.path.exists(pdf_path) and os.path.getsize(pdf_path) < 30_000_000:
                    try: pdf_els = parse_elements(pdf_path)
                    except Exception: pdf_els = []      # noqa: BLE001
                s_txt, n_lab = scale_by_text(els, pdf_els or [])
                if s_txt:
                    scale, note = s_txt, 'text-match(%d labels)' % n_lab
                elif len(files) == 1 and pw and ph:
                    # 2nd choice: fit the CONTENT box (not the slide) to the printed size
                    cw, ch = max(cb[2] - cb[0], 1e-6), max(cb[3] - cb[1], 1e-6)
                    sw, sh = pw / cw, ph / ch
                    scale, note = (sw, 'content-fit') if 0.85 <= sw / sh <= 1.18 else (math.sqrt(sw * sh), 'content-fit-aspect-mismatch')
            pad = 2.0 / scale
            frame = (max(cb[0] - pad, vb[0]), max(cb[1] - pad, vb[1]), min(cb[2] + pad, vb[0] + vb[2]), min(cb[3] + pad, vb[1] + vb[3]))
            Wp, Hp = (frame[2] - frame[0]) * scale, (frame[3] - frame[1]) * scale
            pxpt = max(2.0, min(6.0, 1700.0 / max(Wp + MARGIN, Hp + MARGIN, 1.0)))
            png = d / ('render_%d.png' % k)
            conf = 'good' if note.startswith('text-match') or note == 'content-fit' or note == 'pdf' else ('low' if Wp > 520 or Hp > 680 else 'approx')
            finfo.append({'index': k, 'rel': rel, 'path': os.path.abspath(path), 'scale_pt_per_unit': round(scale, 6),
                          'scale_note': note, 'scale_confidence': conf, 'viewBox': [round(v, 3) for v in vb], 'frame_src': [round(v, 3) for v in frame],
                          'print_w_pt': round(Wp, 1), 'print_h_pt': round(Hp, 1), 'n_elements': len(els),
                          'render': png.name, 'render_px_per_pt': round(pxpt, 3)})
            if not a.no_render:
                try:
                    svg, _w, _h = grid_svg(path, scale, frame); grid_jobs.append((svg, png, pxpt))
                except Exception as exc:  # noqa: BLE001
                    print('  grid failed %s %s: %s' % (fid, rel, exc), file=sys.stderr)
        clean = os.path.join(a.extracted_dir, row['paper_id'], row['pdf_svg'].replace('.svg', '.png')) if row['pdf_svg'] else ''
        info = {'id': fid, 'paper_id': row['paper_id'], 'fig': row['fig'], 'venue': row['venue'], 'caption': row['caption'],
                'tool': row['tool'], 'panels': row['panels'], 'column': row['column'], 'aesthetic': row['aesthetic'],
                'groups': lab['groups'], 'primary': lab['primary'], 'worked_example': lab.get('worked_example', False),
                'v2_types': lab.get('v2_types'), 'base': p.get('base'), 'patterns': p.get('patterns'), 'grammar': p.get('grammar'),
                'frames': p.get('frames'), 'steps': p.get('steps'), 'flags': {f: p.get(f) for f in FLAGS},
                'source_kind': kind, 'files': finfo, 'clean_png': os.path.abspath(clean) if clean and os.path.exists(clean) else None,
                'dir': str(d.resolve())}
        (d / 'info.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        figures.append(info)
    if grid_jobs:
        print('rendering %d grid images...' % len(grid_jobs), flush=True); render_grids(grid_jobs)

    if not a.no_extract and a.source != 'pdf':
        run_extract(a, ids, index, pool_dir)
    if (pool_dir / 'candidates.jsonl').exists():
        n = per_figure_sheets(pool_dir, figs_dir, ids); print('candidate sheets: %d tiles over %d figures' % (n, len(ids)), flush=True)

    # stratified round-robin assignment: sort by (base, tool) so every agent sees every kind of figure
    order = sorted(figures, key=lambda f: (f['base'] or '', f['tool'], f['id']))
    agents = [[] for _ in range(max(1, a.agents))]
    for i, f in enumerate(order):
        agents[i % len(agents)].append(f); f['agent'] = 'agent_%d' % (i % len(agents) + 1)
    for n, lst in enumerate(agents, 1):
        d = out / 'agents' / ('agent_%d' % n); (d / 'requests').mkdir(parents=True, exist_ok=True); (d / 'cuts').mkdir(exist_ok=True)
        (d / 'figures.json').write_text(json.dumps([{k: f[k] for k in ('id', 'dir', 'primary', 'base', 'tool', 'frames', 'steps', 'caption')}
                                                    for f in sorted(lst, key=lambda f: f['id'])], ensure_ascii=False, indent=1), encoding='utf-8')
    (out / 'figures.json').write_text(json.dumps(figures, ensure_ascii=False, indent=1), encoding='utf-8')
    print('done in %.1f min: %d figures, %d files, %d agents -> %s' % ((time.time() - t0) / 60, len(figures),
                                                                       sum(len(f['files']) for f in figures), len(agents), out))
    print('by base:', dict(collections.Counter(f['base'] for f in figures)))
    print('by tool:', dict(collections.Counter(f['tool'] for f in figures)))


if __name__ == '__main__':
    main()
