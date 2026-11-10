# Changelog: minutes-of-meeting

Format: Semantic Versioning (MAJOR.MINOR.PATCH).
- MAJOR: changes to output structure or section titles that affect existing users
- MINOR: new capabilities or sections that stay compatible
- PATCH: wording fixes, clarifications, typo fixes

When updating the skill, bump `metadata.version` and the "Skill version" line in SKILL.md, then add an entry here.

## [3.0.0] - 2026-11-10

### Changed
- People are referred to with "Pak" or "Bu" in running text (Meeting Outcome, Key Points, Discussion Notes, Action column, To Be Confirmed). Names stay plain only in the Participants row and the PIC column.
- When the source does not show whether someone is Pak or Bu, the skill now asks the user instead of guessing. No placeholder is written; in automated runs the name is written without Pak/Bu.

### Added
- After the MoM, an offer to create a reply-all email draft to the meeting invitation (only when a mail connector can create reply drafts).
- On acceptance: finds the invitation in inbox or sent items, creates a reply-all draft (never sends) with the MoM as HTML, and asks before creating a new draft if no invitation is found.

## [2.1.0] - 2026-11-02

### Changed
- New default structure, modeled on the preferred MoM format: title, Meeting Information (two-column table), Meeting Outcome, Key Points (numbered topics with bold titles), Next Actions.
- Section titles and table headers are now always English (Meeting Information, Meeting Outcome, Key Points, Next Actions, Discussion Notes, To Be Confirmed). Content stays Indonesian by default.
- Participants moved into the Meeting Information table instead of a separate section.
- The separate Meeting Notes section is removed from the default; available as Discussion Notes in the Detailed level.
- Next Actions table is numbered (No | Action | PIC | Due Date); actions start with a verb.

### Added
- Meeting Outcome: one-sentence bottom line plus 2-5 decision bullets at the top.
- Three detail levels: Concise (default), Detailed, Brief.
- Decisions left open become "Putuskan ..." actions instead of placeholders; placeholders are kept only for information the writer cannot verify.
- Output format stated explicitly: Markdown in the chat reply only; no document, artifact, or email draft unless explicitly requested.
- Consistency check across sections in final validation.

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
