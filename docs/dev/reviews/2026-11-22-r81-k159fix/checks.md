# CRITIC checks: k159fix (r81)

## Findings

### CHECK-1 (SUSPECTED, maintenance/answer-guard) wrong-repeat mutants not caught by [facts-width-cpu]
The guard's witness (nested + 14 deep) is UNBOUNDED, and `[1,inf)` is also what ANY over-eager stop returns (e.g. stop on the first frontier, or `ncur == nck` size-only). The guard therefore checks only CPU. Bounded-width protection comes from other tables: run_facts_checks.sh [facts-sl1] (~l.535: `abcd` [4,4], `a|bc` [1,2], `.{3,8}` [3,32], `.` [1,4], `é` [2,2]). Those catch a size-only match (abcd: frontier size 1 at every depth -> UNBOUNDED, caught). Mutants I could NOT find a witness for (acyclic frontiers whose states recur at other depths, e.g. `(?:a|bb)c`: c is in the depth-1 and depth-2 frontiers): (a) subset-instead-of-equal (drop the `w.ncur == nck` guard so `i == w.ncur` means "cur subset of ck"); (b) not bumping `ckid` (stale marks accumulate, so a later frontier that is a subset of the union of older checkpoints "repeats"); (c) `i <= w.ncur` (reads ck[cur[ncur]], out of bounds; only ASAN/UBSAN would see it). All three are plausibly invisible to the existing tables (no bounded witness with a state shared across depths in the hand table). Confirm: build the mutants and run [facts-sl1] + rxt corpus; or add `(?:a|bb)c` [2,3]-style bounded witnesses with a recurring state. Blast radius: a wrong UNBOUNDED on a bounded pattern loses width-based skips (answer-preserving but a silent optimisation loss); wrong BOUNDED cannot arise from the stop. facts/kset.c:431-436.

### CHECK-2 (CONFIRMED-by-reading, design/minor) guard has no -m memory bound
Section 9b wraps the compile in `watchdog -c 5 -s 120` without `-m`; CLAUDE.md's rule for a possibly-runaway compiler is wall+RSS+CPU. Harmless today (arena ck array is n ints) but an unfixed/regressed walk that allocates would not be RSS-capped. run_facts_checks.sh:593.

### CHECK-3 (SUSPECTED, doc) cost figures in the comment do not match this box
Comment says whole compile "0.07 s CPU" and bound "70x the fixed cost". Measured here (loaded box, subject build, exact guard command): cpu 0.19+0.09 = 0.28 s, wall 0.40, rc 0 (so ~18x headroom, still very safe; 10x slower fixed walk = 2.8 s passes, 20x fails). The "x70" is box- and load-dependent; the statement "CPU, not wall, so a loaded box does not move it" holds. Reword to the measured range. run_facts_checks.sh:583.

### CHECK-4 (CONFIRMED, design) width_cells.py can exit 0 with zero cells / zero derived / both-sides-failed
No floor on patterns, cells or derived (it only prints them). es.run returns rc None on timeout (rows empty) on both sides: ra==rb so no RC-DIFF, no cells counted, exit 0. A compile refusal on both sides (same nonzero rc, no width row) likewise contributes nothing. Zero patterns (enumerate_corpus empty, no files) -> `patterns=0 cells=0 ... differ=0` and exit 0. A missing binary raises FileNotFoundError (crash, nonzero: fine). Also the nested-+ witness itself is not asserted present: BASE takes ~20 s CPU there, and a deeper one would time out on BASE with rc None vs NEW rc 0 -> RC-DIFF (exit 1 by design), so a patterns file with K159 witnesses always "fails" and cannot be told from a regression. Not run by me (corpus sweep is thousands of compiles, over the 300 budget). docs/dev/lanes/k159fix_evidence/width_cells.py:44-57.

### CHECK-5 (CONFIRMED, minor) width_cells.py row fields match the real listing
Listing row: enc, fact, grain, epoch, status, used, value, why, note (verified on a real `--emit-facts` line: `byte width pattern E3 derived yes [1,inf) <why> core; owner...`). Script reads f[4] status, f[6] value, f[7] why: correct. `derived` counts BASE-side derived cells only (fine as a floor candidate). Uses ThreadPoolExecutor(12) with no nice/boxqueue: not a problem for an evidence script, but heavy on a shared box.

### CHECK-6 (CONFIRMED, minor) sabotage row scoring does not name WHICH check fails
Row S3505 uses SAB_SUITES='facts'; the facts arm scores any `checks failed:` > 0 (run_sabotage_matrix.sh:3251-3256). So DETECTED could come from another failing facts check; here the plant fails only 9b (rc 123, cpu 6.15, see below), so the row is currently honest, but the arm cannot distinguish. Pre-existing design of the arm, not a fix-lane defect.

## PROBED-AND-HELD
- Guard's exact command (pattern built by the same loop, 99 chars; `--emit-facts`, `-c 5 -s 120 -l k159-width -L log`):
  SUBJECT: rc 0, cpu 0.19+0.09 s, wall 0.40, width row `byte width pattern E3 derived yes [1,inf)`: guard passes.
  PLANT S3505: rc 123 (CPU kill), cpu 6.15+0.69 (killed at 5 s), wall 5.46: guard would fail with the right message (123 branch).
  BASE: rc 123, cpu 6.14+0.69: the guard fails on the unfixed walk too (the check goes red for the right reason, and the 123 branch is distinct from rc 124/125/127 which go to the generic `rc N` bad).
- Wrong-reason greens: missing binary -> wrc 127 -> bad; empty listing -> wbv '' != '[1,inf)' -> bad; wall kill 124 -> bad; only rc 0 + exactly `[1,inf)` passes. grep -F `fact=width<TAB>` cannot match other fact names (tab-terminated). The default `--emit-facts` lists byte only, so the value is one line.
- Sabotage anchor: `python3 -I worktrees/crit-k159fix/scripts/m6read_check_sab_anchors.py` (its root derives from the script's own location, so the review tree's copy must be run; the main-repo copy would check main) with TMPDIR set: "sabotages checked: 1377 (1436 anchor sites) / all anchors resolve"; `if (w.ncur == nck) {` occurs exactly once in src/facts/kset.c (git grep -c = 1), SAB_COUNT=1 correct. The script reads files only, writes nothing.
- Row's replacement `if (0 && ...)` keeps the checkpoint code live, so the plant removes only the stop; the plant build behaves like BASE in cpu.
- Size-only repeat mutant: caught by [facts-sl1] `abcd` [4,4] (reasoned; not built). Largest witness: nested + 14 deep, ~65,000 NFA states, 99-char pattern; probes: 3 compiles by hand (subject, plant, base) plus 1 listing.

## STATE AT HANDOFF
OWED: none. All probes finished, no processes left running, no repo writes.

CHECK COMPLETE
