# SIM critic: crit-memfn-spanpick4 (span_pick rev 4, 76a7f02e7)

Lens SIM: the blind minimax rule and the with-data rule run over the real data. Own implementation from
the design text: SIM/mine.py (written before smp20.py was opened); outputs SIM/*.out.

## Findings

### SIM-1 CONFIRMED (doc): the '/'-region threshold "hit(PAIR) at least 4x hit(memchr) (8x at hit(memchr) 5)" is wrong
- Where: §Robustness "Card values that make '/' the minimax pick" (rev 4 line 310-314).
- Repro: SIM/thresh.py (own implementation SIM/mine.py of the design's formula, stand-ins of §Robustness,
  bundles population/bundles_spanpick3; byte(PAIR) swept 1.00-8.00x in 0.05 steps, hit(PAIR) in 0.25x
  steps), output SIM/thresh.out. Cause confirmed after the blind implementation: smp20.py sweeps hit(PAIR)
  only at 1x, 2x, 4x, 8x hit(memchr) (smp20.out lines 40-55, which my sweep reproduces exactly where the
  grids overlap), so "at least 4x"/"8x" are grid points, not boundaries. The least hit(PAIR)/hit(memchr) multiple at which '/' is the minimax
  c* for some byte(PAIR): hit(memchr) 5: 4.75x (design: 8x); 10: 3.5x; 20: 2.75x (hits 20/55, byte(PAIR)
  2.55-2.75x; at 20/60 '/' holds 1.90-2.70x); 40: 2.25x (40/90, 4.45-4.70x; at 40/120 '/' holds
  1.65-4.50x); 60: 2.25x. Expected per the text: no '/' region below 4x.
- Also "With hit(PAIR) at most 2x hit(memchr) '/' is never minimax" fails at hit(memchr) >= 80: at
  exactly 2.0x '/' is minimax for byte(PAIR) 8.00-8.50x (80/160), 10.2-12.3x (120/240), 12.3-16.2x
  (160/320). Out of the plausible card range, but the sentence is unconditional.
- What reproduces: the four byte(PAIR) ceilings (2.60x at 20/80, 2.10x at 20/160, 1.10-1.75x at 10/40,
  4.25x at 40/160) and "{X,x} holds up to 4.20x (20/20), 3.25x (20/40)" (SIM/sweep.out).
- Why it matters: the stage-2 reading the design schedules ("is the measured card point in '/''s region,
  {X,x}'s or '3''s?", §The watched witness) would misread a measured point at hit ratio 2.75-4x as
  outside '/''s region. Likely cause: the study swept only hit multiples 1,2,4,8 (to confirm against
  smp20.py). Fix: state the region as the sweep's actual boundary per hit(memchr) (or a finer grid).
- Effort: one paragraph + a finer sweep grid. Blast radius: the forecast text only.

### SIM-2 CONFIRMED (design): the minimax pick depends on IRRELEVANT candidates (the loss normaliser min_c' over the set)
- Where: §The pick "The priced action" 2-3 (`loss_r(c) = price_r(c) / min_c' price_r(c')`).
- Repro: SIM/iia.py, SIM/iia_case.py (outputs .out). Card point hit(memchr) 10, hit(PAIR) 20, byte(PAIR)
  0.12 (2.00x), other stand-ins as §Robustness, kinds P, F, log, weblog. Candidates {@0 {X,x}, @1 '/'}:
  W({X,x}) 2.718 (F), W('/') 2.470 (weblog) -> c* = '/'. Add @5 '4' (its own W 3.904, never picked):
  '4' becomes weblog's least (194,665 < 286,612), '/''s weblog loss rises 2.470 -> 3.636, c* = {X,x}.
  The full six-candidate set also picks {X,x}. Over a grid of 435 card points (hit(memchr) 10/20/40 x hit(PAIR) 1,2,3,4,6x x byte(PAIR) 1.00-8.00x step 0.25) x every candidate subset
  containing the default, 720 "add a non-picked candidate, the pick flips between two OTHER candidates"
  cases; three distinct shapes (also '4'->'3' when '/' is added at 10/10, 6.00x; '/'->'3' when '4' is
  added at 10/20, 2.50x).
- Why it matters: the candidate set is "the complete plans that differ from the default only at the
  row's LEVELS" (step 1), so it moves with things unrelated to the two plans being compared: which levels
  a row opens, soundness flags (a RESEED alternative never stops at F0), a `--memfn=no-X` deny filtering
  T-FIND/T-PICK rows (open point 5), a new T-FIND method row (Growth rule: "a new method adds a T-FIND row
  plus its card"). Adding a method row whose candidate is never chosen can move every site's pick between
  two old plans; a stage-3 "no-mover" claim for such an addition does not hold by construction. Neither
  §The pick nor §Robustness states this property (it is the known non-IIA property of minimax regret).
- Fix options: state it (and make any candidate-set change a choice event with its own evidence), or
  normalise by a set-independent reference (e.g. the default's price, loss_r = price_r(c)/price_r(default)
  makes W a pairwise comparison against today's plan), or by the per-kind least over the FULL legal
  set regardless of the row's levels. Effort: a paragraph + the smp20.py loss line. Blast radius: every
  priced row; the stage-3 mover accounting.

### SIM-3 CONFIRMED (design/doc): on the DEF-deny arm the minimax rule moves today's '/' to '3', a mover the witness table does not forecast
- Where: §The watched witness table, row "stage 3 row 1" column (1) ("the minimax pick", read on every arm
  incl. the DEF deny), and today's row ("'/' on the DEF deny"); §The pick open point (5) (denies filter
  T-FIND/T-PICK rows).
- Repro: SIM/defarm.py -> SIM/defarm.out. Under `--memfn=no-window-search,no-window-skip` the PAIR
  candidate is filtered (witness: DEF blind stops on '/' alone), so the candidates are the five
  one-member memchr stops, default '/'. Stand-ins, kinds P, F, log, weblog: W('/') 4.055 (weblog: '/'
  1,225,432 vs '4' 302,235), W('3') 1.974 (log: 760,657 vs '/' 385,409), W('4') 2.216, W('2') 3.221,
  W('1') 3.789. c* = '3', W(default) - W(c*) = 2.081 (independent of hit(PAIR)). Once card noise exists
  and is under ~2.0 in loss units, the DEF arm departs '/' -> '3' even though P prefers '/' 1.49x and
  `log` prefers it 1.97x.
- Why it matters: (a) the RTE/DEF ratio the design reads smp20 by (job 588's 1.58-4.03x, Goal 2's
  "RTE/DEF <= 1 + floor") has a MOVING denominator at stage 3; a "closed" ratio could come from DEF
  getting slower, not RTE faster. (b) Goal 2 requires every arm's movers read new/old <= 1 + floor; this
  mover is not listed for evidence. Fix: state the DEF-arm forecast in the witness table and judge smp20
  by absolute per-arm times (new/old per arm), not RTE/DEF, from stage 3 on; or state that the deny arm
  also denies the priced row. Effort: two table cells. Blast radius: the watched witness's reading.
- Caveat: if a walk-method {X,x} candidate survives the deny, it re-normalises the losses (SIM-2); the
  computation above has no walk card to price it.

### SIM-4 CONFIRMED (design): the with-data rule names no departure TARGET; on the stand-in '4' vs '3' is a 1.46-sigma call on counts 11 vs 19
- Where: §The pick "With data" ("a candidate departs from it only if cheaper beyond the band under B
  ALONE"); §The watched witness stage 3 row 1 (2) ("'4' departs under B (63,555 vs 168,871)").
- Repro: SIM/withdata.py -> SIM/withdata.out (my Poisson band: per position set, sqrt(count) x 1e6/N
  times d price/d mass, quadrature; N = prose's 69,462 counted bytes). Under prose FOUR candidates beat the
  incumbent {X,x} (168,871) far beyond band: '4' 63,555, '3' 66,143, '2' 70,350, '/' 72,938. The text
  never says which one departs (the least? the least with TIE among those within band of it?). '4' vs '3':
  gap 2,588 against a 1-sigma sampling band of 1,774 (counts '4' 11, '3' 19): beyond band at 1 sigma, within
  band at 2 sigma (then TIE's rows decide, not the price, and the witness's '4' is not guaranteed; either
  stop still PASSES (2), which only needs a one-member stop rarer than {x,X}). An exact Poisson split test of
  11 vs 19 under equal rates gives P(<= 11 of 30) = 0.100 one-sided, 0.200 two-sided: not a significant difference.
- Fix: state "departs to B's least; candidates within band of B's least go to TIE" (mirroring step 3), and
  write the witness cell as "a one-member stop ('4' or '3', TIE between them)". Effort: one sentence.
  Blast radius: the with-data rule's spec and the witness cell.

### SIM-5 SUSPECTED (design): the band has no stated coverage factor, and Poisson sqrt(n) is 0 at n = 0
- Where: §The band of a comparison; §The pick "With data" (`sqrt(n)` on a count n).
- Observation: "exceeds the band" with band = the quadrature sum of coef x noise is a 1-sigma test unless
  `noise_e6` is defined as something else (the text cites the 3 % `gate_e6` as the only constant, and D186
  add. 2 says "the cards' measured noise"); which sigma multiple a departure needs is never stated. A
  1-sigma test departs on ~16 % of equal-price comparisons per side. Separately sqrt(0) = 0: a byte absent
  from a small bundle carries zero sampling noise. Constructed: prose counts '#' 0, '[' 3 (SIM/w/bundles/
  prose.list); for a site whose candidates stop on '#' or '[', the gap 3 x 14.4 ppm x 22.5 = 970 exceeds the
  band sqrt(3) x 14.4 x 22.5 = 561 (byte and hit cards cancel, both memchr), so the rule departs on a 0-vs-3
  count split (equal-rate probability 1/8). The price stakes there are small (~1.6 % of 60,000), so the
  harm is bounded; the issue is that property (iii) "the cell's subject is B's kind within B's sampling
  noise" leans on a band whose confidence is undefined.
- Would confirm: the stage-2 noise-field definition (1 sigma vs a gate). Fix: name the coverage factor
  (one constant, labelled UNMEASURED DEFAULT as `gate_e6` is) and use a Poisson interval that is nonzero at
  n = 0 (e.g. the count's upper bound). Effort: a sentence. Blast radius: every priced comparison.

### SIM-6 CONFIRMED (doc/maintenance): smp20.py diverges from the design text it evidences
- Where: population/span_pick_rev4/smp20.py vs §The pick 1-4, "With data", §Robustness.
- Divergences (my text-only SIM/mine.py vs smp20.py; prices, losses and worst cases are otherwise
  identical to the unit, all 60 price cells and 12 worst-case values):
  (a) guard (b) is not implemented: the printed "minimax pick" is c*, never compared with W(default) and a
      band (the docstring says so; the design's sentence "guard (b) keeps it anyway" at line 309 is not
      something the script computes). (b) ties on W break by lowest offset (`min(..., key=(w, i))`), not by
      TIE's rows (step 3). (c) "with data" prints B's least, with no incumbent comparison, no band and no
      Poisson term, so the witness claim "'4' departs under B" is not tested by the script (SIM-4).
      (d) the card sweep's hit grid is 1, 2, 4, 8x (the source of SIM-1's wrong thresholds). (e) the
      candidates are the six stream-method stops only; the formula's walk and Horspool lines are never
      priced, so a row that opens the METHOD level (walk on {X,x}, Horspool over the window) is outside the
      study, and per SIM-2 their presence can change the pick. (f) P is read from `--list-analysis
      default` (bundle digest 1822fb973b95a4da) while §Robustness names PRIOR_AUTHORED `a322116b1b87f9f6`;
      the quoted values agree ({x,X} 1,097 = 100 + 997, '/' 4,154), so this is a labelling gap only.
- Fix: say in §Robustness that the printed picks are c* ignoring guard (b) and the with-data band; add the
  band/TIE/with-data target to the script when the noise field exists. Effort: small. Blast radius: the
  study's credibility as a mechanism check.

### SIM-7 CONFIRMED (doc): in a with-data compile, "the default" of step 3 is ambiguous (KEY reads B)
- Where: §The pick step 3 + "With data" ("the BLIND pick (steps 1-4 ...) is computed first and is the
  incumbent") + "NOT covered: ... KEY's mass-only rows read B as their prior".
- Repro: witness.out (re-run, SIM/witness.out): with `--analysis prose` today's KEY default is @5 '4', not
  {X,x}. Step 3 keeps "the default" unless W(default) - W(c*) exceeds the band. If "the default" in a
  with-data compile is that compile's KEY default ('4', W 6.654), the blind step departs to {X,x} (W 2.000)
  and the B step departs back to '4': the same final answer here, but whenever W(KEY_B default) is within
  band of W(c*), the "incumbent" is the KEY_B default, not the blind compile's pick, and the property's
  sentence "the with-data pick's predicted price under B is <= the blind pick's" compares against a plan
  the blind compile never chose. It still holds within band (a blind-compile pick cheaper beyond band
  under B would itself depart), so the property survives; the text should say which default.
- Fix: one clause: "the default of a with-data compile's blind step is the BLIND compile's default (KEY
  over the prior)". Effort: one sentence. Blast radius: implementer reading of step 3.

## PROBED-AND-HELD

- §Robustness price table: all 5 kinds x 4 quoted columns at hit(PAIR) 20 and the 5 bracketed hit-40
  values reproduce to the unit from my text-only implementation (SIM/mine.out); the "kind's least" column
  holds at both hits ('/' least under P and '4' under weblog at hit 40, as bracketed).
- Minimax worst-case lines: all 6 values at hit 20 ({X,x} 2.000 F, '/' 4.276 weblog, '3' 5.925, '4' 6.654,
  '1' 8.939, '2' 9.670, the latter four set by log) and the 3 at hit 40 (3.056, 4.055, 5.600) reproduce.
- Card-value region: the four byte(PAIR) ceilings (2.60x at 20/80, 2.10x at 20/160, 1.10-1.75x at 10/40,
  4.25x at 40/160), "{X,x} holds up to 4.20x (20/20), 3.25x (20/40)" and "then '3' (worst 2.5-4.0, set by
  log)" reproduce (SIM/sweep.out: '3' W 2.13-3.56 at the switch points, all set by log). Only the
  hit-multiple thresholds fail (SIM-1).
- Job 588's none cell: RTE/DEF 2.79 with none's {x,X} 1,388 per 1 MB and '/' 0 (t588tri §a) gives
  byte(PAIR) x 1e6 = 2.79 x 60,000 - 1,388 x 22.5 = 136,170, i.e. 2.27x byte(memchr) ("~2.3x" holds), inside
  {X,x}'s region at hits 20/20 (up to 4.20x) and 20/40 (up to 3.25x).
- §The watched witness: "2.00 vs '/''s 4.28" holds; witness.sh re-run into SIM/w with the review tree's
  binaries (8 compiles): SIM/witness.out is byte-identical to the committed witness.out (blind {X,x} on
  default/vm/SIMD-on, '/' on the DEF deny; prose '4' on three arms, '/' + '4' on the DEF deny; bundle
  digests 1822fb973b95a4da and 4542f53066ffb40c match). Bundle rates quoted (prose {x,X} 2,172, '/' 575,
  '4' 158; log '/' 14,462 vs {x,X} 372; weblog 51,754 vs 7,396) hold.
- "With data matches or beats blind by construction" (re-derived under minimax): holds for the predicted
  price under B, up to the band, whatever the incumbent (SIM-7 is wording only). B a blind kind: log, no
  departure ({X,x} is log's least, every gap >= 257,025 vs band <= 5,175); weblog at hit 20, {X,x} is
  weblog's least (no departure; '4' 15,622 behind, band 3,032); at hit 40 weblog's least is '4' (the
  incumbent {X,x} loses 132,297), so the with-data pick is B's least, as the text says.
- Unmeasured card noise: steps 4 and "With data" both forbid a departure with `noise_e6` missing; today all
  68 kit rows carry '-', so every rule above is inert until stage 2 (consistent with Goal 2 stage 1).
- F's five one-member ties: the per-kind normaliser is the tied minimum (147,929), so the tie does not
  perturb losses; no exact W ties arose over the 435 card points x every candidate subset holding the default. Near the '/'/'3' boundary W gaps
  fall to 0.12-0.6 % (SIM/region.out): those points go to TIE's rows under any realistic band, which is the
  rule's stated behaviour, not a defect.
- Zero-ppm byte in a real blind bundle: log has 'X' count 0; {X,x} carries x's 373 counts, so its band is
  nonzero; no sqrt(0) term enters smp20's comparisons (the n = 0 case is SIM-5's constructed one).
