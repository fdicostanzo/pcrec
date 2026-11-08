# process: crit-spanarms3 (design readiness re-check, L1 only, ONE critic + verifier as ruled)
- freeze 2026-11-08T16:34: subject span_arms.md rev 2 @ 9e879e82c (main 36072b2a0); build tree = main 36072b2a0; rulings decisions.md @a47aa97ce, plan.md @fbcb4819c; cites base c054e38e7 -> 36072b2a0 diff over src cli lib memfn docs/spec tests EMPTY. Ruling records: D168 decisions.md:9831; r1 + r2 "Manager rulings (2026-11-08)" (r2 review :120). No FREEZE NOTE.
- build: nice make -j2 in review tree, unlocked, rc 0 (~1 min). First attempt blocked by no_cd_worktree hook (bare cd); subshell form worked.
- ready (opus) launched 16:36, ended 16:49 (~14 min, 82 tool uses), file complete, lanecheck DONE; final reply LOST ("ended without delivering a report through SubagentHandback") -- file carried everything, as the skill predicts.
- findings: 10 (9 CONFIRMED, 1 SUSPECTED); all doc/gate-level text fixes; none answer-level against the design's rules; one (READY-1) is an answer-WITNESS that cannot fail.
- verify (sonnet) launched 16:50, ended ~16:56 (55 tool uses), file complete, VERIFY COMPLETE, lanecheck DONE; final reply LOST again (same SubagentHandback message). One stray write into ready/m/ (the critic's dir) before it redirected; harmless (critic done).
- verdicts: 8 HOLDS, READY-6 HOLDS softened, READY-9 PARTLY, 0 REFUTED (no REFUTED to re-run).
- freeze drift at hand-back (main 7b4e3cc7a): plan.md one line, the kit/SIMD row status; nothing on this subject.
- draft 16:58; total round ~24 min wall from freeze.

## Process observations
- One critic over L1 was enough: real plants (an env-override of the walk's output at the one walk entry) let the critic test answer witnesses of an UNBUILT unit end to end. That plant shape should be a COMMON tool for every run-arm round.
- The window condition (READY-1) was missed by two earlier rounds' SIM models, which modelled the whole run. The miss class: a model of the fact, not of what the artifact reads.
- Both nested agents' final replies were lost; the file-first rule carried the round.
- The ruled reduction dropped the standing questions (sibling, general form + unlocks); the skill does not say what a one-critic round does with them.

## Proposed changes
- Skill §4 readiness row, append: "For a run/set witness compute the EMITTED window (`pcrec_req_window`, PCREC_MAX_REQ_RUN_EMIT) under the correct and the sabotaged fact; a difference outside it fails only under the whole-run test (`--memfn=no-fd-pres-pick`). For every gate check, grep its population for the witness (a fixed WIT list) (2026-11-08 r3 spanarms3: W-T1, W-S4)."
- Skill §5 COMMON: "For a fact-level unit not yet built, offer critics the WALK-OUTPUT PLANT: an env override of the fact at its one derive site, built once into the round dir by the coordinator (saves each critic a build)." (r3 spanarms3: the critic built it itself.)
- Skill §4: "A ruled one-critic round folds the two standing questions into that critic's brief as a closing sub-part, or records that they were dropped."

## Framework notes
- A coordinator for a ONE-critic round is still cheaper than the manager doing it: freeze, build, COMMON, verifier and draft took ~8 coordinator turns, and the manager's large context woke once. The verifier earned its place: it narrowed READY-1's repro (the unmasked sabotage was a substring of the subject) and softened READY-6.
