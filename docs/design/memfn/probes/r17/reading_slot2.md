# R-17 follow-up: the stateful/adaptive timing reading (2026-10-12, lane r17rd)

## The run

- Run 2026-10-12 03:48:18-05:37:42 on the Linux dev box (7700X Zen 4), core 14,
  SMT sibling idle, gcc 15.2.0, `-O2 -fPIC`, R 7, MIN_MS 50. Quiet box (the
  pcrec manager's gates ended 03:48:04; the first ~3 min were checks).
- Pre-checks: 190 twins, 4,037,733,349 calls, 0 mismatches; planted check
  caught 152/152. Completion line: `rows=9654 void=0 perf=126`.
- Data: `out/slot2/{times.tsv,summary.txt,perf/,check*.txt,run.log}`.
- Every number below is recomputed from `times.tsv` by `analyze_slot2.py`
  (this directory; `python3 -I analyze_slot2.py out/slot2 <section>`), not
  copied from `summary.txt`. Its tables agree with `summary.txt` where they
  overlap (noise band 1.016 reproduced). `summary.txt` pools the 14 real
  cells with the 5 synthetic ones; the tables here use the 14 real cells
  (`adl qdm alt2 alt2r bkn bpr sig tki kel hbr hbrc u8l dig lc`) and read the
  synthetic cells only in answer 5.
- Tier: kit timings are UNOFFICIAL (D144 add. 4).
- Real bench subjects were NOT run (no SUBJ_TSV).

Conventions. A ratio is form/`table`, ns per call, min of 7 ("raw"), as
median/worst over the 14 cells of a regime. Noise band: p95 med/min = 1.016, so
a ratio inside [0.984, 1.016] is a tie. `d_floor` = ns minus the no-read floor
row; raw and `d_floor` never disagree in sign beyond the band on any of the
574 x 13 real-cell rows, but `d_floor` magnifies dense differences (below).
Regime names: `inf`/`k16`/`k4`/`call` = findall with the state reset never / every
16 hits / every 4 hits / every hit (`call` = true matches, today's stateless
API); `clus gN` = geometric runs of mean N; `pc L16/L64` = percall spans.
"Dense" = >= 300k ppm.

## The measurement artifact that conditions every 64K dense verdict

At 64K the same subject is rescanned every sample. `table` at 300k:

| n | ns/byte | ns/call | branch-miss/call (perf, 64K only) |
|---|---|---|---|
| 64K | 0.65 | 2.49 | 0.038 (300k), 0.014 (70k), 0.63 (800k) |
| 1M | 1.91 | 7.36 | not measured |

(dig/lc/bkn/bpr medians.) The 4.9 ns/call gap is about one mispredict per
call. So `table`'s 64K 300k figure is consistent with the predictor having
learned the repeated stream (INFERENCE: no 1M perf pass was taken). It makes
the 64K dense rows the HARDEST case for every form against `table`, and the 1M
rows the cleanest; the truth for a real subject lies between, and which end the
bench is nearer is unknown (the bench also repeats subjects). Hypothesis H5
("table's miss rate peaks 100k-500k") is falsified at 64K: its miss rate
peaks at 800k, and 300k is a trough.

## 1. THE VERDICT QUESTION

findall reset=inf, 64K, 14 real cells, form/table median/worst (raw):

SIMD-off:

| form | 0 | 20k | 70k | 150k | 200k | 300k | 400k | 600k | 800k | 1M |
|---|---|---|---|---|---|---|---|---|---|---|
| swar | .38/.63 | .48/.63 | .80/.93 | .99/1.18 | 1.15/1.31 | 1.25/1.47 | 1.24/1.42 | .62/.75 | .69/.84 | .88/1.08 |
| mask8_swar | .59/.90 | .54/.69 | .69/.84 | .73/.80 | .81/.93 | **.86/.90** | .78/.88 | .38/.44 | .52/.58 | .69/.75 |
| mask64_swar | .68/.83 | .60/.71 | .73/.86 | .78/.90 | .89/1.00 | .98/1.13 | .92/1.00 | .48/.54 | .57/.68 | .74/.87 |
| mask64i_swar | .69/.89 | .60/.71 | .67/.77 | .74/.84 | .89/.95 | .99/1.05 | .91/1.01 | .48/.55 | .55/.63 | .74/.80 |
| ring_swar | .69/.86 | .66/.77 | .91/1.02 | 1.06/1.23 | 1.26/1.40 | 1.40/1.60 | 1.33/1.52 | .64/.78 | .74/.80 | .93/1.11 |
| adapt_swar | .38/.63 | .57/.69 | 1.11/1.17 | 1.15/1.34 | 1.31/1.40 | 2.25/2.50 | 2.38/2.55 | 1.20/1.37 | 1.26/1.41 | 1.34/1.49 |

SIMD-on:

| form | 0 | 20k | 70k | 150k | 200k | 300k | 400k | 600k | 800k | 1M |
|---|---|---|---|---|---|---|---|---|---|---|
| sse2 | .13/.14 | .29/.31 | .66/.73 | .89/1.03 | 1.13/1.19 | 1.27/1.37 | 1.19/1.32 | .59/.69 | .68/.78 | .88/1.01 |
| avx2 | .06/.06 | .30/.31 | .72/.79 | 1.00/1.15 | 1.27/1.30 | 1.41/1.48 | 1.34/1.43 | .66/.76 | .75/.86 | 1.00/1.11 |
| mask64_sse2 | .11/.13 | .22/.24 | .47/.54 | .65/.74 | .77/.84 | **.90/.97** | .86/.94 | .44/.53 | .53/.61 | .70/.78 |
| mask64_avx2 | .05/.06 | .20/.22 | .46/.49 | .61/.67 | .76/.77 | **.88/.89** | .85/.88 | .44/.50 | .52/.57 | .68/.72 |
| ring_avx2 | .07/.08 | .29/.33 | .60/.66 | .89/1.05 | 1.08/1.27 | 1.33/1.44 | 1.23/1.37 | .61/.70 | .72/.80 | .95/1.07 |
| adapt_avx2 | .06/.06 | .42/.43 | 1.11/1.18 | 1.14/1.30 | 1.32/1.40 | 1.86/2.53 | 2.36/2.55 | 1.17/1.33 | 1.23/1.37 | 1.35/1.42 |

1M (reset=inf): swar .38/.63 (0), .92/1.08 (70k), .51/.60 (300k); mask8_swar
.58/.88, 1.05/1.17, .63/.69; **mask64_swar .68/.82, .48/.57, .37/.43**;
mask64_avx2 .06/.06, .35/.36, .33/.35; mask64_sse2 .11/.12, .36/.38, .34/.38;
ring_swar .69/.85, .68/1.04, .56/.60; adapt_swar .38/.63, 1.10/1.15, 1.13/1.24.

The dense controls alone (dig lc bkn bpr) read the same within a few
hundredths (e.g. 300k: mask8_swar .83/.87, mask64_swar .97/.99, mask64_avx2
.86/.88, swar 1.28/1.47, ring_swar 1.42/1.60, adapt_swar 2.25/2.34).

**Answer, by layer (at reset=inf):**

- SIMD-off. YES for `mask8_swar` (beats `table` at every ppm from 70k to 1M
  at 64K, worst cell .93 at 200k, and keeps sparse wins: .59/.90 at 0 ppm,
  .54/.69 at 20k). `mask64_swar` / `mask64i_swar` TIE at 300k (.98/1.13 and
  .99/1.05; the worst cell loses, `u8l` 1.13) and win elsewhere; at 1M they are
  the best SIMD-off forms (.37 / .48 at 300k / 70k). Plain `swar` LOSES at
  150k-400k (1.15-1.31 median, 1.47 worst). `ring_swar` LOSES at 150k-400k
  (1.06-1.40) like `swar` and is slower than it. `adapt_swar` / `adapt_mask`
  LOSE from 70k up (1.04-2.38; answer 4).
- SIMD-on. YES for `mask64_sse2` and `mask64_avx2` (.88-.90 at 300k, worst
  cell .89-.97; sparse .05-.22). Plain `sse2`/`avx2` lose 150k-400k (up to
  1.48), `ring_avx2` loses (1.33 at 300k), `adapt_avx2` loses (1.86).
- D147 check (SIMD must beat the best SIMD-off form per row): `mask64_avx2`
  loses to the best SIMD-off form (always `mask8_swar` or a mask64 SWAR form)
  on 51 reset=inf rows, ALL at 64K and >= 300k ppm (worst 1.28, `bpr` 600k),
  none at 1M or <= 200k. `mask64_sse2`: 70 such rows at 64K, 6 at 1M. So at
  64K dense the SIMD arm is not strictly better than the SWAR mask8 arm; at
  1M and below 300k it is, by 2-6x.
- Over ALL measured rows (574 real-cell rows per form) the verdict is NOT a
  clean win for anyone: rows losing beyond the band, rows > 1.5, worst row:

| form | losing / 574 | > 1.5 | worst row |
|---|---|---|---|
| swar | 179 | 25 | 1.94 (adl 300k inf) |
| mask8_swar | 127 | 26 | 1.87 (adl pc L64 800k) |
| mask64_swar | 206 | 139 | 7.24 (adl pc L16 800k) |
| mask64i_swar | 211 | 138 | 7.13 |
| ring_swar | 286 | 187 | 43.2 (adl call 300k) |
| adapt_swar | 401 | 77 | 2.55 |
| adapt_mask | 447 | 184 | 7.65 |
| sse2 | 142 | 15 | 1.74 |
| avx2 | 173 | 29 | 1.93 |
| mask64_sse2 | 132 | 39 | 2.21 |
| mask64_avx2 | 118 | 26 | 2.05 (adl call 300k) |
| ring_avx2 | 231 | 159 | 28.4 |
| adapt_avx2 | 393 | 65 | 2.59 |

By K-1 ("no loss beyond the band in any row") NO form is a candidate (the
summary's own `CANDIDATE` column is empty for the same reason). The rows that
make every form lose are in answer 7.

d_floor view (the driver's cost removed; `table` 300k is only 0.58 ns above a
1.83 ns floor, so ratios inflate): at 64K inf 300k swar 2.04/2.95,
mask8_swar .47/.57, mask64_swar .91/1.54, ring_swar 2.67/3.48, mask64_avx2
.52/.70, avx2 2.69/3.00. Same ordering as raw; `mask64_avx2` goes NEGATIVE
(-0.06 ns net) at 70k, i.e. a form can finish below the "no-read floor", so
the floor is not a strict lower bound (the driver overlaps it). Raw stays the
verdict basis, as pre-registered.

## 2. THE STATE-RESET AXIS (64K, 300k ppm, 14 real cells, median/worst)

| form | inf | k16 | k4 | call |
|---|---|---|---|---|
| swar (stateless) | 1.25/1.47 | 1.19/1.48 | 1.22/1.47 | 1.24/1.48 |
| mask8_swar | .86/.90 | .97/1.24 | .98/1.19 | 1.65/1.83 |
| mask64_swar | .98/1.13 | 1.07/1.19 | 1.42/1.72 | 3.98/5.43 |
| mask64i_swar | .99/1.05 | 1.06/1.23 | 1.37/1.67 | 3.98/5.40 |
| ring_swar | 1.40/1.60 | 2.37/2.94 | 9.44/10.86 | 35.6/43.2 |
| adapt_swar | 2.25/2.50 | 2.08/2.55 | 1.38/1.52 | 1.37/1.59 |
| avx2 (stateless) | 1.41/1.48 | 1.32/1.48 | 1.40/1.48 | 1.40/1.49 |
| mask64_sse2 | .90/.97 | .96/1.13 | 1.00/1.10 | 1.88/2.21 |
| mask64_avx2 | .88/.89 | .95/1.06 | .96/1.06 | 1.81/2.05 |
| ring_avx2 | 1.33/1.44 | 2.06/2.30 | 7.58/7.88 | 27.7/28.4 |
| adapt_avx2 | 1.86/2.53 | 1.65/2.59 | 1.31/1.42 | 1.53/1.70 |

Absolute ns/call at 300k, median over cells (table 2.4 at every reset):

| form | inf | k16 | k4 | call | call minus inf |
|---|---|---|---|---|---|
| swar | 3.2 | 3.2 | 3.2 | 3.2 | 0 |
| mask8_swar | 2.1 | 2.4 | 2.6 | 4.1 | +2.0 |
| mask64_swar | 2.4 | 2.8 | 3.9 | 10.9 | +8.5 |
| mask64_avx2 | 2.1 | 2.4 | 2.5 | 4.5 | +2.4 |
| ring_swar | 3.5 | 6.6 | 25.7 | 93.5 | +90 |
| ring_avx2 | 3.2 | 5.2 | 18.6 | 67.3 | +64 |

And `call` at lower density (form/table, median/worst): 20k mask8_swar .65/.84,
mask64_swar 1.02/1.28, ring_swar 2.60/3.34, mask64_avx2 .35/.40; 70k mask8
.97/1.17, mask64_swar 2.05/2.72, ring_swar 10.7/13.6, mask64_avx2 .93/1.04;
800k mask8 .94/1.07, mask64_swar 2.39/2.73, mask64_avx2 1.03/1.13.

- The state's benefit over the STATELESS form exists only with re-entry.
  At 300k mask64_swar/swar = .78 (inf), .90 (k16), 1.16 (k4), 3.2 (call): break
  even near 8-16 candidates per state lifetime. mask8_swar/swar = .69, .82,
  .80, 1.33: break even near 2-3 candidates. mask64_avx2/avx2 = .62, .72, .69,
  1.29. Ring never breaks even against its own stateless form after k16.
- Cost of reset=1 (find-all with true matches, today's API) is the REFILL, paid
  once per call: mask64_swar +8.5 ns, mask64_avx2 +2.4, mask8_swar +2.0, ring
  +64-90 (it fills 256 bytes and drains every member in them, ~77 positions at
  300k, to use one).
- Safest across all resets: stateless `swar`/`avx2` are flat (swar 1.24 at every
  reset), but lose 25% / 40% at 300k even at inf. Among stateful forms,
  `mask8_swar` (worst reset=call 1.65 at 300k, .65-.97 at 20-70k) and
  `mask64_avx2` / `mask64_sse2` (1.81 / 1.88 at 300k call, .35 at 20k call) are
  the safest; `mask64_swar` (3.98 at call, 7.2 worst row) and the rings (36x)
  are not.

## 3. MASK VERSUS RING

ring/mask ratio (ns), median/worst:

| regime | swar pair (ring_swar/mask64_swar) | avx2 pair (ring_avx2/mask64_avx2) |
|---|---|---|
| inf 64K 0 | 1.02/1.10 | 1.24/1.40 |
| inf 64K 20k | 1.11/1.17 | 1.44/1.55 |
| inf 64K 70k | 1.26/1.32 | 1.36/1.51 |
| inf 64K 300k | 1.45/1.62 | 1.54/1.68 |
| inf 64K 800k | 1.34/1.60 | 1.40/1.54 |
| inf 1M 70k | 1.38/2.43 | 1.47/3.70 |
| inf 1M 300k | 1.53/1.68 | 1.58/1.70 |
| clus g2 / g32 | 1.33/1.61, 1.34/1.56 | 1.46/1.66, 1.50/1.68 |
| k16 300k | 2.27/2.52 | 2.14/2.23 |
| k4 300k | 6.61/7.29 | 7.60/8.21 |
| call 20k / 300k | 2.53/2.62, 8.70/11.5 | 1.80/1.91, 14.8/16.2 |
| pc L16 | 0.56/1.15 | 2.03/3.32 |
| pc L64 | 1.39/4.66 | 2.84/11.8 |

- The ring loses to the mask in every measured regime except one: SWAR
  percall L16 (median .56). That is an artifact of the mask64 SWAR shape at
  hi < 64 (its tail path runs words then bytes: mask64_swar costs 11.4 ns at
  L16 0 ppm against swar 2.5), not a ring win; at the avx2 pair the ring loses
  there too (2.03).
- H3's exception ("ring wins at 1M 20-70k") is falsified: ring/mask is 1.38-1.47
  at 1M 70k. The ring does not win anywhere; it ties at 0 ppm SWAR (1.02).
- WHY (perf, 64K, floor subtracted, median over cells):

| ppm | branches/call: table / swar / mask64_swar / ring_swar / mask64_avx2 | branch-miss/call: table / swar / mask64_swar / ring_swar / adapt_swar / mask64_avx2 |
|---|---|---|
| 70k | 28.6 / 5.7 / 7.1 / 13.7 / 4.7 | .014 / .008 / .003 / .004 / .019 / .003 |
| 300k | 6.7 / 3.2 / 5.5 / 11.7 / 4.2 | .038 / .001 / .022 / .040 / .629 / .016 |
| 800k | 2.6 / 3.0 / 5.2 / 11.3 / 4.1 | .627 / .002 / .028 / .023 / .682 / .028 |

  The ring executes about twice the branches of the mask (11.3-13.7 vs
  5.2-7.1 per call) because the drain loop touches every member of a 256-byte
  fill; its mispredict count is NOT worse than the mask's at 70k / 800k (.004 /
  .023 vs .003 / .028) and is worse at 300k (.040 vs .022). So the ring's loss
  is instruction count and wasted drain work (positions drained that are
  never asked for: the k4/call blowup of 6-15x), not mispredicts. Only branch
  counts were taken, not instructions or cycles: "instruction count" is the
  inference from branches/call and the call-regime scaling.
- Mask W: `mask8_swar` is 0.82-0.95 of `mask64_swar` at 64K inf, wins the
  reset axis (call .40, k4 .71) and percall (L16 .32, L64 300k .28), and LOSES
  at 1M: 2.18 (70k), 1.74 (300k), .87 (0 ppm). Why mask64 wins at 1M: the same
  per-8-byte branch that is learned at 64K is not at 1M (see the artifact
  section). W is therefore not decided by a single regime (answer 7).

## 4. THE ADAPTIVE SWITCH

Constants as shipped in the twins (GAP 8, BLOCK0 16, CAP 1024; untuned
defaults, and the `-D` overrides were not swept, so no threshold can be read
off this run).

form / (fixed form or table), median/worst:

| ratio | inf 0 | inf 20k | inf 70k | inf 150k | inf 300k | inf 800k | call 300k | pc L16 | pc L64 |
|---|---|---|---|---|---|---|---|---|---|
| adapt_swar/swar | 1.00/1.01 | 1.18/1.30 | 1.45/1.76 | 1.20/1.41 | 1.69/2.16 | 1.83/2.07 | 1.08/1.11 | 1.25/1.47 | 1.17/1.46 |
| adapt_swar/table | .38/.63 | .57/.69 | 1.11/1.17 | 1.15/1.34 | 2.25/2.50 | 1.26/1.41 | 1.37/1.59 | .95/1.84 | .90/1.85 |
| adapt_avx2/avx2 | 1.00/1.00 | 1.43/1.49 | 1.53/1.61 | 1.14/1.18 | 1.33/1.80 | 1.62/1.72 | 1.10/1.15 | 1.09/1.55 | 1.15/1.43 |
| adapt_mask/mask64_swar | 1.00/1.01 | 1.13/1.34 | 1.43/1.83 | 1.40/1.60 | 2.37/2.61 | 2.27/2.46 | 1.05/1.11 | 1.04/1.15 | 1.05/1.13 |

- It does not pay. It beats the better of (table, its fast form) beyond the band
  in 9 / 4 / 4 of 574 rows (adapt_swar / adapt_avx2 / adapt_mask), best 0.95;
  it loses beyond the band in 401 / 393 / 447.
- H4 ("adapt_swar ties table at >= 300k") is falsified at 64K: 2.25 at 300k,
  2.38 at 400k. Cause visible in perf: 0.63 branch-miss/call against table's
  0.038 at 300k (and 10.7 branches/call against 6.7). The mode-dependent
  walk/fast branch is itself unpredictable and the walk loop loses the
  pattern `table` had learned. At 1M, where `table` mispredicts anyway, the
  switch costs about 13% (adapt_swar 1.13, adapt_mask 1.10, adapt_avx2 1.12 at
  300k).
- It also costs sparse wins. adapt_swar/swar is 1.18 at 20k and 1.45 at 70k, so
  at 70k it gives up swar's .80 for 1.11. Behaviour behind that (inference from
  the constants, not isolated by a sweep): the arm rule fires on two successive
  skips shorter than GAP = 8; at 20k-70k such pairs are common enough, and each
  arm walks 16 calls (mean gap 14 bytes at 70k, 50 at 20k) at the byte-walk's
  speed, several times slower per byte than the fast form.
- Under reset the switch resets with the state, so `call`/`k4` rows show only
  its bookkeeping (adapt_swar/swar 1.08 at call 300k, 1.05 at call 20k).
- Verdict: a fixed stateful form beats the adaptive switch in every regime
  where adaptivity could matter. `adapt_*` is not built (D77), unless a sweep of
  GAP/BLOCK0/CAP (not run) changes this, which nothing here suggests.

## 5. K, THE TERM COUNT (synthetic cells, form/table, single cell)

`table` is the same loop in all four. Rows: findall inf 64K (fa) at 0, 20k, 70k,
300k, 800k ppm; percall (pc) L16 / L64 at 0 and 300k.

| cell | best SIMD-off form per row; "-" = worst loss |
|---|---|
| syn4 | fa0 .81 swar; fa20k .77 swar; fa70k .86 mask64; fa300k 1.03 (mask8/mask64; tie-loss); fa800k .45 mask64; pc L16 0 .85 swar; pc L16 300k **1.25**; pc L64 0 .79; pc L64 300k **1.31** |
| syn5 | fa0 **1.04** swar; fa20k .91 swar; fa70k .89 mask64; fa300k .83 mask64i; fa800k .57; pc L16 0 1.01 (tie); pc L16 300k **1.41**; pc L64 0 .96; pc L64 300k **1.50** |
| syn6 | fa0 **1.25**; fa20k 1.06; fa70k **1.11**; fa300k **1.13**; fa800k .62; pc L16 0 **1.09**; pc L16 300k **1.55**; pc L64 0 **1.14**; pc L64 300k **1.65** |
| syn8 | fa0 .85 mask8; fa20k .75; fa70k .76; fa300k .97 mask8; fa800k .61; pc L16 0 .82; pc L16 300k **1.31**; pc L64 0 .80; pc L64 300k **1.40** |

- K = 4 is the largest count whose best SIMD-off form wins every SPARSE regime
  (0, 20k, 70k findall; percall at 0 ppm): margins .77-.86 (0.81 swar at 0 ppm,
  .77 at 20k, .86 mask64 at 70k, .85 / .79 at L16 / L64). At K = 5 the 0-ppm
  scan ties-to-loses (1.04, percall L16 1.01) and K = 6 loses sparse outright
  (1.25 at 0 ppm, 1.09-1.14 percall). Plain `swar` at K = 4 alone loses at 70k
  (1.05) and 300k (1.54); the margin at 70k needs the state.
- No count wins in EVERY measured regime, including K = 4 (percall 300k 1.25 /
  1.31) and, for that matter, the real 1-3 term cells (swar L64 300k 1.02/1.26):
  dense percall is table's regime (the first byte hits). Excluding percall
  dense, K = 4 misses only fa300k (1.03, a tie-loss), K = 5 misses only fa0
  (1.04), K = 6 misses sparse.
- ANOMALY: K = 8 is better than K = 6. syn8 `mask8_swar`/`mask64_swar` run at
  0.158 / 0.166 ns/byte at 0 ppm against 0.268 / 0.267 for syn6 and 0.181 /
  0.184 for syn4, while syn8 `swar` is the slowest (0.311). Same `table` time
  (0.185). Unexplained: probably gcc 15.2 -O2 code generation for that
  8-member shape (not verified; no objdump was taken on this slot). So the
  K = 8 wins are real for THIS compiler and member set and must not be read as
  "8 terms are fine"; the disassembly check the design owes is exactly this.
- The stateless-vs-mask difference at high K is large and is the only reason K
  > 4 is not dead: syn6 at fa300k swar 1.88 / mask8 1.23 / mask64i 1.13.

## 6. PERCALL SHORT SPANS

form / table, median/worst (14 real cells):

| form | L16 0 | L16 20k | L16 300k | L16 800k | L64 0 | L64 300k | L64 odd 0 | L64 odd 300k |
|---|---|---|---|---|---|---|---|---|
| swar | .50/.69 | .49/.62 | .96/1.20 | 1.20/1.52 | .47/.62 | 1.02/1.26 | .47/.63 | 1.01/1.27 |
| mask8_swar | .70/.90 | .65/.81 | 1.23/1.46 | 1.50/1.85 | .59/.78 | 1.30/1.54 | .59/.78 | 1.30/1.55 |
| mask64_swar | **2.21/2.73** | 2.13/2.58 | 4.78/5.61 | 6.00/7.24 | .69/.83 | 4.76/5.53 | .69/.83 | 4.76/5.57 |
| ring_swar | .99/1.35 | .95/1.27 | 2.70/3.32 | 4.49/5.27 | .71/.88 | 8.06/8.99 | .71/.88 | 8.08/9.03 |
| adapt_swar | .62/.84 | .58/.77 | 1.21/1.44 | 1.53/1.84 | .46/.66 | 1.27/1.52 | .46/.66 | 1.31/2.06 |
| sse2 | .49/.65 | .46/.55 | .88/.97 | 1.10/1.22 | .23/.28 | 1.00/1.09 | .23/.28 | 1.00/1.09 |
| avx2 | .64/.72 | .58/.64 | 1.11/1.25 | 1.40/1.49 | .21/.23 | .89/.97 | .21/.23 | .89/.97 |
| mask64_sse2 | .64/.77 | .61/.72 | 1.41/1.67 | 1.74/2.12 | .19/.22 | 1.25/1.47 | .18/.22 | 1.25/1.48 |
| mask64_avx2 | .58/.66 | .59/.66 | 1.28/1.37 | 1.62/1.73 | .17/.19 | 1.08/1.24 | .17/.19 | 1.08/1.24 |
| ring_avx2 | .95/1.33 | .95/1.28 | 2.81/3.38 | 4.65/5.36 | .22/.23 | 5.08/5.21 | .22/.23 | 5.09/5.30 |

- Absolute ns, L16 at 0 ppm: floor 1.13, table 4.93, swar 2.49, mask8_swar
  3.63, **mask64_swar 11.40**, ring_swar 4.95, adapt_swar 3.21; mask64_sse2
  3.22, mask64_avx2 3.03, avx2 3.18, sse2 2.44. At L64: mask64_swar 10.5
  (L64 0 ppm .69 of table 15.3), SIMD mask64 2.65-2.85.
- Who loses and why: `mask64_swar` / `mask64i_swar` / `adapt_mask` lose 2.1-2.7x
  at L16 sparse, because hi < 64 sends the refill down the tail path (whole
  words, then single bytes), a fixed ~9 ns (the "init cost") on a table walk that
  costs 4.9. At L64 sparse the same form wins (.69). `ring_*` pay the
  256-byte-fill machinery per call (L64 300k 8.06 / 5.08; 800k 17.9 / 14.6).
  `mask8_swar` pays one word-pack + store (+1.1 ns at L16 sparse: .70 against
  swar .50; still a win). All SIMD mask forms win sparse L16 (.58-.64) but are
  beaten by plain `sse2` / `avx2` (.46-.64) and tie-lose dense.
- At dense percall (>= 300k, hit within ~3 bytes of lo) every SWAR form ties
  or loses; only `sse2`/`avx2` tie-or-win at L64 300k (.89-1.00).
- Odd (misaligned) L64 equals aligned L64 within noise for every form.

## 7. RECOMMENDATION per width (the body behind `next_candidate(&state, lo)`)

**No single form holds in every measured regime (K-1 fails for all 13).** Regimes
where `table` beats EVERY SIMD-off form on a majority of cells (counted per
14-cell group; "best-off" = the oracle best SIMD-off per row):

| regime (64K unless noted) | rows where table beats all SIMD-off forms | best-off median/worst | SIMD-on (all forms) |
|---|---|---|---|
| findall call 300-400k | 14 / 14 | 1.24/1.48 | still 14 / 14 lose |
| clustered g32, 300k | 12 / 14 | 1.08/1.17 | 11 / 14 lose |
| clustered g8, 300k | 5 / 14 | .96/1.11 | 5 / 14 |
| k4 / k16 300k | 6 / 4 of 14 | .98/1.19, .97/1.17 | 3 / 3 |
| percall L64 (and odd) 300k | 7 / 14 | 1.02/1.26 | 0 / 14 (avx2 .89 wins) |
| percall L16 300k | 2 / 14 | .96/1.20 | 0 |
| percall L16 / L64 800k | 14 / 14 each | 1.20/1.53, 1.22/1.53 | 10 / 14, 7 / 14 lose |

Everything else is a win for the best form of the layer: all inf, 1M, clus g2,
call at <= 70k and >= 500k, percall sparse.

The minimal set where no SIMD-off single form holds: (a) hit-per-candidate with
the state lost, at >= ~300k ppm (call, k4); (b) percall dense (>= 300k, spans
16/64); (c) clustered runs >= 8 at 300k. All three are "the hit is within a few
bytes AND the state does not carry". None is lost at reset=inf (state carried)
at 1M.

Recommended implementation per width (loss bounded by the measured worst rows):

| width | recommended body | why | residual loss |
|---|---|---|---|
| SWAR (w8) | `mask8_swar` | 444 / 574 wins, 127 losses, worst row 1.87 (swar: 374 / 179 / 1.94); wins the whole reset=inf 64K column (.86 at 300k), halves mask64's reset cost (call 1.65 vs 3.98); no L16 init cliff (.70) | call 300k 1.65; percall dense 1.3-1.9; 1M 70k 1.05 (vs mask64 .48); sparse 1.5x slower than `swar` (0 ppm .59 vs .38 of table) |
| SWAR where reset=inf is GUARANTEED and spans >= 64 | `mask64_swar` instead | wins 1M (.37 / .48), best at 300k inf for the unmemorized case | 4-7x on call and L16: unsafe without the guarantee |
| SSE2 (w16) | `mask64_sse2` | 434 / 574 wins, 132 losses, worst 2.21 (call 300k); inf .47 at 70k, L16 sparse .64 | call 300k 1.88; percall dense 1.25-1.74; at 64K >= 300k it is up to 1.28 slower than mask8_swar (D147) |
| AVX2 (w32) | `mask64_avx2` | 446 wins, 118 losses (fewest of all), worst 2.05; inf .88 at 300k, 1M .33 | call 300k 1.81; percall dense L16 1.28-1.62; D147 loss vs mask8_swar at 64K dense (1.1-1.28) |

Never `ring_*` (worse than its mask twin everywhere but one artifact, answer 3)
and never `adapt_*` (answer 4). `mask64i_swar` (refill as a call) equals
`mask64_swar` within noise at every regime in answer 1 (.99 vs .98 at 300k,
.67 vs .73 at 70k, 3.98 vs 3.98 call): the composable-pieces shape costs
nothing measurable, so the body may be written as primitives (D155 add. 4).

An untested form the numbers point at (NOT measured, for the next round if the
sparse loss matters): mask8 packs a mask even for empty words; `swar` is 1.5x
faster at sparse. A "stateless test first, pack on a nonzero word" body would
keep swar's .38 and mask8's re-entry. This is a hypothesis, to be written as a
twin before it is claimed.

**What each residual regime needs that the kit lacks today:**

| regime | needs | where it comes from |
|---|---|---|
| reset = how often the state survives (inf vs k4 vs call) | cross-call state in the caller's struct | [FINDALL-NEXT]; without it every find-all site runs at call/k(false candidates per match) and the mask forms' benefit is only the within-call false-candidate re-entry |
| density >= ~300k with state lost | density facts: `cand_ppm`/`freq` (the D162 analysis object) | analysis object kinds; absent => decide without |
| percall vs findall site (a call that starts at a fresh `lo` and ends at the first hit) | call pattern (one-shot search vs loop consumer) and span-length class | analysis object "length class and call pattern" kinds / the site kind pcrec already knows |
| clustered runs | run-length profile | analysis object (not available per site; mean run is a subject property) |

**What the fallback density gate (§9.2) would still be for.** With
`mask8_swar` / `mask64_{sse2,avx2}` the worst rows are 1.87-2.21 and the loss
rows are the (a)-(c) regimes, so the gate's value is bounded by ~2x on those
regimes (versus the 4-7x it would have protected `mask64_swar` from). Total
without data (Frank: decisions without data): ADMIT when facts are absent
(D_ABSENT does not decline), because the measured regret of the recommended
forms is <= ~2x on the dense/state-lost corner and a win of 2-17x elsewhere;
decline (walk) only on positive evidence of density >= ~300k AND a non-inf
call pattern. T_SPARSE = 70k is not what the data fixes: the dense edge is at
150k-400k only for the stateless forms; the stateful ones cross 1.0 only at the
reset/pattern corner, not at a density. This reverses §9.2's D_ABSENT-declines
rule on the evidence; it is a recommendation to the manager, and rests on the
unmeasured real-subject mix and the 64K-memorization caveat (a lower table
cost makes the 64K dense numbers the pessimistic end for the forms).

## 8. Regimes NOT measured that the sites can be in

- REAL SUBJECTS (no SUBJ_TSV): C2-2's real-subject question stays OPEN (the
  `ppm_meas` / `run_mean` columns are all 0). Everything is i.i.d. or
  geometric-cluster synthetic text.
- 1M (and larger, DRAM-resident) subjects beyond reset=inf findall: no 1M
  clustered, no 1M reset=k/call, no 1M percall; no 4M+ (1M is about the
  per-core L2 of this CPU). No perf pass at 1M, so the memorization inference
  stands untested.
- A subject that is NOT rescanned, or interleaved with a consumer's work
  between calls (the driver is a bare loop; a real consumer pollutes the
  predictor and caches), and cold-cache first-touch.
- reset = K other than inf/16/4/1, and a state lifetime that varies WITHIN a
  subject (real find-all: false candidates per true match is a distribution).
- The state in the caller's struct across a call boundary (the twins keep it in
  a file-scope/local `sstate` the compiler can see; a state behind a pointer
  from a non-inlined caller pays loads/stores the twins may have optimized
  away). Not checked on disassembly.
- Percall spans other than 16/64 (32, 48, 128-4K); hi != n (end_back > 0);
  lo near hi.
- Set shapes: only the 14 cells + 5 synthetic; |S| > 3 only as synthetic
  one-byte terms; no case-folded multi-range sets of several terms with ranges.
- The adaptive constants (GAP, BLOCK0, CAP) were measured at one setting each.
- Other hardware (Zen 1 ubuntubudu, the Mac/NEON, AVX-512 stays unfiled), other
  compilers (clang), -O3/-march, non-PIC, and the SIMD-on gating cost (ifunc /
  dispatch) of a width pick at run time.
- The disassembly check (no call in an inlined `__find` hot loop; the syn8
  anomaly) is still owed; no objdump read was done for this reading.
- Multi-site functions sharing one predictor; several finds in flight.

## Checks on this reading

- Noise band reproduced: 1.016 over 9,654 rows; void 0; check and planted
  check lines taken from `check.txt` / `run.log`.
- `analyze_slot2.py` section outputs were produced by running it over the
  committed TSVs (no compile, no timing). Section list: verdict, reset,
  mask_ring, adapt, k, percall, losers, perf, all. A few tables above (the
  best-off group table, the D147 count, the 64K-vs-1M table ns/byte, the
  adapt-wins count, the syn ns/byte) were computed with one-off snippets of the
  same helpers and are not separate sections.
- Raw vs `d_floor` sign disagreements beyond the band: 0 on the real cells.
