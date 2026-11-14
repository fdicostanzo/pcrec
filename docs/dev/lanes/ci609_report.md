# ci609: re-pin the start-set VM mover manifests for s2d27's Part D witnesses

## STATE AT HANDOFF
- Done and verified: `make -k test-startset` green on the lane worktree (35 checks passed, 0 failed, no `*** [test-` lines). Rulings file: no entries.

## CAUSE
- CI run 43609245192 (main f296774df), shard 6/18, `test-startset`: `[vm-movers]` auto 6 and forced 25 "not in the manifest". All are new `tests/litscan/d27/partd_*.rxt` blocks (s2d27's Part D spec-first witnesses), correct VM-hat movers never pinned.

## FIX
- `docs/design/startset/s1/census_s1.py` run on this build; vs the committed manifests the only difference is +6 auto / +25 forced rows, all `tests/litscan/d27/partd_*`; 0 rows removed or moved (stop rule not hit, no answer change).
- `tests/startset/manifests/manifest_s2_vm_auto.tsv` +6 rows, `manifest_s2_vm_forced.tsv` +25 rows, each with a history comment line. Bench rows untouched.

## VALIDATION
- `make -k test-startset` green (above).

## OWED
- CI result after landing.
