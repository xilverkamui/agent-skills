# Changelog: lnk-visual-presentation

Versioning follows the repository rules in [VERSIONING.md](https://github.com/xilverkamui/agent-skills/blob/main/VERSIONING.md).

## [1.1.0] - 2026-11-27

### Added
- Quality gate before delivery with HARD rules (layout geometry, no logos or prohibited elements, accurate text and numbers) and SOFT rules (balance, composition, illustration quality). Only a failed HARD rule triggers a correction; a SOFT preference never causes regeneration.
- Accepted ranges for the measurable rules (for example gutter 1.2% to 1.8%, title top at Y 2% to 6%), so normal generator drift is not reported as a failure.
- Reference image handling: an existing slide image is a content reference by default. Wording, numbers, hierarchy, and illustration concept are kept; its background, header, logo, layout, and colors are not inherited.
- Waiver policy: layout rules can be waived for one slide only when the user names the rule, and prohibited content only when the user asks for that exact element. Logos and invented data are never allowed.
- Illustration guidance: clean flat vector, editorial, polished isometric, or restrained 2.5D, one major illustration per slide, separated from the canvas by its own contrast or a light panel rather than glows or blobs.
- Optional `scripts/validate_slide.py` (Python 3 with Pillow) that measures image size, aspect ratio, gutter width, color, and continuity, both reserved zones, the title row, and background edges. It only measures and never edits the image. Text, numbers, prohibited elements, and composition still need visual inspection.
- Failure handling: at most two correction passes, then deliver the best result with a one-line note of any remaining deviation.

### Changed
- Title placement is stricter: the title is the first visible text, its top sits at about Y = 4%, it starts at X = 5% and ends before X = 78%, nothing is placed above it, and it is never moved down to make room for other content. Content moves down instead.
- Prompt template follows a fixed eight-part order with the prohibitions last, and every prompt must state the gutter, title position, empty zones, and the ban on logos, photos, decorative backgrounds, and invented data.
- Redesign requests no longer attach the old slide image by default. The content is transcribed into the prompt instead, so old styling is not carried over.
- Single-generation policy: one image per slide. Alternative variants are produced only when the user asks.

## [1.0.0] - 2026-11-26

### Added
- Initial release, based on the earlier unversioned Visual Presentation Framework prototype.
- Constraints-first framework: locked canvas geometry with percentage positions, a 1.5% blue left gutter, and concrete reserved zones (top-right, bottom-right) that must stay plain white.
- Title rules: one short line, two lines when needed, never entering the top-right reserved zone; title sits in the top band.
- Explicit list of prohibited elements (photos, background images, gradients and glows, decorative shapes, logos, unrequested headers, footers, and slide numbers, placeholder boxes).
- "Only supplied elements" rule: nothing is added that was not part of the supplied content or instruction.
- Semantic alert color for negative values, plus tinted card surfaces derived from the core palette.
- `references/prompt-template.md`: prompt assembly order, exact-text blocks, and a targeted correction loop (maximum two passes).
- Fallback: when image generation is unavailable, output the assembled prompt.
