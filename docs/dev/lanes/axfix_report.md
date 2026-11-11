# axfix report

## STATE AT HANDOFF

- Merged lane/axtri (`git merge --no-ff`, rc 0, no conflicts) onto main f843c7cf1.
- Cause of job 450's only red (`fd-pres-pick` byte c-default `DIFFER FLOOR 87 < 88`, both layers): the 88 came from the 7d74499bc full-suite axes log, whose compile set still held the old witness-only patterns. `differ=` counts corpus plus witness-only patterns, and axtri re-aimed the witnesses, so one fewer differs. No main commit moved it: the only src/cli/lib commit since 7d74499bc is 656690044 (-o write-if-changed), expected to be inert here.
- Re-pinned `tests/axes/memfn_arm.py` fd-pres-pick byte c-default 88 -> 87 (utf8 140 unchanged) with its rule comment. Measured on this tree (5139 corpus patterns, +2 witness-only): `MEMFN_REACH_ONLY=1 AXES=--memfn=no-fd-pres-pick tests/axes/run_axes.sh` -> `memfn arm: OK`, 47 passed, 0 failed (log: $PCREC_TMPDIR/scratch/axfix/run2.log).
- `make strict` clean.
- OWED: the cloud axes verdict (`scripts/cloudrun --owner main --kind axes --name axfix`). Expect only the known `-fprefilter` 3 lost-other (tests/litscan/spanarms.rxt:503/504/515), not mine.
