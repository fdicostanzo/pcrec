# hdrrest — [HDR-1] purpose headers for src/, cli/, lib/ (excl. emit_vm.c/emit_dfa.c)

Branch `lane/hdrrest` from `c007e9d2` (main). Frank's charter, verbatim:
"it would be helpful if the functions had a header comment that indicated
their purpose."

## Population before/after (new `header` census column)

276 functions across 43 files were `banner` or `none` at the branch point
(counted by the new column, cross-validated against the manager's
pre-population census — identical 504/75/338-of-917 totals and identical
per-file counts everywhere that census listed one). After this lane: **0**
in this slice. By file (before → after, all → 0):

| file | before | file | before |
|---|---|---|---|
| src/parse/rxt_source.c | 28 | src/parse/mod_recursion.c | 5 |
| src/core/sb.c | 23 | src/opt/lower_enc.c | 5 |
| src/parse/parse.c | 17 | src/core/cpset.c | 5 |
| src/opt/callgraph.c | 17 | src/core/internal.h | 5 |
| src/dump/syntax_dump.c | 13 | src/core/tune.c | 5 |
| src/parse/rxt_schema.c | 12 | src/opt/prefix_k.c | 4 |
| src/opt/possessify.c | 11 | src/parse/ext.c | 4 |
| cli/main.c | 10 | src/parse/mod_modifiers.c | 3 |
| src/core/compile.c | 9 | src/opt/scanedge.c | 3 |
| src/parse/rxt_compose.c | 9 | src/parse/mod_verbs.c | 3 |
| src/ir/nfa.c | 9 | src/parse/enabled.c | 3 |
| src/ir/dfa.c | 9 | src/opt/select_engine.c | 2 |
| src/opt/atomic.c | 9 | src/parse/mod_uprops.c | 2 |
| src/opt/revdet.c | 7 | src/parse/mod_lookaround.c | 2 |
| src/enc/enc.c | 7 | src/opt/altcls.c | 2 |
| src/parse/registry.c | 7 | src/parse/mod_atomic_groups.c | 2 |
| src/dump/axes_dump.c | 6 | src/parse/definitions.c | 2 |
| src/parse/mod_backrefs.c | 6 | src/core/arena.c | 2 |
| | | src/opt/postresolve.c | 2 |
| | | src/opt/mrl.c, schema_dump.c, mod_assertions.c, fold.c, limits_dump.c, compile_defs.c | 1 each |

**Total: 276 → 0.** Confirmed by `awk` over a full census regeneration
(`python3 tools/review/function_census.py`): zero `banner`/`none` rows
outside `src/gen/emit_vm.c`/`src/gen/emit_dfa.c` (hdrgen's slice).

**Correction to my own commit log**: the `src/core` commit message says
"35 functions" — the real count, matching the table above, is **51**
(2+9+1+5+1+5+5+23). A typing slip in the message text, not in the diff;
the file-by-file counts above are the ones to trust.

## UNCLEAR list

Empty. Every function's purpose was recoverable from its body, its
immediately surrounding comments, or (for a handful of thin wrappers and
enum-to-string tables) its one obvious caller — none needed an
`HDR-1 UNCLEAR` marker.

## Anchors touched

None deliberately; all insertions are new lines strictly ABOVE a
function's signature, never touching an existing line. Verified rather
than assumed: `python3 scripts/m6read_check_sab_anchors.py` on the
finished tree reports `sabotages checked: 269 (285 anchor sites) / all
anchors resolve`, matching the branch-point figure (285/285) exactly —
the anchor mechanism resolves by text match, not raw line number, so no
row needed re-aiming.

## Validation

- **`make -j4 CC=gcc-16 && make strict CC=gcc-16`: CLEAN.** Verbatim
  tail: `strict: whole tree compiles clean with -Werror -Wshadow`,
  `BUILD+STRICT EXIT=0` (log: `/tmp/hdrrest_build.log` in this worktree's
  session scratchpad path, not committed).
- Per-file `gcc-16 -fsyntax-only -Ilib -Isrc -std=gnu11` on every touched
  `.c`/`.h` file, run after each batch, all clean (no output) before that
  batch's commit.
- `python3 scripts/emit_sweep.py --ref c007e9d2` (five streams,
  byte-identical, 0 movers expected — comment-only change, not an `abi`
  event), `make test-codegen` (expect the standing darwin `nm` probe as
  the only red) and `make test-registry`: **OWED.** A darwin battery
  (`build/battery_gate_11ff5f51/`, main tree, shape `test -j4 PROCS=3 |
  axes PROCS=10 | san -P4 | mech PROCS=6`) was running for this lane's
  entire working period, so per BOILERPLATE's one-heavy-suite-at-a-time
  rule these were not run inline. Launched as this lane's LAST act,
  backgrounded, polling `build/battery_gate_11ff5f51/trailer.log` for
  `== BATTERY DONE` before starting: log path
  `/tmp/hdrrest_acceptance.log` (this worktree's session scratchpad),
  completion line `== ACCEPTANCE GATE COMPLETE <date> ==`. A fresh agent
  or the manager should read that log rather than re-run the gate.

## Deliverable

Commits on `lane/hdrrest` (not merged), in order: `a90ad72c` (src/core,
51 functions), `e95131ed` (src/parse, 106), `d48a3de8` (src/opt, 63),
`672f2942` (src/ir, 18), `a1dacf4b` (src/enc, 7), `70a720a0` (src/dump,
21), `7e42b86a` (cli/main.c, 10), `025d03fc` (function_census.py's
`header` column, `tools/review/CLAUDE.md`, `docs/dev/coding_guide.md`
§4.2's one-sentence extension, the regenerated
`tools/review/out/function_census.tsv`). This report is the ninth and
last commit. Head: see `git -C worktrees/hdrrest rev-parse HEAD`.
