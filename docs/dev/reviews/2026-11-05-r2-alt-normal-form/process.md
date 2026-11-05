# process.md — critic round alt-normal-form (design), coordinator notes
Freeze 2026-11-05 17:21 EST. Subject docs/design/alt_normal_form.md @ d202eae162c0 (doc commit); build tree main HEAD 04a161516 (no source drift d202eae..04a1615: only lane report + history index).
Rulings freeze: decisions.md/plan.md last touched at d202eae162c0 (main HEAD 04a161516). Copy: .coord/plan_freeze.md.
Review tree worktrees/crit-alt-normal-form built nice make -j2 unlocked, rc=0, ~1 min (box load ~30, mech job running).
Population copied read-only to population/.
Lenses: owner(+goals,+kit-seam) opus; premise opus; soundness opus; simulate(+measurement) sonnet; slots(+ruling check,+REQ siblings,+family/unlocks,+cost/overlap D153) opus.
## Agents
- critics launched 17:24 (one message, background, unnamed): owner opus, premise opus, soundness opus, simulate sonnet, slots opus.
- ALL FIVE returned within the launch turn (5-13 min; SubagentHandback "no report" notice each, files complete). lanewatch DONE rc=0 at 17:36. Files: owner 7 findings, premise 7, soundness 6, simulate 8, slots 8 + 3 sibling subsections.
- No resend/nudge needed. Blinding: slots read memfn/docs/wake.md (not denied; the kit's wake) — no leak of the subject's own reports seen.
- Overlaps: PREM-2 = SLOT-1 (abi); SIM-6 = SLOT-7 (2b mover already stage 2's); OWN-4 ~ SLOT-3 (trie output); OWN-6 G2 kind ~ SLOT rulings D186 (stage 1 pick flip is a choice); SIM-1 ~ OWN-6 (766 at least vs exactly); PREM-7 ~ OWN-2 (rr_alt comment misread); SND-5 ~ PREM-3 (S-c reach; PREM-3 stronger: S-c never reaches).
- verifier (opus) launched 17:37, returned in the launch turn 17:46; verify.md complete, VERIFY COMPLETE, lanewatch DONE. HOLDS 17, PARTLY 2 (OWN-1, OWN-5), REFUTED 0 (no re-run owed).
- draft review.md ~17:52; review/ copies; PL14 fix in review/verify.md copy (a line-numbered plan cite -> tag). Worktree removed via wtprune --force --quiet-min 1. FREEZE DRIFT: none (main moved to eb29a0996, decisions/plan/note unchanged).
- Per lens: owner 7 raised / 6 verified (OWN-1 PARTLY, OWN-5 PARTLY) design+doc; premise 7 / 3 verified (PREM-1 speed/size, PREM-2 process, PREM-3 check); soundness 6 / 3 verified (SND-1, SND-2 answer; SND-3 check); simulate 8 / 5 verified; slots 8 + 3 siblings / 6 verified.
- Time: freeze 17:21 -> draft 17:52 (~31 min).

## Process observations
- Every agent (5 critics + verifier) returned within its launch turn although backgrounded; files complete each time; no resend or nudge. lanewatch was a one-shot confirmation, not a wait.
- Lens fit: the soundness lens produced both answer-level findings (in stage 2b, the code-point caller) AND the stage-1 negative result (3112 checks). Premise and slots independently reversed the abi claim (overlap = confidence, cost one duplicated read). Owner-criteria and slots overlapped on the trie/hull (OWN-4/SLOT-3) — folding goals into owner worked; folding 5 sub-questions into slots made its file the longest (309 lines) but it delivered all of them.
- Three of the note's six sabotage witnesses could not fail or reach (S-c, S-f, S-d): the lens table has no explicit "can the witness fail" step for DESIGN rounds (check adequacy is code-mode only).
- Simulate (sonnet) found the non-confluence by a drill nobody asked for explicitly; worth making standard for fixpoint "normal forms".

## Proposed changes
1. SKILL §4 soundness row, append: "For each sabotage witness the design proposes, compute whether its fact clears every floor and domain test in BOTH the correct and the sabotaged build; a witness under the floor in both cannot fail (2026-11-05 alt-nf: S-c out of domain, S-f under the floor, S-d named none)."
2. SKILL §4 simulate row, append: "A rewrite run to a fixpoint and called a normal form gets a confluence drill: every merge order over small exhaustive grids plus the real widest inputs (2026-11-05 alt-nf SIM-2: 23% of grids, \\p{Lu} 76 vs 66)."
3. COMMON template: list memfn/docs/wake.md alongside docs/dev/wake.md as a deny candidate when the subject is pcrec-side and the kit's in-flight state could leak (slots read it; here it was harmless and useful, so: launcher's call).

## Framework notes
- The coordinator pattern ran ~31 min wall for 5 critics + verifier with zero delivery failures; the launch-turn return makes the coordinator effectively synchronous. A coordinator could run two design rounds back to back (rev 0 then a readiness re-check) without the manager waking between them.
- The owner's scope addition (sibling rows) folded cleanly into one lens with its own subsections; pattern fits "review X, and tell me whether X absorbs rows A, B, C" questions generally.
