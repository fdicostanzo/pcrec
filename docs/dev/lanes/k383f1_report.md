# k383f1 report

## Summary
Kit manager's ruling on F1 applied: the 25 `enter_back` ver-4 rows left J5 and are job and group `J5B` in
`docs/design/memfn/span_cards/slot/plan.py`. J5 is as before K38-3 (16 arms). J5B is UNSCHEDULED and UNMEASURED; art.py
still refuses a step-back arm by name. Note `[k383 F1]` recorded in the K38-3 row of
`docs/design/memfn/span_runs_sheet.md` and in `span_cards/slot/CLAUDE.md`. Commits on lane/memfn-k383.
OWED: none

## The J5 split
- plan.py: `row("J5B", Arm(key, "J5B", ...))` for the back rows; comment updated.
- est.py: the selftest's synthetic record writes cells only for jobs in `record.JOBS`; without this J5B (planned, not
  in the record's jobs) made 30 of 52 selftest cases refuse ("cells.J5B.tsv ... unplanned").
- Not touched: `record.JOBS`, `jobs/common.sh` (J1..J5 only, so no window job runs J5B). `plan.py groups J5` = 3
  (J5.base, J5.ctl, J5.enter); k383's report said 4 because J5.back was a group then.
- `plan.py report`: J5 16 arms / 18 points; J5B 51 arms / 53 points (25 rows + base/twins + ctl).

## Checks
- `plan.py report` rc 0.
- `run.py dry J5`: green, 16 arms, 7 launches gate + round check ok, "groups 3".
- `run.py dry J5B`: refuses: `art: REFUSED: kit.enter_back.1.NONE.0: the step-back arm (t = 0) has no artifact
  specification yet ...`.
- `est.py selftest`: 52 cases, 0 wrong (after the est.py line; 30 wrong before it).
- `tests/memfn/run_finder.sh`: finder_check 1109/0 (whole script; k383's 906/0 was its check C subset, sets+store);
  total 3415/0. No card or store file changed, so check_store's ver-3 comparison is unmoved.
- S3105 DETECTED: `slot/sabotage.sh SCRATCH d1` -> `d1 DETECTED (plan dry run rc 1: plan: card enter_back@4 dim back
  has no DIM_FIELD line ...)`, 1 DETECTED 0 MISSED.

## Charter-vs-committed checklist
- [x] enter_back rows out of J5 into J5B (job and group)
- [x] `dry J5` works with 16 arms
- [x] J5B dry run refuses with the art.py message; art.py unchanged
- [x] `[k383 F1]` note in span_runs_sheet.md K38-3 row and slot/CLAUDE.md
- [x] plan report, est selftest, check C, S3105 shown
- [x] no suites, no monread, job 590 untouched, nothing merged or pushed

## STATE AT HANDOFF
All committed on lane/memfn-k383; nothing owed. J5B waits for its card to be scheduled for measurement (artifact form and F2 designed then).
