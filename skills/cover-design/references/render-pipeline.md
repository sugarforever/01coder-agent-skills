# 渲染管线 · Chrome DevTools MCP 截图

把 HTML 封面渲染成 PNG 的标准三步加陷阱说明。

## 标准命令序列

```
mcp__chrome-devtools__new_page          → 打开 file:// 路径
mcp__chrome-devtools__resize_page        → 设到 画布宽 × (画布高 + 20)
mcp__chrome-devtools__navigate_page      → reload (新尺寸下重新布局)
mcp__chrome-devtools__take_screenshot    → fullPage: true,保存到 cover-{比例}.png
```

## 多比例渲染

每个目标比例渲染一次。改 HTML 里 `:root` 的 `--cv-h`（横屏族 16:9↔16:10，竖屏族 9:16↔3:4），resize 到对应尺寸，截图存成带比例后缀的文件。resize 高度比画布多 20px 留余量（见视口陷阱）。

| 比例 | --cv-w × --cv-h | resize(width × height) | 输出文件 | 输出像素(2x) |
|---|---|---|---|---|
| 16:9  | 1920 × 1080 | 1920 × 1100 | cover-16x9.png  | ~3840×2160 |
| 16:10 | 1920 × 1200 | 1920 × 1220 | cover-16x10.png | ~3840×2400 |
| 9:16  | 1080 × 1920 | 1080 × 1940 | cover-9x16.png  | ~2160×3840 |
| 3:4   | 1080 × 1440 | 1080 × 1460 | cover-3x4.png   | ~2160×2880 |

同一个浏览器页面可复用：改 `--cv-h` 后 reload 再截图，省去重开页面。比例集合与平台映射见 `platform-specs.md`。

### Step 1 - 打开页面

```
new_page(url: "file:///Users/.../cover.html")
```

返回页面列表,新页面通常会自动 [selected]。如果之前有页面占着,后续命令会作用在新打开的这个上。

### Step 2 - 调视口大小

```
resize_page(width: 1920, height: 1100)
```

**高度故意设到 1100 而不是 1080**。原因见下方"视口陷阱"章节 - 多 20px 让浏览器 UI 余出空间,避免内容被压缩。

### Step 3 - Reload

```
navigate_page(type: "reload")
```

resize 之后必须 reload。原因:CSS 里的 `clamp(_, _vw, _)` 在 viewport 改变时不会自动重算,需要文档重新解析才能拿到正确的尺寸。

### Step 4 - 截图

```
take_screenshot(
  filePath: "/Users/.../cover.png",
  format: "png",
  fullPage: true,
)
```

**`fullPage: true` 是关键**。`fullPage: false` 只截视口可见区域,因为视口陷阱问题底部会被裁掉。`fullPage: true` 截完整 document,刚好对应 1920×1080 的 `.cover` 元素。

## 视口陷阱

`resize_page(width: 1920, height: 1080)` 不等于实际可用视口是 1920×1080。Chrome 的浏览器 UI(标签栏、URL 栏、bookmark 栏、Developer Tools 等)会占掉一部分高度。实测在 macOS Chrome 上,设 1920×1080 实际拿到的 viewport 是 **1920 × 714** 左右,差了将近 366px。

如果 HTML 用 `100vh` 决定 `.cover` 高度,内容会被压缩到 714px 高,底部行被裁。

### 两个修正

1. **CSS 用固定像素** - `.cover { width: 1920px; height: 1080px; }` 不依赖视口。
2. **截图用 fullPage** - 不依赖视口大小,截整个 document。

两条都要做。只做其一仍会出问题:
- 只用固定像素 + 非 fullPage 截图 → 截到的图被视口裁剪
- 只用 fullPage 截图 + 100vh → `.cover` 高度变成 714px,内容被压缩

## 输出尺寸

截图默认按当前设备的 device pixel ratio 输出。在 macOS Retina 屏上 DPR = 2,所以 1920×1080 的 CSS 像素 → **3840 × 2160 的实际像素 PNG**。

这是好事 - 高分辨率 PNG 缩到平台落点尺寸(YouTube 1280×720、Bilibili 1146×717、抖音 1080×1920、视频号 1080×1440、X Card 1200×630)都还清晰。各平台精确像素见 `platform-specs.md`。

如果需要严格 1920×1080 输出,可在 Step 1 之前加:

```
new_page(url: "...")
# 用 evaluate_script 强制 DPR = 1
# (一般不需要,3840×2160 直接缩到 1920×1080 质量更好)
```

## 常见错误排查

| 现象 | 可能原因 | 修法 |
|---|---|---|
| 截图底部被裁 | 用了 `fullPage: false` 或 CSS 用了 `100vh` | 改成 `fullPage: true` + 固定像素 |
| 字号比预期小 | `clamp()` 里 `_vw` 没达到最大值,因为视口宽度不够 | resize 到至少 1920 宽 |
| 字体加载失败 | Google Fonts 没加载完就截图了 | 截图前用 `wait_for` 等待 / `mcp__chrome-devtools__wait_for` |
| 颜色偏暗 / 偏亮 | Chrome 用了自动暗色模式 | 加 `<meta name="color-scheme" content="dark">` |
| PNG 是 1920×714 | 视口陷阱,见上方 | 改用 `fullPage: true` |

## 完整调用示例

```
# Step 1
mcp__chrome-devtools__new_page(
  url: "file:///Users/wyang14/github/contenthub/videos/20260529-claude-code-dynamic-workflows/cover.html"
)

# Step 2
mcp__chrome-devtools__resize_page(width: 1920, height: 1100)

# Step 3
mcp__chrome-devtools__navigate_page(type: "reload")

# Step 4
mcp__chrome-devtools__take_screenshot(
  filePath: "/Users/wyang14/github/contenthub/videos/20260529-claude-code-dynamic-workflows/cover.png",
  format: "png",
  fullPage: true
)

# Step 5 (optional - 给用户预览)
Bash: open /Users/wyang14/github/contenthub/videos/20260529-claude-code-dynamic-workflows/cover.png
```

## 回退：headless Chrome（MCP 被占用时）

如果 Chrome DevTools MCP 报 `browser is already running ... profile` —— 说明已有 Chrome 占着 MCP 的 profile 锁，MCP 连不上。**不要去劫持用户当前的标签页**。改用 headless Chrome 直接截图（用独立 profile，不抢锁）：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --user-data-dir=/tmp/chrome-render-profile \
  --force-device-scale-factor=2 \
  --window-size=1080,1920 \
  --virtual-time-budget=5000 \
  --screenshot=/path/to/cover-9x16.png \
  "file:///path/to/cover.html"
```

- `--window-size` 设成该比例的画布尺寸（横屏 1920×1080 等），截图即视口，正好对应固定像素 `.cover`
- `--force-device-scale-factor=2` 出 2x retina（如 1080×1920 → 2160×3840）
- `--virtual-time-budget=5000` 给 Google Fonts 留加载时间，否则字体可能没就绪就截了
- 每个比例改 `--window-size` 和 HTML 里的 `--cv-h`，跑一次

**坑：`--headless=new` 写完 PNG 后常常不退出**（进程挂住）。所以**不要**把多个渲染串行写在一条命令里 - 第一个会卡住，后面的永远不跑。两个稳妥做法：
1. 每个渲染用独立 `--user-data-dir`，detached 并行起（`( "$CHROME" ... & )`），PNG 落地后再 `pkill -f "Google Chrome.*--headless"` 统一收尸；
2. 或用 `--headless`（老模式），截完更可能自己退。
PNG 本身是好的，挂住的只是进程退出。

## 性能与并发

每次 `take_screenshot` 大约 1-3 秒(取决于字体加载、渲染复杂度)。一次性渲染多版本可以:

1. 在同一个浏览器实例里复用页面,每次只换 URL
2. 或者在不同模板间用 `evaluate_script` 切换 CSS 变量,只截图不 reload

但绝大多数封面只渲染 1-2 次,简单串行就够,不用过早优化。
