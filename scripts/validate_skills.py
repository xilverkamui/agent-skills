#!/usr/bin/env python3
"""Validate every skill in skills/ and third-party/ against the Agent Skills spec (agentskills.io)."""
import re
import sys
from pathlib import Path

import yaml

from skilllib import THIRD_PARTY, UPSTREAM_FILE, read_frontmatter, skill_dirs

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def check(skill_dir: Path) -> list[str]:
    """Return messages; ones starting with 'warning' do not fail the build."""
    third_party = skill_dir.parent == THIRD_PARTY
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return ["missing SKILL.md"]
    try:
        fm, _ = read_frontmatter(md)
    except yaml.YAMLError as e:
        return [f"invalid YAML: {e}"]
    if fm is None:
        return ["SKILL.md must start with YAML frontmatter between '---' lines"]
    if not isinstance(fm, dict):
        return ["frontmatter must be a mapping"]

    errs = []
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
        msg = f"unknown frontmatter field(s): {', '.join(sorted(unknown))}"
        errs.append(("warning: " + msg) if third_party else msg)

    if third_party:
        if not (skill_dir / UPSTREAM_FILE).is_file():
            errs.append(f"third-party skill needs {UPSTREAM_FILE} (use scripts/vendor.py)")
        if not any(p.name.upper().startswith(("LICENSE", "LICENCE", "COPYING")) for p in skill_dir.iterdir()):
            errs.append("third-party skill must keep its original LICENSE file")

    if len(md.read_text(encoding="utf-8").splitlines()) > 500:
        errs.append("warning: SKILL.md over 500 lines; move detail into references/")
    return errs


def main() -> int:
    dirs = skill_dirs()
    failed = 0
    for d in dirs:
        errs = check(d)
        hard = [e for e in errs if not e.startswith("warning")]
        print(f"[{'FAIL' if hard else 'ok'}] {d.parent.name}/{d.name}")
        for e in errs:
            print(f"    - {e}")
        failed += bool(hard)
    print(f"\n{len(dirs)} skill(s) checked, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
