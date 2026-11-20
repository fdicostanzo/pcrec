# dhremeas report: dense-hit loss re-measure after K38-2

## Summary
(filled after the run; see Verdict)

## What was measured before
Source: docs/dev/lanes/reqpast_report.md F6 (lane reqpast, 2026-11-12, Linux dev box Ryzen 7 7700X, queue job
200-reqpast-bench, single process, gcc -O2, best of 7, ms per search, 1 MB subject), quoted in docs/spec/tuning.md
section 2.41 para 8c. Flag: the whole `-fno-req-handoff` deny vs default, `--engine=vm`.
- Cell 1 (unbounded row `handoff-attempts-unbounded`): `[^@ ]+@x`, subject " @x" repeated to 1 MB (dense; no match):
  1.38 ms on vs 0.81 ms denied (runs 1.284/0.849, 1.380/0.805, 1.427/0.840).
- Cell 2 (bounded row `handoff-attempts`): `[^@ ]{1,5}@x`, same subject: 1.56 vs 0.71 ms.
- Cell 3 (the tail WIN): " @x" then "ab " to 1 MB, `[^@ ]+@x`: 0.009 vs 1.47 ms.
- Binary: lane/reqpast before it was ported onto K38-2 (abi 105 after rpport; main then abi 103/104). Today's main is abi 109.
- NOT recoverable: the bench scratch ($PCREC_TMPDIR/scratch/reqpast/bench/) and job script were never committed and the
  scratch is gone. The harness is reconstructed from the report's words (in-process rx_search loop, per-search time).
  Differences from the original, named: (a) abi 105 -> 109 (K38-2 run API, lookaround L1 and later work are in the
  binary); (b) driver is mine, repetition count and launch statistic differ (median of 7 launches here, best of 7 there);
  (c) the old A/A control did not exist. Same: patterns, subject construction, engine, compiler flag, box.

## The decision rule (declared before timing)
- Cells: C1 dense_unb `[^@ ]+@x`; C2 dense_bnd `[^@ ]{1,5}@x` (both on 1 MB " @x" repeated, no match); C3 tail_unb
  (informational win cell, not part of the rule). All `--engine=vm`.
- Unit: ms per rx_search over 1,500 (C3: 300) calls in one process, after 20 warm calls; one launch = one such figure.
- Launches: 7 per arm per cell, interleaved per round with the arm order rotated; the statistic is the MEDIAN of 7.
- Arms (each differs from its reference in ONE axis): `on` = default (row active; RX_REQ_HANDOFF stamp not "none");
  `off` = `on` plus `-fno-req-handoff` (stamp "none"); `on2` = `on` regenerated and recompiled as a separate binary
  (the A/A control: same source, differs only in being a second binary). Every other axis (pcrec binary, gcc -O2, driver,
  subject, box, load) is shared.
- Noise floor = the largest |on2/on - 1| of the medians over the three cells. Threshold = max(5%, 2 x floor).
- LOSS STILL SHOWN: C1 or C2 has median(on)/median(off) > 1 + threshold.
- NO LOSS: neither C1 nor C2 does. INCONCLUSIVE: floor above 5%, or a stamp check fails (on must not say "none", off must).
- Run through scripts/boxqueue as an idle-ok timing job (docs/dev/lanes/dhremeas_bench/job.sh); load checked with
  scripts/loadshame before queueing.

## Cells and controls
## Results
## Verdict
