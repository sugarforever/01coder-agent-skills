# Brand Theme · 从产品官网提取真实品牌色 + 字体

当选题是**某个具体产品 / 工具 / 开源项目**（impeccable、某 SaaS、某框架）时，封面采用**产品自己的品牌色和字体**，比采用频道默认 lime + Manrope 更贴合产品 - 封面气质和被介绍的东西一致。

这份和 `brand-logos.md`（取 logo）互补：logo + 色 + 字 配齐一整套品牌匹配。

> 来源：impeccable 选题实战。从 impeccable.style 提取出它的「漆器 + 金箔（kinpaku）」oklch 色板和 Cormorant / Alumni / Albert 字体族，应用后封面质感明显优于默认模板。

## 一键提取

```bash
scripts/extract-brand-theme.sh https://impeccable.style
```

输出一份**可直接写入模板 `:root`** 的 token 清单：Google Fonts 链接、字体 family 列表、颜色变量（含 oklch / hex）。

## 手动步骤（脚本背后的三步）

```bash
# 1) 抓官网 HTML
curl -sL https://impeccable.style/ -o /tmp/site.html

# 2) 字体：Google Fonts 链接 + family 列表
rg -oiP 'fonts\.googleapis\.com/css2\?family=[^"'\'' )]+' /tmp/site.html

# 3) 颜色：先找链接的 CSS，再从中提取颜色变量（hex / oklch / 语义品牌变量名）
for css in $(rg -oP 'href="\K/[^"]+\.css' /tmp/site.html); do
  curl -sL "https://impeccable.style$css"
done | rg -oiP '\-\-[a-z0-9-]+:\s*(oklch\([^)]+\)|#[0-9a-f]{3,8})' | sort -u
```

## 要点

### 颜色
- **直接使用 `oklch()` 原值**。headless Chrome（111+）原生支持 `oklch()`，把官网色值**原样**写入模板 `:root`，比手动转 hex 更忠实、更省事。
  - 例（impeccable）：金箔 `--kinpaku: oklch(84% .19 80.46)`、漆黑底 `--lacquer: oklch(7% .006 95)`、香槟字 `oklch(91% 0 0)`、铜绿 patina `oklch(70% .12 188)`。
- 现代站点常把颜色定义**两套**（light / dark 主题）。选与封面底色一致的那套（深色封面取 dark 变体）。
- **语义变量名能反推品牌调性** - `kinpaku`（金箔）、`lacquer`（漆器）、`champagne`（香槟）指向日式漆器美学，对应 `noir-editorial` / `editorial` 这类暖金暗调风格最匹配。变量名是判断品牌想表达什么的线索。
- 取主色（accent）+ 底色（bg）+ 文字色（ink）+ 一两个辅助色即可，不必把整套色板都写进去。

### 字体
- 把官网字体按**封面三个角色**映射：display（标题）/ body（副标）/ mono（标签）。
  - 例（impeccable）：display 衬线 Cormorant Garamond、wordmark Alumni Sans、body Albert Sans、mono Roboto / JetBrains Mono。
- **中文标题**：拉丁品牌字体渲染不了中文。选一款气质接近的中文字体搭配：
  - 官网用衬线（Cormorant / 宋体感）→ 中文用 `Noto Serif SC`
  - 官网用无衬线 grotesk → 中文用 `Noto Sans SC`
  - 拉丁数字 / 字母（如「33.3k」「AI」）可单独用品牌的拉丁 display 字体，和中文混排出层次（impeccable 封面「祛 *AI* 味」的 AI 用 Cormorant 斜体金箔）。
- Google Fonts 链接直接沿用官网那条（已含所有 weight），再补 `Noto Serif SC` / `Noto Sans SC`。

### 取不到时的处理
- 官网没有 CSS 变量、提取不到、或非 Google Fonts（自托管 woff2）时：取颜色 hex + 用最接近的 Google Fonts 替代；都不行时回退频道默认（lime `#7bff9f` + Manrope + Noto Sans SC）。
- 提取只是**起点**，不是照搬整站。封面仍按 `cover-composition.md` 的三信号和单焦点来组织，品牌色 / 字只是表层样式。

## 和模板的衔接

提取出的 token 覆盖模板 `:root` 的默认值：`--bg`、`--ink`、`--accent`、`--font-display`、`--font-mono`（模板约定的最小变量集，见 SKILL.md「写新模板的约定」）。风格按官网调性从 `design-styles.md` 选最接近的一个，再用品牌色覆盖其 accent / bg。
