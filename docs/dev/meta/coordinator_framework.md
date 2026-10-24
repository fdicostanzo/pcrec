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
