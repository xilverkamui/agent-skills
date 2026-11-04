# Provider: Microsoft 365 (Outlook and Teams)

Read this only in create mode with a Microsoft 365 connector. Tool names below are those of Claude's Microsoft 365 connector; other agents may expose the same Microsoft Graph functions under different names. Use whichever tools perform these functions.

| Function | Tool |
|---|---|
| Find a person's email | `search_people` |
| Check availability | `find_meeting_availability` |
| Create the event | `outlook_create_event` |

## Resolving attendees

- Call `search_people` with the name as written.
- Prefer results with `personType` `Person/OrganizationUser` (directory users). `Person/PersonalContact` entries are Outlook contacts and are fine for external guests.
- Use the `mail` field as the address. If it is empty, use `userPrincipalName` only for an `OrganizationUser`.

## Checking availability

Behaviour observed with this connector:

- The organizer is included automatically; pass only the attendees.
- `afterDateTime` and `beforeDateTime` must be UTC (`YYYY-MM-DDTHH:mm:ssZ`). WIB 08:00 is 01:00Z; WIB 17:00 is 10:00Z.
- Returned slots are in the mailbox time zone (`SE Asia Standard Time` is UTC+7, the same as WIB). Present them as returned; do not convert again.
- `nowDateTime` in the result is the authoritative current time. If it changes what "tomorrow" or "next week" means, search again with corrected dates.
- Suggestions are **not** limited to working hours or weekdays. Ask for more candidates than needed (for example `maxCandidates: 20`) and keep only slots that fit the skill's defaults.
- Attendees whose calendars cannot be read (usually external guests) do not cause an error. They appear in `unavailableParticipants` or with availability `unknown` in each slot. Treat them as unverifiable and name them in the preview.

**Finding slots:** search from now to 10 calendar days ahead in one call, with the meeting duration, then filter.

**Validating a requested time:** set the window to exactly the requested start and end, with `maxCandidates: 1`.
- A returned slot where every checkable attendee is `free` means the time works.
- Availability values such as `busy`, `tentative`, or `oof` identify who has a conflict.
- An empty result means at least one attendee is not free; say that the time is not free for everyone without naming anyone the result does not name, then search for alternatives.

## Creating the event

Call `outlook_create_event` with:

- `subject`: the subject from the preview.
- `start` and `end`: `{dateTime: "YYYY-MM-DDTHH:mm:00", timeZone: "Asia/Jakarta"}` (local wall-clock time, no offset).
- `attendees`: `{email, name, type}` with `type` `required`, or `optional` when the user marks someone optional. Maximum 50.
- `isOnlineMeeting`: `true` unless the meeting is explicitly offline. Outlook adds the Teams join details; this cannot be removed afterwards, which is why the preview must state it.
- `location`: the physical location as plain text, only if given.
- `body` with `bodyType: "html"`: the invitation body as simple HTML, paragraphs in `<p>` and agenda items in `<ul><li>`. No styling, images, or scripts.
- `responseRequested`: `true`.

The result returns the event id and a `webLink`. Give the user the `webLink`.

Each attendee receives the invitation as soon as the call succeeds. Call it once per confirmed preview.
