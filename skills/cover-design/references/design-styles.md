# Design Styles · 封面风格目录

cover-design 的每个风格都落成一对模板：横屏（`{style}.html`，16:9 / 16:10）+ 竖屏（`{style}-vertical.html`，9:16 / 3:4）。这份文档给每个风格的视觉锚点、identity test（判定是否"做对了"的硬标准）和适用场景。新增风格时照这个结构补一段。

通用约束（所有风格都遵守，见 `thumbnail-vs-slide.md` 和 `platform-specs.md`）：
- 固定像素画布（`--cv-w` / `--cv-h`），不用 viewport 单位
- 单焦点 + 大标题（缩到 160px 仍可读）
- 竖屏文字收在中央安全带
- 一个风格 = 一套可复用的 CSS 变量 + 占位符，新增风格不动主流程

---

## 中文大标题的行高（line-height）

**这是个真坑，不是品味问题。** 拉丁字母的字身框（em box）上下自带留白（ascender 上方、descender 下方），所以西文 display 大字用 0.9 行高仍有呼吸感；**中日韩方块字几乎填满整个 em box**，同样 0.9 行高，两行的笔画就会贴脸甚至相撞（带 辶 / 宀 / 廴 这类上下伸展部首时最明显）。所以**同字号下中文标题要比拉丁标题松一档**。

两个约束的交集决定取值：
- 中文比拉丁需要更大行高（[Typotheque](https://www.typotheque.com/articles/typesetting-cjk-text)：CJK 填满 em box；[Material Design](https://m1.material.io/style/typography.html)：CJK 行高比西文统一 +0.1em）。
- display 越大行高越紧（headline 安全区 1.1–1.4；[Pimp my Type](https://pimpmytype.com/line-length-line-height/) / [Material 3](https://m3.material.io/styles/typography/applying-type)）。
- 中文正文是 1.5–1.7（[W3C clreq](https://www.w3.org/TR/clreq/)：行距取字身 50%–100%）——标题要比这紧得多。

**落点：中文 display 标题 ≈ 1.05–1.10**。字重越重 / 笔画越粗 / 衬线，越要往高取：

| 档 | 风格（按字重·字体） | 中文标题 line-height |
|---|---|---|
| 轻（weight ≤500） | swiss(300)、aurora(500) | **1.06** |
| 中（weight 600） | glass-dark(600) | **1.08** |
| 重（weight ≥700）/ 衬线 | hero-typography、neo-brutalism、bauhaus、brutalism、spotlight、blueprint、terminal、holographic、editorial、noir-editorial | **1.10** |

注意：
- line-height **只影响多行标题**。这些模板标题都是两行 `.stack`，所以都生效；单行标题取多少都无所谓。
- 取值按**中文最坏情况**定；纯英文标题在同一行高下只是略松，不影响。
- 副标 / 正文（`.sub`）保持 1.1–1.25，不动。
- 改完务必渲染验证：横屏挑一个重字重风格（如 neo-brutalism）确认不撞行，竖屏确认三行标题仍在安全带内。

---

## 已实现

### hero-typography（黑底霓虹）
- **锚点**：纯黑底 + 霓虹大字（lime）+ 两侧 fan-out 节点 + radial glow
- **identity test**：①纯黑底 ②单一霓虹强调色 ③大标题字重 ≥800（越大越粗）④装饰是发光节点/连线
- **适合**：技术解读、新功能发布、概念视频，强视觉钩子

### swiss（瑞士国际主义）
- **锚点**：暖纸底 + 严格网格 + 极轻大字 + 单一高饱和强调色 + 1-2px 细线，左对齐非对称留白
- **identity test**：①大标题（≥72px）字重 ≤300（越大越细）②不加载衬线 ③分隔只用 hairline/网格线，无卡片/阴影/圆角 ④恰好一个强调色
- **强调色预设**：IKB 蓝 `#0a1cff`、安全橙 `#ff5a1f`、柠檬绿 `#b6ff3b`、柠檬黄 `#e8ff00`（只选一个）
- **适合**：技术拆解、评测、数据类，冷静专业

### neo-brutalism（新粗野）
- **锚点**：高饱和撞色底（亮黄/亮粉/电蓝）+ 粗黑描边（4-6px）+ 硬阴影（offset 实色，无模糊）+ 圆角块 + 粗黑字
- **identity test**：①每个主元素有 ≥4px 纯黑 border ②阴影是 `Npx Npx 0 #000`（hard，无 blur）③≥2 个高饱和色块 ④无渐变、无柔和阴影
- **字体**：粗 grotesque（Archivo / Space Grotesque）+ Noto Sans SC
- **适合**：产品发布、工具类、玩味醒目的选题

### bauhaus（包豪斯）
- **锚点**：米白/黑底 + 三原色（红黄蓝）色块 + 圆/三角/方几何构成 + 粗网格 + 大写无衬线
- **identity test**：①只用红黄蓝 + 黑（不加其他色相）②画面有圆/三角/矩形几何元素参与构图 ③字体几何无衬线（Futura/Poppins 类）④构图基于网格
- **适合**：设计/理论/艺术类、经典感选题

### editorial（杂志风）
- **锚点**：暖纸底 + 衬线大标题（Songti/Playfair 类）+ 安静无衬线正文 + 氛围背景（纸纹/墨晕）+ 细线/分栏/pull quote
- **identity test**：①大标题用衬线字族 ②背景有氛围层（grain/纸纹/墨色），不是纯平色 ③"越大越细"（display weight ~500 + 宽字距）④有杂志感元素（栏线、引文、页眉 ledger）
- **适合**：观点、深度长文、人物、叙事类

### brutalism（粗野）
- **锚点**：白底 + 系统默认字体（Times/Courier/Arial）+ 硬黑边框 + 刻意"未加工"的排版 + 裸链接/下划线感
- **identity test**：①字体是系统默认/等宽（不加载花哨 web font）②硬边框、无圆角无阴影 ③高对比黑白为主，强调色至多一个且生硬 ④排版刻意朴素甚至"丑"
- **适合**：黑客、独立开发、逆向工程、反精致气质的技术内容

### aurora（极光渐变）
- **锚点**：近黑深色底 + 2-3 团彩色径向光晕（蓝/紫/青）柔和叠加 + 细网格 + 渐变描字
- **identity test**：①深色底 ②多团彩色光晕通透叠加 ③大字偏细（weight ≤500）④无硬边框/无硬阴影，整体通透（Vercel / Linear / OpenAI 那种现代 AI/SaaS 审美）
- **适合**：AI / SaaS / 现代科技产品解读，当下感最强
- **强调色**：默认蓝紫青三色光晕，可整体换色相

### glass-dark（深色玻璃拟态）
- **锚点**：深底 + 背后柔光透出 + 磨砂玻璃面板（backdrop-blur + 半透明 + 1px 高光描边 + 大圆角）
- **identity test**：①深色底 ②背后 2-3 团柔光 ③主内容在磨砂玻璃面板里（模糊 + 透明 + 高光边）④大字偏白通透，无硬阴影
- **适合**：AI / 产品 / 现代科技解读，通透高级（visionOS / Apple 质感）
- **强调色**：默认蓝紫青光晕，可整体换色相

### terminal（终端黑）
- **锚点**：纯黑 + 全等宽字 + 绿/琥珀荧光 + 扫描线 + 命令提示符 + 光标块
- **identity test**：①纯黑底 ②全等宽字体 ③单一荧光色带 glow ④有扫描线 + prompt + 闪烁光标
- **适合**：CLI / 开发 / 黑客 / 逆向 / 命令行工具
- **换色**：默认荧光绿，琥珀把 `--term` 改 `#ffb000`

### noir-editorial（暗调杂志）
- **锚点**：近黑底 + 衬线大标题 + 单一暖金强调 + 胶片颗粒 + 细线/№ 页眉
- **identity test**：①近黑底（非纯黑）②大标题衬线字族 ③恰好一个暖金强调色 ④背景有颗粒氛围，"越大越细"
- **适合**：观点 / 深度长文 / 人物 / 叙事（editorial 的暗黑高级版）

### spotlight（聚光戏剧光）
- **锚点**：全黑 + 单束聚光（径向亮斑）落在标题 + 四周强暗角 + 高对比白字
- **identity test**：①近黑/全黑底 ②单束聚光照亮标题区 ③明显暗角 vignette ④明暗反差极大（chiaroscuro）
- **适合**：发布 / 悬念 / 重磅选题，电影海报感

### blueprint（深蓝图）
- **锚点**：深藏青底 + 白色双层网格 + 线稿装饰（角标尺/标注线/⌖）+ 等宽标注，标题描边
- **identity test**：①深藏青/蓝图蓝底 ②细网格 + 主网格两层 ③有工程线稿元素（标注线/十字/尺寸线）④等宽标注字
- **适合**：架构 / 原理 / 技术拆解，工程蓝图气质

### holographic（暗调全息）
- **锚点**：深底 + 油膜虹彩渐变大字（青/品红/黄/绿）+ 全息箔色带 + 微噪点
- **identity test**：①深色底 ②大字填充多色虹彩渐变 ③有一条全息箔色带 ④微噪点/微光，premium 不廉价
- **适合**：前沿 / 概念 / 潮流科技
- **字体**：Space Grotesk + Noto Sans SC

---

## 写新风格的检查清单

1. 横屏 `{style}.html` + 竖屏 `{style}-vertical.html` 两个文件
2. `:root` 暴露 `--cv-w` `--cv-h` `--bg` `--ink` `--accent` `--font-display` `--font-mono`（按风格可加）
3. 文件顶部 HTML 注释写：支持比例 + 怎么切 `--cv-h` + 适配平台 + identity test 摘要
4. 竖屏文字收在中央安全带，带 `body.show-guide` 辅助线
5. 在本文件加一段（锚点 + identity test + 适用场景），并在 SKILL.md Step 2 列入候选
6. 渲染验证：横屏 16:9 + 竖屏 9:16 各截一张，肉眼确认 identity test 全过
