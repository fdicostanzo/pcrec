# Lane k152fix — the NFA builder's compile-stack crash (K152)

Branch `lane/k152fix` from main 2b4e56eab. Tier opus. A bug fix in the
family's existing mechanism (`PCREC_OWN_FRAME`, [DD-10]). No feature, no
abi event, no flag. Box: gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0, default
flags (`-O2 -g`).

## Summary

`pcrec_compile` no longer dies on K152's witness. Before the fix the review
r64 witness `^(?i:` + `(?:abc|abd` x249 + `abe` + `)*` x249 + `)|b$` died
(rc 139) on the 442,368-byte budget thread. After it, it compiles there at
306,032 B. The plain nest `(?:abc|abd…abe)*` x250 dropped from 440,176 to
293,744 B. `litpost`, `(abc|abd…abe)*d`, dropped from 440,560 to 317,744 B
and is back in DEPTH_FAMILIES. It is now the measured worst of all families
(28% below the budget; the budget is 1.39x it). The same builder carried
`(?:a|b…c)*`, which dropped from 344,176 to 229,904 B.

There are 0 emitted-byte movers over the corpus. Sabotage S3470 is
DETECTED. limits.md §3.10 and the limits.def budget row are restated from
measurement. K152 is FIXED on this branch, not landed. The cloud make test
is dispatched and its verdict is OWED (see Validation dispatched).

PREMISE TEST (at the worktree's base, before any edit):
`$PCREC_TMPDIR/scratch/k152fix/probe.sh <worktree>` builds
tests/thread/compile_stack_driver.c against the worktree's libpcrec.a and
runs each witness. Result: `witness st=442368 rc=139`, and
`witness st=8388608 … hw=452080`.

## Cause

Measured with gdb at base. The driver ran on a 420,000-byte thread, the
plain nest overflowed, and the frames were summed from the backtrace's
stack pointers (script `scratch/k152fix/frames.py`):

| frame | count | bytes | frame size | share |
|---|---|---|---|---|
| `compile_ast` (src/ir/nfa.c) | 976 | 374,784 | 384 | 89.7% |
| `frag_star` | 244 | 31,232 | 128 | 7.5% |
| `compile_driver` | 1 | 11,072 | 11,072 | 2.7% |

The compound witness gave the same table. Each nesting level costs four
`compile_ast` frames and one `frag_star`, about 1.66 KB. A level is REP ->
`frag_star` -> CAT (the factored `ab`) -> ALT -> CAT (`d` + the next REP).
`compile_ast` is the tree's one exhaustive switch. gcc inlined every arm
into it (CAT, ALT, REP, the leaves, `trie_key` and the atomic arm's
by-value `KindRow`), so each level paid the union of their locals. The
`KindRow` slot also cost a stack-protector canary. The compound route's
second `compile_driver` frame (about 11 KB) then pushed the 440 KB nest
past the budget. `-fstack-usage` at base: `compile_ast` 384, `frag_star`
128.

## Fix

src/ir/nfa.c only. All of it is the existing mechanism (coding.md §2.4,
core/internal.h's `PCREC_OWN_FRAME` comment):

- Each recursive arm of `compile_ast` is its own `PCREC_OWN_FRAME`
  function (the mark's second use): `nfa_cat`, `nfa_alt`, `nfa_rep`, and
  the rarer recursions `nfa_eol` (a tail `$`'s body) and `nfa_splice` (a
  spliced call's callee). The leaves `nfa_class`, `nfa_ctx` and
  `nfa_wclass` also left the dispatcher, so its frame carries none of their
  locals.
- Scratch that is dead before the recursion goes in a marked callee (the
  mark's first use): `trie_key`, and the atomic arm's row read
  `nfa_erase_by_row`.
- `nfa_cat` has ONE recursion site instead of one per loop. The order of
  the calls and the joins is unchanged, so the frame holds one result slot.

The bodies were moved verbatim, and every `nst` call happens in the same
order. Frames after the fix (`-fstack-usage`): `compile_ast` 32, `nfa_cat`
176, `nfa_rep` 224, `nfa_alt` 160, `frag_star` 128. A level now costs
about 1.0 KB on this shape. No explicit stack was needed: the recursion is
bounded by the nesting, so this is not K147's memo re-entry case.

## Depth rows

tests/thread/run_compile_stack.sh gains four DEPTH_FAMILIES rows:

- `nclitrep`, the plain nest `(?:abc|abd;abe;)*`.
- `litpost`, `(abc|abd;abe;)*d`, the trailing-element shape. Lane k147tri
  had moved it under K152; it is now back among the rows expected to pass.
- `nclitpost`, `(?:abc|abd;abe;)*d`.
- `litcompound`, `^` + `(?:abc|abd;abe;)*` + `|b$`, the compound-route
  shape.

The compound reach check now loops over `compound` and `litcompound`. Both
take the compound route: their stamps read "compound".

The harness cannot express the review's exact wrapper. The `^(?i:` level
would make depth 250 into 251. `litcompound` is the same nest on the same
route at 250 levels, and it dies at base like the witness (rc 139, checked
with the base driver).

High-water marks at the tip, from `make test-stackdepth` (log
`$PCREC_TMPDIR/scratch/k152fix/stack2.log`; 74 passed, 0 failed, plus the
matcher arm's 5 passed). The budget is 442,368 B and 80% of it is
353,894 B:

| row | at depth 250 | share of budget | at base |
|---|---|---|---|
| `litpost` | 317,744 | 71.8% | 440,560 |
| `litrep` | 317,504 | 71.8% | 317,504 |
| `litcompound` | 307,056 | 69.4% | dies, 139 |
| `nclitrep` | 293,744 | 66.4% | 440,176 |
| `nclitpost` | 292,864 | 66.2% | 440,560 |
| the review's witness (probe, not a row) | 306,032 | 69.2% | dies, 139 |

Every row has at least 28% headroom. Other rows that moved: `ncaltrep`
from 344,176 to 229,904, `ncaltpost` and `optaltpost` to 230,352, `altpost`
from 344,560 to 257,792, `altpospost` to 293,792, and `optpost` from
208,504 to 186,176. Every other row is unchanged. At depth 251 the maximum
is 214,152 B (a parser refusal, unchanged).

limits.md §3.10 is restated from these measurements and from a base-vs-fix
sweep (`scratch/k152fix/measure.sh` and `measure2.sh`: depth 250 on the
budget thread plus the deepest nesting on 131,072 B). The base column
reproduced every old ¶3/¶4 figure (83, 116, 88, 115, 149, 129, 64…), which
validates the script. The changes:

- ¶1 and ¶2 name only K148 as the exception.
- ¶3 names the new worst (317,744 B) and the fallen figures: `+`/`{2}`
  refusals at most 312,560 B, the literal `+` refusal 242,224 B (was
  410,224), and the compound literal nest 307,056 B.
- ¶4 re-measures the depths at 128 KB: 88/92/78 levels for the literal
  nest (was 64), 100 for `*+`, 115 for the capturing nest, 120 for the
  non-capturing one (was 83), and 166 for optional groups (was 149).
- ¶5's CI sentence is made historical.

The limits.def `PCREC_COMPILE_STACK_BUDGET` row text (`--list-limits`)
says the same: 1.39x today, 317,744 B, one excluded defect (K148). The
r64 ruling has this text move with ¶2. `tests/registry/limits_check.sh`:
44 passed, 0 failed.

## Identity

`scripts/emit_sweep.py --ref 2b4e56eab --bin <copy of the fix build at
dfeeb645d> --jobs 8` is the K147 lanes' command (k147fix_report.md
"Identity"; the ref is built clean from `git archive`). Result: SELF-CHECK
PASSED at full reach. 0 movers and 0 asymmetric on every stream:

- c-default (6,659 reach), c-vm (6,660), emit-ir-vm (6,684), facts (6,675)
- the four emit-ir-auto arms (7,233 each) and stderr (7,233)
- composition (466 files, 38 producing, 88 artifacts) and dumps (7)

`emit_sweep: DONE rc=0`. Log: `$PCREC_TMPDIR/scratch/k152fix/sweep.log`.

nfa.o did not change after the swept build (same md5 of the archive
member at the tip). The later commits touch tests, docs and the
limits.def DESCRIPTION text. That text shows up only in `--list-limits`,
which is a dumps-stream text change by design (the r64 ruling) and not an
emitted artifact byte.

## Sabotage

S3470 (`tests/mech/sabotages/S3470_nfa_arms_inlined.sh`) undoes the fix in
two sites. Site 1 makes all 10 `static PCREC_OWN_FRAME` marks in nfa.c
always_inline. Site 2 gives `nfa_cat` back its two loops. Measured by
plant, this rebuilds base exactly: 440,176, 440,560 and 440,560 B, and the
witness dies.

`bash tests/mech/run_sabotage_matrix.sh S3470` at 63dce3213:
`compstack:1fail/73pass DETECTED`, and `mech run COMPLETE: 1 rows
(unexpected: 0, undetected: 0, unreached: 0, anomalies: 0)`. Log:
`scratch/k152fix/mech.log`. The row that goes red is `litcompound`.

One row, not one row per piece (S3471-S3479 unused). Each partial undo
was measured by plant and none dies:

| partial undo | deepest row |
|---|---|
| marks dropped, sites kept single | 408,560 |
| `nfa_rep` alone inlined | 408,560 |
| `nfa_alt` alone inlined | 376,560 |
| `nfa_cat` alone inlined | 328,560 |
| `nfa_rep` + `nfa_alt` inlined | 400,560 |
| all marks always_inline | 376,560 |

The harness reads the budget, not the headroom, so a partial undo is
invisible to it by design. That is r62's UNLOCK-1 finding again: plan row
[LINT-FRAME] (a frame-ceiling check) is the instrument that would see it.
Proposed filing, not built: an optional headroom arm in
run_compile_stack.sh (each family at most 80% of the budget, on the
measured compiler only). It needs a ruling because a box-dependent number
would become a gate.

## Validation dispatched

- Cloud make test: `scripts/cloudrun --owner main --kind test --ref
  91dccb67a --name k152fix-test` returned `cloudrun: DONE rc=0 pushed
  91dccb67a -> cloud/main/test/k152fix-test`. Proof:
  `git ls-remote origin 'refs/heads/cloud/main/*/k152fix*'` printed
  `91dccb67a8b71cb315d2539cbc1523c5bd6c7fef
  refs/heads/cloud/main/test/k152fix-test`. The verdict is OWED and
  reaches main as CLOUD-DONE through queuewatch. 91dccb67a is the code
  tip: the only later commit adds this report.
- The first dispatch attempt was refused by the pre-push hook on a PL14
  violation in main's r66 review files (not this branch's content). Main
  had fixed it (0ab38150f), and the retry pushed.
- Local runs, all targeted:
  - `make test-stackdepth`: green.
  - The S3470 mech row: DETECTED.
  - The emit_sweep: 0 movers.
  - `make test-spec-history test-plan-lint test-claudemd-size`: rc 0.
  - `tests/registry/limits_check.sh`: 44/0.
- Not run locally, left to the cloud run: the full corpus,
  `run_trie_identity.sh` (the `-DPCREC_NO_TRIE` build was compiled
  warning-free here) and the island and reverse NFA corpora.
- Local box use ended at 00:51.

## STATE AT HANDOFF

STATE: delivered. Commits: dfeeb645d (fix), the DEPTH_FAMILIES rows,
63dce3213 (S3470), 91dccb67a (records and spec), then this report. The
rulings file `k152fix_rulings.md` was empty at every re-read, so no R-n
was applied. The cloud verdict for `k152fix-test` at 91dccb67a reaches main
through queuewatch; it is not a lane obligation.

OWED: none
 Not done: nothing in scope. The proposed headroom arm
above is a filing for the manager. Scratch: `$PCREC_TMPDIR/scratch/k152fix/`
(probe, frames.py, measure*.sh and the logs named above).
