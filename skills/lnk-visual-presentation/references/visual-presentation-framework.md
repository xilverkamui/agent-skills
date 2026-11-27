# Visual Presentation Framework

**Purpose:** Single source of truth for the design rules of generated presentation slides: geometry, title placement, reserved zones, visual language, illustration, prohibited elements, and the HARD/SOFT rule catalog with tolerances.

`SKILL.md` holds the workflow and failure handling. `prompt-template.md` holds the prompt wording. Neither repeats the rules below.

---

## 1. Scope and Priority

Follow this priority order:

1. The user's explicit instruction for the current slide (subject to the waiver policy below)
2. This framework
3. Content supplied for the current task (text, numbers, a reference slide image used as a content reference)
4. General visual design principles

### Waiver policy

Rules fall into three groups.

| Group | Rules | Can the user override it? |
| --- | --- | --- |
| **Layout contract** | Canvas, white background, left gutter, title placement, reserved zones (Section 3) | Only for one slide, and only when the user names the specific rule ("this slide may use a grey background"). A general request such as "make it more creative" is not a waiver. |
| **Content prohibitions** | The elements in Section 5, except the two items below | Only for one slide, and only when the user asks for that exact element ("add a photo of the product"). |
| **Never waived** | Generating a logo or brand mark; inventing data, sources, or conclusions | No. |

A waived rule is dropped from the Quality Gate (Section 9) for that slide only, and nothing else about the slide changes. Every other rule still applies. A waiver never carries over to other slides or to later requests.

---

## 2. Design Principles

Slides should feel clean, modern, minimal, professional, structured, highly legible, restrained, and generous in whitespace.

**Core principle: Less decoration, more visual clarity.**

Every visual element must contribute to comprehension, hierarchy, or meaning. Do not fill whitespace to make a slide look fuller. A slide contains only what the user supplied or asked for. Do not add elements to make it look more "finished".

---

## 3. Locked Canvas and Geometry

Positions are percentages of the canvas: X from the left edge, Y from the top edge. Pixel values assume 2560 × 1440 and are for orientation only.

The values below are **targets**. Section 9 gives the **accepted ranges** used when inspecting a result. Prompts always use the targets.

### Canvas

- 16:9 widescreen. Do not crop, stretch, or distort.
- Default resolution 2560 × 1440 when supported, otherwise the highest 16:9 size available.
- Background: solid flat white `#FFFFFF`. Nothing behind the content: no image, pattern, texture, gradient, glow, or tint.

### Left Blue Gutter

- Solid `#1EA7F2`, flush with the far-left edge, full canvas height.
- Width: **1.5% of canvas width** (about 38 px). It must be clearly visible.
- Flat: no gradient, shadow, border, rounded edge, transparency, or pattern.
- Same width on every slide in a deck.

### Content Margins

- Main content starts at X = 5% and ends at X = 97%. It never touches or crowds the gutter.
- Content ends at Y = 92%, except where a reserved zone applies.

### Title Placement

- The main title is the **first visible text element** on the slide.
- The top of the title text sits at about **Y = 4%**.
- The title starts at **X = 5%** and ends before **X = 78%**.
- Prefer a **short one-line title** (rule of thumb: up to about 40 characters). Refine the wording first. A **two-line title** is allowed only when one line would be unclear or too long. Both lines stay left of X = 78%.
- An optional subtitle goes directly below the title: one line, muted gray, also ending before X = 78%.
- Nothing is placed above the title: no section label, eyebrow, header, tag, or decorative text. A section number or label from supplied content goes into the subtitle or is dropped.
- The title is never moved downward to make room for secondary information. When space is short, the content region moves down or shrinks instead.
- Title alignment, size, weight, and color are identical on every slide in a deck.

### Content Region

- Starts below the title block (title plus optional subtitle), with about 2% of clearance.
- Normally starts near Y = 20%. A two-line title with a subtitle may push the start down to about Y = 25%. That is the only reason the start moves.

### Top-Right Reserved Zone

- Rectangle: X = 80% to 100%, Y = 0% to 16%.
- Must be **completely empty white canvas**: no text, icon, logo, line, shape, border, outline, box, or placeholder.
- Purpose: the user places a logo there after generation, aligned with the title. Do not draw anything that suggests the slot.

### Bottom-Right Reserved Zone

- Rectangle: X = 80% to 100%, Y = 88% to 100%.
- Completely empty white canvas, same rule as above. Right-hand content ends above Y = 88%.

---

## 4. Visual Language

### Color

| Role | Color |
| --- | --- |
| Primary blue / gutter | `#1EA7F2` |
| Deep navy / primary text | `#082F43` |
| Green | `#00B58B` |
| Purple | `#6F52C7` |
| Orange | `#F6A623` |
| Alert red (negative values, decline, risk only) | `#D64545` |
| Muted gray | `#96A7AE` |
| Divider / border | `#D7E4E9` |
| Light neutral surface | `#F7FAFB` |
| Light blue surface | `#EAF7FD` |
| Light orange surface | `#FFF8ED` |
| White surface | `#FFFFFF` |

- A light tint of any accent (about 8–12% on white) may be used as a card surface when it signals a category or state, for example green for improvement or red for decline.
- Use accent colors only to communicate hierarchy, category, state, or data distinction. Never as decoration.

### Typography

- One clean modern sans-serif family for the whole slide (Inter or Segoe UI style).
- Hierarchy: slide title, then section heading or primary message, then body, then supporting information.
- Approximate sizes relative to canvas height: title 6%, section heading 3%, body 2.2–2.5%, supporting text not below 1.8%.
- Title in bold deep navy. Secondary information in muted gray. One accent-colored word in the title is allowed when it emphasizes the message.

### Components

Use cards, KPI blocks, charts, diagrams, tables, labels, dividers, and callouts only when they improve comprehension.

- Cards: light surface fill, optional 1 px `#D7E4E9` border, small corner radius, no heavy shadow.
- Keep component styling consistent within the slide and across the deck.

### Illustration

Use an illustration only when it improves comprehension. It must communicate the message, not fill whitespace.

- **Allowed styles:** clean flat vector, professional editorial illustration, polished isometric illustration, restrained 2.5D vector illustration.
- Restrained corporate palette, based on Section 4 colors. Quality and style are consistent across slides in a deck.
- One major illustration per slide, unless several visuals are needed to understand the content.
- Keep it inside the content region. It never enters a reserved zone or the title block.
- **Separation from the canvas:** the illustration separates itself through its own contrast and outlines, or sits on a light tint panel (Section 4 surfaces). Do not separate it with blobs, glows, halos, gradient backdrops, or heavy shadows.
- Soft flat shading and subtle tonal variation inside the illustration are fine. The gradient and glow ban in Section 5 applies to the canvas and to decoration, not to shading within an illustration.
- When redesigning an existing slide, keep the illustration concept the user already chose.
- Never photorealistic. No stock photography, realistic human renders, photographic textures, motion blur, or dramatic lighting.

### Icons

Simple monoline icons (navy or one accent color) are allowed when separate concepts benefit from differentiation. Do not give every point an icon by default.

### Data

When meaningful numbers are present, prefer a suitable representation: KPI hierarchy, comparison, trend, chart, ranked list, scorecard, or compact table. Small sparklines and simple charts are fine. Charts must be readable, restrained, accurately labeled, and proportionally meaningful. Never fabricate or estimate missing values.

---

## 5. Prohibited Elements

Unless a waiver under Section 1 applies, none of these may appear.

- Photographs or photorealistic imagery of any subject: people, products, food, ingredients, objects, buildings, landscapes, stock imagery. Realistic human renders and photographic textures count as photorealistic.
- Background images, textures, patterns, gradients, glows, blur, vignettes, or lighting effects on the canvas, plus motion blur and dramatic lighting anywhere.
- Decorative shapes: waves, swooshes, curves, corner ornaments, ribbons, blobs, or abstract graphics.
- Logos and brand marks. They are never generated, even on request. A company name that appears in the supplied slide text may be rendered as plain text.
- Headers, footers, running titles, section tags, taglines, page or slide numbers, dates, and confidentiality labels that were not supplied.
- Placeholder boxes, "logo here" markers, empty frames, or outlines of any kind.
- Heavy drop shadows and glossy or 3D-rendered effects. Restrained isometric and 2.5D illustration (Section 4) is not a 3D effect.
- Invented facts, metrics, claims, sources, or causal relationships.

A source or footnote line is allowed only when its text is supplied. It sits bottom-left, small and muted gray, outside the bottom-right reserved zone.

---

## 6. Content and Hierarchy

Light editorial refinement is allowed: shorten wording, remove repetition, group related information, improve headings, and convert prose into clearer visual structures. Preserve meaning, numbers, scope, qualifiers, and limitations. Do not translate; keep the slide text in the language supplied.

Use concise, direct, executive language.

As a strong default, organize a slide around about **3–5 main information groups** (a preference, not a hard limit).

Establish a clear hierarchy: main message, primary evidence, supporting explanation, secondary detail. Do not give equal visual weight to everything.

---

## 7. Layout Selection

Choose the composition from the content rather than a fixed template. Possible structures: single-message, two- or three-column, KPI plus explanation, chart plus insight, comparison, process or flow, matrix, structured data, mixed editorial.

**Consistency means shared visual language, not identical layouts.** Use a disciplined grid, shared alignment axes, consistent spacing, and deliberate whitespace. Use the minimum visuals needed to make the message immediately understandable.

---

## 8. Multi-Slide Consistency

Keep identical across the deck: the Section 3 geometry, color system, typography hierarchy, title treatment, spacing rhythm, illustration style, and editorial tone. Allow layout, chart type, card arrangement, and emphasis to adapt to each slide's content.

---

## 9. Quality Gate: HARD and SOFT Rules

This section is the catalog. `SKILL.md` describes when and how to run it.

How each rule is checked: **[M]** can be measured by `scripts/validate_slide.py`, **[V]** needs visual inspection by the agent. A rule marked [M] still gets a visual look. A rule waived under Section 1 is skipped for that slide.

### Accepted ranges (inspection only)

Generators never hit pixel-exact values, and compression blurs edges. Judge a result against these ranges. Do not put the ranges in prompts.

| Item | Target | Accepted |
| --- | --- | --- |
| Aspect ratio | 16:9 | within 1% |
| Gutter width | 1.5% of width | 1.2% to 1.8% |
| Gutter color | `#1EA7F2` | each color channel within ±30 |
| Gutter continuity | full height | at least 98% of rows |
| Title top | Y = 4% | Y = 2% to 6% |
| Title start | X = 5% | X = 4% to 6% |
| Title end | before X = 78% | up to X = 79% |
| Reserved zones | empty white | at least 99.5% of pixels near white (each channel 245 or higher) |

### HARD rules (mandatory)

| # | Rule | Check |
| --- | --- | --- |
| 1 | Canvas is 16:9 | [M] |
| 2 | Background is solid white `#FFFFFF`, with no image, texture, gradient, or glow | [M] on unobstructed edge areas, [V] overall |
| 3 | Left gutter is visible, full height, and 1.5% wide (accepted range above) | [M] |
| 4 | Gutter color is `#1EA7F2` | [M] |
| 5 | Top-right reserved zone is completely empty | [M] |
| 6 | Bottom-right reserved zone is completely empty | [M] |
| 7 | Main title is the first visible text, within the title placement targets, with nothing above it | [V], partly [M] (advisory) |
| 8 | Title does not enter the top-right reserved zone and ends before X = 78% | [M] (title row clearance), [V] |
| 9 | No logo or brand mark appears | [V] |
| 10 | No prohibited element from Section 5 appears | [V] |
| 11 | Every displayed number matches the source | [V] |
| 12 | All text is accurate, free of spelling errors, and large enough to read (supporting text not below 1.8% of height) | [V] |
| 13 | Nothing is clipped, overlapping, or distorted | [V] |

### SOFT rules (judged after all hard rules pass; adjust to the content)

- Visual balance
- Illustration quality (also whether it improves understanding)
- Readability optimization (comfortable sizes, contrast, line length)
- Information density
- Alignment
- Whitespace
- Composition
- Visual hierarchy and whether the main message is immediately clear
- Consistency with other slides in the deck

A soft-rule issue never triggers regeneration by itself (see `SKILL.md`).

---

## 10. Default Output

Unless the user specifies otherwise: high-resolution PNG, 16:9 (2560 × 1440 if the tool supports it, otherwise the highest 16:9 size available), optimized for insertion into presentation software, with crisp typography and clean edges.
