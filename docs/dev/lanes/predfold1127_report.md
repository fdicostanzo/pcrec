# Lane predfold1127: one-path and gate-beside-label folded (DESIGN)

Branch lane/predfold1127, cut from lane/pred-rev28 at 637a5e79c. Design only: nothing under src/, cli/, lib/,
memfn/, tests/ or scripts/ was edited. The rulings are the record entries of 2026-11-27 in
docs/design/plan_row_bodies/COND-FAMILY.md ("OWNER RULING — gate-beside-label: error" and "OWNER RULING —
one-path: "yes all five"", with his proposal and his remark on arrays).

## STATE AT HANDOFF

- OWED: none
- The rulings file `docs/dev/lanes/predfold1127_rulings.md` was re-read before each commit, before each run over two
  minutes and before this report. It stayed empty: no entry was applied (last entry: none).
- Branch tip: the commit carrying this report (see EVIDENCE AND COMMANDS for the lane's commits).
- pred_doc_lint: `checks passed 10099, failed 0` (WARN L7 file soft caps only). `make -s test-plan-lint`: green.
- Model: `predfold1127_model: 13 checks, 0 failed` (full, SUCCESSOR1127 included); sabotage: `PASS PLANTS1127: 15 plants, caught 15` (one per check, two each for READINGS1127 and QUOTES1127).
- Printed reads moved to a compile error: 8, each with a full-path or labelled line keeping its old answers.
- Owner questions left: 2 (array-gate, body-own-name).

## RULINGS FOLDED

- **one-path** ("yes all five"): a new ruled piece, core/labels/rule/one-path, beside core/labels/rule/paths.
  - The statement as asked: "a step in a path may be skipped only when exactly one label of that name is visible
    from the start." His five lines are quoted verbatim, with his proposal sentence and, as the principle, his
    "Skipping labels is about efficiency in total clarity."
  - It AMENDS rule 4's "unambiguously" (2026-11-23) for skipped reads. core/labels/rule/paths restates rule 4 with
    a one-path summary in place of the old "'Unambiguously' is the existing rule ..." quote; reading (f) is marked
    AMENDED in its details entry.
  - core/labels/rule/kinds: the skippable cells of the written-label, part-used-alone and group rows cite one-path.
  - core/labels/flow: the last mention decides a read that skips nothing; a read that skips a step to such a name
    is a compile error asking for the full path.
  - Line 5 closes gate-twice-scope: "more than once" is counted under the path's start (alone-as-middle's
    "Two uses, one under the read's prefix" loses "a marked reading").
- **gate-beside-label** ("error"): alone-as-middle's two marked-reading bullets are removed. The line "Beside a
  written label" (`[n = ([a = P] SEQ Q)] & (n.d: <5)`) is now a compile error naming `n.a.d` or `n.Q.d`; "Beside a
  written label, the full path" (`n.a.d`) keeps its old answers. His whole answer is quoted in alone-as-middle's
  details entry; its last sentence is quoted in one-path as the principle.

## MANAGER READINGS TESTED

One-path entry:
- (a) "visible": a wall hides the labels under it, a gate leaves them visible and counted — SUPPORTED as run
  (READINGS1127 (a)).
- (b) `D2.c` and `aa.h` skip no step and keep the label flow (last mention) — SUPPORTED as run (READINGS1127 (b):
  no node between the start and either target; answers equal to the hand regexes `\d3` and `\d,[0-4]`).
- (c) the census's four reads move (`date.v`, `c.d`, `B.d`, `W.h`) — SUPPORTED, and three more move that the census
  did not parse or counted once: `B(A) & (B.d: <5)` (call-prefix, beside `c.d`), `pair(A) & (pair.d: <5)` (the
  argument at two spots, line 5), `list_of.h` (library, two spots). Of the 59 unparsed reads, 38 are still not
  parsed by this model; each is given its category, and the three whose name is written twice in the text are
  judged by hand; none moves (CENSUS1127).
- (d) the array form through a gate — a QUESTION. Both readings RUN (READ_D1127): `error` (printed, a MARKED
  reading, "The array form through a gate") and `exempt` (every setting read: the program with each gate written
  as a label equals the hand regex `(?:[0-4],\d|\d,[0-4])`; WHOLE `7,3` HOLDS, `3,7` HOLDS, `7,7` FAILS / SEARCHED
  `7,7 3,7` `3,7`@4 / FIND-ALL `7,3 7,7 1,2` [`7,3`@0, `1,2`@8]). Listed below as array-gate.

The lane's own readings, RUN:
- (e) a list alias and an argument's place count as nodes between — forced by line 4's four reads (`W.h` skips only
  aliases, `B.d` only an argument's place) — SUPPORTED (RULE1127).
- (f) one target reached directly beside one reached by a skip is two visible, a compile error. The other reading
  ("a full path to one target wins") keeps `c.d` and `B.d` legal and contradicts line 4 — both RUN (READINGS1127
  (f), switch `direct`). Its corollary is listed below as body-own-name.

Gate-beside-label entry:
- (1) any gated target under the start makes the skipped read a compile error, whether or not another legal target
  is beside it — SUPPORTED as run (`n.d` refused naming `n.Q.d` or `n.a.d`).
- (2) `g.h` over `/(?<g>${A})x/` is the same rule with no other target — SUPPORTED as run (refused naming `g.A.h`).
- (3) a private part beside a written label (`[n = ([m = P] SEQ [_x = Q])]`, `n.d`) is unchanged — SUPPORTED as run
  (legal, P's `d`, equal to the hand regex `[0-4],\d` and to MECH111).

## ANSWERS CHANGED

Each line below was legal at 637a5e79c and is now a compile error; the old answers are kept by a new or re-spelled
line written with the full path or a label (SWEEP1127 runs every one: same).
- core/labels/rule/alone-as-middle "Beside a written label" `[n = ([a = P] SEQ Q)] & (n.d: <5)`: was WHOLE `3,7`
  HOLDS, `7,3` FAILS / SEARCHED `7,3 3,7` `3,7`@4 / FIND-ALL `3,7 7,3 4,1` [`3,7`@0, `4,1`@8]; now a compile error;
  `n.a.d` carries those answers.
- core/labels/export/flat-read-outside "Across a sequence" `date & (date.v: <5)`: was WHOLE `7-3` HOLDS, `3-7` FAILS /
  SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2` [`7-3`@0, `1-2`@8]; now a compile error; `date.m.v` carries them.
- core/labels/paths/call-prefix `[c = B(A)] & (c.d: <5)` and `B(A) & (B.d: <5)` (A := `/(?<d>\d)/`, B(rx) :=
  `/${rx}-(?<d>\d)/`): were WHOLE `7-3` HOLDS, `3-7` FAILS, `3-3` HOLDS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3
  3-7 1-2 9-9` [`7-3`@0, `1-2`@8]; now compile errors; the body's own `d` is printed with A := `/(?<e>\d)/`, same
  answers.
- core/labels/paths/call-prefix `pair(A) & (pair.d: <5)`: was WHOLE `7,3` HOLDS, `3,7` FAILS, `3,3` HOLDS / SEARCHED
  `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2 9,9` [`7,3`@0, `1,2`@8]; now a compile error; `pair([x = A]) & (x.d: <5)`
  carries them.
- core/labels/paths/two-sources `B(/(?<d>\d)/) & (B.d: <5)`: was WHOLE `7-3` HOLDS, `3-7` FAILS / SEARCHED `3-7 7-3`
  `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8]; now "Through the call, both", a compile error.
- lib/convention/argument-labels "Two arguments" `W(/(?<h>\d)/, /;(?<h>\d)/) & (W.h: "3")`: was WHOLE `7;3` HOLDS,
  `3;7` FAILS / SEARCHED `x3;7 7;3` `7;3`@5 / FIND-ALL `7;3 3;7 1;3` [`7;3`@0, `1;3`@8]; now a compile error; "Two
  arguments, labelled" (`b.h`) carries them.
- lib/records/list-of "The last item, through the call" `list_of(/(?<h>\d)/, sep = ",") & (list_of.h: "5")`: was
  WHOLE `7,3,5` HOLDS, `7,5,3` FAILS / SEARCHED `x7,5 3,5` `7,5`@1 / FIND-ALL `1,5 3 5` [`1,5`@0, `5`@6]; now a
  compile error; "The last item, by a label on the argument" (`x.h`) carries them.
- lib/control/when: the prose "A name test and then both hold is one label" now reads "two through the call:
  `when.h` is a compile error"; no printed line moves.

## WHAT MOVED

- core.md: core/labels/rule/paths (statement, `see:`, the rule-4 quote, readings bullet); NEW core/labels/rule/one-path
  (8 bullets, 4 lines); core/labels/rule/alone-as-middle (two bullets, two lines); core/labels/rule/kinds (three
  cells); core/labels/flow (statement, one line); core/labels/export/flat-read-outside (bullet, two lines);
  core/labels/paths/call-prefix (bullets, five lines); core/labels/paths/two-sources (bullet, one line);
  core/labels/paths/binding-prefix (a pointer in "Counted in the text").
- library.md: lib/convention/argument-labels (bullet, two lines), lib/control/when (prose), lib/records/list-of
  (statement, bullet, two lines, an annotation dropped).
- core_details.md, library_details.md: a rulings item and a history line (the old text verbatim) for each piece
  above; the new one-path entry; alone-as-middle gains slugs gate-twice-scope and gate-beside-label, rejected
  items for gate-beside (ii), (iii) and gate-twice-scope (a), and its two marked readings marked RULED.

## DRAFT READINGS ADDED

- core/labels/rule/one-path "The array form through a gate" (`[n = (P SEQ Q)] & some(@n.d, <5)`): a compile error,
  a MARKED reading (array-gate).
- core/labels/rule/one-path readings (e) and (f) above, the manager's to confirm: aliases and argument places are
  nodes between; a direct target beside a skipped one counts as two.
- core/labels/paths/call-prefix: with an argument that also sets `d`, no path from the call names the body's own
  `d` alone (body-own-name).

## OWNER QUESTIONS LEFT

- **array-gate**: does the array form go through a gate? `[n = (P SEQ Q)] & some(@n.d, <5)` (P := `/(?<d>\d)/`, Q :=
  `/,(?<d>\d)/`). Line 2 says a part used alone is never skipped; line 3 says the array form is exempt. Printed: a
  compile error (conservative, marked). The other reading reads every setting: WHOLE `7,3` HOLDS, `3,7` HOLDS, `7,7`
  FAILS / SEARCHED `7,7 3,7` `3,7`@4 / FIND-ALL `7,3 7,7 1,2` [`7,3`@0, `1,2`@8]. Both RUN (READ_D1127). Lean: the
  error, since line 2 says "still never skipped" and his words on arrays came before the gate was asked.
- **body-own-name**: `[c = B(A)] & (c.d: <5)` with A := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/` is now a compile
  error, but no path from `c` names the body's own `d` (the argument's place has no name). The ways to reach it: a
  caller's private label on the argument (`B([_a = A])`, a wall: untested), the body labels its own group, or "a
  full path to one target wins" (reading (f)'s other side, RUN: `c.d` legal, the body's own). Lean: the body's own
  label, nothing new to rule.

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/predfold1127_evidence/` (CLAUDE.md, predfold1127_model.py, predfold1127_model.out,
  predfold1127_sabotage.out, predfold1127_succ_decl.tsv).
- Premise, before any edit: `pred_doc_lint: checks passed 10020, failed 0`; predfix111 full at 637a5e79c:
  `predfix111_model: 14 checks, 0 failed` (SUCCESSOR111: 18 models, 67 reds, all as declared).
- Model: `timeout 6000 python3 -I -B docs/dev/lanes/predfold1127_evidence/predfold1127_model.py` with
  `PREDFOLD1127_SUCCDIR=/var/tmp/pcrec-pcrec/scratch/predfold1127/succ1127`: `predfold1127_model: 13 checks, 0 failed`. SUCCESSOR1127: `19 models read, 73 reds, each against its declared key (73 declared): all as declared` (40 keys as predfix111 declared, 27 moved and 6 new, each with its reason in predfold1127_succ_decl.tsv).
- Sabotage: `PREDFOLD1127_SABOTAGE=all PREDFOLD1127_SUCCDIR=... PREDFOLD1127_LIGHT=1`: `PASS PLANTS1127: 15 plants, caught 15` (one per check, two each for READINGS1127 and QUOTES1127).
- `python3 -I scripts/pred_doc_lint.py`: failed 0. `make -s test-plan-lint`: green. `scripts/lanecheck`: DONE rc=0.
- Commits: 549ddb202, 42b1a708d (WIP), and the tip carrying this report.
