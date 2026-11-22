# process r78 memfn-bsu4 (coordinator)
- 08:51 freeze SUBJECT 023ab6eb8 BASE ad3c8f1c2 (merge-base with lane/memfn-k1108 d9d53d77f); main 92f5e77b6; decisions bc22e155a plan 0ec0a8f35
- 08:51 review tree built nice -j2 unlocked (~1 min); BASE archive built clean
- plants: 9 rows built (~3 min); traced compilers x10 built
- coordinator checks: 0 paths under memfn/src src cli lib; 164 BASE/SUBJECT emitted pairs identical; anchors 1384 resolve; span_pins 65/0 (1 s); g2_vspan both 2830/0 (31 s)
- lenses: PLANTSA opus, PLANTSB opus (9 rows > 5: split, one row each), G2V opus, PINS opus, C18WIRE opus. emitted-vs-replaced NOT staffed (no emitted byte moves, checked above).
- 08:58 five critics launched (all opus, background, unnamed); all returned in the launch turn, files complete, lanecheck DONE: plantsa 4.2 min, pins 8.1, plantsb 8.7, g2v 7.7, c18wire 11.8. Final replies: all "ended without SubagentHandback" (expected; files are the delivery).
- findings: PLANTSA 2 (1 doc, 1 suspected gap), PLANTSB 3 (1 doc w/ plant-answer note, 2 held), G2V 5, PINS 8 + standing Q, C18WIRE 8.
- coordinator plant V1 (V ahead of T-deny only): span_pins 65/0 GREEN; deny renders 1 vs0 call; default==deny text (basename only) so memfn_arm span-loop DIFFER (test-axes) would red. PLANTSA-2 CONFIRMED: no make-test check.
- coordinator ran g2v on plant S3530: rc1, 16 FAIL, 0 guard faults (k-source/text disagreement at off, refusal at on). G2V-3: design's "start guard page" attribution wrong; detection exists.
- 09:12 verifier (sonnet) launched; returned in launch turn 8.7 min, 12/12 HOLDS, lanecheck DONE. INCIDENT (self-disclosed): it symlinked tests/ into a fake root and once overwrote $W/tests/memfn/span_pins.py with an identical copy; `git status --short` in W clean afterwards (coordinator re-checked: clean). Review worktree only, no repo damage.
- 09:22 freeze drift: main 92f5e77b6 -> 2910d6f7a; decisions/plan unchanged; critic SKILL.md gained complexity lens (a16f2ba92), not applied (test code). Kit branch unmoved.
- 09:25 draft review.md written; 26 ids. Time to draft ~34 min from freeze.

## Process observations
- All five critics and the verifier returned within their launch turn (4-12 min); narrow opus briefs plus prebuilt plants/trace compilers meant no critic spent time building. ~34 min freeze-to-draft.
- Splitting 9 plants into two disjoint critics worked: no duplicate plant runs.
- Mutation-of-the-test (G2V, PINS, C18WIRE did it on their own check files) found most claim-3 gaps; the plant critics found mostly doc issues. For a CHECKS-ONLY unit the mutation harness over the checks is the productive lens.
- Symlinked fake roots are a write hazard: a cp through a symlinked dir writes into the review tree.

## Proposed changes
- SKILL §5 COMMON template: "Fake roots for test mutations symlink FILES, never directories of the review tree; a cp through a symlinked directory writes the review tree (r78 verifier overwrote span_pins.py, identical by luck)."
- SKILL §4 check-adequacy row: "For a new HARNESS, mutate the harness to disable each promised regime (a guard page, a layer, a staircase) and require a red: floors that count what is generated, not what is driven, pass every such mutant (r78 G2V-1: 4 of 4 green)."
- SKILL §4: "A CHECKS-ONLY subject gets a mutation lens per new check file; the product plants found mostly doc findings in r78."

## Framework notes
- The coordinator pattern ran cleanly at 6 agents with no resends; prebuilding everything (plants, traces, kit, timings) before briefing let every critic finish in one turn.
