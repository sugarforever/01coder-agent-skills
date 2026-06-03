---
name: slides-video
description: Produce slides-driven narration videos (口播视频) where each slide maps 1:1 to one voiceover section. Orchestrates `magazine-web-ppt` (PPT) and `video-planner` (script + publishing materials) with a method-focused production workflow. Use when user wants to make a video that uses slides to explain a topic - e.g. 发布解读 / 产品评测 / 行业观察 / 技术解读 / 趋势分析. Triggers on "做一期视频 + PPT", "slides 视频", "发布解读视频", "深度讲解视频", or similar requests for structured narration videos.
---

# Slides-Video · 幻灯片驱动的口播视频

制作"一张 PPT 对应一段口播"的结构化视频。本 skill 沉淀的是**制作方法和校对流程**,不是某一次的视觉风格 —— 风格由用户决定、由下游 skill 实现。

---

## Pre-flight · 依赖检查

本 skill **显式依赖**以下 skill:

| 依赖 | 作用 |
|---|---|
| `magazine-web-ppt` | 生成单文件 HTML 横向翻页 PPT · 负责所有视觉风格 |
| `video-planner` | 生成 script.md / youtube.md / bilibili.md / x.md 等脚本与发布素材 |

使用前先确认这两个可调用。**任一不可用立即告知用户并停止** —— 不要自己重写 PPT / 脚本生成逻辑(那样会失去与生态的一致性)。

建议并行调用 `personal-chinese-writing-style` 确保语言风格跟作者一致。

---

## 适用场景

**适合** —— 任何需要用 slides 搭配口播讲解的视频:
- 发布解读(新模型、新产品、新版本)
- 产品评测 / 技术讲解
- 论文 / 报告 / 行业数据拆解
- 多主体横向对比
- 趋势观察 / 现象评论

**不适合** —— 纯教程(用通用 `video-planner` 够了)· 纯屏幕演示(slides 不是主体)· 短视频 / Shorts。

---

## 核心原则 · 本 skill 的方法学

这 4 条是贯穿整个工作流的方法原则。**不涉及具体风格**,只规定**做事的方式**。

### 1. PPT-脚本 1:1 同步

**每张 PPT 页 = 一段脚本**。录视频时翻页 = 切段。

- 脚本每段开头有切页标记:`【PPT 切到 Slide N · 页名】`
- 视频总时长 ≈ 页数 × 平均每页 30-50 秒
- 页数预算参考:
  - 5-6 分钟 → 约 9 页
  - 7-8 分钟 → 约 13-15 页
  - 3-4 分钟 → 约 6-7 页

这个 1:1 约束是本 skill 相对通用 `video-planner` 的核心增量,不可妥协。

### 2. 语言面向目标受众,而非内部专家

无论受众是 AI 爱好者、开发者还是普通用户:

- **首次出现的术语必须用人话解释一句**,不能裸用 jargon
- 用 **类比 / 比喻** 替代抽象名词(让观众能在头脑里形成图像)
- **每段结尾点出"对受众意味着什么"** —— 把技术点翻译成受众能感受到的场景 / 价值
- **数字要带参照系** —— 不要堆"30%"、"1.6T"这类裸数,给参照("相当于 X"、"比上代 Y 倍")

谁是受众在 Step 1 跟用户对齐。不同受众,解释深度和比喻选择不同。

### 3. 叙事框架二选一

开工前必须决定:

- **单主角** —— 深度拆一个话题/产品 · 页面呈线性展开
- **多主角** —— 多个话题/产品同框对比 · 页面按"每主角独立幕"组织

这决定页面结构。不要含糊开写,中途很难改。

### 4. 生成后必做 QA 审核

PPT 生成完必须验证:
- 每页内容**不溢出** foot 区域(overflow audit)
- 语言风格 / 术语密度 / 用户视角落脚是否到位(语言复审)

详见 `references/overflow-audit.md`。

**修复原则 —— 改内容,不改模板**。模板是 `magazine-web-ppt` 的维护范围,本 skill 不动它的 CSS。

---

## 工作流程

每一步都指向 `references/` 里对应的方法指引。

### Step 1 · 需求澄清

问用户(已给的跳过):

1. **主题** —— 讲什么?(必填)
2. **叙事框架** —— 单主角 vs 多主角?(默认:单主角)
3. **目标时长** —— 大约几分钟?(默认 7-8 分钟)
4. **目标受众** —— AI 爱好者 / 开发者 / 普通用户 / ...?(默认:AI 爱好者)
5. **参考资料** —— 推文 / 论文 / 博客 / 源码仓库?
6. **视觉风格** —— 是否继承某个已有项目的风格?(给 URL / 项目路径) · 还是全新开始?

第 6 条很关键 —— **本 skill 不规定风格**,风格由用户在这里指定。继承已有项目的话,在 Step 5 把相应配置原样传给 `magazine-web-ppt`。

### Step 2 · 资料研究

详见 `references/research-method.md`。核心:
- 用 `WebFetch` / `WebSearch` 拉推文、公告、报道
- 用 `Read` 读论文 PDF(支持 `pages` 参数提取特定页)
- 用 `Explore` agent / `Grep` / `Glob` 摸代码仓库
- **关键数据带来源记录** —— 每个跑分 / 价格 / 日期记下出处,方便 foot 行引用

### Step 3 · 规划结构

详见 `references/planning.md`。**先画页面节奏表、跟用户确认,再动笔**。

规划产物:N 页 × 每页主题 + 主题 class(light/dark/hero light/hero dark) 的表格。

### Step 4 · 创建输出目录

按项目惯例建:

```
{output-dir}/{YYYYMMDD}-{slug}/
├── ppt/
│   ├── index.html         # 由 magazine-web-ppt 生成
│   └── images/            # (可选)插图
├── script.md              # 由 video-planner 生成,本 skill 加 1:1 标记
├── youtube.md
├── bilibili.md
└── x.md
```

### Step 5 · 调用 `magazine-web-ppt` 生成 PPT

用 `Skill` 工具调用,传入 Step 1 和 Step 3 收集到的配置:

- 主题色(用户指定 / 继承参考项目)
- 页面节奏表
- 内容(按 Step 3 规划 + Step 2 研究)

**本 skill 不规定主题色、不规定封面 / masthead 样式** —— 这些由用户选择和 `magazine-web-ppt` 负责实现。

### Step 6 · 调用 `video-planner` 生成脚本 + 发布素材

用 `Skill` 工具调用,并应用本 skill 的方法增强:

- 在 script.md 每段开头加切页标记 `【PPT 切到 Slide N · 页名】`
- 在 script.md 顶部加 PPT 同步说明注释
- 每段结尾落到"对受众意味着什么"
- 其他细节见 `references/script-method.md`

发布素材(youtube/bilibili/x)的详细约定见 `references/publishing-method.md`。

### Step 7 · QA 审核

详见 `references/overflow-audit.md`。

两类审核:
- **overflow 审核** —— 用 chrome-devtools MCP 跑 JS 扫每页,≤ 5px 才算过
- **语言复审** —— 通读 script + PPT,检查术语密度、用户视角、比喻合理性

### Step 8 · 迭代

用户反馈后的调整:
- 修改都用 Edit tool(surgical edit),不整文件 rewrite,方便用户看清每次改动
- 内容改写优先,模板不动
- 迭代后重新跑 Step 7 的 overflow 审核

### Step 9 · 完成报告

简短清单:
```
视频制作完成,产物在 {目录}:
├── ppt/index.html         — N 页 PPT(全部 0 overflow)
├── script.md              — N 段口播(带切页标记)
├── youtube.md / bilibili.md / x.md — 发布素材

PPT 已在浏览器打开,可以开始录制。
```

---

## 工程注意事项

### 风格选择交给用户

本 skill 的原则是 **方法固定 · 风格开放**:
- 主题色、品牌名、masthead 文案、封面设计 —— 都由用户在 Step 1 决定或继承参考项目
- 本 skill 不规定具体视觉方案

如果用户想沿用之前某期视频的风格,在 Step 5 把该项目的 PPT 配置传给 `magazine-web-ppt`(主题色、封面结构、品牌元素等)。

### 不要自动发布

只生成文件,**不调用任何发布 API**。用户手动发布。

### 复用个人推广信息

`video-planner` 会从 auto memory 的 `video-promo.md` 读取作者的固定推广块。本 skill 信任这个机制,不重新发明。

### 文件夹命名

统一 `{YYYYMMDD}-{slug}` 格式。日期默认取**视频制作/发布日**(不是产品发布日),除非用户指定。

---

## Examples

已有的产出可以作为参考,但**不应视为必须复制的风格** —— 下次的视频可以保留同一套风格(作为系列),也可以完全另起一套视觉:

- **单主角深度版参考** —— `src/content/videos/20260424-deepseek-v4/`
- **多主角对比版参考** —— `src/content/videos/20260424-frontier-releases/`

参考它们的 **结构方法**(页面节奏、1:1 同步、用户视角落脚、overflow 控制),而非**具体视觉**(主题色、品牌名、masthead 文案)。

---

## Critical Rules

1. **显式调用两个依赖 skill** —— 不自己重写 PPT / 脚本生成逻辑
2. **先规划后动手** —— Step 3 的页面节奏表必须跟用户确认
3. **1:1 同步不妥协** —— 每张 PPT 对应一段脚本,每段脚本开头带切页标记
4. **每段必须有受众视角** —— 技术点必须翻译成受众能感受的价值
5. **术语首次出现必解释** —— 不假设受众懂
6. **风格由用户决定** —— 本 skill 不钉死主题色 / 品牌名 / 具体页面设计
7. **PPT 生成后必须 QA 审核** —— overflow ≤ 5px 才算完
8. **修内容,不改模板** —— overflow / 术语问题通过改内容解决,不改 CSS
9. **不自动发布** —— 只产文件,用户手动发
