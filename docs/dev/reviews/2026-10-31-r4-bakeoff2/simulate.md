# SIM findings: bakeoff2 (pricing_bakeoff.md rev 1 @ deebb4dd8)

Lens: simulate. Method: (a) my own implementation of §7.2 + §9.3 from the TEXT, written before
reading verdict_drill.py (simulate/work/mytables.py), run on the 23 §9.5 outcomes rebuilt from the
table prose; then a diff against verdict_drill.py; (b) boundary hunt; (c) power re-derivation,
normal approximation plus a seeded Monte Carlo of the full four-condition SUPERIOR test
(simulate/work/power_mc.py). All scripts python3 -I, niced, seeded.

## Findings

### SIM-1 SUPERIOR's condition (iii) has no stated scale; under the definition it cites, SUPERIOR is unreachable
- status: CONFIRMED
- severity: answer
- effort: small
- blast radius: under the cited definition, no candidate is ever SUPERIOR to another, G = every candidate, and every reading lands MARGINAL (FM included in G). The drill reaches its targets only because the script quietly uses a different scale.
- where: §7.2 SUPERIOR (iii) ("N the measurement noise of the pair (quadrature over the differing sites of their NULL_c, regime_eval.md §3.0)"); verdict_drill.py `Pair.__init__` (`np.sqrt(...)/self.n`)
- finding: regime_eval.md §3.0 defines `N(S) = sqrt(Σ_groups (Σ_cells NULL_c)²)`, the noise of a regret SUM in walk-cost units. §7.2 compares it with d̄, a MEAN over n frame sites, and never says to divide by n. The script divides by n (N ≈ sqrt(k)·NULL/n) and uses one constant 1-point floor where the text names each site's NULL_c. With N read as regime_eval defines it, 2N for 16 differing sites at a 1-point NULL is 8 points. No δ-sized d̄ clears that.
- repro: `nice python3 -I simulate/work/scenarios.py mean` gives 2 of 24 off target (both D6, SIM-12). `... scenarios.py sum` gives 17 of 24 off target. D1, D3, D4, D4b, D9, D10, D11, D11b, D14, D15 and D16 all read MARGINAL, with FM inside G.
- proposed fix: write (iii) as `d̄ > 2·sqrt(Σ_i NULL_i²)/n`, with NULL_i the site's own floor (its cells' NULL_c summed linearly inside the site's timing group, regime_eval's within-group rule, then divided by the number of cells). Pin it as a prereg row and make the script use per-site NULL_i.

### SIM-2 D12b lands on target only because the script skips row 1's reach gate when L-KIT is absent
- status: CONFIRMED
- severity: design
- effort: medium
- blast radius: read as written, the backend-only verdict "PRICING DOES NOT PAY ON THE BACKEND SLOTS" cannot be reached. Read as the script does, it fires with NO blind-spot probe at all, which is exactly the unpowered early stop B3 was meant to remove (§0 item 4: "requires a POWERED blind-spot probe").
- where: §9.3 row 1 ("C-BLIND is green with reach ≥ 0.8"; "With C-BLIND's reach below 0.8 the row does not fire"); §8 C-BLIND (reach formula over "n kit sites"; population (ii) only on "census-truncated sites"); §3.1 dry census ("no pattern truncated at the cap"); verdict_drill.py `verdict()`: `if ok and r1["blind_reach"] is None: return PRICING-DOES-NOT-PAY "backend slots only"`; review-1 B3
- finding: without L-KIT, population (i) is empty (it needs L-KIT's dump). Population (ii) is empty whenever no site truncates, and the dry census truncated 0 of 259. So the reach is 0 (formula n = 0) and row 1 cannot fire. The script maps "no L-KIT" to reach = None and fires row 1 without checking reach. D12b's target is met only through that divergence.
- repro: read verdict_drill.py `verdict()` and the D12b scenario (`blind_reach=None`); census_dry_summary.txt "truncated at cap 0" (all 277). My text implementation needs an asserted reach of 0.85 for D12b, a number the design gives no way to compute without L-KIT.
- proposed fix: give the backend-only reading its own probe and reach, for example k salted random deny sets on EVERY H-core site (not only truncated ones), with the reach formula over that n. Then make the script compute the reach instead of skipping it.

### SIM-3 C-BLIND's red threshold is degenerate as specified, and the 0.87 reach holds only in that degenerate case
- status: CONFIRMED (the arithmetic and the definitional reading); SUSPECTED on how the A/A "beat" would actually be scored
- severity: design
- effort: medium
- blast radius: the control either reds on any single noise beat among about 440 draws (blocking row 1), or, if the A/A rate is measured another way, has a reach well below the 0.8 that row 1 needs and a large false-red rate.
- where: §8 C-BLIND ("Red when the number of beating sites exceeds the 99 % binomial bound of the false-beat rate measured on the A/A copies"; reach 0.87 / 0.66); §5.4 NULL_c = max(AA_c, ν·σ_pool)
- finding: (a) a draw beats when it is faster by more than max(NULL_c, 5 %). NULL_c ≥ AA_c, the cell's own A/A gap, so an A/A copy scored by the same rule can never beat. The measured false-beat rate is 0 by construction and the 99 % bound is 0: one beat anywhere is red. Nothing calibrates the false rate of a DIFFERENT arm, whose noise is not bounded by its own A/A. (b) Sites with k = 4 draws are compared with a one-copy-per-site rate. (c) The 0.87 / 0.66 values are P(≥ 1 detection). They are the reach of the red rule only when the bound is 0. With one A/A false beat in 130 copies (p0 = 0.0077, bound 4) the reach is 0.62 and the false-red rate with no blind spot is 0.24. At p0 = 2/130 the false-red rate is 0.65.
- repro: `nice python3 -I simulate/work/reach.py` (reach.out). The formula arithmetic itself checks: 1 − (1 − 0.1·(1 − 0.95⁴))^110 = 0.8725; k = 2: 0.6596.
- proposed fix: calibrate the false-beat rate PER DRAW on null draws: the model's own pick re-timed as a separate arm and scored by the same beat rule against its cross-fit half. State the reach of the actual red rule (detections > bound) at the measured p0.

### SIM-4 The EQUIV power column uses a wrong formula; the stage-0 floor derived from it is below 80 % power
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: the stage-0 STOP floor (40 sites) is a DERIVED prereg row whose claimed power (0.84) is really about 0.78. Row 3 of the power table misstates EQUIV power by a factor of 17 at n = 110 (it is understated, so the claims built on it are conservative).
- where: §7.2 power table; the "stage-0 floor" bullet (MEAS-11); verdict_drill.py `power_tables()` `eqp()`
- finding: the script computes `2Φ((δ−|D|)/se − 1.645) − 1`, the formula for a true difference of 0, at D ≠ 0 (its own header says "at true diff 0"). The normal TOST power is Φ((δ−D)/se − 1.645) + Φ((δ+D)/se − 1.645) − 1. The actual percentile site bootstrap (MC, 1,000 reps, B = 2,000) differs again at small differing-site counts:

  | row (s, g, σ_g) | claimed 110 / 40 / n80 | correct normal | MC (bootstrap) |
  |---|---|---|---|
  | .05 .02 .01 | 1.00 / 1.00 / 5 | 1.00 / 1.00 / 3 | 1.00 / 1.00 |
  | .05 .10 .10 | 1.00 / 0.84 / 38 | 1.00 / 0.92 / 28 | 0.98 / 0.78 / n80 ≈ 45 |
  | .05 .20 .20 | 0.03 / 0.00 / 335 | 0.51 / 0.18 / 242 | 0.51 / 0.41 / n80 ≈ 300 |

  The sd_d formula and the four sd_d values are right.
- repro: `nice python3 -I simulate/work/power_mc.py` (power_mc.out) and `power_n.py` (power_n.out: n = 40 0.783, 45 0.831, 50 0.829).
- proposed fix: correct `eqp`, add the MC column, and re-derive the stage-0 floor from the bootstrap (about 45-50 H-core sites at the pessimistic g = 10 %).

### SIM-5 Superiority sizing: the four conditions together give 0.65-0.71 at the stated n, not 0.80, and "about 16 differing sites, whatever the gap" is false near δ
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: an H-frame sized by §7.2 (320 / 160 sites at s = 5 / 10 %) finds a real 3-point winner only about 2 times in 3, and the expected outcome is INCONCLUSIVE far more often than the design budgets. Near the margin (d̄ = 2.5 points) the frame needed is about twice the stated one.
- where: §7.2 "Superiority needs differing sites" (n·s ≥ 7.84(1+CV²) ≈ 16; d̄ = 3 pt rows n = 307 / 150 / 71); §0 item 1 ("about 16 sites ... whatever the gap", "a frame of about 320")
- finding: the normal-approximation figures reproduce (sd_d, the 307 / 150 / 71, and 7.84·2 = 15.7). But the claim rests on (ii) alone. A seeded MC of the full test (d_i = 0 or N(g, (CV·g)²); percentile bootstrap; the mean-scale (iii) of SIM-1; the exact sign test over |d_i| > 1 point) shows two other conditions binding. (i) holds only 0.81-0.85 of the time. (iv) holds only 0.69-0.75, because at CV = 1 about 16 % of the differing sites go the other way and some fall inside NULL. All four together: 0.67 (s = 5 %, n = 307), 0.70 (10 %, 150), 0.65-0.66 (20 %, 71). 80 % needs about 20 differing sites (n ≈ 400 / 200 / 100). At d̄ = 2.5 points the script's own table already prints n = 691 / 337 / 160 (about 34 differing sites), and the MC at 16 differing sites gives 0.64. At CV = 2: 0.21 at n = 71.
- repro: `power_mc.py` / `power_n.py` outputs in simulate/work/.
- proposed fix: size the frame from the four-condition MC, not from (ii). Replace "whatever the gap" with the d̄-dependent table (n grows like (0.84·sd/(d̄−δ))² as d̄ → δ).

### SIM-6 A sign-test failure with six or more one-way sites lands MARGINAL ("about δ") for a difference far above δ
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: Frank is asked to rule on a "difference near the margin" that is 2.5δ but rests on too few clean sites. The honest reading is INCONCLUSIVE with a frame size.
- where: §7.2 UNDERPOWERED ("|d̄| ≥ δ on fewer than six one-way differing sites") and MARGINAL ("the interval excludes 0 but straddles δ"); T1 row 8
- finding: the six-site clause is a proxy for (iv) that only covers the all-one-way case. With 6 + 1 sites the sign test gives p = 0.0625, and with 6 + 2 it gives 0.14. Both fail (iv), and neither is "fewer than six one-way". The interval excludes 0, so the reading falls to MARGINAL, whose row-8 prose ("a pair in G differs by about δ") is false. The same happens when only (iii) fails.
- repro: simulate/work/boundary.py case B3. Dx is better on 7 sites by 80 % and worse on 2 by 3 % (d̄ = 4.9 points). drill → `('MARGINAL', ...)`; my text implementation → MARGINAL.
- proposed fix: UNDERPOWERED's second clause becomes "|d̄| ≥ δ, (i)-(ii) hold, and (iii) or (iv) fails", with the frame size taken from the sign test.

### SIM-7 The printed "frame size that would settle it" is smaller than the frame already read
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: an INCONCLUSIVE verdict tells the stage-3b lane that 54 sites would settle a pair already read on 110, so the J3b extension is sized wrong (or skipped).
- where: §7.2 UNDERPOWERED ("names the frame size ... `n x (half-width / gap)²`"); T1 row 7; verdict_drill.py `Pair.j4`; drill output D2 and D8
- finding: in the few-sites case the binding constraint is the sign test (six or more clean one-way sites), not the interval width. The text never defines "gap", and the script's choice gives D2 "A1-HY needs ~54 sites" on a 110-site frame and D8 "~45" on 40. Getting six one-way sites at D2's 4.5 % share needs about 133 sites, and more for power.
- repro: verdict_drill.out lines D2 and D8 (rerun output identical).
- proposed fix: frame size = max(interval-based n, the n at which the observed share yields enough one-way sites for (iv) at 80 % power).

### SIM-8 T2 has no row for T1 row 2 / row 3 / NO VERDICT on one shape; they fall to "SPLIT (regime)", a trade that does not exist
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: "pricing helps SHORT, and A1 is equivalent to FM on LONG" reads SPLIT (regime) ("Frank rules with the regime trade stated") instead of "A1 WINS on one shape only". UNRESOLVABLE on one shape plus a WIN on the other also reads SPLIT (regime), which hides a model defect.
- where: §9.3 T2 rows a-e; verdict_drill.py `T2` (it adds NO-VERDICT to the weak list, which the text does not)
- finding: rows c and d match only WIN and TIE kinds. A row-2 verdict (NO PLACEMENT BEATS FM, whose G may hold every candidate, all EQUIV) is neither, so any mixed pair falls to row e. Row 1 is read on both shapes jointly, so "FM is fine on LONG only" is exactly the case that reaches T2 this way.
- repro: boundary.py case B4. LONG: FM ≈ every candidate (all EQUIV, row 2). SHORT: A1 better than all on 12 sites by 30 %. drill → `('SPLIT', "LONG ('NO-PLACEMENT-BEATS-FM', ...) / SHORT ('WIN','A1')")`; text → SPLIT (regime).
- proposed fix: in T2, treat a row-2 verdict as a TIE whose group is G (so rows c and d apply), let UNRESOLVABLE and NO VERDICT dominate (like row b), and add a drill scenario for each case.

### SIM-9 T2 row d drops row 6b's named losses
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: a site losing 1.5x or more between two tied members on one shape reaches Frank as a plain TOP-GROUP TIE ("architecture decides"), so the 6b escalation is lost.
- where: §9.3 T2 row d ("both TIE"); verdict_drill.py `T2` (`kinds <= {WIN, TIE, TIE-WITH-LOSSES}` → returns `("TIE", inter)`)
- finding: when the two shapes differ only in 6 vs 6b with the same group, row a does not match (different rows). Row d then returns a plain tie on the intersection. The text is silent on whether 6b counts as "TIE", and the script answers that it does and drops the losses.
- repro: boundary.py case B5 (LONG TIE; SHORT the same with Dx losing 70 % on one site) → `('TIE', (A1, HY, Dx, MN, KF))` in both implementations.
- proposed fix: row d yields 6b (with the listed sites) if either shape is 6b.

### SIM-10 Row 0's per-row blocking: the script and the text disagree in both directions, and the text's fall-through can print a false MARGINAL
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: per the text, a red control that leans on row 4 only (the population / manifest control, lean "4") blocks row 4. With G = {X}, rows 5-7 do not match and row 8 "otherwise" prints MARGINAL ("a pair in G differs by about δ") for a one-member G. Per the script, ANY red control except C-BLIND returns NO VERDICT, including ones row 1 does not lean on.
- where: §9.3 row 0 ("NO VERDICT for that row and every row after it that leans on the same control"); §8 lean column (C-RULE 2-8; the strata / manifest control 4); verdict_drill.py `verdict()` (`if not (set(leans) <= {"C-BLIND"}): return NO-VERDICT`)
- finding: D13 hits its target only because its scenario carries no row-1 data. It reuses D12's outcome. With D12's row-1 data added and C-RULE red, the text gives PRICING DOES NOT PAY (row 1 runs "before any simulator exists" and does not lean on C-RULE), while the script gives NO VERDICT.
- repro: `nice python3 -I simulate/work/checks2.py`: drill → `('NO-VERDICT','C-RULE')`; my text implementation → `('PRICING DOES NOT PAY', None)`. The row-8 fall-through is shown by reading T1 with row 4 blocked and |G| = 1.
- proposed fix: say that a blocked row makes the WHOLE per-shape verdict NO VERDICT (rows are not skipped), except row 1, whose block only means "continue to T1". Mirror that in the script and add the D13-with-row-1 scenario.

### SIM-11 INCOMPLETE is not stated as global or per shape; read per shape, a coverage gap reads as a regime trade
- status: CONFIRMED (on my text reading; the script treats INCOMPLETE as global)
- severity: design
- effort: small
- blast radius: a rule that wins SHORT but has more than 2 % UNCOVERED LONG cells gives SPLIT (regime) ("X is outside the other shape's group") although X never lost on LONG.
- where: §3.5 ("more than 2 % UNCOVERED cells on any of the top-up readings is INCOMPLETE"); §9.3 ("dropped from the candidate set"); T2 row e
- finding: UNCOVERED is counted on cells, and cells carry a shape, so per-shape INCOMPLETE is a natural reading.
- repro: boundary.py case B6. A1 INCOMPLETE on LONG only and winning SHORT → SPLIT (regime) in my text implementation.
- proposed fix: state that INCOMPLETE on any shape drops the candidate from both (the script's behaviour), or add a T2 row that names the coverage gap.

### SIM-12 D6 (and D12c / D13b) land on target only through the drill's every-site construction
- status: CONFIRMED
- severity: doc
- effort: small
- blast radius: the drill claims "MN beats the priced options by 1.5 points → TOP-GROUP TIE". That holds only when the 1.5 points are spread over at least about a quarter of the sites. MN is first-match everywhere except its one priced row, so its differences are concentrated, and in that shape the verdict is MARGINAL.
- where: §9.5 D6; verdict_drill.py `base()` (one common multiplicative site weight, so every rule differs from every other on 100 % of sites, contrary to §7.2's "agreeing sites contribute d_i = 0 exactly")
- finding: with MN's 1.5-point advantage over the priced options on 100 / 50 / 25 % of sites the drill reads TIE, and on 15 % it reads MARGINAL. My text implementation, with the advantage on 14 % and on 5 % of sites, reads MARGINAL. MARGINAL is arguably the honest verdict for a real 1.5-point difference whose interval reaches δ. The design's stated intention is the one that is not robust.
- repro: boundary.py B10 (drill: TIE, TIE, TIE, MARGINAL); scenarios.py D6 / D6-concentrated OFF.
- proposed fix: build the drill's outcomes with exact zeros on agreeing sites at a stated disagreement share. State D6's verdict as a function of that share (EQUIV needs sd_d below about 3.2 points at n = 110).

### SIM-13 A d̄ of exactly δ is decided by floating-point rounding
- status: CONFIRMED
- severity: doc
- effort: small
- blast radius: an outcome at exactly the margin flips between WIN and MARGINAL depending on whether the scorer differences regrets or times. The C-SCORE "null mutation must score identically to the bit" property does not protect against this.
- where: §7.2 (i) d̄ ≥ δ; §9.2 (its "exactly δ" remark)
- finding: Dx better on 10 of 110 sites by 22 % (exactly 2.0 points on paper). Differencing regrets gives d̄ = 0.02 and WIN. Differencing times (1 + r) gives 0.019999999999999997 and MARGINAL.
- repro: checks2.py (it prints both means); boundary.py B1b (drill WIN, mine MARGINAL).
- proposed fix: the prereg states the comparison in fixed-point units (for example integer basis points after rounding) or with a stated tolerance.

### SIM-14 Script-vs-text divergences no drill scenario exercises
- status: CONFIRMED (by reading verdict_drill.py against §7.2 / §9.3)
- severity: doc
- effort: small
- blast radius: the prereg's claim that the drill "implements §9.3 exactly as written" is not true. Each item below can move a real verdict that no drill outcome covers.
- where: verdict_drill.py vs §7.2, §7.4, §9.3
- finding: (a) row 5 vs row 7: if robustness is UNDERPOWERED and a powered stratum FAILS, the text's first match is row 5 (SPLIT). The script returns INCONCLUSIVE, because its robustness check runs before the stratum check (`if r.startswith("underpowered")`). (b) Row 6b: the script uses |d| > 0.50 in regret points. The text says a loss "above 1.5x outside NULL_c", a ratio. (c) Robustness: the script uses the 97.5 % quantile where the text says "95 % upper bound". (d) "Differing sites" for N: the script uses |d| > FLOOR, not d ≠ 0. (e) Powered strata: the script takes "powered" as a given flag, while the text defines it as "the winner's pair tests inside the stratum are not UNDERPOWERED". (f) Row 1: the script takes `ub` and `big` as given numbers and never computes them from per-site FM regret.
- repro: read the functions `T1`, `robust`, `stratum_ok`, `Pair`, `verdict`.
- proposed fix: either align the script with the text item by item, or write the script's choices into the text. Then add a drill scenario per item.

### SIM-15 §5.6's H-core composition double-counts S-bench (minor; the error is conservative)
- status: CONFIRMED
- severity: doc
- effort: small
- blast radius: the H-core timing is about 3.6 h, not 4.0 h. The total stays about 7 h.
- where: §5.6 H-core row ("≈105 S-real x 1 + ≈25 S-bench x 3") vs §3.2 (H ≈ 170 S-real + ≈ 23 S-bench; H-core = 2/3 of H by hash)
- finding: two thirds of the ≈ 23 S-bench sites is about 15, which leaves about 113 S-real in H-core: 113 + 15·3 ≈ 160 streams, not 180.
- repro: arithmetic from §3.2's own sizes.
- proposed fix: restate it as ≈ 113 + ≈ 15 x 3 ≈ 160 streams, or say that all S-bench rows go to H-core.

## PROBED-AND-HELD

- §9.5's 23 outcomes rebuilt from the table PROSE and run through my own text implementation (simulate/work/mytables.py, scenarios.py): 22 of 24 (D6 in two shapes) land where §9.5 states, on the mean-scale reading of (iii). The 2 off-target are D6 only (SIM-12). D11 needed my construction to keep the degradation unbiased; once it did, it landed.
- verdict_drill.py rerun from my copy (`nice python3 -I verdict_drill.py --power`): rc 0, 23 scenarios, 0 off-target. The output is byte-identical to subject/verdict_drill.out.
- G is never empty (8 constructions incl. B7, FM alone at the top, which gives row 2, "NO PLACEMENT BEATS FM"). SUPERIOR requires d̄ ≥ δ > 0, and paired means on a common frame are additive. A cycle X>Y>Z>X would need the means to sum to ≥ 3δ while summing to 0, so SUPERIOR is acyclic and the lowest-mean candidate is never beaten. This holds as long as every pair is read on the same frame sites; UNCOVERED cells (≤ 2 %) dropped per pair could in principle break additivity, but only with regrets of 300 % or more on those cells.
- Exactly 6 one-way differing sites: p = 1/64 < 0.025, and a 6-site, 3.3-point winner reads WIN in both implementations (B2). Exactly 5: p = 1/32, so it fails (D2).
- A single-site loss between tied members (sweep 0.5-2.0, B8): 6 below 0.6, 6b for 0.6-0.72, INCONCLUSIVE from 0.75. The verdict weakens as the loss grows, but coherently: a larger frame resolves it.
- sd_d formula and its four values (0.0049 / 0.0312 / 0.0624 / 0.0872); n·s ≥ 7.84(1+CV²) = 15.7 at CV = 1; 320 / 160 frames; the d̄ = 3 points rows n = 307 / 150 / 71 (normal approximation, (i) and (ii) only): all reproduce.
- §0 item 1: 0.1 points is twenty times below δ. "90 % interval inside ±δ at n ≈ 110 whenever sd_d < about 5 points" holds and is conservative (normal: 80 % power up to sd_d ≈ 8 points at d̄ ≈ 0).
- C-BLIND reach arithmetic: 0.8725 (k = 4) and 0.6596 (k = 2) reproduce exactly. The defect is in the red rule (SIM-3), not in the formula.
- §5.6 run length: arms 3.2 + 0.65 + 2.9 + 3.84 + 1 = 11.6 (D, "12") and + 3.84 = 15.4 (H-core, "16"). The census means check: 553/172 = 3.21 default-route, 503/172 = 2.92 route-seed, 112/172 = 65 % no-search. Every timed-work cell (4.0 / 2.0 / 0.2 / 0.7 / 1.5 h, C-XH 1-3 h) and the ≈ 7 h total reproduce, apart from SIM-15's stream count.
- Row 1 thresholds D12 / D12c / D13b, and T2 rows a, c and e on D9 / D10: they land in both implementations.
