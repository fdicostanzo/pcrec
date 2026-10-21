# b4prep item 1: the quiet F3 re-time (job 520-kit-b4prep-f3rr, closed by lane b4close)

**NO SIGN CHANGED.** V1 still loses to the walk on both shapes: word-eq (2,0,1) -13.7% (grid2read -13.3%), quad (3,1,0)
-41.3% (grid2read -41.3%). Magnitudes moved by at most 0.4 points. Every value below is MEASURED.

Run: slot `worktrees/memfn-slot/grid2`, `PHASE=F3 CELLS_RE='^f3-(word-eq|quad)$' RAW_TAG=F3rr LAUNCHES=3`, 4 groups, wall 244 s,
GREEN. Raw rows: `raw_F3rr.tsv` (114 rows, copied from `time/raw_F3rr.tsv`). Log: the queue run dir `*-520-kit-b4prep-f3rr/job.log`.

Why MEASURED: no cell is flagged LOAD-SUSPECT (the job log has no such line); load1 at start/end was 1.10-1.31 in all four groups; in all four
groups both walk copies (walk#b, walk#c) sit within the A/A floor of walk (word-eq n64k +5.97/+5.86 ns on 12.4 us; n1m +127/+1 ns on 198 us;
quad n64k -3.3/-7.8 ns; n1m -154/+112 ns, intervals within about 0.1%); counters: each arm's `uses`/`calls` match across arms. Group 1
(word-eq n64k) waited 9 times for the quiet gate before it started, which is the gate working. The slope is computed as grid2read does:
beta = (ns at n1m - ns at n64k) / 983,040 B, ratio = beta / 0.1891 ns/B (u), saving = 1 - beta_arm / beta_walk, from the cell values the
job log tables (medians over 3 launches). Slopes here are recomputed by this lane from those table values, not by `grid2read.py`.

| shape | arm | beta ns/B (new) | ratio (new) | grid2read ratio | saving vs walk (new) | grid2read saving | state |
|---|---|---|---|---|---|---|---|
| (2,0,1) word-eq | walk | 0.189034 | 0.99965 | 1.003456 | - | - | MEASURED |
| (2,0,1) word-eq | V1 | 0.214948 | 1.13669 | 1.136652 | -13.71% | -13.27% | MEASURED |
| (2,0,1) word-eq | S1 | 0.041756 | 0.22082 | 0.220968 | +77.91% | +77.98% | MEASURED |
| (2,0,1) word-eq | A1 | 0.019163 | 0.10134 | (dropped: after load onset) | +89.86% | - | MEASURED, NEW (expected 0.019-0.021: met) |
| (3,1,0) quad | walk | 0.189363 | 1.00139 | 0.999771 | - | - | MEASURED |
| (3,1,0) quad | V1 | 0.267502 | 1.41461 | 1.412251 | -41.26% | -41.26% | MEASURED |
| (3,1,0) quad | S1 | 0.053251 | 0.28160 | 0.286374 | +71.88% | +71.36% | MEASURED |
| (3,1,0) quad | A1 | 0.027021 | 0.14289 | 0.142975 | +85.73% | +85.70% | MEASURED |

What this changes: the (2,0,1) and (3,1,0) key rows in `grid2read/keys.tsv` may be re-issued MEASURED by the converter (E14) from this
table; `keys.tsv` and `SHA256SUMS` are NOT edited by this lane (they are grid2read's record). word-eq's A1 beta now exists (0.019163 ns/B).
r17b_prime §3.1a item 1 is CLOSED.
