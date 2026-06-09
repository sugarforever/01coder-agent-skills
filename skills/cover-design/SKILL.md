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
| 文字精度 | AI 渲染的文字常常模糊 / 错字 | 100% 精确 |
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

### 0. 想法先行(方法论主线 · 最高优先)

这个 skill 只采用**一套**构思方法论:Paul Rand 的「想法先行」。封面不是先选模板填标题,而是**先有一个想法(idea)** - 这期到底要让人 get 到什么 - 再让画面为它服务。四步:**研究(不预设)→ 抽取核心想法 → 删减(simplicity 是好想法的副产品)→ 缩到 160px 验证那个想法还在**。

核心想法**不一定是产品名**,形态开放:一个名字 / 一个 logo / 一个隐喻装置 / 一种氛围。下面的所有原则(单焦点、传达、精简)都是这套方法论的执行层 - **先有想法,再谈表达**。完整方法论见 `references/design-conception.md`,这是全 skill 的构思总纲,不要混入别的设计流派。

### 1. Thumbnail ≠ Slide

封面缩略图在订阅列表 / 推荐位 / 搜索结果里最小可能只有 160px 宽。**bento 网格、4 个 metric tiles、信息密集的布局都不工作**。要的是:

- **单焦点** - 一个主元素占据 40-60% 画面
- **大字优先** - 主标题字号 ≥ 200px (1920×1080 画布)
- **3 秒原则** - 缩到 160px 仍能读出主标题
- **少即是多** - 一个视觉钩子 + 标题 + 副标 + 作者署名,完。

**元素预算(默认 ≤ 5,模板一律按此交付精简版,多出来的先删再说)**:① 一个 kicker(品类 / 工具,可选)② 一个核心主元素(标题 或 logo / 隐喻装置 - 单焦点)③ 一句副标(可选)④ 一处署名(只一次)⑤ 至多一个领域装置(before/after、命令条、N→1、大数字 - 仅当承载信息时)。**默认不放**:日期、eyebrow 小字、`Ep·` 胶囊、扇出节点 / 纯装饰色块 / 几何形、上下分隔横线、第二处署名、重复副标。要加回任何一项,先自问「它传达了信息吗」 - 不传达就删,这是原则 0「删减」的执行。

**关键区分(精简时别误伤)**:风格本身的视觉语言 - swiss 的网格细线、bauhaus 的几何色块、terminal 的扫描线 + 光标、aurora / glass 的光晕渐变、blueprint 的网格线稿 - 是这个风格的**身份**,不是 chrome,**不在精简之列**。要删的是被过度填充的**内容槽**(eyebrow / 日期 / episode 胶囊 / 第二署名)和**不承载信息的装饰**(扇出节点、纯平衡用的抽象色块)。

详见 `references/thumbnail-vs-slide.md` 与 `references/cover-composition.md`(默认元素集)。

### 2. 模板驱动 + 参数化

每种风格落地为一个 HTML 模板,所有可变内容(主标题、副标、accent 色、作者署名等)通过 CSS 变量或文本占位符暴露。新增风格 = 新增一个模板,不动 skill 主流程。

可用模板见 `templates/` 目录，每个风格一对（横屏 + 竖屏）。当前有 13 个风格（见 Step 2 列表），风格目录与扩展规格见 `references/design-styles.md`。

### 3. 固定像素画布 + 浏览器陷阱

`.cover` 元素**必须用固定像素**（通过 `--cv-w` / `--cv-h` 变量 - 横屏 1920 宽、竖屏 1080 宽，高度按比例取值），**不要用 `vw` / `vh` / `%`**。原因见 `references/render-pipeline.md` 里的浏览器视口陷阱章节 - 简单说,resize_page 设的高度不等于实际视口高度,Chrome 工具栏 / 标签栏会吃掉 200-400px。固定像素 + fullPage 截图才稳。

### 4. 传达 > 好看(让核心想法落到画面)

封面读得清还不够,要在三秒内说清**核心想法是什么(及它的形态)/ 什么品类 / 什么领域**:核心想法做最显眼的主元素(它可能是名字、logo、隐喻装置或氛围 - 见原则 0),品类给信号(agent skill→斜杠命令条、模型→logo),领域给锚(设计→before/after、安全→告警)。品牌署名只出现一次,精简次要 chrome(simplicity 是好想法的副产品)。这是封面质量能超过纯模板套用的关键一环 - 详见 `references/cover-composition.md`。

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

### Step 1.5 · 构思:抽取核心想法（动手前必做 · 见原则 0）

收集完信息,**先别选模板**。按 `references/design-conception.md` 走一遍「想法先行」,抽出这期的**核心想法**写下来,再定层级(核心想法做最大主元素 ＞ 角度 / 卖点做 accent 副线 ＞ 能力 / 细节做灰字),带着它进 Step 2。

两条提醒:核心想法**不一定是产品名**(也可能是 logo / 隐喻装置 / 氛围);**别把「角度 / 卖点」误当核心想法**。**这一步不可跳过 - 是封面超过「模板套标题」的关键。**

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

#### 选风格的方法（智能选,不套默认皮）

风格 / 配色和「核心想法」一样要**主动推导**,不是拿模板的默认皮直接用。上面那张「风格 → 适用」清单是**起点不是答案**,照着题材类别机械对号最容易落进套路默认。方法:

1. **从核心想法 + 题材的「调性 / 情绪」出发,而不是题材类别机械映射。** 先问:这期是什么调性 - 冷静严谨?发布的兴奋?悬念压迫?粗粝的黑客气?温和人文?**调性决定风格,题材类别只是线索之一。**
2. **列 2-3 个候选,逐个问「它的视觉语言服务这个想法和调性吗」**,选最贴的(`design-styles.md` 有每个风格的 identity test)。拿不准就走「多方向预览」(Step 5),一次出 3-4 版让用户选。
3. **配色要主动定,别继承模板默认皮。** 每个模板 `:root` 自带一套默认配色(terminal 黑绿、aurora 紫渐变、bauhaus 红黄蓝……)—— 那是**起点不是终点**。讲具体产品优先走品牌匹配(Step 1 的 `extract-brand-theme.sh`),否则按调性主动调 `--bg` / `--accent`。
4. **品类信号独立于皮肤。** 「agent skill → 命令条、模型 → logo」给的是**元素**,不绑定某个风格 - 命令条可以放进白底编辑风,logo 可以放进任何风格。别因为「要给命令条」就反射性套 terminal 黑绿皮。

> **套路默认皮:合适就用,别反射性套。** CLI / skill 题材用 terminal 黑绿、AI 题材用 aurora 紫渐变 - 这些常规组合**本身没问题**,前提是你**真判断过它贴这期的想法和调性**。要避免的是「没思考、顺手抓题材最套路那张皮」,不是「避免常规选择」。
> **判据**:你能说出「**为什么这个风格服务这个核心想法**」,就用;只能说出「因为这题材一般都长这样」,就再想想。

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

讲模型/产品/厂商时（Claude、OpenAI、Gemini、DeepSeek、Ollama……），从 **[@lobehub/icons](https://lobehub.com/icons)** 取官方 logo 融进模板。**取图标、选变体、放置(品牌行/lockup/角标)、对比类双 logo、深底避坑、identity test 全见 `references/brand-logos.md`。**

一条判断要点留在这:**`@lobehub/icons` 只覆盖 AI / LLM 厂商。** 讲非 AI 产品（开发工具、运行时、框架、SaaS，如 Bun、Vite、Zed）时它多半没有对应图标，`fetch-brand-icon.sh` 会报 FAIL。**这时别硬拼 logo、别用网络图片（Rule 8）** - 改走**无 logo 的排版 / 品牌色识别**：产品名做大字主元素 + 品牌色 + 命令条 / 领域装置（Bun 封面就是这么做的，见 `references/cover-composition.md`）。

### Step 4 · 渲染成 PNG（每个比例一张）

**默认用脚本 `scripts/render-cover.sh`** - 它把多比例、2x retina、降采样预览、以及 headless Chrome 的所有坑（输出别用 /tmp、截图落盘时序、`--headless=new` 不自退要主动收进程、独立 profile）都封好了。一条命令搞定一期的横屏或竖屏全比例：

```bash
scripts/render-cover.sh cover.html ~/covers/<slug>            # 横屏 HTML → 自动出 16x9 + 16x10
scripts/render-cover.sh cover-v.html ~/covers/<slug> 9x16 3x4 # 竖屏显式指定比例
```

产物：`cover-<比例>.png`（2x retina，如 16:9 → 3840×2160）+ `cover-<比例>.preview.png`（≤1400px，给 Read / 验收看）。运行 `scripts/render-cover.sh` 无参看完整用法；坑的来由见 `references/render-pipeline.md`。

**交互式微调时**可改用 chrome-devtools MCP 逐张截（适合一边看一边调 CSS）：`new_page` 打开 `file://` → `resize_page` 到 `画布宽 ×（画布高 + 20）` → `navigate_page` reload → `take_screenshot` `fullPage: true`。但批量出图、最终交付一律走脚本（见 Critical Rule 10）。

### Step 5 · 验收 + 迭代

`open` 在 macOS 默认查看器里打开所有 PNG 给用户看。

**先过想法验证(见 `references/design-conception.md`)**:
- [ ] **核心想法 test at scale** - 缩到 160px,问的不是「标题读得出吗」,而是**那个核心想法还在吗**(名字认得出 / 氛围透得出 / 隐喻读得懂)?读不出 → 回 Step 1.5 换更强的表达,或做得更大、删更多。
- [ ] 主元素是不是**核心想法本身**,而不是被「角度 / 卖点」抢了位?

**再过内容传达自检（见 `references/cover-composition.md`）**:
- [ ] **三信号**都到位?逐条指认画面里哪个元素负责:**是什么**(核心想法当主角,是不是最显眼)/ **什么品类**(agent skill→命令条、模型→logo)/ **什么领域**(设计→before/after、安全→告警…)
- [ ] **品牌署名只出现一次**?(注意区分:产品名=选题主角要显眼,频道署名=低调一次。两者不算重复)
- [ ] 有没有可删的**次要 chrome**(日期 / `Ep·`胶囊 / 分隔横线 / 装饰标签)?空白处是有信息量的视觉还是纯空?
- [ ] 空白处放了**领域装置**没有?(转变类→before/after,整合类→N 个 ✕ → 一个 ✓,对比类→vs,数据类→大数字;partial 见 `templates/partials/before-after.html`)

再问视觉反馈:
- 文字位置 / 字号合不合适?
- **缩略图测试** - 缩到 ~320px / 160px 宽,主标题还读得出吗?(3 秒原则)
- **竖屏安全区 + 居中** - 9:16 / 3:4 核心文字是否在中央安全带、没贴边?短主视觉(标题/产品名)是否水平居中?(规则与例外见 `references/platform-specs.md` 竖屏安全区)
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
8. **品牌 logo 用官方来源** - 需要模型/产品/厂商 logo 时从 `@lobehub/icons` 取(见 `references/brand-logos.md` + `scripts/fetch-brand-icon.sh`),不要自行制作或随意使用网络图片;深色底别用 mono `<img>`(会变黑),用 color 变体或内联着色;对比类选题(X vs Y)双 logo 放大成标题上方 lockup,别缩成 kicker 小图标
9. **中文标题行高** - 中文大标题 line-height ≈1.05–1.10,别用拉丁 display 的 0.9(会撞行);见 `references/design-styles.md`
10. **渲染输出别用 `/tmp`** - headless 渲染输出到持久目录(`/tmp` 会被清);优先用 `scripts/render-cover.sh`,坑见 `references/render-pipeline.md`
11. **想法先行(方法论主线,最重要)** - 选模板前先按 `references/design-conception.md` 抽出**核心想法**(可能是名字/logo/隐喻/氛围,别把「角度/卖点」误当想法);全 skill 只用这一套方法论,别混入别的流派。落到画面的传达自检(三信号/署名只一次/精简 chrome)见 `references/cover-composition.md`
12. **讲具体产品时做品牌匹配** - 用产品官网真实色 + 字(`scripts/extract-brand-theme.sh` + `references/brand-theme.md`),不要一律采用默认 lime;封面气质和被介绍的产品一致更专业
13. **风格/配色要主动选,别套题材默认皮** - 按核心想法 + 题材调性推导风格(列 2-3 候选),模板自带配色是起点不是终点,品类信号(命令条/logo)不绑定某皮肤;常规选择合适就用,但要能说出「为什么这风格服务这个核心想法」(见 Step 2「选风格的方法」)
