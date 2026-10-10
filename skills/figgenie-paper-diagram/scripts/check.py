#!/usr/bin/env python3
"""One-shot self-check for a drawn figure: validate spec → lint SVG → render PNG (+ annotated PNG) → preview page.

  python3 scripts/check.py fig.svg [--spec fig.json] [--scale 3] [--out-dir DIR] [--strict]

Writes next to the SVG (or in --out-dir):
  fig.png            what the figure looks like (LOOK at it with your image-viewing tool)
  fig.lint.json      machine-readable findings
  fig.lint.svg/.png  the figure with red (error) / orange (warning) boxes on the offending elements
  fig.preview.html   browser debug page (zoom, grid, hover for coordinates, click a finding to highlight)
Exit code 1 if the spec is invalid or the lint has errors (or warnings with --strict).
"""
import argparse, json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _svgkit as K


def run(cmd):
    r = subprocess.run([sys.executable] + cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('svg'); ap.add_argument('--spec'); ap.add_argument('--scale', type=float, default=3.0)
    ap.add_argument('--out-dir'); ap.add_argument('--strict', action='store_true'); ap.add_argument('--no-preview', action='store_true')
    a = ap.parse_args()
    svg = Path(a.svg); od = Path(a.out_dir) if a.out_dir else svg.parent; od.mkdir(parents=True, exist_ok=True)
    stem = od / svg.stem; ok = True
    if a.spec:
        rc, out = run([str(HERE / 'spec_validate.py'), a.spec]); print(out.splitlines()[-1] if out else ''); ok &= rc == 0
    lint_json = Path(f'{stem}.lint.json'); lint_svg = Path(f'{stem}.lint.svg')
    cmd = [str(HERE / 'lint.py'), str(svg), '--report', str(lint_json), '--annotate', str(lint_svg)] + (['--spec', a.spec] if a.spec else []) + (['--strict'] if a.strict else [])
    rc, out = run(cmd); print(out); ok &= rc == 0
    text = svg.read_text(encoding='utf-8'); here = svg.resolve().parent   # bitmap links are relative to the SVG, also in fig.lint.svg
    K.render_png(text, f'{stem}.png', scale=a.scale, base_dir=here)
    if lint_svg.exists():
        K.render_png(lint_svg.read_text(encoding='utf-8'), f'{stem}.lint.png', scale=a.scale, base_dir=here)
    print(f'rendered {stem}.png' + (f' and {stem}.lint.png' if lint_svg.exists() else ''))
    if not a.no_preview:
        rc2, out2 = run([str(HERE / 'preview.py'), str(svg), '--lint', str(lint_json)] + (['--spec', a.spec] if a.spec else []) + ['-o', f'{stem}.preview.html']); print(out2)
    rep = json.loads(lint_json.read_text()) if lint_json.exists() else {}
    styled = [f['message'] for f in rep.get('findings', []) if f.get('code') == 'style.checked']   # named style (meta.style)
    print(f'RESULT: {"PASS" if ok else "FAIL"} — {rep.get("errors", "?")} error(s), {rep.get("warnings", "?")} warning(s)'
          + (f'; {styled[0]}' if styled else '') + f'. Now LOOK at {stem}.png (and {stem}.lint.png) before deciding it is done.')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
