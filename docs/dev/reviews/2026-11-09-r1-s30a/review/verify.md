# verify

## verify
Summary of verdicts (detail per finding below). Plant builds: 6 (S2993/R, B, C, Q as pcrec builds; M and R again as rows_check kit builds), copy restored (cmp) between each.
- SLOTS-4 / EMIT-1: HOLDS by plant (`foo|bar\d`, an E-stmt site, refused rc 1 with E-find's ST-many text; Table E never walked); SLOTS-4's own witness `a[Xx].b --memfn=no-window-search` REFUTED (rc 0, bytes identical); EMIT-1's E-func half not verified. Extra: under S2993 `a[Xx].b` default is a SILENT MOVE (rc 0, falls back to the FUNC form).
- CHECKS-5, CHECKS-6: HOLD (rc 0, silent move E-stmt pf_walk -> E-find B-pair; B and C texts identical).
- CHECKS-1: HOLDS. CHECKS-2: HOLDS (duplicate BEFORE the real row green; after it, red by cell compare). CHECKS-3: HOLDS. CHECKS-4: HOLDS. CHECKS-7: HOLDS (20 failed: 6 named, 13 unnamed, §S). CHECKS-8: HOLDS.
- SLOTS-1, -2/EMIT-2, -3, -5, -6, -9, -10: HOLD. SLOTS-7: PARTLY. SLOTS-8: PARTLY (adding the shapes leaves a stray at window.c:2061; wf_srows needs a member line).
- HOUSE-1, -3, -4: HOLD. HOUSE-2: PARTLY (the ST-many arm at window.c:2251 is unreachable, not a second producer). HOUSE-5: PARTLY (designated initializers bind index to enum; the missing assert guards only a hole).

Setup: copy = `git -C /home/pcrec/projects/pcrec archive 6dc54e383 | tar -x -C verify/tree` + copied build/; plant builds by
verify/build_plant.sh (recompile the changed memfn/src/*.c twice: plain -O2 -g into a copy of build/libpcrec.a, and
-O1 -DMF_TRACE into a copy of bin/lib_subj.a; relink cli/main.c with the Makefile's ALLFLAGS). Probes by verify/probe.sh
(run from the review tree, `-p rx ... -o OUT/t.c --pattern P`). CONTROL (unplanted rebuild p0): `a[Xx].b --memfn=no-window-search`
plain+traced rc 0, C byte-identical to bin/pcrec-subj and bin/pcrec-mftrace-subj (cmp) -> the recipe reproduces SUBJECT.

## SLOTS-4 / EMIT-1 (ST-many refusal raised before Table E walks)
Verdict: HOLDS (mechanism and consequence confirmed by plant on an E-stmt site); SLOTS-4's own concrete witness
(`a[Xx].b --memfn=no-window-search`) is NOT refused (see below), and the E-func half is not shown.
- Code (review tree): memfn/src/window.c:2194-2199 — `if (wf_find_decide(art, d, w, def, 1, fx)) ...; if (fx->brow && !strcmp(fx->brow, WF_STREAM_REFUSAL)) { ... *why = "E-find: Table S answers ST-many for T-FIND's pick ..."; return -1; }`
  precedes window.c:2206 `size_t r = kit_walk(&wf_etable, 0, &in, gphases, 0, &e, &tc, &v);`. wf_find_decide always asks fd_find with frame E_FIND (window.c:2125).
- Plant 1 = S2993 SAB_BEFORE->SAB_AFTER (count 1; window.c:2030 `WF_ST_RESTART | WF_ST_SHIFT`), build p1.
- `foo|bar\d --features all` (a composer E-stmt site): SUBJECT rc 0, `END table=wfE ... chosen=E-stmt`, `FDROUTE row=R7w arm=pf_walk ren=pf_walk frame=E-stmt`.
  PLANTED: plain rc 1, traced rc 1, no output file, zero `END table=wfE` lines (Table E never walked), stderr:
  `pcrec: internal error: the memfn kit refused a site: mf_define: E-find: Table S answers ST-many for T-FIND's pick (two streams or more on the frame), REFUSED until a row with evidence exists (D186) (pattern offset 0)`.
  So a site Table E serves by E-stmt (not E-find) is refused with E-find's ST-many text — the design's refusal of E-find's decision only (§2.4 [rev2.2 R3]) would have kept pf_walk. Byte verdict: DIFFERS (refused). CONFIRMED.
- `(?:(?!a)z|w)` (B-pair, E-find): planted rc 1/1, same message — the intended (R) refusal. `(?:(?i:abs)|(?i:ab)S)` (B-fn): planted rc 1/1, `pcrec: internal error: the memfn kit refuses the start-search site a selection reads (its define would refuse it too)` (no kit reason; matches CHECKS-7).
- SLOTS-4's witness `a[Xx].b --memfn=no-window-search`: SUBJECT and PLANTED both: first ASK rc=-1 (the STMT site: E-find denied, no Table E row), then the FUNC-form site `END table=wfE ... chosen=E-func`; planted plain/traced rc 0, C BYTE-IDENTICAL to SUBJECT. Not refused: SLOTS-4's "concrete site" claim (chosen=E-stmt, refused) is REFUTED as stated (`.../verify/probe.sh .../p1 ax_nws_p1 'a[Xx].b' --memfn=no-window-search`). I could not name an E-func site with a PAIR stop that the plant refuses, so EMIT-1's E-func half is not verified.
- Extra observation (affects S2993's stated detector): `a[Xx].b` default regime under the plant: rc 0 (plain and traced), NOT a compile failure: the STMT site's ASK is refused (`ASK rc=-1`), pcrec falls back to the FUNC form (wfE E-func), and the C equals SUBJECT's `--memfn=no-window-search` output (cmp identical). So "every B-pair site is refused, and pcrec fails the compile" (S2993 header) holds for the corpus witnesses but `a[Xx].b` -p rx is a SILENT MOVE under (R).

## CHECKS-5 (row B is a SILENT MOVE, not a LOUD refusal naming PAIR)
Verdict: HOLDS.
- Design: plan_frame.md:911-913 "(B) ... an (E-stmt, PAIR) search renderer row declared with NO arm: T-FIND picks PAIR on a composer two-member stop, `select_arm`'s refusal ... fires, and pcrec's `pcrec_ctx_fail` refuses the compile ... the check asserts the refusal names row PAIR".
- Plant B (fresh re-extract of memfn/src, verified `diff -r` empty first): window.c enum `RB_ST_WALK_B, RB_ST_PAIR, RB_N` and row `[RB_ST_PAIR] = { { E_STMT, REN_PICK(FF_PAIR), "pf_pair", NULL }, 0, "", NULL, NULL, NULL, NULL, NULL, "PLANT B: no arm" }`; build pB (compiles).
- `foo|bar\d -p rx --features all`: SUBJECT rc 0, `END table=wfE ... chosen=E-stmt`, `FDROUTE row=R7w arm=pf_walk ren=pf_walk frame=E-stmt`.
  PLANTED: plain rc 0, traced rc 0, `END table=wfE ... chosen=E-find`, `FDROUTE row=PAIR arm=E-find ren=B-pair frame=E-find`; C DIFFERS from SUBJECT (`cmp`: differ byte 8632, line 165). No refusal text on stderr. So (B) is a silent move to E-find B-pair; select_arm's refusal is never reached.

## CHECKS-6 (row C is likewise a SILENT MOVE)
Verdict: HOLDS.
- Design: plan_frame.md:922-924 "(C) the renderability check removed from `fd_holds`: the same refusal as (B), asserted by the same invariant's message (rc != 0 AND it names PAIR)".
- Plant C (fresh re-extract): finder.c:510 `    if (r->slot == FD_FIND && !wf_renders(q->frame, fd_pick_of(r, q), q->site)) return 0;` replaced by `    /* PLANT C: the gate removed */`; build pC.
- `foo|bar\d -p rx --features all`: PLANTED plain rc 0, traced rc 0, `chosen=E-find`, `FDROUTE row=PAIR arm=E-find ren=B-pair frame=E-find`; C DIFFERS from SUBJECT (byte 8632, line 165) and is byte-IDENTICAL to plant B's output. rc 0, not "rc != 0 AND names PAIR".

## CHECKS-1 (S2983, S2984, S2988 hosted nowhere)
Verdict: HOLDS.
- Command: `for id in S2982..S2993; git -C /home/pcrec/projects/pcrec grep -l "$id" 6dc54e383 -- . ':!docs/dev/lanes/s30a*' ':!memfn/docs/lanes/s30a*' ':!*s30afix*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!docs/dev/full_suite_ledger.md'`
- Output: S2983 (none), S2984 (none), S2988 (none). Hosts for the others: S2982 tests/mech/sabotages/S2982_ren_search_epair_dropped.sh; S2985 tests/memfn/decider_census.py; S2986/S2987/S2989/S2991 memfn/tests/run_g2_win.sh (+ memfn/tests/CLAUDE.md); S2990 tests/mech/sabotages/S2990_renderable_gate_unscoped.sh; S2992 tests/mech/sabotages/S2992_wf_libc_union_two_pieces.sh; S2993 tests/mech/sabotages/S2993_support_pair_two_streams.sh.
- The id-to-row mapping is the design's: plan_frame.md:872 "expected as S2982-S2993 for 3.0a's 12 rows (A-D, K-R)", which makes B=S2983, C=S2984, M=S2988; it is consistent with every hosted id (D=S2985 in decider_census.py:35, O=S2990, Q=S2992, R=S2993). rows_check.py has no in-script plant for B/C/M (`grep -n -i 'plant\|sabotage'` hits only the census-judge plants :422-483). plan_frame.md:1068 lists (B), (C), (M) among commit 2's rows.

## CHECKS-2 (§S duplicate pin row green)
Verdict: HOLDS (with a nuance: only a duplicate placed BEFORE the real row is green).
- Code: tests/memfn/rows_check.py:826 `pmap = {c[0]: c for c in pin}` (last row per key wins; no count of lines read) and :825 `kmap = {c[0]: c[1:4] for c in kit if len(c) == 4}`.
- Harness: verify/rows.sh = run_rows.sh's env (ROWS_FLOOR=31 KIT_SRC_FLOOR=15 FIXTURE_FLOOR=34 ROW_MAP_PIN CLASS_CASE_FLOOR=15) + `python3 -I tree/tests/memfn/rows_check.py --root verify/tree --cc gcc --tmp DIR` (builds its own traced kit; nothing in either repo touched).
- Clean copy: exit=0, `support pin: 6 rows, 6 in the kit's table, 1 ruling ledger(s) read`, `checks passed: 243`, `checks failed: 0`.
- Plant: `LIBC	yes	yes	no	DERIVED	wrong duplicate` inserted at line 14, ahead of the real LIBC row -> exit=0, `support pin: 6 rows` (7 data lines), `checks passed: 243`, `checks failed: 0`. GREEN.
- Same row appended AFTER the real LIBC row -> exit=1, `FAIL: support row LIBC: the pin says RESTART/MASK/SHIFT yes/yes/no, the kit's table yes/no/no` — red by the cell compare, not as a duplicate (so a duplicate with correct cells after, or any wrong one before, passes). Pin restored (cmp equal to review tree).

## CHECKS-3 (self-cited ledger path green)
Verdict: HOLDS.
- Code: rows_check.py:839-852 opens `os.path.join(root, key)` for whatever PATH the RULING basis names; no allowlist.
- Plant: both RULING rows' `@ memfn/docs/responses.md 067aca4df` -> `@ tests/memfn/stream_support.tsv 067aca4df` (`sed -i`). rows.sh -> exit=0, `support pin: 6 rows, 6 in the kit's table, 1 ruling ledger(s) read`, `checks passed: 243`, `checks failed: 0`. GREEN: the pin is accepted as its own source. Pin restored.

## CHECKS-4 (census backstop misses a copy of ren_find and a pointer-alias twin)
Verdict: HOLDS.
- Code: tests/memfn/decider_census.py:65-66 `LIVE = [..., "ren_find(", "ren_search[", "ren_stream[", "ren_check[", "ren_skel[", "ren_fused["]`; window.c:1800-1808 ren_find walks `const ren_key *k = (const void *)((const char *)rows + i * size)`; `grep -n 'ren_search\[' memfn/src/*.c` -> only window.c:1908 (the definition). The in-script S2985 plant (decider_census.py:339-343) spells `ren_search[i].k.frame`, a spelling no reader uses; its own comment (:337-338) concedes "a copy of it would hold no shape".
- Census control on clean copy: `python3 -I tree/tests/memfn/decider_census.py --root verify/tree` -> `renderer-list plant (S2985): 2 stray hit(s)`, `checks passed: 83`, `checks failed: 0`.
- Plant b1 (appended to the copy's window.c; `gcc -std=gnu11 -fsyntax-only` ok): `census_find2`, a byte copy of ren_find's loop, + `census_twin_b1(pick) { return census_find2(REN_ROWS(ren_search), E_FIND, REN_PICK(pick), NULL); }` -> `decider_census.py --root verify/tree --no-plants`: exit=0, `backstop hits: 50 (expected 50), outside a member: 0`, `checks passed: 75`, `checks failed: 0`. GREEN.
- Plant b2: `const ren_search_row *t = ren_search; for (i < RB_N) if (t[i].k.frame == f && (t[i].k.keys & REN_PICK(pick))) return &t[i];` -> exit=0, hits 50, outside 0, failed 0. GREEN. (window.c restored, cmp equal.)
- Note against design (D) (plan_frame.md:925-928): "a COPY of the one accessor's loop (holding the search renderer table's name)": b1 holds `ren_search` (in `REN_ROWS(ren_search)`) and is not caught.

## CHECKS-7 (under R only 6 of 19 refusals named)
Verdict: HOLDS (exact counts reproduced).
- rows_check with the S2993-planted kit (rows_check builds it) AND the planted p1 pcrec temporarily copied over the copy's build/pcrec (restored after, cmp equal): exit=1, `checks passed: 223`, `checks failed: 20`; 6 lines `REFUSED naming Table S's ST-many refusal`, 13 lines `does not compile` (e.g. `renderer PAIR/B-fn witness: does not compile (traced rc 1, plain rc 1): pcrec: internal error: the memfn kit refuses the start-search site a selection reads (its define would refuse it too)`; also runcmp/words, runcmp/bytes, fn/fn-pair, fn/vrun-w16/w32, fd/P4 witness+control), plus §S `FAIL: support row PAIR: the pin says RESTART/MASK/SHIFT yes/no/no, the kit's table yes/no/yes`.
- Code: rows_check.py:305 `msg = rp.stderr.decode(...)` reads build/pcrec only; :306 regex.
- Side evidence for SLOTS-4: the same run's `FAIL: renderer R7w/pf_walk witness: REFUSED naming Table S's ST-many refusal ... mf_define: E-fin...` — the E-stmt pf_walk witness refused by E-find's refusal.

## CHECKS-8 (Q hosted UNDETECTED; M's only detector is §S, outside mech)
Verdict: HOLDS.
- S2992 header: `SAB_EXPECT=UNDETECTED`, `SAB_EXPECT_REASON='no reader sees libc_free on a window site ...'`. Design plan_frame.md:948-951 "(Q) ... `wf_plan_class` reports `libc_free` 1. emit_sweep is red on that arm, and the reply-class pin ... moves."
- Plant Q (S2992 BEFORE->AFTER, count 1), build pQ: `abcdef --memfn=no-fd-d1` (default and `-e utf8`): plain rc 0 / traced rc 0 both sides; t.c and t.h BYTE-IDENTICAL to SUBJECT (cmp); FDROUTE `row=D1w ... ren=B-walk frame=E-find` both; only the trace's ASK moves: SUBJECT `MFTRACE ASK art=1 rc=0 exists=1 libc_free=0 includes=1`, PLANTED `... libc_free=1 includes=0`; artifact still has `#include <string.h>` (t.c:18) and `#define RX_MEMFN_LIBC "none"`. So emit_sweep (bytes) cannot be red; the design's (Q) detector is falsified as S2992 says.
- Plant M (`{ "LIBC", FF_LIBC, WF_ST_RESTART | WF_ST_MASK, ...}`) via rows.sh: exit=1, `checks passed: 242`, `checks failed: 1`, sole FAIL `support row LIBC: the pin says RESTART/MASK/SHIFT yes/no/no, the kit's table yes/yes/no`; 0 "differs" lines (no artifact moved).
- `grep -n 'rows_check\|run_rows\|memfnrows' tests/mech/*.sh tests/mech/*.py` -> no rows arm (only an unrelated `cand_rows_check.py` comment at run_sabotage_matrix.sh:680).

## SLOTS-1 (E-stmt search rows' `libc` 0 vs the arms' `libc` 1)
Verdict: HOLDS (no byte moves; a wrong, unread cell).
- window.c:1928-1933 `[RB_ST_MEMCHR] = { { E_STMT, REN_PICK(FF_LIBC), "pf_memchr", stmt_end0_holds }, 0, ...`, `[RB_ST_MEMCHR_B] = { ..., 0, ...`, `[RB_ST_BACK] = { { E_STMT, REN_PICK(FF_LIBC_BACK), "pf_memchr_back", NULL }, 0, ...`; the column's comment window.c:1897 `uint8_t libc; /* its text calls memchr */`.
- pffind.c:547-550 `const arm pf_memchr_arm = { "pf_memchr", 1, ..., 0, MF_INC_STRING_H, 1, ARM_TESTS_EVERY, };` (the `libc` field, kit.h:457 `uint8_t libc;`, is the 1 after MF_INC_STRING_H); same 1 at :553-554 (bounded) and :563-564 (back).
- Only reader of the search row's libc: window.c:2166 `w->libc = (uint8_t)(w->srch->libc || ...)` (E-find path); compose.c:364 `out->libc_free = !a->libc;` reads the ARM's.

## SLOTS-2 / EMIT-2 (renderable set is not the one function the composition reads; two predicate context types)
Verdict: HOLDS (latent: every E-find search row's predicate is NULL today).
- Gate: window.c:2088-2092 `int wf_renders(wf_frame_row f, fd_form pick, const mf_site *s) { ... if (!ren_find(REN_ROWS(ren_search), f, REN_PICK(pick), s)) return 0;` (x = `mf_site *`), called from finder.c:510 and :688.
- Composition: window.c:2132-2134 `wf_bx bx = { d, w, def, fx->pick, fx->fn }; fx->fused = ren_find(REN_ROWS(ren_fused), E_FIND, REN_PICK(fx->pick), &bx); if (!fx->fused) fx->srch = ren_find(REN_ROWS(ren_search), E_FIND, REN_PICK(fx->pick), &bx);` (x = `wf_bx *`); wf_stmt_arm window.c:2098 passes `s`. ren_find calls `k->holds(x)` (window.c:1805) with no type tie.
- E-find rows RB_PAIR/RB_MEMCHR/RB_WALK/RB_HORS all key `{ E_FIND, ..., "B-...", NULL }` (window.c:1910-1925): NULL predicate, so no disagreement today. E-stmt rows' predicates (stmt_end0/1_holds, window.c:1893-1894) cast x to `const mf_site *` — consistent with both their callers. Not exercised by a plant (would need a new predicate).

## SLOTS-3 (B-fn's pick stated three times)
Verdict: HOLDS.
- window.c:2005 `[RF_FN] = { { E_FIND, REN_PICK(FF_PAIR), "B-fn", b_fn_holds }, FF_PAIR, WF_ST_RESTART, 1,` (key + declared `search`); window.c:1851 `if (b->pick != FF_PAIR || !legacy_ok(...) || eb) return 0;` (predicate re-test). window.c:2236 `fd_form search = r != E_FIND ? WF_NO_SEARCH : fu ? fu->search : fx->pick;` feeds Table S the declared copy, while the lookup (window.c:2133) matches the key. `grep -n 'fu->search\|\.search\b\|->search\b' memfn/src/*.c` -> window.c:2236 only; no self-check ties key to `search`.

## SLOTS-4
See the SLOTS-4 / EMIT-1 section above: HOLDS by plant on `foo|bar\d` (E-stmt site refused, rc 1); its stated witness `a[Xx].b --memfn=no-window-search` REFUTED (rc 0, bytes identical under the plant).

## SLOTS-5 (FUNC floor's loop open-coded beside the skeleton table)
Verdict: HOLDS.
- window.c:1874-1878 `[RK_GENERIC] = { { E_GENERIC, REN_FRAME, "E-generic", NULL }, wf_floor_expr, "text: open; cand; for (; BOUND; NEXT) ..." }` — one skeleton spelling.
- window.c:2765-2796 wf_floor_define (MF_FORM_FUNC only) writes `kb_printf(&f, "static inline size_t %s(", fn);` ... `kb_printf(&f, ")\n{\n    for (size_t %s = %s; %s; ", rc.C, rc.LO, cond.p); rc.w->strm->next(&rc, &f); kb_printf(&f, ")\n        if %s return %s;\n    return %s;\n}\n\n", ...)` reading `rc.w->chk->test` and `rc.w->strm->next` but no `skel`; wf_floor_use's non-FUNC branch uses `rc.w->skel->expr` (window.c:2810).

## SLOTS-6 (FDROUTE's E-stmt `frame=` literal; `ren=` the arm's contract row)
Verdict: HOLDS.
- compose.c:1128-1132 `fprintf(stderr, "MFTRACE FDROUTE ... row=%s arm=%s ren=%s frame=%s\n", ..., frow, row->ct->row, rid ? row->ct->row : wf_plan_bren(wplan), rid ? "E-stmt" : wf_plan_frame(wplan));`
- wf_stmt_arm returns only `r->arm` (window.c:2098-2100), so the E-stmt row's `k.id` ("pf_memchr", "pf_memchr_bounded", ..., window.c:1928-1937) is read by nothing; `grep` of window.c finds no reader of an E-stmt row's id. Trace (bin/pcrec-mftrace-subj, `foo|bar\d --features all`): `MFTRACE FDROUTE art=1 site=1 row=R7w arm=pf_walk ren=pf_walk frame=E-stmt`.

## SLOTS-7 (the support pin's "owner's text" attribution)
Verdict: PARTLY.
- Holds: the quoted sentence is not in Frank's quoted words. D190 (`git -C /home/pcrec/projects/pcrec show bf9e313d6:docs/dev/decisions.md | sed -n 10097,10112p`): `- Frank's words: "Candidate search and candidate validation are two different primitive pieces that are composed." Asked "Adopt search, stream, check as composed pieces?" he answered "Yes"` and, as a separate unquoted bullet, `- libc memchr supplies only one-shot. vrun becomes one composition; ...`; the ledger notice (COMMON quote) likewise has the libc line unquoted, a sibling of "Kit reading:". The pin and code call it the owner's: stream_support.tsv:7 "so the expectation is the owner's text", rows_check.py:115 "so its expectation is the owner's text", window.c:2017-2018 "the LIBC rows' pin cells are the owner's ruling's text". rows_check §S checks only a substring in the named file (rows_check.py:853-856).
- Does not fully hold: D190 files the libc line INSIDE the "**Decision (Frank, directly to the kit ...)**" block, among the statements Frank answered "Yes" to, so "RULING (D190)" is a fair label; "the owner's text" (his words) is the overclaim. Cell content held: LIBC/LIBC_BACK = RESTART yes, MASK no, SHIFT no (stream_support.tsv:14-15; window.c:2022-2026) matches "only one-shot".

## SLOTS-8 (census backstop omits the support table and Table S)
Verdict: PARTLY (gap holds; the claimed "no stray" fix is REFUTED).
- decider_census.py:65-66 LIVE lacks `wf_support[` / `wf_srows[`; their readers window.c:2075, :2080, :2250 hold no shape.
- Probe (copy's decider_census.py LIVE + `"wf_support[", "wf_srows["`, then restored, cmp equal): `python3 -I tree/tests/memfn/decider_census.py --root verify/tree --no-plants` -> `backstop hits: 55 (expected 50), outside a member: 1`, `FAIL: a decider shape outside every census member: window.c:2061: } wf_srows[] = {`. The +5 hits hold, but wf_srows (the Table S rows' definition) is not a census member (decider_census.tsv:73-75 list wf_support, table_s, wf_renders; wf_plan_site at :66), so the fix also needs a wf_srows member line (MEMBER_COUNT 61 -> 62), not just two shapes.

## SLOTS-9 (+ HOUSE-3 key-bit part): REN_FRAME == REN_PICK(FF_UNSTATED) == WF_ST_RESTART
Verdict: HOLDS (latent).
- window.c:1792-1793 `#define REN_FRAME 1u`, `#define REN_PICK(f) (1u << (f))`; kit.h:539 `typedef enum { FF_UNSTATED = 0, FF_NONE, ...`; kit.h:564 `enum { WF_ST_RESTART = 1u << 0, ...}`; kit.h:567 `#define WF_NO_SEARCH FF_UNSTATED`.
- finder.c:653 `*pick = FF_UNSTATED;` on entry, and the ?stream / ?need refusals return with it (finder.c:688-690, :678); compose.c:289 `const arm *ra = rid ? wf_stmt_arm(s, pick) : NULL;` then calls `ren_find(REN_ROWS(ren_search), E_STMT, REN_PICK(FF_UNSTATED)=1u, s)`. No ren_search/ren_fused row keys bit 0 today (window.c:1910-1937, :2005), so NULL; a REN_FRAME-keyed search/fused row would match. Support "floor" row is keyed WF_NO_SEARCH = FF_UNSTATED (window.c:2035), so table_s(FF_UNSTATED, ...) also answers the floor's row for a refusal's pick.

## SLOTS-10 (declared renderer cells with no reader)
Verdict: HOLDS.
- `ren_find(REN_ROWS(ren_check), ...)` runs only at window.c:2242 inside `if (sr == ST_ONE && !fu)` after `if (r != E_FIND && r != E_GENERIC) return 0;` (:2230), so `[RC_CALLER]` (window.c:1984) is never looked up; `libc_runs` is read only at window.c:2166 (E-find), so RC_FLOOR's 0 is unread; the E-stmt search rows' libc/path/prepare/head/k.id are unread (SLOTS-1, SLOTS-6). RS_CALLER (window.c:1961, `next` NULL) is reached only as a membership bit by table_s's `ren_find(REN_ROWS(ren_stream), f, b, NULL)` loop (window.c:2077-2078).

## HOUSE-1 (wf_renders 0/1/2 magic codes; "?stream" sentinel; double evaluation)
Verdict: HOLDS (maintenance; no byte effect).
- window.c:2092 `return r == ST_ONE ? 1 : r == ST_MANY ? 2 : 0;` re-encodes `enum { ST_ONE, ST_NONE, ST_MANY, ST_N };` (window.c:2057). finder.c:510 reads it as a boolean (`!wf_renders(...)`, so 2 passes the gate), finder.c:688 `if (wf_renders(frame, d.pick, s) == 2) { *row = WF_STREAM_REFUSAL;`.
- Sentinel kit.h:554 `#define WF_STREAM_REFUSAL "?stream"`, written finder.c:689, tested by strcmp at window.c:2195 and compose.c:1076.
- Double evaluation: wf_renders runs per FIND row inside fd_holds (finder.c:510) and again for the terminal pick (finder.c:688). (kit.h's doc is at :547-553, not :545-548 as cited; :545 is the wf_frame_row enum.)

## HOUSE-2 (ST-many text spelled three times; two alloc+snprintf copies; dead guard)
Verdict: PARTLY.
- Holds: three phrasings — window.c:2196-2197 "E-find: Table S answers ST-many for T-FIND's pick (two streams or more on the frame), REFUSED until a row with evidence exists (D186)", window.c:2249-2252 "%s: Table S answers %s for its search: ... two streams or more, REFUSED until a row with evidence exists (D186)", compose.c:1077 " (Table S's ST-many refusal of the finder's pick)". Two `art->a->alloc(art->a->u, WF_WHY_MAX)` + snprintf blocks: window.c:2212-2223 and :2245-2257.
- Dead guard HOLDS: table_s (window.c:2080) `while (r < ST_N && !wf_srows[r].holds(popcount)) r++;` over st_one (==1), st_none (==0), st_many (>=2) — a partition of unsigned popcount, so r < ST_N always and `sr < ST_N ? wf_srows[sr].row : "no row"` (window.c:2250) never takes "no row".
- REFUTED part: "the second (2249) is reachable for the same condition via table_s on the fused/floor path". By the code it is not: fused path `fs = fu->stream` (RF_FN declares the single bit WF_ST_RESTART, window.c:2005) and the frame-stream loop is skipped (`!fu &&`, window.c:2077), so popcount <= 1; floor path (E_GENERIC) has one stream row (RS_GENERIC_RESTART, window.c:1956), popcount <= 1; non-fused E-find computes table_s(fx->pick, E_FIND, NULL) — the same call wf_renders made inside fd_find (finder.c:688), which already returned ?stream and was refused at window.c:2195. So the ST_MANY arm at :2251 is unreachable today (only ST-none reaches that branch): one live producer of the ST-many text in window.c, not two. Not run (reasoning from the cited lines).

## HOUSE-3 (b_fn_holds writes inside a predicate)
Verdict: HOLDS (pre-existing side effect, now behind the shared accessor).
- window.c:1852 `translate(b->d, b->w, 0, b->fn);` inside `static int b_fn_holds(const void *x)` (window.c:1847), called through ren_find's `k->holds(x)` (window.c:1805), whose header (window.c:1796-1799) says only "whose predicate holds over `x`". Key-bit part: see SLOTS-9 (HOLDS).

## HOUSE-4 (history narration and retired names in code)
Verdict: HOLDS.
- Quoted: finder.c:39 "3.0a, the asker fact's successor"; finder.c:625 "(fd_holds; until plan_frame.md 3.0a, the asker fact)"; kit.h:587 "renderable set, wf_renders, replaced it.)"; compose.c:287 "plan_frame.md 3.0a this file's fd_renderers)"; window.c:1752 "One prepare until plan_frame.md 3.0a (Table"; window.c:1889 "since 3.0a's commit 2; `fd_renderers` until then)"; window.c:1891 "(D2's RUN pick retired with D2: ..." — and `git diff 73075a9d1 6dc54e383 -- memfn/src/compose.c` shows that sentence as a REMOVED compose.c line (`- * and the composer refuses it. (D2's RUN pick retired with D2: a RUN span 0`), i.e. moved, not removed; window.c:3167-3168 "Since span_pick 1e D-hors is that row too (its FDROUTE record is new; no byte moves)". Names `brow`/`bren`/`wf_plan_bren`/`wf_bx` and ids "B-pair"/"B-fn"/... persist after the Table B split (window.c:1910-1925, :2005). Comment-only; no byte effect.

## HOUSE-5 (Table E index cast without a _Static_assert)
Verdict: PARTLY.
- Holds: `(wf_frame_row)r` casts of the kit_walk index (window.c:2238-2242: `table_s(search, (wf_frame_row)r, fu, &st)`, `ren_find(REN_ROWS(ren_skel), (wf_frame_row)r, ...)`); Table E has `#define WF_NEROWS (sizeof wf_erows / sizeof wf_erows[0])` (window.c:1632) and no _Static_assert, while the five renderer tables and wf_srows each have one.
- REFUTED part: "inserting a Table E row before E_FIND would silently misdirect every renderer lookup". wf_erows is DESIGNATED by the enum (window.c:1627-1630 `[E_FUNC] = ..., [E_STMT] = ..., [E_FIND] = ..., [E_GENERIC] = ...`; kit.h:545 `typedef enum { E_FUNC, E_STMT, E_FIND, E_GENERIC } wf_frame_row;`), so a new row needs a new enumerator and index == enumerator by construction; the residual risk an assert would close is an enumerator with NO row (a zero-filled hole, NULL `holds` called by kit_walk), or a row index beyond the enum. The loop-condition style point (`!fu && b <= WF_ST_SHIFT`, window.c:2077) holds as read.

VERIFY COMPLETE
