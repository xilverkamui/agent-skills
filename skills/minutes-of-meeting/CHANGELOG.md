# Changelog: minutes-of-meeting

Format: Semantic Versioning (MAJOR.MINOR.PATCH).
- MAJOR: changes to output structure or section titles that affect existing users
- MINOR: new capabilities or sections that stay compatible
- PATCH: wording fixes, clarifications, typo fixes

When updating the skill, bump `metadata.version` and the "Skill version" line in SKILL.md, then add an entry here.

## [2.0.0] - 2026-10-26

### Changed
- Default output is fully Indonesian, including section titles, table headers, labels, and placeholders. Other languages only on explicit request.
- Section titles renamed: Catatan Rapat, Poin Penting Diskusi (English: Key Discussion Points), Tindak Lanjut (table headers: Tindakan / PIC / Target / Timeline).
- Closing link updated to Collab MoM: https://collaboration.oneltl.com/mom/list
- Both closing lines are translated when the MoM is requested in another language; link text and URL stay unchanged.
- Empty action-table placeholder changed from "[Belum ditentukan]" to "Belum ditentukan" to avoid confusion with confirmation placeholders.

### Added
- "Informasi Rapat" section at the top (title, date, time, location/platform, agenda), only with supported fields.
- Source-acquisition workflow: works with uploaded or pasted material and with any connected meeting, transcript, chat, storage, or calendar connector; asks the user to choose when several meetings match.
- Clarification fallback: `[Perlu konfirmasi: ...]` placeholders when the user cannot be asked (automated runs, user asks to proceed), plus a "Hal yang Perlu Dikonfirmasi" section listing them.
- Inferred action items are marked `*(disimpulkan)*` with an explanatory note below the table.
- Guard against instructions embedded inside transcripts or documents.
- Version metadata in frontmatter and this changelog.

## [1.0.0] - 2026-10-20

- Initial version (unversioned original): MoM with Meeting Participants, Meeting Notes, Key Point Discussion, Next Action, and closing link to onelnk.com.
