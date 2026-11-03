# bar588 — job 588's BAR: the per-call layout allowance made to mean what the design says (2026-11-02)

Lane bar588 (branch lane/memfn-bar588, from lane/memfn-k1102). Changed: `docs/dev/lanes/s3_evidence/read_588.py` and `docs/design/memfn/window_site.md` (Goal 2 and the §6 allowance bullet, marked `[2026-11-02 bar588]`). No new measurement: the reader was re-run over job 588's existing data (copied from `/var/tmp/pcrec-pcrec/scratch/memfn/t588/o`). Scratch outputs, all under `/var/tmp/pcrec-pcrec/scratch/memfn/bar588/`: `old_reread.md` (old reader, byte-identical to the job's `s3t_table.md`, the control), `new_bar.md` (the fixed reader), `new_rel0585_informational.md` (relative 0.0585, NOT the bar), `flips_new_vs_old.txt`, `flips_rel0585_vs_old.txt`, `flips.py`.

## What was wrong

Two defects in the reader, both from t588tri section (b).
1. The allowance came from `year4/none`, a throughput cell with `calls == 1` (hits 0, plus 1). Its "per call" figure is a whole-pass delta (24,498.593 ns), which was then applied to cells with thousands of calls, so throughput cells were effectively uncapped.
2. The allowance was computed per regime (throughput 24498.593, search_short 14.766, match 0.877). The design says one number: Goal 2 and §6 say "the largest |delta| in ns per call over every variant and cell of the run".

The design text, read closely, matches the brief: one number over the run, from per-call figures. A one-call cell is not covered by the design's text either way; I followed the brief for it (judged on the floor alone).

## The fix

`read_588.py`: ONE `ALLOW`, the largest |med(DVk) - med(DEF)| / calls over every variant, regime, cell and class, taken only from cells with `calls > 1`; printed with its variant, regime and cell. A new `within()` serves all four readers (§6 cells, mover sample, two-stream sample, SIMD reading); a `calls <= 1` cell is never excused by the allowance. The BAR line prints the one number. An optional 4th argument REL replaces the per-call allowance by a relative one for an informational reading; its heading and BAR line are renamed `INFORMATIONAL-NOT-THE-BAR(rel ...)`.
`window_site.md`: Goal 2 and the §6 bullet each carry a dated correction `[2026-11-02 bar588]` saying exactly this.

## Re-read

Control: the unmodified reader over the copied data reproduces the job's `s3t_table.md` byte for byte.

New BAR line (`new_bar.md`):
`== s3t BAR FAIL: 72 cells read on the scalar layer (allowance ns/call: 14.766); sample FAIL: stratum WALK/one/run 1.200 > 1.028; two-stream PASS`

The one allowance is 14.766 ns/call (DV3, search_short on word-digit/real: the 22 % layout swing). It is the run-wide maximum, so it is larger than the 3.994 that t588tri got for throughput alone (excluding calls == 1 there); under the design's one-number rule the search_short swing sets it. The bar stays FAIL, for the same single cause as before (stratum WALK/one/run); no §6 cell fails.

Flipped versus the old table.log, scalar layer (11 cells, all PASS (allowance) -> FAIL, all calls == 1 cells now judged on the floor alone; none in the §6 table):
- mover sample (6): smp02 throughput/none, smp04 throughput/random, smp05 throughput/random, smp12 throughput/random, smp17 throughput/none, smp20 throughput/none.
- two-stream sample (5): pr02, pr03, pr04, pr05, pr07, each throughput/mixed.
Strata (scalar): none flipped. WALK/one/run was FAIL and stays FAIL (1.200); COVER-PAIR stays PASS (gmean 1.068 > 1.028, but every cell of it still passes its floor or the allowance, which is the stratum rule's second arm); LIBC, WALK/hors, WALK/one/norun, REQRUN, COVER-BFN stay PASS. Note t588tri's "COVER-PAIR flips to FAIL" was a floor-only reading, not this one. Individual rows pr02-pr05, pr07 (REQRUN, COVER-BFN) and six mover rows now print FAIL, but the bar's term for both samples is the stratum.
SIMD layer (reported, not the bar; 7 cells, within -> SLOWER, because the same allowance rule now applies to it): smp02 throughput/none, smp04 throughput/random, smp10 throughput/none, smp10 throughput/random, smp12 throughput/random, smp17 throughput/none, smp20 throughput/real. No SIMD stratum or §6 cell changed.

Informational, NOT THE BAR: a relative allowance of 0.0585 read in place of the per-call one (`new_rel0585_informational.md`, `flips_rel0585_vs_old.txt`) flips 35 scalar cells versus the old table (4 in §6: year4 match/real, match/none, match/dense, file-ext-order match/none; 10 mover sample; 20 two-stream) and 15 SIMD cells, and one stratum, COVER-PAIR PASS -> FAIL (1.068 > 1.028); WALK/one/run stays FAIL. Its line reads `== s3t INFORMATIONAL-NOT-THE-BAR(rel 0.0585) FAIL`, FAILING: year4 match/real 1.173, match/none 1.115, match/dense 1.079, file-ext-order match/none 1.066; sample WALK/one/run; two-stream COVER-PAIR.

## Findings not fixed

- The driver's DV flags (32/64/64+loops32) differ from the design's 16/32/64; fixing that needs a new timing run (t588tri section (b)).
- smp20 `(?i)x/1234` (stop-pricing gap) and smp04 `[a[:b]` (compare-chain walk form) causes: held for the kit-units work (t588tri section (a)); they are what keeps WALK/one/run FAIL.
- The allowance is set by one search_short cell (word-digit/real, a 22 % layout swing) and then applies to every regime, including throughput cells of ~100 ns per call deltas below it; that is the design's literal one-number rule, but it is a large allowance (the manager may want to look at whether DV3's swing on that cell is itself an outlier). Not changed here.
- Anything pcrec-side.

## STATE AT HANDOFF

STATE: done. Committed on lane/memfn-bar588; read_588.py and window_site.md changed, this report committed, scratch re-read files cited above (not committed). OWED none.
