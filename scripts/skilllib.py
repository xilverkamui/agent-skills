"""Shared helpers for the repo scripts."""
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"            # own skills (MIT)
THIRD_PARTY = REPO / "third-party"  # vendored skills (their own licenses)
SHARED = REPO / "shared"            # single source for files used by several skills
DIST = REPO / "dist"

SHARED_MANIFEST = "shared.txt"      # per-skill list of files copied from shared/
UPSTREAM_FILE = "UPSTREAM.md"       # provenance of a vendored skill


def skill_dirs(roots=(SKILLS, THIRD_PARTY)):
    out = []
    for root in roots:
        if root.is_dir():
            out += sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))
    return out


def read_frontmatter(path: Path):
    """Return (dict, body) from a Markdown file with YAML frontmatter, or (None, text)."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    if not m:
        return None, text
    return (yaml.safe_load(m.group(1)) or {}), text[m.end():]


def parse_shared_manifest(skill_dir: Path):
    """Lines: '<file in shared/> [-> <dest in skill>]'. '#' starts a comment.
    Without '->' the file keeps the same relative path inside the skill."""
    f = skill_dir / SHARED_MANIFEST
    if not f.is_file():
        return []
    pairs = []
    for n, raw in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        src, _, dst = (s.strip() for s in line.partition("->"))
        dst = dst or src
        for p in (src, dst):
            if p.startswith("/") or ".." in Path(p).parts:
                raise ValueError(f"{f}:{n}: path must be relative and inside the folder: {p}")
        pairs.append((SHARED / src, skill_dir / dst))
    return pairs
