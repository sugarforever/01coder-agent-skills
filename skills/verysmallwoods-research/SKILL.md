---
name: verysmallwoods-research
description: Fetch and browse recent items from the verysmallwoods research feed — AI, LLM, Agents, and Coding-Agent articles/videos collected from RSS and YouTube sources — plus AI/tech news headlines from a separate aggregator lane (TechCrunch AI, Hacker News, The Decoder, MarkTechPost, Ars Technica AI, MIT Tech Review AI, AI News). Use these items as grounding material for drafting blog posts or topic discovery. Invoke when the user asks things like "今天有什么新鲜的", "过去 24 小时有什么", "研究源", "新内容", "情报", "看看最近", "看看过去一周", "什么值得写", "候选素材", "帮我找篇能写的", "今天 AI 圈有什么新闻", "最新动态", "AI 趋势", "热点话题", "what's new", "what landed today", "research feed", "candidate sources", "any good articles lately", "draft a post on the latest X", "trending in AI", "AI news today", or when the user names a topic and wants candidate articles or asks for help drafting a blog post based on recent items.
---

# verysmallwoods-research

Fetch recent research feed entries (articles and videos) from the verysmallwoods backend, present them as a candidate list, then fetch full detail for the one the user picks — ready to ground a blog post draft.

## Two lanes, two endpoints

The backend exposes two separate feeds:

| Lane | Endpoint | Use for | Importance scored? |
|---|---|---|---|
| **research** | `/research/recent` | Deep content (blogs, VC posts, newsletters, YouTube) — finding material to write about | Yes (1-5) |
| **trends** | `/research/trends` | News headlines (TechCrunch AI, HN, The Decoder, etc.) — spotting what's happening right now | No (binary filter only) |

`/research/recent` automatically excludes news-aggregator sources, and `/research/trends` only returns them. They never overlap. Pick the right one based on whether the user wants "what's worth writing about" (research) vs "what's trending" (trends).

## Setup

This skill requires two environment variables:

| Variable | Example value |
|---|---|
| `VSW_RESEARCH_API_BASE` | `https://verysmallwoods.<account>.workers.dev` |
| `VSW_RESEARCH_API_TOKEN` | `resrch_…` (research-specific token) |

If either variable is missing or empty, stop and tell the user:

> "I need `VSW_RESEARCH_API_BASE` and `VSW_RESEARCH_API_TOKEN` set in my environment. Please add them (e.g., via `claude config set env.VSW_RESEARCH_API_BASE=…`) and try again."

Do not attempt any API calls until both are confirmed present.

---

## Mode 1 — List candidates ("what's new")

**Trigger:** the user asks what's new, what's available, last N hours/days, "情报", "看看最近", "research feed", etc., or wants a pool of candidate articles to choose from.

**Note:** This endpoint excludes news-aggregator sources (TechCrunch AI, Hacker News, etc.) — for breaking news and trend-scanning, use **Mode 3** (`/research/trends`) instead.

### 1.1 Build the request

```
GET {VSW_RESEARCH_API_BASE}/research/recent
  ?since_hours={N}
  &min_importance={M}
  [&source_type=article|video]
  [&limit={K}]

Authorization: Bearer {VSW_RESEARCH_API_TOKEN}
```

**Defaults (use these unless the user specifies otherwise):**

| Param | Default | Override when user says… |
|---|---|---|
| `since_hours` | `24` | "过去一周" → `168`, "last 3 days" → `72`, etc. |
| `min_importance` | `3` | "broader" / "包括更多" → `2`; "只要精品" / "importance 5" → `5` |
| `source_type` | _(omit — no filter)_ | "只看视频" / "videos only" → `video`; "只看文章" → `article` |
| `limit` | `50` | user says "give me the top 10" → `10` |

Do NOT override `min_importance` unless the user explicitly asks — the server default of 3 is already calibrated.

### 1.2 Response shape

```json
{
  "entries": [
    {
      "id": "e_abc123...",
      "url_original": "https://...",
      "title_original": "...",
      "source_type": "article",
      "published_at": "2026-05-01T08:00:00Z",
      "fetched_at": "2026-05-01T08:31:12Z",
      "importance": 4,
      "source": {
        "id": "anthropic-eng",
        "name": "Anthropic Engineering",
        "kind": "rss"
      }
    }
  ],
  "count": 42
}
```

### 1.3 Present as a table

Sort by `importance DESC`, then `published_at DESC`.

For Chinese conversations, use Chinese column labels. For English, use English.

**Chinese table:**

| # | ★ | 来源 | 标题 | 发布时间 | 链接 |
|---|---|---|---|---|---|
| 1 | 5 | Anthropic Engineering | … | 3 小时前 | … |

**English table:**

| # | ★ | source | title | when | url |
|---|---|---|---|---|---|
| 1 | 5 | Anthropic Engineering | … | 3h ago | … |

"when" column: compute relative time from `published_at` (e.g., "3 小时前", "昨天", "2 天前"; "3h ago", "yesterday").

**Do NOT fetch full content for every item** — only display what's in the list response. Wait for the user to pick one.

After presenting: ask the user which item(s) they want to explore ("哪条想深入看看？" / "Which one would you like to explore?").

### 1.4 Client-side filtering

The API does not filter by source. If the user asks for a specific source (e.g., "看看 Anthropic 出了什么"), fetch the full list then filter in-display by `source.id` or `source.name`. Show a note: "以下是 Anthropic Engineering 的条目：".

---

## Mode 3 — Scan trends ("what's happening today")

**Trigger:** the user asks what's happening / trending / making news, "今天 AI 圈有什么新闻", "AI 趋势", "热点", "what's trending in AI", or wants topic discovery from breaking news rather than a curated reading list.

### 3.1 Build the request

```
GET {VSW_RESEARCH_API_BASE}/research/trends
  ?since_hours={N}
  [&limit={K}]
  [&source_id={id}]

Authorization: Bearer {VSW_RESEARCH_API_TOKEN}
```

**Defaults:**

| Param | Default | Override when user says… |
|---|---|---|
| `since_hours` | `72` | "today" / "今天" → `24`; "this week" / "过去一周" → `168` |
| `limit` | `100` | "top 20" → `20` |
| `source_id` | _(omit — all news sources)_ | "只看 Hacker News" → `hn-front`; "TechCrunch" → `tc-ai` |

The hard cap on `since_hours` is `168` (7 days) — older trends data isn't kept.

### 3.2 Response shape

```json
{
  "entries": [
    {
      "id": "e_xyz789...",
      "url_original": "https://...",
      "title_original": "...",
      "published_at": "2026-05-06T15:00:00Z",
      "fetched_at": "2026-05-06T15:30:00Z",
      "source": {
        "id": "tc-ai",
        "name": "TechCrunch AI"
      }
    }
  ],
  "count": 47
}
```

**Note:** No `importance`, no `source_type` — trends entries are binary-filtered for AI/tech relevance, not scored.

### 3.3 Present as a table

Sort by `published_at DESC` (already the API's default order — preserve it).

**Chinese table:**

| # | 来源 | 标题 | 发布时间 | 链接 |
|---|---|---|---|---|
| 1 | TechCrunch AI | … | 2 小时前 | … |

**English table:**

| # | source | title | when | url |
|---|---|---|---|---|
| 1 | TechCrunch AI | … | 2h ago | … |

### 3.4 Spotting trending events

Multiple sources covering the same release / launch / story = trending event. After presenting the table, scan for clusters and call them out:

> "看起来 OpenAI 今天发了新模型 — TechCrunch、The Decoder、Hacker News 都有报道。要深入看吗？"

When the user picks one, drill down via Mode 2 (`/research/entry/:id`) or directly WebFetch the URL for the full article.

### 3.5 News sources currently covered

| id | source |
|---|---|
| `tc-ai` | TechCrunch AI |
| `mit-tr-ai` | MIT Tech Review AI |
| `hn-front` | Hacker News (front page) |
| `the-decoder` | The Decoder |
| `marktechpost` | MarkTechPost |
| `ai-news` | AI News (artificialintelligence-news.com) |
| `ars-ai` | Ars Technica AI |

---

## Mode 2 — Fetch one entry (after user picks)

**Trigger:** user picks a specific item — "write about #2", "the Anthropic one", "就那篇 Cursor 的", "let's do that one", etc.

### 2.1 Fetch the full entry

```
GET {VSW_RESEARCH_API_BASE}/research/entry/{id}

Authorization: Bearer {VSW_RESEARCH_API_TOKEN}
```

The response includes the full row, including a `raw_content` field (the RSS/Atom description — typically a 200-500 character snippet, **not the full article body**).

### 2.2 Fetch full article body for grounding

`raw_content` is almost always a short snippet. **Use WebFetch on `url_original`** to retrieve the full page body when you need real grounding for the blog post.

```
WebFetch: {entry.url_original}
```

Read the full article carefully before drafting.

### 2.3 Draft the blog post (when user asks)

Follow the user's established writing style:

- Language: Chinese (zh) primary unless the user asks for English
- Structure: numbered sections (一、二、三 for zh; 1. 2. 3. for en)
- Tone: technical deep dive, practical — explain the "why" before the "how"
- Include code snippets, tables, and Mermaid diagrams where they illustrate the concepts
- End with an actionable summary / optimization section
- Frontmatter: `title`, `date`, `excerpt`, `tags` (tags in Chinese for zh posts)
- File naming: `YYYYMMDD-slug.md` convention

You may invoke the `personal-writing-style` skill once the full article content is in hand.

---

## Examples

**"今天有什么新鲜的"**
→ Mode 1, `since_hours=24`, default `min_importance=3`, no source filter.

**"过去一周 Anthropic 出了什么"**
→ Mode 1, `since_hours=168`, then filter displayed results client-side by `source.name` containing "Anthropic".

**"给我 importance 5 的清单"**
→ Mode 1, `min_importance=5`.

**"只看视频"**
→ Mode 1, `source_type=video`.

**"过去 3 天最重要的 10 条"**
→ Mode 1, `since_hours=72`, `limit=10`.

**"我想写一篇关于这条 Cursor blog 的文章"** (after user picks #3)
→ Mode 2 → `GET /research/entry/{id_of_3}` → WebFetch `url_original` → draft following zh writing style.

**"what's new today"**
→ Mode 1, `since_hours=24` (same as Chinese equivalent above).

**"draft a post on the OpenAI release"**
→ Mode 1 with broad filter to find the item → present list → once user confirms, Mode 2 + WebFetch + draft.

**"看看最近有没有关于 Claude 工具调用的文章"**
→ Mode 1, `since_hours=72`, filter display by keyword "tool" / "工具" in title; ask user to pick.

**"今天 AI 圈有什么新闻"**
→ Mode 3, `since_hours=24`. Scan headlines, surface clusters of multiple sources covering the same event.

**"What's trending in AI right now"**
→ Mode 3, `since_hours=24` or `72`. Same as above.

**"只看 Hacker News 的"**
→ Mode 3, `source_id=hn-front`.

---

## What this skill does NOT do

- Does not write the blog post automatically — the user always picks which item to write about first.
- Does not fetch full article bodies in Mode 1 — only calls WebFetch on `url_original` after the user selects a specific entry (Mode 2).
- Does not modify the research pipeline (no publish/reject/score override). For pipeline tuning, edit the backend Worker repo directly.
- Does not support `source_type=podcast` — only `article` and `video` are valid in Phase A.
- Does not push or publish to Substack/X — use the `publish-substack-article` or `promote-post` skill for that.

---

## Errors and troubleshooting

| Error | Likely cause | Action |
|---|---|---|
| `401 Unauthorized` | Wrong or expired token | Check `VSW_RESEARCH_API_TOKEN`. If compromised, rotate the secret on the Worker (Cloudflare Dashboard → Workers → Settings → Variables). |
| `404` on `/research/entry/:id` | Item was `filtered_out` — only `filtered_in` rows are returned by the API | Show the user the title from the list and ask: "这条被过滤掉了，API 里没有全文。想直接用原始链接 `{url_original}` 继续吗？" |
| `entries: []` (empty list) | `since_hours` too narrow, cron hasn't run yet, or `min_importance` too high | Suggest: "试试扩大时间窗口（如 `since_hours=72`）或降低 `min_importance` 到 2？" |
| `400 Bad Request` on `source_type` | Invalid value passed | Only `article` or `video` are accepted. Correct and retry. |
| WebFetch fails on `url_original` | Page behind paywall / JS-rendered / requires auth | Inform the user; fall back to `raw_content` snippet for a lighter draft, noting coverage is limited. |
