#!/usr/bin/env python3
"""Build ready-to-upload zips in dist/: one <skill-name>.zip per skill.

    python scripts/bundle.py               # all skills (skills/ and third-party/)
    python scripts/bundle.py laporan-qc    # only the named skill(s)

Each zip holds the skill folder itself (laporan-qc/SKILL.md, ...), which is the
layout Claude and other agents expect on upload. Validation and the shared-file
check run first; nothing is built if they fail.
"""
import subprocess
import sys
import zipfile
from pathlib import Path

from skilllib import DIST, REPO, SHARED_MANIFEST, SKILLS, skill_dirs

EXCLUDE_NAMES = {".DS_Store", "Thumbs.db", SHARED_MANIFEST, "__pycache__", ".git"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".zip"}
FIXED_TIME = (2020, 1, 1, 0, 0, 0)  # same input -> byte-identical zip


def files_of(skill_dir: Path):
    for p in sorted(skill_dir.rglob("*")):
        rel = p.relative_to(skill_dir)
        if p.is_file() and not (set(rel.parts) & EXCLUDE_NAMES) and p.suffix not in EXCLUDE_SUFFIXES:
            yield p, rel


def build(skill_dir: Path) -> Path:
    DIST.mkdir(exist_ok=True)
    out = DIST / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        names = set()
        for p, rel in files_of(skill_dir):
            arc = f"{skill_dir.name}/{rel.as_posix()}"
            info = zipfile.ZipInfo(arc, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if p.stat().st_mode & 0o111 else 0o644) << 16
            z.writestr(info, p.read_bytes())
            names.add(rel.as_posix())
        # Own skills carry the repo's MIT license so the notice travels with the zip.
        if skill_dir.parent == SKILLS and "LICENSE" not in names:
            info = zipfile.ZipInfo(f"{skill_dir.name}/LICENSE", FIXED_TIME)
            info.external_attr = 0o644 << 16
            z.writestr(info, (REPO / "LICENSE").read_bytes())
    return out


def main() -> int:
    here = Path(__file__).parent
    for cmd in (["sync_shared.py", "--check"], ["validate_skills.py"]):
        r = subprocess.run([sys.executable, str(here / cmd[0]), *cmd[1:]], capture_output=True, text=True)
        if r.returncode:
            print(r.stdout + r.stderr)
            print(f"Stopped: {cmd[0]} failed.")
            return 1

    wanted = set(sys.argv[1:])
    dirs = [d for d in skill_dirs() if not wanted or d.name in wanted]
    missing = wanted - {d.name for d in dirs}
    if missing:
        print(f"Unknown skill(s): {', '.join(sorted(missing))}")
        return 1
    for d in dirs:
        out = build(d)
        print(f"[zip] {out.relative_to(REPO)}  ({out.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
