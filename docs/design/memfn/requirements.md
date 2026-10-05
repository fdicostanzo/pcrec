# memory-functions: R1, THE REQUIREMENTS

Owner row: `[MEMFN]` (docs/dev/plan.md), step R1. Lane `memfnreq`,
2026-10-04, written from main at cdd12942. Docs and one small probe only;
nothing under `src/`, `cli/`, `lib/` or `tests/` changes.

**R1b, ISA selection and checking, is `isa_selection.md`** (lane memfnisa,
2026-10-04): the dynamic, declared-ISA and hybrid options with Mac
per-call costs, a first-match selection table, RB-10..RB-13, N-12..N-14,
rubric rows H-14..H-16, and one Linux script (`probes/linux_run.sh`) that
also runs §2.6's owed probe.

**What this is:** the requirements an implementation of byte search and
compare kernels ("memory-functions") must meet so that pcrec can later
EMIT its kernels into self-contained generated C, written so that EXISTING
open-source projects and a build of our own can be scored against them on
equal terms (R2, the survey lane). **What this is not:** a survey (§5.3
only names candidates as pointers), a design, or a change to pcrec's
emission. D91 stands: nothing here moves an emitted byte.

The hard constraint every requirement answers to (CLAUDE.md, top): the
generated artifact is self-contained gcc-dialect C with no runtime
dependency on pcrec. Two further shipped contracts bind any kernel that
reaches an artifact: **match_api.md §5.3** (a generated matcher holds no
mutable state of its own, a BINDING contract on future emitters) and
**TS-1** (`make test` fails an emitted file carrying any non-const static
object or any non-reentrant or allocating libc symbol).

---

## 0. Findings first

1. **On the Mac (M1, libSystem) the per-call cost of `memchr` is small.**
   It is a flat **1.63 ns** per call up to 16 bytes. The best inline form
   runs **0.97-1.31 ns** and the harness loop alone costs 0.33 ns (§2.4).
   Our own kernel behind `noinline` costs **1.95 ns**, about the same as
   libc's. So the Mac call term is about 0.3-1 ns, not the ~3.4 ns that
   k82diag measured for glibc on Linux. That matches k82diag's note that
   "Mac does not reproduce the term". **The decisive number is the Linux
   one, and it is OWED** (§2.6, the exact protocol).
2. **The ~10 ns pair-arm floor is two calls AND two passes, and only
   fusion removes both.** Two libc calls cost 3.27 ns at n ≤ 16 against
   **0.96-1.46 ns** for one fused inline two-needle pass (gcc, n 8-16). Fusion also wins on long
   spans: at 4 KiB the fused pass costs 131 ns (gcc) or 116 ns (clang)
   against 208 ns or 203 ns for two calls, because the span is read once.
   On a hit at offset 0, the second libc stream still reads its whole span
   (6.2 ns against 0.98 ns fused). That is k82diag's overshoot in small
   form. **A fused multi-needle kernel is the requirement. A cheaper call
   is not.**
3. **An inline SCALAR byte loop is the wrong short-span form on this box.**
   It loses to libc `memchr` from 2 bytes (gcc) or 4 bytes (clang) up,
   at ~0.65 ns per byte. D91's corollary ("a proven-short window earns
   an inline scalar scan") holds only below that length. Above it, the
   short form must be loop-free word or vector loads: two overlapping
   8-byte words cover 8..15 bytes in 0.97 ns. The same holds for a vector
   loop's own byte-loop TAIL, which costs 4.5-5.9 ns at n = 12 against
   1.0-1.8 ns loop-free. **A short-span path with no loop and no call** is
   therefore requirement RB-4, not an optimization.
4. **Branch shape is a compiler outcome, and it matters.** One loop-free
   short path, compiled by clang, costs **6.6 ns** when its result feeds
   the next call's address, against 1.8 ns when it does not. gcc's build of
   the same source costs 1.0 ns. The likely cause is clang if-converting
   the exits into `csel` (8 against 3 in the disassembly; BELIEVED, not
   proven). The library must make branch shape controllable or verified
   per compiler (N-8).
5. **Runtime dispatch is not available to emitted code, and it is not
   needed for the baseline tier.** GNU ifunc is ELF-only (there is none on
   Mach-O). A dispatch-once function pointer is a mutable static, which
   §5.3 and TS-1 forbid. SSE2 is baseline on x86-64 and NEON (ASIMD) is
   baseline on AArch64, so the 16-byte tier needs no dispatch on either
   target. Wider tiers (AVX2, AVX-512, SVE) can reach an artifact only
   through the CONSUMER's compile flags (`-march`), which pcrec does not
   control (K24's lesson: "pcrec cannot dictate its users' CFLAGS"). Runtime
   dispatch is therefore a property of the library's own out-of-line form
   only (§2.5 RB-3, RB-8). *Narrowed by isa_selection.md §0 item 4:
   Apple clang now lowers multiversioning to a dyld-resolved
   `__func_variants` table on Mach-O, so the reason is "toolchain-
   dependent", not "unavailable". The conclusion stands.*
6. **Licence is a gate, not a score.** Text that pcrec injects lands in
   every user's generated artifact. A licence that requires its notice in
   "all copies or substantial portions" (MIT, BSD, Apache-2.0's NOTICE)
   follows that text into users' programs, unless the project grants an
   output exception. LLVM's exception covers code embedded in COMPILED
   object form; whether any such exception covers emitted SOURCE is part
   of Q1. pcrec's own LICENSE is MIT
   and does not say what licence generated output carries. **That is a
   question for Frank before any adoption** (§7 Q1).

---

## 1. The function menu

### 1.1 Common semantics (bind every function below)

- **S-1 Spans, not strings.** Every input is `(const unsigned char *s,
  size_t n)`. Nothing is NUL-terminated. `n == 0` is legal for any `s`,
  including NULL, and returns "absent". (C's own `memchr(NULL, c, 0)` is
  UB. The library must not inherit that.)
- **S-2 Never read outside `s[0..n)`.** This applies even within a page and
  even in one vector load. It is ASan-, Valgrind- and guard-page-clean.
  This is compare_stack.md P8 (the subject-end guard) stated for the
  library. The overlapping final block (a load that ends exactly at `n`)
  and loop-free overlapping short loads are the sanctioned ways to avoid
  a scalar tail. An aligned over-read "because it cannot cross a page" is
  REJECTED: C has no such guarantee and ASan flags it (memcmp_lowering_study
  §10).
- **S-3 No alignment requirement** on `s`. A kernel may align internally,
  but only by loads that stay inside the span.
- **S-4 Return convention.** The core forms return an INDEX in `[0, n]`,
  with `n` meaning absent. Forward forms return the lowest matching
  index; reverse forms return the highest, still with `n` meaning absent.
  An index composes with pcrec's position loops (`pos = f(s, pos, n)`) and
  avoids NULL pointer arithmetic. A `memchr`-compatible pointer wrapper is
  a nice-to-have, not a substitute.
- **S-5 Resumable without state.** Searching from `pos` is a call on
  `(s + pos, n - pos)`, or an equivalent `(s, pos, n)` form. There is no
  hidden cursor, no context object and no per-call setup the caller must
  repeat.
- **S-6 Pure.** No writes outside the return value. No global mutable
  state, no `errno`, no locale, no allocation, no I/O. Reentrant and
  thread-safe by construction (match_api.md §5.3, TS-1).
- **S-7 Operands.** A byte is `unsigned char`. A byte SET is a 256-bit
  bitmap (`uint64_t[4]` or `unsigned char[32]`). A CUBE is `(K, T)` with
  membership `(x & K) == T` (compare_stack.md P2; `pcrec_cube_of` is the
  single source in `src/core/cpset.c`). A literal is `(bytes, L)`, and a
  masked literal adds a per-position `(K_i, T_i)`.

### 1.2 The operations

`site` cites compare_stack.md §2 rows (at its 897a97f0 inventory plus its
S4 annotations). "In-loop" marks D91's second budget: a site that may run
many times per match, inside the pattern.

| id | operation | exact semantics | pcrec sites | value outside pcrec |
|---|---|---|---|---|
| **F1** | `find_byte` | the first `i` with `s[i] == c` | §2.4 `DFA_PF_MEMCHR` (rest of subject); `emit_attempt`'s `\n` for `(?m)^`; `pcrec_emit_req_byte_check` (REQ_BYTE); `<p>_ofsskip`'s scan member at offset k*; the exact stream of the run pre-check (`<p>_reqrun`) | universal (`memchr`) |
| **F2** | `find_any2` / `find_any3` | the first `i` with `s[i]` equal to one of 2 (or 3) bytes. ONE pass: no per-stream overshoot | the run pre-check's TWO leapfrogged streams for a caseless scan member (S4 C3, the K82 pair arm, about 10 ns on glibc); `pf_emit_bcls` for 2-3-member escape sets (`{u,U}`, `union-select`) | high (Rust `memchr2/3`, tokenizers, CSV) |
| **F3** | `find_cube` | the first `i` with `(s[i] & K) == T` | P2 at L3: S4(b)'s cube scan; a fold pair is K = 0xDF, so one compare per vector does F2's caseless case | medium (case-insensitive byte find) |
| **F4** | `find_in_set` | the first `i` with `s[i]` in a 256-bit set | `pf_emit_bcls[_bounded]` (`can_begin_match[]` table walk, one load per byte); the `byte-class` prefilter of the WAF cells (§6.3) | high (`strpbrk`/`memcspn` shape, lexers) |
| **F5** | `skip_in_set` (span) | the first `i` with `s[i]` NOT in the set (the run's end) | **in-loop**: `dir_fwd_skip` (`stay<K>` per DFA state); the scan edge (`pcrec_scanedge_dfa`, a counted class run); `vm_cursor_rep` greedy class runs; studies/simd1 §15 run extension (classify + clz, 2-3x over a table loop) | high (`strspn`, whitespace/identifier skipping, JSON/CSV) |
| **F6** | reverse forms: `rfind_byte`, `rskip_in_set` | the highest `i` (as F1/F5, backwards) | the reverse stay skip (`emit_dfa.c:5619`); `vm_rev_emit`'s backward walk; lookbehind | medium (`memrchr`, last-line scans) |
| **F7** | run compare, constant operand | `s[0..L)` equals a literal, exact or masked per position; the caller guarantees `L <= n` | P4, `pcrec_emit_run_compare` (`src/gen/runcmp.c`): ofsskip run term, REQ_RUN verify, VM literal run, island single-child chains (S4 C1/C3) | low as a function, high as a FORM: it is never a call (§2.3 row 1) |
| **F8** | `mismatch` (run-time operand) | the length of the common prefix of `a[0..n)` and `b[0..n)`, exact or ASCII-caseless | `$_span_match[_caseless]` (`enc_byte.c:153/184`) behind backrefs and `[VAR]` | high (`std::mismatch`, diff, `strncasecmp`-like) |
| **F9** | `find_literal`, anchored on a chosen byte | the first `i` where literal `(bytes, L)` matches at `s[i..i+L)`; the CALLER names the scan byte `j` (and optionally a second, Study A's rare pair) | `<p>_ofsskip` (memchr at offset k* + verify); the REQ_RUN pre-check (memchr + constant memcmp, restarting per hit) | high (`memmem`), and the caller-chosen anchor is what pcrec's frequency prior feeds |
| **F10** | `find_multi` (Teddy class) | the first `i` where any of N short literals starts, with the literal's id | S4(c) / `[OPT-A]`: keyword alternations (`942140-dbnames`, `942360-concat-sqli`) | high (Aho-Corasick prefilters, grep -F) |
| **F11** | `validate_utf8` (prefix) | the length of the longest well-formed UTF-8 prefix | `<prefix>_valid_upto` under `-futf-check` ([UTF-VALID], opt-in) | very high (simdutf's whole niche) |
| **F12** | find-all positions | a bitmap or list of every candidate position in a block | studies/simd1 §14 pre-searcher; `[SIMD-META]` hypothesis (1) | medium |
| **F13** | `count_byte` | the number of `i` with `s[i] == c` | none known | high (line counting) |

### 1.3 Rank: pcrec demand × general value

| tier | functions | why |
|---|---|---|
| **A, the core** | F1, F2, F4, F5, F9 | named emitted sites today, a measured motivating cell (F2 = K82), the in-loop budget (F5), and universal value outside pcrec |
| **B** | F3, F8, F7 (as a form), F10 | F3 folds into F2 or F4 for most uses. F8's customers are unmeasured (compare_stack.md S6 is gated on a cell). F10 is `[OPT-A]`'s row. F7 is a code template, not a call |
| **C** | F6, F11, F12, F13 | low pcrec demand (F6), opt-in only (F11), a hypothesis (F12), or no pcrec site at all (F13). In scope for a general-purpose library, not required of it |

The survey scores tier A as must-haves (§5.1 M-1). Tier B is a
nice-to-have with weight. Tier C is a nice-to-have at low weight.

### 1.4 The building blocks pcrec actually composes

pcrec's sites are not "call memchr" alone. They are "find a candidate,
verify around it, maybe resume". The library is most useful when it
exposes the parts as well as the whole:

- **block classifiers**: one vector of bytes in, a lane mask out. The
  forms are `eq1`, `eq2`, `eq3`, `cube`, `range` (subtract and compare),
  `shufti` (nibble lookup for an arbitrary ASCII set; NEON `tbl`), and
  `bitmap` (the fallback for sets with high bytes). This is
  studies/simd1 §3's encoder menu. Lanes compose by AND/OR, which is how a
  pinned rare byte plus a second position becomes one filter (Study A).
- **mask → position**: the first set lane (`ctz`, or `shrn` + `ctz` on
  NEON, which has no `movemask`) and the last set lane for the reverse
  forms.
- **loop skeletons**: forward/reverse, with the overlapped final block and
  the loop-free short path, generic over the classifier.

That split is requirement RB-6 below.

---

## 2. The binding-form criterion

Frank's question: "when is it acceptable to be a function call, an inline
call, or injected code? It shouldn't have this 10 ns overhead."

### 2.1 The forms

| form | what it is | what it pays | dispatch |
|---|---|---|---|
| **B1a, external call** | a symbol in another TU or shared library, for example libc `memchr` through the PLT (ELF) or a stub into the dyld shared cache (Mach-O), with glibc's ifunc choosing the body | call and return; argument setup; the caller's live registers spilled around the call or kept in callee-saved ones (inside a DFA loop, those are its state registers); no constant propagation (each call re-broadcasts the needle); the callee's own length-tier branches on every call | resolved once at load (ifunc) or fixed at libc build |
| **B1b, local out-of-line** | one emitted `static` helper per kernel shape, behind `noinline`: `[OPT-SIMD]`'s "one emitted helper per class-shape" idea | call and return, and the spills, but no PLT; constants not propagated unless the helper is specialized | compile time only (§2.5) |
| **B2, inline generic** | a `static inline` kernel from a header, visible to the compiler at the call site | nothing for the call. Constants propagate if the compiler does it (studies/simd1 §8: gcc's const-prop failed through indirection, so this is not guaranteed). Broadcasts hoist out of the caller's loop | compile time, by predefined macros |
| **B3, injected** | emitted text specialized per pattern: the needle bytes, `(K, T)`, set tables, offsets and `L` are literals; the loop shape is chosen by the emitter (no loop at all for a proven-short window); it can FUSE with its neighbours (two streams into one pass, a verify folded into the scan) | code bytes per site (the `[OPT-DIAL]` size term) | compile time |

B2 and B3 differ in WHO specializes. B2 relies on the compiler. B3
guarantees the result and can restructure across what would have been a
call boundary. compare_stack.md's P4 run compare is already a B3 instance:
gcc fuses a constant-length `memcmp`, so the emitter writes one.

### 2.2 The cost model

For one call at a site, with span `n`:

    T(form, n) = F_form + n * beta_form + hits * s_form

- `F` is the fixed entry cost: call, setup, and the tier branches.
- `beta` is the steady-state ns per byte, set by vector width and
  unrolling.
- `s` is the per-hit cost: the re-entry plus the verify that fails
  (k82cost's `s`, 7.5 ns Mac and 8.0 ns Linux, measured through B1a).

A site's cost is `E[T]` over its distribution of `n` and hit density,
times its call count. A form is chosen by the smallest `E[T]`, with a size
term `lambda * bytes(form, site)` priced by the dial. Four consequences
follow:

1. **The crossover length `n*`.** Inline beats a call only while
   `F_call - F_inline > n * (beta_inline - beta_call)`. libc's long-span
   `beta` is very good (unrolled, widest ISA via ifunc), so `n*` is finite.
   On the Mac it is about 512-1024 bytes: from there libc's 104 ns at
   4 KiB beats our non-unrolled 108-113 ns (§2.4). An inline kernel whose
   long path is as unrolled as libc's pushes `n*` to infinity. That is
   RB-7.
2. **k streams cost k F's and k passes.** A multi-needle search spelled as
   k calls pays `k * F + k * n * beta`, plus every stream's overshoot past
   the first hit. A fused kernel pays `F + n * beta'`, where `beta'` is
   about `beta` (one more compare and OR per vector). This is the largest
   term in the K82 cell (§0 item 2).
3. **Call count multiplies F.** D91's two budgets are this term. A
   PREFILTER call runs about once per match point, so `F` is amortized over
   a long scan. For a single stream, B1a is acceptable there (D91 budget 1,
   unchanged). An IN-LOOP site (F5 inside the DFA's step loop, D91 budget
   2) may run once per state visit, so `F` lands on the per-byte cost.
4. **Short subjects make every site a short-span site.** On the bench's
   per-call cells (6-11 B subjects, k82diag §2), a "rest of subject" scan
   is a 6-11 B scan. `F` is the whole cost there. Span length is a property
   of the call, not of the site. That is why k82cost's `W` was decisive.

### 2.3 The decision, as a first-match table

The first row whose predicate holds decides the form (the `dfa_pfs[]`
idiom). Thresholds are per box and come from §2.4 and the owed Linux run.
None is a constant to be guessed.

| # | predicate (all known at compile time unless noted) | form | why |
|---|---|---|---|
| 1 | the operand is a compile-time literal AND the span length is fixed or bounded by a small `maxw` (a run compare, F7; a counted window) | **B3**, loop-free | constant-length compares inline for free (D91 corollary; memcmp_lowering_study); `memchr` never inlines |
| 2 | the site is IN-LOOP (D91 budget 2: a stay skip, a scan edge, a VM cursor run) | **B3 or B2**, never a call, until a measurement at that site says otherwise | `F` multiplies by the visit count; D91 forbids inheriting the prefilter argument |
| 3 | the search has two or more needles or streams over one span (F2/F3, the pair arm, a pinned pair) | a **fused** kernel (B2 or B3); never k calls | §2.2 item 2; §0 item 2 |
| 4 | the expected span is below `n*`: from `maxw`, from a findings bundle's `W` ([FINDINGS.B4]), or from the call's own `n` at run time (a size knee) | **B2** inline | `F_call - F_inline` dominates below `n*` |
| 5 | a single-stream, rest-of-subject scan run once per match point | **B1a** (libc) is acceptable; B2 if its long path matches libc's `beta` | D91 budget 1; libc's ifunc gives the widest ISA for free |
| 6 | otherwise | **B2** | the safe default: no call, no PLT, compile-time ISA |

Row 4's run-time arm is a size-tiered body inside one kernel: a call
first tests `n` against the short-path widths, then the vector loop, then
the unrolled long loop. That is studies/simd1 §13's "haystack-size
tiering" applied per call, and it is the remedy k82diag §2 named ("a
subject-length knee in front of the pair arm") made general.

### 2.4 The probe (Mac, measured)

`probes/callcost.c` (build: `probes/probes.mk`; transcripts:
`probes/out/callcost.mac.{gcc,clang}.txt`). Kernels: libc `memchr`; an
inline byte loop; inline SWAR; an inline 16-byte NEON loop with a byte
tail (`neon`), with an overlapped final block (`neon_ov`), and with a
loop-free short path below 16 (`neon_sm`); the same behind `noinline`
(`*_ool`); two libc calls (`pair_libc`) against one fused inline
two-needle pass (`pair_neon`). The case is a MISS: the needle is absent,
so the whole span is read, as when a gate rejects. Every timed loop is
calibrated to at least 50 ms and run three times; min..max is printed.
The `loop` row is the harness's own cost per iteration. `--check` runs
7,272,160 cases (n 0..300, every hit position, alignments 0..15, the span
ending at its allocation's end) against the reference, 0 bad, under gcc,
clang, and clang `-fsanitize=address,undefined`.

ns per call, independent calls, min of 3 (M1 Max, macOS 26.6, `-O2`;
**unpinned on a shared box: directional only, D144 addendum 1**):

| n | 1 | 8 | 16 | 32 | 64 | 256 | 1024 | 4096 |
|---|---|---|---|---|---|---|---|---|
| loop (harness) | 0.32 | 0.32 | 0.32 | 0.33 | 0.32 | 0.33 | 0.32 | 0.33 |
| libc `memchr` | 1.64 | 1.63 | 1.63 | 1.96 | 3.89 | 7.80 | 23.56 | **104.04** |
| inline byte loop (gcc / clang) | 1.29 / 0.65 | 4.25 / 3.26 | 6.81 / 5.86 | 12.0 / 11.1 | 22.5 / 21.3 | 92.8 / 93.0 | 342 / 342 | 1348 / 1341 |
| inline `neon` (byte tail), gcc | 1.63 | 4.57 | 1.30 | 2.28 | 2.94 | 6.86 | 24.12 | 107.53 |
| inline `neon_sm`, gcc | 1.30 | **0.97** | 1.30 | 1.64 | 2.93 | 6.89 | 24.00 | 108.52 |
| inline `neon_sm`, clang | 1.31 | 1.77 | 1.31 | 2.28 | 2.92 | 6.85 | 24.39 | 113.20 |
| `neon_sm` behind `noinline`, gcc | 1.95 | 1.96 | 1.94 | 2.29 | 3.61 | 7.51 | 24.49 | 108.61 |
| two libc calls (pair arm), gcc | 3.28 | 3.26 | 3.27 | 3.92 | 7.51 | 15.34 | 46.87 | 208.56 |
| fused inline two-needle, gcc / clang | 1.63 / 0.98 | **1.46** / 1.90 | **0.96** / 1.31 | 1.35 / 2.27 | 2.56 / 2.93 | 8.22 / 7.12 | 31.8 / 26.9 | 131.3 / 115.7 |

Hit at offset 0, n = 64 (the pure entry cost), independent calls:
libc 1.96, `neon_sm` 0.98 (gcc) or 0.86 (clang), `noinline` 1.95-1.63,
two libc calls **6.22** (the absent second stream reads all 64 bytes),
fused 0.98-0.89.

The same, but with each call's start address depending on the previous
call's result (`dep` mode): libc 8.1-8.2 ns, every vector form 6.9-7.9 ns,
the byte loop 0.65-0.72 ns. That is LATENCY. A vector find whose result
feeds the next address pays the vector-to-GPR mask transfer plus `ctz` on
the critical path, whatever its binding form. The byte loop's figure is a
predicted branch at a fixed position, which real data will not give it.
In the miss case `dep` measures no latency, because a predicted branch
breaks the dependency. The one exception is finding 4: clang's
if-converted short path, which costs 6.6 ns in `dep` against 1.8 ns
independent.

Readings, each directional:

- **F on the Mac:** libc's call costs 1.3 ns over the harness loop, and the
  inline loop-free form costs 0.65-1.0 ns over it. The binding-form saving
  is about **0.3-0.65 ns per call**. Our own `noinline` call costs the same
  as libc's. The Mac call term is small.
- **`n*` on the Mac:** inline leads to about 512 B (12.25 ns against
  12.99 ns) and ties or loses from 1 KiB, where libc's unrolled loop takes
  over (104 ns against 108-113 ns at 4 KiB).
- **Fusion is the big lever:** about 2 ns per call at short spans, and
  1.6-1.8x at 4 KiB.
- **Short-path shape is the second lever:** a byte tail costs 3.6-5.9 ns
  at n = 8-12 where loop-free overlapping words cost 1.0-1.8 ns.
- **The compiler matters:** clang's byte loop is twice gcc's speed at
  n ≤ 4 (it unrolls). clang's loop-free path is slower than gcc's at
  n = 8-12 and much slower in `dep`.

### 2.5 The requirements that follow

- **RB-1 Header-only availability.** Every kernel must be consumable as
  `static inline` source with no external symbol, no link step and no
  library to ship. That is what makes B2 possible, and B3 needs the same
  text as the thing it copies and specializes.
- **RB-2 Embeddable text.** The header compiles inside a generated
  artifact: gcc and clang, in the GNU C dialect pcrec emits (the probe
  uses `-std=gnu11`), clean under
  `-Wall -Wextra`, C and not C++. All names sit behind a prefix macro, so
  that two artifacts carrying different library versions can share one
  TU. Include guards alone do not handle that.
- **RB-3 Compile-time ISA selection in the inline forms.** The inline
  forms select their ISA only by predefined macros (`__SSE2__`, `__AVX2__`,
  `__ARM_NEON`, `__ARM_FEATURE_SVE`). They do no CPU detection and carry no
  mutable static (match_api.md §5.3, TS-1). The scalar or SWAR fallback
  always compiles. The baseline vector tier (SSE2, NEON) must not depend
  on any `-m` flag.
- **RB-4 A short-span path with no call and no loop.** Below the vector
  width the kernel uses overlapping loads (two words for 8..15 bytes, two
  half-words for 4..7, probes for 1..3) that stay inside `s[0..n)` (S-2).
  At or above the width it uses an overlapped final block, never a byte
  tail. §2.4 measures a 2-6x gap at n = 8-12.
- **RB-5 Constant operands specialize.** With constant needles, masks,
  sets or lengths, the kernel must specialize: broadcasts and tables
  hoisted, branches on constants folded. Either `always_inline` makes that
  reliable on gcc and clang, or the library exposes a TEMPLATE pcrec can
  instantiate (a macro, or the classifier plus skeleton split of RB-6).
  simd1 §8 is the warning: do not trust const-prop through indirection.
- **RB-6 Separable parts.** Block classifiers, mask-to-position, and loop
  skeletons are exposed separately (§1.4), so pcrec can fuse two streams,
  verify at a hit inside the scan, or swap the classifier per pattern
  without forking the library.
- **RB-7 Long spans match libc.** At least the long path (≥ 1 KiB) must
  be unrolled (64 B or more per iteration) so that `n*` is not a cliff. A
  B2 kernel that loses to libc at 4 KiB forces a two-form site.
- **RB-8 The library's own out-of-line form may dispatch at run time.**
  ifunc on ELF, a constructor-resolved pointer elsewhere. Every ISA
  variant must also have its own directly callable name, so a static,
  dispatch-free use is always possible. *Sharpened as RB-13 in
  isa_selection.md §5.*
- **RB-9 Measurable size.** The per-kernel, per-ISA code size must be
  reportable (an object build per kernel is enough), because B3's per-site
  bytes are the dial's size term (`[OPT-DIAL]`).

### 2.6 Owed: the same probe on the Linux x86 box

The motivating ~3.4 ns per call is glibc's (k82diag §2: two fresh
`memchr` calls cost 6.8 ns, and the rejecting pair-arm floor is 10.06 ns).
The Mac cannot stand in for it. **Owed on ubuntubudu**, through the
manager's executor channel (pcrecdev2), pinned and on a quiet box (D144
addendum 1). The probe's SSE2 path compiles today (checked with
`clang -target x86_64-apple-macos13`, plain and `-mavx2`). It has not
run on x86.

    cd <pcrec checkout at this branch>
    make -f docs/design/memfn/probes/probes.mk CC_GCC=gcc CC_CLANG=clang check
    taskset -c 2 build/memfn_probe/callcost.gcc   > callcost.linux.gcc.txt
    taskset -c 2 build/memfn_probe/callcost.clang > callcost.linux.clang.txt
    # the AVX2 build: the probe's vec forms stay SSE2 (16-byte), but -mavx2
    # shows whether a VEX build changes F; glibc's memchr is AVX2 by ifunc
    make -f docs/design/memfn/probes/probes.mk CC_GCC=gcc CFLAGS='-O2 -std=gnu11 -mavx2' OUT=build/memfn_probe_avx2 build/memfn_probe_avx2/callcost.gcc
    taskset -c 2 build/memfn_probe_avx2/callcost.gcc > callcost.linux.gcc-avx2.txt

**One script now runs all of it:** `probes/linux_run.sh` runs these commands
pinned and bounded, plus R1b's probes (isa_selection.md §4).

The questions it answers: glibc's `F` (predicted about 3.4 ns, against
the Mac's 1.3), `n*` against glibc's AVX2 body, and whether fusion's
advantage holds on x86. An AVX2 arm of the kernels themselves is a later
probe. It belongs to the survey or the build, not to R1.

---

## 3. Non-functional requirements

| id | requirement |
|---|---|
| **N-1 ISAs** | x86-64: SSE2 baseline (no dispatch), AVX2 tier (by `-march` in inline forms, optionally by run-time dispatch in B1), AVX-512 optional. AArch64: ASIMD/NEON baseline, SVE/SVE2 optional. Both architectures are first-class: neither is primary ([OPT-SIMD], Frank 2026-08-31) |
| **N-2 Scalar fallback** | portable C (SWAR permitted) for any other target. Correct on big-endian as well as little-endian: the SWAR `ctz` lane trick assumes little-endian, so a big-endian path, or a `__BYTE_ORDER__` guard that selects the byte form, is required |
| **N-3 Compilers** | gcc (pcrec's target compiler; the floor version is the oldest gcc pcrec supports) and clang (the macOS toolchain, `[CC-CLANG]`). Both at `-O1`..`-O3` and `-Os` (memcmp_lowering_study measured `-Os` behaving differently) |
| **N-4 Dependencies** | the inline forms need only `<stddef.h>`, `<stdint.h>`, compiler intrinsics headers, and builtins (`__builtin_ctz*`, `memcpy` for unaligned loads, which both compilers lower to a load). No libc calls, no libgcc or compiler-rt runtime functions, no `__builtin_cpu_supports` (it reads libgcc's `__cpu_model`; on Darwin it answers 0 for every feature, and an opt-in Linux exception is isa_selection.md Q5) |
| **N-5 Licence** | §0 item 6 and §7 Q1. Disqualifying: GPL and LGPL for any text that is injected or inlined (glibc's string routines are LGPL-2.1+: ideas only). Acceptable for ideas in every case. For TEXT, a licence pcrec can carry into generated output under the answer to Q1: MIT, BSD-2/3, ISC, zlib, 0BSD, Unlicense or CC0, Apache-2.0 (with its NOTICE implication), or Apache-2.0 WITH LLVM-exception |
| **N-6 Correctness method** | exhaustive testing against a scalar reference over every length 0..≥ 2×(widest vector + unroll), every hit position (and none), every alignment 0..(vector width − 1), and spans ending exactly at an allocation's end (the probe's `--check` shape), under ASan + UBSan, on BOTH architectures. Guard pages at both ends (studies/simd1's harness: a `PROT_NONE` page flush against the span end and another before its start). Plus random fuzzing against the reference, and for F4/F5 every 256-bit set shape the corpus and the uprops census produce |
| **N-7 Benchmark method** | span lengths 1..64 KiB on a log scale (short spans weighted: the bench's per-call cells are 6-11 B), hit densities from none to dense, hit position (first, middle, last), independent and dependent call chains (throughput and latency), calibrated loops of 50 ms or more, absolute ns with the min..max spread, `taskset` pinning on Linux, Mac numbers marked directional (D144 addendum 1). Many distinct small buffers rather than one hot one (studies/simd1 §13's honesty note) |
| **N-8 Codegen verification** | the branch shape of each kernel (branchy against `csel`/`cmov`) and the absence of calls are checked in the disassembly per compiler: the D82 bound, "the hot loop's instruction sequence after gcc must equal the hand-written form", applied to the library. Finding 4 is the reason |
| **N-9 Freestanding and reentrant** | S-6, and usable in the freestanding/embedded profile (match_api.md §10.7): no heap, no TLS, no static data except `const` tables |
| **N-10 Stable API** | semantic versioning, or vendored at a pinned version. pcrec vendors by `third_party/`'s shape (one directory per source, versioned, with a PROVENANCE.md naming what derives from it) if text is adopted |
| **N-11 Size** | per-kernel code size small enough for B3 at many sites (RB-9). A kernel whose minimal instantiation runs to kilobytes (FDR-class tables, for example) is a B1-only kernel |

---

## 4. Where pcrec's existing facts already fit (no new requirement)

- **Operands come from pcrec's single sources**: P2's `pcrec_cube_of` and
  `pcrec_cls_cube` for cubes, the class bitmaps for sets, P6's prior and
  P3's run fact for the anchor byte of F9. The library takes operands. It
  never derives them (compare_stack.md §5's must-not-re-derive column).
- **Selection stays pcrec's.** Which kernel and which form a site gets is a
  `dfa_pfs[]`/`req_admits[]` row decision, stamped and deniable as today.
  The library has no policy.
- **Fold:** the library's caseless forms are ASCII-only (`(x & 0xDF)` under
  an is-letter guard, never a blind `| 0x20`: studies/simd1 §4). utf8
  folding stays `$_span_match_caseless`'s own (compare_stack.md §5).

---

## 5. The evaluation rubric (for R2, the survey)

Each candidate, and "build our own" as a candidate, is scored against
this table. A must-have that fails disqualifies the candidate as a TEXT
source. It may still be scored as an IDEAS source (§5.4).

### 5.1 Must-haves (pass/fail)

| # | must-have | from |
|---|---|---|
| M-1 | covers tier A (F1, F2, F4, F5, F9), or its structure admits them without a rewrite | §1.3 |
| M-2 | never reads outside `s[0..n)`; passes N-6's exhaustive and guard-page method (run, not read) | S-2, N-6 |
| M-3 | header-only or `static inline` consumable, no link-time symbol needed | RB-1 |
| M-4 | C (gnu11-compatible), compiles in gcc and clang | RB-2, N-3 |
| M-5 | ISA selection available at compile time, scalar fallback present, no mandatory run-time dispatch or mutable static | RB-3, N-4 |
| M-6 | x86-64 SSE2 and AArch64 NEON both implemented, not one emulated through the other | N-1 |
| M-7 | licence permits the use proposed (text or ideas) under Q1's answer | N-5 |
| M-8 | no allocation, no libc dependency in the inline path | N-4, N-9 |

### 5.2 Nice-to-haves (scored 0-3 each, weight in brackets)

| # | nice-to-have | weight |
|---|---|---|
| H-1 | loop-free short path below the vector width (RB-4), measured | 3 |
| H-2 | fused multi-needle (F2/F3) rather than k single scans | 3 |
| H-3 | separable classifier / mask / skeleton parts (RB-6) | 3 |
| H-4 | constant-operand specialization is reliable or templated (RB-5) | 2 |
| H-5 | long-span `beta` at or better than libc on both boxes (RB-7) | 2 |
| H-6 | tier B coverage (F3, F8, F10) | 2 |
| H-7 | AVX2 tier; AVX-512 / SVE | 1 |
| H-8 | reverse forms (F6) | 1 |
| H-9 | its own exhaustive and fuzz test suite, and a benchmark suite we can rerun | 2 |
| H-10 | active maintenance, a release history, a public issue tracker | 1 |
| H-11 | big-endian correctness (N-2) | 1 |
| H-12 | small per-kernel code size (N-11) | 1 |
| H-13 | tier C coverage (F11, F12, F13) | 1 |

Score = the weighted sum of the 0-3 marks (maximum 69; 81 with
isa_selection.md §6's H-14..H-16). A score is
reported with its EVIDENCE (a test run, a disassembly, a timing), never
from documentation alone. That is pcrec's measured-not-read rule.

### 5.3 Candidates to evaluate (pointers only; R2's job, not R1's)

C header or C-friendly: **StringZilla** (header-only, multi-ISA),
**sse4-strstr / Muła's SIMD notes** (`memmem` ideas), **simdutf** (F11),
**SIMDe** and **sse2neon** (portability layers, not kernels), **ARM
optimized-routines** (AArch64 `memchr`/`strlen`), **musl** (scalar
reference), **LLVM libc** (Apache-2.0 WITH LLVM-exception, relevant to
Q1), **Vectorscan/Hyperscan** (Teddy, FDR; large, BSD-3). Idea sources in
other languages: **Rust `memchr` crate** (memchr2/3, the memmem rare-byte
heuristic, the "packed pair"), **aho-corasick's Teddy**, **simdjson**
(classifier design), **Google Highway** (C++ portable SIMD). Also the
**GCC/Clang portable vector extensions** as the write-once layer
([OPT-SIMD] item (b)). Expect them to cover compare, OR and range, and to
leave `shufti` and mask extraction needing per-ISA intrinsics. And
**studies/simd1** itself, pcrec's own prior art (AVX2-measured, with a
validated harness).

### 5.4 Ideas-only scoring

A candidate that fails M-3, M-4, M-5 or M-7 can still be scored for
borrowable ideas (the algorithms, the short-path tricks, its test
method). Record those ideas as citations in the build design, not as
text.

---

## 6. What we do not know yet

| # | unknown | answered by |
|---|---|---|
| U-1 | glibc's `F` and `n*` on x86, and whether fusion's margin holds there | the owed Linux probe (§2.6), via pcrecdev2 |
| U-2 | which class shapes are HOT at F4/F5 sites (size, range, ASCII-only?). The corpus has 41 distinct byte classes, all 2-4 intervals (cls_tree_study §1), but no bench census exists of which shapes the scanning sites actually run | a bench class-shape census (a pcrec-bench question, listed for relay), then the survey's weighting of shufti against range against OR-chains |
| U-3 | the in-loop dispatch cost of B1b and B2 at a scan edge or stay skip (D91 budget 2): whether an outlined helper costs anything inside the DFA loop | a later probe at a real emitted in-loop site ([OPT-SIMD]'s check (a)) |
| U-4 | any NEON number beyond 16-byte `cmeq`: `tbl` shufti, the range idiom, unrolled loops, against libSystem | the survey (H-5, measured) or the build |
| U-5 | the latency cost (§2.4 `dep`) in real verify-and-resume loops, where hit positions vary and branches mispredict | a later probe on bench subjects |
| U-6 | span distributions per site (what `W` really is per call) | [FINDINGS.B4] / k82cost's model; the bench's per-call cells |
| U-7 | whether gcc's and clang's branch shapes for a short path can be pinned without inline asm | the build, with N-8's disassembly check |
| U-8 | the AVX2 tier's value over SSE2 for short spans: wider vectors raise the short-path threshold | the Linux probe's AVX2 arm (`isacost`, isa_selection.md §4), then the build. U-9..U-14 continue in isa_selection.md §7 |

---

## 7. Questions for Frank

1. **Q1, the licence of generated output.** pcrec's LICENSE (MIT) does
   not say what licence an emitted artifact carries. Does today's emitted
   text carry pcrec's MIT notice obligation into users' programs? If
   third-party kernel text is injected, which licences are acceptable for
   it? **Recommendation:** decide pcrec's own output terms first (an
   explicit output exception, in the shape of Bison's or LLVM's), then
   accept only kernel text under terms compatible with that exception:
   0BSD, CC0, Unlicense, or a licence with its own output exception. Treat
   MIT/BSD/Apache text as ideas-only unless Q1 says otherwise.
2. **Q2, where the library lives.** This is the plan row's R3 decision
   (adopt, fork, or a new separate repo; the scope mandate extends only on
   that ruling). R1 adds one fact: RB-1/RB-2 mean pcrec needs the TEXT at
   emit time. Whatever repo it lives in, pcrec vendors a pinned copy
   under `third_party/` (N-10). **Recommendation:** no ruling needed
   until R2 reports.
3. **Q3, the Linux probe now or with the survey.** It is small (two
   pinned runs). **Recommendation:** run it now, because U-1 decides
   whether §2.3's row 4 matters on the reference box at all.
