# Invitation content rules

Adapted from the user's original `outlook-meeting-invitation` skill. These rules decide what the subject and body say in both modes. Section "Meeting details" and "Output contract" differ by mode.

## Understand the request

- Read the agenda and meeting context, including explicit corrections.
- Identify the main purpose without inventing intended outcomes.
- Ask a small number of focused questions only when missing or conflicting information materially changes the purpose or agenda. If there is no meaningful agenda or purpose, ask for it.
- Proceed when the core purpose is clear. Missing date, time, location, or attendee names do not prevent drafting.

## Preserve meaning and facts

- Derive the subject and opening from the supplied purpose or agenda.
- Improve wording, combine duplicate points, and arrange agenda items for clarity while preserving meaning, scope, emphasis, and any explicit sequence.
- Do not add agenda items because they might be useful.
- Do not turn a discussion into an approval, decision-making, or assignment meeting without support in the input.
- Do not invent attendees, preparation requirements, commitments, deadlines, intended decisions, recipient titles, or a sender signature.
- Use only supplied logistical details; never infer them from the topic or attendees.

Example: "discuss implementation obstacles and follow-up options" supports discussing those matters. It does not support assigning owners, approving solutions, or setting completion dates.

## Meeting details

**Create mode:** never put the date, time, location, or meeting link in the body. They live in the event fields, and Outlook adds the Teams join details itself. Keeping them out of the body prevents stale text if the meeting is moved.

**Draft mode:**
- By default, leave date, time, and location out of the body, because the user enters them in Outlook's event fields.
- If the user supplies a date, time, or location for the meeting, include only the supplied parts in a short section before the agenda, with labels such as `Tanggal:`, `Waktu:`, and `Lokasi:`.
- Do not invent a year, end time, duration, time zone, or meeting link. Preserve a supplied online link exactly.
- Never output empty labels or placeholders.
- Distinguish real meeting details from dates or places that are only mentioned in agenda topics.

## Write the invitation

- Indonesian by default. Change language only when explicitly asked; do not produce several language versions unless asked.
- Formal but natural and straightforward. Avoid slang, ceremonial phrasing, repeated courtesies, and stiff bureaucratic language.
- A concise subject reflecting the main purpose.
- A brief opening paragraph stating the meeting's intention.
- The agenda as bullet points, even when there is only one point.
- A polite closing that thanks attendees for attending. Ask for attendance confirmation only if the user asks for it or the context explicitly requires it.
- Do not add an unsupported preparation request or imply that attendance is mandatory.

## Output contract

**Draft mode:** return one draft in plain text, in this order:

1. `Subject: ` followed by the meeting title.
2. Opening paragraph.
3. Meeting-details section, only when applicable.
4. `Agenda:` followed by bullet points.
5. Closing paragraph.

Separate the subject from the body with a blank line. No body label, code fences, tables, explanations, review notes, alternative versions, or placeholders inside the draft.

**Create mode:** the subject goes into the event subject field. The body (opening, `Agenda:` with bullets, closing) goes into the event body, formatted as the provider reference describes. The same text also appears in the preview.

## Final check

Before showing the draft or preview, silently check that:

- every substantive agenda point is covered and the purpose is preserved;
- nothing unsupported was added (fact, requirement, commitment, decision);
- meeting details follow the rules for the current mode;
- subject, opening, agenda, and closing agree and read naturally.

Fix anything that fails before responding.
