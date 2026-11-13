# ssfix: re-pin the start-set VM mover manifests for the S708 witness blocks

## STATE AT HANDOFF
- Done and verified: `nice -n 19 make test-startset` green on the lane worktree (35 checks passed, 0 failed).
- CI red on main (run 43346560912, shard 6) was `[vm-movers]` auto 1 and forced 2 "not in the manifest".
- Cause as predicted by k382land: the `(a)(?:ab){2,}?ac|q` blocks appended to `tests/base/vm_lazy_rmin_prefix.rxt` (mech row S708's witness) are new VM-hat movers.
- Census: `docs/design/startset/s1/census_s1.py` run on this build (bench checkout read-only). Compared as (options, pattern) multisets over corpus rows: the ONLY difference is that one pattern, +1 in `s2_vm_auto`, +2 in `s2_vm_forced`. `s3_dfa` unchanged for corpus rows. No other mover appeared (stop rule not hit).
- Bench rows and line-shifted ids of other files in the census output were NOT taken (bench checkout drift, counted never checked).
- Push to main: see the deliver commit/merge note below.

## CHANGES
- `tests/startset/manifests/manifest_s2_vm_auto.tsv`: +1 row (`vm_lazy_rmin_prefix.rxt:253`, `--engine=vm`) and a history comment line.
- `tests/startset/manifests/manifest_s2_vm_forced.tsv`: +2 rows (`:242` own options, `:253` `--engine=vm`) and a history comment line.
