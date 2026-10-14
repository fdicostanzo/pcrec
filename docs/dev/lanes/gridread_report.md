# gridread — the reading of the grid1 joint timing slot (costmodel §F F1/F3)

Lane gridread, 2026-10-13, branch `lane/memfn-gridread` (cut from the kit branch
`lane/memfn-r17`). ANALYSIS ONLY: no timing, no build, no `make`. Every ns is read
from the finished slot in `worktrees/memfn-slot/grid1/`. That slot ran 2026-10-13
19:33-20:56 EDT on the Zen 4 dev box (7700X), on CPU 14, with 5 launches, an A/A pair
per group, governor `performance`. F2 was skipped (perf denied). Every count comes
from the slot's no-clock counting pass (`counts.tsv`).

- Script: `docs/dev/lanes/gridread/gridread.py`.
- Run: `python3 -I gridread.py OUT > analysis.txt`. `--check OUT` verifies the 14 input
  checksums in `gridread/SHA256SUMS` (it last read 14 inputs, 0 mismatched).
- Citations of the form "an. 4.2" point into `gridread/analysis.txt`.

Labels used:
- **MEASURED**: read straight from a row or a counter.
- **FITTED**: a least-squares or interpolation result.
- **INTERPRETATION**: my inference. These are listed together at the end.

Box and tier: Zen 4, gcc 15.2 -O2, kit tier, UNOFFICIAL (D144 addendum 4).

## Summary

1. **Noise.** The quiet gate held. Load1 was at most 1.20, and the timed process itself
   accounts for 1.0. No group waited, and every launch printed the same answer.
   - The A/A floor over the 141 F1 groups: median 0.20% of the walk, p90 3.37%, max 43%.
   - The noise is the WALK's. It spreads more than 5% across launches in 45 of the 141
     groups; the forms do so in 3-12.
   - The walk is bimodal on the repeated u-shape groups at g = 8-64. For example, dig
     g16 L64k read 19.2k, 19.2k, 19.2k, 27.4k, 27.8k ns across the launches.
   - NULL rule used everywhere: |Δ| ≤ max(A/A, 3.09% of the base), the grid's own p90,
     or the five launch-paired deltas disagree in sign. It moves 65 log verdicts, all
     to NULL.
2. **Re-fit.** Each arm's absolute cost per cell is FITTED:
   `T = F·A + w·(U−A) + p·U[unpredictable fresh] + q·U[repeated u] + β·bytes`.
   The median relative residual is 1-6%. The walk's terms:
   - per landing: 1.4-1.9 ns (costmodel 3.42);
   - per **unpredictable fresh** landing: +4.3 (dig), +5.3 (dfa-hat), +2.0 (bounded) ns.

   Against costmodel:
   - β per byte at 1 term: CONFIRMED (walk 0.189, V1 0.108, S1 0.0205, A1 0.0106).
   - β at 3 terms: REFUTED as a linear extrapolation. Measured V1 0.214 / S1 0.042 /
     A1 0.019, against costmodel's derived 0.168 / 0.021 / 0.010.
   - c_warm (unkept forms): CONFIRMED, +0.4 to +1.0 ns.
   - c_cold: MOVED. It is +2.3 to +2.9 ns for EVERY form; width does not triple it. A
     W=64 cold activation adds 52-54 B of overscan (CONFIRMED against 59 B), worth
     about 1 ns.
   - m_fresh: REFUTED as defined (see item 5).
   - κ (kept forms): REFUTED, 1.00 against 1.22-1.32.
   - regimefacts' SIMD F = 10-20 ns: REFUTED as a per-call cost. At n ≥ 64, a single
     call's fixed part is 4.7-5.0 ns for walk, S1 and A1 alike. The 10-20 ns was the
     sub-block tail at n = 40.
3. **Out of sample.** costmodel's estimator agrees on sign in DINGHY 81%, TUG 78% and
   LINER 99% of rows. Its absolute share explained (absExp) is −0.04..0.48 in DINGHY,
   −0.38..−0.02 in TUG and 0.31..0.85 in LINER. Two kinds of miss dominate:
   - its fresh term fires on predictable streamed rows (−35 µs predicted, +0.6..+1.4 µs
     measured);
   - the dense dfa-hat rows (−40 µs measured, +8 µs predicted).
4. **Crossovers, measured.** W=64 is the SSE2 and AVX2 width.
   - **g\* on repeated data:** W=64 4.2-4.7 B (costmodel 3.8-4.7, CONFIRMED). V1 11-17 B
     on dig (costmodel 15.6, CONFIRMED) and 21 B on bounded. Kept A3 4.6-5.3 B.
   - **g\* with every buffer fresh and gaps irregular:** 2-4 B for the stateful forms
     (stateless 6-7 B).
   - **g\* with the state lost (L = 32):** A1 13.6 B, A3 11.2 B (costmodel 28 B).
   - **L\* (call span), W=64:** between 8 and 32 B, FITTED c_cold/Δβ = 16-17 B. A single
     member-free call crosses at about 18-20 B (interpolated). costmodel's per-form
     19-39 B is CONFIRMED; its L\* = 64 B is conservative. regimefacts' ~1 KB n\* is a
     different quantity: the span where a SIMD form is half fixed cost. It MOVES to about
     230-470 B once F is the 4.7-5.0 ns measured here; it is not the pay-off span.
   - **L\*, SWAR:** 45-100 B.
   - **Block straddle:** at n = 48 and 63, S1 loses +11.6 / +15.8 ns per call and A1
     +1.3 / +5.8. At n = 64 and 65 every W=64 form wins by 9-11 ns. V1 wins at every
     length.
5. **Regimes.** The two facts are right: L per activation and g per landing.
   - The boundaries move with width and with predictability.
   - For W=64 the best boundary is L ≥ 8-32 and g ≥ 4. costmodel's 64 / 18.5 makes
     32-38 errors per form there, against 7-8 for the best split.
   - For SWAR, 64 / 18.5 is about right (12 errors against 10).
   - **The fresh-data effect is real and is the predictor, not the cache.** On streamed
     irregular buffers the walk runs 2.0-2.7x slower at g = 8, which is 4-7 ns per
     landing. Streamed reg/burst buffers with the same bytes, but landing offsets that
     repeat, run within 1% of repeated. Forms lose almost nothing. So losses are a
     density matter of LANDINGS, priced by how PREDICTABLE they are.
6. **Decision.**
   - With SIMD on, the gap and span facts together regret 0.0-0.1% in sample. Refitted
     without the row's g they regret 1.0 / 1.1 / 0.0%.
   - A regime hint (walk / A1 / A1) regrets 9.1 / 1.2 / 0.0%. Always-A1 regrets 11.1%
     in DINGHY.
   - With SIMD off, the hint (walk / walk / V1) regrets 2.4 / 6.4 / 0.1%. The gap model
     gets 0.4% in TUG in sample, but 14% out of sample: the SWAR TUG call is fragile.
   - With the iterator, always-A3 regrets 5.6 / 11.3 / 1.7%.
7. **Rules (§E).**
   - CONFIRMED: D1, T2, L1, L2, X2.
   - AMENDED: R0's boundaries, D2, D4, D5, T1, L3, X1.
   - CONFIRMED in direction: D3.
   - UNTESTED here: T3.
   - The full table is §6.

## 1. Regime and noise (an. 1)

### 1.1 The A/A floor

| phase | groups | A/A median | A/A p90 | A/A max | per-launch A/A p90 | base spread p90 |
|---|---|---|---|---|---|---|
| F1 | 141 | 0.195% | 3.37% | 43.3% | 6.96% | 12.2% |
| F3 | 8 | 0.062% | 0.17% | 0.27% | 0.49% | 0.63% |
| EXT | 24 | 0.025% | 0.38% | 1.91% | 1.26% | 2.68% |

- **The noise is the walk's** (MEASURED, an. 1):
  - The walk's per-launch spread exceeds 5% in 45 of 141 F1 groups. V1 does so in 3,
    S1 in 12, A1 in 11, kept forms in 4-9, and stateless forms in 7-8.
  - Most of the 55 unstable groups (A/A > 1% or spread > 5%) are 64 KiB find-all groups
    with u-shaped landings at g = 4-64. The rest are the 48-128 B subjects (relative
    noise on 20-75 ns) and a few g = 2 and burst groups.
- **The walk is BIMODAL across launches** on those groups (an. 6.2b):
  - dig g16 L64k: 19,262 / 19,226 / 19,177 / 27,440 / 27,771 ns.
  - dfa-hat g16 L64k: 21,074 .. 32,737 ns.
  - INTERPRETATION: the branch predictor either learns the repeated 64 KiB gap pattern
    or does not, per launch. See §5.1 for the controlled evidence.

### 1.2 The NULL rule

A row is NULL when |Δ| ≤ max(A/A floor, FRG · base), where FRG = 3.09% is the grid's own
p90 A/A. A row is also NULL when the five launch-paired deltas (arm − base in the same
round) do not all share a sign.

| rule | W | R | N |
|---|---|---|---|
| time.sh's (|Δ| ≤ A/A) | 536 | 420 | 27 |
| costmodel's strict (max(A/A, 2.3%)) | 525 | 391 | 67 |
| this reading | 515 | 376 | 92 |

This reading's rule moves 65 rows, every one of them to NULL. The largest is bounded g2
L8-S S3, +12.3 µs, whose launches disagree in sign.

### 1.3 The quiet gate held (MEASURED)

| phase | launches | load1 min | load1 median | load1 max | > 1.5 | groups that waited |
|---|---|---|---|---|---|---|
| F1 | 6,325 | 0.92 | 1.01 | 1.20 | 0 | 0 of 141 |
| F3 | 400 | | | 1.08 | 0 | 0 |
| EXT | 400 | | | 1.16 | 0 | 0 |

- The baseline of 1.0 is the timed process itself.
- Every group's launches printed one answer line (0 disagreements).
- `slot.status`: CHECK_OK with 6,319 legs OK and 0 FAIL, and plants 14 of 14 detected
  (`plants.log`).

## 2. The re-fit on controlled data (an. 2)

### 2.1 β per byte (F3, MEASURED)

β is the slope between the 64 KiB and 1 MiB member-free single calls.

| arm | 1 term `[0-9]` | 2 terms `[a-f0-9]` | 3 terms `[A-Za-z_]` | 4 terms `[0-9A-Fa-f_]` | costmodel 1t / 2t / 3t | verdict |
|---|---|---|---|---|---|---|
| walk | 0.1892 | 0.1877 | 0.1896 | 0.1891 | 0.1894 | CONFIRMED (and flat in terms) |
| V1 | 0.1082 | 0.1851 | 0.2141 | 0.2667 | 0.1095 / 0.1386 / 0.168 D | 1t CONFIRMED; 2t MOVED (cover shape, below); 3t REFUTED (+0.046) |
| S1 | 0.0205 | 0.0334 | 0.0417 | 0.0540 | 0.0206 / 0.0208 / 0.021 D | 1t CONFIRMED; 3t MOVED ×2 |
| A1 | 0.0106 | 0.0150 | 0.0192 | 0.0270 | 0.0105 / 0.0102 / 0.010 D | 1t CONFIRMED; 3t MOVED ×1.9 |

(D = DERIVED by costmodel.)

- **β depends on the cover's SHAPE, not only on its term count.** dfa-hat's 2-term cover
  is a cube {f,n} plus an equality t. On its own 64 KiB one-call row it reads V1 0.1384,
  S1 0.0212, A1 0.0107 (an. 2.3), which CONFIRMS costmodel's 2-term figures. Those were
  measured on that cell. hex-run's two RANGES cost V1 0.185, essentially the walk.
- **The saving β_t − β_f** (an. 2.1):
  - SWAR: +0.081, then +0.003, then −0.025, then −0.078 ns/B for 1, 2, 3 and 4 terms.
  - S1: from +0.169 at 1 term to +0.135 at 4.
  - A1: from +0.179 at 1 term to +0.162 at 4.

### 2.2 The per-call term, single member-free call (D5-sparse, MEASURED)

F(n) = ns − β·n, in ns per call.

| n | walk | V1 | S1 | A1 | Sn | An |
|---|---|---|---|---|---|---|
| 48 | 4.84 | 4.17 | 24.54 | 14.73 | 13.64 | 13.93 |
| 64 | 4.74 | 4.18 | 4.70 | 4.98 | 4.15 | 4.44 |
| 128 | 8.05 | 4.26 | 4.69 | 4.69 | 3.97 | 4.33 |

- regimefacts gave F = walk 4.29, V1 3.09, S1 20.45, A1 10.54, a line through
  n = 40 and 1 MiB. costmodel §B.4 cites the SIMD figures.
- Once the subject holds one whole block, every form's per-call fixed part is about
  4-5 ns, the walk's. The 10-25 ns is the sub-block TAIL (n < 64), not a per-call setup.
- regimefacts' SIMD n\* (the span where fixed = half of one call, F/β) was 975-993 B.
  With F ≈ 4.7-5.0 ns it MOVES to about 230 B (S1, 4.70/0.0205) and 470 B (A1,
  4.98/0.0106). The walk's is 25 B.
- The span at which a SIMD form starts to PAY against the walk is a different quantity.
  It is §4.2's L\*, 15-30 B, because the forms' F equals the walk's at n ≥ 64.

### 2.3 Every arm decomposed (FITTED, an. 2.3)

The fit is `T − β·bytes = F·A + w·(U−A) + p·U·[streamed u] + q·U·[repeated u]`.

- A = activations, the site's cold uses.
- U = uses, that is landings plus matches.
- bytes = ADV for the walk and blocks·W for a form (counters).
- β = the cell's own one-call 64 KiB row.
- The fit is relative least squares over the all-mode n = 64 KiB groups.
- Median relative residual: 1.2-5.7%. absExp: 0.93-0.99.

For dig (PF, 1 term):

| arm | F/activation | w/warm use | p (u-S use) | q (u-rep use) | β |
|---|---|---|---|---|---|
| walk | 8.11 | 1.67 | 4.31 | −0.15 | 0.1949 |
| V1 | 10.58 | 2.38 | 2.97 | 0.16 | 0.1159 |
| S1 | 11.01 | 2.22 | 0.80 | 0.02 | 0.0266 |
| A1 | 11.02 | 2.23 | 0.81 | 0.02 | 0.0164 |
| V3 / S3 / A3 | 10.5 | 2.3-2.4 | 3.1 / 1.0 / 0.9 | ~0.1 | as unkept |
| Sn / An | 10.7 / 10.5 | 4.0 / 3.9 | 0.6 | 0.0 | as S1/A1 |

bounded and dfa-hat are in an. 2.3.

- The walk's p is +2.0 ns on bounded and +5.3 ns on dfa-hat.
- dfa-hat's walk alone carries q = +1.46: the HAT walk loses on irregular gaps even when
  the subject repeats.
- The walk's own crossovers (FITTED):
  - g\* = w/β = 8.6 B (dig), 10.0 (bounded), 7.6 (dfa-hat).
  - With unpredictable fresh landings, g\* = (w+p)/β = 21-36 B.
  - L\*_walk = F/β = 34-68 B (F carries the match verify here, since calls ≈ matches).
  - costmodel: u 3.42 → g\* 18.5 B.
  - INTERPRETATION: real text's 3.42 ns per use is a mix of predictable and
    unpredictable landings.

### 2.4 costmodel's terms recomputed as differences (form − walk, FITTED, an. 2.3b)

Verdict rule: CONFIRMED when |grid − costmodel| ≤ max(0.5 ns, 25%), MOVED when the sign
holds, REFUTED when the sign flips.

| term | grid (dig / bounded / dfa-hat) | costmodel | verdict |
|---|---|---|---|
| c_cold V1 | +2.47 / +2.25 / +4.68 | +1.54 | MOVED (+0.7..+3.1) |
| c_cold S1 | +2.90 / +3.05 / +3.35 | +5.36 | MOVED (−2.0..−2.5) |
| c_cold A1 | +2.91 / +2.87 / +3.91 | +4.45 | MOVED on PF, CONFIRMED on HAT |
| c_cold V3 / S3 / A3 | +2.41 / +2.47 / +2.35 (dig) | +2.52 / +9.76 / +5.96 | CONFIRMED / MOVED −7.3 / MOVED −3.6 |
| c_warm V1 / S1 / A1 | +0.41..+0.99 | +0.96 / +0.72 / +0.65 | CONFIRMED |
| c_warm V3 / S3 / A3 | +0.44..+1.57 | +1.40 / +1.08 / +1.04 | CONFIRMED on dfa-hat and S3/A3 dig; MOVED down 0.5-0.8 on bounded and V3 dig |
| m (fresh) A1 | −3.49 / −0.65 / −3.99 (u-S) | −1.41 (1 MiB real text) | MOVED; its definition REFUTED (below) |
| m (fresh) V1 | −1.34 / +1.14 / −1.91 | −0.29 | MOVED / REFUTED on bounded |
| overscan ω, cold use | V1 1.0 B; S1 52.0; A1 54.2 | 4.7; 59.2; 59.2 | V1 MOVED; S1/A1 CONFIRMED |
| overscan ω, warm use | ≈ 0 for all | 2.62 / 3.63 | MOVED to 0 |
| κ (kept, scanned/advanced) | 1.000 / 1.001 / 1.001 | 1.22 / 1.32 / 1.32 | REFUTED on controlled data |
| stateless per use | +2.3..+2.8 ns, 61 B rescanned per use | — | new |

- **Width does not set the cold cost; the block it evaluates does.** c_cold is
  +2.3-2.9 ns for every form on PF. A W=64 activation then evaluates 52-54 B past
  its hit (MEASURED), about +1 ns at β = 0.016-0.027. The total is about 3.8-4.3 ns for
  W=64 against 2.5 for SWAR.
- **costmodel's "fresh" term is REFUTED as defined.** costmodel keyed its term on subject
  size. Here, streamed buffers whose landing offsets repeat (g = 2 `reg`, `reg`/`burst`
  shapes) show no fresh effect (an. 6.1), yet its estimator charged them −35 µs (§3).
- **The variable is the landing's predictability:**
  - the walk pays +4.3/+5.3 ns per unpredictable fresh landing;
  - the W=64 forms pay +0.8-1.4 ns;
  - SWAR pays +3.0-3.4 ns.

### 2.5 Fit quality per regime (delta = fit(form) − fit(walk), an. 2.5)

- **absExp:**
  - stateful forms: DINGHY 0.52-0.70, TUG 0.67-0.71, LINER 0.64-0.91;
  - stateless forms: 0.83-0.94.
- **In-sample sign errors:** at most 2 per form per regime.
- **Refitted without the row's g (sign errors):**
  - W=64: 0-6;
  - V1 TUG: 14 of 29;
  - V3 TUG: 11 of 25.

  The SWAR decision in TUG does not extrapolate across g. The repeated-u bimodality
  (§1.1) sits exactly there.

## 3. costmodel's estimator out of sample (an. 3)

Inputs: costmodel's printed constants (analysis.txt C.1, PF/HAT) and the grid's workload
facts U, ADV, A and fresh = streamed. No blocks counter is used. Measured class uses
this reading's NULL rule.

| form | DINGHY agree / absExp | TUG agree / absExp | LINER agree / absExp |
|---|---|---|---|
| V1 | 92% / 0.48 | 69% / −0.02 | 100% / 0.65 |
| S1 | 61% / −0.04 | 84% / −0.38 | 100% / 0.84 |
| A1 | 78% / 0.25 | 96% / −0.25 | 100% / 0.85 |
| V3 | 86% / 0.44 | 80% / −0.03 | 94% / 0.31 |
| S3 | 87% / 0.20 | 69% / −0.06 | 100% / 0.82 |
| A3 | 82% / 0.14 | 76% / −0.06 | 100% / 0.84 |
| pooled | 163/201 = 81% | 127/162 = 78% | 197/199 = 99% |

- costmodel's in-sample figures were DINGHY 86-91%, TUG 93-100%, LINER 96-100%.
- The confusion counts per cell are in an. 3.
- **The largest misses** (an. 3):
  - A1 on dfa-hat g4 L32: measured −40.4 µs, predicted +8.2 µs.
  - V1 on the same cell: measured −22.6 µs, predicted +17.5 µs.
  - Streamed g = 2 rows (reg shape) on all three cells: measured +0.6..+1.4 µs,
    predicted about −35 µs.
- **Verdict.** The estimator transfers in LINER (sign 99%, absExp up to 0.85). In TUG it
  explains less absolute ns than predicting zero would. Both misses are its fresh term
  and the HAT walk's per-landing cost.

## 4. The crossovers, measured (an. 4)

### 4.1 g\* per form (interpolated in log2 g between measured points; FITTED by interpolation)

| form | dig rep L=1k / 64k | dig rep L=32 (state lost) | dig streamed u | dfa-hat rep | bounded rep L≥1k | costmodel carried / lost |
|---|---|---|---|---|---|---|
| V1 | 16.7 / 10.8 | never wins (R at every g) | 3.7-4.3 | 3.0-3.3 | 21.5-21.6 | 15.6 / 25.7 |
| S1 | 4.7 / 4.3 | 20.5 | 2.0-2.8 | 2.1-2.4 | 3.6-5.8 | 4.7 / 39.0 |
| A1 | 4.4 / 4.2 | 13.6 | 2.0-2.6 | 2.1-2.3 | 2.4-3.0 | 3.8 / 28.4 |
| V3 | 18.5 / 14.0 | never wins | 4.0-4.9 | 3.5-3.9 | 22.8-23.7 | 29.3 |
| S3 | 6.8 / 5.5 | 13.8 | 2.3-2.7 | 2.8-3.0 | 4.7-8.9 | 6.7 |
| A3 | 5.3 / 4.6 | 11.2 | 2.3-2.6 | 2.8-3.1 | 2.7-4.7 | 5.9 |
| Sn / An | 24.8 / 20.7 (L=1k) | 58.5 / 33.3 | 6.1-7.4 | 12.3-14.3 | 22-27 | — |

- **Carried state, repeated:** costmodel's carried g\* is CONFIRMED for the W=64 forms,
  within ±0.9 B. V1 on dig reads 10.8-16.7 B against 15.6, so CONFIRMED at L = 1k. V1
  on bounded reads 21 B. V3 reads 14-18.5 B against 29.3 B: MOVED.
- **Lost state (L = 32):** W=64 crosses at 11-21 B. costmodel's 28-39 B is MOVED down.
- **Fresh irregular landings** move every g\* to 2-7 B.
- **dfa-hat** crosses at 2-4 B even on repeated data. INTERPRETATION: its walk's q term,
  §2.3.
- **FITTED g\*** (an. 4.1b): carried c_warm/Δβ = 2.3-6.4 B (W=64) and 8.2-8.9 (V1, PF).
  Lost c_cold/Δβ = 6-23 B (W=64) and 30-31 B (V1, PF).

### 4.2 L\*, the call span at which a form starts to pay (find-all, a match every L bytes; an. 4.2)

| cell, landings | walk/V1/A1/A3 at L = 8 | L = 32 | L\* (interpolated) |
|---|---|---|---|
| dig g=∞ | (not timed in all mode) | S1 −3.5 µs W, A1 −4.1 µs W, V1 +2.0 µs R | W=64 < 32 B; V1 89 B, V3 101 B |
| dig g=64 | V1 +24.6 µs, A1 +27.0, A3 +9.6 (all R) | A1 −4.3, A3 −6.0 (W) | A1 26 B, A3 19 B, V1 45 B |
| dig g=4 | all R | all R | none: W=64 NULL at L ≥ 1k, V1 R everywhere |
| dfa-hat g=4 | V1 +37 µs, A1 +33, A3 +17 (R) | V1 −22.6, A1 −40.4 (W) | V1 19 B, A1 15 B, A3 14 B |
| bounded g=∞ | S1 +19.4, A1 +12.4 (R) | S1 −2.8, A1 −4.6 (W) | S1 27 B, A1 22 B, V1 58 B |
| bounded g=32 | R except S3/A3 W | A1 −1.7 W, S1 N | A1 28 B, S1 34 B, V1 325 B |

The deltas are per 64 KiB pass.

- **L\* for W=64 sits between 8 and 32 B (MEASURED)**, about 15-30 B interpolated.
  FITTED c_cold/Δβ on dig: S1 17, A1 16, S3 15, A3 13, Sn 15, An 14 B. For SWAR it is
  45-100 B (FITTED 31-33 B).
- **This settles the disagreement:**
  - costmodel's per-form break-even, 19-39 B: CONFIRMED.
  - Its regime boundary L\* = 64 B: conservative by 2-4x for W=64.
  - regimefacts' n\* ≈ 1 KB is not a pay-off span. It is where a SIMD form is half fixed
    cost, and its F came from the n = 40 tail (§2.2). With the measured F it MOVES to
    about 230-470 B.

### 4.3 The single-call (`first`) crossover (D4/H4, an. 4.3)

One call of span about L, with landings every g inside it. Values are Δ in ns per call.

| cell, landings | L = 8 | L = 32 | L = 128 |
|---|---|---|---|
| dig g=∞ (walk 9.3 / 14.1 / 32.4 ns) | V1 +2.3, S1 +2.9, A1 +3.2, An +2.0 (all R) | V1 +0.6 R, S1 −1.9, A1 −1.6, An −2.8 (W) | V1 −6.3, A1 −19.5 (W) |
| dig g=8 | all R (+2.0..+3.2) | all R (+3.6..+19.6) | S1/A1 NULL; V1 +18 R |
| dig g=2 | all R | all R | S1/A1 +5 R; Sn/An +165..+216 R |
| dfa-hat g=∞ | all R (+3.9..+4.5) | W=64 −2.3..−2.9 (W; S1 NULL) | all W |
| dfa-hat g=8 | all R | W=64 +2.7 R | S1/A1 −13 W |

- A single member-free call crosses between 8 and 32 B: S1 at about 18 B and A1 at about
  20 B (interpolated), V1 at about 36 B.
- With a landing every 8 B the crossover moves past 32 B.
- With a landing every 2 B a single call never pays.
- Stateless forms lose single calls that hold landings heavily: +15 to +216 ns.

### 4.4 The block-straddling lengths {48, 63, 64, 65, 128} (dig, an. 4.4; ns per pass)

| n | first, member-free: walk / V1 / S1 / A1 / Sn / An | all, g=8 a match per 32 B: walk / V1 / S1 / A1 / A3 / An |
|---|---|---|
| 48 | 13.9 / 9.4 / 25.5 / 15.2 / 14.6 / 14.4 | 20.4 / 24.6 / 41.8 / 32.7 / 33.3 / 20.8 |
| 63 | 16.7 / 11.1 / 32.5 / 22.5 / 17.2 / 17.1 | 20.4 / 24.6 / 48.4 / 38.3 / 38.8 / 20.6 |
| 64 | 16.9 / 11.1 / 6.0 / 5.7 / 5.5 / 5.1 | 37.2 / 48.6 / 43.3 / 42.2 / 41.0 / 45.3 |
| 65 | 17.0 / 12.0 / 7.7 / 6.6 / 7.1 / 6.0 | 38.6 / 49.0 / 43.4 / 42.1 / 41.1 / 45.8 |
| 128 | 32.3 / 18.1 / 7.3 / 6.1 / 6.6 / 5.7 | 74.8 / 90.4 / 79.0 / 76.3 / 73.7 / 96.4 |

- **The step is at the block, n < 64 versus n ≥ 64, MEASURED.**
  - Below 64 B the stateful W=64 forms pay the tail: S1 +11.6/+15.8, A1 +1.3/+5.8 ns.
  - The stateless forms are near neutral there (+0.5 ns). V1 wins (−4.6..−5.6 ns).
  - At n ≥ 64 every W=64 form wins a member-free call by 9-11 ns, and by 25-27 ns at 128.
- **In the dense find-all:**
  - every form loses at 64-65 B (+3.8..+13.7 ns);
  - stateless Sn/An tie the walk below 64 B (+0.3 ns) and lose above it;
  - by 128 B A3 wins (−1.1 ns).

## 5. The regime boundaries (an. 5) and the other axes (an. 6)

### 5.1 Do DINGHY / TUG / LINER hold on controlled data?

costmodel's rule (L < 64; else g < 18.5) places the all-mode groups as follows:

| cell | DINGHY | TUG | LINER |
|---|---|---|---|
| dig | 19 | 20 | 17 |
| dfa-hat | 10 | 13 | 13 |
| bounded | 10 | 5 | 5 |

Per form per regime, W / R / N and the summed Δ per pass (an. 5.2):

| form | DINGHY | TUG | LINER |
|---|---|---|---|
| V1 | 3/33/3, +377 µs | 9/20/6, +157 µs | 32/0/3, −141 µs |
| A1 | 15/21/3, +134 µs | 23/2/13, −362 µs | 35/0/0, −451 µs |
| A3 | 18/15/6, −54 µs | 18/11/6, −173 µs | 35/0/0, −440 µs |
| An | 10/20/5, +632 µs | 6/26/1, +1,190 µs | 33/0/0, −360 µs |

- **The two facts hold as the variables.** The single best threshold on g, for rows with
  L ≥ 64, separates W=64 wins from losses with 0-2 errors on 58-64 rows (an. 5.3).
- **The boundaries do not hold for W=64.** The best 2-D split "win iff L ≥ L\* and
  g ≥ g\*" is (MEASURED, an. 5.4):

  | form | best (L\*, g\*) | errors | costmodel (64, 18.5) |
  |---|---|---|---|
  | S1 | (8, 3) | 8 of 89 | 32 |
  | A1 | (8, 4) | 7 of 96 | 38 |
  | A3 | (8, 4) | 10 of 97 | 36 |
  | V1 | (64, 4) | 10 of 97 | 12 |
  | V3 | (64, 10) | 8 | 9 |
  | Sn | (8, 20) | 6 | 13 |
  | An | (8, 12) | 7 | 16 |

  The grid's L axis has no point between 8 and 32, so "L\* = 8" means "somewhere in
  8 to 32"; §4.2 places it at about 15-30 B.

- **How the boundary moves:**
  - **Width:** W=64 g\* is 4-5 B; SWAR g\* is 11-21 B. W=64 L\* is 15-30 B; SWAR L\* is
    45-100 B.
  - **Keep:**
    - A3 lowers the lost-state g\* (11.2 against A1's 13.6 at L = 32).
    - On bounded L = 8, the kept S3/A3 are the only forms that win: W at g = 32, NULL
      at g = 8.
    - At long L, keep is slightly worse (g\* 4.6-5.3 against 4.2-4.4).
  - **Terms:** with SWAR, a second RANGE term removes the saving (§2.1). With W=64 the
    saving falls only 7-20% from 1 to 4 terms.
  - **Site kind:** on dfa-hat every form crosses at g = 2-4 B, against 4-17 on dig.
    INTERPRETATION: that is the walk's q, not the cover.
  - **Predictability:** fresh irregular landings move every g\* to 2-7 B.

### 5.2 Absolute cost per regime (an. 5.5; medians over the 64 KiB all-mode groups)

| regime | walk ns per call | walk ns per MiB | V1 Δ per call / per MiB | A1 Δ | A3 Δ | An Δ |
|---|---|---|---|---|---|---|
| DINGHY | 16.5 | 765,311 | +2.4 / +155,074 | +0.8 / +25,324 | −0.7 / −60,090 | +1.9 / +122,075 |
| TUG | 1,101 | 766,091 | +112.6 / +88,974 | −64.5 / −56,330 | −51.1 / −53,102 | +668 / +307,984 |
| LINER | 297 | 270,429 | −72.9 / −64,912 | −209 / −188,791 | −205 / −187,219 | −230 / −186,629 |

- **A dinghy call costs about 16 ns.** A form moves it by a nanosecond or two: +0.8 ns
  (A1) to +2.4 ns (V1).
- **Per MiB of dense text the same call pattern costs 0.77 ms.** A form moves that by
  25-155 µs.
- **A liner MiB costs 0.27 ms.** W=64 cuts it by 0.19 ms, 70%.

### 5.3 Repeated vs streamed: the learned predictor (an. 6.1)

Walk ns per pass, repeated against streamed (fresh), at equal (g, L, shape):

| subject | walk rep | walk streamed | ratio | extra per landing |
|---|---|---|---|---|
| dig g8 L1k u | 23,484 | 62,597 | 2.67 | 4.79 ns |
| dig g8 L32 u | 38,610 | 80,473 | 2.08 | 5.84 ns |
| dig g32 L1k u | 16,583 | 29,315 | 1.77 | 6.24 ns |
| dfa-hat g8 L64k u | 28,057 | 66,157 | 2.36 | 4.65 ns |
| bounded g32 L1k u | 15,850 | 26,193 | 1.65 | 5.07 ns |
| dig g8 L1k **reg** | 20,962 | 21,051 | 1.00 | 0.01 ns |
| dig g8 L1k **burst** | 29,478 | 28,111 | 0.95 | −0.17 ns |
| dig g32 L1k reg / burst | 16,902 / 17,280 | 16,972 / 17,368 | 1.00 / 1.01 | 0.03 / 0.04 ns |
| every g = 2 (reg) row | | | 1.00-1.01 (dfa-hat L64k 1.11) | ≤ 0.03 ns (dfa-hat L64k 0.18) |

- **The effect costmodel blamed for the 1 MiB misses is present, and the grid isolates it
  as the predictor.**
  - The streamed `reg`/`burst` buffers are 64 MiB of distinct bytes, past the 32 MiB L3,
    yet run at the repeated speed. Their landing offsets repeat.
  - The streamed `u` buffers, whose offsets vary, cost the walk 4-7 ns per landing.
  - So it is not cache or DRAM. INTERPRETATION: a mispredicted loop exit per landing.
    F2 would have counted it.
- **The forms barely move,** so the deltas flip:
  - dig g8 L1k: A1 −3.8 µs repeated against −39.8 µs streamed; V1 +5.6 against
    −14.3 µs.
  - At g = 256 the effect fades: dig L1k 1.05x.

### 5.4 Gap shape at equal mean (D7, dig L = 1k, an. 6.2)

| g | walk reg / u / burst (repeated) | V1 Δ reg / u / burst | A1 Δ reg / u / burst |
|---|---|---|---|
| 8 | 20,962 / 23,484 (bimodal, 8.3% A/A) / 29,478 | +7.3 R / +5.6 R / −1.6 N | −0.9 W / −3.8 W / −9.6 W |
| 32 | 16,902 / 16,583 / 17,280 | −4.0 / −3.2 / −4.1 (all W) | −10.4 / −10.1 / −11.1 (all W) |

Deltas are in µs.

- **At g = 8 the shape matters.**
  - Bursts make the walk 41% slower than a regular gap, so every form gains about
    8.7-9.0 µs.
  - `u` sits between, and is bimodal.
- **At g = 32 the shape is within 4% on repeated data.** It matters only when the data is
  fresh: `u` streamed costs the walk 1.77x.

### 5.5 Start alignment and the prologue arms (D6, an. 6.3)

- **64 KiB member-free call:** S1/S2/A1/A2 are identical within 15 ns at offsets 0, 7
  and 31 (A/A ≤ 0.2%).
- **65-byte call:** the prologue costs A2 +7.4 ns and S2 +1.3 ns at offset 7, and gains
  0.6-1.3 ns at offset 31. S1 and A1 do not move with offset at all.
- **Find-all TUG, g = 8 L = 1k:** S2 and A2 are 0.5-1.4 µs WORSE than S1 and A1 at every
  offset.
- **F3, one member-free call:** S2 − S1 and A2 − A1 are within ±2 ns at 64 KiB. At
  1 MiB they range from −608 to +54 ns (≤ 1.1%), on a floor of 0.27%. V2 − V1 is
  +0.6..+11.2 µs at 2-4 terms: the SWAR prologue loses.

So the prologue arms never pay on this box at any offset measured.

### 5.6 Stateless Sn/An vs stateful at dinghy spans (costmodel F6, an. 6.4)

Summed Δ per pass over the all-mode groups at each span:

| L | S1 / S3 / Sn | A1 / A3 / An |
|---|---|---|
| 8 | +165 / +14 / +290 µs | +229 / +35 / +235 µs |
| 32 | −64 / −62 / +553 µs | −95 / −89 / +397 µs |
| 1k | −390 / −276 / +696 µs | −420 / −324 / +465 µs |

- An − A1 at L = 32 is +77 µs (g = 2), +37 µs (g = 4), +3.5 µs (g = 32), and −0.8 µs
  only at g ≥ 256.
- Stateless forms rescan a block per use (61 B, an. 2.4) at +2.3-2.8 ns per use.
- **slot2's kernel finding, that stateless beats stateful mask forms at dinghy spans, is
  REFUTED in the pipeline.** Stateless is the better form only where the subject is
  shorter than a block (§4.4: +0.5 ns against +1.3..+15.8 ns at n = 48/63). At L = 8 the
  kept stateful forms (S3/A3) lose 7-20x less than stateless (summed +14/+35 µs against
  +290/+235 µs).

### 5.7 dfa-hat vs the PF cells (an. 6.5)

Same g, L = 1k, u shape. The walk costs, in ns:

| g | dig walk | hat walk |
|---|---|---|
| 4 | 38,139 | 69,217 |
| 8 | 23,484 | 34,874 |
| 16 | 18,502 | 25,801 |
| 64 | 17,576 | 17,609 |

At g = 2 with the reg shape, the hat walk is the CHEAPER one (61,358 against 73,876).

- **The forms gain where the hat's walk pays:** A1 −34.1 µs on the hat against +0.7 µs on
  dig at g = 4.
- **The hat's walk pays per irregular landing even on repeated data** (q = +1.46 ns,
  §2.3).
- INTERPRETATION: the DFA's start-state re-entry mispredicts on irregular gaps, and the
  PF scan's exit learns them.
- **Consequence:** costmodel's assumption that "the consumer term cancels" fails at the
  hat on irregular gaps.

### 5.8 F3: β by terms, the SWAR term limit (§2.1)

- **SWAR stops paying at 2 RANGE terms.** V1's saving is +0.003 ns/B at 2 terms and
  negative at 3 and 4. A cube+eq 2-term cover still saves 0.05 ns/B.
- costmodel's "SWAR stops paying at 4-5 terms" (slot2 synthetic) is AMENDED: it is 2-3
  terms, and the limit depends on the cover's shape.
- **W=64 stays well inside the saving:** 0.135-0.169 (S1) and 0.162-0.179 (A1) ns/B across
  1-4 terms.

### 5.9 EXT (main's engine arms) — placed only

There are 24 groups; main reads them itself. vm against dfa:

| cell family | W | R | N |
|---|---|---|---|
| p1/p2/p3 `all` | 9 | 0 | 3 |
| p1/p2/p3 `first` | 6 | 3 | 6 |

The `dfa` arms (p2) are W 4 / N 4. EXT A/A p90 is 0.38%.

## 6. The decision table re-priced (an. 7)

### 6.1 The priced rows

`FORM_ROWS` keeps its shape (row, layer, needs).

- **The PRICE** is now the absolute closed form of §2.3, per cell, with the re-fitted
  constants (an. 7.1 table):
  - F, w, p, q are FITTED; β and ω/κ are MEASURED;
  - bytes for a form = ADV + ω_cold·A + ω_warm·(U − A), or κ·ADV for a kept form.
- **The walk is priced too**, not fixed at 0, so the argmin is over absolute cost.
- The regime is still not a column.

On the oracle facts, the argmin agrees with the measured best on 28-32 of 33-35 groups
per regime per layer.

### 6.2 Regret per information source, absolute (an. 7.2)

Regret is the measured pick's ns minus the layer's fastest row's, summed over the 101
all-mode groups that time all nine forms. It is shown as µs per pass summed and as % of
the walk's summed ns. Walk sums: DINGHY 1,630 µs, TUG 1,579 µs, LINER 583 µs.

The model rows are IN SAMPLE except LOGO, which is refitted without the row's g. The
sources:

| source | landings | span (A) | predictability |
|---|---|---|---|
| prior | p(1−p) from the unigram | 1 | assumed predictable |
| gap (exemplar) | true | 1 | true |
| span (call pattern / iterator) | prior | true | — |
| gap+span | true | true | true |

| layer | policy | DINGHY | TUG | LINER |
|---|---|---|---|---|
| SIMD-off | always walk | 38.7 µs (2.4%) | 100.9 (6.4%) | 135.3 (23.2%) |
| | always V1 | 307.1 (18.8%) | 262.5 (16.6%) | 0.5 (0.1%) |
| | prior / span | 96.2 (5.9%) / 38.7 (2.4%) | 157.7 (10.0%) | 56.5 (9.7%) |
| | gap | 43.2 (2.7%) | 6.4 (0.4%) | 0.5 (0.1%) |
| | gap+span (LOGO) | 25.2 (1.5%) [83.2 (5.1%)] | 6.4 (0.4%) [221.2 (14.0%)] | 0.5 (0.1%) [0.5] |
| | hint walk/walk/V1 (LOCO same) | 38.7 (2.4%) | 100.9 (6.4%) | 0.5 (0.1%) |
| SIMD-on | always walk | 148.5 (9.1%) | 337.6 (21.4%) | 428.4 (73.5%) |
| | always A1 | 180.2 (11.1%) | 19.5 (1.2%) | 0.1 (0.0%) |
| | always An | 780.0 (47.9%) | 1,527.6 (96.8%) | 68.1 (11.7%) |
| | prior | 180.2 (11.1%) | 19.5 (1.2%) | 0.1 |
| | gap / span | 107.6 (6.6%) / 109.0 (6.7%) | 2.3 / 19.5 | 0.1 |
| | gap+span (LOGO) | 0.8 (0.0%) [15.6 (1.0%)] | 2.3 (0.1%) [17.9 (1.1%)] | 0.0 [0.0] |
| | hint walk/A1/A1 (LOCO) | 148.5 (9.1%) [281.7 (17.3%)] | 19.5 (1.2%) | 0.1 |
| SIMD-on + iterator | always A3 | 91.4 (5.6%) | 178.6 (11.3%) | 9.8 (1.7%) |
| | always A1 | 218.4 (13.4%) | 19.5 (1.2%) | 0.1 |
| | gap+span (LOGO) | 7.6 (0.5%) [24.1 (1.5%)] | 2.3 (0.1%) [17.9 (1.1%)] | 0.3 (0.1%) [0.7] |
| | hint A3/A1/A1 (LOCO) | 91.4 (5.6%) [238.6 (14.6%)] | 19.5 (1.2%) | 0.1 |

Readings, which are MEASURED regret over the model's or the hint's picks:

- **SIMD-off: the information that matters is the GAP.**
  - In TUG the regime hint regrets 6.4% and the exemplar gap model 0.4%, in sample.
  - Refitted without the row's g, the gap model regrets 14%. INTERPRETATION: SWAR's TUG
    boundary sits where the walk is bimodal (§1.1), so this one cell of the table is
    not decidable from these data.
  - The prior alone is worse than "always walk" in DINGHY and TUG (5.9% / 10.0% against
    2.4% / 6.4%).
- **SIMD-on: the information that matters is the SPAN plus the gap, and only in DINGHY.**
  - In TUG and LINER, A1 is within 1.2% with no information at all.
  - In DINGHY, a fixed row regrets 9-11% and the regime hint does no better than "always
    walk". gap+span gets 1.0% out of sample.
  - The hint is unstable across cells: LOCO 17.3%.
- **With the iterator, A3 is the best single row in DINGHY (5.6%), but not elsewhere.**
  - costmodel's "avx2+keep everywhere" regretted 2.8 / 4.0 / 1.9%. On the grid it
    regrets 5.6 / 11.3 / 1.7%: MOVED.
  - Dropping KEEP outside DINGHY (hint A3/A1/A1) gives 5.6 / 1.2 / 0.0%.

### 6.3 The rules of thumb (costmodel §E)

| rule | verdict | evidence (rows / an. section) |
|---|---|---|
| R0 two facts L and g; landings not bytes | CONFIRMED as the variables; boundaries AMENDED | g separates W=64 wins with 0-2 errors of 58-64 at L ≥ 64 (an. 5.3). Best split (8-32 B, 3-4 B) for W=64, (64, 4-10) for SWAR, against costmodel's (64, 18.5) (an. 5.4). Bytes vs landings is not varied here (members = landings by construction). |
| D1 SIMD-off DINGHY: walk | CONFIRMED | V1 DINGHY 3/33/3, +377 µs; regret walk 2.4% against V1 18.8% (an. 5.2, 7.2) |
| D2 SIMD-on, no state, DINGHY: walk | AMENDED | Right as a fixed row (9.1% against A1 11.1%), but DINGHY splits by landings. At L = 32 every W=64 form wins from g ≥ 16-32 (dig L32 A1 W at g ≥ 32; dfa-hat L32 W at g ≥ 4) and loses at L = 8 at every g (an. 4.1, 4.2). Decide on L ≥ ~16-32 B AND g ≥ ~4-16 B. |
| D3 SIMD-on + iterator DINGHY: W=64 + KEEP | CONFIRMED in direction | A3 DINGHY 18/15/6, −54 µs; always A3 regrets 5.6% against walk 11.5% (an. 7.2). The kept S3/A3 are the only wins at bounded L = 8 g = 32 (−5.6/−6.6 µs); A3 is NULL at dig L = 8 g = 4 where A1 loses +10.4 µs. The kept forms are still hand edits. |
| D4 single short calls cannot be helped; lowest fixed cost | AMENDED | At L = 8 every form loses +2.0..+5.6 ns (dig/dfa-hat, an. 4.3). From L ≈ 18-20 B a member-free single call wins with W=64 (−1.6..−2.9 ns at 32, −19.5 at 128). Stateless is NOT the low-fixed-cost choice when the call holds landings (+15..+216 ns). |
| D5 subjects shorter than a block: no W=64 form | CONFIRMED for stateful; AMENDED | n = 48/63: S1 +11.6/+15.8, A1 +1.3/+5.8 ns. Stateless +0.5. V1 −4.6/−5.6 (an. 4.4). At n ≥ 64 every W=64 form wins a member-free call (−9..−11 ns). regimefacts' "n\* ≈ 1 KB, SIMD forms' F 10-20 ns" was the n = 40 tail (§2.2). |
| T1 SIMD-off TUG: walk | AMENDED | Right as a fixed row (6.4% against V1 16.6%), but V1 wins TUG rows with unpredictable fresh landings (dig g8 L1k u-S −14.3 µs; dfa-hat g8 −15.3 µs) and dfa-hat g ≥ 4 repeated (an. 6.1, 6.5). The gap model reaches 0.4% in sample (14% LOGO). |
| T2 SIMD-on TUG: W=64, AVX2 over SSE2; KEEP adds machinery | CONFIRMED | A1 TUG 23/2/13, −362 µs; S1 19/6/11, −302 µs; A3 18/11/6, −173 µs; always A1 1.2% against S1 2.8% and A3 11.3% (an. 5.2, 7.2). |
| T3 P2/P3 multi-position filters | UNTESTED | No multi-position arm in the grid. |
| L1 LINER: widest block | CONFIRMED | A1 LINER 35/0/0, −451 µs; always A1 0.0% (an. 5.2, 7.2). |
| L2 LINER: KEEP and the prologue add nothing | CONFIRMED | A3 −440 against A1 −451 µs. S2/A2 within ±15 ns at 64 KiB at offsets 0/7/31; ±1.1% at 1 MiB (an. 6.3). |
| L3 SWAR term count; stops paying at 4-5 terms | AMENDED | It stops at 2 RANGE terms (saving +0.003 ns/B), and a cube+eq 2-term cover still saves 0.05. The 3-term β was DERIVED 0.168 and is MEASURED 0.214 (an. 2.1). |
| X1 information buys the regime; within a regime one fixed form is within 0.1-3% | AMENDED | Holds for SIMD TUG/LINER (A1 ≤ 1.2%) and SIMD-off LINER (V1 0.1%). Fails in DINGHY (fixed rows 5.6-11%; gap+span 1.0% LOGO) and SIMD-off TUG (6.4%). |
| X2 decide on fresh large data, not 64 KiB repeats | CONFIRMED and sharpened | The effect is unpredictable landing positions (u-S walk 1.65-2.67x, 4-7 ns per landing). Streamed reg/burst = repeated within 1%: not cache/DRAM (an. 6.1). Repeated u is bimodal across launches (an. 6.2b). |

## 7. What is still unknown

- **F2 (perf branch misses), skipped: perf_event_paranoid=4.** It would turn the
  INTERPRETATIONS of §5.3 and §5.7 into counts:
  - p (+4-5 ns per unpredictable fresh landing on the walk) = one mispredicted exit per
    landing;
  - the walk's per-launch bimodality = predictor learning state;
  - the hat's q = its re-entry mispredicting.

  Expected if right: about 1 miss per u-S landing for the walk, about 0.2 for W=64, and a
  bimodal miss count on the repeated u groups. F2 is a measured cell list in
  `grid1/arms_f2.tsv`, about 1-2 min where perf is allowed.
- **F4 / F7 (D165's iterator).**
  - The kept rows (V3/S3/A3) are hand edits. Their c_cold (+2.4) and their DINGHY win
    (A3 −54 µs, the best fixed row with the iterator) are what F4 must reproduce through
    the real iterator.
  - F7 prices the span hint. The grid says the span decision is the one that matters in
    SIMD DINGHY: 9.1% with the hint, 1.0% with gap+span out of sample. F7 measures what
    learning L per call costs against that.
- **F5 (Zen 1, through a bench request).**
  - Every constant here is Zen 4 (AVX2 2x256 ports, AVX-512 present).
  - On Zen 1 (AVX2 executed as 2x128), A1's β should approach S1's, moving W=64's L\*
    and g\* up. The predictor and mispredict penalty also differ, which moves p.
  - The official verdict on any rule here is that bench run (D144 addendum 4).
- **Not covered by the grid at all:**
  - near-hit depth (every landing fails within 1-2 bytes);
  - bytes-vs-landings decoupling (members = landings here);
  - multi-position filters (T3);
  - real text's MIX of predictable and unpredictable landings, which is what sets
    costmodel's 3.42 ns per use (§2.3).

## Interpretations flagged (not measurements)

- **§1.1, §5.3: the walk's bimodality and the u-S per-landing cost are the branch
  predictor.** Inferred from the reg/burst/u controls and the per-launch values. No perf
  count (F2).
- **§5.7: the hat's walk pays on irregular gaps because its start-state re-entry
  mispredicts.** Inferred from dfa-hat against dig at equal gaps and from g = 2 reg.
- **§2.2: regimefacts' SIMD F (cited by costmodel §B.4) came from the n = 40 sub-block tail.**
  Supported by the measured step at n = 63/64, but not re-run on n = 40.
- **§2.3: real text's 3.42 ns per use is a mix of predictable and unpredictable
  landings.** No real-text subject was run here.
- **§6.2: SWAR's TUG boundary is not decidable from these data.** Inferred from the LOGO
  regret and the bimodal walk.

## Method notes

- **ADV (bytes the find advances)** is DERIVED from the planted counts:
  - all mode: n − matches × the match token's bytes after its landing (dig 1, dfa-hat
    3.33, bounded 0);
  - first mode: the span to the first match.

  Everything else is a counter.
- **Activations A** are the site's cold uses (`site(G1)`, identical to V1's counters, as
  in costmodel).
- **Streamed rows** are per buffer (the counters are divided by `nbuf`).
- **β per cell** for §2.3 comes from the cell's own one-call 64 KiB row (ginf L64k).
  - It carries that row's one match and two calls: about +0.006 ns/B on dig against F3's
    member-free 0.1892.
  - F3's slopes are the clean β (§2.1).
- **The absolute-fit approach.** costmodel fitted DELTAS (form − walk) with its walk
  terms fixed. On the grid that confounds the walk's predictability with the form's
  costs: the first delta fit returned c_cold = −4,434 ns on the hat's kept forms. Fitting
  each arm's ABSOLUTE ns and differencing is what made the terms identifiable (median
  relative residual 1-6%).

## Files

- `docs/dev/lanes/gridread/gridread.py`: the reading (sections 1-7 of analysis.txt).
- `docs/dev/lanes/gridread/grload.py`: the loaders and the per-cell compile-time facts.
- `docs/dev/lanes/gridread/SHA256SUMS`: the 14 inputs, verified by `--check`.
- `docs/dev/lanes/gridread/analysis.txt`: the full output.
- `docs/dev/lanes/gridread/CLAUDE.md`.

## Charter vs committed

| charter item | committed |
|---|---|
| 1. A/A floor per group from per-launch values; spread; unstable groups; NULL rule; quiet gate | §1 (an. 1): floor tables, per-arm spread, 55 unstable groups listed, three-rule comparison, gate held (load1 ≤ 1.20, 0 waits, 0 answer disagreements) |
| 2. Re-fit β, c_cold, c_warm, overscan, per-call setup per form and width; CONFIRMED/MOVED/REFUTED; fit quality per regime | §2 (an. 2.1-2.5). β by terms (F3); setup F(n); absolute per-arm fits per cell; the costmodel terms as differences with verdicts; ω/κ; absExp and sign/LOGO errors per regime |
| 2. costmodel's estimator out of sample: sign and absolute agreement per regime, confusion counts | §3 (an. 3): per form and regime confusion, absExp, pooled agreement, largest misses |
| 3. g\* per form (carried/lost, repeated/streamed, keep); L\* (19-39 B vs ~1 KB); single-call first crossover; {48,63,64,65,128} | §4.1-4.4 (an. 4) |
| 4. Do DINGHY/TUG/LINER hold; measured boundaries; movement with width, keep, terms | §5.1-5.2 (an. 5.1-5.5) |
| 5. Repeated vs streamed; gap shape; alignment and prologue; stateless vs stateful at dinghy spans; dfa-hat vs PF; F3 terms | §5.3-5.8 (an. 6.1-6.6); EXT placed §5.9 |
| 6. §C.3's priced table re-priced; regret per information source per regime in absolute terms; §E verdicts with evidence | §6.1-6.3 (an. 7) |
| 7. Unknowns: F2, F4/F7, F5 and what each would change | §7 |
| Label interpretation; tie claims to rows; MEASURED vs FITTED | labels throughout; "Interpretations flagged" |
| Report, scripts re-runnable with `python3 -I`, input checksums, CLAUDE.md line, checklist | this file; `gridread/` (own CLAUDE.md); `SHA256SUMS` + `--check`; `docs/dev/lanes/CLAUDE.md` one line |
| No timing, no build of timed binaries, no make test; slot outputs read only | held: python reading only; nothing written under `worktrees/memfn-slot/grid1/` |
