#!/usr/bin/env python3
"""Build the exemplars of a named style (references/styles/<style>.md) from a paper the user pointed at.

A named style comes from one paper outside the rated corpus, so its figures are kept apart from the corpus
exemplars that build_exemplars.py regenerates (its --clean would otherwise remove them):

    assets/exemplars/styles/<style>/index.json            the style's figures: id, kind, templates / groups
                                                           (star, why_chosen, what_to_learn), print / preview paths
    assets/exemplars/styles/<style>/figures/<id>/         same files as a corpus exemplar: source.svg, print.png,
                                                           preview.png, semantics.json, manifest.json (style, origin)

Input: scripts/distill/style_exemplars/<style>.json (hand-written: paper metadata, one entry per figure with the
author PDF, printed width, template / group slots and the semantic record) and the author figure PDFs under the
repo-relative `paper.source_dir`. source.svg is the author PDF converted by PyMuPDF with text kept as <text>;
print.png renders it at its printed width at 110 dpi (the corpus print.png resolution), preview.png at 300 dpi.
find_exemplars.py reads these figures next to the corpus ones (`--style <style>` gives them a bonus).

    python3 build_style_exemplars.py charon [--dry-run]
"""
import argparse, json, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
REPO = SKILL.parent
OUT_ROOT = SKILL / 'assets' / 'exemplars' / 'styles'
PRINT_DPI, PREVIEW_DPI = 110, 300


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('style'); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    try:
        import fitz
    except ImportError:
        sys.exit('needs PyMuPDF (pip install pymupdf)')
    sel = json.loads((HERE / 'style_exemplars' / f'{a.style}.json').read_text(encoding='utf-8'))
    paper = sel['paper']; src = REPO / paper['source_dir']
    out = OUT_ROOT / a.style
    entries = []
    for f in sel['figures']:
        pdf = src / f['file']
        if not pdf.exists(): sys.exit(f'missing {pdf}')
        page = fitz.open(pdf)[0]
        w, h = page.rect.width, page.rect.height
        scale = f['print_width_pt'] / w
        sem = {'paper_id': paper['paper_id'], 'fig': f['fig']}
        sem.update(f['semantics']); sem['venue'] = paper['venue']
        kind = f['kind']
        slots_key = 'templates' if kind == 'architecture' else 'groups'
        slots = [dict(s, note_source='hand') for s in f['slots']]
        man = {
            'id': f['id'], 'kind': kind, 'paper_id': paper['paper_id'], 'fig': f['fig'],
            'venue': paper['venue'], 'year': paper['year'], 'caption': f['caption'],
            'title': paper['title'], 'authors': paper['authors'], 'arxiv': paper['arxiv'],
            'style': a.style, 'origin': 'style-reference',
            'column': sem['layout'].get('column'), 'aspect': round(w / h, 2),
            'print_width_pt': f['print_width_pt'], 'print_height_pt': round(h * scale, 1),
            'tool': 'powerpoint', 'source_kind': 'author', 'license': paper['license'],
            'files': {'source.svg': 'author figure PDF converted to SVG (PyMuPDF, text kept as <text>), author units',
                      'preview.png': f'the author figure at its printed width, {PREVIEW_DPI} dpi',
                      'print.png': f'the author figure at its printed width, {PRINT_DPI} dpi',
                      'semantics.json': 'hand-written semantic record', 'manifest.json': 'this file'},
            'original_paths': {'source.svg': f"{paper['source_dir']}/{f['file']}"},
            slots_key: slots,
        }
        d = out / 'figures' / f['id']
        entries.append({'id': f['id'], 'kind': kind, slots_key: slots, 'section': f['section'],
                        'print': f'figures/{f["id"]}/print.png', 'preview': f'figures/{f["id"]}/preview.png',
                        'print_width_pt': f['print_width_pt']})
        print(f"{f['id']}: {kind}, {w:.0f}x{h:.0f} author pt -> {f['print_width_pt']} pt printed (x{scale:.2f})")
        if a.dry_run: continue
        if d.exists(): shutil.rmtree(d)
        d.mkdir(parents=True)
        (d / 'source.svg').write_text(page.get_svg_image(text_as_path=False), encoding='utf-8')
        for name, dpi in (('print.png', PRINT_DPI), ('preview.png', PREVIEW_DPI)):
            page.get_pixmap(matrix=fitz.Matrix(scale * dpi / 72, scale * dpi / 72), alpha=False).save(d / name)
        (d / 'semantics.json').write_text(json.dumps(sem, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        (d / 'manifest.json').write_text(json.dumps(man, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    index = {'style': a.style, 'generated_by': 'figgenie-paper-diagram/scripts/distill/build_style_exemplars.py',
             'selection': f'scripts/distill/style_exemplars/{a.style}.json', 'style_card': f'references/styles/{a.style}.md',
             'paper': {k: paper[k] for k in ('paper_id', 'title', 'authors', 'venue', 'arxiv', 'license')},
             'how_to_read': 'open figures/<id>/print.png (print size) or preview.png (detail) and manifest.json; '
                            'star = must-see. These show one paper\'s house style; borrow its look, not its layouts.',
             'n': len(entries), 'figures': entries}
    if not a.dry_run:
        (out / 'index.json').write_text(json.dumps(index, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f'wrote {len(entries)} figures to {out.relative_to(SKILL)}')


if __name__ == '__main__':
    main()
