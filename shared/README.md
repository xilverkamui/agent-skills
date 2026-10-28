# shared/

Single source for files that more than one skill uses (logos, glossaries, templates…).

A skill is installed as a standalone folder, so it can't reach this directory at run time.
Instead, each skill that needs a shared file lists it in `skills/<skill>/shared.txt`:

```
# <file in shared/>  [-> <destination inside the skill>]
logo-lnk.png -> assets/logo-lnk.png
glosarium-produk.md -> references/glosarium-produk.md
```

Then run `python scripts/sync_shared.py` to copy the files in. Commit both the file here
and the copies. CI fails if a copy no longer matches its source here.

Edit shared files **here**, never the copies inside a skill.
