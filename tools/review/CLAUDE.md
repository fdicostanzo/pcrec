# tools/review/ -- code-review metric artifacts

Built by lane `revtools` (2026-09-17) per `docs/dev/reviews/
code_review_criteria_draft.md`'s "Metric artifacts" section: repo-owned,
python3-STDLIB-ONLY scripts the eleven review lenses cite per admissibility
rule A5 ("findings cite the metric artifacts where one applies"). Delivery
report: `docs/dev/lanes/revtools_report.md`.

## Standing rules

- Python3 stdlib only: no system installs, no third-party packages; must run
  on every dev box (Mac, ubuntubudu, Linux dev box).
- Nothing here is built or run by `make`/`make test`: one-shot analysis
  scripts, re-run by hand when the tree changes enough to merit a fresh census
  (e.g. whenever a wave moves files). A regeneration is a data refresh, not a
  finding; cite the TSV header's own commit when quoting a row.
- Every script is deterministic (same commit in, byte-identical TSV out) and
  writes its evidence file under `out/` with a header line naming the commit,
  generation date and row count (line 1 header comment, line 2 column header);
  detect truncation by comparing the stated count with `tail -n +3 FILE.tsv |
  wc -l`. The TSV headers' `rows N` is the number to trust if this file's
  prose and the data drift.
- Scope: the five tree-walking scripts cover the charter's PRIMARY tier only
  (`src/`, `cli/`, `lib/` `.c`/`.h`, via `reviewlib.iter_source_files()`); the
  SECONDARY tier (`tests/lib/`, `tests/harness/`) and EXCLUDED paths (emitted
  C, `.rxt` corpora, `studies/`, `docs/`) are out of scope.
- A tool finds CANDIDATES: per A2 a lens-1 finding built on a clone row still
  needs the shared abstraction NAMED; a census fact may already be
  A1-ruled-deliberate, so a lens checks the ruling first.
- `include_backedges.tsv` reading 0 rows is a statement about INCLUDES, not a
  clean bill of health (a cross-layer CALL needs no cross-layer include when
  `core/internal.h` declares the callee; a call-level census found 30
  back-edges, lens 6 §2.2). `driver` is a per-FILE tier override in the
  script's `FILE_LAYER` table (`src/core/compile.c`, ruling M4), placed below
  `dump` on a measurement; read that table for the exceptions.
- Validation habit: hand-validate a new or changed script against `git log` /
  manual counts on the largest and smallest files (compare with the identical
  flag, e.g. `--follow`); the scripts' own docstrings record the transcripts
  and the traps they defend against.
- Maintenance: update this file when a script is added/removed, its output
  files change, or a validated finding changes its interpretation.

## Files

- `reviewlib.py` -- shared primitives: file walk, git-commit/date/row-count
  evidence header, LEXICAL MASKING stages (`strip_comments`,
  `blank_string_interiors`, `blank_preprocessor_lines`, `mask_text` = all
  three; each script uses the subset its docstring names), and the brace-depth
  walk (`iter_top_level_headers`/`classify_header`) that gives
  `function_census.py` and `clone_candidates.py` identical
  (file, function, start_line, end_line) join keys.
- `function_census.py` -> `out/function_census.tsv` -- every C function: file,
  span, CODE lines (ranking key), max nesting depth, name, and `header`
  ([HDR-1]: `header` / `banner` / `none` of the comment directly above the
  signature; `docs/dev/coding_guide.md` §4.2's every-function header rule is
  measured against it, a `banner`/`none` row still owes a header). Hand-rolled
  brace/state parser, not ctags (BSD ctags lacks end-line/depth).
- `clone_candidates.py` -> `out/clone_candidates.tsv` -- token-shingle
  winnowing (MOSS core) at function granularity; identifiers normalized, so it
  finds structural duplication.
- `literal_census.py` -> `out/literal_census.tsv` + `out/literal_value_freq.tsv`
  -- every numeric/string/char literal (uses `strip_comments()` only) and the
  by-value frequency table (A5 instrument for "X appears N times, never via
  `limits.def`"; `limits.def` is never walked).
- `include_graph.py` -> `out/include_edges.tsv`, `out/include_layer_matrix.tsv`,
  `out/include_backedges.tsv` -- lens 6's include-layer order: `lib` -> `core`
  (base) -> `enc` -> `parse` -> `ir` -> `opt` -> `gen` -> `driver` -> `dump` ->
  `cli`; a back-edge is a LOCAL include from a lower layer into a strictly
  higher one. Does not run the charter's "live link experiment".
- `churn_hotspots.py` -> `out/churn_hotspots.tsv` -- per-file `git log
  --follow --numstat` churn joined with current size; `hotspot_score` =
  touch_count * current_lines (raw components reported alongside).
- `fragment_census.py` (lane `w2census`, 2026-09-18; `docs/dev/w2census.md`) --
  takes explicit file paths (chartered against `src/gen/emit_vm.c` and
  `src/gen/emit_dfa.c`): classifies fixed `char <ident>[...]` scratch buffers
  as (a) integer literal, (b) bare `PCREC_MAX_EMIT_NAME_LEN` (K38 family), (c)
  anything else. Usage: `python3 tools/review/fragment_census.py FILE [FILE...]
  [--out PATH]`.
- `out/` -- the evidence TSVs (regenerated 2026-09-19 by lane `w4` after
  [REVW.3] wave 3's file moves; row counts live in each header).

## Pointers

`docs/dev/reviews/code_review_criteria_draft.md` (rules A1, A2, A5, charter
scope tiers), `docs/dev/lanes/revtools_report.md`,
`docs/dev/lanes/w4_report.md`, `docs/dev/w2census.md`,
`docs/dev/coding_guide.md` §4.2, `tools/CLAUDE.md`, `src/CLAUDE.md` (layer
order).

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/tools__review.md
