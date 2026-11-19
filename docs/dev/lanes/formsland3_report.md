# formsland3 report (sonnet, 2026-11-17)

## Summary

Merged lane/memfn-formsfixe (r37 cards.py fixes) and lane/memfn-formsfixf (G2 window / lever fence fixes, plants
S3300-S3304) into lane/memfn-forms. No conflicts of any kind; no doc line needed hand-merging. Validation green,
movers 0. Note: the history-index line for formsland3 is added in this lane's own commit.

## Merges

- formsfixe: clean `ort` merge (7 files: cards.py, r45_reply.md, review r37, reports). 13b6743e2.
- formsfixf: clean `ort` merge (11 files: g2_win_gen.c, run_g2_win.sh, run_shell_checks.sh, cloud_mech_shards.tsv
  S3300-S3304 once each, five sabotage scripts). 0e055d01d.
- The history index was touched by neither branch, so no conflict there; the mech shard table carries each new id once.

## Validation

All local, niced, -j4, gnutimeout; logs in scratch/memfn/formsland3/.
- make strict rc 0; make test-codegen rc 0; test-registry rc 0; test-rxtsource rc 0; test-memfn-finder rc 0;
  test-memfn-link rc 0; test-resource rc 0; test-cli rc 0; test-compound rc 0;
  tests/compound/run_lever_fence.sh: PASS G7 lever fence (3 checks, 4 controls).
- make test-memfn-g2 (quick): rc 0, checks passed 70358673, failed 0 (954 s).
- memfn/tests/run_g2_win.sh: rc 0, checks passed 27348, failed 0, wall 151 s ("G2W wall total 151s").
- cards.py selftest: 89 checks, 0 failed.
- cards.py dry (WIDTH_FLAG=none, --quick): cells 1374, built and gated 1374, failures 0; distinct compiles 269.
  Deny check: 42 arm-I artifacts with no span loop, 54 non-I with one (reach), failures 0. Step 2b's deny check
  reports reach (h64) 0, "WOULD REFUSE: DENY CHECK VACUOUS" -- expected under WIDTH_FLAG=none (no width flag, no
  span loop at h64); the real run uses --window-search-width=4095. Not a regression, not re-run with the flag.
- Mech shard table: `bash tests/ci/cloud_mech_check.sh tests/ci/cloud_mech_shards.tsv`: PASS, 90 shards hold the
  1330 sabotage ids exactly once. (tests/ci/check_shards.sh is the test-section control, not this one; run bare it
  reports zero section names.)
- `python3 -I scripts/m6read_check_sab_anchors.py`: rc 0.
- emit_sweep vs 3ede650a0: movers=0 asymmetric=0 on every population line, rc 0.

## STATE AT HANDOFF

Branch lane/memfn-forms, tip = this report's commit on top of 0e055d01d. Rulings file formsland3_rulings.md was empty;
no ruling applied. No full make test, queue job, timing or cloud run was done (as briefed).
OWED: none
