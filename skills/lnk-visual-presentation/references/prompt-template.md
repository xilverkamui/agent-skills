# Prompt Template

How to turn a slide into an image-generation prompt, how to prompt when a reference slide is given, and how to word a correction.

Design rules, targets, and accepted ranges live in `visual-presentation-framework.md`. This file only gives the prompt structure and wording. Prompts use the **targets** from the framework, never the accepted ranges.

Image generators tend to add things that look polished (backgrounds, logos, headers, decorative waves) and to ignore rules that are vague or buried. So: give exact positions, give the exact text, describe empty zones as empty, and put the prohibitions last.

## Required order

1. Canvas specification
2. Exact layout coordinates
3. Exact slide wording
4. Content hierarchy
5. Charts, diagrams, and illustrations
6. Typography and color palette
7. Mandatory empty zones
8. Prohibited elements (always last)

## Must appear in every prompt

- Solid white canvas
- Full-height blue gutter at X = 0–1.5%
- Main title at X = 5%, Y = 4%, ending before X = 78%, and it is the first text on the slide
- Main content region starting below the title
- Empty top-right zone
- Empty bottom-right zone
- No logos or brand marks
- No photographic or decorative backgrounds
- No invented data or unsupported conclusions

## Template

Replace the bracketed parts. Keep every other line as written. Leave out a bracketed line that does not apply.

```
1. CANVAS
Create one 16:9 widescreen presentation slide, [2560x1440] px if supported.
Background: solid flat white (#FFFFFF), nothing behind the content.

2. LAYOUT (percent of slide width x height)
- Left gutter: solid flat #1EA7F2 vertical bar at X=0% to 1.5%, flush with the left edge, full slide height. No gradient, shadow, or border.
- Main title: the first text on the slide. Top of the text at Y=4%, starting at X=5%, ending before X=78%. [One line / Two lines]. Nothing is placed above it.
- [Subtitle: one muted gray line directly below the title, also ending before X=78%.]
- Main content region: starts below the title [at about Y=20%] and runs from X=5% to X=97%, down to Y=92%: [describe the layout, e.g. "four KPI cards in a 2x2 grid on the left 60%, three takeaway rows on the right 35%"].

3. EXACT TEXT (render exactly as written; do not rewrite, translate, add, or omit)
Title: "[title]"
[Subtitle: "[subtitle]"]
[Group 1 label]: "[text]"
[Group 2 label]: "[text]"
[Source line, bottom-left, small, muted gray: "[text]"]

4. CONTENT HIERARCHY
- Primary: [the main message or key number]
- Supporting: [explanations, comparisons]
- Secondary: [notes, sources]

5. CHARTS, DIAGRAMS, AND ILLUSTRATIONS
- [Chart or sparkline: type, series, labels. Use only the supplied values.]
- [Illustration: concept, style (clean flat vector / editorial / polished isometric / restrained 2.5D), position inside the content region, one major illustration only. It separates itself by its own contrast or a light tint panel, with no glow, halo, or blob behind it.]
- [Icons: simple monoline, navy, only on ...] or "No icons or illustrations."

6. TYPOGRAPHY AND COLOR
One sans-serif family (Inter / Segoe UI style). Title bold deep navy #082F43 at about 6% of slide height; section headings about 3%; body 2.2-2.5%; supporting text not below 1.8%. Palette: blue #1EA7F2, navy #082F43, green #00B58B, purple #6F52C7, orange #F6A623, alert red #D64545 (only for negative values), muted gray #96A7AE, dividers #D7E4E9, light tinted card surfaces. Clean, modern, minimal, generous whitespace.

7. MANDATORY EMPTY ZONES
- The rectangle X=80% to 100%, Y=0% to 16% is pure empty white. Leave it blank; it is filled in later in another tool.
- The rectangle X=80% to 100%, Y=88% to 100% is pure empty white. Leave it blank.
Nothing is drawn in either rectangle: no text, icon, shape, line, box, outline, or mark.

8. PROHIBITED (applies to the whole image)
No photographs or photorealistic images of any kind. No background image, texture, gradient, glow, or blur. No decorative shapes such as waves, swooshes, or curves. No logos or brand marks. No header, footer, tagline, section label above the title, date, or slide number. No placeholder boxes. No text other than the exact text above. No invented data or unsupported conclusions.
```

Notes:
- Never write "logo here" or "placeholder" in the prompt. Describe the zones only as empty white.
- Do not paste the full framework into the prompt. Use the template wording.
- When a waiver applies (framework Section 1), change only the waived line and leave the rest as written.

## When a reference slide image is provided

A reference image is a **content reference**, not a style reference.

**Default: do not attach it to the generation request.** Transcribe from it: the main message, title and supporting wording, numbers, the information hierarchy, key takeaways, and a one-sentence description of the illustration concept. Put these into sections 3 to 5 of the template. Attached images are the strongest style signal a generator receives, and attaching the old slide brings back its background, header, logo, and layout.

If a number or word in the image cannot be read with confidence, ask the user. Do not guess.

Handle elements of the old slide this way:

| In the old slide | In the new prompt |
| --- | --- |
| Eyebrow or section number above the title | Drop it, or move it into the subtitle |
| Logo, header, footer, slide number | Drop it |
| Background image, wave, glow, decorative shape | Drop it |
| Gutter or margins that differ from the framework | Use the framework values |
| Illustration the user wants to keep | See below |
| Colors that differ from the palette | Use the framework palette |

**Keeping an illustration.** Attach the image only when the user wants that exact illustration preserved and it cannot be described in words. Then add this block directly after the template's section 5:

```
REFERENCE IMAGE (attached) - use it ONLY for: [the illustration of ... / the chart style of ...].
Preserve: [illustration concept, wording, numbers, information hierarchy].
Ignore everything else in it: its background, layout, title position, gutter, logo, header, footer, decorative shapes, and colors.
All layout, geometry, typography, color, empty zones, and prohibitions in this prompt override the reference image.
```

**Editing an existing slide the user wants adjusted** (not rebuilt): attach it and state both lists:

```
Preserve unchanged: [content to keep, e.g. all wording and numbers].
Change: [what the user asked for].
These design rules override the reference image: [list the rules the old image breaks, e.g. gutter 1.5% wide, empty top-right zone, title at X=5% Y=4%].
```

**Keep the original visual styling** only when the user asks for it explicitly and the framework allows it (framework Section 1). State the waived rule by name in the prompt.

## Correction wording

After inspecting the result (see `SKILL.md`), fix only a failed HARD rule. Name the exact problem. Prefer a targeted edit of the existing image when the tool supports editing. Otherwise regenerate with the same prompt plus the correction:

```
Keep everything else identical. Fix only this: [the specific problem].
```

Examples of the specific problem:

- "Remove the logo at the top-left. The slide has no logo."
- "The top-right rectangle (X=80% to 100%, Y=0% to 16%) must be completely empty white. Remove everything inside it."
- "Remove the background image and the curved shape at the bottom. The background is plain flat white."
- "Move the title up so its top is at Y=4% and it ends before X=78%. Nothing is above it."
- "The left blue bar must be visible: solid #1EA7F2, 1.5% of slide width, full height."
- "Fix the text: [word] is misspelled, it should be '[word]'."
- "The number [x] is wrong. It must read [y]."

Do not write a correction for a soft-rule preference such as balance, composition, or illustration taste.
