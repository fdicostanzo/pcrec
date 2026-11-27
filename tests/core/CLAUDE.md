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

## Files

- **sat_arith_check.c** / **run_core_tests.sh** — [REVW.U L5-R2], REVISED at [PATFACTS] step 3.6 (R3, 2026-09-28, lane pf36): THE SATURATING-ARITHMETIC AGREEMENT between ...
- **sb_fragf_check.c** — [REVW.2] wave 2 stage 3: `pcrec_sb_fragf`'s own property, below any emitted artifact.
- **sb_stamp_check.c** — [REVW.2] wave 2, EP2 step 10 / lens 1 X8: `pcrec_sb_stampf`/`pcrec_sb_stampwf`/`pcrec_sb_stamp_str`, the artifact-stamp primitives, which emit ...
- **alloc_inject.h** / **alloc_check.c** / **run_alloc_tests.sh** — [w5fix] W5's witness pattern `(?:a?){N}` is MEASURED, not pinned: `w5_run` tries `w5_counts` in order ...
- `varexp_check.c` — [VAR] M1 (2026-09-23): the expansion grammar (`src/core/varexp.c`), checked below any artifact and below any match. 47 sub-checks: accept rows, refuse ...
- **flag_access_check.py** -- [FLAG-ACCESS] (lane flagacc, 2026-10-10): THE OPTION WORD'S READER CENSUS AS A GATE, run as the last section of `run_core_tests.sh` (a source ...
- **scratch_builder_check.py** -- [K155] (lane k155fix, 2026-11-24): THE COMPILE PATH'S BUILDER CENSUS AS A GATE (a source scan in `run_core_tests.sh`): no heap StrBuf, private Arena or raw heap call under the compile-path layers outside its named allowlist (reasons inline; [ARENA-SCOPES] clients by object name), plus the scope rules (L2-static, L4, D-7, readers) and D-11 (the type-keyed `mf_arena` binder rule: only `pcrec_memfn_art` binds, and to `&cx->arena`; sabotage S3614), every Job StrBuf freed by job_cleanup; self-test fixtures, floors, stale rows FAIL. Its independent control is `alloc_check.c`'s stranded-heap property (W1-W6; sabotage S3570-S3572, S3580-S3584).
- **memgate/** -- [ARENA-SCOPES] T1: the per-compile memory and cost gate (`make memgate`, opt-in, never in `make test`): peak live heap, attempt-arena block high-water, growth-ladder refusals and instruction counts, two built sides compared compile by compile. Own CLAUDE.md.
- **ksrc_deps_check.sh** -- [KNOW-SRC] K0 (lane ksrc, 2026-10-16): the knowledge module's DEPENDENCY RULE (`docs/design/measure_sets.md` rev 3 §9.2, sabotage S989).
- **ucd_wall_check.sh** / **ucd_wall_check.py** -- [DATA-PLAN] A1 (lane dpcompact, 2026-11-24; hardened by dpfix after review r97): THE UCD WALL, one module (`src/parse/ucd_tables.c`) understands the Unicode tables' format. The .sh is a wrapper; the .py derives its needle from the module and its product, scans every non-prose file (docs/ code included), has a src/lib/cli population floor and a whole-pipeline planted control, and lists in its header what a text wall cannot see. Mech S3575-S3579, S3587-S3592.
- **kindrow_check.sh** -- [INLINE-C] stage 1a (lane ic1a, 2026-10-26): `src/core/kindrow.def` is COMPLETE — the AKind/row census as text, a control, and four plants (new kind, deleted/swapped/duplicated row) that must fail to compile. Five `-fsyntax-only` runs on one subject, ksrc_deps_check.sh's shape.

## What this directory is for

A helper qualifies for a check here when its SUBJECT does not belong to any
one existing test directory. The first instance
(`sat_arith_check.c`) checks a primitive whose two remaining independent
implementations live in two different directories (`src/opt/mrl.c` — the
shared caller since [PATFACTS] step 3.6 unified mrl.c's and callgraph.c's
own copies — and `src/gen/emit_vm.c`) — no single existing test directory
owns both. `sb.c`/`arena.c` (`src/core/`) and the growable-array/text-kit
primitives wave 1 builds (R3/R4 of the same lens 5 report) are the intended
future population.

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

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__core.md`.
