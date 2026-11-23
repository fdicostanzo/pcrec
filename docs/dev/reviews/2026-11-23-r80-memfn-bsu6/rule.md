# CRITIC rule: memfn-bsu6 (r80)

## Findings

### RULE-1 CONFIRMED (verdict): a short arm NOISEs only the comparisons it is in; the rule says BOTH of the cell's comparisons
- Clause: c6_rule.md CPU-QUIET CONTROL: "an arm still short of LAUNCHES valid launches makes both of its cell's comparisons
  INCONCLUSIVE-NOISE" (same for a re-time, which uses "the same unit and floor").
- Code: cards.py:1266-1282 `c6_cell` computes `c6_cmp(V,H64)` and `c6_cmp(H64.b,H64)` pairwise; `c6_arm` -> None only NOISEs
  the pair holding that arm. Same in `c6_owes` (1603) and in the re-time leg of `c6_cell`. A `gatefail` arm row reads the same way.
- Repro (records built by my rule/scratch/gen.py + drills.py; `kit/cards.sh rule c6decide rule/scratch/drills/<name>.tsv`,
  diffed against my rule-only decider rule/scratch/mydec.py):
  - `hb_void_loss` (H64.b every launch void, V = 1.3 x H64 both passes, 20 TIE fillers): code `C6 on: LOSS` (the level blocked);
    rule: the cell is INCONCLUSIVE-NOISE -> `NO LOSS`, readable 20 of 21. `hb_short4_loss` (H64.b 4 valid launches): same.
  - `rt_v_void_aa` (first pass A/A H64.b = 1.3 x H64; re-time V void): code reads the re-time A/A as TIE -> "A/A LOSS not
    repeated", cell readable; rule: both re-time comparisons NOISE -> the A/A non-TIE STANDS -> INCONCLUSIVE-HARNESS (rate 1/20).
  - `v_void`, `gatefail`: code counts the cell A/A-readable (21) where the rule has 20. On the coordinator's own DRY record
    (kit/ref, 8 cells with V void): code "A/A ... of 32 readable" for C6 on and "of 12" for each C6c layer; the rule gives 28
    and 10. The inflated denominator lowers the A/A rate, so it can hide a VOID (e.g. 2 standing of 38 readable = 0.053 VOID
    reads 2 of 42 = 0.048 NO LOSS if 4 cells have a short V).
- Fix: in `c6_cell` (and `c6_owes`), if any of the three arms of a pass reads None, both of that pass's comparisons are NOISE.
  Effort: ~4 lines + a c6selftest row per direction (H64.b short with a V LOSS; V short with an A/A non-TIE). Blast radius:
  every C6/C6c verdict with a void-short arm; C6's gate (D155 item 2) can read LOSS where the rule reads NO LOSS.

### RULE-2 CONFIRMED (doc/report): a reading LOSS that stands on a NOISY re-time is not "listed so"
- Clause: RE-TIME: "A re-time INCONCLUSIVE-NOISE or NOT-RUN: a reading LOSS stands (listed so)".
- Code: `_standing` (cards.py:1254) returns the note "re-time noisy" for that case, but `c6_report` (1675-1707) prints only
  notes containing "not repeated" plus the re-time NOT-RUN list; the noisy-re-time note is computed and dropped.
- Repro: drill `rt_noise_LOSS` (V = 1.3 x H64 first pass; re-time H64 spread 0.5): the report's only trace is
  `C6 on: LOSS (standing): c6_hex32/near-miss-in`, indistinguishable from a repeated LOSS. The NOT-RUN twin (`rt_notrun_LOSS`)
  IS listed (the re-time NOT-RUN line). The same holds for an A/A non-TIE standing on a noisy re-time (counted, never listed).
- Fix: print the `re-time noisy` / `re-time NOT-RUN` notes on the standing-LOSS line (e.g. "c6_hex32/near-miss-in (single
  pass; re-time noisy)"). Effort: 2 lines. Blast radius: the report only; the verdict is right. A LOSS that blocks a level on
  one pass is exactly the one a reader must see flagged.

### RULE-3 CONFIRMED (verdict/window): the deadline is an optional operator input anchored AFTER the builds, not the rule's
- Clause: WINDOW: "no cell starts at or after the job's deadline (710's: min(STOP_AT, the job's start + its cap - 600 s))";
  710's GATES-9 reason: a cap kill leaves no verdict (here: no `#end`, so c6decide REFUSES the whole record).
- Code: cards.py:1806-1808: `probe_t0 = time.time()` is taken after step 1 (C6 text check), step 2 (the reach builds and
  passes) and step 3 (84 pools x 4 exes built and proved, 336 compiles: part of the coordinator's 49 s DRY at JOBS=2, not measured apart; a real
  run builds the same set); `--deadline +S` is `probe_t0 + S`. `t_start` (1764), the job's start, exists and is unused
  for this. With no `--deadline` there is no window at all (`stop = None`). Nothing computes min(STOP_AT, start + cap - 600).
  The quiet sample (QC_SECS 60 s + calibration) also starts regardless of the deadline.
- Failure scenario: the job script passes `--deadline +$((CAP-600))` (the natural reading of "start + cap - 600"); the
  deadline lands (pre-timing build time) later than the rule's, eating the 600 s margin that protects the last cell from the
  cap kill; a kill leaves a record without `#end` -> REFUSED, the window lost. 710's harness took an absolute epoch only.
- Fix: anchor `+S` at `t_start` (or take `--cap SECONDS [--stop-at EPOCH]` and compute the rule's min itself), and refuse a
  non-DRY `time` without a deadline. Effort: ~6 lines. Blast radius: the timing window only; SUSPECTED as to whether the
  boxqueue job script (not in this diff) already passes an absolute epoch, which would make this a latent trap, not a live one.

### RULE-4 CONFIRMED (doc, low): a re-time cut by the window exits 4 (TRUNCATED) but the verdict line carries no "TRUNCATED: "
- Clause: WINDOW: "a cell not started is NOT-RUN, listed; the verdict is prefixed 'TRUNCATED: '"; VERDICT: "Any NOT-RUN cell
  prefixes the verdict". RE-TIME separately rules a re-time NOT-RUN's reading (LOSS stands, WIN -> TIE, A/A stands).
- Code: `c6_decide` (1318) prefixes only on first-pass NOT-RUN (`cause["NOT-RUN"]`); `cmd_c6decide` (1720) returns 4 on
  `info["retime_notrun"]` too, and its docstring says 4 = "a cell of either pass not started"; `_time` prints a separate
  "cards: time: TRUNCATED".
- Repro: drills `rt_notrun_LOSS` / `rt_notrun_WIN`: rc 4, verdict line `C6 on: LOSS` / `C6 on: NO LOSS` (no prefix); the
  re-time NOT-RUN list is printed. My rule-only reading gives the same unprefixed verdict (a re-time is not a cell), so the
  defect is the two signals disagreeing, not the verdict.
- Fix: pick one: prefix the verdict when a re-time was cut (the run WAS truncated, and a WIN silently became a TIE), or
  document rc 4 as "a first-pass cell or a re-time not started" and keep the line as is. Effort: 1 line. Blast radius: report.

### RULE-5 CONFIRMED (design, rule text; no code change): INCONCLUSIVE-HARNESS can never be the verdict's cause
- Clause: VERDICT row 4, cause "the most numerous of HARNESS, NOISE, NOT-RUN (a tie in that order)", after VOID (rate >
  AA_VOID_MAX 0.05).
- Argument: HARNESS cells H are standing A/A non-TIEs, so the rate is H / aa_readable, and aa_readable <= H + readable + N
  (NOT-RUN cells are never A/A-readable). Not VOID needs aa_readable >= 20 H. Cause HARNESS needs H >= N and H >= NR, and row 4
  needs H + N + NR > readable, so readable < 3 H, so aa_readable <= H + readable + N < 5 H (N's A/A-readable cells at most
  N <= H) -- contradiction for H >= 1. So "INCONCLUSIVE-HARNESS" as a verdict and the HARNESS-first tie order are dead text
  under AA_VOID_MAX 0.05 (they become live only above ~0.2). The code implements them faithfully (drilled: cause ties
  NOISE/NOT-RUN both orders -> NOISE); a selftest row cannot plant them without moving AA_VOID_MAX.
- Disposition suggestion: none needed for the code; note it in c6_rule.md's next revision (a reader may expect the cause to
  be reachable). Severity doc; effort nil.

## PROBED-AND-HELD

Method: my rule-only decider (rule/scratch/mydec.py, written from the fenced block before reading `c6_decide`), a record
generator (gen.py, the subject's own head/`#run`/`cell`/`first`/`retime`/`#end` format) and 35 constructed records
(drills.py -> rule/scratch/drills/), each run through `kit/cards.sh rule c6decide` and diffed (rule/scratch/drill_out.txt),
plus the coordinator's DRY record (kit/ref). No full DRY run, 0 compiles.
- 29 of 35 records: identical verdict, readable/population, W/T/L, A/A counts and cause counts. The 5 divergent are RULE-1
  (hb_void_loss, hb_short4_loss, rt_v_void_aa, v_void, gatefail); 1 (spread_0.30) was REFUSED because my generator's
  spread rounded to 0.30000000000000004 > SPREAD_MAX and the reader then found re-time rows the cell no longer owes: the
  reader and timer share `c6_cmp`/`c6_owes`, so their agreement held (a float exactly at a constant is no real outcome).
- HELD: UNIT (median; spread x[n-1]-x[2] = sorted[-2]-sorted[1]; outlier launch at each end of every arm leaves a 1.20 LOSS
  standing); FLOOR max(0.15, spreads), strict > SPREAD_MAX for NOISE, strict WIN/LOSS inequalities (1.1499, 1.15 -> TIE,
  1.1501 -> LOSS); bimodal arm -> NOISE never TIE; RE-TIME: LOSS/WIN repeated stands, flip -> TIE "not repeated", re-time
  TIE -> TIE, NOISE/NOT-RUN -> LOSS stands, WIN -> TIE, A/A non-TIE stands on NOISE, flips -> TIE (8 drills); A/A standing at
  rate exactly 0.050 -> not VOID, 0.100 -> VOID; VOID before LOSS (void_before_loss: VOID with a standing LOSS present);
  READABLE_MIN at exactly half (10 of 20 via NOISE and via NOT-RUN) -> NO LOSS, 9 of 20 -> INCONCLUSIVE-<cause>; cause tie
  NOISE vs NOT-RUN -> NOISE in both cell orders; partly NOT-RUN first pass -> NOT-RUN cell + TRUNCATED prefix + rc 4; all
  NOT-RUN -> "TRUNCATED: VOID (A/A UNREAD)"; all N/A -> INCONCLUSIVE-N/A; gate failure -> rc 1 over rc 4, the arm NOISE.
- HELD, RECORD/reader: refuses a missing/stale header, no `#end`, LAUNCHES mismatch, a re-time set the first pass does not
  owe (or owes and lacks), rows outside the population.
- Sub-part (population and WINDOW): the C6 population matches block_span.md §8 (3 real sites w32; window k16 w32, k31 via
  the real sites, k32 and k1000 w4095; scan k24 w32, k64 w4095; C6_F2_DIFFERS empty per its comment; near-miss-in only at
  window sites with k+1 <= 255, i.e. not at c6_hex1001; not-warm/short-subject void by method, out of the verdict
  population; N/A from `c6_reach`'s instrumented V text, one untimed pass; kit/ref's 4 C6 + 2+2 C6c N/A cells are exactly the
  window near-miss cells k <= 32). WINDOW's per-cell check (`stop()` before each cell, `>=`) holds in both passes (the
  re-time pass gets the same `stop`); the deadline's anchor does not (RULE-3).

CRITIC COMPLETE
