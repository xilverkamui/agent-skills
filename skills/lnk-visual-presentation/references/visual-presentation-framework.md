# Visual Presentation Framework

**Purpose:** Design rules for generating presentation slides as high-resolution images.

---

## 1. Scope and Priority

Follow this priority order:

1. The user's explicit instruction for the current slide
2. This framework
3. Reference material provided for the current task
4. General visual design principles

A slide-specific instruction may override a rule for that slide only. Two things are never overridden by Claude's own judgment: the reserved zones (Section 3) and the prohibited elements (Section 5).

---

## 2. Design Principles

Slides should feel clean, modern, minimal, professional, structured, highly legible, restrained, and generous in whitespace.

**Core principle: Less decoration, more visual clarity.**

Every visual element must contribute to comprehension, hierarchy, or meaning. Do not fill whitespace to make a slide look fuller. A slide may only contain what the user supplied or asked for. Do not add elements to make it look more "finished".

---

## 3. Locked Canvas and Geometry

Positions are percentages of the canvas (x = from the left edge, y = from the top edge). Pixel values assume a 2560 × 1440 canvas and are for orientation only.

### Canvas

- 16:9 widescreen. Do not crop, stretch, or distort.
- Background: solid flat white `#FFFFFF`. Nothing behind the content: no image, texture, pattern, gradient, glow, or tint.

### Left Blue Gutter

- Solid `#1EA7F2`, flush with the far-left edge, full canvas height.
- Width: **1.5% of canvas width** (about 38 px). It must be clearly visible.
- Flat: no gradient, shadow, border, rounded edge, transparency, or pattern.
- Same width on every slide in a deck.

### Margins and Content Area

- Content starts at x = 5% and ends at x = 97%. It must never touch or crowd the gutter.
- Content area runs from y = 20% to y = 92% (except where a reserved zone applies).

### Title Band

- The title sits in the top band: the top of the title block at about y = 4%, and a one-line title centered in the band y = 4% to 14%.
- Title text must end at x = 78% or earlier. It never enters the top-right reserved zone.
- Prefer a **short one-line title** (as a rule of thumb, up to about 40 characters). Refine the wording first. A **two-line title is acceptable** when one line would be unclear or too long; the second line still stays left of x = 78% and above the content area.
- An optional subtitle goes directly below the title, in muted gray, one line.

### Top-Right Reserved Zone

- Rectangle: x = 80% to 100%, y = 0% to 16%.
- Must be **plain empty white canvas**: no text, shape, line, box, outline, icon, label, mark, or placeholder.
- Purpose: the user places a logo there after generation, aligned with the title. Do not draw anything that suggests the slot.

### Bottom-Right Reserved Zone

- Rectangle: x = 80% to 100%, y = 88% to 100%.
- Must be plain empty white canvas, same rule as above. Content in the right-hand column ends above y = 88%.

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
- Title in bold deep navy. Secondary information in muted gray. A single accent-colored word in the title is allowed when it emphasizes the message.

### Components

Use cards, KPI blocks, charts, diagrams, tables, labels, dividers, and callouts only when they improve comprehension.

- Cards: light surface fill, optional 1 px `#D7E4E9` border, small corner radius, no heavy shadow.
- Keep component styling consistent within the slide and across the deck.

### Illustration and Icons

- Default: no illustration. Use one main illustration only when it clearly improves understanding.
- Simple monoline icons (navy or one accent color) are allowed when separate concepts benefit from differentiation. Do not give every point an icon by default.
- Any illustration is clean, professional, flat vector. Never photorealistic. Keep one consistent style across the deck.

### Data

When meaningful numbers are present, prefer a suitable representation: KPI hierarchy, comparison, trend, chart, ranked list, scorecard, or compact table. Small sparklines and simple charts are fine. Charts must be readable, restrained, accurately labeled, and proportionally meaningful. Never fabricate or estimate missing values.

---

## 5. Prohibited Elements

These must not appear unless the user explicitly asks for that exact element on that slide.

- Photographs or photorealistic imagery of any subject: people, products, food, ingredients, objects, buildings, landscapes, stock imagery.
- Background images, textures, patterns, gradients, glows, blur, vignettes, or lighting effects.
- Decorative shapes: waves, swooshes, curves, corner ornaments, ribbons, blobs, or abstract graphics.
- Logos, brand marks, watermarks, or company names that were not part of the supplied slide text. Logos are never generated at all.
- Headers, footers, running titles, section tags, taglines, page or slide numbers, dates, and confidentiality labels that were not supplied.
- Placeholder boxes, "logo here" markers, empty frames, or outlines of any kind.
- Heavy drop shadows, 3D effects, or excessive borders.
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

## 9. Final Quality Check

Inspect the generated image and verify:

**Locked rules**
- The left gutter is visible, flat, full height, and about 1.5% wide.
- The background is plain flat white, with no image, texture, gradient, glow, or decorative shape anywhere.
- The top-right zone is completely empty: no text, logo, box, line, or placeholder.
- The bottom-right zone is completely empty.
- The title is in the top band, one short line (or two when needed), and ends before the top-right zone.
- No logo, header, footer, slide number, tagline, or other element that was not supplied.
- No photographic or photorealistic imagery.

**Quality**
- The main message is immediately clear and the slide is easy to scan.
- Hierarchy and alignment are intentional, and whitespace is deliberate.
- Text matches the supplied wording exactly: no typos, missing words, or garbled characters.
- Numbers match the source. Nothing was invented.
- Colors are meaningful rather than decorative. Nothing is clipped, distorted, or crowded.

If a locked rule fails, regenerate with a targeted correction before delivering.

---

## 10. Default Output

Unless the user specifies otherwise: high-resolution PNG, 16:9 (2560 × 1440 if the tool supports it, otherwise the highest 16:9 size available), optimized for insertion into presentation software, with crisp typography and clean edges.
