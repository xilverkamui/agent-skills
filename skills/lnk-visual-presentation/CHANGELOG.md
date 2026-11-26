# Changelog: lnk-visual-presentation

Versioning follows the repository rules in [VERSIONING.md](https://github.com/xilverkamui/agent-skills/blob/main/VERSIONING.md).

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
