# Lane bsu3fix: review r76's FIX-NOW items on R-47 unit U3

## STATE AT HANDOFF

STATE: delivered, validation OWED

Branch lane/bsu3fix (cut from lane/bsu3 at ec578d053, abi 112, unchanged). Code commit 37394534b; report commit follows.
Rulings file docs/dev/lanes/bsu3fix_rulings.md: last entry applied R-1 (the gap critic discharged r75 SLOT-3/SLOT-4; its one residue is the SLOT-3 pairing, done).

Done in-lane: `make -j2`, `make strict` green; `tests/memfn/run_arch_blind.sh` 32 passed / 0 failed (before the commit); decider census 68 hits, expected 68, 0 outside a member (steady, no re-pin); a by-hand probe of the new check code on a real V artifact (below); `v3` artifact of `[0-9a-f]{17}` byte-identical to the ec578d053 binary's.
NOT done in-lane: `test-memfn-simdfloor`, the plant runs and the identity sweep. The box was held by the bsu3 mech job (725, cap 9000 s) for the whole session; a lock wait of 10 minutes had not cleared, so they are queued instead (OWED RUNS). No plant has been run red yet: that is owed, not claimed.

OWED keys: kit-bsu3fix-test (726), kit-bsu3fix-mech (727), kit-bsu3fix-ids (728).

## THE JOB

Apply r76's FIX-NOW items as the manager ruling says: CHECKS-1, CHECKS-2, CHECKS-3, CONTRACT-1, r76 SLOT-1, r76 SLOT-3 (second form). No emitted byte may move against ec578d053.

## FIXES APPLIED

- CHECKS-1 (tests/memfn/simd_floor_check.py): in-script control V_O0_CONTROL, a `__w32` without always_inline on the clean V mover, compiled at -O0 and judged by `o0_inline_issues` ALONE. S3515's header and the script docstring now say S3515 proves the suite (V head leg and -O0 rule both reject it). New row S3516 empties the rule's loop; the control must then go red.
- CHECKS-2 (same file): new `o0_compile_issues`: a failed or timed-out -O0 compile is an issue for every selector, V ones included; the C9 loop calls it and skips the rest of the cell. Control: a fake failed result and a timeout are handed to it with the V mover's selectors; each must get an issue. New row S3517 restores the old silence for `_vs` selectors.
- CHECKS-3 (tests/memfn/simd_guarded_check.py): floor `named-vspan-w32` 1, counted when `named:vspan` reads the row `span-vector-w32`. New row S3518 re-points the witness at a caseless run (total `simd-form-named` stays at or above 9; only the new floor sees it).
- CONTRACT-1 (memfn/src/options.def): the span-vector help string says what U3 builds (a 32-byte block test where the SIMD layer admits that level); worded arch-free. `--list-axes` prints it.
- r76 SLOT-1 (memfn/src/window.c): `WF_VBLK_MIN` 16 and `WF_VBLK_MAX` 32 (in the existing enum: a second enum trips -Wenum-compare under strict), used in vs_w32_block's assert, its message and the B choice; two `_Static_assert`s that WF_VWIN_LO and WF_VSCAN_LO are >= WF_VBLK_MIN.
- r76 SLOT-3, second form (window.c): the `define` column comment states a define-bearing row IS the V family and names its two reads (wf_stretches' j/nv, wf_find_define); `wf_tables_check` pairs `render == wf_span_v` with `define != NULL`, both ways (R-1's wording). Decider census count steady at 68.

## GAP ITEMS

R-1 (the only entry): r75 SLOT-3 and SLOT-4 DISCHARGED by the gap critic (one vs_head, one vs_name); the residue is r76 SLOT-3's pairing, applied above. No other work.

## IDENTITY

By construction no byte moves: the changes are a comment, two compile-time constants (values equal to the old literals), a message with the same text, a table self-check and a help string. Spot check: the x86-64-v3 artifact of `[0-9a-f]{17}` is identical to the ec578d053 binary's. The full proof is OWED: job 728 runs emit_sweep of this tip against ec578d053 (binary copy in scratch/bsu3fix/ref) at c-default and c-vm, every arm (off, x86-64, x86-64-v3 byte and utf8, span-loop force and deny, v3 + no-span-vector, span_seed at width 4095 under five settings), no mask, then tests/memfn/span_vector_identity.py. Expected: movers=0 everywhere.

## OWED RUNS

- kit-bsu3fix-test (726): `make test` through perfrun, log scratch/bsu3fix/maketest.log; verdict by `scripts/verdict`. This also runs test-memfn-simdfloor, simdguarded, registry and the decider census.
- kit-bsu3fix-mech (727): S3515 S3516 S3517 S3518 and the bsu3 set (S730 S693 S1852 S3170 S3198 S699-S703 S723 S724 S728), 17 rows, after 726. Each new row must read DETECTED; a plant that does not go red is a stop.
- kit-bsu3fix-ids (728): identity as above, log scratch/bsu3fix/idsweep.out, per-arm logs ids_*.log; completion line `== IDSWEEP DONE fail=0`.
