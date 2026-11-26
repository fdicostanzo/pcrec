# Lane predfix90 — review r90's dispositions applied to the predicate documents; the review filed

Branch `lane/predfix90`, cut from `lane/pred-rev28` at 33abd6926. Record of the dispositions: "2026-11-25 MANAGER — review r90 (predfold1124): the dispositions; no owner words" (docs/design/plan_row_bodies/COND-FAMILY.md, not edited). Design only: nothing under src/, cli/, lib/, memfn/, tests/ or scripts/ changed.

## STATE AT HANDOFF

- Tip: the commit after e5cf5a684 (the evidence ran at e5cf5a684; the tip adds only the .out files, this report and the history line) (the commit that carries this report and the .out files of the run at the tip).
- Rulings file `docs/dev/lanes/predfix90_rulings.md`: empty at every checkpoint; last entry applied: empty.
- `python3 -I scripts/pred_doc_lint.py`: `pred_doc_lint: checks passed 9061, failed 0`. `make -s test-plan-lint`: green (checks passed: 2, checks failed: 0).
- The model's last line: `predfix90_model: 26 checks, 0 failed`. Sabotage: `predfix90_sabotage: 18 plants, 0 not caught`. Mutation gate: `predfix90_mutation: 46 arms inverted, 14 plant arms deleted; failing: none`.
- Nothing stopped. One reading of mine is flagged for the manager: C3, below.

## DISPOSITIONS APPLIED

Each item's RULED text and its DONE line (commit, piece) are in the filed review, docs/dev/reviews/2026-11-25-r90-predfold1124.md. The documents' edits are in commit 5658509b4 (A1-A12, B1-B9; the B items' first pass by a helper subagent, checked here against each item's text and by the model's pins), with lint and the model run after. The evidence items C1-C9 are in predfix90_model.py at the tip.

| id | done |
|---|---|
| A1 | core/labels/rule/paths line "A public label between"; PATH10 reads a public label over a sequence (rules 1, 3, 4) |
| A2 | "rule 4 applies repeatedly" marked a reading (core/labels/rule/paths); two lines in core/labels/rule/stacked-chain (depth 3, two binding levels) |
| A3 | export statement 3 names rule 2 (a reading); core/labels/ownership "A wall one binding level up"; PATH10 walls across bindings |
| A4 | PATH10 rule 6 below a label over an expression or a hole; core/labels/paths two lines; open alone-as-middle (core/labels/rule/alone-as-middle) |
| A5 | reading (e) restricted (the line renamed "The caller's label, a start under the body's wall"); core/labels/ownership `B.a.d` line; open sent-label-wall |
| A6 | the legal-path-candidates clause (a reading); open skip-past-wall, three lines per candidate |
| A7 | his equivalence as the outside view; open equivalence-inside with both inside lines; (g) UNTESTABLE withdrawn in the details |
| A8 | argument-default narrowed to the read through `A.d`; "From outside" re-witnessed on `/${[p = rx]}xx/` with its written-out half run; the c.A ground on reading (b); open shorthand-outside |
| A9 | core/holes/labels' sentence and core/diagnostics/errors' row restated |
| A10 | the EB line live in core/operators/bindings/unspecified; the rejected item reworded |
| A11 | the terms block, "contains", the nested-macro pointer; open group-as-node (PLAN) |
| A12 | the cross-reference clause only; the unified reachability statement NOT done (PLAN, its trigger in the record) |
| B1 | core/holes/insert count row cites the ruling |
| B2 | binding-as-label `rulings:` items marked; the three pieces given a shorthand-is-callers item |
| B3 | closed-argument details marks |
| B4 | core/labels/rule: rule 2 restricts lines 4 and 5; label-in-argument's reading (c) re-grounded on reading (e) restricted |
| B5 | lib/structural/capture parent bullet; in-set readings marked |
| B6 | stale OPEN readings marked; missing `rulings:` items added (option-hole-explicit, options-reach-constants, path-rules) |
| B7 | parked/ideas/effect-form rebuttal and trigger marked the manager's |
| B8 | closed-argument's first bullet quotes him bare; reading (d) marked |
| B9 | core/patterns/flags and lib/builtin/options narrowed to the asked letter; "Inside a union" without the intersection |
| C1 | SUCCESSOR10 keys with document line numbers normalised out; the .out files re-committed at the tip |
| C2 | DOC/MARKS reds keyed by their set of MISSING lines; plant q13 |
| C3 | a red with an engine CRASH row or a crash count in its verdict is class CRASH, keyed by its crash rows, never "documents moved" (see the note below) |
| C4 | CONTROL gains identity and the five provided shorthand bodies against regexes built from their texts (flat_call), not through SHORT9; plant q7 |
| C5 | TABLE10: each ownership cell's grounds against a declared list; plant q8 |
| C6 | STACKCHAIN10 pins; NAMEGRID's stacked-chain cells decide by the ruled clauses; plant q9 |
| C7 | READINGS (b) and (d) by `refused` with keys "not visible" and "neither written"; plant q10 |
| C8 | SWEEP keyed by the full key; plant q11 reaches the moved arm |
| C9 | CANARY (plant q1); ERRSWEEP counts the 4 unread lines (declared) and lists legality changes (plant q18); per-plant expected FAIL fragment; the mutation gate over this lane's arms |

C3, my reading, for the manager: four predecessors' SWEEP reds carry an engine crash (predfix84: `TypeError` on `((0: !contains("7")) SEQ /\d/ SEQ ";")+`; preddef, predfix82, predfix83: `CRASH 2` in their verdicts). Their files are historical and cannot be fixed. Treating them as never declarable would leave SUCCESSOR10 red for good. I read "CRASH rows count as traceback class" as: a crash is its own class, keyed by its crash rows, its reason naming the crash and never "documents moved"; a new or changed crash row is undeclared and fails. If the ruling meant "never declarable", SUCCESSOR10 turns red on those four rows and nothing in this lane can green it.

## MANAGER READINGS TESTED

All eight SUPPORTED, run by READINGS10 (pasted from the run):

- SUPPORTED: (1) rule 4 applies repeatedly (A2): every GRID cell skipping two or more labels legal, its answers the built regex's (86 cells)
- SUPPORTED: (2) a label under an underscore label is not exported (A3): `X.n.h` and, a level up, `Y.c.h` refused
- SUPPORTED: (3) `n.Q.d` inside a compile error: an implicit label is a start, never a middle (A4)
- SUPPORTED: (4) reading (e) restricted (A5): the caller's label a start under the body's wall (`a.h` legal), never a licence below it (`B([a = [_x = A]]) & (a.h: <5)` refused)
- SUPPORTED: (5) sent-label-wall: the sent label above the body's blank a compile error by rule 2 (A5 i)
- SUPPORTED: (6) rule 4's candidates count only the targets a legal path reaches (A6), per operator `SEQ`, `&`, `|`: each answer that of the program with the private competitor renamed
- SUPPORTED: (7) his equivalence holds from outside and fails inside under reading (g) (A7)
- SUPPORTED: (8) the shorthand's expansion: the same READ inside the binding, parting from outside, for a labelling and a listing body (A8; the inside half compares the shorthand with the text SHORT9 rewrites it to, checks C4 names)

The (5) program is `R(x:, A) & (x.h: <5)`, R(l:, v) := `/${[l = [_ = v]]}xx/`: refused by rule 2. (8)'s inside half compares the shorthand with the text SHORT9 rewrites it to, which is C4's self-comparison. CONTROL's direct regexes for the same bodies (C4) are the independent control for that half.

## ANSWERS CHANGED

No printed answer of the starting commit moved: SWEEP, all printed lines at 33abd6926 under predfold1124's engine against the documents now, reports `moved or gone and not declared 0; declared 0`. ERRSWEEP reports `of the starting commit's lines 0 changed legality`. What changed is the ENGINE's answer on cells no printed line reached, now printed:

| program | before (predfold1124's engine) | after | by |
|---|---|---|---|
| `[n = [m = A] SEQ "!"] & (n.h: <5)` | refused | legal | A1 |
| `[n = [m = [k = P]]] & (n.k.d: <5)`, `X & (X.c.h: <5)` two levels | refused | legal | A2 |
| `Y & (Y.c.h: <5)`, X := `[_x = [n = A]] SEQ "!"`, Y := `[c = X] SEQ ";"` | legal | refused (rule 2) | A3 |
| `X & (X.ab.l: <5)`, X := `[ab = (B \| A)] SEQ "!"` | legal | refused (rule 6) | A4 |
| `X & (X.n.d: <5)`, X := `[n = ([m = P] SEQ Q)] SEQ "!"` | WHOLE `3,7!` FAILS, `7,3!` HOLDS (Q's `d`) | WHOLE `3,7!` HOLDS, `7,3!` FAILS (m's `d`) | A4 |
| `R(x:, A) & (x.h: <5)`, R(l:, v) := `/${[l = [_ = v]]}xx/` | legal | refused (rule 2, open sent-label-wall) | A5 (i) |
| `B([a = A]) & (B.a.d: <5)`, B(rx) := `/${[n = [_x = rx]]}xx/` | legal | refused (rules 5, 2) | A5 (ii) |

The canary rows (PATH10 off, then on), pasted:

- CANARY `Y & (Y.c.h: <5)`: PATH10 off legal, on refused
- CANARY `[n = [m = A] SEQ "!"] & (n.h: <5)`: PATH10 off refused, on legal
- CANARY `X & (X.ab.l: <5)`: PATH10 off legal, on refused
- CANARY `[n = [m = [k = P]]] & (n.k.d: <5)`: PATH10 off refused, on legal

## WHAT MOVED

- core/labels/rule/paths' lines "A blank label in the stack" (printed once, in core/labels/ownership) and "Through a call, a private label in the body" (to core/labels/ownership).
- "The caller's label, a start whatever the body stacks" renamed "... a start under the body's wall".
- argument-default's "From outside": now on the labelling body `/${[p = rx]}xx/` (the alone body witnessed no parting).
- Six new open pieces: core/labels/rule/{sent-label-wall, skip-past-wall, equivalence-inside, alone-as-middle, group-node}, core/labels/paths/shorthand-outside.
- The model's declared patches to predfold1124's checks (each printed by the run, 21): CONTROL rows (C4), the moved lines' tags, READINGS (b)/(d) (C7), NAMEGRID clauses (C6), FLAGS pins (B9), the union line (B9).

## OWNER QUESTIONS LEFT

Each OPEN line is its piece's heading status `open <slug>` in docs/design/predicates/core.md; the details entry in core_details.md carries both candidates' runs. The current definition and the runs, pasted from the pieces:

### sent-label-wall — [core/labels/rule/sent-label-wall]

Asked: When a body places a sent label ABOVE its own blank (`R(l:, v) := /${[l = [_ = v]]}xx/`), may the caller read through the sent label past the blank?

    The reading today: a compile error by rule 2 for now (the manager's reading): the path x, `_`, h contains the blank,
    not its start; reading (e) makes the sent label a start, never a licence to cross a wall below it. Candidates: (a)
    the compile error; (b) legal, the sent label a backdoor past the body's blank too (his "it wouldn't be affected by
    the _ as it becomes an accepted backdoor into the inner pattern", said of a blank ABOVE the sent label). They part:
    (a) refuses the program; (b) gives the answers of the body that writes the wall above the label (second line).
    The sent label above the body's blank: modes: a compile error (`R(x:, A) & (x.h: <5)`, A := `/(?<h>\d)/`, R(l:, v) := `/${[l = [_ = v]]}xx/`: the path x, `_`, h crosses the blank (rule 2, the manager's reading)).
    Candidate (b)'s answers: the wall written above the sent label: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`R(x:, A) & (x.h: <5)`, A := `/(?<h>\d)/`, R(l:, v) := `/${[_ = [l = v]]}xx/`)

### skip-past-wall — [core/labels/rule/skip-past-wall]

Asked: When one route to a skipped label's target crosses an underscore label, does rule 4's "unambiguously" count that route's target?

    The reading today: rule 4's candidates count only the targets a legal path reaches (the manager's reading; the
    inside twin of flat-read-outside's "a source it keeps protected does not exist for that read"): `n.d` reads m's
    `d` past `[_x = Q]`, per operator. Candidates: (a) legal paths only; (b) every target counts, by the existing rule
    as worded: in a sequence the last mention (Q's `d`), across `&` the ambiguous reference, across `|` the branch
    taken. They part on every operator: the first three lines are (a), the last three (b) (`[k = Q]` written public
    gives (b)'s answers).
    In a sequence, the private part last: WHOLE `3,7` HOLDS, `7,3` FAILS / SEARCHED `7,3 3,7` `3,7`@4 / FIND-ALL `3,7 7,3 4,1` [`3,7`@0, `4,1`@8] (`[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`): m's `d`
    Across `&`: WHOLE `37` HOLDS, `73` FAILS / SEARCHED `73 37` `37`@3 / FIND-ALL `37 73 14` [`37`@0, `14`@6] (`[n = ([m = P] & [_x = Q])] & (n.d: <5)`, P := `/(?<d>\d)\d/`, Q := `/\d(?<d>\d)/`): m's `d`
    Across `|`: WHOLE `3` HOLDS, `a3` FAILS, `a7` FAILS / SEARCHED `a7 a3` `3`@4 / FIND-ALL `3 a7 a4` [`3`@0, `4`@6] (`[n = ([m = P] | [_x = Q])] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/a(?<d>\d)/`): m's `d`, unset where the private branch is taken
    Candidate (b) in a sequence, the last mention read: WHOLE `3,7` FAILS, `7,3` HOLDS / SEARCHED `7,3 3,7` `7,3`@0 / FIND-ALL `3,7 7,3 4,1` [`7,3`@4, `4,1`@8] (`[n = ([m = P] SEQ [k = Q])] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`): Q's `d`
    Candidate (b) across `&`: modes: a compile error (`[n = ([m = P] & [k = Q])] & (n.d: <5)`, P := `/(?<d>\d)\d/`, Q := `/\d(?<d>\d)/`: both sides set `d`, the ambiguous reference).
    Candidate (b) across `|`, the branch taken: WHOLE `3` HOLDS, `a3` HOLDS, `a7` FAILS / SEARCHED `a7 a3` `a3`@3 / FIND-ALL `3 a7 a4` [`3`@0, `a4`@5] (`[n = ([m = P] | [k = Q])] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/a(?<d>\d)/`)

### equivalence-inside — [core/labels/rule/equivalence-inside]

Asked: Inside the binding that writes it, is `[_t = A]` the same as `[_ = [t = A]]`, so that `t.h` reads A's `h`?

    His words: "[_t = A ] is equivalent to [_ = [t = A ]]", said of rule 2. From outside the two agree (the third line).
    The reading today: no label `t` is made by `[_t = A]` (the manager's reading (g)), so inside, `t.h` is a compile
    error and `_t.h` the read. Candidates: (a) reading (g); (b) the equivalence holds inside too: `t.h` is legal, the
    answers of the first line. They part on the first two lines.
    Inside, the blank above `t`: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6] (`[_ = [t = A]] SEQ "!" & (t.h: <5)`, A := `/(?<h>\d)/`): rule 3
    Inside, his `[_t = A]`: modes: a compile error (`[_t = A] SEQ "!" & (t.h: <5)`, A := `/(?<h>\d)/`: no label `t` is made (the manager's reading (g)); `_t.h` is the read).
    From outside, both: modes: a compile error (`X & (X.t.h: <5)`, A := `/(?<h>\d)/`, X := `[_ = [t = A]] SEQ "!"`: the path crosses the blank (rule 2); X := `[_t = A] SEQ "!"` with `X.h` alike, crossing `_t`).

### shorthand-outside — [core/labels/paths/shorthand-outside]

Asked: Does "`B(A)` read through `A.d` means `B([A = A])`" cover a read from OUTSIDE the caller, through a label on the call (`pub.A.h` for `[pub = B(A)]`)?

    The reading today: the shorthand label is protected, as statement 2's implicit label is (the manager's reading
    (b)): it adds no export, so `[pub = B(A)] & (pub.A.h: <5)` is a compile error while the written-out
    `[pub = B([A = A])]` reads A's `h`. Candidates: (a) reading (b); (b) the expansion holds from outside too: the
    second line's answers. They part on a labelling body (`/${[p = rx]}xx/`) and a listing body alike.
    From outside: modes: a compile error (`[pub = B(A)] & (pub.A.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`: the shorthand label is protected: it adds no export (the manager's reading (b); open shorthand-outside)).
    From outside, written out: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[pub = B([A = A])] & (pub.A.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`)

### alone-as-middle — [core/labels/rule/alone-as-middle]

Asked: Inside a binding, may a path name a part used alone as a MIDDLE step (`n.Q.d` for `[n = (P SEQ Q)]`)?

    The reading today: a compile error (the manager's reading): the read is `Q.d`; an implicit label is a start, never
    a middle (core/labels/export statement 2). Candidates: (a) the compile error; (b) legal, `n.Q.d` read as `Q.d`
    (the third line's answers). `n.d`, skipping through the part used alone, is legal either way (the second line).
    A part used alone as a middle, inside: modes: a compile error (`[n = (P SEQ Q)] & (n.Q.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`: the read is `Q.d`; an implicit label is a start, never a middle (the manager's reading)).
    Through the part used alone, skipped: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 4,1` [`7,3`@0, `4,1`@8] (`[n = (P SEQ Q)] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`): Q's `d`, the last mention
    Candidate (b)'s answers: the read as `Q.d`: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 4,1` [`7,3`@0, `4,1`@8] (`[n = (P SEQ Q)] & (Q.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`)

group-as-node ([core/labels/rule/group-node]) is PLAN, kept open for the manager to frame; its two lines are in the piece.

## REVIEW FILED

- docs/dev/reviews/2026-11-25-r90-predfold1124.md: the draft with each PROPOSED disposition replaced by the RULED one, and a DONE line per item (30 items).
- docs/dev/reviews/2026-11-25-r90-predfold1124/: checks.md, fixind.md, modes.md, namegrid.md, ruling.md (the critics' texts), verify.md, process.md, copied verbatim from the round's scratch.
- docs/dev/reviews/INDEX.md: one line, in the r88 line's form.

## EVIDENCE AND COMMANDS

Run from the worktree (any cwd):

    timeout 3000 python3 -I -B docs/dev/lanes/predfix90_evidence/predfix90_model.py           # -> predfix90_model.out
    PREDFIX90_SABOTAGE=all timeout 3600 python3 -I -B docs/dev/lanes/predfix90_evidence/predfix90_model.py   # -> predfix90_sabotage.out
    PREDFIX90_SABOTAGE=mut timeout 1500 python3 -I -B docs/dev/lanes/predfix90_evidence/predfix90_model.py   # -> predfix90_mutation.out
    python3 -I scripts/pred_doc_lint.py; make -s test-plan-lint

- The GRID: 3050 cells, 0 disagreeing, 16 undecided (declared: the alone-as-middle family), its expected verdicts from `g_eval` (a separate evaluator over the quoted rule sentences, GRULE), each legal answer against a regex built from the stack in all three modes.
- SUCCESSOR10: predfold1124 and the fifteen models before it re-run; 55 reds, each declared in predfix90_succ_decl.tsv by class (LINE 43, MISSING 8, CRASH 4) with its key.
- Mutation gate (C9): every arm of this lane's checks inverted (each turns its check FAIL), and each plant's named arm deleted under that plant (each plant then goes uncaught). SUCCESSOR10's arms are run by plant q13 only (heavy). predfold1124's patched checks are covered by plants q7, q10 and q17, not by the gate.
- Limits: predfix90_evidence/CLAUDE.md, "Known limits".
