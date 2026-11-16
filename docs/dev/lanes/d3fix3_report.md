# d3fix3 report (review r12-memfn-d3fix2 FIX-NOW)

## Summary
D3G-1/2/3/4/6 fixed, D3G-5 noted-and-done (cheap). Merged origin/main (ea83fbc01) first: one docs conflict in docs/dev/reviews/CLAUDE.md (kept both sides). The merge did not move the census (gate green unchanged: 78/174/119/247, compiles/failed/records equal the pins), so NO re-pin: lost 0, gained 0. Review filed as docs/dev/reviews/2026-11-15-r12-memfn-d3fix2.md and indexed. Only tests/memfn/d3_floor.py and run_d3floor.sh changed; nothing under src/ or memfn/src/, no emitted byte.

## Fixes by id (S3234-S3237 used; plants now 13 per cell)
- D3G-1: new cell_why() = verdict + set_why + remedy, THE per-cell function; main() and every plant call it. S3232 swap is planted in the RECORDS (two pat_hex traded, counts equal), plus S3232-swap-gained, S3233 pure loss (named), S3234 pure gain (named). RED repro on 6af642db1: neutered set line kept 40/40 plants green (review). GREEN: with the set line in cell_why replaced by `pass`, 16 plants go WRONG (S3232 x2, S3233, S3234 per cell), rc 1.
- D3G-2: repin_refusals(): missing cell, 0 compiles, census below the live DIFFER pin, compiles below the pinned count -> rc 1, nothing written (D3FLOOR_REPIN_SHRINK=1 / --shrink allows fewer compiles only). Repro (utf8/c-vm sweep empty): old rc 0 and pins 0; new rc 1, 3 refusals, both files untouched (cmp). Plants S3235 empty, S3236 sub-pin, S3237 short.
- D3G-3: --repin rewrites d3_floor.tsv's four rows (bands 0, comment block kept, provenance = note), both files built before either is written. Verified on a stale copy (77 -> 78 rewritten, only provenance differs from the pin).
- D3G-4: run_d3floor.sh REPIN runs python without exec, then `exit $?`; a full REPIN run left the scratch dir count unchanged (2 foreign dirs, not mine, untouched).
- D3G-6: one remedy text per cell, naming `D3FLOOR_REPIN=1 bash tests/memfn/run_d3floor.sh` and both files; inline "re-pin d3_floor.tsv" removed from the count messages. Docstring SELF-TEST paragraph updated.
- D3G-5: note defaults to `git describe --always --dirty` (shown: v0.2.0-beta-7551-gfbf668d0d-dirty).

## Validation
make -j4 up to date; `make test-memfn-d3floor`-equivalent (run_d3floor.sh) rc 0, 4 cells ok, 52/52 plants ok; the repros above; make strict rc 0; tests/memfn/run_arch_blind.sh 17/0. Full REPIN run reverted (checkout) since numbers equal the pins. No make test, no box jobs.

## STATE AT HANDOFF
Branch lane/memfn-d3wire, rulings file empty (no entry applied). Ready for the one-critic check.
OWED: none
