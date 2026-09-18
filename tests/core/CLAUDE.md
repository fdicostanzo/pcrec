# tests/core — unit checks on an internal helper that belongs to no single feature

[REVW.U L5-R0.3] (`docs/dev/reviews/lens_reports/lens5_unit_seams.md` R0.3):
this directory is the home for a NEW check on a `src/core/`-style helper
whose subject spans more than one feature directory, or belongs to no
feature at all. It is NOT a generic `tests/unit/` — every existing
unit-shaped check in this tree stays co-located with the suite that owns
its subject (`tests/codegen/cpset_model_check.c`,
`tests/parse/branch_count_check.c`, `tests/mrl/cwmax_check.c`,
`tests/backrefs/fold_agreement*_check.c`, `tests/utf8/
startbnd_backend_check.c`, `tests/registry/*.c`) — moving them here would
be a second home for something that already has one, for zero gain.

## What this directory is for

A helper qualifies for a check here when its SUBJECT does not belong to any
one existing test directory. The first instance
(`sat_arith_check.c`) checks three functions living in three different
directories (`src/opt/mrl.c`, `src/gen/emit_vm.c`, `src/opt/callgraph.c`) —
no single existing test directory owns all three. `sb.c`/`arena.c`
(`src/core/`) and the growable-array/text-kit primitives wave 1 builds
(R3/R4 of the same lens 5 report) are the intended future population.

## The build

Every check here builds through `tests/lib/unit_cc.sh`'s `unit_build`
function — the ONE way an internal-property check is compiled (`-Ilib
-Isrc`, `$SANFLAGS` threaded, `$LIBPCREC` linked, `-Werror` unconditionally).
See that file's own header for the policy argument.

## The cost budget (R0.4)

A shape, not a stopwatch: **one gcc invocation and one process spawn per
SUBJECT.** No check in this tier may invoke `pcrec` or `gcc` per case (that
is a differential driver and belongs in the suite that owns the feature,
under D45's gen-timeout budgets), and no check in this tier may read the
`.rxt` corpus. `sat_arith_check.c` is one binary holding several sub-checks,
`cwmax_check.c`'s own established pattern.

## Files

- **sat_arith_check.c** / **run_core_tests.sh** — [REVW.U L5-R2] THE
  SATURATING-ARITHMETIC AGREEMENT: `mrl_sat_add`/`mrl_sat_mul`
  (`src/opt/mrl.c`), `vm_fadd`/`vm_fmul` (`src/gen/emit_vm.c`) and
  `cg_sat_add`/`cg_sat_mul` (`src/opt/callgraph.c`) must agree — the tree
  states the requirement twice in prose (`src/opt/CLAUDE.md`'s `mrl.c`
  entry, `emit_vm.c`'s own comment above `vm_fadd`) and, until this check,
  enforced it nowhere. Checked for CROSS-FAMILY EQUALITY over the
  non-negative domain every real caller uses (which also answers lens 1's
  own open question — `cg_sat_add`'s extra `CG_EXP_INF` guard is redundant
  on that domain, proved by evaluation rather than by reading) and for
  three algebraic laws the callers rely on and the implementations do not
  themselves state: MONOTONE, CAPPED, ABSORBING. See the check's own
  header for the domain argument (why no pair literally pairs `LLONG_MAX`
  with itself — that is genuine signed-overflow UB in the subject
  functions, and this file is wired into `san_scripts.txt`, so a real hit
  there would ABORT the sanitizer battery rather than FAIL cleanly) and
  the four-sabotage failing-direction story, of which one — a one-character
  boundary weakening in `mrl_sat_mul` — is invisible to every answer-level
  check in the tree by construction (it under-estimates, which is
  `pcrec_minw`'s safe direction). Sabotage row S254.

  **The six functions are not `static` any more** (`src/opt/mrl.c`,
  `src/gen/emit_vm.c`, `src/opt/callgraph.c`, declared in
  `core/internal.h` beside `pcrec_minw`) — a linker cannot reach a
  file-private symbol from a separate translation unit, and this check
  calls the shipped functions directly rather than transcribing their
  bodies (a transcription checks only itself). No behaviour change: this
  is pcrec's own compile-time arithmetic, never emitted into generated
  text, so it is not an `abi` event.

  Written against TODAY's three separate implementations. Lens 1's X3
  (wave 2 of the code review) unifies them into `pcrec_sat_add`/
  `pcrec_sat_mul` taking the ceiling as a parameter; this check must keep
  passing unchanged against the unified pair — that is what proves the
  unification changed nothing, and the six declarations in `internal.h`
  retire with it, not before.

- **alloc_inject.h** / **alloc_check.c** / **run_alloc_tests.sh** —
  [REVW.U L5-R1] THE ALLOCATION-FAILURE INJECTOR (`make alloc`, opt-in,
  NOT part of `make test`). `alloc_inject.h` is `-include`d ahead of
  every source file in a SEPARATE build tree (`ALLOC_DIR := build-alloc`
  in the Makefile — the `make ubsan`/`make asan` shape one axis over;
  nothing under `src/`/`cli/`/`lib/` is edited, `build/` is never
  touched), redirecting every `malloc`/`calloc`/`realloc`/`strdup` call
  to a `pcrec_inject_*` function `alloc_check.c` defines, so the check
  can force the Nth allocation in a real `pcrec_compile()` call to
  return NULL and assert the library never `abort()`s, segfaults, or
  silently succeeds — only diagnoses. One `fork()` per trial (the
  outcomes under audit include SIGABRT, which cannot run in-process
  without taking the whole sweep with it), K (allocations per witness)
  measured by a "never fail" profiling pass rather than guessed, over
  three fixed witnesses (R0.4's tier budget: no per-case `pcrec`/`gcc`
  call, so this is a deliberate, named exception rather than a
  corpus sweep).

  **CONFIRMS F1 (fix-now #1, `23eb3d34`) IN BOTH DIRECTIONS.** Built at
  `23eb3d34`'s parent (F1 unrepaired) and pointed at the `--engine=vm`
  witness `[a-z]{2,10}`: `1 of 11 forced allocations KILLED THE PROCESS
  BY SIGNAL ... signal 6` (SIGABRT — `sb_grow`'s unattached-buffer
  `abort()`, `scr_test`/`scr_desc`'s own reaching sequence). On the
  current (fixed) tree the same witness: `every one of 11 forced
  allocation failures was diagnosed ... never abort/signal/success`. See
  `docs/dev/lanes/waveu_report.md` for the full transcript.

  **AND IT FOUND K60 (docs/dev/known_issues.md, filed not fixed) ON ITS
  FIRST REAL RUN** — its own two other witnesses (a plain DFA compile,
  and `\p{L}` under `-e utf8`, which needs `[K53-SELRETRY]`'s drop rung
  to compile at all) show `pcrec_compile` SUCCEEDING despite a forced
  allocation failure, at a real, non-trivial rate (21% / 8% of the
  allocations swept): a stale per-attempt eligibility flag
  (`cx.size_cap_refused`/`cx.dfa_overflowed`, never reset between
  retries) and the size-term ladder's own documented "ANY reason means
  this K is out" catch-all both absorb a genuine OOM as "try a different
  internal attempt" rather than propagating it — invisible to every
  existing check because the final artifact is a correct compile with
  `rc == 0`, and invisible to `tests/resource/`'s `ulimit -v` approach
  because an address-space limit cannot be steered to a non-final
  attempt specifically.

Maintenance: update this file when files are added/removed or their roles change.
