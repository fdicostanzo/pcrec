# memory-functions: R1c, ISA SELECTION CROSSED WITH THE USE CASE

Owner row: `[MEMFN]` (docs/dev/plan.md), step R1c, an evaluation over
`isa_selection.md` (R1b). It cross-notes `[ART-MGR]` and `[V-E]`. Lane
`memfneval`, 2026-10-04, written from main at e2f57982. This is a design
evaluation only: no probe was run, nothing under `src/`, `cli/`, `lib/` or
`tests/` changes, and no emitted byte moves (D91). Every emitted-text or
`rx_info` change below is DESIGNED, not built. Building one is an `abi`
event plus a `docs/spec/` hunk (D76/D94, D80).

Frank's ask (2026-10-04): *"we should do an evaluation on the best approach
to arch selection crossed with the use case for it; it may be one solution
emerges or several. Also for the mix — we output several artifacts with
rx_info so perhaps the selection utility we have parked can pick based on
arch."* Linux x86-64 is the primary architecture.

Every cost below comes from `isa_selection.md` §1.1 (Mac M1, directional
only, D144 addendum 1) or `requirements.md` §0/§2.4. Where the cost is a
Linux number nobody has taken, the cell says OWED and names the unknown
(U-n). The "parked selection utility" is `[V-E]`'s organizer, which
`[ART-MGR]` carries as layers L0 (the `rx_info` entry pointers, stage S1)
and L1 (the catalog, stage S2), with L2 (the hosted loader, S3/S4) above
them.

---

## 0. Findings first

1. **One mechanism wins, applied at three places.** The unit is the
   DECLARED-ISA ARTIFACT: one level, fixed at build, stamped, with every
   kernel inlined at that level and no dispatch inside it. Selection
   between levels happens ABOVE the artifact, never inside it. There are
   three places it can happen:
   - the caller, for one build aimed at a known box;
   - the L1 catalog, which picks among N variants linked into one binary;
   - the L2 loader, which picks among N shared objects or cache entries.

   Approach (d), multi-artifact selection, is not a rival to the
   declared-ISA artifact. It is that artifact's generalization to N levels.
   A memfn LIBRARY (B1a) is the one case outside this: it keeps its own
   dispatch (ifunc or a constructor-set pointer), which is legal there and
   none of pcrec's business (isa_selection.md §2 row 2).
2. **Every per-call dynamic test loses everywhere it is legal.** That covers
   D1, D2, the D8-in-`rx_ctx` hybrid and multiversioning. The cases:
   - In-loop sites (D91 budget 2) cannot take one: the test multiplies by
     the visit count, and the wide kernel is forced out of line
     (isa_selection.md §0 item 5).
   - Prefilter sites can take one through H2, the span-gated hybrid. But a
     declared or (d) build gets the same wide kernel inlined, at zero cost
     per call.

   The per-call hybrid's one remaining advantage is CODE SIZE. It adds one
   helper per site, where (d) adds a whole artifact per level. So it stays
   HELD (not declined) for a single size-dialed binary aimed at unknown
   CPUs, decided after U-9 (Q11).
3. **(d) is legal under every contract today, if the pick returns a pointer
   and the CALLER holds it.** The L1 catalog is generated code. Under
   artifact_manager.md §4.4 it is all `const`, so it cannot memoize the
   pick. Its helper is a pure function, `pick(group, level)`, and the CPU
   level comes from a pure, baseline-compiled `cpuid` function (RB-11). The
   caller keeps the result. That is D8, the caller's word, which is the one
   dispatch word an artifact may lean on. L2 is hosted and has mutable
   state by definition, so it caches per handle.
4. **The pick is a first-match table by construction.** A variant group is
   an ordered row list, highest level first, and the first row whose level
   is ≤ the CPU's level is executed (the `dfa_pfs[]` idiom). It is also
   D46-shaped:
   - it is OBSERVABLE: the picked member's `rx_info.isa` says which variant
     runs;
   - it is FORCEABLE: the caller passes the level, so a test can run every
     variant on one box.
5. **(d) has two fences, and the static link forbids one of them.** The
   loader's ISA marker (`GNU_PROPERTY_X86_ISA_1_NEEDED`) is OR-merged over
   the whole linked object (BELIEVED, U-11).
   - A static catalog that links a v3 variant beside a v1 variant must
     therefore carry NO marker. With one, the whole program refuses to load
     on the v1 box the v1 variant exists for.
   - Under L2 each variant is its own `.so`, so the marker is per-object.
     There it becomes a free second fence: `dlopen` refuses the wrong one
     cleanly.

   Whether a distro toolchain writes the marker unasked for `-march=v3`
   objects is a new Linux question (L-4).
6. **K79's fix is what makes the variants honest.** Before abi 54 the
   prefix LENGTH moved the VM entry shape. Variants `rx_v1`/`rx_v3` would
   then have differed in more than their ISA. Since the fix the emitters
   see a canonical placeholder prefix (`\x01q`). N variants of one request
   differ by construction only in what `--isa` moves. K80's fix (the valued
   ABI guard, a mixed-abi TU fails to compile) is L1's own prerequisite and
   is also discharged.
7. **The cheapest measurement that could change the verdict is not in
   `linux_run.sh`.** It is the bench's existing artifacts compiled at
   `-march=x86-64-v3` against the baseline, before any memfn kernel
   exists (L-2, §3.3). If gcc's own vectorization and BMI2 already pay,
   then declared-ISA and (d) have a customer NOW, ahead of memfn. If they
   do not, the whole axis waits for memfn's wide kernels and the U-8 knee.

---

## 1. The matrix

### 1.1 Rows and columns

Rows (approaches; isa_selection.md's D-numbers in brackets):

| id | approach |
|---|---|
| A0 | **baseline only** (SSE2/NEON at compile time, no test): the control row and today's shipped state |
| A1 | **per-call dynamic test inside the artifact**: (A1q) an uncached query every call [D1]; (A1s) `__builtin_cpu_supports` every call [D2] |
| A2 | **dispatch once in a LIBRARY**: ifunc [D6], a constructor or init-set function pointer [D4], a lazy pointer [D5], multiversioning [D7] |
| A3 | **declared-ISA artifact**: route A (`--isa=L`, target attributes) or route M (the consumer's `-march`), the `<PREFIX>_ISA_LEVEL` stamp, `rx_info.isa`, and `<prefix>_cpu_ok()` called once by the caller (isa_selection.md §1.2) |
| A4 | **hybrid**: an inline baseline kernel plus a wide out-of-line (B1b) kernel behind a cheap test. Tested by D2 (A4s, ELF opt-in) or by the caller's word in `rx_ctx` (A4w, D8, an `abi` field); span-gated (H2) |
| A5 | **(d) multi-artifact selection**: N declared-ISA artifacts of one request, each stamped; the L1 catalog or the L2 loader picks the highest level ≤ the running CPU's (§2) |

Columns (use cases):

| id | use case |
|---|---|
| U1 | a **memfn library function** called out of line (B1a external, B1b local helper) |
| U2a | a kernel **inlined or injected** in an artifact at a **prefilter** site (B2/B3, D91 budget 1: about once per match point) |
| U2b | a kernel **inlined or injected in the loop** (B2/B3, D91 budget 2: per state visit; a stay skip, a scan edge, a VM cursor run) |
| U3 | **one binary shipped to unknown x86-64 CPUs** |
| U4 | **a build for a known deployment box** |
| U5 | **a program holding many artifacts** (M patterns) |
| U6 | **a `dlopen`ed `.so` plugin** (the bench shim's shape; `[ART-MGR]` L2) |

### 1.2 The summary

Each cell gives the verdict and its dominant term. The 5-attribute detail is
§1.3. Legend: **BEST** (recommended for that use case), ok (legal and sound,
not preferred), opt (opt-in only), — (illegal or not applicable).

| | U1 library call | U2a prefilter | U2b in-loop | U3 unknown CPUs | U4 known box | U5 many artifacts | U6 `.so` plugin |
|---|---|---|---|---|---|---|---|
| **A0 baseline** | ok: no wide tier | ok: the default (isa_selection.md §2 row 6) | **BEST until a level is declared** (§2 row 4) | ok: safe, slow on long spans (2x at 4 KiB, Mac stand-in) | ok: leaves the box's ISA unused | ok | ok |
| **A1q query per call** | — on any hot path (~930 ns Mac; `cpuid` OWED U-10) | — | — | — | — | — | — |
| **A1s cpu_supports per call** | ok, but A2 is cheaper to reason about | opt (N-4 exception, ELF; Q5); answers 0 on Darwin | — (per visit, forces out of line) | opt (the A4s form) | — (A3 is free) | opt; each artifact pays separately | opt; each `.so` carries libgcc's constructor |
| **A2 library dispatch once** | **BEST** (ifunc on ELF, a pointer elsewhere; RB-13) | — in emitted text (§5.3/TS-1) | — | **BEST for U1's library**; — for an artifact | ok (the library can just build at `-march`) | n/a (one library serves all) | ok: the library `.so`'s own resolver; glibc-hwcaps |
| **A3 declared ISA** | ok: a `-march` build of the library (RB-3/RB-12) | **BEST when a level is known**: inlined at L, 0 per call | **BEST when a level is known** (isa_selection.md §2 row 3) | ok only at L = v1; above v1 a v1 CPU gets a clean refusal and no service | **BEST**: one artifact, `cpu_ok()` once | ok: one `cpu_ok` serves all (one level) | ok: `dlopen`, then `cpu_ok`; the marker is a free fence (U-11) |
| **A4 hybrid (H2)** | ok inside the library (that is A2 with a size knee) | opt: zero below the knee, one test plus one call above | — | opt: the SIZE-CONSCIOUS alternative to A5 (held, Q11) | — (A3 is free) | opt; one helper per site per artifact | opt (A4s needs libgcc in the `.so`) |
| **A5 (d) multi-artifact** | ok: glibc-hwcaps is exactly this for a library | **BEST for U3/U5/U6** (inherits A3's 0 per call) | **BEST for U3/U5/U6** (inherits A3's form) | **BEST**: v1 always present, best level served, 0 per call; costs N× text | over-built: A3 suffices | **BEST** with an L1 catalog: one level query for all M groups | **BEST** with L2: picks the `.so` before loading it |

### 1.3 Per-approach cells

"Cost" is per call unless it says otherwise. Code size is stated
STRUCTURALLY, because no lane has measured bytes for any ISA variant;
every byte figure is unmeasured.

#### A0 baseline only

| use | legal | cost | failure mode | complexity | code size |
|---|---|---|---|---|---|
| U1 | yes | base_ool 1.64 / 2.30 ns at n=16 (gcc / clang); 108-110 ns at 4 KiB | none | none | 1× |
| U2a | yes | base_inl 1.63 / 1.31 at n=16; 107-113 at 4 KiB | none | none | 1× |
| U2b | yes | the same | none | none | 1× |
| U3 | yes | the wide tier's gain is forgone: 2x at 4 KiB on the Mac stand-in; x86 OWED (U-8) | none | none | 1× |
| U4-U6 | yes | as U3 | none | none | 1× |

#### A1 per-call dynamic test inside the artifact

| use | legal | cost | failure mode | complexity | code size |
|---|---|---|---|---|---|
| U1 | yes (a library may) | A1q: ~930 ns Mac (`sysctlbyname`), `cpuid` OWED (U-10; BELIEVED tens to hundreds of cycles bare, µs under a hypervisor). A1s: ≈0 Mac; x86 OWED (U-9) | A1s returns 0 on Darwin, so it silently picks the baseline. A1s is unset before constructors run | low | + the wide arm |
| U2a | A1q: §5.3-legal but never on a hot path. A1s: §5.3-legal, TS-1-clean, but **N-4 forbids it** (opt-in exception, Q5) | as U1, amortized over the scan | as U1; with no libgcc it fails to link | medium: an N-4 exception plus ELF-only gating | + one B1b helper per site |
| U2b | **no**: the test multiplies by the visit count, and the wide kernel is never inlined into baseline code (§0 item 5) | — | — | — | — |
| U3 | as U2a | as U2a | as U2a | medium | + helpers |
| U4 | pointless: the level is known, and A3 costs 0 | — | — | — | — |
| U5 | as U2a | each of the M artifacts pays its own test at each site | as U2a | medium | + helpers × M |
| U6 | as U2a | as U2a | each `.so` links libgcc's `__cpu_model` and its constructor (BELIEVED a per-`.so` copy from `libgcc.a`) | medium | + helpers |

#### A2 dispatch once, in a LIBRARY

| use | legal | cost | failure mode | complexity | code size |
|---|---|---|---|---|---|
| U1 | yes: the library owns mutable state legitimately (glibc's `memchr` is this) | fnptr = a direct call ±0.06 ns (Mac); ifunc is a PLT indirect, OWED (U-9); Mac FMV +0.3-0.4 ns. glibc's call term ~3.4 ns (k82diag; U-1) | a pointer that is never initialized is a NULL call unless it starts at the baseline. ifunc: resolver order in static binaries. LLVM clang FMV is a hidden mutable static | low in the library; RB-13 asks for direct per-tier names too | every tier in one library |
| U2a, U2b | **no** in emitted text (§5.3, TS-1). D7 multiversioning is toolchain-dependent (a hidden static under one lowering) | — | — | — | — |
| U3 | yes, for the library a binary calls | as U1 | as U1 | low | as U1 |
| U4 | yes, but a `-march` build of the library is simpler | 0 with a static build | — | low | 1 tier |
| U5 | n/a: one library serves every artifact | as U1 per call | as U1 | low | once per program |
| U6 | yes: the library `.so`'s own resolver, or glibc-hwcaps subdirectories (`$LIB/glibc-hwcaps/x86-64-v3/`) | as U1 | hwcaps needs glibc ≥ 2.33 and a name search, so an absolute-path `dlopen` bypasses it | low | N builds on disk (hwcaps) |

#### A3 declared-ISA artifact (stamp plus a caller-once check)

| use | legal | cost | failure mode | complexity | code size |
|---|---|---|---|---|---|
| U1 | yes: a library compiled at `-march`; RB-12's compiled-level macro | 0 per call | a library built at v3 running on a v1 CPU: SIGILL unless it checks | low | 1× at L |
| U2a | yes: route A's target attributes or route M's macros; §5.3/TS-1 clean | **0 per call**. The Mac stand-in: wide_inl 0.97 / 1.30 at n=16 against base_inl 1.63 / 1.31, and 53 against 107-113 at 4 KiB. x86 OWED (isa_selection.md §4, the `-v3` transcripts) | the caller skips `cpu_ok()`: SIGILL on a lower CPU (N-13: a documented precondition). Route M without the `#error` floor builds a silent baseline, which the stamp reveals | medium: a CLI flag, the stamp, an `rx_info` field, the check, the error code | 1× at L |
| U2b | yes: the same inlined form | 0 per call | as U2a | as U2a | 1× |
| U3 | only at L = v1. Above that, a lower CPU gets `PCREC_ERR_ISA`: clean, but no service | 0 | a clean refusal (good); a skipped check gives SIGILL | as U2a | 1× |
| U4 | **yes, the natural fit** | 0 per call; one `cpu_ok()` at startup (`cpuid` OWED, U-10) | as U2a | as U2a | 1× |
| U5 | yes. Every artifact shares one level, so one check serves all M | 0 | as U2a | as U2a | M× |
| U6 | yes: `dlopen`, then `cpu_ok()` before the first match. With the opt-in marker, `dlopen` itself refuses (BELIEVED; U-11) | 0 | as U2a; with the marker the refusal comes before any code runs | as U2a | 1× |

#### A4 hybrid: an inline baseline plus a wide B1b behind a cheap test (H2)

| use | legal | cost | failure mode | complexity | code size |
|---|---|---|---|---|---|
| U1 | yes: inside the library this is A2 plus RB-4's size tiers | below the knee 0; above it one test plus one call (wide_ool) | as A2 | low | as A2 |
| U2a | A4s: opt-in, ELF only, N-4 exception (Q5). A4w: legal everywhere, but `rx_ctx` gains a level field (an `abi` event) | below the knee: base_inl, 0 extra (flag_hyb's base arm 0.98 / 1.65 against base_inl 1.63 / 1.31: layout noise). Above it: the wide arm = wide_ool (1.92 / 2.27 at n=16; 53 at 4 KiB), so +0.3-1.0 ns over the inlined declared form at short spans and nothing at long ones | A4s: 0 on Darwin, silently baseline. A4w: a caller who passes a wrong level gets SIGILL | high: two kernels per site, a knee constant per box, a test path, and per-compiler N-8 verification | + one target-attributed helper per site |
| U2b | **no** (isa_selection.md §2 row 4) | — | — | — | — |
| U3 | opt: the one use where A4 is not dominated, because A5 costs N× text and A4 one helper per site | as U2a | as U2a | high | ≈1× + helpers |
| U4 | dominated by A3 (0 per call, inlined) | — | — | — | — |
| U5 | opt | as U2a, per site per artifact | as U2a | high | M× (1 + helpers) |
| U6 | opt (A4s needs libgcc in the `.so`) | as U2a | as U2a | high | as U3 |

#### A5 (d) multi-artifact selection

| use | legal | cost | failure mode | complexity | code size |
|---|---|---|---|---|---|
| U1 | yes: glibc-hwcaps is (d) for a library, done by the loader | as A2 | as A2 (hwcaps) | low | N builds |
| U2a, U2b | yes: each variant is A3, so every kernel is inlined at its level | **0 per call**, A3's figures. The pick runs once: one `cpuid` (U-10) plus a run scan within the name group in the catalog. Calls through `rx_entries` pointers cost the same as a direct call (the fnptr row; an artifact entry is never inlined into its caller anyway) | the pick never chooses above the CPU, so failure is impossible while the group holds a v1 member. A caller who bypasses the pick and calls `rx_v4_search` by name: SIGILL (N-13) | high: §2's whole design, needing [V-E] S1 + S2 | N× text per pattern (§2.4) |
| U3 | **yes, the best**: v1 is always in the group, so the pick is total | 0 per call; startup once | as above; plus §2.6's marker hazard on a static link | high | N× text; resident ≈ 1× (BELIEVED, page-granular) |
| U4 | yes, but over-built: A3 suffices | — | — | — | — |
| U5 | **yes, the best with L1**: one level query, M picks | 0 per call; M picks once | as U3 | the catalog's job, already chartered (S2) | M·N artifacts; M·N gcc runs |
| U6 | **yes, the best with L2**: the loader picks the `.so` from its sidecar, or from the cache key's level, BEFORE `dlopen` | 0 per call; one pick per handle | the opt-in marker makes a wrong `dlopen` a clean refusal: a second fence (U-11) | the loader's job (S3/S4) | N `.so` on disk; 1 resident |

---

## 2. Approach (d): multi-artifact selection

### 2.1 The shape

One compile request (pattern plus options) is emitted N times, once per
level in a declared LEVEL SET. Each copy is a complete declared-ISA artifact
(A3) with its own prefix and file (D88: one artifact per file). An emission
set's manifest header lists all N. Something above the artifacts picks one
at startup or at load. Nothing inside any artifact changes from A3. (d)
adds no emitted dispatch at all, so the §5.3/TS-1 question never arises for
the artifacts. It arises only for the PICKER, which §2.2 places.

### 2.2 Where the pick happens

| # | pick site | mechanism | holds the result | legal | verdict |
|---|---|---|---|---|---|
| P1 | **the caller, by hand** | the caller calls each variant's `cpu_ok()` in order and keeps the first that passes | the caller | yes | works with A3 alone and needs no L1. It is the U4 path applied N times. Fine for one or two patterns |
| P2 | **L1 catalog, static** (`[ART-MGR]` S2) | the composer emits a VARIANT GROUP per request: an ordered row list `{level, const struct rx_info *}`, highest level first. Also a pure `<catalog>_pick(group, level)` that returns the first row whose level ≤ `level`, and a pure, baseline-compiled `<catalog>_cpu_level()` (RB-11's body: `cpuid` + `xgetbv`) | **the caller** (D8). The catalog is `const` (artifact_manager.md §4.4) and cannot memoize | yes: §5.3 binds no mutable state because there is none. The helper is an emitted compare loop, freestanding on x86 (`cpuid` is an instruction; `<cpuid.h>` is static-inline, with no libgcc call) | **recommended for U3/U5**. The level is an ARGUMENT, so the pick is forceable (D46) and testable at every level on one box |
| P3 | **L2 loader** (`[ART-MGR]` S3/S4) | the loader reads each candidate's level from its SIDECAR (R8.2, no `dlopen`) or from the cache key (R5.1(f)), takes the first ≤ the CPU's, then `dlopen`s it | the handle (L2 may hold mutable state) | yes: hosted by definition | **recommended for U6**. It is one mechanism on both OSes. glibc-hwcaps is a Linux-only alternative, and an absolute-path `dlopen` bypasses it |
| P4 | an **emitted ifunc** per group entry (`<catalog>_<name>_search` resolving to the best variant) | the ELF loader writes the GOT slot | the loader | ELF only. The resolver needs raw `cpuid` (static-free) or D2 | **not first**. It is the one way a caller who calls BY SYMBOL gets (d) transparently, but it is ELF-only, a PLT indirect on every call (U-9), and has resolver-order hazards in static binaries. Held behind a named consumer who must call by symbol |

**AArch64.** P2's `cpu_level()` needs `getauxval` on Linux and
`sysctlbyname` on macOS, both libc calls. That breaks L1's freestanding
rule (artifact_manager.md R2.4) on that architecture. AArch64's only real
level choice is NEON against SVE: no Apple core has SVE, and pcrec has no
Graviton-class box (U-13). So on AArch64, (d) is single-variant today. The
pick takes the level as an argument precisely so that a hosted caller
can supply it there.

### 2.3 What the stamp must hold

Per artifact (all of it already in isa_selection.md §1.2.3's design, so (d)
adds nothing to the ARTIFACT):

- `rx_info.isa_family` (x86-64, aarch64) and `rx_info.isa`: the level the
  code REQUIRES. Under route M the initializer is the preprocessor's
  `<PREFIX>_ISA_LEVEL`, so the field is truthful under the consumer's flags
  and the text stays level-independent. Under route A it is the declared
  literal.
- The `<PREFIX>_ISA_LEVEL` / `<PREFIX>_ISA` macros, for compile-time
  consumers.

What the stamp must NOT be asked to hold: "which artifacts are variants of
one another". Name equality does not answer it, because one definition
under three configs is three artifacts with one name (artifact_manager.md
§2). A request hash in `rx_info` would duplicate R5.2's pcrec-published
key. **The composer that emits the variants already knows the group**, so
the group is a catalog-side row list (P2) or a loader-side sidecar field
(P3). The artifacts carry only their own level (Q8).

The level is a NUMBER on a ladder: x86-64 psABI v1..v4, and on AArch64
0 = NEON, then SVE, then SVE2. A feature bitmask is not needed: the pick
compares levels, and the psABI levels are the ladder every distro ships.
If a non-ladder feature is ever needed (AVX10 subsets, say), `isa` becomes
the ladder position and a mask field is appended (`[DD-13c]`'s
append-only shape).

### 2.4 The cost of N variants

| term | cost | note |
|---|---|---|
| per call | 0 | inherits A3; the call goes through an `rx_entries` pointer (= a direct call) or the variant's own symbol |
| per startup | one `cpu_level()` (U-10) + M picks | each pick is a scan of ≤ N rows |
| emitted C | N× per pattern | D84's caps apply PER VARIANT. A catalog's total is N× the dial's per-artifact figure (`[OPT-DIAL]`'s size term) |
| gcc time | N× per pattern | gcc dominates large artifacts (artifact_manager.md §4.7). The bench times it per phase |
| binary `.text` | N× per pattern, unmeasured | — |
| resident memory | ≈ 1× | BELIEVED. The variants sit in separate TUs, so their text is contiguous per variant, and pages of unpicked variants are never touched. Unmeasured |
| disk (L2) | N `.so` per pattern | the loader `dlopen`s one |
| link | N prefixes per pattern | R2.6 (no duplicate prefixes) holds. The (name, config) duplicate report must treat `isa` as part of config |

N stays small if the level set is fixed (Q9): {v1, v3} is enough for most,
and v4 only where AVX-512's 64-byte compares or masked tails measurably
pay. v2 adds `pcmpestri`, which is BELIEVED slower than SSE2 compares for
byte search (isa_selection.md §1.2.1), so it is not offered. Never
`-march=native`. A native build is keyed to one CPU model, so a cache in
a home directory shared across boxes would hold an entry that is a SIGILL
on the next box. A psABI level is a bounded, shareable key.

### 2.5 How (d) composes with the clean-fail check

- **The pick SUBSUMES the check.** `pick(group, cpu_level())` never returns
  a member above the CPU. With a v1 member in the group (Q9: mandatory),
  the pick is TOTAL, so it never fails and needs no error path.
- **Without a v1 member** (a deliberately v3-only group, as in A3 for U4)
  the pick returns NULL. The caller maps that to `PCREC_ERR_ISA`, the same
  code `cpu_ok()` returns (isa_selection.md §1.2.4), so one error answers
  both routes.
- **Each artifact still emits its own `cpu_ok()`**, for callers who use it
  standalone by symbol. The catalog's `cpu_level()` is the same body
  emitted once. It is BASELINE-compiled (N-12), and it lives in the
  catalog's TU, which is compiled at the baseline anyway, so no variant's
  `-march` reaches it.
- **Bypassing the pick** (calling `rx_v3_search` by name) is A3's
  skipped-check case: SIGILL on a lower CPU, a documented precondition
  (N-13).

### 2.6 Hazards specific to (d)

| hazard | what goes wrong | fence |
|---|---|---|
| **H-a the ISA marker on a static link** | `GNU_PROPERTY_X86_ISA_1_NEEDED` is OR-merged over the linked object (BELIEVED, U-11). So a v3 variant carrying it, linked beside a v1 one, makes the whole program refuse to load on v1 | a static catalog's variants MUST NOT carry the marker. Q6's `--isa-marker` is refused in combination with catalog membership. Owed: does the ubuntubudu toolchain write the marker UNASKED for a `-march=x86-64-v3` object? (L-4; `isanote.sh` has no such row) |
| **H-b the marker under L2** | none: per-object, checked at `dlopen` (BELIEVED) | under L2 it is a SECOND fence; the loader could even rely on it (try `dlopen` from the highest level down), if U-11 confirms |
| **H-c COMDAT merge across levels** | a non-`static` `inline` function, or a weak symbol, emitted identically in two variants is merged by the linker. The v1 caller can then get the v3 copy | BELIEVED absent today: emitted functions are `static` or prefix-unique externs, and the ABI block is types only. It is a check to write with the build, in TS-1's grep shape: no non-static inline or weak definitions in emitted text |
| **H-d answer identity across variants** | route M's `#if` ladder selects DIFFERENT kernel text per level. A level-specific kernel bug answers wrongly only on that level's CPUs | a level axis in `test-axes`' shape. Route A with a forced level lets a v4 box run every variant (P2's level argument, D46). memfn's N-6 covers the kernels themselves |
| **H-e K79 (fixed)** | variants differing in more than ISA because their prefixes differ in length | discharged at abi 54: the emitters see the canonical placeholder prefix |
| **H-f K80 (fixed)** | the manifest header includes all N variants in one TU | discharged at abi 54: same abi passes, mixed abi is a compile error naming the cause. R2.5's generation-time refusal stays the second fence |
| **H-g a native build in a cache** | a shared home directory across boxes | never `-march=native`. Cache keys carry the psABI level, and a hit is re-checked against the CPU on lookup |

### 2.7 Dependencies, and what each costs as an `abi` event

| piece | row / stage | `abi`? |
|---|---|---|
| `rx_info.isa`, `rx_info.isa_family`, `<PREFIX>_ISA_LEVEL`, `<prefix>_cpu_ok()`, `PCREC_ERR_ISA`, `--isa` | `[MEMFN]` / isa_selection.md §1.2 (A3); behind its own D77 trigger (Q4) | yes: `rx_info` layout and emitted scaffolding (D76/D94), a match_api.md §6 hunk and a `PCREC_ERR_*` code (D80) |
| `const struct rx_entries *entries` (and `prefix`) | `[V-E]` item 1 = `[ART-MGR]` S1 | yes (artifact_manager.md §6 S1) |
| the variant group, `pick()`, `cpu_level()` in the catalog | `[ART-MGR]` S2 plus this note's addition | a new EMISSION (L1). It moves no artifact byte, but its own contract is spec (D80) |
| the sidecar's level field, a loader pick | `[ART-MGR]` S3/S4 | no artifact change |
| K79, K80 | fixed (abi 54) | — |

If A3 and S1 are both built, they can land as ONE `abi` event. Neither has
fired its trigger today.

---

## 3. Verdict

### 3.1 The recommended combination

One mechanism emerges. The use case decides only WHERE its selection runs:

1. **Inside an artifact: no run-time dispatch, ever, by default.** Every
   kernel is selected at compile time, at the baseline or at a declared
   level. This is isa_selection.md §2's table unchanged: rows 1, 3, 4 and 6
   cover it, and row 5 (H2 with D2) stays opt-in and held.
2. **The unit is the declared-ISA artifact (A3)**: one level, stamped in
   `rx_info`, with a static-free baseline check.
3. **Selection between levels is hoisted ABOVE the artifact**, to the
   cheapest holder of the dispatch word for the use case:

   | use case | who picks | how |
   |---|---|---|
   | U4 known box | the build | A3 at the box's level, `cpu_ok()` once |
   | U3 unknown CPUs, U5 many artifacts | the L1 catalog (P2) | (d): a variant group, a pure `pick`, the caller holds the result |
   | U6 plugins and the cache | the L2 loader (P3) | (d): pick from the sidecar or key level, then `dlopen` |
   | fallback for any of them | the caller (P1) | `cpu_ok()` in order |

4. **A memfn library (U1) keeps its own dispatch** (A2: ifunc or a
   constructor pointer, with direct per-tier names, RB-13). That lives
   outside emitted text, and pcrec decides nothing there.
5. **The per-call hybrid (A4) is HELD**, as the size-dialed alternative to
   (d) for one binary aimed at unknown CPUs. It is the only cell where (d)'s
   N× text could lose. It is decided on U-9 and the dial's size term,
   never default.

Why this combination:
- It is the only one that puts **zero per-call cost on BOTH D91 budgets**.
- It inlines the wide kernel instead of crossing a call (isa_selection.md
  §0 item 5).
- It keeps **every artifact static-free** (§5.3/TS-1) without an N-4
  exception.
- It works the **same on ELF and Mach-O**. P2 and P3 are one mechanism
  each on both, unlike ifunc or FMV.
- It **reuses the organizer already chartered** (`[V-E]`/`[ART-MGR]`)
  rather than adding a dispatch mechanism (memory
  `pcrec-general-mechanisms-not-special-cases`).

Its price is N× code and N× compile time per pattern, paid only by the
use cases that asked for portability.

### 3.2 As a first-match table (deployment level, above the artifact)

This composes with isa_selection.md §2 (the per-SITE table inside the
artifact) and with requirements.md §2.3 (the binding FORM). It decides the
ISA of the artifact itself. Thresholds come from Linux measurements, and
none is a guessed constant.

| # | predicate | selection | why |
|---|---|---|---|
| 1 | no level gain is measured for this request on the target box (L-1/L-2 not met) | **A0 baseline**, one artifact | D77: N× size for nothing |
| 2 | the consumer is a memfn LIBRARY (B1a) | **A2**, the library's own dispatch | legal there; not pcrec's |
| 3 | the deployment box's level is known at build | **A3** at that level, `cpu_ok()` once | 0 per call, 1× size |
| 4 | unknown CPUs, AND the program links a catalog (or opts into one) | **A5 via P2**, level set per Q9 with v1 mandatory | total pick, 0 per call |
| 5 | the artifacts are loaded as `.so` or from the cache | **A5 via P3** | pick before `dlopen`; the marker becomes a second fence |
| 6 | unknown CPUs, a size dial below the middle, ELF, opt-in | **A4 (H2)** at prefilter sites only (held, Q11) | one helper per site against N× text |
| 7 | otherwise | **A0 baseline** | the safe default (isa_selection.md §2 row 6) |

### 3.3 What Linux measurement could change the verdict

`linux_run.sh` (pending, manager-run) answers U-1 and U-8..U-12. Three of
the questions below are NOT in it.

| # | measurement | in `linux_run.sh`? | what it would change |
|---|---|---|---|
| L-1 | U-8: AVX2's value over SSE2 by span (`wide_ool` against `base_ool`), and the declared form (`wide_inl`, `-v3` TU) at 6-11 B | yes | if the wide tier does not pay at the spans the bench's cells run, levels have no customer. Table row 1 holds everywhere, and A3/(d) stay designed only |
| L-2 | **today's artifacts at `-march=x86-64-v3` against the baseline**, on a bench subset: gcc's own vectorization at `-O2`, BMI2, `movbe`. No memfn kernel needed | **no**. A future exact-command brief: compile the bench's pinned artifacts twice and run the pinned cells, interleaved | if MATERIAL, A3/(d) have a customer NOW, ahead of memfn: route M needs only the consumer's flags, and the stamp is the first piece worth building. If nil, the whole axis waits for memfn's wide kernels |
| L-3 | U-9: the per-call cost of D2, ifunc and a pointer on glibc | yes | if ≈ a direct call, A4s becomes a real competitor to (d) for size-dialed unknown-CPU builds (row 6), and P4 (the emitted ifunc) becomes cheap. It cannot change U2b (in-loop), which is structural |
| L-4 | U-11 plus a new row: does a `-march=x86-64-v3` object WITHOUT `-z`/`-mneeded` carry `ISA_1_NEEDED` on ubuntubudu's toolchain, and does `ld.so` enforce it at `dlopen`? | partly: `isanote.sh` covers `-z`, a source note and `dlopen`, but not a plain `-march` object | if the toolchain marks unasked, a static (d) catalog must strip or suppress the note (H-a), or (d) becomes L2-only. If `dlopen` enforces, P3 can lean on it |
| L-5 | U-10: `cpuid` + `xgetbv` cost | yes | it confirms that once-at-startup is the only placement. It cannot change the verdict unless it is absurd |
| L-6 | the size and resident set of N variants: `.text` per variant and RSS after a v1 pick | no (needs a built A3) | it prices row 4 against row 6. Owed at build time, not now |

**The cheapest decisive item is L-2.** It needs no new code: two compiles
and the bench's own cells. It is the D77 trigger for building the stamp.

---

## 4. Questions for Frank

Numbering continues from isa_selection.md's Q4-Q6.

7. **Q7, the verdict as design of record.** Should §3.1 be the design of
   record? That is: no in-artifact dispatch by default; the declared-ISA
   artifact as the unit; selection hoisted to the caller, the L1 catalog or
   the L2 loader; library dispatch left to the library. **Recommendation:**
   yes. Build nothing until L-2 or L-1 shows a measured level gain at a
   real site (D77). The first build is A3's stamp and check (isa_selection.md
   Q4), and (d) follows with `[ART-MGR]` S2.
8. **Q8, where the variant group lives.** Should variant grouping be a
   catalog-side (or sidecar) row list emitted by the composer, rather than
   a new `rx_info` field carrying a request hash? **Recommendation:**
   catalog-side. The composer already knows the group. A hash in `rx_info`
   would duplicate R5.2's pcrec-published key. Artifacts carry only `isa`
   and `isa_family`.
9. **Q9, the level set.** Should (d)'s levels be fixed to the psABI ladder
   {v1, v3, v4} (no v2, never `-march=native`), with the v1 member
   mandatory in any catalog group? **Recommendation:** yes. N stays bounded,
   cache keys stay shareable across boxes, and the pick is total, so no
   error path exists.
10. **Q10, the marker and (d).** Should `--isa-marker` (Q6) be refused for
    artifacts destined for a static catalog, and allowed (opt-in) for L2
    `.so` variants? **Recommendation:** yes, conditional on U-11/L-4.
11. **Q11, the per-call hybrid.** Should A4 (H2) stay HELD rather than
    declined, as the size-dialed alternative to (d)? **Recommendation:**
    hold it. Decide after U-9, and only at prefilter sites, ELF, opt-in.
    Isa_selection.md Q5 governs its D2 half.

---

## 5. Cross-note text for plan.md `[ART-MGR]` (manager pastes)

> **ISA SELECTION CROSS-NOTE (lane memfneval, 2026-10-04,
> docs/design/memfn/isa_evaluation.md, [MEMFN] R1c):** the catalog (S2) and
> the loader (S3/S4) are the recommended place to pick among ISA VARIANTS of
> one request ("(d) multi-artifact selection", Frank 2026-10-04). pcrec
> emits N declared-ISA artifacts per request (isa_selection.md §1.2: route A
> `--isa=L` or route M macros; each stamped `rx_info.isa`/`isa_family`), and
> the selection runs above the artifacts. That keeps every artifact
> static-free (§5.3/TS-1) with zero per-call cost on both D91 budgets.
> - **L1:** the composer emits a VARIANT GROUP per request, an ordered row
>   list `{level, const struct rx_info *}` with the highest level first and
>   the v1 member mandatory. It also emits a pure `<catalog>_pick(group,
>   level)`, a first-match table with the level as an ARGUMENT (D46:
>   forceable and testable at every level), and a pure, baseline-compiled
>   `<catalog>_cpu_level()` (`cpuid`/`xgetbv`, freestanding on x86). The
>   CALLER holds the result, because L1 is `const` (§4.4).
> - **L2:** the loader picks from the sidecar or cache-key level BEFORE
>   `dlopen`. The cache key carries a psABI level, never `-march=native`.
> - **Hazards:** a static catalog's variants must carry NO
>   `GNU_PROPERTY_X86_ISA_1_NEEDED` marker (OR-merged, it would make the
>   whole program refuse to load on v1). Under L2 the marker is a per-`.so`
>   second fence. No non-static inline or weak definitions may appear in
>   emitted text (COMDAT across levels).
> - **Prerequisites and checks:** answer identity across variants needs a
>   level axis. K79/K80's fixes (abi 54) are the prerequisites, and both are
>   discharged.
> - **Dependencies:** S1 (`rx_entries`, to call a picked member by pointer)
>   and A3's stamp fields (an `abi` event of `[MEMFN]`'s).
> - **D77 trigger:** a measured level gain on ubuntubudu (isa_evaluation.md
>   §3.3 L-2: today's artifacts at `-march=x86-64-v3`; or L-1: the AVX2
>   knee), plus S2's own trigger. Frank questions Q7-Q11 are in §4 of that
>   note.
