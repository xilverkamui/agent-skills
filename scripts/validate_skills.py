#!/usr/bin/env python3
"""Validate every skill in skills/ and third-party/ against the Agent Skills spec (agentskills.io)."""
import re
import sys
from pathlib import Path

import yaml

import json

from skilllib import REPO, SKILLS, THIRD_PARTY, UPSTREAM_FILE, read_frontmatter, skill_dirs

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHANGELOG_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})", re.M)
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
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

    if skill_dir.parent == SKILLS and isinstance(meta, dict):
        errs += check_version(skill_dir, meta, md.read_text(encoding="utf-8"))

    if len(md.read_text(encoding="utf-8").splitlines()) > 500:
        errs.append("warning: SKILL.md over 500 lines; move detail into references/")
    return errs


def check_version(skill_dir: Path, meta: dict, text: str) -> list[str]:
    """Version rules from VERSIONING.md, for own skills only."""
    errs = []
    version, updated = meta.get("version"), meta.get("last_updated")
    if not version or not SEMVER_RE.match(version):
        errs.append(f"metadata.version {version!r} must be MAJOR.MINOR.PATCH, e.g. \"1.0.0\" (see VERSIONING.md)")
        return errs
    if not updated or not DATE_RE.match(updated):
        errs.append(f"metadata.last_updated {updated!r} must be a quoted date, e.g. \"2026-11-04\"")
    m = re.search(r"^Skill version: (\S+)", text, re.M)
    if not m:
        errs.append("SKILL.md needs a line 'Skill version: x.y.z (see CHANGELOG.md for history)'")
    elif m.group(1) != version:
        errs.append(f"'Skill version: {m.group(1)}' does not match metadata.version {version}")
    log = skill_dir / "CHANGELOG.md"
    if not log.is_file():
        errs.append("missing CHANGELOG.md")
    else:
        top = CHANGELOG_RE.search(log.read_text(encoding="utf-8"))
        if not top:
            errs.append("CHANGELOG.md needs entries like '## [1.0.0] - 2026-11-04'")
        else:
            if top.group(1) != version:
                errs.append(f"newest CHANGELOG entry is {top.group(1)}, metadata.version is {version}")
            if updated and top.group(2) != updated:
                errs.append(f"newest CHANGELOG date {top.group(2)} differs from metadata.last_updated {updated}")
    return errs


def check_marketplace() -> list[str]:
    """Plugin entries must point at existing skills; single-skill plugins share the skill's version."""
    if not MARKETPLACE.is_file():
        return []
    try:
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    errs = []
    for plugin in data.get("plugins", []):
        name = plugin.get("name", "?")
        version = plugin.get("version")
        if not isinstance(name, str) or not NAME_RE.match(name):
            errs.append(f"plugin name {name!r}: use lowercase a-z, 0-9, single hyphens")
        if not version or not SEMVER_RE.match(version):
            errs.append(f"{name}: version {version!r} must be MAJOR.MINOR.PATCH")
            continue
        paths = plugin.get("skills", [])
        for rel in paths:
            if not (REPO / rel / "SKILL.md").is_file():
                errs.append(f"{name}: skill path {rel} has no SKILL.md")
        if len(paths) == 1 and (REPO / paths[0] / "SKILL.md").is_file():
            fm, _ = read_frontmatter(REPO / paths[0] / "SKILL.md")
            skill_version = ((fm or {}).get("metadata") or {}).get("version")
            if skill_version != version:
                errs.append(f"{name}: plugin version {version} must equal skill version {skill_version}")
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
    market = check_marketplace()
    if MARKETPLACE.is_file():
        print(f"[{'FAIL' if market else 'ok'}] .claude-plugin/marketplace.json")
        for e in market:
            print(f"    - {e}")
        failed += bool(market)
    print(f"\n{len(dirs)} skill(s) checked, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
