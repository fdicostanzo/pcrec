# process — crit-memfn-span-cards-r11 (coordinator)

## Freeze (2026-11-06T10:20-05:00)
- SUBJECT doc: docs/design/memfn/span_cards.md rev 1.1 @ ef2f130fc (branch lane/memfn-s2rev11 head e52cd716a adds only the denied lane report + a history index line).
- BUILD tree: main 6f1b40f75 (kit branch lane/memfn-k1102 = main + journal commits only). No binary needed; no worktree built.
- RULINGS frozen at main 6f1b40f75 (decisions.md/plan.md last touched 468afbb0a); requests.md R-35 at 6f1b40f75.
- Exports: subject/ (design + drills @ef2f130fc), buildtree/ (data + .inc @6f1b40f75), read-only.
- Coordinator dry run of drills: all rc=0 (tree_drill needed src/core/*.inc added to the export).
- Blinding note: while finding the DELIVER shape I listed the earlier round dir crit-memfn-span-cards-r1/ (file names only; a cat of *DELIVER* matched nothing). No content read.

## Lenses
- readiness (opus): the launcher's ruled lens; + the two standing questions (sibling of a family, general form + unlocks).
- measurement (opus... see agents table) with the simulate drills.

## Agents
| agent | model | launched | ended | final state |
|---|---|---|---|---|
| ready (a8dfafc6650a3afa1) | opus | 10:28 | 10:37 | file complete, lanecheck DONE; 10 findings; reply lost (no handback) - file is the record |
| meas (ae09892db02180c13) | opus | 10:28 | 10:38 | file complete, lanecheck DONE; 13 findings; reply lost (no handback) |
Both critics returned in the launch turn (foreground-like). No nudges, no resends. Neither file shows a denylist touch.
| verifier (a5a499fff7f8e57f3) | sonnet | 10:40 | 10:44 | verify.md complete, VERIFY COMPLETE, lanecheck DONE; 13 HOLDS, 1 PARTLY, 0 REFUTED; reply lost (no handback) |

## Per lens
- readiness: 10 raised (all CONFIRMED), 7 verified (6 HOLDS, 1 PARTLY), 3 text-only not sent; 2 blocker-class (READY-1, READY-3); 3 fix-induced (READY-1 by CELLS-3, READY-3 by EMBED, READY-8 by CHECKC).
- measurement: 13 raised (12 CONFIRMED, 1 SUSPECTED), 7 verified (all HOLDS; MEAS-1 magnitude 1.3-1.8x vs critic's 2.7x - MC size 4,000 vs 20,000); 6 doc.
- Overlaps: READY-6/MEAS-7, READY-6/MEAS-2.
- No answer or speed findings.

## Timing
Freeze 10:20; critics launched 10:28, both done 10:38; verifier 10:40-10:44; draft 10:50. ~30 min total.

## FREEZE DRIFT
main 6f1b40f75 -> adb2d44b7 during the round, plan.md only: [KIT-POLICY-TABLE] status text (drops COVER_Z_E3 cite, which the design itself asked for) and a new [ANCH-AT] row. No finding moves.

## Process observations
- Both critics and the verifier "ended without delivering a report through SubagentHandback": every final reply was lost, exactly as §1 predicts; the FILES + lanecheck .done markers carried everything. No resend needed.
- Exporting the subject and a build-tree data slice (git archive, chmod a-w) into the round dir let critics run tree_drill.py without a worktree; the coordinator's dry run caught that tree_drill needs src/core/*.inc (a generated-but-committed file) before briefing.
- Fix-induced findings dominated the blocker class again (3 of the round's design blockers came from rev 1.1's own fixes) - yet the launcher ruled readiness + measurement only, no fix-induced lens. Readiness caught them because its "every reader of what it changes" question reaches the loader and the STORE checks.
- MEAS-1's magnitude differed between critic (4,000 trials) and verifier (20,000): a critic's Monte Carlo figure quoted as a ratio ("~3x") needs its trial count large enough that the ratio is stable.
- Blinding: coordinator listed (names only) an earlier round dir while looking for the DELIVER shape; no content read. The skill could say where the DELIVER template lives (it is fully specified in §5 + lanecheck's header).

## Proposed changes
1. Skill §4 readiness lens: add "for each new or changed DATA ROW SHAPE the design writes (a column's content, an input, a section), run the build tree's LOADER over it (read its refusal paths): a format the loader refuses is a blocker no spec hunk fixes" (motivated by READY-1: spec text at S2c, loader untouched, S2e's set unloadable).
2. Skill §4 readiness lens: add "when a design omits data from an EMBED or copy, list every check that compares the copy with its source" (READY-3: three STORE compares red in the correct build).
3. Skill §4 simulate lens: add "a verdict table over gates (FULL/PARTIAL/REFUSED/HELD) gets a first-match drill on constructed run outcomes, with each clause's key domain stated; a clause unreachable under one reading is a finding" (MEAS-2), and "a seeded draw described as noise: check the seed varies across the re-runs the statistics assume independent" (MEAS-1).
4. Skill §6.2: a verifier re-running a Monte Carlo finding uses at least 5x the critic's trials and reports both figures (MEAS-1).
5. COMMON template: say that a design's drills that read the repo take an EXPORT of the build tree, and the coordinator dry-runs every drill before briefing (saved both critics the tree_drill failure).

## Framework notes
- Coordinator pattern, 2-critic re-check: 30 min wall, one turn of manager attention. All three nested final replies were lost; file + lanecheck delivery made it irrelevant - evidence the files-only rule is load-bearing, not a precaution.
- A design-mode round needed no binary; a read-only git-archive export (subject + build-tree data slice) replaced the worktree entirely. Fits any design round whose evidence is scripts over committed data.
