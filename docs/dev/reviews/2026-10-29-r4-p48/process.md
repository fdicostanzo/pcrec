# process — critic round p48 (design)

Coordinator: opus, started 12:55 (2026-10-29). Subject frozen: docs/dev/lanes/p48_report.md @ b1ecc22ad5ac4dad89d0e11d8b6081176c7913df (copy: subject_p48_report.md). Base code for the build: main @ 02a05485148faadf96910332e4386ba0ac9e3268 (doc written at b05ccfc0b).
Review tree worktrees/crit-p48 @ 02a054851, `nice make -j2` unlocked, 12:56 -> ~12:57, exit 0 (box held by queue job 690 at the time; unlocked build did not wait).

## Profile -> lenses
Profile: a new table (SCAN_SITE_ROWS) + priced rule; a measured quantity (break-even, card); a build proposal (entry rule now); an answer-identity claim BY ARGUMENT (entry rule, relaxation); rulings relied on.
Launcher asked for a light round (2-3 lenses, soundness included). Chosen:
| lens | model | question | why |
|---|---|---|---|
| sound | opus | apply ENTRY and RELAX as written to the emitter's real output; does any answer move vs libpcre2? | answer identity by argument |
| design (premise + slot tracing + goals + ruling check + both standing questions) | opus | true premises, one slot per fact | new table + pricing; measurement folded in as premise |
| cost (cost and overlap) | sonnet | cost/benefit/trigger/D153 overlap of the manager's 3-way split | build proposal; launcher asked for it |
Not run: simulate (the census is the lane's simulation; design lens recomputed masses instead), measurement as its own lens (folded into design's premise item).

## Agents
| agent | model | launched | file complete | state |
|---|---|---|---|---|
| sound | opus | ~12:58 | 13:09 | lanecheck DONE; 53 compiles; built 2 twins |
| design | opus | ~12:58 | 13:08 | lanecheck DONE |
| cost | sonnet | ~12:58 | 13:03 | lanecheck DONE; built 1 twin |
All three returned within the launch turn (background agents, ~7-12 min); their final replies were not delivered ("ended without SubagentHandback") — files carried everything, no resend needed.

## Per lens
- sound: 2 findings (both CONFIRMED, design/check), 0 answer moves over ~2,000 answer lines; positive control (bounded head, jump deleted) moved 8/84 answers.
- design: 10 findings (8 CONFIRMED, 1 SUSPECTED, 1 mixed). Gap noted: D153 overlap (optloop denylisted), evidence raw rows (DESIGN-9 SUSPECTED).
- cost: 8 findings (6 CONFIRMED, 2 SUSPECTED).
Overlaps: SOUND-1 = COST-1 = DESIGN-7(b) (dfa_start_is_scan_head is the s0head prefilter predicate too); DESIGN-7(a) = COST-8 (key on the kill fact / one helper); SOUND-2 ~ COST-2 (entry checks: the unbounded witness is text-only; check (2) of run_scan_edge_census.sh asserts the removed line); DESIGN-8(c) = COST-5 (card trigger names row 3).
Blinding leaks: none noticed. COST read plan rows [LANDWALK-EDGEPRICE]/[PRIOR-COST-UNIFY] by tag (allowed).

## Verifier
sonnet, launched ~13:11, verify.md complete ~13:18 (lanecheck DONE, VERIFY COMPLETE). Final reply lost like the critics'; file carried it.
Value added: corrected two counts (census manifest 7 vs 6 rows losing the line; 9 vs 11 `scan_span != 0` spellings), REFUTED DESIGN-5(a) against the doc's stated uniform prior, downgraded DESIGN-2 / SOUND-2 / DESIGN-3 to PARTLY with reasons.
Review tree removed 13:20 (wtprune --force --quiet-min 1). Draft complete 13:20: ~25 min from freeze to draft.

## Process observations
- All four nested agents (3 critics + verifier) finished within their launch turn and their final replies were not delivered; the file + lanecheck .done protocol made that a non-event. lanewatch was not needed.
- The subject was written at an older base (b05ccfc0b) than the build base (main 02a054851). Telling critics both commits and asking them to report any cited code that moved worked: three critics checked it independently (it had not moved for the cited sites).
- Three lenses converged on the same top finding (F1). For a light round that is redundancy, not waste: it is the finding that would have shipped in the build brief.
- The light 3-lens set was enough: sound found no answer issue (with a positive control), design carried premise+slots+goals+rulings+standing questions in one opus critic (10 findings, no sign of overload), cost (sonnet) added the concrete site/check counts the design lens did not look for.
- Denylisting docs/dev/optloop/ blinded the D153 check partly (design noted it as a gap; cost used plan rows instead).

## Proposed changes
1. Skill §3.1 (design mode): "also record the commit a BUILD would land on (normally main HEAD) and build the review tree THERE, not at the doc's base; tell critics both and make 'cited code that moved' a finding." Motivation: this round's doc base was 4+ commits behind main with emit_dfa.c changed; the instruction let every lens verify the citations against the landing code.
2. COMMON template, Output format: "Say which PART of the design each finding hits" (a part list from the coordinator) — made consolidation across lenses mechanical here (ENTRY/RELAX/TABLE/STAY).
3. critics.md lessons: the three in review.md "Lessons for the guide" (trace a named site's other readers; a sabotage plant needs a named detector; a transparent priced row states its missing-price verdict).

## Framework notes
- The coordinator pattern ran a light round in ~25 min wall, with zero resends, because every nested agent delivered by file. Evidence: four lost final replies, four complete files with .done seals.
- The verifier's main value in a design round is calibration (counts and premises), not refutation of answer claims: 1 REFUTED part, 4 PARTLY, rest HOLDS.
