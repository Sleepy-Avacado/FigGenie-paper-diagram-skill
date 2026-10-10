#!/usr/bin/env python3
"""Place a label from the font's own metrics instead of by eye: a label centred in a box (level, or turned ±90° in a
narrow bar), or a line of text pieces with inline step badges (a ① disc inside a sentence or a legend entry).

  python3 scripts/place_text.py --font helvetica --size 6.5 center --box 80,10,60,12 "Placement table"
  python3 scripts/place_text.py --font helvetica --size 6.5 center --box 268,70,22,234 --rotate -90 "Dispatch all-to-all"
  python3 scripts/place_text.py --font helvetica --size 6.5 center --box 40,20,70,22 "Prefix\\nIndexer"     # two lines
  python3 scripts/place_text.py --font helvetica --size 6.5 line --at 12,433 @badge:1 "Attention: E0 weights, 2.4 ms"
  python3 scripts/place_text.py --font calibri --size 6.5 --bold line --at 300,40 --anchor middle "(" @badge:2 "Count)"

center  The label's glyph ink -- from its tallest glyph down to its lowest descender, measured on the font file with the
        same function the linter uses (_svgkit.ink_band) -- is centred on the box (a block of lines 1.2 em apart is
        centred as one), so lint's centre.y / centre.x and text.padding see exactly what this script computed. A label
        without descenders ('Attention') thus centres its capitals; 'Dispatch' sits a little higher for its p. --rotate
        -90 / 90 turns the label about the box centre and centres it across the bar the same way (glyph tops point left
        for -90, the usual upward-reading label). The script also says whether the box leaves the 1.5 pt that
        text.padding asks for, along and across the text.
line    Lays out pieces left to right from --at x,baseline: plain strings are text runs (keep their own spaces), @badge:N
        a filled disc with the digit N (diameter --badge em, default 1.0) wrapped in <g data-symbol="badge"> -- the
        linter then treats its digit like a step badge's (1 pt below the type floor is fine) -- @gap:P an empty P pt. --anchor middle / end
        centres or right-aligns the whole line on x. Each badge sits on the cap-height middle of the line.

Prints ready-to-paste SVG (font-size on every element; add your fill, font-weight and ids) and the numbers it used.
Widths come from the same font files as measure_text.py (PIL / FreeType), so they match Chromium with the faces
embedded.

From a script that generates the SVG (a make_fig.py that writes every box), call the same code instead of the CLI:

    import sys; sys.path.insert(0, '<skill>/scripts')
    from place_text import place, svg_text
    p = place('Dispatch all-to-all', (268, 70, 22, 234), size=6.5, font='helvetica', rotate=-90)
    p['x'], p['y'], p['transform'], p['fits']        # first baseline, rotate() or '', and whether 1.5 pt padding holds
    svg_text(p)                                      # the <text> element itself
    import _svgkit as K; K.ink_band('Gate', 6.5, 'helvetica')   # (above, below) pt of the ink around the baseline
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _svgkit as K
from measure_text import _face, width_of


def metrics(key, size, bold=False):
    """(cap_height_pt, x_height_pt) of the face, measured on 'H' and 'x' at 10x for precision."""
    from PIL import ImageFont
    p = _face(key, bold)
    if p is None:
        return 0.72 * size, 0.52 * size
    f = ImageFont.truetype(str(p), size=int(round(size * 10)), index=0)
    cap = -f.getbbox('H', anchor='ls')[1] / 10.0
    xh = -f.getbbox('x', anchor='ls')[1] / 10.0
    return cap, xh


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _key(font):
    fonts = K.load_fonts(); key = font or fonts['default']
    return key if key in fonts['families'] else K.resolve_font(key)


def place(text, box, size=6.5, font=None, bold=False, rotate=0, leading=1.2, cjk=None, pad=1.5):
    """Centre `text` ('\\n' separates lines) in `box` = (x, y, w, h) pt, level or turned by rotate = ±90. Returns a dict:
    x, y (first baseline; text-anchor middle), lines, pitch (pt between baselines), transform ('' or a rotate()),
    above / below (ink around the first / last baseline), widths, fits (bool) and short (what is missing for `pad` pt)."""
    key = _key(font)
    if cjk is None: cjk = K.cjk_default_key()
    x, y, w, h = (float(v) for v in box)
    cx, cy = x + w / 2, y + h / 2
    lines = str(text).replace('\\n', '\n').split('\n')
    pitch = leading * size
    up = K.ink_band(lines[0], size, key, bold)[0]; down = K.ink_band(lines[-1], size, key, bold)[1]
    ink = up + (len(lines) - 1) * pitch + down                    # first line's ink top to last line's ink bottom
    b1 = cy - ink / 2 + up                                        # first baseline: the ink block centred on cy
    widths = [width_of(l, key, size, bold, cjk_key=cjk)[0] for l in lines]
    along, across = (h, w) if rotate else (w, h)
    need_along, need_across = max(widths) + 2 * pad, ink + 2 * pad
    short = []
    if along < need_along: short.append(f'{"length" if rotate else "width"} {along:g} < {need_along:.1f} pt')
    if across < need_across: short.append(f'{"thickness" if rotate else "height"} {across:g} < {need_across:.1f} pt')
    return dict(x=cx, y=b1, cx=cx, cy=cy, lines=lines, pitch=pitch, size=size, above=up, below=down, widths=widths,
                transform=f'rotate({rotate:g} {cx:.2f} {cy:.2f})' if rotate else '', rotate=rotate, fits=not short, short=short)


def svg_text(p, attrs=''):
    """The <text> element for a place() result; `attrs` is added verbatim (fill, font-weight, class ...)."""
    rot = f' transform="{p["transform"]}"' if p['transform'] else ''
    extra = f' {attrs.strip()}' if attrs.strip() else ''
    if len(p['lines']) == 1:
        return f'<text x="{p["x"]:.2f}" y="{p["y"]:.2f}" font-size="{p["size"]:g}" text-anchor="middle"{rot}{extra}>{esc(p["lines"][0])}</text>'
    spans = ''.join(f'<tspan x="{p["x"]:.2f}" y="{p["y"] + i * p["pitch"]:.2f}">{esc(l)}</tspan>' for i, l in enumerate(p['lines']))
    return f'<text font-size="{p["size"]:g}" text-anchor="middle"{rot}{extra}>{spans}</text>'


def center(a, key, cjk):
    p = place(a.text, a.box.split(','), a.size, key, a.bold, a.rotate, a.leading, cjk)
    print(svg_text(p))
    print(f'# centre ({p["cx"]:.2f}, {p["cy"]:.2f}); ink {p["above"]:.2f} above / {p["below"]:.2f} below the baseline; '
          f'first baseline {p["y"]:.2f}' + (f' in the turned frame (rotate {a.rotate:g} about the centre)' if a.rotate else '')
          + f'; widest line {max(p["widths"]):.2f} pt', file=sys.stderr)
    if p['short']:
        print(f'# box too small for 1.5 pt padding (lint text.padding): {"; ".join(p["short"])}', file=sys.stderr)


def line(a, key, cjk):
    x0, base = (float(v) for v in a.at.split(','))
    cap, _ = metrics(key, a.size, a.bold)
    d = a.badge * a.size
    pieces = []
    for t in a.pieces:
        if t.startswith('@badge'):
            pieces.append(('badge', t.split(':', 1)[1] if ':' in t else '', d))
        elif t.startswith('@gap:'):
            pieces.append(('gap', '', float(t.split(':', 1)[1])))
        else:
            pieces.append(('text', t, width_of(t, key, a.size, a.bold, cjk_key=cjk)[0]))
    gaps = [a.gap if 'badge' in (p[0], q[0]) else 0.0 for p, q in zip(pieces, pieces[1:])]
    total = sum(p[2] for p in pieces) + sum(gaps)
    x = x0 - (total / 2 if a.anchor == 'middle' else total if a.anchor == 'end' else 0.0)
    cy = base - cap / 2
    for i, (kind, txt, wd) in enumerate(pieces):
        if kind == 'text':
            print(f'<text x="{x:.2f}" y="{base:.2f}" font-size="{a.size:g}" xml:space="preserve">{esc(txt)}</text>')
        elif kind == 'badge':
            ds = 0.78 * a.size                                       # digit size: badge digits are exempt from the 6 pt floor down to 5 pt
            dcap = metrics(key, ds, True)[0]
            print(f'<g data-symbol="badge"><circle cx="{x + wd / 2:.2f}" cy="{cy:.2f}" r="{wd / 2:.2f}"/>'
                  + (f'<text x="{x + wd / 2:.2f}" y="{cy + dcap / 2:.2f}" font-size="{ds:.2f}" font-weight="bold" '
                     f'text-anchor="middle" fill="#ffffff">{esc(txt)}</text>' if txt else '') + '</g>')
        x += wd + (gaps[i] if i < len(gaps) else 0.0)
    print(f'# line {total:.2f} pt wide from x {x - total:.2f}; baseline {base:.2f}; badge centre y {cy:.2f} (cap middle), '
          f'diameter {d:.2f}', file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--font', default=None); ap.add_argument('--size', type=float, default=6.5)
    ap.add_argument('--bold', action='store_true'); ap.add_argument('--cjk', default=None)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('center', help='a label centred in a box, level or turned')
    c.add_argument('--box', required=True, help='x,y,w,h in pt'); c.add_argument('--rotate', type=float, default=0, choices=[0, 90, -90])
    c.add_argument('--leading', type=float, default=1.2, help='line pitch in em (default 1.2)'); c.add_argument('text')
    l = sub.add_parser('line', help='text pieces and inline badges on one baseline')
    l.add_argument('--at', required=True, help='x,baseline in pt'); l.add_argument('--anchor', choices=['start', 'middle', 'end'], default='start')
    l.add_argument('--gap', type=float, default=1.2, help='space on each side of a badge, pt'); l.add_argument('--badge', type=float, default=1.0, help='badge diameter, em')
    l.add_argument('pieces', nargs='+')
    a = ap.parse_args()
    fonts = K.load_fonts(); key = a.font or fonts['default']
    if key not in fonts['families']: key = K.resolve_font(key)
    cjk = a.cjk or K.cjk_default_key()
    if cjk and cjk not in fonts['families']: cjk = K.resolve_font(cjk)
    (center if a.cmd == 'center' else line)(a, key, cjk)


if __name__ == '__main__':
    main()
