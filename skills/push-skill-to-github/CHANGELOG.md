# Changelog: push-skill-to-github

Versioning follows the repository rules in [VERSIONING.md](https://github.com/xilverkamui/agent-skills/blob/main/VERSIONING.md).

## [1.1.0] - 2026-11-27

### Added
- Preferred route through the Claude GitHub App (`add_repo`): clone and push with no PAT. The PAT route stays as a fallback.
- Notes on what the App session blocks (tag push/API, release asset upload, GraphQL) and why not to retry.

### Changed
- Release step is now automatic: the `Release zips` workflow creates the date tag and Release on every push to `main` that touches skills, shared or third-party files. The skill no longer creates or pushes tags; it only verifies the Release and gives the `releases/latest/download/<skill-name>.zip` link.

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
