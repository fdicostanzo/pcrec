# Lane xcalldes — [OPT-HYB-RESEED-XCALL] design (2026-10-03)

DESIGN ONLY (opus). Branch `lane/xcalldes` from main c231ffc1. The
deliverable is `docs/design/xcall.md` plus its index entry in
`docs/design/CLAUDE.md`. The probe kit and raw numbers are in
`studies/hyb_reseed_cal/shape/`. Nothing under `src/`, `cli/`, `lib/`,
`tests/` or `docs/spec/` changed. `make test` was not run (design lane). The
only probes were small compiles and timings, all on the Mac at load 2-5.

## Summary (resume from here)

**The cross-call hint reaches none of the cost O-81 measured.** The 14 slow
cells, read against the bench driver (`testees/pcrec/driver.c`, adapter
l.4321) and against instrumented counts on the bench's own regenerated
subjects (45/45 sha-verified), fall into four groups:

- **ss**: one `_search` per short subject. 0-2 re-seeds over all 42
  subjects; lka-nonatomic never fails an attempt at all.
- **mc**: `_match_caps` on the whole-subject artifact. There is no attempt
  loop, and the executed C is byte-identical between arms.
- **qnt-poss-quest thr** and **asr-lb-fixed synth-***: zero matches, so one
  call each.
- **grp-atomic-alt thr**: 308 calls, 0 failed attempts.

logparse-atomic is anchored: its retry is unreachable dead text.

**The cost is the emitted SHAPE.** On the Mac, a variant whose re-seed never
fires is as slow as the shipped form: qnt-poss-quest thr ×1.19 against
×1.275, ss ×1.17 against ×1.205. A single-call-site, call-free step-loop
form (F1) gives these results:

- qnt-poss-quest thr ×1.086.
- asr-lb-varwidth synth-dense ×0.997 (shipped ×1.040).
- Every win is kept.
- lka-* ss reads +0.8 ns per call, from the init hoist.

A semantically identical sibling form (F2) reads ×1.742. gcc's codegen here
is fragile, so the form must be chosen on x86 gcc and clang.

**Census** (byte, 3,424 patterns): all 48 start-anchored adaptive artifacts
are `adaptive-dense`. That is 79% of that row, and it happens because an
anchored scan reads ppm 1,000,000.

**The only measured per-call cell** is the scratch `lka_dense`: 2.5
re-seeds per call, ×1.62. An emulated hint brings it to ×1.14. No bench cell
has that shape.

**Recommendation.** Round 1 builds [OPT-HYB-RESEED-FORM]:

- A1: an undeniable `anchored` row.
- A2: the call-free step loop, after an x86 bake-off.

XCALL's API is designed (B2: `_search_ex` plus an opaque
`pcrec_search_state`) and HELD under a restated D77 trigger: a bench
find-all cell with more than one re-seed per call. Eight questions for the
manager are in xcall.md §7.

## Validation

There are no tests to run for a design. The census and every timing are
reproducible from `studies/hyb_reseed_cal/shape/README.md`. Mac numbers are
directional only; xcall.md §6 specifies the Linux alpha protocol.

## Scope notes

- The bench checkout was read only. Its subjects were regenerated with
  `PYTHONDONTWRITEBYTECODE` into the scratchpad, and its `git status` was
  clean afterwards.
- The scratchpad is `worktrees/xcalldes-scratch/`, which is gitignored and
  uncommitted.
- One stray `mkdir` under /private/tmp was removed in the same minute;
  nothing was written there.
