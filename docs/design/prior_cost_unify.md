# [PRIOR-COST-UNIFY]: one priced scan decision (DESIGN NOTE, revision 2)

Revision 1: lane `pcudes`, 2026-10-11, read at main `85f3ef1d`.
Revision 2: lane `pcurev`, 2026-10-11, read at main `4a9748bb` (abi 75). It
applies the light D6 panel r3 (`docs/dev/reviews/2026-10-11-r3-prior-cost-unify.md`,
critics' texts in `docs/dev/reviews/2026-10-11-r3-prior-cost-unify/`). Every
finding was ACCEPTED, and each disposition is marked `[r3 ID]` where it lands.
Design only: nothing under `src/`, `tests/` or `docs/spec/` moves. Instruments
and probe outputs are in `prior_cost_unify/` (own CLAUDE.md).

Inputs: plan.md [PRIOR-COST-UNIFY] (with its SHARED VOCABULARY note),
[ADAPTIVE-ARM], [SIZE-KNEE], [EFFORT-BUDGET], [START-DENSE],
[OPT-HYB-RESEED-POLICY], [EST-REGISTRY]; `docs/dev/optloop/lossreview/fixes.md`
rev 2 §1 F1; `src/opt/prefix_k.c` `model_cost`; D126 Q4/Q5, D141, D144 add. 4,
D146, D148, D149, D151, D152, D153, D157, D158 (+add. 1), D160; K102, K105;
`rlhbuild_report.md` §1.4, §7; `match_split_requirements.md` §3.3, §5.1;
`litscan_k82b.md`; `where_to_start.md` §2.4; `rewtwin_report.md`.

## §R2 — what revision 2 changed, by finding id

| id | what changed | where |
|---|---|---|
| S1 / F9 | The framed reseed gap is relabelled MEASURED: the smallest crossover of its class's witnesses. The formula gap = ⌈reseed/attempt⌉ is withdrawn because its own table refutes it (frameless predicts 16, measures 16/26/30). The U3 VF.gap mover and rev 1 §8(a) are DROPPED. | §3.2, §5.1, §8 |
| S2 / F1 | D158's check is now a PER-COUNTER vector (steps, work, frames, trail): each metered counter's charge with the row on must be ≤ the denied form's. A weighted sum is its later projection, once [EFFORT-BUDGET] rules weights. The meter cell is a column on `axes.def` (population = all 44 axis rows; K35 floor 44). DELETES/ADDS are DERIVED from the emitted charge sites with the axis on and denied, then compared with the declaration. K102 is carried only as D158 add. 1's exact-key allowance. §0 item 4 is restated. | §0, §3.5, §8 |
| S3 | U1 members read `stop_ppm`, never an advance. Each per-member quirk is an ADAPTER row with its reach (A1-A5). Rounding direction is a parameter of the product. | §4.2 |
| S4 | [MATCH-SPLIT]'s END admission stays OFF the primitive as a decision. It is stated as a conservative proxy, valid for single-stay END arms only. The first-passage-time UNLOCK is filed with its trigger. | §4.5, §7.3 |
| S5 | The signature gains `step_k` (Q) and `stepped_ppm` (Exp). NONE = every byte stepped and ZERO stops. The stepped term's saturation is handled per linear piece. | §2.1-§2.3 |
| S6 | #11's break-even is now `reentry / (step_byte − skip_byte)` over the STAY run t/(1−t), declining when step ≤ skip. DU/DR cells are split. #11 leaves "switch now", and its plumbing is listed. | §3.2, §4.3 |
| F2 | Sabotage rows 1-2 are rebuilt. Row 1's plant sits inside `pcrec_scan_expect`. NONE asks are counted per encoding from the `<P>_FINDINGS "byte-rate=none"` stamp. A synthetic bundle with no `serves` for the compile's encoding is the standing NONE witness. | §5.4 |
| F3 | The disagreement count becomes an arithmetic GRID per formula pair with planted off-by-ones (prototype: `prior_cost_unify/grid.py`). The corpus only names populated regions. emit_sweep decides movers. #3's exactness is proved. | §5.4, §5.2 |
| F4 / S8 | Two references: the pinned old `model_cost` for U0, and exact rationals for the verdict's arithmetic. Every rounding is stated. The cost has no division at all, because the numerator is scaled. A core-owned UNSIGNED helper is added, with a static magnitude bound under which it never saturates, asserted twice. | §2.4, §5.4 |
| F5 | The census is DERIVED by call graph from the `pcrec_find_*` rate primitives, with a completeness check (`prior_cost_unify/census.py`, exit 1 on an undispositioned or stale reader, failing direction run). It finds 10 roots and 14 readers: 10 decisions in 9 functions. `pcrec_find_run_rank`'s reader is found (#21). Counts are fixed. Unbuilt members are added: rev-inner G3, and rev-end-width vs rev-end. | §1.1 |
| F6 | The kit-field mapping is written: per-term vs post-conjunction, point vs range, and unknown (0..FULL) wherever only the independence estimate exists. `rank_ppm` is named as a consumer. | §4.6 |
| F7 | Q1 is restated with the RQ-2 precedent. (ii′) rank facts for the k-set offset is the D157-shaped end; (i) is an interim with an expiry trigger. | §7.1 |
| F8 | MANAGER (Q3): same-box ratios only, no cross-box derived cells, ISA/libc recorded per cell. | §3.2, §7 |
| F10 | No numeric accessor exists for an UNSET or UNMEASURED cell. A read fails the build, or the reader is listed `uses-unmeasured`. U2 for #4 and #7 is blocked until `stop_reentry` is measured. | §3.3 |
| F11 | Control (c) is the kind-aware call-graph census with a floor. (d) is labelled an INSTRUMENT. Reach comes from stamps. | §5.4 |
| F12 | Folded in: RQ-2; `vm_reseed_cal`'s gap/arm split as ONE row set owned by the runtime-arm family; START-DENSE + ADAPTIVE-ARM + OPT-HYB-RESEED-POLICY named ONE family to be ONE table; #11 vs DFA_SELECT; EST-REGISTRY's stray-literal detector (owed); the RETRY rows of `cand_rows[]`; U0's listing as a D80 surface. | §4.4, §5.1, §5.5 |
| S7 | Both forms of the advance duality are defined. The complement is `10^6 − mass(T)`, never `MASS(¬T)` (they differ by flooring under NONE). | §2.2 |
| S9 | `adv_milli` is deleted. An advance is a RATIONAL `10^6 / stop_ppm`, compared by cross-multiplication. stop_ppm 0 = never stops. | §2.2 |
| S10 | F-1 is restated with its `nverify == 0` conjunct (the run-pinned row is a singleton scan WITH a run verify). | §1.2 |
| S11 | #8's 256 is structural. D149's label belongs to the \|S\| = 1 → memchr cut-over. verify(chain) is SUM at U0/U1; U2 states short-circuit (a counted mover). | §1.1, §4.1 |
| S12 | "every DFA route row: trivially" is scoped to DFA-ONLY artifacts. A hybrid's inlined DFA prefilter changes VM attempts (99,601 vs 1). | §3.5 |
| S13 | Citations fixed: `rn_better` req.c:327, D126 Q5 decisions.md:8655, 10.7 vs 7.751 (src/gen/CLAUDE.md:2565), 11 of 1,352 (offset_k_skip.md:366, with the periodic-steady-state caveat), `pcrec_req_window` req.c:667. | §1.2 F-5 |
| manager | Q2, Q3, Q5 are recorded as SETTLED. §7 keeps only Q1 and Q4, each with forces and a leaning. | §7 |

Two findings are new to revision 2. Both came from the instruments the panel
asked for:
- **F-8.** A second D158 violator, the [ENG-ISL] alternation island. It
  charges WORK for its trie bytes where the denied form spends STEPS. Witness:
  `(foo|bar|baz)q` on `fooq` at `--work-budget=2`. The default build gives up
  (`work`, on the default engine selection too) and `-fno-alt-island` answers
  (0,4).
- **F-11.** On its witness, the literal-run row's static meter delta is
  DELETES, not the SUBSTITUTES rev 1 declared.

§8 lists both.

---

## 0. Answers first

1. **The family, derived (§1).** Ten decisions read the byte-rate prior
   today. A call graph walked backwards from the ten rate primitives in
   `src/core/findings.c` finds them, and a completeness check fails on any
   undispositioned or stale reader.
   - Of the ten: one COMPARE (G1), six PICKs (set-leads, run window start,
     run scan index, run pin, req pick, the RQ-2 rank) and three cost
     comparisons, the kind this note calls VERDICT (R4, the handoff K
     admission, the `prefix_k` planner).
   - A call graph cannot find a decision that SHOULD read the prior and does
     not. Ten of those are listed by hand and labelled so: six built (a byte
     count, `|S| < 256`, `T ⊊ E`, an always-applies row, `MIN_SCAN_CHAIN`,
     the run choice by information) and four unbuilt (deferpre,
     [MATCH-SPLIT] END, rev-inner G3, rev-end-width vs rev-end).
   - Six more are not decisions.
   - VERDICT's NONE answer is MASS's cardinality. It moves nothing, because
     every VERDICT member already prices that way (§1.3).
2. **The primitive (§2).**
   - `pcrec_scan_expect` turns a scan's FACTS into EXPECTATIONS: a stop rate,
     a pass rate (an independence estimate, labelled), and a stepped-byte
     rate, the bytes the engine walks itself.
   - `pcrec_scan_cost` prices them against a consumer row.
   - `pcrec_scan_verdict` compares two alternatives under a caller's bar. It
     returns PAYS or DECLINE, plus the break-even stop rate, which is the
     [ADAPTIVE-ARM] hook.
   - **NONE (no scan) is zero stops and every byte stepped.**
   - The arithmetic is unsigned, has no division in the cost, compares by
     cross-multiplication, and is bounded statically so that saturation is
     unreachable. Every rounding is stated (§2.4).
3. **The operation-kind table (§3).** It is one grid, route × program class
   by operation kind, with two planes. MEASURED is for selection: per-box
   cells, same-box ratios only. CONTRACT is [EFFORT-BUDGET]'s meter: every
   cell UNSET today.
   - **No numeric accessor exists for an UNSET or UNMEASURED cell.** A reader
     that needs one fails to build, or is listed `uses-unmeasured`. So the
     restart term `stop_reentry`, the term the row exists to add, blocks
     every U2 that prices it until it is measured.
   - The two kit-form constants are Q1.
4. **D158, per counter (§3.5).** Each optimization axis declares, per metered
   counter (steps, work, frames, trail), whether its charge with the axis on
   is ≤ the denied form's. The declaration is a new `axes.def` column.
   - A table-build check reads the column. An independent control DERIVES
     the class from the emitted charge sites with the axis on and denied.
   - The prototype (11 witnesses) reproduces K102's class on possessify. It
     also finds the alternation island in the same class, and that one is
     not allowed: F-8, a second D158 violator, shown dynamically.
   - The weighted single-budget form is the per-counter check's projection,
     once [EFFORT-BUDGET] rules weights. It is not built here.
5. **Migration (§5).**
   - U0: the table, the primitive and the helper, with `model_cost` moved in
     verbatim. Zero movers, and no caller-visible surface (the listing is a
     separate step, U0b, with its D80 hunk).
   - U1: each member reads its INPUTS through the primitive via its listed
     adapter. Zero movers.
   - U2.k: per member, a formula switch gated by the arithmetic grid, then
     emit_sweep.
   - U3: `C_ENTER` re-measured on one box.
   - U4: the meter column and its two checks.
   - U5: K105.
6. **K105 (§5.3).** An exemplar bundle ALREADY declines the re-entry today,
   with no build. Measured compile-side: hcolon_in's NEXT row goes from
   `handoff` to `byte-class` under a colon-dense exemplar. So the arm is
   needed only without an exemplar, and it is a member of ONE runtime-arm
   family (Q4).
7. **Settled by the manager:** Q2 (`estimates.def`), Q3 (same-box ratios
   only), Q5 (the labelled independence product). **For Frank (§7):** Q1 and
   Q4.

---

## 1. Census

### 1.1 The members, DERIVED, read at main `4a9748bb`

**Method `[r3 F5]`.** `prior_cost_unify/census.py` reuses
`docs/design/start_table/call_graph.py`'s parse: every top-level definition
under `src/`, its body, and an edge to every definition the body names.
census.py runs that parse with call_graph.py's own output discarded, then
walks BACKWARDS from the RATE PRIMITIVES. These are the `pcrec_find_*`
definitions in `src/core/findings.c` whose answer is a byte-rate prior or a
choice made from one:
- **Roots.** Every other `pcrec_find_*` there (store access, resolution,
  digests, the stamp, the normalizer) is listed in the script's `NOT_RATE`
  with a reason. A new primitive classified as neither is exit 1.
- **Readers.** A reader is any definition whose body names a root or a
  CARRIER.
- **Carriers.** A carrier hands a rate or a pick on, and its own readers are
  walked too.
- **Dispositions.** Every reader is dispositioned in
  `prior_cost_unify/census_disp.tsv` as MEMBER, CARRIER or NOT.
- **Failures and floors.** An undispositioned reader or a stale disposition
  is exit 1. The root count (10) and member count (9 functions) are K35
  floors.
- **Failing direction, run:** deleting `ofs_pred_rank`'s row reads
  `UNDISPOSITIONED reader ofs_pred_rank ... member count 8 below floor 9`.
  Adding a `rn_better` row reads `STALE disposition rn_better`. Output:
  `prior_cost_unify/census.tsv`.

**Part A: derived, reads the prior (10 decisions, 9 functions).**

| # | member | file:line | decides | reads | kind |
|---|---|---|---|---|---|
| 1 | G1 density | `src/gen/emit_dfa.c:7530` `req_byte_dominated_by` (site :7538) | elide a one-byte pre-check whose byte is no rarer than the scan's | `pcrec_find_no_commoner` | COMPARE |
| 2 | set-leads | `emit_dfa.c:7584` `req_set_leads_applies` (:7590, :7595) | emit the set pick's memchr ahead of the run search | `pcrec_find_pick` over [run scan cube, set pick]; carrier `req_set_pick` (:7544) | PICK |
| 3 | R4 adaptive-dense | `emit_dfa.c:8739` `cand_rs_dense_applies` (:8740) | RETRY row `adaptive-dense` | carrier `pcrec_dfa_cand_ppm` (:7427, site :7450, `pcrec_find_set_ppm`) × `CandVmFacts.reseed_gap` | VERDICT |
| 4 | handoff K admission | `emit_dfa.c:7786` `req_landmark_admits` (:7789-7795) | NEXT row `handoff` (the re-entry) | carrier `req_landmark_hit_ppm` (:7753; `pcrec_find_set_mass` :7761, :7765), `pcrec_find_set_mass` for the displaced row | VERDICT (an advance comparison today, §5.2) |
| 7 | prefix_k planner | `src/opt/prefix_k.c:179` `pcrec_prefix_ksets` (:187, :201), `model_cost` :114 | scan offset k* and verify chain | `pcrec_find_set_ppm` per offset | VERDICT (an argmin planner, D152) |
| 13 | run window start | `src/facts/req.c:667` `pcrec_req_window` (:684) | which 8-position window of a long run | `pcrec_find_run_window_start` (SEQUENCE MASS) | PICK |
| 15a | run scan index | same function (:682) | the run member the memchr scans | `pcrec_find_run_scan_index` | PICK |
| 14 | run pin | `src/facts/kset.c:298` `pcrec_run_pin` (:309) | the exact stretch the pin claims | `pcrec_find_pick` | PICK |
| 15b | req pick | `src/facts/req.c:709` `pcrec_req_pick` (:716) | the set's pick, unless an exact run member ships | `pcrec_find_set_pick` | PICK |
| 21 | RQ-2 rank | `emit_dfa.c:1181` `ofs_pred_rank` (:1185) | the kit's position RANKING facts (D157) | `pcrec_find_run_rank` | PICK (the full order) |

Carriers: `pcrec_dfa_cand_ppm`, `req_landmark_hit_ppm`, `req_set_pick`.
NOT: `req_lead_byte` (:7643) emits #2's byte, and `pf_derive`
(`src/facts/facts.c:233`) is the fact epoch's driver handing the accessor to
#14. Rev 1 missed #21 (`[r3 F5]`). It also read #13 and #15 as two rows where
the code has three decisions in two functions.

**Part B: decisions that compare scan alternatives WITHOUT the prior (10,
hand-listed and labelled).** No call graph from a rate primitive reaches a
decision that does not call one. What would derive this part is a census of
hand-set selection constants, which is [EST-REGISTRY]'s stray-literal detector
(owed, §5.5). Until then this list is a hand judgment, and it says so.

| # | candidate | file:line | today's test | would be |
|---|---|---|---|---|
| 5 | run choice | `src/facts/req.c:327` `rn_better` | information Σ popcount(K), floor `PCREC_MIN_REQ_RUN_BITS` 16 (`limits.def:405`, RULED) | PICK by a VERDICT, outside the fact (F-3) |
| 8 | VM hat admission | `emit_dfa.c:7176` `pf_vm_start_applies` | `\|S\| < 256`, not nullable. **The 256 is STRUCTURAL** (`[r3 S11]`): \|S\| = 256 means every byte is a candidate. D149's UNMEASURED label belongs to the \|S\| = 1 → memchr cut-over, not to this. | VERDICT (MASS admission filed, D148 add. 2 Q-R5) |
| 9 | DFA hat admission | `emit_dfa.c:7019` `pf_dfa_start_set` | T ⊊ E (structural) | VERDICT (mass + entry, K91) |
| 10 | plain byte-class rows | `emit_dfa.c:9009`, `:9016` (`cand_rows[]`) | always applies | VERDICT (hex8 under `-fno-start-set`) |
| 11 | M2.1 stay states | `emit_dfa.c:4777` `pick_skip_states` (`bestcnt = 191`, :4783) | stay-set byte COUNT ≥ 192 | VERDICT by break-even (§4.3) |
| 18 | scan-chain floor | `limits.def:392` `PCREC_MIN_SCAN_CHAIN` 2 | constant (MEASURED null at m = 2..4) | VERDICT (time half); HELD |
| u1 | deferpre | (unbuilt) | K = 64, UNLABELLED | label it UNMEASURED DEFAULT (D149) when built |
| u2 | [MATCH-SPLIT] END admission | (unbuilt; `match_split_requirements.md` §3.3, §5.1) | expected suffix walk vs the free locator's gap | a CONSERVATIVE PROXY only (§4.5) |
| u3 | rev-inner G3 | (unbuilt; `where_to_start.md` §2.4) | `ppm(L's scan byte) ≤ ppm(today's key) / F`, F = 2 | COMPARE with a bar; a VERDICT candidate once `stop_reentry` exists |
| u4 | rev-end-width vs rev-end / end-minus-width | (unbuilt; `rewtwin_report.md` §0) | a W-byte forward verify at n−W vs a reverse walk | VERDICT on `DR.walk_byte` vs `verify`: the second reader of `DR.walk_byte` (§3.2) |

**Part C: not decisions (6).**

| row | file:line | what it is |
|---|---|---|
| G2 one-attempt | `emit_dfa.c:7489` `req_route_one_attempt` | a route fact (fixes.md r2 F5) |
| utf8 rate NONE | `findings.c:390` `pcrec_find_byte_rate`; stamp `<P>_FINDINGS "byte-rate=none"` | data: D160's authored prior is its fix |
| find floor | `limits.def:186` `PCREC_FIND_FLOOR_PPM` 2 | bounds the primitive's denominators (an advance ≤ 500,000 B) |
| stay pass cap | `emit_dfa.c:4782` `pass < 4` | capacity, [SIZE-KNEE]'s |
| prefix_k singleton gate | `prefix_k.c:225` `count != 1` | form scope inside #7. UNLOCK: the kit's cube FIND row (trigger ci-moskva) |
| reseed calibration | `src/gen/emit_vm.c:11033` `vm_reseed_cal` | data, owned by the runtime-arm family (§4.4) |

**Score `[r3 F5]`.** The 26 rows break down as follows:
- **10 derived decisions:** COMPARE 1 (#1), PICK 6 (#2, #13, #14, #15a,
  #15b, #21), VERDICT 3 (#3, #4, #7).
- **6 built candidates:** VERDICT 5 (#8, #9, #10, #11, #18), PICK 1 (#5).
- **4 unbuilt candidates.**
- **6 not decisions.**

VERDICT, the kind the row is about, has 3 members that read the prior and 9
candidates. Rev 1's "twenty" was 21 rows under a twenty heading, and it missed
#21, u3 and u4.

### 1.2 Findings from the census

- **F-1. G1's `memchr_form` clause is a stop-set FACT, not a kit-form cost,
  WITH its `nverify == 0` conjunct `[r3 S10]`.**
  - `memchr_form` holds where the selected NEXT row scans one byte at the
    candidate start. The rule that clause encodes is a singleton at the start
    with NO verify chain.
  - The run-pinned row scans a singleton (`nsel == 0`, `sp == 0`,
    `emit_dfa.c:6602-6604`), but WITH a run verify, and `memchr_form` is
    false there. G1 is answer-equal on it only because its run conjunct
    returns first (:7534-7536).
  - So the shape the COMPARE is scoped to is
    `exp.shape == SINGLETON_AT_START && nverify == 0`.
  - Generalizing it (a set scan compared by mass) would be a mover. It is
    filed, not proposed (D77).
- **F-2. The family's NONE answers already differ, and correctly.**
  - G1 (COMPARE) answers `false`.
  - The VERDICT members price with cardinality inside MASS.
  - The PICK members take the cardinality argmin, ties to the reader's
    rightmost.
  - A single NONE answer would move G1 under `-e utf8`, so the kinds stay
    distinct (§2.5).
- **F-3. RUN-PICK's fix cannot live in `rn_better`** (`src/facts/req.c:327`).
  D126 Q5 (`decisions.md:8655`) excludes route and emission decisions from
  the record. The general form is D157's: the fact states the candidate runs,
  ranked, and the consumer picks through the verdict.
- **F-4. set-leads and G1 are VERDICTs wearing a cheaper kind.** K85 is
  set-leads' gap, measured. Neither is proposed for change (D77).
- **F-5. The constants come from two boxes, and one input is stale `[r3
  S13]`.**
  - `prefix_k`'s cost constants are Zen 1 (ubuntubudu). `vm_reseed_cal`'s
    calibration is the Mac M1.
  - `C_ENTER` = 10.7 c/B × "~2 bytes". 10.7 is the pre-[OPT-3] figure, and
    the premultiplied table measured 7.751 (`src/gen/CLAUDE.md:2565`). But
    7.75 is a PERIODIC steady-state throughput, while `C_ENTER` prices a
    FALSE ENTRY that survives ~2 bytes, so the substitution is not automatic
    either.
  - 11 of 1,352 corpus patterns change their k-set between 12 and 20 cycles
    (`offset_k_skip.md:366`).
  - **Correction to rev 1:** rev 1 said "R4 multiplies a Zen 1-shaped rate
    by a Mac-shaped gap". A RATE is a byte frequency and box-free. Only the
    COST cells carry a box, and R4 reads one box's crossover. No shipped
    verdict mixes boxes today. Q3's settled rule keeps it so.
- **F-6. `limits.def`'s "selection knee" rows are caps and floors, not
  prices.** They stay where they are (Q2 settled).
- **F-7 (new). The set's pick is spelled twice:** `pcrec_req_pick`'s last
  line (`req.c:716`) and `req_set_pick` (`emit_dfa.c:7547`). It is the same
  primitive with the same arguments, so the answers are identical by
  construction. It is a census finding, not a defect: fold the emitter's copy
  into a read of the fact when PRESENCE next moves.

### 1.3 VERDICT: the kind the row is about

A VERDICT compares two scan ALTERNATIVES by expected cost per subject byte.
- **Members that read the prior:** #3, #4, #7.
- **Candidates:** #8-#11, #18 time half, u1-u4.
- **Its NONE answer, spelled once (D126 Q4):** price with MASS's NONE answer
  (cardinality). Every member that reads a rate already does this: #3 through
  `pcrec_find_set_ppm`, #4 through `pcrec_find_set_mass`, #7 through
  `pcrec_find_set_ppm`. The rule moves no byte.
- **Inheritance:** the "no scan" shape has its own definition (§2.2: zero
  stops, every byte stepped). It is NOT MASS of the whole alphabet.

---

## 2. The primitive

### 2.1 Facts in `[r3 S5]`

```c
/* A scan as FACTS: what it stops on, what it checks at each stop, and how
 * many bytes the engine walks itself per stop. No form appears (D146). */
typedef struct {
    PcrecScanShape shape;      /* SINGLETON_AT_START, SET, CUBE_RUN, NONE      */
    const uint8_t *set;        /* SET / SINGLETON: the stop set (256 flags)    */
    const unsigned char *bytes, *mask;   /* CUBE_RUN: positions (T, K)          */
    int            n;          /* CUBE_RUN: positions                          */
    int            nverify;    /* the verify chain, ascending offset; <= PCREC_SCAN_VERIFY_MAX */
    const PcrecVerifyTerm *verify;
    long long      step_k;     /* bytes the ENGINE walks itself per stop: 0 for
                                * a scan that hands a candidate; K for the
                                * handoff (it restarts K bytes back); unused for
                                * NONE, which steps every byte by definition    */
    PcrecRound     round;      /* the CUBE_RUN / verify-chain product's per-step
                                * rounding: UP (the landmark's, declining) or
                                * DOWN (prefix_k's chain): a PARAMETER, never a
                                * silent choice ([r3 S3]) */
    long long      span;       /* proven span bound, or PCREC_SPAN_UNKNOWN     */
} PcrecScanQ;
```

`PCREC_SCAN_VERIFY_MAX` is derived as `max(PCREC_OFSK_MAX_SET,
PCREC_MAX_REQ_RUN_EMIT)` = 8 and asserted (§2.4).

### 2.2 Expectations out `[r3 S5, S7, S9]`

```c
typedef struct {
    uint32_t stop_ppm;    /* stops per 10^6 subject bytes. SET: MASS(set).
                           * CUBE_RUN: the product over positions, rounded per
                           * step by q->round. NONE: 0 (no scan, no stops)   */
    uint32_t pass_ppm;    /* of the stops, the fraction passing the verify chain:
                           * the product of the terms' masses, rounded per step
                           * by q->round. INDEPENDENCE ESTIMATE, labelled
                           * (Q5 settled). Never a match probability.         */
    uint32_t stepped_ppm; /* bytes the engine walks itself per 10^6 subject
                           * bytes: min(10^6, stop_ppm * step_k); NONE: 10^6  */
    PcrecRateSrc src;     /* RATE | NONE, the accessor's answer, recorded    */
} PcrecScanExp;

void pcrec_scan_expect(Ctx *cx, const PcrecScanQ *q, PcrecScanExp *e);
```

**NONE is zero stops and every byte stepped `[r3 S5]`.** Rev 1 charged a
no-scan alternative as 10^6 stops each paying re-entry, verify and attempt,
plus every byte stepped. That charged it twice, and it biased every verdict
toward scanning once `stop_reentry > 0`.

**The advance is a RATIONAL, not a field `[r3 S9]`.** `adv = 10^6 /
stop_ppm` subject bytes per stop. A reader that compares advances does so by
cross-multiplication (`pcrec_scan_adv_lt(e, num, den)`). stop_ppm 0 means the
scan never stops, and the advance is infinite. Rev 1's `adv_milli` (`10^9 /
stop_ppm`, truncated) had a wrong bound and a truncation a boundary could flip
on. Under a ceil-per-step product stop_ppm reaches 1, so adv_milli reaches
10^9, not the 5 × 10^8 rev 1 stated. Floor products reach 0, which #4
special-cases (`if (h == 0) return true;`, `emit_dfa.c:7797`). Deleted.

**The advance duality, both forms `[r3 S7]`.** Let t be the mass of a STAY
set T (a state that stays on T):
- **The stay RUN** (bytes stayed before the exit byte) has expectation
  t/(1−t). It is what a stay skip saves (#11, §4.3).
- **The run plus its exit byte** has expectation 1/(1−t). It is the advance
  of the scan that stops on T's complement, and the length of a walk that ends
  on the exit byte (an END walk, §4.5).
- **The complement's mass is defined as `10^6 − mass(T)`**, exact by
  definition. It is never computed as `MASS(¬T)`. Under NONE,
  `uniform_mass(k) + uniform_mass(256 − k) = 10^6 − 1` for most k (both
  floor), so the two spellings differ.

### 2.3 The consumer price and the verdict

```c
/* Expected cost of running scan `e` in front of consumer row `c`, as a
 * SCALED NUMERATOR N = 10^6 x (cost per 10^6 subject bytes), in the row's
 * native unit. No division anywhere. */
uint64_t pcrec_scan_cost(const PcrecScanExp *e, const PcrecOpRow *c,
                         uint32_t scan_byte /* KIT-ESTIMATE or 0, §3.4 */);

/*   N = 10^12 * scan_byte                               (the kit's scan, §3.4)
 *     + 10^6  * stop_ppm * (stop_reentry + verify(chain))  (pcrec, per stop)
 *     +         stop_ppm * pass_ppm * attempt              (pcrec, per false entry)
 *     + 10^6  * stepped_ppm * step_byte                    (pcrec, bytes walked)  */

typedef enum { PCREC_SCAN_PAYS, PCREC_SCAN_DECLINE } PcrecScanVerdict;
PcrecScanVerdict pcrec_scan_verdict(uint64_t n_new, uint64_t n_old,
                                    unsigned bar_num, unsigned bar_den,
                                    PcrecFlip *flip /* may be NULL */);
```

- **`verify(chain)` is a SUM at U0/U1 `[r3 S11]`.** It is
  `Σ (C_VERIFY + C_MISPRED·min(p,1−p))` per term, which is what `prefix_k`
  does today. The emitted `&&` chain short-circuits, so its expectation is
  `c1 + p1·c2 + p1·p2·c3 …`. The switch to short-circuit is a formula change
  that U2 states and counts.
- **The bar** (`bar_num/bar_den`) is the caller's: `prefix_k`'s MATERIAL 2/1,
  1/1 elsewhere. It belongs to [SIZE-KNEE]/MATERIALITY. The verdict takes it
  as an argument and owns no value.
- **The verdict:** PAYS iff `n_new · bar_num < n_old · bar_den`, reading the
  bar as "the new form must be `bar` times cheaper". A TIE is DECLINE, the same
  as `prefix_k`'s strict `cost < best` (keep what ships).
- **`flip`** is the break-even stop rate, holding the other expectations
  fixed. N is piecewise LINEAR in stop_ppm, with one knee where `stop_ppm ·
  step_k = 10^6` (the stepped term saturates; `[r3 S5]`'s "breaks the exact
  solve"). So the flip is solved per piece, two closed forms, and the smallest
  in-range root is returned.
  - **Rounding:** `flip.ppm` is the SMALLEST integer stop_ppm at which the
    verdict reads DECLINE (ceil of the rational root), or `PCREC_FLIP_NONE`
    if the sign does not change on [FIND_FLOOR_PPM, 10^6].
  - **Its defining property is checkable:** `verdict(flip.ppm) == DECLINE`
    and `verdict(flip.ppm − 1) == PAYS`.

### 2.4 Integer rules and the magnitude bound `[r3 F4 / S8]`

1. **Units.** Rates are `uint32` ppm. Costs are `uint64` scaled numerators
   (§2.3) in each row's native unit. No floating point: a selection must not
   change with the compiling box.
2. **No division in the cost.** Scaling by 10^6 makes the pass term
   (`stop · pass · attempt / 10^6`) exact, and nothing else divides. Rev 1
   inherited `model_cost`'s three truncating divisions, and those are now
   confined to the verbatim U0 copy (rule 6).
3. **Compare by cross-multiplication** (the verdict, the advance comparison,
   #3's `ppm · gap > 10^6`, #4's `(10^6 − K·h)·m > 10^6·h`).
4. **Every rounding is stated:**
   - MASS: a sum capped at 10^6; NONE `floor(k·10^6/256)` (shipped).
   - Products: per step, by `q->round`.
   - The complement: `10^6 − mass` (exact).
   - The cost: exact.
   - The verdict: exact, tie → DECLINE.
   - `flip`: ceil, with the property above.
   - `stepped`: `min(10^6, stop · step_k)`, exact.
5. **The magnitude bound, which makes saturation dead code.**
   - **Cell and chain limits.** Every MEASURED, DERIVED or RULED cell must
     be ≤ `PCREC_OPCOST_CELL_MAX` = 2^14 native units (16,384 cc = 163.84
     cycles per operation). The largest cell today is `C_ENTER`, 2,000 cc.
     The Mac's 25 ns reseed is about 8,000 cc at 3.2 GHz. A verify term is
     ≤ 2 · CELL_MAX, the chain ≤ 8 terms, and the bar ≤ 16.
   - **Bounds.** With stop/pass/stepped ≤ 10^6 < 2^20:
     - `10^12·scan < 2^54`;
     - `10^6·stop·(reentry + verify) < 2^40·(2^14 + 2^18) < 2^58.4`;
     - the pass and stepped terms < 2^54 each;
     - so N < 2^58.7, and N × bar < 2^62.7 < 2^64.
   - **Assertion one:** the bound is a `_Static_assert` in `scancost.c` over
     the generator's cell maximum and the three limits.
   - **Assertion two:** `tests/core/scancost_check.c` evaluates the all-max
     corner and asserts the helper raised no saturation.
6. **The helper is core-owned and UNSIGNED.** `pcrec_u64_add_sat` and
   `pcrec_u64_mul_sat` go in `src/core`: overflow is tested before the
   operation, the result saturates at `UINT64_MAX`, and a sticky flag is set.
   - **Why not `pcrec_sat_add`/`pcrec_sat_mul`** (`src/opt/mrl.c:125`)? They
     are signed. `sat_add` computes `a + b` before the cap. They are sound for
     their own callers, whose operands are ≤ 2^40 (`PCREC_MINW_MAX`), but
     they are not a general primitive. Calling them from `src/core` would also
     be a core → opt back-edge. F-10 records this.
   - **The flag's job.** Under rule 5 the flag never fires, and the check
     asserts that. If a future cell above CELL_MAX ever makes it fire, the
     comparison still resolves in the saturating direction or ties, because
     saturation is monotone.
7. **`model_cost` moves VERBATIM at U0**, truncation order included.
   `prefix_k`'s selections are pinned by it. Rule 2's exact cost replaces it
   only at #7's U2, as a counted mover.

### 2.5 The question kinds, and where each NONE lives

| kind | primitive | NONE answer | readers |
|---|---|---|---|
| MASS | `pcrec_find_set_mass` / `_seq_mass` (`findings.c:451`, `:460`) | cardinality, `floor(k·10^6/256)` | `pcrec_scan_expect` (stop and pass rates) |
| PICK | `pcrec_find_pick` (`:433`) and its readers `_set_pick`, `_run_scan_index`, `_run_window_start`, `_run_rank` | cardinality argmin, ties to the reader's rightmost | #2, #13, #14, #15a, #15b, #21 (and #5 after F-3) |
| COMPARE | `pcrec_find_no_commoner` (`:445`) | `false` | #1 |
| VERDICT | `pcrec_scan_verdict` over `pcrec_scan_cost` over `pcrec_scan_expect` | cardinality, inherited from MASS; "no scan" = zero stops, every byte stepped (§2.2) | #3, #4, #7; candidates #8-#11, #18, u1-u4 |

The VERDICT primitive lives in a sibling file, `src/core/scancost.c`
(answer-free; the table it reads is not findings data). It sits in the base
tier.

---

## 3. The operation-kind table

### 3.1 Shape

One grid. **Rows** are route × program class. **Columns** are operation
kinds. **Two planes** sit over the same grid (Frank's SHARED VOCABULARY
note).
- **MEASURED plane (selection).** Each cell is MEASURED (box, ISA, libc,
  compiler, regime, source file), DERIVED (a formula over cells of ONE box),
  UNMEASURED, or KIT. **Same-box ratios only (Q3, settled; `[r3 F8]`):** a
  verdict reads cells of one box, and no cross-box derived cell exists. A
  verdict whose cells are not all on one box is UNMEASURED for that verdict.
  The plane holds one column per box measured.
- **CONTRACT plane (metering, [EFFORT-BUDGET]).** Each cell is RULED,
  DERIVED (a counting rule) or UNSET. Memory bounds (frames, trail,
  recursion) are not effort, so their cells are n/a here. They stay separate
  budgets, and §3.5's per-counter check covers them.

Rows: as rev 1, with DU/DR split for the stay skip `[r3 S6]`.

| row | route × class | an operation here |
|---|---|---|
| DU | DFA unanchored, forward | the forward table walk; the forward stay skip |
| DA | DFA attempt | a labelled-state step; one attempt per start |
| DR | DFA reverse walk (RECOVER `reverse-pass`, LOCATE `rev-end`) | the reverse table walk; the reverse stay skip |
| VL | VM frameless | a VM step with no resume frame |
| VF | VM framed | a VM step with frames and trail |
| HY | VM hybrid retry | a prefilter call from the retry loop |

Columns:

| kind | meaning | metered today? |
|---|---|---|
| `step_byte` | the engine walks one subject byte itself | VM: steps (D51) where backtracking; DFA: no budget |
| `skip_byte` (new) | one byte passed by a stay skip loop (M2.1) | no |
| `stop_reentry` | a scan stop hands control to the engine | no |
| `verify` | one positional test at a candidate (probe + `C_MISPRED·min(p,1−p)`) | no |
| `attempt` | entering the engine on a candidate that will fail | VM: its steps |
| `reseed` | one prefilter call from the hybrid retry | no |
| `walk_byte` | one byte of a reverse walk | no |
| `resume` | a backtrack resume | STEPS (D51) |
| `work_byte` | forward-only work the fail label never sees | WORK (D49) |
| `frame` / `trail` | a push / a trail entry | FRAMES / trail capacity (memory) |
| `scan_byte` | a byte passed over by a delegated FIND | KIT (§3.4) |

### 3.2 The MEASURED plane, corrected `[r3 S1/F9, F8, S6]`

| cell | value (native unit) | label | source | note |
|---|---|---|---|---|
| DU.step_byte | 7.751 c/B | MEASURED, Zen 1 (ubuntubudu), periodic throughput (I-10's confound) | `src/gen/CLAUDE.md:2565` | a steady state, not a false-entry cost (F-5) |
| DU.attempt | 2000 cc (`C_ENTER`) | DERIVED from a stale input: 10.7 c/B (pre-premul) × "~2 bytes" (UNMEASURED) | `prefix_k.c:52-58` | U3 re-measures it on one box (§5.1); never re-derived from 7.751 |
| DU.verify | 250 cc + 1500 cc · min(p, 1−p) | MEASURED, Zen 1 | `offset_k_skip.md` §4.2, §7.3 | |
| DU.stop_reentry | — | **UNMEASURED: no numeric accessor (§3.3)** | none | nearest evidence: b2ledger's fitted `c_call` 7.72 ns/memchr occurrence (Zen 1, one cell, the kit's call inside it) |
| DU.skip_byte, DR.skip_byte, DR.step_byte | — | UNMEASURED | — | M2.10 (`emit_dfa.c:4766-4776`): a reverse byte-at-a-time skip lost ~27% to the reverse table walk, i.e. DR.skip ≥ DR.step on that cell |
| DA.* | — | UNMEASURED | — | no member prices the attempt route |
| DR.walk_byte | — | UNMEASURED | rev-end timed whole-call only (O-96, K103/K104; rewtwin) | read by u2 and u4 |
| VL.attempt | 1.6 ns | MEASURED, Mac M1, gcc-16, scratch | `hyb_reseed.md` §3 | |
| VF.attempt | 8.6 ns | MEASURED, Mac M1 | same | |
| HY.reseed | ~25 ns, "about constant" | MEASURED, Mac M1 | same | |
| VL/VF R4 `gap` | 16 / 4 bytes | **MEASURED crossover: the smallest of its class's witnesses** (frameless 16 from 16/26/30 B; framed 4 from `(?<=a\|é)x`'s ~3 B, with `(?<!日)本` crossing at 9-12 B) | `hyb_reseed.md:96-101`, `emit_vm.c:11033` | **not a cost cell, and not derived.** ⌈reseed/attempt⌉ is REFUTED by its own table (frameless 16 vs 16/26/30; framed (?<!日)本 ≈13 vs 9-12). It stays in `vm_reseed_cal`, owned by the runtime-arm family (§4.4). A gap formula needs a model reproducing 26/30 first |
| VL/VF block, cap, first | 64/1024/64, 16/64/2 | chosen settings, except frameless `first` (one pattern) | `vm_reseed_cal` | the runtime-arm family's parameters (§4.4) |
| *.scan_byte | `C_MEMCHR` 0.055 c/B, `C_BITMAP` 1.16 c/B | MEASURED Zen 1 glibc AVX2 | `prefix_k.c:65-66` | KIT-ESTIMATE (§3.4, Q1) |
| VL/VF resume, work_byte, frame, trail | — | UNMEASURED in this plane | K102's numbers are COUNTS | [EFFORT-BUDGET]'s study |

**Units.** Each cell carries its native unit and box. Under same-box ratios,
no cross-box conversion is defined. Rev 1's "DERIVED = value × that box's
clock, CROSS-BOX flag" is withdrawn `[r3 F8]`.

### 3.3 No numeric accessor for UNSET or UNMEASURED `[r3 F10]`

- **The table is an X-macro** in `estimates.def` (Q2 settled). The generator
  emits a value macro `PCREC_OPC_<ROW>_<KIND>` only for cells labelled
  MEASURED, DERIVED or RULED. An UNSET or UNMEASURED cell emits NO value
  macro, so a reader that names one is an undeclared-identifier BUILD
  FAILURE. There is no default value anywhere (memory
  `pcrec-no-silent-defaults`).
- **A `PcrecOpRow`** (the cost function's input) is generated for a row only
  when every kind the cost formula reads is numeric. Today no row qualifies:
  DU lacks `stop_reentry`, VL/VF lack `step_byte` in this plane. So
  `pcrec_scan_cost` has no caller until those are measured. That is how U2 is
  BLOCKED by construction rather than by a note.
- **A reader whose formula omits an UNMEASURED term** must be listed
  `uses-unmeasured: <cell>` in the census disposition (`census_disp.tsv`
  gains the column at U1). The moved `model_cost` omits `DU.stop_reentry`
  exactly as it does today, so it carries that line. That makes the omission
  a stated property of the reader, not an implicit 0.
- **The rev 1 readers that read the silent 0:**
  - §2.3's cost: it now has no row to price over.
  - #4's U2: blocked until `stop_reentry` is measured.
  - #7's U2: likewise.
  - §4.5's END admission: it needs `DR.walk_byte`, so it is blocked as a
    decision, and its proxy is labelled.

### 3.4 The kit-form constants (D146 disposition)

`C_MEMCHR` and `C_BITMAP` price HOW a set is scanned, and that is the kit's
FIND row (R4c/R4g). `prefix_k` uses them to rank WHAT to scan. They stay as
KIT-ESTIMATE cells:
- only `pcrec_prefix_ksets` may read them, and the census disposition is the
  structural check;
- they have an expiry trigger.

Q1 (§7.1) carries the end state.

### 3.5 D158, per counter `[r3 S2 / F1, S12]`

**D158 is per budget**: step, work, frames, trail. With two effort counters,
any substitution that raises WORK breaks D158 for a caller who tunes the work
budget, whatever the weights. So the check is a VECTOR. A weighted sum is
only its later projection, once [EFFORT-BUDGET] rules weights. Rev 1's §0.4
and its K102 sentence are withdrawn: with CONTRACT UNSET, rev 1's weighted
check would have passed K102 (it fails only if w(work) > 0.9938 w(resume)),
so it did not "FAIL today".

**The declaration.** `axes.def` gains a `meter` column: one cell per counter,
each `le` (the charge with the axis on is ≤ the denied form's on every input)
or `gt:<K-row>` (a known violator, citing its K row). The population is EVERY
axis row (44 today). There is no default, so a row without the cell is a
build failure, and the check's K35 floor is the literal 44. Rows that act
only on DFA-ONLY artifacts declare `le` on all four, trivially. Meter cells
are read only by the checks, never by a selection. The axis count is read
from `--list-axes` and compared with the literal.

**What "DFA rows are trivial" covers `[r3 S12]`.** A DFA row acting on a
DFA-ONLY artifact cannot move a budget: the artifact has none. A DFA row
acting on a hybrid's INLINED prefilter does move one: it changes VM attempts.
The collapsed-prefilter rung gives 99,601 attempts against 1. So such a row
is declared like a VM row (its attempts are `le` only if it only removes
them).

**The check (table-build time).**
- Every `gt` cell must cite a K row listed in D158's allowance. Today that is
  exactly K102, an exact key per D158 add. 1, and K102's cell is
  `possessify: work gt:K102`. Any other `gt` fails, and so does any `gt`
  without a key.
- The axes with no deny (RETRY `exact`, `clamped`, `anchored`) are not
  `axes.def` rows. They stay covered by their twin (LR-S11) and by
  [GIVEUP-DIFF].

**The independent control: derived from the emitted charge sites.** It is
prototyped as `prior_cost_unify/meter_sites.sh` (output `meter_sites.tsv`).
- For each axis and each witness in a population, the artifact is compiled
  with the axis on and denied, and the emitted charge SITES are counted per
  counter:
  - `RX_PUSH(` stands for steps (each resume point pays a step at the fail
    label) and for frames;
  - `RX_CHARGE_WORK(` stands for work;
  - `RX_TRAIL(` and `RX_SET(` stand for trail.
- The per-artifact delta classifies the axis: all ≤ 0 is DELETES, mixed signs
  is SUBSTITUTES, all ≥ 0 with some > 0 is ADDS, all 0 is NONE.
- Any counter with delta > 0 contradicts an `le` declaration unless the
  dynamic arm shows the dynamic charge still ≤ the denied form's.
- The control shares no source with the declaration: the declaration is
  hand-written, the derivation is the compiler's own text.
- Its limit is stated: a site count is a PROXY for the dynamic charge. A row
  that removes attempts (start-set, reseed) reads NONE statically. So the
  derived class must be ⊑ the declared one, with NONE ⊑ DELETES, and an ADDS
  or SUBSTITUTES derivation must match a declaration that names it.
- The dynamic arm stays [GIVEUP-DIFF]'s budget ladder (LR-G5), per counter.

**The prototype (11 witnesses, `-p rx --engine=vm --features all`, worktree
build at 4a9748bb):**

| axis | witness | Δpush | Δwork | Δtrail | derived |
|---|---|---|---|---|---|
| `-fno-possessify` | `\b(\w+)\b\s+\1\b` | −2 | +2 | −2 | SUBSTITUTES (K102's class) |
| `-fno-possessify` | `(a+)b`, `([a-z]+)\d` | −1 | +1 | −1 | SUBSTITUTES |
| `-fno-poss-bref-first`, `-fno-poss-ctx-follow` | `\b(\w+)\b\s+\1\b` | −1 | +1 | −1 | SUBSTITUTES |
| `-fno-lit-run` | `(abcdef\|x)y` | 0 | −4 | 0 | DELETES (F-11) |
| `-fno-alt-island` | `(foo\|bar\|baz)q` | −2 | +6 | 0 | **SUBSTITUTES (F-8)** |
| `-fno-counter`, `-fno-revdet`, `-fno-hyb-reseed`, `-fno-start-set` | one each | 0 | 0 | 0 | NONE (attempts removed dynamically, if at all) |

- **F-8: the island's derived SUBSTITUTES is real.** Under `--work-budget=2`,
  `(foo|bar|baz)q` on `fooq` GIVES UP (`work`) with the island and ANSWERS
  (0,4) with `-fno-alt-island`. This happens on the default engine selection
  (the artifact is VM) and on forced VM (`prior_cost_unify/island_work.sh`,
  `island_work.txt`). It is a second D158 violator, of K102's class (steps
  re-categorized as work), and D158 add. 1 accepts only K102.
- **F-11:** the lit-run row's witness DELETES work sites, where rev 1
  declared SUBSTITUTES. The population answer (the join over every artifact)
  is U4's.

**The weighted projection, when [EFFORT-BUDGET] lands.** Once weights are
RULED, the vector check projects to Σ W(op′)·ratio + overshoot ≤ Σ W(op) per
SUBSTITUTES row. Only then is a single-budget statement checkable. The
vector check does not wait for it.

### 3.6 How [EFFORT-BUDGET] reads the CONTRACT plane

As rev 1 §3.4:
- a weight is one CONTRACT cell;
- the emitted charge is a literal from that plane;
- the weights are stamped on every VM artifact, an abi event plus a
  `limits.md` hunk whenever one moves.

This row creates the grid, the kinds, an empty CONTRACT plane and the meter
column. The values and the unit are [EFFORT-BUDGET]'s study output. F-8 is
now that study's second witness beside K102.

---

## 4. How each member reads it

### 4.1 One line each

| # | member | U1 (inputs through the primitive, formula kept) | U2 (formula switch) |
|---|---|---|---|
| 1 | G1 `dominated` | COMPARE face unchanged, scoped to `SINGLETON_AT_START && nverify == 0` (F-1) | none proposed (F-4, D77) |
| 2 | set-leads | PICK unchanged | VERDICT candidate whose cell is K85; blocked by F10 |
| 3 | RETRY `adaptive-dense` | `stop_ppm · gap > 10^6` via adapters A3 and A5; gap from `vm_reseed_cal` | a cost verdict (reseed vs stepping): the grid's band (§5.2) |
| 4 | NEXT `handoff` | `(10^6 − K·h)·m > 10^6·h` with h, m as stop_ppm via A1 (round UP) and A2; reads stop_ppm, never an advance (A4) | `verdict(cost(landmark, step_k = K), cost(displaced)) == PAYS`; BLOCKED until DU.stop_reentry is measured |
| 7 | `prefix_k` | `model_cost` verbatim over stop_ppm via A1 (round DOWN); `uses-unmeasured: DU.stop_reentry` | `pcrec_scan_cost` over DU; short-circuit verify (S11); BLOCKED likewise |
| 13, 14, 15a, 15b, 21 | PICKs | unchanged (already on the PICK primitives) | — |
| 8 | NEXT `first-class` (VM) | — | adds `verdict(cost(S seek), cost(no scan)) == PAYS` to `\|S\| < 256`; needs VL/VF `step_byte` |
| 9 | NEXT `first-*-bounded` | — | adds `verdict(cost(T), cost(E))` to T ⊊ E (K91's entry term is `stop_reentry`) |
| 10 | NEXT `byte-class[-bounded]` | — | `verdict(cost(set), cost(no scan))` (hex8) |
| 11 | `pick_skip_states` | — | §4.3 |
| 18 | `MIN_SCAN_CHAIN` time half | — | HELD at 2 |
| u2 | [MATCH-SPLIT] END | — | §4.5 |

**Nothing is "switch now".** Rev 1 named #3, #4, #7 and #11. With F10:
- #4 and #7 need `stop_reentry`;
- #11 needs DU/DR `skip_byte` and `stop_reentry`;
- #3's cost form needs one box's attempt and reseed cells (it has them: the
  Mac's), but its band is a MOVER the grid names (§5.2), counted before it is
  built.

Q4 reorders what comes first.

### 4.2 U1's adapters, each with its reach `[r3 S3]`

U1 is zero-mover only if every member's quirk is reproduced. Each quirk is
an ADAPTER row in the U1 commit. An adapter is a stated mapping, not a
special case in the primitive. Each reach is counted at U1 by the trace
build's per-adapter counter, with the stamp predicate below as its
independent floor (`[r3 F11]`: reach from stamps).

| id | member | quirk (today's code) | adapter | reach (stamp predicate) |
|---|---|---|---|---|
| A1 | #4 and #7 | #4 rounds the landmark product UP per step (`emit_dfa.c:7765`); #7 rounds its chain product DOWN per step (`prefix_k.c:261`, `vrate * ppm / 1e6`) and can reach 0 | `q.round = UP` for #4, `DOWN` for #7 | #4: artifacts stamped `RX_DFA_PREFILTER "handoff"` with a run landmark; #7: every DFA artifact whose k0 is usable (selections: `"offset-set"`) |
| A2 | #4 | the displaced row is priced only when BYTE/SET (`emit_dfa.c:7792-7796`); OFS/LANDMARK displaced rows get m = 10^6 | an OFS/LANDMARK displaced row maps to `SET(Σ)` (stop_ppm 10^6), NOT to NONE | handoff artifacts whose `-fno-req-handoff` twin stamps `offset-set`/`run-pinned*` (a deny-pair census) |
| A3 | #3 | `pcrec_dfa_cand_ppm` prices only the SCAN BYTE of an offset/run-pinned row (`dfa_cand_scan`'s `cs.byte ≥ 0`) | an OFS/run-pinned scan maps to `SINGLETON(scan byte)`, verify chain dropped | `RX_VM_RESEED` ∈ {`adaptive-dense`, `adaptive`} with the hybrid's prefilter ∈ {`offset-set`, `run-pinned*`} |
| A4 | #4 | rev 1 §4.1 said "reads adv", §5.1 said cross-multiplied; a truncated advance flips at the boundary | **a rule, not an adapter:** U1 members read `stop_ppm`, never an advance (§2.2) | all #4 asks |
| A5 | #3 | no usable scan, or the ATTEMPT route, returns 10^6 (`emit_dfa.c:7439`, `:7443`) | maps to `SET(Σ)`, NOT to §2.2's NONE (zero stops), which would flip R4 | R4 asks on hybrids with no DFA scan or on the ATTEMPT route (2026-10-12, a5inv_report.md: DELIBERATE — a scan testing nothing stops everywhere; reach is 12 artifacts on the 10^6 branch, 6 with a live retry loop, bench 0; the summary's 16/46% over-counts) |

### 4.3 #11, the stay skip, by break-even `[r3 S6]`

- **The test.** A stay skip in state s pays iff the expected stay RUN (§2.2:
  t/(1−t), not 1/(1−t)) saves more than the skip's entry and exit cost. In
  formula form: `t/(1−t) · (step_byte − skip_byte) > stop_reentry`, all on ONE
  row (DU forward, DR reverse). It DECLINES when `step_byte ≤ skip_byte`.
- **Why the decline matters.** M2.10's ~27% reverse regression is exactly
  that case. Rev 1's break-even (`stop_reentry / step_byte`) treated skipped
  bytes as free, and with `stop_reentry` at 0 every state qualified.
- **Status.** NOT in "switch now". DU/DR `skip_byte` and `stop_reentry` are
  UNMEASURED (§3.2).
- **Plumbing owed.** `pick_skip_states(const Dfa *d, int exclude, int
  out[4])` has no `Ctx` (no prior) and no direction. Its caller
  (`emit_dfa.c:10731`) must pass both.
- **Fit `[r3 F12(d)]`.** The stay-skip choice is a sibling of the DFA's
  form-selection axes (`dfa_select`/DFA_SELECT's scan-edge rows). As a
  VERDICT it becomes a row there, not a free-standing function.

### 4.4 The runtime-arm family: ONE table `[r3 F12]`

Three filed rows are one mechanism: a per-call state, armed, unarmed or off,
whose INITIAL state comes from a compile-time decision and whose run-time
counter may flip it.
- **[START-DENSE]:** the RETRY adaptive rule carried to the VM-only and
  DFA-hat routes (K90, K91, K83 once sized).
- **[ADAPTIVE-ARM]:** K105's re-entry, and [LOSS-REVIEW] 5(a)'s dense
  decline.
- **[OPT-HYB-RESEED-POLICY]:** the disarm rule, "halve, don't reset" (already
  folded into START-DENSE by D153).

Its prototype ships: the RETRY rows `adaptive-dense`/`adaptive` of
`cand_rows[]` (`[r3 F12(f)]`: no longer `pcrec_reseed_rows`, since [START-TABLE]
C5) with `reseed_steps`/`reseed_block` in `emit_vm.c`.

**Proposal.** The family is ONE first-match table (memory
`pcrec-decisions-as-first-match-tables`). Its rows are (decision site,
initial-state predicate, counter parameters).
- **Its first rows are today's RETRY adaptive rows, folded at zero movers.**
- **`vm_reseed_cal` is that table's data**, all four columns (gap, block,
  cap, first) `[r3 F12(b)]`.
  - Today `gap` is read as a selection input through
    `CandVmFacts.reseed_gap` (`emit_vm.c:11048`), while block, cap and first
    are the arm's parameters. Splitting them into the opcost table and an arm
    table would be a parallel table.
  - The opcost table holds only per-operation prices (HY.reseed,
    V*.attempt), which the gap was measured against.
- **The primitive's role:** the initial state's predicate is a VERDICT
  (PAYS → armed, DECLINE → unarmed), and `off` is the static case. The verdict
  is evaluated at both ends of the rate's support, FIND_FLOOR_PPM and 10^6. If
  the sign is the same at both, no arm is needed. `flip` is the arm's switch
  point.
- **K105** is the family's first NEW row, never a fourth separate instance
  (Q4).
- **Whether to EMIT an arm** (≈560 code bytes per artifact, from the RETRY
  precedent) is [SIZE-KNEE]'s or the family's own trigger cell. It is not
  decided here.

### 4.5 [MATCH-SPLIT]'s END admission: OFF the primitive as a decision `[r3 S4]`

The ruled requirement (`match_split_requirements.md` §5.1) admits an
UNBOUNDED END arm beside a FREE class only when the expected suffix walk is
short against the gap between MATCHES. The END walk repeats per call under
the stateless API, so its cost per match is E[walk] against the inter-MATCH
gap. The primitive cannot supply that:
- `pass_ppm` is not a match probability;
- the free locator's stop rate is the inter-CANDIDATE gap;
- one stay set cannot describe a multi-stay walk (`a\d*\s*$` walks two stay
  states).

**So the END admission is not built on the primitive.** If [MATCH-SPLIT]'s
END+FREE stage wants a rule before the missing quantity exists, it may use
this CONSERVATIVE PROXY, labelled as one:
- **Admit only a single-stay END arm**, and only iff `walk(T)·DR.walk_byte <
  adv(free)·<free route's per-byte cost>`, where walk(T) = 1/(1−t) (§2.2) and
  adv(free) is the candidate gap.
- **Why it is conservative:** every match start is a candidate, so the
  candidate gap ≤ the match gap. The proxy therefore never admits where the
  true rule would decline. It can decline where the true rule admits.
- **Multi-stay END arms are DECLINED** under the proxy.
- **It is blocked anyway** until `DR.walk_byte` is measured (F10).

The UNLOCK (filed, §7.3) is the expected first-passage time over the DFA
under the iid prior.

### 4.6 The kit-field mapping `[r3 F6]`

pcrec states rate FACTS to the kit (D157). The mapping is one derivation
(`pcrec_scan_expect` and MASS), but the three fields are different quantities.

| kit field (`memfn/include/memfn.h`) | quantity | filled from | under NONE |
|---|---|---|---|
| `mf_term.ppm_lo/ppm_hi` (:272) | a PER-TERM match density, as a range | SET/SINGLETON term: `lo = hi = MASS(set)`, an EXPECTATION under the prior stated as a point, never a bound on the text. A masked RUN term: UNKNOWN (0..MF_PPM_FULL), because only the independence product exists for it | UNKNOWN (cardinality is not a density of the text) |
| `mf_site.cand_ppm_lo/hi` (:337) | the whole predicate's POST-CONJUNCTION density | a one-term predicate: the term's own; a conjunction: UNKNOWN (independence only, Q5) | UNKNOWN |
| `mf_pred.rank_pos/rank_ppm` (:300, RQ-2) | the run term's positions ORDERED, each with its rate | `pcrec_find_run_rank` (member #21), exact under the prior | the uniform rate (RQ-2 as shipped): an ORDER is meaningful under cardinality, a density is not |

Today `memfn_sites.c` fills every hint as unknown (`term_unknown_density`,
`cand_ppm_hi = MF_PPM_FULL`, `memfn_sites.c:206`, `:223-224`), and fills
`rank_*` (#21). Filling the hints from the table above is fixes.md F3's step,
after U1, and it is one derivation for pcrec's verdict and the kit's facts.

---

## 5. Migration

### 5.1 Steps (implement-then-replace, no-mover first)

| step | what | movers | gate |
|---|---|---|---|
| U0 | `estimates.def`'s opcost section (both planes, labels, per-cell box/ISA/libc), the generator with §3.3's no-accessor rule and §2.4's `_Static_assert`; `src/core/scancost.c` (`pcrec_scan_expect`/`_cost`/`_verdict`); the unsigned helpers; `model_cost` and `req_landmark_hit_ppm`'s product moved in VERBATIM. **No caller-visible surface.** | zero | `scripts/emit_sweep.py --ref <base>`, all streams, `-e utf8`, every limit variant: 0 movers with a REACH figure from stamps (§5.4 (a)); `scancost_check.c` |
| U0b | the table's listing (`--list-*` or [LIST-TABLES]) | the `dumps` stream only | **a D80 surface `[r3 F12(g)]`:** its `docs/spec/` hunk and a registry pin in the same commit |
| U1 | members read inputs through `pcrec_scan_expect` via adapters A1-A5 (§4.2), formulas kept; `census_disp.tsv` gains `uses-unmeasured` and a per-member allowed-roots column (a VERDICT member may read only `pcrec_scan_expect`) | zero | emit_sweep as U0; the grid's U1 pairs at 0 (§5.4 (b′)); `census.py` with the allowed-roots rule; adapter reach ≥ the stamp floors |
| U2.k | per member, the formula switch; FIRST the grid names the disagreement band, THEN emit_sweep counts movers over corpus + bench; a mover commit is its own abi bump (D76/D94, readers by grep), a mover manifest by id, a D144 alpha | per member | the grid, then emit_sweep; BLOCKED where F10 says so |
| U3 | `C_ENTER` (DU.attempt) re-measured on ONE box (same-box rule), replacing the derived 2000 | counted (the 12-20 cycle band moved 11/1,352) | as U2 |
| U4 | `axes.def`'s meter column (44 rows, floor 44), the table-build vector check, the site-derived control over a witness population per axis, F-8's row declared `gt` pending a K row (the manager's) | zero | the check, with a planted `gt` without a key and a planted `le` on the island row (must fail) |
| U5 | K105 (§5.3), as the runtime-arm family's first new row, after RETRY's rows fold in at zero movers | K105's movers | §5.3 |

The order follows D153 (remodel first). Remodel overlap: §5.5. **Dropped from
rev 1 `[r3 S1/F9]`:** U3's VF.gap "DERIVED 3, not 4" mover. The gap is
MEASURED.

### 5.2 Why U1 cannot already be U2, and #3's exactness

The three VERDICT members use three formulas: an advance comparison (#4), a
constant crossover (#3) and truncating costs (#7). One verdict over one cost
model answers differently from each on some inputs. So U2 is per member and
counted, never assumed neutral.

**#3's rational form is exact `[r3 F3]`.** For ppm > 0, `ppm · gap > 10^6`
is the same as `10^6/ppm < gap`. Rev 1's truncated spelling is exact too:
`floor(10^9/ppm) < 1000·gap` ⇔ `ppm·gap > 10^6`, since 1000·gap is an
integer. The grid confirms both, at 0 of 1,332 cells. A switch of #3 to the
rational advance is therefore not a mover. Its switch to a COST verdict is,
and the grid names the band. With the Mac's one-box cells:
- frameless: R4 steps first iff ppm > 62,500; the cost verdict iff ppm >
  10^6 · 1.6/25 = 64,000;
- framed: (250,000, 344,000].

Those bands are what a U2 commit counts its movers in. The numbers are an
illustration from one box, not a prediction.

### 5.3 K105, and what an exemplar already does

K105's witness is `[a-y]\d{0,100}:` over ':'-dense digit text, ×1.537 against
main (3,871 → 5,949 µs).
- **A prior-only verdict admits it.** Under the default prior ':' is rare.
  The loss lives in the text contradicting the prior (rev 1 §5.3, unchanged).
- **An exemplar already declines it, with no build (measured compile-side,
  `prior_cost_unify/q4_exemplar.sh`, `q4_exemplar.txt`).** A 36 KB
  synthesized colon-dense exemplar was counted by `build/pcrec-analyze` and
  passed as `-I DIR --analysis=colondense`. The witness's NEXT row moves from
  `RX_DFA_PREFILTER "handoff"` to `"byte-class"`: the K admission (#4) reads
  the exemplar's rates and declines the re-entry. The FIRST row's entry
  handoff stays (`RX_REQ_HANDOFF "101"`). That is consistent with
  `litscan_k82b.md`'s finding that exemplar rates call every K82 cell right.
  Whether the exemplar build recovers the ×1.537 in TIME is not measured here.
  It is K105's own cell, owed with Q4's decision.
- **Without an exemplar** (the bench, the default analysis), the fix is a
  run-time arm: a member of the runtime-arm family (§4.4).
  - Its initial state is the verdict's (PAYS → armed).
  - Its counter disarms after short re-entry gaps (RETRY's text).
  - Witness: hcolon_in back inside the null band, counted by memchr calls and
    DFA steps.
  - Control: colon-SPARSE text keeps L1's win.
  - The prior-agreeing cells (`loglines/ipv6`, `ipv4`, `sfx-64`) must not
    move past the floor, with the arm's per-call entry as a short-call
    absolute delta (D144 add. 1).
- **The gate is D77.** K105's trigger is a bench cell with a landmark denser
  than its prior. hcolon_in is our own regression ([START-DENSE]'s accepted
  evidence class). Q4.

### 5.4 Controls and sabotage

**The controls, each independent of what it checks:**
- **(a) Byte identity at U0/U1/U4.** `emit_sweep.py` against a pinned base
  binary. Its REACH comes from STAMPS, not from the subject's own trace
  counters `[r3 F11]`:
  - artifacts stamped `RX_VM_RESEED` adaptive rows (#3 asked);
  - `RX_DFA_PREFILTER "handoff"` (#4);
  - DFA artifacts with a usable k0 (#7);
  - per encoding, `<P>_FINDINGS "byte-rate=none"` (the NONE asks).

  Each is printed, and each has a floor.
- **(b) The unit check, `tests/core/scancost_check.c`, with TWO references
  `[r3 F4]`:**
  - **(b1)** a PINNED copy of today's `model_cost` (`prefix_k.c` at the U0
    base commit) for U0's verbatim move. It shares the formula ON PURPOSE,
    because U0's claim is "moved, not changed".
  - **(b2)** exact rationals (`fractions.Fraction`, generated into the
    check) for the verdict, the flip and the bound.
  - **What (b2) cannot do.** It checks the ARITHMETIC (no rounding, no
    overflow, the flip's defining property, tie → DECLINE). It shares the
    MODEL, so it cannot say the model is right. The model's control is (d)
    and the bench.
  - **Cells:** break-even ±1 ppm, the all-max corner (no saturation), and
    stop_ppm 0, 1, 10^6.
- **(b′) The arithmetic GRID `[r3 F3]`.** Per formula pair (today's
  spelling, the primitive's), it runs over (mass, K, gap, bar) ladders that
  include every equality point, each with a PLANTED off-by-one. Prototype:
  `prior_cost_unify/grid.py`, `grid.txt`.

  | pair | cells | disagree | its plant | plant reads |
  |---|---|---|---|---|
  | #3 R4 vs rational advance | 1,332 | 0 | `>=` for `>` | 4 |
  | #3 R4 vs rev 1's adv_milli | 1,332 | 0 | — | — |
  | #4 landmark product (ceil/step) vs primitive, UP | 17,475 | 0 | the other rounding / ceil spelled `+10^6` | 17,471 / 178 |
  | #7 chain product (floor/step) vs primitive, DOWN | 17,475 | 0 | the other rounding | 17,471 |
  | #4 K admission, formula kept | 749,100 | 0 | K + 1 | 67 |

  - The equality plant reads 4 of 1,332, and K + 1 reads 67 of 749,100: a
    corpus count would almost never reach either. This is why the corpus
    decides only which REGIONS are populated (a stamp-derived floor per
    region). At U1 the grid runs the two C spellings (a test hook), not the
    Python stand-ins.
  - It exits 1 if a U1 pair disagrees or a plant reads 0. emit_sweep, not the
    grid, decides movers.
- **(c) The reader census `[r3 F5, F11]`.** `census.py` is kind-aware (each
  reader's kind and allowed roots), walks carriers (a wrapper cannot evade
  it), carries floors, and fails on undispositioned or stale readers. This
  replaces rev 1's grep with an allowlist.
- **(d) The stop-count INSTRUMENT `[r3 F11]`, not a check.** It sets predicted
  `stop_ppm` against COUNTED stops (rlhtwin/lrmisc's counted-memchr drivers)
  on real subjects. It has no threshold. It measures the independence error
  and the prior/text mismatch per member, which are [ADAPTIVE-ARM]'s trigger
  inputs. Its population is printed (K35).
- **(e) The meter controls (§3.5).** The vector check against `axes.def`'s
  column, the site-derived classification against the declaration, and
  [GIVEUP-DIFF]'s dynamic ladder.

**Sabotage rows** (S-ids unallocated: the manager assigns from a free range).
Each names its site and its reach.

| plant | site | detector | reach |
|---|---|---|---|
| 1. VERDICT's NONE answer swapped to COMPARE's: stop_ppm = 0 when the rate is NONE (bypassing MASS) `[r3 F2]` | inside `pcrec_scan_expect` | (b2)'s NONE cells; emit_sweep's **synthetic-bundle arm**: a committed bundle with no `serves` for the compile's encoding, so every compile under it is NONE on purpose | by construction in (b2). For the sweep: the count of NONE asks per encoding from `<P>_FINDINGS "byte-rate=none"`, with a floor. The synthetic bundle is the STANDING witness, because D160/[U8-PICK] will remove the utf8 NONE population (the S806/S807 shape) |
| 2. G1 re-expressed by mass (`set_mass(p) ≤ set_mass(q)`) | `req_byte_dominated_by` (`emit_dfa.c:7538`) | the synthetic-bundle arm: G1 elides one-byte pre-checks (F-2) | artifacts with a memchr scan, a one-byte pre-check and `byte-rate=none`, counted from stamps (`RX_REQ_WHY`, `RX_DFA_PREFILTER`), with a floor |
| 3. a VERDICT member reads a rate root directly | the member | (c): a VERDICT member's allowed roots are `{pcrec_scan_expect}` from U1 | structural |
| 4. the verdict divides (rounding) or ties toward PAYS | `pcrec_scan_verdict` | (b2)'s break-even and tie cells; (b′) | by construction |
| 5. a CUBE_RUN product rounds the wrong way, or takes the minimum position mass | `pcrec_scan_expect` | (b′): 17,471 cells; handoff witnesses in `run_prechecks.sh` §5.12m (`[a-y]\d{0,150}:` stays un-re-entered) | yes on run landmarks; the byte landmark is unaffected (stated) |
| 6. a cell above CELL_MAX | `estimates.def` | the `_Static_assert`; (b)'s corner | build |
| 7. an UNMEASURED cell given a value macro | the generator | a structural check: value macros exist only for MEASURED/DERIVED/RULED cells, compared with the labels | structural |
| 8. CONTRACT read by a selection, or MEASURED by the meter | accessors | a structural check on accessor names | structural |
| 9. an axis declares `le` on a counter its emitted text charges more (the island row's `work` declared `le`) | `axes.def` | (e)'s site derivation: island Δwork +6; dynamic: `island_work.sh` | yes: F-8's witness |
| 10. VF's gap read from VL's row | `vm_cand_facts` (`emit_vm.c:11048`) | the existing [OPT-HYB-RESEED] calibration check (S372's shape) | yes (S372 reaches it) |

### 5.5 Remodel overlap (D153) `[r3 F12]`

| row / lane | overlap | order |
|---|---|---|
| [TIE-ALIGN] | the PICK members #13-#15 and #7's offset ranking | neither blocks the other's U0; #7's U2 waits for TIE-ALIGN if both are scheduled |
| RQ-2 / D157 (`ofs_pred_rank`, #21) `[r3 F12(a)]` | pcrec already hands the kit ranking FACTS | Q1's (ii′) extends exactly this to the k-set offset |
| runtime-arm family ([START-DENSE] + [ADAPTIVE-ARM] + [OPT-HYB-RESEED-POLICY]) | §4.4; `vm_reseed_cal`; K105 | U5 is that table's first new row, after RETRY's rows fold in at zero movers |
| DFA_SELECT (`dfa_select`'s scan-edge axes) `[r3 F12(d)]` | #11 | #11's VERDICT becomes a row there |
| [EST-REGISTRY] (D141) `[r3 F12(e)]` | the table's home is its `estimates.def` (Q2 settled); its stray-literal detector is what would DERIVE §1.1 part B | the detector is OWED, filed, not built here |
| [START-TABLE] RETRY rows `[r3 F12(f)]` | #3 is `cand_rows[]`'s `adaptive-dense` row (not `pcrec_reseed_rows`) | U1 touches the row's predicate only |
| [MATCH-SPLIT] | u2 (§4.5) | a reader; blocked on DR.walk_byte |
| fixes.md F3 (kit hints) | §4.6 | after U1 |
| [FINDINGS] B4 (bigram) | joint rates replace the independence product | Q5 settled; the label in §2.2 is the trigger |
| [EFFORT-BUDGET] | §3.5-§3.6; F-8 is its second witness | U4 builds the vector check without it |

---

## 6. Standing questions (`docs/design/CLAUDE.md`)

**1. The measurement regime: RELEVANT, central.** Every MEASURED cell
carries box, ISA, libc, compiler, latency vs throughput, and hit vs miss.
**Same-box ratios only** (Q3 settled): a verdict reads cells of one box, and
a cross-box combination is UNMEASURED. The regime facts that bear on
decisions:
- DU's cells are periodic-subject throughput on Zen 1, while `C_ENTER` prices
  a false entry (F-5).
- VL/VF/HY are Mac scratch hand twins.
- Each R4 gap is the smallest crossover of its class's witnesses, so a
  regime between the witnesses mis-picks. The framed 4-12 B band re-seeds
  where stepping is cheaper (cjk4 ×1.21, cjk1 ×0.94).
- `stop_reentry`, `skip_byte` and `walk_byte` are UNMEASURED everywhere.

A different regime does flip decisions: `prefix_k` moved 11 of 1,352
selections between 12 and 20 cycles. RATES are box-free (F-5). Selection is
never re-measured per compiling box. The CONTRACT plane is regime-free.

**2. The independent control: RELEVANT.** §5.4 (a)-(e):
- byte identity is checked against a pinned binary;
- the unit check's arithmetic against exact rationals, and U0 against a
  pinned old copy (sharing the formula on purpose, stated);
- the grid against planted off-by-ones;
- the census against a call graph, not a grep;
- the meter declaration against the compiler's own charge sites, plus the
  dynamic ladder.

No control takes its expectation from the code it checks, except (b1), which
is stated. Each population is counted, with floors (K35). Each sabotage row
names its site and reach ([MECH-REACH]). Row 1's reach does not rely on a
population D160 will remove.

**3. What moves when data is regenerated: RELEVANT, and it is the row's
purpose.**
- **A MEASURED cell re-measured** moves every selection that reads it:
  emitted bytes and stamps (`RX_VM_RESEED`, `RX_DFA_PREFILTER`, offset stamps,
  `RX_REQ_HANDOFF`). That is an abi event with readers by grep, including the
  byte-count class, plus an identity re-pin. It is not a spec event unless a
  stamp's value SET changes (D80).
- **The prior regenerated** (D160's authored utf8 prior, any bundle) moves
  every VERDICT, PICK and COMPARE member at once through one accessor. It
  also moves the NONE populations that controls (a) and row 1 count, which is
  why row 1's standing witness is a synthetic bundle.
- **A CONTRACT cell changing** is a spec event (`limits.md`), an abi event
  (the stamped weights) and a GIVEUP1 re-baseline.
- **A meter cell changing** (`axes.def`) moves no artifact. It moves the
  check's verdict, and a `gt` cell needs a K row.
- **The table's listing (U0b)** moves the `dumps` stream and a registry pin.

---

## 7. Decisions and questions

### Settled by the manager (from the review; answer-free or following from rulings)

- **Q2 (the table's home):** it is born as [EST-REGISTRY]'s `estimates.def`,
  under the general-mechanisms rule. Opening EST-REGISTRY early for this is
  accepted. Its stray-literal detector is filed as owed, not built now.
- **Q3 (the reference box):** same-box ratios only. The MEASURED plane
  records box, ISA and libc per cell. No cross-box derived cells exist.
- **Q5 (the independence product):** keep the labelled independence product
  until joint rates exist (status quo plus a label). When a bundle serves a
  joint rate, `pass_ppm` and the CUBE_RUN `stop_ppm` read it.

### 7.1 Q1 (for Frank): how does pcrec decide WHAT to scan without pricing HOW? `[r3 F7]`

**The problem.** `prefix_k` chooses a scan offset by comparing a table walk
at offset 0 (`C_BITMAP`, 1.16 c/B) with a memchr at k* (`C_MEMCHR`, 0.055).
That ~20× form gap is the whole reason a scan "must move". The form is the
kit's (D146: pcrec prices no forms). The offset is pcrec's choice today.

**The forces.**
- **D146 and D157 point one way.** pcrec hands FACTS, and the kit owns
  methods. RQ-2 already did this for the run position: pcrec states the
  ranked positions with their rates (#21, `ofs_pred_rank`), and the kit picks
  KB. That is (ii) half-built, on the shipped precedent.
- **(i) is stale by construction for a delegated site.** Under (i) two
  pcrec-held numbers stand for the kit's forms. When the kit changes its FIND
  forms (SIMD rows, R-13/R-14), pcrec's ranking does not follow, and no check
  can see it, because pcrec is forbidden to look at the form.
- **(ii) needs a return channel.** G1 (#1), R4's `pcrec_dfa_cand_ppm` and
  the reseed read WHICH byte is scanned. If the kit picks the offset, those
  readers must read the kit's answer back. That is a contract item, not free.
- **(iii) a form-neutral per-byte cost** is refuted by `prefix_k`'s own §7.3.

**My leaning: (ii′) as the end state, (i) as a labelled interim with an
expiry trigger.**
- **What (ii′) is:** pcrec states the k-set walk as ranked FACTS, the D157
  shape. That means the offsets, each offset's set and its MASS, and which
  are proven. The kit chooses the scan offset and the verifies, and returns
  the chosen offset and byte through a declared field that pcrec's readers
  read.
- **The interim is (i):** the two cells stay KIT-ESTIMATE, only
  `pcrec_prefix_ksets` may read them, and the census enforces that.
- **Expiry trigger for (i):** the first kit change that adds or reorders a
  FIND form for an offset-set site, or the first multi-offset FIND site with a
  measured cell (ci-moskva's 146,633 `D0` stops is the nearest). On either,
  (ii′) is filed as a kit request (memory `pcrec-requests-are-mine-to-file`).

**Room to push back.** (ii′) moves a planner into the kit. If Frank reads
"what to search for" as pcrec's even when it is priced by form, (i) becomes
permanent and the expiry trigger becomes a review trigger.

### 7.2 Q4 (for Frank): K105 by exemplar, or by the runtime arm, and when?

**The problem.** K105's re-entry is admitted on the prior and loses ×1.537
on text that contradicts the prior (hcolon_in).

**The forces.**
- **The exemplar route exists today.** A caller who passes an exemplar
  bundle (`--analysis`) gets the right compile-time answer with no build: the
  witness's NEXT row reverts to `byte-class` (§5.3, measured compile-side).
  `litscan_k82b.md` found exemplar rates call every K82 cell right. Its cost
  is that the CALLER must have and pass representative text. The bench and
  the default compile do not.
- **The arm is the only no-exemplar fix**, and it is not a new mechanism. It
  is a row of the runtime-arm family (§4.4): [START-DENSE], [ADAPTIVE-ARM] and
  [OPT-HYB-RESEED-POLICY] are one per-call armed/unarmed state with an initial
  state from compile time. Building K105's arm alone would make a fourth
  instance. Building it as the family's table folds RETRY's rows in first, at
  zero movers, and makes K105, K90, K91 and the disarm rule rows of one
  mechanism.
- **D77.** K105's filed trigger is a bench cell with a landmark denser than
  its prior. None exists yet. hcolon_in is our own regression, the evidence
  class [START-DENSE] accepted. The arm adds fixed per-call text to every
  armed artifact (a short-call delta, D144 add. 1).

**My leaning.**
1. Record the exemplar route now as K105's answer for callers with
   representative text. That costs a sentence in K105 and the guide, plus
   one TIME cell confirming the exemplar build recovers the ×1.537 (owed,
   cheap).
2. Build the arm as the runtime-arm family's TABLE when the family's trigger
   fires: a bench cell where the prior contradicts the text and a
   compile-time decision loses past the null band (bak-2 vs
   phone-no-start-set is [ADAPTIVE-ARM]'s named witness).
3. K105 is that table's first new row, not a standalone fix ahead of it.

If Frank wants K105 off the books before the trigger, the order is the same:
fold RETRY's rows into the family table first, then K105.

### 7.3 Unlocks filed (with triggers)

- **(a) The expected first-passage time over the DFA under the iid prior**
  (an absorbing Markov chain, an exact integer solve for small machines;
  sound critic unlock (a), fit critic 14). It generalizes `adv`: it gives
  stay runs, multi-state END walks (u2), landmark gaps (#4), the inter-MATCH
  gap §4.5 lacks, and rev-inner G3 and rev-end-width (u3, u4). **Trigger:**
  the [MATCH-SPLIT] survey counting END arms with ≥ 2 reverse stay states;
  or the first U2 reader needing a match rate; or a third reader of `adv`.
- **(b) The weighted single-budget projection of §3.5's vector check.**
  **Trigger:** [EFFORT-BUDGET] rules weights.
- **(c) The static magnitude bound** is BUILT into the design (§2.4), not
  deferred.
- **(d) The exemplar route as a second unlock beside the arm** (§7.2).

**Answer-free choices taken here** (memory
`pcrec-answer-free-choices-are-mine`):
- one rate field per quantity, with the advance as a rational and no stored
  field;
- the scaled numerator (no division);
- the tie → DECLINE rule (`prefix_k`'s);
- `flip` as the smallest DECLINE rate;
- `src/core/scancost.c`;
- VERDICT's NONE as MASS's cardinality;
- `axes.def` as the meter's home (the axis IS the deny unit D158 compares);
- the verdict stays two-valued until the arm family builds.

## 8. Findings for the manager

F-1 to F-7 (§1.2), plus:
- **F-8 (new, a defect for a K row).** The [ENG-ISL] alternation island
  violates D158 under a caller-tuned `--work-budget`.
  - Witness: `(foo|bar|baz)q` on `fooq`, `--work-budget=2`. The default build
    gives up with `work`; `-fno-alt-island` answers (0,4). This holds on the
    default engine selection and on forced VM.
  - Mechanism: K102's class. The trie walk charges WORK per byte where the
    denied form's resumes charge STEPS.
  - D158 add. 1 accepts only K102, so this needs its own K row or a ruling
    that extends the allowance. Owner by analogy: [EFFORT-BUDGET].
  - Repro: `prior_cost_unify/island_work.sh`.
- **F-9 (correction).** Rev 1's "R4 multiplies a Zen 1-shaped rate by a
  Mac-shaped gap" is wrong. Rates are box-free, and no shipped verdict mixes
  boxes (F-5).
- **F-10.** `pcrec_sat_add`/`pcrec_sat_mul` (`src/opt/mrl.c:125`) are sound
  only for operands ≤ their callers' 2^40 cap (`a + b` is computed before the
  cap). That is not a defect for today's callers. It is a reason not to reuse
  them as general helpers (§2.4).
- **F-11.** On its witness, the lit-run axis derives DELETES (work sites −4),
  where rev 1 declared SUBSTITUTES. The population verdict is U4's.
- **(withdrawn).** Rev 1's §8(a) (C_ENTER and VF.gap as U3 movers) and
  §8(b) (K102 visible as a failing SUBSTITUTES row) are withdrawn. C_ENTER is
  a re-measurement (U3), the gap is MEASURED, and K102 is the vector check's
  one keyed allowance (§3.5).
- **(c, kept).** [MATCH-SPLIT]'s END+FREE stage owes `DR.walk_byte` and,
  beyond the proxy, unlock (a).

None is filed here: plan.md and known_issues.md are the manager's.
