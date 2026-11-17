# process.md — round predspec22 (r30), coordinator (opus)
- 18:00 coordinator start. Freeze: subject 8defc5d66 (rev 22); rev 21 d01d10ae3; rev 20 d1434199b; main HEAD 7e22f7efe;
  decisions/plan/COND-FAMILY last change 03a2ce715 (COND-FAMILY copy taken at 8defc5d66; identical file content to be
  re-diffed at each return). predicates_future.md differs subject->HEAD (+28 lines, the merge's item 12; in the copy? copy taken at 8defc5d66).
- Rulings record in force: COND-FAMILY.md entries 16:13, 16:20, 16:23 (manager derivation), 16:31, 16:44, 17:29 (+ correction), 17:42.
  No FREEZE NOTE: every ruling relied on has its record there.
- Evidence: predspec22_check.py re-run in the round dir copy: 4 s, PARTS A-F byte-identical; PART G needs git (rev 21 line empty in copy).
- Lenses: changetab (sonnet), simulate (opus), fixind (opus, + two standing questions), ruling (opus, 4th lens: the record
  hands the 17:29 readings (1)-(4), the 17:42 consequence, the 16:23 derivation, the 16:31 readings and rev 22's own
  one-witness "manager's reading" to the round; r29's ruling lens produced 9 findings; the r29 lesson on withdrawn readings
  applies to the 17:29 correction).
- 18:03 launched 4 critics in one message (background, unnamed): changetab sonnet, simulate/fixind/ruling opus. All four
  returned IN THE LAUNCH TURN (6.2 / 16.7 / 9.5 / 11.1 min), files complete with CRITIC COMPLETE, lanecheck .done x4.
  Each Agent result said "ended without delivering a report through SubagentHandback": final replies lost, FILES carried
  everything (skill §1 holds). No resend/nudge needed.
- Findings: changetab 7 (all doc/maint), simulate 9 (3 answer), fixind 9 (3 answer), ruling 10 (4 answer). No freeze drift
  at 18:20 (main = 7e22f7efe).
- Inline verification (coordinator): RULING-1 (no 17:46 entry: 0 hits in frozen copy and HEAD), RULING-3 (no 17:02 entry:
  0 hits), CHANGETAB-6 (item 12 absent at 8defc5d66, present at HEAD via b4a62a75f/62fbef5ab): HOLD.
- Overlaps seen: `when` body (SIM-1, RUL-6, FIX-1); adding-a-condition scope (SIM-6, FIX-2); transparency unit
  (SIM-9, RUL-2, RUL-5, RUL-7, SIM-7 note): three lenses from three sides again; complemented-pattern scope (SIM-4,
  RUL-10, SIM-5); error hints (FIX-3, -5, -6, -7, RUL-9b).
- 18:21 verifier (opus) launched; returned in the launch turn (7.8 min), verify.md complete (VERIFY COMPLETE), V1-V12:
  no item REFUTED in full; PARTLY: RULING-6's body, V6's per-pass-only, FIXIND-6, FIXIND-7, FIXIND-8 (conflicts with
  his explanation, not the ruled statement), RULING-8 (polarity objection refuted in context). The verifier added its
  own candidate rule (absent marked label ranges over the regex's values) with 0 splits on 3 witnesses: labelled
  as the verifier's in the draft. No REFUTED resting on a crafted input, so no coordinator re-run needed.
- 18:30 draft written (review.md); no review worktree (design only); freeze drift none. Time to draft: 30 min.

## Process observations
- All five nested agents' final replies were lost ("ended without delivering a report through SubagentHandback");
  pre-created findings files + CRITIC COMPLETE + lanecheck .done made it a non-event (skill §1/§5 vindicated again).
- The fourth lens (ruling) was the most productive on answer-level identity breaks (RULING-2/-4/-7) and the only one
  to catch unrecorded quotes; r29's recommendation of three lenses for the re-check would have missed group I and L.
- Three lenses reached the transparency unit from three sides (as r28 MARK-DOMAIN, r29 group A): the domain rule is
  where every round lands; a dedicated "DOM computation" drill may be cheaper than three lenses converging.
- The runnable `tree/` copy (scripts' relative paths resolved under the round dir) let every critic run the lane's
  engine in seconds with no repo access.
## Proposed changes
- skill §4 simulate row: lessons 1-3 of review.md (trap-order swap; three insertion points for nested programs;
  recompute with the document's set-membership, not the script's lambda).
- skill §4 ruling row: lesson 4 (grep every cited CF time).
- skill §5 design mode: "when the lane scripts read the draft or each other by RELATIVE path, build a read-only
  runnable copy (`R/tree/` mirroring docs/dev/lanes + docs/design) and name it in COMMON" (r30: 4 s re-run, 0 setup per critic).
- On a re-check, the coordinator may add the ruling lens whenever the record hands manager's readings to the round,
  regardless of the previous round's recommended set (r30: 4 of 10 answer/design findings).
## Framework notes
- A 4-critic + verifier round on a 6,000-line design closed in 30 minutes wall, coordinator-drafted, with every agent
  returning inside its launch turn; the coordinator pattern scales to giant subjects when critics get frozen copies
  and a runnable evidence tree, and briefs are ONE question with two sub-parts.
