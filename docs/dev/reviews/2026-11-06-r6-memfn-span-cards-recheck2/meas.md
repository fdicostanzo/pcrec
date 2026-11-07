# meas — memfn-span-cards-r11
Critic: measurement lens. Subject span_cards.md rev 1.1 @ ef2f130fc; build tree 6f1b40f75. Scratch: meas/ (mine.py =
my implementation of §3.4-§3.5 written from the TEXT before reading drill.py; run/ = the design's drills re-run).

## Findings

### MEAS-1 — placement is seeded from (job, l, arm): a re-run links the SAME seven placements, so r5 PLACE/meas-3's "a re-run cannot clear it" is partly back, and HELD's 0.3 % is computed on an independence the text does not give
CONFIRMED (text + drill). §3.2: pads "drawn by a seeded generator from (job, l, arm)", re-draws "seeded,
deterministic"; no run/window term in the seed. The frozen commit re-run in a later window (§3.5 "re-run whole")
therefore re-links identical executables: placement is noise WITHIN a run but a fixed draw ACROSS runs.
place_drill.py A computes rev 1.1's "held" as `r2 * r2` (two independent runs). Repro `meas/seeded_place.py`
(place_drill's model and estimator, 4,000 runs; run 2 reuses run 1's placements, fresh run noise):
s 0.5 % tau 0.5 %: refused 5.72 %, held seeded **1.02 %** vs independent 0.38 % (P(re-run refuses again | refused)
**17.9 %** vs 6.6 %); tau 0.7 %: 6.80 % vs 4.00 % (35.8 % vs 21.1 %); tau 1 %: 36.8 % vs 27.5 %. So §3.2's "Below
tau ~ 0.5 % rev 1.1's refusals are run noise and a re-run clears them" and §3.5 HELD's "(two independent runs ...
both refuse 0.3 %)" overstate by ~3x; the same holds for J1 (j1_drill's "launch" mode assumes fresh draws) only
within one run, which is all J1 has. What MOVES on regeneration: run noise yes; placement NO (re-run, and a new
box with the same toolchain). Severity: design (the HELD outcome's statistics; r5 PLACE (i) claimed fixed).
Effort: one word (seed from (run id, job, l, arm), the run id the window's, recorded in PROVENANCE) + re-quote.
Blast: §3.2, §3.5 HELD, place_drill.py. Alternatively state that the re-run is deliberately the same layout and
re-derive HELD's figures for it.

### MEAS-2 — the outcome table (FULL/PARTIAL/REFUSED/HELD) is not drilled and its "floor" has two readings; under one, r5 GOAL2's exact scenario is still ACCEPTED, under the other PARTIAL-by-refusal is dead
CONFIRMED (first-match drill `meas/outcome_drill.py`, §3.7 jobs/groups, §2.5 keys, §1 Goal 2 floor; `meas/outcome_drill.out`).
§3.5 PARTIAL: "Goal 2's floor holds over every key NOT NAMED"; REFUSED: "or Goal 2's floor fails"; §1 Goal 2:
"A run that passes its gates but misses the floor is REFUSED". Reading A (floor over all keys) vs B (named keys
exempt):
- S3 J3 drift-refused: A REFUSED, B PARTIAL with NO priced random find_hit row for libc/walk/walk-set.
- S6 = r5 GOAL2's scenario ("non-unit groups refused but one"): A REFUSED; **B PARTIAL with 3 priced keys** (unit,
  libc, walk-set). r5 GOAL2 ("cannot fail") is fixed only for the all-NULL half; §R1.1 claims it fixed.
- S8 J4+J5 drift-refused: A REFUSED, B PARTIAL (no verify, no enter row).
- Under A, every gate or drift refusal of any job holds a floor key (every job does: J2.byte every find_byte key,
  J3 random rows, J4 every census pair, J5 NONE, J2p pair unless (b)), so PARTIAL is reachable ONLY by J1 (b): the
  "some group is refused" clause of PARTIAL is dead text.
- S5 every non-unit group refused: under B matches BOTH PARTIAL and REFUSED ("nothing but the unit passes"); the
  table states no precedence (pcrec-decisions-as-first-match-tables).
- HELD "a second REFUSED on the same cause ... or the same floor key": under A a twice drift-refused job is HELD
  on its floor key, though drift is box state, not "a property of the frozen text" (HELD's own rationale). And a
  two-phase-class unit refuses by gate in one run and by bimodal in another (MEAS-9's split: both fire 16 % at
  0/2 %), so "the SAME cause" needs a rule for a refusal with two causes.
drill.py implements none of this (Text vs script diff 1). Severity: design (Goal 2/Goal 3: the recompute must
re-derive `partial` EXACTLY from this text). Effort: small (one first-match table: REFUSED rows first, the floor's
key domain stated, refused-by-drift vs refused-by-text causes). Blast: §3.5, §1 Goal 2, the recompute (S2e).

### MEAS-3 — standing drill "add a never-picked candidate": a sibling cost row's gate refuses its whole GROUP, removing a passing row
CONFIRMED (text + `meas/outcome_drill.out` S7). §3.5 "A group passes iff every cost row in it passes"; the
set "holds passing groups' rows". J2's byte group holds libc AND walk-set (§3.7). A walk-set row above its gate
(a form row 1 may never pick) removes `find_byte.libc`: reading A -> the whole run REFUSED (every find_byte key is
a floor key); reading B -> PARTIAL with libc unpriced. The normalisers themselves do not couple: ctl (per job),
W (unit only), trim (per row) read no sibling, and adding an arm moves no other row's arithmetic (by the formulas;
PROBED-AND-HELD). The coupling is the group verdict only. The unit group is guarded (walk + twin only, MEAS-4 r4).
Severity: design (a priced row lost to a sibling's noise). Effort: small (cost rows pass/fail per ROW, the group
verdict kept for the unit and drift). Blast: §3.5, §3.7 J2/J2p grouping. If walk-set folds into walk (§2.4) the
J2 case vanishes but the rule stays.

### MEAS-4 — drift: "smaller drifts are unresolvable by a 7-launch median comparison" is false; the threshold is on the PER-LAUNCH scale, ~4.5 standard errors of the statistic
CONFIRMED (`meas/drift_se.py`, 4,000 runs, place_drill B's model). The statistic |med_j - med_2| has s.d. 0.65-0.66
s_L; the threshold 3 x isqrt(sp2_2 + sp2_j) is 3 x sqrt(2) x s_L = 4.24 s_L, i.e. ~6.4 s.e. At s_L 1 %: a 3 % drift
is refused 18.1 % by the rule, but a 3-s.e. rule refuses it 90.5 % with 0.6 % false; 2 % drift: 3.0 % vs 52.7 %.
So drifts of 2-3 % at s_L 1 % ARE resolvable; the factor 3 (labelled D149) sets the trade, and the text's
justification for low power is wrong. Severity: doc/design (the r5 DRIFT text fix restates power correctly but adds
a false reason). Effort: text (state the scale; or put the s.e. in the threshold). Blast: §3.5 Drift.

### MEAS-5 — the delta NULL rule's "every D_l > 0" has no outlier tolerance, while the spread trims one launch
CONFIRMED (`meas/null_outlier.py`, floor_drill's model + a one-sided cell spike with prob q, 4,000 runs). Walk form
g 1024, h 20 wb (hits 2 % of a call), s 0.5 %: priced 97.9 % clean; q 2 % k 3 %: 87.0 % (one-launch trim: 97.5 %);
q 5 % k 8 %: 68.8 % (90.9 %). One base-cell spike nulls EVERY row that base serves in that launch (J3's base.walk
serves four, §3.4 step 2). §3.5's table shows the trim absorbing "one outlier +8 %" for cost rows; the same event
on a delta row is a NULL, and on a floor key a REFUSED run (MEAS-2 A). floor_drill's h50/h90 (§2.3) assume normal
noise only. Severity: design (floor fragility). Effort: small (the sign rule over the trimmed six, or say why not).
Blast: §3.5 NULL rule, §2.3 floor figures.

### MEAS-6 — J1: margin 2 and "5 of 8" are not selected by (b)'s false rate (0 % over the whole re-swept region); their only drilled effect is power, and the "intended reading" does not cover the power lost
CONFIRMED (`meas/j1_sweep.py`, j1_drill's model, 3,000 trials, margin {1,1.5,2,2.5,3} x k {3..6}).
False (b) with no effect: 0.0 % at EVERY (margin, k), tau 0 and tau 1 (the all-seven-signs rule alone makes it
~0). Power, true effect 4 within-s.d., tau 1: m 2 / k 5 10.4 % (the design's 9.7 %), m 1.5 / k 5 53.9 %, m 1 / k 5
90.0 %. §3.6 says the constants were "chosen for (b)'s false rate under no effect (drilled below)"; the drill
cannot select them. §3.6 also says "An effect smaller than a width's own placement spread is not one an artifact
would see": at tau 1 the effect 4 is ~2.8x the per-launch placement s.d. of r (sqrt(2) tau), yet filed 9.7 %.
Severity: design/doc (a pre-registered rule whose stated reason does not bind; J1 is the ONE bounded effort,
pcrec-one-pass-loss-chasing, so its power is the point). Effort: text, or a re-chosen margin with its drill.

### MEAS-7 — J1's verdict, which sets the set's PARTIAL status, has no independent control
CONFIRMED (text). J1's cells are outside the set (§3.5 CELLS-2), the verdict is re-derived only by
`slot/j1_rule.py` in the SAME slot harness (§3.6), and the recompute takes "the run summary's list of groups that
never ran" (J2p under (b)) as GIVEN. A slot bug giving a false (b) yields an accepted PARTIAL set missing every pair
key, with nothing sharing no source checking it; Goal 3's independence stops at J1. Severity: design (low).
Effort: small (the recompute, or a pcrec-side test written from §3.6, re-derives J1's verdict from j1_cells.tsv,
or the PROVENANCE never-ran line cites the verdict's sha). Blast: §3.5, §3.6.

### MEAS-8 — §2.3 quotes walk-set's floor as walk's, at a precision below floor_drill's own Monte Carlo resolution
CONFIRMED (`meas/run/floor_drill.out`). "walk and walk-set 4.25 wb at g 256 and 15.75 wb at g 1024 for s 0.5 %
... 8.25 / 31.25 at s 1 %": walk-set (identical model, another random stream) prints 16.0 and 31.75. h90 is the
first 0.25-wb grid step with >= 90 % of N = 1,000 runs priced (binomial s.e. ~1 % at 0.9, so the first-crossing is
biased low and uncertain by several steps). Severity: doc. Effort: text (quote one figure per pair, or round to the
drill's resolution).

### MEAS-9 — "a two-phase-class walk is caught HERE" (the bimodal test, 67 %) is the half gate's catch
CONFIRMED (`meas/bimodal_split.py`, place_drill's classes model, 4,000 runs). Classes 0/2 %: half gate 64.2 %,
bimodal 19.2 %, either 67.3 %, bimodal-ONLY 3.0 %; at 0/1.5 % bimodal 3.6 % (only 0.8 % not already gated). The
bimodal threshold (gap > gate/2 = the unit's half gate) is nearly subsumed by the half gate it sits beside.
Severity: doc (and a design note: the test's independent contribution is ~3 %). Effort: text.

### MEAS-10 — a delta row's noise_e6 is in a different regime from a slope row's, unstated
CONFIRMED (text + drill.py (2)). For slope rows, the per-launch spread is the placement/launch distribution of the
cost itself (§6's "NEW draw"). For delta rows it is dominated by the ESTIMATOR's error (two 1 MiB calls' noise / E,
plus the base's own placement): drill.py's end-to-end walk hit row has noise 3.27 wb on 19.49 (16.8 %) from 0.2 %
cell noise. Rows sharing a base (J3 base.walk serves four) share that error per launch, and every row shares W and
its job's ctl, while §6's band sums cards in quadrature as independent. Errs wide (wins forgone, the safe side);
§6's z derivation (one card, its own launch distribution) does not describe it. Severity: doc/design (low). Effort:
a sentence in §3.4 step 7 / §6.

### MEAS-11 — z 3.0's tolerance holds at f 0 only for NORMAL launches (the regime is unstated)
CONFIRMED. Re-sweep finer (`meas/z_fine.py`, 10^6 draws): z 2.95 2.373 %, **3.00 2.247 % +- 0.015 %**, 3.05 2.135 %:
the 2.3 % tolerance (Phi(-2) = 2.275 %) is met with a z margin of ~0.02-0.05 (HELD as stated). Under heavier
tails (`meas/z_tails.py`, 300,000, f 0): t10 2.60 %, t5 3.07 % > tolerance; two-class 1.92 %. §6 "z 3.0 holds the
tolerance at every f" is a normal-launch statement. Severity: doc (f near 1 in practice errs wide; trigger exists).

### MEAS-12 — §3.2 "from tau ~ 1 % ... rev 1.1 reports that every time": place_drill prints 52 % (s 0.5 %) and 42 % (s 0.25 %)
CONFIRMED (`meas/run/place_drill.out`; finer `meas/seeded_place.out`: tau 0.7 19 %, 0.8 30 %, 0.9 43 %, 1.0 53 %,
1.5 86 %, 2.0 97 %). "Every time" holds from tau ~ 1.5-2 %. Severity: doc.

### MEAS-13 — "every group boundary re-checks load" is undefined under interleaved rounds, and box time counts no boundary waits
SUSPECTED. §3.3: a launch runs EVERY group of the job "in rotated, interleaved rounds", yet "every group boundary
re-checks load ... WAITS (bounded) until quiet; a group is timed only after its check passes". With groups
interleaved per round there is no single boundary per group; if a boundary is per (group, round) that is up to
groups x 7 x 7 checks per job, and if each check is the 650 gate's >= 55 s two samples (the `--ready` gate) §3.7's
35 minutes (6 min for six job STARTS only) does not hold. Confirm by: the text naming what a boundary is under
interleaving and the check's cost. Severity: doc (box time, quiet-implied-by-presence in CELLS-2). Effort: text.

## PROBED-AND-HELD

- Text-vs-script: 6 functions x 200,000 fuzz cases, 0 divergences (`meas/cmp_drill.out`); every §3.5 table figure
  reproduced by my own implementation before reading drill.py.
- Every figure quoted from the six drills reproduces (see Recomputed figures): 40+ figures, 0 mismatches except
  MEAS-8's walk-set attribution.
- K_TRIM: 1/E[trsd^2] = 1.7238 at 10^6 draws (design 1.723 from 200,000): DERIVED as stated (`meas/z_fine.out`).
- Normalisers vs a never-picked candidate: v_l reads only the row's own cells, its base (same job's J<j>.base,
  same launch) and its job's ctl; W reads only the unit; trim per row; drift per job from ctl. No arithmetic path
  from an added arm to another row (MEAS-3 is the group verdict, not a normaliser).
- The control's placement: ctl is one fixed executable and every row is divided by W (the unit's median over 7
  drawn placements in the same ctl units), so ctl's own placement cancels in every anchored value (step 4); the
  control shares the walk's TEXT with the unit by design (a launch-state probe, not an independent cost control);
  the drift's blindness to non-proportional change is stated (§3.5), r5 DRIFT's text fix holds apart from MEAS-4.
- The unit's value = 10^6 exactly (rhafz monotone, L odd): checked in drill.py (2) and by the formula.
- Bimodal k range 2..5 = clusters >= 2 at both ends (4 gaps checked); "one outlier" unit at index 6 passes.
- Gate edges: cost gate `noise x 10^6 <= gate x value` inclusive (2001/60000 refused, 604 passes); unit half gate
  integer 15000; NULL `med(D) > aa_D` strict; drift strict `>`; tie trim "later launch" identical in mine/drill.
- Box time: 0.95 s per point-launch is grid2's regime (7 rounds per launch, r17b_prime.md:2059-2063 @ 6f1b40f75),
  same rounds as kit-grid@3; 195 x 7 x 0.95 s = 21.6 min; 1,008 cells = (195 - 51) x 7.
- r5 measurement findings claimed fixed, checked in the text: CELLS-1 (a)-(e) FIXED (events column, round `med`,
  J<j>.<name>, one base rule, launch identity); CELLS-2 FIXED (domain named; J1 home named; MEAS-7 is a new gap);
  meas-5 (f) exact E per subject, (g) per-launch fraction then med, (h) several widths named: FIXED; Z (meas-4)
  FIXED (aa in the drill, ONE event, figures reproduce); FLOOR (meas-6) FIXED (paired floor; per-key table; see
  MEAS-5/8); TWIN (meas-1) FIXED (linked addresses, 3 of 4 phases, `.text` equality); J3/meas-8 counts FIXED (30);
  DRIFT (meas-7) FIXED in text except MEAS-4; PLACE (meas-2/3) FIXED within a run, NOT across re-runs (MEAS-1);
  GOAL2 FIXED for NULL rows, NOT for refusals under reading B (MEAS-2); J1-WIN FIXED (J2p, --ready 77) but see MEAS-7.
- r5 Rulings' process change (3) (linked addresses, not object bytes): applied in §3.2.
- z re-sweep: 2.95/3.00/3.05 at 10^6 draws, the tolerance crossing at z ~ 2.98 (`meas/z_fine.out`).
- J1 false (b): 0 % over margin 1-3 x k 3-6, tau 0/1, 3,000 trials each (`meas/j1_sweep.out`).

## Text vs script diff

- Method: `meas/mine.py` written from §3.4-§3.5 text only (rhafz per measure_sets.md:509 at 6f1b40f75), then
  `meas/cmp_drill.py` fuzzes it against drill.py's functions: 200,000 random cases each (scales 10..10^8, forced
  ties, heavy ties) for row (value, aa, noise), sp2/trim, bimodal, NULL rule, drift, rhafz. **0 divergences in
  every function** (`meas/cmp_drill.out`). My constructed-table run (`meas/mine_table.out`) reproduces every §3.5
  table figure (92, 92, 2034 / 3.39 %, 604, 2001, null/null/priced, 20000 vs 49626 = 2.0 % < 4.96 %).
- Divergences (text says, script does not):
  1. drill.py implements NO outcome table (FULL/PARTIAL/REFUSED/HELD, Goal 2's floor, "a group passes"); §R1.1
     and §3.5 say drill.py drills "§3.5's constructed outcomes", but the verdict table is not drilled (see MEAS-2).
  2. Step 2 "E one value over all of a's and a#b's cells, else the set is refused": drill `events()` checks a and
     a#b separately, never their equality (no refusal path). Step 2 "B's cells are in J<j>.base, same launch":
     `c()` matches on job prefix + arm only, never the group. Both are recompute refusal paths with no drill.
  3. The control's estimator: text says `slope X1,X2,X3` "(find_byte, and the control)" but `ctl` has no card,
     so the recompute (which "reads ONLY the set file: header, cards, rows, cells") has no `lengths` field to
     parse for it; drill.py hard-codes LEN. The text should say the control's slope is over its own cells'
     `length` values (or name the card it borrows). doc.
  4. Drift's `gate_e6/2`: the text does not say WHICH card's gate (drift is per job; J4/J5 hold other cards);
     drill.py uses a constant 30000. Equal today (all four cards 30000), so answer-free; doc.
  5. j1_drill.py models r_l and aa as ABSOLUTE differences in unit-normal noise; §3.6's rule is RELATIVE
     (rhafz(... x 10^6, t_l(128))). Equivalent to first order at small relative noise; not an integer drill of
     the text. doc.
  6. floor_drill.py models per-call noise as normal only; §3.4 trims one launch for the spread, but the NULL
     rule's "every D_l > 0" has no trim (see MEAS-5): the drill never meets the case the trim exists for.

## Recomputed figures

All six drills re-run (`python3 -I`, outputs `meas/run/*.out`); every quoted figure checked against them:
- drill.py: §3.5 table rows clean 92, outlier 92 ("launch 6" is 1-based: index 5; at index 6 noise would be 111),
  bimodal 2034 (3.39 %), A/A 604 / 2001, null/null/priced (med 40.0 us, aa_D 4.0 us), drift none 264 (0.03 %),
  tight 29997 (3.0 %), wide 20000 vs 49626 (4.96 %); end-to-end unit 10^6, libc 63298, walk random hit priced,
  147 cells: ALL REPRODUCE.
- place_drill A (§3.2): rev 1 7.65/3.83, 34.08/27.55, 63.35/59.05; rev 1.1 5.70/0.32, 52.25/27.30, 96.95/93.99;
  classes 0/2 % 67.38 %; held 0.3 % (§3.5): REPRODUCE (but see MEAS-1: "held" is computed as r^2, the
  independence the design's seeded placement does not give).
- place_drill B (§3.5 drift power): 0 %; 100/100/93.3/18.9; 50.2/38.1/15.2/1.0: REPRODUCE.
- coverage_drill: rms 0.7618 -> 1.7230; table 6.69/3.85/2.25/1.35, 2.70/1.14/0.47/0.20, 1.68/0.65/0.26/0.10;
  mean noise 0.95/1.21/1.40; stored event 0.005 %: REPRODUCE.
- floor_drill (§2.3): walk 2.25/8.25 (s .25 %), 4.25/15.75 (s .5 %), 8.25/31.25 (s 1 %); pair 0.5/2.0, libc
  0.25/1.0; rev 1 floor 31.64: REPRODUCE for walk. The text's "walk AND walk-set 4.25 / 15.75 ... 8.25 / 31.25"
  is walk's: walk-set (the identical model, another MC stream) prints 16.0 and 31.75 (MEAS-8).
- j1_drill (§3.6): 0 of 20,000; 0/12/81/100 %; fixed 0.03/1.15/4.53 %; launch 0 %; power 9.7 % / 0.1 % (rev 1
  39 % / 19 %): REPRODUCE.
- tree_drill (buildtree): 49 rows / 40 form rows; points 51/21/26/30/37/30 = 195, 21.6 min; 1,008 cells;
  check C 9 of 10 cards, 0 without form first, 65 resolved, 0 of 1 measure_store sets; embed 23,788 B, 305 B/row,
  15.8 KB, 260 KB = 14.5 % of 1,834,467 B, 232 KB vs 24.3 KB: REPRODUCE. 0.95 s per point-launch x 7 x 195 =
  21.6 min reproduces; its regime (grid2's 7 rounds per launch, r17b_prime.md:2059-2063 at 6f1b40f75) matches.
