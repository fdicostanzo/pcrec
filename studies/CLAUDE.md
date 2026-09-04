# studies/ — adopted exploratory work

Self-contained studies adopted into the repo as REFERENCE MATERIAL: measured
explorations whose findings inform pcrec design rows, but which are not
product code. Nothing here is built by the top-level `make`, run by
`make test`, or linked into pcrec; each study carries its own Makefile and
harness. Findings graduate into pcrec by the normal route — a design note or
plan row citing the study — never by importing study code directly.

Numbers in a study are evidence from the machine and date recorded in the
study's own document (D35 spirit): cite them with their hardware context,
re-measure before load-bearing use.

## Studies

- `simd1/` — precompiled AVX2/SSE fixed-pattern SIMD matchers (Frank +
  a separate Claude session, adopted 2026-08-16). Harness + 43 validated
  candidates + measured studies behind a generator design. See its
  CLAUDE.md and `precompiled-simd-matchers.md`.
- `tt4_batching/` — [TT-4.1] measurement study for batched test compilation:
  a gcc/cc/pcrec invocation-census shim (`census/`) over one full `make
  test`, and a batching prototype (`proto/`) measuring three compile-shapes
  at several batch sizes on the two worst sections the census names. Backs
  docs/dev/tt4_measurement.md. See its own CLAUDE.md.
- `alt_dispatch/` — [ENG-ISL.S0] the alternation-dispatch study (chartered
  by Frank 2026-09-03): five dispatch algorithms for a wide literal
  alternation — today's serial try (`vm_alt`), first-byte grouping, a
  ported `src/ir/nfa.c:192` M2.8 trie walk with priority-tagged accepts, a
  `[OPT-ALTHASH]` k-byte block hash, and (ruling R1, added mid-study) the
  VM-native trie walk (commit/defer, frames pushed) — compared for
  exactness (answer-identity against the serial oracle at every subject
  position, zero mismatches everywhere) and cost, on pcrec-bench's
  `bench/altwide/` patterns and subjects. Backs
  docs/design/alt_dispatch_study.md. See its own CLAUDE.md. **Algorithm (e)
  SHIPPED 2026-09-03 as [ENG-ISL] STEP 1, with two deviations: no runtime
  deferred mask (the walk is single-path, so the live set is a compile-time
  function of the node reached), and a predicate over the alternation's
  LANGUAGE rather than per branch — the per-branch form measured wrong,
  because altcls factors the tree before the emitter sees it (the
  eleven-islands defect).**
- `ccd2_entry_shape_ladder/` — [CC-DIFF] STEP 2's ns/call LADDER: the harness
  and the RAW DATA behind `docs/dev/lanes/ccd2_report.md` §12 and
  `src/core/limits.def`'s `VM_INLINE_CHAIN_MAX_BYTES` comment. Twenty
  artifacts x four entry-shape rungs, quiet box, `load1 < 0.5` gated before
  EVERY cell and refusing rather than warning, answers checksummed every round.
  It is adopted rather than left in a scratchpad for the reason the same lane
  had to rewrite its own answer-identity sweep from scratch: the write phase
  ran that one ad hoc and it died with its scratchpad, so the branch carried a
  claim and not a check. See its own CLAUDE.md for the two things that must not
  be simplified away (every cell is `--engine=vm`, or the rungs reach nothing;
  the subject is dense, or `ns/call` is not a reading of a per-call cost).

Maintenance: update this file when studies are added/removed.
