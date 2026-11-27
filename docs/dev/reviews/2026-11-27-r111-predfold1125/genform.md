# CRITIC GENFORM: r111 predfold1125

## Findings

### GENFORM-1 — `n.Q.d` is evaluated by REWRITING it to the start form `Q.d`; "used more than once" then counts over the whole definition by accident (CONFIRMED; answer + design)
- Piece: core/labels/rule/alone-as-middle (core.md:546 "A part used more than once is refused as a step, as it is
  as a start."); R5PATCH11's walk10 replacement (predfold1125_model.py:983-984, `rest[1:], ..., [nm]` "the read is the
  part's own: `Q.d`"). Ruling: alone-as-middle, record l.12131.
- Repro (my harness `genform/grid.py` = the model up to `unit11("CANARY", `, then `run11`; cells `genform/cells2.txt`,
  out `genform/grid2.out`), P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`:
  `[n = (P SEQ Q)] SEQ [m = (P SEQ Q)] & (n.Q.d: <5)` -> REFUSED "`Q.d`: Q is used 2 times here; label the part
  (`[left = Q]`) to read one use"; `m.Q.d` alike; `... SEQ ";" SEQ [m = (P SEQ Q)] & (m.P.d: <5)` alike for P.
  The message names `Q.d`, a read the program never wrote.
- Mechanism: the patch's OWN twice-count is under the prefix (`_leaves(t, lo, hi, ...)`, n's content: 1 use), so it
  passes; it then returns the route `[nm]`, path10 rewrites `n.Q.d` to `Q.d`, and the loaded engine's START rule
  counts Q over the definition (2 uses) and refuses. Two scopes in one evaluator, the stricter winning silently.
- Proof the legal answer depends on the rewrite: mutation `route` (route `route + pub + [nm]`, the full path; file
  `genform/mut_route.py`, run `genform/mutrun_route.out`) -> SPECLINES FAILS: "ALONE1 `n.Q.d`: `Q.d` is not visible
  through `n`" — the loaded engine cannot read the step at all; only the start form runs. So READINGS11's "R-5:
  `n.Q.d` inside has `Q.d`'s answers" (model :1671) compares the rewrite with its own target: a control sharing its
  source with what it controls; it cannot fail while the rewrite exists.
- Doc gap: the scope of "more than once" for a STEP is not stated. core_details.md:1185 counts a START "in the
  definition the reference is written in". For a step the two readings differ exactly in the gate's natural use:
  (a) definition-wide: two labelled copies of one gated part (`[n = (P SEQ Q)] SEQ [m = (P SEQ Q)]`) give NO access
  through either gate, and the owner's "you have to mention the gate label" (record l.12105) buys nothing there;
  (b) under the prefix: `n` disambiguates, `n.Q.d` legal (rule 4's "unambiguously referenced from a" is relative to
  the start a). Lean: (b) — rule 4 already measures ambiguity from the path's start, and (a) makes `n.` a no-op.
  Either way it is a question for the owner or a stated reading with a printed line; today the model answers (a)
  by artefact.
- Effort: doc a sentence + one printed line; model: see GENFORM-6's rebuild. Blast radius: every gated read
  where the gated part is used again anywhere in the definition.

### GENFORM-2 — a skip over a part used alone BESIDE a written label: the model drops the gated candidate silently; no sentence decides it (CONFIRMED in the model; design)
- Piece: core/labels/rule/alone-as-middle, core.md:540 "never skipped: `n.d` through it is a compile error naming
  `n.Q.d`" and :546 "A label someone WROTE (`[a = P]`) is still skipped by rule 4"; skip-past-wall core.md:519
  "Rule 4's candidates count only the targets a legal path reaches: a private part behaves as if its labels were
  not there". Rulings: alone-as-middle l.12131, skip-past-wall l.12054.
- Repro (`genform/grid.out`, `grid2.out`): `[n = ([a = P] SEQ Q)] & (n.d: <5)` -> LEGAL, P's `d` (holds `3,7`,
  fails `7,3`); `[n = ([m = P] | Q)] & (n.d: <5)` and `[n = ([m = P] & Q2)] & (n.d: <5)` -> LEGAL (the labelled
  side's d); from outside `X := [n = ([a = P] SEQ Q)]`, `X.d` LEGAL (P's d — that one is statement 3's "a source it
  keeps protected does not exist for that read", fine).
- Three readings inside, none stated: (i) a compile error — `n.d` does reach Q's `d` "through it", the ruling's own
  words; (ii) P's `d`: the gated part behaves as a wall in rule 4's candidates (the model; skip-past-wall's
  sentence extended from a PRIVATE part to a part used alone, which statement 2 calls protected, not private);
  (iii) Q's `d`, the last mention, rule 4 as worded. This is exactly the owner's own "Against: an array on d
  constructed from multiple sources" (record l.12107), now in its mixed form. The printed lines cover only the
  pure cases (both alone; both labelled in the record run l.12117).
- Fix shape: a sentence + a printed line in alone-as-middle (or an owner question). Lean (ii) for symmetry with
  outside, where the gated part is already "not there" — but (i) is closer to "never skipped". Effort small.

### GENFORM-3 — a macro call used alone is not a gate in the model, and the piece never says whether it is (CONFIRMED; answer + doc)
- core/labels/rule/paths terms, core.md:465-466: "a node is ... a label used alone (a binding's or a macro's name on
  its part: implicit)"; alone-as-middle (core.md:540) speaks of "a part used alone" and prints only binding uses.
- Repro (`genform/grid2.out`, `grid.out`), B(rx) := `/${[p = rx]}xx/`:
  `[n = (P SEQ B(Q))] & (n.B.p.d: <5)` -> REFUSED "`B.p.d` is not visible through `n`" (generic);
  `[n = (P SEQ B(Q))] & (n.B.d: <5)` -> REFUSED alike; `[n = (P SEQ B(Q))] & (n.d: <5)` -> REFUSED naming
  "`n.p.d`: `p.d` is not visible through `n`" — a path nobody wrote, and not the alone-as-middle message naming
  `n.B.d` / `n.P.d`; yet `(B.d: <5)` and `(B.p.d: <5)` as starts are LEGAL.
- Cause: R5PATCH11 edits only the `kind == "bind"` branch of walk10; the `call` branch keeps
  `raise Und("a macro's name as a middle")` (predfix90_model.py:296) and hands the read to the loaded engine.
- The documents' own term makes a macro's name on its part the same node as a binding's; the ruling's general form
  covers it. Either the piece says "a binding's or a macro's use" with one printed line (`n.B.p.d` legal), or it
  excludes calls in a sentence. Today the evaluator answers one sibling by the rule and the other by a hand-off.

### GENFORM-4 — parentheses decide whether a sole part is "used alone": `[n = Q]` vs `[n = (Q)]` answer differently (CONFIRMED in the model; doc)
- Repro (`genform/grid.out`): `[n = Q] & (n.d: <5)` -> LEGAL; `[n = (Q)] & (n.d: <5)` -> REFUSED "the path skips a
  part used alone ... write `n.Q.d`"; `X := [n = (Q)]`, `X & (X.n.d: <5)` -> REFUSED rule 6, where `[n = Q]`
  would export it. Cause: predfix90's `_directly` compares the label's content text with the leaf text after
  `strip()` (predfix90_model.py:234-239), so a parenthesis makes the leaf "unlabelled".
- The documents never define "used alone" against grouping parentheses. core.md:495 says the nested form
  `[n = ([m = P])]`, "two spots, reads the same" — for two LABELS; nothing says whether `(Q)` under `[n = ..]` is a
  labelled use. Before R-5 this was invisible (an unlabelled use was a start only); now that a part used alone is
  never skipped, a parenthesis moves an answer from legal to a compile error.
- Fix shape: one sentence in core/labels/export statement 2 ("a use is labelled when it is the whole content of a
  label, parentheses aside" or the opposite) + one printed line. Lean: parentheses aside (grouping is not a spot;
  core/principles/label-names-spot). Effort small.

### GENFORM-5 — "inside" means two things in two sibling pieces: the gate is readable through a written label (`n.Q.d`), the shorthand is not (`pub.A.h`); no sentence names the boundary (design; doc)
- alone-as-middle (core.md:540): inside the definition, `n.Q.d` through the definition's own label n is legal.
  shorthand-outside (core.md:1111-1117; ruled l.12148), printed: `[pub = B(A)] & (pub.A.h: <5)` "a compile error ...
  the shorthand label is protected: it adds no export" — called "a read from outside the caller", though `pub` and
  the read are written in ONE definition, and A is, by the same piece's ruled lean, "An implicit name ... from an
  argument passed by name, behaves one way: named inside, invisible outside" — the same sentence covers "a part
  used alone".
- So two implicit names, one stated behaviour, two answers for the same shape (written label, then the implicit
  name, then the target, all in one text). The reconciling fact is the CALL BOUNDARY: the shorthand's spot lies in
  B's body (below `p`), so `pub.A.h` re-enters the caller after crossing B's tree, while `n.Q.d` crosses no
  boundary. No document sentence says this; "inside"/"outside" are defined per binding (core/labels/rule/paths:
  "'within a binding' is the text of one definition"), which makes `pub.A.h` INSIDE.
- Consequences the documents now owe (each a printed line or an open question): where the caller's implicit name
  sits in a path through a call (`pub.A.h`? `pub.p.A.h`? never?), whether `[n = B(Q)] & (n.Q.d: <5)` is legal (the
  model refuses it generically, `genform/grid.out`), and whether a sent label (also "the caller's", a start under
  the body's wall) may be a middle step. The ruling stands (it is the owner's); the finding is the missing general
  sentence: "a path is inside while it crosses no binding or call boundary; an implicit name is a node only inside".

### GENFORM-6 — R5PATCH11 by text is mechanically safe but semantically leans on the loaded engine; three of its arms guard nothing or are guarded by accident (CONFIRMED; maintenance)
- Mechanics HOLD: each replacement is asserted `body_.count(old_) == 1` inside its own function's slice
  (model :1019-1023), so a zero or double match cannot pass silently; recursion goes through the X11 switch
  (`globals()[fn_] = _r5(fn_)`). The `\ndef ` slice end is safe for these three functions (no module code between).
- Semantics do NOT hold by itself. My one-arm mutations (copies `genform/mut_*.py`, LIGHT, outputs
  `genform/mutrun_*.out`; verdict = last line):
  | mutation | what moved | verdict |
  |---|---|---|
  | outside arm off (`if outside:` -> `if False:`) | READINGS11's "R-5 check" (X.Q.d refused) still PASSES: the read is rewritten to `Q.d` and the loaded engine refuses it for ANOTHER reason ("`Q` is neither written nor a binding used in this definition"); only ERRSWEEP11's message wording fails | 1 failed (ERRSWEEP11) |
  | twice arm off (`> 1` -> `> 99`) | answers unchanged (the loaded engine's START rule refuses `Q.d`); only the message | 1 failed (ERRSWEEP11) |
  | `[ok] or sub` filter -> `sub` | nothing | **0 failed** |
  | route = full path (GENFORM-1) | SPECLINES/SWEEP11/READINGS11 | 3 failed |
  | walker never-skipped arm off | GRID 168 cells + ERRSWEEP11 | 2 failed |
  | g_eval arm off | GRID 168 cells | 1 failed |
  | path10 alone message off | ERRSWEEP11 | 1 failed |
- Plant q15 (`genform/plant_q15.out`) turns off BOTH the walker's arm and the evaluator's arm: 168 of the 184 moved
  GRID cells move on both sides and agree unseen; it is caught only by 16 residual cells (legal->refused, the loaded
  engine's own refusal) and ERRSWEEP11's printed line. A plant that edits the control with the subject.
- GRID never exercises the middle-step half: its steps are subsequences of the PUBLIC labels only (`g_cells`), so no
  cell writes `n.A.h`; the pinned GRULE["alone"] sentence (model :1030) is that unexercised half ("may start a path
  or be a middle step"), while the half GRID does exercise ("never skipped") is unpinned.
- Verdict: patch-by-text is acceptable for "never skipped" (both one-sided mutations caught by GRID) and unsound
  for "a middle step" and "used twice" (answered by the loaded engine after a rewrite). Cheapest sound rebuild: a
  TEXT relabel before the engine — rewrite each unlabelled use `Q` under the read's prefix to a written label with
  a fresh name (`[Q__1 = Q]`) and the read to `n.Q__1.d`, so the loaded engine answers the full path natively and
  the twice-count is the engine's own label count under the chosen scope; plus GRID steps drawn from public labels
  AND alone names (one extra token), and READINGS11's R-5 identity check replaced by a regex-built expected answer.

### GENFORM-7 — the wall reported is the first site's, not the deciding one: the ruled message "naming `n.Q.d`" is lost beside a private part (CONFIRMED; doc/message tier)
- Repro (`genform/grid.out`, `grid2.out`): `[n = ([_ = P] SEQ Q)] & (n.d: <5)` -> "the path crosses the underscore
  label `_`, not the start (rule 2)"; `[_x = P]`, `[_a = P]` alike. By skip-past-wall (core.md:519) the private
  part's labels "were not there", so the only candidate is through Q, and the ruled error is the one "naming
  `n.Q.d`" (core.md:540). With the private part SECOND (`[n = (P SEQ [_ = Q])]`) the model gives the alone message
  naming `n.P.d`: the answer is order-dependent wording. path10 raises on `walls[0]` (predfix90_model.py:393).
- Message tier only (D26); fix: prefer an "alone" wall over a rule-2 wall in path10's choice, or state the order.

### GENFORM-8 — a lookaround's KIND is stated three ways; the model picks a fourth (CONFIRMED; design + answer)
- Sentences: core/filters/negation (core.md, its statement): "`!X` is the logical not of a test (a condition, a
  lookaround, a group question, or another `!X`)" — a lookaround is a TEST; core/patterns/lookaround/ahead: "`^A`
  is a zero-width pattern that can match, usable wherever a pattern is" — a PATTERN; core/filters/family table:
  `^A` and `!^A` both with operand "a pattern" and "can match", beside the row "`!X`, X a set or pattern | a
  compile error naming `~`" — which, read literally, refuses `!^A`. Rulings: bang-split l.11963 (the ruled lines say
  only "`^A` looks ahead and `!^A` is its negative").
- Repro (`genform/cells3.txt` -> `genform/grid3.out`):
  `"x" SEQ ~^/\d/` -> REFUSED "`~` on a test ... is `!^/\d/`" (the model: `^A` is a test; by the lookahead piece it is
  a pattern and `~` on a pattern is the complement);
  `"x" SEQ !/(?=\d)/` -> REFUSED "`!` on a set or pattern" — an rx-text lookaround, which negation's statement
  lists as a test, so `!` on it should hold (= `(?!\d)`); the same zero-width construct is a test when spelled
  `^/\d/` and a pattern when spelled `/(?=\d)/`;
  `/(?<h>\d)x/ SEQ ^(h: <5)`, `^^/\d/`, `^!^/\d/` -> LEGAL: `^` on a test and on a lookaround, no sentence.
- General form the rulings imply but no document states: ONE kind lattice — consuming pattern, ZERO-WIDTH
  (a lookaround, a condition in a sequence: core.md:204 "zero width at its point | a test"), set — and one
  operator x operand table: `^` consuming -> zero-width; `!` zero-width -> zero-width; `~` set -> set and
  consuming -> filter; every other cell a compile error naming the operator that fits. Then `!^A`, `!(h: <5)` and
  `!/(?=x)/` are one row, `~^A` is a named error ("a complement of a zero-width pattern: write `!^A`"), and
  `^(h: <5)` is decided (identity, or an error).
- Trigger: any printed program writing `!/(?=..)/` or `~^A`, or the lookbehind operator's ruling (GENFORM-9) —
  it must fill the same row. Effort: one table replacing the family table's two error rows; CENSUS11 can read it.

### GENFORM-9 — lookbehind, the missing sibling of `^`, is half-named: a fold-touched row spells it `^A` (CONFIRMED; doc)
- core.md:207, changed BY THE FOLD (fold.diff:63-64): "| a positive lookahead or lookbehind (`^A`) | from its
  point, consuming nothing | can match |" — `^A` now labels a row that includes lookbehind, while
  core/patterns/lookaround/ahead says "lookbehind has no operator for now" (core.md:391; bang-split line 6, "Lookbehind
  gets no operator for now"). Also no row of that operand-context table covers `!^A` (the not row says "a test";
  the family table says `!^A` "can match").
- Fix: "(`^A`; a lookbehind in rx text)" or split the row. Unlock with a trigger: the lookbehind operator (a
  mirrored `^`, e.g. a postfix form) falls out of GENFORM-8's table as one row, and the stream roadmap's reverse
  DFA in a VM lookbehind (memory pcrec-stream-manifesto-roadmap) is its first engine client; trigger = a printed
  library body (lib/) that writes `(?<=` / `(?<!` in rx text because no operator exists — today a grep of
  library.md counts them; at 3+ the operator pays.

### GENFORM-10 — one label-kind table: the fold adds two implicit kinds and the word "protected" now names two different path behaviours (design; unlock)
- Kinds the documents now have, each in its own piece: public written `[a = A]`; protected written `[_a = A]`
  (statement 6, path rule 2); blank `[_ = A]` (statement 7); a part used alone, binding or macro (statement 2,
  alone-as-middle); the caller's shorthand (shorthand-outside); a sent label (sent-label-wall); an export-list
  alias (export-list); a map element label (core/modules/map: "an array of labelled elements"); an rx group
  (group-node, OPEN). Columns the rulings decide: start inside / middle step inside / skippable (rule 4) / start
  from outside / crossed from outside / exported / "used twice" refusal / counted in rule 4's candidates when not
  reached (skip-past-wall).
- The inconsistency today: the export table (core.md:763) calls `A` alone "protected" and statement 6 calls
  `[_a = A]` "protected", but `n._a.h` is refused (rule 2: an underscore label in the path, not the start) while
  `n.A.h` is legal (alone-as-middle). Same word, opposite middle-step column. And the ruled lean "An implicit name
  ... behaves one way" (l.12148) is a ROW claim (alone == shorthand) that GENFORM-5 shows the pieces do not keep.
- Unlock: the table is the walker's spec — a row-driven walker replaces R5PATCH11-style text patches (each future
  label ruling is one row edit, as GRULE pins sentences today), and GRID's evaluator reads the same rows (with
  a SEPARATE hand-filled expectation per row, not derived, to keep the control independent).
  Trigger: the group-node ruling (open, core/labels/rule/group-node) — it is exactly "which row is an rx group";
  or a fourth label-kind piece. Effort: a table in core/labels/rule + one bullet per piece pointing at its row.

## PROBED-AND-HELD

- The record's flagged defect (l.12101, `X.Q.d` from outside answered legal): FIXED. The patched walker refuses
  `X & (X.Q.d: <5)`, X := `[n = (P SEQ Q)]` by rule 6; `X.d`, `X.n.Q.d`, `X.n.d` refused alike; `X := [n = Q]`,
  `X := Q SEQ "!"` refused (`genform/grid.out`). It matches export statement 3 and the ruling's "From outside it
  exports nothing".
- My own evaluator, written from core/labels/rule/alone-as-middle, paths rules 1-6, export statements 2/3/6/7,
  agreed with the model on 55 of the 72 path cells (14 disagree: GENFORM-1, -2, -3, -4, -7; 2 undecided by the documents: GENFORM-5; 1 right answer by the loaded engine's generic message, `[n = (P SEQ Q SEQ [a = Q])] & (n.Q.d: <5)`) (`genform/cells*.txt`, all 2- or 3-part definitions, min
  witness length 3 chars `7,3`). Among them: pure-alone inside (`n.Q.d`, `n.P.d` legal; `n.d` refused naming
  both), starts (`Q.d`, `P.d`), used twice under the prefix (`[n = (Q SEQ Q)]`, step and start refused), nested
  written label then a gate (`n.m.Q.d`, `n.Q.d` skipping m legal; `n.m.d` refused naming `n.m.Q.d`), a gate inside
  a used binding (`n.Y.Q.d` refused, rule 6), blanks and private labels as walls, `[_n = ..]` as the start,
  `&` and `/${P}${Q}/` holes (alike), and from outside through a written label (`X.n.q.d`, `X.d` legal). The
  disagreements are as listed. The 9 kind cells (`genform/cells3.txt`) are GENFORM-8's.
- Sabotage plants (LIGHT, own dir): q10 -> READINGS11 caught; q11 -> GRID caught (sentence pin); q15 -> GRID and
  ERRSWEEP11 caught (but see GENFORM-6 on how). Each ends with a `predfold1125_model: 15 checks, N failed` line and
  no traceback (`genform/plant_q1[015].out`). q12 not run (I made no full run with SUCCDUMP; SUCCESSOR11 does not
  touch R-5).
- Seven one-arm mutations of R5PATCH11 and its g_eval (`genform/mutrun_*.out`): 6 move a check, 1 (the `[ok] or sub`
  filter) moves none; the table is in GENFORM-6.
- The text patch's mechanics: each `old_` asserted to occur exactly once in its function's slice; a typo in a site
  aborts loading. No silent zero or double match is possible.
- The model header's readings (docstring lines 9-23, R5PATCH11's comment) checked against the subject: `every` ->
  `occurs.none(@d, ~S)` (library.md:647, :651), the counters by `count` (library.md:615), adjacent strings refused
  (core.md:259, :273), `!!X` -> X (negation, "a reading"), nothing-found -> the never-matching rx
  (core/modules/map/access). Each has a sentence. The engine readings with NO sentence are listed as findings:
  the mixed-case drop (GENFORM-2), `n.Q.d` read as `Q.d` (GENFORM-1), parentheses (GENFORM-4), `^A` read as a
  test (GENFORM-8).
- X11[0]: flipping it off restores predfix90's three functions (the `_r5` switch); the CANARY and the R-5
  READINGS11 check (`Pz0` legal under off, `Pz1` refused under on) both need it to move, so the switch guards a
  real reversal for the outside arm. For the inside arm it reverses nothing READINGS11 can see (GENFORM-1).
- Lookbehind counts in rx text today: core.md 3, library.md 1, parked.md 0 (`(?<=` / `(?<!`): below the GENFORM-9
  trigger.

CRITIC COMPLETE
