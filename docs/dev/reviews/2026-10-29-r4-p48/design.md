# CRITIC design — p48
## Findings

### DESIGN-1 Row 4's byte-prior price declines the context runs the relaxation is said to enable (§5's own argument applies to row 4)
- status: CONFIRMED
- severity: design
- effort: M      blast radius: TABLE row 4, RELAX's role as D161 add. 17's enabler, Q3, the census "priced in" counts
- where: RELAX + TABLE; subject lines 73-83 (§5), 379-385, 426, 432-436, 681-694
- claim: The doc proves (§5, lines 73-83) that a context-blind byte prior cannot do admission, because it is wrong exactly where the pattern's context sets the run. It then gives row 4 that same prior as its admission price, on the grounds that split-exit loops are "dominated by restart loops whose context is the byte itself" (line 435). But uniform-vs-split exit is not the same boundary as context-vs-unconditioned. A context run gets a split exit as soon as the pattern names its terminator. Under the default prior (findings `default`, recomputed from src/core/findings_table.inc), row 4 declines:
  - `\d+-`, which line 380 lists as what the relaxation admits: p(\d) = 0.075, E[k] = 0.08;
  - `foo[a-z]*bar`'s `[a-z]*`, also listed at line 380: p = 0.663, E[k] = 1.97 < 2.3;
  - `id=\d+;`, a one-state split-exit digit run after a literal context, the same shape as hex-after-`0x`. The review binary stamps `RX_DFA_SCAN_EDGE "none"` on it today, so row 4 is its only route to an edge.
  Under `-e utf8` the byte-rate answer is NONE (findings.md §2 paragraph 7), so row 4 is transparent and declines every split-exit loop. D161 add. 17 calls this relaxation the thing "that makes T3's inner runs fast". A landmark-seeded reverse DFA's inner run (`[\w.$]+` before `(`) is by construction a context-conditioned run, the case §5 says the prior gets wrong.
- evidence / repro: masses via `python3 -I` over findings_table.inc counts_0: \d 0.075; [a-z] 0.663; [\w.$] 0.817; [^\]] 0.998. The threshold k*/(1+k*) = 2.3/3.3 = 0.697. `$B -p rx --features all --pattern 'id=\d+;'` gives `"none"`.
- proposal: Price row 4 on what actually separates the trivia, which is STRUCTURAL: a restart loop is a self-loop whose set is a literal byte of the pattern that re-enters a partial-literal state (`oodo`'s `o`). Decline that shape by a structural row and admit the rest as row 3 does (insurance, bounded F). Alternatively, keep the prior-priced row 4 but drop "enabler" from the claim and state the utf8 and low-mass-context exclusions as its known misses. Either way, correct line 380's examples.

### DESIGN-2 Row predicates 3/4 omit soundness gates the code and the corrected twin rely on: (6), (8), the END-view member clause, and the s0 unanchored-wrap refusal
- status: CONFIRMED
- severity: design (as written: loud refusals per run 500 and wasted slots on s0, not wrong answers)
- effort: S      blast radius: TABLE rows 3-4; the build's row text; S213-style sabotage rows
- where: TABLE; subject lines 425-426 vs 301-304, 358-372; scanedge.c:396-412 (s0 refusal), :399 `prefilter_reseeds && seedtgt` (8), :365-395 (6), member_ok :271-279
- claim: Row 1 says "(1)-(8)". Rows 3 and 4 say only "(2), (3); (7)". The doc's own run 500 shows that dropping (8) for the new heads is a loud internal error on every `\b`/`\B` shape, and the corrected twin (503) keeps (6) and (8). Neither row's predicate says so. Rows 3 and 4 also omit the `s == d->s0 && !a` refusal (scanedge.c `collect`, the "unanchored wrap's own" shape). Every unanchored forward machine's s0 is a NON-accepting one-state self-loop with SPLIT exits (it stays on non-candidate bytes and leaves to several states). Row 4 as written ("one-state self-loop with ANY exits") therefore matches s0 on every unanchored machine, and spends a slot re-skipping bytes the candidate prefilter owns. A first-match table whose row text is not the whole predicate keeps the rest of the predicate in a second slot (`collect`'s `continue`s). That second slot is exactly where the next relaxation will forget it.
- evidence / repro: subject line 425 `| 3 | self-loop | ... (2), (3); (7) at selection |` and line 426 `| 4 | split-exit | ... (2), (3); (7); AND priced in |`. Code: scanedge.c `if (s == d->s0 && !a) continue;` inside the unbounded form; `if (prefilter_reseeds && seedtgt[s]) continue;`; the `viewtgt[s]` trim block.
- proposal: Split the predicate into one slot for soundness (`eligible(state)` = (2), (3)/END-view, (6), (8), the wrap refusal, (7) at selection), ANDed by every EDGE row, and the rows, which hold only POLICY (shape and price). The listing ([LIST-TABLES]) then shows both.

### DESIGN-3 The measurement card collides with the committed set's existing `beta`/`f`/`xover` cards (measures.md §2.2¶2); k* is already a family row, `kit.xover.<form>.WALK.<kind>`
- status: CONFIRMED
- severity: design
- effort: S      blast radius: TABLE (card `kit-advance@1`), rows 2/4's key spelling, the kit's card ledger
- where: TABLE / card; subject lines 612-632; measure_store/zen4-grid1/1/set.tsv section `cards` (rows 25, 30, 34) and rows 37-104; docs/spec/measures.md [2.2¶2]
- claim: The card declares `kit beta 1` with dims `form; dispatch; dir`, `kit f 1` with dims `form; dispatch; dir`, a derived `xover.ADVANCE.<form>.<dispatch>`, and a NEW pcrec quantity `walk`. The default set (DEFAULTS: `idk zen4-grid1@1`) already holds `kit beta 1 form;kind;shape`, `kit f 1 form;kind;lenclass` and `kit xover 1 form;vs;kind`. Its derived rows `kit.xover.{A1,S1,V1}.WALK.DFA_SCAN` are this same quantity: f/(1-beta) against the walk, in walk-bytes. The unit row the card's `walk` cites (`kit.beta.WALK.DFA_SCAN`) is that set's own `beta` row. [2.2¶2] says "A set holds at most one card per owner.quantity", so the card cannot be "added to the canned grid" as written. Its derived key also has the wrong token order for the `xover` card (`form;vs;kind`). The design restates an existing family under new names, which puts one fact in two slots.
  A second slot issue: `dispatch` (EDGE sentinel vs STAY `state == X` compare) is pcrec's own loop scaffolding, not a kit form. Measuring it under a KIT card puts a pcrec method fact into the kit's row, against D146/D157's direction (pcrec states facts, the kit owns forms). Its cost belongs with pcrec's `walk`-side rows.
- evidence / repro: `grep -n '^kit	\(beta\|f\|xover\)	' measure_store/zen4-grid1/1/set.tsv`; measures.md:83.
- proposal: Make ADVANCE a new `kind` value of the existing cards: `kit.beta.<form>.ADVANCE.<shape>`, `kit.f.<form>.ADVANCE.<lenclass>`, and k* = `kit.xover.<form>.WALK.ADVANCE`, with direction as a shape/kind token if the kit wants it. Put the STAY-vs-EDGE dispatch overhead in a pcrec-owned quantity. Row 2/4's "k* from the loaded set" then reads an existing derived-row family and needs no new card.

### DESIGN-4 "Ranking by prior mass can only reorder; it cannot decline a measured win" is false at a 4-slot cap, and the key orders the measured wins last
- status: CONFIRMED
- severity: speed / design
- effort: S      blast radius: TABLE (cap ranking), chain_cmp in scanedge.c
- where: TABLE; subject lines 441-448; scanedge.c `chain_cmp` + the `nedges < SCAN_MAX_EDGES` loop; limits.def:395
- claim:
  - At a cap, a reorder IS a decline: the 5th-ranked edge is not emitted. The doc's own census counts this ("displaced a HEAD edge at the 4-slot cap": 2 corpus, 3 bench, line 584).
  - The proposed key is the default byte-rate mass, and it ranks the two measured wins below every row-4 edge. `\s` has p = 0.138 (0.128 without `\n` under D164's lowering) and hex has p = 0.305, while every row-4 admit has p ≥ 0.70 by construction. So the refinement drops `\s+$`'s x0.29 edge before any priced-in edge. That is the outcome G2 (the top goal) forbids, produced by the very prior §5 disqualified.
  - Under `-e utf8` the key is NONE (findings.md §2 paragraph 7). The design does not say what ranks then, a presumed value that the no-silent-defaults rule forbids.
  - The doc says the ranking "matters only once the relaxation lands". Changing it now has no measured need (D77).
- evidence / repro: masses recomputed from findings_table.inc (above). Census line 584. `chain_cmp` today: unbounded, then nmembers, then head index.
- proposal: Do not use the prior in the ranking. Rank row-4 (relaxed, priced) edges AFTER every edge today's walk admits (rows 1 and 3, kept in today's `chain_cmp` order), so the relaxation can never displace today's population. This is the declared-table spelling, and it needs no data. Revisit with a measured case of more than 4 unbounded candidates (trigger: the census's displaced-at-cap count on a bench cell).

### DESIGN-5 The STAY premise is false: "192/256 is a cardinality version of the same inequality", and "M2.10's regression is what the inequality predicts"
- status: CONFIRMED
- severity: design
- effort: S (text) / M (if Q4 is built on it)      blast radius: STAY, Q4, the future priced STAY row
- where: STAY; subject lines 241-243, 469-471, 695-701; emit_dfa.c:5063-5120 (`pick_skip_states`, `bestcnt = 191`); decisions.md D13
- claim: Three separate failures:
  (a) The two criteria disagree in BOTH directions on ordinary sets. Under the default prior:
    - `[^a-z]` has 230 bytes and p = 0.337, and `[^\w]` has 193 bytes and p = 0.193. The stay rule admits both, and the inequality (p > 0.70) declines both.
    - `[0-9a-z]` has 36 bytes and p = 0.738. The inequality admits it, and the stay rule declines it.
    So retiring 192 "into the same priced row" is a policy change with movers both ways, not a re-spelling.
  (b) The cost models differ. A STAY is a `state == X` compare at EVERY loop top, in every state (a per-iteration tax on the generic path). It is not a per-entry F. The doc's own card says so (line 631-632: "so the generic-path compare cost of STAY is in the row and not assumed zero"), which contradicts Q4's "it is the inequality p > 0.70 with a uniform prior".
  (c) D13 records the M2.10 regression as follows: a REVERSE skip table on a state that "stays on 100% of the bytes that pattern can ever see", with "Mechanism unknown and deliberately left so rather than guessed at". A context-blind prior that "predicts" it does so because {0,1} has a low unigram mass, which is the §5 failure mode. That is not a confirmation of the inequality, and it contradicts a ruled D-row's recorded state.
- evidence / repro: masses from findings_table.inc. emit_dfa.c:5069 `int best = -1, bestcnt = 191;`. D13 text quoted above.
- proposal: Strike the equivalence claim and the M2.10 sentence. Q4's priced STAY row stands on its own card and measurement (which is the doc's leaning anyway), with D13's "do not re-attempt without measuring the REVERSE machine" as an explicit precondition.

### DESIGN-6 G2, the top-priority goal, fails on the design's own HEAD numbers
- status: CONFIRMED
- severity: doc
- effort: S      blast radius: Goals; the entry-rule build's acceptance check
- where: Goals; subject line 395-396 vs table line 151 and Summary line 63
- claim: G2 requires `\s+$` "at ≤ 0.35x of pre-SET instructions on `t-trim-match-60k`". The table gives set 369k against single 922k instructions, which is 0.400x. The 0.29x figure is CYCLES (120k/412k). The Summary itself says "−60% instructions, x0.29 cycles". A builder checking G2 as written sees red on today's HEAD and on the `ng` twin (369k), so the top-ranked goal cannot pass for any design. The ranking G2 > G1 is otherwise served: the entry rule leaves `\s+$` (row 3, no entry jump) unchanged.
- evidence / repro: 369/922 = 0.400; 120/412 = 0.291.
- proposal: Restate G2 as "≤ 0.35x of pre-SET cycles", or as "≤ 0.45x instructions", or name both with their own bounds.

### DESIGN-7 The entry rule keys on a PROXY (`scan_span > 0`) for "this head's class cells were killed"; the fact then lives in three slots, and one named site has a second reader the rule must not touch
- status: CONFIRMED (slots, second reader); SUSPECTED (whether the twin narrowed `dfa_start_is_scan_head`, because the patch is in denylisted evidence)
- severity: maintenance / design
- effort: S      blast radius: ENTRY; scanedge.c's kill loop and (8); emit_dfa.c's entry sites; tuning.md §2.18¶3
- where: ENTRY; subject lines 341-348, 450-454; scanedge.c:711-713 (`if (ch->span > 0) ... hd->tr[c] = -1`); scanedge.c (8) `prefilter_reseeds && seedtgt[s]`; emit_dfa.c:12872-12898, :12920, :12982, :13059, :13705-13706, :13768
- claim:
  - The dispatch exists for one hazard: a state installed onto a head whose class cell is DEAD. The pass decides that kill at scanedge.c:711 (`span > 0`). The entry rule re-encodes it as "bounded head" in the emitter. Precondition (8) guards the same hazard for the mid-body reseed, and its rationale is false for unbounded heads by the doc's own argument (lines 299-304). After the build, three slots hold one fact under two different answers. A future change to the kill (period-k chains, which scanedge.c:695-703 anticipates, or killing an unbounded head's cell to share the sentinel) would silently desynchronise the entry rule, and a desync here is a miscompile, not a refusal.
  - The doc names `dfa_start_is_scan_head` among "the four sites" (lines 341-343, 450-452). That function has a SECOND reader, `s0head` (emit_dfa.c:12920), which decides whether the candidate prefilter sits on the generic path or the edge path (:12982/:13059). STEP 1.1's comment at :12866-12871 split exactly these two questions apart. Narrowing it to `> 0` would move the prefilter for an unbounded s0 head. That is harmless only because an unbounded s0 head is accepting and so has no candidate prefilter (probed: `[a-z]*`, `x*`, `[^,]*,?` all stamp `RX_DFA_PREFILTER "none"`). That is a coincidence, not a derivation.
  - Mover class: constant-seed s0 unbounded heads emit an UNCONDITIONAL `goto ..._scan_edge; // the start state carries a scan edge` (probed: `[a-z]*`, `x*`, `[^,]*,?`, `(?:ab)*[a-z]*`, forward and anchored). The rule removes these too. The doc describes its movers as "seeded unbounded heads" and lists `x*` among them (line 589-590), but `x*` is not seeded. The abi reader grep must cover both entry-line spellings.
- evidence / repro: `$B -p rx --features all --emit-main -o x.c --pattern 'x*'` gives line 101 `goto rx_forward_scan_edge;   // the start state carries a scan edge`. For base10num: line 181 `if (rx_forward_is_stop(...) && !rx_forward_is_dead(...)) goto rx_forward_scan_edge;   // seeded straight onto a scan-edge head`.
- proposal: Have scanedge.c record the kill as the fact (e.g. `DState.scan_kills`, set where the cells are killed, or derive it from `tr[head][scan class] != head`). Have the entry dispatch (`dfa_seed_can_be_scan_head` and the two revend writers) and, when its widening is taken, (8) read THAT. Leave `dfa_start_is_scan_head` unchanged for `s0head`. The rule then reads "dispatch iff an entry state has a killed cell", which is the question itself and not its current proxy.

### DESIGN-8 Rows 2 and 4 hold the E[k]-vs-k* price twice, with two different "missing" verdicts, and the card text names the wrong row
- status: CONFIRMED
- severity: design / doc
- effort: S      blast radius: TABLE rows 2-4; the card's trigger; Q3's build order
- where: TABLE; subject lines 424-426, 615-616, 523-531, 692-694
- claim:
  (a) Row 2 (`priced-out`) applies to every one-state self-loop, with "a run estimate E[k] the row trusts", and it names the source only for uniform-exit loops (`run-rarity`). Row 4 prices split-exit loops by "E[k] ≥ k* from the byte-rate prior". If row 2 trusts the byte prior for split-exit loops, then row 4's price clause is unreachable (anything that reaches row 4 has already passed `E[k] ≥ k*`). If it does not, row 2's applicability text is wider than its effect. Either way, the comparison `E[k] vs k*` has two slots, and the per-shape estimate source is spread across them.
  (b) "Transparent" means two opposite verdicts. With k* or the estimate missing, row 2 falls through to row 3 (ADMIT), and row 4 falls through to row 5 (NONE). The default set (`zen4-grid1@1`) holds no ADVANCE row (`grep -c ADVANCE` = 0), so k* is missing today. Every compile without a re-measured DEFAULT set therefore declines every split-exit loop. The relaxation that Q3 lands "IN the P1/T4 build" is then INERT until the card is measured and the DEFAULTS row moves. That is a build-order dependency (the card before the enabler) that Q3 and bench ask (c) do not state; ask (c) says the card is "owed only when row 2's or row 4's trigger fires".
  (c) Line 615-616: "It is added to the canned grid when row 3's trigger fires. Until then the rows are UNMEASURED and row 3 is transparent." Row 3 reads no data (line 525: "Rows 0, 1, 3 and the entry rule read no data"), so the reference must be to row 2 or row 4.
- evidence / repro: subject quotes above; measure_store/DEFAULTS gives `idk zen4-grid1@1`; the set has no ADVANCE key.
- proposal: One priced column per one-state row, `{estimate source; verdict when the price is missing}`: row 3 = {run-rarity; ADMIT}, row 4 = {byte-rate; NONE} (or the structural row of DESIGN-1). Delete row 2 as a separate row. Fix "row 3" in the card. State in Q3 that the card's measurement and a DEFAULTS move come before (or within) the P1/T4 build, or the enabler does nothing.

### DESIGN-9 The break-even's linear model does not fit its own stated crossing; E[k] ≥ k* is exact only for linear Δ
- status: SUSPECTED (the raw rows are in denylisted evidence)
- severity: doc
- effort: S      blast radius: TABLE threshold 0.70; the card's derived row
- where: TABLE / break-even; subject lines 64-70, 217-231, 236-240
- claim: With F = 14 and g = 13.0 − 7.1 = 5.9 (shape A), Δ(k) = F − k·g gives Δ = +2.2 at r = 3 (k = 2) and Δ = −3.7 at r = 4 (k = 3). The table says the crossing is "r = 4 (105 = 105)", i.e. Δ(r=4) = 0. So the short-run per-byte gain is smaller than the long-run slope (or F is larger than the r = 1 figure), and the measured crossing is k = 3, which is threshold p = 0.75 rather than 0.70. With nonlinear Δ, the admission test must be E[Δ(k)] < 0 over the run-length distribution, not E[k] ≥ F/g on the slope. Under a geometric run at p ≈ 0.7, ~30% of entries have k = 0.
- evidence / repro: the arithmetic above, from subject line 219. Confirm from `breakeven_measure.txt`'s r = 1..6 rows.
- proposal: Let the card's derived row be the measured crossing over the run-length grid, not f/(1−beta) from the slope. Or state the threshold as a band (0.70-0.75 in instructions, about 0.5 in cycles) and note that no row reads it until the card is measured.

### DESIGN-10 SCAN_SITE_ROWS is the third member of an undeclared family: "which loop form runs a self-looping state", today split between `pick_skip_states` and scanedge.c's ranking, with two caps, two rankings and two thresholds
- status: CONFIRMED (the family exists); proposal is design
- severity: design
- effort: M      blast radius: STAY + TABLE (Q4's end state); `pick_skip_states`; `chain_cmp`; limits.def
- where: STAY / TABLE; emit_dfa.c:5063-5120 (`int out[4]`, `bestcnt = 191`, ranked by stay CARDINALITY, excludes `scan_span != 0`); scanedge.c `chain_cmp` + `PCREC_MAX_SCAN_EDGES` (limits.def:395, "awaiting a measured re-choice"); measure_store `kit.xover.<form>.WALK.DFA_SCAN` (the kit's priced crossover family); decision_families_survey.md has no row for it (§3.1-3.14 checked)
- claim: For the same population, the self-looping states, two selectors each pick "up to 4". The stay selector ranks by uniform-prior mass (byte cardinality, with an unregistered literal floor of 192). The edge selector ranks by run shape, and the design proposes adding byte-prior mass as a key. A structural exclusion links them (a head is never a stay). That is two rankings over one budget question, and the design's own end state (lines 469-471, Q4) is one table deciding the dispatch. The survey's "propose unification at ~3 members" mark is reached: stays, edges, and now the priced/relaxed edge row. The crossover the priced rows read is the kit's existing `xover` family (DESIGN-3).
- general form: a per-state first-match RUN-LOOP FORM table over `{walk, STAY, EDGE-bounded, EDGE-unbounded}`. Rows declare a soundness slot (DESIGN-2) and a priced column that reads `kit.xover.<form>.WALK.<kind>`, under ONE cap whose value is a limits.def row with its measurement. The entry dispatch and (8) read the kill fact the table's EDGE rows produce (DESIGN-7).
- unlocks, each with its trigger:
  1. retire the 192 literal and the `out[4]` literal into rows. Trigger: the card's STAY-dispatch rows are measured (Q4).
  2. the utf8 class-run edge that sel_cost.md bucket B names as absent (`\p{L}+` utf8, VM x3.08 inside runs). Trigger: [OPT-3-RUNEND] (a) or a utf8 run cell on the bench.
  3. the VM's cursor rung (decision_families_survey §3.5's `vm_rung_of`) reading the same `xover` for its own run loops. Trigger: §3.5's table being built.
  4. the reverse-DFA tiers (D161 add. 17) admitting T3 inner runs through the same table, rather than through a row-4 prior. Trigger: the P1/T4 build.
- proposal: Do not build any of this with the entry rule (D77; the entry rule is independent). File the family under the survey (a new §3 row) so that Q4 and row 4 land INTO one table rather than as a third selector.

## PROBED-AND-HELD
- base10num premise: at 02a054851 the review binary stamps `RX_DFA_SCAN_EDGE "mixed"` and emits the conditional `seeded straight onto a scan-edge head` entry (line 181). `\S+@\S+`, `0x[0-9a-fA-F]+` and `\s+$` stamp `"bitmap"`. Held.
- "An unbounded head's cells are never killed": scanedge.c:711 `if (ch->span > 0)` guards the kill loop. Held. The ENTRY soundness argument (generic step from an unbounded head lands on the head, then `is_stop` routes to the edge path) holds on reading `emit_scan_loop`. Accept probe, prefilter placement, stay exclusion and view select are all unaffected for a non-s0 head. Held, with DESIGN-7's caveat on `s0head`.
- The cited code did not move: `dfa_start_is_scan_head`, `dfa_seed_can_be_scan_head`, `s0head` and both revend `entry_head` writers are present with the same bodies at b05ccfc0b and 02a054851. The diff to emit_dfa.c is 39 lines elsewhere, and there is no scanedge.c or limits.def diff. Held.
- Prior masses (recomputed from findings_table.inc `default`): [0-9.+-] 0.090; [0-9] 0.075; \S 0.862; hex 0.305; \s 0.138 (0.128 without \n); `o` 0.050 (the doc says ≈0.04). E[k] = p/(1−p) values match. Held.
- Threshold arithmetic: k*/(1+k*) = 2.3/3.3 = 0.697 and 1/2 = 0.5; k* = 14/5.9 = 2.37 and 17/6.9 = 2.46. Held, modulo DESIGN-9.
- Census arithmetic: 295+2 = 297; 144+10 = 154; 2533+500+248+9 = 3290; 80+41 = 121. Held. One wording slip: "roughly a fifth reverse" (line 600, which is the corpus figure, 18/84) and "a third of them reverse" (line 690, which is the combined figure, 46/153) describe different populations. Doc-level only.
- (8)'s emitter re-derivation exists (emit_dfa.c:12752 "edge and is named by seed family ... prefilter reseeds"), as the doc says for run 500. Held.
- The 192 floor is unmeasured and unregistered: it is a literal (emit_dfa.c:5069 `bestcnt = 191`) and not a limits.def row. Held, as the doc says ("an unmeasured constant").
- D80 / D94 / D76 for the entry rule: tuning.md §2.18¶3 states the entry dispatch ("The loop's entry asks the same question once per search..."), so a spec hunk is owed, and the doc says so. Removing the line is an emitted-text change, so it is an abi event, and the doc says so. Held (see DESIGN-7 for the second entry-line spelling the reader grep must cover).
- D77: the entry rule answers a measured loss (bench x1.20, twin +18.6% instructions), so it is built under measurement. Held. The ranking refinement has no measured need (DESIGN-4).
- D146/D157: no new kit fact for rows 0/1/3/5 or the entry rule. Held (`edge_advance`/`stay_advance` exist at emit_dfa.c:12490/9148). The card's `dispatch` dimension is the exception (DESIGN-3).
- D161 add. 17: the doc agrees that the relaxation is the T3 enabler and is direction-agnostic. The conflict is in its PRICE (DESIGN-1, DESIGN-8b).
- One-pass loss rule: the doc applies it only to the near-noise residual (+1.0%/+0.8%) and to cls-s-uc's shape question after one bounded effort. That is consistent with the rule. Held.
- Goals: G1 is checkable and met by the doc's numbers (ng vs single: +1.0%, −2.4%, +0.75%). G2 is mis-stated (DESIGN-6). G3 is not advanced by the entry-only build, which is fine, but the ranking and STAY plans risk a third selector (DESIGN-10). G4 is contradicted by a prior-keyed ranking (DESIGN-4) and by two missing-price verdicts (DESIGN-8). The stated order G2 > G1 > G3 > G4 is otherwise respected by the entry-only leaning.
- GAP: D153 (remodel overlap with in-flight emit_dfa.c work) cannot be checked without docs/dev/optloop/, which is denylisted. The census and break-even raw rows (p48_evidence/) are denylisted, which is why DESIGN-9 is SUSPECTED and the census mover-class question in DESIGN-7 is unverified.
