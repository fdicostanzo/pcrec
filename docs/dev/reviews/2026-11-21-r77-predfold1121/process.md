Sun Nov 22 12:01:18 AM UTC 2026 critics returned in launch turn; 5 opus, 8-14 min
- Setup ~10 min: R/subject (6 docs + base74 + diff + record + doc_format), R/tree mirror; evidence re-run by coordinator before briefing: predscope 2 FAIL (CLOSEDB, DOC), predfix61 DOC FAIL, predarr DOC FAIL (report absent: mirror artifact), predasc cannot run (git show). Not told to critics; EXAMPLES found all of them independently.
- Launched 5 opus critics (ruling, examples, general, modes, fixind) in one message; all returned in the launch turn (8-14 min), all files complete with CRITIC COMPLETE; final replies undeliverable (expected).
- Findings: RULING 12, EXAMPLES 4, GENERAL 12, MODES 12, FIXIND 17 = 57 raw; heavy overlap on three roots (array scope vs sealed piece: GENERAL-1/MODES-1/FIXIND-2; bound-condition carve-out: RULING-1/GENERAL-3/FIXIND-4; library helper captures: RULING-6/GENERAL-7/FIXIND-16) despite one-root-per-lens assignment: the roots were not foreseeable at briefing.
- Verifier (opus) 15 grouped items, ~8 min: 13 HOLDS, 4 PARTLY (V-2 spellings leg refuted, V-8 GENERAL-8 falsity conditional, V-13 line 1117 wording-only, MODES-10 answered by core.md:653), 0 REFUTED. Its key add: A1 is two OWNER rulings colliding (array-scope record 5744 vs case 2 6765).
- MODES-4 (0 in a FIND-ALL place) was left out of the verifier's list by the coordinator: marked not verified, PLAN.
- FREEZE DRIFT: lane/pred-rev28 moved 882bcf330 -> cff981597 mid-round (+4 OWNER entries, none a ruling); hand-mapped in review.md. main decisions/plan unchanged.
- Draft written ~00:15Z; total round ~45 min wall.

## Process observations
- All six agents returned in the launch turn; no monitoring needed. Pre-created files + CRITIC COMPLETE worked again.
- Despite one-root-per-lens assignment, three roots were found by three lenses each (array scope, bound-condition exemption, helper captures): the roots were not knowable at briefing; the overlap cost little and the triple find raised confidence.
- The coordinator's own pre-brief evidence re-run found the stale-evidence finding before any critic; it was kept out of the briefs and EXAMPLES found it independently.

## Proposed changes
- critics.md / skill §5 design mode: "The coordinator RE-RUNS every evidence script before briefing and records red checks in .coord/ (blind); a red committed evidence at the freeze is a finding even if no critic reports it." Motivation: three of four scripts red at the freeze, all committed .out green.
- RULING lens brief (skill table, ruling check row): "for each ruling in force, grep the record for EARLIER rulings tagged with the same pieces and check each pair still agrees" (A1: array-scope 2026-11-19 vs case 2 2026-11-21, found only by the verifier).
- pred manager skill: after a DIRECT fold (no lane), re-run every evidence DOC check reading the folded pieces in the same commit.

## Framework notes
- Coordinator + fan-out on a 1,530-line design diff: 5 opus critics in parallel, ~14 min wall to all files, verifier 8 min; the coordinator's context held only files (~60 KB). The pattern fits a fold review well; the verifier grouping by root (15 items from 57 raw) is where consolidation happens.
