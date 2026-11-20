# CRITIC RULING: r60 preddoc5

## Findings


### RULING-1  CONFIRMED   severity: doc   effort: S
where: core.md [core/modules/positional] (statement + last bullet; diff lines 739-753); record L5487-5511 ("2026-11-19 MANAGER — the withdrawal above is itself CORRECTED ...")
what: the rewritten piece scopes the open question to ONE TUPLE and puts the MAP case outside it ("a positional list against a MAP, which has no order, is not stated"). That is the wording of the WITHDRAWN entry (L5474: "NOT STATED by either entry, and the only part still open: a positional list against a MAP"), not of the correction that replaced it, which says the map case is INSIDE tuple-parts.
evidence: record L5507-5509: "WHAT STANDS NOW: the positional list `(a, b) := X` is OPEN under tuple-parts, for a tuple and for a map alike; statement 7 of import-symbols ("left undefined for now") was nearer the record than its withdrawal". Piece statement: "Is a positional list on the left of a binding, `(a, b) := lo`, a way to take ONE tuple apart, or is a tuple only ever used whole?"; last bullet: "a positional list against a MAP, which has no order, is not stated." Observed: map case = "not stated" (outside the slug); expected: map case = open under tuple-parts.
proposed fix: state the question as the correction does: "Is the positional list `(a, b) := X` defined, for a tuple and for a map alike?", with (A)/(B1) for the tuple and the map case named as part of tuple-parts; drop "is not stated". Optionally add to the details `history:` that statement 7's "left undefined" was the nearer reading (the correction's words).

### RULING-2  CONFIRMED   severity: doc   effort: S
where: core_details.md [core/filters/complement] `rulings:` item 4 (added by the fix lanes, diff line 1299; core_details.md:771); record L1949-1972 (21:49) and L2036-2052 (23:46, same night)
what: the added item cites "Source-row: yes" and states, as the ruling's content, "a row of the source is the whole subject; a searched pattern gives several result rows per subject; the complement is per subject". That wording was SUPERSEDED under two hours later, the same night, by row-is-match, which calls it the manager's framing and replaces it (a row is ONE POTENTIAL MATCH; the subject is the search text, not a row). The prior round's worst-finding shape exactly: a "yes" later corrected, the piece still stating it as ruled.
evidence: record L2015-2027 (23:31, "OWNER REMARKS — what a row is"): "The wording "a row of the source is the whole subject; the complement is per subject" (source-row, 21:49) was the MANAGER's framing of the question ... the manager WITHDRAWS it as the model's statement". L2036-2046 (23:46, "OWNER RULING — row-is-match"): "SUPERSEDES the 21:49 source-row wording ("a row of the source is the whole subject; the complement is per subject"), which was the manager's framing: `t2 & !q` searched on `9:30` HOLDS reporting `9`". The rest of the documents already follow row-is-match (core_details.md:259-274, piece core/model/... with slug row-is-match), so this item contradicts a sibling piece.
proposed fix: drop the item from `rulings:` (or keep the quote with "SUPERSEDED the same night by row-is-match (record: "2026-11-16 OWNER RULING — row-is-match"); its wording was the manager's framing") and move the slug source-row's history to `history:`; add `see:` to the row-is-match piece. Complement's ruled status is unaffected (regex-settles, not-is-complement's first half and complement-place carry it).

### RULING-3  CONFIRMED   severity: doc   effort: S
where: parked_details.md [parked/ideas/known-nothing] and [parked/ideas/warning-rows] `rulings:` (lines 1106, 1122; both new in the diff); record L5048 ("2026-11-19 MANAGER — review r54 of rev 29: dispositions ruled (no owner words)")
what: each item puts the MANAGER's disposition text in `rulings:`, the field whose shape is `<date> "<his words, verbatim>"` (doc_format.md line 89). The items themselves say "(class: MANAGER, no owner words)", and the cited entry's title says "(no owner words)". Nothing the owner said is quoted; the field misattributes by its position (a reader scanning `rulings:` takes it as his words), and the lint passes it because it only checks the title exists.
evidence: quote found WHITESPACE-ONLY in L5048-5086 inside "The predicate manager RULES: every item FIX-NOW as proposed (rev 29.1), the two general forms (one cause-free "known nothing" warning; warnings as rows of form / places / look-alike) PLAN (ideas file)". No owner quote in the entry.
proposed fix: empty `rulings:` on both (parked pieces need none) and put the disposition under `history:` ("2026-11-19, the manager's r54 disposition: PLAN (ideas file)", record title). Consider an L4 check: an item whose cited title contains "no owner words" or begins "<date> MANAGER" fails.
(RULING-2 addendum: the sibling that follows row-is-match is core/model/match, core_details.md:258-274.)

### RULING-4  CONFIRMED (pre-existing, outside the diff; reported because the diff's new core/filters/negation leans on it)   severity: doc   effort: S
where: core_details.md [core/filters/complement] `rejected:` "`!` on a condition — by owner ruling — not-is-complement (a compile error naming the two rewrites)" (core_details.md:709 in BEFORE, unchanged); record L1790-1800 (17:29) and L2053-2066 (23:48 same day)
what: the rejection cites a ruling half of which was REVERSED the same evening. condition-not ruled `!` on a condition LEGAL ("REVERSES the second half of not-is-complement (17:29, "no meaning on a condition")"). Today `!` on a condition is absent from the documents by the new negation piece's spelling READING ("On a condition the record also wrote `!`; the documents write `NOT` there (a reading)"), not by not-is-complement.
evidence: record L2056-2059: "`!` on a condition is LEGAL ... REVERSES the second half of not-is-complement (17:29, "no meaning on a condition"; its first half, `!` on a pattern is a complement, stands)". The complement piece's rulings item 2 ("not-is-complement: yes agree") is fine for the first half; its rejected line states the reversed half as ruled.
proposed fix: rejected line: "`!` on a condition as a compile error — reversed by condition-not (record ...); the spelling on a condition is `NOT` (core/filters/negation, a reading)". Add a note on the not-is-complement rulings item: "its first half; the second half reversed by condition-not".

### RULING-5  CONFIRMED   severity: doc   effort: S
where: parked_details.md [parked/ideas/label-hygiene] `rulings:` item (changed in the diff: class added); record L2785-2794 ("2026-11-17 OWNER RULING — shared-label: keep the compile error") and L2952-2990 (same evening: label-flow proposal, then "OWNER RULING — label-flow (closes the proposal above)")
what: the item's gloss "the error is ruled, the hygiene idea parked" states shared-label's error (one label name on both sides of `&` is refused) as standing. Later the same evening label-flow REVISED it from an error of EXISTENCE to an error of REFERENCE (a name both sides surface is an error only where it is referenced). The record notes that this revision is what eases the very hygiene problem the parked piece is about. The piece's details also quote "One label name on both sides of `&` is refused" (the ideas file's text, history) with no pointer to the revision.
evidence: record L2965-2967 (proposal): "This REVISES the shared-label ruling of the same evening from an error of existence to an error of reference (which also eases the library hygiene problem: a collision nobody references is harmless)"; L2983-2985 (label-flow RULING, (4) STANDING): "across `&`, a name that both sides surface is an AMBIGUOUS REFERENCE and an error where it is referenced (not an error for merely existing: the shared-label ruling so revised)".
proposed fix: gloss: "the error, as revised the same evening by label-flow (an ambiguous REFERENCE across `&`, not mere existence; record "2026-11-17 OWNER RULING — label-flow (closes the proposal above)"), is ruled; the hygiene idea parked". Add a history line that label-flow already removes the unreferenced-collision case (it changes the piece's trigger/problem statement).

### RULING-6  CONFIRMED   severity: doc   effort: S
where: parked_details.md [parked/ideas/string-level-rx] `rulings:` (line 929, new); record L3855-3884 ("2026-11-18 OWNER RULING — match-is-rx ...")
what: the item tags "It's certainly a phase two project." as `(class: RULING)`. doc_format says the class is "the record's word" for the quote. The record does not put that sentence in the RULED list (1)-(4); it quotes it in the IDEA paragraph ("IDEA, his (filed predicates_future.md item 30): string-level manipulation of an rx as GRAPH manipulation ... "certainly a phase two project""). The entry is a ruling, but this sentence is classed IDEA. The second quote ("unbuilt territory ... "under construction" sign") IS ruled (item (4)), but it is also refined that evening by "2026-11-18 OWNER, what "under construction" was about" (L4188): a CLARIFICATION that "under construction" means a compile error when a regex, not a constant or a `$` match, reaches such a function ("left(/\d+/,2) is a compile error when enumerate() != 1"). The item does not point to it.
evidence: record L3874-3877: "IDEA, his (filed `predicates_future.md` item 30): string-level manipulation of an rx as GRAPH manipulation (...); "certainly a phase two project"". L4188-4200 (clarification, his words quoted above).
proposed fix: `(class: IDEA, in a ruling's message)` on the first quote, and keep the second as the ruled part with "(clarified the same evening: record "2026-11-18 OWNER, what "under construction" was about")". Lower-grade instance of the same mislabel: core_details.md [core/principles/regex-default] item `(class: OWNER)` (diff line 862). "OWNER" is the heading's speaker, not a class word; the record's own word in that entry is that access to the hits "STAYS" as a "NOTED EXCEPTION". Suggest `(class: OWNER, a qualification of the DIRECTION)`, or the entry's word.

### RULING-7  SUSPECTED   severity: doc   effort: S
where: core.md [core/modules/export] (reading 2026-11-19); record L5512-5549 (the two 2026-11-19 provided-names entries)
what: after the move, the only call-form name the core still defines is `@export(names)`: "A library file exports with `@export(names)` ...". The 2026-11-19 take he agreed to ("syntax and meaning in the core, every call-form name in the library marked `defined: language` or `defined: native`") leaves no call-form piece in the core. There is no lib/ piece for `export` (no `[lib/.../export]` heading in library.md), while its siblings `import` and `assert.*` were moved or created in lib/. Whether an `@`-effect call counts as "a macro x()" is not stated in the record. That is why this is SUSPECTED, not CONFIRMED.
evidence: `grep -n '^### ' core.md` together with the statements that name `x(`: only core/modules/export (core.md:1131-1132) defines one; core/modules/call-shorthand and core/operators/bindings name `f(...)`/`m(...)` as syntax, which is correct. Record L5541-5545: "every call-form name in the library marked `defined: language` or `defined: native` ...; `import` as a call goes to the library while the binding list stays in the core".
proposed fix: move `@export(names)` to a library piece (`lib/builtin/export`, `defined: native (a compile-time effect on the file's public names)`), keeping in core/modules/export only the meaning (what is public, the `_` rule, "a file that exports nothing is a compile error" if that is syntax-level). Or have the manager rule that `@` effects are syntax, and record that ruling.

### RULING-8  CONFIRMED   severity: doc   effort: S
where: core.md [core/modules/all-symbols] last bullet; core_details.md [core/modules/binding-list] `readings:`; record L5355-5386, L5474-5511
what: two places in the module pieces do not carry the record's readings, and the corrections to them, as readings.
(a) all-symbols (ruled) states "With `(=)` a reader cannot tell from the file alone whether a bare name is a label or an imported name." as a plain bullet. In the record it is one of "The manager's readings of the addition, FOR A LANE TO CHECK", "Told to him as the cost of the form, not an objection". Each of the bullet's three siblings is marked "(a reading)"; this one is not.
(b) binding-list's reading "the eight statements he agreed to are the manager's list, "no wider" — SUPPORTED by the record entry" still presents all eight as agreed and standing. Statement 7 ("A bare positional `(a, b) := X` is left undefined for now") was WITHDRAWN (L5474) and that withdrawal CORRECTED (L5487: the positional list is "OPEN under tuple-parts, for a tuple and for a map alike"). The piece names neither entry.
evidence: record L5378-5383 ("The manager's readings of the addition, FOR A LANE TO CHECK ... - With `(=)` a reader can no longer tell from the file alone whether a bare name is a label or an import ... Told to him as the cost of the form, not an objection."); L5487-5509 as quoted in RULING-1.
proposed fix: (a) end the bullet with "(a reading: the cost told to him, not an objection)". (b) add to the reading: "statement 7 is superseded: withdrawn (record "...WITHDRAWN (the positional binding list)") and that withdrawal corrected to OPEN under tuple-parts (core/modules/positional)". Minor in the same piece: its `rejected:` line cites "it has implications for the rest of the language" "by owner ruling". That sentence is a CAUTION in a DISCUSSION entry (L5311-5332, "Class: DISCUSSION, not a ruling"). The rejection is carried by the later ruling, which adopted the `=`-marked form, so cite that ruling and keep the quote as the reason.

### RULING-9  SUSPECTED   severity: maintenance   effort: S
where: library_details.md `was:` move lines for lib/control/peek, lib/control/when, lib/control/when-test (lines 209, 228, 257: "the owner: core document macros are defined in the library unless primitive") and lib/rx/repeat (line 705: "a library definition over count holes: the core holds primitives only"); unchanged context in the diff (2683, 2691, 2917)
what: the moves stand under the new rule, but their stated reasons quote a designation the owner withdrew on 2026-11-19 ("my 'primitive' designation doesn't work"). The repeat line goes further and states a rule ("the core holds primitives only") that doc_format.md has dropped (diff lines 3487 and 3523 remove "primitives only"). A reader resolving a previous tag sees the withdrawn rule given as the reason.
evidence: record L5520-5524 (his words, as quoted in the entry); `grep -n 'unless primitive\|primitives only' library_details.md`.
proposed fix: append the current reason to each line, e.g. "(... unless primitive; since refined: every call-form name is a library piece, record "2026-11-19 OWNER, refining where provided names live ...")". Lines 209/228/257 are accurate history as dated, so this is optional for them; line 705 is a rule statement and should change.

## Appendix A: quote-containment census (sub-part (a))

METHOD (re-runnable, read-only, my scratch dir):
`timeout 60 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc5/ruling/items.py > .../ruling/items.txt`. It parses the `rulings:` field of the three
details files in R/before and R/tree, keyed by piece tag. An item counts as NEW OR CHANGED if its whitespace-normalised text is not
under the same tag in BEFORE. The script resolves `(record: "...")` by EXACT title match, following L4's title rule: `##`/`###`
headings plus bold `**YYYY-...**` openers after a blank line or heading, matching the whole title or the part before the first ` (`.
Each "..." segment before the citation is then checked against the resolved entry's text (from its line to the next title).
Context dump for the his-words-or-manager's check: `.../ruling/ctx.py` (110 characters before every match), read by hand.

| population | count |
|---|---|
| `rulings:` items new/changed under a tag (incl. 18 carried unchanged to a NEW tag by a move) | 120 (102 text-new/changed + 18 moved) |
| cited titles resolved to exactly ONE record entry | 120 / 120 (0 ambiguous, 0 absent) |
| quoted segments checked (an item's quote splits at inner `"`) | 129 |
| EXACT substring of the cited entry | 53 |
| WHITESPACE-ONLY difference (line wraps) | 76 |
| NOT FOUND in the cited entry | 0 |
| quoted segments that are NOT the owner's words | 2 items (known-nothing, warning-rows: the manager's r54 disposition; RULING-3). The "Inserting through a hole." segment on core/holes/labels is the manager's heading, honestly labelled "under the manager's heading" (held) |
| secondary quotes in item glosses, checked by hand | 5: "I'd like to consider that unbuilt territory ..." (string-level-rx, WS, found), "(5) last-pass-default (14:30) STANDS" (L2467, found), "His second sentence is a REMARK, not a directive" (found, labelled the entry's words), "Then there is a = some(between" (found), "Even /x?/ is a loop from 0 to 1" (found) |
| longest quoted segment checked | 318 characters (max over items.json) |
| `(class: ...)` tags checked against the record's word | 51 tagged items; 2 mislabels (RULING-6: string-level-rx RULING for an IDEA sentence; regex-default "OWNER" no class word) |

Status lines (base files, BEFORE vs TREE; `.../ruling/status.py`): 212 pieces after, 190 before; 33 NEW, 3 CHANGED
(core/modules/positional ruled->open tuple-parts; core/principles/stated-behaviour ruled->reading;
core/modules/default-set/members open default-set->open default-imports), 8 GONE (moved, `was:` lines). Every NEW/CHANGED
status was checked against its rulings items and record. Findings: RULING-1 (positional's scope), RULING-7 (export's placement).
The rest held (PROBED-AND-HELD).

## Appendix B: following entries per cited entry (sub-part (a), reopen/correct/narrow/withdraw check)

METHOD: `timeout 60 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc5/ruling/follow.py`. For each record entry cited by a NEW/CHANGED
item, it lists every later entry dated the SAME DAY or the NEXT DAY whose title or `tags:` line (marked TITLE/TAG), or whose body
(marked BODY), names one of the cited entry's SUBJECT keys. The keys are the kebab slugs in its title plus the tags on its `tags:` line.
Entries with no slug in the title ("subject: (none)") were covered by a supplementary keyword pass
(`.../ruling/kw.py START 'regex'`), shown after the table. Every listed follower was then read by hand. The followers that change a
cited ruling: L1411 (positional, handled in the piece), L2036 row-is-match (RULING-2), L2053 condition-not (RULING-4),
L2952/L2971 label-flow (RULING-5), L4188 (RULING-6), L5474/L5487 (RULING-1, RULING-8). All others were read and found consistent
(PROBED-AND-HELD). Entries inside the L732-1025 block (the bold sub-entries 761-1001, not L4 titles) were read IN FULL by hand, because the
script treats the block as one entry. The count items' lean -> budget -> later-optimisation sequence is carried correctly.
```

CITED L573 2026-11-14 RULINGS on predicates_draft.md §13 (Frank)
  by: core/values/comparisons
  subject: (none)

CITED L583 2026-11-14 RULINGS on docs/dev/lanes/predx_report.md §11 (Frank: "I agree with your leans excepting explain 6,
  by: core/values/computed-labels core/values/metadata lib/assert/assert
  subject: (none)

CITED L644 2026-11-14 RULINGS on the predx gaps (Frank)
  by: lib/builtin/enumerate
  subject: (none)

CITED L713 2026-11-14 RULING — Q1 foundation (Frank: "1. agree", on review 2026-11-14-r1-predspec's proposed answer)
  by: core/filters/operand-context
  subject: r1-predspec

CITED L722 2026-11-14 RULING — OWN-1, transforms are FILTER MODIFIERS (Frank: "The problem is the name. Trim or unpad imp
  by: core/modules/naming
  subject: (none)

CITED L732 2026-11-14 RULINGS on rev 3's contradictions (Frank: "agree all four")
  by: core/modules/naming core/values/comparisons lib/assert/assert lib/counting/count lib/counting/some
  subject: (none)

CITED L1026 2026-11-15 RULING — the provided transform `search` is renamed `occurrences` (Frank, to session 133, ~20:40)
  by: core/modules/naming
  subject: (none)

CITED L1033 2026-11-15 RULINGS — `anchored` has exact ends; which `&` is the operator in rx text (Frank, to session 133, ~
  by: lib/search/anchored
  subject: (none)

CITED L1048 2026-11-15 CORRECTION and RULING (Frank, to session 133, ~21:20)
  by: core/diagnostics/warnings core/filters/and lib/search/anchored
  subject: (none)

CITED L1068 2026-11-15 RULINGS — a per-call hit name; no count warning; the hole is the scope an `&` in it anchors to (Fra
  by: lib/search/occurrences
  subject: per-call

CITED L1083 2026-11-15 RULING — the sides of `&` "match the same stretch whole"; the word "anchored" is kept for the macro
  by: core/holes/and-in-hole
  subject: (none)

CITED L1093 2026-11-15 RULINGS — no anchored-specific error in a hole; the anchor warning covers every whole-match place (
  by: core/diagnostics/warnings
  subject: anchored-specific whole-match
  -> L1103 [ BODY:whole-match] 2026-11-15 RULING — the anchor warning keys off the ROLE, never a transform's name (Frank, to session 133, box clock 20:
  -> L1150 [ BODY:whole-match] 2026-11-15 RULING — the anchor warning has no exemption for macro-body text (Frank, to session 133, box clock 21:21)

CITED L1103 2026-11-15 RULING — the anchor warning keys off the ROLE, never a transform's name (Frank, to session 133, box
  by: core/diagnostics/warnings
  subject: (none)

CITED L1126 2026-11-15 RULING — `unpadded` is cut from the first spec (Frank, to session 133, box clock 20:57)
  by: lib/modifiers/padded
  subject: (none)

CITED L1150 2026-11-15 RULING — the anchor warning has no exemption for macro-body text (Frank, to session 133, box clock 
  by: core/diagnostics/warnings
  subject: macro-body

CITED L1178 2026-11-15 RULING — `json.quoted` is cut from the first spec (Frank, to session 133, box clock 21:54)
  by: lib/modifiers/quoted
  subject: (none)

CITED L1268 2026-11-15 RULING + OWNER IDEA — no bare field reference; a mark for the other side of the intersection (Frank
  by: parked/ideas/other-side-sigil
  subject: (none)

CITED L1304 2026-11-16 RULING — a compare names its fields with the other-side sigil (Frank, to session 134, box clock 00:
  by: parked/ideas/other-side-sigil
  subject: other-side
  -> L1336 [ BODY:other-side] 2026-11-16 OWNER DIRECTION — PAUSE the field-reference direction; consider a condition over several labels at once (Fran
  -> L1573 [ BODY:other-side] 2026-11-16 OWNER RULING — retire-paused: split; the sigil's pause is indefinite (Frank, to session 135, box clock 12:51)

CITED L1318 2026-11-16 OWNER DIRECTION — arrays of macros: the general path, no special mechanism (Frank, to session 134, 
  by: core/arrays/lift
  subject: (none)

CITED L1336 2026-11-16 OWNER DIRECTION — PAUSE the field-reference direction; consider a condition over several labels at 
  by: parked/ideas/other-side-sigil
  subject: field-reference

CITED L1362 2026-11-16 OWNER RULING + REQUEST — the tuple as a value: OK, to be fleshed out (Frank, to session 134, box cl
  by: core/values/tuples
  subject: (none)

CITED L1384 2026-11-16 OWNER CLARIFICATION + ANSWER — "left/right" was about the binding sign; tuple-anywhere: yes (Frank,
  by: core/values/tuples
  subject: tuple-anywhere

CITED L1394 2026-11-16 OWNER CONFIRMATION — a tuple on the left of a binding takes it apart (Frank, to session 134, box cl
  by: core/modules/positional
  subject: (none)

CITED L1402 2026-11-16 OWNER IDEA (offered, not a ruling) — first/rest binding with recursion (Frank, to session 134, box 
  by: parked/ideas/first-rest
  subject: (none)

CITED L1411 2026-11-16 OWNER — reaching a tuple's parts is REOPENED; he wants the "use it whole" case heard (Frank, to ses
  by: core/modules/positional parked/ideas/tuple-apart
  subject: (none)

CITED L1420 2026-11-16 OWNER — on first-rest: the built-in tuple mechanism is simpler, "which I like"; and a question (Fra
  by: core/values/tuples
  subject: first-rest
  -> L1433 [TITLE/TAG:first-rest] 2026-11-16 OWNER RULING — first-rest: PARKED, kept in the wings (Frank, to session 134, box clock 10:22)

CITED L1433 2026-11-16 OWNER RULING — first-rest: PARKED, kept in the wings (Frank, to session 134, box clock 10:22)
  by: parked/ideas/first-rest
  subject: first-rest

CITED L1441 2026-11-16 OWNER RULING — set-arity: a set carries an arity (Frank, to session 134, box clock 10:26)
  by: core/values/tuples
  subject: set-arity

CITED L1474 2026-11-16 OWNER RULING — default-set: a default of several strings is an error, for now; idea: `some(...)` (F
  by: core/conditions/defaults parked/ideas/default-set
  subject: default-set

CITED L1483 2026-11-16 OWNER RULINGS — unset-component: yes; default-unused: agree (Frank, to session 134, box clock 11:05
  by: core/conditions/defaults core/diagnostics/warnings
  subject: default-unused unset-component

CITED L1503 2026-11-16 OWNER RULING — two-orders: keep both (Frank, to session 134, box clock 11:20)
  by: core/values/tuples
  subject: two-orders

CITED L1514 2026-11-16 OWNER RULING — modifier-lift: yes; a "future consideration" document (Frank, to session 134, box cl
  by: core/values/tuples parked/ideas/partial-transforms
  subject: modifier-lift

CITED L1535 2026-11-16 OWNER RULING — record-is-product: yes (Frank, to session 134, box clock 11:35)
  by: core/values/tuples
  subject: record-is-product
  -> L2087 [ BODY:record-is-product] 2026-11-17 RECORD after review r34 (round predspec231 on rev 23.1; session 137, box clock 03:47; the manager's entries, 

CITED L1544 2026-11-16 OWNER RULING — zero-pass-record: the outside label is tested (Frank, to session 135, box clock 12:4
  by: core/conditions/two-valued parked/ideas/empty-value parked/ideas/field-count parked/ideas/unset-member parked/ideas/zero-loop-default
  subject: zero-pass-record

CITED L1560 2026-11-16 OWNER RULING — library-not-syntax: the 11-14 ruling is withdrawn (Frank, to session 135, box clock 
  by: core/values/tuples
  subject: library-not-syntax

CITED L1573 2026-11-16 OWNER RULING — retire-paused: split; the sigil's pause is indefinite (Frank, to session 135, box cl
  by: core/values/tuples parked/ideas/field-count parked/ideas/other-side-sigil
  subject: retire-paused

CITED L1585 2026-11-16 OWNER RULING — label-twice: an error (Frank, to session 135, box clock 13:16)
  by: parked/ideas/label-twice
  subject: label-twice
  -> L2850 [ BODY:label-twice] 2026-11-17 OWNER RULING — the three remaining error-or-warning candidates (Frank, to session 138, evening)
  -> L2885 [ BODY:label-twice] 2026-11-17 OWNER — label numbers: try them (Frank, to session 138, evening)

CITED L1594 2026-11-16 OWNER RULING — pairing-loop, part 1: the wording confirmed; his remark on optionals (Frank, to sess
  by: parked/ideas/unset-member
  subject: pairing-loop
  -> L1607 [ BODY:pairing-loop] 2026-11-16 OWNER DIRECTION — absent-holds: work out the options (Frank, to session 135, box clock 13:38)
  -> L1655 [ BODY:pairing-loop] 2026-11-16 OWNER RULING — absent-rule: LOCKED (Frank, to session 135, box clock 14:31)

CITED L1655 2026-11-16 OWNER RULING — absent-rule: LOCKED (Frank, to session 135, box clock 14:31)
  by: core/principles/no-absence
  subject: absent-rule
  -> L1682 [TITLE/TAG:absent-rule] 2026-11-16 MANAGER'S READINGS after the fold of absent-rule (session 135, box clock 14:50; NOT the owner's words; told t
  -> L1832 [ BODY:absent-rule] 2026-11-16 OWNER DIRECTION — conditions are their own kind (Frank, to session 136, box clock 19:31)
  -> L1856 [ BODY:absent-rule] 2026-11-16 OWNER REMARK — the SQL NULL parallel (Frank, to session 136, box clock 19:44; a remark, an INPUT to the condi
  -> L1932 [ BODY:absent-rule] 2026-11-16 OWNER REMARK — drop the optional mark? (Frank, to session 137, box clock 21:16; a question to the manager aft
  -> L1949 [ BODY:absent-rule] 2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane (Frank, to session 137, box clo
  -> L1989 [ BODY:absent-rule] 2026-11-16 RECORD after review r31 (round condkind on docs/design/condition_kind.md; session 137, box clock 22:58; the m
  -> L2423 [ BODY:absent-rule] 2026-11-17 OWNER RULING — labels match every pass, captures match the last (Frank, to session 138, evening)

CITED L1696 2026-11-16 OWNER RULING — optional-as-loop (Frank, to session 136, box clock 15:23)
  by: core/labels/one-rule
  subject: optional-as-loop
  -> L1832 [ BODY:optional-as-loop] 2026-11-16 OWNER DIRECTION — conditions are their own kind (Frank, to session 136, box clock 19:31)

CITED L1727 2026-11-16 OWNER RULING — match-context (Frank, to session 136, box clock 16:13)
  by: parked/ideas/explainer
  subject: match-context
  -> L1759 [ BODY:match-context] 2026-11-16 OWNER RULING — domain-scope (Frank, to session 136, box clock 16:31)
  -> L1832 [ BODY:match-context] 2026-11-16 OWNER DIRECTION — conditions are their own kind (Frank, to session 136, box clock 19:31)
  -> L1949 [ BODY:match-context] 2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane (Frank, to session 137, box clo

CITED L1790 2026-11-16 OWNER RULINGS — not-is-complement and mark-in-none (Frank, to session 136, box clock 17:29)
  by: core/filters/negation
  subject: mark-in-none not-is-complement
  -> L1812 [TITLE/TAG:mark-in-none BODY:not-is-complement] 2026-11-16 CORRECTION — mark-in-none is NOT ruled (session 136, box clock 17:29)
  -> L1817 [TITLE/TAG:mark-in-none] 2026-11-16 OWNER RULING — mark-in-none: LEFT AS IS (Frank, to session 136, box clock 17:42)
  -> L1832 [ BODY:mark-in-none,not-is-complement] 2026-11-16 OWNER DIRECTION — conditions are their own kind (Frank, to session 136, box clock 19:31)
  -> L1856 [ BODY:not-is-complement] 2026-11-16 OWNER REMARK — the SQL NULL parallel (Frank, to session 136, box clock 19:44; a remark, an INPUT to the condi
  -> L1868 [ BODY:not-is-complement] 2026-11-16 OWNER REMARK, continued — the condition as a WHERE clause (Frank, box clock 19:49; an INPUT to the condition-
  -> L1888 [ BODY:mark-in-none] 2026-11-16 OWNER REMARK — a macro raising its own warning (Frank, to session 136, box clock 17:46; filed late by lane fi
  -> L1932 [ BODY:mark-in-none] 2026-11-16 OWNER REMARK — drop the optional mark? (Frank, to session 137, box clock 21:16; a question to the manager aft
  -> L1949 [ BODY:mark-in-none] 2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane (Frank, to session 137, box clo
  -> L1989 [ BODY:not-is-complement] 2026-11-16 RECORD after review r31 (round condkind on docs/design/condition_kind.md; session 137, box clock 22:58; the m
  -> L2053 [ BODY:not-is-complement] 2026-11-16 OWNER RULING — condition-not: allowed (Frank, to session 137, box clock 23:48)

CITED L1832 2026-11-16 OWNER DIRECTION — conditions are their own kind (Frank, to session 136, box clock 19:31)
  by: core/conditions/form
  subject: (none)

CITED L1878 2026-11-16 OWNER REMARK — a default restricted to the values the label could hold (Frank, to session 136, box 
  by: parked/ideas/default-range
  subject: append-only
  -> L1888 [TITLE/TAG:append-only] 2026-11-16 OWNER REMARK — a macro raising its own warning (Frank, to session 136, box clock 17:46; filed late by lane fi

CITED L1888 2026-11-16 OWNER REMARK — a macro raising its own warning (Frank, to session 136, box clock 17:46; filed late 
  by: parked/ideas/macro-warning
  subject: append-only

CITED L1912 2026-11-16 OWNER ANSWER, CORRECTED BY HIM — condition-kind (Frank, to session 137, box clock 20:41; he interru
  by: core/model/match
  subject: condition-kind

CITED L1949 2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane (Frank, to session 13
  by: core/conditions/defaults core/filters/complement
  subject: default-scope default-value drop-mark source-row
  -> L1973 [TITLE/TAG:default-scope] 2026-11-16 OWNER RULING — default-scope: per test (Frank, to session 137, box clock 22:30; after docs/design/condition_k
  -> L1989 [ BODY:source-row] 2026-11-16 RECORD after review r31 (round condkind on docs/design/condition_kind.md; session 137, box clock 22:58; the m
  -> L2015 [ BODY:source-row] 2026-11-16 OWNER REMARKS — what a row is; negating a condition; the value of a complemented pattern (Frank, to session 1
  -> L2036 [ BODY:source-row] 2026-11-16 OWNER RULING — row-is-match (Frank, to session 137, box clock 23:46)

CITED L2004 2026-11-16 OWNER RULING — all-question: retire (Frank, to session 137, box clock 23:18; after review r31 findi
  by: lib/counting/some
  subject: all-question

CITED L2053 2026-11-16 OWNER RULING — condition-not: allowed (Frank, to session 137, box clock 23:48)
  by: core/filters/negation
  subject: condition-not
  -> L2233 [ BODY:condition-not] 2026-11-17 OWNER RULINGS — regex-settles; absent-under-not (Frank, to session 138, box clock about 13:25)

CITED L2067 2026-11-17 RECORD (session 137, box clock 03:01; filed late after review r33 F14; the first two items are the 
  by: parked/ideas/match-then-judge
  subject: (none)

CITED L2118 2026-11-17 OWNER RULING — branch-scope: reading (ii); atomic wanted, its spelling OPEN (Frank, to session 138,
  by: parked/ideas/atomic
  subject: branch-scope
  -> L2140 [TITLE/TAG:branch-scope] 2026-11-17 OWNER, on the model after branch-scope (Frank, to session 138, box clock about 11:50)
  -> L2188 [ BODY:branch-scope] 2026-11-17 OWNER DIRECTION — decide the open choices by a REGEX MODEL where one exists (Frank, to session 138, box clock
  -> L2197 [ BODY:branch-scope] 2026-11-17 OWNER — a regex model for occurrences (Frank, to session 138, box clock about 13:10; a model offered with "Co
  -> L2474 [ BODY:branch-scope] 2026-11-17 OWNER RULING — nested-pass: the outermost view (Frank, to session 138, evening)

CITED L2151 2026-11-17 OWNER IDEA — options written in the language (Frank, to session 138, box clock about 12:05; an idea
  by: parked/ideas/capability-optins
  subject: (none)

CITED L2160 2026-11-17 OWNER — a library element beyond the user's level is an ERROR (Frank, to session 138, box clock abo
  by: lib/builtin/import parked/ideas/capability-optins
  subject: (none)

CITED L2188 2026-11-17 OWNER DIRECTION — decide the open choices by a REGEX MODEL where one exists (Frank, to session 138,
  by: core/principles/regex-default
  subject: (none)

CITED L2210 2026-11-17 OWNER — the regex model explains; it does not exclude useful features (Frank, to session 138, box c
  by: core/principles/regex-default
  subject: (none)

CITED L2233 2026-11-17 OWNER RULINGS — regex-settles; absent-under-not (Frank, to session 138, box clock about 13:25)
  by: core/filters/negation
  subject: absent-under-not regex-settles
  -> L2296 [ BODY:absent-under-not] 2026-11-17 OWNER QUESTIONS on when-meaning (Frank, to session 138, box clock about 14:25; questions, no ruling)
  -> L2510 [ BODY:regex-settles] 2026-11-17 OWNER on atomic-search (Frank, to session 138, evening)

CITED L2310 2026-11-17 OWNER RULING — when-meaning (Frank, to session 138, box clock about 13:55)
  by: core/filters/negation
  subject: when-meaning
  -> L2341 [ BODY:when-meaning] 2026-11-17 OWNER PROPOSAL — building patterns without rx literals: an "rx" module and a concatenation operator (Frank, t

CITED L2323 2026-11-17 OWNER RULING — last-pass-default: regex (Frank, to session 138, box clock about 14:30)
  by: core/labels/labels-vs-captures lib/counting/every-pass
  subject: last-pass-default
  -> L2385 [ BODY:last-pass-default] 2026-11-17 OWNER LEAN — a loop pass has its own labels (Frank, to session 138, evening; a lean with a request, NOT yet a
  -> L2408 [ BODY:last-pass-default] 2026-11-17 OWNER on pass-own-labels after the ramifications (Frank, to session 138, evening; leans and a remark, not yet
  -> L2423 [ BODY:last-pass-default] 2026-11-17 OWNER RULING — labels match every pass, captures match the last (Frank, to session 138, evening)
  -> L2454 [ BODY:last-pass-default] 2026-11-17 OWNER RULING — after-loop-read: the last pass's own label (Frank, to session 138, evening)

CITED L2341 2026-11-17 OWNER PROPOSAL — building patterns without rx literals: an "rx" module and a concatenation operator
  by: parked/ideas/rx-module
  subject: (none)

CITED L2454 2026-11-17 OWNER RULING — after-loop-read: the last pass's own label (Frank, to session 138, evening)
  by: lib/counting/some
  subject: after-loop-read
  -> L2529 [ BODY:after-loop-read] 2026-11-17 OWNER RULING — polarity-rule (Frank, to session 138, evening)
  -> L2661 [ BODY:after-loop-read] 2026-11-17 OWNER RULING — pass-list-read (Frank, to session 138, evening)

CITED L2493 2026-11-17 OWNER, on what kind of language this is (Frank, to session 138, evening; reflections, recorded as p
  by: parked/ideas/user-doc-traps
  subject: (none)

CITED L2510 2026-11-17 OWNER on atomic-search (Frank, to session 138, evening)
  by: lib/control/atomic parked/ideas/atomic parked/ideas/match-then-judge
  subject: atomic-search
  -> L2529 [ BODY:atomic-search] 2026-11-17 OWNER RULING — polarity-rule (Frank, to session 138, evening)

CITED L2529 2026-11-17 OWNER RULING — polarity-rule (Frank, to session 138, evening)
  by: parked/ideas/capability-optins
  subject: polarity-rule

CITED L2661 2026-11-17 OWNER RULING — pass-list-read (Frank, to session 138, evening)
  by: core/values/reads
  subject: pass-list-read
  -> L2684 [ BODY:pass-list-read] 2026-11-17 OWNER RULING — what an unqualified `$x` reads (closes the discussion reopened above) (Frank, to session 138, 
  -> L4354 [ BODY:pass-list-read] 2026-11-18 OWNER RULING — `${@y}` is a future direction: not built, not defined now (Frank, to the predicate manager, ev

CITED L2785 2026-11-17 OWNER RULING — shared-label: keep the compile error (Frank, to session 138, evening)
  by: parked/ideas/label-hygiene
  subject: shared-label
  -> L2868 [ BODY:shared-label] 2026-11-17 OWNER, three points on labels (Frank, to session 138, evening)
  -> L2952 [ BODY:shared-label] 2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error (Frank, to session 138, evening; he writes "
  -> L2971 [ BODY:shared-label] 2026-11-17 OWNER RULING — label-flow (closes the proposal above) (Frank, to session 138, evening)

CITED L2814 2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path (Frank, 
  by: parked/ideas/user-doc-traps
  subject: (none)

CITED L3062 2026-11-17 OWNER RULING — quantifier operators (the rx module's last question) (Frank, to session 138, evening
  by: lib/rx/repeat
  subject: (none)

CITED L3161 2026-11-18 OWNER RULING — product-order: first slowest; and a correction of the product's scope (Frank, to ses
  by: parked/ideas/cartesian
  subject: product-order
  -> L4391 [ BODY:product-order] 2026-11-18 MANAGER — review r52 of rev 28: readings withdrawn or corrected, and calls made (the predicate manager, night
  -> L4834 [ BODY:product-order] 2026-11-19 OWNER RULING — other-holes

CITED L3238 2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea (Frank, to session 139, morning)
  by: core/principles/conservative-first parked/ideas/count-filter
  subject: value-is-pattern

CITED L3438 2026-11-18 OWNER, continuing the export-scope discussion (Frank, to session 139, morning; DISCUSSION, nothing 
  by: core/holes/labels
  subject: export-scope
  -> L3458 [TITLE/TAG:export-scope] 2026-11-18 OWNER, export-scope discussion, third exchange (Frank, to session 139, morning; DISCUSSION; the manager then 
  -> L3473 [TITLE/TAG:export-scope] 2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labe

CITED L3458 2026-11-18 OWNER, export-scope discussion, third exchange (Frank, to session 139, morning; DISCUSSION; the man
  by: core/labels/export/caller-ambiguous
  subject: export-rule export-scope
  -> L3473 [TITLE/TAG:export-scope,export-rule] 2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labe
  -> L3501 [TITLE/TAG:export-rule] 2026-11-18 OWNER, clarifying export-rule's sixth statement, and adding a form: `[_ = A]` closes all exports (Frank, to s
  -> L3554 [ BODY:export-rule] 2026-11-18 OWNER RULING — lookahead-labels: visible, as in PCRE (Frank, to session 139, morning)
  -> L4674 [ BODY:export-rule] 2026-11-19 OWNER, on exported and private labels (after same-name-count)
  -> L4693 [ BODY:export-rule] 2026-11-19 OWNER, on building rx from many bindings: use the label rules as defined, watch for a problem

CITED L3473 2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public
  by: core/labels/export/caller-ambiguous
  subject: export-rule export-scope path-and-ambiguity
  -> L3501 [TITLE/TAG:export-rule] 2026-11-18 OWNER, clarifying export-rule's sixth statement, and adding a form: `[_ = A]` closes all exports (Frank, to s
  -> L3554 [ BODY:export-rule] 2026-11-18 OWNER RULING — lookahead-labels: visible, as in PCRE (Frank, to session 139, morning)
  -> L4674 [ BODY:export-rule] 2026-11-19 OWNER, on exported and private labels (after same-name-count)
  -> L4693 [ BODY:export-rule] 2026-11-19 OWNER, on building rx from many bindings: use the label rules as defined, watch for a problem

CITED L3513 2026-11-18 OWNER confirms the reading of `[_ = A]` (Frank, to session 139, morning)
  by: core/labels/export
  subject: (none)

CITED L3762 2026-11-18 OWNER RULING — a `when` with a single argument is an error (Frank, to session 139, afternoon)
  by: parked/ideas/assert
  subject: (none)

CITED L3782 2026-11-18 OWNER RULING — `then` is required; NOT gives the else-only behaviour (Frank, to session 139, aftern
  by: core/filters/negation
  subject: else-only

CITED L3855 2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match" (Frank, to session 140,
  by: parked/ideas/string-level-rx
  subject: match-is-rx
  -> L4188 [TITLE/TAG:match-is-rx] 2026-11-18 OWNER, what "under construction" was about (Frank, to the predicate manager, evening; a CLARIFICATION of his 
  -> L4243 [ BODY:match-is-rx] 2026-11-18 OWNER RULING — construction-line: enumerate (Frank, to the predicate manager, evening)
  -> L4280 [ BODY:match-is-rx] 2026-11-18 MANAGER'S CALL — dollar-warning: the warning stays (the predicate manager, evening; no owner words; an answer
  -> L4287 [ BODY:match-is-rx] 2026-11-18 OWNER, a question on the `$x & <5` warning (Frank, to the predicate manager, evening; a QUESTION, written und
  -> L4611 [ BODY:match-is-rx] 2026-11-19 OWNER RULING — dollar-diagnostic (the form gets a warning)

CITED L3935 2026-11-18 OWNER, a RECOLLECTION in the hole-reads-capture discussion: the label-only group (Frank, to the pre
  by: parked/ideas/label-only-group
  subject: hole-reads-capture label-only
  -> L3959 [TITLE/TAG:label-only BODY:hole-reads-capture] 2026-11-18 OWNER, correcting his spelling of the label-only group (Frank, to the predicate manager, evening; a CORRECTIO
  -> L3966 [TITLE/TAG:hole-reads-capture BODY:label-only] 2026-11-18 OWNER RULING — hole-reads-capture: the label; and a way to get the PCRE capture value (Frank, to the predicat
  -> L4364 [ BODY:hole-reads-capture] 2026-11-18 MANAGER CORRECTION — readings of this evening NOT supported by the runs of lane predspec28 (the predicate man

CITED L3959 2026-11-18 OWNER, correcting his spelling of the label-only group (Frank, to the predicate manager, evening; a
  by: parked/ideas/label-only-group
  subject: label-only
  -> L3966 [ BODY:label-only] 2026-11-18 OWNER RULING — hole-reads-capture: the label; and a way to get the PCRE capture value (Frank, to the predicat

CITED L4019 2026-11-18 OWNER RULING — number-domain: canonical (Frank, to the predicate manager, evening)
  by: core/values/comparisons
  subject: number-domain
  -> L4068 [ BODY:number-domain] 2026-11-18 OWNER, a third way to bound a minimum-width `padded` (Frank, to the predicate manager, evening; an OBSERVATIO
  -> L4188 [ BODY:number-domain] 2026-11-18 OWNER, what "under construction" was about (Frank, to the predicate manager, evening; a CLARIFICATION of his 
  -> L4364 [ BODY:number-domain] 2026-11-18 MANAGER CORRECTION — readings of this evening NOT supported by the runs of lane predspec28 (the predicate man
  -> L4391 [ BODY:number-domain] 2026-11-18 MANAGER — review r52 of rev 28: readings withdrawn or corrected, and calls made (the predicate manager, night
  -> L4710 [ BODY:number-domain] 2026-11-19 OWNER, asked plus-operands: a parameter restriction written `m(g & /\d+/)`, and the same for arithmetic
  -> L4771 [ BODY:number-domain] 2026-11-19 OWNER, discussing the base idea: numbers are strings over an ordered set of symbols

CITED L4167 2026-11-18 OWNER RULING — unset-in-hole: no string, a regex that matches nothing; and an idea, a constant for 
  by: parked/ideas/never-constant
  subject: unset-in-hole

CITED L4316 2026-11-18 OWNER, on `${@y}`: a proposal with examples first; otherwise a future direction (Frank, to the pred
  by: parked/ideas/array-in-hole
  subject: (none)

CITED L4354 2026-11-18 OWNER RULING — `${@y}` is a future direction: not built, not defined now (Frank, to the predicate m
  by: parked/ideas/array-in-hole
  subject: (none)

CITED L4492 2026-11-19 OWNER RULING — padded-order
  by: core/principles/stated-behaviour
  subject: padded-order
  -> L4818 [ BODY:padded-order] 2026-11-19 MANAGER — after lane predspec29 (rev 29): readings not supported, one statement withdrawn (no owner words)
  -> L5048 [ BODY:padded-order] 2026-11-19 MANAGER — review r54 of rev 29: dispositions ruled (no owner words)
  -> L5134 [ BODY:padded-order] 2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited` macro, and a direction on ma
  -> L5487 [ BODY:padded-order] 2026-11-19 MANAGER — the withdrawal above is itself CORRECTED: taking a tuple apart is OPEN (tuple-parts), not confirmed

CITED L4710 2026-11-19 OWNER, asked plus-operands: a parameter restriction written `m(g & /\d+/)`, and the same for arithm
  by: parked/ideas/restricted-parameter
  subject: plus-operands
  -> L4746 [TITLE/TAG:plus-operands] 2026-11-19 OWNER, on plus-operands: `+` is for numbers only; a class as the base (an idea)
  -> L4771 [ BODY:plus-operands] 2026-11-19 OWNER, discussing the base idea: numbers are strings over an ordered set of symbols
  -> L4794 [TITLE/TAG:plus-operands] 2026-11-19 OWNER RULING — plus-operands
  -> L4818 [ BODY:plus-operands] 2026-11-19 MANAGER — after lane predspec29 (rev 29): readings not supported, one statement withdrawn (no owner words)

CITED L4746 2026-11-19 OWNER, on plus-operands: `+` is for numbers only; a class as the base (an idea)
  by: parked/ideas/class-base
  subject: plus-operands
  -> L4771 [ BODY:plus-operands] 2026-11-19 OWNER, discussing the base idea: numbers are strings over an ordered set of symbols
  -> L4794 [TITLE/TAG:plus-operands] 2026-11-19 OWNER RULING — plus-operands
  -> L4818 [ BODY:plus-operands] 2026-11-19 MANAGER — after lane predspec29 (rev 29): readings not supported, one statement withdrawn (no owner words)

CITED L4771 2026-11-19 OWNER, discussing the base idea: numbers are strings over an ordered set of symbols
  by: parked/ideas/class-base
  subject: (none)

CITED L5048 2026-11-19 MANAGER — review r54 of rev 29: dispositions ruled (no owner words)
  by: parked/ideas/known-nothing parked/ideas/warning-rows
  subject: (none)

CITED L5134 2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited` macro, and a direc
  by: parked/ideas/limited
  subject: padded-lazy-sparse
  -> L5245 [ BODY:padded-lazy-sparse] 2026-11-19 MANAGER — after lane predspec291 (rev 29.1): review r54 applied and filed (no owner words)

CITED L5451 2026-11-19 OWNER RULING — import-several: an import may name several files; one name bound to it is the combin
  by: lib/builtin/import lib/builtin/import/filter
  subject: core/modules/binding-list core/modules/import import-several
  -> L5474 [TITLE/TAG:core/modules/binding-list] 2026-11-19 MANAGER — a statement told to the owner under import-symbols is WITHDRAWN (the positional binding list)

--- supplementary keyword pass (cited entries with no slug subject) ---
== L644 /[Ee]numerate/
  L1201 (8) 2026-11-15 OWNER POINTER — `enumerate` as a basis for `any_case` (Frank, to session 133, box clock 21:59)
== L722 /OWN-1|filter modifier|FILTER MODIFIER/
== L1026 /occurrences/
  L1068 (2) 2026-11-15 RULINGS — a per-call hit name; no count warning; the hole is the scope an `&` in it anchors to (Frank, to session 133, 
  L1448 (1) 2026-11-16 OWNER — unset-component: leaning to "unset fails", wants a default worked out; idea: one "or equals" operator shared wi
== L1083 /same stretch whole/
== L1126 /unpadded/
  L1139 (1) 2026-11-15 IDEA from the owner (not a ruling) — compare an ARRAY of numbers (Frank, to session 133, box clock 20:58)
  L1178 (1) 2026-11-15 RULING — `json.quoted` is cut from the first spec (Frank, to session 133, box clock 21:54)
== L1178 /json.quoted/
  L1190 (1) 2026-11-15 OWNER IDEA on record — "blessed" callouts for the DFA (Frank, to session 133, box clock 21:58)
== L1318 /macro-arguments|array of macros/
== L1832 /own kind|OWN KIND/
== L2160 /non-dfa|beyond the user/
== L2188 /REGEX MODEL|regex model/
  L2197 (1) 2026-11-17 OWNER — a regex model for occurrences (Frank, to session 138, box clock about 13:10; a model offered with "Correct?", n
  L2210 (1) 2026-11-17 OWNER — the regex model explains; it does not exclude useful features (Frank, to session 138, box clock about 13:20)
  L2233 (1) 2026-11-17 OWNER RULINGS — regex-settles; absent-under-not (Frank, to session 138, box clock about 13:25)
  L2310 (1) 2026-11-17 OWNER RULING — when-meaning (Frank, to session 138, box clock about 13:55)
  L2385 (2) 2026-11-17 OWNER LEAN — a loop pass has its own labels (Frank, to session 138, evening; a lean with a request, NOT yet a ruling)
  L2442 (1) 2026-11-17 OWNER, reconsidering the entry above within minutes (Frank, to session 138, evening)
  L2454 (1) 2026-11-17 OWNER RULING — after-loop-read: the last pass's own label (Frank, to session 138, evening)
  L2616 (1) 2026-11-17 OWNER on what `hits` is (Frank, to session 138, evening; questions, not yet a ruling)
  L2631 (2) 2026-11-17 OWNER RULING — the hit list: atomic and anchored (hits-committed and hits-text together) (Frank, to session 138, evenin
== L3062 /quantifier/
  L3522 (1) 2026-11-18 OWNER RULING — condition-in-sequence: yes, and `&` stays (Frank, to session 139, morning)
  L3539 (4) 2026-11-18 OWNER RULING — quantified-condition: an error, as a formal punt (Frank, to session 139, morning)
  L3618 (1) 2026-11-18 OWNER RULING — lone-complement-match: it stays an error; provide "anything" (Frank, to session 139, late morning; close
  L3647 (1) 2026-11-18 OWNER, a question on the conditional form (Frank, to session 139, afternoon; a QUESTION, nothing ruled)
  L3671 (1) 2026-11-18 OWNER RULING — when-default: the missing else requires nothing; and a `when` operator to be considered (Frank, to sessi
== L3513 /\[_ = A\]/
  L5403 (1) 2026-11-19 OWNER, import-symbols: leaving a member out (`(=,left=)`, `(=, left=_)`)
== L3762 /when\(x\)|single arg/
== L4354 /@y/
  L4364 (2) 2026-11-18 MANAGER CORRECTION — readings of this evening NOT supported by the runs of lane predspec28 (the predicate manager, late
  L4391 (1) 2026-11-18 MANAGER — review r52 of rev 28: readings withdrawn or corrected, and calls made (the predicate manager, night; no owner
== L5048 /known nothing|warnings as rows/
== L1362 /tuple as a value|tuple-as-value/
== L1394 /take.*apart|tuple-parts/
  L1402 (1) 2026-11-16 OWNER IDEA (offered, not a ruling) — first/rest binding with recursion (Frank, to session 134, box clock 09:52)
  L1433 (1) 2026-11-16 OWNER RULING — first-rest: PARKED, kept in the wings (Frank, to session 134, box clock 10:22)
== L583 /Q6|Q9|metadata|check\(/
  L682 (1) 2026-11-14 RULING — counting occurrences (Frank: "more obscure but valuable"; concern: confusion with value numbers; put it in a l
  L732 (3) 2026-11-14 RULINGS on rev 3's contradictions (Frank: "agree all four")
  L1068 (1) 2026-11-15 RULINGS — a per-call hit name; no count warning; the hole is the scope an `&` in it anchors to (Frank, to session 133, 
== L573 /C9/
  L732 (2) 2026-11-14 RULINGS on rev 3's contradictions (Frank: "agree all four")
== L2493 /matching language/
```

## PROBED-AND-HELD

- 120 new/changed `rulings:` items: every cited title resolves to exactly one record entry, and all 129 quoted segments are inside it
  (53 exact, 76 whitespace-only, 0 absent). 118 of 120 quote the owner's words, with his words told apart from the manager's by the
  entry's "HIS WORDS"/"his words:" marker in ctx.txt. Exceptions: RULING-3.
- The prior round's worst shape (a "Yes" reopened minutes later) is now carried correctly on core/modules/positional: both the
  09:50 "Yes" and the 09:58 reopening are items, the first glossed "REOPENED the same morning". The piece status `open tuple-parts`
  matches the 11-19 correction entry.
- Glosses that state a later supersession, checked and correct: zero-pass-record (absent-rule reversed the 12:45 WORDING, ANSWER kept),
  pass-list-read point (1) reopened then settled by the `$x` ruling (L2684), last-pass-default STANDS per after-loop-read (5)
  (L2467), anchored "Anchored def: agree" corrected by the 21:20 entry, Q1 foundation narrowed, library-not-syntax withdrawing the 11-14
  TUPLE CONDITIONS, sigil PAUSED within the half hour, label-section, condition-kind CORRECTED BY HIM, first-rest preference then
  PARKED, unset-component / default-unused (manager's reading of "agree" labelled), drop-mark retiring match-context (explainer
  piece cites only his remark, labelled REMARK).
- Status words of the 33 new pieces against the record: core/values/{comparisons, tuples}, core/modules/naming, core/filters/negation,
  lib/counting/{count, some}, lib/builtin/{enumerate, import} `ruled` each have at least one owner ruling and no later reversal of what the
  statement says. number-domain's followers (L4364, L4391, numeral-width) touch arithmetic width only, not comparisons. The `count`
  items' lean (L823) is followed by the budget ruling (L832) and the later-optimisation note (L840), all carried. lib/assert/assert `ruled` on the
  agreed CONCEPT, with the spelling marked a placeholder reading (held, borderline). lib/control/atomic, computed-labels, metadata,
  lib/builtin/pattern, core/holes/value/other-positions, core/modules/standard-library `reading` (held). The `under-construction`
  pieces (import/filter, eval, ...) held. stated-behaviour ruled->reading follows r59 RULING-1 and the record (the general words
  were the manager's).
- default-set/members' slug renamed `default-imports`, documented in the details history (the record's word `default-set` already
  names the 11-16 question). Held as a documented rename.
- Sub-part (b): the named list is ruled (binding-list, call-shorthand, all-symbols, leave-out, conflicts: each statement traced to
  the 11-19 import-symbols rulings, with the manager's readings marked "(a reading)" except RULING-8a). `import` as a call is a LIBRARY piece
  (lib/builtin/import, `defined: native (it reads library files at compile time)`). The binding list stays in core. "primitive" no longer
  appears as a designation in any base file: every `Primitive:` line was removed (diff lines 2232-2433), `defined:` is used throughout, and
  any_case says `defined: native (for now, by the owner's ruling ...)`. The owner's "provides the symbols" (offered for discussion) is
  carried nowhere as a ruling. The only residues are the move-reason lines (RULING-9).
- import's readings correctly demote the 2026-11-14 addendum (a paraphrase) from `rulings:` to `readings:` (r59 RULING-4 applied).
  The level-error item (L2160, "RULED for libraries") has no later reversal.
- Lint not re-run: the RULING lens checks words, and the lint is clean at the frozen commit per COMMON.md.

CRITIC COMPLETE
