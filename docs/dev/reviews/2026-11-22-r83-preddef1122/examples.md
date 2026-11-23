# CRITIC EXAMPLES — r83 preddef1122

## Findings


### EXAMPLES-1 — two-sources' line "(a) ... an argument written in place" awaits argument-default and is not marked
CONFIRMED (text + model run). Severity: answer (a printed line's legality depends on an open question it does not
name). Effort: small (mark the line, widen the bullet). Blast radius: core/labels/paths/two-sources, its default-export
bullet, argument-default's list of awaiting lines. Tag: core/labels/paths/two-sources, core.md:728.
- The line, core.md:728: "(a) the label as it reaches the caller, an argument written in place: WHOLE `7-3` HOLDS ...
  (`B(/(?<d>\d)/) & (d: <5)`, B(rx) := `/${rx}-(?<d>\d)/`)" — no "(awaits argument-default)".
- argument-default's question, core.md:691: "Where a macro's body uses an argument alone, is the caller's read of that
  argument's labels (`A.d` in `B(A)`, a group written in place) its own local read, legal, or a compile error?" The
  bare `d` at core.md:728 is (one source of) exactly that read: a group written in place, used alone by B's body.
- label-reference, core.md:608: "a bare name is a label the definition itself writes." The default-export bullet of
  two-sources, core.md:725-727: "the first shape's in-place `d` is a source only if argument-default makes it visible
  to the caller (...; under its candidate "error" the line (b) in place is a compile error)".
- Derivation under (error): the in-place `d` is no visible label; the only `d` left is the call's export, the body's
  own group, which the caller does not write; a bare read of it is label-reference's compile error ("Bare: modes: a
  compile error", core.md:626, same shape). So under (error) core.md:728 is a compile error, under (local) the printed
  answers: it awaits argument-default exactly as (b) in place does.
- The model resolves it the other way, by the homonym only (driver R/examples/py/t2.py on preddef_model.py's engine):
  `B(/(?<d>\d)/) & (d: <5)` under (error): ACCEPTED, `7-3` HOLDS (the body's d read bare); `B(/(?<e>\d)/) & (d: <5)`:
  "COMPILE ERROR: label `d` is not written in this definition: reference it with its source" under both. So an
  INVISIBLE group's name is what licenses the bare read of a label the caller does not write — which is why UNMARKED
  ("moved under (error): none") passes this line. Either the line is marked (and argument-default's list at
  core.md:701-704 gains "two-sources' (a) in place"), or the documents state that a group invisible under (error)
  still makes its name "a label the definition itself writes" (a reading nobody has made).
- Min witness length: the printed texts (3 characters) suffice; the difference is compile-time.

### EXAMPLES-2 — the changed reading "labelled (`[ab = A & B]`) `ab.h` is still ambiguous" is contradicted by the newest model; his "B.a is always an error" fails for an in-place chain
CONFIRMED (model run against the text). Severity: answer (a stated compile error the evidence engine compiles and
answers). Effort: small-medium (a refusal in the engine plus one printed refusal line, or the reading withdrawn).
Blast radius: core/labels/flow, core/labels/export/flat-read-outside, the export error table. Tag: core.md:415-416.
- core.md:415-416 (changed in this revision): "A chain `A & B` whose sides both surface h is read ambiguously where it
  is written; used alone in another binding it exports neither side's h, and labelled (`[ab = A & B]`) `ab.h` is
  still ambiguous (readings)." flat-read-outside, core.md:469: "Outside a binding a label it exports is read through
  the binding's name (`pair.x`), by name, under the inside rules". Inside, core.md:425-426: "the plain read
  `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h: <2)` is a compile error".
- Derived from the text: (i) `[ab = A & B] & (ab.h: "1")` (A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`): a compile error
  (the bullet). (ii) `P & (P.h: "1")`, P := `/(?<h>\d)\d/ & /\d(?<h>\d)/`: P's own text writes both groups, so P
  exports `h` (statement 3, core.md:436-437); read "under the inside rules" it is the `&` ambiguity: a compile error.
- The newest model (driver R/examples/py/t4.py, preddef_model.py's engine, argument-default (local)): (i) ACCEPTED,
  WHOLE `12` FAILS, `21` HOLDS, `11` HOLDS, `22` FAILS / SEARCHED `22 21` `21`@3 / FIND-ALL `12 22 21` [`21`@6] — it
  reads B's side (the textually later one); (ii) ACCEPTED, the same answers; `[ab = /(?<h>\d)\d/ & /\d(?<h>\d)/] &
  (ab.h: "1")` likewise; the in-place `.. & (h: "1")` IS refused ("both sides of `&` surface it, an ambiguous
  reference"). The old engine (predfix82, t5.py) accepts (i) and (ii) too: pre-existing in the engine, but this
  revision restates the reading in a changed line with no run and its evidence contradicts it.
- His example of the day (record "2026-11-22 OWNER, discussing the analogy": "here B.a is always an error") is
  printed only for `B := A & A` (core.md:487), where default-export refuses it as NOT VISIBLE. With the two `a`
  groups written in B's own text the not-visible ground is gone and only the ambiguity ground is left, which the
  evidence does not enforce: the "always" is unwitnessed. A printed refusal line for (ii) (and the engine's refusal)
  would close it; the error table row at core.md:1855 names only the not-visible case.
- Min witness length 2 (`12`, `21`): the answers above separate A's side from B's.

### EXAMPLES-3 — "used alone" is not defined for a binding under a part label over a composition; three printed programs' legality rests on the model's header, not the text
CONFIRMED (text). Severity: design (legality of printed lines decided by an unstated rule). Effort: small (one
sentence in statement 2 or 3). Blast radius: core/labels/export, core/patterns/alternation's line, the re-spelled
atomic line, the flow bullet. Tag: core/labels/export statements 2-3; core.md:248, 277, 415-416.
- The rule text: core.md:428 "a part used alone is seen inside it and not exported"; core.md:434 "a part USED ALONE
  (no part label)"; core.md:436-438 "the public labels its own text writes (a group in its literals, a part label)
  and, through a public part label, the labels that part exports ... A part used alone exports none of its labels".
- The programs: core.md:248 `[ab = B | A] & (ab.l: <20)`; core.md:277 (re-spelled by this revision) `atomic([ab = B
  | A]) & (ab.l: <20)`; core.md:415-416 `[ab = A & B]`, `ab.h`. In each the part under `ab` is a COMPOSITION in which
  B and A carry no part label of their own: by the words "(no part label)" each is used alone, so the part `B | A`
  writes no label and exports none, and `ab.l` is "a label only a part used alone holds": a compile error (row
  core.md:1855). The documents print them as legal answers instead (core.md:248 HOLDS lines; core.md:277 under (local)).
- What makes them legal is stated only in the evidence: preddef_model.py header, PROTECT: "A part label `[x = ..]`
  (and everything written under it) is NOT a use alone". The manager's reading (a) (record "2026-11-22 OWNER RULING —
  default-export: protected") lists "a sequence operand, in a hole or as an `&` operand without a part label": an
  alternation operand is not in the list, and "without a part label" does not say whether an ENCLOSING one counts.
- Run: the model accepts `[ab = B | A] & (ab.l: <20)` and `P & (P.ab.l: <20)`, P := `[ab = B | A]` (t3.py), as its
  header says. The fix is one sentence in statement 2 or 3 (e.g. "a part written under a part label, however deep,
  is not used alone; the label passes what it holds") marked a reading — and the four-row table's "`A` alone" row
  then needs the same qualifier. Without it, a reader applying statement 3 refuses the alternation piece's own line.

### EXAMPLES-4 — two library examples await argument-default and are neither marked nor listed: when's "Labels the test sets are visible in then", occurrences' re-split example
CONFIRMED (model run under both candidates; text). Severity: doc/answer (examples whose legality flips under one
candidate, outside the list at core.md:701-704). Effort: small (two marks, two list entries; or one sentence in
argument-default scoping candidate (error) to reads that leave the argument). Blast radius: lib/control/when,
lib/search/occurrences, core/labels/paths/argument-default's list. Tag: library.md:267, library.md:319.
- argument-default, core.md:691: "is the caller's read of that argument's labels (`A.d` in `B(A)`, a group written in
  place) its own local read, legal, or a compile error?"; its list, core.md:701-704: "The lines that await it ...
  and in the library peek, hits, endsWith, list_of, rx.repeat's labelled item and occurrences' argument group."
- when, library.md:257: `when(test, then, else = //) := (test SEQ then) | (NOT peek(test) SEQ else)` — the body uses
  `test` and `then` alone. library.md:267: "Labels the test sets are visible in then; in the else branch they are
  unset, a failed test setting nothing (a reading, run)." A condition in `then` reading a group of `test` is the
  caller's read (both are the caller's text, the condition resolved where written: core/holes/bare-condition
  "Passing the condition") of a group written in place in an argument the body uses alone: argument-default.
  Witness with when's own shape (`test SEQ then`), driver R/examples/py/t3.py: `W(/(?<h>\d)/, (h: <5))`, W(t, c) :=
  `/${t}${c}/`: under (local) WHOLE `3` HOLDS, `12` FAILS; under (error) "COMPILE ERROR: `h`: no group visible here sets
  it". (The model has no `when`; `when(...)` itself is "an undeclared name" there.)
- occurrences, library.md:319: "The hits are re-split whenever a condition rejects: `occurrences(/(?<n>\d+)/ & (n:
  <100))` on `1234` HOLDS with the hits `12`, `34`." The read `n` is written inside the argument with its group.
  Under the model's (error) (t6.py): "COMPILE ERROR: `n`: no group visible here sets it"; under (local) `1234` HOLDS.
  Likewise `B(/(?<d>\d)/ & (d: <5))`, B(rx) := `/${rx}xx/`: (local) `3xx` HOLDS, `7xx` FAILS; (error) refused.
- Two ways out, and the documents take neither: (1) mark both and list them; or (2) state that a read written INSIDE
  the argument beside its group is not "the caller's read through the call" (candidate (error)'s own words at
  core.md:698-699: "no label of it is visible through the call") and fix the model's (error), which today refuses
  it. As printed, the occurrences sentence is a rule example ("whenever a condition rejects") that the evidence's
  (error) candidate refuses, and UNMARKED never saw it (it is prose, not a three-mode line).
- Min witness length 1 (`3`/`3xx`): the difference is compile-time.

### EXAMPLES-5 — the ruled examples through the changed error table: export-list's own error has no row; the new row names only "used alone" while statement 3's sentence also covers `_` part labels and `[_ = A]`
CONFIRMED (text). Severity: doc (nit; the table declares itself PARTIAL). Effort: trivial (one row widened, one
added). Blast radius: core/diagnostics/errors. Tag: core.md:1855.
- Each refusal printed or stated by this revision, run through the table (core.md:1848-1875):
  `p2.h` (p2 := `/${A}!/`, and `A SEQ "!"`) — the new row; `B.a` and `some((B.a: "9"))`, B := `A & A` — the new row;
  `X.D.h`, X := `D SEQ "!"` — the new row and "a path to a label not visible through its source" both fit;
  `B.d`/`c.d`, B(rx) := `/${rx}xx/` — the new row; `date.month` under `(=year)` and `date.isodate.month` — "a path to
  a label not visible through its source"; `p6.h` under `[_a = A]` (core.md:465) — NO row names it: the new row says
  "a label only a part used alone holds", while statement 3 (core.md:439-440) makes the same compile error for "a
  part under a `_` part label or `[_ = A]` ... a read from outside of a label only such a part holds";
  `[(=hour) = isodate]` — "a compile error at the list" (core.md:537-538, "Only an EXPORTED label of the part can be
  listed; a `_` label or one the part keeps protected is a compile error at the list (a reading, run ...)") — NO row.
- The atomic old program `[ab = atomic(B | A)] & (ab.l: <20)` (now refused, core_details.md:434) — the new row fits.
- Fix: widen the new row to "... only a part used alone, under a `_` part label or under `[_ = A]` holds" and add "a
  label listed on a part label that the part does not export (`[(=hour) = isodate]`) | core/labels/export/export-list".

### EXAMPLES-6 — statement 2's "a part USED ALONE is reached by its own name" reaches a macro parameter too; the printed reading `d.year` (a parameter's label read in the body) is illegal under core.md:654 and the model
CONFIRMED (text + model). Severity: design/doc (a rule sentence wider than its evidence; one printed fragment that
reads a label the documents call not nameable). Effort: small. Blast radius: core/labels/export statement 2,
core/operators/bindings/macro-types (the `d.year` reading), the four-row table's "`A` alone" row. Tag: core.md:434,
core.md:1681-1685.
- core.md:433-434 (changed): "a part USED ALONE (no part label) is reached by its own name, `A.h`, as under `[_A =
  A]`". Nothing restricts "part" to a bound name or macro call; inside `B(rx) := /${rx}xx/` the parameter rx is a part
  used alone in a hole, so the sentence licenses `rx.d` in the body.
- Against it, core.md:654: "a parameter's label inside the body is not nameable (core/holes/bare-condition/
  nested-scope)"; his example 1: "C cannot see rx as its a binding variable not a label" (core.md:1529-1530).
- The model sides with core.md:654 (t9.py): `B(A)`, B(rx) := `/${rx}xx/ & (rx.d: <100)`, A := `[d = rx.digits]`:
  "COMPILE ERROR: at the binding ...: B names a label it does not hold: rx.d", under both argument-default candidates.
- A printed program that reads exactly that: core.md:1684-1685, macro-types: "under that ruling the body would name
  it through the parameter, `d.year` (a reading; not asked)" for `B(d) := d & isodate & (isodate.year: < 2100)` — d
  is the parameter, used alone in the body. Illegal by core.md:654 and the model; legal by statement 2's new words.
  Pre-existing fragment, but the revision's statement 2 now reads it as legal, so the contradiction is new in kind.
- Fix: statement 2 "a bound name or a macro call used alone" (the model's PROTECT wording: "a bound name or a pattern
  macro's call written as a sequence operand, in a hole or as an `&` operand"), and the `d.year` fragment re-read or
  marked against core.md:654.

### EXAMPLES-7 — month_numbered still says "The label `mname` is visible in the result"; under default-export no caller can read it (its sibling `length` was corrected, this one was not)
CONFIRMED (text + model). Severity: doc (a claim about what a caller reads, wrong under the ruling). Effort: trivial.
Blast radius: lib/modifiers/month-numbered. Tag: library.md:234. (Overlaps FIXIND's sweep; recorded here because it
is a claim about a printed program's labels: the line library.md:236 `month_numbered(between(1, 6))`.)
- library.md:225: "`month_numbered(S) := months & (months.mname.index: S)`" — the body uses `months` alone.
  library.md:234: "The label `mname` is visible in the result; `[mname = ...]` makes no capture (pure-label)."
- The rule: core.md:629 "A macro's name qualifies the labels its call exports, those its body's text writes";
  core.md:438 "A part used alone exports none of its labels". The body's text writes no `mname` (it is months's), so
  the call exports none: the very derivation this revision applied to `length` at library.md:217-220 ("The body uses
  `chars` alone, so a call exports no `ch`: `length.ch` and `length.chars.ch` are compile errors").
- Model (t10.py, months shortened to seven names, MN(S) := `months & (months.mname.index: S)`): `MN(>= 6)` WHOLE `Jun`
  HOLDS, `Jul` HOLDS, `Feb` FAILS; `MN(>= 6) & (MN.mname: /Jun/)`, `(MN.months.mname: ..)` and `[m = MN(>= 6)] &
  (m.mname: ..)`: each "COMPILE ERROR: ... is not visible through ...". "Visible in the result" holds only inside the
  body; the sentence should say so as length's does.

## PROBED-AND-HELD

- The newest model run clean from R/tree: "preddef_model: 22 checks, 0 failed" (R/examples/model_run.out).
- Sub-part 1, re-derived BY HAND from the rule text (one-rule, flow, export statements 2-3, call-prefix, the list),
  every mode, then diffed against the model through R/examples/py/drv.py (the engine loaded up to "the checks"),
  under both argument-default candidates: 26 changed printed lines (core.md 277, 463, 464, 465, 487, 488, 489, 518,
  541, 542, 543, 601, 602, 661, 662, 664, 666, 686, 708, 709, 710, 729, 1541; library.md 254, 367, 400, 616 by their
  mark) — every printed answer, every SEARCHED offset and every FIND-ALL list agrees with the hand derivation (the
  canonical-numeral rule on `042xx` and `00xx`, the atomic commit on `25`, the greedy `(\d)+` in D, positions in the
  multi-word texts); (local) reproduces each awaiting line, (error) refuses each one that reads the argument.
- Capture-state drill (an optional label in a loop; the edge case in SECOND place at min >= 2), t8.py, 7 programs,
  19 texts: through a part label (`X.d.h`), a binding used alone (`A.h` in p2), a prefix (`D.h`) and the `&` of two
  labelled uses (`B.x.a`), the one-rule reset on a later pass holds (`1x;4xx!` FAILS, `x4x!` HOLDS, `44x!` FAILS,
  `4xx!` with `anything` FAILS: h unset), identically to the rule text. Held.
- Domain drill (one set, two spellings), t7.py, 14 programs: `(B.x.a: 9)` = `"9"` = `/9/`; `(date.year: >= 2000)` =
  `/[2-9]\d{3}/` incl. `0999`; `(date.day: "02")` vs `(date.day: 2)`: the number FAILS on `02` (not a canonical
  numeral) as the rule says, so the printed string spelling is the right one. Held.
- export-list beyond the printed: several (`(=year, =day)`, the form its readings mark UNTESTED) reads `year` and
  `day` and refuses `month`; a listed name the binding also writes is one label, the last mention (reading (d),
  marked UNTESTED: run here, holds); the list gives no local `isodate.year` either (consistent with the table row's
  local name `year`). Held.
- Sub-part 2, legality over the WHOLE of core.md and library.md: 72 printed lines with a dotted read and 133 prose
  snippets with a path (R/examples/dotted_lines.txt, prose_paths.txt) checked against export statement 3 (core.md:
  436-441), label-reference (core.md:608), call-prefix (core.md:629) and the list (core.md:522): no program written
  before the reversal reads, unmarked, a label that only a part used alone holds, apart from EXAMPLES-1, -4, -6, -7.
  The model's SCAN (17 reads) covers only bindings defined on the line; library helpers (months, chars, hits,
  occurrences, capture) were checked by hand: hits/occurrences/capture bodies write their labels (exported); length
  and month_numbered use theirs alone (EXAMPLES-7 for the latter).
- The holes/labels pass-on (`/${[y = year]}-x/`, `Q.y.v`, also `Q.v` by name) and `[=A]` as `[A = A]` (`pub.A.h`)
  run legal; `Q.year.v` for `/${year}-x/` refused, as statement 3 says. Held.
- Minimum witness length reached: 1 character (compile-time differences) to 14 (`2025-01-021999`); every 0-diff above
  is over the printed texts or longer.

CRITIC COMPLETE
