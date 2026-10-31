# crit-pricing-split, lens COST (cost and overlap + measurement), 2026-10-31

Subject: docs/dev/lanes/splitstudy_report.md @ 70464e9a3 (snapshot read). Base: main a3cc4de82, review tree
worktrees/crit-pricing-split. Denylist: no denied file opened (docs/dev/lanes/ not read at all). Read-only;
a few compiler probes (artifacts under cost/), no make, no gcc.

Cites checked against the review tree: cand_rows[] 51 rows at emit_dfa.c:10154 (counted: 51), cand_nodes 9930,
cand_select_quiet 10869, req_landmark_admits 9016, cand_rs_dense_applies 10087, req.c:764-830, window.c:669-683,
facts.c:128 (`pf->used |=`). All match. No cite finding.

## Findings

### COST-1  Stage 3 orders the slots by "small population", not by measured need (D77)  [design, CONFIRMED]
- Study: Q6 stage 3 ("RETRY first, one prior comparison, small population; then FIRST/NEXT's handoff; then
  LOCATE cover vs composite"); Summary 5.
- The only measured loss the sources name is LOCATE's: `cover` is first-match and never priced against the
  composite DFA scan (PS C6; SRS 5.1: `[.,;]\d` 6.9 -> 11.4 instr/B, `[QXZ]{2}` 6.3 -> 11.3). Probe:
  `$B -p rx -o t1.c --trace --pattern '[.,;]\d'` -> `#define RX_DFA_SCAN "cover"` (t1.c:23). Frank's 2026-10-31
  notice ("no search becomes a priced row ... amends D176's shape") names the same slot.
- RETRY (R4 `cand_rs_dense_applies`, emit_dfa.c:10087-10088) and the handoff K admission (9016-9025) have NO
  measured mispick on record. The K admission's own comment (9013-9015) says whether it pays in time is
  "UNMEASURED (the bench's per-cell timings are its test)"; R4's `gap` is a measured crossover
  (emit_vm.c:11088 `vm_reseed_cal`, {16,4}) beside three CHOSEN settings (block, cap, first) the price would not
  touch. The study's unlock 4 gives R4 a trigger only AFTER RETRY is priced. So RETRY first builds ahead of a
  measured need, and needs a `reseed_gap` set row that does not exist (68 rows, none engine/reseed).
- Costlier-must-prove-more: the cheap, triggered first step is "the old/no-search path as one priced row in
  LOCATE (cover vs composite) plus the per-route no-search card". The path argmin over FIRST/NEXT/RETRY, the
  frontier reply and the MARGIN/C_ENTER move have no trigger of their own in the study's text.
- Changes the recommendation? It changes the MIGRATION ORDER and what counts as "the build", not the target
  shape (d). Fix: stage 3 starts with LOCATE (trigger: the S3 witnesses, measured); the rest filed with named
  triggers (D77).

### COST-2  The study gives no cost per change; here is the list with sizes read off the code  [doc/design, CONFIRMED]
Columns: change, sites in the review tree, size, what it buys, trigger named by the study (N = none).

| # | change implied by (d) | sites | size | buys | trigger in study |
|---|---|---|---|---|---|
| 1 | strategy (path-family) table + path argmin beside cand_rows[] | emit_dfa.c: 51 rows, 241 CAND_SLOT_ refs, 16 `wr` readers; new table, enumeration, simplicity order | large: a new mechanism in a 16k-line file; counterfactual reads (COST-6) | priced LOCATE/NEXT/FIRST/RETRY | LOCATE yes (COST-1); others N |
| 2 | 7 predicate splits | presence fold (`dominated`), `offset-set` reseed, K admission, R4, `next_key_holds`, req.c picks; crossing 6 is the whole strategy/rendering split | medium each, 3-4 predicates deep | removes price-in-validity | N |
| 3 | fact hand-over (spans, entry kinds accepted, route validity) | rides [MEMFN-UNBOUNDED-SPANS] (not-started) | one MF_SITE_ABI event, already planned | presence as span | row exists |
| 4 | rate-pick retirement | req.c:764-830; 26 readers of req_run/req_byte in emit_dfa.c; spec findings.md rows 109-110; stamps `<PREFIX>_REQ_BYTE`, `REQ_RUN @idx` (caller-visible); -fno-req-byte / -fno-req-run | medium-large: stamps + two deny flags change meaning (abi + spec hunk, D80) | D157 purity | belongs to UNBOUNDED-SPANS, not this migration |
| 5 | kit reply = frontier + components + set id | memfn include `mf_wreply` (memfn.h:1435), MF_SITE_ABI 20, window.c decide() 986-1030, reply_of, c_plan; 16 pcrec readers of `wr` | large: kit contract + pcrec readers + G1/G2 at both layers | removes kit-held A_entry | N ("designed with the D176 build") |
| 6 | C_ENTER move | only reader is window.c:394 `model_cost`; replacement card needed | small code, medium measurement | one box/one unit | N |
| 7 | MARGIN delete | window.c:655-720 (T_MARGIN, `ct_m_margin`, `wf_mtable`, `m_margin_holds`, d->ch at 1011-1019), plan_cost.def MATERIAL_NUM/DEN | small code, but a MOVER event and not independent (COST-5) | deletes an ARGUED constant | N |
| 8 | per-route consumer cards (A_entry, no-search/byte, reverse/byte) | measure_store: 68 rows, 0 pcrec-owned, 0 engine rows; the canned pcrec measuring script ([MEASURE-SET] (a)) is unbuilt | large: script + night windows with Frank | feeds every priced slot | prerequisite list only |
| 9 | backend-only trace | today the selection trace exists only in the PCREC_CAND_TRACE build (#ifdef near emit_dfa.c:10880..11194); `--trace` in the default build is matcher instrumentation (`$B --help`: "emit an INSTRUMENTED matcher") | medium: a default-build selection trace is NEW, not an extension | G2 explainability | N |
| 10 | shadow stage | COST-3, 4, 7 | medium | localises candidate movers (never acceptance) | N |
| 11 | dated addenda | D146, D161 add. 6, Q-WR-9 (study) + D176 Q1/Q4 (omitted, COST-8) | doc | | owner ruling |
- Order of magnitude (INFERENCE from file sizes and abi history; the study offers none): rows 1, 5, 8 are each
  lane-sized (opus), 2 and 4 each a lane, 6, 7, 10 small. The total is not "a migration of predicate splits".

### COST-3  Third shadow hazard: any pcrec-side read of a measurement-set row flips `RX_MEASURES` in every artifact  [identity gate, CONFIRMED by reading + probe]
- Study Q6 stage 1 names two hazards. A shadow that prices must read set rows (consumer cards). Spec
  measures.md 4 para 2: "A reader is pcrec's own (none exists today) or the kit's"; 4 para 4: "No kit row reads
  a set key today, so every artifact's stamp is `""`". The stamp comes from `meas_consulted`
  (memfn_sites.c:977-996, set only from the kit's `mf_art_end`). The first pcrec-side reader makes every
  artifact it runs on carry `RX_MEASURES "zen4-grid1@1:13a6536315af1520"`. Probe: `$B -p rx -o t.c --pattern
  'abc'` -> `RX_MEASURES ""` (6 patterns, all empty). So "byte-identical" fails on that line unless the shadow
  reads through a non-consulting path (none exists) or runs only in the trace build.
- `RX_FINDINGS` does NOT have this hazard: 12 patterns probed incl. '', '^', 'a*', '.': all carry
  `byte-rate=default:1822fb973b95a4da` because the rate is asked first on every compile (req.c:762-763 comment).
- Unstated dependency: the shadow's price needs ONE set for kit and consumer terms (R4.3). The kit's window code
  reads compiled-in `plan_cost.def` (window.c:65-72, 11 `COST(` uses), not the set. No shared-set shadow can exist
  before the D176 migration (plan_cost.def rows into the sets, [MEASURE-SET] rev 2, gated on the step-0 census,
  plan.md:183-190). `HORS_MIN` is still read at window.c:1596, so that build has not landed. Stage 1 is behind it.
- Changes the recommendation? No; it changes stage 1's definition.

### COST-4  Hazard 1 exists, but the remedy "or the quiet walk" does not protect `used`; `_stated` covers six facts only  [shadow plan, CONFIRMED]
- Exists: facts.c:128 `if (pass) pf->used |= pf_bit(f);`; the public accessors pass true; `--emit-facts` `used`
  is caller-visible.
- `cand_select_quiet` (emit_dfa.c:10869-10877) only raises `pcrec_cand_trace_quiet` and sets `cand_eval_base`;
  it does not touch `cx->job->pf.used`. The tree's own precedent is the explicit save/restore in
  `req_pres_proof_quiet` (emit_dfa.c, just above the "START-TABLE THE HIT COUNTER" block): `uint32_t used =
  cx->job->pf.used; ... cx->job->pf.used = used;` with the comment "the facts' `used` record is restored".
  Predicates walked quietly still call public accessors and set `used`.
- `_stated` accessors exist for six facts only (facts.c:532-616: req_set, req_whole_run, req_run, req_byte,
  run_pin, span). A path-pricing shadow reads many more (landmark maxoff, end_window, cand_ppm, root_minw ...).
  The restore pattern is the general one.
- Changes the recommendation? No. Fix the stage text: "save/restore `pf.used` around the shadow (as
  req_pres_proof_quiet does), plus a check that `used` is bit-identical shadow-on vs off".

### COST-5  MARGIN deletion and the frontier reply are not independent steps; they land with the backend argmin  [ordering, CONFIRMED]
- window.c:1005-1019: `d->ch`, the kit's pick that pcrec's NEXT rows read as `us->wr`, comes from the M-table
  (M_ONE / M_MARGIN / M_PARKED). With a frontier reply the kit no longer picks between PARKED and RESEED; the
  backend does. Until the backend argmin is live, deleting MARGIN leaves na==2 sites to M_PARKED (every one a
  silent mover on the offset-set population). Q6 places neither the MARGIN deletion nor the reply change in any
  stage. The reply must be additive (frontier AND old pick) through stage 3 and the pick removed when the last
  slot is priced: two kit contract events, or one large atomic one.
- The deletion replaces an ARGUED bar by the tie band (COST-9). The band is a margin too (measured), so the
  ipv4 case (plan_cost.def MATERIAL_NUM provenance: 1.5-1.6x "inside the model's error bars") flips or not
  depending on band width, and no stage names that census.

### COST-6  A per-path argmin needs counterfactual reads the read graph does not support today  [design, SUSPECTED]
- cand_nodes has `reads`/`under`/`kask`, the self-check `table-read-cycle` and the trace trap `ask-while-open`
  (emit_dfa.c:9876-9896, 11596-11625). They assume ONE selection per slot per compile; `under` bits express a deny
  (rows removed), not "assume row X chosen". G1 reads LOCATE and NEXT, `landing` reads NEXT, `handoff-reentry`
  reads FIRST (study Q1). A path enumeration needs "validity of NEXT rows given a hypothetical LOCATE/FIRST
  pick". Whether deny bits can emulate every edge or a new "assume" input is needed is not shown; that is the
  main unknown inside COST-2 row 1.
- Hazard 2 (kask/kfields) is real as described (trap is trace-build only: sabotage S1019), but wider: a shadow
  asks the kit about site descriptions first-match never fixed (non-chosen NEXT families); each needs its own
  constructor call, and ask-while-open fires for them unless the shadow runs after all slots close.
- To confirm: shadow one slot pair (LOCATE x NEXT) in a scratch tree. That is the first lane's work.

### COST-7  Compile time (pricing_requirements G5) is unaddressed; "the shadow writes only the trace" may leave the default build untested  [speed/maintenance, SUSPECTED]
- G5: pricing adds <= 1 % to the `scripts/compile_time_census.py` median (script exists). First-match stops at
  the first applicable row; an argmin evaluates every row's validity and every priced row's inputs (cover's
  C3-C14 machine conjuncts, landmark tests, kit asks), per path combination. The study has no estimate and Q6
  has no census gate in any stage; the stage-1 shadow doubles selection work in whichever build runs it.
- If the shadow exists only in the PCREC_CAND_TRACE build (the only place a selection trace exists today), the
  default build never executes it, the emit_sweep identity arm tests nothing about it, and the first run of the
  argmin in a shipping build is stage 3. State which; add the census to stages 1 and 3.
- To confirm: run compile_time_census over a path-enumerating prototype (not possible here: no build).

### COST-8  The addendum list omits D176 Q1/Q4, whose "ONE priced choice / ONE decider" (d) splits  [design/doc, CONFIRMED against decisions.md D176]
- D176 Q1: "which stop, found how is ONE priced choice in the kit's Table A over (alternative x stop position x
  find method)". Entry kind (PARKED/RESEED) IS Table A's "alternative" axis (window.c `m_pair`). The footprint
  split moves that axis from the kit's argmin to the backend's. D176 Q4: "ONE decider, the kit's window family".
  Open point 1 asks for addenda to D146, D161 add. 6 and Q-WR-9 only. Frank's 2026-10-31 notice says the D176
  shape will be amended by an addendum; (d) belongs named in THAT one.
- Kit-queue overlap: S3 (D172, abi 92 pending merge), R-30b (abi 94 planned; the notice: "S3 rewrites the same
  PRES/window decision code, so building R-30 first would be rebuilt"), trailgc (abi 93). A frontier reply
  rewrites the same decide()/reply_of. Under D153 the kit reply waits for S3 and R-30b; the study says only
  "designed with the D176 build".

### COST-9  The "derived" noise band is not derivable from the set as it exists, and rests on an independence assumption the set contradicts  [measurement claim, CONFIRMED]
- Q5 item 4: "root of the sum of squared per-term bands, weighted by the prior's multipliers ... DERIVED".
- measure_store/zen4-grid1/1/set.tsv: all 68 rows have `noise_e6` = `-`. The only noise-like data: three
  `kit.eps.*` A/A p90 rows (ext.engine 3820, findall.l64k 33650, streamed.slope 1730, value_e6 = 0.38 %, 3.4 %,
  0.17 %) and the cards' constant `gate_e6` 30000 (3 %). measure_sets.md:948-950: "No selection reads noise
  today ... A kit row that wants noise asks by REQUEST". measures.md 3.2 has a closed derivation list with no
  quadrature (compile-time arithmetic is legal, but the INPUTS, per-term bands, are absent from the data).
- Independence is false by construction: every value is relative to the one unit row, so each carries the
  unit's noise; terms from one run share box state. Quadrature of shared-denominator terms understates the
  band. It also covers measurement noise only, not model error (survivor gap 21x-1,750x, PS C5; VM 5x
  per-artifact variance, PS 7.4 item 7).
- With today's data the band IS a constant in disguise (`gate_e6` or an eps row) until `noise_e6` is populated:
  a schema/measurement change plus a first selection reader of it.
- Related gap: a pick that reads `noise_e6` is not covered by the stamp. `values_digest` hashes no provenance
  column (measures.md 3.3 para 1), `noise_e6` is outside it (measure_sets.md:109, :492-495), and 5 para 4 only
  requires a file with a committed (id, rev) to carry that `values_digest`. Two FILE/-I sets with equal values
  and different `noise_e6` carry the same `RX_MEASURES` and can pick differently (committed sets are immutable,
  so only file-loaded sets are affected).
- Changes the recommendation? No. The supporting claim "(d) needs no constant" is incomplete: the tie band
  replaces MARGIN as a measured margin whose width is data the set does not yet hold.

### COST-10  "A_entry as a measured per-route set row" inherits C_ENTER's ASSUMED factor; the frontier prune is exact only on predicted entries  [speed, CONFIRMED in the source rows]
- plan_cost.def C_ENTER = 2000 = "[OPT-3]'s measured 10.7 c/B times an ASSUMED ~2 bytes a false start
  survives". Moving the number to a per-route row cannot carry the survival length: it is a property of the
  machine and the subject's rates (the C5 joint-survival class), not of the route. The moved row would keep an
  ASSUMED factor under a MEASURED label. Split it: entry overhead per route (a card) + survival bytes (derived
  from machine facts and rates, with an error bound, R4.6) times the route's per-byte card. Q4's row S2 lists
  "A_entry per route x entries" and does not split it.
- "An option no cheaper to scan AND yielding no fewer entries can never win under any non-negative A_entry" is
  exact on PREDICTED entries. Predicted survivors are the independence product PS measured 21x-1,750x off, so
  the prune can drop the true winner. "Exact without any number" (Summary 4, Q3 table) holds for the model, not
  the machine; state an error bound or keep within-bound options on the frontier.

### COST-11  The "independent control" shares sources with the price in three places  [measurement, (a) CONFIRMED, (b)(c) SUSPECTED]
Study Q5 item 2 and standing question 2: held-out regret timed by pcrec-side bench runs.
- (a) The SRS 5.1 witnesses (`[.,;]\d`, `[QXZ]{2}`, hex8, `[<>&]x` ...) MOTIVATED the design (Frank: "See if
  pricing fixes these"); Q6 stage 3 calls them "a timed held-out regret run". They are the acceptance set, not
  held-out (requirements R6.2: a site used to diagnose a term leaves the validation population).
- (b) Same box, harness family, compiler and emitted-code form as the consumer cards. A systematic error in a
  card (VM frame discipline, DFA table form [OPT-3]) repeats in the regret run. The kit's cards carry `deps
  kit:form.<form>` so a form change stales them; the study names no equivalent dependency for pcrec-owned
  rows, though pcrec's emitted forms change at each abi event (abi 91 -> 94 pending in a week) and D182 rewrites
  the VM body writer. Consumer cards could go stale silently.
- (c) The price reads the authored byte-rate prior (PS: "AUTHORED ... English-log-shaped"); the bench subjects
  are the same families, so a prior error the subjects share is invisible (SRS 5.1 item 3 shows dense hex
  invisible by construction). Independence needs subjects whose rates are counted by something other than the
  prior (K35).
- Stage 2 (shadow-vs-first-match census) shares a source by the study's own admission; it is a localiser only.

### COST-12  What the measurement set can represent today, for the consumer cards  [measurement, CONFIRMED]
- Representable: owner `pcrec` is legal (measures.md 2.3; measure_sets.md:338), keys `pcrec.<quantity>.<tokens>`,
  units ratio / walkbytes / bytes / count (closed, 3.1), tier scratch, class x86_64-avx2/zen4, one default `idk`.
- Absent: any pcrec card (0 of 10; all `kit`), any engine / no-search / reseed row (0 of 68); a per-dimension unit
  (per byte vs per entry vs per call lives only in the quantity name, so Q5 item 1's dimension type check must be
  in the reader); a derivation for products; noise (COST-9); fallback rows (a compile on a non-zen4 class reads
  the zen4 set under the single `idk` default, against R4.5); a pcrec reader for the stamp (COST-3).
- What moves on regeneration: a new rev changes C_ENTER from Zen 1 to Zen 4 data and flips PARKED/RESEED
  (COST-5) and cover/composite near-ties; per D166 a mover census plus an abi event. The first rev with
  consumer rows is the first one a selection reads; the store holds only movers/0001.tsv, so that path is
  unexercised end to end.

### COST-13  Overlap against D153 ("remodels first")  [ordering, CONFIRMED / SUSPECTED as marked]
- Done, not blocking: [START-TABLE] C1-C7 (C7 merged 2026-10-08, plan.md:631), [DEC-FALLBACK]
  (plan_completed.md:5415). cand_rows[] is not under remodel from those.
- In flight and touching the same sites:
  - [VMREC] D182 step (b)/(c) (plan.md:238). The RETRY slot's spelling is in emit_vm.c (`vm_reseed_cal`,
    `vm_plan_reseed`; "The emitted retry spells all four as literals", emit_vm.c:11088-11160). COST-1's
    RETRY-first stage collides; D153 puts RETRY after VMREC (c). D182 (c) ruling 1 also asks the kit for
    "declared effects with each delivered window", a second window-contract change to bundle with the frontier
    reply into one MF_SITE_ABI event (SUSPECTED that both land on the same struct).
  - [MEMFN-UNBOUNDED-SPANS] (plan.md:894, not-started): the same req.c rate picks (crossing 7) and an
    MF_SITE_ABI event: bundle, do not sequence as two events. [TIE-ALIGN] (plan.md:613, run reader tie vs
    prefix_k pick) is a sibling of crossing 7 the study does not mention.
  - Kit S3 / R-30b / trailgc (abi 92/93/94): window decide code and the abi counter.
  - D176 build and [MEASURE-SET] rev 2 (plan.md:183): prerequisite (COST-3).
- The proposed order respects D153 only if "RETRY first" is dropped (COST-1) and the kit reply waits for S3,
  R-30b and UNBOUNDED-SPANS.

## PROBED-AND-HELD
- Line cites: 8 checked (cand_rows 51 rows counted by awk, cand_nodes, cand_select_quiet, req_landmark_admits,
  cand_rs_dense_applies, req.c 764-830, window.c 669-683, facts.c 128). All hold.
- Hazard 1 (`used` bit, `_stated` accessors) exists as described (facts.c:128, 532-616); remedy wrong (COST-4).
- Hazard 2 (kask/kfields, trace trap) exists as described (emit_dfa.c:9876-9896, 11280, 11596-11625).
- `cand_select_quiet` is "a check walk, not a read" as cited (10869-10878).
- `RX_FINDINGS` byte-identity under a rate-reading shadow HOLDS (12 patterns always stamped); `RX_MEASURES` does
  not hold under a set-reading shadow (COST-3).
- Kit holds a consumer cost (C_ENTER) contrary to MV's "kit never receives engine costs": HOLDS
  (plan_cost.def:38, window.c:394).
- Kit rows read plan_cost.def, not the set: HOLDS (window.c:65-72; measures.md 4 para 4).
- Probes: 1 trace-flag compile + 12 stamp compiles; 0 gcc, 0 make. About 45 files/regions read.

## STATE AT HANDOFF
STATE: complete
OWED: none
Not done (no build allowed): a prototype to measure compile-time cost and the read-graph change (COST-6 and
COST-7 stay SUSPECTED). Scratch: cost/ps.md, srs.md, req.md (git show copies), t1.c, t.c.
