# tools/review/ — code-review metric artifacts

Built by lane `revtools` (2026-09-17) per `docs/dev/reviews/
code_review_criteria_draft.md`'s "Metric artifacts" section: repo-owned,
python3-STDLIB-ONLY scripts (no system installs, no third-party
packages, runnable on both boxes — the Mac dev box and ubuntubudu) that
the eleven review lenses cite per admissibility rule A5 ("findings cite
the metric artifacts where one applies"). See
`docs/dev/lanes/revtools_report.md` for the delivery report (headline
numbers, validation evidence, findings the build itself surfaced).

Nothing here is built or run by `make`/`make test`; these are one-shot
analysis scripts, re-run by hand when the tree changes enough to be
worth a fresh census. Every script is deterministic (same commit in,
byte-identical TSV out) and writes its evidence file directly under
`out/` with a header line naming the commit, generation date, and row
count — a truncated file is detectable by comparing that stated count
against a re-count of the body (`tail -n +3 FILE.tsv | wc -l`, since
line 1 is the header comment and line 2 is the column header).

## Scope

All five scripts walk the review charter's PRIMARY tier only: `src/`,
`cli/`, `lib/` (`.c`/`.h` files, found via `reviewlib.iter_source_files()`).
The SECONDARY tier (`tests/lib/`, `tests/harness/`) and everything
EXCLUDED by the charter (emitted C, `.rxt` corpora, `studies/`, `docs/`)
are out of scope for this round; see the charter's own "Scope tiers".

## Files

- `reviewlib.py` — shared primitives every script imports: the file
  walk, the git-commit/date/row-count evidence header, and a LEXICAL
  MASKING toolkit factored into composable stages (`strip_comments`,
  `blank_string_interiors`, `blank_preprocessor_lines`, and `mask_text`
  = all three) because different scripts need different subsets — see
  its own module docstring for exactly which script wants which stage
  and why. Also carries the brace-depth walk
  (`iter_top_level_headers`/`classify_header`) that `function_census.py`
  and `clone_candidates.py` both build on, which is WHY their
  (file, function, start_line, end_line) join keys agree exactly
  (ADDENDUM 1's loop needs this).
- `function_census.py` → `out/function_census.tsv` — every C function in
  the tier: file, start/end line, span, CODE lines (blank/comment-only
  lines excluded — the ranking key, per ADDENDUM 2 the whole population
  in priority order, not a filtered list), max brace-nesting depth,
  name. Written with a hand-rolled brace/state parser rather than ctags
  (this box's `/usr/bin/ctags` is BSD ctags: no end-line, no depth, no
  JSON — unusable for a census that needs spans); ten functions hand-
  validated across the smallest and largest files in the tier (see the
  script's own module docstring for the exact transcript, including the
  two traps it specifically defends against: a `;`-terminated PROTOTYPE
  immediately before the real definition, and every brace/paren/quote
  the emitters print AS TEXT inside their own generated-code string
  literals).
- `clone_candidates.py` → `out/clone_candidates.tsv` — token-shingle
  winnowing (Schleimer/Wilkerson/Aiken, the MOSS algorithm's core) over
  the SAME function boundaries, at function granularity. Identifiers are
  normalized to a generic token, literals to STR/NUM/CHR, so it finds
  STRUCTURAL duplication (same control flow / call shape) independent of
  naming — the "separable semantic operation... repeated with variation"
  shape lens 1 is chartered to find. Its two largest groups were hand-
  validated as real: a family of AST tree-walk PREDICATE functions
  (`pcrec_has_atomic`, `pcrec_has_call`, `pcrec_has_lookaround`, ...,
  `src/opt/atomic.c`) sharing one recursive switch-over-node-kind
  skeleton that differs only in which node kind is the "hit"; and a
  family of enum-to-string `*_name`/`kind_name` functions across
  `src/parse/rxt_schema.c`, `src/parse/syntax_dump.c`, etc. This tool
  finds candidates; per admissibility rule A2 a lens-1 finding built on
  a row here still needs the shared abstraction NAMED before it is
  admissible.
- `literal_census.py` → `out/literal_census.tsv` (every numeric/string/
  char literal occurrence: file, line, kind, literal text, context) +
  `out/literal_value_freq.tsv` (the same rows grouped by exact literal
  value, count, distinct-file count — the direct A5 instrument for "the
  string/number X appears N times, never through limits.def"). Uses only
  `strip_comments()` (comments blanked, but preprocessor lines and
  string CONTENT both left intact) — deliberately lighter than the
  structural scripts' mask, because a magic number inside a `#define`
  body and a diagnostic string's own text are exactly what this census
  needs to see. The `src/core/limits.def`-exclusion the charter asks for
  needs no special-case code: `limits.def` is not a `.c`/`.h` file (never
  walked), and every module's own reference to it is a preprocessor
  `#include` whose numeric VALUES never appear as text in the
  referencing file (this script does not run a preprocessor). Confirmed
  by hand: `literal_value_freq.tsv`'s `"missing closing ) for group"` row
  (count 8, 7 files) is a REAL repeated diagnostic string across
  `src/parse/{ext,mod_atomic_groups,mod_lookaround,mod_modifiers,
  mod_named_groups,mod_recursion}.c` and `parse.c` — but `parse.c` itself
  carries a comment saying this exact repetition is what keeps the
  phrase "single-homed" at the base grammar's own doorway, i.e. this may
  already be A1-ruled-deliberate rather than a fresh finding; the census
  reports the fact, the lens must check the ruling before treating it as
  new. The validation pass also caught and fixed a real bug in the first
  draft (a suffix capture group appended twice, turning `1u` into
  `1uu` in the frequency table) — see the script's own VALIDATION section.
- `include_graph.py` → `out/include_edges.tsv` (every `#include`, local
  and system) + `out/include_layer_matrix.tsv` (a from-layer x to-layer
  count matrix over local/resolved edges) + `out/include_backedges.tsv`
  (just the violations, for direct citation) — lens 6's "is there a
  clean core→parse→ir→opt→gen order or cross-reference? VERIFIED
  deliverable, not prose." Layers: `lib` (bottom, public API) → `core` →
  `parse` → `ir` → `opt` → `gen` → `cli` (top consumer); a back-edge is a
  LOCAL include from a lower-numbered layer into a strictly
  higher-numbered one. **Caught during validation, not before**: the
  first draft had this comparison INVERTED, flagging `parse`/`opt`/`gen`
  including `core/internal.h` as back-edges — which is backwards, since
  `core` is the shared foundation (`Ast` itself is defined in
  `src/core/internal.h`, confirmed by reading it) and everything
  depending on it is the FORWARD, expected direction. Fixed before this
  file was ever committed; the shipped `include_backedges.tsv` reads 6
  rows, every one the SAME single pattern — `core`/`parse`/`ir`/`opt` all
  reaching into `src/gen/enc/enc.h` — which is a tight, specific,
  citable finding for lens 6 to weigh against DD-12/D58's own encoding-
  seam design ruling (per admissibility rule A1) rather than the diffuse
  mess a wrong comparison direction would have manufactured. Does NOT
  attempt the charter's "live link experiment" (can a matcher-only
  consumer link `libpcrec.a` without the `rxt_*` objects) — that is an
  actual link/build experiment for lens 6 itself, not a static census.
- `churn_hotspots.py` → `out/churn_hotspots.tsv` — per-file `git log
  --follow --numstat` churn (touch count, lines added/removed, total
  churn) joined against current file size; `hotspot_score` =
  touch_count * current_lines (Tornhill's classic formula), with the raw
  components reported alongside so a reader can recompute with
  `total_churn` instead if they prefer a churn-VOLUME weighting. Touch
  counts hand-validated exactly against `git log --follow --oneline` for
  the largest and smallest files in the tier — including one recorded
  near-miss: a manual check WITHOUT `--follow` gave a different count for
  `emit_vm.c` (142 vs 140), which looked like a script bug until the
  manual comparison used the identical flag.

- `fragment_census.py` — lane `w2census` (2026-09-18), chartered by
  `docs/dev/reviews/lens_reports/emitvm_second_pass.md` (EP2) §4's three
  sizing categories of fixed `char <ident>[...]` scratch buffers, per the
  `[REVW.2]` row's stated precondition ("emit_dfa.c third-category census
  FIRST"). Unlike the five scripts above, it does NOT walk the whole
  PRIMARY tier — it takes explicit file paths on the command line, since
  the census is chartered against two named files
  (`src/gen/emit_vm.c`/`src/gen/emit_dfa.c`), not a tree-wide sweep. Finds
  every `char <ident>[<expr>]` declaration statement/declarator (a
  statement can declare several; a statement can mix categories across its
  own declarators, reported explicitly rather than forced into one bucket)
  and classifies each declarator: (a) bare integer literal, (b) bare
  `PCREC_MAX_EMIT_NAME_LEN` (the K38 family), (c) anything else — a
  catch-all, not a fixed shape list, matching the repaired stage-3
  acceptance criterion's own "ANY size expression" wording. Reuses
  `reviewlib.mask_text()` (so text printed AS emitted-code inside an
  `sb_printf`/`snprintf` format string is never mistaken for a real
  declaration) and `reviewlib.iter_top_level_headers()` (function
  attribution, including correctly reading a struct-field declaration as
  having no enclosing function). See `docs/dev/w2census.md` for the full
  writeup: it reproduces EP2's `emit_vm.c` statement count exactly (58) but
  finds ONE MORE declarator (67 vs EP2's 66) — traced to a specific site
  EP2's own per-statement tally dropped — and reports `emit_dfa.c`'s
  category (c) in full (a population EP2 never measured). `python3
  tools/review/fragment_census.py FILE [FILE...] [--out PATH]`.

## Headline numbers (commit `1edd6c5e`/`998af066`, 2026-09-17)

See `docs/dev/lanes/revtools_report.md` for the full table; the raw
counts are always the TSV headers' own `rows N` field, which is the
number to trust if this file and the data ever drift.

Maintenance: update this file when a script is added/removed, its output
files change, or a validated finding changes its interpretation.
