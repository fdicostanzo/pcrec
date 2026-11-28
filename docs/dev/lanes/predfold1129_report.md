# predfold1129 — the seven owner rulings of 2026-11-28 folded into the predicate documents

Lane predfold1129 (opus), branch `lane/predfold1129`, cut from `lane/pred-rev28` at 43bbce01f. Design only: nothing
under src/, cli/, lib/, memfn/, tests/ or scripts/ was edited. Record: docs/design/plan_row_bodies/COND-FAMILY.md,
from "2026-11-28 OWNER RULING — reference-example-checked" to the end (not edited).

## STATE AT HANDOFF

- Rulings file `docs/dev/lanes/predfold1129_rulings.md`: empty at every re-read (before each commit, before each run
  over two minutes, before this report). No entry applied; the last entry applied: none.
- `scripts/pred_doc_lint.py`: `pred_doc_lint: checks passed 10658, failed 0`.
- Model, full run at the tip (committed `predfold1129_evidence/predfold1129_model.out`):
  `predfold1129_model: 10 checks, 0 failed`. Plants: `predfold1129_sabotage.out`, 15 plants, every one caught.
- `make -s test-plan-lint` and `make -s test-doc-lint`: green (EVIDENCE AND COMMANDS).
- The strong-lean marker phrase ("(the owner's strong lean, entailed by carve-out-reading and caller-label-export; to
  be confirmed)"): 40 at 43bbce01f, ZERO now in all six documents (MARK129).

## RULINGS FOLDED

Each folded into the pieces named, its words quoted verbatim in the piece's "His words" bullet (QUOTES129 checks every
quoted span against the record at the pinned 43bbce01f), the old text kept in the details entry's history.

1. reference-example-checked — core/operators/bindings/reference: `checked(B) := B & (B.year: < 2100)` is legal (a
   pattern argument read through the parameter's name); the bare-read form and the no-gate call are compile errors.
2. named-list-body-read — core/labels/export/named-list: `N2(rx) := /${[(=h) = rx]}/ & (h: <5)` legal ("same as
   before"); with `(=)` a bare read is an error (the line N3).
3. label-names-gate — NEW piece core/labels/rule/gates ("Every crossing is a gate"), and with it core/labels/rule/paths,
   one-path, stacked-chain, skip-past-wall, alone-as-middle, kinds, ownership, export, flat-read-outside,
   core/patterns/alternation, atomic, core/operators/precedence, core/labels/paths: every crossing (a use, a call, a
   placed parameter) is a gate, never skipped; named by the label written on it, else the thing's own name; only a
   label over text written in place may be skipped; an export list is a nameless door.
4. argument-is-gate — core/labels/rule/argument-place re-written ("A placed parameter is a gate like any other"),
   argument-door, caller-label, list-over-label, forwarded-place, sent-over-body-label, core/holes/labels,
   core/labels/paths/closed-argument, call-prefix, lib/convention/argument-labels, parked/ideas/label-interface.
5. part-of-argument — NEW piece core/labels/paths/placed-part ("A path placed in a pattern"); nested-scope.
6. last-placement — core/labels/paths/binding-prefix, one-use-read, argument-default, call-prefix, lib/search/
   occurrences, lib/search/hits, lib/records/list-of: a plain read through a name placed twice reads the last
   placement written before the read.
7. same-path-last — core/labels/rule/one-path: a skip is legal when every label it could reach has the same full path
   (reads the last mention); different full paths are an error naming both; the array form is exempt from one-path,
   never from a gate.

## MANAGER READINGS TESTED

Each a reading printed as the manager's (derived from the ruled statements, not asked), RUN by the model:

- label-above-call: `[k = [c = B([a = A])]] & (k.a.h: <5)` legal (`k`, `c` stacked names of the call's gate).
- the sender's own text: `B.a.h` and `pub.A.h` for `[pub = B([A = A])]` legal (caller-label).
- stacked across a place: the body's `p` and the caller's `a` on the argument are one spot: `Y.c.p.h` and
  `B([a = A]) & (B.p.a.h: <5)` legal (OWNER QUESTIONS LEFT, question stacked-across-place).
- list-over-label printed reading: `B1.h` a compile error, `B1.p.h` legal.
- sent-over-body-label printed reading: `x.h`, `x.p.h` legal.
- forwarded-place printed reading: `Mx.h` legal through two listed places; `Mt.h` an error, `Mt.t.h` legal.
- RESPELL129, the hand judgments the engine runs for programs the reader cannot parse (each a same-meaning spelling):
  `B(A) & (B.dd.d: <100)` as `B(A) & (A.d: <100)` (the place's gate `dd` holds A), `C := B(A) & (B.dd.d: <100)` alike;
  `chars SEQ ":" SEQ chars & (chars.ch: "a")` as `... SEQ [r = chars] & (r.ch: "a")` (the last placement);
  `occurrences(/\d/) SEQ ";" SEQ occurrences(/\d/) & (occurrences.hit: "9")` as the second use labelled `o`.
- `_part129` (part-of-argument): `Y(isodate)` with `Y(date) := [y = date.year] SEQ "!"` specialized to a binding; a
  declared approximation, checked by PART129 against hand regexes.

## ANSWERS CHANGED

The census (`predfold1129_census.out`, the documents AT 43bbce01f, predfix113's engine against GATE129): 413 printed
programs (363 in base files), 120 not parsed, 227 reads judged. Legality moves: error to legal 17 in base files and 10
in details files; legal to error 13 in base files; legal reads whose spot moves 0.

Error to legal, base files (printed now as legal, each RUN; old = a printed compile error):
core.md `[n = (Q SEQ Q)] & (n.Q.d: <5)` (same-path-last), `[n = (P SEQ B(Q))] & (n.B.p.d: <5)`, `B(A) & (B.p.h: <5)`,
`B([a = A]) & (B.a.h: <5)`, `Y & (Y.c.a.h: <5)`, `[k = [c = B([a = A])]] & (k.a.h: <5)`, `pair(A) & (pair.d: <5)`,
`B(A) & (B.p.d: <5)` (argument-is-gate), `/${A},${A}/ & (A.d: <5)`, `B(A) SEQ A & (A.d: <5)` (last-placement),
`[pub = B([A = A])] & (pub.A.h: <5)` twice (the sender's own text), `B(A) & (B.dd.d: <100)` (argument-is-gate),
`checked(isodate)` (reference-example-checked); library.md `W(/(?<h>\d)/, /;(?<h>\d)/) & (W.h: "3")`,
`list_of(/(?<h>\d)/, sep = ",") & (list_of.h: "5")`. The 17th, `/(?<h>\d)/ & (h: >5)` (core.md, `late`), was
already printed legal (an inherited engine refusal, not a printed move).

Legal to error, base files (old printed legal; each now a compile error under label-names-gate, its line re-spelled
legal with EQUAL answers, declared in `predfold1129_decl.py`): the alternation, atomic and precedence lines
(`[ab = ([b = B] | [a = A])] & (ab.l: <20)` and kin, now each branch's text in place); `[n = [m = P] SEQ "!"] & (n.d:
<5)`; `[n = ([a = P] SEQ [b = Q])] & some(@n.d, <5)`; `X & (X.h: <5)` (`X.n.h`, `X.m.h` now); `X & (X.a.h: <5)`
(stacked-chain's two levels); the three skip-past-wall lines; `pub & (pub.h: <5)` twice (export); `X & (X.n.d: <5)`
(now `X.n.m.d`). Where the old program is kept it is printed as a compile error naming the gate (ERRSWEEP129).
Nested-scope's Example 3 (`B(A)`, a bare `dd` read) was re-written as the lines ex3d and ex3rx.

SWEEP129: 475 printed lines now (same 415; inherited engine refusals 52, DIFF 7, unparsed 1 = 60 inherited), 405 keys at
the start; not same and not inherited 0; moved 0 (no kept key's printed answers changed); gone 13, each declared; added
57, each RUN same. The marker grep finds ZERO in all six documents.

## WHAT MOVED

- core.md: 31 pieces changed, 2 new (core/labels/rule/gates, core/labels/paths/placed-part); library.md 4 pieces
  (argument-labels, occurrences, hits, list-of); parked.md 1 (label-interface). Every changed piece has its details
  history (the old statement verbatim where it moved).
- Statements re-written: gates (new), one-path, stacked-chain, skip-past-wall, argument-place (title too),
  caller-label, binding-prefix, one-use-read, nested-scope, reference, placed-part (new).
- Retired texts (STALE129, each present at the start, none now): "is binding-prefix's compile error", "not referenced
  unambiguously", "which no list opens", "never passes an argument", "passes nothing of", "the strong lean reads".

## DRAFT READINGS ADDED

- core/labels/paths/placed-part line 5 (the manager's): a placed path makes no implicit label (`date.year SEQ "!" &
  (year: < 2100)` an error; label it).
- caller-label: `Y.c.p.h` legal by the stacked-names reading (above), and `k.a.h` (label-above-call).
- list-over-label, sent-over-body-label: still open, each with its derived reading printed and the other RUN.
- forwarded-place: status "reading 2026-11-28", derived from argument-is-gate and label-names-gate.

## OWNER QUESTIONS LEFT

Each with BOTH readings run (OTHER129; texts typed from each reading's own words):

1. list-over-label — `B1(A) & (B1.h: <5)`, `B1(rx) := /${[(=) = [p = rx]]}xx/`. Printed: a compile error (`p` names
   the place's gate; write `B1.p.h`). Other: any list above the place opens it: legal, `3xx` HOLDS, `7xx` FAILS.
2. sent-over-body-label — `Rs(x:, A) & (x.h: <5)`, `Rs(l:, v) := /${[l = [p = v]]}xx/`. Printed: legal (`l`, `p`
   stacked on the place), `3xx` HOLDS, `7xx` FAILS. Other: the path passes `p` as a step: a compile error.
3. forwarded-place — `Mx(A) & (Mx.h: <5)` through `L2(x) := /${[(=) = x]}/`. Printed: legal, `<3>` HOLDS, `<7>`
   FAILS. Other (only Mx's own list counts): a compile error at L2's place.
4. stacked-across-place — `Y & (Y.c.p.h: <5)`, `Y := [c = B([a = A])] SEQ "!"`, `B(rx) := /${[p = rx]}xx/`. Printed:
   legal (`p` and `a` one spot), `3xx!` HOLDS, `7xx!` FAILS. Other (no stack across a place): a compile error, write
   `Y.c.p.a.h`. `B([a = A]) & (B.p.a.h: <5)` is legal under both.

No conflict between two rulings was found; nothing was left unfolded.

## EVIDENCE AND COMMANDS

Evidence: `docs/dev/lanes/predfold1129_evidence/` (its CLAUDE.md). Checks: RULE129 (30 programs), CENSUS129,
SWEEP129, ERRSWEEP129 (121 error lines), MARK129, QUOTES129 (8 bullets, 15 spans), STALE129, PART129 (5 programs x 9
texts), OTHER129 (5 readings, both run), SUCCESSOR129 (23 models: predfix113 and the 22 it re-runs, 105 reds, each
declared by its FAIL line's key in `predfold1129_succ_decl.tsv`; no traceback), PLANTS129 (s1..s15).

    timeout 300 python3 -I scripts/pred_doc_lint.py
    PREDFOLD1129_SUCCDIR=<empty scratch dir> timeout 6000 python3 -I -B docs/dev/lanes/predfold1129_evidence/predfold1129_model.py
    PREDFOLD1129_SUCCDIR=<that dir> PREDFOLD1129_SABOTAGE=all PREDFOLD1129_LIGHT=1 timeout 6000 python3 -I -B docs/dev/lanes/predfold1129_evidence/predfold1129_model.py
    PREDFOLD1129_CENSUS=1 timeout 1200 python3 -I -B docs/dev/lanes/predfold1129_evidence/predfold1129_model.py
    make -s test-plan-lint ; make -s test-doc-lint ; scripts/lanecheck

Re-run of the in-force models: predfix113 in full at the tip (via SUCCESSOR129), every red declared with its FAIL-line
text in `predfold1129_succ_decl.tsv`; the 14 reds new since predfix113's declarations carry this lane's reason.
