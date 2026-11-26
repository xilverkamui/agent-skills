# Organization profile

Organization-specific defaults for this skill. They live only here, so another organization can adapt the skill by replacing this one file without touching `SKILL.md`.

Current profile: **LNK**.

If this file is missing, or a section below is empty, use that section's neutral fallback.

## Time zone

WIB (UTC+7). IANA name: `Asia/Jakarta`. Windows / Outlook name: `SE Asia Standard Time`.

Fallback: the user's time zone when known; otherwise ask once.

## Working schedule

Times in the organization time zone. Slots proposed by the meeting scheduler must lie completely inside a working block.

| Day | Working blocks | Break |
|---|---|---|
| Monday-Thursday | 08:00-12:00, 13:00-17:00 | 12:00-13:00 |
| Friday | 08:00-11:30, 13:00-17:30 | 11:30-13:00 (break and Friday prayer) |
| Saturday-Sunday | none | — |

Fallback: Monday-Friday 09:00-12:00 and 13:00-17:00; no weekends.

## Minutes of Meeting closing

End every MoM with these two lines, unless the user or the calling workflow overrides them:

> Mohon rekan-rekan dapat memberikan masukan atau koreksi apabila terdapat hal yang perlu disesuaikan dari MoM ini.

> MoM ini juga tersedia di aplikasi [Collab MoM](https://collaboration.oneltl.com/mom/list)

For another content language, translate both lines; keep the link text "Collab MoM" and the URL unchanged.

Fallback: only the first line (a request for feedback or corrections), without any application link.
