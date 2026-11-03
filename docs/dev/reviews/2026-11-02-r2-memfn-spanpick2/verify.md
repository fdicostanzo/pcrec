# VERIFY — critic round crit-memfn-spanpick2 (span_pick.md rev 2, frozen 5b3bc376a)

Verifier (opus). Review tree: worktrees/crit-memfn-spanpick2 (main 959c08124); all file:line cites are
that tree. Own outputs: verify/vA (V1-V9), verify/vB (V10-V15), verify/vC (V16-V22). Compiles used in
total: 4 (vA) + 2 (vB) + 4 (vC) = 10, all `timeout 60`, trace build unless said. No make, no timing.
"Stage-1 block" = would stop a stage-1 build go as specified (byte identity of a unit, or a check that
cannot pass); "later" = bears only on stage 2/3 or doc accuracy.

## V1

FIX-2 (+SLOT-8): T-FIND's answer depends on the asker.
- Code, re-read: `SF_WINDOW_STOP` is set ONLY at finder.c:938 (`q.facts |= SF_WINDOW_STOP;` inside
  `fd_find`) and read ONLY by PAIR's row (finder.c:306, facts `SF_SPAN0 | SF_TWO_MEMBER | SF_WINDOW_STOP`);
  `fd_route` (finder.c:863-903) builds its facts with `find_facts` -> `set_facts` (:806 sets
  `SF_TWO_MEMBER` for a two-member term 0) and never sets the window bit; its switch maps FF_PAIR to no arm
  (:894 `case ... FF_PAIR: break;`). `e_legacy_holds` (window.c:1386-1393) -> `kit_legacy_serves` ->
  `select_arm` -> `fd_route` (compose.c:281); a routed row with no arm returns NULL ("a pick its arm does
  not serve is REFUSED", compose.c:270-273, :282-288). E-find's holds is `e->fx->holds` (window.c:1403-1407).
- Witness re-run (trace build, vA/w1.trace, vA/w1.c): `[a-z]+[%&][a-z]+` site 2 (stop {%,&}:
  `rx_landmark_bytes` has 1 at 0x25 and 0x26, w1.c:216): `wfE ... chosen=E-stmt`, then the fd walk
  `row=PAIR verdict=PRED_FALSE`, `row=R7w verdict=CHOSEN`, `arms chosen=pf_walk`, `WPATH path=mass
  arm=pf_walk fd=R7w`. Contrast (vA/s20.trace): `(?i)x/1234` (REPORT, legacy rows excluded) `wfE
  chosen=E-find`, `row=PAIR verdict=CHOSEN`, `FDROUTE ... row=PAIR arm=E-find`.
- Consequence check: with the bit deleted, PAIR's facts would hold on the translated STMT site's
  two-member term 0 and PAIR sits above R7w (finder.c:300-306 "above R7w, which it narrows"), so fd_route
  returns row PAIR with no arm, select_arm returns NULL, E-stmt declines and the site falls to E-find or
  below: bytes move. By code; not compiled (deleting the bit needs a build).
- Verdict: **HOLDS.** SLOT-8 (SUSPECTED ordering) is subsumed: FIX-2's witness is the byte-level form of
  it. **Stage-1 block (unit 1e as written):** 1e's "deletes `SF_WINDOW_STOP` as a stop fact" and N4's "T-FIND
  reads T-FRAME's contracts" cannot be byte-identical; the cheap fix (keep the bit, renamed, or state that
  the legacy frame rows are asked before the method) is a text change, so it blocks 1e's go, not 1a-1d.

## V2

FIX-3: Table E reads hooks/def/gphases; `mf_wdecide` takes no hooks.
- Re-read: Table E's walk `kit_walk(&wf_etable, 0, &in, gphases, 0, &e, &tc, &v)` with `gate_in in = { s,
  def, NULL, NULL, &f }` and `wf_ex e = { d, w, def, gphases, L, fx }` (window.c:1817-1821); E-func/E-stmt
  hold via `kit_legacy_serves(e->d->art, &e->L->site, e->def, e->gphases)` (window.c:1392), i.e. the
  composer's arm walk over the hooks (compose.c:263-296); the plan's C-table offer reads
  `def && def->table_name` (window.c:1150). compose.c:255-258: "`gphases` ... MF_PH_DEFINE for mf_define;
  MF_PH_DEFINE | MF_PH_USE for a one-call entry (mf_emit), which holds the use hooks at selection time, so a
  row whose use-time fields the hooks fail to serve is DECLINED here"; callers :995 (`ask_sel(...,
  MF_PH_DEFINE,...)`), :1161, :1272 (`MF_PH_DEFINE | MF_PH_USE`): quoted correctly.
- The plan call: `int mf_wdecide(const mf_art *, const mf_site *site, mf_wreply *out);` (memfn.h:1450), no
  hooks; window.c:1061 "the decision reads no frame fact (§0): only the window facts are held". pcrec relies
  on it: emit_dfa.c:7600-7602 "The decision reads no frame fact, so one ask serves every NEXT row and every
  selection of this machine" (`window_reply_ask`). window_site.md:86 defines the frame as
  "form/op/handoff/empty/use/body/decl_point/hooks" and :95 "Phase 2, TEXT: pcrec states the frame its NEXT
  row chose". Rev 2 §The shape :53-55 lists "form, handoff, site_kind (the stated consumer kind) ... floor"
  in step 1 FIXED FACTS beside "[rev2 B2: no frame fact here]": by window_site's own definition form and
  handoff ARE frame fields. Contradiction confirmed.
- Not re-verified: that a concrete plan takes different E rows under mf_ask vs mf_emit (by code it can;
  no witness compiled).
- Verdict: **HOLDS.** **Stage-1 block (1e as written):** "T-FRAME at plan time, its answer a plan field"
  needs either the frame + hooks + phase set on the plan call (a pcrec-side change at
  `window_reply_ask`, which asks once per machine before any NEXT row) or T-FRAME stays at text time. Rev 2
  names neither; 1a-1d are unaffected.

## V3

FIX-8: D-hors pre-empts `fd_find` and reads the plan.
- Re-read `wf_find_decide` (window.c:1719-1758): Table D walked first (`fx->drow = kit_walk(&wf_dtable,
  ...)`, :1738); `if (!wf_drows[fx->drow].finds) { fx->holds = 1; return 0; }` (:1743-1746) returns before
  `fd_find` (:1748). wf_drows (:1634-1641): D-hors `finds` 0, opt `WF_HORS_ID`. So Horspool is not a resume
  attached to a T-FIND row; it replaces the find. Rev 2's T-FIND rows "D1c, PAIR, D1, D1w, R7w" with
  "Horspool: D-shift, its admission D-hors's holds kept" (:110) has no row that is Horspool.
- Reads the plan: `d_hors_holds` reads `dx->w->set[dx->w->stop_ix]` (:1595-1597), `w` built by `plan_of`
  from `rd_set` (:1148, the re-seed-aware read); `hors_window` reads the CHOSEN alternative's verify-YES
  span core (:1537-1550); the action `hors_table(w, ...)` (:1557-1568, called :1611) scans `w->off[i]` /
  `w->set[i]`, the sets the plan TESTS (T-VERIFY's output). Rev 2's order "T-FIND (method + resume) ->
  T-VERIFY" is inverted for this row.
- Renders only on E-find: Table D comment "asked on E-find's text only (a legacy row's own text resumes at
  c + 1, as today ...)" (:1573-1575); E's legacy rows walk first (THE ORDER comment, :1440-1444).
- The SUSPECTED population (D-hors holds while a legacy row serves): **not verified** (the setup is quiet
  in the trace; not countable from R-33).
- Verdict: **HOLDS** (code). **Stage-1:** a design-text defect for 1d/1e ordering; byte identity is
  reachable by keeping today's order (Horspool row first, after the frame), so it blocks the 1d/1e TEXT,
  not the feasibility.

## V4

FIX-7 + SLOT-1: B-fn re-walks `fn_rows` BODY; same method, two texts.
- Re-read `b_fn_holds` (window.c:1673-1683): `b->pick != FF_PAIR || !legacy_ok(...) || eb` -> 0; then
  `translate`, `ofs_fn_serves(..., &two) && two`; `ofs_fn_serves` (ofsskip.c:478-491) walks
  `kit_walk(&fn_table, FN_BODY, ...)` and sets `*two = ... fn_rows[r].render == pair_body`. Comment
  :1667-1669 "so B-fn never renders another method under PAIR's name (where they would not, B-pair renders
  the pick)". wf_brows order B-fn, B-pair, B-memchr, B-walk (:1693-1707).
- Re-compiled (trace build): smp05 `(?:(?i:abs)|(?i:ab)S)`: `FDROUTE row=PAIR arm=E-find`, `table=fn
  chosen=fn-pair`, C has `static inline size_t rx_mf1_ofsskip__body(...)` (vA/smp05.c:60) and a call at
  :105. pr09 `x[Q%]y`: `FDROUTE row=PAIR arm=E-find`, no fn walk, C is an inline statement-expression with
  two memchr streams on 37/81 (vA/pr09.c:68). Same method PAIR, same frame row E-find, different C. The
  critics' 28/73 split of 101 E-find+PAIR traces not re-counted (structure confirmed instead).
- Rev 2: "renderers select TEXT by the plan's method and frame row" (:89); reply grows "method, resume,
  frame row" (:91-92); 1e "deletes B-fn's reconciliation" (:280) while "OFS's `fn_rows` BODY" is NOT in
  stage 1 (:283-284) and `b_fn_holds` is a ratchet member (:292). Contradiction confirmed.
- Verdict: **HOLDS.** **Stage-1 block (1e):** the emit key is not a function of the reply's fields; 1e
  must keep B-fn's agreement test (or add a renderer field / split E-find) to stay byte-identical. Text fix.

## V5

FIX-1 (+addendum) + SLOT-7: unit 1a's six rows carry two denies.
- options.def:61-67: `MF_OPT("fd-r8", MF_OPT_DENY, ...)` "the finder table's row R8 ..." and
  `MF_OPT("fd-ndisp", ...)` "the finder table's N-dispatch rows R1 and R2"; the block comment above
  (:58-60) "`fd-r0` and `fd-r5` RETIRED at B4' with their rows". finder.c fd_rows: R8 `"fd-r8"` (:253),
  R1 `"fd-ndisp"` (:273), R2 `"fd-ndisp"` (:279); R3a/R3b/R4 carry no deny.
- registry.md §6¶8a (:158): "the finder rows R0, R5 and R7 were withdrawn with their denies `fd-r0` and
  `fd-r5`; the names are retired, `--memfn=no-fd-r..." (the precedent); rows `fd-r8` (:168) and `fd-ndisp`
  (:169) are spec rows ("Inert ..."); §6¶8b (:177) "`memfn` section floor: 14".
- emit_sweep.py:556-558: ASSERT_ZERO arms `"--memfn=no-" + row` for `base in ("byte", "utf8")`, `stream in
  ("c-default", "c-vm")`, `row in ("fd-r8", "fd-ndisp")`: quoted correctly. Other readers by `grep -l`:
  tests/memfn/finder_check.py, tests/memfn/rows_check.py, tests/axes/memfn_arm.py, docs/spec/registry.md,
  scripts/emit_sweep.py (+ design history docs). Line numbers in the test files not re-checked one by one.
- Addendum: the pay column (last field) is 1 ONLY on R1 (`&ct_r1, 1`, finder.c:276) and R2 (`&ct_r2, 1`,
  :282); every other fd_rows entry is 0. `mf_finder_pay` is public (memfn.h:1557) and read by
  tests/memfn/arm_fixtures.c:1685. Holds: 1a's "7 members" does not say whether the pay machinery and the
  public entry go.
- `pres_row` index shift: `cls->pres_row[i] = (uint8_t)(d.terminal + 1)` (finder.c:1058); pcrec reads it
  only under `#ifdef PCREC_CAND_TRACE` and resolves it through the listing to the row id
  (memfn_sites.c:779-790), so the trace TEXT and emitted bytes do not move; only the `mf_class` VALUE does.
  HOLDS as stated (no byte; a value change), minor.
- SLOT-7's reading of rev 2 :100 ("the namespace is unchanged (D147 add. 9)") as a 1a claim is a stretch:
  that sentence is A-PLAN open point (5) on denies-as-filters, not 1a. The finding stands without it.
- Verdict: **HOLDS** (FIX-1, addendum, SLOT-7). **Stage-1 block (1a):** as written, 1a's witness
  "byte-identical on EVERY arm (... each `--memfn=no-X` deny ...)" cannot pass if the denies retire (two
  arms become refused options, `--list-axes` floor 14 -> 12, a registry.md hunk owed, D80); if they stay,
  two denies deny nothing. A small text decision (state the disposition, or shrink 1a to R3a/R3b/R4).

## V6

FIX-6 + SLOT-2 + SLOT-6: Goal 3's census vs rev 2's own kept deciders.
- Rev 2 Goal 3 (:28-31): "six question tables, four pick-side tables (two are defaults that retire by
  census), one named untabled pair ... a second decider that stays byte-identical fails it." Pick-side
  list (:117-122): KEY, M, TIE, and "**T-PICK** (arrives with stage 3's first row)"; ratchet (:293-294)
  "stage 1 adds no member (T-PICK waits for stage 3 ...)". After stage 1 there are THREE: count error HOLDS.
- Kept second deciders, by rev 2's own text: T-CMP "generic.c's per-byte RUN chain stays a SECOND decider
  until U8's unit change" (:113); "`fn_rows` BODY ... stays a decider until pcrec states a kind on OFS
  sites" (:127-128); the RESEED KEY row "keeps `scan_ok`'s one-member test itself" (:126-127; code
  window.c:446-449 `count(a->spans[i].set[0]) == 1`, beside T-FIND's one-member rows). Only "vrun's KA/KB"
  is named untabled (:124). So the check as worded is red at every stage-1 HEAD: HOLDS.
- `fn_rows` PREFIX is its own first-match kit_table rows (ofsskip.c:418-420, `FN_PREFIX` rows `vrun_w32`,
  `vrun_w16`, their own denies) walked separately from BODY: HOLDS (rev 2 calls SIMD forms "rungs of a
  T-FIND row", which is the intent, not today's table count). compose.c `arms[]` as the renderer/frame
  selector for non-plan sites: code HOLDS (select_arm walks `arm_table`, compose.c:290-291); SLOT-2's
  non-window site counts (generic 5,541 etc.) not re-counted.
- SLOT-6 (census cannot see non-kit_walk deciders): translate's run rank (window.c:1320-1343, an inline
  insertion sort, comment "ties to the higher position, as pcrec_find_run_rank") and `run_member`
  (window.c:763-782, `tie_takes(T_MASS_STRETCH, ...)`) both pick the run member, neither is a `kit_walk`
  table nor matches a `_holds|_choose` name: HOLDS. Rev 2 names no grep pattern and no table->function map.
- Verdict: **HOLDS** (all three). **Stage-1 block:** Goal 3's check, as written, can never pass at a
  stage-1 HEAD (a check that cannot pass): it needs a named exception list with retiring triggers and a
  corrected count (3 pick-side tables), and an implementable census (map + grep + sabotage row). Text fix.

## V7

FIX-5 + SLOT-3: inline ties outside `wf_ties`.
- translate's rank (window.c:1325-1341): `for k: i = n-1-k`, insertion `while (j > 0 && p->rank_ppm[j - 1]
  > c)`: an equal mass stops the shift, so the earlier-inserted (higher) position ranks first: ties to the
  HIGHER position, inline, not read from `wf_ties`. HOLDS.
- presence run window (presence.c:183-188): `if (w == lo_s || wm < wl) { wl = wm; at = w; }` over
  ascending w: the LEFTMOST window on a tie, inline. `wf_ties[T_WINDOW]` (window.c:98-100): TIE_LEFTMOST,
  "today's; no kit reader (window_site.md §9)": the kit has its own unread spelling. HOLDS.
- `tie_over` (presence.c:128-134): `oa = a->member_order == MF_ORDER_UNKNOWN ? 0 : ...`, compares member
  order then `one_byte(...)`; `tie_takes(int r, int32_t c, int32_t b)` (window.c:107-110) compares
  offsets. The new row needs a second comparator shape, and the UNKNOWN-below-known value is unstated in
  rev 2 ("pattern order, then the larger byte", :120-121). HOLDS.
- Also: P3's scan position loop (presence.c:173-177, "rightmost first: a tie stays", strict `<`) is the
  `run_scan` spelling 1c retires (rev 2 U2), consistent.
- Verdict: **HOLDS.** **Not a stage-1 byte block** (all can stay byte-identical); it falsifies "`wf_ties`
  the one tie table" after stage 1 and feeds V6's red census: maintenance/doc, fix by adding the two
  inline ties to 1b/1c or listing them as kept.

## V8

FIX-4: `window_mass` sums per (position, member).
- Code (presence.c:101-113): for each of `MF_PRES_WINDOW` (= 8, memfn.h:1620) positions, every cube
  member `k++; if (rate) m += rate[t->run[j] | b];`: a multiset sum; NONE `uniform_mass(k)` over the
  member count. `kit_set_sum` (:89-96) sums over a byte SET.
- Constructed case (vA/v8_window.py, .out; prior a322116b1b87f9f6 from the sweep's rates.json; the
  run_window loop of presence.c:173-189 transcribed): run `zzzzzzz~J` (rates 498 x7, 83, 108). Scan = '~'
  @7; windows 0..1. Multiset (today): w0 3,569, w1 3,179 -> window 1. Set-shaped primitive: w0 581, w1 689
  -> window 0. The pick moves. Arithmetic transcription, not compiled.
- Rev 2 1b says "one mass primitive (named capped/uncapped argument; `window_mass` keeps a NONE-mode
  total ...)" (:277): input shape unstated; a set-shaped reading moves bytes. The landmark ceiling product
  (presence.c:231-237) not re-read.
- Verdict: **HOLDS** (as an unstated input shape that decides byte identity). **Stage-1:** a 1b byte-
  identity hazard; fixed by one sentence (the primitive takes a position/cube list, or window_mass keeps
  its own sum). Not a block if stated.

## V9

SLOT-4 + SLOT-5: presence ordering, C-bound, grouping.
- P4 is the order row: finder.c:1049 "P4, the order row, asked on its own (deny, gate, predicate)"; the
  chain order + coverage rule follow (:1063-1089, "the chain order, and the one coverage rule": HEAD/RUN/
  REST, a REST member a whole exact run covers is un-verified). Rev 2: T-VERIFY "replaces Q5, PRES part
  ordering ..." (:111) and U10 in 1d (:364) while presence keeps its own entry in stage 1 (:47-50) and
  T-PRES lists P4 (:114). Double-booking HOLDS; the chain order/coverage is in no rev-2 table: HOLDS.
- `implied_by` (precheck.c:158-182): a FUNC part implied by a later part, lever `KIT_LEVER_PRES_WINDOW`:
  decides which members a pass tests inside the renderer; unplaced in rev 2: HOLDS.
- C-bound (window.c:949-952): `{ 2, "C-bound", c_always, NULL, "a FULL-SET position is never a plan test
  ... Applied inside C-yes ... and C-floor" }`; rev 2's step list (:111) names C-floor/C-yes, C-model/
  C-none, C-pin, C-stop, C-run, C-asc, not C-bound. HOLDS, doc-level (it has no `apply`; it is a clause of
  C-yes/C-floor, so "in no step" is a naming gap, not a lost behaviour).
- Grouping: `find_groups` (:1481-1500) groups a `pterm` stretch only `if (j - i >= 2 && run_group_ok(w, i,
  j) ...)` (core and run-shaped, :1467-1473); `translate` (:1280-1293) groups by `pterm` equality alone
  (`grouped = j - i >= 2`). Two rules for one plan's grouping: HOLDS.
- Verdict: **HOLDS** (both). **Not a stage-1 byte block**; SLOT-4 makes U10's PRES half unfalsifiable
  ("where byte-identical") and contradicts B4 (a text fix: move PRES ordering to T-PRES); SLOT-5 is
  doc/maintenance.

## V10

MEAS-1 + SIM-5: `streams x byte(method)` with a per-method `find.byte` card.

Re-ran: subject :170 "stream methods (memchr, memchr-back, PAIR): streams x byte(method) x 1e6"; `streams` is defined nowhere in the note (grep: only that line). Card table :192: "`find.byte` per method (memchr, memchr-back, PAIR, walk; ...) | byte scanned". C1's principle :181-182 ("a PAIR's second stream is in its measured `hit(PAIR)`, not a formula factor"). `onestream.py` prices `streams * C_SCAN * PPM` with C_SCAN = 0.06 (memchr's), i.e. byte(PAIR) read as a PER-STREAM number. Recount re-run (`python3 -I onestream.py r33_sim sweep.jsonl`, verify/vB/onestream.rerun): byte-identical to the committed onestream.out (P PAIR 144,694.0 / '/' 153,476.5 at hit 20; 166,634.0 at hit 40).
Reading B computed: if `find.byte(PAIR)` is the PAIR method's own per-subject-byte cost (= 2 x 0.06 = 0.12, what "per method ... byte scanned" most naturally means), the formula's `streams = 2` adds a further 120,000: P PAIR = 144,694 + 120,000 = **264,694** at hit 20 (286,634 at hit 40) vs '/' 153,477, so '/' wins under P at EITHER hit value and §Robustness's "under P the verdict turns on `hit(PAIR)`" holds only under reading A.
Verdict: **HOLDS** (both MEAS-1 and SIM-5; the 264,694 reading is arithmetically exact). The defect is an undefined factor/card unit, not a wrong number under the script's own reading. Not stage-1 blocking (stage 1 reads no card); owed before stage 2's card definition / the first priced stream row. Does not touch ONE-STREAM (a hand row, reads no card).

## V11

MEAS-2, MEAS-3, MEAS-5, MEAS-6 + OWNER-3, MEAS-7.

**MEAS-2 (hit(hors) uncarded).** Subject :174 Horspool line reads `hit(hors)`; the only prerequisite lists are :262 "With `hors.probe` and `hit(walk)` defined and carded, priced Horspool is decided by measured cards" and :338 "Horspool priced ...: `hors.probe`, `hit(walk)`"; :453 (C6 disposition) the same. `hit(hors)` occurs only at :174 (grep). `find.byte`'s method list (:192) is memchr, memchr-back, PAIR, walk; `find.hit` (:193) is "per method" with no list. **HOLDS**: the line names a term neither prerequisite list carries. The verify_r-excludes-S_last sub-point is a fair ambiguity (q_r = m(S_last) and verify_r's sum has no stated exclusion), HOLDS as a doc gap. Later-stage only (priced Horspool row).

**MEAS-3 (exact-once rounding vs fixed point).** Subject :164-167 "each term computed exactly and rounded half-up once at its end (D176 Q5: integers; no per-factor truncation ...)". D176 Q5 (decisions.md D176 row): "prices are higher-resolution fixed-point integers, deterministic on every host and compiler". measure_sets §1.7: "round half AWAY FROM ZERO at the final division. In C this uses `__int128` intermediates". Re-ran `meas/factors.py` over the sweep (verify/vB/factors.out): 5,329 alternatives, **192** with > 6 non-full positions, **34** in the >= 20 bucket — both counts reproduce. Arithmetic: `m(S) x prod pass(j)`, pass = m/1e6, exact over k positions needs a numerator of up to 1e6^k; int128 (~1.7e38) holds k <= 6. **HOLDS**: "exactly, once" is not implementable in the declared int128 fixed point for 192 alternatives without a declared scale or bignum; "half-up" vs §1.7's "half away from zero" is a naming mismatch (same on positive prices). Later-stage (first priced row); stage 1 keeps plan_cost.def integers and truncation (:136-137).

**MEAS-5 (verify.cmp two regimes, one term).** Card :195 "pass rate 0 and 0.5 | C_VERIFY (UNMEASURED), C_MISPRED"; formula :175 `verify_r = sum_i cmp(form_i) x prod_{j<i} pass_r(j)` — no pass-rate argument. Today's code does carry it: window.c:385-389 `verify_cost(ppm)`: `tail = min(ppm, PPM-ppm); return COST(C_VERIFY) + COST(C_MISPRED) * tail / PPM;` and plan_cost.def:42 C_MISPRED 1500 (= 6 x C_VERIFY 250). **HOLDS**, and stronger than stated: the formula drops a term today's model has, so the card's 0.5 regime has no reader. Later-stage.

**MEAS-6 + OWNER-3 (qualifier ranking inside the band).** Subject :153-156 "Among qualifiers: the least worst-case ratio `max_r price_r(c) / price_r(default)`, then TIE. A default within band of every candidate is TIE's row T_BAND -> TIE_DEFAULT". D176 Q5: "prices within the measurement-noise band tie, decided by the existing declared tie rows". guide addenda/kit.md:39-42 "Prices within the measurement-noise band count as a tie and are decided by the existing declared tie rows, never by which price happens to be lower. **Why:** an argmin over noise is an arbitrary pick that moves with a re-measure." **HOLDS**: the band governs only default-vs-candidate; two qualifiers within band of each other are ordered by the ratio (a sub-noise argmin), and "then TIE" applies only on exact equality. A3 is PARTLY. Later-stage.

**MEAS-7 (comparison band; model error 0 at first row).** Subject :234-238 defines "A price's band" (per price) and "the spread of that ratio is the model-error term the NEXT priced row adds to its band"; :151-152 "cheaper than the default beyond the band" names no combination rule for two prices sharing cards. **HOLDS** on both halves: comparison band unspecified (sum / quadrature / band of the difference differ near the edge); the first priced row carries model error = nothing measured (it is guarded by its own 588-style run, which the note implies via D186 but does not say is the substitute). Later-stage.

Stage-1 impact of V11: none (all five concern priced rows after stage 2).

## V12

MEAS-8: noise becomes a decision input; the digest and no-shadowing exclude it.

Re-read: `docs/spec/measures.md` [3.3¶1] "`values_digest` is FNV-1a-64 over ... the key's bytes, a NUL, the unit byte, the status byte and `value_e6` ... It covers no provenance column, card, cell or member, so the same values from any provenance give the same digest." [2.2¶3] "The other columns are provenance and display, carried as text" — `noise_e6` is one of the `rows` columns not in the digest (header row :79 lists `key unit value_e6 abs_ns_e6 noise_e6 ...`). [5¶4] "A set read from a file ... whose (`id`, `rev`) is a committed set must have that set's `values_digest` ... So a stamp naming `id@rev` always names the values the store holds." [4¶2] stamp = `id@rev:values_digest`. measure_sets.md §4.1 (:950) "No selection reads noise today." Subject :203-206 (stage 2 owes: kit request, noise field "an MF abi event with its `measures.md` §4 and match_api hunks", producer, derived-row rule) and :234-235 (band = card noise x coefficient) make noise decide a priced pick.
Consequence check: a FILE naming committed `zen4-grid1@1` with identical `value_e6` but different `noise_e6` passes [5¶4] (digest equal), stamps the identical string, yet can move a within/beyond-band verdict: the stamp no longer names everything that decided the bytes. One nuance: measure_sets §2.2 (:587-588) says "a user set may not reuse a committed id (§3.3)", but the CONTRACT ([5¶4]) admits a digest-matching file, so the spec reading governs. Also "`measures.md` §4" is the stamp section (§4 heading :146), not the kit channel.
Verdict: **HOLDS**. Later-stage (stage 2 / first priced row); not stage-1 blocking.

## V13

MEAS-9: "zen4-grid1 rev 2" vs "new run = new id".

Re-read: `measures.md` [8¶1] "A committed revision never changes: a second reading of the same cells is published as a new `rev`, and a new run as a new `id`." measure_sets.md §2.2 (:590) "A re-measure on the same box is a NEW id (`zen4-grid3`), because it is a new run." Subject :208-213: "the grid keys are re-measured under it; the job is grid-sized ... It lands as a new REVISION of the box's set (D176 Q3: `zen4-grid1` rev 2) ... whether a revision may carry a successor method version is measure_sets' question, asked of main before the job (if not: a new id, said as a departure from D176 Q3)". D176 Q3 (decisions.md): "... as a new revision of the box's set"; plan [MEASURE-SET] next-line: "as zen4-grid1 rev 2". kit-grid.tsv header: "`ver 2` (grid2's ...)".
Verdict: **HOLDS**, with a qualifier: rev 2 follows the owner-ruled wording (D176 Q3 and the plan row) and already names the new-id fallback as a departure, so it is not silently wrong; the defect is that the question it asks (method version) is not the one the contract decides on (a new RUN is a new id regardless), so the contract already answers "new id" and the conflict to surface is D176 Q3 / [MEASURE-SET] vs spec [8¶1]. Doc/design; stage 2, not stage-1 blocking.

## V14

MEAS-10: DEFAULTS flip owed; M2 envelope excludes per-byte cost rows.

Re-read: `measures.md` [5¶6] "Today there is one class, `idk` ..., and its default is the latest committed set: `zen4-grid1@1`"; [8¶1] `DEFAULTS` maps each class to its default `id@rev`, `DEFAULTS.log` records each change. measure_sets.md §3.4 (:788ff): "RULED (D166 addendum 2): M0 and M1 ship D166's literal reading. ... a bare compile reads the LATEST committed non-synthetic set"; "The envelope default (D161 add. 12) arrives at M2"; "Every row whose safe direction is `none` (every per-byte COST, the unit included) is excluded from an envelope. So under it ... every reader of a cost row skips"; "At M2 the default for each class flips ... The flip is a default-set change. It carries a census in its commit (§8.4) ... It is an abi event (§3.6)". Plan [MEASURE-SET] (:183) "the envelope default is M2". Subject :215-217 ("an unnamed compile uses `idk`'s set (`zen4-grid1@1` ...): a conscious choice") and :299-300 (stage 2 "No reader, no consult, zero movers, stamps unchanged"); §What moves (:417-428) names neither move.
Checks: (1) `zen4-grid1@1` holds no span card (stage 2's are new quantities), so a priced row on a bare compile finds every card absent and keeps, until DEFAULTS names the new set — a default-set change with its census, unstated. Stage 2's "zero movers" stays TRUE (no reader yet, stamp-on-consult only), so the flip's movers land with the first priced row, which is where the note must say it. (2) Span cards (`find.byte`, `find.hit`, `enter`, `hors.probe`, `verify.cmp`) are per-byte/per-event COST rows, so at M2 they are excluded from the envelope: priced rows go dark on every bare compile, and every artifact whose pick consulted re-stamps (and may revert to the default pick).
Verdict: **HOLDS** (both halves; M2 is planned, not landed, as the critic says). Later-stage (stage 2/3 and M2), not stage-1 blocking.

## V15

MEAS-11: no MFTRACE in the artifact; `consulted` never assigned.

Re-ran (2 compiles, verify/vB/): review build `build/pcrec -p rx --measures=zen4-grid1 -o s20.c --pattern '(?i)x/1234'` rc 0: `grep -c MFTRACE` = 0 in s20.c, s20.h and stderr; `#define RX_MEASURES ""` (s20.c:311). Trace build, same flags: 98 `MFTRACE` lines on STDERR only, 0 in s20t.c. `git grep -E 'consulted *= *[^=]' -- memfn/src` -> only compose.c:1303 `if (consulted) *consulted = art->consulted;` (the out-param copy); `art->consulted` is declared at kit.h:292 ("set when a ROUTED finder decision resolves", :288) and never assigned anywhere; finder.c:862 "`consulted` here; the first one that does is B4's". measure_sets §4.2: the kit reports "ONE fact ... `consulted` (a boolean)", "no per-key traffic". Subject :413-415: "the keys a pick read are counted pcrec-side (the stamped set against the artifact's trace), not by the kit's consult recorder".
Verdict: **HOLDS**. The artifact carries no trace; the only trace is the kit's own stderr self-report from a separately built binary, so "counted pcrec-side ... against the artifact's trace" names a source that is (a) not in the artifact and (b) the kit's self-report (a K35-shaped control sharing a source with its subject). Setting `consulted` from T-PICK is owed and unstated. Later-stage (first priced row); stage 1 and ONE-STREAM (no consult) unaffected.

## V16

MEAS-13 + OWNER-2 (SIMD-form cards; rule 6 vs the owner's per-layer winner).

Re-read independently:
- Subject L161-162 (rule 6): "Only scalar plans are compared; SIMD forms are rungs inside the chosen
  scalar plan (D147), so a SIMD-on compile never picks another stop or alternative." L192 (card):
  "`find.byte` per method (...; each SIMD form its OWN row, no layer column `[rev2 C7]`)". L374 N12:
  "vany: a T-FIND SIMD form, declined (no card) | live when carded".
- roadmap.md :56-57 "The target (SIMD layer, CPU) is an input given at the top, like a compile flag."
  :67-71 Motivating case O-117 "... x1.95 slower on the scalar build, while a two-load vector window
  plausibly wins with SIMD on. Under this shape the scalar build and the SIMD build each choose their own
  winner, with no special case." (agreed 2026-11-02, :43).
- plan.md :1541 [COVER-PRICE-WITNESS] Charter: "add the pattern to the pricing tests on BOTH layers ...
  solved only when the chosen arm is no slower on both (Frank 2026-11-02: not cover-or-not, it depends on
  whether SIMD is in the cards ...)".
- decisions.md :9000 D147: "SIMD is a LAYER on top of the scalar algorithm and never a substitute for it
  ... The scalar layer (the algorithm: what is searched, the plan, ...)"; "each layer must be the best it
  can be on its own".
- measure_sets.md §7.3 (:1239-1240): "A quantity nobody reads is not measured (D77)."

Verdicts:
- MEAS-13: HOLDS. Under rule 6 no pick compares SIMD-form prices, so the per-SIMD-form `find.byte` rows
  have no T-PICK reader; the only reader rev 2 names is N12's "live when carded" rung admission, which is a
  priced choice outside T-PICK (no D186 row, no deny, a SIMD-only stamp consult that §What moves does not
  list). Later-stage only (stage 2 card list / reader closure); not stage-1 blocking.
- OWNER-2: PARTLY. HOLDS that rule 6 contradicts roadmap §0a's owner-agreed sentence ("each choose their
  own winner", target an input at the top) and that rev 2 neither cites it nor asks the owner; rev 2's
  reading does have D147 behind it ("the plan" is the scalar layer's), so this is a genuine owner-level
  conflict between two rulings, not a mis-citation. OVERSTATED part: O-117 / [COVER-PRICE-WITNESS] is a
  cover-vs-byte-class-scan ROUTE choice (pcrec's frame/route; rev 2's Non-goals exclude engine/route and
  its own L330 calls DEF's route change "confounded"), so rule 6 (stop/alternative inside a site) does not
  by itself make that row's acceptance "unreachable". Later-stage (priced rows; rule 6 reads nothing in
  stage 1); not stage-1 blocking. Owed: one owner question.

## V17

SIM-1 (`--engine=vm`: smp20 two NONE non-COVER sites; pr09/c04989 not movers; the sweep's arms).

Re-ran: 4 trace-build compiles (`tracebuild/pcrec -p rx -o ... [--engine=vm] --pattern P`, `timeout 60`,
outputs verify/vC/*.c/.err): smp20 `(?i)x/1234` vm and default, pr09 `x[Q%]y` vm, c04989
`x[\x{e0}-\x{ff}]y` vm. Plus the sweep's arm set (python over sweep.jsonl).
- Sweep arms: {(bench,RTE), (corpus,RTE), (s588,RTE), (s588,DEF)} only: no vm, no SIMD, no other deny. HOLDS.
- smp20 vm: two kit window sites, both `wfA chosen=A-mass fields=entry:R2:NOENTRY`:
  site 2 `SEL ... form=FUNC handoff=RETURN`, `wfE chosen=E-func`, `fn chosen=fn-pair`, FD records
  `kind=VM_ATTEMPT` (216 of them, all site 2); C = `rx_reqrun__body`, two memchr streams on 88/120 ({X,x})
  (vC/smp20_vm.c:211-235). Site 3 `wfE chosen=E-stmt`, `FDROUTE site=3 row=R7w arm=pf_walk`; its C is the
  start-set walk with `rx_start_set` = {88,120} (decoded). Both stops are {X,x} k=2 with '/' (4,154 ppm)
  under the 7,812 bound, so row 1's text (NONE alternative, no COVER clause) holds on both. Neither is a
  COVER (REPORT) site. HOLDS.
- smp20 default: one site, A-mass, E-find, `fd chosen=PAIR` (memchr 88/120): the census's COVER site. Agrees.
- pr09 vm and c04989 vm: site 2 `wfA chosen=A-mass`, `fd chosen=D1w`, `wfE chosen=E-stmt`, start-set walk
  bytes = {120} only ({x}): already the one-member stop, so NOT movers on vm. HOLDS (the held-out class is
  empty on the vm arm).
- Side observation (feeds SIM-7, not in my groups): smp20 vm's `RX_REQ_BYTE "47"` while the kit's reqrun
  body scans {X,x}: pcrec's pre-check states '/' as its byte and the kit's run scan stops on {X,x}, i.e.
  row 1 there would move a kit stop on a pcrec-owned pre-check part.
Verdict: HOLDS (all three parts). Not stage-1 blocking (stage 1 is byte-identity on every arm, which R-33's
sweep never claimed to cover; the per-unit witness re-runs every arm). It blocks ROW 1's census/held-out
claims (stage 3): the movers census and the held-out class must be recomputed on the vm (and SIMD/deny)
arms before the row's run.

## V18

SIM-2 (k >= 13 crossover under rev 2's formula, Zen 1 constants).

Re-ran (verify/vC/v18.out, exact fractions): plan_cost.def (review tree) C_MEMCHR 6 (0.06 c/B), C_BITMAP
116 (1.16 c/B, "the 256-entry walk"), C_VERIFY 250, C_ENTER 2000; hit 20 c (R-33's assumption, V21). Prior
`a322116b1b87f9f6` from sweep.jsonl.rates.json: 'e' 84,235 ppm, [\x80-\xbf] total 128 ppm, {x,X} 1,097,
'/' 4,154.
- One byte AT the bound `floor(k x 1e6/256)` vs a zero-mass walk default (k >= 3), stream line
  `0.06e6 + m x (20 + 2.5)` vs walk `1.16e6`: k=12 bound 46,875 -> 1,114,688 < 1,160,000; k=13 bound 50,781
  -> 1,202,573 > 1,160,000. First P-loss at k = 13. HOLDS. Since A-mass makes the default the least-prior-mass
  stop (m_default <= m_one), the general P-loss needs (m_one - m_default) x 22.5 > 1.1e6, i.e. m_one > 48,889,
  reachable only when the bound exceeds it: k >= 13 is the exact threshold for walk defaults.
- The constructed `[\x80-\xbf]e`: 'e' 84,235 <= bound 250,000 (k=64), row departs; P: memchr 'e'
  1,955,503 vs walk 1,163,096 (1.68x worse). Matches SIM's numbers to the unit. HOLDS.
- Nuance the critic does not state: the same simple comparison at k = 2 (two-stream PAIR default, 0.12e6)
  also loses at the bound (235,770 vs 120,000); this is the smp20 P-ambiguity rev 2 already admits
  (§Robustness table, hit(PAIR)), so SIM-2's NEW content is specifically the walk-default range k >= 13,
  where "Why the bound" (candidate counts only) ignores the walk's per-byte cost.
- Population: zero in the sweep (rev 2's census: holds only at k = 2 and k = 32 c04989, where P favours 'x').
Verdict: HOLDS (latent speed risk; the computation reproduces). Stage 3 (row 1's condition) only; not
stage-1 blocking. Remedy is a condition clause (k range, or k <= 12) stated before the row's run.

## V19

SIM-3 (T_MASS_STRETCH -> TIE_HIGHER vs onestream.py's min(mass, off); `(?i)x1234`).

Re-read: memfn/src/window.c:86-90 `[T_MASS_STRETCH] = { "A-mass at a position inside a stated run stretch
(one-member or cube, C-run's grouping) ...", TIE_HIGHER, ...}`, :91-92 `[T_MASS_SET] ... TIE_LOWER`;
`tie_takes` :107-110; `a_mass_choose` :544-561 (`int row = in_stretch(p) ? T_MASS_STRETCH : T_MASS_SET;`
`ms < bm || (ms == bm && tie_takes(row, k, bk))`); `in_stretch` :522-526 (`p->multi && shape(...)`, shape =
one-member or cube). Subject L315 "stop at the least-prior-mass such one-member candidate (ties as A-mass)".
span_pick_dir/onestream.py :20 docstring "lower offset on a tie", :26 and :33
`min(..., key=lambda p: (p["mass"], p["off"]))` for both the default and the row pick.
Computation: prior '1'..'4' = 7,476 ppm each, {x,X} 1,097, bound floor(2e6/256) = 7,812. In `(?i)x1234`
every position is one-member or a cube in one stated stretch, so the A-mass tie row is T_MASS_STRETCH
(HIGHER): text -> @4 {4}; script -> @1 {1}. Two answers.
Not compiled (row 1 does not exist in code; the claim is text-vs-script, settled by the code reads).
Census effect: none of rev 2's 4 holding units has a tied one-member minimum (smp20 '/' 4,154 unique;
pr09/c04989 'x' 997 unique), so 1,637/1,056/577/4 stand (agrees with SIM's diverge.py statement; I did not
re-run its 135-alternative default-stop count).
Verdict: HOLDS. Doc-level now; byte-level for row 1's build (stage 3). Not stage-1 blocking. Fix: the
script (and the row's spec) use the T_MASS_STRETCH/T_MASS_SET rows, or the text says which.

## V20

SIM-4 (counts pool the DEF deny arm; PF statement wrong on 291 + 22 / 740).

Re-ran (python over sweep.jsonl; verify/vC/v20.out; the FIRST block's "core positions" line in that file
is from a buggy first attempt (absolute vs span-relative core_lo) and is superseded by the second block):
- Per arm, with rev 2's own counts.py predicates: PF sites RTE 1,742 + DEF 25 = 1,767; PF with >= 2
  alternatives RTE 1,429 + DEF 25 = 1,454; OFS (form 2, handoff 0) RTE 371 + DEF 10 = 381; RESEED
  alternatives RTE 1,800 + DEF 35 = 1,835, of them A-floor RTE 1,397 + DEF 23 = 1,420. Each quoted count
  pools the 43-pattern DEF deny recompile with the default arm. HOLDS. (1,637 = 1,621 + 16 not re-split.)
- PF entry shapes: RTE (NONE only) 291, RTE (PARKED only) 22, RTE (PARKED, RESEED) 1,429, DEF (PARKED,
  RESEED) 25. So "PF states span 0 on its PARKED alternative" (subject L73) is false on 291 sites (no PARKED
  alternative), and the RESEED claim holds on 1,454. HOLDS.
- Core positions per PF RESEED alternative after C-meet (merge per offset, core if any covering span marks
  it): ONE core position 733 + 7 = 740; >= 2 core positions 696 + 18 = 714; >= 2 NON-FULL core positions
  443 + 14 = 457. So "a RESEED one with several core positions" fails on 740 of 1,454. HOLDS, exactly SIM's
  numbers.
Verdict: HOLDS. Doc-level (rev 2 L73-74 and its E1 row; the later RESEED-admission row's population).
Not stage-1 blocking; it matters only for the RESEED-admission row's population and for honest counts
(a deny-arm recompile is not a distinct site: state RTE-only counts or say "units incl. DEF").

## V21

SIM-6 + MEAS-4 (153,476.478 exact; F ratios 2.000 / 3.056; plan_cost.def has no hit row).

Re-ran independently (verify/vC/v21.out, exact Fractions, rev 2's formula L170-176: stream line
`streams x 0.06 x 1e6 + m(S) x (hit + verify) + passes x 20`, verify in ascending mass with cmp 2.5, prior
`a322116b1b87f9f6`, F = |S| x 1e6/256):
- P, '/' memchr: 153,476.4781559... ; rounded half-up once = 153,476. Rev 2's table says 153,477 (its
  script prints 153476.5, a second rounding). HOLDS.
- P PAIR {x,X}: 144,693.978 (hit 20), 166,633.978 (hit 40): rev 2's 144,694 / 166,634 hold; 6.1 % and 8.6 %
  hold.
- F: PAIR/'/' ratio = 1.99999999999904 at hit 20 and 3.05625 at hit 40 (147,929 / 295,858 / 452,108 hold).
  "F favours '/' 2:1 either way" (L248) is "at least 2:1" (2.0 and 3.06). HOLDS as a wording point.
- plan_cost.def's MF_COST rows (review tree :29-61): C_MEMCHR, C_BITMAP, C_VERIFY, C_ENTER, C_MISPRED,
  MATERIAL_NUM, MATERIAL_DEN, MAX_SET, HORS_MIN; NO hit row. The 20 c is R-33's `H_HIT` (r33_sim/sim.py :29
  "ASSUMPTION (no measurement on file)", :44 CONST; r33_report.md :85 "ASSUMPTION, nothing on file").
  Rev 2 L241 "Zen 1 `plan_cost.def` constants scan 0.06, verify 2.5, enter 20, hit 20 c" mis-attributes
  hit. HOLDS.
Verdict: HOLDS (all three). Doc-level (lesson 1, "every quoted number recomputed"); no verdict changes
(P still turns on hit(PAIR); F still favours '/'). Not stage-1 blocking.

## V22

OWNER-1, 4, 5, 6, 7, 8, 9, 10, 11, 12 (rulings, plan rows, roadmap text).

Sources quoted from the review tree (worktrees/crit-memfn-spanpick2): decisions.md D186 :10020-10036 (+ add. 1),
D176 :9912-9925, D157 :9373-, D167 add. 1 A11 (:9764), D144 :8953-; roadmap.md :43-71 (§0a), :379-408
(A-PLAN); plan rows by tag; units_inventory.md :172-173; bar588_report.md :38; t588tri_report.md :13, :27;
memfn/src/window.c :446-457; memfn/include/memfn.h :1414-1444 (mf_wreply). Subject = the frozen copy.

- **OWNER-1 (hand rows need 1e, not only 1d): PARTLY.** Text conflict HOLDS: L307 "Hand rows need only stage
  1d" vs D186 add. 1 A2 "it becomes our poster child for the FINISHED refactor" and row 1's L315 "T-FIND,
  T-VERIFY and T-FRAME then answer for it". The technical claim "before 1e the stop a T-PICK row changes
  cannot reach the renderers" is REFUTED: today's decision reply already carries `alt`, `has_stop`, `stop`,
  `stop_set` (memfn.h mf_wreply, ~:1430-1437) and phase 2 re-decides method and frame for whatever stop it
  carries, so a stop-changing hand row after 1d renders through today's text call. The fix is owner-intent
  (A2), not a build impossibility. Stage-3 sequencing only.
- **OWNER-4 (A-model's one-member preference + ONE-STREAM = two rules): HOLDS.** window.c :446-449
  `scan_ok`: `walked(a, i) && a->spans[i].core_len && count(a->spans[i].set[0]) == 1` (RESEED's KEY row,
  priced by C_MEMCHR in `a_model_choose`); row 1 (L312-315) is a NONE-only one-member preference by mass
  bound. D186 Relations: "D172 S3's two stop rules are the first unification target"; units_inventory :172
  "U1 ... One Table A stop row priced over (position x method) for every entry kind, so OFS and COVER pick the
  same stop for `(?i)x/1234`". Rev 2 L355 keeps "A-model and A-mass ... as two KEY rows". After row 1 smp20's
  OFS and COVER stops agree by two different rules. Mitigation not stated by the critic: U1's own home is a
  PRICED row, which A1 legitimately defers to cards, so the finding is "name the sibling and where it meets",
  not a ruling breach. Stage 3; not stage-1 blocking.
- **OWNER-5 (Q2 vs D176 Q3; two triggers): HOLDS.** D176 Q3 (owner "Yes but make it a formal thing"): "the
  kit measures this box (zen4) far enough to fill Q1's cost table ... gated on the step-0 census"; Effect:
  "the build waits for the step-0 census and the method measurements". D186 (pre-addendum): "Pricing ...
  returns only if hand-written rows start conflicting". Subject Q2 (L486) leans "only when a fix first needs
  prices (when hand-written rules start to disagree)"; stage 2 (L300-301) "run it when its first reader (a
  priced row) is chartered". Two differently worded triggers; Q2 does not tell the owner he ruled Q3. (The
  D77 case for waiting is legitimate; the owner question is mis-framed, not wrong to ask.) Later stage.
- **OWNER-6 (pilot baseline): HOLDS.** plan.md [PRICE-BAKEOFF] status (2026-11-02): "default 0.981 of ideal
  held-out, PASS at 0 rules ... is the baseline pricing must beat"; pricing_requirements.md :16 "the pilot is
  the baseline any ...". Subject grep: "pilot"/"baseline" appear only at L260 ("Drift gauge: D186's pilot
  distance (0.981), per stage-3 row"); no priced-row acceptance against the pilot; row 1's evidence list has
  no gauge reading. Later stage (first priced row).
- **OWNER-7 (smp04 held; goal order): PARTLY.** Subject L295-297 holds opt rows touching window.c, finder.c,
  ofsskip.c, compose.c, presence.c, "smp04's unit change included, unless the owner rules otherwise"; Goals
  L16 "a higher goal wins a conflict", Goal 2 above Goal 3. [PAIR-LOOKAHEAD-TIME] edits ofsskip.c
  `PAIR_LOOKAHEAD` (row text), so it is held too: HOLDS. bar588 :38 names smp20 and smp04 as what "keeps
  WALK/one/run FAIL": HOLDS. Overstated: t588tri :13 heads smp04 "(WALK/one/norun; 4.475x random, passed only
  by the allowance ...)", so "shipped loss" is a loss inside the allowance and its stratum label disagrees
  with bar588's; and D153 (cited by rev 2) is the owner's own ruling that refactors go first, so the "goal
  inversion" is a reconciliation to state + an owner question, not a breach. SIMD-batch part not verified
  (SUSPECTED by the critic). Not stage-1 blocking (it is about what waits for stage 1).
- **OWNER-8 (two bars for smp20): HOLDS.** Goal 2 L25-26 "it closes by stage 3's first row" (bar: RTE vs the
  row denied, L303-306); Goal 5 L37-38 "RTE/DEF <= 1 + floor on every job-588 cell"; row 1 L333-334 "smp20
  must also close Goal 5 against DEF"; L330 "(DEF also changes the route, so it is confounded)". No outcome
  stated for "row bar passes, DEF bar fails"; A2 forbids narrowing S3's cover row AHEAD of the unification,
  which leaves narrowing-after or an owner exception, neither named. Stage 3.
- **OWNER-9 (D144 item 3 vs D186 narrowing): HOLDS.** Subject grep: no "D144", no "batch gate". D144 item 3:
  "Regressions found at the batch gate become NEW ISSUE ROWS, not reverts"; D186: "a losing regime narrows the
  row's condition". Unreconciled for a stage-3 row's batch-gate loss. Doc/design; stage 3.
- **OWNER-10 (A-PLAN "candidates and cards out"): HOLDS.** roadmap :387-388 "Split the site call into a plan
  call (facts in, candidates and cards out) and an emit call (chosen candidate in, C out), byte-identical";
  open point 1 (:396-397) "the plan face returns a BOUNDED set". Rev 2 L95-97 returns ONE plan (interim) and
  asks Q1 without telling the owner it amends the agreed next-step text; no roadmap edit listed. (Open point 1
  is explicitly "settled at the split", so rev 2 MAY settle it; the omission is the departure statement.) Doc.
- **OWNER-11 (Q3 "does not depend"): HOLDS.** Row 1 admits a one-member candidate whose PRIOR mass is <=
  k x 1e6/256 (L312-314); smp20 '/' 4,154 vs 7,812 (1.88x margin); Q3 (L491-492) "the `(?i)x/1234` rule does not
  depend on them". It depends on the prior's absolute level, not on the x-vs-'/' ranking (which L317-319
  correctly says). Doc (owner's decision input overstated).
- **OWNER-12 (D157 "never a position"): HOLDS.** D157 Ruling: pcrec "does NOT send `mf_pred.plan_pos2` (a second
  filter position chosen by pcrec ...). It sends the site's candidate positions, rarest first, each with its
  prior rate: `rank_n`, `rank_pos[MF_RANK_MAX]`, `rank_ppm[...]`". Subject L86 "never a position, method or
  cost (D157)". D167 add. 1 A11: landmark admission "Until it is restated in code, it is recorded as a D157
  exception"; subject L382-384 carries no exception status. Doc ("never a CHOSEN position").
Overall: none of OWNER-1..12 blocks a STAGE-1 build go (none touches unit byte identity or a stage-1 check);
all bear on stage-3 rows, the open questions' framing, or doc accuracy.

## Stage-1 summary

- Would block a stage-1 build go AS WRITTEN (text fixes, no new measurement needed): V1 (1e deletes
  `SF_WINDOW_STOP`; T-FIND's method depends on the asking frame row), V2 (T-FRAME "at plan time" needs
  hooks/phase/frame the plan call does not take; step 1 lists frame facts), V4 (B-fn vs B-pair: the emit
  key is not (method, frame row); 1e deletes the reconciliation BODY still needs), V5 (1a orphans the
  `fd-r8`/`fd-ndisp` denies: "every arm" witness and `--list-axes` floor 14 move, registry.md hunk owed),
  V6 (Goal 3's census as worded cannot pass at a stage-1 HEAD; pick-side count is 3, not 4).
- Stage-1 text hazards, not blocks if stated: V3 (Horspool row order vs T-VERIFY), V7 (two inline ties),
  V8 (mass primitive input shape: constructed `zzzzzzz~J` moves run_window), V9 (PRES ordering
  double-booked; C-bound unnamed; two grouping rules).
- Later stages only: V10-V22 (every group HOLDS or PARTLY; none touches stage-1 byte identity). PARTLY:
  V13 (rev 2 follows D176 Q3; the conflict is D176 Q3 vs measures.md §8¶1), V16 OWNER-2 (O-117 is a
  route choice, outside rule 6), V22 OWNER-1 (a stop change CAN reach today's renderers before 1e; the
  1e need is owner intent, A2) and OWNER-7 (smp04's loss is inside the allowance; D153 is the owner's
  own ordering). Nothing REFUTED outright; one critic sub-claim refuted (OWNER-1's "cannot reach").

VERIFY COMPLETE
