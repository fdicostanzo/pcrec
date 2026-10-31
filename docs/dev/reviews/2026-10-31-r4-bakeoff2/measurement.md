# MEAS findings: bakeoff2 (pricing_bakeoff.md rev 1 @ deebb4dd8)
Lens: is the re-cast timing plan (§5: grid1 primary, bench C-XH cross-check, §5.4, §5.6) trustworthy. No timing run, nothing built; all by reading and arithmetic.

## Findings

### MEAS-1 The ORACLE_CMD gate does not check the bake-off's arms against libpcre2 (ext cells have no leg O)
- status: CONFIRMED
- severity: design
- effort: medium
- blast radius: a base (default compile) that is wrong passes the gate whenever its arms agree with it; the "answers equal libpcre2" claim of §5.5 / G2 is undelivered for every ext cell, i.e. the whole bake-off.
- where: §5.5, §8 row "a timed arm is wrong", §11 stage 0 (cost); grid1 `check.sh:5-8,53-55`, `checklib.sh:18-20`, README "Subjects from an external set" ("no python oracle, so legs R, L and C check them against the cell's base only").
- finding: grid1 leg O compares the base to `oracle.tsv` and ONLY for the six own cells (`dig bounded dfa-hat hex-run word-eq quad`); `ORACLE_CMD` only replaces how the own cells' `oracle.tsv` is produced. Ext arms get R (equal to the cell's base), L, C. Nothing compares an ext cell's base to libpcre2. grid1 hashes only group 0 (`gdrv.c` pass(): `cp[0][0]`, `cp[0][1]`), so "captures where requested" (§5.5) are not compared by any leg either. The 14 plants are SIMD-lane / driver plants on the own cells (`plants.sh:26-35`); they show the machinery works there, not that a wrong pcrec route is caught.
- repro: read `check.sh` header (legs O "own cells"), `checklib.sh:18`, `gdrv.c:pass`; grep ORACLE_CMD shows one use, `check.sh:54`.
- proposed fix: cost a new leg O for ext cells (libpcre2 adapter -> per (cell, window, mode) match/hash line in gdrv's fold, plus a captures hash), and say the hand-broken ext arm must be a BASE-wrong case too.

### MEAS-2 The bench's call-stream cannot (as documented) be handed a window-end, and the cited fallback is the wrong mechanism
- status: CONFIRMED (the doc mismatch); SUSPECTED (the cost)
- severity: design
- effort: medium
- blast radius: C-XH's LONG cells either time O(tail) scans for no-match windows (inflating exactly the arms that search most) or an anchored search (a different operation than find-first/find-all); the cross-check then disagrees with grid1 for harness-protocol reasons, and rev 1's red reading ("one of the harnesses has a defect") misattributes it.
- where: §5.1 "What the bench answered" (Streaming T1), C-XH paragraph, §5.3 LONG; unusual_set_v1.md §7.1 (lines 599-625), b148l4_report.md:21,48-52.
- finding: (a) §7.1: "the engine is given the rest of the subject from the call's offset"; the call's `length`/`segment_bytes` is only the throughput denominator. (b) The L4 fallback the design cites (`stream_anchor = explicit`) means PCRE2_ANCHORED / `onig_match` etc.: anchor the match AT the offset. It bounds a `\G`-anchored cscan pattern; for an arbitrary unanchored census pattern it changes the operation timed (match-at-offset, not search). L4's own control: cscan with `\G` removed reads 8.2x/14.0x for a 10x tail (b148l4_report.md:50-52). So "enforce the window end as the call's length" is a new protocol change (pass offset+length as n), not an existing fallback. (c) Per-call tokens are `n | m:s,e | r`: one match per call (group 0, group 1). LONG is "find-all over each window" (§5.3); a find-all call kind is not in §7.1 either.
- repro: read unusual_set_v1.md:605-625 and :655-660 against §5.1 lines 607-612 and 643-644.
- proposed fix: say "new bench work: a call kind with a bounded subject length (and find-all)", cost it in §11 (it is in B7 only as a question), or make C-XH SHORT-shaped first-match with line-sized subjects where the rest-of-subject problem does not arise.

### MEAS-3 The "2-7 % noise floor" is CPU occupancy, not timing noise, and the "+4-5 % same-pin offset" is cross-WINDOW
- status: CONFIRMED
- severity: answer (for C-XH's pass rule) / doc
- effort: small
- blast radius: C-XH's "both harnesses' floors ... its stated 4-5 % short-cell offset" admits or excludes sites on a floor that means something else.
- where: §5.1 lines 618-622 and 645-646, B8; bench quiet_baseline.md:40 ("noise floor is ~2-7 % busy per core"), :129; decisions.md:135; first-window-614d45eb3.md:97,213; dev_journal.md:6720.
- finding: quiet_baseline's 2-7 % is the idle per-core BUSY percentage mpstat reads (the pre-flight bar is 10 %); it says nothing about the spread of a timed cell. The +4-5 % is a shift in short cells between the 10-26 and 10-28 WINDOWS at the same pin, traced "to our own harness change; not isolated". A single window's A/A duplicate does not contain it. Using it as a within-window floor in C-XH is a category error; the bench does hold nearer facts the design omits: null_band_v1.md (the measured cross-pin band from program-identical cells, per regime and scale) and the same-pin twin readings (noreqbyte ledger: "pure-twin controls read 1.0000 +- 0.0006", "twin's own same-window noise +-1.96 %").
- repro: read the cited lines.
- proposed fix: replace both with: the bench's A/A duplicate gap in the same window (C-XH's own), cite null_band_v1 for a cross-window reference, drop the 2-7 % and the 4-5 % from the pass rule (keep B8 as a question).

### MEAS-4 C-XH's planted failure is not shown to turn the rule red
- status: CONFIRMED (arithmetic on the rule as written)
- severity: design
- effort: small
- blast radius: the control can read green on its own plant, so a green C-XH carries no weight.
- where: §5.1 C-XH, §8 row "primary harness has a defect".
- finding: the rule needs (i) the same best arm on every site whose grid1 gap exceeds the floors and (ii) positive rank correlation on at least 90 % of sites (18 of 20). The plant "two config ids swapped in the join for one site" fails (i) only if the swapped pair includes the best arm, and (ii) only if the swap makes the rank correlation non-positive; one site of 20 is inside the 90 % allowance anyway. A swap of two middle arms leaves both tests green.
- repro: 6 arms ranked 1..6, swap ranks 3 and 4: Spearman rho = 1 - 6*2/(6*35) = 0.943 > 0; best arm unchanged.
- proposed fix: state the plant as "swap the grid1-best arm with the worst", and require the rule to read red on it AND green on a swap-free replay; or tighten (ii).

### MEAS-5 C-XH covers LONG only and arms the two harnesses build differently
- status: CONFIRMED (coverage); SUSPECTED (build effect)
- severity: design
- effort: medium
- blast radius: the SHORT shape (DINGHY, where per-call overhead and harness shims matter most, and where the bench has its known short-cell offset) has no independent check; a red from build differences gets read as a defect.
- where: §5.1 C-XH ("LONG shape"), §5.3, §8.
- finding: (a) SHORT has no cross-check at all; grid1's `first` pass is one `rx_search` from 0 over a buffer, the same loop the design calls the primary. (b) The bench times the artifact as a `shim.c` + `driver.c` `.so` loaded by `dlopen` (testees/pcrec/CLAUDE.md:67), grid1 statically links `gdrv.c`; call overhead differs by construction. (c) The bench pins ONE pcrec commit in configs.toml and carries a fixed list of ~52 testees; C-XH needs it at the H commit (chosen after R-30b and the VMREC answer) plus ~6 per-site arm configs (each needs a `config_extra` token) and per-call expectations (`expectations_stream.tsv` is compared by the harness). A bench re-pin, new configs and expectations are not costed in §11 (the bench's lane appears only as "C-XH configs, B7-B9").
- repro: read testees/pcrec/CLAUDE.md:1-66, unusual_set_v1.md:637-645 (X-rule on results_sha256).
- proposed fix: cost the re-pin and per-site configs; add a SHORT C-XH on the same 20 sites or say SHORT is unchecked; define the C-XH red as "explain, then rule", not "a defect".

### MEAS-6 NULL_c as written is neither regime_eval's definition "by name" nor well defined
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: every per-cell WIN/LOSS/NULL and the "UNDERPOWERED" and pair tests ride on NULL_c; if the pool is one value, NULL_c is one noisy A/A difference.
- where: §5.4 lines 717-722; regime_eval.md:540-546 and EP30 (:1795), §4.3 (:2103-2133).
- finding: regime_eval defines `NULL_c = max(AA_c, nu * ns_walk(c))` with nu the slot's MEDIAN of |walk - walk#c| / walk over groups, taken from a SECOND independent A/A arm (`walk#c`) so that the floor does not read its own pair (§4.3 "M-5"). Rev 1 says "by name" but uses `max(AA_c, nu * sigma_pool)`, sigma_pool = p95 of A/A gaps "over every cell of the same timing block", and then defines the block as ONE group: one site, stream, shape. grid1 emits one A/A pair per group (`base`, `base#b`), so the pool has one member and sigma_pool = AA_c; NULL_c collapses to a single |difference of two 5-launch medians|, which is near 0 about as often as it is large. There is no `#c`, so the independent drift anchor is gone, and `ν=1` over a p95 is not the median-based nu either.
- repro: arithmetic: 1 pair per group in time.sh (`arms_of`), pool of 1.
- proposed fix: pool over the stratum (all groups of a class/shape) or use regime_eval's nu from a `base#c` arm (+1 launch per group, about +6 %), and say which; do not cite "by name".

### MEAS-7 Cross-fit halves: median of two is undefined; D has halves of 1 and 2 although D feeds verdict-bearing constants
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: the half {2,4} is a median of two (grid1's `med()` returns the LOWER of two: `a[int((NR+1)/2)]` = a[1]); a 3-launch half and a min-of-2 half are biased differently, and the average of the two readings keeps a launch-count-dependent bias. D (3 launches) splits into {1,3}/{2}.
- where: §5.4 lines 709-716, §5.1 line 674 ("D runs at 3 launches (diagnostic only)"), §3.2 ("D ... the fitted constants are fitted"), §6.3 K-fit, §8 C7 (b) ("the bar comes from D's noise"), §9.3 T1 row 3.
- finding: (a) the design must say median-of-2 = mean and compute from `time/raw_<PHASE>.tsv`, not from time.sh's printed figure. (b) K-fit (fitted on D, enters T1 row 3) and C7(b)'s bar (derived from D's noise) are verdict-bearing, so D is not "diagnostic only"; with 3 launches the noise estimate that sets the bar rests on 3 values and a one-launch half. The raw file does carry per-launch values, so the fix is possible; but §5.1 says "per-round values are kept" and only per-LAUNCH values are (`gdrv.c` prints only t[3]; the file's `round` column is the launch index).
- repro: read time.sh `med()` and the raw header; `gdrv.c` last lines.
- proposed fix: define median-of-2; either run D at 5 launches (+1.3 h by the design's own table, 2.0 h -> 3.3 h) or state that K-fit and the C7 bar use 3-launch data and size the bar for it; correct "per-round".

### MEAS-8 The rep-vs-stream column has no null, so its differences are not attributable to the regime
- status: CONFIRMED (as designed)
- severity: design
- effort: small
- blast radius: the column "measures what a repeated-loop harness would have decided differently"; it is not in the verdict, so the damage is a misleading finding in the report.
- where: §5.2 last paragraph.
- finding: rep64k is ONE 64 KiB window; the stream is 64 DIFFERENT windows (4 MiB, past L2, different content and match density). A site's oracle can change because the rep window is unrepresentative, not because of repetition or cache or predictor training. The design gives no window-sampling null (e.g. rep on a second window, or the stream's own per-window spread), so "share of sites whose oracle changes" has an unknown floor. It also times 1 shape of 2 (table: shapes 1) without saying which.
- repro: read §5.2 and the §5.6 table row.
- proposed fix: add rep on two windows and report the rep-vs-rep disagreement as the null; name the shape.

### MEAS-9 §5.1 "grid1 does ..." claims that are new work (quiet gate, occupancy, ext streamed subjects with SHORT, ext arm builds) are not all costed
- status: CONFIRMED (for the gate); SUSPECTED (SHORT subjects)
- severity: design
- effort: medium
- blast radius: the timing windows run on a shared box under a gate that grid1 does not enforce.
- where: §5.1 "Quiet gate", §5.1 line 666-669, §11 stage 0; grid1 `time.sh:111-114`, README "Quiet gate".
- finding: (a) time.sh waits at most LOADWAIT=60 x 20 s, then PROCEEDS and times the group (it prints a note; it does not skip, flag the rows, or fail). Load1 < 1.5 is also the only test; there is no per-core occupancy check anywhere in grid1 (`grep mpstat|occupancy` in the lane scripts: none). The design's "plus a per-core occupancy check of CPU 14 and its neighbours at every group boundary" is therefore new work in time.sh, not costed; and "wait then proceed" needs to become "wait then mark the group NOT-QUIET and re-queue" for the verdict to be trusted. (b) the ext arm set's build.sh, generator for per-site arms.tsv (about 400 cells), per-site `gen_subj` for both shapes (SHORT needs line-bucket subjects as hundreds-to-thousands of tiny files under grid1's directory loader) are one line, "grid1 ext arm set and its generator", in stage 0.
- repro: read `time.sh` lines 111-114: loop ends without break, falls through.
- proposed fix: add the gate change and the SHORT subject generator as named stage 0 items; make an unquiet group a re-queue.

### MEAS-10 §5.6: "one launch is about 0.5 s" is below grid1's own measured constants
- status: CONFIRMED (arithmetic and the script's own numbers)
- severity: speed
- effort: small
- blast radius: stage-2 box time understated by about 30 % (and by 40-90 % if the stream load counts); the quiet-window requests to Frank are sized on it.
- where: §5.6 line 740 and table; grid1 `time.sh:34-35` (`SEC_REP=0.65`, "measured ... 0.45-0.85 s"; `SEC_STREAM=0.95`, "measured ... 0.92-0.97 s"), `gdrv.c` main().
- finding: gdrv calibrates by doubling until a loop is >= 50 ms (the final loop is 50-100 ms, the doubling runs sum to about the final one), then 7 rounds of that loop: 0.35-0.7 s of rounds plus 0.05-0.2 s of calibration plus the answer pass and load. 0.65 s is the middle; 0.5 s is the optimistic end. At 0.65 s: H-core 5.2 h, D 2.6 h, total about 9.3 h against 7.2 h. The design already says `time.sh --estimate` replaces it, so this is a small correction, but the 4 MiB streams are less than the 64 MiB the 0.95 figure covers, so 0.65 is the fair constant.
- repro: 180x2x16x5x0.65 = 18,720 s = 5.2 h; 100x2x2x12x3x0.65 = 9,360 s = 2.6 h.
- proposed fix: use 0.65 s (or run `--estimate` on the first ext set before the plan is quoted).

### MEAS-11 §5.1 quotations that differ from the bench's docs (smaller)
- status: CONFIRMED (the docs); the bench's rulings file is denylisted so the 0.5-1.5 min and 15 s figures are UNVERIFIED
- severity: doc
- effort: small
- where: §5.1 lines 613-617.
- finding: "configs run as sequential blocks 15 s apart": the bench docs measure 24-44 s between cells and a 25-40 s sleep (b138hours_report.md:14, :31); "0.5-1.5 min per cell" is not in any bench doc I may read (the nearest, b138hours, gives whole capability cells of about 28 min); "T4: no environment key at any tier" is consistent with the docs read (CLI flags, `cflags`, `config_extra`), so that quote held. "No measured A/A floor" omits null_band_v1 and the twin ledgers (MEAS-3).
- proposed fix: cite file:line for each bench fact in §5.1 instead of "its docs".

## PROBED-AND-HELD
- Cost table arithmetic (§5.6): H-core 180x2x16x5x0.5 = 4.0 h; D 100x2x2x12x3x0.5 = 2.0 h; rep column 0.22 h; total with top-up 7.2 h; stage-2 "about 6 h" = 4.0+2.0+0.2. 4 of 4 rows reproduce.
- Arm counts against census_dry_summary.txt: route-seed arms 754/259 = 2.91 (design 2.9) held; default-route arms (1565-754)/259 = 3.13 (design 3.2, fine); no-search arm sites 155/259 = 60 % (design "about 65 %" is the J1 ratio 112/172 = 65 %; effect on the total 0.05 arms) ; footprint 0.96x4 = 3.84 and C-BLIND the same. 5 of 5 held within rounding.
- grid1 mechanics the design relies on, read in time.sh/gdrv.c/gload.h/README: streamed directory subject with a never-resetting cursor and check leg C (`gdrv.c` next_pass, `cycle`/`cycleexp`); base and `base#b` per round with rotation (`time.sh` arms_of, `V=A[(p+i-1)%k]`); 5 launches default; 50 ms doubling then 7 rounds, median; CPU 14 and `taskset`; raw per-launch file with load1; ext arm sets with their own build.sh (`ext_example/build.sh` builds per-arm compiler invocations); ORACLE_CMD hook present (`check.sh:54`). 9 of 9 present; the issues are in MEAS-1, 7, 9.
- Cross-fit split {1,3,5}/{2,4} works with grid1's raw file (one value per launch per arm per round index); rotation keeps base and base#b adjacent in every round, so the A/A pair is always back-to-back (SUSPECTED: a small optimistic bias in the floor, because the second run of the same binary follows its twin; would be confirmed by comparing base#b - base against a non-adjacent base#c on one group).
- Bench T4 (levers CLI-only, `config_extra` for twins) and T2 (no pairing, one testee per run) agree with testees/pcrec/CLAUDE.md and harness_contract.md (2 of 2).
