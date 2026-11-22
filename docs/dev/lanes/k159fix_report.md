# k159fix report

## Summary
K159 fixed on lane/k159fix: `pcrec_width_walk` (src/facts/kset.c) stops when the closed frontier's consuming set repeats an earlier one, which proves the walk has entered a cycle. Answers are identical by construction (the argument is below and in the code comment). On the box, nested `+` at d=14 dropped from 20.2 s to 0.07 s CPU, and d=15 takes 0.2 s. Added a guard, `[facts-width-cpu]` in tests/codegen/run_facts_checks.sh, with sabotage row S3505. K159 and [K159-PLUS-SUPERLINEAR] are marked fixed-on-lane.

The corpus-wide proofs run as box-queue jobs and are OWED (keys under STATE AT HANDOFF). The kit's 736-739 held the box when the jobs were queued. Those proofs are the emit_sweep identity (bytes plus the facts stream), the four-cell `width` comparison, the S3505 mech row and the quiet timing table. The cloud make test is also OWED (section below).

Premise: src/facts/ is unchanged between plusprof's 715b90b5f and the branch point 92f5e77b6 (`git log 715b90b5f..92f5e77b6 -- src/facts/ src/ir/nfa.c` is empty), so plusprof's profile still applies: 83% wdrain, 10% wclose, 7% the walk. Re-measured at 92f5e77b6 on a loaded box (load about 17): d=10 0.06 s, d=11 0.25 s, d=12 1.19 s.

## Fix
What the walk carries from one depth to the next is the SET `w.cur`, the closed frontier's consuming states. `wadvance` reads only that set: it takes the successors and closes them. The step's `accept` comes from the same closure. So `cur[j+1]` and `accept[j+1]` are pure functions of the set `cur[j]`, and the order does not matter because the closure of a seed set is a set.

Suppose `cur[j]` equals an earlier `cur[c]`. Then every later frontier is one of `cur[c+1..j]`. All of those are live (the walk would have exited otherwise), so the frontier never empties. That is the docstring's own "live past the NFA's state count" case, so bmax = `PCREC_W_UNBOUNDED`, which is what the old loop returned at `j > n`. Every later accept is one already met at a depth of j or less, so no new first accept (bmin) can appear.

The repeat test is placed after the depth-j accept and empty checks, so depth j is fully accounted for before the stop. The `accept` flag does not need to be in the key, because the next step does not read it.

Detection uses Brent's checkpoint. The set at depths 0, 1, 2, 4, 8, … is kept as membership stamps (`ck[s] == ckid`, one int per state, arena). Each later frontier is compared with it EXACTLY: same size, and every member stamped. `cur` has no duplicates, because the generation stamp pushes each state once per closure. So no hash is involved and a collision cannot change an answer. A cycle of period λ that starts by depth μ is caught by depth 4·max(μ, λ). Memory is one set: O(n), not O(steps x n).

The `j > nfa->n` exit stays as a backstop, so no pattern takes more steps than before. The only added per-step cost is one O(|cur|) comparison, which is less than the closure itself.

Shared shape:
- `pcrec_kset_walk` steps the same iterator, but it is bounded by `PCREC_PREFIX_K_MAX`, so it has no unbounded walk and the stop is not needed.
- `pcrec_land_char` does not step the union frontier. It closes each byte's successor set exactly, and it already memoizes its mid-character frontiers as sorted lists (a re-entry is a cycle).
- So only `width` had the defect, and the fix is confined to it (one function).

No caller-observable change (same fact values, same bytes), so no spec hunk. Bug fix, so no deny/force flag (pcrec-flag-follows-caller-effect). Commits: dc08453cc (fix), 8dede63f7 (guard, sabotage, evidence script), 154d68d64 (K159/plan/CLAUDE.md).

## Identity
- (1) The `width` fact in all four cells. docs/dev/lanes/k159fix_evidence/width_cells.py reuses emit_sweep.py's own corpus enumeration plus docs/dev/lanes/spanpick_bench_patterns.txt (400 bench patterns). For each distinct pattern it compares the `width` row (status, value, why) of `--features all [--engine=vm] --emit-facts=byte,utf8` between the 92f5e77b6 build and the lane build.
  - Smoke run, 4 patterns including nested `+` d=11: `width_cells: DONE patterns=4 cells=14 derived=8 differ=0 rc_diff=0`.
  - The vm cells list `width` as not derived. The fact is E3, sealed only on the unanchored DFA route, so under `--engine=vm` it is not computed. The comparison still covers those rows for equality.
  - CONTROL: a planted bmin+1 at the stop, built as scratch pcrec.sab, made the same script print 6 DIFFER lines and exit 1. So the instrument can fail.
  - The full run is box-queue job `k159fix-widthcells`, OWED. Completion line: `width_cells: DONE patterns=N cells=N derived=N differ=0 rc_diff=0`.
- (2) Emitted bytes: `scripts/emit_sweep.py --ref 92f5e77b6` over the corpus plus the same 400 bench patterns. Its facts stream (6) compares the whole `--emit-facts=byte,utf8` listing at the default engine, so it is a second, whole-record check on (1). Box-queue job `k159fix-sweep`, OWED. Expected: rc 0, no movers; movers file $PCREC_TMPDIR/scratch/k159fix/sweep.movers.tsv. Spot check: d=10 and d=12 nested `+` `.c` are byte-identical before and after, apart from the `#include "<basename>.h"` line, because the two runs used different output names. If any byte moves, the fix is wrong: stop and report, no abi event.

## Timing
CPU seconds, `build/pcrec -p rx -o OUT.c --pattern P`, nested `+` as in the brief.

| d | before (plusprof, 715b90b5f, load1 1.5) | before (92f5e77b6, load ~17) | after (lane build, load ~17) |
|---|---|---|---|
| 10 | 0.05 | 0.06 | 0.00 |
| 11 | 0.22 | 0.25 | - |
| 12 | 1.04 | 1.19 | 0.01 |
| 13 | 4.74 | - | 0.03 |
| 14 | 20.16 | - | 0.07 |
| 15 | - | - | 0.21 |

RSS is unchanged: d=15 is 98.6 MB after, and the NFA itself doubles per level. The before/after table on a quiet box (loadshame before and after, d=10..15 both sides) is box-queue job `k159fix-timing`, OWED. It runs on the box the queue holds, and its log carries the loadshame lines. Completion line: `timing: DONE`, with 12 `d=N base|new cpu=` lines. After the fix the cost is no longer in the width walk. The rest grows with the NFA (doubling per level), so a d=15+ residue belongs to whoever owns NFA size, not to this row.

## Growth cell
`[facts-width-cpu]` in tests/codegen/run_facts_checks.sh, section 9b, rides `make test-codegen`. It compiles the d=14 nested `+` (`--emit-facts`) under `scripts/watchdog -c 5 -s 120` and checks that the listed `width` is `[1,inf)`. That value is written by hand: the shortest match is one byte, and the pattern is unbounded.

The bound is 5 CPU seconds, derived from measurements. The fixed whole compile costs 0.07 s on the dev box, so 5 s is 70x headroom for slower boxes and sanitized builds. The unfixed walk costs 20.2 s on the fastest box we have, and every other box is slower, so 5 s is a 4x margin under the old cost. CPU time does not move with load. The 120 s wall bound is only a hang guard.

The guard passes on the lane build: `PASS: [facts-width-cpu] nested + 14 deep lists width [1,inf) within 5 CPU seconds`, 17 passed, 0 failed.

Planted-bug row S3505 (`tests/mech/sabotages/S3505_width_walk_no_repeat_stop.sh`) disables the checkpoint compare. Its field validation passes (VALIDATE_ONLY, 1 definition valid). The real row is box-queue job `k159fix-mech`, OWED, completion `== mech run COMPLETE: 1 rows`, expected DETECTED.

ID NOTE for the manager: the brief granted S3500-S3509, but the ledger worktrees/.mgr/sabotage_ids.txt already gives S3500-S3504 to the kit's bsu1fix, and S3500/S3501 exist on main (run_skip_pins.sh). So this row uses S3505, which is inside the grant and after the ledger's "next free". The ledger is the manager's: S3505 needs recording there.

`make -s strict`: clean. `make -s test-plan-lint`: 2 passed, 0 failed. The plan row moved from Boonies into Active, because PL13 refuses STATE:started outside Active.

## Cloud make test
Dispatched: `scripts/cloudrun --owner main --kind test --name k159fix-a1e541f --ref a1e541f8c` printed `cloudrun: DONE rc=0 pushed a1e541f8c -> cloud/main/test/k159fix-a1e541f owner=main kind=test`. Proof: `git ls-remote origin 'refs/heads/cloud/main/*/k159fix*'` lists `a1e541f8c497c5bef768068a00724b1e51cdb99a refs/heads/cloud/main/test/k159fix-a1e541f`. a1e541f8c holds all of the lane's code; later commits are report text only. The verdict reaches main through queuewatch as CLOUD-DONE. Not waited for.

## STATE AT HANDOFF
Committed on lane/k159fix; code complete at a1e541f8c. Last ruling applied: none (k159fix_rulings.md empty at every checkpoint, R-0).
OWED: k159fix-sweep k159fix-widthcells k159fix-mech k159fix-timing (box queue) + cloud make test cloud/main/test/k159fix-a1e541f
OWED box-queue jobs (queued 2026-11-22 ~09:10, behind kit 736; scripts in $PCREC_TMPDIR/scratch/k159fix/jobs/):
- `k159fix-sweep`: emit_sweep vs 92f5e77b6, corpus + bench; green = rc 0.
- `k159fix-widthcells` (after sweep): `differ=0 rc_diff=0`.
- `k159fix-mech`: S3505 DETECTED.
- `k159fix-timing` (after mech): the quiet before/after table.

Read the verdicts with `scripts/monread k159fix --wait` or `scripts/boxqueue state KEY`. A mover or a differ is a STOP: report it, do not land.
OWED cloud: make test, branch cloud/main/test/k159fix-a1e541f at a1e541f8c (verdict via queuewatch CLOUD-DONE).
Scratch: /var/tmp/pcrec-pcrec/scratch/k159fix (pcrec.base = the 92f5e77b6 build; nest.py the witness generator).
