---
name: cover-design
description: Design typography-driven video cover images using HTML/CSS + Chrome DevTools screenshot. Generates covers in all needed aspect ratios - 16:9 (YouTube), 16:10 (Bilibili), 9:16 and 3:4 (抖音/视频号 竖屏短视频) - with big readable text. Different from `cover-image` (AI hand-drawn aesthetic) - this is precise typography control via code. Use when user asks for "视频封面", "thumbnail", "做封面", "cover design", "缩略图", "横屏/竖屏封面", "抖音封面", "视频号封面".
---

# Cover Design · 代码驱动的封面设计

用 HTML/CSS 写封面,然后用 Chrome DevTools MCP 截图成 PNG。**字体精确可控**,适合视频缩略图、文章题图、社交分享卡这类对文字位置敏感的场景。

## 跟 `cover-image` 的分工

| | `cover-image` | `cover-design` (本 skill) |
|---|---|---|
| 渲染方式 | AI 生图 (Replicate gpt-image-2) | HTML/CSS + 浏览器截图 |
| 视觉风格 | 手绘 / 插画 / 编辑设计 | 排版驱动 / typography hero |
| 文字精度 | AI 渲染的文字常常糊 / 错字 | 100% 精确 |
| 适合 | 文章题图 / 抽象概念 / 美术导向 | 视频缩略图 / 大标题 / 品牌一致性 |
| 风格扩展 | 通过 prompt 调整 | 通过新增 HTML 模板扩展 |

需要 thumbnail 在 160px 缩略图也读得出大字 - 用本 skill。
需要插画美感和氛围 - 用 `cover-image`。

## 适用场景

- 横屏视频缩略图 (YouTube / Bilibili)
- 竖屏短视频封面 (抖音 / 视频号)
- 文章 hero 题图 / 社交分享卡 (X Card / Open Graph)
- 系列内容 (品牌一致性)

## 输出比例（4 套核心）

封面要覆盖横屏长视频和竖屏短视频，去重后是 **4 种核心长宽比**，分两个模板族生成。完整规格、平台落点像素、安全区见 `references/platform-specs.md`。

| 比例 | 朝向 | 设计画布 | 模板族 | 主要平台 |
|---|---|---|---|---|
| 16:9 | 横 | 1920×1080 | `hero-typography` | YouTube、横屏短视频 |
| 16:10 | 横 | 1920×1200 | `hero-typography` | Bilibili（封面位是 16:10，不是 16:9） |
| 9:16 | 竖 | 1080×1920 | `hero-typography-vertical` | 抖音、视频号 |
| 3:4 | 竖 | 1080×1440 | `hero-typography-vertical` | 视频号官方封面、抖音九宫格 |

一期视频通常做 **1 个横屏设计 + 1 个竖屏设计**，各导出 2 个比例，共 4 张图。横屏的 16:9↔16:10、竖屏的 9:16↔3:4 只差 `--cv-h`，同一 HTML 改一个变量就能切。**竖屏务必遵守安全区**（抖音/视频号首尾会叠 UI 或被裁），核心文字居中。

## 核心原则

### 1. Thumbnail ≠ Slide

封面缩略图在订阅列表 / 推荐位 / 搜索结果里最小可能只有 160px 宽。**bento 网格、4 个 metric tiles、信息密集的布局都不工作**。要的是:

- **单焦点** - 一个主元素占据 40-60% 画面
- **大字优先** - 主标题字号 ≥ 200px (1920×1080 画布)
- **3 秒原则** - 缩到 160px 仍能读出主标题
- **少即是多** - 一个视觉钩子 + 标题 + 副标 + 作者署名,完。

详见 `references/thumbnail-vs-slide.md`。

### 2. 模板驱动 + 参数化

每种风格落地为一个 HTML 模板,所有可变内容(主标题、副标、accent 色、作者署名等)通过 CSS 变量或文本占位符暴露。新增风格 = 新增一个模板,不动 skill 主流程。

可用模板见 `templates/` 目录，每个风格一对（横屏 + 竖屏）。当前有 13 个风格（见 Step 2 列表），风格目录与扩展规格见 `references/design-styles.md`。

### 3. 固定像素画布 + 浏览器陷阱

`.cover` 元素**必须用固定像素**（通过 `--cv-w` / `--cv-h` 变量 - 横屏 1920 宽、竖屏 1080 宽，高度按比例取值），**不要用 `vw` / `vh` / `%`**。原因见 `references/render-pipeline.md` 里的浏览器视口陷阱章节 - 简单说,resize_page 设的高度不等于实际视口高度,Chrome 工具栏 / 标签栏会吃掉 200-400px。固定像素 + fullPage 截图才稳。

### 4. 传达 > 好看

封面读得清还不够,要在三秒内说清**是什么 / 什么品类 / 什么领域**:产品名做主元素、品类给信号(agent skill→斜杠命令条、模型→logo)、领域给锚(设计→before/after、安全→告警)。品牌署名只出现一次,精简次要 chrome。这是封面质量能超过纯模板套用的关键一环 - 详见 `references/cover-composition.md`。

## 工作流

### Step 1 · 收集信息

问用户(已给的跳过):

1. **目标平台 / 比例** - 要哪些?默认全 4 套(16:9 YouTube / 16:10 Bilibili / 9:16 抖音·视频号 / 3:4 视频号·抖音九宫格)。这决定做横屏、竖屏、还是都做 (见上方「输出比例」表)
2. **主标题** - 大字部分,通常 1-3 个英文词或 4-8 个中文字 (必填)
3. **副标题** - 一句话点题,中文 / 英文都行 (必填)
4. **品牌信息** - 频道名 / 作者名 / 日期 (可读 auto memory 的 `video-promo.md`)
5. **强调色** - 默认 lime `#7bff9f`,可换 (可选)
6. **背景** - 默认纯黑 `#000`,可换 (可选)
7. **品牌 logo** - 要不要带某个模型/产品/厂商的官方 logo (Claude / OpenAI / Gemini / DeepSeek / Ollama……)?来源是 `@lobehub/icons`,取图标和放置见 `references/brand-logos.md` (可选)
8. **额外元素** - 比如版本号、tagline、装饰图形 (可选)
9. **输出路径** - 默认输出到视频目录,文件名带比例后缀 (`cover-16x9.html/.png` 等)
10. **是不是讲某个具体产品 / 工具?** - 是的话拿到官网 URL,进入**品牌匹配模式**(见下),用产品自己的色 + 字 + logo,比频道默认 lime 更贴合产品

如果用户给了文章 / 脚本路径,先 Read 抽取主标题和副标题,再确认。

#### 品牌匹配模式(选题是某个具体产品 / 工具 / 开源项目时)

封面采用**产品官网的品牌色和字体**,封面气质和被介绍的产品一致。运行:

```bash
scripts/extract-brand-theme.sh https://产品官网
```

它输出可直接写入模板 `:root` 的 Google Fonts + 颜色 token(含 oklch 原值,Chrome 原生支持,原样写入即可)。用提取值覆盖模板默认的 `--accent`/`--bg`/`--ink`/`--font-display`/`--font-mono`,风格按官网调性从 `design-styles.md` 选最接近的。**方法、字体中文搭配、取不到时的处理见 `references/brand-theme.md`**。这和 `brand-logos.md`(取 logo)互补,配齐「色 + 字 + logo」一整套。

### Step 2 · 选模板（按朝向选模板族）

根据 Step 1 要的比例选模板族:

先按朝向选模板族，再按风格选具体模板（每个风格都有横屏 + 竖屏两版）:

- 要横屏 (16:9 / 16:10) → `{style}.html`
- 要竖屏 (9:16 / 3:4) → `{style}-vertical.html`
- 两个都要 → 两版各做一份,共享同一套标题 / 副标 / 品牌信息

当前可用风格（每个都有横屏 `{style}.html` + 竖屏 `{style}-vertical.html`）:
- **`hero-typography`** - 黑底霓虹大字 + fan-out 节点。技术解读 / 新功能发布，强视觉钩子。
- **`swiss`** - 瑞士国际主义：暖纸底 + 网格 + 极轻大字 + 单一强调色 + 1px 细线。冷静专业，技术拆解 / 评测 / 数据。
- **`neo-brutalism`** - 新粗野：高饱和撞色 + 粗黑描边 + 硬阴影 + 圆角块。玩味醒目，产品发布 / 工具类。
- **`bauhaus`** - 包豪斯：米白底 + 红黄蓝几何色块 + 粗网格。经典感，设计 / 理论 / 艺术类。
- **`editorial`** - 杂志风：暖纸底 + 衬线大标题 + 氛围背景 + 细线引文。有质感，观点 / 深度长文 / 人物。
- **`brutalism`** - 粗野：白底 + 系统/等宽字体 + 硬黑边框 + 刻意朴素。黑客 / 独立开发 / 逆向工程气质。
- **`aurora`** - 极光渐变：深底 + 多彩光晕 + 通透细字。AI / SaaS / 现代科技，当下感最强。
- **`glass-dark`** - 深色玻璃拟态：深底 + 背后柔光 + 磨砂玻璃面板。AI / 产品 / 现代科技，通透高级。
- **`terminal`** - 终端黑：纯黑 + 等宽荧光 + 扫描线 + 光标。CLI / 开发 / 黑客 / 逆向。
- **`noir-editorial`** - 暗调杂志：近黑 + 衬线大标题 + 暖金强调 + 颗粒。观点 / 深度 / 人物。
- **`spotlight`** - 聚光戏剧光：全黑 + 单束聚光 + 强暗角 + 高对比。发布 / 悬念 / 重磅。
- **`blueprint`** - 深蓝图：深藏青 + 白色网格线稿 + 等宽标注。架构 / 原理 / 技术拆解。
- **`holographic`** - 暗调全息：深底 + 油膜虹彩大字 + 全息箔 + 噪点。前沿 / 概念 / 潮流科技。

每个风格的视觉锚点、identity test、适用场景见 `references/design-styles.md`。

### Step 3 · 定制内容

读取选定模板的 HTML,把占位符替换成用户的实际内容:

| 占位符位置 | 替换内容 |
|---|---|
| `<title>` | 文档标题 + 频道名 |
| `.tag` / `.brand-mark` | 顶部品牌行 |
| `.hero-eyebrow` | 主标题上方小字 (类似 kicker) |
| `.hero-title` | 主标题大字 (英文小写效果最好) |
| `.hero-sub` | 中文副标题 |
| `.foot .author` | 作者署名 |
| `.foot .episode` | 底部右侧 chip |
| `--accent` (CSS var) | 强调色 |
| `--bg` (CSS var) | 背景色 |
| 品牌 logo (可选) | 顶部品牌行 / 标题前 lockup / 角标，来源 `@lobehub/icons`，做法见下「品牌 Logo」节 |

两个模板族共享上面这套占位符（竖屏族没有侧边 `.nodes` 和 `.episode`，其余一致）。**竖屏族**：所有文字已在 `.safe` 列里垂直居中，落在安全带内，不要把文字往画布上下边缘挪。

用 `Write` 工具把定制后的 HTML 写到输出路径（与最终 PNG 同目录）。横屏一版、竖屏一版分别写。

#### 品牌 Logo（@lobehub/icons）

用户要带某个模型/产品/厂商 logo 时（讲 Claude、OpenAI、Gemini、DeepSeek、Ollama 等），从 **[@lobehub/icons](https://lobehub.com/icons)** 取官方 logo 融进模板。**完整说明（CDN URL、变体、放法、避坑、identity test）见 `references/brand-logos.md`**，要点:

1. **取图标**：跑 helper 下载到封面同目录的 `assets/`（离线可渲染，最稳）:
   ```bash
   scripts/fetch-brand-icon.sh claude color svg ./assets   # 官方配色
   scripts/fetch-brand-icon.sh openai mono  svg ./assets   # 单色，可 CSS 重新着色
   ```
   也可直接引 CDN：`https://unpkg.com/@lobehub/icons-static-svg@latest/icons/{id}.svg`（快速预览用）。
2. **选变体**：要官方配色用 `color`；要跟封面同色系用 `mono`（`fill=currentColor`，内联后父级 `color` 着色）。注意不是每个 id 都有 `-color`，脚本会自动回退 mono。
3. **放置**：首选**内联 SVG**（可着色、最清晰），放顶部品牌行（`hero-typography`/`swiss` 是 `.topbar .tag`；其余风格是 `.top .kicker`）旁，或标题前做 lockup，或角标。**深色底别用 mono `<img>`（会变黑看不见），用 `color` 变体或内联着色。**
4. logo 是辅助识别，标题仍是第一焦点 - 缩到 160px 要先看到标题。

### Step 4 · 渲染成 PNG（每个比例一张）

对 Step 1 选定的**每个比例**渲染一次。改 HTML `:root` 的 `--cv-h` 切比例（横屏 1080↔1200，竖屏 1920↔1440），resize 到对应尺寸，截图存成带后缀的文件。逐比例的 resize 尺寸 + 输出文件名见 `references/render-pipeline.md` 的多比例表。

标准三步（每个比例重复，同一页面可复用 - 改 `--cv-h` 后 reload 再截）:

1. `mcp__chrome-devtools__new_page` 打开 `file://` 路径
2. `mcp__chrome-devtools__resize_page` 设到 `画布宽 ×（画布高 + 20）`
3. `mcp__chrome-devtools__navigate_page` reload(确保新尺寸下重新布局)
4. `mcp__chrome-devtools__take_screenshot` `fullPage: true` → `cover-{比例}.png`

每张 PNG 是 2x retina（如 16:9 → 3840×2160，9:16 → 2160×3840），缩到平台落点尺寸都清晰。

### Step 5 · 验收 + 迭代

`open` 在 macOS 默认查看器里打开所有 PNG 给用户看。

**先过内容传达自检（见 `references/cover-composition.md`）**:
- [ ] **三信号**都到位?逐条指认画面里哪个元素负责:**是什么**(主角是不是最显眼)/ **什么品类**(agent skill→命令条、模型→logo)/ **什么领域**(设计→before/after、安全→告警…)
- [ ] **品牌署名只出现一次**?(注意区分:产品名=选题主角要显眼,频道署名=低调一次。两者不算重复)
- [ ] 有没有可删的**次要 chrome**(日期 / `Ep·`胶囊 / 分隔横线 / 装饰标签)?空白处是有信息量的视觉还是纯空?
- [ ] 转变类选题(把 X 变成 Y / 优化前后)有没有放 **before→after 装置**?

再问视觉反馈:
- 文字位置 / 字号合不合适?
- **缩略图测试** - 缩到 ~320px / 160px 宽,主标题还读得出吗?(3 秒原则)
- **竖屏安全区** - 9:16 / 3:4 的核心文字是否都在中央安全带、没贴边?
- accent / 背景色调要不要换?是否换模板?

> **多方向预览**:定稿前不确定方向时,**一次给出 3-4 个不同方向供用户选择**(不同风格 / 配色),比单版反复改收敛更快。存档命名 `cover-styles/{字母}-{风格}.html/.png`。

迭代时优先改 CSS 变量和占位符文本,不要重新写整个 HTML(节省 token,改动可见)。竖屏调试若用了 `body.show-guide` 看安全带,**最终渲染前去掉这个 class**。

### Step 6 · 完成

简短清单:

```
封面已生成（按你选的平台 / 比例）:
├── cover-16x9.png   - 16:9  YouTube / 横屏短视频
├── cover-16x10.png  - 16:10 Bilibili
├── cover-9x16.png   - 9:16  抖音 / 视频号
└── cover-3x4.png    - 3:4   视频号官方封面 / 抖音九宫格
（对应 .html 源文件同目录）

已用系统默认查看器打开。如需调整告诉我哪里改。
```

只选了部分平台就只出对应比例。

## 写新模板的约定

未来加新模板时遵守以下约定(以便 skill 主流程不动也能识别):

1. 文件名 kebab-case,横屏族用基名(如 `split-hero.html`),竖屏族加 `-vertical` 后缀
2. `.cover` 元素**必须**:
   - 用 `--cv-w` / `--cv-h` 变量定宽高(固定像素,**不要** `vw`/`vh`/`%`);横屏族 1920 宽、竖屏族 1080 宽
   - `position: relative; overflow: hidden;`
   - 直接作为 `<body>` 第一个 child(或 flex 容器居中其内容)
3. CSS 变量在 `:root` 暴露,**至少**包含:`--cv-w`、`--cv-h`、`--bg`、`--ink`、`--accent`、`--font-display`、`--font-mono`
4. 字体用 Google Fonts 加载,优先 `Manrope` (display) + `Noto Sans SC` (中文) + `JetBrains Mono` (mono)
5. 文件顶部 HTML 注释里写明:支持的**比例**和怎么切(改 `--cv-h`)、适配**平台**、以及"何时用这个模板"(让 Step 2 能正确推荐)
6. 竖屏模板把文字收在垂直居中的安全带里,别贴上下边缘(见 `references/platform-specs.md` 安全区)

新模板写好后**不需要**改 SKILL.md 主流程,只要 Step 2 时把它列入候选即可。

## Critical Rules

1. **固定像素画布** - `.cover` 用 `--cv-w`/`--cv-h` 固定像素(横屏 1920 宽 / 竖屏 1080 宽),不要 viewport 单位
2. **fullPage 截图** - 截图时 `fullPage: true`,避免视口陷阱
3. **3 秒原则** - 主标题字号 ≥ 200px,缩到 160px 也能读
4. **按目标平台出全比例** - 默认 4 套(16:9/16:10/9:16/3:4);竖屏核心文字放安全带,首尾会叠 UI/被裁(见 `references/platform-specs.md`)
5. **不替 cover-image 做事** - 用户要插画 / AI 生图,转 `cover-image` skill,本 skill 只做代码驱动的排版型封面
6. **不自动发布** - 只产 PNG,不动用户的发布渠道
7. **品牌信息从 auto memory** - 频道名 / 作者名优先读 `video-promo.md`,首次没有再问用户
8. **品牌 logo 用官方来源** - 需要模型/产品/厂商 logo 时从 `@lobehub/icons` 取(见 `references/brand-logos.md` + `scripts/fetch-brand-icon.sh`),不要手搓或随便找网图;深色底别用 mono `<img>`(会变黑),用 color 变体或内联着色;对比类选题(X vs Y)双 logo 放大成标题上方 lockup,别缩成 kicker 小图标
9. **中文标题行高** - 中文大标题 line-height ≈1.05–1.10,别用拉丁 display 的 0.9(会撞行);见 `references/design-styles.md`
10. **渲染输出别用 `/tmp`** - headless 渲染输出到持久目录(`/tmp` 会被清);优先用 `scripts/render-cover.sh`,坑见 `references/render-pipeline.md`
11. **封面要传达选题,不止好看** - 定稿前过三信号自检(是什么/品类/领域)、品牌署名只一次、精简次要 chrome、转变类放 before/after;见 `references/cover-composition.md`
12. **讲具体产品时做品牌匹配** - 用产品官网真实色 + 字(`scripts/extract-brand-theme.sh` + `references/brand-theme.md`),不要一律采用默认 lime;封面气质和被介绍的产品一致更专业
