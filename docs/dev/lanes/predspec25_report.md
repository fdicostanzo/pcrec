# predspec25 — predicates_draft.md revision 25 (the 11-17 evening rulings and the rx module)

Lane predspec25 (2026-11-17, opus; DESIGN ONLY, no build go). Inputs: COND-FAMILY's entries from "2026-11-17 OWNER
RULING — pass-start-read" to the end of the file; `docs/design/rx_module.md`; `docs/design/predicates_future.md` items
19-25; rev 24.4 of the draft; predspec244's report and engine; the rulings file.

## STATE AT HANDOFF

STATE: done. `docs/design/predicates_draft.md` is at rev 25; evidence in `docs/dev/lanes/predspec25_evidence/`;
`docs/design/predicates_future.md` item 24 entries 17-20 APPENDED (nothing else there changed).
OWED: none.
RULINGS FILE: empty (re-read before each commit and before this report).
STOP RULE: nothing stopped. Every table or answer line the owner was shown in the applied entries reproduces (below).
The record does not contradict the brief. PREMISE: predspec244's engine re-ran byte-identical to its committed `.out`
(checks 129 of 129).
Head line BEFORE: `**rev 24.4: one label rule (branchings reset), the hit list atomic and anchored, the filter
sentence, join order (the owner, 2026-11-17 evening); NOT STABLE pending the owner's answers** (§R.8).`
Head line AFTER: `**rev 25: labels across parts (label-flow, pass-start-read, array-slot, numbers name the nearest
pattern's groups), the warnings set (structural or a library's, `pcrec.` names), and the rx module (a sequence
operator that splices, holes by position, counts by product, one repeat, nine postfix quantifier operators) (the
owner, 2026-11-17 evening); NOT STABLE pending the owner's answers** (§R.8).`
Size: 7,638 lines (919,410 bytes) before, 8,020 lines (967,407 bytes) after. Changelog: a new top entry.
REVIEWS: r40 C6 (the place table as the skeleton of the next full revision; filed in predicates_future.md item 22) is
STILL OPEN: rev 25 does not restructure the draft around a place table. r42 C3 (one severity-by-selector table) is
STILL OPEN; its trigger, "the next design step on warnings", is arguably reached by the warnings rulings applied here
(§R.2), so the manager may want to schedule it. No other r40 / r42 finding was reopened.

## RULINGS APPLIED

| record entry (COND-FAMILY, 2026-11-17) | his words quoted at | where in the draft |
|---|---|---|
| OWNER RULING — pass-start-read | R.1.7 PASS-START-READ ("pass-start-read: yes keep it") | R.1.7; §R.8 ruled list; §R.11 row 56 |
| OWNER RULING — shared-label: keep the compile error | R.1.13 SHARED-LABEL ("keep the compiler error. It does cause problems for library writers...") | R.1.13; superseded by label-flow (§R.9 row); §R.11 row 57 |
| OWNER RULING — array-slot: only what was set | R.1.7 ARRAY-SLOT ("only what was set. As you say, someone could get the empty values.") | R.1.7; item 24 entry 20; §R.11 row 58 |
| OWNER — a principle for warnings | §R.2 THE WARNINGS ("Warnings should be structural or definable by a library option.") | §R.2; §R.11 row 59 |
| OWNER RULING — warnings: the list accepted; library warnings named by the library path (+ ADDENDUM) | §R.2 THE WARNINGS (library path; `@config.warn.off(...)`; "prefixed with "pcrec."") | §R.2; §7.1 mark; spellings 10; item 24 entry 17; §R.11 row 60 |
| OWNER RULING — empty-search-error: a warning | §R.2 table ("empty-search-error: warning") | §R.2; §7 mark; §R.11 row 61 |
| OWNER RULING — the three remaining error-or-warning candidates | §R.2 table ("Agree with all three. But for: $x & <5 How is that not an error?$x is not a pattern but a match") | §R.2; §2.6, §4.1, §0.1 L28, §13 O58 marks; §R.11 row 62 |
| OWNER — the numbered-label warning accepted | §R.2 ("Agree. Good warning"); R.1.4 zero-place | §R.2; §7.1 mark; §R.11 row 63 |
| OWNER, three points on labels | R.1.13 SETTING A LABEL, NUMBERS NAME THE GROUPS ("setting labels is just the label using the group-label-not-capture syntax"; "Makes sense") | R.1.13; §R.11 row 64 |
| OWNER — label numbers: try them (+ ADDENDUM) | R.1.13 LABEL NUMBERS, TRIED ("Let's see how label numbers work and try it"; "the error ... would apply to n and 2 above") | R.1.13; §R.8 (b) numbered-duplicate, sequence-numbers; §R.11 row 65 |
| OWNER RULINGS — the rx module: sequence-precedence and sequence-operator | R.1.14 THE SEQUENCE OPERATOR ("binds tighter than & and |"; "is there a reason why not?") | R.1.14; §2.5 mark; §R.9 row; §R.11 row 66 |
| OWNER RULING — sequence-reading (+ his hole question) | R.1.14 SEQUENCE-READING ("sequence-reading: splice.") | R.1.14; §R.11 row 67 |
| OWNER PROPOSAL — label-flow; OWNER RULING — label-flow (+ ADDENDUM) | R.1.13 LABEL-FLOW (his four points; "a compose and a literal rx have the same label behavior"; "its the last mention") | R.1.13; R.1.4; §R.6 rows; §R.9 row; §R.11 rows 68-69 |
| OWNER RULING — hole-reading | R.1.14 HOLE-READING ("agree and explicitly then, assertions become ok to cross the border") | R.1.14; R.1.4; §0.1 L8, §11 HOLES and role table row 5 marks; §R.9 rows; §R.11 row 70 |
| count-argument discussion; OWNER RULING — the count proposal | R.1.14 COUNTS ("i agree with the count proposal ... is it a primative?") | R.1.14; §R.11 rows 71, 73 |
| OWNER — one repeat construct; plurals as conveniences | R.1.14 ONE REPEAT CONSTRUCT ("i agree with repeat. i agree with plurals, why not...") | R.1.14; §R.11 row 72 |
| OWNER RULING — two kinds of hole; illegal combinations are removed (+ ADDENDUM) | R.1.14 ONE INSERT ("it is a context aware rx insert ... remove illegal versions from the cartesion product"; "the kinds are all the various places") | R.1.14 position table; §R.8 hole-member-kind; §R.11 row 74 |
| OWNER RULING — quantifier operators (+ two ADDENDA) | R.1.14 THE POSTFIX QUANTIFIER OPERATORS ("+ +? * *? ? ??"; "lets include the possessive forms but the brace counts are repeat"; "fairly tight with parenthesis otherwise") | R.1.14; §R.8 plus-operands, quantified-condition; spellings 12; item 24 entries 18-19; §R.11 row 75 |

SUPERSEDED, and the draft says so: shared-label's error of existence by label-flow's error of reference (R.1.13,
§R.6, §R.9); §2.5's lean against a concatenation operator; §0.1 L8 / §11's edge-assertion error for holes; §11's "every
hole denotes a set of strings"; §7's empty-match error; §2.6's `min` limit; `compare.width` as a compiler warning;
`rx_module.md`'s union reading of a several-member count (§R.9 rows for each).

## WHAT MOVED

Answers that MOVED from rev 24.4's text (each a line of `predspec25_model.out`):
- `/x${num}/`, num := `/\b\d+\b/` (§0.1 L8): was the EDGE-ASSERTION ERROR; now `/x(?:\b\d+\b)/`, never matching (0 of
  364 texts), the can-never-match warning's case.
- §7's empty-match hazard in a predicate program: was an ERROR; now PCRE's empty matches with `pcrec.empty.search`:
  `/(?<h>\d*)/ & NOT (h: <5)` FIND-ALL `7a3` [`7`@0, ``@1, ``@2, ``@3].
- `occurrences(/\d/, min = 2)`: was an ERROR; now WHOLE `1a2` HOLDS, SEARCHED `1 a2 3`@0.
- A name surfaced by both sides of `&`: was an error wherever it occurs (shared-label); now an error only where
  referenced; `[aa = A] & B & (aa.h: <2)` gives rev 24.4's LEFT line.
- `rx_module.md`'s two-argument count with n := [2, 4] (its C1 "union" reading, exactly 2 or exactly 4): now two to
  four digits by the product with removal (`(?|\d{2,2}|\d{2,4}|\d{4,4})`, WHOLE `123` HOLDS).
- `occurrences(x) & occurs.at_least(2, ..)` on `aab` (x := `/aab|a/`), which §13 O58 said rejects: under branch-scope
  re-entry it HOLDS, as `{2,}` does; only the atomic hit list rejects (PART E).
- The postfix quantifier operators, the sequence operator and the value-position holes are NEW surface (no earlier
  answer).

## SHOWN TABLES REPRODUCED OR STOPPED

Every one REPRODUCED; none stopped.

| shown to the owner (record entry) | result | PART / tag |
|---|---|---|
| the sorted list (pass-start-read), 6 WHOLE and 2 SEARCHED lines on libpcre2 | 8 of 8 as shown, libpcre2 and the engine; engine = libpcre2 on 0 / 0 / 0 of 1,365 | PS |
| the corrected restatement "every item except the LAST" | 0 of 1,093 differ from the Python intent | PS |
| array-slot's `7;;3;` ([`7`, `3`] against an empty slot) | [`7`, `3`]; the item-label lean [`7`, ``, `3`, ``] | AS |
| shared-label's LEFT line (as `aa.h` under label-flow) | `12` HOLDS, `21` FAILS; `12`@3; [`12`@0, `10`@6] | LF |
| label-flow's two cases (i) unset on `7`, (ii) the lookahead | (i) unset (engine = static-order 0 / 0 / 0 of 364); (ii) `1,2`@0 h = `2` | LF |
| the label-number example `(a)(?:b)(?<n>c)(?=d)((d)e)` | groups [abcde, a, c, de, d], as the manager said | NUM |
| rx_module.md's splice answers and precedence answers (P1 etc.) | as shown; each = hand-written regex on 0 of 364 / 781 | RX1, RX2 |
| the count pairs and "two to four digits" (the manager's hand reasoning, shown as unrun) | RUN, agrees: `(?|\d{2,2}|\d{2,4}|\d{4,4})`, 0 of 364 vs `\d{2,4}` | RX5 |
| the repeat's labels (the manager's answer to "can i name the item") | RUN, agrees (`3417` FAILS, `341` HOLDS a = `1`, ...) | RX6 |
| the empty-search row and the min-values row (the three candidates) | as shown; empty-search engine = libpcre2 0 of 121 | E |

HAND-WORKED, marked in the draft: none left; the label-mark example first written by hand was RUN (PART RX, RXL) and
replaced.

## MANAGER READINGS NOT IN THE OWNER'S WORDS

Each is marked THE MANAGER'S READING / MINE / THE DRAFT'S READING in the draft.

| reading | where | run verdict |
|---|---|---|
| the sorted list relies on a label set inside a lookahead being visible after it | R.1.7 | SUPPORTED (libpcre2 agrees); still asked as **lookahead-labels** |
| the corrected restatement "fail if anything besides the LAST matches C" | R.1.7 | SUPPORTED (0 of 1,093) |
| the `when((h: /\d/), (n: >= $h))` spelling equals the one callout | R.1.7 | SUPPORTED (0 / 0 / 0 of 1,365) |
| array-slot's lean: label the whole item to keep empty values | R.1.7 | SUPPORTED (PART AS) |
| looped-warning is `label.unset` seen under the one rule | §R.2 | NOT SUPPORTED: the triggers differ in two of five programs (PART W) |
| the `pcrec.` prefix makes library and compiler names collision-free | §R.2 | by construction (not runnable) |
| the answer to his "helpful or dangerous" on broad selectors | §R.2 | not runnable (an opinion) |
| the answer to "did we decide on a way to set labels" | R.1.13 | not runnable (a reading of §3.1) |
| numbers never collide across `&` (the nearest pattern's groups) | R.1.13 | SUPPORTED (PART NUM) |
| PCRE's numbering kept (capturing groups only, by opening parenthesis, local to each literal) | R.1.13 | SUPPORTED (libpcre2, PART NUM) |
| juxtaposition collides with five forms | R.1.14 | not runnable (grammar) |
| `/${rx}?/` acts on the whole rx (hole rationale) | R.1.14 | SUPPORTED (RX3: `ac` FAILS vs a string insert's HOLDS) |
| a dead edge assertion is a can-never-match warning | R.1.14 | SUPPORTED (0 of 364 match) |
| last mention is not last match, cases (i)/(ii) | R.1.13 | SUPPORTED; confirmed by him ("yes, i agree with those points") |
| the count hand reasoning (pairs; two to four) | R.1.14 | SUPPORTED (RX5) |
| the repeat-label answers | R.1.14 | SUPPORTED (RX6) |
| `repeat` is not a primitive (unbounded needs a body without a maximum) | R.1.14 | answer-free (the draft's reading of the body) |
| the removal warning and the position table (a position with no row an error) | R.1.14 | proposals; the table's count row RUN (RX4, RX5), the kind column asked (**hole-member-kind**) |
| the copies share group numbers; product order first-hole slowest | R.1.14 | SUPPORTED as answer-free (0 / 0 / 0 over seven sets) |
| operators read longest first; after `+` / `*` an operand-starting token makes it binary | R.1.14 | SUPPORTED (RX9 tokenizer) |
| "adding two patterns is an ordinary type error" | R.1.14 | COLLIDES with ruled R.1.12; asked (**plus-operands**) |
| "a quantifier on a condition is a type error" | R.1.14 | NOT SUPPORTED as entailed: regex gives the piece a meaning (RXQ); not adopted, asked (**quantified-condition**) |
| possessive forms excluded (the manager's earlier list) | R.1.14 | superseded by his ADDENDUM (included) |
| an ambiguous reference propagates through composition (`/${A & B}x/`) | R.1.13 | answer-free (the draft's reading) |
| which "at least n" (re-cutting, as `{n,}`) | §R.2 | SUPPORTED: (C) = (B) 0 / 0 / 0; the hit list differs 17 / 17 / 17 of 364 |

Count: 25 readings; 2 the runs do NOT support (looped-warning = `label.unset`; a quantified condition a type error),
1 collides with a ruling (the type-error sentence for `+`).

## OWNER QUESTIONS LEFT

New in rev 25 (§R.8 (b), each with the current definition, WHOLE / SEARCHED / FIND-ALL answers, a several-match
subject, not chosen):
- **numbered-duplicate**: a number on a group whose name another group shares: the name's label, or the group's own.
- **sequence-numbers**: what `1` names after the sequence operator (written-out, none, or the nearest literal).
- **plus-operands**: arithmetic on one-member patterns ("a constant is an rx") against "adding patterns is a type
  error".
- **quantified-condition**: a postfix operator after a condition (regex's meaning or a refusal).
- **hole-member-kind**: in a value position, legality by the pattern (PCRE reads `\d{x}` as text) or by the position's
  kind.
Still open from rev 24.4 (kept): empty-pass, outer-pass-forms, value-point, hits-pass, some-own, same-results,
unsettable-label, sql-picture, complement-place, nested-complement, repeated-means, group-truth / pass-table,
lookahead-labels, atomic-spelling, options-spelling, conditional-spelling, every-pass-spelling; **label-mark** listed
in the remaining table. Removed (ruled): pass-start-read, shared-label, array-slot, empty-search-error,
label-twice-warn, min-values, dollar-condition, numbered-label-warning; withdrawn: looped-warning. The spellings list
has 15 entries, none settled.

## EVIDENCE AND COMMANDS

All from `$PCREC_TMPDIR/scratch/predspec25` (`/var/tmp/pcrec-pcrec/scratch/predspec25`); `<wt>` is
`/home/pcrec/projects/pcrec/worktrees/predspec25`; libpcre2-8 10.46 (installed) through
`docs/dev/lanes/rxmodel_evidence/pcre2h.py` and ctypes.
- PREMISE: `timeout 1800 python3 -I -B <wt>/docs/dev/lanes/predspec244_evidence/predspec244_model.py > premise.out`
  then `diff premise.out <wt>/docs/dev/lanes/predspec244_evidence/predspec244_model.out`: identical; CHECKS 129 of 129.
- FORWARD: `timeout 900 python3 -I -B <wt>/docs/dev/lanes/predspec25_evidence/predspec25_model.py > fwd.out`: CHECKS
  42 of 42 OK; committed as `predspec25_evidence/predspec25_model.out`. Every number in the draft's rev 25 text and in
  this report is a line of it (PARTS PS, AS, LF, NUM, RX, E, W).
- SABOTAGE: `PREDSPEC25_SABOTAGE=1 timeout 900 python3 -I -B <wt>/docs/dev/lanes/predspec25_evidence/predspec25_model.py
  > sab.out`: 29 of 42 OK; FAILED: the PS shown lines (4), PS engine = libpcre2, the two PS oracles, RX2 (2), RX4,
  RX5, RX8 (2): caught. It does not reach PARTS LF, NUM, E, W (no sabotaged rule there; their controls are libpcre2
  and the static-order model, independent of the engine's label rule).
- Engine description, controls and limits: `predspec25_evidence/CLAUDE.md`.
