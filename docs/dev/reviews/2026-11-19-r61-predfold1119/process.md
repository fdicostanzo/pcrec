# process r61 predfold1119
- setup start 22:22; freeze 2e0adc746, base 50f56b1cd = main HEAD at setup (main == base); rulings freeze: main decisions/plan commit 85c5f28e4.
- R/subject copied; R/tree mirror; predasc evidence needs GIT_DIR (git show base); with it 24/24 green.
- COORD NOTE (not briefed): predloop_model.py at the freeze: 20 checks, 9 FAIL (EXclassorder EXsub EXtwo EXlazy EXfirst EXnest EXbounded EXenumclass EXpos) — it encodes "classes descending", reversed by quantified-order. Committed evidence red at tip.
- COORD SUSPICION (not briefed): array-scope "two groups of one name in a sequence give it both settings" vs core/holes/same-name "a group through a hole ... does not count as a second group of its name".
- lanecheck/lanewatch NOT used: design mode, pre-created files + CRITIC COMPLETE marker (deadline 00:30).
- critics launched 22:26 (5, background, unnamed): RULING/RUNOWN/REACH/GENERAL opus, STALE sonnet. All returned in the launch turn (Agent results "ended without delivering a report through SubagentHandback" for all five: EXPECTED; files complete).
  RUNOWN ~7.3 min, 7 findings; GENERAL ~8.6 min, 15; RULING ~10.3 min, 13; REACH ~11.2 min, 9; STALE ~14 min, 6. No resend, no nudge, no stall.
- verification inline (all CONFIRMED were quote/text or one-call re repros): .coord/v/v.py; predloop baseline/s5/s12 rerun; quotes grepped. No verifier agent (r14 rule).
- the two COORD notes above were both found blind: predloop red (STALE-3, RULING aside); same-name vs array-scope (GENERAL-2, resolved as the label/capture namespace split, no contradiction).
- FREEZE DRIFT: lane/pred-rev28 moved to ada7386d9 (journal only). main unchanged.
- draft 22:47. No review worktree (design mode). No process left running.

## Process observations
- Root overlap: the polarity defect was found by 4 lenses, the nested-hole rx by 3. Briefs named the drill topic (bare-condition) in RUNOWN only, but REACH/RULING/GENERAL reached it from their own questions. Assigning by root concept needs the root named in the OTHER briefs as "not yours".
- The round fit easily inside the deadline: narrow one-question briefs + R/subject copies + pre-created files: all done in <15 min.
- GIT_DIR trick let an evidence script that git-shows a base commit run from a read-only mirror without repo access.

## Proposed changes
- Skill §5 (design mode): "When an evidence script reads a base commit by `git -C <its tree> show`, run it from the R/tree mirror with `GIT_DIR=<repo>/.git` (read-only object access) rather than from the worktree (r61)."
- Skill §5: "Name the root concept of each assigned drill in the OTHER briefs as excluded ('the polarity of an unset read is RUNOWN's')" (r61: 4 lenses on one root).
- Lens table, simulate/mode-closure row: "a fold that widens a scope is drilled against every privacy/closing rule of the same names" (r61 F-A/F-E/F-F).

## Framework notes
- Coordinator pattern worked at low cost: ~25 min wall from launch to draft; the coordinator's own suspicions were kept out of briefs and confirmed blind.
