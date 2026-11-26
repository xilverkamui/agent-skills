---
name: lnk-visual-presentation
description: Generate presentation slides as polished, high-resolution 16:9 PNG images using a fixed visual framework (flat white canvas, narrow blue left gutter, reserved empty top-right and bottom-right zones, restrained palette, no decorative backgrounds). Use whenever the user asks to create, generate, redraw, redesign, or visually improve a presentation slide as an image, or to turn slide content into a visual slide, even if they do not mention the framework. Do not use for PPTX generation, storyline or outline development, speaker notes, or content-only critique.
license: MIT
metadata:
  author: Eriyanto Wibowo
  version: "1.0.0"
  last_updated: "2026-11-26"
---

# Visual Presentation

Skill version: 1.0.0 (see CHANGELOG.md for history)

## Purpose

Generate presentation-slide images that follow one consistent, restrained visual framework.

Two reference files carry the details. Read both before generating:

- `references/visual-presentation-framework.md` is the single source of truth for design rules: geometry, reserved zones, prohibited elements, palette, typography, quality check.
- `references/prompt-template.md` explains how to turn a slide into an image-generation prompt and how to correct a result.

Do not duplicate or reinterpret those rules here. If this file and a reference appear to conflict, follow the reference.

## When to use

Use when the requested output is a presentation slide rendered as an image: creating a slide from supplied content, redesigning an existing slide image, or improving the visual composition of a slide while preserving its meaning.

Do not use solely for storyline or outline development, speaker notes, content-only critique, PPTX generation, or documents, spreadsheets, and dashboards that are not slide images.

## Workflow

1. **Understand.** Identify the slide's message, audience (if given), source content, and any slide-specific instruction. Supplied content is the only factual basis.
2. **Resolve only necessary gaps.** Never invent facts, metrics, claims, or data. Ask one focused question only when something essential is missing; otherwise proceed.
3. **Refine content.** Shorten and structure wording as the framework allows. Preserve meaning, numbers, scope, and qualifiers. Keep the title short enough for the title limit in the framework.
4. **Prioritize and compose.** Decide the main message, primary evidence, and supporting detail, then pick the simplest layout that communicates them.
5. **Assemble the prompt.** Follow `references/prompt-template.md`: canvas, layout map, exact text, visual elements, style, empty zones, and prohibitions last.
6. **Generate.** Use the available image-generation capability to produce a 16:9 PNG. When editing an existing slide image, preserve everything the user did not ask to change.
7. **Inspect and correct.** Check the result against the Final Quality Check in the framework. If a locked rule is violated, regenerate with a targeted correction (see the template). Use at most two corrective passes.
8. **Deliver.** Present the image.

## No image generation available

If no image-generation capability is available, say so in one line and give the assembled prompt in a code block so the user can run it elsewhere.

## Logos and brand marks

Never generate, draw, or place a logo, brand mark, or watermark. The top-right zone is reserved so the user can add one later. If asked to include a logo, tell the user in one line to add it after generation in that zone.

## Multi-slide requests

Apply the multi-slide consistency rules in the framework. Reuse the same prompt scaffold, geometry, and style wording for every slide. Let each slide's composition adapt to its content; do not make slides identical in structure.

## Output behavior

The default deliverable is the generated slide image only. Add no explanatory prose after a successful image unless the user asks for explanation, critique, or alternatives. If the result still has a known deviation after the corrective passes, state that deviation in one line.
