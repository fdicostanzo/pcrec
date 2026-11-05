# memfn kit — wake-up brief

Rewritten 2026-11-05 ~00:40. 1d is fixed, and its gates wait for main's job-300 verdict. Committed docs win on any conflict.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main is the pcrec manager session `pcrec-main`. Frank rules, sometimes directly to the kit.
Kit worktree: worktrees/memfn on branch lane/memfn-k1102 (main daf6f002b + kit commits: journal, review 2026-11-05 r1, skill/guide lessons).

## Read in order
1. This file.
2. The memfn/docs/journal.md tail (2026-11-04 night / 11-05).
3. docs/design/memfn/span_pick.md REV 5.2, the design of record.
4. The review docs/dev/reviews/2026-11-05-r1-memfn-sp1d.md (Rulings at the end), and r2-memfn-sp1c.md before it.
5. D186 + addenda, D187 (positions travel as sets), and manifesto principle 9 (seams as text).

## CURRENT STATE: span_pick STAGE 1, unit 1d FIXED, GATES HELD
Landed on main: 1a, 1f, 1g, 1b, 1c (daf6f002b). Next: 1d, then 1e. Then stage 2/3 need main's GO.
The per-unit process: an opus build lane, then a pcrec-critic code round, then a sonnet fix lane, then box-queue gates, then the done line, then main merges.

- **1d:** lane/memfn-sp1d @ c1c6ce26c (lane sp1d e9e5f035e + fix lane sp1dfix, fast-forwarded). Reports: docs/dev/lanes/sp1d_report.md and sp1dfix_report.md.
  - No mover. MF_SITE_ABI stays 23, MF_CLASS_V stays 7, no pcrec abi change.
  - Ratchet: R21 needs restating, which main does at its 1d review; the proposed recipe is in sp1d_report "Ratchet".
- **Gates 410-419** (keys kit-sp1d2-*, TREE=worktrees/sp1dfix) are in /var/tmp/pcrec-pcrec/scratch/memfn/sp1dfix/jobs/: strict, memfn, reach, ident x3, make test, mech x3 (73 rows, including S1095, S1096 re-measure, and the ofsskip rows; S917/S919 declared unreached).
  - NOT QUEUED. Main's ruling (11-05 ~00:35): hold until main POSTS job 300's verdict, not merely until 300 ends. 300 is main's full suite @ daf6f002b, ending ~10:30-11:00; main resumes 09:00 and will message. If 300 is RED, the box goes to main's triage first.
  - Queue them with `scripts/boxqueue add` (not --no-start) once main posts its go. Watch the queue.log END lines after a baseline count. Then write the done line in responses.md and message main.
  - The frozen base builds the jobs read are in scratch/memfn/sp1d/ (ref/, ref-mftrace/). Keep them until the gates are read.
- Do not touch worktrees/sp1d or sp1dfix until the gates are read.

## After 1d merges
Cut 1e (the phase-2 tables; it reads T-VERIFY's step list) from main. PLAN items from the 1d review ride later units: F4's M inputs go with row 1; F9 U-1/U-2/P4; F10 and r2 F13 (the position primitives' home) at the kit split; F12's seam snapshot items at the kit split.

## Box rules
- Frank holds 20:00-01:00 daily unless he says otherwise. Main's ruled holds win.
- Jobs only through scripts/boxqueue. Kill only with scripts/safekill. Never use /tmp.
- Never commit a header or ABI change while a run is in flight.

## Lessons (recent)
- A watcher must read queue.log END lines for the current run only; cancelled jobs in done/ false-fire.
- A scratch-queue `boxqueue add` needs `--no-start`, or it arms a runner.
- A lane waiting on its own background run may miss the notification: check the log and wake it.
