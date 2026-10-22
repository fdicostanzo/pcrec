# docs/dev/lanes/ — per-lane restart records and delivery reports

One `<lane>_report.md` (delivery, acceptance table with MEASURED values) and/or `<lane>_log.md` (running log) per
lane that chose to keep them, plus lane-owned evidence files.

## Standing rules

- `BOILERPLATE.md` is the standing rules every lane reads FIRST; briefs name only task, tier and deliverable. Change a rule there; do not grow briefs back.
- `BRIEF_TEMPLATE.md` is the manager's brief field list. Point at these two; never restate them here.
- A lane's report MUST be added to the history index (per-lane entry list, in the history file) in the SAME change (N-1 / D149; pcrec and kit lanes).
- `_log.md` and `_report.md` are optional. `<lane>_brief.md` is the manager's, kept only for a parked lane; delete when its row merges.
- Lane files are the lane's voice; on disagreement the committed docs in docs/dev/ win. Never edited after merge.
- Lane-written files stay inside this directory; the root scope mandate applies.

## Files / subdirectories

- `BOILERPLATE.md`, `BRIEF_TEMPLATE.md`.
- `<lane>_report.md` (about 480), `<lane>_log.md`, `<lane>_brief.md` (a `NAME_rulings.md` is polled by a running lane).
- `<name>_evidence/` and other per-lane instrument directories (`grid1/`, `costmodel/`, `rwquest/`, ...): data, drivers, logs cited by the matching report.
- Loose lane artifacts (`*.py`, `*.sh`, `*.c`, `*.patch`, `*.tsv`, `*.out`, `*.log`, `*.txt`) and lane notes/drafts.

## Pointers

`BOILERPLATE.md`, `BRIEF_TEMPLATE.md`; `.claude/skills/pcrec-manager` section 3; `docs/dev/plan.md`, `dev_journal.md`, `decisions.md`, `reviews/`.

Full text and the complete directory list (verbatim): NOTES.md here.

History (not auto-injected): docs/dev/history/claude_md/docs__dev__lanes.md
