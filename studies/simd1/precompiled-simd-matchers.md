# Precompiled SIMD Matchers

A learning document from building and measuring AVX2 fixed-pattern string matchers in C.
Written so that someone could build a pattern→matcher **generator tool** from it. Updated as the
project continues. Code and harness live alongside this file; all numbers are from the test rig
described in [Hardware context](#hardware-context).

**Status:** harness + 25 validated candidates covering literals, case-insensitivity, character
classes, ranges, alternation, and prefilters. Next: the generator engine.

---

## 1. The contract

A matcher is compiled for **one fixed pattern known at build time** and exposes:

```c
const char *find(const char *hay, size_t n);
```

- Returns the **leftmost position** where the pattern matches, or `NULL`.
- Semantics equal `memmem()` for plain needles, generalized for classes/alternation.
- The haystack is **not** NUL-terminated and may contain any byte values.
- The function must never read at or past `hay + n`, nor before `hay`; `n` shorter than the
  minimum match length returns `NULL` without touching memory. This is the contract SIMD code
  most wants to violate (offset loads read past the end); the harness enforces it with guard
  pages (§9).

The **leftmost-START-only** choice is load-bearing: it is what makes `X+` compile to a single
position (§6) and removes any need for backtracking.

## 2. The core algorithm

Per 32-byte block at offset `i`, load the block at `hay+i+j` for each pattern position `j`,
test each load against that position's allowed bytes to get a 32-lane mask, AND the masks:
a surviving lane is a **confirmed match start** — no verify step. `movemask` + `ctz` yields the
leftmost hit.

```c
/* pattern "wolf": lane l survives iff hay[i+l..i+l+3] == "wolf" */
m  =        cmpeq(load(hay+i+0), bcast('w'));
m &=        cmpeq(load(hay+i+1), bcast('o'));
m &=        cmpeq(load(hay+i+2), bcast('l'));
m &=        cmpeq(load(hay+i+3), bcast('f'));
mask = movemask(m);  if (mask) return hay + i + ctz(mask);
```

Two invariants every generated function needs:

- **Loop bound**: the highest byte read in an iteration is `i + (k-1) + 31`, so the vector loop
  runs while `i + 32 + (k-1) <= n` (`k` = pattern length; longest branch under alternation).
  A scalar tail finishes `i` while `i + k_min <= n`.
- **Early exit** (`k > ~4`): after ANDing each position, `if (_mm256_testz_si256(m,m)) break;`
  — `vptest` is cheap and most blocks die within two positions. Not applicable across
  alternation branches (§7 is the fix there).

## 3. The position-encoder menu

Every position is independently "some set of allowed bytes." The generator picks the cheapest
encoding per position; all encodings produce a lane mask and compose by AND/OR with everything
else. Measured throughput is for the whole matcher containing the encoder, 1 MiB haystacks.

| class shape | encoding | ~ops/block | measured |
|---|---|---|---|
| 1 byte | `cmpeq` vs broadcast | 1 | 17–33 GB/s (k=4–2) |
| 2–3 bytes (incl. case twin) | OR of `cmpeq`s | 3–5 | 15–18 GB/s |
| contiguous range `[0-9]` | saturating-subtract | 3 | 13.8 GB/s |
| arbitrary ASCII set (any size) | `pshufb` nibble lookup ("shufti") | ~7 | 15.3 GB/s |
| 4 bytes as OR-chain (for contrast) | OR of 4 `cmpeq`s | 7 | 6.0 GB/s |

**Range idiom** — works for any `[lo,hi]` at any byte value:

```c
t  = _mm256_sub_epi8(v, set1(lo));                 /* wraps below lo to huge unsigned */
in = _mm256_cmpeq_epi8(_mm256_subs_epu8(t, set1(hi-lo)), zero);  /* 0 iff t <= hi-lo */
```

**Shufti** — membership of an arbitrary set at flat cost. For each member `b` (< 0x80):
`lo_tbl[b & 15] |= 1 << (b >> 4)`; `hi_tbl[h] = 1 << h` for `h < 8`, else 0. Then per block:

```c
t = shuffle(lo_tbl, v & 0x0f) & shuffle(hi_tbl, (v >> 4) & 0x0f);  /* nonzero = member */
```

`pshufb` works per 128-bit lane, so broadcast the same 16-byte table into both lanes. Bytes
≥ 0x80 reject for free (`hi_tbl` is zero there); members must be ASCII. Beats OR-chains from
4 members up and is the only flat-cost option for scattered sets.

**Normalizing ("fold the source block") vs testing membership:** collapsing a class to one
representative then doing a single `cmpeq` only wins if the collapse is cheaper than the
membership test. In practice it never was (§4); emit the membership mask directly.

## 4. Case insensitivity

- **OR-of-twins wins.** Per alpha position, `cmpeq(v,'h') | cmpeq(v,'H')`. Measured
  15.3–17.9 GB/s. It pays 1 extra op only where a twin exists.
- **Fold-the-block loses** (~10.7 GB/s): range-check `A..Z`, OR `0x20` under the mask, then one
  `cmpeq` vs lowercase. Costs ~4 ops on **every** position, including digits/punctuation that
  did not need it. Widest gap on partial-alpha needles.
- **Blind `| 0x20` is a bug, not an optimization**: `'0' | 0x20 == 0x30`, but so is
  `0x10 | 0x20` — non-alpha needle bytes false-match control bytes. Caught in minutes by
  random-binary fuzzing (§9); fold only under an is-upper mask.
- **Baselines**: glibc `strcasestr` runs 1.2–2.7 GB/s. "tolower-copy then `memmem`" is *not*
  a faster baseline (~1.3 GB/s) — the fold pass spends the memory bandwidth the search needed.
  SIMD CI matchers beat both by 4–10×.

## 5. Needle length: where the AND-chain stops winning

Exact-literal chain vs glibc `memmem`, 1 MiB, random text:

| k | chain GB/s | memmem GB/s | verdict |
|---|---|---|---|
| 2 | 32.4 | 1.7 | 19× — memmem is weakest exactly where chains are strongest |
| 4 | 17.3 | 3.4 | 5× |
| 8 | 25.6* | 5.9–8.9 | ~3× (*early-exit active) |
| 16 | 25.6 | 8.7–15.8 | wins, narrowly |
| 32 | 21.4 | 11.3–24.0 | memmem wins on skippable content |

The chain touches every byte `k` times (bounded by early exit); `memmem`'s two-way algorithm
skips ahead sublinearly, so it scales with `k` while the chain does not.

**Periodic-prefix pathology.** Content that repeats the needle's first `k-1` bytes
(`"backfirbackfir…"`) defeats the early exit — some lane always survives deep into the chain.
Measured collapse: 0.70× memmem at k=8, 0.18× at k=16, 0.05× at k=32. This is algorithmic, not
codegen. **Generator rule:** full chain for k ≲ 8–16; beyond that, use a few selective
positions as a filter + `memcmp` verify, or fall back to `memmem`.

## 6. Alternation without backtracking

Pattern grammar that proved sufficient: top-level `|` branches; per-position classes `[abc]`;
bounded repeat `{N}` (expands to N copies of the position); `+`.

- **`X+` compiles to one position.** Under leftmost-START semantics, `X+` matches at `i` iff
  `X` does — the first byte witnesses "one or more." Exact, not an approximation. `{N}` is just
  N copies. No backtracking exists anywhere in this model.
- **Branches share loads.** All branches' chains read the same `v0..v_{maxk-1}` blocks;
  compares are per-branch, loads are not. Result = OR of branch masks; one `movemask`+`ctz`
  gives the leftmost hit of any branch.
- **Shared prefixes share masks.** `fred` ⊂ `frederick`: frederick's mask extends fred's
  already-computed mask. A generator finds this from a trie of the branches. (Position-only
  semantics even makes the subsumed longer branch prunable.)
- **Loop bound from the longest branch; scalar tail runs to `n - min_k`** — short branches can
  match where the vector loop can't reach. Forgetting this is the classic bug; the harness
  plants every branch at every boundary.

Measured: `fred|bob|janet|frederick` single-pass 4.4 GB/s, flat across content —
3.4–5.9× over the honest alternative (per-branch `memmem`, earliest result, ~1.0 GB/s).
`bob|[0-9]{5}|ted` 5.9 GB/s (no libc equivalent exists).

Cost note: alternation forfeits the §2 early exit (the OR needs every branch's verdict), which
is what the prefilter repairs.

## 7. Prefilters: derived union classes

For branches `b1..bm`, the union of all branches' members at offset `j` is a **necessary**
condition for any match — valid only for `j < min_k` (shorter branches stop constraining past
their length). Filter: `F = C_0(v0) & C_1(v1) & … & C_{N-1}(v_{N-1})`, `vptest` → skip the
block. Survivors get full evaluation (the union forgets cross-position correlation — "f" then
"o" passes though no branch has that pair — so verification is required and already exists).

**Build the filter from the branch chains' own first compares.**
`C_0 = eq(v0,'f') | eq(v0,'b') | eq(v0,'j')` — those three results are the first terms of
fred's/bob's/janet's chains. Keep them in registers and reuse on filter-pass: the filter costs
only ORs + `vptest` beyond unavoidable work; a rejection skips the remaining loads and every
chain's back half.

**Selectivity is a numbers game.** A block skips only if all 32 lanes fail:
`P(skip) = (1 - p)^32` where `p` = per-lane pass probability (product of union-class densities
over the filter offsets). You need `p ≲ 1–2%` before real skipping happens.

- Depth 1, `{f,b,j}` on text: `p ≈ 3/26` → ~2% skip rate → **slower than no filter** (3.7 vs 4.4).
- Depth 3: 7.5–9.0 GB/s — ~2× plain on every realistic content kind.
- Dense unions (`bob|[0-9]{5}|ted`: ten digits in every class) → only +20%, because the filter
  is both less selective and nearly as expensive as full evaluation.
- Worst case is bounded: on content built to pass the filter every period (§9 pf-trap), the
  depth-3 filter costs ~17% vs plain.

**Generator rules:** estimate union densities against a background byte model at build time;
choose depth — and *which* offsets, any subset of `j < min_k` is legal, so pick the rarest
unions, not necessarily the first N — to clear the ~1–2% per-lane bar; skip the filter when
unions are dense.

## 8. Codegen: don't trust the optimizer with indirection

A generic always-inline search loop parameterized by `(k, sets)` should constant-fold into the
hand-written code. With `static const char *const sets_[] = {"w","o","l","f"}` **GCC 15 never
specialized it**: the compiled loop fetched set pointers, re-broadcast needle bytes from memory
(`vpbroadcastb` in the hot loop), and tested NUL terminators at runtime — ~35 instructions
per block instead of 12, half the throughput (9.2 vs 17.3 GB/s post-fix). Constant propagation
gave up at pointer-array indirection because it needed loop unrolling first to see which
literal each iteration reads.

Fixes, in order of reliability:

1. **Emit per-position code explicitly.** The generator writes the unrolled chain as source.
   Guaranteed; this is the plan of record.
2. Flatten indirection: `typedef char bg_set[8];` — a 2D char array keeps member bytes visible
   to const-prop (string literals still initialize it), plus `#pragma GCC unroll` on the
   position/member loops. This fixed the template.
3. **Always verify with `objdump -d`.** The smell test: any `vpbroadcast*` inside the hot
   loop, or scalar loads feeding it, means specialization failed. Correct codegen has all
   broadcasts hoisted (compiler even dedupes repeated bytes into one register) and a body of
   memory-operand `vpcmpeqb` + `vpand`.

## 9. Verification methodology (what made all of this trustworthy)

The harness design earned every number above; a tool builder should replicate it.

- **Universal oracle.** Compile the pattern to `k` positions × 256-bit membership bitmaps
  (branches of them, under alternation); a naive `O(n·k)` scan is the ground truth for every
  matcher type. Cross-check the oracle itself against independent implementations where they
  exist: `memmem`/`strstr` (exact), `strcasestr` (CI), per-branch `memmem`-earliest
  (literal alternation).
- **Guard pages both ends.** Every test haystack runs twice: once ending flush against a
  `PROT_NONE` page (overreads segfault) and once starting flush after one (underreads).
  `len==0` placement sits *on* the guard page — a matcher that touches memory when `n==0`
  crashes, by design.
- **Fork isolation + alarm.** Each matcher's test run is a child process writing "what I'm
  doing" to a shared page; a crash or hang is reported with the exact failing case, and the
  harness survives.
- **Red-team the harness.** Before trusting green, plant known bugs and confirm each detector
  fires: an overread loop bound (guard page caught it at the first vulnerable length), an
  off-by-one return, a case-sensitive function registered as CI (first mixed-case plant), a
  blind `|0x20` fold (binary fuzz, ~20 hits), a dropped alternation branch (first plant).
- **Every optimization gets its own adversary.** first+last filters → `fl-trap` (first/last
  bytes co-occur at needle distance, middle never matches: 33 GB/s → 3.4). Early exit →
  periodic prefix. Union prefilters → `pf-trap` (cycle members of the derived union classes:
  passes the filter every period, no real match). If a design has a shortcut, the corpus must
  contain the content that voids the shortcut.
- **Scrub every benchmark corpus with the oracle.** Plant the only intended match at the end;
  overwrite accidental matches (first byte → a filler byte no position accepts). Alternation
  lesson: hostile content built from one branch can contain a *real* match of another branch
  (`"frederic…"` contains `fred`), silently turning a cell into an instant-return measurement
  of call overhead. Scrub all content kinds, not just random ones.
- **Deterministic PRNG** (seeded splitmix64) so failures reproduce; dump failing haystacks to
  files.

## Hardware context

All numbers: AMD Ryzen 5 1600 (Zen 1), GCC 15.2, `-O3 -mavx2`, single thread, 1 MiB
haystacks unless noted. Zen 1 splits 256-bit ops into 2×128-bit µops and has two 128-bit load
pipes — newer cores widen the SIMD-vs-libc gaps, and load-port pressure matters more here than
on current parts. Broadcasts (`vpbroadcast*`) are shuffle-domain: hoisting them out of loops
matters everywhere, and on Intel they'd contend for port 5.

## 10. Engine design implications (the tool to build)

Input: pattern (literals, classes, ranges, `|`, `{N}`, `+`, CI flag). Output: C source (or JIT)
for one matcher function. The generator:

1. Parses to branches × positions × byte-sets; expands `{N}`; collapses `+`; folds CI twins in.
2. Builds a branch trie; shares prefix masks; prunes branches subsumed under position-only
   semantics.
3. Picks per-position encoders by the §3 menu (cmpeq / OR / range / shufti).
4. Decides the prefilter: union-class densities vs a background model → depth and offset
   choice per §7, or none.
5. Chooses strategy by length per §5: full chain, filter+verify, or defer to `memmem`.
6. Emits explicit unrolled code (never a generic loop, §8), with the §2 loop bound, early
   exit where legal, and a class-aware scalar tail to `n - min_k`.
7. Is validated by the §9 harness — oracle diff, guard pages, adversarial corpus including
   the traps for whichever shortcuts it emitted.

## 11. Porting: SSE and other 128-bit targets

The design is width-agnostic; the port is a lane-count change plus an ISA tier decision.

| technique | needs | notes |
|---|---|---|
| cmpeq chains, OR classes, range idiom, CI fold, alternation, prefilters | SSE2 | baseline x86-64, no CPU check needed |
| early exit | SSE2 / SSE4.1 | `movemask()==0` works everywhere; `_mm_testz_si128` (SSE4.1) is marginally cheaper |
| shufti | SSSE3 | `_mm_shuffle_epi8`; simpler than AVX2 — one flat 16-byte table, no per-lane duplication |
| SSE4.2 string instructions | — | skip: `pcmpistri` et al. are microcoded and lose to `pshufb` approaches (Hyperscan/simdjson consensus) |

Changes that are real:

- Lane count 16: loop bound `i + 16 + (k-1) <= n`; 16-bit movemask; same `ctz`.
- **Generator: emit against a ~10-macro ISA layer** (`VLOAD/VCMPEQ8/VOR/VAND/VMOVEMASK/VTESTZ/VLANES/...`), one template per strategy, backends per ISA. The same 128-bit layer is most of a NEON port (`tbl` = shufti) and a WASM-SIMD port (`i8x16.swizzle`) — three targets for one abstraction.
- Registry `needs_avx2` → ISA-level enum + `__builtin_cpu_supports`. Harness needs zero changes: the contract is width-independent, and full-length coverage catches any ported loop-bound bug automatically.
- Prefilter skip probability becomes `(1-p)^16`: blocks are easier to reject but each rejection saves half the work — net wash, same ~1–2% per-lane rule.
- Legacy SSE encodings are destructive two-operand (compiler inserts `movdqa` copies); compiling 128-bit intrinsics with `-mavx` yields VEX three-operand forms if wanted.

**Measured (Zen 1, 8 idiom pairs, honest tiering: SSE file built `-mno-avx -mssse3`).**
The naive "Zen 1 double-pumps 256-bit ops, so SSE should tie" hypothesis is **false**:

| idiom | AVX2 | SSE | ratio |
|---|---|---|---|
| exact chain k=5 / k=4 | 14.1 / 17.4 | 12.0 / 14.4 | 0.85 |
| k=8, k=16 with early exit | 25.6 | 21.4 / 18.0 | 0.84 / 0.70 |
| range idiom | 13.9 | 11.4 | 0.82 |
| shufti | 15.4 | 10.3 | 0.67 |
| alternation + depth-3 prefilter | 9.0 | 6.3 | 0.70 |
| CI OR-of-twins | 15.4 | **6.6** | **0.43** |

Why: a 256-bit instruction on Zen 1 is ONE instruction double-pumped into two µops. At equal
µop counts, AVX2 halves front-end decode/dispatch load and amortizes loop overhead (branch,
index math, movemask) over twice the bytes. SSE additionally pays a `movdqa` per value that
must survive a destructive op — worst for CI twins, where every loaded block feeds two
compares (~2.0 instructions/byte vs ~0.9 on AVX2; the flat 6.6 GB/s is a front-end ceiling).
Disassembly confirmed constants stay hoisted — the loss is instruction count, not spills.

Consequences for the generator:

- **Prefer the widest vectors the CPU has, even on double-pumped cores.** Width buys decode
  density regardless of datapath width.
- No algorithm *flips* at 128-bit on this core — rankings held across all six content kinds —
  but margins compress toward low-instruction-count encodings: the 3-op range idiom keeps 82%
  of its AVX2 speed while shufti keeps 67% and twin-ORs 43%. Plausible (untested) that for
  small scattered sets (~4 members) an OR chain overtakes shufti at 128-bit where shufti wins
  at 256-bit; a generator with per-ISA cost tables would decide this per pattern.
- The port itself was mechanical: lane count, loop bound, 16-bit movemask, movemask-based
  early exit. Every SSE candidate passed the full guard-page/oracle suite unchanged on the
  first build — the contract and harness are width-independent, as claimed.

## 12. Established techniques: survey and three measured studies

Survey of optimizations established elsewhere (BurntSushi's memchr crate, Hyperscan, Muła/
Lemire, glibc, EPSM), ranked for a compile-time-needle generator. Adopted-and-measured items
first; the rest are catalogued with verdicts.

### Study A — rare-position filter selection (ADOPT; big win)

Established in memchr's `packedpair`: pick the filter pair by **background byte frequency**,
not position. Needle `"enzyme"` is the perfect stress case: first/last are both `'e'` (12.7%
of English) while the interior has `'z'` (0.07%) and `'y'` (2.0%). Same instruction shape,
different offsets (filter positions j map back to start `i` by subtracting j). 1 MiB:

| content | full chain | first+last (`e`,`e`) | rare pair (`z`,`y`) |
|---|---|---|---|
| english (frequency-weighted) | 11.8 | 5.2 | **31.6** |
| all-'e' fill | 11.8 | **0.96** | 31.8 |
| uniform a–z | 11.7 | 20.4 | 20.3 |

6× over first+last on English, 33× on 'e'-heavy content; the uniform-text tie proves the
effect is purely corpus statistics — which is why the harness needed a frequency-weighted
`english` content kind to see it at all (uniform corpora hide this entire optimization).
Rare2's own adversary exists (content where the two rare bytes co-occur at needle distance —
its fl-trap analogue: 3.5 GB/s on periodic prefix) and is bounded like every filter.
**Generator rule:** ship a default English/binary frequency table, let the user supply their
own (their "unlikely strings" hint = force those bytes' rank to zero); choose the 2–3
positions minimizing the product of background densities; fall back to full chain when all
bytes are common. memchr's runtime fallback (disable a filter that observably misfires) is
the dynamic complement.

### Study B — blockwise shift-and (REJECT as primary; niche fallback)

Bitap done blockwise: load a 64-byte window once, compare it against every distinct needle
byte, combine the movemask bitmaps in scalar registers (`AND_j (m_j >> j)`), step by
`64-(k-1)`. Predicted win: 2 loads instead of k per window. Measured: **8.0 GB/s flat (k=8)
and 4.0 flat (k=16)** vs the AND-chain's 18.6–25.7. The chain was never load-bound — L1 hits
on dual load pipes are cheap — while shift-and pays 2k `vpmovmskb`s per window (~4–5 cycle
latency each on Zen 1, single port) plus the scalar merge: the vector→scalar crossing costs
more than the loads it saves. Its one virtue is total content-independence: on the periodic-
prefix pathology it holds its flat rate and beats the collapsed chain (8.0 vs 6.2 at k=8,
4.0 vs 2.8 at k=16). **Verdict:** never the default; at most a bounded-worst-case fallback —
and the better long-needle answer is Study A's rare-pair filter (31 GB/s on English) anyway.

### Study C — Teddy-style bucketed prefilter (ADOPT for wide alternations)

Hyperscan's multi-literal filter: per leading offset, two `pshufb` nibble tables map each
byte to a bitset of candidate **branches** ("buckets"); AND across offsets; a surviving
lane's byte says *which branches* to verify. Versus our union-class filter, which forgets
branch identity and must run full 8-branch evaluation on every filter pass. Eight branches
(`fred|bob|janet|frederick|alice|megan|carol|dave`), 1 MiB:

| content | union filter (depth 3) | Teddy (depth 2) |
|---|---|---|
| text / english | 2.2 / 1.7 | 3.0 / 2.4 |
| first-byte / bytes | 6.0 / 6.0 | 9.0 / 8.8 |
| periodic prefix | 1.6 | **9.0** |
| pf-trap | 1.6 | 1.3 |

Teddy wins 35–50% broadly and 5.7× on periodic content — with one less filter level —
because bucket bits turn "filter passed, evaluate everything" into "verify exactly these
branches." Both sit far above 8 sequential `memmem` calls (~0.5 GB/s effective).
**Generator rule:** branch count ≲4 → union filter + shared-load evaluation; more → Teddy
buckets (≤8 per lane byte; Fat Teddy doubles that). pf-trap-shaped content still costs both
~2× — bounded, same as every filter.

### Study D — software prefetch (ADOPT above L3 only; size-gated)

One `_mm_prefetch(hay+i+DIST, _MM_HINT_T0)` per 32-byte block on the rare-pair matcher,
distances 512/1024/4096. (Prefetch is the one legal "read" past `hay+n`: architecturally a
no-op on unmapped addresses, never faults — guard pages confirm.) 1 MiB is L3-resident,
32 MiB is DRAM-resident on this 16 MB-L3 part:

| size | no prefetch | +512 | +1024 | +4096 |
|---|---|---|---|---|
| 1 MiB (english) | **31.7** | 29.0 | 28.7 | 28.7 |
| 8 MiB | 20.3 | 22.2 | 22.2 | 22.3 |
| 32 MiB | 15.7 | 17.7 | **17.7–18.1** | 17.1–17.6 |

Below L3 the hardware stream prefetcher plus out-of-order overlap already cover the stream,
and the extra µop costs ~9%. At and beyond the L3 edge it recovers 9–15%. Distance is
insensitive across 512–4096; use ~1024. **Generator rule:** emit prefetch only in the
large-haystack tier (see §13); never unconditionally.

### Study E — cold file mappings (page-cache warming is a scheduling problem, not codegen)

Setup: 1 GiB file, mmap'd, pages evicted via `posix_fadvise(DONTNEED)` and *verified* evicted
with `mincore()` before each run (0% resident); SATA SSD (~540 MB/s). Median of 3 interleaved
rounds (`coldmap.c`, `make coldmap`):

| strategy | MB/s |
|---|---|
| cold, plain scan | 539.7 |
| cold, + `prefetcht0` (+1024) | 540.1 |
| cold, `madvise(MADV_SEQUENTIAL)` | 540.0 |
| cold, `madvise(MADV_WILLNEED)` at scan time | 539.9 |
| cold, `MAP_POPULATE` (populate inside the clock) | 520.5 |
| warm (page-cache resident) | **15,293** |

Three findings:

1. **CPU prefetch is provably inert on cold pages** — identical to plain within noise.
   `prefetcht0` never faults a page in; hardware drops it for not-present pages. "Warming the
   next block" at the cache-line level and at the page-cache level are different machines.
2. **At scan time, no userspace readahead hint helped either**: the kernel's demand-paging
   readahead already saturates this device, so `MADV_SEQUENTIAL`/`WILLNEED` had nothing to
   add. `MAP_POPULATE` was slightly *worse* — it serializes (read everything, then scan)
   where demand paging overlaps scan with readahead. On faster NVMe the madvise hints may
   matter more (unverified here).
3. **The cold/warm gap is 28×.** If cold-file scanning matters to a workload, the win is not
   in the matcher's code: it is issuing `MADV_WILLNEED` (or a reader thread) *ahead of when
   the scan is needed*, or pipelining scan-file-N with readahead-of-file-N+1. Warming is
   scheduling, not codegen — the generator's only job here is to not bother emitting scan-time
   hints.

### Catalogued, not yet measured

- **Overlapped final block** (StringZilla et al.): replace the scalar tail with one full
  vector ending exactly at `n`, dedup against prior blocks — removes a whole code path. Cheap;
  next in line. At small haystack sizes this stops being cleanup and becomes the main event
  (see §13).
- **64/128-byte unrolling** (memchr, Muła): fewer branches per byte, hides compare latency —
  should compound with our front-end-density findings (§11). Watch register pressure on long
  chains.
- **memchr-jump hybrid**: when the single rarest byte is very sparse, `memchr`-skip to it and
  verify — same frequency data as Study A, different combinator; wins at very low densities.
- **Length-tiered dispatch** (EPSM's meta-lesson): established implementations all converge
  on choosing the algorithm by needle length at build time — validates §10's structure.
- **FDR** (Hyperscan): shift-or over bucket tables for *large* literal sets (tens+); the tier
  above Teddy; not needed at our branch counts.
- **Two-Way / bad-char skip fallback** (glibc): worst-case-linear insurance for degenerate
  needles; with compile-time needles we can detect those statically and emit it only then.
- **PCMPESTRI/PCMPESTRM/MPSADBW**: rejected industry-wide for tight loops (microcoded, high
  latency) — documented so nobody "improves" toward them later.
- **AVX-512**: 64-byte blocks + compare-into-mask (`vpcmpb` → k-registers, no movemask) +
  `vpcompressb` — would specifically fix Study B's movemask cost; future backend.

Primary sources: memchr crate design (BurntSushi), aho-corasick Teddy README, Hyperscan
NSDI'19 paper, Muła's SIMD substring-search notes, glibc str-two-way, Faro & Külekci EPSM.

## 13. Haystack-size tiering (a second dispatch axis)

The needle decides the algorithm (§5, §10); the *expected haystack size*, if the user can
hint it, decides the surrounding machinery. §10's dispatch is really a 2-D matrix:
needle length × haystack size.

- **Tiny (≲ 64 B):** below `n ≈ 32+k` the vector loop never runs — the "matcher" is its
  scalar tail. Emit a loop-free form instead: one or two overlapping vector blocks, or
  scalar/SWAR.
- **Small (≲ 4 KiB):** fixed overhead rivals scan time (a 256 B scan is ~8 ns; hoisting a
  long chain's broadcasts costs a comparable amount). Prefer few-constant strategies
  (rare-pair filter over full chain) even where the chain wins at 1 MiB; skip shufti/Teddy
  table setup unless branch count forces it; no unrolling; no prefetch; replace the scalar
  tail with an overlapped final block — at n=256 the tail is 15–25% of the work.
- **Medium (L1–L3):** everything measured in §3–§7 applies as-is. No prefetch (Study D:
  it costs ~9% here).
- **Huge (> L3):** memory bandwidth is the ceiling (~20–25 GB/s single-core here). Emit
  prefetch (+1024, Study D: +9–15%), consider unrolling, huge pages for TLB. Roofline
  corollary: compute hidden under memory time is free, so this tier can afford the more
  robust content-independent strategy (full chain, deeper filter) at zero throughput cost —
  worst-case immunity for nothing.
- **Exactly-known n** (fixed-width records): `n` becomes a compile-time constant — emit the
  exact iteration count with no loop counter, no bound checks, no tail. Strictly better than
  the general form.

Measurement honesty note: benchmarking the small tier by hammering one 256 B buffer trains
the branch predictor and keeps L1 hot in ways real many-small-buffer workloads don't; the
harness needs a cycle-through-distinct-buffers mode before small-tier numbers are trusted.

## 14. Find-all mode (pre-searcher for a regex engine)

Contract (`findall.h`): report **every** occurrence start, exact and ascending, overlaps
included; offsets into a caller buffer, return the total count (count-past-cap signals
truncation). This is the mode where the matcher serves as a *pre-searcher* — the anchor
source for a regex engine's match attempts — so the output must be exact, not probabilistic.
Study driver: `make findall` (own guard-page correctness suite vs a naive looped oracle,
~3,100 cases/candidate; `fa_abab_chain` proves the lane-parallel design reports overlapping
starts — `"ababab"` → 0, 2 — for free).

Measured compile choices (needle "enzyme", English-minus-z corpus, planted densities):

**Emission strategy, by hit density** (1 MiB; 8 MiB within ~10%):

| hit density | fused ctz bit-walk | two-pass mask-store | rare-pair filter+verify |
|---|---|---|---|
| 0.01% | 11.6 | 9.2 | **30.8** |
| 0.1% | 10.5 | 8.5 | **22.8** |
| 1% | 4.8 | 5.2 | 6.9 |
| 10% | 2.8 | 3.0 | 3.2 |

At ≥1% density everything converges to an **emission floor of ~3.2–3.8 ns per hit** — the
scan strategy stops mattering and per-hit bookkeeping is the ceiling. Bit-walk wins below
~1%; the branchless mask-store two-pass edges ahead above it. (Mask-store's deeper virtue is
architectural: handing `(base, mask)` streams to the consumer skips offset materialization
entirely.)

**Internal strategy, by filter fire rate** — the find-all ranking flip. The table above
flatters the filter: that corpus has no stray 'z', so the filter only fires on true matches.
Adding decoy `"qzyq"` fragments (light the filter, never verify) at fixed 0.01% true density:

| decoy density | chain (ctz) | chain (mask2p) | rare-pair filter |
|---|---|---|---|
| 0.1% | 11.6 | 9.2 | **21.7** |
| 1% | **11.6** | 9.1 | 6.9 |
| 10% | **11.7** | 9.2 | 2.8 |

In find-first a false candidate costs one wasted verify before the exit; in find-all every
candidate bit pays. **Generator rule:** estimate the filter's fire rate (true density + false-
candidate rate, both computable from the §12-A frequency model at build time); below ~0.5–1%
emit filter+verify, above it emit the always-exact chain, whose mask needs no rebuilding.

**Factor pairing (`A.*B`, `A.{0,64}B`)** — per-branch masks kept separate (not OR'd) pair in
mask/stream space; gap constraints are shifts/window checks, O(hits), no rescanning. Fused
single-pass (shared loads, inline two-cursor pairing, O(1) carry) vs two-pass (two find-alls
+ stream merge): **0.95–1.02× — a tie** at 0.1% factor density. Prefer the simpler two-pass
merge until profiling says otherwise; fused's shared loads save little because scans are
cheap and hit lists are small. `X+` under start-only semantics still needs no loop, and the
regex engine receives anchors where both literal factors are already confirmed at compatible
distances.

## 15. Run extension (embedded `[class]+` atoms) and vector-width choice

The email-pattern shape `[a-zA-Z.]+@...` compiles to: find-all the rare anchor (`@`), then
measure the class run adjacent to each anchor — branchless: load a block ending at the
anchor, classify (shufti), movemask, and the run length is one `clz` of the inverted mask.
`runext.c` (self-contained; `cc -O3 -mavx2 -o runext runext.c` on any x86-64 Linux box — built
for cross-architecture comparison, Intel numbers still to be collected) measures scalar
table-loop vs 16-byte (VEX-encoded AVX-128) vs 32-byte extension, ns per anchor, Zen 1:

| run length dist | scalar map | xmm16 shufti | ymm32 shufti |
|---|---|---|---|
| L=5 fixed | 4.9 | **4.5** | 6.8 |
| L=15 fixed | 10.9 | **4.4** | 6.7 |
| L=50 fixed | 38.0 | 22.1 | **8.8** |
| U(3,20) mixed | 22.8 | 9.8 | **6.7** |
| U(3,60) mixed | 32.3 | 23.7 | **15.2** |

(xmm16 with range-compares instead of shufti is within ~5% of shufti at this class shape.)

Findings:

- **Scalar's fixed-L rows are a lie the benchmark tells on purpose**: with constant run
  length the exit branch predicts perfectly. The mixed rows are reality — the unpredictable
  run-end costs the scalar loop ~50 cycles of mispredict per anchor, which is why it loses
  2–3× even at mean length ~11.
- **The 128-bit hypothesis ("shorter loads for shorter strings") is confirmed on Zen 1 with a
  boundary**: xmm wins whenever the run fits its window (L ≤ 16: 4.4 ns vs ymm's 6.7 — half
  the µops on a double-pumped core). But U(3,20) flips to ymm despite a mean of ~11, because
  runs that straddle 16 make xmm's "need another block?" branch unpredictable, while ymm
  covers the whole distribution in one block and that branch never mispredicts.
- **Width rule for the generator: pick the vector width whose window covers ~p99 of the run
  distribution** (exemplar statistic, §12/§14) — width buys branch *predictability* first,
  bytes second. True 5–15 email runs (p99 ≤ 16) → xmm on Zen-class cores; anything
  straddling → ymm. On Intel (single-µop 256-bit) ymm should never lose — the open column.
- Per-anchor cost lands at 4–7 ns for email-like runs; at ~0.1% anchor density this is noise
  next to the anchor scan. The `+` atom is effectively free once anchored.

**Encoding-mixing note** (so nobody trips on SSE/AVX "mixing"): penalties are about legacy
vs VEX *encodings*, not width. One TU compiled `-mavx2` emits VEX for everything including
128-bit ops (which zero ymm uppers) — no mixing exists. Legacy-encoded objects (our
`-mno-avx` cand_sse.o) are safe across function calls because the compiler `vzeroupper`s on
AVX-side exits. The only real hazard is hand-written legacy-SSE assembly inside an
AVX-dirty loop on Intel (Haswell: state-transition stalls; Skylake+: false dependencies);
AMD Zen has no such penalty at all.

## 16. Exemplar statistics: profile-guided generation

Because matchers are precompiled, a one-time offline pass over an exemplar corpus turns
every dispatch decision in this document from a guess into a computation. The pass is cheap:
the naive oracle plus histograms (the harness's generators already contain the machinery),
run once at build time. Every statistic below maps to a measured knob.

| statistic | how gathered | what it decides (where measured) |
|---|---|---|
| byte-frequency histogram (256 bins) | one counting pass | filter/anchor position choice — pick the 2–3 needle positions minimizing the product of background densities (§12-A: 6–33× swing); user-declared "rare strings" are injected as rank-0 bytes |
| per-atom fire rate: each literal factor's and class's real hit rate | naive scan of the exemplar per atom | find-first vs find-all internal strategy — filter+verify below ~0.5–1% fire rate, always-exact chain above (§14 decoy flip); prefilter depth via `(1-p)^lanes` ≥ skip target (§7) |
| overall match density | naive full match count | emission strategy — ctz bit-walk below ~1% density, mask-store two-pass above; output buffer `cap` sizing (§14) |
| run-length distribution per `+`/`*` atom (p50/p95/p99/max) | measure runs at real anchor hits | vector width for run extension — window covers p99 (§15); single-block vs multi-block vs whole-buffer mask RLE |
| gap distribution between paired factors | measure at real factor pairs | bounded-window encoding, FIFO bounds, fused vs merge re-check if dense (§14: tie at 0.1%) |
| newline/record-separator density | one counting pass | whether `.*` compiles as `[^\n]*` stream algebra (§14) vs unbounded pairing |
| haystack size distribution | from the workload, not the file | §13 tier: loop-free / no-unroll / as-measured / prefetch+robustness-free; exact-`n` fully-unrolled form for fixed records |
| storage temperature (page-cache residency expectations) | workload knowledge | nothing in codegen — scheduling only: `MADV_WILLNEED` ahead of need, pipeline files (§12-E) |
| branch count of alternations | from the pattern itself | union filter ≲4 branches, Teddy beyond (§12-C) |

Usage notes:

- **Fire rate, not just true density.** The §14 flip is driven by how often the *filter*
  lights, which is true matches plus false candidates. Both are computable: false-candidate
  rate for a position pair = product of those bytes' background frequencies at their offsets
  (validated against the measured decoy sweep before trusting the model).
- **User hints compose with measurement.** A declared unlikely string ("this log never
  contains `\x00\xff`") overrides the histogram where the exemplar may under-represent
  reality; the frequency table is an input, not an oracle.
- **Guard against unrepresentative exemplars.** The generated matcher is only optimal for
  corpora that resemble the exemplar; a rare-pair filter tuned on English collapses on a
  corpus where those bytes are common (§12-A shows a 6× swing both directions). Two
  defenses: emit the memchr-crate-style runtime demotion (count filter fires; if the rate
  blows past the model, fall back to the chain), and keep the pathological-content bench
  kinds (fl-trap, prefix, pf-trap) as acceptance gates so worst-case behavior is bounded
  regardless of what the exemplar promised.
- **Stats collection is itself find-all.** Fire rates and run lengths come from running the
  find-all oracle over the exemplar — the same machinery §14 built, so the profiler and the
  matcher share code.

## Changelog

- **2026-08-16** — §16: exemplar-statistics section — what a profile-guided generator
  gathers from a sample corpus, how, and which measured knob each statistic drives; model
  validation, user hints, unrepresentative-exemplar defenses.
- **2026-08-16** — §15 run-extension study (`runext.c`, self-contained for cross-arch runs):
  branchless SIMD extension beats scalar map-loop 2–3× on honest mixed-length runs (~50-cycle
  run-end mispredict); 128-bit wins when runs fit 16 bytes (half the µops on Zen 1), 256-bit
  wins once the distribution straddles the window — width rule: cover p99 of run length.
  Encoding-mixing (SSE/AVX) rules documented. Intel column open.
- **2026-08-16** — §14 find-all / pre-searcher mode measured: emission floor ~3.3 ns/hit at
  high density; bit-walk vs mask-store crossover ~1%; filter-vs-chain ranking flips at
  ~0.5–1% filter fire rate (decoy sweep); fused vs two-pass factor pairing is a tie — prefer
  the simpler merge; overlap handling free by construction. New `findall` driver + 7
  candidates.
- **2026-08-16** — §12 Study E: cold mmap'd file scan (1 GiB, mincore-verified eviction, SATA
  SSD). prefetcht0 provably inert on cold pages; scan-time madvise hints no help (kernel
  readahead already saturates the device); MAP_POPULATE slightly worse; cold/warm gap 28×.
  Page-cache warming = scheduling (WILLNEED ahead of need / pipeline), not codegen. New
  `coldmap` driver, `make coldmap`.
- **2026-08-16** — §12 Study D + §13: software prefetch measured (hurts ~9% below L3, gains
  9–15% at/above it; distance-insensitive 512–4096; adopt size-gated at ~+1024). New 32 MiB
  DRAM bench tier. §13 haystack-size tiering: tiny/small/medium/huge/exact-n dispatch axis.
  43 matchers passing.
- **2026-08-16** — §12: established-techniques survey + three measured studies. Rare-position
  filter selection adopted (6–33× over first+last on realistic corpora; new frequency-weighted
  `english` harness kind). Blockwise shift-and rejected (movemask-bound: 8.0/4.0 GB/s flat;
  niche worst-case floor only). Teddy adopted for wide alternations (beats union filter
  35–50%, 5.7× on periodic content, at 8 branches). 40 matchers passing.
- **2026-08-15** — §11 measured: 8 SSE/AVX2 idiom pairs on Zen 1. Parity hypothesis falsified —
  AVX2 wins 1.2–2.3× via front-end instruction density (double-pumped 256-bit = half the
  instructions), worst for constant-heavy CI twins. No algorithm ranking flips; margins favor
  low-op encodings at 128-bit. 33 matchers passing.
- **2026-08-15** — §11: SSE porting analysis (tier table, ISA macro layer, NEON/WASM reach,
  Zen 1 parity hypothesis).
- **2026-08-15** — Initial document: harness methodology; encoder menu (cmpeq/OR/range/
  shufti); CI verdict (OR-twins > fold; blind-fold bug); length crossover + prefix pathology;
  alternation composition (`+` collapse, shared loads, trie sharing, min_k tail);
  union-class prefilters with selectivity math and pf-trap; GCC specialization failure and
  fixes. 25 matchers passing, ~9–11k oracle cases each.
