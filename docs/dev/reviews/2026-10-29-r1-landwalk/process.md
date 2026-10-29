# process.md — critic round landwalk (design), coordinator log

- Coordinator start: 2026-10-29T11:21:48-04:00. Subject frozen: docs/dev/lanes/p1dsg_report.md @ 3afd1a439a9aa4aba8ea2df069c7bbfda6004de7 (main HEAD 13056c942).
- Profile: a new mechanism/row in an existing table (premise, slots); a selection rule (admission table: simulate); a measured quantity + card (measurement); a build proposal with stages, flag bit, abi event, ladder rung (cost and overlap; caller-facing stamps/ladder folded into cost as the D94 reader hunt); rulings relied on (folded into slots).
- Lenses: premise (opus, + goals), simulate (opus: soundness of admission = answer severity), slots (opus, + ruling check + sibling-of-family + general form/unlocks), measure (sonnet), cost (sonnet, + contract reader hunt).
- No review worktree (design mode); critics use main's build/pcrec read-only.

## Agents
| agent | model | launched | ended (file) | final state |
|---|---|---|---|---|
| premise | opus | 11:22 | 11:30 | file complete, lanecheck DONE; final reply lost (no handback) |
| simulate | opus | 11:22 | 11:37 | file complete, lanecheck DONE; final reply lost |
| slots | opus | 11:22 | 11:32 | file complete, lanecheck DONE; final reply lost |
| measure | sonnet | 11:22 | 11:26 | file complete, lanecheck DONE; final reply lost |
| cost | sonnet | 11:22 | 11:27 | file complete, lanecheck DONE; final reply lost |

- All five background launches RETURNED IN THE LAUNCH TURN (blocking ~16 min for the slowest), each "ended without delivering a report through SubagentHandback"; the files carried everything (skill §6.1's case). No resend or nudge needed.
- Raised: premise 6, simulate 6, slots 15, measure 8, cost 10 = 45 raw.
- Overlaps noticed at read: landmark choice (SIM-3 = PREMISE-2); baseline of the "9 other movers" (SIM-5 = PREMISE-4 = COST-4 part); negative control unpassable (PREMISE-5 = MEAS-5); stamp slot (SLOT-2 = COST-1); flag count (PREMISE-6b = COST-3, CONFLICTS with slots' held "8"); UNIQUE rule (PREMISE-1 too strict vs SIM-1 forms too loose: compatible); overlap column (SLOT-13 + COST-8); listing/declared conjuncts (SLOT-5/6 + COST-8 last bullet); ladder rung (SLOT-12 vs COST-PROBED held the placement: CONFLICT on order reasoning); card/kit (SLOT-11 + MEAS-1/2).
| verifier | opus | 11:39 | 11:48 | verify.md complete (27 items), lanecheck DONE; final reply lost |

- Verifier DELIVER file: the coordinator FORGOT to write `landwalk-verify_deliver.txt` before launch (skill §5 specifies DELIVER files for critics only; §6.2 says nothing for the verifier). The verifier created its own (`sections: Tally`) and passed lanecheck. No harm; a gap in the skill.
- Draft review.md written 11:50-12:00; time to draft ~40 min from coordinator start (11:20), ~9 min critics' longest wall since the launch turn blocked until all returned.
- Blinding: no leak noticed. The denylist cost the round the twin-side numbers (MEAS could not rebuild the twin; MEAS-3's cycle projection and every x70 claim stay unverified). The verifier was also bound by the denylist.
- Per lens (raised / verified / severity top / overlaps):
  - premise: 6 / 6 HOLD (6a doc) / answer-adjacent design (PREMISE-1), design (PREMISE-3) / S1, S2, S3, C1
  - simulate: 6 / 5 HOLD, SIM-6 structural / answer (SIM-1, SIM-2, stage 2) / A1, S1, S2
  - slots: 15 + sibling + unlocks / 9 HOLD, 3 PARTLY, 1 held-claim REFUTED (8 bits), 3 not verified / answer/hang (SLOT-1, SLOT-4) / D5, C4
  - measure: 8 / MEAS-1, -4, -5 HOLD; MEAS-3 arithmetic only / design / S3, S4
  - cost: 10 / COST-1,-3,-4,-7,-8 HOLD; held rung reason REFUTED / design, speed / S2, D5, C1, C4
- Unique catches: SIM-1/SIM-2 (simulate only), PREMISE-1 (premise only), PREMISE-3 (premise only), SLOT-1/SLOT-4 (slots only), MEAS-1/MEAS-2 (measure only), COST-2/COST-7 (cost only). Every lens had at least one unique finding; no lens was redundant.

## Process observations
- All six background agents returned IN the coordinator's launch turn (blocking until the slowest), each with "ended without delivering a report through SubagentHandback". Files carried 100% of the content; lanecheck markers made completion checkable with one lanewatch call. The file-first design of the skill worked exactly as intended.
- The two opus behaviour lenses (simulate, premise) disagreed on A1 in OPPOSITE directions (rule too loose vs too strict) and were both right; the verifier's job was to reconcile, not to pick. Running an opus verifier was worth it here: items 1, 4 and 14 needed judgment, and item 14 found a consequence neither critic drew.
- One critic's PROBED-AND-HELD was wrong (slots' "8 free bits", from a stale ruling text). PROBED-AND-HELD claims that conflict with another lens's finding should be verifier items too; this round did so by chance.
- The lens table fitted: the contract reader hunt folded into cost and overlap produced the longest reader list (COST-2) without a fifth opus.
- Over-staffing: none. Under-coverage: the twin-side numbers (x70, x1.45) were unverifiable under the denylist; every critic noted it.

## Proposed changes
1. Skill §6.2 (verifier): add "The verifier gets a DELIVER file too (`report=verify.md`, `sections: Tally`), written before launch." Motivation: this round's coordinator omitted it; the verifier improvised one.
2. Skill §6.2: add "Include in the verifier's list every PROBED-AND-HELD claim that contradicts another lens's finding." Motivation: slots' held "8 bits" contradicted PREMISE-6b/COST-3 and was stale.
3. Skill §3.3 / COMMON template (design mode): "The VERIFIER (not the critics) may read the subject lane's evidence DATA and drivers to re-run a disputed number; critics stay denied." Motivation: the verifier is not a finder, so blinding it buys nothing, and this round left the twin-side claims (and MEAS-3's cycle projection) unverified.
4. docs/dev/guide/critics.md "Design rounds": add the lessons in review.md §Lessons, esp. "a new row that hands a new hand is a table walk" and "a price needs the selected path's baseline".

## Framework notes
- The coordinator pattern ran a 5-critic + verifier design round in ~40 minutes of wall time with one coordinator context and zero manager wake-ups before the hand-back; nested replies were all lost and nothing depended on them.
- Agents launched with run_in_background still blocked the coordinator's launch turn here (all returned together). For a coordinator this is harmless (it had nothing else to do); for a manager it would not be. Evidence: six "ended without delivering" results in the launch/verify turns, 2026-10-29.
- Where else it fits: any fan-out whose results must be reconciled before a human-facing ruling (e.g. a census over several bench boxes, a multi-lens spec survey), because the reconciliation step (here: A1's opposite-direction findings) is the expensive judgment and benefits from a fresh, blind context.
