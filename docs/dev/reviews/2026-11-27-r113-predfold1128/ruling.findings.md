# CRITIC ruling — r113 predfold1128

## Findings

### RULING-1 — param-reference line 3 misquoted: the word "own" dropped from "by the caller's own path rules"
CONFIRMED. The record (COND-FAMILY.md:12588, entry "2026-11-27 OWNER RULING — param-reference: "yes all four"...")
quotes line 3 as asked: "Each listed label is read there, by the caller's own path rules, at the point of the call."
core.md:2702 (core/operators/bindings/reference-call, "line 3 as asked") prints "by the caller's path rules", and the
piece statement core.md:2697 repeats "by the caller's path rules". Repro: `grep -n "caller's own path rules\|caller's
path rules" R/subject/COND-FAMILY.md R/subject/core.md` (1 hit record, 2 hits core.md, none with "own").
Script: ruling/py/quotes2.py + q3.py (every multi-line quote in the fold's bullets carrying "his words"/"as asked"/
"as put"/"told to him", 147 single-line quotes + joined bullets; this is the only owner-quote miss; 40 record titles
cited in the fold's hunks, 40 resolve).
Severity: doc (a quote of a ruled statement is not word for word; "own" also carries meaning: the CALLER'S OWN path
rules, i.e. read in the caller's binding, the sender's-own-names sense of argument-place). Effort: one word, two
sites. Blast radius: core/operators/bindings/reference-call statement + bullet.
Also (nit, same piece family): core.md core/operators/bindings/reference quotes lines "1. ... 2. ... 4. ..." as ONE
quoted string with line 3 cut out and no ellipsis; the lead-in says "lines 1, 2 and 4 as asked", so disclosed, but
the quote is a splice, not a contiguous quotation (doc_format quote rules: check; close the quote after 2 and reopen at 4).

### RULING-2 — the WITHDRAWN meaning ("as the body's own") is printed twice, once by the fold, and export-list's own-label bullets now give the rejected answer for `Bo`
CONFIRMED (text; answers by hand regex). The record (carve-out-reading entry, COND-FAMILY.md ~12479) withdraws "in
which case they count as the body's own labels" and rules the DOOR; details core/labels/rule/argument-door
`rejected:` "the listed labels as the body's own (reading B)". The exact clause appears nowhere (grep 0 hits). But the
MEANING is printed:
- core.md:1120 (NEW, the fold's core/labels/export/named-list): "The list takes the named label as the body's own, an
  alias (core/labels/export/export-list)".
- library.md:24-25 (lib/convention/argument-labels, untouched by the fold): "the list on it, `[(=) = x]`, takes every
  label the argument exports as the body's own".
- core.md:1040 export-list statement (ruled 2026-11-22): "the binding takes the listed labels of the part as labels of
  its own (exported; read bare inside it)", and its bullet "A listed name the binding also writes itself is the same
  label, the last mention (a reading)."
Since named-list-use makes a list on a PARAMETER's place real, export-list's bullet now applies there and parts from
the door on the fold's own printed line "The body's own beside the list" (core.md ~688): Bo(rx) :=
`/(?<d>\d)-${[(=) = rx]}/`, Ad := `/(?<d>\d)/`, `Bo(Ad) & (Bo.d: <5)`, WHOLE `3-7`: door + body-own-name = body's d=3,
HOLDS (printed); export-list "same label, the last mention" = the argument's d=7, FAILS. (Witnesses `3-7` and `7-3`,
length 3; python re `(?<d1>\d)-(?<d2>\d)`.) That is exactly problem 2 the owner's lean rejected ("can never change an
answer silently"), and a named list `(=d)` makes it sharper (the body names `d` twice on purpose).
Severity: design (a ruled reading B printed as the rule's own gloss in a new piece; an un-excepted reading bullet that
yields the rejected answer). Effort: re-word core.md:1120 and library.md:25 to the door ("passes ... through the
call"); add to export-list: on a parameter's place the list is a door (core/labels/rule/argument-door), not own
labels; "same label, last mention" covers a part, not a place. Blast radius: export-list, named-list,
lib/convention/argument-labels, every provided body.

### RULING-3 — param-reference line 4's "stays legal, as today" was not so for what he was shown; the fold narrows it by an UNMARKED reading in a ruled piece and lists the conflict only in details
CONFIRMED (text + the committed model). What he was shown (record, named-list-use/param-reference entry ~12530-12560,
the paramref run): "3. checked(B) := B & (B.year: < 2100) ; checked(isodate) == isodate & (isodate.year: < 2100):
the answers of 1", then asked line 4: "A plain parameter that the body places and then reads stays legal, as today."
The BEFORE documents refuse `checked`'s read:
- before/core.md:1024-25 (core/labels/export/arguments): "A macro's parameter is not a part whose labels the body may
  name (core/holes/bare-condition/nested-scope): statement 2 of core/labels/export does not license `rx.d`."
- before/core.md:1124 "a parameter's label inside the body is not nameable (core/holes/bare-condition/nested-scope)";
  before/core.md:2421 "A parameter's name is not a label: "C cannot see rx as its a binding variable not a label"";
  nested-scope statement (ruled 2026-11-22) "the label a parameter holds is not its to name".
- The old engines agree: predfold1128_model.out:39 "at the binding `checked(B) := B & (B.year: < 2100)`: checked names
  a label it does not hold".
- Only an unasked reading said otherwise: before/core.md:2564 (macro-types) "the body would name it through the
  parameter, `d.year` (a reading; not asked)".
So "as today" was true only of placing under the body's own label and reading THAT (nested-scope example 3, `dd`),
false of the example he was shown. How the fold printed it: core.md:2685-86 "- "Places and then reads", as today: the
body places the parameter under a label of its own and reads that label, nested-scope's example 3" with NO "(a
reading)" mark, inside a ruled piece; the conflict ("NOT FOLDED ... listed for him") is only in core_details.md:3154.
The model's guard for it, `rdg[...] = (iso is not None, "run")` (model.py:644), passes on either reading (it reverses
nothing). Still printed and now contradicting line 2/the fold's own macro-types bullet: core.md:2758 "under that
ruling the body would name it through the parameter, `d.year` (a reading; not asked)" beside core.md:2759-61
"meaning (ii)'s promise has a declared form ... `B((=year)) := (year: < 2100)`; a body may name what the list names".
What the owner was told that was not so: that a body may place a plain parameter and read ITS labels (`B.year`)
today. Severity: design (a ruled sentence rests on a false premise; the owner may have ruled line 4 believing
`checked` legal). Effort: mark the core.md bullet "(a reading, the fold's; the owner was shown `checked` as legal,
which today's rules refuse: an owner question)"; mark core.md:2758 REPLACED by param-reference; put the question to
him by slug (e.g. placed-param-read). Blast radius: reference, nested-scope, macro-types, named-list (see RULING-6:
the named list is the natural spelling of `checked`).

### RULING-4 — the strong-lean MARKER: count, and the site table; three over-marks of RULED or lean-free answers, three lean-dependent sentences unmarked
CONFIRMED (grep -F of the exact phrase). Count: core.md 35, library.md 3, core_details/library_details/parked/
parked_details 0 (before: 0 everywhere). Details carry the lean in rulings/readings/history prose only (fine).
Table (states = states the argument rule; depends = its answer moves if the lean is lifted; ruled = the answer is an
owner ruling independent of the lean; free = legal under either reading):
| site | file:line | class | marked | verdict |
|---|---|---|---|---|
| rule/paths readings bullet "a path never passes an argument's place" | core.md:486 | states | y | OK |
| "Through a call, the middle label skipped" `B.h` error | core.md:492 | depends | y | OK |
| stacked-chain bullet + "through the call's label" `X.c.h` | core.md:536, 544 | depends | y | OK |
| "Two binding levels, the sender's label" `X.a.h` LEGAL | core.md:545 | free (caller-label-export rules `Y.a.h`; X over Y skips `y` by rule 4, no place crossed by the export) | y | OVER-MARK |
| alone-as-middle bullet + "through its place" `n.B.p.d` | core.md:591, 604 | depends | y | OK |
| argument-place statement/bullets (piece open) | core.md:639-660 | states | piece bullet y | OK (piece-level) |
| "Through a call, the sender's name" `A.h` LEGAL | core.md:663 | free (shorthand-is-callers, ruled 2026-11-23) | y | OVER-MARK |
| `B.p.h`, `B.a.h` errors | core.md:665, 666 | depends | y | OK |
| door piece "It rests on the base statement" | core.md:675 | depends (the door is moot without the wall) | y | OK |
| caller-label "The error rests on the base statement" + "Through the call's label" `Y.c.a.h` error | core.md:701, 707 | RULED ("`Y.c.a.h` "an error: that path goes through B's argument place"") | y | OVER-MARK: a ruled answer printed "to be confirmed"; only its GROUND is the lean. `Y.c.h alike` in the same line is depends (unruled) |
| caller-label bullet "In the sender's own text ... `pub.A.h` ... and `B.a.h` are compile errors" | core.md:702-703 | depends + a READING (details core/labels/rule/caller-label readings) | n | UNMARKED (neither the marker nor "a reading", in a ruled piece) |
| list-over-label, forwarded-place, sent-over-body-label | core.md:714, 718, 725, 738 | depends (marked readings) | y | OK |
| kinds: shorthand row skippable cell "reaches the argument only through a list on its place (argument-place)" | core.md:754 | depends | n (the bullet core.md:764 covers "The two place rows"; there is ONE place row, the alias row did not change) | UNMARKED / ambiguous cover |
| kinds: caller-label row outside cell "never through ... the macro's name (`Y.c.a.h`, `B.a.h`) (caller-label-export)" | core.md:756 | `B.a.h` depends + reading, attributed to the ruling | n | UNMARKED; a reading cited as ruled |
| kinds place row | core.md:760 | depends | y (764) | OK |
| ownership "labelled" cells | core.md:782-783, 786 | depends | y | OK |
| export statement 3 "of an argument, only what a list on its place passes" | core.md:959 | depends | y | OK |
| named-list "Never satisfiable" bullet + line | core.md:1127-1133 | depends (a RULED edge, its witness lean-dependent) | y | OK |
| call-prefix, closed-argument, argument-default, shorthand-outside, two-sources, nested-scope sites | core.md:1251-1356, 2340, 2415, 2425 | depends | y | OK |
| hits/occurrences/argument-labels | library.md:39, 453, 484 | depends (the reason for the body change; `hits.hit.g` itself free) | y | OK |
Severity: doc (over-marks invite lifting a ruled answer; unmarked sites survive a lift silently). Effort: drop the
marker from 545/663 (or say "free"), re-word 701/707 "ruled; its ground the strong lean", mark 702-703, 754, 756.
Blast radius: one-place confirm/lift, which the manager's decision was built for.

### RULING-5 — earlier rulings param-reference revises are left standing unmarked: nested-scope's statement, label-kinds' `rejected:` item, the parked reference-kind idea
CONFIRMED (text). param-reference line 2: "The body reads the listed names bare" (core.md:2676-77). Against it, unrevised:
- core.md:2395 nested-scope (ruled 2026-11-22) statement: "the label a parameter holds is not its to name"; and
  core.md:1156-57 "A macro's parameter is not a part whose labels the body may name ... does not license `rx.d`";
  core.md:1256. No exception or REVISED mark for a declared reference (the fold's diff touches nested-scope only in
  example 1's bullet).
- core_details.md (label-kinds) `rejected:` "a reference kind for users (a parameter naming a caller's existing label)
  — by owner ruling — "stays off limits for users until we see a valid, safe set of rules for it"" with no REVISED mark,
  beside the new rulings item "REVISES this piece for users".
- parked.md:219 parked/ideas/reference-kind "parked 2026-11-23", Trigger: "a valid, safe set of rules for it (his
  words)": the trigger has fired (the record: "these four lines are that set of rules, for users"); parked.md is
  unchanged by the fold (0 hunks). It should be closed or narrowed (the LABEL-MARK reference `A(a:, B) := B & (a: 5)`
  stays an error, core.md "The reference kind by the label mark"; the declared list is the taken form).
Severity: doc/design (a ruled statement contradicted without its exception; a parked trigger fired and unrecorded).
Effort: three marks. Blast radius: nested-scope, label-kinds details, parked.

### RULING-6 — what the five rulings plus the lean imply that the documents do not state (cells, deciding sentence, proposed reading, unlock + trigger)
SUSPECTED (undecided cells, by text; none run). Probes read: core.md reference (2667-2695), reference-call
(2696-2717), named-list (1110-1133), export-list (1039-1069), argument-door (668-692), nested-scope (2394-2412),
call-forms, label-kinds.
| cell | deciding sentence | proposed reading | unlock / trigger |
|---|---|---|---|
| a placed parameter's NAMED list read in the body: `N(rx) := /${[(=h) = rx]}/ & (h: <5)` | CONFLICT: export-list core.md:1040 "(exported; read bare inside it)" and core.md:1120 "as the body's own" say legal; nested-scope core.md:2395 "the label a parameter holds is not its to name" says error | legal, the body reads only what its list names (param-reference line 2's rule, for a placed parameter); it is the owner's stated PURPOSE: "a macro that simply needed the form to match like accepting a date looking argument to calculate the leap or day of week" | gives `checked`'s honest spelling (`checked(B) := /${[(=year) = B]}/ & (year: < 2100)`), RULING-3's cell; TRIGGER: fires now (his named purpose); ask with RULING-3 |
| a reference beside a label parameter in one head, `f(l:, (=year))`; may the list name it, `(=l)`? | undecided (call-forms "positional entries first, then named" never places a reference entry) | a reference is a positional entry; `(=l)` a compile error (a label parameter is a name, not a caller's label) | a macro that sets a label and tests a caller's beside it; TRIGGER: the first such library macro, or the call-mark question |
| a reference to a label set many times (a loop, `rx.repeat([d = isodate])`, `[d = ..]` placed under `*`) | undecided: line 3 "a name used twice" covers two PLACEMENTS, not one placement looped; "read there ... at the point of the call" | the last pass (label flow); the array only by an explicit `@` entry in the head list, refused for now | `some(@year, ..)` in a reference body; TRIGGER: a macro over a repeated field |
| a reference inside a group question, `some(@h, before2100)` | undecided | a compile error for now: an array slot is not "a name of something the caller has placed" | per-element macro tests over `hits`; TRIGGER: a library ask |
| the export-list forms in a head: `before2100((=))`, `((=, _ = month))` | core.md:2684 "The head's list has the export list's forms" makes them legal; line 1 "the list of labels it needs" and line 2 "can read nothing ... the head did not list" argue a named list only | `(=)` and all-but-one refused in a head (a wildcard is a secret dependency, his "declared then enforced") | none needed; TRIGGER: the spelling step |
| does a reference call export its listed labels (`[r = before2100(d)]`, `r.year`)? | undecided | no: the body places nothing; the caller already reads `d.year` | none |
| a renamed named list `[(y = year) = rx]` lacking `year`: which name the use error names; `N.y` through the door | named-list's "names the missing label and the list that demands it" (told to him) | names the ARGUMENT's `year` and the list `(y = year)`; `N.y` reads the alias by the door | TRIGGER: the first renaming list in a provided body |
| an argument holding `h` in TWO labelled parts, `N([a = P] SEQ [b = Q])`, N's list `(=h)` | CONFLICT: the ruled edge "an argument setting the label twice is legal and reads the last" vs one-path (two labels reached by a skip, a compile error); only `/(?<h>\d)(?<h>\d)/` (one label, label flow) is printed | one-path decides: a use error naming both `a.h` and `b.h` (the edge is about one label set twice) | TRIGGER: now (a ruled edge's scope) |
| a gate / wall / underscore group in the argument: named list | core.md:1122 "(none, one behind an underscore label, one used alone in it)": only "none" printed | each the use error, `(?<_h>..)` too (export 3) | print two lines |
| the same in a reference argument (`D := isodate SEQ "!"`, `D & before2100(D)`; `[_d = isodate]`) | line 3 "by the caller's own path rules": `D.year` crosses a part used alone (rule 6) | "a missing label" naming the path rule that hides it | message wording only |
| the same for a plain parameter with `(=)` | transform-export + export 3 | unchanged | none |
| a label two levels above the call in the sender's own text, `[k = B([a = A]) SEQ "!"] & (k.a.h: ..)` | undecided in the documents; the model's PLACE128 reading (model.py:11-16, 116: "the step's start is neither the call nor a label directly on it") makes it LEGAL while `c.a.h` on `[c = B(..)]` is an error | as the model, if `Y.a.h` from outside is the analogue; but the base lean "a path never goes through an argument's place" refuses it: an engine reading with no document sentence | ask with the strong lean's confirmation; print the line |
Severity: design. Effort: one question round (two cells fire now). Blast radius: named-list, reference, one-path.

### RULING-7 — the GENERAL FORM: the named list, the declared reference and the export door are one family, a parameter's declared label interface; the documents hold its members as four unrelated pieces
SUSPECTED (design synthesis from text; standing question). Members today, each quoted:
- named-list (core.md:1111): "A body's list that names a label (`[(=h) = rx]`) requires the argument to have it: ... a
  compile error at the call" — a PLACED parameter with a declared demand, written at the place.
- reference (core.md:2668): "A reference parameter is declared in the head as the list of labels it needs" — an
  UNPLACED parameter with a declared demand, written in the head; "It can read nothing of the argument that the head
  did not list".
- lib/convention/argument-labels / transform-export: `[(=) = x]` on every spot — a placed parameter, interface "all".
- macro-types (ii) (core.md:2756): "a promise checked at the call that x holds isodate's labels" — an interface named
  by a binding's exports; the fold's own bullet (2759) already says param-reference gives (ii) "a declared form".
- label-kinds' natives reference kind (`weekday_of($rest.year, $rest.month, $rest.day)`, lib/planned/standard) — an
  unplaced interface by value, natives only until now.
- bound-condition's general form "every label a binding's body names has its target in it" — the interface IS the
  target the head supplies (the fold's bullet, core.md ~2461).
The general form: every parameter may carry a DECLARED LABEL INTERFACE in the export list's named forms; it is
checked at the call (one use error: the missing label and the list that demands it), traces through forwarding, and
is the body's ONLY access to the argument's labels (read bare, through the door for callers); orthogonal to it,
the parameter is PLACED (a pattern) or NOT (a reference). The four lines, named-list-use's three edges and the door
are then one rule set, and the strong lean reduces to "an undeclared interface is empty".
Unlocks, with triggers: (1) the owner's named-list PURPOSE (leap / day of week of a date-shaped argument) and
`checked` (RULING-3) get one legal spelling, placed + declared — TRIGGER: now (both open); (2) macro-types (ii)
closes as "interface = a binding's export set" (e.g. a placeholder `(=isodate)`), (i) stays the pattern restriction
— TRIGGER: macro-types next asked; (3) the call-mark question ("whether the CALL also carries a mark", left for
later) is asked once for both forms — TRIGGER: the spelling step; (4) the head list and the place list become two
spellings of one fact, to be chosen once (placeholders today) — TRIGGER: the spelling step; (5) natives' reference
kind becomes the same declaration, so `weekday_of` can be written as a user macro of the library — TRIGGER: the
planned-standard natives are defined. Cost: none to answers; it is a re-statement plus RULING-2's export-list
exception. Severity: design (the forest-for-trees lens: four siblings, no unified piece). Effort: one piece + pointers.

### RULING-8 — hits-through-hit (the manager's call) rewrites the STATEMENT/body of two ruled pieces with no mark on the changed line, and opens reads nobody states (`hits.g`, `occurrences.n`)
CONFIRMED (text). library.md:429 lib/search/occurrences "ruled 2026-11-22", statement now "`/(?:(?s:.*?)(?<:hit>${[(=)
= x]})){${min},}(?s:.*)/`", and library.md:474 hits' body "`(?<:hit>${[(=) = r]})`": the changed lines carry neither
"the manager's call" nor a pointer; the mark sits in a later bullet (library.md:453, 484) and in details rulings
items ("THE MANAGER'S CALL"). The brief's requirement (marked as the manager's call, not the owner's) holds at the
bullets and details, not at the statement a reader quotes.
Implication unstated: by the door (core.md:669 "a path may pass it, and one-path and body-own-name apply to what is
reached") and one-path, `hits(/a(?<g>x)?/) & (hits.g: ..)` and `occurrences(/(?<n>\d+)/) & (occurrences.n: ..)` now
skip `hit` (a written label, skippable by one-path when one `g` is in view) and the alias and place: legal, the last
hit's — new reads the old body (a label only) refused under the lean and allowed before it by rule 4. Grep: no
printed `hits.g`/`occurrences.n` (0 hits). And `hit` is one label set once per pass (one label, label flow), so
one-path does not refuse it; is that the intent?
Severity: doc. Effort: mark the two body lines "(hits-through-hit, the manager's call)"; one line each for `hits.g`.
Blast radius: lib/search.

## PROBED-AND-HELD

- Owner quotes: 147 single-line quoted strings in the fold's added lines + every joined bullet carrying "his words"/"as
  asked"/"as put"/"told to him" checked word for word against COND-FAMILY.md (ruling/py/quotes.py, quotes2.py); the
  only owner-quote miss is RULING-1; the other misses are printed-line titles and verbatim history text (not owner
  words). 40 record titles cited in `(record: "...")` in the hunks: 40 resolve to a `### ` title.
- The withdrawn clause "in which case they count as the body's own labels" / "count as the body's own": 0 hits in all
  six documents (its MEANING: RULING-2). The argument-place quote (core.md:642-644) ends at "export list", the clause
  left out, and the rulings item says WITHDRAWN.
- gate-beside-direct: the mark became the ruling at both sites (core.md:516 his words, :525 "(gate-beside-direct)"),
  details rulings item + REPLACED reading; gate-beside-label still stands for an all-skip read (core.md:595).
- carve-out-reading: the statement as asked quoted (core.md:672-674) and the lean as put; his observation printed as an
  observation with the manager's reading ("available today"), the line "His remedy"; reading B rejected in details.
- caller-label-export: both sentences (the first reading; the underscore label, line "Kept in by an underscore label",
  `[_a = A]` refused `Y.a.h`); stacked-chain `X.c.h` re-spelled `X.a.h`.
- named-list-use: the three edges each printed (Set twice, Through a forwarding body, Never satisfiable) and the told
  message ("names the missing label and the list that demands it": the lines' messages name `h` and `(=h)`); the old
  definition-error line moved to `rejected:`.
- param-reference: the four lines printed (1, 2, 4 in reference; 3 in reference-call, RULING-1's word aside); each line-3
  error is a printed line (pattern in place, missing label, name twice, read before the match); "Left for later: the
  call mark" printed; label-kinds' statement revised and its rulings item says REVISES; the label-mark reference stays a
  compile error naming the list form.
- hits/occurrences: marked as the manager's call in bullets and both details rulings items ("told to him, no
  objection") (RULING-8 for the statement lines).
- The three unasked questions (list-over-label, forwarded-place, sent-over-body-label): each an `open` piece, the printed
  reading marked "a marked reading; not asked", the other reading stated with its run (answers or the switch).
- Earlier-ruling pairs checked: label-kinds (RULING-5), body-own-name/one-path (agree: `Bo.d` body's own), gate-beside-
  label (agree), shorthand-outside (agree: its ruling was the shorthand only; the written-out contrast was a printed
  line, not ruled; the fold moved it, the record's manager reading "the contrast stands" is reported in details as
  SUPPORTED in a moved form only), shorthand-is-callers (agree: same read, not same export), argument-label/closing-
  own-label (agree), bound-condition (an exception stated by the fold's bullet), nested-scope (RULING-5).
- Witness lengths of my own probes: 3 (`3-7`, `7-3`, RULING-2); no other run of mine. Model not re-run (the coordinator's
  verdicts read: 16 checks, 0 failed; lint 10524/0).
CRITIC COMPLETE
