# adasim -- an adaptive per-64-byte-stretch WALK/M64 choice, simulated from counts and priced from measured costs

Lane adasim, 2026-10-21. NO clock, no product code. Tools and outputs in `docs/dev/lanes/adasim/` (`run.txt` = full output,
`cells.tsv` = per-cell predictions). Labels: MEASURED = read from a run/file; DERIVED = arithmetic/fit; INTERPRETATION = mine.
Inputs: `flat_report.md` §2 (walk/V1/M64 ns, 41 J1 subjects + 2 anchors), `e8_cells.tsv` (walk/V1 on 94 J1 cells), each cell's
V1 `__member()` set, the real subject bytes (the real member mask of every whole 64-byte stretch, `feat.py`).

## 1. Verdict (INTERPRETATION)
**Worth a timed twin, narrowly, as a pricing probe and not as a loss-free arm.** On these counts the rule removes the big losses
(dense-regular logs/prose/code: M64 +4..+43%, adaptive +0.2..+3.6%) and keeps 90% of M64's wins on the fit cells (total -13.2% vs
M64 -7.4%, V1 about -4%). It does NOT avoid every loss beyond the A/A floor (22 of 41 flat cells exceed the floor, 4 exceed 5%) and
on the sparse-neutral prose class it is worse than M64. Three costs that decide whether it nets out are unmeasured (§5): reading the
rule's inputs (`ob`), the walk-mode bookkeeping (`bk`), and carrying the mode across `rx_search` calls. At `ob` 6 ns it loses.

## 2. Cost model (DERIVED, `fit.py`)
Price an arm as a DELTA to the walk (the DFA/match work is common and cancels; absolute per-arm fits were 22-45% off, deltas 6-9%):
delta(M64, stretch) = -7.37 [stretch empty] + 0.979 members - 1.53 qmiss  ns, qmiss = misses of the subject's ideal order-6 context
predictor on the member bit (e8why's Q numerator: the walk's byte loop mispredicts where stops are unpredictable). V1: -6.29, 0.779, -1.05.
- Fit on flat's 41 J1 subjects (weights 1/walk): |err| median 6.2%, max 22.1% of the walk; leave-one-CELL-out median 6.6%, max 34.6%.
- Hold-out = V1 on the 49 e8-only cells (S03's 4 early-exit subjects, < 4 ns/stretch, cannot be priced from whole-file counts):
  |err| median 11.1%, p90 30.3%, max 78.4%; sign right on 84% of the 25 cells with |delta| > 5% of walk.
- **M64 on the e8-only cells has no measurement.** Two stand-ins, both labelled where used: the raw model, and the model shifted so
  its V1 total equals V1's measured one ("V1-calibrated", validated on flat: that proxy vs measured M64 |err| median 3.1%, p90 9.9%, max 13.6%).
  On the 41 flat cells the per-stretch delta is shifted so ALWAYS-M64 equals the measurement ("calibrated"); the raw model is off by 6.2% median.
- Anchors: the table's ns is ns/pass = ONE 64 KiB buffer; scaled x64 to the features. Calls: matches+1 per subject, evenly spaced (approximation).

## 3. The rules (3 thresholds each; fit on flat's 41 J1 cells, objective mean(d/walk)+mean(max(0,d/walk)), grid 1930 configs)
Cost of a run = walk + sum(delta over M-mode stretches) + S per switch (3 ns) + bk per W-mode stretch (0.3) + ob per non-empty M-mode
stretch (2). A call starts in W (COLD) unless the mode is carried across calls (CARRY, primary; needs a mode byte outside the cursor).
- **R1 (as asked, e64 + trans64):** from the previous stretch's t: enter/stay M if t <= a or t >= b; leave to W only if a+h < t < b-h.
  Chosen (a,b,h) = (1,31,8). The fit is a plateau: 44 of 1930 configs within 0.003 of the best (a 0-1, b 29-33, h 5-12; leave band 6-13..20-26);
  b is barely identified (random-dense subjects enter M through an empty stretch and then stay).
- **R2 (adds members k, my variant after R1 failed on tar):** M if k <= kc or t >= b; W only if k > kc+h and t < b-h. (kc,b,h) = (2,33,12)
  (coarse grid). W-mode is assumed to see k and t exactly (optimistic; see §5 for the degraded view).

## 4. Results (predicted ns; % vs the walk; "losses" = predicted worse than the walk by more than that cell's A/A floor)
| set (n) | ALWAYS-M64 | R1 ADAPT carry | R2 ADAPT carry | ORACLE (per stretch) | losses>floor / >1% / >5% (M64; R1; R2) |
|---|---|---|---|---|---|
| flat J1, total (41, calibrated) | -7.4 | -13.2 | -13.4 | -16.8 | 19/19/16 ; 22/11/4 ; 22/12/5 |
| flat J1, R1 COLD | -7.4 | -1.3 | -1.0 | -16.8 | R1 25/11/4 |
| e8-only, total (49, V1-calibrated) | -10.0 (proxy) | -6.0 | -13.3 | -18.3 | 14/12/7 ; 25/25/12 ; 21/21/7 (V1 measured 23/20/6) |
| e8-only, raw model | +10.6 | +10.6 | n/a | -8.3 | model error dominates (B09 tar +97% raw) |
Per cell class, mean of cells, % vs walk (M64 = measured on flat; ADAPT R1 carry / worst cell in class):
L10 logs +23.7 -> +1.0 (+3.6) | P14 prose +19.6 -> +0.3 (+0.5) | C16 code +3.8 -> +0.6 (+1.3) | P12 prose +2.7 -> +5.6 (+8.2, worse than M64)
| P05 -42.4 -> -40.8 | N08/N10 -60.3 -> -60.3 | B10 binary -38.7 -> -37.2 (worst -23.9) | anchors dig L1k +28.1 -> +1.5, dfa-hat L32 +31.4 -> +0.7.
- **Loss avoidance:** not complete. The dense-regular losers drop from +18..+43% to <= +3.6%, but stay above their 0.01-0.3% floors (bk
  alone is 0.2% on P14); the sparse-neutral prose class (P12/P15/P04/P06/P24, E~0.3, k~1) is +2..+10% for M64 and for ADAPT, where ORACLE is -3..-8%:
  the calibrated per-stretch delta is positive on average there and the rule cannot tell which stretches carry it.
- **Share of M64's wins kept:** 0.90 (R1), 0.93 (R2) on flat; 0.79 (R1), 0.84 (R2) on e8-only; ORACLE share 0.79/0.80 flat.
- **Worst cell:** flat +8.2% (P12 pg2600; M64 +5.0%). e8-only: R1 +30.8% (B09 libpng tar: k=57 members/stretch, t=3.6, so "few transitions"
  reads as sparse; V1 measured +9%); R2 +9.7% (P15 pg1184). Anchors under R1 +0.7/+1.5%; R2 CARRY +36% on dfa-hat L32 (it carries M across
  32-byte calls, which is M64's loss), R2 COLD +0.9/+1.5%.
- **Vs the measured best arm per cell (walk/V1/M64):** R1 carry flat mean +3.2%, median +1.4%, worst +16.7%; e8-only (walk/V1) mean +2.2%.
- **Mode switches per MiB of subject (R1 carry; M-share of bytes):** binary 871 (86%), code 183 (50%), logs 939 (30%), prose 255 (82%), non-English
  115 (96%), structured 10351 (one dense gazetteer file, 56%), anchors 0. R2 on flat: binary 221, code 358, logs 1651, prose 31, non-English 0.9. R1 COLD: binary 2338, prose 819.
  One switch per 0.6-1 KiB on logs is cheap at 3 ns: the switch cost is not the sensitivity (below).

## 5. Sensitivity (INTERPRETATION of the table in `run.txt`)
- **Switch cost S 0..10 ns:** flat total -13.4 -> -12.8, e8-only (R1) -6.2 -> -5.4. Negligible.
- **Walk bookkeeping bk 0 / 0.3 / 1.0 ns per W stretch:** flat losses>floor 15 / 22 / 22, total -13.5 / -13.2 / -12.7. bk decides the "above the floor" count, not the size.
- **Input-reading cost ob 0 / 2 / 6 ns per non-empty M stretch (popcount of m^(m>>1) and of m; no hardware popcnt on the baseline target, §3 of flat):**
  flat R1 -14.1 / -13.2 / -11.4; e8-only R2 -14.5 / -13.3 / -10.8 with >5% losses on 1 / 7 / 25 of 49 cells. **The decisive unknown.**
- **Thresholds:** flat total moves <= 3 points over (a 0..3, b 27..33, h 3..11); R1 e8-only swings -2.7..-7.9 with b; R2 e8-only stays -13..-14.6 unless h <= 4
  (-5.3 at h=4, -3.4 at h=0): hysteresis is needed, its width is not delicate.
- **Mode carried across calls:** COLD loses the random-dense binaries (zip/gz/bz2 have ~2 calls per stretch) and the sparse wins on short calls: flat -1.3% vs -13.2%,
  wins kept 0.13 vs 0.90. Persisting the mode is required, and it breaks R2 on 32-byte calls (above).
- **Degraded walk-mode view (stops only, stops = rho * runs; python loop on the 32 flat cells with <= 120k stretches):** rho 1.0 -> total -4.9%, wins kept 0.87;
  rho 0.5 -> -3.4%, 0.64; adding a mask sample every 16th W stretch (4 ns) restores 0.82. (Loop equals the vectorised rule at rho 1: checked.)

## 6. What this does not show
- No timing; M64 on e8-only cells is a proxy; the model misses by 6-11% of the walk, so cells where ADAPT is within ~5% of the walk are inside model noise
  (the `>5%` column is the safer read). Early-exit subjects (S03 xml/geojson/csv) are excluded.
- W-mode input availability (R2 needs k there), the cursor-external mode byte, and the cost of ob/bk are assumed, not measured.
- A timed twin should be R2-with-persistent-mode on: L10 openstack, P14 pg2600, P12 pg2600 and P15 pg1184 (sparse-neutral, the likely loser), B10 zip, B09
  libpng.tar (dense, few transitions) and dfa-hat L32 -- enough to pin ob, bk and the call-boundary behaviour. If ob measures near 6 ns the idea is closed.
