# Agent Skills

A collection of reusable [Agent Skills](https://agentskills.io) by Eriyanto Wibowo.

Every skill follows the open Agent Skills specification, so it works in any
compatible agent (Claude, ChatGPT, and others that support `SKILL.md`).

## Layout

```
skills/
└── <skill-name>/
    ├── SKILL.md        # required: YAML frontmatter + instructions
    ├── scripts/        # optional: executable helpers
    ├── references/     # optional: docs loaded on demand
    └── assets/         # optional: templates, data, images
```

`<skill-name>` must equal the `name` field in its `SKILL.md`
(lowercase letters, digits and single hyphens, max 64 characters).

## Using a skill

- **Claude (claude.ai / Cowork):** zip the skill folder and upload it under
  *Settings → Capabilities → Skills*, or copy it into `~/.claude/skills/` for Claude Code.
- **ChatGPT / other agents:** add the skill folder using that product's skill import.
- Or clone the whole repo:
  `git clone https://github.com/<your-username>/agent-skills.git`

## Validation

Each push runs `scripts/validate_skills.py`, which checks every `SKILL.md`
against the spec. Run it locally with:

```bash
pip install pyyaml
python scripts/validate_skills.py
```

## License

[MIT](LICENSE) — free to use, modify and redistribute, including commercially,
as long as the copyright notice is kept. Individual skills may state the same
license in their frontmatter (`license: MIT`).
