# docs/dev/artifact_size_census/ — the [ART-SIZE] STEP 1 census script

Not a test suite, not built or run by `make`/`make test`. One committed
file, `census.py`: a standalone reproduction of the population, compile,
and byte-attribution methodology behind `docs/dev/artifact_size_census.md`
(the report), so the next lane (STEP 2's own re-measurement, or a future
re-census after the emitter changes) does not have to re-derive it.

## Files

- `census.py` — compiles every distinct `pattern <regex>` line under
  `tests/**/*.rxt` plus every pcrec-bench pattern file (`bench/email/`,
  `bench/loglines/`, read-only) with `build/pcrec -p rx --features all`
  (default auto engine), then `gcc -O2 -c`, recording source bytes, `.o`
  bytes, `size(1)`'s text/data/bss, gcc wall/CPU (D45's own plain-axis
  budget numbers, reused: 10 s CPU soft / 60 s wall backstop — raise both
  via the module-level `GCC_CPU_BUDGET`/`GCC_WALL_BACKSTOP` constants for a
  population expected to contain deliberately large artifacts, the way
  `tension.py` — an uncommitted scratch sibling this lane wrote, see the
  census report's own §1 — monkey-patched them for the six outlier/witness
  patterns it rebuilt under tuning flags), the D46 selection-fact stamps,
  and a byte ATTRIBUTION of the source into five buckets (prose / tables /
  program / scaffold / main) derived from the artifact's own comment
  syntax, `static const ... = { ... };` table-literal shape, and
  [M6-READ]'s function-naming convention — validated to sum to the file's
  own byte count on every artifact (`attr_sum_ok`, a bug check, not a
  hope). See `attribute_source()`'s own docstring for the exact rule and
  the two attribution bugs this lane found and fixed while developing it
  (an off-by-one in the newline-byte accounting; a multi-line
  function-pointer typedef that a naive regex mismatched as a
  body-bearing function definition, which then folded every NESTED
  comment and table inside the "function" into the PROGRAM bucket instead
  of recursing the same dispatch into it — caught only by cross-checking
  the fuzz-gate witness's attribution against an independent
  `gcc -fpreprocessed -dD -E -P` comment-strip measurement, §6 of the
  report).

  Usage:
  ```
  python3 docs/dev/artifact_size_census/census.py \
      --root /path/to/pcrec --bench-root /path/to/pcrec-bench \
      --out /some/scratch/dir [--limit N] [--only-bench] [--start-at N]
  ```
  Writes `patterns.tsv` (id, source tag, pattern text — `\t`-escaped, since
  a `.rxt` pattern line may legitimately contain a literal tab), `census.tsv`
  (one row per pattern; column list is `ROW_FIELDS` at the top of the file)
  and `progress.log` (append-only, one line per pattern processed, for
  polling an async run per `docs/dev/learnings.md` §6 — never `pgrep`/`ps`).
  Also writes each successfully-compiled artifact's self-contained `.c`
  under `<out>/cc/<id>.c` (kept; the `.o` is deleted once measured — this is
  a census, not an artifact archive) so a later pass (a re-attribution
  after a classifier fix, an outlier deep-dive) can re-read the exact
  source without recompiling.

  Async by design: run under `setsid`/background, poll `progress.log` by
  content. A full run over this corpus (2,772 patterns) took ~8 minutes of
  wall time on the box `docs/dev/artifact_size_census.md`'s §1 names.

Maintenance: update this file when files are added or `census.py`'s output
schema (`ROW_FIELDS`, the attribution bucket set) changes.
