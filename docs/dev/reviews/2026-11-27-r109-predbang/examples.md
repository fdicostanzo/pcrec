# CRITIC examples: predbang (r109)

## Findings

Own model: `model.py` (a backtracking matcher in PCRE order written from core.md's sentences; its READINGS string
lists R1..R10 with the sentence each rests on). CALIBRATED: drill1.py reproduces the printed ruled lines of
core/conditions/form/optional-entry ("The entry `?:`", "The plain entry", "Under `NOT`") and the P2 column of
core/conditions/two-valued's table, in all three modes, before any claim below.

### EXAMPLES-1 CONFIRMED (design): `:!` breaks the ruled record-is-product identity; a record of `:!` entries is "neither", not "not both"
Subject line 43-44 (`:!` present and outside) beside core/conditions/form ("a record is the product of its entries:
`(h: A, m: B)` = `((h, m): (A, B))`", ruled "absolutely") and core/conditions/two-valued ("A record ... is the `&` of
its entries"). Read as the `&` of its entries, `(a :! S, b :! T)` is "both present, a outside S AND b outside T";
read through record-is-product, `((a, b) :! (S, T))` is "both present and the pair outside S x T" = a outside S OR
b outside T. Run (drill2.py, a and b each absent or a digit, 121 cases, S = `<5`, T = `>=3`):
`(a :! S, b :! T)` vs `((a,b) :! (S,T))`: 50 of 121 differ, every one with both labels PRESENT (e.g. a=`0`, b=`0`);
CONTROL `(a: S, b: T)` vs `((a,b): (S,T))`: 0 of 121 (the ruled identity, so the comparison is not blind) and
`(a :! S)` vs `(a ?:! S)`: 11 of 121. Same for `?:!` (62 of 121 under optional-edges candidate (b)).
Modes on `/(?<a>\d)?,(?<b>\d)?/`: `(a :! <5, b :! >=3)` WHOLE `3,1` FAILS, `7,1` HOLDS / SEARCHED `3,4 7,1`
`7,1`@4 / FIND-ALL `3,4 7,1 ,4 6,` [`7,1`@4]; `!(a: <5, b: >=3)` WHOLE `3,1` HOLDS / SEARCHED `3,`@0 / FIND-ALL
[`3,`@0, `7,1`@4, `,4`@8, `6,`@11]. This is the owner's Q1 "perhaps its in the compound forms": the user who
moves the `!` of `!(a: S, b: T)` onto each colon gets De Morgan wrong (71 of 121 differ; 50 with both present).
Fix shape: the candidate states that record-is-product holds for `:` and `?:` only (or not at all for the marked
operators), and the negation of a record is written `!(...)` (V-B/V-D) or the entry-wise `|` (`(a ?:! S) | (b ?:!
T)`, 0 of 121 differ). Effort: one sentence. Blast radius: core/conditions/form, record-in-some.
Minimum witness length: subject length 3 (`3,1`).

### EXAMPLES-2 CONFIRMED (answer, V-A; doc, V-B/V-D): the equivalence `(a ?:! S)` = `!(a: S)` (subject line 66-67) and line 6's "`(h ?:! <5)` for one entry" fail at four RULED printed places; there the obvious V-A re-spelling moves answers
The equivalence holds for a plain label outside a group question. Where `?:` is a compile error for now
(core/conditions/form/optional-entry: "`?:` on a joint entry's left part, on a value left of `:`, and inside a group
question are compile errors for now"), `?:!` inherits the error, and `:!` is NOT the same test (drill4.py):
1. core/conditions/form/value-left, ruled, line "NOT holds on nothing" (`/(?<a>\d)/ & NOT (($a - 5): >= 0)`):
   printed WHOLE `7` FAILS, `3` HOLDS / SEARCHED `x3 7` `3`@1 / FIND-ALL `3 7 5 1` [`3`@0, `1`@6]; my model
   reproduces it. V-A `(($a - 5) ?:! >= 0)`: a compile error. V-A `(($a - 5) :! >= 0)`: WHOLE `3` FAILS / SEARCHED
   FAILS / FIND-ALL [] (answer moved).
2. core/labels/labels-vs-captures/array-vs-passes, ruled, "Past the end" (`/(?:(?<h>\d)?;)+/ & NOT (h[2]: "5")`):
   printed WHOLE `3;` HOLDS, `3;;` HOLDS, `3;5;` FAILS; model the same. `(h[2] :! "5")`: WHOLE `3;` FAILS, `3;;`
   FAILS / SEARCHED `x3;` FAILS / FIND-ALL [] (answer moved). `(h[2] ?:! "5")` keeps the answers, but whether `h[k]`
   left of `:` is a label (then `?:` is legal) or a value (then an error) is not stated: value-left's parse names
   "a bare name or a label path" as a label and "any other expression" a value; an index is neither listed.
3. array-vs-passes "An empty array", "A count of zero" and lib/counting/every-pass (`some(NOT (d: "7"))`,
   `count(NOT (d: "7"))`, `occurs.none(NOT (d: "7"))`): `(d ?:! "7")` is a compile error there; the
   answer-keeping V-A spelling is `(d :! "7")` (settings are never absent: printed "An empty array" WHOLE `,`
   FAILS, `7,` FAILS, `1,` HOLDS / SEARCHED `7, ,` FAILS / FIND-ALL `, 7, 1,` [`1,`@5] reproduced by both).
   So in a group question the crosswise rule flips: `NOT (d: S)` re-spells as `:!`, not `?:!`.
4. core/holes/bare-condition/zero-binding (`NOT (0: 5)`): `(0 ?:! 5)` draws `pcrec.default.unused`
   (optional-entry: "`0` is never absent, so `?:` on it draws the same warning"); `(0 :! 5)` is the clean one
   (WHOLE `5` FAILS, `7` HOLDS / SEARCHED `x5 7` `7`@3 / FIND-ALL `5 7 5` [`7`@2], both).
CONTROL: the same comparison shows `(h :! <5)` vs `(h ?:! <5)` differing on `/(?<h>\d)?x/` WHOLE `x` (drill1.py).
Consequence: under V-A (no bare `!`) items 1 and 2 have NO one-entry spelling; they fall to line 6's
`A &! (cond)` / `^!(cond)`, i.e. exactly the form the owner dislikes, plus EXAMPLES-3's open reading of `&!` on a
condition. Under V-B/V-D the fold is `NOT` -> `!` everywhere, mechanical. Effort: V-A needs a per-place rule table
in the fold; V-B/V-D a search-and-replace. Blast radius: 8 printed ruled lines (value-left 1, array-vs-passes 3,
every-pass 2, zero-binding 1, group-truth/some prose). Minimum witness length 1 (`3`).

### EXAMPLES-3 CONFIRMED (design, V-A): `A &! (cond)` (subject line 52) is not given by line 45's definition of `&!`; read literally it does not negate the condition
Line 45: "`A &! B`: the difference (A's stretch is not a B whole); the shorthand of `A & (0 :! B)`". With B a
condition: `(0 :! (h: <5))` puts a condition in a set position, which no piece defines; and "the stretch is not a
c whole", c judged as an operand in the stretch's own world (core/principles/operand-world: "There is no outside
subject"), sees no group setting h, so c fails there and the difference keeps every path. The intent (line 52) is
`A & NOT c`, which rests on a different sentence (core/filters/and: "A condition written in an `&` chain stands
after every pattern operand of that chain"). Run (drill5.py, A = `/(?<h>\d)?x/`):
reading N (line 52's intent): WHOLE `x` HOLDS, `3x` FAILS, `7x` HOLDS / SEARCHED `3x 7x` `x`@1 / FIND-ALL `3x 7x x`
[`x`@1, `7x`@3, `x`@6]; reading D (line 45 literally): WHOLE `3x` HOLDS / SEARCHED `3x`@0 / FIND-ALL [`3x`@0,
`7x`@3, `x`@6], identical to the CONTROL (A alone). So `&!` has two meanings by the kind of its right operand,
against the subject's own Goal 1 checkable ("one sentence gives its meaning with no reference to the kind of its
operand, or the sentence that does refer to it is stated as a rule"). This is the spelling V-A leans on for every
negated condition that has no one-entry form (EXAMPLES-2 items 1-2, `NOT some(c)` in lib/counting/some, the
record and joint negations). Fix shape: state the rule ("a condition operand of `&!` is negated where it stands,
as `&` places a condition") or refuse a condition right of `&!`. Effort: one sentence. Blast radius: V-A only
(V-B/V-D write `A & !c`). Minimum witness length 2 (`3x`).

### EXAMPLES-4 CONFIRMED (answer, all variants): the error that "names the operator to use" (line 41) points at `:!`, which changes the answer for a compound set; the answer-keeping re-spelling is `&!` inside the set
Today `(x: !<200 | >900)` is `((!<200) | >900)` (core/operators/precedence level 3: prefix `!` "on ONE atom"; "Inside
a call or a condition `&` and `|` bind tighter than `=` and `:`"). Line 41 makes `(a: !<v)` an error naming the
operator to use; the record's own run (11764) shows `:!` over the whole set parts. My run (drill6.py, x over 0..999
plus 4 non-numerals, 1004 values): today `(x: !<200 | >900)` 804 hold; `(x :! <200 | >900)` 705; differ on 99.
Today `(x: !<200 & >100)` 800; `(x :! <200 & >100)` 905; differ on 105. The re-spelling that keeps the answers in
every case is `&!` INSIDE the set: `(x: anything &! <200 | >900)` 804 (0 differ), `(x: >100 &! <200)` 800 (0 differ).
Every PRINTED form negates one atom, so no printed answer moves (HELD below); the risk is the user following the
message. Fix shape: the message for a prefix `!` in a set names `:!` only when the `!` covers the whole set, else
`&!` inside the set; or the fold states "`(x: !S op T)` is `(x: anything &! S op T)`". Effort: a message rule.
Blast radius: diagnostics; core/filters/complement's `!<200` line. Witness: a value set, length 3 (`950`).

### EXAMPLES-5 CONFIRMED (answer, all variants): `&!`'s precedence and associativity are not stated, and they decide answers
The candidate adds `&!` (and `:!`, `?:!`, `^`, `^!`, `~`, `~!`) with no row in core/operators/precedence (level 7
holds `&`: "binary, a chain; the left side decides"). `A &! B &! C` read left, `(A &! B) &! C`, is the ruled
fold target of `A & !B & !C` (the record's "`A & !B & !C` is `A &! (B | C)`"); read right, `A &! (B &! C)`, it is
`A & (C | !B)`. Run (drill6.py, A = `\d+`, B = `7\d*`, C = `\d*3`, every text over `1372` to length 5): WHOLE
differs on 341 of 1364; `73` left FAILS, right HOLDS / SEARCHED `73 12` left `12`@3, right `73`@0 / FIND-ALL
`7 73 12` left [`12`@5], right [`73`@2, `12`@5]. CONTROL-equal: `(A &! B) &! C` vs `A &! (B | C)` 0 of 1364 (so
the left reading is the one that keeps `neither`'s answers). Also unstated: `A &! B | C` (`|` looser, level 9) and
`A & B &! C`. Fix shape: `&!` at `&`'s level 7, the same chain, left to right; one row. Effort: one row. Blast
radius: core/operators/precedence; every printed `A & !B & !C` fold. Witness length 2 (`73`).

### EXAMPLES-6 CONFIRMED (answer, V-D): V-D does not say that line 1's errors stay; without them two ruled printed examples change answers silently, and `!contains(x)` keeps a legal spelling with a new meaning
V-D (subject line 62-64) is "prefix `!A` on a pattern IS PCRE's `(?!A)`"; unlike V-B it is not stated "as V-A", so
whether `(a: !<v)` and `A & !B` stay compile errors is not in the variant (the record's 11692 entry says `A & !B`
falls to core/filters/operand-context's error; a lookahead in a `label:` set is not named by that rule, which
speaks of "a filter operand", while the place table lists a `label:` set as its own place). Taken literally
(drill7.py; my model judges a set against the label's text whole, core/model/places row "a `label:` set"):
- core/conditions/match-so-far/in-loop, ruled, "`0` first in the pass", `((0: !contains("7")) SEQ /\d/ SEQ ";")+`:
  printed WHOLE `3;4;` HOLDS, `3;7;` HOLDS / SEARCHED `3;7;4;` `3;7;`@0 / FIND-ALL `3;7;4; 7;7; 1;2;` [`3;7;`@0,
  `4;`@4, `7;`@7, `7;`@9, `1;2;`@12] (my model reproduces it for `(0 :! contains("7"))`); V-D literal
  `(0: (?!contains("7")))`: WHOLE `3;4;` FAILS, `3;7;` FAILS / SEARCHED `3;`@0 / FIND-ALL [`3;`@0, `7;`@2, `4;`@4,
  `7;`@7, `7;`@9, `1;`@12, `2;`@14] (holds only where `0` is empty).
- lib/search/contains: "The negated test is `!contains(x)`". Today a lone complement in a sequence is an error;
  under V-D `/\d+/ SEQ !contains("7")` is legal and means "no 7 anywhere AHEAD, to the subject's end": WHOLE `17`
  HOLDS / SEARCHED `12 7` `7`@3 / FIND-ALL `12 7 34` [`7`@3, `34`@5]; CONTROL today's `/\d+/ & !contains("7")`
  (= `/\d+/ &! contains("7")`): WHOLE `17` FAILS / SEARCHED `12`@0 / FIND-ALL [`12`@0, `34`@5]. A relaxation, not
  a moved answer, but the library sentence then teaches the trap.
Fix shape: V-D states "a prefix `!` in a `label:` set or as an `&` operand is a compile error naming `:!` / `&!`"
(the record's agreed one-token reading), and lib/search/contains's sentence becomes "`X &! contains(x)`".
Effort: two sentences. Blast radius: V-D; core/filters/operand-context's wording (name the `label:` set place).
Witness length 4 (`3;4;`).

### EXAMPLES-7 CONFIRMED (design, V-A and V-B): line 5's `when` body writes `^!T`, so with a condition test it IS `^!(cond)`, the form the owner dislikes; V-B must keep it legal (two spellings of condition-not) or the ruled condition test breaks
Line 5: `when(T, B, C) := T SEQ B | ^!T SEQ C`. lib/control/when-test (ruled): "A condition or a `peek(A)` as the test
consumes nothing"; lib/control/when prints `when(NOT (h: <5), z)` as a legal else-only call. With T = `(h: <5)` the
body's guard is `^!(h: <5)`: the owner's "i don't like ^!(cond) because it looks like abuse" (record 11858). V-B
("line 6 leaves") does not say whether `^!` still takes a condition operand: if it does, condition-not has two
legal spellings (`!(c)` and `^!(c)`), against Goal 1's one-meaning-one-symbol aim in reverse (one meaning, two
symbols); if it does not, the body is ill-formed for every condition test. V-D's body would be `T SEQ B | !T SEQ
C` (one operator for both kinds); V-C's `!^T`. The lowerings agree with the printed lines wherever the guard is
well-formed (drill8.py, python `re`): printed `when(peek(/\d/), /\d\d/, else = /\w/)` WHOLE `12` HOLDS, `1`
FAILS, `x` HOLDS / SEARCHED `x123` `x`@0 / FIND-ALL `12 x 123 1x 7` [`12`@0, `x`@3, `12`@5, `x`@10], line 5's
`(?=\d)\d\d|(?!(?=\d))\w` identical; bare test `\d\d\d|(?!\d)\w` identical to line 5's; CONTROL `\d\d\d|\w`
differs (WHOLE `1` HOLDS). Fix shape: state in V-B that `^!X` takes any zero-width X (a condition included) and
that `!(c)` is the user-facing spelling, or write the body per kind (against one-body). Effort: one sentence.
Blast radius: lib/control/when, when-test. Witness length 1 (`1`).

### EXAMPLES-8 CONFIRMED (doc, all variants): the effect-under-negation rule names `NOT` and `!` only; the re-spelled ruled error lines escape it unless it names every negative mark
core/filters/negation/effects (ruled): "'Under negation': inside the operand of `NOT` (a condition, a peek) or of `!`
(a set, a pattern), at any depth"; its printed lines "Under `!`: a compile error (`/(?<h>\d)?x/ & (h:
!capture("h"))`)" and "In `when`'s test ... reaches the guard's `NOT peek(test)`". Re-spelled: `(h :! capture("h"))`,
`A &! capture("h")`-shaped forms and line 5's guard `^!T` contain no `!` operator and no `NOT`, so by the rule's
words they are not "under negation" and the two printed errors become legal (an effect under a never-holding
`:!`: `capture("h")` is `anything` with an effect, so `(h :! capture("h"))` never holds). Fix shape: the rule
reads "inside the operand of any negative mark (`!(..)`, `:!`, `?:!`, `&!`'s right side, `^!`, `~!`)". Effort:
one sentence. Blast radius: negation/effects, lib/structural/capture's pointer line, lib/control/when's first bullet.

### EXAMPLES-9 CONFIRMED (doc): census, Step 1. Spans holding `!` or `NOT` in core.md + library.md, and the spans with two meanings
census.py / classify.py (every backtick span and fenced line; output census.out, census_classes.out): 279 spans.
| class | spans (distinct) | examples |
|---|---|---|
| literal `!` in subject text or rx text (`3!`, `SEQ "!"`, `/${A}!/`, `x err!`) and prose mentions of the mark alone | 166 + 24 | core/labels/*, prose `!`/`NOT` |
| condition-not (`NOT c` on a condition, incl. in holes, group questions, `when`'s test) | 34 (24) | value-left, optional-entry, two-valued, array-vs-passes, pass-start-read, bare-condition/*, zero-binding, lib some/every-pass/when |
| complement on a set after a label (`(h: !<5)`, `(0: !contains("7"))`, `(d: !"7")`, `(x: !B)`) | 11 (8) | optional-entry, two-valued, defaults, in-loop, complement, negation, effects |
| complement on a pattern (`A & !B`, `!B & A`, `neither`, `!contains(x)`, `rx.any & !S`, `[!startsWith("#") & ..]`) | 20 (15) | complement, kinds, two-valued, flags/in-filter, any-case, contains, anything, assert, file-literals, rx/classes |
| negative peek `NOT peek(A)` (incl. the ruled `when` body) | 13 (5) | negation, effects, peek, when, when-test, when-test/not |
| inside rx text (`(?!A)`, `(?!)`, `/!foo/`) | 11 (8) | untouched by every variant |
Two meanings in one span: (1) `NOT x` (lib/control/when-test/not, OPEN): complement or negative peek, by the
documents' own statement; V-D closes it as (b), V-A/B/C as (a). (2) core/filters/negation's last bullet: "On a
condition the record also wrote `!`": `!` was both complement and condition-not; the documents print `NOT` to
separate them, so every `NOT` span is a V-B/V-D fold to `!`. (3) `!contains(x)`, called "the negated test" while it
is a complement (filter-only); see EXAMPLES-6 for V-D. (4) A prefix `!` before a compound set (EXAMPLES-4).
Stale: the 13 `NOT peek(..)` spans print a form the 2026-11-25 drop-not ruling replaced by `peek(!A)` (subject
line 32: "ruled and not folded"); every variant re-spells them again (`^!A`, V-C `!^A`, V-D `!A`). Effort: the
fold's site list. Blast radius: 78 non-literal spans in 29 sections.

## ANSWERS AND SUGGESTION INPUT

Mode definitions used (core/model/modes, quoted): "matched WHOLE (some surviving path spans the whole text), SEARCHED
(the first surviving path at the leftmost start) or FIND-ALL (PCRE2's global loop over it)"; FIND-ALL "after an
EMPTY report, a retry at the same place for the first surviving non-empty path starting there, and only then a
step of one character". The `occurrences` argument is run as its own FIND-ALL place (its body, lib/search/occurrences).

Readings I had to choose (each in model.py READINGS): R1 reset on entering an optional or a loop (one-rule); R4
record = `&` of entries (two-valued), joint = both present; R5 a condition in an `&` chain reads P's labels, `0` =
P's stretch; R6/R7 as the subject; a set is judged against the label's text whole (place table); `(?!X)` in a set
judged whole (V-D literal only, EXAMPLES-6); a tuple compares in dictionary order (core/values/comparisons).

**Q1, "what is the difference between (a:! 5) and !(a: 5)?"** They part exactly where a label (or the value left of
`:`) is ABSENT, and every compound place is a way of making it absent or of distributing the mark:
1. The absent label: on `/(?<h>\d)?x/`, `(h :! <5)` WHOLE `x` FAILS, `!(h: <5)` WHOLE `x` HOLDS; SEARCHED `7x x`
   both `7x`@0; FIND-ALL `7x 3x x` [`7x`@0] vs [`7x`@0, `x`@4, `x`@6]. `(a :! S)` = `!(a ?: S)`, `!(a: S)` =
   `(a ?:! S)` (drill1.py; 11 of 121 label states differ).
2. A loop's label (the last pass's own value): `/(?:(?<d>\d)?,)+/` on `7,,`: d is unset (PCRE's capture is `7`),
   so `(d :! "7")` FAILS and `!(d: "7")` HOLDS; SEARCHED `x7,, 1,` `1,`@5 vs `7,,`@1; FIND-ALL `7,, 1,7, ,` [`1,`@4]
   vs [`7,,`@0, `1,`@4, `,`@7, `,`@9]. A reader thinking in PCRE captures expects `!(d: "7")` to FAIL there: the
   trap is the label rule's, not `!`'s. Two depths (`/(?:(?:(?<h>\d)?;)+,)+/`): parting on `3;;,` and `3;,;,` alike.
3. An optional label inside an `occurrences` argument: the hit list itself moves: `occurrences(/(?<h>\d)?x/ & C)`
   on `x 3x 7x`: `(h :! <5)` hits [`7x`]; `!(h: <5)` hits [`x`, `x`, `7x`] (the second `x` is `3x` re-split, h
   dropped, regex's behaviour); min = 1 WHOLE `3x` FAILS vs HOLDS (drill3.py).
4. A record: `(a :! S, b :! T)` is "neither", `!(a: S, b: T)` "not both": 71 of 121 differ, 50 with both present
   (EXAMPLES-1); the entry-wise equivalent of `!(a: S, b: T)` is `(a ?:! S) | (b ?:! T)` (0 of 121).
5. A joint entry `((a, b) :! >= (5, 3))` vs `!((a, b): >= (5, 3))`: 21 of 121 differ (a part absent); the exact
   entry form of the latter, `((a, b) ?:! ..)`, is the open optional-entry-edges error (0 of 121 under its candidate (b)).
6. Group questions: NO difference: a setting is never absent, `some((d :! "7"))` = `some(!(d: "7"))` in all three
   modes (drill3.py), but `?:!` is an error there (EXAMPLES-2).
7. The empty set, `[]` and `/(?!)/` (same answers, drill3.py): `(h :! [])` = `(h: anything)` = "h present";
   `!(h: [])` and `(h ?:! [])` always hold (a `pcrec.test.always` warning); `(h ?: [])` = `(h ?:! anything)` =
   `!(h: anything)` = "h absent"; `(h :! anything)` never holds. Nothing new parts beyond the absent label.
Minimum witness length 1-4 (`x`, `7,,`, `3,1`, `x 3x 7x`).

**Q3, "would it make sense to replace :! et al if we went with !(cond)?"** By `!(..)` over a positive form:
- `?:!` on a plain label: exactly `!(a: S)`, every mode and place (drill1/3/9). Where `?:` is refused (value left,
  group question, joint, possibly an index) `!(..)` is the ONLY form that keeps the printed answers (EXAMPLES-2).
- `:!` on a plain label: exactly `!(a ?: S)` (a double negative for "present and outside"), or with no negation of a
  condition at all `(a: anything &! S)` (0 of 18 text-mode cells differ; CONTROL 8 of 18): `:!` and `?:!` are
  sugar for `:`/`?:` with `&!` inside the set, so once `&!` exists the entry marks add no expressive power. On a
  joint left part `:!` = `(a: anything, b: anything) & !((a,b): R)` (0 of 121).
- `&!`: `A &! B` = `A & !(0: B)` only BESIDE `&` (core/conditions/match-so-far: "joined by `&`, `0` is the left
  operand's match, COMPLETE; in a sequence or a hole it is the open prefix"); moved into a sequence the `!(0: B)`
  spelling reads the whole definition's prefix. A nullable A or a lookbehind in A changes nothing (A is an `&`
  operand in both spellings, core/filters/operand-context applies alike). `&!` also keeps the chain readable
  (`A &! B &! C`), given EXAMPLES-5's precedence row.
What a user loses with `!(cond)` only: `(h :! <5)` becomes `!(h ?: <5)`; gains: one negation for records, joints,
values, group questions and `0`. Mean the same? `?:!` yes (on a label); `:!` no (presence); `&!` yes beside `&`.

**Leaning from this lens: V-B, with `?:!` dropped and `:!` kept or dropped by taste.** Reasons, all from the
printed examples: (1) under V-B/V-D every `NOT` span folds to `!` mechanically and every printed answer holds; under
V-A eight ruled lines need a per-place rule and two of them have no one-entry spelling (EXAMPLES-2/3); (2) the
negation of a record has no entry-wise mechanical form, and the `:!`-per-entry move is a De Morgan trap
(EXAMPLES-1); (3) `?:!` is a strict synonym of `!(a: S)` that is legal in fewer places. V-D gives the same fold
plus `when(!x, z)`, but only with EXAMPLES-6's two sentences; V-C is V-B with `!^A` for `^!A` (no printed example
distinguishes them). Whatever the variant, EXAMPLES-4, -5 and -8 are needed.

## PROBED-AND-HELD

- Every printed RULED example holding `!`/`NOT`, re-spelled per variant, answers unchanged in WHOLE, SEARCHED and
  FIND-ALL against the printed line (drill1, drill4, drill7, drill8, drill9; my model reproduced each printed line
  first): optional-entry "Under `NOT`" (V-A `(h :! <5)`, V-B/D `!(h ?: <5)`); two-valued's table, both P columns
  (`(h ?:! <5)` / `!(h: <5)`, `(h :! <5)`, `P &! (P & (h: <5))`); defaults `(h = "x" :! <5)`; in-loop `(0 :!
  contains("7"))` and `(d :! "7")`; complement `/\d+/ &! /7\d*/`; kinds `/\d+/ &! /7\d*/ &! /8\d*/` (left chain;
  the binding `neither` itself is an error in every variant, a named complement lost, as the record says);
  pass-start-read `(h ?:! /\d/)` / `!(h: /\d/)`; bare-condition "Pass 2" (`?:!`; `:!` would kill the loop);
  effects "Beside a negation"; every-pass "Every setting" `occurs.none((d :! "7"))`; "A count of zero"; "An empty
  array"; zero-binding `(0 :! 5)`; value-left and "Past the end" under V-B/V-D; `when` printed lines under line 5's
  body. 19 printed lines x 3 modes, 0 answers moved under the answer-keeping spelling; the moving spellings are
  the findings. Witness lengths 1 to 6.
- `(h :! S)` = `(h: anything &! S)` and `(h ?:! S)` = `(h ?: anything &! S)`: 0 of 18 (text, mode) cells; CONTROL 8.
- De Morgan for a record: `!(a: S, b: T)` = `(a ?:! S) | (b ?:! T)`: 0 of 121; CONTROL 71 of 121.
- `(A &! B) &! C` = `A &! (B | C)`: 0 of 1364 (agrees with the evidence's 0 of 5461); CONTROL right reading 341.
- My model's four entries agree with evidence/bang_entry.out line for line (WHOLE, SEARCHED, FIND-ALL).
- Empty set spelled `[]` and `/(?!)/`: identical answers under all four entries and `!(..)` (10 forms, 3 modes).
- Group question: `some((d :! "7"))` = `some(!(d: "7"))` on 6 texts, 3 modes; CONTROL `(d: "7")` differs.
- Not checked: PCRE2 behaviour of `~A`/`~!A` with variable-width A (python `re` refuses; out of scope); `^A`'s
  label passing (not this lens).

CRITIC COMPLETE examples 2026-11-27T19:38Z
