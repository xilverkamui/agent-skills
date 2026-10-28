# Agent Skills

A collection of reusable [Agent Skills](https://agentskills.io) by Eriyanto Wibowo.

Every skill follows the open Agent Skills specification, so it works in any
compatible agent (Claude, ChatGPT, and others that support `SKILL.md`).

## Download

Ready-to-upload zips (one per skill) are on the
[Releases](https://github.com/xilverkamui/agent-skills/releases) page.

- **Claude (claude.ai / Cowork):** upload the zip under *Settings → Capabilities → Skills*,
  or unzip it into `~/.claude/skills/` for Claude Code.
- **ChatGPT / other agents:** import the zip or folder using that product's skill import.

## Layout

```
skills/                 # skills written for this collection (MIT)
└── <skill-name>/
    ├── SKILL.md        # required: YAML frontmatter + instructions
    ├── scripts/        # optional: executable helpers
    ├── references/     # optional: docs loaded on demand
    ├── assets/         # optional: templates, images, data
    └── shared.txt      # optional: files to copy in from shared/
shared/                 # single source for files used by several skills
third-party/            # skills by other authors, each under its own license
scripts/                # repo tooling (validate, sync, bundle, vendor)
```

`<skill-name>` must equal the `name` field in its `SKILL.md`
(lowercase letters, digits and single hyphens, max 64 characters).
A skill must be self-contained: reference its files with paths relative to its own folder.

## Tooling

```bash
pip install pyyaml
python scripts/sync_shared.py        # copy shared/ files into the skills that list them
python scripts/validate_skills.py    # check every SKILL.md against the spec
python scripts/bundle.py [name ...]  # build dist/<skill>.zip
python scripts/vendor.py add <github-url-to-skill-folder>   # import a third-party skill
```

| File | Purpose |
|---|---|
| [`shared/README.md`](shared/README.md) | How shared files work |
| [`third-party/README.md`](third-party/README.md) | Importing and updating other people's skills |

Every push runs the shared-file check, validation and a test bundle.
Pushing a tag such as `v1.0` publishes a Release with all zips attached.

## License

Everything in this repository is [MIT](LICENSE)-licensed **except `third-party/`**,
where each skill keeps its original license (see the `LICENSE` and `UPSTREAM.md`
in its folder).
