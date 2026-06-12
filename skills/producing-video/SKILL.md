---
name: producing-video
description: Turn a user-provided voiceover audio file + SRT subtitle into a finished, narration-synced MP4 using HyperFrames (HTML-to-video). The audio + SRT are the source of truth — scenes are timed to the SRT cues, content is read from the SRT, and the audio is muxed in automatically. Use when the user hands over an mp3/wav + srt and wants a video, says "把音频做成视频", "做一期视频", "audio + srt to video", "把这期早读做成视频", "render this narration into a video", or provides a recording + subtitles for an explainer / daily / 解读 / 口播. If the user gives only the narration text (no audio), it can optionally generate the audio (ListenHub TTS) and subtitles (cloud ASR via Groq/OpenAI) upstream first. NOT for slide decks (use a slides skill).
---

# Producing-Video · 音频 + 字幕 → 成片

把"用户已经录好的口播音频 + SRT 字幕"做成一条**画面跟着声音走**的 MP4。用 HyperFrames（HTML 即视频）出片。

**铁律：音频和 SRT 是唯一事实源。** 画面的内容来自 SRT，画面的时间轴来自 SRT 的 cue 时间戳，音频作为一个 `<audio>` clip 直接挂进合成里、渲染时自动合流 —— **没有"先出视频再合音频"这一步**。

## 分工（很重要）

| 谁 | 做什么 |
|---|---|
| **用户** | 写稿 → 录音/合成音频 → 生成 SRT → 把 `audio.mp3` + `audio.srt` 交给你 |
| **本 skill（你）** | 选 frame/品牌 → 按 SRT 搭 HyperFrames 合成 → 校对 → 渲染成片 |

默认用户给你音频 + SRT，你只管出片。**但若用户只给了「文本」（口播稿）、没有音频**，本 skill 也能补上游 —— 用 `scripts/listenhub-tts.sh` 出音频 + 字幕，见下方「上游（可选）：文本 → 音频 + 字幕」。声音克隆仍是另一条线（见"超出范围"）。

## 依赖检查（pre-flight）

```bash
npx hyperframes doctor      # 需要 Node ≥ 22 · FFmpeg · Chrome
```

需要 `hyperframes` / `hyperframes-cli` 两个 skill 在场（编写合成 + 跑 CLI）。缺了就让用户 `npx hyperframes skills` 安装后重来。

确认用户给了**两个文件**：音频（mp3/wav/m4a）+ SRT。只给音频没给 SRT → 本 skill 需要 SRT 拿时间轴；可让用户补 SRT（很多录音工具/剪辑软件能导出），**不要**默认去跑 Whisper 转写（用户没给 SRT 往往是有意的，先问）。**只给了文本（口播稿）、连音频也没有** → 走下面「上游（可选）」一节，用 ListenHub 出音频 + 云端 ASR 出字幕。

---

## 上游（可选）：文本 → 音频 + 字幕

**仅当用户没给音频、只给了口播文本时走这步**；已给 mp3 + SRT 就跳过、直接进工作流。
配套 `scripts/listenhub-tts.sh`（+ `scripts/srt_helper.py`），两步出「音频 + 原始字幕」：

1. **TTS（ListenHub）** → `narration-full.mp3`。OpenAI 兼容端点 `POST /v1/audio/speech`
   （base `https://api.marswave.ai/openapi/v1`，`Authorization: Bearer $LISTENHUB_API_KEY`）。
2. **云端 ASR → 原始 SRT**。运行时选 **Groq `whisper-large-v3`** 或 **OpenAI `whisper-1`**，各自从
   `GROQ_API_KEY` / `OPENAI_API_KEY` 找 key（非交互用 `ASR_PROVIDER=groq|openai`）。**时间轴准是关键**
   —— 这步要的就是它；识别错的字下一步修。

```bash
LISTENHUB_API_KEY=...  GROQ_API_KEY=... \
  scripts/listenhub-tts.sh <narration.txt> <out-dir> [speakerId] [ttsModel]
# 出 narration-full.mp3 + narration.srt（原始，未校正）
```

### 第三步 · 字幕校正（你来编排，按此顺序）

ASR 时间轴准，但中文里的英文专名/同音字会有个别错（如 Claude→Cloud、Vercel→Verso）。**铁律仍是不动时间轴。**

1. **先扫描可用的「字幕校正」skill，优先用它。** 在当前 skill 列表里找名字含 `subtitle` / `字幕` /
   `correction` 的（如 `subtitle-correction`）。有就把原始 SRT 交给它修 —— 交互式、会问术语、质量更高。
2. **没有这类 skill** → **先跟用户确认**：「要用同一 ASR 提供方的 chat 模型做一次**文本级**校正吗？
   （只改文字、按原条目重挂时间戳，零时间轴风险）」。**用户同意**再跑：
   ```bash
   python3 scripts/srt_helper.py correct narration.srt narration.fixed.srt \
     --base <ASR_BASE> --key <ASR_KEY> --model <chatModel> --terms "OpenAI, Anthropic, Claude, Vercel, ..."
   # Groq → llama-3.3-70b-versatile · OpenAI → gpt-4o-mini；base/key 复用 ASR 那套
   ```
   `srt_helper.py correct` 只把字幕文本发给 LLM、按原条目重挂时间戳/编号；LLM 出错或条数不符自动退回原始。
3. 有 `subtitle_tool.py`（字幕校正 skill 里）就再 `validate <raw> <fixed>` 兜底确认时间轴/条数/编号没变。

校正完，把 `narration-full.mp3` + 校正后的 SRT 作为 `audio/narration-full.mp3` + `audio/narration.srt`
放进项目（Step 2），进主流程。

> 成本（~3 分钟日更）：TTS 是大头（ListenHub credits，~4 credits/分钟）；云端 ASR ~半美分到两美分、
> LLM 校正 ~1 美分，**可忽略**；渲染本地、零成本。

---

## 工作流

### Step 1 · 选 frame / 品牌

画面的风格 = 一个 frame.md / visual-style / 既有系列品牌。三种来源，按情况选：

1. **延续系列品牌**（推荐用于日更/系列）。如果这期属于一个已有系列（如"AI 早读"），去翻该系列的封面/历史成片，**沿用同一套 token**（颜色、字体、栅格、页眉页脚），让视频和封面一脉相承。
2. **HyperFrames frame.md 模板**。用户可能直接点名，例如 `creative-mode` / `biennale-yellow` / `cobalt-grid`。取 token：
   - `curl -sSL https://www.hyperframes.dev/design/<slug>.md` （站点是 JS 渲染，多半取不到正文）；
   - **更靠谱**：在本机 `open-design` 仓库里找 `design-templates/*<slug>*/template.json`，里面有精确的 `palette` / `typography`（hex + 字体名）。
3. **8 个内置 visual-style**（Swiss Pulse / Velvet Standard / Shadow Cut / Maximalist 等）。在 `hyperframes` skill 的 `visual-styles.md` 里，直接抄 YAML token。

**字体一律本地 woff2**（见 Gotcha "字体"）。中文必须配 `Noto Sans SC`（400/500/700/900 视用量）；英文 display 按 frame 选（Archivo Black / Manrope / Oswald…）；标签数字常用 `JetBrains Mono`。从 `fontsource` CDN 下到项目的 `fonts/`：
```bash
curl -sSL -o fonts/<name>.woff2 "https://cdn.jsdelivr.net/fontsource/fonts/<family>@latest/<subset>-<weight>-normal.woff2"
# 中文：subset 用 chinese-simplified；拉丁：latin
```

### Step 2 · 起项目

```bash
cd <repo>/studio/videos                       # 仓库约定：成片放这里
npx hyperframes init <YYYYMMDD-slug> --example blank --non-interactive
cd <YYYYMMDD-slug> && mkdir -p fonts audio
cp <user-audio> audio/narration-full.mp3
cp <user-srt>   audio/narration.srt
```

> **目录已有源文件时**（日更目录常已放了 `script.md` / `narration.txt`）：`hyperframes init` 拒绝非空目录（报 `Directory already exists and is not empty`）。先 `init` 到一个临时目录，再 `cp -R __tmp/. <slug>/` 把脚手架并进来，或先 `init` 再放稿。

### Step 3 · 解析 SRT → 切场景

读完整 SRT（`scripts/srt-cues.mjs` 可打印每条 cue 的开始秒数 + 文本，方便规划）。然后：

1. **按内容把 cue 归成"幕/场景"**。一条 SRT cue 通常是一句话；把讲同一件事的几条 cue 合成一个场景（scene）。一支 6~7 分钟的日更，大约 12~16 个场景比较舒服（平均 ~30s/场，画面不至于久不动）。
2. **场景开始时间 = 它第一条 cue 的开始时间戳**（秒）。
3. **场景时长 = 下一场开始 − 本场开始 + ~0.5s**（这 0.5s 重叠让转场 wipe 能盖住上一场，避免穿帮）。最后一场到音频结束。
4. **场景内的逐步出现（sub-reveal）= 对应子 cue 的开始时间**。让标题/要点/数字"在被念到的那一刻"出现 —— 这是同步感的关键。
5. **画面文案从 SRT 来，且不能和口播打架**。可以精炼成海报式短句，但不能说的是 A、画面写 B。顺手核对事实（数字、专有名词、人名）—— 用户很在意准确。

> 把场景开始时间放进一个 JS 数组 `const B = [...]`，所有 tween 用 `B[i-1] + 局部偏移` 定位。日后微调时间轴只改数组，不用逐条改 tween。

### Step 4 · 编写合成（index.html）

- **持久 chrome**：页眉/页脚/栅格/边框这类每一场都在的元素，放在场景**之外**（直接挂 `#root`，不是 clip），整片不动 —— 营造"节目"感。
- **音频一条连续 clip**（"音频即时钟"）：
  ```html
  <audio id="vo" src="audio/narration-full.mp3" data-start="0" data-duration="<总时长>" data-track-index="20" data-volume="1"></audio>
  ```
  媒体元素不需要 `class="clip"`；给它独立的 `data-track-index`。
- **每个场景一个全画布 `.scene.clip`**，各自独立 `data-track-index`（重叠的 wipe 需要不同 track），`z-index` 递增（后面的盖前面的）。
- **转场只用"incoming 场景自身的 clip-path 揭幕"**（见 Gotcha「转场」）：
  ```js
  function wipe(sel, at){ tl.fromTo(sel,{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0% 0 0)",duration:0.5,ease:"power3.inOut"}, at); }
  ```
- **入场动画**用 `tl.from(sel, vars, 位置秒)`（**必须挂在注册到 `window.__timelines` 的 `tl` 上**，第三参是 tl 上的绝对秒），定位在对应 cue 时间。短（0.3–0.7s），错峰，变化 ease。**绝不用裸 `gsap.from()` / `gsap.to()`** —— 它们挂到 gsap 全局时间轴，而渲染只 seek `tl`，会导致部分场景（尤其后段）在 seek 渲染里整片空白（见 Gotcha 12）。
- **复用一套 class 化的 CSS 工具件**（kicker / headline / note / stat / chip-xform / cards / numbered-list / accent-mark），15 个场景共享，别每场写一套 id 样式。
- **品牌纪律**：严格按 frame 的 token；强调色当"标点"不当"填充"（深色系：强调色只给小而实的标记；浅色系：强调色做色块、文字用墨色压在色块上）。

### Step 5 · 校对（每次改完都跑）

```bash
npx hyperframes lint        # 0 error 才继续（var(--x) 字体告警是误报，可忽略）
npx hyperframes validate    # WCAG AA 对比度；改掉过暗的次级灰
npx hyperframes inspect --samples 30   # 版面溢出，带时间戳；场景多就多采样
```
装饰元素故意出血到画外 → 标 `data-layout-ignore`。真实溢出 → 改容器/字号/padding。

### Step 6 · 渲染 + 验收

- **先 standard 跑一版自检**（快），用 `ffmpeg` 抽几帧验证同步：在"你知道这一刻在讲什么"的时间点抽帧，确认画面对得上。
  ```bash
  ffmpeg -y -ss <秒> -i renders/x.mp4 -frames:v 1 /tmp/f.png   # 然后看图
  ```
- **空白场景廉价自检**：每个场景中点各抽一帧，先比 PNG 文件大小 / 哈希 —— 跨场景出现一模一样的尺寸＝同一张空白帧的强信号（深色主题尤其靠这个，别只信肉眼）。命中再针对性看图。
  ```bash
  for t in <每场中点秒>; do ffmpeg -y -ss $t -i renders/x.mp4 -frames:v 1 /tmp/f_$t.png; done; ls -la /tmp/f_*.png   # 同尺寸 = 可疑
  ```
- **成片渲染**（master）：
  ```bash
  npx hyperframes render --resolution landscape-4k --quality high --output renders/<slug>-4k.mp4
  ```
  `--resolution landscape-4k` 是把同一合成按 2× DPR 真·超采样到 3840×2160（不是放大）；4K master 即使观众看 1080p 也更耐平台二压。4K + 长片渲染较久（几分钟到十几分钟），可后台跑。
- **响度核查 + 规范化**：用户的口播 / TTS 常偏安静。先 `ffmpeg -i renders/x.mp4 -af loudnorm=print_format=summary -f null -` 量整体响度；低于约 -16 LUFS 就规范化到网络标准（-14 LUFS）—— **视频流 `-c:v copy` 不重渲，几秒搞定**：
  ```bash
  ffmpeg -y -i renders/x.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k renders/x-loud.mp4
  ```
  顺手把源 `audio/narration-full.mp3` 也规范化，将来重渲（竖屏 / 改版）自动继承。
- 验收：`ffprobe` 确认有 video(h264) + audio(aac) 两条轨且时长对得上（**CLI 汇总行的时长可能误报，以 `ffprobe` 为准**）；抽帧确认每场落在它的 cue 上。

成片留在 `studio/videos/<slug>/renders/`。**不要自动提交**（除非用户明确要）。

---

## Gotchas（血泪，务必遵守）

这些是踩过的坑，违反任何一条都会出废片：

1. **音频即时钟**。场景时长从 SRT 量出来，不要凭感觉定时长再硬塞音频。
2. **有 SRT 就别转写**。用户给了 SRT = 精确时间轴免费拿到，不需要 Whisper。（没 SRT 想自己转写前先问用户。）
3. **转场只用场景自身 clip-path 揭幕**。**绝不**用单独的全屏色块/幕布/刀闸/砸场板去做转场 —— 在渲染引擎里它会"扫进来盖住下一场后卡住不走"，整场变成纯色/黑屏。揭幕揭的是 incoming 场景本体。
4. **不要给 `.pad` 容器套整体 opacity 的 "pushIn" 包装**。容器级 opacity 动画在 seek 渲染里可能留在 0，把整场变黑。用每个元素各自的 `tl.from()`（挂在 `tl` 上，不是裸 `gsap.from`，见 Gotcha 12）。
5. **配对 tween 不要加 `overwrite:"auto"`**。它会把配对的另一条 tween 杀掉（比如"扫入"在、"扫出"没了）。lint 的 overlapping_gsap_tweens 是无害告警，宁可留着。
6. **字体必须本地 woff2**。Google Fonts `<link>` 会被 lint 标记、且 sandbox 渲染里不可靠。中文配 Noto Sans SC；**中文字在彩色 accent 色块里要给足竖直 padding/line-height**（CJK 字形比 em 框高，padding 太紧 inspect 会报 text_box_overflow，给到 ~0.2em 竖直 padding + line-height ~1.12）。
7. **深色主题别信亮度探测**。1×1 平均亮度对深底+稀疏文字永远偏低，会把正常场景误判成黑屏。**靠抽帧看图**确认。
8. **浅色主题的对比度误报**。validate 在固定几个时间戳采样**所有** DOM 文字，包括当时未激活的场景。浅底上"浅色文字"（白字、奶油字）一旦不在自己场景的激活时刻被采到，就报低对比度——这是误报。规避：**accent 色块上一律用墨色（深）文字**，未激活时墨字压奶油底仍是高对比，零误报。
9. **确定性**。禁止 `Date.now()` / `Math.random()`（破坏可复现渲染）；要随机用种子化 PRNG。
10. **每个场景独立 track-index**；音频单独高 track-index。装饰出血标 `data-layout-ignore`。
11. **画质**：原生 1080p 在 Retina 上看会发虚（被放大 + H.264 4:2:0 软化彩色字缘）；master 用 `--resolution landscape-4k --quality high`。
12. **定时动画必须挂在 `tl` 上**（最高频废片坑）。一律 `tl.from / tl.to / tl.fromTo(sel, vars, 位置秒)`。**绝不用裸 `gsap.from()` / `gsap.to()`** —— 它们挂到 gsap 全局时间轴，而 HyperFrames 渲染只 seek 注册到 `window.__timelines` 的那个 `tl`。结果 wipe（在 tl）与入场（在全局轴）各跑各的，**后段场景的 clip-path 不被驱动 → 整片只剩持久 chrome、内容空白**。现象很隐蔽：前几场正常、越往后越空。排查用 Gotcha 7 / Step 6 的「空白场景廉价自检」。
13. **`data-layout-ignore` 元素保持静态**。标了它的装饰元素（大水印数字等）会被 validate 从 DOM 上下文剔除，再对它 `tl.from` 会报 `GSAP target not found`。装饰随场景 wipe 一起揭出即可，别单独 tween 它。

## SRT → 场景时间轴（配方）

```
场景[i].start    = cue[第一条].start                 (秒)
场景[i].duration = 场景[i+1].start − 场景[i].start + 0.5   (末场到音频末尾)
场景内某元素入场 = 它对应 cue 的 start
音频 clip        = data-start=0, data-duration=总时长
root data-duration = 音频末句之后留 ~3s 收尾
```

JS 里：
```js
const B = [0, 38.63, 53.96, /* ...每场 start... */];   // 从 SRT 量
const at = (i, off) => B[i-1] + off;                   // i 是 1-based 场号
function wipe(sel, i){ tl.fromTo(sel, {clipPath:"inset(0 100% 0 0)"}, {clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"power3.inOut"}, B[i-1]); }
```

## 超出范围

- **声音克隆 / 「听起来像我」**：上游 TTS（见「上游（可选）」）用的是通用音色。要克隆自己的声音，用支持克隆的云端 TTS（MiniMax / ElevenLabs），克隆只换"出声那一步"，下游时间轴/挂载/渲染不变。HyperFrames 自带的 Kokoro TTS **做不了中文**（CLI 传 `zh`、espeak 要 `cmn`，且质量差）；本机临时方案 macOS `say -v Tingting`。
- **幻灯片 deck**：要的是横向翻页 deck 而非视频 → 用 slides 类 skill。

## 输出清单

- [ ] `lint` 0 error · `validate` 全过 · `inspect` 0 issue
- [ ] 所有定时动画挂在 `tl` 上（无裸 `gsap.from/gsap.to`，见 Gotcha 12）
- [ ] 抽帧确认每场落在它的 cue 上（尤其数据页/转折页）；跨场景帧大小无异常雷同（无空白场景）
- [ ] `ffprobe`：video + audio 两轨、时长 = 音频时长（CLI 汇总行时长可能误报）
- [ ] 响度已核查：低于 -16 LUFS 已 `loudnorm` 到 -14（`-c:v copy` 不重渲）
- [ ] master 用 4K high（除非用户另说）
- [ ] 成片在 `studio/videos/<slug>/renders/`，未自动提交
