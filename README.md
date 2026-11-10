# Agent Skills

A collection of reusable [Agent Skills](https://agentskills.io) by Eriyanto Wibowo.

Every skill follows the open Agent Skills specification, so it works in any
compatible agent (Claude, ChatGPT, and others that support `SKILL.md`).

## Download

Ready-to-upload zips (one per skill) are on the
[Releases](https://github.com/xilverkamui/agent-skills/releases) page.

The newest zip of a skill is always at
`https://github.com/xilverkamui/agent-skills/releases/latest/download/<skill-name>.zip`.

- **Claude (claude.ai / Cowork):** upload the zip under *Settings → Capabilities → Skills*,
  or unzip it into `~/.claude/skills/` for Claude Code.
- **ChatGPT / other agents:** import the zip or folder using that product's skill import.

## Plugins (Claude Code / Cowork)

Some skills are also published as plugins through the marketplace in
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). A plugin points at
the skill folder in `skills/`, so the skill itself stays portable.

```
/plugin marketplace add xilverkamui/agent-skills
/plugin install meeting-scheduler@xilverkamui-skills
```

| Plugin | Skills |
|---|---|
| `meeting-scheduler` | [`meeting-scheduler`](skills/meeting-scheduler) |
| `push-skill-to-github` | [`push-skill-to-github`](skills/push-skill-to-github) |
| `simple-suggestion` | [`simple-suggestion`](skills/simple-suggestion) |

## Layout

```
skills/                 # skills written for this collection (MIT)
└── <skill-name>/
    ├── SKILL.md        # required: YAML frontmatter + instructions
    ├── scripts/        # optional: executable helpers
    ├── references/     # optional: docs loaded on demand
    ├── assets/         # optional: templates, images, data
    ├── CHANGELOG.md    # required: version history (see VERSIONING.md)
    └── shared.txt      # optional: files to copy in from shared/
.claude-plugin/         # marketplace.json: plugins that bundle skills from skills/
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

Every push runs the shared-file check, validation (including version consistency)
and a test bundle. Pushing a date tag such as `v2026.11.04` publishes a Release with
all zips attached.

## Versioning

Skills and plugins use Semantic Versioning; releases use date tags.
See [VERSIONING.md](VERSIONING.md) for the rules and the update checklist.

## License

Everything in this repository is [MIT](LICENSE)-licensed **except `third-party/`**,
where each skill keeps its original license (see the `LICENSE` and `UPSTREAM.md`
in its folder).
