# grid2read — the reading of the zen4-grid2 timing slot (r17b_prime.md §5.4 / §9.3)

Lane grid2read, 2026-10-16, branch `lane/grid2read` (cut from `lane/memfn-fd` b66645a48). ANALYSIS ONLY:
no timing, no build, no `make`; python over the slot's TSVs. Inputs are the 18 slot files listed in
`docs/design/memfn/r17b_prime/grid2read/SHA256SUMS` (verified: 18 inputs, 0 mismatched), under
`worktrees/memfn-slot/grid2/`. The design read is `docs/design/memfn/r17b_prime.md` REV 3 (blob 1fb32b445 at
`lane/memfn-fd`), D167 + addenda 1-3, the shipped finder's operand spellings (`memfn/src/finder.c` on `lane/fdb2`)
and the predecessor reading `docs/dev/lanes/gridread_report.md` (`lane/memfn-gridread`), whose NULL rule and
fit shape this reuses.

- Scripts and data: `docs/design/memfn/r17b_prime/grid2read/` (`grid2read.py`, `grload2.py`, `analysis.txt`,
  `keys.tsv`, `SHA256SUMS`, its `CLAUDE.md`). Re-run: `python3 -I grid2read.py > analysis.txt`.
  Citations "an. 4.2" point into `analysis.txt`.
- Slot: method `kit-grid@2`, Zen 4 7700X, CPU 14, governor `performance`, gcc 15.2 -O2, 3 launches (+2 by the
  rerun rules), SLOT_START 18:59:54, COMPLETE 20:06:22 (`required=ok optional=done`, wall 3,988 s). Compiler:
  `lane/memfn-r17` c90d65e53, abi 77, sha256 8952969605e8…, build inputs clean. Gate: `CHECK_OK arms: 141
  (cell, arm) pairs, 227 groups, 1070 items, 0 problems`, provcheck 67 arm signatures, U2 60 groups 0 failures,
  0 `ANSWER MISMATCH` lines, one answer line per arm in every group (an. 1).
- Labels: **MEASURED** (read from a row or counter), **FITTED**, **DERIVED** (arithmetic on measured values),
  **INTERPRETATION** (mine; listed in §9). Every number is Zen 4, gcc 15.2, streamed distinct buffers, KIT tier,
  UNOFFICIAL (D144 add. 4). The slot's `walk` arm is the kit compiler with `--memfn=no-pf-terms-mask`
  (`compiler_pf_terms_mask_deny=moves-text`), i.e. the kit branch's table walk; §9.2 names MAIN's walk as the
  B4 baseline, and byte equality of the two walks was not checked here (INTERPRETATION that they are the same).
- The NULL rule (gridread's, regime-split): a delta is NULL when |delta| <= max(the group's own A/A floor,
  FRG[regime] x base) or the launch-paired deltas disagree in sign. The group floor is max(|walk#b - walk|,
  |walk#c - walk|); FRG is that regime's pooled #b+#c A/A p90 (an. 3).

## Summary

1. **Contamination: one group visit, 45 launch rows (0.87% of 5,163), no data lost.** The window 19:38:11-19:39:30
   overlaps only the first F3 group (`f3-dig` n64k, 19:38:11-19:38:38, 5 launches x 9 arms, load1 up to 3.12). The
   harness saw it (`BREACH(requeue)`), waited 200 s, and re-timed it at 19:46:33 (load1 max 1.06); every verdict
   here uses the clean re-timing. Contaminated medians read +1% to +8% (walk copies +6.9%/+8.1%). No constant or
   prediction depends on the lost visit. F1 and F2 logged no violation (§2).
2. **Two further F3 groups and one F1 group breached LOADMAX outside the stated window and the harness did not log
   them** (`f3-word-eq` n1m 19:43, `f3-quad` n64k 19:44, F1 `dig g8 L1k u @7` 19:21): treated as LOAD-SUSPECT. They
   make the (2,0,1) and (3,1,0) shape rows PROVISIONAL (V1/S1 slopes agree with grid1 to 0.4%). **OWED:** a 2-minute
   re-run of the two cells (§8).
3. **kit.eps.streamed.slope = 0.113%** (grid1 0.173%): CONFIRMED as a regime-split token (F1 find-all 1.316%, 11.6x
   larger). The noise of the quantity the savings derive from, the slope, is 0.25% p90 / 0.32% max, 2.2x the token;
   no R0/R7 decision flips.
4. **beta (u = 0.1891 ns/B):** V1 saves +42.0% on the (1,0,0) class, +1.2% on (2,0,0), +26.8% on (0,1,1) and loses
   13.3%, 41.3% and 46.4% on (2,0,1), (3,1,0), (3,0,1); the three unmeasured item-3a shapes save +39%, +55%, +21%.
   S1/A1 save 69-89% / 84-94%. Within 0.1-3.3% of grid1 on all 11 comparable cells.
5. **Contradiction, M9:** with the compiler's own V1 text V1 beats the walk at EVERY measured N from 8 B (-0.18 ns,
   4.5x floor) to 1 MiB. The 36 B crossover (grid1) is not reproduced; the staircase rule gives N* = 8 = the lowest
   measured point, NOT LOCATED. R1 has no interval. S1/A1 lose to the walk below 64 B (n=63: +13.7/+2.8 ns).
6. **Contradiction, M15:** g* is not a gap threshold on streamed data. On unpredictable (u) landings every form wins
   from g = 4 (V1 -23.7% at g = 4, dig L = 64k); on regular landings V1 LOSES (g = 2: +15..+46%; g = 8 reg: +34.9%)
   while the walk is cheap. The walk pays ~1 mispredict per u-landing (4.2-5.4 ns); the wide forms ~0.1.
7. **Pay rule on the measured dispatch charge: T2 and T3 fail on every twin, T1 holds for R2 only above N = 8.**
   The V1 path costs +0.18..+0.74 ns per call, the WALK path +1.6..+2.4, the W64 path -0.3..+0.3. Rev 3's own
   branch is taken: **no dispatch at B4**, B8 waits for [REGIME-TWIN].
8. **One-byte (M19-M22):** LIBC is best-or-tied on 8-9 of 10 cells of every kind and loses +69..+208% on the dense
   g = 2 cell; no libc-free form dominates it (kit.dom = 0 everywhere), so F1 never fires and D1 stands. NONE never
   beats the walk beyond the floor except `o-bnd` at g = 2 (-7.0%): F0 is effectively dead. The VM hat's V1 saving is
   +0.515 but V1 loses +38% at g = 2 (crossing ~4 B).
9. **M23:** on the letter Q-WR-9's trigger fires (KEEP loses 1.47/1.54 ns, 3.4-3.8%, on TUG g8 early cells); the
   same pre-check wins x49-x112 on absent cells. A price, not a measurement gap.
10. B4's rows (§6): R0 does not fire under the slope token (hex-run's +1.21% is the class max), R1 and R2 stay
    unpaid, R2's `unpaid` WALK is the worst form below the block, F0/F1/P1 stay unbuilt, F2 needs a density condition,
    R5's g* keys are shape-confounded.

## 1. Provenance, gates and what ran (an. 1)

| item | value |
|---|---|
| phases | F1 123 groups (3,154 raw rows, 32 reran), F3 16 groups + 1 requeue visit (453 rows, 5 reran), OB 60 (1,388, 26 reran), TRIG 12 (168, 3 reran); F2 369 rows, F2S 36 rows |
| required phases | wall 61 min; with the optional passes 66.5 min (rev 3 estimated 91-129 min required: the 3-launch floor is below the 3.4 it assumed) |
| rerun rules | within-launch 32 F1 groups (26%), the cross-launch trigger fired in 28 of those 32 (and 23 of 26 OB reruns) |
| counters | available (`perf_event_paranoid=2`): F2 and F2S ran, no SUGGESTION text needed |
| gate | `check.sh` legs R, L, C, U2, P (provenance, 67 signatures) and M (census) all green before any timing |

The 149 grid1 fit groups map to 121 grid2 groups (28 merged D1/D2 twins, `fit_map.tsv`); F1's 123 timed groups
include the dispatch-twin and staircase groups; F3's 16 add `wcls` and the three item-3a cover shapes.

## 2. Contamination accounting (an. 2)

**Window: 19:38:11 to 19:39:30 EDT (epoch 1792193891-1792193970).** A launch overlaps iff its end stamp is inside
the window or within 1 s before its end.

| | count |
|---|---|
| group visits overlapping | **1**: F3 `f3-dig g2-f3-dig-n64k-ginf-Lnone-S` visit 1, 19:38:11-19:38:38 |
| launch rows excluded | **45** of 5,163 (5 launches x 9 arms; 24 rows load1 > 1.5, max 3.12) |
| other phases | 0 (the last F1 launch ended 19:38:10.4, 0.6 s before; OB and TRIG are 20 min later) |
| required cells left without data | **0**: the harness's own requeue re-timed the group at 19:46:33-19:46:49 (3 launches, A/A 0.11%/0.13%, load1 max 1.06) |

What the contamination looks like (median ns, contaminated / clean): walk 12,802/12,422 (1.031), walk#b 1.069, walk#c
1.081, V1 1.034, S1 1.025, A1 1.033, tw0 1.015, tw1 1.033, tw2 1.010; the contaminated visit's A/A is 3.59%/4.80%
against 0.11%/0.13% clean. **A reader who takes the first occurrence of the group in `time_F3.log` reads the
contaminated table**: the log prints both, the second under `# requeue`. After the breach the harness waited 10 x 20 s
(load1 < 1.5) before group 2, so no later group started in the window.

**Dependence.** `f3-dig` n64k feeds beta(1,0,0) for every form, `kit.eps.streamed.slope`, and the F fits. All of them
use the clean visit; nothing depends on the excluded rows.

**Load excursions outside the window (the harness logged none of them; its gate is evaluated at group start and a
BREACH only at end-load >= 3.0):**

| visit | when | rows > 1.5 | effect (against a quiet twin) | treatment |
|---|---|---|---|---|
| F3 `f3-word-eq` n1m | 19:43:18-19:43:46 | 39 of 50, load1 2.08 | walk 1.107x, copies 1.054/1.059; walk copies at 198k/209k/220k in different launches | LOAD-SUSPECT: launch 1 only for walk/V1/S1 (arms before the onset); A1, tw*, sc0 dropped |
| F3 `f3-quad` n64k | 19:44:07-19:44:31 | 41 of 45, load1 2.76 | walk 1.000x in launches 3-5 (A/A 0.08%/0.42%), launches 1-2 +4..+11% | LOAD-SUSPECT: launches 3-5 only |
| F1 `dig g8 L1k u @7` | 19:21:00-19:21:34 | 29 of 50, load1 1.70 | every arm 0.995-1.005x its @0/@31 twins | excluded from statistics, shown flagged in the alignment table |

The first launch of the word-eq visit had load1 1.04 on every row and the second 2.07: the one-minute average lags,
so a row's load1 does not certify the row (the walk-type arms at launch-1 positions 0-4 sit at the quiet level; A1,
tw0 and sc0 at positions 5-9 read +5..+9%, an. 2.5). **F2 and F2S** (`f2perf.sh`) have no quiet gate and write no load
or time column, so the harness could not log a violation; the last OB launch before them read load1 1.06 and the first
TRIG launch after them 1.00. F2 is counts of one pinned process, used as diagnosis only.

## 3. Measured constants (each: regime, layer, floor, confidence)

All values are in `keys.tsv` in the shipped finder's spellings (270 rows). `u` = beta_walk(dig) = **0.1891 ns/B**
(grid1 0.1892). Layers: OFF = walk, V1; W16 = S1 (SSE2); W32 = A1/W64 (AVX2). Confidence: HIGH >= 5x the floor or a
direct slope, MED, LOW (interpolated on a coarse grid or shape-confounded), PROVISIONAL (a load-suspect source).

### 3.1 Noise (the eps tokens, M6) — an. 3

| token | regime (subject; lenclass) | grid2 | grid1 | n | confidence |
|---|---|---|---|---|---|
| `kit.eps.streamed.slope` | streamed member-free single calls, F3 n64k/n1m, A/A #b p90 | **0.113%** (pooled #b+#c 0.126%, median 0.032%, max 0.20%) | 0.173% | 14 groups | MED |
| `kit.eps.findall.l64k` (grid1's definition: all F1 find-all) | streamed find-all, F1 all-mode | **1.316%** (L=64k alone 0.657%; pooled 1.305%) | 3.365% | 83 | MED |
| `kit.eps.streamed.short` (not in the design) | F1 first-mode, n <= 128 | 0.675% (pooled 1.192%) | — | 39 | MED |
| OB first / OB all / TRIG pooled p90 | one-byte cells | 2.723% / 2.384% / 1.687% | — | 24/36/12 | MED |
| `kit.eps.beta.slope` (candidate) | the slope itself: walk copies' beta vs walk, 8 F3 cells | 0.247% p90, 0.319% max (word-eq, provisional; 0.217% without it) | — | 8 | MED |

The walk is the noisy arm: per-launch spread > 5% in 7 of 83 find-all groups (median 0.75%), 10 of 24 OB single-call
groups; its bimodality across launches remains on u-shaped find-all groups, as gridread found.

### 3.2 beta, savings, shapes (M1-M5) — an. 4, 4b, 4c

ns/B (u-relative in `keys.tsv`); saving = 1 - beta_f/beta_walk of the same cell. Regime: F3 member-free single calls,
slope n64k -> n1m. A/A of the slope 0.01-0.32% per cell. Source marked: **p** = load-suspect, restricted as in §2.

| cell | shape (range, eq, cube) | walk | V1 | S1 (W16) | A1 (W32) | save V1 | save S1 | save A1 | grid1 save V1 |
|---|---|---|---|---|---|---|---|---|---|
| dig | (1,0,0) | 0.1891 | 0.1097 | 0.0212 | 0.0107 | **+0.420** | +0.888 | +0.943 | +0.428 |
| hex-run | (2,0,0) | 0.1880 | 0.1857 | 0.0336 | 0.0153 | **+0.012** | +0.821 | +0.919 | +0.014 |
| word-eq (p) | (2,0,1) | 0.1897 | 0.2149 | 0.0418 | — | **-0.133** | +0.780 | — | -0.129 |
| quad (p) | (3,1,0) | 0.1890 | 0.2670 | 0.0541 | 0.0270 | **-0.413** | +0.714 | +0.857 | -0.410 |
| wcls | (3,0,1) | 0.1891 | 0.2768 | 0.0588 | 0.0299 | -0.464 | +0.689 | +0.842 | — |
| c020 `[ad]+=` | (0,2,0) | 0.1892 | 0.1154 | — | — | +0.390 | — | — | — |
| c001 `[xy]+=` | (0,0,1) | 0.1891 | 0.0856 | — | — | +0.548 | — | — | — |
| c110 `[0-9_]+=` | (1,1,0) | 0.1891 | 0.1493 | — | — | +0.211 | — | — | — |
| dfa-hat (derived, an. 4c) | (0,1,1) | 0.1899 | 0.1391 | 0.0221 | 0.0114 | +0.268 | +0.884 | +0.940 | +0.262 |

Confidence HIGH except the (2,0,1) and (3,1,0) rows (PROVISIONAL) and (0,1,1) (MED: derived from the F-corrected
`dfa-hat` ginf-L64k find-all group, no member-free dfa-hat cell exists in grid2). The walk is flat in terms (0.1880-
0.1899), as grid1 found. `kit.saving.V1.WALK.r2` = max over (2,0,0), (2,0,1), (3,1,0) = **+0.0121**.

### 3.3 Single-call fixed part, staircase, block (M7-M12) — an. 5

Regime: one call over a member-free subject of n bytes, fresh streamed buffers (F1 first-mode n8..n128, F3 n64k/n1m).
F = T(n) - beta*n, median over n in {64, 65, 128}; floors 0.01-0.06 ns for n <= 128.

| arm (layer) | F, ns | grid1 F | F at n=48 | grid1 F(48) |
|---|---|---|---|---|
| walk (OFF) | 5.86 | 4.74 | 4.65 | 4.84 |
| V1 (OFF) | 4.38 | 4.18 | 3.49 | 4.17 |
| S1 (W16) | 4.62 | 4.70 | **21.71** | 24.54 |
| A1 (W32) | 5.35 | 4.98 | **12.87** | 14.73 |

V1 - walk, ns (floor): N=8 **-0.18** (0.04), 32 **-2.87** (0.02), 33..46 -2.15..-3.86 (0.00-0.06), 48 -4.98, 63 -6.60,
64 -7.25, 65 -5.96, 128 -13.54, 64 KiB -5,225, 1 MiB -83,294. The staircase rule (§2.6 [C5]) gives **N\* = 8, the
lowest measured point: NOT LOCATED** (grid1: 36 B INTERPOLATED(32,48); M12 at N = 8/32 was +2.3/+0.6 ns, now
-0.18/-2.87). S1 - walk: +0.11 (8), +4.21 (32), +9.00 (48), +13.70 (63), -12.01 (64), -10.07 (65), -24.69 (128).
A1 - walk: +0.24, -2.33, -0.35, +2.79, -11.99, -11.01, -25.30. N\*(S1) = N\*(A1) = 64: the block (T(63) - T(64) = +25.3 ns
S1, +14.4 ns A1, **M11 = 64 B CONFIRMED**). Below 64 B V1 is the best form at both layers (A1 - V1 = +0.42/+0.54/+4.63/
+9.39 ns at N = 8/32/48/63; S1 - V1 = +0.29/+7.08/+13.98/+20.30). Alignment (offset 0/7/31): walk and V1 move < 0.1%
on 64 KiB and <= 1.4% at n=65; S1 -1.6..-1.7% on 64 KiB (an. 5b).

### 3.4 Find-all: c_cold, w_use, unpredictable-landing cost (M13, M14) — an. 6

FITTED per arm on the n = 64 KiB all-mode groups (dig 34, dfa-hat 28, bounded 16), weighted by 1/T:
`T = F*A + w*(U-A) + p*PU + beta*ADV` (A cold activations, U uses, PU planted landings of the u-shaped groups, ADV bytes
advanced). Median relative residual 3.5-7.1%. dig:

| arm (layer) | c_cold = F - F_walk, ns | w warm use, ns | p per u-landing, ns | beta, ns/B | grid1 c_cold / w |
|---|---|---|---|---|---|
| walk (OFF) | (F = 8.94) | 1.60 | **4.26** | 0.2092 | — / 1.67 |
| V1 (OFF) | +2.45 | 2.24 | 2.54 | 0.1377 | +2.47 / 2.38 |
| S1 (W16) | +3.64 | 2.15 | 0.51 | 0.0330 | +2.90 / 2.22 |
| A1 (W32) | +3.41 | 2.18 | 0.51 | 0.0204 | +2.91 / 2.23 |
| A3 (iterator) | +2.23 | 2.28 | 0.58 | 0.0210 | — |

dfa-hat: c_cold +4.26/+4.22/+4.31 (V1/S1/A1), w walk 1.43, p walk 5.02; bounded: +2.39/+3.99/+3.28, w 1.85, p 4.50.
V1's c_cold and w are CONFIRMED; the wide forms' c_cold is +17..+25% above grid1's. p is the new term: the walk pays
4.3-5.0 ns per unpredictable landing, V1 2.5-3.5, the wide forms 0.5-1.3. Confidence MED.

### 3.5 g* is a predictability threshold (M15) — an. 6b, 6c, 6d

Streamed, all-mode, n = 64 KiB, % against the walk (verdict). g = 2 is a regular landing offset, g >= 4 uniform-random:

| dig L=64k | g=2 reg | g=4 | g=8 | g=16 | g=32 | g=64 | g=256 | inf |
|---|---|---|---|---|---|---|---|---|
| V1 (OFF) | +14.9% R | -23.7% W | -21.9% W | -9.7% W | -14.7% W | -13.8% W | -30.0% W | -40.6% W |
| S1 (W16) | +0.6% N | -58.9% W | -62.8% W | -63.7% W | -69.4% W | -71.5% W | -77.1% W | -85.2% W |
| A1 (W32) | +0.5% N | -59.6% W | -64.2% W | -65.9% W | -71.7% W | -74.7% W | -82.5% W | -90.8% W |

Predictability at equal mean gap (dig, L = 1k, ns/pass; V1/S1/A1 against the walk): g = 8 u: walk 63,308, V1 -23.6%,
S1 -62.6%, A1 -64.0%; **g = 8 reg: walk 21,107, V1 +34.9% R**, S1 -1.2% N, A1 -4.3%; g = 8 burst: V1 -1.8%. F2: the
walk takes 0.97 (g8) / 1.44 (g32) branch misses per u-landing, 0.009 per regular landing, and V1 0.5/1.1, A1 0.12/0.27;
the walk's u-minus-reg excess is 5.39 / 4.21 ns per extra miss (26.6 / 24.4 cycles). **g\* from grid1 (V1 10.8-16.7 /
3.0-3.3 / 21.5 B) is NOT reproduced:** on u-shaped data V1 wins from g = 4 for dig L >= 1k (g\* = "all-win"), crosses at
~33-37 B for dfa-hat L = 64k/1k and ~64 B for bounded, and is never faster at dfa-hat L = 32. These crossovers are
shape-confounded (confidence LOW). By regime (an. 6c; DINGHY = bytes per activation < 64, TUG = bytes per landing <
18.5): V1 at OFF is W/N/R 5/2/8 in dig DINGHY, 10/0/3 TUG, 11/0/0 LINER; A1 at W32 is 8/0/7, 11/2/0, 11/0/0. Against
V1, the SIMD-on forms win in 72 of 78 (A1) and 70 of 78 (S1) find-all groups, in 9 of 10 at g = 2 (an. 6c2).

### 3.6 Dispatch charges and the scaffold (M16-M18) — an. 7

Twins: tw0/tw1 = the WALK+V1 scaffold with f forced to WALK/V1 (layer OFF, 2 forms); tw2 = WALK+V1+W64 with f forced
to W64 (layer W32, 3 forms). Charge = twin - single-form artifact in the same interleaved group. Per activation, dig
member-free single calls, N <= 128 (floors 0.01-0.06 ns):

| twin (path) | charge per call, ns, range | UPPER bound | slower beyond the NULL rule at |
|---|---|---|---|
| tw0 - walk (WALK path, OFF) | -0.08 (N=8), +1.63..+2.44 (N >= 32) | +2.44 | 6 of 7 points |
| tw1 - V1 (V1 path, OFF) | -0.14 (N=8), +0.18..+0.74 | +0.74 | 6 of 7 |
| tw2 - A1 (W64 path, W32) | -0.29..+0.32 (N >= 64: -0.11/+0.05/-0.29) | +0.32 | 3 of 7 |

Per use, dense dig groups at n = 64 KiB: tw0 -0.53..+0.59 ns, tw1 +0.06..+0.48, tw2 +0.04..+0.35, slower beyond the
NULL rule in 6/8/10 of 11 groups; **the charge is not proportional to uses** (about 1-2 us per pass at U = 2,000 and at
U = 32,000). The helper-in-a-struct scaffold alone (sc0 - walk, member-free n64k): -5.8..+3.8 ns, <= 0.05% of the call;
sc0's short-call cost is not measured (it exists only on 64 KiB/1 MiB groups). **M18 is a long-call bound.** Confidence
MED (upper bounds). Not measured: any W16 twin, the V1/WALK path through a 3-form chain, kinds other than DFA_SCAN.

### 3.7 One-byte arms and NONE (M19-M22), VM hat — an. 8, 8b

Five DFA kinds + the VM hat, 4 member-free lengths + 6 gaps each, streamed, OFF layer only (LIBC is the host's
ifunc-selected SIMD `memchr`: 0.0074 ns/B, so the "OFF" label does not describe it). Per kind, F (ns) and beta (ns/B):

| arm | F | beta | note |
|---|---|---|---|
| LIBC | 4.27-5.82 | 0.0073-0.0075 | best-or-tied on 8-9 of 10 cells of every kind |
| WALK at \|S\|=1 | 3.72-5.64 | 0.1862-0.1879 | best only at g = 2 (within a few % of the loop and NONE) |
| V1 one-term (stateless; o-vm: the compiler's own stateful text) | 2.90-6.44 | 0.0891 (o-vm 0.0910) | best at n = 8 on o-fwd, o-hyb, o-vm only |
| generic loop | 3.52-5.40 | 0.1837 (o-bnd 0.3658) | ties the walk at g = 2 |

- **D1 regret** (libc vs the best timed arm, g = 2): o-fwd +71%, o-bnd +76%, o-hat +146%, o-hyb +72%, o-back +208%, o-vm
  +107%; at g >= 8 libc is best or tied (-50..-96% against the walk). libc overtakes the walk at **g ~ 4.1-6.1 B**
  (INTERPOLATED(2, 8), two straddling cells, confidence LOW).
- **kit.dom.<f>.LIBC.<kind> = 0 for every libc-free form and kind** (each is slower than LIBC beyond the NULL rule on
  8-10 of 10 cells): F1 has nothing to displace D1 with.
- **NONE** vs the walk: R at every gap on o-fwd (g=2 N), o-hat, o-hyb (g=2 N), o-back; W only on o-bnd at g = 2 (-7.0%);
  +185..+497% at g >= 32. `kit.gnone` is -1 (never) for DFA_SCAN fwd, DFA_HAT, HYB_PF, 2 B for DFA_SCAN.bounded
  (tie-inclusive 2-8 B).
- **VM hat (F2):** `kit.saving.V1.WALK.VM_ATTEMPT.r0e1c0` = **+0.515** (single-call slope), 454x kit.eps.streamed.slope;
  find-all against the walk: g = 2 **+38.3% R**, g = 8 -39.6%, 32 -33.5%, 256 -44.1%, 4096 -51.5%, inf -53.9% (crossing
  ~4 B, INTERPOLATED(2, 8)). The row as written (a beta saving only) would ship the g = 2 loss.

### 3.8 The pre-scan probe (M23) — an. 9

KEEP (default) vs DROP (`-fno-req-byte -fno-req-run`), DFA route, first-mode over 64 KiB, byte early / late / absent,
g = 8 (TUG) / 32. KEEP - DROP per call: early +1.47 (dig g8), +1.66 (g32), +1.54 (word g8), +1.82 (g32) ns = 3.4-6.8%
of a 25-46 ns call, beyond the floor; late -297..+359 ns (0.03-0.7%, NULL); absent **-46,730 / -23,318 / -53,424 /
-30,921 ns (DROP loses x49-x112)**. Q-WR-9's trigger ("a TUG cell measured losing for want of it") fires on the letter
on the two TUG g8 early cells; P1's price is a design question (§6).

### 3.9 Real text, perf only (F2S) — an. 6e

User-space cycles per pass against the walk (NOT timed, no A/A): bounded on prose V1 +16.7% / A1 +19.3% (the named
residual), docs +5.0/+3.3, code +4.0/+1.5; dfa-hat prose V1 +8.9% / A1 -13.6%; hex-run V1 +0.7%, A1 -3.0%, A3 -19.8%.

## 4. Predictions (§9.3) and rev 3's assumptions against the slot (an. 10)

| # | rev 3 statement | verdict | numbers |
|---|---|---|---|
| P1 | R0: hex-run and word-eq find-all groups NULL against the walk at OFF | **not scorable as written** (grid2 times no such find-all group). Under the shipped slope token R0 does NOT fire (class max +1.21% > 0.113%), hex-run goes to R7 (a +1.2% member-free GAIN), word-eq/quad/wcls reach WALK through R7w. True only under the find-all token (1.316%) | §3.2 |
| P2 | R7 on (1,0,0), (0,1,1) and item 3a's shapes: pick - walk <= -floor at every L >= the crossover | **holds member-free; FAILS in a named region** of find-all: dense regular groups (g = 2, reg g = 8), L <= 8, and L = 32 at g >= 16 for dfa-hat (V1 +15..+46% at g = 2); 4 NULL ties at g = 32 L >= 1k (bounded, dfa-hat). 3a: V1 wins by 39/55/21%. The residual SHIPS: R5 cannot fire without a measured E | an. 10 |
| P3 | R1 if paid | moot: no interval, T1/T2/T3 fail | §5 |
| P4 | regret on the grid | not scored (no hex-run/word-eq grid rows) | — |
| P5 | dfa-hat prose contradicts R5 | consistent, perf only: V1 +8.9% / A1 -13.6% cycles; not timed | §3.9 |
| P6 | no SIMD-on prediction at B4 | confirmed vacuous; SIMD-on reported for B6 | §3.3, 3.5 |

| # | assumption | verdict |
|---|---|---|
| A1 | `kit.eps.streamed.slope` = F3 A/A p90 (0.173%) | CONFIRMED in kind (0.113%); regime split real (11.6x); the slope-based noise is 2.2x the token |
| A2 | M9: V1 crossover 36 B INTERPOLATED(32,48) | **CONTRADICTED**: N\* <= 8; V1 faster at every N >= 8 |
| A3 | M15 g\* values | **NOT REPRODUCED** as a gap threshold (§3.5) |
| A4 | M13/M14 | V1 CONFIRMED; wide forms' c_cold +17..+25% higher |
| A5 | F ~ 4.2-5.0 ns at n >= 64; sub-block tail | CONFIRMED (V1/S1/A1); the walk is +1.1 ns on streamed buffers |
| A6 | beta by shape | CONFIRMED to 0.1-3.3% on 11 comparable cells |
| A7 | pay-rule operand spellings (finder.c, provisional) | see §5: orientation alt - pick; four keys no earlier set carries; W16 has no twin |
| A8 | "if the twins fail T1-T3, no dispatch at B4" | branch TAKEN |
| A9 | R2 pick V1, unpaid WALK | the unpaid pick is the worst form below the block (walk - V1 = +4.98/+6.60 ns at N = 48/63); W64 vs walk -0.35/+2.79 |
| A10 | D1 libc default | measured: +69..+208% at g = 2, best elsewhere; STANDS |
| A11 | F2 V1 at the VM hat | saving +0.515, but +38% at g = 2 |
| A12 | F0 NONE below g_none | g_none <= 2 B: effectively never |
| A13 | P1 waits for Q-WR-9's trigger | fires on the letter (1.5 ns); price unasked |
| A14 | grid1 prototype figures not comparable (D167) | CONFIRMED (g\*, F_walk +1.1 ns, F1 A/A 3.365% -> 1.316%, M9) |
| A15 | 3.4-5 launches, 91-129 min | 3 launches (+2 on 32 F1 / 26 OB groups), 61 min required |

## 5. The pay-rule operands and the T1-T3 verdicts (an. 7b)

Operands, kit-grid@2, in the finder's spellings (`finder.c pay_fill`; PROVISIONAL there until the cards fix them), all in
`keys.tsv`; "walkbytes" = ns / u:

| key | meaning | source here |
|---|---|---|
| `kit.delta.<ALT>.<PICK>.<KIND>.n<N>` | cost(ALT) - cost(PICK), single call at N = 8, 32, 48, 63, 64, 65, 128 | an. 5.4 |
| `kit.dfloor.<ALT>.<PICK>.<KIND>.n<N>`, `kit.ffloor.<ALT>.<KIND>.n<N>` | the group's A/A floor at N (max of #b, #c) | an. 5.4 |
| `kit.cdisp_call.<KIND>.<LAYER>.<NFORMS>`, `kit.cfloor.*` | UPPER bound over paths and N <= 128: OFF.2 +2.44 ns (WALK path; V1 path +0.74), W32.3 +0.32 ns; floor 0.04 | an. 7.1 |
| `kit.cdisp_use.*`, `kit.ufloor.*` | UPPER bound per use: OFF.2 +0.59 ns, W32.3 +0.35 ns; worst group floor 0.43 ns/use | an. 7.2 |
| `kit.cscaffold.WALK.DFA_SCAN` | status null: <= 5.8 ns on 64 KiB calls | an. 7.3 |
| `kit.wfloor.WALK.DFA_SCAN` | median per-use A/A floor of the dig dense groups | an. 7b |

Two spelling facts the rev 3 text leaves implicit: (i) `delta` is oriented alt - pick, so R2 (pick V1, alt WALK) reads
`kit.delta.WALK.V1`, a key grid1's interim set does not carry (it holds V1.WALK only, R1's orientation); (ii) the
charge keys name no path, so they carry the maximum over the paths of one (layer, nforms) and the path-specific
values are extra rows (`...OFF.2.WALKPATH`, `...V1PATH`, `...W32.3.W64PATH`).

- **T1 (R2, interval [0, 64), pick V1, alt WALK):** the V1-path charge upper bound +0.74 ns + cfloor 0.04 = +0.78 ns.
  saving(walk - V1) - dfloor = +0.14 (N=8, **FAILS**), +2.85 (32), +4.94 (48), +6.57 (63) (all hold); every staircase
  point 33..46 holds. T1 FAILS on the interval's first measured point. **R1** (pick WALK below N\*, alt V1): N\* = 8,
  the saving of WALK over V1 is negative at every measured N, T1 FAILS (and would fail at 36 B too).
- **T2:** charge + cfloor = +2.48 (tw0), +0.78 (tw1), +0.36 (tw2) ns against the next form's floor at b = 64 of
  0.010 ns: FAILS on every twin (tw2 alone is within the floors or faster at N = 64, 65, 128; its upper bound over N <=
  128 is not).
- **T3:** the twin is slower beyond the NULL rule in 6/8/10 of 11 dense groups: FAILS on every twin.
- **Decision (rev 3 §2.5, §3.2): B4 ships NO dispatch;** R1 and R2 stay unpaid rows; B8 waits for [REGIME-TWIN].

## 6. What B4's table rows should take

Row ids per rev 3 §1.3. "Key" = the `keys.tsv` row.

| row | takes from this slot | note |
|---|---|---|
| R0 `r2` | `kit.saving.V1.WALK.r2` = +0.0121 (hex-run) | fires only if eps >= 1.21%: not under `kit.eps.streamed.slope` (0.113%), yes under the find-all token (1.316%). The class MAX hides three losing shapes (-13%, -41%, -46%); they reach WALK via R7w. B4's census must say which token and that R0 does not fire |
| R7 `liner` | `kit.saving.V1.WALK.<shape>` for 9 shapes (§3.2); fires for (1,0,0), (2,0,0), (0,1,1), (0,2,0), (0,0,1), (1,1,0); not for (2,0,1), (3,1,0), (3,0,1) | (2,0,0)'s margin is 10.7x the token and 4.9x the slope noise. The (2,0,1)/(3,1,0) rows are PROVISIONAL but the sign is not (13% and 41%) |
| R7 at W16/W32 (B6) | S1/A1 savings 0.69-0.89 / 0.84-0.94; W64 beats V1 in 72 of 78 find-all groups, 9 of 10 at g = 2; below 64 B V1 is the best form | the W64 interval starts at N = 64 (block) |
| R5 `gstar` | keys exist only for L = 32 (dig V1 53.3 B) and dfa-hat/bounded V1 (33-64 B); all other cells "all-win" (-1) | shape-confounded: record `u-shape` in the key's provenance or leave absent; R5 reads E at MEASURED only, so the default compile is unaffected |
| R1 | no interval (N\* = 8 not located) | row dropped; `kit.xover.V1.WALK.DFA_SCAN` = 8 B recorded as an UPPER bound |
| R2 | T1 fails at N = 8, T2/T3 fail | `unpaid` should be the terminal (W64) / drop the row, NOT WALK: WALK is the worst form below the block (+4.98/+6.60 ns vs V1 at N = 48/63) |
| R8 | `kit.xover.W64.WALK` = 64 B; W64 beats V1 at every g tested (g8 not located: < 2 B) | find-all L = 32 included |
| D1 / D1c | default stands; LIBC regret +69..+208% at g = 2, best elsewhere | `kit.xover.LIBC.WALK` 4.1-6.1 B (LOW) |
| D1w | WALK default for the VM hat stays until F2 | |
| F0 NONE | `kit.gnone` = -1 / 2 B | do not build (no customer, D77) |
| F1 | `kit.dom` = 0 for every libc-free form and kind | do not build (nothing to displace D1 with) |
| F2 `vm-hat-1b` | `kit.saving.V1.WALK.VM_ATTEMPT` = +0.515 | add an E.g >= ~4 B condition or wait for a measured E; as written it ships +38% at g = 2 |
| P1 priced pre-scan | `kit.gate.byte1.DFA_SCAN.early/late/absent` = +8.1 / 0 / -247,000 u*B | operands measured; the rule is not a measurement question (Q-WR-9) |
| pay rule | §5 | no dispatch |

SIMD-off AND SIMD-on: every OFF verdict above has its W16/W32 counterpart in the beta, F, c_cold, g* and wide-vs-V1
tables; the one-byte arms and NONE exist at OFF only (no one-byte W64 arm was specified); the dispatch twins cover OFF
(2 forms) and W32 (3 forms), not W16.

## 7. Findings the brief did not ask for

1. **The load average lags a disturbance by a launch.** Row load1 cannot certify a row (§2); the harness's group-start
   gate misses a mid-group breach below 3.0. A launch-level load filter would have saved neither word-eq n1m nor quad
   n64k; the A/A and the quiet-twin ratio are the evidence.
2. **R0's class key is a MAX.** One shape that wins by 1.2% suppresses R0 for shapes that lose by 13-46%; correct
   results still come out through R7w.
3. **F2's key reads a slope and ignores density,** so the VM hat's g = 2 loss is not priced.
4. **The WALK path through the dispatch is the expensive one (+2.4 ns),** the V1 path 3x cheaper, the W64 path ~0.
5. **LIBC's SIMD comes from the host's libc,** so "SIMD-off" does not describe a LIBC row; the `libc-mismatch` flag
   (D167 add. 3) matters most for exactly these rows.
6. **The dense `reg` cells make the walk a good form,** which grid1's repeated condition also produced; streaming alone
   did not remove it: predictability is the axis.
7. F2S shows `bounded` on prose losing +17-19% cycles for the wide forms (the named residual), measured only as counts.

## 8. OWED

1. **Re-time the two load-suspect F3 cells in a quiet slot** (word-eq n1m and quad n64k, plus their n64k/n1m partners
   so the slope is within one condition), about 2 minutes. They bound the (2,0,1) and (3,1,0) rows, word-eq's A1 beta and
   its twin charges:

       cd <slot> && OUT=<slot> PHASE=F3 CELLS_RE='^f3-(word-eq|quad)$' RAW_TAG=F3rr \
           PASS_STATUS=<slot>/time_F3rr.status CPU=14 LAUNCHES=3 \
           bash docs/dev/lanes/grid2/time.sh > <slot>/time_F3rr.log

   `<slot>` = `worktrees/memfn-slot/grid2` (its `bin/` is intact); the script path is `lane/grid2r3`'s. `PASS_STATUS`
   and `RAW_TAG` stop it overwriting `time_F3.status` / `raw_F3.tsv`. Expected: word-eq (2,0,1) A1 beta ~0.019-0.021;
   quad (3,1,0) V1/S1/A1 unchanged.
2. **Measurements the slot did not contain:** a W16 dispatch twin; the V1/WALK path through a 3-form chain; a
   member-free dfa-hat cell (the (0,1,1) shape is derived); dispatch charges at DFA_HAT/HYB_PF/VM_ATTEMPT; a gap grid
   between 2 and 8 B (libc/V1-at-VM-hat crossings are INTERPOLATED(2, 8)); and any hex-run/word-eq find-all timing.
3. Not owed because the contamination left a required cell empty: none.

## 9. INTERPRETATION (mine, not read from a number)

- The compiler's V1 text differs from grid1's V1 arm, which would explain M9; this slot cannot attribute it.
- The kit branch's walk equals MAIN's walk byte for byte (the B4 baseline).
- The walk's 5-10% bimodality at load1 2 is another process contending for the core or its SMT sibling.
- The late `trig` cells' sign and the late-cell medians in `keys.tsv` are NULL, not trends.
- The 26 cycles/miss is an average over the u-minus-reg difference, not a pipeline constant.

## 10. Charter vs delivered

| charter item | delivered |
|---|---|
| READ the completed slot, analysis only, no timing/make/heavy work | yes: python over TSVs, `nice` not needed (< 1 s per run); no build, no make |
| measured constants and predictions §5.4/§9.3 ask for, each with regime, layer, floor, confidence | §3 and `keys.tsv` (270 rows; layer, floor and confidence columns); M24 not measurable here |
| confirm/contradict rev 3 (eps token, pay-rule operands) | §4 (A1-A15), §5 |
| contamination accounting: every F3 group/measurement overlapping 19:38:11-19:39:30, excluded, count, dependence | §2: 1 visit, 45 rows; 0 required cells lost |
| required cell without data -> exact re-run OWED | none lost; a separate re-run for the two load-suspect cells is OWED (§8) |
| check F1 and F2 for QUIET/loadmax violations the harness logged | §2: F1 none logged (one unlogged 1.70); F2 has no gate or load record, bracketed quiet |
| what B4's table rows should take | §6 |
| verdicts: named regime, absolute deltas against a floor, both layers | §3 tables (regime and floor columns), §6 last paragraph |
| scripts under `docs/design/memfn/r17b_prime/grid2read/` with a CLAUDE.md, SHA256SUMS | yes (`grid2read.py`, `grload2.py`, `analysis.txt`, `keys.tsv`, `SHA256SUMS`, `CLAUDE.md`) |
| docs/dev/lanes/CLAUDE.md index entry | yes |
| commit on lane/grid2read, short summary | tip sha in the handback |
