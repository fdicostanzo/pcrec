# PREMISE findings

Lens: premise. Subject: docs/design/memfn/target_seam.md rev 0 (e2f9793d1). Build tree W =
worktrees/crit-xarch @ 5b43f8e9a (memfn/ src/ identical to aeede1d16: `git diff --stat aeede1d16
5b43f8e9a -- memfn src lib cli` is empty). Kit branch K = 5b6cf41aa. Scratch artifacts under
premise/art, premise/zq, premise/prag.

## Findings

### PREM-1 CONFIRMED — "one variant = one mf_art (today's per-artifact kit state)" is false for compound artifacts
- § 2 line 42-43 ("The unit is ONE VARIANT = one `mf_art` (today's per-artifact kit state)"), § 3.
- Code: the art is per compile ATTEMPT (Job), not per artifact: W src/gen/memfn_sites.c:183-200
  (`job->mf = mf_art_begin(..., cx->opt->prefix, ...)`). A compound artifact has one art per part
  plus the shell: tests/compound/run_part_measures.sh:92 expects "MFMEAS roles '- f q ' (one per art)".
- Repro: `build/pcrec --features all -fmemfn-simd -p rx -o c1.c --pattern '^\s+|\s+$'` ->
  `RX_COMPOUND "split"`, per-part kit stamps `RX__F_MEMFN_FORMS`, `RX__Q_MEMFN_FORMS` (c1.c:171,346),
  part stems `rx__f_*`, `rx__q_*`, and a shell union `RX_RUN_WORDS -1` (c1.c:515).
- So a variant of a compound artifact is (parts+1) arts, and per-variant stamps compose with
  per-part stamps (variants x parts). The note never mentions compound artifacts. D155 addendum 5
  (decisions.md:9353, ruled) frames an ISA level as "one more part the controller selects among"
  (D163 part layout, compound_entries.md); the note departs from that ruled frame (variant = a
  prefix stem, dispatch = a hand-written entry) without citing or arguing it.
- Severity design. Effort: a § on compound x variant (unit, stems, stamp union) or adopt the
  D155-add-5 part frame. Blast: §2, §3, §4 stamps, §6 G2 sweep (compound streams).

### PREM-2 CONFIRMED — the variant stem `<prefix>_<vtag>` collides with the caller's prefix namespace and with the default variant
- § 3 lines 94-99.
- (a) pcrec's own derived names use a DOUBLE underscore (`rx__next_pos`, part stems `rx__f`,
  `rx__q`: c1.c above; a2.c:41,53), keeping single-underscore space for the caller. `rx_v3` is a
  legal caller prefix: `build/pcrec -fmemfn-simd -p rx_v3 -o b2.c --pattern '(?i)cat'` works
  and defines `rx_v3_search`. A program linking pattern A at prefix `rx` with variants {generic,v3}
  and pattern B at prefix `rx_v3` gets two `rx_v3_search` (duplicate symbol), violating G3.
- (b) "The default variant keeps today's stem (`rx`)" + "the public entries (`rx_search`, ...)
  become pcrec's dispatchers": with a list {generic, v3}, the generic variant's own entry and the
  dispatcher are both `rx_search`. §7 also calls `rx_<vtag>_search` for every variant, so generic
  needs a vtag in multi-variant lists, i.e. its names DO move there. The note has to say which.
- Probe (prag/tu.c): with generic at stem `rx_gen`, v3 at `rx_v3`, a hand dispatcher `rx_search`,
  one TU links and answers equal on 5 subjects; with generic at `rx` it cannot.
- Severity design. Effort small (pick `<prefix>__<vtag>` or similar, state the generic name).

### PREM-3 CONFIRMED — "emitted once" vs "per stem" is not a two-way split: the dispatcher's public contract is a third class
- § 3 line 99 ("Shared header types and `PCREC_*` macros are emitted once").
- Held part: the shared types (`rx_ctx`, `rx_iter`, `struct rx_info`, `rx_var`, `rx_matchfn`, ...)
  are FIXED names inside `#ifndef PCREC_RX_ABI_H` (a2.h:11-266); two prefixes in one TU compile
  clean (art/tu1.c = a2.c + b2.c, gcc -O2: 0 diagnostics).
- Not covered: the per-stem header items the CALLER sizes against: `RX_NCAPS`, `RX_RESUME_FRAMES`,
  `RX_TRAIL_FRAMES`, `*_FRAME_SIZE`, `RX_BUFFER_ALIGN`, and the per-stem anonymous
  `typedef struct {...} rx_buffers` (b2.h:268-281: `rx_v3_buffers`). The dispatcher `rx_search_in(...,
  const rx_buffers *)` must forward to `rx_v3_search_in(..., const rx_v3_buffers *)`: distinct
  types (needs a cast), and the frame macros a caller allocates by must be the MAX over variants
  (each variant is a separately planned matcher; frames are plan facts). Same for `rx_info`
  (which variant's engine/flags?), the per-artifact plan stamps `RX_ENGINE`, `RX_DFA_*`, `RX_REQ_*`,
  `RX_MEASURES`, `RX_SIMD_GUARDED_BYTES` (a2.c:4-31,371-385): per variant under the stem rule, but
  the unprefixed `RX_*` names are then the generic variant's, not the dispatching artifact's.
  Also `#define PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES` sit unguarded at the top of every .c
  (a2.c:2-3): "once per artifact", a third bucket again.
- The iterator: D155 add. 5 puts the dispatch choice in `rx_iter` (caller-held state); `rx_iter`
  (a2.h:224-234) has no field for it, so this is a `PCREC_ITER_LAYOUT` bump (a2.h:213) and an abi
  event the note does not name (D155 add. 5 says "no new caller struct", which holds, but the
  layout still moves).
- Severity design (abi surface). Effort: a classification table (shared / per-variant / dispatcher
  = union or max) in §3.

### PREM-4 CONFIRMED — `__builtin_cpu_supports` answers 0 (baseline) before libgcc's constructor: in an ifunc resolver and in an early constructor
- § 5 lines 142-146 ("'Once per process' is the CPU probe, which libgcc runs once (its
  `__cpu_model`)"; names "ELF ifunc" as a per-platform option).
- isa_evaluation.md:163 already records "A1s is unset before constructors run" and :169 "each
  `.so` links libgcc's `__cpu_model` and its constructor (BELIEVED a per-`.so` copy)"; the note
  drops both caveats.
- Repro (gcc 15.2, this Zen 4): prag/ctor.c, `constructor(101)` reading
  `__builtin_cpu_supports("x86-64-v3")` -> `ctor=0 main=2` (dynamic and -static); prag/ifr.c, an
  ifunc resolver using it -> picks the generic arm (`ifunc picked 1`). The kit's own driver
  calls `__builtin_cpu_init()` first (memfn/tests/run_g2_simd.py:345).
- Answer-safe (generic is correct) but a silent speed loss for any caller compiling/matching from
  a constructor, and the ifunc route is wrong without `__builtin_cpu_init()`. "Once per process"
  is "once per linked libgcc copy" (BELIEVED per `.so`).
- Severity speed / doc. Effort trivial: the dispatcher calls `__builtin_cpu_init()` (idempotent) and
  the note restores the two caveats. Other claims here HOLD: 0.44-0.59 ns (linux_results.md:23);
  Darwin answers 0 (requirements.md:407 N-4, isa_evaluation.md:137,163).

### PREM-5 CONFIRMED — the pragma form is GCC-only; clang ignores `#pragma GCC target` and fails to compile the variant
- § 5 lines 132-134, Q4 lean (line 226), § 2 line 73 ("never an attribute").
- Repro: prag/b2v3.c (the v3 variant of `(?i)cat`, guards removed, intrinsics headers at file
  top, `#pragma GCC push_options / target("arch=x86-64-v3")` region): gcc -O2 -Wall -Wextra clean,
  15 ymm, helpers inlined (matches the note's probe); `clang -O2 -c` (Ubuntu clang 21.1.8): 20
  errors, "always_inline function '_mm256_set1_epi8' requires target feature 'avx' ...".
- Clang is a compiler artifacts are built with in this project (README.md:52-53 Apple Clang
  caveats; linux_results.md prices clang throughout). Today's `-fmemfn-simd` artifact compiles
  under clang (art/a2.c: 0 errors).
- Fix that keeps "no kit change": pcrec emits a compiler-gated pair, `#ifdef __clang__ #pragma
  clang attribute push(__attribute__((target("arch=x86-64-v3"))), apply_to = function)` else the
  GCC pragma (prag/b2cl.c: clang 0 errors, 15 ymm, inlined; gcc 0 errors). That is a
  compiler-capability `#if`, the class §4 already exempts. The per-head-attribute alternative
  forces attributes into the kit's heads (prag/b2attr.c: attributing only the kit helpers leaves
  them out of line under gcc, 1 symbol), contradicting §2's "never an attribute".
- Severity design. Effort small.

### PREM-6 CONFIRMED — "MF_P_PORTABLE_ONLY becomes redundant" understates its readers; today SIMD admission is the GATE's policy class, not levels.def
- § 2 lines 56-61; § 6 line 152-154 ("no level is admitted ... `fn_selector` with no rung").
- Readers of the bit at W/K (git grep, excluding lanes): public header memfn/include/memfn.h:461;
  lib/pcrec.h:1134 (doc); src/gen/memfn_stamps.c:323 (`pcrec_memfn_policy`); src/core/internal.h:7455
  and src/gen/memfn_sites.h:109 (doc); memfn/src/gate.c:438-451 (`cl_policy`, `policy_classes`) +
  fields.def:137 (class PORTABLE) + every row's `[FLD_policy]` contract entry (vrun.c:498 `CM(NONE)
  | CM(SIZE)`, the scalar rows' `MF_ANY` in generic.c:848, runcmp.c:638, mismatch.c:276,
  ofsskip.c:907,987, precheck.c:477, pffind.c:393, finder.c:176, window.c:664); formhash.c:254,:291
  (main) and on K the new entry table carries a `policy` word per instance (K formhash.c:294-303,
  10 rows, all `MF_P_PORTABLE_ONLY`; :413 `mf_art_begin(..., e->policy, ...)`); tests
  (g2_gen.c, g2_simd_gen.c:371, g2_win_gen.c x9, arm_fixtures.c, proof_check.c, proven_check.c) and
  sabotages S722, S1224.
- Mechanism: whether a SIMD PREFIX row is chosen at all is decided by the walk's FLD_policy class
  (vrun.c:498; ofsskip.c:476-489 `fn_select`), and `fn_rungs` (ofsskip.c:508-522) ALWAYS puts the
  chosen row in rung[0] (nr >= 1 whenever a PREFIX row is chosen). So "empty features -> nr == 0"
  holds only if the `needs`-subset test becomes a gate field the walk reads (a new contract field
  on every SIMD row, fields.def + gate.c), not a filter over levels.def. Retiring the bit is
  then a public memfn.h change, a pcrec_memfn_policy change and a row-contract edit across ~10 rows;
  the word itself stays (INLOOP, SIZE_LEANING share it).
- Severity design/maintenance (claim of a free simplification). Effort: name the gate field and
  the reader list.

### PREM-7 CONFIRMED — "headers ... a fact like today's MF_INC_* bits; pcrec writes them once at file scope" has no existing path: pcrec decides its includes BEFORE the kit renders
- § 2 line 68; § 4 rows `fn_level_block`/`vany_level` ("the header goes to `headers`").
- MF_INC_* has ONE bit, `MF_INC_STRING_H` (memfn.h:469); the SIMD headers are written by the kit
  INLINE, inside the guard (ofsskip.c:569-572 via `art->simd_inc`, vany.c:157), never as a fact.
  pcrec's prologue decides `<string.h>` from its OWN facts (emit_dfa.c:15660-15685, written at
  :15946) and the kit bit is only an after-the-fact assertion (memfn_sites.c:1001-1003: "the
  kit's text calls <string.h> functions the prologue did not include" = internal error). The
  DFA path writes the prologue after its body but before file-scope kit blocks (emit_dfa.c:15955
  comment), so a returned header fact needs either pcrec to predict it (a pcrec rule per level)
  or a deferred prologue. A new mechanism, not "like today".
- Severity design. Effort small/medium (name it; or keep the kit's include inside the variant
  region, which is legal inside a pragma region and needs no new fact).

### PREM-8 CONFIRMED — G4's "the one callback today, `simd_open`/`simd_close`" is false
- § 2 lines 75-77 (and G4 line 35 "no pointer, callback").
- memfn.h:880-891 (sink: puts, vprintf, cmt_open, cmt_close, stamp, cstr, comment_byte with an
  `extra_escape` callback, legend_byte, stamp_int, simd_open, simd_close) and :1005-1017 (hooks:
  `on_cand` and `note` write pcrec TEXT into the kit's text mid-render through a sink; `member`,
  `table_name`, `fn_name`, `note_tag` return pcrec strings on demand). §2 keeps "site facts, hooks"
  unchanged and §3 relies on `table_name`. The text-injection hooks (`on_cand`, `member`, `note`)
  are the ones a serialized seam must turn into placeholders; the note's round-trip argument does
  not reach them.
- Severity doc/design (G4 is the seam's stated principle-9 claim). Effort: list them and their
  serialized form (most are value-able: names, or placeholder tokens).

### PREM-9 CONFIRMED — the [XARCH-DEV] quote elides the ruled build-time mode
- § 0 lines 18-20 quote "[...]"; the elided text (plan.md row [XARCH-DEV]) is "Build time: pcrec emits the
  build target's variant. Run time: ...". The note's default is `{generic}` (§5 line 147, §6) and
  `-fno-memfn-simd` "maps to the generic target" (line 60, 157), but it never says what
  `-fmemfn-simd` (today: w16 at plain x86-64, w32 at a `-march=x86-64-v3` consumer build, art/a2.c
  :89-171) maps to, nor how a caller asks for the ruled "build target's variant". With `generic`
  = empty features, today's `-fmemfn-simd` SSE2 rung (baseline on every x86-64) is lost unless a
  `x86-64` (v1, sse2) target exists in pcrec's table; §2's family column has `x86-64` but §5/§6
  never place it.
- Severity design (ruled text). Effort small: map the switch and the build-target mode to list
  values.

### PREM-10 CONFIRMED (doc) — line cites drift on the kit's branch
- runcmp.c:533-535 (§3) is K runcmp.c:542-544 (9 lines inserted at :492, `run_cmp_row`);
  formhash.c:232 `mf_tbl` (§3) is K formhash.c:240, and K adds a second fixed test-only name
  `mf_fn` (K formhash.c:256). All other cited lines are byte-identical on K (ofsskip.c, vany.c,
  window.c, precheck.c, levels.def unchanged: `git diff --stat 5b43f8e9a 5b6cf41aa -- memfn/src`
  touches only CLAUDE.md, formhash.c, kit.h, runcmp.c).
- Severity doc. Effort trivial.

### PREM-11 CONFIRMED (doc, minor) — §3's enumeration misses kit file-scope emitters (all prefix-built, so the conclusion holds)
- Uncited file-scope emitters: generic.c:646 (`static inline <fn>(`, fn from pcrec's `fn_name`
  hook, generic.c:633), window.c:2423 (`static inline size_t <fn>(`), window.c:2686
  (`static const unsigned char <prefix>_mf<h>_sh[256]`), window.c:2136 (`<prefix>_mf<h>_ofsskip`,
  a function the KIT names from art->prefix), vany.c:115 (`<fn><suffix>`, stand-alone kernel),
  and compose.c:1404-1410 `mf_reach_table`: EXTERNAL-linkage `unsigned long <st>[n]`,
  `const char *const <st>_row[]`, `const unsigned <st>_n` (harness lever only; stem
  `PCREC_HARNESS_PREFIX reach_<prefix>`, memfn_sites.c:206). The note's "exceptions are block-scope
  or test-only" should add this harness-only external object.
- Severity doc. Effort trivial.

## PROBED-AND-HELD

- §3 core claim: every kit file-scope name is built from a pcrec-given string. Grep of every
  string literal containing `static`/`const`/file-scope heads in memfn/src (9 emitters) + 18 real
  artifacts (12 patterns x SIMD off/on at `-p zq`, -O0 objects): `nm` shows 0 symbols lacking
  `zq` except libc `memchr`/`__stack_chk_fail`; text scan shows 0 unprefixed file-scope decls in
  .c besides `PCREC_FEATURE_*` and the shared `rx_*` ABI block. `wf_nm` OOM fallback "mf"
  (window.c:2112) is the only fixed name, unreachable in practice.
- §3: prefix substitution is total: `sed s/rx_v3/rx/` of b2.{c,h} equals a2.{c,h} byte for byte.
- §4 counts at aeede1d16, 5b43f8e9a and 5b6cf41aa: `#if __AVX2__` 1, `__AVX2__` 3, `__SSE2__` 4,
  `__builtin_cpu_supports` 6, `target(` 3, `__builtin_cpu_init` 2, files as stated. Wider grep
  (`__x86_64__|__aarch64__|__ARM_NEON|__SSSE3__|__SSE4|__BMI2__|__AVX512|__ILP32__|cpu_supports|
  ifunc`) over memfn/src, memfn/include, src, lib, cli: only levels.def:42,45. pcrec's emitted
  `#if` set (18 distinct literals in src/lib/cli) has no CPU test: ABI guards, `__has_attribute`,
  test hooks. So "all emitted CPU guards come from levels.def" HOLDS.
- §4 cited lines (ofsskip.c:547-555, 568-575, 590-611, 617-622, 686-687; vany.c:146-158, 157,
  178, 184-198, 210-215; window.c:2107-2112; ofsskip.c:158-164; precheck.c:318) point at the
  stated code at W.
- §4 "rung chain is a length test": vrun.c:354 / vany.c:159 entry test `if (pos >= n || n - pos <
  W) return <fall>(...)`; fall = next rung (ofsskip.c:686-687). Holds.
- §6 "`fn_selector` with no rung is already the one plain call": ofsskip.c:596-611 with nr == 0
  writes head + `return <fn>__body(...)` + `}`; art/a1.c:89-92 (SIMD off) shows exactly that.
  Holds GIVEN no PREFIX row is chosen (see PREM-6).
- §5 pragma probe reproduced under gcc 15.2 (0 diagnostics -Wall -Wextra, 15 ymm, no out-of-line
  helper); `__builtin_cpu_supports("x86-64-v3")` works under gcc 15 and clang 21; a two-variant
  TU with a dispatcher answers equal to both variants on 5 subjects (prag/tu.c, bad=0).
- §5 0.4-0.6 ns (linux_results.md:23 "0.44-0.59 ns"); Darwin answers 0 (requirements.md:407,
  isa_evaluation.md:137,163). D155 add. 5 quote and match_api §5.3 framing match decisions.md:9353.
- endianness: kit word compares are endian-neutral by construction (runcmp.c:45,72), so
  `target.family` needs no byte-order fact today.
- emit_sweep.py has `--ref` and `--extra` (scripts/emit_sweep.py:3099,3152), as §6 uses.
