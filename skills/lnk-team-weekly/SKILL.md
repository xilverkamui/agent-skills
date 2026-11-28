---
name: lnk-team-weekly
description: Write the weekly Friday email ("Team Weekly") from an IT manager to their team, in natural Bahasa Indonesia. Use whenever the user asks to write, draft, or revise the weekly team email, Team Weekly, the Friday note to the team, or pastes a list of wins, updates, shoutouts, or next-week priorities for the team, even if they don't name the email. Produces a subject line and body ready to paste into Outlook, after an internal self-critique that must reach at least 9.5/10.
license: MIT
metadata:
  author: Eriyanto Wibowo
  version: "3.0.0"
  last_updated: "2026-11-28"
---

# Team Weekly

Skill version: 3.0.0 (see CHANGELOG.md for history)

Write the weekly internal email that an IT manager sends to their team every Friday afternoon. The user is that manager; write in their voice, first person ("saya"), to their own team.

The email exists to keep the team informed, recognize real contributions, and build trust through consistent, human communication. It should read like a thoughtful note from a team leader, never like an announcement from corporate communications.

## Audience

The manager's team members, from several technical sections. Readers are technical, collaborative, and busy.

Friday afternoon context: people are wrapping up, tired, and skimming. Optimize for quick reading, low mental load, warmth, and calm energy.

## Inputs

The user provides one or more of:

- Wins / achievements
- Updates
- Shoutouts (person + what they did)
- Next week focus
- Optional flags: include 1-on-1 Corner (yes/no), include Mini Corner (yes/no; older prompts may say "Micro Engagement", which is the same section)
- Optional: last week's edition (pasted), to avoid repeating its patterns

You cannot see previous editions unless the user pastes one. Do not pretend to remember them. Section rotation (1-on-1 Corner, Mini Corner) is decided by the user's flags. If no flag is given, omit those two sections.

## Reference files and private context

- `references/style-examples.md` — tone illustrations. Read before drafting.

This skill deliberately contains no company-specific details (org structure, system names, internal projects), because it may live in a public repository. If the user's environment supplies private context (e.g. Project instructions or knowledge describing team scopes or internal terms), use it only to understand the input, never as a source of facts for the email. If an item is unclear, or an internal name could be read more than one way, ask the user.

## Ask, don't invent

Never fabricate achievements, updates, numbers, names, dates, events, reasons, or outcomes. If something needed for a section is unclear, ask the user before writing. Ask when:

- A shoutout names a person but not what they did or why it helped.
- An item uses an acronym or project name whose meaning changes how it should be explained to the team.
- It is unclear whether an item is finished (win) or still in progress (update).
- The input is so thin that the email would have nothing real to say.

Keep questions few and focused (ideally 1–3, in one message). Do not ask about minor details you can reasonably handle by simply writing less. If an item is ambiguous but low-stakes, write it at the level of detail given rather than embellishing.

For the opening and Weekly Thought, only reference things that are in the input or genuinely common knowledge (e.g. a national holiday, end of month). Do not invent "busy week", "lots of discussions", or similar claims unless the input supports them.

Also do not add offers, promises, or claims the user did not give: for example offering the team help with someone's preparation, or wording like "as usual" for a recurring item when recurrence is not confirmed. A collective label over a group of items (for example "from event X, four pieces of news") must be true for every item in the group; if one item belongs to a different event, word the label neutrally.

Seasonal or calendar context the user provides (month-end, payday, a holiday) belongs in the opening. Do not repeat it in the Weekly Thought or elsewhere.

## Language

Default: natural Bahasa Indonesia, the way an Indonesian manager actually writes to their team. Use another language only if the user explicitly asks.

Common workplace English terms are fine when they fit naturally (dashboard, deploy, go-live, ticket, sprint, meeting, feedback, progress). Never force English where Indonesian sounds better, and never force formal Indonesian where everyday workplace Indonesian sounds better.

Write in first person singular ("saya"). Address the team as "teman-teman" or "tim" — vary it, and don't overuse either.

### Sounding human, not AI

The biggest risk for this email is sounding generated. Watch for these tells and avoid them:

- Stock openers: "Tidak terasa kita sudah sampai di penghujung minggu", "Halo semuanya! Semoga dalam keadaan sehat selalu", "Mari kita...".
- Inflated praise: "luar biasa", "sangat membanggakan", "dedikasi yang tinggi", "kerja keras yang tak kenal lelah".
- Formal-bureaucratic phrasing: "dalam rangka", "adapun", "sehubungan dengan", "perlu kami sampaikan", "demikian".
- Rule-of-three lists for rhythm ("lebih cepat, lebih rapi, dan lebih efisien") when one point would do.
- Every paragraph ending on an uplifting note.
- Excessive em dashes, colons, or exclamation marks. At most one exclamation mark in the whole email.
- Motivational or LinkedIn-style lines ("Ingat, setiap langkah kecil adalah awal dari perubahan besar").
- Literal translations of English idioms.

Natural writing has some unevenness: a short sentence next to a longer one, a conversational aside, a transition like "Oh ya," or "Satu lagi,". Use this lightly. At most one deliberately loose or spoken-style sentence per email; never make the writing sloppy on purpose.

A normal week should sound like a normal week. Not every paragraph needs to inspire.

## Subject line

Format: `<prefix> | <hook>`

The default prefix is `Team Weekly`. If the user's prompt gives a different email name or prefix, use theirs instead.

The hook is 4–7 words reflecting something real about this week. Professional, simple, specific, no clickbait. Avoid generic hooks ("Weekly Update", "Another Great Week"). If a previous edition was pasted, don't reuse its wording.

Hooks may be in Indonesian or English, whichever sounds more natural for the content.

## Email structure

Sections in this order. Include only what has real content. Sections should differ in length; some may be one sentence, some a few bullets.

1. **Opening** (always) — 2–4 short sentences, no heading. Pick an approach that fits this specific week: an observation, a milestone, something timely, a light reflection, a look ahead, or appreciation. If last week's edition was pasted, use a different approach than it did. Don't thank the team every week by default.

2. **Wins This Week 🏆** (only if wins are given) — Celebrate naturally. Say briefly why each win matters to the business or users. Recognize effort as well as outcome. No status-report language, no exaggeration. When the wins are achievements by people (competitions, awards, recognition), add one short, sincere paragraph about what that kind of effort generally involves, only in terms that are common knowledge and never inventing specifics, and acknowledge every placing, including lower ones, in one general sentence. Say thank-you once in the whole email; do not repeat it across Wins, shoutouts, and closing.

3. **Updates 📢** (only if updates are given) — Plain explanation of what people need to know. Conversational: "Minggu depan kita akan lebih banyak fokus ke..." rather than "Perhatian utama kita akan bergeser...".

4. **Team Shoutout 🙌** (only if shoutouts are given) — Specific and believable: what the person did, why it helped. Use names exactly as given.

5. **Next Week Focus 🎯** (only if priorities are given) — Practical and short. Help the team align without sounding like instructions from above.

6. **Weekly Thought ✨** (always) — One or two sentences. A small, ordinary observation someone might say over Friday coffee. Not a lesson, not advice, not a quote. Ideally connected to something in this week's content.

7. **Mini Corner 💬** (only if flagged) — One casual, optional invitation to share something (an AI tool, a coffee place, a podcast, weekend plans). Nobody should feel they must reply.

8. **1-on-1 Corner 🤝** (only if flagged) — A warm, low-pressure reminder that the manager's calendar is open for ideas, brainstorming, growth, feedback, check-ins, or just catching up. Vary the wording. Where natural, connect it to something in this week's content.

9. **Closing** (always) — One or two short sentences: a relaxing weekend, looking ahead, appreciation, or a simple goodbye. No name or signature; the user's Outlook signature is added automatically.

If content is minimal, write a short email. A shorter, honest email is better than a padded one. Typical length: 120–300 words in the body.

The examples in `references/style-examples.md` show register only; never copy their sentences.

## Self-critique before delivering

Before showing anything to the user, score the draft internally against this rubric (each 0–10), then take the overall score as the lowest of the five, not the average. One weak dimension is enough to make the email feel off.

1. **Accuracy** — Every fact, name, and claim traces to the user's input. Nothing invented or exaggerated.
2. **Natural Indonesian** — Reads like a real Indonesian manager wrote it in 10–15 minutes. None of the AI tells listed above.
3. **Warmth and tone** — Human, approachable, appreciative where earned; not HR, not motivational, not stiff.
4. **Readability** — Skimmable on a tired Friday; varied rhythm; sections sized to their content.
5. **Structure compliance** — Correct subject format, right sections included or omitted, Weekly Thought and Closing present, no signature.

If the overall score is below 9.5, identify the specific problems, revise, and score again. Repeat up to 3 revision rounds. Be a strict reviewer: a score of 9.5 means you would send it unchanged as the manager.

If after 3 rounds the draft still scores below 9.5, the cause is usually missing input. Don't keep polishing; ask the user the question that would fix it, and show the best draft so far with a one-line note on what is holding it back.

## Output

Deliver, in this order:

1. The subject line.
2. The email body in a single code block so it is easy to copy, ready to paste into Outlook (headings as plain text with emoji, optional divider lines under headings, short bullets where helpful, no Markdown tables, no bold markup since it will not survive the paste).
3. One short line after the email: the final self-critique score, plus at most one sentence on anything worth the user's attention (e.g. "1-on-1 Corner tidak saya sertakan karena tidak diminta minggu ini."). Write this line in Indonesian.

Do not show the internal rubric scoring or revision history unless the user asks.

If an email connector (e.g. Outlook / Microsoft 365) is available, offer once to create it as a draft. Never send the email.
