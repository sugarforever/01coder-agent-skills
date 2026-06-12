#!/usr/bin/env bash
# listenhub-tts.sh — 上游：口播文本 → 音频(ListenHub) + 原始字幕(云端 ASR)
#
# 在 producing-video 流程里：当用户只给了**文本**（没给音频/SRT）时，用本脚本补上
# 音频 + 字幕，再进入主流程。校正不在本脚本里做 —— 见 SKILL.md「上游」一节，由
# agent 编排（优先调用可用的字幕校正 skill，没有再确认后用 srt_helper.py correct）。
#
# 用法：
#   LISTENHUB_API_KEY=...  [GROQ_API_KEY=... | OPENAI_API_KEY=...] \
#     scripts/listenhub-tts.sh <input.txt> <out-dir> [ttsSpeakerId] [ttsModel]
#
# ASR 提供方：运行时选 Groq(whisper-large-v3) 或 OpenAI(whisper-1)，各自从环境变量找 key。
#   非交互用 ASR_PROVIDER=groq|openai 指定（不弹提示）。
#
# 产物（out-dir 下）：
#   narration-full.mp3   ListenHub 音频
#   narration.srt        ASR 原始字幕（未校正；交给 agent 校正后再喂 producing-video）
#
# 依赖：curl · python3（srt_helper.py 同目录）
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LH_BASE="${LISTENHUB_API_BASE:-https://api.marswave.ai/openapi/v1}"
INPUT="${1:?need input text file}"
OUTDIR="${2:?need output dir}"
TTS_SPEAKER="${3:-CN-Man-Beijing-V2}"     # GET /v1/speakers/list?language=zh 查更多
TTS_MODEL="${4:-flowtts}"

command -v curl >/dev/null || { echo "need curl" >&2; exit 1; }
command -v python3 >/dev/null || { echo "need python3" >&2; exit 1; }
[ -f "$INPUT" ] || { echo "input not found: $INPUT" >&2; exit 1; }
: "${LISTENHUB_API_KEY:?set LISTENHUB_API_KEY (https://listenhub.ai/settings/api-keys)}"
mkdir -p "$OUTDIR"

MP3="$OUTDIR/narration-full.mp3"
SRT="$OUTDIR/narration.srt"
JSON="$(mktemp -t lh-asr).json"
trap 'rm -f "$JSON"' EXIT

# ---------- 1) ListenHub TTS（OpenAI 兼容 /v1/audio/speech，同步出 mp3）----------
echo "[1/3] ListenHub TTS → $MP3  (speaker=$TTS_SPEAKER model=$TTS_MODEL)"
HTTP=$(curl -sS -w '%{http_code}' -o "$MP3" -X POST "$LH_BASE/audio/speech" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" -H "Content-Type: application/json" \
  --data "$(T="$(cat "$INPUT")" SP="$TTS_SPEAKER" MD="$TTS_MODEL" python3 -c '
import json,os; print(json.dumps({"input":os.environ["T"],"voice":os.environ["SP"],"response_format":"mp3","model":os.environ["MD"]}))')")
if [ "$HTTP" != "200" ] || ! file "$MP3" | grep -qiE 'audio|mpeg|MP3'; then
  echo "TTS failed (HTTP $HTTP):" >&2; head -c 600 "$MP3" >&2; echo >&2; exit 1
fi
echo "    ok: $(du -h "$MP3" | cut -f1)"

# ---------- 2) 选 ASR 提供方（各自从 env 找 key）----------
PROVIDER="${ASR_PROVIDER:-}"
if [ -z "$PROVIDER" ]; then
  if [ -t 0 ]; then
    echo "选择字幕 ASR 提供方：" >&2
    echo "  1) Groq   whisper-large-v3   (需 GROQ_API_KEY)" >&2
    echo "  2) OpenAI whisper-1          (需 OPENAI_API_KEY)" >&2
    read -rp "输入 1 或 2 [默认 1]: " ans
    case "${ans:-1}" in 2) PROVIDER=openai;; *) PROVIDER=groq;; esac
  else
    PROVIDER=groq; echo "[非交互] 未设 ASR_PROVIDER，默认 groq" >&2
  fi
fi
case "$PROVIDER" in
  groq)   ASR_BASE="https://api.groq.com/openai/v1"; ASR_KEY="${GROQ_API_KEY:-}";   ASR_MODEL="whisper-large-v3"
          [ -n "$ASR_KEY" ] || { echo "需要 GROQ_API_KEY（选了 Groq）" >&2; exit 1; } ;;
  openai) ASR_BASE="https://api.openai.com/v1";      ASR_KEY="${OPENAI_API_KEY:-}"; ASR_MODEL="whisper-1"
          [ -n "$ASR_KEY" ] || { echo "需要 OPENAI_API_KEY（选了 OpenAI）" >&2; exit 1; } ;;
  *) echo "未知 ASR_PROVIDER: $PROVIDER（用 groq|openai）" >&2; exit 1 ;;
esac

# ---------- 3) ASR → 原始 SRT（verbose_json → srt_helper build）----------
echo "[2/3] ASR ($PROVIDER · $ASR_MODEL, zh) → $SRT"
AHTTP=$(curl -sS -w '%{http_code}' -o "$JSON" -X POST "$ASR_BASE/audio/transcriptions" \
  -H "Authorization: Bearer $ASR_KEY" \
  -F file=@"$MP3" -F model="$ASR_MODEL" -F response_format=verbose_json -F language=zh)
[ "$AHTTP" = "200" ] || { echo "ASR failed (HTTP $AHTTP):" >&2; head -c 600 "$JSON" >&2; echo >&2; exit 1; }
python3 "$HERE/srt_helper.py" build "$JSON" "$SRT"

echo "[3/3] done →"
echo "  audio: $MP3"
echo "  srt  : $SRT   (原始，未校正)"
echo "下一步（agent 编排）：优先用可用的字幕校正 skill 修字幕；没有则确认后用"
echo "  scripts/srt_helper.py correct（只改文字、不动时间轴），见 SKILL.md「上游」一节。"
echo "校正后把 mp3 + srt 作为 audio/narration-full.mp3 + audio/narration.srt 进主流程。"
