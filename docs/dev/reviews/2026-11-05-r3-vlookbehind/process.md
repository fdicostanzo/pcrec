# process.md — crit-vlookbehind (design), coordinator opus
- 18:53 freeze: subject docs/design/vlookbehind.md @ 9f3aaaee1abff0cc761f170da2e08db7fc8ffcd3; build tree main HEAD 9f077685a095be9923fe825e4bd09760effc989f (no src/ drift between them: diff = lane report, plan.md, history index only). Rulings freeze decisions.md/plan.md @ 9f077685a.
- review tree worktrees/crit-vlookbehind, nice make -j2 unlocked (box lock held by queue:433-mechfix2-mechfull).
- population: vlbinv_evidence + vlbdesign_evidence copied read-only; oracle_probe built from vlbinv's source into tools/.
- coordinator note: system clock 18:53 while owner addendum stamped 19:30 same day (stamps are owner/lane wall-time; not a finding).
- ~18:58 launched 4 critics in one message (background, unnamed): premise (opus), ruling+contract (opus), soundness (opus), simulate (sonnet). All four returned IN the launch turn (durations 350-920 s); all four .done markers present, files complete; no resend, no nudge. Each reported "ended without SubagentHandback" (final replies lost, as the skill predicts; files carried everything).
- per lens: premise 9 findings (PREMISE-1 65535 ceiling answer/accept-set; -3 sketch cursor answer bug; -4 cwmin(A_BREF) stage 2; rest doc/design) + owner Q1 answer; ruling 5 (RULING-1 dup-name/branch-reset accept-set; -2 cwmin; -3 forward refs need deferral + false cwmax comment; -4 spec hunks + refusal shape/sentence + readers; -5 D58/VMREC consequences) + owner Q2 table (29+ shapes); soundness 5 (SOUND-1 sketch cursor answer bug; -2 fold not a constant fold; -3 W6 cannot fail; -4 S136 re-aim green under cwmax sabotage; -5 WD6 cell 1); simulate 2 (SIM-1 UTF startpos clip = D142 class; SIM-2 greedy-tail witness) + ~570M-case held simulation.
- overlaps: PREMISE-3 = SOUND-1 (+ SOUND-2 on the fold); PREMISE-4 = RULING-2; PREMISE-2 = SIM-1.
- note: the simulate harness implemented the INTENT (each branch from the cursor) not the sketch's frame position, so its 0-diff simulation did not catch SOUND-1; the two strong reading lenses did.
- 19:11 verifier (sonnet) launched over 11 CONFIRMED findings; returned in the launch turn (~4 min), crit-verify.done present; 11/11 HOLDS, 0 REFUTED (nothing to re-run). Final reply lost again (no SubagentHandback); file carried it.
- 19:15 freeze drift check: decisions.md/plan.md/design unchanged 9f077685a..4ef43f338. None.
- 19:16 draft review.md written (16 consolidated findings F1-F16 from 21 ids); critic texts + verify + COMMON in review/.
- 19:17 review worktree removed (wtprune --apply --force --quiet-min 1). Time freeze->draft ~25 min.
- Blinding leaks noticed: none. Brief confusions: none reported. Critics stayed within budgets (premise ~130 compiles + timed PCRE2 scans up to 22.6 s; simulate ~570M in-process comparisons, CPU-heavy but single-process; neither touched the box lock).

## Process observations
- All five agents returned inside the launch turn even though backgrounded; lanecheck .done markers + files made the lost final replies irrelevant. Monitoring cost: zero nudges.
- The simulate lens (sonnet) modelled the rule's INTENT and so could not see the sketch's frame bug; two strong reading lenses caught it independently. Simulation and literal hand-execution are complementary, not substitutes.
- The owner-scope questions fitted cleanly into premise (cap) and ruling (backrefs); folding them in kept the round at 4 critics.
- Simulate ran a CPU-heavy multi-hundred-million-case harness on a box whose lock was held by a mech job; COMMON capped compiles (~300) but not in-process oracle work. Not harmful tonight (mech is not timing), but a timing window would have been.

## Proposed changes
1. Skill §4 soundness row, append: "When the design ships pseudo-code over the machine's real primitives (frames, saved positions, slots), hand-execute the PSEUDO-CODE literally on multi-branch witnesses, recording what each push saves and each pop restores (2026-11-05 vlookbehind: a 570M-case simulation of the rule's intent was 0-diff while the sketch's frame saved the candidate, not the cursor)."
2. Skill §4 soundness row, append: "A byte-identity-by-fold claim is checked statement by statement against today's emitted prologue: order, saved operands, charge amounts, slot allocation (vlookbehind SOUND-2: four differences besides the folded test)."
3. COMMON template: bound in-process oracle work too ("no harness over ~10 CPU-minutes without telling the coordinator; never during a timing window"), not only compile counts.

## Framework notes
- Coordinator pattern held well at this size: 4 critics + 1 verifier, ~25 min freeze-to-draft, zero manager wake-ups until hand-back. Owner-scope questions travelled through the coordinator into lens prompts without the manager knowing results — the blindness property did its job.
- Nested agents returning within the launch turn makes "monitor" mostly "read files"; the file+marker contract is the load-bearing part, the polling loop rarely fires.
