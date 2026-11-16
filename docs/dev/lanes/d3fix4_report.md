# d3fix4 report

## Summary
The ruled r21 review (D3H-1/2/3) is fixed in tests/memfn/d3_floor.py, run_d3floor.sh and d3_floor.tsv. No floor value or census row changed. The review is copied unchanged to docs/dev/reviews/2026-11-16-r21-memfn-d3fix3.md (no same-day r21 collision) and indexed in docs/dev/reviews/CLAUDE.md. D3H-4/5 are noted, not fixed.

## Fixes by id
- D3H-1: PLANTS = 15 (12 record plants + 3 refusals). run_d3floor.sh now checks `-ne` against 4 x PLANTS and prints "d3floor: N plants ok of M".
- D3H-3: d3_floor.tsv header names D3FLOOR_REPIN=1 / D3FLOOR_NOTE, what REPIN rewrites and refuses; the hand-copy text is gone.
- D3H-2: `repin_decide(floors, sets, pins, shrink, write, cells)` decides refuse-or-write and the rc; main() --repin and plants S3235-S3237 both call it. A plant is ok only if rc 1 and write() never called (accept case: rc 0 and written).

## Validation
- `make strict`: rc 0.
- `make test-memfn-d3floor`: green, "d3floor: 60 plants ok of 60", checks passed 1.
- D3H-1 proof (scratch copy, S3237 refuse() deleted): 56 plants ok, want 60, `-ne` check goes red.
- D3H-2 proof (scratch copy, `if refused:` neutered to `if False:` in repin_decide): rc 1, S3235-S3237 WRONG on every cell (rc=0 wrote=1), 48 plants ok. The guard now lives in the shared function, so the neutering is there, not in main().
- tests/memfn/run_arch_blind.sh: 17 passed, 0 failed.

## STATE AT HANDOFF
Last ruling applied: none (d3fix4_rulings.md empty). Tip is the commit after 251a79c57 (this report). 
OWED: none
