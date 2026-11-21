# formsfixf report (review r37 H5, H6, H8)

## Summary
Three check-adequacy gaps from review r37 are closed. Each has a sabotage row (S3300-S3304) that goes DETECTED.
No `src/`, `cli/`, `lib/` or `memfn/src/` byte moved (diff against 3ede650a0 is empty there), so the emit sweep has 0 movers
by construction; the emitted default is the same as 3ede650a0.

## Fixes
- H5 (memfn/tests/g2/g2_win_gen.c, memfn/tests/run_g2_win.sh): the long-row `pinned` counter is split by state
  (`pinned_force` printed beside `pinned`); the default pass floors the default state (8), the force (8) and its
  `pinned_sites` (floor 50, measured 55). Deleting the pin (S3300) or the force's count (S3304) goes red.
- H6 (same files): `lever_controls` counts into its own `lever_ok`; the generator prints `lever controls ok=N of 8`
  and the script holds it by equality (8 of 8). FLOOR_CONTROLS re-measured to 207 (230 measured) and its comment fixed.
  Deleting the call (S3301) goes red.
- H8 (tests/compound/run_shell_checks.sh section 4): the accepted rows compile `[0-9a-f]{32}` at `-o -`, assert head 8
  renders `_j = 8; for (`, `08` gives head 8's artifact, heads 7 and 9 differ (the check can fail), and `4095`
  gives the same artifact as 4094 and differs from head 8. Limit: at width 32 head 4095 is past the pattern's reach, so
  it cannot be told from 4094 except by being equal to it; a wider pattern than the kit's window renders no loop at all.

## Validation
- Sabotage rows (run_sabotage_matrix.sh S3300..S3304): all five DETECTED, unexpected 0, undetected 0.
  S3300 g2win 2 fail; S3301 g2win 1 fail; S3302 compound 1 fail; S3303 compound 2 fail; S3304 g2win 1 fail.
  S3302/S3303 are the CLI and sites halves of the forwarded head.
- `make strict` rc 0. `memfn/tests/run_g2_win.sh` (full grid, with ASan at head 0): 27348 passed, 0 failed, rc 0.
- `make test-compound` PASS (section 4: 17 checks, 0 failed). `make test-cli` 0 failed.
- `tests/compound/run_lever_fence.sh` PASS; `scripts/m6read_check_sab_anchors.py`: all anchors resolve.
- cloud_mech_shards.tsv gains S3300-S3304 on shard 45 at the mean estimate (existing convention).
- No full make test, no queue jobs, no timing, no cloud.

## STATE AT HANDOFF
Branch lane/memfn-formsfixf, all committed. No rulings file entries were present.
OWED: none
