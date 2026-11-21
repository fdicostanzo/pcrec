# VERIFY: memfn-bspan3 (r69)


## V1 (SEAM-2)
HOLDS. Read window.c at build tree 7b0ac8bae: plan_of (1486) memsets w (1490), writes stop_ix=-1 and off/set/core/table/grp only (no hl, stop_alone, pick). wf_plan_site (2516-2518): decide -> plan_of -> wf_find_decide (fd_find writes fx->pick/brow, 2423) -> ... -> wf_find_prepare (2578). wf_find_prepare writes stop_alone (2464), find_groups (2471, writes w->grp), srch->prepare (2473) -> b_hors_prepare writes w->hl (1999). d_hors_head skip = plan_ix(w,w->hl) with grp[ih]<0 (3977); find_head skip = stop_alone ? stop_ix : -1 (3988). Unset skip would be 0 (memset). Calls: sed/grep only.

## V2 (SEAM-3, confirmed part)
HOLDS. window.c:3540-3552 wf_test_to: stretches are found by loop over i, wf_loop_len(w,i,skip) (3498, head check inside at 3500), then `i += len - 1`; no stored stretch list. wf_find_define (4062-4072) touches only w->fused / w->runs / w->strm->define, walks no plan entries. wf_find_use re-enters wf_rc_init and the render path (iteration at use only). Calls: sed on window.c.

## V3 (SEAM-4)
HOLDS. kit.h:1309 `const gate_contract *(*ct)(size_t i)`; compose.c:169 walk_row calls t->ct(i) unconditionally; :172 opt applied only `t->opt && in->s && kit_opt_denied(...)` (in->s NULL skips the deny); window.c:2387-2398 wf_tables_check checks Table E holes (`!holds || !ct`); memfn/docs/trace_format.md:95-96,103 names wfA/wfM/wfE (not in reach registry; floors G2's). Calls: sed/grep.

## V4 (SEAM-5)
HOLDS. ofsskip.c:707-718 fn_level_block: simd_open; includes |=; fn_head(name) then r->decl->render(...) (render closes the brace, kit.h:901-906 doc), "\n"; simd_close: exactly one function per block. kit.h:904 render typed `const struct fn_in *x`. ofs_fn_fits (ofsskip.c:674, counts fn_head+render+fn_call_line vs guarded_max); ofs_fn_fall (:636); callers vrun.c:683 (fits) and :592 (fall). fn_head (:614) is the single head. Calls: sed/grep.

## V5 (SEAM-1)
HOLDS. export TMPDIR=verify; python3 -I -B kit/site.py --simd off --width 32 -- '[0-9a-f]{32}' --memfn=no-window-skip -> fd=R7w, loop lo=1 end=32 k=31 (rc=0). '[0-9a-f]{31}[0-9]' -> fd=R7w, wfE E-find, loop lo=0 end=31 k=31. Control '[0-9a-f]{32}' no deny -> fd=D-hors, k=31 hors=1.

## V6 (EMIT-1, CHECK-2)
HOLDS. site.py --simd x86-64-v3 --out verify/v6X.c, then checks/tools/mkv.py ... base (hand-built V per §4.1/5), gcc -O0 -mavx2 -w -c, objdump of <rxa_search>: '[0-9a-f]{17}' (k16,B16) ymm=0 xmm=492 pshufb=6; '[0-9]{25}' (k24,B16) ymm=0 xmm=492; '[0-9a-f]{41}' width 4095 (k40,B32) ymm=138. So a ymm test is red at B16, positive at B32.

## V7 (EMIT-2, CHECK-2 control)
HOLDS. mkv.py base vs noai (drops always_inline from __w32), gcc -O0 -mavx2 -c, nm | grep 'vs0|w32': k40 B32 base -> no symbol, ymm in rxa_search 138; noai -> 't rxa_mf1_vs0__w32', ymm in search 0. k24 B16: base no symbol; noai lists t rxa_mf1_vs0__w32.

## V8 (EMIT-3, CHECK-3)
HOLDS. src/core/sb.c:206-232: pcrec_sb_simd_open/close only set flags and byte counters (simd_at, simd_guarded, simd_size); no sb write. Region is file-wide: verify/v6c_v.c has the target pragma push/pop around whole file (grep above); tests/memfn/simd_floor_check.py:160-185 PLACEMENT lint requires every BODY_OPEN between spans open and close ("a body outside the region"). Docstring lines 31-33 same.

## V9 (EMIT-4)
HOLDS (and stronger). python3 -I -B one-liner re.findall(r'(\w+)__w(\d+)\(', ...): on 'rxa_mf1_vs0__w32_b(' -> [] ; on 'rxa_mf1_vs0__w32(' -> [('rxa_mf1_vs0','32')]. The real regex is tests/memfn/simd_floor_check.py:124 HELPER = ^static inline size_t (\w+)__w(\d+)\( , which additionally requires a size_t return; V's functions are 'static inline __attribute__((always_inline)) int ...' (v6c_v.c:80,90), so the real HELPER matches neither __w32_b nor __w32 of V as spelled in §4.1/§5.

## V10 (EMIT-5, CHECK-10)
HOLDS. tests/memfn/routing_shape.py:38-40: FUNC_SUFFIXES = ('_reqrun_whole','_reqrun','_ofsskip'); HEAD = ^static inline size_t (\w+)\(const unsigned char \*subject, size_t n, size_t pos.... §5 V selector head is 'static inline __attribute__((always_inline)) int rxa_mf1_vs0(const unsigned char *rxa_mf1_s, size_t rxa_mf1_c)': wrong attribute position, int not size_t, params (s, c) not (subject, n, pos), name suffix _vs<j> not in FUNC_SUFFIXES. No match on any.

## V11 (POP-1)
HOLDS. R/population/spancensus2_bench_own.tsv: line 41 bench/bounded/patterns/hex32.rx = '[0-9a-f]{32}' (1:window:31); line 53 dig-exact-32.rx = '\\d{32}' (1:scan:31); line 175 bench/loglines/patterns/hex32-id.rx = '\\b[0-9a-f]{32}\\b'. Subject §0.1 table (rev3 lines 88-90) attaches 'loglines/hex32-id' to the plain '[0-9a-f]{32}' row and gives '\b[0-9a-f]{32}\b' none. Calls: grep/sed.

## V12 (POP-2, CHECK-6 frame part, RULING-8(b))
HOLDS. site.py --simd off: '[0-9a-f]{20}[g-z]{20}' --width 32 -> wfE E-stmt, fd R7w, no loop; --width 4095 -> E-find, D-hors, loops k=20 and k=19 (so stretches 20/19 < R7w's 24: with the frame column removed T-vscan still refuses, cell still reads absent; T-vwin needs D-hors, row is R7w at w32). '[0-9a-f]{33}' --width 32 -> E-stmt, R7w (a 32-position stretch only the frame column would refuse). Pin list §10.2 (rev3 line 780) counts: patterns hex16,hex17,hex1001,hex1002,dig24,dig25,dig65,dig66,ab[0-9]{26},[xy][0-9]{26},frame = 11 patterns; cells = hex16/17 x2 widths (4) + hex1001/1002 (2) + dig24/25 x2 (4) + dig65/66 (2) + brow 2 + frame 1 + once 1 = 16 pattern-width cells; note says "12 cells".

## V13 (POP-3)
HOLDS. site.py --simd off ... -e utf8: width 32: '[a-f]{17}' fd R7w, E-find, loop k=16; '[aeiou]{17}' R7w, E-find, k=16; '[^\n]{17}' R7w, wfE E-stmt, no loop. Width 64: '[0-9]{64}' R7w E-find k=63; '[0-9]{65}' R7w E-stmt no loop.

## V14 (CHECK-1)
HOLDS. site.py artifact verify/v6a.c line 320 '    .abi = 109,' (v6a.h carries the four: header '(abi 109)' l.1, '#if ... != 109' l.8, '#error ... (abi 109)' l.9, '#define PCREC_RX_ABI_H 109' l.12; .c also has '(abi 109)' l.1). src/gen/emit_dfa.c:3233 pcrec_sb_printf(c, "    .abi = %d,\n", PCREC_ARTIFACT_ABI). §10.2 mask (rev3 l.781) lists the four spellings only; '.abi = 109,' is a fifth.

## V15 (CHECK-4)
HOLDS. kit/anchors_fn.txt (each count=1): S2995 ofsskip.c:711 fn_level_block; S3001 :712 fn_level_block; S3002 :712 fn_level_block; S724 :712 fn_level_block; S730 :734 fn_selector; S690 :629 fn_call_line; S694 :629 fn_call_line; S695 :802 fn_define. SAB_BEFORE re-read in tests/mech/sabotages/S*.sh: S2995 'o->simd_open(o->u, (int)r->decl->level);', S3001/S3002/S724 'art->includes |= kit_level(...)->includes;' (fn_level_block lines), S730 the three-line simd_open/fn_call_line/simd_close block (fn_selector), S690/S694 'kit_out(o, "    return %s(subject, n, pos", callee);' (fn_call_line), S695 'if (fn_head(art, h, p, x.body_fn, o) || body->render(...)) return -1;' (fn_define). Rev3 §10.2 'Re-aims at U1' (l.824-834) names only S3277-S3282; none of the eight. §10.2 l.836 / §14 U6: REACH_ONLY at U1 and 'before delivery' (U6 row); U2 (where the one-writer lift rewrites these) lists no REACH.

## V16 (CHECK-5, by reading)
HOLDS. memfn/tests/run_g2_win.sh:567-596 (head passes): G2W_SPAN_HEAD="$h" G2W_FORMS_ONLY=1 one_run "head$h" "$LIB" runs g2/g2_win_gen.c's generated sites through the kit API (g2_win_gen.c:178-184 g2_art_begin: mf_art_begin + mf_art_target(mf_portable_target()) + mf_lever span lever); grep of run_g2_win.sh for 'build/pcrec|pcrec -p|--pattern' finds no hit: it never compiles a pcrec pattern. Generator declares g2w_t* tables at file scope (g2_win_gen.c:1927-1941).

## V17 (CHECK-6 main)
HOLDS. site.py --width 32 --simd off -- 'ab[0-9]{26}' --memfn=no-fd-d1 -> wfE E-find, fd D1w, loop lo=2 end=28 k=26. grep -n 'fd-d1' R/subject/block_span_rev3.md: only l.394 (§3.3 text) and l.968 (§16 item); the §10.2 T-table pins row (l.780) uses no --memfn=no-fd-d1 cell (its brow cells are default-D1 / PAIR 'ab[0-9]{26}', '[xy][0-9]{26}').

## V18 (CHECK-7)
HOLDS (padding part by running; non-mover part by reading + a base-tree pair). Copied checks/tools/census.sh to verify/census_v.sh (D= verify/w) and ran: bash verify/census_v.sh '\b[0-9a-f]{32}\b' 0 31 32 -> "lines 538; raw diff 3; after declared normalizer 1 (of which nop-like 1)". Raw diff: '< cs nopw 0x0(%rax,%rax,1)', '< nopl   0x0(%rax,%rax,1)' vs '> xchg %ax,%ax'. After removing exactly the §2.1 lines (nop, xchg %ax,%ax, data16...nopw, cs nopw; grep -v -E '^(nop|xchg +%ax,%ax|data16 .*nopw.*|cs nopw.*)$'): diff leaves '49d48 < nopl   0x0(%rax,%rax,1)'. Non-movers: §2.1 (rev3 l.229) defines them as non-eligible cells (k19 scan class here, e.g. '[0-9]{20}': R7w k=19 <24); the U2 arms do not exist yet, but a stretch that gets no wrapper compiles to the same C text: two compiles of '[0-9]{20}' at the build tree differ only in the '#include "nmN.h"' output-name line (diff of 1 line), no vs0/__w32 text (count 0). So the pair cannot exercise the normalizer: its diff is 0 independent of it.

## V19 (CHECK-8)
HOLDS. bin/pcrec-harness-mftrace -p rxa --features all -fno-memfn-simd --window-search-width=32 --pattern '[0-9a-f]{32}' (1 compile): stderr 'MFTRACE FDROUTE art=1 site=1 row=D-hors arm=E-find ren=B-hors frame=E-find' - no k field. Format source compose.c:1375: "MFTRACE FDROUTE art=%u site=%u row=%s arm=%s ren=%s frame=%s\n".

## V20 (CHECK-9)
HOLDS. tests/axes/memfn_arm.py:365-369: check(set(spelling) == {k[0] for k in MEMFN_CLASS}, "list-axes memfn rows ... != MEMFN_CLASS rows ...") (spelling = the --list-axes memfn section, l.288-289; skipped only under --measure). grep -n MEMFN_CLASS R/subject/block_span_rev3.md: no hit anywhere (§9.3, §10.1, §14 included); the only axes mention is §14 U6 'make test-axes' (l.933). A new span-vector memfn row would therefore make memfn_arm.py red until MEMFN_CLASS gains a row, and no unit lists that edit.

## V21 (RULING-1, -2, -3, -6, -7, -8(a), -10)
All HOLD, quote by quote, against R/subject/{decisions,memfn_requests,plan}.md and the subject.
- RULING-1 HOLDS. decisions.md:10307 add. 2 reads "READING (the kit's and main's, not his words; he may narrow it): option A, with the SIMD-off machine-code changes checked for no loss: a non-timing census ..., then a short timing of only those in a window he clears; any loser keeps today's text through a selector row." Subject FREEZE NOTE row (l.~44): "option A, the wrapper at every layer, with its SIMD-off machine code checked" (timing + keep-row dropped, no note that the reading moved). memfn_requests.md:983 R-47 GO: "No go for the scalar layer: it stays H64." decisions.md:10304 Consequences: "Off by default rides on -fmemfn-simd (OFF) as today." 10307 also records "true in source, but gcc's machine code differs on 2 of 10 probes (`\w{20}`, `\w{32}`)".
- RULING-2 HOLDS. grep -ci over decisions/plan/memfn_requests/memfn_responses: 'smallest form','scan-scope','wrap-deny','wrap-differs' = 0 everywhere; 'SMALLEST' only unrelated hits (requests:869 lookbehind, plan:91, decisions:705,8714); 'recalled' = 1 unrelated (decisions:10223). decisions.md:9316 D155 item 6 AMENDMENT: "The SIMD-off artifact routes through the helper too — a one-time, measured byte move and abi event — so the floor rule stays exact."; the subject never cites 9316/"AMENDMENT"/"measured byte move" (grep, 0 hits).
- RULING-3 HOLDS. decisions.md:9021 D147: "Every acceptance reading for a change that touches searching reports BOTH layers (SIMD-off and SIMD-on)."; R-47 CONSTRAINTS: "G1 alpha at both layers". Subject §2.2 l.249-251: "No measurement of that change is planned (the timing was cut: it cannot see the effect)." and §9.4 (l.733-735) meets D147 at SIMD-off by the census only "where the code is identical".
- RULING-6 HOLDS. Subject §9.4 l.726-730: population "the bench patterns and SPAN-SEED", then "The real population is 3 movers, so every bin is UNREACHED at both layers by construction"; trigger "a bin reaches 8 real movers" (l.732-733); SPAN-SEED has 28/31 V sites (§10.1 as cited).
- RULING-7 HOLDS. decisions.md:10302 now names kit journal commit 923ea33d2 and says 29e893818 "does not quote them"; :10307 gives "0 corpus sites ... 3 bench sites" and says "CORRECTED by the kit's review r67 memfn-bspan". Subject §0.1 l.96-97 still says add. 2's "corpus 1 of 6,403" is "main's record to correct"; §15 item 3 (l.946-947) still lists the provenance pointer and population line as owed.
- RULING-8(a) HOLDS. Subject U1 row (l.927): "The five sabotage re-aims (S3277-S3282)"; l.1011 "five sabotage re-aims"; tests/mech/sabotages has S3277,S3278,S3279,S3280,S3281,S3282 = 6 rows in the range; §10.2 l.827-834 lists six (S3278, S3279, S3282, S3281, S3280 re-anchored, S3277 re-checked).
- RULING-10 HOLDS. Subject l.69: D201: "Revisit when the scalar layer is measured"; record decisions.md:10305: "**Revisit when:** the scalar layer is measured" (colon). Subject l.170: "no `#if` in the code the kit emits into a function body"; record :9349: "NO `#if`/`#ifdef` in the code the kit emits into a function BODY".

## V22 (SEAM-6, premise only)
Premise HOLDS; no witness hunted (0 extra compiles). src/gen/emit_dfa.c:3743-3746 emit_u8_table prints "    static const unsigned char %s_%s[%d] = {" (4-space indent; callers 4580, 5256, 7695). In a real artifact (verify/v6a.c) 'static const unsigned char rxa_anchored_byte_class[256]' (l.104), '..._is_accepting' (l.122), '..._scan1' (l.125) sit inside rxa_match's body (opens l.100, closes l.173): function-local. Only the kit's own '_sh' table is file-scope (l.68). ofsskip.c:181-193 table_params exists precisely to pass pcrec's tables as parameters. Subject §5 V signature is `(const unsigned char *rxa_mf1_s, size_t rxa_mf1_c)`: no table parameter. So a `__body` at file scope naming pcrec's local table would not compile; whether a real site shares one C-table offer across a 16+ stretch is not established here.

VERIFY COMPLETE
