# r110 arenaf4: verification (coordinator, inline; plants built from plant:S3653's seeded tree, exact-count edits)

| plant | edit (on top of S3653's two edits) | CLI `^abc\|x+$` | `--w7-only` | `--sites` (W1-W7) |
|---|---|---|---|---|
| S3653 | none | rc 1, "[K163]" internal error | lent row FAIL (profiling refused, K=-1), alloc rc=1 | not run |
| V1 | walk_part's lend and unlend deleted (`uses = 0`) | rc 0, RX_COMPOUND split | lent row INFO (0 points), alloc rc=0 | W6 FAIL: 1014 of 1059 absorbed vs pin 1016; alloc rc=1 |
| V2 | `if (uses)` -> `if (0 && uses)` | rc 0 | lent row FAIL: "2 of 2 forced allocations returned with a DFA memo arena still holding a block", alloc rc=1 | not run |
| V3 | `pcrec_arena_alloc`'s count line deleted | rc 0 | lent row FAIL (same memo message), alloc rc=1 | W6 FAIL (1014 of 1059) + lent row FAIL; alloc rc=1 |

## LIFE-1: HOLDS (by reading). pcrec_ctx_fail (src/core/compile.c:20-40) ends `longjmp(cx->jb, 1)`; a refusal through the lent outer Ctx lands at the outer setjmp (compile.c:2593) before walk_part's `pcrec_ctx_unlend`, so the count of that use is never read.
## LIFE-2: HOLDS for 4 of 5 lines. V3 shows `pcrec_arena_alloc`'s line is netted (W6 pin, lent row, and mech S3653 on a tree missing it). rec_take, sb_grow, sb_take, render_prefix: no plant routes an inner use through them (S3653 uses pcrec_sb_fragf -> pcrec_arena_alloc); deleting any one moves nothing on any shipped path (lent population 0).
## LIFE-3 / CHECK-2: HOLDS. The lent row never sweeps on SUBJECT (INFO) or on S3653 (profiling refused). V2 proves the row CAN sweep and go red when the refusal is neutered, so a V2-shaped sabotage row would make it a proven control. Its red message names the R-1 memo premise, not the K163 strand.
## CHECK-1: PARTLY. Deleting the lend while the member is back (V1) is invisible to the CLI, the compound corpus answers and the lent row, but W6's EXACT allocation pin catches it (1014 of 1059), and mech S3653 would read UNDETECTED on such a tree. The net is the pin (incidental to the member's allocation shape) plus mech, not a lent-specific check.
## CHECK-5: HOLDS (critic's --sites runs: BASE 1057, SUBJECT 1061 with 1016 absorbed).
VERIFY COMPLETE
