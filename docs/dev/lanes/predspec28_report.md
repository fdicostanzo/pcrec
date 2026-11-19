# Lane predspec28 — report (2026-11-18, opus; DESIGN ONLY)

Deliverables: `docs/design/predicates_draft.md` REVISION 28 (head line "rev 28: the owner's 2026-11-18 evening rulings
folded (nine rulings, and array-in-hole by the rulings file); NOT STABLE pending the owner's answers"); evidence
`docs/dev/lanes/predspec28_evidence/` (model, its output, the sabotage output, CLAUDE.md). Branch lane/predspec28, cut
from lane/pred-rev28 @ c32e93bc6; not merged, not pushed. Draft size (`wc -lc docs/design/predicates_draft.md`):
9,523 lines / 1,221,021 bytes before, 9,755 / 1,273,900 after. A FOLD only: no restructuring (reviews r47 E1 and r48
O stay the next full revision). Nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/`, `scripts/` was touched; no
`make` other than `make -s test-plan-lint` (PASS); no box job.

## STATE AT HANDOFF

STATE: complete.
OWED: none

- PREMISE TEST: `timeout 600 python3 -I docs/dev/lanes/predspec271_evidence/predspec271_model.py` re-ran
  BYTE-IDENTICAL to the committed `predspec271_model.out` (diff empty). STOP RULE: nothing stopped; no run or record
  line contradicted the brief. One reading the brief asked to test is NOT SUPPORTED as the record grounds it (number-
  domain m1: numeral-width is NOT moot; see MANAGER READINGS TESTED); it is reported and the question kept, not
  stopped on, because no RULING is contradicted.
- RULINGS FILE `docs/dev/lanes/predspec28_rulings.md`: re-read at each checkpoint; LAST ENTRY APPLIED: R1 (array-in-hole,
  a tenth ruling: "${@y} stays as a future direction item and is not built or defined now"), applied in R.1.15 (13),
  T21, §R.8 (RULED list and the row), §R.11 row 148, the changelog. Its readings: m1 NOT SUPPORTED, m2 SUPPORTED (below).
- Evidence: CHECKS 19 of 19 OK (6 are the helper's selfchecks); s1-s14 each alone CAUGHT; all at once 6 of 19.

## RULINGS FOLDED

Each with his words (COND-FAMILY, verbatim) and where it is applied. §R.11 rows 125-148 (one per folded entry: 23
record entries plus the rulings-file R1).

| slug | his words | applied in |
|---|---|---|
| hole-reads-capture | "what i want is that $y works like label. however, there is a way to get the pcre capture value" | R.1.15 (11); R.1.16 A23; §R.8 (RULED list, row marked); §0.1 L33; §5.4 `${ }` row; the seven live uses |
| number-domain | "number-domain: canonical" | R.1.16 THE NUMBER DOMAIN (now RULED; the width half NOT ruled); R.1.15 (2); §2.4; §13 O27 |
| padded-width | "padded-width: minimum" (ground: "i meant the length = 4 to speak to how far out the 0 would go") | §2.7 THE WIDTH FORM (new paragraph); R.1.16 A20; spellings 31 |
| hole-flags | "hole-flags: i have heard you say both that the ${} gets the flags in force and also that a hole has its own flags. i agree with your interpretation of flags and holes. a hole takes the flags in force at the hole. each regex literal has its own flags. do the flags propagate down though? /(?i)${/blah/}/ is blah case insensitive?" | R.1.15 header; T12; §R.8 |
| flags-propagate | "flags-propagate: yes" | NO INHERITED FLAGS REVERSED: §11, R.1.14 HOLE-READING (1), R.1.15, §R.6, §13 O32 and O70, §2.7 `any_case` row, §0.1 L32, R.1.16 A18, §R.9 |
| unset-in-hole | "unset-in-hole: i meant what you describe "no string" as. its a regex that matches nothing. that would be a good constant to provide" (RULED on the manager's reading, ALGEBRA; the constant an IDEA) | R.1.15 (3), (5); T12, T20; §5.4 `$` row; spellings 32 |
| construction-line | "construction-line: enumerate" | R.1.16 T4, T5 (THE LINE), T8, T9, T13 (part (b) untouched), the composition; R.1.15 (9); R.1.14's AL mark; §5.5; A24 |
| value-test | "value-test: that "if" statement was purely illustrative. i was thinking at the time that $y was NOT a regex and so when() wouldn't work on it. the idea was to query how far runtime manipulation could go. we have since ruled that $y is a regex of a single enumeration at runtime, so the when forms would work on it." | R.1.15 (12); T11; A12, A22 |
| same-name-twice | "same-name-twice: i agree with your lean." (the lean as put: "the error at the backreference, with `(?J)` as the opt-in to PCRE's first-group reading") | R.1.15 (8); T20; A10, A25; R.1.7 (b) and REF4 marks; §R.6 |
| array-in-hole (rulings file R1) | "${@y} stays as a future direction item and is not built or defined now" | R.1.15 (13); T21; §R.8 |
| MANAGER'S CALLS (marked as his, not the owner's) | under-construction-class: its own class; dollar-warning: the dedicated warning WITHDRAWN; L28 DIFFERENT, BY DESIGN; lift-order: enumerate's order, first operand slowest | T4; §R.2; §0.1 L28; A21; §5.5; §R.8 |

NOT ruled and NOT applied as rules (kept as the record has them): the label-only group `(?<:x>...)` (his PROPOSAL;
mentioned in R.1.15 (11) as a proposal only; spellings 30); `padded`'s parameter names and the keyword rule
(spellings 31); the never-matching constant (IDEA; spellings 32, with the naming trap); the bounds on a padded result
(OBSERVATIONS); numeral-width (narrowed, kept); construction-line (b); "arrays are written with `|` only"; every
question open since rev 26.1; the spellings review. WITHDRAWN readings printed as withdrawn (§R.9): "the record lacks
a per-group labelled-not-returned form"; hole-flags' split "plain text with no flags of its own vs pattern text"; the
manager's leaning "exact" for padded-width; the call "the warning stays".

## MANAGER READINGS TESTED

S = SUPPORTED, NS = NOT SUPPORTED, U = UNTESTABLE. "PART x" = a line of `predspec28_model.out`.

| entry | reading | verdict | the run or the record line |
|---|---|---|---|
| hole-reads-capture discussion | m1 his (3) is consistent with §6.2 / R.1.13 | S | §6.2 (captures opt-in), R.1.13 "setting a label is the group form read as a LABEL" |
| same | m2 no per-group "labelled, not returned" form | WITHDRAWN (the record, next entry) | printed as withdrawn, §R.9 |
| same | m3 a read in a hole needs the group's text kept during the match | S, HAND-WORKED | the callout model reads the group's text at the hole, mid-match (PART HR's label model) |
| recollection | m1 withdraws "lacking" | S (applied) | §R.9 |
| recollection | m2 a label-only group has no capture, so `$y` there is the label | moot after the ruling; `\k<y>` on a label-only group NOT STATED anywhere | grep of the draft: 0 hits for `(?<:` before rev 28 |
| recollection | m3 how it sits with `captures` is not stated | S | 0 hits (grep `(?<:` / `label-only` before this lane) |
| hole-reads-capture ruling | m1 `\k<y>` reads the capture in rx text | S | PART HR: `/(?:(?<y>\d)?-\k<y>;)*/` WHOLE `3-3;-3;` HOLDS where the label FAILS; 2 / 2 / 2 of 21,845 |
| same | m2 the carried-capture form still to be spelled | S | §R.8 spellings 3 unspelled; R.1.16 A10 |
| same | m3 nothing to read on a label-only group | U | a proposal's construct; libpcre2 rejects `(?<:x>foo)`, `(?':x'foo)` (error "subpattern name expected"); `(<:x>foo)` compiles (PART HR) |
| number-domain question | m1 `padded()` pads the RESULT, so it answers numeral-width, not number-domain | S for the wrap; NS as "answers numeral-width" | PART PW A: under canonical `0099-0100` FAILS (the read is no number); PART NW: numeral-width parts under `-` |
| same | m2 zeros outside the label (C) | S | PART PW C: canonical = parsed, 0 / 0 / 0 of 3,906 |
| same | m3 WIDTH KEPT not needed under any domain | NS | PART NW: `$y - 1` on canonical operands parts on 3 of 9,999 (`10`, `100`, `1000`) |
| padded runs A, B, C (exact model) | the record's answers | S (REPRODUCED, both domains) | PART PW A, B, C (the scratch approximation's answers agree with the exact callout model on every printed case) |
| padding-width idea | m1 the width form is a plain macro `/0*${rx}/ & /(?s:.){${n}}/` | S as a macro; it is the EXACT reading (overtaken by the minimum ruling) | PART PW: EXACT fails `9999-10000` |
| same | m2 one macro, optional parameter | reading kept (no run decides it) | — |
| same | m3 exact vs minimum not decided | overtaken by the ruling | — |
| number-domain ruling | m1 numeral-width is moot ("the two candidates part only if the domain admits padded numerals") | NS | PART NW: CANONICAL `/(?<y>\d+)-${$y - 1}/` WHOLE `10-9` HOLDS, `10-09` FAILS; WIDTH KEPT the reverse; under `+ 1` 0 of 10,000 differ, under `- 1` 3 of 9,999. The draft's sentence holds for `+` only |
| same | m2 the result is canonical, pad by wrapping | a READING (not ruled: the record says the second half was not named) | — |
| same | m3 "outside: removed at compile time, nothing at run time" ruled with the quoted definition | U beyond the record's statement | the record says the definition was quoted; its text is not in the record. Run of the meaning: PART PW A `0099-0100` FAILS |
| width clarification | m1 his sketch is a count hole holding a read: UNDER CONSTRUCTION | S | R.1.16 T13 (a read of an infinite label in a count) |
| same | m2 the two-case macro = "zero-filled to n" (minimum), the manager's 36,119 checks | S (0 differ); the COUNT not reproducible | PART PW: 47,112 checks (this lane's six candidate texts per value; the record does not list the manager's six), 0 differ; several-string arguments (`7|123|12345`, `007|5`, `0|00`, `123456|42`, `abc|x`) 0 of 137,257 each; a member with its own zeros `007|5` gives `0005|0007`; a member longer than n `123456` is unpadded |
| same | m3 exact already spelled without a width | S | `padded(rx) & /\d{4}/` = PART PW B |
| rightmost-4 | m1 image and filter differ on overflow | S | PART PW bounds: value `10000`: image `0000`, filter nothing; `43`: both `0043`; `2026`: both `2026` |
| same | m2 compositions over minimum | a READING | — |
| `<=9999` | m1 on the value vs on the padded text | S | PART PW bounds: `43`: on the value `0043`, on the padded text nothing; `10000`: nothing both |
| same | m2 only the comparison is order-sensitive | S | the same four-way table |
| padded-width ruling | m1 the body is the two-case macro | a READING, S as equal to the meaning | PART PW (sabotage s2 caught) |
| same | m2 no width: the 2026-11-15 body | S | §2.7 unchanged |
| hole-flags ruling | m1 the two PCRE analogues disagree | S | PART FL (propagate vs `(?-i:..)`); rev 27.1's PART J |
| same | m2 `any_case` under propagation | S | PART AC |
| flags-propagate discussion | m1 propagation with override | RULED (row 138) | — |
| same | m2 the read is the case with nothing written | S | PART FL: the read `${$y}` vs the binding `${q}` at the same hole 0 / 0 / 0 of 1,365; read vs `\k<y>` 0 / 0 / 0 |
| flags-propagate ruling | m1 every flag (i, m, s, x) | S by the ruled form's words ("the flags in force at the hole"), each RUN | PART FL: `(?m)a\n${/^x/}` WHOLE `a\nx` HOLDS (not: FAILS); `(?s)a${/./}b` on `a\nb` HOLDS (FAILS); `(?x)${/a b/}`: `ab` HOLDS, `a b` FAILS (the reverse) |
| same | m2 an `&` operand, a condition's set, a filter-role argument are not holes | what the draft says today: §11 THE ROLE TABLE keeps them as their own literals ("a filter role ... matched whole"); not extended | §11 mark; PART AC shows the consequence |
| same | m3 `any_case(rx) := /(?i:${rx})/` for plain args; filter-role args still fail | S | PART AC: `/ho/`, `/h[o1]+/`, `/(?:ho|1h)/` 0 of 781 each (reversed rule: 3, 64, 4); `any_case(quoted("ho"))` 3 of 781 under (a), 0 under (b) |
| same | m4 PART J moves (`a-A` FAILS -> HOLDS) | S | PART FL: WHOLE `a-A` HOLDS / SEARCHED `x a-A` `a-A`@2 / FIND-ALL `a-A a-a A-a` [`a-A`@0, `a-a`@4, `A-a`@8] |
| same | the override `/(?i)${/(?-i)blah/}/` (hand-worked) | S, RUN | PART FL: WHOLE `BLAH` FAILS / SEARCHED `BLAH blah` `blah`@5 / FIND-ALL `blah BLAH Blah blah` [`blah`@0, `blah`@15] |
| same | a binding `/blah/i` in a caseful hole | S, RUN | PART FL: `/x${q}/` WHOLE `xBLAH` HOLDS, `XBLAH` FAILS; FIND-ALL `xblah XBLAH xBLAH` [`xblah`@0, `xBLAH`@12] |
| unset-in-hole question | the manager's answer table | S | PART UN: `(?<y>\d)?-${$y | "x"}` = PCRE's `(?:\k<y>|x)` 0 / 0 / 0 of 1,365 |
| unset-in-hole ruling | m1 the constant is `(?!)` | S | PART UN: python `re` and libpcre2: finds nothing in `abc`, not the empty string; `(?:(?!)|x)` holds on `x`; `a(?:(?!))?` holds on `a` |
| same | m2 the naming trap | S | the record's `when` ruling, "It holds and matches nothing" (the empty string) |
| same | m3 the empty array = `(?!)` under the `|`-only proposal | a READING over a proposal; not folded | — |
| same | m4 the "previous value" forms need the optional lead | S | PART UN: the first form hits [] on both texts; the edge-second witness hits as printed |
| clarification | m1 per-member reading | overtaken by the ruling (enumerate line) | — |
| same | m2 `\d + 1` a compile error | NS after the ruling | PART CN: `\d + 1` compiles (ten strings) |
| same | m3 (a) answered: arrays BUILT | S | the ruling; PART TT |
| same | m4 error class open | closed by the manager's call | — |
| same | m5 `/a|b/` vs `"a" | "b"` | closed by the ruling | PART CN: `left(/foobar|bazqux/, 2)` = `left("foobar" | "bazqux", 2)` = `fo|ba` |
| same | m6 `length` on a read yields a numeral | S | PART CN: `/(?<y>\w+)-${length($y)}/` WHOLE `abc-3` HOLDS / SEARCHED `ab-3 abc-3` `abc-3`@5 / FIND-ALL `a-1 ab-3 abcdefghij-10` [`a-1`@0, `abcdefghij-10`@9] |
| two options | m1 the enumerate line | RULED | — |
| same | m2 array-lift with "array" = what enumerate lists | S | PART CN `[1, 2] + [10, 20]` = `11|21|12|22` |
| same | m3 option (i) refuses the ruled array examples | a READING | — |
| construction-line ruling | m1 (a) answered | S | T8 |
| same | m2 lift-order by consequence | S | PART CN: for `\d{1,2}` enumerate's order (greedy first) = PCRE's path order: run-time vs copies 0 / 0 / 0 of 1,365 |
| same | m3 `\d + 1` compiles; `left(/\d+/, 2)` does not | S | PART CN |
| same | m4 one answer for `/a|b/` and `"a" | "b"` | S | PART CN |
| same | m5 (b) untouched | S | the ruling names no count/class/option read; T13, T15, T16 unchanged |
| same | m6 the hand-worked table RUN | S | PART CN: `left("foobar", 2)` = `fo`; `left(/foobar|bazqux/, 2)` = `fo|ba` (WHOLE `fo` HOLDS / SEARCHED `xba fo` `ba`@1 / FIND-ALL `fo ba fofo` [`fo`@0, `ba`@3, `fo`@6, `fo`@8]); `\d + 1` WHOLE `10` HOLDS / SEARCHED `x10` `1`@1 / FIND-ALL `10 3 11` [`1`@0, `3`@3, `1`@5, `1`@6]; `left(/\d+/, 2)` refused; `left(/(?<=x)ab/, 1)` refused |
| dollar-warning revised call | do the general diagnostics fire on `/(?<x>\d+)-/ & ($x & <5)`? | NS (by the draft's rules) | §5.2: "nothing when emptiness is match- or parameter-dependent"; T19: `$x & S` "is now T2, not a condition", so not a `test.never` test. PART DW: the program never holds (0 / 0 / 0 of 364), `(x: <5)` 1 / 132 / 132. A GAP, reported (OWNER QUESTIONS LEFT, dollar-diagnostic) |
| same-name-twice | m1 a group arriving through a hole or a part | U: NOT STATED in the draft (R.1.16 A9 reads the part's own group for backref-across-parts; nothing counts hole/part groups toward "two groups of that literal") | — |
| same | m2 `\2` untouched | S | PART SN: `(?J)(?<h>\d)(?<h>\d)-\2` WHOLE `12-2` HOLDS / SEARCHED `x12-1 34-4` `34-4`@6 / FIND-ALL `12-2 34-3 56-6` [`12-2`@0, `56-6`@10] |
| same | m3 A10's note and PART BL m3 become this rule's cases | S, applied | PART SN: without `(?J)` libpcre2 rejects ("two named subpatterns have the same name (PCRE2_DUPNAMES not set)"); with it `12-1` HOLDS, `12-2` FAILS; vs "the first group" 0 of 121 |
| array-in-hole (R1) | m1 written today, the under-construction class | NS | R.1.16 T4's own rule: "UNDER CONSTRUCTION needs a DEFINED meaning"; the ruling says "not ... defined now". Its class is the manager's to call |
| same | m2 the array form outside a hole untouched | S | his words name `${@y}` only |

## ANSWERS CHANGED

His earlier words (or the draft's), where the draft states them, what they become, follows-or-reading (R.1.16 rows A18-A25).

| # | earlier words | where | becomes | follows or reading |
|---|---|---|---|---|
| A18 | NO OWNER WORDS: §11 "NO INHERITED FLAGS (a hole's pattern keeps its own flags: §13 O32)"; R.1.14 "keeping its own flags" (the draft's rule; he observed the draft said both) | §11, R.1.14, R.1.15, §13 O32/O70, §R.6, §2.7, §0.1 L32 | REVERSED: the inserted rx starts with the hole's flags, its written flags win | FOLLOWS ("flags-propagate: yes"); the reversed rule was the draft's, not his |
| A19 | "I understand why any_case is currently a primitive ... I am ok with that being a followup" | §2.7 BODIES, §13 O70 | its ground gone for plain arguments (0 of 781); a filter-role argument still differs (3 of 781); the primitive stays RULED | READING (the lane's) |
| A20 | "padded(rx) := /0*${rx}/ ... Give or take details" | §2.7, §2.4, §13 O27 | kept; NEW `padded(rx, n)`, a minimum, body the two-case macro | the width FOLLOWS ("padded-width: minimum"); the body a READING; names not ruled |
| A21 | the dedicated "did you mean `x: <5`?" warning (draft's reading; the manager's call "the warning stays") | §0.1 L28, §R.2, A1, A15 | WITHDRAWN; L28 BY DESIGN; the general diagnostics do not fire (a GAP) | MANAGER'S CALL after "is it still needed?" |
| A22 | his `if($y & (0: 1492), "Columbus", $y)` | R.1.15 (12), A12, T11 | an illustration; no value-test case | FOLLOWS |
| A23 | "To restate, $y is a regex but of an anchored plain string that is a backreference"; "my understanding of $y is that it represents the captured value at the labeled group" | R.1.15 (11) | `${$y}` the LABEL; the capture via `\k<y>` | FOLLOWS |
| A24 | "We can create functions like left() and restrict them to constants now"; "The "under construction" remark is that this is hard"; rev 27.1's T5 line | R.1.16 T4, T5, T8, T9, A6; §5.5 | the line at enumerate: finite rxs BUILT | FOLLOWS ("construction-line: enumerate") |
| A25 | the label rule's two groups of one name; rev 27's three `\k` candidates | R.1.15 (8), A10, T20 | `\k<h>` an error unless `(?J)`, then first set group | FOLLOWS ("same-name-twice: i agree with your lean.") |

## WHAT MOVED

Answers (the §R.7 REV 28 block lists them): rev 27.1's PART J `/(?i)(?<y>a)-${q}/`, q := /a/: WHOLE `a-A` FAILS ->
HOLDS; SEARCHED `x a-A` FAILS -> `a-A`@2; FIND-ALL `a-A a-a A-a` [`a-a`@4, `A-a`@8] -> [`a-A`@0, `a-a`@4, `A-a`@8].
§13 O32 `/${q}/m` on `{a}\n{b}`: [] -> [`{a}`@0, `{b}`@4]. §0.1 L32 GAP -> SAME (q without flags of its own). §2.7
`any_case` candidate body on plain arguments 3 of 781 -> 0. T8/T9 on a finite rx UNDER CONSTRUCTION -> BUILT NOW
(`/${\d + 1}/` WHOLE `10` HOLDS); T8 on an array OPEN -> BUILT NOW; `\d{${n + 1}}`, n := [2, 4]: OPEN -> BUILT NOW.
`\k<h>` after two same-name groups without `(?J)`: three candidates -> a COMPILE ERROR. §0.1 L28 WARNING -> BY DESIGN;
L33's answer difference GAP -> BY DESIGN. No answer moved for unset-in-hole, number-domain or hole-reads-capture (the
draft's readings were the ruled ones; their status moved to RULED).

Withdrawn/changed terms grepped over the WHOLE draft after the edit (`grep -c -F TERM docs/design/predicates_draft.md`;
then `grep -n -F TERM | grep -v "REV 28"` for the unmarked lines): "NO INHERITED FLAGS" 16 lines, "keeps its own flags"
8, "own flags" 14, "hole-reads-capture" 24, "number-domain" 27, "numeral-width" 29, "unset-in-hole" 29,
"construction-line" 40, "value-test" 17, "dollar-warning" 14, "same-name-twice" 18, "lift-order" 14,
"under-construction-class" 9, `padded(` 147, "array-in-hole" 12, "flags-propagate" 23, "padded-width" 9, "hole-flags"
18 (counts before the last four marks; the marks added lines to none). Every unmarked live line left is one of: the
changelog (history), a dated older-revision block of §R.7/§R.10/§R.11 (the record), a quote of his words, or a
continuation line of a paragraph whose REV 28 mark is on a neighbouring line (R.1.15 header and (2), (3), (11), (13);
§11's NO INHERITED FLAGS; §13 O70 (ii)). Marked live sites: R.1.0 MATCH VALUE; R.1.7 (b) and REF4; R.1.14 HOLE-READING
(1) and AL; R.1.15 header, (2), (3), (5), (8), (9), (11), (12), (13); R.1.16 T4, T5, NUMBER DOMAIN, T8, T9, T11, T12,
T13, T20, T21, the composition, A1, A6, A10, A12, A15; §R.2 dollar-condition; §R.6 two rows; §R.8 RULED rev 28 and 14
rows; §R.9 nine rows; §0.1 L28, L32, L33; §2.4; §2.5 and §4.1 dollar hints; §2.7 (THE WIDTH FORM, `any_case` row, the
closing paragraph); §5.4 `$`, `${ }`; §5.5; §11; §13 O27, O32, O70 (three places), the glossary-table pointer row; the
seven live `${$..}` uses (one bracket, 7 occurrences).

## DRAFT READINGS ADDED

Each marked in the draft as a reading, not a ruling:
- The two-case macro as `padded(rx, n)`'s body (THE MANAGER'S READING; equal to the ruled meaning on every check).
- numeral-width NARROWED to "a result narrower than its operand" (the lane's, from PART NW); THE DRAFT'S READING stays canonical.
- An `&` operand, a condition's set and a filter-role argument are NOT holes for flags-propagate (§11's ROLE TABLE as it stands; not extended).
- array-in-hole written today: a compile error whose class is not stated (the manager's m1 not supported).
- §2.4's `$` component "leading zeros ignored" marked IN CONFLICT with number-domain (§R wins).

## OWNER QUESTIONS LEFT

New or reshaped by this lane (the manager decides whether to ask; definitions as the draft now has them):

| slug | current definition | runs, every mode |
|---|---|---|
| **numeral-width** (narrowed) | the text of a computed numeral narrower than its operand (`10 - 1`): CANONICAL (`9`, THE DRAFT'S READING) or WIDTH KEPT (`09`) | PART NW: `/(?<y>\d+)-${$y - 1}/` CANONICAL WHOLE `10-9` HOLDS, `10-09` FAILS / SEARCHED `10-09 10-9` `10-9`@6 / FIND-ALL `10-9 100-99 100-099` [`10-9`@0, `100-99`@5]; WIDTH KEPT WHOLE `10-9` FAILS, `10-09` HOLDS / `10-09`@0 / [`100-099`@12]; 3 of 9,999 operands differ; `+ 1` 0 of 10,000 |
| **dollar-diagnostic** (a GAP, from the withdrawn warning) | `/(?<x>\d+)-/ & ($x & <5)` never holds; no diagnostic of the draft fires (§5.2's "nothing when emptiness is match- or parameter-dependent"; not a test, T19) | PART DW: WHOLE `3-` FAILS / SEARCHED `7-3-` FAILS / FIND-ALL `3- 7- 3-` []; `(x: <5)`: HOLDS / `3-`@2 / [`3-`@0, `3-`@6]; 0 / 0 / 0 vs 1 / 132 / 132 of 364 |
| **any-case-body** | does `any_case(rx) := /(?i:${rx})/` replace the primitive now? Equal on plain pattern arguments; a filter-role argument differs unless flags also reach `&` operands (not ruled) | PART AC: (a) `any_case(quoted("ho"))` WHOLE `"HO"` FAILS / SEARCHED `x "HO" "ho"` `"ho"`@7 / FIND-ALL `"ho" "HO" "Ho"` [`"ho"`@0]; (b) (= the primitive) HOLDS / `"HO"`@2 / [`"ho"`@0, `"HO"`@5, `"Ho"`@10]; plain args 0 of 781 |
| **domain-components** | §2.4's rev 18 LEAN reads a `$` component of a tuple bound "by its VALUE, leading zeros ignored", in conflict with number-domain (a read `09` is no number) | HAND-WORKED (tuple comparisons are not in this lane's model): `((h, m): > ($sh, $sm))` with sh read as `09`: under the LEAN 9; under the ruled domain the bound yields nothing, so the test never holds on such a text, in every mode |
| **array-in-hole class** | `${@y}` today: a compile error; which class (UNDER CONSTRUCTION needs a defined meaning, T4; the ruling says not defined) | no run: every mode a compile error under either class |
| **same-name-count** (same-name-twice m1) | does a group arriving through a hole or a part count toward "two groups of that literal"? NOT STATED | no run (no rule to model) |

Still open from before (unchanged; their §R.8 rows carry runs in every mode): plus-operands, construction-line (b),
other-holes, anything-text, zero-in-sequence, group-truth / pass-table, number-in-loop, hit-carry-depth,
caller-ambiguous, not-test, condition-group, product-order, the conditional's spelling; the spellings review (now
items 1-32).

PCRE2 facts that would need its SOURCE (D181): none needed; every PCRE fact here is a run of libpcre2-8 10.46.

## EVIDENCE AND COMMANDS

- Premise: `(cd <worktree> && timeout 600 python3 -I docs/dev/lanes/predspec271_evidence/predspec271_model.py) | diff - docs/dev/lanes/predspec271_evidence/predspec271_model.out` -> empty.
- Forward: `(cd $PCREC_TMPDIR/scratch/predspec28 && timeout 900 python3 -I -B <worktree>/docs/dev/lanes/predspec28_evidence/predspec28_model.py > fwd.out)`; committed as `predspec28_model.out`; CHECKS 19 of 19 OK; re-run byte-identical.
- Sabotage: `PREDSPEC28_SABOTAGE=sN` for N = 1..14, each alone, and `=1`; committed as `predspec28_sabotage.out`: 14 of 14 CAUGHT (s2 fails two checks, the rest one each); all at once 6 of 19 (the helper selfchecks). Every non-selfcheck check has at least one sabotage.
- Counts the draft states anew carry their source: 47,112 and 137,257 (PART PW, `vals` x `cands` and `pool("0123457", 6)`); 781 (`pool("hHoO1", 4)`); 1,365 (`pool("aA-x", 5)`, `pool("0123", 5)`, `pool("37x-", 5)`); 3,906 (`pool("0159-", 5)`); 21,845 (`pool("37-;", 7)`); 364 (`pool("37-", 5)`); 9,999 / 10,000 (PART NW ranges); 121 (`pool("12-", 4)`).
- Draft size: `wc -lc docs/design/predicates_draft.md` 9,523 / 1,221,021 before; 9,755 / 1,273,900 after.
- `make -s test-plan-lint`: PASS.
- Files: `docs/design/predicates_draft.md`; `docs/dev/lanes/predspec28_evidence/{predspec28_model.py, predspec28_model.out, predspec28_sabotage.out, CLAUDE.md}`; this report; the history index line in `docs/dev/history/claude_md/docs__dev__lanes.md`.
