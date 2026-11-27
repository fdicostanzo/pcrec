# CRITIC ruling: predbang (r109)

## Findings

### RULING-1 (CONFIRMED; severity design; effort small; blast radius: V-A line 6, every condition negated beside a pattern) `A &! (h: <5)` as "negating a condition" is undefined by candidate line 3, and its natural reading is the meaning the record holds APART from NOT c
- Subject line 52 (record 11825, the manager's reading in the bang-split statement item 6) writes "the condition
  fails here" as `A &! (h: <5)`. Subject line 45 defines `&!` ONLY as `A & (0 :! B)`, the stretch difference ("A's
  stretch is not a B whole"); with B a condition, `(0 :! (h: <5))` puts a condition where a set stands: no meaning.
- The ruled record keeps the two apart: condition-not (2026-11-16, record 2053-2057): "the pattern difference
  `P & !(P & c)` differs from both on absent rows"; core.md core/conditions/two-valued (ruled 2026-11-17, lines
  1262-1268): `NOT (h: <5)` and `P & !(P & (h: <5))` are "three meanings", parting on P = `/(?<h>\d)?\d?x/`, `3x`.
- Own model (scr/andbang_cond.py, paths of P enumerated by hand, not the evidence's lowering), WHOLE, every subject
  over `0-9x` up to length 4 (16105): R1 = per-path NOT c (today's `!(h: <5)`) against R2 = the difference reading of
  `&!` (no path of `P & c` matches the stretch): 5 differ (`0x`..`4x`; `3x`: R1 HOLDS, R2 FAILS). MINIMUM WITNESS
  LENGTH 2. Control: R1 against `(h :! <5)` (present and outside): 6 differ (`x` among them), so the comparison sees
  a difference. One differing mode suffices to show the readings part; SEARCHED/FIND-ALL not needed for that claim.
- Expected: line 6 states which reading `A &! c` takes (a rule like core/filters/and's "a condition written in an
  `&` chain stands after every pattern operand" for `&!`, giving R1), or `&!` with a condition operand is a compile
  error and line 6 loses its middle form. As written the candidate re-spells condition-not with the operator whose
  definition is the meaning condition-not was ruled distinct from.

### RULING-2 (CONFIRMED by the quoted lines; severity design; effort small (a list per variant); blast radius: V-C, V-D) V-C and V-D reverse ruled errors of drop-not and of the complement rulings, and the subject does not name them
- drop-not (2026-11-25 OWNER RULING, record 10831), reading taken item 3 (10853-10855): "`!peek(A)` stays a compile
  error (his "I could understand !peek() being an error"). `when(!x, z)`, x a bare pattern, stays a compile error
  ... not-test is CLOSED by it (candidate (a))"; item 4 (10856-10857): "NOT taken: the general rule that a
  complement written anywhere a match is needed in place means "cannot match here" (it would reverse
  lone-complement-match); "its own question", not asked."
- V-C (subject line 60-61): `!^A` is the negative peek, i.e. today's `!peek(A)` made legal: REVERSES item 3's first
  error. The record says so of the same idea (11457-11459: "the REVERSE of the two forms as drop-not ruled them");
  the subject omits it.
- V-D (subject line 62-64): prefix `!A` on a pattern is `(?!A)`, so `!peek(A)` / `!^A`, `when(!x, z)`, a lone `!B`
  program, `digits SEQ not_seven`, `occurrences(not_seven)`, `/x${not_seven}y/` all become LEGAL. These are the
  ruled errors of drop-not item 3, lone-complement-match (2026-11-18, record 3624: "a lone complement stays a compile
  error in every mode") and complement-place's table (3571-3582). V-D IS drop-not item 4's untaken general rule
  (minus the complement object). The record lists part of this (11757-11758, "(2) `!A` where a pattern stands in
  place ... becomes the negative lookahead"); the subject's V-D line does not.
- Each is error -> answer, which core/principles/conservative-first allows ("A refused form can be allowed later
  without changing any existing answer", core.md 44), so nothing is a changed answer; but each is a RULED error,
  and the owner rules a reversal knowingly. Fix: each variant line carries its "reverses" list (the table below).

### RULING-3 (CONFIRMED by grep; severity design; effort small; blast radius: core/principles/match-and-filter, core/filters/kinds, lib/sets/anything) every variant empties the filter-only kind of a RULED principle; the subject does not name it
- core.md 81-82 core/principles/match-and-filter, ruled 2026-11-18: "There is rx that can match. There is rx that
  can filter. Neither is wholly a subset of the other". Record 3590 (complement-place): "THE MANAGER'S
  ILLUSTRATION (mine): filter-only: a complement". grep of core.md/library.md for `filter-only`: the complement is
  the ONLY member named (core.md 1398, 1413, 1429, 1705; library.md 392). The record's own manager line, 11446:
  "That kind exists almost only to give `!B` a home".
- All four variants remove the complement object (subject line 41; V-B/V-C/V-D keep line 1). The principle's
  filter side then has no stated member; the ruled sentence is either vacuous or false. Its ground (complement-place)
  is reversed while it is kept by silence. Likewise lib/sets/anything, provided by lone-complement-match "for the
  user to write beside" a complement (record 3624-3625): its use survives as `anything &! B`, its stated reason
  does not.
- Expected: the candidate says whether match-and-filter stays (the kind kept as the general form, its member
  `&!`'s right operand position or none), is restated, or is retired, as a named item the owner rules.

### RULING-4 (CONFIRMED; severity design; effort small; blast radius: V-A only) V-A keeps "Use NOT to get else behavior" only through the line the owner disliked; without it the ruling is reversed for some tests
- Ruled 2026-11-18 (record 3782-3787): "When: start with required then. Use NOT to get else behavior"; drop-not
  (10858) keeps it "under the spelling `!`". Under V-A (no bare `!`), the else-only form for a condition test is
  `when(^!(c), z)`, i.e. line 6, which he called "abuse" (record 11864); the one-entry form `(h ?:! <5)` and the
  hand rewrite of a record (`(a ?:! S) | (b ?:! T)`, record 11510) cover only some tests.
- For a joint entry over a set that is not a product, `((a, b): >= (5, 3))`, the record (11518-11521) shows the hand
  split fails (4 of 121 differ, evidence bang_record) and the exact negation `((a, b) ?:! >= (5, 3))` "inherit[s]"
  optional-entry-edges' compile error. So V-A WITHOUT line 6 leaves `when(not ((a,b): >= (5,3)), z)` unwritable:
  a reversal of the ruled else-only route for that test. V-B, V-C, V-D keep `!(cond)` and keep the ruling as
  drop-not states it.
- Collision pair: V-A keeps then-required/else-by-negation only by keeping line 6; the owner's dislike of line 6
  plus V-A is exactly the combination that reverses it. The subject should say so beside V-A.

### RULING-5 (CONFIRMED; severity doc; effort trivial; blast radius: subject line 42) "His later words: not ruled out forever" is the manager's reading, not his words; and RESERVED is not the build-later case
- His words (record 11845): "i've not written out ! forever." The reading (11849-11850): "READING TAKEN (told to
  him): "written out" is "ruled out" or "written off"". "so RESERVED, under construction" is "The manager's reading
  (told to him; nothing applied)" (11853-11855). Subject line 42 prints the reading as "His later words".
- core/principles/build-later (ruled 2026-11-18, core.md 99-101): "A meaning can be acknowledged and its build
  deferred". A bare `!` reserved with NO acknowledged meaning is not that case; and line 41 already says the errors
  "nam[e] the operator to use" (a conservative-first refusal). One form, two kinds of error. Fix: mark line 42 the
  manager's reading, quote "i've not written out ! forever", and pick one error kind (or say the reserved error
  names the operator to use, a reading).

### RULING-6 (CONFIRMED; severity doc; effort small; blast radius: Goals 1-4) the Goals section states non-rulings as the owner's goals; Goal 3 pre-decides a reversal of a ruled principle
- Header (line 9): "the owner's, in his words where quoted". Status per goal against the record:
  - Goal 1: quotes from a PROPOSAL entry (11799-11800, "NOT a ruling" by its class) and an OBSERVATION / STATEMENT OF
    INTENT (11845-11852, "NOT recorded as ruled"). Words verbatim; a goal by the manager's reading.
  - Goal 2: first quote is from backref-label (ruled 2026-11-18, record 3812), a ruling on backreferences; the
    principle the goal names is core/principles/regex-default (ruled 2026-11-17, core.md 21-23) with its own words
    ("it is in line with regex behavior ..."). Second quote: a CONCERN in a LEAN entry (11698, 11704-11706, "NOT a
    ruling"). Both verbatim. The closest RULED ground is unnamed: brace-counts (2026-11-25, record 11078-11080: "I
    reminded myself that this is pcre so I should try to stay familiar. I rule we should do this.").
  - Goal 3: a QUESTION inside an IDEA ("half baked"; 11421-11422: "NOT a ruling; drop-not stands as ruled"); the same
    message says "A:= !B is not disallowed" (11417). As a goal ("No object that cannot be used where its operand
    could") it is the contrary of RULED complement-place ("It stands alone. I think it's the use that is the
    problem", 3575) and match-and-filter (RULING-3): it states the reversal as a premise.
  - Goal 4: his stated GOAL (10728-10738: "Not asked as a ruling; recorded as his stated goal (a candidate
    principle)"), verbatim; the YES/NEVER/MAYBE clause is his STANDING REQUEST (10811-10815). Its own "Checkable"
    is not met by the subject: no candidate or variant line carries a category (the record gives them in the
    discussion entries; for `~`/`~!` only "the manager's estimate, nothing run", 11827-11828).
  - Goal 5: core/principles/conservative-first, ruled 2026-11-17 (core.md 41-45); restated faithfully.
- Fix: one status word per goal (ruled principle / stated goal / question / proposal / the manager's reading);
  Goal 3 marked the manager's reading of a question, naming the rulings it would reverse.

### RULING-7 (CONFIRMED; severity maintenance; effort small; blast radius: core/filters/negation/effects under V-A..V-D) capture-negated's scope is written over `NOT` and `!`; the candidate's new negative operators are not placed under it
- capture-negated (2026-11-23 OWNER RULING, record 9156, words 9163): "any effect macro cannot be under negation"; reading
  (b) (9174): "inside the operand of `NOT` (a condition, a peek) or of `!` (a set, a pattern), at any depth";
  printed error lines core.md 1457-1458 include `(h: !capture("h"))`.
- Under V-A there is no `!`; the negations are `:!`, `?:!`, `&!`, `^!`, `~!` (V-B/C/D add or keep `!`). The ruling
  KEEPS its meaning, but its stated scope no longer names the operators: `(h :! capture("h"))`, `A &! B` with a
  request in B, `~!A` with one in A, and `when`'s guard `^!T` (effect-in-guard, 9176-9179, 9183) each need the restated
  reading. A fold that only renames `!` could miss `&!`'s right operand (it is not "the operand of `!`").
- Fix: the candidate lists core/filters/negation/effects among what it re-spells, reading (b) over every negative
  operator of the chosen variant.

### RULING-8 (CONFIRMED; severity doc; effort trivial; blast radius: subject line 60) V-C's attribution and form are not the record's
- Subject line 60: "V-C (the manager's, earlier the same day, then set aside)". Record 11449-11450: "His sketch as
  one system: `!` negates a TEST": the manager's reading OF the owner's sketch line 1 ("you can use ! on conditions",
  11418-11419), told to him; its negative peek was `!peek(A)` (11457), `^` not yet proposed. "Set aside" is the
  manager's own act (the `ahead` idea 11559; the general form 11683-11686); no owner words set it aside. Fix:
  "(the manager's reading of his sketch, earlier the same day, as `!peek(A)`; the manager set it aside)".

## ANSWERS AND SUGGESTION INPUT

### The ruling table (rulings tagged with the brief's pieces; plus the untagged 11-16..11-18 rulings found by grep of inline "OWNER RULING")
Cells: REV = reverses; KEEP; RESP = re-spells (meaning kept, spelling moves); NT = not touched. "err->ok" marks a
reversal that only relaxes a ruled error (no answer changes; conservative-first allows it).

| record line, slug | content (one line) | V-A | V-B | V-C | V-D |
|---|---|---|---|---|---|
| 1790 not-is-complement (11-16) | `!` on a pattern or set is the complement (first half; its second half reversed by condition-not) | REV: no complement object | REV | REV | REV: `!` on a pattern becomes `(?!A)` (his "! takes an rx and gives the complement set" read otherwise) |
| 2053 condition-not (11-16) | `!`/NOT on a condition legal | RESP: `^!(c)`, `A &! c` (undefined, RULING-1), `(h ?:! S)` | KEEP `!(c)` | KEEP `!(c)` | KEEP `!(c)` |
| 2233 regex-settles item 2 (11-17) | `!B` holds when no path of B survives the stretch | RESP as `A &! B` | RESP | RESP | RESP |
| 2233 regex-settles item 3 | negative lookahead tries every inner path; outer condition never re-enters | KEEP (`^!`) | KEEP | KEEP (`!^`) | KEEP (`!A`) |
| 2233 absent-under-not (11-17) | NOT over an absent label HOLDS | KEEP (if `A &! c` reads per path; RULING-1) | KEEP | KEEP | KEEP |
| 2310 when-meaning (11-17) | `when` a library definition; NOT a negative lookahead | KEEP | KEEP | KEEP | KEEP |
| 3571 complement-place (11-18) | a complement may be bound, passed, combined; error at the USE | REV (`X := !B` an error) | REV | REV | REV (`X := !B` legal, meaning changed; its uses' errors err->ok) |
| 3571 principle match-and-filter (11-18, his words) | can-match and can-filter, neither a subset | NOT RESTATED: filter side emptied (RULING-3) | same | same | same |
| 3618 lone-complement-match (11-18) | lone complement an error in every mode; provide `anything` | REV object; `anything` KEEP (`anything &! B`) | same | same | REV err->ok: lone `!B` is a zero-width program |
| 3671 when-default; 3685 guarded form; 3762 single-arg error | missing else matches nothing; `(A then B) | (not A, C)`; `when(x)` an error | KEEP (body `T SEQ B | ^!T SEQ C`) | KEEP | KEEP (`!^T` guard) | KEEP (`!T` guard, one body: `!T` on a bare T is `(?!T)`) |
| 3700/3710 when-test, when-peek (11-18) | bare test consumes + warning; `peek()` makes a peek | KEEP; `peek` RESP `^A` | KEEP; RESP | KEEP; RESP | KEEP; `^A` or `peek(A)` |
| 3782 then-required, NOT for else (11-18) | else-only by negating the test | KEEP only via line 6 (RULING-4); REV without it for joint non-product tests | KEEP | KEEP | KEEP |
| 3287 hole-in-filter; core/filters/operand-context (11-17) | outward-looking piece in a filter operand an error | KEEP; `^A`/`^!A` refused as `&` operands by it | KEEP | KEEP | KEEP; `A & !B` becomes this error (record 11720-11722) |
| 7959/7985 wrapper-export, transform-export (11-22) | provided wrappers pass the argument's labels on | KEEP (`^A` passes; negatives none) | KEEP | KEEP | KEEP (`!!A` passes none, record 11726) |
| 8882 optional-label (11-23) | `?:` absent or in | KEEP; adds `:!`, `?:!` | KEEP (+ `:!`/`?:!` if wanted) | same | same |
| 9156 capture-negated (11-23) | no effect under negation | KEEP; scope to restate (RULING-7) | same | same | same |
| 10831 drop-not item 1 (11-25) | `NOT` leaves; `!` the only negation | REV (`!` leaves too) | KEEP for conditions only | KEEP for tests | KEEP, `!` widened |
| 10831 drop-not item 2 | negative peek `peek(!A)` | REV/RESP `^!A` | RESP `^!A` | RESP `!^A` | RESP `!A` |
| 10831 drop-not item 3 | `!peek(A)` an error; `when(!x, z)` bare an error | KEEP both errors (no `!`) | KEEP both | REV err->ok `!^A`; KEEP `when(!x,z)` error | REV err->ok both (RULING-2) |
| 10831 drop-not item 4 (NOT taken) | complement in place = "cannot match here" not adopted | NT | NT | NT | TAKEN in its general form (RULING-2) |
| 10831 drop-not readings (b) hole row, (d) no labels | `(?=${!A})` flips; `peek(!A)` passes none | REV (b): `${!A}` an error; (d) KEEP for `^!` | same | same | (b) answers kept: `(?=(?!A))` = `(?!A)`; (d) KEEP |
| 11066 brace-counts (11-25), regex-default ground | chose PCRE's syntax "to stay familiar" | NT (spirit: avoids PCRE's `(?!`) | NT | NT | KEEP-in-spirit: PCRE's `!` meaning for lookahead |
| 10728 / 10811 DFA goal + standing request (GOAL, not ruled) | all DFA unless specified; YES/NEVER/MAYBE per form | not stated per line (RULING-6) | same | same | same |
| core/conditions/form/optional-edges (OPEN, not a ruling) | `?:` on a joint/value left part an error for now | `?:!`, `:!` inherit it | same | same | same |
| 11799 "agree" on one-token `:!`, `?:!`, `&!` (AGREEMENT, not asked under a slug) | `(a: !<v)`, `A & !B` errors naming them | KEEP | KEEP | KEEP | KEEP |

Collision pairs checked (a rule kept by one variant, its ground reversed by it or another):
- match-and-filter KEPT by silence, complement-place REVERSED, in all four (RULING-3).
- then-required/else-by-negation KEPT by V-A only through line 6 (RULING-4).
- drop-not item 3's message ("naming `when(peek(!x), z)`") KEPT as an error by V-A/B/C, its named rewrite reversed by
  item 2's re-spelling: the message must name `^!x` (V-A/V-B) or `!^x` (V-C). Re-spell, no answer.
- condition-not's three-meanings distinction KEPT, while V-A's line 6 spells NOT c with the difference operator
  (RULING-1).
- lone-complement-match's `anything` KEPT, its stated reason (a complement to write beside) gone: harmless
  (`anything &! B` is the same program).
- V-D and not-is-complement's first half: V-D reverses his own stated reading ("! takes an rx and gives the
  complement set of strings", record 1795-1796) while keeping his 11-27 observation that the two meanings part.

### Leaning from this lens (the coordinator writes the suggestion; the owner rules)
On the ruling record alone, V-B reverses the fewest rulings: it reverses what EVERY variant reverses (the complement
object: not-is-complement first half, complement-place, lone-complement-match's object, drop-not's peek spelling) and
keeps condition-not, absent-under-not, then-required/else-by-negation and drop-not item 3 as ruled, with none of
RULING-1 (no `A &! c` needed) or RULING-4. V-D adds ruled-error relaxations (RULING-2) and reverses his own stated
reading of `!`; V-C reverses drop-not item 3's `!peek(A)`; V-A depends on the line he disliked. Whatever is chosen,
the statement should list match-and-filter's fate and capture-negated's restated scope.

## PROBED-AND-HELD

- QUOTES (sub-part a), word for word against the record, all HELD except line 42 (RULING-5):
  line 4 = 11865-11866; lines 11-12 = 11799-11800; lines 12-13 = 11846-11847; line 16 = 3812 (backref-label);
  lines 17-18 = 11698; line 19 = 11418; lines 21-22 = 10734 (his "Amended: " prefix dropped, no change of sense);
  line 51 = 11864; line 58 = 11864-11865; line 62 = 11711 (the manager's words, attributed so; case only);
  lines 71-73 = 11865-11868; line 74 = 11866. 13 quotes checked, 12 verbatim.
- Attributions HELD: line 3-4 (request is his, 11865); line 51 "DISLIKED by the owner" (11864, 11869-11870);
  V-B "the owner's" (a LEAN, "perhaps", 11869); V-D "the owner's question" (11701-11702) and "the manager judged"
  (11711). Line 39 "NOT answered" HELD (11851-11852, 11872-11873). Candidate lines 41-53 against the statement put
  (11833-11843): items 1-6 HELD in meaning; item 1's parenthesis is the manager's addition (RULING-5).
- "Today" lines 26-37 against core.md / library.md at the freeze, all HELD: 28-29 = core/filters/complement
  (1397-1399) and core/filters/kinds (1413-1414); 30-31 = core/filters/negation (1425) [core/conditions/two-valued
  1257 has "an absent label included", not "a negative lookahead"; a cite, not a drift]; 32-33 = drop-not reading
  items 2-3 (10849-10855), not yet folded (library.md 344 still prints `NOT peek(A)`); 34-35 =
  core/conditions/form/optional-entry (1186); 36 = lib/control/when (352) verbatim; 37 = lib/control/when-test (381).
- Goal 5 against core/principles/conservative-first (core.md 41-45): HELD.
- Rulings tagged with the brief's pieces (scr/rul.py over every `###` entry with a tags line and a RULING class):
  31 listed, 12 bearing on `!` / peek / when / entries placed in the table; the rest (bare-nested-scope,
  bound-condition, count-in-set, export-list, argument-default, label-parameter-default, label-forward,
  count-unspecified, shorthand-is-callers, capture-in-set, exact-count-unspecified, array-argument, map-creator,
  string-literals, zero-condition-binding) checked by heading/one-line content: NOT TOUCHED by any variant.
  The untagged 11-16..11-18 rulings (inline "OWNER RULING" grep, keyword-filtered, 30 headings) added to the table
  where they bear on `!`, `when`, peek, filters.
- core/operators/precedence is "reading 2026-11-19" (core.md 2124), not a ruling: placing `^`, `^!`, `~`, `~!`, `:!`,
  `?:!`, `&!` in it is no ruling collision (a gap for the fold only). core/conditions/form/optional-edges is OPEN.
- Own model scr/andbang_cond.py (RULING-1): 16105 WHOLE subjects; differ 5; control 6.

CRITIC COMPLETE ruling 2026-11-27T19:34Z
