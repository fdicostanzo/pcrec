# bsu1fix report: r72 FIX-NOW items on U1

## STATE AT HANDOFF
Branch lane/bsu1fix (cut from lane/bsu1 4a098e1e4), commits 8ff1712ce (fix items) and 20b94dff4 + one follow-up (CHECKS-1 detector). Rulings file read at start (empty). In-lane green: make, make strict, test-codegen, test-memfn-rows, test-memfn-finder, test-memfn-g2 (window family included), decider census (HITS 68, no change), anchors tripwire (1428 sites resolve), identity gate movers=0. OWED (queued as the last act): `715-kit-bsu1fix-test` (make test) and `716-kit-bsu1fix-mech` (S3278 S3279 S3281 S3282 S3500 S3501).

## THE JOB
Apply review r72's FIX-NOW items to block-span U1 with no emitted byte moved; settle CHECKS-1 (V1/V2 plants).

## FIXES APPLIED
- SLOT-3/HOUSE-1: wfS comment ("no FLD_* contract field"; opt column NULL by design), file header lists wfS, block_span.md §3/§14 say "four (six at U2)", `use_nothing`, the `{i,k,h}` subset.
- SLOT-4/HOUSE-2: dead `x->d->art &&` dropped (S3279's anchor updated to match); the unreachable branch is now a named `kit_fail` ("no span form row holds") and wf_tables_check asserts the last row holds always.
- SLOT-5: wf_tables_check refuses an E-find search row without head or skip. Written as one loop with a local row pointer so the decider census backstop stays at 68 (a first draft added a hit line and went red).
- SLOT-1: invariant comment in wf_test_to; `n/2+1` bound comment.
- CORPUS-1: gen_span_seed.py puts `!` between find-all matches of bounded patterns; span_seed.rxt regenerated (one mc line, 0 -> 2; 1145 cases unchanged). CORPUS-2: §10.1 says `g`. CORPUS-3: §14 U1 says the 4095 run is the lane's one-off, ratchet at U2. CORPUS-4: tests/memfn/CLAUDE.md heading moved below the d3floor bullet.
- HOUSE-4: headers of S3278/S3279/S3281/S3282. HOUSE-5: the three long comments reflowed (window.c).

## CHECKS-1
Plants V1 (hors_skip -1) and V2 (stop_skip -1) built in archive trees. NO existing suite detects them: the .rxt corpus aside, test-memfn-forms, -rows, -finder, -d27frame and test-codegen all stay green with V1 (only the census, red from my own first draft, differed). So one detector was added: `tests/codegen/run_skip_pins.sh` (two CLI compiles, literal spelling counts: `[0-9a-f]{17}` position 16 once, position 15 four times; `ab[0-9]{26}` no `S[C+1] == 98`), in test-codegen, mech arm `skippins`, san_excluded row. Proven: clean tree 5 pass; V1 tree red (x5 vs 1); V2 tree red (x1 vs 0). Rows S3500 (V1 direction) and S3501 (V2 direction): two rows because the two plants are distinct directions of the column (ruling said one; both ids are inside S3500-S3504). Their matrix run is OWED (716).

## IDENTITY
idgate.sh adapted from U1's: base 367cbdedb binary vs worktree build, c-default and c-vm, no mask: off/v3 byte, off/v3 utf8, force, deny, SPAN-SEED 4095 (off, v3, force, deny). Run on the final binary: all rc=0, SELF-CHECK PASSED, movers=0 asymmetric=0 in every run (corpus 7274, SPAN-SEED 41/41). Logs: scratch/bsu1fix/idg_*.log, idgate2.out.

## OWED RUNS
715-kit-bsu1fix-test (make test via perfrun, log scratch/bsu1fix/maketest.log); 716-kit-bsu1fix-mech (after 715; trailer `== mech run COMPLETE: 6 rows`). Note: an aborted first mech attempt (killed by PID, my mistake: it ran before the rows were committed) left a /tmp/pcrec-mech-sabotage.* dir because TMPDIR was unset; not removed.
