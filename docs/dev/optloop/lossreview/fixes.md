# [LOSS-REVIEW] phase 2: general fixes (lane lrfix, 2026-10-11; REVISION 2, lane lrrev)

Contract: `../lossreview_charter.md`, Phase 2. Frank: "look for general fixes,
assess them; PRIORITIZE FIXES TO EXISTING OPTS." Inputs: the three phase-1
attributions on main 28b3df8a (`dfa.md` 51.2 ms / 29 cells, `vm.md` 34.6 ms /
37 cells listed, 34 attributed, `misc.md` 8.56 ms / 25 cells), their twins, and
the plan rows they name.

**Evidence tier.** This lane is a desk read. No clock was read and nothing
was timed. Every ns figure is a bench set-grain number quoted from phase 1.
Every count is phase 1's, except the three no-clock counts revision 2 adds
(rev2/, marked `[r2 count]`). Every "expected gain" below is a prediction, and
each one names the owed twin that confirms or refutes it. The source sites
were read at main 28b3df8a.

## Revision 2 (lane lrrev, 2026-10-11)

Applies the r2 D6 panel's dispositions, every row ACCEPTED
(`../../reviews/2026-10-11-r2-lossreview-fixes.md`; critics' texts in
`../../reviews/2026-10-11-r2-lossreview-fixes/`). Each change is marked with
its finding id, like `[r2 C1]`.

| ids | where applied |
|---|---|
| R1 | §0 counts and the family claim, §1 table note, §2 candidate 1 (3.94M, 11 cells), cand 5 with/without C1c, §0 item 4 median-ratio sentence, §3 step numbering, §4 "7 of 88" |
| R2 | §4 states all three orderings and the false "every ordering" claim is withdrawn; weighting question is Q7 |
| R3 | §2.0 overlap table and a "remodel overlap (D153)" column in §0 |
| R4 | §5: Q1 dropped, Q2 answered by the attemptcensus, Q3/Q5 marked manager's, Q4 split, Q7 added |
| C1 | candidate 1 restated; Q3; the call-site census UNLOCK |
| C2 | DENSE-SKIP as a five-arm per-subject design (candidate 5(a) and §2.0); boundary-pair skip filed with its trigger count |
| C3 | candidate 3: HIT-RESTART + C3 gain UNKNOWN, K101 kept, one per-cell twin owed |
| C4, F7 | candidate 6 folded into [OPT-3-RUNEND]; `stay_len` = 1/(1-mass) |
| C5, C6 | candidate 5(a) reach; candidate 7 gain (~25 ms, derived) |
| F1 | the pricing split (§1 F1, candidate 5(a), §3 step 6) |
| F2, F5, F8 | §1 F1: [PRIOR-COST-UNIFY] generalizes `model_cost`; the eight added members; the signature sketch; the independence model labelled |
| F3 | candidates 3 and 5(b): the density facts; §3 |
| F4 | §1 F2 and candidates 3 and 5(b): ONE SWAR set/cube FIND row |
| F6 | candidate 5(a) as an adaptive arm; [ADAPTIVE-ARM] and [SIZE-KNEE] filed (plan.md) |
| instruments | `[r2 count]` results: ATTEMPT-SPLIT size (candidate 7, Q2), word-wait / stay counts (candidate 6), boundary-pair count (candidate 5(a)) |

## 0. Answers first

1. **Four cross-route families partition the 94.3 ms.** `[r2 R1]` The
   assignment is 100% by construction: every phase-1 cause sits in exactly one
   family (§1 table: 17.41 + 17.40 + 27.46 + 32.05 = 94.32). The earlier "about
   90%" was wrong, and so was the note that F1 and F2 overlap on DENSE-SKIP:
   DENSE-SKIP's 13.23 ms is counted ONCE, in F1; its "how" half (the loop form)
   has no separate ms. Each family already has dispersed members in the tree.
   §1 names them by file/function.
   - **F1, one priced decision ("is this scan worth it, and on which
     byte").** Every pick and every admission that reads the byte-rate prior,
     or should read it. It includes four start-skip admissions that carry NO
     density term today (the DFA hat, the VM hat, the plain byte-class rows,
     M2.1's stay threshold). Home: `[PRIOR-COST-UNIFY]` + `[START-DENSE]`.
     `[r2 F1]` pcrec prices its CONSUMER side (the per-stop re-entry, reseed or
     attempt cost) and states density as a FACT; the kit picks the per-hit form.
   - **F2, the scan kernel's FORM.** That is: memchr restart per hit, a 2-stream
     leapfrog, a SWAR pair filter, a SWAR set/cube skip, a range compare, or a
     table walk. Today the form is chosen by set CARDINALITY alone (one byte
     means memchr, otherwise a byte-at-a-time walk). Home: the memfn kit's FIND
     and FUNC-body row tables (D157: pcrec states the set and its rate, the
     kit picks the form).
   - **F3, the VM's per-attempt overhead.** The seam call through the PLT,
     trail undo, cursor-rung rewind, and start-independent re-attempts. Home:
     `emit_vm.c` and the encoding seam's existing `inline_def` column.
   - **F4, route shape.** The `^`-on-some-arms attempt route, cuts whose
     language is regular, and DFA steps over a literal the pre-check already
     found. Home: `[OPT-ATTEMPT-SPLIT]`, `pcrec_discharge_atomic`, and FINISH
     `verify-at`.
2. **A cross-route finding phase 1 did not join up: the `\b` WORD-WAIT
   state.** The DFA steps every byte of a word while it waits for a word
   boundary. This one state appears in four phase-1 causes on all three
   routes:
   - DENSE-SKIP (hex8, dbnames, json-constant);
   - C5 (ctx-*);
   - SEEDED-MACHINE START (aws, asr-b-ascii);
   - the listed hex32-id.

   The one existing opt that covers it is `[OPT-3-RUNEND]`(a), "the skip loop
   generalised to EVERY self-looping state", and M2.1's stay loop declines it
   only on a hand-set constant: `pick_skip_states` admits a state that stays
   put on at least 192 of 256 bytes (`src/gen/emit_dfa.c:4742`), and a word
   state stays put on 63. `[r2 C4]` `[OPT-3-RUNEND]`(a) is priced as a net LOSS on
   non-periodic text, so this is a candidate to MEASURE, not a fix to build
   (candidate 6). `[r2 count]` On the three DENSE-SKIP cells the word-wait
   state takes 66.5 / 78.9 / 73.8% of a plain walk's steps and a stay run there
   is 4.29 / 4.37 / 4.05 bytes (rev2/wordwait.txt).
3. **Top candidates, cheap-and-certain first** (§3 gives the order and its
   dependencies). The reach figures are phase-1 bench ns and are not additive
   across rows (§2.0 states the overlaps). `[r2 R3]` The last column is the
   D153 remodel overlap.

   | # | candidate | kind | reach (cells / phase-1 loss) | expected gain (basis) | decisive twin | remodel overlap (D153) |
   |---|---|---|---|---|---|---|
   | 1 | **Seam entries `inline_def`** (`<p>_span_match[_caseless]`, `<p>_back_step` stop being PLT calls) | fix-existing: an existing `PcrecEncEntry` column | C1's **11** cells (27.19 ms); lkb-* mostly C3 | **3.94M** seam calls (gcov-measured 2.49M on four cells; bak-py and bak-g-rel assumed at bak-1's value) at ~2-4 ns = **7.9-15.8 ms** (derived, Zen 1, UNMEASURED); per-cell bands in §2 | `modj-static-seam` (decisive), `bak2-static-noinline` (PLT only, new), `bak2-static-seam`, `bak1-static-seam` | its abi event orders against L1; the N7 loop is kit-rendered INSIDE the entry (PcrecEncSite, M7 pins, S513/S517) and `inline_def` moves its placement; check C17/C12 |
   | 2 | **D160 in the `fo` shape** (the authored utf8 prior) | fix-existing: data read by three existing pick sites | 6 U8-PICK cells (≤1.24 ms) | ≤1.17 ms modelled; counted stops ×4-×2,400 fewer; 0 of 62 other utf8 cells move >6% | T5 (`misc/`, `--analysis fo20`) | none (data; [PRIOR-COST-UNIFY] reads the same prior) |
   | 3 | **ONE SWAR set/cube FIND row + R4d's fused pair filter as a `fn_rows[]` BODY row** | fix-existing: new rows in two existing kit row tables | K101 2 cells (0.92 ms) claimable from R-1; HIT-RESTART 14 + C3 7 + stop cost 7 (7.84 ms) UNKNOWN | R-1 measured 1.95x / 2.7x on the **masked two-stream sparse** cells at SIMD-off; for the exact one-stream dense HIT-RESTART cells there is NO gain estimate (§2 candidate 3) | R-1 is the kit-side witness; owed per cell: `swar` in lit-cat's `fn-memchr` body | kit files with in-flight rows (`precheck.c`, `fn_rows[]` with R-15, R-16, slot21); 2:1 migration:SIMD split, R4d fits neither pool |
   | 4 | **[ART-TRAIL-ELIDE]'s frameless sub-case** (no dominance fact needed) | fix-existing: narrows a filed row to the half that needs no new analysis | 5 frameless C1 cells (17.74 ms): 22.7M trail-reset iterations | up to ~7-11 ms at 0.3-0.5 ns per iteration (derived, UNMEASURED) | `bak2-trail-free`, `bak2-both`, `bak1-both`, `phone-both` | none per the row; check [ART-POSS-ARMS]'s state; one VM abi event with candidate 1 |
   | 5 | **(a) A density-priced START admission as an ADAPTIVE ARM; (b) ONE SWAR set/cube FIND row** (`[START-DENSE]` widened to the VM hat, the DFA hat and the plain table-skip rows) | fix-existing: three predicates gain the MASS fact R4 reads; `pffind.c` gains one row | 5(a): bak-2's +17.5% (the one D77 witness), mod-j-uc and the bak-1 family (same VM-hat seek, not D77 witnesses), DFA hats 13.2 ms UNKNOWN; 5(b): C2 3 + set-skip 5 + PAIR-SKIP 2 + RANGE-SKIP 2 + ci-moskva cells | per sub-form, §2 candidate 5 | five-arm per-subject DENSE-SKIP design (§2.0 and candidate 5), `bak2-no-start-set`, `phone-no-start-set`, `quoted-seek`, T2/T6 | `[START-DENSE]` itself; [PRIOR-COST-UNIFY]; `memfn_sites.c` (density facts) after L1 |
   | 6 | **WORD-WAIT stay** — FOLDED INTO `[OPT-3-RUNEND]`(a) `[r2 C4]` | measure first; not a build candidate | C5 5 cells (0.26 ms vs jit) + whatever the stay twins show on DENSE-SKIP | `ctx64-stay22`: 85,988 → 6 forward steps, but on text a run is ~4-4.4 B, at or under break-even | `ctx64-stay22` (built); `hex8-stay`, `dbnames-stay`, `json-stay` owed | R4h STAY text (kit); `pick_skip_states` is an F1 member |
   | 7 | **[OPT-ATTEMPT-SPLIT]** (ratified, unbuilt) | new route composition | concat-sqli 28.87 ms (1 cell) | ~25 ms (36.47 → 11.2 ms at M5.b's 2.40 ns/B; derived, older pin) | `split` (#18) | `[ENG-ABS-CARET]` |

   `[OPT-ATTEMPT-SPLIT]` (28.9 ms, the largest single item) is candidate 7 and
   step 8 of §3 on purpose:
   - it is ONE pattern corpus-wide (bench O-82 A3);
   - it is a new route composition, not a widened opt;
   - its size question is now answered (`[r2 count]` 1.21x by the row's
     construction, 0.92x by the exact twin; candidate 7 and Q2), so what is left
     is Frank's default-or-`--tune` ruling (Q2) and the build.

   Its exact twin exists (`dfa/twins/mk_split.py`).
4. **Weighting (§4).** `[r2 R2]` The three orderings disagree and the old
   sentence "candidates 1, 3 and 5 rank high on every ordering" was false (§4
   restates it). By total ns the ranking is ATTEMPT-SHAPE > C1 > DENSE-SKIP.
   By cell count it is HIT-RESTART (14) > C1 (**11**) > the utf8 picks / C3 /
   stop cost (7 each). By median ratio it is C7 ×10.7 (jit) / ×39.8 (re2) >
   RUN-PICK ×9.5 (jit; ×1.33 re2) > ATTEMPT-STEP ×7.22 (jit) > ATTEMPT-SHAPE
   ×4.8 > S5 ×3.8 > U8-PICK ×2.9. The three disagree most on two items:
   - **C1** is 27 ms, but each cell is x1.27 and non-algorithmic (interp is
     6-8x slower than pcrec);
   - **the utf8 picks / set-skip / C3** total only 1.2-4 ms, but each cell is
     x2-x10.

   The weighting rule is Q7. The manager's lean: owner-actionable and certain
   first (a cheap confirmed step gate), then total ns, with cell count and
   worst ratio as tie-breaks.

## 1. Families (sibling-of-a-family lens)

Each family names its existing DISPERSED members (file:function, read at
main). Phase-1 causes map onto the families as follows:

| family | phase-1 causes (ms) | sum |
|---|---|---|
| F1 priced decision | RUN-PICK 1.76, U8-PICK 1.24, C7 0.06 + ATTEMPT-STEP 0.04, K105 (off-bench), ci-moskva 0.82, C5 0.26, plus DENSE-SKIP 13.23 (admission AND form, counted once) | 17.41 |
| F2 kernel form | HIT-RESTART 4.42, K101 0.92, C3 1.99, stop cost 1.43, PAIR-SKIP 1.36, set-skip 3.85, C2 2.58, RANGE-SKIP 0.44, C8 0.41 | 17.40 |
| F3 VM per-attempt | C1 27.19, C6 0.27 | 27.46 |
| F4 route shape | ATTEMPT-SHAPE 28.87, C4 1.83, DFA-steps-over-literal 0.57, REV-PASS 0.13, S5 0.65 | 32.05 |

`[r2 R1]` The four sums add to 94.32 ms: a partition of the 88 attributed cells
(29 DFA + 34 VM + 25 misc; the VM share's 37 includes three listed-only cells,
github-pat and level-context twice), not a 90% cover. C1c (bak-2's +17.5%
growth, 2.3 ms) is INSIDE C1's 27.19 ms and is also a customer of candidate
5(a); that is an overlap between candidates (§2.0), not between families.

### F1: one priced decision

**The family's question.** Every one of these sites asks the same thing:
the expected hit gap of a byte (or set, or run) under the prior, against the
work a scan saves per hit and costs per entry. `[PRIOR-COST-UNIFY]` was
filed with four members (G1, set-leads, R4, `req_landmark_admits`). Phase 1
found eight more siblings and the r2 panel found eight further ones, so the
family is twenty:

| member | file:function | what it reads today | what it should read |
|---|---|---|---|
| G1 dominance | `emit_dfa.c:7441 req_byte_dominated_by` | `pcrec_find_no_commoner` (rate) | (filed member) |
| set-leads | `findings.c:433 pcrec_find_pick` via the PRESENCE row | rate | (filed member) |
| R4 adaptive-dense | `emit_dfa.c:8531 cand_rs_dense_applies` | `pcrec_dfa_cand_ppm` × gap, with the gap from `vm_reseed_cal` (`emit_dfa.c:8532`, `ppm*gap > 1e6`) | (filed member). `[r2 F2]` NOT the only density-priced START decision: `prefix_k.c` `model_cost` prices one too (below) |
| handoff admission | `req_landmark_admits` (lane/rlhbuild, unmerged) | prior gap only; K105 | prior + a run-time arm (K105's fix shapes) |
| **run choice** | `src/facts/req.c:308 rn_better` | information (Σ popcount) alone; rate only for the member | rate × per-hit cost among runs that clear `PCREC_MIN_REQ_RUN_BITS` (RUN-PICK: FROM/`f` −27% hits) |
| **G2 one-attempt** | `emit_dfa.c:7400 req_route_one_attempt` | route only, no reach | the byte's reach (unbounded leading run ⇒ admit): C7 + ATTEMPT-STEP. `[r2 F5]` G2 is a ROUTE fact, not an F1 member; it appears here only because its fix needs the reach term |
| **prefix_k offset pick** | `src/opt/prefix_k.c:204` `base_scan = k0count == 1 ? C_MEMCHR : C_BITMAP`; `model_cost` `:114-123` | constants 6 / 116 (`:65-66`), `C_VERIFY` 250 / `C_ENTER` 2000 (`:67-68`), `C_MISPRED` 1500 (`:85`), `MATERIAL_NUM` 2 (`:99`, `:280`); NO per-stop scan-restart term | stops × per-stop cost against bytes × per-byte cost (ci-moskva: memchr `D0` 146,633 stops). `C_MEMCHR`/`C_BITMAP` are KIT-FORM costs left in pcrec after R4c |
| **VM hat admission** | `emit_dfa.c:7087 pf_vm_start_applies` | `\|S\| < 256` only (D149 UNMEASURED) | MASS: decline a dense S (bak-2's `\w` at 76%) |
| **DFA hat admission** | `emit_dfa.c:6930 pf_dfa_start_set` | T ⊊ E only | MASS + entry cost (DENSE-SKIP; K91) |
| **plain byte-class NEXT rows** | `cand_rows[]` `byte-class[-bounded]` | always applies over `none` | MASS (hex8 under `-fno-start-set` is just as short) |
| **M2.1 stay states** | `emit_dfa.c:4742 pick_skip_states` | stays on ≥ 192 bytes (count) | stays on bytes carrying ≥ X of the prior's MASS (C5; WORD-WAIT, §0 item 2) — see candidate 6 |
| utf8 rate NONE | `pcrec_find_byte_rate` under `-e utf8` | NONE ⇒ rightmost/leftmost rule | D160's authored prior (data, not code) |
| `[r2 F5]` run window start | `findings.c:586 run_window_start` | prior | (member) |
| `[r2 F5]` run pin | `kset.c:298-309 run_pin` | prior | (member) |
| `[r2 F5]` req pick / req byte | `req.c:646`, `req.c:689 req_pick`/`req_byte` | prior | (member) |
| `[r2 F5]` reseed calibration | `emit_vm.c:11033-11036 vm_reseed_cal` | measured per-class gap, read by R4 | moves into the primitive's consumer-cost table |
| `[r2 F5]` prefix_k singleton gate | `prefix_k.c:225` `count != 1` | cardinality | UNLOCK: a cube FIND row lifts it; trigger ci-moskva |
| `[r2 F5]` scan-chain floor | `limits.def:392 MIN_SCAN_CHAIN` (2) | constant | priced comparison |
| `[r2 F5]` find-floor | `limits.def:186 FIND_FLOOR_PPM` (2) | constant | priced comparison |
| `[r2 F5]` stay pass cap | `emit_dfa.c:4747` `pass < 4` | constant | priced comparison |

`deferpre`'s K = 64 is a ninth, UNLABELLED constant `[r2 F5]` (label it UNMEASURED DEFAULT, D149, if it is built).

Not members `[r2 F5]`: `PCREC_MAX_SCAN_EDGES`, `PCREC_VM_INLINE_CHAIN_MAX_BYTES`,
`VM_ISL_*` (they are size knees, not density prices: see the SIZE-KNEE family
below). Kit-side unmeasured defaults (the kit's own concern, D157): `vrun.c:56`,
`:133`, `:147`.

**The general form.** `[r2 F2]` The primitive already exists in embryo:
`prefix_k.c` `model_cost` prices a candidate scan against the alternative.
`[PRIOR-COST-UNIFY]` GENERALIZES `model_cost` rather than inventing a new
mechanism: it adds the per-stop scan-restart term `model_cost` lacks and
carries the consumer-side constants (`C_ENTER`, `C_VERIFY`, `C_MISPRED`,
`vm_reseed_cal`'s gap) in one table. `[r2 F1]` The split follows D146/D157:
- **pcrec** prices its CONSUMER side: what a stop costs it (re-entry, reseed,
  an attempt, a verify) and what a byte of plain stepping costs. It states the
  scanned set's density as a FACT (`pcrec_find_set_ppm`, `pcrec_dfa_cand_ppm`,
  `pcrec_find_run_rank`).
- **the kit** picks the per-hit FORM (memchr, pair, SWAR cube, range, table).
  A "price the form" decision in pcrec would be D146's rejected price market.

Pieces already in the tree:
- `pcrec_find_set_ppm` (MASS);
- `pcrec_dfa_cand_ppm` (the scanned set's mass);
- `pcrec_find_run_rank` (the per-position ranking already handed to the kit,
  RQ-2).

**A sketch of the signature** `[r2 F2]` (the family critic's proposal; a
sketch, not a design, and the independence model in it is LABELLED `[r2 F8]`:
a bignum prediction by that model was 13x and the measurement a wash):

```
PcrecScanQ    { set; bytes, mask, n, scan; verify[], nverify; span }
PcrecScanExp  { stop_ppm, pass_ppm (INDEPENDENCE MODEL), run_len, stay_len, rate_src }
pcrec_find_scan_expect(cx, q) -> PcrecScanExp
PcrecConsumerCost { step_byte, stop_reentry, verify, attempt }   // per route x program class
pcrec_scan_verdict(e, c, bar) -> PAYS | DECLINE | ADAPTIVE
```

`vm_reseed_cal`'s gap and `prefix_k`'s `C_ENTER`/`C_VERIFY`/`C_MISPRED` move
into `PcrecConsumerCost`. The sketch CANNOT express, and needs a ruling for:
- `prefix_k`'s `C_MEMCHR`/`C_BITMAP` baseline (`:204`) and G1's `memchr_form`
  density clause (`emit_dfa.c:7448`): they are kit-form costs. Leaning: move
  them into the kit's choice under D146; the alternative is labelled constants
  under a D146 guard. An open item for the [PRIOR-COST-UNIFY] design.
- K105: the verdict has only an INITIAL arm state (see ADAPTIVE-ARM below).
- G2: a route fact.

**Two halves with different timing.**
- The START-admission half (VM hat, DFA hat, byte-class rows, stay) can read
  `pcrec_dfa_cand_ppm` / `pcrec_find_set_ppm` today with no new primitive.
  This is how R4 already works.
- The PICK half (run choice, offset pick, G2 reach, K105) needs the per-hit
  term, so it is `[PRIOR-COST-UNIFY]` proper.

Recommendation (Q4, split in §5): the VM-hat part of the START half need not
serialize behind `[REQ-HANDOFF-L1]`; the DFA-hat part is not yet supported.

**Constants that are this family's symptoms** (memory
pcrec-suspect-tuning-constants), each a hand-set cut-over standing where a
priced comparison belongs:
- `pick_skip_states`' 191;
- `C_MEMCHR`/`C_BITMAP` 6 / 116 (kit-form costs, see above);
- `pf_vm_start_applies`' 256;
- `pf_vm_emit_first_class`'s "|S| = 1 → memchr cut-over is not taken"
  (D149).

**Two more families the panel found** `[r2 F6]` (filed in plan.md, NOT
scheduled, no build):
- **[ADAPTIVE-ARM]**: the RETRY adaptive rows, K105 (the handoff admission),
  and candidate 5(a)'s dense decline are one pattern: a runtime-adaptive arm
  whose INITIAL state (armed / unarmed / off) the F1 primitive sets. A
  compile-time decline repeats hcolon_in's x1.5. Trigger: `bak-2` vs
  `phone-no-start-set` under prior-contradicting text.
- **[SIZE-KNEE] / MATERIALITY**: `SIZE_TERM_THRESHOLD`/`SIZE_TERM_BAR`,
  `INLINE_CHAIN`, `ISL`, `SCAN_EDGES`, clskit `PLACE` `atom_min_sites` (11),
  `FAST_TIER`; `MATERIAL_NUM`, `SIZE_TERM_BAR` 75%, the ISL factor 2. File,
  do not build. Home: [OPT-DIAL]'s lambda and the `tune.c` cells.

### F2: the kernel's FORM, chosen by set shape and density

**The family's question.** Given the set a scan stops on, which loop? Today
the choice is set CARDINALITY alone:
- `memfn/src/pffind.c`'s header says "the one-byte/table split is the
  SITE's ..., not a priced choice";
- the ofsskip FUNC body has two rows (`memfn/src/ofsskip.c:206 fn_rows[]`:
  `fn-pair` for a cube pair, `fn-memchr` otherwise).

`[r2 F4]` The FIND rows are ALREADY one table: `memfn/src/pffind.c`, reached
through `PcrecFind` (`.site`/`.offset`/`.floor`/`.holdback`). Integration is
per site (the handoff, the `n-1` holdback, the `DELEG_LOOP` budget, the entry
regime), so D63 holds: the derivation is shared and the loop integration is
per engine. The retry reaches PF only through `prefn`.

Dispersed members:

| site | file | forms today | phase-1 loss of the missing form |
|---|---|---|---|
| PF (DFA prefilter FIND, DFA hat, VM hat seek) | `memfn/src/pffind.c` rows `pf_memchr[_bounded]`, `pf_walk[_bounded]` | memchr (\|S\| = 1), byte table walk (\|S\| > 1) | set-skip 3.85 (cube SWAR; rust-only, a SIMD baseline `[r2 R2]`), PAIR-SKIP 1.36 (memchr2/SWAR pair), RANGE-SKIP 0.44 (range), C2 2.58 (the VM hat has the TABLE only, even at \|S\| = 1: `emit_dfa.c:7111`) |
| OFS FUNC body | `memfn/src/ofsskip.c:206 fn_rows[]` (`:350` per the panel) | `fn-pair` (cube pair, 2 memchr streams), `fn-memchr` | HIT-RESTART 4.42 (lit-cat family, keyword-prefix-order, grp-noncap), C3 1.99, stop cost 1.43 |
| PRE (run pre-check composite) | `memfn/src/precheck.c` | 1 or 2 memchr streams + verify | K101 0.92 (`fresh = 1` restart), RUN-PICK's per-hit 14.6 ns |
| scan EDGE / VM span test | `src/gen/clskit.c ROWS` at `CLSS_SCAN` / `CLSS_VM` | range, fold (cube), kit, table: **already a set-shape table** | (none; this is the model) |

**The general form.** Phase 1 shows the scan-edge's class-form table already
chooses a membership TEST by set shape: one interval → range, one cube →
fold, else kit/table (`clskit.c`, D139). The FIND/FUNC sites need the same
thing one level up, for a LOOP form:

| set shape | FIND form |
|---|---|
| 1 byte | memchr |
| 2 bytes | memchr2-leapfrog or SWAR pair |
| ≤ 3 cube terms | SWAR cube skip (`pcrec_cube_of` already proves the terms) |
| 1 interval | range loop |
| a run with a pair | the SWAR pair filter + verify (R4d) |
| otherwise | table walk |

`[r2 F4]` Two different things are called a "pair" and must not be conflated:
- a **SET pair** (|S| = 2: one byte position, two members), candidate 5(b);
- a **POSITION pair** (two positions of a run, ANDed at a fixed distance),
  R4d, candidate 3.

They share only the SWAR word-classify, which is [POS-PARALLEL]'s stage 1.
The kit request is therefore written as ONE SWAR set/cube FIND row in
`pffind.c`; the OFS BODY and PRE rows COMPOSE it. Putting SWAR bodies in three
tables (`precheck.c`, `ofsskip.c` `fn_rows[]`, a new row beside `pf_walk`) would
be a parallel mechanism.

Under D157 pcrec's half is only facts: the set (already handed over as
`PCREC_FIND_START_SET`), the rate (MASS, RQ-2's ranking), and the set's
cube/interval decomposition, which the kit can derive itself from the set.
`[r2 F3]` The density channel EXISTS and is empty on both sides:
`mf_term.ppm_lo/hi` (`memfn.h:272`) and `mf_site.cand_ppm_lo/hi` (`:337`) are
written as "unknown" by pcrec (`memfn_sites.c:206`, `:223-224`, `:423`) and read
by nothing in the kit. Filling them from `pcrec_find_set_ppm` /
`pcrec_dfa_cand_ppm` at the PF / OFS / PRE / VM-hat sites is the pcrec half of
candidates 3 and 5(b): facts only, no movers, no abi, scheduled AFTER the L1
merge (the `memfn_sites.c` overlap). **No pcrec decision moves**: this is new
rows in existing kit row tables, D146/D147.

**[POS-PARALLEL] as the general home.** A SWAR cube skip IS stage-1
classification over an 8-byte window. The pair filter IS two class vectors
ANDed at a fixed distance. So F2's scalar rows are the window-sized case of
[POS-PARALLEL]'s stage 1, and its hybrid consumer is "attempt-loop skip by
bit reads and ctz". **Recommendation: do not route these fixes through
[POS-PARALLEL].** It is a design study ("NEEDS THOUGHT"). F2's rows are kit
forms with measured triggers (R-1) and identity-checked twins (T2/T6).
Record the scalar rows as [POS-PARALLEL]'s stage-1 witnesses, so the study
starts from measured forms. `[r2 C2]` DENSE-SKIP's 13.2 ms is NOT a
[POS-PARALLEL] customer: its gap is not the data-dependent chain (§2 candidate 5).

**Unlock** (for the panel's general-form lens): once the kit holds a cube or
pair FIND row, the same row also serves:
- the VM hat seek (C2);
- the hybrid RETRY's step-through-set (C4 retry half, `possq-stepset`: VM
  attempts 1,295,798 → 95,957);
- `[REQ-HANDOFF-L1]`'s two-landmark window scan (Frank's 2026-10-11
  refinement: the window scan IS an offset-set pick bounded by the
  landmark);
- `[r2 F5]` `prefix_k`'s singleton gate (`prefix_k.c:225`), which the cube row
  lifts; trigger ci-moskva.

Trigger for each: a cell where that site scans a 2-4 member set.

### F3: VM per-attempt overhead

Dispersed members:
- **The encoding seam's entries**, `src/enc/enc_byte.c` (`$_span_match`,
  `$_span_match_caseless`, `$_back_step` are exported and therefore called
  through the PLT under `-fPIC`). **The tree already states the rule and
  already has the mechanism.** `src/enc/enc.h`'s `inline_def` column reads:
  "An exported entry cannot be inlined into a `-fPIC` build (interposable),
  which is the whole reason a per-character helper is not exported." The
  three compare/back-step entries are per-attempt helpers that never got
  the column.
- **The trail**: `RX_SET`/`RX_TRAIL` and `rx_reset_for_next_attempt`
  (`emit_vm.c`). Filed as [ART-TRAIL-ELIDE].
- **The cursor rung's retreat**: `emit_vm.c:4773 vm_cursor_rep` (C6, one
  frame per retreated position).
- **The attempt loop's advance**: `emit_vm.c vm_emit_search_body` (C1d,
  start-independent failures; a new mechanism).
- `[r2 C1]` **The framed `rx_match_anchored` call per attempt**: mod-j-uc
  (entry shape `plain`) calls it out of line 1,017,146 times.

The [CC-DIFF] STEP 1 `always_inline` work was the same lever for the entry
chain's statics. The seam entries were outside it because they are exported.
That is the sibling this lens exists to catch.

**UNLOCK** `[r2 C1]`: a **call-site census of every per-attempt call
boundary** in the attempt loops: the seam entries, the framed
`rx_match_anchored`, and the `rx_search_run` split. Each is an out-of-line
call paid once per attempt; the census counts them by emitted shape over the
corpus and the bench, so the next boundary is found by count rather than by
a cell. Compile-only; filed, not run.

### F4: route shape

Dispersed members:
- **`^` on some arms:** `emit_dfa.c:13-17` route rule. Two filed
  constructions: [OPT-ATTEMPT-SPLIT] and [ENG-ABS-CARET].
- **Cuts whose language is regular:** `src/opt/atomic.c
  pcrec_discharge_atomic`. Its header names `(?>a|ab)c` as the VM-forced
  example.
- **The DFA route steps a literal the pre-check located:** FINISH
  `verify-at` exists on the VM (`pcrec_lit_run`, S2a), and the DFA route
  has no consumer. Litrun is synthetic.
- **The reverse pass re-reads a landing-exact match:** [START-LANDING-EXC],
  filed, trigger unmet (0.13 ms).

## 2. Candidates, FIX-EXISTING first

Fields per candidate: the site it changes; what changes; reach; expected
gain; risk; remodel overlap; D77 status; owed twins.

### 2.0 Overlaps between candidates `[r2 R3]`

The reach figures in §0 and §2 are not additive. The overlaps, stated:

| overlap | ms | candidates | note |
|---|---|---|---|
| DENSE-SKIP | 13.23 | 5(a) and 6 (now [OPT-3-RUNEND]) | two explanations of one gap; the five-arm design (candidate 5) times them together |
| concat-sqli residual after the split | not quantified | 5 and 6, behind 7 | the residual is the first set's word class |
| PAIR-SKIP | 1.36 | 5(b) and 3 ("in part") | a SET pair is 5(b), a POSITION pair is 3 (§1 F2) |
| ci-moskva | 0.82 | 5 (cube row) and 8 (the prefix_k pick) | 8 needs 5's cube row first |
| RUN-PICK | 1.76 | 3 and 8 | pick (8) vs per-hit form (3) |
| qnt-poss-quest (C4, part of 1.83) | — | 9 and 5's retry half | moot if the language rewrite lands |
| the frameless C1 pool | 17.74 | 1, 4, C1c | candidate 1's upper bound 3.21M calls × 4 ns = 12.8 ms; candidate 4's upper bound 11.4 ms; C1c's 2.3 ms: the sum 26.5 ms exceeds the pool, so they cannot all be won |
| C1c | 2.3 | C1 (27.19) and 5(a) | inside C1's total |
| mod-j-uc | 9.45 | 1 reaches 1.5-2.9 ms (727,369 calls × 2-4 ns) | the remaining 6.5-8 ms has NO named candidate; 5(a)'s VM-hat dense decline reaches an unquantified part (1,337,133 seek iterations), and the out-of-line `rx_match_anchored` per attempt (1,017,146 calls) is what the F3 call-site census would count |

### 1. Seam entries become `inline_def`

- **Site:** `src/enc/enc_byte.c` and `enc_utf8.c` entry rows for
  `span_match`, `span_match_caseless` and `back_step`; the column is at
  `src/enc/enc.h:132`.
- **What changes:** these rows gain `inline_def = true`. Their definitions
  become `static inline`, emitted ahead of the VM body by
  `pcrec_enc_emit_inline_defs` (the same path `$_decode` already takes).
  The `.h` declarations go. `match_api.md §3¶2` already says "They are not
  caller entries; their signatures are not part of this contract", so the
  spec hunk is one sentence (§3¶2 stops saying "export and declare").
  - `[r2 C1]` Q3 (manager's, §5): either **drop the export** (the above) or
    **keep an exported one-line wrapper** and call the static body from the VM
    (lrvm's proposal). The three checks `tests/backrefs/fold_agreement_check.c`,
    `fold_agreement_utf8_check.c` and `fold_agreement_ucp_check.c` call
    `rx_span_match_caseless` (`run_backref_diff.sh:655`, `:683`, `:706`), so
    dropping the export means **re-homing those three checks in the same
    change**. The earlier text said "a reader of the symbol may turn up"; they
    already have.
- **Reach:**
  - Bench: C1's **11** cells (6 throughput + 5 short), 27.19 ms. lkb-pos/neg
    (6 `back_step` sites each) are mostly C3, so the gain there is minor.
  - Corpus: every backreference-, variable- and lookbehind-bearing artifact.
    This is countable as artifacts whose mask carries `PCREC_ENCE_SPAN*` or
    `BACK_STEP`. Not counted here: the box is held.
- **Expected gain (restated `[r2 C1]`):**
  - Counts: **3.94M** PLT seam calls on the six throughput cells (gcov-measured
    `span_match_calls`: mod-j-uc 727,369; bak-1 726,049; bak-2 794,481; phone
    240,718, summing to 2.49M; bak-py and bak-g-rel are not gcov'd and are
    taken at bak-1's value, 1.452M). The earlier 4.7M was phone's VM-hat seek
    iteration count (4,681,579), a conflation.
  - Assumed cost per call: an indirect PLT `jmp` plus call/ret plus, where it
    exists, the lost specialization of a constant-length compare, ~2-4 ns on
    Zen 1 (derived, UNMEASURED). At 2-4 ns the total is **7.9-15.8 ms**,
    capped by the loss.
  - **Per-cell bands** (the share of each cell's own ns the same 2-4 ns buys):
    bak-2 10-21%, bak-1 9-18%, mod-j-uc 5.7-11.4%, phone 5.7-11.3%.
  - **The effect splits in two** (asm, `-fPIC -S`):
    - *specialization* exists only on the 1-char-capture cells. bak-2: 12 PLT
      calls → 0, the reflen folds to 1 (`cmpb`), `rx_search` 192 → 157 insns;
      phone 222 → 176 insns. Those two cells are 7.26 ms.
    - *call overhead only* elsewhere. bak-1 has a runtime length: the loop is
      inlined, not specialized (158 → 179 insns). mod-j-uc and the bak-1 family
      are 19.93 ms.
  - mod-j-uc (9.45 ms, the largest C1 cell, FRAMED) is reached by this
    candidate only for its seam calls (1.5-2.9 ms). It also pays an
    out-of-line `rx_match_anchored` per attempt (entry shape `plain`; 1,017,146
    calls), 1,017,095 frame pops and 1,337,133 VM-hat seek iterations, so
    candidate 5(a) reaches it too. `[r2 C1]` The earlier inference "if
    `modj-static-seam` is null, C1 is the trail" is DROPPED: it does not
    follow, because mod-j-uc has at least three other per-attempt costs.
  - Static evidence: bak-2 `.text` 4,161 → 3,156 B.
- **Risk:**
  - Answers: none. The same function is called from the same site.
  - abi: an event. Emitted text moves on every artifact carrying the
    entries; readers are found by grep (D94).
  - Checks:
    - S109 and S133 count CALLS of the seam (per site), so an inline call
      keeps them green.
    - The [M5-SEAM] codegen fixtures assert declarations per row; those
      move.
    - `tests/memfn/pins/n7_target/` pins the N7 span loop's text inside the
      entry. The loop is unchanged; only the linkage and the declaration
      move.
  - Size: none (it shrinks).
- **Remodel overlap:** `[r2 R3]` not "none". The abi event orders against the
  L1 merge. The N7 loop is kit-rendered INSIDE the entry (`PcrecEncSite`, the M7
  pins, S513/S517), and `inline_def` moves where that text is placed, so
  confirm C17 and C12 (the site manifest and the form ceilings) still read it.
  The entry's signature is the backend's (D58 addendum 2).
- **D77:** met: a measured per-call PLT site on 6 bench cells, 27 ms.
- **Twins:** `modj-static-seam` (the decisive one, since the framed cell
  has no C1b confound), `bak2-static-seam`, `bak1-static-seam`, and, new
  `[r2 C1]`, **`bak2-static-noinline`**: `twin.py`'s `static_seam` is
  `always_inline`, so it buys BOTH the PLT removal and the specialization; the
  `static noinline` arm on bak-2 buys the PLT removal alone and separates the
  two. **Refute bar `[r2 C1]`:** a twin is read against its cell's band above
  (the 2% bar contradicted the 5.7-11.4% modj prediction). The result REFUTES
  the attribution only if it lands below the band's LOW end for that cell, on
  a bench-class box. The twins' box is the 7700X (`taskset -c 14`), and 2-4 ns
  is a Zen 1 figure, so a 7700X result is scaled before it is compared with a
  band (or the twin is run on the bench box).

### 2. D160 in the `fo` shape (the authored utf8 prior)

- **Site:** the shipped default analysis (`src/findings/default.rxt`)
  gains the utf8 `freq` block in D160 addendum 1's ordered shape. Readers,
  unchanged in code:
  - `rn_scan_index` (the run's scan member);
  - `pcrec_find_pick` (set-leads);
  - `req_byte_dominated_by` (G1);
  - prefix_k's offset choice.
- **Reach:** 6 utf8 cells to their peer (sharp-s, offset-at-head, 1ch-4b,
  qnt-bounded-4b, mixed-ascii, ci-ascii-control). Every `-e utf8` artifact
  whose pick reads a rate.
- **Expected gain:** ≤1.17 ms modelled (`misc.md` §3.1: counted stops
  83,154 → 2,089; 16,728 → 7; 14,582 → 2,638; 12,027 → 2,638; 3,727 → 7;
  25,844 → 9,463). 0 of the other 62 utf8 cells move more than 6%
  (ci-strasse +6%).
- **Risk:**
  - The SHAPE is the risk. The `fu` reading regresses lit-cyr-run x24, and
    5% non-ASCII mass regresses CJK x2.5. The acceptance floor is
    `misc.md` §3.1's 76-cell stops table (D160 addendum 1).
  - abi: an event (the FINDINGS digest and emitted picks).
  - Answers: identical (picks only).
- **Remodel overlap:** `[PRIOR-COST-UNIFY]` reads the same prior. This is
  data, so it does not conflict.
- **D77:** met (sharp-s x10.5).
- **Twins:** T5 (`misc/` `mk.py ... --analysis fo20`). The counted-stops
  half is already done; the timing is owed.

### 3. ONE SWAR set/cube FIND row, and R4d's fused pair filter as a BODY row

- **Site:** `[r2 F4]` the memfn kit, as a request the manager files:
  - ONE SWAR set/cube FIND row in `memfn/src/pffind.c` (the existing FIND
    table). The OFS BODY and PRE rows COMPOSE it rather than carrying SWAR
    bodies of their own;
  - R4d's fused pair-filter scan+verify (the R-1 `swar` variant, integration.md
    §22) as a BODY row in `memfn/src/ofsskip.c:206 fn_rows[]` above
    `fn-pair`/`fn-memchr`, and in the PRE composite (`memfn/src/precheck.c`).

  pcrec's half is only the facts it already states (the run, its mask, RQ-2's
  ranking) plus the density facts `[r2 F3]`: `mf_site.cand_ppm_lo/hi` and
  `mf_term.ppm_lo/hi`, written from `pcrec_find_set_ppm` /
  `pcrec_dfa_cand_ppm` at the OFS / PRE sites (facts only, no movers, no abi;
  scheduled AFTER the L1 merge because of the `memfn_sites.c` overlap). The
  manager files the R-n.
- **Reach `[r2 C3]`:** split by what the evidence supports.

  | cause | cells | phase-1 loss | gain claim |
  |---|---|---|---|
  | K101 | 2 (mod-i/-r) | 0.92 ms | CLAIMABLE: R-1's mod-i is the same cell family (2.7x on the sweep) |
  | HIT-RESTART | 14 (lit-cat family run-pinned, keyword-prefix-order and grp-noncap offset-set, stack-frame, asr-*, cls-fold-pair) | 4.42 ms | **UNKNOWN** |
  | C3 | 7 (lkb-*, lka-*, slack) | 1.99 ms | **UNKNOWN** |
  | stop cost | 7 (lit-l8, alt-foo-tails, nfc-pair half, counted-3b, nearmiss, 1ch-3b, cyr-run) | 1.43 ms (1.14 of it from the synthetic litrun cells lit-l8 and alt-foo-tails) | **UNKNOWN** |

  In part it also reaches union-select (RUN-PICK, 1.76 ms vs jit),
  PAIR-SKIP's `{c,d}` as a two-byte filter, and C8 (grp-cap family, DENSE's VM
  twin). The 17 listed SCAN-SIMD cells have the same per-hit shape at sparse
  density; their scalar share is reached too.
- **Expected gain `[r2 C3]`:** R-1 (Zen 1, gcc 15.2) measured 1.95x on the
  union-select gate (364,078 / 187,022 ns) and 2.7x on the mod-i sweep
  (724,503 / 267,480 ns). That baseline is the glibc **two-stream, masked
  case-pair** `fn-pair` (integration.md:1921-1925) on **sparse** text
  (mod-i: 6,030 hits per MiB). The HIT-RESTART cells are the other shape: ONE
  stream of an EXACT (unmasked) run, `fn-memchr`, on **dense** text
  (lit-cat ~31K hits per MiB), and integration.md:1938-1941 itself excludes
  the exact unmasked window and the OFS run-pinned site. Only union-select is
  both dense and masked. So for HIT-RESTART, C3 and stop cost the gain is
  **UNKNOWN**; the earlier "50-80% of these cells' time is memchr calls" is
  CIRCULAR (it divides the cell's ns by its memchr calls, so the 10-17 ns
  includes ~32 B of scan per hit, the verify, the post-hit DFA and the
  per-match `rx_search`: lit-cat 663,117 ns / 42,663 calls = 15.5 ns), and
  `misc`'s independent fit prices a stop at 8.7 ns, about 56% on lit-cat.
  - **Near-noise cells named as such.** 9 of the 14 HIT-RESTART cells sit at
    x1.26-1.29 vs jit with jit's measured p5-p95 drift at 0.924-1.052. The
    manager's call (f) in `judgement_gapreport_2026-10-11.md` left the DENSE
    group (≤ x1.68) unfiled as near-noise on cross-window data. R4d is not
    exempt on that ground; the reason to keep it is that it is kit-owned and
    its trigger is MET at SIMD-off (R-1), for the masked sparse shape.
  - **Caveat:** R-1's gate-mode row shows swar SLOWER when the first hit is
    near (mod-i gate 1m, hit at 404: 75.75 vs 73.35 ns).
- **Risk:**
  - Answers: identity by construction; the kit's own checks.
  - pcrec: an abi event at the kit merge (a kit byte move is a pcrec abi
    event in the same commit, D147).
  - D149: `swar`'s 2x unroll is a labelled unmeasured default.
  - `[r2 R4]` "Q1 (is SWAR scalar?)" is DROPPED: it is ruled (D122 addendum 3,
    "SWAR is fine", 2026-09-25; D147 addendum 6 / Q50, integration.md §R4.3.1:
    the scalar layer includes SWAR and libc).
- **Remodel overlap:** `[r2 R3]` kit files with in-flight rows: `precheck.c`,
  `fn_rows[]` with R-15, R-16 and slot21 in flight; under the 2:1
  migration:SIMD split R4d fits neither pool. `[REQ-HANDOFF-L1]` touches
  stack-frame's site (not a mover per its census) and the PRE re-entry (R-15).
- **D77:** MET at SIMD-off for the K101 shape (R-1); NOT MET for HIT-RESTART /
  C3 / stop cost until the per-cell twin below is timed.
- **Twins:** `[r2 C3]` the R-1 probe (`docs/design/memfn/probes/twins/`) is the
  kit-side witness. **Owed, one per-cell twin before the BODY row claims
  HIT-RESTART or C3:** `tb_r4b.c`'s `swar` placed in lit-cat's `fn-memchr`
  body (exact run L = 3, one stream). A bench alpha on the HIT-RESTART cells is
  the landing gate.

### 4. [ART-TRAIL-ELIDE], frameless sub-case first

- **Site:** `emit_vm.c` `RX_SET` emission and `rx_reset_for_next_attempt`
  on a FRAMELESS program (`!Vm.has_push`, the bool `_VM_FRAMELESS`
  stamps).
- **What changes:**
  - An untrailed slot write.
  - The reset rewrites the program's own written slots to `PCREC_UNSET`
    (every attempt starts with every slot unset).
  - The row's dominance fact is NOT needed, because the trail's only reader
    in a frameless program is that reset (`vm.md` §4.1 item 2).
- **Reach:**
  - 5 frameless C1 cells (bak-2, bak-1, bak-py, bak-g-rel, phone): 17.74 ms.
    Trail-reset iterations: 6.79M + 3 × 4.04M + 3.81M = 22.7M.
  - Population (from the row): 27 bench / 623 corpus frameless artifacts
    with `RX_SET`.
  - mod-j-uc is FRAMED, so not reached.
  - `[r2 R3]` overlaps candidate 1 and C1c inside this pool (§2.0).
- **Expected gain:** up to ~7-11 ms at 0.3-0.5 ns per reset iteration
  (derived, UNMEASURED). It composes with candidate 1: bak-2 `.text`
  4,161 → 2,036 B for the pair, but the gains are not additive (§2.0).
- **Risk:**
  - The trail FRAMES give-up disappears on these artifacts (a one-way
    change). That needs the limits.md §3.2 / §5 hunk the row already
    names.
  - abi: an event.
  - Answers: identical, since a frameless program never resumes.
- **Remodel overlap:** none (the row says so). The row was sequenced after
  [ART-POSS-ARMS]; check that row's state at scheduling.
- **D77:** met by the counts. The row's own STEP 0 (the dominance census)
  is needed only for the framed half.
- **Twins:** `bak2-trail-free` (isolated), `bak2-both`, `bak1-both`,
  `phone-both`.

### 5. A density-priced START admission as an adaptive arm, plus the set/cube FIND row

This candidate is two halves of one table: F1's "whether" and F2's "how".

- **(a) Admission, pcrec side `[r2 F1, F6]`.** Three predicates read the
  density FACT (`pcrec_dfa_cand_ppm` / `pcrec_find_set_ppm`, the MASS R4 reads),
  against pcrec's CONSUMER-side per-entry cost:
  - `pf_vm_start_applies` (`emit_dfa.c:7087`);
  - `pf_dfa_start_set` (`:6930`);
  - the plain `byte-class[-bounded]` NEXT rows.

  The per-entry cost comes from the twins, never a guess (D149). The decision
  is an **adaptive arm** (armed / unarmed / off) whose INITIAL state the F1
  primitive sets; a bare compile-time decline repeats hcolon_in's x1.5 on text
  that contradicts the prior ([ADAPTIVE-ARM]). pcrec does NOT price the kit's
  per-hit form here (D146). This is `[START-DENSE]` (K90 + K91 + K83 +
  [OPT-HYB-RESEED-POLICY], gated on C7, which is done) widened from "the hat's
  disarm" to every table-skip NEXT row and the VM hat.
- **(b) Form, kit side `[r2 F4]`.** ONE SWAR set/cube FIND row in `pffind.c`
  (candidate 3's request; a SET pair |S| = 2 and ≤ 3 cube terms are the same
  row), plus a range row if the range cells justify it. The VM hat drops its
  "TABLE form at any \|S\|" rule (`pf_vm_emit_first_class`, Q-R5). At \|S\| = 1
  it takes `pf_memchr`.
- **Reach and expected gain per sub-form:**

  | sub-form | cells | phase-1 loss | expected (basis) |
  |---|---|---|---|
  | VM hat \|S\| ≤ 2 → memchr/pair | quoted-delim, bak-k-named, balanced-parens | 2.58 ms | 4.6M / 1.3M / 1.3M table-walk iterations → memchr; most of the loss (jit's edge is a SIMD first-unit search, and glibc memchr is that) |
  | VM hat dense decline `[r2 C5]` | bak-2 (+17.5% since 10-05 ≈ 2.3 ms of pcrec time, **the one D77 witness**), plus mod-j-uc, bak-1, bak-py and bak-g-rel (1,337,133 seek iterations each; the bak-1 family's +3-4% is INSIDE the null band, +8.77% per `cycle2_batch2_reading.md`, so it is not a D77 witness) | bak-2 2.3 ms; the others overlap C1 | the grower reverses; `phone-palindrome-6` must not regress (10-member digit set, low density) |
  | cube-SWAR skip | ci-sigma, ci-kelvin, ci-turkish-i, alt-distinct-lead, ci-strasse | 3.85 ms (**rust-only, a SIMD baseline** `[r2 R2]`) | scalar-skip loads ÷ 8 ⇒ up to ~3 ms (misc S2; fit price 0.44 ns/B, UNMEASURED) |
  | memchr2 / pair | alt-two, alt-nested | 1.36 ms | near O-51's 8% crossover; one bounded attempt (pcrec-one-pass-loss-chasing) |
  | range | high-byte-run, utf8-lead-no-cont | 0.44 ms | small; fold into the same row set |
  | prefix_k re-price | ci-moskva | 0.82 ms | possible only once a cube row exists to price |
  | DFA admission | hex8, dbnames, json-constant | 13.2 ms | UNKNOWN until the five-arm design below is timed |

  `[r2 R1]` The 5(a)+5(b) reach is **22.28 ms WITHOUT C1c and 24.6 ms with it**;
  C1c's 2.3 ms is already inside candidate 1's 27.19 ms.

- **DENSE-SKIP: the five-arm per-subject design `[r2 C2]`.** The three
  explanations of the 13.2 ms are:
  - (i) the skip's ENTRY cost (the loop entry, the seed reload, the
    data-dependent exit, every ~7 bytes): `plainloop` wins;
  - (ii) the word-wait state's per-byte table walk: a stay loop wins;
  - (iii) neither: OPT-3's latency chain on every step, which only a
    second-stream / mask form addresses ([POS-PARALLEL]).

  **(iii) is ruled out as the GAP.** re2's lazy DFA pays the same chain at
  1.62-1.67 ns/B, and pcrec's premultiplied plain loop is ~1.80 ns/B
  (`opt3_dfa_scan_measurement.md:343`; `waf_attribution.md` §3.4); the gap of
  1.2-1.6 ns/B is per-step dispatch, entry and skip. That retires the
  [POS-PARALLEL] route for this 13.2 ms, which [POS-PARALLEL] loses as a
  customer.

  **(i) vs (ii) are NOT separable on the set totals, and the earlier "evidence
  favours (i)" (dfa.md §2.2) is unsupported.** The three cells' totals are
  collinear: entries per step 0.196 / 0.173 / 0.215 and steps + skipped
  ≈ 1.000 per byte. A three-parameter solve gives a NEGATIVE entry cost
  (−5.3 ns); a two-parameter fit (4.07 ns per step + 0.86 ns per skipped byte)
  fits all three cells within 0.05 ns/B with no entry term at all.
  json-constant goes AGAINST (i): the O-46 narrowed-first-set twin runs
  1.52-1.66 vs 3.09 ns/B, the hat's landing moved 3.05 → 1.84 ns/B
  (`waf_attribution.md:321`, `dfa/cells.tsv`), and its residual (x1.14, 1.03 ms)
  is near the drift band. Only hex8 (mean skip 1.75 B, 7.29 ms) is plausibly (i).

  **The decisive design is per SUBJECT, five arms, per cell** (hex8, dbnames,
  json-constant):

  | arm | what | built? |
  |---|---|---|
  | (A) base | the shipped artifact | yes |
  | (B) `plainloop` | the skip block removed, plain stepping | yes (dfa `plainloop` ×3) |
  | (C) `-fno-start-set` | the hat denied | yes (×3) |
  | (D) stay | a stay loop on the word-wait state (hex8: state 3, `next_state` row 0,3,3) | NO (owed: `hex8-stay`, `dbnames-stay`, `json-stay`) |
  | (E) boundary-pair skip | `!(T[s[p]] & NW[s[p-1]])`, below | NO, and gated on the count below |

  Counters per subject: entries, skipped bytes, word-wait steps vs other
  steps, stay exits. A per-subject regression of ns on those counters
  separates the per-step coefficient (a) from the per-entry one (b).
  Predictions: (i) ⇒ B < A with the gain ∝ entries, and D ≥ A; (ii) ⇒ D < A by
  `ww_steps × (a − stay) − runs × mispredict`, and B ≈ A. `[r2 count]` the
  word-wait counts the regression needs are in rev2/wordwait.txt.

  **The general form, filed `[r2 C2]`: a boundary-pair skip.** A `\b`-led
  start is a two-byte CLASS PAIR (the previous byte non-word, the current byte
  in T). The skip stops only where `!(T[s[p]] & NW[s[p-1]])` is false: two
  independent loads, no data-dependent chain, no mid-word entries and no
  word-wait steps there. It is R4d's pair filter generalized from bytes at a
  fixed distance to CLASSES at distance 1, and [OPT-FIRSTSET]'s re-seed as a
  predicate. **Trigger (no clock):** count, on the subjects, the boundary-pair
  stops against today's skip-block entries; build the twin if the ratio is
  below ~0.3. `[r2 count]` (rev2/pairskip.txt; whole-subject positions over
  the 11 capability throughput subjects, 4,681,573 bytes; entries reproduce
  dfa.md §2.2's 0.146 / 0.095 / 0.067 per byte):

  | cell | skip entries today | boundary-pair stops | ratio | trigger (< ~0.3) |
  |---|---|---|---|---|
  | hex8-bounded | 682,437 (0.146/B) | 267,010 (0.0570/B) | **0.391** | NOT met |
  | dbnames | 445,565 (0.095/B) | 258,878 (0.0553/B) | 0.581 | NOT met |
  | json-constant | 311,524 (0.067/B) | 60,655 (0.0130/B) | **0.195** | met |

  So on hex8, the cell the critic named, the ratio is 0.39: above the ~0.3
  line, near it. Only json-constant clears it, and json-constant is the cell
  where evidence already goes against (i). Whether 0.39 is close enough on
  hex8 to build arm (E) is the manager's call.

  **Manager, 2026-10-11 (after the panel):** arm (E) IS built for the step-0 slot.
  **Frank's extension (session 108), the general form:** `\b` is a CLASS PAIR AT AN OFFSET, so it belongs in the
  offset-set row's vocabulary (`kset_walk`: test the rarest offset, verify the rest) as a new TERM KIND beside byte sets.
  On a FIXED-WIDTH pattern both boundaries sit at known offsets: `\b[0-9a-f]{8}\b` needs NW at p-1 and at p+8 (a word of
  exactly 8 bytes), which rejects nearly every word start before any DFA work. Customers: a leading `\b`, a trailing `\b` at
  a fixed offset, and a one-character lookbehind (`(?<=x)` = a pair at offset -1; `lookaround_census.md` shape (a), ~35% of the
  lookaround-only VM population). It supersedes the stay loop for `\b`-led patterns (no mid-word entry, so no word-wait state).
  TRIGGER: arm (E)'s timing on hex8/json-constant; then a no-clock count of both-end pair stops on hex8's subjects.

- **Risk:**
  - Answers: identical (skip forms only).
  - abi: events on both sides.
  - The dense-decline threshold must come from the twins (D149). A wrong
    one regresses the sparse controls (the phone cell; startset.md §7's
    guard cells).
- **Remodel overlap:** `[r2 R3]`
  - `[START-DENSE]` itself.
  - The PF text is memfn's (R4g), so the FIND rows are kit rows.
  - `[PRIOR-COST-UNIFY]` later absorbs the MASS read; the density facts
    (`cand_ppm`) wait for the L1 merge.
- **D77:**
  - The VM-hat half is met: measured round-2 regressions are named in the
    START-DENSE row (quoted-delim +0.84 ns/B), and bak-2 is the one
    grower.
  - The cube-SWAR half is met by loss (3.85 ms, rust-only). Its speed is owed.
  - The DFA-hat half is NOT met until the five-arm design is timed.
- **Twins:**
  - `bak2-no-start-set`, `phone-no-start-set` (the control);
  - `quoted-seek`, `quoted-seek-seam`, `parens-seek`, `kname-seek`;
  - misc T2 and T6 ×3;
  - `hiskip`;
  - the five arms above per subject: dfa `plainloop` ×3, `-fno-start-set` ×3,
    the stay twins ×3 (owed), the pair-skip twin (owed, gated).

### 6. WORD-WAIT: folded into [OPT-3-RUNEND](a) `[r2 C4, F7]`

The earlier candidate 6 ("price M2.1's stay threshold by mass") is the plan
row **[OPT-3-RUNEND](a)**, "the skip loop generalised to EVERY self-looping
state (scan the run with the state's stay-set, transition once at the
boundary)". It is folded into that row; this section keeps the evidence and the
mover set.

- **The row already prices it as a loss.** `[OPT-3-RUNEND](a)` is "~4 c/B on
  t-a after STEP 2 MINUS one data-dependent exit branch per run (every 2-6
  bytes, ~19 c per mispredict) = a net LOSS on non-periodic text unless
  predicted" (`opt3_dfa_scan_measurement.md` §7). The [ARTREV] pilot timed it
  as I13: NOISE on level-context fail/syslog, +6% on the hit-dense subject
  (`report_pilot.md:79`, `:155`; [ART-CTX-TRIO] holds it). The first revision
  cited none of RUNEND, I13 or O-46.
- **The break-even is the stay RUN length.** `[r2 F7]` The same primitive
  gives `stay_len` = 1/(1 − mass): about 5 B at 0.8 mass, which is the
  break-even of ~4 c/B saved against ~19 c per exit. ctx-*'s win comes from
  its random-letters subject (86 of 106 KB in one state), not from text.
- **`[r2 count]` the three DENSE-SKIP cells** (rev2/wordwait.txt; the
  unmodified `vm/stayprobe.py` plus `wordwait.py`, 4,681,573 plain-walk steps
  over the 11 subjects):

  | cell | word-wait state | steps in it | share | stay runs | mean run |
  |---|---|---|---|---|---|
  | hex8-bounded | 3 | 3,111,185 | 66.5% | 586,111 | 4.29 B |
  | json-constant | 11 | 3,695,589 | 78.9% | 679,884 | 4.37 B |
  | dbnames | 29 | 3,453,240 | 73.8% | 674,042 | 4.05 B |

  All three states self-loop on 63 bytes (the word class) and none has a stay
  table. The mean run is 4.05-4.37 B, **under** the ~5 B break-even: by the
  row's own pricing a stay twin is more likely to lose than to win on this
  text. That is a derived reading, NOT a timing; the stay twins decide it.
- **The mover set includes shipped stays.** dbnames ships
  `rx_forward_stay95` and `rx_forward_stay110` (192-byte NON-word waits, low
  mass). A mass threshold would DECLINE them, so re-pricing `pick_skip_states`
  moves shipped artifacts in the other direction. `[r2 count]` On the 11
  subjects those two states are never visited in a plain walk (0 steps), so
  their cost is invisible here; the mover set is still named. The earlier gcov
  counts (2.56M / 1.46M / 3.23M forward steps on dbnames / json-constant /
  hex32-id) are TOTAL forward steps, not word-wait steps, and are not cited
  as word-wait counts.
- **Reach, cut `[r2 C4]`:** C5's 5 cells (0.26 ms vs jit, 0.59 ms vs rust) plus
  whatever the stay twins show on DENSE-SKIP's three cells and aws (~0.25 ms).
  The earlier "up to ~14 ms" is withdrawn as a gain claim; the 13.2 ms stays
  candidate 5(a)'s five-arm question.
- **Expected gain:** UNCERTAIN.
  - On ctx-*'s random-letter subject the run is the whole subject
    (`ctx64-stay22`: 85,988 → 6 steps).
  - On text the stay loop removes the data-dependent table-load chain but not
    the per-word exit mispredict, which is what makes the DFA-hat skip lose.
  - M2.10's regression was a REVERSE-machine skip. The forward machine is
    untested (`pick_skip_states`' own comment).
- **Risk:** answers identical (the `state_acc_varies` and `scan_span`
  exclusions stay); abi: an event; a stay loop on short runs can lose like the
  hat does.
- **Remodel overlap:** R4h STAY text (kit); `pick_skip_states` is an F1
  member; `[START-DENSE]` (the same regime from the other side).
- **D77:** `[OPT-3-RUNEND]`'s subject is O-82 A1 (the non-periodic 1 MiB
  subject). Met on ctx-*; NOT met on DENSE-SKIP until the stay twins exist.
- **Twins:** `ctx64-stay22` (built); **owed:** `hex8-stay`, `dbnames-stay`,
  `json-stay`, each timed against `plainloop` and base inside the five-arm
  design.
- **Unlock:** if the stay twin shows the per-word exit dominates, the next
  rung is the boundary-pair skip of candidate 5 (it removes the word-wait
  steps rather than speeding them).

### 7. [OPT-ATTEMPT-SPLIT] (ratified, unbuilt)

- **Site:** the route rule at `emit_dfa.c:13-17`; the BOUND/LOCATE rows.
  The construction:
  - ONE attempt of the original machine at `search_from`;
  - then ENG_UNANCH built without the `^` arms (leftmost-first by
    construction).

  The exact form is phase 1's twin (`dfa/twins/mk_split.py` +
  `split_rx.c`): the `^` arm is last, has the lowest priority, and can
  start only at 0.
- **Reach:**
  - concat-sqli: 28.87 ms, re2 x4.80, algorithmic.
  - Corpus: **one witness** (bench O-82 A3: the only non-top-level `^`
    pattern corpus-wide).
- **Expected gain `[r2 C6]`:** concat-sqli is 7.79 ns/B (36.47 ms over
  4.68 MB). At waf M5.b's 2.40 ns/B (an OLDER pin, so this is DERIVED) the cell
  is 11.2 ms, a gain of ~25 ms (the first revision said ~20), leaving ~3.6 ms
  against re2. After the split the residual is the first set's word class,
  which candidates 5 and 6 address. They compose.
- **Size `[r2 count]` (the attemptcensus size number, compile-only,
  rev2/split_size.txt):** the original `wild-waf-crs-942360-concat-sqli` is
  389,031 B of C and 196,839 B of `.o` (`gcc -O2 -c`; text 46,879 + data
  149,960), `RX_DFA_SCAN "attempt"`, `start_max = subject_length`, and it
  already draws pcrec's `--warn-emit-bytes=250000` warning (395,789 B emitted).

  | construction | `.c` B | x orig | `.o` B | x orig |
  |---|---|---|---|---|
  | original (today) | 389,031 | 1.000 | 196,839 | 1.000 |
  | the four `^`-free arms `u` (unanchored: `byte-class-bounded`, premultiplied) | 149,274 | | 42,123 | |
  | the `^` arm `a` (attempt, `start_max = 0`: fully `^`-anchored) | 282,118 | | 138,959 | |
  | **the row's construction** (original + `u`) | 538,305 | **1.384** | 238,962 | **1.214** |
  | **the exact twin** (`a` + `u`) | 431,392 | **1.109** | 181,082 | **0.920** |

  So the split costs 1.21x of the object by the row's own construction and
  LESS than today by the exact twin's, because the anchored `^` arm alone is a
  smaller machine than the whole `attempt` artifact. Both are under the
  parkmeas decision rule's 1.5x line (`parkmeas_report.md` A3: "population ~
  the witness AND size ≥ 1.5x = a `--tune` position"). The population half is
  the bench's O-82 A3 finding (a single witness), cited, NOT re-run: the
  corpus sweep of `RX_DFA_SCAN "attempt"` with `start_max != 0` is not run
  (the heavy chain holds the box).
- **Risk:**
  - Size: bounded by the table above for the witness; every other artifact is
    unaffected.
  - Answers: exact by construction (87/87 subjects).
  - The predicate is false for every other artifact, so the five
    fully-anchored artifacts stay byte-identical (the row's
    do-not-regress list).
  - abi: an event.
- **Remodel overlap:** `[ENG-ABS-CARET]`. Split versus absorb is decided on
  size first, and the size is now measured.
- **D77:** met (28.9 ms, algorithmic).
- **Twins:** `split` (#18) is the acceptance witness.
- **Q2** carries the default-or-`--tune` question, now with the size number.

### 8. [PRIOR-COST-UNIFY]'s pick half, after [REQ-HANDOFF-L1]

These members need the per-hit term; the primitive is §1 F1's generalization
of `model_cost`:

| member | change | reach | gain | twins |
|---|---|---|---|---|
| run choice (`rn_better`) | rate × per-hit cost among runs over the floor | union-select | −27% hits by prior (FROM/`f`); 1.76 ms vs jit / 0.49 vs re2 is the ceiling | `ciprecheck select c` (control), `from f`, `from m`, `union u` |
| G2 reach-aware (`req_route_one_attempt`) | admit where the byte sits behind an unbounded leading run (the landmark-offset fact `[REQ-HANDOFF-L1]` introduces) | moment-iso8601, email-owasp | 0.10 ms (re2 x39.8: algorithmic) | `moment-precheck`, `precheck`, `deferpre` |
| K105 handoff admission | the initial state of an [ADAPTIVE-ARM] (the RETRY rows' shape) | hcolon_in (off-bench, x1.5) | the x1.5 | T3 (`twin_hcolon.sh`) |
| prefix_k cost | stops-priced; the per-stop scan-restart term `model_cost` lacks | ci-moskva | 0.82 ms | none (needs candidate 5's cube row first) |

`deferpre`'s K = 64 is an unmeasured default; label it if built. **Remodel
overlap:** total. It is queued behind `[REQ-HANDOFF-L1]` (Frank,
2026-10-11).

### 9. Smaller fix-existing items (one bounded effort each, memory pcrec-one-pass-loss-chasing)

- **C4: cut-language rewrite as a widening of `pcrec_discharge_atomic`**
  (`src/opt/atomic.c`).
  - Today the discharge deletes a cut that is a no-op. The widening first
    deletes a branch the cut makes DEAD: in `(?>X|Y)` where every string
    of Y has a prefix in X's language and X is tried first, Y never runs.
  - Then the existing discharge removes the now no-op cut, and the pattern
    leaves the VM (`(?>a|ab)c` → `ac`; `a?+a` → `aa` by the
    possessive-optional sibling).
  - Reach: grp-atomic-alt, qnt-poss-quest (1.83 ms). Population not
    counted.
  - Twins: `atomicalt-ac`, `possq-aa` (pattern ceilings).
  - Risk: answer-changing if the deadness proof is wrong. It needs the
    discharge's own differential (tests/atomic_groups).
  - The retry half (`possq-stepset`) rides candidate 5's FIND rows
    (overlap, §2.0).
- **C6: cursor-rung follow-byte seek** (`vm_cursor_rep`, `emit_vm.c:4773`).
  - pwd-strength-chain, 0.27 ms. `pwd-rewind`: 81,922 frames → 0.
  - It needs a give-up statement (STEPS can only become an answer).
  - A census of cursor rungs whose follow starts with a one-byte test is
    the STEP 0.
- **S8: lit-1ch-3b's second memchr per match** (G1 / handoff). 18 µs. Fold
  into `[REQ-HANDOFF-L1]`'s integration.
- **S6: `end_bytes` + RECOVER guard** (tail-dotstar, K103/K104). T1 is
  identity-checked. +1.25 ns per subject; K103's 10% trigger is unmet.
  Stays filed.
- **REV-PASS:** `[START-LANDING-EXC]` stays filed (0.134 ms against its own
  1 ms trigger).

### 10. New mechanisms (each states why no existing opt widens to it)

- **C1d: start-independent failure skip.**
  - Mechanism: when an attempt's first atom is a possessive class run and
    the failing test reads only positions at or past the run's end, every
    start inside the run fails identically. Skip to the run's end.
  - Reach: bak-1 family, 291,097 of 1,017,146 attempts.
  - Why not a widening: no existing opt reasons about failure-position
    independence. The nearest relatives miss it:
    - the VM hat and MRL prune by START byte and REMAINING length;
    - possessify removes retreats WITHIN an attempt, not ACROSS attempts.
  - PCRE2 lacks it too, so it would be a lead over jit.
  - D77: its own census is owed. Not proposed for this round.
- **S4: exact-literal FINISH on the DFA route.**
  - Mechanism: `pcrec_lit_run` consumed by `verify-at`.
  - Reach: litrun l16/l31/l40, 0.57 ms, synthetic set (`sellit_read.md`).
  - Why not a widening: FINISH `verify-at` exists, but it takes an anchored
    DFA, not a literal compare.
  - Low priority. T4 (forced VM against auto) decides first.

## 3. Proposed order (cheap-and-certain first)

`[r2 R1]` Step numbers are this table's own; "candidate N" is §2's number.
Candidate 7 (ATTEMPT-SPLIT) is therefore step 8, after the twin slot at step 0.

| step | item | size | depends on | can run beside |
|---|---|---|---|---|
| 0 | **Quiet slot: time the owed twins in this priority**: `modj-static-seam`, `bak2-static-noinline` (new), `bak2-static-seam`, `bak2-both`, `bak2-trail-free`, the DENSE-SKIP five arms per subject (hex8 / dbnames / json-constant: `plainloop`, `-fno-start-set`, the stay twins; the pair-skip twin only if the manager builds it), lit-cat's `swar` BODY twin, `bak2-no-start-set` + `phone-no-start-set`, `quoted-seek`, T2/T6, `ctx64-stay22`, `split`, T5 | one slot | box | — |
| 1 | Candidate 1: seam `inline_def` | S (a column flip + spec sentence + re-pins; + re-home three fold checks if the export is dropped) | modj twin at or above its band's low end (§2) | 2, 3 |
| 2 | Candidate 2: D160 `fo` prior | S (data) + abi | T5 | 1, 3 |
| 3 | Candidate 3: file the R-n for ONE SWAR set/cube FIND row + the R4d BODY/PRE rows; claim K101 only | kit lane | the lit-cat `swar` twin before HIT-RESTART / C3 are claimed | 1, 2 |
| 4 | Candidate 4: trail-free frameless | M | after 1 (one VM abi event each, or one combined) | 5 |
| 5 | Candidate 5(b): the kit FIND rows (memchr at the VM hat \|S\| = 1, the set/cube row, range) | kit lane | R4d shares the SWAR layer (one request, not three) | 4 |
| 6 | The density facts: fill `mf_site.cand_ppm_lo/hi` and `mf_term.ppm_lo/hi` from the existing primitives (the pcrec half of 3 and 5(b)) | S (facts only, no movers, no abi) | AFTER the L1 merge (`memfn_sites.c`) | — |
| 7 | Candidate 5(a): the START admission as an adaptive arm, on the density fact and pcrec's consumer-side cost | M | the step-0 twins (the threshold); the VM-hat half only until the five-arm design is timed | after 5(b) lands its forms |
| 8 | Candidate 6 → [OPT-3-RUNEND](a): the stay twins decide; a build only if they win | S-M | the three owed stay twins | 7 |
| 9 | Candidate 7: ATTEMPT-SPLIT | M-L | Q2 (default or `--tune`); size now measured | any |
| 10 | Candidate 8: the PRIOR-COST-UNIFY pick half | M | `[REQ-HANDOFF-L1]` merged | — |
| 11 | Candidate 9's one-pass items | S each | — | any |

Dependencies, in short:
- Step 7 reads per-entry costs measured on the forms step 5 ships.
- Step 8 and step 7 are two explanations for the same 13.2 ms, so their
  twins are timed together (the five-arm design).
- Step 10 waits on the L1 merge (Frank's queue); so does step 6.
- `[r2 R1]` An earlier draft's table said ATTEMPT-SPLIT ranks 7th and was
  step 8; both now read "candidate 7, step 9".

## 4. Weighting caveat: ns total against cell count against ratio

Totals are dominated by a few cells:
- concat-sqli alone is 28.9 of 94.3 ms (31%);
- C1's six throughput cells are 27.2 ms (29%);
- together they are 59% of all loss on 7 of **88** attributed cells.

`[r2 R1]` The 88 attributed cells are 29 DFA + 34 VM + 25 misc (the earlier "91"
counted three listed-only cells).

| cause | total ms | cells | median ratio (vs the trailing peer) | a scalar engine also wins? |
|---|---|---|---|---|
| ATTEMPT-SHAPE | 28.87 | 1 | 4.80 (re2) | yes |
| C1 BACKREF-ATTEMPT | 27.19 | **11** | 1.27 | no (interp 6-8x slower) |
| DENSE-SKIP | 13.23 | 3 | 1.65 | yes (re2) |
| HIT-RESTART | 4.42 | 14 | 1.44 | no |
| set-skip (cube) | 3.85 | 5 | 2.37 | rust only (SIMD) |
| C2 VM-hat table | 2.58 | 3 | 2.14 | no |
| C3 one-byte restart | 1.99 | 7 | 2.25 | no |
| C4 VM-forced regular | 1.83 | 2 | 2.34 | no |
| RUN-PICK | 1.76 | 1 | 9.49 (jit) / 1.33 (re2) | yes (re2) |
| stop cost (misc) | 1.43 | 7 | 1.85 | rust/re2 |
| PAIR-SKIP | 1.36 | 2 | 1.58 | no |
| U8-PICK (utf8-blind) | 1.24 | 7 | 2.86 | rust/re2 |
| K101 | 0.92 | 2 | 1.81 | no |
| ci-moskva | 0.82 | 1 | 2.70 | rust |
| S5 seeded start | 0.65 | 2 | ~3.8 | rust |
| C6, C5, C8, RANGE-SKIP, REV-PASS, DFA-literal, C7/ATTEMPT-STEP | 0.04-0.57 each | 1-5 | 1.16-1.97 (C7: x10.7 jit / x39.8 re2; ATTEMPT-STEP x7.22 jit) | C7 yes |

`[r2 R2]` **Baselines are mixed.** The pooled 94.3 ms mixes comparators: 17 of
`misc`'s 25 cells (6.28 ms, 73% of its 8.56) have rust as the comparator;
`dfa.md` lists its rust-only (9 cells, 4.06 ms) and SCAN-SIMD (17 cells,
7.42 ms) causes apart as not attributed; candidate 5's cube-SWAR 3.85 ms is
rust-only (a SIMD baseline), so it sits inside the ~22 ms reach under a rule
`dfa.md` and `vm.md` did not apply. The last column above tags it per cause;
a reader who wants only D119-eligible loss drops the "rust only" and
"rust/re2"-only rows and reads the rest. The D119-eligible subtotal is not
recomputed here.

**The reach table, by candidate** `[r2 R2]` (candidate 5 without C1c; candidate
3 = HIT-RESTART + K101 + C3 + stop cost; candidate 6 at its pre-fold reach):

| cand | reach ms | cells | max ratio | median ratio |
|---|---|---|---|---|
| 7 ATTEMPT-SPLIT | 28.87 | 1 | 4.80 | 4.80 |
| 1 seam inline | 27.19 | 11 | 1.59 | 1.27 |
| 5 admission + FIND | 22.28 | 17 | 7.35 | 1.80 |
| 4 trail-free | 17.74 | 9 | 1.55 | 1.27 |
| 6 stay (pre-fold) | 13.74 | 9 | 2.59 | 1.60 |
| 3 SWAR + R4d | 8.76 | 30 | 8.20 (2.98 excluding synthetic litrun) | 1.45 |
| 8 PRIOR-COST-UNIFY pick half | 2.68 | 4 | 10.7 (39.8 vs re2) | ~8.4 |
| 9 small items | 2.10 | 4 | 2.74 | 1.96 |
| 2 D160 | 1.17 | 6 | 10.55 | 2.54 |

**The three orderings, stated** `[r2 R2]` (the proposed §3 order is 1, 2, 3, 4,
5, 6, 7, 8, 9):
- **(a) total ns:** 7, 1, 5, 4, 6, 3, 8, 9, 2.
- **(b) cell count:** 3 (30), 5 (17), 1 (11), 4 and 6 (9 each), 2 (6), 8 and 9
  (4 each), 7 (1).
- **(c) worst ratio:** by max, 8, 2, 3, 5, 7, 9, 6, 1, 4; by median, 8, 7, 2, 9,
  5, 6, 3, then 1 and 4 tied.

**Where the orderings disagree, and what it does to the candidates:**

- **Total ns** puts ATTEMPT-SPLIT and C1 first. ATTEMPT-SPLIT is one cell
  of one pattern corpus-wide, so its 28.9 ms is a single bench cell's
  weight. C1 is non-algorithmic: jit wins by code generation.
- **Cell count** puts candidate 3 first (30 cells), then 5 (17), then 1 (11).
  HIT-RESTART alone is 14 cells, but each is about x1.29 and 9 of them are
  near the jit drift band.
- **Median ratio** puts the small-total cells first: candidate 8 (RUN-PICK
  x9.5, C7 x10-40), then 7, 2, 9, 5. These are the cells a reader of the bench
  sees as "badly behind", and their totals are small because the throughput
  subjects are small or the sets are synthetic.
- **The old claim is withdrawn** `[r2 R2]`: "candidates 1, 3 and 5 rank high on
  every ordering" is FALSE for 1 and 3. Candidate 1 is lowest or near-lowest on
  either ratio view (x1.27 median, non-algorithmic). Candidate 3 is 6th on ns
  and 7th on median ratio. Only candidate 5 stays in the top five throughout,
  and 59% of its reach is DENSE-SKIP, which has no timing yet. Candidate 1 can
  still go first as the cheap, certain step gated by the modj twin: that is a
  COST argument, not a ranking-robustness one.
  - ATTEMPT-SPLIT survives only total ns (and median ratio).
  - D160 survives ratio and cell count, not ns.
- **Moves against the proposed order:** candidate 7 goes from 8th to 1st on ns
  and 2nd on median ratio (last on cells); candidate 2 from 2nd to last on ns;
  candidate 8 from 8th to 1st on ratio; candidate 1 is last on ratio.
- **Two adjustments the rank critic adds** `[r2 R2]`: report ms AND ns/byte
  (set-grain ns scales with subject bytes: the subjects are ~1 MiB); handle
  ATTEMPT-SPLIT's single-witness status with a FLAG, not a down-weight (it is
  algorithmic, ratified, and its exact twin exists). Cells are not independent
  either: the 88 attributed cells are syntax 37 (42%, 35.0 ms), utf8 19,
  capability 16, bounded 8, litrun 6, loglines 2; the 14 HIT-RESTART cells are
  about four artifact shapes, and 19 of candidate 3's 30 cells are `syntax`.
- **The rule** is Q7. The panel's recommendation: weight by total expected
  RECOVERABLE ns, with cell count and ratio as gates and tie-breaks. The
  manager's lean: owner-actionable and certain first (a cheap confirmed step
  gate), then total ns, with cell count and worst ratio as tie-breaks. The two
  agree on the second clause and differ on whether "certain" comes first.
- **Bench caveats carried from the gap report:**
  - peers are cross-window (`--peer-group`);
  - capability moved from 0.1 to 0.2, which changed its throughput
    subjects, so moment-iso8601 and email-owasp exist as losses only on
    0.2's hazard subjects;
  - litrun is synthetic.

## 5. Questions (plain, each with a recommendation)

1. **(dropped `[r2 R4]`)** "Is portable-C SWAR part of the scalar layer?" is
   RULED: D122 addendum 3 ("SWAR is fine", 2026-09-25) and D147 addendum 6
   (Q50, integration.md §R4.3.1: the scalar layer is SWAR plus libc). No
   question; "Q1 gates it" is removed from candidate 3 and §3.
2. **ATTEMPT-SPLIT: default or a `--tune` position?** (Frank's.) It is one
   witness corpus-wide and 28.9 ms on the bench.
   - `[r2 count]` The size question is ANSWERED: 1.21x of the object by the
     row's construction, 0.92x by the exact twin (candidate 7).
   - **Recommendation: default-on, behind a size decline.** The predicate
     is false for every other artifact, so the size cost lands only on the
     one pattern that has the shape, and it is under the 1.5x line.
     Decline where the split artifact would cross the size-ladder threshold.
   - `[r2 R4]` The build is not blocked on this ruling's timing: the earlier
     "ready the moment Frank rules on Q2" misstated the blocker, which was the
     census, now run.
3. **Seam entries: drop the export (`inline_def`, a §3¶2 spec sentence), or
   keep an exported wrapper?** (**Manager's call**, `[r2 R4]`: match_api.md §3¶2
   already says they are not caller entries, so it is an abi ritual plus a
   reader grep.)
   - **Drop the export:** the spec already says they are not caller entries,
     and `inline_def` is the tree's existing mechanism. Cost: re-home
     `tests/backrefs/fold_agreement_check.c`, `fold_agreement_utf8_check.c`,
     `fold_agreement_ucp_check.c` (they call `rx_span_match_caseless`) in the
     same change.
   - **Keep an exported one-line wrapper** that calls the static body: the
     three checks and any symbol reader keep working; the VM calls the static
     body.
   - Lane's lean: drop, because the readers are three test files in one
     directory. The choice is the manager's.
4. `[r2 R4]` **Split.** Should the START-admission half of `[START-DENSE]` read
   the existing MASS primitive now, rather than wait for `[PRIOR-COST-UNIFY]`
   (queued behind `[REQ-HANDOFF-L1]`)? (Frank's: it overrides his queue and
   D153.)
   - **4a, the VM-hat half: recommendation yes.** R4 already reads the fact, it
     needs no new primitive, bak-2 is a D77 witness, and PRIOR-COST-UNIFY
     absorbs it later (implement-then-replace, which the general-mechanisms
     memory allows).
   - **4b, the DFA-hat half: NOT supported.** D77 is not met until the
     five-arm DENSE-SKIP design is timed; the set totals cannot separate the
     entry cost from the per-step cost.
5. **Widen `[START-DENSE]`'s scope from the hat's disarm to every
   table-skip NEXT row plus the VM hat, and add `pick_skip_states` to the
   same family?** (**Manager's call**, `[r2 R4]`.)
   - Lane's lean: yes for the scope; the three phase-1 routes show one
     decision.
   - `pick_skip_states` is an F1 member (§1), but its candidate is now
     [OPT-3-RUNEND](a), which prices a stay as a loss on non-periodic text;
     keep it as that row's own small question, not part of START-DENSE.
6. **Order:** the §3 table. (Frank's for the round; the abi batching and
   filing the R4d / FIND R-n are the manager's, `[r2 R4]`: file the R-n now.)
   - **Recommendation:** the step-0 twin slot first; candidates 1 and 2 as
     the first pcrec lane (two small abi events, or one combined); the SWAR
     R-n filed at once.
7. `[r2 R2, R4]` **The WEIGHTING rule** (Frank's; D119's priority rule is the
   input). How should the round be ordered when total ns, cell count and
   worst ratio disagree (§4)?
   - **Manager's lean:** owner-actionable and certain first (a cheap confirmed
     step gate), then total ns, with cell count and worst ratio as
     tie-breaks.
   - **The panel's recommendation:** total expected recoverable ns, with cell
     count and ratio as gates and tie-breaks only (ns is the only additive
     unit; cells are not independent; ratio is dominated by ns-scale cells
     and by jit or SIMD peers).
   - Under the lean, candidate 1 goes first because it is cheap and gated by
     one twin; under the panel's rule candidate 7 does.

## 6. What remains open after the panel `[r2]`

The panel found no blocker. Open items, by who can close them:

**Needs a timing slot (owed twins).**
- `modj-static-seam` against its band's low end; `bak2-static-noinline` to
  separate the PLT from the specialization (candidate 1).
- The DENSE-SKIP five arms per subject on hex8, dbnames, json-constant
  (candidate 5), including the three stay twins (candidate 6 / [OPT-3-RUNEND]).
- lit-cat's `swar` BODY twin before the R4d row claims HIT-RESTART or C3
  (candidate 3).
- `bak2-trail-free` / `-both`, `bak2-no-start-set` + `phone-no-start-set`, T5,
  `split`.

**Needs a decision (the manager's, Frank's, or both).**
- Q2 (default or `--tune`, with the size number now in hand), Q3 (manager:
  drop the export or keep a wrapper), Q4 (4a yes, 4b unsupported), Q5
  (manager), Q6 (round order), Q7 (the weighting rule).
- Whether hex8's boundary-pair ratio of 0.391 is close enough to the ~0.3 line
  to build arm (E) (manager).
- The [PRIOR-COST-UNIFY] design's open rulings: where `C_MEMCHR`/`C_BITMAP` and
  G1's `memchr_form` density clause live (the kit's choice under D146, or
  labelled constants under a guard), and how K105 is expressed (the initial
  state of an [ADAPTIVE-ARM]).

**Not counted here.**
- The corpus population of candidate 1 (artifacts with `PCREC_ENCE_SPAN*` /
  `BACK_STEP`), of the `RX_DFA_SCAN "attempt"` / `start_max != 0` shape
  (candidate 7's population half; the bench's O-82 A3 single-witness finding is
  cited, not re-run), and of the F3 call-site census.
- The D119-eligible subtotal of the 94.3 ms (§4 tags the comparators, but the
  subtotal is not recomputed).
- mod-j-uc's remaining 6.5-8 ms has no named candidate (§2.0).
- Every timing: this document is a desk read plus three no-clock counts. The
  three counts are `[r2 count]`: rev2/split_size.txt, rev2/wordwait.txt and
  rev2/pairskip.txt.

**Filed, not scheduled.** [ADAPTIVE-ARM] and [SIZE-KNEE] (plan.md, `[r2 F6]`),
the F3 call-site census UNLOCK (§1), the boundary-pair skip (candidate 5), and
the `prefix_k` singleton-gate UNLOCK (§1 F2, trigger ci-moskva).
