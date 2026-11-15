# process: crit-predspec10 (coordinator, opus)
- freeze 2026-11-15T22:52Z: draft at 8d6b77c4f (== 287289b5e for the draft); CF at 8d6b77c4f (last CF commit 40134849f, the per-match ruling, folded by the draft as CF:997-1000); decisions.md bf8319fb8, plan.md 782502e99.
- design mode, no build proposal: no review tree built (nothing to cite in code). Oracle kit R/oracle.py (libpcre2 ctypes) sanity-run 4 calls OK.
- lenses per launcher: SIMULATE (opus), CENSUS (opus); fix-induced folded into both; standing questions (sibling/unlocks, goals) scoped OUT by the launcher ("Nothing else is in scope").
- 22:53Z launched SIMULATE (opus) + CENSUS (opus), background, unnamed. Both returned in the launch turn: SIMULATE ~6.4 min (26 tool uses, file complete, lanecheck DONE), CENSUS ~9.8 min (62 tool uses, file complete, DONE). No resends, no nudges. Neither delivered a final reply text (harness: "ended without SubagentHandback"); files were complete, so no loss.
- VERIFY (sonnet) ~2.7 min, 15 findings: 13 HOLDS, 2 PARTLY (CENSUS-1 overstated "label-free"; CENSUS-6 (a) refuted by location). Coordinator re-checked the (a) refutation by grep: holds.
- Freeze re-diff at hand-back: no drift (main 0eb33b780 touched none of the four files).
- Findings: SIM 3 (1 answer, 1 design, 1 doc), CENSUS 12 (6 fix-induced by rev 10).
## Process observations
- The extracted read-only subject copies in R/subject/ removed every grep-leak risk; critics needed no repo access.
- A pre-built oracle (libpcre2 via ctypes) let SIMULATE run ~175k calls with zero tool building.
- CENSUS found the most again (12 vs 3): a census on a notation re-check stays the productive lens.
## Proposed changes
- Skill §5 design mode: "copy the frozen subject and its rulings record READ-ONLY into R/subject/ and point critics at the copies" (this round: no denylist exposure at all).
- Skill §4 simulate row: on a re-check that FOLDS a ruling, re-apply every SAME look-alike row under each ruling folded in that revision (SIMULATE-1).
## Framework notes
- A two-critic confirming round (opus) + sonnet verifier finished in ~25 min wall with a verified draft; the coordinator pattern fits short re-checks when the subject copy and oracle are prepared before briefing.
