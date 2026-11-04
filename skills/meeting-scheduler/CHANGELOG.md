# Changelog: meeting-scheduler

Versioning follows the repository rules in [VERSIONING.md](https://github.com/xilverkamui/agent-skills/blob/main/VERSIONING.md).

## [1.1.0] - 2026-11-04

### Changed
- Working hours follow the LNK schedule: Monday-Thursday 08:00-17:00 with a 12:00-13:00 break; Friday 08:00-17:30 with an 11:30-13:00 break and Friday prayer; no weekends.
- Proposed slots must lie completely inside a working block; slots overlapping a break are dropped.
- A time the user explicitly requests outside working hours is still used, with a note in the preview.
- Microsoft 365: request up to 50 candidates and search again if filtering leaves fewer than 2.

## [1.0.0] - 2026-11-04

### Added
- Initial release, built on the invitation rules of the earlier `outlook-meeting-invitation` skill (now `references/invitation-content.md`).
- Two modes chosen from the tools available: draft mode (text only, works in any agent) and create mode (calendar connector).
- Create mode for Microsoft 365: attendee lookup, availability check with 2-3 proposed slots, validation of a requested time, preview, explicit confirmation, event creation.
- Defaults: WIB, 60 minutes, 08:00-17:00 Monday-Friday, 10-calendar-day search window, Teams link always added unless the user says offline, physical location as plain text.
- Unverifiable attendees (such as external guests) are kept and named in the preview.
- Provider-neutral structure: provider details live in `references/<provider>.md`.

### Changed (compared with outlook-meeting-invitation)
- Create mode never puts date, time, location, or meeting link in the body.
- The "never use an Outlook connection" boundary is removed.
