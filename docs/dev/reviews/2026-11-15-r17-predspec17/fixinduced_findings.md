# FIXIND findings

## Findings


### FIXIND-1. §0 Status line still says "DRAFT rev 15" (revs 16 and 17 both missed it)
CONFIRMED (text). rev 17 line 230: "**Status: DRAFT rev 15 (lane predspec15, 2026-11-15). NOT a ruling ...". Same line
in rev 16 (line 208) and rev 15 (line 189): neither rev 16 nor rev 17 bumped it, while the changelog (line 5) and the
CF-range paragraph (line 252) say rev 17. A reader of §0 alone is told the document is rev 15.
Severity: doc. Effort: one word. Blast radius: §0 Status only. §0, line 230.

### FIXIND-2. Moving the labels to the AUTHOR's pattern makes UNSET labels possible; the derived strict forms, kept "rev 16, unchanged", then accept them
CONFIRMED (rule emulation). Rev 16's bundled body defined `t1`..`t3` itself, every one set in every match, so its
derived forms were exact. Rev 17 lets the projection name any author label, and its new caveat (5) (line 2382-2384) says
"An UNSET label ... makes its conditions false (§4.2), so the compare rejects that match". That holds for the halves and
between, but §4.2 (line 1467) also says a failed condition's `!` is TRUE, so the derived forms carried over
verbatim at lines 2360-2362 ("THE FAMILY IS SMALL ON PURPOSE (rev 16, unchanged): strictly above lo is `P &
!lex_le2(s, lo)` ... strictly below hi is `P & !lex_ge2(s, hi)`") ACCEPT every match with an unset compared label.
Repro: `/var/tmp/pcrec-pcrec/scratch/crit-predspec17/fixinduced/unset_probe.py` (python3 -I; out: `unset_probe.out`,
table (U)): author `/(?<h>\d{1,2})(?::(?<m>\d\d))?/`, bound [9, 0], subject `9` (m unset): lex_ge2 false, lex_le2
false, "strictly above 9:00" TRUE and "strictly below 9:00" TRUE at once; equality false. Expected: "above" a subset of
lex_ge2 (rev 16's exact claim). Every (D)/(R) population has all labels always set (no optional group), so the 0-differ
counts do not reach the case. Caveat (5) also states only half the consequence.
Fix: either caveat (5) names the derived forms' behaviour and spells strict as `lex_ge2(s, lo) & !lex_le2(s, lo)`
(the halves then gate on the labels being set), or the derived forms are restricted to always-set labels; one sentence
either way. Severity: answer (a documented derived spelling gives a wrong answer on a reachable author pattern).
Effort: small. Blast radius: §8 THE FAMILY IS SMALL, caveat (5), DECIDED (44)'s "derived by `!`". §8, lines 2360-2362, 2382-2384.

### FIXIND-3. A REPEATED author label in the projection: the compare silently becomes "every iteration, field by field", not a tuple compare per iteration; rev 17 states nothing
CONFIRMED (rule emulation). Same cause as FIXIND-2: rev 16's own labels were set once; rev 17's projection takes any
author label, and §8 TUPLE COMPARISONS / THE PROJECTION / CAVEATS (lines 2285-2417) never mention a REPEATED label
(grep of 2280-2420 for repeat/iteration/loop: no hit). Under §4.2/§4.3 a plain condition on a repeated label holds for
EVERY iteration (vacuously over zero), and each entry's conditions quantify h and m SEPARATELY, so the tuples are not
compared per iteration. Repro: `unset_probe.py` table (L): author `/(?:(?<h>\d{1,2}):(?<m>\d\d),)*/ & lex_ge2([(h:),
(m:)], [9, 0])`: `10:00,9:30,` -> REJECT although every tuple is >= 9:00; `` (zero iterations) -> ACCEPT (vacuous).
Neither is wrong under the rules, but the draft's description ("the PROJECTION, the array of the labels to compare",
"integer lexicographic order in PROJECTION order", line 2357-2358) reads as a tuple compare and no caveat, warning or error
covers a looped label. Fix: a caveat (6') "a repeated label: each condition reads every iteration; for a per-iteration
compare put the call inside the loop's item (`list_of(P & lex_ge2(...))`)" or a compile error/warning for a repeated
compared label. Severity: design (unstated semantics of a new construct). Effort: one caveat. Blast radius: §8 caveats.
§8, lines 2308-2312, 2375-2387.

### FIXIND-4. Reading (a) ("`s[k]` on an array of MACROS is its k-th entry, a macro") CONTRADICTS §3.2 tool 1, which the draft says only "states the result for arrays of rx"
CONFIRMED (text). §8 line 2352-2354: "(a) `s[k]` on an array of MACROS is its k-th entry, a macro (§3.2 tool 1 states
the result for arrays of rx; §3.5 makes an array of macros a macro)". §3.2 tool 1 (line 1326-1327) does not limit itself
to arrays of rx: "`X[...]` = POSITION in the array interface only ...; the result is ALWAYS AN RX read through the array
interface", and its REASONING (line 1349): "The output of `[]` is always an rx". It also says in value position `[n]`
"indexes the entries of the rx on its left, a SPELLED array" (line 1333), while `s` is a macro (§3.5) bound to a
parameter. So reading (a) is not a gap-filler: it changes a stated "always". The decision list (51) and "Neither adds
a kind or a mark" (line 2355) inherit the understatement. Fix: §3.2 tool 1 gains the sentence "on an array of macros
(§3.5) the result is the entry, a macro" (and its REASONING's "always an rx" is qualified), marked LEAN, with §8
pointing at it. Severity: doc/design (a rule silently extended). Effort: two sentences. Blast radius: §3.2, §8, (51).
§8 line 2352-2354; §3.2 lines 1326-1333, 1349.

### FIXIND-5. Reading (b) ("a parameter bound to a macro may be called in the body") steps over §5.3's FENCE on passed macros, which the draft cites as its precedent
CONFIRMED (text). §8 line 2354-2355: "(b) a parameter bound to a macro may be called in the body (`each` already
applies a passed macro, §5.3; ...). Neither adds a kind or a mark." §5.3 line 1840: "Macros are passable values,
FENCED: compile-time only, over finite SPELLED arrays ..., STRUCTURAL OPERATORS ONLY." `each` is a structural operator;
`lex_ge2` is a plain library macro, and rev 17 itself says the projection is NOT a structural primitive (THE PROJECTION
(ii), line 2401-2403). Passing a macro BY NAME (`[h_is, m_is]`, unapplied, its required parameter open) into a plain
macro and CALLING it there with an argument has no precedent in §5.2/§5.3 (the existing non-structural macro arguments,
`occurs.exactly(1, (name: S))`, `when(c, p)`, pass a condition with only its operand open, applied by `&`, never called).
§5.2 also says "NO PARTIAL APPLICATION ... a section is the one way to leave a hole" (line 1806-1807): an unapplied
`h_is` passed as a value is a macro with a REQUIRED PARAMETER left open, which is what that sentence forbids outside
`each`. So (b) widens two stated rules (the fence; the one-way-to-leave-a-hole), not "no new kind or mark". Fix: state
(b) as an amendment of §5.3's fence and §5.2's partial-application sentence (LEAN, listed for the owner), or route it
through O71 (a label section leaves the set open by a SECTION, the one sanctioned hole). Severity: design (the "today's
language" claim for the accessor form at lines 2313-2318 rests on it). Effort: small. Blast radius: §5.2, §5.3,
§8 "in today's language", (51), O71's "TODAY the author writes one accessor". §8 lines 2313-2326, 2352-2355.

### FIXIND-6. BOUNDS FROM THE SAME MATCH: "existing rules, not new ones" drops §2.4's condition that the LITERAL decides the reading; a captured bound has no literal and is not padded
SUSPECTED (text; confirm by stating which reading `(b1: padded(>$a1))` takes for `$a1` = `09`). §8 BOUNDS AND LEVELS
(line 2363-2374) adds `lex_ge2([(b1:), (b2:)], [$a1, $a2])`, "which makes each entry a value-vs-value relation, `(b1:
padded(>$a1))`, §4.6", and closes "the bound kinds above are §4.6's and §6.1's existing rules, not new ones". The bodies
pad only the COMPARED side; the bound is a raw atom. §2.4 (line 903-907): "The LITERAL decides the reading" and an
integer set holds "CANONICAL numerals ... no leading zeros ... unless the literal has them"; its REASONING (line 913):
"declared constraint sets are needed only where no literal fixes the reading (value vs value, §4.6)"; §4.6 STATUS: value
comparisons "typed". With constant bounds the author writes `9`; with a captured bound the text comes from the author's
field (`\d\d` gives `09`), no literal fixes integer-vs-string, and typed parameters are OUT of phase 1 (§5.2). Rev 16's
bundled form never had captured bounds, so this is new with rev 17. Fix: say the bound must be read as a number (e.g.
`padded` on both sides, or the bound through a computed numeric label, §4.4), or mark the match-bound form "needs a
declared reading, §13 O27/O48". Severity: design (doc for phase 1, since no row uses it). Effort: one sentence.
Blast radius: §8 BOUNDS AND LEVELS, DECIDED (50), (52). §8 lines 2363-2368.

### FIXIND-7. "The DFA/VM claims of rev 16 stand unchanged" points at claims rev 16 never made
CONFIRMED (text + grep). rev 17 §8 BOUNDS AND LEVELS line 2372-2374: "So the DFA/VM claims of rev 16 stand unchanged for
constant bounds (the expansion is rev 16's conditions with the author's labels; table (R))"; changelog line 21-22: "constant
bounds at the DEFAULT level as automaton states (the DFA/VM claims of rev 16 stand)". grep of rev 16 for DFA/VM/level/
automaton near any tuple/`lex_` text: the ONLY statement is caveat (5) "the automaton size is UNMEASURED" (rev 16
§8); no level, DFA or VM claim was made for the tuple family (rev15->16 diff: no DFA/level line in the tuple hunk).
So the restatement presents a NEW claim (the compare is default-level automaton states) as an unchanged old one, and
table (R) (answer identity of the two bodies) is offered as its evidence, which says nothing about level. Fix: drop
"of rev 16 stand unchanged"; state the default-level claim as rev 17's own LEAN (it is already DECIDED (52)), resting on
§6.1/§4.1 conditions-against-fixed-sets. Severity: doc (provenance). Effort: one clause, two places. §8 line 2372-2374; changelog line 21-22.

### FIXIND-8. Caveat (4) "a field that is not digits makes the compare reject it" is false for the derived strict forms (rev 16, carried into rev 17)
CONFIRMED (rule reading; same mechanism as FIXIND-2, emulation shape as table (U)). rev 16 caveat (4): "a field
pattern that admits other text makes the compare reject it"; rev 17 caveat (4) (line 2380-2382) keeps "A label's text
compares as a number only if it is digits (a comparison set holds numerals, §2.4)". For an author label admitting
non-digits, e.g. `/(?<h>\w{1,2}):(?<m>\d\d)/` on `ab:00`, every condition of lex_le2 fails, so `P & !lex_le2(s, lo)`
("strictly above lo", line 2360-2361) ACCEPTS `ab:00`. Rev 16's populations (F) and rev 17's (D) use digit-only fields,
so no table reaches it. Rev 17 widens the exposure: the field is now the AUTHOR's arbitrary labelled group, not a
library-supplied field line. Fix: the same as FIXIND-2 (strict = half & !other half). Severity: answer. Effort: shared
with FIXIND-2. §8 lines 2360-2362, 2380-2382.

### FIXIND-9. Tuple-compare status disagrees between places: §14 still says the array spelling is OPEN, O69 says names "OPEN ... RULED", DECIDED (45) still "OPEN"
CONFIRMED (text). (i) §14 line 4202-4205: "whether a tuple comparison is spelled over arrays is OPEN (§13 C25; ...; rev
17: over arrays, names and order RULED ...)": the sentence's main clause says OPEN, its own rev-17 parenthesis and C25
(line 3438, "REV 17: RESOLVED for the fixed sizes. Reading (A) over arrays, names RULED") say decided. (ii) O69 line
4066-4067: "the names are OPEN (**tuple-names**; RULED in rev 17, CF:1226 on main)". (iii) DECIDED (45) line 3908-3909
still ends "(OPEN as **tuple-names**)" while (53) explicitly withdraws its sibling (46); (45) gets no "RULED in rev 17"
note, so the decision list shows the names open. Fix: rewrite §14's clause ("spelled over arrays at fixed sizes: RULED,
rev 17; any number of fields later"), O69's to "RULED in rev 17 (was OPEN)", and add "(45) RULED in rev 17" in (49)-(53)
or beside (45). Severity: doc. Effort: three edits. §14 line 4202; §13 O69 line 4066; DECIDED line 3909.

### FIXIND-10. The first-library tuple family rests on constructs §0.2 still lists as "phase 1 not stated" and §12's census lists as unused (positional `X[...]`, passed macros)
SUSPECTED (text; confirm by the author's reading of "first library" vs "phase 1"). Rev 16 put the fixed-size compares
"IN THE FIRST LIBRARY" (RULED, CF:1166) and rev 17's bodies (line 2299-2306) read `s[k]` and `lo[k]` by position and
call passed macros. §0.2 line 657-662 still says "Not stated by the owner: which library pieces (§8) ... phase 1
carries; and, of the constructs NO §12 case uses (... positional `X[...]`, ...), which stay in phase 1". The census row
for positional `X[...]` (line 3027) still reads "none" with no pointer that the tuple bodies (§8) use it, while the
tuple census row two lines up says "none (§8 carries their worked rows)". Neither rev 16 nor rev 17 touched §0.2: a
ruled first-library family now depends on a construct whose phase-1 status §0.2 calls undecided. Fix: §0.2 gains a line
("the tuple compares are in the first library, RULED; their bodies use positional `X[...]` and a passed macro called in
a body (§8 readings (a), (b)), so those are in with them"), and the `X[...]` census row points at §8. Severity: doc
(scope consistency). Effort: two sentences. §0.2 line 657; §12 census line 3027.

### FIXIND-11. Rev 17 dropped, unannounced, rev 16's WHY (tuple compare vs a string range) and the `\d+`-fields worked row
CONFIRMED (diff). rev16->17 diff lines 209-243 remove: "Why a tuple compare and not a string range: as strings `"1.10"`
sorts before `"1.4"`, so `between("1.4", "1.10")` is EMPTY, and `between("1.4", "1.9")` also accepts `1.45`", the
statement that the time range "gives the same answers as §2.7's split-fields form", and the table row "the version
range with `\d+` fields | `1.04`, `01.10`, `1.010` (`padded` ignores leading zeros) | `1.011`". Rev 17's changelog
lists none of these as withdrawn (it names only the bundled form, separator and helper-label caveats). grep of rev 17
for `1.45` / `"1.10"`: no hit; the reason the family exists is now stated nowhere in §8, and caveat (4)'s "leading zeros
are ignored (`padded`)" lost its one worked witness with a leading-zero FIELD ((W)'s version rows all refuse leading
zeros). Fix: restore the WHY sentence and the `\d+` row (re-checked in the decomposed form), or list them in the
changelog as dropped. Severity: doc. Effort: restore two lines. §8 after the worked table (line 2342).

### FIXIND-12. `compare.width`'s suggestion is stated two ways (§2.7: split fields OR the tuple compare; §9: split fields only), and §2.7's rev 17 example uses the OPEN `(h:)` unmarked
CONFIRMED (text). §2.7 line 1261-1263: the lint "suggests the SPLIT-FIELDS form ... or, since rev 16, the library's tuple
compare ... (rev 17: `/(?<h>\d{1,2}):(?<m>\d\d)/ & lex_between2([(h:), (m:)], [9, 0], [10, 0])`)". §9 line 2477-2478 (not
touched by rev 16 or 17): "`compare.width` keeps its warning and suggests that form" (split fields only). And §2.7's
example spells the label section `(h:)`, OPEN (O71), with no "placeholder / accessor `h_is`" note (§8 line 2324-2326
carries that note for §8's own examples only), so §2.7 presents a not-yet-language spelling as the lint's fix, "in one
call" (it needs two accessor bindings today). Fix: §9 gets "or the tuple compare (§8)"; §2.7's example gets "(with
`(h:)` OPEN, O71: today `h_is`, `m_is` as in §8)". Severity: doc. Effort: two clauses. §2.7 line 1261-1263; §9 line 2477.

### FIXIND-13. §0.3's "filter role" row still says "LEAN pending §13 O67" for a bodyless transform's argument; rev 16 CLOSED O67 and moved the lean to §2.7 / row 8
CONFIRMED (text). rev 17 line 680 (§0.3 words, **filter role**): "... a compile-time set (and, LEAN pending §13 O67, the
argument of a transform without a body)". O67 (line 4040): "CLOSED in rev 16, NOT as asked"; §2.7 line 1258-1259 now
holds the lean as "`any_case`'S ARGUMENT (stated once, here; the manager's LEAN, not ruled)", and THE ROLE TABLE row 8
(line 2593) names `any_case` only. Rev 16 updated the neighbouring **filter modifier** row (line 685) for the same
change but not this one, so §0.3 cites a closed item as the pending authority and keeps the plural "a transform without
a body" class rev 16 reduced to one member. Fix: "(and, the manager's LEAN, §2.7, the argument of `any_case`, the one
transform without a body, THE ROLE TABLE row 8)". Severity: doc (a pointer that no longer lands). Effort: one clause.
§0.3 line 680.

### FIXIND-14. §0.3 "subject" row: rev 17 put the owner's tuple "subject" (= the compared fields) into the NAMES cell, so the one-word-one-thing row now names two things
CONFIRMED (text). Line 671 (diff line 78): "| **subject** | (the tuple compare's "subject" in the owner's 23:07 and 23:25
words is the COMPARED FIELDS, the projection, §8) the run-time TEXT being matched ... | the operand of `&` (...CF:749's
ruled phrase "the subject is never an argument" means the operand) |". §0.3 (line 667): "Each word below
names ONE thing throughout; a quoted ruling keeps its own words, glossed where they differ": a gloss is allowed, its PLACE is the issue. The existing precedent for a quoted ruling's other
sense (CF:749) sits in the NOT-USED-FOR cell; rev 17's note sits first in the NAMES cell, before the definition. Fix:
move the parenthesis to the third cell ("the compared fields of a tuple compare: the owner's "subject" at 23:07/23:25,
kept in quotes; this document says "compared fields""). Severity: doc (minor). Effort: move one clause. §0.3 line 671.

### FIXIND-15. O71's for/against omits the sibling rule its spelling collides with: §2.3's RULED error on a call written after a condition, `(a: digit)(x)`
CONFIRMED (text; judged under the stated lean, the question itself not raised). O71 (line 4150-4159) and §8 (line 2321-
2322) define `(h:)(S)` = `(h: S)` and list as "Against" only "one more bracket form ... a `:` with nothing after it reads
like an unfinished entry". §2.3 (line 888-890), RULED CF:749: "A call that passes the operand (`(a: digit)(x)`, `p(x)`,
`padded(S)(x)`) is a compile error naming the fix". `(h:)(S)` (a set) and `(h: S)(x)` (an operand) differ only by
whether the record's set is empty, so the §2.3 error must now distinguish them, and the error message's example is the
label section's own shape. Rev 17's RULE CHECK (line 2345-2355) does not list §2.3 among the rules the examples were
checked against. Fix: one "against"/"note" line in O71 naming §2.3 and the distinguishing rule (an open set = the
section; a filled set followed by `( )` = the operand error). Severity: doc. Effort: one sentence. §13 O71 line 4157.

### FIXIND-16. The 23:25 order ruling is cited "by date and words, on main only / this branch does not carry", but the frozen main COND-FAMILY carries it at CF:1250-1254
CONFIRMED (text). rev 17 line 252-253: "rev 17: CF:1214-1248, and the 23:25 order ruling, which this branch does not
carry and which is cited by date and words"; §0 rulings table preamble (line 381-382) "on main only". The subject is
rev 17 AS ON MAIN (876491894 in f06c4bcac), whose COND-FAMILY.md holds "2026-11-15 RULING — tuple compare argument
order ... his words: "tuple-arg-order: subject low high"" at CF:1250-1254. Every other ruling in the draft is cited by
CF line; this one now has a line and the "this branch does not carry" sentence is stale after the merge. Fix: cite
CF:1250-1254 on main in the CF-range paragraph, the §0 rulings row, §8, C25, (12), and §15's rev 17 row. Severity: doc.
Effort: mechanical. Lines 252-253, 381-382, 2289-2291, 3439, 4183-4184, 4226.

## PROBED-AND-HELD

- Withdrawn helper labels `t1`..`t3` and decision (46)'s `label =`: every live mention is either withdrawn in place
  (§8 caveat (1), line 2375-2377; DECIDED (53)) or history (changelog, O69's kept sketch at 4078-4090, DECIDED (46)'s
  own rev-16 text). 13 grep hits, none citing them as live. HELD.
- Withdrawn separator / field-pattern arguments: 0 live mentions outside history (changelog, §8 line 2296 "WITHDRAWN",
  caveat (3), O69 sketch, owner question (12) "as asked"). HELD.
- `json.quoted` CUT: 33 grep hits; §1, §0.3 filter-modifier row, §2.7 (text, table, STATUS), §8 list and STATUS, §9
  ALSO CUT + STATUS, §11 THE ROLE TABLE row 8, §12 REV 16 RE-APPLIED and E-JSONL, O37, O61 audit, O67, O70, owner
  question (9): all say CUT or are marked history. Only §0.3's filter-role row is stale (FIXIND-13, via O67). HELD.
- `any_case` a primitive for now: §2.7 text/table/STATUS, §8 list, row 8, O67, O70, (9) consistent. HELD.
- O68 ("behind the tuple compare"), O47 (still (C), rev 17 note consistent with C25), C25 (RESOLVED for fixed sizes),
  O70 route (a) (matches plan.md [PRED-REREAD] at f06c4bcac, line 977 "Route (a)'s shape ... 22:03"), O71 OPEN,
  owner questions (12) ANSWERED / (13) OPEN, DECIDED (49)-(53) vs §8 text: consistent except FIXIND-9's three places.
- §0.1 REV 17 paragraph (no row moves; L20, L37 unchanged): held; no §0.1 row uses a tuple compare.
- §12: no case uses a tuple compare; census row updated; E-JSONL unchanged by rev 17. HELD.
- Sibling rules for the new constructs: §3.5 (array of macros = macro, shared arity: `[h_is, m_is]` arity 1, the body
  arrays' entries operand-only conditions) HELD; §4.1 (chain lookup, unknown-label and ambiguity errors, `$x & ...` as a
  condition an error, the `[$h, $m]` values form not constrainable) HELD; §5.2 (`date_in(years)` precedent for a
  parameter after `:`) HELD for the accessor's BODY; §6.1 (`param` bounds parametric at default) HELD; §4.6 class-count
  pricing of match bounds HELD as pricing (typing gap: FIXIND-6). §3.2 tool 1 and §5.3: FIXIND-4, FIXIND-5.
- Restatements diffed: phase-1 spelling without the library, `semver & ((major: >=2) | (major: 1, minor: >=4))`:
  verbatim in rev 16 and rev 17. ANY NUMBER OF FIELDS / O68 sentences: verbatim. Caveat (6) cost = rev 16's (5)
  verbatim. Rev 16's caveat (2) LEAN (a parameter as a comparison atom) moved to the RULE CHECK, kept LEAN. Rev 16's
  (4) lost its "a field pattern that admits other text makes the compare reject it" clause (meaning kept; the claim's
  derived-form exception is FIXIND-8). The §9 time-range form unchanged (but see FIXIND-12).
- Evidence re-run: `predspec17_check.py` reproduces its committed `.out` byte for byte (after the version line):
  25,848 + 7,528 cases, 35 worked rows, 0 differ, 0 engine disagreements (`rerun17.out` here). Its populations never
  hold an optional, repeated or non-digit compared label, which is why FIXIND-2/3/8 do not show in it.
- Own probe: `unset_probe.py` / `.out` (python3 `re` only, emulating §4.2's unset and repeated-label rules on the rev 17
  bodies): table (U) 6 subjects, table (L) 6 subjects.
- Not run: libpcre2 cross-check of my own probe (the probe reads labels only; `re` and libpcre2 agree on such patterns
  in the lanes' own tables). Not raised: the label-section question itself and question (13) (open, per COMMON).
