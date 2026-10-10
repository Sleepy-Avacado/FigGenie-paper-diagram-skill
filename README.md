<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/banner-dark.png">
    <img src="docs/banner-light.png" width="100%" alt="FigGenie-Skill: a paragraph from a paper on the left becomes a camera-ready architecture figure on the right">
  </picture>
</p>

<p align="center">
  <b>Draw camera-ready figures for top-venue papers.</b><br>
</p>

<p align="center">
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-d9661f">
  <img alt="Codex skill" src="https://img.shields.io/badge/Codex-skill-182c51">
  <img alt="Agent Skills standard" src="https://img.shields.io/badge/Agent%20Skills-SKILL.md-5b9bd5">
  <img alt="Output: SVG, PDF, PPTX" src="https://img.shields.io/badge/output-SVG%20%7C%20PDF%20%7C%20PPTX-6a9955">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-lightgrey">
</p>

<p align="center">
  <a href="#examples"><b>Examples</b></a>  | 
  <a href="#why-figgenie">Why FigGenie</a>  | 
  <a href="#quick-start">Quick start</a>  | 
  <a href="#features">Features</a>  | 
  <a href="README.zh-CN.md">中文说明</a>
</p>

<div align="center">
<table>
  <tr>
    <th valign="top">🏆<br>Top-Conf<br>Style</th>
    <th valign="top">✏️<br>Editable</th>
    <th valign="top">📐<br>SVG</th>
    <th valign="top">📄<br>PDF</th>
    <th valign="top">📊<br>PPTX</th>
    <th valign="top">🧮<br>Formulas</th>
    <th valign="top">🀄<br>Chinese</th>
    <th valign="top">🕹️<br>Interactive<br>Editor</th>
  </tr>
  <tr>
    <td align="center">✅</td>
    <td align="center">✅</td>
    <td align="center">✅</td>
    <td align="center">✅</td>
    <td align="center">✅</td>
    <td align="center">✅</td>
    <td align="center">✅</td>
    <td align="center">🚧</td>
  </tr>
</table>
<sub>✅ available now  |  🚧 coming soon</sub>
</div>

## Examples

The figures below are examples drawn by FigGenie Skill. It draws editable vector graphics, not bitmaps from an
image-generation model, so you can open them in **Illustrator**, **PowerPoint** and similar tools and keep editing.
Chinese text and formulas are supported too. The systems, components and numbers in the figures are invented.

<table>
  <tr>
    <th colspan="2">Architecture figures</th>
  </tr>
  <tr>
    <td valign="top">
      <img src="docs/gallery/tidepool-fig1.png" width="400" alt="Tidepool architecture: a control plane with Request Router, Tide Scheduler and KV Directory above a data plane of prefill and decode instances whose Transfer Engines stream KV blocks into a pooled KV cache">
      <br><sub><a href="docs/gallery/tidepool-fig1.svg">SVG</a> / <a href="docs/gallery/tidepool-fig1.pdf">PDF</a> /
      <a href="docs/gallery/tidepool-fig1.pptx">PPTX</a></sub>
    </td>
    <td valign="top">
      <img src="docs/gallery/brickyard-fig1.png" width="400" alt="Brickyard architecture: a CI service band above a build pool with a Graph Merger, a three-stage Build Planner and runners with sandbox executors; jobs J1 to J3 are tracked by colour">
      <br><sub><a href="docs/gallery/brickyard-fig1.svg">SVG</a> / <a href="docs/gallery/brickyard-fig1.pdf">PDF</a> /
      <a href="docs/gallery/brickyard-fig1.pptx">PPTX</a></sub>
    </td>
  </tr>
  <tr>
    <th colspan="2">Mechanism figures</th>
  </tr>
  <tr>
    <td valign="top">
      <img src="docs/gallery/tidepool-fig4.png" width="400" alt="Tidepool mechanism: two Gantt panels comparing transfer after prefill, where decode starts at 84 ms, with layer-wise streaming, where decode starts at 57 ms; idle time is hatched and the transfers on the critical path are outlined">
      <br><sub><a href="docs/gallery/tidepool-fig4.svg">SVG</a> / <a href="docs/gallery/tidepool-fig4.pdf">PDF</a> /
      <a href="docs/gallery/tidepool-fig4.pptx">PPTX</a></sub>
    </td>
    <td valign="top">
      <img src="docs/gallery/quota-admission.png" width="400" alt="Quota admission: on the left a service and its quota client reserve quota from the quota manager, are admitted, query the database and refund, with the quota manager's per-tenant bucket record opened up; on the right three placements of the quota manager, CentralQ, SidecarQ and EdgeQ">
      <br><sub><a href="docs/gallery/quota-admission.svg">SVG</a> / <a href="docs/gallery/quota-admission.pdf">PDF</a> /
      <a href="docs/gallery/quota-admission.pptx">PPTX</a></sub>
    </td>
  </tr>
</table>

## Why FigGenie

- **Learned from real figures, not from taste.** Its rules come with numbers, measured on 2,041 hand-rated figures
  from top systems venues.
- **Drawn at print size.** It works in points for a 240 pt column, so the labels stay readable in the paper and not
  only on screen.
- **Every figure is checked.** A linter measures every box in a headless browser, and the agent looks at the render
  before handing anything over.

### Learned from 12,577 top-venue figures

We collected the figures of every OSDI, NSDI, SOSP and ASPLOS paper from 2023 to 2026, rated 2,041 of them by hand,
and measured what separates the good ones from the rest.

| Corpus          | Size                                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------------- |
| Papers          | 1,113 from OSDI, NSDI, SOSP and ASPLOS, 2023 to 2026                                                     |
| Figures indexed | 12,577                                                                                                   |
| Rated by hand   | 2,041                                                                                                    |
| Distilled into  | 20 layout templates, 5 mechanism families, 21 palettes, 485 annotated exemplars and 2,853 reusable parts |

<p align="center">
  <img src="docs/corpus-collage.png" width="100%" alt="A collage of 16 architecture and mechanism figures from ASPLOS and SOSP papers">
  <br><sub>16 figures from the corpus, taken from papers published under CC BY 4.0. Each figure belongs to its authors;
  see <a href="CREDITS.md">CREDITS.md</a>.</sub>
</p>

### How it draws

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/workflow-dark.png">
    <img src="docs/workflow-light.png" width="100%" alt="The workflow: your material, a brief you confirm, spec and plan, draw and check in a loop of render, lint, look and fix, then deliver SVG, PDF, PNG, PPTX and a caption for you to review; changes asked in plain words go back to the drawing step">
  </picture>
</p>

## Quick start

Simply drop the URL of this repo into your AI agent and ask it to install the skill:

```text
Install this skill and set up its dependencies: https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill
```

Or install it manually:

**Claude Code**: install the plugin.

```text
/plugin marketplace add Sleepy-Avacado/FigGenie-paper-diagram-skill
/plugin install figgenie@figgenie
```

**Codex and other agents**: FigGenie is a plain Agent Skill, a folder with a `SKILL.md`, scripts and references. Any
agent that loads skills, runs shell commands and can look at a PNG can use it.

```bash
git clone https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill.git
mkdir -p ~/.agents/skills
ln -s "$PWD/FigGenie-paper-diagram-skill/skills/figgenie-paper-diagram" ~/.agents/skills/figgenie-paper-diagram
```

Older Codex releases read skills from `~/.codex/skills` instead.

**Requirements**: Python 3 and a headless Chromium for rendering and linting.

```bash
pip install lxml pillow playwright fonttools
playwright install chromium
```

Optional: Node.js 18+ for TeX formulas (MathJax installs itself on first use), and `pip install python-pptx` for the
PowerPoint export (native equations there also need Office's `mathml2omml.xsl`).

## Features

| Feature          | What you get                                                                                                                                                                 |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Figure kinds** | Architecture figures in 20 layout templates. Mechanism figures in five families: comparison, evolution, logic, walkthrough and anatomy, with worked examples in real values. |
| **Outputs**      | An SVG with fonts embedded and every element named, a PDF cut to the figure's size for LaTeX, a PNG preview and a caption draft. An editable PowerPoint deck on request.     |
| **Content**      | Vector TeX formulas, Chinese and other CJK labels, icons from a 2,853-part library, and bitmaps such as screenshots or photos.                                               |
| **Workflow**     | A brief before drawing, a lint and visual self-check after every edit, changes in plain words, and critiques or redraws of existing figures.                                 |

**Editable in PowerPoint.** On request, the finished figure becomes a deck with one native shape per primitive, at the
same coordinates as the SVG.

<table>
  <tr>
    <td valign="top"><img src="docs/pptx/pptx-named-groups.jpg" width="400" alt="PowerPoint selection pane listing groups named after the figure's element ids"><br><sub>Every element is a group named after its id in the spec.</sub></td>
    <td valign="top"><img src="docs/pptx/pptx-native-shape.jpg" width="400" alt="PowerPoint Format Shape pane for a selected box, showing its solid fill and line"><br><sub>Boxes are native shapes with their own fill and line.</sub></td>
  </tr>
  <tr>
    <td colspan="2" valign="top"><img src="docs/pptx/pptx-live-text.jpg" width="826" alt="Editing the text of a label in PowerPoint, with the Helvetica Neue font shown in the ribbon"><br><sub>Labels are live text in the figure's own font.</sub></td>
  </tr>
</table>

## Roadmap

- [ ] Figures in the style of top AI venues (NeurIPS, ICML, ICLR, CVPR, ACL)
- [ ] An interactive editor
- [ ] Support for more editors (draw.io, OmniGraffle and others)

## Acknowledgements

FigGenie learned from the figures of the authors whose papers make up the corpus; the figures remain theirs. The
collage above is credited figure by figure in [CREDITS.md](CREDITS.md). Fonts: TeX Gyre, Latin Modern, Source Sans,
Inter, Roboto, Arimo, Tinos, Carlito and DejaVu. Formulas: MathJax. Rendering: Playwright and Chromium.

**Removal requests.** If you are an author of a figure used in this repository and want it removed, email
ahawkinthesky@outlook.com or open an issue at
https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill/issues. We will take it down.

## License

The code and documentation are released under the [MIT License](LICENSE). Two things are not covered by it:

- figures and parts taken from published papers, which belong to their authors (see [CREDITS.md](CREDITS.md) and
  [SOURCES.md](SOURCES.md));
- the bundled fonts, which keep their own licenses (see
  [`assets/fonts/LICENSES.md`](skills/figgenie-paper-diagram/assets/fonts/LICENSES.md)).
