# VERIFY: predspec23

## Items


### V-1 RULING-1 + MODECLOSURE-6 + SIMULATE-2 (the complement's left operand)
(a) HOLDS. rev23:425-426 cites 20:41 ("The table is the source of matches. Like the text for a pattern.") then says
"it is what PRODUCES the table from the text". CF:1900-1901 (20:36 RECORD): "the TABLE is what it produces, the set of
matches"; CF:1916-1918 (20:41): "the TABLE is the SOURCE the statement runs over ... (NOT the set of matches, as his
first message and the manager's entry above had it)". Mitigation the critic also notes: CF:2018-2019 (23:31, his
remark, not a ruling) "the table is the set of possible matches" and CF:2039-2040 (23:46 RULING) "a ROW of the table
is ONE POTENTIAL MATCH" give the per-pattern table a later basis; the defect is the citation (20:41 for its opposite).
(b) HOLDS. Reason at rev23:444-445 "the reason in the model's words: a complement's rows are rows of its LEFT operand"
is the manager's (no owner entry states it). dispositions.md A5: "FIX-NOW (rev 23 text), manager's call, owner told |
keep the standalone-complement error, reason in the model's words, unless A1's answer gives the row a span". CF:2050
(23:46): "Review r31 finding A is closed by this ruling"; CF:2039-2040 a row is "a stretch of the text". Rev 23
(rev23:444, rev23:704 "A5 the standalone-complement error kept") never mentions the condition.
(c) HOLDS (with a weight note). CF:2047-2050 (23:46, MINE): "\"the text contains no B anywhere\" is a separate,
whole-text question needing its own spelling (a complement with nothing on its left, or not-contains), to be stated
in rev 23 and shown to him." R.8 item 1 (rev23:793-803) shows routes (i) lookahead and (ii) text.none only; the first
candidate appears only as "A standalone `!B` is the compile error of §R.1.4" (rev23:610). Note: both MINE and A5 are
the manager's items, so "decides the owner's parked question" overstates it; it is a presentation gap (the record's
own candidate is not shown to him), design/doc.
(d) HOLDS. R.1.4 defines `!P` only "used AFTER `&`" (rev23:440) with the reason "with nothing on its left there is no
row" (rev23:445); `!q & t2` matches neither the defined form nor the listed error spellings (`${!B}`, `C | !B`, "a
program that is only `!B`"). L1 (rev23:1353) "`a & b & c` in any order"; L39 (rev23:1391) `A & B` vs `B & A` SAME;
§2.2 (rev23:1890-1891) "the ORDER and GROUPING of an `&` chain never change which strings it admits". No sentence
assigns `!q & t2` a meaning or an error (grep "nothing on its left": rev23:443, 1908 only).
(e) HOLDS (doc). rev23:2045 "`$m !~ r` is `(m: !contains(r))`"; R.1.1 (rev23:409) puts a `label:` set among nested
programs; R.1.4 (rev23:443-444) "a program that is only `!B`" is the ERROR; §2.2 (rev23:1903) lists `!contains(r)`
as a PATTERN. Nothing says `label:` supplies the left operand. Answers not run (the conflict is textual).

### V-2 RULING-2 (whole-text "PARKED 2026-11-17, 'Let's not answer now'")
HOLDS. `grep -n "not answer now" COND-FAMILY.md` -> 0 hits; the record ends at CF:2065 (23:48 entry; `wc -l` 2065);
its last PARKED entries are CF:795, 1433 (other topics). Rev 23 uses the quote at rev23:625-626 ("the owner PARKED
it on 2026-11-17 (\"Let's not answer now\", as relayed in the predspec23b brief)") and rev23:793 (no relay
qualifier at all there). R.11 rev23:998: "the whole-text question | OPEN: **whole-text** (§R.8) | 23:46 (\"MINE\")",
no parking. So the owner quote has no record entry, R.8 states it unqualified, and R.11 disagrees with §R.4/§R.8.
Severity doc/process as filed.

### V-3 RULING-3 (spelling principle restated through the 20:36 consequence)
Text: HOLDS. rev23:426-427 "two patterns with the same table answer every condition alike (the spelling principle,
15:29, restated)" = CF:1905-1906 (20:36, MANAGER's consequence (1)): "two statements with the same table answer
every condition alike"; CF:1919-1921 (20:41): "derived under the first wording and are NOT carried: the definition
lane re-derives them". Ruled (*) wording CF:1721-1725: "two patterns that match the same subjects and set their
labels the same way answer every condition alike" (*), "the sentence carries an asterisk wherever it is quoted";
R.1.3 drops the asterisk (rev23:1330 keeps it). rev23:1319-1320 "MEANING, NOT SPELLING now holds BY CONSTRUCTION".
Answer split: NOT FOUND for answers; compile-status split not verified. Run (v1.py, engine imported read-only): pair
`/(?:(?<h>\d);)+/ & /\d;/` (passes table, Kleene AND) vs `/(?<h>\d);/` (set-once) over 341 texts {3,7,;,x}<=4:
`(h: <5)` differ [WHOLE 0, SEARCHED 0]; `NOT (h: <5)` differ [0, 0]. The critic's hypothesised split runs through
compile rules keyed on repeatedness (sibling-loop error, group-question legality, `$h` sequence rule), which the
engines do not model: not verified. So "narrower than (*)" holds as a textual fact (a table carries the pass table,
R.1.2/R.1.8), but no answer split was exhibited; the "by construction" claim stands unproven rather than refuted.

### V-4 RULING-4 (G23-2 vs §R.8; G23-1's cite)
HOLDS. G23-2 rev23:383 "every reading this lane had to take is marked \"the draft's reading\" and listed (§R.8)". R.8
(rev23:791-824) has four items: whole-text, pass-table, group-truth, lookahead-labels. Not in R.8: (a) rev23:459-461
"Kleene AND over the pass rows ... THE DRAFT'S READING of the three-valued form"; (b) rev23:530 "on CONDITIONS
Kleene OR (the draft's reading ...)" (listed in R.11 rev23:1015 only, not asked); (c) rev23:497-498 repeated-means
"the MANAGER's ruling, told to the owner by name" (= CF:1997-1999, MANAGER RULING). G23-1 rev23:382 "the coverage
table §R.1.9"; the coverage table is R.1.11 (rev23:513); R.1.9 is "HOW A PROGRAM REPORTS" (rev23:501).
By hand, `NOT ((h: S) | (k: T))`, row with h absent, k FALSE: Kleene: U OR F = U; NOT U = U -> row dropped.
Two-valued (absent = FALSE, rev 22's "fails"): F OR F = F; NOT F = T -> row kept. Split confirmed; it exists only
because NOT is new (rev 22 made `!` on a condition an error), as the critic says. Also by hand for (a): `7;;` under
R.1.5: passes {7: FALSE, absent: U} -> Kleene AND FALSE -> NOT TRUE (HOLDS, = rev23:578); the alternative "a pass
lacking h makes it UNKNOWN" -> NOT U = U -> dropped. Split confirmed.

### V-5 RULING-5 + FIXINDUCED-1 (default.unused (b) under NOT)
HOLDS. §7.1 rev23:3447-3451: "`default.unused` (rev 20: a label's default that can never change an answer: (a) the
label is never absent where the condition reads it, (b) the default's text is outside every set it meets; ... rev
23: a default may be any text, default-value 21:49, and the warning is the one on a default that can never be
USED)". Record CF:1486 (11:05) asked "a default that can never change an answer, the label never unset or the
default outside the set"; CF:1961-1962 (21:49) "a warning only on a default that can never be used". Run (v1.py,
predspec23_model imported read-only), `/(?<h>\d)?x/`: on `x` `NOT (h: <5)` FAILS / FAILS, `NOT (h = 9: <5)`
HOLDS / HOLDS `x`@0; over SVPOOL (341) differ [WHOLE 1, SEARCHED 164] (= the critic's 1 / 164; = rev23:564's `x`
row). 9 is outside `<5`, the only set it meets, so (b) fires on a default that changes the answer.

### V-6 RULING-6, RULING-7 (a)-(e), RULING-8 (quote checks)
RULING-6 HOLDS. CF:1550-1552 (12:45 RULED): "a label outside the pairing loop is tested once even when the loop runs
zero passes (`9` FAILS ...); the draft's equality ... holds at every depth"; CF:1552-1555 "THE MANAGER'S WORDING
(his \"agree\" covers the answer; the wording is the manager's ...): ... ONE tuple whose looped parts are EMPTY";
CF:1674 (14:31) REVERSES "the manager's 12:45 zero-pass wording (the ANSWER `9` FAILS and record = & are kept)".
`grep -n "LEFT JOIN" COND-FAMILY.md` -> 0 hits. Rev 23: rev23:418-419 "(the LEFT JOIN row of zero-pass-record,
12:45)", rev23:419-421 R1 "HAS NO OWNER RECORD", R.11 rev23:1008 "zero-pass-record (the LEFT JOIN row) | STANDS |
12:45".
RULING-7: (a) HOLDS: CF:1885-1886 "nothing ruled; item 11 holds the manager's judgment given to him and parks the
remark"; R.11 rev23:1016 "ANSWERED by default-value (any text) | 21:49" (21:49 entry CF:1961-1962 does not name
17:02). (b) PARTLY: CF:1922-1924 "THE MANAGER'S JUDGMENT given to him ... it makes a complemented pattern carry NO
labels"; rev23:440 says "(20:41's judgment, held by r31)" -- it does say "judgment", not "his words", so only the
bare-time cite is loose; §2.2 rev23:1905 "with no labels (20:41)" is the bare cite. (c) HOLDS: rev23:2674 "Two
tests may give one label different defaults (BY DESIGN, 22:30; §R.5 E)"; CF:1980-1982 "As put to him before he
answered: two different defaults on one label stay legal". (d) HOLDS: CF:1662 "(2) ONE READING: a condition needs a
text; on an absent label it FAILS"; R.11 rev23:999 "STAND (LOCKED)" with no note of the three-valued re-reading
(CF:2056 23:48 "unknown"). (e) HOLDS: CF:1976-1980 "THE READING THE MANAGER TOOK of \"yes per test\" ...: the
per-ENTRY form ... (a2) ... so a record is exactly the AND of its entries"; R.11 rev23:987 "`$a` reads the real
label (per entry, (a2)) | RULED" (the question as asked, CF:1974, did name `$a` reading the real label).
RULING-8 HOLDS. CF:1891-1893: his words "... we might put together @compiler.warn(cond, ...)"; "the sketch (a
placeholder spelling, D193 add. 4): `@compiler.warn(cond, \"! In none\")`". rev23:1277 quotes as his words
"If there is a way to describe it, we might put together @compiler.warn(cond, \"! In none\")".

### V-7 MODECLOSURE-1 (modes of a `records` item and a `contains`/`occurrences` argument)
HOLDS. R.1.1 rev23:409-410: "In a filter role (either side of `&`, a `label:` set, a `contains`/`occurrences`
argument, a `records` item) the text is that role's STRETCH (rev 22 §11 THE ROLE TABLE: a filter role matches its
stretch whole)"; R.1.3 rev23:427-428 "A WHOLE-VALUE program (a filter role; ...) has ... at most the rows whose
stretch is the whole text". THE ROLE TABLE rev23:3855 "the FILTER ROLES are rows 1-4"; row 7 rev23:3865 "a
`records` item rx | no | its file text (searched, §7)"; rev23:3849-3850 "the argument of ... `contains` ... and
`occurrences` lands in a hole of the body"; row 5 rev23:3863 "a hole never opens one". D11 R.11 rev23:997
"`t2 & contains(t2 & !q)` on `9:30` HOLDS / HOLDS, its hit `9`" (a sub-stretch, so the argument is not matched
whole). Whole vs searched of `t2 & !q` on `9:30`: rev23:600 "WHOLE FAILS / SEARCHED HOLDS `9`@0" (PART 1, D1), so
the place's mode decides the answer. Not separately re-run (both facts are stated lines of the subject + PART 1).

### V-8 MODECLOSURE-2 (hits over a FILTERED argument)
HOLDS. R.1.9 rev23:506-508 "leftmost, non-overlapping find-all, as `records` and `occurrences` already work";
§2.6 rev23:2049 "The hits are those of PCRE's OWN matching of the body"; R.4.1 rev23:637-638 a hole holding a
program with conditions is "its STRING SET". Runs: (v1.py, predspec23b find-all) `/(?<n>\d+)/ & (n: <100)` on
`1234` -> [`12`@0, `34`@2]; on `123456` -> [`12`@0, `34`@2, `56`@4]. (v3.py, own: the string set {0..99} spliced
as `[\s\S]*?(SET)` repeated) shortest-first `1234` -> ['1','2','3','4'], longest-first -> ['12','34'];
`123456`: 6 vs 3. So the hole/string-set reading is order-dependent and agrees with R.1.9 only for one order.

### V-9 MODECLOSURE-3 ("adding a condition never admits" unscoped in §4.2)
HOLDS. rev23:2675 "\"Adding a condition never admits\" holds in both modes (§R.5 A4)." (no insertion point);
R.5 A4 rev23:697-698 scopes it "at the top of an `&` chain AND through a twice-used program". Run (v1.py):
`/(?<n>\d+)/` find-all on `1234` [`1234`@0]; with `(n: <100)` [`12`@0, `34`@2] (row `34`@2 newly reported); on
`123456` 1 -> 3. Positive polarity, no NOT. (The `occurrences(..., min = 2)` consequence rests on V-8's find-all
reading of the hits.)

### V-10 MODECLOSURE-4 (NOT over a nested `label:` program)
HOLDS on the answers; PARTLY on "contradicts the promise". Run (v1.py, X = `/(?<x>[\d:]+)/`, q = `t2 & late`,
`(x: q)` read as membership of x's value in q's whole-value rows): on `9` `X & NOT (x: q)` HOLDS / HOLDS `9`@0;
flat `t2 & NOT late` FAILS / FAILS; on `9:15` both HOLD; on `9:30` X-form FAILS / HOLDS `9:3`@0, flat FAILS / FAILS.
Text: rev23:403-404 "A missing label never passes a test, negated or not". The outer row's label x is present; the
missing label is q's inner m, so the sentence is literally about the row's labels and not falsified; but the
behaviour (NOT over a nested program keeps an inner-absent row, i.e. acts as difference) is not in §R.3's table
(rev23:550-554). Design/doc as filed is fair; "false" is too strong.

### V-11 MODECLOSURE-5 + FIXINDUCED-4 (`|` of FILTERED branches)
HOLDS. Grep rev 23 for "next branch|fall(s) through|fallthrough|filtered branch|of filtered|branch it took":
only rev23:437 ("with the labels of the branch it took") and rev23:970 (§R.10 evidence description "`|` of
filtered patterns"); no rule stated. The engine (predspec23b_model.py:50-51, `accept` with `alt`: "branch 1
first, the next branch when its filters reject") implements fallthrough. Run (v1.py, when body
`(t2 & c & p) | (t2 & !(t2 & c))`, c = `(h: <5)`, p = TRUE, WHOLE): `3` True/True; `7` fallthrough True, no
fallthrough False; `12` True/False. With no fallthrough the else branch is unreachable, so A3's "agree"
(rev23:701-703) depends on the unstated rule. `5;1;9` (KH, c = `(h: <5)`, p = `(k: between(3, 7))`) SEARCHED:
engine end-major reports `5;1;9` (0, 5); branch-major `5;1` (0, 3). §8 rev23:3572-3573 "`x & when(c, p)` =
`(x & c & p) | (x & !q)`" carries no mode. Which order is "PCRE's one parse" for filtered branches is undecided by
the text; the split itself holds.

### V-12 MODECLOSURE-7 (nullable B in text.none / !contains)
HOLDS (maintenance; no stated count moves). Engines: predspec23_model.py:154,156,169 and predspec23b_model.py:306,311
all use `for l in range(k + 1, ...)` (non-empty stretches only). Run (v1.py, B = `/(?:(?<n>\d),)*/ & (n = 9: >=5)`,
Kleene AND over passes): text.none by the definition (empty rows included) FALSE on '', '1,', 'a'; the engine's
form TRUE on all three. Every stated count uses q = `t2 & late`, and t2 needs a digit, so q is not nullable: no
stated count moves. R.6 (rev23:738-748) does not list the case.

### V-13 FIXINDUCED-2 + SIMULATE-5 (live "a condition is a macro" / pointwise `!M`)
HOLDS. Live sentences: rev23:1796 "There is no third value kind: a CONDITION is a macro"; rev23:1823-1824
"operators on macros are POINTWISE (`M & N`, `M | N`, `!M` filter as both, either, neither; rev 22: `!M` only where
M is not a CONDITION ...)"; rev23:1872 "STATUS. Two kinds (rx, macro), a condition is a macro: RULED (CF:858";
rev23:1897 "Macros in the filter role combine pointwise by `& | !`"; rev23:2627 "A condition is a MACRO (§2.1)";
L46 rev23:1398 "a condition is a MACRO, a value"; O45 rev23:4980 "The ruling says a condition is a macro";
also §5.4 rev23:3164 "a CONDITION, i.e. a MACRO (CF:858)". Against R.1.11 rev23:521 "no longer \"a macro
(CF:858)\" (19:31 supersedes CF:858 ...)" and R.9 S056 rev23:877 "STANDS". Run (v1.py, `/(?<h>\d)?x/`): pointwise
"neither" `P & !(P & (h: <5))` on `x` HOLDS / HOLDS; `NOT (h: <5)` FAILS / FAILS; differ over SVPOOL [1, 164]
(= §R.3 rev23:569). §R wins by its header (rev23:360), so the answer is fixed; the defect is live contradicting
text (doc, or design for the macro-parameter case the critic names, not run).

### V-14 FIXINDUCED-3 (H's "the program's regex" qualifier dropped)
HOLDS. rev22:2301-2302: "Where no match of the program's REGEX (its `&` operands, conditions not applied) sets a
label ... a COMPILE ERROR". Rev 23: rev23:727 "a condition or a default on a label NO MATCH OF ITS REGEX CAN SET";
rev23:2611, 2672 same; rev23:2672-2673 and rev23:544 "the per-label regex value set" / "the values the label's
own regex can give". Run (v1.py, `/(?<o>\d)x|y/ & /y/`, pool SVPOOL + {1,y}^<=3): with `(o = "1": <5)` vs
without: differ [WHOLE 0, SEARCHED 0] (plain holds W 1 / S 11: constant TRUE wherever the program holds);
`(o: <5)` holds 0 / 0. Caveat: "its regex" at rev23:727 is ambiguous ("its" = the label's or the program's), but
§R.2 and the per-label wording favour the critic's reading.

### V-15 FIXINDUCED-5 + SIMULATE-3 + SIMULATE-4 (the §5.2 empty-intersection error)
HOLDS (all three, by the text). §5.2 rev23:3090-3091: "At NARROWING SITES (condition literals, ...) an empty
intersection from pure parts is an ERROR"; §R.2 rev23:543-544 "STAYS, read from the values the label's own regex
can give ... `(n: <0)` on a digit label is still the error"; R.1.11 DOM row rev23:536 same; no sentence says a
default's text joins that value set (grep "default joins|value set.*default": none; S115 rev23:928 "read with a
default, §R.1.6" is about history sites). Runs (v1.py): `NOT (n: <0)` on `/(?:(?<n>\d),)*/`: `` FAILS / FAILS,
`3,` HOLDS / HOLDS, `3,7,` HOLDS / HOLDS (non-constant, yet contains the erroring literal `(n: <0)`).
`occurs.none((h = "x": !<10))` on `/(?:(?<h>\d)?;)*/`: `` HOLDS / HOLDS, `;` FAILS / HOLDS, `7;` HOLDS / HOLDS
(non-constant; `!<10` meets no digit, so the error as written applies). L30 (rev23:1382 "SAME on a set-once label"):
empty S: `NOT (x: <0)` holds the literal `(x: <0)` (error) while `(x: !<0)` meets every digit (legal); full S:
`(x: !<10)` meets no digit (error) while `NOT (x: <10)` is legal and never TRUE. Derived from the text; no compile
check exists to run.

### V-16 SIMULATE-1 (L83 SAME under NOT; closing example)
HOLDS (counts differ from the critic's; direction and key cases confirmed). Run (v1.py, t2, S = `<9`, T = `<30`,
the engine's canonical-numeral `<n`): on `10` `t2 & NOT ((h, m): (S, T))` FAILS / FAILS, `t2 & NOT (h: S, m: T)`
HOLDS / HOLDS `10`@0; differ over T2POOL (11,110) [WHOLE 101, SEARCHED 281] (critic: 92 / 470 with its own
evaluator; set readings of `05`-style minutes differ); without NOT differ [0, 0]. Text: R.1.5 rev23:456-458 (joint
UNKNOWN if any part absent) and rev23:463 (record = `&` of entries) vs L83 rev23:1435 "SAME | the record IS the
product". Closing example (v2.py): record twin `occurs.none(NOT (h: <10, m: <30))` WHOLE holds 40, I1 differ 25,
I2a differ 45 (first `12,`), I2b differ 0; committed out line 107: `occurs.none(NOT ((h, m): R))` WHOLE holds 85,
I2a differ 0. So the joint form is EXACT on I2a and its L83 twin is EXACT on I2b, as the critic says.

### V-17 CHANGETABLE-1, CHANGETABLE-2 (spot checks)
CHANGETABLE-1 HOLDS on 3 of 3 sampled ranges. (1) rev22:650 "run under the program DOM (§4.2 THE CANDIDATES); ..."
-- sites.tsv `S021 651` and R.9 rev23:850 `| S021 | 651 |`: 650 not cited. (2) rev22:2265 "(e2) is answered for a
`$a` on the condition's own labels by the manager's derivation (16:23)" -- S092 is 2234-2257, S093 2269-2299
(rev23:907-908): 2265 in neither (both rows say §4.2 MOVED verbatim to §16.4, so it is handled in substance, as the
critic says). (3) rev22:3406 "every component is read (§2.4, DOM)" -- S126 is 3409-3419 (rev23:936): not cited.
The defect is citation completeness against the "every site" claim (doc).
CHANGETABLE-2 HOLDS on 2 of 2 sampled bullets. rev23:5705-5707 **zero-pass-empty** "F1 is the mark's one meaning
... `(h?: <$a, k: 3)` on `0-3` FAILS" and rev23:5717-5719 **mark-under-not** "`!` takes a pattern or a set, never a
condition (§2.2)" carry no inline [REV 23] note, while rev23:5750-5752 and rev23:5756-5757 do; the retirement is
only in the trailing block from rev23:5761. Doc severity (rev23:375 allows dated history labelled "where it
stands"; these are labelled only by the later block).

VERIFY COMPLETE
