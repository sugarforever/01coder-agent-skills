#!/usr/bin/env bash
# render-cover.sh — 把定制好的封面 HTML 渲染成多比例 2x PNG，并各生成一张可 Read 的小图预览。
#
# 这是 headless Chrome 回退管线的「打包版」，把本仓库遇到过的问题都内置了：
#   - 用字面 ratio 列表，不靠 shell 变量分词（zsh 不会对 $VAR 分词，老 bug）
#   - 输出到调用方给的持久目录，绝不用 /tmp（会被清）
#   - 渲染与降采样分两段：先确认 PNG 落地（有界轮询，因为 headless Chrome 常在
#     截图落盘前就让 wait 返回），再 sips 缩图
#   - 每个渲染用独立 --user-data-dir，跑完 pkill 收尾，避免 SingletonLock / 不退出
#   - 预览图缩到 <2000px，方便 Read 工具直接看（验收用）
#
# 用法:
#   render-cover.sh <html> <outdir> [ratios...]
#     <html>     定制好的封面 HTML（占位符已替换）
#     <outdir>   输出目录（持久路径，如 ~/covers/<slug>）
#     [ratios]   要出的比例，缺省按 HTML 朝向自动选：
#                  横屏 (--cv-w:1920) → 16x9 16x10
#                  竖屏 (--cv-w:1080) → 9x16 3x4
#                可选值: 16x9 16x10 9x16 3x4
#
# 例:
#   render-cover.sh cover-h.html ~/covers/demo            # 横屏自动出 16x9 + 16x10
#   render-cover.sh cover-v.html ~/covers/demo 9x16       # 只出 9:16
#   render-cover.sh cover-h.html ~/covers/demo 16x9 16x10 # 显式
#
# 产物（outdir 内）:
#   cover-<ratio>.png         2x retina 成品（如 16x9 → 3840×2160）
#   cover-<ratio>.preview.png 缩到 ≤1400px 的预览（给 Read 看，验收后可删）
set -uo pipefail   # 注意：不开 -e，渲染/缩图的零星非零退出码不应中断整批

HTML="${1:?need html path}"
OUTDIR="${2:?need output dir (use a persistent path, NOT /tmp)}"
shift 2
RATIOS=("$@")

CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -f "$HTML" ] || { echo "no such html: $HTML" >&2; exit 1; }
[ -x "$CHROME" ] || { echo "Chrome not found at: $CHROME (set \$CHROME)" >&2; exit 1; }
mkdir -p "$OUTDIR"
# 绝对化 OUTDIR：下面用 "file://$src"（src 在 OUTDIR 内）拼截图 URL，
# 若 OUTDIR 是相对路径会拼成非法的 file://covers/...（缺主机/根斜杠），Chrome 渲染出错误页。踩过的坑。
OUTDIR="$(cd "$OUTDIR" && pwd)"

# ratio → "cv-h 画布宽 画布高 预览长边"
dims() {
  case "$1" in
    16x9)  echo "1080 1920 1080 1400" ;;
    16x10) echo "1200 1920 1200 1400" ;;
    9x16)  echo "1920 1080 1920 760"  ;;
    3x4)   echo "1440 1080 1440 760"  ;;
    *)     echo "" ;;
  esac
}

# 朝向：横屏 cv-w 1920 / 竖屏 1080；未显式给比例时按朝向默认
cvw=$(grep -oE -- '--cv-w: *[0-9]+px' "$HTML" | grep -oE '[0-9]+' | head -1)
[ -z "$cvw" ] && cvw=1920
if [ "${#RATIOS[@]}" -eq 0 ]; then
  if [ "$cvw" = "1080" ]; then RATIOS=(9x16 3x4); else RATIOS=(16x9 16x10); fi
fi

# 先校验比例合法，过滤掉非法值（避免后面空迭代误计数）
VALID=()
for r in "${RATIOS[@]}"; do
  if [ -n "$(dims "$r")" ]; then VALID+=("$r"); else
    echo "skip unknown ratio: $r (use 16x9|16x10|9x16|3x4)" >&2
  fi
done
[ "${#VALID[@]}" -eq 0 ] && { echo "no valid ratios" >&2; exit 1; }

pkill -9 -f "Google Chrome.*--headless" 2>/dev/null || true
sleep 1

# 1) 渲染阶段：每个比例并行，独立 profile
PIDS=()
for r in "${VALID[@]}"; do
  read -r cvh W H _ <<< "$(dims "$r")"
  src="$OUTDIR/.render-$r.html"
  sed -E "s/--cv-h: *[0-9]+px/--cv-h:${cvh}px/" "$HTML" > "$src"
  "$CHROME" --headless=new --disable-gpu --force-device-scale-factor=2 --hide-scrollbars \
    --default-background-color=00000000 --user-data-dir="$OUTDIR/.prof-$r" \
    --window-size="$W,$H" --virtual-time-budget=8000 \
    --screenshot="$OUTDIR/cover-$r.png" "file://$src" >/dev/null 2>&1 &
  PIDS+=($!)
done

# 2) 等所有 PNG 落地 —— 有界轮询。
#    关键：不要 `wait` 这些 Chrome 进程。--headless=new 截图后常不自退（render-pipeline.md 记录的坑），
#    `wait` 会永久阻塞，后面的收尾就永远到不了。改为只等文件落地，再主动收掉进程。
deadline=$((SECONDS + 40))
while [ "$SECONDS" -lt "$deadline" ]; do
  missing=0
  for r in "${VALID[@]}"; do [ -s "$OUTDIR/cover-$r.png" ] || missing=1; done
  [ "$missing" -eq 0 ] && break
  sleep 1
done

# 主动收掉本次起的 Chrome：先按 PID，再按本次 OUTDIR 的 profile 目录精确收掉残留
#（用 profile 路径匹配，不会误杀别处正在跑的其它 headless Chrome 实例）
for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null || true; done
sleep 1
pkill -9 -f "user-data-dir=$OUTDIR/.prof-" 2>/dev/null || true
for pid in "${PIDS[@]}"; do kill -9 "$pid" 2>/dev/null || true; done

# 3) 降采样 + 计数（此时文件已落地）
ok=0; fail=0
for r in "${VALID[@]}"; do
  read -r _ _ _ plong <<< "$(dims "$r")"
  png="$OUTDIR/cover-$r.png"
  if [ -s "$png" ]; then
    sips -Z "$plong" "$png" --out "$OUTDIR/cover-$r.preview.png" >/dev/null 2>&1
    d=$(sips -g pixelWidth -g pixelHeight "$png" 2>/dev/null | awk '/pixel/{printf "%s ",$2}')
    echo "OK   cover-$r.png [${d}] + preview"
    ok=$((ok + 1))
  else
    echo "FAIL cover-$r.png not produced"
    fail=$((fail + 1))
  fi
done

# 4) 清理中间文件
rm -f "$OUTDIR"/.render-*.html 2>/dev/null || true
rm -rf "$OUTDIR"/.prof-* 2>/dev/null || true

echo "done: $ok ok, $fail fail → $OUTDIR"
[ "$fail" -eq 0 ]
