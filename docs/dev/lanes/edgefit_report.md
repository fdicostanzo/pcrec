# edgefit — [OPT-EDGE] I-82 fit + m=2 floor-cell mechanism (2026-09-21)

Lane `edgefit`, sonnet, data + one report, no `src`/`tests` code. Source
logs: `studies/scan_edge_ladder/runs/2026-09-21-i82-89d986c3/{ladder_run1,
floor_run1,floor_run2}.log`, fetched verbatim from the Linux reference box
(`duxevents@100.69.121.107:/home/duxevents/pcrec/studies/scan_edge_ladder/
out/`) at bench executor item I-82, pcrec pin `89d986c3`. Reproduction
script committed beside them:
`studies/scan_edge_ladder/runs/2026-09-21-i82-89d986c3/fit.py` (stdlib
only; `python3 fit.py` from that directory reproduces every number below;
its captured stdout is `fit_output.txt` in the same directory).

I do not rule on the floor. This is the numbers the manager rules on.

## Commands

```
timeout 120 scp duxevents@100.69.121.107:/home/duxevents/pcrec/studies/scan_edge_ladder/out/{ladder_run1.log,floor_run1.log,floor_run2.log} \
  studies/scan_edge_ladder/runs/2026-09-21-i82-89d986c3/
timeout 60 python3 studies/scan_edge_ladder/runs/2026-09-21-i82-89d986c3/fit.py
```

## Part 2 — the ladder fit

The README (`studies/scan_edge_ladder/README.md`) states the isolation
that works is BEFORE (`9d8401a`, per-edge `if` chain) vs AFTER (`b048fa61`,
shared-sentinel dispatch) **on the same machine** — same states, same
edges, only the dispatch differing — and that the ladder exists to fit
`t(k) = a + b·k` over machines carrying 1..4 forward edges, splitting the
fixed per-artifact cost (`a`) from the per-edge one (`b`). `noedge` is
named explicitly as a **control, printed and never subtracted**.

**Before fitting anything**: each rung is a *different pattern and a
different near-miss subject*, not one machine scaled — `run_ladder.sh`'s
own `PAT`/`SUBJ` tables (`\d{2}y` / `a1y ` at k=1, up through
`\d{2}y\d{2}y\d{2}y\d{4}` / `12y34y56y789x ` at k=4). Rung 4's near-miss
straddles the pattern one digit short of the FINAL `\d{4}` group — the
deepest, latest failure point of any rung — so a rung-4 candidate that
enters the chain does much more "productive" in-chain byte-consumption
per entry than rung 2 or 3's shorter near-misses do, which dilutes the
per-byte cost of the entry/dispatch mechanism this ladder is measuring.
**That is what the README means by fitting `t(k)=a+b·k`: it is the
intended computation, run over exactly this ladder of test artifacts** —
but it is worth stating plainly that the four points are not a clean
"same subject, more edges" scaling series, so `b` estimates the average
per-rung slope of *this specific ladder*, not a subject-invariant
marginal edge cost. This is why rung 4 reads faster in absolute ns/byte
than rung 2 or 3 on every arm (see per-rung medians below) — the fit
below is still exactly what the README specifies, reported honestly with
this caveat rather than silently treated as a clean isolation.

### Per-rung medians (over 15 rounds, ns/byte)

| arm | k=1 | k=2 | k=3 | k=4 |
|---|---|---|---|---|
| before | 2.4423 | 3.3550 | 2.9923 | 1.6735 |
| after | 1.4380 | 2.7826 | 2.7711 | 1.4383 |
| step11 | 1.4438 | 2.7790 | 2.7272 | 1.4546 |
| noedge | 1.4418 | 4.0460 | 3.8430 | 1.8038 |

### Fit `t(k) = a + b·k` over the medians (k=1..4)

| arm | a (fixed) | b (per-rung slope) |
|---|---|---|
| before | 3.2831 | −0.2669 |
| after | 2.1101 | −0.0011 |
| step11 | 2.1060 | −0.0019 |
| noedge | 2.5629 | +0.0883 |

`after`'s slope is essentially flat (−0.0011 ns/byte per rung) against
`before`'s clearly negative −0.2669 — consistent with the design intent
(the shared-sentinel dispatch removes the per-edge cost the old if-chain
paid), though the confound above means "flat" here is "flat across this
specific ladder of subjects," not proven subject-invariant.

### Per-round fit stability (15 independent 4-point fits per arm)

| arm | b median | b IQR | b min | b max |
|---|---|---|---|---|
| before | −0.2097 | 0.6407 | −0.8236 | 0.5523 |
| after | −0.0361 | 0.1311 | −0.8226 | 0.1088 |
| step11 | −0.0071 | 0.1075 | −0.5432 | 0.3656 |
| noedge | +0.0860 | 0.1179 | −0.4392 | 0.2079 |

The per-round `b` for `before` is wide (IQR 0.64, spanning negative to
positive) — several individual rounds show `before` NOT monotonically
decreasing in k (e.g. round 6, `before` at k=2 is 6.2176, an outlier).
`after`/`step11`/`noedge` are tighter (IQR ~0.11-0.13) but still cross
zero at both ends — the per-round fit is noisy at n=4 points, and the
medians-based fit above is the more stable read.

### Per-edge cost — the README's named isolation (before − after), never noedge

| k | before − after (ns/byte) |
|---|---|
| 1 | 1.0043 |
| 2 | 0.5724 |
| 3 | 0.2212 |
| 4 | 0.2352 |

Fit of `diff(k) = a + b·k`: **a = 1.1729, b = −0.2658** (identical to
`b_before − b_after` by OLS linearity, confirmed in `fit_output.txt`).
The difference is **not flat across k** and is not linear either — it
drops sharply from k=1 to k=3 (1.00 → 0.22) then ticks back up slightly
at k=4 (0.24), tracking the subject-depth confound above rather than a
clean per-edge marginal cost. Read literally, the branch-vs-main
isolation shows STEP 1 saving the most at k=1 (≈1.0 ns/byte) and the
least at k=3 (≈0.22 ns/byte), with k=4 not the extrapolated continuation
of a line through k=1..3.

## Part 3 — the m=2 floor cell, by mechanism

### D77 gap test (|median−1| vs IQR, vs whether 1.0 ∈ [min,max]) — all 8 cells, both runs

| run | m | family | median | IQR | \|med−1\| | min | max | 1 in range | separated |
|---|---|---|---|---|---|---|---|---|---|
| run1 | 2 | exact | 1.0629 | 0.6706 | 0.0629 | 0.9908 | 2.6394 | yes | **no** |
| run1 | 2 | nullable | 0.8862 | 0.1468 | 0.1138 | 0.8363 | 1.8079 | yes | **no** |
| run1 | 3 | exact | 0.9990 | 0.0084 | 0.0010 | 0.9743 | 2.4823 | yes | **no** |
| run1 | 3 | nullable | 0.9614 | 0.1917 | 0.0386 | 0.4784 | 2.1138 | yes | **no** |
| run1 | 4 | exact | 1.0021 | 0.0065 | 0.0021 | 0.9899 | 1.0410 | yes | **no** |
| run1 | 4 | nullable | 0.9568 | 0.0799 | 0.0432 | 0.8778 | 1.9913 | yes | **no** |
| run1 | 8 | exact | 0.9979 | 0.0288 | 0.0021 | 0.5869 | 1.2265 | yes | **no** |
| run1 | 8 | nullable | 0.9812 | 0.0348 | 0.0188 | 0.4214 | 2.1526 | yes | **no** |
| run2 | 2 | exact | 1.4379 | 0.8307 | 0.4379 | 0.9935 | 2.4578 | yes | **no** |
| run2 | 2 | nullable | 0.8908 | 0.2238 | 0.1092 | 0.8419 | 1.7574 | yes | **no** |
| run2 | 3 | exact | 0.9989 | 0.0051 | 0.0011 | 0.9893 | 1.8052 | yes | **no** |
| run2 | 3 | nullable | 0.9750 | 0.2438 | 0.0250 | 0.8863 | 1.6694 | yes | **no** |
| run2 | 4 | exact | 1.0013 | 0.0132 | 0.0013 | 0.9805 | 1.2227 | yes | **no** |
| run2 | 4 | nullable | 0.9806 | 0.0887 | 0.0194 | 0.8812 | 1.8362 | yes | **no** |
| run2 | 8 | exact | 1.0507 | 0.1031 | 0.0507 | 0.9864 | 1.2240 | yes | **no** |
| run2 | 8 | nullable | 0.9869 | 0.0237 | 0.0131 | 0.9625 | 1.0299 | yes | **no** |

`separated` = `|median−1| > IQR` AND `1.0 ∉ [min,max]`. **Zero of 16
cells separate.** Every cell's own round-to-round range bridges back to
1.0 — the widest excursions (m=2 exact, both runs; m=2 nullable run1)
are exactly where the per-round range is also widest, so the "no gap, no
move" test (D77) reads NO on every cell, consistent with
`limits.def:371`'s 2026-09-04 finding that kept `PCREC_MIN_SCAN_CHAIN`
at 2.

### m=2 exact / m=2 nullable — per-round mechanism attribution

Threshold: ratio > 1.20 = HIGH mode, else low mode (rough mode centers:
~1.0 low, ~1.8 high — chosen to separate the visibly bimodal cluster;
see `fit_output.txt` for every round's raw triple).

| run | family | n HIGH / 15 | edge low-mode median | edge high-mode median | noedge low-mode median | noedge high-mode median |
|---|---|---|---|---|---|---|
| run1 | exact | 7 | 2.3043 | 4.1646 (+81%) | 2.3094 | 1.9041 (−18%) |
| run1 | nullable | 3 | 3.2545 | 4.9315 (+52%) | 3.6791 | 3.0579 (−17%) |
| run2 | exact | 8 | 4.1691 | 4.2465 (+2%, flat) | 4.1684 | 2.1051 (**−50%**) |
| run2 | nullable | 3 | 3.2477 | 5.2482 (+62%) | 3.4205 | 3.0109 (−12%) |

**(a) which arm moves — answer: BOTH, and which one dominates is NOT
consistent between the two runs of the same cell.** In run1 (both
families) and run2 nullable, the **edge** arm's absolute time jumps
(+52% to +81%) while noedge drops only modestly (−12% to −18%) — the
edge arm dominates the swing. In run2 exact, the pattern **inverts**:
edge is essentially flat (4.1691 → 4.2465, +2%) while **noedge collapses
by half** (4.1684 → 2.1051, −50%) — here noedge dominates. So the
bimodal ratio is not "the edge build gets slow" as a fixed property of
the mechanism; it is whichever of the two independently-compiled binaries
happens to read fast or slow in a given round, and that identity flips
between runs even for the identical cell.

**(b) does the mode correlate with round index or the preceding cell?**
Round-index correlation is weak in both runs (Pearson r = 0.203 run1,
0.302 run2 for m=2 exact ratio vs round number 1..15) — not a drift or
warm-up effect. Correlation with the immediately preceding cell in run
order (round r's `m2,exact` is measured right after round r−1's
`m8,nullable` — the loop order is `(m2,exact)(m2,null)(m3,exact)
(m3,null)(m4,exact)(m4,null)(m8,exact)(m8,null)` repeating every round) is
**inconsistent across runs**: Pearson r(m2exact[r], m8null[r−1]) = 0.622
in run1 (moderate) but −0.084 in run2 (none). A simple mode-match rate
(both HIGH or both low, threshold 1.20) is exactly 7/14 = 50% in both
runs — chance level. **No reliable adjacency effect either by round
index or by preceding cell.**

**(c) is the split consistent across run1, run2, and the O-42 runs?**
Within `m=2 exact`, the HIGH-mode round SETS only partly overlap between
run1 `{2,4,7,8,9,12,15}` and run2 `{1,4,7,9,10,12,13,15}` — intersection
`{4,7,9,12,15}`, 5 of 7-8 rounds. Within `m=2 nullable` the overlap is
much thinner: run1 `{3,11,13}` vs run2 `{2,3,14}`, intersection only
`{3}`. **The bimodal signature's existence is consistent (both runs show
it, both families show it to some degree), but which specific ROUND
lands in which mode is not reproducible round-for-round.** O-42's own
floor logs cannot be compared round-for-round here: `edgefix_report.md`'s
fault-2 diagnosis is that O-42's floor cells read `forward edges = 0`
("TAKES NO EDGE") throughout, i.e. that harness run did not engage the
scan-edge mechanism these numbers measure, so its "edge" column is not
the same measurement. `edgefix_report.md`'s own quoted m=2-exact excerpt
(rounds 12-15 reading ~4.18/4.20, ratio ≈1.0, then two rounds at ratio
≈1.81) does not numerically match either run1 or run2 fetched here
(confirmed by direct comparison — no overlap in any row), so it is
evidence from a different measurement pass (plausibly the lane's own Mac
verification build, not archived as a file). What IS directly
comparable is the **signature itself**: `edge2_report.md` §9.3
(2026-09-04, a different pin and toolchain) already recorded this exact
shape — "median 1.78, IQR 0.87 ... bimodal ... plausibly because
`[0-9]{2}x}`'s 256 KB sweep is the shortest-running cell of the eight" —
and it reproduces again here, independently, on ubuntubudu at I-82. The
signature is reproducible across at least three independent measurement
passes; the specific rounds it lands on are not.

## What the numbers say

Over 16 m×family cells across two independent 15-round floor runs, none
separate from an edge/noedge ratio of 1.0 by the D77 gap test — the
widest cells (m=2, both families) are exactly the ones with the widest
per-round range, so the excursions do not clear their own noise floor.
The m=2 bimodal signature is real and reproduces across three
independent measurement passes on two toolchains, but it is not a fixed
property of either binary: in three of four run×family combinations the
edge (scan-edge) binary's own absolute time is what jumps in the HIGH
mode, while in the fourth (run2, exact) it is the noedge binary that
drops by half while edge stays flat — and neither round index nor the
immediately-preceding cell in measurement order predicts which round
lands in which mode (round-index correlation ~0.2-0.3, preceding-cell
correlation inconsistent between runs at 0.62 and −0.08, mode-match
rate exactly 50%). The ladder's before/after isolation shows the
shared-sentinel dispatch's slope essentially flat (b≈−0.001 to −0.002)
against the old per-edge if-chain's clearly negative slope (b≈−0.27) over
the medians, but each rung is a structurally different subject (deepest
near-miss at k=4), so that flatness is demonstrated for this specific
ladder rather than proven subject-invariant, and the before-minus-after
per-edge-cost series (1.00, 0.57, 0.22, 0.24 ns/byte at k=1..4) is
neither flat nor linear in k.
