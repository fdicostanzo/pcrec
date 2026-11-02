# VERIFY: critic round pricing-split (2026-10-31)

## PREMISE-1
Verdict: HOLDS (with a note on pcre2).
Evidence (verify/w/, B = review-tree compiler, `-p rx --emit-main`, subject = 20,000 x `a` as argv[1], `gcc -O2`, under scripts/watchdog):
- default: `RX_ENGINE_SEL "declined-nullable-default"`, `RX_VM_PREFILTER "none"`; prints `steps`, exit rc=3, 2.30 s.
- `-fprefilter`: `RX_ENGINE_SEL "selected"`, `RX_VM_PREFILTER "hybrid"`; prints `match 0 0`, rc=0, 0.13 s.
- libpcre2-8 driver (verify/w/pc.c, pcre2_match, no JIT): `rc=-47` (PCRE2_ERROR_MATCHLIMIT): pcre2 also gives up on this subject.
So the default build gives up where the override answers (D158 shape holds). Note: pcre2 gives up too, so the answer is better than pcre2's, and the "D158 defect" is real but not a compatibility defect.
Consequence for the study: follows (the nullable decline is not a free dominance); it is a speed trade that can cross the give-up contract.

## PREMISE-2
Verdict: HOLDS.
Evidence: docs/design/memfn/r17b_prime.md (review tree) P1 row: "the trigger FIRES ON THE LETTER: KEEP loses 1.47 / 1.54 ns (3.4-3.8%) on two TUG g8 early cells ... Recorded as fired on the letter and NOT built (Q-R17P-28, the kit manager's call)"; Q-R17P-28 ANSWERED: "record P1 as fired on the letter, do NOT build it ... (it never fires on a default compile; D77)". Subject: Q1.4 item 1 (lines 161-162) "That conflict only arises at Q-WR-9's trigger (a TUG cell measured losing), and today's default is KEEP"; unlock (d)1 (line 321) and open point 5 (line 527) "resolve at Q-WR-9's trigger". `grep -i "fired|fires|Q-R17P-28"` on the subject: no hit, so the study never mentions the firing.
Consequence: follows as stated (the trigger is met on the letter, P1 deliberately unbuilt); it affects open point 5 and unlock (d)1, not option (d) itself.

## PREMISE-3
Verdict: HOLDS.
Evidence: src/facts/facts.c:324-328 `case PF_RUN_PIN: ... pcrec_run_pin(&pf->kset_walk, &pf->req_run, pcrec_find_byte_rate(cx), &pf->run_pin)`; src/facts/kset.c:294-306 `x = pos[pcrec_find_pick(rate, cand, NULL, nc, 0)];` (rate-based pick of which stretch is pinned). Subject §1.2 line 115 classes `run-pinned(-bounded)` as "F (run, pin, ...) ... no (rendering of the kit's pick)"; grep of the subject for run_pin/run-pin finds only that row, so the crossing list (crossings 1-7) lacks it. Second half: facts.c:310-318 req_landmark_maxoff = req_run.maxoff when run len >= 2, and req_run's window comes from req.c:764-782 `pcrec_find_run_window_start(rate ...)`; emit_dfa.c:8797-8799 `k = pcrec_fact_req_landmark_maxoff(cx); if (k < 0 || k >= PCREC_W_UNBOUNDED) return false;`. So the rate-pick flows into handoff validity. Both confirmed.
Consequence: follows (inventory incomplete, an eighth rate reader); the seam survives by the same restatement.

## PREMISE-4
Verdict: HOLDS.
Evidence: memfn/src/finder.c:335-339 row P2 "span 0's proof covers the span (identity, run_verified, or the density conjunct on the prior): dropped", basis FB_UNMEASURED_DEFAULT. src/gen/emit_dfa.c:8546-8555 `req_byte_dominated_by` ends `return pcrec_find_no_commoner(pcrec_find_byte_rate(cx), p, q);` (rate comparison). P0 undeniable: finder.c:330-333 "a REQUIRED span ... undeniable (D158)". emit_dfa.c:8492-8499 comment: pre-check is the NO-MATCH PROOF keeping `^([a-z]+)+@` from giving up.
Subject text (line 157-158) "The fold is itself a dominance (a folded pass costs nothing)" is about the target fold; the critic's reading (today's P2 includes a density disjunct) is accurate.
Consequence: follows as a supporting-claim correction; presence on/off is a price only for OPTIONAL spans (matches P0 undeniable).

## PREMISE-6
Verdict: HOLDS (scope caveat).
Evidence: docs/dev/decisions.md (review tree) heading "D161 addendum 14 — single-byte search sites move into the KIT's purview; the kit decides whether to scan at all" and its Reading: "the kit's candidate-finder table (add. 11) decides the form, including NOT pre-scanning at all"; clarification: pre-scan and candidate search are ONE request. Subject open point 1 (lines 515-518) names only D146, D161 add. 6 and Q-WR-9; add. 14 appears only at lines 118 and 354 (leak 2). Subject line 340 (S0 NO SEARCH) and line 122 put the no-search price on the backend side (B route consumer).
Caveat: add. 14's literal scope is single-byte sites (and the same-day clarification widens to presence+candidate as one request); the critic's "search at all vs not moves to backend" is the study's design, so the conflict is real but only for that population.
Consequence: follows (a fourth ruling to name in the addendum); does not change (d)'s shape.

## PREMISE-8
Verdict: PARTLY. Facts HOLD; "missing class" is overstated.
Evidence: src/core/compile.c:1358-1399 rungs `drop-anchored`, `drop-premul` ("measured ~1.27x"), `drop-handoff` ("measured up to ~2.5x more instructions"), `drop-prefilter` ("measured up to ~4x slower"): first-match order among strategy-dropping rungs with measured slowdowns, no price. The subject treats the ladder only as validity/late-fact source: line 47 "resource limit (DFA overflow, size caps)", line 258 "resource caps (overflow, size ladder)", line 54 "fits the existing retry ladder". It never says whether rung ORDER is a cost choice, so the critic's gap (cap = constraint, order = choice, unstated) is real; but the study does retain the ladder as the late-validity source (RECOMMENDATION front end: "Keep the build-and-retry loop"), so size is not wholly absent.
Consequence: a one-sentence scope declaration suffices; does not touch (d).

## PREMISE-10
Verdict: HOLDS.
Evidence: src/gen/emit_dfa.c:10869-10878 `cand_select_quiet`: only increments `pcrec_cand_trace_quiet` and rebases `cand_eval_base`; it runs `cand_select` with the same predicates. src/gen/emit_dfa.c:8612-8623 `req_set_leads_applies` calls `(void)pcrec_fact_req_set(s->cx)` "asked as a PASS here (the facts' `used` record ...)". src/facts/facts.c:128 `if (pass) pf->used |= pf_bit(f);` with the header comment (lines 14-20) that public accessors set `used`. `_stated` accessors exist (src/facts/facts.h:520-531). Subject lines 442-444: "Use the non-pass `_stated` accessors or the quiet walk". The quiet walk does not stop `used`; the argmin-evaluates-every-row point follows from first-match stopping at the first applying row.
Consequence: follows (Q6 stage-1 mitigation needs the `_stated` route and a design for non-consuming evaluation); a maintenance finding.

## PREMISE-12
Verdict: HOLDS (code reading; logic).
Evidence: subject lines 238-240 "That is exact: the minimum over a union is the minimum of the minimums, as long as every term that depends on the route sits inside that route's terms", and line 54. src/core/compile.c:1358-1399: the ladder's rungs (`.on = FIT_L_SIZE`, `.applies = fit_*_applies`) remove strategies when the emitted size is refused, so whether a (route, path) fits depends on the path chosen. The study states only the match-phase/validity-by-build qualification (reasons 1-3 at 244-252), not path-dependent size validity.
Consequence: follows as a qualifier on "exact"; supporting claim only.

## SIM-1
Verdict: HOLDS (magnitude is model-dependent; the structural point is independent of the model).
Evidence: re-ran verify/sim/sim.py on tests/findings/default_ppm.tsv: output byte-identical to the critic's sim_out.txt (diff empty, 282 lines). Independent few-line script (inline python reading the same default_ppm.tsv, own formulas for verify_cost and walk length) for window `ereh`: stop@1 `r` verify{0}: kit 20.9442, entries 3344.8 ppm, L 3.084; stop@3 `h` verify{0}: kit 21.1945, entries 3400.8 ppm, L 2.043. With per-entry 10.7 c/B (1070 in 1/100 cycle) x L the totals are 31.98 vs 28.63, as claimed. The first Pareto-dominates the second on (kit, entries), the second is 11.7% cheaper in total. Emitted DFA (verify/sim/probe/p14.c:186-196) does re-walk from a false candidate until `rx_forward_is_dead`; memfn/src/plan_cost.def:38-41 C_ENTER provenance "[OPT-3]'s measured 10.7 c/B times an ASSUMED ~2 bytes a false start survives".
Caveats: the walk length uses the critic's independence model; the critic itself notes real `ereh\w+` is a pinned run on main so the case is moot there, and the 3c population (no pinnable run) shows <=2.8% regret.
Consequence: follows qualitatively (Pareto prune on (kit price, entries) is exact only at equal per-entry cost, so "needs no number" does not hold across proof shapes); (d) not overturned.

## SIM-2
Verdict: HOLDS.
Evidence: sim_rerun.txt (identical to critic's): "exact frontier sizes: Pareto max 6, hull max 4; distribution Pareto [1, 3, 3, 3, 4 x17, 6]" over 22 sites; for `foo(bar|baz)+` the hull is PARKED + stop@3 verify{0} / {0,5} / {0,1,5} + stop@1 {0,3,5}; for `ab[0-9]+cd` stop@1 {0} / {0,2} / {0,2,3}: hull points beyond the first are deeper verify plans at one stop. Cites: memfn/src/window.c:394 `model_cost` includes `C_ENTER`; window.c:496 `if (nc >= cost) continue;` in the verify-depth loop. Subject line 312 "frontier size (expected 1-3, INFERENCE)" and line 514 "Keep every within-footprint method choice"; grep of subject for "C-model" or verify depth: none (only A-model in the T1 row, line 137).
Note: the frontier count depends on which dimension is counted (the critic enumerates hand-stated sites, 18 of the 22 not compiled), but 4 compiled-site counts (5,4,4,5) already exceed 1-3.
Consequence: follows (the 1-3 estimate is low; verify-depth choice moves to the backend unless the footprint definition changes; wording of the kit's role); (d) stands.

## SIM-3
Verdict: HOLDS.
Evidence: sim_rerun.txt "MARGIN-only flips": quick.*fox 0.996, GET /\S* 0.814, zq\d+x 0.882, Mozilla/\d 0.667, xyzzy\d+ 0.766 (5 of 22). memfn/src/window.c:669-683 `m_margin_holds` (RESEED wins only below half of PARKED); window.c:710 basis "ARGUED (offset_k_skip.md §4.5; ipv4's 1.5-1.6x inside the error bars)". Subject lines 168-170 "MARGIN 2/1 then has no role and is deleted" and line 309 "DELETES MARGIN 2/1". MARGIN guards model error, not consumer cost, so the frontier derivation does not remove its reason.
Consequence: follows (MARGIN's deletion is a separate decision, not a corollary); only the simplification credit is affected.

## SIM-4
Verdict: HOLDS.
Evidence: `$B -p rx --features all -o cat.c --pattern '\bcat\b'` (verify/w/cat.c): `RX_ENGINE "dfa"`, `RX_DFA_SCAN "cover"`; rx_search is one kit memchr+verify loop (word compares `rx_w2("ca")`, `rx_w2("at")`, boundary checks) and sets `capture_spans[0][1] = scan_position + 3`: no forward DFA, no reverse pass, no match phase. Subject Q2.2 (lines 236-240) charges `match_phase(rt)` per route outside the path min.
Consequence: follows (match phase must be inside the path for cover/rev-end); supporting claim only.

## SIM-6
Verdict: PARTLY.
Evidence: (a) HOLDS: measure_store/zen4-grid1/1/set.tsv (review tree), awk over the 68 data rows with 12+ columns: `noise_e6` (column 5) is "-" on all 68; the only noise-like rows are `kit.eps.ext.engine` 3820, `kit.eps.findall.l64k` 33650, `kit.eps.streamed.slope` 1730 (e6 ratios = 0.382%, 3.365%, 0.173%), regime-level, as the critic says. The subject itself lists the composite band as "Open (PS §7.3)" (lines 417-419). (b) re-ran part4.py (copied, with price_orig.py): output identical to part4_out.txt; Proxy A 1 of 10 tie, Proxy B 10 of 10, but Proxy B's x/2 rate error is the critic's own proxy, so "10 of 10" is conditional, not measured. (c) the 6-order demo reproduces (picks complex/mid/simple depending on order) but only for a running-best loop with a band-tie; the subject does not specify the loop, so the claim "never depends on evaluation order" is unproven rather than false (the two-pass rule fixes it).
Consequence: the rule as written lacks inputs and an algorithm (follows); the quantitative tie claims are proxy-dependent.

## SLOT-1
Verdict: PARTLY. The ruling reading HOLDS; "operative clause cut out" and "study never compares (a')" are overstated.
Evidence: docs/dev/decisions.md:9526 (Q-WR-9): "If it fires, the consumer's cost enters as a per-route MEASURED constant in the D166 set, never a pcrec price model, and add. 6 gets a dated addendum." D161 add. 11 (decisions.md ~9498): "no price model returns ... the only pcrec-side quantity is a MEASURED per-candidate fixed cost per route ... FILED, not built: trigger = a TUG cell measured losing". r17b_prime.md:787 P1 `priced` is a KIT row reading set quantity M23. So the ruled shape is: consumer cost as a set row feeding a kit decision; (d) has the backend decide, which Q-WR-9's "never a pcrec price model" does not pre-authorize. Subject Summary 5 (line 66) says "Q-WR-9 itself anticipated this" (overreach holds).
Against the critic: the subject's open point 1 (lines 517-518) DOES print the clause: "a dated addendum to D146 ..., D161 add. 6 and Q-WR-9 ("never a pcrec price model")", so the clause is not hidden, it is listed as needing an addendum. And option (a) (line 295: kit prices every strategy "given per-route consumer constants in the set") plus (c) "leaves A_entry inside the kit" cover most of (a'); what is missing is a row for "kit reads per-route A_entry as a set row for its own PARKED/RESEED, backend compares only vs no-search/reverse".
Consequence: the claim that Q-WR-9 licenses (d) does not follow; the addendum Frank is asked for is a reversal of a clause, not the pre-authorized one. Affects open point 1's framing, not (d)'s technical shape.

## SLOT-2
Verdict: PARTLY.
Evidence: D157 (decisions.md:9376) "any rule about which or how many positions to use is a method, and choosing methods is the kit's job"; D176 Q1 (decisions.md:9915) "'which stop, found how' is ONE priced choice in the kit's Table A over (alternative x stop position x find method)"; memfn/src/window.c:637-648 `wf_arows[]` = empty / parked / reseed / mass / floor. Under (d) (subject lines 296-300, 495) the kit returns options across footprints and the backend takes the argmin, so the PARKED-vs-RESEED alternative choice (Table A rows parked/reseed) leaves the kit, contradicting D176 Q1 as quoted. Subject open point 1 (lines 515-518) lists D146, D161 add. 6, Q-WR-9 only; grep shows no D176 Q1 addendum asked (D176 appears for Q2/Q4 only).
Not verified/arguable: that "render option k" is "pcrec naming a method". The options are kit-invented; selecting one by id is arguably selecting a fact-described plan, not carrying a method. The D176 Q1 conflict is solid.
Consequence: follows in part (a D176 Q1 / D172 addendum is needed that the study does not ask for); D157 violation is arguable.

## SLOT-5
Verdict: HOLDS.
Evidence: src/gen/emit_dfa.c:11828-11834 `typedef struct CandPath { bool body; CandRoute locate, finish; unsigned built, needs, members; unsigned asks[3]; const CandRow *recover; }` ("A value, recomputed per reader"); `cand_route_of` (3835, body route) and `cand_finish_of` (3846-3849: `fit.chosen == ENGM_DFA ? cand_route_of(cx) : CAND_ROUTE_VM`), CAND_PATH_READS at 9924. `grep -c "CandPath|cand_path_of"` on the subject: 0. The hybrid is a (locate, finish) pair (DFA/ATTEMPT body, VM finisher), but the subject lists S6 at line 346 as an inner strategy row while also routing it through `pf_admits[]` validity (line 220). The citation `emit_dfa.c:9845` for the route enum is off (also noted by PREMISE-11).
Consequence: follows (the argmin's output must BE CandPath or two path definitions coexist; S6 is route-pair level); supporting claim.

## SLOT-7
Verdict: HOLDS.
Evidence: src/opt/select_engine.c:496-500 `run_possessify`: `if (fit->chosen != ENGM_VM) return;`; :520-525 `run_revdet`: same guard; both called after the pick (select_engine.c:1475-1482, comment "the only steps here that need the engine ALREADY chosen"). `grep -rnE 'fit(\.|->)chosen' src/opt src/core --include=*.c | wc -l` = 30 (matches the critic's count, comments included). Subject Q2.4 (lines 283-285): the "prefer the DFA" rule "moves (logically) from `src/opt` to the backend"; the seam rule's clause 4 lets only rendering read a pick.
Consequence: follows (front-end AST transforms read the engine pick; no seam clause covers it).

## SLOT-8
Verdict: HOLDS (with the critic's own caveat).
Evidence: `grep -n '^- \[SEL-COST\]' docs/dev/plan.md` -> line 331 `STATE:not-started`; docs/dev/sel_cost_census.md:78-85 table: large-subject-throughput 80 cells, forced-VM wins (>1.03x) 10; short-subject-search 83 cells, 19. Subject line 235: "'prefer the DFA' is not proven. No cell is on record showing it wrong."; `grep -c SEL-COST` on the subject = 0. The census itself (lines 35-36) notes forced-VM "also disables the DFA prefilter", so the wins mix engine and prefilter choice, as the critic says.
Consequence: follows (the "no cell on record" sentence is wrong as stated and open point 4's trigger should cite [SEL-COST]); not (d)'s shape.

## SLOT-9
Verdict: PARTLY.
Evidence: HOLDS: D161 add. 6 (decisions.md:9471) "consumer price per route as DATA ... is withdrawn: hard to gauge, fuzzy to use, box-specific, and stale after every engine change", and the per-false-candidate cost "is removed by verification at the chain's last link ([KIT-VERIFY]) rather than priced"; D166 add. 2 (decisions.md:9740) staleness is keyed on "a measured form's (normalized) body", i.e. kit formhash (memfn/src/formhash.c exists), not pcrec engine bodies; the subject's answer (line 311) is about location only.
Contradicted: the inference that the frontier has more than one member "only on SUPERSET-span sites". The simulate critic's data (verify/sim/sim_rerun.txt, 22 sites incl. exact literal windows such as `foo(bar|baz)+`, `ab[0-9]+cd`) shows 4-5-member frontiers on EXACT sites, because today's kit verifies a chosen subset and leaves a residual entry rate (e.g. stop@3 verify{0} 146 ppm entries). So add. 6's premise (false-candidate cost removed by verification) is not what the shipped kit does (consistent with the study's own crossing 2: C_ENTER still live).
Consequence: staleness gap follows; the "population is superset-only, so (d) is small" corollary does not.

## SLOT-12
Verdict: HOLDS.
Evidence: subject line 102 `rev-end` LOCATE row class P with "no data"; line 456 "A slot is priced only when every row on it is measured"; line 453-454 Q6 stage 3 prices "LOCATE's `cover` vs `composite`" third; open point 6 (lines 529-530) "rank it UNMEASURED, and keep its first-match place". PR (git show lane/memfn-pricesurvey:docs/design/memfn/pricing_requirements.md): R1.1 puts T13 (reverse routes) in round 1; R4.5 "A term with no measured value ... makes its row UNMEASURED: declined, with that reason"; R1.2 "unpriced: first-match". The study defines no mixed-slot rule (where an UNMEASURED row sits relative to priced rows); R1.2 gives a reading that reconciles it, which the study does not adopt by name.
Consequence: follows (a declared mixed-slot rule is missing; stage 3's third step is not runnable as stated).

## SLOT-15
Verdict: HOLDS (design reasoning; not a probe).
Evidence: D158 (decisions.md:9391) "if the build with an optimization DENIED answers, the default build answers too"; src/gen/emit_dfa.c:9823-9831 `CG_FIXED` is declared per ROW ("must never move the give-up surface"), checked behaviourally by [GIVEUP-DIFF]. Subject Q5 item 5 (lines 423-425) frames it as "a cheaper path ... its fallback"; under an argmin the runner-up is set-dependent, so a set revision can move a pick between any two valid paths. The pairwise rule is not in the seam clause 1.
Consequence: follows (a D158 addendum / pairwise filter on the valid set is a missing requirement).

## SLOT-16
Verdict: HOLDS.
Evidence: D147 (decisions.md:9002-9003) "SIMD is a LAYER on top of the scalar algorithm and never a substitute for it"; "The scalar layer (the algorithm: what is searched, the plan, handoffs ...) must be the best it can be with SIMD OFF"; :9048 "What sits inside SIMD-on is the kit's choice, per site". D176 Q1 (9915): the SIMD layer "changes which methods are available, not their cost". The subject mentions the layer only as a Table B "layer flag" (line 138). Under (d) kit quotes enter the backend's cross-strategy argmin, so the SIMD-on best quote can flip the strategy; derivation is straightforward.
Consequence: follows (a D147 addendum / price-with-SIMD-off rule is needed).

## SLOT-17
Verdict: HOLDS.
Evidence: D146 (decisions.md:8995) "pcrec does no cost comparison and carries no architecture knowledge (Q12's refinement)"; Revisit-when (:8998) "a delegated site's kit code is measured worse than pcrec's pre-migration form and the kit cannot fix it"; Guard (:8997) "pcrec's own bench/alpha timings with the kit on vs off". Subject line 311 and open point 1 ask for the first half only ("pcrec does no cost comparison"); the backend's per-route consumer rows (subject lines 506-507) are box-specific architecture data.
Consequence: follows (addendum must cover both halves and say it is a new direction, not a fired Revisit).

## COST-1
Verdict: HOLDS.
Evidence: subject Q6 stage 3 (lines 449-453) orders "RETRY first (one prior comparison, small population); then FIRST/NEXT's handoff; then LOCATE's `cover` vs `composite`". Probes (verify/w/t1.c, t2.c): `[.,;]\d` and `[QXZ]{2}` both stamp `RX_DFA_SCAN "cover"`; SRS (git show lane/memfn-stopstudy:docs/design/memfn/stop_ranking_study.md line 480): `[.,;]\d` walk @0 6.9 -> 11.4 as the modelled cost. src/gen/emit_dfa.c:9007-9013 (handoff K admission comment): whether the jump "stops PAYING in time is UNMEASURED (the bench's per-cell timings are its test)"; emit_dfa.c:10087-10088 `cand_rs_dense_applies` is `cand_ppm x reseed_gap > 1000000`. The kit's 2026-10-31 notice (lane/memfn-wake1030 responses.md tail): "PRICING DIRECTION ... 'No search' becomes a ..." priced row, i.e. the same slot. Only LOCATE has named measured witnesses.
Consequence: follows (stage order is by population size, not measured need; D77); changes migration order, not (d).

## COST-3
Verdict: HOLDS.
Evidence: src/gen/memfn_sites.c:975-996 `pcrec_memfn_art_end`: `consulted` comes only from `mf_art_end`; `cx->job->meas_consulted` otherwise unset (comment: "no routed finder row reads a set key, so it reads 0 today"). docs/spec/measures.md:155 [4¶2] "A reader is pcrec's own (none exists today) or the search-code kit's ... A key looked up and not found still consults" and [4¶4] "No kit row reads a set key today, so every artifact's stamp is `""`". Probes: `abc`, `a+b`, `[.,;]\d`, `foo(bar|baz)+`, `xy\d+z` all emit `#define RX_MEASURES ""`. So a shadow that reads a set row (consumer card) would be the first pcrec reader and would flip the stamp unless it reads through a non-consulting path (none exists in the code read). memfn/src/window.c:1596 still reads `COST(HORS_MIN)` (live), consistent with the critic's "kit rows read plan_cost.def, not the set".
Consequence: follows (stage 1's "byte-identical" needs a third hazard named).

## COST-5
Verdict: HOLDS.
Evidence: memfn/src/window.c:1003-1021: `d->ch` is set from the M-table result (`M_MARGIN` -> RESEED row, `M_PARKED` -> PARKED row, else 0); `wf_mtable` rows M_ONE/M_MARGIN/M_PARKED at :703-712. Deleting MARGIN while the kit still picks leaves `na == 2` sites to `M_PARKED`; the five MARGIN movers from sim_rerun.txt are exactly those flips. Subject Q6 (lines 428-460): stages are shadow / census / replace slot family / delete first-match; neither MARGIN's deletion nor the kit reply change appears in any stage.
Consequence: follows (ordering gap; reply must be additive until the last slot is priced).

## COST-9
Verdict: HOLDS.
Evidence: measure_store/zen4-grid1/1/set.tsv (review tree): `noise_e6` column is "-" on all 68 data rows (awk, same count as SIM-6); only `kit.eps.*` ratio rows (3820 / 33650 / 1730 e6) carry noise-like data. docs/design/measure_sets.md ~946-950: "No provenance columns. `abs_ns_e6`, `noise_e6`, ... are pcrec's listing's ... No selection reads noise today." docs/spec/measures.md:141 [3.3¶1] `values_digest` covers key, unit, status and value_e6 only, "no provenance column", so two sets differing only in `noise_e6` share the stamp. Subject Q5 item 4 (lines 417-419) proposes a DERIVED root-sum-of-squares band; the independence objection (terms measured relative to one unit row share noise) is analytic, not tested here, but the missing inputs and the digest gap are checked.
Consequence: follows ("derived, never a constant" has no inputs today; the band is a disguised constant until noise_e6 is populated).

## COST-11
Verdict: PARTLY. (a) HOLDS; (b) and (c) NOT VERIFIED (analytic suspicions).
Evidence: (a) subject lines 449-455 name `[.,;]\d` and `[QXZ]{2}` (SRS §5.1) as the S3 witnesses that motivate stage 3 and then call the stage-3 check "a timed held-out regret run with the SRS §5.1 witnesses"; PR R6.2 (pricing_requirements.md): "a site used to diagnose a term moves to the card's measurement set and is replaced in the validation population". (b) same-box/same-harness dependence and (c) the authored byte-rate prior shared with the bench subjects are plausible (subject itself cites PS "AUTHORED" prior) but nothing was re-measured here.
Consequence: (a) follows (acceptance set mislabelled held-out); (b),(c) are risks, not shown failures.

## VERIFY COMPLETE
Counts over the 28 findings: HOLDS 22, PARTLY 6, REFUTED 0, NOT VERIFIED 0 (as whole findings). PARTLY: PREMISE-8, SIM-6, SLOT-1, SLOT-2, SLOT-9, COST-11 (PREMISE-1 holds with a pcre2 note: pcre2 also gives up, rc=-47). No finding changes option (d)'s shape; SLOT-1/2/9 and PREMISE-6 bear on the ruling framing of open point 1.
