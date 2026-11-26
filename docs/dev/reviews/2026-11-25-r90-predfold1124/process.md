# r90 predfold1124 — coordinator process record

## Freeze (2026-11-25 ~17:00)
- SUBJECT lane/pred-rev28 = 07a46f0185f9e304c762605a7d6ee68f8cc277f9 (a merge of main 3c179f98a into the lane);
  worktrees/pred HEAD = same. Fold range 0dda97065..freeze, docs/design/predicates/ (1,337-line diff).
- main HEAD at freeze 3c179f98a; decisions.md/plan.md last touched cb1fb59a2 (both on branch and main).
- Record: COND-FAMILY.md at freeze, range 10136..10540; QUOTES check pins 172930848 and db8382c63 (freeze adds 43
  lines after 172930848: the R-1, R-2 entries).
- Doc commits after the lane's evidence: 3bed07409 (the manager's close, "two rulings items cited") adds 1 line to
  core_details.md and 1 to library_details.md.

## Evidence re-run (coordinator, blind to critics)
- LIGHT/plant run in clone R/tree: PREDFOLD1124_SABOTAGE=all + LIGHT=1: 67 s, "20 plants, 1 not caught" (p17
  SUCCESSOR): MY invocation (LIGHT=1 inherited by the heavy plant, so SUCCESSOR skipped). Not a subject finding; but
  the runner silently honours an inherited LIGHT for its HEAVY plant (it prints NOT CAUGHT, so loud). Note only.
- Full run in clone: 113 s, "20 checks, 1 failed (SUCCESSOR)": [predfold1123 QUOTES UNDECLARED; predspot FSWEEP
  TEXT CHANGED; predfix83 SWEEP TEXT CHANGED; predfix83 UNMARKED TEXT CHANGED]. Committed .out: 0 failed.
  - predspot/predfix83: declared FAIL lines carry line numbers (core_details.md 419->420, 1141->1142) shifted by
    the manager's close commit 3bed07409 after the evidence ran. => evidence RED at the freeze (r77 rule: a finding).
  - predfold1123 QUOTES reads the LIVE branch `lane/pred-rev28` (not pinned); missing in the clone (no local branch).
    Added the branch to the clone; worktree run pending to classify.
- pred_doc_lint.py at freeze: 8811 passed, 0 failed (0.2 s).
- Worktree run (worktrees/pred, freeze HEAD): "20 checks, 1 failed (SUCCESSOR)": the 3 line-number reds only;
  predfold1123 QUOTES green there (reads the live branch). Worktree has an unrelated dirty docs/dev/pred/journal.md
  (the predicate manager's; not touched).

## Agents
| agent | model | launched | ended | state |
|---|---|---|---|---|
| RULING critic | opus | ~17:27 | ~17:38 (11 min) | file complete, CRITIC COMPLETE; final reply undeliverable (expected) |
| MODES critic | opus | ~17:27 | ~17:39 (12 min) | complete |
| FIXIND critic | opus | ~17:27 | ~17:39 (12 min) | complete |
| NAMEGRID critic | opus | ~17:27 | ~17:40 (13 min) | complete |
| CHECKS critic | opus | ~17:27 | ~17:55 (28 min) | complete (heavy mutation harness, 125+125 mutants) |
| verifier | opus | ~17:56 | ~18:07 (12 min) | verify.md complete, V1-V13 |
No resends, no nudges, no stalls. All six final replies "ended without delivering a report": the files were the delivery.
Blinding: no leak noticed; the R/tree clone holds denied files (needed by SUCCESSOR, which reads reports); critics were
told to read only the evidence dirs there. Not audited per critic.

## Per lens
- RULING: 9 findings; verified 1 PARTLY (RULING-2), RULING-9 one sub-claim refuted; rest held/inline. Ruling table delivered.
- MODES: 4; MODES-2/3 held (V1/V6); overlaps FIXIND/RULING on A8, insert-table B1.
- FIXIND: 12; FIXIND-9 REFUTED; FIXIND-3/6 PARTLY; FIXIND-1/10 unique (base sentences no mark reached).
- NAMEGRID: 12; all held except -10 and -11.3 PARTLY; produced most answer-level cells (A2-A7).
- CHECKS: 11; all held (4 re-verified V13; rest on the critic's own drills, not re-run); C1 = coordinator's pre-brief finding.
Overlaps: A8 (3 lenses), B1 (3), A1 (2), A7 (2), B3 (2).
Time: setup ~25 min (evidence re-runs 2 min + 67 s + 2 min), critics ~28 min wall, verify 12 min, draft ~15 min.

## Process observations
- The evidence's plant runner with `=all` inherits LIGHT=1 into the HEAVY plant (p17): my own invocation produced a
  spurious NOT CAUGHT. COMMON then warned critics. Loud, not silent, so no finding.
- A shared clone at the freeze lacks local branch refs; an older model reads `lane/pred-rev28` by name. Adding the
  branch to the clone fixed it; worth a line in the skill (r83's "shared no-checkout clone" note).
- The probe kit (exec the model up to its first check, X9 switch) took ~5 min to build and every lens used it; ~0.5 s per call.
- Freeze drift: 9 owner-record commits landed on the lane mid-round (not-test/drop-not/all-DFA goal); hand-mapped, none
  touched the fold's rulings.

## Proposed changes
1. Skill §3 (design mode, committed evidence): "When the round's tree is a shared clone, create the subject's branch ref
   in it (`git -C R/tree branch <branch> <freeze>`): older models read branches by name (r90: predfold1123 QUOTES)."
2. Skill §4 name-grid row: "Give the lens a probe that runs ONE program through the evidence engine, and ask for depth
   >= 3, two binding levels, and a wall BELOW every kind of start (r90: 7 answer/evidence cells, none reached by the
   model's own 39-cell grid)."
3. COMMON template (design mode with committed evidence): "A verbatim-line declaration that carries document line numbers
   is a finding; the committed .out must be the delivered tip's run (r90 C1: a later one-line rulings edit by the
   manager turned the verdict red)." Also a manager-side rule: re-run the evidence after any document edit on the lane
   (the close commit 3bed07409 edited two details files after the evidence).

## Framework notes
- Five opus critics + one opus verifier on a 1,337-line fold delivered in ~55 min wall with zero resends; the
  coordinator's pre-brief re-run found the evidence red that the committed output hid, before any critic saw it.
- Fan-out by root concept (launcher's five lenses) produced low overlap except on the one root three lenses approached
  from different sides (A8); the overlap was useful (each side named a different facet).
