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
- `scan_edge_ladder/` — [OPT-EDGE]'s two owed measurements (lane edge2,
  2026-09-04): the 1/2/3/4 EDGE LADDER and the MINIMUM-CHAIN FLOOR STEP 1 left
  owed. Committed rather than left in a session scratchpad because a harness
  that dies with its session cannot be re-run against the next compiler.
  Carries `make refs` (both reference compilers from `git archive`:
  `9d8401a`'s per-edge `if` chain and `b048fa61`'s shared-sentinel dispatch),
  `make rungs`/`make floorcells` (regenerate AND VERIFY the artifacts), and
  the two run scripts. Read its README for why edge1's ladder design was
  wrong — subtracting the `-fno-scan-edge` arm subtracts a DIFFERENT MACHINE,
  so the entry cost read negative at every rung — and for the three REFUSALS
  the harness makes instead of caveats (`load1 >= 0.5`; a rung whose forward
  edge count is not `k`; a subject that never entered the chain).
  **THE VERIFICATION ARM EARNED ITS KEEP BEFORE ANY TIMING RAN**: the floor's
  nullable family was first written `[a-z]{0,m}9` and takes NO forward edge —
  a literal on either side of the chain gives the counting states a
  class-dependent exit and breaks the pass's precondition (1). Measured over
  eight spellings, only the bare `[a-z]{0,m}` and the exact `[0-9]{m}x` take
  one; timing the first version would have compared two identical machines and
  reported 1.000 as a finding. NOT TIMED YET — the box was held for the lane's
  whole write phase.
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
- `lim2_census/` — [LIM-2] STEP 1's corpus-wide raw-vs-minimized DFA
  transition-table census (manager ruling 1, docs/dev/lanes/
  lim2_rulings.md, 2026-09-04), kept as a permanent measuring instrument
  after the projected-size bail it was built to validate was WITHDRAWN
  (ruling 7) — the census itself is what withdrew it: a real corpus
  pattern shrinks 97.062% on minimization, and 2x that (194.1 points)
  exceeds what a percent-of-raw-bytes margin can express at all
  ([0,100)). Population 12 (1 corpus + 11 pcrec-bench altwide),
  committed as `census_data.tsv`. Feeds [LIM-2] STUDY-1's N2/N1 successor
  design (`docs/dev/dfa_online_minimization_study.md` on `main`). See its
  own README.md for the full finding and CLAUDE.md's usual shape
  (`make` builds `lim2_census` against `../../build/libpcrec.a`, `make
  census` re-runs the sweep).
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
- `lim2_m1/` — [LIM-2] M1, the [NF25] partition-rule measurement (lane
  `m1part`, 2026-09-04): does the paper's own intermediate-minimization rule
  (Hopcroft on the partial DFA, every unexplored state pinned as a
  singleton, `docs/dev/dfa_online_minimization_study.md` §6.6 item 4's
  re-scoping of M1 away from the study's original closed-subgraph-only
  reading) give a usable size-bail lower bound on pcrec's real population —
  counted repeats, a shape [NF25]'s own evaluation contains none of? NO:
  measured on 119 patterns (the lim2 census's 12 plus a broader `raw
  states > 1000` sweep plus `tests/counterk/`'s tower plus a 41-pattern
  control set), the intermediate block count EXCEEDS the true minimized
  count on 25.2% of the population before the final checkpoint, by up to
  3,001× on one witness — not even loosely bounded in the direction a bail
  needs. The comparison finding: the paper's rule sees dramatically more
  than the study's original closed-subgraph reading (a measured 33-49%
  "already merged" at the census witness's midpoint against under 0.01%
  closed) — confirming §6.6's re-ranking of candidate A quantitatively
  rather than by hand-reading one witness, and confirming N2 (the
  closed-subgraph lower bound) is vacuous on this population. The
  instrument (`lim2_m1.c`) reconstructs its own construction timeline
  POST-HOC from ONE real, unmodified `pcrec_build_dfa` call — exact rather
  than approximate, because the worklist's processing order is index order
  by inspection of `src/ir/dfa.c` and `eolvar`/`endvar` never point forward
  (checked as an invariant on every population member) — and self-checks
  against the real `pcrec_minimize_dfa` at the 100% checkpoint (zero
  mismatches over 119 patterns); its failing-direction control
  (`--sabotage-selftest`) plants two wrong-block-count bugs and demonstrates
  the self-check catches one of them on the census witness. Backs
  `docs/dev/lim2_m1_partition_measurement.md`. See its own README.md/CLAUDE.md
  (`make CC=gcc-16` builds it against `../../build/libpcrec.a`, `make sweep`
  re-runs the population).
- `form_char_twins/` — [FORM-CHAR] STEP 0 + [OPT-CLSPACK] STEP 0 hand-twins
  (lane form0, 2026-09-04): four families of mechanical hand-twins over
  emitted `build/pcrec` artifacts — the VM literal chain under
  caselessness (fold/table/atom), a single general/sparse VM class site
  (table/rangecmp), the DFA scan edge including pcrec-bench's `ci-256`
  witness plus a non-fold-pair control (range/fold), and a synthetic N=16
  many-class site testing [OPT-CLSPACK]'s ~10-class crossover (table/atom)
  — each twin's byte set parsed off the base artifact's OWN emitted text,
  correctness-checked against its base, and sized (`.text`/`.rodata`).
  Also carries a `gcc -O2 -S` compiler-equivalence check
  (`asm_evidence.c`/`results/three_spellings.s`) showing every fold-pair
  spelling compiles to the same branchless mask+compare+sete — which
  narrows the "table's one-load latency could still win" open question to
  families B and D only; family A's ranking is closed on `.text` alone.
  Backs `docs/dev/form_char_step0.md`. See its own CLAUDE.md and README.md.
  **Size only, no timing** — the study's `make check`/`sizes` targets are
  answer-identity and static-size, never a stopwatch; the timing run is
  still owed on a quiet box (the design note's §6).

Maintenance: update this file when studies are added/removed.
