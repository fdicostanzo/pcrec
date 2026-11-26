# CRITIC NAMEGRID: r90 predfold1124

## Findings

### NAMEGRID-1 UNDECIDED: a skip inside a binding where one route to the target crosses an underscore label (sequence, `&`, `|`)
CONFIRMED (the engine answers; no sentence decides; two readings of rule 4 give different answers). Severity: answer
(+ design). Effort: one sentence in [core/labels/rule/paths] (does rule 4's "unambiguously referenced from a" judge
among ALL `c`s under `a`, or only among those a LEGAL path reaches?) and three printed lines. Blast radius: every
skip `n.d` under a label whose expression mixes a public part with a `_x`/`_`/`_p` part that also sets `d`.
Where: core.md [core/labels/rule/paths] rule 4 + the manager's reading (b) ("across `&` a name both sides set is
ambiguous; in a sequence the last mention wins; across `|` the branch taken"); [core/labels/export/flat-read-outside]
"A read from OUTSIDE sees the binding's EXPORTED settings only ... (a reading, the manager's)" -- an OUTSIDE reading,
2026-11-22, before path-rules; nothing carries it inside.
- Sequence, private LAST: `[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`.
  probe: LEGAL WHOLE `3,7` HOLDS, `7,3` FAILS / SEARCHED `7,3 3,7` `3,7`@4 / FIND-ALL `3,7 7,3 4,1` [`3,7`@0, `4,1`@8]
  (m's d). Reading (b) read literally ("the last mention wins") names Q's d, whose only path crosses `_x` (rule 2):
  a compile error; or, if the last mention is taken anyway, python `re` (namegrid/remodel.py) gives WHOLE `3,7`
  FAILS, `7,3` HOLDS / SEARCHED `7,3`@0 / FIND-ALL [`7,3`@4, `4,1`@8]. `[_ = Q]` in its place: the same (probe LEGAL, m's d).
- `&`: `[n = ([m = P] & [_x = Q])] & (n.d: <5)`, P := `/(?<d>\d)\d/`, Q := `/\d(?<d>\d)/`. probe: LEGAL WHOLE `37`
  HOLDS, `73` FAILS / SEARCHED `73 37` `37`@3 / FIND-ALL `37 73 14` [`37`@0, `14`@6]. Reading (b) as worded, "a name
  both sides SET is ambiguous": Q sets d, so a compile error; and core/labels/flow "a part SURFACES a name where the
  name is visible in the definition, its protected labels included" -- `_x.d` is visible in this definition, so both
  sides surface d: the ambiguous reference. With `[k = Q]` the probe does refuse (ambiguous), so the engine's legal
  answer rests only on filtering the `_x` route first, a rule no sentence states for an inside read.
- `|`: `[n = ([m = P] | [_x = Q])] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/a(?<d>\d)/`. probe: LEGAL WHOLE `3` HOLDS,
  `a3` FAILS, `a7` FAILS / SEARCHED `a7 a3` `3`@4 / FIND-ALL `3 a7 a4` [`3`@0, `4`@6] (n.d unset when the `_x` branch
  is taken). "Across `|` the branch taken" gives `a3` HOLDS / SEARCHED `a3`@3 / FIND-ALL [`3`@0, `a4`@5] (remodel.py)
  if the read is allowed through the taken branch, or a compile error (rule 2) if a branch whose only path crosses
  `_x` makes the reference illegal. Three candidate answers; the engine's is a third rule (unset), stated nowhere.
- Smallest witness: two one-digit parts, texts of length 2-3; the readings differ at WHOLE already.
- Fix shape: state in [core/labels/rule/paths] whether rule 4's candidates are the targets reachable by LEGAL paths
  only (the engine; it extends the outside "exported setting only" reading inward) or every same-named label under
  the start (reading (b) as worded; then the cells above are compile errors). Print one line per operator.

### NAMEGRID-2 CONFLICT (evidence) : from OUTSIDE, a label over an expression or hole passes a part used alone in it; the documents say a compile error, the engine answers
CONFIRMED. Severity: evidence (the engine the fold's rules 5/6 runs on contradicts a decided cell) + answer (the
cell's printed decision is unrun). Effort: one engine fix (apply rule 6 / statement 3 below a part label whose
right side is an expression or a literal with a hole) + one printed line. Blast radius: every outside read
`X.n.<h>` / `X.<h>` where n labels `(..)`, `B | A`, `P SEQ Q` in parentheses, or `/${Q}../`; predecessor too (`--old`
answers alike: pre-existing in the engine, but the fold's rule 6 is its first ruled ground).
Where: core.md [core/labels/paths] "`X.ab.l` from outside X := `[ab = (B | A)] SEQ "!"` is a compile error, B and A
used alone in it"; [core/labels/export] statement 3 "A part used alone exports nothing, through a hole and the
sequence operator alike"; [core/labels/export/arguments] row "`identity((A))` ... an expression exports what its own
text writes, a part used alone in it nothing"; [core/labels/rule/paths] rule 6 "A part used alone inside a binding is
crossed from outside as an underscore label is". Deciding answer for every cell below: a compile error.
- `X & (X.ab.l: <5)`, B := `/(?<l>\d)/`, A := `/a(?<l>\d)/`, X := `[ab = (B | A)] SEQ "!"` (the documents' own example).
  probe: LEGAL WHOLE `3!` HOLDS, `a3!` HOLDS, `a7!` FAILS / SEARCHED `a7! a3!` `a3!`@4 / FIND-ALL `3! a7! a4!` [`3!`@0, `a4!`@7].
  `[ab = B | A]` (no parentheses): LEGAL too. `--old`: LEGAL.
- Through a hole: X := `[n = /${Q},/] SEQ "!"`, Q := `/(?<d>\d)/`, `X & (X.n.d: <5)`: LEGAL WHOLE `3,!` HOLDS, `7,!` FAILS /
  SEARCHED `7,! 3,!` `3,!`@4 / FIND-ALL `3,! 7,! 4,!` [`3,!`@0, `4,!`@8]; `X.d` (rule 4) the same.
- In parentheses: X := `[n = (Q)] SEQ "!"`, `X.n.d`: LEGAL (the documents' `identity((A))` reading: nothing).
- Mixed, where it changes the ANSWER, not only legality: X := `[n = ([m = P] SEQ Q)] SEQ "!"`, P := `/(?<d>\d)/`,
  Q := `/,(?<d>\d)/`, `X & (X.n.d: <5)`: probe LEGAL WHOLE `3,7!` FAILS, `7,3!` HOLDS / SEARCHED `7,3! 3,7!` `7,3!`@0 /
  FIND-ALL [`7,3!`@5, `4,1!`@10] -- Q's d, the part used alone, read from outside. By rule 6 + "exported setting only"
  the read is m's d: WHOLE `3,7!` HOLDS, `7,3!` FAILS / SEARCHED `3,7!`@5 / FIND-ALL [`3,7!`@0, `4,1!`@10] (python `re`,
  `(?P<m_d>\d),(?P<q_d>\d)!`, condition on m_d). `X.d` alike. `[n = ([m = P] & Q)]`: refused as the `&` ambiguity,
  where "a source it keeps protected ... makes no `&` ambiguity" says legal, m's d.
- Control that the engine CAN apply rule 6: X := `[n = Q SEQ ","] SEQ "!"` (no parentheses) refuses `X.n.d`; so the
  engine's parse of the parenthesised / `|` / hole right side is where rule 6 is lost.
- Smallest witness: one one-digit part, text length 3.

### NAMEGRID-3 UNDECIDED: inside a binding, is a part used alone under a label a node of the label DAG? the skip through it is legal, the full path through it refused
CONFIRMED (engine) / UNDECIDED (text). Severity: design. Effort: one sentence (rule 6's inside half: "is a start
inside its own binding" -- is it also a MIDDLE label inside?) + two printed lines. Blast radius: every inside read
under a part label over an expression holding a binding used alone.
Where: core.md [core/labels/rule/paths] rules 1, 3, 4, 6; [core/labels/export] statement 2 ("An UNLABELLED use carries
the implicit label of the binding's name, protected: reached as `A.h` there"); [core/labels/paths] "A part label over
an EXPRESSION (`[ab = (B | A)]`) reads, inside the definition, the labels visible in it by the inside rules".
- `[n = (P SEQ Q)] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`: probe LEGAL WHOLE `3,7` FAILS, `7,3` HOLDS /
  SEARCHED `7,3 3,7` `7,3`@0 / FIND-ALL [`7,3`@4, `4,1`@8] (Q's d, the last mention: python `re` agrees for that meaning).
- `[n = (P SEQ Q)] & (P.d: <5)`: LEGAL (P's implicit label a start: rule 6's inside half, statement 2).
- `[n = (P SEQ Q)] & (n.P.d: <5)` and `(n.Q.d: ..)`: REFUSED "`P.d` is not visible through `n`".
- So the engine treats the implicit label as a node a skip passes through (n.d reaches Q's d, so by rule 4 "if a
  legal path exists a.b.c" the path n.Q.d must be legal) and as no node for the spelled path. Rule 1 ("in the label
  DAG ... the starting label has at least one path to the target") with statement 2 (the implicit label IS a label)
  makes n.Q.d a path; the engine's refusal cites [core/labels/paths]'s "A path to a label NOT VISIBLE through its
  source is a compile error", which does not say what is visible. No sentence names the cell; the two readings give
  LEGAL (Q's d) vs a compile error for `n.Q.d`.
- Compare the mixed inside cell `[n = ([m = P] SEQ Q)] & (n.d: <5)`: the engine reads Q's d (`3,7` FAILS), not the
  public m's d -- the alone part is crossed inside, which agrees with rule 6 being an OUTSIDE rule, and makes the
  refusal of `n.Q.d` the odd one out.
- Smallest witness: two one-digit parts, length 3.

### NAMEGRID-4 CONFLICT: a public part label stacked UNDER an underscore label -- statement 3 exports it, rule 2 refuses every path to it
CONFIRMED (two sentences, two answers; the engine follows rule 2). Severity: doc (+ design: "exports" has two
meanings). Effort: one clause in [core/labels/export] statement 3 ("a part label it writes" -> "... that no path from
the binding's name crosses an underscore label to reach") and the one-line summary. Blast radius: every binding that
stacks `[_x = [n = ..]]`, `[_ = [t = ..]]`, `[_p = [n = ..]]`; every sentence that says "a binding exports the labels
its own text writes".
Where: core.md [core/labels/export] summary "a binding exports the labels its own text writes and those a public part
label passes" and statement 3 "its OWN names (a group in its literals, a part label it writes, a label an export list
it writes takes; none beginning with `_`)"; [core/labels/export/flat-read-outside] "Outside a binding a label it
exports is read through the binding's name"; vs [core/labels/rule/paths] rules 2 and 5; [core/labels/ownership] "A
blank or private label stacked on a spot shuts every path that crosses it, inside the binding and out".
- X := `[_x = [n = A]] SEQ "!"`, A := `/(?<h>\d)/`: `n` is a part label X's text writes, not beginning with `_`, so X
  EXPORTS n by statement 3 and `X.n.h` is "read through the binding's name" (flat-read-outside; statement 3's own
  `pub.a.h`). Rule 5 + rule 2: the path X, `_x`, n crosses `_x`: a compile error. probe: REFUSED "`X.n.h`: the path
  crosses the underscore label `_x`" (and `X.h` alike). If exported: python `re` `(?P<n_h>\d)!`, `n_h<5`: WHOLE `3!`
  HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL [`3!`@0, `4!`@6].
- X := `[_ = [t = A]] SEQ "!"`: `X.t.h` REFUSED (crosses `_`), yet `t` is a part label X writes (statement 3 exports it).
- Inside X both are legal (`n.h`, `t.h`: rule 3; probe `[_ = [t = A]] SEQ "!" & (t.h: <5)` LEGAL WHOLE `3!` HOLDS ...),
  so "a label the binding exports" (statement 3: every public name it writes) and "a label readable from outside"
  (rule 5: the names no path from its name blocks) are two sets; the documents use "exports" for both.

### NAMEGRID-5 CONFLICT (evidence): three labels stacked on one spot -- rule 1's full path and rule 4's single skips are refused by the engine; the definition decides them legal
CONFIRMED. Severity: evidence (the engine the fold's path rules are run on refuses decided-legal cells; no printed
line reaches depth 3, so nothing caught it). Effort: engine fix in the stacked-label walk + one printed line at depth 3.
Blast radius: every stack of 3+ labels on one spot and every two-binding-level path (below); the fold's PATHS checks
run depth 2 only.
Where: core.md [core/labels/rule/paths] rules 1 and 4; [core/labels/rule/stacked-chain] "`n.m.d` is the full path,
`n.d` skips `m` (rule 4), `m.d` starts at `m` (rule 3)" and "The nested form `[n = ([m = P])]`, two spots, reads the
same"; from outside "`X.n.m.h`, `X.n.h`, `X.m.h` and `X.h` (rule 4)" (so a skip may land on a middle label: `X.m.h`).
- `[n = [m = [k = P]]] SEQ "!" & (n.m.k.d: <5)`, P := `/(?<d>\d)/`: probe REFUSED "`n.k.d`: `k.d` is not visible through
  `n`" (the engine rewrote the path it was given); `--old` REFUSED too. Decided (rule 1): LEGAL; python `re`
  `(?P<d>\d)!`, d<5: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6].
  The nested form `[n = ([m = ([k = P])])]` with `n.m.k.d`: LEGAL (stacked-chain says the two forms read the same).
- Same stack: `n.k.d` (skip m, rule 4) REFUSED; `n.m.d`, `n.d`, `m.d`, `k.d`, `m.k.d` LEGAL. From outside, Z :=
  `[n = [m = [k = P]]] SEQ "!"`: `Z.n.m.k.d` and `Z.n.k.d` REFUSED; `Z.m.k.d`, `Z.m.d`, `Z.k.d`, `Z.d`, `Z.n.d` LEGAL.
- Two binding levels (a binding using a binding that uses a macro): A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`,
  Y := `[c = B(A)] SEQ "!"`, X := `[y = Y] SEQ ";"`. LEGAL: `X.y.c.p.h`, `X.y.c.h`, `X.y.h`, `X.h`. REFUSED: `X.c.p.h`
  (skips only y, as the printed `X.m.h` skips only n), `X.c.h`, `X.y.p.h`, `X.p.h`. Every refused path is a legal
  path with single middle labels skipped, each target unambiguous (one use of each), so rule 4 (as the printed `X.m.h`
  and `X.h` apply it) decides LEGAL, reading A's h: python `re` `(?P<h>\d)xx!;`, h<5: WHOLE `3xx!;` HOLDS, `7xx!;` FAILS.
- Definition gap beside it (doc): rule 4 is worded for ONE skipped label ("then b can be skipped a.c"); the documents
  apply it to two (`X.h` over `[n = [m = A]]`) and to a skip landing on a middle label (`X.m.h`) with no sentence that
  it iterates. One clause: "rule 4 applies repeatedly; any set of middle labels may be skipped".
- Smallest witness: one one-digit literal, three stacked labels, text length 2.

### NAMEGRID-6 CONFLICT: a sent label the body places ABOVE its own blank or private label -- rule 2 refuses `x.h`, reading (e) ("whatever the body stacks around them") and the engine allow it
CONFIRMED. Severity: answer (legal vs compile error) + design. Effort: one sentence: reading (e) makes the caller's
label a START; whether the body's `_`/`_x`/`_p` BELOW a sent label closes the path is rule 2's, and the reading should
say so (or the owner be asked: a sent label is the one caller label whose position in the stack the BODY's text
chooses). Blast radius: every label macro that stacks its sent label over a closed or private spot (`R(l:, v) :=
/${[l = [_ = v]]}xx/`); with it the ownership table's "sent label" row.
Where: core.md [core/labels/rule/paths] reading "a label the caller writes in an argument, a sent label and the
caller's shorthand label are starts in the CALLER's binding, whatever the body stacks around them" (the manager's
reading (e), marked); vs rule 2 "the path may not contain any underscore labels full or prefix unless the
underscore prefix label is the start" (his) and the printed "A blank label in the stack: modes: a compile error
(`[l = [_ = P]] & (l.d: <5)`)"; [core/labels/ownership] row "a sent label ... closed by the blank mark: `x` bare:
another door" (a sent label naming a GROUP, the blank above it: a different stack).
- `R(x:, A) & (x.h: <5)`, A := `/(?<h>\d)/`, R(l:, v) := `/${[l = [_ = v]]}xx/`: the path x, `_`, h has the blank as
  a middle label, not the start. Rule 2: a compile error (the same stack written in place, `[l = [_ = A]] SEQ "xx" &
  (l.h: <5)`, the probe REFUSES by rule 2). probe: LEGAL WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 /
  FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (python `re` `(?P<h>\d)xx`, h<5, agrees for the legal meaning).
  `[l = [_x = v]]` and `[l = [_p = v]]` in the body: LEGAL alike; `--old`: LEGAL.
- The caller-written analogue IS refused: `B([a = [_x = A]]) & (a.h: <5)`, B(rx) := `/${rx}xx/`: REFUSED by rule 2,
  `_x.h` LEGAL. So "the caller's label is a start" already does not mean "whatever is stacked under it": the sent
  label is the one case where the engine lets a body's wall below the caller's label be crossed.
- The shorthand label under `[_ = rx]` (ruled legal: shorthand-is-callers) is not this cell: there the body's label
  sits ON the spot and the shorthand "is on the spot where the body places the template"; the sent label's place is
  written by the body ABOVE its own wall.
- Smallest witness: one one-digit literal, text length 3.

### NAMEGRID-7 CONFLICT (evidence): a label stacked under another is no TARGET -- `n.m` refused for `[n = [m = P]]`, legal for the nested form
CONFIRMED. Severity: evidence (same walker as NAMEGRID-5, depth 2) + doc (no printed line reads a part label as the
target of a path). Effort: engine fix + one printed line. Blast radius: every read of a part label's own value
through a label above it (`date.y`, `X.n.m`), the one-spot form only.
Where: core.md [core/labels/rule/paths] rule 1 ("in the label DAG there is a target label and a starting label");
[core/labels/rule/stacked-chain] "The nested form `[n = ([m = P])]`, two spots, reads the same"; a part label read as
a value is printed (`B([f = /\d/]) & (f: <5)`, [core/labels/export/arguments]).
- `[n = [m = P]] SEQ "!" & (n.m: <5)`, P := `/\d/`: probe REFUSED "`m` is not visible through `n`"; `m` bare LEGAL;
  `[n = ([m = P] SEQ "!")] & (n.m: <5)` LEGAL WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!`
  [`3!`@0, `4!`@6]; from outside X := `[n = [m = P]] SEQ "!"`: `X.n.m` REFUSED, `X.n` and (X := `[m = P] SEQ "!"`) `X.m`
  LEGAL. Decided (rule 1, m on a path from n): LEGAL, the same answer as `m` (python `re` `(?P<m>\d)!`, m<5).
- Smallest witness: one one-digit literal, length 2.

### NAMEGRID-8 UNDECIDED: is a named group of rx text a node of the label DAG (a middle label, a start over a hole)?
CONFIRMED (engine refuses; no sentence decides). Severity: design. Effort: one sentence in [core/labels/rule/paths]
naming what the DAG's edges are (part label over part; label over a hole's content; group over group?). Blast
radius: every path through a literal's groups (`g.d` for `/(?<g>(?<d>\d))x/`) and through a group wrapping a hole.
Where: core.md [core/labels/rule/paths] rule 1 ("the label DAG"); [core/labels/paths] "a named group in pattern
text is a label and also a capture"; [core/labels/rule] line 2 ("a path is a chain of labels"); [core/principles/
label-names-spot] (a label names a spot: a group names its spot, which encloses the inner group's spot).
- `/(?<g>(?<d>\d))x/ & (g.d: <5)`: probe REFUSED "`d` is not visible through `g`"; `[n = /(?<g>(?<d>\d))x/] &
  (n.g.d: <5)` REFUSED; `n.d` (skip g?) and `d` bare legal. If groups are labels and nesting is the DAG, rule 1 makes
  `g.d` a path: python `re` `(?P<g>(?P<d>\d))x`, d<5: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL
  [`3x`@0, `4x`@6]; if not, a compile error. No sentence says which.
- Over a hole: `[n = /(?<g>${[p = A]})x/] & (n.p.h: <5)` LEGAL, `n.g.p.h` REFUSED, `/(?<g>${[p = A]})x/ & (g.h: <5)`
  REFUSED: the engine treats a group as a wall to nothing and a node of nothing, while `n.p.h` crosses its spot.

### NAMEGRID-9 CONFLICT (answer): one binding level up, a wall over a public label is lost -- `Y.c.h` legal where `X.h` is refused
CONFIRMED. Severity: answer (a compile error by the rules, a legal read with an answer in the engine) + evidence.
Effort: engine fix (carry rule 2 through a part label over a used binding) + one printed line at two binding levels;
the documents' half is NAMEGRID-4 (statement 3 "exports" every public part label the text writes, and the engine's
second level reads exactly that meaning). Blast radius: every two-level read through a binding that stacks `_`/`_x`
over a public label; the fold's printed lines stop at one level.
Where: core.md [core/labels/rule/paths] rule 5 "The path then continues into that binding's tree by rules 1, 2 and 4"
and rule 2; [core/labels/ownership] "A blank or private label stacked on a spot shuts every path that crosses it,
inside the binding and out"; [core/labels/export] statement 7 ("you can't go through A to get inside").
- A := `/(?<h>\d)/`, X := `[_x = [n = A]] SEQ "!"`, Y := `[c = X] SEQ ";"`. From outside X: `X & (X.n.h: <5)` and
  `X.h`: REFUSED (rule 2, the path crosses `_x`). From outside Y: `Y & (Y.c.h: <5)`: LEGAL WHOLE `3!;` HOLDS, `7!;` FAILS
  / SEARCHED `7!; 3!;` `3!;`@4 / FIND-ALL `3!; 7!; 4!;` [`3!;`@0, `4!;`@8]; `Y.h` and `Y.c.n.h` LEGAL too. The path Y, c,
  (X's tree:) `_x`, n, h crosses `_x`: decided a compile error by rules 5 and 2.
- X := `[_ = [t = A]] SEQ "!"`: `Y.c.h`, `Y.h` LEGAL alike (the blank, statement 7's own door, crossed).
- Controls that the engine walls a level up when nothing public sits under the wall: X := `[_ = A] SEQ "!"`,
  `[_x = A] SEQ "!"`, `A SEQ "!"`: `Y.c.h`, `Y.h` REFUSED. So the leak is exactly "a public label under the wall":
  the engine's second level counts what statement 3 says X EXPORTS (n, t) and forgets the path to it.
- If the read were legal, python `re` `(?P<h>\d)!;`, h<5, gives the engine's line; the defect is legality, not the value.
- Smallest witness: one one-digit literal, two bindings, text length 3.

### NAMEGRID-10 UNDECIDED / UNRUN: a call boundary crossed twice -- a body that passes its pattern parameter on to another macro
SUSPECTED (cells unrun: the engine refuses every one as "not modelled"; the documents print no line and name no
piece). Severity: evidence + doc. Effort: one sentence ("rule 5 applies at each call: a call inside a body is a part
of the body's tree, used alone or labelled as written") + two printed lines, and the engine's known limit lifted or
listed as a cell no check covers. Blast radius: every library macro built on another (a wrapper over `hits`,
`occurrences`, `atomic`).
Where: core.md [core/labels/ownership] "A body that passes its PATTERN parameter on to another macro is no column
here." (no pointer, unlike the sentence's other three cases: "their own pieces"); [core/labels/rule/paths] rules 5, 6.
- A := `/(?<h>\d)/`, C(r) := `/${[q = r]}x/`, B(rx) := `C(rx) SEQ "!"`. The general rules, iterated, give:
  `B(A) & (A.h: <5)` LEGAL (shorthand-is-callers, "whatever B's body does with the spot"; python `re` `(?P<h>\d)x!`,
  h<5: WHOLE `3x!` HOLDS, `7x!` FAILS / SEARCHED `7x! 3x!` `3x!`@4 / FIND-ALL `3x! 7x! 4x!` [`3x!`@0, `4x!`@8]);
  `B.q.h`, `B.C.q.h`, `B.h` compile errors (C(rx) used alone in B's body: rule 6); with B(rx) := `[k = C(rx)] SEQ "!"`,
  `B.k.q.h` and `B.h` LEGAL (rules 5, 4). But "the spot where the body places the template" (argument-default) is
  C's spot, placed by C, not B: whether the shorthand's spot and condition 4 ("no label has already been made on it
  there") look through B to C's `[q = r]` (or C's `[_ = r]`) is decided by no sentence.
- probe: all six programs REFUSED "not modelled (predfix88's known limits): the body of B passes its pattern parameter
  `rx` on to C (a nested body)" -- an emulator limit, not a sentence.

### NAMEGRID-11 DEFINITION COMPLETENESS: terms of the path definition with two meanings (part (b))
CONFIRMED (each pair quoted; where the meanings give different answers, the run is named). Severity: doc (design
where an answer moves). Effort: a short "terms" block in [core/labels/rule/paths] fixing each word once. Blast
radius: the whole labels chapter. Where: core.md, the pieces named per term.
1. "exports" -- [core/labels/export] statement 3: "its OWN names (a group in its literals, a part label it writes ...;
   none beginning with `_`)" (every public name) vs [core/labels/rule/paths] rules 5 + 2 (only names no wall hides).
   Answers move: NAMEGRID-4 (`X.n.h` for `[_x = [n = A]]`), NAMEGRID-9 (the engine uses meaning 1 one level up).
2. "equivalent" / "no label `t` is made" -- his "[_t = A ] is equivalent to [_ = [t = A ]]" vs the reading in
   [core/labels/rule/paths] "a wall with a start inside, not a second spelling; no label `t` is made". Run:
   `[_ = [t = A]] SEQ "!" & (t.h: <5)` LEGAL (`3!` HOLDS ...), `[_t = A] SEQ "!" & (t.h: <5)` REFUSED ("`t` is neither
   written ..."), `_t.h` legal only in the second. So "equivalent" holds for reads from outside only, and even there
   not under statement 3's "exports" (t is a public part label `[_ = [t = A]]` writes). The reading should say "the
   same from outside; inside, `[_ = [t = A]]` makes `t`, `[_t = A]` makes `_t`".
3. "crosses" vs "contains" -- the piece's summary: "crosses no underscore label unless that label is its start"; rule 2
   (his): "the path may not contain any underscore labels". At an underscore TARGET they part: `[n = /(?<_v>\d)/]
   SEQ "!" & (n._v: <5)` -- the path ends at `_v`, crosses nothing; it contains `_v`. probe REFUSED "the path crosses
   the underscore label `_v`" (rule 2's meaning, the summary's word); `_x._v` (both private, inside) REFUSED alike;
   `_v` bare LEGAL. Whether a private group is readable through a label above it inside its own binding is decided
   only by choosing which wording is the rule.
4. "start" -- rule 3 "any label on the path may be used as a start label"; reading (a) "means a label the binding's
   own text writes"; rule 6 "[a part used alone] is a start inside its own binding" -- an implicit label, which the
   text writes as a binding's name, not as a label (statement 2: "carries the implicit label of the binding's name").
   Reading (a) read strictly excludes rule 6's start; and a sent label (NAMEGRID-6) is a start whose NAME the caller
   writes and whose PLACE the body writes.
5. "label DAG" vs "tree" vs "equal names" -- rule 1 "in the label DAG"; rule 5 "that binding's tree"; [core/labels/
   rule] line 5 "Labels stacked on one spot are equal names of it; their order does not matter". Run: `[n = [m = P]]`
   `n.m.d` LEGAL, `m.n.d` REFUSED: stacked labels are parent and child, not equal names, for every path but a
   one-step one; line 5 stays printed unqualified in the piece's own list (its restriction lives in a later bullet).
   Nothing in the documents makes the structure a DAG rather than a tree (no node with two parents is shown); if a
   label mentioned twice (`[aa = ..] SEQ [aa = ..]`) is one node, say so; that is the only DAG-making case.
6. "a part used alone" -- statement 2 "protected: reached as `A.h` there" (a label, a start); rule 6 "crossed from
   outside as an underscore label is" (a wall); [core/labels/ownership] body row, used alone column: "no label"
   (no node); [core/labels/paths/argument-default] "A binding used alone in a definition IS placed: its name stands
   for its spot there". Inside under a label: NAMEGRID-3 (`n.d` through it legal, `n.Q.d` refused); outside: NAMEGRID-2.
7. "unambiguously referenced" -- reading (b) "across `&` a name both sides SET is ambiguous"; [core/labels/flow] "a
   part SURFACES a name where the name is visible in the definition, its protected labels included"; [core/labels/
   export/flat-read-outside] "a source it keeps protected does not exist for that read, so it supplies no value and
   makes no `&` ambiguity" (outside only). Answers move: NAMEGRID-1.
8. "within a binding" vs "from outside" -- rule 3 "within a binding"; rule 5 "From outside, the start is ... a label
   written on the use"; reading (e) "starts in the CALLER's binding, whatever the body stacks around them". A label
   on the use (`[c = B(A)]`) is both a rule-3 start (the caller's text writes it) and a rule-5 start; an argument's
   labels lie inside the body's tree and in the caller's binding. No answer found that moves on this pair alone
   beyond NAMEGRID-6; it needs one sentence: "the binding a label is IN is the one whose text writes its name".
9. "the blank label is never a start" -- held: `[_ = P] SEQ "!" & (_.d: <5)` REFUSED ("no part label or used binding
   `_`"); a program cannot spell `_` as a start in a path, so the reading prunes no spellable cell. One meaning.

### NAMEGRID-12 evidence: READINGS calls path-rules (g) UNTESTABLE ("nothing runs `t` as a label"); two programs test it, and (e)'s SUPPORTED covers only labels the body stacks ABOVE
CONFIRMED. Severity: evidence. Effort: two arms in READINGS. Blast radius: the model's verdict on readings (e), (g).
Where: R/tree/docs/dev/lanes/predfold1124_evidence/predfold1124_model.py READINGS (LIGHT run, namegrid/light.out:
"UNTESTABLE: path-rules (g), the equivalence is a picture, not a spelling: nothing runs `t` as a label";
"SUPPORTED: path-rules (e): a caller's label is a start whatever the body stacks"); core.md [core/labels/rule/paths].
- (g): `[_ = [t = A]] SEQ "!" & (t.h: <5)` LEGAL vs `[_t = A] SEQ "!" & (t.h: <5)` REFUSED (A := `/(?<h>\d)/`) is a run
  of "no label `t` is made": it holds for `[_t = A]` and is false for the form the owner called equivalent (NAMEGRID-11
  item 2). From outside both refuse `X.t.h` and `X.h` (held).
- (e): its arm is `B([a = A])` under B(rx) := `/${[n = [_x = rx]]}xx/` (the body's wall ABOVE the caller's label). The
  arm that can fail it -- a wall BELOW a caller-side start, the sent label under `[l = [_ = v]]` -- is not run; run,
  it is legal in the engine and a compile error by rule 2 (NAMEGRID-6). As armed, (e) cannot fail on the question
  "whatever the body stacks".

## PROBED-AND-HELD

- Underscore walls at one level, every start kind: `[_x = [n = A]]`/`[_ = [t = A]]`/`[_p = A]`/`[_t = A]` read from
  outside (`X.n.h`, `X.h`, `X.t.h`, `X._p.h`, `X._t.h`) REFUSED by rule 2, as decided (7 probes); inside, the start
  below or at the wall (`_x.d`, `n.d` under `_x`, `_t.h`, `t.h` under `_`) LEGAL with the printed three-mode answers (4).
- Private target refusals and bare reads: `_v` bare LEGAL (`3!` HOLDS ...), `_.d` REFUSED (the blank never a start: no
  spellable cell) (3).
- Through a call, depth 1-2: `B.h`, `B.q.h`, `B.p.h`, `B.p.q.h` for B(rx) := `/${[p = [q = rx]]}xx/` LEGAL (`3xx` HOLDS,
  `7xx` FAILS / SEARCHED `3xx`@4 / FIND-ALL [`3xx`@0, `4xx`@8], = python `re` `(?P<h>\d)xx`, h<5) (4); caller labels:
  `B([a = A])` with bodies alone/labelled/closed/stacked-`[n = [_ = rx]]`: `a.h` LEGAL; `B.a.h` LEGAL through
  `[p = rx]` and REFUSED through `${rx}` and `[_ = rx]`; `B.p.a.h`, `B.h`, `B.p.h` LEGAL (8); `B([a = [_x = A]])`:
  `a.h` REFUSED, `_x.h` LEGAL; `B([_x = [a = A]])`: `a.h` LEGAL (3); `B(A) & (p.h)` REFUSED (the body's label is
  no start for the caller) (1).
- Skips across operators with PUBLIC parts only: `[n = ([m = P] & [k = Q])] & (n.d)` REFUSED (ambiguous `&`, as
  reading (b)); `[n = ([_x = Q] SEQ [m = P])] & (n.d)` reads m's d (last mention and legal agree) (2).
- Two binding levels without walls: X := `[y = Y] SEQ ";"`, Y := `[c = B(A)] SEQ "!"`: `X.y.c.p.h`, `X.y.c.h`, `X.y.h`,
  `X.h` LEGAL (4); `X.Y.c.h` and `X.h` with X := `Y SEQ ";"` REFUSED (rule 6) (2); Y := `B(A) SEQ "!"`: `Y.p.h`, `Y.h`,
  `Y.B.p.h` REFUSED (a call used alone exports nothing outward) (3).
- Export lists: `[(=) = [n = A]]`: `X.h` LEGAL, `n.h` inside and `X.n.h` REFUSED (the "listed part label's path"
  reading); `[(=) = [_x = A]]`/`[(=) = [_ = A]]`: `h` and `X.h` REFUSED (5). `[n = [(=) = A]]` does not parse in the
  engine (no sentence says whether a list may sit under a label: not counted as a finding; one probe).
- The model's LIGHT run at the freeze: `predfold1124_model: 20 checks, 0 failed` (namegrid/light.out); PATHS pins 7
  rule sentences and passes; every finding above is a cell its arms do not reach (depth 3, two binding levels with
  a wall, a wall below a sent label, a mixed public/private skip, an alone part under a label over an expression).
- Minimum witness lengths: every finding's witness is a one-digit part and a text of length 2-4; pool: about 110
  probe calls, 6 python `re` model sets (namegrid/remodel.py and inline).

CRITIC COMPLETE
