# Lane possside report

Branch `lane/possside` from main 225a0feb. Two items from `possarms_report.md`.
Validation COMPLETE: no long runs owed.

## 1. K94 — CONFIRMED on PCRE2 10.46, filed

Probe (ubuntubudu, `pcre2test` 10.46 2025-08-27, one run, scratch file removed):

    /(\xe9)\1/i,ucp          \xe9\xc9  -> 0: \xe9\xc9  1: \xe9
    /(\xe9)\1/i,ucp,utf      \x{e9}\x{c9} -> match
    /(\xe9)\1/i              \xe9\xc9  -> No match
    /(a)\1/i,ucp             Aa        -> match

pcrec (local build of the branch point, `--features all`):

    byte, default route, -i --ucp, (\xe9)\1 on \xe9\xc9   nomatch
    byte, --engine=vm                                      nomatch
    byte control \xe9\xe9                                  match 0 2
    byte control (a)\1 on Aa                               match 0 2
    -e utf8 (é)\1 on é É, with --ucp                        match 0 4
    -e utf8 (é)\1 on é É, without --ucp                     match 0 4

Scope: byte encoding only (default and VM routes alike); utf8 is correct.
Filed as K94 at the top of `docs/dev/known_issues.md`. Not fixed.

## 2. Give-up surface (D80 correction, no code)

Grep of `docs/spec/` for "one-way" / "give-up" found no sentence claiming
possessify's give-ups only disappear; the one-way claim lives in the design
note's row, not the spec. The spec gap was `tuning.md` §2.1 ("changes no
answer") with no budget caveat, and `limits.md` §7 with no mention. Hunks:

- `docs/spec/tuning.md` §2.1: new paragraph after "Reason it exists" — answer
  identity holds under default budgets; give-ups move in two directions.
- `docs/spec/limits.md` §7: new bullet "Possessification trades one counter
  for another".

Measured with the SHIPPED compiler (`--engine=vm`, 200 distinct words plus
`last last`, 1.5 KB, binary search on `--work-budget`): `\b(\w+)\b\s+\1\b`
minimum 581 under default AND `-fno-possessify` (580 gives up WORK); the
possessive `\b(\w++)\b\s++\1\b` minimum 1,586 (1,585 gives up WORK). So on
main the default does not possessify doubled-word (the [ART-POSS-ARMS] arms
do; the note's 1,070 -> 2,565 is that arms-armed measurement on its own
subject). I used the user-written possessive form as the shipped witness and
dropped the drafted sentence about the unbuilt arms.

`tests/registry/axes_registry_check.sh` (reads tuning.md): 205 passed, 0 failed.
