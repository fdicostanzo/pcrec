# FIX findings: bakeoff2 (pricing_bakeoff.md rev 1 @ deebb4dd8)

Lens: fix-induced. For each §14 fix: does it hold, what did it add, and does the addition close
a cycle, add a check that fires on correct data (or never fires), an unreachable/shadowed row, or
a term used in two senses. Code at main `a3cc4de82`. Scripts and probes:
`fixinduced/py/` (`vd.py` = a copy of the design's `verdict_drill.py`; `probe1-3.py` mine) and
`fixinduced/c/` (7 single compiles, `gnutimeout 30 nice`). Nothing timed, no make.

## Findings

### FIX-1 The H-frame consumes H-sealed: the sealed reserve is read at the first reading
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: the one-revision held-out mechanism (COST-9's saving, B18) is void exactly when
  it is needed. A rule revised after the first reading gets "held-out" sites whose pair results
  already shaped the revision.
- where: §3.2 (H-sealed, H-frame), §7.2, §11 stage 3b; B4 (frame) against B18/COST-9 (sealing)
- finding: H = 70 % of S-real plus S-bench's deployed rows. H-core is 2/3 of H and H-sealed is
  the other 1/3. "H-frame: H-core plus every further H site of J3" therefore means H-core plus
  H-sealed's S-real sites (until J3b exists, nothing else is "further"). The frame's disagreeing
  sites are timed at 3b and every pair test reads them (§7.2: "the pair tests of §7.2 read the
  frame"). H-sealed is supposed to be "NOT TIMED unless opened ... read ALONE as that revision's
  held-out set". The pair tests T1 is built on would already have read it. §0's "frame of about
  320 H sites" also needs H-sealed plus about 130 J3b sites, since H totals about 193.
- repro: text. §3.2 lines 326-335 (H-core 2/3 of H, H-sealed 1/3, frame = H-core + further H
  sites of J3), §3.2 size paragraph (H ≈ 193, H-core ≈ 130, H-sealed ≈ 65), §7.2 "read the frame".
- proposed fix: build the frame from H-core plus J3b only (H-sealed is excluded by name). Or drop
  H-sealed and say a revision needs a fresh J3c. In either case §0's 320 is J3b's size.

### FIX-2 "Paired difference" (normalised by t_FM) and "regret" (normalised by the cell oracle) put δ and "mean" in two senses, and can flip a pair's sign
- status: CONFIRMED
- severity: answer
- effort: medium
- blast radius: SUPERIOR/EQUIV, and so the top group G and every T1 row from 2 on, are read on a
  metric that discounts each site by FM's slowness there. Row 1, the worst-case guard, §9.2's
  justification of δ and "G is never empty (the lowest mean cannot be beaten)" are on the regret
  scale. A pair can be ordered one way in regret and the other way in the tests.
- where: §0 Words (paired difference), §7.1, §7.2, §9.2, §9.3 T1 preamble; B4 (the frame
  introduced it: frame sites time no cell oracle, so the oracle cannot be the denominator)
- finding: d = mean over cells of (t_X − t_Y)/t_FM. Regret is t/t_oracle − 1. On a site where FM
  is k times the oracle, d is the regret difference divided by about k. The sites FM loses worst
  on (SRS's 1.6x-18x witnesses, §9.1 item 1) are exactly where placements differ, and they are
  discounted by up to 18x. δ = "2 points of paired difference" (§9.2) is justified against PR O1's
  5 % of REGRET. The drill (§9.5) builds d = r_X − r_Y from regrets (`Pair.__init__`), so it
  never exercises the metric the tables are defined on.
- repro: `python3 -I fixinduced/py/probe1.py fixinduced/py`. Two sites, one cell each, times over
  the oracle: FM = (10, 1), X = (1, 1.3), Y = (2, 1). Mean regret: X 0.150, Y 0.500 (X better by
  35 points). Paired d(X, Y) = +0.100 (X SLOWER by 10 points). Observed: sign flip. Expected: one
  ordering.
- proposed fix: state one scale. Either time the cell oracle arm (or FM, then rescale by the
  stage-2 FM/oracle ratio) on frame sites and use regret differences, or justify the FM scale and
  restate δ, row 1 and the worst-case guard on it. Make the drill read the same d.

### FIX-3 The frame added a second site set, but K-fit (row 3), robustness (rows 4/5, 7) and strata never say which set they read; both readings break
- status: CONFIRMED (text); consequence simulated
- severity: answer
- effort: medium
- blast radius: row 3 "UNRESOLVABLE AT THIS MODEL" can fire on sample size alone. Or, if read on
  the frame, a rule goes INCOMPLETE because the frame times only K-card picks.
- where: §3.2 H-frame ("the pair tests ... read the frame; nothing else does"), §3.5 top-up,
  §7.3, §7.4, §9.3 rows 3-5, 7; B4, B17
- finding: G under K-card is built from the pair tests, which read the frame (n ≈ 320). Row 3
  needs G under K-fit, and row 4 needs G (and the non-inferiority bound) under σ = 0.3 and
  cross-box. §3.2 says nothing but the pair tests reads the frame, so these must read H-core
  (n ≈ 130): a smaller sample, which alone can take X out of sole membership. If they read the
  frame instead, the top-up (§3.5) times untimed K-fit/σ/cross-box picks but never says it covers
  frame sites. 3b times "the picks of the frozen rules" (K-card) only. The frame's K-fit picks are
  then UNCOVERED and the 2 % rule drops candidates. Strata (§7.3) and C-BLIND do not name a set
  either. The same goes for J: it is "the argmin over every timed pair", so is that before or
  after the top-up?
- repro: `python3 -I fixinduced/py/probe2.py fixinduced/py`, using the design's own `Pair` and
  `top_group`. Dx is better on 5 % of sites by an exponential gap (mean 50 %, CV 1, true d about
  2.5 points), with K-fit picks IDENTICAL to K-card. Over 60 trials, G = {Dx} on the 320-site frame
  in 37, on its 130-site H-core prefix in 29. In 12 of 60, G = {Dx} on the frame but not on
  H-core, so a row 3 read on H-core prints UNRESOLVABLE although K-fit changed nothing.
- proposed fix: one sentence per reading naming its set. Better: every robustness/K-fit/stratum
  reading uses the frame, the top-up covers frame sites under the four named readings, and the
  frame cost row is re-derived for it.

### FIX-4 Row 1 cannot be read at stage 2: it leans on C-SCORE (built at stage 3), and the scorer refuses H before the rule shas exist
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: the early stop (G4, B18's whole reorder) never fires where it is staged. Stage 1
  (three measuring windows) and stage 3 are always paid before row 1 can read.
- where: §8 lean column (C-SCORE "1-8", C7 "1-8"), §9.3 row 0 ("NOT RUN is not green"), §11
  (stage 3 lists C-SCORE and the drill on the scorer; stage 2 reads row 1), §3.2 item 3 ("the
  scorer refuses to read H until the prereg's sha matches the code": simulator, rules, scorer),
  G3; B3, B18, B21
- finding: three of rev 1's additions close a cycle. (1) Row 0 makes a NOT RUN control block every
  row that leans on it. C-SCORE leans on row 1 and runs at stage 3, so at stage 2 row 1 is NO
  VERDICT. (2) The leak guard pins the RULE and SIMULATOR shas before any H read, and those exist
  only at stage 3. Row 1 is "read ... before any simulator exists". (3) C7(a) is "the whole
  scoring run" on each half, which needs the rules. §3.2 item 4 (aggregate-only) is the intended
  exception but is not written into item 3's refusal or into row 0.
- repro: text (lines cited above). Row 1's own text says "row 1 before any simulator exists".
- proposed fix: give row 1 its own pinned scorer subset (FM-only regret, cross-fit, C-SCORE's
  arithmetic plants and C7 on FM alone) in the stage-0 skeleton, and write the aggregate-only
  exception into §3.2 item 3 and row 0.

### FIX-5 Without L-KIT, row 1's "DOES NOT PAY ON THE BACKEND SLOTS" is unreachable as written; the drill fires it by a rule the text does not have
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: F7's leaning (run without L-KIT if it is late) gets no early stop at all. Or, by
  the drill's reading, it gets an early stop with no blind-spot probe: B3's original defect,
  restated for the backend scope.
- where: §8 C-BLIND (population (ii): "salted random deny sets past the cap on census-truncated
  sites"), §9.3 row 1, drill D12b; B3
- finding: row 1 fires only if "C-BLIND is green with reach ≥ 0.8". Without L-KIT, population (i)
  is empty and population (ii) exists only on census-truncated sites. The dry census truncated 0 of
  277 patterns, so reach is 0 and the row "does not fire" (its own last sentence). The drill's
  `verdict()` instead fires the backend-only verdict when `blind_reach is None`, with no reach
  test (D12b). So the drill and the text disagree, and D12b "lands where intended" only under the
  drill's reading. B3's disposition asked for random cross-path arms "so the probe exists without
  L-KIT". Rev 1 confined them to truncated sites. That is honest (an untruncated walk is near
  exhaustive over the levers), but it leaves the backend scope with no probe and no stated reason
  it needs none.
- repro: `census_dry_summary.txt` "truncated at cap 0" (rwquest 172, rxt 87). `verdict_drill.py`
  `verdict()`: `if ok and r1["blind_reach"] is None: return ("PRICING-DOES-NOT-PAY", "backend
  slots only")`.
- proposed fix: say the backend scope needs no C-BLIND because the census is exhaustive over the
  levers (C-ENUM is its control) and write that into row 1. Or keep (ii) on a salted sample of ALL
  sites, as B3 asked. Make the drill and the text say the same thing.

### FIX-6 C-BLIND's red threshold is calibrated on a false-beat rate that is 0 by construction
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: one noisy beat on any H-core site turns C-BLIND red and blocks row 1. Or, if the
  implementer substitutes a non-zero rate, the stated reach (0.87, which assumes one detection is
  red) is overstated.
- where: §8 C-BLIND ("Red when the number of beating sites exceeds the 99 % binomial bound of the
  false-beat rate measured on the A/A copies"), §5.4 NULL_c; B3
- finding: a draw beats when it is faster than every model-chosen arm by more than
  max(NULL_c, 5 %). Applied to the A/A copy (grid1's `base#b`), the copy is compared with its twin
  `base`, which is model-chosen (the kit's default pick). Their gap is AA_c by definition, and
  NULL_c ≥ AA_c, so the copy can never beat. The measured false-beat rate is identically 0, its
  binomial bound is 0 beats, and any single beat is red. The reach formula P(≥ 1 detection)
  matches that only by accident. With any non-degenerate null it overstates reach.
- repro: arithmetic. |base#b − base| = AA_c ≤ max(AA_c, ν·σ) = NULL_c ≤ max(NULL_c, 5 %), so
  "faster by more than" is never true for the A/A copy.
- proposed fix: calibrate on a null that can beat: time ONE C-BLIND draw twice per site (draw vs
  draw#b), or confirm each beat on the other cross-fit half. State reach for that threshold.

### FIX-7 "NULL_c ... by name (regime_eval.md §4.3)" is not regime_eval's NULL_c, and as defined it collapses to the single-pair floor B12 rejected
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: every per-cell NULL call, C7(b)'s qualifying set, (iii)'s N, C-BLIND's and C-XH's
  floors and the 1.5x worst-case guard rest on ONE A/A gap per cell. Round 1 MEAS-6 measured that
  about half of truly tied cells clear such a floor.
- where: §5.4 NULL_c, §3.5 (one A/A copy), §8 C7; B12
- finding: rev 1 sets σ_pool = "the 95th percentile of the A/A gaps over every cell of the same
  timing block (one group: one site, stream and shape)". A cell IS (site, stream, shape) (§0
  Words), and grid1's group is one (cell, subject, mode) with one `base`/`base#b` pair (grid1
  README "Groups", "Per-row figures"). So the block holds one cell, σ_pool = AA_c, and
  NULL_c = AA_c. regime_eval's NULL_c is `max(AA_c, ν·ns_walk(c))`, with ν the slot's median
  RELATIVE gap from an INDEPENDENT copy `walk#c` that AA_c never reads (regime_eval.md:540-545,
  :2113-2117). Rev 1 times one A/A copy, so it cannot form that ν.
- repro: regime_eval.md line 540; grid1 README lines 174-183; rev 1 §5.4 and §3.5 ("one A/A copy
  of the default").
- proposed fix: adopt regime_eval's formula literally, with a third base copy (grid2 already times
  `base#c`, FIX-21) and ν pooled over the box's blocks of one pool, or pool σ over a declared set
  of blocks. Not "by name" with a different formula.

### FIX-8 C-ENUM goes red on correct data: the walk's own omissions are not among its allowed explanations
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: C-ENUM leans on rows 2-8, so a red C-ENUM is NO VERDICT for every placement row.
- where: §8 C-ENUM ("must be explained (refused contract row, split-gated, truncated)"), §3.1
  item 2 (RECOVER and FINISH NEVER walked; route seeds contribute their default arm, "not a
  sub-walk"); B8 × B10
- finding: B8's fix deliberately leaves rows unreached: every valid RECOVER/FINISH row below the
  upstream default, and every priced-slot row reachable only under a VM/DFA seed (for example
  RETRY `fixed` via `-fno-hyb-reseed` on a VM-seed arm of a DFA-default site). B10's fix makes
  L-VALID dump validity on every arm, so all of these are "valid on some arm and reached on none".
  None fits C-ENUM's three explanations. The dry census shows the scale: RETRY differs on 250 of
  259 sites only through seeds, and on about 12 through the default route.
- repro: §3.1 item 2 vs §8 C-ENUM text; `census_dry_summary.txt` (default-route RETRY
  signatures: "FIRST+PRESENCE+RETRY 5; FIRST+NEXT+PRESENCE+RETRY 3; FIRST+NEXT+RETRY 2; RETRY 1;
  FIRST+RETRY 1" = 12).
- proposed fix: add "dependent slot (RECOVER/FINISH), reached as upstream default" and "seed arm,
  not sub-walked" as declared, COUNTED explanations, and name the seed-only RETRY stratum as
  predicted ungated in §7.3.

### FIX-9 C-FM's stated derivation omits the readers' `under` deny masks, so a simulator written from the text mis-derives every predicate-READ record on handoff sites
- status: CONFIRMED (code); firing count SUSPECTED (needs the trace build)
- severity: design
- effort: small
- blast radius: "a single mismatch stops stage 3". C-FM red on correct data, or a blinded C-RULE
  author who reads only the design misses the term.
- where: §6.4 C-FM ("from (that arm's deny set, that arm's L-VALID records, the table order and
  the deny classes)"), §0 Words (path = CANDROW records); `src/gen/emit_dfa.c:11638-11643`,
  `:9957`, `:9986`, `:10022`, `:11517-11519`; B9, B10
- finding: CANDROW records include predicate READS (field 5 `read`, `cand_hit_as(..., "read")`
  at :11588). `cand_read` selects under `flags | cand_nodes[reader].under[slot]`, and PRESENCE,
  NEXT and RECOVER all read NEXT under `PCREC_NO_REQ_HANDOFF`. On an arm whose NEXT ask lands
  `handoff-reentry`, the read records name the row BELOW it. A re-derivation that uses only the
  arm's deny set yields `handoff-reentry` there and mismatches.
- repro: `sed -n 11638,11643p src/gen/emit_dfa.c` (`cand_select(slot, s, s->cx->opt->flags |
  cand_nodes[reader].under[slot])`); `grep -n '\.under = ' src/gen/emit_dfa.c` → 9957, 9986, 10022.
- proposed fix: add "the reader's `under` mask (record field 5 = read)" to C-FM's inputs and to
  L-VALID's dump key, and plant a C-FM failure that drops it.

### FIX-10 C-SCORE's site-oracle clause is either a tautology or red on honest data under cross-fit
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: B7's replacement check either never fires, or (implemented as a one-pick rule)
  fires on every site where the cross-fit halves disagree. C-SCORE leans on rows 1-8.
- where: §0 Words ("The site oracle's regret is 0 by definition"; "chosen and scored on different
  trials"), §5.4 cross-fit, §8 C-SCORE; B7
- finding: if the scorer scores the SITE-ORACLE rule against its own oracle, "0 exactly" restates
  the definition and cannot go red. The planted join swap is caught only by the ANTI-ORACLE leg.
  If it is a real one-pick rule, cross-fit has TWO site oracles (one per half). Where they differ,
  any single pick has non-zero regret.
- repro: arithmetic. Two tied arms; half A: a1 = 1.00, a2 = 1.02; half B: a1 = 1.02, a2 = 1.00.
  The pick a1, read on B against the oracle chosen on A (a1): 1.02/1.02 − 1 = 0. Read on A against
  the oracle chosen on B (a2, 1.02 on A): 1.00/1.02 − 1 = −0.020. Cross-fit mean −0.010, not 0.
- proposed fix: state C-SCORE's oracle leg as "the scorer's oracle column, re-joined from raw
  logs by an independent path, scores 0", or as an expected value with a tolerance from C7.

### FIX-11 Top-up (and late frame) arms are compared across timing windows with no bridge
- status: CONFIRMED (text)
- severity: design
- effort: small
- blast radius: regret of every top-up pick (K-fit, σ = 0.3, cross-box: the robustness readings
  rows 3-5 read) carries window-to-window drift that NULL_c, a within-block A/A floor, does not
  contain.
- where: §3.5 top-up ("ONE top-up window"), §11 3b, §5.4; §4.3's own premise ("Two windows add
  drift that no within-window band contains"); B17
- finding: a top-up arm is timed in a later block. The cell oracle it is divided by, and FM in the
  paired difference, come from the stage-2 block. grid1 re-times `base` and `base#b` in every
  group (README "Interleaving"), so the bridge exists, but rev 1 never uses it.
- repro: text, §3.5 / §5.1 / §4.3.
- proposed fix: express each late arm as t_arm/t_base(own block) × t_base(stage-2 block), or
  re-time the cell's oracle arm in the late group. State which.

### FIX-12 C-REPRO estimates the between-window term from the data it then tests with; a family-wide drift certifies itself
- status: CONFIRMED (logic)
- severity: design
- effort: small
- blast radius: a card family that does not re-measure (the failure C-REPRO exists for) widens its
  own band through s_bw and passes W3. The card floor reads only `noise_e6` (within-window), so
  s_bw is checked nowhere.
- where: §4.3 items 1-2, §4.2 card floor; B13
- finding: s_bw is the pooled excess variance of (W1 − W2) over the family. A family that drifts
  by X between windows gets s_bw ≈ X, so W3's test allows about z·X. The bigger the
  irreproducibility, the wider the band. No ceiling on s_bw exists, and the UNUSABLE floor uses the
  within-window band.
- repro: text; with s_w = 1 %, a family drift of 10 % gives s_bw ≈ 10 % and W3 passes at ±3.4 ×
  √(0.01² + 0.005² + 0.1²) ≈ ±34 %.
- proposed fix: carry the TOTAL band √(s_w² + s_bw²) into §4.2's UNUSABLE floor (it then stops at
  stage 1), and plant a family-wide drift in W2 that must turn the floor red.

### FIX-13 T2 relabels a model artifact as a regime trade, and treats an FM tie differently from a candidate tie
- status: CONFIRMED
- severity: answer
- effort: small
- blast radius: Frank is handed "SPLIT (regime)" where one shape says the winner is the model's
  constant error. A one-shape win reads SPLIT when the other shape ties X with FM, but WIN when it
  ties X with a priced candidate. TIE WITH NAMED LOSSES drops its losses when combined.
- where: §9.3 T2 rows b-e; the drill's `T2()`; B4
- finding: row b lists INCONCLUSIVE, MARGINAL and SPLIT only. UNRESOLVABLE (row 3) and NO
  PLACEMENT BEATS FM (row 2) fall through to row e. Row d's "both TIE" is silent on 6b.
- repro: `python3 -I fixinduced/py/probe3.py fixinduced/py`. (UNRESOLVABLE A1 | WIN A1) → SPLIT;
  (NO-PLACEMENT-BEATS-FM with Dx ∈ G | WIN Dx) → SPLIT, while (TIE ∋ Dx | WIN Dx) → "Dx (one shape
  only)"; (TIE-WITH-LOSSES {A1, Dx} | TIE {A1, Dx, KF}) → plain TIE.
- proposed fix: put UNRESOLVABLE in row b's weakness order (before MARGINAL), treat a row-2 group
  as a TIE in rows c-d, and carry 6b's named sites through row d. Add three drill scenarios.

### FIX-14 L-ROW's refusal rule contradicts the code on the handoff rows, and refuses `pred-memchr`, leaving the ATTEMPT route's no-search arm unreachable and uncounted
- status: CONFIRMED (code); the site count is SUSPECTED
- severity: design
- effort: small
- blast radius: the no-search arm (§10 item 2's prerequisite) is missing on DFA_ATTEMPT sites
  whose NEXT is `pred-memchr`. The census's 112 count reads stamps, and `pred-memchr` stamps
  `memchr`, so they are neither counted nor excluded.
- where: §3.4 L-ROW rules 1-2, §3.3 NEXT row; `emit_dfa.c` FIRST `handoff`,
  `handoff-attempts`, `handoff-attempts-entry` (`.c.deny = PCREC_NO_REQ_HANDOFF` AND
  `.contract = CG_FIXED`, rows at about :10283-10305); `pred-memchr` (deny 0, CR_ATTEMPT,
  :10421-10423); B5
- finding: rule 1 says a row with `.contract` set is "undeniable by the code's own statement". But
  CG_FIXED means "must never move the give-up surface" (:9831), and three FIRST rows carry it WITH
  a public deny the census walks. The undeniable set is the deny-0 contract rows. Rule 2 refuses a
  deny-0 row outside every declared class. `pred-memchr` is listed in §3.3 as a no-search
  alternative but in no class.
- repro: `sed -n 10280,10305p` and `10421,10427p src/gen/emit_dfa.c`; `grep -n CG_FIXED` (6 rows:
  3 FIRST with deny, 3 RETRY deny 0).
- proposed fix: refuse "deny 0 AND contract" rows, declare {`pred-memchr`} as a singleton class
  (through the same answer-identity sweep), and count DFA_ATTEMPT no-search sites from CANDROW,
  not stamps.

### FIX-15 C7's DERIVED bar is a prereg-skeleton row, but it needs D's timings, and the skeleton is fixed before any H timing with D and H timed in the same stage
- status: CONFIRMED (text)
- severity: design
- effort: small
- blast radius: either C7's bar is not pre-registered (fixed after timing starts), or D must be
  fully timed before H-core starts, which §11 stage 2 does not order.
- where: §8 C7(b) ("the bar DERIVED before any H data ... from the measured per-cell noise of D"),
  §9.3 preamble (C7's bar is a prereg row), G3 (the skeleton before the first H timing), §11
  stage 2 (D and H-core together, jobs by site range); B12, B21
- finding: this is an ordering gap that rev 1's two additions (C7's derived bar, the skeleton/
  rule-sha split) create together. It also re-uses the cross-fit halves {1,3,5}/{2,4} as C7's
  halves. Inside a half, the "whole scoring run" then has no second half to cross-fit on, which
  is unstated (regime_eval splits ROUNDS for C7, :2106-2109).
- repro: text, lines cited.
- proposed fix: order stage 2 as "D, then derive and journal C7's bar, then H-core", and say how
  cross-fit runs inside a C7 half (or split rounds as regime_eval does).

### FIX-16 P-SUBJ picks per (site, pool), but the site oracle is per site: B7's fix holds for P-PRIOR only
- status: CONFIRMED (text)
- severity: doc
- effort: small
- blast radius: the "rate error" reading (P-PRIOR vs P-SUBJ, §7.4) mixes better rates with an
  extra degree of freedom on the multi-pool sites (S-bench and S-corpus, timed on three pools).
  P-SUBJ regrets can go negative.
- where: §0 Words (site oracle), §6.1 ("under P-SUBJ one arm per (site, pool)"); B7 (asked "per
  site x class under P-SUBJ"), B16
- finding: B7's disposition named the per-(site, class) oracle, and rev 1 dropped it.
- repro: text.
- proposed fix: define the (site, pool) oracle for P-SUBJ, or restrict P-SUBJ's comparison to the
  single-pool S-real sites.

### FIX-17 "About 16 differing sites, whatever the gap" is false near the margin, by the design's own power script
- status: CONFIRMED
- severity: doc
- effort: small
- blast radius: §0 item 1's affordability claim for a winner holds only for true differences well
  above δ. Near δ the frame needed is more than twice as large.
- where: §0 item 1, §7.2 "Superiority needs differing sites"; B4
- finding: `n s ≥ 7.84 (1 + CV²)` assumes condition (ii) binds. Near δ, condition (i) (point ≥ δ)
  binds instead.
- repro: `python3 -I fixinduced/py/vd.py --power`: "D 2.5 pp s 0.05 g 50 % → n 691" (34.6
  differing sites), "s 0.10 → n 337" (33.7); 16 holds only from D = 3 pp (n 307 at s 0.05).
- proposed fix: say "about 16 differing sites when the true difference is at least 1.5δ; about 35
  at 1.25δ".

### FIX-18 Condition (iii)'s N cites regime_eval's quadrature, which is a SUM; compared with a MEAN, SUPERIOR becomes unreachable
- status: CONFIRMED
- severity: doc
- effort: small
- blast radius: a scorer written from the text never crowns anyone. The drill-on-scorer gate
  (§9.5) would catch it (D3 must WIN), which is why this is doc.
- where: §7.2 (iii); regime_eval.md §3.0 (`N(S) = sqrt(Σ_g (Σ NULL_c)²)`, compared there with
  Σ regret); the drill's `Pair.N` divides by n
- finding: the text and the drill disagree on the term.
- repro: 16 differing sites at NULL = 3 %: N = 0.03 × √16 = 0.12, so d̄ > 0.24 (24 points) is
  needed. Drill: N = 0.12/320 (frame n).
- proposed fix: "N = sqrt(Σ NULL_i²)/n (the mean's noise)".

### FIX-19 J3b (the frame's source) has no stated D/H split, no dedupe against J1/J3, and no lane or cost
- status: SUSPECTED
- severity: design
- effort: small
- blast radius: a 320-site frame needs about 130 more qualifying H sites. On one seven-directory
  corpus, a third blinded list (after J1 = 177 and J3 = 300) is likely to repeat patterns. A
  repeated site is double-weighted in the bootstrap, and a J1 repeat puts the regime evaluator's
  judge population into H. §11's eight lanes do not include J3b.
- where: §3.2 H-frame, §7.2, §11; B4
- finding: the exclusion manifest covers S-witness only. Nothing dedupes J3/J3b against J1 or each
  other.
- repro: would be confirmed by the J3/J3b pattern lists' text-sha intersection with J1's.
- proposed fix: dedupe every J list by text sha and skeleton against all earlier lists (J1, J1b,
  J3), state J3b's split (all H?), and add its lane to §11.

### FIX-20 C-XH's rank-correlation clause has no gap condition, so near-tied arm sets can turn it red on correct data
- status: SUSPECTED
- severity: design
- effort: small
- blast radius: C-XH leans on rows 1-8, so a red C-XH is NO VERDICT. Within-site rank correlation
  over tied arms is about a coin flip against a 90 % bar. The bench also builds arms differently
  (`-O2 -fPIC -shared` shim, `testees/pcrec/configs.toml:414`) from grid1 (static `-O2`,
  `grid1/build.sh:121`), so a real small reorder is possible.
- where: §5.1 C-XH
- finding: clause 1 is gap-gated, clause 2 is not.
- repro: confirm by counting, on D's timings, the sites whose public-flag arms all lie within the
  bench's floor (2-7 %).
- proposed fix: rank correlation only over arm pairs whose gap exceeds both floors, with the bar
  derived from D the way C7's is.

### FIX-21 (sibling) The timing harness should JOIN grid2, which already is grid1 + streamed windows + libpcre2 + three base copies
- status: CONFIRMED
- severity: maintenance
- effort: small
- blast radius: a parallel grid1 ext set re-builds `streamgen.py` (64 x 64 KiB windows,
  `disjoint`), the libpcre2 oracle wiring, the provenance gate and the rerun rule. It also lacks
  the `base#c` copy whose absence breaks NULL_c (FIX-7).
- where: §5.1 (grid1 primary), §13 (grid2 never cited); `docs/dev/lanes/grid2/CLAUDE.md`,
  `README.md:84-88, 105-107`
- finding: grid2 (`kit-grid@2`) extends grid1 through its two env hooks and is regime_eval's
  harness. Rev 1 has also already redefined three of regime_eval's evaluator terms: NULL_c
  (FIX-7), C7's halves (FIX-15) and N (FIX-18). P1's "share at the build go" would then be a
  re-definition, not a share.
- repro: `grep -n 'base#c\|streamgen' docs/dev/lanes/grid2/README.md`; `grep -c grid2` in the
  subject = 0.
- proposed fix: name grid2 as the harness (method `kit-grid@2`, with the ext set for levers), and
  restate NULL_c, C7 and N by regime_eval's text where they agree, or say why they differ.

## GOALS

§G states five ranked goals, each with a checkable form. Rev 1 serves G1 (fairness: blinded
C-RULE, salted split, view check) and G3 (drilled first-match tables, skeleton and shas) first,
as ranked. One conflict is resolved against the rank without saying so: G4's "the early stop reads
before any per-box set is built" requires reading H at stage 2, while G1/G3's leak guard ("the
scorer refuses to read H until" the rule shas exist) forbids it. As written, neither yields (FIX-4).
G2's measurable form rests on C7, C-XH and NULL_c, which FIX-7, FIX-15 and FIX-20 weaken. No
other goal finding.

## STANDING QUESTIONS

- **Sibling of a family.** The census → `emit_sweep.py` mode (P1) and L-VALID → [DECISION-LOG]
  hold as planned. The miss is grid2 (FIX-21): the design picks grid1 and re-derives regime_eval's
  streamed method around it, while regime_eval's own grid2 already packages it. The prereg as an
  evaluator-params ([KNOW-SRC]) table is P1's. Note that regime_eval's EP table already carries
  EP32 (C7's bar), EP30 (ν) and EP01 (the 2·N factor), the very rows rev 1 re-states differently.
- **General form + unlocks** (P3's replay evaluator not repeated). Rev 1 adds a second general
  piece P3 does not name: DISAGREEMENT-ONLY PAIRED TIMING. When two policies' picks are known
  compile-only, time only the sites where they differ, against a common base in the same block
  (the H-frame). It is emit_sweep's mover census (which already counts movers between two compiles,
  compile-only) joined to grid2's interleaved block. Unlock: any selection-row landing whose speed
  claim is a paired comparison against FM could be graded on its movers alone, with power derived
  from the mover share (§7.2's formula). Trigger: the next opt row landing with a speed claim and a
  known mover count. Prerequisite: FIX-2's scale question, settled once for the general form.

## PROBED-AND-HELD

- B1: (a)/J out of the candidate set (§9.3 preamble; drill `CANDS` has no (a); D5 lands TIE, not
  "(a) WINS"). 1 table, 1 drill scenario. Holds.
- B9: CANDROW carries 6 fields (slot, route, row, site, ask|read, hand), `emit_dfa.c:11517-11519`.
  The Words key (slot, route, asker, hand) maps onto fields 1, 2, 4 and 6. Holds (but see FIX-9 for
  field 5).
- B5's twin-class rationale: the `memchr`/`byte-class` predicates (`:6602-6609`) do not test
  `views`, and the bounded ones do (`:6599-6606`). 4 predicates. Holds.
- Code cites at `a3cc4de82`: cand_select 10721, cand_fallback 10735-10747, cand_select_quiet 10869,
  PCREC_PICK_PLANT 10974, req_pick_shadow `used` restore ~10996, CandPath 11828, FINISH totality
  11394-11400, views 4603-4605, UNMEASURED DEFAULT 7872-7876 and 8020-8026, adaptive-dense 10087,
  RETRY contract comment 10430-10447, `PCREC_MF_MEAS_CONSULT` (in `memfn_sites.c:986-990`, not
  emit_dfa, as the design says). 14 cites land.
- L-ROW inside `cand_select` reaches the quiet walks and predicate reads too (all go through
  `cand_select`: :10875, :11641), so a class deny cannot desynchronise the cross-route self-check
  (`cand_every_route`, :11549-11558). 3 call paths. Holds.
- C-BLIND reach arithmetic: k = 4 → 0.8725, k = 2 → 0.660 (n = 110, f = 5 %, q = 10 %). 2 values
  hold.
- Power table (§7.2): 4 rows reproduced exactly by `vd.py --power` (sd_d 0.0049/0.0312/0.0624/0.0872;
  n 5/38/335). Holds.
- Drill: 23 scenarios, 0 off-target, re-run. The tables as the DRILL implements them are
  consistent; text-vs-drill gaps are FIX-5, FIX-13 and FIX-18.
- Frame exactness: agreeing sites contribute d = 0 exactly (same arm, same launches), and
  agreement is decided compile-only from frozen rules, so timing only disagreeing sites selects
  nothing on outcomes. Holds.
- Census: truncated at cap 0 of 277; route-seed arms 754 of 1,565; default-route qualifying 197 of
  259. 3 figures match §3.1.
- B23 (MN reads C-BYTE and C-ENTRY, §6.1), B24 (`sealed/` excluded), B19 (rulings table with
  quoted clauses, 5 rulings), B6 (MARGIN at equal setting for Dx/Dp/J), B21 (G1 on D). 5 doc fixes
  present and consistent.
- Compiles: 7 (`gnutimeout 30 nice`, sequential) to look for an ATTEMPT-route stamp; none of the 6
  probe patterns landed it, hence FIX-14's count is SUSPECTED.
