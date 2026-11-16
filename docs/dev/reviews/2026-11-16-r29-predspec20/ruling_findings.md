# CRITIC RULING: predspec20 findings

## Findings

### RULING-1 — F1 makes a ONE-label marked condition FAIL where the ruled point (3) says it is "satisfied"
CONFIRMED (quoted lines). Ruled text, rev 20 §4.2 l.1847-1849 quoting CF 14:31 verbatim: "the OPTIONAL MARK ...: absence
is acceptable, the condition is satisfied; in a joint condition a marked absent label reads 'some value would put the
tuple in the set'". So for ONE label the ruled sentence is unconditional; F1 was ruled only for the joint case. Rev 20
l.1878 extends F1 to one label ("the joint sentence's k = 1 case ... the manager's reading 14:50 (b), in every
shape"), and with DOM (15:27 reading (3)) its own worked rows then FAIL a marked absent single label: l.1958
`(mnum?: >5)` FAILS; l.1927 `(h?: /a+b/)` FAILS; l.1928 `(h?: !/a+ba+/)` FAILS; l.2039 `all((n: <0))` = `(n?: <0)` FAILS.
Expected by the ruled sentence: HOLDS in all four. The 14:50 (b) justification ("for one label with a non-empty set
that is the same as 'satisfied'", CF:1689) is false once DOM is the domain (needs S ∩ DOM(h) non-empty, not S
non-empty) and false for a MATCH-DEPENDENT S: drill `ruling/work/drill.out` DRILL 3, `/(?<k>\d+);(?:(?<n>\d),)*/`
with `(n?: >$k)`: on `50;` n is absent (PCRE2 and `re` agree), DOM(n) = 0-9, no value > 50, so F1 FAILS; on `5;` it
HOLDS. A non-constant answer the ruled sentence does not allow. The owner's pending question **zero-pass-empty**
(l.1951) covers only the EMPTY-set corner, so his assent there would not cover this departure.
Manager's reading attacked: 14:50 (b) + 15:27 (3). Severity: design (a manager's reading contradicting a ruled
sentence the draft quotes). Effort: small (one owner question, slug e.g. **mark-one-label**: "satisfied" outright vs F1,
with the four rows above as witnesses; or restate point (3) as departed-from pending his word). Blast radius: §4.2
(AR) cell, (d), (e1), §4.3 `all` row, L82, L93. Rev 20 §4.2 l.1843-1879, §0 row 547 (b).

### RULING-2 — `all(c)` = "c with every label marked" is no longer "every, possibly none"; labelled RESTATED, not changed
CONFIRMED. The manager's 14:31 reading of "lock" (CF:1670-1671): "`all(...)` over no values HOLDS (the spelled-out
'every, possibly none')"; 14:50 (a): holds "for EVERY absence alike". Rev 20 (r28 C) defines `all(c)` as c with every
label marked, read F1 (l.2033), and calls this RESTATED (row 546 "the first and last RESTATED"; row 547 (a)). It is a
change of answer, not a restatement: (i) `all((n: >$k))` over `/(?<k>\d+);(?:(?<n>\d),)*/` on `50;` (zero passes,
DRILL 3) FAILS under rev 20 and HOLDS under the 14:31 reading, a match-dependent split, not only the constant
empty-intersection corner jc §4H.3 counts (1 of 1,111, `all((n: <0))`); (ii) rev 20 still says the old thing in two
places: l.2110 "('every, possibly none' is `all`, rev 20)" and l.1353 "'Every hit, possibly none' is written with
the mark, `(g?: "x")`, or `all((g: "x"))`". (iii) Consequence against the owner's SAVING PEOPLE criterion: since `all`
marks EVERY label, it also relaxes a missing field INSIDE a present item, so "every item complete, possibly no items"
(the common list idiom) has no `all` spelling: on `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/` the author's natural
`all(((h, m): R))` silently accepts `5,` (no minutes); the only spelling is `occurs.none(((h, m?): !R))` (l.2040-2041),
a double negation through a count. L36 classes the split BY DESIGN, but a BY DESIGN row is "a mark's stated
meaning"; `all` is a group question, and the silent acceptance is not listed as silent (§0 criterion row l.593's own
checkable form).
Manager's readings attacked: 14:31 (first sub-choice), 14:50 (a) and (f). Severity: design (answer change under a
reading told to the owner, not put back to him) + doc (l.2110, l.1353, rows 546-547). Effort: small-medium: relabel
as CHANGED with the `50;` witness; fix l.2110/l.1353; put "is `all` the vacuous 'every, possibly none' or 'every
label marked'" to the owner beside zero-pass-empty. Blast: §4.3 table, L36, L93, §4.2 (c), (f).

### RULING-3 — 15:23's "upper bound 1 is not a loop" reads the SPELLING; it breaks the ruled mark-domain principle
CONFIRMED (drill). The ruling is "`x?` and `(?:x|)` answer alike" (CF:1698-1699); the HOW is the manager's: "a
quantifier with upper bound 1 is NOT a loop" (rev 20 l.2074-2079, L94; loop = `*`, `+`, `{n,m}` m >= 2: a syntactic
list, also l.2021-2022 for "repeated label"). That only reconciles the two spellings jc §4H.5 tested, both of upper
bound 1. A loop that can run at most once BY MEANING is still a loop by the list: `ruling/work/drill.out` DRILL 1,
P1 = `(?<k>\d)?-(?<h>\d)?` vs P2 = `(?:(?<k>\d)(?=-))*-(?:(?<h>\d)(?!\d))*`, whole match over 781 subjects (alphabet
`059-a`, length 0-4): 0 match differences, 0 capture differences (libpcre2-8 10.46 and Python `re`, 0 engine
disagreements). Under rev 20, `P1 & (h: <5, k?: between(3, 7))` answers (L94) while `P2 & (...)` is the SIBLING-LOOPS
COMPILE ERROR (h and k in sibling `*` loops, l.2063), and a bare `$k` on P2 is the repeated-label error at the default
level (l.2006-2007) while on P1 it reads. Expected under **mark-domain** (RULED 15:27) and its provisional wording (*):
"two patterns that match the same subjects and set their labels the same way answer every condition alike" (*): the
same answer. "If it is possible": it is (whether a group can be set twice in one match is decidable for a regular
pattern by its automaton).
Manager's reading attacked: 15:23. Severity: design (contrived spelling, but the principle is ruled and this is the
rule that the principle was invoked to settle). Effort: small to state: "a loop for the pairing rule and for 'repeated'
is a group that can be set more than once in some match" (meaning, not quantifier), or record the syntactic list as
the principle's named exception under "if it is possible" with the owner. Blast: §4.3 pairing rule, repeated-label
definition, L94, §7.1 sibling-loop text.

### RULING-4 — the provisional wording (*) is false of the ruled sequence rule if "set their labels" means PCRE's capture state
CONFIRMED (drill). The wording (*) (15:27 reading (1), agreed provisionally 15:29; rev 20 l.550, l.591, l.1882):
"two patterns that match the same subjects and set their labels the same way answer every condition alike" (*). Read
as a user reads PCRE ("set" = the capture a match reports), it is contradicted by the RULED sequence rule (CF:583; rev
20 l.2005, a plain condition tests EVERY iteration): `ruling/work/drill.out` DRILL 2, `(?<n>\d)+` vs `\d*(?<n>\d)`:
84 subjects, 0 match differences, 0 differences in PCRE2's reported n; `(n: <5)` by the sequence rule differs on 28
(`993`: iterations 9,9,3 FAIL; one iteration 3 HOLDS). The wording holds only if "set their labels the same way" means
the same PER-PASS values (every iteration of every label), which rev 20 never says. Also unstated: the owner's own
candidates were "(graph, behavior, semantics, string set)"; the wording picks label behaviour, and so keeps the ruled
ONE READING (§4.5, l.577: "a condition on a label reads the spelling's parse") consistent with it; a "string set"
reading would collide with §4.5. Both are exactly what the asterisk is for, and rev 20 lists neither as a candidate
adjustment.
Manager's reading attacked: 15:27 (1). Severity: doc (the asterisk's "needs adjustment" case, found). Effort: one
sentence at §0 STANDING CRITERIA: "(*) 'set their labels the same way' = the same values on every pass"; one line
naming §4.5 as the reason "string set" was not the reading. Blast: §0 l.591, §4.2 l.1882.

### RULING-5 — the withdrawal of "any text" is attributed to the owner's principle; the record says it is the manager's judgment
CONFIRMED (quoted). Record, CF 15:27 reading (3) (CF:1714-1715): "'any text' also ignores spelling but stays withdrawn
on the round's own ground (a value the label can never hold witnesses an answer), which is the manager's judgment, not
his". Rev 20 l.1987: "The manager's 14:50 (c) (the mark ranges over ANY text) is WITHDRAWN by **mark-domain**
(15:27)"; row 547 (c) "(WITHDRAWN 15:27)"; jc §4H.7 row (c) likewise. Expected: "WITHDRAWN (the manager's judgment,
review r28 A; **mark-domain** does not decide between 'any text' and DOM, both ignore spelling)". A manager's choice
presented as following from an owner ruling, which shields it from his review. l.1876-1878 states the 92-vs-2 drill
as the reason, correctly, but does not say whose judgment it is.
Manager's reading attacked: 15:27 (3). Severity: doc (status). Effort: trivial (three places). Blast: none beyond
labels.

### RULING-6 — two more status labels overstate or misstate: row 546 "RESTATED" (a reversal) and l.2117 "RULED in effect"
CONFIRMED (quoted). (a) Row 546: "the manager's 14:31 readings (... a marked absence not counted): the first and last
RESTATED, below". The last is REVERSED twice (14:50 (d) made it an error; r28 E made it COUNTED: rev 20 l.1900, l.2034,
row 547 (d) "WITHDRAWN: a marked absence COUNTED"). Expected: "the last REVERSED (counted)". (b) §4.3 STATUS l.2117:
"`?` not a loop for it: RULED in effect (**optional-as-loop** CF 15:23), the 'how' the manager's reading". The ruling
is only "answer alike" (CF:1699); "`?` not a loop" IS the how, and it is not the only how (RULING-3: a meaning-based
loop also makes them answer alike). The changelog l.23 and l.2074 label it correctly; l.2117 does not. Expected: "`?`
not a loop: the manager's reading of how (CF 15:23)".
Severity: doc. Effort: trivial. Blast: labels only.

### RULING-7 — 15:27 reading (4): the worked row `(h?: "aaba")` draws a COMPILE ERROR where the exact answer is computable
CONFIRMED (drill). Rev 20 §4.2 (a) l.1916-1931: DOM "not exactly computable" -> under/over approximation, error where
they differ; worked row `(h?: "aaba")` -> "COMPILE ERROR naming `\k<a>`". But for a FINITE S, membership of each member
in DOM(h) is decided exactly by running h's own group on it: `ruling/work/drill.out` DRILL 4, group `(?<a>a+)b\k<a>`
(as `(?P=a)`, accepted by both engines): `aaba` not a value, `aabaa`, `aaabaaa` values, `ab` not; the whole pattern
`/(?<h>...)?x/` agrees on `<s>x`. So `(h?: "aaba")` FAILS exactly; the owner's qualifier "if it is possible" (CF
15:27) says to use the meaning wherever possible, and here it is. The error tier should be confined to the cases where
the exact question is not decidable or not cheap (an infinite S against a non-regular DOM), and the rule should say
"exact first". Also unstated: the compile-time cost of computing DOM(h) (an automaton per marked label) against G2
and the class-count pricing of §4.6.
Manager's reading attacked: 15:27 (4). Severity: design (minor; one corner, an unnecessary error, no wrong answer).
Effort: small (one sentence + the row's verdict to FAILS). Blast: §4.2 (a) table.

### RULING-8 — "his criteria (G1-G4, Goals)" points at the MANAGER'S goals; the 00:31 "test of the language" criterion is missing; rank provenance contradicts the note
CONFIRMED (quoted). (a) Rev 20 §0 row 518 (00:31): "his criteria (G1-G4, Goals)". In rev 20, "Goals" G1-G4 are
EXPRESSIVENESS, LINEAR, PCRE COMPATIBILITY, STRUCTURE (l.571-574), headed "MANAGER DRAFT" (l.565); his 00:31 criteria
are joint_condition.md's G1-G4 (jc l.66-73), a different table. A reader of rev 20 alone attributes the manager's draft
goals to the owner. (b) The 00:31 record's criterion (2), "the tuple compare matters as a TEST of the language, not for
itself" (CF:1347-1348; his words "it tests the language on an interesting problem"), has no row in rev 20's STANDING
CRITERIA (l.588-594): the row there merges "in line with existing concepts" and "helps the larger language" only.
(c) Rank: rev 20 l.585-586 calls the standing criteria (00:31 row included) "UNRANKED ... their rank is his and is not
asked now, joint_condition.md §4H.9"; but §4H.9 makes only the ABSENCE criteria unranked, and jc's Goals present the
00:31 criteria "in his order; a conflict is won by the higher one" (jc l.66). The record (CF:1346-1348) lists them
without a rank, so rev 20's "unranked" is the more faithful, but then jc's "in his order ... won by the higher" is a
manager's ranking presented as his, and rev 20's citation of §4H.9 for the 00:31 row is wrong. Missing/unranked goal:
a doc finding as the brief directs.
Severity: doc. Effort: small (rename the pointer "his 00:31 criteria, STANDING CRITERIA below"; add the TEST row;
fix the citation; flag jc's "in his order" as the manager's ordering). Blast: §0 rows 518, 594; jc Goals.

### RULING-9 — the criteria's checkable forms are stated but never APPLIED to rev 20's new claims; graded here, in his order
CONFIRMED (absence of a grading table; grep of rev 20 for the criteria's checkable forms finds them only at l.588-594).
G0 (ranked first, the owner's): acceptance is "no GAP row" (l.569); rev 20 ADDS a GAP, L97 (l.705, "no diagnostic is
possible"), and §13 O38 (l.4127ff), the GAP register, does not list it: a new claim argued against the ranked-first
goal without being surfaced as such. G0b (few marks, one meaning): the label mark `h?` and default `h = v` serve it
(one meaning each, l.1854-1856); DOM (a new compile-time concept with an approximation tier, l.1916ff) is new
machinery needed ONLY by the mark, not weighed against G0b or 00:31's "a lot of special syntax and values to handle an
obscure case". Standing criteria (unranked): SIMPLIFYING SEMANTICS: served by record-is-product, one kind of absence,
`all` as "every label marked" (one rule); AGAINST it: the syntactic loop list (RULING-3: shape-specific). SAVING PEOPLE:
served by not-both, label-twice, sibling loops; AGAINST it, not listed as silent: `all(((h, m): R))` accepting
incomplete items (RULING-2), `(h?: S)` and `(h?: !S)` both holding on one absent h (l.1906-1908, BY DESIGN). A SET NEVER
CONTAINS ABSENCE: held everywhere checked (controls on the label; D never a set member, l.1868). MEANING, NOT SPELLING:
broken by the syntactic loop (RULING-3); its wording ambiguous (RULING-4). IN LINE / LARGER LANGUAGE: the joint
condition names E-CAL as a second problem (jc problem 4); DOM, F1-for-one-label and the under/over tier name no
problem beyond the mark. No rev 20 claim was found arguing FOR something the owner ranked as a constraint (no
alphabetic operators, `&`/`|`/`!` extensional): held.
Severity: doc (a missing self-check the draft defines for itself). Effort: medium (one table: each rev 20 construct x
each criterion, SERVES / AGAINST / SILENT). Blast: §0.

## PROBED-AND-HELD

- OWNER QUOTES, word for word: every owner sentence of the 2026-11-16 CF entries (CF:1304-1725; 45 distinct quoted
  strings, extracted by `ruling/work/q2.py`, whitespace-normalised, `\|` unescaped) diffed against rev 20 (`q3.py`:
  every double-quoted rev 20 string sharing a 4-word run with an owner quote). 0 inserted, dropped or moved words. Full
  quotes at rev 20 l.502-550, 590-594, 1007, 1176, 1746-1757, 1843, 1857, 1981, 2059, 2072, 2876, 3977, 4361, 4697,
  4791-4914, 5013-5029 all exact; mid-quote cuts at l.518 and l.533 carry "..." and every segment is exact; the
  tail-truncations at l.520, 522, 523, 524, 544, 545 stop at a sentence end (no word altered). Pre-11-16 hits
  (l.470/4667, CF:1170) out of scope. The 14:31 record points (1)-(4) quoted at l.1843-1852 verbatim.
- STATUS faithful (beyond RULING-5/6): RULED vs NOT A RULING vs IDEA vs LEAN for 00:31 (direction, not ruling), 00:35
  (GO, design only), 09:42, 09:50 (REOPENED 09:58), 09:52/10:18 (idea/preference), 10:22 PARKED, 10:35 lean + idea,
  10:37 preference, 10:40 (question, not carried as ruled), 10:43, 11:05, 11:17, 11:20 (no-warning = manager's
  reading), 11:27, 11:32, 11:35, 12:45 (wording SUPERSEDED), 12:48, 12:51, 13:16, 13:29 (remark = discussion, 15:23),
  13:38 NOT A RULING, 13:52 principle + idea, 14:09 lean, 14:15 idea NOT TAKEN, 14:31, 15:23, 15:27, 15:29: 33 entries,
  each carried with its record status in §0 l.515-550.
- ASTERISK: the provisional sentence is quoted 3 times (l.550, l.591, l.1882-1883) and carries (*) at all 3, with the
  footnote at l.558, l.596, l.1883; the two non-quoting mentions (l.17, l.1990) also mark it provisional (*).
- 14:31 reading (ii) `!` of a marked condition = plain complement (l.1907, labelled): consistent with "a set never
  contains absence" (the complement is of the CONDITION, not a set with an absence member) and with `&`/`|`/`!`
  extensional; consequence BY DESIGN L95 stated. (iii) never-absent-mark warning (l.1969-1970, labelled): a property
  of the pattern's meaning, consistent with mark-domain.
- 14:50 (e) per-pass absence (KEPT): needed by record = `&` (12:45) and by the ruled pairing rule; spelling-free; held.
- 12:45 zero-pass-record: `9` FAILS and record = `&` kept at l.2069-2071; wording superseded, labelled (row 536).
- 13:16 label-twice: L92 ERROR; no rev 20 construct (all-marking, defaults) re-admits a doubled label: held.
- 12:51 retire-paused: `^h` / `lex_` appear outside §16 only in changelog history, §0 history rows, and PAUSED-tagged
  rows (L72-L81, l.899, l.923, l.2462, l.3552); not in rev 20's language text: held.
- 13:52 consequence (2) (in-set absence forms closed): D holds texts only (l.1868): held.
- Owner-ranked constraints (no alphabetic operators; `&`/`|`/`!` extensional): no rev 20 claim argues against them.

CRITIC COMPLETE
