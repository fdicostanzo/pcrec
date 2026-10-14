# costmodel — the search-form cost model by REGIME: dinghies, tugs and liners

Lane costmodel, 2026-10-13, branch `lane/memfn-costmodel` (cut from the kit branch
`lane/memfn-r17` at a66076383). ANALYSIS ONLY: no timing run, no `make`, nothing
under `src/` or `memfn/src/` changed, no pcrec byte moved. Every ns figure is read
from logs that earlier slots measured; every count comes from a no-clock counting
pass. The one new measurement is a counting pass (no clock): lane r17loss's
instrument re-run over all nine subjects instead of five. Its 80 slot25c lines
reproduce r17loss's `counts.txt` byte for byte.

All tables below are cut from `docs/dev/lanes/costmodel/analysis.txt`
(`python3 -I costmodel.py > analysis.txt`); section numbers like "an. A.2" point
into it. Box for every ns number: the Linux dev box, Ryzen 7 7700X (Zen 4), gcc
15.2 -O2, CPU 14 pinned, kit tier, UNOFFICIAL (D144 addendum 4).

## Summary (the answers first)

1. **Three regimes, split by two counted facts.** The facts are `L`, the bytes
   the find advances per ACTIVATION (per call into the site), and `g`, the bytes
   it advances per USE (per candidate it returns).
   - DINGHY: `L < 64 B`. Per-call and per-use fixed terms are 72% of the walk's
     time. The median walk call is 11.8 ns.
   - TUG: `L ≥ 64 B` and `g < 18 B`. The per-use term is 51% and the consumer
     34%. The median call is 2.8 µs.
   - LINER: `L ≥ 64 B` and `g ≥ 18 B`. The per-byte term is 77%. The median
     call is 7.3 µs.

   The boundaries are derived, not picked. `g* = 18.5 B` is where the walk's
   per-use term equals its per-byte term. `L* = 64 B` is the block width, which
   covers every form's per-activation break-even (19-39 B). Per call, dinghy
   and liner differ by roughly 600x at the median and ~5×10^4 at the extremes.
   Per MiB of subject the order INVERTS: the dense dinghy pass costs the walk
   1.75 ms/MiB and the liner 0.24 ms/MiB. Dense data is the expensive data.
2. **The absolute re-score makes ALPHA look worse, not better.** Weighted by ns,
   the 62 WIN / 87 REGRESSION / 11 NULL rows (both layers) sum to −0.68 ms of
   wins and +2.48 ms of losses. On the OFF layer, by regime:
   - LINER: 14/0/0, −287 µs, −30% of the walk.
   - TUG: +501 µs, +14%.
   - DINGHY: +685 µs, +12%.
   - The 24 unreached rows: −0.6 µs.

   Three rows carry 85% of the loss ns. They are 1 MiB dense passes:
   - bounded prose1m all: +599 µs;
   - dfa-hat prose1m all/first: +232 µs / +234 µs.

   Frank's "a +50% on a few ns" is true PER CALL: a DINGHY call loses +1 to
   +5 ns (median +1.96 ns, +24.5%). It is not true per pass on a dense 1 MiB
   subject, where 161,476 such calls make +0.6 ms.
3. **The drivers, by regime** (an. A.4). The SWAR R17-b form (V1) differs per
   regime:
   - DINGHY: the cold per-activation cost (+1.6 ms summed) and the wasted scan
     past the hit (+0.63 ms) outweigh the per-byte saving (−0.30 ms).
   - TUG: the warm per-use cost (+1.14 ms) and the waste (+0.46 ms) outweigh
     the saving (−0.51 ms).
   - LINER: it is the per-byte saving alone (−0.91 ms).

   At W=64 SIMD the per-byte saving more than doubles. That flips TUG to a win
   (16/0/2, −2.9 ms), but DINGHY's cold cost quadruples (A1 +4.65 ms summed),
   so DINGHY stays a loss. KEEP at SIMD width removes the cold cost (A3 DINGHY
   10/10/3, net −1.9 ms).
4. **The formula** (an. C.1). Per byte of a pass:

       delta_f/byte = c_cold·α + c_warm·(λ − α) + m·λ·fresh − (β_t − β_f)·φ + β_f·over/byte

   - λ = uses per byte (landings), α = activations per byte (calls), φ = the
     share of bytes the find advances over.
   - β_t = 0.189 ns/B (the walk, MEASURED). β_f is MEASURED per width: SWAR
     0.110/0.139, SSE2 0.021, AVX2 0.010 ns/B.
   - c_cold, c_warm and m are FITTED per form and site kind.
   - The overscan is MEASURED from the counters: 4.7 B per cold use at SWAR,
     59 B at W=64.

   Sign agreement from workload facts alone, per regime: LINER 100%, TUG
   93-100%, DINGHY 86-91%. Absolute ns explained: LINER 0.77-0.95, TUG
   0.2-0.64, DINGHY ≤ 0.34. The misses are the 1 MiB dense rows, where branch
   behaviour that no counter records moves the walk.
5. **Density.** Yes, the loss is high density, but density of LANDINGS, not of
   bytes (an. B.1).
   - By gap g, V1 loses 32 of 38 rows below 4 B and 18 of 22 at 8-16 B, and
     wins 13 of 16 at 16-32 B and every row at 32 B and up.
   - By byte density p the split is blurred: 11 wins and 12 losses in
     50-100k ppm. bounded's [a-z] is 85% of prose bytes but lands every 6.5 B;
     dfa-hat's {f,n,t} is 10% of bytes but lands every 11 B. Both lose.

   Crossovers (an. B.2) move with the CALL PATTERN far more than with width:
   - V1, 1 term: g* = 15.6 B with the state carried, 25.7 B with it lost.
   - AVX2: g* = 3.8 B carried, 28 B lost.
   - KEEP at AVX2: g* = 5.9 B.

   In landings per million bytes: the carried AVX2 form wins down to about
   260,000; the lost-state forms only up to 26,000-40,000. Losses that are NOT
   density: single-call dinghies (+0.2 to +26 ns), 40-byte subjects at W=64
   (the sub-block tail, +7 to +24 ns), and word-eq's 3 terms (SWAR saves only
   0.022 ns/B at 3 terms, DERIVED).
6. **What decides, and what each information source buys** (an. D.1). Regret is
   the measured ns of a policy's pick minus the fastest form's, summed, as a %
   of the walk, given as DINGHY / TUG / LINER.
   - **SIMD-off**: R17-b as shipped regrets 7.5% / 7.2% / 0.2%. A regime hint,
     or an exemplar's gap, regrets 0.8% / 0.1% / 0.2%, picking walk / walk /
     mask8.
   - The compile-time prior's gap misplaces `dig` on real text and costs 12.3%
     in LINER. The r17loss rule (prior ≥ 100k declines) costs 0.7 / 0.3 / 0.6%.
   - **SIMD-on without the iterator**: the decision is DINGHY or not, and that
     needs the call SPAN, which no byte statistic carries. Always-AVX2 costs
     7.2% in DINGHY; a regime hint costs 3.1% (9.1% learned leave-one-cell-out).
   - **SIMD-on with the D165 iterator**: AVX2+KEEP everywhere costs 2.8% / 4.0%
     / 1.9% with no information at all. A hint that drops KEEP in TUG/LINER gets
     2.8% / 0.1% / 0.7%.
   - So the information decides the REGIME, and within a regime one fixed form
     is within a few % of the oracle.
7. **The sources, ranked.**
   - λ (landings) is a bigram fact. `pcrec-analyze --scan freq,bigram`, its
     default, already counts it for any set (Σ over a∉S, b∈S). The shipped
     bundles carry no bigram.
   - α (span per call) is a call-pattern fact. No byte statistic carries it: it
     comes from a hint, a pattern-specific profile (declined by D83(2)), or the
     run time. The run time is exactly where D165's iterator lives.
   - The adaptive switch as slot2 built it costs 1.6-3.2x on dense carried rows
     (an. D.2) and is not the way to learn the span.
8. **Rules of thumb** are in §E, grouped by regime. Measurements owed, with
   cells and wall time, are in §F. They lead with a perf branch-miss pass on the
   1 MiB dense rows and the controlled length × gap × span grid (regimefacts
   §4.1, extended).

## Inputs, method, and what this report adds

| input | what | read how |
|---|---|---|
| `slot25c/time.log` → `data/alpha_time.log` | R17-b ALPHA: new vs deny (the walk), 8 cells × 5 subjects × 2 modes × 2 layers | sha256 `a8113a50…3440` (= r17loss's copy) |
| `spike1/time.log` → `data/spike_time.log` | vecspike: V0 walk vs V1..V4 (8 B), S1..S4 (SSE2 W=64), A1..A4 (AVX2 W=64) over 9 subjects × 2 modes; 1,549 rows | `5ad6f4c3…` |
| `spike1/v2/time2.log` → `data/spike2_time.log` | vecspike2: dfa-hat P1/P2/P3/P4/P3W at 3 widths; 288 rows | `0964e4fc…` |
| `spike1/counts.tsv`, `v2/counts2.tsv` | per-variant counters (cold, cache_hit, xcall, head, blocks; cands) | `62594d1e…`, `53910d55…` |
| `data/counts9.txt` (NEW, no clock) | r17loss's `instrument.py` + `cnt.c` (copied verbatim as `count_instrument.py`/`count_cnt.c`) run over all 9 subjects: calls, matches, uses, cold, skip bytes, masks | `count9.sh`; 80 slot25c lines byte-identical to r17loss's `counts.txt`; re-run byte-identical |
| `subjstats.tsv` (NEW, no clock) | per (cell, subject): byte density p of S, landings, gap mean/CV, the walk's skip-run predictability | `subjstats.py` over the subject files |
| slot2 `times.tsv` (branch file `docs/design/memfn/probes/r17/out/slot2/`) | the kernel-only density sweep: 19 cells × 18 forms × ppm grid × n ∈ {64K, 1M} × reset ∈ {inf, call, 4, 16} × percall spans {16, 64}; 9,654 rows | read directly |
| r17loss, vecspike_reading, origsurvey, regimefacts (main, same day), setfind.md §8/§9.2/§13.5, reading_slot2.md, D161/D162/D165, plan rows | quoted where cited | — |

Noise floor: the vecspike reading's strict floor, used throughout for the spike
rows. A row is NULL when `|d| ≤ max(A/A, 2.3% of the walk)`; 2.3% is the p90 of
the A/A distribution (reading §1.3). The six unstable 64 KiB find-all groups are
kept and judged by their own A/A. ALPHA rows keep their log's verdict.

**Relation to lane regimefacts** (`docs/dev/lanes/regimefacts_report.md` on main,
the same day). regimefacts fits per-call constants against SUBJECT LENGTH
(F, c_byte, n* per form) and places the bench's 30,117 pcrec cells by length and
match gap. This report adds four things:
- it places every timed kit row by COUNTED per-activation and per-use facts, so
  a 1 MiB dense find-all is a dinghy pass, a point regimefacts §2.2 already made;
- it re-scores ALPHA and the spike in absolute ns per regime;
- it decomposes each form's delta into named mechanical terms;
- it turns the terms into an estimator, a priced decision table and a regret per
  information source.

Its constants agree with regimefacts' where they overlap: walk 0.189 vs 0.190
ns/B, V1 0.110 vs 0.109, SSE2 0.0206 vs 0.0206, AVX2 0.0105 vs 0.0108.

## 0. THE REGIMES

### 0.1 The two facts and where the boundaries come from

For every timed row the counting pass gives `calls`, `uses`, `cold` (the uses
that open an activation) and `skip` (bytes the find passes over). From them:

- `L` = (skip + uses) / cold: the bytes the find advances per activation;
- `g` = (skip + uses) / uses: the bytes it advances per use, which is the gap
  between the landings it stops at;
- `λ` = uses / n: landings per subject byte.

The walk's own pass, decomposed (an. 0.1, noise-weighted least squares over every
reached spike group, V0 = F·calls + u·uses + b_skip·skip + b_cons·consumed):

| site kind | rows | F/call | u/use | b_skip ns/B | b_cons ns/B | median rel. residual |
|---|---|---|---|---|---|---|
| PF (DFA prefilter scan) | 68 | 2.54 | 3.42 | 0.185 | 0.561 | 0.33 |
| DFA hat | 18 | −2.03 | 3.96 | 0.189 | 0.218 | 0.05 |
| VM hat | 30 | 4.11 | −1.94 | 0.187 | 4.595 | 0.07 |

The per-skipped-byte rate is the same for all three kinds, 0.185-0.189 ns/B.
- **g\***: the per-use term (3.4 ns) equals the per-byte term at g = 3.42 /
  0.185 = **18.5 B**. Below it, a pass is made of uses; above it, of bytes.
- **L\***: the per-call term equals the per-byte term at 13.8 B for the walk.
  The FORMS' per-activation break-even (an. B.2) is 19 B (V1), 25 B (A1) and
  32 B (S1), plus the overscan. **64 B**, the W=64 block width, covers all of
  them: an activation shorter than one block cannot amortize the block.

Sensitivity:
- at L\* = 32 B, nine of the 116 spike groups move out of DINGHY: the 40-byte
  subjects (dig, dfa-hat, vm-hat-1), word-eq mix64k, and vm-hat prose64k
  `first`;
- moving g\* anywhere within 16-20 B moves at most eight groups between TUG
  and LINER: six vm-hat groups, bounded digits64k `first` and vm-hat-1 mix64k
  `first`;
- no other group moves.

| regime | rule | what the facts say about the pass |
|---|---|---|
| DINGHY | L < 64 B | each activation advances less than one W=64 block: the fixed per-activation and per-use costs dominate. Short subjects, single calls that match within a few bytes, AND find-all passes over dense matches (each call is a dinghy even when the subject is 1 MiB) |
| TUG | L ≥ 64 B, g < 18 B | long activations full of candidates: the per-use cost dominates and the state CAN carry within the activation (dfa-hat on prose/docs/code, word-eq and email on docs/code) |
| LINER | L ≥ 64 B, g ≥ 18 B | sparse candidates: bytes dominate (dig on prose/docs/code, vm-hat-1 on everything, dfa-hat with no `f`/`n`/`t`) |
| UNREACHED | uses = 0 | an upstream presence gate rejects the subject; the site never runs |

### 0.2 Every cell placed (all-mode / first-mode)

| cell | short | prose64k | digits64k | prose1m | mix64k | docs64k | docs1m | code64k | code1m |
|---|---|---|---|---|---|---|---|---|---|
| dig | D/D | L/L | D/D | L/L | D/D | L/L | L/L | L/L | L/L |
| email | –/– | –/– | –/– | –/– | –/– | –/– | T/T | –/– | T/T |
| word-eq | –/– | –/– | –/– | –/– | D/D | T/T | T/T | T/T | T/T |
| hex-run | D/D | D/D | D/D | D/D | D/D | D/D | D/D | D/D | D/D |
| bounded | D/D | D/D | T/T | D/D | D/D | D/D | D/D | D/D | D/D |
| dfa-hat | D/D | T/T | L/L | T/T | L/L | T/T | T/T | T/T | T/T |
| vm-hat | –/– | T/D | –/– | T/T | T/T | T/L | T/L | L/T | L/T |
| vm-hat-1 | D/D | L/L | –/– | L/L | L/L | L/L | L/L | L/L | L/L |

(D = DINGHY, T = TUG, L = LINER, – = unreached.) The regime is a property of the
(site, workload) pair, not of the site. `dig` is a dinghy on digits and a liner
on prose. hex-run and bounded find-all are dinghies on every subject, because
every match ends the call within ~2-7 bytes.

### 0.3 Orders of magnitude: what a pass costs and what dominates it (an. 0.3, 0.3b)

| regime | spike rows | walk ns/pass (min..max) | walk ns/call (min..max) | per-call share | per-use share | skip-byte share | consumer share | walk median ns/call | walk median ns/MiB (MiB/s) |
|---|---|---|---|---|---|---|---|---|---|
| DINGHY | 47 | 3.8 .. 3,035,070 | 3.8 .. 70.6 | 30% | 42% | 8% | 20% | 11.8 | 1,745,166 (573) |
| TUG | 35 | 53.6 .. 2,348,413 | 50.2 .. 2,348,413 | 0% | 51% | 14% | 34% | 2,789.7 | 814,054 (1,228) |
| LINER | 34 | 39.7 .. 617,314 | 39.7 .. 200,409 | 1% | 4% | 77% | 19% | 7,330.8 | 235,914 (4,239) |

Two readings, both measured:
- **Per call the regimes differ by orders of magnitude.** A dinghy call is
  4-70 ns; a liner call is 40 ns to 200 µs. That is ~600x at the medians and
  ~5×10^4 at the extremes.
- **Per MiB of subject the order inverts.** A dinghy pass over dense text costs
  the walk 1.75 ms/MiB, 7.4x a liner's 0.24 ms/MiB. Most of a dinghy pass is
  per-call and per-use fixed cost, so a 4 ms → 6 ms dense pass is a sum of
  161,476 calls of 18 → 22 ns.
- **Which axis matters depends on the workload.** Per CALL counts for
  latency-bound callers (validation of short fields). Per MiB counts for
  throughput-bound callers (scanning a corpus).

Where real calls sit: regimefacts §3 places the bench's 30,117 measured pcrec
cells by length.
- 86% are short-subject or whole-match cells, almost all under 527 B: dinghies
  by length for every fast form.
- 74% of all cells finish within 2x the bench's 8.86 ns empty-call floor.
- 7% are liners by length (2,204 throughput cells). Of the throughput cells,
  16% have a match every < 100 B (dinghy passes in liner subjects) and 62%
  report zero matches.

INTERPRETATION: "lower density is the likely case" holds for BYTES scanned in
throughput work. For CALLS, the bench, which mirrors typical regex use, is
dominated by dinghies. A short subject with no match is a dinghy however sparse
its alphabet.

### 0.4 ALPHA re-scored in absolute ns, per regime (an. 0.4)

OFF layer (the ON layer times the identical artifact). W/R/N is the log's verdict.
Sums are of new − deny in ns per pass. "Per MiB" is delta·2^20/n, all-mode rows
only.

| regime | rows | W/R/N | Σ win ns | Σ loss ns | net ns | Σ win ns/MiB | Σ loss ns/MiB | net % of walk |
|---|---|---|---|---|---|---|---|---|
| DINGHY | 31 | 7/23/1 | −51,347 | +725,542 | +684,855 | −1,058,193 | +3,595,112 | +12.1% |
| TUG | 11 | 4/7/0 | −15,051 | +515,656 | +500,606 | −239,637 | +417,775 | +14.1% |
| LINER | 14 | 14/0/0 | −286,914 | 0 | −286,914 | −595,691 | 0 | −29.8% |
| UNREACHED | 24 | 7/12/5 | −650 | +36 | −629 | −9,316 | +5,531 | −1.1% |

Both layers, all 160 rows: the 62 WIN rows sum to **−676,933 ns** and the
87 REGRESSION rows to **+2,482,970 ns** (3.7x). The 11 NULL rows sum to −5 ns.

- **The tally does look different weighted by ns, and it looks worse.** 85% of
  the OFF-layer loss ns sits in three rows, all dense 1 MiB passes:
  - bounded prose1m all: +599,268 ns (+20%; DINGHY, 161,476 calls of +3.71 ns);
  - dfa-hat prose1m all/first: +231,943 / +234,456 ns (+17%; TUG, one call,
    75,836 uses of +3.1 ns).
- **The single-call dinghy losses are tiny in absolute terms.** Their per-call
  rates are large: the 21 DINGHY first-mode REGRESSION rows of V1 in the spike
  sum to +76 ns per pass in total (an. 0.5), each +0.2 to +26 ns (+3% to +57%).
- **Every LINER row wins**, by 17-46% (dig and vm-hat-1 on prose/mix, dfa-hat
  on digits/mix).
- **The 24 unreached rows are absolute noise** (−0.6 µs total) though they
  carry 12 of the "regressions".

INTERPRETATION: ALPHA's subject set over-represents dense 1 MiB find-all with
[a-z]-sized sets, the one shape where both the per-call and the per-MiB views
lose. The liner rows show the form doing what it was built for.

### 0.5 The spike's twelve variants, per regime (an. 0.5, 0.7)

All-mode rows, strict floor. Columns: W/R/N against the walk, and net ns per pass
summed over the regime's rows.

| var | form | DINGHY W/R/N, net ns | TUG W/R/N, net ns | LINER W/R/N, net ns |
|---|---|---|---|---|
| V1 | SWAR 8 B (R17-b) | 6/14/3, +1,071,613 | 3/14/1, +1,144,423 | 16/0/1, −583,336 |
| V3 | SWAR + keep | 4/16/3, +1,725,977 | 2/15/1, +2,088,836 | 16/1/0, −486,959 |
| V2 | SWAR + prologue | 3/18/2, +2,278,777 | 3/15/0, +2,364,209 | 16/1/0, −477,481 |
| S1 | SSE2 W=64 | 1/18/4, +1,647,459 | 16/0/2, −2,620,387 | 17/0/0, −1,785,630 |
| S3 | SSE2 + keep | 8/11/4, −1,634,583 | 14/2/2, −1,890,679 | 17/0/0, −1,707,678 |
| A1 | AVX2 W=64 | 6/14/3, +658,162 | 16/0/2, −2,891,360 | 17/0/0, −1,878,277 |
| A2 | AVX2 + prologue | 4/12/7, +619,610 | 14/0/4, −1,804,935 | 17/0/0, −1,819,595 |
| A3 | AVX2 + keep | 10/10/3, −1,888,772 | 16/2/0, −2,162,660 | 17/0/0, −1,843,470 |

Per-row medians, both modes (rel / ns per call / ns per MiB of subject):

| var | DINGHY | TUG | LINER |
|---|---|---|---|
| V1 | +24.5%, +1.96, +155,332 | +8.9%, +354, +74,751 | −40.4%, −2,900, −94,095 |
| S1 | +49.3%, +4.30, +261,276 | −20.2%, −160, −187,664 | −81.9%, −5,991, −179,843 |
| A1 | +26.4%, +2.97, +140,260 | −22.2%, −175, −218,415 | −86.5%, −6,339, −193,657 |
| A2 | +16.6%, +1.39, +116,234 | −14.6%, −108, −159,788 | −85.7%, −6,272, −188,893 |
| A3 | +20.6%, +3.10, +36,644 | −10.7%, −151, −209,481 | −86.6%, −6,438, −191,813 |

The first-mode DINGHY rows (24 single calls) lose at every width:
- V1: 21 of 24 lose, +76 ns summed; S1: 23 of 24, +149 ns; A1: 21 of 24,
  +80 ns.
- Nothing can be kept across one call, so KEEP and the prologue cannot help.

The per-MiB medians give a **break-even mix**:
- SWAR loses +155 µs/MiB in DINGHY and saves 94 µs/MiB in LINER. It breaks
  even when liner text is more than 62% of the dinghy + liner bytes, and more
  than 44% of the tug + liner bytes.
- AVX2 without the iterator loses only in DINGHY (+140 µs/MiB) and saves
  194-218 µs/MiB elsewhere.
- AVX2 + KEEP is +37 µs/MiB in DINGHY: nearly neutral.

### 0.6 The multi-position filter (vecspike2, dfa-hat only; an. 0.6)

| var | DINGHY (short, 2 rows) | TUG (prose/docs/code, 12 rows) | LINER (digits/mix, no candidates, 4 rows) |
|---|---|---|---|
| V1 (P1, 8 B) | 0/2/0, +3 ns | 0/12/0, +863,116 | 4/0/0, −13,144 |
| P2w | 2/0/0, −5 | 12/0/0, −3,876,238 | 0/4/0, +20,544 |
| P3w | 0/2/0, +4 | 12/0/0, −4,137,922 | 0/4/0, +43,578 |
| S1 | 0/2/0, +36 | 12/0/0, −1,235,781 | 4/0/0, −44,005 |
| P3s | 0/2/0, +60 | 12/0/0, −5,478,759 | 4/0/0, −30,394 |
| A1 | 0/2/0, +13 | 12/0/0, −1,348,946 | 4/0/0, −46,785 |
| P3a | 0/2/0, +60 | 12/0/0, −5,674,446 | 4/0/0, −42,014 |

- In TUG, where the site is candidate-bound, the second and third positions are
  worth 3-4x the first position's whole saving. They turn the SWAR loss into
  the largest SWAR win in the data.
- In LINER they cost: at SWAR every row loses (+21 to +117 µs summed over the
  4 rows, per variant); at SIMD they still beat the walk.
- In DINGHY they are noise in absolute terms.

## A. THE DRIVERS

### A.1 The terms, and the constants the data isolate (an. A.1, A.1b)

A form's delta against the walk, per pass, splits into:
- **per-activation (cold-use) cost**: struct init, the first block load, mask
  build and movemask, and the first `next_candidate`;
- **per-use (warm) cost**: the call, the cache test, the ctz and the return,
  against the walk's inline loop exit;
- **per-byte**: the form's block evaluation rate β_f against the walk's
  per-byte test β_t, over the bytes the find advances;
- **wasted scan**: bytes a block evaluates past the hit that are never used
  (overscan);
- **fresh-subject branch term**: on 1 MiB subjects the walk's loop exit
  mispredicts where it had learned the repeated 64 KiB stream;
- **prologue head bytes** (V2/S2/A2 only), and **tail cost** (subjects shorter
  than a block) on the 40 B rows.

Constants measured where the data isolate them:

| constant | value | how | label |
|---|---|---|---|
| β_t (walk, per byte tested) | 0.1894 ns/B | dig prose64k/prose1m + dfa-hat digits64k/mix64k, one use over the whole subject | MEASURED |
| β_f, 1 term / 2 terms | V1 0.1095 / 0.1386; S1 0.0206 / 0.0208; A1 0.0105 / 0.0102 ns/B | same rows, each variant | MEASURED |
| β_f, 3 terms | V1 0.168; S1 0.021; A1 0.010 | linear in terms from the 1- and 2-term points (no 3-term set is ever sparse here) | DERIVED |
| overscan per cold / warm use | V1 4.7 / 2.62 B; S1, A1 59.2 / 3.63 B; A2 4.5 / 1.17 B | regression of blocks·W − advance on (cold, warm) uses, counters only | MEASURED |
| scanned / advanced, kept forms | V3 1.22, S3 1.32, A3 1.32 | counters | MEASURED |
| slot2 kernel, per byte at 0 ppm | table 0.185-0.189; mask8_swar 0.052-0.166 (1 term, by cover shape), 0.181/0.209/0.268 (4/5/6 terms); mask64_sse2 0.018-0.041; mask64_avx2 0.010-0.019 | slot2 `times.tsv` (an. B.3 source rows) | MEASURED (kernel only, no consumer) |

At W=64 the unkept forms evaluate **3.74 bytes per byte they advance**. Each
activation evaluates one whole block to find a hit that is a few bytes in. That is
the dinghy's wasted scan.

### A.2 The per-use terms, fitted (an. A.2)

Target: delta − β_f·blocks·W + β_t·advance, fitted on (cold, warm, uses·fresh,
[head bytes]). Weights are 1/max(A/A, 1% of walk, 0.3 ns). PF and DFA-hat sites
are fitted apart from VM-hat sites.

| var | kind | rows | c_cold ns | c_warm ns | m_fresh ns/use | wR² | absExp | sign err | LOCO err |
|---|---|---|---|---|---|---|---|---|---|
| V1 | PF/HAT | 86 | +1.54 | +0.96 | −0.29 | 0.83 | 0.20 | 5/81 | 10 |
| V1 | VM | 30 | +0.10 | −0.38 | +0.92 | 0.95 | 0.53 | 2/29 | 2 |
| V3 | PF/HAT | 86 | +2.52 | +1.40 | +0.05 | 0.81 | 0.37 | 2/81 | 4 |
| S1 | PF/HAT | 86 | +5.36 | +0.72 | −1.61 | 0.70 | 0.22 | 4/78 | 4 |
| S3 | PF/HAT | 86 | +9.76 | +1.08 | −1.17 | 0.80 | 0.43 | 6/78 | 7 |
| A1 | PF/HAT | 86 | +4.45 | +0.65 | −1.41 | 0.81 | 0.27 | 4/77 | 4 |
| A1 | VM | 30 | +1.88 | −0.12 | −1.35 | 0.98 | 0.82 | 0/30 | 0 |
| A2 | PF/HAT | 86 | +2.27 | +0.57 | −0.97 | 0.91 | 0.32 | 4/69 | 4 |
| A3 | PF/HAT | 86 | +5.96 | +1.04 | −1.06 | 0.92 | 0.43 | 8/81 | 8 |

Every variant and kind is in an. A.2. absExp is the share of ABSOLUTE ns
explained (1 − Σ|resid|/Σ|delta|). LOCO counts sign errors when each cell is
predicted by a fit that never saw it.

Reading:
- **A VM-hat use costs about nothing over the walk** (c_warm −0.38 ns at SWAR,
  −0.12 ns at AVX2). r17loss found this as a_VM ≈ −0.1.
- **A cold use at W=64 costs 4.5-5.4 ns** (PF), three times SWAR's 1.5 ns.
- **The kept forms pay +1.0-1.4 ns per warm use** for the pointer-held state.
  That matches the reading §2.4's +0.2-2.9 ns of machinery with nothing to
  reuse.
- **m_fresh is negative at SIMD widths** (−1.0 to −1.6 ns/use): on 1 MiB
  subjects the walk loses more to misprediction than the block forms do.

### A.3 What drives each regime (an. A.4)

Each term's contribution, ns per pass, summed over the regime's rows (model of
A.2). The last column is the measured sum.

| var | regime | cold uses | warm uses | per-byte | wasted scan | fresh (walk) | measured |
|---|---|---|---|---|---|---|---|
| V1 | DINGHY | **+1,607,623** | +56,680 | −298,617 | +630,990 | −277,250 | +1,071,689 |
| V1 | TUG | +3,254 | **+1,144,771** | −506,262 | +464,015 | −224,042 | +1,465,764 |
| V1 | LINER | +1,504 | −8,449 | **−913,698** | +5,787 | +76,218 | −909,173 |
| A1 | DINGHY | **+4,652,388** | +38,172 | −888,024 | +641,523 | −1,360,866 | +658,242 |
| A1 | TUG | +19,129 | +790,017 | **−1,445,276** | +53,460 | −1,871,438 | −3,829,374 |
| A1 | LINER | +9,781 | +7,692 | **−2,064,144** | +2,014 | −163,915 | −2,521,969 |
| A3 | DINGHY | +269 | **+1,145,798** | −887,724 | +21,268 | −1,029,472 | −1,888,659 |
| A3 | TUG | +189 | +1,231,204 | −1,444,497 | +51,203 | −1,653,944 | −3,028,932 |

The drivers, per regime:
- **DINGHY is a cold-use regime.** Every activation pays the form's setup
  (1.5 ns SWAR, 4.5-5.4 ns W=64) and evaluates a block past its hit (4.7 B
  SWAR, 59 B W=64) to advance a few bytes. KEEP turns cold uses into warm ones
  (A3: cold +269 ns, warm +1.15 ms) and the W=64 per-byte saving then wins.
- **TUG is a warm-use regime.** The state already carries within the one
  activation, so KEEP buys nothing (A3 ≈ A1). The per-use cost is set against
  the per-byte saving: SWAR's 0.08 ns/B does not cover ~1 ns/use at a 6-10 B
  gap, while W=64's 0.17-0.18 ns/B plus the fresh-subject term does.
- **LINER is a per-byte regime.** The delta is β_f − β_t, and width is
  everything: 0.08 ns/B (SWAR) against 0.17-0.18 ns/B (W=64).

### A.4 Fit quality per regime, and what the model misses (an. A.3, A.5)

| var | regime | wR² | absExp | sign errors |
|---|---|---|---|---|
| V1 | DINGHY / TUG / LINER | 0.74 / 0.64 / 0.97 | −0.06 / 0.20 / 0.77 | 4/44, 3/33, 0/33 |
| A1 | DINGHY / TUG / LINER | 0.35 / 0.84 / 0.99 | −0.81 / 0.64 / 0.87 | 4/44, 0/29, 0/34 |
| A3 | DINGHY / TUG / LINER | 0.18 / 0.83 / 0.99 | 0.26 / 0.57 / 0.93 | 6/42, 2/29, 0/25 |

**What the model gets right and what it misses.**
- **LINER**: the model explains 77-95% of the absolute ns. The **sign** is right
  almost everywhere.
- **DINGHY**: the model explains almost none of the absolute ns (absExp
  −0.81..0.34).
- **The misses are the 1 MiB dense rows** (an. A.5). Three groups:
  - hex-run docs1m/prose1m/code1m all: V1 is measured −72k / +7k / +47k ns,
    the model predicts +250k to +300k; A1 is measured −126k to −137k, the
    model predicts +400k to +513k.
  - bounded prose1m all: measured +606k, predicted +282k.
  - dfa-hat prose1m/docs1m/code1m: measured +175k to +239k, predicted +40k
    to +52k.

**Why the 1 MiB rows miss.**
- **hex-run's walk call nearly doubles at 1 MiB**: 11.7 ns per call against
  5.7 at 64 KiB. Its skip length varies; the most common skip length covers
  only 19% of skips, against bounded's 100% (`subjstats.tsv` `skmode`). So the
  walk's loop exit mispredicts on fresh data. On the repeated 64 KiB stream it
  had been learned (reading_slot2 §"measurement artifact"; r17loss §3.4).
- **The model's single `m·uses·fresh` term cannot fit both cells.** bounded
  pays no such penalty and hex-run pays ~6 ns/call. Gap-CV and skip-predictability
  features were tried and did not improve the absolute fit.
- **No counter records branch misses.** They are the variable. A perf pass is
  OWED (§F2).
- **dfa-hat at 1 MiB**: the consumer's verify per candidate costs 18-19 ns at
  1 MiB against 4.6-5.0 ns at 64 KiB (A.6). That moves the form-versus-walk
  difference through the interleaving, which no counter isolates.

### A.5 Out of sample: the spike's V1 model applied to ALPHA (an. A.6)

ALPHA is another run (slot25c, load1 0.72) of the same artifact family. Measured
class (log verdict) against predicted sign, both layers:

| regime | W→predW | W→predR | R→predW | R→predR | N | absExp |
|---|---|---|---|---|---|---|
| DINGHY | 10 | 3 | 0 | 46 | 3 | 0.07 |
| TUG | 8 | 0 | 4 | 10 | 0 | 0.11 |
| LINER | 28 | 0 | 0 | 0 | 0 | 0.94 |

Sign agreement 56/59, 18/22 and 28/28. The four TUG misses are two rows on
each layer: bounded digits64k `first` (+2 ns, predicted −2) and vm-hat prose1m
`all` (+33,470 / +30,056 ns, predicted −44,577: the VM hat's fresh-subject
term). dfa-hat prose1m's sign is right, but its size is 5.7x under-predicted.
The absolute ns are explained only in LINER.

### A.6 The multi-position filter's terms (derived from vecspike2's own rows)

| form | β per byte (no-candidate rows) | ns per candidate handed on, after the per-byte term: 64 KiB / 1 MiB |
|---|---|---|
| P1 SWAR (V1) | 0.1385 | 4.6-5.0 / 18.0-19.2 |
| P2 SWAR | 0.2670 | 6.2-7.5 / 17.6-19.1 |
| P3 SWAR | 0.3477 | 21-63 / 26-58 (few candidates; noisy) |
| P1 SSE2 / AVX2 | 0.0208 / 0.0102 | 4.0-4.5 / 13.2-13.9 |
| P2 SSE2 / AVX2 | 0.0394 / 0.0193 | 6.1-7.7 / 6.2-17.8 |
| P3 SSE2 / AVX2 | 0.0727 / 0.0284 | 8.1-13.1 / 8.3-12.8 |

So a k-position filter costs β_Pk·n + c_cand·cands_k, where cands_k is the
candidate rate after k positions: a JOINT rate across positions. On prose1m the
candidates per byte are 0.072 (P1), 0.0089 (P2) and 0.00053 (P3).

This predicts the reading's per-width best arm from the constants:
- SSE2 at 1 MiB: P1 1.03 ns/B, P2 0.164 ns/B, P3 0.080 ns/B. **P3 is best.**
- SWAR at 64 KiB: P2 0.31 ns/B against P3 0.35 ns/B. **P2 is best.**
- SWAR at 1 MiB: P2 0.39 ns/B against P3 0.36 ns/B. **P3 is best.**

That is the same general form as the single-set FIND: cost per byte = per-byte
rate + candidate rate × per-candidate cost. The single-set form is the k = 1
case, and the walk and the form share its candidate set, so the consumer term
cancels between them.

### A.7 Compile-time facts and subject facts

| variable | kind of fact | where it enters |
|---|---|---|
| cover terms, set size, cube/range shape | compile-time (the kit's cover of S) | β_f (per-byte rate); SWAR break-even moves 15.6 → 26 → 65 B with 1/2/3 terms |
| site kind (PF scan / DFA hat / VM hat) | compile-time (`mf_site` op and host) | c_warm (≈ 0 at VM hats) and the consumer price |
| positions available to a filter (k-set walk) | compile-time | which P_k rows apply |
| end_back, anchoring, find vs find-all entry | compile-time + API | whether a site is reached at all; first vs find-all |
| λ (landings per byte), φ (advance share), p | SUBJECT | the per-use and per-byte terms |
| α (activations per byte = span per call) | CALL PATTERN (subject + pattern + API) | the cold term; DINGHY vs not |
| fresh vs repeated subject | WORKLOAD | the walk's branch term |
| joint candidate rate across positions | SUBJECT (pair/triple statistics) | the P_k price |

## B. THE DENSITY QUESTION

### B.1 Win/loss by gap g and by byte density p (an. B.1; all reached spike rows, both modes)

| g bin (B) | V1 W/R/N | V1 med d/use | A1 W/R/N | A1 med d/use | A3 W/R/N | A3 Σ ns/MiB |
|---|---|---|---|---|---|---|
| [0,4) | 2/32/4 | +1.31 | 7/23/8 | +0.83 | 9/28/1 | +1,329,300 |
| [4,8) | 2/9/1 | +1.35 | 3/8/1 | +1.26 | 6/5/1 | −2,640,384 |
| [8,16) | 4/18/0 | +0.92 | 18/4/0 | −1.35 | 15/4/2 | −1,529,319 |
| [16,32) | 13/2/1 | −1.80 | 16/0/0 | −3.83 | 8/0/0 | −1,702,738 |
| [32,128) | 12/0/0 | −5.91 | 12/0/0 | −15.86 | 9/0/1 | −862,326 |
| [128,∞) | 16/0/0 | −1,870 | 16/0/0 | −6,265 | 12/0/0 | −1,499,745 |

| p bin (ppm of S) | V1 W/R/N | A1 W/R/N |
|---|---|---|
| 0 | 10/0/0 | 10/0/0 |
| (0, 50k) | 24/0/0 | 24/0/0 |
| [50k, 100k) | 11/12/1 | 20/4/0 |
| [100k, 300k) | 2/18/2 | 11/9/2 |
| [300k, 600k) | 1/9/0 | 3/7/0 |
| [600k, 1M] | 1/22/3 | 4/15/7 |

**Is the loss primarily high density? Yes, of LANDINGS; byte density is the
wrong variable.**
- By gap the split is clean. The SWAR form wins 41 of 44 rows at g ≥ 16 B and
  loses 59 of 72 below 16 B.
- By byte density it is blurred. [50k, 100k) is split 11/12, and the same p can
  win or lose.
- Gaps decouple from bytes in two directions:
  - long runs: bounded/email on prose, p = 0.846 but g = 6.5 B, because a
    run-consuming scan stops once per word;
  - isolated members: hex-run on prose (p = 0.195, g = 6.3) and dfa-hat
    (p = 0.097, g = 11.4). Low byte density, short gap, still a loss.

origsurvey made this observation for origins ("landings, not bytes"); it is the
same variable for form choice.

### B.2 The crossovers (an. B.2; model of A.2, PF/HAT)

The break-even gap is g\* = per-use cost / per-byte saving, with the per-use cost
taken either with the state carried (warm) or with it lost (cold, one use per
activation, the find-all-with-dense-matches case).

| form | terms | saving ns/B | g\* carried (B) | g\* lost (B) | landings per million bytes at g\* (carried / lost) |
|---|---|---|---|---|---|
| V1 SWAR | 1 | 0.080 | 15.6 | 25.7 | 64,000 / 39,000 |
| V1 SWAR | 2 | 0.051 | 26.1 | 43.2 | 38,000 / 23,000 |
| V1 SWAR | 3 | 0.022 (DERIVED) | 64.7 | 107.7 | 15,000 / 9,000 |
| S1 SSE2 | 1-3 | 0.168 | 4.7 | 39.0 | 213,000 / 26,000 |
| A1 AVX2 | 1-3 | 0.179 | 3.8 | 28.4 | 262,000 / 35,000 |
| V3 SWAR + keep | 1 | 0.048 | 29.3 | (= carried) | 34,000 |
| S3 SSE2 + keep | 1 | 0.162 | 6.7 | (= carried) | 149,000 |
| A3 AVX2 + keep | 1 | 0.176 | 5.9 | (= carried) | 169,000 |
| any, VM hat | 1-2 | — | < 0 (wins at every gap) | 7.7-50 | — |

How the crossover moves:
- **Call pattern (state carried vs lost)**: by 5-8x at W=64 (3.8 → 28 B) and
  1.6x at SWAR.
- **Width**: carried, by 3-4x (15.6 → 3.8 B); lost, hardly at all (25.7 → 28 B).
  The W=64 block's cold cost eats its own per-byte gain when every activation is
  short.
- **Terms**: at SWAR only (15.6 → 65 B from 1 to 3 terms); the SIMD per-byte
  cost is flat in terms.
- **KEEP**: it moves a W=64 form from the lost line to just above the carried
  line (5.9-6.7 B). At SWAR it makes things worse (29 B), because the 8-byte
  block holds too few candidates to be worth keeping.

### B.3 The kernel sweep (slot2: no consumer, i.i.d. placement, so landings ≈ members; an. B.3)

Median over 14 real cells of form/table; "x" marks a loss beyond the slot's
1.016 band.

| regime (slot2) | ppm | mask8_swar | mask64_sse2 | mask64_avx2 | sse2 (stateless) | avx2 (stateless) |
|---|---|---|---|---|---|---|
| findall, state kept, 64K | 70k / 300k / 800k | 0.69 / 0.86 / 0.52 | 0.47 / 0.90 / 0.53 | 0.46 / 0.88 / 0.52 | 0.66 / 1.27x / 0.68 | 0.72 / 1.41x / 0.75 |
| findall, state kept, 1M | 70k / 300k / 1M | 1.05x / 0.63 / 0.56 | 0.36 / 0.34 / 0.47 | 0.35 / 0.33 / 0.45 | 0.64 / 0.45 / 0.66 | 0.45 / 0.49 / 0.75 |
| findall, state lost every hit (ALPHA's find-all), 64K | 20k / 70k / 300k / 800k | 0.65 / 0.97 / 1.65x / 0.94 | 0.39 / 0.99 / 1.88x / 1.11x | 0.35 / 0.93 / 1.81x / 1.03x | 0.29 / 0.65 / 1.27x / 0.70 | 0.29 / 0.71 / 1.40x / 0.78 |
| percall spans of 16 B (dinghy calls) | 0 / 20k / 300k / 800k | 0.70 / 0.65 / 1.23x / 1.50x | 0.64 / 0.61 / 1.41x / 1.74x | 0.58 / 0.59 / 1.28x / 1.62x | 0.49 / 0.46 / 0.88 / 1.10x | 0.64 / 0.58 / 1.11x / 1.40x |
| percall spans of 64 B | 0 / 20k / 300k / 800k | 0.59 / 0.54 / 1.30x / 1.57x | 0.19 / 0.27 / 1.25x / 1.54x | 0.17 / 0.24 / 1.08x / 1.34x | 0.23 / 0.26 / 1.00 / 1.11x | 0.21 / 0.24 / 0.89 / 1.10x |

In ppm, for the dinghy shapes (state lost, short spans) the crossover sits
between 70k and 300k for every form. With the state kept it does not exist: the
mask forms win at every density.

The kernel also shows something the pipeline spike never timed: **in dinghy calls
the STATELESS SIMD forms beat the stateful mask forms**. At L16 300k, sse2 is 0.88
against mask64_sse2's 1.41; at L64 300k, avx2 is 0.89 against 1.08. The mask's
cache bookkeeping is a per-call cost with nothing to cache. Owed as a pipeline
measurement (§F6).

### B.4 Losses that are not density (an. B.4)

- **Single-call dinghies.** A `first` call that matches within a few bytes loses
  a fixed +0.2 to +26 ns (+3% to +57%) at every width. hex-run and bounded on
  every subject, dig on digits/mix, and word-eq mix64k all show it. It is the
  cold per-activation cost; no gap enters.
- **Short subjects at W=64.** On the 40 B subjects S1 loses +7 to +24 ns
  (+49% to +339%) and A1 +7 to +11 ns, even where V1 wins (dig short: V1 −35%,
  S1 +80%). This is the sub-block tail (reading V-8); regimefacts §1.1 gives the
  SIMD forms' F = 10-20 ns against the walk's 4.3.
- **Term count.** word-eq's 3-term cover leaves SWAR a per-byte saving of only
  0.022 ns/B (DERIVED), so its break-even gap is 65-108 B. slot2's synthetic
  cells place the SWAR break-even at 4-5 terms (mask8 0.181/0.209 ns/B at 4/5
  terms against the table's 0.185).
- **Fresh 1 MiB dense data** moves the walk itself (A.4). The sign follows
  branch predictability, not density alone: hex-run 1M wins at SIMD where
  hex-run 64K loses, and bounded loses on both.

### B.5 How representative the contrived subjects are (an. B.5)

| var | contrived (slot25c's 5) W/R/N, median rel | real text (docs/code) W/R/N, median rel |
|---|---|---|
| V1 | 25/28/3, +5.2% | 24/33/3, +3.1% |
| S1 | 27/26/3, +2.1% | 38/17/5, −16.9% |
| A1 | 32/22/2, −15.6% | 40/13/7, −18.8% |
| A3 | 24/22/3, +0.9% | 35/15/2, −10.5% |

The real-text rows place 16 DINGHY / 24 TUG / 20 LINER, against the contrived
31 / 11 / 14.
- **Real text is TUG-heavier and dinghy-lighter.** It has fewer single-letter
  matches and more long activations full of candidates.
- **The SIMD forms do better on it** than on the contrived subjects; the SWAR
  form does about the same.
- **The contrived extremes miss.** digits64k for dig, an all-digit subject; and
  prose for dig, with no digit at all. Real text puts dig in LINER (gap
  44-125 B).

INTERPRETATION: the ALPHA subjects test the extremes. Real text sits mostly in
TUG and LINER, where SIMD wins and SWAR is mixed.

## C. THE ESTIMATOR

### C.1 The closed form

Per pass, for form f at a site of kind k with `terms` cover terms:

    delta_f = c_cold(f,k)·A + c_warm(f,k)·(U − A) + m(f,k)·U·fresh
            + (β_f − β_t)·ADV + β_f·OVER
    OVER    = ω_cold(f)·A + ω_warm(f)·(U − A)     (unkept forms)
            = (κ_f − 1)·ADV                         (kept forms; A = 1 per pass)

- ADV is the bytes the find advances, φ·n_scan.
- U is the uses, λ·n_scan; every activation has at least one use.
- A is the activations (calls) that reach the site, α·n_scan.

Per byte:

    delta_f/n = c_cold·α + c_warm·(λ − α) + m·λ·fresh − (β_t − β_f)·φ + β_f·over/n

The constants are an. C.1. β_t is MEASURED; β_f is MEASURED for 1-2 terms and
DERIVED for 3; c_cold, c_warm and m are FITTED (A.2); ω and κ are MEASURED (A.1).
`costmodel.py --price kind=PF terms=1 n=... lam=... p=... alpha=... fresh=...
layer=on iterator=0|1` prices every row of C.4 for one site.

Two worked examples with the subject's own facts:
- **bounded prose1m all, SIMD-on, no iterator**: walk is the argmin, which is
  right. With the iterator, sse2+keep and avx2+keep are priced −0.06 ns/B.
  That is WRONG: A3 measured +1.94 ns/use there, a loss. It is one of the
  model's DINGHY sign errors (A.4).
- **dfa-hat prose1m, SIMD-off**: walk is the argmin (mask8 +0.04 ns/B).

### C.2 Predicted vs measured, from workload facts alone (an. C.2; no blocks counter)

| var | DINGHY agree | TUG agree | LINER agree |
|---|---|---|---|
| V1 | 91% | 94% | 100% |
| S1 | 91% | 97% | 100% |
| A1 | 91% | 100% | 100% |
| V3 | 91% | 94% | 96% |
| S3 | 90% | 93% | 100% |
| A3 | 86% | 93% | 100% |
| A2 | 87% | 100% | 100% |

These are over the non-NULL rows (strict floor). The confusion counts per cell
are in an. C.2.

### C.3 The decision table, priced (house style: declared rows, priced argmin)

`FORM_ROWS` in `costmodel.py`, one row per form. Columns:
- `layer`: the build that may offer the row (off = SIMD-off, on = `-fmemfn-simd`);
- `needs`: a fact that must hold for the row to apply;
- PRICE: the C.1 delta, with the walk priced 0.

The regime is NOT a column. It is a function of the facts the price reads, so an
applicable row is priced in every regime, and the regime only decides which term
dominates the price.

| row | form | layer | needs | price |
|---|---|---|---|---|
| walk | 256-byte table walk | off | — | 0 |
| mask8 | SWAR mask, W=8 (R17-b) | off | — | C.1 with V1 constants |
| mask8+head | + alignment prologue | off | — | V2 |
| mask8+keep | + state kept across calls | off | find-all iterator (D165) | V3 |
| sse2 / sse2+head / sse2+keep | W=64 SSE2 | on | — / — / iterator | S1 / S2 / S3 |
| avx2 / avx2+head / avx2+keep | W=64 AVX2 | on | — / — / iterator | A1 / A2 / A3 |
| (P2, P3 k-position filters) | multi-position class filter | off/on | ≥ 2 filterable positions | A.6's form; needs the JOINT candidate rate, which the C.1 facts do not carry; not wired into the argmin |

The priced argmin uses oracle workload facts (each row's own λ, φ, α) and is
compared with the measured fastest applicable row (an. C.3):

| layer, iterator | DINGHY: agree, regret | TUG: agree, regret | LINER: agree, regret |
|---|---|---|---|
| off, no | 40/47, +128,794 ns (0.81% of walk) | 27/35, +70,860 (0.34%) | 15/34, +10,132 (0.32%) |
| on, no | 31/47, +497,547 (3.11%) | 20/35, +133,826 (0.65%) | 22/34, +4,245 (0.14%) |
| on, yes | 29/47, +662,980 (4.15%) | 12/35, +150,609 (0.73%) | 15/34, +6,706 (0.21%) |

The argmin often picks a different row from the measured best (agreement 34-85%).
Even so, the regret stays under 1% of the walk except in SIMD-on DINGHY. The rows
near the top cost about the same, so a wrong pick among them is cheap.

**The decision the data support, per regime.** The best single row per regime
(an. D.1) is within the noted regret of the per-row oracle:

| layer | DINGHY | TUG | LINER |
|---|---|---|---|
| SIMD-off | walk (regret 0.8%) | walk (0.1%) | mask8 (0.2%) |
| SIMD-on, no iterator | walk (3.1% in-sample; 9.1% leave-one-cell-out) | avx2 (0.0%) | avx2 (0.1%) |
| SIMD-on, iterator | avx2+keep (2.8%, the same out of sample) | avx2 (0.1%) | avx2 (0.7%) |

Readings:
- **The prologue (head) never ranks first in any regime.** It helps bounded's
  near hits at W=64 (reading §3.4) and hurts hex-run at 1 MiB.
- **KEEP pays only in DINGHY**, and only at W=64.
- **The P2/P3 filters are a TUG row for candidate-bound sites.** In vecspike2
  they beat every single-position form in TUG: P3a −5.67 ms against A1
  −1.35 ms. A table that carried them would price them by A.6.

## D. WHAT INFORMATION DECIDES

### D.1 Each estimator input and where it could come from

| input | compile-time only | exemplar (`pcrec-analyze`) | user hint | run time |
|---|---|---|---|---|
| terms, set, kind, positions | exact (the kit's cover; `mf_site`) | — | — | — |
| p (byte density of S) | the shipped prior `src/findings/default.rxt` (unigram, always sent, D162 add. 2) | exact for the exemplar: `freq` kind (counted today) | — | free inside a block (the mask's popcount) |
| λ (landings) | independence p(1−p) from the prior: good for dense letter sets, wrong where the subject's alphabet differs (dig on prose: 0 vs 0.069 assumed; dig on code: gap 117 B vs 14.5 assumed) | exact for the exemplar: Σ over a∉S, b∈S of the `bigram` kind, which `pcrec-analyze --scan freq,bigram` already counts by default; the shipped `log`/`weblog` bundles carry no bigram; the compiler's bigram reader is held ([FINDINGS.B4]) | "sparse / dense candidates" | the kept state sees it per block |
| α (span per call: matches per byte for find-all, distance to the first match for first) | NOT derivable from byte statistics; the API mode (find vs find-all) is not visible at compile time either | not from byte counts; needs a PATTERN-specific profile (declined, D83 (2)) or match counts on the exemplar | "short subjects / dense matches" vs "long subjects / sparse matches": the regime itself | the iterator (D165) sees every call's span; this is [OPT-HYB-RESEED-XCALL]'s hint, carried in the one struct |
| joint candidate rate (P_k) | not from unigram (wingame: the unigram table misses survivor rates by 21x-1,750x) | from `bigram` for 2 adjacent positions; 3+ positions need trigram (declined, docs/design/findings/design.md §17) | — | the filter's own counts |
| fresh vs repeated subject | — | — | "the same buffer rescanned" (rare) | — |

The findings design already declines "gap / burstiness, set-membership run
length" as kinds (findings design §17). Its trigger is "C5's restarts pay arm or
C7 landing with a measured cell". The DINGHY rows here are cells where restarts
pay. Whether that meets the trigger is main's ruling, not this report's.

### D.2 The regret of each source, per regime (an. D.1)

Regret = measured ns of the policy's pick − measured ns of the fastest applicable
row, summed over the regime's spike rows, as % of the walk. Absolute ns per pass
are in an. D.1.

SIMD-off (rows: walk, mask8, mask8+head):

| policy | DINGHY | TUG | LINER |
|---|---|---|---|
| always walk | 0.8% (+129 µs) | 0.1% | 29.2% (+916 µs) |
| always mask8 (R17-b as shipped) | 7.5% (+1.20 ms) | 7.2% (+1.49 ms) | 0.2% |
| prior ≥ 100k declines (r17loss, compile-time only) | 0.7% | 0.3% | 0.6% |
| setfind §9.2 rule (prior ≥ 300k AND measured uses/activation < 3) | 1.1% | 7.2% | 0.2% |
| model with prior facts | 0.7% | 0.3% | 0.6% |
| model with an exemplar's p and landings | 0.8% | 0.3% | 0.3% |
| regime from the prior's gap (span unknown) | 0.8% | 0.1% | 12.3% |
| regime from an exemplar's gap (span unknown) | 0.8% | 0.1% | 0.2% |
| regime hint → walk/walk/mask8 (leave-one-cell-out: the same) | 0.8% | 0.1% | 0.2% |
| model with oracle facts | 0.8% | 0.3% | 0.3% |

SIMD-on, no iterator (rows: the above + sse2, avx2 with and without head):

| policy | DINGHY | TUG | LINER |
|---|---|---|---|
| always walk | 3.1% | 18.6% | 80.6% |
| always mask8 | 9.8% | 25.6% | 51.6% |
| always avx2 | 7.2% (+1.16 ms) | 0.0% | 0.1% |
| prior ≥ 100k declines | 3.0% | 18.7% | 52.0% |
| model with prior facts | 13.4% | 0.6% | 0.1% |
| model with an exemplar's p and landings | 12.5% | 0.7% | 0.1% |
| model with an exemplar + the call pattern | 3.1% | 0.7% | 0.1% |
| regime from a gap (prior or exemplar; span unknown) | 7.2% | 0.0% | 0.1% |
| regime hint → walk/avx2/avx2 | 3.1% (LOCO 9.1%) | 0.0% | 0.1% |
| model with oracle facts | 3.1% | 0.6% | 0.1% |

SIMD-on, with the iterator (adds sse2+keep, avx2+keep, mask8+keep):

| policy | DINGHY | TUG | LINER |
|---|---|---|---|
| always avx2 | 18.8% (+3.0 ms) | 0.1% | 0.7% |
| **always avx2+keep (no information)** | **2.8%** | 4.0% | 1.9% |
| model with prior facts | 24.9% | 0.7% | 0.8% |
| model with an exemplar + the call pattern | 4.2% | 0.7% | 0.2% |
| regime hint → avx2+keep/avx2/avx2 (LOCO 2.8/0.1/2.5%) | 2.8% | 0.1% | 0.7% |

### D.3 Regime information vs within-regime information

- **SIMD-off: the decision is LINER or not.** mask8 in LINER, the walk
  elsewhere. The fact that decides it is the GAP (landings). An exemplar's
  bigram gives it exactly (0.2% regret). The prior gives it well for dense
  letter sets and badly where the subject's alphabet differs: dig is a
  LINER mistaken for a TUG, 12.3% regret in LINER. The span is not needed,
  because DINGHY and TUG pick the same row.
- **SIMD-on without the iterator: the decision is DINGHY or not.** The walk in
  DINGHY, avx2 elsewhere. The fact that decides it is the SPAN, and no byte
  statistic carries it: every gap-only policy sits at 7.2%. Only the call
  pattern (a hint, a pattern-specific profile, or run time) gets to 3.1%. Even
  learned leave-one-cell-out, the DINGHY row is not stable (9.1%). Some dinghy
  passes favour AVX2 (hex-run at 1 MiB) and others the walk (bounded
  everywhere).
- **SIMD-on with the iterator: almost no information is needed.** avx2+keep
  everywhere regrets 2.8 / 4.0 / 1.9%. Dropping KEEP where activations are long
  (TUG/LINER) saves 2-4% more and needs only the span.
- **So the information mostly picks the REGIME.** Within a regime one fixed row
  is within 0.1-3% of the per-row oracle on this table. The model's finer
  per-row pricing adds nothing measurable over the regime hint, and its DINGHY
  pricing is the weakest part of the fit (A.4).

### D.4 Runtime adaptivity

setfind §9.1 did not build the adaptive switch. Its measured cost in slot2
(an. D.2), adapt_swar against the best SIMD-off form, by median:
- 1.6-3.2x on dense rows with the state kept;
- 1.05-1.37x with the state lost per hit;
- 1.2-1.5x on percall spans.

The mode branch itself mispredicts 0.63 times per call at 300k (setfind §9.1).
As built, it observes the per-use skip, which pays per use.

INTERPRETATION: the observation that decides the dinghy question is the call's
SPAN, not the per-use skip. The span is available once per CALL, in the D165
iterator that carries the kit's state across calls ([FINDALL-NEXT];
[OPT-HYB-RESEED-XCALL]'s hint lives in the same struct). Its cost is one
comparison per call against a 2-20 ns call. Batch mode (ideas.md 2026-10-13)
would get the same fact as a popcount. Neither has been measured (§F7).

## E. RULES OF THUMB, by regime (box: Zen 4, gcc 15.2; kit tier, UNOFFICIAL)

**Placing the regime**
- **R0. Place the regime from two facts: L (bytes advanced per call) and g
  (bytes advanced per candidate).** DINGHY: L < 64 B. TUG: g < ~18 B in long
  calls. LINER: g ≥ ~18 B. Byte density p is not the variable, landings are;
  measure gaps by landings (S-runs), not by members.
  - Evidence: an. B.1 (gap bins clean, p bins blurred); bounded and hex-run on
    prose.
  - Confidence: high on this table.

**DINGHY (fixed costs dominate; judge by ns per call and by never-worse)**
- **D1. SIMD-off: take the walk.** The SWAR mask form loses +1.5 ns per cold
  use, and on dense 1 MiB text that sums to +0.6 ms per pass.
  - Evidence: V1 DINGHY 6/14/3 (all-mode) and 3/21/0 (first); regret 0.8% for
    the walk against 7.5% for mask8.
  - Confidence: high.
- **D2. SIMD-on without carried state: take the walk.** A W=64 block costs
  4.5-5.4 ns per activation and evaluates ~59 B past each hit.
  - Exception: dense find-all on fresh 1 MiB text with an unpredictable skip
    (hex-run 1M), where AVX2 wins 125-137 µs per pass.
  - Evidence: A1 DINGHY 6/14/3; regret 3.1% for the walk against 7.2% for avx2.
  - Confidence: medium. The leave-one-cell-out row flips (9.1%).
- **D3. SIMD-on with the find-all iterator: take W=64 + KEEP.** It turns cold
  uses into warm ones; A3 DINGHY is 10/10/3 with a net −1.9 ms (S3 −1.6 ms).
  - Evidence: an. A.3 (cold +4.65 ms → +269 ns); regret 2.8%, the same out of
    sample.
  - Confidence: medium. A3 is a hand-edit, and D165's iterator owes its own
    parity measurement.
- **D4. Single calls that match in a few bytes cannot be helped by state.**
  They lose +0.2 to +26 ns at every width. Accept it: the absolute sum over all
  24 such spike rows is +76 ns (V1). Prefer the form with the lowest fixed
  cost: the walk, or the stateless SIMD per slot2 (§F6).
  - Evidence: an. 0.5 first mode, B.4.
  - Confidence: high.
- **D5. Subjects shorter than one block: no W=64 form.** On 40 B subjects S1
  loses +49% to +339%. A1 loses +39% to +168% wherever it loses; dig short is
  the one exception, a −6% to −8% win.
  - Evidence: an. B.4; regimefacts §2.1 (n\* ≈ 1 KB for the SIMD forms).
  - Confidence: high.

**TUG (per-use costs dominate; judge by ns per MiB)**
- **T1. SIMD-off: take the walk.** SWAR's 0.08 ns/B saving does not cover
  ~1 ns per warm use plus overscan below g ≈ 16-26 B.
  - Exception: VM hats, where a use costs ~0 (vm-hat wins at 64 KiB and loses
    +0.4-0.5 ns/use at 1 MiB).
  - Evidence: V1 TUG 3/14/1, +1.14 ms; regret 0.1% for the walk.
  - Confidence: high for PF and DFA-hat sites; medium for VM hats.
- **T2. SIMD-on: take W=64, AVX2 over SSE2.** KEEP only adds machinery here
  (the state already carries within the one call).
  - Evidence: A1 TUG 16/0/2, −2.9 ms; A3 adds +0.8-1.1 ns per use with 0-2%
    reuse (reading §2.2); regret 0.0%.
  - Confidence: high.
- **T3. A candidate-bound TUG site with ≥ 2 filterable positions: filter on
  them.** Use P2 at SWAR and P3 at W=64. The extra positions remove 85-99% of
  the candidates.
  - P3s/P3a: −5.5/−5.7 ms against −1.2/−1.3 ms for P1. P2w turns SWAR from
    +0.86 ms to −3.9 ms.
  - Decline them where the site has no candidates: +89-692% over P1.
  - Evidence: an. 0.6, A.6.
  - Confidence: high on dfa-hat, the only cell measured.

**LINER (bytes dominate; judge by ns per MiB, i.e. throughput)**
- **L1. Take the widest block the layer offers.** SWAR saves 0.08 ns/B (−40%),
  SSE2 0.168 (−82%), AVX2 0.179 (−87%). Every LINER row wins at every width.
  - Evidence: an. 0.5; regret 0.1-0.2%.
  - Confidence: high.
- **L2. KEEP and the prologue add nothing.** Kept rows sit within 0-2 points of
  their unkept twin's median (V3 −38.8% vs V1 −40.4%; A3 −86.6% vs A1 −86.5%),
  and keep's LINER regret is 1.9% of the walk. The prologue is within 1 point.
  - Evidence: an. 0.5, D.2.
  - Confidence: high.
- **L3. At SWAR, the term count sets the bar.** With 3 terms the saving falls to
  0.022 ns/B (DERIVED) and the break-even gap rises to 65-108 B. The SWAR cover
  stops paying at about 4-5 terms (slot2 synthetic cells).
  - Evidence: an. A.1, B.2.
  - Confidence: medium (3 terms DERIVED).

**Across regimes**
- **X1. The information buys the regime; within a regime one fixed form is
  within 0.1-3% of the oracle.**
  - SIMD-off needs the GAP: bigram, from an exemplar, or the prior for dense
    letter sets.
  - SIMD-on without carried state needs the SPAN: call pattern, from a hint or
    run time.
  - SIMD-on with carried state needs little.
  - Evidence: an. D.1.
  - Confidence: medium. It is one table, and the subjects are contrived at the
    extremes.
- **X2. Decide on 1 MiB-scale, fresh-data measurements, not 64 KiB repeats.**
  The walk learns a repeated 64 KiB stream, which makes every form look worse
  there.
  - Evidence: A.4; reading_slot2 §"measurement artifact".
  - Confidence: high on the direction.

**Metrics the kit should record per site** (the MF_TRACE rendering already
counts most of these; setfind §12.4a files `mfk-upa`):
- activations (calls reaching the site);
- uses;
- bytes advanced, so that L and g fall out;
- block evaluations, so that the overscan falls out;
- cache-served uses and uses served from an earlier call (KEEP's value);
- head-served uses;
- for multi-position forms, candidates handed on per k;
- histograms of uses per activation (`mfk-upa`: the TUG/DINGHY split) and of
  the skip per use (branch predictability);
- per measured cell, the branch-miss rate of the walk and of the form (perf):
  the variable the model lacks.

## F. OWED measurements (named, NOT run)

| id | what | cells | expected rows | wall time (estimate) |
|---|---|---|---|---|
| F1 | **The controlled grid.** regimefacts §4.1, extended with this report's SPAN axis and a FRESH axis. Synthetic subjects at controlled landing gap g ∈ {2, 4, 8, 16, 32, 64, 256, ∞}, call span L ∈ {8, 32, 128, 1 Ki, 64 Ki} (find-all with a match every L bytes, and `first`), and subject reuse ∈ {repeated 64 KiB, streamed distinct buffers totalling 64 MiB}, on forms {walk, V1, S1, A1, V3, S3, A3, stateless sse2/avx2}. Kit `drv.c` loop, A/A pair, 5 launches, counters on every cell. | fractional design: 9 forms × 8 g × 3 L × 2 reuse = 432 arm-cells; plus the full L axis at g ∈ {4, 64} on walk/V1/A1/A3 (40) | ~470 timed rows + 47 counter rows | ~45-60 min at ~5-7 s per arm-cell (5 launches × (calibration + 7 × 50 ms)); the official tier repeats it on ubuntubudu (Zen 1) by a bench slot request |
| F2 | **perf branch-miss pass** on the 1 MiB dense rows the model misses: hex-run, bounded, dfa-hat × {prose1m, docs1m, code1m} × {walk, V1, A1, A3}, plus the same at 64 KiB as the learned-predictor control | 72 perf runs | 72 | ~10 min |
| F3 | **3- and 4-term sets, sparse.** word-eq (3 terms) and a 4-term cover on a subject containing none of S (digits64k, prose1m), to MEASURE β for 3/4 terms per width | 2 cells × 2 subjects × 13 variants | 52 | ~5 min |
| F4 | **The real iterator.** Once D165 builds: avx2+keep and mask8+keep through the iterator on the DINGHY rows (hex-run, bounded, dig digits/mix, all mode), against today's hand-edit A3/V3 and the walk. D165's own named parity measurement (`a` over `aaaa`, `\w+` over prose, a one-byte subject) belongs in the same slot. | 6 cells × 9 subjects × 4 arms | ~216 | ~25 min |
| F5 | **Zen 1 replicate** of the per-form constants (β_t, β_f, c_cold, c_warm) on ubuntubudu. These are the official-tier constants (D144 add. 4); requested through the bench, never run by the kit. | the 12 sparse rows + 12 dense rows of A.1/A.2 × 13 variants | ~300 | ~30 min in a bench window |
| F6 | **Stateless SIMD in the pipeline at DINGHY spans.** slot2 says stateless sse2/avx2 beat the stateful mask64 at L16/L64 dense by 1.2-1.6x; it was never timed through `rx_search`. hex-run, bounded, dig × all subjects × {walk, A1, stateless avx2, A3} | 3 × 9 × 4 | 108 | ~12 min |
| F7 | **The span hint's cost.** One comparison per call in the iterator, choosing walk vs avx2 from the previous call's span, on the DINGHY and TUG rows. This is the observation that would replace the per-use adaptive switch. | 8 cells × 9 subjects × 3 arms (walk, avx2, span-switch) | ~216 | ~25 min |
| F8 | **The P_k price with joint rates.** vecspike2's dfa-hat arms on subjects with controlled pair survival (bigram-shaped), to test A.6's cost = β_Pk + c_cand·r_k beyond one cell | 1 cell × 6 synthetic subjects × 12 arms | 72 | ~8 min |

## Standing design questions (docs/design/CLAUDE.md)

- **Measurement regime: RELEVANT.**
  - Every constant is from one box (Zen 4, gcc 15.2 -O2, CPU 14) at the kit
    tier, UNOFFICIAL (D144 addendum 4). The official verdict is a bench run on
    each targeted box (F5).
  - The 64 KiB rows are repeated subjects and pessimistic for every form (X2).
  - ALPHA was taken at load1 0.72.
- **Independent control: RELEVANT.**
  - The ALPHA run is out of sample for the spike-fitted V1 model (A.5).
  - Leave-one-cell-out checks both the fits (A.2 LOCO) and the regime hint
    (D.2).
  - slot2 is a population with no consumer and i.i.d. placement, disjoint from
    the spike's (B.3).
  - The counting pass reproduces r17loss's counts byte for byte.
- **What moves when data is regenerated: RELEVANT.** `costmodel.py` recomputes
  every table from the inputs. The FITTED constants move with any new timing
  log. The MEASURED per-byte rates move with box or compiler. The regime
  boundaries move with the walk's fitted u/b_skip, and are re-derived, not
  pinned.

## Interpretations flagged (not measurements)

- **§0.3: "low density is the likely case" holds for bytes in throughput work,
  but bench CALLS are mostly dinghies.** This reads regimefacts' bench
  population against Frank's sentence.
- **§0.4: ALPHA over-represents dense 1 MiB find-all.**
- **§A.4: the cause of the 1 MiB misses is branch prediction.** It is inferred
  from walk ns per call and skip-length predictability; there is no perf count
  (F2).
- **§D.4: the span is the observation to learn at run time, once per call in
  the iterator.** This is an inference from D.3, unmeasured (F7).
- **§B.5: real text sits mostly in TUG/LINER.** This is 4 real-text subjects,
  not a census.

## Charter vs committed

| charter item | committed |
|---|---|
| 0. Regimes from the data, boundaries from measurable facts, every row placed, ALPHA + spike variants re-scored in absolute ns and ns/MiB beside the ratio tally | §0.1-0.6; an. 0.1-0.7 (placement of all 116 spike groups and all 160 ALPHA rows) |
| A. Per-form mechanical terms (setup, per-use, per-block, verify, tail, wasted scan, misprediction), fitted from counters against ns across both logs and ALPHA, fit quality, misses explained, compile-time vs subject facts | §A.1-A.7; misprediction is a fitted fresh-subject term plus a named miss, because no counter records it (F2) |
| B. Density: win/loss against p AND gap, crossovers per form/width and how they move with terms and KEEP, non-density losses, representativeness | §B.1-B.5 |
| C. Closed-form estimator, labelled constants, confusion per regime, decision as a declared row table with a priced argmin | §C.1-C.4; `costmodel.py --price`; P_k rows declared but not priced (needs a joint rate) |
| D. Information sources (compile-time, exemplar, hint, runtime), regret in absolute terms per regime, regime vs within-regime | §D.1-D.4 |
| E. Rules of thumb by regime with evidence, scope and confidence; per-site metrics | §E |
| F. Owed measurements with cells, rows and wall time | §F (F1-F8) |
| scripts runnable with `python3 -I`, report committed, CLAUDE.md entry | `docs/dev/lanes/costmodel/` (own CLAUDE.md), `docs/dev/lanes/CLAUDE.md` one line |
| no timing, no make, nothing under src/ or memfn/src/ | held: one counting pass (no clock), one `gcc -O2` per cell into the scratch directory |

## Files

- `docs/dev/lanes/costmodel/costmodel.py`: the analysis and the estimator (`--price`).
- `docs/dev/lanes/costmodel/cmload.py`: loaders and compile-time facts.
- `docs/dev/lanes/costmodel/subjstats.py`, `subjstats.tsv`: subject facts.
- `docs/dev/lanes/costmodel/analysis.txt`: the full output.
- `docs/dev/lanes/costmodel/data/`: the measured inputs (`SHA256SUMS`).
- `docs/dev/lanes/costmodel/count9.sh`, `count_instrument.py`, `count_cnt.c`:
  the counting pass.
