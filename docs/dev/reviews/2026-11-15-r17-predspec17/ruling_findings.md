# RULING findings

## Findings

### RULING-1 (CONFIRMED, doc/design; effort small; blast radius §8 THE PROJECTION (i), DECIDED (49), owner question (13))
§8 THE PROJECTION (i), rev 17 line 2396-2399: the verdict "a PLAIN MACRO taking label NAMES ... NOT EXPRESSIBLE"
rests on "the left of `:` is a path written in the program, never an expression (§4.1, RULED CF:595)". CF:595-597
records the owner AGREEING THE CONCEPT "one condition form `label: set`" (his words: "I agree with both excepting the
spelling ..."); the "left of `:` may be a PATH" is the MANAGER's proposal in the 2026-11-14 01:00 entry (CF:275, "Manager:
... let the DOT do what it does elsewhere"), and NO owner sentence anywhere in the record says a label position cannot
be filled by a macro PARAMETER (the "written in the program" clause is new in rev 17). The record itself treated
exactly this as unsettled: CF:1239-1240 "TO CHECK in rev 17: whether a macro body may use a PARAMETER AS A LABEL NAME
... if not, say exactly what is missing and bring it to him"; CF:1245 replaced that check by the projection check but
did not answer it. So the one argument that turns down the owner's literal shape ("a macro that ... produces an array
given labels", CF:1241) is labelled RULED where it is this document's reading of a concept ruling (plus C13, which the
draft correctly marks OPEN). Fix: label the (i) premise LEAN (this document: §4.1's path rule extended to parameters),
and say in owner question (13) (or a sibling line) that his literal shape was not built because label positions take
no parameter, so his answer on (13) is not read as consent to that premise. Consequence check: (iii) stands on its
own (CF:749, CF:890-891 do say what the draft says: "THE SUBJECT IS NEVER AN ARGUMENT"; "interfaces aren't themselves
values that can be created"), so the recommendation need not move; only the status label and the owner's sight of it.

### RULING-2 (CONFIRMED, doc/design; effort small; blast radius §13 O70 route (a), §0 rev-17 rulings table row 1, §5.4 `${ }` row, §11 typed positions)
§13 O70 rev 17 lines 4138-4147 and §0 line 386 fold the owner's 22:03 pointer "One thing we talked about was exposing
options like (illustrative example) /(?i=${case})fred/" (CF:1215) as a NEW shape ("By itself it makes an option a
VALUE"), with no citation of where it was talked about. It is on record in his own words: CF:86, HOLES IN SYNTAX
POSITIONS (Frank 2026-11-13: "they could show up in different places like \d{${x}} with certain constraints of course.
Also (?i=${})"), which the record turned into "FLAGS (?i=${ci}) (boolean): parameter = start-state switch; from text
... = split into variants", and CF:87, READ A PARAMETER AS LATE AS POSSIBLE, built on his example
"abcd(?i=${insensitive})\d+xyz". The draft's typed-syntax-position lists (§5.4 `${ }` row, line 1912; §11, line
2725-2726) name quantifier bounds, class range ends and group names but DROP the flag position his CF:86 words named,
so rev 17 neither cites CF:86-87 nor notices that the option-as-value half of route (a) is an existing typed hole
position (boolean, finite set, read late), leaving only the manager's real question (does the option reach INTO a
hole, CF:1217-1221) new. "his word" for "illustrative" is verbatim (CF:1215) and the manager's question is correctly
labelled a question, not ruled: those hold. Fix: cite CF:86-87 in O70 (a) and the §0 row's third column; restore the
flag position (`(?i=${p})`, boolean) to the typed-position lists or list it in §13 as dropped with a reason.

### RULING-3 (CONFIRMED, design (G0); effort small-medium; blast radius §0.1 LOOK-ALIKE TABLE, §8 THE PROJECTION, §11 diagnostics)
G0 (line 400, the owner's standing criterion, ranked first) makes the LOOK-ALIKE TABLE §0.1 its acceptance: every pair
of forms that look alike is SAME or DIFFERENT with one class, and "acceptance = no GAP row". Rev 17 says "§0.1: no row
moves" (line 25) yet introduces three spellings of the compared side that look alike and do different things, none
with a row or a named diagnostic:
(a) `lex_between2([(h:), (m:)], [9, 0], [10, 0])` (works) vs `lex_between2([h, m], [9, 0], [10, 0])`, which is the
EXACT shape the owner was shown when he gave the decomposition (CF:1234) and when he RULED the order (CF:1252: "e.g.
`lex_between2([h, m], [9, 0], [10, 0])`"), so the first thing he or a user types; bare names as values are §13 C13
(OPEN), and the draft does not say what this call does; vs `lex_between2([$h, $m], ...)`: the draft says it "cannot
be the compared side" (line 2408) but names no diagnostic, and by its own rules each `$h` is a one-string set (§5.4),
so the body's `s[1](padded(>lo[1]))` is CALLING A PATTERN, whose stated error hint is "write `isodate & (year: ...)`"
(line 1798): the wrong fix for this trip (the right one: "write `(h:)` / an accessor; `$h` belongs in the bounds").
(b) `[(h:), (m:)]` as the projection (entries read BY POSITION, an ordered tuple) vs `[(h: 9), (m: 0)]` in a filter
role (= either condition, an alternation, line 1429-1430, §3.5), and vs `[(h:), (m:)]` applied outside a compare
(an array of macros is a macro, pointwise: `[(h:), (m:)](S)` = `(h: S) | (m: S)`, CF:645-647): the same brackets read
as "both, in this order" inside `lex_*` and as "either" everywhere else. This is BY DESIGN (the body indexes `s[k]`),
but G0 requires the row and the user-facing sentence; §8 never says it.
Fix: add §0.1 rows for (a) (DIFFERENT: ERROR, with the projection hint for `[$h, $m]` and a stated outcome for
`[h, m]` pending C13) and (b) (DIFFERENT: BY DESIGN), or list them as GAP; correct line 25's "no row moves".

### RULING-4 (CONFIRMED by hand expansion; design, GENERAL FORM + UNLOCK; effort small; blast radius §8 TUPLE COMPARISONS "ANY NUMBER OF FIELDS", §13 O69 (3) and its TRIGGER, the six-name family)
§8 line 2385-2386 and §13 O69 (3) (line 4070-4072, 4096-4098) say any number of fields "needs a structural macro with a
running prefix over array positions (bounded recursion over the array's length, or a library primitive); today's
`each` ... cannot", TRIGGER "a real use with four or more fields, or a looping structural macro ... built for another
need". But the draft already has the general mechanism, RULED: bounded recursion by a strictly decreasing literal
parameter (§7 STATUS line 2131, CF:583/CF:591 predx Q12), with a literal base case, used by §12.11 E-DEPTH
(`value_depth(0) := ...`, `value_depth(k) := ... value_depth(k - 1) ...`). With the size passed as a literal, the
array compare for ANY n is a plain recursive macro over positions (indexing keeps original positions, §3.2 tool 1, so
recurse on an offset, not a slice):

    lg(1, n, s, lo) := s[n](padded(>=lo[n]))
    lg(j, n, s, lo) := [s[n-j+1](padded(>lo[n-j+1])), s[n-j+1](padded(==lo[n-j+1])) & lg(j - 1, n, s, lo)]
    lex_ge(n, s, lo) := lg(n, n, s, lo)

Hand expansion: `lex_ge(2, s, lo)` = `[s[1](>lo1), s[1](==lo1) & s[2](>=lo2)]` = rev 17's `lex_ge2` (padded elided);
`lex_ge(3, ...)` = `[s[1](>), s[1](==) & [s[2](>), s[2](==) & s[3](>=)]]`, which by `&` distributing over an array's
entries (§3.2 tool 2) is rev 17's `lex_ge3`; `le` mirrors; between = ge & le. What is actually missing is narrower than
the draft says: (1) O21 (the base case by literal argument, "not stated as a general feature", though E-DEPTH uses it),
(2) compile-time arithmetic on literal parameters inside an index (`s[n-j+1]`; E-DEPTH does `k - 1` as an argument
only), (3) optionally a spelled entry count so `n` need not be passed. UNLOCK: the six sized names become instances
of one (`lex_ge2(s, lo) := lex_ge(2, s, lo)`), any n is in reach of the ruled recursion, and the TRIGGER for O69 (3)
should name O21 + (2), not an unbuilt looping macro. Not a call to add it to the first spec (D77): a correction of
what the later item waits on.

### RULING-5 (CONFIRMED, doc; effort trivial; blast radius §13 O71, owner question (13), §8 line 2321-2324)
O71 (line 4154-4156) and §8 (line 2322-2324) present the label section `(h:)` as C33's "other operators ... then we'll
see" (CF:753) "met by its first case". C33's ruled shape is "sections START with `&` only (`(& f)`, subject on the
left ...)": the operator's LEFT side (the subject) is the open one. `(h:)` opens the OTHER side: the label (left of `:`)
is fixed and the SET (right) is open, so it is the first RIGHT-open section, not merely another operator in the ruled
shape; and `:` is not an operator between two sets at all (its left is a path, §4.1). The fit with C34 ("sections are
the one way to leave a hole", CF:754-755) holds, but the question put to the owner should name both novelties (another
operator AND the other side), so "label-section: yes" is not later read as covering, e.g., `(<= 5)`-style right-open
sections of `&`/`|` by analogy. No answer moves.
(RULING-5 addendum: the owner's words at CF:753 are "1. start with & and then we'll see"; "other operators" is the
record's gloss, so the quoted phrase "other operators ... then we'll see" at line 4155 / 2322-2323 mixes the record's
words into a quotation marked RULED. Quote only "start with & and then we'll see".)
(RULING-5 second addendum: the §0.3 glossary row rev 17 edits (line 682, "**section** | `(& B)`, the macro with only its
OPERAND open (§5.2); a section of the condition, `(h:)`, ... is OPEN") defines a section by its open OPERAND and then
lists `(h:)`, whose open part is the SET; the definition itself needs the second shape if O71 is adopted.)

### RULING-6 (CONFIRMED, doc; effort trivial; blast radius citations only)
(a) §13 O69 line 4067: "the names are OPEN (**tuple-names**; RULED in rev 17, CF:1226 on main)": one clause says OPEN
and RULED; rev 17 should read "the names RULED in rev 17 (CF:1226)". (b) The 23:25 order ruling is cited everywhere
"by date and words, on main only" (lines 6, 382, 389, 2288-2289, 2436, 3439, 4184, 4226) because the lane's branch did
not carry it; in the frozen record it is CF:1250-1254 ("tuple-arg-order: subject low high", CF:1253), verbatim as
quoted. The landing should add the CF line so the provenance table (§15 line 4226) can be checked like every other
row. (c) §2.7 (line 1261-1263, rev 17 hunk; the `compare.width` lint's suggested fix) shows `lex_between2([(h:), (m:)], ...)` as what "the library's tuple
compare ... writes", with no note that `(h:)` is the OPEN spelling (O71); §8 says "each `(x:)` standing for an
accessor", §2.7 does not. A reader of §2.7 alone takes an open question's spelling as the language.

### RULING-7 (CONFIRMED, doc; effort trivial; blast radius §0 rev-16 rulings row (line 375), §8 TUPLE COMPARISONS header, owner question (10))
The owner's "tuple-compare: agree" (CF:1166) answered a question whose premise was "a 2- and 3-field tuple compare is
a plain macro with nothing missing" (question (10) as asked, line 4170-4173; record CF:1167 "plain macros, the bodies of
rev 15's sketch"). Rev 17, by his later direction, replaces those bodies; the new bodies are plain macros only under
TWO READINGS the draft itself labels LEAN, not ruled (line 2352-2355, DECIDED (51): `s[k]` on an array of macros is a
macro; a parameter bound to a macro may be called in a body). The rev-16 rulings row (line 375, "join the first
library as plain macros") and §8's "IN THE FIRST LIBRARY (RULED, CF:1166)" are left reading as if the ruled status
covers the decomposed bodies' plain-macro-ness. The ruling (in the first library, fixed sizes) stands; the row's
third column should add "since rev 17, plain only under readings (a), (b) of §8 (LEAN)". No answer moves.

## PROBED-AND-HELD
- VERBATIM QUOTES (rev 16 and rev 17 rulings tables, §8, §13, changelog): 14 owner quotations checked against the
  frozen record, all verbatim at the cited lines: CF:1154, 1151-1152, 1166, 1170-1172, 1180-1181, 1191-1192, 1202,
  1215, 1226, 1231-1232, 1241, and the 23:25 "tuple-arg-order: subject low high" (CF:1253, uncited, RULING-6 (b)).
- CF RANGES LAND: 1164-1168, 1169-1176, 1178-1188, 1190-1199, 1201-1208, 1214-1221, 1223-1227, 1229-1248; CF:461-480
  (blessed callouts, capability levels); CF:553 (`[]` positional); CF:644/648 (tuple a library macro; `lex_ge` shape);
  CF:749 ("THE SUBJECT IS NEVER AN ARGUMENT", says what §8 (iii) says); CF:890-891 ("interfaces aren't themselves
  values that can be created", says what (iii) says); CF:753 (C33; quotation caveat in RULING-5).
- RECORD vs RULING SEPARATION: "map is an interface in his model" (CF:1243) put in the record column; the manager's
  O70 question (CF:1217-1221) labelled a question; the manager's json.quoted answer (CF:1185-1188) in the record
  column; the blessed-callout CORRECTION (CF:1197-1199) honoured (guarantees from CF:463-466, not the manager's
  candidates); `enumerate` reading (CF:1203-1208) labelled the manager's untested reading and tested separately;
  "illustrative ... his word" verbatim. `any_case` "for now" and "followup": RULED for now + follow-up, matching
  "I am ok with that being a followup"; the "one reading primitive not adopted" is the record's reading of a non-answer,
  and the draft says "CLOSED, NOT as asked" (O67): acceptable.
- THE DEPARTURE FROM HIS LITERAL SHAPE IS ARGUED OPENLY: (iii) and the values-vs-conditions reading are LEAN, named
  "this document's consequence of §4.1's split, not his words" (line 2413-2414) and listed in DECIDED (49)-(50) "so the
  owner sees them"; the order-word "subject" is reconciled with CF:749 in the glossary (line 671). Only the (i) premise
  is mislabelled RULED (RULING-1).
- SIBLING OF A FAMILY: the label section is placed with sections `(& B)` (C33) by the draft itself (O71); the condition
  record `(a: x, b: y)` is not a substitute (an unordered AND, not indexable by position); `each` maps one entry at a
  time and cannot carry the running prefix (true); comparison sets are the 1-field case the array compare extends. No
  single general form should replace these; the one general mechanism the draft misses is the ruled bounded recursion
  (RULING-4).
- GOALS ORDER: the rev 16-17 material serves G0 only partly (RULING-3, missing look-alike rows); G3/G4 unaffected
  (the projection expands at compile time; recursion form in RULING-4 keeps G4's strictly-decreasing-literal rule).
- NOT RUN: the evidence scripts (SIMULATE's lens); no oracle runs needed for a ruling check.
