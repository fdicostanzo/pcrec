# revtools — code-review metric artifacts (2026-09-17)

Lane `revtools`, sonnet, writer, branch `lane/revtools`. Process step 2
of `docs/dev/reviews/code_review_criteria_draft.md`: builds the
repo-owned metric artifacts the eleven review lenses cite per
admissibility rule A5. PARKED on the branch, not merged, per BOILERPLATE
("never merge to main yourself").

## What was built

`tools/review/` — five python3-stdlib-only scripts plus a shared
`reviewlib.py`, plus their committed TSV outputs under `tools/review/out/`,
plus `tools/CLAUDE.md` + `tools/review/CLAUDE.md` (new top-level
directory; the root `CLAUDE.md`'s "Where things are" list gained the
one-line pointer per convention). No installs — only python3 stdlib,
`git`, and `gcc-16` (already on the box) were used. Every script:

- takes no build/compile step to run (pure text/git processing);
- is deterministic (same commit → byte-identical output);
- writes its own commit+date+row-count evidence header, so a truncated
  output file is detectable by comparing the stated count to a re-count
  of the body;
- documents, in its own module docstring, the hand-validation actually
  performed (never merely asserted) — see "Validation evidence" below
  for the highlights, and each script's own file for the full transcript.

## Why not ctags

This box's `/usr/bin/ctags` is BSD ctags (`ctags --version` errors with
"illegal option --", no `-f` pipe to a parseable format, no end-line, no
nesting-depth output) — unusable for a census that needs spans and
depth, not just start lines. Per the charter's own fallback clause,
`function_census.py` and `clone_candidates.py` share a hand-written
brace/state parser (`reviewlib.iter_top_level_headers`) instead, hand-
validated on ten functions (below) including the exact traps this
codebase's style presents: a `;`-terminated prototype immediately before
the real definition (`vm_rolef`), a single-line function body
(`vm_label`, `cls_set`/`cls_has`), a two-line-wrapped signature
(`vm_cursor_fits`), and — the big one — every brace/paren/quote the
emitters (`emit_vm.c`/`emit_dfa.c`) print AS TEXT inside their own
generated-code string literals, which the shared lexical masker
(`reviewlib.mask_text`) blanks before any brace is counted.

## The five scripts

1. **`function_census.py`** → `out/function_census.tsv` — every function
   in the PRIMARY tier (src/, cli/, lib/), LENGTH-RANKED descending by
   CODE lines (blank/comment-only lines excluded from the length count,
   span kept as a separate column). Per ADDENDUM 2, this is the WHOLE
   population in priority order, not an over-N filter.
2. **`clone_candidates.py`** → `out/clone_candidates.tsv` — token-shingle
   winnowing (the MOSS algorithm's core) over the SAME function
   boundaries (shared join keys with the census, per ADDENDUM 1), at
   function granularity, identifiers/literals normalized so it finds
   STRUCTURAL duplication independent of naming.
3. **`literal_census.py`** → `out/literal_census.tsv` +
   `out/literal_value_freq.tsv` — every numeric/string/char literal with
   file:line and context, plus a frequency rollup for the "this exact
   spelling repeats N times, never through limits.def" citation shape.
4. **`include_graph.py`** → `out/include_edges.tsv` +
   `out/include_layer_matrix.tsv` + `out/include_backedges.tsv` — the
   #include graph and a layer-order violation list (lib→core→parse→ir→
   opt→gen→cli nominal order).
5. **`churn_hotspots.py`** → `out/churn_hotspots.tsv` — git-log-derived
   churn (touch count, lines added/removed) × current file size.

See `tools/review/CLAUDE.md` for the full per-script description
including what each one's validation caught.

## Headline numbers (commit `998af066`, 2026-09-17)

- **Function census**: **860** functions across 49 of 54 primary-tier
  files (5 files — `lib/pcrec.h`, `src/core/limits.h`,
  `src/gen/enc/enc_byte.c`, `src/gen/enc/enc_utf8.c`,
  `src/parse/parse_mods.h` — are pure declarations or emitted-text
  templates with zero real function bodies, confirmed by hand).
  - Over 200 code-lines: **8**. Over 100: **30**. Over 50: **76**.
  - **Top 10 longest by code-lines** (file, function, code_lines/span):
    1. `src/gen/emit_vm.c` `pcrec_emit_vm` — 778 / 3037
    2. `src/parse/rxt_source.c` `pcrec_rxt_source_parse` — 548 / 975
    3. `src/core/compile.c` `compile_driver` — 402 / 1234
    4. `cli/main.c` `main` — 331 / 514
    5. `src/gen/emit_vm.c` `vm_render_listing` — 288 / 501
    6. `cli/main.c` `cli_parse` — 247 / 431
    7. `src/gen/emit_vm.c` `vm_emit` — 211 / 515
    8. `src/gen/emit_dfa.c` `emit_attempt` — 201 / 509
    9. `src/gen/emit_vm.c` `vm_revdet_rep` — 184 / 323
    10. `src/parse/axes_dump.c` `emit_predicate_axes` — 178 / 294
  - `pcrec_emit_vm`'s 3037-line SPAN but only 778 CODE lines is itself a
    finding: ~74% of its span is blank/comment, consistent with lens 4's
    own seed observation about long change-history preambles in this
    file. `code_lines` vs `span_lines` diverging this hard is exactly why
    the census reports both rather than only one.
- **Clone candidates**: **70** candidate groups, **258** member rows
  (out of 664 functions considered — functions under 6 code-lines are
  excluded from clone detection as too short to be meaningful). The two
  largest groups were hand-verified real (not scan noise): a family of
  AST-predicate tree-walk functions in `src/opt/atomic.c`
  (`pcrec_has_atomic`, `pcrec_has_call`, `pcrec_has_lookaround`,
  `pcrec_has_bref`, `pcrec_has_linked_call`, ... — one recursive
  switch-over-node-kind skeleton, differing only in which node kind is
  the "hit"), and a family of enum-to-string `*_name`/`kind_name`
  functions spread across `src/parse/rxt_schema.c`,
  `src/parse/syntax_dump.c`, `src/parse/rxt_source.c`,
  `src/parse/definitions.c`.
- **Literal census**: **12,617** literal occurrences (5,212 numeric,
  7,405 string/char). The frequency rollup's sharpest hand-verified row:
  `"missing closing ) for group"` repeats verbatim across **7 files**
  (`src/parse/ext.c` twice, `mod_atomic_groups.c`, `mod_lookaround.c`,
  `mod_modifiers.c`, `mod_named_groups.c`, `mod_recursion.c`,
  `parse.c`) — BUT `parse.c:1902`'s own comment says this exact
  repetition is what keeps the phrase single-homed at the base grammar's
  doorway, which is a live A1 ("ruled-record") question for lens 3 to
  resolve, not something this census can adjudicate.
- **Include graph**: **197** `#include` statements, **0** unresolved
  local includes (a first draft had 7: gcc's quoted-include search
  checks the INCLUDING file's own directory before `-Ilib -Isrc`, which
  the resolver initially did not model — `src/core/tune.c`'s bare
  `#include "internal.h"`, `src/parse/definitions.c`/`mod_uprops.c`'s
  bare `#include "parse_mods.h"`, and four generated-table `.inc`
  headers included same-directory by their owning `.c` file, e.g.
  `src/core/fold.c`'s `#include "fold_tables.inc"`, all resolve
  correctly once same-directory search is added; fixed before commit),
  **6** back-edges, ALL ONE PATTERN: `src/core/compile.c`, `src/ir/dfa.c`,
  `src/ir/nfa.c`, `src/opt/lower_enc.c`, `src/parse/parse.c`, and
  `src/parse/rxt_compose.c` each reach into `src/gen/enc/enc.h` — a
  single, tight, citable finding for lens 6 to weigh against the
  DD-12/D58 encoding-seam design (admissibility rule A1: that design
  explicitly makes `enc.h` the seam's whole interface, so this may be
  ruled-deliberate rather than a fresh violation).
- **Churn hotspots**: top 5 by `hotspot_score` (touch_count ×
  current_lines): `src/gen/emit_vm.c` (140 touches, 11,575 lines,
  score 1,620,500), `src/core/internal.h` (171 touches, 5,522 lines,
  944,262), `src/gen/emit_dfa.c` (124 touches, 7,579 lines, 939,796),
  `src/parse/rxt_source.c` (30 touches, 4,037 lines, 121,110),
  `src/core/compile.c` (60 touches, 1,892 lines, 113,520).

## Validation evidence (see each script's own docstring for the full transcript)

- **function_census.py**: ten functions hand-checked by reading `sed -n`
  output against the reported boundaries — `arena_alloc`/`arena_free`
  (whole small file), `vm_rolef` (prototype-then-definition pair,
  confirms the `;`-discard path), `vm_label`/`cls_set`/`cls_has`
  (single-line bodies), `vm_cursor_fits` (two-line-wrapped signature,
  confirms start_line points at the SIGNATURE start, not the `{` line),
  `vm_emit` (515 lines, inside the charter's own cited 300-527 range),
  `pcrec_emit_vm` (3037 lines, confirmed genuinely running to EOF — not
  a brace-tracking bug — by grepping for any signature after it and
  reading the file's literal last lines), `usage()` (depth 1, one huge
  `fputs` call, no nested blocks), and `frame_constraints` (the single
  depth-8 function in the whole census, nesting hand-counted brace by
  brace against the source to confirm 8, not a parser artifact).
  `lib/pcrec.h` (pure declarations) correctly reports zero functions.
- **clone_candidates.py**: the two largest groups read against source
  side-by-side (see headline numbers above).
- **literal_census.py**: ten rows read against source (five numeric
  including `arena.c`'s `ABLOCK_MIN` `64 * 1024` line, five string
  including the `"missing closing ) for group"` repeat). The validation
  pass itself caught a real bug — the suffix capture group was appended
  to the match text a second time, turning `1u` into `1uu` in the
  frequency table (visible as a `1uu`/count-69 row with no plausible C
  reading) — fixed before commit (`m.group(0)` alone, not
  `m.group(0) + m.group(2)`).
- **include_graph.py**: the SHARPEST validation catch of the whole lane.
  The first draft's back-edge comparison was INVERTED — it flagged
  `parse`/`opt`/`gen`/`ir` including `src/core/internal.h` as violations,
  which is backwards: `core` is the shared foundation (`Ast` itself is
  defined there, confirmed by reading `internal.h:415-416`, and `core`
  itself includes nothing from `parse`/`ir`/`opt`/`gen`), so later
  stages depending on it is the FORWARD, expected direction. Caught by
  reading the (nonsensical, 58-row) first output before committing
  anything, fixed by flipping the comparison, and re-run to the tight
  6-row result reported above. This is exactly the kind of check-design
  trap `docs/dev/learnings.md` §3 warns about — a plausible-looking
  metric that silently measured the wrong direction — caught here by
  reading the output against known ground truth (where `Ast` is defined)
  rather than trusting the number.
- **churn_hotspots.py**: touch counts for the largest (`emit_vm.c`, 140)
  and smallest (`arena.c`, 2) primary-tier files matched
  `git log --follow --oneline -- <path> | wc -l` exactly. Recorded
  near-miss: a first manual check WITHOUT `--follow` gave a different
  number for `emit_vm.c` (142) — looked like a script bug until the
  manual command used the identical `--follow` flag.

## Owed / not investigated further

- **make strict**: not run this lane (no C files touched; the sanity
  build below used the plain `make -j4 CC=gcc-16` BOILERPLATE names as a
  structural check, not a gate).
- **include_graph.py's link experiment**: the charter's lens-6 ask also
  names a live link experiment ("can a matcher-only consumer link
  `libpcrec.a` without `rxt_source`/`rxt_compose`/`rxt_schema` objects
  today"). Deliberately NOT built here — it is an actual link/build
  probe for lens 6 to run, not a static census this tool can produce;
  noted in `include_graph.py`'s own module docstring so it isn't
  mistaken for an oversight.

## Sanity build

`make -j4 CC=gcc-16` in the worktree: clean build, `build/pcrec`
produced, no warnings beyond the tree's existing baseline. This lane
touches no build files, so this is a structural sanity check per
BOILERPLATE, not a validation gate for the metric scripts themselves
(which need no build to run). `build/` removed after the check (gitignored).

## Handback

Branch `lane/revtools`. Validation stated above is COMPLETE for all five
scripts — nothing is OWED except the deliberately-out-of-scope link
experiment noted above. Not merged; the manager reviews and merges per
BOILERPLATE.
