# process — critic round altcode (coordinator crit-altcode, opus)
- freeze 2026-11-06 20:58 EST: SUBJECT 4cc816446 BASE 80341284e; rulings at main eeff89640 (decisions/plan); main HEAD d49361e30
- review tree worktrees/crit-altcode built 20:59 (nice -j2, rc 0); BASE git-archive export $R/base built rc 0
- regime spellings checked: -e utf8 --engine=vm stamps; --emit-facts req_pieces; -I tests/findings/adversarial --analysis=uniform rc 0
- lenses: emit (opus), contract (opus), slot+ruling+goals+standing+house (opus), checks (sonnet), trade (sonnet)
- critics launched ~21:10; all five returned in-launch (no handback text); files read next
- 21:14 all five files complete (STATE done, lanecheck .done present for all five): emit 3, contract 2, slot 8, checks 7 (+1 buried in PROBED: S238 anchor count), trade 8
- overlaps: CON-1 = SLOT-1 (abi 95 half-bumped); EMIT-3 ~ TRD-1 (utf8 island flip; TRD-1 says broader than "near the knee"); EMIT-1 ~ TRD-2 (rule M kills byte islands; TRD-2 measured one case FASTER) ; SLOT-8 ~ EMIT-2/TRD-4 (retry row family)
- checks critic filed a CONFIRMED regression (S238 SAB_COUNT 5 vs 6 anchors) under PROBED-AND-HELD, not Findings: promoted to CHK-8 by coordinator
- PLANT-REQUEST (CHK-1 trie erosion): declined — four builds in the owner's evening hold; disposition proposes the cheap check fix instead

## Per agent
| agent | model | launched | ended | final state |
|---|---|---|---|---|
| emit | opus | ~21:01 | ~21:14 (766 s) | file complete, lanecheck DONE, 3 findings, ~1,350 compiles |
| contract | opus | ~21:01 | ~21:11 (584 s) | file complete, DONE, 2 findings (doc), 0 answer movers over ~1,400 compiles |
| slot | opus | ~21:01 | ~21:08 (398 s) | file complete, DONE, 8 findings |
| checks | sonnet | ~21:01 | ~21:10 (515 s) | file complete, DONE, 7 findings + 1 CONFIRMED regression misfiled under PROBED (promoted CHK-8) |
| trade | sonnet | ~21:01 | ~21:06 (292 s) | file complete, DONE, 8 findings, ~75 compiles |
| verify | opus | ~21:15 | ~21:21 (375 s) | verify.md complete, DONE; 14 HOLDS, 0 REFUTED, 2 sub-claims not verified |
All six agents returned inside their launch turn with no handback text ("ended without delivering a report"); every result travelled as a FILE, as the skill expects. No nudges, no resends. No TaskStop needed.
Review worktree removed 21:23 via wtprune --force --quiet-min 1. Freeze drift: none (decisions/plan diff eeff89640..main empty; subject sha unchanged). Time freeze -> draft: ~25 min.

## Per lens
| lens | raised | verified | top severity | overlaps |
|---|---|---|---|---|
| EMIT | 3 | 3 HOLDS | speed (130x) | EMIT-3=TRD-1; EMIT-1~TRD-2 |
| CON | 2 | 1 HOLDS, 1 not run (doc) | doc | CON-1=SLOT-1 |
| SLOT | 8 | 5 quoted HOLDS | maintenance/design | SLOT-5 explains EMIT-3 |
| CHK | 7+1 | 2 HOLDS (CHK-2, CHK-8) | maintenance | - |
| TRD | 8 | 5 HOLDS | speed | as above |

## Process observations
- The decisive finding (EMIT-1) came from a critic told to diff PRE-EXISTING behaviour by instruction count on the bench family; the subject's own evidence evidently judged by program size and census, which read the loss as a win. The emitted-vs-replaced lens earned its opus slot.
- A sonnet critic filed a CONFIRMED regression (S238 anchor count) under PROBED-AND-HELD because it was a script-reported fact, not one it derived. The output format does not say "anything that fails at SUBJECT and passed at BASE is a Finding, whoever found it".
- Two critics independently caught the same abi miss: cheap redundancy, fine.
- Evening hold: COMMON forbade wall-clock timing and allowed instructions:u counts only; every speed claim came out as counts and reproduced to +-3 instructions. Good fit for a hold window.
- The plant request (CHK-1) was declined for box load; the skill gives no rule on when a coordinator should build plants. A cap of "plants only outside the owner's hold" would settle it.
- The design's ERRATUM and K139 point into denied lane files (rulings R1/R2/R4); two critics could only say "judged by a ruling I cannot read". The manager should check whether R1/R2 carry an OWNER exception (TRD-1 under D186).

## Proposed changes
1. COMMON template, Output format: add "A check, script or gate that is red at SUBJECT and green at BASE is a Finding (CONFIRMED), even when a tool reported it; never file it under PROBED-AND-HELD." (motivated by CHK-8)
2. Skill §4 lens table, emitted vs replaced row: add "For a rewrite upstream of a CHOICE it does not own (island, rung, engine route), measure matching instructions on the bench family that choice serves, BASE vs SUBJECT, both directions; program bytes are not a proxy (2026-11-06 altcode: w-256 program -23%, work x130)." (EMIT-1)
3. Skill §3.2: "Plant builds requested by critics: at most three, never during the owner's evening hold or a bench window; else the finding stays SUSPECTED and is PLANned." (CHK-1)
4. critics.md lessons: the three guide lessons in review.md.

## Framework notes
- The coordinator pattern ran end to end in ~25 minutes for a 73-file code subject with zero manager turns, zero nudges, and every nested reply lost as expected; FILES + lanecheck/.done carried everything. Evidence for keeping "results travel as files" as the core rule.
- Fit elsewhere: any "fan-out, verify, draft for a ruling" job with a frozen subject (e.g. a pre-landing perf audit of a branch against a bench family) fits this shape; the verifier step was what made the speed numbers trustworthy enough to propose a landing block.
