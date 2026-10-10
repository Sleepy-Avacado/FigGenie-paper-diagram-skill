#!/usr/bin/env python3
"""Find exemplars by what the figure is about, not only by template: research domain, drawn content, meaning.

  python3 scripts/find_exemplars.py --domain "llm serving, kv cache" \
      --content "prefill instance, decode instance, scheduler, shared memory pool" \
      --semantics "prefill and decode share one KV cache pool over RDMA" --template control-data
  python3 scripts/find_exemplars.py "hash table resize, buckets" --kind mechanism --group evolution -n 6
  python3 scripts/find_exemplars.py ... --json

Every exemplar's `semantics.json` (the 485 corpus ones and the named styles' figures) is scored on three dimensions, each against its own fields:
  domain     system.domain, tags, system.one_liner              (what research area / system)
  content    components / elements (name + role), flows, depicts, subject   (what is drawn)
  semantics  key_idea, summary, one_liner, reading_order, caption           (what the figure argues)
A positional query is matched against all three. Terms are weighted by rarity (a rare word like "prefill" counts
far more than "system"), multi-word phrases ("kv cache") get a bonus when they appear whole. --kind, --template
and --group only add a bonus; nothing is filtered out, so a mechanism figure from the same field can still show how
that field draws its objects. At most two figures per paper. Output: id, kind, templates / groups (* = starred),
system, one-liner, the matched terms per dimension, and the print.png path to LOOK at.

The figures of the named styles (`assets/exemplars/styles/<style>/figures/`, one paper each, see
references/styles/README.md) are searched with the corpus ones and marked `style: <name>`; `--style <name>` gives
them a bonus and lists every figure of that style first, so a figure drawn in that style can borrow its devices.
"""
import argparse, json, math, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / 'assets' / 'exemplars' / 'figures'
STYLES = ROOT / 'assets' / 'exemplars' / 'styles'
STOP = set('a an and are as at be by for from in into is it its of on or that the this to with via its their each '
           'one two which when where how what who than then them they these those our we figure fig shows show '
           'shown using used use per all any both let lets make makes can may also so not only'.split())
WEIGHT = {'domain': 1.6, 'content': 1.2, 'semantics': 1.0}


def norm_word(w):
    w = w.lower()
    for suf in ('ies', 'es', 's'):
        if len(w) > 4 and w.endswith(suf) and not w.endswith('ss'):
            return w[:-len(suf)] + ('y' if suf == 'ies' else '')
    return w


def words(text):
    return [norm_word(w) for w in re.findall(r'[A-Za-z0-9]+', text or '') if w.lower() not in STOP]


def flat(x):
    if isinstance(x, str): return x
    if isinstance(x, dict): return ' '.join(flat(v) for v in x.values())
    if isinstance(x, list): return ' '.join(flat(v) for v in x)
    return ''


def fields(sem, man):
    sysm, con = sem.get('system') or {}, sem.get('content') or {}
    parts = con.get('components') or con.get('elements') or []
    return {
        'domain': ' '.join([flat(sysm.get('domain')).replace('-', ' '), flat(sem.get('tags')).replace('-', ' '),
                            sysm.get('one_liner') or '']),
        'content': ' '.join([' '.join(f"{p.get('name', '')} {p.get('role', '')}" for p in parts),
                             ' '.join(f"{f.get('what', '')}" for f in con.get('flows') or []),
                             flat(con.get('depicts')), flat(con.get('subject')), flat(con.get('groups'))]),
        'semantics': ' '.join([flat(con.get('key_idea')), flat(sem.get('summary')), sysm.get('one_liner') or '',
                               flat(con.get('reading_order')), man.get('caption') or '']),
    }


def figure_dirs():
    dirs = sorted(d for d in FIG.iterdir() if d.is_dir())
    if STYLES.is_dir():
        dirs += sorted(d for d in STYLES.glob('*/figures/*') if d.is_dir())
    return dirs


def load():
    figs = []
    for d in figure_dirs():
        sp, mp = d / 'semantics.json', d / 'manifest.json'
        if not sp.exists(): continue
        sem, man = json.loads(sp.read_text()), json.loads(mp.read_text()) if mp.exists() else {}
        f = fields(sem, man)
        figs.append({'id': d.name, 'dir': d, 'sem': sem, 'man': man, 'text': {k: v.lower() for k, v in f.items()},
                     'bag': {k: set(words(v)) for k, v in f.items()}})
    return figs


def terms(spec):
    """'kv cache, prefill instance' -> phrases ['kv cache', 'prefill instance'] and their words."""
    phrases = [p.strip().lower() for p in re.split(r'[,;\n]', spec or '') if p.strip()]
    return phrases, [w for p in phrases for w in words(p)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('query', nargs='?', default='', help='free text, matched against all three dimensions')
    ap.add_argument('--domain', default='', help='research area / system kind, comma-separated')
    ap.add_argument('--content', default='', help='what the figure draws: components, structures, objects')
    ap.add_argument('--semantics', default='', help='what the figure argues, in a phrase or a sentence')
    ap.add_argument('--kind', choices=['architecture', 'mechanism'], help='bonus for this figure kind')
    ap.add_argument('--template', help='bonus for exemplars of this architecture template')
    ap.add_argument('--group', help='bonus for exemplars of this mechanism group')
    ap.add_argument('--style', help='a named style (references/styles/): its figures get a bonus and are listed first')
    ap.add_argument('-n', type=int, default=8, help='how many to list (default 8)')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    figs = load()
    df = Counter(w for f in figs for w in set().union(*f['bag'].values()))
    idf = lambda w: math.log((len(figs) + 1) / (df.get(w, 0) + 1)) + 0.1

    asks = {k: terms(getattr(a, k)) for k in WEIGHT}
    if a.query:
        for k in WEIGHT:
            ph, ws = terms(a.query)
            asks[k] = (asks[k][0] + ph, asks[k][1] + ws)
    if not any(ws for _, ws in asks.values()) and not a.style:
        ap.error('give a query, --domain, --content or --semantics (or --style)')

    scored = []
    for f in figs:
        score, hits = 0.0, {}
        for dim, (phrases, ws) in asks.items():
            got = sorted({w for w in ws if w in f['bag'][dim]})
            s = sum(idf(w) for w in got)
            whole = [p for p in phrases if ' ' in p and p in f['text'][dim]]
            s += sum(1.5 * sum(idf(w) for w in words(p)) / max(1, len(words(p))) for p in whole)
            if got: hits[dim] = got
            score += WEIGHT[dim] * s
        man = f['man']; kind = man.get('kind') or f['sem'].get('kind') or 'architecture'
        tpls = [t['template'] + ('*' if t.get('star') else '') for t in man.get('templates') or []]
        grps = [g['group'] + ('*' if g.get('star') else '') for g in man.get('groups') or []]
        if a.kind and kind == a.kind: score *= 1.15
        if a.template and any(t.rstrip('*') == a.template for t in tpls): score *= 1.15
        if a.group and any(g.rstrip('*') == a.group for g in grps): score *= 1.15
        style = man.get('style')
        in_style = bool(a.style) and style == a.style
        if in_style: score = score * 1.3 + 0.01
        if score > 0:
            sysm = f['sem'].get('system') or {}
            scored.append({'id': f['id'], 'score': round(score, 2), 'kind': kind, 'templates': tpls, 'groups': grps,
                           'venue': man.get('venue'), 'system': sysm.get('name'), 'style': style,
                           'in_style': in_style,
                           'one_liner': sysm.get('one_liner'), 'matched': hits,
                           'print': str((f['dir'] / 'print.png').relative_to(ROOT))})
    scored.sort(key=lambda r: (not r['in_style'], -r['score']))
    out, per_paper = [], Counter()
    for r in scored:
        paper = r['id'].rsplit('_', 1)[0]
        if per_paper[paper] >= 2 and not r['in_style']: continue
        per_paper[paper] += 1; out.append(r)
        if sum(1 for o in out if not o['in_style']) >= a.n: break      # the style's own figures come on top of -n

    if a.json:
        print(json.dumps(out, indent=1, ensure_ascii=False)); return
    for i, r in enumerate(out, 1):
        where = ', '.join(r['templates'] or r['groups'])
        tag = f"  style: {r['style']}" if r['style'] else ''
        print(f"{i}. {r['id']}  [{r['kind']}: {where}]  {r['venue']}  score {r['score']}{tag}")
        print(f"   {r['system']}: {(r['one_liner'] or '')[:150]}")
        print('   matched  ' + '  |  '.join(f"{k}: {' '.join(v)}" for k, v in r['matched'].items()))
        print(f"   LOOK at  {r['print']}")


if __name__ == '__main__':
    main()
