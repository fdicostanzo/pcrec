# NAMES findings — r88 predfold1123b

## Findings


Probe engine: the evidence model's own definitions (predfold1123b_model.py executed up to its `== TABLE` line, all 10
preceding checks PASS), driven from my own clone (NAMES/tree, file names_probe.py beside the model; case files
NAMES/c1..c4.txt, outputs NAMES/c1..c4.out). Each legal cell printed in all three modes (WHOLE `3xx`/`7xx`/`x`,
SEARCHED `7xx 3xx`, FIND-ALL `3xx 7xx 4xx`, or the case's own texts). MINIMUM WITNESS LENGTH: 3 (`3xx`, `7,3`).
Bodies: alone `/${rx}xx/`, labelled `[p = rx]`, listed `[(=) = rx]`, closed `[_ = rx]`, `_p`, stacked `[n = [_x = rx]]`.

### NAMES-1 — the "forwarded" column is wrong for rows 1-4: a body CAN pass a pattern parameter on, and there the model loses every label (silent wrong answers) and checks condition 4 one body deep only
CONFIRMED (model), UNDECIDED (text). Severity: answer. Effort: medium (a column + the model's nested-call path). Blast: every body that calls another macro with its parameter (the library's bodies over `atomic`, `when`, user wrappers).
- The table's cells for rows 1-4 say "n/a: only a label parameter is passed on (core/operators/bindings/label-forward)" (core.md:374-377). A body passing its PATTERN parameter to another macro, `B(rx) := /${C(rx)}xx/`, is ordinary; no sentence makes it n/a.
- Runs (C(r) := `/${r}/` unless stated; A := `/(?<h>\d)/`):
  - `B(S(x:)) & (x: <5)`, S(l:) := `/(?<:${l}>\d)/`: WHOLE `3xx` FAILS, `7xx` FAILS. The text decides HOLDS/FAILS: "Placed once, twice or never by the receiving body: set once" (core.md:2087). The model loses the label with no refusal and no warning.
  - `B(/(?<h>\d)/) & (h: <5)`: WHOLE `3xx` FAILS (an in-place group, the caller's own: core.md:658).
  - `B([a = A]) & (a.h: <5)`: REFUSED "`h` is not visible through `a`" (row 4 says `a.h` in every column, core.md:377).
  - `B(A) & (A.h: <5)`: REFUSED "every use of `A` here is labelled" (no label is written anywhere: a wrong mechanism); its expansion `B([A = A]) & (A.h: <5)` is refused the same way.
  - Condition 4 one body deep: `B(rx) := /${C(rx)}xx/` with C(r) := `/${[q = r]}/` gives `A.h` LEGAL. So does `B(rx) := /${atomic(rx)}xx/` (atomic lists its spot, library.md:394). Then no path reads it: `B.h`, `B.q.h`, `B.C.q.h`, `B.atomic.h` are all refused. core.md:342-343 says "A label made there is made by anyone on that use, the body included", but no sentence says whether "the body" includes a body the first body calls.
- To decide: a forwarded-pattern column, saying whether condition 4 looks through nested bodies and which path reads a label a nested body makes. The model's nested call needs fixing before any such cell can be run.

### NAMES-2 — an argument that is an EXPRESSION holding a binding (`B(A SEQ /x/)`, `B(C(A))`, `occurrences(B(A))`): no row decides it, and the model's sugar disagrees with its own written-out expansion
CONFIRMED. Severity: answer. Effort: small for the text (one row), medium for the model. Blast: every `B(A SEQ ..)` / `B(A | ..)` / call-in-argument read.
- The expansion rule: "Written out, `B(A)` is `B([A = A])` for that use (the expansion, run)" (core.md:870). Condition 4 is "no label has already been made on it there" (core.md:343). Reading (a) is "anything between them makes two spots" (core.md:353). Read together, a body's label on the argument's spot `A SEQ /x/` is not on A's spot, so `A.h` is legal.
- Runs, sugar against expansion (A := `/(?<h>\d)/`):
  | body | `B(A SEQ /x/) & (A.h: <5)` | `B([A = A] SEQ /x/) & (A.h: <5)` |
  |---|---|---|
  | `/${rx}x/` (alone) | REFUSED "a label of an argument, which is a template and not a spot" | WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `3xx`@4 / FIND-ALL [`3xx`@0, `4xx`@8] |
  | `/${[p = rx]}x/` | legal, the same answers | legal, the same answers |
  | `/${[_ = rx]}x/` | REFUSED "the body closes the door through `A`" | legal, the same answers |
  | `/${[(=) = rx]}x/` | legal | legal |
  `B(A | /y/) & (A.h: <5)` with the alone body is REFUSED the same way.
- The model is also inconsistent across shapes. With a closing body, `B(C(A)) & (A.h: <5)` (C alone, so B's blank mark sits directly on A's spot) is LEGAL, while `B(A SEQ /x/)` (something between) is refused. `occurrences(B(A)) & some((A.h: "3"))` is legal, while `B(A SEQ /x/)` with the alone body is refused.
- The "template and not a spot" refusal names no current sentence: argument-default (core.md:869) says the shorthand label "is on the spot where the body places the template".

### NAMES-3 — "a label made on it there" is undefined for a label over a WIDER spot or written in rx text around the hole: dead cells with no deciding sentence
CONFIRMED (model), UNDECIDED (text). Severity: design. Effort: small (a sentence on what "on the spot" covers). Blast: condition 4, columns labelled/closed.
- Stacked labels are defined as "label brackets nested directly; anything between them makes two spots" (core.md:353), but "made on it" (core.md:343) is never tied to that definition. Runs (A := `/(?<h>\d)/`, read `B(A) & (A.h: <5)` / `(B.p.h: <5)`):
  - `B(rx) := /${[p = rx SEQ /x/]}x/`: `A.h` REFUSED ("a label is already made on the spot ... `p`") and `B.p.h` REFUSED. No spelling reads A's h.
  - `B(rx) := /${[n = (rx)]}xx/`: `A.h` LEGAL, so parentheses count as "between" here. But `[n = ([_x = rx])]` gives `B.n.h` REFUSED, so parentheses also count as "between" for line 5. A `SEQ` between does NOT count for condition 4: the two "between" tests disagree.
  - `B(rx) := /(?<p>${rx})xx/` (a named group in rx text around the hole): `A.h` REFUSED (label made) and `B.p.h` REFUSED. Dead. The label-only `(?<:p>${rx})` gives `B.p.h` legal (`3xx` HOLDS, `7xx` FAILS / `3xx`@4 / [`3xx`@0, `4xx`@8]). No sentence says a plain rx group over a hole is a label on the spot, or why it passes nothing.
  - `B(rx) := /${[p = rx | /y/]}xx/`: `A.h` REFUSED.
- To decide: one sentence on what spot a label is "on" (directly nested only, or any enclosing label), applied to condition 4 and line 5 alike.

### NAMES-4 — two PUBLIC labels stacked (`[n = [m = A]]`): line 5 and export statement 3 disagree on `n.m.h`
CONFIRMED (model takes line 5), UNDECIDED (two sentences). Severity: design. Effort: small. Blast: the stacked column (the table only shows a private inner layer).
- Line 5: "Labels stacked on one spot, with nothing between them, are equal names of that spot" (core.md:350).
- Statement 3: "through a public part label, the labels that part exports, by path (`pub.a.h`, each step passed by the previous one ...)" (core.md:540-541). `n`'s text writes the part label `m`, so `n.m.h` is a path.
- Runs: `[n = [m = /(?<h>\d)/]] SEQ /xx/ & (n.m.h: <5)` REFUSED ("`m.h` is not visible through `n`"). `X & (X.n.m.h: <5)`, X := `[n = [m = A]] SEQ /xx/`, REFUSED. With something between, `X := [n = [m = A] SEQ /x/] SEQ /x/`, `X.n.m.h` is LEGAL (`3xx` HOLDS, `7xx` FAILS). So adding `SEQ /x/` opens a path. `B.n.h` and `B.m.h` both legal (the equal names hold).
- To decide: whether equal names also chain, i.e. whether line 5 removes statement 3's path.

### NAMES-5 — a body that never places a binding argument: the shorthand and its expansion get different verdicts from two sentences
SUSPECTED (the model refuses both; its CLAUDE.md lists the never-pass warning as not modelled). Severity: design. Effort: small.
- `Z(A) & (A.h: <5)`, Z(p) := `/xx/`. Condition 2, "a label could have been set on it there" (core.md:342), fails because there is no "there": a compile error. The written-out `Z([A = A]) & (A.h: <5)` is the caller's own label never placed: "never, the never-pass warning" (core.md:663), which is legal. Sugar and expansion part.
- Model: `Z(A) & (A.h: <5)` REFUSED "no part label or used binding `A` here".
- To confirm: a sentence for the never-placed shorthand.

### NAMES-6 — by-name reads through a body's list do not pass a caller's part label, though they pass through a body's label
CONFIRMED (model), UNDECIDED (text). Severity: design. Effort: small.
- `B([a = A]) & (B.p.h: <5)`, B(rx) := `/${[p = rx]}xx/`: LEGAL (by name through `p` then `a`, statement 3 "and by name (`pub.h`)", core.md:542). `B([a = A]) & (B.h: <5)`, B(rx) := `/${[(=) = rx]}xx/`: REFUSED ("`h` is not visible through `B`"). `B.a.h` is legal there.
- "A list takes all the part exports" (core.md:640) plus statement 3's by-name export of `[a = A]` would make `B.h` legal. The export/arguments table (core.md:679) states only `identity.a.h`. Row 4 of the ownership table prints only `a.h`, so neither read is in the table.

### NAMES-7 — the table's "listed" cell for the body row cites a piece whose own sentences decide the opposite
CONFIRMED (text). Severity: doc. Effort: trivial.
- Row 3, listed: "`B.h` (core/labels/export/export-list)" (core.md:376). Export-list says "Only an EXPORTED label of the part can be listed" (core.md:649), and its partner row says "`[(=h) = rx]` in a body | a compile error at the definition: a parameter exports nothing the body can list" (core.md:682). Read alone, they make the read through `[(=) = rx]` a compile error.
- The ground that makes `B.h` legal is transform-export: "`identity(A)`, `identity.h` | A's exported labels, through the list on the spot | transform-export" (core.md:678). The model agrees `B.h` is legal (`3xx` HOLDS, `7xx` FAILS / `3xx`@4 / [`3xx`@0, `4xx`@8]).

### NAMES-8 — "the one cell no ruling decides" is not one; the backdoor cell is a reading "to confirm" elsewhere
CONFIRMED (text). Severity: doc. Effort: trivial.
- core.md:370: "'a reading' marks the one cell no ruling decides: a list on the spot is a label made".
- The details partner (core_details.md:534-537) lists THREE cell readings: the listed cell, "the definition's own text, closed", and "forwarded column ... (a reading of the column)". It also lists reading (c) of the stacked blank label (core_details.md:535).
- Row 5, closed: "`x` bare: the backdoor (line 4)" (core.md:378), with no reading mark. Label-in-argument says "The backdoor passes `[_ = rx]`, a `_` part label and a body that uses the argument alone (reading (c), the last the natural extension, to confirm" (core.md:2089-2090). His ruling's `_` was `_:` on the outer spot (core.md:2082, 2085-2086), which label-omitted makes "the part with NO label" (core.md:2035), not the blank mark. One cell carries two statuses.

### NAMES-9 — the table is narrower than "Every case in one table", and its run statement gives one mode
CONFIRMED (text). Severity: doc. Effort: small.
- core.md:852 says "Every case in one table: core/labels/ownership". The table has no column for a `_` part label `[_p = rx]` (decided at core.md:847), none for a body placing its argument twice, alone and labelled, or never (core.md:663, 812-815, 883-884), and no row for an in-place group of the caller's (`B(/(?<h>\d)/)`, core.md:658, 670).
- The table states "Every cell is run, WHOLE `3xx` HOLDS and `7xx` FAILS where it is legal" (core.md:371): WHOLE only. TABLE runs one program per cell, so these cells' second reads are never run: `x.h` (row 1 labelled), `B._x.h` (row 3 stacked), and `B.h`, which is also legal by name in the labelled and stacked columns but unprinted.
- I ran all of these in three modes. Each agrees with what its sentence decides, and every legal cell gives SEARCHED `3xx`@4 and FIND-ALL [`3xx`@0, `4xx`@8] (c1.out, c2.out). The defect is the table's statement, not the answers.

### NAMES-10 — refusals that name the wrong mechanism
CONFIRMED (model). Severity: nit (COMMON: a refusal must name the mechanism). Effort: trivial.
- `B([a = A]) & (A.h: <5)`: "`A` is neither written nor a binding used in this definition". A is written there; the ground is binding-prefix "a labelled use is reached by its label" (core.md:740-741) or argument-default:868.
- `R(_:, A) & (R.h: <5)`, R(l:, v) := `/${[l = v]}xx/`: "`R` is neither written nor a binding used". R is called here; the ground is that the call exports nothing (core.md:807).
- NAMES-1's "every use of `A` here is labelled", where no label is written.

### NAMES-11 — a list the CALLER writes, `[(=) = A]` / `[(=h) = A]`, over a binding whose label is a group: the text decides legal and the model refuses, even outside any argument
CONFIRMED (model against text). Severity: answer (in the evidence engine; no printed line meets it). Effort: small. Blast: the list row of the root concept, and every lens that probes lists through this engine.
- The text: "the binding takes the listed labels of the part as labels of its own (exported; read bare inside it)" (core.md:626). A's own names include "a group in its literals" (core.md:539-540). `[(=) = isodate]` takes "all the part exports" (core.md:640). A label the caller writes inside an argument (a part label) is the caller's own (core.md:658).
- Runs (A := `/(?<h>\d)/`):
  - `[(=) = A] SEQ /xx/ & (h: <5)`: REFUSED ("label `h` is not written in this definition").
  - `[(=h) = A] SEQ /xx/ & (h: <5)`: REFUSED ("`h__own` is not a label the part exports"). The name `h__own` is internal to the model, and A does export `h`.
  - The same two refusals inside an argument, `B([(=h) = A]) & (h: <5)`, under the alone, closed and labelled bodies.
  - The renaming form, `B([(y = h) = A]) & (y: <5)`, is LEGAL: `3xx` HOLDS, `7xx` FAILS / `3xx`@4 / [`3xx`@0, `4xx`@8]. Only the same-name form fails, so the defect is in the model's same-name handling, not in the rule.
  - `B([(=h) = A]) & (B.h: <5)` through a listing body is LEGAL (the same answers).

### NAMES-12 — THE ROOT CONCEPT (sub-part 2): for each way a name comes to be on a spot, does the text decide its owner and its doors?
Summary (each line was run; the evidence is in c1..c5.out):
- Written by the defining text (a group, a part label, `_`, `_p`, stacked, listed): owner and doors DECIDED by line 1 and line 4's gloss "its owner always reads it". Held in 3 modes (12 cells).
- Written by the caller inside an argument (part label, in-place group, sent label, private `_a`, `_y:`): DECIDED, held in 3 modes, EXCEPT when the body passes its parameter on (NAMES-1) and for the caller's same-name list (NAMES-11).
- Made by the body on the spot (label, list, blank mark, `_p`, stacked): DECIDED one body deep. NOT DECIDED for a nested body (NAMES-1), a wider spot or an rx-text group (NAMES-3), or two public layers (NAMES-4).
- A binding's shorthand: DECIDED for `B(A)`. NOT DECIDED for an expression argument (NAMES-2) or a never-placed argument (NAMES-5).
- A label parameter (`x:`, `_y:`, `_:`, a default `_`): DECIDED. `R(x:, A)` gives `x.h` legal and `A.h` refused (made by anyone). `R(_y:, A)` gives `_y.h` legal. `R(_:, A)` gives `A.h` legal ("no label", core.md:2035). Held.
- "made": defined only by example (core.md:342-343, 845-848). "on it there" is never tied to line 5's "nothing between them" (NAMES-3). "stacked": defined (core.md:353), but whether parentheses count as "between" is decided only by the model (identity((A)) at core.md:681 is the nearest sentence). "nothing between them": not applied to condition 4. Root definition: INCOMPLETE on these three words.

### The grid, every cell (sub-part 1): the table's 26 printed cells, each with its deciding sentence and my run
Columns: alone / labelled / listed / closed / stacked / forwarded. A := `/(?<h>\d)/`. Legal cells give WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] unless stated.
- Row 1, the defining text. Deciding sentences: core.md:330 (line 1), 346-347 (line 4's gloss), 350 (line 5).
  - All five columns `h` bare: legal.
  - Second reads: `x.h` legal, `n.h` legal, `_x.h` legal.
  - Outside the table: `_p` column `h` and `_p.h` legal; `[n = [_ = ..]]` `h` and `n.h` legal.
  - Forwarded: n/a. WRONG (NAMES-1).
  - Verdict: DECIDED, agrees.
- Row 2, a binding passed whole, `A.h`. Deciding sentences: core.md:340-343 (line 3, the four conditions) and 845-848.
  - alone: legal. labelled, listed, closed, `_p`, stacked (either order): refused (condition 4).
  - Path reads: `B.p.h` legal; `B.h` legal through the list and ALSO through the labelled and stacked bodies (unprinted); `B.n.h` legal; `B._x.h` refused.
  - Forwarded: n/a. WRONG (NAMES-1).
  - `$A.h` and `some((A.h: "3"))` give the same verdicts in every column (val.*, gq.*).
  - Verdict: DECIDED, agrees, apart from NAMES-2/3/5.
- Row 3, the body's label. Deciding sentences: core.md:376, 806-807.
  - alone `B.h`: refused. labelled `B.p.h`: legal. listed `B.h`: legal (grounded in the wrong piece, NAMES-7). closed `B.h`: refused. stacked `B.n.h`: legal; `B._x.h`: refused. `_p` `B._p.h`: refused.
  - Verdict: DECIDED, agrees, apart from NAMES-3/4.
- Row 4, the caller's own label. Deciding sentences: core.md:658, 669-670, 850.
  - `a.h` legal in all five columns, and under `_p`. `_a.h` legal under a closing body.
  - Path reads: `B.a.h` legal (listed), `B.p.a.h` legal, `B.n.a.h` legal, `B.p.h` legal; `B.h` through the list refused (NAMES-6). `A.h` refused (wrong message, NAMES-10).
  - Forwarded: n/a. WRONG: the model loses `a` (NAMES-1).
  - Verdict: DECIDED, agrees, apart from NAMES-1/6/11.
- Row 5, a sent label. Deciding sentences: core.md:2082, 2087-2089, 2097.
  - `x` bare legal in all six columns, `_p` too.
  - `_x:` legal. `_:` matches with nothing to read (`3xx` and `7xx` HOLD). `B.x` legal (listed), `B.p.x` legal (labelled). `S.x` and `F.x` refused ("not offered", core.md:680).
  - Forwarded through a pattern parameter: WRONG ANSWER in the model (NAMES-1).
  - Verdict: DECIDED; the closed cell has two statuses (NAMES-8).
- Occurrences axis, all agreeing with core.md:871 (condition 1), 812-815 and 883-884:
  - caller references A twice: `A.h` refused (condition 1).
  - `B(A) SEQ B(A)`: `B.p.h` refused (label the call); `some((B.p.h: "3"))` legal (`3x7x` HOLDS, `7x3x` HOLDS, `7x7x` FAILS).
  - body places twice alone: `A.h` reads the last mention (`7,3` HOLDS); `A.h[1]` reads the first; `some` reads both.
  - body places twice labelled `q`: `P2.q.h` reads the last mention; `P2.p.h` refused.
  - body places once alone and once labelled or closed (either order): `A.h` reads the alone spot.
  - body never places: NAMES-5.
- Read kinds:
  - condition, `$` value read and group question agree in every column run.
  - find-all argument: `occurrences(B(A) & (A.h: <5))` is legal / refused as `B(A)` is. `occurrences(B(A)) & some((A.h: "3"))` is legal (WHOLE `3xx` HOLDS, `7xx` FAILS, `7xx3xx` HOLDS) but is in tension with NAMES-2. `occurrences.hit.A.h` refused (core.md:720).

## PROBED-AND-HELD
- 181 cells run through the model's engine (c1 52, c2 55, c3 54, c4 11, c5 9); 80 are refusals, each checked against its deciding sentence.
- The table's 26 printed cells: every printed legality reproduced, all three modes printed for each legal cell, and each answer agrees with the cell's sentence (minimum witness `3xx`, length 3).
- The table's second reads that TABLE never runs (`x.h`, `B._x.h`, `B.h` labelled/stacked, `B.a.h`, `B.p.a.h`, `B.n.a.h`): legal and agreeing.
- Stacked order (`[n = [_x = ..]]` against `[_x = [n = ..]]`, `[n = [_ = ..]]` against `[_ = [n = ..]]`): order-free, as line 5 says.
- Label parameters `x:`, `_y:`, `_:` on a spot: owner and doors as label-omitted / label-in-argument say.
- Occurrences axis (12 cells) and read kinds (`$`: 6 cells, group question: 4, find-all: 8): held, except where noted in NAMES-2/5.
- Not run: libpcre2 lowering of these cells. The model's engine was the oracle; the `3xx`/`7xx` answers are trivially `(\d)xx` + a comparison.
CRITIC COMPLETE
