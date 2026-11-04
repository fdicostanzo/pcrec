# The coordinator framework — observations across uses

A manager launches ONE coordinator agent that runs a fan-out of narrow
subagents, verifies their output, meta-monitors the process and drafts a
result for the manager to RULE (Frank, 2026-10-23, first applied to critic
rounds: `.claude/skills/pcrec-critic/SKILL.md`). Frank asked that it be
watched as a framework that might apply in other areas. Append one dated entry
per use: what was coordinated, cost and turns where known, what worked, what
broke, and where else it might fit. Claims name their evidence or say OPINION
(this directory's rule).

## 2026-10-23 — baseline: the iterator code round run WITHOUT a coordinator

Round `docs/dev/reviews/2026-10-23-r2-iter-code.md` was run by the manager
directly: five critics, a verifier, the draft and the fixes. Evidence for the
change:
- about a dozen manager turns on the round (launch, five reports, one stalled
  critic prodded, verification, compile, a citation-hook fix), each re-reading
  the manager's full context;
- the manager knew the find-all timing results and had to keep them out of the
  briefs by care, not by construction;
- four of five critics took their named output file for an input (a brief
  wording fix, now in the skill);
- nested agents: a subagent can launch a subagent, but the nested agent's final
  reply did not reach its parent (test, 2026-10-23); results must travel as files.
Other candidate uses, OPINION until tried: red-suite triage (many reds, one
coordinator classifying and verifying), landing stacks (several branches, one
coordinator sequencing merges and validation), bench result reading.

## 2026-10-31 — critic rounds pricing-split, bakeoff, bakeoff2, bakeoff3 (reviews 2026-10-31 r1, r3, r4, r5)

Evidence: the rounds' process.md files (scratch/crit-*/, not committed; the reviews carry the results).
- pricing-split (4 critics + verifier, ~35 min freeze to draft, zero manager turns): the coordinator is blind to the manager but NOT a firewall to its own critics unless its notes are segregated; the slot critic read the coordinator's planted-check note in process.md. Fixed by a denied `.coord/` subdirectory. Subject citing three other branches' documents fit the pattern (one freeze, one review tree at the merge-base). Elsewhere it might fit (OPINION): a round on a REQUIREMENTS draft reusing the COMMON nearly verbatim.
- bakeoff (4 critics + verifier, ~32 min): fan-out returned synchronously, so lanewatch was a one-shot confirmation; the blindness held by construction (the coordinator never saw the lane's report or rulings). Overlap among three opus lenses was ~25 % duplicated effort, clustered on the decision table and the external harness. Elsewhere it might fit: any "is this experiment able to decide X" review (measurement plans, evaluator designs such as [REGIME-EVAL]).
- bakeoff2 (3 critics + verifier, ~35 min, four coordinator wakes): nested agents never returned a handback reply (4/4); files plus lanecheck/lanewatch carried all delivery. Confirms "everything travels as FILES".
- bakeoff3 (2 critics + verifier, ~35 min, ~3 wakes): on a narrow re-check, splitting by ITEM (not by lens question) gave zero cross-lens overlap and 8-17 min critics; it fits any "re-check items N of review M" request. lanewatch writes to worktrees/.mgr/ in the main tree unless LANEWATCH_LOG is set, a hazard under a no-edits mandate.

## 2026-11-01 — critic round stream1 (review 2026-11-01 r1)

- stream1 (5 critics + verifier, ~26 min freeze to draft): a design round with no code subject fit the coordinator pattern: one build, five parallel critics, one verifier. All six agents returned without a handback; files plus lanecheck markers carried everything. The verifier's value was correcting magnitudes and refuting one ruling-conflict claim, not re-running answers. Elsewhere it might fit (OPINION): reviewing a SYNTHESIS step (merging N blinded drafts) with a soundness critic diffing source rows against merged rows. Two COMMON-template lessons: resolve every cited doc path before writing COMMON; a count over git history states its window (first..last commit) and command (a critic's count silently truncated at 400 lines). A subject citing its own scratch runs should freeze those outputs as part of the subject.

## 2026-11-03 — critic round memfn-sp1g (review 2026-11-03 r5)

- A small code unit took about 20 minutes from freeze to draft, with one coordinator turn chain and zero manager wakes. The verifier reproduced 8 plants from a critic's own harness copy in under 4 minutes. Pattern worth requiring: a critic that plants leaves plant.sh plus its .sub files for the verifier.
- A nested final reply was lost again (SubagentHandback failed three times, "spawner no longer running"); the critic's FILES carried the round.

## 2026-11-04 — critic round memfn-sp1b (review 2026-11-04 r1)

- Four critics plus a verifier took 22 minutes and cost the launcher one message in and one out. Findings duplicated across lenses were consolidated by the coordinator, not in the launcher's context.
- A ruling ABOUT the subject (D187) landed mid-round. The coordinator's freeze diff caught it and re-read the dispositions against it without breaking the critics' blindness, since they had finished first.
