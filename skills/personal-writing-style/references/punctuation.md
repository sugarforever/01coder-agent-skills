# Chinese Punctuation Preferences

Personal style preferences for Chinese punctuation in written content.

> 🛑 **Rule #1 — Quotes are the most-broken rule.** Read this section before anything else, and verify your output against it before saving. AI assistants repeatedly write straight `"` (U+0022) in Chinese body text even after reading this skill — including immediately after acknowledging the rule. The fix is mechanical: every `"` that surrounds Chinese body text must be `“` (U+201C) or `”` (U+201D). Treat this as a checklist item, not a stylistic preference.

## Quotes / 引号

**Preferred**: `“` (U+201C, left curly quote) and `”` (U+201D, right curly quote)
**Avoid**: `"` (U+0022, straight ASCII double quote)
**Context**: For Chinese text content (body text, not code)

### Why this rule gets broken

When an AI tool writes a file containing `"` it almost always produces U+0022 unless the curly characters were explicitly pasted from another source. The visual difference is small in some fonts but the codepoints are different and Chinese typography expects U+201C/201D. A correctly-styled file is byte-identifiable; a wrong one is not.

### Pre-save checklist for AI assistants

Before saving any Chinese content (blog post, tweet, subtitle, doc):

1. Search the file for `"` (U+0022)
2. For every match, confirm it's inside:
   - YAML frontmatter (`title: "..."`) ✅ keep
   - Code block (```` ``` ````) ✅ keep
   - Config / JSON value ✅ keep
3. Any other `"` in Chinese body text → replace with `“` / `”`
4. Verify by reading codepoints, not by visual inspection

### Examples

```
✅ Correct (Chinese content):
但“真正去做事情”意味着“可以在你的电脑上执行任意命令”。
很多人想体验这个“贾维斯式”的 AI 助手。

❌ Avoid (Chinese content):
但"真正去做事情"意味着"可以在你的电脑上执行任意命令"。
很多人想体验这个"贾维斯式"的 AI 助手。
```

### How to Type

- macOS: `Option + [` for `“`, `Option + Shift + [` for `”`
- Or copy from here: `“` `”`

### Exception: YAML/Code

Use straight quotes `"` in:
- Markdown frontmatter (YAML syntax requirement)
- Code blocks
- JSON/config files

```yaml
# Frontmatter uses straight quotes
---
title: "文章标题"
tags: ["AI", "安全"]
---
```

---

## Dash / 破折号

**Preferred**: ` - ` (space-hyphen-space)
**Avoid**: `——` (Chinese em dash, U+2014)

### Examples

```
✅ Correct:
Clawdbot 文档推荐使用 Opus 4.5，部分原因就是它有"更好的 prompt injection 抵抗能力" - 这说明维护者们很清楚这是一个真实的问题。

❌ Avoid:
Clawdbot 文档推荐使用 Opus 4.5，部分原因就是它有"更好的 prompt injection 抵抗能力"——这说明维护者们很清楚这是一个真实的问题。
```

### Rationale
- More consistent across platforms and fonts
- Easier to type
- Cleaner visual appearance in technical content

---

## Ellipsis / 省略号

**Preferred**: `......` (six ASCII periods)
**Avoid**: `……` (Chinese ellipsis, U+2026 × 2)

### Examples

```
✅ Correct:
Clawdbot、Claude computer use，所有这些......能力确实是变革性的。

❌ Avoid:
Clawdbot、Claude computer use，所有这些……能力确实是变革性的。
```

### Rationale
- Consistent character width
- Better compatibility with plain text environments
- Easier to search and replace

---

## Summary Table

| Punctuation | Chinese Name | Preferred | Unicode | Avoid | Unicode |
|-------------|--------------|-----------|---------|-------|---------|
| Dash | 破折号 | ` - ` | U+002D | `——` | U+2014 |
| Ellipsis | 省略号 | `......` | U+002E × 6 | `……` | U+2026 × 2 |
| Left Quote | 左引号 | `"` | U+201C | `"` | U+0022 |
| Right Quote | 右引号 | `"` | U+201D | `"` | U+0022 |

---

## Bullet 列表项的结尾标点

列表项的句号要么都加、要么都不加，不混搭。这是排版一致性的小要求，不是 punctuation 选择题。

### When to use which

- **列表项是完整句子**（带主语 + 谓语 + 宾语，能独立读完不别扭）→ 都加句号
- **列表项是名词短语 / 关键词 / 标签 / 短结构**（如「闭环」「跑通流程」）→ 都不加
- **列表项是「短语 + 解释」**（用 ` - ` 或冒号分隔的展开）→ 看解释部分：解释是完整句就都加，解释是短语就都不加

### Examples

```
✅ 一致（都加，因为每项是完整句）：
- 客户端代码在打包后是公开的，key 一旦出现就有可能被反编译看到。
- Mint client secret 在服务端做，offscreen 只接到生命期几分钟的临时 token。
- 即使被截获影响也有限。

✅ 一致（都不加，因为每项是短语）：
- 闭环
- 抓手
- 颗粒度

❌ 不一致：
- 这是第一项。
- 这是第二项
- 这是第三项。
```

---

## Application Scope

These preferences apply to:
- Blog posts and articles
- Translated content
- Video subtitles (Chinese)
- Social media posts

Exceptions:
- Code and technical identifiers
- Markdown/YAML frontmatter
- Direct quotes from sources (preserve original punctuation)
