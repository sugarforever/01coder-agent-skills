#!/usr/bin/env bash
# fetch-brand-icon.sh — 从 @lobehub/icons 下载品牌 logo 到本地，供封面内联使用。
#
# 来源: https://lobehub.com/icons （@lobehub/icons，200+ AI/LLM 品牌 logo）
# 用法:
#   fetch-brand-icon.sh <id> [variant] [format] [outdir]
#     <id>       图标 id（小写），如 claude / openai / anthropic / deepseek / gemini / ollama / qwen
#     [variant]  mono(默认) | color | text | brand | brand-color
#     [format]   svg(默认) | png-light | png-dark
#     [outdir]   输出目录，默认当前目录
#
# 示例:
#   fetch-brand-icon.sh claude color svg ./assets       → ./assets/claude-color.svg
#   fetch-brand-icon.sh openai mono svg .               → ./openai.svg   (fill=currentColor，可 CSS 重新着色)
#   fetch-brand-icon.sh gemini color png-dark ./assets  → ./assets/gemini-color.png
#
# 注意: 不是每个 id 都有全部变体（如 openai 没有 -color，anthropic 只有 mono + text）。
#       命中 404 会自动回退到 mono；全部失败则报错退出。
set -euo pipefail

ID="${1:?need icon id, e.g. claude}"
VARIANT="${2:-mono}"
FORMAT="${3:-svg}"
OUTDIR="${4:-.}"
VER="${LOBE_ICONS_VERSION:-latest}"   # 可 export LOBE_ICONS_VERSION=1.91.0 锁版本

mkdir -p "$OUTDIR"

# variant → 文件名后缀
suffix=""
case "$VARIANT" in
  mono|"") suffix="" ;;
  color) suffix="-color" ;;
  text) suffix="-text" ;;
  brand) suffix="-brand" ;;
  brand-color) suffix="-brand-color" ;;
  *) echo "unknown variant: $VARIANT (use mono|color|text|brand|brand-color)" >&2; exit 2 ;;
esac

# format → 包 + 路径前缀 + 扩展名
case "$FORMAT" in
  svg)      pkg="icons-static-svg"; prefix="icons";      ext="svg" ;;
  png-light)pkg="icons-static-png"; prefix="light";      ext="png" ;;
  png-dark) pkg="icons-static-png"; prefix="dark";       ext="png" ;;
  *) echo "unknown format: $FORMAT (use svg|png-light|png-dark)" >&2; exit 2 ;;
esac

fname="${ID}${suffix}.${ext}"
out="$OUTDIR/$fname"

# CDN 回退链: unpkg → jsdelivr → npmmirror(阿里云)
urls=(
  "https://unpkg.com/@lobehub/${pkg}@${VER}/${prefix}/${fname}"
  "https://cdn.jsdelivr.net/npm/@lobehub/${pkg}@${VER}/${prefix}/${fname}"
  "https://registry.npmmirror.com/@lobehub/${pkg}/${VER}/files/${prefix}/${fname}"
)

try_download() {
  local url="$1" dest="$2"
  local code
  code=$(curl -sL -A "Mozilla/5.0" -o "$dest" -w "%{http_code}" "$url" || echo 000)
  # 404 / 错误响应常返回 200 + 一个 JSON 或纯文本错误体（如 npmmirror 的 {"error":"[NOT_FOUND]"}）。
  # 按大小 + 内容校验；任何不合格的下载都删掉写坏的文件，绝不把错误响应体留在磁盘当 logo。
  if [ "$code" = "200" ] && [ -s "$dest" ]; then
    if [ "$ext" = "svg" ] && ! grep -q "<svg" "$dest"; then rm -f "$dest"; return 1; fi
    return 0
  fi
  rm -f "$dest"
  return 1
}

for url in "${urls[@]}"; do
  if try_download "$url" "$out"; then
    echo "OK  $out  ($(wc -c < "$out" | tr -d ' ') bytes)  <- $url"
    exit 0
  fi
done

# 全失败：若不是 mono，回退到 mono 再试一遍
if [ "$VARIANT" != "mono" ]; then
  echo "warn: ${VARIANT} not available for '${ID}', falling back to mono" >&2
  exec "$0" "$ID" mono "$FORMAT" "$OUTDIR"
fi

echo "FAIL  could not fetch '${ID}' (${VARIANT}/${FORMAT}) from any CDN" >&2
rm -f "$out"
exit 1
