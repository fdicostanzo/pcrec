# span_pick — the kit's ONE "find the span" choice mechanism (design, rev 1)

**Status: PROPOSED, rev 1 (lane spanpick, 2026-11-02, from main 884996ef6). Design only: not a build
go, no code, no make, no timing.** Direction from the owner (Frank, 2026-11-02, agreed with the kit
manager), taken as requirements: one set of "find the span" choices used by every scenario; one small
table per inner QUESTION, never per scenario; inner-first order with the position picked LAST; bounded
per-site costs from measured COST CARDS per CPU class; a pick robust to the byte-rate prior; staging
under D186 (TRIAL). Evidence: `units_inventory.md` (ids U1-U10, N1-N14, Q1-Q11 below are its ids),
`docs/dev/lanes/kitunits_report.md`, `r33_report.md` (R-33 simulation, classes R1-R5),
`t588tri_report.md`, `bar588_report.md` (job 588), `window_site.md` rev 3.3 (Tables A-E, M),
`walk_vs_v1_record.md`, `pricing_requirements.md` (deferred; requirements R4-R6 reused where they
fit), `measure_sets.md` + `measure_store/`, `docs/design/stream/roadmap.md` §0a and A-PLAN;
decisions D157, D176, D186. Code cites are the inventory's (re-read at main 34c8ed620); the build
re-greps them.

## Goals

Ranked; a higher goal wins a conflict.

1. **Answers exact** (every caller). Every plan the tables can produce yields exactly the candidates
   its facts define: G2 (`memfn/tests/run_g2_win.sh` and the finder G2) green against the scalar byte
   loop over the generated predicate space, every plant red; zero corpus answer changes at every stage.
2. **No regime slower beyond noise** (users of the default build; D186's bar). Stage 1: zero movers
   (artifacts byte-identical to main but for the abi digits, counted by a pcrec-side sweep). Stage 3:
   each moved site class reads new/old <= 1 + its A/A floor in EVERY regime of a 588-style run, or it
   is narrowed until it does; a loss kept is an owner-approved exception, never a mean.
3. **One table per question** (the next editor; `architecture.md` "One table per slot"). Deciders
   per question: today FIND (Q3) has 4 plus precheck's own text, the stop (Q1) 5 table rows plus 5
   other answers; after stage 1, exactly ONE per question: six question tables plus the pick's one
   admission table (§The tables, §The pick), whatever the number of scenarios (seven today).
4. **Costs measured, by target class, none hand-set** (owner; D176 Q1/Q3). After stage 3 every cost
   the pick reads is a declared row of the stamped measurement set (a check), measured on the
   target's class; zero UNMEASURED DEFAULT or other-box constants read by a moving pick
   (`plan_cost.def`'s Zen 1 rows retired).
5. **The measured losses close** (users of common patterns). smp20 `(?i)x/1234`: routed/DEF <= 1 +
   floor on every job-588 cell (today 1.58-4.03x); the six D-hors sites keep their wins (RTE/DEF
   0.57-0.78). A win is never a requirement.

**Non-goals.** Engine choice, engine crossings and whole-artifact effects (declared rules in
architecture; engine-level pricing stays DEFERRED, `pricing_requirements.md` header). The SIMD
official verdict (`vrun_bench_request.md`). New find methods beyond the ones that exist (V1/M64 stay
closed, `walk_vs_v1_record.md`). Run-time adaptive switching (Boonies). Changing the byte-rate prior
(a facts change, §Open questions 3).

## The shape

Every scenario (DFA prefilter OFS, cover/REPORT, PF find, presence/pre-check parts, VM re-find (the
attempt's seek), MLINE, LMHIT) makes the SAME call: facts in, a complete plan out (A-PLAN's plan
face; window_site's phase-1 reply made general). Inside, four steps, inner first:

```
 1 FIXED FACTS   target class (-> the measurement set), layer (SIMD on/off), frame class,
                 alternatives (PARKED / RESEED / no entry), floor, byte rates
 2 CANDIDATES    per alternative: every stated core position after C-meet, not the full set,
                 with its set S, offset d, prior mass, flat mass |S|/256, table offer,
                 soundness flags                                   (DATA, not rules)
 3 PER CANDIDATE the shared tables:  FIND (method, Horspool among them) -> VERIFY plan ->
                 RESUME -> SET-TEST / RUN-COMPARE forms of each test  => one COMPLETE plan
                 per (candidate, method) the FIND table admits
 4 PICK, LAST    over complete plans: the method within a candidate, then the position within
                 an alternative, then the alternative one level up; one pick rule at all three
                 levels (§The pick)
 then EMIT       renders the plan; it decides nothing a card covers (roadmap §0a)
```

**The candidate list is data.** It is built mechanically from pcrec's stated spans (start, sets,
core, verify, table offer) and the art's byte rates, plus soundness flags that are facts, not
preferences: on a PARKED alternative only verify-YES positions are readable stops (`rd_set`; today
k0); on a RESEED alternative F0 (offset 0) is never the stop (S188, MISCOMPILE-1; R-33's R3 also
measured offset-0 stops slower on its three confounded sites C11/C14/S20). No row reads a label
("REPORT", "OFS"): the scenario shows only through these facts (`architecture.md` "A row checks its
own contract").

**What is a scenario then.** A list of stated facts and a frame. PF find states one alternative with
one candidate (span 0, pcrec's start set); presence states unbounded spans (D176 Q4: presence-only,
read off the range) and asks the same tables with a presence price; LMHIT and MLINE state one
position each. None carries its own selection.

**The trace** (observable, `architecture.md`): every candidate, every admitted method, both prices
with their bands, the default plan, the winner and the deciding level, printable per site (trace
build, as MFTRACE today). R-33's probe reads the same record.

## The designer/emitter split

This mechanism IS the kit's planning face of roadmap §0a (the waterfall: pcrec designer -> architecture
-> emit -> gcc) and A-PLAN's "next step". Who does what:

| stage | owns | in this design |
|---|---|---|
| pcrec, the designer | the FACTS and the legal choices: spans, alternatives with their entry, floor, frame class it may host, the art's byte rates, the measurement set (from the target) | states them once per site; never a position, a method or a cost (D157) |
| architecture: the kit's planning face | candidates, the six tables, the pick, the cards | the plan call: facts in, ONE complete plan out (alternative, stop, method, verify, resume, test forms) plus its trace (every candidate's prices under P and F, the default, the winner); a library call inside the stage, not a seam |
| architecture: pcrec's rules | non-local choices (engine, route, crossings: `next_keys`, the FIRST/NEXT rows) | reads the plan reply as today's NEXT rows read the phase-1 reply (window_site §2.4); never prices across engines |
| emit: the kit's emitting face | rendering | the emit call: chosen plan in, C text out; Table E and B's renderers select TEXT by the plan's method and the frame; they decide nothing a card covers, so a golden plan-in/C-out test per seam holds |

**What moves across.** The plan reply grows from window_site's phase-1 reply (alternative, stop, plan,
RE-SEED bit) by the method and resume, which today the text call re-decides (`fd_find` in phase 2,
`fn_rows` BODY inside the legacy rows). Moving them into the plan is exactly stage 1's deletion of
the duplicate deciders, so the split and stage 1 are one change, byte-identical (A-PLAN open point 6:
the emit face still produces the bytes, so the same-commit abi rule is unchanged).

**A-PLAN's open points, as this design answers them.** (1) A candidate is a composition: the plan call
returns one complete plan per site, the per-level winners kept in the trace, not a set for
architecture to re-pick (architecture never prices across the kit's internals). (2) Helper sharing
stays emit's, declared cost-free (no card prices it). (3) Run-time dispatch stays held: a target SET
would price each arm with its class's cards; nothing here forbids it. (4) Cards are tables keyed by
class and regime (§Cost cards). (5) `--memfn=no-X` denies become filters on T-FIND rows and `T-PICK`
rows inside the plan call; the option namespace (D147 add. 9) is unchanged. (6) As above.

**Frame classes are the one backward-looking fact.** Validity (a method must have a renderer in the
frame, §Frame availability) is knowledge about emit; it travels as DATA, the renderer table's
declared contract read at plan time, never as a question to emit, as §0a requires.

## The tables

One per inner question; each is a `kit_table` on `kit_walk` (rows with a contract, a deny where it
moves bytes, a basis, reach counters). Rows say what is VALID; price and dominance are separate
(`pricing_requirements.md` R2.7). In stage 1 each table answers first-match exactly as today.

| # | question | rows (stage 1, today's answers) | replaces (inventory) |
|---|---|---|---|
| T-FIND | how to find the next member of S at offset d | Horspool (today D-hors's holds: mass >= HORS_MIN, window >= 2, last >= 0; a METHOD: it replaces find and resume), D1c memchr-back, PAIR (2 members, valid only where the frame has a two-stream renderer), D1 memchr, D1w walk (VM seek), R7w walk; inert R8/R3a/R3b/R4/R1/R2 kept, declined where no renderer exists (N14); SIMD forms are FORMS of a row (vrun rungs over PAIR's and memchr's text, vany over 2-3 bytes when carded), applicable only at `-fmemfn-simd` | Q3's four deciders (`fd_route`, `fd_find`, compose `arms[]`, `fn_rows` BODY), precheck's own memchr (N9), Table D's D-hors admission (Q7), Q4 |
| T-VERIFY | which other positions to test, in what order and grouping | Table C's 12 rows unchanged (C-meet .. C-asc; C-model's greedy over verify-NO walked offsets) | Q5's Table C, PRES part ordering, ofsskip's legacy plan (U10) |
| T-RESUME | where to restart after a miss or a failed verify | D-shift (Horspool's `sh[b]`, holds only when T-FIND chose Horspool), D-one `c + 1` | Q7 (its admission moves to T-FIND) |
| T-SETTEST | how one byte's membership is tested | offered table `T[b]`, then the kit's range chain (`kit_set_test`); stage 1 adds nothing | Q11, `member_test`, C-table/C-own |
| T-CMP | how a literal stretch is compared | runcmp's rows (words, overlap, bytes, memcmp; `rc_row_of`) | Q6, generic.c's per-byte bypass (U8) |
| T-PRES | which required members a presence pass tests | the PRES slot's rows (P0, P2, P3, P4, P9) over `kit_pres_picks` | Q9 (D176 Q4: one decider for stop and presence; a different price) |

**Not tables.** The stop position (Q1) and the alternative (Q2) are not questions with rows: they are
the PICK's levels over the candidate list (D176 Q1). Table A's three rules (A-parked, A-model,
A-mass) become soundness flags (above) plus, in stage 1, the KEY the pick ranks by (§The pick). The
frame (Q8) is a fixed fact chosen by pcrec's NEXT row from the reply; Table E becomes the emit face's
renderer selector. Landmark admission (Q10) is pcrec's (D167; §pcrec-side findings). Mass and ties
are primitives, not questions: one `kit_set_sum` with a named capped/uncapped argument (U4) and ONE
tie table (`wf_ties`, U5) that every level reads.

**Six question tables, one pick admission table (`T-PICK`), seven scenarios.** A new scenario adds no table; a new method adds a
T-FIND row plus its card in the same change (D176 standing rule); a new question (one not answered
by these) is the only way to add a table.

## The pick

**One rule, three levels.** `pick(plans, default)` runs (a) over the methods T-FIND admits at one
candidate, (b) over the candidates' winners within one alternative, (c) over the alternatives' winners.
Each level is a priced argmin with a conservative default (architecture.md permits a priced argmin;
the optimizer sits inside the level, the levels are declared):

1. Price every plan under TWO rate models: P = the committed prior (the art's byte rates, as today)
   and F = flat (`|S|/256` per position, "subject unknown"). Each price carries a band from its
   cards' measured spread (§Robustness).
2. The DEFAULT plan is the stage-1 answer at that level: T-FIND's first match; the position the
   stage-1 KEY row ranks first; the alternative today's MARGIN row keeps (PARKED unless RESEED
   prices under half).
3. A challenger replaces the default only if it is cheaper than the default under BOTH P and F by
   more than the combined band in each. Otherwise the default stands. Among several qualifying
   challengers, the least P price wins; ties within a band go to the TIE table.

**The price of a complete plan** (one unit: the target set's scalar-walk per-byte cost, D176 Q1;
fixed-point integers, D176 Q5), per 1e6 subject bytes, under rate model r:

```
 price_r = scan(method, S)                       streams x c_byte(method) x 1e6; walk: c_byte(walk) x 1e6;
                                                 Horspool: (c_probe + m_r(S) x verify) / E_r[shift]  (D176 Q2)
         + hits_r(S) x c_hit(method)             hits_r(S) = m_r(S) (ppm; PAIR: m_r(a) + m_r(b))
         + hits_r(S) x verify_r(plan)            verify_r = sum_i c_cmp(form_i) x prod_{j<i} pass_r(j)
         + passes_r x c_enter(consumer)          passes_r = m_r(S) x prod_i pass_r(i); pass_r(j) = m_r(set_j)/1e6
```

Positions are independent (an ASSUMPTION, as R-33's; `pricing_requirements.md` R4.6: its measured
error bound joins the band before any pair-rate fact is used). `c_enter` is per consumer kind (DFA
re-seed, VM attempt), a site-local term: every plan of one site hands to the same consumer, so only
`passes_r` differs between plans; no engine is priced.

**Where the pick may depart at all (the D186 gate).** A priced departure is admitted only on site
classes named by rows of ONE admission table, `T-PICK`: each row a condition on stated facts (entry,
candidate set sizes, frame class), its own deny, and its per-regime evidence (D186: a choice change
is a row). The last row, `keep`, returns the default plan. Stage 1 ships `T-PICK` with `keep` alone
(zero movers); stage 3 adds rows one choice change at a time (§Staging). When `T-PICK` rows start
conflicting, that is D186's revisit trigger and pricing's ([PRICE-BAKEOFF]).

**Stage 1's KEY rows** (today's three cost models, kept so answers stay; deleted in stage 3 by the
first choice change):

| entry fact | key the position level ranks by | today's code |
|---|---|---|
| PARKED | the one readable candidate (verify-YES k0); price for MARGIN only: `model_cost(k0 one member ? C_MEMCHR : C_BITMAP, ...)` | A-parked :407-420 |
| RESEED | prefix_k's `model_cost` with C-model's greedy plan; candidates whose T-FIND answer is not memchr are UNPRICED (the key has no other method's cost: today's `scan_ok`) | A-model :446-466 |
| none (REPORT, parts, VM seek, MLINE) | least prior mass, no method term | A-mass :529-561 |

## Cost cards

**What is measured** (one card per quantity, regime named, `measure_sets.md` §7.2 shape):

| card | per | regime | replaces |
|---|---|---|---|
| `find.byte` per method x layer (memchr, memchr-back, PAIR, walk, Horspool probe, each SIMD form) | byte scanned | miss-only stream, fresh long buffer (the unit's pinned regime, §1.4) | C_MEMCHR, C_BITMAP |
| `find.hit` per method x layer | candidate returned and restarted | slope over hit density; TWO landing regimes, periodic and random (the walk's predictor effect, walk_vs_v1 §3) | the ASSUMED H_HIT (R-33's 10-40 c sweep) |
| `verify.cmp` per T-SETTEST form and per T-CMP row x length class | one compare | pass rate 0 and 0.5 (the mispredict slope) | C_VERIFY (UNMEASURED), C_MISPRED |
| `enter` per consumer kind | candidate passed to the matcher | false-start survival measured, not assumed | C_ENTER (MEASURED x ASSUMED) |

Not cards: MATERIAL 2/1 (deleted: the robustness rule replaces it), HORS_MIN (deleted, D176 Q2),
MAX_SET (a compile budget: read from `limits.def`'s `PCREC_OFSK_MAX_SET`, U9).

**Where they live.** As `kit.` rows of a measurement set in `measure_store/<id>/<rev>/set.tsv` with
its PROVENANCE.md, keyed by class (`x86_64-avx2/zen4`, a Zen 1 class, an Apple class), their method
cards appended to `memfn/data/cards/` (a new `kit-span@1`, finder_check.py's check C holds the
shape), embedded at pcrec build by `make gen-measures`, handed to the kit on `mf_art_begin`
(`mf_measures`, kit rows only; the existing channel, no new fact). A compile reads ONE set (sets
never include one another, `measure_sets.md` §0), so the span cards and the finder's grid keys must
sit in the same set: the stage-2 job measures both, or the set carries grid1's rows re-read under
one method version.

**Chosen by the target, not the host.** The set is the one the compile names (`--measures=NAME`, the
config line) or its class's `DEFAULTS` row; the host the compiler runs on is never consulted. An
unknown target (class `idk`) gets `DEFAULTS` (today `zen4-grid1@1`; the M2 envelope later, §Open
questions 2). The SIMD layer changes which T-FIND rows apply, never a cost (D176 Q1, R4.7).

**Measured how.** One short timing job per box, through the box queue (`idle-ok`, quiet-gated, one
stage per job, cleared with the owner for the timing window): the dev box (zen4) first; ubuntubudu
(Zen 1) by slot request; the Mac directional only (D144 add. 1). Unmeasured on a set means the row is
UNMEASURED and visibly so (R4.5): a plan whose method has no card is unpriced and cannot challenge;
it may still BE the default.

**Generated C carries no costs.** Cards move picks at compile time only; an artifact stamps the set it
priced with (`<PREFIX>_MEASURES`, `id@rev:digest`).

## Robustness to the byte rates

**The weakest input is the prior.** R-33: the default prior (PRIOR_AUTHORED, digest
`a322116b1b87f9f6`) rates {x,X} at 1,097 ppm and '/' at 4,154 ppm; job 588's real subjects held x
2,338 against '/' 1,026 candidates (t588tri §a). Under the prior alone a price-correct pick still
picks the measured-slower stop. Rates are a property of the subject, unknown at compile time, as
landing predictability was in the walk-vs-V1 record; its ruling ("the walk when the subject is
unknown") is the precedent: when the evidence cannot say, keep the choice that is never badly wrong.

**The rule.** Two rate models, P (prior) and F (flat), and a challenger must win under both (§The
pick, step 3). F is not a guess about text; it is the absence of one, so a departure that survives F
does not rest on the prior. A plan that wins only under P (the prior's claim alone) keeps the
default.

**The margin is measured, not tuned.** Each card row carries its A/A `noise_e6` (`measure_sets.md`
§1.4/§7: A/A and fit spread in quadrature). A price's band is the quadrature sum of each card's noise
times that card's coefficient in the price (its hit count, its byte count). A challenger wins under
model r when `price_r(default) - price_r(challenger) > sqrt(band_r(default)^2 + band_r(challenger)^2)`.
No constant appears; a noisier box or an envelope set (whose spread includes cross-box spread)
widens the band and so departs less, which is the conservative direction. Where a card was measured
in two landing regimes, the price takes the band spanning both (the regime is as unknown as the
rates).

**What it predicts for the witnesses** (R-33's arithmetic, Zen 1 constants; stage 2's cards decide):
- smp20 `(?i)x/1234`: under F, '/' (one stream, half the flat mass) beats {x,X} PAIR by a wide
  margin; under P it wins by 8.6 % under KEY B and loses under KEY A or H_HIT 40. So the flip holds
  only if zen4's `find.byte` and `find.hit` separate it beyond band under P. If they do not, the rule
  keeps {x,X}, correctly saying "the prior says otherwise", and the fix is the prior's rate for that
  pair (a data change judged on its own; §Open questions 3), not a bent pick (R6.1).
- R1 dense pairs (`cat|dog`, {c,d} 46,603 ppm under P, 7,812 under F): the walk wins under P, PAIR
  under F: no dominance, the default stands. Rare pairs (`(["'])`, 4,569 ppm) can depart.
- The six D-hors sites: Horspool is a T-FIND row and stays the default there in stage 1, so R-33's
  "the sim picks the measured-slower walk" (no Horspool candidate) cannot occur.

## Staging under D186

D186 (TRIAL) judges every optimization as a UNIT change (a better implementation of one unit in the
cases it handles; bar: no regime slower beyond noise) or a CHOICE change (a row on stated facts with
per-regime evidence; bar: no regime loses beyond noise, a losing regime narrows the row).

**Stage 1: unify the tables, today's answers kept.** One candidate builder, the six tables, `pick`
at three levels with `T-PICK = {keep}` and the stage-1 KEY rows; every scenario routed through the
one call; the duplicate deciders deleted (§What stage 1 deletes). Neither kind: a no-mover refactor
(D153: refactors are no-movers). Bar: the byte-identity sweep (§Independent control) shows zero
movers; any item that cannot be byte-identical leaves stage 1 and lands alone as a unit change
with its own deny. Abi: none if bytes are identical; an MF_SITE_ABI event only if the plan call's
seam changes `mf_site` (A-PLAN's split; byte-identical, the kit's agreement).

**Stage 2: measure the cards.** One job per box (§Cost cards), a new set id per box per run, the
cards committed to `memfn/data/cards/` first. No pick reads them yet, so zero movers; a `DEFAULTS`
transition, if made, carries its movers census (`movers/<seq>.tsv`), expected empty.

**Stage 3: the pick reads the cards.** Each place it differs from today is a SEPARATE choice change:
one `T-PICK` row, its deny (`--memfn=no-<row>`), its per-regime evidence from a 588-style run (RTE vs
the row denied, every regime and subject class, A/A floor, both layers reported, scalar the bar),
its movers census, its own abi event. Order:
1. **smp20's class** (U1, R-33's R4: no-entry sites whose candidates differ in member count): the
   no-entry KEY row (mass alone) is replaced by the priced key. Evidence: job 588 (RTE/DEF 1.58-4.03x
   on every class) plus the row's own run. R-33's R4 neighbours (pr09 `x[Q%]y`, `a[\18]b`, `a[*/]b`,
   `x[\x{e0}-\x{ff}]y`, `\B(?<!a)[de]`) are its population.
2. **Horspool priced** (D176 Q2): HORS_MIN deleted, Horspool competes as a method; witnesses
   hex8-bounded (dense 1.53x loss today) and the five other D-hors sites.
3. **RESEED admission** (R-33's R2, 95 PF units): RESEED candidates of any set size priced with
   PAIR/walk cards; MARGIN replaced by the robustness rule at the alternative level.
4. **Dense pairs** (R1, 225 units): needs PAIR rendered in PF frames first (a unit addition,
   §Frame availability), then the method level may choose walk over PAIR on stated rates.
Offset-0 RESEED stops (R3) are not a stage-3 row: they stay excluded (soundness flag) unless an
unconfounded timing says otherwise (§Open questions 4).

**smp04 `[a[:b]` is a UNIT change** (T-SETTEST: the walk's membership test as a 256-entry table
instead of the compare chain; 4.475x random, inference: mispredicts, t588tri §a). It lands
independently of stages 1-3 under the unit bar; if some regime (a one-range set on real text) is
slower, it narrows into a T-SETTEST row and becomes a choice change.

**Re-measuring is a deliberate data change.** A new card rev that moves bytes is an abi event (D76/
D94, readers by grep) with its movers census; every moved pick in that census is judged as a choice
change under D186, per regime, before the `DEFAULTS` row moves.

## What stage 1 deletes

Every duplicate (inventory §4) and every neither-kind item (§3), by id.

| id | today | stage 1 does | later |
|---|---|---|---|
| U1 | A-model vs A-mass give smp20 two stops | one candidate builder and one pick; the two keys remain as two KEY rows (byte-identical) | stage 3 item 1 replaces both with the priced key |
| U2 | run scan member: 5 spellings | kit side: presence.c P3 `run_scan` and translate's rank call `run_member` (one tie rule); identity checked by the sweep | pcrec's two: §pcrec-side findings |
| U3 | find method: 4 deciders + precheck | T-FIND asked once per candidate; compose `arms[]`, `fn_rows` BODY and B-fn become renderers keyed by the pick; precheck's parts ask T-FIND | — |
| U4 | mass: 3-4 kit variants | one primitive with a named capped/uncapped argument | pcrec's findings.c copy stays (D157) |
| U5 | tie rules in 3 tables | `wf_ties` the one table; presence.c `tie_over` reads it | pcrec's PICK: finding |
| U6 | landmark admission: 3 copies | the kit's evidence-only shadow (presence.c:222-245) retired if no census reads it (re-grep) | pcrec owns admission (D167) |
| U7 | vrun KB = `rank_pos[1]`, w16 KA only | KEPT (it moves SIMD-on bytes) | a SIMD-layer choice change: KA/KB from the plan's stop and first verify position |
| U8 | generic.c compares per byte, bypassing runcmp | generic.c asks T-CMP if byte-identical; else a separate unit change | — |
| U9 | MAX_SET stated twice | `plan_cost.def` row reads `limits.def` | MAX_SET leaves the cost table in stage 3 |
| U10 | verify plan: Table C, PRES ordering, ofsskip legacy | T-VERIFY the one plan; PRES and ofsskip's legacy text render it where byte-identical | — |
| N1 | `a_model_choose`: whole-plan search, method hard-wired | split into candidates + T-VERIFY's C-model + the RESEED KEY row; same arithmetic | stage 3 item 3 |
| N2 | MARGIN 2x (ARGUED) | the alternative level's default (kept) | stage 3 item 3: robustness rule; MATERIAL deleted |
| N3 | `mf_set_terms`, no caller | deleted (only the link check reads it) | returns as a T-FIND form with its card if measured to win (D77) |
| N4 | `SF_WINDOW_STOP` gates PAIR | deleted as a stop fact; becomes T-FIND's validity column "a two-stream renderer exists in this frame class" | stage 3 item 4: PF frames get the renderer, the column empties |
| N5 | B-fn reconciles two method picks | a renderer row keyed on the pick and the plan's shape; decides nothing | — |
| N6 | A, then D, then B: stop fixed before its find is priced | order becomes candidates -> T-FIND (Horspool inside) -> T-VERIFY -> T-RESUME -> pick; same answers (stage-1 keys read no method price but memchr's) | priced in stage 3 |
| N7 | HORS_MIN (PROVISIONAL, one cell) | kept as the Horspool row's `holds` | stage 3 item 2 deletes it |
| N8 | A-parked prices a pair as C_BITMAP whatever renders | kept (the PARKED KEY row) | stage 3: priced by the method T-FIND admits in that frame |
| N9 | precheck's own memchr | asked through T-FIND (byte-identical expected: same memchr text) | — |
| N10 | vrun's second "which positions" | = U7, kept | SIMD choice change |
| N11 | Table E: "legacy rows first so bytes stay" | frame becomes a fixed fact; Table E the renderer selector, order kept | legacy E-func/E-stmt retire at A-PLAN's split |
| N12 | vany.c, no row reaches it | a T-FIND SIMD form row, declined (no card, `kit-kernels@1` UNMEASURED) | live when carded and measured |
| N13 | Zen 1 constants used on zen4 | kept (stage-1 keys) | stage 2 measures, stage 3 retires `plan_cost.def` |
| N14 | finder R8/R2/R3b pick unrenderable V1/W64/A3 | declined by the validity column (no renderer); deleted after a reach census shows zero | — |

## Frame availability, and how the shape removes it

Today the same stop gets PAIR through `fd_find` (E-find sets `SF_WINDOW_STOP`, finder.c :938) and the
walk through `fd_route` (PF sites, R7w), because only E-find has a two-stream renderer; B-fn (window.c
:1672) then reconciles the finder's pick with `fn_rows`' BODY pick; A-parked prices k0 as C_BITMAP
whatever renders it (N8); Table A "reads no frame fact" and so cannot know what it priced. Renderer
availability is dressed as a stop fact. In the shape, availability is a VALIDITY column of T-FIND,
keyed on the frame class (a fixed fact, step 1), declared beside the renderer table it mirrors; the
pick prices only valid methods, so a price always belongs to the method that renders. The end state
gives every frame that hosts a find the same renderers (one two-stream text, `ofs_pair_text`, already
serves E-find and fn-pair), the column becomes uniform and the plan becomes frame-free again, as
window_site's phase 1 requires.

## The multi-variable risk

Three inputs move a pick: the cards (about ten rows per class), the rates (two models) and the margin.
Free to vary jointly, they could be fitted to any outcome. The design bounds them: the cards are
measured in isolation, never fitted to end-to-end timings, never set from a validation site
(`pricing_requirements.md` R4.2, R6.2); the rate models are two fixed inputs, the committed prior and
flat, with no weight between them; the margin is computed from the cards' own noise. Nothing is left
to tune. A card error moves a pick only if it shifts a price beyond its own band under BOTH models; a
prior error moves nothing F refuses. A mispick is fixed only by a corrected measurement, a missing
term with its own card, or a corrected validity row (R6.1), recorded with its evidence. The drift
gauge is D186's: the rule-list pilot's distance from the per-site ideal (0.981 on 2026-11-02),
re-read after each stage-3 row.

## pcrec-side findings (for main; not changed here)

- **Run pin and scan index.** `pcrec_find_run_scan_index` (findings.c:745), `_window_start` (:780),
  read in src/facts/req.c:779-781, and `pcrec_run_pin` (src/facts/kset.c:294) restate the kit's run
  member with their own tie rule; agreement is held by `req_run_member` (emit_dfa.c:1058-1076, loud)
  and the KW-8 census. End state: pcrec asks the plan reply (window_site §2.3 already makes the reply
  the owner); its two spellings retire.
- **Landmark admission.** `req_landmark_admits` (emit_dfa.c:9064) and lmwalk's `lc_rarity`
  (lmwalk.c:231) share `pcrec_landmark_margin` (:9057); lmwalk adds its own walk-length model with
  `LMWALK_K_HIT_UNMEASURED` 10. The landmark origin is pcrec's (D167). End state: pcrec states the
  landmark as a candidate and reads the kit's price for its find (the `find.hit` card replaces K_HIT).
- **lmwalk's route** and **`next_keys`** (emit_dfa.c:7299) choose handoff, scan or landmark walk
  partly from the reply: an architecture rule, outside this mechanism's per-site scope.
- **PF span 0** is pcrec's statement; the kit never picks another stop there. If pcrec stated more
  positions, PF would join the position level with no new table.

## The measurement regime

RELEVANT. Every card names its regime (§Cost cards): miss-only streaming for `find.byte`; hit-density
slope in periodic and random landings for `find.hit` (a regime that flips walk vs stream choices,
walk_vs_v1 §3, hence both measured); pass rates 0 and 0.5 for `verify.cmp`; per consumer kind for
`enter`. Box and compiler per set (dev box zen4 gcc 15.2 first; Zen 1 and Apple per their boxes),
Linux verdicts, `taskset`-pinned, scalar layer the bar and SIMD-on reported. The rates (prior vs
flat) are the regime the compile cannot know; the robustness rule exists because that regime flips
decisions (smp20). Stage-3 evidence regimes are job 588's: throughput, search_short, match; real,
none, random, dense subjects.

## The independent control

RELEVANT.
- **Answers:** G2 checks every renderable plan against the scalar byte loop over a generated predicate
  space (shares nothing with the tables); the `.rxt` oracle under every committed set plus synthetic
  extreme sets that force each T-FIND row (`measure_sets.md` §8), which also gives each row a
  population that reaches it ([MECH-REACH]).
- **Stage 1:** a byte-identity sweep (`scripts/emit_sweep.py` over the corpus, the bench patterns and
  job 588's sample, main vs branch), counted on the pcrec side from artifact diffs, never from the
  kit's `moved` (K35). R-33's probe gives a decision-level comparison but reads the kit's own query,
  so it is a diagnostic, not the control.
- **Stage 3:** per row, a 588-style timed run of RTE vs the row's deny, every regime and class, A/A
  floor; the population is the movers census from artifact diffs; the validation sites share no
  number with the cards (R5.2) and print predicted price vs measured time (R5.3), so a wrong card
  shows even when the pick is right.
- **Cards:** a check that every cost an artifact's pick read is a declared row of its stamped set
  (D176 Q1); finder_check.py's check C holds card shape and deps. Sabotage: a plant that drops model F
  must flip smp20's class witness; a plant that swaps two cards must move a reach witness.

## What moves when the data is regenerated

RELEVANT. Generated C carries no cost, so only picks move. A new card rev or a new set enters a build
through `make gen-measures`; it moves bytes only where a `T-PICK` row admits a departure and the new
prices change a dominance verdict. Such a move is an abi event (D76/D94; readers by grep, the byte-
count class included), carried with the `DEFAULTS` transition's `movers/<seq>.tsv` and each moved site
judged under D186 as a choice change. The `<PREFIX>_MEASURES` stamp names the set; `docs/spec/
measures.md` §8 (sets today) and §5 (the default) take their hunk when a set or default changes (D80).
Stages 1 and 2 move nothing.

## Open questions

For the owner, plain words, each with a leaning.

1. **When nothing clearly wins.** If no plan beats today's under both the prior rates and flat rates,
   should the kit keep today's plan, or take the plan whose worst case across the two is smallest?
   Leaning: keep today's. The other way moves hundreds of sites at once with no per-site evidence,
   which D186 forbids; it can come back later as its own choice change.
2. **An unknown target.** Today a compile that names no target class prices with the dev box's
   (Zen 4) cards. Once the multi-box envelope exists (M2), cost cards have no "safe direction" in it
   and would price nothing, so an unknown target would keep today's plans everywhere. Is that the
   behaviour you want for unknown machines? Leaning: yes; it is "the walk when the subject is
   unknown" applied to the machine.
3. **smp20 and the prior.** If Zen 4's measured cards do not make '/' win clearly under the prior
   rates, the rule keeps {x,X}, because the prior wrongly calls x rarer than '/'. Fix the prior's
   rates (a separate facts change with its own evidence), or accept smp20 as a known gap until then?
   Leaning: fix the prior; never bend the pick to get the answer.
4. **Offset-0 re-seed stops.** The simulation liked them on 17 sites; the only timings (three,
   confounded) say slower, and an old miscompile forbade F0 as the stop. Keep them excluded?
   Leaning: keep excluded until one clean timing says otherwise.
5. **Two-stream search in plain prefilter frames.** Today the plain prefilter frame cannot render a
   two-byte stream search, so a two-byte start set is always walked there. Add that renderer (a unit
   change) so the method choice no longer depends on the frame? Leaning: yes, before the dense-pair
   choice change (stage 3 item 4).

## STATE AT HANDOFF

OWED none. Design lane: one new note (this file) and one index line in `docs/design/memfn/CLAUDE.md`;
no make, no runs, no code, no re-pin. Not a build go; the next step is the owner's answers to the open
questions and a critic round (`/pcrec-critic design`).
