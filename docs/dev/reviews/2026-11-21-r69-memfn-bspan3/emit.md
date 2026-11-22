# CRITIC EMIT: memfn-bspan3 (r69, design re-check of block_span.md rev 3)

## Fix ledger
- F-1 (rule part): LANDED-WRONG (EMIT-1, EMIT-2, EMIT-3, EMIT-4, EMIT-5). The spelling half works: the amended SELECTOR finds the selector and leg (c) and (b) pass on correct text (12 pairs); the -O0 half does not.
- F-5: LANDED-RIGHT (reversed halves, signed values: 0 answer differences on 13 sites; index-order control differs 414/1204).
- F-8: LANDED-RIGHT (B = 32 iff K >= 32 else 16, K >= 16 assert; read [p, p+K) only, guard pages both ends, k 16..1000).
- F-13: LANDED-RIGHT (re-derived: the 3 bench sites 0 instruction differences, `\w{20}` 20 lines, with rev 3's `unused` on `__body`).

Per unit: **U3 READY** (§4.1/§4.2/§5 text, built literally, is answer-identical and compiles clean everywhere probed). **C18 in U4: READY WITH TEXT FIXES** (EMIT-1..5; suggested rule: at -O0 an always_inline helper is ABSENT from `nm`, path fixed by the selector's head, not the helper's; bracket placement is leg (c)'s).

## Findings

### EMIT-1 (CONFIRMED; build/check, blocks U4) - the amended C18 -O0 rule (ii) "a `ymm` register in the function that calls the selector" is FALSE on the correct text at B = 16, i.e. on every real site and on BOTH named witnesses
§10.2 "The C18 amendment", -O0 rule (ii); §16 item 6c (its probe was a ymm helper only). r68 F-1 (rule part).
Repro: hand-built §4.1+§5 text (emit/tools/build_v.py) from the build tree's `[0-9a-f]{17}` (HORS k 16, B 16) and `[A-Za-z0-9_-]{33}` @4095 (HORS k 32, B 32) x86-64-v3 artifacts; `gcc -O0 -c`; `objdump -d` of `rxa_search`:
- k 16 / B 16: compiles, no `vs0` symbol (chain inlined, 6 `pshufb` in rxa_search), **ymm 0**, xmm 492 -> rule (ii) RED on correct text;
- k 32 / B 32: ymm 138 -> (ii) green.
The B = 16 rung is `__m128i`/`_mm_` text (§4.1, §4.4): xmm only. Every real site is k 31 (§0.1), `[0-9a-f]{17}` and `[0-9]{25}` (the NAMED witnesses) are B 16, so a lane building (ii) literally gets C18 red on all of them. Baseline: today's ON `rxa_search` at -O0 holds 0 xmm/ymm (hx17, hx32), so the rule could read "a vector register (xmm or ymm) / the level's `pshufb`" - but see EMIT-2 for the simpler form.
Severity build (C18 red on correct text); effort trivial (text); blast radius U4.

### EMIT-2 (CONFIRMED; check design) - the -O0 rule does not say how a helper is put on the `nm` path or the always_inline path; read off the helper's own head (the only fact the text offers), the "drop always_inline" plant takes the `nm` path and PASSES
§10.2 the -O0 rule ("for `always_inline` helpers: the `nm` test does not apply") and its first control ("must not silently pass both shapes"). r68 F-1.
Repro: the k 16 and k 32 texts above with `always_inline` deleted from `__w32`'s head only; `gcc -O0 -c`: rc 0, `nm` lists `t rxa_mf1_vs0__w32` (today's C9 `nm` leg: PASS), rxa_search holds a `call` to it and ymm 0. A checker that sends a helper down the always_inline path because its head says `always_inline` sends this plant down the `nm` path, where it is a legal ofsskip-shaped helper: no leg rejects it. To catch it the rule must FIX the path independently of the helper's head (e.g. "every helper of a selector whose own head is always_inline must be always_inline", or a name-family rule). Simplest rule that works at BOTH widths and distinguishes the plant: **at -O0 an always_inline helper is ABSENT from `nm`** (correct text: 0 `vs0` symbols at k 16 and k 32; plant: the symbol appears), with the path fixed by the selector's head; no register reading, so EMIT-1 goes with it.
Severity check design (a control the rule cannot pass); effort small; blast radius U4.

### EMIT-3 (CONFIRMED; check design) - rule (i) ("the -O0 compile succeeds") cannot see a helper outside the BRACKET: the bracket is not text and not the ISA region
§10.2 -O0 rule (i) and its second control ("a plant that moves `__w32` outside the bracket makes (i) fail"); §5 "between `simd_open(LV_X86_W32)` and `simd_close`"; §16 item 6c. The plant itself is lens checks'; what (i) can see is the rule.
Facts (build tree): the bracket is `src/core/sb.c:206-234` `pcrec_sb_simd_open`/`_close`, a byte counter that writes no text. The ISA comes from the target REGION, a file-wide `#pragma GCC push_options` + `target("avx2,...")` (clang `attribute push`) opened ahead of the first function and closed at the file's end (hx32 @x86-64-v3: lines 24-29 .. 352-356); C18's placement lint already requires every body inside it. So:
- `__w32` outside the bracket, inside the region = BYTE-IDENTICAL text but for the `SIMD_GUARDED_BYTES` stamp: -O0 compiles; the amended C18 rejects it only by leg (c)'s byte count (`(c) inserted 1992 bytes, SIMD_GUARDED_BYTES 0x...68d`; emit/a/id33.onv_outbracket.c);
- `__w32_b` + `__w32` moved ahead of the region open: placement rejects it ("a body outside the region"), and the compile fails at EVERY -O level (the intrinsics' own "inlining failed ... target specific option mismatch"), so (i) adds nothing to C9's existing -O2 `-Werror` compile.
§16 6c's `outreg` (a caller outside the region) cannot occur in an artifact without failing placement. Fix: drop (i) as a separate leg; name leg (c) as what catches bracket placement.
Severity check design; effort trivial (text); blast radius U4.

### EMIT-4 (CONFIRMED; build) - the amended HELPER spelling does not reach `__w32_b`, which the note says IS a HELPER for the exclusivity lint
§10.2 "spelling" bullet. The words amend the HEAD (attributes, `int`), not the NAME: `HELPER`'s `(\w+)__w(\d+)\(` needs `(` right after the digits, so `rxa_mf1_vs0__w32_b(` never matches. Repro: emit/c18/sfc_amended.py (the head family applied literally) over 12 hand-built ON texts: `HELPER.findall` = `[('rxa_mf1_vs0', '32')]` only; the block helper is invisible to "helper ... is no admitted level". Fix: state the name form, e.g. `(\w+)__w(\d+)(?:_b)?\(`.
Severity build (a stated guarantee silently absent); effort trivial; blast radius U4.

### EMIT-5 (CONFIRMED; check gap) - C18 leg (d) (routing_shape.py, the D155 add. 1 selector rule) never sees a V selector; the amendment names only SELECTOR/HELPER
§10.2 amendment; `tests/memfn/routing_shape.py` `HEAD` (`static inline size_t X(const unsigned char *subject, size_t n, size_t pos...)`) and `FUNC_SUFFIXES` (`_reqrun_whole`, `_reqrun`, `_ofsskip`). V's head is `static inline __attribute__((always_inline)) int rxa_mf1_vs0(const unsigned char *rxa_mf1_s, size_t rxa_mf1_c)`. Repro: `routing_shape.check()` on the 12 ON texts: 0 FUNCs counted on every one. So the "selector is ONE forwarding call, `__body` defined above with the same parameters" rule, which the note leans on (§2 "one call per arm"), is checked for V only incidentally by (c). Its "no #if in a body" half still covers V. Fix: the amendment names routing_shape's HEAD/FUNC suffix too (the one writer's head family), or says (c) is V's only selector check. Not answer-moving.
Severity maintenance/check; effort small; blast radius U4.

## PROBED-AND-HELD
Tools: emit/tools/build_v.py (§4.1 + §5 hand-built LITERALLY from the build tree's OFF/ON artifacts, `--head keep`; `unused`+`always_inline` on `__body`, selector one call, `#include <immintrin.h>` ahead of the region, stamp = C18's own byte count), emit/tools/{drv.c,subj.py,ans.sh} (find-all, OFF today vs wrapped-OFF vs V-ON, subject flush against a PROT_NONE page at the START and at the END), emit/c18/sfc_amended.py (C18 copy with the §10.2 head family), emit/c18/run_pair.py.
- **Answers (U3 text):** 13 sites, 0 differences, OFF-wrapped and ON both: `[0-9a-f]{17}` (k16 B16), `[0-9a-f]{32}` (k31), `[0-9]{25}` (R7w k24), `\w{20}`, `\w{32}`, `[^\n]{17}` (255-member, all tables -1), `[\x80-\xbf]{25}` (R7w, hi_t only), `[0-9]{33}`@4095 (k32 B32), `[A-Za-z0-9_-]{33}`@4095 (k32), `[0-9]{65}`@4095 (k64), `[0-9a-f]{1001}`@4095 and `[^\n]{1001}`@4095 (k1000; today's lone 0..63 + loop 64..999 replaced whole); ~1100-7000 cases each incl. a full failing-index staircase; 4 of them also at -O0 and -march=native. Control: index-order tables -> 414/1204 differ (the driver sees a wrong text). No guard-page fault anywhere.
- **Compiles:** 12 sites x {OFF-wrapped, ON} x {gcc -O2/-O1 -std=gnu11 -Wall -Wextra -Werror, gcc -O0 -Werror, gcc -O2 -march=native -Werror, clang -O1/-O0 -Wall -Wextra -Werror} = 144, all clean (F-6's `unused` holds under clang); C9's -mgeneral-regs-only, x86-64-v4, sandybridge cells clean at B16 and B32.
- **Amended C18 text legs:** 12 pairs: selector found (`rxa_mf1_vs0` -> w32), (c) passes incl. the byte count, guard lint passes with `<immintrin.h>`; (b) by `gcc -E -P` passes (2 pairs). Unamended C18 on the same pair: 0 selectors, "(c) a deleted line that is no SIMD FUNC's floor call", "a mover with no SIMD FUNC selector" (r68 V1 reproduced).
- **-O0 facts:** selector and the whole always_inline chain inline into `rxa_search` (no `vs0` symbol; 6 `pshufb`); region = file-wide target pragma, bracket = invisible byte count (EMIT-3).
- **F-13 machine code (SIMD-off rxa_search, gcc -O2, padding stripped):** `[0-9a-f]{32}` 0, `\b[0-9a-f]{32}\b` 0, `\d{32}` 0, `\w{20}` 20 lines: matches §2/§16 6b. The `\b` site wraps only the 31 class tests (the `\b` tests stay inline in the walk's `&&` chain; they read `rxa_mf1_n`, which `__body` does not take).
- §4.3's membership algebra and §4.2's block bound re-read by hand (K 16, 24, 31, 32, 64, 1000): reads exactly [p, p+K).
- Passed to lens seam (not mine): ofsskip's `fn_level_block` writes the helper's HEAD first, then its body; V's bracket must hold `__w32_b` BEFORE `__w32`'s head, so the lifted one writer needs a pre-head slot (or a second bracket).
Budget: 30 pcrec compiles; ~193 gcc/clang invocations.

CRITIC COMPLETE

