# S217 — the regression net for the 2026-09-01 has_push miscompile

Lane `s217` (sonnet, worktree `worktrees/s217`, branch `lane/s217`). Small,
surgical lane: one mech sabotage row. Coded entirely under the box hold
(`worktrees/s217.lift` did not exist at any point during this lane's work) —
every claim below marked HAND-TRACED is text-level (greps, `python3
str.count`, `bash -n`, `bash -c '. file'`), never a build or a run.

## What the row edits, and why that form

The defect (journal 2026-09-01, parts 2-3; `src/gen/emit_vm.c`) had TWO
components, not one:

1. **`has_push`** (the fail label's gate for whether the pop-and-resume
   dispatch is emitted at all) read the pre-pass ESTIMATE `v.npush > 0`.
2. **The counter rung's unbounded (`rmax < 0`) arm** had no special case, so
   it fell through a ternary computing `nopt = rmax - rmin` — negative for an
   unbounded repeat — and SUBTRACTED that from `v->npush`.

Neither alone reproduces the miscompile: with only (1) reverted, `v->npush`
is still computed correctly (today's fix to (2) is still in place) and stays
positive on any push-bearing program, so `has_push` still reads true
everywhere it should. With only (2) reverted, `v->npush` goes negative but
`has_push` (today) reads `v.emitted_push`, the emitted-text flag, which is
blind to the pre-pass's own arithmetic. **Only the combination is the tree
that actually shipped** between `c657ae9` ([CC-CLANG] step 1) and `adc0f5a`
(the fix), and S217 restores exactly that combination as one row with
`SAB_FILE2`/`SAB_BEFORE2`/`SAB_AFTER2` (S141's precedent for two independent
sites in the same file, same row).

**The brief asked which of two forms to pick — the tight two-site revert
above, or the blunter `v->emitted_push = true;` deletion in `vm_push_at`
(which omits the dispatch from every pushing program in the tree,
unconditionally).** Went with the tight form. The blunter edit is a strictly
bigger population — it would fail nearly every backtracking-bearing corpus
file simultaneously — and a row that big proves "the field is read", not
"the specific unbounded-counter accounting bug that shipped is gone". The
tight form is falsifiable against the exact historical shape (it is, byte
for byte, the two hunks `adc0f5a`'s own commit message and header comments
name as cause), which is the check-design rule in
`docs/dev/learnings.md` SS3 and memory `pcrec-check-design-lessons`: edit the
SPECIFIC mechanism, not a stand-in with a bigger blast radius. It is also the
row that would have caught the bug during the exact window it was live in
main, for the reason it was live — the accounting error, not merely "some
gate reads the wrong flag".

## Anchors

Both sites verified to occur exactly once in `src/gen/emit_vm.c` at HEAD
(`ae3e6ca`), via a direct `str.count` over the file text (not the
`m6read_check_sab_anchors.py` tripwire itself, which is gated behind the same
hold as everything else that touches `build/`):

- site 1 (`has_push = v.emitted_push || v.has_linked_calls;`) — count 1
- site 2 (the counter arm's `rmax < 0 ? 1 : cuts ? ...` ternary) — count 1

The row was also sourced directly (`bash -c 'set -a; . S217_*.sh; ...'`) to
confirm it parses with no stray command substitution — the [M6.5.2] backtick
trap the sabotages/CLAUDE.md warns about. The first draft's `SAB_DOC_FIGURE`
did carry three backticks (referencing the emitted field/comment names); they
are removed rather than escaped, since a double-quoted field is exactly where
the trap lives.

## Predicted vs measured detectors

**Predicted: `atomicdiff` (tests/atomic_groups/run_atomic_diff.sh) is the
ONLY suite that can see this**, and `SAB_SUITES="atomicdiff"` is set
accordingly (the vocabulary already carries the word — no registration
needed).

Reasoning, hand-traced:

- The witness pattern is not invented for this row. `(?:ab|b){8,}+c` is
  already `run_atomic_diff.sh`'s own `PATSPEC` entry (`cut:(?:ab|b){8,}+c`,
  line 181) — the exact pattern the journal's fix note names as the one that
  caught the real bug the day it shipped.
- Grepped the whole `tests/` tree for any OTHER unbounded (`{N,}+`-shaped)
  counter-rung witness over an alternation body: none exists. Every other
  counter-rung fixture in the corpus (e.g. `tests/atomic_groups/
  possessive.rxt`'s `(?:aa|a){8,12}+ab`) is BOUNDED (`rmax >= 0`), so `nopt`
  stays non-negative there and this row's edit changes nothing on it. That
  means the whole `.rxt` corpus, `harness`, and every other differential are
  predicted GREEN — the defect's population is exactly as narrow as its one
  witness in `run_atomic_diff.sh`'s own PATSPEC array.
- All three of that script's build arms (DEFAULT hybrid, `--engine=vm`,
  `-fno-possessify`) are predicted to see it identically: `vm_cuts(a,
  under_atomic) == a->u.rep.possessive || under_atomic` (`src/gen/
  emit_vm.c:1351-1354`), and `(?:ab|b){8,}+c`'s `+` suffix sets
  `a->u.rep.possessive` directly — `-fno-possessify` denies the LIFT
  mechanism for an atomic group's cut, not a directly-written possessive
  quantifier's own flag, so it does not clear this. The sabotaged arithmetic
  runs identically on all three builds.

Exact fail/pass counts and the `SAB_DOC_FIGURE` prediction (`atomicdiff:
Nfail/?pass`, `corpus:0fail`) are marked OWED at the manager's battery run —
S216's own precedent for a row written entirely under a box hold.

## Landing bar

- `tests/mech/sabotages/S217_has_push_npush_estimate_reverts.sh` — the row,
  committed.
- No `SAB_SUITES` vocabulary registration needed (`atomicdiff` pre-exists).
- No CLAUDE.md updates: `tests/mech/CLAUDE.md` carries no hand-maintained row
  census (its own founding argument is against one) and
  `tests/mech/sabotages/CLAUDE.md` is conventions/traps, not a manifest —
  neither names a place this row's addition needs to touch.
- Validation OWED, exact commands for the manager once the hold lifts:
  1. `python3 scripts/m6read_check_sab_anchors.py` (or `bash tests/codegen/
     run_codegen_tests.sh`'s `[SABANCHOR]` section, whichever is the wired
     path this session) — expect the new row's two anchors among those
     resolved, population count +1.
  2. `bash tests/mech/run_sabotage_matrix.sh S217` — expect `DETECTED`,
     `atomicdiff:Nfail/?pass` (N>0) with `corpus:0fail` (if `harness`/other
     suites are ever added to this row later, they are predicted green too),
     zero anomalies, zero unexpected verdicts.
