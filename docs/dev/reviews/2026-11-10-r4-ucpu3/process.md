# process.md — critic round ucpu3 (code)
- 18:58 freeze: SUBJECT 2b5adbff1, BASE 7d74499bc, main eb83f0902; rulings commit (decisions/plan) 79440bf19. Review tree built 18:59 (nice -j2, rc 0, ~1 min); BASE export built 19:00.
- Denylist note: allowed docs/dev/lanes/ucpu3b_evidence/*.py (the test generator) to critics, denied its .tsv + the report.
- 19:01 launched 5 critics (answers opus, admit opus, emit opus, checks sonnet, rules opus). All five returned in the launch turn (~7-8 min each); all files complete, lanecheck .done present for all. The Agent tool reported "no report delivered" for each: the FILES carried everything (skill §1's rule held).
- admit ran ~75 compiles (over the ~50 budget; it says why: a shell read stripped backslashes, batch rerun).
- checks put findings 1-8 under the PROBED-AND-HELD heading (format slip; content intact).
- 19:11 verifier (sonnet) launched; returned ~5 min, 20 sections, all HOLD (checks-4 count 269 vs critic's 170 on a wider range). EMIT-6 (suspected) not verified.
- 19:20 freeze re-diff at hand-back: no drift (main still eb83f0902; subject unchanged).
- Per lens: answers 1 (doc, inherited) | admit 6 (doc/diag/naming; 2 overlap rules, 1 overlaps emit) | emit 6 (5 confirmed, 1 suspected; 1 overlaps admit, 1 overlaps rules) | checks 9 (all test gaps, 3 answer-risk) | rules 11 (design/maintenance/doc).
- Time: freeze 18:58 -> draft ~19:22 (~25 min).

## Process observations
- All five critics + verifier returned inside the launch turn (foreground-like) despite run_in_background; the Agent tool reported "no report delivered" each time, while every FILE and .done was complete. Files-as-transport held fully.
- Narrow one-question briefs again finished in 7-8 min each with no resends or nudges.
- Overlap was useful, not waste: three findings were found independently by two lenses (ADMIT-1/RULES-6, ADMIT-4/EMIT-2, EMIT-1/RULES-4, ADMIT-6/RULES-7), which raised confidence before the verifier ran.
- The checks lens's cheap PLANT method (hand-edit a copy of the emitted C, run the corpus cells; no compiler rebuild) produced the round's most consequential findings while a full suite held the box. The lens table's check-adequacy row speaks of plants without naming this zero-build form.
- admit overran the ~50-compile budget (75) and said so; a budget stated in COMMON is advisory for agents batching probes.
- checks wrote findings 1-8 under the PROBED-AND-HELD heading; lanecheck passed (both sections nonempty). Form check cannot see heading misplacement.

## Proposed changes
1. Skill §4 check-adequacy row, add: "When the box is held (a suite running) or the subject emits a matcher, plant in a COPY of the emitted C and run the subject's own corpus cells against it: no rebuild; report SAME plants per site (2026-11-10 r4 ucpu3: 10 SAME plants found in 281 cells, zero builds)."
2. Skill §5 COMMON template: state compile budgets as a HARD cap with "if a batch must be rerun, count it" (r4 ucpu3: 75 vs 50).
3. lanecheck DELIVER for critics: add `cites: ^### [A-Za-z]+-[0-9]+ in PROBED-AND-HELD -> Findings`-style guard, or a simpler rule "no `### <LENS>-n` heading under PROBED-AND-HELD" (r4 ucpu3 checks).
4. critics.md lesson: a generated-from-oracle corpus reaches but does not discriminate; demand interval-edge cells and a succeeding retry witness for any character-stepped or retry machine.

## Framework notes
- The coordinator pattern ran end to end in ~25 min on a held box with zero manager wakes: one build + one BASE export, 5 critics + 1 verifier, all via files. Strongest evidence yet that a coordinator can run a code round "beside" a full suite when critics are restricted to single compiles and emitted-C plants.
