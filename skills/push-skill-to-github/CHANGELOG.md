# Changelog: push-skill-to-github

Versioning follows the repository rules in [VERSIONING.md](https://github.com/xilverkamui/agent-skills/blob/main/VERSIONING.md).

## [1.0.1] - 2026-11-09

### Changed
- Every push is followed by a date-tag release, so the newest zips are always published.
- Release step gives the stable `releases/latest/download/<skill-name>.zip` link; no moving `latest` tag.

## [1.0.0] - 2026-11-04

### Added
- First versioned release in this repository (previously maintained outside the repo, unversioned).

### Changed
- Skill versions use `x.y.z` with `last_updated`, following VERSIONING.md, including the update checklist (Skill version line, CHANGELOG, plugin version).
- Commit messages follow VERSIONING.md.
- Release tags use dates (`vYYYY.MM.DD`).
