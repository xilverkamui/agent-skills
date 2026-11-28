# Changelog: learn-tutor

Versioning follows the repository rules in [VERSIONING.md](https://github.com/xilverkamui/agent-skills/blob/main/VERSIONING.md).

## [1.0.0] - 2026-11-28

### Added
- Initial release: one adaptive tutor skill for Indonesian SMP students (grades 8-9) covering mathematics and science (biology, physics, chemistry), with a reference file per subject.
- Subject routing from the content of the question, so students do not have to name the subject; overlap cases such as speed and density load both subjects.
- National curriculum (Kurikulum Merdeka) by default, mixed with Cambridge Lower Secondary per subject. Detects Cambridge from signals and asks once, after helping, when unsure. Notation and language follow the curriculum in use.
- Help modes: short direct answers, explanations, full solutions on request, a subject-specific hint ladder for practice, and answer checking that names what is right before locating the error.
- Shared mini quiz and study plan rules: one quiz offer per topic, one question at a time, closing assessment without a grade.
- Student safety rules: no procedures for hazardous experiments, no medical advice, care for distress, no personal data requests, and guiding instead of answering during an exam.
- Source rules: sources only for health, safety, contested or recent topics, and only what was verified.
- `evals/routing-tests.md` with 17 prompts for testing routing and behavior.
