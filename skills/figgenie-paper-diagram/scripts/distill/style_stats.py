#!/usr/bin/env python3
"""Quantify style rules for systems-conference architecture diagrams.

Reads the corpus index, keeps rows with type == 'diagram' and subtype ==
'architecture', and for every numeric/categorical field of the `style` JSON
column (see paper-figure-corpus/scripts/svg_features.py + style_of() in
classify_figures.py for exactly how each field is measured) computes:

  1. per-group distributions (good / ok / bad / discard / good_src), split by
     column (single / double / all) -- p5/p25/p50/p75/p95/mean for numeric
     metrics, frequency tables for categorical ones.
  2. a good-vs-(ok+bad) contrast: Cliff's delta (rank-biserial effect size)
     and a Mann-Whitney U p-value for numeric metrics (Benjamini-Hochberg
     FDR-adjusted within each column split), and frequency differences with a
     two-proportion z-test for categorical metrics.
  3. a diagnostic good-vs-bad-only contrast (bad n=32 total, n=1 for double
     column -- treat as exploratory, not a rule source).
  4. tool x aesthetic and venue x aesthetic cross-tabs.

Only the stdlib + numpy are required; scipy is used for the Mann-Whitney
p-value when available and a hand-written normal-approximation (with tie
correction) is used otherwise -- both paths are exercised by --self-test.

Usage:
    python3 style_stats.py [--index PATH] [--out DIR] [--min-n N] [--subtype architecture|mechanism] [--self-test]

--subtype mechanism runs the same analysis over the mechanism figures (kind 2 of the skill); the
meta key n_architecture_rows then counts mechanism rows (name kept for build_thresholds.py).

Outputs written to --out (all CSV except summary.json):
    metrics_per_figure.csv       one row per architecture figure, every metric
    numeric_distributions.csv    metric x group x column split -> p5..p95/mean
    categorical_distributions.csv metric x group x column split x value -> freq
    contrast_numeric.csv         good vs ok+bad, per numeric metric x split
    contrast_numeric_bad_only.csv good vs bad only (diagnostic, low power)
    contrast_categorical.csv     good vs ok+bad, per categorical value x split
    tool_by_aesthetic.csv        tool x aesthetic counts/fractions
    venue_by_aesthetic.csv       venue x aesthetic counts/fractions
    summary.json                 everything above, nested, for the doc-writing step
"""
import argparse
import bisect
import csv
import json
import math
import os
import sys
from collections import Counter

try:
    import numpy as np
except ImportError:
    np = None

try:
    from scipy import stats as _scipy_stats
    HAVE_SCIPY = True
except ImportError:
    _scipy_stats = None
    HAVE_SCIPY = False

csv.field_size_limit(10**9)

TYPE, SUBTYPE = 'diagram', 'architecture'
COL_WIDTH = {'single': 240.0, 'double': 504.0}   # canonical printed column widths, pt
GROUPS = ['good', 'ok', 'bad', 'discard', 'good_src']
SPLITS = ['all', 'single', 'double']
PCTS = (5, 25, 50, 75, 95)
DEFAULT_INDEX = 'lab/extracted/corpus_index.csv'
DEFAULT_OUT = 'distill-out/step1/style_stats'


# ----------------------------------------------------------------------------
# JSON access helpers
# ----------------------------------------------------------------------------

def get(d, *path, default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(p, default)
    return default if cur is None else cur


def safe_div(a, b):
    return (a / b) if b else None


def eff_column(row_column, style):
    """single/double, inferring from size.w when the CSV column field is blank."""
    if row_column in ('single', 'double'):
        return row_column
    w = get(style, 'size', 'w', default=0) or 0
    return 'double' if w >= 380 else 'single'


# ----------------------------------------------------------------------------
# metric extraction -- the single place that defines what we measure
# ----------------------------------------------------------------------------

def build_metrics(style, col_eff):
    """-> (numeric_dict, categorical_dict) for one figure's parsed `style` JSON."""
    heads = get(style, 'arrows', 'heads', default=0) or 0
    curved = get(style, 'arrows', 'curved', default=0) or 0
    lines = get(style, 'arrows', 'lines', default=0) or 0
    fsize = get(style, 'font', 'size', default=[0, 0, 0]) or [0, 0, 0]
    fsize = (list(fsize) + [0, 0, 0])[:3]
    w = get(style, 'size', 'w', default=0) or 0
    h = get(style, 'size', 'h', default=0) or 0
    text = get(style, 'density', 'text', default=0) or 0
    shapes = get(style, 'density', 'shapes', default=0) or 0
    circled = get(style, 'steps', 'circled', default=0) or 0
    area100 = (w * h / 10000.0) if (w and h) else None

    numeric = {
        'palette.n': get(style, 'palette', 'n', default=0),
        'palette.gray_frac': get(style, 'palette', 'gray_frac', default=0.0),
        'palette.n_hues': len(get(style, 'palette', 'hues', default=[]) or []),
        'stroke.median': get(style, 'stroke', 'median', default=0.0),
        'stroke.widths': get(style, 'stroke', 'widths', default=0),
        'arrows.heads': heads,
        'arrows.curved': curved,
        'arrows.lines': lines,
        'arrows.curved_ratio': safe_div(curved, curved + lines) if (curved + lines) else None,
        'arrows.heads_per_line': safe_div(heads, lines),
        'icons.images': get(style, 'icons', 'images', default=0),
        'icons.image_area': get(style, 'icons', 'image_area', default=0.0),
        'icons.glyph_paths': get(style, 'icons', 'glyph_paths', default=0),
        'steps.circled_count': circled,
        'steps.digits': get(style, 'steps', 'digits', default=0),
        'font.size_min': fsize[0],
        'font.size_med': fsize[1],
        'font.size_max': fsize[2],
        'font.bold': get(style, 'font', 'bold', default=0.0),
        'density.text': text,
        'density.shapes': shapes,
        'density.per_100pt2': get(style, 'density', 'per_100pt2', default=0.0),
        'density.text_boxes': get(style, 'density', 'text_boxes', default=0),
        'density.text_per_100pt2': safe_div(text, area100),
        'density.shapes_per_100pt2': safe_div(shapes, area100),
        'size.w': w,
        'size.h': h,
        'size.aspect': get(style, 'size', 'aspect', default=None),
        'font.size_med_over_colwidth': safe_div(fsize[1], COL_WIDTH.get(col_eff)),
    }
    categorical = {
        'palette.named': get(style, 'palette', 'named', default='') or '(none)',
        'fill': get(style, 'fill', default='') or '(unknown)',
        'stroke.dashed': bool(get(style, 'stroke', 'dashed', default=False)),
        'corners': get(style, 'corners', default='') or '(unknown)',
        'steps.circled_present': bool(circled and circled > 0),
        'font.cls': get(style, 'font', 'cls', default='') or '(unknown)',
    }
    return numeric, categorical


NUM_KEYS = list(build_metrics({}, 'single')[0].keys())
CAT_KEYS = list(build_metrics({}, 'single')[1].keys())


# ----------------------------------------------------------------------------
# loading
# ----------------------------------------------------------------------------

def load(index_path, subtype=SUBTYPE):
    recs = []
    n_total = 0
    n_bad_json = 0
    with open(index_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            n_total += 1
            if row.get('type') != TYPE or row.get('subtype') != subtype:
                continue
            raw = row.get('style') or ''
            style = {}
            if raw.strip():
                try:
                    style = json.loads(raw)
                except json.JSONDecodeError:
                    n_bad_json += 1
                    style = {}
            col_eff = eff_column(row.get('column') or '', style)
            numeric, categorical = build_metrics(style, col_eff)
            rec = dict(
                paper_id=row.get('paper_id', ''), fig=row.get('fig', ''), venue=row.get('venue', ''),
                year=row.get('year', ''), aesthetic=row.get('aesthetic') or '',
                has_source=bool((row.get('src_svgs') or '').strip()),
                column_raw=row.get('column') or '', column_eff=col_eff,
                tool=row.get('tool') or 'unknown', tool_source=row.get('tool_source') or '',
                label_source=row.get('label_source') or '',
            )
            rec.update(numeric)
            rec.update(categorical)
            recs.append(rec)
    return recs, n_total, n_bad_json


def in_group(rec, g):
    if g == 'good_src':
        return rec['aesthetic'] == 'good' and rec['has_source']
    return rec['aesthetic'] == g


def in_split(rec, sp):
    return sp == 'all' or rec['column_eff'] == sp


# ----------------------------------------------------------------------------
# numeric stats
# ----------------------------------------------------------------------------

def pct_stats(values):
    vals = [v for v in values if v is not None]
    n = len(vals)
    if n == 0:
        return dict(n=0, mean=None, p5=None, p25=None, p50=None, p75=None, p95=None)
    if np is not None:
        arr = np.asarray(vals, dtype=float)
        p5, p25, p50, p75, p95 = (float(x) for x in np.percentile(arr, PCTS))
        mean = float(arr.mean())
    else:
        s = sorted(vals)
        def pct(p):
            if n == 1:
                return s[0]
            k = (p / 100) * (n - 1)
            lo, hi = math.floor(k), math.ceil(k)
            if lo == hi:
                return s[int(k)]
            return s[lo] + (s[hi] - s[lo]) * (k - lo)
        p5, p25, p50, p75, p95 = (pct(p) for p in PCTS)
        mean = sum(s) / n
    return dict(n=n, mean=round(mean, 4), p5=round(p5, 4), p25=round(p25, 4),
                p50=round(p50, 4), p75=round(p75, 4), p95=round(p95, 4))


def cliffs_delta(a, b):
    a = [x for x in a if x is not None]
    b = [x for x in b if x is not None]
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return None, n, m
    sb = sorted(b)
    more = less = 0
    for x in a:
        l = bisect.bisect_left(sb, x)
        r = bisect.bisect_right(sb, x)
        more += l              # b_j < x  -> a_i > b_j
        less += (m - r)        # b_j > x  -> a_i < b_j
    return (more - less) / (n * m), n, m


def delta_magnitude(d):
    if d is None:
        return None
    ad = abs(d)
    if ad < 0.147:
        return 'negligible'
    if ad < 0.33:
        return 'small'
    if ad < 0.474:
        return 'medium'
    return 'large'


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def manual_mwu_p(a, b):
    """Normal-approximation Mann-Whitney U p-value with tie correction (fallback for no-scipy)."""
    combined = [(v, 0) for v in a] + [(v, 1) for v in b]
    combined.sort(key=lambda t: t[0])
    n = len(combined)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and combined[j + 1][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[k] = avg_rank
        i = j + 1
    n1, n2 = len(a), len(b)
    r1 = sum(r for (v, g), r in zip(combined, ranks) if g == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    tie_counts = Counter(v for v, _ in combined)
    tie_sum = sum(t ** 3 - t for t in tie_counts.values())
    denom = (n1 + n2) * (n1 + n2 - 1)
    sigma2 = (n1 * n2 / 12.0) * ((n1 + n2 + 1) - (tie_sum / denom if denom else 0))
    if sigma2 <= 0:
        return 1.0
    sigma = math.sqrt(sigma2)
    if u1 > mu:
        z = (u1 - mu - 0.5) / sigma
    elif u1 < mu:
        z = (u1 - mu + 0.5) / sigma
    else:
        z = 0.0
    return min(1.0, max(0.0, 2 * (1 - norm_cdf(abs(z)))))


def mwu_p(a, b, force_manual=False):
    a = [x for x in a if x is not None]
    b = [x for x in b if x is not None]
    if not a or not b:
        return None, 'n/a'
    if len(set(a) | set(b)) == 1:
        return 1.0, 'constant'
    if HAVE_SCIPY and not force_manual:
        try:
            _, p = _scipy_stats.mannwhitneyu(a, b, alternative='two-sided')
            return float(p), 'scipy'
        except Exception:
            pass
    return manual_mwu_p(a, b), 'normal-approx'


def two_prop_p(x1, n1, x2, n2):
    if not n1 or not n2:
        return None
    p1, p2 = x1 / n1, x2 / n2
    p = (x1 + x2) / (n1 + n2)
    if p <= 0 or p >= 1:
        return 1.0
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return 1.0
    z = (p1 - p2) / se
    return min(1.0, max(0.0, 2 * (1 - norm_cdf(abs(z)))))


def bh_fdr(pvals):
    """Benjamini-Hochberg step-up FDR. None entries pass through as None."""
    idx_p = [(i, p) for i, p in enumerate(pvals) if p is not None]
    out = [None] * len(pvals)
    m = len(idx_p)
    if m == 0:
        return out
    idx_p.sort(key=lambda t: t[1])
    running_min = 1.0
    for rank in range(m, 0, -1):
        i, p = idx_p[rank - 1]
        q = p * m / rank
        running_min = min(running_min, q)
        out[i] = round(min(1.0, running_min), 6)
    return out


# ----------------------------------------------------------------------------
# self-test: cross-check the hand-written fallback against scipy, and Cliff's
# delta against the brute-force O(n*m) definition, on synthetic data.
# ----------------------------------------------------------------------------

def self_test():
    import random
    random.seed(0)
    ok = True
    for trial in range(20):
        a = [random.gauss(0, 1) for _ in range(random.randint(5, 40))]
        b = [random.gauss(0.3, 1) for _ in range(random.randint(5, 40))]
        # tie in a few values to exercise tie correction
        if trial % 3 == 0:
            a[0] = b[0] = 0.0
        p_scipy, _ = mwu_p(a, b, force_manual=False)
        p_manual, _ = mwu_p(a, b, force_manual=True)
        if HAVE_SCIPY and abs(p_scipy - p_manual) > 0.02:
            print(f'[self-test] FAIL trial {trial}: scipy p={p_scipy:.4f} manual p={p_manual:.4f}', file=sys.stderr)
            ok = False
        d, n, m = cliffs_delta(a, b)
        brute = sum((1 if x > y else (-1 if x < y else 0)) for x in a for y in b) / (n * m)
        if abs(d - brute) > 1e-9:
            print(f'[self-test] FAIL trial {trial}: cliffs_delta={d} brute={brute}', file=sys.stderr)
            ok = False
    # BH-FDR sanity: monotone p-values should stay monotone in q, q >= p
    ps = [0.001, 0.01, 0.02, 0.04, 0.5, 0.9]
    qs = bh_fdr(ps)
    if any(q < p - 1e-9 for p, q in zip(ps, qs)) or any(qs[i] > qs[i + 1] + 1e-9 for i in range(len(qs) - 1)):
        print(f'[self-test] FAIL: bh_fdr not monotone / not >= p: {ps} -> {qs}', file=sys.stderr)
        ok = False
    print(f'[self-test] {"PASS" if ok else "FAIL"} (scipy {"available" if HAVE_SCIPY else "NOT available -- only fallback path exercised"})')
    return ok


# ----------------------------------------------------------------------------
# CSV writers
# ----------------------------------------------------------------------------

def write_csv(path, fieldnames, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--index', default=DEFAULT_INDEX, help='corpus_index.csv path')
    ap.add_argument('--out', default=DEFAULT_OUT, help='output directory')
    ap.add_argument('--min-n', type=int, default=10, help='below this n per side, flag a contrast row low_power')
    ap.add_argument('--subtype', default=SUBTYPE, help="diagram subtype to analyse (default 'architecture'; 'mechanism' for the mechanism-figure kind)")
    ap.add_argument('--self-test', action='store_true', help='run internal consistency checks and exit')
    ap.add_argument('--corpus-root', default=None, help='corpus root (<root>/extracted/corpus_index.csv): replaces the lab/ default of --index')
    args = ap.parse_args()
    if args.corpus_root and args.index == DEFAULT_INDEX:
        args.index = os.path.join(os.path.abspath(args.corpus_root), 'extracted', 'corpus_index.csv')

    if args.self_test:
        sys.exit(0 if self_test() else 1)

    os.makedirs(args.out, exist_ok=True)
    recs, n_total, n_bad_json = load(args.index, args.subtype)
    if not recs:
        print(f'No {args.subtype} rows found in {args.index}', file=sys.stderr)
        sys.exit(1)

    aesthetic_counts = Counter(r['aesthetic'] for r in recs)
    column_counts = Counter(r['column_eff'] for r in recs)
    blank_column_n = sum(1 for r in recs if not r['column_raw'])
    good_src_n = sum(1 for r in recs if in_group(r, 'good_src'))

    print(f'rows in index: {n_total} | {args.subtype} rows: {len(recs)} | bad style JSON: {n_bad_json}')
    print(f'aesthetic: {dict(aesthetic_counts)} | column_eff: {dict(column_counts)} '
          f'(blank column field on {blank_column_n} rows, inferred) | good_src: {good_src_n}')

    # ---- metrics_per_figure.csv (raw per-row export) ----
    meta_cols = ['paper_id', 'fig', 'venue', 'year', 'aesthetic', 'has_source',
                 'column_raw', 'column_eff', 'tool', 'tool_source', 'label_source']
    write_csv(os.path.join(args.out, 'metrics_per_figure.csv'),
              meta_cols + NUM_KEYS + CAT_KEYS, recs)

    # ---- numeric_distributions.csv + nested summary dict ----
    numeric_rows = []
    numeric_summary = {}  # metric -> group -> split -> stats
    for metric in NUM_KEYS:
        numeric_summary[metric] = {}
        for group in GROUPS:
            numeric_summary[metric][group] = {}
            for split in SPLITS:
                vals = [r[metric] for r in recs if in_group(r, group) and in_split(r, split)]
                st = pct_stats(vals)
                numeric_summary[metric][group][split] = st
                numeric_rows.append(dict(metric=metric, group=group, column_split=split, **st))
    write_csv(os.path.join(args.out, 'numeric_distributions.csv'),
              ['metric', 'group', 'column_split', 'n', 'mean', 'p5', 'p25', 'p50', 'p75', 'p95'],
              numeric_rows)

    # ---- categorical_distributions.csv + nested summary dict ----
    all_values = {m: sorted({r[m] for r in recs}, key=str) for m in CAT_KEYS}
    cat_rows = []
    categorical_summary = {}  # metric -> group -> split -> {value: {count, frac}}
    for metric in CAT_KEYS:
        categorical_summary[metric] = {}
        for group in GROUPS:
            categorical_summary[metric][group] = {}
            for split in SPLITS:
                vals = [r[metric] for r in recs if in_group(r, group) and in_split(r, split)]
                n = len(vals)
                c = Counter(vals)
                categorical_summary[metric][group][split] = {}
                for value in all_values[metric]:
                    cnt = c.get(value, 0)
                    frac = round(cnt / n, 4) if n else None
                    categorical_summary[metric][group][split][str(value)] = dict(count=cnt, frac=frac)
                    cat_rows.append(dict(metric=metric, group=group, column_split=split,
                                          value=value, count=cnt, n_group=n, frac=frac))
    write_csv(os.path.join(args.out, 'categorical_distributions.csv'),
              ['metric', 'group', 'column_split', 'value', 'count', 'n_group', 'frac'], cat_rows)

    # ---- contrast: good vs ok+bad (numeric) ----
    def numeric_contrast(b_group_name, b_pred, tag):
        rows_by_split = {sp: [] for sp in SPLITS}
        for split in SPLITS:
            pvals = []
            partials = []
            for metric in NUM_KEYS:
                a_vals = [r[metric] for r in recs if in_group(r, 'good') and in_split(r, split)]
                b_vals = [r[metric] for r in recs if b_pred(r) and in_split(r, split)]
                a_stats = pct_stats(a_vals)
                b_stats = pct_stats(b_vals)
                delta, n, m = cliffs_delta(a_vals, b_vals)
                p, method = mwu_p(a_vals, b_vals)
                pvals.append(p)
                partials.append(dict(
                    metric=metric, column_split=split,
                    good_n=a_stats['n'], good_mean=a_stats['mean'], good_p5=a_stats['p5'], good_p25=a_stats['p25'],
                    good_p50=a_stats['p50'], good_p75=a_stats['p75'], good_p95=a_stats['p95'],
                    **{f'{tag}_n': b_stats['n'], f'{tag}_mean': b_stats['mean'], f'{tag}_p50': b_stats['p50']},
                    cliffs_delta=round(delta, 4) if delta is not None else None,
                    magnitude=delta_magnitude(delta),
                    mwu_p=round(p, 6) if p is not None else None, p_method=method,
                    low_power=bool(n < args.min_n or m < args.min_n),
                ))
            fdrs = bh_fdr(pvals)
            for row, q in zip(partials, fdrs):
                row['mwu_p_fdr'] = q
                row['signal'] = bool(q is not None and q < 0.05 and row['magnitude'] not in (None, 'negligible')
                                      and not row['low_power'])
            rows_by_split[split] = partials
        return rows_by_split

    okbad_pred = lambda r: r['aesthetic'] in ('ok', 'bad')
    bad_pred = lambda r: r['aesthetic'] == 'bad'
    contrast_okbad = numeric_contrast('ok+bad', okbad_pred, 'okbad')
    contrast_bad = numeric_contrast('bad', bad_pred, 'bad')

    fieldnames_okbad = ['metric', 'column_split', 'good_n', 'good_mean', 'good_p5', 'good_p25', 'good_p50',
                         'good_p75', 'good_p95', 'okbad_n', 'okbad_mean', 'okbad_p50', 'cliffs_delta',
                         'magnitude', 'mwu_p', 'mwu_p_fdr', 'p_method', 'low_power', 'signal']
    write_csv(os.path.join(args.out, 'contrast_numeric.csv'), fieldnames_okbad,
              [row for sp in SPLITS for row in contrast_okbad[sp]])

    fieldnames_bad = ['metric', 'column_split', 'good_n', 'good_mean', 'good_p5', 'good_p25', 'good_p50',
                       'good_p75', 'good_p95', 'bad_n', 'bad_mean', 'bad_p50', 'cliffs_delta',
                       'magnitude', 'mwu_p', 'mwu_p_fdr', 'p_method', 'low_power', 'signal']
    write_csv(os.path.join(args.out, 'contrast_numeric_bad_only.csv'), fieldnames_bad,
              [row for sp in SPLITS for row in contrast_bad[sp]])

    # ---- contrast: good vs ok+bad (categorical) ----
    cat_contrast_rows = []
    for split in SPLITS:
        pvals = []
        partials = []
        for metric in CAT_KEYS:
            a_all = [r[metric] for r in recs if in_group(r, 'good') and in_split(r, split)]
            b_all = [r[metric] for r in recs if okbad_pred(r) and in_split(r, split)]
            n1, n2 = len(a_all), len(b_all)
            ca, cb = Counter(a_all), Counter(b_all)
            for value in all_values[metric]:
                x1, x2 = ca.get(value, 0), cb.get(value, 0)
                f1 = round(x1 / n1, 4) if n1 else None
                f2 = round(x2 / n2, 4) if n2 else None
                diff = round(f1 - f2, 4) if (f1 is not None and f2 is not None) else None
                p = two_prop_p(x1, n1, x2, n2)
                pvals.append(p)
                partials.append(dict(metric=metric, value=value, column_split=split,
                                      good_n=n1, good_count=x1, good_frac=f1,
                                      okbad_n=n2, okbad_count=x2, okbad_frac=f2, diff=diff,
                                      z_p=round(p, 6) if p is not None else None,
                                      low_power=bool(n1 < args.min_n or n2 < args.min_n)))
        fdrs = bh_fdr(pvals)
        for row, q in zip(partials, fdrs):
            row['z_p_fdr'] = q
            row['signal'] = bool(q is not None and q < 0.05 and row['diff'] is not None
                                  and abs(row['diff']) >= 0.1 and not row['low_power'])
        cat_contrast_rows.extend(partials)
    write_csv(os.path.join(args.out, 'contrast_categorical.csv'),
              ['metric', 'value', 'column_split', 'good_n', 'good_count', 'good_frac', 'okbad_n',
               'okbad_count', 'okbad_frac', 'diff', 'z_p', 'z_p_fdr', 'low_power', 'signal'],
              cat_contrast_rows)

    # ---- cross-tabs ----
    def cross_tab(field):
        keys = sorted({r[field] for r in recs})
        rows = []
        for k in keys:
            sub = [r for r in recs if r[field] == k]
            c = Counter(r['aesthetic'] for r in sub)
            total = len(sub)
            good_n = c.get('good', 0)
            okbad_n = c.get('ok', 0) + c.get('bad', 0)
            rows.append({
                field: k, 'good': c.get('good', 0), 'ok': c.get('ok', 0), 'bad': c.get('bad', 0),
                'discard': c.get('discard', 0), 'total': total,
                'good_frac': round(good_n / total, 3) if total else None,
                'okbad_frac': round(okbad_n / total, 3) if total else None,
            })
        rows.sort(key=lambda r: -r['total'])
        return rows

    tool_rows = cross_tab('tool')
    venue_rows = cross_tab('venue')
    write_csv(os.path.join(args.out, 'tool_by_aesthetic.csv'),
              ['tool', 'good', 'ok', 'bad', 'discard', 'total', 'good_frac', 'okbad_frac'], tool_rows)
    write_csv(os.path.join(args.out, 'venue_by_aesthetic.csv'),
              ['venue', 'good', 'ok', 'bad', 'discard', 'total', 'good_frac', 'okbad_frac'], venue_rows)

    # ---- summary.json: single source of truth for the doc-writing step ----
    summary = dict(
        meta=dict(
            index_path=os.path.abspath(args.index), subtype=args.subtype, n_index_rows=n_total, n_architecture_rows=len(recs),
            n_bad_style_json=n_bad_json, aesthetic_counts=dict(aesthetic_counts),
            column_eff_counts=dict(column_counts), blank_column_field_rows=blank_column_n,
            good_with_source_n=good_src_n, column_widths_pt=COL_WIDTH, min_n_for_power=args.min_n,
            groups=GROUPS, splits=SPLITS, numeric_metrics=NUM_KEYS, categorical_metrics=CAT_KEYS,
            have_scipy=HAVE_SCIPY,
        ),
        numeric_distributions=numeric_summary,
        categorical_distributions=categorical_summary,
        contrast_numeric_okbad={sp: contrast_okbad[sp] for sp in SPLITS},
        contrast_numeric_bad_only={sp: contrast_bad[sp] for sp in SPLITS},
        contrast_categorical=cat_contrast_rows,
        tool_by_aesthetic=tool_rows,
        venue_by_aesthetic=venue_rows,
    )
    with open(os.path.join(args.out, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=1)

    # ---- console highlights ----
    print(f'\nwrote outputs to {args.out}')
    sig = [row for row in contrast_okbad['all'] if row['signal']]
    sig.sort(key=lambda r: -abs(r['cliffs_delta']))
    print(f'\n{len(sig)}/{len(NUM_KEYS)} numeric metrics show a significant good-vs-(ok+bad) signal '
          f'(all-column split, FDR<0.05, |delta|>=0.147, n>={args.min_n} both sides):')
    for row in sig:
        print(f"  {row['metric']:32s} delta={row['cliffs_delta']:+.3f} ({row['magnitude']:9s}) "
              f"good_p50={row['good_p50']!s:>8} okbad_p50={row['okbad_p50']!s:>8} p_fdr={row['mwu_p_fdr']}")
    non_sig = [row['metric'] for row in contrast_okbad['all'] if not row['signal'] and not row['low_power']]
    print(f'\n{len(non_sig)} numeric metrics show NO significant difference (all-column split): {non_sig}')


if __name__ == '__main__':
    main()
