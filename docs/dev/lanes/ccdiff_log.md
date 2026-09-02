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

### 2. `floor` (`:`) / match-compliance / `auto` — ledger 0.432 — DOES NOT REPRODUCE

The artifact is byte-identical to the ledger's (`git log 1989c62..22a6775 -- src/`
is empty, so the emitter has not moved since the pin). Summed over all 49
subjects of `floor`'s compliance set, 20,000 iterations each, five interleaved
rounds: **clang's absolute number reproduces the ledger to 1.4 % (214.6 vs
217.6 ns), gcc's does not (median ~307 vs 503.3).** The measured ratio is
~0.79, not 0.432.

And there is no transformation to name. The two `rx_match` bodies are the same
shape and nearly the same length — gcc 53 instructions, clang 48, both a
bottom-tested rotated loop of 12 instructions per byte, both hoisting the
three table bases into the entry block. If anything gcc's entry is leaner:
gcc pushes one callee-saved register, clang pushes three.

VERDICT: a layout / i-cache artefact of the ledger's gcc build, not a codegen
difference. At ~5 ns per call over 49 short calls this is exactly the scale
alignment moves. Reported to the bench rather than chased further (stop rule).

### 3-6. The four VM cells — THE GENERAL SIGNAL, and it is one transformation

`dig-upto-16` thr/vm (0.378), `floor` thr/vm (**1.996, a control where clang
LOSES**), `nest3-16` thr/vm (1.511 control), `stack-frame` search/vm (0.680).

NAMED: **clang inlines the VM entry chain and gcc does not.** On every one of
the four, gcc's `rx_search` is a stub that builds a 152-byte frame, stores the
four run-state binding fields, pays a `-fstack-protector-strong` canary — the
arrays in `rx_run_buffers` are what trigger it, and Ubuntu's gcc has it on by
default — and then CALLs `rx_search_run` out of line. Per search attempt.
clang inlines `rx_search_run` into `rx_search` in all four cases, and on the
two FRAMELESS artifacts it inlines `rx_match_anchored` too and then proves the
whole `rx_run_state` / `rx_run_buffers` storage dead and deletes it: no frame,
no canary, no binding stores.

Measured directly: `nm` on the loglines `stack-frame` artifact shows
`rx_search_run` as a local symbol in the gcc build and **no such symbol in the
clang build**, with `rx_match_anchored` out of line in both (it holds the
computed goto, which neither compiler will inline).

Twin V: `__attribute__((always_inline))` on every emitted static helper except
the matcher, plus the matcher itself when the artifact is frameless. gcc
REFUSES the attribute on a function containing a computed goto — a hard error,
not a warning — so the gate is required; it is the SAME predicate
`src/gen/emit_vm.c` already evaluates for [CC-CLANG]'s `has_push`, so the
spelling rides a stamp pcrec already computes.

Static result, `rx_search` instruction counts (gcc / clang / twinV):

| cell | gcc | clang | twinV-gcc | canary gcc -> twinV |
|---|---|---|---|---|
| `dig-upto-16` thr/vm | 20 (a stub + call) | 55 | 88 | 2 -> 0 |
| `floor` thr/vm | 14 (stub + call) | 22 | 25 | 2 -> 0 |
| `nest3-16` thr/vm | 41 (stub + call) | 103 | 99 | 2 -> 2 |
| `stack-frame` search/vm | 40 (stub + call) | 102 | 97 | 2 -> 2 |

twinV reaches clang's shape on all four, and removes the out-of-line
`rx_search_run` symbol on all four.

## Answer identity

Every twin checked against BOTH the gcc original and the clang build over all
178 bench subjects (bounded + loglines, compliance and throughput) in all
three regimes, comparing every reported span, not just a count: **3,204
comparisons, all identical.**
