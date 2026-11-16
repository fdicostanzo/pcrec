# d3fix2 report (sonnet): r11 FIX-NOW on the D3 floor gate

## Summary
D3F-1 and D3F-2 both done and validated before 00:15. Bands are 0, any census or population change reds in the verdict
itself with "census changed: re-pin tests/memfn/d3_floor.tsv", and the census is pinned as a SET (tests/memfn/d3_census.tsv).
No change under src/ or memfn/src/, no emitted byte.

## Fixes by id
- D3F-1: census_band/pop_band/records_band = 0 in d3_floor.tsv (header cites the measured spread 0 over four sweeps).
  verdict() appends the re-pin message on any count mismatch. A WRONG plant now prints its text
  (`D3-FLOOR-PLANT-WRONG ...`); the summary counts failed_cells and failed_plants apart. Critic's +1 repro: before, red only
  through "only 24 of 32 plants" with S3228-lose-one / S3231-lost-pattern WRONG; after, the cell itself is RED with the
  re-pin message and the plants are skipped on it (honest line).
- D3F-2: d3_census.tsv (626 rows, sorted, provenance header). set_why(): lost members red and named, gained red and named,
  and census_floor must equal the row count. `D3FLOOR_REPIN=1 bash tests/memfn/run_d3floor.sh` (d3_floor.py --repin) rewrites
  the file and prints the member diff plus the numbers for d3_floor.tsv. Plants S3232-swap (lose one + gain one, counts
  equal: RED naming both) and S3233-lost-named; PLANTS=10 per cell, run_d3floor.sh reads that line (one source, the r11 minor).
  The critic's in-place swap repro (run G shape) was RED after, green before.
- Docs: NOTES.md and the d3_floor.py docstring no longer say "counts suffice"; review copied to
  docs/dev/reviews/2026-11-15-r11-memfn-d3fix.md and indexed.
- Not done (PLAN line, trigger: the next d3 re-pin): the same set pin for "compiled at pin time and now fails" (the failed
  count stays an exact count); the movers <= census subset check; one shared floor-table reader (D3W-8 general form);
  unparseable-record guard (r11 minor E).

## Validation
- `make test-memfn-d3floor`: rc 0, 4 cells ok, 40/40 plants ok, failed_cells=0 failed_plants=0.
- Repros on mutated copies of the kept sweeps: +1 census pattern RED (re-pin message, plants skipped); in-place swap RED
  (LOST 'frank|fred', GAINED 'a(b|c)+d'). Baseline sweeps green.
- `make strict` clean; tests/memfn/run_arch_blind.sh 17/0; check_claudemd_size ok; bash -n run_d3floor.sh.
- Untested end to end: the shell `D3FLOOR_REPIN=1` path (the python --repin was run directly and produced d3_census.tsv).

## STATE AT HANDOFF
Branch lane/memfn-d3wire, all committed. Rulings applied: none (file empty). OWED: none
