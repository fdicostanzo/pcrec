# process.md — crit-memfn-span-cards (coordinator notes)
- 08:45 freeze: subject 6f93716f6 (span_cards.md rev 0, branch lane/memfn-s2design 2948ac356); build tree main fb22c62a6; rulings freeze 80341284e (decisions/plan). Code identical subject vs main; span_pick.md and requests.md identical.
- 08:46 review tree built (nice make -j2, unlocked, ~1 min, rc 0).
- Regime spellings checked: --list-measurements, --measures=zen4-grid1 (RX_MEASURES "" , MEMFN_FORMS none on 'a/b').
- Coordinator's own notice (not given to critics): R-35 says "Sabotage ids: the kit takes its own"; doc §9 says "ids: the manager's". R-35 says "leaves DEFAULTS unchanged"; doc §8.3 recommends flipping DEFAULTS at S2e. Check the slot/ruling critic finds these.
- 08:47 launched 5 critics in one message (premise opus, meas opus, slot opus, contract opus, cost sonnet), background, unnamed. All RETURNED IN THE LAUNCH TURN (~2.5-8.5 min each; harness reported "ended without SubagentHandback", but every findings file + lanecheck .done present). lanewatch DONE rc=0 at 08:56.
- Findings raised: premise 13 (12 CONF, 1 SUSP), meas 14 (12 CONF, 2 SUSP), slot 12 (8 CONF, 4 SUSP), contract 9 (8 CONF, 1 SUSP), cost 7 (mostly CONF-by-text). Overlaps: vrun at SIMD-on (PREMISE-1, SLOT-5); DEFAULTS (B) (PREMISE-4, SLOT-3, CONTRACT-4; also my own pre-noted R-35 conflict); harness reader no digest (PREMISE-8, CONTRACT-2); four vs three constructors (PREMISE-9, SLOT-12, CONTRACT-9); derived-noise ahead of need (SLOT-10, COST-1, CONTRACT-6, MEAS-13); sabotage ids (SLOT-11, my pre-note). check C (SLOT-4, COST-5(10), PREMISE-3).
- cost critic's file uses no `###` headings per finding (format drift; content fine).
- 08:57 verifier launched (opus; several MEAS drills needed a faithfulness judgment). Returned in the launch turn (~7 min); verify.md complete, VERIFY COMPLETE, lanecheck DONE. Verdicts: most HOLDS; PARTLY on PREMISE-1/SLOT-5 (key move not forced), PREMISE-4 (a), MEAS-5 (a) second half REFUTED by text reading (no crafted input to re-run), MEAS-14 (+2/3), COST-4.
- 09:04 FREEZE DRIFT found at hand-back: main 80341284e -> 013af687c; D188 (SIMD facts per level, HOMED in span_cards rev 1) landed 08:54, mid-round; [ISL-PRICE], [XARCH-DEV] unrelated. Recorded as DRIFT-1 (FIX-NOW). Subject unchanged (6f93716f6; branch tip 2948ac356).
- 09:06 draft review.md written; critic texts + verify.md copied to review/; review worktree removed (wtprune --force --quiet-min 1). Time to draft: ~21 min from freeze.

## Per agent
| agent | model | launch | end | final state |
|---|---|---|---|---|
| premise | opus | 08:47 | ~08:55 | file complete, lanecheck DONE |
| meas | opus | 08:47 | ~08:55 | file complete, DONE |
| slot | opus | 08:47 | ~08:53 | file complete, DONE |
| contract | opus | 08:47 | ~08:53 | file complete, DONE |
| cost | sonnet | 08:47 | ~08:50 | file complete, DONE (no per-finding ### headings; ids inline) |
| verifier | opus | 08:57 | ~09:04 | verify.md complete, DONE |
No nudges, no resends, no stalls. All agents' Agent-tool returns said "ended without SubagentHandback" yet every file and .done marker existed: the files-not-replies rule carried the round.

## Per lens
| lens | raised | verified HOLDS/PARTLY | top severity | overlaps |
|---|---|---|---|---|
| premise | 13 | 9 checked: 7 HOLDS, 2 PARTLY | design (producer) | slot (SIMD-on, DEFAULTS, constructors), contract (harness path, DEFAULTS) |
| meas | 14 | 12 checked: 10 HOLDS, 2 PARTLY | design (gates/estimator) | slot-9, cost-1/contract-6 (derived noise) |
| slot | 12 | 7 checked: all HOLDS | design (DEFAULTS, cells, §7.1) | premise, contract, cost |
| contract | 9 | 7 checked: all HOLDS | answer-adjacent (CONTRACT-5) | premise-8, slot-3/6 |
| cost | 7 | 4 checked: 3 HOLDS, 1 PARTLY | check (sabotage rows) | slot-4/10, contract-6 |

## Blinding
No leaks noticed. The cost critic copied plan.md into its dir (no denied row in this round). Coordinator pre-noted two R-35 conflicts (sabotage ids, DEFAULTS) before launch and did not brief them; slot found both independently, premise/contract found DEFAULTS.

## Process observations
- Every critic and the verifier returned within the launch turn (2.5-8.5 min). Monitoring cost was one lanewatch call.
- The measurement lens, run as opus with explicit constructed-outcome drills (from the simulate lens's text), was the most productive (14 findings, 10 design-level). Its drills reproduced exactly under the verifier.
- Five lenses with heavy overlap on three facts (SIMD-on vrun, DEFAULTS, derived noise): three-way overlaps are confirmation, but the slot and premise lenses spent effort on the same cites. Acceptable for a rev 0 of a broad design.
- D188 landed mid-round with "Home: span_cards.md rev 1". The rulings freeze caught it only at hand-back; no critic examined J6 under it.
- R-35 itself has a "Not asked" line (method/shape is the kit's, D157); several findings (MEAS gates, SLOT-1 cells) are about method. Proposed dispositions keep them FIX-NOW because they are defects in the stated method, not a choice of method; the launcher may route them to the kit as findings, not directives.

## Proposed changes
1. Skill §4 measurement lens row: append "When the design specifies an ESTIMATOR or a gate over measured data, run the simulate lens's constructed-outcome drills on it (clean / one outlier launch / bimodal / A/A > spread / an equal-effect sweep of any decision rule), implemented from the TEXT." (Motivation: MEAS-2,4,7,8,10 came only from such drills.)
2. Skill §3 step 1 (freeze the rulings): add "Re-diff the rulings at each critic return, not only at hand-back; a ruling whose text names the SUBJECT as its home triggers one fresh critic on the section it lands in." (Motivation: D188, 08:54, homed in span_cards rev 1, unexamined.)
3. COMMON template: name the verifier's re-run budget per drill and require it to READ each critic script for faithfulness before re-running (done here ad hoc in VERIFY_BRIEF; the verifier's faithfulness notes made MEAS-7/8 credible).

## Framework notes
- The coordinator pattern ran a 5-critic design round plus verification in ~21 minutes wall with zero manager turns; the launcher sees one 15-line message. Files-not-replies was decisive: all six Agent returns reported no handback, yet nothing was lost.
- Where else: the same freeze -> fan-out -> verify -> draft shape fits a bench-ledger audit (pcrec-bench outbox claims checked against raw ledgers by blinded critics) and a kit-request acceptance check (R-n delivered vs asked), both currently manager-context work.
