# CRITIC fixind: predfold1122 (r82)

## Findings

### FIXIND-1  CONFIRMED  doc (teaches errors)  effort S  blast: parked/ideas/user-doc-traps (the seed list for user documentation)
The user-documentation trap list in parked_details.md (parked/ideas/user-doc-traps, unchanged text) still teaches
five withdrawn or revised rules, unmarked:
- item 15, parked_details.md:708: "A binding's name is not a path." Revised by binding-prefix (record
  "2026-11-22 OWNER RULING — binding-prefix": "with one use the prefix is legal"); the base bullet saying the same was
  removed (core_details.md:623 history), its copy here was not. Its advice "label the part (`[aa = A]`, then `aa.h`)"
  now has the shorter legal `A.h` for one use.
- item 21, parked_details.md:731-734: `occurrences(/${c}(?<h>\d)/, min = 2)` "with c := NOT (h: >= 5)": a condition
  bound alone naming a label its binding does not hold, now a compile error at `c` (core.md:1376, bound-condition:
  "A condition or computed value bound alone that names a label no pattern in its binding holds is a compile error
  at the binding").
- item 13, parked_details.md:688-693: the sorted list `/(?:(?=(?<n>\d))${c}(?<h>\d);)*/` "with c := ..." binds the
  pass-start-read test alone: the same compile error (the record names "pass-start-read's `c`" among the five
  refused definitions, record line 123-124; the base re-wrote it in its hole).
- item 25, parked_details.md:745-749: "a flat `v` outside `date := [y = year] SEQ "-" SEQ [m = month]` reads the last
  mention, the month's (ruled 2026-11-21: flat-read-outside): write `m.v` to say which." Under label-reference the
  flat `v` is refused (core.md:453: "The bare `x` is refused here"); `m.v` is now `date.m.v` too (m is date's part
  label, not written in the reader's text).
- item 30, parked_details.md:766: `([ok = item & ((h, m): ("5", "3"))] | item)+ & some((ok: anything))`: `h`, `m` are
  item's, not written in the program: refused by label-reference; and `item` is used twice, so `item.h` would be the
  binding-prefix error too. The base line was re-spelled `[it = item] & ((it.h, it.m): ...)` (core.md:356).
Repro: grep -n 'not a path\|c := NOT\|flat `v`\|ok = item & ((h, m)' subject/parked_details.md.
Expected: each item restated under today's rules (or marked overtaken, as the list already does elsewhere).

### FIXIND-2  CONFIRMED  doc (a live reading against a ruling)  effort S  blast: lib/search/occurrences, lib/search/hits
library_details.md:424, a live `readings:` item of lib/search/occurrences, unmarked: "the label `hit` (written as a
group in rx text) is a capture the caller receives, here and in lib/search/hits (a reading of pure-label ...) —
UNTESTED as meant". helper-captures RULED the opposite (record "2026-11-22 OWNER RULING — helper-captures": "occurences
et al should only set labels not captures unless they are so declared"); the base now says "The body's `hit` is the
label-only group: a label and no capture" (library.md:354). The lane's history line (library_details.md:437) records
the BASE bullet's removal; the details reading it mirrored was kept as if live.
Expected: moved to `rejected:` "by owner ruling — helper-captures (b)".

### FIXIND-3  CONFIRMED  doc  effort S-M  blast: every details/parked_details printed program (the sweep's scope gap)
The label-reference sweep checked "every printed program of the three base files" (core_details.md:757, predref
SCAN); the details files' live readings and evidence lines were not swept, and the bound-condition sweep likewise
(core_details.md:1869 "every binding printed in core.md, library.md and parked.md"). Unchanged details text still
prints, as CURRENT (readings / evidence, not history, not "verbatim as run" of a rejected candidate):
- library_details.md:454 `hits(/\d+/) & occurs.none((hit: >= 100))`, SUPPORTED reading: bare `hit` from a macro
  body; call-prefix case 1 makes it `hits.hit` (the base line was re-spelled `[h = hits(/\d+/)] & ...h.hit`,
  library_details.md:465).
- library_details.md:481 `occurrences(x) & some((hit: /(?s).*/))`: bare `hit`.
- library_details.md:422 hit-carry's witness `occurrences(/${c}(?<h>\d)/, min = 2)`, c := NOT (h: >= 5): a condition
  bound alone, now a compile error (bound-condition).
- core_details.md:1251 the tuples evidence line `time & ((h, m): >= (9, 30))` SUPPORTED: bare `h`, `m` from `time`;
  the base line it supports is now `time & ((time.h, time.m): ...)` (core.md:933).
- parked_details.md:129 (zero-pass mark NOTES): "Rejecting the empty case has spellings today: ... a count
  (`n := count((h: S))`, `(n: >=1)`)": that spelling is now a compile error at `n` (record line 115-117); today's is
  `(count((h: S)): >=1)`.
- parked_details.md:450 (kleene-completion COST) `t2 & ((h, m): padded(>= (9, 30)))`: bare `h`, `m` from `t2`.
Repro: fixind/lref2.py over the six files (bare names left of `:` / `$x` not written as a group or part label in the
same span), then reading each hit's context. Expected: re-spelled, or marked "as printed before label-reference /
bound-condition" where kept as found.

### FIXIND-4  CONFIRMED  doc (a revived rejected candidate left rejected)  effort S  blast: core/labels/export/flat-read-outside, core/labels/export
- core_details.md:668, `rejected:` of flat-read-outside: "(b) a flat read of a part's labels from outside is a
  compile error, the path required (his sentence of 2026-11-19: "... So it's b.x or a.b.x.") — by owner ruling —
  flat-read-outside: a; both programs of the piece would be refused". Under label-reference its SPELLING side is
  now the rule: the bare read is refused and both programs of the piece were re-spelled `pair.x`, `date.v`
  (core.md:453). What stays rejected is only its GROUND (ambiguity), not its refusal. Unmarked; read cold, the
  entry says the refusal was ruled out.
- core_details.md:645 (core/labels/export readings): "a bare `v` outside `date := ...` reads the last mention ...
  RULED 2026-11-21 (core/labels/export/flat-read-outside), no longer a reading": now false as worded (the bare `v` is
  a compile error; `date.v` reads the last mention). Same for core_details.md:673 "(a) flat reads outside a binding
  follow the inside rules — RULED".
Expected: (b) annotated "its refusal of the bare read revived by label-reference (2026-11-22), its ambiguity ground
still rejected"; the two readings re-worded to `binding.x`.

### FIXIND-5  CONFIRMED  doc (a withdrawn reading kept live; a SUPPORTED claim on an open question)  effort S  blast: core/holes/bare-condition, zero-binding
core_details.md, core/holes/bare-condition `readings:` (unchanged lines):
- :1772 "a binding whose whole body is a bare condition behaves as the bare condition (the manager's reading 11) —
  SUPPORTED (preddoc1 PART R11 ... the rival, the binding as its own rx, never holds)". For a condition naming a label
  this is now a compile error (bound-condition); for one naming only `0` it is the OPEN zero-condition-binding
  (core.md:1401, "Neither answer is applied"), whose candidate (a) this reading asserts as SUPPORTED.
- :1775 "(the manager's (b) of zero-in-definition) a condition bound ALONE has no rx of its own: its `0` is the match
  so far of the definition it is USED in — UNTESTED": the record WITHDRAWS exactly this reading ("WITHDRAWN by the
  manager on this position: ... (case-2 entry, reading (b); zero-in-definition entry, reading (b))", record line
  78-80). The parallel case-2 reading WAS marked withdrawn (core_details.md:1829); this one was not.
Expected: :1775 marked withdrawn (record entry named); :1772 restricted to a hole's in-place condition, or pointed at
zero-binding as one candidate, not SUPPORTED.

### FIXIND-6  CONFIRMED (textual conflict)  design/doc  effort S  blast: lib/strings/join, lib/records family
library.md:528 (lib/strings/join, unchanged): "Joined parts stay reachable by their labels (`c.A`)." Its origin is
the 2026-11-14 join note (COND-FAMILY.md:281: "the joined parts are always navigable labels (`c.A: <200`, `c[1]`)"),
i.e. `c` a label on the call `join(a)`, `A` a MEMBER of the argument reached by its name. The owner's statement of
2026-11-22, "[ c = B(A) ] does not allow c.A" (record line 424-430; core.md:491 "a call's label reaches no argument
by the argument's name"), says the opposite for a call's label in general; the base gives no exception for `join`.
Either join is a stated exception (it reads the declared order and names structurally, the 11-14 reading) and must
say so beside the closed-argument rule, or the bullet is stale. Ask or mark; no answer moves today (join is
`defined: native`, no printed line uses `c.A`).

### FIXIND-7  CONFIRMED  doc (two adjacent bullets disagree)  effort S  blast: core/labels/labels-vs-captures (array-scope)
core.md:308-309 (array-scope bullet, unchanged by this diff): "The array's scope is the entire rx as composed, not
one literal or one definition". The bullet after it (core.md:313-315, array-in-piece) and the record's class
paragraph (record line 20-22: "array-scope ... is read over the definition the question is written in") make the
scope exactly ONE definition for a bound piece: the line "Bound first" (`A SEQ B`, B bound, WHOLE `7;1` FAILS)
refutes "not ... one definition" as a universal. The restatement kept the old exclusion; it now holds only for a
question written where both parts are in place.
Expected: "the entire rx as composed in the definition the question is written in (not one literal)".

### FIXIND-8  CONFIRMED  doc (parked premises gone)  effort S  blast: parked/ideas/label-hygiene, parked/ideas/label-parameter
- parked/ideas/label-hygiene (parked.md:176-180, parked_details.md:774-799, untouched by the diff although the record
  tags it on the label-reference ruling and the entry before it, record lines 251, 274): its DIRECTIONS say "none
  ruled", but direction (b) "labels reached through the pattern's own name (`t.h`), so two patterns' `h` never meet
  unqualified" is now ruled (binding-prefix + label-reference), direction (a) "a pattern EXPOSES only the labels it
  declares" is the new parked/ideas/declared-labels, and helper-captures makes library bodies' labels label-only. Its
  WHAT ("a collision is an error the user did not write and cannot fix without renaming their own labels") is no
  longer true as stated: a library label is reached only through its source, so a collision is referenced only by
  the user's own prefixed text. Its trigger "the first library file with labels" also stands unexamined.
- parked/ideas/label-parameter (parked_details.md:810-814): "QUESTIONS IT RAISES (listed, none asked yet): ... whether
  the body may also read labels that are NOT parameters" is answered: no (bound-condition, nested-scope case 1). And
  the THING is now under construction as core/operators/bindings/label-variables while the idea "stays parked"
  (parked_details.md:835): label-only-group, in the same position the same day, LEFT the parked list ("the THING is
  needed, so it leaves the parked list", record line 320-321). Two treatments of one situation; restricted-parameter
  vs macro-types the same.

### FIXIND-9  CONFIRMED  doc (a retired term as a current rule)  effort XS  blast: core/operators/statements, lib/search/within
The binding form of a computed label is withdrawn (record line 127: "core/values/computed-labels (a reading) is
withdrawn as a binding form"; the piece renamed "A computed value in an entry", core.md:936 "it is never bound alone
to a name"). Unchanged base text still states it:
- core.md:1536 (core/operators/statements): "A binding that mentions a match label is match-dependent (a computed
  label); otherwise it is pure (compile time)." A binding mentioning a match label is now legal only when a pattern
  in it holds the label, and is then an ordinary pattern binding, not a "computed label".
- library.md:416 (lib/search/within): the day difference is "out of reach of a set written in the language: a
  computed label or a blessed callout" (no in-place spelling of a day difference exists: `days` is unplanned).
(library.md:766 is marked "kept as found": fine.)

### FIXIND-10  SUSPECTED  design (parse rules whose ground assumed a label-only left part)  effort S  blast: core/conditions/form, core/operators/precedence, core/diagnostics/errors
Three unchanged sentences were written when the left of `:` was "a label path, never an expression"
(core_details.md:893, the statement until then):
- core.md:638 "Left of `:` a bare name or a label path is a label; on the value side a bare name is a binding". With
  a value now left of `:` (core.md:650), a bare name INSIDE a left-side expression, `((n + 1): <5)`, is on the left
  of `:` (so a label by :638) and inside a value (so a binding, by the value-side rule and the parse reading
  core.md:656-657, which makes "any other expression" a VALUE). Not stated which; the examples all use `$a`.
- core.md:1448 precedence row 9 (`:` loosest in an entry) and core.md:1453 "Inside an entry ... `&` and `|` bind
  tighter than `=` and `:`": before, `(h | m: <5)` or `(A & h: <5)` had a non-path left part and was refused; now the
  left part `h | m` parses as a VALUE expression in which `h`, `m` are BINDINGS (or labels; see above), and
  `$h | $m` as a value of several strings (the compile error "for now", core.md:658). A typo for `(h: <5 | m: ..)`
  changes from a form error to a different program or a different error. The parse reading should say whether a
  left-side expression may contain bare `&`/`|` at all.
- core.md:639 / core.md:1667 "A label named twice in one condition is a compile error": with value-left, is
  `($h: <5, h: >2)` (the same label read once as a value, once as a label; `($h: S)` and `(h: S)` "answer alike")
  a label named twice? The ground assumed every left part names a label directly.
What would confirm: a ruling or reading on each; no printed line exercises them.

### FIXIND-11  SUSPECTED  design (a prefix position the older name rules did not foresee)  effort S  blast: core/values/metadata, core/operators/statements, core/labels/paths/call-prefix
- Metadata through an implicit part label. core.md:946 "A part label over an array carries two fields: `.index` ...
  and `.label`"; binding-prefix (core.md:504-505): a binding used as a part "carries a part label of its own name, as
  if `[A = A]`". Composed, `/${days}/ & (days.index: >= 2)` with days := `[/Mon/, /Tue/, /Wed/]` (no `w`) becomes
  legal metadata, and `months.index` beside `months.mname.index` (library.md:224-230). No sentence admits or refuses
  it; core/values/metadata's ground (core.md:955-956: reached "through its name (`days.w.index`)") assumed the
  binding's name only PREFIXES a written part label.
- A part label named like a provided macro (record line 327: "`[hits = occurrences(..)]` ... a label named like a
  provided macro, which "still works" (core/operators/statements)"). Its ground, core.md:1529-1533, is that names are
  "reserved in CALL position only" (said of the built-ins; the validation extends it to provided macros); call-prefix
  (core.md:535) now puts a macro's name in PREFIX position too. In `[hits = occurrences(/\d+/)] & hits(/[a-z]/) &
  (hits.hit: ..)`, `hits.hit` names the part label's `hit` or the call's surfaced `hit`: not stated
  (binding-prefix states only "a label and a binding of one name"; the macro case is not that). The printed line
  library.md:339 is unambiguous only because no `hits(..)` call is in it.

Minimum witness length: these are textual findings (each repro is a file:line and the rule sentence it breaks);
no model was run or mutated (the MODE-CLOSURE lens owns runs). The scans' unit is one printed program span.

## PROBED-AND-HELD

- Label-reference over printed example lines: fixind/lref.py over the 240 three-mode lines of core.md, library.md and
  the three details files (program and each `NAME := body` checked as its own definition): 7 hits, all explained
  (core.md:1396 and core_details.md:1860 printed refusals; core_details.md:524/531 rejected candidates verbatim as
  run; core_details.md:759 the printed "Bare" refusal; core_details.md:975 a quoted draft refusal). Every base
  example line holds.
- Label-reference over prose code spans: fixind/lref2.py over 1,001 spans holding `&`, `:=`, SEQ or a hole in the six
  files: 56 hits in unchanged lines; each read in context. Held: generic `P`/`X` fragments (core.md:690, 717, 790,
  852, 900-901, the `$x & S` rows), owner quotations (core.md:1354-1357, core_details.md:1732, 1955), printed
  refusals (core.md:1340, core_details.md:1822), history "until then" text. Not held: FIXIND-1, -3.
- Bound-condition: every `NAME := (cond)` / `:= count(..)` / `:= $..` in the six files (grep): base clean except the
  intended refusals; details/parked not (FIXIND-1, -3, -5).
- Withdrawn sentences: "They are the same label" (only history/rejected), "the `&` is taken as a placeholder" (gone),
  "never an expression" (only history), "laid against the pattern it meets" for bound conditions (core.md:632 is the
  ruled form for a condition in place: held), "A binding's name is not a path" (base gone; trap 15 FIXIND-1),
  flat reads (base re-spelled: core.md:428, 447, 453, 1280, 1354-1356 held; details FIXIND-4).
- helper-captures: every provided body in library.md writing a named group (grep `(?<`): occurrences, hits now
  `(?<:hit>`; peek/endsWith/list_of/capture lines' groups are in ARGUMENTS (the caller's text, a capture: held, as
  library.md:329 states); `chars`, `months` use part labels (no capture): held.
- `c := (0: ..)` left open: core.md:1392, 1401-1413 apply neither answer: held.
- Compile-error index (core.md:1660-1679): the new rows read against their pieces: held (the label-reference
  refusal itself has no row; the index says it is partial).
CRITIC COMPLETE
