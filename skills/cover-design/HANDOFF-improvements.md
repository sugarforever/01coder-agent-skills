# Cover-Design Skill · 改进 Handoff（来自 impeccable 选题实战，2026-06-02）

> 背景：做一期 impeccable（前端设计 Skill）视频时，本 skill **没装进当时环境**，于是全程手搓封面（手写 HTML/CSS + headless Chrome 截图），并跟用户多轮迭代。
> 结论：**手搓的成品质量高于本 skill 模板套出来的**。本文档拆解差距来源，给出**可直接实现**的补强项。渲染管线（`scripts/render-cover.sh`）已是强项，**不动**——手搓那套反而更糙、重踩了本 skill 早解决的坑（`/tmp` 被清、截图落盘时序、SingletonLock 等）。

## 差距来源（手搓为什么赢）

| 维度 | 本 skill 现状 | 这次手搓做对的 | 是否该补 |
|---|---|---|---|
| 渲染管线 | ✅ 成熟（多比例 / 2x / 踩坑齐全） | 更糙，不如 skill | ❌ 保持现状 |
| 视觉风格模板 | ✅ 13 风格 × 横竖 | 直接写 bespoke CSS | 🔸 可加 1 个「品牌匹配 / before-after」样例模板 |
| **品牌主题（色 + 字）** | ❌ 只有默认 lime + 品牌 **logo** | 从产品官网扒真实 oklch 色板 + Google Fonts 套上 | ✅ **高价值，必补** |
| **封面内容策略** | ❌ 只有 thumbnail 易读性 | 一眼说清「是什么/品类/领域」、品牌只一次、空白放有意义视觉、转变类用 before→after | ✅ **高价值，必补** |
| 迭代裁剪 | 🔸 有验收 Step，但无「砍 chrome」原则 | 用户反馈逼出「冗余元素一律删、品牌只一次」 | ✅ 并入验收清单 |

## 补强项 1 · 品牌主题提取（新增 reference + helper）

**场景**：选题是「某个具体产品/工具」（impeccable、某 SaaS、某开源项目）时，封面套**产品自己的品牌色和字体**，比套频道默认 lime 更专业、更原生。

**这次的实操配方**（可直接固化成 `scripts/extract-brand-theme.sh`）：

```bash
# 1) 抓官网 HTML
curl -sL https://impeccable.style/ -o /tmp/site.html

# 2) 扒 Google Fonts（字体分工）
rg -oiP 'fonts\.googleapis\.com/css2\?family=[^"'\'' ]+' /tmp/site.html

# 3) 扒 CSS 变量里的颜色（hex / oklch / 自定义品牌变量名）
#    现代站点多用 oklch + 语义命名（如 --ks-kinpaku 金箔、--ks-lacquer 漆器）
for css in $(rg -oP 'href="\K/[^"]+\.css' /tmp/site.html); do curl -sL "https://impeccable.style$css"; done \
  | rg -oiP '\-\-[a-z0-9-]+:\s*(oklch\([^)]+\)|#[0-9a-f]{3,8})' | sort -u
```

**要点（写进 reference）**：
- **直接用 oklch() 值**：headless Chrome 支持 `oklch()`，把官网原值原样搬进模板 `:root`，比转 hex 更忠实（这次 impeccable 的金箔 `oklch(84% .19 80.46)`、漆黑底 `oklch(7% .006 95)` 直接用）。
- **字体按官网分工映射**：display / body / mono 各取一支；中文标题用与拉丁同气质的 Noto Serif/Sans SC 配对（impeccable 用 Cormorant Garamond 衬线 → 中文配 Noto Serif SC；拉丁数字用 Alumni Sans）。
- **识别语义变量名**能反推品牌调性（`kinpaku`=金箔、`lacquer`=漆器 → 日式漆器美学），帮选风格。
- 产出一个 `brand-theme.md`（色 token + 字体分工）交给模板定制，**和现有 `brand-logos.md`（logo）并列**，凑齐「色 + 字 + logo」一整套品牌匹配。
- 兜底：官网无 CSS 变量/取不到时，回退频道默认（lime + Manrope）。

建议新增：`references/brand-theme.md`（方法 + 避坑）+ `scripts/extract-brand-theme.sh`（封装上面三步，输出 token 清单）。

## 补强项 2 · 封面内容策略（新增 reference + 并入验收）

本 skill 现有 `thumbnail-vs-slide.md` 只管**易读性**（大字、单焦点、160px 可读）。缺**「封面该放哪些元素来传达选题」**。这次用户反馈逼出的硬规则：

### 三信号原则（最高优先）
封面要让人 3 秒读出三件事，缺一补一：
1. **是什么** —— 主角（产品名 / 概念）必须是显眼主元素。本例初版把中文标语「祛 AI 味」做最大、产品名 impeccable 缩成角标 → 用户反馈「品牌名不显眼」。改成 impeccable 金箔大字为主。
2. **什么品类** —— 让人看出是 agent skill / CLI 工具 / 模型 / 框架。手段：品类标签（`Claude Code · Agent Skill`）+ **斜杠命令条**（`/polish /bolder /colorize /animate`，一眼是技能命令）。
3. **什么领域** —— 设计 / 安全 / 数据…要有领域视觉锚。本例用 **before→after 设计小样**（紫渐变套卡片 AI 味 → 漆底金箔衬线干净版）点明「设计」。

### before → after 装置（转变类选题通用）
凡是「把 X 变成 Y」「治某病」「优化前后」的选题，右半/一侧放一个 before→after 对照小样，是**领域感 + 价值传达 + 填空白**三合一的最强单元。可做成可复用 partial（两张 mini「设备框」+ 箭头 + ✕/✓ 标签）。

### 砍 chrome / 品牌只一次（并入 Step 5 验收）
- **品牌署名全图只出现一次**。本例初版 VerySmallWoods 在右上 + 页脚出现两次 → 用户「冗余」。删到只剩左下一处。
- 日期、`Ep ·` 胶囊、上下分隔横线、装饰标签这类**次要 chrome 默认不放**，除非有信息价值。
- 「简洁风」≠ 空：砍的是次要 chrome，**省下的空间用 before/after 或命令条这类有信息量的视觉填**，而不是留大片黑。

建议新增：`references/cover-composition.md`（三信号原则 + before/after 装置 + 砍 chrome 清单），并在 SKILL.md Step 5 验收里加：
- [ ] 三信号都到位？（是什么 / 品类 / 领域）
- [ ] 品牌署名是否只出现一次？
- [ ] 有没有次要 chrome 可删？空白处是有意义视觉还是纯空？

## 补强项 3 · SKILL.md 主流程小改

1. **Step 1 收集信息**加一问：「选题是不是某个**具体产品/工具**？是的话给官网 URL」→ 触发**品牌匹配模式**（跑 `extract-brand-theme.sh`，用产品真实色 + 字 + logo）。
2. **Step 2 选模板**：品牌匹配模式下，模板的 `:root` token 用提取出的品牌值覆盖默认；风格按官网调性挑（漆器金箔 → `noir-editorial`/`editorial` 系）。
3. **Step 3 定制**：转变类选题，挂上 before/after partial。
4. **Step 5 验收**：并入上面的「三信号 / 品牌一次 / 砍 chrome」清单。

## 可参照的成品（质量基线）

这次的迭代产物在 contenthub 仓库 `videos/20260602-impeccable-design-skill/` 下：
- `cover.html` / `cover.png` —— 最终版（品牌匹配 + 三信号 + before/after，简洁）
- `cover-styles/` —— A 杂志浅色 / B 粗野 / C 暖色块 / D 瑞士蓝 / E 官网品牌早期版（一次给 4 方向预览让用户选的工作法，也值得固化进 Step 5「多方向预览」）

> 附带工作法：**一次出 3-4 个差异化方向让用户挑**（而非单版反复改），收敛更快。可考虑写进 Step 5。

## 实现优先级

1. （高）`references/cover-composition.md` + Step 5 验收清单 —— 纯文档，立刻提质，零风险。
2. （高）`references/brand-theme.md` + `scripts/extract-brand-theme.sh` —— 解锁品牌匹配。
3. （中）before/after partial + 1 个品牌匹配样例模板（把 impeccable 这版泛化）。
4. （低）Step 5 加「多方向预览」工作法。
