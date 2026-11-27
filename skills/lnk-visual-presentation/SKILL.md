---
name: lnk-visual-presentation
description: Generate presentation slides as polished, high-resolution 16:9 PNG images using a fixed visual framework (flat white canvas, narrow blue left gutter, title at a fixed top position, reserved empty top-right and bottom-right zones, restrained palette, no decorative backgrounds), then check the result against hard layout rules before delivery. Use whenever the user asks to create, generate, redraw, redesign, or visually improve a presentation slide as an image, or to rebuild an existing slide image in the standard style, even if they do not mention the framework. Do not use for PPTX generation, storyline or outline development, speaker notes, or content-only critique.
license: MIT
compatibility: Needs an agent with image-generation capability. The optional scripts/validate_slide.py needs Python 3 with Pillow and access to the generated image file; without them the checks are done by visual inspection only.
metadata:
  author: Eriyanto Wibowo
  version: "1.1.0"
  last_updated: "2026-11-27"
---

# Visual Presentation

Skill version: 1.1.0 (see CHANGELOG.md for history)

## Purpose

Generate presentation-slide images that follow one consistent, restrained visual framework, and verify them before delivery.

Read these before generating:

- `references/visual-presentation-framework.md` is the single source of truth for design rules: geometry, title placement, reserved zones, palette, typography, illustration, prohibited elements, and the HARD/SOFT rule catalog with accepted ranges.
- `references/prompt-template.md` gives the prompt structure, the wording for reference-image and editing requests, and the correction wording.

Do not duplicate or reinterpret those rules here. If this file and a reference appear to conflict, follow the reference.

## When to use

Use when the requested output is a presentation slide rendered as an image: creating a slide from supplied content, rebuilding an existing slide image in this framework, or improving the visual composition of a slide while preserving its meaning.

Do not use solely for storyline or outline development, speaker notes, content-only critique, PPTX generation, or documents, spreadsheets, and dashboards that are not slide images.

## Reference image handling

When the user provides an existing slide image, treat it as a **content reference** by default, not a style reference.

- **Take from it (content):** main message, title and supporting text, numbers, the illustration concept, information hierarchy, key takeaways.
- **Do not inherit from it (design):** canvas and geometry, title placement, colors and typography, gutter, reserved zones, and any element the framework prohibits.
- Rebuild the composition with the current framework. Remove inherited elements that break it, such as a background image, an eyebrow above the title, a logo, a header, a footer, or decorative shapes. The current framework always wins over styling from earlier generated images.
- Keep the original styling only when the user explicitly asks and the framework's waiver policy allows it (framework Section 1).
- If wording or a number in the image is unreadable, ask. Do not guess.

The exact prompt wording, including how to attach an image when an illustration must be preserved, is in `references/prompt-template.md`.

## Workflow

1. **Understand.** Identify the slide's message, audience (if given), source content, any reference image, and slide-specific instructions. Supplied content is the only factual basis.
2. **Validate content first.** Check numbers and wording against the source before generating. Never invent facts, metrics, claims, or data. Ask one focused question only when something essential is missing or unreadable; otherwise proceed.
3. **Refine.** Shorten and structure the wording as the framework allows. Preserve meaning, numbers, scope, and qualifiers. Keep the title within the framework's title rules.
4. **Compose.** Decide the main message, primary evidence, and supporting detail, then pick the simplest layout and, only if it improves understanding, one illustration.
5. **Assemble the prompt** in the order and with the required items in `references/prompt-template.md`.
6. **Generate ONE image.** Use the available image-generation capability to produce a 16:9 PNG.
7. **Inspect** with the Quality Gate below.
8. **Correct** only if a HARD rule failed (Failure handling below).
9. **Deliver** the single final image.

## No image generation available

If no image-generation capability is available, say so in one line and give the assembled prompt in a code block so the user can run it elsewhere.

## Quality Gate

Every generated slide is inspected before delivery. The rule catalog, accepted ranges, and the [M]/[V] check types are in framework Section 9. Do not restate them here.

1. **Measure, if possible.** When code execution is available and the image exists as a file, run `python3 scripts/validate_slide.py <image>`. It measures the layout rules marked [M]. Use `--help` for options and tolerance settings.
2. **Inspect visually.** Check every HARD rule marked [V], and take a visual look at the [M] rules too. Text accuracy, numbers, prohibited elements, clipping, and the overall composition can only be checked visually.
3. **Review SOFT rules** only after all HARD rules pass.
4. **Confirm before delivery:** the main message is immediately understandable, displayed data matches the source, an illustration (if any) improves understanding, and no unauthorized element was added.

Rules about automated checks:

- Never say or imply that automated validation passed unless the script was actually executed and exited successfully. If it was not run, do not mention measurements.
- A script PASS never replaces the visual inspection. A script WARN is a prompt to look closer, not a failure.
- A rule waived under framework Section 1 is skipped for that slide.

## Single-generation policy

- Generate **one** image per slide. Do not automatically produce variations.
- Do not regenerate for subjective visual preferences (SOFT rules).
- Deliver only the final image. Do not show failed attempts.
- **Variants** (alternative designs) are produced only when the user explicitly asks. When practical, ask before producing an extra variant.
- **Corrections** (fixing a failed HARD rule on the same slide) are not variants. They need no approval and follow the next section.

## Failure handling

If any HARD rule fails:

1. Mark the result non-compliant and identify the exact violation.
2. Correct it. Prefer a targeted edit of the existing image when the tool supports editing, otherwise regenerate with the same prompt plus a targeted correction (wording in `references/prompt-template.md`). Avoid a full redesign for a local problem.
3. Inspect again. Use at most **two** correction passes.
4. If a HARD rule still fails, do not deliver it silently. Deliver the best result and state the remaining deviation in one line.

A failed HARD rule is never ignored to keep to the single-generation policy, and the two-pass limit is never raised without the user's request.

## Logos and brand marks

Never generate, draw, or place a logo, brand mark, or watermark, even when asked. The top-right zone is reserved so the user can add one later. If asked to include a logo, tell the user in one line to add it after generation in that zone.

## Multi-slide requests

Apply the multi-slide consistency rules in the framework. Reuse the same prompt scaffold, geometry, and style wording for every slide. Let each slide's composition adapt to its content; do not make slides identical in structure.

## Output behavior

Deliver only the requested slide image by default. Add no explanatory prose after a compliant result unless the user asks for explanation, critique, or alternatives. If a deviation remains after the correction passes, state it in one line.
