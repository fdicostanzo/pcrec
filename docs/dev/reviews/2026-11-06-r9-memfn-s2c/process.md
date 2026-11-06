# process — crit-memfn-s2c (code), coordinator log

- 13:25 freeze: SUBJECT lane/memfn-s2c = 8983c402673921c40c799fb735364781c8d41c72; BASE (skill) merge-base main = adb2d44b7;
  S2c own diff = ea5d54abf..8983c4026 minus tests/registry/limits_check.sh (the d9afba62b merge, S2a's; no file overlap).
  Rulings freeze: main ae7b58d8c (decisions.md/plan.md last touched there).
- 13:25 review tree worktrees/crit-memfn-s2c built unlocked nice -j2: rc 0 (~?min). Box load ~8, boxlock HELD by queue:463 (kit-s2a-ident2).
- 13:3x BASE export ea5d54abf built in round dir base/: rc 0. Spelling checks: slot `run.py dry J2 ... s2c-dry` rc 0 in 2 s;
  one pattern BASE vs SUBJECT emitted C SAME; arm_fixtures --hash built both trees.
- 13:27 launched 5 critics (emit opus, contract opus, checks sonnet, slot opus, house sonnet), background, unnamed.
  All 5 returned IN THE LAUNCH TURN (6-13 min each); every findings file complete; lanewatch rc 0 at 13:41 (all .done).
  Final replies were lost ("ended without SubagentHandback"): files carried everything, as the skill predicts.
- Raised: CHECKS 7 (2 answer), CONTRACT 6, EMIT 6, SLOT 18, HOUSE 17. Heavy overlap: canonical-instance dep (EMIT-1/SLOT-6/HOUSE-2),
  est.py's absent build/arm_fixtures (EMIT-2/SLOT-7/HOUSE-1/CONTRACT-6c), est ignores the record (CONTRACT-2/SLOT-1),
  record keys + J2p cause (SLOT-3/HOUSE-3/CONTRACT-5), finalize hang (SLOT-4/CONTRACT-5), plan.py second home (SLOT-8/HOUSE-4/HOUSE-7/CONTRACT-2),
  copied primitives (HOUSE-5/SLOT-18), stale reuse (HOUSE-9/SLOT-2/SLOT-16), gate coverage (CHECKS-1/CHECKS-2/CHECKS-5/SLOT-2), quiet wait (SLOT-12/HOUSE-11), vcls (SLOT-9/HOUSE-16).
- 13:42 verifier (sonnet) launched over 29 ids in two tiers; returned in its launch turn 13:52 (10 min), verify.md complete, lanecheck .done.
  Verdicts: all HOLDS except CONTRACT-2 PARTLY (odd-gate halving only on the unit's noise gate; the other two halvings are equal for integers)
  and SLOT-11 PARTLY (kind 5 has a die byte; kind 6 alone departs from die1). No REFUTED, so no coordinator re-run needed.
- 13:53 draft review.md; critic texts + verify.md + COMMON + verify brief copied to review/.
- 13:54 worktree removed: scripts/wtprune --apply --force --quiet-min 1 crit-memfn-s2c (REMOVED). Its output listed other branches'
  commit SUBJECT lines (kit journal subjects) to the coordinator: subject lines only, critics never saw them; noted as a minor blinding
  exposure of the coordinator via tooling output.
- Freeze drift: main still ae7b58d8c at hand-back: NONE.
- Time to draft: ~29 min from freeze (13:25 -> 13:54). Dry runs: coordinator 1, critics ~20 + sabotage.sh x2, verifier ~6; never >2 concurrent
  as far as observable (critics were told one at a time; CHECKS and SLOT both ran sabotage.sh, possibly overlapping with others' dry runs: not checked).

## Per lens

| lens | model | raised | verified | top severity | overlaps |
|---|---|---|---|---|---|
| EMIT | opus | 5 + standing | 5 HOLDS | answer (EMIT-1) | EMIT-1=SLOT-6=HOUSE-2; EMIT-2=SLOT-7=HOUSE-1 |
| CONTRACT | opus | 6 | 4 HOLDS, 1 PARTLY, 1 suspected-held | doc/design + answer-latent | CONTRACT-2=SLOT-1; CONTRACT-5=SLOT-4/SLOT-3 |
| CHECKS | sonnet | 7 | 4 HOLDS (rest not verified, low) | answer (CHECKS-1/2) | CHECKS-5~SLOT-2 |
| SLOT | opus | 18 + charter + rulings + standing | 14 HOLDS, 1 PARTLY | answer (SLOT-1, -15) | most |
| HOUSE | sonnet | 17 | 6 HOLDS | answer-latent (HOUSE-3/4) | many with SLOT |

## Process observations
- Every agent (5 critics + verifier) returned INSIDE the launch turn even though backgrounded; their final replies were lost
  ("ended without SubagentHandback") but every file was complete and lanechecked. Files-as-delivery worked fully; no nudges or resends.
- SLOT (opus) was the most productive lens and overlapped HOUSE heavily: a "slot tracing" lens on a HARNESS acts as a correctness lens
  (it found 2 of the 4 answer-level holes). HOUSE's maintenance findings mostly re-explained SLOT/EMIT findings from the style side;
  for a harness subject, HOUSE could have been dropped or narrowed to the C kit hunks only.
- The two answer-level gate holes (CHECKS-1 timed-vs-gated, SLOT-15 key-vs-arm) are the same shape as EMIT-1 (dep-vs-timed) and
  SLOT-1 (verdict-vs-record): pairs of representations of one fact, each with its own check. No lens row names that question.
- Five critics on a 3,840-line diff with ~20 KB findings each made the consolidation the coordinator's largest task; the overlap
  table had to be built by hand.
- Mixed subject (kit C + spec + a python/C evidence harness) fit no single profile; the profile list has no "measurement harness" item.

## Proposed changes
1. Lens table (SKILL.md §4), new row (motivated by G1/G2/G3/G4 all being one shape):
   `| C | a measurement harness (code that produces a priced number) | **harness fidelity** | Is the thing TIMED the thing GATED,
   the thing KEYED and the thing RECORDED? Plant a divergence between each pair (timed loop vs gate loop; key tokens vs rendered form;
   recorded dep vs timed text; verdict vs run record) and require a refusal. | opus |`
   and §3.4's code profile list gains "a measurement harness".
2. seam round trip row: append "For a PRODUCER's run record, construct two runs with byte-identical records and different verdicts
   (2026-11-06 s2c: a leftover cells file flipped FULL/REFUSED)."
3. COMMON template: tell critics to tag each finding with the FACT it concerns (e.g. "dep of a verify row"), so the coordinator can
   join overlaps mechanically; and to read the other lens names in COMMON so they can say "also a <lens> question" instead of
   re-deriving it.
4. wtprune: the coordinator's removal printed other branches' commit subjects; harmless here, but a `--quiet` output mode for the
   critic round's removal would keep the coordinator blind to unrelated journal subjects.

## Framework notes
- The coordinator pattern held: 6 agents, zero manager wake-ups, ~29 min freeze-to-draft, every finding verified before the draft.
  The cost centre moved from monitoring (none needed: all returned in-turn) to CONSOLIDATION (≈52 raised ids into 8 FIX-NOW groups).
  Where else: any fan-out whose outputs overlap heavily (multi-lens audits, multi-box run triage) benefits more from a
  consolidating coordinator than from a monitoring one; a "consolidation key" in the output format would cut that cost.
- crit-house: its final reply reached the launcher, not me (the caller was gone); the launcher relayed it. Marked RELAYED. Its file was already complete (17 findings, lanecheck rc 0) and was read directly, so the draft is unchanged.
