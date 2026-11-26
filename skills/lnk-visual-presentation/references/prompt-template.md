# Prompt Template

How to turn a slide into an image-generation prompt, and how to correct the result.

Image generators tend to add things that look polished (backgrounds, logos, headers, decorative waves) and to ignore rules that are vague or buried. So: put exact positions in the prompt, put the exact text in the prompt, describe empty zones as empty, and put the prohibitions at the end.

## Assembly order

1. Canvas
2. Layout map
3. Exact text
4. Visual elements
5. Style
6. Empty zones
7. Prohibitions

## Template

Replace the bracketed parts. Keep every other line as written.

```
Create one 16:9 widescreen presentation slide, [2560x1440] px if supported.
Background: solid flat white (#FFFFFF), nothing behind the content.

LAYOUT (percent of slide width x height)
- Left gutter: solid flat #1EA7F2 vertical bar, flush with the left edge, full height, 1.5% of slide width. No gradient, shadow, or border.
- Title: top-left, starting at x=5%, top of text at y=4%. [One line / Two lines]. Text must end before x=78%.
- [Subtitle: one muted gray line directly below the title.]
- Content area: x=5% to 97%, y=20% to 92%: [describe layout: e.g. "four KPI cards in a 2x2 grid on the left 60%, three takeaway rows on the right 35%"].

EXACT TEXT (render exactly as written, do not rewrite, translate, add, or omit)
Title: "[title]"
[Subtitle: "[subtitle]"]
[Group 1 label]: "[text]"
[Group 2 label]: "[text]"
[Source line, bottom-left, small, muted gray: "[text]"]

VISUAL ELEMENTS
- [Cards: light tinted surface, small corner radius, no heavy shadow.]
- [Chart or sparkline: type, series, labels. Use only the supplied values.]
- [Icons: simple monoline, navy, only on ...] or "No icons or illustrations."

STYLE
Clean, modern, minimal, professional. One sans-serif family (Inter / Segoe UI style). Title bold deep navy #082F43 at about 6% of slide height; body 2.2-2.5%; supporting text not below 1.8%. Palette: blue #1EA7F2, navy #082F43, green #00B58B, purple #6F52C7, orange #F6A623, alert red #D64545 (only for negative values), muted gray #96A7AE, dividers #D7E4E9. Generous whitespace.

EMPTY ZONES
- The rectangle x=80% to 100%, y=0% to 16% is pure empty white. Leave it blank; it is filled in later in another tool.
- The rectangle x=80% to 100%, y=88% to 100% is pure empty white. Leave it blank.
Nothing is drawn in either rectangle: no text, shapes, lines, boxes, outlines, or marks.

DO NOT
No photographs or photorealistic images of any kind. No background image, texture, gradient, glow, or blur. No decorative shapes such as waves, swooshes, or curves. No logos, brand marks, or watermarks. No header, footer, tagline, section tag, date, or slide number. No placeholder boxes. No text other than the exact text above.
```

Notes:
- Never write words like "logo here" or "placeholder" in the prompt. Describe the zones only as empty white.
- Do not paste the full framework into the prompt. Use the template wording.
- For a redesign of an existing slide image, attach the image and add: "Keep all content, wording, and numbers unchanged. Change only the visual design as specified."

## Correction loop

After generating, inspect against the Final Quality Check in `visual-presentation-framework.md`. If a locked rule failed, regenerate once with the same prompt plus a targeted correction, naming only what is wrong:

```
Keep everything else identical. Fix only this: [the specific problem].
```

Examples of the specific problem:

- "Remove the logo at the top-left. The slide has no logo."
- "The top-right rectangle (x=80% to 100%, y=0% to 16%) must be completely empty white. Remove everything inside it."
- "Remove the background image and the curved shape at the bottom. The background is plain flat white."
- "Move the title up so its top is at y=4% and shorten it to end before x=78%."
- "The left blue bar must be visible: solid #1EA7F2, 1.5% of slide width, full height."
- "Fix the text: [word] is misspelled, it should be '[word]'."

Use at most two corrective passes. If a deviation remains, deliver the best result and name the deviation in one line.
