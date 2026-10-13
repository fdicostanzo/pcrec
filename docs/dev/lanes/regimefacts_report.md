# regimefacts — ocean liners and dinghies: the fixed-vs-per-byte split from data that already exists

Lane regimefacts, 2026-10-13, branch `lane/regimefacts` (off main 0e370bb04). FACTS ONLY: no timing run, no
build of a matcher, no design, no recommendation. Every number below is read from existing logs or
computed from them by the scripts in `docs/dev/lanes/regimefacts/` (pure, no clock, `python3 -I`).
Outputs are committed beside the scripts (`*.out`, `population.tsv`).

Frank's framing: one set of rules for large/sparse subjects (per-byte cost dominates) and small/dense ones
(per-call / per-use / per-match FIXED costs dominate). Model every number is read through:

    T(find-all pass) ≈ calls·C_call + uses·C_use + matches·C_match + bytes·c_byte

`uses` = kit `next_candidate` / scan activations. n* = subject length at which the fixed terms are half of
T for ONE call; g* = bytes between consecutive matches (or uses) at which the per-match fixed terms are half.

## 0. Inputs, boxes, and the two things never to mix

| source | what it is | box | read how |
|---|---|---|---|
| S1 vecspike | `worktrees/memfn-slot/spike1/{time.log,counts.tsv}` (read-only); reading at `git show b00365e13:docs/dev/lanes/vecspike_reading.md` | Linux dev box, Ryzen 7 7700X (**Zen 4**), pinned core 14, 5 launches, A/A pair per group | re-fit by `fit_vecspike.py` |
| S2 r17loss | `git show lane/r17loss:docs/dev/lanes/r17loss_report.md` (per-use deltas at PF/DFA/VM sites, from slot25c's log) | same box | quoted, §2.3 / §3.3 / §4 of that report |
| S3 origsurvey | `docs/dev/lanes/origsurvey_report.md` (landings vs bytes) | same data | quoted |
| S4 bench | `pcrec-bench/reports/*handoff-6b2dbd3e.subject-grain.tsv` (and email at `landing-b8337c33`, bounded testee `pcrec_b8337c33`: the 6b2dbd3e bounded/email records carry no pcrec row), joined with `bench/<set>/manifest*.tsv` (subject lengths) and `bench/<set>/expectations.tsv` (oracle `nmatches`) | ubuntubudu, Ryzen 5 1600 (**Zen 1**), pinned core | `bench_population.py`, `floor_fits.py`, `classify.py`, `setgrain.py`, `density.py` |
| S5 misc | revpred / o101ans / k82diag / alphas* / r1read / rewtwin reports (fixed-term facts, quoted) | both | quoted |

**The two boxes are different CPUs (Zen 4 vs Zen 1) with different drivers (the kit's `drv.c` loop vs the bench's
`timed_run`).** O-101/o101ans measured the transfer between them as "a ratio 2.2" on one cell (f-tag: Zen 4 +7.9
ns, bench +17 ns) and the revend design carries "x1.6 plus a 5 ns bench tax", both labelled UNMEASURED transfer
terms. So: S1/S2 constants are Zen 4 per-form constants; S4 constants are Zen 1 bench constants; an n* is only
a length when both its terms come from the same row of the table in §1. Where §3 mixes (the bench-population
bands) the mixing is stated.

## 1. (a) Constants: fitted / derived, per site, form, engine

Noise-floor rule in the kit logs: the A/A pair (V0 launched twice per round). Over the 116 vecspike groups
A/A is median 0.15% of V0, p90 2.3%, max 60.8% (the 64 KiB find-all rows are bimodal, vecspike_reading §1.3).
Bench noise: the null-control band of reporter v26, ±1.1–3.2% depending on regime × baseline scale
(capability report, 6b2dbd3e). `conf` = my confidence in the number as a measurement of that term.

### 1.1 Zen 4, kit harness: sparse whole-subject scan (calls = 1, uses = 1, density 0)

Cell `dig` (`[0-9]+x`), mode `all`, subjects `short`(40 B)/`prose64k`/`prose1m`; rows from `time.log`
(`fit_vecspike.out` part 1). Line through (40 B, 1 MiB); the 64 KiB point is the held-out check.

| form (site: PF DFA scan) | F = intercept (ns) | c_byte (ns/B) | n* = F/c | 64 KiB pred vs meas | conf |
|---|---|---|---|---|---|
| V0 walk (256-B table, the baseline) | 4.29 | 0.19002 | **23 B** | +0.2% | high on c (4 routes agree, below); F is one point (the 40-B row) |
| V1 SWAR 8 B (R17-b `new`) | 3.09 | 0.10876 | **28 B** | −1.4% | high c; F one point |
| S1 SSE2 W=64 (4×16 B) | 20.45 | 0.02060 | **993 B** | +1.8% | high c; F one point, includes the sub-block tail of a 40-B subject |
| A1 AVX2 W=64 (2×32 B) | 10.54 | 0.01081 | **975 B** | +7.7% | high c; F one point, same tail caveat; the 64 KiB miss is 7.7% (cache/prefetch regime, not separated) |

Walk c_byte cross-checks (3-term OLS t = a·calls + u·uses + b·n, relative-error weighted, `fit_vecspike.out`
part 3): `dig` 0.184, `dfa-hat` 0.189, `vm-hat-1` 0.190 ns/B (median relative residual 0.10 / 0.20 / 0.01).
So **c_byte(walk) = 0.19 ns/B on Zen 4 from four independent routes, within 3%.** `vm-hat` (7 rows) fits
0.427 with a negative `calls` term: that fit is not usable (collinear), reported as such.

Single-call single-use totals in the same harness (`first` mode, hex-run/bounded short subject): V0 6.4–7.0 ns,
V1 7.2–9.2 ns, S1 25–31 ns, A1 14–17 ns: the whole time of a dinghy call is the fixed term, and the SIMD
forms' fixed term is 2–4× the walk's.

### 1.2 Zen 4, kit harness: per-use and per-match fixed terms

| term | value | derivation | conf |
|---|---|---|---|
| C_use(walk): candidate hand-off to the DFA | 2.65 (`vm-hat-1`), 4.14 (`dfa-hat`), 5.69 (`dig`) ns/use | 3-term OLS above | **low–medium**: range 2×; `calls` term not separable (1.04 / −3.02 / 1.61 ns, sign unstable) |
| C_call + C_use + C_match, find-all, ONE use per call, V0 | `hex-run` 10.5 ns, `bounded` 17.0–19.8 ns per match | ns/call at 1 MiB (prose/docs/code) minus gap·0.19: `fit_vecspike.out` part 2; gap 5.5–8.2 B | medium (1 MiB rows only; the 64 KiB rows are bimodal) |
| same, V1 / A1 | `hex-run` 10.4–10.8 / 9.7–10.1; `bounded` 20.8–21.2 / 20.2–21.3 ns | same | medium |
| form delta, new − walk, per use (r17loss §3.3) | PF cold +2.06, PF warm +1.09, VM hat −0.15 ns/use | weighted LSQ over 112 reached rows, R² 0.79, 5/109 sign errors | medium (single box, "not quiet" load1 0.72; rows bimodal ±50%) |
| per skipped byte, new − walk (r17loss §3.3) | 1 term −0.092, 2 terms −0.051 ns/B (measured directly: −0.080 / −0.050 ns/B on two whole-subject rows) | same fit; 3- and 4-term never sparse in the table | medium; 3+ terms UNMEASURED |
| break-even skip per use, form vs walk | 22 B (PF 1 term cold), 21 B (PF 2 terms warm), ≈0 (VM hat) | a/|b| | medium. In density: ~**50,000 ppm** of S per subject byte |

`C_call`, `C_use`, `C_match` are NOT separately identifiable from this data wherever uses ≈ calls ≈ matches
(`hex-run`, `bounded`, `dig` find-all): the OLS returns negative or sign-unstable terms there. Only the SUM per
match is a number. `dfa-hat` (1 call, up to 75,836 uses) is the only cell where uses ≫ calls and gives a
usable C_use; it gives 4.1 ns.

### 1.3 Zen 1, bench: pcrec `auto-caps` (pin 6b2dbd3e), the `floor` pattern and the litrun floor series

`floor_fits.out`. `floor` is a one-byte memchr-class search (stamps: the bench's own floor row; the bench
describes it as the control "a small fixed set of short-call cells timed first in every window").

| term | value | derivation | conf |
|---|---|---|---|
| empty-call floor F, short regime | **8.86 ns** (4-B subject, 60+ `floor` cells in altwide agree to ±0.01), 13.47 ns (222–230-B subject, same pattern) | `floor` rows of `altwide` short/match-compliance | **high** (stddev 0.0 in the report) |
| immediate-return call | 5.61 ns | revpred §4, O-91's own floor: `base10num-near-miss` on the 1 MiB / 16 KiB tails | medium (revpred states it, I did not re-derive) |
| c_byte, memchr class, 1 MiB | **0.01682 ns/B** (17,632 ns / 1 MiB) | `floor`/`floor-byte` large rows: 64 KiB 0.01690, 256 KiB 0.01670, 1 MiB 0.01682 | high at ≥ 60 KiB |
| c_byte, small | 0.01471 (4 KiB), 0.01374 (16 KiB); slope 222 B→4 KiB = 0.0121 | same rows | medium: below 16 KiB the F term is NOT separable from c (60.2 ns at 4 KiB < F + c·4096 = 77.7) |
| n*, memchr class | **527 B** (8.86 / 0.01682); 334 B with F = 5.61; 738 B with c = 0.0121 | derived | medium: range 334–738 B |
| per-landing cost, find-all, memchr class | **14.2 ns / landing** | litrun `floor` `fbf-lK`, 64 KiB, K = 2…31: ns·K = 931–936k constant, i.e. ns = 14.2 × (65536/K); all 8 points within ±0.5% | medium-high for the arithmetic; the reading "one landing per K bytes" is MY inference from the 1/K law (bench question Q5) |
| the same series at K = 40 | 18.9 ns / landing (30,941 ns, not 23.3k) | same | the law breaks at K = 40 (a different form past 32 B); not explained here |
| `mat-lK` (litrun `floor`, 64 KiB, other form) | 1,105–1,113 ns for every K | ≈ 0.0169 ns/B, K-independent: a pure per-byte pass | high |

Immediate-return 5.61 vs `floor` 8.86: the difference, 3.25 ns, is one memchr call; the kit's memfn probe
reports glibc memchr's call term as "~3.4 ns" (memfnreq_report). That is a consistency check, not a fit.

### 1.4 Other fixed-term facts already on record (quoted, not re-derived)

| fact | value | source | box |
|---|---|---|---|
| K82 pair arm's short-call floor (two fresh `memchr` calls) | ~10.06 ns, flat | k82diag §2, k82alpha | Linux glibc, Zen 4 |
| K90 L3, per-call seek on a hit at offset 0 | +14…+17 ns | alphas2, o101ans | Zen 4 |
| [OPT-VEDGE] entry term | +1.3…+8.7 ns past the floor on short non-matching subjects; `floor` +1.1…+1.6 ns per subject on four bench sets | r1read, o83read | Zen 4 / bench |
| start-set DFA hat entry term | +2.6…+9 ns on absent-byte `memchr`-floor cells (0.4%) | alphas3 | Zen 4 |
| rev-end walk vs forward route, short regime | "~9 ns vs 3.8 ns; 66 of 75 subjects +5.5 ns each" (K103); today 1.9–2.6 ns vs `-fno-rev-end` 3.7–4.6 ns per call | o101ans, rewtwin | Zen 1 / Zen 4 |
| L1 re-entry cost | NOT a fixed per-call term: scales with landmark stops (4 vs 2 memchr calls on `f-tag`) | o101ans fact 5 | both |
| revpred's own F range for a rev-end call | low 5.6 ns, high 20 ns (floor + 5 ns function + 10 ns instrument slack) | revpred §4 | bench |
| bench driver tax | a driver-main edit moved short calls 40–50 ns (the reason for `timed_run`) | methodology "The timed loop" | bench |

## 2. (b) Crossovers

### 2.1 Per-call: subject length n* at which fixed = half (one call, one use, no further landings)

| form | n* | basis (§1) | what moves it |
|---|---|---|---|
| scalar walk, Zen 4 | 23 B | 4.29 / 0.190 | – |
| SWAR 8 B, Zen 4 | 28 B | 3.09 / 0.109 | – |
| SSE2 W=64, Zen 4 | 993 B | 20.45 / 0.0206 | F includes a sub-block tail at n = 40 |
| AVX2 W=64, Zen 4 | 975 B | 10.54 / 0.0108 | same |
| memchr class, Zen 1 bench | 527 B (334–738) | 8.86 / 0.01682 | F=5.61 → 334; small-subject slope → 738 |
| scalar walk with the BENCH floor (mixed boxes: Zen 1 F, Zen 4 c) | ~47 B | 8.86 / 0.19 | c on Zen 1 unmeasured; labelled mixing |

Read: **below ~25–50 B every form is a dinghy (fixed ≥ half of the time) — a 40-byte subject on the AVX2 form is 96%
fixed cost; between ~50 B and ~1 KB the scalar walk is already a liner while the fast forms are still dinghies;
above ~1 KB (5 KB for ≥ 90% per-byte) every form is a liner.** The SIMD forms trade a 2–4× larger fixed term
(10–20 ns vs 3–4 ns) for a 10–18× smaller per-byte term.

### 2.2 Per-match / per-use: gap g* (bytes between consecutive matches or uses) at which per-match fixed = half

| case | per-match fixed | c_byte | g* | density at g* | conf |
|---|---|---|---|---|---|
| walk, `hex-run`, Zen 4 | 10.5 ns | 0.190 | 55 B | 18 matches/KiB (18,000 ppm of matches/byte) | medium |
| walk, `bounded`, Zen 4 | 17.0–19.8 ns | 0.190 | 90–104 B | 10–11 /KiB | medium |
| form swap new-vs-walk at a PF scan (r17loss) | a_PF = 1.09–2.06 ns/use | b = 0.051–0.092 ns/B skipped | 21–22 B | ~50,000 ppm of S per byte | medium |
| memchr class, litrun floor, Zen 1 | 14.2 ns | 0.01682 | **845 B** | 1.2 landings/KiB | medium (landing = my inference) |

Read: per-match overhead is 10–20 ns on both boxes (10.5–21 ns Zen 4; 14.2 ns Zen 1 for the cheapest form),
which equals the per-byte cost of 55–100 B of scalar walk or 850 B of memchr. **A find-all pass is
per-match-dominated whenever matches (or landings) come more often than once per ~50–100 B for the scalar forms,
once per ~850 B for the memchr class.** That is a property of the subject's density, NOT of its length: a
1 MiB subject with a match every 6 B (hex-run prose1m: 166,490 matches) is a dinghy pass in a liner subject, 94%
fixed by this fit, while a 64 KiB sparse scan is 99.99% per-byte.

### 2.3 The two ways the bytes≠landings gap shows (S3)

`uses` equals S-runs ("landings") almost exactly (bounded prose64k 10079 vs 10079; hex-run 10454 vs 10454;
dig digits64k 9055 vs 9057), so the fixed-term counts are landings, not member bytes. `bounded` is the example:
`\W` is 5.5× rarer BY BYTES than `[a-z]` on prose but 1.0× by landings, and the whole 657,770 ns (53% of the
1.24 ms OFF-layer loss on the table) is the fixed per-use term, +3.7…3.9 ns per use at skip 0. 43% is
wrong-origin (a different, parked tactic), 4% kit cost with no better origin, 12 rows unreached side effects.

## 3. (c) The bench's population by regime (pcrec auto-caps, pin per §0)

Method: `population.tsv` = 30,117 measured pcrec cells (subbench × pattern × subject × regime), each with its
subject length (bench manifests) and median ns/call. `classify.out`: bands by subject length n against §2.1:
D0 n < 47 B (fixed ≥ half for every form), D1 47–526 B (dinghy for the fast forms/memchr class, liner for the
scalar walk), M 527–5,269 B (transition; 5,270 = 10 × 527, where fixed < 10% for the memchr class), L ≥ 5,270 B.
"T ≤ 2F": measured time within 2× the bench's empty-call floor (8.86 ns), i.e. fixed ≥ half of the time by the
bench's own number, independent of any n*.

Regimes present: `short-subject-search`, `match-compliance` (single-subject whole-match, same short subjects),
`large-subject-throughput`. `sentinel` has no pcrec rows in these reports and is not counted.

### 3.1 Per-subject cells

| subbench | regime | cells | D0 <47 | D1 47–526 | M | L ≥5,270 | T ≤ 2F |
|---|---|--:|--:|--:|--:|--:|--:|
| altwide | short | 1,360 | 612 | 748 | 0 | 0 | 445 (33%) |
| altwide | match | 1,560 | 702 | 858 | 0 | 0 | 1,448 (93%) |
| altwide | throughput | 136 | 0 | 0 | 0 | 136 | 0 |
| bounded | short | 1,932 | 1,302 | 630 | 0 | 0 | 1,375 (71%) |
| bounded | match | 2,058 | 1,302 | 672 | 84 | 0 | 1,614 (78%) |
| bounded | throughput | 210 | 0 | 0 | 84 | 126 | 0 |
| capability | short | 5,175 | 4,761 | 414 | 0 | 0 | 4,224 (82%) |
| capability | throughput | 757 | 0 | 0 | 69 | 688 | 229 (30%) |
| email | short | 231 | 231 | 0 | 0 | 0 | 97 (42%) |
| email | match | 255 | 231 | 3 | 15 | 6 | 156 (61%) |
| email | throughput | 15 | 0 | 0 | 0 | 15 | 0 |
| litrun | short | 378 | 322 | 56 | 0 | 0 | 298 (79%) |
| litrun | match | 378 | 322 | 56 | 0 | 0 | 355 (94%) |
| litrun | throughput | 378 | 0 | 0 | 0 | 378 | 26 (7%) |
| loglines | short | 1,232 | 0 | 286 | 946 | 0 | 184 (15%) |
| loglines | throughput | 132 | 0 | 0 | 0 | 132 | 0 |
| syntax | short | 3,486 | 2,905 | 581 | 0 | 0 | 2,944 (84%) |
| syntax | match | 3,442 | 2,868 | 574 | 0 | 0 | 3,357 (98%) |
| syntax | throughput | 240 | 0 | 0 | 0 | 240 | 18 (8%) |
| utf8 | short | 6,279 | 6,279 | 0 | 0 | 0 | 5,592 (89%) |
| utf8 | throughput | 483 | 0 | 0 | 0 | 483 | 21 (4%) |
| **TOTAL** | | **30,117** | **21,837** | **4,878** | **1,198** | **2,204** | **22,383 (74%)** |

Reading: the short and match regimes (26,000 cells, 86% of the population) are almost all D0/D1: dinghies by
length for every fast form, and 71–98% of the short/match cells (utf8/syntax/capability/litrun) sit within 2× the empty-call floor. The
exceptions are `altwide` short (222–244-B subjects; only 33% within 2F: the 8–390 ns spread is work, not
floor) and `loglines` short (279–3,772-B subjects, median 1,125 B: the one set whose short regime is in the
transition band; 15% within 2F, median 198.6 ns). 2,204 cells (7%) are liners by length, all throughput.

Caveat that matters for classification: **subject length is not bytes touched.** 229 of capability's 757
throughput cells (30%) are within 2× the empty-call floor despite 4–1,048,576-B subjects: an early exit or a
required-byte/run reject answers in one call (5.9 ns at the 5th percentile). By time they are dinghies inside a
liner-sized subject. The data here cannot count "bytes touched" per cell; a stamp or counter census would.

### 3.2 Set-grain cells (the front-page grain: pattern × regime, summed over the subjects), by the cell's largest subject

`setgrain.out`: 827 set cells: D0 72 (utf8 short 69, email short 3), D1 377, M 53, L 325 (all throughput:
altwide 34, bounded 42, capability 69, email 3, litrun 14, loglines 11, syntax 80, utf8 69; plus the match
regime of bounded 42 and email 3 whose largest subject is ≥ 527 B).

### 3.3 Throughput cells by match gap (the liner subjects that are dinghy passes)

`density.out`: 2,351 throughput cells joined to the oracle's `nmatches` (len / nmatches = gap). Bands per §2.2:

| subbench | cells | 0 matches | gap ≥ 845 | 100–844 | < 100 B |
|---|--:|--:|--:|--:|--:|
| altwide | 136 | 49 | 78 | 9 | 0 |
| bounded | 210 | 84 | 31 | 11 | 84 |
| capability | 757 | 658 | 37 | 32 | 30 |
| email | 15 | 9 | 3 | 0 | 3 |
| litrun | 378 | 278 | 1 | 0 | 99 |
| loglines | 132 | 80 | 40 | 0 | 12 |
| syntax | 240 | 39 | 45 | 138 | 18 |
| utf8 | 483 | 255 | 48 | 42 | 138 |
| **TOTAL** | **2,351** | **1,452 (62%)** | **283 (12%)** | **232 (10%)** | **384 (16%)** |

So 16% of the liner-sized throughput cells (384) have a match every < 100 B: per-match fixed cost is the
larger share on the scalar forms by §2.2, ~1 MiB subject or not; another 10% (232) are dense enough for the
memchr class (< 845 B) but not for the walk. 62% report zero matches: whether those are per-byte passes
or dense candidate passes that fail verification is not in the oracle data (§4 gap 3). `nmatches` counts
matches, not uses or landings, and §2.3 shows they differ.

## 4. (d) What the data cannot tell

1. **C_call, C_use, C_match are one number wherever uses ≈ calls ≈ matches.** Only the per-match SUM is
   identified (§1.2). The three are separable only in cells with uses ≫ calls (`dfa-hat`, one call, up to 75,836
   uses: C_use = 4.1 ns) and calls ≫ 1 with uses = calls.
2. **F for the SIMD forms** (§1.1) rests on ONE short row (40 B) per form and includes a partial-block tail; no
   subject between 40 B and 64 KiB was timed on the sparse cells, so the shape of T(n) in the transition (50 B–60
   KiB: tail handling, L1→L2) is unmeasured. The 64 KiB prediction is off by +7.7% for A1.
3. **Bytes touched / uses / landings per bench cell** are not in any committed bench report. Length and
   match count are; landings and early-exit position are not (hence the 30% of capability throughput cells that
   finish in dinghy time, and the 62% zero-match cells whose density of CANDIDATES is unknown).
4. **Zen 4 ↔ Zen 1 transfer** has one measured point (a ratio 2.2 on `f-tag`) and two documented guesses (×1.6, +5
   ns bench tax). c_byte(walk) on Zen 1 has no measurement; the 47-B bench n* mixes boxes.
5. **No cold/warm separation of C_use at the pcrec entry level**: r17loss splits PF cold +2.06 / warm +1.09 but those
   are form deltas between two kit forms, not pcrec's own `rx_search` entry cost (the 5.61–8.86 ns floors are).
6. **Subject size 64 KiB vs 1 MiB are different regimes** in the kit data (branch predictor learns a 64-KiB
   stream: hex-run walk 0.907 ns/B at 64 KiB vs 1.852 at 1 MiB); a length-only model cannot fit both. And 64 KiB
   find-all rows are bimodal across replicates (A/A up to 60.8%): per-row coefficients from them are ±50%.
7. **3- and 4-term sets** have no sparse measurement; their per-byte saving is an extrapolation.
8. **No cell holds subject length, match density and use density apart.** The kit's cells fix pattern and vary
   subject (9 subjects, densities correlated with length); the bench varies both but is not designed as a grid.

### 4.1 The small controlled grid that would fill it (named, NOT run)

One pattern per row of the table below on ONE box, `drv.c`-style pinned loop, A/A pair, ≥ 5 launches; the cells are
orthogonal on the three axes the existing data confounds.

- **Axis N (subject length, bytes)**: 8, 16, 32, 64, 128, 256, 512, 1 Ki, 2 Ki, 4 Ki, 16 Ki, 64 Ki, 256 Ki, 1 Mi
  (14 values; fills gap 2: the transition shape).
- **Axis G (gap between matches/landings, bytes, subject length held ≥ 64 Ki)**: ∞ (zero), 2 Ki, 512, 128, 32, 8, 2
  (7 values; separates matches·C_match from bytes·c_byte at fixed n).
- **Axis U (candidates per match that fail verification, i.e. uses/landings per match)**: 1, 4, 16 (3 values; fills
  gap 1 and gap 3: separates C_use from C_match).
- **Axis K (calls per pass at fixed total bytes)**: 1, 16, 256, 4,096 (4 values; isolates C_call from C_use).
- **Sites/forms (the table's rows)**: the scalar walk, SWAR, SSE2, AVX2 PF scan; VM hat; DFA hat; memchr-class
  `floor`. Minimum cells: N sweep on {walk, AVX2, memchr-class} × 14 = 42 sparse cells; G × U on {walk, AVX2} × 7 × 3
  = 42 find-all cells at n = 64 Ki; K sweep on {walk, memchr-class} × 4 = 8 cells. **92 cells ≈ 92 × (5 launches ×
  ≥ 50 ms)**, plus the Zen 1 repeat of the memchr-class and walk rows to measure the transfer (gap 4).
- **Counters (no clock)** on every cell: calls, uses, landings, bytes touched. These make gap 3 a lookup.

## 5. (e) Bench-only questions, for relay (never reverse-engineered here)

1. **Q1.** Is a `short-subject-search` / `match-compliance` per-call figure measured over one `rx_search` call
   per subject, with the loop overhead of `timed_run` inside it? What is the instrument term in the 8.86 ns
   `floor` (the 5.61 ns immediate-return figure is revpred's quote of O-91; is that the same driver)?
2. **Q2.** Can the bench export, per throughput cell, the pcrec-side counters the stamps already allow: number of
   `rx_search` calls per pass, number of candidate landings/uses, and bytes touched (or the position of the last
   byte read)? This turns §3.3's `nmatches` proxy and the 30% early-exit class into lookups.
3. **Q3.** Can a Zen 1 `drv.c`-style kit-loop run be done on ubuntubudu for the sparse N sweep (gap 4), so the kit's
   per-form constants have a bench-box twin? (The bench reports only pcrec-level cells.)
4. **Q4.** For `sentinel` (76 subjects, no pcrec rows in the reports read), which pcrec testee, if any, is the
   reference, so its cells can be added to §3?
5. **Q5.** In litrun, what is the periodicity of the `fbf-lK` throughput subjects? §1.3's "14.2 ns per landing"
   assumes one literal occurrence per K bytes; and why does the 1/K law break at K = 40 (18.9 ns/landing) while
   `lbf-l40` (24,595 ns) lies on it? (Is the fbf form different past 32 B?)
6. **Q6.** `email` at pin 6b2dbd3e and `bounded` at 6b2dbd3e carry no pcrec row in the handoff reports (only libpcre2
   and older pcrec pins); is that deliberate? §3 uses b8337c33 for both (a different pin than the other six).

## 6. Reproduction

```
python3 -I docs/dev/lanes/regimefacts/fit_vecspike.py /home/pcrec/projects/pcrec/worktrees/memfn-slot/spike1
python3 -I docs/dev/lanes/regimefacts/bench_population.py /home/pcrec/projects/pcrec-bench > population.tsv
python3 -I .../floor_fits.py population.tsv ; classify.py population.tsv ; setgrain.py population.tsv
python3 -I .../density.py population.tsv /home/pcrec/projects/pcrec-bench
```
`fit_vecspike.py` imports numpy (`-I` still finds it from site-packages). Nothing here writes outside this directory.
