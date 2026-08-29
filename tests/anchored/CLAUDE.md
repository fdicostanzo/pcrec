# tests/anchored — [ENG-ABS]'s anchored match-here form, as ANSWERS

The pcrec-vs-pcrec differential for `docs/design/anchored_match_unwrapped.md`:
the same pattern compiled with the unwrapped anchored machine and with
`-fno-anchored-dfa`, linked into ONE translation unit under two prefixes and
compared on every anchored entry, every capture slot and every position.

## Why the directory exists at all

**MEASURED before it was written (2026-08-29, lane engabs): nothing else in
this tree asks what `<prefix>_match` ANSWERS.**

- `tests/harness/driver.c` drives `<prefix>_search` for every `m`/`n` cell.
  It touches the anchored entries only as an `_in`-vs-un-suffixed cross-check
  ([DD-14.FB]), and both sides of that are the same code path.
- `make test-axes` compares the corpus's SEARCH answers under each deny flag,
  so `-fno-anchored-dfa` rides that sweep without asking about `_match`.
- `tests/codegen/run_anchored_match.sh` reads the ARTIFACT — which form was
  selected, which tables are present, what the entry bodies are shaped like —
  and says nothing about what they compute.

So before this directory, an anchored form that reported the WRONG LENGTH left
every check in the tree green. Sabotage **S189** is that made real and
measured: `prune=false` on the third machine makes `a|ab` at `ctx->pos` 0 over
`"ab"` return 2 where it must return 1, and on the planted tree
`tests/base/alternation.rxt` — the file that CONTAINS that pattern and that
cell — is 26 passed / 0 failed, `run_anchored_match.sh` is 14 passed / 0
failed, and this script is the only thing that is red.

## The ground truth is the DENIED build, and that is not circular

Under `-fno-anchored-dfa` the entry is the pre-row code, which derives its
answer from `<prefix>_search` — the entry every `.rxt` cell, both oracles and
every differential in this tree already verify. A disagreement is therefore a
bug by construction, with no question about which side is right and no
external oracle needed. It is the same argument `tests/possessify/`'s
differential makes for its own denied build, one row over.

## Files

- **`anchdiff_driver.c`** — the two-artifact driver. Both builds are linked
  into one TU under the prefixes `on`/`off` (`tests/possessify/
  possdiff_driver.c`'s shape: one gcc link per pattern rather than two
  programs and a diff of their stdout). Per (pattern, subject, position) it
  compares `_match`, `_match_caps` and its every capture pair, both `_in`
  spellings, the two spellings against each other WITHIN each build, and
  `<prefix>_search` — the last being the arm that says a divergence is about
  the anchored ENTRY rather than about the compiler having moved under both.
  Capture slots are seeded with a **known sentinel, not zero**: `caps_out` is
  UNTOUCHED on every negative return (spec §3.3), and a zero fill would make
  an untouched slot indistinguishable from a written `[0,0)`.

  **EVERY POSITION FROM 0 TO n+1**, and the two ends are the cells the design's
  argument turns on: `pos == n` is where the END view is selected and where a
  zero-length match is reported, and `pos > n` is the range guard, whose two
  forms return different values from different functions.

- **`run_anchored_diff.sh`** — the sweep. Population is every `pattern` line in
  every `.rxt` under `tests/` that compiles under `--no-captures --features
  all` AND selects the form; patterns that do not select it are COUNTED and
  skipped, because comparing a build against itself is this project's
  most-recorded check-design failure. The selected population is FLOORED (1150;
  1213 measured 2026-08-29) for the reason `run_anchored_match.sh` §5 pins its
  census: a compiler that stopped selecting the form would make every
  comparison trivially equal and this file would report a large green number
  while measuring nothing.

  The SUBJECT GRID is written in the script rather than harvested from the
  corpus's own `m`/`n` lines, and that is deliberate: a corpus subject is
  chosen to make ITS pattern match, which biases the grid toward the matching
  case, and half of this row's claim is about the FAILING probe.

## Where it runs

`make test-anchored-match`, part of `make test`, in a `run_group` beside
`tests/codegen/run_anchored_match.sh` — the two halves of the row, the shape
`tests/possessify/` established (a corpus, a differential, structural checks;
none substitutes for another). It is in `tests/lib/san_scripts.txt`, since it
compiles and runs generated C.

Maintenance: update this file when files are added/removed or change roles.
