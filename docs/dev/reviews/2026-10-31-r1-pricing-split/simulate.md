# crit-pricing-split / simulate (opus): the study's rules run over real data and real sites

Critic lens: SIMULATE. Subject: `docs/dev/lanes/splitstudy_report.md` @ lane/splitstudy 70464e9a3
(snapshot `../subject_splitstudy_report.md`). Review tree `worktrees/crit-pricing-split` @ a3cc4de82.
Scratch: this directory (`sim.py`, `sim_out.txt`, `probe/`, copies `price_orig.py`, `out_orig.txt`,
`srs.md`, `ps.md`, `req.md` taken with `git show` from lane/memfn-stopstudy and lane/memfn-pricesurvey).
No denied file was opened. No `make`, no suite; compiles of single patterns only (counted below).

## Findings

### The price model the kit uses today (written down, as briefed)

Read off `memfn/src/window.c` @ a3cc4de82 and `memfn/src/plan_cost.def`; re-implemented in
`sim.py` Part 1 in the same integer arithmetic. Validated against the compiled stamps of 4 real
sites (all 4 match: `foo(bar|baz)+` RESEED stop@3 verify{0} = `offset-set "0,3*"`; `ab[0-9]+cd`
RESEED stop@1 = `offset-set "0,1*"`; `xy\d+z` and `quick.*fox` PARKED = `run-pinned "0*,..."`).

    unit: 1/100 cycle per subject byte; masses m in ppm (PPM = 1e6); integer, truncating
    verify_cost(p) = C_VERIFY(250) + C_MISPRED(1500) * min(p, PPM-p) / PPM
    model_cost(scan, m, vc, vr) = scan + m*vc/PPM + (m*vr/PPM)*C_ENTER(2000)/PPM   (window.c:394)
    A-parked  base = model_cost(|k0|==1 ? C_MEMCHR(6) : C_BITMAP(116), m(k0), 0, PPM)
                   = scan + m(k0)*C_ENTER/PPM          (every stop is an entry; window.c:420)
    A-model   per one-member walked stop s (offset >= 1): F0 = k[0] always verified; the other
              walked offsets by ascending mass, added GREEDILY while the plan holds < MAX_SET-1
              and only if the TOTAL (C_ENTER term included) drops (`if (nc >= cost) continue;`,
              window.c:496); least cost, ties to the lower offset
    MARGIN    RESEED iff best_reseed * 2 < base (window.c:669-683; basis "ARGUED
              (offset_k_skip.md §4.5; ipv4's 1.5-1.6x inside the error bars)", window.c:710)

SRS's proposed price (`stop_ranking_study.md` §4.1, `price.py`): `β_f + r(S)(s_f + V) +
r(S)·π(c)·A_entry` (scan), `(c_probe + r·V)/E[sh]` (skip); `price.py` itself carries NO A_entry
term (it prices the A-mass/REPORT domain, where SRS §4.1 shows the consumer terms cancel).
A_entry = C_ENTER, whose own provenance is "[OPT-3]'s measured 10.7 c/B times an ASSUMED ~2
bytes a false start survives" (plan_cost.def): a per-byte DFA cost times BYTES WALKED.

### SIM-1. The frontier prune is not exact: the consumer's per-entry cost depends on the plan, not only on the footprint's entry count (CONFIRMED, model + data)

- **Claim tested** (Summary 4; Q1.4 item 2; Q3 (d); RECOMMENDATION seam rule 5): "an option no
  cheaper to scan AND yielding no fewer entries can never win under any non-negative A_entry. So
  the kit can prune it, and it needs no number to do so"; "The backend multiplies the entries
  term by its measured per-route `A_entry`."
- **What breaks it.** The consumer's cost per false entry is not a per-route scalar. In the
  emitted DFA (`probe/p14.c`, `foo(bar|baz)+`, lines ~186-196) a false candidate re-enters the
  unanchored machine at the candidate start and the machine WALKS until it falls back; the bytes
  walked depend on which positions the plan proved (a contiguous proven prefix is re-walked in
  full). C_ENTER's own provenance is exactly that product (10.7 c/B x "~2 bytes a false start
  survives"). So A_entry = A(plan), and Pareto dominance in (kit price, entries) does not imply
  dominance in total cost.
- **Counterexample, computed** (`sim.py` Part 3b, `sim_out.txt`; prior = shipped
  `default_ppm.tsv`; per-entry cost = 10.7 c/B x expected walk length under independence):
  window `e r e h` (the literal prefix of `ereh\w+`):
  - RESEED stop@1 `r`, verify{0}: kit 20.944, entries 3344.8 ppm, walk 3.084 B -> total 31.98
  - RESEED stop@3 `h`, verify{0}: kit 21.194, entries 3400.8 ppm, walk 2.043 B -> total 28.63
  The first dominates the second on both axes the study prunes on, so the kit drops the second;
  the second is 11.7% cheaper. Over 115,248 literal windows (14-letter alphabet, len 4 all, len 5
  1/7): the true winner is strictly dominated (pruned) on 3.6%, and on a further 14.3% it ties a
  kept option on (kit, entries) exactly while differing in true cost by up to 14.1% (`eeee`), so
  the frontier's choice among equal-component options is itself a consumer-cost question.
- **How much it matters on today's population (bounding the damage honestly).** On main a
  literal stretch like `ereh` is a PINNED run (`ereh\w+` compiles to `run-pinned "0,1*,2,3"`,
  `probe/e1.c`): the plan verifies the whole run, entries ~ full-match rate, and the plan-dependence
  is moot. On windows with no pinnable run (Part 3c: single letters alternating with 3-member
  classes, 85,176 windows) the strict prune hits 0.6% (worst regret 1.85%) and the
  equal-component pick 7.1% (worst 2.79%): inside the regime noise bands (kit.eps up to 3.4%).
- **Second break, independent of the walk model.** The "entries" coordinate is the kit's
  independence ESTIMATE (π(c) = Π p_j, SRS §4.1), which errs 21x-1,750x on survivors (PS §7.4
  item 3). Two options with different proofs are ordered by that estimate; "needs no number" is
  false: it needs the prior's survivor estimate, the term PS calls the largest error source. Only
  WITHIN one footprint (same proof, same survivors) is the cancellation exact, and that is the
  SRS §4.1 A-mass domain the study already had.
- **Severity** design. **Effort** small to restate (the prune is valid only among options with
  equal per-entry cost: same entry kind AND same proof shape; across them the kit must return
  each option or state the per-entry walk as a component). **Blast radius**: the kit reply
  contract (open point 2) and the "no number" argument behind deleting C_ENTER from the kit.
- **Changes the RECOMMENDATION?** It changes seam rule 5's exactness claim and Q1.4 item 2's
  derivation, not the choice of (d): the footprint split survives as "the kit prunes only where
  the consumer's per-entry cost is provably equal; the reply carries the proof shape so the
  backend's A(plan) can be applied". The reply gets larger (SIM-2).

### SIM-2. The frontier is 3-6 options per site, made of VERIFY-DEPTH variants: the kit's C-model greedy is itself a cross-footprint choice that (d) silently moves to the backend (CONFIRMED, data)

- **Claim tested**: Q3 table "frontier size (expected 1-3, **INFERENCE**)"; RECOMMENDATION "Keep
  every within-footprint method choice (D146's core)"; Q1.4 item 6 (pcrec RENDERS the kit's
  tactic, never chooses it); the study's own definition (line 21): a tactic is "which stop, which
  method, which verify order".
- **Data** (`sim.py` Part 2 exact mode, 22 sites: the 4 compiled above plus 18 hand-stated
  prefilter windows of common log/text shapes, today's option space = PARKED k0 plus RESEED
  stop x verify subset of <= MAX_SET-2 walked offsets):
  - Pareto frontier per site: distribution [1, 3, 3, 3, then 4 on 17 sites, 6]; lower convex hull
    (the options that are the argmin for SOME scalar A_entry >= 0): max 4. In today's truncating
    integer unit the frontier is 1-5 (it collapses where verify costs truncate to 0).
  - Every hull point beyond the first is the SAME stop with a deeper verify plan (e.g.
    `foo(bar|baz)+`: verify{0} / {0,5} / {0,1,5} at stop@3; `ab[0-9]+cd`: {0} / {0,2} / {0,2,3}).
  - Not counted, and each can only ENLARGE it: fold-reach classes (an option whose first find
    covers the presence member is incomparable with one that does not), the pinned-run (C-pin)
    variants, Table B method rows (these share a footprint, so only the cheapest survives: no
    growth), and per-proof splitting needed by SIM-1 (then the reply is the whole option set:
    1-204 options on these 22 sites, `sim_out.txt` "options").
- **Why it matters.** C-model's acceptance test (`window.c:496`, `if (nc >= cost) continue;`)
  compares totals that include `C_ENTER` (`window.c:394`): choosing the verify depth IS the
  trade of verify cost against false entries, i.e. a consumer-cost choice. Under (d) the kit cannot
  run it (no A_entry), so it must return every depth, and the backend's argmin over the frontier
  picks the verify plan. That is pcrec choosing a kit tactic (which verify order), which the
  study's own seam (rule 4: rendering may read a pick; validity never reads one) and D157 ("which
  position becomes the stop, and how it is found, is the kit's", SRS §2.2) do not cover. The
  study never mentions C-model.
- **Held part.** The greedy never mispicked against the exhaustive best on these 22 sites (exact
  arithmetic, `exact+MARGIN` column equals today's pick on 21; the 22nd, `(tion|sion)s?`, is a
  truncation tie, stop@1 vs stop@3 at 33 = 33, the `\d\dxyz` defect class of SRS §4.3).
- **Severity** design. **Effort** small (state it: the frontier is over (stop, verify depth),
  the backend chooses the depth, and D146/D157's addendum must say so; or give the kit a
  per-route A_entry as a set row, which is (a)-flavoured and reverses D161 add. 6 for this one
  term). **Blast radius**: open point 1's ruling text, the reply contract. **Changes the
  RECOMMENDATION?** Its wording of the kit's role ("keep every within-footprint method choice")
  and the 1-3 estimate; (d) stands.

### SIM-3. Deleting MARGIN 2/1 is not a consequence of the frontier: it moves 5 of 22 sites, one on a 0.4% modelled gain (CONFIRMED, data)

- **Claim tested**: Q1.4 item 2 "MARGIN 2/1 (`window.c:669-683`) then has no role and is deleted,
  as HORS_MIN was"; Q3 measurements row "DELETES MARGIN 2/1"; RECOMMENDATION kit bullet.
- **MARGIN's basis is not a consumer cost.** `window.c:710`: "ARGUED (offset_k_skip.md §4.5;
  ipv4's 1.5-1.6x inside the error bars)": a guard against the MODEL's error, keeping the PARKED
  baseline unless RESEED is modelled at under half. SRS §4.1 keeps it for that reason ("the MARGIN
  bar stays ARGUED"). Moving A_entry out of the kit does not address model error, so the frontier
  derivation gives MARGIN no replacement and no reason to go.
- **Movers if it goes** (exact arithmetic, plain argmin at A_entry = C_ENTER, `sim_out.txt`
  "MARGIN-only flips"): PARKED -> RESEED on `quick.*fox` (RESEED/PARKED = 0.996, compiled today
  `run-pinned "0*,1,2,3,4"`), `GET /\S*` (0.814), `zq\d+x` (0.882), `xyzzy\d+` (0.766),
  `Mozilla/\d` (0.667). `quick.*fox`'s 0.4% modelled gain is far inside every noise band on
  record (kit.eps 0.17%-3.4%) and inside the 1.5-1.6x cell MARGIN was set on.
- The study's own Q5 item 4 forbids a hysteresis band ("that would be a margin"), so under (d)
  these flips are intended, yet no measured cell backs any of them.
- **Severity** speed (5 unmeasured movers in 22) / design. **Effort** none to restate (make
  MARGIN's fate its own row with its own measurement: the ipv4 cell, A_entry per route, held-out
  witnesses). **Changes the RECOMMENDATION?** Only the "simplification" credit (Q3 row, kit
  bullet): MARGIN's deletion is a separate decision, not a corollary of (d).

### SIM-4. Q2.2's nesting puts the match phase at the ROUTE level, but a path can delete it: `cover` runs no DFA at all on the DFA route (CONFIRMED, probe)

- **Claim tested**: Q2.2 `best artifact = min over valid routes rt of ( match_phase(rt) + min over
  valid paths p on rt of price(p) )`, "exact ... as long as every term that depends on the route
  sits inside that route's terms"; Summary 3 "That nesting is exact".
- **Probe**: `$B -p rx --features all -o probe/cat.c --pattern '\bcat\b'`: stamps `RX_ENGINE "dfa"`,
  `RX_DFA_SCAN "cover"`; `rx_search` (probe/cat.c:66-76) is one kit find-then-verify loop and
  `capture_spans[0][1] = scan_position + 3` (cat.c:74): no forward DFA, no reverse pass, no match
  phase. Expected under the formula: a DFA-route match phase common to every DFA-route path.
  Observed: the match-phase cost is a property of the PATH (cover's REPORT replaces search AND
  match; `rev-end` replaces the forward search and runs the reverse machine, emit_dfa.c `rev-end`
  row's desc).
- **Consequence.** Read as written, the outer formula charges cover a match phase it does not
  run; on the very slot family the study prices first among LOCATE (Q6 stage 3, "LOCATE's `cover`
  vs `composite`", witnesses `[.,;]\d`, `[QXZ]{2}`) that biases the comparison against cover by
  exactly the term cover saves. The exact form is `min over valid (rt, p) of total(rt, p)` with
  every match-phase term inside the path; min-of-mins then holds trivially, and the separation
  condition the study states is satisfied only by moving match_phase inside p. The stated reason
  (1) for an outer argmin ("a route's own costs ... are not search costs") is false for the
  cover/rev-end paths.
- Held, same check: the hybrid prefilter (S6) and the handoff do NOT break the separation; their
  terms (DFA per byte + VM per candidate; landmark find + engine bytes skipped) are inside the
  VM route's paths. Route validity known only after a build (study's `zq.{1,40}abc`) extends to
  PATH validity: the VM route's `collapsed-prefilter` path (`probe/p18.c`: `RX_ENGINE "vm"`,
  prefilter `memchr`) exists only after the collapsed DFA was built.
- **Severity** design (a mispricing of cover vs composite if built as written). **Effort** none
  (restate the formula). **Changes the RECOMMENDATION?** No; a supporting claim (Q2.2, Summary 3).

### SIM-5. A path's price is not a per-byte sum of its slots' terms: PRESENCE, FIRST and NEXT run on disjoint, outcome-dependent byte ranges (CONFIRMED, emitted code)

- **Claim tested**: Q1.4 item 1 "Each PATH's price adds the presence term unless that path's option
  folds it"; Q3 (d) "The backend adds its consumer terms and takes the argmin"; Q4 S2 "backend adds:
  A_entry per route x entries; presence term unless folded; RECOVER term".
- **Emitted structure** (`probe/p14.c`, `foo(bar|baz)+`, stamps `REQ_WHY "emitted"` via P4
  set-leads, `REQ_HANDOFF "0"`, `DFA_PREFILTER "offset-set" "0,3*"`): `rx_search` first runs
  `memchr(.., 'b', ..)` over the window (p14.c:121; NOMATCH if absent), then `rx_reqrun` (memchr
  `f` + two word compares) to the first `foo`, and only from that handoff position does the DFA
  run with `rx_ofsskip` (memchr `b` at +3, verify `f`). On a subject without `b` only the presence
  pass runs; with `b` but no `foo` the run search scans the rest and NEXT never runs; NEXT's
  per-byte price applies only to bytes after the first landmark.
- So `price(path)` = a sum over slots of (per-byte term x the FRACTION of bytes that slot sees),
  and the fractions are outcome probabilities (landmark density, match density). An additive
  per-byte sum would charge every slot on every byte: presence would always be a pure cost and the
  handoff could never pay. This is the same match/landmark-density model Q2.2 defers for engine
  pricing ("nothing measures yet"); the five priced slots need it already (FIRST's "engine bytes
  skipped" in the study's own S5 row is that fraction).
- Held: the PATH, not the slot, is the right unit (FIRST `handoff` has no price in isolation, NEXT
  `handoff-reentry` is valid only on a FIRST=handoff path: `jq[a-z]+x` default `DFA_PREFILTER
  "handoff"`, under `-fno-req-handoff` `"memchr"`, probes q6/q7). A per-slot greedy is not merely
  mispicking: FIRST cannot be priced alone at all.
- **Severity** design. **Effort** medium (a byte-allocation term per path: one landmark-density and
  one match-density row per regime, or a declared regime for which prices are quoted).
  **Changes the RECOMMENDATION?** No; it adds a prerequisite to Q6 ("before stage 3": a
  match/landmark-density model or a declared regime), and qualifies "presence priced per path"
  (unlock 1) and FIRST/NEXT's handoff (Q6 stage 3's second step).

### SIM-6. Q5 item 4's tie rule: the composite band has no inputs today, it either ties almost nothing or almost everything, and "total order, so never evaluation-order dependent" is false for a band tie (CONFIRMED, data + arithmetic)

- **Claim tested**: Q5 item 4 (fixed-point prices; "Prices within the measured noise band tie, and
  the tie goes to a declared SIMPLICITY ORDER ... That order is total, with table order as the last
  key, so a pick never depends on evaluation order"; composite band = "root of the sum of squared
  per-term bands, weighted by the prior's multipliers ... DERIVED, never a constant"); Q5 item 2
  ("A pick within one band of the runner-up is a tie-class pick; its regret is expected noise").
- **(a) Not well defined today.** `measure_store/zen4-grid1/1/set.tsv`: the `noise_e6` column is
  `-` on every one of its value rows; the only noise rows are three REGIME-level A/A p90 ratios of
  whole calls (`kit.eps.streamed.slope` 0.173%, `kit.eps.ext.engine` 0.382%,
  `kit.eps.findall.l64k` 3.365%), not per-term bands; `plan_cost.def` has no band column at all
  (C_VERIFY is an UNMEASURED DEFAULT; c_probe and v0 are unmeasured in SRS). The RSS has no terms
  to sum. RSS also assumes independent errors; terms measured in one run on one box (D166's own
  rule) are correlated, and two candidates that share a term (same β, same verify) should be
  compared on the band of their DIFFERENCE, where shared terms cancel, not on each price's band.
- **(b) Ties: almost none, or all** (`part4.py`, `part4_out.txt`, SRS's 10 patterns and price.py's
  constants). Proxy A (per-byte terms 0.173%, per-stop/probe terms 3.365%): 1 of 10 winners ties its
  runner-up, and that one is an EXACT tie (`[aeiou]..[aeiou]` walk@0 = walk@3, 0.8011). So the band
  does not make most picks ties; but it measures timing noise only, while the price's dominant error
  is the RATE (one-position stop counts 0.3x-6.8x on real text, PS §7.4). Proxy B (the same plus a
  x/÷2 rate error on the r(S)-scaled terms, well inside 0.3x-6.8x): 10 of 10 tie, and "simplest
  inside the band" then picks `\d\dxyz` -> memchr `x`@2 (the D151 defect SRS §4.3 fixed by
  resolution), `[xq]abc` -> memchr@1 at 0.462 vs the min 0.047 (10x), `[a-z]{6}` -> walk at 3.1x
  the SKIP price. Q5 item 2's reading of in-band regret as "expected noise, not a model error" holds
  only under Proxy A, which excludes the error that dominates.
- **(c) Order dependence.** A band tie is not transitive (A~B, B~C, A!~C). With a running-best
  evaluation (the shape of every argmin loop in window.c today: `cost < best || (cost == best &&
  tie_takes(..))`, e.g. a_model_choose), prices 1.000 (complex) / 1.030 / 1.060 (simplest), band
  3.4%: the 6 evaluation orders yield all three candidates as the pick (`part4_out.txt`). A total
  simplicity order does not fix this; only a stated TWO-PASS rule does ("the simplest among the
  candidates within the band of the MINIMUM", order-free: picks the 1.030 one). The study does not
  state it. A per-candidate band (each price's own RSS) also makes the tie relation asymmetric:
  costlier candidates carry wider bands and tie more easily (Proxy B's 10x pick).
- **Severity** design. **Effort** small (state the two-pass rule; define the band on differences;
  name the per-term band rows as a measurement prerequisite; decide whether rate error is in or
  out and say what in-band regret then means). **Changes the RECOMMENDATION?** No; Q5 item 4 and
  item 2 as written are not implementable; open point to add.

### SIM-7. The footprint is defined three ways; as written in Q4 it makes the kit's own argmin vacuous (CONFIRMED, doc)

- Summary 4: "same CONSUMER FOOTPRINT (same entry kind, candidate rate, proof and fold reach)";
  Q4 S2 row: "footprint = (entry kind, candidate stops per byte, survivors per byte after its
  verify, proven positions, which necessary members its first find covers)"; Q3 (d): no fields.
- "Candidate stops per byte" is not something a RESEED consumer sees (verified-away stops never
  reach it), yet as a footprint field it splits options that differ only in the stop, even in the
  A-mass/REPORT domain where SRS §4.1 shows the consumer terms cancel exactly across stops.
  "Proven positions" splits every (stop, plan) pair. With both, "within one footprint" leaves only
  the METHOD for the same stop and plan, so the kit's exact argmin covers method choice alone and
  every stop/plan choice becomes cross-footprint (SIM-2's backend choice). On the 22 sites that is
  1-204 footprints per site (`sim_out.txt` "options"), against the 1-3 guessed.
- What the consumer actually sees (and so what the footprint should be): entry kind, the survivor
  set (its rate, and its proof shape where the consumer re-walks it, SIM-1), fold reach. Stops
  matter only for PARKED (each stop is an entry).
- **Severity** doc / design. **Effort** small. **Changes the RECOMMENDATION?** The definition
  behind seam rule 5, not the option.

## PROBED-AND-HELD

- **Table A re-implementation** (sim.py Part 1): 4 of 4 compiled sites match today's stamps
  (`foo(bar|baz)+`, `ab[0-9]+cd`, `xy\d+z`, `quick.*fox`). Over 22 sites, the greedy C-model never
  mispicked against the exhaustive (stop x verify subset) best in exact arithmetic (21 equal, 1
  integer-unit tie, `(tion|sion)s?`, stop@1 = stop@3 = 33: `tie_check.py`).
- **Consumer-cost dependencies the brief listed, checked one by one against "depends only on the
  footprint"**: where entries land / bytes re-walked: BREAKS (SIM-1); survivors after verify:
  holds only within one proof shape, and the cross-proof order rests on the independence estimate
  (SIM-1); presence fold: HOLDS (it is a footprint field; the backend adds the presence term per
  path); RECOVER: HOLDS for the kit's options at one site (the reverse pass runs per match, and the
  matches are the same for every option of one site; `landing`'s read of NEXT is a path-level
  read); per-artifact consumer variance (PS §7.4 item 7, 5x on the VM): not a break of the
  footprint rule but of "per-route" A_entry; the study already lists it as unlock 2; match phase:
  equal across one site's options (HOLDS), path-dependent across LOCATE rows (SIM-4).
- **Integer-unit note** (SRS knew the class): in today's 1/100-cycle unit the C_ENTER term of a
  RESEED option truncates to 0 on most sites (e.g. `foo(bar|baz)+` stop@3: 146 ppm entries x 2000
  /1e6 = 0.29 -> 0), so today PARKED's entries are priced and RESEED's are not; 8 of 22 integer
  picks differ from the integer frontier argmin, 3 of them pure truncation (`0x[0-9a-f]+`,
  `id="[^"]*"` verify depth; `(tion|sion)s?`). In exact arithmetic only the 5 MARGIN movers
  (SIM-3) remain.
- **Nesting (Q2.2)**: min-of-mins is exact once match_phase sits in the path (SIM-4); the hybrid
  prefilter, the handoff and presence put no route-dependent term outside the route's paths:
  HELD (3 term families checked).
- **Path as the unit (Summary 2)**: HELD. The selection graph (`cand_nodes[]`,
  emit_dfa.c:9930) has the PRESENCE -> NEXT (under PCREC_NO_REQ_HANDOFF) -> FIRST -> PRESENCE read
  cycle broken only by deny bits; FIRST has no standalone price; `jq[a-z]+x` and `foo(bar|baz)+`
  enumerated under default / -fno-req-handoff / -fno-offset-skip / both / -fno-req-byte (10
  compiles, probes q1-q10): 5 and 3 distinct paths, every one a joint (PRESENCE, FIRST, NEXT)
  choice. Tractability: 51 rows (LOCATE 4, PRESENCE 5, FIRST 4, NEXT 14, RETRY 6 priced; 6,720 raw
  tuples before route and validity cut them), times a kit frontier of <= 6 per window site (more
  under SIM-1/SIM-7): plain enumeration is tractable; no search heuristic is needed.
- **SRS price over the 10 SRS patterns** under the tie rule: 1 exact tie at timing-noise bands
  (SIM-6 (b)); the study's "most picks" worry does not arise unless rate error enters the band.
- **Cites checked**: window.c:620-622 (Table A contracts), :669-683 (MARGIN), :394, :420, :496,
  :710; emit_dfa.c:9930 (`cand_nodes[]`), :10087 (`cand_rs_dense_applies`), :9016
  (`req_landmark_admits`), :7280 (`next_key_holds`), :10154 (`cand_rows[]`, 51 rows counted by
  slot): all match the review tree.
- **Counts**: claims checked 9 (footprint exactness, frontier size, MARGIN deletion, nesting,
  separation condition, path unit, slot tractability, band definition, tie order); sites priced
  22 real-shape + 115,248 + 85,176 synthetic windows; compiler invocations 33 (all single
  patterns, `gnutimeout 30`); no matcher compiled or run; no make, no suite.
- No denied file opened. Read tool used only on the subject snapshot.

## STATE AT HANDOFF

- STATE: complete
- OWED: none
- Artifacts: `sim.py` + `sim_out.txt` (Parts 1-3c), `part4.py` + `part4_out.txt` (tie rule),
  `tie_check.py`, `price_orig.py`/`out_orig.txt` (SRS copies), `probe/` (emitted C of every probe).
