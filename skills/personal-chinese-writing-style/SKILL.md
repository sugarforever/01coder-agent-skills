---
name: personal-chinese-writing-style
description: Apply the user's Chinese writing style when writing, translating, editing, proofreading, polishing, or publishing Chinese content, including blog posts, articles, subtitles, captions, tweets/X posts, threads, newsletters, and social posts. Enforce punctuation rules, especially Chinese curved quotes, halfwidth dash " - ", ASCII ellipsis "......", and no leftover fullwidth/English punctuation in Chinese body text.
---

# Personal Chinese Writing Style

Use this skill for Chinese content. The goal is not to explain the style back to the user; the goal is to apply it and verify the final text.

## Operating Workflow

1. Identify the content type: article/blog, translation/edit, subtitle/caption, or social post/thread.
2. Load only the needed reference:
   - `references/punctuation.md` - always read for Chinese output.
   - `references/article-structure.md` - read for blog posts, newsletters, long articles, and technical writeups.
   - `references/voice-and-phrasing.md` - read for translation, editing, and long-form Chinese prose.
   - `references/social-media-style.md` - read for X/Twitter, threads, short social posts, and launch notes.
3. Write or edit the content.
4. Run the final punctuation pass before delivering or saving.
5. Fix every real violation in Chinese body text, then reread the affected sentence for meaning.

## Non-Negotiable Punctuation

These are output requirements, not suggestions.

Use this exact punctuation in Chinese body text:

- Quotes: use `“` and `”`. Do not use `"` around Chinese prose.
- Dash: use ` - ` with one space on both sides. Do not use `--`, `——`, or `—`.
- Ellipsis: use `......`. Do not use `……`; do not use `...` as a Chinese ellipsis.
- Chinese sentence punctuation: use `，` `。` `：` `；` `？` `！` `、`. Do not leave `,` `.` `:` `;` `?` `!` between Chinese characters.

Allowed exceptions: YAML frontmatter, code blocks, inline code, JSON/config, URLs, file paths, shell commands, exact source quotes, and English-only sentences.

## Final Checklist

Before returning Chinese content, check:

- No `"` remains around Chinese body text.
- No `--`, `——`, or `—` remains as a dash in Chinese prose.
- No `……` remains; ellipsis is `......`.
- Chinese sentences use Chinese punctuation, not ASCII comma/period/colon/question/exclamation marks.
- Article prose has no duplicate body `# H1` when frontmatter already has `title`.
- Long-form article endings stay light: no `## 总结`, `## 最后`, `## 结语`, or repeated link dump unless the user explicitly asks.
- Social posts do not end with an empty self-summary such as “这是 X 的标志性时刻”.

## Voice Defaults

- Prefer natural Chinese technology prose over literal English translation.
- Avoid business cliches unless they are the precise industry term: 闭环、抓手、颗粒度、对齐、赋能、赛道、弯道超车、心智.
- Delete trust-me lines: “最干净的实现”, “每一步都是真实代码”, “最完整教程”.
- Let facts carry the point; do not over-explain the author’s conclusion in short posts.
