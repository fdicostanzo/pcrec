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

Maintenance: update this file when files are added/removed or their roles change.
