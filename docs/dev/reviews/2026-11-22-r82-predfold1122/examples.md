# CRITIC examples: predfold1122 (r82)

## Findings

### EXAMPLES-1 — the ruled `occurrences`/`hits` bodies are written in a form the subject calls not defined, and that the literals rule does not admit
CONFIRMED (text). Severity: design. Effort: small (re-spell two bodies, or re-state one status). Blast radius: every
printed program that calls `occurrences` or `hits` (library.md lib/search/occurrences, lib/search/hits; core.md
core/labels/paths/call-prefix, its 6 example lines; lib/counting, the record's validation lines).
- library.md:307 (ruled 2026-11-22): "`occurrences(x, min = 0)` is the lazy-gap loop
  `/(?:(?s:.*?)(?<:hit>${x})){${min},}(?s:.*)/`"; library.md:346: "`hits(r) := /\A(?>(?:(?s:.*?)(?<:hit>${r}))*[\s\S]*)\z/`".
- The form `(?<:hit>...)` is core/labels/label-only-group, core.md:364, status `under-construction`; doc_format.md:83-84 (status list):
  "`under-construction` (a direction acknowledged, not defined)"; core.md:94 (core/principles/build-later, ruled): "A
  meaning can be acknowledged and its build deferred: the program is refused with the under-construction error."
  Read literally, every printed `occurrences`/`hits` program is refused with the under-construction error, yet each
  prints answers.
- core.md:200 (core/patterns/literals, ruled 2026-11-14): "An rx literal `/.../` is full PCRE and means exactly what
  PCRE means; the predicate language adds only two marks inside it, the hole `${` and, under its switch, the operator
  `&`." `(?<:hit>` is a third mark, and core.md:375 itself says "libpcre2 rejects `(?<:x>foo)` (error 162)": the two
  ruled bodies are not legal rx literals under the literals rule as written.
- Observed vs expected: expected the ruled bodies to use only defined, admitted forms (or the label-only piece to
  carry a defined meaning and an amended literals statement). Observed: neither.
- Unlock (the general form): the thing the bodies need already exists at the expression level, core.md:371 "It is
  to rx text what `[x = A]` is to the expression level: a label, no capture". A body written with `[hit = x]` in
  place of the rx-text group (e.g. a sequence of a lazy gap and `[hit = x]` under the loop quantifier) uses only
  ruled forms and gives the same labels; the rx-text form then stays an idea for USER literals, under construction.
  I did not hand-model that re-spelling's answers (the lazy-gap-as-operand form is not in the diff); my hand model of
  the bodies as written (a label, no capture) reproduces every printed line (PROBED-AND-HELD).

### EXAMPLES-2 — the compile-error table refuses neither the ruled label-reference error nor two of the printed refusals
CONFIRMED (text: table rows vs printed refusals). Severity: doc (the bare-name row) and design (the `c.d` row, below).
Effort: small (2-3 table rows). Blast radius: the table core/diagnostics/errors (core.md:1661-1682) as an index.
Every printed refusal in the diff, run against the table's rows (the four new rows at core.md:1668-1671 included):
| printed refusal | table row that refuses it |
|---|---|
| core.md:533 `chars & (count((ch: /(?s:.)/)): ==3)`, "`ch` is not written in it" (label-reference, RULED "required") | NONE. core.md:1663 "an undeclared name that is not a label" does not reach it: `ch` IS a label (of `chars`) |
| core.md:514 binding-prefix "Twice used", `chars SEQ ":" SEQ chars & (chars.ch: "a")` | core.md:1670 — refused |
| core.md:569 call-prefix "Called twice, a plain read" (`occurrences.hit`, a MACRO's name) | core.md:1670 names "a binding's prefix, the binding used more than once"; a macro name is reached only via call-prefix's "under a binding prefix's two rules" (core.md:536). Refused by extension, not by the row's words |
| core.md:587 closed-argument `B(A) & (A.d: <5)` | core.md:1671 — refused |
| core.md:587 `[c = B(A)] & (c.d: <5)` "alike: no `d` surfaces" | NONE; see EXAMPLES-3 |
| core.md:494 `[c = B(A)] & (c.A.d: <5)` "is refused, run" | NONE (and "run" is an engine's refusal, not a rule) |
| core.md:1396 bound alone `/(?<h>\d)/ & late`, late := `(h: >5)` | core.md:1668 — refused |
| core.md:1385 (`lt5(S) := (h: S)`, a macro body) | core.md:1668 by the bound-condition text "A macro whose body is such a condition is the same compile error" — refused |
- The table says it is PARTIAL (core.md:1658: "this index is PARTIAL: more compile errors are stated in their
  pieces only"), so no row is REQUIRED; but the revision adds four rows and leaves out the one ruled error of the day
  with the widest reach (label-reference re-spelled every printed program). Expected: a row "a label not written in
  the referencing definition, read bare (it says to reference it with its source) | core/labels/paths/label-reference";
  the binding-prefix row widened to "a binding's or a macro's name"; a row for a path through a call's label to an
  argument's name (core/labels/paths).
- Accepted-as-legal check: no printed RULED example line in the diff (35 lines, PROBED-AND-HELD) is caught by any row:
  no value of several strings left of `:` (every left value is `count(..)`, `$a + $b`, `$a - 5`, `$h`), no binding
  used twice read plainly (`item` in "Same item" is used twice but read only through the part label `it`;
  `occurrences.hit` twice only inside `some(..)`), no condition bound alone.

### EXAMPLES-3 — `[c = B(A)] & (c.d: <5)` under a closing B is printed as a compile error with no rule; the ruled nearest rule makes it a warning
CONFIRMED (text). Severity: design (the diagnostic TIER of a printed line). Effort: small (one sentence + its row, or
re-print the line as the warning). Blast radius: core/labels/paths/closed-argument's "Closed by the macro" line
(core.md:587), and every path through a part label whose part closes the named label.
- Printed, core.md:587: "Closed by the macro: modes: a compile error (`B(A) & (A.d: <5)`, ... B(rx) := `/${[_ = rx]}xx/`;
  `[c = B(A)] & (c.d: <5)` alike: no `d` surfaces)."
- The piece's own statement covers only the ARGUMENT's binding name, core.md:572: "For an argument that is a binding,
  the caller's `A.d` is legal exactly where `d` is visible through the call; where the macro closes the argument's
  labels it is a compile error." `c` is a part label on the call, not the argument; the ruling quoted at core.md:574-576
  is likewise about `A.d` only.
- The ruled rule that does reach `c.d`, core.md:393-394 (core/labels/one-rule, ruled): "A test on a label no match
  can set draws a warning, not an error: it is a test that can never pass (`pcrec.test.never`,
  core/diagnostics/warnings)"; the warnings table core.md:1706 repeats it ("a test on a label no match can set
  included"). Under `[c = B(A)]` with the closing B no match sets a `d` that `c` surfaces, so by the ruled text the
  program draws `pcrec.test.never` and is legal (it never holds), not a compile error.
- The only "not visible = compile error" sentence is for a bare condition IN A HOLE, core.md:1307: "a label not
  visible there is a compile error" (core/holes/bare-condition/labels): an `&` condition is not that place.
- Expected: either a rule sentence (paths or closed-argument: "a path naming a label its source does not surface is
  a compile error", which then ALSO revises one-rule's warning for every `x.h` whose part never surfaces h, e.g. a
  typo'd path) or the line re-printed as the warning. Which one is a ruling-level choice (D26 tier), so it goes to
  the owner or is marked a reading; as printed it is neither.
- Related, same ground: core.md:494 "`[c = B(A)] & (c.A.d: <5)` is refused, run" rests on his statement "[ c = B(A) ]
  does not allow c.A" (core.md:491); "does not allow" is not worded as compile error vs never-pass warning either.

### EXAMPLES-4 — the changed `occurrences` bullet still calls two calls' shared `hit` "the ambiguity error", which label-reference and call-prefix no longer leave reachable as stated
SUSPECTED (text; what would confirm it: the manager's reading of which rule a group question through a macro name
across `&` falls under). Severity: doc, possibly design. Effort: small. Blast radius: library.md:331-333 and the
sibling binding case (`chars & chars & ...`).
- library.md:332 (the line the diff extended): "two calls in one chain exposing the same hit label are the
  ambiguity error, the per-call name its fix; each call reached through a label of its own (`a.hit`, `b.hit`) is not
  ambiguous (a reading)."
- After the day's rulings the bare `hit` can no longer be written by the caller at all (label-reference, core.md:517:
  "a bare name is a label the definition itself writes"; `hit` is the body's). Through the macro's name, call-prefix
  (core.md:536, ruled case 1) and binding-prefix (core.md:499) give: a PLAIN read with two calls is the "label the
  call" error (not the ambiguity error), and a GROUP QUESTION "reads every call's settings, in order" (core.md
  call-prefix, the line "Called twice, a group question reads every call", printed as legal for two calls across the
  sequence operator). For two calls across `&` (the "chain"), core.md:403 (flow) says "Across `&` a name both sides
  surface is an ambiguous reference: a compile error where a condition or a `$` references it", while binding-prefix
  says the group question through the prefix reads every use: `occurrences(/a/) & occurrences(/b/) &
  some((occurrences.hit: "a"))` is legal by one sentence and the ambiguity error by the other. No printed line
  decides it; the bullet keeps the pre-ruling wording.
- Expected: the bullet restated in the new terms (plain read: label the call; group question: every call, or the
  `&`-ambiguity if that is the intended reading, said once in binding-prefix for bindings and macros alike).

## PROBED-AND-HELD

(A) Every three-mode example line the diff ADDS OR CHANGES in core.md and library.md (and the two example lines it
adds to the details files, "The last use only" and "Bare, read as before the ruling"), re-derived from the pieces'
own rule text with my own hand model, written before opening any evidence script:
`R/examples/tmp/hm.py` (a backtracking engine in PCRE's order: one label rule with resets on entering an
alternation, an optional or a loop, the array of settings, atomic, lookahead, `\A`/`\z`, `&` as a filter over the
operand's own stretch, the number domain of canonical numerals, arithmetic outside the domain = nothing; FIND-ALL as
core.md:128 states it: the leftmost first surviving path, again from the reported end, after an EMPTY report a retry
for a non-empty path at the same place, then a step of one) and `R/examples/tmp/ex.py` (the 35 lowerings; output
`R/examples/tmp/ex.out`). Each output string was then matched mechanically against the documents (annotations such
as `(hits [..])`, `(l = ..)` stripped): 35 of 35 lines found byte-identical in WHOLE, SEARCHED and FIND-ALL:
- core.md: alternation, atomic, "Same item, on the item", "A count of zero", export statement 3, flat-read-outside
  (both lines), binding-prefix ("His example, every use", "One use"), label-reference "With its source",
  call-prefix (all 6 run lines: by the macro's name, labelled, called twice, A's own d, c.d, by B's name, the argument
  used twice), closed-argument "Visible through the call", value-left (all 6 lines), pass-start-read, computed-labels,
  metadata, holes/labels, nested-scope Example 1, bound-condition (3 lines).
- library.md: length, month_numbered, count, occurrences (2 new lines), hits (4 new lines, their hit lists too).
- FIND-ALL's empty-match rule exercised and held on pass-start-read (``@6, ``@11) and occurrences "Every hit" (``@7);
  non-overlap held on every multi-match line (e.g. binding-prefix ` 1:234`@6 starting at the previous end).
- computed-labels' claim "`(a: <(10 - $b))` answers alike on the 100 digit pairs": 0 of 100 differ (WHOLE).
- hits' annotations (hit lists for 11 texts) reproduced from the model's first path.
MINIMUM WITNESS LENGTH: the printed texts only (up to 27 characters) plus the exhaustive 100 texts of length 3; no
exhaustive sweep beyond the printed texts (that is MODE-CLOSURE's), so a difference needing another text is not
excluded by this lens.
(B) Legality, every printed program in the changed text: labels referenced with their source (label-reference,
core.md:517) — all re-spelled programs name a binding, a part label or a macro name, or a label their own literal
writes (35 of 35); no plain read through a binding used twice (`item` in "Same item" read only via `it`); no plain
read through a macro name called twice except the printed refusal; no reference through a closed argument except
the printed refusal; no condition or computed value bound alone except the printed refusal (`late`) and the
acknowledged old uses in lib/planned/standard; no value of several strings left of `:`; precedence (core.md:1435:
`&` looser than the sequence operator, `|` looser than `&`, `&`/`|` tighter than `=`/`:` inside an entry) gives the
intended parse for every program with mixed operators (alternation, Same item, pass-start-read's `NOT .. | ..`,
binding-prefix's `X SEQ ":" SEQ X & ..`, the two-call lines). The part label `hits` named like a provided macro held
(the record's validation: "still works", core/operators/statements). The refusals vs the table: EXAMPLES-2.
CRITIC COMPLETE
