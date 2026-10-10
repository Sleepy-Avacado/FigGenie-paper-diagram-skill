#!/usr/bin/env python3
"""Merge the reviewer agents' output of a mechanism parts-mining package (mech_pool.py + cut_parts.py) into one
deduplicated set of kept parts, with contact sheets for the human pass.

  python3 scripts/distill/mech_merge.py --package mech-parts/pilot-evolution [--out <package>/result] [--drop review_drops.json]

Reads  <package>/agents/agent_*/review.jsonl  (+ cuts/<fig>/cuts.json and the pool's candidates.jsonl to
resolve each line's SVG) and writes under --out:
  kept.jsonl        one line per surviving part: the review fields + svg/thumb paths, size, colours, provenance
  rejected.jsonl    agent rejections, invalid lines, and merge drops (with `merge_reason`)
  stats.md          counts by agent / kind / family / group / style / quality, new families, drops, warnings
  discoveries.md    the agents' discoveries.md files concatenated
  sheets/<theme>_N.png + .json   numbered contact sheets (30 tiles), grouped by theme, for the human review
  tiles/            230 px tiles (sheets and silhouette checks)

Dedupe: identical geometry hash -> one survivor; nothing else is dropped or flagged automatically. Raster silhouette
comparisons (16x16 and 48x48 hashes, ink-cropped 64x64 masks) all paired unrelated parts -- a padlock with a video
frame, any filled block with a library card -- so near duplicates are left to the human pass on the theme sheets.
Lines kept by an agent but flagged `license` stock / emoji / logo are set aside as redraw candidates (rejected.jsonl
with merge_reason license-*, listed in stats.md). <package>/*_parts.tsv list the parts of the library and of earlier
waves: a bare family name that an earlier wave introduced as `new:<name>` gets its prefix restored, and a part name
already taken there is suffixed the same way as a clash inside this wave.
Nothing here writes into the skill; build_symbols.py --append does that after the human pass.
"""
import argparse, collections, csv, json, math, os, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import extract_parts as X          # noqa: E402
import cut_parts as C              # noqa: E402
import mech_svg as M               # noqa: E402

KINDS = ('icon', 'shape', 'motif', 'device')
THEMES = [
    ('steps-traces', {'step-badge', 'step-arrow-label', 'trace-path', 'return-path'}),
    ('frames-change', {'frame-border', 'frame-arrow', 'panel-label', 'ghost-copy', 'delta-highlight', 'strike-removed',
                       'swap-move-arrow', 'compare-marker', 'check-cross'}),
    ('logic-time', {'state-node', 'guarded-edge', 'decision-diamond', 'lane-divider', 'timeline-axis', 'time-span',
                    'message-arrow', 'clock-mark'}),
    ('structures', {'slot-array', 'pointer-cursor', 'matrix-cells', 'hash-bucket', 'tree-node', 'list-node', 'packet-token', 'hw-micro'}),
    ('annotations', {'zoom-callout', 'brace-annotation', 'formula-callout', 'legend-block', 'connector-style'}),
    ('icons', {'actor-icon', 'misc-icon'}),
]
QUALITY_RANK = {'clean': 0, 'ok': 1, 'rough': 2}
# Artwork a reviewer flags in `license` never enters the library (user decision): lines kept by the agent become
# candidates for an original redraw of the same subject, listed in stats.md.
LICENSE_EXCLUDED = ('stock', 'emoji', 'logo')


PKG_THEMES = {}            # family -> theme from <package>/family_themes.json (AI packages: the vocabulary's themes)
PKG_GROUPS = None          # allowed `groups` values from <package>/groups.json (AI packages: the figure kinds); None = mechanism v3 groups


def theme_of(family):
    if (family or '').startswith('new:'): return 'new-families'
    if family in PKG_THEMES: return PKG_THEMES[family]
    for name, fams in THEMES:
        if family in fams: return name
    return 'other'


def load_agent(adir, pool_cands, bitmaps=None, pkg=None):
    """-> (lines, problems). Each valid line gets `_svg`, `_meta` (cut / candidate / bitmap record)."""
    lines, problems = [], []
    rp = adir / 'review.jsonl'
    if not rp.exists(): return lines, ['%s: no review.jsonl' % adir.name]
    cuts_cache = {}
    for i, raw in enumerate(open(rp, encoding='utf-8'), 1):
        raw = raw.strip()
        if not raw: continue
        try: r = json.loads(raw)
        except json.JSONDecodeError as e:
            problems.append('%s:%d bad json (%s)' % (adir.name, i, e)); continue
        r['_agent'] = adir.name; r['_line'] = i
        fig, src, ref = r.get('figure'), (r.get('source') or 'cut'), r.get('ref') or r.get('name')
        if not fig or not ref: problems.append('%s:%d missing figure/ref' % (adir.name, i)); continue
        if src == 'candidate':
            c = pool_cands.get(ref)
            if not c: problems.append('%s:%d unknown candidate %s' % (adir.name, i, ref)); continue
            svg = Path(c['_pool']) / c['svg_path']
            meta = dict(w_pt=c['w_pt'], h_pt=c['h_pt'], n_elements=c['n_elements'], colors=c.get('colors_all') or c.get('colors') or [],
                        geom_hash=c.get('geom_hash'), scale=c.get('scale'), source_file=c.get('file'), texts=c.get('hint_text', ''),
                        bbox_src=c.get('bbox_src'), occurrences=c.get('occurrences', 1))
        elif src == 'bitmap':
            b = (bitmaps or {}).get(ref)
            if not b: problems.append('%s:%d unknown bitmap %s' % (adir.name, i, ref)); continue
            if not b.get('svg'): problems.append('%s:%d bitmap %s has no vector trace' % (adir.name, i, ref)); continue
            svg = Path(pkg) / 'bitmaps' / b['svg']
            t = b.get('trace') or {}
            meta = dict(w_pt=b['disp_pt'][0], h_pt=b['disp_pt'][1], n_elements=t.get('layers', 0), colors=t.get('colors') or [],
                        geom_hash=ref, scale=1.0, source_file=None, texts=' | '.join(b['contexts'][0].get('texts') or []),
                        bbox_src=None, occurrences=b.get('occurrences', 1), trace=t, raster=str(Path(pkg) / 'bitmaps' / b['png']),
                        warnings=[] if b.get('trace_ok') else ['vector trace below the fidelity threshold'])
        else:
            if fig not in cuts_cache:
                cp = adir / 'cuts' / fig / 'cuts.json'
                cuts_cache[fig] = {c['name']: c for c in json.load(open(cp, encoding='utf-8'))['cuts']} if cp.exists() else {}
            c = cuts_cache[fig].get(ref) or cuts_cache[fig].get(C.slug(ref))
            if not c or not c.get('svg'): problems.append('%s:%d no cut named %s in %s' % (adir.name, i, ref, fig)); continue
            svg = Path(c['svg'])
            meta = dict(w_pt=c['w_pt'], h_pt=c['h_pt'], n_elements=c['n_elements'], colors=c.get('colors') or [], geom_hash=c.get('geom_hash'),
                        scale=c.get('scale'), source_file=c.get('source_file'), texts=c.get('texts', ''), bbox_src=c.get('bbox_src'),
                        bbox_pt=c.get('bbox_pt'), warnings=c.get('warnings') or [], occurrences=1,
                        fidelity_diff=c.get('fidelity_diff'), bitmaps=c.get('bitmaps') or [])
        if not svg.exists(): problems.append('%s:%d svg missing %s' % (adir.name, i, svg)); continue
        r['_svg'] = str(svg); r['_meta'] = meta
        lines.append(r)
    return lines, problems


def normalise(r, earlier_new=frozenset()):
    """Fill defaults, clean enumerations; returns a list of warnings. `earlier_new`: families an earlier wave
    introduced as new:<name>, so a reviewer who wrote the bare name gets the prefix back."""
    w = []
    r['name'] = C.slug(r.get('name') or r.get('ref'))
    k = (r.get('kind') or '').lower()
    if k not in KINDS: w.append('kind %r -> device' % k); k = 'device'
    r['kind'] = k
    fam = (r.get('family') or '').strip().lower().replace(' ', '-')
    if not fam: w.append('no family -> other'); fam = 'other'
    if fam in earlier_new: w.append('earlier-wave family written without new: prefix -> restored'); fam = 'new:' + fam
    r['family'] = fam
    g = r.get('groups') or []
    if isinstance(g, str): g = [g]
    allowed = PKG_GROUPS or ('comparison', 'evolution', 'logic', 'walkthrough', 'anatomy')
    r['groups'] = [x for x in g if x in allowed] or [allowed[0]]
    r['style'] = (r.get('style') or 'flat').lower(); r['quality'] = (r.get('quality') or 'ok').lower()
    if r['quality'] not in QUALITY_RANK: r['quality'] = 'ok'
    r['tags'] = [str(t).lower() for t in (r.get('tags') or [])][:12]
    r['depicts'] = (r.get('depicts') or '').strip()
    return w


def svg_prefixed(svg, prefix):
    """SVG text with every id (and reference to it) prefixed, so several parts can share one render page."""
    from lxml import etree
    doc = etree.fromstring(svg.encode('utf-8'), parser=etree.XMLParser(recover=True, huge_tree=True))
    M._prefix_ids(doc, prefix)
    return etree.tostring(doc, encoding='unicode')


def render_tiles(named_svgs, out_dir, size=C.TILE):
    """[(name, svg_text)] -> out_dir/<name>.png, each part fitted into a size x size tile on white."""
    out_dir.mkdir(parents=True, exist_ok=True)
    imgs = M.render_fit([(n, svg_prefixed(sv, 't%d-' % i)) for i, (n, sv) in enumerate(named_svgs)], size=size)
    for n, im in imgs.items(): im.save(out_dir / (n + '.png'))


def draw_theme_sheet(rows, tiles_dir, out_png, title, cols=5, per_row_h=None):
    from PIL import Image, ImageDraw
    F = X._fonts()
    T = C.TILE; tw, th = T + 16, T + 80
    nrows = max(1, -(-len(rows) // cols))
    img = Image.new('RGB', (cols * tw + 20, nrows * th + 50), '#ffffff'); dr = ImageDraw.Draw(img)
    dr.text((10, 10), title[:140], fill='#111111', font=F['hdr'])
    for k, r in enumerate(rows):
        rr, c = divmod(k, cols); x = 10 + c * tw; y = 40 + rr * th
        dr.rectangle([x, y, x + tw - 6, y + th - 6], outline='#d8d8d8')
        tp = tiles_dir / (r['name'] + '.png')
        if tp.exists():
            try: img.paste(Image.open(tp).convert('RGB'), (x + 8, y + 26))
            except Exception: pass          # noqa: BLE001
        dr.rectangle([x + 3, y + 3, x + 40, y + 21], fill='#1a1a1a'); dr.text((x + 8, y + 2), str(k + 1), fill='#ffffff', font=F['num'])
        dr.text((x + 46, y + 6), r['name'][:30], fill='#0b57a4', font=F['lbl'])
        ln = y + 26 + T + 2
        dr.text((x + 8, ln), '%s · %s · %.0fx%.0f pt · %s' % (r['family'][:22], r['kind'], r['_meta']['w_pt'], r['_meta']['h_pt'], r['quality']),
                fill='#333333', font=F['txt'])
        dr.text((x + 8, ln + 13), (r.get('depicts') or '')[:48], fill='#555555', font=F['txt'])
        dr.text((x + 8, ln + 26), ('%s  %s' % (r['figure'], r['_agent']))[:52], fill='#999999', font=F['txt'])
    img.save(out_png)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--package', required=True); ap.add_argument('--out', default=None)
    ap.add_argument('--no-sheets', action='store_true')
    ap.add_argument('--drop', default=None, help='JSON list of {figure, ref, reason}: parts a review pass dropped (rejected.jsonl, merge_reason review-drop:<reason>)')
    a = ap.parse_args()
    t0 = time.time()
    pkg = Path(a.package); out = Path(a.out) if a.out else pkg / 'result'
    global PKG_THEMES, PKG_GROUPS
    if (pkg / 'family_themes.json').exists(): PKG_THEMES = json.load(open(pkg / 'family_themes.json', encoding='utf-8'))
    if (pkg / 'groups.json').exists(): PKG_GROUPS = tuple(json.load(open(pkg / 'groups.json', encoding='utf-8')))
    tiles = out / 'tiles'; sheets = out / 'sheets'
    for d in (tiles, sheets): d.mkdir(parents=True, exist_ok=True)
    for old in sheets.glob('*'): old.unlink()          # sheets of an earlier merge must not linger
    pool_cands = {}
    pool = pkg / 'pool'
    if (pool / 'candidates.jsonl').exists():
        for line in open(pool / 'candidates.jsonl', encoding='utf-8'):
            if line.strip():
                c = json.loads(line); c['_pool'] = str(pool); pool_cands[c['candidate_id']] = c

    # ---- collect ---------------------------------------------------------------
    lines, problems, disc = [], [], []
    bitmaps = {}
    if (pkg / 'bitmaps' / 'index.json').exists():
        bitmaps = {e['bid']: e for e in json.load(open(pkg / 'bitmaps' / 'index.json', encoding='utf-8'))['entries']}
    agent_dirs = sorted(p for p in (pkg / 'agents').glob('agent_*') if p.is_dir())
    for adir in agent_dirs:
        ls, pr = load_agent(adir, pool_cands, bitmaps, pkg); lines += ls; problems += pr
        dp = adir / 'discoveries.md'
        if dp.exists(): disc.append('# %s\n\n%s' % (adir.name, dp.read_text(encoding='utf-8')))
    kept = [r for r in lines if r.get('keep') is True and (r.get('license') or 'ok') not in LICENSE_EXCLUDED]
    redraw = [r for r in lines if r.get('keep') is True and (r.get('license') or 'ok') in LICENSE_EXCLUDED]
    rejected = [dict(r, merge_reason='agent-rejected') for r in lines if r.get('keep') is not True]
    rejected += [dict(r, merge_reason='license-%s:redraw-candidate' % r['license']) for r in redraw]
    dropped = []
    if a.drop:
        want = {(d['figure'], d['ref']): d.get('reason') or 'review' for d in json.load(open(a.drop, encoding='utf-8'))}
        dropped = [r for r in kept if (r.get('figure'), r.get('ref')) in want]
        kept = [r for r in kept if (r.get('figure'), r.get('ref')) not in want]
        rejected += [dict(r, merge_reason='review-drop:%s' % want[(r['figure'], r['ref'])]) for r in dropped]
        missing = sorted(set(want) - {(r['figure'], r['ref']) for r in dropped})
        print('review drop list: %d dropped%s' % (len(dropped), ('; not among the kept parts: %s' % missing) if missing else ''), flush=True)
    # parts of the library and of earlier waves (<package>/*_parts.tsv: name, kind, family, depicts, figure): their
    # new: families keep the prefix here, their names stay unique
    earlier_names, earlier_new = set(), set()
    for ep in sorted(pkg.glob('*_parts.tsv')):
        for row in csv.DictReader(open(ep, encoding='utf-8'), delimiter='\t'):
            earlier_names.add(row.get('name') or '')
            if (row.get('family') or '').startswith('new:'): earlier_new.add(row['family'][4:])
        print('%s: %d parts so far, %d new: families' % (ep.name, len(earlier_names), len(earlier_new)), flush=True)
    warn = collections.Counter()
    for r in kept:
        for w in normalise(r, earlier_new): warn[w] += 1
    # unique names across agents and waves
    seen = collections.Counter({n: 1 for n in earlier_names})
    for r in sorted(kept, key=lambda r: (r['_agent'], r['_line'])):
        seen[r['name']] += 1
        if seen[r['name']] > 1: r['name'] = '%s-%d' % (r['name'], seen[r['name']])
    print('agents %d, review lines %d, kept %d, agent-rejected %d, licence-excluded %d, review-dropped %d, problems %d' % (
        len(agent_dirs), len(lines), len(kept), len(lines) - len(kept) - len(dropped) - len(redraw), len(redraw), len(dropped), len(problems)), flush=True)

    # ---- dedupe 1: geometry ------------------------------------------------------
    by_geom = collections.defaultdict(list)
    for r in kept: by_geom[r['_meta'].get('geom_hash') or r['name']].append(r)
    survivors = []
    for gh, members in by_geom.items():
        members.sort(key=lambda r: (QUALITY_RANK.get(r['quality'], 1), -(r['_meta']['w_pt'] * r['_meta']['h_pt'])))
        survivors.append(members[0])
        members[0]['dups_geom'] = [m['name'] for m in members[1:]]
        for m in members[1:]: rejected.append(dict(m, merge_reason='same-geometry-as:' + members[0]['name']))
    print('after geometry dedupe: %d' % len(survivors), flush=True)

    # ---- tiles ------------------------------------------------------------------------------
    print('rendering %d tiles...' % len(survivors), flush=True)
    render_tiles([(r['name'], open(r['_svg'], encoding='utf-8').read()) for r in survivors], tiles)
    final = survivors

    # ---- outputs ---------------------------------------------------------------------
    final.sort(key=lambda r: (theme_of(r['family']), r['family'], r['kind'], r['name']))
    for r in final:
        r['theme'] = theme_of(r['family']); r['thumb'] = str(tiles / (r['name'] + '.png'))
    with open(out / 'kept.jsonl', 'w', encoding='utf-8') as fh:
        for r in final:
            d = {k: v for k, v in r.items() if not k.startswith('_')}
            d.update(agent=r['_agent'], svg=r['_svg'], size_pt=[r['_meta']['w_pt'], r['_meta']['h_pt']], n_elements=r['_meta']['n_elements'],
                     colors=r['_meta']['colors'], geom_hash=r['_meta'].get('geom_hash'), scale=r['_meta'].get('scale'),
                     source_file=r['_meta'].get('source_file'), bbox_src=r['_meta'].get('bbox_src'), cut_warnings=r['_meta'].get('warnings') or [])
            for k in ('fidelity_diff', 'bitmaps', 'trace', 'raster', 'occurrences'):
                if r['_meta'].get(k) is not None: d[k] = r['_meta'][k]
            fh.write(json.dumps(d, ensure_ascii=False) + '\n')
    with open(out / 'rejected.jsonl', 'w', encoding='utf-8') as fh:
        for r in rejected:
            d = {k: v for k, v in r.items() if not k.startswith('_')}; d['agent'] = r.get('_agent')
            fh.write(json.dumps(d, ensure_ascii=False) + '\n')
    (out / 'discoveries.md').write_text('\n\n---\n\n'.join(disc) or '(no discoveries.md found)\n', encoding='utf-8')

    # sheets
    n_sheets = 0
    if not a.no_sheets and final:
        by_theme = collections.defaultdict(list)
        for r in final: by_theme[r['theme']].append(r)
        order = [t for t, _ in THEMES] + sorted(set(PKG_THEMES.values())) + ['new-families', 'other']
        for t in order:
            rows = by_theme.get(t) or []
            for s in range(0, len(rows), 30):
                batch = rows[s:s + 30]; n = s // 30 + 1
                png = sheets / ('%s_%d.png' % (t, n))
                draw_theme_sheet(batch, tiles, str(png), '%s  %d-%d of %d   (families: %s)' % (
                    t, s + 1, s + len(batch), len(rows), ', '.join(sorted({r['family'] for r in batch}))[:80]))
                json.dump({'theme': t, 'sheet': n, 'tiles': {str(k + 1): {'name': r['name'], 'family': r['family'], 'kind': r['kind'], 'figure': r['figure'],
                                                                         'agent': r['_agent'], 'svg': r['_svg']}
                                                             for k, r in enumerate(batch)}},
                          open(str(png)[:-4] + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
                n_sheets += 1

    # stats
    cnt = lambda key: collections.Counter(key(r) for r in final)
    L = ['# Merge report — %s' % pkg.name, '', 'generated in %.1f min' % ((time.time() - t0) / 60), '',
         '| stage | count |', '|---|---|', '| review lines | %d |' % len(lines), '| kept by agents | %d |' % (len(kept) + len(dropped)),
         '| dropped after review (--drop) | %d |' % len(dropped),
         '| after geometry dedupe | %d |' % len(survivors), '| final | %d |' % len(final),
         '| licence-excluded (kept by agents, set aside as redraw candidates) | %d |' % len(redraw), '| problems (invalid lines) | %d |' % len(problems), '']
    if dropped:
        L += ['## dropped after review', '', '| name | reason | figure | agent | family |', '|---|---|---|---|---|']
        L += ['| %s | %s | %s | %s | %s |' % (r.get('name') or r.get('ref'), want[(r['figure'], r['ref'])], r['figure'], r['_agent'], r.get('family'))
              for r in dropped] + ['']
    if redraw:
        L += ['## licence-excluded: redraw candidates', '',
              'Flagged artwork (stock / emoji / logo) is not added to the library. Redraw the subject as an original icon; do not trace the artwork.', '',
              '| name | license | figure | agent | depicts |', '|---|---|---|---|---|']
        L += ['| %s | %s | %s | %s | %s |' % (r.get('name') or r.get('ref'), r['license'], r['figure'], r['_agent'], (r.get('depicts') or '').replace('|', '/'))
              for r in redraw] + ['']
    for title, key in (('agent', lambda r: r['_agent']), ('kind', lambda r: r['kind']), ('theme', lambda r: r['theme']), ('style', lambda r: r['style']),
                       ('quality', lambda r: r['quality']), ('source', lambda r: r.get('source') or 'cut')):
        L += ['## by %s' % title, '', ', '.join('%s %d' % kv for kv in sorted(cnt(key).items())), '']
    L += ['## by family', '', '| family | theme | kept | figures | agents |', '|---|---|---|---|---|']
    fam = collections.defaultdict(list)
    for r in final: fam[r['family']].append(r)
    for f, rs in sorted(fam.items(), key=lambda kv: (theme_of(kv[0]), -len(kv[1]))):
        L.append('| %s | %s | %d | %d | %s |' % (f, theme_of(f), len(rs), len({r['figure'] for r in rs}), ', '.join(sorted({r['_agent'] for r in rs}))))
    L += ['', '## groups served', '', ', '.join('%s %d' % kv for kv in sorted(collections.Counter(g for r in final for g in r['groups']).items())), '']
    figs_done = collections.Counter(r['figure'] for r in lines)
    L += ['## figures', '', '%d figures produced review lines; parts per figure: min %d, median %d, max %d' % (
        len(figs_done), min(figs_done.values()) if figs_done else 0, sorted(figs_done.values())[len(figs_done) // 2] if figs_done else 0, max(figs_done.values()) if figs_done else 0), '']
    if warn: L += ['## normalisation warnings', ''] + ['- %s ×%d' % kv for kv in warn.most_common()] + ['']
    if problems: L += ['## problems', ''] + ['- %s' % p for p in problems[:80]] + ['']
    L += ['## sheets', '', '%d sheets under sheets/ (30 tiles each, grouped by theme; the .json next to each maps tile numbers to names)' % n_sheets, '']
    (out / 'stats.md').write_text('\n'.join(L), encoding='utf-8')
    print('final %d parts, %d sheets -> %s (%.1f min)' % (len(final), n_sheets, out, (time.time() - t0) / 60))


if __name__ == '__main__':
    main()
