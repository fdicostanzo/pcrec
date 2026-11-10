# verify — memfn-planframe1

## SPLIT-1
HOLDS (duplicates PREM-2, SAB-3 say the same thing; PREM-2 and SAB-3 both locate the same two lines).
- window.c:2817-2820: `const char *wf_plan_brow(...) { return w->row == &wf_find_arm && w->bren < WF_NBROWS ? w->brow : NULL; }`; w->brow = fx->brow (window.c:1865), set by `fd_find(..., &fx->pick, &fx->brow)` (:1842) = T-FIND's deciding row. Comment at :2813 says "Table B's renderer row is wf_brows[w->bren]"; the renderer accessor is the separate `wf_plan_bren` (:2824-2827, returns "B-pair" etc.).
- finder.c:289 the T-FIND row is `{ "PAIR", FD_FIND, ...`; formhash.c:296 `{ "pair", "-", 1, MF_FH_WINDOW, "PAIR", "Xx", ...`; formhash.c:472 `*row = r->wplan ? wf_plan_brow(r->wplan) : NULL;` then :511 `if (e->row && (!*row || strcmp(*row, e->row))) goto out; /* reached another row */`.
- Design §2.4 formhash row (plan_frame.md:191): "stays valid if the accessor stays (`[rev1]` it returns the composed search renderer row, or B-fn's fused id)". Read literally the accessor would return "B-pair"/"B-fn", never "PAIR", so `pair` is refused. The sentence is wrong as an account of today's accessor (it returns the FIND-slot deciding row). A charitable reading (accessor unchanged) is safe, but the text as written misdescribes it and tells the builder to change it.

## SPLIT-2
HOLDS (PREM-4 says the same).
- window.c:2730-2735 (wf_find_expr): `wf_cand(rc,&b); if (w->bren == B_PAIR) { ... ofs_pair_decl(&b,&t); kb_puts(&b," "); } wf_raise(rc,&b); kb_puts(&b,"for (;;) { ");` - decl is B_PAIR-only, before raise and loop.
- Compile `build/pcrec -p rx --emit-main --pattern 'a[Xx].b'` (verify/p.c) contains: `size_t rx_mf1_c = rx_mf1_lo; int rx_mf1_f = 0; size_t rx_mf1_ha = 0, rx_mf1_hb = 0, rx_mf1_wa = 128, rx_mf1_wb = 128; for (;;) ...`.
- Design §2.6.4 table (plan_frame.md ~:322-330) columns: head, test, next, file scope; the B-pair row has no pre-loop declaration entry (only `wf_b_pair` + bound). So the omission is real.

## SPLIT-3
HOLDS as a conditional (a gate placed unscoped at fd_holds); the design text does not scope it.
- finder.c:498-509 `fd_holds(size_t i, const void *x)` is the single predicate of `fd_table` (finder.c:521 `{ "fd", FD_NROWS, fd_ct, fd_slot, NULL, fd_holds, fd_opt }`); `fd_decide(fd_x *q, int slot, ...)` (:528-533) calls `kit_walk(&fd_table, slot, ...)`; it is called with FD_FIND (:673) and FD_PRES (:765, in fd_pres).
- PRES rows P0, P2, P3, P4, P9 (finder.c:313-336) all carry pick `FF_UNSTATED` (e.g. `FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, ...`). A rule "declines a row whose pick is not in the renderable set" placed in fd_holds without a slot guard would decline every PRES row (FF_UNSTATED is in no renderable set; the PRES walk carries no set).
- Design §2.4 (plan_frame.md ~:165): "`fd_decide`'s row gate (beside `finder.c` :503) declines a row whose pick is not in the set" - no slot scope stated. Real text defect; fix is scoping to FD_FIND.

## SPLIT-4
HOLDS.
- window.c:1879-1880: `w->libc = (uint8_t)((fx->bren < WF_NBROWS && wf_brows[fx->bren].libc) || w->nrun); w->includes = w->libc ? MF_INC_STRING_H : 0;`. The table: `[B_WALK] = { "B-walk", b_walk_holds, 0, "", NULL, ...` and `[B_HORS] = { "B-hors", b_hors_holds, 0, "+hors", d_hors_prepare, ...` (libc 0); B_FN/B_PAIR/B_MEMCHR libc 1.
- So the design's sentence (§2.6.4: "B-hors's probe and S-shift write no `memchr`, and the other search rows do") is wrong for B-walk (also libc 0) and omits the `|| w->nrun` term (check piece's run compares).
- Witness: `build/pcrec -p rx --memfn=no-fd-d1 --emit-main --pattern abcdef` (verify/w2.c) has `static inline uint32_t rx_w4(...) { ...; memcpy(&w, p, 4); ...}` and `#include <string.h>`, from the run compare, with a walk (non-memchr) search. A union of "search + stream" facts alone would give libc 0 there.

## SPLIT-5
HOLDS (SAB-8 says the same hard-wiring point; its (N) deletion consequence is a sabotage-design claim not separately re-derived).
- window.c:2321-2332 `wf_floor_expr`: `wf_test(rc,&t,&cond)`; `wf_open; wf_cand; kb_printf(&e,"for (; %s; ", cond.p); resume_next(rc,&e); kb_printf(&e,") if %s { %s = 1; break; } ", t.p, rc->F);` - skeleton `for (; COND; C++) if TEST {..}`, stream text written in the for-header before the test, `resume_next` called directly (not through any table/index).
- window.c:2274-2279 `wf_test`: `wf_bound(rc, cond); return wf_test_to(rc, t, NULL, -1, 1);` - the bound (cond) comes from the CHECK function and the last arg 1 (lower) differs from E-find's `wf_test_to(rc,&b,o,skip,0)` (window.c:2741) with `wf_raise` before the loop and the bound produced by the search head (`wf_bound(rc,&bound)` at :2725, passed to head).
- Design §2.6 "Today" gives only `for (;;) { HEAD; if TEST {...} NEXT; }`; §2.6.4 floor row lists "none / wf_test / resume_next" but states no per-frame skeleton. Not reached on real output (floor not reachable by a single compile); code read only.

## PREM-1
HOLDS.
- tests/memfn/renderer_rows.tsv exists at a678d0a4e: header "THE DECLARED RENDERER ROWS (span_pick 1e's F4): the (method row, renderer row) pairs `MFTRACE FDROUTE ... row=ROW ren=REN` may print", "HAND-MAINTAINED, and written from the two renderer tables"; columns row, ren, frame, flags, witness; lines such as `PAIR	B-fn	E-find`, `PAIR	B-pair	E-find`, `D1	pf_memchr	composer`, `D-hors	B-hors	E-find`. Reader: tests/memfn/rows_check.py section R (line ~751: `rr = read_tsv(... "tests/memfn/renderer_rows.tsv", 5)`; FDROUTE pairs at :282). memfn/docs/trace_format.md documents FDROUTE (:63, :101-103, :167).
- compose.c:1153-1157: `frow = rid ? rid : wplan ? wf_plan_brow(wplan) : NULL; ... MFTRACE FDROUTE ... row=%s arm=%s ren=%s` with `ren` = `wf_plan_bren(wplan)` (Table B's row) - these names are what the split retires/renames.
- `grep -c 'renderer_rows\|rows_check\|FDROUTE' subject/plan_frame.md` = 0: the design never names the pin, section R, or FDROUTE (only `MFTRACE REACH`). It is a hand pin of (T-FIND row, renderer row, frame) that the split's retirement of `wf_brows`/B-* names would turn red or require editing.

## PREM-3
HOLDS (SAB-2 same point, as the sabotage-side consequence).
- compose.c select_arm (~:316-325): `fd_find(art,s,def,NULL,quiet,&pick,&rid); const arm *ra = rid ? fd_renderer(s,pick) : NULL; *row = rid; if (rid) { for (i...) if (arms[i]==ra) return kit_ask(...) ? ra : NULL; return NULL; } size_t i = kit_walk(&arm_table, 0, ...)` - i.e. whenever a row decided (rid set) and its arm is missing OR declines its own ask, the function returns NULL (refusal); only `rid == NULL` falls through to the walk.
- Same branch serves `?need`: finder.c:663-667 `if (q.span && q.span->need == MF_NEED_UNSTATED) { *row = "?need"; return 0; }` sets rid with no pick; fd_renderer finds no arm; the branch refuses. And the `kit_ask(...) ? ra : NULL` is the arm's own deny/gate decline, which a (frame,pick) renderable set does not see.
- Consequence re-derived: if a builder deleted the branch because the design says the refusal "becomes unreachable by construction" (plan_frame.md:172-173), rid set with ra NULL would fall to `kit_walk` and render some other arm (walk) under the deciding row's name; rows (B)/(C) then would not refuse (they depend on this branch, design :174-175 "would pick PAIR and refuse"). The design's own sentence is overbroad: only the PAIR/HORS sub-case becomes unreachable.

## PREM-5
PREM-5(c) HOLDS (the only sub-item asked).
- `git show a678d0a4e:docs/dev/plan.md`, line 1844 (the row's line): `- [SEAM-READER-CENSUS] STATE:not-started — every mf_* seam member has a kit reader or a listed trigger (a census, Boonies weight)`. The row's indented continuation carries (line 1847) `  trigger: the next MF_SITE_ABI layout event` (found by `grep -n 'next MF_SITE_ABI layout'`; it is the row's own field, 1845 is its `  filed:` field).
- `grep -n 'SEAM-READER-CENSUS' subject/plan_frame.md` finds nothing: the design neither names the row nor says whether 3.0b (which §3 states is an MF_SITE_ABI layout event) fires it. (a), (b), (d) not re-verified.

## PREM-6
HOLDS (the fact); the impact claim (nothing sees arena growth) also holds.
- window.c:1227-1232 (mf_wdecide): "the decision is ~10 KB, so it lives on the heap (R-28 ...); the ask is pure, so not the art's arena; a refused allocation is -1" then `wf_dec *d = calloc(1, sizeof *d); ... free(d);`.
- window.c:1900-1906 (wf_prepare): `wf_dec *d = art->a->alloc(art->a->u, sizeof *d); struct wf_plan *w = art->a->alloc(...); char *pid = ...; wf_legacy *L = ...; wf_fx *fx = art->a->alloc(...)`; also :1846 `fx->fn = art->a->alloc(...)`, :1673-1683 (build_runs), :2034-2035. So the frame part (wf_find_decide/prepare path) allocates from the art's arena; mf_wdecide deliberately does not.
- Purity harness: arm_fixtures.c:161 `static void *a_alloc(void *u, size_t n) { (void)u; return calloc(1, n); }`, :2248 `static mf_arena ar = { NULL, a_alloc };` - a plain calloc arena with no accounting; pur_diff compares replies only (see SAB-9). No check measures arena growth.
- Design §4.1/§2.2 do not say which allocator the shared plan function takes (grep for heap/arena in plan_frame.md finds no statement on it).

## SLOT-1
HOLDS.
- compose.c:1309-1316 (mf_defined): `snprintf(out->form_id, sizeof out->form_id, "%s", r->arm->id);` for every defined site (no arm excluded), plus `out->row = r->fd_row`.
- plan_frame.md:122 (§2.3 `fused`): "On E-func/E-stmt it is the arm the text is written by (the value `mf_result.form_id` reports) ... It is `""` where the family composes the triple: E-find's other rows, and E-generic" - so every E-func/E-stmt ask has non-empty `fused`.
- plan_frame.md §2.6.3 (:312): fused row `E-func, E-stmt | the composer's arm ... each arm's own fused text: the offset-skip function (fn-pair, fn-memchr), the pre-check composite, the PF arms, the generic row`.
- plan_frame.md §2.6.1 (table, `composer` row): `LIBC (by end_back), LIBC_BACK, WALK (by end_back) | fd_renderers' arms | the PF arms (pffind.c): a search only; the caller restarts and checks`, and §2.6.2: `composer | ONESHOT | S-caller | no text: the caller's NEXT loop restarts at c + 1`.
- Both claims cover the same PF arms: composed (search row + S-caller + caller's check) in §2.6.1/2, fused in §2.6.3/§2.3. A single ask on the composer frame therefore has `stream` ONESHOT and `fused` = the PF arm id; the design's own definition of fused ("renders search, stream and check as one piece") contradicts the "a search only" row. Also, since E-func/E-stmt always report non-empty fused, §2.8's "fused empties as fused rows are re-expressed" cannot happen for them while arms[] stays.

## SLOT-5
HOLDS.
- finder.c:650-656: `if (st) { q.ff.need = CL_N_REQUIRED; set_facts(...); seek_facts(&q); hors_facts(&q, st); if (st->renders_pair) q.facts |= SF_ASKER_PAIR; } else { find_facts(&q); ...` - `hors_facts` (the only setter of SF_HORS_WINDOW / SF_HORS_DENSE, finder.c:629-635; grep shows no other `q->facts |= SF_HORS`) is called only when `st` is set. D-hors's row is `{ "D-hors", FD_FIND, KN_P | KN_E, SF_HORS_WINDOW | SF_HORS_DENSE, ...` (finder.c:257), so on the composer (`st` NULL) it can never hold, independent of any renderable set.
- Design §2.4 (plan_frame.md:~162-172): "D-hors is filtered only by an ABSENT fact ... PAIR and HORS are then filtered by one mechanism." After the change HORS is excluded by the renderable set (no composer search row) AND still by the absent fact; so "one mechanism" overstates (PAIR is the only pick whose absent-fact filter is replaced).

## SEAM-1
HOLDS.
- window.c:1314 (in the plan builder): `w->table[i] = def && def->table_name ? offer_at(m->alt, offs[i], w->set[i]) : 0; if (w->table[i]) w->reads_table = 1;` - the per-position test (C-table vs C-own) depends on whether the define hooks STATE `table_name`.
- memfn.h:1467-1482 `mf_wreply` members: alt, reseed, has_stop, stop, stop_set[32], nplan, plan[], plan_term[], pinned, run_stated, run_member, run_lo, run_len, path[16]. No per-position table/test-kind member (and `mf_wdecide` at window.c:1222-1236 reads no hook: it calls `decide(art, site, 1, d); reply_of(d, out)`).
- plan_frame.md's added members (framed, frame_row, method, stream, fused; §2.3) carry none either (grep of 'table' in the design finds no reply member for it). So two framed asks differing only in `table_name` stated-ness get equal replies yet the plan renders `tbl[...]` vs an inline set test. Whether this matters for Goal 2's claim is a design judgment; the fact is confirmed by code.

## SEAM-2
HOLDS.
- Compile pair, `build/pcrec -p rx --emit-main --pattern 'foo[Xx]bar'` with `-fno-memfn-simd` vs `-fmemfn-simd` (verify/s-fno-memfn-simd.c, verify/s-fmemfn-simd.c): `grep -c 'while (m)'` = 0 vs the count printed above for SIMD; the diff (after splitting on `;`) is only added guarded helpers: `#if defined(__x86_64__) ... static inline size_t rx_mf1_ofsskip__w16(...)` containing `m = _mm_movemask_epi8(...); while (m) { size_t cand = i + (size_t)__builtin_ctz(m); if (((memcpy(&pw, subject + cand, 8), pw) & pk) == pt) return cand; m &= m - 1; } i += 16; continue;` - a mask-driven candidate stream with a trimmed check.
- The reply is the OFF variant's: the design's own non-goal / §2.7 statements (grep lines above) and no field in mf_wreply or the added members carries the layer, so the two compiles' replies cannot differ. Reply-equality is by the design's rule (not run: mf_wdecide needs a harness).
- Note: the design itself states this at plan_frame.md:364 ("The reply is the OFF variant's ... so no reply reader sees vrun's ..."); the finding's addition is only that §6's comparisons name no layer in their FIXED column (not re-checked here).

## SEAM-4
PARTLY. Settled: `fused` is "ofsskip" for BOTH fn-pair and fn-memchr (PREM-7's reading is right; SEAM-4's "`fused` = fn-pair/fn-memchr" is wrong on the value).
- ofsskip.c:910-911: `const arm ofsskip_arm = { "ofsskip", 0, ofsskip_applies, ...` - first member is the arm id (kit.h:433-434 `typedef struct arm { const char *id; /* the form id mf_result reports */`). compose.c:1310 `snprintf(out->form_id, ..., "%s", r->arm->id)` (and :1253 for the emit result). "fn-pair"/"fn-memchr" are only the `fn_ct` contract ROW names (ofsskip.c:418-419 `fn_rows` BODY entries with `&fn_pair_ct` / `&fn_memchr_ct`; ofsskip.c:990/995 `"fn", "fn-pair"`), not what `form_id` reports. So the design's `fused` ("the value `mf_result.form_id` reports", plan_frame.md:122) is "ofsskip" for both.
- Confirmed part of SEAM-4: on the DFA prefilter's E-func ask `method` is "" (design §2.3) and `fused` is the arm id, so the reply is (E-func, "", ONESHOT, "ofsskip") and cannot tell fn-pair from fn-memchr. (design §2.3 `fused` on E-find under B-fn is "the offset-skip function's form id, the same value E-func reports" - also "ofsskip".) PREM-7's last item is the accurate version; the two are duplicates in substance with SEAM-4's value claim wrong.

## SAB-1
HOLDS.
- decider_census.py:57-61: `LIVE = ["kit_walk(", "< best", "tie_takes", "TIE_", "pick_takes("]`, `BYPASS = ["< b.v", "<= b.v", "< b->v", "<= b->v", ".v <", "->v <"]`, `BACKSTOP = LIVE + BYPASS`; check B flags a hit line (`any(p in ln for p in BACKSTOP)`, :226) lying in no listed member. Spellings are pick/argmin shapes.
- Test (python3 -I over the shape list): `if (fd_renderers[i].pick == pick &&` (compose.c:288, the real renderer loop) -> no shape matches (False); a planted `for (...) if (sr_rows[i].pick == pick) return ...` -> False; `if (wf_brows[i].holds(&bx)) break;` (window.c:1851, Table B's walk) -> False; `wf_arows[i].holds(x)` -> False. So a second hand-written renderer-list loop in an unlisted function is invisible to the backstop; the design's sabotage row (D) ("a second renderer list planted in an unlisted function: decider_census.py's backstop is red") would not go red unless the backstop gains a shape (the existing renderer loop is only covered because it is a declared member).

## SAB-5
HOLDS (both facts); the consequence is a check-adequacy judgment that follows from them.
- g2_win_gen.c:998-1007 (path memfn/tests/g2/g2_win_gen.c): counts are taken from the rendered TEXT: `ef_hors += strstr(ft, "_sh[256]") != NULL; ef_walk += strstr(t, "while (") != NULL; ef_libc += strstr(t, "memchr(") != NULL; ef_pair += strstr(t, "_ha < ") != NULL; ef_fn += strstr(ft, "_ofsskip__body(") != NULL` - classification by emitted text, not by the reply.
- memfn/tests/run_g2_win.sh:82 `EFIND_FLOORS="libc:320 walk:103 hors:110 run:115 below:95 report:370 refused:17 pair:316 fn:48 hwin:146"`, with the comments :70-83 ("each floor the measure less ~10%", "pair measures 352 (floor 316)"). 
- Design §5/§Q3 (plan_frame.md ~:586-589): "per-frame-row and per-stream framed asks by G2's own tally, with a floor per row and per produced stream". The existing floors are population counts by text class over one frame family (E-find); a "floor per produced stream" counts across frames, so a wrong `stream` on one frame (e.g. E-generic's floor) is not isolated unless the tally is per (frame, stream). The design does not state the key or the floor size; the finding's "floor of 1 is aggregate" reads the design's "floor of 1" wording (not located verbatim; I did not find a numeric `1` in the lines grepped), so the exact-size part is not verified.

## SAB-6
HOLDS.
- compose.c:1303-1318 `mf_defined`: sets `form_id = r->arm->id`, `handle`, `reads_table`, `includes`, `cls`, and `row = r->fd_row ? r->fd_row : ""` - nothing else.
- On a window-plan site (E-find): compose.c:1071-1087, 1128-1130 `window_route(...&wplan...)`; `rid` stays NULL (`const char *rid = NULL;` and only `select_arm` sets it, which is not called when `wplan` is set); `row = wf_plan_row(wplan)`; `r->arm = row; r->fd_row = rid; r->wplan = wplan`. So for E-find `row` reads "" (no T-FIND row exposed) and `form_id` is the single E-find arm id for B-fn, B-pair, B-memchr, B-walk and B-hors alike (wf_plan_row returns the family's E-find arm, window.c:2830 region). The only per-row difference left is `cls` (libc_free/includes, from wf_plan_class), which is equal for B-fn and B-pair (both libc 1).
- So `mf_defined` carries no E-find `method` (T-FIND row) and no B-fn bit; a G2 check "holds the reply's frame part to `mf_defined`" for `method`/`fused` on E-find has no independent observer there (the trace FDROUTE/MFTRACE is the only one).

## SAB-9
HOLDS.
- arm_fixtures.c:2204-2221 `pur_diff(const mf_wreply *a, const mf_wreply *b)`: a hand-listed chain `if (a->alt != b->alt) return "alt"; ... reseed, has_stop, stop, memcmp(stop_set,32), nplan, plan[]/plan_term[] loop, pinned, run_stated, run_member, run_lo/run_len, strcmp(path)` and `return NULL` - one line per existing member, no sizeof-based or memcmp-of-struct comparison. A new member (framed, frame_row, method, stream, fused) is invisible to it until a line is added (the design §3.0b says the harness gains "pur_diff over the new fields", i.e. by hand).
- window.c:1191-1195 `reply_of`: `memset(out, 0, sizeof *out);` then fills fields; mf_wdecide also `memset(out, 0, sizeof *out)` first (window.c:1224). So a new field that no code writes reads as 0 / "" on every ask, and a hand-listed compare plus a zero-filled reply means an unwritten or unfilled new field passes silently as equal.

## SAB-10
HOLDS.
- plan_frame.md:479 (3.0b's sabotage column) lists (E) `reply_of` writes another walk's frame row; (F) ASK-1 states STMT/ASSIGN; (G) plan face calls `table_name` once; (H) `stream` keyed on `art->nsites`; (I) framed ask walks Table E without the art's denies; (J) `method` filled from the `fused` column. The 3.0a column (:~482, rows A-D, K-N) concerns the renderer/support tables. No row plants a change to how `mf_wcall` is read (UNSTATED treated as NONE; NONE answering a frame part; EMIT not applying DEFINE|USE phases). `grep -n -i call` over the design restricted to plant/sabotage lines finds none naming `call`.
- The behaviours exist in the contract: §2.2 (plan_frame.md:33) "`call` ... UNSTATED (refused), NONE (decision only), DEFINE (as `mf_define`) or EMIT (phase set DEFINE and USE)", and :95 "UNSTATED is refused (-1). There is no presumed value".

## SAB-11
HOLDS.
- memfn.h:1005-1017: mf_hooks has six callbacks: `on_cand`, `member`, `table_name`, `fn_name`, `note`, `note_tag`.
- arm_fixtures.c:2233-2238 `pur_define`: `mf_hooks hd = { .fn_name = h_fn_name, .table_name = h_table_name, .note = h_note, .note_tag = h_note_tag, .u = &fd, .miss = MF_MISS_N };` - four stated; `member` and `on_cand` are NULL.
- Design plan_frame.md:50 (Goal 3 row): "A COUNTING HOOK asserts that a framed ask makes **0** hook callback calls (`fn_name`, `table_name`, `member`, `note`, `note_tag`, `on_cand`)". With the fixture's hooks, `member` and `on_cand` are not stated, so a counting hook cannot count calls to them (a plant that called either would either be skipped as unstated or crash, not read as a count); the counting check covers 4 of the 6 callbacks it names unless the fixture is extended.
VERIFY COMPLETE
