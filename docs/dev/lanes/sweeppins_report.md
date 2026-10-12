# sweeppins report (2026-10-12, sonnet)

Two pre-existing defects in `scripts/emit_sweep.py`, found by the kit's slot24
triage (ref-vs-ref at a080c69a, so not the kit's). Only `scripts/emit_sweep.py`
changed. Branch `lane/sweeppins` from main fae3987e8.

## 1. VARIANT_PINS refresh

Done with the script's own mechanism, no hand-edited numbers:
`python3 scripts/emit_sweep.py --ref HEAD --tree-rev HEAD --variant all --no-variant-floor --no-self-check --emit-pins pins.py`
(the header command without `--trace`; TRACE_VARIANT_RECORDS_FLOOR not
re-measured), the emitted dict pasted through `pprint` (width 120 reproduces the
block's existing layout exactly). One reason per group is in the comment above
`VARIANT_PINS`:

- reach and most tag floors rise: corpus growth (5,645 rows now), old floors had
  1-4% slack; floors are again AT the measured smaller side.
- four floors fall by one (lowsize/utf8 no-size-cap 290->289, stderr-default
  357->356; lowboth/utf8 267->266, 416->415): seambuild (337f9a6ed, abi 76).
  BISECTED here, not inferred: `--ref 337f9a6ed^ --tree-rev 337f9a6ed --variant
  lowsize --bases utf8` reads no-size-cap 290/289 (a/b), the parent holding the
  old pins.
- thin-tag manifests: `((a)+)+` -> `((ab)+c)+`, `(\p{Xwd})` -> `(\p{Xwd})x`, three
  witnesses -> `a.{1,50000}z`, lowboth/byte stderr-default no longer thin.

## 2. Composition floors per arm

`composition_producing_floor` / `composition_artifacts_floor` in PINS count the
PLAIN arm (fixtures building >= 1 artifact; .c/.h files written, both sides,
`--features all`). `-e utf8` reads 36 / 104 on both sides (ref-vs-ref), so the
plain 37 fired. New `COMPOSITION_EXTRA_PINS`, keyed by the run's extra tuple as
`TRACE_EXTRA_PINS` is (same key, no new mechanism), read through
`composition_floor()`: `("-e","utf8")` producing 36 (AT measured, zero slack like
plain), artifacts 98 (6 below measured 104, plain's own margin). The population
each floor counts is stated in the comment above the dict (K35).

## Validation (jobs 8, full 5,645-row population, 384 composition files)

| run | result |
|---|---|
| variants, lane (HEAD) vs main fae3987e8 | `VARIANTS: CLEAN`, 0 movers / 0 asymmetric, 0 floor/manifest lines |
| variants, main vs main | `VARIANTS: CLEAN`, same |
| utf8 (`--extra=-e utf8 --no-differ-floor`), lane vs main | rc 0, composition 36 / 104, 0 floor/manifest lines |
| utf8, main vs main | rc 0, same |
| control A: producing floor 36 -> 37 (copy of the script) | rc 1, `COMPOSITION PRODUCING FLOOR VIOLATION: 36 < 37` |
| control B: lowsize/utf8 no-size-cap floor 289 -> 290 (copy) | rc 1, `TAG FLOOR side a/b: no-size-cap 289 < 290`, `VARIANTS: FAILED` |

Control copies were deleted. Lane-vs-main equals main-vs-main in emitted content
(the lane touches only the script), as expected.

Nothing owed. Not run: `--trace` variants (records floors untouched).
