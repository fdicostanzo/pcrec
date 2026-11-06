# MEAS findings

Lens: measurement (values and noise mean what the design says; regime, independent control, what moves
on regeneration). Subject: span_cards_rev0.md (cited `SC:<line>`). Drills (synthetic only, no box timing):
`meas/est.py` (§3.4 estimator from the text), `meas/slope.py` (slopes, A/A scaling), `meas/stats.py`
(quoted numbers, coverage, minutes), `meas/drift.py` (in-group walk check), `meas/sweep.py` (J1 rule),
`meas/aa/` (separate-compile A/A). Run: `python3 -I meas/<x>.py`.

## Findings

### MEAS-1 CONFIRMED — the A/A arm is byte-identical to its base, so the floor holds no code-placement term
- Severity: design (noise understated; a control that shares everything with what it controls). Effort: small. Blast: every group's `aa`, every row's noise, the drift check, the J1 rule, sabotage row (9).
- Text: SC:168-169 "`walk#b`, `null#b` is a SEPARATE compile and link of the same text ..., so code placement
  differences are in the floor, not hidden."
- Repro: `meas/aa/{A,B}/a.c` identical source, `gcc -O2 -c` + link in two directories -> `cmp A/bin B/bin`:
  "binaries byte-identical", `.text` identical, `count` at 0x1160 in both. The template the design copies
  ASSERTS this: `docs/design/kit_proof/measure/measure.sh:71-72` refuses the run unless DEF's and AA's
  sources are `cmp`-identical, and gcc is deterministic, so the two binaries are the same bytes.
- Consequence: `aa` is a second sample of run-to-run noise in the same launch, never placement. The isolation
  gap the design concedes (§2.6: a form in the fixture loop vs inside a DFA) is exactly a placement/alignment
  effect, and nothing measures even its fixture-side size. Sabotage row (9) ("A/A linked from the base's
  object: the driver's distinct-build check red", SC:493) can only be detected by path/inode, not content.
- Fix direction: make the A/A arm a PERTURBED identical text (e.g. a pad function / `-falign-functions=` shift
  / link-order swap, stated), or relabel `aa` honestly as "same-binary rerun noise" and drop the placement claim.

### MEAS-2 CONFIRMED — the group gate `noise_e6 / value_e6 <= gate_e6` is ill-defined (scale, zero, sign)
- Severity: answer (of the gate). Effort: trivial text. Blast: every group's pass/refuse; FULL/PARTIAL/REFUSED.
- Text: SC:206. `gate_e6` is 30000 (an e6-scaled fraction, 3 %), `noise_e6/value_e6` is a plain fraction.
- Repro (`meas/est.py`): read literally, every case passes, incl. an outlier row at 3.58 % and a verify row at
  301 % ("literal_gate=True" on all six cases); value 0 divides by zero; a NEGATIVE value (verify_cmp, a
  difference, can be < 0 as grid1's `kit.delta.*` rows are) passes literally for any noise and FAILS always
  under the scaled form `noise_e6*1e6 <= gate_e6*value_e6`. Neither reading is written; the producer and the
  "independent" recompute (Goal 3) can pick differently.
- Fix: `noise_e6 * 10^6 <= gate_e6 * |value_e6|` with an explicit rule for |value| below the floor (MEAS-3).

### MEAS-3 CONFIRMED — the difference rows (`verify_cmp`, `enter`) bypass measure_sets.md §7.4's NULL rule
- Severity: answer/design. Effort: small. Blast: J4, J5 (and every row-1 key they feed).
- Text: SC:194 (verify_cmp = m(arm) - m(null)), SC:85/193 (enter = pass minus fail); measure_sets.md §7.4:
  "A delta row ... is NULL when |Δ| <= max(A/A floor, FRG x base) [or] the launch-paired deltas disagree in
  sign"; a cost row is "not a delta". The design never mentions §7.4; its only NULL word is SC:322.
- Effect (`meas/est.py` cases verify~0, verify<0): a compare cheaper than the loop's noise gets value 1500 with
  noise 4520 (301 %): under a relative gate the WHOLE verify group is refused (one row sinks the group);
  under the literal gate it passes and a sign-unstable number is priced. A negative cmp (an alignment win of
  the arm over `null`) is priced as a NEGATIVE cost in span_pick's verify_r. §7.4 exists for exactly this.
- Fix: delta rows take §7.4 (NULL, never refusing the group); the relative gate applies to cost rows only.

### MEAS-4 CONFIRMED (mechanism) / SUSPECTED (size on the box) — the walk's absolute A/A floor sinks fast arms, and they sit in the UNIT group
- Severity: design (likely REFUSED run). Effort: small. Blast: J2 (unit group: walk, memchr, pair), J6 SIMD.
- Text: SC:197-199 (aa = the GROUP's A/A arm, scaled by the value's ratio, i.e. ABSOLUTE); SC:206-207 (every row
  of the group passes; "the unit group at half"); §3.7 J2 = one group "walk, walk#b, memchr, pair".
- Drill (`meas/slope.py`): an absolute floor equal to f x walk becomes f/ratio relative on an arm of ratio r.
  At grid1's committed streamed-slope A/A p90 (`kit.eps.streamed.slope` 1730 = 0.173 %, zen4-grid1 set.tsv:67):
  memchr (r 0.06, the C_MEMCHR stand-in) aa-only 2.83 % > the unit group's 1.5 % half gate; vrun-w32 (r 0.03)
  5.67 % > 3 %. Even at 0.10 % memchr is 1.67 % > 1.5 %. The unit group failing is REFUSED (§3.5): the whole
  window is lost because memchr is fast, not because the unit is noisy.
- Confirm: the walk's per-group A/A median on this box (J2's dry data or grid1 F3 cells). Fix: per-arm A/A (or
  aa as a FRACTION of each arm, as §7.3 says "both as fractions of the value"), and the unit group = walk +
  walk#b only, memchr/pair their own group.

### MEAS-5 CONFIRMED — §3.4 is not an executable spec, so Goal 3's "EXACT recompute from the text" cannot hold
- Severity: maintenance/answer (the self-check is the set's only value control, §11 Q2). Effort: medium (write
  the integer recipe literally, as measure_sets §1.7 does for rhafz). Blast: every row; S2e's recompute check;
  sabotage (13).
- Items, each from the text:
  (a) find_byte "the least-squares slope of m over the three lengths" with m = "ns per unit of work (per byte)"
      (SC:189-192): the slope of ns/B over length is ns/B^2 (`meas/slope.py`: -1.7e-9), not the per-byte cost;
      the intended is total ns over length (0.1892 ns/B). find_hit "slope of time over hit count" with m in ns
      PER HIT: m = 778.8, 52.2, 9.9 at g = 4096, 256, 32 (h = 3.8): no slope over hit count recovers h.
  (b) the miss-only point "shared with find_byte" (SC:82) is J2's, another job and another launch sequence: the
      per-launch slope pairs launch l of J2 with launch l of J3 arbitrarily (and J2's rerun count may differ).
  (c) aa: WHICH point p of a multi-point group (3 lengths, 3 densities)? "the group's A/A arm" for J5/J6/J1 is
      not named (J4's is `null`, a loop with no compare).
  (d) sp: "the sample standard deviation of the per-launch values" — in ns or in the row's unit? Only aa is said
      to be scaled. And per-launch values divided by the MEDIAN unit, or by that launch's own unit?
  (e) integer rule: `est.py` implements sd as rounded-variance-then-root and noise as isqrt(aa^2+sd^2) (double
      rounding) vs one root over the exact rational: they differ by one unit on 4,793 of 20,000 random inputs
      ("a one-unit difference is a failure", measure_sets §1.7). The LS slope's integer arithmetic, x units and
      rounding point are unstated. Median over an even launch count (a dropped/contaminated launch) unstated.

### MEAS-6 CONFIRMED — find_hit is a cross-group row whose slope reads the densest regime; its noise scaling is off by up to ~38x
- Severity: design (regime) + answer (noise). Effort: medium. Blast: every `find_hit` key row 1 prices.
- Text: SC:82 (slope over g in {4096,256,32} + miss-only), SC:248 (J3: each density its OWN group), SC:198-199.
- (i) One row spans 4 groups (3 densities + J2's miss point): "pass iff ... on every row of the group" and "the
  group's A/A floor" have no single group to refer to.
- (ii) Regime (`meas/slope.py`): LS weights on the four points are -13.0, -12.7, -7.3, +33.0; the g=32 point
  carries 74 % of the slope's information. g=32 is 31,250 ppm; row 1's masses are 1,097 ppm ({x,X}) and 4,154
  ('/') (span_pick.md §Robustness), g ~ 240-900. Periodic hits at g=32 are branch-predictable in a way g~900
  random ones are not: the card measures the wrong density's hit cost wherever hit cost is non-linear in
  density, while the price is linear in m_r(S).
- (iii) Noise: a per-point A/A error d (ns/B) propagates to the slope as d x sqrt(sum w^2) = 38.4 d (independent
  per point) or 0 (a constant placement offset cancels in a slope); "scaled by the same ratio as the value"
  gives 1 x d. The design's aa term for slope rows is neither physical case.
- Fix: per-density rows (or a pinned density matching row 1's mass range) and the A/A taken on the VALUE
  (slope of A#b minus slope of A, per launch).

### MEAS-7 CONFIRMED — the in-group drift check refuses ~25-57 % of groups with NO drift, and is undefined for most groups
- Severity: design (PARTIAL/REFUSED by construction). Effort: small. Blast: every group of J1-J6.
- Text: SC:182-183, SC:207, SC:529 (it is the design's only drift control, §11 Q2).
- Drill (`meas/drift.py`, 5 launches, A/A floor = median |A#b - A|, compare |median(group walk) - unit walk|):
  between-launch sd 0 / 0.5 / 1 / 2 (within sd 1): false REFUSE per group 0.245 / 0.295 / 0.387 / 0.572. A true
  drift of 1 within-sd is caught only 52-63 %. With ~40 groups in the window, FULL is essentially unreachable.
  The threshold compares a difference of two MEDIANS across jobs (carrying between-launch variance) to a
  within-launch paired floor; grid2's own cross-launch trigger (spread > A/A floor) fired in 28 of 32 F1 reruns
  (r17b_prime.md:2043-2044), the box evidence that launch spread exceeds the floor.
- Undefined: J4 (forms + null), J5 (whole artifacts), J1 (pair widths) have no walk arm; J3's walk runs on a
  HIT subject, so it differs from the miss-only unit walk by hits x hit(walk) (at g=32, hit 20 u.B: +62 %),
  i.e. every hit group is "drifted".
- Fix: a walk miss-only CONTROL cell in every job (not every group), compared with a threshold from the
  between-launch spread (e.g. z x sqrt(sp_unit^2 + sp_ctl^2)), and a stated drift size that matters (the band).

### MEAS-8 CONFIRMED — J1's decision rule picks outcome (b) "file a D186 unit change" ~50 % of the time when no width matters
- Severity: design (spurious abi-event work, PAIR cards delayed). Effort: small. Blast: §3.6, J2/J3's PAIR rows.
- Text: SC:228-233. (a) needs 128 within the A/A floor of the BEST of 5 widths on all 8 cells; (b) some w
  beats 128 beyond the floor on a cell and loses on none.
- Drill (`meas/sweep.py`, all five widths truly equal, 8 cells, 5 launches): outcome shares a 0.063 / b 0.551 /
  c 0.386 (between-launch sd 0); a 0.042 / b 0.504 / c 0.454 (sd 1). Best-of-5 selection plus a single
  same-binary floor (MEAS-1) per comparison, 32 comparisons, no multiplicity control.
- Fix: a pre-registered margin on the paired per-launch difference (§7.4's sign rule plus a z x noise margin)
  and a family rule over 4 widths x 8 cells; (b) only when the same w wins on a stated majority of cells.

### MEAS-9 CONFIRMED — the coverage factor's "2.3 %" is not what z = 2 gives for the noise §3.4 defines
- Severity: doc/design (the derivation of a policy constant). Effort: small text. Blast: §6, COVER_Z_E3.
- Text: SC:397-399 "with 1-sigma card noise ... a departure happens with probability Phi(-z)"; SC:199-200 noise
  is a single-launch s.d. from 5 launches "not divided by sqrt(L): between-launch variation is systematic".
- Drill (`meas/stats.py`, equal-price comparison, one card): if launches are iid, the stored median's error vs
  the band 2s departs 0.62 % (not 2.3 %); if the systematic reading holds (a new run's draw vs s from 5 launches,
  the reason the text gives), 5.77 % (t_4-like). Phi(-z) assumes a KNOWN sigma; with 4 dof, P(s < 0.5 sigma) =
  0.090 (9 % of rows' noise understated 2x), 0.041 at 7 launches. The quoted 2.3 % is neither reading.
- Fix: state which error the band covers and quote the t-adjusted figure (or z from the t_{L-1} quantile).

### MEAS-10 CONFIRMED — one bad launch refuses a group whose median it did not move
- Severity: design (robustness). Effort: trivial. Blast: every group.
- Drill (`meas/est.py` case outlier): 4 launches within 0.03 %, one at +8 %: value 1,000,100 (median unmoved),
  noise 35,764 = 3.58 % > 3 % gate -> refused. The estimator pairs a robust centre with a non-robust spread;
  the +2-launch rerun keeps the outlier inside sp. Fix: a robust spread (1.4826 x MAD over launches) or the
  rerun rule replacing, not adding, a launch beyond k x MAD.

### MEAS-11 SUSPECTED — common-mode launch effects are counted as independent card noise in the band
- Severity: speed (wins forgone; safe direction). Effort: small. Blast: every priced comparison's band.
- Text: SC:194 value = median over launches / the unit's MEDIAN abs; SC:199 sp = per-launch spread. A launch-wide
  shift (frequency, ASLR/page colouring) moves every row of the launch together; it enters each row's sp and
  span_pick's band sums the cards in quadrature as independent (span_pick.md "the quadrature sum over cards of
  (coef_a - coef_b) x noise"), so a shift that cancels in price_a - price_b still widens the band.
- Confirm: per-launch ratios (row / that launch's unit walk) on J2's data vs absolute: if sp shrinks
  materially, normalize per launch (also resolves MEAS-5(d)).

### MEAS-12 SUSPECTED — the "streamed-fresh" regime does not pin the cache level, which moves memchr/SIMD cards several-fold
- Severity: design (regime, standing question 1). Effort: small text. Blast: find_byte/find_hit of memchr,
  pair, vrun, vany.
- Text: SC:81 "streamed-fresh, MISS-ONLY, long"; §3.2 "fresh streamed buffers". grid1's streamed = "a directory
  of distinct buffers ... cycle through the buffers" (docs/dev/lanes/grid1/README.md:94-96) with no footprint
  rule in the design. The driver calibrates to >= 50 ms (memchr ~0.011 ns/B => ~4.5 GB per loop): a pool
  inside L2 (1 MiB = the 7700X's L2), L3 (32 MiB) or DRAM gives different memchr rates; the walk (~5 GB/s) is
  insensitive, so the RATIO moves. span_pick prices "long subjects" without a cache level.
- Confirm: memchr's find_byte at a 4 MiB vs 256 MiB pool. Fix: pin pool size (and say "> L3" or "in L3") on
  the card's `subject` token.

### MEAS-13 CONFIRMED — derived-noise rules are first-order right but not exact-recompute specs, and cross-lin ignores fit covariance
- Severity: maintenance/doc (population 0 in zen4-grid3). Effort: small. Blast: FILE sets with derived rows.
- Text: SC:310-323. Each rule IS the first-order propagation for measures.md §3.2's definition with
  independent inputs (checked below). But "every product in int128 at e6, rhafz at each division" leaves the
  scale of (sa/a)^2 and the order of operations open (same class as MEAS-5(e)); and cross-lin's F_a and beta_a
  of one arm are the intercept and slope of ONE fit (§1.5 cells), negatively correlated, so quadrature
  without the covariance term misstates the crossover noise. Fix: write the integer formula literally; state
  "inputs assumed independent" as the rule's ASSUMPTION.

### MEAS-14 CONFIRMED — box-time text: counts and window figures do not agree with themselves
- Severity: doc. Effort: trivial. Blast: the window request to Frank.
- J3 "12 groups, 4-5 arms, 54 points" (SC:248); the §2.5 keys give `one` = memchr, walk, pair, walk#b (4) and
  `alt` = pair, walk, walk#b (3): 6x4 + 6x3 = 42. "+2/3 of a ~35-minute window" (SC:60): 5 vs 3 launches adds
  12.5 min to an 18.8-min 3-launch run (2/3 of THAT), not 2/3 of 35. Window: "~35-45" (§0), "~35" (§2.1),
  "~32, ~45 with waits" (§3.7), "~45" (S2d). "+40 %" (SC:238) is exactly 7/5, i.e. EVERY group rerun: a
  ceiling, not an allowance; and "28 of 32 F1 reruns" is a share of reruns, not of groups.

## PROBED-AND-HELD
- value_e6 = rhafz(abs x 1e6, unit abs) is dimensionally coherent for both units: ratio (ns/B over ns/B;
  memchr 11.35 ps/B -> 59,989) and walkbytes (ns/event over ns/B = u.B; 3.8 ns/hit -> 20,084,567 = 20.08 u.B).
  (est.py)
- ABSOLUTE noise in the row's unit is what span_pick's band needs ("(coef_a - coef_b) x noise", span_pick.md
  §The band; coefficients 1e6 for byte, m_r(S) for hit): consistent.
- Quoted numbers: Phi(-1) 0.1587, Phi(-2) 0.0228, Phi(-2.58) 0.00494; one-sided Bonferroni 5 %/10 -> z 2.576:
  all as quoted. One-sidedness right (only price(inc) - price(c) > band departs).
- §3.7 minutes recomputed: 0.95 s x 5 x 1.4 / 60 per point: J1 5.32, J2 1.33, J3 5.98, J4 3.99, J5 4.65, J6 9.97;
  282 points, 31.3 min ("~280", "~32"): consistent. Point counts J1 (8x6=48), J2 (12), J6 ((6+2)x3+36+30=90)
  consistent; J3 not (MEAS-14).
- §4.3 against measures.md §3.2 (6 rules): ratio |a/b| sqrt((sa/a)^2+(sb/b)^2) correct; ratio-complement the
  same (d(1-x) = -dx) correct; diff correct; cross-lin (F_b-F_a)/(beta_a-beta_b) -> relative quadrature of
  numerator and denominator, denominators squared so sign-free, correct for independent inputs; min/max
  "the supplying input, the larger on a tie" correct first-order; step 0; interp-log2 UNMEASURED.
- §3.4 cases that behave: clean (noise 0.117 %), A/A > spread (noise = aa, 0.5 %), bimodal non-unit row (median =
  majority mode, noise 1.64 % reflects the split; the unit row's bimodal test is separate). isqrt_rn exact.
- Not dividing sp by sqrt(L) is defensible as a prediction spread for one future run (but see MEAS-9).
- Isolation (fixture loop vs in-DFA) is declared model error outside the band (§2.6, span_pick R5.3): held as
  stated; MEAS-1 says the fixture side of it is unmeasured too.
