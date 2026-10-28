#!/usr/bin/env python3
"""Copy a skill from someone else's GitHub repo into third-party/, keeping a link to its source.

    python scripts/vendor.py add https://github.com/OWNER/REPO/tree/REF/path/to/skill
    python scripts/vendor.py add https://github.com/OWNER/REPO --path skills/foo --ref main
    python scripts/vendor.py check [name ...]    # is upstream newer than our copy?
    python scripts/vendor.py update [name ...]   # replace our copy with the latest upstream
    python scripts/vendor.py list

Provenance goes into third-party/<name>/UPSTREAM.md (repo, ref, path, commit, license).
The original LICENSE (and NOTICE, if any) is copied along. Skills without a license,
or marked proprietary / all rights reserved, are refused: link to them instead.
Uses plain git (no API token needed for public repos).
"""
import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from skilllib import THIRD_PARTY, UPSTREAM_FILE, read_frontmatter

LOCAL_CHANGES = "## Local changes"
LICENSE_RE = re.compile(r"^(LICEN[CS]E|COPYING)(\.(md|txt))?$", re.I)


def git(*args, cwd=None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"git {' '.join(args)} failed:\n{r.stderr.strip()}")
    return r.stdout.strip()


def parse_url(url, path, ref):
    m = re.match(r"https://github\.com/([^/]+)/([^/#?]+?)(?:\.git)?(?:/(?:tree|blob)/([^/]+)(?:/(.*))?)?/?$", url)
    if not m:
        raise SystemExit(f"Not a GitHub repo/folder URL: {url}")
    owner, repo, url_ref, url_path = m.groups()
    path = (path or url_path or "").strip("/")
    if path.endswith("SKILL.md"):
        path = path[: -len("SKILL.md")].strip("/")
    return f"https://github.com/{owner}/{repo}", ref or url_ref or "HEAD", path


def fetch(repo_url, ref, tmp: Path, blobs=True):
    """Shallow, blob-less fetch of one ref; returns the commit SHA."""
    git("init", "-q", str(tmp))
    git("remote", "add", "origin", repo_url, cwd=tmp)
    args = ["fetch", "-q", "--depth", "1"] + ([] if blobs else ["--filter=blob:none"])
    git(*args, "origin", ref, cwd=tmp)
    return git("rev-parse", "FETCH_HEAD", cwd=tmp)


def tree_sha(tmp, commit, path):
    return git("rev-parse", f"{commit}:{path}" if path else f"{commit}^{{tree}}", cwd=tmp)


def detect_license(text: str) -> str:
    t = " ".join(text.split()).lower()
    rules = [
        ("all rights reserved" in t and "permission is hereby granted" not in t, "PROPRIETARY"),
        ("proprietary" in t[:400], "PROPRIETARY"),
        ("permission is hereby granted, free of charge" in t, "MIT"),
        ("apache license" in t and "version 2.0" in t, "Apache-2.0"),
        ("gnu affero general public license" in t, "AGPL"),
        ("gnu lesser general public license" in t, "LGPL"),
        ("gnu general public license" in t, "GPL"),
        ("mozilla public license" in t, "MPL-2.0"),
        ("this is free and unencumbered software" in t, "Unlicense"),
        ("cc0" in t or "creative commons zero" in t, "CC0-1.0"),
        ("creative commons" in t and "attribution" in t, "CC-BY"),
        ("redistribution and use in source and binary forms" in t, "BSD"),
        ("isc license" in t, "ISC"),
    ]
    return next((spdx for cond, spdx in rules if cond), "UNKNOWN")


def write_upstream(dest: Path, info: dict, keep_local: str):
    front = yaml.safe_dump(info, sort_keys=False, allow_unicode=True).strip()
    body = (
        f"# Upstream source\n\n"
        f"This skill is a copy of [{info['path'] or '/'}]({info['repo']}/tree/{info['commit']}/{info['path']}) "
        f"from {info['repo']} at commit `{info['commit'][:12]}`.\n"
        f"It remains under its original license ({info['license']}); see the LICENSE file in this folder.\n"
        f"The MIT license of this repository does not apply to it.\n\n"
    )
    local = keep_local or f"{LOCAL_CHANGES}\n\nNone. Describe any edits made to this copy here.\n"
    (dest / UPSTREAM_FILE).write_text(f"---\n{front}\n---\n\n{body}{local}", encoding="utf-8")


def read_upstream(skill_dir: Path):
    fm, body = read_frontmatter(skill_dir / UPSTREAM_FILE)
    i = body.find(LOCAL_CHANGES)
    return fm, (body[i:] if i >= 0 else "")


def vendor(repo_url, ref, path, force_name=None, allow_unknown=False, keep_local="", expect_name=None):
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        commit = fetch(repo_url, ref, tmp)
        src = tmp / path if path else tmp
        git("checkout", "-q", commit, "--", path or ".", cwd=tmp)
        if not (src / "SKILL.md").is_file():
            raise SystemExit(f"No SKILL.md in {repo_url}/{path} — point the URL at the skill folder.")

        fm, _ = read_frontmatter(src / "SKILL.md")
        name = force_name or (fm or {}).get("name") or src.name
        if expect_name and name != expect_name:
            raise SystemExit(f"Upstream skill is now named {name!r}, expected {expect_name!r}. Re-add it manually.")

        # License: inside the skill folder first, then the repo root.
        lic = [p for p in src.iterdir() if LICENSE_RE.match(p.name)]
        root_extra = []
        if not lic and path:
            root_files = git("ls-tree", "--name-only", commit, cwd=tmp).splitlines()
            root_lic = [f for f in root_files if LICENSE_RE.match(f)]
            root_extra = root_lic + [f for f in root_files if f.upper() in ("NOTICE", "NOTICE.TXT", "NOTICE.MD")]
            if root_extra:
                git("checkout", "-q", commit, "--", *root_extra, cwd=tmp)
            lic = [tmp / f for f in root_lic]
        if not lic:
            raise SystemExit("No license found. Without a license the author keeps all rights — "
                             "do not copy it; add a link in README instead.")
        spdx = detect_license(lic[0].read_text(encoding="utf-8", errors="replace"))
        fm_lic = str((fm or {}).get("license", ""))
        if spdx == "PROPRIETARY" or "proprietary" in fm_lic.lower():
            raise SystemExit(f"License looks proprietary ({fm_lic or lic[0].name}). Not copied — link to it instead.")
        if spdx == "UNKNOWN" and not allow_unknown:
            raise SystemExit(f"Could not recognise the license in {lic[0].name}. Read it; if it allows "
                             "redistribution, re-run with --allow-unknown-license.")

        dest = THIRD_PARTY / name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".git"))
        for f in root_extra:
            shutil.copy2(tmp / f, dest / Path(f).name)

        info = {
            "repo": repo_url, "ref": ref, "path": path, "commit": commit,
            "tree": tree_sha(tmp, commit, path), "license": spdx,
            "fetched": dt.date.today().isoformat(),
        }
        write_upstream(dest, info, keep_local)
        print(f"[vendored] third-party/{name}  ({spdx}, {repo_url}@{commit[:12]})")
        if spdx in ("GPL", "AGPL", "LGPL", "MPL-2.0", "CC-BY"):
            print("    note: copyleft/attribution terms apply — keep this skill under its own license.")
        if spdx == "Apache-2.0":
            print("    note: Apache-2.0 — record any edits under 'Local changes' in UPSTREAM.md.")
        return name


def targets(names):
    dirs = sorted(p for p in THIRD_PARTY.glob("*") if (p / UPSTREAM_FILE).is_file()) if THIRD_PARTY.is_dir() else []
    if names:
        dirs = [d for d in dirs if d.name in names]
        missing = set(names) - {d.name for d in dirs}
        if missing:
            raise SystemExit(f"Not vendored: {', '.join(sorted(missing))}")
    return dirs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("url")
    a.add_argument("--path")
    a.add_argument("--ref", help="branch, tag or commit (default: the URL's ref or the default branch)")
    a.add_argument("--name", help="override the folder name (must equal SKILL.md name)")
    a.add_argument("--allow-unknown-license", action="store_true")
    for c in ("check", "update"):
        p = sub.add_parser(c)
        p.add_argument("names", nargs="*")
    sub.add_parser("list")
    args = ap.parse_args()

    if args.cmd == "add":
        repo, ref, path = parse_url(args.url, args.path, args.ref)
        vendor(repo, ref, path, args.name, args.allow_unknown_license)
        return 0

    outdated = 0
    for d in targets(getattr(args, "names", [])):
        fm, local = read_upstream(d)
        if args.cmd == "list":
            print(f"{d.name:30} {fm['license']:12} {fm['repo']}/tree/{fm['commit'][:12]}/{fm['path']}")
            continue
        with tempfile.TemporaryDirectory() as t:
            commit = fetch(fm["repo"], fm["ref"], Path(t), blobs=False)
            new_tree = tree_sha(Path(t), commit, fm["path"])
        if new_tree == fm["tree"]:
            print(f"[up to date] {d.name}")
        elif args.cmd == "check":
            print(f"[update available] {d.name}: {fm['repo']}/compare/{fm['commit'][:12]}...{commit[:12]}")
            outdated += 1
        else:
            if "None." not in local:
                print(f"    warning: {d.name} has local changes; they will be overwritten — re-apply them "
                      "(see git diff) and keep the notes in UPSTREAM.md.")
            vendor(fm["repo"], fm["ref"], fm["path"], d.name, True, local, expect_name=d.name)
    return 1 if (args.cmd == "check" and outdated) else 0


if __name__ == "__main__":
    sys.exit(main())
