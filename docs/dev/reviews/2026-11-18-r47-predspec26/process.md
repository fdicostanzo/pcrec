# process: crit-predspec26 (r47, 2026-11-18), coordinator notes
- 12:49 freeze. SUBJECT predicates_draft.md @ 29c16a6ba (rev 26; main HEAD b850ee1 holds the same draft). Last reviewed rev 25 @ db77f9daed0f; rev 25.1 @ 8b6291f5d unreviewed. Rulings: COND-FAMILY.md @ b850ee1 (adds a 15-line MANAGER CORRECTION entry AFTER the subject commit: a later manager reading -> RULING hand mapping). decisions.md/plan.md last change @ 8949a92.
- Blinding: coordinator saw b850ee1's commit body via git show --stat (body = one-line subject restatement + trailers; no lane-report content). Entry 3632-3645 references the denied report's section name only.
- Evidence sanity: predspec26_model.py from R/tree, byte-identical to committed .out (111 of 111).
- No ORDER/SWAP switch in the engine (only PREDSPEC26_SABOTAGE).
- 12:53 launched 5 critics (RESTRUCTURE opus, SIMULATE opus, MODECLOSURE opus, RULING opus, CHANGETABLE sonnet), all returned in the launch turn (~4-10 min each; final replies undeliverable as expected); all 5 files CRITIC COMPLETE, lanecheck .done for all 5.
- Raised: RESTRUCTURE 8, SIMULATE 10, MODECLOSURE 7, RULING 7 (+ ruling table + hand mapping), CHANGETABLE 4 = 36.
- Overlaps: nullable meaning x3 (SIM-1, MC-6, RUL-1); §5.4 ${} row x2 (RES-1, CT-1); `0` in parts x2 (MC-1 run, RUL-5 hand); export read-out (RUL-4, CT-4 partly); label-mark (RUL-3 status, CT-3 cite).
- 13:02 verifier (opus) launched over 14 grouped items (V1-V14, the drill-backed CONFIRMED findings); returned in the launch turn, ~7 min, VERIFY COMPLETE, 14 of 14 HOLDS, lanecheck .done. Text/quote findings verified inline by the coordinator (sed/grep on the frozen copy): RES-1/CT-1, RES-2, RES-5, RES-6, RES-7, RUL-2, RUL-3, RUL-7, CT-2, CT-3, CT-4(ii) all hold as quoted.
- 13:09 FREEZE DRIFT: main gained 6 COND-FAMILY entries (0d9361252..3c3ebae99, the conditional: when-default, guarded form, when-test, when-peek RULED). Not homed in the subject -> hand mapping in the draft. decisions.md/plan.md unchanged since 8949a92.
- No review worktree (design mode). No critic stalled, no resend, no nudge. No blinding leak observed (critics cited only the frozen copies; RULING quoted the record only).
- 13:15 draft review.md written (round ~25 min from freeze to draft). Per lens raised / verified: RESTRUCTURE 8 (1 by verifier V14, 6 inline, 1 PLAN); SIMULATE 10 (10 by verifier); MODECLOSURE 7 (7 by verifier); RULING 7 (1 V1, 5 inline, 1 SUSPECTED); CHANGETABLE 4 (inline). Consolidated: 6 answer, 13 design, 4 evidence, 5 doc, 1 maintenance.

## Process observations
- Every critic and the verifier returned within the launch turn (4-10 min); pre-created files + CRITIC COMPLETE + lanecheck --dir worked with no resend. Narrow, two-sub-part briefs over frozen copies in R/subject + a runnable R/tree again cost no setup per critic.
- Three lenses spent effort on the same nullable finding (A1); acceptable as corroboration, but the overlap came from three briefs all naming hit-carry/nullable. A brief's drill list should be assigned to ONE lens per topic.
- Mid-round FREEZE DRIFT (six conditional rulings in ~20 min) was found only by the hand-back diff; with rounds this fast, a single hand-back re-diff suffices.
- The lens table has no row for "a restructure must lose nothing"; fix-induced fitted with a rewritten question. Worth a named sub-part.

## Proposed changes
1. Skill §4 fix-induced: add "When a revision REPLACES prose or a table with a new table that is 'the statement', map every fact of the replaced text to a cell or a kept sentence, and check each cell against the subsection it summarises (2026-11-18 r47 predspec26 RESTRUCTURE: 7 of 8 findings; an unsourced cell, a dropped default, a missing row)."
2. Skill §4 simulate / mode closure: "A rule proved on one witness whose FIRST item is already the edge case cannot separate the rule from its rivals: drill the edge case in SECOND place and at `min >= 2` (r47 A1, three lenses)." And: "for each CHECK cited as support, mutate one arm; a check no mutation of its arm can move shares its source (r47 N3, CS3)."
3. COMMON template: "State the minimum witness length your pool reached; a 0/0/0 below the witness's length is not evidence (r47 A4 needed length 7)."
4. Skill §5: assign each named drill topic to ONE lens in the briefs (r47: hit-carry/nullable named in three briefs).

## Framework notes
- Coordinator pattern again cheap: freeze -> draft ~25 min, 6 agents, no manager wake-ups. Inline verification of quote/grep findings by the coordinator plus one verifier for drill items split the load well (14 drill items in 7 min).
