# process — round predspec20 (coordinator, opus)
Freeze (15:58): subject predicates_draft.md rev 20 @ d1434199b (main merge 3cd3d4376); rev 19 = 3cd3d4376^1.
Rulings freeze: decisions.md/plan.md @ d12b63a67; COND-FAMILY.md @ 90d08c256 (spelling-phrasing 15:29), ancestor of subject.
joint_condition.md @ 50d586bc3 (absfix), ancestor of subject. predicates_future.md @ 4b2dfe934.
No reading postdates the subject commit at freeze.
Evidence chain copied (13 scripts + .out); predspec20_check.py re-run 12 s, output SAME as committed, rc 0.
Lenses: changetab (sonnet), fixind (opus), simulate (opus), ruling (opus), census (opus).
## Agents
launch 15:59
- 5 critics launched together ~16:00; ALL returned within the launch turn (changetab 7.4 min sonnet, ruling 8.2, census 8.4, fixind 10.4, simulate 12.0 opus). Each file complete with CRITIC COMPLETE; 0 resends, 0 nudges. Each agent ended "without SubagentHandback" (final reply lost; files carried everything, as the skill predicts).
- Findings: changetab 10, fixind 12, simulate 9, ruling 9, census 10 = 50.
verifier launch 16:13
- Verifier (opus) launched 16:13, returned in-turn 8.9 min, verify.md complete (16 items: 11 HOLDS, 5 PARTLY, 0 REFUTED). Final reply lost (no SubagentHandback); file carried it.
- Doc-only quote findings verified INLINE by the coordinator (sed of the cited rev 20 lines): CHANGETAB-1, -2, -6, -9; FIXIND-9; RULING-5, -6(b); CENSUS-3, -5, -10. Not separately verified (quote claims, DOC): CHANGETAB-5, -7, -8, -10; FIXIND-8; RULING-8, -9; CENSUS-2, -4, -8.
- FREEZE DRIFT at hand-back re-diff (16:22): owner rulings match-context (16:13) and zero-pass-empty (16:20) landed on COND-FAMILY.md mid-round; not homed in the subject -> HAND MAPPING in review.md (no fresh critic). Also 08c5a9140 predicates_future.md (non-ruling). Re-diffed only at hand-back, not at each critic return: all critics returned in ONE turn (16:00-16:12), before either ruling landed, so per-return re-diffs would have found nothing.
- Brief confusion (coordinator's): the simulate brief paraphrased the record's 15:27 (4) list ("backreferences, lookarounds, recursion") as rev 20's; rev 20 lists "a backreference, recursion, a verb". The critic caught and flagged it (SIMULATE-4 NOTE). Lesson: brief from the subject's text, never from the record's paraphrase.
- Blinding: no leak noticed. changetab cited a post-freeze main subject line (08c5a9140) from git log: allowed (subject lines), harmless.
- Time to draft: launch 16:00 -> draft 16:25 (~25 min).

## Process observations
- Pre-created findings files + CRITIC COMPLETE: 5 of 5 critics and the verifier wrote cleanly and all returned inside the launch turn; lanewatch/resends never needed.
- Every agent's final reply was lost ("ended without SubagentHandback"): files are the only channel, as the skill says.
- Lens table fit: changetab (sonnet) was fast and complete; the census found the unique doc+one design item (CENSUS-7); simulate and fixind overlapped productively on DOM (three-side convergence again, as r28).
- The opus verifier earned its cost: it corrected SIMULATE-2 (overstated "forced"), SIMULATE-7 (false premise), SIMULATE-4/CHANGETAB-4 (refusal-tier framing), and unified FIXIND-3 into the DOM cluster.

## Proposed changes
1. Skill §4 ruling-check row, append: "When a revision WITHDRAWS a reading, re-check every KEPT reading whose stated equivalence rested on it (2026-11-16 r29 predspec20 V4: 14:50 (b) 'same as satisfied' held only under (c) 'any text', withdrawn in the same revision)."
2. Skill §4 simulate row, amend the REAL MODE clause: "apply each acceptance case AND every worked table the revision adds in the program's REAL MODE (r29 SIMULATE-1/6: two new tables stated whole-value answers that move when searched)."
3. Skill §4 simulate DOMAIN drill, append: "and an equal-behaviour pair built by a CONDITION (`rx & (cond)` vs the narrowed rx) or a second `&` operand (r29 FIXIND-7, AND-DEAD)."
4. Skill §6.2: "opus verifier when the CONFIRMED findings are interlocking semantic claims; group same-root findings as one item (r29: 16 items, 5 PARTLY corrections, one unification)."
5. Skill §5 COMMON template: "brief a lens from the SUBJECT's text, never the record's paraphrase of what the subject should say (r29: a wrong list in the simulate brief)."

## Framework notes
- A 5-critic + 1-verifier design re-check ran in ~25 min wall with zero coordinator interventions; the coordinator's main value was the freeze-drift hand mapping (two owner rulings landed mid-round and settled or reshaped 6 findings) and the consolidation of 50 findings into 17 groups. The pattern fits any fold re-check where rulings are moving the same afternoon.
