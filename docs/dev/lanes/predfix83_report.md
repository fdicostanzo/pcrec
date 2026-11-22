# Lane predfix83 — review r83's ruled dispositions applied; the name table

Branch `lane/predfix83`, cut from `lane/pred-rev28` at 8619d21f1; `lane/pred-rev28` NOT merged in (the rulings file
named no R-n). Design only: the six predicate documents `docs/design/predicates/{core,library,parked}{,_details}.md`,
the filed review `docs/dev/reviews/2026-11-22-r83-preddef1122.md` (+ dir, + its `NOTES.md` line), and the evidence in
`docs/dev/lanes/predfix83_evidence/`. Nothing under src/, cli/, lib/, memfn/, tests/, scripts/ touched; the record,
plan.md, decisions.md, known_issues.md and docs/dev/pred/ were not edited. The task list: the record entry
"2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on
default-export (no owner words)".

## STATE AT HANDOFF

- STATE: done.
OWED: none
- Branch tip: the commit carrying this report (WIP predecessors 44afebc85, 595ff0d6b and the sabotage
  commit after them).
- Rulings file `docs/dev/lanes/predfix83_rulings.md`: EMPTY at every checkpoint (before each commit, before the
  sabotage run, before this report). Last entry applied: none (no R-n).
- `pred_doc_lint: checks passed 6797, failed 0`; `make -s test-plan-lint` clean (EVIDENCE AND COMMANDS).
- The model: `predfix83_model: 25 checks, 0 failed`; 25 plants, 0 not caught, no traceback.
- FOR THE MANAGER: `lane/pred-rev28` moved during this lane (8619d21f1 to 77c7ac345, record + journal + wake only):
  the record now holds "2026-11-22 OWNER RULING — argument-default: an error; ...", "... wrapper-export: agree (a)
  ..." and "... transform-export: yes ...". This lane applies NONE of them (no R-n named them; the brief has
  argument-default NOT RULED). Every printed sentence here still states argument-default as open, with both
  candidates run; the fold of those rulings meets the lines listed under argument-default below (the AWAITS lines,
  the seven UNDECIDED grid cells, the two "Both uses" lines, the library face of `hit`).

## DISPOSITIONS APPLIED

Every id of the dispositions entry. The filed review's closing section "APPLIED" names each landing in full.

| id | state | where it landed (tag; check) |
|---|---|---|
| A1 | applied | core/labels/flow (refusal line "From outside, a chain written in a binding"), core/diagnostics/errors (row); ANDTAG, AMBOUT |
| A2 | applied | core/labels/export/export-list (refusal line "Through a call that uses its argument alone"), errors (row); LISTX, LISTCALL |
| A3 | applied | core/labels/paths/argument-default (the sentence corrected, the lines "Both uses, (local)/(error)", the (error) cost across the library); TWOUSE |
| A4 | applied | core/labels/export/flat-read-outside (a reading, the line "The exported setting only"); OUTSIDE |
| A5 | applied | core/labels/paths/binding-prefix (a reading, the line "The unlabelled use"); OWNUSE |
| A6 | applied | core/labels/paths/call-prefix (statement, bullet), core/labels/export statement 3; LISTCALL |
| A7 | applied | core/labels/flow (refusal line "Bare `$h` and the index across `&`"), errors (row); ANDTAG, BAREAMB |
| A8 | applied | core/labels/paths/argument-default (the list, the reading), closed-argument (reading (a) awaits), lib/control/when, lib/search/occurrences; ARGOWN |
| D1 | applied | core_details core/labels/export `rejected:` (revived / partly in force), hole-export rulings items marked |
| D2 | applied | core/labels/flow (exception bullet; lines "One literal", "Composed"), core/holes/bare-condition/nested-scope; WITNESS |
| D3 | applied | core/labels/export statement 2 (the one statement); core/labels/paths, binding-prefix point at it |
| D4 | (i), (ii) applied; (iii) applied as the question's library face; (iv) planned | core/labels/paths (two bullets, the line "Outward, what the expression's text writes"); argument-default, lib/search/occurrences; EXPR, PARAM |
| D5 | applied | lib/modifiers/month-numbered; WITNESS (its shape) |
| D6 | applied | marks: core/patterns/atomic, export statement 3, flat-read-outside, call-prefix, export-list, binding-list, lib/control/peek, lib/records/list-of; AGREEMENT on the caveat; "(g)", "(h)" corrected |
| D7 | applied | core/labels/export statement 3 (own names), core/labels/paths/label-reference |
| D8 | applied | core/holes/labels (mark, top-level reading); TOPLEVEL |
| D9 | applied | flow, paths, two-sources, holes/labels statements; map, binding-list, closed-argument line; old-sense details readings marked; parked_details user-doc trap 25 |
| D10 | applied | core/labels/export statements 2, 5 and the filter bullet; call-prefix statement |
| D11 | applied | core/operators/statements, core/diagnostics/warnings (`pcrec.label.hidden`), parked/ideas/label-hygiene |
| D12 | applied | core/diagnostics/errors (two rows changed or added) |
| D13 | applied | core/labels/export statement 1 |
| D14 | applied | core/conditions/form (home), core/modules/binding-list (pointer) |
| D15 | NOW part applied; grid planned | core/labels/export (the `[=A]` row) |
| D16 | NOW part applied; table planned | core/labels/export/export-list (two readings); LISTCOLL |
| D17 | applied | core/labels/paths/one-use-read `ruled 2026-11-22`; flow, binding-prefix, label-reference; TOPLEVEL |
| D18 | applied | core/labels/export/export-list (bullet); LISTCOLL |
| E1 | applied | EXAMPLE compares the reason; SETAND behaviour arms |
| E2 | applied | VISIBLE bare-name top arm |
| E3 | noted | nothing changed |
| S1 | planned | not applied (a principle needs his words) |
| NAME-GRID | applied | GRID; the name table: new piece core/modules/names (`reading`) |

Not applied and why: D4 (iv), D15's grid, D16's table, S1 are PLAN by the ruling; E3 is NOTED. The flag rulings
(program-options, hole-flags) are not this lane's: no fix crossed core/patterns/flags, core/holes/flags,
core/holes/flags/in-filter or lib/builtin/options.

## MANAGER READINGS TESTED

| reading | verdict | evidence |
|---|---|---|
| A4: a read from outside sees exported settings only; a protected source no value, no `&` ambiguity | SUPPORTED as run | OUTSIDE (`pub.h` the first digit; `B.a`, B := `A & /(?<a>\d)/`, legal outside); s5 |
| A5: a binding's own name reaches unlabelled uses only; a same-named part label wins, with the warning | SUPPORTED as run | OWNUSE; s6 |
| A8: a read inside an argument beside its own group is the caller's own text, legal under both | SUPPORTED as run | ARGOWN (`occurrences(/(?<n>\d+)/ & (n: <100))`); s10 |
| D4 (i): a part label over an expression reads inside by the inside rules, exports only its text's | SUPPORTED as run | EXPR; s8 |
| D4 (ii): a macro's parameter is no part whose labels the body names | SUPPORTED as run | PARAM; s9 |
| D8: at the top nothing is outside | SUPPORTED as run | TOPLEVEL, GRID; s24 |
| D15/D16: the cross case `(=year) := isodate` a compile error for now | UNTESTABLE | the model parses no binding list left of `:=` |
| D15/D16: two lists colliding give the same label, the last mention | SUPPORTED as run | LISTCOLL; s11 |
| D2 CORRECTION 1: composed from parts used alone exports nothing, one literal its groups | SUPPORTED as run | WITNESS; s25 |

## ANSWERS CHANGED

One, carried by the A5 reading: `[a = A] SEQ A & (A.h: <5)`, A := `/(?<h>\d)/` (the new line "The unlabelled use",
core/labels/paths/binding-prefix): the old engine (preddef's) refused it ("A is used 2 times here"); the fixed
engine reads the unlabelled use. Listed in the model's ANSWERS_CHANGED; SWEEP over 236 printed lines finds no
other move under either candidate.

## WHAT MOVED

- Status: core/labels/paths/one-use-read `open idiom-confirm` to `ruled 2026-11-22` (by default-export, the record's
  closing; its 2026-11-17 point 4 named as revised). New piece core/modules/names, `reading 2026-11-22`.
- Statements changed (old text in each details history): core/labels/flow, core/labels/paths,
  core/labels/paths/call-prefix, core/labels/paths/two-sources, core/labels/paths/one-use-read, core/holes/labels.
- Restated: core/labels/export statements 1, 2, 3, 5; the hide-label warning's trigger; user-doc trap 25.
- Moved: "Some labels but not others" from core/labels/export to core/labels/export/export-list (40-line cap);
  the caveat's full wording from core/modules/binding-list to core/conditions/form.
- The line "One use, the reading" renamed "One use" (answers unchanged).

## DRAFT READINGS ADDED

All marked "(a reading)" with their ground: what "surface" means (flow); the `[=A]` row; `_` by grain; the own
names enumerated; the top level; the cross case; two lists; the part's own prefix inside a listing binding; the
hide-label trigger; month_numbered's export; the name table and its four cells (the manager's view, his AGREEMENT
quoted, record "2026-11-22 OWNER, on the two-kind view: "I agree with your interpretation. I note that captures
can have no label."").

## OWNER QUESTIONS LEFT

argument-default (open in these documents; see STATE AT HANDOFF for its ruling on the moved branch), with its
library face (do `hits`/`occurrences` export their argument's labels through the label-only `hit`). The seven
UNDECIDED grid cells, all deciding sentence core/labels/paths/argument-default "is the caller's read of that
argument's labels (`A.d` in `B(A)`, a group written in place) its own local read, legal, or a compile error?",
each A := `/(?<h>\d)/`, B(rx) := `/${rx}x/`, (local) the printed answer, (error) refused "`h` is not visible
through `A`":
- argument/one/plain `B(A) & (A.h: "3")`
- argument/one/$ `(B(A)) SEQ $A.h`
- argument/one/group `B(A) & some((A.h: "3"))`
- argument/one/index `B(A) & (A.h[1]: "3")`
- argument/seq/group `B(A) SEQ B(A) & some((A.h: "3"))`
- argument/seq/index `B(A) SEQ B(A) & (A.h[1]: "3")`
- argument/and/group `B(A) & B(A) & some((A.h: "3"))`

Also still open, untouched: capture-export, two-sources, zero-condition-binding, `(?<:x>...)` as a final
spelling, macro variables / macro types, count-several, capture-loop-value, zero-in-loop.

## EVIDENCE AND COMMANDS

- `timeout 1200 python3 -I -B docs/dev/lanes/predfix83_evidence/predfix83_model.py` (from the worktree):
  `predfix83_model: 25 checks, 0 failed` (`predfix83_model.out`). GRID: 96 cells, AGREE 89, DISAGREE 0,
  UNDECIDED 7. SWEEP: 236 printed lines. NULLABLE: 543 programs, none with a nullable loop body (the KNOWN LIMIT,
  EVID-4, stated in the header and the directory's CLAUDE.md).
- `timeout 2400 python3 -I -B docs/dev/lanes/predfix83_evidence/predfix83_sabotage.py`: `predfix83 sabotage: 25
  plants, 0 not caught by their target` (`predfix83_sabotage.out`, each plant's FAIL line, no traceback).
- SUCCESSOR re-ran preddef (22 checks, 2 failed: MARKS, UNMARKED), predfix82 (2: SUCCESSOR, MARKS), predcall (3:
  SCAN, PREDREF, DOC), predref (3: SCAN, MARKS, DOC), predbound (1: DOC), predfix77 and predarr (AssertionError,
  the `chars` body reader), predscope (3: NAMES, CLOSEDB, DOC); each red declared superseded with its FAIL line's
  digest and reason (the model's SUPERSEDED). New reds from this lane's text: preddef MARKS and UNMARKED, predfix82
  MARKS (content), predcall/predref SCAN (one more span, an export list's own `d`).
- `(cd W && timeout 120 python3 -I scripts/pred_doc_lint.py)`: `checks passed 6797, failed 0`.
- `make -s test-plan-lint`: clean.
