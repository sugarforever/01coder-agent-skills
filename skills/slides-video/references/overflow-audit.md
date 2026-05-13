# QA 审核方法 · PPT 溢出 + 语言复审

本文档规定生成完 PPT 和脚本之后的 QA 审核流程。这是纯方法,不涉及任何风格。

---

## 何时审核

- **Step 7 · 生成完 PPT 和脚本之后必做**
- 任何一次 slide 内容修改之后**重做审核**
- 用户反馈迭代之后重做审核

---

## 一 · PPT 溢出审核

### 工具

用 `chrome-devtools` MCP 做自动化审计。不可用时退化到 `playwright` MCP。

### 审核流程

#### 1. 打开 PPT

```
mcp__chrome-devtools__new_page(url="file:///{abs-path}/ppt/index.html")
```

等加载完。

#### 2. 跑 JS 审计脚本

```js
() => {
  return Array.from(document.querySelectorAll('.slide')).map((s, i) => {
    const foot = s.querySelector('.foot');
    const footRect = foot.getBoundingClientRect();
    let max = 0;
    s.querySelectorAll('*').forEach(el => {
      if (el.closest('.foot') || el.closest('.chrome') || el === s) return;
      const r = el.getBoundingClientRect();
      if (r.height === 0 || r.width === 0 || el.children.length > 3) return;
      const o = r.bottom - footRect.top;
      if (o > max) max = o;
    });
    return {s: i+1, o: Math.round(max)};
  });
}
```

这段 JS 返回每张 slide 最大 overflow 像素值。

**通过标准 —— 每页 `o ≤ 5`**(抗锯齿误差范围)。

#### 3. 视觉核查可疑页

对 `o > 15` 的 slide,截图人眼再看:

```js
// 切到第 N 页
() => { document.querySelector('#deck').style.transform = 'translateX(-{N-1}00vw)'; }
```

```
mcp__chrome-devtools__take_screenshot(filePath="/tmp/slide-N.png")
```

Read 截图看是不是真的压到 foot 上了。

### Hero 页特殊情况

Hero 页(封面 / 章节幕封 / 大引用等)因 `min-height:82vh` + `align-content:center` 的渲染特性,JS 检测值可能略偏高(5-15px 假阳性)。**配合截图人眼核查** —— 视觉不压 foot 就 OK。

---

## 二 · 修复原则 · 改内容,不改模板

**优先顺序**:

1. **删冗余信息** —— 一行 meta-row 没必要? 删。callout 跟正文重复? 删。
2. **精简文字** —— 长副标写短,多段压一段。
3. **减项** —— 5 行表格改 4 行,6 张 stat 卡改 4 张。
4. **分页** —— 内容必要但一页装不下,拆成两页(页数预算 +1)。

**不允许**:
- ❌ 改模板 CSS(字号 / 间距 / padding) —— 那是 `magazine-web-ppt` 的维护范围
- ❌ 加 `overflow:hidden` —— 会截断内容
- ❌ 改 `min-height` —— 会破坏节奏

### 常见溢出场景与修法

| 场景 | 症状 | 修法 |
|---|---|---|
| stat-note 太长 | 卡片第二行文字溢出 | 改短句"13 行业 · 30 任务"(不是完整句) |
| Pipeline step-desc 写满 | 多行描述挤 foot | 每条控 2 行以内,关键词优先 |
| Callout 挤在最后 | callout + 正文叠加超出 | 改放到 foot 左侧作为 tagline |
| 表格行过多 | 最后几行落下来 | 删最次要的 1-2 行 |
| Lead 段太长 | lead 占 3 行压到后面 grid | 一句话讲清的不写两句 |
| 两个 Pipeline 堆叠 | 第二个 section 整体溢出 | 合并成一个或拆成两页 |

---

## 三 · 语言复审

PPT / script 的语言审核。跟 overflow 审核一起做。

### 审核维度

1. **术语首次出现是否有"人话"解释?**
   - 扫一遍 script,检查有没有"光秃秃"的技术术语没带解释
   - 扫一遍 PPT 每页,检查 step-title / stat-label 等是否术语过密

2. **每段是否落到"对受众意味着什么"?**
   - 扫 script 每个 section,找"对你的影响"、"翻译成场景"这类句式
   - 没找到的 section 标记出来,跟用户沟通是否需要加

3. **比喻是否合适?**
   - 每个比喻反问自己:比技术名词更直接吗?受众熟悉吗?
   - 强扭的比喻(比本体还复杂)应该去掉,改直说

4. **数字是否有参照系?**
   - 扫 PPT 里的 stat-nb / big-num 旁边,看有没有 stat-note 给参照
   - 扫 script 里的数字,看前后有没有"相当于 X"这类承接

### 复审产出

输出一份 checklist 给用户:

```
语言复审报告:

- [x] 术语解释:Slides 5/6 有术语 "mHC / CSA / HCA",script 已带人话解释 ✓
- [!] 用户视角:Slide 7 "训练稳定性三件套"段,script 未明确落"对用户意味着什么",建议补一句
- [x] 数字参照系:Slides 10 "Codeforces 3206" 已标"全球前 25 名真人选手" ✓
- [!] 过度行业体:script Section 3 有 "里程碑式发布",建议改成具体变化描述
```

用户同意后修改。

---

## 迭代原则

- 每次修改都用 **Edit tool(surgical edit)**,不整文件 rewrite —— 方便 diff 查看
- 内容优先,模板不动
- 迭代后**重跑 overflow 审核**,确保修改没引入新 overflow
- 语言复审可以在用户侧提出后再跑(不强求每次都做)

---

## 完成标准

审核通过的输出:

```json
// overflow audit
[{"s":1,"o":0},{"s":2,"o":0}, ..., {"s":N,"o":0}]
```

全部 `o ≤ 5`,且语言复审无遗留问题。然后向用户报告:

```
QA 审核通过:
- PPT overflow audit · 全部 ≤ 5px ✓
- 语言复审 · 所有 section 术语带解释 + 用户视角落点 ✓

可以开始录制。
```
