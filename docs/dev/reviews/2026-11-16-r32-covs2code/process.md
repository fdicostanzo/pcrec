22:43 freeze SUBJECT=ad6f4cb BASE=77ddecc rulings main=85fba0d20
22:43 worktree + build (nice -j2, unlocked) done ~1 min; prebuild (base, CAND_TRACE base/subject, 17 plants) 22:43:40-22:44:52
22:50 COMMON written; regimes checked (0/4096 refused rc1, 4095 cover on [0-9a-f]{40}); kit smoke OK
Lenses (5): EMIT (opus; emitted vs replaced + house rules sub-part), CONTRACT (opus; contract + adversary resource sub-part),
 CHECKSAB (opus; check adequacy, sabotage rows via plants, >5 rows), CHECKHAR (opus; check adequacy, kitproof/axes/san/shards/reference compile),
 SEAM (opus; seam round trip + slot tracing + ruling check + goals + standing questions sibling/general-form; owner quote verifier)
Deviation: house rules folded into EMIT (cap of 5 critics), not run as a sonnet lens.
22:47 5 critics launched in one message (opus, background, unnamed); ALL returned in the launch turn (durations: CONTRACT 7.5 min, EMIT 8.6, SEAM 9.0, CHECKHAR 6.3, CHECKSAB 11.3); each file complete with CRITIC COMPLETE, lanecheck DONE (5 .done records in the round dir). No resend, no nudge, no stall.
Agent ids: EMIT a567654923b9c20df, CONTRACT a98968d198ec9c5e0, CHECKSAB a55fe8cbcee4636d9, CHECKHAR a31462a310ac39ee0, SEAM ac7089df16cb9520c. Final replies not delivered (harness: "ended without SubagentHandback"); files carried everything (the skill's files-not-replies rule held).
Per lens: EMIT 6 (2 shared), CONTRACT 4 (2 shared), CHECKSAB 6, CHECKHAR 6 (1 SUSPECTED), SEAM 6 + standing answers. Overlaps: code-cap x3 (EMIT/CONTRACT/SEAM), near-miss x2 (EMIT/CONTRACT), dead conjuncts x2 (EMIT/SEAM). 28 raw -> 22 consolidated.
22:58-23:00 inline verification (skill §6.2 allowance: one-call repros/quotes/greps): F1, F2 (perf stat instructions:u, taskset -c 7, 3 repeats), F3, F7, F5, F17 HOLD; F16 PARTLY (pre-existing in MFROUTED). No verifier agent.
Freeze drift: none (decisions.md/plan.md unchanged e1f6a8349..94edfed66).
Blinding: no leak noticed. One critic (CONTRACT) cited cover_cap.md's own header listing READ-3 as OPEN: that is the subject's text, allowed.
Last box process of the round: ~23:00 (deadline 00:40 kept by 1h40).
Time to draft: freeze 22:43 -> draft 23:05 (~22 min).

Process observations:
- Prebuilding all 17 plants + BASE + 2 trace builds took 72 s on this box (incremental: plant copy carries the review tree's build/ and the archive's older mtimes, so only the planted file recompiles). Planting is cheap enough to always do on the dev box.
- The run kit (kit.sh: tree selector incl. plant:<ROW>, same-basename OUTDIR, libpcre2 SAME/DIFF) was used by every lens; no critic built tools; all finished in 6-11 min.
- Three lenses converged on the code-cap refusal from three sides; the lens table's "premise: for each new LIMIT find the existing limits on the same object" (design-mode only) is the one that would have caught it at design time. In code mode no lens asks "run the new range's top through every cap".
- Folding house rules into EMIT kept the round at 5 and EMIT still delivered three house findings.
Proposed changes:
- skill §4, contract lens (C): add "run the newly legal range's TOP (and the default) through every `compile budget` cap in limits.def (not just the cap the design names) and check each cap's fallback sentence in the spec" (motivation: F1; the design priced PCREC_MAX_EMIT_BYTES and missed PCREC_MAX_VM_EMIT_CODE_BYTES).
- skill §3.2: "plants: copy the SUBJECT `git archive` + the review tree's build/ into plants/<ROW>/tree; the archive's commit-time mtimes make each plant an incremental build (17 plants in ~60 s, 2026-11-16 covs2code)".
- COMMON template: a `kit.sh plant:<ROW>` tree selector beside base/subject/trace (every check-adequacy probe used it).
Framework notes:
- A coordinator round with prebuilt plants + one shared kit ran 5 opus critics to completion in ~11 min wall, inside an owner evening hold, with the box idle by 23:00: the pattern fits short box windows when the build cost is front-loaded by the coordinator.
- Nested final replies were lost for all 5 critics (harness), the files carried the round: confirms §1's files-only rule.
