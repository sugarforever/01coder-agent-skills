# Brand Theme · 从产品官网提取真实品牌色 + 字体

当选题是**某个具体产品 / 工具 / 开源项目**（impeccable、某 SaaS、某框架）时，封面套**产品自己的品牌色和字体**，比套频道默认 lime + Manrope 更专业、更原生 - 封面气质和被介绍的东西一致。

这份和 `brand-logos.md`（取 logo）互补：logo + 色 + 字 凑齐一整套品牌匹配。

> 来源：impeccable 选题实战。从 impeccable.style 扒出它的「漆器 + 金箔（kinpaku）」oklch 色板和 Cormorant/Alumni/Albert 字体族，套上去后封面质感明显超过默认模板。

## 一键提取

```bash
scripts/extract-brand-theme.sh https://impeccable.style
```

输出一份**可直接抄进模板 `:root`** 的 token 清单：Google Fonts 链接、字体分工候选、颜色变量（含 oklch / hex）。

## 手动配方（脚本背后的三步）

```bash
# 1) 抓官网 HTML
curl -sL https://impeccable.style/ -o /tmp/site.html

# 2) 字体：Google Fonts 链接 + family 列表
rg -oiP 'fonts\.googleapis\.com/css2\?family=[^"'\'' )]+' /tmp/site.html

# 3) 颜色：先找链接的 CSS，再从中扒颜色变量（hex / oklch / 语义品牌变量名）
for css in $(rg -oP 'href="\K/[^"]+\.css' /tmp/site.html); do
  curl -sL "https://impeccable.style$css"
done | rg -oiP '\-\-[a-z0-9-]+:\s*(oklch\([^)]+\)|#[0-9a-f]{3,8})' | sort -u
```

## 要点 / 避坑

### 颜色
- **直接用 `oklch()` 原值**。headless Chrome（111+）原生支持 `oklch()`，把官网色值**原样**搬进模板 `:root` 比手动转 hex 更忠实、更省事。
  - 例（impeccable）：金箔 `--kinpaku: oklch(84% .19 80.46)`、漆黑底 `--lacquer: oklch(7% .006 95)`、香槟字 `oklch(91% 0 0)`、铜绿 patina `oklch(70% .12 188)`。
- 现代站点常把颜色定义**两套**（light / dark 主题）。挑和你封面底色一致的那套（深色封面取 dark 变体）。
- **语义变量名能反推品牌调性** - `kinpaku`(金箔)、`lacquer`(漆器)、`champagne`(香槟) → 日式漆器美学 → 选 `noir-editorial`/`editorial` 这类暖金暗调风格最搭。变量名是免费的「这品牌想表达什么」线索。
- 取主色（accent）+ 底色（bg）+ 文字色（ink）+ 1-2 个辅助色就够，别把整套色板都搬上去。

### 字体
- 把官网字体按**封面三角色**映射：display（标题）/ body（副标）/ mono（标签）。
  - 例（impeccable）：display 衬线 Cormorant Garamond、wordmark Alumni Sans、body Albert Sans、mono Roboto/JetBrains Mono。
- **中文标题**：拉丁品牌字渲不了中文。挑一支**同气质**的中文字配对：
  - 官网用衬线（Cormorant / 宋体感）→ 中文用 `Noto Serif SC`
  - 官网用无衬线 grotesk → 中文用 `Noto Sans SC`
  - 拉丁数字/字母（如「33.3k」「AI」）可单独用品牌的拉丁 display 字，和中文混排出层次（impeccable 封面「祛 *AI* 味」的 AI 用 Cormorant 斜体金箔）。
- Google Fonts 链接直接抄官网那条（已含所有 weight），自己再补 `Noto Serif SC` / `Noto Sans SC`。

### 兜底
- 官网没有 CSS 变量、取不到、或非 Google Fonts（自托管 woff2）时：取颜色 hex + 用最接近的 Google Fonts 替代；实在不行回退频道默认（lime `#7bff9f` + Manrope + Noto Sans SC）。
- 提取只是**起点**，不是照搬整站。封面是封面，仍按 `cover-composition.md` 的三信号和单焦点来组织，品牌色/字只是皮肤。

## 和模板的衔接

提取出的 token 覆盖模板 `:root` 的默认值：`--bg`、`--ink`、`--accent`、`--font-display`、`--font-mono`（模板约定的最小变量集，见 SKILL.md「写新模板的约定」）。风格按官网调性从 `design-styles.md` 选最接近的一个，再用品牌色覆盖其 accent/bg。
