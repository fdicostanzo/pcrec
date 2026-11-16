# Lane absent: a condition on an ABSENT label, the options side by side

Lane absent, 2026-11-16, opus, DESIGN ONLY (no build go; nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/`; no
edit to `joint_condition.md`, `predicates_draft.md`, the rulings record or `predicates_future.md`). Branch `lane/absent`
(cut from `lane/jcfix`, main merged). The owner's direction (CF 13:38, verbatim): "absents-hold: do work it out but
consider also the option that missing means failing. Or options where the user can control the interpretation". This
report chooses nothing; every sentence not quoted or cited is the lane's.

EVIDENCE. `docs/dev/lanes/absent_check.py` / `.out`, run from the worktree root as
`timeout 120 python3 -I docs/dev/lanes/absent_check.py` (1.4 s; libpcre2-8 10.46, Python 3.14.4). Every count below is
from that output unless another command is named. Its kinds of result:

- RUN: (SP) every spelling group is the SAME language (all strings over the row's alphabet up to length 5 or 6, both
  engines: 0 pairs differ), and the parse fact each row rests on (which construct the match entered) is read from
  PCRE2's capture state through probe groups.
- COMPUTED: each option's answer, from the option's one declared table (`resolve()` in the script: absence kind x
  option -> the default's text, EMPTY, or FAIL), on the subject split by string code.
- ENGINE-RUN: for (TM), (RZ), (OP), (DL) the H, F and T answers are also built as regexes from the rule stated over
  intervals and run against the computed answer: 72,196 engine cases, 0 differ, 0 engine disagreements.
- CONTROL: the T columns are compared with the earlier lanes' own functions (jcfix's (OP) record and its (UP) readings
  Y, W', W; jcfold2's (RZ)/(ZN) `&` reading; unsetdef's (D1), (DA), (DL); jointexp's (U), (S); jcfold2's (ZD) b, c):
  53,366 comparisons, 0 differ.
- SABOTAGE: `ABSENT_SABOTAGE=1 timeout 120 python3 -I docs/dev/lanes/absent_check.py` (the H unfolds lose their absent
  branch, the F unfolds gain one): 210 differ, so the check can fail.

One modelling choice, named: every option's column reads a one-label condition's absent part by the SAME projection as
a joint one (the part ranges over its group's strings; jcfix's lean domain). Today's ruled one-label zero-pass rule is
"holds" (vacuous). The two agree on every population here except one subject, `0-3` in (ZE), where the set is empty
for that match (section THE OPEN CORNERS UNDER EACH).

## STATE AT HANDOFF

- STATE: done. Commits on `lane/absent`: the evidence script and its output (two WIP commits), this report, the
  history-index line.
- Rulings file `docs/dev/lanes/absent_rulings.md`: EMPTY at every read (before each commit, before the runs, before
  this report). Last entry applied: none.
- OWED: none.
- Nothing ruled was edited. `docs/design/CLAUDE.md` not touched; no file added under `docs/design/`.
- Deviations from the brief, named: (1) H is worked in two sub-readings (H, H-d2) because the default's reach under H
  is a real choice; (2) one option of the lane's own is added, X1 (the owner's 13:29 remark taken literally); (3) three
  populations not in the brief's list are added and their counts kept apart (marked ADDED): (D1) without a default,
  (DA) the alternative not taken, (DL) without a default.

## THE OPTIONS

Absence KINDS used throughout (where the match stopped short of the label, `predicates_draft.md` §4.2's "deepest
construct entered"): O an optional or `{0,1}` skipped; A an alternative not taken; Z a loop (upper bound 2 or more)
reached and run zero times; EO an optional around the label's loop skipped; EA an alternative around the loop not
taken. Inside a loop a label may also be missing from ONE pass while set in another (scope "in a pass").

Results of an absent part: the DEFAULT's text read; EMPTY (the part ranges over its group's strings: for a product the
other parts are tested on their own, for any other set the outside parts must be possible for some value: the
projection, J7's manager's wording); FAIL.

### T, today's ruled line, and its two sub-readings

RULE: Z gives EMPTY and never reads a default (J7, CF 12:45; §4B.1); O, A, EO, EA leave the label UNSET: FAIL unless a
default, then the default is read (J6, CF 11:05; §4.2 per match, CF:997-1000). The open sub-choice, for a label
missing in one pass of an enclosing loop (jcfix's THE OPTIONAL-IN-A-PASS CASE):

- T-pass: unset is judged PER PASS (the draft's :1694 "a label the iteration did not set is unset in it", §2.6 LEAN;
  §4B.1's LOOPED row). That pass FAILS, or reads the default. jcfix's (A) and (Y).
- T-match: unset is judged PER MATCH. The pass reads like a zero-pass reach (EMPTY, default NOT read); only a label
  with no value in the whole match is unset. jcfix's (B) and (W').

| state | plain condition / record, no default | with `= v` | `some` / `count` |
|---|---|---|---|
| a value | tested | tested, v unread | counted |
| Z: a reached loop ran zero times | HOLDS; outside labels tested (projection) | HOLDS, v NOT read | not counted |
| O, A, EO, EA: never reached | FAILS (`label.unset` warns) | v read | not counted |
| missing in one pass, set in another | T-pass: FAILS / T-match: as Z | T-pass: v read / T-match: v NOT read | not counted |
| missing in every pass that ran | FAILS | v read | not counted |

Concept count: 3 absence states (zero passes, unset, missing-in-a-pass), and to tell Z from the rest an author must
read the quantifier's upper bound (1 vs 2 or more) and whether an alternative or an optional encloses the loop. Two
default rules (read on unset, not on zero passes). Review OWNER-6 counted 7 live forms in today's text.

### H: absent HOLDS

RULE (one sentence): a condition tests the values that exist; an absent label's part is EMPTY (it ranges over its
group's strings, so a joint condition asks that the present parts be possible); "unset" disappears; presence is
required with `some(...)`, a count, or the pattern itself; a default gives an absent label a value.

The default's reach is a real choice, so two sub-readings:

- H: the default is read on EVERY absence, the empty loop's included. `predicates_future.md` item 7 is then not a
  separate idea, it is the rule.
- H-d2: the default is read for a field missing from a tuple that exists; never for the looped part of a zero-pass
  tuple. This keeps item 7 out, but the DEFAULT then distinguishes two absences again (`x?` reads it, `x*` does not),
  so H-d2 fails the spelling test for defaults (it passes it for plain conditions).

| state | no default | with `= v` | `some` / `count` |
|---|---|---|---|
| a value | tested | tested | counted |
| absent (any kind, any scope) | part EMPTY: holds unless no value of the group could satisfy | v read (H-d2: not on an empty loop) | not counted |

Concept count: 1 absence state, 1 rule, 1 default rule (H) or 2 (H-d2). Needs one sentence the draft lacks: a
set-once label is a list of 0 or 1 values for the group questions (the owner's "Even /x?/ is a loop from 0 to 1").

### F: absent FAILS

RULE (one sentence): a condition naming a label that has no value fails, an empty loop included, unless the author
wrote a default, which is then read on every absence.

What an author writes to accept the absent case under F:

- a DEFAULT inside the set, for a one-label condition: `(n = 0: <5)` holds on the empty list. Under F the default must
  be read on zero passes (item 7 NECESSARY), or nothing short of an alternative accepts the empty list.
- defaults on EVERY label of a record, for the empty list of a record: `(h = 0: <10, m = 0: <30)` equals H's answers
  on all 259 (OP) subjects; with the default on m alone it differs on `''` (table (AU)).
- an ALTERNATIVE in the condition or the pattern: `P & ((n: <5) | ...)`, or `+` vs `*` in the pattern for "at least
  one" (which F already gives).
- NOT the guard `(m: <30) | !(m: /[\s\S]*/)`: per pass it is wrong. On `3:45,3,`, `(m: any)` fails (pass 2 has no m),
  so `!` is true and the whole condition HOLDS although 45 is not < 30 (DERIVED from F's table; not run).
- For a JOINT "does not matter" (the projection) NO single default serves: under F, `(h = 10, m = 0)` vs H's
  projection on (DL) without a default differs on 71 of 585 (`9,`: H holds because 9:30 is possible, F with m = 0
  reads 9:00) (table (AU)). This is unsetdef's (DD) date finding, generalised.

| state | no default | with `= v` | `some` / `count` |
|---|---|---|---|
| a value | tested | tested | counted |
| absent (any kind, any scope) | FAILS | v read | not counted |

Concept count: 1 absence state, 1 rule, 1 default rule. No projection anywhere (nothing is ever "possible for some
value"), so the domain of "some value" (jcfold2 corner 2) never arises.

### X1 (the lane's addition): every quantifier with minimum 0 is a loop; only an alternative is "a complete no set"

The owner's remarks (CF 13:29, 13:38), "Even /x?/ is a loop from 0 to 1" and "Only an alternation would be a complete
no set, no?", taken literally. RULE: O, Z, EO (a quantifier ran zero times, `?` included) give EMPTY; A, EA (an
alternative not taken) FAIL. A default must be read on the zero-run kinds too, otherwise `(h, m = 0)` on optional
minutes would never be read (the whole of §4B dies); so X1 adopts item 7.

| state | no default | with `= v` |
|---|---|---|
| a value | tested | tested |
| a quantifier ran zero times (`?`, `{0,1}`, `*`, `{0,n}`, an optional around a loop) | EMPTY | v read |
| an alternative not taken (around the label or its loop) | FAILS | v read |

Concept count: 2 absence states, told apart by quantifier vs alternation (no upper-bound rule).

### U, the author controls the reading

Survey of the candidates (each worked in section AUTHOR-CONTROLLED FORMS):

- U1: the existing default `(m = v: S)` as the ONLY control, over H or over F. One concept.
- U2: a marker meaning "absent is acceptable" / "absent is not acceptable". Placeholders, NOT spellings: `ABSENT-OK`,
  `ABSENT-FAILS`. Three positions: (U2a) a set member on the value side (`predicates_future.md` items 5-6, the owner's
  `epsilon` / "unset"); (U2b) a mark at the label, left of the colon, in the slot the default uses; (U2c) the owner's
  own `m = some(S)` (default-set, CF 10:43) read as the marker, `m = some(<the group's strings>)` = ABSENT-OK.
- U3: ONE fixed base rule, with the existing group questions (`all`, `some`, `count`) as the control.
- U4: the pattern's spelling as the control (`+` vs `*`, the draft's "+ or * control", CF:933). This IS T.

## THE SPELLING TEST

Table (SP). `(n: <5)` on a subject where n has no value; rows grouped by EQUAL patterns (RUN: each group accepts one
language; each row's kind RUN by probe). A group is marked **SPLIT** under an option when its rows answer differently.
Cells: H = HOLDS, F = FAILS.

| group | spelling | subject | kind | T-pass | T-match | X1 | H, H-d2 | F |
|---|---|---|---|---|---|---|---|---|
| x? | `(?<n>\d)?x` | `x` | O | F | F | H | H | F |
| x? | `(?:(?<n>\d)\|)x` | `x` | A | F | F | **F** | H | F |
| x? | `(?<n>\d){0,1}x` | `x` | O | F | F | H | H | F |
| x? | `(?<n>\d)??x` | `x` | O | F | F | H | H | F |
| x* | `(?<n>\d)*x` | `x` | Z | H | H | H | H | F |
| x* | `(?:(?<n>\d)+)?x` | `x` | EO | **F** | **F** | H | H | F |
| x* | `(?:(?<n>\d)+\|)x` | `x` | EA | **F** | **F** | **F** | H | F |
| x* | `(?:(?<n>\d)*)?x` (greedy) | `x` | Z (PCRE enters the optional) | H | H | H | H | F |
| x* | `(?:(?<n>\d)*)??x` (lazy) | `x` | EO (PCRE skips it) | **F** | **F** | H | H | F |
| x{0,2} | `(?<n>\d){0,2}x` | `x` | Z | H | H | H | H | F |
| x{0,2} | `(?:(?<n>\d){1,2})?x` | `x` | EO | **F** | **F** | H | H | F |
| x\|y | `(?:(?<n>\d)\|y)` | `y` | A | F | F | F | H | F |
| optional in an item | `(?:a(?<n>\d)?,)*` | `a,` | O | F | F | H | H | F |
| optional in an item | `(?:a(?:(?<n>\d)\|),)*` | `a,` | A | F | F | **F** | H | F |
| the same, one pass | `(?:a(?<n>\d)?,)*` | `a3,a,` | O | F | H | H | H | F |
| the same, one pass | `(?:a(?:(?<n>\d)\|),)*` | `a3,a,` | A | F | H | **F** | H | F |
| loop in an item | `(?:a(?<n>\d)*,)*` | `a,` | Z | H | H | H | H | F |
| loop in an item | `(?:a(?:(?<n>\d)+)?,)*` | `a,` | EO | **F** | **F** | H | H | F |
| loop in an item | `(?:a(?:(?<n>\d)+\|),)*` | `a,` | EA | **F** | **F** | **F** | H | F |
| the same, one pass | `(?:a(?<n>\d)*,)*` | `a3,a,` | Z | H | H | H | H | F |
| the same, one pass | `(?:a(?:(?<n>\d)+)?,)*` | `a3,a,` | EO | **F** | H | H | H | F |
| the same, one pass | `(?:a(?:(?<n>\d)+\|),)*` | `a3,a,` | EA | **F** | H | **F** | H | F |
| loop in an optional in an item | `(?:a(?:-(?:(?<n>\d),)*)?;)*` | `a-;` | Z | H | H | H | H | F |
| loop in an optional in an item | `(?:a(?:-\|-(?:(?<n>\d),)+)?;)*` | `a-;` | EA | **F** | **F** | **F** | H | F |
| the same, item skipped | `(?:a(?:-(?:(?<n>\d),)*)?;)*` | `a;` | EO | F | F | H | H | F |
| the same, item skipped | `(?:a(?:-(?:(?<n>\d),)*\|);)*` | `a;` | EA | F | F | **F** | H | F |
| the same, one pass | `(?:a(?:-(?:(?<n>\d),)*)?;)*` | `a-3,;a;` | EO | F | H | H | H | F |
| the same, one pass | `(?:a(?:-(?:(?<n>\d),)*\|);)*` | `a-3,;a;` | EA | F | H | **F** | H | F |

Groups SPLIT, of 11 (the script's per-option count):

| option | split groups | which |
|---|---|---|
| T-pass | 5 | x*, x{0,2}, loop in an item (both subjects), loop in an optional in an item |
| T-match | 4 | x*, x{0,2}, loop in an item (`a,`), loop in an optional in an item (`a-;`) |
| X1 | 9 | every group holding an alternative beside a quantifier |
| H, H-d2 | 0 | (H-d2 splits for a DEFAULT: `(?<n>\d)?x` reads it, `(?<n>\d)*x` does not; DERIVED from its table) |
| F | 0 | |

A fact the RUN probe adds: `(?:(?<n>\d)*)?x` and `(?:(?<n>\d)*)??x` differ ONLY in laziness, and PCRE's parse enters
the greedy optional (its `*` runs zero times: Z, holds under T) but skips the lazy one (EO, fails under T). Under T,
greedy vs lazy changes a condition's answer on a pattern whose matches are identical.

## WHAT MOVES UNDER EACH

Table (MV), moved = answers that differ from T-pass, then from T-match. Ruled populations only (the brief's list):
48,180 answers per option.

| population | answers | T-match | X1 | H | H-d2 | F |
|---|---|---|---|---|---|---|
| (U) `((h, m, s): padded(>= (9, 0, 30)))`, s optional | 7 | 0 | 3 | 3 | 3 | 0 |
| (S) `((h, m): padded(> (9, 30)))`, m optional | 6 | 0 | 2 | 2 | 2 | 0 |
| L56/L65 witnesses, `(n: <5)` | 5 | 0 | 2 | 3 | 3 | 2 |
| (RZ) `(h: <5, k: 3..7)`, h looped | 1,110 | 0 | 0 | 0 | 0 | 5 |
| (ZD a) `(h = 9: <5, k: 3..7)` | 1,110 | 0 | 5 | 5 | 0 | 5 |
| (ZJ) five non-product sets | 5,550 | 0 | 0 | 0 | 0 | 22 |
| (ZN) nested `(c, h, k)` | 2,526 | 0 | 0 | 0 | 0 | 69 |
| (OP) `(h: <10, m: <30)`, m optional per item | 259 | 8 | 11 | 11 | 11 | 1 |
| (UP) `(h: <5, k: <5)`, k's loop in an optional | 241 | 16 | 22 | 22 | 22 | 15 |
| (DL) `((h, m = 0): padded(between((9,30),(11,0))))`, looped | 585 | 46 | 0 | 0 | 0 | 1 |
| (ZD b) never reached, no default / `h = 9` / `h = 2` | 3 x 1,120 | 0 | 10 | 10 | 5 | 10 |
| (ZD c) `((h, m = 0): >= (5, 3))`, looped | 91 | 6 | 0 | 0 | 0 | 1 |
| (D1) `(m = 0 / 45 / 00: <30)` | 3 x 11,110 | 0 | 0 | 0 | 0 | 0 |
| TOTAL vs T-pass | 48,180 | 76 | 55 | 56 | 46 | 131 |
| TOTAL vs T-match | | 0 | 83 | 84 | 74 | 207 |

ADDED populations (33,915 answers: (D1) no default, (DA) both, (DL) no default): vs T-pass T-match 102, X1 251, H 255,
H-d2 255, F 1.

The smallest moved example of each kind (RUN as parse, COMPUTED as answer):

| kind | H (and X1 where it agrees) | F |
|---|---|---|
| optional field | `9:00` of (U) now in (`(9, 0, s) >= (9, 0, 30)` is possible); `9` of (S); `3,` of (OP) | none: F = T on every set-once optional |
| empty list | none without a default; with `h = 9`: (ZD a) `3` FAILS (the default read on zero passes) | `''` of (OP), (DL), (ZD c); `3` of (RZ) (k in 3..7, zero passes) |
| alternative not taken | `x` on `/x\|(?<n>\d)+/` (L65); `9 o'clock` of (DA, added); X1 does not move it | none |
| nested | `3;` of (UP) (pass skips k's optional: holds); `3:15,3,` of (OP) (vs T-pass) | `3-;` of (UP) (k's loop reached, zero passes) |

T-match vs T-pass (the undecided sub-choice inside today's text): `3:15,3,` (OP), `3-2,;4;` (UP), and on (DL) 46
answers, e.g. `9,10:30,` HOLDS under T-match: pass 1 has no minutes but m is set in pass 2, so pass 1 reads like a
zero-pass reach (9:30 is possible) and its default `m = 0` is NOT read. That contradicts §4B.1's LOOPED row ("an
iteration whose item skipped the label reads the default", lane unsetdef's reading), so T-match carries a second
change the T-pass reading does not.

### The time example (TM)

`t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/ & ((h, m): >= (9, 30))` (the DOM reading). COMPUTED for the four subjects;
ENGINE-RUN over all 11,110 `t2` subjects for T-pass, F, H.

| | `9` | `10` | `9:15` | `9:45` |
|---|---|---|---|---|
| T-pass, T-match, F, no default | FAILS | FAILS | FAILS | HOLDS |
| H, H-d2, X1, no default | HOLDS | HOLDS | FAILS | HOLDS |
| every option, `m = 0` | FAILS | HOLDS | FAILS | HOLDS |

Over 11,110 subjects: minutes-absent subjects accepted with no default, T-pass 0, F 0, H 91 (every canonical hour
from 9); with `m = 0`, 90 under all three.

### The record equality (EQ)

`(a: S, b: T)` vs `(a: S) & (b: T)`, each side under the SAME option: 0 differ under every option on (RZ) 1,110,
(ZN) 2,526, (OP) 259, (UP) 241. It survives at every depth and in every pass under T-pass, T-match, X1, H, H-d2 and F,
PROVIDED the one-label rule is read the option's way. Crossed (record one way, `&` the other): (OP) T-pass record vs
T-match `&` 8; (UP) 16 both ways. So under T the equality forces a choice between T-pass and T-match (jcfix's
finding, re-run); under H and F there is nothing to choose.

### The default under each option

| option | when `m = v` is read | item 7 (a default read on an empty loop) |
|---|---|---|
| T-pass | on unset (never reached), per pass; never on zero passes | optional: a separate rule to adopt or not |
| T-match | on unset in the WHOLE match; not on a pass missing m when m is set elsewhere ((DL) 46 move) | optional |
| X1 | on every absence | NECESSARY (else `?`-defaults are never read) and automatic |
| H | on every absence | automatic: it IS the rule ((ZD a): 5 move, `3` FAILS with `h = 9`) |
| H-d2 | on every absence except a zero-pass loop's part | excluded by sentence; costs the spelling test for defaults |
| F | on every absence | NECESSARY (the one-condition way to accept the empty list) and automatic |

Item 7's warning about overload (`m = 0` written for "an item without minutes is :00" also changes the empty list's
answer) is live under X1, H and F. Example (DERIVED): `list & ((h = 0, m = 0): >= (9, 30))` on the empty list HOLDS
under T and FAILS under X1, H, F.

`default.unused` (table (DU), (D1) population, is `(m = v: <30)` answer-identical to `(m: <30)`?):

| default | T-pass, T-match, F | X1, H, H-d2 |
|---|---|---|
| `m = 0` (inside the set) | used | UNUSED: it changes nothing, absent already holds |
| `m = 45`, `m = 00` (outside) | UNUSED | used: it makes absent FAIL |

Under H the warning's clause (b) inverts: a default OUTSIDE the set is the way to say "absent fails", and one INSIDE
is the one that warns.

## AUTHOR-CONTROLLED FORMS

**U1, the default as the only control.**

- Over H: "absent fails" is written as a default the set never admits (a sentinel), `(h: <10, m = x: <30)`. That
  reproduces T-pass on (OP) except the empty list (1 of 259, `''`), and on (DL) except `''` (1 of 585), because H
  reads the sentinel on the empty list too (table (AU)). One concept, but the idiom is opaque: the reader must know
  that `x` is outside `<30`, and `default.unused` inverts (above).
- Over F: "absent holds" is a default inside the set, per label; for a record's empty list, a default on every label
  (0 of 259 differ from H on (OP)). It cannot write a joint "does not matter" (71 of 585 differ on (DL)).
- Base rule when nothing is written: H's or F's. One concept.

**U2, a marker.** Two concepts (the default and the marker), unless merged into one slot (U2b/U2c).

- (U2a) a set member on the value side, `(h: S, m: T | ABSENT-OK)` (items 5-6). It fits a record (each label its
  own set) and has no place in a joint order: `((h, m): >= (9, 30) | ABSENT-OK)` has no meaning for one component.
  Item 5's note: it makes three ways to treat a missing field (default, alternative, member).
- (U2b) a mark at the label, left of the colon, in the default's slot: `(h, m ABSENT-OK): R`. The slot then has three
  fills: `= v` (read v), ABSENT-OK (the projection: "does not matter"), ABSENT-FAILS (fail). Over F only
  ABSENT-OK is needed; over H only ABSENT-FAILS. ONE place for every absence decision, per label, in every condition
  shape (single, record, joint).
- (U2c) the owner's own `m = some(S)` (default-set, CF 10:43: "Then there is a = some(between(...))"). Its reading is
  4B.6's SOME: the union of the slices. With S = the group's strings it IS the projection, i.e. ABSENT-OK. It reopens
  default-set (a several-string default is an error "for now") and L54's withdrawal of `some` on a set (4B.6).
- Base rule when nothing is written: whichever of H or F is chosen; with U2b over F the two-fill slot (`= v`,
  ABSENT-OK) covers every answer H gives (the projection) and every answer T gives (by leaving it FAIL), the empty
  list included (DERIVED from the tables: ABSENT-OK on every label of the empty list's tuple gives H's answer).

**U3, the group questions with one fixed base.**

- Over H: `(n: S)` is `all` (true over no values), `some((n: S))` is "a value exists and is in S", `count` counts. A
  set-once label is a list of 0 or 1 values. This is H, with presence written as `some`; it needs the sentence
  "a set-once label has 0 or 1 values for the group questions" and nothing else. Its limit: "EVERY item has minutes"
  over a loop is not `some`; it takes a count comparison (`count((m: any)) == count((h: any))`, needing an
  anything-set, item 8's snag) or the pattern (make m required), or U1's sentinel.
- Over F: accepting absence takes `(n: S) | occurs.none((n: any))` (an anything-set again), and per pass it has the
  guard's flaw (`3:45,3,` HOLDS, section THE OPTIONS, F). U3 is a natural control over H only.
- One concept (the group questions already exist), one new sentence.

**U4, the pattern's spelling (today).** The control is real for `+` vs `*` (an author who writes `+` gets "at least
one"). Its cost is the spelling test: 5 split groups of 11 under T-pass, 4 under T-match, among them a pair that
differs only in laziness. Behind each split is a refactor that changes no match and flips a condition.

## WHAT EACH REVERSES

Rulings and ruled sentences, per option (his words in quotes; "kept" = unchanged).

| ruling / sentence | T-pass | T-match | X1 | H / H-d2 | F |
|---|---|---|---|---|---|
| unset-component, CF 11:05, "unset-component: yes" (J6: unset FAILS unless a default) | kept | kept | REVERSED for `?`-skips | REVERSED | kept, widened to zero passes |
| per-match boundary, CF:997-1000, "Agree with lean" (§4.2: never reached FAILS; reached zero times HOLDS) | kept (J6 per pass) | kept literally | line MOVED (optionals hold) | "never reached fails" REVERSED | "zero times holds" REVERSED |
| the "+ or * control", CF:933 ("What's missing is the + or * control"), §4.2 :1601-1602 | kept | kept | kept for quantifiers | dropped as the absent control | dropped as the absent control (`+` still forces one) |
| zero-pass-record, CF 12:45, "zero-pass-record: I agree ..." | kept | kept | kept | answer kept (`9` FAILS), `&` equality kept; "'unset' keeps its meaning" goes | answer kept, `&` equality kept; the wording's "empty satisfies any set", "a plain single-label condition still HOLDS on zero passes" and "a default is NOT read there" REVERSED |
| §4B.1 "a default is never read on zero passes"; item 7 not adopted (12:45 notes) | kept | kept | REVERSED | REVERSED (H); kept (H-d2) | REVERSED |
| §4B.1 LOOPED row (default read per iteration; lane reading) | kept | CHANGED ((DL) 46) | kept | kept | kept |
| default-unused, CF 11:05, "default-unused: agree" | kept | kept | clause (b) inverts | clause (b) inverts | kept |
| §4.2 RULE: `[x = /\d/, y = /[a-z]/] & (x: /[0-5]/)` = `[0-5]` (the alternative lacking x drops); L6 | kept | kept | kept | REVERSED: `[0-5] \| [a-z]` | kept |
| §4.2 RULE, LEAN (CF:173): "a comparison on an UNSET label is false (its `!` true)"; the 4B.2 guard `!(m: /[\s\S]*/)` | kept | kept | for A only | `!` of an absent label's condition becomes FALSE; the guard no longer detects absence | kept |
| L36 / §4.3 :1659-1660 ("on ZERO iterations both HOLD") | kept | kept | kept | kept | REVERSED (both fail) |
| GROUP-ZERO (manager's reading, not ruled) | kept | kept | kept | kept ("some" = presence) | "tested by the plain condition and `all`" becomes "fails them" |
| default-set, CF 10:43, "We can punt, as you say, and throw an error" | kept | kept | kept | kept | kept (U2c alone reopens it) |
| record-is-product (11:35), joint-loops (11:17), pairing-loop part 1 (13:29), set-arity (10:26), label-twice (13:16), defaults one string | kept | kept | kept | kept | kept |

STOP-RULE check: every option can be stated as one rule; none contradicts an unlisted ruling. X1 is stateable only
with item 7 adopted (listed).

PROTECTION ("saving people from themselves", CF 12:45). Diagnostics each option needs or keeps (texts illustrative,
D26), and what each lets through silently:

- T: keeps `label.unset` (warns where a label can be unset, names both fixes) and `default.unused`. Silent: the empty
  list passes every "all items" condition; a refactor between equal spellings flips answers (the five split groups),
  with no diagnostic possible (two legal programs).
- X1: `label.unset` shrinks to alternatives. Silent: as T, on 9 split groups; a missing field passes (`9` vs
  `>= (9, 30)`).
- H: `label.unset` goes. It needs a NEW warning on a joint condition with a part that can be absent, since the
  projection is permissive, e.g. "m can be absent (the optional `(?::(?<m>\d\d))?`); `((h, m): >= (9, 30))` then
  holds when SOME m would put (h, m) in the set, so `9` passes. To read absent m as a value write `m = 0`; to require
  it write it in the pattern". Silent without it: `9` passes "at or after 9:30"; `semver2 & ((major, minor, patch): >=
  (1, 4, 2))` admits `1.4` (DERIVED); `/x|(?<n>\d)+/ & (n: <5)` admits `x`; filtering a labelled alternation by a
  label (`days & (x: S)`) keeps every other entry. `default.unused` inverts.
- F: keeps `label.unset`'s cases (now one message for every absence, e.g. "n has no value when the loop `(?:...,)*`
  runs zero times; `(n: <5)` then FAILS. To accept that, write `n = v` with v in the set, or `| ...`"). It fires on
  every condition over a `*` loop: noisy where vacuous truth was meant. Silent: nothing passes without a value; the
  risks run the other way (an empty list rejected), and the per-pass guard idiom `| !(m: any)` admits `3:45,3,`.

## THE OPEN CORNERS UNDER EACH

| open question | T-pass | T-match | X1 | H | F |
|---|---|---|---|---|---|
| pairing-loop part 2 (zero passes per reach) | the per-reach reading stands as drafted | same | same | answered by the rule (EMPTY per reach) | answered: every empty reach FAILS (`3-;` of (UP)) |
| pairing-loop part 3 (a pass that never reaches the pairing loop) | (Y): FAILS | (W'): h tested; k unset only if no pass reaches | (W) for an optional, Y-like for an alternative | (W): h tested | FAILS |
| THE OPTIONAL-IN-A-PASS CASE | (A) | (B) | (B)-like (holds) | holds (`3:15,3,`) | FAILS |
| zero-pass-empty | open | open | open | CLOSED if H's one-label rule is the projection (below) | CLOSED |
| the domain of "some value" (jcfold2 corner 2) | a zero-pass corner | same | wider (every `?`) | EVERY optional field, not a corner | never arises |
| GROUP-ZERO | the manager's reading | same | same | follows ("some" = presence) | plain and `all` fail on zero |
| tuple-parts | untouched | untouched | untouched | untouched | untouched |

Table (ZE) (jcfix's zero-pass-empty population, 11,100 subjects): with the one-label condition read by projection,
`(h: <$a, k: 3)` and `((h, k): < ($a, 0))` agree on all 1,110 subjects with a = 0, and `(h: <$a, k: 3)` and
`(h: <$a) & (k: 3)` on all 11,100, under every option (0 differ); on `0-3` all FAIL. With today's ruled VACUOUS one-label rule, `(h: <$a) & (k: 3)` HOLDS on `0-3`: 1 of 11,100 differ.
So the corner is created by the one-label rule being vacuous while the joint rule projects. F has no projection and
no vacuous truth, so it closes the corner outright. H closes it only if its one-label rule is "holds unless no value
of the group could satisfy" (the projection). Read as "holds whenever absent" it keeps the corner exactly as today.

## FOR THE OWNER

You asked for three options worked side by side, plus today's line. Each is below in one paragraph, with its rule.

**Today's line.** A loop of two or more that ran zero times passes. A skipped optional, an alternative not taken, or
an optional around a loop fails, unless there is a default. Equal patterns split: `(?<n>\d)*x` holds on `x`, while
`(?:(?<n>\d)+)?x` fails. So do greedy `(?:(?<n>\d)*)?x` (holds) and lazy `(?:(?<n>\d)*)??x` (fails). Five of eleven
groups of equal spellings split. Inside a loop it still owes you a choice: is a missing field judged per item or per
match? The two readings differ on 76 of the 48,180 answers tested.

**Absent holds.** A condition tests the values that exist; a missing one never fails it. No group splits. For a
condition over several labels, a missing field means "could it fit?". You give up unset-fails (11:05), half of the
per-match line (11-15), and "the alternative lacking x drops" when you filter a labelled alternation. A default is
read on every absence, the empty list's included (your item 7 becomes the rule). Presence is asked with
`some(...)`, a count, or the pattern.

**Absent fails.** A condition naming a label with no value fails, the empty list included, unless a default supplies
one. No group splits, and there is no "could it fit" anywhere. You give up the other half of the 11-15 line:
`/(?<n>\d)*x/` on `x` and the empty list now fail. A default inside the set is the way to accept absence, and it must
be read on the empty list. A missing field that "does not matter" across several labels has no one-default spelling
(the date case).

**You control it.** (a) The default alone, on top of either base. Under "holds", "must be present" is a default
outside the set, an opaque idiom. (b) A mark at the label, in the default's slot: `(h, m ABSENT-OK): R`. This is your
own `m = some(...)` with "any value of m", one slot for every absence decision. (c) Your `some`, `all` and `count`,
over "absent holds": `(n: S)` is "all of them", `some(...)` is "and at least one". (d) The pattern, as today.

The time example, `((h, m): >= (9, 30))`, minutes optional:

| | `9` | `10` | `9:15` | `9:45` |
|---|---|---|---|---|
| today, and absent fails, no default | fails | fails | fails | holds |
| absent holds, no default | holds | holds | fails | holds |
| any option, with `m = 0` | fails | holds | fails | holds |

The facts that separate them:

- **Equal spellings give equal answers:** under "holds" and "fails" always; today, not in 5 of 11 groups; "only
  alternatives fail" (your 13:38 remark taken literally), not in 9.
- **Answers that move**, of 48,180 tested:
  - "holds" moves 56: missing fields and alternatives (`9:00` of the seconds table, `3;`), plus 5 empty lists
    that carry a default (it is now read there);
  - "fails" moves 131, all empty lists or empty inner loops (`''`, `3`), none of them optional fields;
  - your 12:45 answer (`9` fails) and the record = `&` equality survive under every option (0 differ).
- **"Fails" never needs "could it fit"**, so the open question on empty sets (zero-pass-empty) disappears. "Holds"
  makes "could it fit" an everyday reading for every optional field.
- **The default:** under "holds" a default inside the set changes nothing (the unused warning flips sides); under
  "fails" it is the main tool.

---
What the evidence favours on each of his two stated criteria (the lane's, not a recommendation):
- Simplifying semantics: "holds" and "fails" each have one absence state and pass the spelling test; "fails" has no
  projection anywhere.
- Saving people from themselves: "fails" never passes a value that is not there; "holds" lets `9` through
  "at or after 9:30"; today's line lets a refactor between equal patterns flip answers silently.
