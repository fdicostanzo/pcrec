# pinfix report (round r8-memfn-mcfixc, FIX-NOW: ADQ-3, ADQ-2)

## Summary
ADQ-3: est.py now refuses a missing cells pin or manifest pin on any record that carries a `window` key. A legacy
record (no `window` key: s2d1/s2d2) still prices, with the NOTE. ADQ-2: 609 and 610 pass
`--second FIRST_RUNDIR FIRST_RUNDIR_AVX2` to d197_rule.py when those two optional window.vars entries are set. No
change to what a valid pinned record scores; no emitted byte.

## Fixes by id
- ADQ-3 (est.py, sabotage.sh; commit 628487669). PREMISE: reproduced on 38869c333 (an mfcard-window synth with
  `cells_sha256_J2` deleted: priced, rc 0, NOTE only). RED then GREEN: now `CELLS PIN absent cells.J2.tsv ...` refused.
  `legacy_record(rec)` = `"window" not in rec["run"]` gates both tolerances: read_cells' cells pin and
  manifest_check's manifest pin (`MANIFEST PIN absent`). Selftest: `mf_nopin` retargeted to a window-less synth
  (still priced with the NOTE); new cases S3224 (cells pin line deleted from an mfcard record: refused) and S3225
  (manifest pin line deleted: refused); the r11-REV15-1 `unpinned` case now also drops the window key (it models a
  legacy record). Sabotage row m7 (S3226): the cells-pin refusal off -> the S3224 case goes WRONG.
- ADQ-2 (job files, kit scratch jobs/; backup in scratch/memfn/pinfix/jobs.bak/; diff stat: common.sh +11,
  609-kit-mfcard-time +2/-2, 610-kit-mfcard-confirm +2/-2, window.vars.example +4). common.sh header documents
  FIRST_RUNDIR and FIRST_RUNDIR_AVX2 (both or neither, else exit 1) and builds `SECOND_ARGS`; 609's and 610's
  d197_rule.py calls (the echoed would-run line and the real call) append it. 610's first-run arguments still come
  from window.vars (RUN_ID-derived RUNDIR plus the optional FIRST_*).
  Dry-run d197 lines (copy of the jobs dir, own window.vars, MFCARD_TREE=this worktree; R = scratch rundir path):
  - 609 unset: `d197_rule.py rule R/pinfix-dry R/pinfix-dry.avx2libc`
  - 609 set: `d197_rule.py rule R/pinfix-dry R/pinfix-dry.avx2libc --second R/mfcard-zen4-1 R/mfcard-zen4-1.avx2libc`
  - 610 unset: `... rule R/pinfix-dry R/pinfix-dry.avx2libc  --confirm R/pinfix-dry.confirm R/pinfix-dry.confirm.avx2libc`
  - 610 set: `... rule R/pinfix-dry R/pinfix-dry.avx2libc --second R/mfcard-zen4-1 R/mfcard-zen4-1.avx2libc --confirm
    R/pinfix-dry.confirm R/pinfix-dry.confirm.avx2libc`
  - one of the two vars set: exit 1 with a message.
- r8 review filed at docs/dev/reviews/2026-11-15-r8-memfn-mcfixc(.md|/), indexed in reviews/CLAUDE.md.
- IDs used: S3224, S3225 (selftest cases), S3226 (sabotage m7). S3227 unused.

## Validation
- est selftest: 70 cases, 0 wrong (68 before; +S3224, +S3225).
- d197 drill: 51 cases, 0 wrong.
- sabotage.sh m7 and m1 (with the control run): 2 DETECTED, 0 MISSED.
- tests/memfn/run_arch_blind.sh: 17 passed, 0 failed.
- make strict: clean.
- dry JMH (run.py dry JMH, scratch): rc 0; GATE ok 172 arms, ROUND CHECK ok 172 points, 0 misses.
- Not run (per brief): box jobs, make test, run_axes, mech.

## STATE AT HANDOFF
Rulings applied: none (pinfix_rulings.md empty).
OWED: none
