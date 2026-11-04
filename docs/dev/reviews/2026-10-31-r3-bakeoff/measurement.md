# MEASUREMENT findings: bakeoff (pricing_bakeoff.md @ a7b229f3f)
## Findings
### MEAS-1 The bench's timed loop is the REPEATED regime, not the STREAMED one the design requires
- status: CONFIRMED
- severity: answer
- effort: medium (a bench harness extension, or the grid1 fallback, named as a prerequisite)
- blast radius: every ground-truth cell is timed on a buffer the branch predictor has learned; the oracle is biased toward walk-heavy arms (no-search, the consumer walk), which is exactly the side MN, R2.5's "no search" row and FM-vs-priced comparisons turn on. The verdict could flip on any slot where search vs walk is the choice.
- where: §1 item 1 ("every timed cell is STREAMED"), §5.1, §5.2; pcrec-bench `docs/design/harness_contract.md:146-154`, `docs/methodology.md` "What is timed"
- finding: the design times ground truth on the bench "for independence" and also requires every cell STREAMED (64 distinct 64 KiB buffers, regime_eval §2.4's condition (S)). The bench's driver protocol loops ONE subject `iters` times in-process until that subject's loop is >= 50 ms, then moves to the next subject. A 64 KiB buffer at ~0.19 ns/B (armread §1, c_byte) is ~12 us per call, so each buffer is walked ~4,000 times in a row: that is regime_eval's `rep64k` condition, which regime_eval §2.4 measured as cutting the walk's branch misses from 145-251/KiB (fresh) to 0.4-0.9/KiB (dfa-hat) and 4.7-22 (hex-run prose/code). B5 asks only whether the bench can time on our subjects, not whether it can STREAM them.
- repro: `sed -n 146,154p pcrec-bench/docs/design/harness_contract.md`: "for each subject runs `iters` iterations with a monotonic clock around the loop ... `iters` chosen so one subject's loop is >= 50 ms". methodology.md: "times a loop of repeated calls to the same compiled matcher". Expected (design §5.2): consecutive calls see distinct data (grid1 README item 5's never-resetting cursor). Observed: the same buffer repeated.
- proposed fix: make "a streamed-cursor subject mode in the bench driver" an explicit bench prerequisite (new B-question), or time ground truth on grid1 (which streams) and accept COST-11 (b) as NOTED; either way add a rep-vs-stream control column (regime_eval's P-PRED) on a subsample so the regime is measured, not assumed.

### MEAS-2 The run-length prediction does not follow from the bench's calibration (off by about 64x)
- status: CONFIRMED
- severity: design
- effort: small (re-derive) / medium (if the run really is ~40 h)
- blast radius: the window request (F6, B2), the stage-2 job split and G4's "about 6 quiet hours" are all built on a per-cell cost the harness does not have; the run either does not fit its windows or is quietly reshaped (fewer subjects, i.e. not 64 windows) without the design saying so.
- where: §5.6, §0 item 6, G4, §11
- finding: §5.6 prices a cell (arm, subject set, call shape) at "about 50 ms of timed work per trial, five trials" = 0.25 s. The bench calibrates 50 ms per SUBJECT (per row: pattern, regime, form, subject; gate_shape_v14 §0 vocabulary; methodology "Per-row calibration target ... 50000000"). A LONG cell is 64 subjects (the 64 windows), so 64 x 5 x 50 ms = 16 s, not 0.25 s; a SHORT cell over line buckets is worse (one subject per bucket buffer at least).
- repro: arithmetic. Design: 9,000 cells x 0.25 s = 2,250 s = 37.5 min ("~40 min"). Under the bench's per-subject target: LONG 4,500 cells x 16 s = 72,000 s = 20 h of timed work before SHORT, pre-flights or compiles. (The bench's TRIAL_BUDGET_SECONDS = 20 per pass, gate_shape_v14 line 47-48, also caps a 64-subject pass at 20 s, i.e. ~0.31 s per subject, which still gives 64 x 5 x 0.31 s ~ 100 s per cell.)
- proposed fix: state the bench's per-subject calibration in §5.6 and re-derive; or ask the bench (new B-question) for a per-cell (whole-stream) timed-work target, which MEAS-1's stream mode would naturally give.

### MEAS-3 The arms of one site are separate bench runs, so "paired trial deltas" and "timing groups" have no meaning as written
- status: CONFIRMED
- severity: design
- effort: medium
- blast radius: the per-cell NULL rule (§5.4, "the paired trial deltas disagree in sign"), the cross-fit's trial pairing and the noise rule N (§7.2, "linear within a timing group, quadrature across groups") all assume the arms of a cell share trials in time. If they do not, between-run drift enters every arm difference unmodelled, and N is undefined, so the 2.N test and the UNDERPOWERED floor read numbers with no stated meaning.
- where: §5.1 ("every arm is one testee config"), §5.4, §7.2; pcrec-bench `harness_contract.md` §4 (`run --subbench .. --testee ID`), `gate_shape_v14.md:43` ("trials are interleaved by group")
- finding: the bench interleaves trials by GROUP (pattern, regime, form) WITHIN one testee's run; a run takes one `--testee`. The bake-off makes every arm its own testee config, so the 7-9 arms of a site are 7-9 runs at different times. Trial t of arm A and trial t of arm B are not paired in time; regime_eval's quadrature rule was derived for its own harness, where "the cells inside one group share launches". Nothing in §5 says what a timing group is on the bench, or how arms of one site are ordered/rotated across runs.
- repro: `harness_contract.md` §4: "`python3 -m pcrecbench run --subbench email --testee pcre2-jit [--trials 5]`" (one testee per run); `gate_shape_v14.md:42-44`: "a PASS is one trial's sweep over every subject of one group (harness.py: trials are interleaved by group ...)". Design §5.4 uses "paired trial deltas" and §7.2 "a timing group" without a bench mapping.
- proposed fix: ask the bench (new B-question) for a multi-config interleaved run (all arms of a site inside one pass), or define the timing group as "one site's arms in one rotated block" with the A/A configs spread through the block, and derive N from that.

### MEAS-4 C-PRICE's pooled rank correlation cannot fire: it is dominated by between-site scale, not within-site ranking
- status: CONFIRMED
- severity: answer
- effort: small
- blast radius: the stop "the model cannot rank arms, so no placement of it can be graded" (§6.4, §9.3 row 0) passes on a model with ZERO within-site ranking skill, so rows 3-5 grade placements of a model that picks at chance.
- where: §6.4 C-PRICE, §9.3 row 0, §11 stage 3
- finding: a POOLED Spearman over all timed arms of D ranks a slow VM site's arms above a fast DFA site's arms whatever the model does inside a site; picks depend only on WITHIN-site order.
- repro: `python3 -I measurement/sims/cprice.py` (synthetic; 100 sites, 3-6 arms, within-site true spread 15 %, price noise 15 %). With skill = 0 (price carries no within-site information): pooled Spearman 0.88 / 0.98 / 1.00 at between-site sd 0.5 / 1 / 2, while the model picks the true best on 20-29 of 100 sites (chance). Expected for a working stop: below 0.5 at skill 0.
- proposed fix: gate on the WITHIN-site statistic (mean per-site Spearman, or pick accuracy against a chance baseline computed from each site's arm count), pooled only after per-site centring.

### MEAS-5 C-BLIND cannot see a narrow blind spot, is vacuous without L-KIT, and row 1 leans on it
- status: CONFIRMED
- severity: answer
- effort: small (reach as a probability; restate row 1's condition) to medium (more random draws)
- blast radius: §9.3 row 1 "PRICING DOES NOT PAY" (an early stop that ends the question) reads FM's regret as a usable lower bound because C-BLIND <= 10 %; that bound is unsupported whenever the better options are a small share of the space, or not timed at all.
- where: §3.5 (2 random options per kit site), §8 C-BLIND, §9.3 row 1, §10 item 1 and closing paragraph
- finding: (1) Reach: with 2 uniform draws from up to 204 options, if a share f of options beat every model-chosen one, the per-site detection probability is 1-(1-f)^2: 0.04 at f = 2 % (4 of 204), 0.098 at f = 5 %. The rate stays under the 10 % bar even when the model is blind on EVERY site. (2) Without L-KIT no random kit option can be forced, so C-BLIND's population is empty; §10 says the bake-off still runs row 1 without L-KIT, and an empty rate reads 0 <= 10 % (learnings §3: empty-vs-empty). (3) The rows behind validity-gated prices (§10 item 3) and arms past the census's 64-compile cap are never timed, so no random draw can reach them; FM's regret is a lower bound over a set that excludes exactly the gated choices. (4) The §8 row's planted failure is "none (it is itself the probe)", against §1 item 2's "every control in §8 has a planted failure that must turn it red".
- repro: `python3 -I measurement/sims/repro_blind.py` (arithmetic). Design line 736: "above 10 % stops stage 4 ... none (it is itself the probe); its reach is reported as the number of random arms timed"; line 777 row 1's condition; lines 827-829 (row 1 runs without L-KIT).
- proposed fix: report C-BLIND's reach as a detection probability for a stated f and size the draws to it; make row 1 require a NON-EMPTY C-BLIND population (INCONCLUSIVE otherwise) and exclude, or name, the strata whose alternatives are untimed (§10 item 3, census-truncated sites); give C-BLIND a planted failure (a timed option hidden from the model-chosen set).

### MEAS-6 C7 turns red on honest noise, and its planted failure does not reach it
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: §9.3 row 0 (any §8 control red -> NO VERDICT) fires on a correctly measured population whenever many cells have near-tied top arms, which the design itself predicts (§9.1 item 1, "most sites are near their oracle"; byte-distinct arms that time the same). Conversely the planted failure gives no evidence C7 can go red.
- where: §5.4, §8 row "the oracle is noise" (C7), §9.3 row 0
- finding: (1) C7(b) qualifies a cell when its top two arms "differ by more than the floor", and the floor is ONE A/A pair's difference (half-normal: below its own median half the time). With 5 trials split 3/2, about half of truly TIED cells pass the qualification, and of those ~35 % pick different oracle arms in the two halves, independent of sigma. regime_eval's C7 had 7 rounds split 4/3; this has 5 split 3/2. (2) The planted failure ("time one arm twice under two config ids; the halves must call it NULL") is an A/A check of the per-cell NULL rule; it does not make C7's (a) or (b) red.
- repro: `python3 -I measurement/sims/c7.py` (synthetic, 7 arms, floor = |mean(default) - mean(A/A copy)|): top-two TIED: 49-50 % qualify, 35.4-35.6 % disagree (bar 5 %) at sigma 0.5-2 %; at sigma 1 % and a 1 % gap: 14.3 %; a mixed gap population at sigma 1 %: 5.8 %, at 2 %: 9.4 %. Expected: an honest population passes.
- proposed fix: qualify cells on a pooled noise estimate (the distribution of A/A differences across the group, e.g. its 95th percentile), and derive C7(b)'s bar by simulation from the measured noise, pre-registered; plant a C7 failure that perturbs one half's trials (e.g. a scaled half) so (a) must go red.

### MEAS-7 C-REPRO's "every row within its own noise band" fails on honest noise, and the band does not exist today
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: the stage-1 early stop (§4.5, §11 stage 1: "C-REPRO fails on a card every priced rule reads ... stop") fires on a box whose measuring method is fine, or (with the band absent) passes vacuously; either way no box's set reaches the bake-off on evidence.
- where: §4.3 C-REPRO, §4.5, §8 C-REPRO row, §11 stage 1
- finding: (1) Two independent re-measures of a row differ with sd sqrt(2) x the row's sd. If `noise_e6` is a one-sigma-ish A/A floor, each row agrees with probability ~0.52, so ALL rows agree essentially never; even a 3-sigma band gives P(all 68 rows) ~ 0.10. Two SEPARATE windows also add between-window drift that a within-window A/A floor does not contain. (2) The one existing set has `noise_e6 = -` and `n = -` on all 68 rows, so the band C-REPRO reads does not exist for the kit rows the design calls "already ruled"; nothing in §4 requires the kit half (K7) to write it. (3) The planted failure "a deliberate per-run offset" names no size, so it cannot show the control's threshold (a large offset is red under any rule).
- repro: `python3 -I measurement/sims/repro_blind.py`: band = 1/2/3/4 sigma -> P(every one of 68 rows agrees) = 5e-20 / 9e-6 / 0.096 / 0.73. `awk -F'\t' 'NR>36 && NR<105 && !/^#/ {n++; if($5=="-")d++} END{print n,d}' measure_store/zen4-grid1/1/set.tsv` -> `68 68` (every row's noise_e6 absent).
- proposed fix: a per-row test at a pre-registered family-wise level (e.g. agreement within z x sqrt(2) x sd with z from the row count), a between-window term measured by the two runs themselves, `noise_e6` and `n` REQUIRED in every row the bake-off reads (hard-fail on `-`), and a planted offset sized at the band's edge.

### MEAS-8 The decision table has an unreachable region: a small real difference lands on row 7 for ever
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: a population on which the priced options genuinely differ on a minority of sites (the case the stop-ranking study describes: losses concentrated on LOCATE/NEXT/PRESENCE witnesses) can never reach a verdict; row 7 asks for J4, and more sites do not change either test.
- where: §7.2 power floor, §9.2 delta, §9.3 rows 4, 5, 7
- finding: row 4 needs timing-equivalence on >= 95 % of H sites; row 5 needs a POPULATION-mean advantage >= delta = 2 pp. Two options that differ by 10 % on 9 % of sites fail both: row 4 (91 % equivalent) and row 5 (mean 0.9 pp). Row 7 says "otherwise (UNDERPOWERED comparisons): INCONCLUSIVE, more sites (J4)", but with 220 sites the comparison is no longer underpowered (20 differing sites >= 15) and still fails rows 4 and 5, because both are ratios that more sites do not move. Also, delta on the population mean means a pair must differ on k sites with k x (net gain) >= 2.2 on H-open = 110: at the 15-site floor the net gain must be >= 14.7 % per differing site; and at a true advantage exactly delta the point test passes ~50 % of the time.
- repro: arithmetic as above; `python3 -I measurement/sims/row5.py` (synthetic, n = 110): true mean diff 1.5 pp -> P(row 5's point+CI tests) = 2 %; 2.0 pp -> 50-60 %; 1.8 pp -> 30 %.
- proposed fix: add the missing row ("options differ on a stated share of sites but below delta in aggregate -> NUMBERS TIE ON AGGREGATE, report the stratum") or state delta per differing site; make row 7 fire only on UNDERPOWERED, with the J4 size derived from the power calculation.

### MEAS-9 Option (a) is J, yet it is a row-5 candidate: row 5 can then only crown model error, and (a) can win "on numbers"
- status: CONFIRMED
- severity: answer
- effort: small
- blast radius: a "THAT OPTION WINS ON NUMBERS" verdict for any option other than (a) requires beating the joint model optimum by delta, which happens only where model error favours that option's deviations (a noise/model artifact crowned as a placement win); and when the others lose to J by delta, (a) "wins on numbers" although §2 and F4 say its case is architectural, not numeric.
- where: §2 ("(a) is J in this simulation"), §9.3 preamble ("the CANDIDATE placements: A1, HY, Dx, MN, KF and (a)"), rows 3 and 5
- finding: (a) has placement loss 0 by construction and is still in "every other's" set of row 5. Row 3's guard also uses "the LARGEST paired placement-loss difference among the options", which (a) and MN dominate (§9.1 item 4 predicts MN captures only half of J's gain), so row 3 passes while the A1/HY/Dx differences it should protect sit far below model error.
- repro: design lines 172-174 ("(a) is J ... its case is architectural, not numeric") vs line 767 ("The options in rows 3-6 are ... A1, HY, Dx, MN, KF and (a)") and line 781 (row 5: "lower than every other's by at least delta").
- proposed fix: take (a)/J out of the row-5 candidate set (report it as the ceiling), and make row 3 per comparison: a pair is resolvable only if its own paired difference exceeds model error / 3 (or the bound the calibration readout gives).

### MEAS-10 The text-class strata, the regime the design says decides, never reach the 15-site floor
- status: CONFIRMED
- severity: design
- effort: small (state it) to medium (size J3 per class)
- blast radius: §7.3's guard ("the winning rule's paired difference has the same sign in every stratum with at least 15 sites") is silently vacuous for most text classes, so a placement that wins on prose/logs and loses on binary/structured (where SRS §5.1 item 3 says the prior hides dense hex) is crowned.
- where: §1 item 1, §3.2 (size), §5.2, §7.3, §9.3 row 5
- finding: J1's class balance (the list J3 copies, "exactly as [REGIME-CORPUS] wrote J1") is 22-28 questions per class over seven classes. H takes 70 % of S-real and H-open 2/3 of H, so even if EVERY question qualified, each class gives 10-13 H-open sites; only prose and logs can pass 15, and only through S-bench sites (timed on prose, logs and one salted pool). The MISS density bin (where search wins by construction, §5.2) is 9 of 171 J1 questions with a full-file density, ~5 %, i.e. ~6 H-open sites. "Density bin" and "call shape" are also CELL attributes in a SITE-counted stratum, so their site counts are undefined.
- repro: `awk -F'\t' 'NR>1{c[$2]++} END{for(k in c) print k,c[k],c[k]*0.7*2/3}' docs/dev/lanes/rwquest/questions.tsv` -> structured 24 (11), logs 28 (13), markup 24 (11), nonenglish 25 (12), code 27 (13), binary 22 (10), prose 27 (13). `python3 -I measurement/sims/dens.py ...` -> MISS 9, SPARSE 88, DENSE 74, n/a 5.
- proposed fix: size J3 per class from the power floor (>= 15 differing sites per class, so many more than 25 questions per class), or pre-register the classes that will be ungated and make row 5 name them (as §10 item 3 does for the partial strata); define the site count of a cell-level stratum.

### MEAS-11 The stage-0 floor and the robustness clause do not follow from the power floors
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: the bake-off proceeds to timing on a population that cannot meet its own 15-site floor, and row 5's robustness clause passes BECAUSE it is underpowered.
- where: §11 stage 0 ("fewer than 60 H sites qualify ... stop"), §3.2, §7.2, §7.4 (Zen 1 subset, 60 H sites), §9.3 row 5
- finding: (1) the verdict reads on H-OPEN, 2/3 of H: at the 60-site floor that is 40 sites, and a pair must then differ on 15 of 40 (37.5 %) to be powered, and by >= 5.3 % net per differing site to reach delta. (2) Row 5's robustness clause is a NON-INFERIORITY test ("degrades no more than delta worse than the runner-up under ... cross-box"): a low-powered non-inferiority test passes, so the 60-site Zen 1 subset (where few pairs differ on 15 sites) reads "robust" by default. §7.2's UNDERPOWERED rule is written for superiority comparisons and is not applied to this clause.
- repro: arithmetic: 60 x 2/3 = 40; 15/40 = 37.5 %; 0.02 x 40 / 15 = 5.3 %. Design line 781: "it degrades no more than delta worse than the runner-up under §7.4's sigma = 0.3 and cross-box readings" with no power condition.
- proposed fix: state the stage-0 floor in H-open sites derived from §7.2 (and from MEAS-8's arithmetic); apply UNDERPOWERED to the robustness clause (an underpowered robustness reading makes row 5 INCONCLUSIVE, never PASS).

### MEAS-12 The cards' regime is not the regime the rules are applied in (rates, density, call mode, pattern)
- status: CONFIRMED
- severity: design
- effort: medium
- blast radius: MODEL ERROR is inflated in exactly the search-vs-no-search and per-entry terms every priced rule reads, which pushes the bake-off to rows 2-3 ("model cannot beat first-match", "unresolvable") for a measurement-design reason, not a model reason; and MN's single priced row (C-BYTE x bytes vs entries x C-ENTRY) is decided on extrapolated values.
- where: §4.2 card table (C-BYTE, C-ENTRY, C-MATCH), §6.2 A1/MN, §6.4 C-PRICE
- finding: (1) C-ENTRY plants candidate rates 0, 1/256, 1/32 per byte; real start sets on the corpus run 3-8x above the top point (digits 0.239 of apache_access.log, space 0.151 and `e` 0.093 of a prose book), so the per-entry term at the densities where "no search" wins is an extrapolation. (2) armread (the method the card cites) found the analogous per-match cost NOT constant (p1 dfa 7.7 -> 3.9 -> 3.2 ns at m = 64 -> 1024 -> 8192 per 64 KiB) and "C_call is not transferable between modes" (first vs find-all), and the VM's per-byte cost non-linear in length; a single slope per kind over three rates and "slope over two subject lengths" cannot see either, and the design has no functional-form check (learnings §1, "three sizes"). (3) Each card is keyed only by consumer KIND; the pattern(s) a card is measured on are not named, while the consumer's per-byte and per-entry costs depend on the pattern's automaton (DFA width, VM program).
- repro: `python3 -I measurement/sims/dens.py ...` (byte shares above); `docs/dev/lanes/armread_report.md` §2 readings ("C_match is not a constant here", "C_call is not transferable between modes") and §1 ("VM: C_call is not separable ... The VM is not linear"); design §4.2 lines 375-378.
- proposed fix: plant rates spanning the H population's measured entry rates (up to ~0.25/B), at least three lengths and three rates with a residual check against the linear form, cards per call shape, and name the card patterns (a declared small set per kind) with the calibration readout (R5.3) reporting per-pattern card error.

### MEAS-13 The 20 % relative card floor is ill-defined for near-zero and signed quantities
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: the stage-1 early stop ("a card's A/A floor exceeds 20 % of its value") fires on cards whose value is small or a difference, which are often the cards that matter least, and ends the bake-off.
- where: §4.5 "Stage 1 early stop", §9.3 preamble (the 20 % is CHOSEN)
- finding: several card quantities are differences or near zero: today's set holds signed rows (`kit.delta.V1.WALK.DFA_SCAN.n48 = -23784355` e6, `n63 = -29598309`), and armread's VM C_match is "~0, within the C_call(e0) uncertainty" (p2 vm -0.32 ns). A relative floor on such a row is undefined or always exceeded, regardless of measuring quality.
- repro: `grep 'kit.delta' measure_store/zen4-grid1/1/set.tsv` (negative values); armread_report.md §2 table (p2 vm C_match -0.32).
- proposed fix: state the floor against the row's CONTRIBUTION to a price at the H population's rates (absolute in walk-cost units), not against the row's own value.

### MEAS-14 The coverage top-up is not sized: perturbed constants send each rule to many untimed kit options
- status: SUSPECTED
- severity: design
- effort: small (restrict robustness picks to timed arms) / medium (size and budget the top-up)
- blast radius: either the "<= 1 h" top-up window is too small, or rules cross the 2 % UNCOVERED line and read INCOMPLETE (never PASS) on the robustness readings row 5 requires, so no option can win.
- where: §3.5 "Coverage top-up", §7.4 (perturbed: 3 sigmas x 200 draws + 2 x families; cross-box; stale; re-measured), §11 stage 3b
- finding: "any arm a rule picks under any constant set (§6.3, §7.4) that was not timed is timed in ONE top-up window". At a kit site with tens to 204 options, one rule's argmin moves across many options as the constants are perturbed; nine rules plus J's top 3 make the union per site larger than the 3-6 footprint bests + 2 random + default timed in stage 2.
- repro: `python3 -I measurement/sims/topup.py` (synthetic option geometry: price = sum of 5 component x constant): ONE rule visits a median of 5 / 7 / 9 distinct options (p90 8 / 11 / 14) at K = 20 / 60 / 204. What would confirm: the stage-0 dump's real option components (L-KIT) run through the same count.
- proposed fix: define robustness picks over the TIMED arms only (the rule's best timed option, flagged when its unrestricted pick is untimed and counted), or pre-register a top-up budget derived from a stage-0 dry count on the real dumps.

### MEAS-15 The subject design cannot give 64 distinct windows per cell, or D/H disjointness, on most pools
- status: CONFIRMED
- severity: design
- effort: medium
- blast radius: the text classes with small pools (code except c/java/python, two log sources, every non-English script) are timed on fewer windows than stated or on windows shared between D (the K-fit and rule-debug set) and H, so the "held-out" reading of K-fit and the disjointness claim fail on those classes, or those sites drop out of H uncounted.
- where: §5.2 ("64 distinct 64 KiB buffers (4 MiB) drawn from the site's class pool ... disjoint from every card subject and fit buffer"), §3.2 item 2 ("a contaminated buffer is redrawn")
- finding: regime_eval §2.4's drawing rule (which §5.2 adopts) draws windows per POOL, not per site, with M = min(64, U / 64 KiB) and a 16-window floor; so every D and H site of a pool gets the SAME windows, and a pool below ~4.6 MiB cannot give 64. Pools (sizes): apache_access 2.3 MB, linux_syslog 2.2 MB, rust 1.6 MB, javascript 2.6 MB, go 0.4 MB, prose books 0.4-3.2 MB each (prose pools all twelve books, fine), non-English files 0.1-1.0 MB. A disjoint D/H pair of 16-window sets needs >= 2 MiB plus the 1/8 reserve; rust and go cannot, and "redrawn" has nowhere to draw from.
- repro: `ls -l worktrees/.corpus/{code,logs,nonenglish}` (sizes above); regime_eval.md §2.4 rule 3 (`M = min(64, floor(U / 64 KiB))`, windows per pool, `h(pool, W, j)`) and rule 4 (16-window floor).
- proposed fix: state M per pool, draw D's and H's windows from disjoint strata of the pool (or accept sharing and say K-fit's H reading is not subject-held-out), and count short-pool sites as regime_eval does (`short-pool`, GATE-EXCLUDED, listed).

### MEAS-16 P-SUBJ reads its rates from the very subjects it is scored on
- status: CONFIRMED
- severity: doc
- effort: small
- blast radius: the "rate error" reading (§7.4, P-PRIOR against P-SUBJ) is an in-sample upper bound presented as "the subject's own measured rates", and it contradicts §3.2 item 2's disjointness of H subjects from analysis exemplars.
- where: §6.1 table rows "rates" ("P-SUBJ: the cell's measured rates via pcrec-analyze") and "fractions" ("counted on the site's subjects (§5.2)"); §3.2 item 2
- finding: regime_eval's E exemplar reserve exists precisely so the analysis input is disjoint from the timed windows; here P-SUBJ's analysis input IS the timed windows.
- repro: design lines 573 and 578 vs lines 250-252 ("every H subject buffer is checked ... against ... every analysis exemplar").
- proposed fix: take P-SUBJ's rates from the pool's E reserve (regime_eval §2.4 rule 2), or label P-SUBJ IN-SAMPLE everywhere it is printed.

### MEAS-17 Cells the bench does not rank (inconclusive-spread, re-measured) are an uncounted population, and the bench's tolerance is median-based while the cross-fit is not
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: arms or sites whose record is `inconclusive-spread` drop out (or are silently re-measured once) without a count, and the dropping is not random (noisier, slower arms); meanwhile one slow trial, which the bench accepts as "the box's ordinary behaviour", moves a 2-trial cross-fit half by up to its full size.
- where: §5.1, §5.4, §5.5 (counts only answer failures and give-ups), §12 B3
- finding: (1) a bench record is `inconclusive-spread` (UNRANKED) if ANY group disagrees, and "a window script re-measures such a cell once"; §5 says nothing of how such a record's cells enter the bake-off or are counted. (2) The trial-agreement rule tolerates one trial up to 1.5x over the median ("one slow trial of five is a tolerated perturbation (the median is untouched)"), because the bench reports MEDIANS; the bake-off reads means of 3-trial and 2-trial halves, where a 1.4x trial shifts the 2-trial half by 20 %. The store shows 387 of 62,923 rows with a trial above 1.5x and 724 above 1.3x (gate_shape_v14 §3.2 table), i.e. ~1 % of rows, so ~90 of the ~9,000 cells carry such a trial.
- repro: gate_shape_v14.md §3.4 ("An inconclusive-spread record is UNRANKED"), harness_contract.md §4 step 5 ("a window script re-measures such a cell once"), gate_shape_v14.md §3.2 table (k = 1.30: 724 rows >= 1 slow; k = 1.50: 387).
- proposed fix: count and list spread/re-measured cells per arm like §5.5's exclusions, pre-register what they do (excluded with the site, or re-timed), and use a robust half estimator (median of the half, or exclude a trial the bench flags slow) in §5.4.

### MEAS-18 C-ENUM depends on an "optional" lever and counts only the DEFAULT path's rows
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: either row 0 ("any control in §8 is red") can never be satisfied when L-VALID is not built, or C-ENUM is skipped silently; and when it runs, valid rows that exist only on a non-default path (after a deny moves the upstream slot) are an uncounted population.
- where: §3.4 L-VALID ("optional ... Not needed for the bake-off's correctness"), §8 C-ENUM, §9.3 row 0
- finding: L-VALID "evaluates EVERY row of every slot on the default path"; the census walk reaches non-default paths by denies, and rows valid only there are invisible to the dump, so C-ENUM's "every valid row unreached is listed and counted" covers one path per site.
- repro: design line 307 ("L-VALID, the valid-row dump (pcrec, trace build only, optional)"), lines 309-312 ("on the default path ... lets the census say how many valid rows the walk did NOT reach, which is the census's own completeness control (§8 C-ENUM)"), line 776 (row 0).
- proposed fix: make L-VALID required if C-ENUM is a §8 control, and run the dump on every census arm (not only the default), counting rows valid on some arm and reached on none.

### MEAS-19 K-fit cannot separate "constant error" from "missing term", and it is fitted on a witness-enriched set
- status: SUSPECTED
- severity: design
- effort: small (reword the reading) / medium (a real test)
- blast radius: §6.3's diagnostic ("if K-fit closes most of J's gap on H, the cards are wrong; if it does not, a term is missing", mapped to PR R6.1 (a) vs (b)) can send the follow-up work to re-measuring cards when a term is missing, or the reverse.
- where: §6.3, §3.2 (D = all S-witness + stratified S-corpus + 30 % S-real)
- finding: a missing term that scales with a carded quantity (a per-entry overhead the card's regime does not include, MEAS-12) is absorbed EXACTLY by a multiplicative correction on that card, so "K-fit closes the gap" does not imply "the card is wrong". And D is enriched with the motivating witnesses (extreme by selection) and test-shaped `.rxt` patterns, so the fitted multipliers transfer to H's distribution only by assumption.
- repro: by construction (a term c x entries is indistinguishable from a change of C-ENTRY by c); what would confirm: a planted missing term in a synthetic replay, fitted by K-fit, reading "constant error".
- proposed fix: state K-fit's reading as "consistent with constant error OR a term proportional to a carded quantity", and fit on the S-real third of D only (or report both fits).

### MEAS-20 Smaller measurement wording defects
- status: CONFIRMED
- severity: doc
- effort: small
- blast radius: confusion at build time; none on the verdict if read charitably.
- where: §3.5, §5.1, G4/§11/F6, §3.1, §8 C-SCORE
- finding: (1) §3.5 dedupes arms whose emitted C is byte-identical, but §5.1's A/A configs are "the default compile under two config ids", byte-identical by definition; the dedupe must exempt them. (2) G4/F6 say "2 on the Mac", but §11 stage 1 is "two quiet windows per box (~1 h each on Zen 4, ~1-2 h on Zen 1 and the Mac)" = 2-4 h; Zen 4's "about 6" vs the table's 2 + (1-2) + (<= 1) = 4-5 h. (3) §3.1 cites `tests/codegen/run_form_census.sh:307-316` for "290+ at offset-set"; the offset-set floor is at line 323. (4) C-SCORE's "ORACLE rule must score 0 regret exactly" holds only if that rule picks per CELL (with the oracle's own half assignment); every rule picks per SITE (§6.1), so a per-site oracle rule scores > 0 wherever the best arm varies across a site's cells.
- repro: (3) `grep -n offset-set worktrees/crit-bakeoff/tests/codegen/run_form_census.sh` -> `323:floor_check "D:RX_DFA_PREFILTER=offset-set" 290`. (1), (2), (4): design lines 332-334 vs 503-505; 94 vs 838-841; 730 vs 584-585.
- proposed fix: exempt A/A configs from dedupe; restate the hour totals from the table; fix the cite; define the ORACLE control rule as per-cell.

## PROBED-AND-HELD
- C-LEVER's premise today: 14 patterns compiled by both prebuilt compilers (`build/pcrec` vs `build-trace/pcrec`, same output name): 14 of 14 `.c` and `.h` byte-identical (one more pattern refused on both with "requires module 'assertions'").
- §5.6's own arithmetic under its own assumption: 250 x 9 x 2 x 2 = 9,000 cells; 9,000 x 0.25 s = 37.5 min (states "~40 min"); 250 x 9 = 2,250 arms (§5.1 "about 2,200"): 3 of 3 consistent (the assumption itself fails, MEAS-2).
- §3.2 sizes: H-open ~110 + H-sealed ~55 = 165, inside "150-200", and 1/3 sealed: consistent (1 check).
- The per-cell NULL rule (§5.4, gridread's): synthetic, sigma 1-2 %: P(NULL | true 0) = 0.95, P(NULL | 10 %) = 0.00, P(NULL | 5 %) = 0.00-0.20: conservative and sound (10 configurations, `sims/nullcell.py`).
- The cross-fit split itself ({1,3,5} vs {2,4}) removes the minimum-over-arms bias as regime_eval §4.3 describes; the raw-vs-cross-fit bias print is kept (1 check; its small-half fragility is MEAS-6/MEAS-17).
- The perturbation set (§7.4: sigma in {0.1, 0.3, 0.7}, 200 draws, seeded; families x0.5/x2) and its "a rule that reads fewer constants is immune" caveat: stated correctly (1 check).
- The SIMD-off verdict layer against PR R4.7/R5.2(c) ("both SIMD layers"): the design declares it a non-goal with a reported SIMD-on reading (D147); a scope choice, not a measurement defect (1 check).
- Code cites the measurement gates rest on: `emit_dfa.c:7872-7876` (proper-subset "UNMEASURED DEFAULT"), `:8020-8026` (`|S| < 256` "UNMEASURED DEFAULT"), `:10087` (`ppm x reseed_gap > 1000000`), `run_form_census.sh` memchr 750 floor (line 315): 4 of 4 match.
- The bench facts the design leans on: five trials, pinned core, quiet pre-flight with per-core occupancy, libpcre2 10.46 expectations, give-ups/wrong answers excluded and counted (methodology.md): 5 of 5 as stated.
- Density bins are populated on J1 (MISS 9, SPARSE 88, DENSE 74 of 171 with a density): all three bins non-empty (the MISS bin's size is MEAS-10).
- The noise-rule allowance 2.N and the site bootstrap answer different questions (measurement vs sampling) and both are required: sound in principle (1 check; its bench mapping is MEAS-3).
