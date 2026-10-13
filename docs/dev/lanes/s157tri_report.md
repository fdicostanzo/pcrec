# s157tri -- mech row S157 read UNDETECTED on main (2026-10-13)

## Cause: (b), a detection gap created by k93fix

The sabotage still applies (both anchors match once; the emitted code
differs on 25 of 259 call-bearing corpus patterns). The row's old witnesses
`^(a?)(?1)+a$`, `^(a?)(?1){2}a$` no longer reach its arms.

Bisect (sabotage applied by hand to `git archive` trees, `^(a?)(?1)+a$` on
"a", `--features all`):

| tree | sabotaged answer |
|---|---|
| 54c42e36a (121cdac9d^) | nomatch (detected) |
| 121cdac9d ([k93fix] joined call-site contexts) | match 0 1 (not detected) |

Why: since [K93] a callee's verdict is taken under the lexical follow
joined with every call site's follow (`cc_join` / `cc_widen`). In the old
witnesses the group holding `a?` is itself called, and its call site's
follow carries the literal tail `a`, so disjointness is refused with
`first_of(A_CALL)` emptied. The first arm's effect was reachable only through
the lexical follow, which the join now dominates for any CALLED group.

## Not an equivalent mutant

The arm still matters for a group NOTHING calls, whose only context is the
lexical follow: `^(a?)(?2)$(?(DEFINE)(a))` on "a" is `match 0 1` clean,
`nomatch` sabotaged (also `(?2)+`, `(?2){2}` on "aa"); stamp
`RX_VM_STRATS` backtracking -> possessive.

## Fix

Two cells added to QUANTIFIED in tests/recursion/gen_corpus.py (oracle
answers from libpcre2 via the generator), regenerated into
tests/recursion/quantified.rxt (only that file moves). The old three cells
stay as the pre-K93 record and still pass on the clean build. Row
expectation unchanged (DETECTED).

## Verdicts (single-row, `bash tests/mech/run_sabotage_matrix.sh S157`)

- before (main d67e07507): corpus 0fail/57pass, recdiff 0fail/10pass --
  UNDETECTED, UNEXPECTED.
- after (4ba75935f): corpus 4fail/64pass, recdiff 0fail/10pass -- DETECTED.
- clean-build harness run of quantified.rxt: 68 passed, 0 failed (rc 0).

Logs: worktrees/s157tri/build/s157_main.log, s157_after.log.

## Note

The row's header comment and tests/mech/CLAUDE.md still describe the old
witnesses as the detectors; not rewritten here (the DESC field stays true
for the pre-K93 mechanism). Candidate follow-up: a one-line pointer to this
report in the sabotage file.
