# span_pick — the kit's ONE "find the span" choice mechanism (design, rev 5.2)

**Status: PROPOSED, rev 5.2 (lane spanpick52, 2026-11-03): THE TEXT THE STAGE-1 BUILD FOLLOWS. Design
only: no build go by itself, no code, no make, no timing.** `[rev5.2]` Rev 5.1 plus the diff check's
C1-C8 (review r2's `CHECK_rev51.md`). `[rev5.1]` Rev 5 plus review 2026-11-03 r2's FIX-NOW items as
ruled, and main's 7f55a62f9/fa736a260 rulings. Read §Staging's stage-1 tables and §The pick first;
marks `[rev5.2]`, `[rev5.1]` and older stay. Evidence: `units_inventory.md`, `r33_report.md`,
`t588tri_report.md`, `bar588_report.md` (job 588), `window_site.md` rev 3.3, `measure_sets.md`,
roadmap §0a/A-PLAN/§5; `span_pick/`. Code cites re-checked at main 2636dee99 (code tree = 4f9368e7c).

## Goals

Ranked; a higher goal wins a conflict.

| # | goal (who benefits) | measurable form |
|---|---|---|
| 1 | **Answers exact** (every caller) | every plan the tables can produce yields exactly the candidates its facts define: G2 (`memfn/tests/run_g2_win.sh` and the finder G2) green against the scalar byte loop, every plant red; zero corpus answer changes at every stage |
| 2 | **No regime slower beyond noise** (users of the default build; D186's bar) | stage 1: zero movers on EVERY arm, no pcrec abi number change `[rev3 P3]` (1f is a caller-visible step of its own; `[rev5.1]` 1f/1g are MF_SITE_ABI events, 1a/1f/1e MF_CLASS_V events, none moves a byte); stage 3: each row's movers read new/old <= 1 + the A/A floor in every regime and arm of a 588-style run, `[rev5]` a random-like regime among them, else the row narrows or is an owner exception |
| 3 | **One table per question** (the next editor; `architecture.md` "One table per slot") | `[rev3 P4]` after stage 1, for plan-call sites: six question tables and three pick-side tables (KEY, M, TIE; T-PICK arrives with the first priced row), plus the NAMED exceptions of §The tables, each with its retiring trigger; check: the decider census of §The tables, which can fail |
| 4 | **Costs measured, by target class, none hand-set: the END STATE** (D186 add. 1 A1; D176 Q1/Q3) | no priced departure before its cards are measured; every cost a priced row reads is a declared row of the stamped set (checked); `plan_cost.def`'s Zen 1 rows retire with their last reader |
| 5 | **Blind picks are the default's, data never hurts** (users of common patterns) | `[rev5]` a blind pick depends only on the pattern, the target and the stamped defaults: no bundle moves it; smp20 `(?i)x/1234` blind is "consistent with the default" by definition (E1); with a bundle matching job 588's real text it moves to '/' or '4', RTE/DEF <= 1 + floor there (§The watched witness); the six D-hors sites keep their wins (0.57-0.78); `[rev3 WD]` with data matches or beats blind; a win is never a requirement |

**Non-goals.** Engine choice, crossings and whole-artifact effects (architecture's rules; engine
pricing stays DEFERRED). The SIMD official verdict. New find methods (V1/M64 stay closed). Run-time
adaptive switching (Boonies). `[rev5]` Changing a default prior: a deliberate data event with its
census (§What moves), evaluated for smp20 only at the last planned step if the default is wrong.

## The shape

Six scenarios make the SAME call (DFA prefilter OFS, cover/REPORT, PF find, VM re-find, MLINE, LMHIT;
a pre-check's window-stating parts ride their site's call). Presence (the PRES slot) keeps its own
entry until [MEMFN-UNBOUNDED-SPANS] states unbounded spans. Inner first:

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

`[rev3 P1]` T-FRAME and T-FIND stay TEXT-time through stage 1: Table E reads hooks and a phase set the
plan call does not take (compose.c :255-258; emit_dfa.c :7600-7602), and T-FIND's answer depends on
its asker (PAIR needs `SF_WINDOW_STOP`, set only by `fd_find`, finder.c :938). A priced row compares
methods, so it needs the frame at plan time: unit 3.0.

**The candidate list is data**, with soundness flags (a RESEED alternative never stops at F0, S188);
PARKED readability is a T-VERIFY output (`rd_set`, window.c :251-254, :877-878). **A scenario** is
stated facts. `[rev3 R4, rev5.1 R17]` Of R-33's 1,742 RTE PF sites (1,767 incl. the 43-pattern DEF
recompile), 1,429 state PARKED + RESEED, 291 one NONE alternative, 22 PARKED only; of the 1,429 RTE
RESEED alternatives 733 have one core position, 696 two or more (740/714 of 1,454 incl. DEF;
`span_pick/counts.out`). **The trace**: every candidate, the rows walked, the incumbent and the
deciding row (MFTRACE build); `[rev5]` from row 1 also the handed rates' digest, each candidate's
price, the qualifiers and bands. ONE plan out.

## The designer/emitter split

This mechanism IS the kit's planning face (roadmap §0a) and stage 1 IS A-PLAN's first step (D186 add.
1 A6), with the roadmap's ratchet accounting (§Staging).

| stage | owns | in this design |
|---|---|---|
| pcrec, the designer | facts and legal choices: spans, candidate positions with their rates, alternatives with entry, floor, frame facts, byte rates and their source, the set | states them once per site; never a CHOSEN position, method or cost `[rev3 O6]` (D157; D167 add. 1 A11's landmark-admission exception stands until restated in code); `[rev5.1]` the source stays pcrec's (stamp, trace): the kit gets rates and digest (1g) |
| the kit's planning face | candidates, the question tables, the pick, (later) the cards | phase 1: facts in, one plan out (alternative, stop, verify plan, test forms) plus its trace |
| pcrec's rules | engine, route, crossings (`next_keys`, FIRST/NEXT rows) | reads the reply as NEXT reads the phase-1 reply today (window_site §2.4) |
| the kit's emitting face | frame, method and renderer rows, then text | phase 2: plan + frame in, C out; golden plan-in/C-out tests per seam |

**What moves across** `[rev3 P1, rev5.1 R1]`. In stage 1 the reply does NOT grow. Its seam events: 1f
(an entry, two denies) and 1g (`mf_akind`'s provenance) are MF_SITE_ABI events; 1a, 1f and 1e (finder rows
added or removed ahead of the PRES rows) MF_CLASS_V events. The reply grows (method, resume, frame row) at unit 3.0.

**A-PLAN's open points.** (1) ONE PLAN WITH ITS TRACE (D186 add. 2; `[rev5 D1]` A-PLAN OPEN POINT 1 already
amended on main, 5e8bcf455/b405ff811); `[rev5.1 R10, rev5.2 C8]` roadmap §0a and §5's kit rows R20-R27 are
DONE on main (27cfc44f7, 2636dee99); no stage-1 unit edits the roadmap. **The plan face is a PURE FUNCTION**
(D186 add. 2) of (site facts, frame: engine/target/layer, measure set, handed rates): same inputs, same
plan, no hidden state. `[rev5 C1]` One plan SUFFICES to compare scenarios once its price is readable
(REVISIT TRIGGER: whole-artifact pricing un-deferred); until then the reply carries no price (trace only).
`[rev5 C2]` **Axes**: site facts per CALL (`mf_wdecide(art, site, out)`); the frame no input through stage 1
(window.c :1061; layer hard-coded, finder.c :934), per call from unit 3.0; set, handed rates, denies and
levers per ART (`mf_art_begin`, compose.c :869-882). **Purity breakers today** `[rev5.1 R5]` (grep of
memfn/src for mutable statics and `art->` uses; no local static, `_Thread_local` or `getenv`):

| breaker | where | unit 1d |
|---|---|---|
| (a) the sticky `art->err` refusal | window.c :1062; compose.c :960 | `[rev5.2 C2]` FENCED in 1d, code unchanged: pcrec fails the compile on any refused define (`kit_check`, memfn_sites.c :674-678) and on any plan-call -1 (emit_dfa.c :1068, :7610), so no reply after a refusal reaches an artifact; purity is stated over arts with no error; a fix is its own later unit change, keeping every error path's outcome and diagnostic |
| (b) the call-order label `art->nsites + 1`, and `fd_route`'s `handle` | window.c :997, :1007, :1734, :1818; finder.c :930, :863; ofsskip.c :486; compose.c :268, :281, :982, :988, :1005 | trace-only (gate.c :936): stays unread by rows |
| (c) the process-global reach counters and `trace_arts` | gate.c :850-856; read by `reach_print` (:884-900), rows_check.py (`asked` = the phase=ask FD records), run_g2.sh :986-1024 (per-row floors), run_g2_gate.sh :144, `memfn/docs/trace_format.md` "Reach" | ALREADY FENCED, KEPT: `mf_wdecide` decides quiet (window.c :1070) and quiet counts no reach (gate.c :943/:956/:978), so reach counts on the define. The risk is serving phase 2 from a stored phase-1 plan (the counted define drops): no cache. Trace records and counters are fenced together or not at all |
| (d) `art->consulted` | no writer today: kit.h :292 declares it, `mf_art_end` reads it (compose.c :1303) | a FUTURE breaker: the plan call takes `const mf_art *`, so a T-PICK row sets it on the define path (non-quiet). pcrec ORs it over every attempt and part (memfn_stamps.c :275-286): "taken" means a define, every attempt's define counts |

`[rev5 C3]` `wused & ~wemitted` (runcmp.c :515) and `simd_inc` (ofsskip.c :565-567) decide emitted
text first-use-wins: the EMITTING face is order-dependent by design, so 1d's purity witness is scoped
to the plan call. (2) Helper sharing stays emit's; (3) run-time dispatch held; (4) cards keyed by
class and regime. (5) `--memfn=no-X` denies become filters on T-FIND and T-PICK rows (D147 add. 9).
(6) The same-commit abi rule is unchanged.

## The tables

Rows say what is VALID; price and dominance are separate. Each table answers as today in stage 1.

| # | question | form and rows (stage 1) | replaces |
|---|---|---|---|
| T-FIND | how to find the next member of S at d, and where to resume | first-match `kit_table`, asked at TEXT time on E-find only `[rev3 P1]`: Horspool FIRST (D-hors's holds kept, deny `window-skip` with it; its admission reads T-VERIFY's tested sets, window.c :1592-1597, and its D-shift resume T-VERIFY's offsets), then `[rev5.1 R9]` TODAY'S ORDER, KEPT: D1, D1c, D1w, PAIR, R7w (finder.c :282-322; resume D-one `c + 1`); ONE walk with the asker fact "the asker renders PAIR" (today `SF_WINDOW_STOP`, kept, renamed) replaces `fd_find`/`fd_route`'s two entries; SIMD forms are rungs of a row; inert R3a/R3b/R4 deleted (1a), R8/R1/R2 at 1f | Q3's `fd_route`/`fd_find`, Table D, T-RESUME |
| T-VERIFY | which other positions to test, in what order and grouping | a DECLARED STEP LIST read in order, every holding row applying: `[rev3 S3]` C-bound (a full-set position is never a test), C-floor or C-yes, C-model or C-none, C-pin, C-stop, C-run (its core/shape clause `run_group_ok`, read by `find_groups`, window.c :1494; `[rev5.1 R8]` `translate`'s `pterm` grouping, window.c :1278-1300, stays a NAMED MEMBER), C-asc; first step the run member (`run_member`, T_MASS_STRETCH), an output of the plan | Q5, Table C and ofsskip's legacy plan (U10) |
| T-SETTEST | how one byte's membership is tested | offered `T[b]`, then `kit_set_test`; C-table/C-own live HERE only | Q11, `member_test` |
| T-CMP | how a literal stretch is compared | runcmp's rows (`rc_row_of`); generic.c's RUN chain is a named exception | Q6 |
| T-PRES | which required members a presence pass tests, in what order | the PRES rows (P0, P2, P3, P4, P9); `[rev3 S3]` `fd_pres`'s chain order (HEAD/RUN/REST, REST ascending byte, a REST member a whole exact run covers un-verified) and precheck's `implied_by` are its kept renderer-side deciders; precheck's three renderers are its rendering (N9); D176 Q4's fold is a T-PRES row, its own choice change | Q9, PRES part ordering |
| T-FRAME | which renderer serves this plan in this frame | Table E (`wf_erows`, legacy first, order kept), at TEXT time `[rev3 P1]`; `[rev3 P2]` plus the renderer row: B-fn vs B-pair (both PAIR on E-find, different C: smp05's `ofsskip__body` vs pr09's inline loop), reading the plan's shape and `fn_rows` BODY; `b_fn_holds`'s reconciliation KEPT | Q8, the phase-2 frame walk |

**Pick-side tables** (`[rev5 A5]` together THE INCUMBENT of every priced comparison, §The pick 2; each
retires only when a census shows no site reads it as a pick OR as an incumbent, its own no-mover):

| table | rows |
|---|---|
| KEY | Table A's five rows: A-empty, A-parked, A-model, A-mass, A-floor (the RESEED default with no `scan_ok` walked span: 1,420 of 1,835 RESEED alternatives incl. DEF, 1,397 of 1,800 RTE); A-empty's reach owed |
| M | MARGIN, M-one, M-parked |
| TIE | `wf_ties`, `[rev3 S1]` readers made explicit: the presence-member row, a SECOND comparator shape (member order, then the larger byte; an UNKNOWN order ranks below every known, as `tie_over` reads `MF_ORDER_UNKNOWN` today); presence's run window reads T_WINDOW (LEFTMOST); translate's run rank reads T_MASS_STRETCH (HIGHER), its `rank_pos[0]` asserted equal to `run_member`'s answer. `[rev5.1 R19]` A tie among priced QUALIFIERS goes per level to a named row: position to the offset rows (T_MASS_SET, T_MASS_STRETCH by span kind), alternative to T_MARGIN (PARKED), method to a NEW row (row 1's design; it amends D176 Q5's "existing rows": a manager line, For main); an incumbent within band stays (T_BAND -> TIE_DEFAULT, MARGIN's family) |
| T-PICK | arrives with the first priced row |

**Named exceptions** `[rev3 P4]`, each a second decider kept on purpose, with its retiring trigger:

| decider | answers | retires when |
|---|---|---|
| generic.c's per-byte RUN chain | T-CMP | U8's unit change |
| `fn_rows` BODY (ofsskip.c :414-416) and the RESEED KEY row's `scan_ok` | T-FIND on OFS sites (no consumer kind: 371 of 371 RTE OFS sites) | pcrec states a kind on OFS sites |
| `fn_rows` PREFIX (own denies `vrun-w32`/`vrun-w16`) and vrun's KA/KB (U7) | SIMD rungs | `[rev5 D4]` the census rule: a census shows no site's rung is decided by them (every SIMD rung a T-FIND rung or a SIMD T-PICK row's, C9) |
| compose's `arms[]` as the frame selector of NON-plan sites (carries the `precheck-assign-byte` deny) | frame + method off the plan call | outside Goal 3's plan-call scope; joins when a kit request adds an arm |
| `fd_pres` chain order, `implied_by` | T-PRES | presence joins the call ([MEMFN-UNBOUNDED-SPANS]) |
| the asker fact (the one T-FIND walk answers per asker: E-find with it, legacy rows without) | T-FIND per frame | unit 3.0 (plan takes the frame) |
| `[rev5.1 R8]` `translate`'s `pterm` grouping (no core, cap or adjacency clause; a pinned join needs no core, window.c :905-929): reading `run_group_ok` is not provably byte-identical | T-VERIFY's C-run, legacy renderer | a census shows its groups equal `find_groups`' on every B-fn site |
| `[rev5.1 R4]` U6, the kit's landmark shadow (`kit_pres_picks`, presence.c :222-245): writes the public `mf_pres_picks.landmark`, read by pcrec's KW-8 record (emit_dfa.c :11256) and run_pres_picks.sh :61 | landmark admission (pcrec's, D167) | pcrec states the landmark as a candidate (D167 add. 1 A11) |
| `[1b fix R9]` P2's dominance compare (presence.c `kit_pres_picks`: `rate && ... rate[proof->byte] <= rate[lead]`): reads the RAW rate table, so under NONE it answers "not dominated" where the declared NONE row (equal counts) would answer `<=`; pcrec's verbatim COMPARE port, kept | P2's dominated pick (today's answers) | presence joins the call, or a priced row on NONE |
| `[rev5.1 R2]` HORS_MIN and MARGIN reading the NONE row's uniform mass as a density: D-hors admits under NONE at 38 or more members (window.c :1596, HORS_MIN 145,822); MARGIN's cost ratio (window.c :669-683) | D-hors admission, M (today's answers; every `-e utf8` compile is NONE) | [SPAN-PICK-UTF8]'s per-encoding prior, or a priced row on NONE |

**The decider census** `[rev3 P4, rev5.1 R3a]` (Goal 3's check, per unit HEAD) is a DECLARED FUNCTION
LIST, a committed map `function[:part] -> table or named exception` (plain loops by hand) written by
1a's lane at its base, kept by each unit's. Members `[rev5.2 C3: by name]`: finder.c `fd_route`,
`fd_find`, `fd_decide`, `fd_pres`'s chain; compose.c `select_arm` (`arms[]`); ofsskip.c `fn_select`,
`ofs_fn_serves` (`fn_rows` BODY, PREFIX); vrun's KA/KB; window.c `decide` (KEY, M walks), `a_empty_holds`
.. `a_none_choose`, `m_one_holds`, `m_margin_holds`, `m_parked_holds`, `run_member`, `tie_takes`,
`find_groups`, `run_group_ok`, `translate` (grouping; run rank :1335), `d_hors_holds`, `wf_find_decide`
(Table D, B rows), `wf_prepare` (Table E), DATA member `wf_ties` + `TIE_` (:77-101) -> TIE; presence.c
`kit_pres_picks`'s set pick (:165), run scan (:182), run window (:192), landmark (:222-245); precheck.c
`implied_by`; runcmp.c `rc_row_of`; generic.c `kit_set_test`, the RUN chain. EXCLUDED: `kit_walk`'s
definition (compose.c :192), prototype (kit.h :951). BACKSTOP: a grep of memfn/src/*.{c,h,def}, red
on a hit in no member: `kit_walk(`, `< best`, `< bm`, `< lo`, `< sm`, `< wl`, `> c)`, `tie_takes`,
`TIE_`, `[rev5 E1]` `< inc`; at 2636dee99 all 36 hit lines map. Two plants, byte-identical copies in
an unlisted function, must go red: `run_member`'s loop and presence.c :182's `c < sm` loop.

**Growth rule.** A new scenario adds no table; a new method adds a T-FIND row and card (D176);
`[rev5.1 R15]` its movers census counts the sites it does NOT win too (§The pick 3). `[rev5 E2]`
**Families, unified at row 1** (trigger: the `enter` cards): "beat the incumbent by a margin" (MARGIN,
the qualifier test, T_BAND -> TIE_DEFAULT, `pcrec_landmark_margin`, HORS_MIN); the pure queries
(`mf_ask`, `mf_wdecide`, `mf_pres_ports`). KEY and the pick read ONE handed rate table.

## The pick

**Stage 1: no prices.** The default is TODAY's plan (KEY, M, TIE, then phase 2's frame and method);
nothing reads a cost but KEY/M's `plan_cost.def` integers, C-model's truncation order kept. **Stage 3:
T-PICK rows, all priced** `[rev3 A2]`: a condition on stated facts, the LEVELS it opens (method,
position, alternative), the priced action, its deny, its per-regime evidence; `keep` last.

**The rates** `[rev5]` (D186 add. 2 as amended; owner: "pcrec would simply send the default as the
analysis"): the kit receives ONE byte-rate table with its digest, or none, as a fact (D157), resolved
by pcrec (§pcrec-side findings), and never tells a bundle from the default (`[rev5.1 R1]` after 1g the
seam carries no source). No rates or no card set: rules only; `[rev5.1 R2]` with no rates the rules
rank sets by MEMBER COUNT (1b's declared NONE row).

**The priced action** `[rev5]` (after stage 2, one row at a time; r = the handed rate table):

| # | rule |
|---|---|
| 1 | CANDIDATES are the complete plans that differ from the incumbent only at the row's levels, each priced under r; nothing else is priced. `[rev5.1 R18]` A blind and a with-data compile of one site see ONE candidate set only where inc_P and inc_B agree outside the row's levels: KEY's A-mass, MARGIN and C-model read the rates (window.c :421, :470, :552, :669-684, :991) |
| 2 | `[rev5 A5]` The INCUMBENT is today's plan (KEY, M, TIE as stage 1 keeps them) under the same handed rates (as A-mass reads them today: smp20 handed `prose` stops at '4', `witness.out`), its NONE answers when none were handed (`findings.md` §4¶1) |
| 3 | c QUALIFIES when `price_r(incumbent) - price_r(c)` exceeds their band. The pick is the CHEAPEST qualifier, else the incumbent. `[rev5 A3]` Only qualifiers tie: those within band of the cheapest go to TIE's rows (D176 Q5, per level), never the incumbent. `[rev5.1 R15]` The anchor is the cheapest qualifier, equal prices ordered by TIE's rows. The property is the WEAK one: a never-QUALIFYING candidate cannot move the pick, but a never-picked qualifier CAN, since within-band does not chain (I 100, q1 80, q2 84, band 5, TIE prefers q2: q2; add c 78 ranked last: q1) |
| 4 | Unpriced incumbent: keep. Unpriced candidate (no card, or a card without noise): cannot qualify; a missing `noise_e6` is UNMEASURED, never 0. `[rev5.1 R20]` On either side, a card with a nonzero coefficient difference and no noise means no departure. No rates handed: keep |
| 5 | A renderer addition that flips a T-FIND first match moves the DEFAULT: its own row and evidence |
| 6 | `[rev4]` SIMD (C9, D186 add. 2): a `-fmemfn-simd` build may pick its own position by its OWN T-PICK row (SIMD-form cards, SIMD-on evidence, scalar the bar); else SIMD forms are rungs (D147). Witness utf8-lead-no-cont `[\xc2-\xdf](?![\x80-\xbf])`, NOT smp20; `[rev5 D4]` its candidate shape and card keys are its own design |
| 7 | `[rev3 R5]` Each row states whether it applies on pre-check parts, where pcrec scans the reply's run member, not its stop (`req_run_member`, emit_dfa.c :1045-1077) |

**With data** `[rev3 WD, rev5]` (pcrec hands a named bundle's rates, B; plan [BENCH-WITHDATA]): the
same action on the one table handed; `[rev5.1 R1]` the band adds the sampling noise pcrec STATES with
the rates, or none. `[rev5 B4]` The target is B's cheapest qualifier, within band to TIE (smp20 with
`prose`: '4' is incumbent and B's least: no departure). **The property** (the owner's bar, scope
CONFIRMED 2026-11-02: "The analysis data must match the test subject to require same-or-better
results."): on every cell whose subject kind B describes, a with-data compile matches or beats the
blind compile beyond noise. **Why the structure gives it** `[rev5, rev5.1 R16]`: where the two
incumbents agree outside the row's levels, the blind pick c_P is a with-data candidate. If it
qualifies under B the pick costs at most price_B(c_P) + band (TIE may take a dearer qualifier within
band of the cheapest); else `price_B(c_P) >= price_B(inc_B) - band` and the pick is inc_B or cheaper.
Either way within band of c_P or better, so "beyond noise" needs the model band no wider than the
measured noise. The MEASURED cell holds when (i) the cards' regime is the cell's (long subjects;
per-call cells need [SPAN-PICK-PERCALL]'s term); (ii) model error stays inside the band; (iii) the
cell's subject is B's kind within B's sampling noise (a held-out sample, never the timed bytes); (iv)
a priced row admits the site; `[rev5.1 R18]` (v) inc_P and inc_B agree outside the row's levels. A
with-data loss is a broken (i)-(v): a mechanism finding ([BENCH-WITHDATA] item 4), never a trade. NOT
covered, each a [BENCH-WITHDATA] census line: sites no priced row admits (KEY reads B, today's) and
`[rev5.1]` admitted sites whose incumbents differ outside the row's levels.

**The price of a plan** `[rev3 C1, C2]`: in the set's unit (the scalar walk's per-byte cost, D176 Q1)
per 1e6 subject bytes; masses in ppm; card values `value_e6` integers. Fixed point (D176 Q5): every
product in int128 at a scale of 1e-12 of the unit, rounded there half away from zero
(`measure_sets.md` §1.7), the price rounded to an integer at its end; a term under the scale
contributes 0, deterministically. Under rate model r:

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

`hit(m)` is per candidate RETURNED, the method's own slope over hit density. Positions are independent
(an ASSUMPTION). `[rev5.1 R21]` verify_r orders positions by mass while T-VERIFY runs the run member
first and a run as one T-CMP stretch: row 1's design prices verify over T-VERIFY's own step list.

**The band of a comparison** `[rev3 C3, rev5]`: for prices a and b under one model, the quadrature sum
over cards of `(coef_a - coef_b) x noise` (a card both read with one coefficient cancels), plus, with
data, B's sampling terms. No constant enters but the card gates (`gate_e6` 3 %, UNMEASURED DEFAULT,
D149). `[rev5 A4]` Stage 2 defines a COVERAGE FACTOR, UNMEASURED DEFAULT (`[s2]` it covers a NEW draw of
each card against its stored value, one launch at a new placement; z 3.0 departs at most 2.25 % of equal-price
one-card comparisons per side, `span_cards.md` §6; the former "1 sigma departs ~16 %" described a different
event, a departure decided on stored values against true ones), and B's sampling noise by block bootstrap per bundle byte (Poisson
`sqrt(n)` is 0 at n = 0, 2-5x low on clustered text). `[rev5.1 R1]` pcrec STATES it with the rates, or
none (no sampling term); the kit keys nothing on provenance. Its seam field: `[s2]` DEFERRED to its
producer (`span_cards.md` §4.6; no producer writes a bundle noise today): one MF_SITE_ABI event with its
pcrec producer when [BENCH-WITHDATA]'s held-out bundles or row 1's with-data band need it. Stage 2's own
event (MF_SITE_ABI 24, unit S2a) carries the CARDS' noise only.

## Cost cards

**What is measured** (one card per quantity, regime named, `measure_sets.md` §7.2 shape). `[rev4]`
SIMD-form cards RETURN to stage 2 (C9, D186 add. 2): each card is measured per layer (scalar, and each
SIMD form a SIMD T-PICK row would price), scalar the bar:

| card | per | regime | replaces |
|---|---|---|---|
| `find.byte` per method (memchr, memchr-back, PAIR, walk) `[rev3 C1]` | subject byte, all the method's streams | miss-only stream, fresh long buffer | C_MEMCHR, C_BITMAP |
| `find.hit` per method (the four, and `hors` `[rev3 C2]`) | candidate returned and restarted | slope over hit density, periodic and random landings; the member split named in its subject (x only vs x/X alternating) | the ASSUMED H_HIT |
| `hors.probe` | Horspool probe (load, table read, shift) | miss-only, the window's shift distribution | — |
| `verify.cmp` per T-SETTEST form, per T-CMP row x length class | one compare | pass rate 0 and 0.5 (`cmp0`, `cmp½`) | C_VERIFY (UNMEASURED), C_MISPRED |
| `enter` per consumer kind x entry fact (PARKED resume, RESEED re-seed, NONE) | candidate passed on | false-start survival measured | C_ENTER (MEASURED x ASSUMED) |

`[rev5.1 R14c]` **Stage 2's list** is main's [MEASURE-SET] row (fa736a260): memchr, two-stream pair,
walk, verify, "Horspool-probe later". `hors.probe` and `find.hit(hors)` move to the Horspool priced
row, so every D-hors incumbent stays UNPRICED and §The pick 4 keeps it. Row 1 also reads `enter`
(NONE); that row lists neither it nor memchr-back: For main. MARGIN (2x, ARGUED) stays M's default
until the PARKED and RESEED `enter` cards exist. `[rev3 C10]` A per-(kind, entry) card may bake in its
fixture's survival; the alternative is a pcrec-stated survival fact x a per-byte card. OFS sites state
no kind (no `enter` key; fine while T-FIND declines on OFS). MAX_SET is no card.

**Noise reaches the kit.** `mf_measure` has no noise field (68 kit rows, `noise_e6` '-'). Stage 2 owes
`[rev3 C4]`: a kit request (main's); a noise field (MF abi event, `measure_sets.md` §4.1, `match_api`
hunks); a producer; derived rows by quadrature; noise in `values_digest` (a digest-version event,
`measures.md` §3.3¶1, §5¶4, readers by grep), or a FILE set may not share a committed id.

**Where they live** `[rev3 C5]`. The span cards are quantities of the grid's successor method
(`[s2]` `kit-grid@3`; `@2` is grid2's, TAKEN), the grid keys re-measured under it. `[rev5 D2]` The set is a FRESH id, `zen4-grid3`
(D186 add. 2; `zen4-grid2` is D167's slot, never reused; `measures.md` §8¶1). Embedded by `make
gen-measures`, handed on `mf_art_begin`; chosen by `--measures=NAME`, else `DEFAULTS` (`measures.md`
§5¶6); measured by quiet-gated `idle-ok` jobs.

## Robustness to the byte rates

`[rev5]` **Robustness is MEASURED, by each row's regimes, not modelled in the pick** (D186 add. 2 as
amended 2026-11-03). The weakest input is P, the default table, `[rev5.1 R17]` digest
`1822fb973b95a4da` (the stamp's, handed to the kit; R-33's local hash `a322116b1b87f9f6` is the same
table): {x,X} 1,097 ppm, '/' 4,154; job 588's subjects held x 2,338 vs '/' 1,026 candidates on real
text, 1,388 vs 0 on none, 21,788 vs 10,856 on random (t588tri §a). **The rule** `[rev5]`: the kit
prices under the one table handed (blind: P; no flat kind, no shipped bundle, no minimax); every
priced row's D186 evidence MUST include a random-like regime (job 588's `random`) beside real text and
none, and a regime it loses beyond noise narrows the row or is an owner exception. **Model error** is
NOT in the band: `[rev3 C3]` row 1 runs with it UNMEASURED, guarded by its predicted-vs-measured print
per mover (R5.3), whose spread the NEXT row adds.

**What the formula says for smp20** `[rev5]` (`span_pick/census0.py control`, `smp20.out` `[s2b]`; bundles and
incumbents from `witness.sh`/`witness.out`; STAND-INS in its docstring: byte(memchr) 0.06 = C_MEMCHR,
byte(PAIR) 2x, hit 20, cmp 2.5, enter 20). Per 1e6 bytes, hit(PAIR) 20 (40 in brackets where it
differs). `[rev5.1 R17]` The last column and every grid count below are BAND-0 ARGMINS (`census0.py` `pick`):
under §The pick 4 the noiseless stand-ins qualify nothing, so every point keeps the incumbent.

| source | @0 {X,x} PAIR | @1 {/} | @4 {3} | @5 {4} | least | today's (incumbent) | band-0 argmin |
|---|---|---|---|---|---|---|---|
| blind: P | 144,694 (166,634) | 153,476 | 228,231 | 228,231 | {X,x} ('/') | {X,x} | {X,x} ('/', 1.086x) |
| with `prose` | 168,871 (212,311) | 72,938 | 66,143 | 63,555 | '4' | '4' | '4' |
| with `log` | 128,384 (135,824) | 385,409 | 760,657 | 854,238 | {X,x} | {X,x} | {X,x} |
| with `weblog` | 286,612 (434,532) | 1,225,432 | 441,512 | 302,235 | {X,x} ('4') | {X,x} | {X,x} ('4', 1.438x) |

`[rev5 B2]` Under P, '/' is least only at hit(PAIR) 40. `[rev5 B1]` **Boundaries, EXACT** (linear in k
= byte(PAIR)/byte(memchr) and in hit(PAIR), solved in rationals; GRID: hit(memchr) h1 5, 10, 20, 40 x
hit(PAIR) 1, 2, 4, 8 x h1; cmp, enter fixed). Blind, default arm, challenger '/': {X,x} kept for k <
k* (h1 5, 10, 20, 40): 1x h1: 1.382, 1.637, 2.146, 3.165; 2x: 1.291, 1.454, 1.781, 2.434; 4x: 1.108,
1.088, 1.049, `[rev5.1 R17]` then under 1 (0.971); 8x: under 1 ('/' at every k >= 1). At k 2, '/' wins
at every hit(PAIR) for h1 <= 10, above 28.0 at h1 20, above 103.7 at h1 40. Job 588's none cell (k
~2.3 at hit 20; directional, Zen 1 stand-ins) lies just above k* 2.146: the cards decide; either
answer is the default's. `[rev5.1 R17]` Over the grid x k 1.00-12.00 by 0.05 (3,536 points) P's argmin
is '/' at 3,381. `[rev5 B3]` DEF arm: '/' is P's cheapest at every grid h1, no move. With data over
that grid: `prose` '4' everywhere; `log` {X,x} 1,502, '/' 2,034; `weblog` '4' 3,438, {X,x} 98.

**Uncovered** (review r1 C5). Where real text is far from P (UTF-8 lead bytes, case-folded pairs,
dense classes), P is wrong (R-33's `utf8/alt-cyr-64`). `[rev5]` Under `-e utf8` blind is NONE today
(`findings.md` §2¶7); the gap is byte-encoded compiles over UTF-8 text: priced rows over two-member
stops are gated on a fix (an encoding fact, or a per-encoding default prior). **Nothing is tuned.**

## The watched witness

`[rev3 A2, WW; rev5]` smp20 `(?i)x/1234` is resolved by data, never by a rule, read TWO ways at every
stage; `[rev5 B3]` from stage 3 each arm (default, `--engine=vm`, both layers, the DEF deny) is judged
by its own new/old. (1) BLIND, "consistent with the default" (D186 add. 2 as amended): the priced
action on P, re-priced pcrec-side; correct by definition, {X,x} or '/'; job 588's blind timings judge
P, and a wrong P is a data question at the last planned step. A blind pick that is NOT P's cheapest
qualifier is a mechanism problem. (2) WITH a text-like bundle: a one-member stop the bundle rates
rarer than {x,X}, '/' or '4' (D186 add. 2): passes TODAY ('4') and must at the last planned step
(stage 3 row 1), else a mechanism finding. **Forecast** `[rev5, rev5.1 R17]`: P keeps {X,x} at the
stand-in point only ('/' is P's argmin at 3,381 of 3,536 grid points); the cards decide; real-text
cells close through (2). The text-like bundle until [BENCH-WITHDATA]'s held-out one: `prose` (GPL-3 +
GFDL-1.3 + Apache-2.0 by `pcrec-analyze`: {x,X} 2,172 ppm, '/' 575, '4' 158; job 588's real text 2,338
vs 1,026), made in scratch by `witness.sh`, never committed. `log`/`weblog` ('/' 14,462 vs {x,X} 372;
51,754 vs 7,396) are with-data rows only. `[rev5 B7, rev5.1 R14a]` Each witness compile names its card
set: `DEFAULTS` until M2, then `--measures=zen4-grid3` (at M2 a bare compile prices nothing; a
named-set compile keeps its priced pick).

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
once); D186 WHAT the fix is: narrow the row, or an owner-approved exception. Unit changes (1a-1g, 3.0,
smp04) stay under D144 alone.

**Stage 1: unify, today's answers kept: A-PLAN's first step.** No-mover units, each with its own
byte-identity witness; one that cannot be byte-identical lands alone as a unit change with its deny.
`[rev3 P3]` A finder row added or removed ahead of the PRES rows is an MF_CLASS_V event (pres_row).
`[rev5.1 R13]` **Landing order 1a, 1f, 1g, 1b, 1c, 1d, 1e; no unit after 1a lands out of it**: all
read 1a's census map and ratchet base; 1c needs 1b (presence's `mf_term` cubes need the
position-multiset primitive); 1e needs 1d (D-hors's admission and D-shift resume read T-VERIFY's step
list); 1f follows 1a so 1e's merged walk never carries R8/R1/R2, their denies and the pay rule; 1g is
independent, beside 1f's seam event; main's R10 step is done (`[rev5.2 C8]`).

| unit | content | deletes |
|---|---|---|
| 1a dead code `[rev3 P3]` | N3 `mf_set_terms` (internal: no seam event); inert rows R3a/R3b/R4 (no deny; zero reach by code); MF_CLASS_V (pres_row shift); writes the census map and takes the ratchet base | 4 members `[rev5.2 C7]`: R26 -3, R27 -1 |
| 1f retired denies `[rev3 P3]` | R8/R1/R2 with `fd-r8`/`fd-ndisp`, the §2.5 pay rule (`fd_pay`, `pay_fill`, `n_interval`) and the public `mf_finder_pay`; CALLER-VISIBLE, not a no-mover: `registry.md` §6¶8a/§6¶8b hunks (floor 14 -> 12), `--list-axes` re-pin; an MF_SITE_ABI and `[rev5.1 R3]` an MF_CLASS_V event (R8/R1/R2 precede the PRES rows, finder.c :249ff) | 3 rows, 2 denies, the pay rule, 1 entry `[rev5.2 C7]` (no R20-R27 row counts them: the registry hunks and `--list-axes` do) |
| 1g provenance leaves the seam `[rev5.1 R1]` | D186 add. 2 (main 7f55a62f9): `mf_akind` becomes {tag, version, present, digest, payload}. The DIGEST STAYS, as `mf_akind.digest`: the kit's trace names it from row 1. `source` and the bundle label leave as ruled; `bytes` and `fidelity` leave too: they let the kit tell a measured bundle from the default (bytes 0 for the default, findings.c :579), and the band's sampling term is noise pcrec states. `mf_prov`, `mf_prov_source`, `mf_prov_fidelity` and pcrec's stanza mapping go; an MF_SITE_ABI event, byte-identical (no kit `.c` reads them; MF_SITE_ABI reaches no text, memfn_sites.c :413); no docs/spec names them | 1 struct, 2 enums, 1 mapping (no R20-R27 row) |
| 1b primitives `[rev3 S1, S2]` | U4 one mass primitive over a POSITION MULTISET (a list of cubes, a repeated byte counted per position, as `window_mass`: a set-shaped primitive moves `run_window`, e.g. `zzzzzzz~J`), a capped/uncapped argument, the NONE-mode total (62,500, not 62,496); the landmark admission's per-factor round-up product stays its caller's; `[rev5.1 R2]` the DECLARED NONE ROW: no rates handed, a set's mass is its member count's uniform ppm, floor(k x 1e6 / 256) (`uniform_mass`, presence.c :58-62), the rules' own tie-break by member count (D186 add. 2), its density readers the named exception; U5 `wf_ties` with the presence-member row and presence's run window reading T_WINDOW | 2-3 mass variants, `[rev5.2 C7]` 1 tie spelling (`tie_over`; `wf_ties` stays): R22 -2 or -3, R23 -1 |
| 1c kit-only spellings `[rev3 S1]` | U2: P3's `run_scan` asks `run_member`; translate's run rank reads T_MASS_STRETCH, `rank_pos[0]` asserted against `run_member`; `[rev5.1 R4]` U6 is NOT here (a named member; its ratchet row kept) | `[rev5.2 C7]` 1: R24 -1 (`run_scan`'s spelling); -2 only if translate's rank is derived from `run_member` and its `rank_pos[j] = (uint16_t)i` loop goes; R25 unchanged |
| 1d planning core `[rev5 C5]` | one candidate builder; KEY/M/TIE as the default; T-VERIFY as a step list with C-bound and the run member (`translate`'s grouping a named member, R8); trace without prices (U1 as two KEY rows, U10 = Table C + ofsskip's legacy plan, N1, N6); PURITY per the breaker table `[rev5.1 R5]` | `a_model_choose`'s private enumeration, `mass_domain`'s copy `[rev5.2 C7]`: R21 -1 (`mass_domain`'s copy: no row, the census map's) |
| 1e phase-2 tables `[rev3 P1, P2]` | T-FRAME (legacy first) at text time; T-FIND as ONE walk with the asker fact, Horspool first, then today's order (R9); the renderer row (B-fn/B-pair, reconciliation kept); compose `arms[]` and `fd_find`'s text become renderers keyed by (frame row, method row, renderer row) (U3 less OFS, N5, N11); no MF_SITE_ABI event; MF_CLASS_V if the Horspool row's move shifts pres_row | `fd_find`/`fd_route`'s second entry walk `[rev5.2 C7]`: R20 -1 (3 -> 2: `select_arm` and BODY stay, named exceptions) |

**Each unit's readers and extra witness** `[rev5.1 R1, R3, R6, R7, R11]` (readers by grep at main
2636dee99; "RETIRED" = deleted with its registration):

| unit | readers it edits | its witness, beyond the per-unit one |
|---|---|---|
| 1a | finder_check.py :109 `FIND_ROWS`; rows.tsv :120-122; row_floors.tsv :104-106 (the `kit.h3a`/`kit.gstar.*` keys stay in zen4-grid1, unread) | the census map's base, red on both plants; `[rev5.2 C6]` reach equality on every SURVIVING row, the declared difference the three gone `table=fd` lines R3a, R3b, R4 |
| 1f | grep `fd-r8\|fd-ndisp\|mf_finder_pay\|fd_pay\|pay_fill\|n_interval`: finder.c (rows :249ff, the pay rule); options.def :58-66; memfn.h :1550-1557 and its MF_SITE_ABI history; arm_fixtures.c :1685 (`--pay-grid`: a build break); finder_check.py :109, :119 `B1_DENIES`, :493, :641 (section H); rows.tsv :119, :123-124; row_floors.tsv :103, :107-108; rows_check.py :495; tests/axes/memfn_arm.py :122-125; emit_sweep.py :553-560, :605-609, :2996-2997 (`IDENT_MEMFN`); S1025_sn9-pay-tie-pays.sh RETIRED (run_sabotage_matrix.sh :497); `registry.md` §6¶8a/§6¶8b (axes_registry_check.sh reads the floor there) | `--list-axes` moves exactly by the two rows (emit_sweep stream 5); `[rev5.2 C6]` reach equality on every SURVIVING row, the declared difference the three gone `table=fd` lines R8, R1, R2 (whether their `asked` is non-zero today, as heads of the FIND walk, is SUSPECTED, not run: their lines go whatever their counts) |
| 1g | grep `MF_PROV_\|MF_FID_\|mf_prov\|\.prov\.\|->prov\b\|prov_stanza`: memfn.h :1205-1238 (its stale "NO kit row reads it before B3a" too), its MF_SITE_ABI history (`[rev5.2 C4]` :105-108's 15 entry names `mf_prov`: history, kept; the new entry records the removal), memfn/include/CLAUDE.md; `[rev5.2 C4]` memfn/CLAUDE.md :38 and tests/memfn/CLAUDE.md :82 (name `prov_check.c`: its role restated); memfn_sites.c :186-191 (`akind_source_map`), :273-280 (writes; the out-of-vocabulary fidelity refusal goes with the mapping, the schema's `closed fidelity` row already holds it), :582-613 (`prov_fidelity_rows`, `pcrec_memfn_prov_stanza`), :233-249 (the `KSRCTRACE object` record reads bytes/fidelity from the BUILT object: it reads pcrec's offer instead, columns unchanged, and tests/findings/e1_object_check.py's header re-states its premise: the offer, not the object); memfn_sites.h :170-176; tests/memfn/prov_check.c (offsetof :27-31: a build break; reduced to `mf_akind.digest`'s offset) and its build, run_finder.sh :37-41 (kept: a build-only static assertion); `[rev5.2 C4]` the `--provchk` plumbing GOES with parts (1)-(3): run_finder.sh :67's argument, finder_check.py `prov_run` :675-679, :748 (required argument), :758 (`check_prov(..., a.provchk)`); finder_check.py section L (:654-740: parts (1)-(3) test the stanza and retire; part (4)'s `KIT_READERS_RE` :658 re-aimed at "memfn.h states no source, bundle, bytes or fidelity", its render loop varying the digest, `[rev5.2 C8]` its plant a kit row reading `mf_akind.digest` (holds iff the digest is odd), red; docstring :65); S1092_prov-stanza-drops-fidelity.sh RETIRED (run_sabotage_matrix.sh :503); arm_fixtures.c :1267, :1569-1590 (`fd_an_make`); memfn/tests/g2/g2_win_gen.c :625-627, :830-832 (build breaks; `[rev5.2 C4]` :832's `prov.digest` moves to `mf_akind.digest`, as :627's); `window_contract.md` §3.1/§3.2 (a revision line). NOT readers: the `KSRCTRACE` line counters (emit_sweep.py :2777, run_part_analysis.sh, data_trace_check.py, S1332); docs/dev/lanes/r33_sim/probe.c (lane evidence) | the `KSRCTRACE object` records unchanged byte for byte; finder_check L green |
| 1b | — | a golden-value test of the one primitive: NONE at k = 1, 3, 6, 16, 256; a repeated byte per position; capped vs uncapped |
| 1d | compose.c :882's stale comment ("no row reads it before B3a") | REACH EQUALITY; the PURITY HARNESS, built by 1d's lane in arm_fixtures `[rev5.2 C1]`: N window sites; each site's `mf_wreply` on a fresh art is compared field by field with its reply after k `mf_define`s of the other sites (k = 0..N-1, in order, reversed and repeated), the plan calls INTERLEAVED with the defines. WHY: `art->nsites`' one writer is `mf_define` (compose.c :1072) and the plan face takes `const mf_art *` (window.c :1058), so plan calls alone see one `nsites` in every order and a row keyed on it stays green (K35); order reaches the plan face only through defines, the real phase-1/phase-2 interleave. Its plant: a KEY or M row that changes an answer with `nsites` (holds iff `nsites > 0`), red; its CONTROL: the plant moves a reply on the unharnessed fixture (plant build vs base build, a site asked after one define), so the plant is reached. `[rev5.2 C2]` The sticky-`err` case: after a refused define every plan call returns -1, asserted as breaker (a) FENCED, not a purity failure; equal replies are asserted only if a later unit fixes (a). A D27 author optional |
| 1e | a DECLARED `wfD` -> `fd` row map: rows.tsv, row_floors.tsv, rows_check.py's derived row set, the MFTRACE table names | REACH EQUALITY through that map |

**Witness, per unit**: `scripts/emit_sweep.py` byte-identical on EVERY arm (default, each
`--memfn=no-X` deny, `--engine=vm`, both SIMD layers), stamps included, over the corpus plus `[rev5.1
R6]` three `--patterns-file` inputs (a pattern per line in `--list-source` escapes, `#` lines skipped,
emit_sweep.py :1553): `[rev5.2 C5]` job 588's sample, column 3 of
`docs/dev/lanes/s3_evidence/sample_588.tsv` (`pick_588.py` writes it in those escapes) less its `#`
lines, in a scratch file, 24 patterns counted in and out; the bench pattern list (main names it); `zzzzzzz~J`. `*_movers.txt`
unchanged; G2; the census; REACH EQUALITY, not floors (0.9 x measured): chosen and asked per row
(`MFTRACE REACH`) equal at base and HEAD on every SURVIVING row, a unit's deleted rows' lines its
declared difference (1a, 1f; 1e's row map). **Ratchet** `[rev5.2 C7]`: roadmap §5's R20-R27
(2636dee99; 15 at 27cfc44f7), each unit's delta in its "deletes" cell; stage 1 ends at 3 or 4 (R20 2,
R25 1, R22 0-1; R24 reads 0 since 1c derived translate's rank from the run member, `[rev5.2 C7]`'s -2 case),
restated against roadmap §5's current recipes. A counted name a unit keeps as a thin caller still counts: main re-states that
recipe before the unit lands, or the lane drops the name. **Sequencing** (D153): opt rows on window.c,
finder.c, ofsskip.c, compose.c or presence.c wait ("remodel overlap"); O3 = WAIT: smp04, look-ahead.

**Stage 2: measure the cards** `[rev3 O1, A2]`, directly after stage 1 (D186 add. 1 A2): §Cost cards
(scalar and SIMD forms; Horspool's later), the noise channel (coverage factor, the noise pcrec
states), the id `zen4-grid3`, the step-0 gate; `[rev5 D5]` [PAIR-LOOKAHEAD-TIME]'s width sweep (its
trigger fires here). No reader, zero movers, stamps and `DEFAULTS` unchanged.

**Stage 3: priced choice rows, one per change.**

| step | what it carries |
|---|---|
| Unit 3.0, the plan takes the frame `[rev3 P1]` | pcrec states form, handoff and site_kind per NEXT row's frame at phase 1; the call takes hooks and phase set; the reply grows method, resume, frame row; the asker fact retires. Byte-identical; one MF_SITE_ABI (+ MF_CLASS_V) |
| Each row | one T-PICK row naming its levels; a deny with a D174 name (`registry.md` §6¶8a, `cli.md` §2.4¶1); `[rev3 R1]` a 588-style run, RTE vs the row denied, on EVERY arm (scalar the bar), `[rev5]` a random-like regime among them; its movers census per arm from artifact diffs (`[rev5.1 R15]` sites it does not win included); `[rev3 C7]` `consulted`, set on the define path (breaker (d)); `[rev3 C8]` its drop-F witness or the plant UNREACHED; `[rev3 R5]` its pre-check-part statement; its pcrec abi event and spec hunk |
| Row 1 `[rev3 A2]` | the first priced departure, admitting smp20's class on `[rev5.1 R18]` STATED facts: a NONE alternative whose core position 0 is a two-member set (not "whose default is", which reads the rate-dependent incumbent); job 588 its evidence, §The watched witness its reading. `[rev3 O2]` Acceptance also against the rule-list pilot (0.981 of ideal, [PRICE-BAKEOFF]), re-run after each priced row. `[rev3 C6]` It flips `DEFAULTS` to the new set. `[rev5 A5]` R7 RESTATED: A-model's one-member preference (`scan_ok`) and A-mass meet in T-PICK, not in KEY; KEY's rows stay the incumbent. `[rev5.1]` Its design items: the method-level tie row (R19); verify priced over T-VERIFY's step list (R21); finder_check L(4) holding the rates fixed and varying only the digest (R22: today it compares no analysis against `fd_an_make`'s, so a priced fd row would read red). `[sp1g review F5]` finder_check L's digest loop (now `check_seam`) compares the traced kit's stderr across digests, so once row 1's trace names the digest it must MASK that token (or compare decision lines only), else the sanctioned line reads red |
| `[rev3 O7]` Ratchet delta; `[rev3 R9, rev4]` batch gate | T-PICK with its `keep` row falling to KEY is one table (delta 0 at row 1); each later row names the member it deletes or is rejected at review (roadmap §0). Choice-row losses as above; SIMD rows (C9): §The pick 6 |
| Later rows (none scheduled) | Horspool priced (D176 Q2; deletes HORS_MIN; `hors.probe`, `hit(walk)`, `hit(hors)`; hex8-bounded and the five other D-hors sites). RESEED at any set size (PF E-stmt: [MEMFN-PAIRSTOP] or walk-only, both `enter` cards). Dense pairs (after [MEMFN-PAIRSTOP] and the C5 fix). smp04 `[a[:b]`: a UNIT change. `[rev5 D5]` [COVER-PRICE-WITNESS] (x1.95 on the SCALAR layer too): its SIMD half the C9 row's, its scalar half a scalar priced row |

## What stage 1 deletes

| id | stage 1 does | unit | later |
|---|---|---|---|
| U1, N1 | one candidate builder; A-model and A-mass stay two KEY rows; C-model same arithmetic | 1d | meet in T-PICK at row 1; KEY retires by census `[rev5 A5]` |
| U2, U5 | `run_scan` asks `run_member`; translate's rank and the run window read `wf_ties`; presence-member row `[rev3 S1]` | 1b, 1c | pcrec's two and its PICK: findings |
| U3, N4, N5 | one T-FIND walk with the asker fact (N4 kept, renamed `[rev3 P1]`); arms/`fd_find` text become renderers; not on OFS | 1e | the asker fact retires at 3.0; OFS joins with a kind |
| U4; U6 | one primitive over a position multiset, NONE-mode total kept `[rev3 S2]`, the NONE row declared; `[rev5.1 R4]` U6 KEPT, a named member | 1b; — | pcrec's findings.c copy stays (D157); U6 when pcrec states the landmark (D167 add. 1 A11) |
| U10, N6 | T-VERIFY = Table C + ofsskip's legacy plan (PRES ordering is T-PRES's `[rev3 S3]`); translate's grouping kept `[rev5.1 R8]` | 1d | priced rows; the grouping census |
| N11 | Table E becomes T-FRAME at text time, order kept, plus the renderer row `[rev3 P1, P2]` | 1e | plan-time at 3.0 |
| N3, N14, R3a/R3b/R4; R8/R1/R2 + denies | deleted (zero reach); retired with registry hunks `[rev3 P3]` | 1a; 1f | — |
| `mf_prov` `[rev5.1 R1]` | source, bundle, bytes, fidelity leave the seam; the digest stays | 1g | stage 2's stated sampling noise |
| kept | U7/N10/N12 (SIMD; SIMD-form cards in stage 2), U8 (unit change), U9 (boundary), N2 (MARGIN), N7/N8/N13, N9 | — | a SIMD T-PICK row (C9); U8; a reader grep; `enter` cards; priced rows |

## pcrec-side findings (for main; not changed here)

- **Run pin and scan index**: `pcrec_find_run_scan_index` (findings.c :745), `_window_start` (:780),
  `pcrec_run_pin` (kset.c :294) restate the run member (held by `req_run_member`, emit_dfa.c :1058).
- **Landmark admission** `[rev3 O6]`: `req_landmark_admits` (emit_dfa.c :9064) and lmwalk's
  `lc_rarity` share `pcrec_landmark_margin` (+ `LMWALK_K_HIT_UNMEASURED`): a D157 EXCEPTION (D167
  add. 1 A11) until pcrec states the landmark as a candidate and reads `find.hit`.
- `[rev5.1 R2]` **NONE arithmetic**: `pcrec_find_set_mass(NULL, ...)` (findings.c :661, read at
  :606/:814; D126 Q4) is the kit NONE row's arithmetic in pcrec's own copy (D157).
- **The rate source, pcrec's resolution** `[rev5]` (D186 add. 2 as amended; first match, one per
  compile; the kit's trace names only the digest):

| # | when | pcrec hands | pcrec's stamp |
|---|---|---|---|
| 0 `[rev5.1 R12]` | an `--analysis` chain answers `byte-rate` for this encoding but cannot derive it (T-KIND `underivable-arrives`, findings.c :538): the compile is REFUSED iff the kind is consulted (`window_contract.md` §3.3 rule 9; `-e utf8 --analysis l1none` refuses) | unconsulted: none (PRESENT, no payload; `[rev5.2 C8]` PRIOR_NONE is pcrec's offer state, the seam carries no source after 1g) | none |
| 1 | an `--analysis` chain answers `byte-rate` for this compile's encoding (`findings.md` §1, §7) | that bundle's rates, B | `B:digest` |
| 2 | else the built-in `default` serves this encoding (`findings.md` §2¶7: today `-e byte` only) | the default's rates, P | `default:digest` |
| 3 | else | none (rules only, as M2's unknown target) | none |

  Today's code already (`pcrec_find_byte_rate`, `[rev5.1 R11]` src/core/findings.h :303;
  `findings.md` §6¶3, §7¶6; `witness.out`). Kit grep (memfn/src + memfn.h): no built-in or fallback
  table; `kit_byte_rate` returns the handed table or NULL (presence.c :48-56); NULL takes the NONE
  row (presence.c :58-113). `[rev5.1 R1]` The source fields (`mf_prov_source`, memfn.h :1213-1214;
  `source`, `bundle` "default", :1224-1225) are read by no kit `.c` and leave at 1g.
- `[rev5.1 R12]` **Consults** (SUSPECTED; PLAN, trigger: the first priced row reading rates): rule 9
  and `_FINDINGS` see pcrec's own asks only, so correctness rests on pcrec's MIRROR asks (emit_dfa.c,
  "for exactly the population prefix_k's selection asked it"; facts.c :327); known.c's cover site has
  none; memfn_stamps.c :385 "no routed kit row consults a kind yet" is stale (window.c :991). Unlock:
  `mf_art_end` reports a per-kind consult mask, which retires the mirrors.
- Prerequisites pcrec-side: `[rev3 P1]` unit 3.0's per-frame ask; a consumer kind on OFS sites;
  [MEMFN-UNBOUNDED-SPANS]; [MEMFN-PAIRSTOP]. `next_keys` and lmwalk's route stay architecture's.

## The measurement regime

RELEVANT. Each card names its regime (§Cost cards; landing flips walk vs stream choices, walk_vs_v1
§3). Per set: box, compiler, Linux verdicts, `taskset`-pinned, scalar the bar. Prices are
long-subject; row evidence regimes are job 588's (throughput, search_short, match x real, none,
random, dense); `[rev5]` a random-like regime is REQUIRED in every row's evidence. `[rev3 C11]`
Non-card numbers the pick reads: KEY/M's `plan_cost.def` integers (Zen 1, a box mismatch until they
retire); C_ENTER (MEASURED x ASSUMED); MARGIN (2x, ARGUED); HORS_MIN (PROVISIONAL); `gate_e6` and
`[rev5]` the coverage factor (UNMEASURED DEFAULTs); the ONE handed rate table.

## The independent control

RELEVANT.

| subject | checked against |
|---|---|
| answers | G2 against the scalar byte loop; the `.rxt` oracle under every committed set plus synthetic extreme sets forcing each T-FIND row (`measure_sets.md` §8) |
| stage 1 and 3.0 | the §Staging witness counted pcrec-side from artifact diffs, never the kit's `moved` (K35); the census (a function list, its backstop grep, two plants); reach EQUALITY; the purity harness and its plant |
| priced rows | predicted price vs measured time per mover (R5.3; validation sites share no number with the cards, R5.2). `[rev3 C7]` A pcrec-side python re-price from the stamped rows (no kit code) `[rev5]` recomputes source (from the stamp), prices, incumbent, qualifiers and pick, diffed against the artifact's; its tests by a spec-first (D27) author from §The pick (review r1). finder_check.py checks D and F's true arms at row 1. A swapped-cards plant moves a reach witness |
| with data | [BENCH-WITHDATA]'s compile-only census (blind vs each bundle, movers listed, the differing-incumbent sites their own line) and its held-out bundles (no training on the timed bytes) |
| the watched witness | job 588's timings judge smp20's pick per regime, never the kit's own price |

## What moves when the data is regenerated

RELEVANT. Only picks and the `<PREFIX>_MEASURES` / `_FINDINGS` stamps move. The measures stamp (""
today) becomes `id@rev:digest` where a pick consults the set and changes on every card rev (stamp-only
movers: their own class). A byte move is an abi event (D76/D94, readers by grep) with its per-arm
census; `measures.md` §8/§5 hunks. `[rev5]` **Rate sources.** A shipped, added or recounted bundle
moves NO blind compile (`findings.md` §6¶3), only compiles naming it. A DEFAULT-prior change (the
`default` bundle, per encoding) moves blind compiles: a deliberate data event with its census,
`[rev5.1 R14b]` its log filed with the first such change (D186 add. 2; `DEFAULTS.log` logs set
defaults only). `[rev3 C6]` **Defaults.** `DEFAULTS` (`idk zen4-grid1@1`) holds no span card, so bare
compiles keep the incumbent until row 1 flips it, with its census (`measures.md` §5¶6, §8¶3).
`[rev5.1 R14a]` **M2** (RULED, [MEASURE-SET], fa736a260): not ordered against row 1; at M2 the idk
default has no per-byte cost rows, so priced rows go DARK on bare compiles (rules; stamps move; M2's
census owns them), INTENDED; named-set compiles keep their priced picks. Stage 1 moves no emitted byte
(1f: `--list-axes`, two options; 1g: none); stage 2 and 3.0 move nothing; row 1 its movers.

## Disposition of review 2026-11-03 r2

`[rev5.1]` Every id as the kit manager ruled (all PROPOSED accepted); `[rev5.2]` C1-C8 (`CHECK_rev51.md`).

| id | disposition | where |
|---|---|---|
| R1 (STAGE1-1, FIX-1, FIX-2, SIM-4) | FIXED: unit 1g, readers by grep (incl. S1092, run_finder.sh, g2_win_gen.c, memfn_sites.h, unlisted in the review); digest stays, source/bundle/bytes/fidelity leave; the band keyed on stated noise; "main's call" struck | §Staging; §The pick; §pcrec-side |
| R2 (STAGE1-11, FIX-3) | FIXED: 1b's declared NONE row; HORS_MIN/MARGIN a named exception with its trigger; pcrec's NONE pointer | §Staging; §The tables; §pcrec-side |
| R3, R3a (STAGE1-3, -2) | FIXED: 1f's readers (plus memfn_arm.py, `B1_DENIES`) and MF_CLASS_V; the census a function list, a widened backstop, a second plant | §Staging; §The tables |
| R4, R8 (STAGE1-4, -8) | FIXED, KEEP: U6 and translate's grouping named members | §The tables; 1c; 1d |
| R5 (STAGE1-5, FIX-4) | FIXED: (b) widened; (c) a KEEP with its mechanism; (d) a future breaker on the define path | breaker table |
| R6, R7 (STAGE1-6, FIX-5, STAGE1-7) | FIXED: reach equality; the missed reach readers; 1b's golden test; three `--patterns-file` inputs; 1d's purity harness and plant | §Staging; breaker (c) |
| R9 (STAGE1-9) | FIXED: today's T-FIND order | §The tables |
| R10 (STAGE1-10) | PLAN: main's pre-build step | For main |
| R11 (STAGE1-12, FIX-11) | FIXED: cites, 1a's test edits, 1e's row map, compose.c :882 | §Staging; §pcrec-side |
| R12 (FIX-6) | FIXED: row 0 (refuse); the consult part PLAN; a D186 line for main | §pcrec-side |
| R13 (STAGE1-13) | FIXED: landing order 1a, 1f, 1g, 1b-1e, with its dependencies | §Staging |
| R14 (FIX-9) | FIXED (a)-(c) against main fa736a260; (d), (e) DOC for main; r1's A1 "reduced to" | §What moves; §Cost cards; §Owner rulings |
| R15-R20 (SIM-1/2/3/5/6/8/9, FIX-7/8) | FIXED: weak property, defined anchor, Growth census; the c_P bound; one candidate set scoped, cause (v), row 1 on stated facts; tie rows per level; the either-side noiseless rule; band-0 labels, the stamp digest, the RTE split, 0.971, 3,381 of 3,536 | §The pick; §The tables; §Robustness; §The shape |
| R21, R22 (SIM-7, FIX-10) | PLAN: row 1's design items, one sentence each now | §Staging row 1 |
| families (FIX) | NOTED: handed-fact resolution -> a PLAN row (trigger: first priced row reading rates; unlock: the consult mask); hysteresis: E2 at row 1 | For main |
| C1 (diff check) | FIXED: the purity harness interleaves `mf_define`s between plan calls (fresh art vs after k defines; in order, reversed, repeated), with WHY (one `nsites` writer; `const mf_art *`); plant holds iff `nsites > 0`, with a reach control | 1d's witness |
| C2 (diff check) | FIXED: breaker (a) FENCED in 1d, code unchanged (pcrec fails the compile on any refusal); sticky-`err` case expects -1 on every later plan call, recorded as breaker (a) | breaker table; 1d's witness |
| C3 (diff check) | FIXED: census list by name: `fd_decide`, `decide`, `select_arm`, `fn_select`, `ofs_fn_serves`, `wf_prepare` (Table E's walk, split from `wf_find_decide`'s Table D), `wf_ties` a DATA member; `kit_walk` def/prototype excluded; backstop re-run at 2636dee99, all 36 hit lines map | §The tables, the census |
| C4 (diff check) | FIXED: 1g adds g2_win_gen.c :832, the `--provchk` plumbing (goes: run_finder.sh :67, finder_check.py :675-679, :748, :758), memfn/CLAUDE.md :38, tests/memfn/CLAUDE.md :82, memfn.h :105-108 (history, kept) | 1g's readers |
| C5 (diff check) | FIXED: the 588 input is column 3 of sample_588.tsv (`pick_588.py`'s, in emit_sweep's escapes), `#` lines dropped, 24 patterns counted; the patterns-file format stated | §Staging, Witness |
| C6 (diff check) | FIXED: reach equality on surviving rows; 1a's declared difference R3a/R3b/R4, 1f's R8/R1/R2 | 1a, 1f witness; Witness |
| C7 (diff check) | FIXED: "deletes" restated as R20-R27 deltas (1a R26 -3, R27 -1; 1b R22 -2/-3, R23 -1; 1c R24 -1, -2 only with translate's rank derived; 1d R21 -1; 1e R20 -1; 1f/1g none): 15 -> 4 or 5; thin-caller names re-stated by main first | §Staging table; Ratchet |
| C8 (diff check) | FIXED: row 0 "(PRESENT, no payload)"; L(4)'s plant (a kit row reading `digest`); R10 and four rows DONE, the bench pattern list still owed | §pcrec-side; 1g; For main |

## Owner rulings since rev 4

Rev 5's rows stand, durable in D186 add. 2 (main 5d42c5618): blind uses the DEFAULT by pcrec's first-match
table, the kit sees rates and digest only; no bundle moves a blind pick; robustness is measured per row, a
random-like regime required; a default-prior change is a data event; the [BENCH-WITHDATA] blind testee is
P-only; smp20 blind "consistent with the default", with data '/' or '4'. `[rev5.1]` Since rev 5: provenance
leaves the seam in stage 1, no-rates ranks by member count (7f55a62f9: 1g, 1b); M2 unordered against row 1,
bare compiles dark at M2 (fa736a260: §What moves). **Earlier dispositions** `[rev5 D3]` stand as rev 5 wrote
them, except review r1's A1, `[rev5.1 R14e]` now REDUCED: within one rate source the pairwise form IS §The
pick 3's qualifier test. **For main** `[rev5.1]`: `[rev5.2 C8]` DONE on main: R10, [SPAN-PICK-UTF8],
[SPAN-PICK-PERCALL], [PICK-IDIOM], the [IFACE-PUSH] option. OWED before 1a's witness runs: the bench pattern
list. Owed otherwise: a manager line amending D176 Q5's "existing rows" for the method tie (R19); D186 add.
2's source list gains the refuse row (R12), its "smp20 blind keeps {x,X}" is a forecast the cards may fail
(R14d), its pairwise-minimax line is reduced to the qualifier test (R14e); [MEASURE-SET]'s `next:` lacks
`enter` and memchr-back (R14c); a PLAN row for the handed-fact family and its consult mask (R12).

## Open questions

`[rev5.1, rev5.2]` None for the owner or the kit manager (R1, R4 and R8 are decided by the rulings).

## STATE AT HANDOFF

OWED none. Lane spanpick52: rev 5.2 (C1-C8 of `CHECK_rev51.md`), merged with main 2636dee99, new cites
re-checked there by grep (the backstop, 1g's grep plus `provchk`, sample_588.tsv against
`read_patterns_file`, R20-R27's recipes); the CLAUDE.md rev line. No make, no timing. Not a build go.
