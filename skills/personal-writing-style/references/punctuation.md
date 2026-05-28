# Chinese Punctuation Rules

Apply these rules to Chinese body text. They do not apply to YAML frontmatter, code, JSON/config, URLs, file paths, commands, or exact source quotes.

## Required Forms

Use the form on the left. Replace the form on the right.

- `“中文”` replaces `"中文"`.
- `前文 - 后文` replaces `前文--后文`, `前文——后文`, and `前文—后文`.
- `中文......` replaces `中文……` and Chinese prose ellipsis written as `中文...`.
- `中文，中文。` replaces `中文,中文.`.
- `问题？回答！` replaces `问题?回答!`.
- `说明：内容；补充` replaces `说明:内容;补充`.

## Common Failure Modes

- Straight quotes remain in Chinese prose: `他说"可以运行了"` should be `他说“可以运行了”`.
- The model writes `--` or `——` for a dash. Replace with ` - `.
- The model writes `……`. Replace with `......`.
- English punctuation leaks into Chinese sentences: `中文,中文` should be `中文，中文`.

## Examples

```text
Correct:
Clawdbot 文档推荐使用 Opus 4.5，部分原因就是它有“更好的 prompt injection 抵抗能力” - 这说明维护者很清楚这是一个真实问题。
所有这些......能力确实是变革性的。

Avoid:
Clawdbot 文档推荐使用 Opus 4.5,部分原因就是它有"更好的 prompt injection 抵抗能力"——这说明维护者很清楚这是一个真实问题。
所有这些……能力确实是变革性的。
```

## Manual Audit

Before delivering, scan the final text for these literal tokens:

- `"` in Chinese body text.
- `--`, `——`, or `—` used as a dash.
- `……`.
- `,` `.` `:` `;` `?` `!` between Chinese characters.

Fix all true positives. If a token is inside a source quote or technical syntax, keep it and do not rewrite the quoted/source material.

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
