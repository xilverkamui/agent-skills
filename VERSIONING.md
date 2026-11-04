# Versioning

This repository has three kinds of version. Each has one job, and `scripts/validate_skills.py` checks that they stay consistent.

| What | Format | Where it lives | Example |
|---|---|---|---|
| Skill | Semantic Versioning `MAJOR.MINOR.PATCH` | `SKILL.md` frontmatter, `Skill version:` line, `CHANGELOG.md` | `2.1.0` |
| Plugin | Semantic Versioning `MAJOR.MINOR.PATCH` | `.claude-plugin/marketplace.json` | `1.0.0` |
| Repository release | Date tag `vYYYY.MM.DD` | Git tag | `v2026.11.04` |

## 1. Skill versions

Every own skill (in `skills/`) carries its version in four places that must match:

```yaml
metadata:
  author: Eriyanto Wibowo
  version: "1.2.0"          # always quoted, always three numbers
  last_updated: "2026-11-04"
```

- the line `Skill version: 1.2.0 (see CHANGELOG.md for history)` near the top of `SKILL.md`;
- the newest entry in the skill's `CHANGELOG.md`: `## [1.2.0] - 2026-11-04` (same date as `last_updated`).

A new skill starts at `1.0.0`. Do not use `0.x` versions or two-number versions such as `1.0`.

### Which number to bump

Judge by what a person using the skill would notice.

**MAJOR** — existing users must adapt:
- the output structure, section titles, or output format change;
- a default changes in a way users rely on (for example, Teams links no longer added by default);
- a capability is removed, or the skill now asks for input it did not need before.

**MINOR** — something new, nothing breaks:
- a new capability, mode, option, or optional section;
- a new provider reference (for example `references/google-calendar.md`);
- a new default that only applies where the skill used to do nothing.

**PATCH** — same behaviour, better instructions:
- wording, clarifications, typo fixes;
- an instruction fixed so the skill does what it was already meant to do.

When unsure between two levels, choose the higher one. Reset lower numbers when bumping (`1.4.2` → `1.5.0` → `2.0.0`).

### Changelog entries

Newest first. Use these headings, only those that apply: `Added`, `Changed`, `Fixed`, `Removed`. Write for the user of the skill, not about file edits.

## 2. Plugin versions

Plugins are listed in `.claude-plugin/marketplace.json`; each points at skill folders in `skills/` (no copies).

- **Single-skill plugin:** the plugin version equals the skill version. Bump both together.
- **Multi-skill plugin:** the plugin has its own version. Bump it by the largest bump among the changes it contains. Adding a skill is MINOR; removing one is MAJOR.

## 3. Repository releases

A release publishes one zip per skill (see `.github/workflows/release.yml`). Because skills have independent versions, release tags use the date: `vYYYY.MM.DD`, with `.2`, `.3`, … for further releases on the same day (`v2026.11.04.2`).

- Tag only when a release is wanted; not every push needs one.
- Never move or delete a published tag.

## 4. Commit messages

- New skill: `Add <skill-name> v1.0.0`
- Update: `<skill-name> v1.2.0: <short summary>`
- Repository tooling or docs: `Repo: <short summary>`

## 5. Checklist for an update

1. Decide MAJOR, MINOR, or PATCH.
2. Update `metadata.version`, `metadata.last_updated`, and the `Skill version:` line.
3. Add the `CHANGELOG.md` entry.
4. If the skill is in a plugin, update the plugin version in `.claude-plugin/marketplace.json`.
5. Run `python scripts/bundle.py` and fix every FAIL.
