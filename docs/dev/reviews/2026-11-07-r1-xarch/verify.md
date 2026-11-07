# VERIFY xarch

## PREM-1 HOLDS
`( cd verify/work && build/pcrec --features all -fmemfn-simd -p rx -o c1.c --pattern '^\s+|\s+$' )` rc=0. c1.c:16 `#define RX_COMPOUND "split"`; :171 `RX__F_MEMFN_FORMS "none"`; :346 `RX__Q_MEMFN_FORMS "none"`; :516 `RX_MEMFN_FORMS "none"` (shell). `grep -c _MEMFN_FORMS c1.c` = 3 stamps, i.e. one kit art per part (f, q) plus the shell. Code: src/gen/memfn_sites.c:183-200 `if (!job->mf) ... job->mf = mf_art_begin(...)` (art per Job/attempt). tests/compound/run_part_measures.sh:92 text "MFMEAS roles '$roles', not '- f q ' (one per art)". Caveat: this pattern reaches no SIMD form here (FORMS "none"), but the multi-art structure and per-art stamps are as claimed.

## PREM-2 / PROBE-3 HOLDS
- `build/pcrec -fmemfn-simd -p rx_v3 -o b2.c --pattern '(?i)cat'` rc=0; b2.c:180 defines `int rx_v3_search(` (legal caller prefix). So pattern B at prefix `rx_v3` defines the same symbol the note's variant stem `rx_v3` gives pattern A's v3 variant (`rx` + `_v3`): duplicate by construction.
- Generic at stem `rx` (a2.c, `-p rx`) + a hand dispatcher `int rx_search(...)` in one TU (`#include "a2.c"` + `#include "b2.c"` + dispatcher): `gcc -O2 -c st.c` -> `st.c:3:5: error: redefinition of 'rx_search'` (note: previous definition at a2.c:180), gcc rc=1. Control: `#include a2.c; #include b2.c` alone (stems rx and rx_v3) compiles, rc=0.
- Note the pcrec double-underscore derived names (`rx__f_*`) are visible in c1.c (PREM-1 repro), supporting PREM-2(a).

## PREM-3 / PROBE-4(1) HOLDS
TU = `#include "a2.c"` (-p rx) + `#include "b2.c"` (-p rx_v3) + `int disp(..., const rx_buffers *b, ...) { return rx_v3_search_in(s,n,0,c,b); }`: `gcc -O2 -c buf.c` -> `buf.c:3:117: error: passing argument 5 of 'rx_v3_search_in' from incompatible pointer type [-Wincompatible-pointer-types]`, rc=1 (b2.h:276-281 `typedef struct {...} rx_v3_buffers;` anonymous, per-prefix). Frame/size macros are per-stem: a2.h:268-274 `RX_NCAPS, RX_RESUME_FRAMES, RX_TRAIL_FRAMES, RX_RESUME_FRAME_SIZE, RX_TRAIL_FRAME_SIZE, RX_BUFFER_ALIGN` vs b2.h:268-274 `RX_V3_*` same set (equal for this pattern; per-variant by construction). The "iterator layout" sub-claim of PREM-3 is not part of this id; see PROBE-7.

## PROBE-4(3) HOLDS
Note text (`git show e2f9793d1:docs/design/memfn/target_seam.md | grep -ciE guarded`) = 0. The stamp exists and is emitted: a2.c:374 `#define RX_SIMD_GUARDED_BYTES 0x0000000000000d91ULL` (b2.c:374 `RX_V3_SIMD_GUARDED_BYTES`, same value). Readers (git grep at build tree, src lib cli tests docs/spec memfn scripts): docs/spec/{limits,match_api,tuning}.md, src/gen/{memfn_stamps,stamp_kinds}.c, tests/memfn/{simd_guarded_check.py,simd_floor_check.py,run_simd_guarded.sh,simd_bounds.tsv,stamp_mover_census.py}, tests/codegen/{run_codegen_tests,run_cpset_structure,run_recursion_identity}.sh, tests/resource/run_resource_tests.sh, tests/mech/sabotages/S730_*.sh.

## PROBE-4(4) HOLDS
`build/pcrec -fmemfn-simd -p rx --pattern '(?i)cat'` (m1.c) vs same plus `--emit-main` (m2.c): m1.c:373 `#define RX_MEMFN_LIBC "memchr"`, m1.c:388 `.flags = 0ULL,`; m2.c:375 `#define RX_MEMFN_LIBC "fprintf,memchr,printf,strlen"`, m2.c:390 `.flags = 2ULL,`.

## PREM-4 HOLDS
gcc 15.2.0 (Ubuntu 15.2.0-16ubuntu1), Zen 4. `ctor.c` (constructor(101) reads `__builtin_cpu_supports("x86-64-v3")`, main reads it too): `gcc -O2 ctor.c && ./ctor` -> `ctor=0 main=2`; `-static` -> `ctor=0 main=2`. `ifr.c`: ifunc resolver without init vs with `__builtin_cpu_init()`: `ifunc picked 1 ; with cpu_init 2` (1 = generic arm, 2 = v3 arm). Both rc=0 compiles.

## PREM-5 / PROBE-2 HOLDS
Inputs copied READ-ONLY from critics' scratch into verify/work (b2v3.c = v3 variant of `(?i)cat` with `#pragma GCC push_options / target("arch=x86-64-v3")` at lines 21-22, b2cl.c = same with `#pragma clang attribute push(__attribute__((target("arch=x86-64-v3"))), apply_to = function)` at :22 and the GCC pragma at :24-25). clang = Ubuntu clang 21.1.8.
- `gcc -O2 -Wall -Wextra -c b2v3.c` rc=0, 0 errors. `gcc ... b2cl.c` rc=0, 0 errors; `objdump -d` of the gcc object: 15 ymm lines.
- `clang -O2 -Wall -Wextra -c b2v3.c` rc=1, 21 `error` lines, first: `b2v3.c:130:24: error: always_inline function '_mm256_set1_epi8' requires target feature 'avx', but would be inlined into function 'rx_v3_mf1_ofsskip__w32' that is compiled without support for 'avx'`.
- `clang -O2 -Wall -Wextra -c b2cl.c` rc=0, 0 errors; clang object has 15 ymm lines.
(Side note: one stray `gcc -c -o /dev/stdout` of mine used gcc's default temp dir, which I had not redirected; it errored and wrote nothing of consequence. TMPDIR was set to verify/work for all later compiles.)

## PROBE-1 HOLDS
comb.c = critic's two-variant TU for `(?i)cat` using `#pragma GCC target("arch=x86-64-v3")` (lines 343-344); combisa.c = same with additive list `target("avx2,bmi,bmi2,fma,lzcnt,movbe,popcnt,f16c,xsave,sse4.2,ssse3,sse4.1,cx16")`. `gcc -O2 <flags> -c <src>` (gcc 15.2.0), rc / error count:
- default: comb.c rc=0/0; combisa.c rc=0/0
- `-march=native`: comb.c rc=1, 1 error `string_fortified.h:26:1: error: inlining failed in call to 'always_inline' 'memcpy': target specific option mismatch`; combisa.c rc=0
- `-march=x86-64-v4`: comb.c rc=1, same memcpy error; combisa.c rc=0
- `-march=native -U_FORTIFY_SOURCE`: comb.c rc=1, 20 errors, first `emmintrin.h:658:1: ... '_mm_set1_epi8': target specific option mismatch`; combisa.c rc=0
- `-march=x86-64-v4 -U_FORTIFY_SOURCE`: comb.c rc=1, 20 errors (same); combisa.c rc=0
Matches the claim (fails with and without fortify; additive list compiles). Not re-run: the 2.36M answer-equality count.

## PROBE-5 / ADD2-2 / MEAS-4 HOLDS (the factual half; the "loses it" half is a reading of the note)
`build/pcrec -fmemfn-simd -p rx -o s1.c --pattern '(?i)cat'` -> s1.c:372 `#define RX_MEMFN_FORMS "vrun@w32+w16"`; `-fno-memfn-simd` -> s0.c:292 `"none"`. `gcc -O2 -c` (default -march): s1.o xmm lines 14 (12 in `<rx_search>`, 2 in `<rx__one_local>`), ymm 0, text 2618; s0.o xmm 2, text 2386. s1.c:89 guard `#if defined(__x86_64__) && !defined(__ILP32__) && defined(__SSE2__)` plus :126/:165 AVX2 and :167 SSE2 arms: at default -march the SSE2 w16 rung is live. Note text (target_seam.md at e2f9793d1): :147 "the default list is `generic` alone", :152-153 "With the default list `{generic}` ... the features are empty, so no level is admitted. The kit text is today's SIMD-off text"; :60 `-fno-memfn-simd` "maps to the generic"; the note never says what `-fmemfn-simd` maps to (grep above shows no such sentence). So an empty-features default yields the SIMD-off text, losing the w16 rung that `-fmemfn-simd` has today, unless a baseline (sse2) target is added. Whether the owner intends that is a design question, not testable here.

## PROBE-7 HOLDS
- Shape: `gcc -O2 -c comb.c` (critic's hand dispatcher TU; the dispatcher is their construction following note §5, I recompiled it) then `objdump -d comb.o`: `<rx_next>: endbr64; mov 0x0(%rip),%rax # __cpu_model; testb $0x2,0x8(%rax); je be0; jmp ad0 <rx_v3_next>; ... be0: jmp 280 <rx_gen_next>` = a tail-jump trampoline.
- D165 item 5 at decisions.md (5b43f8e9a) line 9704: "5. **Indirection budget** ... one EXPORTED call per match, never a chain (`next` contains the search body, it does not wrap `_search`); `rx->entries->next` is the artifact's own function pointer, no trampoline; ..." The word "trampoline" is ruled out there by name.
- `rx_iter` (a2.h, `-fmemfn-simd -p rx`): fields hdr, rc, flags, s, n, lo, vars, nvars, bufs; a2.h:213 `#define PCREC_ITER_LAYOUT 3u /* bumps with any change to rx_iter's layout */`. No field for a dispatch choice (only `flags`, `PCREC_ITER_F_*`, could carry a bit).

## PREM-6 HOLDS
`git -C worktrees/crit-xarch grep -n MF_P_PORTABLE_ONLY -- src lib cli memfn tests` = 67 lines in 20 files (excluding docs/dev/lanes). Non-test source/doc readers (memfn/src memfn/include src lib): lib/pcrec.h:1134 (doc), memfn/include/memfn.h:460-461 (definition), memfn/src/fields.def:137 (`MF_CLASS(PORTABLE, ...)`), memfn/src/formhash.c:254 and :291, memfn/src/gate.c:438,439,448,451, memfn/src/vrun.c:16 (doc), src/core/internal.h:7455 (doc), src/gen/memfn_sites.h:109 (doc), src/gen/memfn_stamps.c:323 (`? 0u : MF_P_PORTABLE_ONLY`). Tests: memfn/tests/g2/{g2_gen.c 21, g2_simd_gen.c 2, g2_win_gen.c 11}, tests/memfn/{arm_fixtures.c 11, proof_check.c 2, proven_check.c 2, run_proof.sh 1}, tests/mech/sabotages/{S722,S1224}. The SIMD row's admission is a gate-contract class, not levels.def: vrun.c:498 `[FLD_policy] = CM(NONE) | CM(SIZE), /* SIMD layer: never PORTABLE, never INLOOP */`.
fn_rungs, ofsskip.c:509-522: `unsigned nr = 0; rung[nr++] = top;` then adds named rungs -> nr >= 1 whenever a PREFIX row `top` is chosen. So empty-features -> nr==0 needs the walk (fn_select, not levels.def) to decline, i.e. a gate field. (Test-count caveat: 67 lines includes tests and docs; the "~10 rows" part of the critic's claim not separately counted.)

## PREM-7 HOLDS
- One bit: memfn/include/memfn.h:469 `#define MF_INC_STRING_H (1u << 0)`; `git grep MF_INC_` over memfn/include memfn/src src shows only MF_INC_STRING_H (and the generic `includes` fields at memfn.h:1143,1200,1391).
- SIMD headers are written inline by the kit inside the guard: memfn/src/ofsskip.c:567-571 `kit_out(o, "#if %s\n", lv->guard); if (!(art->simd_inc & 1u << ...)) { kit_out(o, "#include <%s>\n", lv->header); ...}`; memfn/src/vany.c:157 `kit_out(o, "#if %s\n#include <%s>\n", l->guard, l->header);`.
- pcrec decides its includes itself: src/gen/emit_dfa.c:15660 `bool need_string_h = dfa_body && ...`, :15946-15947 `if (need_string_h) pcrec_sb_puts(c, "#include <string.h>\n");`, :15951 `cx->job->string_h = need_string_h || ...EMIT_MAIN`; the kit bit is only an assertion afterward: src/gen/memfn_sites.c:1001-1003 `if ((mf_includes(art) & MF_INC_STRING_H) && !cx->job->string_h) pcrec_ctx_fail(cx, 0, "internal error: the memfn kit's text calls <string.h> functions the prologue did not include");`.

## PREM-8 HOLDS
memfn/include/memfn.h:878-891 `typedef struct mf_sink { puts, vprintf, cmt_open, cmt_close, stamp, cstr, comment_byte (with `int (*extra_escape)(uint8_t)`), legend_byte, stamp_int, simd_open, simd_close } mf_sink;` and the hooks at :1003-1017: `on_cand(void *u, mf_sink *c, const char *cand)`, `member`, `table_name`, `fn_name`, `note(void *u, mf_sink *c, uint32_t part)`, `note_tag`. So callbacks go well beyond simd_open/simd_close; on_cand and note write pcrec text through a sink mid-render.

## PREM-9 HOLDS
Plan row `- [XARCH-DEV]` at 5b43f8e9a; its RULED text reads (quoted): "A variant is a complete matcher planned and priced for one target. Build time: pcrec emits the build target's variant. Run time: one artifact holds 2-3 variants (generic + 1-2 SIMD) as target-attributed functions, a once-per-process CPU dispatch entry, and each variant's own entry." The note (target_seam.md at e2f9793d1, lines ~18-20) quotes it as "A variant is a complete matcher planned and priced for one target. [...] one artifact holds 2-3 variants ...": the elided sentence is "Build time: pcrec emits the build target's variant. Run time:". The note's own text has no sentence mapping `-fmemfn-simd` or the build target to a list value (see PROBE-5 grep).

## MEAS-3(b) HOLDS
- `grep -c 'fno-memfn-simd' scripts/emit_sweep.py` = 0 (build tree): no DIFFER_PINS cell for it (`DIFFER_PINS = {` at :465; the only memfn cells are `-fmemfn-simd`: :515,:516,:546,:547). NULL_ARM (:613) is `("byte", "", "c-default")`, ASSERT_ZERO (:599) names only `-fno-end-window`.
- Tool text: usage :173-177 "--extra=ARGS ... With --extra the run is ONE ARM ... fail unless DIFFER_PINS has a floor for it (--no-differ-floor to waive, loudly)"; code :1704-1708 `elif key not in DIFFER_PINS: if not waive_unpinned: verdict.append("NO DIFFER FLOOR PINNED (an arm that cannot fail on its own plumbing is not a check; --no-differ-floor waives)")`. I did not run the (heavy) sweep; the refusal is from reading the code path.
- MEAS-3(a) side fact reproduced: `build/pcrec -p rx` vs `-fno-memfn-simd -p rx` on `(?i)cat`: `cmp` differs at byte 551; `diff` shows only line 17 `#include "d0.h"` vs `"d1.h"` (output file name).

## MEAS-5 HOLDS
memfn/src/levels.def: `grep -n 'MF_LEVEL(' ` -> :41 `MF_LEVEL(LV_X86_W16, "x86-64", ..."w16")` and :44 `MF_LEVEL(LV_X86_W32, "x86-64", ..."w32")` (plus the doc line :12 of the macro signature). Exactly two levels; header comment at :37-39 says a 64-byte level and every aarch64 level are born with their first row.

## ADD2-4 HOLDS
levels.def :12 signature `MF_LEVEL(token, family, guard, header, vw, test_march, forbid, stamp)` - `family` is the 2nd column ("x86-64" for both rows). Guards (lines 41-46): `"defined(__x86_64__) && !defined(__ILP32__) && defined(__SSE2__)"` and `"defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX2__)"`: the family predicate (`__x86_64__`) and `!__ILP32__` are in the guard strings. Same strings appear in emitted s1.c:89,126,165,167.

## MEAS-7 HOLDS
`build/pcrec -fmemfn-simd -p rx --pattern P`, then `gcc -O2 -c` (default) vs `gcc -O2 -march=x86-64-v3 -c`, `.text` extracted with `objcopy -O binary -j .text` and `cmp`:
- `abc` (FORMS "none"): .text 1272 vs 1272 bytes, DIFFERENT
- `a(b|c)+d` ("none"): 5272 vs 5272, DIFFERENT
- `[0-9]+x` ("none"): 2104 vs 2104, DIFFERENT
- `foo|bar|baz` ("none"): 1384 vs 1384, DIFFERENT
- `(?i)cat` ("vrun@w32+w16"): 1784 vs 2104, DIFFERENT; and `(?i)cat` with `-fno-memfn-simd` (SIMD-off): DIFFERENT too.
So 4 of 4 SIMD-less patterns have equal size but non-identical .text.
§8 data point reproduces via `size` (text/data): SIMD-off 2386/224; `-fmemfn-simd` default -march 2618/224; `-march=x86-64-v2` 2618/224; `-march=x86-64-v3` 2922/224; `-march=znver4` 2962/224 (the critic's v2 and znver4 figures also match). Not re-checked: the 2618+2922 vs 2386+2922 "formula inconsistency" in the note (a reading of §8 text).

## ADD2-5 HOLDS
- tests/cli/run_cli_tests.sh:2421 `pass "-fmemfn-simd renders the vrun-w16 helper and names it in MEMFN_FORMS"` (regex :2418 `^#define RX_MEMFN_FORMS "vrun@[a-z0-9+]*w16"$`); :2436-2438 greps `^#define RX_MEMFN_FORMS "vrun@w32+w16"$` on the `-fmemfn-simd ... (?i)cat` output, pass text "-fmemfn-simd renders the vrun-w32 helper above vrun-w16 (MEMFN_FORMS vrun@w32+w16)". Also :2425-2433 compare `--memfn=no-vrun-w16` bytes against the -fmemfn-simd artifact.
- tests/memfn/row_floors.tsv:106-107 `fn vrun-w16 70 743` / `fn vrun-w32 70 743` (per-row CHOSEN floors; header says ROWCON N4); tests/memfn/simd_accept.tsv (SIMD acceptance record: "One line per SIMD row x level x official CPU class", R-13); both wired in tests/memfn/run_rows.sh/rows_check.py and Makefile (git grep). Also memfn/tests/run_g2_simd.py and tests/memfn/simd_guarded_check.py mention vrun@w32/w16.
- CI: .github/workflows/ci.yml has one `runs-on:` (line 51, `ubuntu-latest`); no job for Darwin/aarch64 (the only darwin/macos mentions are comments at :11, :112; grep for aarch64/arm64 empty).
- Not verified: the "SIMD-on default is now box-dependent output" half of ADD2-5 (it concerns D188 Addendum 2 text at commit 6fc4b6912 and the design's selection rule, not the tests/CI facts asked for here).

VERIFY COMPLETE
