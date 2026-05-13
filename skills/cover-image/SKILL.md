---
name: cover-image
description: Generate elegant cover images for articles. Analyzes content and creates eye-catching hand-drawn style cover images with multiple style and composition options. Use when user asks to "generate cover image", "create article cover", or "make a cover for article".
---

# Cover Image Generator

Generate hand-drawn style cover images for articles with rich style and composition options.

## Usage

```bash
# From markdown file (auto-select style based on content)
/cover-image path/to/article.md

# Specify a style
/cover-image path/to/article.md --style tech
/cover-image path/to/article.md --style gradient

# Specify a composition
/cover-image path/to/article.md --composition hero-center

# Without title text
/cover-image path/to/article.md --no-title

# Combine options
/cover-image path/to/article.md --style editorial --composition split --no-title

# From direct text input
/cover-image
[paste content or describe the topic]
```

## Options

| Option | Description |
|--------|-------------|
| `--style <name>` | Specify cover style (see Style Gallery below) |
| `--composition <name>` | Specify layout composition (see Composition Gallery below) |
| `--no-title` | Generate cover without title text (visual only) |

## Style Gallery

### Core Styles

| Style | Description | Best For |
|-------|-------------|----------|
| `elegant` (Default) | Refined, sophisticated, understated | Business, thought leadership, professional |
| `tech` | Modern, clean, futuristic with glow effects | AI, coding, digital, algorithms |
| `warm` | Friendly, approachable, human-centered | Personal growth, lifestyle, education |
| `bold` | High contrast, attention-grabbing, energetic | Opinion pieces, controversial, urgent |
| `minimal` | Ultra-clean, zen-like, maximum whitespace | Philosophy, focus, essentialism |
| `playful` | Fun, creative, whimsical doodles | Tutorials, beginner guides, casual |
| `nature` | Organic, calm, earthy tones | Sustainability, wellness, outdoor |
| `retro` | Vintage, nostalgic, aged textures | History, retrospectives, classic topics |

### Extended Styles

| Style | Description | Best For |
|-------|-------------|----------|
| `gradient` | Smooth color transitions, dreamy, modern | Product launches, announcements, branding |
| `editorial` | Magazine-quality, sophisticated typography | Long-form essays, deep dives, journalism |
| `blueprint` | Technical drawing aesthetic, grid paper | Architecture, system design, engineering |
| `watercolor` | Soft washes, organic bleed, painterly | Art, culture, creative writing, poetry |
| `geometric` | Sharp shapes, tessellations, mathematical | Data science, math, structured thinking |
| `neon` | Dark background with vivid glowing elements | Nightlife, gaming, cyberpunk, startup |
| `paper-cut` | Layered paper cutout depth effect | Storytelling, children's content, craft |
| `ink-wash` | East Asian brush ink aesthetic (水墨风) | Chinese culture, philosophy, calligraphy |

Detailed style definitions: `references/styles/<style>.md`

## Composition Gallery

Compositions define how elements are arranged in the cover image.

| Composition | Description | When to Use |
|-------------|-------------|-------------|
| `hero-center` (Default) | Single focal visual centered, title above or below | General purpose, strong single concept |
| `split` | Left/right or top/bottom split, visual one side, text other | Comparison, before/after, dual concepts |
| `floating` | Elements scattered with depth, floating in space | Abstract topics, multiple related concepts |
| `frame` | Decorative border framing the central content | Formal, announcement, certificate-like |
| `diagonal` | Dynamic diagonal division or flow | Movement, progress, transformation |
| `spotlight` | Dark background with a single illuminated subject | Focus, highlight, key insight |
| `panoramic` | Wide scene spanning the full width | Landscape, journey, timeline |
| `mosaic` | Grid of small related visuals forming a bigger picture | Collection, variety, ecosystem |
| `vignette` | Soft fade from edges to center focus | Intimate, personal, memoir-style |
| `layered` | Overlapping planes creating depth | Complex topics, multi-layered ideas |

### Composition Tips

- **hero-center** + title: Place visual slightly left, title right
- **hero-center** + no-title: Center the visual fully, let it breathe
- **split**: Use contrasting colors or concepts on each side
- **floating**: 3-5 elements max, vary sizes for depth
- **diagonal**: Direction implies progress (bottom-left → top-right = growth)
- **spotlight**: Keep background very dark, subject vivid
- **mosaic**: Use 4-9 tiles, maintain consistent style across tiles
- **layered**: Use opacity/blur to create foreground/background separation

## Auto Style Selection

When no `--style` is specified, analyze content to select the best style:

| Content Signals | Selected Style |
|----------------|----------------|
| AI, coding, tech, digital, algorithm, API | `tech` |
| Personal story, emotion, growth, life, journey | `warm` |
| Controversial, urgent, must-read, warning, breaking | `bold` |
| Simple, zen, focus, essential, less is more | `minimal` |
| Fun, easy, beginner, casual, tutorial, step-by-step | `playful` |
| Nature, eco, wellness, health, organic, outdoor | `nature` |
| History, classic, vintage, old, traditional | `retro` |
| Product, launch, release, announcement, brand | `gradient` |
| Essay, analysis, deep dive, investigation, review | `editorial` |
| System design, architecture, blueprint, infrastructure | `blueprint` |
| Art, painting, creative, poetry, culture | `watercolor` |
| Data, math, statistics, geometry, patterns | `geometric` |
| Gaming, startup, nightlife, crypto, hacker | `neon` |
| Story, folktale, illustration, craft, children | `paper-cut` |
| 中国, 文化, 哲学, 书法, 国风, 传统 | `ink-wash` |
| Business, professional, strategy, analysis (default) | `elegant` |

## Auto Composition Selection

When no `--composition` is specified:

| Condition | Selected Composition |
|-----------|---------------------|
| Single strong concept/metaphor | `hero-center` |
| Article compares two things | `split` |
| Article covers multiple tools/ideas | `floating` or `mosaic` |
| Personal/intimate topic | `vignette` |
| Journey/timeline/progress narrative | `diagonal` or `panoramic` |
| One key insight or revelation | `spotlight` |
| Complex multi-layered topic | `layered` |
| Formal/announcement tone | `frame` |

## File Management

### With Article Path

Save to `imgs/` subdirectory in the same folder as the article:

```
path/to/
├── article.md
└── imgs/
    ├── prompts/
    │   └── cover.md
    └── cover.png
```

### Without Article Path

Save to current working directory:

```
./
├── cover-prompt.md
└── cover.png
```

## Workflow

### Step 1: Analyze Content

Extract key information:
- **Main topic**: What is the article about?
- **Core message**: What's the key takeaway?
- **Tone**: Serious, playful, inspiring, educational?
- **Keywords**: Identify style-signaling words
- **Structure**: Is it a comparison? A journey? A deep dive?
- **Visual metaphors**: What real-world objects/scenes represent the topic?

### Step 2: Select Style & Composition

If `--style` or `--composition` specified, use those. Otherwise:
1. Scan content for style and composition signals
2. Match signals to most appropriate style + composition
3. Default to `elegant` style + `hero-center` composition if no clear signals

### Step 3: Generate Cover Concept

**Title** (if included, max 8 characters):
- Distill the core message into a punchy headline
- Use hooks: numbers, questions, contrasts, pain points
- Skip if `--no-title` flag is used

**Visual Elements**:
- Style-appropriate imagery and icons
- 1-2 symbolic elements representing the topic
- Metaphors or analogies that fit the style

**Composition Layout**:
- Apply the selected composition template
- Consider title placement within the composition
- Ensure visual hierarchy: primary element > secondary > decorative

### Step 4: Create Prompt File

**Prompt Format**:

```markdown
Cover theme: [topic in 2-3 words]
Style: [selected style name]
Composition: [selected composition name]

[If title included:]
Title text: [8 characters or less, in content language]
Subtitle: [optional, in content language]

Visual composition:
- Main visual: [description matching style]
- Layout: [composition-specific layout description]
- Primary element: [what draws the eye first]
- Secondary elements: [supporting visuals]
- Decorative elements: [style-appropriate accents]

Color scheme:
- Primary: [style primary color]
- Background: [style background color]
- Accent: [style accent color]

Style notes: [specific style characteristics to emphasize]
Composition notes: [specific layout guidance]

[If no title:]
Note: No title text, pure visual illustration only.
```

### Step 5: Generate Image

**Image Generation Skill Selection**:
1. Check available image generation skills
2. If multiple skills available, ask user to choose

**Generation**:
Call selected image generation skill with prompt file and output path.

### Step 6: Output Summary

```
Cover Image Generated!

Topic: [topic]
Style: [style name]
Composition: [composition name]
Title: [cover title] (or "No title - visual only")
Location: [output path]

Preview the image to verify it matches your expectations.
```

## Notes

- Cover should be instantly understandable at small preview sizes
- Title (if included) must be readable and impactful
- Visual metaphors work better than literal representations
- Maintain style consistency throughout the cover
- Image generation typically takes 10-30 seconds
- Title text language should match content language
- When in doubt, `elegant` + `hero-center` is a safe default
- Combine unexpected style+composition pairs for unique results (e.g., `ink-wash` + `split`)
