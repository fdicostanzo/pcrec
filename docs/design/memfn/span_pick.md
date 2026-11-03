# span_pick — the kit's ONE "find the span" choice mechanism (design, rev 2)

**Status: PROPOSED, rev 2 (lane spanpick2, 2026-11-02, from main 959c08124). Design only: not a build
go, no code, no make, no timing.** Applies review `docs/dev/reviews/2026-11-02-r1-memfn-spanpick.md`
and the owner's answers (decisions.md D186 addendum 1: A1, A2, A6). Read §Disposition of review
2026-11-02 r1 first; changed text is marked `[rev2 <id>]`. Direction (owner, 2026-11-02): one set of
"find the span" choices for every scenario, one table per inner question, the position picked last,
costs from measured cards per target class, robust to the byte-rate prior, staged under D186.
Evidence: `units_inventory.md` (ids U1-U10, N1-N14, Q1-Q11), `r33_report.md` + `docs/dev/lanes/r33_sim/`,
`t588tri_report.md`, `bar588_report.md` (job 588), `window_site.md` rev 3.3, `walk_vs_v1_record.md`,
`measure_sets.md`, roadmap §0a/A-PLAN/§5; rev 2's recounts in `span_pick/` (over R-33's raw sweep).
`[rev2 B1]` Code cites are the review tree's (884996ef6; no kit code changed to 959c08124).

## Goals

Ranked; a higher goal wins a conflict.

1. **Answers exact** (every caller). Every plan the tables can produce yields exactly the candidates
   its facts define: G2 (`memfn/tests/run_g2_win.sh` and the finder G2) green against the scalar byte
   loop, every plant red; zero corpus answer changes at every stage.
2. **No regime slower beyond noise** (users of the default build; D186's bar). `[rev2 B5]` Stage 1:
   zero movers on EVERY arm (§Staging's witness list), no pcrec abi number change, one MF_SITE_ABI
   (+ MF_CLASS_V) event for the grown reply. Stage 3: each row's movers read new/old <= 1 + the A/A
   floor in every regime of a 588-style run, else the row narrows; a kept loss is an owner-approved
   exception. `[rev2 A2]` The shipped smp20 loss (S3's `cover` row, RTE/DEF 1.58-4.03x) is a Goal-2
   matter: D186's bar applies to shipped rows too; it closes by stage 3's first row.
3. **One table per question** (the next editor; `architecture.md` "One table per slot").
   `[rev2 B3]` After stage 1: six question tables, four pick-side tables (two are defaults that retire
   by census), one named untabled pair (§The tables), whatever the scenarios. Check: a decider census
   per question at each unit's HEAD (deciding functions by grep against their table, `kit_walk` reach
   over the corpus); a second decider that stays byte-identical fails it.
4. **Costs measured, by target class, none hand-set: the END STATE** (owner, D186 add. 1 A1; D176
   Q1/Q3). `[rev2 A1]` No priced departure before its cards are measured; until then a changed pick
   is a hand row. Every cost a priced row reads is a declared row of the stamped set (a check);
   `plan_cost.def`'s Zen 1 rows retire with the last default reading them. `[rev2 D2]` "Class" today
   = the named set or `DEFAULTS` (`idk`).
5. **The measured losses close** (users of common patterns). smp20 `(?i)x/1234`: RTE/DEF <= 1 +
   floor on every job-588 cell, by row ONE-STREAM (§Staging); the six D-hors sites keep their wins
   (RTE/DEF 0.57-0.78). A win is never a requirement.

**Non-goals.** Engine choice, crossings and whole-artifact effects (architecture's rules; engine
pricing stays DEFERRED). The SIMD official verdict. New find methods (V1/M64 stay closed). Run-time
adaptive switching (Boonies). Changing the byte-rate prior (Open question 3).

## The shape

`[rev2 B4]` Six scenarios make the SAME call in stage 1 (DFA prefilter OFS, cover/REPORT, PF find,
VM re-find, MLINE, LMHIT; a pre-check's window-stating parts ride their site's call): facts in, one
complete plan out. Presence (the PRES slot) keeps its own entry until [MEMFN-UNBOUNDED-SPANS] (not
started; its own MF_SITE_ABI event) states unbounded spans; then it joins as the seventh. Inner first:

```
 1 FIXED FACTS   the measurement set (named or DEFAULTS), layer (SIMD on/off), form, handoff,
                 site_kind (the stated consumer kind), alternatives (PARKED/RESEED/NONE), floor,
                 byte rates                                   [rev2 B2: no frame fact here]
 2 CANDIDATES    per alternative: every stated core position after C-meet, not the full set,
                 with its set S, offset d, prior mass, flat mass, table offer, soundness flags
 3 PER CANDIDATE the question tables: T-FIND (method + resume) -> T-VERIFY (step list) ->
                 T-SETTEST / T-CMP forms -> T-FRAME (which renderer serves this plan) => one
                 COMPLETE plan per (candidate, method) whose frame row renders it
 4 PICK, LAST    the default plan (the KEY, M and TIE rows: today's answer), then T-PICK's rows
 then EMIT       renders the plan and its frame row; decides nothing a card covers (roadmap §0a)
```

**The candidate list is data**, built from pcrec's stated spans and the art's byte rates, with
soundness flags: on a RESEED alternative F0 (offset 0) is never the stop (S188, MISCOMPILE-1).
`[rev2 B1]` PARKED readability is NOT a step-2 fact: `rd_set` widens a PARKED plan's reads when
T-VERIFY's C-pin sets the re-seed bit (window.c :251-254, :877-878), so a PARKED candidate's
readability is a T-VERIFY output; stage 1 is unaffected (the PARKED stop is k0).
`[rev2 B2]` Frame validity's effective key is the stated consumer kind (on R-33's sweep the E row is a
function of form, handoff, site_kind and floor; two-member stops are PAIR on REPORT, walked elsewhere).

**A scenario** is stated facts. `[rev2 E1]` PF states span 0 on its PARKED alternative and, on 1,454
of R-33's 1,767 PF sites, a RESEED one with several core positions (`\d{4}`: 0-3). **The trace**
`[rev2 C9]`: every candidate, the rows walked, the default and the deciding row (MFTRACE build);
prices and bands join it only with the first priced row.

## The designer/emitter split

This mechanism IS the kit's planning face (roadmap §0a) and `[rev2 A6]` stage 1 IS A-PLAN's first
step (D186 add. 1 A6): the plan call and the emit call, byte-identical, with the roadmap's ratchet
accounting (§Staging).

| stage | owns | in this design |
|---|---|---|
| pcrec, the designer | facts and legal choices: spans, alternatives with entry, floor, form/handoff/site_kind, byte rates, the measurement set | states them once per site; never a position, method or cost (D157) |
| architecture: the kit's planning face | candidates, the question tables, the pick, (later) the cards | the plan call: facts in, ONE complete plan out (alternative, stop, method, resume, verify, test forms, frame row) plus its trace |
| architecture: pcrec's rules | engine, route, crossings (`next_keys`, FIRST/NEXT rows) | reads the plan reply as NEXT reads the phase-1 reply today (window_site §2.4) |
| emit: the kit's emitting face | rendering | the emit call: plan in, C out; renderers select TEXT by the plan's method and frame row; golden plan-in/C-out tests per seam |

**What moves across.** The reply grows from window_site's phase-1 reply by the method, resume and
frame row, which the text call re-decides today (`fd_find` in phase 2, `fn_rows` BODY, Table E).
`[rev2 B5]` One MF_SITE_ABI (+ MF_CLASS_V) event, NO pcrec abi event (window_site §5.2).

**A-PLAN's open points.** `[rev2 A6]` (1) is NOT settled here: stage 1 returns one plan as the
INTERIM (byte-identical; prices exist nowhere yet); the reply grows a bounded, priced set when
[PRICE-BAKEOFF] opens (Open question 1). The landmark end state (§pcrec-side findings) reads the
kit's price only then. (2) Helper sharing stays emit's, declared cost-free. (3) Run-time dispatch
stays held. (4) Cards are tables keyed by class and regime. (5) `--memfn=no-X` denies become filters
on T-FIND and T-PICK rows inside the plan call; the namespace is unchanged (D147 add. 9). (6) The
same-commit abi rule is unchanged.

## The tables

`[rev2 B3]` The stage-1 inventory, every decider with its home. Rows say what is VALID; price and
dominance are separate. Each table answers as today in stage 1.

| # | question | form and rows (stage 1) | replaces |
|---|---|---|---|
| T-FIND | how to find the next member of S at d, and where to resume | first-match `kit_table`; rows carry a RESUME action column `[rev2 SLOT-9]` (Horspool: D-shift, its admission D-hors's holds kept; every other row: D-one `c + 1`); D1c, PAIR, D1, D1w, R7w; SIMD forms are rungs of a row at `-fmemfn-simd` `[rev2 C7]`; validity READS T-FRAME's row contracts `[rev2 B2]`; inert R8/R3a/R3b/R4/R1/R2 deleted `[rev2 C8]` | Q3's `fd_route`/`fd_find`/compose `arms[]`, Table D, T-RESUME |
| T-VERIFY | which other positions to test, in what order and grouping | `[rev2 B1]` a DECLARED STEP LIST read in order, every holding row applying (Table C's cumulative steps C-floor or C-yes, C-model or C-none, C-pin, C-stop, C-run, C-asc), not first-match; `[rev2 SLOT-2]` its first step is the run member (`run_member`, tie row T_MASS_STRETCH, computed before Table C's rows as today), an output of the plan | Q5, PRES part ordering and ofsskip's legacy plan where byte-identical (U10) |
| T-SETTEST | how one byte's membership is tested | offered `T[b]`, then `kit_set_test`; C-table/C-own live HERE only, T-VERIFY reads them `[rev2 B1]` | Q11, `member_test` |
| T-CMP | how a literal stretch is compared | runcmp's rows (`rc_row_of`); `[rev2 B1]` generic.c's per-byte RUN chain stays a SECOND decider until U8's unit change | Q6 |
| T-PRES | which required members a presence pass tests | the PRES rows (P0, P2, P3, P4, P9); `[rev2 B1]` precheck's three renderers (`gate`, `landmark`, `set_rest`) are T-PRES's rendering, not T-FIND's (N9); `[rev2 SLOT-10]` D176 Q4's fold is a T-PRES row reading the plan's stop, landing as its own choice change | Q9 |
| T-FRAME | which renderer serves this complete plan | `[rev2 B2]` Table E (`wf_erows`, legacy first, order kept) asked at PLAN time per complete plan; its answer is a plan field the emit face reads | Q8, the E-row half of phase 2 |

Pick-side tables: **KEY** (`[rev2 SLOT-3]` Table A's five rows: A-empty, A-parked, A-model, A-mass,
A-floor; the RESEED default with no `scan_ok` walked span is A-floor's "no stop", 1,420 of R-33's
1,835 RESEED alternatives; A-empty has no population in the sweep, its reach owed); **M** (MARGIN,
M-one, M-parked); **TIE** (`wf_ties`, plus `[rev2 B1]` a NEW presence-member row: pattern order, then
the larger byte, for `tie_over`; plus `[rev2 A3]` T_BAND -> TIE_DEFAULT for priced rows); **T-PICK**
(arrives with stage 3's first row `[rev2 C9]`). KEY and M are the DEFAULT; each retires only when a
census shows no class reads it, as its own no-mover step `[rev2 C3]`.
Untabled, named: vrun's KA/KB (U7) are SIMD-rung parameters, kept (they move SIMD-on bytes).
`[rev2 B1]` OFS sites state no consumer kind (381 of 381 FUNC/handoff-0 window sites in the sweep:
site_kind UNSTATED), every T-FIND row reads it, so T-FIND declines there: the RESEED KEY row keeps
`scan_ok`'s one-member test itself, and `fn_rows` BODY (cube -> fn-pair, else fn-memchr) stays a
decider until pcrec states a kind on OFS sites (a pcrec-side MF_SITE_ABI event, §pcrec-side findings).

**Growth rule.** A new scenario adds no table; a new method adds a T-FIND row plus its card (D176).

## The pick

`[rev2 C3, C9]` **Stage 1: no prices.** The default plan is TODAY's complete plan: the KEY row's
position, T-FIND's first match there, M's alternative, TIE's order. Stage 1 builds the defaults and the
trace only; no pick code reads a cost other than the KEY/M rows' existing `plan_cost.def` integers,
whose truncation order (C-model's) is preserved for byte identity `[rev2 B5]`.

**Stage 3: T-PICK rows.** Each row: a condition on stated facts, the LEVELS it opens (method,
position, alternative) `[rev2 C3]`, an action, its deny, its per-regime evidence (D186: a choice
change is a row). `keep` is the last row. Until the cards are measured every action is a RULE
(A1); the first is ONE-STREAM (§Staging). The condition is tested before any card key is looked up,
so a site the row does not admit never consults the set `[rev2 D1]`.

**The priced action (the end state; only after stage 2, one row at a time, A1).** A row's action may
be a priced comparison:
1. Candidates are the complete plans that differ from the default only at the row's levels, each
   priced under P (the committed prior) and F (flat, `m_F(S) = |S| x 1e6 / 256` ppm `[rev2 C1]`),
   each with a band.
2. `[rev2 C3]` ONE comparison of each candidate against the default complete plan (no per-level
   stickiness; the levels only order the trace). A candidate QUALIFIES only if cheaper than the
   default beyond the band under BOTH P and F.
3. `[rev2 A3]` Among qualifiers: the least worst-case ratio `max_r price_r(c) / price_r(default)`,
   then TIE. A default within band of every candidate is TIE's row T_BAND -> TIE_DEFAULT: D176 Q5's
   "within the band, the declared tie rows decide" holds to the letter, and the row's content (the
   incumbent stands) is D186's "keep the choice that is never badly wrong".
4. `[rev2 C3, C2]` Unpriced default (its method has no card): keep. Unpriced candidate (no card, or a
   card without noise): cannot qualify; a missing `noise_e6` is UNMEASURED, never 0.
5. `[rev2 C3]` A renderer addition that flips a T-FIND first match moves the DEFAULT, so it is its own
   choice change with its own row and evidence, never a side effect.
6. `[rev2 C7]` Only scalar plans are compared; SIMD forms are rungs inside the chosen scalar plan
   (D147), so a SIMD-on compile never picks another stop or alternative.

**The price of a complete plan** `[rev2 C1, C6]`: in the set's unit (the scalar walk's per-byte
cost, D176 Q1) per 1e6 subject bytes; masses in ppm; card values `value_e6` integers; each term
computed exactly and rounded half-up once at its end (D176 Q5: integers; no per-factor truncation, so
`m x prod pass` never vanishes for a rare set). Under rate model r:

```
 stream methods (memchr, memchr-back, PAIR): streams x byte(method) x 1e6
                                           + m_r(S) x (hit(method) + verify_r)  + passes_r x enter
 walk:                                       byte(walk) x 1e6
                                           + m_r(S) x (hit(walk) + verify_r)    + passes_r x enter
 Horspool:   (1e6 / E_r[sh]) x (probe + q_r x (hit(hors) + verify_r))           + passes_r x enter
   verify_r = sum_i cmp(form_i) x prod_{j<i} pass_r(j);  pass_r(j) = m_r(set_j) / 1e6
   passes_r = m_r(S) x prod_i pass_r(i);  enter = enter(consumer kind, entry fact)   [rev2 C4]
   E_r[sh]  = sum_b rate_r(b) x sh[b] / 1e6 over Horspool's shift table for the window
              (a byte in no window position shifts the full window w); q_r = m_r(S_last) / 1e6
```

`hit(method)` is per candidate RETURNED, measured as the method's own slope over hit density, so a
PAIR's second stream is in its measured `hit(PAIR)`, not a formula factor `[rev2 C1]`. Horspool pays
its candidates inside its own line, never the stream lines too `[rev2 C6]`. Positions are
independent (an ASSUMPTION; model error is outside the band, §Robustness).

## Cost cards

**What is measured** (one card per quantity, regime named, `measure_sets.md` §7.2 shape):

| card | per | regime | replaces |
|---|---|---|---|
| `find.byte` per method (memchr, memchr-back, PAIR, walk; each SIMD form its OWN row, no layer column `[rev2 C7]`) | byte scanned | miss-only stream, fresh long buffer | C_MEMCHR, C_BITMAP |
| `find.hit` per method | candidate returned and restarted | slope over hit density, periodic and random landings | the ASSUMED H_HIT |
| `hors.probe` `[rev2 C6]` | Horspool probe (load, table read, shift) | miss-only, the window's shift distribution | — (no card today) |
| `verify.cmp` per T-SETTEST form, per T-CMP row x length class | one compare | pass rate 0 and 0.5 | C_VERIFY (UNMEASURED), C_MISPRED |
| `enter` per consumer kind x entry fact `[rev2 C4]` (PARKED resume, RESEED re-seed, NONE) | candidate passed on | false-start survival measured | C_ENTER (MEASURED x ASSUMED) |

`[rev2 C4]` MARGIN (2x, ARGUED) stays the alternative default until the two `enter` cards exist; a
PARKED-vs-RESEED priced row needs both. `[rev2 B1]` MAX_SET is not a card and U9 leaves stage 1: the
kit may not read pcrec's `limits.def` (memfn/CLAUDE.md), so the duplicate is closed at its own unit
by a grep of `PCREC_OFSK_MAX_SET`'s readers (pcrec states it as a fact, or pcrec's copy retires).

**Noise reaches the kit** `[rev2 C2]`. Today `mf_measure` has no noise field and the committed set's
68 kit rows carry `noise_e6` '-'. Stage 2 owes: a kit request (main files it), a noise field (an MF
abi event with its `measures.md` §4 and match_api hunks), a producer that writes it, and a noise rule
for derived rows (propagated from their inputs in quadrature through the row's formula).

**Where they live** `[rev2 D3]`. A set names ONE method version, so the span cards are quantities of
the grid's successor method (`kit-grid@2`, grid2's cards) and the grid keys are re-measured under it;
the job is grid-sized, not "one short job". It lands as a new REVISION of the box's set (D176 Q3:
`zen4-grid1` rev 2), gated on the step-0 census; whether a revision may carry a successor method
version is measure_sets' question, asked of main before the job (if not: a new id, said as a
departure from D176 Q3). Embedded by `make gen-measures`, handed on `mf_art_begin`.

**Chosen by the set, not the host** `[rev2 D2]`. A compile names a set (`--measures=NAME`) or reads
`DEFAULTS`; no option declares a class, so an unnamed compile uses `idk`'s set (`zen4-grid1@1`,
`measures.md` §5¶6): a conscious choice. A class option goes to [IFACE-PUSH] (plan row 2).

**Measured how.** Timing jobs through the box queue (`idle-ok`, quiet-gated, windows cleared with the
owner): dev box first, ubuntubudu by slot request, the Mac directional; uncarded = UNMEASURED.
`[rev2 D5]` Cards are long-subject per-byte quantities, so a priced pick is a long-subject pick;
search_short/match stay row evidence, and a per-call term is owed before a priced row with per-call movers.

## Robustness to the byte rates

**The weakest input is the prior.** PRIOR_AUTHORED (`a322116b1b87f9f6`) rates {x,X} at 1,097 ppm and
'/' at 4,154; job 588's subjects held x 2,338 against '/' 1,026 candidates on real text, 1,388 vs 0
on none, 21,788 vs 10,856 on random (t588tri §a). The walk-vs-V1 ruling is the precedent: when the
evidence cannot say, keep the choice that is never badly wrong.

**The rule.** Two rate models, P and F; a candidate must win under both, beyond the band. F is the
absence of a guess about text, so a departure that survives F does not rest on the prior alone.

**The band is measured, not tuned.** A price's band is the quadrature sum of each card's noise times
its coefficient in the price; `[rev2 C2]` no constant appears except the card gates (kit-grid@1's
`gate_e6` 3 %, an UNMEASURED DEFAULT, D149). Model error (independent positions, landing regime) is
NOT in the band: each priced row's run prints predicted vs measured per mover (R5.3), and the spread
of that ratio is the model-error term the NEXT priced row adds to its band.

**What the formula says for smp20** `[rev2 C1]` (recomputed, `span_pick/onestream.out`; Zen 1
`plan_cost.def` constants scan 0.06, verify 2.5, enter 20, hit 20 c; verify in ascending mass):

| model | {x,X} PAIR, hit(PAIR) = 20 | {x,X} PAIR, hit(PAIR) = 40 | {/} memchr |
|---|---|---|---|
| P | 144,694 ('/' loses by 6.1 %) | 166,634 ('/' wins by 8.6 %) | 153,477 |
| F | 295,858 | 452,108 | 147,929 |

F favours '/' 2:1 either way; under P the verdict turns on `hit(PAIR)`, a card nobody has measured
(R-33's 8.6 % was its per-stream reading). That is why smp20's fix is a hand row (A1, A2), not a
price, and why a drop-F plant cannot reach smp20 (§The independent control).

**Uncovered by F** `[rev2 C5]`. Where real text is far from BOTH the prior and uniform text (UTF-8
lead bytes, case-folded letter pairs, dense classes the prior under-rates), P and F agree wrongly
(R-33's bench `utf8/alt-cyr-64`, {\xd0,\xd1}). Any priced row over two-member stops is gated on a fix
(an encoding fact, or a third, adversarial rate model).

**The multi-variable risk.** Cards measured in isolation (never fitted to end-to-end timings or set
from a validation site), two fixed rate models, a band from the cards' own noise: nothing is tuned;
a mispick is fixed only by a corrected measurement, a missing carded term or a corrected validity
row. Hand rows carry no fitted input. Drift gauge: D186's pilot distance (0.981), per stage-3 row.

**Horspool** `[rev2 C6]`. With `hors.probe` and `hit(walk)` defined and carded, priced Horspool is
decided by measured cards; until then the D-hors row stays the default and HORS_MIN its holds.

## Staging under D186

D186 (TRIAL): a UNIT change (a better unit inside its cases; bar: no regime slower) or a CHOICE change
(a row on stated facts with per-regime evidence; a losing regime narrows the row).

**Stage 1: unify, today's answers kept: A-PLAN's first step** `[rev2 A6, E3]`. Neither kind: a
no-mover refactor. Separable units, each with its own byte-identity witness; a unit that cannot be
byte-identical leaves stage 1 and lands alone as a unit change with its own deny.

| unit | content | deletes |
|---|---|---|
| 1a dead code | N3 `mf_set_terms`; the inert finder rows R8/R3a/R3b/R4/R1/R2 (zero reach by code, PREMISE probe) | 7 members |
| 1b primitives | U4 one mass primitive (named capped/uncapped argument; `window_mass` keeps a NONE-mode total: one floor over the total, 62,500, not a sum of floors, 62,496 `[rev2 B1]`); U5 `wf_ties` the one tie table plus the presence-member row | 2-3 mass variants, 1 tie rule |
| 1c kit-only spellings | U2 presence.c P3 `run_scan` asks `run_member`; U6 the kit's landmark shadow (presence.c :222-245) retired if no census reads it | 1-2 |
| 1d planning core | one candidate builder; KEY/M/TIE as the default; T-VERIFY as a step list with the run member; trace without prices (U1 as two KEY rows, U10, N1, N6) | `a_model_choose`'s private enumeration, `mass_domain`'s copy |
| 1e plan/emit split | the reply grows (method, resume, frame row); T-FRAME at plan time; compose `arms[]`, B-fn, `fd_find`'s text become renderers keyed by the plan (U3 less OFS, N4, N5, N11); one MF_SITE_ABI (+ MF_CLASS_V) event, no pcrec abi event | B-fn's reconciliation; `SF_WINDOW_STOP` as a stop fact |

Not in stage 1 `[rev2 B1]`: U8 (a unit change: generic.c's chain can never match runcmp's rows), U9
(the boundary, above), N9 (stays T-PRES's rendering), OFS's `fn_rows` BODY (a pcrec-side
prerequisite), U7/N10 (SIMD-on bytes).
**Witness, per unit** `[rev2 B5]`: window_site §5.2's list: `scripts/emit_sweep.py` byte-identical
over the corpus, the bench patterns and job 588's sample on EVERY arm (default, each `--memfn=no-X`
deny, `--engine=vm`, both SIMD layers), stamps included; `tests/findings/manifests/*_movers.txt`
unchanged; reach floors; G2; plus Goal 3's decider census. Counted pcrec-side from artifact diffs.
**Ratchet** `[rev2 A6]` (roadmap §5). A-PLAN's entry says the split "deletes nothing in §5 today", so
the kit's duplicates join §5 as rows counted at stage 1's base (proposed for main, recipes written by
the unit's lane at the base): find-method deciders (`fd_route`, `fd_find`, compose's method walk,
`fn_rows` BODY, `b_fn_holds`; members − 1), position enumerators (`mass_domain`, `a_model_choose`'s
scan), kit mass variants, tie rules, kit run-member spellings, the landmark shadow, inert finder rows. Each unit lowers its row and raises none; stage 1 adds no
member (T-PICK waits for stage 3; T-FRAME is Table E moved; the candidate builder replaces two).
**Sequencing** `[rev2 E2]` (D153: in-flight refactors first): while stage 1 is in flight, opt rows
touching window.c, finder.c, ofsskip.c, compose.c or presence.c carry "remodel overlap" and wait,
smp04's unit change included, unless the owner rules otherwise.

**Stage 2: measure the cards** (§Cost cards; noise channel, method version, step-0 gate). No reader,
no consult, zero movers, stamps unchanged. `[rev2 D3]` Under D77 and measure_sets §7.3's reader
closure, the leaning is to run it when its first reader (a priced row) is chartered (Open question 2).

**Stage 3: choice rows, one per change.** Each: one T-PICK row naming its levels, a deny with a D174
behaviour name (spec home `registry.md` §6¶8a, listed by `cli.md` §2.4¶1) `[rev2 E2]`, a 588-style
run of RTE vs the row denied (every regime and subject class, A/A floor, both layers, scalar the bar),
a movers census from artifact diffs with stamp-only movers as their own class `[rev2 D1]`, its own
pcrec abi event and spec hunk. Hand rows need only stage 1d; priced rows need stage 2.

**Row 1, ONE-STREAM** `[rev2 A2]`, the poster child of the finished refactor (D186 add. 1 A2):
- **Opens** level (b), the position, on a no-entry (NONE) alternative. **Deny**
  `--memfn=no-single-byte-stop`.
- **Condition** (stated facts only: entry, the candidates' sets, the art's byte rates): the default
  stop (KEY A-mass: least prior mass, ties as today) has a set of k >= 2 members, and some candidate
  has ONE member whose prior mass is <= `k x 1e6 / 256` (the default's flat mass, floored).
- **Action**: stop at the least-prior-mass such one-member candidate (ties as A-mass); T-FIND,
  T-VERIFY and T-FRAME then answer for it as for any stop. Reads no card: no consult, stamp unchanged.
- **Why the bound** (no constant): the default is a k-stream or walk search whose candidate count on
  unknown text is its flat mass; the one byte is refused only when the prior positively says it is
  denser than that. The prior never has to rank x against '/'.
- **Check on smp20** (prior `a322116b1b87f9f6`): default @0 {x,X}, k = 2, 1,097 ppm; bound 7,812;
  one-member candidates '/' @1 4,154 and '1'..'4' @2-5 7,476 each, all under it; least is '/', so
  the stop is @1 {/}: DEF's stop (t588tri: DEF runs memchr on '/'). `span_pick/onestream.out`.
- **Population** (R-33's sweep: corpus 5,014, bench 392, job 588 2 x 43 compiles): 1,637 NONE
  alternatives; 1,056 with a one-member default (cannot hold); 577 refused (no one-member candidate
  under the bound); the row holds on 4 units, 3 patterns, all COVER: smp20 (job 588 and corpus
  c02129); pr09 `x[Q%]y` @1 {%,Q} 481 ppm -> @0 {x} 997; c04989 `x[\x{e0}-\x{ff}]y` @1 32 bytes 64 ->
  @0 {x} 997 (bound 125,000). R-33's other R4 sites and the R5 parts are refused.
- **Evidence.** Motivating: job 588 smp20 RTE/DEF throughput real 1.663, none 2.793, random 4.028,
  search_short real 1.578 (DEF also changes the route, so it is confounded). Acceptance: the row's own
  run over its three movers (pr09 is in job 588's set; c04989 joins the pattern list), RTE vs the deny,
  every regime <= 1 + floor. pr09 and c04989 are the HELD-OUT class `[rev2 D4]` (not the motivating
  site). A losing held-out regime narrows the condition (e.g. to k = 2) and the run repeats; smp20
  must also close Goal 5 against DEF.
- **Moves** the three patterns' artifacts: a pcrec abi event (the next number at landing, readers by
  grep), its movers census, the deny row and the spec hunk. G2 and every `.rxt` answer unchanged.

**Later rows, each its own change and its own prerequisites** (none scheduled):
- Horspool priced (D176 Q2; deletes HORS_MIN): `hors.probe`, `hit(walk)`; witnesses hex8-bounded and
  the five other D-hors sites.
- RESEED admission at any set size: `[rev2 E1]` its population is PF E-stmt sites, where PAIR has no
  renderer: needs [MEMFN-PAIRSTOP] (or the row is walk-only) and both `enter` cards (MARGIN goes then).
- Dense pairs: [MEMFN-PAIRSTOP] first (a unit addition, then its own choice row for the flipped first
  match), gated on the C5 fix.
- Offset-0 RESEED stops stay excluded (`[rev2 A4]` the kit's call; one unconfounded timing reopens).
- smp04 `[a[:b]`: a UNIT change (T-SETTEST table form), own deny and regime run, after stage 1 (D153).

**Re-measuring** is a deliberate data change: §What moves when the data is regenerated.

## What stage 1 deletes

Every duplicate (inventory §4) and neither-kind item (§3), by id, with its unit `[rev2 B1, E3]`.

| id | stage 1 does | unit | later |
|---|---|---|---|
| U1 | one candidate builder and pick; A-model and A-mass stay as two KEY rows | 1d | ONE-STREAM admits smp20's departure; KEY rows retire by census |
| U2 | P3's `run_scan` asks `run_member` (one tie rule) | 1c | pcrec's two: §pcrec-side findings |
| U3 | T-FIND asked once per candidate; arms/B-fn/`fd_find` text become renderers; NOT on OFS (no kind) | 1e | OFS joins when pcrec states a kind |
| U4 | one primitive, NONE-mode total kept | 1b | pcrec's findings.c copy stays (D157) |
| U5 | `wf_ties` the one table, plus the presence-member row | 1b | pcrec's PICK: finding |
| U6 | the kit's shadow retired if no census reads it | 1c | pcrec owns admission (D167) |
| U7, N10 | KEPT (SIMD-on bytes) | — | a SIMD-layer choice change: KA/KB from the plan |
| U8 | NOT in stage 1: a unit change, own deny, regime run | — | T-CMP then one decider |
| U9 | NOT in stage 1: the kit/pcrec boundary | own unit | closed by a reader grep |
| U10 | T-VERIFY the one plan; PRES/ofsskip's legacy text render it where byte-identical | 1d | — |
| N1 | split into candidates + C-model + the RESEED KEY row; same arithmetic | 1d | a priced row |
| N2 | MARGIN kept as M's default | — | after both `enter` cards |
| N3 | deleted | 1a | returns only as a carded T-FIND form |
| N4 | no longer a stop fact; T-FIND reads T-FRAME's contracts | 1e | [MEMFN-PAIRSTOP] |
| N5 | a renderer keyed on the plan | 1e | — |
| N6 | candidates -> T-FIND -> T-VERIFY -> T-FRAME -> default; same answers | 1d | priced rows |
| N7, N8, N13 | kept (D-hors holds; PARKED KEY; Zen 1 integers) | — | priced rows after stage 2 |
| N9 | stays: T-PRES's rendering | — | — |
| N11 | Table E becomes T-FRAME, order kept | 1e | legacy rows retire by evidence |
| N12 | vany: a T-FIND SIMD form, declined (no card) | — | live when carded |
| N14 + R4/R1/R3a | deleted on the zero-reach proof `[rev2 C8]` | 1a | — |

## pcrec-side findings (for main; not changed here)

- **Run pin and scan index**: `pcrec_find_run_scan_index` (findings.c :745), `_window_start` (:780)
  and `pcrec_run_pin` (kset.c :294) restate the run member, held by `req_run_member` (emit_dfa.c
  :1058, loud); end state: pcrec reads the plan reply.
- **Landmark admission**: `req_landmark_admits` (emit_dfa.c :9064) and lmwalk's `lc_rarity` share
  `pcrec_landmark_margin`, lmwalk adds `LMWALK_K_HIT_UNMEASURED`; end state: pcrec states the landmark
  as a candidate and reads the kit's price once the reply carries prices (`find.hit` replaces K_HIT).
- `[rev2 B1, B4]` Prerequisites stated pcrec-side: a consumer kind on OFS sites (an MF_SITE_ABI event;
  U3 on OFS waits for it); [MEMFN-UNBOUNDED-SPANS] (presence joins); [MEMFN-PAIRSTOP] (later rows).
  `next_keys` and lmwalk's route stay architecture rules outside this per-site mechanism.

## The measurement regime

RELEVANT. Each card names its regime (§Cost cards): miss-only streaming (`find.byte`, `hors.probe`);
hit-density slope in periodic and random landings (`find.hit`; landing flips walk vs stream choices,
walk_vs_v1 §3); pass rates 0 and 0.5 (`verify.cmp`); consumer kind x entry fact (`enter`). Per set:
box, compiler, Linux verdicts, `taskset`-pinned, scalar the bar. Prices are long-subject; per-call
regimes are row evidence. The byte rates are the regime the compile cannot know (P vs F). Row
evidence regimes are job 588's: throughput, search_short, match x real, none, random, dense.

## The independent control

RELEVANT.
- **Answers:** G2 against the scalar byte loop; the `.rxt` oracle under every committed set plus
  synthetic extreme sets forcing each T-FIND row (`measure_sets.md` §8), giving each row a population.
- **Stage 1:** per unit, the §Staging witness (every arm, stamps, movers manifests, reach floors),
  counted pcrec-side from artifact diffs, never from the kit's `moved` (K35); R-33's probe is a
  diagnostic only. Goal 3's decider census is read at review.
- **Stage 3, hand rows:** the row's own 588-style run over its movers census (from artifact diffs),
  with a held-out class `[rev2 D4]`; ONE-STREAM's census in this note was recomputed from R-33's raw
  sweep by a script that shares only the candidate builder with R-33 (`span_pick/`).
- **Priced rows:** predicted price vs measured time per mover (R5.3); validation sites share no number
  with the cards (R5.2). `[rev2 D4]` The drop-F plant's witness is a site where P admits a challenger
  and F refuses it (a dense two-member stop), chosen with the cards; never smp20, where F already
  favours '/' 2:1 so dropping F cannot change the verdict. A swapped-cards plant moves a reach witness.
  `[rev2 D1]` finder_check.py checks D and F (no row reads a key; `consulted` 0) get their true arms in
  the first consulting row's change; the keys a pick read are counted pcrec-side (the stamped set
  against the artifact's trace), not by the kit's consult recorder.

## What moves when the data is regenerated

RELEVANT. Generated C carries no cost, so only picks and the `<PREFIX>_MEASURES` stamp move.
`[rev2 D1]` The stamp is "" today on every artifact; it becomes `id@rev:digest` on every artifact
whose pick consults the set (found or absent), and changes on every later card rev, with or without a
pick change: stamp-only movers are their own census class, counted and re-pinned, never judged as
choice changes. Because a T-PICK condition is tested before any key lookup, only sites a priced row
admits consult. A byte move is an abi event (D76/D94, readers by grep, the byte-count class included)
with its movers census, each moved pick judged per regime as a choice change; `measures.md` §8/§5
take their hunk when a set or default changes (D80).
Stage 1 moves no byte (an MF_SITE_ABI event only); stage 2 moves nothing; ONE-STREAM moves its three
patterns' bytes and no stamp.

## Disposition of review 2026-11-02 r1

Every consolidated id (each critic id maps to one in the review's by-id table). FIX-NOW and E3 applied
per the rulings; A1, A2, A6 per D186 addendum 1.

| id | disposition | landed in |
|---|---|---|
| A1 | owner answered (add. 1 A1): priced costs are the end state; no priced departure before cards; hand rows until then. Trigger sentence corrected (the pick's pricing is per-row, after stage 2) | Goals 4; §The pick (stage 3, priced action); §Staging stage 2/3 |
| A2 | owner answered (add. 1 A2): no interim narrowing; ONE-STREAM is stage 3's first row, defined, checked, censused, evidenced; Goal 5's smp20 part ranked under Goal 2 | Goals 2, 5; §Staging row 1 |
| A3 | FIX-NOW: TIE row T_BAND -> TIE_DEFAULT, qualifier choice by worst-case ratio on both models, D176 Q5 + D186 cited | §The tables (TIE); §The pick step 3 |
| A4 | FIX-NOW: open questions rebuilt (owner-level only); rev 1's Q1 answered by D186, Q4 the kit's call, Q5 = [MEMFN-PAIRSTOP] (D176 Q6), Q2 dropped (D2 covers today's case) | §Open questions; §Staging later rows |
| A5 | DOC: the prior change is Open question 3 with a source sharing no subject with job 588; ONE-STREAM does not depend on the prior's x-vs-'/' ranking | §Open questions 3; §Staging row 1 "Why the bound" |
| A6 | owner answered (add. 1 A6): stage 1 IS A-PLAN's first step; ratchet rows proposed; A-PLAN point 1 left open (one plan = interim) | §The designer/emitter split; §Staging stage 1; §Open questions 1 |
| B1 | FIX-NOW: per item: N9 T-PRES; U8 unit change; OFS no kind (KEY keeps `scan_ok`, BODY stays); Table C a step list; C-table/C-own T-SETTEST only; PARKED readability a T-VERIFY output; U5 new row; U4 NONE total; U9 out; A-floor/A-empty rows | §The shape; §The tables; §Staging; §What stage 1 deletes |
| B2 | FIX-NOW: option (i): Table E becomes T-FRAME at plan time, its answer a plan field; T-FIND validity READS its contracts; no frame fact in step 1; effective key = stated consumer kind | §The shape; §The tables |
| B3 | FIX-NOW: true inventory (6 + 4 + KA/KB), run member a T-VERIFY output, T-RESUME folded into T-FIND, presence fold a T-PRES row, decider census as Goal 3's check | Goals 3; §The tables |
| B4 | FIX-NOW: presence keeps PRES in stage 1 (six scenarios); [MEMFN-UNBOUNDED-SPANS], [MEMFN-PAIRSTOP] named | §The shape; §pcrec-side findings |
| B5 | FIX-NOW: stage 1 = one MF_SITE_ABI (+ MF_CLASS_V) event, no pcrec abi event; window_site §5.2 witness list per unit; KEY/M keep plan_cost.def integers and truncation order | Goals 2; §The designer/emitter split; §Staging |
| C1 | FIX-NOW: hit per candidate returned (PAIR's cost in its own card), F in ppm, Horspool term defined, rounding stated; smp20 predictions recomputed with the formula | §The pick (formula); §Robustness table |
| C2 | FIX-NOW: missing noise = UNMEASURED; noise channel owed in stage 2; derived-row rule; "no constant except the card gates"; model error handled outside the band | §The pick 4; §Cost cards; §Robustness |
| C3 | FIX-NOW: default = today's complete plan; one comparison per candidate vs the default; KEY/M retire by census; renderer flips are their own rows; unpriced default keeps; rows name levels | §The pick; §The tables |
| C4 | FIX-NOW: `enter` keyed by entry fact; MARGIN kept until both cards exist | §Cost cards; §Staging later rows |
| C5 | PLAN: class named uncovered; dense-pair and two-member priced rows gated on an encoding fact or a third model | §Robustness; §Staging later rows; plan row below |
| C6 | FIX-NOW: `hors.probe`, `hit(walk)` defined and carded; Horspool's line excludes the stream lines | §The pick; §Cost cards; §Robustness |
| C7 | FIX-NOW: only scalar plans compared; SIMD forms rungs; cards keyed per method, SIMD forms their own rows | §The pick 6; §Cost cards |
| C8 | PLAN (applied as stage 1a): the six inert rows deleted on the zero-reach proof | §The tables; §Staging 1a; §What stage 1 deletes |
| C9 | FIX-NOW: stage 1 builds defaults and the trace only; T-PICK arrives with row 1 | §The shape (trace); §The pick |
| D1 | FIX-NOW: condition before key lookup; stamp-only movers their own class; checks D/F replaced at the first consulting row | §The pick; §The independent control; §What moves |
| D2 | DOC + PLAN: unnamed compile = DEFAULTS (conscious); class option for [IFACE-PUSH] | Goals 4; §Cost cards; plan row below |
| D3 | FIX-NOW: kit-grid@2 quantities, new revision (D176 Q3), step-0 gate, grid-sized job | §Cost cards; §Staging stage 2 |
| D4 | FIX-NOW: drop-F witness at a site where F refuses a P winner; held-out class for row 1 (pr09, c04989) | §Staging row 1; §The independent control |
| D5 | PLAN: a long-subject pick; per-call term owed before a priced row with per-call movers | §Cost cards; plan row below |
| E1 | FIX-NOW: RESEED-admission row needs [MEMFN-PAIRSTOP] or walk-only; PF statement corrected (1,454 of 1,767) | §The shape; §Staging later rows |
| E2 | FIX-NOW: D153 cited for sequencing (remodel overlap, smp04 waits); denies get D174 names, spec home registry.md §6¶8a / cli.md §2.4¶1 | §Staging |
| E3 | PLAN, adopted: stage 1 as units 1a-1e, each with its own witness | §Staging stage 1 |
| F | sibling: PLAN (plan row 4 below); unlocks: NOTED (analysis-bundle rate model, per-stretch level, target-set arms, derived crossovers) | — |
| Lessons 1-3 | NOTED: applied by the review's ruling commit; lesson 1 applied here (every quoted number recomputed) | `span_pick/` |

**Plan rows for main to file** (text only; this lane writes no plan.md): (1) [SPAN-PICK-UTF8] the C5
class, trigger: the first priced row over two-member stops. (2) a class-declaring compile option, for
[IFACE-PUSH]. (3) [SPAN-PICK-PERCALL] a per-call term and card, trigger: a priced row whose movers
include a per-call loss. (4) [PICK-IDIOM] one "admission table + declared default + priced action"
idiom across the D157 boundary (lmwalk, T-PICK, [PRICE-BAKEOFF]'s shape), trigger: the first priced
row or the bake-off's revisit. (5) the ratchet rows of §Staging, at stage 1's go.

## Open questions

`[rev2 A4]` For the owner, plain words, each with a leaning.

1. **What the kit hands back.** After stage 1 the kit tells pcrec its one chosen plan for each search.
   Later, pcrec's own planner could compare the kit's options against other ways of matching, which
   needs the kit to hand back a short list of options with their costs instead. Hand back one plan
   for now and switch when that comparison work starts, or build the list now? Leaning: one plan now;
   a list nobody reads would be built ahead of need, and stage 1 stays byte-identical either way.
2. **When to measure the costs.** The fixes now planned are hand-written rules (like the `(?i)x/1234`
   one) and need no measured costs. Measuring them takes a large timing run per machine. Measure right
   after stage 1, or only when a fix first needs prices (when hand-written rules start to disagree)?
   Leaning: wait for that need; nothing would read the numbers before then, and they would age.
3. **The built-in letter frequencies.** When pcrec knows nothing about the text it assumes fixed
   frequencies, which call '/' about four times as common as 'x' and 'X' together; the job-588 texts
   say the opposite. Revisit them from a large sample of real text that shares nothing with our timing
   tests, or leave them? Leaning: leave them for now; the `(?i)x/1234` rule does not depend on them,
   and a change moves choices across the whole corpus. Revisit when a second loss traces to them.

## STATE AT HANDOFF

OWED none. Design lane: rev 2 of this note, `span_pick/` (two recount scripts over R-33's raw sweep,
their outputs, its CLAUDE.md) and the index line in `docs/design/memfn/CLAUDE.md`; no make, timing,
compile or code. Re-run: `python3 -I span_pick/onestream.py docs/dev/lanes/r33_sim SWEEP` and
`span_pick/counts.py SWEEP`, SWEEP = `/var/tmp/pcrec-pcrec/scratch/memfn/r33/sweep/sweep.jsonl`
(re-made by R-33's job 240). Not a build go: next is the re-check round on rev 2 (D186 add. 1 A6).
