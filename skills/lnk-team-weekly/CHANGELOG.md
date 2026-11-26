# Changelog: lnk-team-weekly

Versioning follows the repository rules in [VERSIONING.md](https://github.com/xilverkamui/agent-skills/blob/main/VERSIONING.md).

## [1.0.0] - 2026-11-26

### Added
- Initial release: writes the weekly Friday team email from an IT manager to their team, in natural Bahasa Indonesia, from the manager's wins, updates, shoutouts, and next-week focus.
- Subject line `<prefix> | <hook>`; the prefix defaults to `Team Weekly` and can be overridden in the prompt.
- Optional sections (1-on-1 Corner, Micro Engagement) are included only when the user flags them, because the skill cannot see earlier editions. Pasting last week's edition helps avoid repeated openings and closings.
- Asks before writing when a shoutout, item, or term is unclear; never invents achievements, names, or events.
- Guidance for sounding human in Indonesian, with a list of common AI tells to avoid.
- Internal self-critique (accuracy, natural Indonesian, warmth, readability, structure); the email is delivered only when the lowest score is at least 9.5/10.
- `references/style-examples.md` with tone illustrations.
- Contains no organization-specific details; private team context can be supplied through Project instructions or knowledge.
