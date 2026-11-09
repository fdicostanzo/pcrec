# process.md: critic round spanarms5 (L2/L3 readiness), coordinator notes

- t0 16:58 freeze: subject span_arms.md rev 2 @9e879e82c / main 36072b2a0; build tree main 9161402da (built nice make -j2, unlocked, rc 0, ~1 min). Rulings: decisions a47aa97ce, plan 682cb5f6d. Ruling records: r1/r2/r3 "Manager rulings" sections (r3:100). No FREEZE NOTE.
- 17:01 launched ready2 (opus, L2) and ready3 (opus, L3), background, unnamed. Both RETURNED IN THE LAUNCH TURN (ready2 ~11.6 min, ready3 ~16.5 min), files complete, lanecheck DONE for both (ready2.done 17:12, ready3.done 17:17). No resend, no nudge.
- Findings: ready2 7 (READY2-1..7, all CONFIRMED; 1 build blocker READY2-2, 1 speed READY2-6); ready3 9 (READY3-1..9, all CONFIRMED; answer-class shape READY3-3 covered by the note's general move; speed/contract READY3-4).
- 17:18 at critic return: re-diffed rulings: decisions/plan unchanged. Main had moved: b0867839d/7c0203a5e (rev 2.1, L1-only text; "L2 and L3 text is rev 2's, unchanged") and 1ffcce0c1: the MANAGER had already RULED the round from the critics' files (copied this round dir's .coord/ into the committed review as coord/), stating the coordinator had ENDED before verifier/draft. So no verifier and no draft were run by me: the ruling supersedes them (rev 2.2 lane re-checks each CONFIRMED finding).
- Cross-critic conflict noticed (not verified): READY3-1 says the keep-LAST sabotage of a 40-position `++` capped at 32 is `a^12 b^20`, not the note's `a^8 b^20`; READY2-1's W-T2 plant used the note's `a^8 b^20`. Under READY3-1's mechanism (`a^12 b^20` is a substring of the subject) W-T2 may not fail even under `--memfn=no-fd-pres-pick`, leaving only the `req_whole_run` listing row.

## Process observations
- The coordinator's turn ended when both background critics returned inside the launch turn; the manager saw the critics' hand-backs and ruled before the coordinator resumed. The skill's "critics may return in the launch turn" rule assumes the coordinator keeps the turn; with nested agents the hand-back can reach the launcher first.
## Proposed changes
- Skill §6.1: "If critics return in the launch turn, read their files and launch the verifier IN THE SAME TURN before any reply; never end the turn with critics complete and no verifier launched." Motivation: this round (and per the manager, twice).
- Skill §5 per-lens brief for paired witnesses (W-T2/W-T3): when two critics review mirror witnesses, the coordinator diffs their arithmetic before the verifier (the a^8/a^12 slip surfaced in one critic only).
## Framework notes
- Fan-out by UNIT (one readiness critic per build unit) was clean: no overlap except the L2/L3 dependency (READY2-7 and READY3-6 found the same `cons` dependency from both sides: a useful cross-check).
