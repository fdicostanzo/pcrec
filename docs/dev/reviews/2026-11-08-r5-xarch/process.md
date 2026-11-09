# process.md — crit-xarch code round (2026-11-08)
- 19:45 freeze: SUBJECT 424ddc742 (lane/u3tgt), BASE 550e23364, main c857164fe; rulings freeze = decisions.md/plan.md at c857164fe
  (decisions last touched a47aa97ce, D146 add. 1 at decisions.md D146 block line ~9007; R1-R4 in docs/dev/reviews/2026-11-07-xarch1-rulings.md;
  target_seam_units.md §6 at da051bb78, same on SUBJECT).
- Round dir crit-xarch/ held an EARLIER round's files (2026-11-07 r1 xarch, design); this round lives in crit-xarch/code/, the rest denied.
- Interface sheet lives inside docs/dev/lanes/u2_report.md (a DENIED file): coordinator extracted ONLY its "U3 interface sheet" section
  (lines 38-101, by heading) to code/u3_interface_sheet.md; read no other section. FREEZE NOTE.
- docs/dev/lanes/u3tgt_movers.py (the movers proof) is under the lane-report denylist; not reviewed.
- Builds: review tree 19:46 (rc 0, ~1 min); BASE export built 19:48... (first attempts blocked by the no-cd hook; rc 0).
- 19:50 launched 5 critics in one message (emit opus, contract opus, checks sonnet, seam opus, house sonnet), background, unnamed.
  ALL FIVE returned in the launch turn (durations: emit 12.8m, contract 8.6m, checks 12.3m, seam 9.2m, house 2.2m); each reply
  was "ended without SubagentHandback" (final text lost, as the skill predicts) but every FILE was complete; lanewatch DONE rc=0 at 20:03.
  No resends, no nudges, no stalls. Findings: emit 5, contract 7, checks 7 (one, checks-7, filed under Findings as the trade audit;
  checks-1..6 sit under the PROBED-AND-HELD heading by a heading slip), seam 6 + standing, house 9.
- 20:03 freeze drift: main still c857164fe, decisions/plan/design unchanged. SUBJECT unchanged.
- 20:04 verifier (sonnet) launched over 17 finding groups; returned in-turn at ~20:09 (5.0 min), verify.md complete, VERIFY COMPLETE,
  17 HOLDS / 0 REFUTED / 0 PARTLY; no REFUTED to re-run. It also tried EMIT-3's fix by hand (works; artifacts still compile at -mno-sse2).
- 20:10 review.md drafted; critic texts + verify.md + COMMON + extracted sheet copied to review/. 20:11 worktree removed (wtprune --force --quiet-min 1).
- Time to draft: ~25 min from freeze; ~20 min from critic launch.

## Per lens
| lens | model | raised | verified | top severity | overlaps |
|---|---|---|---|---|---|
| emit | opus | 5 | 4 checked, all hold | build break (gcc consumer TU) x2 | EMIT-1 with CONTRACT-1/SEAM-4 |
| contract | opus | 7 | 5 checked, all hold | doc | CONTRACT-1 x3 lenses |
| checks | sonnet | 7 (6 confirmed, 1 suspected) | 4 checked, all hold | silent sabotage row (mech red pending) | stale switch comments with seam/house |
| seam | opus | 6 + standing | 4 checked, all hold | design (address identity, dead slots) | SEAM-2 = HOUSE-2/3 |
| house | sonnet | 9 | 2 checked, hold | maintenance | HOUSE-5 folds into EMIT-5 |

## Process observations
- Every agent (5 critics + verifier) returned INSIDE the launch turn, each with "ended without SubagentHandback" (final text lost) and a complete
  FILE: the files-not-replies rule carried the whole round; lanewatch was a one-shot DONE.
- The narrow two-sub-part briefs (2026-11-07 lesson) worked: no stalls, house finished in 2 min, the widest (emit) in 13 min with 330 compiles.
- The interface sheet, the contract between the two units, lives inside a denied lane report. The coordinator had to extract it by heading,
  which is a blinding risk (a sheet can carry results: its rev 1.1 notes name a deviation). The sheet belongs in memfn/docs/ or the responses ledger.
- A heading slip: checks put six findings under its PROBED-AND-HELD heading; lanecheck's nonempty test passed. Harmless here, but a reader
  that splits by heading would have dropped them.
- The round dir name was reused from the 11-07 design round (crit-xarch/ held its files): a second round on one topic needs its own dir.
- The no-cd hook blocked two compound `cd X && ...` commands at freeze (one silently swallowed an archive step: the BASE build ran in a
  missing dir and "completed"); subshells only.
- Lens table: emit's consumer-TU sub-part (added from the 11-07 lesson) found both build breaks; no lens was idle.

## Proposed changes
1. Skill §5 / COMMON template, emit lens: "compile the artifact INSIDE a consumer TU that, after the include, uses the same facility the
   artifact's text configures (intrinsics, fortified libc calls, a second artifact of another target), under each supported compiler"
   (motivating: X-1, X-2 compile alone under every flag set and break only in a consumer TU, gcc only).
2. Skill §3 freeze: "a round on a topic that already has a round dir uses `crit-<topic>-<mode>N/`; never mix two rounds' files" (this round).
3. Skill §5 COMMON output format: "every finding goes under `## Findings`; PROBED-AND-HELD holds only held probes", and the deliver's
   `nonempty:` cannot catch a mis-filed finding, so the coordinator greps for finding ids under PROBED-AND-HELD (checks-1..6 this round).
4. Kit/manager practice (for docs/dev/guide/critics.md): an interface sheet between units lives in a non-denied file (memfn/docs/ or the
   responses ledger), not inside a lane report, so a round can read it without the coordinator cutting a denied file.
5. Skill §6.2: when every critic returns in the launch turn, launch the verifier in that same turn (done here; already in the launch note).

## Framework notes
- The coordinator pattern ran a 5-critic code round plus verification in ~25 minutes of wall time with zero manager wake-ups, all delivery
  by file. The one point where blindness needed a judgment call (the sheet inside a denied report) is a launcher-side input problem, not a
  coordinator one: the pattern fits any review whose contract documents are in the open.
