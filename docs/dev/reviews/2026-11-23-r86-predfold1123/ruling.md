# CRITIC RULING: predfold1123 (review r86)

## Findings

### RULING-1 — zero-open is folded as ruled in five pieces but carried by NO `rulings:` item anywhere ("to add at the merge", never added)
CONFIRMED. Record 9402 "2026-11-23 OWNER RULING — zero-open: yes, all four (...)" is IN the freeze record and in scope
(record_in_scope.md 1395). The fold prints its consequences as ruled: core/conditions/match-so-far (status `ruled
2026-11-23`, base quotes "zero-open: yes all 4" and the observation of record 9370), core/values/reads (`$0` legal),
lib/counting/some (no settings), lib/structural/capture (request only on a complete `0`), core/diagnostics/warnings
(`pcrec.default.unused` on `0`). Yet each details entry says, in history only: "the zero-open entries are recorded on
lane/pred-rev28 after this lane's cut, so they are cited here in history only (...), not as a `rulings:` item (lint L4
would fail on this worktree's record; to add at the merge)". `grep 'zero-open' core_details.md library_details.md`:
no `rulings:` item, no `slugs:` entry. The owner's observation (record 9370, "All other labels are completed at the
condition. 0 is not. ...") is quoted in the base and has no class item either. core/values/reads keeps status date
2026-11-22 "for the same reason" though its `$0` sentence rests on a 2026-11-23 ruling. Expected: rulings items
(zero-open; 9370 as class OBSERVATION) in core/conditions/match-so-far and each consequence's piece, `slugs:
zero-open`, reads re-dated 2026-11-23. Severity: doc (the ruling's ledger is missing; a ruled base quote with no
rulings item is exactly what L4 exists to catch, defeated here because match-so-far has OTHER items). Effort: small.
Blast radius: 5 details entries. Location: core_details.md core/conditions/match-so-far, core/values/reads;
library_details.md lib/counting/some, lib/structural/capture; core_details.md core/diagnostics/warnings.

### RULING-2 — optional-label's ruled conservative edges are dropped, one reversed by a reading (value left part printed LEGAL)
CONFIRMED. Record 8882: optional-label was "ASKED AS A RULING (slug optional-label: `(h?: S)` holds when h is absent or
in S, as a general entry form; the conservative edges proposed: `?` on a joint entry's label, on a value left of `:`,
inside a group question are compile errors for now; if yes, the capture shape is ...)"; he answered "optional-label:
yes." The fold takes the capture shape from that same statement "by the statement he answered" (lib/structural/capture)
but drops the three edges. Then record 9034 says of optional-place: "Not ruled by these words: the operator form
itself (his "perhaps"), the joint and value cases, `(a?, b)`, `h+` / `h*`". So the ruled state for a value left part is
"a compile error for now". core/conditions/form/optional-entry instead prints, as the manager's reading (a), "a value
when it is nothing (the line "A value left part")" with a LEGAL run line (`(($a + $b) ?: <10)`: WHOLE `3,4` HOLDS ...),
and "a joint holds when a part has no value" (also not ruled). The group-question edge appears nowhere (`?:` inside
`some(..)`: no sentence in the piece or in lib/counting/some). The details' rulings item restates optional-label as
"`(h?: S)` holds when h is absent or in S, as a general entry form" with no edges. A manager's thought (record 8971
(a), "none ruled") reverses a ruled refusal. Expected: the value and group-question edges stated as compile errors for
now (ruled, optional-label), the joint/value generalisation kept as an open reading pending his word. Severity:
answer (a program the ruling refuses is printed with answers). Effort: small. Blast radius: optional-entry base +
details, the line "A value left part", lib/counting/some. Location: core.md core/conditions/form/optional-entry;
core_details.md same entry.

### RULING-3 — the owner's FLAG optional-label-general (to be filed as an open item) is closed by a manager's thought
CONFIRMED. Record 8882: "flag an item to see if this is a special form or general" — the record: "a FLAG he asks to be
filed, an open item, slug optional-label-general". Record 8971: his answer is a LEAN, "I think the ? In conditions is a
special case, but I'm trying to figure out how special" ("how special" is open in his words; "optional-label-general
not answered by letter"). Record 9034: the `?:` operator is his "perhaps"; the manager's (b) "It closes
optional-label-general as "special, and not a quantifier"" is one of "the manager's thoughts (...; each marked, none
ruled)". At the freeze no piece is `open optional-label-general` and no bullet calls it open: core_details
core/conditions/form/optional-entry files the slug and writes "the manager's thought (b) on optional-place: his `?:`
closes optional-label-general"; the base says "`h+`, `h*` and `(a?, b)` are not forms: there is no mark on a label to
generalise (the manager's reading (b))". Expected: an open bullet (or open line) for optional-label-general, his lean and
the `?:` lean as its standing state. Severity: design (an owner-requested open item disappears). Effort: small. Blast
radius: optional-entry. Location: core.md and core_details.md core/conditions/form/optional-entry.

### RULING-4 — r84 C3 not closed: argument-default still REJECTS "the middle (labelled)" "by owner ruling, as the manager read it", which argument-label made the documents' own answer
CONFIRMED. core_details.md core/labels/paths/argument-default `rejected:` still reads: "the middle (labelled), a read
only through a label the caller writes on the argument (`B([a = A])`, `a.d`) — by owner ruling, as the manager read it
— "A parameter like rx in a call B(rx) cannot be labeled ..."". That line IS reading (a) of record 7945 ("(a) the middle
(labelled) is refused by his words") — the exact "as the manager read it" phrase review r84 C3 named. Record 8770
(argument-label) WITHDRAWS readings (a) and (b), and the base now prints `B([a = A]) & (a.d: <100)` legal while `A.d`
stays an error: i.e. the documents now state the "middle (labelled)" candidate itself. The fold marked readings (a)/(b)
"[WITHDRAWN ...]" in `readings:` but left the `rejected:` line naming the same candidate as rejected by owner ruling.
Record 8912 C3: "readings (a) and (b) are withdrawn". Expected: the rejected line moved to history (withdrawn with
reading (a)); no candidate listed as rejected by owner ruling that a ruling of the range adopts. Severity: doc (status
word wrong on a live answer). Effort: trivial. Blast radius: one details line. Location: core_details.md
core/labels/paths/argument-default `rejected:`.

### RULING-5 — caller-ambiguous still REJECTS "(b) h absent from the captures" by owner ruling, which is now the printed answer
CONFIRMED. core_details.md core/labels/export/caller-ambiguous `rejected:`: "(b) h absent from the captures; (c) ...;
(d) ... — by owner ruling — export-rule statement 5 (the caller's captures follow the program's rules, where a shared
public name is an ambiguous reference)". The fold replaced statement 5 (capture-export, record 8111, "1. no") and the
base now says "Below, `A & B` gives the caller nothing" — candidate (b) exactly. The cited ground (statement 5 as it
was) no longer exists. The readings line "pending a ruling (...) — favours (a) or (e); not ruled" also still stands as
if the question were open. Expected: (b) recorded as the answer by capture-export (1 no), the rejection and the stale
reading moved to history. Severity: doc. Effort: trivial. Blast radius: one details entry. Location: core_details.md
core/labels/export/caller-ambiguous.

### RULING-6 — core/labels/labels-vs-captures calls capture-loop-value "not stated", which array-capture CLOSED; and keeps pure-label's "a group in rx text is a capture" against capture-export
CONFIRMED. core.md core/labels/labels-vs-captures (ruled 2026-11-22, untouched by the fold): "What the caller receives
for a captured label that a loop sets, PCRE's carried value or the label's last-pass value, is not stated (a reading)".
Record 8598: "capture-loop-value is CLOSED as (a), the label" (array-capture, ruled; lib/structural/capture now says so).
Same piece: "A group written in rx text is a label and a capture; ... what the caller gets is the captures" — record
8111 rules a named group in a part of a composed program is NOT a capture by default and "REVISES pure-label of
2026-11-21 ("captures are explicitly written either in literal form ...") for the literal form inside a composed
program"; core/labels/label-only-group likewise keeps "a user's own literal keeps pure-label, its named group a capture".
The revision of pure-label is noted in no details entry: the pure-label quote stands unannotated as a `rulings:` item in
four core entries and lib/structural/capture. (The contradiction half overlaps FIXIND; the open-question-the-record-
answers half and the unmarked revision are this lens's.) Expected: the loop sentence states the closed answer (the
label) or points at lib/structural/capture; pure-label items annotated "revised by capture-export (1 no) for a composed
program". Severity: doc (a closed question printed open; a revised ruling printed whole). Effort: small. Blast radius:
labels-vs-captures, label-only-group, five pure-label items. Location: core.md core/labels/labels-vs-captures,
core/labels/label-only-group; core_details.md/library_details.md pure-label items.

### RULING-7 — r84 C4 only partly closed: argument-default and call-prefix still state WHICH spots make `A.d` visible as settled by the rulings
CONFIRMED. The fold fixed the mark in core/labels/paths/closed-argument ("WHICH spots make `d` visible through the call
is the manager's reading on his ruling"). But core.md core/labels/paths/argument-default (ruled) keeps, unmarked: "it
settles call-prefix case 2 and closed-argument's "visible through the call" in the strict sense: visible only where the
body puts a label on the spot (his example 3, `[dd = rx]`) or passes the labels on" — the very sentence predfix84's
history says "is review r84 C4's, left for the fold lane". And core/labels/paths/call-prefix case 2: "by closed-argument
and argument-default: legal only where the body labels the spot or passes the labels on" (unmarked). Record 8912 C4:
"WHICH spots make it visible is the manager's reading"; the owner's argument-default words are about a body using the
argument alone, and his principle ("label ... to the spot") points at `B.p.d` (r84 C4), not `A.d`. Expected: both
sentences marked as the manager's reading as closed-argument now is. Severity: doc (a reading printed as ruled in two
ruled pieces). Effort: trivial. Blast radius: two bullets. Location: core.md core/labels/paths/argument-default (bullet
"His example 1"), core/labels/paths/call-prefix (bullet "Case 2").

### RULING-8 — "one literal stays plain PCRE" printed unmarked in RULED export statement 5 and as "The seam, stated" — the record says "not ruled by these words"
CONFIRMED. core.md core/labels/export (ruled), statement 5: "The caller's captures are those the program asks for ...:
a named group in a part of a composed program is no capture by default (...); one literal stays plain PCRE." —
unmarked. core/labels/export/capture-export (ruled): "- The seam, stated: a one-literal program returns PCRE's carried
value for a group; the same group requested in a composed program returns the label" — unmarked. Record 8111 reading
(b): "a program that is ONE literal stays plain PCRE, every group a capture, numbers included (said to him twice the
same evening, not objected to; not ruled by these words)"; record 8598 reading (b): "the seam stands and is to be
stated" — a manager's reading. The capture-export bullet two lines up marks the same fact "(reading (b))", and
lib/structural/capture marks it "(a reading)": the two ruled-piece sentences do not. Expected: "(a reading)" on both.
Severity: doc (design-relevant: the one-literal/composed seam decides what a caller receives). Effort: trivial. Blast
radius: two sentences. Location: core.md core/labels/export statement 5; core/labels/export/capture-export bullet "The
seam, stated".

### RULING-9 — six more manager readings/answers printed unmarked inside RULED statements or ruled bullets
CONFIRMED (each quoted from the freeze base; the record's class in brackets):
(i) core/conditions/match-so-far/in-loop STATEMENT: "...; a per-pass test is a label on the part." [record 9217: "The
manager's answers (told to him; marked)"; his own words give the picture `[prefix = (/\d/)] seq (prefix: /\d/)` but rule
only (b)]. (ii) core/holes/bare-condition/zero-binding STATEMENT: "is a compile error at its binding, for now; written in
place, or passed as an argument, it is legal." ["at its binding" = reading (a), in place/argument = reading (b), record
8143 "The manager's readings (marked)"]. (iii) core/filters/negation/effects STATEMENT: "An effect (a form whose meaning
is more than which texts it accepts; today the capture request) cannot stand under a negation, `NOT` or `!`, at any
depth" [the definition is reading (a), "`NOT` or `!` ... at any depth" reading (b), record 9156; his words: "any effect
macro cannot be under negation"]. (iv) core/conditions/form/optional-entry base: "Ruled: the mark is the entry's, before
the colon." [record 9034 is class OWNER, not OWNER RULING: "taken as the ruling ... (the reading taken, told to him so he
can object)"; the details entry says so, the base drops it]; and its STATEMENT generalises to "its left part" (joint,
value), which 9034 says is "Not ruled". (v) core/labels/flow (ruled) bullet "for names read at ONE level ..., never
across the bare / sourced line" [record 9196: "two-sources' second shape is CLOSED by the manager on label-reference (no
new owner ruling; he may object)" — the manager's restatement; details marks it a reading, the base does not]. (vi)
library.md lib/structural/capture (ruled): "On `0` only where `0` is complete, `rx & capture("name")` or a hole written
last" ["written last" is zero-open reading (a), record 9402] and "After a loop the caller gets the label as a plain read
gives it: the last pass's own value, unset where that pass set nothing" [record 8598: the manager's answer to his
question, "the precise statement"; the ruling is "closed as the label"]. Expected: "(a reading)"/"(the manager's)" on
each, statements reduced to what the ruling carries (format: statement = "the current rule"; doc_format STATUS `ruled`
= "the owner ruled it"). Severity: doc. Effort: small. Blast radius: 6 pieces. Location: as named.

### RULING-10 — four owner quotes are not word for word
CONFIRMED (record line vs document):
(i) core_details.md core/operators/bindings/label-variables, (class: PROPOSAL) item: "... A(l:,B) := [l = B] or
A(l:) := /(?<:${l}>\d)/ then A(x:) & (x: 5)." — record 8323: "A(l:) := /(?<:${l}>\d+)/" (the `+` dropped; the base's own
run line uses `\d+`). (ii) library.md lib/json/members: "(his string-label words: "the row's label argument is set to
the unquoted portion")" — those are the RECORD TITLE's paraphrase (record 9068 heading), not his words; his words: "the
row() label arg would be set to the unquoted portion of the string". (iii) core_details.md
core/operators/bindings/label-omitted `rulings:` prints ONE quotation "i agree that _ should be the unspecified label-
it also comments on your meaning. we currently don't have overloading ... regardless of labels. label args are not
special by position or requirement. ..." — record 8387 order is "...this is two+ questions. we currently don't have
overloading ... regardless of labels. i agree that _ should be the unspecified label- it also comments on your meaning.
also, label args are not special ..."; sentences reordered and "also," dropped inside one pair of quote marks. (iv)
library.md lib/structural/capture: "His words: "optional-label: yes." answered the statement that the request's shape
is `(h: capture("h"))`, ..., `(h ?: capture("h"))`" — the statement put (record 8882) wrote `(h?: capture("h"))`; the
fold re-spells the statement he answered into a later lean's spelling without saying so. Severity: doc. Effort:
trivial. Blast radius: four items. Location: as named.

### RULING-11 — class words in details items differ from the record's class, and two `rejected:` lines are "by his lean"
CONFIRMED. (i) string-label (record 9068) is class "a CLARIFICATION of his own remark (DISCUSSION; a design intent for
the JSON library, not a language ruling)"; filed "(class: DIRECTION)" in core_details core/operators/bindings/
label-forward and library_details lib/json/members. (ii) items from non-RULING entries filed with no `(class: ...)`,
reading as rulings: core/labels/export/arguments "2026-11-23 "this aligns with my understanding."" (record 8676: "an
AGREEMENT"; argument-export "the reading taken, told to him so he can object"); core/labels/paths/two-sources
"2026-11-23 "two-sources: isn't the A.h not visible bare?"" (record 9196: "a QUESTION ... (not a new ruling)");
core/conditions/form/optional-entry "Before the colon: ..." (record 9034: OWNER, an ANSWER taken as a ruling, and a
PROPOSAL) and "I think the ? In conditions is a special case, ..." (record 8971: "A LEAN", "NOTHING RULED"). The
neighbouring items of the same lane use `(class: AGREEMENT)`, `(class: PROPOSAL)`, so this is inconsistency, not
format. (iii) `rejected:` takes "by <owner ruling | run | review rN>" (doc_format); optional-entry rejects the ruled
spelling `(h?: S)` "by his lean on optional-place", and label-default rejects `l: ts` "by his lean": a lean presented as
deciding (9034: "Not ruled by these words: the operator form itself (his "perhaps")"; 8427: "a SPELLING LEAN, not a
ruling"). Severity: doc. Effort: trivial. Blast radius: 7 items. Location: as named.

### RULING-12 — label-omitted prints a "lane's reading" with no record ground that reverses the manager's reading (c) of the same ruling
SUSPECTED (design; what would confirm: the manager's word on reading (c)). core.md core/operators/bindings/
label-omitted: "A body that places its label parameter and then reads it, passed `_`, reads its own placement under a
private name (the lane's reading; the second line)", with a legal run line (`C(_:)`, C(l:) := `/(?<:${l}>\d)/ & (l:
<5)`: WHOLE `3` HOLDS). Record 8387 reading (c): "A body that READS a label parameter (...) called with `_` is a
compile error at the call: there is nothing to read"; reading (b): "`_` is the unusable name"; core/labels/export
statement 7 / core/modules/leave-out: `_` is the leave-out's unusable name. label-kinds (record 8504) later moved the
NEVER-placed case to the definition, but nothing in the range speaks to the placed-then-read-with-`_` case, so the
standing marked reading is (c), a compile error, and the fold prints the opposite answer on a source class ("the
lane's reading") that the record does not have. Severity: answer (a program the standing reading refuses is printed
with answers). Effort: small (mark it open / revert to reading (c) / ask). Blast radius: one line, one bullet, details
reading. Location: core.md and core_details.md core/operators/bindings/label-omitted.

## Ruling table

The NEXT RULING TABLE, record lines 8008..9402 (49 entries; record line = record_in_scope line + 8007). State: stands /
retired / reversed / open / discussion-only. Carried = file + piece tag, or "not carried". "core" = core.md(+details),
"lib" = library.md(+details), "parked" = parked.md(+details).

| rec line | entry (class) | state | carried | note |
|---|---|---|---|---|
| 8008 | OWNER Q transform-export `A(rx) := /${=rx}/`, `(A.rx: 6)` | discussion-only | not carried | manager's yes + readings (a)-(c) (A.rx the spot's text; no hide-label warning for `=`; spelling) not folded |
| 8028 | OWNER interpretation `[a = A]`, label set | discussion-only | core/operators/precedence (row 8, manager's syntax reading), core/spellings/placeholders | marked as the manager's syntax reading: held |
| 8055 | OWNER statements on arrays, `A[]`, comma | discussion-only (statements) | core/operators/precedence (`,` loosest, `[a,b,c]` = `a|b|c`, "a reading") | his "For now" not carried; held |
| 8077 | OWNER thoughts capture-export | discussion-only | not carried | overtaken by 8111 |
| 8111 | RULING capture-export 1 no / 2 yes | stands (part 2's `capture(path)` spelling replaced by 8882) | core/labels/export/capture-export, core/labels/export st.5, lib/structural/capture | RULING-6 (labels-vs-captures, label-only-group not updated; pure-label revision unmarked), RULING-8 (reading (b) unmarked) |
| 8143 | RULING zero-condition-binding | stands (for now) | core/holes/bare-condition/zero-binding, bound-condition, bare-condition, nested-scope, diagnostics/errors | RULING-9(ii) readings in statement |
| 8165 | OWNER exercise request | discussion-only | not carried | |
| 8174 | MANAGER JSONL exercise | discussion-only | not carried (its findings 1-8 not filed) | finding 3 later withdrawn by 8623 |
| 8240 | OWNER "can't put a hole in predicate" | discussion-only | not carried | candidate (a) of label-name-hole withdrawn; the rx-text half never asked (set aside by 8317) |
| 8260 | OWNER Q "where does row() use the name?" | discussion-only | not carried | |
| 8272 | OWNER request: restrictions on k | discussion-only (manager PROPOSALS) | not carried | k-* proposals overtaken by the label parameter (8317/8350) |
| 8300 | OWNER `_t`, "not textually defined" | discussion-only | not carried | hole-named-label proposal set aside by 8317 |
| 8317 | OWNER two approaches (PROPOSALS) | approach 1 taken up (8350); approach 2 retired (set aside) | core/operators/bindings/label-variables (class PROPOSAL), parked/ideas/label-symbol | RULING-10(i) misquote |
| 8350 | OWNER "lets tentatively work with it" (LEAN) | stands as a direction | core/operators/bindings/label-variables (under-construction) | held |
| 8387 | RULING label-parameter-omitted | stands | core/operators/bindings/label-omitted; parked/ideas/empty-argument (IDEA) | RULING-10(iii) quote reordered; RULING-12 lane reading vs reading (c) |
| 8427 | RULING label-parameter-default | stands (spelling `l = ts:` a lean) | core/operators/bindings/label-default | RULING-11(iii) "rejected by his lean" |
| 8445 | OWNER capture-place lean (a) | retired (replaced by 8882's shape) | lib/structural/capture `rejected:` | his "early capture is no crime" not carried (discussion) |
| 8471 | RULING capture-twice (a) + OBSERVATION two kinds | stands | core/labels/export/caller-ambiguous, lib/structural/capture; observation -> label-kinds | RULING-5 (stale rejected (b)) |
| 8504 | RULING label-kinds | stands | core/operators/bindings/label-kinds, parked/ideas/reference-kind | held |
| 8527 | RULING capture-name (a) | stands in part (last step + rename; `name =` keyword replaced by 8882) | lib/structural/capture | manager's warning proposal not carried (fine: not ruled) |
| 8545 | OWNER PROPOSAL capture-as-pcre | retired (dropped by 8598) | lib/structural/capture `rejected:` | held |
| 8571 | OWNER alternative `capture(@x.year)` | discussion-only -> ruled 8598 | lib/structural/capture/add-on | held |
| 8598 | RULING array-capture; capture-loop-value closed as the label | stands (unbuilt) | lib/structural/capture/add-on, lib/structural/capture | RULING-6 (labels-vs-captures still "not stated"); RULING-9(vi) |
| 8623 | OWNER Q argument-export ("show me why") | discussion-only (manager statement withdrawn) | core/labels/export/arguments (history in reasoning) | held |
| 8657 | OWNER argument-export restated (LEAN) | discussion-only | core/labels/export/arguments | held |
| 8676 | OWNER "this aligns" (AGREEMENT) | argument-export yes as the reading taken (he may object) | core/labels/export/arguments, lib/json/members | RULING-11(ii) no class word in arguments |
| 8707 | RULING label-in-argument (+ second thoughts) | stands | core/operators/bindings/label-in-argument; clarification in argument-default | held; reading (c)'s extension marked "to confirm" |
| 8743 | MANAGER re-examination (proposal) | discussion-only -> ruled 8770 | core/labels/export/arguments (run lines) | held |
| 8770 | RULING argument-label | stands; REVERSES readings (a),(b) of argument-default | core/labels/export/arguments, argument-default, two-sources, call-prefix, lib peek/hits/occurrences/rx.repeat, core/patterns/atomic | RULING-4 (C3 rejected line), RULING-7 (C4) |
| 8795 | OWNER PROPOSAL capture shape on the set side | ruled via 8882 | lib/structural/capture (class PROPOSAL) | held |
| 8820 | OWNER capture-absent (PROPOSAL `?` on request) | retired (overtaken by 8845/8882) | lib/structural/capture history | held |
| 8845 | OWNER capture-optional (LEAN defaults; PROPOSAL `(h?: ..)`) | ruled via 8882 | core/conditions/form/optional-entry history | held |
| 8872 | MANAGER CORRECTION of 8845's plain row | stands (correction) | optional-entry line "The plain entry" (SEARCHED FAILS, FIND-ALL [`3x`@3]) | applied: held |
| 8882 | RULING optional-label + FLAG optional-label-general | stands; spelling moved by 9034's lean; conservative edges part of the ruled statement | core/conditions/form/optional-entry, lib/structural/capture | RULING-2 (edges dropped/reversed), RULING-3 (flag not open) |
| 8912 | MANAGER r84 dispositions | stands (manager's rulings) | A4/C3/C4/C5/D2/A7 into core/lib details histories | A4 closed; C3 RULING-4; C4 RULING-7 |
| 8971 | OWNER optional-label-general (LEAN/QUESTIONS/IDEA) | open (optional-label-general) | value-left reading (d) in core/conditions/form/value-left; parked/ideas/optional-arguments | RULING-3; RULING-11(ii) |
| 9034 | OWNER optional-place "Before the colon" + `?:` PROPOSAL | place: reading taken as ruling (he may object); `?:`: lean | core/conditions/form/optional-entry, core/spellings/placeholders, parked default-set/empty-value/severity-table | RULING-9(iv), RULING-11 |
| 9068 | OWNER string-label (CLARIFICATION) | discussion-only (design intent) | lib/json/members, core/operators/bindings/label-forward | RULING-10(ii) misquote; RULING-11(i) class |
| 9111 | RULING label-forward (+2 questions) | stands; Q1/Q2 answers are readings | core/operators/bindings/label-forward, lib/json/members | held |
| 9156 | RULING capture-negated broadened | stands; group-question part a proposal | core/filters/negation/effects, lib/control/when, diagnostics/errors | RULING-9(iii) |
| 9180 | MANAGER notes (effect-in-guard; array placeholder) | stands as manager's readings | core/filters/negation/effects, lib/control/when, lib/structural/capture/add-on | held (marked) |
| 9196 | OWNER Q two-sources ("isn't the A.h not visible bare?") | second shape closed by the MANAGER on label-reference (he may object) | core/labels/paths/two-sources (ruled), core/labels/flow | RULING-9(v), RULING-11(ii) |
| 9217 | RULING zero-in-loop (b) + POSITION | stands, "held open to argument" | core/conditions/match-so-far/in-loop | RULING-9(i) |
| 9270 | RULING binding-fixed | stands (principle) | core/principles/binding-fixed; nested-scope, match-so-far, in-loop | held |
| 9289 | MANAGER call-forms put again (proposal) | open (call-forms) | not carried (call-forms piece unchanged; his "we currently don't have overloading" not cited there) | discussion-only: held |
| 9315 | OWNER count-prefixed example | discussion-only | not carried | |
| 9348 | OWNER "leading question to using length(0:)" | discussion-only | not carried | its `$0` gap closed by 9402 (core/values/reads) |
| 9370 | OWNER on `0` (OBSERVATION) | discussion-only -> ruled 9402 | quoted in core/conditions/match-so-far base | RULING-1 (no details item) |
| 9402 | RULING zero-open, all four | stands | core/conditions/match-so-far, core/values/reads, lib/counting/some, lib/structural/capture, core/diagnostics/warnings | RULING-1 (no rulings: item anywhere) |

MANAGER readings folded in, attacked: optional-entry (a) joint/value legal — no quoted owner word supports it and the
ruled edge refuses the value case (RULING-2); `?:` closes optional-label-general — his own "how special" says open
(RULING-3); label-omitted "lane's reading" — no owner word, against reading (c) (RULING-12); in-loop per-pass clause —
his "after the fact" picture supports the label spelling as an idiom, not as part of the ruling (RULING-9(i)); effects
definition and depth — his "any effect macro ... under negation" supports a refusal of effects under negation, the
definition and "at any depth" are the manager's (RULING-9(iii)); zero-open (a) "written last" — his "yes all 4" was on
the `&` example only (RULING-9(vi)); argument-export "the reading taken" — his "this aligns with my understanding"
supports it and it is marked (held); label-forward Q1/Q2, JSON sketch — marked readings (held).

## PROBED-AND-HELD

- Every `(record: "...")` citation resolves: lint L4 at the freeze, 979 checks, 0 failed (`pred_doc_lint.py --root
  RD/R/tree`, run from the lens dir).
- Owner quotes checked word for word against the record (each new/changed rulings item and base "His words" of the
  fold): binding-fixed (3), zero-in-loop (2), zero-condition-binding (1), capture-export (1), capture-twice (2),
  capture-name, array-capture (2, one elided with "..." correctly), label-kinds (2), label-default, label-in-argument
  (2 + clarification), label-forward, argument-label (2), capture-negated, optional-label, optional-place, the 8971 lean,
  optional-arguments IDEA, empty-argument IDEA, label-symbol, reference-kind, json-picture, "lets tentatively ...
  label-paramter-twice" (typo kept), "label args are not special ...", zero-open "yes all 4", the 9370 observation,
  "the precedence needs clarifying hence []", "a macro that takes a,b,c and turns it into an array": all exact except
  the four of RULING-10 (31 quotes checked, 4 failed).
- Status words HELD: capture-export ruled 2026-11-22; caller-ambiguous ruled (capture-twice, record: "It answers the
  open caller-ambiguous for requested captures"); in-loop ruled; match-so-far ruled 2026-11-23; zero-binding ruled
  2026-11-22; binding-fixed principle with (class: RULING)/(class: POSITION); label-variables under-construction
  (his "tentatively"); label-omitted/default/kinds/in-argument/forward ruled; lib/structural/capture ruled;
  capture/add-on under-construction (unbuilt); lib/json/members under-construction; precedence reading; parked x4.
- Later same-day entries applied correctly: 8872 CORRECTION (the plain row prints SEARCHED FAILS / FIND-ALL [`3x`@3]);
  capture-as-pcre dropped (8598 over 8545); capture-place lean replaced by 8882; capture-name keyword replaced by 8882;
  reading (f) of 8111 WITHDRAWN by 8471; argument-export statement of 8623 withdrawn (arguments piece follows 8676);
  `l: ts` placeholder withdrawn (8427); 8240 candidate (a) withdrawn (not carried); zero-in-loop "(a)" label for the
  bound-item spelling withdrawn (details reading).
- r84 A4: CLOSED (lib/rx/repeat now legal with its line; the 2026-11-17 "can i name the item" quoted as answered yes;
  repeat-label not asked; RX6 reading consistent again; atomic bullet and line legal). r84 C3: readings (a)/(b) marked
  withdrawn in `readings:`, but NOT closed (RULING-4). r84 C4: closed in closed-argument only (RULING-7).
- No document sentence relies on entries after zero-open (9421 on): grep for `repeat(X, _, 5)`, "play it out",
  "one head per name" in the six files: only the pre-existing call-forms candidate (b) wording (19 Nov) and 9289's
  absent-setting are not carried; held.

CRITIC COMPLETE

