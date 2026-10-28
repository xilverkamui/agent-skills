#!/usr/bin/env python3
"""Validate every skills/*/SKILL.md against the Agent Skills spec (agentskills.io)."""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def check(skill_dir: Path) -> list[str]:
    errs = []
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return ["missing SKILL.md"]
    text = md.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    if not m:
        return ["SKILL.md must start with YAML frontmatter between '---' lines"]
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return [f"invalid YAML: {e}"]
    if not isinstance(fm, dict):
        return ["frontmatter must be a mapping"]

    name = fm.get("name")
    if not isinstance(name, str) or not name:
        errs.append("'name' is required")
    else:
        if len(name) > 64 or not NAME_RE.match(name):
            errs.append(f"'name' {name!r}: use lowercase a-z, 0-9, single hyphens, max 64 chars")
        if name != skill_dir.name:
            errs.append(f"'name' {name!r} must match folder name {skill_dir.name!r}")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errs.append("'description' is required")
    elif len(desc) > 1024:
        errs.append(f"'description' is {len(desc)} chars (max 1024)")

    comp = fm.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or not 1 <= len(comp) <= 500):
        errs.append("'compatibility' must be 1-500 characters")

    meta = fm.get("metadata")
    if meta is not None and (
        not isinstance(meta, dict)
        or not all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items())
    ):
        errs.append("'metadata' must map strings to strings (quote numbers, e.g. version: \"1.0\")")

    unknown = set(fm) - ALLOWED
    if unknown:
        errs.append(f"unknown frontmatter field(s): {', '.join(sorted(unknown))}")

    if len(text.splitlines()) > 500:
        errs.append("warning: SKILL.md over 500 lines; move detail into references/")
    return errs


def main() -> int:
    dirs = sorted(p for p in ROOT.iterdir() if p.is_dir()) if ROOT.is_dir() else []
    failed = 0
    for d in dirs:
        errs = check(d)
        hard = [e for e in errs if not e.startswith("warning")]
        status = "FAIL" if hard else "ok"
        print(f"[{status}] {d.name}")
        for e in errs:
            print(f"    - {e}")
        failed += bool(hard)
    print(f"\n{len(dirs)} skill(s) checked, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
