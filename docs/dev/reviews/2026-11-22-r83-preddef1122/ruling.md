# CRITIC RULING — r83 preddef1122

## Findings


(No model was run by this lens: every finding is a text-against-record check; minimum witness length n/a.)

### RULING-1 — CONFIRMED — design — effort S — blast: core/labels/export details (rejected/rulings), every reader of "rejected by hole-export"
The `rejected:` list of core/labels/export still rejects, "by owner ruling — hole-export", exactly what default-export now RULES:
- core_details.md:649 "neither passes through (only a part label re-exports; candidate (b)) — by owner ruling — hole-export."
  Default-export (record "2026-11-22 OWNER RULING — default-export: protected": "a part used alone ... is NOT exported ... It
  REVERSES hole-export (2026-11-19) and export statement 3 for an unlabelled part") is candidate (b) of hole-export (record
  5694: "(b) neither"). A ruled candidate sits under `rejected:` with a reversed ruling as its reason.
- core_details.md:648 "statement 3 as first ruled, "Outside a binding, what is visible is the public labels written in its own
  literals, and its public part labels" (an unlabelled sequence part exporting nothing, a hole exporting) — by owner ruling —
  hole-export". Record 5694 Class 1: hole-export "REVISES statement 3 of export-rule (2026-11-18 ...)". Reversing hole-export
  restores export-rule's first statement 3 (2026-11-18) for the sequence part AND extends it to the hole; the subject names
  neither (the restored half is no longer rejected; the hole half is new).
- core_details.md:642 and :679 keep hole-export's line ("Agree both pass through"; ":679 the ruled part of statement 3")
  with no mark that it is reversed for an unlabelled part (only the new default-export line :456 says so).
Fix: move both rejected items out (one restored by default-export, one adopted), mark hole-export's two rulings lines
"reversed for an unlabelled part by default-export"; keep "they have to work the same" as standing (hole and sequence
still agree: neither passes).

### RULING-2 — CONFIRMED — design — effort S — blast: label-flow (b), bare-nested-scope case 2 (b), core.md:420-423, :1521-1523
Default-export revises two earlier rulings the subject does not NAME as revised:
- label-flow 2026-11-17 (b): "i adjust my rules to be such that a compose and a literal rx have the same label behavior"
  (core_details.md:614).
- bare-nested-scope case 2 (b) 2026-11-21, as put and ruled: "the compose-equals-literal rule gets an exception: it holds
  for what the user sees, not for what a piece reads inside itself" (core_details.md:1918).
Witness: literal `L := /(?<h>\d)!/` exports `h` (`L.h` legal); composed `p2 := /${A}!/`, A := `/(?<h>\d)/`, exports none
(core.md "Used alone, from outside": a compile error). For the USER the two now differ, which is what case 2 (b) said
still held. The documents leave both sentences standing: core.md:1522-1523 (nested-scope, untouched) "the exception to "a
compose and a literal rx have the same label behavior" (core/labels/flow), which holds for what a piece's USER reads"; and
core.md:421-423 (flow) says in one sentence that "the same label behavior" is for what the user reads AND that the user
reads only what the piece exports (self-contradictory for an unlabelled composition). Only a history line
(core_details.md:631/450 of the diff) concedes it, "now holds ... for the user, where the composition labels its parts
(a reading)". The record's default-export entry names only hole-export and statement 3 as reversed. Fix: name label-flow
(b) and case 2 (b) as REVISED by default-export (rulings lines of core/labels/flow and nested-scope), reword core.md:1522
and :421 to "holds for the user where the parts are labelled"; the record gets a manager CORRECTION line saying so.

### RULING-3 — CONFIRMED — design — effort S — blast: binding-prefix, core/labels/paths, export statement 2, every "[=A]" reader
Three sentences give three different pictures of an implicit binding-name prefix:
- core.md:559 "A binding's name is a prefix of its own, as if a part label `[A = A]` for one use", and core.md:576-577 (binding-
  prefix) "as if `[A = A]`, local to the definition that uses it (exporting nothing ...)". The record's reading (a) of
  binding-prefix (record 7218) is "as if written `[=chars]`".
- core.md:551 (default-export reading (d)): `[=A]`, read `[A = A]`, "is the short way to export a part under its own name
  (`pub := [=A] SEQ "!"` gives `pub.A.h`)".
- core.md:434 (statement 2): a part used alone is reached "as under `[_A = A]`" (default-export reading (a)).
So `[A = A]` both exports (written) and exports nothing (implicit), and the implicit form is both `[A = A]` and `[_A = A]`.
The binding-prefix definition is the one "he liked" ("i like your read", record 7190, a LEAN) and is a reading; default-export
revises it (the implicit label is now protected); the subject must NAME that revision instead of appending "exporting
nothing" to "as if [A = A]". Fix: binding-prefix and core/labels/paths say "as if `[_A = A]` with the local name `A`"
(default-export reading (a)), and its history names the change from `[=chars]`.

### RULING-4 — CONFIRMED — doc — effort S — blast: export statement 3, flat-read-outside, error table
Default-export reading (c) ("a read from outside of a label that only a bare-used part holds (`pub.h`) is a compile error")
is a READING (the error TIER is not in his words "default-export: protected"; it rests on ANS-4, itself "the manager's
reading", record r82 dispositions). It is printed as rule, unmarked:
- core.md:439-440 "a read from outside of a label only such a part holds is a compile error (the line "Used alone, from
  outside")" — the parenthesis closing statement 3's other readings ("(readings; run: ...)") does not cover it.
- core.md:469 (flat-read-outside, ruled, statement line) "a label it does not export is none."
- core.md:480 "outside it is no label, a plain read and a group question alike" (the group-question half also unmarked).
- core.md:1855 error-table row, unmarked where its neighbour row (`c.A.d` "(a reading)") is marked.
Also statement line core.md:428 states reading (b) ("a binding exports the labels its own text writes and those a public
part label passes") as the statement of a ruled piece; (b) is largely export-rule 2026-11-18 ("a binding shows its own
public labels and its public part labels"), so it may stand, but the "by name (`pub.h`)" half is the lane's addition
(core_details history: "the lane's addition ... — a reading") and belongs in statement 3's reading parenthesis only.
Fix: mark each "(a reading: default-export (c), ANS-4)".

### RULING-5 — CONFIRMED — doc — effort S — blast: core/patterns/atomic, call-prefix statement, library peek, list_of
Default-export reading (e) ("a MACRO CALL exports what its body's text writes; an argument the body uses bare is not exported
by the call") is applied as rule, attributed to the ruling, unmarked:
- core.md:274 "`atomic(X)` uses X alone in its body, so a label on the call (`[ab = atomic(B | A)]`, `ab.l`) reaches none of
  X's labels (default-export)" — its own history (core_details diff :434) says "under the manager's reading (e)".
- core.md:629 call-prefix STATEMENT "A macro's name qualifies the labels its call exports, those its body's text writes ...;
  an argument used alone is not exported." (case 1's bullet marks it "a reading of default-export"; the statement does not).
- library.md:250 (peek) "the body uses A alone, so the call exports none of them"; library.md:614 (list_of) "The body uses X
  alone, so the call exports none of its labels" — no reading mark (library.md:218, length, does mark it).
Note on the ground: his words ruled a PART used alone in a BINDING; whether a macro parameter used in a hole is "a part used
alone" of the CALL is exactly what (e) reads; case 1 of call-prefix ("use the macro name as shown") was ruled when the call
surfaced its arguments' labels too (core_details: "its arguments' too: a reading"), so (e) also narrows a reading that rode
on a ruling. Fix: mark the four sites "(a reading, default-export (e))".

### RULING-6 — CONFIRMED — doc — effort XS — blast: two history lines
Two history lines cite manager's readings that the record does not contain: core_details.md:694 "(the manager's reading (g),
SUPPORTED as run, preddef_model.py EXAMPLE)" and library_details.md:283 "(the manager's reading (h), SUPPORTED as run:
preddef_model.py LIBRARY)". The default-export entry's readings are (a)-(f) only (record 7546ff; `awk 'NR>=7510' | grep
'(g)\|(h)'` finds none in the in-force range; binding-prefix's (g) at 7218 is a different subject). The letters presumably
come from the lane's rulings file, which is not the record. Fix: cite them as the lane's readings (or the brief's), not "the
manager's reading (g)/(h)", or have the manager add them to the record.

### RULING-7 — CONFIRMED — doc — effort XS — blast: export-list and binding-list details, core.md:527, :1744
- core_details.md:730 lists under export-list `rulings:` "Agree caveat bindings used to scope labels (A.a: 8)" with no
  `(class: ...)`; the record classes it "an AGREEMENT with the sentence ... and a CAVEAT" (record "2026-11-22 OWNER, on the two
  name spaces"), not a ruling; the documents' own convention marks such items (`(class: STATEMENT)`, `(class: QUESTION)`,
  core_details.md:519, :539). Add "(class: AGREEMENT)".
- core.md:527 (export-list, a ruled piece) states "It is the named binding list with a second target (one form, two name
  spaces: core/modules/binding-list)" unmarked; it is reading (a) of export-list / agreed framing; the target piece marks it
  "(a reading)" (core.md:1741). Mark it.
- core.md:1744 "the hide-label warning is where they meet": that clause is NOT in the sentence he agreed to (record: "Told the
  sentence ... (one form, the named list, with two targets decided by where it stands; bindings and labels two name spaces:
  left of `:` a bare name is a label, on the value side a binding)"), and his caveat says they also meet in a path
  ("bindings used to scope labels (A.a: 8)"); the hide-label observation of the same day narrows that warning further. The
  next bullet (:1745) gives the caveat, so the two bullets disagree on where the spaces meet. Reword: "they meet in a path's
  earlier steps (his caveat) and in the hide-label warning".
- binding-list's `rulings:` (core_details, the entry for core/modules/binding-list) does not list the export-list ruling whose
  DIRECTION ("We should clarify either they are the same thing but different targets or note their space") its two new
  bullets carry; the quote of his caveat in its base (core.md:1745) has no rulings/readings item in that entry, only history.

### RULING-8 — SUSPECTED — design (owner question scope) — effort XS — blast: core/labels/paths/one-use-read (idiom-confirm)
The default-export question put to him included "a part used bare is available locally as `A.h` but exports nothing" (record
7546ff), and he answered "default-export: protected". That ruled sentence is a one-use, local `A.h` read; idiom-confirm (open,
core.md one-use-read piece) asks whether "With ONE use, is a plain read through a binding's prefix (`A.h`) legal". The piece
is untouched by the revision and does not say whether default-export bears on it; statement 2 (core.md:434) prints the line
"Used alone, inside" (`p2 := /${A}!/ & (A.h: <5)`, one use, a plain read) as "(a reading ...)" without pointing at idiom-
confirm. Either default-export is new ground for candidate (a) (the piece should cite it) or it is not (the line "Used alone,
inside" then rests on the open idiom-confirm and should say "open idiom-confirm"). Confirm: the manager rules which, or asks
him in the idiom-confirm question.

### NEXT-REVISION RULING TABLE
In-force entries (record line 7510 to end):
| entry | class | state for the next revision |
|---|---|---|
| analogy, C++ access levels | ANALOGY (validated) | stands as his picture; the four-row table (core.md analogy table) correct; not a ruling |
| discussion `B := A & A`, `C := B & (B.a: 9)` | DISCUSSION | stands; his "always an error" now true for plain read AND group question (the documents' printed line); the entry's own check (group question legal) superseded by default-export, said in history only |
| default-export: protected | RULING | stands; readings (a) supported, (b) stands (export-rule ground; `pub.h` by name a lane reading), (c) and (e) must be MARKED readings (RULING-4, -5), (d) clashes with binding-prefix's `[=chars]` (RULING-3), (f) stands |
| question "some labels but not others" | QUESTION | stands as answered (by part, by `_`, by the list) |
| proposal `[(=year) = isodate]` | PROPOSAL | superseded by export-list (ruled) |
| export-list: yes (+ direction) | RULING | stands; readings (b) table, (c), (d), (e), (f) marked; (a) unmarked at core.md:527 (RULING-7) |
| two name spaces, "Agree caveat ..." | AGREEMENT | stands as agreed framing; needs `(class: AGREEMENT)`; "hide-label is where they meet" not in what he agreed (RULING-7) |
| observation, textually-visible rule vs hide-label | OBSERVATION | open for the r83 fix lane (restate hide-label's trigger, parked/ideas/label-hygiene); not applied in this revision (correct) |
| kinds of reference (question) | QUESTION | open: the name table is PLAN; not applied (correct) |
| "Nothing missed"; combine kinds | ACKNOWLEDGEMENT + IDEAS | open; the two-kind view not applied (correct) |
| two-kind view agreed; "captures can have no label" | AGREEMENT + NOTE | agreed framing, not applied (correct) |
| argument-default (NOT STATED) | to be asked | OPEN, correctly opened; both candidates printed; earlier rulings stand meanwhile |
| capture-export (NOT STATED) | to be asked | OPEN, correctly opened; statement 5 kept, marked |
Earlier rulings the in-force range touches:
| earlier ruling | pair with | state |
|---|---|---|
| hole-export 2026-11-19 "Agree both pass through" | default-export | REVISED (named) for an unlabelled part; but its rejected candidate (b) and export-rule's first statement 3 still listed rejected "by hole-export" (RULING-1); "they have to work the same" STANDS |
| export-rule 2026-11-18 statement 3 "public labels written in its own literals, and its public part labels" | default-export | RESTORED for the sequence part, extended to the hole: not named (RULING-1) |
| export-rule statements 6/7, `[_ = A]` confirm 2026-11-18 | analogy | STAND (rows `[_a = A]`, `[_ = A]`) |
| label-flow 2026-11-17 (b) "a compose and a literal rx have the same label behavior" | default-export | REVISED for the user where parts are unlabelled: not named (RULING-2) |
| label-flow 2026-11-17 proposal "an ambiguous REFERENCE is the error" | discussion B := A & A | STANDS (inside B); outside, superseded by "not exported" |
| bare-nested-scope case 2 (b) 2026-11-21 "holds for what the user sees" | default-export | REVISED, not named; core.md:1522 stale (RULING-2) |
| bare-nested-scope case 1 2026-11-21 | — | STANDS |
| pure-label 2026-11-21, example 1 "is legal. C can see d as a flat look into A" | default-export (e) | STANDS until argument-default; candidate (error) would revise it (named in argument-default) |
| pure-label "`_` labels never export"; captures explicit | default-export, capture-export | STANDS; capture half OPEN (capture-export) |
| flat-read-outside 2026-11-21 "a" | default-export | STANDS, limited to exported labels; "is none" tier a reading (RULING-4) |
| label-reference 2026-11-22 "required" | default-export | STANDS |
| binding-prefix 2026-11-22 parts 1, 2 | default-export | STAND; its definition reading "as if `[=chars]`" REVISED by default-export, not named (RULING-3) |
| idiom-confirm (open) | default-export | OPEN; possibly touched by the ruled "available locally as `A.h`" (RULING-8) |
| call-prefix case 1 2026-11-22 "use the macro name as shown" | default-export (e) | STANDS for a body's own labels; the reading "its arguments' too" withdrawn (named in history); statement's (e) unmarked (RULING-5) |
| call-prefix case 2 lean / closed-argument 2026-11-22 "a" | default-export | STANDS; for a body using the argument alone OPEN as argument-default (named) |
| closed-argument "[ c = B(A) ] does not allow c.A" (statement) | — | STANDS |
| helper-captures 2026-11-22 (b) | default-export, capture-export | STANDS |
| array-in-piece 2026-11-22 (b) | default-export (f) | STANDS |
| array-scope 2026-11-19 | default-export | STANDS (a part label limits the array; unaffected) |
| bare-condition-labels 2026-11-19 "no such label is an error" | default-export (c) | STANDS; it is the ground of the error tier, via ANS-4 (a reading) |
| import-symbols 2026-11-19 binding list, `(=)`, bare `=` first, leave-out `(=, _ = left)` | export-list | STAND; carried over to labels as readings (b), table rows consistent with the three map rulings |
| numbers (core/labels/numbers, 2026-11-19) | two-kind note | STANDS; not applied by this revision |
| count-in-set 2026-11-22 (b), "left of `:` a bare name ... is a label" | caveat (conditions/form) | STANDS; the caveat bullet is a reading, marked |

## PROBED-AND-HELD
- Owner quotes, word for word: every double-quoted string on an added diff line checked against the record by script
  (R/ruling/work/q.py): 31 are record text, 26 byte-exact and 5 exact up to line-wrap whitespace (the analogy, export-list,
  argument-default/capture-export question sentences); none altered. The other 62 quoted strings are printed-line names,
  code fragments or document text, none an owner quote. Hand-checked against their entries: "default-export: protected";
  the four analogy sentences; "A := <label a> B := A & A   C := B & (B.a: 9) here B.a is always an error." (the leading
  "Discussion:" dropped, a fair part-quote); the isodate question and proposal; "Export list: yes. ..."; "Agree caveat
  bindings used to scope labels (A.a: 8)"; "what would A.d mean if d no longer was visible?" (record 7422, the
  closed-argument entry, correctly attributed); "i'd say A.d is legal there"; "is legal. C can see d as a flat look into A".
- History "until then" quotes (not owner words, checked against the previous tree R/tree_prev): 17 of 17 verbatim (one
  elided with "...").
- Status lines and dates on changed/new pieces: export-list "ruled 2026-11-22", capture-export "open capture-export
  2026-11-22", argument-default "open argument-default 2026-11-22", flow/export/flat-read-outside/call-prefix/closed-argument/
  holes/labels "ruled 2026-11-22": each agrees with its record entry; the two open slugs are those the default-export entry
  names "NOT STATED ... to be asked"; neither answer applied (both pieces print both candidates).
- Readings marked correctly: statement 2's `[_A = A]` (a); `[=A]` (d); export-list (b)-(f); the caveat in conditions/form and
  binding-list; length's "a call exports no `ch`"; array-in-piece (f) unchanged.
- The analogy table's four rows against export statements 2, 3, 6, 7 and the ruling: consistent (row `A` alone "protected" is
  ruled by default-export, the other three by export-rule).
- The two-kind view, the reference-kinds question and the hide-label observation are NOT applied as rules anywhere in the
  diff (grep of added lines): held.
- Every line marked "(awaits argument-default)" keeps its printed answers, and argument-default lists the earlier rulings it
  could revise (closed-argument, example 1, call-prefix case 2): the earlier rulings are not silently reversed.
CRITIC COMPLETE
