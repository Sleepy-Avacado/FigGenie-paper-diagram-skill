#!/usr/bin/env python3
"""Faithful SVG sub-setting for parts mining: measured element geometry and subtractive cuts.

Parts used to be rebuilt leaf by leaf from a flattened walk (extract_parts.export_candidate_svg). That loses what
lives outside the leaf: pattern tiles referenced from <defs> (hatching), clip paths and masks on ancestor groups,
group opacity (a faded group composites differently from individually faded leaves) and gradients. A subtractive
cut keeps the source document, deletes every drawable that is not selected and prunes the resources to what is
still referenced, so the part renders exactly like that region of the source.

  anchors(root)                      render-tree drawables in document order; sets data-cut-idx = position
  measure_files([(svg, cache)])      per-anchor bbox in root user units + visibility, measured in Chromium, cached
  walk_anchored(root)                extract_parts.walk() leaves plus the anchor that renders each leaf
  subtractive_cut(root, keep, vb)    standalone SVG text (ids prefixed, @font-face dropped, subset font names cleaned)
  render_fit(items, size, css)       {key: PIL RGB image}, each SVG fitted into a size x size cell
  diff_ratio(a, b)                   share of inked pixels that differ between two renders
"""
import copy, io, json, math, os, re, sys
from pathlib import Path
from lxml import etree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import extract_parts as X          # noqa: E402

SVG_NS = 'http://www.w3.org/2000/svg'
XLINK_HREF = '{http://www.w3.org/1999/xlink}href'
RESOURCE = {'defs', 'clipPath', 'mask', 'pattern', 'marker', 'symbol', 'linearGradient', 'radialGradient', 'filter',
            'style', 'metadata', 'title', 'desc', 'script', 'font', 'font-face', 'cursor', 'view', 'color-profile'}
SERVERS = RESOURCE - {'defs', 'style', 'metadata', 'title', 'desc', 'script'}
CONTAINERS = {'g', 'a', 'svg', 'switch'}
ANCHORS = {'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text', 'image', 'use', 'foreignObject'}
GENERIC = ('serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui')
URL_RE = re.compile(r'url\(\s*[\'"]?#([^)\'"\s]+)[\'"]?\s*\)')
SUBSET_RE = re.compile(r'^[A-Z]{6}\+')
FONTFACE_RE = re.compile(r'@font-face\s*\{[^}]*\}', re.S)
IDX = 'data-cut-idx'


def local(node):
    """SVG local name, or None for comments/PIs and foreign-namespace elements (inkscape/sodipodi metadata)."""
    t = node.tag
    if not isinstance(t, str): return None
    if t.startswith('{'):
        ns, name = t[1:].split('}', 1)
        return name if ns == SVG_NS else None
    return t


def parse(path):
    return etree.fromstring(open(path, 'rb').read(), parser=etree.XMLParser(recover=True, huge_tree=True, remove_comments=True))


def anchors(root):
    """Render-tree drawables in document order. Each gets data-cut-idx=<position> (idempotent)."""
    out = []

    def rec(node):
        for ch in node:
            t = local(ch)
            if t is None or t in RESOURCE: continue
            if t in CONTAINERS: rec(ch)
            elif t in ANCHORS:
                ch.set(IDX, str(len(out))); out.append(ch)
    rec(root)
    return out


def viewbox_of(root):
    v = [float(x) for x in X.NUM_TOKEN.findall(root.get('viewBox') or '')]
    if len(v) == 4 and v[2] > 0 and v[3] > 0: return v
    return [0.0, 0.0, X.fnum(root.get('width'), 100.0) or 100.0, X.fnum(root.get('height'), 100.0) or 100.0]


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------
MEASURE_JS = r"""() => {
  const svg = document.querySelector('svg'); const R = svg.getBoundingClientRect();
  const b = svg.viewBox && svg.viewBox.baseVal; const vb = (b && b.width) ? b : {x: 0, y: 0, width: R.width, height: R.height};
  const sx = vb.width / R.width, sy = vb.height / R.height, els = [];
  for (const el of svg.querySelectorAll('[data-cut-idx]')) {
    const r = el.getBoundingClientRect();
    let v = el.checkVisibility ? el.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}) : true;
    if (r.width === 0 && r.height === 0) v = false;
    const rec = {i: +el.getAttribute('data-cut-idx'), tag: el.tagName, x: (r.left - R.left) * sx + vb.x, y: (r.top - R.top) * sy + vb.y,
                 w: r.width * sx, h: r.height * sy, v: v ? 1 : 0};
    if (el.tagName === 'text') rec.t = (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160);
    els.push(rec);
  }
  return {vb: [vb.x, vb.y, vb.width, vb.height], els};
}"""


def page_html(svg_text, bg='#fff', css=''):
    return ('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:%s}'
            'svg{display:block}%s</style></head><body>%s</body></html>' % (bg, css, svg_text))


def _sized(root):
    """Serialise with width/height = viewBox size, so 1 CSS px == 1 user unit."""
    vb = viewbox_of(root)
    r = copy.copy(root) if False else root
    old = (r.get('width'), r.get('height'))
    r.set('width', '%g' % vb[2]); r.set('height', '%g' % vb[3])
    txt = etree.tostring(r, encoding='unicode')
    for k, v in zip(('width', 'height'), old):
        if v is None: del r.attrib[k]
        else: r.set(k, v)
    return txt, vb


def measure_files(jobs, quiet=True):
    """jobs: [(svg_path, cache_json)] -> [geometry dict]. geometry = {n, vb, els: [{i,tag,x,y,w,h,v,t?}], src_size}."""
    out = [None] * len(jobs)
    todo = []
    for k, (path, cache) in enumerate(jobs):
        size = os.path.getsize(path)
        if cache and os.path.exists(cache):
            try:
                g = json.load(open(cache, encoding='utf-8'))
                if g.get('src_size') == size and g.get('version') == 1:
                    out[k] = g; continue
            except (OSError, ValueError):
                pass
        todo.append(k)
    if not todo: return out
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--force-color-profile=srgb'])
        for k in todo:
            path, cache = jobs[k]
            root = parse(path); n = len(anchors(root))
            txt, vb = _sized(root)
            pg = b.new_page(viewport={'width': max(200, min(8000, int(vb[2]) + 2)), 'height': max(200, min(8000, int(vb[3]) + 2))})
            pg.set_default_timeout(240000)
            try:
                pg.set_content(page_html(txt), wait_until='load', timeout=120000)
                pg.evaluate('document.fonts.ready.then(()=>1)')
                g = pg.evaluate(MEASURE_JS)
            finally:
                pg.close()
            g.update(version=1, n=n, src_size=os.path.getsize(path), path=str(path))
            g['els'].sort(key=lambda e: e['i'])
            if cache:
                Path(cache).write_text(json.dumps(g, ensure_ascii=False), encoding='utf-8')
            out[k] = g
            if not quiet: print('  measured %s: %d anchors' % (os.path.basename(path), n), flush=True)
        b.close()
    return out


def walk_anchored(root):
    """extract_parts.walk() with the same traversal, plus for every leaf the render-tree anchor that draws it
    (the leaf itself, or the outermost <use> it was reached through). Call anchors(root) first."""
    defs_by_id = {n.get('id'): n for n in root.iter() if isinstance(n.tag, str) and n.get('id')}
    out, anc = [], []
    idx = [0]

    def rec(node, ctm, inh, use_depth, anchor):
        for child in node:
            t = X.tagname(child)
            if not t or t in X.SKIP_TAGS: continue
            m = X.mat_mul(ctm, X.parse_transform(child.get('transform')))
            style = dict(inh)
            for k in X.INHERIT:
                v = X.style_lookup(child, k, inh)
                if v is not None: style[k] = v
            if t in ('g', 'a', 'svg'):
                rec(child, m, style, use_depth, anchor); continue
            if t == 'use':
                if use_depth > 3: continue
                href = child.get(XLINK_HREF) or child.get('href') or ''
                tgt = defs_by_id.get(href.lstrip('#'))
                if tgt is None: continue
                m2 = X.mat_mul(m, (1, 0, 0, 1, X.fnum(child.get('x')), X.fnum(child.get('y'))))
                holder = etree.Element('g'); holder.append(copy.deepcopy(tgt))
                rec(holder, m2, style, use_depth + 1, anchor if anchor is not None else child)
                continue
            if t not in X.DRAW_TAGS: continue
            el = X.build_el(child, t, m, style, idx)
            if el is not None:
                out.append(el); anc.append(anchor if anchor is not None else child)
    rec(root, (1, 0, 0, 1, 0, 0), {}, 0, None)
    return out, anc


# ---------------------------------------------------------------------------
# subtractive cut
# ---------------------------------------------------------------------------
def _family_names(value):
    return [p.strip().strip('\'"').strip() for p in (value or '').split(',') if p.strip().strip('\'"').strip()]


CSS_IDENT_RE = re.compile(r'-?[_a-zA-Z][_a-zA-Z0-9-]*')


def clean_family(value):
    """Subset prefixes (ABCDEF+) removed, a generic family appended, names quoted unless they are CSS identifiers
    (exporters write unquoted names such as ABCDEF+Calibri, which make browsers ignore the whole declaration)."""
    names = []
    for raw in _family_names(value):
        n = SUBSET_RE.sub('', raw)
        if n and n not in names: names.append(n)
    if not any(n in GENERIC for n in names):
        joined = ' '.join(names)
        names.append('monospace' if X.MONO_RE.search(joined) else ('serif' if X.SERIF_RE.search(joined) else 'sans-serif'))
    return ', '.join(n if (n in GENERIC or CSS_IDENT_RE.fullmatch(n)) else "'%s'" % n for n in names)


def _fix_style_fonts(style):
    return re.sub(r'(font-family\s*:\s*)([^;}]+)', lambda m: m.group(1) + clean_family(m.group(2)), style)


def clean_fonts(doc):
    """In place: @font-face rules dropped, font-family names cleaned. Fonts embedded by slide and PDF exporters cannot
    be kept: Chromium rejects most of them (no OS/2 table, Mac-only or missing cmap), and their cmaps often use the
    exporter's private encoding while the text is Unicode, so a repaired font would show wrong glyphs (digits too).
    Text falls back to the generic family; equation labels written in a private encoding show as punctuation."""
    for st in [n for n in doc.iter() if local(n) == 'style']:
        txt = FONTFACE_RE.sub('', st.text or '')
        if txt.strip(): st.text = _fix_style_fonts(txt)
        elif st.getparent() is not None: st.getparent().remove(st)
    for n in doc.iter():
        if not isinstance(n.tag, str): continue
        if n.get('font-family'): n.set('font-family', clean_family(n.get('font-family')))
        if 'font-family' in (n.get('style') or ''): n.set('style', _fix_style_fonts(n.get('style')))


def _relocate_use_targets(doc, keep):
    """Kept <use> anchors may reference drawables that live in the render tree (PowerPoint exports reuse a placed
    image this way). Move those targets (transitively) into <defs>: the reference keeps working, the target no longer
    draws itself at its own position, and deleting or hiding the other drawables cannot remove the clone."""
    ids = {n.get('id'): n for n in doc.iter() if isinstance(n.tag, str) and n.get('id')}
    targets, stack = set(), []
    for n in doc.iter():
        if isinstance(n.tag, str) and n.get(IDX) in keep:
            h = n.get(XLINK_HREF) or n.get('href') or ''
            if h.startswith('#'): stack.append(h[1:])
    while stack:
        i = stack.pop()
        if i in targets or i not in ids: continue
        targets.add(i)
        for d in ids[i].iter():
            if isinstance(d.tag, str):
                h = d.get(XLINK_HREF) or d.get('href') or ''
                if h.startswith('#'): stack.append(h[1:])
    defs = None
    for i in targets:
        n = ids[i]; p = n.getparent()
        if p is None or any(isinstance(d.tag, str) and d.get(IDX) in keep for d in n.iter()): continue
        q, in_resource = p, False
        while q is not None:
            if local(q) in RESOURCE: in_resource = True; break
            q = q.getparent()
        if in_resource: continue
        if defs is None:
            defs = etree.Element('{%s}defs' % SVG_NS); doc.insert(0, defs)
        p.remove(n); defs.append(n)
    return targets


def subtractive_cut(root, keep, viewbox, prefix='', comment=None, prune_resources=True, drop_fonts=True, strip_idx=True):
    """root: parsed source with anchors() applied. keep: anchor indices. viewbox: (x, y, w, h) in root user units.
    drop_fonts: clean_fonts() (@font-face rules removed, font-family names cleaned)."""
    keep = {str(i) for i in keep}
    doc = copy.deepcopy(root)
    protected = _relocate_use_targets(doc, keep)

    def prune(node):
        for ch in list(node):
            t = local(ch)
            if t is None:
                node.remove(ch); continue
            if t in RESOURCE or ch.get('id') in protected: continue
            if t in CONTAINERS:
                prune(ch)
            elif t not in ANCHORS or ch.get(IDX) not in keep:
                node.remove(ch)
    prune(doc)

    # drop containers left empty BEFORE collecting references: an emptied <g clip-path="url(#c)"> still names its clip
    # path, and PDF exports wrap every drawing operation in one, so the cut kept every clip path of the page (thousands)
    def empty_out(node):
        for ch in list(node):
            if local(ch) in CONTAINERS:
                empty_out(ch)
                if not any(local(g) not in (None, 'title', 'desc') for g in ch): node.remove(ch)
    empty_out(doc)

    # resources: keep only what the remaining drawing references (transitively)
    ids = {}
    for n in doc.iter():
        if isinstance(n.tag, str) and n.get('id'): ids.setdefault(n.get('id'), n)

    def refs(n, acc):
        for k, v in n.attrib.items():
            if 'url(' in v: acc.update(URL_RE.findall(v))
            if k in (XLINK_HREF, 'href') and v.startswith('#'): acc.add(v[1:])
        if local(n) == 'style' and n.text: acc.update(URL_RE.findall(n.text))

    def resource_roots(node, inside, out_render, out_res):
        for ch in node:
            t = local(ch)
            if t is None: continue
            if inside or t in RESOURCE:
                out_res.append(ch)
                resource_roots(ch, True, out_render, out_res)
            else:
                out_render.append(ch)
                resource_roots(ch, False, out_render, out_res)
    render_nodes, res_nodes = [doc], []
    resource_roots(doc, False, render_nodes, res_nodes)
    reach, stack = set(), []
    for n in render_nodes:
        acc = set(); refs(n, acc); stack.extend(acc)
    for n in res_nodes:
        if local(n) == 'style':
            acc = set(); refs(n, acc); stack.extend(acc)
    while stack:
        i = stack.pop()
        if i in reach: continue
        reach.add(i)
        n = ids.get(i)
        if n is None: continue
        for d in n.iter():
            if isinstance(d.tag, str):
                acc = set(); refs(d, acc); stack.extend(acc - reach)

    def needed(n):
        return any(isinstance(d.tag, str) and d.get('id') in reach for d in n.iter())

    if prune_resources:
        for n in list(doc.iter()):
            if n.getparent() is None or not isinstance(n.tag, str): continue
            t = local(n); par = local(n.getparent())
            if t in ('metadata', 'script') or (t in ('title', 'desc') and n.getparent() is doc):
                n.getparent().remove(n); continue
            if par == 'defs' and t != 'style' and not needed(n):
                n.getparent().remove(n); continue
            if t in SERVERS and par != 'defs' and not needed(n):
                # a server nested in another reachable server stays with it
                p, inside_needed = n.getparent(), False
                while p is not None:
                    if local(p) in SERVERS and needed(p): inside_needed = True; break
                    p = p.getparent()
                if not inside_needed: n.getparent().remove(n)
        for d in list(doc.iter('{%s}defs' % SVG_NS, 'defs')):
            if d.getparent() is not None and not len(d): d.getparent().remove(d)
    if drop_fonts:
        clean_fonts(doc)

    # drop containers left empty (again: resource pruning can empty a <defs>-only group)
    empty_out(doc)

    if prefix:
        mapping = {}
        for n in doc.iter():
            if isinstance(n.tag, str) and n.get('id'):
                mapping[n.get('id')] = prefix + n.get('id'); n.set('id', mapping[n.get('id')])
        if mapping:
            sub = lambda v: URL_RE.sub(lambda m: 'url(#%s)' % mapping.get(m.group(1), m.group(1)), v)
            for n in doc.iter():
                if not isinstance(n.tag, str): continue
                for k, v in list(n.attrib.items()):
                    if 'url(' in v: n.set(k, sub(v))
                    elif k in (XLINK_HREF, 'href') and v.startswith('#') and v[1:] in mapping: n.set(k, '#' + mapping[v[1:]])
                if local(n) == 'style' and n.text and 'url(' in n.text: n.text = sub(n.text)
    if strip_idx:
        for n in doc.iter():
            if isinstance(n.tag, str) and IDX in n.attrib: del n.attrib[IDX]

    x0, y0, w, h = viewbox
    for k in ('width', 'height', 'x', 'y', 'preserveAspectRatio', 'enable-background'):
        if k in doc.attrib: del doc.attrib[k]
    if doc.get('style'):
        kept = [d for d in doc.get('style').split(';') if d.strip() and d.split(':')[0].strip().lower() not in
                ('width', 'height', 'background', 'background-color', 'overflow', 'position', 'left', 'top', 'margin')]
        if kept: doc.set('style', ';'.join(kept))
        else: del doc.attrib['style']
    doc.set('viewBox', '%.3f %.3f %.3f %.3f' % (x0, y0, w, h))
    doc.set('width', '%.3f' % w); doc.set('height', '%.3f' % h)
    if comment: doc.insert(0, etree.Comment(' ' + comment.replace('--', '- -') + ' '))
    return etree.tostring(doc, encoding='unicode')


HIDE_ATTR = 'data-cut-hide'


def _prefix_ids(doc, prefix):
    mapping = {}
    for n in doc.iter():
        if isinstance(n.tag, str) and n.get('id'):
            mapping[n.get('id')] = prefix + n.get('id'); n.set('id', mapping[n.get('id')])
    if not mapping: return
    sub = lambda v: URL_RE.sub(lambda m: 'url(#%s)' % mapping.get(m.group(1), m.group(1)), v)
    for n in doc.iter():
        if not isinstance(n.tag, str): continue
        for k, v in list(n.attrib.items()):
            if 'url(' in v: n.set(k, sub(v))
            elif k in (XLINK_HREF, 'href') and v.startswith('#') and v[1:] in mapping: n.set(k, '#' + mapping[v[1:]])
        if local(n) == 'style' and n.text and 'url(' in n.text: n.text = sub(n.text)


def hidden_reference(root, keep, viewbox, prefix='', clean=False):
    """The source with every non-selected drawable HIDDEN rather than deleted. Group bounding boxes (and with them
    objectBoundingBox clip/mask/pattern units), nested <svg> viewports and everything else stay exactly as in the
    source, so this is how the selection really looks in the figure -- the reference for fidelity checks. clean=True
    applies clean_fonts() as the cuts do, so text compares like with like."""
    keep = {str(i) for i in keep}
    doc = copy.deepcopy(root)
    _relocate_use_targets(doc, keep)
    if clean: clean_fonts(doc)

    def mark(node):
        for ch in node:
            t = local(ch)
            if t is None or t in RESOURCE: continue
            if t in CONTAINERS: mark(ch)
            elif ch.get(IDX) is not None and ch.get(IDX) not in keep: ch.set(HIDE_ATTR, '1')
    mark(doc)
    st = etree.Element('{%s}style' % SVG_NS)
    st.text = '[%s],[%s] *{visibility:hidden!important}' % (HIDE_ATTR, HIDE_ATTR)
    doc.insert(0, st)
    if prefix: _prefix_ids(doc, prefix)
    for n in doc.iter():
        if isinstance(n.tag, str) and IDX in n.attrib: del n.attrib[IDX]
    x0, y0, w, h = viewbox
    for k in ('width', 'height', 'x', 'y', 'preserveAspectRatio', 'enable-background', 'style'):
        if k in doc.attrib: del doc.attrib[k]
    doc.set('viewBox', '%.3f %.3f %.3f %.3f' % (x0, y0, w, h)); doc.set('width', '%.3f' % w); doc.set('height', '%.3f' % h)
    return etree.tostring(doc, encoding='unicode')


# ---------------------------------------------------------------------------
# rendering + comparison
# ---------------------------------------------------------------------------
def render_fit(items, size=230, css='', bg='#fff', cols=8):
    """items: [(key, svg_text)] -> {key: PIL RGB image (size x size)}; SVGs must not share ids (prefix them)."""
    return render_fit_groups([(items, css)], size=size, bg=bg, cols=cols)[0]


def render_fit_groups(groups, size=230, bg='#fff', cols=8):
    """groups: [(items, css)] rendered in one Chromium session -> [ {key: image} per group ]."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    results = [{} for _ in groups]
    if not any(items for items, _css in groups): return results
    cell = size + 10
    per = cols * 4                      # small pages: cuts can carry large embedded bitmaps
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--force-color-profile=srgb', '--disable-lcd-text'])
        for gi, (items, css) in enumerate(groups):
            for s in range(0, len(items), per):
                batch = items[s:s + per]
                rows = math.ceil(len(batch) / cols)
                pg = b.new_page(viewport={'width': cols * cell, 'height': rows * cell}, device_scale_factor=1)
                pg.set_default_timeout(240000)
                cells = []
                for key, svg in batch:
                    body = re.sub(r'^\s*<\?xml[^>]*\?>\s*', '', svg)
                    body = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"', r'\1', body, count=1)
                    body = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"', r'\1', body, count=1)
                    body = re.sub(r'<svg\b', '<svg width="%d" height="%d" preserveAspectRatio="xMidYMid meet" ' % (size, size), body, count=1)
                    cells.append('<div class="c">%s</div>' % body)
                html = page_html('<div class="g">%s</div>' % ''.join(cells), bg=bg,
                                 css='.g{display:grid;grid-template-columns:repeat(%d,%dpx)}.c{width:%dpx;height:%dpx;display:flex;'
                                     'align-items:center;justify-content:center;overflow:hidden;background:%s}%s' % (cols, cell, cell, cell, bg, css))
                pg.set_content(html, wait_until='load', timeout=120000)
                pg.evaluate('document.fonts.ready.then(()=>1)')
                shot = Image.open(io.BytesIO(pg.screenshot(full_page=True))).convert('RGB')
                pg.close()
                for k, (key, _svg) in enumerate(batch):
                    r, c = divmod(k, cols)
                    results[gi][key] = shot.crop((c * cell + 5, r * cell + 5, c * cell + 5 + size, r * cell + 5 + size))
        b.close()
    return results


def href_bytes(node):
    """Decoded bytes of a data-URI <image> href (None for external references)."""
    import base64
    h = (node.get(XLINK_HREF) or node.get('href') or '').strip()
    m = re.match(r'data:image/[a-z0-9+.-]+;base64,', h, re.I)
    if not m: return None
    try:
        return base64.b64decode(re.sub(r'\s+', '', h[m.end():]))
    except (ValueError, TypeError):
        return None


HIDE_TEXT_CSS = 'text,tspan{visibility:hidden!important}'


def diff_ratio(a, b, ink=245, tol=48):
    import numpy as np
    A = np.asarray(a, dtype=np.int16); B = np.asarray(b, dtype=np.int16)
    inked = (A < ink).any(axis=2) | (B < ink).any(axis=2)
    diff = (np.abs(A - B).max(axis=2) > tol) & inked
    n = int(inked.sum())
    return (float(diff.sum()) / n) if n else 0.0
