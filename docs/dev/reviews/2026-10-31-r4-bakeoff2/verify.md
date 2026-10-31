# VERIFY: bakeoff2 (pricing_bakeoff.md rev 1 @ deebb4dd8), verifier sonnet

## SIM-FIX-iii (SIM-1 + FIX-18: condition (iii) N, sum vs mean)
- verdict: HOLDS as a wording defect; the "unreachable" consequence holds only under the literal reading.
- ran/read: design 7.2 (iii) "d-bar > 2.N, N the measurement noise of the pair (quadrature over the differing sites of their NULL_c, regime_eval.md 3.0)"; regime_eval.md:1843-1849 defines N(S)=sqrt(sum_g (sum_c NULL_c)^2) and applies it to regret SUMS (line 2073 Delta_C(S)=sum_c). Design compares it with d-bar, a MEAN over n frame sites, and never says "/n". verdict_drill.py:42 `self.N = sqrt((diff*FLOOR**2).sum())/self.n` divides by n and uses one constant FLOOR=0.01 (design says each site's NULL_c).
- own arithmetic: 16 differing sites at NULL 1 pt: sum-scale N = 4 pts, 2N = 8 pts, vs a delta-sized d-bar of 2-3 pts: unreachable. Mean-scale (/n, n=320): 2N = 0.025 pt: vacuous (never binds). So the text is ambiguous between "never SUPERIOR" and "no noise test at all"; the drill silently takes the second.
- severity: SIM says answer, FIX says doc. Right call: design (the text cannot be implemented unambiguously; the drill-on-scorer gate D3 would catch the sum reading, so it is not a wrong verdict in practice). Note also that the mean-scale form makes (iii) nearly vacuous, which neither critic says.

## FIX-1 (H-frame consumes H-sealed)
- verdict: HOLDS.
- ran/read: design 3.2 lines 326-337: "H-sealed ... NOT TIMED unless opened ... read ALONE as that revision's held-out set"; "H-frame: H-core plus every further H site of J3 (and of J3b ...). On a frame site only the picks of the frozen rules, FM's arm and one A/A copy are timed, and only where two candidates pick differently. The pair tests of 7.2 read the frame". H sites of J3 not in H-core are exactly H-sealed's S-real sites (H = 70 % of S-real + S-bench deployed; H-core = 2/3 of H by hash). Size paragraph: H ~193, H-core ~130, H-sealed ~65; 7.2/0 item 1 need a frame of ~320, so the frame must absorb H-sealed (65, minus S-bench share) plus ~130 J3b sites. Frame disagreeing sites of H-sealed are therefore timed and read at the first reading, contradicting "NOT TIMED unless opened". Only escape: reading "further H site of J3" as J3b only, which the text does not say.
- severity: design is right (the one-revision held-out reserve is void as written; small fix).

## FIX-2 (paired difference on t_FM scale vs regret: sign flip)
- verdict: HOLDS (arithmetic and definition); consequence for real verdicts is a matter of degree.
- ran: copied probe1.py/vd.py into verify/, `python3 -I probe1.py`: mean regret X 0.150, Y 0.500 (X better) but paired d(X,Y)=+0.100 (X "slower"). Hand check: site1 (tX-tY)/tFM=(1-2)/10=-0.1, site2 (1.3-1)/1=+0.3, mean +0.1; regret X=(0+0.3)/2, Y=(1+0)/2. Design 0 Words defines paired difference as mean of (t_X-t_Y)/t_FM; 9.2 justifies delta against PR O1's 5 % of regret; drill Pair uses d=r_X-r_Y (verdict_drill.py:33-35), so the tables are never run on the defined metric.
- severity: FIX says answer. I rate design: the two scales are a definitional choice that must be unified (and the flip needs FM to differ hugely across sites, which the design's own 1.6x-18x witnesses supply), but nothing says it flips the real verdict.

## FIX-3 (which site set K-fit / robustness / strata read)
- verdict: HOLDS as an unspecified-set defect; the "row 3 fires on sample size" consequence holds only under the H-core reading.
- ran: probe2.py reruns identically: 60 trials, G={Dx}: frame(320) 37, H-core prefix(130) 29, frame-only 12. Design text: 3.2 "pair tests read the frame; nothing else does"; 7.1 "all on H-core"; 9.3 T1 defines G by the pair tests (frame), row 3 uses "G under K-fit"; 3.5 top-up covers "every arm a rule picks under K-fit/sigma/cross-box that was not timed" but frame sites time only the frozen rules' picks. Neither reading is stated. Note the 37/60 (62 %) frame power is itself the SIM-5 power shortfall, not a row-3 effect.
- severity: design (not answer): a one-sentence fix names the set; if the frame is read, the issue becomes top-up coverage of frame sites.

## FIX-4 (row 1 at stage 2 leans on stage-3 controls / sha guard)
- verdict: HOLDS.
- read: 8 lean column: C-SCORE, C7, C-XH, correctness gate, C-LEVER lean on rows "1-8"; 9.3 row 0: a lean-control "red or NOT RUN" gives NO VERDICT for that row. 11: C-SCORE is a stage-3 item ("the simulator ... C-SCORE, the drill on the scorer") and stage 4 lists "C-SCORE green; the drill reproduced" as a prerequisite; stage 2 reads row 1 "STOP if it fires". 3.2 item 3 pins simulator, rules and scorer shas before any H read ("the scorer refuses to read H until the prereg's sha matches"); item 4 describes the aggregate-only early stop but does not exempt it from item 3 or from row 0. Row 1 text itself says "before any simulator exists". So as written row 1 is NO VERDICT at stage 2 (C-SCORE NOT RUN). Mitigation the critic notes: intent is obvious; fix is a pinned scorer subset plus an explicit exception.
- severity: design is right (small).

## ROW1-NOKIT (SIM-2 + FIX-5: backend-only row 1 unreachable as written; drill skips reach)
- verdict: HOLDS (a text-vs-drill inconsistency and an unstated rationale); the "unreachable" reading is one of two readings, so wording defect rather than proven dead row.
- read: 9.3 row 1 requires "C-BLIND is green with reach >= 0.8" and ends "With C-BLIND's reach below 0.8 the row does not fire"; the same cell also says "With L-KIT absent (C-BLIND's kit population empty ...): PRICING DOES NOT PAY ON THE BACKEND SLOTS" (an exception reading). 0 item 4 says the reading "requires a POWERED blind-spot probe; without L-KIT it can only say ... BACKEND SLOTS" (no exception). 8 C-BLIND population (ii) exists only "on census-truncated sites"; census_dry_summary.txt lines 1,7,12: "truncated at cap 0" on 259 of 259 compiling patterns, so without L-KIT the population is empty and reach is 0. verdict_drill.py:165-166: `if ok and r1["blind_reach"] is None: return ("PRICING-DOES-NOT-PAY","backend slots only")` with no reach test (D12b scenario sets blind_reach=None, line 263).
- caveat: the dry census used public flags only; L-ROW classes add arms so some patterns may truncate later, but not enough to give a powered n.
- severity: design is right (F7's "run without L-KIT" gets either no early stop or an unprobed one); fix is small.

## CBLIND-NULL (SIM-3 + FIX-6: A/A false-beat rate 0 by construction; reach at nonzero p0)
- verdict: HOLDS (the arithmetic and the degenerate-null argument); SUSPECTED part (how the rate would be scored) stays suspected.
- ran: copied simulate/work/reach.py to verify/, `python3 -I reach.py`: formula reach 0.8725 (k=4) and 0.6596 (k=2) reproduce (own hand check: 1-(1-0.1*(1-0.95^4))^110 = 0.8725); at p0=1/130, bound T=4, reach of the red rule 0.62, false-red with no blind spot 0.24 (own sanity: site false rate 1-(1-0.0077)^4=0.0305, Bin(110,0.0305) mean 3.4, P(>=5) ~0.24); at p0=2/130 false-red 0.65.
- logic check: a draw beats iff faster than every model-chosen timed arm by > max(NULL_c, 5 %); 5.4 NULL_c = max(AA_c, nu*sigma_pool) >= AA_c; the A/A copy base#b against its twin base (a model-chosen arm) differs by exactly AA_c on the same data, so it can never beat; measured p0 = 0, binomial bound 0, any single beat is red. Two real gaps: the design never says the copy is scored on cross-fit halves (which could give small nonzero p0), and sites carry k=4 draws but p0 is one copy per site.
- severity: design is right.

## SIM-4 (EQUIV power formula)
- verdict: HOLDS.
- ran: own script verify/v_tost.py (normal TOST power Phi((d-D)/se-1.645)+Phi((d+D)/se-1.645)-1, sd_d as in the design) and a 300-rep percentile-bootstrap MC:
  | row (s,g,sg) | design 110 / 40 / n80 | correct normal 110 / 40 / n80 | my MC (bootstrap) |
  | .05 .02 .01 | 1.00 / 1.00 / 5 | 1.00 / 1.00 / 2 | not run |
  | .05 .10 .10 | 1.00 / 0.84 / 38 | 1.00 / 0.92 / 28 | n=40 0.77, n=45 0.81, n=110 0.98 |
  | .05 .20 .20 | 0.03 / 0.00 / 335 | 0.51 / 0.18 / 242 | not run |
  verdict_drill.py:299-300 `eqp` = 2*Phi((DELTA-|D|-1.645se)/se)-1 mirrors the lower tail (its header says "at true diff 0"), so it understates power wherever D != 0 (row 3 at n=110: 0.03 vs 0.51). The 0.84 at n=40 is not even the right sign of error for the bootstrap: the bootstrap gives ~0.77-0.78 (matches SIM's 0.78; critic's n80~45 matches my 0.81 at n=45). The sd_d formula checks (0.0049/0.0312/0.0624).
- severity: design is right but modest: the stage-0 STOP floor should be ~45-50 H-core sites rather than 40, and row 3's claim is wrong in the conservative direction.

## SUPERIOR-SIZING (SIM-5 + FIX-17: four-condition power; "16 differing sites whatever the gap")
- verdict: HOLDS.
- ran: own MC verify/v_sup.py (d_i=0 w.p. 1-s else N(g,(g)^2), D=3 pt, bootstrap 1000, (i) mean>=0.02, (ii) 2.5 % quantile >0, (iv) exact one-sided sign test over |d|>1 pt p<0.025; (iii) on the mean scale is vacuous): all-four power at the design's n = 0.72 (s .05, n 307), 0.68 (.10, 150), 0.67 (.20, 71); with ~20 differing sites 0.81-0.82 (n 400/200/100). Marginals at n=307: (i) 0.83, (iv) 0.76. Matches SIM-5 (0.67/0.70/0.65) within MC noise.
- design's own script output verdict_drill.out lines 39-44: D=2.5 pp needs n=691/337/160 (34.5 / 33.7 / 32 differing sites) vs D=3.0 pp n=307/150/71 (15.4 / 15 / 14); so "about 16 sites ... whatever the gap" (0 item 1, 7.2) is contradicted by the design's own table; it holds only from about 3 pp up.
- severity: SIM says design, FIX-17 says doc. Right: design for the sizing (J3 is sized from it) and doc for the "whatever the gap" sentence.

## SIM-6 (sign-test failure with >= 6 one-way sites lands MARGINAL)
- verdict: HOLDS.
- ran: verify/v_sim6.py driving the design's own T1 (verdict_drill.py copy) on 110 sites, 6 rivals lose 80 % on `a` sites, Dx loses 3 % on `b` sites: (a=6,b=0) WIN Dx; (7,0) WIN; (5,0) INCONCLUSIVE; (6,1) MARGINAL with d-bar(A1-Dx)=4.3 pts, nplus 6 nminus 1 (sign test p=8/128=0.0625); (7,1) MARGINAL, 5.1 pts (p=9/256=0.035); (7,2) MARGINAL, 5.0 pts. 7.2's UNDERPOWERED clause is "fewer than six one-way differing sites", so 6+1 / 7+1 do not match and fall to "otherwise ... MARGINAL, a real difference near the margin", while the difference is ~2.5 delta.
- severity: design is right but mild: the outcome (Frank rules, sees the numbers) is a weak verdict mislabelled "near the margin", not a wrong crowning.

## SIM-7 (printed frame size smaller than the frame read)
- verdict: HOLDS.
- read: verdict_drill.out D2 -> "A1-HY needs ~54 sites" (read on 110) and D8 -> "A1-Dx needs ~45 sites" (read on 40). 7.2 says `n x (half-width / gap)^2` without defining gap; drill j4 (lines 62-65) takes gap=|mean| for |mean|>=delta/2. Own check: D2 has 5 one-way sites of 110 (share 0.0455); P(>=6 one-way sites) is 0.035 at n=54, 0.38 at 110, 0.74 at 160, 0.87 at 190 (binomial). So 54 sites cannot settle a pair already unsettled at 110; ~170-190 would be needed for 80 %.
- severity: design is right (J3b is sized from this number).

## T2-HOLES (SIM-8 + SIM-9 + FIX-13)
- verdict: HOLDS (all three parts).
- ran: probe3.py (copied) on the design's T2: (UNRESOLVABLE A1 | WIN A1) -> SPLIT; (NO-PLACEMENT-BEATS-FM, all six | WIN Dx) -> SPLIT while (TIE with Dx | WIN Dx) -> "Dx (one shape only)"; (TIE-WITH-LOSSES {A1,Dx} | TIE {A1,Dx,KF}) -> plain TIE, losses dropped. Text check (9.3 T2): row b lists INCONCLUSIVE, MARGINAL, SPLIT only; row c needs "X WINS" plus "a TIE whose group contains X"; row d "both TIE"; row e "otherwise ... SPLIT (regime)". Rows 2 and 3 of T1 (and the script's extra NO-VERDICT entry in WEAK, which the text lacks) have no T2 row, so they fall to e. Row d is silent on 6b.
- severity: SIM says design, FIX says answer. Right: design (Frank still rules and sees both shapes' verdicts; the label "regime trade" is wrong and a 6b loss is dropped, but nothing is crowned wrongly).

## SIM-10 (row 0 per-row blocking: script and text disagree)
- verdict: HOLDS.
- ran: verify/v_sim10.py with the design's drill copy and D12's row-1 data: no red -> PRICING-DOES-NOT-PAY; C-RULE red -> NO-VERDICT (verdict_drill.py:158-161 returns NO-VERDICT for any red except C-BLIND, before row 1). Text 9.3 row 0 blocks "that row and every row after it that leans on the same control" and 8's lean column gives C-RULE "2-8", so row 1 should still fire per the text. The D13 scenario carries no row-1 data, which is why it lands. The converse (a control leaning only on row 4 blocked, G={X}: rows 5-7 do not match, row 8 "otherwise" prints MARGINAL for a single-member G) follows by reading T1 rows 5-8 and is not exercised by the drill.
- severity: design is right (small).

## SIM-11 (INCOMPLETE global or per shape)
- verdict: PARTLY (REFUTED in substance, doc-level wording only).
- read: 3.5 line 469-471: "a rule with more than 2 % UNCOVERED cells on any of the top-up readings is INCOMPLETE and is not a candidate in 9.3"; 9.3 preamble: "A candidate that is INCOMPLETE is dropped from the candidate set". The "top-up readings" there are K-card/K-fit/sigma/cross-box, not call shapes, and the candidate set is stated once, before T1, for both shapes. The drill implements it as global (`sc["incomplete"]`). The per-shape reading SIM-11 builds the regime-trade consequence on is not what the text says; the text is merely silent on the word "global".
- severity: doc, not design.

## NULLC (FIX-7 + MEAS-6: NULL_c is not regime_eval's definition and collapses to AA_c)
- verdict: HOLDS.
- read: design 5.4: "regime_eval's NULL_c = max(AA_c, nu x sigma_pool) by name, with AA_c the cell's own A/A gap and sigma_pool the 95th percentile of the A/A gaps over every cell of the same timing block (one group: one site, stream and shape, all its arms interleaved), nu = 1". 0 Words: a cell = (site, stream, call shape), so the block holds ONE cell and, with one base/base#b pair per group (grid1 README lines 174-183), ONE A/A gap: sigma_pool = AA_c and NULL_c = AA_c. regime_eval.md:540-546 and 2113-2117 define nu as the SLOT's median over groups of |walk - walk#c|/walk, taken from an independent third copy walk#c that AA_c never reads, scaled by ns_walk(c). The design has no #c copy, so it cannot form that nu; "nu = 1 over a p95" is a different quantity. So B12 (review 1's rejection of a single-pair floor) is not fixed.
- severity: design is right.

## FIX-8 (C-ENUM red on correct data: the walk's own omissions are not allowed explanations)
- verdict: HOLDS as written (the count of firings is SUSPECTED, needs L-VALID).
- read: 8 C-ENUM: every row "valid on some arm and reached on none ... must be explained (refused contract row, split-gated, truncated)"; 3.1 item 2: RECOVER and FINISH "are NEVER walked: they are reached as the default of the upstream choice", and "Each route seed contributes its own default arm, not a sub-walk". Rows valid below an upstream default, and rows valid only under a seed's subtree, are therefore valid-and-unreached by design and fit none of the three listed explanations; C-ENUM leans on rows 2-8. census_dry_summary.txt: RECOVER(dep) differs on 250 of 259 sites, RETRY on 250 (through seeds), default-route RETRY signatures only 12. A reader could take the parenthesis as illustrative, but it is a closed list.
- severity: design is right (small: add the two declared, counted explanations).

## FIX-9 (C-FM derivation omits the readers' `under` masks)
- verdict: HOLDS (code cites verified; firing count SUSPECTED).
- ran/read at main a3cc4de82: src/gen/emit_dfa.c:11638-11643 `cand_read` = `cand_select(slot, s, s->cx->opt->flags | cand_nodes[reader].under[slot])` with `CAND_READ_HIT(...)` recording the read (:11588-11590 "read"); `.under = { [CAND_SLOT_NEXT] = PCREC_NO_REQ_HANDOFF }` at :9957 (PRESENCE block 9943), :9986 (NEXT block 9974) and :10022 (RECOVER block 10018). Design 6.4 C-FM derives the landing row "from (that arm's deny set, that arm's L-VALID records, the table order and the deny classes)", with no mention of the reader's under mask, and 0 Words makes CANDROW read records part of the path. A re-derivation from the arm's deny set alone cannot apply the extra NEXT deny a reader adds, so a read record can differ on handoff sites. Mitigation: L-VALID is "per (slot, route, asker, hand)" so the records might already carry it; the text does not say so.
- severity: design is right (small).

## FIX-10 (C-SCORE site-oracle clause: tautology or red under cross-fit)
- verdict: HOLDS.
- read/ran: 8 C-SCORE "the SITE-ORACLE rule must score 0 regret exactly"; 0 Words: regret subtracts the site oracle's mean, "The site oracle's regret is 0 by definition", both "chosen and scored on different trials" (5.4 cross-fit, halves {1,3,5}/{2,4}). Own arithmetic of the critic's example: two tied arms, half A (a1 1.00, a2 1.02), half B (a1 1.02, a2 1.00); site oracle chosen on A is a1 (read on B = 1.02), chosen on B is a2 (read on A = 1.02); a single pick a1: read on B 1.02-1.02 = 0, read on A 1.00-1.02 = -0.02; cross-fit mean -0.01, not 0. If instead the rule is scored against its own oracle it is a tautology. The planted join swap is caught only by the ANTI-ORACLE leg.
- severity: design is right (small: state the oracle leg as an independent re-join or as a value with a C7 tolerance).

## FIX-11 (top-up arms compared across windows without a bridge)
- verdict: HOLDS (text).
- read: 3.5 "ONE top-up window", picks "not timed" earlier; 4.3 "Two windows add drift that no within-window band contains". 5.4 floors are within-block. The top-up pick's regret divides by the stage-2 cell oracle and uses stage-2 FM; nothing re-times a base in the top-up group or rescales. grid1 re-times base/base#b in every group (README 174-183), so a bridge is available but unused. Affects the robustness readings (rows 3-5) only, so impact is bounded.
- severity: design (small) is right.

## FIX-12 (C-REPRO estimates s_bw from the same data it tests with)
- verdict: PARTLY.
- read: 4.3 items 1-2: s_bw is the pooled excess variance of (W1-W2) over a family; W3 must agree with mean(W1,W2) within z_FW*sqrt(s_w3^2+(s_w1^2+s_w2^2)/4+s_bw^2). Own check of the critic's numbers: s_w=1 %, s_bw=10 %: sqrt(0.0001+0.000025+0.01)=0.1006; times 3.4 = 34 %. Logic holds: a family whose windows drift apart from each other (W1 vs W2) widens its own band and passes. It does NOT hold for drift of W3 alone (s_bw~0 then; W3 reads red), and 4.2's UNUSABLE floor uses "its noise band" (noise_e6 = within-window A/A) so s_bw is not carried into it. 7.4's "Same box, re-measured" reading re-scores rules on W1-W3 sets, which does catch pick movement from such drift, so the harm is bounded.
- severity: design-minor (control certifies noisy windows, a ceiling on s_bw is missing); not an answer risk because 7.4 reads the moves.

## FIX-14 (L-ROW refusal rule vs the code on handoff rows and pred-memchr)
- verdict: HOLDS (code); the stamp/count consequence is SUSPECTED.
- ran/read at main a3cc4de82: emit_dfa.c:9829-9832 `CG_FIXED /* must never move the give-up surface */`; the three FIRST rows `handoff`, `handoff-attempts`, `handoff-attempts-entry` (:10283-10305) carry `.contract = CG_FIXED` AND a public deny `PCREC_NO_REQ_HANDOFF`; the RETRY contract rows are at :10451/10459/10467 (deny 0). `pred-memchr` is at :10421-10423: deny 0, `.routes = CR_ATTEMPT`, no contract. grep CG_FIXED: 6 rows (3 FIRST, 3 RETRY). Design 3.4 L-ROW rule 1 says "A row with `.contract` set ... is undeniable" (literal reading refuses the three FIRST rows the census itself walks with -fno-req-handoff; the parenthesis says deny 0); rule 2 refuses "a deny-0 row outside every declared class" and the only declared classes are {memchr-bounded, memchr} and {byte-class-bounded, byte-class}, so pred-memchr (listed in 3.3 NEXT row among the no-search alternatives) is refused.
- severity: design is right (small).

## HALVES-C7 (MEAS-7 + FIX-15: median of two, D at 3 launches, C7 bar ordering)
- verdict: HOLDS (all parts; severity of the "answer" flavour not warranted).
- ran/read: grid1 time.sh:112 `med() { ... sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}' }`: for NR=2, index int(1.5)=1, the LOWER of two (not the mean). Design 5.4: halves {1,3,5} and {2,4}, "each half's value is the MEDIAN of its launches' 7-round medians" - the {2,4} half is a median of two, undefined in the text, and the printed time.sh figure is not the right source (use time/raw_<PHASE>.tsv, which README 186-187 says holds every launch). 5.1 line 674: "D runs at 3 launches (diagnostic only, stated)", but 3.2/6.3 fit the K-fit constants on D, 8 C7(b) derives its bar from "the measured per-cell noise of D", and 9.3 preamble makes that bar a prereg row: D is verdict-bearing. A 3-launch D has no stated split ({1,3}/{2}). "Per-round values are kept" (5.1 line 675): gdrv.c:88 prints only t[3] (the 7-round median); the only "round" in the raw file is the launch index (README 186), so the sentence is true only in grid1's vocabulary. Ordering: G3 journals the skeleton "before the first H timing", 9.3 makes C7's bar a skeleton row, 11 stage 2 times D and H-core together "by site range" with no D-first order. regime_eval C7 splits ROUNDS (odd/even) of each launch (regime_eval.md ~2104-2109), not launches; the design reuses its cross-fit halves and does not say how cross-fit runs inside a half.
- severity: design is right (small, ordering plus two definitions).

## FIX-21 (grid2 already provides streamed windows, libpcre2 oracle, base#c)
- verdict: HOLDS on the facts; the proposed fix (join grid2) is a judgment for the manager.
- read: grep -c grid2 on the subject = 0. docs/dev/lanes/grid2/CLAUDE.md: grid2 "extends ../grid1/"; `time.sh` is method `kit-grid@2` ("three base copies, the rerun rule, the re-queue"); `design2.py` has "the libpcre2 10.46 oracle (tests/oracle/ local adapter)"; `streamgen.py` is the streamed subject generator. README (line ~84-88): LAUNCHES 3, base launched THREE times (`base`, `base#b`, `base#c`), rerun rule, "the quiet gate at every group boundary (a group whose end load1 reached 3.0 is re-queued once at the end of its phase)"; subjects: "64 x 64 KiB" distinct buffers, "~0.63 s per launch" at 4 MiB (grid1's 64 MiB ~0.95 s). So the base#c copy the design lacks (NULLC), the re-queue it lacks (MEAS-9) and a measured launch cost above its 0.5 s (MEAS-10) all exist in a harness the design never cites. Caveat: grid2's cells are the kit items 1-8 (design2.py), so per-site ext arms for ~400 cells would still need their own ext set builder; the saving is the harness mechanics, not the arm set.
- severity: maintenance is right (not an answer risk), though it also bears on NULLC, MEAS-9 and MEAS-10 as the cheap remedy.

## MEAS-1 (ext cells have no oracle leg O)
- verdict: PARTLY.
- read: grid1 check.sh header (lines 3-4, 11-13) "every own cell's base must answer exactly as the python re oracle"; leg O in checklib.sh:18-20 is generic: it runs only `if [ -n "$o" ]`, where `o` is the line in `$OUT/oracle.tsv` for (cell, subject, mode); grid.py:289 writes oracle.tsv for own cells only; check.sh:53-55 `ORACLE_CMD` merely replaces that producer (grid2 uses it for its own cells). README 150-151: "Its subjects have no python oracle, so legs R, L and C check them against the cell's base only." So leg O would cover ext cells only if the libpcre2 adapter command writes oracle.tsv lines for them; 5.5 says "ORACLE_CMD pointed at the libpcre2 adapter" but never says it emits lines for the bake-off's ext cells, and no stage-0 item builds that. Under the default behaviour a wrong base passes whenever its arms agree with it. Captures: gdrv.c:41,49-50 hash only cp[0][0], cp[0][1] (group 0), so "captures where requested" (5.5) is compared by no leg - confirmed. The 14 plants are on own cells (not re-read).
- severity: design is right (medium effort), but the claim is "unspecified and uncosted", not "impossible" (the hook exists).

## MEAS-2 (bench call-stream cannot be handed a window end; cited fallback is the wrong mechanism)
- verdict: HOLDS (doc mismatch); the cost consequence stays SUSPECTED.
- read: pcrec-bench docs/design/unusual_set_v1.md 7.1: "the engine is given the rest of the subject from the call's offset ... but the THROUGHPUT DENOMINATOR is the sum of the calls' declared segment lengths"; "Where it fails, that engine anchors explicitly (PCRE2_ANCHORED, onig_match at the offset, RE2::ANCHOR_START ...), recorded as match-scope stream_anchor"; per-call tokens `n`, `m:<s>,<e>[;<g1s>,<g1e>]`, `r` (one match per call). docs/dev/lanes/b148l4_report.md section 3: the pre-flight uses `\G`-anchored cscan; "CONTROL: cscan with `\G` deleted on pcre2-interp reads 8.2x / 14.0x" for a 10x tail; "Every engine stays native". Design 5.1: "the window end must be ENFORCED as the call's length (the L4 pre-flight's `stream_anchor` fallback ...)" and "each call's length enforced as the window end, checked by the bench first". The fallback anchors the START at the offset; it does not bound the END, and `length` is only a denominator. A find-all-per-window LONG shape also needs a multi-match call, which 7.1's one-match token does not provide. The design hedges ("which the bench would check first") but cites a mechanism that does not do the job.
- severity: design is right.

## MEAS-3 (2-7 % "noise floor" is CPU occupancy; +4-5 % is cross-window)
- verdict: HOLDS (and the second quote has a further mismatch).
- read: pcrec-bench docs/design/quiet_baseline.md:38-41: "the instrument's own noise floor is ~2-7 % busy per core even when nothing is scheduled there (timer ticks, mpstat itself ...)" - that is mpstat core-busy percent, the basis of the 10 % pre-flight bar, not timing noise. docs/dev/ledgers/2026-10-29-first-window-614d45eb3.md:87,95-96: "The same pin reads +4.0 to +4.4% on SHORT cells across the two windows, and ~0.0% on the 1 MB-class throughput cells ... a cross-WINDOW pcrec comparison on short-subject or per-call-dominated cells carries a ~+4-5% offset from this harness change; the in-window N vs B pair does not". So it is a cross-window offset on SHORT cells, and C-XH is LONG-shaped (throughput) where the same ledger reads ~0.0 %. docs/design/null_band_v1.md exists in the bench and is not cited.
- severity: MEAS says answer for C-XH's pass rule; I rate design: C-XH can only add NO VERDICT or widen what it admits, it crowns nobody.

## MEAS-4 (C-XH's planted failure not shown to turn the rule red)
- verdict: HOLDS.
- read/ran: 5.1 C-XH pass = same best arm on every site whose grid1 gap exceeds both floors AND positive within-site rank correlation on >= 90 % of sites with >= 3 arms (18 of 20); planted failure = "one site's arm set timed by the bench with two config ids swapped in the join". Own arithmetic: 6 arms, swap the ranks of the 3rd and 4th: d^2 sum 2, Spearman = 1-6*2/(6*35) = 0.943 > 0 and the best arm is unchanged; one site of 20 is inside the 90 % allowance anyway. The plant turns the rule red only if the swap includes the best arm. Not shown.
- severity: design is right (small).

## MEAS-5 (C-XH covers LONG only; arms the harnesses build differently)
- verdict: HOLDS (coverage); build-effect stays SUSPECTED.
- read: design lines 641, 751: C-XH "LONG shape", "pinned, LONG"; SHORT has no independent check. pcrec-bench testees/pcrec/CLAUDE.md: `shim.c` + `driver.c` with `dlopen` as "the third AOT compile phase"; configs.toml:414 `$CC -O2 -fPIC -shared <cflags> shim.c`; one `pin = "<commit>"` per configs.toml. 11 stage 2 lists "the bench (C-XH configs, B7-B9)" but no re-pin to the H commit, no per-site arm configs with `config_extra` tokens, no `expectations_stream.tsv` work. Partly costed as a bench lane, not in the content named.
- severity: design is right.

## MEAS-9 (time.sh quiet gate proceeds; occupancy check is new work)
- verdict: HOLDS.
- read: grid1 time.sh:111-114: `for t in $(seq 1 $LOADWAIT); do ... break if load1 < LOADMAX; waits=$t; sleep 20; done` followed unconditionally by the group; a note is echoed only if waits>0 ("quiet gate: ... waited"). So after 60x20 s the group is timed anyway. `grep mpstat|occupancy` in grid1: no hits (own run). Design 5.1 claims "grid1's (load1 < 1.5 before each group, waits recorded) plus a per-core occupancy check ... at every group boundary" - the occupancy check is an addition and appears in no stage-0 item. grid2 (FIX-21) already has "a group whose end load1 reached 3.0 is re-queued once".
- severity: design is right (medium).

## MEAS-10 (SEC_REP constant: 0.5 s per launch below grid1's own)
- verdict: HOLDS (the critic's line cites are off by 8: the constants are time.sh:42-43, not 34-35).
- read/ran: time.sh:42 `SEC_REP=${SEC_REP:-0.65}  # measured: ... 0.45-0.85 s`, :43 `SEC_STREAM=0.95 ... (64 MiB)`; gdrv.c:84 doubling loop until >= 50 ms, then 7 rounds; grid2 README: 4 MiB streams "~0.63 s per launch". Design 5.6 uses 0.5 s. Own arithmetic: 180x2x16x5x0.65 = 18,720 s = 5.2 h; 100x2x2x12x3x0.65 = 9,360 s = 2.6 h; at the measured 0.63 s the same rows are 5.0 h and 2.5 h; the design's 4.0 h / 2.0 h are 20-30 % low. The design already says `time.sh --estimate` replaces it.
- severity: speed is right.

VERIFY COMPLETE
