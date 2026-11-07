# PROBE findings

Lens: probe (apply target_seam.md rev 0 by hand to build/pcrec's real output, main 5b43f8e9a,
gcc 15.2.0, Zen 4). Scratch: /var/tmp/pcrec-pcrec/scratch/crit-xarch/probe/ (tools/xf.py = the §4
transform, tools/disp.py = a §5 dispatcher, tools/mk.sh + tools/run.sh = build+answer check,
tools/drv.c = the driver, w/<name>/ = per-pattern artifacts, vany/ = the find-any kernel probe).

Transform applied: generic variant = `-p rx_gen` SIMD-off text; v3 variant = `-fmemfn-simd -p rx_v3`
with every `#if defined(__x86_64__)...` arm stripped (helpers kept for admitted rungs w32+w16, each
selector reduced to its top admitted call), its `<emmintrin.h>`/`<immintrin.h>` moved to one file-top
`#include <immintrin.h>`, wrapped in `#pragma GCC push_options / target("arch=x86-64-v3") /
pop_options`; public `rx_*` entries written as `__builtin_cpu_supports("x86-64-v3") ? rx_v3_X : rx_gen_X`;
one `rx_info` with `.next = rx_next`. Header = `rx.h` + `rx_gen.h` + `rx_v3.h` (the shared
`PCREC_RX_ABI_H` block dedupes itself).

## Findings

### PROBE-1 — the §5 pragma form `target("arch=x86-64-v3")` does NOT compile when the consumer's own -march is above or beside v3 (`-march=native` on this Zen 4, `-march=x86-64-v4`, `-march=znver4`, even `-mavx512vl`/`-mavx512f`) — CONFIRMED
Severity: answer-adjacent (hard build failure of a correct artifact; G1 fails). Effort: small (spelling
change) once named. Blast radius: every multi-variant artifact; every kit SIMD form. §5 "Attributes",
§10 Q4, G1's "measurable form".
- Repro: `w/cat/comb.c` (pattern `(?i)cat`): `gcc -O2 -c comb.c` OK; `gcc -O2 -march=native -c comb.c`
  -> `error: inlining failed in call to 'always_inline' 'memcpy': target specific option mismatch`
  (glibc `string_fortified.h:26`, Ubuntu's default `_FORTIFY_SOURCE=3`). With `-U_FORTIFY_SOURCE`,
  or at `-O0 -march=native`, it still fails, now on the intrinsics:
  `emmintrin.h:1316 ... '_mm_and_si128': target specific option mismatch` (also `_mm_cmpeq_epi8`,
  `_mm_movemask_epi8`). Same on the find-any kernels (`vany/t.c`, 24 errors at -march=native).
  The untransformed artifact compiles at every one of these flags (it is today's portable shape).
- Cause: `arch=x86-64-v3` REPLACES the TU's ISA set for the region; a callee defined at file scope
  under the TU's larger ISA (the intrinsic headers are not wrapped when the TU already has the ISA;
  glibc's fortified `memcpy` is always_inline) is not a subset of the region's ISA, so gcc refuses
  the always_inline. The note's own probe (§5) ran only at default `-march`, which is the one case
  that cannot show it.
- What works (checked): an ADDITIVE ISA list, `#pragma GCC target("avx2,bmi,bmi2,fma,lzcnt,movbe,
  popcnt,f16c,xsave,sse4.2,ssse3,sse4.1,cx16")`, compiles at -O0/-O2 x {default, -march=native,
  x86-64-v4, x86-64-v2, -mgeneral-regs-only, -mno-sse2} (0 errors each), and answers match
  (2,360,816 checks, 0 bad, at -march=native). Its unstated consequence: under a TU `-march=native`
  the "v3 variant" may also carry AVX-512 code, so "a variant is planned for its declared target"
  only holds when the consumer compiles at or below the generic target. The note's target table
  "attribute string" (§5) must be this additive form, and the "x86-64-v3 probe string" then describes
  the dispatcher's condition, not the code's ISA. §7's "every variant on its own arch" tests must add
  a `-march=native` (above-target) compile cell; today's G2 builds (run_g2_any.py BUILDS) never compile
  above the guarded level.

### PROBE-2 — the §5 pragma is gcc-only; clang ignores `#pragma GCC target` and the artifact fails to compile — CONFIRMED
Severity: answer-adjacent (build failure; README.md:52-54 names Apple Clang as a consumer compiler;
the untransformed artifact compiles under clang 21.1.8 with 0 errors). Effort: small. §5, §10 Q4
("pragma, since it needs no kit change").
- Repro: `clang -O2 -c w/cat/comb.c` -> 20+ errors, first `always_inline function '_mm256_set1_epi8'
  requires target feature 'avx', but would be inlined into function 'rx_v3_mf1_ofsskip__w32'`.
- Works: `#pragma clang attribute push (__attribute__((target("avx2,..."))), apply_to = function)` /
  `pop` -> 0 errors at -O0/-O2/-O2 -march=native, answers 2,360,816 checks 0 bad. So the "no kit change"
  argument for Q4 survives only if pcrec emits a compiler-capability `#if defined(__clang__)` around two
  pragma spellings (allowed by §4's own compiler-capability carve-out), or per-head attributes are used.
  The note does not mention either; Q4's leaning should name the compiler question.

### PROBE-3 — "the default variant keeps stem `rx`" and "the public entries `rx_search`... become pcrec's dispatchers" collide; G3 fails as written — CONFIRMED
Severity: design/doc. Effort: small (a naming rule). §3 last paragraph.
- Repro: `w/cat/stemrx.c` = generic variant at stem `rx` + v3 at `rx_v3` + dispatchers:
  `gcc -c` -> `error: redefinition of 'rx_search'` (and rx_match, rx_match_caps, rx_search_in,
  rx_match_in, rx_match_caps_in, rx_next, rx_next_n, rx_next_pos, rx_valid_upto; rx_info too).
- §3 says the default variant keeps the stem so G2 holds with one target, AND that with several
  variants the public names are the dispatcher's. Both are true only if the generic variant's stem
  CHANGES (e.g. `rx_gen`, as probed) the moment a second variant is listed. So "names of the default
  variant do not move" holds only for the one-target list; the note should say which stem the generic
  variant takes in a multi-variant list (it is the variant a caller would call directly to force
  portable code; §7 tests call it).

### PROBE-4 — G3 renames and duplicates the note does not mention — CONFIRMED (list)
Severity: doc/design. Effort: small. §3 ("pcrec's own names follow the same stem"; "Shared header
types and PCREC_* macros are emitted once").
Running pcrec with `-p rx_v3` renames the whole artifact cleanly (diff of `-p rx_v3` vs `-p rx` output
after `s/rx_v3/rx/;s/RX_V3/RX/` = only the `#include` line), so the stem approach WORKS. But the
per-prefix (not shared) surface, which a dispatcher must reconcile, is unnamed in the note:
1. `<prefix>_buffers` is a PER-PREFIX anonymous-struct typedef (`typedef struct {...} rx_buffers;`
   after the shared block). The public `rx_search_in(..., const rx_buffers *)` cannot pass its
   argument to `rx_v3_search_in(..., const rx_v3_buffers *)`: gcc 15 `error: passing argument 5 of
   'rx_v3_search_in' from incompatible pointer type` (w/vm/combnc.c). The dispatcher needs a cast,
   and is then only correct if every variant's `RX_*_RESUME_FRAMES / TRAIL_FRAMES / *_FRAME_SIZE /
   BUFFER_ALIGN` equal the public ones (they do today: w/vm RX_GEN_RESUME_FRAMES 1 = RX_V3_RESUME_FRAMES 1,
   ALIGN 8 = 8). Since a variant is "a complete matcher planned and priced for one target", nothing
   keeps them equal; the public sizes must be the max over variants, and the note must say so.
   Same for `<prefix>_iter_buffers`.
2. `const struct rx_info <prefix>_info` per variant: three exported `rx_info` objects (rx_info,
   rx_gen_info, rx_v3_info) in my build; which variant's `engine/scan/prefilter/search_form/
   match_form/flags/findings/measures` the PUBLIC `rx_info` reports is unstated. `.measures` and
   `RX_MEASURES` necessarily differ per variant under §2 (`ms` per target). The note's §4 covers only
   MEMFN_FORMS per variant; every `<PREFIX>_*` stamp (RX_ENGINE, RX_DFA_*, RX_REQ_*, RX_RUN_WORDS,
   RX_MEMFN_LIBC, RX_SIMD_GUARDED_BYTES, RX_FINDINGS, RX_MEASURES, RX_TUNE...) is likewise duplicated
   under `RX_V3_*` and none is named.
3. `<PREFIX>_SIMD_GUARDED_BYTES` (match_api.md table row, limits.md [8.3¶2], tuning.md [2.43¶3a],
   tests/memfn/simd_guarded_check.py + simd_bounds.tsv) is not mentioned anywhere in the note
   (`grep -ci guarded` = 0). With no `#if` arms its meaning ("the guarded text, compiled only at
   -march=L") is gone; the note should retire or redefine it and name its reader.
4. `--emit-main`: `main()` must be emitted once, outside all variants (a per-variant `--emit-main`
   gives a duplicate `main`), and it changes the kit's stamp: `RX_MEMFN_LIBC` becomes
   `"fprintf,memchr,printf,strlen"` and `.flags` 2 vs 0 (diff of p1 with/without `--emit-main`), so
   "the art's stamp values" are not purely the art's.
5. Size: the {generic, v3} object for `(?i)cat` is text 6019 / data 672 (comb.o), vs the §8 stand-in
   (2390 + 2924 = 5314 text, data 224 each). The stand-in omits the dispatchers (10 entries) and the
   third `rx_info` (data triples, not doubles). §8's measurement should compile the real two-variant
   shape, or add the dispatcher+info term.
Held: no file-scope typedef, macro, static or table collides once the stem differs (nm of comb.o:
all `rx_gen_*` / `rx_v3_*` / `rx_*` distinct; block-scope `static const` tables get distinct
`.N` local symbols); `#define __has_attribute` repeats are guarded; the shared ABI block dedupes.

### PROBE-5 — `-fmemfn-simd` with the default list `{generic}` loses the w16 rung on every x86-64 compile (an unstated semantic change of the opt-in axis) — CONFIRMED (by text + today's artifact)
Severity: speed + doc. Effort: small (a rule). §2 (empty features = generic), §6.
- Today: `build/pcrec -fmemfn-simd -p rx --pattern '(?i)cat'` stamps `RX_MEMFN_FORMS "vrun@w32+w16"`,
  and tuning.md [2.43¶3a] promises "the 16-byte arm needs SSE2 on x86-64 (every x86-64 compile)".
  Under §2/§6 the default list is `{generic}` with EMPTY features, so no level is admitted; the note
  says `-fno-memfn-simd` maps to the generic target but never says what `-fmemfn-simd` maps to. If it
  maps to the default list, a `-fmemfn-simd` artifact equals the SIMD-off one (FORMS "none") and the
  w16 helper (live at default -march today; text 2620 vs 2390 SIMD-off) is gone. If it maps to an
  `x86-64` baseline target (features sse2), that target is not in the note's table and the artifact is
  no longer compilable by a non-x86 compiler (PROBE-6). Either way the spec sentences tuning.md
  [2.43¶3a] and limits.md [8.3¶2] change and are not listed as the SIMD-on abi event's spec hunk.

### PROBE-6 — a multi-variant artifact is no longer portable C; today's SIMD-on artifact is — CONFIRMED (partly by construction)
Severity: design/doc. Effort: decision. §10 Q1, §6 ("-fmemfn-simd artifacts DO move").
- tuning.md [2.43¶3a]: "any other target, or -mgeneral-regs-only, compiles the scalar arm, so the
  artifact still compiles and answers everywhere." The transformed artifact has an unconditional
  `#include <immintrin.h>`, `#pragma GCC target("arch=x86-64-v3")` and `__builtin_cpu_supports(
  "x86-64-v3")`: a non-x86 compiler cannot compile it (no aarch64 cross gcc here to run it; the three
  constructs are x86-only by definition; clang shows the pragma half, PROBE-2). §10 Q1 frames this as
  "mixed-family lists"; the actual change is that the family is now fixed at GENERATION time, where
  today it is chosen by the consumer's compiler. The note should state it as a contract change
  (spec hunk) or keep a family-capability `#if __x86_64__` around the non-generic variants and the
  dispatcher (a family test, not a CPU-level test; §4 is silent on whether that is allowed).

### PROBE-7 — D165 item 5 ("no trampoline"; one exported call per match) vs the §5 dispatcher; and the iterator "keeps the choice" has nowhere to keep it — CONFIRMED (shape) / design
Severity: design/doc. Effort: small. §5 "Dispatch", §0 D155 add. 5 quote.
- `objdump -d comb.o` (O2): `rx_next` = `mov __cpu_model; testb $0x2,8(%rax); je; jmp rx_v3_next /
  jmp rx_gen_next` — a tail-jump trampoline. `rx_info.next` points at it. D165 item 5: "`rx->entries->next`
  is the artifact's own function pointer, no trampoline". The cost is one load+branch+jmp per match,
  not a second frame, but it is the shape D165 ruled out by name; the note should argue it (ifunc
  removes it on ELF; a const `rx_info` cannot hold the picked pointer under §5.3's no-static rule).
- Today's `rx_iter` (PCREC_ITER_LAYOUT 3: hdr, rc, flags, s, n, lo, vars, nvars, bufs) has no field for
  a dispatch choice; `hdr`'s bits are fully used (tag/layout/state/opt mask); only `flags` has spare
  bits. "The iterator keeps the decision in its caller-held state" (§5, D155 add. 5) is either a
  layout change (PCREC_ITER_LAYOUT bump: the SHARED rx_iter block, so every artifact moves, against
  G2) or an unnamed `flags` bit. With the tail-jump shape above it is not needed at all. Unstated.
- Iterator answers: one shared `rx_iter` type serves both variants today: find-all via `rx_next`,
  `rx_gen_next`, `rx_v3_next` = oracle on every subject (part of the counts below). D165's S buffer
  is not built at 5b43f8e9a, so S per variant could not be measured.

### PROBE-8 — §9.3 "a kit byte move under a non-default target is a pcrec abi event only for artifacts that list that target" is false for the iterator's S — SUSPECTED (from D165 item 4's text; S not built yet)
Severity: design. Effort: small (a sentence). §9 Q3.
- D165 item 4: `rx_iter` is ONE fixed unprefixed type whose inline buffer S is "the max over
  artifacts of what one artifact holds", "a public-header constant"; "a row outgrowing S raises S = an
  abi event". With variants, S must be the max over every target in pcrec's TARGET TABLE (any artifact
  may list any target), so a new SIMD form's state need under e.g. v4 can raise S for every artifact,
  including the default `{generic}` ones, whose bytes then move (the shared `rx_iter` block is in every
  header). Confirm when S lands: derive S at {generic} and at {generic, v3, v4}; if they differ, §9.3
  and G2's "one target = the stamp commit's bytes" need the S carve-out.

## PROBED-AND-HELD

- Answers: 7 patterns reaching kit SIMD forms (all `vrun@w32+w16`, the only SIMD form any pcrec site
  reaches today): `(?i)cat` (DFA), `(?:(?i:abs)|(?i:ab)S)` (window table row PAIR/B-fn), `(?i)cat(\d+)`
  (VM + captures), `(\w+)(?i)cat` (VM, file-scope class bitmap), `(?i)hello.*(?i)world`, `(?i)ab`,
  `(?i)abcdef`. Each: dispatcher, rx_gen_*, rx_v3_* (run directly on this Zen 4) and the untransformed
  artifact at -march=x86-64-v3 vs the untransformed artifact at default -march (oracle): `_search` at
  every start position, `_match` at every position, full find-all through rx_iter, random subjects
  0..260 bytes with planted hits. 2,360,816 checks per pattern at -O2 (2,366,960 for `(?i)abcdef`),
  plus `(?i)cat` at -O0 and under clang (pragma clang form) and at -march=native (ISA-list form):
  ~19.0M checks, 0 mismatches. No answer moves.
- G1 at default -march: the stripped kit text has 0 CPU `#if` lines (the 10 left are pcrec's
  `__has_attribute(noclone)`), `immintrin.h` once at file scope + the pragma compiles clean at -O0
  and -O2 with -Wall -Wextra for all 7 patterns; at -O2 the w32 and w16 helpers inline into
  `rx_v3_search` (no `ofsskip` symbol in nm; 15 ymm instructions in rx_v3_search; 0 xmm/ymm in
  rx_gen_search).
- Find-any (vany.c, NOT ROUTED: no pcrec pattern reaches it, run_g2_any.py:5-7): 8 kernels rendered by
  memfn/tests/g2/g2_any_gen.c (levels none/w16/w32/both), transformed the same way: 11,256,928 checks vs
  the untransformed kernels at -O0 and -O2, 0 bad. vany emits `#include <emmintrin.h>` per rendering,
  so moving headers to a returned fact is a real dedupe, as §2 says.
- gcc 15 inlining rules: a generic-region `static inline` (and `always_inline`) helper DOES inline into
  an `arch=x86-64-v3` region function (gcc 15 allows arch mismatch for an ISA subset); a v3-region
  `static inline` called from generic code is emitted out of line (safe only behind the dispatch); a
  v3-region `always_inline` called from generic code is a hard error. pcrec's always_inline helpers
  (`rx__step`, `rx__one`, `rx__one_call`) are per-variant and called only inside it, so none bites in
  the emitted shapes (inl/t2.c, 12 compiles).
- §4 "w32 falls to w16 is a length test": inside the v3 variant both helpers survive and w32's entry
  test calls w16 for `n - pos < 34` (ofsskip.c fn_define, `fall = names[j+1]`); exercised by the
  0..260-byte subjects above, 0 mismatches.
- One `rx_iter` type serves every variant (fixed unprefixed type, D165 item 3); the shared
  `PCREC_RX_ABI_H` header block dedupes when rx.h, rx_gen.h and rx_v3.h are all included.
- `-mgeneral-regs-only`, `-mno-sse2`, `-march=x86-64-v2`, `-mavx2`, `-mbmi2` TUs compile the
  `arch=` form clean (it fails only above/beside v3, PROBE-1).
- Compile count used: ~130.
