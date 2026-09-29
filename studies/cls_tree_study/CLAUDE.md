# studies/cls_tree_study/ — [CLS-TREE]'s prototype-before-commit study

Purpose: answer [CLS-TREE]'s four study questions with MEASURED output over
the real populations, before any design note or `src/` change exists. Backs
`docs/dev/cls_tree_study.md`. Read `README.md` for the reproduction recipe
and the five things not to simplify away.

Self-contained per `studies/CLAUDE.md`: pcrec's own `make` never enters here,
nothing is linked into pcrec, `make test` does not run it. It READS
`../../src/parse/uprops_tables.inc` and `../../tests/**/*.rxt` and invokes
`../../build/pcrec`; it WRITES only under this directory.

## Files

- `clsets.py` — the three study POPULATIONS. `uprops()` parses the 312
  distinct sets out of the generated `uprops_tables.inc`; `k53()` the six
  sets `known_issues.md` K53 names, each with its complement;
  `byteclasses()` reads `results/byteclasses.tsv`. `--dump-iv` writes one
  interval file per set for `discover`.
- `kit.py` — the per-section representation KIT (`ALL`, `RANGES`, `CUBES`,
  `MASK64`, `BITMAP`, `PAGE64`, `BSEARCH`), the MEASURED per-form `.text`
  constants, `cube_of` (the O(k) single-cube test that rediscovers the ASCII
  case fold from set structure alone) and `minimize_cubes` (the exact
  Quine-McCluskey minimizer, MEASURED not worth running — memo §6.1).
  Takes no provenance argument by construction.
- `section.py` — the sectioning DP. `partition()` is the Python
  implementation; `partition_c()` shells out to `discover`.
- `discover.c` — the SAME DP in C. Two jobs: the compile-time measurement
  (`--time`) that decides the memo's D77 cache verdict, and an INDEPENDENT
  implementation for `crosscheck.py` to compare against.
- `emit.py` — composes one bespoke straight-line C matcher (global bound +
  balanced binary dispatch tree + per-section leaf test) from a sectioning;
  also emits the deliberately-dumb `reference()` oracle.
- `sweep.py` — one row per (set, policy): build, EXHAUSTIVELY VERIFY against
  the reference on all 1,114,112 code points, and size the `.o`. Also holds
  `obj_sizes()`, the Mach-O/ELF section-size parser everything else reuses.
- `baseline.py` — what `build/pcrec` emits TODAY for the same sets, under
  `--features unicode-props -e utf8`, sized as an object.
- `extract_byteclasses.py` — the byte-class population, parsed off EMITTED
  artifacts over the shipped `.rxt` corpus.
- `calibrate.py` — per-form `.text` by OLS over real sweep rows.
- `calibrate_direct.py` — per-form `.text` by slope over synthetic
  single-form matchers. The two routes disagree and the memo says why.
- `crosscheck.py` — the two DP implementations compared over a population.
- `proptest.py` — the provenance-blindness composition property test.
- `bench.py` — ns/char, house protocol; gated by `loadgate.wait_for_quiet`
  (lane clsgate, 2026-09-29 — see `loadgate.py`'s header): every arm for
  every set is built BEFORE any timing starts, and the gate polls for a
  quiet box immediately before EACH timed unit (one set×regime run), for up
  to `--max-load-wait` seconds (default 600), rather than refusing on the
  first over-threshold reading. `--whole`
  (added 2026-09-28, lane clsdes88) adds the `page2w`/`page3w` arms and the
  `runs` regime (runs of 1..32 code points from one 256-cp block — a crude
  text model where dispatch branches predict); off by default, so `make bench`
  reproduces the committed 2026-09-11 arm set unchanged.
- `loadgate.py` — [CLS-TREE] S0 gate fix (lane clsgate, 2026-09-29): the ONE
  load-average gate `bench.py` and `bench_bytes.py` both use
  (`wait_for_quiet`), replacing each script's own instant-refusal check.
  Diagnoses and fixes the double-REFUSED S0 timing session
  (pcrec-bench `scratch/clstree-s0`, `0d7392c`): the old gate checked load1
  once per SET/N, but the harness's own compiles + timing runs are
  sustained single-core CPU work with no idle gaps, which drives a 1-minute
  load average toward 1.0 on its own — attempt 2's trajectory (pre-wait
  load1 0.07, nothing else running, refused at 0.52 after 10 of 12 sets)
  is that curve, not external contention. `wait_for_quiet` keeps the 0.5
  threshold but POLLS for quiet (logging every reading) for a bounded wait
  before refusing, so a self-inflicted spike gets a short wait instead of
  an aborted multi-hour run, while genuine sustained contention still
  refuses honestly once the bound is reached. See its own header for the
  full diagnosis and `docs/dev/lanes/clsgate_report.md` for the fix.
- `wholeset.py` — WHOLE-SET indexed tables, the forms `section.py`'s
  MAXK=64 cap makes unreachable: `PageW2` (idx[cp>>6] -> deduplicated 64-bit
  leaf) and `PageW3` (three stages, TS=10). Branch-free after one bound test;
  take a bare interval list only (Constraint 1). `python3 wholeset.py k53`
  is the TS stage-width sweep (`results/page3_ts_k53.tsv`). NOT in `kit.KIT` — whether
  the DP offers whole-set sections is `docs/design/cls_tree_design.md`'s
  decision, gated on `make bench2`'s timing.
- `automaton.py` — the UTF-8 byte automaton of a set three ways (today's
  flat `u8_box` alternation transcribed, the minimal forward automaton, the
  exact minimal reverse one) with the closure fan-out on entry; the design
  note's §3 numbers (`results/automaton_k53.tsv`).
- `timefit.py` — analysis only: does the DP's `model_ops` predict the
  ubuntubudu ns/char? (No: `results/timefit_20260928.txt`, design note §1.2.)
- `verify_whole.py` — exhaustive (all 1,114,112 code points) check of the two
  whole-set forms against `emit.reference`, plus their exact rodata; writes
  `results/whole_<population>.tsv`.
- `compare_whole_kit.py` — [CLS-TREE] S0 (lane clss0, 2026-09-28): turns
  `verify_whole.py`'s size columns into a VERDICT against `sweep.py`'s own
  size-minimal kit answer (`results/sweep_<population>.tsv`'s lam=0 "size"
  policy row) — does a whole-set form ever beat the kit on size? Writes
  `results/whole_vs_kit_<population>.tsv`. Confirmed 0/41 (WHOLE-WINS) on
  the byte-class population (design note §7 a1's owed byte-tier half).
- `asm_count.py` — [CLS-TREE] S0 (lane clss0): the [FORM-CHAR2] (i)
  asm-counting method (`studies/form_char_twins/asm_evidence.c`'s one
  hand-picked fold-vs-bitmap witness) extended to every kit byte form the
  emitter can build (`ALL`/`RANGES`/`CUBES`/`MASK64`) vs `BITMAP`, over the
  real 41-class byte population: `gcc -O2 -S`, real per-function
  instruction counts (not sampled), via the SAME `emit.py`/`kit.py`
  machinery `sweep.py` uses (no hand twins). Writes
  `results/asm_count_<population>.tsv` (design note §7 a5).
- `bench_bytes.py` — [CLS-TREE] S0 (lane clss0): the [OPT-CLSPACK] timing
  arm (D129 item 5) — N=4/16/32 live class sites cycled in ONE loop (random
  site + random byte per iteration, the many-live-classes shape a real
  matcher's scan loop has, unlike `bench.py`'s one-class-at-a-time arms):
  `bitmap` (today's shape, read straight off `byteclasses.tsv`'s own hex
  column), `kit` (the sectioning DP's own answer per class, emitted by
  `emit.py`/`section.py`), `atom` ([OPT-CLSPACK]'s shared byte→atom[256] +
  per-class 64-bit mask, generalized from `form_char_twins/twin_D.py`'s
  base.c-parsing method to build straight from membership sets; refuses
  loudly rather than truncating if N classes need >64 atoms). Checked
  against an INDEPENDENT bsearch reference (not the bitmap arm, even
  though its table already IS ground truth — sharing that source with the
  check is the K35 blind spot). Writes `results/<out>` (default
  `bench2_bytes.tsv`); `--smoke` cuts rounds/probes for Mac
  correctness-only runs (`results/smoke_bytes.tsv`, NOT citable timing).
  Gated the same way as `bench.py` (lane clsgate, 2026-09-29): every N's
  arms built before any timing starts, `loadgate.wait_for_quiet` polled
  immediately before each N's run.
- `Makefile` — targets named in README.md. `CC` defaults to `gcc-16`.
  `bench2` is the design note's owed ubuntubudu arm (`--whole`, five
  regimes, `results/bench2.tsv`). `bench2-bytes` rides the same executor
  session for the CLSPACK arm above. `whole-byteclasses`/`asm-byteclasses`
  are the byte-tier a1/a5 targets, reading the committed
  `results/byteclasses.tsv` (no `build/pcrec` rebuild needed).
- `results/` — committed TSVs (the measurements the memo cites).
- `build/` — gitignored scratch (generated `.c`/`.o`/binaries/interval files).

## Two invariants a future editor must not break

**The kit never learns where a set came from.** `kit.py` takes an interval
list and nothing else — no caseless flag, no `\p` tag, no provenance
argument. That is CONSTITUTIONAL CONSTRAINT 1 (Frank, 2026-09-11), it is why
`cube_of` finds the case fold without a fold table, and it is what makes
`proptest.py`'s composition identity a law rather than a coincidence. A
"hint" parameter added for speed would silently retire the property test.

**Nothing here may become the compiler.** The prototypes are study code:
they exist to be measured and thrown away. The route into `src/` is a design
note citing these numbers, then an implementation written against that note —
never an import from this directory.
