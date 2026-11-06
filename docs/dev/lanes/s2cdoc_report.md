# s2cdoc report

## Summary
- Merged S2a's fix d9afba62b into lane/memfn-s2c (already an ancestor via 979eeae83; "Already up to date"). `tests/registry/limits_check.sh`: 39 passed, 0 failed, so S2c's constants need no allowlist entry.
- span_cards.md rev 1.3 now carries S2c-1: each arm needs min(3, 64/A) distinct phases, A the object's own `.text` alignment. At A = 64 the phase is compiler-fixed and recorded, not re-drawn. No alignment flag. J2p's objects are 64-aligned today.
- S2c-2: walk-set is folded into walk (one form hash, bc7b2e02f06fe955), so it is not a card key. The floor quote's "walk and walk-set pair" is kept as history, now noted as one figure already.
- S2c-3: S2c's placement screen (8.56 % on a loaded box) is no reading; the quiet screen is S2d's first step, before J1. Stated in the §9 S2d row and §3.2.
- Two rows were added to the §R1.3 table.

## Changes
- `docs/design/memfn/span_cards.md`: §R1.3 rows S2c-1 and S2c-2; §3.2 constraint, re-draw-order, unmeasured-default and placement-screen sentences; §R1.2 TWIN row; §2.3 floor quote; §2.4 text; §2.5 key and row lists; §3.3 job-shape rows (marked as rev 1.2's shape, since S2c's plan is the record); §3.5 tables and drill rows; §9 S2c sabotage (j) and the S2d row; formhash entry list.
- `docs/dev/history/claude_md/docs__dev__lanes.md`: this report's index line.
- `docs/dev/lanes/s2c_deliver.txt`: committed as-is, by name.

## Checklist
- [x] Merge d9afba62b alone, result read (already up to date).
- [x] limits_check.sh green (39/0).
- [x] S2c-1 text, every phase-rule sentence updated (grep "3 of 4" leaves only the historical quote).
- [x] S2c-2 text, every walk-set key/card listing updated; remaining mentions are history, noted as such.
- [x] S2c-3 in §9 S2d.
- [x] spec_history --staged and check_claudemd_size.sh --all (run before commit).
- [ ] The §3.3 J2/J3 gate counts (21, 30) are not recomputed; they are rev 1.2's shape, flagged in the table.
