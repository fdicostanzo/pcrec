# verify

## EMIT-3
HOLDS. Repro in verify/e3: `pcrec -p ra -fmemfn-simd=x86-64-v3 --pattern '(?i)hello'` + consumer including emmintrin.h: gcc -O2 rc 1 (`emmintrin.h:1460 inlining failed ... _mm_movemask_epi8: target specific option mismatch`); clang rc 0. Two artifacts (v3 `ra` then x86-64 `rb`) in one TU: gcc rc 1 (`_mm_set1_epi8` mismatch), clang 0. BASE (verify/e3b): both gcc rc 0. a.c has `#include <emmintrin.h>` line 100 / `<immintrin.h>` 135, inside region (open line 24-29).
Proposed fix (verify/e3c, private copy, intrin includes moved ahead of region open): consumer TU rc 0, two-artifact TU rc 0 (gcc -O2); artifacts a.c and b.c still compile under `gcc -O2 -mno-sse2` rc 0. Fix works.

## EMIT-5
HOLDS. `pcrec -p rx -fmemfn-simd=x86-64-v3 --pattern '^\s+|\s+$'` (verify/e5/cmp.c): `#include <string.h>` at line 214, region open 24-26, close 574-576. Consumer (include cmp.c, <string.h>, memcpy wrapper): gcc -O2 rc 1 (`string_fortified.h:26 inlining failed ... 'memcpy': target specific option mismatch`); clang rc 0.

## checks-2
HOLDS. Private copy verify/c2 (`git archive 424ddc742 memfn tests/mech/sabotages/S2997_...sh`), plant applied exactly per row (compose.c:954 now `... && 0   /* SABOTAGE S2997 */`). Build `gcc -std=gnu11 -O1 -Imemfn/include memfn/tests/g2/g2_simd_gen.c memfn/src/*.c`: plant compiler rc=0. `gen 20261009 40 OUT x86-64-v3`: control rc=0, PLANT rc=0 (SILENT; row expects DETECTED). kit.h:721 `#define MF_TARGET_REQUIRED 1` (default). Same plant built with `-DMF_TARGET_REQUIRED=0` (compile rc=0): gen rc=1 "g2v: mf_art_target accepted a first statement after a define" (loud). So the order rule is reachable only at switch 0.

## SEAM-5
HOLDS (kernel claim) / HOLDS (art gate, by quote). memfn.h:879-888 says "NULL = not offered: the kit then renders no guarded text at all". vany.c vany_level: `if (o->simd_open && o->simd_close) o->simd_open(...)` only wraps the call; `kit_out(o, "#include <%s>\n", l->header)` plus the helper body and, in vany_selector, `return fn__<stamp>(...)` are written unconditionally whenever `levels` is nonzero, so a bracket-less sink receives unguarded target-dependent text. ofsskip.c:648-649 `fn_in x = {..., o->simd_open && o->simd_close, ...}` feeds `x->brackets`; ofsskip.c:408 `if (!x->brackets) return 0;` (see below) is the second silent gate. Not compiled (reading claim).

## SEAM-1
HOLDS (structural, quoted). compose.c mf_art_target: `if (!t || !mf_target_c_of(t)) ...; if (art->target && art->target != t) kit_fail(...)`; targets.c `mf_target_c_of`: `if (t == &target_table[i]) return &target_c_table[i]` (same for `mf_family_c_of`); src/gen/memfn_targets.c:104 `if (a->family != b->family)` (pointer compare), and :140/:160 deref `t->family->name` / `mf_family_c_of(t->family)`. S2998 row: SAB_DESC 'mf_art_target takes a pointer that is not a row of the kit table (a copy, or NULL)', plants `if (!t || !mf_target_c_of(t))` -> `if (0)`; EXPECT=DETECTED, so by-address identity is a checked contract (checks reported gen rc=1 for it; not re-run).

## SEAM-2 / HOUSE-2 / HOUSE-3
HOLDS. (a) memfn.h:1334-1340 "The art-level `policy` is stored and read by nothing"; compose.c:927 `art->policy = policy;` is the only `art->policy` hit in memfn/src (git grep); kit.h:279 "stored, read by nothing"; pcrec passes literal: memfn_sites.c:199 `mf_art_begin(ma, cx->opt->prefix, 0, ...)`. (b) `git grep -n MF_TARGET_REQUIRED 424ddc742`: code uses are compose.c:1085 and :1088 (`MF_TARGET_REQUIRED && ...`), kit.h:720-721 `#ifndef ... #define MF_TARGET_REQUIRED 1`; the only -D in tests is `=1` (run_finder.sh:217 compile, policy_check). No build/test sets =0 (my checks-2 run used -D0 by hand). So the 0 arm is reachable only by -D.

## checks-1
HOLDS. `pcrec -p rx -fmemfn-simd --pattern '(?i)foobarbaz'` -> `RX_TARGETS "amd64:x86-64"`, `RX_MEMFN_FORMS "vrun@w16"`, `grep -c w32` in the artifact = (see below). simd_guarded_check.py:76 arm is `('simd', ['-fmemfn-simd'])`; its lines ~93 comment still says each vrun-* witness "renders `vrun@w32+w16` under the `simd` arm". simd_bounds.tsv:36 `vrun-w32 2800` is the row no bare-simd artifact can read (git grep 'vrun-w32' shows no other reader in simd_guarded_check; emit_sweep IDENT_MEMFN, axes/memfn_arm are other checks). Reading the "nothing reads the row" part is by absence of a w32 helper in the artifact; I did not plant a delete.
w32 count in c.c: 0

## checks-5
HOLDS (quoted tests/memfn/run_targets.sh at 424ddc742). RAN-floor `[ "$ran" -ge "$want" ]` is line 127 (section 3); section 4's `acell` (defined 191) does `ran=$((ran + 1))` at line 201, after it, so nothing floors section 4's cells. When host != x86_64 or no build/pcrec, line ~233 `else skip "pcrec artifact cells: ..."` skips the whole section; closing gate line 235 `[ $((pass + fail)) -gt 2 ]` is met by sections 1-3. Control line 219: `if gcc -O2 -c ... -o v3n.o v3_noregion.c 2> v3n.err; then bad ... else ok "control: ... refuses to compile"`: v3n.err is never read afterwards (grep of the file: only lines 219 mentions it). Only v3 gets the ymm census (line ~213). I did not run the section.

## checks-6 (the rfind claim only)
HOLDS. tests/cli/run_cli_tests.sh:2713: `if a.rfind(b'\n};', 0, c) < a.find(b'struct rx_info rx_info'): print('close before rx_info'); sys.exit()` (failure is the print). Python demo: with 'struct rx_info rx_info' absent, find=-1 and `rfind(...) < -1` is False for every rfind result (>= -1), so the failure branch never fires: a rename of rx_info disarms the test. Output below.
find -1 rfind 1 cond False
(other checks-6 sub-claims: not verified)

## CONTRACT-4
HOLDS. `pcrec -p rx -fmemfn-simd=<120 x q> --pattern abc` rc=1, stderr 263 bytes (wc -c): `pcrec: unknown CPU target 'qqq...' (known: generic x86-64 x86-64-v3 armv8-a); unknown CPU family 'qqq...` ending mid-token (no closing quote, no family "known:" list): 256-byte message + "pcrec: " prefix and newline cut.

## HOUSE-4
HOLDS. src/gen/memfn_targets.c:123-131 `pcrec_memfn_target` does `SimdSet s = {0,0}; ... resolve(cx->opt->flags, cx->opt->memfn_simd, &s, err, ...)` on EVERY call (fails via pcrec_ctx_fail). Callers (git grep 424ddc742): memfn_sites.c:203 (mf_art_target), memfn_targets.c:138 (stamp), :159 (guard), :167 (region open), :174 (region close) = 5 call sites, 5 resolves per artifact; nothing stores the result on Job/Ctx.

## HOUSE-5
HOLDS. `pcrec_emit_target_open` called once: emit_dfa.c:15961 (prologue); `pcrec_emit_target_close` at emit_dfa.c:16488 and emit_vm.c:14366 (two engine sites). The pairing invariant is not owned by one helper.

## EMIT-1 = CONTRACT-1 = SEAM-4(i)
HOLDS (text). match_api §6.3.10¶4 (line 2780 at 424ddc742): "`MEMFN_FORMS` is `"none"` iff the artifact is byte-identical (stamp lines aside) to its own `-fno-memfn-simd` compile"; ¶7: "its movers half holds an `-fmemfn-simd` compile byte-identical to the default exactly where its `MEMFN_FORMS` reads `"none"`". Neither has the "target's own text aside" clause that tuning §2.43¶4 (line 984) has. Number: `abc -fmemfn-simd` vs default differ by the guard/region/TARGETS/GUARDED_BYTES lines (EMIT-2 compile below shows FORMS none with different bytes). tuning §2.43¶4 still contains a later "none iff identical to SIMD-off" sentence per critic (see line 984 above; not separately diffed).

## EMIT-2
HOLDS. `pcrec -p rx -fmemfn-simd=x86-64-v3 --pattern abc` -> `RX_MEMFN_FORMS "none"` (SUBJECT and BASE). `gcc -O2 -c` rc=0 both. `objdump -d | grep -cE '\bv(pxor|movdqa|mov..|p..)\b'`: SUBJECT 2 VEX instructions, BASE 0.

## CONTRACT-2
HOLDS. `pcrec -p rx -fmemfn-simd=generic --pattern '(?i)hello'`: `RX_TARGETS "none:generic"`, `RX_SIMD_GUARDED_BYTES 0x0000000000000000ULL`, `cmp` vs the default compile = 0 (identical). match_api ¶9 (line ~2828-2836) says "at `-fmemfn-simd[=LIST]` every artifact carries a nonzero count, the guard and region at least".

## CONTRACT-3
HOLDS. `-fmemfn-simd=armv8-a --emit-main --pattern '(?i)hello'`: `RX_TARGETS "arm64:armv8-a"`, `RX_SIMD_GUARDED_BYTES 0x...a5`, `grep -c pragma` = 0 (no region), `sed -n 18,20p | wc -c` = 165 = 0xa5 (guard only).  para 15 (lane/u3tgt) (quoted above) says a family target carries "two pieces ... GUARD ... and the target's REGION"; only the portable target is said to have neither.

## CONTRACT-5
HOLDS. docs/spec/limits.md §8.3 at 424ddc742 (spec untouched by the diff): ¶1 "a SIMD-on form is its SIMD-off text plus whole guarded blocks (`#if <level>` ... `#endif`)" (retired model: no CPU #if now); ¶3 "At `-fmemfn-simd` it is nonzero exactly where a SIMD row rendered", falsified by `abc -fmemfn-simd` (FORMS "none", GUARDED_BYTES 0x1d5, critic's compile; and my armv8-a/v3 compiles above show FORMS none with nonzero bytes: v3 `abc` has region+guard). ¶3 also names "2,400 vrun-w16 and 2,800 vrun-w32" bounds with no target-text row.

## SEAM-3
HOLDS. At 424ddc742 (MF_TARGET_REQUIRED 1): memfn.h:1823-1828 "An art whose target is never stated renders no SIMD level ... the portable target's text" and lists "a call after the art's first define" as a refusal (code, compose.c: refuses only a FIRST statement after a define); kit.h:713-719 "0 until the U2+U3 joint merge, which sets it to 1 ... At 0 ..." directly above `#define MF_TARGET_REQUIRED 1` (721); policy_check.c:6 "kit.h guards the default 0", :8 "At the branch default the refusal is not reached"; run_finder.sh:210 "kit.h's default is 0, which never reaches the refusal"; S3000:7 "(the branch default 0 never reaches the refusal)". All stale. (Contradicted at runtime: checks-2 run shows the =1 default refuses.)


All 17 finding groups checked; 0 REFUTED, 0 PARTLY.

## VERIFY COMPLETE
Done: every verdict above is HOLDS.
