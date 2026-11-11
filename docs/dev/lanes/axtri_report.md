# axtri report

## STATE AT HANDOFF

Input: full suite 300-main-fullsuite, frozen 7d74499bc, red stage `axes`
(`build/full_suite/20261110_7d74499bc/axes.log`). One failing unit: `[RUNAXES]
--memfn= arm reach` (22 checks of 335). Every answer-identity axis in that log is
OK (0 mismatches); no wrong answer.

- Failure: tests/axes/memfn_arm.py DIFFER floors and witnesses. fd-pres-pick
  88/140 < 144/225; precheck-assign-byte 131/189 < 153/220; pres-set-lead
  6/11/3/3 < 14/18/7/8; witnesses inert: fd-pres-g1 utf8 `abc+d`, pres-set-lead
  `é{2,}cat` (byte) and `a{3,}(?i:cat)` (utf8).
- Class: STALE PIN (not a regression, not a flake). Deny moves fewer patterns
  because span arms R1 (f7eb10528, in a0a829246..7d74499bc) gives counted-repeat
  patterns a longer required run the pick / byte assign / set lead cannot change.
  Same cause and same direction as flr2's emit_sweep re-pin 68089d755
  (pres-set-lead 6/11/3/3, fd-pres-pick 87/139 there vs 88/140 here: the two
  scripts count slightly differently).
- Fix: commit "axtri: re-pin memfn_arm floors/witnesses" on lane/axtri
  (tests/axes/memfn_arm.py only): the nine floors above, fd-pres-g1 utf8
  witness `ab+c`, pres-set-lead witnesses `(?i:select)\d+x`. The fd-d1,
  fd-pres-g1, window-search floors and the vrun cells measured above their
  floors/at their floors and are untouched.
- Proof: before = the suite log (22 FAIL lines). After (sampled): memfn_arm.py
  `--every 40 --subset` over fd-pres-g1 and pres-set-lead, both layers, on a
  fresh build at 7d74499bc: "memfn arm: OK, checks passed 59, failed 0"
  (witnesses applied, floors not applied under --every). Floors themselves are
  copied from the full-corpus log counts; their full-corpus proof is OWED.
- OWED: queued `45x-main-axtri-axes` (docs/dev/lanes/axtri_axes_job): AXES= the
  four rows by spelling, both layers, AXES_FULL=1; green line `axes: DONE rc=0`
  in its job.log.axes.
