#!/usr/bin/env python3
"""Cut vector parts out of a corpus figure -- the agent-facing half of mechanism parts mining.

  python3 scripts/distill/cut_parts.py --fig <package>/figs/<fig_id> --requests <agent_dir>/requests/<fig_id>.json --out <agent_dir>
  python3 scripts/distill/cut_parts.py --fig <package>/figs/<fig_id> --probe X0 Y0 X1 Y1 [--file K] --out <agent_dir>

`--fig` is a figure directory made by mech_pool.py (info.json + render_<k>.png). `--requests` is a JSON list:

  [{"name": "ghost-copy-dashed-slot",   kebab-case, unique within the figure
    "file": 0,                          index into info.json "files" (default 0)
    "bbox": [x0, y0, x1, y1],           PRINT PT in the grid of render_<file>.png
    "mode": "inside",                   inside (default): elements with >= min_inside of their box inside bbox
                                        touch: every element the bbox overlaps
    "min_inside": 0.6,
    "drop_text": false,                 true = leave <text> out (the shape without its label)
    "only": [12, 13, 15],               exact element ids (from --probe); bbox is then ignored
    "include": [40], "exclude": [41],   add / remove element ids after the bbox selection
    "bitmaps": true,                    keep embedded <image> bitmaps that fall in the box (default true)
    "placeholder": false,               true = keep the bitmaps' places but replace each <image> by a grey box
                                        (a frame for a sample picture, without the picture)
    "note": "..."}]

Geometry is measured in Chromium (exact text and path boxes; hidden elements are ignored) and cached next to the
figure as geom_<k>.json. Requests carrying "geometry": "legacy" use the old estimated boxes and never keep bitmaps,
so cuts reviewed before the switch re-cut to exactly the same element sets.

Export is subtractive (mech_svg.subtractive_cut): the source document minus everything that was not selected, with
resources pruned to what is still referenced, so pattern fills, gradients, masks, clip paths and group opacity render
as in the source. Each cut is compared with the source with text hidden (`fidelity_diff`) and, when it has text,
with text visible (`text_fidelity_diff`; both sides drop @font-face and use fallback fonts, see mech_svg.clean_fonts).

--probe lists every element that overlaps the box (id, tag, box in pt, text / colours) and writes
probes/<fig_id>/probe_<k>_<x0>_<y0>_<x1>_<y1>.png: the region enlarged with each element outlined and numbered.

Writes, under --out:
  cuts/<fig_id>/<name>.svg    standalone SVG (source user units)     cuts/<fig_id>/<name>.png   thumbnail
  cuts/<fig_id>/verify.png    numbered sheet of all cuts -- LOOK AT IT
  cuts/<fig_id>/cuts.json     one record per request: selected ids, size, texts, bitmaps, warnings, fidelity diffs
Every run REPLACES that figure's cuts.
"""
import argparse, hashlib, json, math, os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import extract_parts as X          # noqa: E402
import mech_svg as M               # noqa: E402

TILE = 230
GRID_MARGIN = 26.0                 # mech_pool.MARGIN: pt between the render's edge and the grid origin
FIDELITY_WARN = 0.02
TEXT_FIDELITY_WARN = 0.05          # the same comparison with text visible (reference fonts cleaned like the cut's)


def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-')
    return s or 'cut'


def el_frac_inside(bb, box):
    """Fraction of the element bbox area (min 0.4 unit per side) inside the box."""
    x0, y0, x1, y1 = bb
    w, h = max(x1 - x0, 0.4), max(y1 - y0, 0.4)
    ix = max(0.0, min(x1, box[2]) - max(x0, box[0])); iy = max(0.0, min(y1, box[3]) - max(y0, box[1]))
    if x1 - x0 < 0.4: ix = 0.4 if box[0] <= x0 <= box[2] else 0.0
    if y1 - y0 < 0.4: iy = 0.4 if box[1] <= y0 <= box[3] else 0.0
    return (ix * iy) / (w * h)


class FileState:
    """One source file of a figure: parsed tree, anchors, leaf walk, measured geometry (lazy)."""

    def __init__(self, fig_dir, info, k):
        self.fig_dir, self.info, self.k = Path(fig_dir), info, k
        self.finfo = info['files'][k]
        self.root = M.parse(self.finfo['path'])
        self.anchors = M.anchors(self.root)
        self.leaves, anc = M.walk_anchored(self.root)
        self.leaf_anchor = [int(a.get(M.IDX)) for a in anc]
        self.s = self.finfo['scale_pt_per_unit']
        self.ox, self.oy = (self.finfo.get('frame_src') or self.finfo['viewBox'])[:2]
        self._geom = None

    def geometry(self):
        if self._geom is None:
            g = M.measure_files([(self.finfo['path'], str(self.fig_dir / ('geom_%d.json' % self.k)))])[0]
            if g['n'] != len(self.anchors):
                raise RuntimeError('geometry cache out of date for %s (%d vs %d anchors)' % (self.finfo['rel'], g['n'], len(self.anchors)))
            self._geom = g['els']
        return self._geom

    def to_src(self, b):
        return (self.ox + b[0] / self.s, self.oy + b[1] / self.s, self.ox + b[2] / self.s, self.oy + b[3] / self.s)

    def to_pt(self, b):
        return [round((b[0] - self.ox) * self.s, 1), round((b[1] - self.oy) * self.s, 1),
                round((b[2] - self.ox) * self.s, 1), round((b[3] - self.oy) * self.s, 1)]

    def leaves_of(self, keep):
        return [e for e, a in zip(self.leaves, self.leaf_anchor) if a in keep]


def select_legacy(st, q, box):
    """The pre-2026-09-16 selection: estimated leaf boxes, bitmaps never kept."""
    mode = (q.get('mode') or 'inside').lower(); thr = float(q.get('min_inside') or 0.6)
    area = (box[2] - box[0]) * (box[3] - box[1])
    sel = []
    for e, a in zip(st.leaves, st.leaf_anchor):
        if e.tag == 'image': continue
        if q.get('drop_text') and e.tag == 'text': continue
        if e.w() * e.h() > 3.0 * area and e.tag != 'text': continue
        fr = el_frac_inside(e.bbox, box)
        if (mode == 'touch' and fr > 0) or (mode != 'touch' and fr >= thr): sel.append((e, a))
    n_img = sum(1 for e in st.leaves if e.tag == 'image' and el_frac_inside(e.bbox, box) > 0.3)
    keep = {a for _e, a in sel}
    bb = None
    for e, _a in sel: bb = e.bbox if bb is None else X.bbox_union(bb, e.bbox)
    return keep, bb, len(sel), n_img


def select_measured(st, q, box):
    g = st.geometry()
    mode = (q.get('mode') or 'inside').lower(); thr = float(q.get('min_inside') or 0.6)
    want_bitmaps = q.get('bitmaps', True) is not False
    area = max((box[2] - box[0]) * (box[3] - box[1]), 1e-9) if box else 0
    keep, n_img_skipped = set(), 0
    if q.get('only'):
        keep = {int(i) for i in q['only'] if 0 <= int(i) < len(g)}
    elif box:
        for e in g:
            if not e['v']: continue
            bb = (e['x'], e['y'], e['x'] + e['w'], e['y'] + e['h'])
            fr = el_frac_inside(bb, box)
            hit = (mode == 'touch' and fr > 0) or (mode != 'touch' and fr >= thr)
            if not hit: continue
            if not want_bitmaps and image_target(st.anchors[e['i']], st.root) is not None: n_img_skipped += 1; continue
            if q.get('drop_text') and e['tag'] == 'text': continue
            if e['w'] * e['h'] > 3.0 * area and e['tag'] != 'text': continue
            keep.add(e['i'])
    keep |= {int(i) for i in (q.get('include') or []) if 0 <= int(i) < len(g)}
    keep -= {int(i) for i in (q.get('exclude') or [])}
    bb = None
    for i in keep:
        e = g[i]
        b = (e['x'], e['y'], e['x'] + e['w'], e['y'] + e['h'])
        bb = b if bb is None else X.bbox_union(bb, b)
    return keep, bb, len(keep), n_img_skipped


def cut_figure(fig_dir, reqs, out_root, render=True, quiet=False):
    """Run every request of one figure. Returns the records (also written to cuts.json)."""
    fig_dir = Path(fig_dir); info = json.loads((fig_dir / 'info.json').read_text(encoding='utf-8'))
    out_dir = Path(out_root) / 'cuts' / info['id']; out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.iterdir():
        if old.suffix in ('.svg', '.png', '.json'): old.unlink()
    states, records, items, gts, names = {}, [], [], [], set()
    for i, q in enumerate(reqs):
        name = slug(q.get('name') or ('cut-%d' % (i + 1)))
        base, n = name, 2
        while name in names: name = '%s-%d' % (base, n); n += 1
        names.add(name)
        legacy = (q.get('geometry') == 'legacy')
        rec = {'name': name, 'request': q, 'file': int(q.get('file') or 0), 'geometry': 'legacy' if legacy else 'measured',
               'warnings': [], 'n_elements': 0, 'n_text': 0, 'w_pt': 0, 'h_pt': 0}
        records.append(rec)
        if not (0 <= rec['file'] < len(info['files'])): rec['warnings'].append('no such file index'); continue
        bbox = q.get('bbox') or []
        has_box = len(bbox) == 4 and bbox[2] > bbox[0] and bbox[3] > bbox[1]
        if not has_box and not (q.get('only') and not legacy): rec['warnings'].append('bad bbox'); continue
        if rec['file'] not in states: states[rec['file']] = FileState(fig_dir, info, rec['file'])
        st = states[rec['file']]
        box = st.to_src(bbox) if has_box else None
        try:
            keep, bb, n_sel, n_img = (select_legacy if legacy else select_measured)(st, q, box)
        except Exception as exc:  # noqa: BLE001
            rec['warnings'].append('selection failed: %s' % exc); continue
        if n_img: rec['warnings'].append('%d bitmap <image> in box (skipped)' % n_img)
        if not keep or bb is None: rec['warnings'].append('nothing selected: check file index / coordinates'); continue
        leaves = st.leaves_of(keep)
        geom = None if legacy else st.geometry()
        w_pt, h_pt = (bb[2] - bb[0]) * st.s, (bb[3] - bb[1]) * st.s
        texts = ([e.text for e in leaves if e.tag == 'text' and e.text] if legacy
                 else [geom[i].get('t') for i in sorted(keep) if geom[i]['tag'] == 'text' and geom[i].get('t')])
        bitmaps = []
        for i in sorted(keep):
            node = st.anchors[i]
            node = image_target(node, st.root)                 # a <use> of a stored <image> counts as a bitmap
            if node is None: continue
            data = M.href_bytes(node)
            bitmaps.append({'idx': i, 'sha1': hashlib.sha1(data).hexdigest() if data else None,
                            'bbox_pt': st.to_pt((geom[i]['x'], geom[i]['y'], geom[i]['x'] + geom[i]['w'], geom[i]['y'] + geom[i]['h'])) if geom else None})
        rec.update(n_elements=n_sel, n_text=len(texts) if not legacy else sum(1 for e in leaves if e.tag == 'text'),
                   w_pt=round(w_pt, 1), h_pt=round(h_pt, 1), has_curve=any(e.curve for e in leaves),
                   bbox_src=[round(v, 3) for v in bb], bbox_pt=st.to_pt(bb), selected_idx=sorted(keep),
                   colors=sorted({e.fill for e in leaves if e.fill and e.fill not in ('none', 'url')} |
                                 {e.stroke for e in leaves if e.stroke and e.stroke not in ('none', 'url')})[:12],
                   texts=' | '.join(texts)[:200], bitmaps=bitmaps,
                   geom_hash=X.geom_hash(leaves, bb) if leaves else hashlib.sha1(repr(sorted(keep)).encode()).hexdigest()[:20],
                   scale=st.s, source_file=st.finfo['rel'])
        if bitmaps: rec['warnings'].append('contains %d bitmap image(s)' % len(bitmaps))
        if n_sel > 120: rec['warnings'].append('%d elements: probably a whole panel' % n_sel)
        if max(w_pt, h_pt) > 220: rec['warnings'].append('%.0f pt long side: larger than a part' % max(w_pt, h_pt))
        if rec['n_text'] and rec['n_text'] == n_sel: rec['warnings'].append('text only')
        if has_box and ((bb[2] - bb[0]) * st.s > (bbox[2] - bbox[0]) * 1.6 or (bb[3] - bb[1]) * st.s > (bbox[3] - bbox[1]) * 1.6):
            rec['warnings'].append('selection much larger than the box (a big element overlaps it)')
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        pad = max(0.04 * max(w, h), 0.5)
        vb = (bb[0] - pad, bb[1] - pad, w + 2 * pad, h + 2 * pad)
        comment = 'source: %s %s bbox_src=%.2f,%.2f,%.2f,%.2f scale=%.4f cut=%s elements=%s' % (
            info['id'], st.finfo['rel'], bb[0], bb[1], w, h, st.s, name, ','.join(map(str, sorted(keep)))[:400])
        try:
            svg = M.subtractive_cut(st.root, keep, vb, prefix='%s-%s-' % (slug(info['id']), name), comment=comment)
            gt = M.hidden_reference(st.root, keep, vb, prefix='gt-%s-' % name, clean=True)
        except Exception as exc:  # noqa: BLE001
            rec['warnings'].append('export failed: %s' % exc); continue
        if q.get('placeholder') and bitmaps:
            svg = placeholder_images(svg); rec['placeholder'] = True; rec['warnings'].append('%d bitmap(s) replaced by grey placeholders' % len(bitmaps))
        (out_dir / (name + '.svg')).write_text(svg, encoding='utf-8')
        rec['svg'] = str(out_dir / (name + '.svg')); items.append((name, svg))
        rec['svg_kb'] = round(len(svg) / 1024, 1)
        # the unpruned reference keeps every resource of the source (whole-slide bitmaps included): skip huge ones
        if len(gt) <= 1_500_000: gts.append((name, gt))
    if items and render:
        with_text = {r['name'] for r in records if r.get('svg') and r['n_text']}
        tiles, cut_nt, gt_nt, gt_t = M.render_fit_groups([(items, ''), (items, M.HIDE_TEXT_CSS), (gts, M.HIDE_TEXT_CSS),
                                                          ([g for g in gts if g[0] in with_text], '')], size=TILE)
        for r in records:
            if r['name'] in tiles:
                tiles[r['name']].save(out_dir / (r['name'] + '.png')); r['png'] = str(out_dir / (r['name'] + '.png'))
                if r['name'] not in gt_nt or r.get('placeholder'): r['fidelity_diff'] = None; continue     # a placeholder cut differs by design
                d = M.diff_ratio(cut_nt[r['name']], gt_nt[r['name']]); r['fidelity_diff'] = round(d, 4)
                if d > FIDELITY_WARN: r['warnings'].append('export differs from source by %.0f%%' % (100 * d))
                if r['name'] in gt_t:
                    td = M.diff_ratio(tiles[r['name']], gt_t[r['name']]); r['text_fidelity_diff'] = round(td, 4)
                    if td > TEXT_FIDELITY_WARN: r['warnings'].append('text renders differently from source by %.0f%%' % (100 * td))
        verify_sheet([r for r in records if r.get('svg')], tiles, str(out_dir / 'verify.png'), '%s  cuts (%d)' % (info['id'], len(items)))
    (out_dir / 'cuts.json').write_text(json.dumps({'figure': info['id'], 'cuts': records}, ensure_ascii=False, indent=1), encoding='utf-8')
    if not quiet:
        for k, r in enumerate(records, 1):
            print('%2d %-36s %4.0fx%-4.0fpt %3d el %2d text  %s  %s' % (k, r['name'], r['w_pt'], r['h_pt'], r['n_elements'], r['n_text'],
                                                                         ('WARN: ' + '; '.join(r['warnings'])) if r['warnings'] else 'ok',
                                                                         ('"' + r['texts'][:40] + '"') if r.get('texts') else ''))
        if items and render: print('verify sheet:', out_dir / 'verify.png')
    return records


XLINK = '{http://www.w3.org/1999/xlink}href'


def image_target(node, root):
    """The <image> a drawable stands for: itself, or the stored <image> a <use href="#id"> places (PDF exports store
    each bitmap once in <defs> and place it with <use>); None for anything else."""
    t = M.local(node)
    if t == 'image': return node
    if t != 'use': return None
    ref = (node.get(XLINK) or node.get('href') or '').lstrip('#')
    if not ref: return None
    hit = root.xpath('//*[@id=$i]', i=ref)
    return hit[0] if hit and M.local(hit[0]) == 'image' else None


def placeholder_images(svg):
    """Replace every bitmap of a cut by a light-grey rectangle in the same place, so a sample-picture frame can be kept
    as a part without the picture. Handles an <image> drawn directly and a <use> of a stored <image> (its x/y add a
    translation after its transform; the size is the image's own width/height); stored images nothing references any
    more are removed. Masks and clip paths of the ancestors stay as they are."""
    from lxml import etree
    doc = etree.fromstring(svg.encode('utf-8'), parser=etree.XMLParser(recover=True, huge_tree=True))
    ns = 'http://www.w3.org/2000/svg'
    resource = lambda el: any(M.local(a) in ('defs', 'mask', 'clipPath', 'pattern', 'symbol') for a in el.iterancestors())

    def opaque_box(im):
        """(x, y, w, h) of the bitmap's visible pixels in the image's own units: a transparent margin around an icon
        must not become grey (it would cover the arrows drawn under it). Falls back to the whole image."""
        x, y, w, h = (float(im.get(k) or 0) for k in ('x', 'y', 'width', 'height'))
        try:
            import io
            from PIL import Image
            data = M.href_bytes(im)
            if not data: return x, y, w, h
            pic = Image.open(io.BytesIO(data))
            if pic.mode not in ('RGBA', 'LA', 'PA') and not (pic.mode == 'P' and 'transparency' in pic.info): return x, y, w, h
            a = pic.convert('RGBA').getchannel('A').point(lambda v: 255 if v > 16 else 0)
            bb = a.getbbox()
            if not bb: return x, y, w, h
            pw, ph = pic.size
            return x + bb[0] / pw * w, y + bb[1] / ph * h, (bb[2] - bb[0]) / pw * w, (bb[3] - bb[1]) / ph * h
        except Exception:  # noqa: BLE001
            return x, y, w, h

    def rect_for(im, extra_transform=None, attrs=None):
        w, h = im.get('width'), im.get('height')
        if not w or not h: return None
        bx, by, bw, bh = opaque_box(im)
        r = etree.Element('{%s}rect' % ns)
        r.set('x', '%.3f' % bx); r.set('y', '%.3f' % by); r.set('width', '%.3f' % bw); r.set('height', '%.3f' % bh)
        if im.get('transform'): r.set('transform', im.get('transform'))
        r.set('fill', '#d9d9d9'); r.set('stroke', '#9a9a9a'); r.set('stroke-width', '0.4'); r.set('vector-effect', 'non-scaling-stroke')
        r.set('data-placeholder', 'image')
        if extra_transform is None: return r
        g = etree.Element('{%s}g' % ns)
        for k, v in (attrs or {}).items(): g.set(k, v)
        g.set('transform', extra_transform); g.append(r); return g

    n = 0
    # <use> placements first: a stored image may also be drawn directly in the body, and replacing that copy first
    # would leave its placements pointing at nothing (no picture and no grey box)
    ids = {el.get('id'): el for el in doc.iter() if el.get('id')}
    for u in list(doc.iter('{%s}use' % ns)):
        if resource(u): continue
        tgt = ids.get((u.get(XLINK) or u.get('href') or '').lstrip('#'))
        if tgt is None or M.local(tgt) != 'image': continue
        tr = ' '.join(x for x in (u.get('transform') or '', 'translate(%s,%s)' % (u.get('x') or '0', u.get('y') or '0')) if x)
        attrs = {k: u.get(k) for k in ('clip-path', 'mask', 'opacity', 'style') if u.get(k)}
        r = rect_for(tgt, tr, attrs)
        if r is None: continue
        u.getparent().replace(u, r); n += 1
    for im in list(doc.iter('{%s}image' % ns)):
        if resource(im): continue
        r = rect_for(im)
        if r is None: continue
        for k in ('clip-path', 'mask', 'opacity', 'style'):
            if im.get(k): r.set(k, im.get(k))
        im.getparent().replace(im, r); n += 1
    # a soft mask is the bitmap's own alpha (often a stock icon's silhouette): drop it from the placeholder and from
    # ancestors that hold nothing but placeholders, so a placeholder stays a plain box
    ph = [el for el in doc.iter() if el.get('data-placeholder') == 'image']
    for el in ph:
        el.attrib.pop('mask', None)
        if el.getparent() is not None and M.local(el.getparent()) == 'g' and el.getparent().get('transform') and len(el.getparent()) == 1: el.getparent().attrib.pop('mask', None)
        for anc in el.iterancestors():
            if anc.get('mask') is None: continue
            drawables = [d for d in anc.iter() if M.local(d) in M.ANCHORS]
            if drawables and all(d.get('data-placeholder') == 'image' for d in drawables): anc.attrib.pop('mask', None)
    # drop the masks and stored bitmaps nothing references any more (repeat: a removed mask frees its images)
    for _ in range(4):
        text = etree.tostring(doc, encoding='unicode'); gone = 0
        for el in [el for el in doc.iter() if el.get('id') and M.local(el) in ('mask', 'image') and (M.local(el) == 'mask' or resource(el))]:
            i = el.get('id')
            if ('#' + i + '"') in text or ("#" + i + "'") in text or ('#' + i + ')') in text: continue
            if el.getparent() is not None: el.getparent().remove(el); gone += 1
        if not gone: break
    return etree.tostring(doc, encoding='unicode')


def verify_sheet(records, imgs, out_png, title):
    from PIL import Image, ImageDraw
    F = X._fonts()
    cols = 4; tw, th = TILE + 16, TILE + 74
    rows = max(1, math.ceil(len(records) / cols))
    img = Image.new('RGB', (cols * tw + 20, rows * th + 50), '#ffffff'); dr = ImageDraw.Draw(img)
    dr.text((10, 10), title[:120], fill='#111111', font=F['hdr'])
    for k, r in enumerate(records):
        rr, c = divmod(k, cols); x = 10 + c * tw; y = 40 + rr * th
        dr.rectangle([x, y, x + tw - 6, y + th - 6], outline='#d8d8d8')
        im = imgs.get(r['name'])
        if im is not None: img.paste(im, (x + 8, y + 26))
        dr.rectangle([x + 3, y + 3, x + 33, y + 21], fill='#1a1a1a'); dr.text((x + 9, y + 2), str(k + 1), fill='#ffffff', font=F['num'])
        dr.text((x + 40, y + 6), r['name'][:34], fill='#0b57a4', font=F['lbl'])
        ln = y + 26 + TILE + 2
        dr.text((x + 8, ln), '%.0f x %.0f pt  %d el  %d text' % (r['w_pt'], r['h_pt'], r['n_elements'], r['n_text']), fill='#333333', font=F['txt'])
        warn = '; '.join(r['warnings'])[:44]
        dr.text((x + 8, ln + 13), warn, fill='#c02020' if warn else '#444444', font=F['txt'])
        dr.text((x + 8, ln + 26), (r.get('texts') or '')[:44], fill='#666666', font=F['txt'])
    img.save(out_png)


def probe(fig_dir, k, box_pt, out_root, limit=150):
    from PIL import Image, ImageDraw
    fig_dir = Path(fig_dir); info = json.loads((fig_dir / 'info.json').read_text(encoding='utf-8'))
    st = FileState(fig_dir, info, k); g = st.geometry()
    box = st.to_src(box_pt)
    first_leaf = {}
    for e, a in zip(st.leaves, st.leaf_anchor): first_leaf.setdefault(a, e)
    rows = []
    for e in g:
        bb = (e['x'], e['y'], e['x'] + e['w'], e['y'] + e['h'])
        if bb[2] < box[0] or bb[0] > box[2] or bb[3] < box[1] or bb[1] > box[3]: continue
        rows.append((e, st.to_pt(bb), el_frac_inside(bb, box)))
    rows.sort(key=lambda r: (r[1][1], r[1][0]))
    print('%s file %d  box %s pt: %d elements overlap (id, tag, x0 y0 x1 y1 pt, %% inside, what)' % (info['id'], k, box_pt, len(rows)))
    for e, p, fr in rows[:limit]:
        lf = first_leaf.get(e['i'])
        if e['tag'] == 'text': what = '"%s"' % e.get('t', '')[:40]
        elif e['tag'] == 'image': what = 'bitmap'
        else: what = ('fill %s stroke %s' % (lf.fill, lf.stroke)) if lf else ''
        print('%5d %-8s %6.1f %6.1f %6.1f %6.1f  %3.0f%%  %s%s' % (e['i'], e['tag'], p[0], p[1], p[2], p[3], 100 * fr, what, '' if e['v'] else '  [hidden]'))
    if len(rows) > limit: print('... %d more (narrow the box)' % (len(rows) - limit))
    # enlarged crop of the grid render with every visible element outlined and numbered
    finfo = st.finfo; pxpt = finfo['render_px_per_pt']
    src = Image.open(fig_dir / finfo['render']).convert('RGB')
    mx = 8.0
    crop = [int(max(0, (GRID_MARGIN + box_pt[0] - mx) * pxpt)), int(max(0, (GRID_MARGIN + box_pt[1] - mx) * pxpt)),
            int(min(src.width, (GRID_MARGIN + box_pt[2] + mx) * pxpt)), int(min(src.height, (GRID_MARGIN + box_pt[3] + mx) * pxpt))]
    im = src.crop(crop)
    zoom = max(1.0, min(6.0, 1100.0 / max(im.width, 1)))
    im = im.resize((int(im.width * zoom), int(im.height * zoom)), Image.LANCZOS)
    dr = ImageDraw.Draw(im); F = X._fonts()
    palette = ['#e6194b', '#3cb44b', '#4363d8', '#f58231', '#911eb4', '#008080', '#9a6324', '#800000', '#000075', '#f032e6']
    for n, (e, p, fr) in enumerate(rows[:limit]):
        if not e['v']: continue
        c = palette[n % len(palette)]
        x0 = ((GRID_MARGIN + p[0]) * pxpt - crop[0]) * zoom; y0 = ((GRID_MARGIN + p[1]) * pxpt - crop[1]) * zoom
        x1 = ((GRID_MARGIN + p[2]) * pxpt - crop[0]) * zoom; y1 = ((GRID_MARGIN + p[3]) * pxpt - crop[1]) * zoom
        dr.rectangle([x0, y0, max(x1, x0 + 1), max(y1, y0 + 1)], outline=c, width=2)
        lab = str(e['i']); tx, ty = x0 + 1, max(0, y0 - 12)
        dr.rectangle([tx, ty, tx + 7 * len(lab) + 4, ty + 12], fill=c); dr.text((tx + 2, ty), lab, fill='#ffffff', font=F['txt'])
    out = Path(out_root) / 'probes' / info['id']; out.mkdir(parents=True, exist_ok=True)
    png = out / ('probe_%d_%s.png' % (k, '_'.join('%g' % v for v in box_pt)))
    im.save(png); print('probe image:', png)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fig', required=True); ap.add_argument('--requests'); ap.add_argument('--out', required=True)
    ap.add_argument('--probe', nargs=4, type=float, metavar=('X0', 'Y0', 'X1', 'Y1'))
    ap.add_argument('--file', type=int, default=0, help='source file index for --probe')
    ap.add_argument('--limit', type=int, default=400, help='--probe: list at most this many elements (default 400)')
    ap.add_argument('--no-render', action='store_true')
    a = ap.parse_args()
    if a.probe:
        return probe(a.fig, a.file, a.probe, a.out, limit=a.limit)
    if not a.requests: ap.error('--requests is required unless --probe is given')
    reqs = json.loads(Path(a.requests).read_text(encoding='utf-8'))
    if isinstance(reqs, dict): reqs = reqs.get('requests') or reqs.get('cuts') or []
    cut_figure(a.fig, reqs, a.out, render=not a.no_render)


if __name__ == '__main__':
    main()
