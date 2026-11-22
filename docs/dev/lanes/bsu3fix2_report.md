# bsu3fix2 report

STATE: delivered, validation owed (queued, not before 2026-11-22T07:00)

## STATE AT HANDOFF

Branch lane/bsu3fix, test-only change in tests/memfn/simd_floor_check.py and a header/desc edit in
tests/mech/sabotages/S3516_o0_rule_disabled.sh. Last rulings entry applied: R-1 (re-queue the identity job
as `kit-bsu3fix2-ids`). `bash tests/memfn/run_simd_floor.sh` (the named file the suite chains): checks passed
22771, failed 0 (log scratch/bsu3fix2/run5.log). The box was shared; only that one section ran, each run ~3 min. Owed: kit-bsu3fix2-test, kit-bsu3fix2-mech, kit-bsu3fix2-ids (see OWED RUNS).

## THE FAILURE

The only red of `make test` was `FAIL: x86-64-v3: control __w32's always_inline dropped did not compile at -O0`
(test-memfn-simdfloor). Cause: the control compiled the planted artifact as `a.c` alone in a fresh temp dir,
but every emitted artifact starts with `#include "a.h"` (its own companion header). The compile died with
`fatal error: a.h: No such file or directory`: a missing file, not an un-inlined target-attribute helper and
not an intrinsic immediate. So the control never reached the -O0 rule and proved nothing.

Second finding: with the header supplied, the old plant (`__w32` loses always_inline) compiles, but the V head
text leg and (c) also reject it (the head reads `None int`), so it was never "the -O0 rule alone" as CHECKS-1
required.

## THE FIX

1. The record of a clean V mover keeps the artifact's `.h` bytes (`rec['hdr']`); the control writes them as
   `a.h` beside `a.c` before the -O0 compile.
2. New plant V_O0_CONTROL: the level helper's `_mm_shuffle_epi8(` becomes `_mm_packus_epi16(` (same arity, same
   16 characters). Every head is untouched, byte count unchanged, so at -O0 the function calling the selector
   holds no pshufb (rule leg 2) and nothing else sees it. CHECKS-1's suggested form (the selector calling
   `__body`) was tried first and rejected: the text legs read it as "no SIMD FUNC selector" and a
   non-floor deleted line.
3. The check now also asserts the plant is invisible to `text_legs` (a new PASS line), so the control stays
   the rule's own if a text leg ever grows to see it. Docstrings and the S3516 header/desc updated.

## PROOF

- Text legs do not reject the plant: `PASS: x86-64-v3: control the level helper's pshufb replaced by a packuswb
  is invisible to the text legs` (run5.log); the old plant was rejected by `V head` and `(c)` (probe, run3.log).
- The rule alone rejects it: `PASS ... rejected by the -O0 rule alone` (run5.log, 22771/0).
- It is the rule's own control: with `o0_inline_issues` stubbed to `return []` the run goes
  `FAIL: ... NOT rejected by the -O0 rule ([])` (run6.log, 22770 passed, 1 failed); stub reverted, file restored.
- S3516 (`for fn in sorted(always_inline_sel(ton) & set(sel)):` -> `sorted(set())`) still plants: its anchor line
  is unchanged and the effect equals the stub above. S3515 plants in src/ and its header speaks of its own plant;
  both stay true. Mech detection of S3515-S3518 is owed (below).

## IDENTITY

Test-only: no file under src/, cli/, lib/ or memfn/ changed, so no emitted byte moves and the abi stays 112.
The identity sweep is queued anyway to carry the held job (R-1).

## OWED RUNS

Queued by scripts/boxqueue, all `not-before 2026-11-22T07:00`:
- `kit-bsu3fix2-test`: make test on the worktree (log scratch/bsu3fix2/maketest.log; verdict = make `*** [...test-` lines).
- `kit-bsu3fix2-mech`: S3515 S3516 S3517 S3518 plus the bsu3 set (after kit-bsu3fix2-test).
- `kit-bsu3fix2-ids`: the held kit-bsu3fix-ids sweep (idsweep.sh, logs scratch/bsu3fix/ids_*.log).
