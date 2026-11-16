# Lane d3wire: R-44, the D3 floor wired into a gate

## Summary
`runpart_floor.py` (R-43) had no caller. It is now a gate: `tests/memfn/run_d3floor.sh` (`make test-memfn-d3floor`), also the last step of `make test-axes` (so the battery's axes stage runs it). The floors left the script: `tests/memfn/d3_floor.tsv` is their one home, with provenance per row. No file under `src/`, `cli/`, `lib/`, `memfn/src/` is touched; no emitted byte moves.

## Choice
Measured wall (`gnutimeout`, nice, -j4, d2496010e): four traced corpus sweeps 20.1 / 37.8 / 25.3 / 38.5 s, whole gate 125 s (probe build 4 s). Over the 60 s line, so by the ruling table NOT a `make test` section. Home: the `test-axes` recipe, which already runs `run_form_census.sh` (a census-floor gate) and is what the battery's `axes` stage calls; plus its own opt-in target `test-memfn-d3floor`. A mech row was not chosen: mech plants source lines and would re-run the 125 s sweep per row; the plants here are over the sweep data.

## Wiring
- `git mv docs/dev/lanes/r33_sim/runpart_floor.py tests/memfn/d3_floor.py`; reads `d3_floor.tsv` (cell, census_floor, movers, min_compiles, min_records, provenance: r43 kit-r43-measure, movers 370aab9fe, populations measured by d3wire).
- Population: prints compiles and records per cell; reds below min_compiles (4500, measured 5030/5031/5100/5077) or min_records (250/700/350/800, measured 380/1055/501/1177).
- Plants, run inside the script on every run (6 per cell, the shell counts 24): S3228 drops the derived-part records of mover patterns (census = floor green control; floor-1 RED), S3229 empty and truncated sweep (RED, population), S3230 floor below movers (RED). Plain control green.
- `tests/lib/san_excluded.txt` row (OWN-TIER) for the new script ([TT-9] check reddened without it).
- CLAUDE.md: tests/memfn and r33_sim updated (collect.py, build.sh, probe.c stay in r33_sim and are now gate dependencies; stated there). Historical mentions of runpart_floor in reports/ledgers left as history.
- Not in the gate: `--movers` per-pattern form (needs deny_reach sweeps); still available by hand. The MOVERS values are still the 370aab9fe measurement (review FLOORS-2 untouched).

## Validation
- run_d3floor.sh green on d2496010e: census 78/174/119/247 vs floors 58/143/99/216; 24/24 plants as expected; 125 s.
- End-to-end red: floor byte/c-vm set to 175 in a scratch tsv -> `RED: census 174 below its floor 175`, rc 1.
- `make strict` clean; `make test-codegen` green (first run red on the missing san_excluded row, fixed); `tests/memfn/run_arch_blind.sh` 17/17.
- Not run (per brief): make test, axes, mech.

## STATE AT HANDOFF
Delivered. Last rulings entry applied: none (file empty). Ids used: S3228-S3230 (in-script plants, no mech rows). Note for the manager: the first real `make test-axes` run will exercise the new last step; the battery axes stage gains ~2 min.
OWED: none
