# GENERAL findings — round predspec29 (r54)

## Findings

### GENERAL-1 — CONFIRMED (doc; effort trivial; blast: R.1.14 (1) only) — the ONE-SENTENCE general spelling of the inherit rule ("as text") is wrong for `U`

Location: §R.1.14 HOLE-READING (1), draft line 1926, the [REV 29] bracket: ""as text" now means the inserted literal
spelt `(?^ims-subset:...)` at the hole". This sentence is the draft's GENERAL FORM of flags-scope (one text spelling
for every inserted rx). It does not reset `U`: PCRE2's `(?^)` resets i m n s x xx, not `U` (nor `J`). The model knows
this (`predspec29_model.py` line 345: "U is reset by an outer `(?-U:...)`"; its `spell()` wraps `(?-U:(?^..:..))`),
the draft sentence does not.
Repro (libpcre2 10.46 through the evidence's own `pcre2h.py`; `GENERAL/u_caret.py`):
`(?U)x(?^:a+)` SEARCHED `xaaa` -> (0, 2) = `xa`@0 (U carried); `(?U)x(?-U:(?^:a+))` -> (0, 4) = `xaaa`@0 (the ruled
answer, A29, R.1.15's `/(?U)x${/a+/}/` SEARCHED `xaaa` `xaaa`@0). So the printed "as text" spelling gives the
REVERSED (rev 28.1) answer for `U`, the one flag the owner singled out ("excepting that U should also not be inherited").
Fix: "spelt `(?-U:(?^ims-subset:...))`" (or say the spelling resets every non-inherited flag, naming `U` beside `(?^)`).
Note for the general form (GENERAL-2): the spelling is the place where the inherit table becomes text; it must list
the not-inherited column, not lean on `(?^)`'s own list, which is PCRE's and differs from the ruled one.

### GENERAL-2 — CONFIRMED (design + doc; effort small; blast: T8, R.1.16 NUMBER DOMAIN, R.1.0 ZERO row, §7.1, §13 O66) — the "known to be nothing" WARNING family: five members, three answers, and T8's general sentence contradicts R.1.16's GAP

(a) SIBLINGS. Rev 29 adds a member to a family the draft already has: "a construct the compiler KNOWS yields the
never-matching rx (zero strings)". Members, with what each says about a warning:
1. COUNT hole, every copy removed (R.1.0 ZERO row, line 919; R.1.14 line 2054): "the can-never-match warning" (`match.never`).
2. Edge assertion that can never hold beside its neighbour (R.1.14 hole-reading (5), §7.1 `match.never` row, line 6730): `match.never`.
3. PATTERN hole of zero values `${[]}` = `(?!)` (R.1.0 line 919): no warning stated.
4. `x${anchored(/a/)}` (never matches): "no warning ... the never-match is §13 O66's" (line 6806; "a general 'can never match' warning: NOT ruled", line 4159).
5. NEW rev 29, plus-operands RULED "a warning if known": T8 (line 2561) "a WARNING only where the whole result is known nothing (`"a" + "b"`, `[a-z] + 1`; silent on `\w + 1`)".
6. NEW rev 29, number-edges RULED nothing: R.1.16 (line 2532) `${$y % 0}` and the lift `${\d % 0}` (ZERO values, `(?!)`) "also with no warning; a GAP, no new rule".
Members 5 and 6 DISAGREE inside rev 29 with no stated reason beyond the wording of `match.never`. T8's sentence is
written GENERALLY ("only where the whole result is known nothing"), and by its own words it covers `\d % 0`,
`5 % 0`, `\d - 10`, `3 - 10` (every result outside the domain, known at compile time). The model's RULE-AS-CODE
predicate for that sentence agrees with T8, not with R.1.16: `warns_arith` (model line 751) over `op_`/`arith`
(which returns None for `% 0` and negatives) FIRES on all four. Repro: `GENERAL/warn_edges.py` (the model's three
functions copied verbatim, no sabotage): `\d % 0` True, `5 % 0` True, `\d - 10` True, `3 - 10` True, `[a-z] + 1` True.
The model never calls it on a number-edge operand, so no check in PART NE or PL can tell the two sentences apart
(mutating `arith`'s `% 0` arm moves no PL check). One of T8 / R.1.16 is wrong as written; the owner's words
("anything else is nothing ... and a warning if known") speak of NON-DIGIT operands, so R.1.16 may stand on the
letter of the ruling, but then T8 must say "a non-numeral operand" not "the whole result".
Also: neither new warning (the plus-operands one; dollar-diagnostic's placeholder `pcrec.dollar.filter`, line 2661)
has a row in §7.1's THE WARNING TABLE, which claims "every warning the draft defines, ONE stable name each" (line
6715); the plus-operands warning has no name at all (the record leaves name/wording to the manager; the table row
can say "name: the manager's call").
(b) GENERAL FORM: ONE warning, `match.never`, defined by its CAUSE-FREE trigger: "a pattern position whose value is
known at compile time to be the never-matching rx (zero strings), whatever made it so: every copy or combination
removed, an edge assertion that cannot hold, a lift leaving zero values, an operand or result outside the number
domain". DELETES: T8's separate "a warning if known" clause and the manager's reading 17's "plain warning at the
operator"; R.1.16's `% 0` GAP and §R.8 GAPS' first item; the R.1.0 ZERO PATTERN/COUNT split on warnings (3 vs 1);
`match.never`'s two enumerated causes. Rulings it must not reverse: number-edges "no compile error of its own for a
written `% 0`" (a warning is not an error: holds); anchored-in-hole "NO compile error specific to `anchored`" (holds);
polarity-rule "Warnings are errors given some strictness setting" (unchanged mechanism). It does NOT reverse any
printed answer (warnings move no answer). It DOES go beyond what is ruled for member 4 (§13 O66 is "not ruled"), so
it is a proposal, not a fold. UNLOCKS: one §7.1 row for every "nothing" source the future adds (other number bases,
ideas items 34/35's restricted parameters "nothing left = no match", `when` with no branch); a strictness setting
that turns every dead position into an error by one name. TRIGGER: the manager's pending call naming the
plus-operands warning (owed now, since §7.1 must list it) — name it `match.never` with the cause-free trigger, or
state why `% 0` differs; or the next §13 O66 discussion.

### GENERAL-3 — CONFIRMED by the record's text (design; effort small; blast: R.1.13 T-a (ii), R.1.0 PATTERN HOLE / BINDING rows, §R.8 GAPS) — the HOLE and the SEQUENCE OPERAND, RULED "ONE reading", EXPORT differently, and only by an unruled draft reading

(a) SIBLINGS. "How one binding's labels reach the binding that USES it" has three join forms in the draft: a SEQUENCE
operand, a PART LABEL, a PATTERN HOLE. R.1.14 hole-reading (3) (line 1928, RULED "hole-reading: agree"): "the
sequence operator and a hole are ONE reading". Rev 29's T-a (ii) (line 1751-1757) finds they part on EXPORT:
`isodate` as an unlabelled SEQ part of binding B exports nothing bare (export-rule (3): "the public labels WRITTEN in
its own literals"), while `/${isodate}/` in B's literal exports `year` — by "THE DRAFT'S READING that they then
count as the binding's own". Reported as a "surprise", "no change proposed", listed in §R.8 GAPS. That reading is the
ONLY source of the asymmetry; no ruling states it. Against the record:
- R.1.0 PATTERN HOLE row (line 896) cites the ruled lean "only X's public (exported) names flow into the outer
  PATTERN" — VISIBILITY inside B (export-rule (2): "everything written or USED there"), not EXPORT from B.
- export-rule (3), ruled verbatim (COND-FAMILY "2026-11-18 OWNER RULING — export-rule"): "the public labels WRITTEN
  in its own literals, and its public part labels". `year` is written in `isodate`'s literal, not B's.
- The export-scope discussion just before it (COND-FAMILY 2026-11-18, "continuing the export-scope discussion"):
  pass-through of exports through a second binding, HIS WORDS "Agree. Not exported by default"; and the ruling's own
  "WHAT THIS CLOSES": "pass-through ... is answered by statement 3: the part label is the re-export". The hole
  reading makes a hole an UNLABELLED re-export, the default he declined.
So the draft's reading contradicts a ruled equivalence (hole = SEQ) and the record's pass-through answer, for no
stated reason. Repro (hand, by the rules as quoted; the model's `visible()` is RULE-AS-CODE of the draft's reading,
sabotage t16 tests only the part-label side): B1 := `isodate SEQ "!"`, B2 := `/${isodate}!/`; caller `B1 & (year:
>2000)`: compile error (free-name / not visible); `B2 & (year: >2000)`: compiles under the draft's reading. Same
text set, same match, different caller namespace.
(b) GENERAL FORM: "EXPORT is by WRITING or by PART LABEL only; HOW a use is joined (sequence, hole, `&` operand,
loop body) never changes what a binding exports". Under it a hole-inserted pattern's public labels are visible
inside the using binding (as now) and leave it only through a part label (`[d = isodate]` written as a SEQ part, or
a part label around the hole's content if the spelling allows), exactly as for a SEQ part. DELETES: THE DRAFT'S
READING "count as the binding's own"; T-a's surprise (ii) and its §R.8 GAPS line; one column distinction in R.1.0.
Reverses NO printed ruled example (export-rule's worked `date := [y = year] SEQ "-" SEQ [m = month]` uses part
labels; the T-a WHOLE/SEARCHED/FIND-ALL answers inside the binding are unchanged; only the caller's namespace of the
hole form shrinks). UNLOCKS: the hole/SEQ equivalence extends to the whole place table (one row could be stated for
"a part joined in place"), and the owner's "use labels as defined and see if there is a problem" gets one rule to
watch, not two. TRIGGER: now — it is an unruled draft reading producing a reported surprise against a ruling; put
it to the owner as a confirm ("a hole re-exports, or only a part label does?") rather than leave it a GAP.

### GENERAL-4 — CONFIRMED gap (design; effort small; blast: R.1.14 (3), R.1.15 flags paragraph, R.1.0 SEQUENCE OPERAND row) — the INHERIT family has seven members stated and one UNSTATED: flags across the SEQUENCE operator

(a) SIBLINGS ("which flags does an rx start with, by where it stands"), each in rev 29's text:
1. a PATTERN HOLE: inherits `i m s`, not `U x xx n` (flags-scope RULED; R.1.15, line ~2196; R.1.14 (1) line 1926).
2. a binding in a hole, at any depth: inherits transitively (reading 5/7, SUPPORTED; R.1.15).
3. both sides of an `&`, a condition's set, a filter-role argument INSIDE a hole: REACH (THE DRAFT'S READING; flags-in-filter, a confirm).
4. an `&` at PROGRAM level: each side its own (R.1.15 "has no surrounding rx").
5. a value computed from a binding ALONE (`enumerate(A)`): A's own flags (reading 6, SUPPORTED).
6. the branch carry of an unscoped `(?i)` into a later alternative holding a hole: stands (R.1.15).
7. what an inserted rx's own unscoped flag does OUTSIDE it: nothing (`(?:X)` scopes it; hole-reading (1)).
8. a SEQUENCE OPERAND (`/(?i)x/ SEQ /ab/`, or `A SEQ B` with A ending in an unscoped flag): NOT STATED anywhere
   (a scan of every line holding `SEQ`/`sequence` for "flag" or `(?i` finds only §R.7's sabotage list, line 3719).
   R.1.0's SEQUENCE OPERAND row says "regex model: regex concatenation", and the TEXT concatenation carries the
   left literal's unscoped `(?i)` into the right; hole-flags RULED "each regex literal has its own flags", and
   hole-reading (3) RULED "the sequence operator and a hole are ONE reading" (a hole is `(?:X)`, which stops the
   carry). Repro (libpcre2 10.46 via `pcre2h.py`, `GENERAL/seqflags.py`): text concatenation `(?i)xab` vs each
   literal its own `(?:(?i)x)(?:ab)`: 6 / 78 / 78 of 1,555 texts (`xXaAbB`, length <= 4; min witness length 3):
   WHOLE `XAB` HOLDS / FAILS; SEARCHED `z XAB` `XAB`@2 / FAILS; FIND-ALL `xab XAb` [`xab`@0, `XAb`@4] / [`xab`@0].
   So two ruled sentences pick opposite answers for member 8 and the draft names neither.
(b) GENERAL FORM (it is the owner's own recollection, "rx inherits the flags of the surrounding rx", COND-FAMILY
2026-11-19 "on flags-in-filter"): "every rx STARTS with the inherited flags (`i m s`) in force at the point that
SURROUNDS it, and its own written flags win; flags never pass SIDEWAYS between parts (a sequence operand's, an `&`
operand's, a hole's unscoped flag ends at its part's end); a place with no surrounding rx (the program level, a value
computed from a binding alone) inherits nothing". Members 1-7 are instances; member 8 follows (each SEQ operand its
own, the `(?:...)` spelling, consistent with hole-reading (3)); the branch carry (6) is INSIDE one literal and so is
PCRE's, not a sideways crossing. DELETES: the per-site sentences of R.1.15's flags-in-filter paragraph (an `&`, a
condition's set, a filter-role argument each argued separately), the "has no surrounding rx" special case for a
program-level `&`, reading 6's separate statement, and (with GENERAL-1) the "as text" spelling becomes ONE wrapper
`(?-U:(?^<inherited>:X))` per part. Reverses no ruled printed example (flags-scope's runs, A29; REACH's runs are the
draft's reading, not ruled). UNLOCKS: flags-in-filter stops being a separate confirm (it is a consequence); `any_case
:= /(?i:${rx})/` (T-c) closes for every argument not writing `(?-i)`, as that is the general rule's "own written
flags win"; the unclassified flags of GENERAL-5 get a column by the same sentence. TRIGGER: the pending
flags-in-filter confirm — ask it as this one sentence (with member 8's example) rather than per site.

### GENERAL-5 — SUSPECTED (maintenance; effort trivial; blast: R.1.15 inherit table only; answer-free today) — the ruled inherit table is a LIST, and PCRE2 inline flags pcrec accepts sit in neither column

flags-scope RULED a split table: inherit `i m s`, not `U x xx n` (`J` closed by same-name-count). pcrec accepts more
inline flags than these: `(?r)` and `(?a)`, `(?aD)`, `(?aS)`, `(?aW)`, `(?aP)`, `(?aT)` (docs/pcre2_compliance.md
annotations "`(?a)` (2026-09-28)" and "`(?r)` (2026-09-28)": accepted, measured no-ops under `byte`; `(?r)` refused
under `-e utf8`, K70). The draft names none of them (0 hits for `(?r)` / `(?a` in rev 29). Today no answer can differ
(both are no-ops where accepted), hence SUSPECTED, not CONFIRMED; it becomes an answer question the day UTF/UCP
folding lands. The table carries no PRINCIPLE that would place a new flag, and the owner's ruling gives one only by
example ("excepting that U ..."; his observation "one could make a case that only i should be inherited").
GENERAL FORM (a reading that fits every ruled cell; not his words): "INHERITED: flags that change WHICH TEXTS an atom
matches (`i` case, `m` line anchors, `s` dot); OWN: flags that change how the literal is READ or its STRUCTURE or
PRIORITY (`x`, `xx` the parse, `n` and `J` the groups, `U` only the order: R.1.15's `U` runs part SEARCHED, never
WHOLE)". It places `r` (a restriction of `i`'s fold) and the `a*` flags (what `\d \w \s` and POSIX classes match)
in the inherited column. DELETES nothing today; it turns a list into a rule. Reverses no ruled cell (check: `i m s`
change the matched set at one position; `U` changes only priority; `x xx n J` change the parse or groups). UNLOCKS:
a new PCRE2 flag needs no ruling; the "only `i`" narrowing he floated can be asked as one principle question.
TRIGGER: UCP / UTF case-fold work making `(?r)` or `(?a*)` real (K70's follow-up), or his narrowing observation
coming back as a question. If the principle is not wanted, the table should at least say "flags not listed:
THE DRAFT'S READING not inherited" (or inherited) so the gap is visible.

### GENERAL-6 — CONFIRMED (answer + doc; effort small; blast: §5.5 RULE/STATUS, §R.8 class-index row, T8 "enumerate's order", A24) — the ORDER family now has TWO orders for one class, and **class-index**'s row says "no MATCH answer differs" when one does

(a) SIBLINGS ("in what order a construct's strings are tried"): enumerate = PCRE priority order (§5.5, line 6430;
A24); a lift = "applied per enumerated string, in enumerate's order" (T8, line 2561; R.1.16; A24 "the lifted order
is enumerate's (lift-order)"); a class's members in a LIFT: longest result first (class-order RULED, §5.5 STATUS);
a class's members in enumerate's ARRAY: codepoint (THE DRAFT'S READING, **class-index**, line 3365; L26); user
alternations and arrays: their own order; `padded`: any-length branch first (padded-order RULED); product: first
hole slowest. Rev 29 leaves "enumerate's order" meaning two things for one class: T8 and A24 still say a lift is
"in enumerate's order", while §5.5 now says enumerate's array is codepoint and a class lift is longest-first. The
two meet in `enumerate(/\d/) + 1` (array-lift of an array whose order is codepoint) against `\d + 1` (a class
position), and in `join(enumerate(/\d/)) + 1`: §5.5's stated purpose "re-joining preserves which match is reported
(hence a built-in)" no longer holds once the re-joined result is lifted.
Repro (python `re`, the two orders as the draft states them; `GENERAL/lift.py`): array order `1|2|...|9|10` vs
class order `10|1|...|9`: 0 / 250 / 570 of 3,906 texts (`0123x`, length <= 5; min witness 2: SEARCHED `x10` `1`@1
vs `10`@1) — the very count §5.5 prints for the replaced codepoint lean. So **class-index**'s "no MATCH answer
differs (equal lengths), only a reported `.index`" (line 3365) is true for `enumerate(/[-\/.]/)` alone and false
for any lift or `each` over an enumerated class whose results differ in length; the row's "DECIDES" column
understates what the owner would rule.
(b) GENERAL FORM: "a CLASS has no member order (class-order); wherever an order of a class's members becomes
observable — a lift's results, enumerate's array, an `each` over it — it is the SAME order: longer RESULT first,
ties (equal length, never both matchable at one position: reading 8) by codepoint". For a bare `enumerate(/\d/)`
every member has length 1, so the array is codepoint exactly as today (L26's SAME pair untouched, E-SEP's comment
untouched); a lift over it then re-sorts by result length as the class lift does, and §5.5's re-join promise holds
again. DELETES: the "for the ARRAY interface only" carve-out in §5.5, half of **class-index** (only the tie-break
remains, and it is answer-free), and T8/A24's now-ambiguous "enumerate's order" (it becomes true again). Reverses no
ruled example: class-order's ruled words are "where a lift gives results of different lengths from ONE CLASS
POSITION, the LONGER is tried first"; an enumerated class is still that one position's members. It does NOT touch
user-written alternations/arrays (`(0|1|...|9) + 1` keeps `1` first, as ruled). UNLOCKS: one order function for
the enumerator, the lifter and `each`; class-positions (C1 vs C2) becomes the only open order question. TRIGGER:
asking **class-index** — ask it with `enumerate(/\d/) + 1` as the witness, since that is where it decides a MATCH.

### GENERAL-7 — CONFIRMED (doc/design; effort trivial; blast: §R.2 dollar-condition row, §0.1 L28, R.1.15 (12)) — the FORM-keyed warning's HINT is keyed on no PLACE; its sibling `anchor.whole` is keyed on form AND place, and in a VALUE HOLE the hint changes the answer

(a) SIBLINGS: form-keyed (structural) warnings already in the draft: `anchor.whole` (§7.1: "an explicit anchor that
provably sits at the EDGE of a FILTER ROLE's stretch"; L7, L11, L41, L69 — fires where right too, L69 SAME),
`label.numbered` (a label named by number), `compare.looped` (withdrawn). Each is keyed on a FORM AT A PLACE where
the look-alike it suggests is a drop-in. Rev 29's dollar warning (§R.2, line 2661) is keyed on the form `$x & S`
"wherever the form is written", "pointing at `(x: S)`", and the draft extends it: "a value hole `${$y & <5}` is the
same form and draws it". The harmlessness check (reading 16; PART DD line 125) is run only for the PROGRAM-level `&`
operand (`/(?<x>\d+)/ & ($x & <5)`, 0 / 0 / 0). In a value hole — where `${$y & <5}` is R.1.15 (12)'s own
printed idiom ("the read or NOTHING") — following the hint changes the answer.
Repro (libpcre2 10.46 via `pcre2h.py`, callouts as the model spells a test; `GENERAL/hint.py`):
`/(?<y>\d+)-${$y & <5}/` vs the hint applied `/(?<y>\d+)-${(y: <5)}/` (a condition at that point, zero width,
condition-in-sequence): 2 / 132 / 132 of 364 texts (`37-`, length <= 5; min witness 3): WHOLE `3-3` HOLDS / FAILS;
SEARCHED `x 7-7 3-3` `3-3`@6 / `3-`@6; FIND-ALL `3-3 3- 7-7` [`3-3`@0] / [`3-`@0, `3-`@4]. The model's
`warns()` (line 616) is a regex on the text (`\$\w+\s*&`), so no PART DD check can see a place.
(b) GENERAL FORM: every structural warning is a row (FORM, PLACES where its look-alike is a drop-in, LOOK-ALIKE);
§0.1's WARNING-class L-rows already pair a form with its look-alike, so the row can live there and §7.1 cite it.
For the dollar row: form `$x & S` everywhere (as RULED: "the form $x & .. should just get a warning" — not
narrowed), the `(x: S)` HINT only at an `&`-operand place; in a hole the hint is omitted (or says "the read, or
nothing, is intended here"). DELETES: the per-warning prose on where each fires; reading 16's single-place support
standing in for all places. Reverses nothing ruled (the warning still fires on the form; only the hint's text is
place-keyed, the manager's call by the record: "its wording ... the manager's call"). UNLOCKS: a uniform "did you
mean" column for the L-table's WARNING rows; the owner's "Warnings should be structural" stated once. TRIGGER: the
manager's pending call on the warning's NAME and WORDING (owed; COND-FAMILY dollar-diagnostic reading (c)).

## PROBED-AND-HELD


- "NOTHING" family, ANSWERS (not warnings): number-domain (a non-numeral read), number-edges (`% 0`, a negative
  result), plus-operands (a non-numeral operand, per member for `\w + 1` / `["7","x","41"] + 1`), unset-in-hole,
  the ZERO-values pattern hole: all ONE meaning, the never-matching rx (the position fails), member by member for a
  set operand. HELD; the record already split "matches nothing" (`when`'s empty string) from "the never-matching rx"
  (COND-FAMILY unset-in-hole entry; rev 28.1 call 5), and the owner's "nothing" in number-edges / plus-operands was
  asked with the never-matching meaning. Checked by reading the model's `arith`/`op_` (and `GENERAL/warn_edges.py`,
  6 operand cases) against R.1.16 and T8. Only the WARNING half disagrees (GENERAL-2).
- Backreference vs label across a hole (same-name-count): `\k<h>` scoped (the inserted group never counts), `$h` the
  last mention including the inserted pattern's public `h`. HELD as a family with a stated reason: `\k` is PCRE's
  capture side (backref-label RULED), `$` the language's label (export-rule (2)); inward, neither crosses (free-name
  makes a `\k<h>` or `$h` inside X to a name X lacks a compile error); across SEQ a `\k` can never name another part
  (free-name), so SEQ and hole agree for `\k`. Not run (no answer differs between members); checked against R.1.13
  REFERENCES (3), R.1.0's PATTERN HOLE / SEQUENCE OPERAND rows and the record's same-name-count correction entry.
- padded-order vs class-order's "nothing else is re-sorted": the any-length-first body re-sorts a user alternation
  (`1|0123`, SEARCHED `x0123` `0123`@1 against per-member `01`@1, the draft's own run). HELD: the disagreement has a
  stated reason in the RULING (`padded` is a plain macro; the difference is "the body's stated behaviour, not an
  error", COND-FAMILY "OWNER RULING — padded-order"). Not re-argued.
- class-order nesting `(1|9) + \d` (alternation order kept, class results longest within each choice) agrees with
  enumerate's PCRE priority order at the alternation and longest-first at the class: one order rule at two kinds of
  choice point. HELD (model PART CO line 97-99: nested vs across 0 / 750 / 1,404 of 3,906, length <= 5, min witness 3).
- flags-scope's ruled cells against the "set vs parse/priority" principle of GENERAL-5: `i m s` each change the set
  at one position; `U` changes only priority (R.1.15's `U` runs: WHOLE `xaaa` HOLDS both ways, SEARCHED parts);
  `x xx n J` change the parse or the groups. HELD for every ruled cell (7 flags + `J`), by the draft's own runs.
- The model's flags spelling (`spell()`, line 342) resets `U` correctly (`(?-U:(?^..:..))`); verified independently
  in libpcre2 (`GENERAL/u_caret.py`, 4 patterns, witness length 4). The defect is only the draft's sentence (GENERAL-1).
- T-a surprise (i) (an unlabelled use first makes a bare `year` read `end_date`'s): HELD, it is export-rule (2)'s
  ruled "last mention", no family member disagrees.

CRITIC COMPLETE
