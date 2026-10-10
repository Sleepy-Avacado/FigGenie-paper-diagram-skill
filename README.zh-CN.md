<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/banner-dark.png">
    <img src="docs/banner-light.png" width="100%" alt="FigGenie-Skill：左边是一段论文原文，右边是由它画出的架构图">
  </picture>
</p>

<p align="center">
  <b>绘制能直接放进顶会论文的图。</b><br>
</p>

<p align="center">
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-d9661f">
  <img alt="Codex skill" src="https://img.shields.io/badge/Codex-skill-182c51">
  <img alt="Agent Skills standard" src="https://img.shields.io/badge/Agent%20Skills-SKILL.md-5b9bd5">
  <img alt="Output: SVG, PDF, PPTX" src="https://img.shields.io/badge/output-SVG%20%7C%20PDF%20%7C%20PPTX-6a9955">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-lightgrey">
</p>

<p align="center">
  <a href="#示例"><b>示例</b></a>  | 
  <a href="#为什么选-figgenie">为什么选 FigGenie</a>  | 
  <a href="#快速开始">快速开始</a>  | 
  <a href="#功能">功能</a>  | 
  <a href="README.md">English</a>
</p>

<div align="center">
<table>
  <tr>
    <th valign="top">🏆<br>顶会风格</th>
    <th valign="top">✏️<br>可编辑</th>
    <th valign="top">📐<br>SVG</th>
    <th valign="top">📄<br>PDF</th>
    <th valign="top">📊<br>PPTX</th>
    <th valign="top">🧮<br>公式</th>
    <th valign="top">🀄<br>中文</th>
    <th valign="top">🕹️<br>交互式编辑器</th>
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
<sub>✅ 已支持  |  🚧 即将支持</sub>
</div>

## 示例

下面几张图都出自 FigGenie Skill。它画的是可编辑的矢量图，不是图片生成模型生成的位图，可以直接放进 **Illustrator**、**PPT** 等工具里继续修改，中文和公式也都支持。图中的系统、组件和数字均为虚构。

<table>
  <tr>
    <th colspan="2">架构图</th>
  </tr>
  <tr>
    <td valign="top">
      <img src="docs/gallery/tidepool-fig1.png" width="400" alt="Tidepool 架构图：上方控制面有 Request Router、Tide Scheduler 和 KV Directory，下方数据面的 prefill 和 decode 实例通过 Transfer Engine 把 KV 块写入共享 KV 缓存池">
      <br><sub><a href="docs/gallery/tidepool-fig1.svg">SVG</a> / <a href="docs/gallery/tidepool-fig1.pdf">PDF</a> /
      <a href="docs/gallery/tidepool-fig1.pptx">PPTX</a></sub>
    </td>
    <td valign="top">
      <img src="docs/gallery/brickyard-fig1.png" width="400" alt="Brickyard 架构图：上方是 CI 服务带，下方的构建池里有 Graph Merger、三阶段的 Build Planner 和带沙箱执行器的 runner；作业 J1 到 J3 用颜色追踪">
      <br><sub><a href="docs/gallery/brickyard-fig1.svg">SVG</a> / <a href="docs/gallery/brickyard-fig1.pdf">PDF</a> /
      <a href="docs/gallery/brickyard-fig1.pptx">PPTX</a></sub>
    </td>
  </tr>
  <tr>
    <th colspan="2">机制图</th>
  </tr>
  <tr>
    <td valign="top">
      <img src="docs/gallery/tidepool-fig4.png" width="400" alt="Tidepool 机制图：上下两个甘特图，对比 prefill 之后再传输（decode 在 84 ms 开始）和逐层流式传输（decode 在 57 ms 开始）；空闲时间画成斜线条，关键路径上的传输有橙色边框">
      <br><sub><a href="docs/gallery/tidepool-fig4.svg">SVG</a> / <a href="docs/gallery/tidepool-fig4.pdf">PDF</a> /
      <a href="docs/gallery/tidepool-fig4.pptx">PPTX</a></sub>
    </td>
    <td valign="top">
      <img src="docs/gallery/quota-admission.png" width="400" alt="配额准入：左边是服务通过配额客户端向配额管理器预留配额、获准、查询数据库、退还配额的过程，并摊开配额管理器里每个租户的 bucket 记录；右边是配额管理器的三种放置方式 CentralQ、SidecarQ 和 EdgeQ">
      <br><sub><a href="docs/gallery/quota-admission.svg">SVG</a> / <a href="docs/gallery/quota-admission.pdf">PDF</a> /
      <a href="docs/gallery/quota-admission.pptx">PPTX</a></sub>
    </td>
  </tr>
</table>

## 为什么选 FigGenie

- **规则来自真实的顶会插图，不凭个人审美**：每条规则都有数据依据，统计自 2,041 张经过人工评分的系统顶会论文插图。
- **按论文的实际尺寸作图**：以 pt 为单位，按 240 pt 的单栏宽度来画，放进论文里文字依然清晰，而不只是在屏幕上好看。
- **绘图检查**：lint 会在无头浏览器里逐个测量图中的元素，agent 还会看一遍渲染结果，确认没问题才交付。

### 从 12,577 张顶会插图中提炼

我们收集了 OSDI、NSDI、SOSP、ASPLOS 2023–2026 年所有论文的插图，并进行了人工评分，再统计好图究竟好在哪里。

| 语料库  | 规模                                                 |
| ---- | -------------------------------------------------- |
| 论文   | OSDI、NSDI、SOSP、ASPLOS 2023–2026 年，共 1,113 篇        |
| 收录插图 | 12,577 张                                           |
| 人工评分 | 2,041 张                                            |
| 提炼出  | 20 种布局模板、5 类机制图、21 套配色方案、485 张带标注的范例图、2,853 个可复用元件 |

<p align="center">
  <img src="docs/corpus-collage.png" width="100%" alt="16 张来自 ASPLOS 和 SOSP 论文的架构图和机制图拼图">
  <br><sub>语料库中的 16 张图，均取自以 CC BY 4.0 协议发布的论文。版权归原作者所有，出处见 <a href="CREDITS.md">CREDITS.md</a>。</sub>
</p>

### 绘图流程

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/workflow-dark.png">
    <img src="docs/workflow-light.png" width="100%" alt="工作流程：你提供材料，确认绘图大纲，生成规格和绘图计划，在渲染、lint、看图、修改之间循环，最后交付 SVG、PDF、PNG、PPTX 和图注供你审阅；用自然语言提出的修改意见会回到绘图这一步">
  </picture>
</p>

## 快速开始

直接把本仓库的地址丢给你的 AI，让它帮你安装这个 skill 即可：

```text
帮我安装这个 skill 并配置好依赖：https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill
```

也可以手动安装：

**Claude Code**：安装插件即可。

```text
/plugin marketplace add Sleepy-Avacado/FigGenie-paper-diagram-skill
/plugin install figgenie@figgenie
```

**Codex 及其他 agent**：FigGenie 是一个标准的 Agent Skill，本质上就是一个装着 `SKILL.md`、脚本和参考文档的文件夹。只要你的 agent 能加载 skill、能执行 shell 命令、能查看 PNG 图片，就可以用。

```bash
git clone https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill.git
mkdir -p ~/.agents/skills
ln -s "$PWD/FigGenie-paper-diagram-skill/skills/figgenie-paper-diagram" ~/.agents/skills/figgenie-paper-diagram
```

旧版 Codex 从 `~/.codex/skills` 读取 skill。

**依赖**：Python 3，以及渲染和 lint 要用到的无头 Chromium。

```bash
pip install lxml pillow playwright fonttools
playwright install chromium
```

可选依赖：画公式需要 Node.js 18+（首次使用时会自动安装 MathJax）；导出 PPT 需要 `pip install python-pptx`，如果要在 PPT 里使用原生公式，还需要 Office 自带的 `mathml2omml.xsl`。

## 功能

| 功能     | 内容                                                                       |
| ------ | ------------------------------------------------------------------------ |
| **类型** | 架构图有 20 种布局模板；机制图分为 5 类：方案对比、演变过程、逻辑流程、步骤讲解、结构剖析，还可以配上带真实数值的算例。          |
| **输出** | 内嵌字体、元素均已命名的 SVG；按图的大小裁切、可直接插入 LaTeX 的 PDF；PNG 预览图和图注草稿。需要时还能导出可编辑的 PPT。 |
| **内容** | 矢量 TeX 公式、中文等 CJK 文字、内含 2,853 个元件的图标库，也可以嵌入截图、照片等位图。                     |
| **流程** | 动笔前先出一份绘图大纲请你确认；每次修改后都会跑 lint、检查渲染结果；修改意见用自然语言说就行；也可以点评或重画已有的图。          |

**在 PPT 里直接编辑**：需要时可以把画好的图导出成 PPT，每个图元都是原生形状，位置与 SVG 完全一致。

<table>
  <tr>
    <td valign="top"><img src="docs/pptx/pptx-named-groups.jpg" width="400" alt="PowerPoint 选择窗格，列出按图中元素 id 命名的组"><br><sub>每个元素都是一个组合，以它在 spec 中的 id 命名。</sub></td>
    <td valign="top"><img src="docs/pptx/pptx-native-shape.jpg" width="400" alt="PowerPoint 设置形状格式面板，显示选中方框的纯色填充和线条"><br><sub>方框是原生形状，填充和线条都能改。</sub></td>
  </tr>
  <tr>
    <td colspan="2" valign="top"><img src="docs/pptx/pptx-live-text.jpg" width="826" alt="在 PowerPoint 里编辑标签文字，功能区显示字体 Helvetica Neue"><br><sub>标签是可编辑的文本，字体与图中一致。</sub></td>
  </tr>
</table>

## 路线图

- [ ] 绘制 AI 顶会风格的图（NeurIPS、ICML、ICLR、CVPR、ACL）
- [ ] 交互式的编辑器
- [ ] 支持更多编辑器（Draw.io, OmniGraffle 等）

## 致谢

感谢语料库中各篇论文的作者：FigGenie 的画法都是从他们的插图里学来的，这些图的版权仍归原作者所有。上面那张拼图的出处已在 [CREDITS.md](CREDITS.md) 中逐张注明。本项目用到的字体有 TeX Gyre、Latin Modern、Source Sans、Inter、Roboto、Arimo、Tinos、Carlito 和 DejaVu，公式由 MathJax 排版，渲染使用 Playwright 和 Chromium。

**删除请求**：如果本仓库用到了你的图而你希望撤下，请发邮件到 ahawkinthesky@outlook.com，或在 https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill/issues 提 issue，我们会将其移除。

## 许可证

代码和文档以 [MIT License](LICENSE) 发布，但以下两类内容除外：

- 取自已发表论文的插图和元件，版权归原作者所有（见 [CREDITS.md](CREDITS.md) 和 [SOURCES.md](SOURCES.md)）；
- 随仓库附带的字体，沿用各自的许可证（见 [`assets/fonts/LICENSES.md`](skills/figgenie-paper-diagram/assets/fonts/LICENSES.md)）。
