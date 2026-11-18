# process — crit-predspec25 (coordinator)
- 23:47 freeze: subject draft db77f9daed0f (rev 25) on main 97e4fe96becd; rulings decisions/plan at 838499cf9; record COND-FAMILY at 97e4fe96b (last entry 5a25ffa85 23:16). predicates_future.md differs between db77f9dae and 97e4fe96b (+18 lines, the lane's later commit): copies taken at 97e4fe96b.
- setup: R/subject + R/tree read-only; evidence re-run byte-identical (rc 0).
- lanecheck dry-run on an empty pre-created file: see below.
- 23:50 lanecheck works on --deliver (empty sections reported); COMMON says end on 'DONE rc=0'.
- 23:52 launched 5 opus critics (ruling, simulate, modeclosure, fixinduced, census), background, unnamed. All returned in the launch turn (9-15 min each: modeclosure 9.0, ruling 10.5, census 12.4, simulate 13.2, fixinduced 14.8 min); every file complete with CRITIC COMPLETE and .done records; no resend, no nudge. Their final replies were lost ("ended without delivering a report through SubagentHandback"): FILES carried everything, as the skill predicts.
- findings: ruling 10, simulate 8, modeclosure 6, fixinduced 16, census 8 = 48 raw.
- 00:04 verifier (opus) launched over 9 groups (V1-V9); returned in the launch turn at 00:13 (8.9 min), verify.md complete, VERIFY COMPLETE. Final reply lost again; file carried it. 0 REFUTED; PARTLY: CENSUS-1 count (6 -> 7), CENSUS-5 (10 -> 11; "no row" framing), FIXINDUCED-6 framing, RULING-4, FIXINDUCED-7 (§4.3). Verifier ADDED: §8 ~4760 (min), four more E-CTX-2 readers, RX9 unchecked + encodes the plus-operands reading.
- 00:15 drafted review.md (11 groups, 5 proposed owner questions). Freeze drift: none. No review worktree (design mode). Time freeze -> draft: 28 min.
- Per lens: ruling 10 raised / 10 verified (1 PARTLY); simulate 8 / 8; modeclosure 6 / 6 (2 SUSPECTED held as such); fixinduced 16 / 16 (2 PARTLY); census 8 / 8 (2 count PARTLY). Overlaps: A found by 4 lenses, B by 3 (4 ids), C by 2, D by 3, E by 2, F by 3.
- Blinding: no leak noticed; critics cited only R/ copies. The draft's rev 24.3 changelog NAMES the previous review file; COMMON told critics not to open it; no critic cited it.

## Process observations
- Five opus critics at ~9-15 min each, all complete on first pass, because every brief was one question over R/ copies with a diff from the last reviewed revision. The diff file (rev 24.2 -> 25) let a three-revision re-check be scoped without the critics reading 8,000 lines.
- Overlap was high (group A by four lenses); acceptable for answer-level items, but the re-check of an 8,000-line draft might staff a dedicated "withdrawn-term sweep" (sonnet) and drop one opus lens.
- Every subagent's final reply was lost ("ended without delivering a report"); files + CRITIC COMPLETE markers made it irrelevant.

## Proposed changes
1. Skill §4 simulate lens, append: "diff the evidence's tokenizer/parser predicates against the subject's parse-rule sentences; a predicate with no sentence is a finding (2026-11-17 r43: the engine's starts_operand restored a clause the draft dropped)".
2. Skill §4 ruling-check lens, append: "diff each RECORD restatement against the question the owner agreed to, list by list (2026-11-17 r43 B: 'the right side of &' existed only in the record's restatement)".
3. Skill §4 fix-induced lens, append: "on a re-check that withdraws rules, grep every term of each withdrawn rule over the WHOLE subject and list the unmarked hits (r43: 8+ unmarked readers beyond the lane's marked list)".
4. COMMON template for a multi-revision re-check: ship the diff from the LAST REVIEWED revision as a file in R/subject/ (worked here).

## Framework notes
- The coordinator pattern ran a 5-critic + verifier round in 28 minutes with zero resends; nested-agent final replies were lost 6 of 6 times and did not matter, which confirms "everything travels as files" as the load-bearing rule.
- 00:16 (after hand-back) the manager wrote that critics reported the coordinator "had stopped" and their handbacks failed. Observation: the critics' final replies were undeliverable (6 of 6 "ended without delivering a report"), which they and the manager read as the coordinator having stopped. In fact the critics had returned within the coordinator's launch turn, and the coordinator read their FILES as soon as they returned. The manager's resume message crossed with the hand-back. Proposed: brief critics that a failed handback is EXPECTED and needs no escalation to the manager; the CRITIC COMPLETE line in the file is the delivery.
