# lane ccdiff — [CC-DIFF] work log

Chartered 2026-09-02 by Frank (plan.md `[CC-DIFF]`): find what clang does
that gcc does not on the emitted C, name it as a transformation, and test
whether a C-LEVEL spelling gets gcc there. One lane-day, no asm, no
intrinsics, no per-arch work. Deliverable: `docs/dev/ccdiff_step0.md`.

## Setup

* Worktree `worktrees/ccdiff`, branch `lane/ccdiff`, off main `22a6775`.
* `build/pcrec` built here; artifacts emitted with the bench's own argv:
  `pcrec -p rx --features all [--engine=vm] -o artifact.c -- '<pattern>'`,
  and for the `match-compliance` regime the whole-subject text
  `(?:<pattern>)\z` (pcrecbench `record.whole_subject_text`).
* Compiled exactly as the bench does, through its own `testees/pcrec/shim.c`:
  `$CC -O2 -std=gnu11 -fPIC -shared`. No `-march`. gcc 15.2.0 (Ubuntu
  15.2.0-16ubuntu1), clang 21.1.8 (Ubuntu 6ubuntu1).
* Timing harness `mb.c` (scratch): reproduces `testees/pcrec/driver.c`'s three
  regime loops verbatim and calls through `dlsym`, as the bench does, so no
  cross-TU inlining is available to either toolchain.

## Cells

### 1. `cls-upto-4` (`[a-z]{0,4}`) / large-subject-throughput / `auto` — clang 0.407

Direction reproduced on the harness (t-letters-016k, find-all): clang ~0.3 of
gcc. `rx_search` is 142 instructions under gcc, **76 under clang**.

NAMED: **uniform-table constant folding.** Every one of this artifact's six
DFA tables is uniform — `rx_forward_next_state[4]` is all `65535` (dead),
`rx_forward_is_accepting[4]` all `1`, and the reverse and anchored pairs the
same — because [OPT-5]'s scan edge absorbed every real transition. LLVM folds
a load from an all-equal constant object regardless of the index
(`ConstantFoldLoadFromUniformValue`); gcc 15 does not fold a variable-index
load even from an all-equal `static const` array. So clang proves the DFA
step unconditionally dead, deletes the outer `for(;;)`, all three table base
`lea`s, and with the register pressure gone the whole frame: **clang's
`rx_search` has no `push` at all, gcc's has three** (`rbx`, `rbp`, `r12`).

SECOND, smaller: clang **fully unrolls the bounded scan-edge run loop** (trip
bound 4) into four straight-line class tests and eliminates the
`scan_run_length` counter; gcc keeps it rolled with a `cmp $0x4` per byte.

Twins built: **A** (fold uniform tables in the emitted `_step`/`_accepts`
helper bodies — arguments still evaluated, so every side effect is kept),
**C** (fold the run bound into a cursor limit computed once: one induction
variable, no unroll threshold, correct for any bound), and **A+C**.

Static result: A takes gcc 142 -> 77 instructions and drops the frame to
zero pushes, i.e. to clang's shape. C alone removes the counter but gcc
still declines to unroll: 138 instructions, frame still 3 pushes. A+C is 80.
**A is the effect; C is a rounding error on top of it.**

Timing deferred: box load 5.0-5.8 all afternoon (lane opt5i's `make test`),
and repeat batches disagreed by 60% on the same binary. Numbers are taken in
one batch at low load and recorded in step0 with the load line.
