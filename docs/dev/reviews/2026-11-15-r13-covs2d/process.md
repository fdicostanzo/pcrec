launch 2026-11-15 20:02:30 coordinator start; freeze: subject 1408c1477 (lane/covs2d head 348d1bca0), build tree main b9b9e8635, merge-base 61f8e9f88; rulings frozen at b9b9e8635 (decisions/plan)
build: review tree worktrees/crit-covs2d at b9b9e8635, nice make -j2, 20:01-20:03, rc 0 (unlocked).
kit: env/facts/emit/ans + oracle (copied from crit-covs1f kit, repointed), sanity-run 5 calls OK.
lenses: premise(opus), readyseam(opus, unit 1 counted seam), readylimit(opus, unit 2 width limit), measure(sonnet, default rule + timing plan), rulings(opus, rulings+owner criteria+standing questions, folds kit-request D157 check and cost/overlap).
critics launched ~20:05 in one message (5, background, unnamed); ALL returned in the launch turn (durations 2.2-7.1 min), each with a complete file + lanecheck .done. No resends, no nudges. Final replies were not delivered ("ended without SubagentHandback") — files carried everything, as the skill predicts.
 premise opus 6.0 min, 7 findings (PREMISE-1..7)
 readyseam opus 7.1 min, 11 findings + verdict "ready with listed text fixes"
 readylimit opus 6.2 min, 8 findings + verdict "ready with listed text fixes"
 measure sonnet 2.2 min, 8 findings (thin on drills: no explicit per-construction table; MEASURE-1/2/3 cover it)
 rulings opus 6.4 min, 8 findings; 0 compiles
overlaps: PREMISE-1 = READYSEAM-1 (proof range); PREMISE-7 ~ READYSEAM-3 (reach/after-context); READYSEAM-4 = READYLIMIT-3 (rename readers); READYSEAM-7 = READYLIMIT-2 (plant d); READYSEAM-11 = READYLIMIT-7(3) = MEASURE-8 Q3 (witness at default); READYSEAM-10 ⊂ RULINGS-3 (stale C15 retire text); MEASURE-1 + RULINGS-4 (rule cannot reach 24; scenario-dependent 31 vs empty) -> one verify item; RULINGS-5 ~ MEASURE-7 (default capped at 40).
verifier sonnet launched ~20:13, 3.3 min, verify.md complete (VERIFY COMPLETE), 21 HOLDS / 1 PARTLY (RULINGS-1: the dial's kit row is clskit, not memfn) / 1 REFUTED (MEASURE-4: shell quoting dropped \b; coordinator re-ran: def scan=cover, eng unanchored).
freeze drift at hand-back: main b9b9e8635 -> 0b7fd2368 (COND-FAMILY.md only); rulings files unchanged. None.
draft: review.md at 20:19; about 20 min from launch to draft. PL14 grep clean.

## Process observations
- All five critics and the verifier returned within the launch turn (2-7 min each), each with a complete file; no final replies reached me (expected). The narrow one-question briefs plus a tested kit kept every critic under 8 minutes.
- The sonnet measurement critic was the fastest and the least careful: one finding rested on a mis-quoted pattern (\b eaten), its drill table was prose rather than per-construction rows. Its two real design findings (rule cannot reach 24; table order) were also found or confirmed by the rulings critic.
- Two readiness critics (one per unit) overlapped on 4 findings (plant d, rename readers, witness drift, kitproof lever): useful as independent confirmation, but about a third of their text was duplicated. Splitting by unit worked; the check-plan items straddle units.
- The lens table had no row that asks "does a new legal range break existing reference builds of a related -D row" (F14 was found by the readiness critic on its own initiative).
- Blinding: no leak noticed. One critic (readylimit) named a denied path (predict.py under docs/dev/lanes/covs1_evidence) as a reader but did not open it.

## Proposed changes
- COMMON template: "Pass patterns in single quotes or via a file; check the "Pattern:" header of every emitted file you cite before reporting a byte-identity or route claim." (MEASURE-4.)
- readiness lens row, append: "For each new legal range coupled to an existing BUILD_D/FLAG_D row, grep every '-D<row>=' reference build in tests/ and check the range's default stays legal there (2026-11-15 r13 covs2d F14)."
- Staffing note: on a design whose check plan spans units, give the sabotage/witness rows to ONE readiness critic and the code items to the per-unit critics, to cut duplication (r13: 4 of 19 readiness findings duplicated).

## Framework notes
- Coordinator pattern held cleanly at small scale: one freeze, one build, one kit, five parallel critics, one verifier, draft in about 20 minutes of wall time; the manager saw nothing until the hand-back.
- The verifier's value was concentrated: of 23 items, the one REFUTED was the only critic error, and it would otherwise have entered the draft as a design finding.
