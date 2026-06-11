---
name: producing-video
description: Turn a user-provided voiceover audio file + SRT subtitle into a finished, narration-synced MP4 using HyperFrames (HTML-to-video). The audio + SRT are the source of truth — scenes are timed to the SRT cues, content is read from the SRT, and the audio is muxed in automatically. Use when the user hands over an mp3/wav + srt and wants a video, says "把音频做成视频", "做一期视频", "audio + srt to video", "把这期早读做成视频", "render this narration into a video", or provides a recording + subtitles for an explainer / daily / 解读 / 口播. NOT for generating the voiceover (that's the user's job here) and NOT for slide decks (use a slides skill).
---

# Producing-Video · 音频 + 字幕 → 成片

把"用户已经录好的口播音频 + SRT 字幕"做成一条**画面跟着声音走**的 MP4。用 HyperFrames（HTML 即视频）出片。

**铁律：音频和 SRT 是唯一事实源。** 画面的内容来自 SRT，画面的时间轴来自 SRT 的 cue 时间戳，音频作为一个 `<audio>` clip 直接挂进合成里、渲染时自动合流 —— **没有"先出视频再合音频"这一步**。

## 分工（很重要）

| 谁 | 做什么 |
|---|---|
| **用户** | 写稿 → 录音/合成音频 → 生成 SRT → 把 `audio.mp3` + `audio.srt` 交给你 |
| **本 skill（你）** | 选 frame/品牌 → 按 SRT 搭 HyperFrames 合成 → 校对 → 渲染成片 |

用户**不**指望你生成配音（那是上游）。如果用户还没有音频、问的是"怎么配音"，那不是本 skill —— TTS / 声音克隆是另一条线（见下方"超出范围"）。

## 依赖检查（pre-flight）

```bash
npx hyperframes doctor      # 需要 Node ≥ 22 · FFmpeg · Chrome
```

需要 `hyperframes` / `hyperframes-cli` 两个 skill 在场（编写合成 + 跑 CLI）。缺了就让用户 `npx hyperframes skills` 安装后重来。

确认用户给了**两个文件**：音频（mp3/wav/m4a）+ SRT。只给音频没给 SRT → 本 skill 需要 SRT 拿时间轴；可让用户补 SRT（很多录音工具/剪辑软件能导出），**不要**默认去跑 Whisper 转写（用户没给 SRT 往往是有意的，先问）。

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
- **入场动画**用 `gsap.from()`，定位在对应 cue 时间。短（0.3–0.7s），错峰，变化 ease。
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
- **成片渲染**（master）：
  ```bash
  npx hyperframes render --resolution landscape-4k --quality high --output renders/<slug>-4k.mp4
  ```
  `--resolution landscape-4k` 是把同一合成按 2× DPR 真·超采样到 3840×2160（不是放大）；4K master 即使观众看 1080p 也更耐平台二压。4K + 长片渲染较久（几分钟到十几分钟），可后台跑。
- 验收：`ffprobe` 确认有 video(h264) + audio(aac) 两条轨且时长对得上；抽帧确认每场落在它的 cue 上。

成片留在 `studio/videos/<slug>/renders/`。**不要自动提交**（除非用户明确要）。

---

## Gotchas（血泪，务必遵守）

这些是踩过的坑，违反任何一条都会出废片：

1. **音频即时钟**。场景时长从 SRT 量出来，不要凭感觉定时长再硬塞音频。
2. **有 SRT 就别转写**。用户给了 SRT = 精确时间轴免费拿到，不需要 Whisper。（没 SRT 想自己转写前先问用户。）
3. **转场只用场景自身 clip-path 揭幕**。**绝不**用单独的全屏色块/幕布/刀闸/砸场板去做转场 —— 在渲染引擎里它会"扫进来盖住下一场后卡住不走"，整场变成纯色/黑屏。揭幕揭的是 incoming 场景本体。
4. **不要给 `.pad` 容器套整体 opacity 的 "pushIn" 包装**。容器级 opacity 动画在 seek 渲染里可能留在 0，把整场变黑。用每个元素各自的 `gsap.from()`。
5. **配对 tween 不要加 `overwrite:"auto"`**。它会把配对的另一条 tween 杀掉（比如"扫入"在、"扫出"没了）。lint 的 overlapping_gsap_tweens 是无害告警，宁可留着。
6. **字体必须本地 woff2**。Google Fonts `<link>` 会被 lint 标记、且 sandbox 渲染里不可靠。中文配 Noto Sans SC；**中文字在彩色 accent 色块里要给足竖直 padding/line-height**（CJK 字形比 em 框高，padding 太紧 inspect 会报 text_box_overflow，给到 ~0.2em 竖直 padding + line-height ~1.12）。
7. **深色主题别信亮度探测**。1×1 平均亮度对深底+稀疏文字永远偏低，会把正常场景误判成黑屏。**靠抽帧看图**确认。
8. **浅色主题的对比度误报**。validate 在固定几个时间戳采样**所有** DOM 文字，包括当时未激活的场景。浅底上"浅色文字"（白字、奶油字）一旦不在自己场景的激活时刻被采到，就报低对比度——这是误报。规避：**accent 色块上一律用墨色（深）文字**，未激活时墨字压奶油底仍是高对比，零误报。
9. **确定性**。禁止 `Date.now()` / `Math.random()`（破坏可复现渲染）；要随机用种子化 PRNG。
10. **每个场景独立 track-index**；音频单独高 track-index。装饰出血标 `data-layout-ignore`。
11. **画质**：原生 1080p 在 Retina 上看会发虚（被放大 + H.264 4:2:0 软化彩色字缘）；master 用 `--resolution landscape-4k --quality high`。

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

- **生成配音 / 声音克隆**：本 skill 只吃用户给的音频。要让它"听起来像我"用云端 TTS（MiniMax / ElevenLabs，支持中文 + 克隆），克隆只换"出声那一步"，下游时间轴/挂载/渲染不变。HyperFrames 自带的 Kokoro TTS **做不了中文**（CLI 传 `zh`、espeak 要 `cmn`，且质量差）；本机临时方案 macOS `say -v Tingting`。
- **幻灯片 deck**：要的是横向翻页 deck 而非视频 → 用 slides 类 skill。

## 输出清单

- [ ] `lint` 0 error · `validate` 全过 · `inspect` 0 issue
- [ ] 抽帧确认每场落在它的 cue 上（尤其数据页/转折页）
- [ ] `ffprobe`：video + audio 两轨、时长 = 音频时长
- [ ] master 用 4K high（除非用户另说）
- [ ] 成片在 `studio/videos/<slug>/renders/`，未自动提交
