# Changelog: simple-suggestion

Versioning follows the repository rules in [VERSIONING.md](https://github.com/xilverkamui/agent-skills/blob/main/VERSIONING.md).

## [1.0.0] - 2026-11-09

### Added
- Initial release, based on the "Simple Suggestion - Kaizen Assistant" instruction (Problem → Cause → Solution → Result → Benefit, no invented facts, QCDSM and ANAKONDA only where relevant).
- Fills the official form FRM-DCI-001/S/001/rev.00 (sheet SS) plus an ANAKONDA sheet as page 2, via `scripts/fill_ss.py`, editing the template at XML level so the logo and in-cell checkboxes survive.
- Two-step flow: draft and confirm in chat, then generate the Excel file.
- Analisa Penyebab structure: ANAKONDA summary, 5-Why, and root cause.
- Cost rules: IDR always, one-time vs recurring, conversion rate with source and date, cost avoidance labelled as such.
- PIC Validasi defaults to the PIC Improvement (first pembuat).
- Output file name: `SS <tahun> - <Nama PIC> - <Judul Singkat>.xlsx`.
- Fit check that warns when a text box would overflow the printed form.
- `references/defaults.md` for department and date defaults. Approvers are always asked as required header data.
