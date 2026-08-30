# docs/dev/lanes/ — per-lane restart records and delivery reports

One `<lane>_log.md` (the lane's own running log: what it did, in order,
for its restart) and one `<lane>_report.md` (the delivery: commits, the
brief's acceptance table filled with MEASURED values, findings) per lane
that chose to keep them. Optional — briefs allow it, never require it.
They are the lane's voice, not the manager's: the plan, journal and
decisions log carry the manager's record, and on any disagreement the
committed docs in docs/dev/ win. Historical once the lane is merged;
never edited afterwards.

- `w11_log.md`, `w11_report.md` — [DD-13b.W1.1] (2026-08-30, lane w11):
  the .rxt HEAD grammar, `--list-source`, the three-parser identity proof
  C1, the wiring of verify_rxt.py (C3), sabotage rows S194-S204.
- `opt41_report.md` — [OPT-4.1] (2026-08-30, lane opt41): the nullability
  gate on [OPT-4]'s count-collapsed prefilter rescue. Carries the PHASE-1
  prediction table for the bench's eleven labelled forms (stated before any
  measurement), the answer to O-10 ask (iv) with its code line, two findings
  about the brief's own premises (the K39 witnesses are NOT nullable; the
  `_LANG_WHY` value alone cannot carry the measured case), and three open
  questions. No `_log.md`: the lane's ordering is in its commits.
