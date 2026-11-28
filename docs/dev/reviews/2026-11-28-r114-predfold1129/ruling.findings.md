# CRITIC ruling: r114 predfold1129

## Findings

### RULING-1 — `when.h` still printed a compile error, while its own cited witness was flipped to legal (same-path-last missed)
CONFIRMED (text + run). Severity: answer. Effort: small (one bullet, one rulings item). Blast radius: lib/control/when, the
"Two arguments" shape (any wrapper that lists two places in sequence).
- library.md:375-376: "A name test and then both hold is two through the call: `when.h` is a compile error
  (core/labels/rule/one-path; run on a user macro of the same shape: lib/convention/argument-labels' line "Two arguments")".
- The fold flipped that very line (library.md, lib/convention/argument-labels, "Two arguments": `W(/(?<h>\d)/, /;(?<h>\d)/) &
  (W.h: "3")` now WHOLE `7;3` HOLDS, "one full path, the last mention", same-path-last 1).
- Record 12875-12877 (told with same-path-last, so ruled with it): "Of the reads that moved to errors when you ruled it, any
  that reach one path twice come back as legal; the fold reports which". when's body `T seq B | !^T seq C` with each spot
  listed is W's shape; `when.h` is such a read and is neither moved nor reported.
- Run: kit probe, `W(/(?<h>\d)/, /;(?<h>\d)/) & (W.h: "3")`, W(a, b) := `[(=) = a] SEQ [(=) = b]` -> LEGAL, `7;3` HOLDS,
  `3;7` FAILS (the then branch's `h`, the last). `when(...)` itself the probe cannot parse ("ERROR unsupported group"), so
  the census/GATE129 never saw when.h. Rulings item library_details.md:449 (one-path: "a name the test and the then branch
  both hold is two through the call") carries no same-path-last revision. Expected: `when.h` legal, then's `h` (or the
  doc says why when differs from W).

### RULING-2 — sentences REVISED/REVERSED on 2026-11-28 still printed as the current rule (record-tagged pieces left untouched)
CONFIRMED (text). Severity: doc (each contradicts a ruled line). Effort: small. Blast radius: five base sites.
- core.md:460 (core/labels/rule/paths, the one-path summary inside the path-rules bullet): "a step may be skipped only
  when exactly one label of that name is visible from the start" -- the sentence same-path-last REVISES (record
  12872-12874: "REVISES one-path's sentence ... to count distinct full paths; the manager's wording of one-path is
  corrected to his sentence "exactly one path possible from the start""). Unquoted, unmarked, as rule.
- core.md:956 (core/labels/flow, ruled 2026-11-27, TAGGED by same-path-last at record 12864): "A read that skips a step to
  such a name is a compile error asking for the full path" -- false for one full path reached twice (same-path-last 1;
  the fold's own line "One full path twice, the last mention", `y.r.g`).
- core.md:960 (core/labels/flow, TAGGED by last-placement at 12829): "a plain read with A used more than once is a
  compile error (core/labels/paths/binding-prefix)" -- REVERSED by last-placement (record 12848-12849).
- core.md:3091 (core/diagnostics/errors table): "a plain read through a binding's or a macro's prefix, used more than once
  (it says to label the part)" listed as a compile error -- reversed (last-placement 2; the fold's "Called twice, a plain
  read" and "Twice used, a plain read" are now legal).
- core.md:3092: "steps through one used more than once (alone-as-middle); ... or references A twice in its text
  (condition 1)" -- both reversed by the fold itself (alone-as-middle "Used twice, the last placement" legal;
  argument-default "Used twice in the caller's text, the last placement" legal).
- core/labels/flow and core/diagnostics/errors have no 2026-11-28 history line: the fold did not visit them although
  the record's `tags:` lines name core/labels/flow for both same-path-last and last-placement.

### RULING-3 — details `rulings:` fields still state, as RULED and unmarked, outcomes the 2026-11-28 rulings reversed
CONFIRMED (text). Severity: doc (the rulings field is the record-of-what-is-ruled the format relies on). Effort: medium
(about a dozen items; the house mark exists: "[REVISED IN PART <date> by <slug> ...]"). Blast radius: the pieces below.
- No 2026-11-28 bracket mark (REVISED/REVERSED/AMENDED) exists anywhere in the six documents (grep: zero), yet:
  - library_details.md:13 (lib/convention/argument-labels): one-path item "two spots or two arguments holding one name are
    two labels for a read through the call"; library_details.md:10 "[REVISED IN PART 2026-11-27 by one-path ...: its two
    stated cases are compile errors ...]" and :20 "[AMENDED 2026-11-27 by one-path: `list_of.h` and `W.h` are compile
    errors now ...]" -- same-path-last RESTORES transform-export's two cases (W.h, list_of.h legal again, printed so); the
    marks now say the opposite of the piece, and the piece has no same-path-last rulings item.
  - library_details.md:1005 (lib/records/list-of): "line 5: the item's two spots under `list_of` are two labels,
    `list_of.h` a compile error" -- printed legal now; no 2026-11-28 rulings item.
  - library_details.md:449 (lib/control/when): see RULING-1.
  - core_details.md:1533 (core/labels/paths/call-prefix): one-path item "lines 4 and 5: `c.d` and `pair.d` compile
    errors" -- `pair.d` legal now; call-prefix also moved "Called twice" to legal (last-placement); rulings28 = 0.
  - core_details.md:631 (core/labels/rule/paths): "[REVISED IN PART 2026-11-27 by one-path, line 4 ...]" -- line 4 itself
    revised by same-path-last; unmarked.
- Pieces whose printed answers moved on 2026-11-28 with NO 2026-11-28 rulings item (counted by field scan): call-prefix,
  argument-default (condition 1, `B.dd.d`, `pub.A.h`), closed-argument (`B.p.d`), shorthand-outside (`pub.A.h` written
  out), core/labels/export (statement 3, `pub.h` now an error), core/labels/rule/paths, skip-past-wall, ownership,
  one-use-read, flat-read-outside, argument-labels, list-of, occurrences, hits (14). doc_format.md:105-106: "a ruling that
  changes an EARLIER piece rewrites that piece's status and statement in the same commit" -- skip-past-wall
  (core.md:569, statement rewritten, status date 2026-11-27) and one-use-read (core.md:1394, statement rewritten, date
  2026-11-22) keep their old status dates.

### RULING-4 — the manager's "stacked labels are equal names of one gate" printed as rule and entered as a ruling
CONFIRMED (text). Severity: design/doc (a reading carries told-and-ruled answers and silently re-admits a rejected candidate's
idea). Effort: small to mark; the question itself is the owner's. Blast radius: stacked-chain, caller-label, argument-place,
sent-over-body-label, label-above-call.
- Record 12746-12748: "The manager's readings, for the fold to test (none ruled): ... a stacked label on a gate (`[a = [b =
  Q]]`): both are names of the one gate ... so `a.d` and `b.d` and `a.b.d` are legal".
- core.md:530, the STATEMENT of the ruled piece stacked-chain: "Two public labels stacked on one spot (`[n = [m = P]]`) are
  equal names of it: `n.m.d`, `n.d` and `m.d` read P's `d`" -- unmarked; the bullet below marks it a reading, the
  statement does not.
- core_details.md:724, in stacked-chain's `rulings:`: "2026-11-28 "label-names-gate: yes all five" ...; on P's use `m` and
  `n` name one gate." -- the reading attributed to the ruling.
- stacked-chain's own `rejected:` keeps "candidate (a), equal names only, no chain ... by owner ruling path-rules, rule 1";
  path-rules ruled the CHAIN (`n.d` "skips `m`" by rule 4). The reading keeps the chain's spellings but replaces its
  ground ("`n.d` skips nothing") -- a change to what path-rules ruled, not marked as such.
- core.md:735 ("Through the call's label and the body's", `Y.c.p.h` legal): ends "`p` and `a` stacked names of one
  spot" with NO reading mark; core_details.md:1149 says it was an error in the lane's first draft and is "an owner
  question in the lane report" -- the question exists only in the (denylisted) report, nowhere in the documents as open
  (parked.md / an `open` piece). Same for argument-place's `B.a.h`, `B.p.a.h` (core_details.md:1116 "listed in the report
  as an owner question").
- Attack: the told-and-ruled `Y.c.a.h` "a full path that skips nothing" (record 12775-12776) is true ONLY under this
  reading (otherwise `Y.c.a.h` skips the gate `p`, label-names-gate 1). So a ruled answer rests on an unruled reading;
  the documents should say so where `Y.c.a.h` is printed (core.md caller-label, argument-place).

### RULING-5 — the kinds row "a placed path" cites part-of-argument line 5, which the owner did not agree to
CONFIRMED (text). Severity: doc. Effort: trivial. Blast radius: core/labels/rule/kinds.
- core.md:801: "| a placed path (`date.year` in pattern position) | no implicit label: label it (part-of-argument 5) | ... |
  no, a gate (part-of-argument 5) | ...".
- Record 12796-12798: "agree 1-4 ... 5. refers to the local implicit label which we could simply say for now is limited
  to a binding or arg but not a path"; "RULING on lines 1 to 4 as asked; line 5 answered by him in his own words". Line 5
  as asked ("The placement is a gate like any other") was not agreed; the documents' own rejected item (core_details,
  placed-part: "line 5 as asked ... -- by owner ruling ...; for now") rejects it. "no implicit label" is the MANAGER'S
  reading of his line 5 (record 12809), not line 5. Cite "his answer to line 5 (the manager's reading)" and mark "a gate" a
  reading (or derive it from label-names-gate 1 if a placed path is a "crossing").

### RULING-6 — named-list-body-read's quoted lean "and nothing else of the argument" printed as RULED, against argument-is-gate 2
SUSPECTED (text; needs the owner or a scoping word). Severity: design. Effort: small. Blast radius: core/labels/export/named-list.
- core.md:1162-1163: "His words: "named-list-body-read: yes same as before.", on: `N2(rx) := ...` legal, "The body reads
  bare what its own list names, and nothing else of the argument""; core_details.md:1385 RULED with that sentence.
- In the same day's record, argument-is-gate 2 (ruled): "`dd.g` inside the body" and reference-example-checked: "rx.d
  would be the gate", "as would dd.d if d existed there": a body DOES read more of the argument, through a gate. And at
  12700-12701, in the same entry: "I did have the strong lean against reading through arguments but then ... I flipped."
- The ruled sentence holds only if "nothing else" is read as "nothing else BARE". The documents print it unscoped.
  Confirm by: asking, or printing the scope ("bare") as the manager's reading beside the quote.

### RULING-7 — `rx.d` under the body's own label printed a compile error from label-names-gate 2 alone; last-placement 1 says otherwise as worded
SUSPECTED (design). Severity: design. Effort: small (mark a reading, or cite binding-as-label condition 4). Blast radius:
core/holes/bare-condition/nested-scope, core/operators/bindings/reference.
- core.md:2447 "Example 3, the parameter's name under the body's label: modes: a compile error (`B(rx) := /${[dd = rx]}xx/
  & (rx.d: <5)` ...)"; bullet (nested-scope, core.md:2438): "the label written on the place is the gate's name, so `rx.d`
  there is no read (core/labels/rule/gates)" -- unmarked, a derivation; the owner's three examples do not include it.
- label-names-gate 2 ("Where none is written, it is the thing's own name") supports it; but last-placement 1, ruled the
  same day ("A placement makes a label of the thing's own name ...", amended "but local implicit") and
  reference-example-checked ("B.year uses the temp label that's created locally for binding B") make no exception for a
  labelled placement. The two ruled sentences pull apart here and the documents pick one silently.
- The refusal text (probe, run): "`rx.d`: no label `rx` is written in this text (... the start of a path is a label it
  writes, a binding's or a macro's name, or, inside a body, a parameter)" -- it lists a parameter as a legal start while
  refusing a parameter as a start: the message contradicts its own refusal.

## PROBED-AND-HELD


(a) Quotes, word for word. Mechanical check (ruling/q.py, q2.py, `python3 -I -B`, whitespace and backticks normalised):
every 2026-11-28 `rulings:` item's quoted words in the six documents (18 items, `...` elisions split) and 16 further
`His words: "..."`-style quotes on added lines are substrings of the record: 0 missing. Hand-checked against the record
lines: label-names-gate's five lines (core.md gates piece vs 12731-12739), argument-is-gate's five (12768-12774),
last-placement's five (12841-12846), same-path-last's three (12867-12871), part-of-argument's five and his answer
(12796-12808), reference-example-checked (12666-12674, the nested-scope and reference pieces), named-list-body-read's
statement, flipped and reconsideration (12699-12710), the DISCUSSION (12759-12760), the QUESTION (12764-12766), the y.r
lean (12837-12838): all verbatim. No 2026-11-28 "the manager's reading" line is quoted as his words.
Open/settled: list-over-label and sent-over-body-label stay `open` (record 12879: "derived, not asked") -- held;
forwarded-place `reading` (record 12777-12778: shown, not asked) -- held; branch-in-loop: not printed as settled -- held.
The seven ruling entries each land on a piece with a `rulings:` item (gates, one-path x2, argument-place, caller-label,
named-list x2, placed-part, binding-prefix, alone-as-middle x2, reference, nested-scope) -- held.

(b) Hand mapping of each "manager's reading ... for the fold to test" (and the MANAGER entry 12879):
- ref-ex-checked r1 (no `year` an error at the CALL) -> reference piece bullet + line "An argument without `year`":
  ADOPTED, grounded on argument-is-gate 4 (ruled later the same day) -- held.
- r2 ("not nameable" reversed for gated spellings, kept bare) -> core/labels/paths bullet, nested-scope statement:
  ADOPTED, backed by his words "No gate. rx.d would be the gate" -- held (but see RULING-7 for the labelled case).
- r3 (dd.d vs the strong lean) -> moot: argument-is-gate ends the lean; rejected item in argument-place -- held.
- r4 (placed twice, `rx.d` an error) -> superseded by last-placement; lines "Placed twice in a body ..." -- held.
- label-names-gate "one-path then counts only labels over in-place text and lists" -> gates readings, SUPPORTED as run;
  `[n = (Q)]` -> reading, run; stacked labels -> RULING-4 (adopted as statement); parenthesised composition -> marked
  reading, run -- held except the stacked one.
- part-of-argument line 5 reading (placed path makes no label) -> marked reading in placed-part, RUN; but RULING-5;
  `$date.year` VALUE -> marked UNTESTED; labels inside come along / once under a loop -> marked UNTESTED -- held.
- last-placement "local implicit" reading -> binding-prefix bullet "His amendment to line 1" -- held as marked.
- same-path-last "the fold reports which" -> one-path readings item (W.h, pair.d, list_of.h, date.v) -- held, except
  when.h (RULING-1).
- MANAGER 12879: sent-over-body-label (`x.h`, `x.p.h` legal) and list-over-label (`B1.h` error, `B1.p.h` legal) ->
  printed as the manager's readings, "derived; not asked", pieces stay `open` -- held.
Earlier rulings re-checked against the AFTER documents (pairs by `tags:`): binding-prefix's error (REVERSED: gone from
binding-prefix, call-prefix, argument-default, alone-as-middle, library occurrences; NOT gone from core/labels/flow and
the errors table, RULING-2); one-path's sentence and line 4 (REVISED: re-worded in one-path; NOT at core.md:460 and the
rulings fields, RULING-2/3); alone-as-middle's kept sentence (REVISED: gone, re-derived at core.md:601) -- held;
caller-label-export for `Y.c.a.h` (REVISED: rejected item added, statement re-worded, line legal) -- held; param-reference
line 4 (re-read "reads in a condition and never places", quoted words unchanged, marked) -- held. shorthand-outside
(`pub.A.h` for `[pub = B(A)]` stays an error) -- held, the written-out form moved (a derivation, not his ruled cell).
binding-as-label condition 1 ("referenced unambiguously") re-read by last-placement 2 -- held as a consequence, unmarked
in rulings (RULING-3).
Runs: kit probe, 5 programs (W.h legal; when unsupported; `rx.d` under `[dd = rx]` refused; `[k = Q]`, `k.d` legal;
`y.r.g` over `[y = [x = [r = A] SEQ [r = A]]]` legal, `73` HOLDS / `37` FAILS = the printed line). Witness shapes: nesting
depth 3 labels over 2 placements (the y.x.r line); max placements 2; macro depth 1 (W), the record's two-binding-level
lines read, not run.

CRITIC COMPLETE
