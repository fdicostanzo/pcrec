# tests/codegen — structural assertions on generated code

Asserts that behavior-preserving optimizations are actually PRESENT in the
emitted C. These are not correctness tests (the .rxt corpus owns correctness);
they exist because checkpoint review R2 (finding R2-PR3) showed that three M2
optimizations — self-loop skip states, the anchored fast path, and DFA
minimization — could each be COMPLETELY disabled with zero signal from
`make test` or `make bench`. Behavior-preserving work needs structural tests
or it has no regression net at all.

## Files

- **run_trie_identity.sh** — DIFFERENTIAL codegen check for the M2.8
  alternation trie (R3.3). Builds a reference compiler from the same sources
  with `-DPCREC_NO_TRIE` (which forces `elig[j] = false` in nfa.c's A_ALT path)
  and diffs the emitted C over 500 generated alternation patterns. The trie is
  required to be OUTPUT-PRESERVING — subset construction plus minimization must
  erase it — so any difference is a rule-1/rule-2 soundness bug. No subjects, no
  gcc, ~4 s. Env: PCREC, CC, TRIE_N, TRIE_SEED, KEEP=1.
- **run_codegen_tests.sh** — greps generated output for each optimization's
  signature (skip tables + skip loop, `start_max = 0` for fully-anchored
  patterns and its ABSENCE for partially-anchored ones, memchr prefilter,
  a table-size ceiling that only holds if minimization ran, engine selection
  for `$` vs `^`, and the M2.12 EOL-path checks: skips present and bounded at
  n-1, reverse skip entry guard, memchr bounded at n-1, and an ORDER check
  that accept/EOL evaluation follows the skips). Part of `make test`;
  env: PCREC, KEEP=1.

The M2.12 additions are the sharpest illustration of why this directory
exists: reverting the EOL path to its M2.7 state (no prefilter, no skips —
~76x slower on `$` patterns) fails 6 checks here while the .rxt corpus still
passes 53/53, because the change is behavior-preserving by construction.

## Two kinds of check live here

`run_codegen_tests.sh` asserts a SIGNATURE is present in the output — cheap,
but it only ever proves the optimization ran, never that it was right.
`run_trie_identity.sh` asserts EQUIVALENCE against a reference build with the
optimization off, which proves soundness across hundreds of patterns at once.
Prefer the second shape whenever an optimization is supposed to be
output-preserving; the M2 journal wrongly concluded M2.8 was not structurally
testable, and the equivalence check turned out to be both possible and far
stronger than the corpus (a broken disjointness guard shows up on 2 .rxt cases
and on ~14 patterns in 500 here).

An equivalence check has its own trap, and the fix for it is not optional: if
BOTH builds had the optimization off, every comparison would agree and the
script would certify a deleted optimization. `run_trie_identity.sh` therefore
carries POSITIVE CONTROLS — patterns whose NFA fits the cap only when factored,
so the two builds fail at different stages — and they are sabotage-validated.

**There are three of them, at 4, 8 and 256 branches, and the small ones are the
important ones.** The first version had only the 256-branch control while every
generated pattern had 3..8 branches, and a critic broke it in one clause:
`elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)` left all three checks
green, `make bench`'s KEYWORD-SCALE green, and the whole `make test` suite green
with the trie deleted for every hand-written pattern. A control that only proves
the optimization fires OUTSIDE the corpus's own range proves nothing about the
corpus. When adding an equivalence check, put a control inside the range of the
inputs it actually compares.

## Conventions

Every check must be validated against a deliberate sabotage: disable the
optimization in a scratchpad build and confirm the check FAILS. A structural
test that passes under sabotage is worse than no test — it certifies nothing
while looking like coverage. Sabotage the SPECIFIC branch under test, not the
feature containing it. When adding an optimization to src/gen or src/opt, add
its check here in the same change.

Validated sabotages for run_trie_identity.sh. **Record the exact edit, not just
the count** — the first version of this table carried a number produced by a
contaminated tree (two sabotages stacked, because a `git checkout` revert
silently failed inside a non-git tarball copy) and another that was never
measured at all:

| sabotage (exact edit) | .rxt | @200 | @500 |
|---|---|---|---|
| `return n;` as the first statement of `disjoint_run_len` | 2 | 21 | 64 |
| in rule 1, hoist every accept to the front instead of partitioning the list around each (keep removing them from the list) | 16 | 38 | 94 |
| `TRIE_ENABLED = 0` in the shipped build | 0 | 0 | 0 — only the CONTROLS fire |
| `elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)` | 0 | 0 | 0 — only the 4- and 8-branch controls fire |

Do NOT use the naive rule-1 sabotage (skip the accept split, change nothing
else): it leaves items with `len == depth` in the list for rule 2, which then
reads `seq + depth*32` past the allocated key — a 32-byte arena over-read, so
the count is unstable between builds (171 and 176 observed for the same edit).
The hoist form above is memory-safe by construction.

Maintenance: update this file when checks are added/removed.
