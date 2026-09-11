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
- `bench.py` — ns/char, house protocol; REFUSES on a loaded box.
- `Makefile` — targets named in README.md. `CC` defaults to `gcc-16`.
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
