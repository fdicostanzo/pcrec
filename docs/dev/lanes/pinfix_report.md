# pinfix: emit_sweep orphan DIFFER_PINS manifest `a.{1,5}z`

## Cause
`scripts/emit_sweep.py` `report_arms` (about line 1560): when a DIFFER_PINS
cell names a manifest pattern and `full_population` is true but the pattern
is not in the swept population, the cell gets the verdict "MANIFEST ... NOT IN
THE POPULATION (K35)" and the run exits 1. B3b's cells for
`--memfn=no-fd-pres-pick` (scripts/emit_sweep.py:565-566, 903f94667) name
`a.{1,5}z`, which occurred only in tests/memfn/rows.tsv and
pres_pick_witnesses.tsv, in no .rxt, so the pin had no population. Not a byte
mover: both sides read identical counts.

## Fix
- tests/litscan/gen_presence_deny.py: one new CASE, `a.{1,5}z` (byte, 9
  subjects); regenerated tests/litscan/presence_deny.rxt (+1 block, +59 case
  lines, appended; python3 re AND libpcre2 agree, generator exits on
  disagreement). `--check-pcrec build/pcrec`: 0 failures under default and
  each of the three denies.
- Pins moved by that corpus edit (found by running the suites):
  - emit_sweep DIFFER_PINS no-fd-pres-pick c-default: 187 -> 188 (byte),
    262 -> 263 (utf8); the manifest pattern is now itself a mover.
  - tests/rxtsource/run_rxtsource_tests.sh: CENSUS_BLOCKS/RUNSH_BLOCKS
    5801 -> 5802, CENSUS_LINES/RUNSH_LINES 71070 -> 71129, C3_PASS 20306 ->
    20365, C3_VERIFIABLE 22466 -> 22525.
  - tests/startset/manifests/manifest_s2_vm_forced.tsv: +1 row
    (presence_deny.rxt:643), as the vmhat mover check demanded.
  - tests/litscan/CLAUDE.md entry updated. The check itself is not weakened.

## Reach
`emit_sweep --arms start` log: `byte --memfn=no-fd-pres-pick c-default
differ=188/188 floor=188/0`, utf8 `263/263 floor=263/0`; no MANIFEST verdict
lines. The manifest check requires `manifest_hit` on both sides, so the 188
includes the pattern differing. Before: floor 187 was met by 187 other
patterns while the manifest was an orphan.

## Commands and verdicts
- `python3 -I scripts/emit_sweep.py --bin build/pcrec --ref-bin build/pcrec --tree <wt> --no-self-check --streams c-default,c-vm --arms start`: rc=0 (build/pf/sweep2.log, 262 s, 4627 distinct patterns).
- `make test-startset`: green after the manifest row (before: 1 mover not in manifest, as expected).
- `make test-rxtsource`: red on census moves, then 0 failed after re-pin.
- `bash tests/memfn/run_presence.sh deny-answers`: rc 0, 24 passed.

## OWED
Full `make test` (box rule: not run); axes allowances / size tripwires not
checked beyond a grep for the old census numbers (none found); codegen and
registry suites not run (no emitter change, corpus-only edit).
