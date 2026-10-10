#!/usr/bin/env python3
"""Write one 600x300 swatch card per palette in references/palettes.json.

Each card shows the 12 role swatches with their hexes plus a tiny sample diagram (a
container, three module boxes, an accent box, a plain arrow and an accent arrow, a lane, a
legend chip and a muted annotation) drawn with that palette, so a family can be judged at
a glance without opening an exemplar figure.

    python3 make_swatches.py [--palettes references/palettes.json] [--out assets/palettes]

Label colours are chosen per swatch by WCAG contrast, so a dark accent gets white text.
The output is plain SVG with no external references; validate with lxml.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette_cluster import contrast  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))

ROLE_ORDER = ["canvas", "container", "lane", "module", "module-alt", "accent",
              "stroke", "text", "text-muted", "arrow", "arrow-accent", "legend"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def on(fill, text, alt="#ffffff"):
    """Pick the label colour that reads on `fill`."""
    return text if contrast(text, fill) >= contrast(alt, fill) else alt


def card(p):
    r = dict(p["roles"])
    alts = r['module-alt'] or [r['module']]
    text, stroke, muted = r['text'], r['stroke'], r['text-muted']
    # transparent ground (palette_grounds.py): container / lane are null = outline only, no fill
    cont_fill = r["container"] or "none"
    cont_dash = '' if r["container"] else ' stroke-dasharray="4 2.5"'
    lane_fill = r["lane"] or "none"
    lane_dash = '' if r["lane"] else ' stroke-dasharray="4 2.5"'
    cont_on = r["container"] or r["canvas"]
    lane_on = r["lane"] or r["canvas"]
    s = []
    a = s.append
    a('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" '
      'viewBox="0 0 600 300" font-family="Helvetica, Arial, sans-serif">')
    a(f'<defs>'
      f'<marker id="ah" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto">'
      f'<path d="M0,0 L7,3 L0,6 z" fill="{r["arrow"]}"/></marker>'
      f'<marker id="ahx" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto">'
      f'<path d="M0,0 L7,3 L0,6 z" fill="{r["arrow-accent"]}"/></marker>'
      f'</defs>')
    a(f'<rect x="0" y="0" width="600" height="300" fill="{r["canvas"]}"/>')
    # header
    a(f'<text x="16" y="24" font-size="15" font-weight="bold" fill="{text}">'
      f'{esc(p["name"])}</text>')
    tag = (f'n={p["stats"]["n_figures"]} ({p["stats"]["share"]*100:.1f}%)' if p.get("stats")
           else f'named style: {p.get("style", p["id"])}')          # a named style is one paper, not a corpus share
    a(f'<text x="584" y="24" font-size="11" text-anchor="end" fill="{muted}">'
      f'{esc(p["id"])} &#183; {esc(tag)}</text>')
    a(f'<line x1="16" y1="33" x2="584" y2="33" stroke="{muted}" stroke-width="0.6"/>')

    # ---- left: sample diagram -------------------------------------------------------
    a(f'<rect x="16" y="46" width="272" height="152" rx="4" fill="{cont_fill}" '
      f'stroke="{stroke}" stroke-width="1"{cont_dash}/>')
    a(f'<text x="26" y="63" font-size="10" font-weight="bold" '
      f'fill="{on(cont_on, text)}">Container{"" if r["container"] else " (outline only)"}</text>')
    boxes = [("module", r["module"]), ("alt 1", alts[0]),
             ("alt 2", alts[1] if len(alts) > 1 else alts[0])]
    for i, (lab, fill) in enumerate(boxes):
        x = 26 + i * 87
        a(f'<rect x="{x}" y="74" width="74" height="34" rx="3" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="1"/>')
        a(f'<text x="{x+37}" y="95" font-size="10" text-anchor="middle" '
          f'fill="{on(fill, text)}">{lab}</text>')
    a(f'<line x1="100" y1="91" x2="111" y2="91" stroke="{r["arrow"]}" '
      f'stroke-width="1.4" marker-end="url(#ah)"/>')
    a(f'<line x1="187" y1="91" x2="198" y2="91" stroke="{r["arrow"]}" '
      f'stroke-width="1.4" marker-end="url(#ah)"/>')
    a(f'<rect x="26" y="128" width="74" height="34" rx="3" fill="{r["accent"]}" '
      f'stroke="{stroke}" stroke-width="1"/>')
    a(f'<text x="63" y="149" font-size="10" font-weight="bold" text-anchor="middle" '
      f'fill="{on(r["accent"], text)}">accent</text>')
    a(f'<path d="M100,145 H150 V112" fill="none" stroke="{r["arrow-accent"]}" '
      f'stroke-width="1.8" marker-end="url(#ahx)"/>')
    a(f'<text x="158" y="143" font-size="9" fill="{on(cont_on, muted)}">'
      f'accent arrow</text>')
    a(f'<text x="26" y="182" font-size="9" fill="{on(cont_on, muted)}">'
      f'text-muted annotation</text>')
    a(f'<rect x="16" y="208" width="272" height="26" rx="2" fill="{lane_fill}" '
      f'stroke="{stroke}" stroke-width="0.7"{lane_dash}/>')
    a(f'<text x="26" y="225" font-size="10" fill="{on(lane_on, text)}">lane / band{"" if r["lane"] else " (none)"}</text>')
    a(f'<rect x="16" y="244" width="96" height="26" rx="2" fill="{r["legend"]}" '
      f'stroke="{stroke}" stroke-width="0.7"/>')
    a(f'<text x="26" y="261" font-size="9" fill="{on(r["legend"], text)}">legend</text>')
    a(f'<text x="124" y="261" font-size="9" fill="{muted}">canvas {r["canvas"]}</text>')
    desc = p["description"]
    if len(desc) > 96:
        desc = desc[:96].rsplit(' ', 1)[0].rstrip(',;') + '...'
    a(f'<text x="16" y="288" font-size="8.5" fill="{muted}">{esc(desc)}</text>')

    # ---- right: role swatches -------------------------------------------------------
    for i, role in enumerate(ROLE_ORDER):
        col, row = i % 2, i // 2
        x, y = 308 + col * 142, 46 + row * 41
        val = r[role]
        extra = ''
        if role == "module-alt":
            val = alts[0]
            if len(alts) > 1:
                extra = f' +{len(alts)-1}'
        if val is None:   # transparent ground: swatch is an empty dashed square
            a(f'<rect x="{x}" y="{y}" width="24" height="24" rx="2" fill="none" '
              f'stroke="{stroke}" stroke-width="0.7" stroke-dasharray="3 2"/>')
            val = "none"
        else:
            a(f'<rect x="{x}" y="{y}" width="24" height="24" rx="2" fill="{val}" '
              f'stroke="{stroke}" stroke-width="0.7"/>')
        a(f'<text x="{x+31}" y="{y+11}" font-size="9.5" fill="{text}">{role}{extra}</text>')
        a(f'<text x="{x+31}" y="{y+22}" font-size="9" font-family="Menlo, monospace" '
          f'fill="{muted}">{val}</text>')
    a('</svg>')
    return '\n'.join(s) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--palettes", default=os.path.join(SKILL, "references", "palettes.json"))
    ap.add_argument("--out", default=os.path.join(SKILL, "assets", "palettes"))
    args = ap.parse_args()
    doc = json.load(open(args.palettes))
    os.makedirs(args.out, exist_ok=True)
    for p in doc["palettes"]:
        path = os.path.join(args.out, f"{p['id']}.svg")
        with open(path, "w") as f:
            f.write(card(p))
        print("wrote", path)


if __name__ == "__main__":
    main()
