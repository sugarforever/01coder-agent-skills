---
name: promote-post
description: Write a promotional tweet for a published article. Takes a post URL (Substack, X Article, blog) and crafts a teaser tweet that opens the story and draws readers in — not a summary, but a hook that leads naturally into clicking the link. Use when user says "promote this post", "write a tweet for this article", "推广这篇文章", or provides a link and asks to write a promo tweet.
---

# Promote Post

Write a promotional tweet for a published article. The tweet is a teaser — it opens the story, not summarizes it.

## Core Philosophy

The article is a block of cheese. The tweet is also part of that same cheese — not a label on the packaging, not a description on the shelf. It's the first bite.

The tweet and the article should feel like one continuous piece. When a reader goes from the tweet to the article, the transition should be seamless — as if they were already inside the story and simply kept reading. There is no "In this article I talk about..." because that language creates a boundary between the tweet and the content. The tweet IS the content. It just happens to be the part that lives on the timeline.

A summary tells readers what the article says so they don't have to click. The tweet we want makes readers feel like the story has already started, and the link is where it continues. The reader should feel pulled forward, not informed.

## Workflow

### Step 1: Get the Article

The user provides a URL (Substack, X Article, blog post, or any published link).

- Use WebFetch (with `r.jina.ai` prefix if needed) to retrieve the full content
- Read carefully — understand the narrative arc, not just the key points
- Identify: What's the emotional core? What's the tension? What's the surprise or insight that makes this worth reading?

If the user provides a file path instead:
- Use Read to load the content
- Ask for the published URL to include in the tweet

### Step 2: Find the Hook

Look for one of these angles in the article:

- **A tension or contradiction** — something that creates curiosity ("X should work, but it doesn't. Here's why...")
- **A vivid scene or moment** — drop the reader into the middle of a situation
- **A surprising fact or framing** — something that makes you go "wait, really?"
- **A relatable feeling** — something the audience has experienced but hasn't articulated
- **A question the reader didn't know they had** — then imply the article answers it

Do NOT:
- List takeaways or bullet points
- Use any language that separates the tweet from the article — "In this article...", "I wrote about...", "Here's what I learned...", "Check out my post on..." — these all create a boundary. The tweet should read as if it IS the beginning of the piece, not a sign pointing at it
- Summarize the conclusion
- Give away the best insight (that's what the article is for)

### Step 3: Write the Tweet

Write 2-3 candidate tweets. Each should:

1. **Open mid-story** — start as if you're already talking about something, not introducing it
2. **Create forward momentum** — the reader should feel like clicking is the natural next step, not a separate decision
3. **End with the link** — placed naturally, as the continuation of the thought, not an afterthought
4. **Stay under 280 characters** (excluding the URL) for single tweets, or use a short thread (2-3 tweets max) if the hook needs room to breathe

#### Tone

- Conversational, not promotional
- Write like you're telling a friend about something interesting, not pitching
- No hype words ("game-changing", "must-read", "incredible")
- No hashtags unless the user requests them
- Match the language of the original article (Chinese article → Chinese tweet, English → English)

### Step 4: Present Candidates

Present 2-3 options clearly:

```
## Option 1

{tweet text}

{url}

## Option 2

{tweet text}

{url}

## Option 3

{tweet text}

{url}
```

Ask the user to pick one, tweak, or mix elements.

## Examples

### Example: Blog post about a technical topic

**Article**: A deep dive into how Claude Code's Telegram Channel plugin works — process model, tmux management, security.

**Bad tweet (summary style):**
> Claude Code now supports Telegram as a remote channel. Here's how to set it up: create a bot, install the plugin, pair your account, and use tmux to keep it running. Full guide here: {link}

**Good tweet (teaser style):**
> I set up Telegram to remote-control Claude Code on my machine. Sent a message from my phone, watched my laptop start editing files on its own.
>
> The setup is surprisingly simple — but there are a few things about tmux and security you'll want to get right.
>
> {link}

### Example: Personal essay

**Article**: A reflection on Sora being shut down and what it feels like to watch AI products come and go.

**Bad tweet (summary style):**
> Sora got shut down by OpenAI. I wrote about how AI products appear and disappear so fast, and how a trip to Barcelona reminded me that life goes on without AI. {link}

**Good tweet (teaser style):**
> Sora stopped. I barely used it — but hearing it was gone felt like running into someone stunning at a party, and by the time you turned around, they'd already left.
>
> {link}

### Example: Technical tutorial series

**Article**: A 3-part series about Sahil Lavingia's Claude Code skills for minimalist entrepreneurs.

**Bad tweet (summary style):**
> Sahil Lavingia turned The Minimalist Entrepreneur into 9 Claude Code skills. Part 1 covers finding your community, validating ideas, and building an MVP. Full breakdown: {link}

**Good tweet (teaser style):**
> The founder of Gumroad took his entire book on minimalist entrepreneurship and turned it into 9 slash commands for Claude Code.
>
> /find-community, /validate-idea, /pricing — each one is a structured thinking framework you can run in your terminal.
>
> I read through all of them: {link}

## Critical Rules

1. **Never summarize** — tease, don't tell
2. **Always include the link** — it's the destination, not an accessory
3. **Match source language** — Chinese article → Chinese tweet
4. **No auto-publishing** — only generate text, never post
5. **Multiple candidates** — always offer 2-3 options
6. **No hashtags by default** — add only if user requests
