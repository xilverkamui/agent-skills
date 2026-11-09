# Form specification — FRM-DCI-001/S/001/rev.00

## Contents
1. Form layout and cell map
2. Length budgets
3. Section guidance
4. ANAKONDA sheet
5. Draft format (chat)
6. JSON input (script)

---

## 1. Form layout and cell map

The template (`assets/FRM-DCI-001-SS-rev00-template.xlsx`) has two sheets:

- **SS** — the official one-page form (A4 portrait).
- **ANAKONDA** — halaman 2, the condition analysis. The form's own note allows supporting analysis as page 2 onward.

| Section on form | Sheet SS cell | Filled from JSON field |
|---|---|---|
| Tema/ Judul | E6 | `judul` |
| Dibuat Oleh 1 (Nama / NIK) | E8 | `pembuat[0]` |
| Dibuat Oleh 2 (Nama / NIK) | E9 | `pembuat[1]` (optional) |
| Departemen | E10 | `departemen` |
| Tgl. SS Dibuat | E11 | `tanggal` |
| Kondisi Sebelum Perbaikan/ Masalah | B14 | `kondisi_sebelum` |
| Kondisi Setelah Perbaikan/ Evaluasi | J14 | `kondisi_setelah` |
| Analisa Penyebab | B17 (B17:H22) | `analisa_penyebab` |
| Solusi Perbaikan | J17 | `solusi` |
| QCDSM checkboxes | J20, K20, L20, M20, P20 | ticked automatically for each filled `manfaat` key |
| Deskripsi QCDSM | J22 (J22:P25) | built from `manfaat` |
| Biaya/ Investasi | B24 (B24:H25) | `biaya` |
| Dibuat oleh — PIC Improvement (1) | N29 | `pembuat[0].nama` |
| Diperiksa oleh — Supervisor/Manager (2) | J29 | `approval.supervisor` |
| Disetujui — Manager/ Dept Head (3) | F29 | `approval.dept_head` |
| Disetujui — Dept. Cont. Improvement (4) | C29 | `approval.dept_ci` (normally blank) |
| No. Reg | B29 | `approval.no_reg` (normally blank; filled by CI) |

The QCDSM description cell starts with the fixed line `Deskripsi masing-masing manfaat/ keuntungan (QCDSM) :`, followed by one line per category: `**QUALITY** Before: … After: …`.

## 2. Length budgets

The boxes have a fixed size so the form prints on one page. Approximate capacity at 9 pt (about 78 characters per line):

| Field | Max lines | Practical target |
|---|---|---|
| `judul` | 1 line | ≤ 95 characters |
| `kondisi_sebelum` | ~16 | ≤ 900 characters, 4–7 points |
| `kondisi_setelah` | ~16 | ≤ 900 characters, 4–7 points |
| `analisa_penyebab` | ~25 | ≤ 1,300 characters |
| `solusi` | ~16 | ≤ 900 characters, up to ~6 numbered items |
| `manfaat` (all categories together) | ~12 after the header line | ≤ 700 characters |
| `biaya` | ~7 | ≤ 450 characters |

Every short line still consumes a full line, so many short bullets use more space than their character count suggests. The script's `--check` gives the authoritative estimate.

If content does not fit, shorten wording first, then move secondary detail (test results, screenshots, configuration details) to a lampiran the user can add after page 2. Never shrink the font or change row heights.

## 3. Section guidance

### Tema / Judul
Offer 3 options with different angles, for example:
1. Action + object + purpose: "Membangun Form Builder internal di One Service untuk survei terintegrasi SSO"
2. Change-focused: "Kuesioner Bisa Dibuat Sendiri oleh User tanpa Antre Developer"
3. Outcome-focused, only if the outcome is confirmed.

Also propose a **judul singkat** of 2–5 words for the file name (e.g. "Form Builder One Service").

### Kondisi Sebelum / Masalah
- Bullet lines starting with `- `, or short prose.
- Order: the old process → the problem → who/what was affected → the impact.
- Include concrete facts the user gave (volumes, frequency, time, incidents with dates).

### Kondisi Setelah / Evaluasi
- Answers "what is different now?" Start with when it went live if known.
- Mirror the Sebelum points where possible, so the evaluator can compare.
- Keep outcomes only. Unit test counts, code coverage, and similar build evidence go to a lampiran.

### Analisa Penyebab
Use this structure (bold markup is rendered in Excel):

```
**Analisa penyebab menggunakan ANAKONDA:**
**Method:** <actual condition that explains the problem>
**Machine:** <…>

**5-Why:**
1. Kenapa <problem>? <answer>
2. Kenapa <answer 1>? <answer>
…

**Akar masalah:** <one sentence>
```

- List only the ANAKONDA categories that appear on the ANAKONDA sheet, in the same order (Man, Method, Machine, Material, Environment).
- 3–5 whys are enough. Each answer must be the cause of the previous one; stop when the answer is something the improvement addressed.
- The root cause must be addressed by the Solusi.

### Solusi Perbaikan
- One opening line: what was built/changed, where, and when it went live.
- Then numbered items `1. … 2. …` describing features, process changes, or controls.
- Use **bold** for the name of the thing built, if helpful.

### Biaya / Investasi
- State what the work used (internal development, existing infrastructure) and what was newly bought or subscribed.
- One-time vs recurring, both in IDR. Example: "Firebase ±Rp200.000/bulan (±Rp2,4 juta/tahun)".
- Currency conversion: "US$2,32/bulan ≈ Rp41.400/bulan, kurs JISDOR BI Rp17.844/USD (19 Agu 2026)".
- End with a total line in bold, e.g. `**Total biaya/investasi:** Rp0 (tanpa pembelian/lisensi baru).`
- If the user has not said anything about cost, ask. Do not assume zero.

### Manfaat / Keuntungan (QCDSM)
JSON keys and their meaning:

| Key | Label | Typical evidence |
|---|---|---|
| `quality` | QUALITY | fewer errors, better accuracy/consistency, better data integrity |
| `cost` | COST | money saved or avoided (in IDR, with source) |
| `delivery` | DELIVERY | less time or fewer steps, faster availability |
| `safety` | SAFETY (form label: Safety/ Environment) | lower operational, security, or workplace risk; environmental impact |
| `morale` | MORALE | less repetitive work, more autonomy, better user experience |

Write each as `Before: … After: …`, one or two sentences in total. The After part states the value created, not a restatement of the feature. Cost avoidance must say what it was compared against and where the price came from. Leave a key out entirely when it is not supported.

## 4. ANAKONDA sheet

Columns: Kategori · What Should Be Happen · What Actually Happen · PIC Validasi · Tempat · Hasil. (The column labels are the form's established wording; keep them.)

- **Kategori**: only relevant ones, at most one row each.
- **What Should Be Happen**: the expected condition. Derive only when the context makes the standard obvious; otherwise ask.
- **What Actually Happen**: the observable condition before the improvement, not a guess about why.
- **PIC Validasi**: defaults to the PIC Improvement. Leave the field out of JSON to use the default; set `pic` only when the user names another validator.
- **Tempat**: the place, system, or process area where the condition was observed. Ask the user.
- **Hasil**: "Valid" only after the user confirms. If not yet validated, ask; do not fill.

## 5. Draft format (chat)

```markdown
## Draft Simple Suggestion

**Opsi Tema/ Judul**
1. …
2. …
3. …
Judul singkat (nama file): …

**Header** — Dibuat oleh: … / … · Departemen: … · Tanggal: … · Diperiksa: … · Dept Head: …

### Kondisi Sebelum Perbaikan/ Masalah
…
### Kondisi Setelah Perbaikan/ Evaluasi
…
### Analisa Penyebab
…
### Solusi Perbaikan
…
### Biaya/ Investasi
…
### Manfaat/ Keuntungan (QCDSM)
**QUALITY** Before: … After: …
…

### ANAKONDA
| Kategori | What Should Be Happen | What Actually Happen | PIC Validasi | Tempat | Hasil |
|---|---|---|---|---|---|

**Perlu konfirmasi**
- …
```

Ask the user to pick a title and confirm or correct before generating the file.

## 6. JSON input (script)

```json
{
  "judul": "Membangun Form Builder internal di One Service untuk survei terintegrasi SSO",
  "judul_singkat": "Form Builder One Service",
  "tahun": 2026,
  "pembuat": [
    {"nama": "Agung Prasetyo", "nik": "LNK000664"},
    {"nama": "Mohammad Andrie Prasetiyo", "nik": "LNK000993"}
  ],
  "departemen": "TNT",
  "tanggal": "27 September 2026",
  "kondisi_sebelum": "- …\n- …",
  "kondisi_setelah": "- …\n- …",
  "analisa_penyebab": "**Analisa penyebab menggunakan ANAKONDA:**\n**Man:** …\n\n**5-Why:**\n1. …\n\n**Akar masalah:** …",
  "solusi": "Membangun modul **Form Builder** …:\n1. …\n2. …",
  "biaya": "…\n**Total biaya/investasi:** Rp0.",
  "manfaat": {
    "quality": "Before: … After: …",
    "delivery": "Before: … After: …"
  },
  "approval": {"supervisor": "…", "dept_head": "…", "dept_ci": "", "no_reg": ""},
  "anakonda": [
    {"kategori": "Method", "should": "…", "actual": "…", "tempat": "…", "hasil": "Valid"}
  ]
}
```

Notes:
- `tahun` is optional; the script takes the year from `tanggal`.
- `judul_singkat` is optional; without it the full title is used in the file name.
- Characters not allowed in file names (`\ / : * ? " < > |`) are removed automatically.
- `**bold**` and `\n` work in every long text field.
- `anakonda` may be empty or omitted; the sheet then keeps only its title and header.
