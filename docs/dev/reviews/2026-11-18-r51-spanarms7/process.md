# process.md — round r51 spanarms7 (design), coordinator crit-spanarms7

## Freeze (18:46-18:50 2026-11-18)
- SUBJECT docs/design/span_arms.md rev 3 at 3b7d1508e (lane/spanarms7 tip 4bf63fb9d adds only the lane report + index line).
- Design's T = 8993b8f82 (branch's merge-base with main). Build tree B = main HEAD 1403873df; `git diff --stat T B` = dev_journal.md only.
- Rulings freeze: decisions.md/plan.md at main 1403873df (last change 8993b8f82). Record copies in R/record/.
- In-force rulings' records: D191 decisions.md:10129; D172 :9904; D168 :9839+; owner 2026-11-18 + remodel-go call REQ-LOOKAROUND.md:3,:25; r50 A6/A8/A17 in docs/dev/reviews/2026-11-18-r50-archlook.md.
- Client design docs: the note req_lookaround_arch.md rev 2.1 ACCEPTED at 30c370701 (ancestor of T: yes, it is on main before 8993b8f82).
- Review tree worktrees/crit-spanarms7 built `nice make -j2`, unlocked, ~1 min, exit 0. Oracle kit/p2probe built from tests/lib/p2probe.c, checked.
- Anchor map run at B: kit/anchors_at_B.out.
- Coordinator note (setup): the main tree's build/pcrec (Nov 15 19:53) is current for src (last src commit 4c8cf3c38 same minute; later commits touch memfn/docs/requests.md only), so §14.2's "main tree's build/pcrec" is a T-equivalent binary. Not a finding.

## Lenses
| lens | model | launched | ended | final state | findings |
|---|---|---|---|---|---|
| READYL1 | opus | 18:49 | 19:01 (12.8 min) | file complete; final reply undelivered (expected) | 8 (verdict READY WITH TEXT FIXES) |
| READYL3 | opus | 18:49 | 19:02 (13.9 min) | file complete; reply undelivered | 9 (READY WITH TEXT FIXES; -1/-4/-6 answer/safety) |
| READYL2 | opus | 18:49 | 18:59 (11 min) | file complete; reply undelivered | 6 (READY WITH TEXT FIXES) |
| CONFORM | opus | 18:49 | ~18:57 (8.2 min) | file complete; reply undelivered | 14 (9 conformance + 5 UNLOCK) |
| RULING | opus | 18:49 | 18:54 (5.9 min) | file complete; reply undelivered | 10 + ruling table |
- All five returned in the launch turn (background launch still blocked the turn: the Agent results came back together). No resends, no nudges.
- Freeze drift re-checked at return (19:03): decisions.md/plan.md/REQ-LOOKAROUND.md/the note unchanged on main (1403873df); lane/spanarms7 tip unchanged (4bf63fb9d). None.
- Overlaps: spec ¶6/¶8 (READYL3-3, READYL2-4, CONFORM-4); rn_cmp home + S474 (READYL3-7, CONFORM-3, READYL2-6.1, READYL1-3 lists S474@490); anchor map limits (READYL3-8, READYL1-3).
| VERIFY | opus | 19:03 | 19:09 (6.6 min) | file complete (VERIFY COMPLETE); reply undelivered | 18 items: 18 HOLDS (V2/V14 consequence parts unverified), 0 REFUTED |

## Per lens: raised / verified / severity
- READYL1 8: 5 sent to verifier, 5 HOLD; severities maintenance/test/doc, one answer-risk-as-worded (READYL1-7).
- READYL3 9: 6 sent, 6 HOLD; answer 1 (READYL3-1), safety 2 (-4, -6), rest maintenance/doc.
- READYL2 6: 5 sent, 5 HOLD; test/doc/design (READYL2-5 unit split).
- CONFORM 14: 3 sent, 3 HOLD; 9 conformance (doc/design/maintenance) + 5 UNLOCK proposals.
- RULING 10 + ruling table: 2 sent, 2 HOLD; attribution/doc, one design (RULING-4, the census stop), one PLAN (RULING-5).
- Time to draft: freeze 18:46 → draft 19:13 (27 min). Worktree removed 19:14.

## Process observations
- All six agents (5 critics + verifier) returned in the coordinator's launch turn although backgrounded: the round ran
  as one blocking step of ~14 min. Fine for a coordinator with nothing else to do; lanewatch was never needed.
- Pre-running the anchor map at B into the kit paid off: READYL3, CONFORM and READYL1 all diffed binding lists against it
  in minutes. It also showed its limits (first-line matching; note-only ranges) — three lenses extended it themselves.
- Copying the record read-only into R/ again meant zero denylist exposure; no critic needed the lane branch.
- The one-readiness-critic-per-unit staffing held: per-unit verdicts came back clean and non-overlapping except the
  spec-hunk root (three lenses) and the rn_cmp/S474 root (four lenses) — both are cross-unit facts no single unit owns.
- No critic ran a literal pseudo-code drill except READYL3, which was briefed to; it found the round's only answer move.

## Proposed changes
1. Skill §5, design mode: when the subject ships per-unit sabotage/anchor lists, the coordinator runs the anchor map over
   EVERY function the design moves or splits (not only the note's remodel ranges) and puts that output in the kit.
   Motivation: S474 (rn_better split), S1925 (E-5i), S3075 (multi-line anchor) were found by three critics extending the
   tool by hand.
2. COMMON template: "Where the design gives emitted-text pseudo-code and keeps caller guards ('stays in its caller'),
   hand-execute with every kept guard in force." Motivation: READYL3-1.
3. Lens table, readiness row: add "a census run on the unit's BASE: which population does its STOP read (model vs
   observed)?" Motivation: RULING-4, found by the ruling lens, not by any readiness lens.

## Framework notes
- Coordinator pattern, design mode, 5 opus critics + 1 opus verifier, 27 min freeze-to-draft, 0 resends: the per-unit
  readiness split plus one cross-cutting conformance lens and one ruling lens covered an L-unit re-base without overlap
  except on genuinely cross-unit roots. The kit (built binary, oracle probe, anchor output) is what kept every critic
  under 15 minutes.
