# k146land: re-pin K146's moved test pins (2026-11-20)

## Summary

lane/k146land (tip 852b3b724 + commit 89d83c400) re-pins the six rxtsource pins and the vm_forced start-set
manifest that the K146 lanes' added `.rxt` cells moved. Every delta is explained by the added cells (below).
The numbers were measured by job 200-qtri1120-pins on an equivalent tree (same tests/ content as this branch:
`git diff lane/qtri1120 -- tests` is empty); the re-run on THIS tree (job 200-k146land-pins) and `make test` are
queued and OWED. `make strict` and `make test-plan-lint` are green here.

## Re-pins and their explanation

The only corpus change since the merge-base with main (f8789cd2e) is `tests/lookaround/quantified.rxt`, +274 lines,
0 deleted, one hunk at line 104 (`git diff f8789cd2e HEAD -- '*.rxt'`). Counted in the added text: 7 `pattern`
lines, 7 `features` lines, 15 comment lines, 7 blank lines, 238 case lines (214 `g` + 22 `m` + 2 `n`).

| pin (tests/rxtsource/run_rxtsource_tests.sh) | old | new | delta = added cells |
|---|---|---|---|
| CENSUS_BLOCKS, RUNSH_BLOCKS | 7224 | 7231 | +7 = the 7 new `pattern` lines |
| CENSUS_LINES, RUNSH_LINES | 99815 | 100053 | +238 = the 238 case lines (214+22+2) |
| C3_PASS | 24467 | 24705 | +238 (measured 24705; every added cell is python-verifiable) |
| C3_VERIFIABLE | 26886 | 27124 | +238, same cells; C3_SKIP 75255 and its parts unchanged |

CENSUS_FILES/RUNSH_FILES unchanged (no file added). Leg C (verify_rxt.py) had 7216 expected and emitted 7223: it
is derived from the census (7231 minus the 8 head-demoted blocks), not pinned separately, so no edit. Each pin
line carries a new "lane k146land (2026-11-20)" history prefix stating this; the check's own "never recompute"
rule was followed (values from the check's FAIL output, cross-checked against the diff count above).

Manifest tests/startset/manifests/manifest_s2_vm_forced.tsv ([vm-movers] vm arm; the log said 6 not in manifest,
3 manifest rows not movers): the three old movers shifted by +274 lines (:108/:114/:121 -> :382/:388/:395; same
patterns, hex asserted unchanged when editing) and three of the seven new blocks are `--engine=vm` movers
(:266, :282, :331, all `--features lookaround,atomic-groups`; hex read off the pattern text). 6 = 3 shifted + 3 new.
The other 4 new blocks (:115, :139, :299, :357) are not movers. Rows kept in the file's id-string order; a header
note records it.

## Checks run

- `make strict` here: rc 0 (log /var/tmp/pcrec-pcrec/scratch/k146land/strict.log).
- `make -s test-plan-lint`: 2 passed, 0 failed.
- Commit hook "staged checks": 52 passed, 0 failed.
- NOT run here (owed to the queue): `make -k test-rxtsource test-startset` on this tree (the box was held by
  l3build mech jobs, queue length hours).

## Validation queued

- 200-k146land-pins: builds this tree, runs `make -k test-rxtsource test-startset`; log
  /var/tmp/pcrec-pcrec/scratch/k146land/pins.log. Expect no FAIL lines.
- Batch b202611201156211532714: 200-k146land-b...build, 201-...strict, 202-...test (scripts/perfrun --label
  k146land, cap 3996; perfrun's own wall cap is now 3600). Read with scripts/verdict and the perfrun note.
- The quantified.rxt cells are new mover sites for the hat, but no strategy/emitter changed in this commit
  (tests only), so no REACH_ONLY mech run.

## STATE AT HANDOFF

Branch lane/k146land committed (re-pin commit 89d83c400 plus this report). Validation OWED: the two queued
items above. If pins.log shows any number different from the table, that is a delta the added cells do not
explain: stop and report. No rulings file entries (none existed).

OWED: none from this lane (the two queued runs above are the queue's; their verdicts are read by main).
