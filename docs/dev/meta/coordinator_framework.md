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

## 2026-11-04 — critic round memfn-sp1c (review 2026-11-04 r2)

- A small no-mover unit took about 22 minutes from freeze to draft, with the manager untouched until hand-back. The cost driver was critic depth (one lens made 1,409 compiles), not coordination. For no-mover units the dual-spelling plant (the old spelling recomputed beside the new, with a disagreement counter) was the strongest single witness.
- The coordinator's own re-run of the plant compares caught two scripts that read failed compiles as silent moves; the verify step earned its place.

2026-11-05 r1 memfn-sp1d (code):
- The round took about 30 minutes wall, with every critic under 12 minutes. Its value was blinding and consolidation (34 critic ids became 13 findings), not monitoring.
- Pre-building BASE/SUBJECT release and MF_TRACE pairs once (4 builds) meant critics needed no builds of their own. This repeats r5 sp1g's lesson; make it the default in code mode whenever MF_TRACE output is in the promise.

2026-11-05 r2 memfn-sp1e (code):
- Freeze to draft took ~36 min, with no resends.
- The verifier reused a critic's plant directory read-only, which saved builds. Worth stating in the verifier brief template.
- Reading found the one gate defect (F1) that ~2k byte-identical compiles could not: on a zero-mover unit, probes confirm the bar and reading finds the defects.

## 2026-11-15 — critic rounds covs2d (review r13) and predspec12 (review r14)
- r13 covs2d (design, 5 critics + sonnet verifier): the coordinator pattern held cleanly at small scale: one freeze, one build, one kit, five parallel critics, one verifier, draft in about 20 minutes of wall time; the manager saw nothing until the hand-back. The verifier's value was concentrated: of 23 items the one REFUTED (MEASURE-4, shell quoting dropped a `\b`) was the only critic error, and it would otherwise have entered the draft as a design finding. All critics returned within the launch turn (2-7 min); the sonnet measurement critic was fastest and least careful.
- r14 predspec12 (design, 2 opus critics, inline verification): for a short re-check the pattern's overhead (COMMON, deliver files, lanecheck) is about 5 min of setup against about 5 min of critic time; still worth it for the blinding and the census counts. Freeze to draft about 11 min; the coordinator verified inline (quotes + 4 oracle calls) because every finding was a quote claim or a one-call repro.

## 2026-11-15 — critic round covs2e (review r15)
- The coordinator pattern handled a mid-round ruling cheaply: one `git diff` of decisions.md at hand-back found D198 addendum 1, and the hand mapping took one paragraph. Without the freeze-drift step the draft would have carried a stale "owner question open".
- Nested critics' final replies were again lost; the files-plus-lanecheck contract made it irrelevant.

## 2026-11-15 — critic round predspec14 (review r16)
- Three opus critics on a ~3,700-line design doc, all done in under 10 min with complete files, from a COMMON that pointed at read-only round-dir copies: no repo access needed, no denylist exposure. Inline verification was cheaper than a verifier agent for quote/one-script findings (second round in a row).

## 2026-11-15 — critic round covs2a (review r18)
- Coordinator pattern worked with no manager wake-ups; the only round-trip was the single hand-back. Inline verification (16 quote/one-call checks in one command) was right-sized; a verifier agent would have cost more.
- For a staged change against a named item list, the conformance lens was the most productive (8 findings, 17 compiles) and earns its own lens.
- A box deadline was easy to meet: zero-mover code rounds at -j2 with prebuilt plants finish probing in about 10 minutes.
## 2026-11-15 — critic round predspec17 (review r17)
- A confirm round over a ~600-line two-revision delta ran end to end in ~15 minutes (launch 23:32 box clock, draft about 23:45) with zero coordinator interventions: three opus critics, all returned in the launch turn (6-8 min), files complete, lanecheck DONE. Evidence: `docs/dev/reviews/2026-11-15-r17-predspec17.md` "Round process".
- The frozen-copy + diffs pack (rev 15/16/17 copies plus both diffs in the round dir) is what made the critics self-contained: no repo reads, no blinding exposure. The text-first simulate and the fix-induced lens converged on the one answer finding (F1) from different directions (rule emulation vs "what did moving the labels to the author change").

## 2026-11-16 — critic round jointcond (review r26)
- A design-only fold needed no build and no verifier agent: about 35 minutes wall from freeze (13:01 box clock) to draft, five critics in parallel (4 opus, 1 sonnet), all evidence as files, all five finished in 3-12 minutes with complete files (a pre-created findings file plus a `CRITIC COMPLETE` line plus lanecheck). All five Agent results came back in the launch turn as "no report delivered"; the file channel was the only channel, as the skill expects. Inline verification (quote claims re-read at their lines, two script re-runs) sufficed. The pattern fits any "fold N rulings into a client doc" step (the predicates_draft revisions especially), where the change table is the seam to check. Evidence: `docs/dev/reviews/2026-11-16-r26-jointcond.md`, its sibling directory (process.md).
- The lens table had no row for a design-to-design FOLD; the coordinator borrowed readiness's reader-grep as a sonnet "rev20 completeness" lens: the cheapest lens and the most raw findings (10). It is now the row "change-table completeness".
- The ruling and owner lenses both re-checked the same ~19 owner quotes (duplicate work, both 0 drift): quote verification is now given to ONE lens.
- A ruling (label-twice) landed at 13:16:09, the second the critics returned; the per-return re-diff caught it and the draft's FREEZE DRIFT block carried a hand mapping.

## 2026-11-16 — critic round absfold (review r28)
- A coordinator with a copied, read-only subject + record + evidence (no repo access needed) ran a 5-lens design round in about 18 minutes wall, zero manager turns. The pattern fits any fold-review of a document against a rulings record.

## 2026-11-16 — critic round predspec20 (review r29)
- A 5-critic + 1-verifier design re-check ran in ~25 min wall with zero coordinator interventions; the coordinator's main value was the freeze-drift hand mapping (two owner rulings landed mid-round and settled or reshaped 6 findings) and the consolidation of 50 findings into 17 groups. The pattern fits any fold re-check where rulings are moving the same afternoon.
