# s22tri2 report (read-only triage of slot22, r15 @ 62261bc3 vs f18935d4)

## Item 1: test-axes red

Verdict: NOT caused by the new axis, and no evidence of an R-15 cause. The failures look like a transient environment event (strong inference; not reproduced, since I may not run the harness).

Exact failures (axes.log; the only `*** [` line is 684 `make: *** [Makefile:1869: test-axes] Error 1`, preceded by 683 `run_axes.sh: FAILED`):
- axes.log:306 `AXIS FAIL: -fno-hyb-reseed (bit 37): 0 mismatch(es) ..., 38 lost-other, 0 gained` (summary line 637: keys_axis=46303 of 46341, lost=38, 1264s).
- axes.log:337-358 `AXIS FAIL: -fno-cls-pack (bit 38)`: 29 REFUSED with an EMPTY message ("") flagged "UNDOCUMENTED refusal" (28 in counterk.rxt:247-317, plus others), plus 7 LOST (classes.rxt:182,192, island.rxt:69-82, captures/priority_and_iteration.rxt:191), 1266s.
- Every other axis is OK (about 55 rows, including `--tune`, `--engine`, `--analysis`, oracle cross-check, DIAL-S3, utfcheck, START-LANDING, START-SET).

Why it is not (a), the new axis:
- `--memfn=no-precheck-assign-byte` is not in test-axes at all. run_axes.sh:281-283 selects only the main table of `--list-axes`; the kit's `memfn` section (`--memfn=` rows) is deliberately excluded. `grep memfn=` in axes.log finds only that comment. No census, floor or witness rule was tripped, so there is no fix to make there. The earlier SIMD denies (vrun-kb, vrun-trim, vrun-pad) are not in test-axes either; they are handled in tests/memfn (simd_accept.tsv, simd_bounds.tsv) and the emit_sweep deny arms (slot22's sweep_deny and sweep_denysimd, both 0 movers).

Why it is not (b), a real answer difference:
- mismatches=0 on hyb-reseed. On cls-pack all 29 "mismatches" are empty-message refusals, not differing answers.

Why it looks transient (this is what makes it not R-15-caused):
- r15's diff against f18935d4 touches nothing under src/, lib/ or cli/. It is memfn/ kit, tests, docs and the mech/registry pins only. The cls-pack and hyb-reseed code is untouched.
- Only these two adjacent axes (bits 37, 38) failed, and each took about 1265 s against about 252 s for every other axis, roughly 5x. That indicates a load or timeout window on the box, and the harness's generated-code compile or run budget expiring gives an empty refusal message and LOST records. The affected cases (counterk `((a)|ab){0,12}c` and similar, island, classes) are heavy-compile patterns, and the same files pass under all the other axes.
- Direct check: with `taskset -c 0-3`, `pcrec -p rx --emit-main --pattern '((a)|ab){0,12}c'` (counterk.rxt:245), plain, with `-fno-cls-pack` and with `-fno-hyb-reseed`, exits 0 with empty stderr on BOTH the main build and r15's build. So there is no deterministic compile refusal.
- I found no main test-axes log to diff against (only slot22's axes.log exists; the lane reports were not checked for a clean hyb-reseed/cls-pack run). The "pre-existing on main" side of this is therefore unproven. The proof offered is the absence of any src change plus the clean single emits.

Recommended action: re-run only the two axes, e.g. `make test-axes AXES="-fno-hyb-reseed -fno-cls-pack"` in the r15 worktree on a quiet box (land5_report.md:47 used this form). If clean, slot22's axes verdict is green. If they still fail, run the same on main to settle PRE-EXISTING, because r15 cannot reach those code paths. No file edit is needed for the new deny.

## Item 2: 26 `FLOOR side` lines in the variants sweep

Verdict: PRE-EXISTING, not artifact movers. They are tag-population floor lines, not artifact differences.
- All 26 are `TAG FLOOR side a/b: <tag> N < M` (stderr-default 68<83, no-size-cap 82<84 and 290<318, refused-default, ...), arriving in a/b pairs with identical counts. They sit in the `stderr` and `emit-ir-auto*` streams of the variant populations. The same sweep prints `movers=0 asymmetric=0` for every artifact stream. Sides a and b carry equal tag counts (e.g. stderr-default=68/68), so base and tree are identical.
- The only `movers=1` is the `dumps` stream (`--list-axes`), the known expected mover, as in slot21 and slot18.
- slot21 (ref 76428e05, an r15-free tree) has the same 26 lines, and `diff <(grep 'FLOOR side' slot21/sweep_variants.log) <(grep 'FLOOR side' slot22/sweep_variants.log)` is empty (byte-identical).
- slot18 had none: its variants log has 0 `FLOOR side` lines (its tag floors "all held"). The change falls between slot18 and slot21 (variants population 5616 -> 5621, pinned floors above the observed counts), i.e. a main-side corpus or floor-pin phase shift, the same kind as the g2m4 floors already explained. Not R-15.
- Consequence: `SWEEP variants rc=1` / `VARIANTS: FAILED` is the same rc=1 slot21 had. It is a pre-existing floor re-pin owed on main, not an R-15 gate failure. The movers judge (0 artifact movers except dumps) is met.
