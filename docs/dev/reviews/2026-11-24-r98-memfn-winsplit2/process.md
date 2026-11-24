# r98 memfn-winsplit2 process (coordinator)
- 16:09 setup. Subject doc commit d408626c5, branch tip cd4900f6f. Build tree = review worktree at cd4900f6f (memfn/src == origin/main 4d26eef02; only memfn/docs/journal.md differs).
- Rulings frozen at origin/main 4d26eef02 (decisions.md/plan.md last touched 668b4b784). Local main e11c5f4 is BEHIND origin/main (does not hold D204) - critics read origin/main copies.
- D204 record: decisions.md "## D204" heading at 4d26eef02. W2 two-file confirmation: kit manager's, via the launcher's brief only (no record file seen) -> FREEZE NOTE.
- Evidence re-run (last lines): syncheck asm 82 PASS 0 FAIL; pure 44/38; binders B g2 71/4bad, tip+plantcheck all OK; --compile 186 PASS+1 SKIP, g2 75 PASS; census B pins 95/2 (the two pins), tip pins 97/0; tables 2 vs 13. All reproduce the note.
- Plantcheck branch tip 838deefe2; design cites 8bd727eab (ancestor; tests/memfn/scripts equal). plantfix2 branch has no commits past c1efbe938 yet.
- Observation (blind): run_g2.sh has no --plant-check (only run_g2_win, run_g2_pres, run_proof, run_wreply); G1 says "each runner's --plant-check".
- 16:13-16:14 Mac suite lock taken, review tree built (gcc-16, ~1 min), lock released. targets-check warning as r95.
- 16:15 critics launched (opus x2, background, unnamed): fixind, ready. Both returned in the launch turn (~24/25 min), files complete with CRITIC COMPLETE; final replies undeliverable (expected). lanecheck DONE rc=0 both (run by coordinator).
- 16:41 verification inline (V1-V10: 9 HOLDS, 1 PARTLY); no verifier agent (all claims quote/one-call reads). Ruling re-diff at return: no drift (origin/main 4d26eef02; subject branch +1 journal-only commit 77bac2e11).
- Findings: fixind 16 (closure table: 27 CLOSED, 9 PARTLY), ready 16 (per-unit table). Consolidated R1-R26: 14 FIX-NOW, 12 DOC (+1 PLAN half). Overlaps 4, all text items (cites, reader counts, F1 timing, rows_check).
- Budget: ready ~119 compiles of 150; fixind 0.

## Process observations
- Two opus critics on a 673-line re-check with a committed assembler: both finished in ~25 min with dense, verified output. Pre-staging R/evidence (asm, pure, binders outputs) and the plantcheck runner export saved both critics the setup; neither rebuilt.
- The readiness critic's most productive move was running gate commands' preconditions on the actual box (check_targets under strict, host_has, v_section): r95 lesson 3 ("arms must reach") is not enough; arms must also be GREEN at base on the listed box.
- Overlap: four text items found by both; drill assignment split by gate/unit vs closure/fix-induced, but cites and reader counts belong to both. Next time assign "cite checks" and "reader-population counts" to one lens by name.
- The hook blocks any `cd` chained in a compound command, even into the repo root; subshells work. COMMON said so; no critic tripped.

## Proposed changes
- critic skill §4 readiness row, append: "Run each gate arm's command (or its precondition) at the BASE on every box the design lists it for; an arm red at base there is a finding (r98 R1/R2: `make strict` and run_g2_win/run_g2_pres red by construction on the Mac)."
- critic skill §4 readiness row, append: "For each per-commit instrument, ask whether commit k's own re-keyed rows stay in its population, and whether it has a floor (r98 R3: binders.py keyed on B's file names)."
- critic skill §4 fix-induced row, append: "Diff every restated HAZARD sentence too: a restated mechanism can name the wrong code path and drop its guard (r98 R8)."
- COMMON template: name ONE lens for line-cite checks and ONE for reader-population counts (r98: 4 overlaps).

## Framework notes
- A re-check sized at 2 critics + inline verification fit a design whose evidence is mechanical and re-runnable: the coordinator's freeze-time re-run removed a whole class of work (re-confirming numbers) from the critics, who spent it on what the evidence does not prove (intermediate commits, box preconditions). Fits any design that ships a runnable assembler/model.
- 16:50 draft written; worktree removal next; hand-back.
