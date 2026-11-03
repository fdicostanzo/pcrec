# span_pick — the kit's ONE "find the span" choice mechanism (design, rev 4)

**Status: PROPOSED, rev 4 (lane spanpick4, 2026-11-02). Design only: not a build go, no code, no make,
no timing.** `[rev4]` Carries the owner's rulings since rev 3 (D186 addendum 2: minimax blind pick,
D186 over D144 item 3, C9; one plan with its trace; main's rev 3.1 answers; O3 = wait) over rev 3
(review 2026-11-02 r2 and D186 add. 1 as amended: A2, smp20 a WATCHED witness). Read §Owner rulings
since rev 3 and §The watched witness first; rev 4 text is marked `[rev4]`, rev 3's `[rev3 <id>]`
marks stay. Evidence: `units_inventory.md` (U1-U10, N1-N14),
`r33_report.md` + `docs/dev/lanes/r33_sim/`, `t588tri_report.md`, `bar588_report.md` (job 588),
`window_site.md` rev 3.3, `measure_sets.md`, roadmap §0a/A-PLAN/§5; `span_pick/` (recounts, witness
compiles). Code cites are the r2 review tree's (959c08124).

## Goals

Ranked; a higher goal wins a conflict.

1. **Answers exact** (every caller). Every plan the tables can produce yields exactly the candidates
   its facts define: G2 (`memfn/tests/run_g2_win.sh` and the finder G2) green against the scalar byte
   loop, every plant red; zero corpus answer changes at every stage.
2. **No regime slower beyond noise** (users of the default build; D186's bar). Stage 1's no-mover
   units: zero movers on EVERY arm (§Staging), no pcrec abi number change `[rev3 P3]` (unit 1f, the
   retired denies, is a caller-visible step of its own). Stage 3: each row's movers read new/old <= 1
   + the A/A floor in every regime and arm of a 588-style run, else the row narrows; a kept loss is
   an owner-approved exception (`[rev4]` D186 add. 2). `[rev3 A2]` smp20's shipped loss (S3's
   `cover` row, RTE/DEF 1.58-4.03x) closes BY DATA, no hand row: Goal 5.
3. **One table per question** (the next editor; `architecture.md` "One table per slot").
   `[rev3 P4]` After stage 1, for plan-call sites: six question tables and three pick-side tables
   (KEY, M, TIE; T-PICK arrives with the first priced row), plus the NAMED exceptions of §The tables,
   each with its retiring trigger. Check: the decider census of §The tables, which can fail.
4. **Costs measured, by target class, none hand-set: the END STATE** (D186 add. 1 A1; D176 Q1/Q3).
   No priced departure before its cards are measured; every cost a priced row reads is a declared
   row of the stamped set (checked); `plan_cost.def`'s Zen 1 rows retire with their last reader.
5. **The measured losses close, and data never hurts** (users of common patterns). `[rev4]` smp20
   `(?i)x/1234`: blind, the MINIMAX pick of the measured cards (least worst-case loss, never "wins
   every cell"); with a bundle matching job 588's real-text subjects, RTE/DEF <= 1 + floor on those
   cells via the first priced departure; read at every stage (§The watched witness). The six D-hors
   sites keep their wins (RTE/DEF 0.57-0.78). `[rev3 WD]` A with-data compile matches or beats the
   blind one (§The pick, "With data"). A win is never a requirement.

**Non-goals.** Engine choice, crossings and whole-artifact effects (architecture's rules; engine
pricing stays DEFERRED). The SIMD official verdict. New find methods (V1/M64 stay closed). Run-time
adaptive switching (Boonies). `[rev3 A2]` Changing the byte-rate prior, or a real-text rate dataset:
options are evaluated only if smp20 still mispicks at the last planned step.

## The shape

Six scenarios make the SAME call (DFA prefilter OFS, cover/REPORT, PF find, VM re-find, MLINE,
LMHIT; a pre-check's window-stating parts ride their site's call). Presence (the PRES slot) keeps its
own entry until [MEMFN-UNBOUNDED-SPANS] states unbounded spans. Inner first:

```
 PHASE 1, the plan call (pcrec reads its reply for NEXT, the OFFSETS stamp and the run member)
 1 FIXED FACTS   the measurement set (named or DEFAULTS), layer, alternatives (PARKED/RESEED/NONE),
                 floor, byte rates (the named analysis bundle's, else the prior)
                 [rev3 P1: form, handoff, site_kind are FRAME facts, stated in phase 2]
 2 CANDIDATES    per alternative: every stated core position after C-meet, with its set S, offset
                 d, prior mass, flat mass, table offer, soundness flags
 3 PER CANDIDATE T-VERIFY (step list incl. the run member) -> T-SETTEST / T-CMP forms
 4 PICK, LAST    the default plan (KEY, M, TIE: today's answer), then T-PICK's rows (stage 3)
 PHASE 2, the text call (pcrec states the frame its NEXT row chose; window_site §0)
 5 T-FRAME       Table E, legacy rows first, over (plan, frame, hooks, phase set)
 6 T-FIND        on E-find only: Horspool first, then the method rows, with the asker fact
 7 RENDER        the renderer row (B-fn / B-pair), then the text; decides nothing a card covers
```

`[rev3 P1]` T-FRAME and T-FIND stay TEXT-time through stage 1: Table E reads hooks and a phase set
the plan call does not take (compose.c :255-258; `window_reply_ask` relies on "the decision reads no
frame fact", emit_dfa.c :7600-7602), and T-FIND's answer depends on its asker (PAIR needs
`SF_WINDOW_STOP`, set only by `fd_find`, finder.c :938; Table E's legacy rows ask `fd_route`, which
never sets it). A priced row compares methods, so it needs the frame at plan time: §Staging's
prerequisite unit 3.0.

**The candidate list is data**, with soundness flags (a RESEED alternative never stops at F0, S188);
PARKED readability is a T-VERIFY output (`rd_set`, window.c :251-254, :877-878). **A scenario** is
stated facts. `[rev3 R4]` Of R-33's 1,742 RTE PF sites (1,767 units incl. the
43-pattern DEF recompile), 1,429 state PARKED + RESEED, 291 one NONE alternative, 22 PARKED only; of
the 1,454 RESEED alternatives (incl. DEF) 740 have one core position and 714 two or more
(`span_pick/counts.out`). **The trace**: every candidate, the rows walked, the default and the
deciding row (MFTRACE build); `[rev4]` from the first priced row, each candidate's prices, losses,
worst case and bands. The reply carries ONE plan: prices and alternatives live ONLY in the trace.

## The designer/emitter split

This mechanism IS the kit's planning face (roadmap §0a) and stage 1 IS A-PLAN's first step (D186
add. 1 A6), with the roadmap's ratchet accounting (§Staging).

| stage | owns | in this design |
|---|---|---|
| pcrec, the designer | facts and legal choices: spans, candidate positions with their rates, alternatives with entry, floor, frame facts, byte rates, the set | states them once per site; never a CHOSEN position, method or cost `[rev3 O6]` (D157; D167 add. 1 A11's landmark-admission exception stands until restated in code) |
| the kit's planning face | candidates, the question tables, the pick, (later) the cards | phase 1: facts in, one plan out (alternative, stop, verify plan, test forms) plus its trace |
| pcrec's rules | engine, route, crossings (`next_keys`, FIRST/NEXT rows) | reads the reply as NEXT reads the phase-1 reply today (window_site §2.4) |
| the kit's emitting face | frame, method and renderer rows, then text | phase 2: plan + frame in, C out; golden plan-in/C-out tests per seam |

**What moves across** `[rev3 P1]`. In stage 1 the reply does NOT grow (method, resume and frame stay
phase-2 answers; only 1f's entry removal is an MF_SITE_ABI event). It grows (method, resume, frame
row) at unit 3.0, when the plan call takes the frame.

**A-PLAN's open points.** (1) `[rev4]` ONE PLAN WITH ITS TRACE (owner, 2026-11-02): the kit hands
back one plan; prices and the alternatives considered appear only in the trace. This AMENDS
A-PLAN's agreed next step ("facts in, candidates and cards out"); stage 1 edits the roadmap (§Staging).
(2) Helper sharing stays emit's, cost-free. (3) Run-time dispatch stays held. (4) Cards are tables
keyed by class and regime. (5) `--memfn=no-X` denies become filters on T-FIND and T-PICK rows; the
namespace is unchanged (D147 add. 9). (6) The same-commit abi rule is unchanged.

## The tables

Rows say what is VALID; price and dominance are separate. Each table answers as today in stage 1.

| # | question | form and rows (stage 1) | replaces |
|---|---|---|---|
| T-FIND | how to find the next member of S at d, and where to resume | first-match `kit_table`, asked at TEXT time on E-find only `[rev3 P1]`: Horspool FIRST (D-hors's holds kept, deny `window-skip` with it; its admission reads T-VERIFY's tested sets, window.c :1592-1597, and its D-shift resume T-VERIFY's offsets), then D1c, PAIR, D1, D1w, R7w (resume D-one `c + 1`); ONE walk with the asker fact "the asker renders PAIR" (today `SF_WINDOW_STOP`, kept, renamed) replaces `fd_find`/`fd_route`'s two entries; SIMD forms are rungs of a row; inert R3a/R3b/R4 deleted (1a), R8/R1/R2 at 1f | Q3's `fd_route`/`fd_find`, Table D, T-RESUME |
| T-VERIFY | which other positions to test, in what order and grouping | a DECLARED STEP LIST read in order, every holding row applying: `[rev3 S3]` C-bound (a full-set position is never a test), C-floor or C-yes, C-model or C-none, C-pin, C-stop, C-run (its core/shape clause `run_group_ok` read by BOTH renderers' grouping, `find_groups` and `translate`), C-asc; first step the run member (`run_member`, T_MASS_STRETCH), an output of the plan | Q5, Table C and ofsskip's legacy plan (U10) |
| T-SETTEST | how one byte's membership is tested | offered `T[b]`, then `kit_set_test`; C-table/C-own live HERE only | Q11, `member_test` |
| T-CMP | how a literal stretch is compared | runcmp's rows (`rc_row_of`); generic.c's RUN chain is a named exception | Q6 |
| T-PRES | which required members a presence pass tests, in what order | the PRES rows (P0, P2, P3, P4, P9); `[rev3 S3]` `fd_pres`'s chain order (HEAD/RUN/REST, REST ascending byte, a REST member a whole exact run covers un-verified) and precheck's `implied_by` are its kept renderer-side deciders; precheck's three renderers are its rendering (N9); D176 Q4's fold is a T-PRES row, its own choice change | Q9, PRES part ordering |
| T-FRAME | which renderer serves this plan in this frame | Table E (`wf_erows`, legacy first, order kept), at TEXT time `[rev3 P1]`; `[rev3 P2]` plus the renderer row: B-fn vs B-pair (both PAIR on E-find, different C: smp05's `ofsskip__body` vs pr09's inline loop), reading the plan's shape and `fn_rows` BODY; `b_fn_holds`'s reconciliation KEPT | Q8, the phase-2 frame walk |

Pick-side tables: **KEY** (Table A's five rows: A-empty, A-parked, A-model, A-mass, A-floor; A-floor
is the RESEED default with no `scan_ok` walked span, 1,420 of 1,835 RESEED alternatives incl. DEF,
1,397 of 1,800 RTE; A-empty's reach owed); **M** (MARGIN, M-one, M-parked); **TIE** (`wf_ties`,
`[rev3 S1]` with three readers made explicit: the presence-member row, a SECOND comparator shape
(member order, then the larger byte; an UNKNOWN order ranks below every known, declared, as
`tie_over` reads `MF_ORDER_UNKNOWN` today); presence's run window reads T_WINDOW (LEFTMOST; its "no
kit reader" text corrected); translate's run rank reads T_MASS_STRETCH (HIGHER), its `rank_pos[0]`
asserted equal to `run_member`'s answer; plus T_BAND -> TIE_DEFAULT for priced rows). **T-PICK**
arrives with the first priced row. KEY and M are the DEFAULT; each retires only when a census shows
no class reads it, as its own no-mover step.

**Named exceptions** `[rev3 P4]`, each a second decider kept on purpose, with its retiring trigger:

| decider | answers | retires when |
|---|---|---|
| generic.c's per-byte RUN chain | T-CMP | U8's unit change |
| `fn_rows` BODY (ofsskip.c :414-416) and the RESEED KEY row's `scan_ok` | T-FIND on OFS sites (no consumer kind: 371 of 371 RTE OFS sites) | pcrec states a kind on OFS sites |
| `fn_rows` PREFIX (own denies `vrun-w32`/`vrun-w16`) and vrun's KA/KB (U7) | SIMD rungs | the first SIMD T-PICK row (`[rev4]` C9, D186 add. 2) |
| compose's `arms[]` as the frame selector of NON-plan sites (carries the `precheck-assign-byte` deny) | frame + method off the plan call | outside Goal 3's plan-call scope; joins when a kit request adds an arm |
| `fd_pres` chain order, `implied_by` | T-PRES | presence joins the call ([MEMFN-UNBOUNDED-SPANS]) |
| the asker fact (the one T-FIND walk answers per asker: E-find with it, legacy rows without) | T-FIND per frame | unit 3.0 (plan takes the frame) |

**The decider census** `[rev3 P4]` (Goal 3's check, per unit HEAD): a committed map `decider ->
table` (one line per deciding function; written by stage 1's first lane at its base, kept by each
unit's lane); a grep over `memfn/src` for argmin and walk shapes (`kit_walk(`, `< best`, `< bm`,
`tie_takes`, `TIE_`) whose every hit must be mapped to a table or a named exception, red on an
unmapped hit; one sabotage row: a byte-identical copy of `run_member`'s loop added elsewhere must go
red. `kit_walk` reach stays a population count, not the census (plain-loop deciders leave no reach).

**Growth rule.** A new scenario adds no table; a new method adds a T-FIND row plus its card (D176).

## The pick

**Stage 1: no prices.** The default is TODAY's plan (KEY, M, TIE, then phase 2's frame and method);
nothing reads a cost but KEY/M's `plan_cost.def` integers, C-model's truncation order kept.

**Stage 3: T-PICK rows, all priced** `[rev3 A2]`. Each row: a condition on stated facts tested
before any card key is looked up, the LEVELS it opens (method, position, alternative), the priced
action below, its deny, its per-regime evidence (D186). `keep` is the last row. No hand rows are
planned (A1 allows one with its own evidence; A2 rules none for smp20's class).

**The priced action** `[rev4]` (after stage 2, one row at a time; BLIND = MINIMAX, D186 add. 2):
1. Candidates are the complete plans that differ from the default only at the row's levels (the
   default among them), each priced under every SUBJECT KIND r of the reading. BLIND kinds: P, the
   committed prior; F, flat (`m_F(S) = |S| x 1e6 / 256` ppm); and REAL DATA, the shipped analysis
   bundles (today `log` and `weblog`; guard (a)). WITH DATA: below.
2. A candidate's LOSS under kind r is `loss_r(c) = price_r(c) / min_c' price_r(c')` (1 = the best
   candidate for that kind); its WORST CASE is `W(c) = max_r loss_r(c)`.
3. The minimax candidate c* has the least W. It is picked only when `W(default) - W(c*)` exceeds the
   band of that comparison (guard (b)); otherwise the default stays. Candidates within band of
   W(c*) go to TIE's rows (D176 Q5; guide addenda/kit.md "within-noise prices tie through tie
   rows"); a default within band is T_BAND -> TIE_DEFAULT.
4. Unpriced default: keep. Unpriced candidate (no card, or a card without noise): cannot be picked;
   a missing `noise_e6` is UNMEASURED, never 0, so it means no departure.
5. A renderer addition that flips a T-FIND first match moves the DEFAULT: its own row and evidence.
6. `[rev4]` SIMD (C9, D186 add. 2): a `-fmemfn-simd` build may pick its own position by its OWN T-PICK
   row, priced on SIMD-form cards, SIMD-on evidence, scalar the bar; else SIMD forms are rungs of
   the scalar plan (D147). Witness utf8-lead-no-cont `[\xc2-\xdf](?![\x80-\xbf])` (a two-byte vector
   window no scalar position equals); NOT smp20 (on '/' the SIMD build calls memchr, as scalar).
7. `[rev3 R5]` Each row states whether it applies on pre-check parts, where pcrec scans the reply's
   run member, not its stop (`req_run_member`, emit_dfa.c :1045-1077).

**With data** `[rev3 WD, rev4]` (a compile naming an analysis bundle B; plan [BENCH-WITHDATA]). At a
site a priced row admits, the BLIND pick (steps 1-4, minimax over the blind kinds) is computed first
and is the incumbent; a candidate departs from it only if cheaper beyond the band under B ALONE,
where the band adds each mass's sampling noise from B's counts (Poisson, `sqrt(n)` on a count n)
times its coefficient; missing card noise means no departure (step 4). No minimax here: the
subject is B's kind (the owner's scope, below). Cost: a minimax and a B pricing per admitted site.
**The property** (the owner's bar, plan [BENCH-WITHDATA]; scope CONFIRMED by the owner 2026-11-02: "The analysis data must match the test subject to require same-or-better results."): on every cell whose subject
kind B describes, a with-data compile matches or beats the blind compile beyond noise. **Why the
structure gives it** `[rev4]` (re-derived under minimax): the with-data pick's predicted price under
B is <= the blind pick's by construction (the blind pick is the incumbent, a departure must win
under B beyond band). The argument never reads HOW the incumbent was chosen, so it holds for the
minimax incumbent exactly as for rev 3's; and when B is itself a blind kind (`log`, `weblog`), the
with-data pick is B's own least within band, never worse under B than the minimax compromise. The
MEASURED cell then holds when (i) the cards' regime is the cell's (long subjects; per-call cells
need [SPAN-PICK-PERCALL]'s term); (ii) model error (independent positions) stays inside the band;
(iii) the cell's subject is B's kind within B's sampling noise (a held-out sample, never the timed
bytes); (iv) the site is one a priced row admits. A with-data loss is therefore a broken (i)-(iv):
a mechanism finding ([BENCH-WITHDATA] item 4), never a trade. NOT covered: sites no priced row
admits, where KEY's mass-only rows read B as their prior (today's behaviour, kept byte-identical by
stage 1); [BENCH-WITHDATA]'s census finds their losses, each answered by a priced row (a blind KEY
incumbent there would undo today's with-data wins, smp20's included).

**The price of a plan** `[rev3 C1, C2]`: in the set's unit (the scalar walk's per-byte cost, D176
Q1) per 1e6 subject bytes; masses in ppm; card values `value_e6` integers. Fixed point (D176 Q5):
every product is carried in int128 at a scale of 1e-12 of the unit and rounded there half away from
zero (`measure_sets.md` §1.7), and the price is rounded to an integer at its end; a term under the
scale contributes 0, deterministically ("exact" is withdrawn). Under rate model r:

```
 stream methods (memchr, memchr-back, PAIR):  byte(m) x 1e6 + m_r(S) x (hit(m) + verify_r) + passes_r x enter
 walk:                                        byte(walk) x 1e6 + m_r(S) x (hit(walk) + verify_r) + passes_r x enter
 Horspool:   (1e6 / E_r[sh]) x (probe + q_r x (hit(hors) + verify'_r))                  + passes_r x enter
   byte(m)  = the method's measured cost per subject byte, ALL its streams (no streams factor)
   verify_r = sum_i cmp(form_i, pass_r(i)) x prod_{j<i} pass_r(j), i over the other positions in
              ascending mass; verify'_r the same without S_last (the probe tested it)
   pass_r(j) = m_r(set_j) / 1e6;   passes_r = m_r(S) x prod_i pass_r(i)
   cmp(f, p) = cmp0(f) + (cmp½(f) - cmp0(f)) x min(p, 1-p) / 0.5   (ASSUMPTION: the mispredict
              share is symmetric about 0.5 and linear; the card's two pass rates are its points)
   enter    = enter(consumer kind, entry fact)
   E_r[sh]  = sum_b rate_r(b) x sh[b] / 1e6 over Horspool's shift table (a byte in no window
              position shifts the full window w); q_r = m_r(S_last) / 1e6
```

`hit(m)` is per candidate RETURNED, the method's own slope over hit density. Horspool pays its
candidates inside its own line. Positions are independent (an ASSUMPTION; model error, §Robustness).

**The band of a comparison** `[rev3 C3]`: for prices a and b, the quadrature sum over cards of
`(coef_a - coef_b) x noise` (a card both read with one coefficient cancels), plus, with data, B's
sampling terms. `[rev4]` The minimax test `W(default) - W(c*)` propagates card noise through both
ratios (first order, in quadrature) plus the real-data kinds' sampling terms. No constant enters except the
card gates (kit-grid's `gate_e6` 3 %, an UNMEASURED DEFAULT, D149; each new card declares its own).

## Cost cards

**What is measured** (one card per quantity, regime named, `measure_sets.md` §7.2 shape). `[rev4]`
SIMD-form cards RETURN to stage 2 (C9, D186 add. 2): each card below is measured per layer
(scalar, and each SIMD form a SIMD T-PICK row would price), scalar the bar:

| card | per | regime | replaces |
|---|---|---|---|
| `find.byte` per method (memchr, memchr-back, PAIR, walk) `[rev3 C1]` | subject byte, all the method's streams | miss-only stream, fresh long buffer | C_MEMCHR, C_BITMAP |
| `find.hit` per method (the four, and `hors` `[rev3 C2]`) | candidate returned and restarted | slope over hit density, periodic and random landings; the member split named in its subject (x only vs x/X alternating) | the ASSUMED H_HIT |
| `hors.probe` | Horspool probe (load, table read, shift) | miss-only, the window's shift distribution | — |
| `verify.cmp` per T-SETTEST form, per T-CMP row x length class | one compare | pass rate 0 and 0.5 (`cmp0`, `cmp½`) | C_VERIFY (UNMEASURED), C_MISPRED |
| `enter` per consumer kind x entry fact (PARKED resume, RESEED re-seed, NONE) | candidate passed on | false-start survival measured | C_ENTER (MEASURED x ASSUMED) |

MARGIN (2x, ARGUED) stays M's default until the PARKED and RESEED `enter` cards exist for the kinds
a priced row admits. `[rev3 C10]` Open card-design question for stage 2's lane: survival is a
property of the pattern's automaton after the stop, so a per-(kind, entry) card may bake in its
fixture's survival; the alternative is a pcrec-stated survival fact times a per-byte card. OFS
sites state no kind, so `enter` has no key there (fine while T-FIND declines on OFS). MAX_SET is not
a card; U9 closes by a grep of `PCREC_OFSK_MAX_SET`'s readers.

**Noise reaches the kit.** `mf_measure` has no noise field; the committed set's 68 kit rows carry
`noise_e6` '-'. Stage 2 owes: a kit request (main files it), a noise field (an MF abi event, with
`measure_sets.md` §4.1 and `match_api` hunks, the kit channel's homes `[rev3 C4]`), a producer, a
rule for derived rows (quadrature through the row's formula), and `[rev3 C4]` the stamp's honesty
once noise decides: noise joins `values_digest` (a digest-version event, `measures.md` §3.3¶1 and
§5¶4, `measure_sets.md` §1.6/§4.1, readers by grep), or a FILE set may not share a committed id.

**Where they live** `[rev3 C5]`. The span cards are quantities of the grid's successor method
(`kit-grid@2`); the grid keys are re-measured under it (a grid-sized job). `[rev4]` The set is a
NEW id, `zen4-grid2` (main, 2026-11-02): `measures.md` §8¶1 (a new run is a new id) beats D176
Q3's wording and plan [MEASURE-SET]'s note ("zen4-grid1 rev 2"). Embedded by `make gen-measures`,
handed on `mf_art_begin`.

**Chosen by the set** (`--measures=NAME`, else `DEFAULTS`, `measures.md` §5¶6; a class option goes to
[IFACE-PUSH]). **Measured** by queue jobs (`idle-ok`, quiet-gated, windows cleared with the owner):
dev box first, ubuntubudu by slot request, the Mac directional. Cards are long-subject quantities; a
per-call term is owed before a priced row with per-call movers.

## Robustness to the byte rates

**The weakest input is the prior.** PRIOR_AUTHORED (`a322116b1b87f9f6`) rates {x,X} at 1,097 ppm and
'/' at 4,154; job 588's subjects held x 2,338 against '/' 1,026 candidates on real text, 1,388 vs 0
on none, 21,788 vs 10,856 on random (t588tri §a). The walk-vs-V1 precedent: when the evidence cannot
say, keep the choice that is never badly wrong.

**The rule** `[rev4]` (D186 add. 2). Blind: MINIMAX over P, F and the shipped real-data bundles
(`log`, `weblog`): the least worst-case loss, departing from today's pick only when the worst case
improves beyond the band (§The pick 1-4): never resting on the authored prior alone, never badly
wrong on a kind the build knows. With data: the bundle alone, against the blind pick. **Model
error** is NOT in the band: `[rev3 C3]` the first priced row runs with it UNMEASURED, guarded by its
own run's predicted-vs-measured print per mover (R5.3), whose spread is the term the NEXT priced row
adds.

**What the formula says for smp20** `[rev4]` (`span_pick/smp20.py`, `smp20.out`, re-run 2026-11-02
over bundles re-made by `witness.sh`; STAND-INS, none a card for these methods: byte(memchr) 0.06 =
`plan_cost.def` C_MEMCHR, byte(PAIR) 0.12 = 2 x C_MEMCHR (ASSUMPTION: two memchr streams), hit 20 c =
R-33's H_HIT ASSUMPTION (no `plan_cost.def` row), cmp 2.5 = C_VERIFY flat, enter 20 = C_ENTER).
Prices per 1e6 subject bytes, hit(PAIR) 20 (40 in brackets where it differs):

| kind | @0 {X,x} PAIR | @1 {/} | @4 {3} | @5 {4} | kind's least |
|---|---|---|---|---|---|
| P (prior) | 144,694 (166,634) | 153,476 | 228,231 | 228,231 | {X,x} ('/') |
| F (flat) | 295,858 (452,108) | 147,929 | 147,929 | 147,929 | the five one-member stops tie |
| `log` | 128,384 (135,824) | 385,409 | 760,657 | 854,238 | {X,x} |
| `weblog` | 286,612 (434,532) | 1,225,432 | 441,512 | 302,235 | {X,x} ('4') |
| B `prose` (with data) | 168,871 (212,311) | 72,938 | 66,143 | 63,555 | '4' |

**Minimax** over P, F, `log`, `weblog` (worst-case loss, the kind that sets it): at hit(PAIR) 20,
{X,x} 2.000 (F), '/' 4.276 (`weblog`), '3' 5.925 (`log`), '4' 6.654 (`log`), '1' 8.939, '2' 9.670;
at hit(PAIR) 40, {X,x} 3.056 (F), '/' 4.055 (`weblog`), '3' 5.600. The minimax pick is TODAY's
{X,x} at both: '/' wins P and F but loses 2.8-4.3x on the real-data kinds (guard (b) keeps it anyway).
**Card values that make '/' the minimax pick** (cmp, enter fixed; the sweep in `smp20.out`, byte(PAIR)
from 1.00 x byte(memchr)): hit(PAIR) at least 4x hit(memchr) (8x at hit(memchr) 5) AND byte(PAIR)
under a ceiling: 2.60x at hits 20/80, 2.10x at 20/160, 1.10-1.75x at 10/40, 4.25x at 40/160. With
hit(PAIR) at most 2x hit(memchr) '/' is never minimax: {X,x} holds up to byte(PAIR) 4.20x (hits
20/20; 3.25x at 20/40), then '3' (worst 2.5-4.0 at the switch points, set by `log`). Job 588's none cell (RTE/DEF 2.79,
read as byte(PAIR) ~2.3x at hit 20; directional, Zen 1 stand-ins against a Zen 4 run) lies in
{X,x}'s region. Stage 2 measures the cards that decide it.

**Uncovered** (review r1 C5). Where real text is far from the prior, uniform text AND the shipped
bundles (UTF-8 lead bytes, case-folded letter pairs, dense classes the prior under-rates), every
blind kind agrees wrongly (R-33's `utf8/alt-cyr-64`; `log`/`weblog` are mostly ASCII). Any priced row
over two-member stops is gated on a fix (an encoding fact, or a further, adversarial rate kind).

**Nothing is tuned:** a mispick is fixed only by a corrected measurement, term or validity row.

## The watched witness

`[rev3 A2, WW]` smp20 `(?i)x/1234` is resolved by data, never by a rule, and read TWO ways at every
stage, each on every arm (default, `--engine=vm`, both layers, the DEF deny):
`[rev4]` (1) BLIND: the MINIMAX pick of the measured cards over P, F, `log`, `weblog` (D186 add.
2), re-priced pcrec-side, departing only beyond noise; job 588's timings judge the model behind it
per regime, never "picks '/'". (2) WITH a text-like bundle: a one-member stop the bundle rates rarer
than {x,X} (main, rev 3.1: '/' or, as on the stand-in, '4', which passes). At the last planned step
(stage 3 row 1; later rows are unscheduled) a failure of (2) is a mechanism problem; a blind pick
that is not the measured minimax is a mechanism problem; a minimax pick job 588 still times as
losing is A2's case: options are evaluated then.
**The forecast to watch** `[rev4]`: the stand-ins keep {X,x} blind (worst 2.00 under F, '/''s 4.28
under `weblog`), so the blind job-588 cells keep their loss unless the cards land in '/''s region
(§Robustness). That is the rule working: on `log`/`weblog` subjects {X,x} is right; real-text
cells close through (2).
The text-like bundle until [BENCH-WITHDATA]'s held-out bundle exists: `prose`, GPL-3 + GFDL-1.3 +
Apache-2.0 counted by `pcrec-analyze` ({x,X} 2,172 ppm, '/' 575, '4' 158; job 588's real text:
2,338 vs 1,026), built in scratch by `span_pick/witness.sh`, never committed. `log` and `weblog`
rate '/' far above {x,X} (14,462 vs 372; 51,754 vs 7,396): blind kinds of (1) `[rev4]`, not (2)'s.

| stage | (1) blind | (2) with the prose bundle |
|---|---|---|
| today = stage 1 (byte-identical; re-compiled 2026-11-02, `span_pick/witness.out` unchanged) | @0 {X,x} PAIR on default, vm and SIMD-on; '/' on the DEF deny. `[rev4]` Today's pick IS the stand-ins' minimax pick (2.00 vs '/''s 4.28); job 588 1.58-4.03x | @5 {4} memchr on default, vm and SIMD-on (KEY A-mass reads the bundle); PASSES. DEF deny: '/' and '4' |
| stage 2 (cards measured, no reader) | unchanged; `[rev4]` the forecast becomes a reading: is the measured card point in '/''s region, {X,x}'s or '3''s? | unchanged |
| unit 3.0 (plan takes the frame) | unchanged (no priced row yet) | unchanged |
| stage 3 row 1, the LAST planned step | `[rev4]` the minimax pick, departing only beyond noise; read against job 588 per regime | the blind pick is the incumbent; '4' departs under B (63,555 vs 168,871); must PASS, else a mechanism finding |

## Staging under D186

D186 (TRIAL): a UNIT change (bar: no regime slower) or a CHOICE change (a row on stated facts with
per-regime evidence; a losing regime narrows the row).
`[rev4]` **Choice-row losses** (D186 add. 2, over D144 item 3 for choice rows): D144 governs WHEN
and HOW (a batch-gate regression is not reverted, it becomes an issue row, the row's deny is the
interim kill switch; a disaster is still denied or reverted at once); D186 sets WHAT the issue
row's fix must be: narrow the row's condition, or an owner-approved exception, never an open-ended
accepted loss. Unit changes (1a-1f, 3.0, smp04's set-test change) stay under D144 alone.

**Stage 1: unify, today's answers kept: A-PLAN's first step.** Neither kind: a no-mover refactor of
separable units, each with its own byte-identity witness; a unit that cannot be byte-identical
leaves stage 1 and lands alone as a unit change with its own deny. `[rev3 P3]` A unit that adds or
removes a finder row ahead of the PRES rows shifts `mf_class.pres_row`/`pres_led` (1 + a finder row
index): no emitted byte, an MF_CLASS_V event in that unit. `[rev4]` Unit 1d also carries the
one-plan roadmap edit: `docs/design/stream/roadmap.md` A-PLAN's next step becomes "a plan call
(facts in, one plan out, its trace beside it)", its end state naming the trace as prices' home.

| unit | content | deletes |
|---|---|---|
| 1a dead code `[rev3 P3]` | N3 `mf_set_terms`; inert rows R3a/R3b/R4 (no deny; zero reach by code); MF_CLASS_V (pres_row shift) | 4 members |
| 1b primitives `[rev3 S1, S2]` | U4 one mass primitive over a POSITION MULTISET (a list of cubes, a repeated byte counted per position, as `window_mass`: a set-shaped primitive moves `run_window`, e.g. `zzzzzzz~J`), a capped/uncapped argument, the NONE-mode total (62,500, not 62,496); the landmark admission's per-factor round-up product stays its caller's; U5 `wf_ties` with the presence-member row and presence's run window reading T_WINDOW | 2-3 mass variants, 2 tie spellings |
| 1c kit-only spellings `[rev3 S1]` | U2: P3's `run_scan` asks `run_member`; translate's run rank reads T_MASS_STRETCH, `rank_pos[0]` asserted against `run_member`; U6 the kit's landmark shadow (presence.c :222-245) retired if no census reads it | 2-3 |
| 1d planning core | one candidate builder; KEY/M/TIE as the default; T-VERIFY as a step list with C-bound and the run member; trace without prices (U1 as two KEY rows, U10 = Table C + ofsskip's legacy plan, N1, N6) | `a_model_choose`'s private enumeration, `mass_domain`'s copy |
| 1e phase-2 tables `[rev3 P1, P2]` | T-FRAME (legacy first) at text time; T-FIND as ONE walk with the asker fact, Horspool first; the renderer row (B-fn/B-pair, reconciliation kept); compose `arms[]` and `fd_find`'s text become renderers keyed by (frame row, method row, renderer row) (U3 less OFS, N5, N11); no MF_SITE_ABI event (the reply does not grow); MF_CLASS_V if the Horspool row's move shifts pres_row | `fd_find`/`fd_route`'s second entry walk |
| 1f retired denies `[rev3 P3]` | R8/R1/R2 with `fd-r8`/`fd-ndisp`, the §2.5 pay rule (`fd_pay`, `pay_fill`, `n_interval`) and the public `mf_finder_pay`; CALLER-VISIBLE, not a no-mover: `registry.md` §6¶8a/§6¶8b hunks (floor 14 -> 12), `--list-axes` re-pin, `emit_sweep.py`/`memfn_arm.py`/`finder_check.py`/rows edits, an MF_SITE_ABI event | 3 rows, 2 denies, the pay rule, 1 entry |

**Witness, per unit**: `scripts/emit_sweep.py` byte-identical over the corpus, the bench patterns and
job 588's sample on EVERY arm (default, each `--memfn=no-X` deny (1f's two once retired), `--engine=
vm`, both SIMD layers), stamps included; `tests/findings/manifests/*_movers.txt` unchanged; reach
floors; G2; the decider census. Counted pcrec-side from artifact diffs.
**Ratchet** (roadmap §5): the kit's duplicates join §5 as rows counted at stage 1's base (proposed
for main): find-method deciders (`fd_route`, `fd_find`, compose's method walk, `fn_rows` BODY;
members − 1), position enumerators, kit mass variants, tie spellings, run-member spellings, the
landmark shadow, inert finder rows. `[rev3 P2]` `b_fn_holds` is in the FRAME family (the renderer
row), not deleted. Each unit lowers its row and raises none; stage 1 adds no member.
**Sequencing** (D153): while stage 1 is in flight, opt rows touching window.c, finder.c, ofsskip.c,
compose.c or presence.c carry "remodel overlap" and wait. `[rev4]` O3 answered WAIT (owner): the
`[a[:b]` set-test unit change (smp04) and the look-ahead measurement wait for stage 1.

**Stage 2: measure the cards** `[rev3 O1, A2]`. Follows stage 1 directly (D186 add. 1 A2); its
trigger is stage 1 done. Contents: §Cost cards (`[rev4]` scalar and SIMD forms), the noise channel,
the new id `zen4-grid2`, the step-0 gate. No reader, no consult, zero movers, stamps and `DEFAULTS`
unchanged.

**Stage 3: priced choice rows, one per change.**
- **Unit 3.0, the plan takes the frame** `[rev3 P1]` (the first priced row's prerequisite): pcrec
  states form, handoff and site_kind per candidate frame at phase 1 (one ask per NEXT row's frame:
  `window_reply_ask` and `req_run_member` change, pcrec-side); the plan call takes the hooks and phase
  set; the reply grows method, resume and frame row; the asker fact retires. Byte-identical; one
  MF_SITE_ABI (+ MF_CLASS_V) event; same witness as stage 1.
- **Each row**: one T-PICK row naming its levels; a deny with a D174 behaviour name (spec home
  `registry.md` §6¶8a, listed by `cli.md` §2.4¶1); `[rev3 R1]` a 588-style run of RTE vs the row
  denied on EVERY arm (default, the deny, `--engine=vm`, both layers; scalar the bar) and its movers
  census computed per arm from artifact diffs, never from a default-arm sweep alone, stamp-only
  movers their own class; `[rev3 C7]` `consulted` set by T-PICK rows; `[rev3 C8]` its drop-F witness
  from its own population, or the plant declared UNREACHED (never a pass); `[rev3 R5]` its
  pre-check-part statement; its pcrec abi event and spec hunk.
- **Row 1** `[rev3 A2]`: the first priced departure, admitting smp20's class (NONE alternatives
  whose default is a two-member stop), job 588 its evidence, §The watched witness its reading.
  `[rev3 O2]` Its acceptance also compares against the rule-list pilot, "the baseline any pricing
  must beat" (0.981 of ideal held-out, [PRICE-BAKEOFF]): the pilot is re-run after row 1 and after
  each later priced row (one pilot job each, SIMD off, Zen 4) and its distance is D186's drift
  gauge. `[rev3 C6]` Row 1 flips `DEFAULTS` to the new set (a default change with its census,
  §What moves). `[rev3 R7]` Row 1 is where A-model's one-member preference (`scan_ok`) and A-mass,
  D186's first unification target, meet: KEY's two rows retire there by census.
- `[rev3 O7]` **Ratchet delta**: T-PICK with its `keep` row falling to KEY is one table (delta 0 at
  row 1); each later row names the member it deletes or is rejected at review (roadmap §0).
- `[rev3 R9, rev4]` **Batch gate**: choice-row losses above. **SIMD rows** (C9): §The pick 6.

**Later rows, each its own change and prerequisites** (none scheduled): Horspool priced (D176 Q2;
deletes HORS_MIN): `hors.probe`, `hit(walk)`, `hit(hors)`; witnesses hex8-bounded and the five other
D-hors sites. RESEED admission at any set size: PF E-stmt sites, where PAIR has no renderer: needs
[MEMFN-PAIRSTOP] (or walk-only) and both `enter` cards. Dense pairs: [MEMFN-PAIRSTOP] first, gated
on the C5 fix. Offset-0 RESEED stops stay excluded. smp04 `[a[:b]`: a UNIT change (T-SETTEST table
form), own deny and regime run, after stage 1 (`[rev4]` O3 = wait).

## What stage 1 deletes

| id | stage 1 does | unit | later |
|---|---|---|---|
| U1, N1 | one candidate builder; A-model and A-mass stay two KEY rows; C-model same arithmetic | 1d | meet at row 1, retire by census `[rev3 R7]` |
| U2, U5 | `run_scan` asks `run_member`; translate's rank and the run window read `wf_ties`; presence-member row `[rev3 S1]` | 1b, 1c | pcrec's two and its PICK: findings |
| U3, N4, N5 | one T-FIND walk with the asker fact (N4 kept, renamed `[rev3 P1]`); arms/`fd_find` text become renderers; not on OFS | 1e | the asker fact retires at 3.0; OFS joins with a kind |
| U4; U6 | one primitive over a position multiset, NONE-mode total kept `[rev3 S2]`; the kit's shadow retired if no census reads it | 1b; 1c | pcrec's findings.c copy stays (D157); pcrec owns admission (D167) |
| U10, N6 | T-VERIFY = Table C + ofsskip's legacy plan (PRES ordering is T-PRES's `[rev3 S3]`); candidates -> T-VERIFY -> default | 1d | priced rows |
| N11 | Table E becomes T-FRAME at text time, order kept, plus the renderer row `[rev3 P1, P2]` | 1e | plan-time at 3.0 |
| N3, N14, R3a/R3b/R4; R8/R1/R2 + denies | deleted (zero reach); retired with registry hunks `[rev3 P3]` | 1a; 1f | — |
| kept | U7/N10/N12 (SIMD; `[rev4]` SIMD-form cards in stage 2), U8 (unit change), U9 (boundary), N2 (MARGIN), N7/N8/N13, N9 | — | a SIMD T-PICK row (C9); U8; a reader grep; `enter` cards; priced rows |

## pcrec-side findings (for main; not changed here)

- **Run pin and scan index**: `pcrec_find_run_scan_index` (findings.c :745), `_window_start` (:780),
  `pcrec_run_pin` (kset.c :294) restate the run member (held by `req_run_member`, emit_dfa.c :1058).
- **Landmark admission** `[rev3 O6]`: `req_landmark_admits` (emit_dfa.c :9064) and lmwalk's
  `lc_rarity` share `pcrec_landmark_margin` (+ `LMWALK_K_HIT_UNMEASURED`): a D157 EXCEPTION (D167
  add. 1 A11) until pcrec states the landmark as a candidate and reads `find.hit`.
- Prerequisites pcrec-side: `[rev3 P1]` unit 3.0's per-frame ask; a consumer kind on OFS sites;
  [MEMFN-UNBOUNDED-SPANS]; [MEMFN-PAIRSTOP]. `next_keys` and lmwalk's route stay architecture's.

## The measurement regime

RELEVANT. Each card names its regime (§Cost cards; landing flips walk vs stream choices,
walk_vs_v1 §3). Per set: box, compiler, Linux verdicts, `taskset`-pinned, scalar the bar. Prices are
long-subject; row evidence regimes are job 588's (throughput, search_short, match x real, none,
random, dense).
`[rev3 C11]` Numbers the pick reads that are NOT cards, each with what would flip it: KEY/M's
`plan_cost.def` integers (Zen 1, ubuntubudu, while the default set is zen4: a box mismatch at every
stage until they retire); C_ENTER (MEASURED x ASSUMED ~2 bytes of survival); MARGIN (2x, ARGUED);
HORS_MIN (PROVISIONAL, one job-581 cell, dev box); every card's `gate_e6` (UNMEASURED DEFAULT);
the prior (authored; the blind reading's P); `[rev4]` the `log` and `weblog` bundles (blind kinds;
their sampling noise is in the band); the bundle (the with-data reading; likewise). smp20's flips:
the hit(PAIR)/hit(memchr) ratio and the byte(PAIR) ceilings between {X,x}, '/' and '3' (§Robustness).

## The independent control

RELEVANT.
- **Answers:** G2 against the scalar byte loop; the `.rxt` oracle under every committed set plus
  synthetic extreme sets forcing each T-FIND row (`measure_sets.md` §8). **Stage 1 and 3.0:** the
  §Staging witness counted pcrec-side from artifact diffs, never the kit's `moved` (K35); the census.
- **Priced rows:** predicted price vs measured time per mover (R5.3); validation sites share no
  number with the cards (R5.2). `[rev3 C7]` The keys a pick read are counted by a pcrec-side python
  re-price from the stamped set's rows (shares no code with the kit; the artifact carries no trace),
  `[rev4]` recomputing each kind's prices, the minimax and the with-data departure, whose pick is
  diffed against the artifact's. finder_check.py checks D and F get their true arms in
  the first priced row's change. A swapped-cards plant moves a reach witness.
- **With data:** [BENCH-WITHDATA]'s compile-only census (blind vs each bundle, movers listed) and its
  held-out bundles (no training on the timed bytes). **The watched witness:** job 588's timings judge
  smp20's pick per regime, never the kit's own price.

## What moves when the data is regenerated

RELEVANT. Only picks and the `<PREFIX>_MEASURES` stamp move. The stamp ("" today) becomes
`id@rev:digest` on every artifact whose pick consults the set (only sites a priced row admits) and
changes on every card rev (stamp-only movers: their own census class). A byte move is an abi event
(D76/D94, readers by grep incl. byte counts) with its per-arm census; `measures.md` §8/§5 hunks.
`[rev3 C6]` **Defaults.** A bare compile reads `DEFAULTS` (`idk zen4-grid1@1`), which holds no span
card, so priced rows keep the default on bare compiles until `DEFAULTS` names the new set: that flip
lands with row 1, a default change with its census (`measures.md` §5¶6, §8¶3; `DEFAULTS.log`). At
M2 (plan [MEASURE-SET], D166 add. 2) the idk default becomes an ISA envelope that excludes every
per-byte cost row: `[rev4]` priced rows then go dark on bare compiles (picks back to the default,
stamps move). That is INTENDED (main, rev 3.1: "an unknown target prices nothing") and is M2's
dependency (main's to record with [MEASURE-SET]); no safe-direction carriage. Noise: §Cost cards.
Stage 1 moves no emitted byte (1f moves `--list-axes` and two options); stage 2 moves nothing; 3.0
moves nothing; row 1 moves its movers and the stamps of the sites it admits.

## Owner rulings since rev 3

| `[rev4]` ruling (source) | landed in |
|---|---|
| Blind pick = MINIMAX, the least worst-case loss over the subject kinds; guards (a) the kinds include the shipped `log`/`weblog` bundles beside P and F, (b) depart from today's pick only when the worst case improves beyond the cards' measured noise (D186 add. 2) | §The pick 1-4 and the band; "With data" (property re-derived); §Robustness (smp20 recomputed, '/''s region); §The watched witness; Goal 5 |
| Choice-row losses: D144 governs when and how, D186 what the fix must be (narrow the row, or an owner-approved exception); unit changes under D144 alone (D186 add. 2) | §Staging (top; stage 3 batch gate); Goal 2 |
| C9: a SIMD build may pick its own position by its own row with SIMD-on evidence, scalar the bar; witness utf8-lead-no-cont, not smp20; SIMD-form cards return to stage 2 (D186 add. 2) | §The pick 6 (rule 6 rewritten); §Cost cards; §Staging (stage 2, SIMD rows); named exceptions; §What stage 1 deletes |
| One plan with its trace; amends A-PLAN's "candidates and cards out" (owner, memfn journal 2026-11-03) | §The shape (trace); §The designer/emitter split (1); §Staging (the roadmap edit in stage 1) |
| Rev 3.1 (main): witness (2) passes on a one-member stop rarer than {x,X} ('4' passes); new id `zen4-grid2`; priced rows dark on a bare compile under M2 intended, M2's dependency, no safe-direction carriage | §The watched witness; §Cost cards; §What moves |
| O3 = WAIT: smp04's set-test unit change and the look-ahead measurement wait for stage 1 | §Staging (sequencing; later rows) |

**Review 2026-11-02 r2** (`docs/dev/reviews/2026-11-02-r2-memfn-spanpick2.md`): dispositioned by id
in rev 3 (d3c4133cc, "Disposition"), all accepted, ONE-STREAM superseded by A2. Rev 4 reopens none;
the minimax replaces C3's step 3, and the rulings above answer C5, C6, C9, R9, O3, O4.
**For main** (carried from rev 3, not yet filed): plan rows [SPAN-PICK-UTF8] (trigger: the first
priced row over two-member stops), [SPAN-PICK-PERCALL] (a priced row with a per-call mover),
[PICK-IDIOM] (the first T-PICK row), a class option for [IFACE-PUSH], §Staging's ratchet rows.

## Open questions

`[rev4]` None for the owner. A forecast, not a question: the stand-ins keep smp20's blind pick at
{X,x} under minimax (§The watched witness); A2's last-step evaluation covers it.

## STATE AT HANDOFF

OWED none. Lane spanpick4: rev 4; `span_pick/smp20.py` rewritten for the minimax (blind kinds, with-
data bundles, the card sweep), `smp20.out` re-made; `witness.sh` re-run (8 compiles, main tree's
`build/pcrec`; `witness.out` identical); both CLAUDE.md rev lines. No make, no timing. Not a build go:
next, the owner's stage-1 build go (or first a narrow re-check of §The pick and §Robustness).
