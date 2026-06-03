---
name: video-planner
description: Plan videos and prepare publishing materials for YouTubers/UP主. Use when user wants to plan a video, write a script (口播稿) with on-screen / screen-share cues, generate video title, description, tags, or YouTube chapter timestamps. Triggers on "策划视频", "写视频脚本", "视频口播稿", "video planner", "video script", "prepare video", "视频发布素材", or mentions creating content for YouTube/Bilibili.
---

# Video Planner & Publishing Materials

Help YouTubers/UP主 prepare video content: write structured scripts (口播稿), blog posts, platform-specific publishing materials, and an X (Twitter) promo tweet.

## Output Structure

Each video gets a date-based directory under user's chosen location:

```
./videos/{YYYY-MM-DD}-{short-slug}/
├── script.md       # 视频口播稿
├── blog.md         # 博客文章
├── youtube.md      # YouTube 发布素材
├── bilibili.md     # Bilibili 发布素材
├── x.md            # X (Twitter) 推广文案
├── fact-check.md   # 技术事实审核表（技术类视频必出，见 Step 8）
└── cover.png       # 封面（可选，见 Step 10）
```

## Interactive Workflow

### Step 1: Gather Information

**IMPORTANT**: Before writing anything, collect sufficient context from the user. Ask the user:

```
请提供以下信息，帮我为你准备视频内容：

1. **视频主题**：这期视频讲什么？（必填）
2. **目标平台**：YouTube / Bilibili / 两者都有？（默认：两者）
3. **目标时长**：大约几分钟？（默认：10分钟）
4. **目标观众**：面向什么人群？（如：开发者、AI爱好者、初学者）
5. **关键要点**：你希望视频覆盖哪些要点？（可以是大纲、笔记、或链接）
6. **相关资料**：有没有参考文章、文档、代码仓库？（可选，我可以帮你研究）
已有部分信息的话，直接告诉我就好，缺的我会追问。
```

If the user provides partial info upfront, only ask for the missing pieces.

### Step 2: Research (If Needed)

If the user provides reference URLs, docs, or repos:
- Use WebFetch to read reference articles/docs
- Use Read/Grep/Glob to explore code repos
- Use WebSearch to find supplementary information
- Summarize key points for script use

If the topic is about a specific technology/tool:
- Research its core features and selling points
- Find common pain points it solves
- Look for comparison angles with alternatives

### Step 3: Create Directory

Create the date-based directory:

```
./videos/{YYYY-MM-DD}-{short-slug}/
```

Example: `./videos/2026-03-07-react-server-components/`

The `short-slug` should be a brief, descriptive kebab-case label derived from the topic.

### Step 4: Write Script (script.md)

Write a structured 口播稿 in the user's preferred language. The script is what the user **reads aloud while recording**, so two things matter as much as the content:

- **照着念友好（read-aloud first）**：每一句都要是「能顺口念出来」的话，不是写出来给人读的文章。太书面、太像技术文档的句子会拖慢录制 - 写完后过一遍，把长定语、术语堆砌、嵌套从句改成短句口语（详见 `references/script-guidelines.md` 的「照着念友好」规则）。
- **屏上呈现推荐（screen-share cues）**：作为 AI，你要**逐段智能判断**这段口播配什么画面最好 - 某个网页的某一段、某个应用 / 终端界面、一段代码、还是一张对比 / 速查卡 - 并写成 `（屏幕：……）` 备注。目的：用户照着口播稿念的同时，一眼知道该在屏幕上呈现什么。在脚本开头加一张「屏上呈现总则」总表（画面来源 + 逐段映射），正文每段再用内联 `（屏幕：……）` 落到具体内容。不是每段都要切画面 - 判断「需不需要」也是你的工作，纯口播段就标「纯口播」。

参考：

- `templates/script.md` - 输出格式模板（含「屏上呈现总则」表与内联屏幕备注）
- `references/script-guidelines.md` - 详细写作规则（含「照着念友好」「屏上呈现推荐」两条）
- `references/examples-tutorial.md` - 教程 / 配置类标准范本，**配置 / how-to / setup 类视频开写前先读**

### Step 5: Write Blog Post (blog.md)

Repurpose the video content into a blog post to maximize content utilization. The blog should NOT be a transcript - it should be a standalone article that reads naturally.

- See `templates/blog.md` for the output format template
- See `references/blog-guidelines.md` for detailed writing rules
- **IMPORTANT**: Follow the `personal-chinese-writing-style` skill conventions

### Step 6: Write Platform Descriptions (youtube.md & bilibili.md)

Generate separate publishing materials for each platform. The two platforms share the same core content but differ in structure and promo placement.

- See `templates/youtube.md` and `templates/bilibili.md` for output format templates
- See `references/platform-differences.md` for platform-specific rules and guidelines
- **YouTube 章节**：YouTube 描述里放章节时间戳（从 `00:00` 开始，按脚本结构估算），列表上方先放一行免责声明「时间戳为按脚本结构的估算，剪辑完成后按实际时长调整」。Bilibili 描述不放章节。
- **参考资料块**：含外部链接（repo / 官网 / 文档）的视频，在 YouTube 描述末尾附一个「参考资料」块，列出链接，以及封面源文件路径（`cover.html` / `cover.png`）便于复用。

### Step 7: Write X/Twitter Promo (x.md)

Generate a short promo tweet that the user can post alongside the video to drive traffic. Not a summary — a hook that makes people want to watch.

- See `templates/x.md` for the output format template
- **IMPORTANT**: Follow `personal-chinese-writing-style` skill's `references/social-media-style.md` rules (link position, bullet vs prose, tone)
- Leave `[视频链接]` as a placeholder — user fills in the real URL on publish

### Step 8: Fact Audit (技术事实审核)

**技术解读 / 评测 / 任何含技术事实点的视频必做，不可跳过。** 在风格校对之前先把内容核实一遍 - 因为审核可能要删改成段内容。

- **逐条核验**：把 `script.md` 和 `blog.md` 里的每一条技术陈述列出来，标来源、给核验结论。规则与来源分级见 `references/fact-audit.md`
- **结论三档**：✅ 成立（有官方来源，可直接讲）/ ⚠️ 需屏上引用（非官方来源，保留但录制时屏上给可见证据）/ ❌ 删除（无来源或属推断，从脚本和博客移除）
- **绝不让模型的猜测 / 幻觉进稿**：没有来源支撑的推断一律删，或改成「官方没披露，不猜」
- **闭源 / research preview 内容**：脚本里要有披露句（「研究预览，部分细节未公开」）和边界句（「未披露的实现不猜」）；启用机制（环境变量 / 命令 / 菜单）对照当前官方文档核对；争议数字默认取官方
- **产物**：把核验结果写成 `fact-check.md` 放进视频目录，便于复核追溯。格式见 `templates/fact-check.md`

### Step 9: Apply personal-chinese-writing-style (统一风格校对)

After every file is written and fact-audited, run a dedicated polish pass over **all** generated Chinese text files. This is a required finishing step, not optional.

- **Invoke the `personal-chinese-writing-style` skill** and apply it to every generated file: `script.md`, `blog.md`, `youtube.md`, `bilibili.md`, `x.md`
- **口播稿不例外**：`script.md` 虽然是用来「说」的，也要完整套用标点与风格规则 — 中文弯引号、半角破折号 " - "、ASCII 省略号 "......"、无标题编号、简洁标题，且不留全角/英文标点
- **额外做一遍「照着念」复核**（口播稿专属，standalone-style 之外）：标点统一不等于好念。再过一遍 `script.md`，确保每句都顺口 - 把太书面 / 太技术文档化的句子（长定语、术语堆砌、嵌套从句、被动腔）改成短句口语；可以默念一遍，卡壳的地方就改。判断标准见 `references/script-guidelines.md` 的「照着念友好」。`（屏幕：……）` 屏上备注保留，不要被风格校对删掉。
- **保留口语化与自然语流**：personal-chinese-writing-style 只做标点与语气的统一，不强加模板结构（不要把 script.md 改成 Hook/引言/正文/CTA 那种套路）
- `x.md` 仍以 personal-chinese-writing-style 的 `references/social-media-style.md` 为准（链接位置、bullet vs prose、语气）

### Step 10: Generate Cover (封面，可选)

封面不是默认产物 - **先问用户要不要做封面**，需要时再生成。

询问：

```
要不要顺手做一张封面？
- 视频缩略图（YouTube / Bilibili）→ 我用 `cover-design`（代码驱动的排版封面，文字清晰、适合缩略图）
- 文章头图（博客 / X Article）→ 我用 `cover-image`（AI 生成的插画风头图）
```

- 缩略图类需求 → 调用 `cover-design` skill
- 文章头图类需求 → 调用 `cover-image` skill
- 产物存进视频目录（如 `cover.html` / `cover.png`）

### Step 11: Review & Iterate

完成后提示用户：

```
视频脚本和配套内容已准备好：

📂 {目录路径}/
├── script.md      — 口播稿（约 X 分钟）
├── blog.md        — 博客文章
├── youtube.md     — YouTube 发布素材
├── bilibili.md    — Bilibili 发布素材
├── x.md           — X (Twitter) 推广文案
├── fact-check.md  — 技术事实审核表（技术类视频）
└── cover.png      — 封面（如已生成）

请检查内容，如果需要调整，告诉我：
- 需要修改哪个部分？
- 风格/语气需要调整吗？
- 有要补充的要点吗？
```

## Personal Promotion Info

Users should configure their promotion block. On first use, ask the user for their promotion links and save to **auto memory** for cross-session persistence.

When asking:

```
我注意到这是你第一次使用视频策划 skill。请提供你的个人推广信息，我会记住以便后续使用：

- 社交媒体链接（Twitter、Bilibili、YouTube 等）
- 知识星球/社群链接
- 联系方式
- 其他固定推广信息（如课程链接、赞助信息等）
```

Save to auto memory directory as `video-promo.md` (e.g. `~/.claude/projects/.../memory/video-promo.md`). On subsequent uses, check if this file exists in the memory directory and read it directly — no need to ask again.

## Examples

See `references/examples.md` for detailed examples of different usage scenarios.

## Critical Rules

1. **先问后写** — 信息不足时必须追问，不要猜测用户意图
2. **照着念友好** — 口播稿是作者照着念的，每句都要顺口；太书面 / 太技术文档化的句子必须改成短句口语（见 Step 4、Step 9 与 `references/script-guidelines.md` 的「照着念友好」）
3. **屏上呈现推荐** — 逐段智能判断这段口播配什么画面（网页某段 / 应用 / 终端 / 代码 / 对比卡），写成内联 `（屏幕：……）` 备注，并在脚本开头给一张「屏上呈现总则」总表；纯口播段标「纯口播」（见 Step 4）
4. **脚本不加时间戳；章节只在 YouTube 描述** — `script.md` 章节标题不标时间戳（节奏由作者录制时掌控）；YouTube 描述放估算章节时间戳（从 `00:00` 起）并在列表上方加免责声明（剪辑后按实际时长调整）；Bilibili 描述不放章节
5. **不要自动发布** — 只生成文件，不执行任何发布操作
6. **保留用户风格** — 如果用户提供了之前的视频风格参考，尽量保持一致
7. **推广信息复用** — 首次询问后保存到 auto memory，后续自动填充
8. **日期目录** — 每期视频按当天日期创建独立目录
9. **技术内容先审后发** — 技术解读/评测等含技术事实的视频，发布前必须逐条事实审核（见 Step 8），无官方来源的点要么删、要么屏上给可见引用，绝不让模型的猜测/幻觉进稿，并出 `fact-check.md` 留档
10. **统一风格收尾** — 所有生成的中文文稿（含口播稿）在收尾时必须用 `personal-chinese-writing-style` 过一遍，见 Step 9，不可跳过
11. **封面按需生成** — 封面不是默认产物，先问用户；缩略图用 `cover-design`，文章头图用 `cover-image`（见 Step 10）
