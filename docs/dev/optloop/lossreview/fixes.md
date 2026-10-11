# [LOSS-REVIEW] phase 2: general fixes (lane lrfix, 2026-10-11)

Contract: `../lossreview_charter.md`, Phase 2. Frank: "look for general fixes,
assess them; PRIORITIZE FIXES TO EXISTING OPTS." Inputs: the three phase-1
attributions on main 28b3df8a (`dfa.md` 51.2 ms / 29 cells, `vm.md` 34.6 ms /
37 cells, `misc.md` 8.56 ms / 25 cells), their twins, and the plan rows they
name.

**Evidence tier.** This lane is a desk read. No clock was read and nothing
was compiled. Every ns figure is a bench set-grain number quoted from phase 1.
Every count is phase 1's. Every "expected gain" below is a prediction, and
each one names the owed twin that confirms or refutes it. The source sites
were read at main 28b3df8a.

## 0. Answers first

1. **Four cross-route families cover about 90% of the 94.3 ms.** Each family
   already has dispersed members in the tree. §1 names them by
   file/function.
   - **F1, one priced decision ("is this scan worth it, and on which
     byte").** Every pick and every admission that reads the byte-rate prior,
     or should read it. It includes four start-skip admissions that carry NO
     density term today (the DFA hat, the VM hat, the plain byte-class rows,
     M2.1's stay threshold). Home: `[PRIOR-COST-UNIFY]` + `[START-DENSE]`.
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

   The one existing opt that would cover it is M2.1's stay loop. It declines
   only on a hand-set constant: `pick_skip_states` admits a state that stays
   put on at least 192 of 256 bytes (`src/gen/emit_dfa.c:4742`), and a word
   state stays put on 63. §2 candidate 6.
3. **Top 6 candidates, cheap-and-certain first** (§3 gives the order and its
   dependencies). The reach figures are phase-1 bench ns and are not
   additive across rows.

   | # | candidate | kind | reach (cells / phase-1 loss) | expected gain (basis) | decisive twin |
   |---|---|---|---|---|---|
   | 1 | **Seam entries `inline_def`** (`<p>_span_match[_caseless]`, `<p>_back_step` stop being PLT calls) | fix-existing: an existing `PcrecEncEntry` column | C1's 10 cells (27.2 ms) + lkb-* | ~2-4 ns × 4.7M PLT calls ≈ 7-19 ms, capped by the loss; the only C1 fix that reaches **mod-j-uc** (9.45 ms, a framed program) (derived; `.text` 4,161 → 3,156 B on bak-2) | `modj-static-seam`, `bak2-static-seam`, `bak1-static-seam` |
   | 2 | **D160 in the `fo` shape** (the authored utf8 prior) | fix-existing: data read by three existing pick sites | 6 U8-PICK cells (≤1.24 ms) | ≤1.17 ms modelled; counted stops ×4-×2,400 fewer; 0 of 62 other utf8 cells move >6% | T5 (`misc/`, `--analysis fo20`) |
   | 3 | **R4d (SWAR fused pair filter) + a `fn_rows[]` BODY row** | fix-existing: new rows in two existing kit row tables | HIT-RESTART 14 + K101 2 + C3 7 + stop-cost 7 cells: 8.8 ms, + part of RUN-PICK and PAIR-SKIP | R-1 measured 1.95x / 2.7x on sweeps at SIMD-off; the per-call share is 50-80% of these cells ⇒ most of 8.8 ms. NOT a gain in gate mode (R-1 mod-i gate 1m: 75.75 vs 73.35 ns) | R-1 is the kit-side witness; per cell, none (`dfa.md` §4): owed |
   | 4 | **[ART-TRAIL-ELIDE]'s frameless sub-case** (no dominance fact needed) | fix-existing: narrows a filed row to the half that needs no new analysis | 5 frameless C1 cells (17.7 ms): 22.7M trail-reset iterations | up to ~7-11 ms at 0.3-0.5 ns per iteration (derived, UNMEASURED) | `bak2-trail-free`, `bak2-both`, `bak1-both`, `phone-both` |
   | 5 | **One density-priced START admission + set-shape FIND forms** (`[START-DENSE]` widened to the VM hat, the DFA hat and the plain table-skip rows; the kit's FIND gains memchr2 / SWAR-cube / range rows) | fix-existing: three predicates gain the MASS term that R4 already reads; `pf_walk` gains siblings | C2 3 + C1c (bak-2's +17.5%) + set-skip 5 + PAIR-SKIP 2 + RANGE-SKIP 2 + ci-moskva + DENSE-SKIP 3 cells: ~22 ms | per sub-form, §2 candidate 5 (scalar-skip loads ÷ 8 on the cube cells; one memchr on the \|S\| = 1 VM hat cells) | `bak2-no-start-set`, `phone-no-start-set` (the control), `quoted-seek`, `parens-seek`, `kname-seek`, T2/T6, `hiskip`, `plainloop` ×3, `-fno-start-set` ×3 |
   | 6 | **WORD-WAIT stay admitted by mass** (`pick_skip_states` priced, not counted) | fix-existing: one constant becomes a priced predicate | C5 5 cells + DENSE-SKIP 3 + aws (S5): up to ~14 ms | `ctx64-stay22`: 85,988 → 6 forward steps. On text the stay run is the word length (~4-6 B), so the gain is the latency-chain removal and NOT the step count: UNCERTAIN | `ctx64-stay22` (built); hex8/dbnames/json-constant stay twins NOT built (owed) |

   `[OPT-ATTEMPT-SPLIT]` (28.9 ms, the largest single item) ranks 7th, and on
   purpose:
   - it is ONE pattern corpus-wide (bench O-82 A3);
   - it is a new route composition, not a widened opt;
   - its size question is open (`[ENG-ABS-CARET]`).

   Its exact twin exists (`dfa/twins/mk_split.py`), so it is ready the moment
   Frank rules on Q2.
4. **Weighting (§4).** By total ns the ranking is ATTEMPT-SHAPE > C1 >
   DENSE-SKIP. By cell count it is HIT-RESTART (14) > C1 (10) > the utf8
   picks / C3 / stop cost (7 each). By median ratio it is RUN-PICK ×9.5 >
   ATTEMPT-SHAPE ×4.8 > U8-PICK ×2.9. The three disagree most on two items:
   - **C1** is 27 ms, but each cell is x1.27 and non-algorithmic (interp is
     6-8x slower than pcrec);
   - **the utf8 picks / set-skip / C3** total only 1.2-4 ms, but each cell is
     x2-x10.

   Candidates 1, 3 and 5 rank high on every ordering. ATTEMPT-SPLIT ranks
   high on total ns only.

## 1. Families (sibling-of-a-family lens)

Each family names its existing DISPERSED members (file:function, read at
main). Phase-1 causes map onto the families as follows:

| family | phase-1 causes (ms) | sum |
|---|---|---|
| F1 priced decision | RUN-PICK 1.76, U8-PICK 1.24, C7 0.06 + ATTEMPT-STEP 0.04, K105 (off-bench), ci-moskva 0.82, plus the ADMISSION half of DENSE-SKIP 13.2 / C1c / C5 0.26 | ~17 |
| F2 kernel form | HIT-RESTART 4.42, K101 0.92, C3 1.99, stop cost 1.43, PAIR-SKIP 1.36, set-skip 3.85, C2 2.58, RANGE-SKIP 0.44, C8 0.41 | ~17.4 |
| F3 VM per-attempt | C1 27.2, C6 0.27 | ~27.5 |
| F4 route shape | ATTEMPT-SHAPE 28.9, C4 1.83, DFA-steps-over-literal 0.57, REV-PASS 0.13, S5 0.65 | ~32 |

(F1 and F2 overlap on DENSE-SKIP, which has both a "whether" half and a
"how" half. The total is therefore not a partition.)

### F1: one priced decision

**The family's question.** Every one of these sites asks the same thing:
the expected hit gap of a byte (or set, or run) under the prior, against the
work a scan saves per hit and costs per entry. `[PRIOR-COST-UNIFY]` was
filed with four members (G1, set-leads, R4, `req_landmark_admits`). Phase 1
found eight more siblings, so the family is twelve:

| member | file:function | what it reads today | what it should read |
|---|---|---|---|
| G1 dominance | `emit_dfa.c:7441 req_byte_dominated_by` | `pcrec_find_no_commoner` (rate) | (filed member) |
| set-leads | `findings.c:433 pcrec_find_pick` via the PRESENCE row | rate | (filed member) |
| R4 adaptive-dense | `emit_dfa.c:8531 cand_rs_dense_applies` | `pcrec_dfa_cand_ppm` × gap: **the only density-priced START decision in the tree** | (filed member) |
| handoff admission | `req_landmark_admits` (lane/rlhbuild, unmerged) | prior gap only; K105 | prior + a run-time arm (K105's fix shapes) |
| **run choice** | `src/facts/req.c:308 rn_better` | information (Σ popcount) alone; rate only for the member | rate × per-hit cost among runs that clear `PCREC_MIN_REQ_RUN_BITS` (RUN-PICK: FROM/`f` −27% hits) |
| **G2 one-attempt** | `emit_dfa.c:7400 req_route_one_attempt` | route only, no reach | the byte's reach (unbounded leading run ⇒ admit): C7 + ATTEMPT-STEP |
| **prefix_k offset pick** | `src/opt/prefix_k.c:204` `base_scan = k0count == 1 ? C_MEMCHR : C_BITMAP` | constants 6 / 116, measured on ASCII-sparse text; no stop count | stops × per-stop cost against bytes × per-byte cost (ci-moskva: memchr `D0` 146,633 stops) |
| **VM hat admission** | `emit_dfa.c:7087 pf_vm_start_applies` | `\|S\| < 256` only (D149 UNMEASURED) | MASS: decline a dense S (bak-2's `\w` at 76%) |
| **DFA hat admission** | `emit_dfa.c:6930 pf_dfa_start_set` | T ⊊ E only | MASS + entry cost (DENSE-SKIP; K91) |
| **plain byte-class NEXT rows** | `cand_rows[]` `byte-class[-bounded]` | always applies over `none` | MASS (hex8 under `-fno-start-set` is just as short) |
| **M2.1 stay states** | `emit_dfa.c:4742 pick_skip_states` | stays on ≥ 192 bytes (count) | stays on bytes carrying ≥ X of the prior's MASS (C5; WORD-WAIT, §0 item 2) |
| utf8 rate NONE | `pcrec_find_byte_rate` under `-e utf8` | NONE ⇒ rightmost/leftmost rule | D160's authored prior (data, not code) |

**The general form.** One primitive returns expected cost given a candidate
set S: rate(S) per byte, a per-hit cost and a per-entry cost (both priced
by the form F2 picks), against the per-byte cost of the alternative (plain
stepping, an attempt, or no check). Each member's predicate reads it. Three
primitives already exist and are the pieces:
- `pcrec_find_set_ppm` (MASS);
- `pcrec_dfa_cand_ppm` (the scanned set's mass);
- `pcrec_find_run_rank` (the per-position ranking already handed to the
  kit, RQ-2).

**Two halves with different timing.**
- The START-admission half (VM hat, DFA hat, byte-class rows, stay) can read
  `pcrec_dfa_cand_ppm` / `pcrec_find_set_ppm` today with no new primitive.
  This is how R4 already works.
- The PICK half (run choice, offset pick, G2 reach, K105) needs the per-hit
  term, so it is `[PRIOR-COST-UNIFY]` proper.

Recommendation (Q4): do not serialize the first half behind
`[REQ-HANDOFF-L1]`. Build it on MASS, and let `[PRIOR-COST-UNIFY]` absorb
it.

**Constants that are this family's symptoms** (memory
pcrec-suspect-tuning-constants), each a hand-set cut-over standing where a
priced comparison belongs:
- `pick_skip_states`' 191;
- `C_MEMCHR`/`C_BITMAP` 6 / 116;
- `pf_vm_start_applies`' 256;
- `pf_vm_emit_first_class`'s "|S| = 1 → memchr cut-over is not taken"
  (D149).

### F2: the kernel's FORM, chosen by set shape and density

**The family's question.** Given the set a scan stops on, which loop? Today
the choice is set CARDINALITY alone:
- `memfn/src/pffind.c`'s header says "the one-byte/table split is the
  SITE's ..., not a priced choice";
- the ofsskip FUNC body has two rows (`memfn/src/ofsskip.c:206 fn_rows[]`:
  `fn-pair` for a cube pair, `fn-memchr` otherwise).

Dispersed members:

| site | file | forms today | phase-1 loss of the missing form |
|---|---|---|---|
| PF (DFA prefilter FIND, DFA hat, VM hat seek) | `memfn/src/pffind.c` rows `pf_memchr[_bounded]`, `pf_walk[_bounded]` | memchr (\|S\| = 1), byte table walk (\|S\| > 1) | set-skip 3.85 (cube SWAR), PAIR-SKIP 1.36 (memchr2/SWAR pair), RANGE-SKIP 0.44 (range), C2 2.58 (the VM hat has the TABLE only, even at \|S\| = 1: `emit_dfa.c:7111`) |
| OFS FUNC body | `memfn/src/ofsskip.c:206 fn_rows[]` | `fn-pair` (cube pair, 2 memchr streams), `fn-memchr` | HIT-RESTART 4.42 (lit-cat family, keyword-prefix-order, grp-noncap), C3 1.99, stop cost 1.43 |
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

Under D157 pcrec's half is only facts: the set (already handed over as
`PCREC_FIND_START_SET`), the rate (MASS, RQ-2's ranking), and the set's
cube/interval decomposition, which the kit can derive itself from the set.
The kit picks the row. **No pcrec decision moves**: this is new rows in two
existing kit row tables, D146/D147.

**[POS-PARALLEL] as the general home.** A SWAR cube skip IS stage-1
classification over an 8-byte window. The pair filter IS two class vectors
ANDed at a fixed distance. So F2's scalar rows are the window-sized case of
[POS-PARALLEL]'s stage 1, and its hybrid consumer is "attempt-loop skip by
bit reads and ctz". **Recommendation: do not route these fixes through
[POS-PARALLEL].** It is a design study ("NEEDS THOUGHT"). F2's rows are kit
forms with measured triggers (R-1) and identity-checked twins (T2/T6).
Record the scalar rows as [POS-PARALLEL]'s stage-1 witnesses, so the study
starts from measured forms.

**Unlock** (for the panel's general-form lens): once the kit holds a cube or
pair FIND row, the same row also serves:
- the VM hat seek (C2);
- the hybrid RETRY's step-through-set (C4 retry half, `possq-stepset`: VM
  attempts 1,295,798 → 95,957);
- `[REQ-HANDOFF-L1]`'s two-landmark window scan (Frank's 2026-10-11
  refinement: the window scan IS an offset-set pick bounded by the
  landmark).

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

The [CC-DIFF] STEP 1 `always_inline` work was the same lever for the entry
chain's statics. The seam entries were outside it because they are exported.
That is the sibling this lens exists to catch.

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
  - Fallback if a reader needs the exported symbol: keep an exported
    one-line wrapper and call the static body from the VM (lrvm's
    proposal).
- **Reach:**
  - Bench: C1's 10 cells (27.2 ms). lkb-pos/neg (6 `back_step` sites each)
    are mostly C3, so the gain there is minor.
  - Corpus: every backreference-, variable- and lookbehind-bearing artifact.
    This is countable as artifacts whose mask carries `PCREC_ENCE_SPAN*` or
    `BACK_STEP`. Not counted here: the box is held.
- **Expected gain:**
  - Counts: 4.7M PLT seam calls across the 6 throughput cells (727K-794K
    each; phone 241K).
  - Assumed cost per call: an indirect PLT `jmp` plus call/ret plus the lost
    specialization of a constant-length compare, ~2-4 ns on Zen 1. That
    figure is derived and UNMEASURED.
  - Result: ~7-19 ms, capped by the loss.
  - It is the **only C1 fix that reaches mod-j-uc** (9.45 ms, the largest
    C1 cell), whose program is FRAMED. C1b's sub-case does not reach it.
  - Static evidence: bak-2 `.text` 4,161 → 3,156 B.
- **Risk:**
  - Answers: none. The same function is called from the same site.
  - abi: an event. Emitted text moves on every artifact carrying the
    entries; readers are found by grep (D94).
  - Checks:
    - S109 and S133 count CALLS of the seam, so an inline call keeps them
      green.
    - The [M5-SEAM] codegen fixtures assert declarations per row; those
      move.
    - `tests/memfn/pins/n7_target/` pins the N7 span loop's text inside the
      entry. The loop is unchanged; only the linkage and the declaration
      move.
  - Size: none (it shrinks).
- **Remodel overlap:** none on the decision side. The N7 loop is memfn's
  (M7) and the entry's signature is the backend's (D58 addendum 2). This
  touches only the backend's own row column.
- **D77:** met: a measured per-call PLT site on 6 bench cells, 27 ms.
- **Twins:** `modj-static-seam` (the decisive one, since the framed cell
  has no C1b confound), `bak2-static-seam`, `bak1-static-seam`. If
  `modj-static-seam` shows less than ~2% on mod-j-uc, the PLT attribution
  is refuted and C1 is trail-dominated.

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

### 3. R4d plus a BODY row in the ofsskip `fn_rows[]`

- **Site:**
  - the memfn kit: a new SWAR pair-filter scan+verify row in the PRE
    composite (`memfn/src/precheck.c`, integration.md §22, the R-1 `swar`
    variant);
  - the same form as a BODY row in `memfn/src/ofsskip.c:206 fn_rows[]`,
    above `fn-pair`/`fn-memchr`.

  pcrec's half is only the facts it already states (the run, its mask, and
  RQ-2's ranking). The manager files the R-n.
- **Reach:**

  | cause | cells | phase-1 loss |
  |---|---|---|
  | HIT-RESTART | 14 (lit-cat family run-pinned, keyword-prefix-order and grp-noncap offset-set, stack-frame, asr-*, cls-fold-pair) | 4.42 ms |
  | K101 | 2 (mod-i/-r) | 0.92 ms |
  | C3 | 7 (lkb-*, lka-*, slack) | 1.99 ms |
  | stop cost | 7 (lit-l8, alt-foo-tails, nfc-pair half, counted-3b, nearmiss, 1ch-3b, cyr-run) | 1.43 ms |

  In part it also reaches:
  - union-select (RUN-PICK, 1.76 ms vs jit);
  - PAIR-SKIP's `{c,d}` as a two-byte filter;
  - C8 (grp-cap family, DENSE's VM twin).

  The 17 listed SCAN-SIMD cells have the same per-hit shape at sparse
  density. Their scalar share is reached too.
- **Expected gain:**
  - R-1 (Zen 1, gcc 15.2): swar against the emitted gate is 1.95x on the
    union-select gate and 2.7x on the mod-i sweep.
  - Phase-1 count: auto_ns per memchr call is 10-17 ns at 5-8 calls per
    match, so the calls are 50-80% of these cells' time (lit-cat: 42,663
    calls × ~12 ns ≈ 512K of 663K ns).
  - Applying R-1's ratio to that share closes most of HIT-RESTART's
    x1.25-1.3 gaps and roughly halves C3's x1.6-3.0. This is an
    extrapolation from R-1's cells, and no per-cell twin exists.
  - **Caveat:** R-1's gate-mode row shows swar SLOWER when the first hit is
    near (mod-i gate 1m, hit at 404: 75.75 vs 73.35 ns). The win is a
    sweep-regime win, and every cell above is sweep regime.
- **Risk:**
  - Answers: identity by construction; the kit's own checks.
  - pcrec: an abi event at the kit merge (a kit byte move is a pcrec abi
    event in the same commit, D147).
  - D149: `swar`'s 2x unroll is a labelled unmeasured default.
  - Q1 (is SWAR scalar?) gates it.
- **Remodel overlap:** kit-owned text. `[REQ-HANDOFF-L1]` touches
  stack-frame's site (not a mover per its census) and the PRE re-entry
  (R-15).
- **D77:** MET at SIMD-off (R-1).
- **Twins:** none per cell (`dfa.md` §4, `vm.md` §4.1 item 7). The R-1
  probe (`docs/design/memfn/probes/twins/`) is the kit-side witness. A
  bench alpha on HIT-RESTART cells is the landing gate.

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
  - 5 frameless C1 cells (bak-2, bak-1, bak-py, bak-g-rel, phone): 17.7 ms.
    Trail-reset iterations: 6.79M + 3 × 4.04M + 3.81M = 22.7M.
  - Population (from the row): 27 bench / 623 corpus frameless artifacts
    with `RX_SET`.
  - mod-j-uc is FRAMED, so not reached.
- **Expected gain:** up to ~7-11 ms at 0.3-0.5 ns per reset iteration
  (derived, UNMEASURED). It composes with candidate 1: bak-2 `.text`
  4,161 → 2,036 B for the pair.
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

### 5. One density-priced START admission, plus set-shape FIND forms

This candidate is two halves of one table: F1's "whether" and F2's "how".

- **(a) Admission, pcrec side.** Three predicates read MASS (the
  `pcrec_dfa_cand_ppm` / `pcrec_find_set_ppm` R4 reads), against a
  per-entry cost:
  - `pf_vm_start_applies` (`emit_dfa.c:7087`);
  - `pf_dfa_start_set` (`:6930`);
  - the plain `byte-class[-bounded]` NEXT rows.

  The per-entry cost comes from the twins, never a guess (D149). This is
  `[START-DENSE]` (K90 + K91 + K83 + [OPT-HYB-RESEED-POLICY], gated on C7,
  which is done) widened from "the hat's disarm" to every table-skip NEXT
  row and the VM hat.
- **(b) Form, kit side.** New PF rows beside `pf_walk`:
  - memchr2 / SWAR pair for \|S\| = 2;
  - SWAR cube skip for ≤ 3 cube terms (misc T2/T6's form);
  - a range loop for one interval.

  The VM hat drops its "TABLE form at any \|S\|" rule
  (`pf_vm_emit_first_class`, Q-R5). At \|S\| = 1 it takes `pf_memchr`.
- **Reach and expected gain per sub-form:**

  | sub-form | cells | phase-1 loss | expected (basis) |
  |---|---|---|---|
  | VM hat \|S\| ≤ 2 → memchr/pair | quoted-delim, bak-k-named, balanced-parens | 2.58 ms | 4.6M / 1.3M / 1.3M table-walk iterations → memchr; most of the loss (jit's edge is a SIMD first-unit search, and glibc memchr is that) |
  | VM hat dense decline | bak-2 (and bak-1/py/g-rel +3-4%) | bak-2's +17.5% since 10-05 ≈ 2.3 ms of pcrec time | the grower reverses; `phone-palindrome-6` must not regress (10-member digit set, low density) |
  | cube-SWAR skip | ci-sigma, ci-kelvin, ci-turkish-i, alt-distinct-lead, ci-strasse | 3.85 ms | scalar-skip loads ÷ 8 ⇒ up to ~3 ms (misc S2; fit price 0.44 ns/B, UNMEASURED) |
  | memchr2 / pair | alt-two, alt-nested | 1.36 ms | near O-51's 8% crossover; one bounded attempt (pcrec-one-pass-loss-chasing) |
  | range | high-byte-run, utf8-lead-no-cont | 0.44 ms | small; fold into the same row set |
  | prefix_k re-price | ci-moskva | 0.82 ms | possible only once a cube row exists to price |
  | DFA admission | hex8, dbnames, json-constant | 13.2 ms | UNKNOWN until `plainloop` is timed: the skip vs plain stepping. Candidate 6 is the competing explanation |

- **Risk:**
  - Answers: identical (skip forms only).
  - abi: events on both sides.
  - The dense-decline threshold must come from the twins (D149). A wrong
    one regresses the sparse controls (the phone cell; startset.md §7's
    guard cells).
- **Remodel overlap:**
  - `[START-DENSE]` itself.
  - The PF text is memfn's (R4g), so the FIND rows are kit rows.
  - `[PRIOR-COST-UNIFY]` later absorbs the MASS read.
- **D77:**
  - The VM-hat half is met: measured round-2 regressions are named in the
    START-DENSE row (quoted-delim +0.84 ns/B), and bak-2 is the one
    grower.
  - The cube-SWAR half is met by loss (3.85 ms). Its speed is owed.
  - The DFA-hat half is NOT met until `plainloop` is timed.
- **Twins:**
  - `bak2-no-start-set`, `phone-no-start-set` (the control);
  - `quoted-seek`, `quoted-seek-seam`, `parens-seek`, `kname-seek`;
  - misc T2 and T6 ×3;
  - `hiskip`;
  - dfa `plainloop` ×3 and `-fno-start-set` ×3.

### 6. WORD-WAIT: price M2.1's stay threshold by mass

- **Site:** `emit_dfa.c:4742 pick_skip_states`, `bestcnt = 191`.
- **What changes:** a state is stay-eligible when the bytes it stays on
  carry at least X of the prior's MASS (X derived from the twin, not set
  by hand), rather than 192 of 256 byte values. The site's text is
  memfn's (R4h STAY); the decision is pcrec's.
- **Why this is a cross-route candidate.** The `\b` word-wait state
  self-loops on the 63 word bytes, which are ~80% of text mass. Phase 1
  finds the DFA stepping it byte by byte in four places:
  - ctx-* (lrvm: 85,988 of 85,988 letter bytes in state 22);
  - dbnames / json-constant / hex32-id (lrvm's FYI gcov: 2.56M / 1.46M /
    3.23M forward steps);
  - aws (lrmisc: after the first non-boundary `A` the machine sits in
    `seed[word]`, 65.5K steps per 65.5K bytes);
  - and plausibly hex8.
- **Reach:** C5 5 cells (0.26 ms vs jit, 0.59 ms vs rust) + DENSE-SKIP's 3
  (13.2 ms) + aws (~0.25 ms). Up to ~14 ms. Corpus: every leading- or
  trailing-`\b` DFA scan, hybrid prefilters included.
- **Expected gain:** UNCERTAIN, and the twin set is incomplete.
  - On ctx-*'s random-letter subject the run is the whole subject
    (`ctx64-stay22`: 85,988 → 6 steps).
  - On text the run is one word (~4-6 B). The stay loop then removes the
    data-dependent table-load chain (the ~3.2 ns/step that OPT-3 attributes
    to latency) but not the per-word exit mispredict. That exit is exactly
    what makes the DENSE-SKIP hat lose (mean skip 1.75 B on hex8).
  - M2.10's regression was a REVERSE-machine skip. The forward machine is
    untested (`pick_skip_states`' own comment).
- **Risk:**
  - Answers: identical. The `state_acc_varies` and `scan_span` exclusions
    stay.
  - abi: an event.
  - A stay loop on short runs can lose like the hat does.
- **Remodel overlap:** R4h STAY text (kit); `[START-DENSE]` (the same
  regime from the other side).
- **D77:** met on ctx-*. NOT met on DENSE-SKIP until a stay twin exists for
  hex8/dbnames/json-constant.
- **Twins:**
  - `ctx64-stay22` (built);
  - **owed and not built:** `hex8-stay`, `dbnames-stay`, `json-stay`, each
    timed against `plainloop` and base.

  Those three-way timings decide between candidates 5(a) and 6 for the
  13.2 ms: skip-or-step against stay-loop.
- **Unlock:** if the stay twin shows the per-word exit dominates, the next
  rung is [POS-PARALLEL]'s "DFA self-loop spans left by one ctz over the
  mask" consumer, with that twin as its trigger cell.

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
- **Expected gain:** waf M5.b's x3.51 upper bound (8.42 → 2.40 ns/B), i.e.
  ~20 ms of the 28.9. After the split, the residual is the first set's
  word class, which candidates 5 and 6 address. They compose.
- **Risk:**
  - Size: up to 2x the table bytes on an already-large artifact; the row's
    own "SIZE IS THE ARGUMENT AGAINST IT".
  - Answers: exact by construction (87/87 subjects).
  - The predicate is false for every other artifact, so the five
    fully-anchored artifacts stay byte-identical (the row's
    do-not-regress list).
  - abi: an event.
- **Remodel overlap:** `[ENG-ABS-CARET]`. Split versus absorb is decided on
  size first.
- **D77:** met (28.9 ms, algorithmic).
- **Twins:** `split` (#18) is the acceptance witness.
- **Q2** carries the default-or-`--tune` question.

### 8. [PRIOR-COST-UNIFY]'s pick half, after [REQ-HANDOFF-L1]

These members need the per-hit term:

| member | change | reach | gain | twins |
|---|---|---|---|---|
| run choice (`rn_better`) | rate × per-hit cost among runs over the floor | union-select | −27% hits by prior (FROM/`f`); 1.76 ms vs jit / 0.49 vs re2 is the ceiling | `ciprecheck select c` (control), `from f`, `from m`, `union u` |
| G2 reach-aware (`req_route_one_attempt`) | admit where the byte sits behind an unbounded leading run (the landmark-offset fact `[REQ-HANDOFF-L1]` introduces) | moment-iso8601, email-owasp | 0.10 ms (re2 x39.8: algorithmic) | `moment-precheck`, `precheck`, `deferpre` |
| K105 handoff admission | an adaptive-dense arm (the RETRY rows' shape) | hcolon_in (off-bench, x1.5) | the x1.5 | T3 (`twin_hcolon.sh`) |
| prefix_k cost | stops-priced | ci-moskva | 0.82 ms | none (needs candidate 5's cube row first) |

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
  - The retry half (`possq-stepset`) rides candidate 5's FIND rows.
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

| step | item | size | depends on | can run beside |
|---|---|---|---|---|
| 0 | **Quiet slot: time the owed twins in this priority**: `modj-static-seam`, `bak2-both`, `bak2-trail-free`, `bak2-no-start-set` + `phone-no-start-set`, `quoted-seek`, `plainloop` ×3, T2/T6, `ctx64-stay22`, `split`, T5 | one slot | box | — |
| 1 | Candidate 1: seam `inline_def` | S (a column flip + spec sentence + re-pins) | modj twin ≥ noise | 2, 3 |
| 2 | Candidate 2: D160 `fo` prior | S (data) + abi | T5 | 1, 3 |
| 3 | Candidate 3: file the R-n for R4d + the `fn_rows[]` BODY row | kit lane | Q1 | 1, 2 |
| 4 | Candidate 4: trail-free frameless | M | after 1 (one VM abi event each, or one combined) | 5 |
| 5 | Candidate 5(b): kit FIND rows (memchr at the VM hat \|S\| = 1, pair, cube, range) | kit lane | Q1; R4d shares the SWAR layer | 4 |
| 6 | Candidate 5(a): the START admission on MASS | M | step-0 twins (the threshold) | after 5(b) lands its forms (the admission prices the form) |
| 7 | Candidate 6: WORD-WAIT stay by mass | S-M | the three owed stay twins | 6 (they split the DENSE 13.2 ms) |
| 8 | Candidate 7: ATTEMPT-SPLIT | M-L | Q2; `attemptcensus` size number | any |
| 9 | Candidate 8: the PRIOR-COST-UNIFY pick half | M | `[REQ-HANDOFF-L1]` merged | — |
| 10 | Candidate 9's one-pass items | S each | — | any |

Dependencies, in short:
- Step 6 reads per-entry costs measured on the forms step 5 ships.
- Step 7 and step 6 are two explanations for the same 13.2 ms, so their
  twins must be timed together.
- Step 9 waits on the L1 merge (Frank's queue).

## 4. Weighting caveat: ns total against cell count against ratio

Totals are dominated by a few cells:
- concat-sqli alone is 28.9 of 94.3 ms (31%);
- C1's six throughput cells are 27.2 ms (29%);
- together they are 60% of all loss on 7 of 91 cells.

| cause | total ms | cells | median ratio (vs the trailing peer) | a scalar engine also wins? |
|---|---|---|---|---|
| ATTEMPT-SHAPE | 28.87 | 1 | 4.80 (re2) | yes |
| C1 BACKREF-ATTEMPT | 27.19 | 10 | 1.27 | no (interp 6-8x slower) |
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
| C6, C5, C8, RANGE-SKIP, REV-PASS, DFA-literal, C7/ATTEMPT-STEP | 0.04-0.57 each | 1-5 | 1.16-1.97 (C7: x10.7 jit / x39.8 re2) | C7 yes |

**Where the orderings disagree, and what it does to the candidates:**

- **Total ns** puts ATTEMPT-SPLIT and C1 first. ATTEMPT-SPLIT is one cell
  of one pattern corpus-wide, so its 28.9 ms is a single bench cell's
  weight. C1 is non-algorithmic: jit wins by code generation.
- **Cell count** puts HIT-RESTART first (14 cells, but each about x1.29),
  then C1 (10), then the utf8 picks / C3 / stop cost (7 each).
  - By this measure, R4d (candidate 3) is the broadest single fix, touching
    30 cells.
  - Candidate 5 is second (18 cells across its sub-forms).
- **Median ratio** puts the small-total cells first: RUN-PICK x9.5 vs jit,
  C7 x10-40, U8-PICK x2.9, set-skip x2.4, C3 x2.3. These are the cells a
  reader of the bench sees as "badly behind", and their totals are small
  because the throughput subjects are small or the sets are synthetic.
- **The candidates that survive every ordering:** 1 (largest-ns family, 10
  cells), 3 (most cells, mid ratios) and 5 (high ratios on C2 / set-skip
  plus the DENSE-SKIP total).
  - ATTEMPT-SPLIT survives only total ns.
  - D160 survives ratio and cell count, not ns.
- **Bench caveats carried from the gap report:**
  - peers are cross-window (`--peer-group`);
  - capability moved from 0.1 to 0.2, which changed its throughput
    subjects, so moment-iso8601 and email-owasp exist as losses only on
    0.2's hazard subjects;
  - litrun is synthetic.

## 5. Questions for Frank (plain, each with a recommendation)

1. **Is portable-C SWAR (64-bit words, no ISA text, no intrinsics) part of
   the scalar layer that ships with `-fmemfn-simd` OFF?**
   - Why it matters: R4d, the cube skip and `hiskip` all depend on it.
     waf_attribution §5 Q1 left it open, though R-1 already calls `swar`
     "the scalar-layer candidate".
   - **Recommendation: yes.** It is plain C that every gcc target compiles.
     The D147 layer line is ISA text, not word width.
2. **ATTEMPT-SPLIT: default or a `--tune` position?** It is one witness
   corpus-wide and 28.9 ms on the bench.
   - **Recommendation: default-on, behind a size decline.** The predicate
     is false for every other artifact, so the size cost lands only on the
     one pattern that has the shape. Decline where the split artifact would
     cross the size-ladder threshold.
   - Before building, run `attemptcensus` (compile-only, already named by
     [ENG-ABS-CARET]) for the split's size on the witness.
3. **Seam entries: drop the export (`inline_def`, a §3¶2 spec sentence), or
   keep an exported wrapper?**
   - **Recommendation: drop it.** The spec already says they are not caller
     entries, and `inline_def` is the tree's existing mechanism for exactly
     this. Keep the wrapper only if a reader of the symbol turns up.
4. **Should the START-admission half of `[START-DENSE]` read the existing
   MASS primitive now, rather than wait for `[PRIOR-COST-UNIFY]` (queued
   behind `[REQ-HANDOFF-L1]`)?**
   - **Recommendation: yes.** R4 already reads it, it needs no new
     primitive, and PRIOR-COST-UNIFY absorbs it later. That is
     implement-then-replace, which the general-mechanisms memory allows.
5. **Widen `[START-DENSE]`'s scope from the hat's disarm to every
   table-skip NEXT row plus the VM hat, and add `pick_skip_states` to the
   same family?**
   - **Recommendation: yes for the scope.** The three phase-1 routes show
     one decision.
   - Keep the stay threshold as its own small row (candidate 6), because
     its twin set differs.
6. **Order:** the §3 table.
   - **Recommendation:** the step-0 twin slot first; candidates 1 and 2 as
     the first pcrec lane (two small abi events, or one combined); the R4d
     R-n filed at once.

## 6. For the D6 panel to attack

- **The PLT attribution (candidate 1).** Is the cost the PLT, or the lost
  specialization of a fixed-length compare that `inline_def` would also
  restore? Either way the fix is the same. The decisive question is the
  magnitude. If `modj-static-seam` shows nothing, C1 is the trail (framed
  mod-j-uc pops 2.05M trail entries) and candidate 1 drops to a
  size-only cleanup.
- **DENSE-SKIP's three explanations:**
  - (i) the skip's entry cost (`plainloop` wins);
  - (ii) the word-wait state's per-byte table chain (the stay twin wins);
  - (iii) neither: OPT-3's latency chain on every step, which only a
    second-stream / mask form addresses ([POS-PARALLEL]).

  These need one three-way timing on hex8 / dbnames / json-constant before
  candidate 5(a) or 6 is built for that 13.2 ms.
- **The F2 claim that FIND forms are ONE kit row table across the PF, OFS
  and PRE sites.** D63 says the DERIVATION is shared and the LOOP
  INTEGRATION is per-engine. Check whether a cube/pair row really serves
  the DFA prefilter, the VM hat seek and the hybrid retry with one
  contract, or splits per site.
- **R4d's extrapolation.** R-1 measured kit-side cells (union-select,
  mod-i). The 14 HIT-RESTART cells are run-pinned/offset-set FUNC bodies
  with exact (unmasked) runs. Is the fused pair filter's advantage there
  the same as on the masked caseless run R-1 timed?
- **Sibling sweep for F1.** Are there more prior-reading or
  constant-gated admissions than the twelve listed? Candidates to check:
  - the scan-edge minimum chain floor;
  - `PCREC_MAX_SCAN_EDGES`;
  - the RETRY rows' calibration columns (`vm_reseed_cal`).
- **General form + unlocks.** Panelists: propose the single expected-cost
  primitive's signature, and which of F2's rows it must price per hit and
  per entry, so that F1's twelve members read it without restating it.
- **Weighting.** Should the round's selection weight cells (or the bench's
  "badly behind" ratio cells) above total ns, given that 60% of ns sits on
  7 cells and one of them is a single corpus witness?
