#!/usr/bin/env bash
# extract-brand-theme.sh — 从产品官网提取品牌色 + 字体，供封面做「品牌匹配」。
#
# 当选题是某个具体产品/工具/开源项目时，用它官网自己的品牌色和字体做封面，
# 比套频道默认 lime + Manrope 更原生。配方与避坑见 references/brand-theme.md。
#
# 用法:
#   extract-brand-theme.sh <url>
#     <url>  产品官网首页，如 https://impeccable.style
#
# 输出（stdout，可直接写入模板 :root）:
#   - Google Fonts 链接 + 解析出的 family 列表（按 display/body/mono 自己分工）
#   - 颜色变量与字面量（含 oklch 原值，可原样写入 Chrome）
#   - 语义化品牌变量名（反推调性，如 kinpaku/lacquer → 日式漆器暖金）
#
# 依赖: curl + rg(ripgrep)。
set -uo pipefail   # 不开 -e：单个 css 取不到不应中断整体

URL="${1:?need a url, e.g. https://impeccable.style}"
command -v rg  >/dev/null 2>&1 || { echo "need ripgrep (rg)" >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "need curl" >&2; exit 1; }

# origin = scheme://host（用于补全相对 css 路径）
ORIGIN="$(printf '%s' "$URL" | sed -E 's#^(https?://[^/]+).*#\1#')"

TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
curl -sL --max-time 25 "$URL" -o "$TMP" || { echo "fetch failed: $URL" >&2; exit 1; }
[ -s "$TMP" ] || { echo "empty response: $URL" >&2; exit 1; }

echo "# Brand theme extracted from: $URL"
echo "# origin: $ORIGIN"
echo

echo "## Google Fonts 链接（直接写入 <head>）"
rg -oiP 'https://fonts\.googleapis\.com/css2\?family=[^"'\'' )]+' "$TMP" | sort -u
echo
echo "## 字体 family（自己按 display / body / mono 分工，中文另配 Noto Serif/Sans SC）"
rg -oiP 'family=\K[A-Za-z0-9+]+' "$TMP" | sed 's/+/ /g' | sort -u
echo

# 收集所有 CSS：内联 <style> + 链接的样式表
CSSALL="$(mktemp)"; trap 'rm -f "$TMP" "$CSSALL"' EXIT
cat "$TMP" >> "$CSSALL"   # 内联 style / CSS-in-HTML 也一并纳入
# 链接的样式表（相对 / 绝对 / 协议相对）
while IFS= read -r href; do
  case "$href" in
    http*)  url="$href" ;;
    //*)    url="https:$href" ;;
    /*)     url="$ORIGIN$href" ;;
    *)      url="$ORIGIN/$href" ;;
  esac
  curl -sL --max-time 20 "$url" >> "$CSSALL" 2>/dev/null || true
done < <(rg -oiP '<link[^>]+rel="stylesheet"[^>]+href="\K[^"]+|href="\K[^"]+\.css[^"]*' "$TMP" | sort -u)

# 噪声来源：站点搜索框(DocSearch/Algolia)、代码高亮主题(Dracula/Shiki/Prism/highlight.js)、
# 文档框架(Docusaurus --ifm-*)、灰阶色阶(gray/slate/zinc/neutral/stone)。这些常压过真正的品牌色。
NOISE='docsearch|algolia|inkeep|--ifm|shiki|prism|hljs|highlight|token|gray|grey|slate|zinc|neutral|stone'

echo "## 颜色：品牌相关的 CSS 变量（已过滤搜索框 / 代码高亮 / 灰阶噪声）"
rg -oiP '\-\-[a-z0-9-]+:\s*(oklch\([^)]+\)|#[0-9a-f]{3,8}\b)' "$CSSALL" 2>/dev/null \
  | rg -ivP "$NOISE" | sort -u | head -50
echo
echo "## ⚠️  频率最高 ≠ 品牌色。机器抓取仍可能混入噪声（代码高亮、搜索框、灰阶）。"
echo "##     真正的品牌色以官网 hero / 页头实际呈现为准 - 打开官网，肉眼确认背景、主按钮、强调色，"
echo "##     不要只取这里出现次数最多的几个。"
echo
echo "## 颜色：裸字面量（噪声更多，仅在上面变量没取到时参考）"
rg -oiP '(oklch\([^)]+\)|#[0-9a-f]{6}\b)' "$CSSALL" 2>/dev/null | rg -ivP "$NOISE" | sort -u | head -30
echo
echo "## 语义品牌变量名（反推调性 - 如 kinpaku/lacquer 暗示暖金漆器；docsearch/gray 等噪声已过滤）"
rg -oiP '\-\-[a-z]+(?:-[a-z0-9]+)*(?=:\s*(oklch|#|rgb))' "$CSSALL" 2>/dev/null \
  | rg -ivP '^--(color|bg|fg|ink|text|border|card|cat|demo|font|space|size|radius|shadow|gap|width|height|x|y|c)$' \
  | rg -ivP "$NOISE" | sort -u | head -40

echo
echo "# 下一步：选 accent/bg/ink + display/body/mono，覆盖模板 :root；风格按调性从 design-styles.md 选。"
echo "# 拿不准就打开官网肉眼对一遍（频率≠品牌）。无 Google Fonts（自托管 system 字体）时回退模板默认字体。"
echo "# 详见 references/brand-theme.md"
