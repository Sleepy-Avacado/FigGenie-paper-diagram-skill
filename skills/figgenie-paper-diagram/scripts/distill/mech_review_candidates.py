#!/usr/bin/env python3
"""Build the single-file HTML page to review the mechanism-figure exemplar candidates, one tab per v3 group.

    python3 mech_review_candidates.py --semantics lab/extracted/corpus_semantics.jsonl \
        --index lab/extracted/corpus_index.csv --out exemplar-review/mechanism/review.html [--ids candidate_ids.txt]

The mechanism counterpart of review_candidates.py: every record with kind == "mechanism" (or only the ids listed
with --ids) becomes a tile under the tab of its primary group, showing the print-size PNG (author preview when the
figure only exists as a source file), the record's subject, base, arrangement, panel count, worked-example flag,
confidence, tool / column and its weaknesses. Two toggles per tile:
  ★ star  -- must-see exemplar (goes into the layouts.md exemplar tables and assets/exemplars)
  ✗ drop  -- exclude from the group's exemplars
State lives in localStorage; the text box always holds the decisions as JSON ({"drop": {group: [ids]}, "star":
{group: [ids]}}) to copy back. Image paths are absolute file:// paths into lab/extracted/, so the page only works
on this machine. A second key, "move", is offered per tile (a select of the five groups) for figures the reviewer
thinks belong to another group; it lands in the same JSON as {"move": {id: group}}.
With --doc <layouts.md>, every id cited in that file's "### Exemplars" tables gets a "layouts.md" badge (plus
"seen" when the doc marks it with a star, i.e. the writing agent opened the PNG), and each tab gets a button
that stars all doc-cited tiles of the group in one go, so the reviewer can start from the documented choice.
"""
import argparse, csv, html, json, os
from pathlib import Path

GROUPS = ["comparison", "evolution", "logic", "walkthrough", "anatomy"]
CSS = """
body{font:13px/1.35 -apple-system,Helvetica,Arial,sans-serif;margin:0;background:#fafafa;color:#222}
header{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;padding:8px 12px;z-index:5}
.tabs button{margin:2px;padding:4px 8px;border:1px solid #bbb;background:#f4f4f4;border-radius:4px;cursor:pointer}
.tabs button.on{background:#1f5fbf;color:#fff;border-color:#1f5fbf}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:10px;padding:10px}
.tile{background:#fff;border:1px solid #ddd;border-radius:6px;padding:6px;position:relative}
.tile.drop{opacity:.35;background:#fee}
.tile.star{border-color:#e6a700;box-shadow:0 0 0 2px #ffe08a inset}
.tile img{width:100%;max-height:300px;object-fit:contain;background:#fff;border:1px solid #eee}
.meta{font-size:12px;color:#444;margin-top:4px}
.meta b{color:#000}
.weak{color:#8a4a00}
.ctl{position:absolute;top:8px;right:8px;display:flex;gap:4px;align-items:center}
.ctl button{border:1px solid #999;background:#fff;border-radius:4px;padding:2px 7px;cursor:pointer;font-size:14px}
.ctl button.on{background:#c00;color:#fff;border-color:#c00}
.ctl button.staron{background:#e6a700;color:#fff;border-color:#e6a700}
.ctl select{font-size:11px}
textarea{width:98%;height:140px;font:12px monospace;margin:10px}
.summ{font-size:12px;color:#555}
.badge{display:inline-block;font-size:10px;padding:0 5px;border-radius:8px;background:#e8f0fe;color:#1f5fbf;border:1px solid #9fbbea;margin-right:4px}
.badge.seen{background:#fff4d6;color:#8a5a00;border-color:#e6c27a}
kbd{border:1px solid #bbb;border-radius:3px;padding:0 4px;font-size:11px;background:#f6f6f6}
"""
JS = """
const KEY='mech-exemplar-review-v1';
let state=JSON.parse(localStorage.getItem(KEY)||'{"drop":{},"star":{},"move":{}}'); if(!state.move) state.move={};
function save(){localStorage.setItem(KEY,JSON.stringify(state));document.getElementById('out').value=JSON.stringify(state,null,1);}
function has(k,t,id){return (state[k][t]||[]).includes(id);}
function toggle(k,t,id){const a=state[k][t]||[];const i=a.indexOf(id);if(i>=0)a.splice(i,1);else a.push(id);state[k][t]=a;save();render();}
function setMove(id,g,cur){if(!g||g===cur){delete state.move[id];}else{state.move[id]=g;}save();}
let cur=Object.keys(DATA)[0];
function render(){
  const tabs=document.getElementById('tabs');tabs.innerHTML='';
  for(const t of Object.keys(DATA)){const b=document.createElement('button');const d=(state.drop[t]||[]).length;const s=(state.star[t]||[]).length;
    b.textContent=`${t} ${DATA[t].length-d}/${DATA[t].length}`+(s?` ★${s}`:'');b.className=t===cur?'on':'';b.onclick=()=>{cur=t;render();};tabs.appendChild(b);}
  const g=document.getElementById('grid');g.innerHTML='';
  document.getElementById('summ').textContent=SUMM[cur]||'';
  const nd=DATA[cur].filter(c=>DOC[c.id]).length;
  document.getElementById('docbtn').textContent=`★ star all ${nd} cited in layouts.md (${cur})`;
  document.getElementById('docbtn').style.display=nd?'':'none';
  for(const c of DATA[cur]){const d=has('drop',cur,c.id),s=has('star',cur,c.id);
    const el=document.createElement('div');el.className='tile'+(d?' drop':'')+(s?' star':'');
    const opts=GROUPS.map(x=>`<option value="${x}" ${ (state.move[c.id]||cur)===x?'selected':''}>${x}</option>`).join('');
    const badge=DOC[c.id]?`<span class="badge${DOC[c.id]==='seen'?' seen':''}" title="cited in the layouts.md exemplar table${DOC[c.id]==='seen'?'; the writing agent looked at it':''}">layouts.md${DOC[c.id]==='seen'?' · seen':''}</span>`:'';
    el.innerHTML=`<img loading="lazy" src="file://${c.png}" title="${c.id}">`+
      `<div class="meta">${badge}<b>${c.id}</b> · ${c.venue} · ${c.tool} · ${c.column} · base:${c.base} · ${c.arrangement}${c.panel_count>1?' x'+c.panel_count:''}${c.worked?' · worked-example':''} · conf:${c.confidence} · groups:${c.groups}<br>${esc(c.subject)}<br><span class="weak">${esc(c.weaknesses)}</span></div>`+
      `<div class="ctl"><select title="move to group">${opts}</select><button class="${s?'staron':''}" title="must-see">★</button><button class="${d?'on':''}" title="drop">✗</button></div>`;
    const sel=el.querySelector('select');sel.onchange=()=>setMove(c.id,sel.value,cur);
    const [bs,bd]=el.querySelectorAll('.ctl button');bs.onclick=()=>toggle('star',cur,c.id);bd.onclick=()=>toggle('drop',cur,c.id);
    g.appendChild(el);}
  document.getElementById('out').value=JSON.stringify(state,null,1);
}
function esc(s){return (s||'').replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));}
function copyOut(){navigator.clipboard&&navigator.clipboard.writeText(document.getElementById('out').value);}
function starDoc(){const a=state.star[cur]||[];for(const c of DATA[cur]){if(DOC[c.id]&&!a.includes(c.id))a.push(c.id);}state.star[cur]=a;save();render();}
function resetAll(){if(confirm('Clear all decisions?')){state={drop:{},star:{},move:{}};save();render();}}
render();
"""


ID_RE = r"\b((?:asplos|osdi|nsdi|sosp)\d\d-\d{3}_fig(?:tex)?\d+[a-z]?)\b"


def doc_exemplars(path):
    """{id: 'cited' | 'seen'} for every figure id in the '### Exemplars' sections of layouts.md ('seen' = the row carries a star)."""
    import re
    out = {}
    for sec in re.split(r"\n(?=#{2,3} )", Path(path).read_text(encoding="utf-8")):
        if "Exemplars" not in sec.split("\n", 1)[0]: continue
        for line in sec.split("\n"):
            for fid in re.findall(ID_RE, line):
                out[fid] = "seen" if ("★" in line or out.get(fid) == "seen") else "cited"
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--semantics", required=True); ap.add_argument("--index", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--ids", help="text file with a comma-separated id list (<pid>_fig<fig>) to restrict the page to")
    ap.add_argument("--doc", help="references/mechanism/layouts.md: ids in its '### Exemplars' tables get a badge (star = 'seen')")
    a = ap.parse_args()
    csv.field_size_limit(10 ** 9)
    idx = {f"{r['paper_id']}_fig{r['fig']}": r for r in csv.DictReader(open(a.index, encoding="utf-8"))}
    want = None
    if a.ids:
        want = {x.strip() for x in Path(a.ids).read_text().replace("\n", ",").split(",") if x.strip()}
    doc = doc_exemplars(a.doc) if a.doc else {}
    ext = Path(a.index).resolve().parent   # <corpus>/extracted, the directory holding <paper_id>/ figure files
    data = {g: [] for g in GROUPS}
    for line in open(a.semantics, encoding="utf-8"):
        if not line.strip(): continue
        r = json.loads(line)
        if r.get("kind") != "mechanism": continue
        fid = f"{r['paper_id']}_fig{r['fig']}"
        if want and fid not in want: continue
        row = idx.get(fid, {})
        cands = [ext / row.get("paper_id", "") / x.replace(".svg", ".png") for x in (row.get("src_svgs") or "").split("|") if x]
        if row.get("pdf_svg"): cands.append(ext / row["paper_id"] / row["pdf_svg"].replace(".svg", ".png"))
        png = next((str(p) for p in cands if p.exists()), "")
        c, lay = r["content"], r["layout"]
        g = (c.get("groups") or ["anatomy"])[0]
        if g not in data: g = "anatomy"
        data[g].append(dict(id=fid, venue=row.get("venue", ""), tool=row.get("tool", ""), column=row.get("column") or "single",
                            base=c.get("base"), arrangement=lay.get("arrangement"), panel_count=lay.get("panel_count") or 1,
                            worked=bool(c.get("worked_example")), confidence=r.get("confidence"), groups="+".join(c.get("groups") or []),
                            subject=c.get("subject") or "", weaknesses=" | ".join(r["encoding"].get("weaknesses") or []), png=png))
    for g in data:
        data[g].sort(key=lambda t: (t["base"] or "", t["id"]))
    summ = {g: f"{len(v)} candidates · bases: " + ", ".join(f"{b} {n}" for b, n in sorted(
        __import__('collections').Counter(t['base'] for t in v).items(), key=lambda kv: -kv[1])) for g, v in data.items()}
    page = ("<!doctype html><meta charset='utf-8'><title>Mechanism exemplar candidates</title><style>" + CSS + "</style>"
            "<header><div class='tabs' id='tabs'></div><div class='summ' id='summ'></div>"
            "<div class='summ'><button id='docbtn' onclick='starDoc()' style='display:none'></button></div>"
            "<div class='summ'>★ = must-see exemplar (goes into layouts.md and assets/exemplars) · ✗ = drop · the select moves a figure to another group. "
            "Decisions stay in this browser; copy the JSON at the bottom when done.</div></header>"
            "<div class='grid' id='grid'></div>"
            "<div style='padding:0 10px'><button onclick='copyOut()'>copy decisions JSON</button> <button onclick='resetAll()'>reset</button></div>"
            "<textarea id='out' readonly></textarea>"
            "<script>const GROUPS=" + json.dumps(GROUPS) + ";const DATA=" + json.dumps(data, ensure_ascii=False) + ";const SUMM=" + json.dumps(summ, ensure_ascii=False) + ";const DOC=" + json.dumps(doc) + ";" + JS + "</script>")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(page, encoding="utf-8")
    print(f"wrote {a.out}: " + ", ".join(f"{g} {len(v)}" for g, v in data.items()) + f" ({sum(len(v) for v in data.values())} tiles; {sum(1 for v in data.values() for t in v if not t['png'])} without PNG"
          + (f"; {sum(1 for v in data.values() for t in v if t['id'] in doc)} of {len(doc)} doc-cited ids on the page)" if doc else ")"))


if __name__ == "__main__":
    main()
