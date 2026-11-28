# Lane predfix114 — review r114's ruled dispositions applied to the predicate documents

Plan row [COND-FAMILY], DESIGN ONLY. Branch lane/predfix114, cut from lane/pred-rev28 at b935b91b6. The review is
filed as docs/dev/reviews/2026-11-28-r114-predfold1129.md, with the critics' texts, the verify runs and the probe kit
in the directory beside it, and a line in docs/dev/reviews/INDEX.md.

## STATE AT HANDOFF

OWED: none

- Rulings file: three entries, R-1 (list-opens-one-step ruled), R-2 (a list that passes nothing ruled), R-3
  (branch-in-loop ruled "error for now"). The last entry applied is R-3. The record entries for R-1..R-3 were on
  lane/pred-rev28 after this lane's cut; the lane took the manager's three commits (27a041a8a, 464414cce, 4b2a952b3)
  by cherry-pick, unchanged, so that the rulings items can cite their titles (lint L4). The record itself was not
  edited by the lane.
- `pred_doc_lint` failed 0; `make -s test-plan-lint` and `make -s test-doc-lint` green; the model green (lines in
  EVIDENCE AND COMMANDS).
- Not done, by the dispositions: F9 (PLAN, one sentence later); F20's retirement of one-use-read into binding-prefix
  (PLAN); F21's lint clause (PLAN: a clause in scripts/pred_doc_lint.py refusing a blank line inside a bullet; not
  edited here, scripts/ is out of scope).

## FINDINGS APPLIED

One entry per finding: what was done, where, which check covers it.

- F1 (FIX-NOW, by the owner's correction on stacked labels). Stacked labels are ordered steps; the label directly on
  a crossing is the gate. Re-derived and re-run: the hub core/labels/rule (his words; line 3 read today), gates,
  stacked-chain (rewritten), argument-place, argument-door, caller-label, sent-over-body-label (`x.h` an error, `x.p.h`
  legal), kinds (a row for a label above a label), shorthand-outside and argument-default (`pub.p.A.h`). Per his
  particulars: `x.h` an error and `x.p.h` legal; `n.d` over `[n = [m = P]]` an error, `n.m.d` and `m.d` legal;
  `Y.c.p.h` an error, `Y.c.p.a.h` legal; `Y.c.a.h` printed as a compile error naming the full path; `Y.a.h` legal.
  argument-place's details entry says the manager's telling with argument-is-gate ("becomes legal, as a full path
  that skips nothing") was wrong, the five ruled lines standing. The withdrawn readings are WITHDRAWN items in
  `readings:` (gates, argument-place, caller-label twice, sent-over-body-label twice, stacked-chain in part).
  Checks: RULE114, SWEEP114, ERRSWEEP114, STALE114.
- F2 (FIX-NOW). library.md lib/control/when: `when.h` reads one full path twice, the last. STALE114; rulings items
  marked REVISED in library_details.
- F3 (FIX-NOW). core/labels/paths/binding-prefix, the line "Placed in two branches, the branch taken". RULE114, TWIN114.
- F4 (FIX-NOW). binding-prefix, the line "Read before the only placement": decided by running the explicit-label twin
  (legal; every text FAILS, the label read as it stands, unset). TWIN114 (a hand-written twin, three modes equal).
- F5 (FIX-NOW). binding-prefix, the lines "Placed twice in a body, the group question" (last-placement line 4) and "An
  optional second placement"; the model's fallback refuses loudly (`FALLBACK114:`). RULE114, LOUD114, ERRSWEEP114.
- F6 (PLAN, owner question group-over-hole). core/labels/rule/group-node: the sentence marked a reading; both
  readings printed and run. OTHER114.
- F7 (PLAN, owner question gate-beside-direct-branch). core/labels/rule/one-path: a bullet and the line "A gate beside
  a direct target, across `|`"; the other reading run (switch BRANCH114). OTHER114.
- F8 (PLAN). Under OWNER QUESTIONS LEFT.
- F9 (PLAN). Not touched.
- F10 (PLAN). Under OWNER QUESTIONS LEFT.
- F11 (DOC). core/labels/rule/list-over-label, the line "Under an unnamed list, read in the body"; first printed as
  his lean, then ruled with list-opens-one-step line 3. RULE114.
- F12 (FIX-NOW). core/labels/export/named-list: the reason re-derived (parts labelled on their uses hold `h` behind
  gates); the line "A labelled literal" printed as the manager's reading, run by the in-force engine (the walker parses
  no named list: a known limit). SWEEP114.
- F13 (DOC). argument-place's bullet on `[dd = rx]` marked the manager's derivation; nested-scope Example 3's reason.
  ERRSWEEP114.
- F14 (NOTED). Nothing to do here; the manager tells it with the correction.
- F15 (DOC). named-list: "nothing else" read as nothing else bare, the manager's reading.
- F16 (FIX-NOW). The paths line, flow, binding-prefix's pointers, the errors table (three now-legal clauses removed,
  a gate row and a two-full-paths row), argument-door's `W.h`/`pair.d`/`list_of.h`, one-path's count of full paths.
  STALE114.
- F17 (FIX-NOW). A 2026-11-28 rulings item in every piece each 2026-11-28 owner entry tags (45 tags); REVISED,
  REVERSED, WITHDRAWN and CORRECTED marks on the items the rulings moved (the six the review named and the others STALE114 found); status dates of skip-past-wall, one-use-read,
  export-list, list-over-label, sent-over-body-label. TAGS114, STALE114.
- F18 (FIX-NOW). kinds: the placed-path row cites the manager's reading of his line 5 of part-of-argument.
- F19 (FIX-NOW in part, rest NOTED). Refusals name every way in ("write `a.dd.g` or `dd.g`"; NAMEBOTH114); nested-scope
  Example 3's reason no longer lists a parameter as a start while refusing one. ERRSWEEP114 (MSG114).
- F20 (FIX-NOW; retirement PLAN). binding-prefix's statement names the `&` exception; two pointers shortened. SWEEP114.
- F21 (FIX-NOW; lint clause PLAN). Blank lines inside bullets joined: library occurrences, placed-part, one-path.
  pred_doc_lint.
- F22 (PLAN). A known-limits line in predfix114_evidence/CLAUDE.md.
- F23 (PLAN). A known-limits line.
- F24 (FIX-NOW in the model). A crash is reported `CRASH`; the F24 program refuses `FALLBACK114:`. LOUD114.
- F25, F26, F27 (PLAN). One joint parked note, parked/ideas/label-rules-one-form.
- F28 (NOTED). Nothing to do here.

Beyond the findings, from the rulings file: list-over-label RULED and rewritten (R-1, with his example
`[a = [(=) = [p = rx]]]` printed from outside and inside); a list that passes nothing a compile error (R-2,
list-over-label and export-list); branch-in-loop (R-3): one-path's bullet, its error line and the array-form line,
and parked/ideas/branch-last-pass with its run (equal to the record's MANAGER run). RULE114, OTHER114.

## MANAGER READINGS TESTED

- `k.a.h` over `[k = [c = B([a = A])]]` stays legal: `k` is the upper label, the path does not enter the call (run,
  printed; derived from the correction, not asked).
- In the sender's text a path that names the call's label passes the place's gate: `pub.p.A.h`, `c.p.a.h`, `B.p.a.h`
  (run; derived).
- Three stacked `[n = [m = [k = P]]]`: `k` is the gate, `n.k.d` skips `m` only (run, marked a reading).
- `[dd = rx]`: `rx.d` a compile error, the place named by `dd` only (F13; run, marked the manager's derivation).
- A labelled literal under a named list may be skipped (F12; run by the in-force engine only).
- The group around a hole read as a group over rx text holding A's use (F6; printed, the other run).
- Gate beside a direct target across `|` legal, the branch taken (F7; printed, the other run).
- The explicit-label twin as the meaning of a body placing a name twice or reading before its only placement
  (last-placement 2; TWIN114 against hand-written twins).
- The withdrawn readings run as the controls: equal names of one gate (X114 off), the gate reading of
  list-over-label (LISTLEAN114 "gate"), the branch of the last pass (LOOPALT114 "last").

## ANSWERS CHANGED

Printed three-mode and compile-error lines of the base files at b935b91b6 against the tip, keyed by program: 13
programs moved, 12 from answers to compile errors and 1 from a compile error to answers. No legal line's answers
moved. `[pub = B([A = A])] & (pub.A.h: <5)` is printed at two sites (shorthand-outside, argument-default): 14 lines.
Prose reads that moved: `when.h`, `W.h`, `pair.d`, `list_of.h` from errors to the last mention (F2, F16); `B2.h`
from legal to an error (his answer). Every other changed line is new (19 three-mode keys added, SWEEP114).

From answers to compile errors (12 programs):

- core.md `[n = [m = P]] & (n.d: <5)`
  - old: The first name: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[n = [m = P]] & (n.d: <5)`, P := `/(?<d>\d)xx/`): rule 4
  - new: The first name, the gate skipped: modes: a compile error (`[n = [m = P]] & (n.d: <5)`, P := `/(?<d>\d)xx/`: `n.d`: a `d` sits behind a gate, which is never skipped: write `n.m.d` or `m.d` (a compile error, label-names-gate))
- core.md `X & (X.n.h: <5)`
  - old: From outside, the gate named: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6] (`X & (X.n.h: <5)`, A := `/(?<h>\d)/`, X := `[n = [m = A]] SEQ "!"`)
  - new: From outside, the upper name over the gate: modes: a compile error (`X & (X.n.h: <5)`, A := `/(?<h>\d)/`, X := `[n = [m = A]] SEQ "!"`: `X.n.h`: a `h` sits behind a gate, which is never skipped: write `X.n.m.h` (a compile error, label-names-gate))
- core.md `[n = [m = [k = P]]] & (n.d: <5)`
  - old: Three stacked, both middles skipped: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[n = [m = [k = P]]] & (n.d: <5)`, P := `/(?<d>\d)xx/`): rule 4 applied repeatedly (a reading)
  - new: Three stacked, the gate skipped: modes: a compile error (`[n = [m = [k = P]]] & (n.d: <5)`, P := `/(?<d>\d)xx/`: `n.d`: a `d` sits behind a gate, which is never skipped: write `n.k.d` or `k.d` (a compile error, label-names-gate))
- core.md `X & (X.y.c.a.h: <5)`
  - old: Two binding levels, through the call's label to the sender's: WHOLE `3xx!;` HOLDS, `7xx!;` FAILS / SEARCHED `7xx!; 3xx!;` `3xx!;`@6 / FIND-ALL `3xx!; 7xx!; 4xx!;` [`3xx!;`@0, `4xx!;`@12] (`X & (X.y.c.a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`, Y := `[c = B([a = A])] SEQ "!"`, X := `[y = Y] SEQ ";"`)
  - new: Two binding levels, through the call's label to the sender's, the place skipped: modes: a compile error (`X & (X.y.c.a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`, Y := `[c = B([a = A])] SEQ "!"`, X := `[y = Y] SEQ ";"`: `X.y.c.a.h`: a `a` sits behind a gate, which is never skipped: write `X.y.c.p.a.h` (a compile erro
- core.md `B([a = A]) & (B.a.h: <5)`
  - old: The macro's name over a label the sender writes: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B([a = A]) & (B.a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`)
  - new: The macro's name over a label the sender writes, the gate skipped: modes: a compile error (`B([a = A]) & (B.a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`: `B.a.h`: a `a` sits behind a gate, which is never skipped: write `B.p.a.h` (a compile error, label-names-gate))
- core.md `Y & (Y.c.a.h: <5)`
  - old: Through the call's label: WHOLE `3xx!` HOLDS, `7xx!` FAILS / SEARCHED `7xx! 3xx!` `3xx!`@5 / FIND-ALL `3xx! 7xx! 4xx!` [`3xx!`@0, `4xx!`@10] (`Y & (Y.c.a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`, Y := `[c = B([a = A])] SEQ "!"`)
  - new: Through the call's label, the place skipped: modes: a compile error (`Y & (Y.c.a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`, Y := `[c = B([a = A])] SEQ "!"`: `Y.c.a.h`: a `a` sits behind a gate, which is never skipped: write `Y.c.p.a.h` (a compile error, label-names-gate))
- core.md `Y & (Y.c.p.h: <5)`
  - old: Through the call's label and the body's: WHOLE `3xx!` HOLDS, `7xx!` FAILS / SEARCHED `7xx! 3xx!` `3xx!`@5 / FIND-ALL `3xx! 7xx! 4xx!` [`3xx!`@0, `4xx!`@10] (`Y & (Y.c.p.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`, Y := `[c = B([a = A])] SEQ "!"`): `p` and `a` stacked names of one spot
  - new: Through the call's label and the body's, the sender's skipped: modes: a compile error (`Y & (Y.c.p.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`, Y := `[c = B([a = A])] SEQ "!"`: `Y.c.p.h`: a `h` sits behind a gate, which is never skipped: write `Y.c.p.a.h` (a compile error, label-names-gate))
- core.md `[k = [c = B([a = A])]] & (c.a.h: <5)`
  - old: The call's label: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[k = [c = B([a = A])]] & (c.a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`)
  - new: The call's label, the place skipped: modes: a compile error (`[k = [c = B([a = A])]] & (c.a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`: `c.a.h`: a `a` sits behind a gate, which is never skipped: write `c.p.a.h` (a compile error, label-names-gate))
- core.md `B1(A) & (B1.p.h: <5)`
  - old: A list above the body's label, the gate named: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B1(A) & (B1.p.h: <5)`, A := `/(?<h>\d)/`, B1(rx) := `/${[(=) = [p = rx]]}xx/`)
  - new: The body's label under the list, its read: modes: a compile error (`B1(A) & (B1.p.h: <5)`, A := `/(?<h>\d)/`, B1(rx) := `/${[(=) = [p = rx]]}xx/`: `B1.p.h`: no label `p` is reached from `B1` (a compile error: a list is no step of a path, list-opens-one-step))
- core.md `B1(A) & (B1.p: <5)`
  - old: The body's label under the list: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B1(A) & (B1.p: <5)`, A := `/(?<h>\d)/`, B1(rx) := `/${[(=) = [p = rx]]}xx/`)
  - new: The body's label under the list: modes: a compile error (`B1(A) & (B1.p: <5)`, A := `/(?<h>\d)/`, B1(rx) := `/${[(=) = [p = rx]]}xx/`: `B1.p`: no label `p` is reached from `B1` (a compile error: a list is no step of a path, list-opens-one-step))
- core.md `Rs(x:, A) & (x.h: <5)`
  - old: A sent label above the body's label: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`Rs(x:, A) & (x.h: <5)`, A := `/(?<h>\d)/`, Rs(l:, v) := `/${[l = [p = v]]}xx/`)
  - new: A sent label above the body's label, the gate skipped: modes: a compile error (`Rs(x:, A) & (x.h: <5)`, A := `/(?<h>\d)/`, Rs(l:, v) := `/${[l = [p = v]]}xx/`: `x.h`: a `h` sits behind a gate, which is never skipped: write `x.p.h` (a compile error, label-names-gate))
- core.md `[pub = B([A = A])] & (pub.A.h: <5)`
  - old: From outside, written out: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[pub = B([A = A])] & (pub.A.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`)
  - new: From outside, written out, through the call's label: modes: a compile error (`[pub = B([A = A])] & (pub.A.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`: `pub.A.h`: a `A` sits behind a gate, which is never skipped: write `pub.p.A.h` (a compile error, label-names-gate))

From a compile error to answers (1 programs):

- core.md `B1(A) & (B1.h: <5)`
  - old: A list above the body's label: modes: a compile error (`B1(A) & (B1.h: <5)`, A := `/(?<h>\d)/`, B1(rx) := `/${[(=) = [p = rx]]}xx/`: `B1.h`: a `h` sits behind a gate, which is never skipped: write `B1.p.h` (a compile error, label-names-gate))
  - new: A list above the body's label: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B1(A) & (B1.h: <5)`, A := `/(?<h>\d)/`, B1(rx) := `/${[(=) = [p = rx]]}xx/`)

## OWNER QUESTIONS LEFT

Each with its slug, its program, and the piece where both readings are printed. Conflicts found under the STOP rule:
none (no disposition contradicts the record's ruled words; the one telling found wrong, `Y.c.a.h`, is the
correction's own particular).

- gate-beside-direct-branch (r114 F7). `[n = (P | /a(?<d>\d)/)] & (n.d: <5)`, P := `/(?<d>\d)/`. Printed: legal,
  the branch taken (3 HOLDS, a3 HOLDS, 7 and a7 FAIL). Other: a compile error naming `n.P.d`, RUN. Piece
  core/labels/rule/one-path.
- group-over-hole (r114 F6). `/(?<g>${A})x/ & (g.h: <5)`, A := `/(?<h>\d)/`. Printed: `g.h` an error, `g.A.h` the
  read. Other: the group a label on the use (`[g = A] SEQ /x/ & (g.h: <5)` legal, 3x HOLDS, 7x FAILS), RUN. Piece
  core/labels/rule/group-node.
- sent-over-body-label, his yes on the read put back to him (his correction). `Rs(x:, A) & (x.h: <5)`, Rs(l:, v) :=
  `/${[l = [p = v]]}xx/`. Printed: `x.h` an error, `x.p.h` legal. Piece core/labels/rule/sent-over-body-label (open
  until his yes; the withdrawn equal-names reading is in its details entry).
- reference argument placed twice (r114 F8, slug to be named by the manager). The caller's reference argument used
  twice: core/operators/bindings/reference-call keeps "used twice ... an error at the call"
  while last-placement reads the last placement. Not printed both ways (PLAN).
- the caller's shorthand when the body places only a path (r114 F10). `Y(isodate) & (isodate.year: ..)`,
  Y(date) := a body placing `date.year`. Undecided; the engine refuses. Not printed both ways (PLAN).
- branch-last-pass, "for now" (R-3). `[n = rx.repeat([a = /(?<d>\d)/] | [b = /x(?<d>\d)/], min = 1, max = _)] &
  (n.d: < 5)`. Ruled an error for now; the other reading (the branch of the last pass: x73 HOLDS, 3x7 FAILS) RUN and
  parked, parked/ideas/branch-last-pass; trigger "a token loop that wants the last item's value".

## EVIDENCE AND COMMANDS

- `timeout 300 python3 -I scripts/pred_doc_lint.py` -> `pred_doc_lint: checks passed 10817, failed 0`.
- `make -s test-plan-lint`, `make -s test-doc-lint`: green (run at the tip before the last commit).
- `PREDFIX114_SUCCDIR=<empty scratch dir> timeout 12000 python3 -I -B docs/dev/lanes/predfix114_evidence/predfix114_model.py`
  from the worktree root -> `predfix114_model: 10 checks, 0 failed` (committed as `predfix114_model.out`).
  SUCCESSOR114: predfold1129 re-run in full and, through it, the 23 models before it: 24 models, 108 reds, every red
  declared by its own FAIL-line key in `predfix114_succ_decl.tsv`; no traceback. predfold1129 itself is red on
  SWEEP129, ERRSWEEP129 and SUCCESSOR129: its engine reads stacked labels as equal names and has no list or loop rule,
  and its declarations predate the correction; each reason is in the declaration file.
- `PREDFIX114_SABOTAGE=all PREDFIX114_LIGHT=1 PREDFIX114_SUCCDIR=<the same dir>` -> `PASS PLANTS114: 18 plants,
  caught 18` (committed as `predfix114_sabotage.out`).
- Counts: SWEEP114 runs every printed three-mode line of the six documents (482); ERRSWEEP114 every printed
  compile-error line of the base files (142, of which 49 are the in-force engine's refusals behind the FALLBACK114
  prefix). Reads printed only in bullet prose are not swept: the bullets' answers here are each run by RULE114 or
  OTHER114.
- The model reads git by commit id only: START114 = b935b91b6, REC114 = 4b2a952b3. Scratch: the lane's
  `$PCREC_TMPDIR/scratch/predfix114/`.
- Known limits: docs/dev/lanes/predfix114_evidence/CLAUDE.md.
