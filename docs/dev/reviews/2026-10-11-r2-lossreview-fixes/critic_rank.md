# lrpanel_rank: D6 critic, SELECTION AND ARITHMETIC lens, on lossreview/fixes.md §2-§5

Read-only critic. No make, nothing committed. Files read (all under docs/dev/optloop/): lossreview/fixes.md, dfa.md, vm.md, misc.md, vm/cells.tsv, vm/gcov_counts.tsv, dfa/data/rollup.tsv, misc/data/cells.tsv, judgement_gapreport_2026-10-11.md.

## 1. Arithmetic: what reproduces and what doesn't

Reproduces:
- DFA 29 cells / 51,178,308 ns; VM 34,603,784 ns; misc 25 cells / 8,562,678 ns; sum 94.345 ms.
- C1 27.195 ms (27.186 on throughput cells); concat-sqli plus C1 throughput = 59.4%.
- Every §4 median ratio, and the per-cause totals used in candidates 5, 6, 8, 9.
- bak-2 growth 2.31 ms; R-1 ratios 1.95x and 2.71x (364,078/187,022; 724,503/267,480).

Does not reproduce:

| # | Sev | fixes.md says | Phase-1 data gives | Disposition |
|---|---|---|---|---|
| 1.1 | major | §0 item 3 / cand 1: "4.7M PLT seam calls ... = 7-19 ms" | Measured span_match_calls: mod-j-uc 727,369; bak-1 726,049; bak-2 794,481; phone 240,718 (sum 2.49M). With bak-py and bak-g-rel at bak-1's value (never gcov'd), the six throughput cells total 3.94M. 4.7M equals phone's hat-seek iterations (4,681,579), probably a conflation. At 2-4 ns: 7.9-15.8 ms. | Fix count and range; bak-py/bak-g-rel unmeasured. |
| 1.2 | minor | C1 "10 cells" (§0 table, §4 table, §0 item 4) | 11 cells = 6 throughput + 5 short. | Fix. |
| 1.3 | minor | "37 cells" VM, "7 of 91 cells" | 34 attributed VM cells (27 throughput + 7 short). The 37 includes 3 listed-only cells (github-pat, level-context x2). Attributed total 88, not 91. | "7 of 88". |
| 1.4 | major | §0 item 1: four families "cover about 90% of the 94.3 ms" | §1 table sums to 17.41 + 17.41 + 27.46 + 32.06 = 94.34 = 100%; every cause is assigned. Text also says F1/F2 overlap on DENSE-SKIP, but DENSE-SKIP appears only in F1. | The two statements can't both hold. Say "100% by construction" or fix the table. |
| 1.5 | minor | cand 5 "~22 ms" | 22.28 ms only without C1c; with C1c's 2.3 ms it is 24.6, and that 2.3 is already inside C1's 27.19. | State which. |
| 1.6 | minor | §0 item 4 median-ratio top 3: RUN-PICK 9.5 > ATTEMPT-SHAPE 4.8 > U8-PICK 2.9 | §4's own table has C7 x10.7 jit / x39.8 re2 and S5 x3.8 above those; ATTEMPT-STEP (email-owasp) is x7.22 jit. | Fix the sentence. |
| 1.7 | minor | "ATTEMPT-SPLIT ranks 7th" | It is step 8 in the §3 table. | Align. |

## 2. Weighting and re-ranking

Reach and reached-cell ratios (cand 5 without C1c; cand 3 = HIT-RESTART + K101 + C3 + stop cost):

| cand | reach ms | cells | max ratio | median ratio |
|---|---|---|---|---|
| 7 ATTEMPT-SPLIT | 28.87 | 1 | 4.80 | 4.80 |
| 1 seam inline | 27.19 | 11 | 1.59 | 1.27 |
| 5 admission + FIND | 22.28 | 17 | 7.35 | 1.80 |
| 4 trail-free | 17.74 | 9 | 1.55 | 1.27 |
| 6 stay | 13.74 | 9 | 2.59 | 1.60 |
| 3 R4d | 8.76 | 30 | 8.20 (2.98 excluding synthetic litrun) | 1.45 |
| 8 PRIOR-COST pick half | 2.68 | 4 | 10.7 (39.8 vs re2) | ~8.4 |
| 9 small items | 2.10 | 4 | 2.74 | 1.96 |
| 2 D160 | 1.17 | 6 | 10.55 | 2.54 |

Ranks (proposed §3 order is 1,2,3,4,5,6,7,8,9):
- (a) total ns: 7, 1, 5, 4, 6, 3, 8, 9, 2.
- (b) cell count: 3 (30), 5 (17), 1 (11), 4 and 6 (9 each), 2, 8 and 9 (4 each), 7 (1).
- (c) worst ratio: by max 8, 2, 3, 5, 7, 9, 6, 1, 4; by median 8, 7, 2, 9, 5, 6, 3, then 1 and 4 tied.

Moves against the proposed order: cand 7 goes 8th -> 1st on ns, 2nd on median ratio, last on cells. Cand 2 goes 2nd -> last on ns. Cand 8 goes 8th -> 1st on ratio. Cand 1 is last on ratio. Cand 3 falls to 6th on ns and 7th on median ratio.

**2.1 (major).** §4's claim that "1, 3 and 5 rank high on every ordering" is false for 1 and 3. Cand 1 is lowest or near-lowest on either ratio view (x1.27 median, non-algorithmic, which §4's own table says). Cand 3 is 6th on ns and 7th on median ratio. Only 5 stays top-5 throughout, and 59% of its reach is DENSE-SKIP, which has no timing yet. Cand 1 can still go first as the cheap, certain step gated by the modj-static-seam twin; that is a cost argument, not a ranking-robustness one.

**2.2 (major).** The pooled 94.3 ms mixes baselines.
- 17 of lrmisc's 25 cells (6.28 ms, 73% of its 8.56) have rust as the comparator.
- lrdfa lists rust-only (9 cells, 4.06 ms) and SCAN-SIMD (17 cells, 7.42 ms) apart as "not attributed".
- Cand 5's cube-SWAR 3.85 ms is rust-only (SIMD) loss, so it sits inside the ~22 ms reach under a rule lrdfa and lrvm did not apply.
- The ratio columns mix jit, rust and re2 as the peer.
Disposition: tag every reach with its baseline (scalar peer / jit-only / rust-only) and report the D119-eligible subtotal beside the pooled one.

**Recommendation.** Weight by total expected recoverable ns. Cell count and ratio are gates and tiebreaks only. Reasons:
- ns is the only unit additive across candidates.
- Cells are not independent. The 88 attributed cells are syntax 37 (42%, 35.0 ms), utf8 19, capability 16, bounded 8, litrun 6, loglines 2. Syntax and litrun are the synthetic-leaning sets.
- The 14 HIT-RESTART cells are about four artifact shapes; 19 of cand 3's 30 cells are `syntax`.
- Ratio is dominated by ns-scale cells and by jit or SIMD peers (e.g. x39.8 on 62 us; x10.5 vs rust).
Two adjustments:
- Subject size: set-grain ns scales with subject bytes (1 MiB subjects), so report ms and ns/byte together.
- Single witness: handle ATTEMPT-SPLIT's single-witness status with a flag, not a down-weight. It is algorithmic (re2 x4.80), ratified, and the exact twin exists.

**2.3 (major).** Cand 3's reach leans on the DENSE-group cells. 9 of the 14 HIT-RESTART cells sit at x1.26-1.29 vs jit, with jit's measured p5-p95 drift at 0.924-1.052. The manager's call (f) in judgement_gapreport_2026-10-11.md left "DENSE (<= x1.68)" unfiled as near-noise on cross-window data, and fixes.md never reconciles this. It should say why R4d is exempt (kit-owned, trigger met at SIMD-off).

**2.4 (minor).** The "50-80% of these cells' time is memchr calls" figure is circular: it takes dfa.md's "auto_ns per memchr call 10-17 ns" (cell ns / calls, including verify and DFA work), then multiplies by ~12 ns. misc's independent fit prices a stop at 8.7 ns, about 56% on lit-cat. Also 1.14 of the 1.43 ms of stop cost is the synthetic litrun cells lit-l8 and alt-foo-tails.

## 3. Double counting and remodel overlap

Overlaps fixes.md states: DENSE-SKIP 13.23 in 5(a) and 6; concat-sqli residual in 5 and 6 (not quantified).

Overlaps it doesn't state:
- PAIR-SKIP 1.36 is in cand 5 and in 3 ("in part").
- ci-moskva 0.82 is in 
[REMAINDER, relayed by message]
ci-moskva 0.82 is in candidates 5 and 8. RUN-PICK 1.76 in 3 and 8. qnt-poss-quest (C4, part of 1.83) in 9 and 5's retry half (moot if language rewrite lands). Frameless C1 pool (5 cells, 17.74 ms): cand 1 upper 3.21M x 4 ns = 12.8; cand 4 upper 11.4; C1c 2.3 -> 26.5 > pool. mod-j-uc (9.45 ms framed) reached only by cand 1 (1.5-2.9 ms); remaining 6.5-8 ms has NO candidate.
3.1 MAJOR remodel overlap (D153): 5(a), 6, 8 touch [PRIOR-COST-UNIFY] sites (cand 6 header omits pick_skip_states = F1 member 11). Cand 1 "none" is wrong-ish: abi event ordering vs L1; N7 loop kit-rendered inside entry (PcrecEncSite, M7 pins, S513/S517), inline_def moves placement; verify C17/C12. Cands 3, 5(b) land in kit files with in-flight rows (precheck.c, fn_rows[] with R-15, R-16, slot21); 2:1 migration:SIMD split, R4d fits neither pool.
4 Q dispositions: Q1 already ruled (D122 add.3 "SWAR is fine" 2026-09-25; D147 add.6/Q50 integration.md §R4.3.1 SWAR+libc scalar layer) -> drop Q1 and "Q1 gates it" from cand 3, §3 steps 3/5. Q2 manager can run attemptcensus (compile-only) now; "ready the moment Frank rules Q2" misstates blocker. Q3 manager's call (match_api.md §3¶2: entries not caller contract) -> grep readers + abi ritual. Q4 Frank's (overrides his queue/D153); split: DFA-hat half unsupported (D77 not met until plainloop timed), VM-hat half supported. Q5 manager's. Q6 round order Frank's; abi batching + filing R4d R-n manager's (file now).
4.2 MINOR missing Frank question: the weighting rule (D119 priority); judgement call (a) "owner-actionable then size" vs fixes.md §3 "cheap-and-certain" — reconcile.
