# CRITIC SIMULATE: predspec20 findings

## Findings



### SIMULATE-1 — the label controls are not upward-closed: in its REAL (searched) mode the §4.2 `t2` table's `9:15` row moves, and `0:09` reports the MINUTES as an hour
CONFIRMED. Rev 20 §4.2 l.1813-1825 gives `t2 & ((h, m?): late)` and `t2 & ((h, m = 0): late)` as programs and tabulates
`9:15` FAILS / FAILS / FAILS. The §12 header (l.3400-3401) says subjects are SEARCHED unless the program anchors, and
§0.1 MODE OF THE ANSWERS (l.746-749) lists the not-upward-closed filters as "a condition on an ambiguous label, a
count" only. A marked or defaulted absent label is a THIRD source: D196 tries the shorter end, and dropping the
optional part turns a present-and-rejected m into an absent-and-accepted one. Engine-run (simulate/d1_searched.py,
libpcre2-8 10.46 + Python `re`, 0 disagreements, 11,110 `t2` subjects; leftmost start, ends in t2's priority order,
each span read by its own parse):
- unmarked `((h, m): late)`: whole vs searched differ on 0;
- `((h, m?): late)`: differ on 1,698, every one a whole-REJECTED subject the search ACCEPTS: `9:15` -> `9` at 0;
  `0:09` -> `09` at 2 (the minutes text read as an hour);
- `((h, m = 0): late)`: differ on 1,660: `9:15` -> `15` at 2.
So the table's `9:15` FAILS holds only on the whole value; the author who wrote "missing minutes are acceptable" gets a
match inside a time the condition rejects. Expected: the MODE paragraph names the label controls beside L34/L59/L66,
§4.2's table says "whole value" and gives the searched answers (or pins `anchored(...)` as §12.9 does), and the
"saving people from themselves" criterion (§0 STANDING CRITERIA l.593) lists this misuse as silent or gives it a
diagnostic. Severity: answer (stated answers wrong in the program's real mode) + design (a new silent trap). Effort:
small (text) / a diagnostic is a design choice. Blast radius: §4.2 table and list table (l.1832-1838 has the same
shape), §0.1 L82/L90/L95/L96/L97 (stated on `t2`, mode unstated), §0.1 MODE paragraph. Rev 20 §4.2 l.1811-1838, §0.1
l.746-749.

### SIMULATE-2 — **match-context** is not a free choice: the manager's reading (b) (DOM over "the pattern") breaks the ruled principle (*) once L1, L2 and L3 are applied; only a context/chain reading keeps all four
CONFIRMED (the manager's reading (b), §4.2 l.1933-1939, and §13 l.4920-4922, which frame it as a free choice "Both
depend only on behaviour"). On rev 20's own (b) pattern P = `/(?|(?<k>a)(?:;(?<h>\d))*|(?<k>b)(?:;(?<h>[5-9]))*)/`
and Q2 = `/(?<k>b)(?:;(?<h>[5-9]))*/` (simulate/d3_context.py, PCRE2 for P, both engines for Q2, 0 disagreements):
`P & (k: "b")` and Q2 match the same subjects and set k, h the same way on 222 of 222 subjects. On `b` (zero passes):
- C  `P & (h?: <5, k: "b")`: under (b), h's part ranges over DOM over P (0..9) -> HOLDS, k = b -> HOLDS: HOLDS (rev 20
  says so, l.1936-1937);
- A  `P & (k: "b") & (h?: <5)` = C by L3 (record = `&`, RULED C22/CF:866) and L1 (`&` order-free, RULED);
- Bq `q := P & (k: "b")` then `q & (h?: <5)` = A by L2 (binding = expansion, RULED CF:722): HOLDS;
- B  `Q2 & (h?: <5)`: DOM(h) over Q2 is 5..9: FAILS.
Bq and B are two patterns that match the same subjects and set their labels the same way, so (*) requires one answer;
under (b) they give HOLDS / FAILS. Under the context (or chain) reading all four FAIL. So the choice the owner is asked
(**match-context**) is already forced by the ruled principle plus three ruled SAME rows, unless one of them is to give
(the record would then have to say which). The (b) text's "differ only where the pattern ties h's values to another
label's text" understates it: any CONDITION on another label narrows the pattern the same way. Severity: answer (a
stated answer, `b` HOLDS, contradicts ruled rows) + design (an owner question framed as open is constrained). Effort:
small in text (restate (b) with this derivation; recommend the context reading or name which ruled row yields).
Blast radius: §4.2 (b), §13 match-context, §0.1 L3/L46 if (b) is kept, §6 "one table per label, priced once" (the
context reading prices DOM per condition, not per label). Rev 20 §4.2 l.1933-1939.

### SIMULATE-3 — DOM(h)'s "some match" leaves two choices unstated that each split equal-behaviour spellings: PCRE's parse vs any accepting parse, and the defining operand vs the `&` chain
CONFIRMED (the manager's reading of **mark-domain**, §4.2 l.1874-1876: "for a group label, the strings its group can
capture in some match"). simulate/d2_domain.py, libpcre2-8 10.46 + Python `re`, 0 disagreements:
- PRIORITY-DEAD (no lookaround, no backreference): P1 = `/(?:(?<h>a|ab)(?<k>b*))?x/`, P2 = `/(?:(?<h>a)(?<k>b*))?x/`
  match the same subjects and set h, k the same way on 3,280 of 3,280 subjects over {a,b,x} to length 7. `ab` is h in
  an ACCEPTING parse of `abx` (h = `ab`, k = ``), never in PCRE's parse (h = `a`, k = `b`). On `x` (h absent):
  `(h?: "ab")` and `(h?: !"a")` FAIL / FAIL with DOM = values in PCRE's parse, HOLD / FAIL with DOM = values in some
  accepting parse (the natural automaton reading of "some match") and under the group's text. Rev 20 does not say
  which parse; only PCRE's (the one reading, §4.5) keeps (*). joint_condition.md §4H.1's construct table (lookaround,
  atomic, conditional, backreference, recursion, context) does not list priority either.
- AND-DEAD: `/(?:(?<h>\d|zz))?x/ & /[^z]*/` vs `/(?<h>\d)?x/`: same subjects and labels on 121 of 121. `(h?: "zz")`
  on `x` HOLDS if DOM is taken over the operand that DEFINES h (`1`, `zz` in its matches), FAILS over the matches of
  the chain (the program) or of the second spelling. §4.2 (b)'s "one table per label, priced once" reads as the
  former; (*) needs the latter (and SIMULATE-2 shows the chain must include conditions too).
Expected: §4.2's DOM sentence says "in some match of the program the condition meets (the flattened `&` chain, §4.1's
lookup set), as PCRE parses it (§4.5)", and §6 l.2597-2600's pricing follows. Severity: answer (equal-behaviour
spellings answer differently under a plain reading of the text). Effort: small (text). Blast radius: §4.2 DOM
paragraph, (b), §6 joint condition at the default level, §0.3 DOM row (l.930). Rev 20 §4.2 l.1874-1879.

### SIMULATE-4 — reading (a)'s "never silently" is triggered only by "a backreference, recursion, a verb"; lookarounds, atomic/possessive groups, conditionals and PCRE priority (regular, but not readable off the group) have neither an exactness commitment nor the fallback
CONFIRMED (the manager's reading (a), §4.2 l.1916-1931; §6 l.2598-2600 repeats the same three-item list; §0 STANDING
CRITERIA l.591 cites (a) as the principle's "where it is not possible" clause). NOTE: rev 20 does NOT list lookarounds
as non-computable (this lens's brief assumed it does). simulate/d2_domain.py, both engines, 0 disagreements:
PA = `/b(?:(?<h>\d)(?<=a\d))?x/` (a non-edge lookbehind that can never hold, so h is never set) vs PD =
`/b(?<h>[^\s\S])?x/` and PB = `/b(?<h>\d){0}x/`: same subjects (`bx` only) and labels on 1,365 of 1,365 subjects;
exact DOM(h) is EMPTY for all three. A compiler that takes DOM from the group's text (`\d` for PA and PB, nothing for
PD) answers `(h?: <5)`, `(h?: !(<5))`, `(h?: /(?s).*/)` on `bx` HOLDS for PA and PB, FAILS for PD: a split (*)
forbids, and no clause of rev 20 makes it an error, because (a)'s trigger list does not name a lookaround or `{0}`.
joint_condition.md §4H.1 (the table "WHERE VALUES IS NOT READ OFF THE GROUP'S TEXT") already names the lookaround, the
atomic/possessive group and the conditional as cases where the text is wrong, and SIMULATE-3 adds PCRE priority; rev 20
carried only the non-regular ones into (a). Meanwhile §6 (l.2609, l.2683) says regular-lookaround lowering for
conditions is NOT a prerequisite, so nothing in the design builds the in-context automaton those cases need.
Expected: (a)'s trigger is "any construct for which the compiler does not compute DOM(h) in context" (or the list
gains lookaround, atomic/possessive, conditional, `{0}`/DEFINE, and priority), and §6 names the in-context DOM
automaton (whole program, PCRE priority) as what the default level must build for the mark. Severity: design (a
promise with an unstated build behind it; a silent answer change otherwise). Effort: small text, real build cost. Blast
radius: §4.2 (a), §6 l.2598-2600, §0 STANDING CRITERIA "where it is not possible". Rev 20 §4.2 l.1916.

### SIMULATE-5 — an EMPTY DOM(h) (a label no match ever sets) makes every marked condition FAIL, `(h?: /(?s).*/)` included, against the owner's verbatim "absence is acceptable, the condition is satisfied"; nothing names the case
CONFIRMED (the general form, the manager's disposition K, l.1863-1868, and F1 in every shape, the manager's reading
14:50 (b), l.1879; the owner's point (3), l.1848-1849, quoted verbatim). Engine-run (simulate/d2_domain.py, eng.py):
`/b(?:(?<h>\d)(?<=a\d))?x/`, `/b(?<h>\d){0}x/`, `/b(?<h>[^\s\S])?x/` never set h (1,365 subjects); PCRE's own idiom
`/(?(DEFINE)(?<o>\d{1,3}))(?&o)\.(?&o)/` matches `1.2` and `192.168` with o UNSET in every match (libpcre2 10.46). DOM =
{} in each, so under the general form `(h?: S)` FAILS for EVERY S, the set of all strings included, and `(o?: <256)`
FAILS on every subject. Point (3) as ruled says the marked absence is "acceptable, the condition is satisfied"; the
gloss "true whenever some value would do" (joint_condition.md §4H.2) is exactly what fails here, and the owner is
asked (**zero-pass-empty**, (d), l.1947-1951) only about the EMPTY SET side, not the EMPTY DOMAIN side of the same
existential. No diagnostic covers it: the never-absent-mark warning is the opposite case (l.1969-1974), `label.unset`
is about unmarked labels, and `dead.branch` (§5.2 l.2363) is not said to fire for a group made dead by a lookaround,
`{0}` or DEFINE. Expected: either the case joins **zero-pass-empty** in the owner's question (F1: FAILS; F2: HOLDS), or
a condition naming a label with an empty DOM is a compile error/warning ("o is never set in any match; DEFINE groups
are not captures"). Severity: design (an owner-ruled sentence contradicted in a corner, silently). Effort: small (text
+ one named diagnostic). Blast radius: §4.2 (d), §7.1, §13 zero-pass-empty. Rev 20 §4.2 l.1843-1868.

### SIMULATE-6 — a per-pass condition over a loop is not upward-closed either: rev 20's new pairing example "every time in the list is at least 9:30" finds `10:00,` inside `10:00,9:15,` when searched, and **zero-pass-empty**'s F1/F2 choice has a searched-mode consequence the owner is not shown
CONFIRMED. §4.3 l.2066-2068 (the pairing rule, RULED **joint-loops**): `list & ((h, m): padded(>= (9, 30)))` "= every
time in the list is at least 9:30". Engine-run, the program's real (searched) mode, each span by its own parse:
`10:00,9:15,` -> `10:00,` at 0; `9:15,10:00,` -> `10:00,` at 5; `10:00,9:15,11:00,` -> `10:00,` at 0 (whole value:
all three rejected). The §0.1 MODE paragraph (l.746-749) names only ambiguous labels and counts as not
upward-closed; "every pass" is a third (fewer passes pass more easily), as are the label controls (SIMULATE-1).
Rev 20 does make one trap smaller: the empty span no longer passes on zero passes (rev 19 would have reported an
empty match at 0 in `9:15,10:00,`). On §13's own zero-pass-empty example, `/(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*/ &
(h?: <$a, k: 3)` (the empty set through a match value), simulate/d6_empty.py, 11,100 subjects, 0 engine
disagreements: whole-rejected but searched-accepted (the zero-pass prefix `a-3` reported) on 165 subjects unmarked
(`(h: <$a, k: 3)`), 660 under F1, 770 under F2 (`0-3;0` -> `0-3`; F1 keeps it out). So F1 vs F2 decides 110 more
searched matches, not only the one whole-value cell (`0-3`) the owner is shown. Expected: the MODE paragraph names
per-pass conditions and the label controls; §4.3's example states its whole-value mode or pins `anchored(list)` (as
§12.9 does for counts); the zero-pass-empty question cites the searched consequence. Severity: answer (a stated
meaning false in the real mode) + doc. Effort: small. Blast radius: §4.3 pairing bullets, §4.2 list table (l.1832-1838),
§0.1 MODE paragraph, §13 zero-pass-empty. Rev 20 §4.3 l.2066-2068.

### SIMULATE-7 — an EMPTY CONSTANT set is a compile ERROR at a narrowing site (§5.2), yet rev 20 states FAILS for it (`all((n: <0))`, (d)'s "every spelling of the empty set", (ZJ-E))
CONFIRMED by the text. §5.2 l.2362-2363: "At NARROWING SITES (condition literals, ...) an empty intersection from pure
parts is an ERROR; a dead branch WARNS; nothing when emptiness is match- or parameter-dependent". `<0` is empty (§2.4:
canonical numerals carry no sign unless the literal has one). Rev 20 nevertheless writes: §4.3 l.2039 "`all((n: <0))`
FAILS (no value in DOM(n) is below 0)" on `/(?:(?<n>\d),)*/`; §4.2 (d) l.1948-1950 "a set that is EMPTY (every spelling
of the empty set, ..., (ZJ-E)) FAILS in all three spellings", where the (ZJ-E) spellings are `(h: <0, k: 3)`,
`((h, k): (<0, 3))`, `((h, k): < (0, 0))` (joint_condition.md l.1634), all constant. Each narrows its label to the empty
set from pure parts (and under F1 the whole program is empty: no pass and no zero-pass case can hold), so by §5.2 each
is a COMPILE ERROR, not a FAILS. Drill of the brief's two-spellings question, read from the text: constant `(h?: <0)`
ERROR; empty intersection `(h?: <5 & >7)` ERROR; empty through a match value `(h?: <$a)` at a = `0` (the one spelling
§13 l.4917 uses) no error, FAILS under F1 (engine-run in simulate/d6_empty.py). Marked and unmarked alike; the two
constant spellings agree with each other (both errors), so the spelling principle holds; the stated answers do not.
Note the F1/F2 interaction: under F2 `P & (h?: <0)` would NOT be empty (it holds on zero passes), so (d)'s choice also
decides whether a constant-empty mark COMPILES. Expected: l.2039 and (d) say "compile ERROR (empty intersection, §5.2)"
for constant spellings and keep FAILS for the match-value one; (d)'s question notes the compile-or-not consequence.
Severity: answer (stated outcomes) / doc. Effort: small. Blast radius: §4.2 (d), §4.3 l.2038-2039, §13 zero-pass-empty.

### SIMULATE-8 — "a quantifier with upper bound 1 is not a loop" decides loop-ness from the TEXT; a `*` loop that the program lets run at most once behaves as `?` but is still a pairing/repeated-label loop, so the same behaviour errors in one spelling and answers in the other
CONFIRMED (the manager's reading of HOW, **optional-as-loop**, §4.3 l.2072-2079; l.2021-2022 itself defines a repeated
label behaviourally, "one that can set it more than once", then lists quantifiers by text). simulate/d5_loopness.py,
both engines, 0 disagreements: `/(?:(?<h>\d),)*;(?:(?<k>\d)\.)*/ & /[^,]*(?:,[^,]*)?/ & /[^.]*(?:\.[^.]*)?/` (two
label-free operands: at most one `,`, at most one `.`) and `/(?:(?<h>\d),)?;(?:(?<k>\d)\.)?/` match the same subjects
and set h, k the same way on 19,531 of 19,531 subjects over {0,5,`,`,`;`,`.`} to length 6. By rev 20's text the first
has h and k in SIBLING `*` loops: `(h: <5, k: <5)` is the sibling-loops compile ERROR (l.2062-2065) and `(k: >$h)` the
repeated-label `$` ERROR (l.2006-2007); the second compiles and answers (`0,;3.` HOLDS). (*) says two patterns with the
same subjects and labels answer every condition alike; the owner's 15:23 words were about `x?` vs `(?:x|)`, and his
15:27 qualifier is "if it is possible": here it is (whether a loop can pass twice in some match of the program is a
regular question). Expected: loop-ness stated by behaviour ("a label that can be set more than once in some match of the
program", l.2021's own words) with the quantifier list as the syntactic sufficient case, or the text says the pairing
rule reads the spelling and lists this as a stated exception to (*). Severity: design (low frequency; error vs answer,
not a silent change). Effort: small text; the behavioural test is one automaton question. Blast radius: §4.3 WHAT IS A
LOOP, §0.1 L94's reason. Rev 20 §4.3 l.2072-2079.

### SIMULATE-9 — reading (a)'s UNDER-approximation is unspecified; with the evidence's enumeration bound, whether a program compiles depends on that bound (an unstated tuning constant), though never its answer
SUSPECTED (confirm by stating the under-approximation in the text and re-running (RA) with two bounds). Rev 20 §4.2 (a)
l.1917-1918 says only "an UNDER-approximation and an OVER-approximation"; predspec20_check.py (RA) takes UNDER = the
values met for a^i b a^j with i, j <= 6. My reading of the text agrees with the script on all six (RA) rows (HOLDS,
ERROR, HOLDS, FAILS, HOLDS, FAILS; 0 silent). But a set that meets DOM only beyond the bound, e.g. `(h?: /a{9}ba{9}/)` on
`x` for `/(?<h>(?<a>a+)b\k<a>)?x/` (exact: HOLDS, `aaaaaaaaabaaaaaaaaa` is a value), is a COMPILE ERROR at bound 6 and
HOLDS at bound 9; so two conforming compilers (or one compiler after a bound change) accept different programs. Not a
silent answer change, so (a)'s promise holds; but the compile-or-refuse boundary is a free constant (the owner's
suspect-tuning-constants rule). Expected: (a) names how UNDER is formed (or that a refusal may depend on it, the error
then printing the bound). Severity: doc (low). Effort: small. Blast radius: §4.2 (a), §6 l.2598-2600. Rev 20 §4.2 l.1916-1931.

## PROBED-AND-HELD
- §0.1 L82 re-applied from rev 20's text on 11,110 `t2` subjects (whole value): nothing vs `m?` 92, nothing vs
  `m = 0` 90, `m?` vs `m = 0` 2: as stated. L95 on `9`: FAILS / HOLDS: as stated. L97: 99 of 11,110: as stated
  (simulate/d4_rows.py, both engines, 0 disagreements).
- §0.1 L94 and **optional-as-loop**: `/(?<k>\d)?-(?<h>\d)?/` under `(h: <5, k?: between(3, 7))` vs SIX other spellings
  of upper bound 1 (`(?:x|)`, `{0,1}`, `(?:|x)`, lazy `??`, possessive `?+`, atomic `(?>x?)`): 0 of 121 differ for each;
  DOM(k) identical. The ruling's verdict holds for every upper-bound-1 spelling (see SIMULATE-8 for `*` narrowed to one pass).
- COMPLEMENT drill: `/(?<h>\d)?x/` vs the same four spellings: same subjects, labels and DOM; `(h?: !S)` answers alike.
- L56, L65 (SAME, rev 20) under **mark-domain**: DOM(n) = digits in all three spellings; `(n: <5)` FAILS and
  `(n?: <5)` HOLDS on `x` in each.
- L36/L93 (`all` = every label marked): SAME by definition; L3/L46/L83 SAME for one-label marks under either context
  reading, except as SIMULATE-2 shows when a condition on another label narrows the pattern.
- PRIORITY-DEAD, AND-DEAD, LOOKBEHIND-EMPTY drills: DOM = values in PCRE's parse of the program's matches keeps every
  equal-behaviour pair alike (0 splits); only the other readings split (SIMULATE-3, -4).
- (RA) reading (a): my reading = predspec20_check.py's on 6 of 6 rows, 0 silent changes.
- EMPTY SET spellings: constant `<0` and intersection `<5 & >7` both compile errors (agree), marked and unmarked; the
  match-value spelling FAILS under F1 (SIMULATE-7 for the stated-answer mismatch).
- §12 (each in its real mode): E-CAL `valid` vs `valid2`: 0 of 1,848 dates differ (four years, months 00-13, days
  00-32; simulate/d7_ecal.py); its stated subjects as stated. E-WEEKDAY, E-IPV4, E-LUHN, E-RFC, E-NEAR, E-SEP, E-DEPTH,
  E-JSONL: no label a condition reads can be absent (fixed-width or always-set labels), no mark, no default, no `?`
  around a read label: none of the three rulings reaches them. E-HTTP: `name` is set in every item and the counts read
  passes, never an absent label; anchored, so no shorter span. E-FILE: `w` always set in a record. E-CTX-7 searched
  on its two subjects: at least one header, the whole span passes first. E-CTX-1..6: unchanged (no absence). Rev 20's
  "0 of the twelve worked answers move" HOLDS.

CRITIC COMPLETE
