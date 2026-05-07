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
See `references/social-media-style.md` for social media (X/Twitter) writing conventions.

## Quick Reference

### Punctuation

| Element | Preferred | Avoid |
|---------|-----------|-------|
| Dash/破折号 | ` - ` (空格-连字符-空格) | `——` (中文破折号) |
| Ellipsis/省略号 | `......` (6个英文句点) | `……` (中文省略号) |
| **Quotes/引号** | `""` (中文弯引号) | `""` (英文直引号) |

⚠️ **Common Mistake**: Always use curved quotes `""` in Chinese body text. Straight quotes `""` are only for YAML/code.

### Article Structure

文章应该像自然对话一样流畅，而不是像教科书大纲那样机械。

- **结构隐于文中**：让内容本身传达层次，不靠编号、标签、"总结"等显式脚手架
- **用散文连接，不要硬切**：话题之间用过渡句桥接，写博客不是写论文

### Voice and Phrasing

中文应该读起来像中文，不像英文翻译。避免翻译腔和近年网感构造。

- **避免** "X 值得花" (worth X 直译) → 用 "X 很有必要" / "X 划算" / "X 值得做"
- **避免** "你买不起 X 的成本" (can't afford X 直译) → 用 "X 的代价很大" / "承担不起 X"
- **避免** 业绩化术语：闭环、抓手、颗粒度、对齐/拉齐、赋能、赛道、弯道超车、心智 → 用日常中文等价表达
- **Test**：句子能一对一回译成英文且不丢信息 → 翻译腔。单句独立读像 startup 公关 → 网感词。

## Notes

- These preferences are personal style choices for consistent output
- Technical content (code, filenames) should use ASCII characters
- Markdown frontmatter should use straight quotes `"` for YAML syntax
