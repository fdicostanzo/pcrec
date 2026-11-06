round altnf2 started 2026-11-05T19:29:08-05:00
SUBJECT doc docs/design/alt_normal_form.md @ f7fd1a759241a5c22a090bd4f14603c8130013ee
BUILD tree main HEAD 569c57d3a7f9ad323ad2a56e69508bfbf4ed8309
RULINGS freeze decisions.md/plan.md @ 569c57d3a
2026-11-05T19:32:55-05:00 review tree built (nice make -j2, rc 0, unlocked)
population copied: altrev1_evidence, altdesign_evidence, altthink_evidence, rpsurvey_evidence + 2 reports
lenses chosen: fix-induced (opus; + ruling check O1-O5/D-rows + standing sibling/general-form), soundness (opus; adjacency test/C2, factoring rules, pieces, witnesses both builds), readiness (opus; + goals), simulate (sonnet; rev-1 numbers, §6 table first-match drill, declared strategy)
not chosen: owner criteria (folded into fix-induced's ruling check: O1-O5 are the owner's criteria in force), premise (rev 0's premise round ran; fix-induced traces additions), cost/overlap (folded into readiness separability + fix-induced), measurement (folded into simulate)
coordinator note: verbs (*THEN) etc refused by pcrec, so suffix-factoring-with-THEN hole is out of scope (checked)
2026-11-05T19:49:53-05:00 all 4 critics returned in launch turn (no SubagentHandback reply; reading files)
2026-11-05T19:50:14-05:00 fix (opus): file complete, lanecheck DONE, 10 findings + ruling check + standing Qs; ~30 compiles
2026-11-05T19:50:14-05:00 soundness (opus): file complete, DONE, 5 findings (1 answer: SND-1 \K/capture in intervening branch); ~75 compiles
2026-11-05T19:50:14-05:00 readiness (opus): file complete, DONE, 9 findings + per-unit verdict "ready with listed text fixes" s1/2p/2b, 2a census-first, 3 blocked by design; ~15 compiles
2026-11-05T19:50:14-05:00 simulate (sonnet): did work (scripts in dir) but NO findings.md; one SendMessage asking for it (resumed)
overlaps: FIX-1=RDY-1; FIX-2=SND-2; FIX-3=RDY-7(+RDY-5); FIX-4=RDY-2. Bit count disagreement FIX-3 (58 used/6 free) vs RDY-7 (57 used/7 free) -> verifier
2026-11-05T19:51:21-05:00 simulate: findings RELAYED via manager (Write refused by harness rule for subagent report files; no lanecheck); saved as simulate/sim.md. Manager note: if others hit the refusal, return findings as final text
2026-11-05T20:00:39-05:00 verifier (sonnet): launched, returned in launch turn, verify.md complete, lanecheck DONE. HOLDS 14, PARTLY 6, REFUTED 0 (no REFUTED to re-run)
2026-11-05T20:00:39-05:00 freeze drift: plan.md changed by vlbrev1 ([VLOOKBEHIND], [LB-EXIST]); decisions.md + note unchanged
2026-11-05T20:00:39-05:00 worktree removed (wtprune --apply --force --quiet-min 1); draft review.md written

per lens: fix 10 raised (9 CONFIRMED, FIX-9 SUSPECTED), 8 verified; soundness 5 raised, 5 verified HOLDS (1 answer); readiness 9 raised, 7 verified; simulate 6 raised, 3 verified (SIM-1/4 PARTLY, SIM-3 HOLDS). Overlaps: 4 pairs.

## Process observations
- All four critics and the verifier returned in the launch turn (no SubagentHandback reply text). Three critic files + verify.md were complete; simulate's Write of findings.md was refused by a harness rule for subagent report files, so its findings reached the manager as final text and were relayed back. One SendMessage to simulate was spent before the relay arrived.
- The harness report-file rule and the skill's "findings to a FILE" design are in tension: three critics wrote theirs, one was refused. Unclear what distinguished them (perhaps the Write tool vs a Bash heredoc).
- Readiness + fix-induced overlapped on 4 findings (bit budget, B0 instrument, -Wswitch claim); acceptable double-confirmation for a re-check, but the bit-count disagreement (57 vs 58) showed the value of the verifier.
- Lens table missed nothing obvious; owner-criteria folded into ruling check worked.
- Time: freeze ~19:20, critics ~19:31-19:47, verifier done ~20:00, draft ~20:05.

## Proposed changes
1. Skill §5 COMMON template: "If writing your findings file is refused by a harness rule, do not route around it: return the full findings as your final reply text; the coordinator records 'relayed'." (motivated by simulate's refusal; the manager had to relay).
2. Skill §4 soundness row: add the side-effect drill (lesson 1 of the draft).
3. Skill §4 fix-induced row: "a fix that re-reads an existing node kind is tested on today's instances it did not create" (SND-2/FIX-2).

## Framework notes
- The coordinator stayed blind and cheap: one draft, ~20 coordinator turns. The weak point is delivery: nested agents' final replies are lost AND a harness rule can refuse their report files, so the manager may become the relay. A fallback channel the coordinator can read (e.g. a Bash-written file) would keep the manager out of the loop.
