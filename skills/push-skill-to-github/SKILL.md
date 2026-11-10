---
name: "push-skill-to-github"
description: "Publish or update an Agent Skill in the user's GitHub repo xilverkamui/agent-skills. Use when the user says to push, publish, or upload a skill to GitHub/the repo."
license: MIT
metadata:
  author: Eriyanto Wibowo
  version: "1.0.1"
  last_updated: "2026-11-09"
---

# Push skill to GitHub

Skill version: 1.0.1 (see CHANGELOG.md for history)

Repo: https://github.com/xilverkamui/agent-skills (public, MIT license, branch `main`).
Skills follow the Agent Skills spec (agentskills.io).

Layout:
- `skills/<skill-name>/` — the user's own skills (MIT). Self-contained: `SKILL.md`, optional `scripts/`, `references/`, `assets/`.
- `shared/` — single source for files used by several skills. A skill lists the ones it needs in `skills/<skill>/shared.txt` (`<file in shared/> -> <dest in skill>`); `scripts/sync_shared.py` copies them in. Edit shared files only in `shared/`.
- `third-party/<skill>/` — other people's skills, imported with `scripts/vendor.py`, each keeping its own LICENSE and an `UPSTREAM.md` (source repo, path, commit, license).

## Before pushing

1. Confirm the user has approved the final skill content.
2. Ask the user for a fine-grained PAT (scoped to this repo; Contents and Workflows read/write) if one has not been given in this session. Never write the token to a file, git config, remote URL, or commit; use it only inline per command.

## Steps

1. Clone (or reuse an existing clone):
   ```bash
   AUTH=$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)
   git -c http.extraheader="Authorization: Basic $AUTH" clone https://github.com/xilverkamui/agent-skills.git
   cd agent-skills
   git config user.name "Eriyanto Wibowo"
   git config user.email "112789454+xilverkamui@users.noreply.github.com"
   pip install pyyaml --break-system-packages -q
   ```
2. Add the change:
   - **Own skill:** copy it into `skills/<skill-name>/`. Folder name must equal the frontmatter `name` (lowercase a-z, 0-9, single hyphens, max 64 chars). Add `license: MIT` and `metadata: {author: Eriyanto Wibowo, version: "x.y.z", last_updated: "YYYY-MM-DD"}` unless the user says otherwise. Follow the repo's `VERSIONING.md`: new skills start at `1.0.0`; on updates pick MAJOR, MINOR, or PATCH, then update `metadata.version`, `metadata.last_updated`, the `Skill version:` line in SKILL.md, the skill's `CHANGELOG.md`, and the plugin version in `.claude-plugin/marketplace.json` if the skill is in a plugin. Reference files with paths relative to the skill folder, never `../`.
   - **File shared by several skills:** put it in `shared/`, list it in each skill's `shared.txt`, run `python3 scripts/sync_shared.py`.
   - **Someone else's skill:** `python3 scripts/vendor.py add <github-url-to-skill-folder>`. If it refuses (no license / proprietary), do not copy it; offer to add a link in README instead. Tell the user to review its `scripts/` before use. For edits to a vendored skill, note them under "Local changes" in its `UPSTREAM.md`. Use `vendor.py check` / `update` to refresh.
3. Check: `python3 scripts/bundle.py` (runs the shared-file check and validation, then builds `dist/*.zip`). Fix every FAIL. Offer the zip to the user if they want it now.
4. Show the user `git status` and a short diff summary; commit with a message from `VERSIONING.md`: `Add <skill-name> v1.0.0`, `<skill-name> vX.Y.Z: <summary>`, or `Repo: <summary>`. Never commit `dist/`.
5. Push: `git -c http.extraheader="Authorization: Basic $AUTH" push origin main`.
6. Verify with `git ls-remote` (same header) that `refs/heads/main` equals the local HEAD, then give the link `https://github.com/xilverkamui/agent-skills/tree/main/<skills|third-party>/<skill-name>`.
7. Release (every push, no need to ask): right after step 6, create and push a date tag, e.g. `git tag v2026.11.04 && git -c http.extraheader=... push origin v2026.11.04` (add `.2`, `.3` for more releases on the same day); GitHub Actions publishes a Release with all zips. The newest Release is marked Latest automatically, so the newest zip of any skill is always at `https://github.com/xilverkamui/agent-skills/releases/latest/download/<skill-name>.zip`; give the user that link. Do not create or move a `latest` tag.

## Notes

- The GitHub REST/GraphQL API may be blocked from the session; git over HTTPS works. Ask the user to check the Actions/Releases tabs.
- Never push without the user's explicit OK, and never force-push.