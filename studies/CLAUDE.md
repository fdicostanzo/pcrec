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

- `specnum/` -- [SPEC-CLEAN] numbering (lane specnum, 2026-10-09): the one-time passes that gave `match_api.md` its permanent section and paragraph numbers and re-pointed the tree's `match_api.md#anchor` citations to `§N¶K`, plus the old-anchor to number map. See its CLAUDE.md.
- `specclean/` -- [SPEC-CLEAN] (lane specclean, 2026-10-09): the claims ledger and citation logs behind match_api.md's facts-only rewrite (2,187 claims, 0 unmapped). See its CLAUDE.md.

- `u3_island_twin/` -- [UCP] U3's D77 trigger (lane u3twin, 2026-09-30): the island form of ucp_design.md s3 hand-built as C twins, proven answer-identical to today's artifacts and libpcre2 10.46, timed island vs all-byte/VM. See its CLAUDE.md.

- `simd1/` — precompiled AVX2/SSE fixed-pattern SIMD matchers (Frank +
  a separate Claude session, adopted 2026-08-16). Harness + 43 validated
  candidates + measured studies behind a generator design. See its
  CLAUDE.md and `precompiled-simd-matchers.md`.
- `hyb_reseed_cal/` — [OPT-HYB-RESEED]'s calibration and timing harness
  (lane reseedfix, 2026-09-30, committed after the r1 panel found the
  calibration unreproducible): subject generator, find-all driver, the
  abi-46 hand-twin transformer, the crossover sweep and the base/new/deny
  table with its noise floor. Backs docs/design/hyb_reseed.md §3 and
  docs/dev/reseed/timing_mac.md / clamped.md. See its own CLAUDE.md.
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
  **FIXED 2026-09-21 (lane edgefix, triaging O-42's ubuntubudu run at
  eaab0d4a)**: two harness defects D112's comments-off default and a stale
  relative-path assumption had introduced since. (1) `run_ladder.sh`'s
  `ARM[before]`/`ARM[after]` were built from a RELATIVE `$OUT` before the
  script's own `cd` into `$OUT/work`, so both reference arms read "COMPILE
  FAILED" on every rung while `step11` (already hardened absolute) ran fine
  — fixed by absolute-izing `$OUT` the same way, in both run scripts. (2)
  the edge-count census reads the `[OPT-5] SCAN EDGE` COMMENT marker, which
  D112 (2026-09-19, abi 26->27) made non-default — the floor's own census
  reads an artifact built by the compiler UNDER TEST (no old-reference
  stand-in), so `floorcells`/`run_floor.sh` now pass `-fcomments` on that
  one build (proven byte/behaviour-neutral, D108); the ladder's census reads
  the OLD `after` reference compiler's artifact, which predates D112 and
  needed no change. A rung/cell that measures nothing now FAILS the run
  (rc<>0) rather than exiting 0, and `run_floor.sh` gained the median/IQR
  summary block the 2026-09-04 report cited (previously computed by hand).
  See `docs/dev/lanes/edgefix_report.md` and the study's own README.
  **`runs/<date>-<item>-<pin>/`** archives each executor pass (own
  `fit.py`/`fit_output.txt` beside the raw ladder/floor logs);
  `runs/2026-09-21-i82-89d986c3/` is I-82's run behind D117
  ([OPT-EDGE] CLOSED), analysis `docs/dev/lanes/edgefit_report.md`.
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

- `lim2_m2/` -- [LIM-2]/dfamin M2, the dominance-prize measurement (lane
  `dfam12`, 2026-09-16): candidate B's Tier-1 dominated-position pruning,
  sized using the study's own named "deliberately illegitimate stand-in"
  (`docs/dev/dfa_online_minimization_study.md` §3.7 -- "drop a position
  when an earlier copy of the same unrolled repeat is present in the
  list"), implemented as a REAL, measurement-only edit to this worktree's
  `src/` (`[PROBE-M2]`, gated on `getenv("PCREC_PROBE_M2")`, committed
  SEPARATELY for the manager to drop at merge -- this directory's harness
  will not link once that commit is dropped, by design; see its own
  CLAUDE.md). Real but NARROW over the shipped corpus (14.3% of 1,232 rows
  see any drop, 4.0% see raw-state relief, aggregate K7 charge relief a
  modest 4.6%), rich and MIXED on `tests/counterk/counterk.rxt` (raw state
  count roughly halves on some rows, K7 charge alone drops up to ~2,000x on
  others with the raw count UNCHANGED), ZERO on K25's own chain shapes
  (`a{0,N}`/`(?:abcdefghij){N}` -- structurally no two copies' positions
  ever coexist in one subset), and -- the sharpest finding -- a
  REGRESSION on the study's own chartering witness: the K18 census pattern
  (`tests/base/k18_cost_gates.rxt:66`) goes from a clean 27,575-state
  compile to a hard refusal (`>32,000 states`) under the stand-in, exactly
  the open-loop-context brittleness the study's §4.3 (B2) predicted, now
  measured rather than argued. Backs `docs/dev/dfamin_m1m2.md`. See its own
  CLAUDE.md (`make CC=gcc-16`, `bash run_m2.sh` re-runs both passes).
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

- `n1budget/` — [LIM-2] N1's default-sizing measurement (lane n1budget,
  2026-09-04): what does the CURRENT corpus + pcrec-bench altwide set spend
  in K7's own unit (`Ctx.subset_elems`) under default (auto) options, over
  every pattern that does NOT already refuse? `n1_measure.c` drives the
  same D7-fast-path pipeline `lim2_census.c` and `lim2_m1.c` already
  established as sound methodology (parse -> altcls -> discharge_atomic ->
  callgraph_build -> select_engine -> postresolve -> the DFA-scan gate ->
  build_nfa -> build the mandatory forward+reverse machines AND, for a
  DFA-chosen artifact, the [ENG-ABS] optional third machine too, mirrored
  inline rather than calling the static `build_anchored_dfa` — so the
  reported MAX is the real total spend a corpus artifact pays today, not an
  under-count of it), reading `cx.subset_elems` off the finished `Ctx`
  rather than computing anything of its own. MEASURED over 3,386 pattern
  blocks (193 `.rxt` files + 33 pcrec-bench altwide patterns): the worst
  currently-compiling (non-refused) spend is 24,050,003 elements
  (`tests/counterk/counterk.rxt:1845`, one of three near-identical
  8,002-raw-state exact-repeat witnesses), against `PCREC_MAX_SUBSET_ELEMS`
  = 48,000,000 — the derivation behind `PCREC_MAX_AUTO_DFA_ELEMS`'s
  30,000,000 default. Backs `docs/dev/lanes/n1budget_report.md`. See its
  own CLAUDE.md/README.md (`make CC=gcc-16` builds it against
  `../../build/libpcrec.a`, `make sweep` re-runs the population).

- `tt4m_batchrun/` — [TT-4M] STEP 1's darwin re-open of the batched-build
  question (lane tt4m, 2026-09-08): does linking N pcrec-generated
  matchers into ONE gcc invocation (distinct prefixes, a generated
  dispatch `main()`, each member its own translation unit by construction)
  beat the harness's one-gcc-call-per-pattern shape on THIS Mac, where the
  profile is process-dispatch spawn tax ([TT-14]/[XARCH] half 1), not gcc
  CPU the way [TT-4.1]'s Linux census found. Reuses `collect_patterns.py`/
  `extract_cases.py` from `tt4_batching/proto/` unchanged; writes a new
  `dispatch_gen.py` against the CURRENT `tests/harness/driver.c` protocol
  (the old one predates DD-14.FB's route argument and the current typed
  give-up codes). Backs `docs/dev/tt4m_darwin_validation.md`. See its own
  CLAUDE.md (`make check` is a smoke test, not the load-bearing sweep).

- `ucp_study/` — [UCP]'s thinking-and-testing study (lane ucpthink,
  2026-09-28; study only). libpcre2 probes run on 10.46 over ssh stdin (they
  write nothing remote) and on 10.48 locally: a per-code-point classifier in
  two independent forms, the exhaustive `\b`-vs-lookaround equivalence, point
  probes, a Latin-1 UCP probe. It also carries a pcrec driver that reproduces
  the equivalence stream from generated matchers, the corpus+bench census
  (lexical UCP features + engine stamps, default and `--no-captures`), and
  the size probes. Backs `docs/dev/ucp_study.md`. See its CLAUDE.md.
- `cls_tree_study/` — [CLS-TREE]'s STUDY (lane clstudy, 2026-09-11; study
  only, nothing under `src/`/`tests/`/`docs/spec/`): does a class matcher
  COMPOSED PER-SECTION from a small kit of representations, statically
  selected, beat today's byte-automaton — measured over the 312 generated
  `unicode-props` sets, K53's six (with complements) and the 41 distinct
  byte classes the shipped corpus actually contains. Backs
  `docs/dev/cls_tree_study.md`. Carries the kit (`ALL`/`RANGES`/`CUBES`/
  `MASK64`/`BITMAP`/`PAGE64`/`BSEARCH`), the sectioning DP in TWO
  independent implementations (`section.py` and `discover.c`, compared by
  `crosscheck.py`), an emitter, an exhaustive verifier (every matcher
  checked against an independently built reference on all 1,114,112 code
  points), the today-baseline (`build/pcrec` under `-e utf8`, sized as an
  object), two separate `.text` calibration routes, and the
  provenance-blindness property test. Headline: `\p{L}` costs 227,409
  object bytes today and 4,359 as a kit matcher; the whole byte-class table
  pool goes to ZERO `.rodata`; discovery on the worst real set is 26.4 ms
  in C, so the study's own D77 verdict is that the pre-analysis cache is
  NOT triggered. **Read its README for the three bugs its own instruments
  caught** — a cost model that prices a form without building it (the
  `PAGE64` price missed the all-empty leaf), two implementations of one
  algorithm disagreeing where neither was self-inconsistent, and a Pareto
  point dominated on BOTH axes, which is a modelling error and not a
  result. Study code, never imported into `src/`.
- `k70_probe/` — K70's oracle evidence (lane k70fix, 2026-09-28): a light
  probe against the 10.46 reference over the tailnet, extending lane
  ucpthink's `ucp_study/probe_misc.py` with two rows that lane did not
  cover — `(?r)` under BYTE across the whole Latin-1 range (not just
  ASCII letters), and the `(?aD)`/`(?aP)`/`(?aS)`/`(?aT)`/`(?aW)`
  sub-letters under `-e utf8` WITHOUT UCP. Both confirmed true no-ops;
  see `docs/dev/known_issues.md` K70.

- `pf_know/` — [PF-KNOW] (D140; lane pfknow, 2026-09-30; research only): the proven-segment probe (`segprobe.c`, real parser + altcls + atomic discharge + enc lowering, captures on), the corpus+bench static census with the DFA-partition-refines-VM-bitmap check (question 2), the gcov dynamic-share instrument and the answer-checked hand twins (`detall`, `prefix`). Backs `docs/design/pf_know.md`. See its own CLAUDE.md.
- `ctx_prefilter_joint/` — [CTX-PREFILTER] joint-position measurement (lane
  ctxjoint, 2026-09-29; measurement only): of the positions a lookaround-free
  prefilter admits, how many would the necessary one-character context
  condition actually reject, measured with libpcre2 on the bench's own
  subjects (capability + syntax throughput texts, sha-verified) and two
  prose texts, 99 patterns x 6 subjects, soundness (`T ⊆ C1 ⊆ C0`) checked in
  every cell plus four controls. Backs `docs/dev/ctx_prefilter_joint.md`. See
  its own CLAUDE.md.
- `artrev/` — [ARTREV] S0 (D150; lane artharness, 2026-10-05): the harness for
  bottom-up artifact review — generation at a pin, patch/seal with SIMD/flag
  rejection, the answer-identity driver + battery, interleaved-round timing with
  the load/lock gates and the `--remote ubuntubudu` day-only wrapper, and the
  `iterations.tsv` bounds ledger; self-test includes the failing direction.
  Charter: `docs/dev/optloop/artrev/charter.md`. See its own CLAUDE.md.
- `revend_twin/` — [OPT-REVEND]'s HAND-TWIN (lane revdes, 2026-10-09; scratch tier,
  Linux dev box): `mktwin.py` rewrites an unmodified artifact's `<p>_search` into
  the seeded reverse walk (form A: exact start + anchored entry; form B: the walk's
  `s*` as the unchanged body's `search_from`), `check.c` sweeps answer identity
  against the artifact and libpcre2 10.46 (every startpos, find-all), two
  `TWIN_SABOTAGE` controls must fail, `timedrv.c` times both on 1 MiB tails.
  Backs `docs/design/revend.md` §6-§7. See its own CLAUDE.md.
- `u8pick_twin/` — [U8-PICK] STEP 0 (lane u8pick0, 2026-10-09; measurement only,
  scratch tier, Linux dev box): the 12 bench `lit-*` utf8 cells compiled `-e byte`
  vs `-e utf8` (plus a scratch structural UTF-8 prior, the bench pin's compiler as
  a calibration arm, and memmem / AVX2-pair proxies), timed on the bench's own
  regenerated subjects, 15 interleaved pinned passes, answer identity 0 diffs.
  Backs `docs/dev/lanes/u8pick0_report.md`. See its CLAUDE.md.
- `locate_finish/` — D156's LOCATE × FINISH census (lane locfin, 2026-10-09;
  compile-side, Linux dev box): every corpus/bench artifact's locator and finisher
  today, the stage-1/stage-2/relaxed-reverse populations, D-2's population, and the
  `fit.chosen` grep behind the FINISH decision; five controls gate the tables
  (stamp vs emitted text twice, the borrowed end-pin probe vs the shipped fact both
  ways, the hybrid classifier vs `RX_VM_RESEED` — plumbing, not independent — and,
  since rev 2.1, the machine-membership rule vs the emitted text). Also the L0 edit
  set and its derived sabotage re-aims. Borrows `docs/dev/optloop/revend/`'s
  population and probe. Backs `docs/design/locate_finish.md` §2.7, §3-§5. See its own
  CLAUDE.md.

- `walk_survey/` — the GRATUITOUS-WALK SURVEY (lane walksurvey, 2026-10-09;
  survey + measurement only): a per-phase subject-load instrument (the
  artifact compiled with KASAN-style call hooks, loads attributed to phases by
  the emitted line), run over every bench cell and every corpus pattern block,
  classes K1-K12 with gratuitous-byte counts, and answer-checked hand-twins
  for the top classes. Backs `docs/dev/walk_survey.md`. See its own CLAUDE.md.

- `start_landing/` — `[START-LANDING]`'s evidence (lane landdes, 2026-10-09;
  design + hand-twin only, Linux dev box): a scratch fact-probe patch (prints
  the landing fact and the fixed byte width, selects nothing), the census over
  walk_survey's bench and corpus populations with the design's first-match
  rows applied, an emitter-independent twin transformer (`replace` and
  per-call `assert` modes, DFA bodies and hybrid prefilters alike), a
  three-answerer identity driver against libpcre2 10.46 with failing controls,
  and directional timing. Backs `docs/design/start_landing.md`. Revision 2 (lane
  landrev): three guard forms in the twin (the post-loop skip, Fix A, the refuted
  restart) calling the seam's own decode, an exhaustive decode-vs-Table-3-7
  check, the class-own ill-formed pool, the guard timing with hostile subjects,
  the regenerated census (empties, the width interval), and the DERIVED edit set,
  reader census and witness-mover tables. See its own CLAUDE.md.

Maintenance: update this file when studies are added/removed.
