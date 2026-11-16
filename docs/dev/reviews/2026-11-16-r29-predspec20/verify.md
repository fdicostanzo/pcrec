# verify.md — round predspec20


### V1 — SIMULATE-1, SIMULATE-6
HOLDS (both).
Calls: `timeout 600 python3 -B R/simulate/d1_searched.py` (rc 0; libpcre2-8 10.46 + Python 3.14.4; 380,789 probes,
0 engine disagreements): plain 0 of 11,110 whole-vs-searched differ; mark 1,698 (`0:09` -> (`09`, 2)); def0 1,660;
`9:15`: plain None, mark (`9`, 0), def0 (`15`, 2). `timeout 600 python3 -B R/simulate/d6_empty.py` (rc 0; 858,455
probes, 0 disagreements): whole-rejected-but-searched-accepted 165 plain / 660 F1 / 770 F2 (F2-F1 = 110, as claimed).
I read both drills' search loop: leftmost start, ends longest-first (t2 and the `*` loop are greedy, so PCRE priority =
longest first), each span re-parsed whole: a faithful D196 emulation for these two patterns.
Rev 20 quoted: l.746-749 "a filter that is not upward-closed (a condition on an ambiguous label, a count) can pass on a
shorter span: L34, L59 and L66 give both answers"; "ambiguous label" is a defined term (l.2168: "two accepting parses
give it different spans"), and t2's m / list's h are UNambiguous, so neither the label controls nor a per-pass
condition is covered by the parenthesis. l.3401 "Subjects are searched ... unless the program anchors"; l.202/l.419 "a
final pattern is searched". §4.2 l.1813-1825 and §4.3 l.2066-2068 state the answers with no mode; contrast l.5127-5131,
where rev 18 already labels a sibling table "every row above is the filter applied to a WHOLE value ... SEARCHED ...
accept out-of-range neighbours through a shorter span". The `9:15` FAILS cell is a whole-value answer only.
Expected fix: RIGHT for the text (name label controls and per-pass "every" in the MODE paragraph; mark §4.2/§4.3 tables
"whole value" or pin `anchored(...)`; cite the 110 searched cases in zero-pass-empty). The DIAGNOSTIC half is not
indicated: the owner REFUSED the analogous `count.searched` warning (L66, l.675, "the fix is `anchored(...)`"), so the
consistent fix is the stated meaning + the anchored idiom, listed as silent under SAVING PEOPLE (l.593), not a new warning.

### V2 — SIMULATE-2, SIMULATE-3, FIXIND-7
SIMULATE-2: PARTLY. SIMULATE-3: HOLDS (AND-DEAD); PARTLY (PRIORITY-DEAD). FIXIND-7: HOLDS (split); circularity PARTLY.
Calls: `timeout 600 python3 -B R/simulate/d3_context.py` (rc 0, 981 probes, 0 disagreements): `P & (k: "b")` vs Q2
same subjects+labels 222/222; DOM(h) over P 0-9, over Q2 = over P & (k: "b") 5-9. `timeout 600 python3 -B
R/simulate/d2_domain.py` (rc 0, 28,571 probes, 0 disagreements): PRIORITY-DEAD same 3,280/3,280, DOM=VALUES {a} both,
DOM=PARSE/GROUP {a,ab} vs {a}, split on `(h?: "ab")`, `(h?: !"a")`; AND-DEAD 121/121, `(h?: "zz")` on `x` operand
HOLDS / chain FAILS. `timeout 600 python3 -B -I R/fixind/fixind_drill.py` (D3): t2m vs t2x 11,110/11,110 same; DOM(m)
100 vs 60; `(m?: padded(>=60))` differs on 110 of 6,710 (`9` HOLDS vs FAILS). 312 cases, 0 disagreements.
Rev 20 quoted: l.1874-1876 "DOM(h) = THE VALUES h CAN TAKE IN SOME MATCH OF THE PATTERN ... for a group label, the
strings its group can capture in some match"; l.1938-1939 "The pattern reading keeps DOM a property of the pattern
(one table per label, priced once)"; §13 l.4920-4922 "some match OF THE PATTERN (one value set per label, fixed at
compile time)"; §0.3 l.930 same; §6 l.2598 "a mark projects the set onto the other labels over DOM(h)".
Ruling: with "the pattern" = the operand that DEFINES the label ("one value set per label"), the Bq/B split (SIMULATE-2),
AND-DEAD and t2m/t2x (FIXIND-7) are real (*) violations from ruled L1/L2/L3 + the ruled principle. All three critics
converge on one fix: DOM over the matches of the PROGRAM the condition meets (the flattened `&` chain, the other
conditions applied, record entries counted as `&`-ed conditions by L3).
Where SIMULATE-2 OVERSTATES: "the choice the owner is asked (match-context) is already forced". It is not. Two
readings keep (*) + L1-L3: the CHAIN reading (DOM over ANY match of the program) and the CONTEXT reading (matches
agreeing with this match's other labels); both are functions of behaviour. They differ on rev 20's own example: `P &
(h?: <5)` on `b` (no condition on k) is HOLDS under chain (DOM over P = 0-9, the d3 output) and FAILS under context.
So what is forced is only "program, not defining operand"; **match-context** (chain vs context) stays a genuine owner
question, and rev 20's stated HOLDS for that example survives under the chain reading. SIMULATE-2's "context (or
chain)" wording is right; its "already forced" is not.
SIMULATE-3 PRIORITY-DEAD: confirmed by run, but rev 20's "capture in some match" plus the ruled ONE READING (§4.5,
l.2168ff: a condition reads PCRE's parse) already points at PCRE's parse; "some accepting parse" is a misreading the
text permits rather than states. A clause ("as PCRE parses it, §4.5") is right; severity doc, not answer.
FIXIND-7 circularity (`X & (h?: <3) & (h?: >7)`): avoidable, not inherent: taking DOM(h) over the program's matches
WHERE h IS PRESENT never consults the marks' absent-case answers, so the one-label case has no fixed point. For marks
on two labels whose present-matches each depend on the other's absence it can recur; that residue is SUSPECTED, unrun.
Expected fix: RIGHT as "DOM over the program's matches (chain incl. conditions), as PCRE parses them, over matches where
the label is present"; and §4.2 (b) / §13 match-context restated as chain vs context (not pattern vs context); §6's
"one table per label, priced once" becomes per condition-site. WRONG to present match-context as closed.

### V3 — SIMULATE-4, CHANGETAB-4
SIMULATE-4: PARTLY. CHANGETAB-4: HOLDS as a carry omission; its consequence framing is wrong.
Calls: `timeout 600 python3 -B R/simulate/d2_domain.py` (rc 0, 0 disagreements): LOOKBEHIND-EMPTY PA vs PB and PA vs
PD same subjects+labels 1,365/1,365; DOM=VALUES empty for all three (all four conditions agree, FAILS); DOM=GROUP
PA/PB 0-9, PD {} -> split on `(h?: <5)`, `(h?: !(<5))`, `(h?: /(?s).*/)`. Reproduced exactly.
Rev 20 quoted: l.1916 "(a) DOM NOT EXACTLY COMPUTABLE (a backreference, recursion, a verb)"; l.2598-2600 same three;
l.1874 DOM = "THE VALUES h CAN TAKE IN SOME MATCH OF THE PATTERN". joint_condition.md §4H.1 "WHERE VALUES IS NOT READ
OFF THE GROUP'S TEXT" table: lookaround, atomic/possessive, conditional are "regular"; backreference "NOT regular";
recursion "context-free". Row 72 (a): "not computable exactly (backreferences, recursion; lookarounds, atomic groups
and conditionals change it from the group's text; §4H.1's table)".
Ruling: rev 20's three-item list is CORRECT as the list of NON-REGULAR constructs: the source itself classes
lookaround/atomic/conditional as regular, i.e. exactly computable, not as error-tier cases. So CHANGETAB-4's "an author
learns the error tier only for three of the six" misreads row 72: the dropped clause says those three CHANGE DOM FROM
THE TEXT, not that they are refused. And SIMULATE-4's split needs a compiler that reads DOM off the group's text, which
rev 20's definition (VALUES) forbids; it is not a split the text licenses. What IS missing (both critics' real point):
rev 20 never says DOM is computed THROUGH those constructs (nor `{0}`, DEFINE, priority: SIMULATE-3), never says the
GROUP candidate is out (grep "group's text" in §4-§7: 0 hits), and §6 (l.2603-2610, l.2683) builds nothing that reads a
lookaround in context for this purpose, so an implementer can take the text and nothing flags it.
Expected fix: SIMULATE-4's FIRST form is right ("never silently" triggers on any construct for which the compiler does
not compute DOM(h) in context, and §6 names the in-context DOM automaton as owed). Its second form ("the list gains
lookaround, atomic, ...") is WRONG: it would put exactly-computable regular cases in the refusal tier. CHANGETAB-4's
fix is right only as "carry row 72's clause as: computed exactly in context, §4H.1's table".
V3 NOTE (added while reading the record for V4): the manager's own 15:27 reading (4) (COND-FAMILY.md l.1715-1717)
says "to be listed: backreferences, lookarounds, recursion"; rev 20 dropped lookarounds and added "a verb". That is a
manager's reading, not a ruling, and joint_condition.md §4H.1's runs class lookarounds as regular; the V3 ruling stands,
but the record should say why lookarounds left the list (computed exactly) rather than drop them silently.

### V4 — SIMULATE-5, RULING-1
HOLDS (both).
Calls: `timeout 600 python3 -B -I R/ruling/work/drill.py` DRILL 3 (rc 0, 0 disagreements): `/(?<k>\d+);(?:(?<n>\d),)*/`
on `50;` match, n unset, k = 50; DOM(n) = 0-9; values > 50: none; > 5: 6-9. So under F1 `(n?: >$k)` FAILS on `50;`,
HOLDS on `5;`. `timeout 600 python3 -B R/simulate/d2_domain.py`: LOOKBEHIND-EMPTY DOM=VALUES empty, `(h?: /(?s).*/)`
FAILS. My own `timeout 60 python3 -B R/verify/work/v4_define.py` (libpcre2-8 10.46): `(?(DEFINE)(?<o>\d{1,3}))(?&o)\.(?&o)`
matches `1.2` and `192.168` with o = None (unset) in both; so DOM(o) = {} and `(o?: S)` FAILS for every S under F1.
Record quoted: CF l.1666-1667 (point (3), RULED 14:31): "the OPTIONAL MARK ...: absence is acceptable, the condition
is satisfied; in a joint condition a marked absent label reads \"some value would put the tuple in the set\"". CF
l.1685-1687 (14:50 (b), "NOT the owner's words; told to him"): "for one label with a non-empty set that is the same as
\"satisfied\"". CF l.1687-1688 (14:50 (c)): "Some value\" ranges over ANY text". Rev 20 l.1877-1879: "The one-label mark
is the joint sentence's k = 1 case (\"some value in DOM(h) would do\", F1, the manager's reading 14:50 (b), in every
shape". Rev 20 rows that then fail a marked absent single label: l.1958 `(mnum?: >5)` FAILS; l.1927 `(h?: /a+b/)`
FAILS; l.1928 `(h?: !/a+ba+/)` FAILS.
Ruling: the decisive fact (sharper than either critic puts it): 14:50 (b)'s equivalence "for one label with a non-empty
set that is the same as satisfied" was TRUE under 14:50 (c) (ANY text: a non-empty S always has a witness) and became
FALSE when 15:27 reading (3) replaced ANY by VALUES. Rev 20 withdrew (c) and kept (b)'s "in every shape" without
re-checking the equivalence (b) rested on. The departure from the ruled one-label sentence is therefore not a corner:
it covers every S disjoint from DOM(h) (constant: `(mnum?: >5)`), every match-dependent S (`50;`), and every empty DOM
(DEFINE, `{0}`, a dead lookbehind: SIMULATE-5). Some constant witnesses may instead be §5.2 compile errors (V5), but an
error is not "satisfied" either, so the departure holds for all four of RULING-1's rows. The owner's zero-pass-empty
question (l.1947-1951) covers only an empty S; his assent there would not cover these.
Expected fix: RULING-1's is right (one owner question, slug e.g. **mark-one-label**: "satisfied" outright vs F1 over
DOM, the `50;` and `(mnum?: >5)` witnesses, and the reason (b)'s premise fell). SIMULATE-5's empty-DOM case belongs in
that same question, plus a named diagnostic for a label no match can set (its proposed "o is never set in any match;
DEFINE groups are not captures" text is right in content); folding it only into zero-pass-empty (its first option)
would mis-file it, since the set is not empty.

### V5 — SIMULATE-7 vs RULING-2(i) / FIXIND-1(b)
SIMULATE-7: PARTLY (conclusion holds, one premise false). RULING-2's `50;` witness: STANDS either way. FIXIND-1(b)'s
witness: survives with a changed verdict word. The contradiction is real and resolves toward SIMULATE-7.
Rev 20 quoted: l.2038-2039 "`(n?: <5)` = `all((n: <5))` HOLDS, `all((n: <0))` FAILS (no value in DOM(n) is below 0)";
l.1948-1950 "a set that is EMPTY (every spelling of the empty set, joint_condition.md §4G.4 corner 1, (ZJ-E)) FAILS in
all three spellings"; l.2362-2363 "At NARROWING SITES (condition literals, an `&` whose operands come from
definitions) an empty intersection from pure parts is an ERROR; a dead branch WARNS (`dead.branch`); nothing when
emptiness is match- or parameter-dependent"; l.2360-2361 "`:` ... NARROWS, in a condition (`isodate & (year:
<2000)` silently drops `5`, which `/\d{4}/` cannot hold)"; l.2467 "a numeral may carry a sign (`between(-15, 15)`,
§2.4)".
SIMULATE-7's false premise: "`<0` is empty (§2.4: canonical numerals carry no sign unless the literal has one)". Rev 20
l.2467 says a numeral MAY carry a sign; `<0` holds `-1`; no "carry no sign" sentence exists (grep: 0 hits). `<0` is
NOT the empty set. What is empty is its INTERSECTION with n's values (`\d`), as l.2039's own parenthesis says, and the
same for the (ZJ-E) spellings, which joint_condition.md calls "the same (empty) set of pairs" only relative to `\d`.
Why the conclusion still holds: §5.2's trigger is "an empty INTERSECTION from pure parts", and l.2360-2361 shows the
intersection meant is the label's values with the condition's set. `\d` ∩ `<0` = {} from two constants: ERROR. Under F1
the marked condition can then hold neither present (no digit < 0) nor absent (no DOM value < 0), so the program is dead
and the ERROR is also the useful answer. Hence l.2039 `all((n: <0))` and (d)'s constant spellings are compile ERRORS by
§5.2, not FAILS; the match-value spelling of §13 (`(h?: <$a, k: 3)` at a = `0`) is "match-dependent": no error, FAILS
under F1 (d6 drill: whole F1 vs F2 differ on the a = 0 subjects).
SIMULATE-7's F1/F2 remark is half right: under F2 the absent case holds, so the program is NOT dead, yet §5.2's
wording (the intersection, not the program) would still fire an ERROR on a program that matches. So under F2 §5.2
needs a clause ("a marked label's empty intersection is not an error"); under F1 it does not. Worth one line in (d).
RULING-2 (i) `all((n: >$k))` on `50;` (`timeout 600 python3 -B -I R/ruling/work/drill.py` DRILL 3: n unset, k = 50,
DOM(n) 0-9, no value > 50): match-dependent, so §5.2 says nothing; F1 FAILS; the 14:31 "every, possibly none" reading
HOLDS. The witness stands regardless of how the constant case resolves. FIXIND-1(b) (`all((n: <0))` on `''`): under
§5.2 the program does not compile, which is still not the vacuous HOLDS "every n below 0, possibly none" promises, so
its point survives with "FAILS" replaced by "a compile ERROR"; the cleaner witness for it is RULING-2's `50;`.
Expected fix: SIMULATE-7's fix is right (constant spellings: ERROR, cite §5.2; match-value: FAILS), with the premise
corrected ("empty intersection with DOM", not "empty set"), and (d)'s "a set that is EMPTY" rewritten as "a set
disjoint from DOM(h)".

### V6 — SIMULATE-8, RULING-3
HOLDS (both), as a stated-rule-vs-principle conflict; low frequency, and an ERROR-vs-answer split, never a silent one.
Calls: `timeout 600 python3 -B R/simulate/d5_loopness.py` (rc 0, 47,263 probes, 0 disagreements): 19,531 subjects, 9
matched (the whole 3x3 language), labels+subjects differ on 0; the narrowing is run as a label-free lookahead standing
for the two `&` operands. `timeout 600 python3 -B -I R/ruling/work/drill.py` DRILL 1 (rc 0): P1 `(?<k>\d)?-(?<h>\d)?` vs
P2 `(?:(?<k>\d)(?=-))*-(?:(?<h>\d)(?!\d))*`: 781 subjects, match differ 0, capture differ 0, 0 disagreements. I checked
P2 by hand: after a k iteration the next char must be `-`, after an h iteration it cannot be a digit, so each `*` body
can run at most once: a one-pattern witness, cleaner than SIMULATE-8's `&` program.
Rev 20 quoted: l.2018-2021 "A repeated label is ANY label inside a loop (one that can set it more than once; ...): a
group under `*`/`+`/`{n,m}` with m >= 2 or no m"; l.2074-2079 "a quantifier with upper bound 1 is NOT a loop for the
pairing rule ... A loop is `*`, `+`, `{n,m}` with m >= 2 or no m"; l.2062-2065 the SIBLING LOOPS error; l.2006-2007 bare
`$x` on a repeated label "is an ERROR". CF l.1698-1699 (RULED 15:23): "`x?` and `(?:x|)` answer alike under the
pairing rule"; the "how" (upper bound 1) is "THE MANAGER'S READING ... to be checked by the next revision".
Ruling: l.2018-2021 states the behavioural definition in its parenthesis and then lists quantifiers by text; the two
disagree on P2, where by the list h and k are repeated and in sibling loops (ERROR) while by "can set it more than once"
they are set-once and `(h: <5, k?: between(3, 7))` answers as on P1. Same subjects and captures (run), so (*) asks for
one answer. "If it is possible": it is (whether a group can be set twice in some match is a regular question for a
regular pattern). The ruled 15:23 text is met (it only names `x?` vs `(?:x|)`); the conflict is with the RULED 15:27
principle, against a manager's reading, so it is in scope.
Expected fix: RIGHT: define loop-ness by behaviour ("a label that can be set more than once in some match of the
program", l.2019's own words) with the quantifier list as the sufficient syntactic case; or keep the list and record
it with the owner as a named exception under "if it is possible" (cost argument: the behavioural test is one automaton
question per label, but over a NON-regular pattern it may not be decidable, so the exception clause is needed anyway
for backreference/recursion patterns; neither critic says so).

### V7 — FIXIND-1, RULING-2
HOLDS (both).
Calls: `timeout 600 python3 -B -I R/fixind/fixind_drill.py` (D2) (rc 0): DOM(g) = [a]; "every hit's g is a, possibly
none" vs `(g?: "a")` over `occurrences(/(?<g>a)?b/)`, spans over {a,b} length 0-6: 94 of 127 differ (`b`, `abb`);
`occurs.none(!(g: "a"))` vs natural: 0. Both drill regexes are engine-run; I read them: natural =
`(?!b)(?![ab]*bb)[ab]*` (every b has an a before it), mark = `[ab]*` (always: a present g is `a`, an absent g has `a`
in DOM). RULING-2's `50;` witness: `timeout 600 python3 -B -I R/ruling/work/drill.py` DRILL 3 (see V5).
Rev 20 quoted: l.1353-1354 "\"Every hit, possibly none\" is written with the mark, `(g?: \"x\")`, or `all((g: \"x\"))`
(`all(c)` is c with every label marked, §4.3): 0 of 5,461 spans from rev 9-19's plain answer (lane absimpact (OC))";
l.1439 "`(g?: ...)` is \"possibly none\""; l.2110-2111 "\"every, possibly none\" is `all`, rev 20"; l.3899
"\"possibly none\" is the mark `n?`"; l.4567 "\"possibly none\" is written with the mark". And §2.6 l.1327-1329 itself
uses `occurrences(/(?<g>a)?b/)` on `abb`, a hit without g: the very pattern where the gloss fails.
Ruling: the gloss is true only under two conditions together: (1) g is REQUIRED inside a hit (so the only absence is
zero hits: (OC)'s `r`), and (2) S meets DOM(g) (else F1 FAILS / §5.2 errors on zero hits, V5). Outside (1) the mark
also passes a hit lacking g (94 of 127); outside (2) "none" is not vacuous (`50;`). The "0 of 5,461" at l.1354 is a
population inside (1); the sentence is stated generally. RULING-2's relabel point also holds: CF l.1670-1671 (14:31
reading) "`all(...)` over no values HOLDS (the spelled-out \"every, possibly none\")" is a different answer from
"every label marked, F1" on `50;`, so "RESTATED" understates a CHANGE.
Expected fix: RIGHT: replace the gloss at the six sites with what the mark says ("each present g in S; an absent g
passes when some value of DOM(g) is in S"); name `occurs.none(!(g: S))` (DOM-free, 0 of 127) as the spelling of
"every, possibly none"; relabel `all` as CHANGED with the `50;` witness and put the vacuous-vs-marked choice to the
owner beside zero-pass-empty (RULING-2's effort estimate "small-medium" is fair).

### V8 — FIXIND-2, CHANGETAB-3
HOLDS (both).
Calls: `timeout 600 python3 -B -I R/fixind/fixind_drill.py` (D5) (rc 0; COMPUTED in Python over 1,111 lists, each list
whole-matched by both engines): R = (<10, <30): marked form 0 differ, `occurs.none(!((h, m): R))` 0; R' = (<10,
padded(<100)): marked form 71 differ (`3,`, `3,3,`, `3,3:15,`), plain-`!` form 0. I read D5's predicate: a minute-less
pass is counted iff some d in DOM(m) = 00-99 puts (h, d) outside R, which is the F1 reading of `((h, m?): !R)`; under
R' no d does, so `3,` passes.
Rev 20 quoted: l.2040-2042 "The one-condition spelling of \"the empty list passes, an item without minutes fails\"
over `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/` is `occurs.none(((h, m?): !R))`, R = `(h: <10, m: <30)`"; l.1742-1743 (J1)
"R names NO label: it is a plain set"; §5.4 l.2436 "`( label: S, ... )` in VALUE position ... a CONDITION, i.e. a
MACRO ..., NOT a record". joint_condition.md l.2123 carries the same `R = (h: <10, m: <30)`: the fold copied a source
slip. Row 66 (jc l.2624) asks rev 20 to write "its answer's dependence on DOM in one line (R' = `(h: <10, m:
padded(<100))` on `3,` ...)" and "`all` by definition gives 11 of 259 (`3,`)"; grep of rev 20: `padded(<100)` 0, `11
of 259` 0, "ANY FAILS" 0.
Ruling: (a) as written R is a labelled record, i.e. a condition (macro) in value position, so `((h, m?): !R)` puts a
negated condition where J1 needs a tuple set: ill-formed; the intended R is the product `(<10, <30)`. (b) the marked
spelling is right only because DOM(m) reaches outside R; the DOM-free spelling `occurs.none(!((h, m): R))` (unmarked
inner condition FAILS on a missing m, so `!` counts that item) gives the intent under every R. CHANGETAB-3's omission
is real, and FIXIND-2 shows why it matters: the dropped line was the one exposing the dependence.
Expected fix: RIGHT: write R as `(<10, <30)`; make `occurs.none(!((h, m): R))` the worked spelling (it needs no
mark and no DOM); keep the marked form only as the row-66 illustration of DOM dependence with R' and the `all` 11-of-259
line. Also amend joint_condition.md §4H.4's same text (a derivation-note fix, not rev 20's).

### V9 — FIXIND-3
HOLDS under rev 20's DOM as written; one cell's verdict word is wrong; and the V2 fix dissolves it.
Calls: `timeout 600 python3 -B -I R/fixind/fixind_drill.py` (D1) (rc 0): `(?<h>\d)?x`, DOM 0-9: 1 of 11 differ (`x`:
separate HOLDS, joined FAILS); `(?:(?<h>\d),)*`: 1 of 111 (`''`). 0 engine disagreements.
Rev 20 quoted: l.700 (L92) "a label named twice in one condition is a compile ERROR ...; `(h: A) & (h: B)` and `(h: A
& B)` are the spellings"; l.1863-1865 "the condition holds when some choice of one text from each absent label's D puts
the tuple in the set" (the choice is per condition); l.2362-2363 (§5.2) an empty intersection from pure parts is an
ERROR.
Ruling: with D = DOM(h) fixed per label and chosen per condition, `(h?: <5) & (h?: >5)` on an absent h HOLDS (3 and 7)
while the joined form cannot: real, and L92's fix hint offers both as if equal. Correction: with A = `<5`, B = `>5`
the joined `(h?: <5 & >5)` is a CONSTANT empty intersection, so by §5.2 it is a compile ERROR, not FAILS (as in V5).
A witness that stays an answer is match-dependent: `(h?: <$k) & (h?: >$k)` vs `(h?: <$k & >$k)` on a k in 1..8 with h
absent: HOLDS vs FAILS, no §5.2 error (by the text; not run).
Cross-finding: under the fix V2 recommends (DOM over the program's matches where h is present, every other condition
of the chain applied), the split disappears: for `(h?: <5)` the other condition `(h?: >5)` narrows h-present matches
to 6-9, so DOM = 6-9 and it FAILS, as the joined form does; symmetric for the other. So FIXIND-3 is a symptom of the
per-operand DOM, like FIXIND-7, and FIXIND-12's "scope of one choice" question largely reduces to the V2 choice.
Expected fix: the look-alike row + L92 sentence is RIGHT if DOM stays per operand; if V2's chain DOM is adopted, the
right fix is one line in L92 saying the two spellings agree because DOM is taken over the chain. Either way correct
the cell to ERROR for constant sets.

### V10 — FIXIND-4
HOLDS (by the text; nothing to run: the never-absent fact is the draft's own).
Rev 20 quoted: §7.1 l.2714-2716 "the NEVER-ABSENT MARK warning (rev 20: a mark `h?` on a label that can never be absent
where the condition reads it; the manager's reading (14:31)...)"; L93 l.701 and §4.3 l.2033 "`all(c)` is c with every
label marked"; §4.2 (e3) l.1964-1967 "`t2 & all(office_c)` ... that is the one way to mark through a macro ... (h is
never absent in `t2`)"; §7.1 l.2724-2725 `anchor.whole`: "text a macro body writes has no exemption, CF:1154 on main";
l.2130-2131 "`some`, `all`, `count` ...: lean library (prelude) names".
Ruling: by the two definitions (`all` = marks inserted; the warning reads a mark on a never-absent label) and with no
exemption stated, `t2 & all(office_c)` carries a mark on h, never absent in `t2`, so it draws the warning (and (f)'s
merged "never consulted" text), on rev 20's own recommended spelling. The only ruled precedent on macro-written text
(CF:1154, anchor.whole) says "no exemption", which points the wrong way for `all`. Not a wrong answer: a false
diagnostic on the idiom, which the SAVING PEOPLE criterion (l.593) cares about in reverse (noise trains authors to
ignore the warning).
Expected fix: RIGHT, and of FIXIND-4's two options the second is better: define `all` through the general form ("D =
DOM for each undefaulted label c names", no inserted written mark), so the warning, which is about what the AUTHOR
wrote, has nothing to read; the first option (the warning skips marks `all` adds) is an exemption the anchor.whole
ruling would need distinguishing from. Either needs one sentence; FIXIND-11's family framing is optional context.

### V11 — FIXIND-5, CENSUS-6
FIXIND-5: (a) HOLDS, (b) HOLDS, (c) PARTLY. CENSUS-6: HOLDS (a real two-reading sentence); by the text the zero-pass
`some` answer is FAILS.
Rev 20 quoted: §7.1 l.2707-2709 `label.unset` "fires wherever a label a condition names can be ABSENT where the
condition reads it, `*`, `{0,n}` and `occurrences` at `min = 0` included, unless the label is marked or defaulted; its
text names the THREE fixes, `h?` (absence acceptable), `h = v` (absence reads as v), an alternative without h"; L90
(l.698, not l.693 as FIXIND-5 cites) `t2 & (((h, m): R) | (h: 10))`; L97 l.705 "`label.unset`'s text names the default
as the fix"; §4.3 l.2034 `some`: "AT LEAST ONE iteration's g is in S; false on zero iterations; a MARKED absent label
inside it is COUNTED by the mark's one meaning"; §4.2 l.1899-1900 "a marked absence is COUNTED by `some`, `count`,
`occurs.*`"; §4.2 list table l.1832-1838 + l.1839 "the loop's zero passes leave h absent" (zero passes ARE an absence
the mark answers). joint_condition.md §4H.4 (l.2120-2121): "The group questions range over the PASSES of the pairing
loop; zero passes give no pass to count"; and l.2127-2128 "`(g?: \"x\")` and `some((g?: \"x\"))` both HOLD" on `ab`.
(a): the exemption clause is closed ("unless ... marked or defaulted"); the first alternative of L90's program names m
unmarked where m can be absent, so the warning fires on a program that took its own third fix. Real.
(b): `some((g: "x"))` over `/ab(?<g>[xy])?/` hits on `ab`: the warning fires (g absent in the hit); its first fix gives
`some((g?: "x"))`, which HOLDS on `ab` (jc §4H.4, quoted) though no hit is `x`. The fix turns "some hit is x" into "some
hit is x or lacks g". Real, by the text.
(c): overstated. A mark or default for a CAN be written (`(a?: <10, b: >$a)`, `(a = 0: /.*/, b: >$a)`); what is OPEN
(l.1961-1963) is whether it REACHES `$a`. So "fixes 1 and 2 cannot be written" should read "their effect on `$a` is
undecided"; the conclusion (e2 needs its own text) stands. V12 covers the reach question.
CENSUS-6: on `''` over `/(?:(?<n>\d),)*/`, `some((n?: <5))`: "false on zero iterations" says FAILS; §4.2's reading of
zero passes as an absence the mark answers, plus "counted", says HOLDS. The text does not decide it in one sentence;
the derivation does (jc §4H.4 "zero passes give no pass to count"; §4G "count no pass, unchanged"), and the rev 20 row
dropped its "in a pass". By the explicit clause and its source I rule the text's intended answer FAILS (count 0).
Expected fixes: FIXIND-5 (a) right (exempt a label every alternative of which controls it or omits it); (b) right
(inside a group question the fix to name is the unmarked condition or `!`, not `g?`; and the warning should not fire
on zero passes there, which also settles CENSUS-6's question); (c) reword as above. CENSUS-6's fix is right ("a marked
absent label in a PASS is counted; zero passes are no pass", plus the `some((n?: <5))` on `''` FAILS / `count` = 0
example row).

### V12 — FIXIND-6, CENSUS-9
HOLDS (both).
Calls: `timeout 600 python3 -B -I R/fixind/fixind_drill.py` (D4) (rc 0): `/(?<a>\d)?-(?<b>\d)/`, 110 subjects, DOM(a)
by running; `(a?: <3, b: >$a)` holds no-reach 24 / shared witness 33 / independent 33, split on `-1`..`-9` F/H/H;
`(a?: >7, b: >$a)` 1 / 2 / 10, split `-1`.. F/F/H. I checked the D4 predicates by hand on `-1`: shared needs one d in
DOM(a) with d > 7 AND 1 > d (none: F); independent takes d = 8 for the entry and d' = 0 for `$a` (H); no-reach reads no
`$a` (F). So the two conditions together separate all three readings, as claimed.
Rev 20 quoted: §4.2 (e2) l.1959-1963 "the condition FAILS (D = {} for a ...); `label.unset` covers it ... NOT
DECIDED: whether a default written for a in the same condition reaches `$a` ... left OPEN (§13)" (the mark is not
named); §13 l.4923-4925 the same, default only; §5.4 `=` row l.2442 "the label's DEFAULT ... one string, CF 10:43; the
value side is J2's, so a bare name there is a binding"; J2 l.1757-1759 "on the VALUE side (a default's value, a bound,
a set) a bare name is a BINDING and a label's value is read `$x`". joint_condition.md l.295 lists "a `$x` default that
can be absent" among the 12 new compile errors; rev 20 grep for it ("itself be absent", a `$x` default): 0 hits.
Ruling: FIXIND-6: the open item names one of two controls; the mark adds the same reach question plus whether the entry
and `$a` share ONE choice from DOM(a) (shared vs independent differ on 9 of 110 for `(a?: >7, b: >$a)`). Real.
CENSUS-9: by colon-scope (RULED) and the `=` row, `((h, m = $k): R)` parses with k's captured text as the default;
rev 20 never says what happens when k is absent or repeated, and the derivation's error for it was not carried. Real.
Expected fix: RIGHT for both (one line each in (e2) and §13: the mark's reach and witness-sharing as part of the same
open item; carry jc's "a `$x` default that can be absent" error or name the question). Note (V2/V9): under a chain DOM
with one choice per label per pass, "shared" is the natural answer, so FIXIND-12's scope-of-choice question and this
one should be put to the owner together, not as separate items.

### V13 — FIXIND-10
HOLDS.
Calls: `timeout 600 python3 -B -I R/fixind/fixind_drill.py` (D6) (rc 0, engine-run, 0 disagreements):
`[x = /\d/, y = /[a-z]/] & (x?: /[0-5]/)` read as `/(?<x>\d)|(?<y>[a-z])/`, 36 subjects: unmarked 6; marked with x
absent on a letter (DOM(x) = 0-9 holds 0-5) 32; marked with the y entry DROPPED 6.
Rev 20 quoted: l.1896-1897 "`[x = /\d/, y = /[a-z]/] & (x: /[0-5]/)` = `[0-5]` (the alternative lacking x drops,
§2.3) is unchanged"; l.1142 "An alternative of x lacking the label is DROPPED (with the `label.unset` warning, §4.2),
never an error"; L6 l.614 "an alternative lacking `a` is dropped by `&` with `label.unset`, an ERROR naming it under
`each`"; §5.4 `[ ]` row l.2434: the array "WRITES AN RX entry by entry ... Under `& | !` ... ANY ONE entry (of rx: an
alternation)", so the array and the rx are one pattern. RULED point (1) (l.1844-1845) lists "an alternative not taken"
as a cause of absence, and point (3) puts each control "over every absence".
Ruling: unmarked, "dropped" and "absent, FAILS" coincide (6 = 6), which is why the drop was harmless; marked, the
ruled text makes a letter an absent x that the mark accepts (32), while l.1896-1897 keeps the structural drop (6). The
example sentence was written for the unmarked case and is correct only there; the drop is a second absence mechanism
that the (*) principle and point (3) both overrule once a mark exists.
Expected fix: RIGHT: restate the drop as "x is absent in that alternative" (identical answers unmarked; the rule's
under a mark), at l.1897, l.1142 and L6; say whether `each((& (a?: d)), x)` is still L6's error on an entry lacking a
(by the restated rule it should not be: the mark accepts the absence), and whether the never-absent-mark warning
counts a label absent through an alternative (by "can never be absent", yes).

### V14 — RULING-4
HOLDS (as an ambiguity of the provisional wording; severity doc, as the critic rates it).
Calls: `timeout 600 python3 -B -I R/ruling/work/drill.py` DRILL 2 (rc 0, 0 disagreements): `(?<n>\d)+` vs
`\d*(?<n>\d)` over 84 subjects (alphabet 0379, length 1-3): match differ 0, PCRE-reported n differ 0; `(n: <5)` by the
sequence rule differs on 28 (`993`: iterations 9, 9, 3 vs the one 3). I checked the drill's iteration model: P3's
iterations are every digit (each pass of `+` sets n), P4 sets n once (the last digit): right.
Rev 20 quoted: l.1882-1883 "**mark-domain**'s \"two patterns that match the same subjects and set their labels the
same way answer every condition alike\" (*)"; l.2005-2006 "At the default level a repeated label follows the SEQUENCE
RULE: `x: S` constrains ALL iterations"; l.2001-2003 the iterations are "those of PCRE's parse"; CF l.1709 the owner's
own candidates "(graph, behavior, semantics, string set)".
Ruling: read as "the capture the match reports", (*) is contradicted by a ruled rule (28 of 84); read as "the same
value on every pass (every iteration)", it holds and agrees with the one reading (§4.5). Rev 20 does not say which;
that is precisely the asterisk's "needs adjustment" case, and nothing in rev 20 lists it. The critic is also right that
the owner's "string set" candidate, read literally, would collide with the ruled one reading (L60: two spellings of
one language answer differently by design), which is why the wording picks label behaviour.
Expected fix: RIGHT: one clause at l.591/l.1882 ("set their labels the same way: the same values on every pass, as PCRE
parses each") and one line saying why "string set" is not the reading (§4.5, L60); keep the asterisk. This also
sharpens V6 (loop-ness by behaviour) and V2 (DOM over PCRE's parse).

### V15 — RULING-7
HOLDS; the error tier can shrink further than RULING-7 says.
Calls: `timeout 600 python3 -B -I R/ruling/work/drill.py` DRILL 4 (rc 0, 0 disagreements): group `(?<a>a+)b(?P=a)`
whole-matched: `aaba` False, `aabaa` True, `aaabaaa` True, `ab` False; the whole `/(?<h>(?<a>a+)b\k<a>)?x/` on `<s>x`
agrees on all four.
Rev 20 quoted: l.1916-1921 "(a) DOM NOT EXACTLY COMPUTABLE ... The compiler takes an UNDER-approximation and an
OVER-approximation of DOM(h); where the condition's answer is the same under both, that is the answer; where it could
differ, a COMPILE ERROR on the mark naming the construct"; table row l.1931 "`(h?: \"aaba\")` | NO: the
over-approximation `a+ba+` holds it, the true domain does not | COMPILE ERROR naming `\k<a>`".
Ruling: rev 20 does not say how either approximation is formed, so the row's ERROR follows from one unstated choice
(an over-approximation that ignores the backreference). For a FINITE S, running h's group (in context) on each member
decides membership exactly, so under = over on that question and the answer is FAILS; the row's own text even states
the exact fact ("the true domain does not"). With the owner's "if it is possible", the exact answer is required where
it is this cheap. Strengthening (reasoning, not run): joint_condition.md §4H.1 classes RECURSION's value set as
context-free; for a context-free DOM and any REGULAR S, "some value of DOM in S" is CF-intersect-regular emptiness,
decidable; so for recursion the refusal tier is empty for regular S, and only backreference-built DOMs (not CF in
general) keep a real refusal case. (PCRE's priority/backtracking inside recursion may complicate the CF claim; that
caveat is SUSPECTED, unrun.)
Expected fix: RIGHT ("exact first": decide exactly where decidable, finite S by running, the row becomes FAILS; refuse
only where neither approximation settles it), together with SIMULATE-9's demand that the text say how UNDER is formed
(its bound otherwise decides compile-or-refuse). RULING-7's note on compile-time cost (an automaton per marked label vs
G2) is a fair addition, ungraded here.

### V16 — CENSUS-1, CENSUS-7
HOLDS (both).
Rev 20 quoted (CENSUS-1): §5.2 l.2333-2334 "a record inside that record would be a record used as a value, an ERROR
(`f((1, 2))`, §0.1 L45)"; §0.1 L45 l.653 "REV 20: `f((1, 2))` is ONE argument, a pair (a TUPLE, a value: **tuple-value**
CF 09:42, **tuple-anywhere** CF 09:49 ...); ... a LABELLED inner record `f((x = 1, y = 2))` stays the error"; §5.4
l.2439 "an argument (`f((1, 2))`: one argument, a pair)"; §5.2 STATUS l.2375 "the nested-record error ..." with no rev
20 qualifier. Two ruled-backed sentences give the same span two meanings, and §5.2 cites L45 for the reading L45
reverses. A stale unchanged rev 19 sentence.
Rev 20 quoted (CENSUS-7): §4.1 l.1728-1732 "REV 20: NO EXCEPTION. Rev 19's one exception (a macro parameter bound to a
FIELD REFERENCE standing on the left of `:`) is PAUSED ... on the left of `:` every name is a LABEL of the pattern the
condition meets ... (RULED, **colon-scope**, CF 11:32)"; §16.2 l.5388 "a parameter bound to anything but a reference
(... the error names the parameter)" (PAUSED text); §4.2 (e3) l.1964-1967 "there is no label parameter in rev 20 ... A
PER-LABEL mark on a passed condition has no spelling: OPEN". Grep of rev 20 for an unused-parameter or shadowing
diagnostic in the live language: none (the shadowing hits, l.491/l.832/l.5100/l.5342, are the paused sigil's record).
So `opt_lt(k, n) := (k?: <n)` compiles with the left `k` read as the pattern's label k, the parameter k never read,
and `opt_lt(x, 5)` silently tests k. By the text, CONFIRMED; no run possible (nothing built).
Expected fixes: CENSUS-1 RIGHT (narrow §5.2 to the LABELLED inner record, as L45 and §5.4 l.2436 do; fix l.2375).
CENSUS-7 RIGHT in substance; of its two forms the ERROR is better than a warning ("a parameter name on the left of `:`:
the left of `:` names labels (colon-scope); a per-label mark through a macro has no spelling, §13"), since a body
that names a parameter there can only be a slip while the field reference is paused; a general "parameter never read"
warning would catch it too but is a new member (trigger: FIXIND-11's family).

### SUMMARY
All drills re-run under `timeout 600` with `python3 -B` (no bytecode written outside verify/): d1, d2, d3, d5, d6,
fixind_drill.py, ruling drill.py: every rc 0, every engine-disagreement count 0, every printed number equal to the
critics' claims. Outputs: R/verify/run_*.out; my one extra probe: R/verify/work/v4_define.py.
HOLDS: V1, V4, V6, V7, V8, V10, V12, V13, V14, V15, V16. PARTLY: V2 (SIMULATE-2 overstates "already forced": a chain
reading keeps (*) and rev 20's stated `b` HOLDS; match-context stays an owner question between chain and context),
V3 (rev 20's three-item list is right as the NON-REGULAR list; the fix is "compute exactly in context", not "refuse
more"), V5 (SIMULATE-7's "`<0` is empty" is false, numerals may be signed; the ERROR still follows from §5.2's empty
INTERSECTION), V9 (cell is ERROR not FAILS for constants; the split vanishes under V2's chain DOM), V11 (FIXIND-5 (c)
overstated). Cross-finding: V2's chain DOM (over the program's h-present matches, other conditions applied) also
dissolves FIXIND-3 and bears on FIXIND-6/12: put them to the owner as one question.
VERIFY COMPLETE
