# Lane rxlib — design note: building patterns without rx literals, an `rx` module and a sequence operator (2026-11-17)

DESIGN NOTE ONLY. Nothing here rules; `docs/design/predicates_draft.md` is not edited; no `src/`, `cli/`, `lib/` or
`memfn/` edit; no `make`. The note is `docs/design/rx_module.md` (PROPOSED rev 0). Evidence:
`docs/dev/lanes/rxlib_evidence/rxlib_check.py` (output `rxlib_check.out`; PART n below).

## STATE AT HANDOFF

- OWED: none
- Rulings file `rxlib_rulings.md`: R1 and R2 APPLIED (re-read before each commit and before this report; R2 is the last
  entry). R1: proceed from `join`/`list_of`/`capture` and the 11-13 lean, the lean's reasons laid beside today's as a
  question (note section 3's table; question **sequence-operator**). R2: the owner's quantifier-operator idea (note
  section 3a; questions **quantifier-operators**, **quantifier-grammar**).
- PREMISE TEST (reported to the manager at the start): NO sequence operator in the draft, but more than holes and
  arrays: §2.5 "No concatenation operator" is an explicit LEAN (CF:69, the manager's; the owner had offered either
  form on 11-13) and §3.1 records "a record of rx is their sequence" NOT adopted; `join([...], sep = s)` is an n-ary
  sequence tool (§5.3, LEAN), `list_of(X, sep = ...)` a separated loop (no body, minimum OPEN), `[x = R]` a label
  without a literal (§3.1), `capture(x)`; the transforms with bodies (§2.7, §8). The note starts from them (section 0).
- Validation (run 2026-11-17, libpcre2-8 10.46, Python 3.14.4): PART A harness selfcheck 6 OK. PART B the three
  before/after examples: BEFORE vs AFTER and AFTER vs the Python `re` intent oracle differ on 0 texts in WHOLE,
  SEARCHED and FIND-ALL (B1 364 texts, B2 3,906, B3 341). PART C the two-copy separator loop vs a split oracle: 0 of
  1,093 for six (min, max) pairs; the one-copy form (conditional group, on PCRE2): 0 of 1,093 each. SABOTAGE
  (`RXLIB_SABOTAGE=1`: loop conditions after the loop, `optional` lazy): summary 0 -> 3,748; B1 2 / 324 / 364, B2 0 /
  480 / 704 texts differ; 20 output lines move. B3 does not move under the sabotage (it uses neither construct; its
  control is the oracle).
- Built-compiler checks for the level column (`/home/pcrec/projects/pcrec/build/pcrec -p rx --features all
  --engine=dfa|vm`, main's build of 2026-11-15): listed in the note's section 2 header.
- Standing questions: measurement regime NOT RELEVANT (no timing); independent control RELEVANT (hand-written regex
  models vs code-expanded definitions vs a Python `re` oracle; sabotage moves it); data regeneration NOT RELEVANT.
- Deliver file `rxlib_deliver.txt`: present, read, not edited, not committed.

## WHAT WAS WRITTEN

`docs/design/rx_module.md` (44 KB; line added to `docs/design/CLAUDE.md`, whose `inline_c_requirements.md` entry moved
to `docs/design/NOTES.md` for room, the precedent of 2026-11-10):
- Goals (G1 the regex model stays the meaning; G2 no new primitive; G3 a condition written where it means; G4 levels
  visible), the three standing questions, section 0 (what the draft already has).
- Section 1: the three before/after examples, run: B1 every item under 5 (`rx.loop(item € ";")` with the conditioned
  item), B2 the time `t2` with `(h: <13)` (labelled parts, `rx.optional`), B3 `(B | A) & (l: <20)` (the alternation;
  a shared label needs PCRE's branch reset `(?|...)`).
- Section 2: 25 constructs, each with its definition as regex text, arguments, definability today and level. 16
  definable today, 7 partly (row 6 from a string; row 12's separator form; rows 14-17 and 22 as `€` operands under the
  hole rule), 2 not (row 23 case-insensitive: `any_case` stays the primitive; row 24 a cross-part backreference).
- Section 3: `A € B` := `/${A}${B}/`; what it adds (a spelling, a chain, a precedence; nothing in meaning under the
  hole rule); the 11-13 reasons beside today's; precedence P1/P2/P3 with run examples; associativity; conditions in a
  sequence (PART D: a condition reading only labels already set gives the same answers at either place, 0 of 364;
  one reading a later part's label differs, 2 / 66 / 66); arrays stay alternations.
- Section 3a (R2): quantifier operators; `(?:\d+)?` and `\d*` try the same ends in the same order (3, 2, 1, 0), so the
  owner's "effectively `\d*`" holds for greedy forms; it FAILS for lazy: `(?:\d+)??` tries 0, 3, 2, 1, `\d*?` 0, 1,
  2, 3 (PART F); five grammar questions with two-way examples.
- Sections 4-5: labels (L1-L4, flat or nested flow, the same label twice), loops (every pass, last pass, the named
  request's home with lane lastpass's must-cover table mapped row by row, separators, counts, modes).
- FINDINGS a reviewer should check first: (1) a separator loop written as two copies of the item (the obvious
  definition, and what `list_of` would expand to) makes a bare label after it read the FIRST item, by PCRE's
  duplicate-name rule (PART E: `(?J)(?'h'\d)(?:;(?'h'\d))*=\k<h>` holds on `1;2;3=1`, fails on `1;2;3=3`), against
  last-pass-default; the one-copy form needs PCRE's conditional group, not built in pcrec. (2) Under the hole rule,
  anchors, `\b` and lookarounds cannot be operands of `€` (the edge-assertion error, §0.1 L8). (3) Lazy quantifier
  operators do not compose into their plain twins.
- Section 6 (what it does not change; the six missing pieces), a one-paragraph context on other libraries (the
  author's own knowledge, flagged), section 7 (the questions).

## QUESTIONS FOR THE OWNER

Ordered by dependence; each in the note's section 7 with state, candidates, one example in three modes and costs; no
recommendation.
1. **sequence-reading** — does `A € B` follow the hole rule (assertions at a part's edge an error) or splice text?
2. **sequence-operator** — have an infix sequence operator at all, given the 11-13 lean and `join`?
3. **sequence-precedence** — `€` against `&` and `|` (D196's order, `&` tighter, or `€` loosest).
4. **label-flow** — a part's labels in the whole: flat, nested under the part's name, or both.
5. **label-mark** — how a part is labelled: `[name = X]`, a construct, the binding's name, or a new mark.
6. **label-twice** — a label set by two parts: error, PCRE's first-set group, the last set, or both by request.
7. **separator-label** — a label in a separated loop: two-copy text (reads the first item), one-copy text (last
   pass, a conditional group), or "last pass" by definition.
8. **count-argument** — a count whose rx has several members: union in enumeration order, error, or hull.
9. **quantifier-operators** — postfix operators, named constructs, or both; which quantifier a lazy mark binds.
10. **quantifier-grammar** — postfix `+`/`*` vs arithmetic, `?` vs the conditional, braces, separators.
11. **every-pass-home** — the named all-passes request: on the loop, in the group questions, or the conditioned item.

## COMMANDS

W = /home/pcrec/projects/pcrec/worktrees/rxlib; run from `/var/tmp/pcrec-pcrec/scratch/rxlib`. Python 3.14 standard
library and the installed libpcre2-8 (10.46), through lane rxmodel's `pcre2h.py` (imported, never edited).

    timeout 900 python3 -I W/docs/dev/lanes/rxlib_evidence/rxlib_check.py > fwd.out      # a few seconds
    diff fwd.out W/docs/dev/lanes/rxlib_evidence/rxlib_check.out                         # prints nothing
    grep 'differ\|SUMMARY' fwd.out                       # PART B 0 everywhere; PART C two-copy and one-copy 0; SUMMARY 0
    RXLIB_SABOTAGE=1 timeout 900 python3 -I W/docs/dev/lanes/rxlib_evidence/rxlib_check.py > sab.out
    grep SUMMARY sab.out                                 # 3748
    diff fwd.out sab.out | grep -c '^<'                  # 20
    for p in 'a(?:b|c)*?d' 'a*+a' 'a++b' '(?>ab|a)c' '(?>\d+)x' 'x(?=\d)' '(?<=a|bc)d' '\bfoo\b' '\Aa\z' '(\d)\1'; do
      /home/pcrec/projects/pcrec/build/pcrec -p rx --features all --engine=dfa -o o.c --pattern "$p"; done   # levels
