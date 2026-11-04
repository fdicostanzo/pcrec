# Review 2026-11-02 r3 — memfn-spanpick4 (design RE-CHECK of span_pick rev 4)

- **Subject:** docs/design/memfn/span_pick.md rev 4 at 76a7f02e75a3a39beea1d5959c326c3c2ac864a9 (lane/memfn-spanpick4);
  rev 3 base d3c4133cc. A build lands on main 5e8bcf455; review tree built there (memfn/src and src unchanged since the
  design's cite tree 959c08124, so every cite was checkable).
- **Rulings frozen:** main 5e8bcf455 (D186 + add. 1, 2; reviews r1, r2). **FREEZE DRIFT: none** (decisions.md,
  plan.md, roadmap.md unchanged on main at hand-back).
- **Coordinator:** crit-memfn-spanpick4 (opus). Critics opus x3, verifier sonnet. Draft: PROPOSED dispositions only.

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| SIM (simulate) | opus | run the minimax blind pick + with-data departure over the real data; implement from text first, diff vs smp20.py, recompute every quoted number, drill constructed outcomes | new rule (owner's minimax) |
| PREMISE (+ goals, sibling-of-family, general form + unlocks) | opus | test every assumption rev 4's additions rest on: the pure-function plan face and the minimax premises | new property + new rule |
| FIX (fix-induced + ruling check) | opus | does each rev-4 change / rev-3 fix hold, and what does it add untraced; are the owner rulings applied as written | re-check of a revised design |

Which lens caught what: SIM alone caught the wrong '/'-region thresholds (SIM-1), the DEF-arm mover (SIM-3) and the
unnamed with-data target (SIM-4). SIM and PREMISE independently found the minimax's dependence on irrelevant
candidates (SIM-2 = PREMISE-7). FIX alone caught the ruling-home problems (FIX-1, FIX-4, FIX-5) and the plan-row
cross-references (FIX-9). PREMISE alone caught that `log` is synthesized (PREMISE-5), the Poisson under-statement
(PREMISE-6) and the KEY-retirement contradiction (PREMISE-4 i). Two coordinator planted checks (one-plan target
already amended on main; ruling rows without durable homes) were both caught by FIX.

## Findings (consolidated) with PROPOSED dispositions

Severity: no answer-level finding (stage 1 is byte-identical and every priced rule is inert until stage 2's noise
exists). No speed finding measured; three findings predict speed-level mispicks at stage 3 (A2, A3, B3).

### A. The minimax rule as written (§The pick 1-4, §Robustness)

- **A1 = SIM-2 + PREMISE-7 (+ FIX-3 denominator part). VERIFIED HOLDS.** `loss_r = price_r / min_c' price_r` makes the
  pick depend on candidates that are never picked: smp20 stand-ins, {X,x} vs '/' picks '/'; add '4' (never picked)
  and the pick flips to {X,x} (720 such flips over a 435-point card grid). The candidate set moves with a row's
  levels, denies and every new method row (Growth rule), so a later card can move an earlier row's sites between two
  old plans: a mover in no row's evidence. Also unstated whether an unpriced/noiseless candidate enters the
  denominator. **PROPOSED: FIX-NOW (design text)** — either state the property and make any candidate-set change a
  choice event with its own census, or (leaning) use the IIA-safe pairwise form against the incumbent
  (`max_r price_r(c)/price_r(default)`), which still is a minimax-over-kinds of the departure's loss and so fits D186
  add. 2's words; if that reading is not the owner's, an owner question.
- **A2 = PREMISE-10 + FIX-6.** A minimax departure that is not Pareto against the default predicts a loss under some
  kind (smp20: '/' region would be ~3x slower under `log`); a row's condition cannot test a subject kind on a blind
  compile, so such losses can only be reverted whole or become owner exceptions, while Goal 2/§Staging read as if
  narrowing is the normal fix. **PROPOSED: FIX-NOW (text)** — state that a blind departure's predicted per-kind
  losses are known before the run, and how they are carried (pre-declared exception per row, or the pairwise form of
  A1 with a per-kind ceiling). Owner question only if the design wants a Pareto rule instead of minimax.
- **A3 = FIX-3 (tie transitivity), SUSPECTED, not verified.** Bands are pairwise; step 3 can send {c*, c2} to TIE and
  pick c2, which does not clear guard (b) against the default. No TIE row compares METHODS. **PROPOSED: FIX-NOW (one
  sentence)**: only candidates that clear guard (b) enter the tie set; name the method-level tie row or defer it to
  row 1's design.
- **A4 = SIM-5 + PREMISE-6 + PREMISE-8 (the band).** No coverage factor (a 1-sigma test departs ~16 % of equal-price
  comparisons per side); Poisson `sqrt(n)` is 0 at n = 0 and under-states clustered text 2-5x (weblog var/mean 4-20,
  VERIFIED); "first order through max_r and min_c'" is undefined at the kinks where decisions are close; a synthetic
  bundle has no sampling noise at all. **PROPOSED: PLAN** (stage 2 defines the noise channel; the design names now:
  coverage factor as a labelled UNMEASURED DEFAULT, a block-bootstrap noise per bundle byte, the kink rule) — a
  sentence each in the design now, the mechanism at stage 2.
- **A5 = PREMISE-4 (i) + SIM-7 + PREMISE-4 (ii). VERIFIED (ii).** Guard (b) needs "today's pick" at every admitted
  site forever, but rev 3 R7 still retires KEY by census at row 1 (unreachable, or guard loses its incumbent). In a
  with-data compile KEY reads the bundle ('4' for smp20/prose), so "the default" of steps 1-4 differs between the
  text (KEY under B?) and smp20.py (blind minimax). The python re-price must reproduce it exactly. **PROPOSED:
  FIX-NOW (text)**: define the incumbent (KEY under P in every compile, or frozen as a declared table) and restate R7.

### B. Numbers and the watched witness

- **B1 = SIM-1. VERIFIED.** "hit(PAIR) at least 4x hit(memchr) (8x at 5)" are grid points of smp20.py's 1/2/4/8x
  sweep, not boundaries: true thresholds 4.75x (hit 5), 3.5x (10), 2.75x (20), 2.25x (40). "At most 2x never minimax"
  fails at hit(memchr) >= 80 (out of plausible range). The stage-2 reading "is the card point in '/''s region" would
  misread 2.75-4x. **PROPOSED: FIX-NOW** (finer sweep in smp20.py, restate the region). The four byte(PAIR) ceilings
  and every price/worst-case value reproduce.
- **B2 = PREMISE-9. VERIFIED.** "'/' wins P and F ... at both": at hit(PAIR) 20 P's least is {X,x}. **FIX-NOW** (doc).
- **B3 = SIM-3. VERIFIED.** On the DEF-deny arm (PAIR filtered) the minimax moves today's '/' to '3' (W 4.055 ->
  1.974, gap 2.08, independent of hit(PAIR)), unforecast; Goal 2/5's RTE/DEF ratio then has a moving denominator.
  **PROPOSED: FIX-NOW** (witness table cell; judge smp20 per arm by new/old, not RTE/DEF, from stage 3).
- **B4 = SIM-4. VERIFIED.** "With data" names no departure target: four candidates beat {X,x} under prose; '4' vs '3'
  is counts 11 vs 19 (not significant). **FIX-NOW** (one sentence: depart to B's least, within-band to TIE; witness
  cell "'4' or '3'").
- **B5 = SIM-6.** smp20.py does not implement guard (b), TIE, the with-data band/incumbent, or walk/Horspool lines;
  P is labelled PRIOR_AUTHORED but read from `default` (same values). **DOC** (say what the script does not compute).
- **B6 = PREMISE-5. VERIFIED.** `log` is SYNTHESIZED (third_party/synth-log-lines-v1, `fidelity synthesized`), and it
  sets the worst case that rejects every digit stop; the ruling's "real data" has one real instance (`weblog`).
  **PROPOSED: owner question (via the kit)** — D186 add. 2 names `log`; the finding argues the ruling's purpose. Plain
  words: "the minimax was meant to lean on real text; one of the two named bundles is generated. Keep it as a kind,
  or count only real bundles?" Leaning: keep it (it is a known regime of job 588's subjects), but label it.
- **B7 = FIX-10, SUSPECTED.** After M2 (independent trigger) bare compiles price nothing, so smp20's witness and Goal 5
  "close via the first priced departure" cannot move without `--measures`; the design would call that a mechanism
  failure. **PLAN** (main records M2's ordering vs row 1 in [MEASURE-SET]; the design names the set each witness
  compile reads).

### C. The pure-function plan face (§The designer/emitter split)

- **C1 = PREMISE-1.** "A caller compares scenarios by calling again" has nothing to compare: the reply carries no
  price (trace only, an MFTRACE build) and through stage 1 not even method/frame. Sufficiency holds only at the
  revisit trigger. **PROPOSED: FIX-NOW (text)**: one plan is sufficient once the price is readable; until then
  scenarios compare by the bench.
- **C2 = PREMISE-2. VERIFIED PARTLY** (precision gap, not contradiction). The stage-1 call `mf_wdecide(art, site,
  out)` takes no frame (comment "reads no frame fact", window.c :1061; layer hard-coded finder.c :934); set and bundle
  are per-ART (`mf_art_begin`, compose.c :869-882), so a scenario differing in them needs a new art; per-art denies
  and levers are further inputs. **FIX-NOW (text)**: state per-call vs per-art axes.
- **C3 = PREMISE-3 + FIX-11 (part). VERIFIED.** "helper sharing ... read only by stamps (compose.c :1363-1417)" is
  false: `wused & ~wemitted` (runcmp.c :515), `simd_inc` (ofsskip.c :565-567) decide emitted text, first-use-wins. The
  PLAN stays pure; the emitting face is order-dependent, so 1d's "calls repeated and reordered, equal" witness must be
  scoped to the plan call. **FIX-NOW** (text).
- **C4 = FIX-2. VERIFIED PARTLY.** Breaker (c)'s reach counters are not write-only: printed by `reach_print`
  (gate.c :884-900) and READ by tests/memfn/rows_check.py (`asked` must equal phase=ask FD records); extra scenario
  calls change them (MFTRACE builds). `art->consulted` (stamp decider; rev 3 C7 sets it from T-PICK rows) is a
  future breaker not listed. **FIX-NOW** (text + 1d's witness: only the TAKEN call counts, or a probe mode).
- **C5 = FIX-11 (rest).** The §Staging 1d row omits the purity work, its witness and the roadmap edit (only prose
  carries them); (a)'s fix changes an error path in a no-mover unit. **FIX-NOW** (table row).

### D. Ruling application and records

- **D1 = FIX-1. VERIFIED** (planted check). D186 add. 2 says one-plan amends A-PLAN OPEN POINT 1; main already made
  that edit (5e8bcf455, not on the branch); rev 4 says it amends the "next step" and schedules a roadmap edit in KIT
  unit 1d; source cited as "memfn journal 2026-11-03" instead of D186 add. 2. Residual roadmap texts (:107, :382-385,
  :387) still say "candidates and cards". **FIX-NOW**: cite D186 add. 2; residual roadmap lines as a request to main.
- **D2 = FIX-4. VERIFIED.** `zen4-grid2` is already D167's grid run (GO 2026-10-16, ran; zen4-grid1 PROVENANCE owes a
  recompute to it; regime_eval E5 waits on its fit cells). Stage 2 cannot reuse the id under the very rule rev 4
  cites (measures.md §8¶1). **FIX-NOW** (pick a fresh id, or state the Oct-16 run is superseded and who owns its
  readers) + main records it (D176 Q3 is an owner ruling; "main, 2026-11-02" has no durable home).
- **D3 = FIX-5. VERIFIED.** Four of seven "owner rulings since rev 3" rows have no durable home at the freeze: rev 3.1
  (incl. widening witness (2) from r2's RULINGS "must switch to '/'" to "'/' or '4'"), O3 = WAIT, the pure-function
  property, and one-plan's cited source. **PLAN for main**: file the decisions lines (and plan rows) before the build
  go; the design then cites them.
- **D4 = FIX-8. VERIFIED (text).** The PREFIX/KA/KB exception's new retiring trigger ("the first SIMD T-PICK row")
  cannot retire it (PREFIX still picks rungs on every site the row does not admit): use the census rule. C9's
  witness (a two-byte window with a look-ahead) is not a "stated core position" the 1d candidate builder produces;
  SIMD-form cards have no layer/form key column. **FIX-NOW** (trigger) + **PLAN** (C9 candidate shape and card keys
  belong to the SIMD row's own design).
- **D5 = FIX-9. VERIFIED.** C9's witness is plan [COVER-PRICE-WITNESS], a SCALAR loss too (x1.95, bar "no slower on
  BOTH layers"), uncited; a SIMD-only row cannot close its scalar half. O3's "look-ahead" is [PAIR-LOOKAHEAD-TIME],
  whose own trigger fires inside stage 2. **FIX-NOW** (cite both tags; say who answers the scalar half; say whether
  stage 2 carries the look-ahead sweep).
- **D6 = FIX-7, SUSPECTED.** "The shipped bundles" as blind kinds makes shipping/re-counting a bundle a pick-moving
  event with no stamp, census or §What-moves line. **PLAN** (the kind list a declared, versioned fact, stamped).

### E. Goals and families

- **E1 = PREMISE-11.** Goal 5's blind clause is conformance, not an outcome (the forecast keeps the loss); checkable
  only once A1/A4/A5 are fixed; the decider census grep shapes miss a `max_r` minimax loop. **DOC** + census shape
  added with A1.
- **E2 = PREMISE-12.** Family: M's MARGIN, guard (b), T_BAND -> TIE_DEFAULT and pcrec's `pcrec_landmark_margin` are
  four "beat the incumbent by a margin" spellings; KEY-reads-B and the with-data departure are two bundle data paths;
  `mf_ask`, `mf_wdecide`, `mf_pres_ports` are the pure-query family the plan face generalises. **NOTED** (name them
  in the design; unify at row 1, trigger the `enter` cards).

## PROBED-AND-HELD (summary; detail in review/)

- Every price (5 kinds x 4 columns + bracketed), every minimax worst case (9 values) and the four byte(PAIR) ceilings,
  "{X,x} to 4.20x/3.25x", job 588's none cell (~2.27x) reproduce from an implementation written from the TEXT (SIM)
  and from smp20.py (FIX, PREMISE).
- witness.sh re-run on the review tree: byte-identical to the committed witness.out (8 compiles).
- Purity-breaker cites: 13 kit cites + 15 pcrec/carried cites resolve; no other mutable static, getenv, clock, rand or
  cache in memfn/src (PREMISE: grep complete for statics).
- D186 add. 2 minimax, D186-over-D144 and C9 rule 6 applied as written (FIX part 1).
- r2 dispositions: 17 ids sampled, all hold in rev 4 except where FIX-4 (C5's new id) and FIX-1 (O4) reopen them.
- F as a kind matches job 588's `random` regime; `log`/`weblog` are shipped bundles with raw counts.

## By-id completeness

SIM-1 B1, SIM-2 A1, SIM-3 B3, SIM-4 B4, SIM-5 A4, SIM-6 B5, SIM-7 A5; PREMISE-1 C1, -2 C2, -3 C3, -4 A5, -5 B6, -6 A4,
-7 A1, -8 A4, -9 B2, -10 A2, -11 E1, -12 E2; FIX-1 D1, -2 C4, -3 A3 (+A1), -4 D2, -5 D3, -6 A2, -7 D6, -8 D4, -9 D5,
-10 B7, -11 C3/C5. 30 critic findings -> 21 consolidated items.

## D27 recommendation

The pick rule is now a self-contained function of declared inputs (prices per kind, bands, default): RECOMMEND a
spec-first test author for the pcrec-side python re-price at row 1 (tests from the rule's text: IIA, tie-set, band,
incumbent cases), once A1/A3/A5 settle the text.

## Lessons for the guide (proposed)

1. A design that quotes a REGION boundary from a sweep must say the sweep's grid; a boundary equal to a grid point is
   unproven (SIM-1: "at least 4x" was the 1/2/4/8x grid).
2. A choice rule with a normaliser over the candidate set (ratio-to-best, regret) must state whether it is
   independent of irrelevant candidates; the simulate lens adds "add a never-picked candidate" as a standard drill.
3. Every "owner rulings since rev N" table row cites its durable home at the freeze (decisions.md line), or is marked
   PENDING-RECORD; the ruling-check lens greps each.

## RULINGS (kit manager, 2026-11-03)

- All PROPOSED dispositions ACCEPTED, with these choices:
  - **A1**: adopt the PAIRWISE minimax against the incumbent. For a challenger c, each kind's loss is measured against the better of {c, today's pick}; c departs only when its worst loss beats the incumbent's worst loss by more than the band. Among several qualifying challengers, take the best such improvement (A3: only qualifiers enter the tie set). This is still "least worst-case loss" (D186 add. 2) and is independent of never-picked candidates. The owner is told in plain words.
  - **A2 goes to the owner**: does the minimax rule itself approve the per-kind losses a departure predicts IN ADVANCE (listed per row before its run, so that an unpredicted loss is a mechanism finding), or does each such loss need its own owner exception? Kit leaning: the rule approves predicted, listed losses.
  - **B6 goes to the owner**: `log` is synthesized. Keep it as a kind, labelled, or count only real bundles? Kit leaning: keep it, labelled.
  - **D1, D2, D3**: requests to main (residual roadmap lines; a fresh measurement-set id, or the 10-16 run superseded; durable homes for the four unrecorded ruling rows).
- Lessons 1-3 ACCEPTED: the skill's simulate row and docs/dev/guide/critics.md, in this commit.
