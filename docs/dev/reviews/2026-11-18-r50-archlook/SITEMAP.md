# CRITIC SITEMAP: archlook (2026-11-18, ARCHITECTURE mode)

## Findings

### My list (written before reading the note's map). T=57fcb57; every row found by git grep at T.
Greps: G1 'A_LOOK\b|A_CTX\b|CTXFN_NEXT|CTXFN_PREV' (src memfn/include memfn/src);
 G2 'rn_members|pos_set|ctx_span|req_run|REQ_RUN'; G3 'omin|mf_wspan|npspan|pspans|MF_WSPAN|MF_WREACH';
 G4 'whole_maxoff|req_landmark_maxoff|whole_len'; G5 'lookaround|lookbehind|lookahead' (docs/spec, tests).
S1 src/facts/req.c:1034-1110 T3 zero rows (rb_zero_look_pos, rb_zero_rows) - the run's lookaround site (G1) - ROW
S2 src/facts/req.c:1190-1204 case A_CTX/A_LOOK in the walk dispatcher (G1) - AS-IS/ROW
S3 src/facts/desc.c / desc.h (pcrec_pd_zero/unit/cat/pos) - the position-set description L1 reads for the body (grep 'desc.c') - SHARED/ACCESSOR
S4 src/facts/facts_derive.h:121-140 ReqWalkParams + src/facts/facts.c:210-235 fill (pos_set) (G2) - WIDEN (item/back-bound param)
S5 src/facts/facts.h:36-76 ReqRun {pos,whole_len,whole_maxoff}: no negative/back offset field; invariant F "q in [p,p+whole_maxoff]" (G4) - WIDEN
S6 src/facts/walk_arms.def (zero arm lever) + facts.h:340 restored arms - ROW (L1 lever)
S7 src/facts/facts.def:54-59 PF_FACT REQ_WHOLE_RUN/RUN_PIN/LANDMARK_MAXOFF (deny masks, 'src/facts/req.c') - fact registry
S8 src/facts/kset.c:302 pcrec_run_pin (reads run, exact stretch, offset o) (G2) - reader
S9 src/facts/req.c:1235-1300 pcrec_req_walk / pcrec_req_pick (reads run, whole_len) - reader
S10 src/gen/emit_dfa.c:1182,1455-1480 (run -> mf_wspan, pcrec_memfn_wspan(sp,0,..), p[i].omin = 0) (G3) - the span facts handed to the kit: start is 0, omin 0 hardwired -> WIDEN (negative start)
S11 src/gen/emit_dfa.c:1511,1536-1600,8726-8813,9064-9220,11341 req_run_* / cls->run readers of whole_maxoff/ver_lo (G4) - readers
S12 src/gen/emit_dfa.c:6891-6956,7443,7587 run_pin readers (us_run_pin kind gate) - readers
S13 src/gen/known.c:331-351,588-599 (MF_WSPAN_POS/MF_WREACH bounds; walt_spans) (G3) - known-site ledger consumers of spans
S14 src/gen/memfn_sites.c:531-600 pcrec_memfn_walt_spans/wspan/wpos_* and shape-bound check w->start < -MF_MAX_BACK (G3) - ACCESSOR (negative start already accepted)
S15 memfn/include/memfn.h:662-667,764-785 (MF_MAX_BACK, MF_WREACH, mf_wspan.start, omin) - kit contract: negative start/omin already declared
S16 memfn/src/window.c / presence.c (kit_run_decide, run part omin) - kit side, consumes (not edited)
S17 src/core/limits.def:408-410 PCREC_MAX_REQ_RUN_SCAN/MIN_REQ_RUN_BITS/MAX_REQ_RUN_POS_SET (+ a new back-bound limits row, 5.5 policy)
S18 src/core/axes.def:220-224 PCREC_NO_REQ_RUN / _FOLD denies; src/dump/axes_dump.c:758-774; docs/spec/tuning.md 2.28-2.39 (deny/lever)
S19 src/ir/nfa.c:658,805 A_LOOK -> N_EPS erased (NFA_ERASED_LOOK), src/core/kindrow.def:63-72 rows; src/opt/atomic.c:124-160 pcrec_has_lookaround; src/ir/CLAUDE.md:21 - engines see erased lookaround; run readers on DFA path
S20 src/gen/emit_vm.c:9536 case A_LOOK and :10675 LOOKAROUND (pcrec_has_lookaround) ceiling - the VM half; run pre-check reads in emit_vm.c (G4 files list)
S21 src/facts/endwin.c:174,326 / startanch.c:162 / startset.c:141 / widths.c:123,250 (A_LOOK arms) - sibling fact walks over lookaround (they treat body as not read)
S22 src/parse/mod_lookaround.c, ctxnode.c (a one-char lookaround becomes A_CTX; the two lowerings) - producers of the two lowerings
S23 src/core/ctxfn.def NEXT/PREV rows + docs/design/ctx_span.md - the per-offset set producer's truth
S24 src/gen/stamp_kinds.c + src/facts/facts.c:682-700,835-926 (REQ_RUN stamp text '@off' spelling) - observable (signed offset in stamp)
S25 docs/spec/facts_listing.md 4.1.2p1,p8; docs/spec/match_api.md 6.3.7p6 (REQ_RUN stamp, line 2437-2450), 2153 run-pinned; docs/spec/tuning.md 2.28p4-5; docs/spec/findings.md §4 (its readers table) (G5, req) - SPEC hunks
S26 tests: tests/base/k66_precheck_whole_run.rxt; tests/litscan/d27/partd_*.rxt; tests/codegen/run_facts_checks.sh, run_prechecks.sh, reqcube_check.py; tests/litscan/gen_reqcube.py; tests/mech/sabotages/S1887_run_head_reads_through_lookbehind.sh, S1905-S1907; tests/axes/run_axes.sh; tests/findings/witness - witness homes
S27 tests/mech/run_sabotage_matrix.sh (sabotage registry)

### My list (written before reading the note's map)
(see list above; copy at R0/sitemap/my_sitemap.md)

### Step 2 additions (vocabulary grep; new vs my list)
S28 src/gen/emit_dfa.c handoff/landmark: req_handoff_k (:336,:1087,:1640), req_landmark_k (:321,:1582,:8989,:9157), emit_req_handoff_rest (:1083,:1537,:1679), emit_req_landmark_move (:346,:7904-7970), req_handoff_entry_applies (:9082,:10725), req_landmark_admits (:7882,:8541,:9233), pcrec_landmark_margin (internal.h:9243, emit_dfa.c:9272) - all read whole_maxoff as nonnegative K from the attempt start
S29 pcrec_emit_start_zero / PCREC_START0_ROUNDUP (internal.h:7662-7678; emit_dfa.c:682,906-941; enc_utf8.c:677) - a scan beginning before the start offset reads these
S30 Ctx.lb_max / pcrec_lb_raise (internal.h:4115,4465; parse/mod_assertions.c:89,106) - lookbehind width bound the back-step needs

### Step 3: diff against the note's map (rows 1-28) and Commands C1-C32

Findings (one per block).

### SITEMAP-1 CONFIRMED, severity design, effort S, blast radius: the pin's readers in emit_dfa.c; note site 19, seams row 2
The note's site 19 lists only `pcrec_run_pin` (kset.c:302-339) as the run pin's reader and classes it ACCESSOR.
My grep `git grep -n -E 'us_run_pin|pf_window_of|ofs_test_of|ofs_test_verifies_run|pf_run_applies_common|walk_proves' $T -- src`
prints these emit_dfa.c readers at T: walk_proves :6872, pf_window_of :6880 (reads `pin.o - pin.at`, `walk_proves(wk, w+lo-1, r, lo-1)`,
`pcrec_run_byte(r, pin.at+i)`), us_run_pin :7428, pf_run_applies_common :7438, ofs_test_of :7469, ofs_test_verifies_run :7582.
They align run position i with k-set walk offset `w + i` (a run position equals a consumed offset). With a guard prefix or suffix
in the run, that alignment is the reader's own assumption. The design's own table names them (span_arms §8.1 A5: "us_run_pin, ofs_test_of,
ofs_test_verifies_run, pf_run_applies_common ... SELF-VERIFYING"). `grep -n -E 'us_run_pin|pf_window_of|ofs_test|walk_proves|pf_run_applies_common'`
over the note prints 0 lines. Class I would give: ACCESSOR readers of RM-4's consumed-extent accessor (one row, six functions), not omitted.
The same grep family shows other emit_dfa.c run readers that the note omits and that A4-A6/A11 list: req_run-related req_note_run :1179, req_parts_in_whole :9018,
req_use_whole :9144, req_use_row :9129, req_none_applies :8745, req_byte_dominated_by :8722, req_set_leads_applies :8811 (all grep 0 in the note). AS-IS rows would do; the pin group needs a non-AS-IS row.

### SITEMAP-2 CONFIRMED, severity maintenance (witness reach), effort S, blast radius: tests/mech/sabotages + corpus pins; note C31/C32, RM-1 "Binding checks"
The note finds binding checks only by function-name greps (C31, C32). Checks that pin lookaround run values and that L1/L2/L3 move are not found:
- S1887_run_head_reads_through_lookbehind.sh: SAB_REACH_EXPECT 'run=none' for `(?<=abc)x`; anchor `case A_LOOK` in src/facts/req.c; premise "the run CUTS at a lookbehind" (SAB_DESC). C31b (rb_zero|RB_ZERO|rr_cat|RbRuns|rr_alt|rb_rep, 20 files) does not list it (checked: 20 files, S1887 absent); C32 matches tests/ only by those names.
- S1925_lookaround_body_walked_consumed.sh: SAB_REACH greps `RX_REQ_RUN "78797a616263@[0-9]"` for `xyz(?<=yz)abc` as the PLANTED output. span_arms §5.6 predicts L1 makes the real value `xyzabc`: the plant then equals the unplanted tree ([MECH-REACH]: the witness reaches nothing).
- S1700, S3076 (`b*xx(?=q)`, RX_REQ_HANDOFF "unbounded"), S469 (`(?:\Gab|x)(cat)(?=dog)`, HANDOFF "1"): REACH lines hold a positive lookahead plus a run/handoff stamp (L2 movers; SUSPECTED, confirm by §5.6 rule).
- tests/codegen/run_prechecks.sh:363 `abc(?=x)$%%4`, :364, :580 `(?<=xyz)ab%%98%6162`, :1824 (lookahead hybrid); tests/codegen/run_facts_checks.sh:713 `xyz(?<=yz)ab\Bcd`, :980-981, :460; tests/litscan/spanarms.rxt:301-353 (`(?<=foo)bar`, `xyz(?<=yz)abc`).
Repro: `git grep -n -E '^SAB_REACH=.*(\(\?<=|\(\?=).*(REQ_RUN|req_whole_run|HANDOFF)' $T -- tests/mech/sabotages` -> 5 files (S1700, S1887, S1925, S3076, S469); the note names none of them (grep over the note for S1887|S1925|S3076|S469|run_prechecks.sh:|spanarms rows: only run_prechecks.sh as a RM-4 check and spanarms.rxt in RM-1).

### SITEMAP-3 CONFIRMED, severity doc, effort S: class of site 16 contradicts "What is deleted"
Site 16 (emit_dfa.c:1448-1482, `p[i].omin = 0` at :1479) is classed AS-IS, while "What is deleted" lists "`p[i].omin = 0` on the run span" (note:~299) and the site text says the run span's `omin` "is filled from the fact where the run span is built". The line at :1479 and `pcrec_memfn_wspan(sp, 0, ...)` at :1469 change in L3. Class I would give: WIDEN (the writer of the span's omin starts stating the fact), or ROW at the run span. Repro: `git show $T:src/gen/emit_dfa.c | sed -n 1466,1481p`.

### SITEMAP-4 CONFIRMED, severity doc, effort S: C10's hit count is wrong
C10 `git grep -n -E "req_run\.(whole_len|whole_maxoff|pos)" $T -- src/facts/facts.c` is stated (8). At T it prints 16 lines (98-100, 254-263, 354, 835-836, 891, 925-926). The cited sites (97-100, 253-262) hold; the count is off by 8, and the 8 extra include readers the note does not name: :891 (run_pin printer), :925-926 (`pcrec_fact_stamp_req_run`, the RX_REQ_RUN stamp text), :835-836 (listing printer; note site 11 names "printers facts.c:840-870": 835-836 is outside that range).

### SITEMAP-5 CONFIRMED, severity doc, effort S: site 12 / RM-2 "three hand-spelled range tests" undercount and mis-describe; C12 does not print two cited lines
C12's regex prints 8 lines (3 unrelated: compound.c:365, emit_code.c:109, emit_subst.c:663), i.e. 5 relevant: facts.c:106, :868, emit_dfa.c:8990, :9085, :9174. The note also cites facts.c:354-356 and emit_dfa.c:9360, which C12 does not print (9360 is `req_handoff_stamp`'s `>= PCREC_W_UNBOUNDED` -> "unbounded", an unbounded test, not a sign test; facts.c:354 is the `: -1` operand). Readers of K's state at T that the note omits (grep `PCREC_W_UNBOUNDED` over src/gen, facts.c: 10 K-state readers vs 3 named): emit_dfa.c:1099, :1644, :7926, :7961, :9113 (`whole_maxoff >=`), facts.c:356, :869. Most test `>=` UNBOUNDED, so a negative K is harmless to them, but "three readers re-ask by hand" and "deletes ... three hand-spelled range tests" state a population of 3 where the same grep prints 10 (only the `< 0` / `>= 0` tests, 8990 and 9085 plus the sentinel writers 106, 354, 9174 and printer 868, collide with a signed K).

### SITEMAP-6 SUSPECTED, severity doc: site 17 and K readers
The design's A3 lists K readers req_handoff_applies :8981, pf_handoff_applies :9309, req_landmark_hit_ppm :9197, req_handoff_stamp :9355, and the other margin caller src/gen/lmwalk.c:248 (passes non-negative K). The note's site 17 names only :9277-9294. Class AS-IS for each is probably right; they are absent from the map (grep 0 in the note except `lmwalk` in the register search term list). Confirm: `grep -n -E 'req_handoff_applies|pf_handoff_applies|req_landmark_hit_ppm|lmwalk.c:248' note` -> 0 lines.

## PROBED-AND-HELD
- Commands re-run at T (R0/sitemap/cmds.sh): C1 19, C2 13, C3 10, C4 13, C5 8, C6 10, C7 7, C8 3, C9 (39/14/9/3/2 per file), C11 6, C13 3, C14 5, C15 3, C16 3 (:238,:768,:941), C17 1 (:9293), C18 5+2, C19 9+0, C20 10 (+compile.c:3303,:3332), C21 2+1, C23 3+4, C24 3, C25 2, C31 31 and 20, C32 17: every count equals the note's. C10 and C12 differ (SITEMAP-4, -5).
- Cited line numbers checked and held: req.c 174, 535, 546, 556, 591, 625, 642, 655-658, 664, 695, 755, 767, 783, 889-892, 921, 940, 986-990, 1059-1063, 1072-1100, 1201/1204, 1247, 1278-1289; facts.c 97-100, 106, 253-263, 354-356, 868; facts.h 68-77, 285; facts_derive.h 105-114, 126-140; emit_dfa.c 1083, 1098, 1099, 1112, 1448, 1479, 1640-1644, 7896, 7919, 7930, 8990, 9082-9085, 9154-9174, 9293, 9360, 10725, 11335-11349, 11345, 5752-5794; kset.c 141, 302; known.h 24-25; internal.h 4115, 4467-4470; emit_dfa.c 3644; ctxnode.c 96-97; architecture.md register rows 609-633 (header at 609, row 20 at 633); match_api.md 6.3.7 heading :2391; tuning.md 2.28 :668, 2.41 :931; D168 :9839, D191 :10129.
- My own list vs the note: the 30 sites S1-S30 map to note rows as follows: S1/S2 -> 1,2; S3 -> 23; S4/S6/S7 -> 8,9,11; S5 -> 10; S8/S9 -> 18,19; S10 -> 16; S11 -> 12-15,17; S13/S14/S15 -> 16 (kit accepted); S19-S21 not a site (erased lookaround; sibling fact walks do not read the run); S22 -> 24; S23 -> 22; S24/S25 -> 28; S28 -> 13-17; S29 -> 25; S30 -> 20. S17/S18 (limits.def, axes.def) are no new row by the design (lb_bytes is a walk parameter, bit 31 text only; note covers via 8 and 28).
- Classes agreed: rows 1-9, 11-15, 17-28 (except 16, SITEMAP-3).

## Out of my lens
- Note line 138 register row 5 "Kind defaults ... NOT CARRIED" and row 14 "NOT CARRIED, done" dispositions: REGISTER lens.
- RM-2's deleted-sentinel claim depends on SITEMAP-5's population; AGGREGATION/FIRSTUNIT may want the 10-reader figure.

CRITIC COMPLETE
