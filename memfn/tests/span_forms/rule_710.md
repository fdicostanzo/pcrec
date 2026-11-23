# blockconfirm decision rule (sha256 6351bff3901e3955), frozen 2026-11-20T19:02:56 before any timing
# AMENDED before any timing (manager rulings 2026-11-20, five-arm plan): verdict on the inlined arms only; avx2-ool vs
# H64@on information; the control voids TBL readings cell by cell.  Previous sha 4e1a1cd2f062fc6a, then 60ca03823c8eeb26.
# AMENDED AGAIN 2026-11-20 (lane bcq), before any timing: the CPU-quiet control (cpuquiet/spec.md), INCONCLUSIVE-NOISE,
# the re-time-short rule, the STOP_AT window / NOT-RUN.  Rule sha 60ca03823c8eeb26 -> d32a1474107714e2.
# AMENDED AGAIN 2026-11-20 (lane bcfix, the critic round memfn-blockconfirm, manager's RULING 17:30), before any
# timing: symmetric re-time (S-pick WINs count only if repeated) + the A/A line (MEASUREMENT-1); the control voids
# by direction + the void share and its 25 % banner (MEASUREMENT-2); re-time variants 10,11,12 at the main pass's
# alignment parity (MEASUREMENT-4); the verdict on the NEW population, OLD the replication line (MEASUREMENT-5);
# CLAIM = what the verdict decides (MEASUREMENT-7, -6); CPU7_MAX capped at 20 % + >= 100 ms observation (spec
# amendment 2', GATES-3/4); LOSS first (GATES-7); the cause word (GATES-6); the cap deadline (GATES-9); TRUNCATED
# prefix (GATES-8); the run's own record (FIDELITY-2).  Rule sha d32a1474107714e2 -> 3af29030022e8555.
# AMENDED AGAIN 2026-11-20 (lane bcfix round 2, the kit manager's ruling on the open MEASUREMENT-2 reading), before
# any timing: a TBL TIE beside a control WIN is VOID; beside a control LOSS it STANDS; both listed with counts.
# Rule sha 3af29030022e8555 -> b7dbbafff6d43441.
# AMENDED AGAIN 2026-11-20 (lane bcfix round 3, the re-check crit-memfn-bcfix NEW-1/NEW-2, the kit manager's ruling),
# before any timing: round 2 REVERSED, a TBL TIE beside a control WIN stands as a TIE (listed "may hide a LOSS");
# the verdict needs at least half of the verdict population readable, else INCONCLUSIVE named for its cause.
# Rule sha b7dbbafff6d43441 -> see line 1.

```
THE RULE (blockconfirm, written 2026-11-20 before any timing; confirm.py implements exactly this):
CLAIM (amended bcfix 2026-11-20, MEASUREMENT-7/-6/-5): with SIMD on, the declared table TBL (below) has no REPEATED LOSS vs
today's form H64@on among the readable cells (non-N/A, non-void, non-noise, run), and WINS (repeated) a strict majority of
the busy cells it routes to the block form, read on the cells 708 did NOT time (NEW, below).  "Busy" is S, 708's
CALL-DENSITY set (below), not span bytes or span time; the byte-heavy pick cells outside S are reported on their own line.
The scalar layer is not tested (it stays H64).
TABLE (first match; rows read compile-time facts only: the site kind pcrec emitted -- WINDOW = the walk tests the
window's last byte first and shifts by a table; SCAN = the walk skips to a member byte and verifies the rest -- and k,
the span's positions; never a class name):
  1. site = window and 16 <= k <= 1000  -> avx2-loop
  2. site = scan   and 24 <= k <= 64    -> avx2-loop
  3. else                               -> H64@on
ARMS (one base text: the cards' h64 artifact at -fmemfn-simd=x86-64-v3; the span expression -> rxs_span(s, c) inside
the artifact's own x86-64-v3 region; only rxs_span's body and inlining attribute differ):
  H64@on    the reference (today's form at the SIMD-on layer, the artifact unchanged)
  Hspk      H64's own span text as rxs_span's body, always_inline: THE HARNESS CONTROL
  avx2-loop 708's avx2-loop form (cascade below 32 B: SSE 16 at k=16..31, SWAR 8 at k=8..15), always_inline
  TBL       = avx2-loop's exe where the table picks avx2-loop, else H64@on's exe (the same text: TIE by construction)
  Hspk-ool, avx2-ool  the same bodies, noipa (out of line): the walk's machine code identical by construction;
            INFORMATION only (avx2-ool vs Hspk-ool = the span's cost alone; Hspk-ool vs H64@on = the call's cost;
            avx2-ool vs H64@on = an out-of-line block span as a form of its own, NOT under test)
  The VERDICT is read on the INLINED arms only (the shippable text); a walk-code difference of inline avx2-loop from
  H64@on is part of that form's real cost (manager's ruling 2026-11-20).
CELL = (class, k, regime).  Variants 6, 7, 8 (fresh; 708 used 0-5), one repeat each, median.  NEW = a class in (af, ident,
  upper, num) or a k in (12, 20, 40, 96, 256); OLD = the rest (708's classes x 708's k: the table was fitted on 708's grid,
  and those cells re-time 708's exact subject bytes and code text on fresh layouts).
FLOOR = max(0.15, spread(A), spread(B)), spread = (max - min) / median of an arm's three per-variant ns/B.
  WIN if A < B / (1 + FLOOR); LOSS if A > B * (1 + FLOOR); else TIE.
N/A: a cell whose span is never called (the depth profile: H64's span instrumented on the same walk, 0 calls) is N/A:
  listed, excluded from every count, from the LOSS check and from the control.
CPU-QUIET CONTROL (amended 2026-11-20, before any timing; manager spec cpuquiet/spec.md): the timed process is pinned to
  CPU 15 but nothing isolates CPU 15 or its SMT sibling (CPU 7, read from sysfs at the run; the run refuses if the pin has
  none).  QUIET SAMPLE, in the job after the quiet wait and before the first timed cell, from nothing of the run's own
  data: 60 s of 1-s /proc/stat samples of CPU 7 and CPU 15 with nothing of ours running, then 10 repeats of one
  calibration exe (H64@on of the first cell, pass A) recording the involuntary context switches (nivcsw) of the timed
  process tree (getrusage RUSAGE_CHILDREN delta).  Written to quiet_sample.tsv.  THRESHOLDS from the sample only, printed
  in decision.md: CPU7_MAX = min(20 %, max(5 %, 2 x the sample's max 1-s busy fraction of CPU 7)) (spec amendment 2'; above
  20 % the sample was not quiet: decision.md opens "QUIET SAMPLE BUSY: CPU7_MAX capped at 20 % (sample max X %)" and the run
  proceeds, the cap voiding more repeats); NIVCSW_MAX = max(2, 2 x the max
  per-repeat nivcsw of the calibration), per T_CAL = the calibration's mean repeat length; a repeat of T seconds is void
  above NIVCSW_MAX x max(1, T / T_CAL).  PER TIMED REPEAT (pass A, the pass whose ns/B is read): CPU 7's busy fraction over
  the repeat (observed over at least 100 ms: /proc/stat moves in 10 ms ticks) and the nivcsw; the repeat is VOID if CPU 7 busy > CPU7_MAX or nivcsw above its scaled limit.  A void repeat
  is re-timed up to 2 more times (same variant); an arm of a cell still short of its 3 valid repeats leaves that
  comparison INCONCLUSIVE-NOISE: listed, excluded (like N/A) from every count, from the LOSS check and from the S
  denominator, its count printed beside the verdict.  A TBL reading is also INCONCLUSIVE-NOISE where its control
  comparison (Hspk vs H64@on) is INCONCLUSIVE-NOISE (the control cannot be read).  Every void repeat is logged
  (voids.tsv) with its readings.  A re-time (variants 10-12) that is itself short of valid repeats ("re-time noisy") or not
  run ("re-time NOT-RUN") cannot clear a LOSS or a control WIN/LOSS: that reading STANDS, listed so; and it cannot repeat a
  TBL WIN: that WIN does not count (see RE-TIME).  More than 10 % of the
  non-N/A cells INCONCLUSIVE-NOISE is said at the top of decision.md.  This is distinct from INCONCLUSIVE-HARNESS (the
  walk control's cell-by-cell void, below): the two counts are printed separately.
WINDOW: no new cell starts at or after the job's deadline = min(STOP_AT, the job's start + its boxqueue cap - 600 s)
  (bcfix GATES-9: a cap kill would leave no verdict); cells not started are NOT-RUN, listed, with a distinct TRUNCATED line
  (and rc 4); the verdict then reads what ran, is prefixed "TRUNCATED: " and covers only what ran (GATES-8).
RECORD (bcfix FIDELITY-2): the depth profile and the walk identity (N/A, S and the A/A population come from them) are under
  the correctness marker; measure copies them, the marker and the exe manifest into the run directory and records the rule
  sha and the marker hash in its meta.json; the verdict reads the run's copies, and decide refuses a run whose rule sha or
  marker hash differs from the live ones.
S (span-dense, 708's definition): span calls >= 1500 per MiB AND (mean failing index >= 4 OR full-span share >= 2 %).
RE-TIME (amended bcfix, MEASUREMENT-1/-4; symmetric for the claim): every LOSS of TBL vs H64@on (any cell), every WIN of
  TBL vs H64@on in an S cell where the table picks avx2-loop, and every non-TIE (WIN or LOSS) of Hspk vs H64@on, is re-timed
  in the same job on further fresh variants 10, 11, 12 (the main pass's alignment parity: even = gcc default, odd =
  alignment off, 2 : 1 in both passes; both arms, median of 3, same floor).  It stands only if the re-time gives the same
  verdict; otherwise it is "not repeated" and counts as a TIE (both readings listed).  A re-time noisy or NOT-RUN: a LOSS
  and a control WIN/LOSS stand; a TBL WIN does NOT count (a WIN counts only if repeated): "WIN not repeated", a TIE.
A/A LINE (MEASUREMENT-1/-3): on the identical-walk patterns (check's walk identity: Hspk's whole rxa_search == H64@on's,
  walkid.json) the control is an A/A layout test; its single-pass and repeated non-TIE counts over its readable cells are
  printed beside the verdict, with the expected false WINs = the verdict population's counted cells x the repeated A/A WIN
  rate (and x the single-pass rate).
CONTROL, CELL BY CELL, BY DIRECTION (manager's ruling 2026-11-20, amended in form 2026-11-20 17:30, MEASUREMENT-2): in a
  non-N/A cell where Hspk has a standing WIN or LOSS vs H64@on, a TBL reading in the SAME direction (control WIN + TBL WIN,
  control LOSS + TBL LOSS) is INCONCLUSIVE-HARNESS: VOID, listed, and excluded (like N/A) from every TBL count, from the
  LOSS check and from the S denominator.  A TBL reading in the OPPOSITE direction STANDS (a fortiori).  A TBL TIE (incl.
  "not repeated") beside a control WIN STANDS as a TIE, a non-WIN in the CONFIRMED denominator (voiding it would only move
  the WIN share up: re-check NEW-1, manager's ruling 2026-11-20 round 3, reversing round 2), listed "may hide a LOSS"; a
  TBL TIE beside a control LOSS STANDS (it can only hide a WIN); both kinds are listed with their counts.  The void share
  (void cells / non-N/A TBL cells, overall and in the verdict population) is printed; above 25 % in either, decision.md
  opens with a VOID SHARE banner.  The void count is split by the control's two populations: on the identical-walk patterns
  the control is an A/A layout test; on the others it measures how gcc perturbs H64's OWN inlined chain, not avx2-loop's
  (MEASUREMENT-3).  PREMISE, not checked by this run: rxs_span always_inline + immintrin.h is the text the kit would ship.
VERDICT (first match, over the readable cells = non-N/A, non-void, non-noise; the INCONCLUSIVE-NOISE count printed beside
  it; the VERDICT POPULATION = the NEW S cells where the table picks avx2-loop):
  LOSS                  TBL has a standing (repeated, or re-time noisy / NOT-RUN) LOSS vs H64@on in any readable cell
                        (listed); it needs no S cell, so it comes first (GATES-7)
  INCONCLUSIVE-HARNESS / INCONCLUSIVE-NOISE / NOT-RUN   fewer than HALF of the verdict population's cells (the whole
                        grid's non-N/A NEW S-pick cells, cells not run included) are readable (round 3, NEW-2); the word
                        names the cause (GATES-6): the most numerous of control-void, INCONCLUSIVE-NOISE, not run (a tie
                        in that order)
  CONFIRMED             TBL WINS (repeated) a strict majority of the readable cells of the verdict population
  NO LOSS but no WIN majority
REPORTED beside it: the REPLICATION LINE (OLD S-pick WINs, never in the verdict); the A/A line; W/T/L (TBL vs H64@on) over
  all non-N/A cells, over S, over S-pick, the verdict population, the byte-heavy pick cells outside S (span bytes >= 10 %
  of the subject); per table row; per NEW class (af, ident, upper, num) and per NEW k (12, 20, 40, 96, 256) separately,
  and old vs new; avx2-loop everywhere vs H64@on (information); the ool comparisons (information); what each comparison
  changes (MEASUREMENT-9).
```
