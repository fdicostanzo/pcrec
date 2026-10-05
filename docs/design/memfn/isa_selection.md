# memory-functions: R1b, ISA SELECTION AND CHECKING

Owner row: `[MEMFN]` (docs/dev/plan.md), step R1b, an addendum to
`requirements.md` (R1). Lane `memfnisa`, 2026-10-04, written from main at
3813fa00. Docs and probes only. Nothing under `src/`, `cli/`, `lib/` or
`tests/` changes, and no emitted byte moves (D91). Every emitted-text change
below is DESIGNED, not built. Building one is an `abi` event plus a
`docs/spec/` hunk (D76/D94, D80).

Frank's ask (2026-10-04): *"I'd be interested in arch checks — either
dynamic, or checkable. For instance, a called function might switch between
fallback SIMD implementations if it's cheap. Or we might specify the arch
for a compiled artifact then fail if it's not the correct one."* Linux
x86-64 is the primary architecture.

The constraints are the ones R1 states. Generated code is self-contained,
holds no mutable state of its own (match_api.md §5.3, a binding contract),
and is checked by TS-1 (no non-const static object and no non-reentrant or
allocating libc symbol in emitted text). The binding forms are R1's B1a
(external call), B1b (local out-of-line helper), B2 (inline) and B3
(injected). The D91 budgets are the prefilter (about once per match point)
and in-loop (per state visit).

---

## 0. Findings first

All Mac numbers below are directional only: M1 Max, unpinned, on a shared
box (D144 addendum 1). The x86 numbers are owed (§4).

1. **Switching on a CACHED word is free. Reading the CPU is not.** Per call
   at n = 16 (gcc / clang, ns): a direct out-of-line call costs 1.64 /
   2.30. The same call through a function pointer costs 1.65 / 2.27. A
   lazily rewritten pointer costs 1.66 / 2.30, and a cached flag choosing
   between two out-of-line kernels costs 1.63 / 2.29. A cached flag in
   front of an INLINE baseline costs the same as the inline kernel
   (0.98 / 1.65 against 1.63 / 1.31; the difference is code-layout noise,
   up to about 0.65 ns either way). Asking the OS on every call
   (`sysctlbyname`) costs **about 930 ns**, roughly 3,000 call costs. So
   Frank's "if it's cheap" holds for any mechanism that reads a word
   somebody already cached. **The question is WHO holds that word.** The
   branch itself costs nothing.
2. **An emitted artifact cannot hold the word itself.** That is §5.3, and
   TS-1 enforces it. The cheap per-call mechanisms that remain read a word
   someone ELSE owns:
   - (i) libgcc's or compiler-rt's `__cpu_model`, through
     `__builtin_cpu_supports`. A constructor writes it before `main`.
     §5.3 allows this, because the state is not the matcher's own, and
     TS-1's text scan does not see it. R1's N-4 forbids it on dependency
     grounds.
   - (ii) the loader's GOT slot, through ifunc or multiversioning. This is
     ELF-only, plus a new Mach-O mechanism (item 4).
   - (iii) the caller's word: a capability the caller checked once.

   Without a cache, "check at the first call" is the same as "check at
   every call". With no memo, an artifact cannot tell which call is the
   first. That makes the per-call cost the query cost: about 930 ns on the
   Mac, and an owed number for `cpuid` on x86.
3. **On Darwin/AArch64 `__builtin_cpu_supports` gives the wrong answer,
   silently.** Apple clang 21 and LLVM clang 23 both return 0 for EVERY
   feature, `simd` and `fp` included, on an M1 that has them all. The
   runtime's `__aarch64_cpu_features` word reads 0 before and after an FMV
   resolver has run. gcc-16 on darwin does not offer the builtin at all
   (`probes/out/fmvdarwin.mac.txt`). A dispatcher built on it silently
   picks the baseline. A CHECK built on it refuses every declared ISA. It is
   a Linux mechanism only.
4. **R1's finding 5 ("ifunc is ELF-only; there is none on Mach-O") is now
   only half true.** Apple clang 21 lowers `target_version` multiversioning
   to a `__LD,__func_variants` table, which the linker and dyld resolve.
   That is a loader-resolved dispatch: it chose the `dotprod` version on
   this M1 and costs 0.3-0.4 ns over a direct call to the same kernel at
   short spans. LLVM clang 23
   lowers the SAME source to a resolver and a lazily written `__DATA`
   pointer. That pointer is a compiler-generated mutable static, which
   TS-1's text scan cannot see. Which lowering an artifact gets therefore
   depends on the CONSUMER's toolchain, and pcrec does not control that
   (K24: "pcrec cannot dictate its users' CFLAGS"). Finding 5's conclusion
   stands: emitted code does no run-time dispatch by default. Its reason
   narrows to "toolchain-dependent", not "unavailable".
5. **Run-time selection and inlining pull against each other.** A kernel
   for a wider ISA lives in a `target("avx2")` function. Neither gcc nor
   clang will inline it into baseline code. A per-call switch to the wide
   tier therefore always crosses a call, which makes it B1b at best. On the
   Mac stand-in that call costs 0.3-1.0 ns at short spans (`wide_ool`
   against `wide_inl`) and nothing at long ones. The remedy is to move the
   selection UP: declare or multiversion the whole matcher, so that the
   kernel inlines inside each version. That is §1.2 and §2 row 3.
6. **Preprocessor selection and multiversioning do not compose.** Inside a
   `target_clones("avx2", ...)` clone, `__AVX2__` still has the TU's value,
   so an `#if __AVX2__` ladder picks the same kernel in every clone. A
   library that wants both static (`-march`) and dynamic selection must
   write each tier as a target-attributed function, so that every tier
   compiles in a baseline TU (new RB-10).
7. **A declared-ISA artifact costs nothing per call if the caller checks
   once.** The stamp is free. The preprocessor computes the level from
   predefined macros, so the emitted text is the same for every level
   (`isacost.c`'s `ISA_COMPILED`; the macro sets for x86-64-v2/v3/v4 were
   measured with clang, §1.2). The check is a pure, static-free
   `cpuid`/`xgetbv` function, and it must be compiled at the BASELINE.
   Compiled at the TU's `-march`, it could itself execute a VEX
   instruction and raise SIGILL. `target("arch=x86-64")` achieves that. In
   the v3 TU's ELF object it emits 0 VEX/EVEX instructions (clang,
   disassembled on the Mac; gcc is owed). The LOADER's ISA marker
   (`GNU_PROPERTY_X86_ISA_1_NEEDED`) is BELIEVED to make glibc ≥ 2.33
   refuse to load the program or library. A marker embedded from C source
   parses correctly (`readelf` on the Mac-built ELF object). Whether the
   link keeps it and `ld.so` enforces it is the Linux run's question
   (§1.2.4).

---

## 1. The options

### 1.1 Dynamic: selection inside a called function

Mac per-call cost, ns, MISS case, independent calls, min of 3 ≥ 50 ms loops
(`probes/out/isacost.mac.{gcc,clang}.sel-{base,wide}.txt`). The harness
loop alone costs 0.33. `base` is the 16-byte NEON kernel and `wide` is a
64-byte-unrolled NEON stand-in. AArch64 has no wider tier on this box, so
the stand-in has the same DISPATCH shape and the dispatch is what is
measured.

| mechanism (probe row) | n=1 | n=16 | n=64 | n=4096 | notes |
|---|---|---|---|---|---|
| inline baseline, no selection (`base_inl`) gcc / clang | 1.30 / 1.31 | 1.63 / 1.31 | 3.25 / 2.91 | 107.4 / 112.8 | the compile-time floor |
| direct call, baseline (`base_ool`) | 1.95 / 1.96 | 1.64 / 2.30 | 3.26 / 3.93 | 108.5 / 109.8 | B1b |
| direct call, wide (`wide_ool`) | 2.29 / 1.95 | 1.96 / 2.29 | 2.28 / 2.93 | 53.4 / 52.0 | the wide tier pays from 64 B, 2x at 4 KiB |
| wide inlined into a wide-compiled caller (`wide_inl`) | 1.63 / 1.49 | 0.97 / 1.30 | 2.27 / 1.95 | 53.2 / 53.1 | the DECLARED-ISA form |
| cached flag → inline base / call wide (`flag_hyb`), base arm | 1.30 / 1.30 | 0.98 / 1.65 | 2.59 / 3.26 | 106.7 / 114.2 | = `base_inl` within layout noise |
| the same, wide arm | 2.31 / 1.96 | 1.92 / 2.27 | 2.30 / 2.96 | 53.2 / 52.0 | = `wide_ool` |
| function pointer set at init (`fnptr`), wide | 2.28 / 1.95 | 1.97 / 2.29 | 2.28 / 2.95 | 53.2 / 51.4 | = a direct call |
| lazily rewritten pointer (`fnptr_lazy`), wide | 2.30 / 1.96 | 1.96 / 2.30 | 2.30 / 2.93 | 52.7 / 52.1 | = a direct call |
| `__builtin_cpu_supports` per call (`cpusup_hyb`), clang | — / 1.30 | — / 1.64 | — / 3.30 | — / 112.2 | reads 0 on Darwin, so it runs the base arm; the test adds nothing measurable (`det_cpusup` = 0.33, the loop's own cost) |
| raw query per call, no cache (`query_hyb`; macOS `sysctlbyname`) | 936 / 941 | 943 / 950 | 934 / 934 | 979 / 1000 | `det_query` alone: 932-953 |
| multiversioned function (`fmv`; Apple clang `__func_variants`) | — / 2.27 | — / 2.63 | — / 3.29 | — / 56.4 | it picked the `dotprod` version (= wide): +0.3-0.4 ns over `wide_ool` at short spans; +4-5 ns (8-10%) at 4 KiB, unexplained (clone layout?) |
| ifunc | n/a on Mach-O | | | | owed on Linux |

The options, one by one:

| # | mechanism | where the cached state lives | cost per call | legal in B1a | B1b / B2 / B3 (in an artifact) | failure mode |
|---|---|---|---|---|---|---|
| D1 | **raw query every call**: x86 `cpuid` (+`xgetbv` for the OS's AVX state); Linux `getauxval(AT_HWCAP)`; macOS `sysctlbyname` | nowhere | macOS about 930 ns. `cpuid` OWED (BELIEVED tens to hundreds of cycles bare-metal, and on a hypervisor a VM exit of microseconds). `getauxval` reads libc's saved auxv (BELIEVED a few ns; aarch64 Linux only, not on the run plan) | yes | §5.3-legal (no state). `getauxval`/`sysctlbyname` are libc calls TS-1 does not deny | cost: never on a hot path |
| D2 | **`__builtin_cpu_supports`** | libgcc / compiler-rt's `__cpu_model` (x86) or `__aarch64_cpu_features`, written by a constructor | about 0 on the Mac (a load and a test). x86 OWED | yes | §5.3-legal (the state is not the matcher's own). TS-1 passes (no static, no denied symbol). **N-4 forbids it** (a runtime-library dependency). Unavailable freestanding (match_api.md §10.7) | **wrong on Darwin** (0 for everything, §0 item 3); unset if called before the constructors run (gcc documents `__builtin_cpu_init` for resolvers and constructors); gcc-darwin has no builtin |
| D3 | **cached flag** (`static int`, set at init) | a mutable static | ≈ 0 over the arm it selects | yes | **no**: §5.3 and TS-1 | none in a library; an init that never ran reads 0 and picks the baseline (fail-safe) |
| D4 | **function pointer set once** (constructor or init) | a mutable static | = a direct call (±0.06 ns) | yes | **no** | an unset pointer is a NULL call unless it is initialized to the baseline |
| D5 | **lazy pointer** (starts at a resolver that rewrites it on the first call) | a mutable static | = a direct call | yes | **no** | the first-call write races between threads. It is benign (idempotent), but strictly it needs a relaxed atomic |
| D6 | **GNU ifunc** | the loader's GOT/IRELATIVE slot | a PLT-style indirect call. OWED; BELIEVED the same as a non-inlined libc call | yes (glibc's `memchr` is this) | no source state, so §5.3/TS-1 pass on a reading of "own state". **ELF only.** The resolver needs D2 (with `__builtin_cpu_init`) or raw `cpuid`. It adds an IRELATIVE relocation to the user's program | resolver order in static binaries; not on Mach-O |
| D7 | **compiler multiversioning** (`target_clones` x86; `target_version` AArch64) | toolchain-chosen: ELF uses ifunc (D6); Mach-O with Apple clang a dyld `__func_variants` table; Mach-O with LLVM clang a lazily written `__DATA` pointer (D5) | Mac (Apple clang): a direct call + 0.3-0.4 ns at short spans | yes | **toolchain-dependent**: legal under the first two lowerings, a hidden mutable static under the third. So it is not emitted by default (§2) | the `#if` interaction (§0 item 6); clone size × count; gcc-darwin has neither attribute |
| D8 | **caller's word**: the caller passes a capability (or calls a check once and then a level-specific entry) | the caller's | ≈ 0 | n/a | legal everywhere. It needs an API surface: a parameter or an `rx_ctx` field (an abi event), or a per-level entry name | a caller that skips the check: SIGILL unless the entry re-checks (D2) |

**AArch64.** NEON (ASIMD) is in every armv8-a CPU, so there is no
NEON-vs-scalar dispatch. The only real choice is NEON against SVE/SVE2.
- SVE kernels are vector-length agnostic, so one SVE kernel serves every
  width and the dispatch is one bit.
- Detection on Linux is `getauxval(AT_HWCAP) & HWCAP_SVE` and `AT_HWCAP2 &
  HWCAP2_SVE2`, or D2 with gcc ≥ 14 / clang.
- On macOS no Apple core through M1 has SVE: `hw.optional.arm.FEAT_SVE` is
  an UNKNOWN sysctl here, and there are no SVE sysctls at all. BELIEVED: M4
  adds SME, with streaming SVE only. So on Apple silicon "the SVE tier" is
  always the baseline.
- A Graviton-class Linux box is where SVE dispatch would matter. None is in
  pcrec's box set, so SVE is designed and not measured (U-13).

### 1.2 Declared-ISA artifacts: "specify the arch, then fail if it is wrong"

#### 1.2.1 The levels

x86-64 uses the psABI microarchitecture levels. These are the predefined
macros each `-march=x86-64-vN` sets, measured with clang (`-dM -E`):

| level | adds (macros) |
|---|---|
| x86-64 (v1) | SSE, SSE2: no macro beyond the defaults; **every kernel's baseline** |
| x86-64-v2 | `__SSE3__ __SSSE3__ __SSE4_1__ __SSE4_2__ __POPCNT__ __CRC32__ __LAHF_SAHF__` |
| x86-64-v3 | v2 + `__AVX__ __AVX2__ __BMI__ __BMI2__ __FMA__ __F16C__ __LZCNT__ __MOVBE__ __XSAVE__` |
| x86-64-v4 | v3 + `__AVX512F__ __AVX512BW__ __AVX512CD__ __AVX512DQ__ __AVX512VL__` |

AArch64 uses armv8-a (NEON, the baseline), `+sve` (`__ARM_FEATURE_SVE`)
and `+sve2` (`__ARM_FEATURE_SVE2`). For pcrec's kernels the levels that
matter are v1 (SSE2, the baseline), v3 (AVX2) and v4 (AVX-512BW, for
64-byte compares and masked tails). v2's SSE4.2 adds `pcmpestri`, which is
slower than SSE2 compares for byte search (BELIEVED; the survey checks it).

#### 1.2.2 Two routes to compile an artifact for a level

- **Route M (macros), the consumer's flags.** pcrec emits one source with
  an `#if __AVX512BW__ / __AVX2__ / else` kernel ladder (R1's RB-3). The
  consumer compiles it with `-march=x86-64-v3`, and the level follows the
  consumer's flags. Every kernel inlines (B2/B3). Nothing changes per
  call. pcrec does not choose the level: K24's lesson.
- **Route A (attributes), pcrec declares the level.** `pcrec --isa=x86-64-v3`
  emits `__attribute__((target("arch=x86-64-v3")))` on every emitted
  function except the check. The artifact then gets the level under ANY
  consumer flags, and the kernels inline inside the target-attributed
  matcher, because caller and callee share the target. This is §0 item 5's
  remedy: the selection is hoisted to the whole artifact. The kernels'
  source must be the target-attributed form (RB-10), because route A
  cannot rely on `__AVX2__`.

Route A's attribute spelling is accepted by clang on both x86 targets
(compiled on the Mac). For gcc, `target("arch=...")` is documented, but its
interaction with a consumer's `-mno-avx2` and its acceptance of `-vN` names
are owed (the Linux run builds it: `isacost.c`'s detection functions carry
the attribute).

#### 1.2.3 The stamp (designed)

- `<PREFIX>_ISA_LEVEL`. In route M it is a preprocessor ladder over the
  macros above, emitted verbatim in every artifact, so the TEXT does not
  depend on the level: the probe's `ISA_COMPILED`. In route A it is a
  literal, the declared level. Spelled as a family string beside it is
  `<PREFIX>_ISA "x86-64-v3"`.
- `rx_info` gains `isa` (the level number) and `isa_family`. That is a
  layout change, so it is an `abi` bump plus match_api.md §6's spec hunk
  (D76/D94, D80).
- Route M with a DECLARED floor (`--isa=x86-64-v3 --isa-route=macro`) emits
  `#if <PREFIX>_ISA_LEVEL < 3` / `#error "artifact declared x86-64-v3:
  compile with -march=x86-64-v3 or later"`. That turns a consumer who
  forgot the flag into a compile error. Without it, the artifact silently
  builds at the baseline. That outcome is correct, and the stamp reports
  it.

#### 1.2.4 The check

`int <prefix>_cpu_ok(void)` returns 0, or a named error `PCREC_ERR_ISA`
(a new code in the caller-refusal class of `PCREC_ERR_STARTPOS`,
`PCREC_ERR_UNSET_VAR` and `PCREC_ERR_UTF`; D26 tier: the code is exact,
the wording is not).

It is pure and static-free. It is `cpuid`/`xgetbv` on x86 (the probe's
`cpu_level()`), and `getauxval` or `sysctlbyname` on AArch64. It is
**compiled at the BASELINE**: `target("arch=x86-64")` on x86, which
emitted 0 VEX/EVEX instructions in the v3 TU (clang ELF object,
disassembled; gcc is owed). On a v1 CPU it RETURNS the error rather than
faulting, provided the caller has not already executed v3 code itself.

It runs at one of four places:

| where | cost | what it gives | verdict |
|---|---|---|---|
| **(a) once, by the caller**, before the first match (documented precondition; `rx_info` lets a loader or catalog do it generically) | one query: about 930 ns macOS; x86 `cpuid` OWED | a named error, never SIGILL, for a caller who checks | **the design** |
| (b) at EVERY entry, by the artifact | the query per call: D1's cost, unless D2 is allowed | protection against a caller who did not check | only as opt-in `-fisa-check=entry` on Linux/ELF through D2 (an N-4 exception, Q5); never through `cpuid` |
| (c) "at the first call" | impossible without a memo: the first call is every call (§0 item 2) | — | not offered |
| (d) **by the loader**: `GNU_PROPERTY_X86_ISA_1_NEEDED` in `.note.gnu.property` | 0 per call; once at load | refusal before any code runs | **BELIEVED**, owed (isanote, §4) |

What the loader marker is BELIEVED to do (the Linux run checks each point):

- glibc ≥ 2.33 reads the marker of the executable and of every shared object
  it loads, and refuses with "CPU ISA level is lower than required"
  (`dlopen` returns that error).
- binutils writes the marker only under `-z x86-64-vN`. gcc and clang do not
  write it by default.
- It is an OR-merged property of the whole linked object. So an artifact
  that embeds it from source (`isanote.c`'s top-level asm; it parses
  correctly) **raises the requirement of the user's ENTIRE program**, not
  just the matcher. That blast radius is why it can only be opt-in (Q6).

glibc-hwcaps (`$LIB/glibc-hwcaps/x86-64-v3/libfoo.so`) is the loader
choosing among several builds of a shared library. It is a B1a mechanism
for a memfn LIBRARY, not for an emitted artifact. Mach-O has no ISA marker,
so on macOS only (a) applies.

**What fails, and how:**
- The check skipped on a CPU without the level: SIGILL at the first wide
  instruction. That may be in the caller's code, if the caller was
  compiled at the level too.
- Route M without the `#error` floor: a silent baseline build, which the
  stamp reveals.
- Route A on a toolchain that ignores the attribute: a build error, never
  a silent miscompile.

### 1.3 Hybrids: a baseline kernel always, a wider one behind a cheap test

- **H1, the per-call hybrid** (`flag_hyb`). The inline baseline arm costs
  nothing extra and the wide arm costs one call (§1.1). In an ARTIFACT, the
  only cheap tests are D2 (Linux, opt-in) and D8 (the caller's word).
- **H2, the span-gated hybrid.** The wide tier only pays above its knee:
  AVX2's 32-byte block by construction. The Mac stand-in pays from 64 B
  (2.28 against 3.25 ns) and 2x at 4 KiB. So the test sits on the long arm
  of R1's size-tiered body (§2.3 row 4's run-time arm). Below the knee the
  call never tests anything. Above it the test is amortized over at least
  the knee's bytes. **This is the hybrid worth having**, because it puts
  zero cost on the short-span calls that dominate the bench's per-call
  cells (k82diag §2: 6-11 B subjects).
- **H3, the entry-multiversioned hybrid.** `target_clones` on the
  artifact's search ENTRY makes one dispatch per match call, with the
  kernels inlined in each clone. It is D7 with every caveat of D7, and the
  artifact's code is multiplied by the clone count (the `[OPT-DIAL]` size
  term).

---

## 2. The decision: a first-match table

The first row whose predicate holds decides (the `dfa_pfs[]` idiom, memory
`pcrec-decisions-as-first-match-tables`). It composes with R1's §2.3
binding-form table: that table picks the FORM, and this one picks how the
form's ISA is SELECTED. Thresholds are per box and come from §1.1 and the
owed Linux run. None is a guessed constant.

| # | predicate | ISA selection | forms | why |
|---|---|---|---|---|
| 1 | the site's spans are below the wider tier's knee (every in-loop F5 skip over short runs; the short-subject per-call cells; any proven `maxw` < 32) | **baseline, compile time** (SSE2/NEON), no test | all | the wide tier cannot pay (§1.3 H2), and a test would only add cost |
| 2 | the form is B1a: libc, or memfn's own shared or static library | **the library's own dispatch** (ifunc, glibc-hwcaps, a constructor pointer: D3-D6) | B1a | legal there and already paid for; pcrec decides nothing (§4 of R1: the library has no policy, pcrec has no dispatch) |
| 3 | a level is DECLARED: pcrec `--isa=L` (route A), or the consumer's `-march` raises the macros (route M) | **compile-time at L**, with the `<PREFIX>_ISA_LEVEL` stamp, `rx_info.isa`, and `<prefix>_cpu_ok()` called once by the caller. The loader marker is opt-in (Q6) | B2, B3 (and B1b) | the kernels inline inside the target-attributed matcher (§0 item 5). Zero per-call cost. A named error, not SIGILL |
| 4 | the site is IN-LOOP (D91 budget 2) and no level is declared | **baseline only** | B2, B3 | a per-call test multiplies by the visit count AND forces the wide kernel out of line (§0 item 5) |
| 5 | a PREFILTER site (D91 budget 1) whose expected span is above the knee; ELF target; opt-in `-fisa-dispatch=cpu-supports` (Q5) | **H2**: an inline baseline short path, and on the long arm a D2 test plus a call to a target-attributed wide B1b helper | B1b behind B2 | the test lands only on calls long enough to amortize it. It depends on libgcc, an N-4 exception that is opt-in |
| 6 | otherwise | **baseline, compile time** | all | R1 row 6's safe default |

**Never**, as standing rules:
- a mutable static of the artifact's own (D3-D5) in emitted code (§5.3,
  TS-1);
- D7 multiversioning emitted by default (its lowering is the consumer's
  toolchain's choice, and one choice is a hidden mutable static);
- an uncached query (D1) on any per-call path;
- `__builtin_cpu_supports` on Darwin (it answers 0 for everything).

---

## 3. The probes

All live under `probes/`, are built by `probes/probes.mk`, and are never
built by pcrec's make.

- **`isacost.c`** times every §1.1 mechanism by span. x86-64: SSE2 base,
  AVX2 wide in a `target("avx2")` function; ifunc and `target_clones` on
  ELF; `cpuid`/`xgetbv` detection compiled at the baseline. AArch64: NEON
  base, a NEON64 stand-in, `sysctlbyname`/`getauxval` queries;
  `target_version` with clang. `--sel=base|wide` forces the cached arms.
  `--isa-report` prints the stamp-against-CPU verdict that a declared-ISA
  check would return.
  - `--check`: every runnable variant under both selections, n 0..300,
    every hit position, alignments 0..31, spans ending at the allocation's
    end. **gcc 26,179,776 cases, clang 31,997,504, clang
    ASan+UBSan 31,997,504: 0 bad.**
  - `make compile-x86` compile-checks the x86 paths on the Mac: ELF and
    Mach-O at x86-64, -v3 and -v4, with clang `-target`. The ELF object has
    the ifunc, the `target_clones` resolver and both clones.
  - The timed loop's barrier carries a `"memory"` clobber, so the dispatch
    state is re-read on every iteration as it would be between real calls.
    The probe's first draft lacked it; clang did not hoist the
    `__builtin_cpu_supports` load anyway, but nothing guaranteed that.
- **`isanote.c` + `isanote.sh`** (Linux x86 only) answer what the loader
  enforces. Each row is one of:
  - no marker (the control);
  - `ld -z x86-64-vN`, dynamic and static;
  - a source-embedded marker;
  - a `dlopen`ed `.so` carrying one;
  - an EVEX instruction with no marker and no check (the SIGILL control).

  Each row records `readelf -n`'s ISA-needed line, the exit code and the
  first output line. On a CPU that supports every level the refusal cannot
  be observed; the transcript's `ld.so --help` section says which levels
  the CPU supports, so the reader can tell.
- **`fmvdarwin.c` + `fmvdarwin.sh`** (Mac only) are §0 items 3-4's
  evidence: `__builtin_cpu_supports` and FMV lowering under Apple clang
  and LLVM clang, at the default and a 13.0 deployment target.
  BELIEVED-untested: whether a `__func_variants` binary loads on macOS
  before 26.

Transcripts: `probes/out/isacost.mac.{gcc,clang}.sel-{base,wide}.txt` and
`probes/out/fmvdarwin.mac.txt`.

---

## 4. Owed: the Linux x86 run (one script)

`probes/linux_run.sh` runs BOTH this note's probes and R1's `callcost`
(requirements.md §2.6), pinned with `taskset -c $CPU` (default 2) and
bounded by GNU timeout (`gnutimeout` on ubuntubudu). Run it from a
checkout's root, on a quiet box, after the current battery:

    sh docs/design/memfn/probes/linux_run.sh

It writes only `build/memfn_linux/<UTC stamp>/`: binaries, one transcript
per run with a provenance header (CPU model and flags, governor, load,
commit, glibc, gcc, clang), and `run.log`. The last line of `run.log` is
`MEMFN-LINUX-RUN COMPLETE <dir> fails=<n>`. It takes about 15 minutes.
Owed answers:

| question | transcript |
|---|---|
| U-1: glibc's `memchr` F and `n*`; whether fusion's margin holds on x86 | `callcost.linux.{gcc,clang,gcc-avx2}.txt` |
| U-8: AVX2's value over SSE2 by span (the H2 knee on x86) | `isacost.linux.*.sel-{base,wide}.txt`, `wide_ool` against `base_ool` |
| U-9: per-call cost of `__builtin_cpu_supports`, ifunc, `target_clones`, a pointer and a flag, against a direct call, on glibc | `isacost.linux.{gcc,clang}.sel-*.txt` |
| U-10: the cost of one `cpuid`+`xgetbv` detection (`det_query`), bare-metal or under whatever hypervisor the box runs | same |
| U-11: what `GNU_PROPERTY_X86_ISA_1_NEEDED` actually enforces (executable, static, `dlopen`; linker-written and source-written) | `isanote.linux.txt` |
| U-12: gcc's `target("arch=x86-64")` keeps the check path VEX-free in a `-march=x86-64-v3` TU | `isacost.evidence.txt` (objdump of `cpu_level`) |
| the declared-ISA form's cost (`wide_inl` in the v3 TU) and the stamp's verdict | `isacost.linux.*-v3.*.txt` |

The manager runs it. This lane ran nothing on the Linux box.

---

## 5. Requirements that follow

New rows, in R1's numbering:

- **RB-10 Every ISA tier compiles in a baseline TU.** Each wider-tier
  kernel exists as a target-attributed function (`target("avx2")`,
  `target("avx512bw")`, `target("+sve")`) that compiles WITHOUT `-m` flags,
  as well as under them through RB-3's macros. Without it, no dynamic or
  route-A selection can reach the tier (§0 item 6).
- **RB-11 Static-free CPU detection.** The library exposes a pure
  `level()` / `has(feature)` that reads the CPU or OS directly: `cpuid` +
  `xgetbv` (the OS's AVX/AVX-512 state, not only the CPU bit), `getauxval`
  or `sysctlbyname`. It holds no cache, needs no constructor, makes no libgcc
  call, and is compiled at the baseline. It is also the body of any
  emitted `<prefix>_cpu_ok()`.
- **RB-12 Compiled-level macro.** The library defines its compiled-for
  level (`<P>_ISA_LEVEL`) from predefined macros, the probe's
  `ISA_COMPILED`, so a consumer's stamp is one `#define` away.
- **RB-13 Dispatch only out of line, with every tier still named.** RB-8,
  sharpened: any run-time dispatch the library offers (D3-D7) lives in its
  out-of-line form; every tier keeps a direct name (`find_byte_avx2`); and
  the dispatch's per-call cost is reported, as the probe's `fnptr` row
  against `base_ool`.
- **N-12 The check runs at the baseline.** No VEX/EVEX instruction on the
  detection path, verified in the disassembly per compiler (N-8's method).
- **N-13 Never SIGILL by design.** Every wider tier has a check path that
  returns a named error (RB-11). A use that skips it is documented as the
  caller's precondition, never left implicit.
- **N-14 No `__builtin_cpu_supports` on Darwin.** Where a library uses D2
  for dispatch, its Darwin path uses `sysctlbyname` once, or the baseline.

Corrections to R1 (made in `requirements.md` in this change, each pointing
here):
- §0 item 5: Mach-O has a loader dispatch on Apple clang (§0 item 4).
- N-4: D2 is a candidate opt-in exception for Linux artifacts (Q5).
- RB-8: now RB-13.

---

## 6. Rubric additions (for R2, the survey)

R1's §5.2 gains three nice-to-haves, each scored 0-3. The maximum score
becomes 69 + 3 × (2 + 1 + 1) = **81**.

| # | nice-to-have | weight |
|---|---|---|
| H-14 | **declared-ISA builds**: every tier reachable by `-march` (RB-3) AND by target attribute in a baseline TU (RB-10), with a compiled-level macro (RB-12) | 2 |
| H-15 | **cheap dynamic dispatch** in its out-of-line form (D4/D6/D7) with direct per-tier names (RB-13), and its per-call cost measured against a direct call | 1 |
| H-16 | **static-free CPU detection** compiled at the baseline (RB-11, N-12), correct on Darwin (N-14) | 1 |

M-5 ("no mandatory run-time dispatch or mutable static") stands, and is
read with §2's rows. A candidate whose only path to AVX2 is a
constructor-set pointer fails M-5 as a TEXT source for B2/B3. It remains
scorable for its out-of-line form (§5.4 ideas-only).

---

## 7. Unknowns this note adds

| # | unknown | answered by |
|---|---|---|
| U-9 | the per-call cost of D2, D6, D7, D4 and D3 on glibc x86 | §4's run |
| U-10 | `cpuid` cost on ubuntubudu (bare metal or VM) | §4's run (`det_query`) |
| U-11 | what the x86 ISA marker enforces, and whether a source-embedded one survives the link | §4's run (`isanote`) |
| U-12 | gcc's `target("arch=...")` semantics against consumer `-m` flags; the VEX-free check under gcc | §4's run, then the build's N-12 check |
| U-13 | SVE dispatch cost and value | no box: the survey's ideas, or a future Graviton-class box |
| U-14 | whether Apple `__func_variants` binaries load on macOS < 26 | an older-macOS box, if a Mac D7 use is ever proposed |

---

## 8. Questions for Frank

4. **Q4, the declared-ISA design.** Should §1.2 (route A `--isa=LEVEL`,
   with route M and its `#error` floor; the stamp; the caller-once
   `<prefix>_cpu_ok()`) be the design of record for when the build lane
   gets there? **Recommendation:** yes. Build it only behind its D77
   trigger: the Linux run showing AVX2 paying at a measured site (U-8 at a
   real prefilter span).
5. **Q5, `__builtin_cpu_supports` in Linux artifacts.** Should it become an
   opt-in exception to N-4 (`-fisa-check=entry`, `-fisa-dispatch=
   cpu-supports`)? It is §5.3-legal (the state belongs to libgcc) and
   TS-1-clean, but it adds a runtime-library dependency, is unavailable
   freestanding, and is wrong on Darwin. **Recommendation:** decline until
   U-9 is measured. If it is cheap, admit it as an opt-in, ELF-only and
   never default, because route A with a caller-once check already gives
   zero per-call cost.
6. **Q6, the loader marker.** Should `--isa=x86-64-vN` also embed
   `GNU_PROPERTY_X86_ISA_1_NEEDED`? It is the only check that runs before
   any of the caller's code, but it raises the whole program's
   requirement. **Recommendation:** decide after U-11. If glibc enforces
   it for executables and `dlopen`, offer it as a separate opt-in
   (`--isa-marker`) that is never implied by `--isa`.
