# Brand Logos · 在封面里融入品牌 logo（@lobehub/icons）

有些封面需要带上品牌 logo - 讲某个模型 / 产品 / 厂商时（Claude、OpenAI、Gemini、DeepSeek、Ollama……），一个官方 logo 比一行文字更快建立识别。本文档说明怎么从 **[@lobehub/icons](https://lobehub.com/icons)**（200+ AI/LLM 品牌 logo 合集）取图标并融进 cover-design 的 HTML 模板。

## 来源

- 浏览全部图标：[lobehub.com/icons](https://lobehub.com/icons)
- 包：`@lobehub/icons-static-svg`（SVG）、`@lobehub/icons-static-png`（PNG，分 light/dark）
- 封面是代码渲染（HTML/CSS → 截图），**不需要装 npm**，直接用 CDN 取静态文件即可。

## 取图标的两种方式

### A. 用 helper 脚本下载到本地（推荐，离线可渲染）

```bash
scripts/fetch-brand-icon.sh <id> [variant] [format] [outdir]
```

- `<id>`：小写图标 id，如 `claude` `openai` `anthropic` `deepseek` `gemini` `ollama` `qwen` `mistral` `meta` `google`
- `variant`：`mono`(默认) | `color` | `text` | `brand` | `brand-color`
- `format`：`svg`(默认) | `png-light` | `png-dark`
- `outdir`：默认当前目录；建议放到封面 PNG 同目录的 `assets/`

```bash
# 官方配色 SVG（多色，自带品牌色）
scripts/fetch-brand-icon.sh claude color svg ./assets      # → assets/claude-color.svg

# 单色 SVG（fill=currentColor，可被 CSS 重新着色，配深底/浅底）
scripts/fetch-brand-icon.sh openai mono svg ./assets       # → assets/openai.svg
```

脚本带 CDN 回退链（unpkg → jsdelivr → npmmirror 阿里云），并在某变体不存在时自动回退到 `mono`。锁版本可 `export LOBE_ICONS_VERSION=1.91.0`。

### B. 直接引 CDN URL（联网渲染时最省事）

SVG（无 light/dark 之分）：

```
https://unpkg.com/@lobehub/icons-static-svg@latest/icons/{id}.svg
https://unpkg.com/@lobehub/icons-static-svg@latest/icons/{id}-color.svg
https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@latest/icons/{id}.svg     # jsdelivr 镜像
https://registry.npmmirror.com/@lobehub/icons-static-svg/latest/files/icons/{id}.svg  # 阿里云镜像
```

PNG（分 light/dark）：

```
https://unpkg.com/@lobehub/icons-static-png@latest/light/{id}.png
https://unpkg.com/@lobehub/icons-static-png@latest/dark/{id}.png
https://unpkg.com/@lobehub/icons-static-png@latest/light/{id}-color.png
```

> 渲染稳定性：headless 截图时外链图标偶有加载竞态。**正式封面优先用方式 A 下载到本地再内联**；快速预览可用方式 B。

## 变体怎么选

| variant | 文件名 | 用途 |
|---|---|---|
| `mono` | `{id}.svg` | 单色，`fill="currentColor"`，**内联后用 CSS `color` 重新着色**，做和封面同色系的 logo |
| `color` | `{id}-color.svg` | 官方品牌色，自带配色，直接用 |
| `text` | `{id}-text.svg` | 纯文字 logotype（厂商名） |
| `brand` / `brand-color` | `{id}-brand[-color].svg` | logo + 文字横排锁版 |

**不是每个 id 都有全部变体**：如 `openai` 没有 `-color`（只有 mono + text），`anthropic` 只有 mono + text。拿不准就先试 `color`，脚本会自动回退 `mono`。

## 融进模板的两种放法

### 放法 1：内联 SVG（首选，可着色、最清晰）

把下载的 SVG 文件内容直接贴进 HTML，外面包一个 `.brand-logo`。**mono 变体**靠父级 `color` 着色：

```html
<!-- 顶部品牌行：logo + 文字锁版 -->
<span class="brand-logo">
  <svg ...>...粘贴 {id}.svg 的内容...</svg>
</span>
```

```css
.brand-logo{
  display:inline-flex;align-items:center;
  width:1.1em;height:1.1em;          /* 跟随旁边文字字号 */
  color:var(--accent);                /* mono SVG 会染成强调色 */
}
.brand-logo svg{width:100%;height:100%;display:block;}
```

- 深色底（aurora / glass-dark / terminal / spotlight 等）：mono logo 用 `color:var(--ink)` 或 `var(--accent)`。
- 浅色底（swiss / bauhaus / editorial / brutalism）：mono logo 用近黑 `color:var(--ink)`。
- 要官方配色：换 `-color.svg`，不要再设 `color`（它自带颜色）。

### 放法 2：`<img>` 引用本地/CDN 文件（简单，但 mono 不可重新着色）

```html
<img class="brand-logo-img" src="./assets/claude-color.svg" alt="Claude" />
```

```css
.brand-logo-img{height:1.1em;width:auto;display:block;}
```

`<img>` 引 mono SVG 时 `currentColor` 会落到默认黑，**深底上会看不见** - 深底配 `<img>` 务必用 `-color` 变体或 `png-dark`。要跟随封面色系，请用放法 1 内联。

## 放在封面哪里

封面是「单焦点 + 大标题」，logo 是**辅助识别**，别喧宾夺主：

1. **顶部品牌行**（单 logo 点缀）：放在 kicker / eyebrow 旁，小尺寸（≈ kicker 字号的 1.1 倍）。各模板的品牌行 class 不同：
   - `hero-typography` / `swiss`：`.topbar` 里的 `.tag`
   - `aurora` / `glass-dark` / `terminal` / `noir-editorial` / `spotlight` / `blueprint` / `holographic`：`.top` 里的 `.kicker`
   - 把 `.brand-logo` 作为该 span 的第一个 child，`gap:.4em` 与文字分开。
2. **标题前的 lockup**：标题上方放一个中等尺寸 logo（≈ 80-120px），适合「单产品解读」。
3. **角标水印**：右上或右下角小 logo（≈ 56-72px，低透明度），适合系列内容统一标识。

尺寸建议（1920×1080 横屏画布）：品牌行 36-48px、标题 lockup 80-120px、角标 56-72px。竖屏（1080 宽）等比缩到约 0.7×，且仍要落在中央安全带内。

### 对比类选题（X vs Y）：双 logo 当主视觉，别塞进 kicker 小字行

讲「Codex vs Claude Code」「GPT vs Gemini」这类对决/对比时，**两个 logo 是内容的核心，应该放大成标题上方的 lockup**（≈ 110-130px 一个，中间夹 `VS`），而不是缩成 kicker 行里的小图标 —— 那样在 16:9 缩略图里几乎看不清，竖屏更糊（实测踩过）。

```html
<!-- 标题上方，作为 .hero 的第一个 child（在 .eyebrow 之前） -->
<div class="vs-lockup">
  <span class="blogo mono"><svg>...openai mono...</svg></span>
  <span class="vs">VS</span>
  <span class="blogo"><svg>...claude color...</svg></span>
</div>
```

```css
.vs-lockup{display:inline-flex;align-items:center;gap:34px;margin-bottom:40px;}
.vs-lockup .blogo{display:inline-flex;align-items:center;justify-content:center;
  width:128px;height:128px;background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.16);border-radius:28px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.22);}   /* 玻璃徽章托住 logo，深底/花底都清晰 */
.vs-lockup .blogo svg{width:78px;height:78px;display:block;}
.vs-lockup .blogo.mono{color:#fff;}                   /* openai 等 mono → 白 */
.vs-lockup .vs{font-family:var(--font-mono);font-weight:700;font-size:40px;color:var(--ink);}
```

竖屏把尺寸缩到约 0.85×（blogo ≈112px、VS ≈34px），仍落在安全带内。

## 不要做

- 不要把多色 logo 摆在花哨渐变/噪点正上方（holographic、aurora 的光晕区）- 垫一个底或挪到纯色区。
- 不要拉伸：`width:auto` 跟着 `height` 走，保持比例。
- 不要堆一排 logo 占满画面 - 最多 1-2 个，封面仍是大标题主导。
- 深色底别用 mono `<img>`（会变黑看不见）- 用 `-color` 或内联 + `color`。

## identity test（logo 用对了吗）

1. logo 是官方来源（@lobehub/icons），不是手搓/网图。
2. 深底/浅底对应的着色正确，logo 清晰可辨、不糊不隐。
3. logo 是辅助，标题仍是第一视觉焦点（缩到 160px 先看到标题，再看到 logo）。
4. 比例正确没有拉伸。
