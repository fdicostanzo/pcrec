# [PRIOR-COST-UNIFY]: one priced scan decision (DESIGN NOTE, revision 1)

Lane `pcudes`, 2026-10-11. Design only: nothing under `src/`, `tests/` or
`docs/spec/` moves. Read at main `85f3ef1d` (abi 75, [REQ-HANDOFF-L1] merged).

Inputs: plan.md [PRIOR-COST-UNIFY] (with its SHARED VOCABULARY note),
[ADAPTIVE-ARM], [SIZE-KNEE], [EFFORT-BUDGET], [START-DENSE], [EST-REGISTRY];
`docs/dev/optloop/lossreview/fixes.md` rev 2 §1 F1;
`docs/dev/reviews/2026-10-11-r2-lossreview-fixes.md` and `critic_family.md`
(findings 1-8, the `PcrecScanQ`/`PcrecScanExp`/`PcrecConsumerCost`/`pcrec_scan_verdict`
sketch); `src/opt/prefix_k.c` `model_cost`; D126 Q4, D141, D146, D148, D149,
D151, D152, D157, D158 (+add. 1), D160; `rlhbuild_report.md` §1.4, §7; K102,
K105; `match_split_requirements.md` §3, §5.1.

## 0. Answers first

1. **The family is not one question, it is three kinds plus a fourth that the
   row is really about.** Of the twenty members, five are PICKs (an argmin
   over the prior: set-leads, run window, run pin, req pick, run choice), one
   is a COMPARE (G1's density clause), and nine are cost comparisons that
   weigh a scan's stops against the work they save. This note calls that kind
   VERDICT. Six of the twenty are not decisions at all: G2 is a route fact,
   the utf8 NONE is data (D160), `FIND_FLOOR_PPM` is the prior's floor,
   `pass < 4` is a capacity, the `prefix_k` singleton gate is a form scope,
   and `vm_reseed_cal` is table data. The primitive the row asks for is the
   VERDICT kind. PICK and COMPARE already have their primitives (`findings.c`).
   D126 Q4 then needs VERDICT's NONE answer spelled once. It inherits MASS's
   cardinality, and that moves nothing, because every VERDICT member already
   prices with cardinality under NONE (§1.3).
2. **The primitive (§2)** has three parts:
   - `pcrec_scan_expect` turns a scan's FACTS (its stop set, run or cube,
     verify chain and span) into EXPECTATIONS: a stop rate, a pass rate (an
     independence estimate, labelled), the expected advance per stop, and
     the rate's source.
   - `pcrec_scan_cost` prices those expectations against pcrec's CONSUMER
     row, which is what a stop, a verify and an attempt cost pcrec's engine.
   - `pcrec_scan_verdict` compares two alternatives and returns PAYS or
     DECLINE plus the break-even stop rate. That rate is the [ADAPTIVE-ARM]
     hook.

   The model uses integer arithmetic only, compares by cross-multiplication
   and saturates, so it is bit-reproducible across boxes. It generalizes
   `model_cost` by the per-stop restart term `model_cost` lacks. The
   critic's `run_len` and `stay_len` are ONE quantity seen from two sides: a
   stay set's run length is the advance per stop of its complement. So the
   expectation has one `adv` field.
3. **The operation-kind table (§3)** is one grid of route × program class by
   operation kind, with TWO value planes over the same cells. The MEASURED
   plane is for selection: expected cost under the prior, each cell
   labelled MEASURED, DERIVED or UNMEASURED-DEFAULT with its box and regime.
   The CONTRACT plane is [EFFORT-BUDGET]'s meter: deterministic,
   box-independent and worst-case, each cell RULED or DERIVED, and today
   every cell is UNSET.

   Today's numbers come from TWO boxes. `prefix_k`'s cycles were measured on
   ubuntubudu (Zen 1) and `vm_reseed_cal`'s ns on the Mac (M1). Two cells are
   derived from stale or chosen inputs:
   - `C_ENTER` is 10.7 c/B × ~2, and 10.7 is the pre-[OPT-3] figure (7.75
     after the premultiplied table).
   - The framed reseed `gap` of 4 is a chosen setting where the measured
     cells derive 3.

   The two kit-form constants (`C_MEMCHR`/`C_BITMAP`) are the one part pcrec
   cannot own under D146. §3.3 gives the D146 disposition (Q1).
4. **D158 becomes table-checkable for the arithmetic half (§3.5).** Every
   start-table row on the VM route DELETES metered operations (it only
   removes attempts), so it satisfies D158 in the meter's units by
   construction. DFA routes carry no budget at all. Rows that SUBSTITUTE
   operations (possessify, the literal-run compare, the span scan) carry a
   declared map, and the check is Σ contract weight ≤ the denied form's.
   K102 is the witness: possessify's map (resume → work byte, plus the +5
   overshoot) fails that check against any weights with w(work) ≥ w(resume).
   The SUBSET half (that the deleted operations really are a subset) stays a
   per-row proof, plus [GIVEUP-DIFF]'s dynamic direction check.
5. **Migration (§5):**
   - U0: the table and the primitive, zero movers, with `model_cost` moved
     in verbatim.
   - U1: members read their INPUTS from the primitive, each keeping its own
     formula, zero movers.
   - U2..: each member's formula switches to the one verdict as its own
     commit. A trace-build both-formulas oracle counts the disagreements
     first. Zero disagreements make it a no-mover; anything else is a
     measured, abi-bumped mover.

   **K105 cannot be fixed by a prior-only verdict.** Its witness is a text
   that contradicts the prior, and pricing the restart term still admits it
   (§5.3). So K105's fix is [ADAPTIVE-ARM]'s first member. Its initial state
   comes from the verdict, and its run-time mechanism generalizes the RETRY
   adaptive text that already ships. That is the first behaviour change,
   with hcolon_in (×1.537) as its witness (Q4).
6. **Questions for Frank (§7): five.**
   - Q1: the kit-form constants under D146.
   - Q2: the table's home: [EST-REGISTRY]'s `estimates.def`, born with this
     section.
   - Q3: the MEASURED plane's reference box.
   - Q4: K105 through [ADAPTIVE-ARM] now.
   - Q5: keep the labelled independence product until joint rates exist.

---

## 1. Census

### 1.1 The members, read at main `85f3ef1d`

"Kind" is the rate question the member asks (D126 Q4's kinds plus VERDICT,
§1.3). "Expressible" says whether it can read the primitive of §2 without
changing its answer today.

| # | member | file:line | decides | reads | hand-set constant(s) | kind | expressible |
|---|---|---|---|---|---|---|---|
| 1 | G1 density | `src/gen/emit_dfa.c:7530` `req_byte_dominated_by` (the clause at :7537-7538) | elide a one-byte pre-check whose byte is no rarer than the scan's | `pcrec_find_no_commoner(rate,p,q)`; scan shape from `dfa_cand_scan` (:7381) | none; the `<=` tie rule | COMPARE | yes: COMPARE face (§2.5); see 1.2 F-1 on `memchr_form` |
| 2 | set-leads | `emit_dfa.c:7584` `req_set_leads_applies` | emit the set pick's memchr ahead of the run search | `pcrec_find_pick` over [run scan cube, set pick] | none | PICK | yes (PICK face); K85 is its cost symptom (1.2 F-4) |
| 3 | R4 adaptive-dense | `emit_dfa.c:8739` `cand_rs_dense_applies` | RETRY row: arm the adaptive re-seed armed | `pcrec_dfa_cand_ppm` (:7427) × `vm_reseed_cal[has_push].gap` | `> 1000000` (the unit); `gap` 16 / 4 | VERDICT | yes: `adv < gap`, by cross-multiplication |
| 4 | handoff K admission | `emit_dfa.c:7786` `req_landmark_admits` (+ `req_landmark_hit_ppm` :7753) | NEXT row `handoff`: re-enter at the landmark's next hit | hit rate h (independence product, ceil per step), the displaced row's mass m | none ("derived from the prior"); the formula `1/h − K > 1/m` | VERDICT | inputs yes; formula is an ADVANCE comparison, not a cost one (§5.2) |
| 5 | run choice | `src/facts/req.c:327` `rn_better` | which necessary run the fact keeps | information Σ popcount(K) | `PCREC_MIN_REQ_RUN_BITS` 16 (`limits.def:405`, RULED) | PICK (by information, not rate) | the fact cannot read consumer costs (1.2 F-3) |
| 6 | G2 one-attempt | `emit_dfa.c:7489` `req_route_one_attempt` | PRESENCE row `one-attempt` | route + BOUND row + exact-hybrid/frameless | none | — (route fact) | excluded: not a rate decision (fixes.md r2 F5) |
| 7 | prefix_k offset pick | `src/opt/prefix_k.c:189` `pcrec_prefix_ksets`, `model_cost` :114 | scan offset k* and verify chain | `pcrec_find_set_ppm` per offset; `k0` mass | `C_MEMCHR` 6, `C_BITMAP` 116 (:65-66), `C_VERIFY` 250, `C_ENTER` 2000 (:67-68), `C_MISPRED` 1500 (:85), `MATERIAL_NUM/DEN` 2/1 (:99) | VERDICT (an argmin planner, D152) | consumer constants yes; `C_MEMCHR`/`C_BITMAP` no (§3.3) |
| 8 | VM hat admission | `emit_dfa.c:7176` `pf_vm_start_applies` | NEXT row `first-class` (VM) | `\|S\| < 256`, not nullable | 256 (D149 UNMEASURED, the comment says so) | VERDICT (unwritten: a MASS admission is filed, D148 add. 2 Q-R5) | yes, as a mover |
| 9 | DFA hat admission | `emit_dfa.c:7019` `pf_dfa_start_set` | NEXT rows `first-*-bounded` | T ⊊ E (structural) | none | VERDICT (unwritten: mass + entry, K91) | yes, as a mover |
| 10 | plain byte-class rows | `emit_dfa.c:9008-9017` (`byte-class[-bounded]` in `cand_rows[]`) | NEXT: scan the candidate set vs `none` | always applies | none | VERDICT (unwritten: hex8 under `-fno-start-set`) | yes, as a mover |
| 11 | M2.1 stay states | `emit_dfa.c:4777` `pick_skip_states` | which states get a stay skip | byte COUNT of the stay set | `bestcnt = 191` (:4783, i.e. ≥ 192 of 256) | VERDICT (by count, not mass) | yes, as a mover ([OPT-3-RUNEND](a), WORD-WAIT) |
| 12 | utf8 rate NONE | `src/core/findings.c:390` `pcrec_find_byte_rate` | which prior applies | the chain's `serves` | — | — (data, D160) | not a member: D160's authored prior is the fix |
| 13 | run window start | `findings.c:586` `pcrec_find_run_window_start` | the 8-position window of a long run | SEQUENCE MASS | `PCREC_MAX_REQ_RUN_EMIT` 8 (`limits.def:394`, MEASURED: one word load) | PICK | already on the PICK/MASS primitives |
| 14 | run pin | `src/facts/kset.c:298` `pcrec_run_pin` | the exact stretch the pin claims | `pcrec_find_pick` | none | PICK | already |
| 15 | req pick / req byte | `src/facts/req.c:669` `pcrec_req_window`, `:709` `pcrec_req_pick` | the run's scan member; the set's pick | `pcrec_find_run_scan_index`, `pcrec_find_set_pick` | none | PICK | already |
| 16 | reseed calibration | `src/gen/emit_vm.c:11033` `vm_reseed_cal` | the R4 gap and the adaptive arm's block/cap/first | measured per class (Mac) | 16/64/1024/64, 4/16/64/2 | — (table data) | `gap` becomes a DERIVED cell (§3.2); block/cap/first belong to [ADAPTIVE-ARM] |
| 17 | prefix_k singleton gate | `prefix_k.c:225` `count != 1` | only a one-byte set may be scanned at k > 0 | walk set cardinality | 1 | — (form scope) | UNLOCK: the kit's cube FIND row lifts it (trigger ci-moskva) |
| 18 | scan-chain floor | `limits.def:392` `PCREC_MIN_SCAN_CHAIN` 2 | shortest bounded run collapsed to a scan edge | constant | 2 (MEASURED both ways: null at m = 2..4; its size half is unconditional) | VERDICT (time half) + SIZE-KNEE (size half) | expressible; HELD (no measured gap, D77) |
| 19 | find floor | `limits.def:186` `PCREC_FIND_FLOOR_PPM` 2 | the prior's normalization floor (`findings.c:154-170`) | — | 2 | — (data) | not a member: it bounds the primitive's denominators (max advance 500,000 B) |
| 20 | stay pass cap | `emit_dfa.c:4782` `pass < 4` | at most 4 stay tables per machine | — | 4 | — (capacity) | not a member: SIZE-KNEE's |
| — | deferpre | (unbuilt) | — | — | K = 64, UNLABELLED | VERDICT if built | label it UNMEASURED DEFAULT (D149) when built |
| new | [MATCH-SPLIT] END admission | (unbuilt; `match_split_requirements.md` §3.3, §5.1) | admit an unbounded END class beside a FREE class | the reverse stay set's run length vs the free locator's gap | none (by design) | VERDICT | the first reader born on the primitive (§4.3) |

Score: of the twenty, nine are VERDICT, five PICK and one COMPARE. Five are
not decisions: G2, the utf8 NONE, `FIND_FLOOR_PPM`, `pass < 4` and the
singleton gate. `vm_reseed_cal` is not a decision either. It is table data
that a decision reads, which is exactly what §3 absorbs. [MATCH-SPLIT]'s END
admission is a tenth VERDICT, unbuilt.

### 1.2 Findings from the census

- **F-1. G1's `memchr_form` clause is NOT a kit-form cost.** The critic
  listed it among the two things the sketch "cannot express". `memchr_form`
  is set where the selected NEXT row's `scan` is `PF_SCAN_BYTE`, or on the
  ATTEMPT route's memchr-or-nothing (`emit_dfa.c:7390`, :7410). That is a
  FACT about the stop set: a singleton at the candidate start, with no
  verify chain. It is not a statement about the kit's rendering. Its own
  comment says why it exists: it "keeps the density comparison off" the
  offset rows, whose `p` is a scan byte at k* with a verify chain. So the
  clause is a SHAPE scope for a COMPARE, and it is expressible as
  `exp.shape == SINGLETON_AT_START`. Generalizing it (a set scan compared by
  mass) would be a mover, and is filed rather than proposed (D77).
- **F-2. The family's NONE answers already differ, and correctly so.** Under
  NONE:
  - G1 (COMPARE) answers `false`, so it keeps the pre-check.
  - The K admission, R4 and `prefix_k` (VERDICT) price with cardinality,
    inside `pcrec_find_set_mass`.
  - set-leads and the other PICK members take the cardinality argmin with
    ties to the rightmost ([K82] (C)).

  A single "one primitive" that answered NONE one way would move G1 under
  `-e utf8`: two singletons tie on cardinality, and G1's `<=` would then
  elide every such pre-check. D126 Q4 is already right here. The unified
  primitive must keep the kinds distinct (§2.5), and the only new spelling
  is VERDICT's own NONE rule.
- **F-3. The run-choice fix that fixes.md proposes cannot live where the run
  choice lives.** `rn_better` is inside the `req_run` FACT (`src/facts/req.c`).
  D126 Q5 rules that the record excludes route and emission decisions, and a
  rate × per-hit cost choice reads consumer costs that depend on the route.
  The general form is D157's. The fact states the candidate runs (every run
  clearing `PCREC_MIN_REQ_RUN_BITS`, ranked), and the decision that consumes
  a run (PRESENCE, OFS) picks among them through the verdict. RUN-PICK's fix
  is therefore a fact-shape change plus a decision. It is not a reweighting
  of `rn_better`.
- **F-4. Two PICK and COMPARE members are VERDICTs wearing a cheaper kind.**
  set-leads asks "is the set pick rarer". The question it means is "does a
  lead memchr pay", and K85 (cls-n-uc +0.025..+0.036 ns/B, a lead that never
  rejects on match-dense text) is that gap measured. G1's density clause is
  a cost question too: one pass against two. Neither is proposed for change
  here, because neither has a cell beyond K85 (D77). Both are listed as
  VERDICT candidates in §4.
- **F-5. The constants come from two boxes and one is stale.**
  `prefix_k`'s four constants were measured on ubuntubudu (Ryzen 5 1600, Zen
  1). `docs/dev/opt3_dfa_scan_measurement.md` names the box; `prefix_k.c`'s
  "this box" predates the 2026-09-04 move. `vm_reseed_cal`'s inputs were
  measured on the Mac M1 (`docs/design/hyb_reseed.md` §3, "Mac M1, gcc-16").
  R4 already multiplies a Zen 1-shaped rate by a Mac-shaped gap.

  `C_ENTER` is derived as "10.7 cycles/byte × ~2 bytes". 10.7 is the
  PRE-[OPT-3] per-byte figure; the premultiplied table it then motivated
  measured 7.75 c/B (`src/gen/CLAUDE.md` [OPT-3]), and "~2 bytes" is
  unmeasured. Standing question 1 (§6) carries the consequence.
- **F-6. `limits.def` already has a "selection knee" kind**, with
  `MIN_SCAN_CHAIN`, `FIND_FLOOR_PPM`, `MAX_REQ_RUN_EMIT`, `MIN_REQ_RUN_BITS`,
  `SIZE_TERM_*`, `VM_ISL_*` and `VM_INLINE_CHAIN_MAX_BYTES` in it. Those are
  CAPS and FLOORS listed by `--list-limits`. The operation-kind table's cells
  are a different thing: per-operation PRICES with a MEASURED/CONTRACT
  plane. They do not belong in `limits.def` (Q2 places them).

### 1.3 VERDICT: the kind the row is about

A VERDICT compares two scan ALTERNATIVES by expected cost per subject byte.
Its members are #3, #4, #7, #8, #9, #10, #11, the time half of #18, and
[MATCH-SPLIT]'s END admission.

Its NONE answer, spelled once (D126 Q4): **price with MASS's NONE answer
(cardinality).** It is a decided, answer-free choice. Every VERDICT member
that reads a rate today already does exactly this:
- #3 reads `pcrec_dfa_cand_ppm`, which calls MASS;
- #4 reads `pcrec_find_set_mass` and the product over masses;
- #7 reads `pcrec_find_set_ppm`.

The unwritten members inherit it. So the rule is a restatement, and it moves
no byte.

---

## 2. The primitive

### 2.1 Facts in: a scan, described by what it stops on

```c
/* A scan as FACTS: what it stops on and what it checks at each stop. No form
 * (memchr, pair, SWAR, table) appears anywhere: the kit chooses forms
 * (D146), pcrec describes the site. */
typedef struct {
    PcrecScanShape shape;     /* SINGLETON_AT_START, SET, CUBE_RUN, NONE (every byte) */
    const uint8_t *set;       /* SET / SINGLETON: the stop set (256 flags)            */
    const unsigned char *bytes, *mask;  /* CUBE_RUN: the run's positions (T, K)       */
    int            n;         /* CUBE_RUN: positions                                 */
    int            nverify;   /* the verify chain, ascending offset                  */
    const PcrecVerifyTerm *verify;      /* each: offset + set (or T,K)               */
    long long      span;      /* proven span bound in bytes, or PCREC_SPAN_UNKNOWN    */
} PcrecScanQ;
```

The shapes are exactly the ones the members have today: the NEXT rows' `scan`
kind (`PF_SCAN_BYTE`/`SET`/`LANDMARK`/`OFS`), the run window (T, K), and the
k-set walk's offsets.

### 2.2 Expectations out

```c
typedef struct {
    uint32_t stop_ppm;    /* stops per 10^6 subject bytes: MASS(set) for a set;
                           * for a CUBE_RUN the product over positions, ceil at
                           * each step (req_landmark_hit_ppm's rule, moved here) */
    uint32_t pass_ppm;    /* of the stops, the fraction passing the verify chain:
                           * the product of the terms' masses.
                           * INDEPENDENCE ESTIMATE, labelled (critic F8): bignum's
                           * independence prediction was 13x and measured a wash;
                           * [OPT-REQPOS] measured joint rates that are not
                           * products. Never read as a probability of a match. */
    uint64_t adv_milli;   /* expected advance per stop, in thousandths of a byte:
                           * 10^9 / stop_ppm, saturating; bounded by the floor
                           * (FIND_FLOOR_PPM 2 -> 500,000,000) except stop_ppm 0 */
    PcrecRateSrc src;     /* RATE (a bundle served this encoding) | NONE
                           * (cardinality) -- the accessor's answer, recorded,
                           * never re-tested by a reader */
} PcrecScanExp;

void pcrec_scan_expect(Ctx *cx, const PcrecScanQ *q, PcrecScanExp *e);
```

**`run_len` and `stay_len` are one field.** The critic's sketch had both.
- A STAY set T (a DFA state that stays put on T) runs for an expected
  1/(1 − mass T) bytes. That is the advance per stop of the scan that stops
  on T's complement.
- A STOP set S advances 1/mass S.

So a stay skip is a scan over the complement, and the [MATCH-SPLIT] END
walk's expected length is the reverse stay set's `adv` (§4.3). One field and
one formula serve both readers (the general-form lens). `run_len` in the
landmark sense, the expected gap between run hits, is the same field for a
CUBE_RUN.

### 2.3 The consumer price, and the verdict

```c
/* Expected cost per 10^6 subject bytes, in the MEASURED plane's unit
 * (centi-cycles), of running scan `e` in front of consumer row `c`
 * (route x program class, §3). */
uint64_t pcrec_scan_cost(const PcrecScanExp *e, const PcrecOpRow *c,
                         unsigned scan_byte_cc /* §3.3: interim, labelled */);

/*   cost = 10^6 * scan_byte_cc                       (the kit's scan; §3.3)
 *        + stop_ppm * (stop_reentry + verify(chain))  (pcrec, per stop)
 *        + stop_ppm * pass_ppm / 10^6 * attempt        (pcrec, per false entry)
 *        + stepped_ppm * step_byte                     (pcrec, bytes the engine
 *                                                       walks itself: K bytes per
 *                                                       handoff hit, all bytes
 *                                                       for NONE)                 */

typedef enum { PCREC_SCAN_PAYS, PCREC_SCAN_DECLINE } PcrecScanVerdict;
PcrecScanVerdict pcrec_scan_verdict(uint64_t cost_new, uint64_t cost_old,
                                    unsigned bar_num, unsigned bar_den,
                                    uint32_t *flip_ppm /* may be NULL */);
```

`model_cost` (`prefix_k.c:114`) is this cost with `stop_reentry = 0`,
`stepped = 0` and per-byte units. The critic's missing per-stop restart term
is `stop_reentry`. Under [MEMFN] the restart is pcrec's side of a stop: the
engine re-entered at a kit hit, a reseed, a DFA restart from the landing.
That makes it a CONSUMER cost and pcrec's to own (D146's line).

`bar_num/bar_den` is the caller's materiality bar (`prefix_k`'s
`MATERIAL_NUM` 2/1; 1/1 elsewhere). The bar belongs to the [SIZE-KNEE] /
MATERIALITY family (plan.md), not to this row. The verdict takes it as an
argument and never owns a value.

`flip_ppm` is the stop rate at which the verdict's sign changes, holding the
other expectations fixed. It is the [ADAPTIVE-ARM] hook (§4.2). It costs
nothing to compute: the cost is linear in `stop_ppm`, so the break-even is one
exact cross-multiplied solve.

### 2.4 Integer rules (bit-reproducible, `prefix_k`'s own rule)

1. Rates are `uint32` ppm and costs are `uint64` centi-cycles per 10^6 bytes.
   There is no floating point anywhere: a selection must not change with the
   compiling box.
2. **Compare by cross-multiplication, never by dividing.** a/b > c/d is
   computed as a·d > c·b, using `pcrec_sat_mul`/`pcrec_sat_add`
   (`src/opt/mrl.c`; saturation is monotone, so a saturated comparison
   resolves in the right direction or ties). The K admission (`(10^6 − K·h)·m
   > 10^6·h`) and R4 (`ppm·gap > 10^6`) are already written this way.
   `model_cost` is not: it truncates at three divisions by 10^6.
3. **Rounding is fixed per formula and never changed silently.** U0 moves
   `model_cost` in VERBATIM, truncation order included. `prefix_k`'s
   selections are pinned by it, and changing it is a mover counted under U2
   (§5).
4. The ceil-per-step product for a CUBE_RUN's `stop_ppm` is
   `req_landmark_hit_ppm`'s existing spelling. It moves into the primitive
   as the one copy.

### 2.5 The question kinds, and where each NONE lives

| kind | primitive | NONE answer | readers |
|---|---|---|---|
| MASS | `pcrec_find_set_mass` / `_seq_mass` (findings.c) | cardinality | `pcrec_scan_expect` (stop and pass rates) |
| PICK | `pcrec_find_pick` | cardinality argmin, ties to the reader's rightmost | #2, #13, #14, #15, (#5 after F-3) |
| COMPARE | `pcrec_find_no_commoner` | `false` | #1 |
| VERDICT | `pcrec_scan_verdict` over `pcrec_scan_cost` | cardinality, inherited from MASS through `pcrec_scan_expect` (§1.3) | #3, #4, #7-#11, #18 time half, MATCH-SPLIT END |

The VERDICT primitive lives beside the other three. That makes it a fourth
section of `findings.c`'s "THE PRIMITIVES" block, or a sibling file
`src/core/scancost.c` once that block grows past one screen. The choice is
answer-free; this note takes the sibling file, because the table it reads is
not findings data. It sits in the base tier (it reads only rates and the
table), so every layer may call it.

---

## 3. The operation-kind table

### 3.1 Shape

One grid. **Rows** are route × program class: the units whose operations
cost differently. **Columns** are operation kinds. There are **two planes**
over the same grid, as Frank's SHARED VOCABULARY note asks: the same kinds
and structure, not necessarily the same values.

- **MEASURED plane (selection).** An expected cost under the prior, in
  centi-cycles on one reference box (Q3). Each cell is labelled:
  - MEASURED: box, compiler, regime, source file;
  - DERIVED: a formula over other cells;
  - UNMEASURED-DEFAULT: D149's label, with its trigger;
  - KIT: the kit's, absent here (§3.3);
  - n/a.
- **CONTRACT plane (metering, [EFFORT-BUDGET]).** Deterministic,
  box-independent and worst-case. Each cell is RULED (Frank) or DERIVED
  (from a counting rule), or UNSET. Memory bounds (frames, trail, recursion)
  are NOT effort ([EFFORT-BUDGET] study item 4), so their cells are n/a in
  this plane. They stay separate budgets.

Rows:

| row | route × class | what an operation is here |
|---|---|---|
| DU | DFA unanchored (premultiplied or indexed table) | the forward table walk |
| DA | DFA attempt (computed goto per start) | a labelled-state step; one attempt per start |
| DR | DFA reverse walk (RECOVER `reverse-pass`, LOCATE `rev-end`) | the reverse table walk |
| VL | VM frameless (`has_push` false) | a VM step with no resume frame |
| VF | VM framed | a VM step with frames and trail |
| HY | VM hybrid retry (the inlined prefilter re-asked) | a prefilter call from the retry loop |

Columns:

| kind | meaning | metered today? |
|---|---|---|
| `step_byte` | the engine walks one subject byte itself | VM: steps (D51) where backtracking; DFA: no budget |
| `stop_reentry` | a scan stop hands control to the engine (restart, landing, reseed) | no |
| `verify` | one extra positional test at a candidate (load + probe; the mispredict term is per-term, `C_MISPRED·min(p,1−p)`) | no |
| `attempt` | entering the engine on a candidate that will fail | VM: its steps |
| `reseed` | one prefilter call from the hybrid retry | no |
| `walk_byte` | one byte of a reverse walk | no |
| `resume` | a backtrack resume (pop + restore) | STEPS (D51) |
| `work_byte` | forward-only work the fail label never sees (a possessive scan byte, a span-compare byte) | WORK (D49) |
| `frame` / `trail` | a push / a trail entry | FRAMES / trail capacity (memory) |
| `scan_byte` | a byte passed over by a delegated FIND | KIT: never pcrec's (§3.3) |

### 3.2 The MEASURED plane, with where today's numbers come from

| cell | value (native unit) | label | source | note |
|---|---|---|---|---|
| DU.step_byte | 7.75 c/B (775 cc) | MEASURED, Zen 1 (ubuntubudu), throughput on the bench's PERIODIC t-a/t-b/t-c (I-10's confound) | [OPT-3] STEP 1 (`src/gen/CLAUDE.md` [OPT-3]: 7.751 premultiplied) | stale: predates [CC-DIFF], [OPT-EDGE] and [OPT-5]'s scan edge |
| DU.attempt | 2000 cc (`C_ENTER`) | DERIVED = step_byte × survival, from 10.7 c/B (pre-premul) × "~2 bytes" (UNMEASURED) | `prefix_k.c:52-58` | **stale by its own input**: 7.75 × 2 = 1550. `prefix_k`'s own note measured 11/1,352 selections moving between 12 and 20 cycles, so re-deriving is a counted mover (§5) |
| DU.verify | 250 cc + 1500 cc · min(p, 1−p) (`C_VERIFY`, `C_MISPRED`) | MEASURED, Zen 1 | `offset_k_skip.md` §4.2, §7.3 | the mispredict term is what separated bignum from the controls |
| DU.stop_reentry | — | UNMEASURED-DEFAULT (0 today, implicitly) | none | the critic's missing term. Nearest evidence: b2ledger's fitted `c_call` 7.72 ns per memchr occurrence (Zen 1, one free parameter, one cell, and the kit's call is inside it) |
| DA.* | — | UNMEASURED | — | no member prices the attempt route yet; `attempt_cand` is memchr-or-nothing by charter |
| DR.walk_byte | — | UNMEASURED | rev-end timed only whole-call (O-96, K103/K104) | [MATCH-SPLIT] END's admission needs it (§4.3) |
| VL.attempt | 1.6 ns per failed attempt | MEASURED, Mac M1, gcc-16, scratch tier | `hyb_reseed.md` §3, `docs/dev/reseed/timing_mac.md` | a different box from DU's |
| VF.attempt | 8.6 ns | MEASURED, Mac M1 | same | |
| HY.reseed | ~25 ns per prefilter call, "about constant" | MEASURED, Mac M1 | same | |
| VL/VF R4 `gap` | 16 / 4 bytes | VL: MEASURED crossover; VF: CHOSEN setting (`emit_vm.c:11009-11012` says so) | `vm_reseed_cal` | **becomes DERIVED: ⌈reseed / attempt⌉ = ⌈25/1.6⌉ = 16 (agrees) and ⌈25/8.6⌉ = 3 (disagrees with 4)**: the one cell where unification moves a stamp; counted under U2 |
| VL/VF block, cap, first | 64/1024/64, 16/64/2 | chosen settings | `vm_reseed_cal` | NOT this table: they are the run-time arm's parameters, [ADAPTIVE-ARM]'s (§4.2) |
| *.scan_byte | `C_MEMCHR` 0.055 c/B, `C_BITMAP` 1.16 c/B | MEASURED Zen 1 glibc AVX2 (opt3 CONTROL 1) | `prefix_k.c:65-66` | KIT: §3.3 |
| VL/VF resume, work_byte, frame, trail | — | UNMEASURED in this plane | K102's counts are COUNTS (800 steps + 394 work vs 0 + 1,199), not costs | [EFFORT-BUDGET]'s study measures them when it opens |

**Units.** Each cell carries its native unit. The plane's comparison unit is
centi-cycles on the reference box. A cell from another box is converted by
DERIVED = value × that box's measured clock, and it keeps a CROSS-BOX flag.
R4 today is exactly such a cross-box comparison: a Zen 1-shaped rate against
a Mac-shaped gap. Q3 asks Frank to fix the reference box. Until then every
MEASURED cell keeps its native unit and box, and U0 changes no number.

### 3.3 The kit-form constants (D146 disposition)

`C_MEMCHR` and `C_BITMAP` price HOW a set is scanned, which since R4c/R4g is
the kit's FIND row (`memfn/src/pffind.c`). `prefix_k` uses them to rank WHAT
to scan: offset 0's escape set k0 (a table walk when multi-byte) against a
singleton at k*. D146 ("pcrec does no cost comparison") forbids pcrec from
pricing forms. It does not forbid pcrec from deciding what to search for, and
that decision currently needs a form price.

Three ways through, discussed in Q1:
- **(i) Labelled interim constants under a guard.** The two cells stay in
  pcrec's table as KIT-ESTIMATE cells. Only the WHAT-to-scan planner
  (`prefix_k`) may read them, and a structural check fails any other
  reader. The kit's actual choice of form is never consulted or presumed.
- **(ii) The kit takes the choice (D157's shape).** pcrec states the k-set
  walk as facts (offsets, sets, masses), the kit picks which offset to scan
  and which to verify, and it reports the choice back. G1 and the reseed
  need to know the scanned byte, so this needs a return channel.
- **(iii) A form-neutral scan term.** Assume one per-byte scan cost for
  every set, so it cancels in every comparison. That is a mover:
  `prefix_k`'s "the scan MUST move" rule is exactly the 20× memchr/bitmap gap.

Leaning: (i) now and (ii) as the end state, filed as a kit request when a
multi-offset FIND site has a cell. (iii) is refuted by `prefix_k`'s own §7.3
table.

### 3.4 How [EFFORT-BUDGET] reads the CONTRACT plane

[EFFORT-BUDGET]'s sketch is one abstract counter with per-piece weights as
the dials. With this table, a weight is one CONTRACT cell `W[row][kind]`.
That gives three things:

- **The meter.** The emitted charge is `RX_CHARGE(kind)`, which expands to
  `effort_left -= <W[row][kind]>`: a LITERAL taken from the CONTRACT plane at
  compile time, so the artifact's metering is box-independent and stated.
  The weights would be stamped on every VM artifact, e.g.
  `<PREFIX>_EFFORT_WEIGHTS "resume=…,work=…"`. That is an abi event and a
  `docs/spec/limits.md` hunk (D80) whenever a weight moves.
- **Selection in the meter's units.** A VERDICT can be evaluated a second
  time in the CONTRACT plane. That is how D158 becomes checkable at
  table-build time (§3.5).
- **What this row creates for [EFFORT-BUDGET].** The grid, the kinds and an
  empty, declared CONTRACT plane (every cell UNSET). The values are that
  row's study output: its items 1-3 ("the unit and the per-piece weights",
  "caller dials, compiler-derived, or a fixed table", "D158 by
  construction"). Nothing here pre-empts its study.

### 3.5 D158, checkable for which rows

D158: if the denied build answers, the default build answers, under every
budget setting. Split any row's effect on the meter into two halves:
- a **subset half**: the operations the row leaves are a sub-multiset of the
  denied path's operations. This needs a proof or a run;
- a **weight half**: the substituted operations weigh no more in the
  CONTRACT plane. This is arithmetic.

Each row declares a `meter` cell: DELETES, SUBSTITUTES(op → op′, ratio,
overshoot), or ADDS. A table-build check (no per-pattern work) then asserts:
- no row ADDS a metered kind;
- every SUBSTITUTES row has Σ W(op′) · ratio + overshoot ≤ Σ W(op) at its
  declared count.

| rows | meter class | D158 at table-build time |
|---|---|---|
| every DFA route row | — | trivially: DFA artifacts carry no budget, so they cannot give up |
| VM-route start-table rows: NEXT `first-class`, FIRST `handoff`, PRESENCE (pre-check: an unmetered pass or an early return), RETRY `exact`/`clamped`/`anchored`/`adaptive*`, BOUND, WINDOW | DELETES (they only remove attempts or attempt positions; the scan is unmetered, `scan_byte` is KIT) | **yes, for the weight half**. The subset half is each row's existing one-way argument: D148 Q6, the RETRY "attempts are a subset" sentence (`tuning.md` §2.35), LR-S11 |
| possessify (A0/A1/B arms) | SUBSTITUTES(resume → work_byte, 1:1, overshoot) | **yes, and it FAILS today**: K102's +5 residue (1,199 vs 1,194) is the overshoot, so the check reports the known violator at table-build time rather than on a budget ladder. This is K102 as the payoff witness |
| VM literal-run compare (S2a), span scan (cursor rung), island trie | SUBSTITUTES (a byte chain's steps → compare/scan bytes; a chain's resumes → trie nodes) | yes, given each row's declared map (S2a's "the budgets charge what the per-byte chain charged" is a map stated in prose) |
| rows whose metered effect is data-dependent in both directions | — | no: GIVEUP1's direction check ([GIVEUP-DIFF], LR-G5) stays the control. None is known; the census of meter cells (§5 U4) is what would find one |

So the table makes the WEIGHT half of D158 a compile-time, per-row
statement. The SUBSET half remains a proof plus the dynamic direction check.
That is the honest scope of "D158 becomes compile-time checkable for most
rows".

---

## 4. How each member reads it

### 4.1 One line each (as first-match rows where the member is a selection)

| # | member | reads (after its U2 commit) |
|---|---|---|
| 1 | G1 PRESENCE `dominated` | COMPARE face, unchanged: `no_commoner(scan.stop, q)` under `exp.shape == SINGLETON_AT_START` (F-1). VERDICT candidate, filed, no cell |
| 2 | PRESENCE `set-leads` | PICK, unchanged. VERDICT candidate whose cell is K85: lead pays iff `verdict(cost(run search with lead), cost(run search)) == PAYS` |
| 3 | RETRY `adaptive-dense` | `exp(cand scan).adv_milli < 1000 · gap[VL\|VF]`, with gap DERIVED = ⌈HY.reseed / V*.attempt⌉ |
| 4 | NEXT `handoff` | `verdict(cost(landmark CUBE_RUN, K stepped), cost(displaced row)) == PAYS`; under U1 it keeps `1/h − K > 1/m` reading `exp.adv` |
| 5 | run choice | the `req_run` fact lists candidate runs (F-3); PRESENCE picks with `verdict` |
| 7 | `prefix_k` | the planner keeps its argmin (D152: an argmin is not first-match); each candidate's cost is `pcrec_scan_cost` over DU, with `MATERIAL` as the bar |
| 8 | NEXT `first-class` (VM) | adds `verdict(cost(S seek), cost(none)) == PAYS` to `\|S\| < 256` (the Q-R5 MASS admission) |
| 9 | NEXT `first-*-bounded` (DFA hat) | adds `verdict(cost(T), cost(E)) == PAYS` to T ⊊ E (K91's entry term is `stop_reentry`) |
| 10 | NEXT `byte-class[-bounded]` | `verdict(cost(set), cost(none)) == PAYS` (hex8's case) |
| 11 | `pick_skip_states` | per state, `exp(complement of stay).adv_milli` ≥ the skip's break-even (DU.stop_reentry / DU.step_byte), replacing `bestcnt = 191` |
| 18 | `MIN_SCAN_CHAIN` time half | held at 2. If it ever moves, it moves on `exp(edge class).adv` |
| new | [MATCH-SPLIT] END | §4.3 |

Rows 1, 2 and 5 are listed so that each member has one stated reading. Only
rows 3, 4, 7 and 11 have a measured reason to switch now: K105, the stale
`C_ENTER`, the derived gap disagreement and WORD-WAIT. The others switch when
their cell exists (D77).

### 4.2 The adaptive-arm hook

[ADAPTIVE-ARM]'s general form is a table of armed / unarmed / off, whose
INITIAL state the primitive sets. Its runtime counter may flip it. The hook
works in three steps:

1. The verdict returns PAYS or DECLINE at the prior, plus `flip_ppm` (§2.3).
2. **Initial state.** PAYS → `armed`, DECLINE → `unarmed`, and `off` where
   the sign cannot flip at any stop rate the text could show. "Cannot flip"
   has a constant-free test: evaluate the verdict at the two ends of the
   rate's support, the floor (`FIND_FLOOR_PPM`) and 10^6. If the sign is the
   same at both, the decision is static and needs no arm.
3. **Whether to EMIT an arm** at all is a size question (an arm is ~560 code
   bytes per artifact today, from the RETRY precedent). It belongs to
   [SIZE-KNEE], or to [ADAPTIVE-ARM]'s own trigger cell (bak-2 vs
   phone-no-start-set). It is not decided here.

**The RETRY adaptive rows are the arm's prototype.** `reseed_steps`/
`reseed_block` (`emit_vm.c`) hold a per-call state that is armed by a short
gap, has a doubling block and is disarmed by a long gap. That is exactly
"armed / unarmed with a run-time counter". `vm_reseed_cal`'s block, cap and
first are the arm's parameters. So [ADAPTIVE-ARM] generalizes a shipped
mechanism rather than adding one, and its first new member (K105's handoff
re-entry, §5.3) reuses that text. That is the general-mechanisms rule
(memory `pcrec-general-mechanisms-not-special-cases`).

### 4.3 [MATCH-SPLIT]'s END admission as a reader

`match_split_requirements.md` §3.3 and §5.1 (ruled) admit an UNBOUNDED END
class beside a FREE class only when the expected suffix walk is short. In
this primitive:

- `walk = pcrec_scan_expect` over the REVERSE machine's stay set near `n`,
  expressed as its complement stop set: `walk.adv_milli` is the expected walk
  length.
- `free = pcrec_scan_expect` over the free locator's stop set (its first-set
  MASS): `free.adv_milli` is the expected inter-candidate gap.
- Admit iff `walk.adv_milli · DR.walk_byte < free.adv_milli · <the free
  route's per-byte cost>`. That compares two primitive outputs, each priced
  by one table cell. The rule has no constant of its own (ruled
  "no hand-set constants").
- A bounded END arm needs none of this: §5.1's cheap test `start ≥ n − max
  width` is a fact.

The reader also names what is missing: DR.walk_byte is UNMEASURED (§3.2). So
the END+FREE stage of [MATCH-SPLIT] (its third build step) owes one
measurement this row's U0 records as a labelled cell.

---

## 5. Migration

### 5.1 Steps (implement-then-replace, no-mover first)

| step | what | movers | gate |
|---|---|---|---|
| U0 | The table (§3) as an X-macro with both planes and labels, every MEASURED value transcribed with its unit/box/provenance and every CONTRACT cell UNSET; `pcrec_scan_expect` / `_cost` / `_verdict`; `model_cost` and `req_landmark_hit_ppm`'s product moved in verbatim. `--list-limits`-style listing of the table (or [LIST-TABLES]). | **zero** (no reader switched; `prefix_k` calls the moved function) | `scripts/emit_sweep.py --ref <base>` all streams + `-e utf8` + every limit variant, 0 movers; a unit check `tests/core/scancost_check.c` (§5.4) |
| U1 | Every VERDICT member reads its INPUTS through `pcrec_scan_expect` (stop rate, pass rate, adv), each KEEPING its own formula: #3's `ppm·gap > 10^6`, #4's `(10^6 − K·h)·m > 10^6·h`, #7's `model_cost`. `vm_reseed_cal.gap` is read from the table (value unchanged, label CHOSEN on VF). | **zero** | emit_sweep as U0; a source check that no VERDICT member calls `pcrec_find_byte_rate`/`_set_mass` directly (the reader census by grep, §5.4 control (c)) |
| U2.k | Per member, its formula switches to `pcrec_scan_verdict(pcrec_scan_cost(...))`. **First**, under `-DPCREC_CAND_TRACE`, a both-formulas oracle (the start table's C2 precedent) runs the old and the new formula at every ask and counts disagreements over corpus + bench, both encodings, all variants. Zero disagreements → a no-mover commit. Otherwise it is a MOVER commit: its own abi bump with readers by grep (D76/D94), a mover manifest by id, a Linux alpha on the bench box (D144 add. 4), and the identity re-pin. | per member, counted before the build | the oracle's disagreement count; then the mover's own D144 alpha |
| U3 | The re-derivations §3.2 found stale, each as its own measured commit: DU.attempt from the current step_byte (and a measured survival length), VF.gap DERIVED (3, not 4). Each needs its cell re-measured on the reference box (Q3) first. | counted (`prefix_k`: the 12-20 cycle band's 11/1,352; R4: framed hybrids with `adv` in [3,4)) | as U2 |
| U4 | Every row gets its `meter` cell (§3.5) and the table-build D158 weight check. CONTRACT values come from [EFFORT-BUDGET]; until then the check runs with weights UNSET and reports only ADDS rows. | zero | the check, with a planted ADDS row |
| U5 | The first behaviour change: K105 (§5.3) | K105's movers | §5.3 |

The order follows D153 (remodel first). U0/U1 touch `emit_dfa.c`'s RETRY and
NEXT predicates, `prefix_k.c` and `emit_vm.c:11033`. The remodel overlap
table is §5.5.

### 5.2 Why U1 cannot already be U2

The four VERDICT members that exist today use three different formulas:
- #4 compares ADVANCES: `1/h − K` bytes against `1/m`. It has no costs.
- #3 compares a gap against a constant crossover.
- #7 compares costs with truncating division.

One verdict over one cost model is the goal, and on some patterns it answers
differently from each of them. #4 is the clearest case. Pricing a re-entry
stop at `stop_reentry` and the K stepped bytes at `step_byte` changes the
admission boundary from "advance wins" to "cost wins". So the no-mover step
can unify the INPUTS and the TABLE but not the formula. Each formula switch
is counted before it is built (U2's oracle), never assumed neutral.

### 5.3 K105: the first behaviour change, and why the verdict alone does not fix it

K105's witness: `[a-y]\d{0,100}:` over ':'-dense digit text, ×1.537 against
main (3,871 → 5,949 µs). The prior gives ':' a mean gap far longer than
K = 101, and the text has one every ~3 bytes. Two readings:

- **Under the prior, any verdict admits it.** With ':' at the default
  prior's rate, `adv` is hundreds of bytes. The displaced `[a-y]` scan's
  `adv` is about 1.7 bytes. Even a generous `stop_reentry` (b2ledger's
  7.72 ns) is far below the hundreds of stepped bytes the jump saves. A
  PRIOR-ONLY verdict therefore says PAYS, as `req_landmark_admits` does. The
  loss lives entirely in the text contradicting the prior.
- **So K105's fix is the arm.** The verdict says PAYS with a `flip_ppm` near
  `1/(K + 1/m)`, so the sign flips at a density the text can show. The
  re-entry therefore starts `armed` (§4.2). A per-call counter disarms it
  after short gaps, which is the RETRY prototype's text (§4.2). This is
  [ADAPTIVE-ARM]'s first new member, and the arm text is shared with RETRY.

**Witness and controls.**
- **The cell:** hcolon_in (`[a-y]\d{0,100}:`, colon-dense, 1.12 MB) must
  come back inside the null band against main's pre-L1 text, counted by
  memchr calls and DFA steps (rlhbuild's instruments). The target is
  +200,451 → ≤ the band.
- **The control:** the same pattern on colon-SPARSE text must keep L1's
  re-entry win (the arm stays armed).
- **The prior-agreeing cells** (`loglines/ipv6`, `ipv4`, `sfx-64`) must not
  move past the floor. The arm's fixed per-call entry is a short-call
  absolute delta (D144 add. 1).

The gate is D77. K105's own trigger is a bench cell with a landmark denser
than its prior, and none exists yet. The hcolon_in witness is our own build's
regression ([REQ-HANDOFF-L1] introduced it), which is the evidence class
[START-DENSE] already accepted ("our own round-2 regressions"). Q4 asks
whether it suffices.

### 5.4 Controls, sabotage sketch

The controls are independent of the primitive they check (standing question
2):

- (a) **Byte identity at U0/U1** is `emit_sweep.py` against a pinned base
  binary. It does not share the new code, and it needs a REACH figure (not a
  pass count): the number of artifacts whose VERDICT members ran, read from
  the trace build's `CANDROW` counters.
- (b) **The unit check** `tests/core/scancost_check.c` takes its expectations
  from a Python reference over exact rationals (`fractions.Fraction`). It
  never shares the C arithmetic. Its cells are crafted at break-even and ±1
  ppm and at the saturation edges.
- (c) **The reader census** is a grep for `pcrec_find_byte_rate` /
  `pcrec_find_set_mass` / `pcrec_find_set_ppm` callers outside `findings.c`,
  `scancost.c` and the PICK readers. It is held against an allowlist IN the
  check, not in the table (the [AXES-DENY-MASK] lesson).
- (d) **The stop-count control** compares predicted `stop_ppm` (the prior)
  against counted stops (rlhtwin/lrmisc's counted-memchr drivers) on real
  subjects. It measures the independence model's error and the prior/text
  mismatch per member, which are the inputs [ADAPTIVE-ARM]'s trigger needs.
  Its population is counted and printed (K35).

Sabotage rows (S-ids unallocated: the manager assigns from a free range):

| plant | detector | reaches its site? |
|---|---|---|
| VERDICT's NONE answer swapped to COMPARE's `false` | emit_sweep `-e utf8` arm: #3/#4/#7 movers | yes, if the utf8 population contains a VERDICT ask (REACH figure) |
| G1 re-expressed through VERDICT (cardinality under NONE) | the same `-e utf8` arm: G1 elides utf8 pre-checks (F-2) | yes, on any utf8 artifact with a memchr scan and a one-byte pre-check |
| a VERDICT member reads the rate directly, bypassing `pcrec_scan_expect` | control (c) | yes, structurally |
| `pcrec_scan_verdict` compares by division (rounding) | control (b)'s break-even cells | yes, by construction of the cells |
| the CUBE_RUN product replaced by the minimum position mass (over-optimistic) | handoff witnesses in `run_prechecks.sh` §5.12m (`[a-y]\d{0,150}:` must stay un-re-entered) and control (d) | yes on run landmarks; the byte landmark is unaffected (state it) |
| CONTRACT plane read by a selection site (plane confusion) | a structural check: selection code references only the MEASURED accessor, the meter only CONTRACT | yes, structurally |
| a row's `meter` cell declared DELETES while its text adds a `RX_CHARGE` | [GIVEUP-DIFF]'s direction check; U4's planted ADDS row | the dynamic arm only where a budget ladder reaches the row |
| VF.gap read from the VL row (class swap) | the existing `[OPT-HYB-RESEED]` calibration check (reads the emitted literals per class), S372's shape | yes (S372 already reaches it) |

### 5.5 Remodel overlap (D153)

| row / lane | overlap | order |
|---|---|---|
| [TIE-ALIGN] (D151 add. 3 Q10: one landmark ranking read by the run reader, the run pin and `prefix_k`) | the PICK members #13-#15 and #7's offset ranking | TIE-ALIGN's ONE ranking is a PICK; the VERDICT reads it. Neither blocks the other's U0; U2 for #7 waits for TIE-ALIGN if both are scheduled |
| [ADAPTIVE-ARM] | §4.2, K105 | U5 is that row's first member |
| [START-DENSE] | #8, #9 and the hat entry term | START-DENSE's static half IS #8/#9's U2; its adaptive half is ADAPTIVE-ARM's. One row, not two (its own "never separate rows") |
| [EST-REGISTRY] (D141) | the table's home | Q2 |
| [MATCH-SPLIT] | §4.3 | a reader; no overlap in code |
| fixes.md F3 (fill `mf_site.cand_ppm_*` / `mf_term.ppm_*`, `memfn_sites.c:206,223-224,423`) | the same expectations, handed to the kit as FACTS (D157) | after U1: the filled values ARE `pcrec_scan_expect`'s `stop_ppm`, one derivation for pcrec's verdict and the kit's facts |
| [FINDINGS] B4 (run-rarity / bigram) | joint rates replace the independence product | Q5; the label in §2.2 is that replacement's trigger |

---

## 6. Standing questions (`docs/design/CLAUDE.md`)

**1. The measurement regime: RELEVANT, central.** Every MEASURED cell
carries its box, compiler, latency vs throughput and hit vs miss. Five
regime facts already bear on decisions:
- The DU cells are throughput figures over the bench's PERIODIC subjects.
  I-10's confound flattered branch costs ×1.64 on the DFA loop.
- The VL/VF/HY cells are Mac M1 scratch-tier hand twins.
- R4 compares a Zen 1-shaped rate to a Mac-shaped gap.
- `C_ENTER` is derived from a pre-premul figure (F-5).
- `stop_reentry`, the restart term the row exists to add, is UNMEASURED
  everywhere.

A different regime does flip decisions. `prefix_k` measured 11 of 1,352
selections moving between `C_ENTER` 12 and 20 cycles, and R4's framed gap
moves between 3 and 4. So: one reference box (Q3); each cell re-measured
there before its U3 commit; selection never re-measured per compiling box
(bit-reproducible integers in the tree); a cross-box cell flagged. The
CONTRACT plane is deliberately regime-free (worst-case, ruled).

**2. The independent control: RELEVANT.** §5.4 (a)-(d). None takes its
expectation from the primitive:
- byte identity is checked against a pinned base binary;
- the unit check's expectations are exact Python rationals;
- the reader census uses an allowlist in the check;
- predicted stops are compared against COUNTED stops on real subjects.

The population of each control is counted and printed (K35), and the REACH
figure of (a) is mandatory. A zero-mover result over artifacts where no
VERDICT member ran is not evidence. Each sabotage row names whether it reaches
its site ([MECH-REACH]).

**3. What moves when data is regenerated: RELEVANT, and it is the row's
purpose.**
- **A MEASURED cell re-measured** moves every selection that reads it. That
  means emitted bytes and stamps (`RX_VM_RESEED`, `RX_DFA_PREFILTER`, the
  offset stamps, `RX_REQ_HANDOFF`), so it is an abi event with readers
  found by grep, the byte-count reader class included, plus an identity
  re-pin. It is not a spec event unless a stamp's VALUE SET changes (D80).
- **The prior regenerated** (D160's authored utf8 prior, a bundle) moves
  every VERDICT, PICK and COMPARE member AT ONCE, through one accessor.
  That is the unification's payoff: one regeneration, one census, instead
  of twenty sites each re-checked.
- **A CONTRACT cell changing** changes caller-visible budget semantics. That
  is a spec event (`limits.md`, D80), an abi event (the stamped weights,
  §3.4) and a GIVEUP1 re-baseline.
- The table's own listing moves the `dumps` stream of `emit_sweep`.

---

## 7. Questions for Frank

Discussion, not menus. Each one gives the problem, the forces and my
leaning, with room to push back.

**Q1. The two kit-form constants: how should pcrec decide WHAT to scan
without pricing HOW?** `prefix_k` chooses the scan offset by comparing a
table walk at offset 0 (`C_BITMAP` 1.16 c/B) against a memchr at k* (0.055).
The form is the kit's (D146), but the choice of offset is pcrec's, and the
20× gap between the two forms is the whole reason a scan "must move" (its
§7.3 table). There are three ways through, with their forces:
- keep the two numbers as labelled KIT-ESTIMATE cells that only the
  what-to-scan planner may read;
- hand the offset choice to the kit as facts (the k-set walk, D157's shape),
  which then needs a return channel, because G1 and the reseed read which
  byte is scanned;
- assume a form-neutral per-byte cost, which the measurements refute.

My leaning is the first now and the second as the end state, filed as a kit
request with the cell that would trigger it (ci-moskva's 146,633 `D0` stops
is the nearest).

**Q2. Where should the table live?** D141 chartered [EST-REGISTRY]'s
`estimates.def` for every weight, bias, threshold and fitted constant, with
RULED/FITTED kinds and provenance. This table is a large part of that, and
its two planes map onto those kinds (MEASURED ≈ FITTED, CONTRACT ≈ RULED,
plus D149's DERIVED and UNMEASURED-DEFAULT). A separate `opcost.def` would
be a parallel registry, the shape the general-mechanisms rule forbids. The
cost is that this row then opens [EST-REGISTRY]'s step 2 early, in part: the
file is born with only this section, and the rest of D141's census follows
when that row is scheduled. `limits.def`'s "selection knee" rows stay where
they are, since those are caps and floors, not prices (F-6). My leaning is
`estimates.def`, born here, with this section first.

**Q3. Which box is the MEASURED plane's reference?** A selection must be
the same integers everywhere it is compiled, so the plane has ONE reference
box. Today's cells come from ubuntubudu (Zen 1) and the Mac (M1). The
candidates:
- the bench box ubuntubudu, where official verdicts are made (D144 add. 4),
  but which is reached only through slot requests;
- the dev box (Zen 4), which is fast and local, but whose verdicts are
  scratch tier.

A cell whose decision flips between boxes is itself information: it is an
[ADAPTIVE-ARM] candidate, or a regime finding. My leaning is ubuntubudu as
the reference, with each cell's calibration run as a bench slot, the dev box
for scratch, and the Mac cells re-measured before any U3 commit reads them.

**Q4. Should K105 be fixed now, through [ADAPTIVE-ARM], on our own
witness?** No prior-only verdict fixes K105 (§5.3): the loss is the text
contradicting the prior. The fix is an arm, which generalizes the RETRY
adaptive text that already ships. K105's filed trigger is a bench cell with
a landmark denser than its prior, and there is none yet. hcolon_in (×1.537)
is our own build's regression from [REQ-HANDOFF-L1], the same evidence class
[START-DENSE] accepts. Forces:
- Building now: it gets K105 off the books and makes the arm general before
  more members want it (5(a), START-DENSE).
- Waiting: it costs nothing until a real text contradicts the prior, and the
  arm adds fixed per-call text to every armed artifact (a short-call delta).

My leaning is to build it after U0-U1, as [ADAPTIVE-ARM]'s first member with
RETRY's rows folded in at zero movers first. Its acceptance would be
hcolon_in back inside the band and the prior-agreeing cells unmoved.

**Q5. Should the independence product stay until joint rates exist?** A
run's hit rate is computed as the product of its positions' masses (the
handoff admission and `prefix_k` both do this today). It is known to be wrong
in both directions: bignum predicted 13× and measured a wash, and
[OPT-REQPOS] measured joint rates that are not products. The alternative is
joint rates from a bigram bundle ([FINDINGS] B4), which the default prior
does not carry. My leaning is to keep the product, LABELLED in the
expectation struct, and treat B4's bigram reader as the replacement. D157's
revisit clause ("joint pair rates") is the same trigger: when a bundle serves
a joint rate, `pass_ppm` and the CUBE_RUN `stop_ppm` read it, and only those
two fields change.

**Answer-free choices taken here** (the same answers at equal measured cost,
memory `pcrec-answer-free-choices-are-mine`):
- one `adv` field instead of `run_len` + `stay_len`;
- cross-multiplication with saturation;
- centi-cycles as the plane's unit, which is `prefix_k`'s;
- `src/core/scancost.c` as the primitive's file;
- VERDICT's NONE answer as MASS's cardinality, which moves zero bytes (§1.3);
- the verdict returning `flip_ppm` rather than a three-valued ADAPTIVE today.

The last one stands because the arm's classification rule (§4.2) belongs to
[ADAPTIVE-ARM]. The verdict stays two-valued until that row builds the arm.

## 8. Findings for the manager

F-1 through F-6 (§1.2), plus three more:
- (a) `C_ENTER` and VF.gap are stale or chosen where the table derives
  different values (§3.2). These are the U3 movers.
- (b) The SUBSTITUTES meter class makes K102 visible at table-build time
  (§3.5).
- (c) [MATCH-SPLIT]'s END+FREE stage owes DR.walk_byte, which is
  UNMEASURED (§4.3).

None is filed here: plan.md and known_issues.md are the manager's.
