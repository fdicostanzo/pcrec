# CRITIC ruling: predfold1122 (r82)

## Findings

### RULING-1 — a one-use plain read through a binding's name is folded as ruled, but no owner ruling covers it, and it reverses a ruled 11-17 example of exactly that shape
CONFIRMED (text). Severity: design. Effort: one owner question, or a "(a reading)" mark. Blast radius: core/labels/flow, core/labels/paths/binding-prefix, the line "One use", and call-prefix's "called once, a plain read ... is legal".
- Record 2026-11-17 PROPOSAL, point 4 (COND-FAMILY.md:2957-2958): "4. A . B & (A.h: blah) error. A is a binding not a label and could be ambigous if its used multiple times in an expression". A is used ONCE there. The 11-17 RULING (record :2979-2981) keeps it STANDING: "a binding's name is not a path".
- Record 2026-11-22 binding-prefix RULING, Class (record_in_force:235-237) says the ruling "REVISES his label-flow point 4 ... the error stays for exactly the case he named there, a plain read with several uses; with one use the prefix is legal". That is not the case he named. He named a one-use read and gave multi-use as his REASON.
- What was asked (record_in_force:223-226) was "1. A group question through a binding's prefix reads the settings of every use." and "2. A plain read through the prefix, when the binding is used more than once: (a) ... (b) ...". The lean round's candidate list ((a) legal once / error otherwise, (b) always, (c) "an error as today", record_in_force:196-198) was cut down when the question was restated. Candidate (c) was DROPPED, and with it the only question about a one-use plain read. The only owner words behind one-use legality are the LEAN "i like your read on this except that perhaps it does refer to all".
- Subject: core.md:100-101 (diff +100) says without a mark "A binding's name is a label prefix: `A.h` is h as A surfaces it". The binding-prefix statement (diff +199) is likewise unmarked. The line "One use" (diff +213, `A & B & (A.h: <2)`) is the 11-17 point-4 program with `&` for `.`, and it now HOLDS on `12` where 11-17 made it an error.
- Fix: either mark one-use legality as the manager's reading (the definition he LIKED, binding-prefix reading (a)) and correct the record's class sentence, or ask him: "with ONE use, is `A.h` legal (11-17 point 4 said error)?" Witness length: 2 (`12`).

### RULING-2 — the ruled closed-argument sentence "it reads `d` as it reaches the caller" allows the opposite answer to the subject's printed "A's own d" line
CONFIRMED (text plus the record's own two run lines). Severity: answer. Effort: a mark plus one confirming question. Blast radius: core/labels/paths/closed-argument, core/labels/paths/call-prefix case 2, the lines "A's own d, through the argument" and "Visible through the call", and nested-scope example 1 re-spelled `C := B(A) & (A.d: <100)`.
- What he confirmed (record_in_force:442-444): "`A.d` is legal in the caller exactly where `d` is visible through the call, and it reads `d` as it reaches the caller."
- With B(rx) := `/${rx}-(?<d>\d)/`, "d as it reaches the caller" is, read literally, B's `d`. That is the last mention, and the record's own reading (a) of call-prefix (record_in_force:411-412) defines it so: "`c.d`, and `B.d` by case 1, are `d` as the call surfaces it (the last mention among the body's and the argument's)".
- Under that literal reading `B(A) & (A.d: <5)` gives the "c.d" line: WHOLE `7-3` HOLDS, `3-7` FAILS (record_in_force:410). The subject prints the opposite: WHOLE `7-3` FAILS, `3-7` HOLDS ("A's own d, through the argument", diff +265; "Visible through the call", diff +286).
- The subject joins the two readings without marking the join. call-prefix (diff +252-253) says "ruled with closed-argument: legal exactly where `d` is visible through the call, reading A's own `d` as it reaches the caller". "A's own" is not in the confirmed sentence.
- A second open point: whether A's `d` is still "visible through the call" when the body sets a later `d` (core/labels/flow: across the sequence operator one label, the last mention) is not stated.
- Fix: mark "A's own `d`" as the manager's reading. Put to him: "`A.d` is A's own `d` even where B sets a `d` after it: `B(A) & (A.d: <5)` on `7-3` FAILS. Reply either way." Witness length: 3 (`7-3`).

### RULING-3 — label-reference says the source of a label from an ARGUMENT is "not ruled", but closed-argument ruled it the same day
CONFIRMED (text). Severity: doc. Effort: one clause. Blast radius: core/labels/paths/label-reference.
- core.md label-reference bullet (diff +224-226): "from an argument and from a typed parameter the source is not ruled (the readings there and in core/operators/bindings/macro-types)".
- The record's closed-argument RULING (record_in_force:451-452): "It also settles call-prefix case 2 ... legal, under this condition". The subject itself says so in call-prefix (diff +252, "Case 2 ... ruled with closed-argument") and in closed-argument (diff +285).
- Only the typed parameter is still unruled (label-reference reading (d)).

### RULING-4 — the open zero-condition-binding piece states its (b) two ways: "a compile error" in the question, "legal and never matching" in the printed line labelled (b)
CONFIRMED (text). Severity: doc (the open question as worded is not the question his "open" left). Effort: re-letter the candidates. Blast radius: core/holes/bare-condition/zero-binding.
- core.md question (diff +576): "is it read where it is used, (a), or sealed at its binding, (b), a compile error like a condition naming a label?"
- The same piece's printed line (core.md, unchanged context line after diff +584) is "(b) sealed, its own `0`: WHOLE `7x` FAILS ... FIND-ALL ... []". That is a LEGAL program that never matches. The bullet (diff +583-584) names it a third answer: "read as sealed and legal instead ... never matches (the second line)".
- Record: the slug was proposed 2026-11-21 (COND-FAMILY.md:6664-6665) as "the `0` of the definition it is used in, or its own, empty" (a legal reading). The third asking of bound-condition (record_in_force:56-59) asked "(b) sealed at its binding, a compile error". The ruling entry (record_in_force:118-119) left the `0` case open "neither answer applied".
- So three candidates stand, under two letters. Fix: (a) where used; (b) a compile error at the binding; (c) sealed and legal, its own empty `0`. Letter the printed line to match.

### RULING-5 — bound-condition reverses the 11-14 named-condition form ("call a named condition: `isSmallYear := (year: <2000)`"), and the record does not say so; the subject keeps "it may be bound" in a re-dated ruled piece
CONFIRMED (text). Severity: design (pair check: a later ruling that revises an earlier one without saying so). Effort: one record note plus one subject clause. Blast radius: core/conditions/form, core/holes/bare-condition/bound-condition.
- Record 2026-11-14, "the 'fractional rx'", with his addendum "It would imply (a: digit)(x)" (COND-FAMILY.md:363-374): "`(a: digit)(x)` (call a named condition: `isSmallYear := (year: <2000)`, `isSmallYear(d)`; a plain DEFINE binding)".
- 2026-11-22 bound-condition RULING: "the form A := (x: blah) has to be illegal". His ground is "the only read consistent with the earlier binding decisions". None of the 11-22 entries names the 11-14 form it revises. The CORRECTION entry cites 11-14 ("a MACRO awaiting its target") only to support macro types.
- Subject core.md:643 (core/conditions/form, re-dated "ruled 2026-11-22" by this diff): "A condition is a value of its own kind: it may be bound, passed or put in an array". Every condition names a label or `0`. So after the ruling a condition can be bound legally only when it names just `0` (open) or names no label at all. "Put in an array" by a binding (`cs := [(h: 1), (h: 2)]`) is now the compile error.
- Fix: a record note that bound-condition REVISES the 11-14 named-condition spelling (macro types is its successor direction). Restate core.md:643 as "passed (an argument written in place) or put in an array in place; bound alone it is bound-condition's compile error".

### RULING-6 — value-left reading (d), "the label form is the value form's common case", fails inside a group question
CONFIRMED (the subject's own sentences; hand witness). Severity: design (a reading not read literally everywhere its premise applies). Effort: one clause, or a new question. Blast radius: core/conditions/form/value-left, lib/counting.
- value-left (diff +331-332): "`($h: S)` and `(h: S)` answer alike in every mode ... so the label form is the value form's common case".
- array-vs-passes (core.md:324): the group questions "read the array of a name's settings". core.md:346: "A `$` read inside a group question's set reads the label as it stands where the read is written, the last pass's".
- So `some((h: "7"))` reads the array, while `some(($h: "7"))` (the value form) reads one value, the last pass's.
- Witness: `/(?<h>\d);(?:(?<h>\d);)*/` on `7;1;`. The array is [7, 1], so `some((h: "7"))` HOLDS. The last pass's label is `1`, so `some(($h: "7"))` FAILS.
- core.md:329-330 gives a sharper case: on `7;` the label h is unset while the array is [`7`].
- Neither reading (d) nor value-left says what a VALUE entry means inside a group question (a constant across the array, or refused). Fix: say "outside a group question", and add the case to record-in-some or a new slug. Witness length: 4.

### RULING-7 — label-reference is stated per NAME, but a name can be both written in the definition and surfaced by a used binding; the ruled "Written in place" line depends on which wins
SUSPECTED (confirm by asking, or by a model run of both choices). Severity: answer. Effort: one owner question. Blast radius: core/labels/paths/label-reference, core/labels/labels-vs-captures (array-in-piece lines), core/labels/flow.
- label-reference (diff +217): "A label not written in the text of the definition that references it is referenced with its source ... a bare name is a label the definition itself writes".
- The array-in-piece ADDITION, his "or A SEQ /B definition/", is printed as ruled (core.md:313-315, 321): `A SEQ /(?:;(?<h>\d))*${some((h: "7"))}/`, A := `/(?<h>\d)/`, where the bare `h` "sees A's settings" (WHOLE `7` HOLDS). That was written BEFORE label-reference. Under label-reference, A's settings of `h` are a label "not written in" this definition (reached as `A.h`), while the name `h` IS written.
- If a bare name reaches only what this definition writes, the line becomes the "own" answers (WHOLE `7` FAILS, `7;1` FAILS, record_in_force:11). If the name is one label, the bare `h` silently reaches A's label, which defeats label-reference's purpose.
- Sharper witness: `/(?<h>\d)/ SEQ A & (h: <5)` with A := `/,(?<h>\d)/`, on `1,7`. Last mention (A's) gives FAILS; this definition's own `h` gives HOLDS.
- Label-reference reading (e), "no answer of any printed example changes", was not checked against this mixed case. Witness length: 3.

### RULING-8 — small claims of ruled state or provenance the record does not carry (doc batch)
CONFIRMED (text). Severity: doc. Effort: a word each. Blast radius: the four sentences below.
- (a) macro-types (diff +639-640, core_details history): "written an hour before label-reference was ruled". The in-force record entries carry no times (grep of record_in_force for hh:mm and "hour": 0 hits). Only their ORDER is in the record. Say "written before".
- (b) label-only-group (core.md:375-376): "as recorded with his proposal of the earlier day". The proposal is of 2026-11-09. The libpcre2 rejection was recorded 2026-11-18 with his RECOLLECTION (COND-FAMILY.md:3935-3949; core_details:573-576 has it right).
- (c) label-only-group (diff +80): "every provided body that writes a group for its own use" is unmarked. His words are "occurences et al", and the record's reading (a) is "every provided body". "for its own use" is a further qualifier that exempts `capture`, and is the manager's (library.md:687-688 marks exactly this as a reading). Mark it.
- (d) value-left (diff +333-334): "a default (`h = v`) stays a label form; inside a group question a joint entry stays refused" sits after the clause's "(a reading ...)" and reads as ruled. The default half is the manager's answer to his question (record_in_force:268-271), not his words. Mark it.

### RULING-9 — label-reference: the one item asked "in particular" was not answered, and the whole re-spelling rests on the manager's reading of the silence
CONFIRMED (text); held as correctly marked. Severity: design (process). Effort: one confirmation.
- Asked (record_in_force:276-277): "Say in particular whether the plain `isodate & (year: ...)` idiom is included". His reply does not address it. The reading taken ("included": he states no exception, and his parked idea is the relaxation) is marked as a reading in the subject (diff +223).
- Every printed program re-spelled with a source (alternation, atomic, export, flat-read-outside, tuples, holes/labels, bindings, metadata) rests on that reading. It is the largest unconfirmed fold of the day. Recommend asking for a confirmation "either way" with the re-spelled `isodate & (isodate.year: < 2100)`.

## Part (B): how the manager's readings map onto the subject (each reading: where the subject states it / whether it is marked / the attack)
- array-in-piece (a), "`&` a placeholder": WITHDRAWN by the "or A SEQ" addition. The subject follows the addition (core.md:313-315). The kept reading (d), "the `&` operand inside one definition" (core.md:340-342), is marked. It no longer rested on (a): held.
- array-in-piece (b), a bound piece sees the public labels of the parts it uses: the subject states it only through export statement 2. After label-reference such a read needs `A.h`. The mixed case is RULING-7.
- array-in-piece (c), the four questions alike: core.md:340, marked. Held.
- array-in-piece (e), the path form unchanged: core.md:311. Held.
- bound-condition: the withdrawn reading "laid against the pattern it meets" survives only as the zero-binding candidate (a), correctly open. No kept reading rests on it: checked in bare-condition, pass-start-read, reads and computed-labels. Held.
- bound-condition (a), in place legal, and (b), a set bound alone legal: diff +561-563, marked "Legal (readings)". Held.
- bound-condition (c), the refused definitions respelled: diff +564-566. Unmarked, but it is a consequence and not a reading of his words. Held.
- bound-condition (d), computed-labels withdrawn as a binding form: the piece is retitled and its status stays `reading`. Held. "Used or not" at the binding (diff +558) is marked only as "(the place a reading)". Held.
- correction entry (i)/(ii), the two meanings: diff +635-638, both stated, neither chosen. Held.
- count-in-set (a), the parse: marked. (b), single: marked. (c), nothing fails: marked. Held.
- count-in-set (d), "`$h` alike": marked but fails inside a group question (RULING-6). Joint form: the WITHDRAWN reading is replaced as the record says (diff +332-334). The default half is unmarked (RULING-8d).
- count-in-set (e): superseded by label-reference spellings. Held.
- binding-prefix (a)-(g): all marked in diff +204-211. (e), "a macro's name is not a prefix", was revised by call-prefix case 1, and the subject follows the later entry. One-use legality is unmarked as ruled (RULING-1).
- label-reference (a)-(c): marked (diff +221-223). (d): superseded for macro calls (call-prefix) and for arguments (closed-argument). The subject still says argument "not ruled" (RULING-3). (e): marked, but untested against the mixed case (RULING-7).
- helper-captures (a): marked in call-prefix; unmarked qualifier in label-only-group (RULING-8c). (b) and (d): marked. (c): bodies restated (library). Held.
- call-prefix (a), `X.d` as X surfaces it: marked "(a reading, run)". But closed-argument's confirmed sentence reads the other way (RULING-2). (b): answered by closed-argument. Held.
- closed-argument (a)-(c): marked (diff +281-284). Held.
- Restatements of questions, compared item by item with what he answered: binding-prefix DROPPED candidate (c) and the one-use case (RULING-1). closed-argument's confirm-statement ADDED "legal exactly where ... reads d as it reaches the caller", which he confirmed as put; that is the source of RULING-2's ambiguity. bound-condition's list: 5 items, the `0` item removed by him, rest confirmed, matches. count-in-set, helper-captures, call-prefix, array-in-piece: restated as asked.

## Ruling table (the next revision's, one row per in-force entry)
| entry (2026-11-22) | state | the subject states it right? |
|---|---|---|
| array-in-piece: b | stands (its reading (a) revised by the next entry) | yes; its in-place line needs a re-check under label-reference (RULING-7) |
| adding "or A SEQ /B definition/" | stands | yes (core.md:313-315) |
| bound-condition, his read + two alternatives | his POSITION, made a ruling by "mostly confirmed" | yes; alternatives under-construction, right |
| correcting `B(d & isodate) := (year: < 2100)` | stands (correction) | yes; "an hour before" unsupported (RULING-8a) |
| bound-condition RULING, `c := (0: 5)` open | stands; it REVISES 11-14 `isSmallYear := (year: <2000)` without saying so | mostly; core.md:643 "may be bound" stale (RULING-5); zero-binding question mis-lettered (RULING-4) |
| "illegal meaning a compiler error" | stands (part of the ruling) | yes |
| count-in-set question on `ch` | answered (no ruling) | yes |
| count-in-set: b + three ideas | stands; ideas parked or under construction | yes, except reading (d) inside group questions (RULING-6) and an unmarked default clause (RULING-8d) |
| binding-prefix lean | superseded by the ruling | yes (details) |
| binding-prefix RULING 1 yes / 2 a | stands; REVISES 11-17 point 4 for the multi-use plain read only | NO for one use: folded as ruled on a lean (RULING-1) |
| label-reference question + joint-form answer | the joint reading withdrawn as recorded | yes |
| label-reference: required | stands; the "isodate idiom" sub-question unanswered (RULING-9) | yes, with RULING-3 stale and RULING-7 open |
| helper-captures RULING | stands; label-only group under construction | yes, with RULING-8b/c |
| helper-captures "right" + second example | acknowledgement | yes (library hits) |
| "critical is the @assert macros" | observation, nothing folded | yes (lib/assert details OBSERVATION item) |
| call-prefix: case 1 ruled; case 2 lean | case 1 stands; case 2 settled by closed-argument | case 1 yes; case 2's "A's own d" not in the ruled words (RULING-2) |
| closed-argument question + "does not allow c.A" | his lean, then confirmed | yes (core/labels/paths bullet) |
| closed-argument: a | stands | ambiguous "as it reaches the caller" (RULING-2) |

## PROBED-AND-HELD
- Owner quotes, word for word: all 96 `rulings:` items of 2026-11-2x in core_details.md, library_details.md and parked_details.md. Each "his words" span is a whitespace-normalized substring of COND-FAMILY.md, and each cited record title exists (script ruling/rulings.py, 96 ok, 0 miss).
- Base-file quotes checked by eye: the "His words" bullets of binding-prefix, label-reference, call-prefix (whole), closed-argument, value-left, bound-condition, label-variables, macro-types, label-only-group and zero-binding, and core.md:314's array-in-piece quote. 11 quotes, all verbatim; slug typos ("cound-condition", "closed-arguments", "help-captures") preserved.
- Piece states against the record: binding-prefix, label-reference, call-prefix, closed-argument, value-left and bound-condition are `ruled` (each has a ruling entry). label-only-group, label-variables and macro-types are `under-construction` (the record says so). zero-binding is `open zero-condition-binding` (the record's slug). computed-labels and metadata are `reading`. 11 pieces, all right.
- Open slugs in the diff, against the record: zero-condition-binding (proposed 11-21, left open 11-22), record-in-some and caller-ambiguous (r77-filed, never asked as `**slug**`: pre-existing, not this diff's).
- Pair check: every in-force entry's tags against earlier entries sharing them: label-flow 11-17 (RULING-1), flat-read-outside 11-21 and hole-export (revised, said so), nested-scope case 1 and case 2 (agree), 11-14 fractional rx (RULING-5), label-only group 11-09/11-18 (agree), pure-label 11-21 (agree with helper-captures), joint-in-some 11-21 (kept).
- Minimum witness length reached by the hand witnesses: 2 (`12`), 3 (`7-3`, `1,7`) and 4 (`7;1;`). No model was run: the runs and plants are the MODE-CLOSURE lens's.
CRITIC COMPLETE
