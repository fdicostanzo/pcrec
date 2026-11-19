# process log: critic round predspec27 (DESIGN mode), coordinator

## Freeze (17:25)
- SUBJECT: docs/design/predicates_draft.md rev 27 @ a088fe542c63e4d894c0df1937686dfb221481a7 (git log -1 -- the doc; main HEAD b22285a36 is the merge, doc identical).
- Build commit: main HEAD b22285a3606a; DESIGN-ONLY language doc, no product code, no review tree built (per launcher).
- Last REVIEWED revision: rev 26 (r47) @ 29c16a6ba; rev 26.1 (2d7f29ed6) unreviewed. Multi-revision re-check: diffs 26.1->27 (636 lines, primary) and 26->27 (1390) shipped in R/subject/.
- RULINGS freeze: decisions.md/plan.md last touched 57fcb5737 (plan.md moved at b22285a36: an unrelated [RUN-POS-SET] status line, not a ruling). RECORD: COND-FAMILY.md lines 3809-3905 @ b22285a36 (last record commit 84610b4fd, ANCESTOR of the subject: no reading postdates the subject). Copied to R/subject/record_2026-11-18_afternoon.md.
- Round dir absent at start; created. R/ read-only (chmod a-w). R/tree mirrors docs/dev/lanes/{predspec27,predspec261,predspec26,rxmodel}_evidence + the draft. Sanity: evidence re-run from R/tree = 21 of 21 OK, output identical to committed .out.
- Review number: provisional r48 (r47 is today's last committed; concurrent crit-archdense round unnumbered); manager assigns final N.
- No ORDER/SWAP switch in the evidence; the sabotages s1-s8 are its switches (COMMON asks whether each reverses something carrying meaning).

## Lenses (5, all opus)
- RULING: owner quotes verbatim (ONLY lens), manager readings attacked, next-revision ruling table for the 5 entries; goals folded in.
- FIXIND: ANSWERS CHANGED A1-A16 cells vs their sections + restated-decision diffs (a); term grep for unmarked readers of every changed/withdrawn answer (change-table completeness folded) (b).
- SIMULATE: TYPE TABLE as text vs RULE-AS-CODE, worked examples of R.1.15/R.1.16 in real modes, mutate-one-arm, sabotage meaning, empty-set spellings, edge case second.
- MODECLOSURE: one type in every mode incl. find-all and filter role; capture-state drill for backref=capture (optional/looped/nullable/two depths); the narrowed ${$y}/\k<y> control count.
- PREMISE: assumptions of one type (a read = one-string rx; unset/array reads; two forms; under-construction class vs illegal); + standing: sibling of a family, general form + unlocks with triggers.
Rationale: profile = new table/mechanism (type table), a foundation replaced (types unified), fold of rulings with manager readings, replacing-table ANSWERS CHANGED. Census not staffed (no new marks beyond `$`/`${}` already censused; folded into PREMISE as a sub-question? no: kept out, one question per lens).

## Agents
- 17:19 launched 5 opus critics (RULING, FIXIND, SIMULATE, MODECLOSURE, PREMISE), background, unnamed. All returned in the launch turn (6.5-9.5 min each); every final reply failed ("ended without SubagentHandback"), as COMMON predicted; every file complete with CRITIC COMPLETE + a lanecheck .done. Raised ids: RULING 10, FIXIND 14, SIMULATE 5, MODECLOSURE 5, PREMISE 12.
- 17:30 rulings re-diffed at critic return: main moved to 2843924a1 (plan.md REQ-LOOKAROUND row only; not COND-FAMILY, not decisions.md, not the record): NO FREEZE DRIFT.
- Overlap groups formed for the verifier (A array/T8, B unset/VH6, C finite-label order, D T1 order, E left collision, F A11 computed label, G duplicate names, H number domain, I status criterion, J hole flags, K occurrences place, + quote items).
- 17:30 verifier (opus) launched over 14 grouped items V-A..V-N; returned in the launch turn (8.9 min), final reply undeliverable, verify.md complete + VERIFY.done. No REFUTED; PARTLY: V-C (severity answer -> design: R.1.2 already defines path order), V-L (RULING-9: L33 is classed GAP), V-M (24/72 reproduce, 14 hard conflicts).
- 17:40 rulings re-diffed at hand-back: main f733e574d; no change to decisions.md, the record, the draft, predicates_future.md: NO FREEZE DRIFT.
- 17:45 review.md drafted; critic texts + verify.md + COMMON copied to review/. No review worktree was created (design-only), nothing to prune.

## Per lens (raised / verified / severity after verify / overlaps)
- RULING 10 / 10 (R9 PARTLY) / answer 0 (co-found A), design 4, doc 6 / overlaps A, I, J, R.
- FIXIND 14 / 14 / answer 2 (A, E co-found), design 5, doc 7 / overlaps A, B, E, G, H, I, R.
- SIMULATE 5 / 5 (S5 PARTLY on count) / answer 3 (B), doc 1, maintenance 1 / overlaps B, D.
- MODECLOSURE 5 / 5 (M2 severity PARTLY) / answer 1 (B), design 3, doc 1 / overlaps B, C, D, G.
- PREMISE 12 / 10 confirmed + 2 notes / answer 4 (B, E, H, J), design 5, doc 1, notes 2 / overlaps A, B, C, E, I, R. J (hole flags) found by PREMISE alone.
- Time: freeze 17:15 -> critics complete 17:28 -> verify complete 17:38 -> draft 17:45 (about 30 min wall).

## Process observations
- Pre-created files + CRITIC COMPLETE + lanecheck worked for all 6 agents; every final reply was lost, as predicted; zero resends.
- Five opus critics finished in 6.5-9.5 min each, faster than r43's 9-15 min: the diff file + line ranges in COMMON let critics scope without reading 9,333 lines.
- Overlap was high on two roots (B unset: 4 lenses, 7 ids; A array: 3 lenses): the brief assigned drills to one lens each, but a ROOT (unset reads) was reachable from SIMULATE's empty-set drill, MODECLOSURE's find-all drill and PREMISE's "one string" assumption. Overlap here was confirming rather than wasted (each added a different consequence), but cost about one critic's worth of effort.
- PREMISE was the most productive lens (12 ids, the sole finder of J, and the general form); RULING the most precise (verbatim diff tool `ruling/q.py`).
- The verifier's PARTLY on V-C (the draft's R.1.2 already defines the order) shows two critics took "values' order" from lift-order's text without checking T1's definition of an rx's order: a premise lens should read the subject's own DEFINITION of a term before testing a sentence using it.

## Proposed changes
1. Skill §4 premise row: add "read the subject's own definition of each term a tested sentence uses (an order, a domain) before constructing a counter-model; a counter-model built on a term the subject defines otherwise is a severity overstatement (r48 V-C)".
2. Skill §5 / COMMON template: when a fold introduces a STATUS table, COMMON lists the draft's printed RULED worked examples (by section) and assigns ONE lens to run all of them through the table (r48 A: three lenses found the same silent move by three routes).
3. Skill §5 drill assignment: assign drills by ROOT CONCEPT as well as by drill name ("unset / empty values: SIMULATE only"), since one root is reachable by several named drills (r48 B: 4 lenses, 7 ids).

## Framework notes
- The coordinator pattern ran a 5-critic + verifier design round in ~30 min wall with no manager wakes; nested replies were 0 of 6 delivered and nothing was lost, because every deliverable was a pre-created file. The round dir's R/subject + R/tree copies meant no critic touched the repo for the subject.
- Grouping findings by root for the verifier (14 items for 46 ids) kept the verifier to one pass; recommended as standard for design re-checks with heavy overlap.
