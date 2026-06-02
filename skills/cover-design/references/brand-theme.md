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

### 输出可能有噪声，频率 ≠ 品牌（重要）
脚本是机器抓取，**出现次数最多的颜色往往不是品牌色**。常见噪声来源：
- **代码高亮主题**（Dracula / Shiki / Prism）：文档站的代码块色值，数量极多。
- **站内搜索框**（DocSearch / Algolia）、聊天件（Inkeep）的 UI 变量。
- **灰阶色阶**（gray / slate / zinc / neutral 的 50–900）。

脚本已过滤掉上面这些常见前缀，但过滤不可能完美。**最终以官网 hero / 页头肉眼确认为准** - 打开官网看背景、主按钮、强调色到底是什么，别只取脚本里频率最高的几个。

### 取不到时的处理
- 官网没有 CSS 变量、提取不到、或非 Google Fonts（自托管 woff2 / system 字体）时：取颜色 hex + 用最接近的 Google Fonts 替代；都不行时回退频道默认（lime `#7bff9f` + Manrope + Noto Sans SC）。
- 提取只是**起点**，不是照搬整站。封面仍按 `cover-composition.md` 的三信号和单焦点来组织，品牌色 / 字只是表层样式。

## 第二个例子：Bun（非 oklch、浅色品牌、自托管字体）

为避免方法只贴着 impeccable 一个例子，这里再放一个完全不同的：给 Bun（`bun.sh`，JS 运行时）做封面。

- **颜色**：`extract-brand-theme.sh https://bun.sh` 的原始输出里，Dracula 代码高亮和 DocSearch 变量数量压过品牌色（过滤后 Bun 的 `--pink-*` 色族才浮上来）。打开官网肉眼确认，真品牌是 **奶油底 `#fbf0df` + 粉 `#f472b6` / `#ec4899` + 近黑 `#0b0a08`**，hex 直接用（不是 oklch）。
- **字体**：Bun 自托管 system 字体栈，**零 Google Fonts**。按「取不到时的处理」回退模板默认字体（Archivo + Noto Sans SC + JetBrains Mono）即可。
- **风格**：浅色 + 粉 + 玩味气质 → 从 `design-styles.md` 选 `neo-brutalism`（产品 / 工具类、玩味醒目），用 Bun 的奶油+粉覆盖模板默认的黄+红。

要点：**方法一样（提取 → 过滤噪声 → 肉眼核对 → 覆盖模板 token → 按调性选风格）**，但具体值、颜色格式、字体来源都和 impeccable 不同。提取脚本的输出永远是起点，不是答案。

## 和模板的衔接

提取出的 token 覆盖模板 `:root` 的默认值：`--bg`、`--ink`、`--accent`、`--font-display`、`--font-mono`（模板约定的最小变量集，见 SKILL.md「写新模板的约定」）。风格按官网调性从 `design-styles.md` 选最接近的一个，再用品牌色覆盖其 accent / bg。
