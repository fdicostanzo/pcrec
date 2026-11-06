# process.md — crit-vlb2 (design re-check, LAST before stage-1 build go)

Coordinator start: 2026-11-05 19:40 EST.
Freeze: subject docs/design/vlookbehind.md at bc9d1eb8f5ec013972d76ee8b0d26e84a045e393 (byte-equal at main 7ddfbfa95);
build tree = main HEAD 7ddfbfa95833b60f193c563cfdb820c5532b61af; rulings (decisions.md/plan.md) frozen at 7ddfbfa95.
No src/lib/cli/docs/spec/tests drift between bc9d1eb8f and 7ddfbfa95 (git diff --stat empty).
Review tree: worktrees/crit-vlb2, nice -n 19 make -j2, unlocked; BUILD rc=0 at ~19:43.
Observation at freeze: the main tree was mid-merge of lane/arevdesign (MERGE_HEAD, UU docs/design/CLAUDE.md,
adds docs/design/stream/arev.md = A-REV). That design is A-REV, which the subject cites; check FREEZE DRIFT at hand-back.
Spellings checked by one compile each: `-e utf8` ok; `--emit-ir` ok; binary prints `match S E`.

## Agents
| agent | model | launched | ended | final state |
|---|---|---|---|---|
| crit-fixind (FIX) | opus | 19:47 | ~19:57 | file complete, lanecheck DONE; returned in launch turn (no handback text) |
| crit-ready (READY) | opus | 19:47 | ~20:02 | file complete, lanecheck DONE; returned in launch turn |
| crit-sound (SOUND) | opus | 19:47 | ~20:03 | file complete, lanecheck DONE; returned in launch turn |
| crit-simlit (SIMLIT) | sonnet | 19:47 | ~19:56 | file complete, lanecheck DONE; returned in launch turn |
All four "ended without delivering a report through SubagentHandback" — files carried everything (skill §1 holds).
No resend/nudge needed. lanewatch DONE rc=0 at 20:01.

## Per lens (raised)
- fixind: 8 (FIX-1 answer; FIX-2..7 maintenance/doc; FIX-8 SUSPECTED design simplification) + standing questions.
- ready: 11 (READY-1 answer; READY-2 design/manager choice; rest doc/maintenance) + per-unit table + verdict.
- sound: 4 (SOUND-1 answer; SOUND-2 doc/design; SOUND-3 doc; SOUND-4 latent).
- simlit: 3 (0 diffs over 76.7M cases; SIMLIT-2 doc; SIMLIT-3 hold). Did NOT model trail capacity -> missed the trail defect
  that 3 reading lenses found independently (same shape as r3 lesson 1: a model that omits a resource bound validates
  semantics only).
## Overlaps
- TRAIL under-charge: SOUND-1 = FIX-1 = READY-1 (three independent, all opus readers).
- Slot family readers: FIX-3 = READY-4 (+ FIX-8 alternative).
- limits.def schema: FIX-4 = READY-8.
- sabotage rows moving: FIX-2 (S133/S134 under A) + READY-5 (S-U4, S136 branch; S133-S135 under B).
- negative end-check / INTERNAL: SOUND-2 (rewrite claim) + FIX-7 (second producer) + FIX-6 (role text).
- wiring unstated: SIMLIT-2 (negative/atomic composition) — the soundness and fixind lenses reconstructed the same from vm_look.
| crit-verify | sonnet | 20:02 | ~20:08 | verify.md complete, VERIFY COMPLETE, lanecheck DONE; returned in launch turn |

## Verification
19 items: HOLDS 15, PARTLY 3 (READY-3 count 22 not 24; READY-5 S-U4 likely still red on cap cells; READY-10 items 2-3), REFUTED 0.
No REFUTED rests on a crafted input, so no coordinator re-run was owed (skill §6.2).
Draft written 20:10; review worktree removed 20:10 (wtprune --force --quiet-min 1). Time to draft: ~30 min from launch.
review/ready.md: two line-numbered plan.md cites rewritten to row tags (PL14) in the COPY only.
Freeze drift: none in decisions.md/plan.md/subject/src/spec between 7ddfbfa95 and main 82d95943c. Mid-round landings:
arev.md (A-REV rev 0, reads vlookbehind §5.1 / G6) and a critic-skill line (relayed findings).

## Process observations
- Fastest round shape yet: all five agents returned inside their launch turn; files + lanecheck carried everything;
  no resends or nudges. Concurrency with crit-altnf2 and a held box lock caused no stall (nice'd, unlocked build, ~2 min).
- The coordinator's own pre-read suspicions (negative-arm wiring unstated; VK_WORK operand) were both reached by critics
  (SIMLIT-2; FIX-5/held); the trail defect was NOT among the coordinator's suspicions — three critics found it.
- The literal interpreter (76.7M cases) missed the round's only answer-level defect because it modelled frames and trail
  without capacity. r3's lesson ("model the sketch, not the intent") was applied and still left a gap one level down:
  the resource the sketch consumes is sized by ANOTHER pass.
- The main tree was mid-merge at the freeze. COMMON's "review tree + git show <freeze>" kept all critics off it.

## Proposed changes
1. Skill §4 fix-induced row, append: "When a fix adds a slot write, a frame or a trail entry, trace it to the pass that
   SIZES that storage (vm_cost_*, vm_plan_capacities), not only to its readers (2026-11-05 vlb2)."
2. Skill §4 simulate row, append: "A literal interpreter reports the peak frame and trail depth per evaluation and
   compares it with the cost pass's charge (vlb2: 76.7M cases, 0 diffs, missed a FRAMES give-up)."
3. Skill §5 COMMON: make "read code ONLY in the review tree, docs ONLY via git show <freeze>: (the live main tree may
   be mid-merge)" a standard COMMON sentence, not only for ruling files.
4. Skill §9.1's PL14 grep: run it in the coordinator's draft step (§6.3) too, so copies arrive clean.

## Framework notes
- A re-check round with a launcher-named lens set (fix-induced, readiness, soundness) plus one mechanised lens chosen by
  the coordinator was right-sized: 4 critics + 1 verifier, ~30 min wall, one answer-level finding triple-confirmed.
- Independent triple discovery is a useful confidence signal and costs little at opus; the mechanised lens's value here
  was the 0-diff semantics floor (which lets the draft say "text fixes only") rather than discovery.
