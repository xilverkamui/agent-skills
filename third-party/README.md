# third-party/

Skills written by other people, copied here so they can be bundled with this
collection. **Each keeps its original license** (the `LICENSE` file inside its
folder); the MIT license of this repository does not apply to them.

Every folder has an `UPSTREAM.md` recording the source repository, path, commit
and license, so it always points back to the original.

```bash
python scripts/vendor.py add https://github.com/OWNER/REPO/tree/main/path/to/skill
python scripts/vendor.py list
python scripts/vendor.py check     # is upstream newer?
python scripts/vendor.py update    # pull the latest version
```

`vendor.py` refuses skills that have no license or are marked proprietary — link to
those from the main README instead. Review a third-party skill (especially its
`scripts/`) before using it.
