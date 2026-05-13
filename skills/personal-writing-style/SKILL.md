---
name: personal-writing-style
description: Personal writing style preferences. Reference this skill when writing, translating, or editing content to ensure consistent style, punctuation, and formatting.
---

# Personal Writing Style Guide

This skill defines personal writing style preferences, including punctuation, formatting, article structure, and tone conventions.

## Usage

Reference this skill when:
- Writing blog posts or articles
- Translating content
- Editing content for consistency
- Generating subtitles or captions
- Writing social media posts (tweets, threads)

## Style Preferences

See `references/punctuation.md` for detailed punctuation rules.
See `references/article-structure.md` for article structure and heading conventions.
See `references/voice-and-phrasing.md` for word-choice rules - avoid translation-style and net-slang constructions.
See `references/social-media-style.md` for social media (X/Twitter) writing conventions, including editorial-restraint patterns for short-form posts.

## Quick Reference

### Punctuation

> 🛑 **READ THIS FIRST — most-broken rule**: Chinese body text uses **curly quotes `“` `”` (U+201C / U+201D)**, never straight `"` (U+0022). AI assistants persistently default to straight quotes even after reading this skill. Before saving any Chinese content, verify every `"` in body text is a curly quote. The straight quote `"` is reserved for YAML frontmatter, code blocks, and config files — nowhere else.

| Element | Preferred | Avoid |
|---------|-----------|-------|
| **Quotes/引号** | `“` `”` (中文弯引号, U+201C / U+201D) | `"` (英文直引号, U+0022) |
| Dash/破折号 | ` - ` (空格-连字符-空格) | `——` (中文破折号) |
| Ellipsis/省略号 | `......` (6个英文句点) | `……` (中文省略号) |

### Article Structure

文章应该像自然对话一样流畅，而不是像教科书大纲那样机械。

- **结构隐于文中**：让内容本身传达层次，不靠编号、标签、"总结"等显式脚手架
- **frontmatter 已经声明 title，正文不要再写 `# H1` 重复**——markdown 渲染会用 frontmatter title 渲染大标题，正文 H1 就是视觉冗余
- **标题简洁，不带主标：副标结构** - 不写 `## X：拆 Y + 释放 Z`，让正文负责展开本节做什么
- **开篇用第一人称引子 + 主角英文 ID** - 「我会梳理 \`xxx\` 模型的使用......期望对大家有所帮助。」是中文技术博客的成熟开场
- **不写 trust-me / 自夸句** - 「每一步都贴真实代码」「这是最干净的实现」类 selling line 一律删，事实让读者自己判断
- **尾部克制** - 强烈偏好轻量级结尾。不写「总结」「最后」「结语」章节；不在结尾做"X 是为 A，不是 Y"的对比定位；一两个核心链接用 `---` + bullet 即可，不要 `## 链接合集` header；正文 inline 已出现的链接不在结尾重复
- **用散文连接，不要硬切**：话题之间用过渡句桥接，写博客不是写论文

### Voice and Phrasing

中文应该读起来像中文，不像英文翻译。避免翻译腔和近年网感构造。

- **避免** "X 值得花" (worth X 直译) → 用 "X 很有必要" / "X 划算" / "X 值得做"
- **避免** "你买不起 X 的成本" (can't afford X 直译) → 用 "X 的代价很大" / "承担不起 X"
- **避免** 业绩化术语：闭环、抓手、颗粒度、对齐/拉齐、赋能、赛道、弯道超车、心智 → 用日常中文等价表达
- **避免** 太口语 / 拟人化的动词（博客/文章场景生效，视频脚本和推文不强制）：「抓走」→「抓取」、「诚实写」→「如实设置」、「接住更稳」→「提高兼容性」
- **Test**：句子能一对一回译成英文且不丢信息 → 翻译腔。单句独立读像 startup 公关 → 网感词。

### Social Media Editorial Restraint

短文本里"作者表达"的空间很小，过度 editorial 反而稀释事实。让事实自己讲。

- **删显性因果连接**："原因是""所以""因此""其实" → 直接并列摆事实，读者自己接
- **软化强断言副词**："就是""完全""一定" → "似乎" / 直接去掉
- **emoji 当强动词用**："砸到 $195" → "📉 $195"；"飙升" → "📈"。视觉信号比形容词更直接
- **推文别加作者总结句**："这是 X 的标志性时刻" 类自我盖章删掉。例外：总结句删掉后推文不成立，说明它是核心观察不是总结，留着

## Notes

- These preferences are personal style choices for consistent output
- Technical content (code, filenames) should use ASCII characters
- Markdown frontmatter should use straight quotes `"` for YAML syntax
