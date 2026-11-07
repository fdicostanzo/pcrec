# process — crit-memfn-span-cards-r1 (design re-check)
Coordinator start 2026-11-06 09:31 EST.
Freeze: SUBJECT doc docs/design/memfn/span_cards.md @ b06c7447f2b1150e3aed423987ce83fcd22ac873 (branch lane/memfn-s2rev1 tip).
Build tree: main 9f5f082de (main at launch was 592ed6da3; 9f5f082de adds only known_issues K139). No code drift fb22c62a6 (rev 0 cite base) -> 9f5f082de in src cli lib memfn scripts tests docs/spec.
Rulings frozen at main 592ed6da3 (last decisions.md/plan.md commit).
Freeze note: main's DEFAULTS ruling (B) — no record found in main's tree (requests.md R-35 / responses.md / decisions / plan / owner / wake) at 592ed6da3 or 9f5f082de; only the kit's ASK at responses.md:3202 on the subject branch. The launcher states it is in force.
Client docs: span_pick.md, measure_sets.md, docs/spec/measures.md identical at subject and main (diff empty).
## Critics (all opus, background, unnamed, launched 09:33 in one message)
| lens | agent | end | state | findings |
|---|---|---|---|---|
| fixind (fix-induced) | add4cf5f1cefdc776 | ~09:43 | file complete, lanecheck DONE | 12 (fixind-1..12) |
| ready (readiness) | aa12e90ac17c0b53a | ~09:41 | file complete, DONE | 11 (READY-1..11), verdict "ready with listed text fixes" |
| meas (measurement, estimator drill) | a75b57209df9cf7b0 | ~09:44 | file complete, DONE | 8 (meas-1..8) |
| ruling (ruling check + slot + standing Qs + goals) | a98c7288075e66b17 | ~09:40 | file complete, DONE | 10 (ruling-1..10) |
All four returned inside the launch turn (Agent result: "ended without delivering a report through SubagentHandback"); files were the delivery channel, as designed. No nudges.
Rulings re-diff at return (accepted r4 process change 1): main 592ed6da3..HEAD touched plan.md once (ad4ead990, [ISL-PRICE] note after K139) — unrelated to the subject. No FREEZE DRIFT on rulings in scope.
Overlaps: fixind-1=READY-3; fixind-2=READY-4; fixind-3=READY-10=meas-5(a,c)=ruling-7(i,ii); fixind-8=READY-7; fixind-9=ruling-9(b); fixind-10=ruling-1; READY-2=meas-1; READY-9=ruling-8; fixind-4~meas-5(e)~ruling-7(iv).
## Verifier
sonnet, a7626be83a59d884e, launched ~09:45, ended ~09:54, verify.md complete (VERIFY COMPLETE), lanecheck DONE. 17 items: 12 HOLDS, 5 PARTLY, 0 REFUTED (so no REFUTED re-run needed). One critic claim NOT REPRODUCED: meas-1's "loop phase unchanged in 6/12 links" (verifier 24/24 moved; critic's driver-size schedule not saved as a script).
## Per lens
| lens | raised | verified HOLDS/PARTLY | top severity | overlaps |
|---|---|---|---|---|
| fixind | 12 | 9 checked: 8 H, 1 P | design (Goal 3 cells, check C) | ready x4, ruling x2, meas x1 |
| ready | 11 | 7 checked: 6 H, 1 P | design (no census tool; S2c checks) | fixind x4, meas x1, ruling x1 |
| meas | 8 | 8: mechanisms H, magnitudes SUSPECTED | design (placement as bias) | fixind/ready on cells+twin |
| ruling | 10 (+ subparts) | 5 checked: 2 H, 3 P (interpretive halves) | design (D176 Q3 split; D188a1 consequences) | fixind (D188a1, embed), ready (smp20) |
Time: launch 09:33 -> critics done 09:44 -> verify 09:54 -> draft ~10:00 (~30 min).
Blinding: no leaks noticed. Denied review file was given as an extract (findings table + Rulings only), which worked: critics classified FI/RES/PEM against r4 ids without the critic texts.
## Process observations
- All five agents "ended without SubagentHandback" yet every file was complete and lanecheck-sealed: files-as-channel held again; lanewatch one-shot was the right poll.
- Four strong lenses converged heavily (CELLS found by 4 lenses, CHECKC/HASH/TWIN by 2 each). For a re-check, fix-induced and readiness overlap most; a 3-critic round (readiness+fix-induced merged, meas, ruling) would likely have found the same set. Over-staffing was mild.
- The DEFAULTS (B) ruling the launcher named "in force on main" had no record on main; the freeze step found it only because the rulings freeze greps for it. Worth a skill line.
- The measurement lens's "implement from TEXT before reading the drill" again paid off: the drills reproduced, so findings were about what the drills OMIT (aa term, placement), not arithmetic.
## Proposed changes
1. Skill §3 step 1 (freeze rulings): "For each ruling the launcher or the subject calls in force, locate its RECORD (file:line at the freeze commit); a ruling with no record is a freeze note in the draft." (this round: DEFAULTS (B) existed only as the kit's ASK on the subject branch).
2. Lens table, fix-induced: "for every pair of fixes that touch one check or one directory, recompute the check's population at the build tree" (CHECKC: SLOT-4 x CONTRACT-1 -> population zero).
3. critics.md lesson: "an 'objects differ' assertion over differently named sources is vacuous (STT_FILE); assert on linked addresses or .text" (TWIN).
4. Lens table, re-check: allow merging readiness and fix-induced into one opus critic when the revision is under ~1,000 lines and r(n-1) had <50 findings; overlap here was 4 consolidated ids of 11-12 each.
## Framework notes
- Coordinator pattern, second re-check of one subject: the extract-the-claimed-fixes approach (deny the review, hand an extract) let critics label findings FIX-INDUCED / RESIDUAL / PRE-EXISTING-MISSED, which made the draft's verdict split (S2a/S2b ready, S2c-e not) mechanical. Recommend the class column as standard for any re-check.
- Whole round ~30 min wall; the coordinator's context stayed small because critic texts arrived as files and the verifier did all re-runs.
