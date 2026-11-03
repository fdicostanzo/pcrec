# span_pick — the kit's ONE "find the span" choice mechanism (design, rev 5)

**Status: PROPOSED, rev 5 (lane spanpick5, 2026-11-03). Design only: not a build go, no code, no make,
no timing.** `[rev5]` Carries the owner's 2026-11-03 ruling "if no analysis is provided, use the
default; the default is by encoding as well" (D186 add. 2 as amended 2026-11-03: ONE rate model per
compile; minimax, F and the kind list leave the pick) and the surviving FIX-NOWs of review 2026-11-03
r1. Read §Owner rulings since rev 4 and §The pick first; rev 5 text is marked `[rev5]`, older marks
stay. Evidence: `units_inventory.md`, `r33_report.md`, `t588tri_report.md`, `bar588_report.md` (job
588), `window_site.md` rev 3.3, `measure_sets.md`, roadmap §0a/A-PLAN/§5; `span_pick/`. Code cites:
959c08124 (memfn/src unchanged on this branch).

## Goals

Ranked; a higher goal wins a conflict.

1. **Answers exact** (every caller). Every plan the tables can produce yields exactly the candidates
   its facts define: G2 (`memfn/tests/run_g2_win.sh` and the finder G2) green against the scalar byte
   loop, every plant red; zero corpus answer changes at every stage.
2. **No regime slower beyond noise** (users of the default build; D186's bar). Stage 1: zero movers
   on EVERY arm, no pcrec abi number change `[rev3 P3]` (1f is a caller-visible step of its own).
   Stage 3: each row's movers read new/old <= 1 + the A/A floor in every regime and arm of a 588-style
   run, `[rev5]` a random-like regime among them, else the row narrows or is an owner exception.
3. **One table per question** (the next editor; `architecture.md` "One table per slot").
   `[rev3 P4]` After stage 1, for plan-call sites: six question tables and three pick-side tables
   (KEY, M, TIE; T-PICK arrives with the first priced row), plus the NAMED exceptions of §The tables,
   each with its retiring trigger. Check: the decider census of §The tables, which can fail.
4. **Costs measured, by target class, none hand-set: the END STATE** (D186 add. 1 A1; D176 Q1/Q3).
   No priced departure before its cards are measured; every cost a priced row reads is a declared
   row of the stamped set (checked); `plan_cost.def`'s Zen 1 rows retire with their last reader.
5. **Blind picks are the default's, data never hurts** (users of common patterns). `[rev5]` A blind
   pick depends only on the pattern, the target and the stamped defaults: no bundle moves it. smp20
   `(?i)x/1234` blind is "consistent with the default" by definition (E1); with a bundle matching job
   588's real text it moves to '/' or '4', RTE/DEF <= 1 + floor there (§The watched witness). The six
   D-hors sites keep their wins (0.57-0.78). `[rev3 WD]` With data matches or beats blind. A win is
   never a requirement.

**Non-goals.** Engine choice, crossings and whole-artifact effects (architecture's rules; engine
pricing stays DEFERRED). The SIMD official verdict. New find methods (V1/M64 stay closed). Run-time
adaptive switching (Boonies). `[rev5]` Changing a default prior: a deliberate data event with its
census (§What moves), evaluated for smp20 only at the last planned step if the default is wrong.

## The shape

Six scenarios make the SAME call (DFA prefilter OFS, cover/REPORT, PF find, VM re-find, MLINE,
LMHIT; a pre-check's window-stating parts ride their site's call). Presence (the PRES slot) keeps its
own entry until [MEMFN-UNBOUNDED-SPANS] states unbounded spans. Inner first:

```
 PHASE 1, the plan call (pcrec reads its reply for NEXT, the OFFSETS stamp and the run member)
 1 FIXED FACTS   the measurement set (named or DEFAULTS), layer, alternatives (PARKED/RESEED/NONE),
                 floor, byte rates: the ONE table pcrec handed, with its digest, or none [rev5]
                 [rev3 P1: form, handoff, site_kind are FRAME facts, stated in phase 2]
 2 CANDIDATES    per alternative: every stated core position after C-meet, with its set S, offset
                 d, mass under the handed rates, table offer, soundness flags (the LIST reads no rate)
 3 PER CANDIDATE T-VERIFY (step list incl. the run member) -> T-SETTEST / T-CMP forms
 4 PICK, LAST    the incumbent (KEY, M, TIE: today's answer), then T-PICK's rows (stage 3)
 PHASE 2, the text call (pcrec states the frame its NEXT row chose; window_site §0)
 5 T-FRAME       Table E, legacy rows first, over (plan, frame, hooks, phase set)
 6 T-FIND        on E-find only: Horspool first, then the method rows, with the asker fact
 7 RENDER        the renderer row (B-fn / B-pair), then the text; decides nothing a card covers
```

`[rev3 P1]` T-FRAME and T-FIND stay TEXT-time through stage 1: Table E reads hooks and a phase set
the plan call does not take (compose.c :255-258; emit_dfa.c :7600-7602), and T-FIND's answer depends
on its asker (PAIR needs `SF_WINDOW_STOP`, set only by `fd_find`, finder.c :938). A priced row
compares methods, so it needs the frame at plan time: unit 3.0.

**The candidate list is data**, with soundness flags (a RESEED alternative never stops at F0, S188);
PARKED readability is a T-VERIFY output (`rd_set`, window.c :251-254, :877-878). **A scenario** is
stated facts. `[rev3 R4]` Of R-33's 1,742 RTE PF sites (1,767 incl. the 43-pattern DEF recompile),
1,429 state PARKED + RESEED, 291 one NONE alternative, 22 PARKED only; of the 1,454 RESEED
alternatives 740 have one core position, 714 two or more (`span_pick/counts.out`). **The trace**:
every candidate, the rows walked, the incumbent and the deciding row (MFTRACE build); `[rev5]` from
row 1, the handed rates' digest, each candidate's price, the qualifiers and bands. ONE plan out.

## The designer/emitter split

This mechanism IS the kit's planning face (roadmap §0a) and stage 1 IS A-PLAN's first step (D186
add. 1 A6), with the roadmap's ratchet accounting (§Staging).

| stage | owns | in this design |
|---|---|---|
| pcrec, the designer | facts and legal choices: spans, candidate positions with their rates, alternatives with entry, floor, frame facts, byte rates and their source, the set | states them once per site; never a CHOSEN position, method or cost `[rev3 O6]` (D157; D167 add. 1 A11's landmark-admission exception stands until restated in code) |
| the kit's planning face | candidates, the question tables, the pick, (later) the cards | phase 1: facts in, one plan out (alternative, stop, verify plan, test forms) plus its trace |
| pcrec's rules | engine, route, crossings (`next_keys`, FIRST/NEXT rows) | reads the reply as NEXT reads the phase-1 reply today (window_site §2.4) |
| the kit's emitting face | frame, method and renderer rows, then text | phase 2: plan + frame in, C out; golden plan-in/C-out tests per seam |

**What moves across** `[rev3 P1]`. In stage 1 the reply does NOT grow (method, resume and frame stay
phase-2 answers; only 1f's entry removal is an MF_SITE_ABI event). It grows (method, resume, frame
row) at unit 3.0, when the plan call takes the frame.

**A-PLAN's open points.** (1) ONE PLAN WITH ITS TRACE (D186 add. 2; `[rev5 D1]` it amends A-PLAN
OPEN POINT 1, already edited on main, 5e8bcf455/b405ff811; no roadmap edit is left to stage 1).
**The plan face is a PURE FUNCTION** (D186 add. 2) of (site facts, frame: engine/target/layer,
measure set, handed rates): same inputs, same plan, no hidden state. `[rev5 C1]` One plan SUFFICES to
compare scenarios once its price is readable (REVISIT TRIGGER: whole-artifact pricing un-deferred);
until then the reply carries no price (trace only, MFTRACE) and scenarios compare by the bench.
`[rev5 C2]` **Axes**: site facts are per CALL (`mf_wdecide(art, site, out)`); the frame is no input
through stage 1 (window.c :1061; layer hard-coded, finder.c :934), per call from unit 3.0; the set,
the handed rates, denies and levers are per ART (`mf_art_begin`, compose.c :869-882): a new art.
**Purity breakers today** (unit 1d; grep of memfn/src for mutable statics and `art->` uses): (a) the
sticky `art->err` refusal (window.c :1062; compose.c :960); (b) the call-order label `art->nsites +
1` (window.c :997, :1007, :1734, :1818; finder.c :930; ofsskip.c :486; compose.c :268, :281), trace-
only (gate.c :936), must stay unread by rows; `[rev5 C4]` (c) gate.c :850-856's process-global reach
counters and `trace_arts`, READ by `reach_print` (gate.c :884-900) and tests/memfn/rows_check.py
(`asked` = the phase=ask FD records): only the TAKEN call counts, or a probe mode; (d) `art->consulted`
(compose.c :1303, set by T-PICK rows, rev 3 C7), likewise. No cache. `[rev5 C3]` `wused & ~wemitted`
(runcmp.c :515) and `simd_inc` (ofsskip.c :565-567) decide emitted text first-use-wins: the EMITTING
face is order-dependent by design, so 1d's "repeated and reordered calls give equal plans" is scoped
to the plan call. (2) Helper sharing stays emit's, cost-free. (3) Run-time dispatch stays held. (4)
Cards are tables keyed by class and regime. (5) `--memfn=no-X` denies become filters on T-FIND and
T-PICK rows (D147 add. 9). (6) The same-commit abi rule is unchanged.

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
arrives with the first priced row. `[rev5 A5]` KEY, M and TIE ARE THE INCUMBENT of every priced
comparison (§The pick 2), so they stay while any priced row reads them; each retires only when a
census shows no site reads it as a pick OR as an incumbent, as its own no-mover step (restates rev 3
R7, §Staging row 1).

**Named exceptions** `[rev3 P4]`, each a second decider kept on purpose, with its retiring trigger:

| decider | answers | retires when |
|---|---|---|
| generic.c's per-byte RUN chain | T-CMP | U8's unit change |
| `fn_rows` BODY (ofsskip.c :414-416) and the RESEED KEY row's `scan_ok` | T-FIND on OFS sites (no consumer kind: 371 of 371 RTE OFS sites) | pcrec states a kind on OFS sites |
| `fn_rows` PREFIX (own denies `vrun-w32`/`vrun-w16`) and vrun's KA/KB (U7) | SIMD rungs | `[rev5 D4]` the census rule: a census shows no site's rung is decided by them (every SIMD rung a T-FIND rung or a SIMD T-PICK row's, C9) |
| compose's `arms[]` as the frame selector of NON-plan sites (carries the `precheck-assign-byte` deny) | frame + method off the plan call | outside Goal 3's plan-call scope; joins when a kit request adds an arm |
| `fd_pres` chain order, `implied_by` | T-PRES | presence joins the call ([MEMFN-UNBOUNDED-SPANS]) |
| the asker fact (the one T-FIND walk answers per asker: E-find with it, legacy rows without) | T-FIND per frame | unit 3.0 (plan takes the frame) |

**The decider census** `[rev3 P4]` (Goal 3's check, per unit HEAD): a committed map `decider ->
table` (one line per deciding function; written by stage 1's first lane at its base, kept by each
unit's lane); a grep over `memfn/src` for argmin and walk shapes (`kit_walk(`, `< best`, `< bm`,
`tie_takes`, `TIE_`, `[rev5 E1]` and the qualifier filter `< inc`) whose every hit must be mapped to a
table or a named exception, red on an unmapped hit; one sabotage row: a byte-identical copy of
`run_member`'s loop added elsewhere must go red. `kit_walk` reach stays a population count, not the
census (plain-loop deciders leave no reach).

**Growth rule.** A new scenario adds no table; a new method adds a T-FIND row and card (D176).
`[rev5 E2]` **Families, unified at row 1** (trigger: the `enter` cards): "beat the incumbent by a
margin" (MARGIN, §The pick 3's qualifier test, T_BAND -> TIE_DEFAULT, `pcrec_landmark_margin`); the
pure queries (`mf_ask`, `mf_wdecide`, `mf_pres_ports`). KEY and the pick read ONE handed rate table.

## The pick

**Stage 1: no prices.** The default is TODAY's plan (KEY, M, TIE, then phase 2's frame and method);
nothing reads a cost but KEY/M's `plan_cost.def` integers, C-model's truncation order kept.
**Stage 3: T-PICK rows, all priced** `[rev3 A2]`: a condition on stated facts, the LEVELS it opens
(method, position, alternative), the priced action, its deny, its per-regime evidence; `keep` last.

**The rates** `[rev5]` (D186 add. 2 as amended; owner: "kit wouldn't know anything about default
analysis as pcrec would simply send the default as the analysis"): the kit receives ONE byte-rate
table with its digest, or none, as a fact (D157), resolved by pcrec (§pcrec-side findings), and never
distinguishes a bundle from the default. No rates or no card set: rules only.

**The priced action** `[rev5]` (after stage 2, one row at a time; r = the handed rate table):
1. CANDIDATES are the complete plans that differ from the incumbent only at the row's levels, built
   from site facts alone (no rate input), so a blind and a with-data compile of one site see ONE
   candidate set. Each is priced under r; nothing else is priced.
2. `[rev5 A5]` The INCUMBENT is today's plan (KEY, M, TIE as stage 1 keeps them) evaluated under the
   same handed rates (as KEY's A-mass reads them today: smp20 handed `prose` stops at '4',
   `witness.out`), its NONE answers when none were handed (`findings.md` §4¶1).
3. c QUALIFIES when `price_r(incumbent) - price_r(c)` exceeds their band. The pick is the CHEAPEST
   qualifier, else the incumbent. `[rev5 A3]` Only qualifiers tie: those within band of the cheapest
   go to TIE's rows (D176 Q5), never the incumbent (within band it stays: T_BAND -> TIE_DEFAULT); the
   method-level tie row is row 1's design item. A never-qualifying candidate cannot move the pick.
4. Unpriced incumbent: keep. Unpriced candidate (no card, or a card without noise): cannot qualify;
   a missing `noise_e6` is UNMEASURED, never 0, so it means no departure. No rates handed: keep.
5. A renderer addition that flips a T-FIND first match moves the DEFAULT: its own row and evidence.
6. `[rev4]` SIMD (C9, D186 add. 2): a `-fmemfn-simd` build may pick its own position by its OWN T-PICK
   row (SIMD-form cards, SIMD-on evidence, scalar the bar); else SIMD forms are rungs (D147). Witness
   utf8-lead-no-cont `[\xc2-\xdf](?![\x80-\xbf])`, NOT smp20. `[rev5 D4]` Its candidate shape and
   card keys are that row's own design.
7. `[rev3 R5]` Each row states whether it applies on pre-check parts, where pcrec scans the reply's
   run member, not its stop (`req_run_member`, emit_dfa.c :1045-1077).

**With data** `[rev3 WD, rev5]` (pcrec hands a named bundle's rates, B; plan [BENCH-WITHDATA]): the
kit runs the same action on the one table it was handed; the band adds the sampling noise pcrec states
with it. `[rev5 B4]` The target is B's cheapest qualifier,
within band to TIE (smp20 with `prose`: '4' is incumbent and B's least: no departure).
**The property** (the owner's bar, plan [BENCH-WITHDATA]; scope CONFIRMED by the owner 2026-11-02:
"The analysis data must match the test subject to require same-or-better results."): on every cell
whose subject kind B describes, a with-data compile matches or beats the blind compile beyond noise.
**Why the structure gives it** `[rev5]`: the blind pick c_P is a with-data candidate (step 1, where
the two incumbents agree outside the row's levels; elsewhere the NOT-covered census below); if it
qualifies under B the pick is no dearer than it, else `price_B(c_P) >= price_B(inc_B) - band` and the
pick is inc_B or cheaper: within band of c_P or better, whatever P chose. The MEASURED
cell then holds when (i) the cards' regime is the cell's (long subjects; per-call cells need
[SPAN-PICK-PERCALL]'s term); (ii) model error (independent positions) stays inside the band; (iii)
the cell's subject is B's kind within B's sampling noise (a held-out sample, never the timed bytes);
(iv) the site is one a priced row admits. A with-data loss is therefore a broken (i)-(iv): a
mechanism finding ([BENCH-WITHDATA] item 4), never a trade. NOT covered: sites no priced row
admits, where KEY reads B (today's); the census finds their losses, each answered by a priced row.
`[rev5]` [BENCH-WITHDATA]'s blind testee is P-only, stable as bundles are added; its bar unchanged.

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

**The band of a comparison** `[rev3 C3, rev5]`: for prices a and b under one model, the quadrature
sum over cards of `(coef_a - coef_b) x noise` (a card both read with one coefficient cancels), plus,
with data, B's sampling terms: a difference of two prices, smooth (rev 4's kinks at `max`/`min` are
gone with the minimax). No constant enters but the card gates (`gate_e6` 3 %, UNMEASURED DEFAULT,
D149). `[rev5 A4]` Stage 2 defines: a COVERAGE FACTOR, labelled UNMEASURED DEFAULT (1 sigma departs
~16 % of equal-price comparisons per side); B's sampling noise by block bootstrap per bundle byte
(Poisson `sqrt(n)` is 0 at n = 0, 2-5x low on clustered text), STATED by pcrec with the rates; no
stated noise (an authored default, a `fidelity synthesized` bundle) means no sampling term.

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

MARGIN (2x, ARGUED) stays M's default until the PARKED and RESEED `enter` cards exist. `[rev3 C10]`
Stage 2's card question: a per-(kind, entry) card may bake in its fixture's survival; the
alternative is a pcrec-stated survival fact x a per-byte card. OFS sites state no kind (no `enter`
key; fine while T-FIND declines on OFS). MAX_SET is no card; U9 closes by a grep of its readers.

**Noise reaches the kit.** `mf_measure` has no noise field (68 kit rows, `noise_e6` '-'). Stage 2
owes `[rev3 C4]`: a kit request (main's); a noise field (MF abi event, `measure_sets.md` §4.1,
`match_api` hunks); a producer; derived rows by quadrature; noise in `values_digest` (a digest-version
event, `measures.md` §3.3¶1, §5¶4, readers by grep), or a FILE set may not share a committed id.

**Where they live** `[rev3 C5]`. The span cards are quantities of the grid's successor method
(`kit-grid@2`); the grid keys are re-measured under it. `[rev5 D2]` The set is a FRESH id,
`zen4-grid3` (D186 add. 2; `zen4-grid2` is D167's 2026-10-16 slot, named by its readers, never
reused; `measures.md` §8¶1). Embedded by `make gen-measures`, handed on `mf_art_begin`; chosen by
`--measures=NAME`, else `DEFAULTS` (`measures.md` §5¶6); measured by quiet-gated `idle-ok` jobs.

## Robustness to the byte rates

`[rev5]` **Robustness is MEASURED, by each row's regimes, not modelled in the pick** (D186 add. 2 as
amended 2026-11-03). The weakest input is P: PRIOR_AUTHORED (`a322116b1b87f9f6`) rates {x,X} 1,097
ppm, '/' 4,154; job 588's subjects held x 2,338 vs '/' 1,026 candidates on real text, 1,388 vs 0 on
none, 21,788 vs 10,856 on random (t588tri §a). **The rule** `[rev5]`: the kit prices under the one
table handed (blind: pcrec hands its default, P; no flat kind, no shipped bundle, no minimax); every priced row's D186 evidence MUST include a random-like
regime (job 588's `random`) beside real text and none, and a regime it loses beyond noise narrows the
row or is an owner exception. A wrong P is a DATA question: a default-prior change is a deliberate
data event with its census (§What moves). **Model error** is NOT in the band: `[rev3 C3]` row 1 runs
with it UNMEASURED, guarded by its predicted-vs-measured print per mover (R5.3), whose spread the NEXT
row adds.

**What the formula says for smp20** `[rev5]` (`span_pick/smp20.py`, `smp20.out`, 2026-11-03; bundles
and incumbents from `witness.sh`/`witness.out`; STAND-INS labelled in its docstring: byte(memchr)
0.06 = C_MEMCHR, byte(PAIR) 2x, hit 20, cmp 2.5, enter 20). Per 1e6 bytes, hit(PAIR) 20 (40 in
brackets where it differs):

| source | @0 {X,x} PAIR | @1 {/} | @4 {3} | @5 {4} | least | today's (incumbent) | pick |
|---|---|---|---|---|---|---|---|
| blind: P | 144,694 (166,634) | 153,476 | 228,231 | 228,231 | {X,x} ('/') | {X,x} | {X,x} ('/', 1.086x) |
| with `prose` | 168,871 (212,311) | 72,938 | 66,143 | 63,555 | '4' | '4' | '4' |
| with `log` | 128,384 (135,824) | 385,409 | 760,657 | 854,238 | {X,x} | {X,x} | {X,x} |
| with `weblog` | 286,612 (434,532) | 1,225,432 | 441,512 | 302,235 | {X,x} ('4') | {X,x} | {X,x} ('4', 1.438x) |

`[rev5 B2]` Under P, '/' is least only at hit(PAIR) 40. `[rev5 B1]` **Boundaries, EXACT** (linear in
k = byte(PAIR)/byte(memchr) and in hit(PAIR), solved in rationals; GRID: hit(memchr) h1 5, 10, 20,
40 x hit(PAIR) 1, 2, 4, 8 x h1; cmp, enter fixed). Blind, default arm, the challenger always '/':
{X,x} kept for k < k* (h1 5, 10, 20, 40):
1x h1: 1.382, 1.637, 2.146, 3.165; 2x: 1.291, 1.454, 1.781, 2.434; 4x:
1.108, 1.088, 1.049, 0.971; 8x: under 1 ('/' at every k >= 1). At k 2, '/' wins at every hit(PAIR)
for h1 <= 10, above 28.0 at h1 20, above 103.7 at h1 40. Job 588's none cell (read as k ~2.3 at hit
20; directional, Zen 1 stand-ins) lies just above k* 2.146: the cards decide; either answer is the
default's. `[rev5 B3]` DEF arm: '/' is P's cheapest at every grid h1, no move (rev 4's minimax moved
it to '3'). With data over the grid x k 1.00-12.00 by 0.05 (3,536 points): `prose` '4' everywhere;
`log` {X,x} 1,502, '/' 2,034; `weblog` '4' 3,438, {X,x} 98.

**Uncovered** (review r1 C5). Where real text is far from P (UTF-8 lead bytes, case-folded pairs,
dense classes), P is wrong (R-33's `utf8/alt-cyr-64`). `[rev5]` Under `-e utf8` blind is NONE today
(`findings.md` §2¶7); the gap is byte-encoded compiles over UTF-8 text: priced rows over two-member
stops are gated on a fix (an encoding fact, or a per-encoding default prior). **Nothing is tuned.**

## The watched witness

`[rev3 A2, WW; rev5]` smp20 `(?i)x/1234` is resolved by data, never by a rule, read TWO ways at
every stage; `[rev5 B3]` from stage 3 each arm (default, `--engine=vm`, both layers, the DEF deny) is
judged by its own new/old, not RTE/DEF. (1) BLIND, "consistent with the default" (D186 add. 2 as
amended): the priced action on the default rates pcrec hands (P), re-priced pcrec-side; correct by definition, {X,x} or '/'; job
588's blind timings judge P, and a wrong P is a data question at the last planned step. A blind pick
that is NOT P's cheapest qualifier is a mechanism problem. (2) WITH a text-like bundle: a one-member
stop the bundle rates rarer than {x,X}, '/' or '4' (D186 add. 2): passes TODAY ('4') and must at the
last planned step (stage 3 row 1), else a mechanism finding. **Forecast** `[rev5]`: on the stand-ins
P keeps {X,x}; the cards may land above k* and move blind to '/'; real-text cells close through (2).
The text-like bundle until [BENCH-WITHDATA]'s held-out one: `prose` (GPL-3 + GFDL-1.3 + Apache-2.0
by `pcrec-analyze`: {x,X} 2,172 ppm, '/' 575, '4' 158; job 588's real text 2,338 vs 1,026), made in
scratch by `witness.sh`, never committed. `log`/`weblog` (rate '/' 14,462 vs {x,X} 372; 51,754 vs
7,396) are with-data rows only, never blind inputs. `[rev5 B7]` Each witness compile names its card
set: `DEFAULTS` until M2, then `--measures=zen4-grid3` (after M2 a bare compile prices nothing).

| stage | (1) blind | (2) with the prose bundle |
|---|---|---|
| today = stage 1 (byte-identical; re-compiled 2026-11-03, 16 compiles, `span_pick/witness.out`, blind and `prose` lines unchanged) | @0 {X,x} PAIR on default, vm and SIMD-on; '/' on the DEF deny; stamp `byte-rate=default:1822fb973b95a4da`; job 588 1.58-4.03x | @5 {4} memchr on default, vm and SIMD-on (KEY A-mass reads the bundle); PASSES. DEF deny: '/' and '4' |
| stage 2 (cards measured, no reader) | unchanged; the forecast becomes a reading: is the measured card point above or below k*? | unchanged |
| unit 3.0 (plan takes the frame) | unchanged (no priced row yet) | unchanged |
| stage 3 row 1, the LAST planned step | P's cheapest qualifier, {X,x} or '/' per arm, departing only beyond noise; job 588 per regime judges P | the incumbent '4' stays unless a qualifier beats it beyond band (on the stand-ins none does); must PASS, else a mechanism finding |

## Staging under D186

D186 (TRIAL): a UNIT change (bar: no regime slower) or a CHOICE change (a row on stated facts with
per-regime evidence; a losing regime narrows the row). **Choice-row losses** (D186 add. 2): D144
governs WHEN and HOW (an issue row, the deny the interim kill switch; a disaster denied or reverted at
once); D186 WHAT the fix is: narrow the row, or an owner-approved exception. Unit changes (1a-1f, 3.0,
smp04) stay under D144 alone.

**Stage 1: unify, today's answers kept: A-PLAN's first step.** No-mover units, each with its own
byte-identity witness; one that cannot be byte-identical lands alone as a unit change with its deny.
`[rev3 P3]` A finder row added or removed ahead of the PRES rows is an MF_CLASS_V event (pres_row).

| unit | content | deletes |
|---|---|---|
| 1a dead code `[rev3 P3]` | N3 `mf_set_terms`; inert rows R3a/R3b/R4 (no deny; zero reach by code); MF_CLASS_V (pres_row shift) | 4 members |
| 1b primitives `[rev3 S1, S2]` | U4 one mass primitive over a POSITION MULTISET (a list of cubes, a repeated byte counted per position, as `window_mass`: a set-shaped primitive moves `run_window`, e.g. `zzzzzzz~J`), a capped/uncapped argument, the NONE-mode total (62,500, not 62,496); the landmark admission's per-factor round-up product stays its caller's; U5 `wf_ties` with the presence-member row and presence's run window reading T_WINDOW | 2-3 mass variants, 2 tie spellings |
| 1c kit-only spellings `[rev3 S1]` | U2: P3's `run_scan` asks `run_member`; translate's run rank reads T_MASS_STRETCH, `rank_pos[0]` asserted against `run_member`; U6 the kit's landmark shadow (presence.c :222-245) retired if no census reads it | 2-3 |
| 1d planning core `[rev5 C5]` | one candidate builder; KEY/M/TIE as the default; T-VERIFY as a step list with C-bound and the run member; trace without prices (U1 as two KEY rows, U10 = Table C + ofsskip's legacy plan, N1, N6); PURITY: breakers (b)-(d) fenced (unread by rows; reach and `consulted` counted on the taken call only, C4), (a) fixed only if every error path keeps its outcome and diagnostic, else it leaves stage 1 as its own unit change; witness: plan calls repeated and reordered give equal plans (plan face only, C3) | `a_model_choose`'s private enumeration, `mass_domain`'s copy |
| 1e phase-2 tables `[rev3 P1, P2]` | T-FRAME (legacy first) at text time; T-FIND as ONE walk with the asker fact, Horspool first; the renderer row (B-fn/B-pair, reconciliation kept); compose `arms[]` and `fd_find`'s text become renderers keyed by (frame row, method row, renderer row) (U3 less OFS, N5, N11); no MF_SITE_ABI event (the reply does not grow); MF_CLASS_V if the Horspool row's move shifts pres_row | `fd_find`/`fd_route`'s second entry walk |
| 1f retired denies `[rev3 P3]` | R8/R1/R2 with `fd-r8`/`fd-ndisp`, the §2.5 pay rule (`fd_pay`, `pay_fill`, `n_interval`) and the public `mf_finder_pay`; CALLER-VISIBLE, not a no-mover: `registry.md` §6¶8a/§6¶8b hunks (floor 14 -> 12), `--list-axes` re-pin, `emit_sweep.py`/`memfn_arm.py`/`finder_check.py`/rows edits, an MF_SITE_ABI event | 3 rows, 2 denies, the pay rule, 1 entry |

**Witness, per unit**: `scripts/emit_sweep.py` byte-identical over the corpus, the bench patterns and
job 588's sample on EVERY arm (default, each `--memfn=no-X` deny, `--engine=vm`, both SIMD layers),
stamps included; `*_movers.txt` unchanged; reach floors; G2; the census. **Ratchet** (roadmap §5;
proposed for main): find-method deciders (`fd_route`, `fd_find`, compose's method walk, `fn_rows`
BODY; members − 1), position enumerators, mass variants, tie and run-member spellings, the landmark
shadow, inert finder rows (`b_fn_holds` is FRAME family), counted at stage 1's base; each unit lowers
its row. **Sequencing** (D153): opt rows touching window.c, finder.c, ofsskip.c, compose.c or
presence.c carry "remodel overlap" and wait; O3 = WAIT (D186 add. 2): smp04 and the look-ahead too.

**Stage 2: measure the cards** `[rev3 O1, A2]`, directly after stage 1 (D186 add. 1 A2): §Cost cards
(scalar and SIMD forms), the noise channel (coverage factor, bundle sampling noise), the id
`zen4-grid3`, the step-0 gate; `[rev5 D5]` and [PAIR-LOOKAHEAD-TIME]'s width sweep (its trigger, the
pair card's set revision, fires here). No reader, zero movers, stamps and `DEFAULTS` unchanged.

**Stage 3: priced choice rows, one per change.**
- **Unit 3.0, the plan takes the frame** `[rev3 P1]`: pcrec states form, handoff and site_kind per
  NEXT row's frame at phase 1; the call takes hooks and phase set; the reply grows method, resume,
  frame row; the asker fact retires. Byte-identical; one MF_SITE_ABI (+ MF_CLASS_V).
- **Each row**: one T-PICK row naming its levels; a deny with a D174 name (`registry.md` §6¶8a,
  `cli.md` §2.4¶1); `[rev3 R1]` a 588-style run, RTE vs the row denied, on EVERY arm (scalar the bar),
  `[rev5]` a random-like regime among its regimes, its movers census per arm from artifact diffs;
  `[rev3 C7]` `consulted`; `[rev3 C8]` its drop-F witness or the plant UNREACHED; `[rev3 R5]` its
  pre-check-part statement; its pcrec abi event and spec hunk.
- **Row 1** `[rev3 A2]`: the first priced departure, admitting smp20's class (NONE alternatives
  whose default is a two-member stop), job 588 its evidence, §The watched witness its reading.
  `[rev3 O2]` Acceptance also against the rule-list pilot (0.981 of ideal, [PRICE-BAKEOFF]), re-run
  after each priced row, D186's drift gauge. `[rev3 C6]` Row 1 flips `DEFAULTS` to the new set.
  `[rev5 A5]` R7 RESTATED: at row 1 A-model's one-member preference (`scan_ok`) and A-mass
  meet in T-PICK's priced departure, not in KEY: KEY's two rows stay as the incumbent and retire only
  by the census of §The tables (no site reads them as a pick or as an incumbent).
- `[rev3 O7]` **Ratchet delta**: T-PICK with its `keep` row falling to KEY is one table (delta 0 at
  row 1); each later row names the member it deletes or is rejected at review (roadmap §0).
- `[rev3 R9, rev4]` **Batch gate**: choice-row losses above. **SIMD rows** (C9): §The pick 6.

**Later rows** (each its own change; none scheduled): Horspool priced (D176 Q2; deletes HORS_MIN;
`hors.probe`, `hit(walk)`, `hit(hors)`; hex8-bounded and the five other D-hors sites). RESEED at any
set size (PF E-stmt: [MEMFN-PAIRSTOP] or walk-only, both `enter` cards). Dense pairs (after
[MEMFN-PAIRSTOP] and the C5 fix). smp04 `[a[:b]`: a UNIT change. `[rev5 D5]` [COVER-PRICE-WITNESS]
(x1.95 on the SCALAR layer too; bar both layers): its SIMD half is the C9 row's, its scalar half a
scalar priced row admitting its class.

## What stage 1 deletes

| id | stage 1 does | unit | later |
|---|---|---|---|
| U1, N1 | one candidate builder; A-model and A-mass stay two KEY rows; C-model same arithmetic | 1d | meet in T-PICK at row 1; KEY retires by census `[rev5 A5]` |
| U2, U5 | `run_scan` asks `run_member`; translate's rank and the run window read `wf_ties`; presence-member row `[rev3 S1]` | 1b, 1c | pcrec's two and its PICK: findings |
| U3, N4, N5 | one T-FIND walk with the asker fact (N4 kept, renamed `[rev3 P1]`); arms/`fd_find` text become renderers; not on OFS | 1e | the asker fact retires at 3.0; OFS joins with a kind |
| U4; U6 | one primitive over a position multiset, NONE-mode total kept `[rev3 S2]`; the kit's shadow retired if no census reads it | 1b; 1c | pcrec's findings.c copy stays (D157); pcrec owns admission (D167) |
| U10, N6 | T-VERIFY = Table C + ofsskip's legacy plan (PRES ordering is T-PRES's `[rev3 S3]`); candidates -> T-VERIFY -> default | 1d | priced rows |
| N11 | Table E becomes T-FRAME at text time, order kept, plus the renderer row `[rev3 P1, P2]` | 1e | plan-time at 3.0 |
| N3, N14, R3a/R3b/R4; R8/R1/R2 + denies | deleted (zero reach); retired with registry hunks `[rev3 P3]` | 1a; 1f | — |
| kept | U7/N10/N12 (SIMD; SIMD-form cards in stage 2), U8 (unit change), U9 (boundary), N2 (MARGIN), N7/N8/N13, N9 | — | a SIMD T-PICK row (C9); U8; a reader grep; `enter` cards; priced rows |

## pcrec-side findings (for main; not changed here)

- **Run pin and scan index**: `pcrec_find_run_scan_index` (findings.c :745), `_window_start` (:780),
  `pcrec_run_pin` (kset.c :294) restate the run member (held by `req_run_member`, emit_dfa.c :1058).
- **Landmark admission** `[rev3 O6]`: `req_landmark_admits` (emit_dfa.c :9064) and lmwalk's
  `lc_rarity` share `pcrec_landmark_margin` (+ `LMWALK_K_HIT_UNMEASURED`): a D157 EXCEPTION (D167
  add. 1 A11) until pcrec states the landmark as a candidate and reads `find.hit`.
- **The rate source, pcrec's resolution** `[rev5]` (D186 add. 2 as amended; first match, one per
  compile; pcrec hands the kit the chosen table and its digest, or none; pcrec's stamp and trace name
  the source, the kit's trace only the digest):

| # | when | pcrec hands | pcrec's stamp |
|---|---|---|---|
| 1 | an `--analysis` chain answers `byte-rate` for this compile's encoding (`findings.md` §1, §7) | that bundle's rates, B | `B:digest` |
| 2 | else the built-in `default` serves this encoding (`findings.md` §2¶7: today `-e byte` only) | the default's rates, P | `default:digest` |
| 3 | else | none (rules only, as M2's unknown target) | none |

  Today's code already (`pcrec_find_byte_rate`, src/core/findings.h :300; `findings.md` §6¶3, §7¶6;
  `witness.out`). `[rev5]` Kit grep (memfn/src + memfn.h): no built-in rate table, no fallback table;
  `kit_byte_rate` returns the handed table or NULL (presence.c :48-56); NULL takes the uniform-mass
  NONE answer (presence.c :58-113), arithmetic, no table. The interface still CARRIES the source:
  `mf_prov.source` PRIOR_AUTHORED/MEASURED and `bundle` "default" (memfn.h :1212, :1224-1225); no kit
  `.c` reads it; whether the field stays is main's call.
- Prerequisites pcrec-side: `[rev3 P1]` unit 3.0's per-frame ask; a consumer kind on OFS sites;
  [MEMFN-UNBOUNDED-SPANS]; [MEMFN-PAIRSTOP]. `next_keys` and lmwalk's route stay architecture's.

## The measurement regime

RELEVANT. Each card names its regime (§Cost cards; landing flips walk vs stream choices,
walk_vs_v1 §3). Per set: box, compiler, Linux verdicts, `taskset`-pinned, scalar the bar. Prices are
long-subject; row evidence regimes are job 588's (throughput, search_short, match x real, none,
random, dense); `[rev5]` a random-like regime is REQUIRED in every row's evidence.
`[rev3 C11]` Non-card numbers the pick reads: KEY/M's `plan_cost.def` integers (Zen 1, a box
mismatch until they retire); C_ENTER (MEASURED x ASSUMED); MARGIN (2x, ARGUED); HORS_MIN
(PROVISIONAL); `gate_e6` and `[rev5]` the coverage factor (UNMEASURED DEFAULTs); the ONE handed
rate table (pcrec's resolution; the kit sees its digest). smp20's flip: k* per hit pair (§Robustness).

## The independent control

RELEVANT.
- **Answers:** G2 against the scalar byte loop; the `.rxt` oracle under every committed set plus
  synthetic extreme sets forcing each T-FIND row (`measure_sets.md` §8). **Stage 1 and 3.0:** the
  §Staging witness counted pcrec-side from artifact diffs, never the kit's `moved` (K35); the census.
- **Priced rows:** predicted price vs measured time per mover (R5.3; validation sites share no
  number with the cards, R5.2). `[rev3 C7]` A pcrec-side python re-price from the stamped rows (no
  kit code) `[rev5]` recomputes source (from the stamp), prices, incumbent, qualifiers and pick,
  diffed against the artifact's; its tests by a spec-first (D27) author from §The pick (review r1).
  finder_check.py checks D and F's true arms at row 1. A swapped-cards plant moves a reach witness.
- **With data:** [BENCH-WITHDATA]'s compile-only census (blind vs each bundle, movers listed) and its
  held-out bundles (no training on the timed bytes). **The watched witness:** job 588's timings judge
  smp20's pick per regime, never the kit's own price.

## What moves when the data is regenerated

RELEVANT. Only picks and the `<PREFIX>_MEASURES` / `_FINDINGS` stamps move. The measures stamp (""
today) becomes `id@rev:digest` where a pick consults the set and changes on every card rev (stamp-
only movers: their own class). A byte move is an abi event (D76/D94, readers by grep) with its
per-arm census; `measures.md` §8/§5 hunks. `[rev5]` **Rate sources.** A shipped, added or recounted
bundle moves NO blind compile (`findings.md` §6¶3), only compiles naming it. A DEFAULT-prior change
(the `default` bundle, per encoding) moves blind compiles: a deliberate data event with its census,
logged (D186 add. 2 names `DEFAULTS.log`, which today logs set defaults only: the byte-rate line's
form is main's). `[rev3 C6]` **Defaults.** `DEFAULTS` (`idk zen4-grid1@1`) holds no span card, so
bare compiles keep the incumbent until row 1 flips it, with its census (`measures.md` §5¶6, §8¶3).
At M2 ([MEASURE-SET], D166 add. 2) the idk default excludes every per-byte cost row: priced rows go
dark on bare compiles, INTENDED ("an unknown target prices nothing"), M2's dependency (main records
it and M2's order against row 1). Stage 1 moves no emitted byte (1f: `--list-axes`, two options);
stage 2 and 3.0 move nothing; row 1 moves its movers and its sites' stamps.

## Owner rulings since rev 4

Durable home of rows 1-6: D186 add. 2, "Blind compiles use the default" (main 5d42c5618).

| `[rev5]` ruling | landed in |
|---|---|
| A blind compile uses the DEFAULT: one rate model by pcrec's first-match rate-source table; the kit sees only the handed rates and digest (correction, D186 add. 2 as amended); pcrec's stamp and trace name the source | §pcrec-side findings (table); §The pick, "With data"; §The shape; Goal 5 |
| A blind pick depends only on pattern, target, stamped defaults; a bundle never moves it | Goal 5; §What moves |
| Robustness leaves the pick (F, minimax, kind list, pairwise form dropped); every row's evidence has a random-like regime | §Robustness; Goal 2; §Staging; §The measurement regime |
| A default-prior change is a data event with its census (log form PENDING-RECORD, main) | §What moves; §Robustness; Non-goals |
| [BENCH-WITHDATA]'s blind testee P-only and stable; with-data bar unchanged | "With data" |
| smp20 blind "consistent with the default"; a wrong default is data at the last step; with data '/' or '4' (and add. 2's witness line) | §The watched witness; Goal 5; smp20.py |
| Review r1's A2 and B6 dissolve (memfn journal 2026-11-03, 0304257b3) | disposition below |

**Rev 4's rulings, homes** `[rev5 D3]`: each its own D186 add. 2 line (minimax struck; D186 over
D144, C9, one plan, pure function, witness wording, O3, `zen4-grid3`); M2-dark: PENDING-RECORD.
**Review 2026-11-03 r1, by id** `[rev5]`: A1 SUPERSEDED (pairwise qualifier test). A2, B6 DISSOLVED.
A3, A5 (R7 restated), B1, B2, B4, C1-C5, D1-D3, D5 FIXED. A4 kinks MOOT, noise PLAN (stage 2). B3
RE-CHECKED (no DEF move). B5, E1 DOC. B7 PLAN. D4 FIXED + PLAN. D6 MOOT. E2 NOTED. r2: rev 3.
**For main**: rows [SPAN-PICK-UTF8], [SPAN-PICK-PERCALL], [PICK-IDIOM], an [IFACE-PUSH] class option,
the ratchet rows; `[rev5]` the byte-rate default's log line; M2's order; `mf_prov.source`'s future.

## Open questions

`[rev5]` None for the owner.

## STATE AT HANDOFF

OWED none. Lane spanpick5: rev 5 + the kit-sees-only-handed-rates correction; `smp20.py`, `smp20.out`,
`witness.sh` (16 compiles), both CLAUDE.md rev lines. No make, no timing. Not a build go.
