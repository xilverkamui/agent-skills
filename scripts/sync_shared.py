#!/usr/bin/env python3
"""Copy files from shared/ into each skill that lists them in its shared.txt.

    python scripts/sync_shared.py          # copy / refresh
    python scripts/sync_shared.py --check  # only report; exit 1 if anything is out of sync (used in CI)
"""
import filecmp
import shutil
import sys

from skilllib import REPO, SKILLS, parse_shared_manifest, skill_dirs


def main() -> int:
    check = "--check" in sys.argv[1:]
    problems = changed = 0
    for d in skill_dirs((SKILLS,)):
        try:
            pairs = parse_shared_manifest(d)
        except ValueError as e:
            print(f"[FAIL] {e}")
            problems += 1
            continue
        for src, dst in pairs:
            rel_src, rel_dst = src.relative_to(REPO), dst.relative_to(REPO)
            if not src.is_file():
                print(f"[FAIL] {d.name}: {rel_src} does not exist")
                problems += 1
            elif dst.is_file() and filecmp.cmp(src, dst, shallow=False):
                continue
            elif check:
                state = "differs from" if dst.exists() else "is missing; source"
                print(f"[OUT OF SYNC] {rel_dst} {state} {rel_src} (run scripts/sync_shared.py)")
                problems += 1
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"[copied] {rel_src} -> {rel_dst}")
                changed += 1
    if check:
        print("shared files: " + ("OK" if not problems else f"{problems} problem(s)"))
    else:
        print(f"{changed} file(s) updated, {problems} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
