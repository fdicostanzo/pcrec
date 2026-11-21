# process.md — round covs1 (coordinator)

freeze: SUBJECT 65ad7d226, BASE 91bae2d98, main 5d0e75680 (decisions/plan freeze). 17:00 start.
builds: review tree (unlocked nice -j2, ok), BASE export (ok), 9 planted compilers (incremental copies, ok, ~10 min total).
kit: cmp.sh, facts.sh, ans.sh, oracle; sanity-run on ab|abc|ad, a{40}(?:b|cc) on S3220, a*?a on S3224.

## agents
- 17:05 launched 5 critics (conform opus, emitted opus, contract opus, checks opus, trades sonnet), one message, background. All returned in the launch turn (foreground-like), files complete, lanecheck .done present for all 5; wall 3-10 min each. Final replies lost ("ended without SubagentHandback"); files carried everything (as the skill predicts).
- findings: conform 5, emitted 2, contract 3, checks 7, trades 5 = 22. Overlap: CONFORM-2 == CONTRACT-1 (view newline k).
- coordinator built extra plant V16 (row compare reduced to memcmp 16 bytes, the CHECKS-5 nearby regression): aé|bè utf8 becomes a cover, wrong answers on "aè"/"bé" vs libpcre2; 63 kitproof verdict/facts rows: 0 flip. CHECKS-5 -> CONFIRMED answer-level for the escape.
- 17:14 launched verifier (sonnet), 16 items; returned in launch turn (~4 min), VERIFY COMPLETE, .done present: 14 HOLDS, 2 PARTLY (CONFORM-4, CHECKS-2), 0 REFUTED. No REFUTED to re-run.
- freeze drift check at hand-back: main 5d0e75680 -> 8f55f4c45, decisions.md/plan.md/cover_cap.md unchanged.
- draft review.md written ~17:25; total round wall ~25 min from launch message.

## per lens
| lens | model | raw | verified | top severity | overlaps |
|---|---|---|---|---|---|
| conform | opus | 5 | 4 (1 PARTLY) | listing | CONFORM-2 = CONTRACT-1 |
| emitted | opus | 2 | 2 | speed | - |
| contract | opus | 3 | 2 | listing | CONTRACT-1 = CONFORM-2 |
| checks | opus | 7 | 5 (+CHECKS-5 by coordinator plant) | answer (escape) | - |
| trades | sonnet | 5 | 4 | CI speed/coverage | - |

No brief confusions surfaced; no blinding leak noticed (verifier was explicitly allowed the critics' files). No resends, nudges or stalls. All final replies were lost (harness: "ended without SubagentHandback"); files + lanecheck .done carried everything.

## Process observations
- Critics returned within the launch turn despite run_in_background: the skill's §6.1 note held; reading files at once worked.
- Prebuilt per-row plant compilers removed every critic-side build question; the checks lens did 90 cross-plant compiles in minutes and found CHECKS-3 from them.
- The design §5.4 "unique witness" column was a claim nobody had measured; a cross-plant matrix is cheap once plants exist.
- The trade lens (sonnet) found the most consequential non-answer item (TRADES-1) by reading a generated table's header.
- The "no timing" constraint was honoured by using perf instruction counts (pinned, 12 runs) for EMITTED-2; that is evidence of mechanism, not a G3 verdict.

## Proposed changes
1. skill §3.2 (code mode, subject moves sabotage rows): "build plants/<ID>/ per moved row from the row's BEFORE/AFTER (incremental copy of the review tree, unlocked nice -j2) and list them in COMMON" (this round: 9 plants ~10 min; every check-adequacy probe ran without a build).
2. skill §6.2: "a nearby regression a critic names but cannot build is built by the coordinator as one more plant and run over cases.tsv's verdict/facts rows (not the suite) before drafting" (V16: SUSPECTED -> answer-level gap in ~5 min).
3. critics.md / trade audit lens: "diff the HEADER of every regenerated table (shard count, measured-row count, defaults used) BASE vs SUBJECT" (TRADES-1).
4. check adequacy lens: "run every plant on every witness (cross-plant matrix) to test 'unique witness' claims" (CHECKS-3).

## Framework notes
- Coordinator pattern held cleanly: 5 critics + 1 verifier in ~25 min wall, manager woken once. The coordinator's own build work (review tree, BASE, 10 plants) was the critical path, not the critics; giving the coordinator build authority for plants (unlocked, incremental) is what made a code round with many sabotage rows this fast. Fits any round whose subject moves checks: the plants are the shared fixture.
- late relay from trades critic (after hand-back): content identical to trades.md already drafted; it reports overwriting trades_deliver.txt with a placeholder then rewriting it (original coordinator-written deliver lost; lanecheck passed on the rewrite). Process note: critics should never write their DELIVER file.
