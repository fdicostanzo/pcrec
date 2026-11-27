# CRITIC EXAMPLES: r111 predfold1125

## Findings

### EXAMPLES-1 — `every`'s bullet says it parts from the item form on a loop that can make no pass; its own printed lines show it does not
CONFIRMED. Severity: answer-adjacent doc (a rule sentence contradicted by the piece's own printed answers). Effort: one
bullet plus one details reading. Blast radius: lib/counting/every, library_details lib/counting/every readings.
Piece: lib/counting/every (library.md:646-661). Ruling: array-argument (record l.10989), `every` "true when there are
no settings".
- The subject, library.md:653: "It reads SETTINGS: a pass that sets nothing is not judged, so where the label is
  optional, or the loop can make no pass, it is not the item form, the condition written inside the loop (the lines
  below)."
- The piece's own lines contradict the "no pass" half: "No pass: WHOLE `x` HOLDS, `7,x` HOLDS, `1,x` FAILS / SEARCHED
  `-x` `x`@1 / FIND-ALL `x 7,x 1,x` [`x`@0, `7,x`@2, `x`@8] (`/(?:(?<d>\d),)*x/ & every(@d, "7")`)" and "No pass, the
  item form: WHOLE `x` HOLDS, `7,x` HOLDS / SEARCHED `-x` `x`@1 / FIND-ALL `x 7,x 1,x` [`x`@0, `7,x`@2, `x`@8]" are the
  SAME answers in every mode. Under the old settings form (`some(c) & occurs.none(NOT c)`) the two parted on `x`; under
  the ruled `every` (true on an empty array) they do not. The fold carried the old sentence over to the new name.
- Repro (my own engine, `work/everyitem.py`, labels/array per core's definitions): `every(@d,"7")` on
  `/(?:(?<d>\d),)*x/` against the item form `/(?:(?<d>\d)${(d: "7")},)*x/`: 0 / 0 / 0 of 5,461 texts over `17,x`,
  lengths 0..6 (max witness length 6); same 0/0/0 for `+` (`/(?:(?<d>\d),)+/`). With the label optional
  (`/(?:(?<d>\d)?,)+/`) they part, 29 / 3,595 / 3,756 (first WHOLE witnesses `,`, `,,`, `7,,`).
- So the true statement: `every` differs from the item form exactly where a pass can set nothing (an optional label);
  a loop that can make no pass is NOT a difference (it is one for `some(@d,S) & every(@d,S)`, the line "No pass, set at
  least once"). The details reading "the settings form and the item form part on a loop that can make no pass as well
  (review r77 MODES-12) — SUPPORTED" (library_details lib/counting/every readings) is stale for the same reason: it
  names the retired form as "the settings form".

### EXAMPLES-2 — `when` with a CONDITION test: the ruled body applies `^` to a condition, which no document defines; no printed line; the model refuses it
CONFIRMED (absence + refusal repro). Severity: design. Effort: a reading + one printed line (or a ruling question).
Blast radius: lib/control/when, lib/control/when-test, core/patterns/lookaround/ahead, core/filters/family, the
place table. Ruling: bang-split line 5 (record l.11963) "`when(T, B, C) := T seq B | !^T seq C`".
- library.md:355-356 (when): "the guard is `!^test` for every kind of test, one body serving a condition and a pattern
  alike (lib/control/when-test)"; when-test statement: "A condition or a lookahead `^A` as the test consumes nothing".
  So `when((h: <5), B, C)` lays `!^(h: <5)`: `^` on a condition.
- Nothing defines `^c`: core/patterns/lookaround/ahead: "`^A` looks ahead, A matching from here"; the family table's
  `^A` row has operand "a pattern", kind "can match"; the place table row "a positive lookahead or lookbehind (`^A`)
  ... can match", while "a condition as a sequence operand ... a test". The only sentence that covered it, peek's
  "A condition given as A is zero width already: `peek(c)` tests c where it stands, as c does (a reading)"
  (library.START.md:345), was DELETED by the fold. By core/filters/kinds ("the error is at the use that needs the
  other kind") the body may even be a compile error for every condition test.
- No printed `when` line has a condition test (grep `when((` over core/library/parked: 0 hits); the three printed
  `when` lines are `^/\d/`, bare `/\d/`, `!^/x/`.
- Repro: the evidence model, imported up to its first check (`work/drv.py`, run in R/tree): `/(?<h>\d)/ SEQ
  when((h: <5), /a/, /b/)` -> REFUSED "unsupported group". My derivation (reading `^c` as c at its point): WHOLE `3a`
  HOLDS, `3b` FAILS, `7a` FAILS, `7b` HOLDS / SEARCHED `3b 7b` `7b`@3 / FIND-ALL `3a 7b 3b 7a` [`3a`@0, `7b`@3].
  The model does accept `^c` in a plain sequence (`/(?<h>\d)/ SEQ ^(h: <5) SEQ /x/`: WHOLE `3x` HOLDS, `7x` FAILS,
  i.e. `^c` = c, `work/p3.json`), so its reading exists but is not in any document; it is the `when` lowering
  (`!^test` over a condition) that it cannot run.
- Fix shape: state `^c` (a condition is zero width; `^c` is c, `!^c` is `!c`) as a reading in
  core/patterns/lookaround/ahead and the family table, and print one condition-test `when` line.

### EXAMPLES-3 — `C(n) := /(?<${n}>\d)x/`: an unmarked parameter placed as a capturing group's whole name, printed legal; label-needs-mark's sentence does not say whether it is covered
SUSPECTED (needs a reading or the ruling's scope). Severity: design (legality). Effort: one reading + one line.
Blast radius: core/holes (the group-name hole piece, core.md:1862-1871), core/operators/bindings/label-variables.
Ruling: label-needs-mark (record l.12042), the side note of sent-label-wall (l.12010): "a binding cannot use an
argument as a label ... This is to catch an unintended miss of not setting the arg as a label arg."
- core.md:2315: "A body that places a parameter's name as a label needs the mark: `[l = ...]` or `(?<:${l}>...)` with
  `l` not marked `l:` is a compile error at the definition."
- core.md:1871, printed LEGAL with answers: "A capturing group, the unspecified label: WHOLE `7x` HOLDS, `x` FAILS ...
  (`C(_)`, C(n) := `/(?<${n}>\d)x/`, is `(\d)x`)". With a whole-name hole the capturing group makes a label (core.md:1869
  `/(?<${n}>\d)x/`, n := "d", and "a group in its literals" is an export, core/labels/export statement 3), so `C("d")`
  places the parameter's name as a label: by the sentence's "places a parameter's name as a label" it is refused, by
  its two listed forms it is not. The census line in my brief names exactly this form, `(?<${l}>`.
- The evidence's sweep (core_details:2843, "SWEEP11: no other printed program refused by it") checks only the two
  listed forms, so this line was not reached.
- Also `C(_)` passes `_` for an UNMARKED parameter, while core/operators/bindings/label-omitted reads "At a call `_` is
  the unspecified label (`string(_:)`...)": the line leans on `n` being a label parameter in all but its mark.
- Census (all six documents): bodies placing an unmarked parameter as a label: core.md:1871 `C(n)` (this one);
  core.md:2322 `R(l, v)` and core.md:2323 `A(l)` (both printed as the compile error: correct); core_details:2838
  (rejected: correct); library_details:1097-1121 `capture(name, x) := /(?<${name}>...)/`, six hits, all in a
  RETIRED body's rejected/readings items (marked "kept as record"): fine.

### EXAMPLES-4 — the map lines named for the key's ORDER and for NO DEDUPLICATION give the same answers under the not-taken reading
CONFIRMED. Severity: doc (a witness that cannot fail). Effort: re-pick two element sets. Blast radius:
core/modules/map, core/modules/map/access. Ruling: map-creator line 4 (record l.11283): "Each string of the key is
looked up in the key's order; every result is kept, with no deduplication".
- core.md:2559 "A search, the key's order: ... (`m["b" | 1] SEQ /\w/`, m := `{a = /\d/, b = /[a-z]/}`)": the two
  elements are disjoint one-character classes, so `[a-z]|\d` and `\d|[a-z]` give the same answers. Repro (my engine,
  `work/mapw.py`): the line's printed answers re-derived with the order REVERSED (`(?:\d|[a-z])\w`): all three modes
  equal the printed ones.
- core.md:2541 "No deduplication: ... (`m SEQ "!"`, m := `{a = "x", b = "x"}`)": `x|x` and `x` give the same answers
  in every mode (repro: same file, printed answers re-derived for the deduplicated `x!`: equal).
- A witness that parts the readings: m := `{a = /\d/, b = /\d\d/}`, `m["b" | "a"]` SEARCHED `123` `12`@0, FIND-ALL
  `123` [`12`@0, `3`@2]; reversed `m["a" | "b"]` SEARCHED `1`@0, FIND-ALL [`1`@0, `2`@1, `3`@2] (my engine and the
  evidence model agree on both, `work/mine.out`, `work/model.out`). Deduplication is answer-free for a plain pattern
  (reading (i): "the same result twice in an alternation matches as once"); it is observable only through `.index`
  or a count of settings, e.g. `m.b` set never, so the line should say what it witnesses or use `.index`.

### EXAMPLES-5 — the ruled `.index` of a map element (map-creator line 7, "a constant for a label inside one alternative") has no printed line
CONFIRMED (absence). Severity: doc. Effort: one line. Blast radius: core/values/metadata, core/modules/map.
Ruling: map-creator line 7 (record l.11283): "`X.a.index` is the position, among X's alternatives, of the alternative
`a` was set in: a constant for a label inside one alternative (your 1, 1, 2), the matched member for a label over the
whole array."
- core/values/metadata (now `ruled 2026-11-25`) adds: "on a map the label is the element's (`m.b.index` is `2` where
  the alternative b matched)". Its only printed program is the matched-member case (core.md:1694, `days.w.index`).
- grep of every printed line (WHOLE / modes:) in core, library, parked for `.index`: 1 hit, that one. No line runs
  `m.b.index` or the constant `X.a.index` of his 1, 1, 2 example, the half of line 7 the ruling ADDED.
- Suggested line: `m & (m.b.index: 2)`, m := `{a = /\d/, b = /[a-z]/}`: WHOLE `x` HOLDS, `7` FAILS (b unset: the
  open edge, so mark it) ... or `F & (F.c.index: 2)` on his `F := [a=99]seq [b=76]|[c=87]`.

### EXAMPLES-6 — `peek` is an OPEN question, yet its four printed programs and lib/convention/argument-labels' examples are printed as legal, unmarked
CONFIRMED. Severity: doc (an open candidate printed as ruled). Effort: mark the lines "under (a)". Blast radius:
lib/control/peek, lib/convention/argument-labels, core/modules default-imported set. Ruling: bang-split line 5
(l.11963) makes `^A` the lookahead; the record's reading there: "`!peek(A)`'s error is gone with `peek` re-spelled
`^A`"; whether the name stays is the fold's own open question peek-name.
- library.md:332-333 "### peek ... open peek-name 2026-11-27 / Does the library keep `peek(A)` as a name for the
  lookahead `^A` ... or is `^A` the one spelling?"; Candidates (a) keep, (b) drop.
- Printed as legal with answers, depending on (a): library.md:345 `peek(/(?<d>\d)/) SEQ /\d\d/`, :346 `peek(A) SEQ
  /\d/ & (A.d: <5)`, :347 `peek(/(?<d>\d)/) SEQ /\d\d/ & (peek.d: <5)` (all three unmarked); :344 "Its not" (marked
  "the manager's reading" in the bullet above it). library.md:25 (lib/convention/argument-labels, a ruled piece)
  teaches the export rule with `peek.d` and `[c = peek(..)]`, `c.d`. Under (b) every one is a compile error (no name).
- The piece also still says `default: yes` and `defined: language` while asking whether it exists.
- My answers for the four lines (independent engine) equal the printed ones, so only the status is wrong, not the
  answers.

### EXAMPLES-7 — "the six escapes" counts seven escape sequences
CONFIRMED. Severity: doc (nit). Effort: one word, three sites. Blast radius: core/patterns/strings, the error index,
the spellings table. Ruling: string-literals line 3 (record l.11380): "The escapes are the backslash, the two quotes,
`\n`, `\r`, `\t` and `\x{..}`."
- core.md:272 "only the six escapes"; core.md:2725 "a string escape not among the six"; core.md:2828 "the six
  escapes". The ruled list is `\\`, `\"`, `\'`, `\n`, `\r`, `\t`, `\x{..}`: seven sequences (six only if "the two
  quotes" count as one). The evidence model's `_unstring` accepts all seven.
- Not stated either: whether the quote that does NOT delimit may be escaped (`"\'"`), and no printed line runs any
  escape but `\x{41}` (`\n`, `\t`, an escaped quote have no line; the evidence's STRINGS covers `\n` by plant q8 only).

### EXAMPLES-8 — "The negated test is `~contains(x)`": after bang-split a test is negated with `!`
CONFIRMED. Severity: doc (nit; a trap the new vocabulary set). Effort: one bullet. Blast radius: lib/search/contains.
Ruling: bang-split lines 1, 2, 4 (l.11963): "`!X` is the logical not of a test"; "`~X` is the complement of a set or a
pattern"; "`!` on a set or pattern is an error naming `~`".
- library.md:506 "- The negated test is `~contains(x)`." `contains(x)` is a pattern (a filter), so `~` is right, but
  the bullet calls it a test, the word bang-split reserves for `!`'s operand; a reader following "test" writes
  `!contains(x)`, the compile error. Say "the complement (the value not holding x)".

### EXAMPLES-9 — details `readings:` items still state CURRENT facts in the retired spellings
CONFIRMED. Severity: maintenance. Effort: a marker ("as run, old spelling") per item, or a twin item. Blast radius:
core_details, library_details. Ruling: drop-not (l.10831), array-argument (l.10989), bang-split (l.11963).
- Census of code spans in `readings:` (details only; history/rejected excluded, they are records): `NOT` 33,
  a condition as a group question's argument 24, `peek(` 11, `!` on a set or pattern 13 (e.g. `(h = "x": !<5)`
  core_details:1617, `((0: !contains("7")) ...)` :1703, `any_case(/[abAB]{2}/ & !/ab/)` library_details:309).
- Most are quotes of runs made under the old spelling (acceptable as records), but several are the piece's standing
  reading of today's rule, with no new-spelling twin: library_details:811-812 (lib/counting/count:
  `(count((d: "7")): ==2)`, `count(NOT (d: "7"))`), :837-838 (lib/counting/occurs: `NOT some(c)` = `occurs.none(c)`,
  `occurs.none(NOT c)` "every setting meets c"), core_details:1849/1872 (`NOT peek(test)` as the guard), :1871
  ("under `NOT` or `!`"). lib/counting/count also has no readings item for the new ruled `count(@d)` or its printed
  line "Every setting counted" (library.md:628).

### EXAMPLES-10 — a gate beside a WRITTEN label inside the binding (`[n = ([m = P] SEQ Q)] & (n.d: <5)`): no printed line, and the readings part on the answers
SUSPECTED (a gap; the model picks one reading silently). Severity: design (answers). Effort: one reading + two lines
(or a question to the owner). Blast radius: core/labels/rule/alone-as-middle, core/labels/rule/paths rule 4.
Ruling: alone-as-middle (record l.12131), as re-asked: "a part used alone ... is never skipped (`n.d` through it is a
compile error naming `n.Q.d`)"; "A label someone wrote, like `[a = P]`, is still skippable by rule 4".
- The ruled cases are pure: `[n = (P SEQ Q)]` (refused, core.md:549) and written labels only (skippable). The mixed
  case, one written label and one gate under n, has no printed line inside the binding (grep `[m = P] SEQ Q)`: one
  hit, core.md:936, which is the FROM-OUTSIDE read `X.n.d`, where rule 6 makes Q a wall).
- Two readings, different answers: (i) a gate's targets are not candidates for `n.d` (skip-past-wall's "a legal path
  reaches"), so `n.d` is m's d; (ii) `n.d` has a route through the gate, so it is the compile error naming `n.Q.d`.
  And (iii), rule 4 as worded before the gate, gave the last mention (Q's d) - the owner's own worry "n.d where does
  the d come from?" (record l.12108) is exactly this program.
- Repro: the evidence model (`work/drv.py`, `work/p3.json`) answers (i) silently: `[n = ([m = P] SEQ Q)] & (n.d: <5)`,
  P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`: WHOLE `3,7` HOLDS, `7,3` FAILS / SEARCHED `7,3 3,7` `3,7`@4 / FIND-ALL `3,7 7,3
  4,1` [`3,7`@0, `4,1`@8] (m's FIRST digit); `[n = (P SEQ [m = Q])]` likewise legal, m's d; while `[n = (P | Q)] &
  (n.d: <5)` is refused with the gate message. Nothing in the documents states (i).

### EXAMPLES-11 — a label set only inside `!^A`, read after it: no line says whether it is a compile error or an unset label
SUSPECTED (gap). Severity: doc. Effort: one line. Blast radius: core/patterns/lookaround/ahead. Ruling: bang-split
line 5 (l.11963).
- core/patterns/lookaround/ahead: "`^A` passes A's labels on, as a lookahead's labels are visible
  (core/patterns/lookaround); `!^A` passes none." The line "Its labels" prints the `^A` half; nothing prints
  `!^/(?<d>\d)/ SEQ /\w/ & (d: <5)`. By core/labels/paths ("A path to a label NOT VISIBLE through its source is a
  compile error") it should be the compile error; by core/labels/one-rule it may instead be the never-pass warning
  on an unset label. The evidence model refuses it with "unsupported group" (`work/p3.json`), a crash-class refusal,
  not a ruled message, so the reading is untested.

## PROBED-AND-HELD

Method: an independent backtracking engine (`work/eng.py`) over python `re`'s own parse tree, written from the
documents' definitions before the model was read: labels reset on entering a loop or an alternation and per pass (a
read before its group in a pass sees the previous pass, core/conditions/pass-start-read), the array = every setting
in path order, conditions as zero-width hooks; modes WHOLE / SEARCHED / FIND-ALL with PCRE's /g empty-match rule.
Each printed line's answers were parsed from the document text itself (`work/cases1-4.py`), then the model was read
and run on extra drills (`work/drv.py` imports it up to its first check) and diffed.
- (a) ANSWERS, 95 printed lines re-derived, every one equal to the print (one mismatch was my own mistranslation of
  "The label set beside `|`", where the label set binds tighter than `|`; re-read, the print is right):
  - group-truth's 3 lines; strings 4; braces 5 (range, lazy, exact, no maximum, no minimum incl. the 10 FIND-ALL
    hits with the empty ones at 1, 10, 14); lookahead operator 3 (Ahead, Not ahead, Its labels); family 2 (Ahead,
    Kinds); negation 4 (Not ahead, A condition, A group question, Twice); complement 4 (pattern difference, present
    and outside, absent or outside, its not); the two-valued table, 6 cells by hand.
  - labels: alone-as-middle 2 legal lines; skip-past-wall 3; sent-label-wall 1; equivalence-inside 1; the 3
    re-spelled `[ab = ([b = B] | [a = A])]` lines (alternation, atomic, precedence).
  - array-vs-passes 12 (two in a pass, outside the loop x2, two arrays, optional m, same item on the item, `&`
    operand, empty array, count of zero, lookahead in a pass, past the end, read inside, two depths) + binding-prefix
    2 + value-left 2 + optional-entry 4 + defaults 1 + pass-start-read/bare-condition 5 + match-so-far in-loop 3 +
    label-variables 4 + map 6.
  - library: peek 4, when 1 (`when(^/\d/, ..)` = `(?=\d)\d\d|(?!(?=\d))\w`, the ruled body laid out), when-test 2
    (bare test; `when(!^/x/, /\w/)` = `(?!x)\w|(?!(?!x))`, incl. the empty hit at 0), some 1, count 2 (incl. `count(@d)`
    "Every setting counted"), occurs 2 (exactly, none), every 6 (incl. "true when there are no settings": `,` and `x`
    HOLD), rx.repeat `some(@r.a, "7")` 1.
- Drills, my engine against the evidence model (20 programs, 3 modes each; 18 run by both, all identical; 2 the
  model refuses, reported in EXAMPLES-2 and noted below): edge cases in SECOND place (`/a;/ SEQ ..& every`, `/a/ SEQ
  !^A`, `/a/ SEQ ^A & (d: <5)`, `/a/ SEQ rx.digit{2}`, `"z" SEQ m`), at `min >= 2` (`{2,}` with `some(@d, ~"7")`,
  `{2,3}` with `occurs.exactly(1, ..)`, `rx.digit{2,}?` between literals), an OPTIONAL label in a loop (`!(h: <5)` and
  `(h ?: ~<5)` over `/(?:(?<h>\d)?;)+/`), a NULLABLE loop body (`/(?:(?<d>\d)?)*x/ & every`, `/(?:(?<d>\d)?;?)+x/ &
  (count(@d): ==1)`: the kept final empty iteration adds no setting in both), braces on a sequence and on a string
  (`("a" SEQ rx.digit){2}` = `(?:a\d){2}`, `"ab"{2}` = `(?:ab){2}`), a possessive count. Model refusal not counted
  as a finding: `(^/(?<d>\d)/ SEQ /\d/)+? SEQ /x/` ("an undeclared name"; a front-end limit; my answers: WHOLE `3x`
  HOLDS, `13x` HOLDS, `31x` FAILS).
- `every` vs the item form: 0/0/0 of 5,461 texts (lengths 0..6, `17,x`) with the label required, `*` and `+`;
  parting only with the label optional (EXAMPLES-1).
- (b) LEGALITY CENSUS over all six documents, code spans, by form (main = core/library/parked; details split into
  readings vs history/rejected):
  - `NOT`: main 0; details 119 (78 history, 5 rejected, 33 readings, 2 evidence, 1 rulings): the readings ones in
    EXAMPLES-9.
  - `!` on a set or pattern: main 2, both printed as the compile error (core.md:1527 `!/7\d*/`, library.md:408
    `when(!/x/, /\w/)`), plus core.md:1528 `(h: !(<5 | >8))` (error) — 0 illegal; the other 37 `!pat` hits are the
    string `"!"` in `SEQ "!"` (false positives, read). `!"7"` as a set: 0 anywhere in main. details 31 (EXAMPLES-9).
  - `~` on a test: main 1, the error example core.md:1489. 0 illegal.
  - `:!`, `?:!`, `&!`: main 3/1/5, all either the "There is no ..." sentence (core.md:1514), the error example
    core.md:1528, or `& !c` / `& !some` / `& !!` (a not of a test after `&`, legal). 8 more `& !(cond)`: legal. 0 illegal.
  - `peek(` / `peeknot(`: main 9 / 0 (EXAMPLES-6); details 33 / 1 (history, rejected, readings).
  - a group question with a condition argument: main 4, all compile-error lines (core.md:1253 x2, :1289, :1328); details
    54 (EXAMPLES-9 for readings). 0 illegal in main.
  - a path skipping a part used alone inside its binding: main 1, the refused line core.md:549; the 3 re-spelled lines
    now skip written labels; core.md:936 is from outside (rule 6). 0 illegal; the mixed case is EXAMPLES-10.
  - an unmarked parameter placed as a label: EXAMPLES-3 (1 doubtful, core.md:1871).
  - `x{}` / `x{,}`: main 10 hits: core.md:354, :363, :2724 shown as errors; :1790 `${}`, :2252 `${ }` (holes, not
    counts); :1849-1850 PCRE's own `a{,}` in rx text (described as libpcre2's reading). 0 illegal.
  - adjacent strings: main 2: core.md:273 (the error line), library.md:265 (a SUBJECT `"a" "b" "ax"`, not a program).
    0 illegal.
- Family table rows each have a printed witness (`!c`, `!some`, `^A`, `!^A`, `(h: ~S)`, `A & ~B`, the two error rows),
  all re-derived equal; group-truth's three statements hold by definition per path.
CRITIC COMPLETE
