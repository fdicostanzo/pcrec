# R-17 step 2: the twin timing reading (2026-10-11, kit manager)

## The run

- Run on main's GO, 22:46-22:59: Linux dev box, 7700X Zen 4, core 14 (SMT
  sibling 6 idle), gcc 15.2.0, `-O2 -fPIC`, R 7, MIN_MS 50.
- Command: `run_time.sh` (see its header). It wrote 1,106 rows with void 0.
  The exhaustive re-check ran first: 65 twins, 1,874,741,290 calls,
  0 mismatches.
- Data: `out/slot/times.tsv` (raw), `out/slot/check.txt`, `out/slot/run.log`.
- Tier: kit timings are UNOFFICIAL (D144 add. 4). An official verdict is a
  bench run on each targeted box, requested through main.

## Each form against today's `table` walk

ns per call (min of 7), as form/table, median / worst over the 14 cells:

| regime (n, ppm, span) | swar | sse2 | avx2 | memchr (|S|=1) |
|---|---|---|---|---|
| findall 64K, 0 | 0.38/0.63 | 0.13/0.14 | 0.06/0.06 | 0.03/0.03 |
| findall 64K, 1000 | 0.40/0.63 | 0.13/0.14 | 0.07/0.08 | 0.05/0.05 |
| findall 64K, 20000 | 0.47/0.62 | 0.28/0.31 | 0.28/0.30 | 0.32/0.34 |
| findall 64K, 70000 | 0.71/0.85 | 0.60/0.64 | 0.66/0.68 | 0.67/0.68 |
| **findall 64K, 300000** | **1.03/1.20** | **1.01/1.11** | **1.14/1.24** | **1.17/1.18** |
| findall 64K, 800000 | 0.65/0.76 | 0.63/0.71 | 0.71/0.82 | 0.75/0.80 |
| findall 1M, 0 | 0.38/0.62 | 0.12/0.14 | 0.06/0.06 | 0.04/0.04 |
| findall 1M, 1000 | 0.41/0.64 | 0.14/0.16 | 0.08/0.08 | 0.06/0.06 |
| findall 1M, 20000 | 0.64/0.77 | 0.44/0.47 | 0.24/0.26 | 0.26/0.27 |
| findall 1M, 70000 | 0.89/1.00 | 0.61/0.67 | 0.43/0.47 | 0.44/0.44 |
| percall span 16, 0 | 0.49/0.68 | 0.47/0.54 | 0.56/0.62 | 0.66/0.71 |
| percall span 64, 0 | 0.47/0.64 | 0.21/0.27 | 0.20/0.24 | 0.25/0.25 |
| percall span 16, 20000 | 0.47/0.62 | 0.45/0.51 | 0.54/0.59 | 0.66/0.69 |
| percall span 64, 20000 | 0.39/0.55 | 0.25/0.28 | 0.24/0.25 | 0.34/0.34 |

The bounded memchr cascades `mc2`/`mc3` lose badly from 70k ppm upward
(up to 1.96x and 2.58x). As the r17s leaning said, they stay twins.

## What it says

1. **Every form beats the table everywhere except ONE regime: hit-dense
   find-all at 300k ppm.** There the call-per-hit term dominates.
   - The worst losses are SWAR +20%, avx2 +24% and memchr +18%.
   - The cells losing most are `lc` ([a-z]) and `dig` ([0-9]): the
     bench's own dense CONTROL sites. These are real sites, not synthetic
     ones.
   - At 800k, every form wins again: almost every call returns on its
     first block.
2. **SWAR (the SIMD-off candidate)** has median 0.38-0.89x and wins on
   188 of 196 regime rows. Its 8 losses (>2%) are all at 300k ppm, and 5
   of them are 14-20%.
3. **memchr for the VM hat's |S| = 1** loses only at 300k ppm (bkn/bpr
   +17/+18%) and wins everywhere else. That is the dense VM-hat regime
   Q-R5 measured. r17s predicted it would need N1, and the expectation was
   confirmed.
4. The SIMD layer (sse2/avx2) beats SWAR in most regimes. That is a
   separate decision (D147: the SIMD thread, 2:1). It needs N2 (the
   file-scope sink) as well.

## The consequence for the build

The losses are reproducible and 15-24% on real bench sites, so the
one-pass rule's "accept" arm does not apply. A static form choice
regresses the dense controls. The kit has no density fact today
(`cand_ppm`/`ppm` read unknown), so it cannot tell a dense site from a
sparse one. A static proxy (a range's width, the set's size) is not
density: `[a-z]` is dense on words and sparse on digits.

The leaning is to build the general row with its density admission
reading N1. Until N1 is filled, the row declines on unknown density only
where the site shape is one the 300k regime hurts. That rule is the
design question for the D6 panel. The other option is to wait for N1
before building. Both go to the panel and then to Frank via main.
