# Lane predfix86 — review r86's ruled dispositions applied to the predicate documents; review r86 filed

Branch `lane/predfix86`, cut from `lane/pred-rev28` at a05795469; `lane/pred-rev28` NOT merged in. Design only:
- the six predicate documents `docs/design/predicates/{core,library,parked}{,_details}.md`;
- the evidence in `docs/dev/lanes/predfix86_evidence/`;
- the filed review `docs/dev/reviews/2026-11-23-r86-predfold1123.md` with its directory and the NOTES.md index line.

Not touched: src/, cli/, lib/, memfn/, tests/, scripts/, the record, docs/dev/pred/, plan.md, decisions.md and
known_issues.md. Task: apply the dispositions of the record entry "2026-11-23 MANAGER — review r86 (predfold1123): the
dispositions; three errors of the manager's own brief named; no owner words", with label-hole-full folded beside A15
and closing-own-label (R1) folded where A3 lands.

## STATE AT HANDOFF

- STATE: done.
OWED: none
- Branch tip: the commit carrying this report (WIP predecessors from d79c017dc on).
- Rulings file `docs/dev/lanes/predfix86_rulings.md`: the last R-n applied is R2. Both were applied.
  - R1: closing-own-label RULED pass.
  - R2: the STOP on A2 answered; reading (c) kept and the examples re-spelled.
  The file was re-read before each commit, before each run over two minutes, and before this report.
- STOP raised once (A2 against a run: reading (c) refuses the JSON sketch's `row(_:, ..)`); answered by R2, applied.
- `pred_doc_lint: checks passed 8104, failed 0`; `make -s test-plan-lint` clean (`checks failed: 0`).
- The model: `predfix86_model: 29 checks, 0 failed`; `predfix86_sabotage: 36 plants, 0 not caught (each plant turned its target check FAIL, no traceback)`.
- FOR THE MERGE:
  - Three record entries exist only on `lane/pred-rev28`, after this lane's cut:
    - closing-own-label (commit 13fc8aa85);
    - unspecified-rule (commit 070ba04ca; cited by R2);
    - R2's own entry.
  - They are cited in `history:` lines only, because L4 cannot find a title that is absent from this worktree's
    record.
  - QUOTES reads closing-own-label's words from the record at the PINNED commit 13fc8aa85, never from a branch name.
  - Once the record carries closing-own-label, core/labels/export/arguments can take it as a `rulings:` item (its
    slug is already there, class AGREEMENT in the details), and so can core/labels/export and
    core/labels/paths/closed-argument.

## DISPOSITIONS APPLIED

Per id, where each landed, is the APPLIED section of `docs/dev/reviews/2026-11-23-r86-predfold1123.md`, filed in
this branch. In short:
- FIX-NOW, documents: A1-A15, C1-C11 and D1-D3 are applied.
  - A3 is applied as RULED (R1), not as open.
  - A2 carries R2.
- FIX-NOW, evidence: B1-B7 and B9-B12 are applied in the successor model.
  - B6 is a marking of two readings as UNTESTED.
  - The B1 fix extends to label-parameter macros: a caller's own label inside a plain argument of a label-parameter
    macro passes `_` on the spot, as a sent label does. The EXPANSION drill found that `W(_:, [a = A])` and its
    written-out `W4([a = A])` disagreed; now they agree.
- PLAN, not applied: B8, B13, G1, G2, G3, G4. A14's G1 part is also PLAN.
- NOTED: the four lessons for the guide go to main (the review's last section); not applied here.

## ANSWERS CHANGED

Printed three-mode lines (at the starting commit a05795469) whose answer or legality moved:
- `C(_:)`, C(l:) := `/(?<:${l}>\d)/ & (l: <5)` (label-omitted): it was WHOLE `3` HOLDS, `7` FAILS; it is now a
  compile error at the call (A2, reading (c)). SWEEP declares it (MOVEDX).
- `/(?<a>\d)?,(?<b>\d)?/ & ((a, b) ?: >= (5, 3))` and `/(?<a>\d)?,(?<b>\d)?/ & (($a + $b) ?: <10)`
  (optional-entry): legal before; now each is a compile error for now (A1). Their old answers are printed
  unchanged as candidate (b) of optional-entry-edges, so SWEEP's key keeps the same answers.

Legality moved for programs that were NOT printed as three-mode lines before:
- `row(_:, "msg", contains("timeout"))` (a json/members prose reading): legal, now refused (A2/R2). Re-spelled
  `row(m:, ..)`.
- `W(_:, A) & (A.h: <5)`: legal under predfold1123's engine, now refused (B1). Now printed refused.
- `B([a = A]) & (a.h: <5)` under `[_ = rx]`: refused under predfold1123's engine, now legal (A3/R1). Now printed.
- `[c = A(x:)] & (c.x: 5)`: legal, now refused (A9). Now printed in the refused line's tail.
- `when(/(?<h>\d)/, (h: <5))`: stated a compile error, now legal (A4). Printed as the user macro `W` line.
- `c := NOT (0: 5)`: legal, now refused (B5). `c := ((0: 5))` and `/\d+/ & (0: capture("n")) SEQ /x/` crashed;
  now both are refused.
- `/\d${(0: capture("n"))}/ SEQ /x/`: legal, now refused (B4).
- `B([n = /\d/]) & (n: <5)` with B(rx) := `/xx/`: refused, now legal with `pcrec.test.never`, and the read fails
  (B7).
- `A((h: <5), /(?<h>\d)/)` with A(c, B) := `B & c`: legal and matched nothing; now `3` HOLDS, `7` FAILS (B3).

## WHAT MOVED

- New pieces:
  - core/conditions/form/optional-edges (open optional-entry-edges);
  - core/conditions/form/optional-general (open optional-label-general, re-opened);
  - lib/structural/capture/in-set (open capture-in-set).
- Re-dated or re-ruled: core/holes/name, ruled 2026-11-23 (label-hole-full); core/labels/paths/closed-argument,
  ruled 2026-11-23 (closing-own-label); core/values/reads, 2026-11-23 (zero-open item).
- core/labels/export: statement 7 and statement 3's clause are in his words of closing-own-label.
- core/labels/export/arguments: the ruled sentence, plus the four-line rule marked as the manager's restatement.
- Every touched piece has a `history:` line naming review r86 and its ids. Moved `rejected:` lines went to history:
  - argument-default's middle (labelled);
  - caller-ambiguous's (b);
  - optional-entry's and label-default's "by his lean".
- The evidence model:
  - It loads predfold1123's model and adds the FIX86 extensions.
  - Checks: CONTROL, ARGLABEL, LABELPARAM, LPRULES, CLOSE, CLOSEOWN, EXPAND, OPTENTRY, EDGES, NULLPASS, CAPTURE, CAPSET, NEGATION, ZEROLOOP, ZEROBIND, ZEROOPEN, CONDARG, WHEN, NEVER, CALLNAME, PRINCIPLE, ARGSHAPES, MEANING, READINGS, SWEEP, NULLABLE, SUCCESSOR, QUOTES, DOC (29).
  - NULLPASS runs the one nullable-loop line through libpcre2 (ctypes) with a per-pass marker group and a callout.

## OWNER QUESTIONS LEFT

- capture-in-set (A13): a capture request inside a set operator; leaning: a compile error for now (the documents'
  conservative reading meanwhile). Candidate (b) lines are printed in lib/structural/capture/in-set.
- optional-entry-edges (A1): `?:` on a joint left part, a value left part or inside a group question.
  - Candidate (b) is printed. Its cost: on `,9`, the joint form HOLDS while the record's two separate entries FAIL,
    so it breaks the ruled identity.
  - Leaning: keep the edges as errors.
- optional-label-general (A1): his FLAG ("a special case ... how special"), re-opened, with his two leans as the
  standing state.
- Not asked (marked readings, conservative): blank-label-read (reading (c), kept by R2), request-in-literal (A6),
  named-label-default (A8).
- From R2, a library-design point, not a language question: the JSON sketch's filter-taking `row` refuses `_`.

## EVIDENCE AND COMMANDS

- `timeout 5400 python3 -I -B docs/dev/lanes/predfix86_evidence/predfix86_model.py` gives `predfix86_model: 29 checks, 0 failed`. The output is
  `predfix86_model.out`.
- `PREDFIX86_SABOTAGE=all timeout 9000 python3 -I -B .../predfix86_model.py` gives `predfix86_sabotage: 36 plants, 0 not caught (each plant turned its target check FAIL, no traceback)`. The output is
  `predfix86_sabotage.out`.
- `python3 -I scripts/pred_doc_lint.py` gives `pred_doc_lint: checks passed 8104, failed 0`. `make -s test-plan-lint` clean (`checks failed: 0`).
- `grep -rnE 'plan\.md:[0-9]'` over the filed review: no hits.
- Runs pasted from the model (all three modes; the model's printed lines):
      [core/labels/export/arguments] A part label written on the argument: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B([f = /\d/]) & (f: <5)`, B(rx) := `/${rx}xx/`)
      [core/labels/export/arguments] Placed twice, the last mention: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2` [`7,3`@0, `1,2`@8] (`pair([f = /\d/]) & (f: <5)`, pair(p) := `/${p},${p}/`)
      [core/labels/paths/two-sources] The first shape, read bare: WHOLE `7-3` FAILS, `3-7` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(/(?<d>\d)/) & (d: <5)`, B(rx) := `/${rx}-(?<d>\d)/`)
      [core/labels/paths/argument-default] A label written on the argument: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`B([a = A]) & (a.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${rx}xx/`)
      [core/labels/export/arguments] His isodate argument: WHOLE `2000-01-02xx` HOLDS, `2001-01-02xx` FAILS / SEARCHED `1999-12-31xx 2000-03-04xx` `2000-03-04xx`@13 / FIND-ALL `2000-01-02xx 2001-01-02xx 2000-12-31xx` [`2000-01-02xx`@0, `2000-12-31xx`@26] (`B([d = isodate]) & (d.year: 2000)`, B(rx) := `/${rx}xx/`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
      [core/labels/export/arguments] The read inside the argument: WHOLE `2000-01-02xx` HOLDS, `2001-01-02xx` FAILS / SEARCHED `1999-12-31xx 2000-03-04xx` `2000-03-04xx`@13 / FIND-ALL `2000-01-02xx 2001-01-02xx 2000-12-31xx` [`2000-01-02xx`@0, `2000-12-31xx`@26] (`B(isodate & (isodate.year: 2000))`, B(rx) := `/${rx}xx/`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
      [core/labels/export/arguments] The body using its argument alone: modes: a compile error (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`: `d` is written in A's text, not the caller's, and B uses A alone; argument-default).
      [lib/rx/repeat] A label written on the argument: WHOLE `3` HOLDS (a = `3`), `73` HOLDS (a = `3`), `37` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `37 73 4` [`3`@0, `73`@3, `4`@6] (`rx.repeat([a = rx.digit], min = 1) & (a: <5)`)
      [lib/search/hits] Bare, the caller's own: WHOLE `ax` HOLDS, `a` FAILS, `axa` FAILS / SEARCHED `a ax` `a ax`@0 / FIND-ALL `a ax ax` [`a ax ax`@0] (`hits(/a(?<g>x)?/) & (g: "x")`)
      [core/operators/bindings/label-variables] His example: WHOLE `5` HOLDS, `55` FAILS, `7` FAILS / SEARCHED `7 5` `5`@2 / FIND-ALL `5 7 56 15` [`5`@0, `5`@4, `5`@8] (`A(x:) & (x: 5)`, A(l:) := `/(?<:${l}>\d+)/`)
      [core/operators/bindings/label-variables] Placed twice, the plain read: WHOLE `7,5` HOLDS, `5,7` FAILS, `5,5` HOLDS / SEARCHED `5,7 7,5` `7,5`@4 / FIND-ALL `7,5 5,7 1,5 5,5` [`7,5`@0, `1,5`@8, `5,5`@12] (`A(x:) SEQ "," SEQ A(x:) & (x: 5)`, A(l:) := `/(?<:${l}>\d+)/`)
      [core/operators/bindings/label-variables] Placed twice, a group question: WHOLE `7,5` HOLDS, `5,7` HOLDS, `7,7` FAILS / SEARCHED `7,7 5,7` `5,7`@4 / FIND-ALL `7,5 5,7 1,2 5,5` [`7,5`@0, `5,7`@4, `5,5`@12] (`A(x:) SEQ "," SEQ A(x:) & some((x: "5"))`, A(l:) := `/(?<:${l}>\d+)/`)
      [core/operators/bindings/label-variables] Placed twice, the index: WHOLE `7,5` FAILS, `5,7` HOLDS / SEARCHED `7,5 5,7` `5,7`@4 / FIND-ALL `7,5 5,7 1,5 5,5` [`5,7`@4, `5,5`@12] (`A(x:) SEQ "," SEQ A(x:) & (x[1]: 5)`, A(l:) := `/(?<:${l}>\d+)/`)
      [core/operators/bindings/label-variables] Across `&`: modes: a compile error (`A(x:) & A(x:) & (x: 5)`, A(l:) := `/(?<:${l}>\d+)/`: both sides set x, an ambiguous reference (core/labels/flow)).
      [core/operators/bindings/label-omitted] The unspecified label: WHOLE `3!` HOLDS, `7!` HOLDS / SEARCHED `x3!` `3!`@1 / FIND-ALL `3! 7!` [`3!`@0, `7!`@3] (`A(_:) SEQ "!"`, A(l:) := `/(?<:${l}>\d)/`)
      [core/operators/bindings/label-default] Passed by name: WHOLE `5` HOLDS, `55` FAILS, `7` FAILS / SEARCHED `7 5` `5`@2 / FIND-ALL `5 7 56 15` [`5`@0, `5`@4, `5`@8] (`A2(l = x:) & (x: 5)`, A2(l = _:) := `/(?<:${l}>\d+)/`)
      [core/operators/bindings/label-default] Left out, the default `_`: WHOLE `5` HOLDS, `55` HOLDS, `x` FAILS / SEARCHED `x5` `5`@1 / FIND-ALL `5 7` [`5`@0, `7`@2] (`A2()`, A2(l = _:) := `/(?<:${l}>\d+)/`)
      [core/operators/bindings/label-kinds] A body reading its own label after placing it: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`C(x:)`, C(l:) := `/(?<:${l}>\d)/ & (l: <5)`)
      [core/operators/bindings/label-forward] Passed on: WHOLE `<3>` HOLDS, `<7>` FAILS / SEARCHED `<7> <3>` `<3>`@4 / FIND-ALL `<3> <7> <4>` [`<3>`@0, `<4>`@8] (`B(x:) & (x: <5)`, B(l:) := `/<${A(l:)}>/`, A(l:) := `/(?<:${l}>\d)/`)
      [core/operators/bindings/label-forward] Passed on across `|`: WHOLE `3` HOLDS (x = `3`), `e3` HOLDS (x = `3`), `e7` FAILS / SEARCHED `e7 3` `3`@3 / FIND-ALL `3 e7 e4` [`3`@0, `e4`@5] (`V(x:) & (x: <5)`, V(l:) := `A(l:) | E(l:)`, A(l:) := `/(?<:${l}>\d)/`, E(l:) := `/e(?<:${l}>\d)/`)
      [core/operators/bindings/label-in-argument] Sent inside the argument, `_` on the outer spot: WHOLE `<"3">` HOLDS, `<"7">` FAILS / SEARCHED `<"7"> <"3">` `<"3">`@6 / FIND-ALL `<"3"> <"7"> <"4">` [`<"3">`@0, `<"4">`@12] (`W(_:, S(body:)) & (body: <5)`, W(l:, v) := `/<${[l = v]}>/`, S(l:) := `/"(?<:${l}>\d)"/`)
      [core/operators/bindings/label-in-argument] The outer body using the argument alone: WHOLE `<"3">` HOLDS, `<"7">` FAILS / SEARCHED `<"7"> <"3">` `<"3">`@6 / FIND-ALL `<"3"> <"7"> <"4">` [`<"3">`@0, `<"4">`@12] (`W3(S(body:)) & (body: <5)`, W3(v) := `/<${v}>/`, S(l:) := `/"(?<:${l}>\d)"/`)
      [core/labels/export/arguments] A caller's label on the spot: WHOLE `2000-01-02xx` HOLDS, `2001-01-02xx` FAILS / SEARCHED `1999-12-31xx 2000-03-04xx` `2000-03-04xx`@13 / FIND-ALL `2000-01-02xx 2001-01-02xx 2000-12-31xx` [`2000-01-02xx`@0, `2000-12-31xx`@26] (`R(x:, isodate) & (x.year: 2000)`, R(l:, v) := `/${[l = v]}xx/`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
      [core/operators/bindings/label-omitted] A body placing then reading its label, passed `_`: modes: a compile error (`C(_:)`, C(l:) := `/(?<:${l}>\d)/ & (l: <5)`: the body reads `l` and `_` names nothing to read).
      [core/operators/bindings/label-default] A default naming a label: modes: a compile error (`A2() & (ts: 5)`, A2(l = ts:) := `/(?<:${l}>\d+)/`: for now the head default is `_` only).
      [core/operators/bindings/label-kinds] The reference kind in a user macro: modes: a compile error (`A(x:, /\w/)`, A(a:, B) := `B & (a: 5)`: A reads a label it never places, off limits for users).
      [core/operators/bindings/label-kinds] A path as a marked argument: modes: a compile error (`A(x.d:)`, A(l:) := `/(?<:${l}>\d)/`: a marked argument is one new name).
      [core/holes/name] A partial label-only name: modes: a compile error (`A(x:) SEQ "!"`, A(l:) := `/(?<:f_${l}>\d)/`: the name hole of a label-only group must be the whole name).
      [core/operators/bindings/label-omitted] Closed by `_`: modes: a compile error (`W(_:, A) & (A.h: <5)`, W(l:, v) := `/<${[l = v]}>/`, A := `/(?<h>\d)/`: `_` on the spot is `[_ = v]`, which closes the door through A).
      [core/labels/paths/closed-argument] The caller's own label, under a closing body: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B([a = A]) & (a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[_ = rx]}xx/`)
      [core/labels/paths/closed-argument] Closed by the macro: modes: a compile error (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[_ = rx]}xx/`: `[c = B(A)] & (c.d: <5)` alike: no `d` is exported, a compile error by the reading in core/labels/paths, a label not visible through its source).
      [core/labels/paths/closed-argument] Closed by a `_` part label: modes: a compile error (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[_p = rx]}xx/`; `c.d` and `B.d` alike; inside its binding a `_` part label is an ordinary one: the line "Statement 6", core/labels/export).
      [core/conditions/form/optional-entry] The entry `?:`: WHOLE `x` HOLDS, `3x` HOLDS, `7x` FAILS / SEARCHED `7x x` `x`@1 / FIND-ALL `7x 3x x` [`x`@1, `3x`@3, `x`@6] (`/(?<h>\d)?x/ & (h ?: <5)`)
      [core/conditions/form/optional-entry] The plain entry: WHOLE `x` FAILS, `3x` HOLDS, `7x` FAILS / SEARCHED `7x x` FAILS / FIND-ALL `7x 3x x` [`3x`@3] (`/(?<h>\d)?x/ & (h: <5)`)
      [core/conditions/form/optional-entry] The default inside the set: WHOLE `x` HOLDS, `3x` HOLDS, `7x` FAILS / SEARCHED `7x x` `x`@1 / FIND-ALL `7x 3x x` [`x`@1, `3x`@3, `x`@6] (`/(?<h>\d)?x/ & (h = "0": <5)`)
      [core/conditions/form/optional-entry] Under `NOT`: WHOLE `x` FAILS, `3x` FAILS, `7x` HOLDS / SEARCHED `7x x` `7x`@0 / FIND-ALL `7x 3x x` [`7x`@0] (`/(?<h>\d)?x/ & NOT (h ?: <5)`)
      [core/conditions/form/optional-entry] A joint left part: modes: a compile error for now (`/(?<a>\d)?,(?<b>\d)?/ & ((a, b) ?: >= (5, 3))`).
      [core/conditions/form/optional-entry] A value left part: modes: a compile error for now (`/(?<a>\d)?,(?<b>\d)?/ & (($a + $b) ?: <10)`).
      [core/conditions/form/optional-entry] Inside a group question: modes: a compile error for now (`/(?<h>\d);(?:(?<h>\d);)*/ & some((h ?: "7"))`).
      [core/conditions/form/optional-edges] Candidate (b) of optional-entry-edges, a joint left part: WHOLE `6,1` HOLDS, `5,3` HOLDS, `5,1` FAILS, `,1` HOLDS, `,9` HOLDS, `5,` HOLDS, `2,` HOLDS, `,` HOLDS / SEARCHED `5,1 ,1 6,0` `5,`@0 / FIND-ALL `5,1 5,4 ,1 2, 7,` [`5,`@0, `5,4`@4, `,1`@8, `2,`@11, `7,`@14] (`/(?<a>\d)?,(?<b>\d)?/ & ((a, b) ?: >= (5, 3))`)
      [core/conditions/form/optional-edges] Candidate (b) of optional-entry-edges, the joint: WHOLE `,9` HOLDS, `5,3` HOLDS, `,3` HOLDS, `5,9` FAILS / SEARCHED `5,9 ,9` `5,`@0 / FIND-ALL `5,9 ,9 5,3` [`5,`@0, `,9`@4, `5,3`@7] (`/(?<a>\d)?,(?<b>\d)?/ & ((a, b) ?: ("5", "3"))`)
      [core/conditions/form/optional-edges] Candidate (b) of optional-entry-edges, a value left part: WHOLE `3,4` HOLDS, `6,7` FAILS, `,4` HOLDS, `3,` HOLDS / SEARCHED `6,7 3,` `6,`@0 / FIND-ALL `6,7 3,4 ,4` [`6,`@0, `3,4`@4, `,4`@8] (`/(?<a>\d)?,(?<b>\d)?/ & (($a + $b) ?: <10)`)
      [core/conditions/form/optional-edges] The record of the same entries: WHOLE `,9` FAILS, `5,3` HOLDS, `,3` HOLDS, `5,9` FAILS / SEARCHED `5,9 ,9` `5,`@0 / FIND-ALL `5,9 ,9 5,3` [`5,`@0, `,`@4, `5,3`@7] (`/(?<a>\d)?,(?<b>\d)?/ & (a ?: "5", b ?: "3")`)
      [core/conditions/form/optional-entry] A loop that can match empty: WHOLE `x` HOLDS, `3x` HOLDS, `7x` HOLDS, `73x` HOLDS / SEARCHED `7x 3x` `7x`@0 / FIND-ALL `7x 3x x` [`7x`@0, `3x`@3, `x`@6] (`/(?:(?<h>\d)?)*x/ & (h ?: <5)`; with `:` WHOLE `x` FAILS, `3x` HOLDS, `7x` FAILS, `73x` HOLDS)
      [lib/structural/capture] Requires the label: WHOLE `x` FAILS, `3x` HOLDS (h = `3`) / SEARCHED `x 3x` `3x`@2 / FIND-ALL `x 3x x` [`3x`@2] (`/(?<h>\d)?x/ & (h: capture("h"))`)
      [lib/structural/capture] If present: WHOLE `x` HOLDS (h unset), `3x` HOLDS (h = `3`) / SEARCHED `x 3x` `x`@0 / FIND-ALL `x 3x x` [`x`@0, `3x`@2, `x`@5] (`/(?<h>\d)?x/ & (h ?: capture("h"))`)
      [lib/structural/capture] The stretch: WHOLE `12` HOLDS, `x` FAILS / SEARCHED `x12` `12`@1 / FIND-ALL `1 22` [`1`@0, `22`@2] (`/\d+/ & capture("n")`)
      [lib/structural/capture] Requested twice, the last mention: WHOLE `7,5` HOLDS (d = `5`), `7` FAILS / SEARCHED `x7,5 1,2` `7,5`@1 / FIND-ALL `7,5 1,2` [`7,5`@0, `1,2`@4] (`A SEQ "," SEQ A`, A := `[d = /\d+/] & (d: capture("d"))`)
      [lib/structural/capture] Through the label's path: WHOLE `2025-01-02` HOLDS (year = `2025`) / SEARCHED `x 2025-01-02` `2025-01-02`@2 / FIND-ALL `2025-01-02 1999-12-31` [`2025-01-02`@0, `1999-12-31`@11] (`isodate & (isodate.year: capture("year"))`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
      [lib/structural/capture] After a loop: WHOLE `3;;` HOLDS (h unset), `3;` HOLDS (h = `3`), `3;4;` HOLDS (h = `4`) / SEARCHED `3;; 3;` `3;;`@0 / FIND-ALL `3; ;` [`3;`@0, `;`@3] (`/(?:(?<h>\d)?;)+/ & (h ?: capture("h"))`)
      [lib/structural/capture/in-set] Inside a union: modes: a compile error (`/(?<h>\d)?x/ & (h: "3" | capture("h"))`; `(h: <5 & capture("h"))`, `($a: capture("h"))` and `some((h: capture("h")))` alike: for now).
      [lib/structural/capture/in-set] Candidate (b) of capture-in-set, a union: WHOLE `3x` HOLDS, `5x` HOLDS, `x` FAILS / SEARCHED `5x 3x` `5x`@0 / FIND-ALL `3x 5x x` [`3x`@0, `5x`@3] (`/(?<h>\d)?x/ & (h: "3" | capture("h"))`)
      [lib/structural/capture/in-set] Candidate (b) of capture-in-set, an intersection: WHOLE `3x` HOLDS, `5x` FAILS, `x` FAILS / SEARCHED `5x 3x` `3x`@3 / FIND-ALL `3x 5x x` [`3x`@0] (`/(?<h>\d)?x/ & (h: <5 & capture("h"))`)
      [core/filters/negation/effects] Under `NOT`: modes: a compile error (`/(?<h>\d)?x/ & NOT (h: capture("h"))`: an effect under negation).
      [core/filters/negation/effects] Under `!`: modes: a compile error (`/(?<h>\d)?x/ & (h: !capture("h"))`: an effect under negation).
      [core/filters/negation/effects] Beside a negation: WHOLE `x` FAILS, `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `7x 3x x` [`3x`@3] (`/(?<h>\d)?x/ & (h: capture("h")) & NOT (h: >= 5)`)
      [core/filters/negation/effects] In `when`'s test: modes: a compile error (`when(/(?<d>\d)/ & (d: capture("d")), /x/)`: the test reaches the guard's `NOT peek(test)`; the manager's reading).
      [core/holes/bare-condition/zero-binding] Bound alone: modes: a compile error (`c`, c := `(0: 5)`: a condition on `0` bound alone; `NOT (0: 5)` and `((0: 5))` bound alone alike, a reading).
      [core/holes/bare-condition/zero-binding] Written in place: WHOLE `5` HOLDS, `7` FAILS / SEARCHED `x5` `5`@1 / FIND-ALL `5 7 5` [`5`@0, `5`@4] (`/\d/ & (0: 5)`)
      [core/conditions/match-so-far] Two reads on one path: WHOLE `34` HOLDS, `35` FAILS, `44` FAILS / SEARCHED `x34 35` `34`@1 / FIND-ALL `34 35 34` [`34`@0, `34`@6] (`/\d${(0: "3")}\d${(0: "34")}/`)
      [core/conditions/match-so-far] A group question on `0`: modes: a compile error (`/(?<d>\d)+/ & some((0: "1"))`: `0` has no settings, so no array).
      [core/conditions/match-so-far] An index on `0`: modes: a compile error (`/(?<d>\d)+/ & (0[1]: "1")`: `0` has no settings).
      [lib/structural/capture] A request on an open `0`: modes: a compile error (`/\d${(0: capture("n"))}x/`: pattern text follows the hole, so `0` is open there; for now).
      [lib/structural/capture] A request on `0` written last: WHOLE `12` HOLDS, `x` FAILS / SEARCHED `a12` `12`@1 / FIND-ALL `1 22` [`1`@0, `22`@2] (`/\d+${(0: capture("n"))}/`)
      [core/values/reads] `$0` in a value hole: WHOLE `abab` HOLDS, `aba` FAILS, `aa` HOLDS / SEARCHED `xabab` `abab`@1 / FIND-ALL `abab cc d` [`abab`@0, `cc`@5] (`/\w+${$0}/`)
      [core/conditions/match-so-far] An argument placed beside `&`: WHOLE `ax` HOLDS, `ay` FAILS / SEARCHED `ay ax` `ax`@3 / FIND-ALL `ax ay ax` [`ax`@0, `ax`@6] (`/a/ SEQ A((0: /x/), /\w/)`, A(c, B) := `B & c`)
      [core/conditions/match-so-far] An argument placed in a sequence: WHOLE `ax` HOLDS, `ay` FAILS / SEARCHED `ay ax` `ax`@3 / FIND-ALL `ax ay ax` [`ax`@0, `ax`@6] (`/a/ SEQ A2((0: /ax/), /\w/)`, A2(c, B) := `/${B}${c}/`)
      [lib/control/when] A read in then: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`W(/(?<h>\d)/, (h: <5))`, W(a, b) := `[(=) = a] SEQ [(=) = b]`; `W(A, (A.h: <5))` with A := `/(?<h>\d)/` the same answers)
      [core/labels/export/arguments] A sent label through the macro's name: modes: a compile error (`A(x:) & (A.x: 5)`, A(l:) := `/(?<:${l}>\d+)/`: not offered for now; `[c = A(x:)] & (c.x: 5)` alike).
      [core/labels/export/arguments] Through the call, by path: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity([a = A]) & (identity.a.h: <5)`, A := `/(?<h>\d)/`, identity(x) := `/${[(=) = x]}/`)
      [core/labels/export/arguments] A part label on an argument of a list body: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity([a = A]) & (a.h: <5)`, A := `/(?<h>\d)/`, identity(x) := `/${[(=) = x]}/`)
      [core/labels/export/arguments] A read inside an argument, bare: modes: a compile error (`B(A & (h: "3"))`, A := `/(?<h>\d)/`, B(rx) := `/${rx}xx/`: `h` is not written in the caller's text; label-reference).
      [core/labels/export/arguments] A read inside an argument, with its source: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx` [`3xx`@0] (`B(A & (A.h: "3"))`, A := `/(?<h>\d)/`, B(rx) := `/${rx}xx/`)
      [core/patterns/atomic] A part label over an expression in an argument: WHOLE `25` FAILS, `13` HOLDS / SEARCHED `25` FAILS / FIND-ALL `25 13` [`13`@3] (`atomic([ab = (B | A)]) & (ab.l: <20)`, A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`)
      [core/labels/export/arguments] A binding in parentheses: modes: a compile error (`identity((A)) & (identity.h: <5)`, A := `/(?<h>\d)/`, identity(x) := `/${[(=) = x]}/`: the argument's own text writes no label, A used alone in it).
      [core/labels/export/arguments] A binding alone: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity(A) & (identity.h: <5)`, A := `/(?<h>\d)/`, identity(x) := `/${[(=) = x]}/`)
      [core/labels/export/arguments] A named list on a spot: modes: a compile error (`N(A) & (N.h: <5)`, A := `/(?<h>\d)/`, N(rx) := `/${[(=h) = rx]}/`: a parameter exports nothing the definition can see, so the list names no exported label).
      [core/patterns/alternation] WHOLE `25` HOLDS (l = `2`), `7` FAILS / SEARCHED `25` `25`@0 / FIND-ALL `25 13` [`25`@0, `13`@3] (`[ab = (B | A)] & (ab.l: <20)`, A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`)
      [core/operators/precedence] The label set beside `|`: WHOLE `25` FAILS, `13` HOLDS / SEARCHED `25` FAILS / FIND-ALL `25 13` [`13`@3] (`[ab = B | A] & (ab.l: <20)`, A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`)
      [core/principles/meaning-not-spelling] A used binding: WHOLE `1,7` HOLDS, `7,1` FAILS / SEARCHED `7,1 1,7` `1,7`@4 / FIND-ALL `1,7 7,1 1,2 9,9` [`1,7`@0, `1,2`@8] (`/(?<h>\d)/ SEQ A & (h: <5)`, A := `/,(?<h>\d)/`; the one literal `/(?<h>\d),(?<h>\d)/ & (h: <5)` WHOLE `1,7` FAILS, `7,1` HOLDS)
      [core/labels/paths/two-sources] The second shape, read bare: WHOLE `1,7` HOLDS, `7,1` FAILS / SEARCHED `7,1 1,7` `1,7`@4 / FIND-ALL `1,7 7,1 1,2 9,9` [`1,7`@0, `1,2`@8] (`/(?<h>\d)/ SEQ A & (h: <5)`, A := `/,(?<h>\d)/`)
      [core/conditions/form/value-left] A value with no label: WHOLE `x` HOLDS / SEARCHED `ax` `x`@1 / FIND-ALL `x x` [`x`@0, `x`@2] (`/x/ & ("Frank": /F.*/)`)
      [lib/json/members] The label on the data: WHOLE `{"v":"ok"}` HOLDS, `{"v":3}` HOLDS, `{"v":7}` FAILS, `{"v":"no"}` FAILS, `{"v":true}` FAILS, `{"v":"3"}` HOLDS / SEARCHED `{"v":7} {"v":"ok"} {"v":3}` `{"v":"ok"}`@8 / FIND-ALL `{"v":"ok"} {"v":7} {"v":3} {"v":"no"} {"v":"3"}` [`{"v":"ok"}`@0, `{"v":3}`@19, `{"v":"3"}`@38] (`row(v:, "v") & (v: "ok" | <5)`, the sketch above)
      [lib/json/members] A filter over two rows at the line: WHOLE `{"lo":3,"hi":7}` HOLDS, `{"hi":7,"lo":3}` HOLDS, `{"lo":7,"hi":3}` FAILS, `{"lo":3}` FAILS, `{"lo":"3","hi":"7"}` HOLDS, `{"lo":3,"x":true,"hi":7}` HOLDS / SEARCHED `{"lo":7,"hi":3} {"hi":9,"lo":8}` `{"hi":9,"lo":8}`@16 / FIND-ALL `{"lo":3,"hi":7} {"lo":7,"hi":3} {"lo":3} {"hi":2,"lo":1}` [`{"lo":3,"hi":7}`@0, `{"hi":2,"lo":1}`@41] (`row(lo:, "lo") & row(hi:, "hi") & (lo: <$hi)`, the sketch above)
      [lib/json/members] Several keys: WHOLE `{"a":3}` HOLDS (x = `3`), `{"b":3}` HOLDS (x = `3`), `{"a":7,"b":3}` HOLDS (x = `3`), `{"a":3,"b":7}` HOLDS (x = `3`), `{"a":7,"b":8}` FAILS, `{"c":3}` FAILS / SEARCHED `{"a":7,"b":8} {"a":3,"b":7}` `{"a":3,"b":7}`@14 / FIND-ALL `{"a":3} {"c":1} {"a":7,"b":8} {"b":4,"a":9}` [`{"a":3}`@0, `{"b":4,"a":9}`@30] (`row(x:, "a" | "b") & (x: <5)`, the sketch above)
      [lib/json/members] A filter inside the argument: WHOLE `{"msg":"db timeout"}` HOLDS, `{"msg":"ok"}` FAILS, `{"msg":"timeout a","msg":"ok"}` HOLDS / SEARCHED `{"msg":"ok"} {"msg":"db timeout"}` `{"msg":"db timeout"}`@13 / FIND-ALL `{"msg":"ok"} {"msg":"db timeout"} {"msg":"timeout"}` [`{"msg":"db timeout"}`@13, `{"msg":"timeout"}`@34] (`row(m:, "msg", contains("timeout"))`, the sketch above; `row(m:, "msg") & (m: contains("timeout"))` the same answers)
