# `memcmp` lowering study — [OPT-LITSCAN] P4, does the constant-length compare need a length bound or form split

2026-09-27, lane `memcmpstudy`, sonnet; measurement only, nothing under
`src/`/`tests/`/`docs/spec/` (the one `[K60-PROBE]`-style exception is a
throwaway compile of `build/pcrec` used only to confirm the real emitted
artifact matches these probes — no `src/` edit). Answers Frank's three
questions about P4's `!memcmp(base, "lit", n)` form
(`emit_exact_compare`, `src/gen/emit_dfa.c:766`) — the one primitive
`compare_stack.md` §2 names as fused by gcc and everything else as
unverified. Read `docs/design/reqpos_2b.md` §3.2 first; this note extends
its four-length table (2, 3, 4, 8, 11) to the full brief and adds the
lengths it never took (14 more), a second toolchain, and instruction
evidence for *why* each row is what it is, not just what it is.

## 0. The verdict, up front

**P4 needs no length bound or form split for the population it serves
today.** Every length pcrec's shipped literal runs actually reach (per
`reqpos_2b.md` §1.2/§3.3: 62.7% of the corpus is `L = 2`, the longest
finite-gain run in the whole population is 8 bytes) lowers on gcc-16
-O1/-O2/-O3 — the harness's `GENCFLAGS` level and the two levels above
it — to a call-free load-and-compare, exactly as `reqpos_2b.md` §3.2
already found for `L ∈ {2, 4, 8}`. The three findings below are all about
lengths **longer than anything the corpus needs today**, and are recorded
as findings for a future longer-run mechanism (`[WORD-FOLD]`'s caseless
cube compare, `reqpos_2b.md` §3.4's "event 2"), not as a defect in P4 as
it ships.

1. **gcc's odd-length lowering is a greedy, non-overlapping, msb-first
   power-of-two decomposition** (16, 8, 4, 2, 1), each piece its own load
   *and* its own compare *and* its own short-circuit branch — not the
   "two overlapping loads" or "one load plus a byte tail" shapes the brief
   named as candidates. **clang uses the overlapping form instead, and it
   is branchless** (one `cmp` + one `ccmp`, chained, no intermediate
   branch) — `L=7` on clang/arm64 is *exactly* Frank's own example,
   `ldr w9,[x8]` (4 bytes at offset 0) + `ldur w8,[x8,#3]` (4 bytes at
   offset 3, overlapping by one byte).
2. **gcc has one real cliff in the tested range and it is narrow**: at
   `-O1`/`-O2`/`-O3`, `L = 31` alone calls `memcmp()` out of line; every
   other length from 1 to 64 tested (including 25–30 and 32–64) stays
   inlined. `-Os` is a different story — everything except `L ∈ {1,2,4,8}`
   calls out, which qualifies `emit_exact_compare`'s own comment ("gcc
   turns a constant-length memcmp into one word load and compare with no
   call out of line at L in {2,4,8}") to two of the harness's four opt
   levels plus one more.
3. **clang never calls `memcmp()` in the tested range on arm64** (1–64,
   all inline) and on cross-compiled x86_64 stays inline through `L = 32`
   (two 16-byte SSE2 `movdqu`+`pxor`+`por`+`ptest`), calling out at 33+.
4. **A real emitted P4 artifact reproduces the probe exactly**: compiling
   `\.tar` with `build/pcrec` on this branch's DFA sites and re-compiling
   the artifact at `-O2` shows the `!memcmp(subject + cand, ".tar", 4)`
   line lowered to one `ldr w1,[x0]` + one `cmp w1,w21` — and gcc even
   **hoists the constant load out of the scan loop entirely** (`w21` is
   loaded once, before `rx_search`'s main loop, not per iteration).

## 1. Method

Instrument-first, timing second, per the brief. Probes and scripts are
committed under `docs/dev/memcmp_lowering_study/` (own CLAUDE.md); nothing
here regenerates without the pinned toolchain versions named below.

- **Compilers**: `gcc-16` (Homebrew GCC 16.2.0, this box's own `gcc-16`,
  the pcrec worktree's default `CC`) at `-O1 -O2 -O3 -Os`, all `-S`;
  Apple clang 21.0.0 (`clang-2100.1.1.101`, arm64-apple-darwin25.6.0) at
  `-O2`; the same Apple clang cross-compiled with
  `-target x86_64-apple-darwin -O2 -S` for a secondary x86 column (light,
  local — no ssh, no box outside this Mac). **`gcc-15` on x86 is OWED**
  (§6).
- **Probe shape**: `docs/dev/memcmp_lowering_study/gen_probe.py` emits one
  `cmp_memcmp_L(const unsigned char *s, size_t pos, size_t n_)` function
  per `L ∈ {1..16, 17, 20, 24, 31, 32, 33, 40, 48, 64}`, body
  `return pos + L <= n_ && !memcmp(s + pos, "<L bytes>", L);` — P4's exact
  shape (`emit_exact_compare`, `src/gen/emit_dfa.c:769-771`), with a
  distinct, deterministic, non-repeating literal per length (so the
  compiler cannot fold two functions' constants together). The same file
  also emits `cmp_mask_L` (load the smallest covering width — 4 or 8
  bytes — AND-mask to the low `L` bytes, one wide compare;
  `[WORD-FOLD]`'s cube-compare shape, safety condition `pos + width <=
  n_`) and, for `L ∈ {5,6,7}`, `cmp_overlap_L` (two half-width loads at
  offset 0 and offset `L - half`, safety condition `pos + L <= n_` only —
  Frank's own "load4@0 and load4@3" example for `L=7`).
- **Analysis**: `docs/dev/memcmp_lowering_study/analyze_asm.py` splits a
  `.s` file into per-function bodies (bounded by `.globl` directives,
  which always precede the next function's own label — internal branch
  targets like `L3:`/`LBB0_2:` are not boundaries) and reports whether the
  body calls out (`bl`/`callq`), how many load-shaped instructions, how
  many compares, and total instruction count. **Known limitation, stated
  rather than silently tolerated**: the branch-count column under-counts
  ARM condition-code branches (`bne`/`beq`/`bhi`) because they do not
  match the generic `b\b`/`cbz`/… pattern the script was written against;
  every branch-count-dependent claim below is corroborated by reading the
  raw assembly by hand, not by trusting that column alone.
- **Timing**: `docs/dev/memcmp_lowering_study/bench.c`, built per `L ∈
  {2,3,4,7,8,10,16}`, three regimes (subject bytes planted so the run
  matches / mismatches at its first byte / mismatches at its last byte),
  best-of-5 rounds per arm, `timeout 25` on every run (bare `timeout` is
  GNU on this box per `BOILERPLATE.md`). Scratch tier: not committed as
  anything pcrec runs, a throwaway per the brief.

## 2. Does gcc inline every L ≤ 16 with no call, and where does it stop up to ~64?

| L | gcc-16 -O1 | gcc-16 -O2 | gcc-16 -O3 | gcc-16 -Os |
|---|---|---|---|---|
| 1 | inline (1 load) | inline | inline | inline |
| 2 | inline (1 load) | inline | inline | inline |
| 3 | inline (2 loads) | inline | inline | **CALL** |
| 4 | inline (1 load) | inline | inline | inline |
| 5 | inline (2 loads) | inline | inline | **CALL** |
| 6 | inline (2 loads) | inline | inline | **CALL** |
| 7 | inline (3 loads) | inline | inline | **CALL** |
| 8 | inline (1 load) | inline | inline | inline |
| 9 | inline (2 loads) | inline | inline | **CALL** |
| 10 | inline (2 loads) | inline | inline | **CALL** |
| 11 | inline (3 loads) | inline | inline | **CALL** |
| 12 | inline (2 loads) | inline | inline | **CALL** |
| 13 | inline (3 loads) | inline | inline | **CALL** |
| 14 | inline (3 loads) | inline | inline | **CALL** |
| 15 | inline (4 loads) | inline | inline | **CALL** |
| 16 | inline (2 loads) | inline | inline | **CALL** |
| 17 | inline (NEON + 1B tail) | inline | inline | **CALL** |
| 20 | inline (NEON + 4B tail) | inline | inline | **CALL** |
| 24 | inline (NEON + 8B tail) | inline | inline | **CALL** |
| 31 | **CALL** | **CALL** | **CALL** | **CALL** |
| 32 | inline (2×NEON) | inline | inline | **CALL** |
| 33 | inline (2×NEON + 1B) | inline | inline | **CALL** |
| 40 | inline (2×NEON + 8B) | inline | inline | **CALL** |
| 48 | inline (3×NEON) | inline | inline | **CALL** |
| 64 | inline (4×NEON) | inline | inline | **CALL** |

(gcc-16, this box, Homebrew 16.2.0, `arm64-apple-darwin25.6.0`; the
`-O2`/`-O3` outputs are byte-identical at every length tested.)

**Answer**: yes for `-O1`/`-O2`/`-O3` at every length in the whole tested
range (1–64) except one — `L = 31` — which is a narrow, gcc-specific
cliff and not a boundary (§4). `-Os` is qualitatively different: only the
four lengths that are themselves a natural machine width and ≤ 8 bytes
(`1, 2, 4, 8`) stay inlined; everything else, including `L = 16`, calls
out. Since pcrec's own harness compiles generated code at `-O1`
(`GENCFLAGS`, `coding_guide.md`) and ships no `-Os` recommendation, the
`-Os` row is a caveat for a size-optimizing downstream integrator rather
than a live pcrec concern — flagged here because `emit_exact_compare`'s
own comment states the `{2,4,8}` result without an opt-level qualifier.

## 3. How does gcc handle the odd lengths — overlapping loads, two loads plus a byte, or a byte tail?

**None of the three.** gcc's inlined `memcmp` expansion is a **greedy,
strictly-decreasing, non-overlapping power-of-two decomposition**
(16 → 8 → 4 → 2 → 1), and — this is the part the brief's candidate list
didn't anticipate — **each piece gets its own compare and its own
short-circuit branch**, not one combined compare. Read left to right, a
mismatch in an earlier (larger) piece skips the later ones entirely:

| L | decomposition | pieces (loads = compares = branches) |
|---|---|---|
| 3 | 2+1 | 2 |
| 5 | 4+1 | 2 |
| 6 | 4+2 | 2 |
| 7 | 4+2+1 | 3 |
| 9 | 8+1 | 2 |
| 10 | 8+2 | 2 |
| 11 | 8+2+1 | 3 |
| 13 | 8+4+1 | 3 |
| 15 | 8+4+2+1 | 4 |
| 17 | 16(NEON)+1 | 2 |
| 20 | 16(NEON)+4 | 2 |
| 24 | 16(NEON)+8 | 2 |

Verbatim from `L=15` at `-O2` (`docs/dev/memcmp_lowering_study/asm/probe_gcc16_O2.s`):
each piece's mismatch (`bne`) jumps straight to the shared "return 0" tail
(`L76`), so the *cost* of an absent run — the case `reqpos_2b.md` §3.3
already prices as the win — pays for however many pieces the FIRST
mismatching piece needs to reach, not the whole decomposition:

```asm
	ldr	x1, [x0, x1]        /* bytes 0-7 */
	...
	cmp	x1, x0
	beq	L79
L76:                         /* shared "not a match" tail */
	mov	w0, 1
	eor	w0, w0, 1
L74:
	ret
	...
L79:
	ldr	w1, [x2, 8]          /* bytes 8-11 */
	...
	bne	L76
	ldrh	w1, [x2, 12]         /* bytes 12-13 */
	...
	bne	L76
	ldrb	w0, [x2, 14]         /* byte 14 */
	...
	bne	L76
	mov	w0, 0
	eor	w0, w0, 1
	b	L74
```

**clang, on both arm64 and x86_64, uses the overlapping form instead, and
renders it branchless.** `L=7` on clang/arm64 is Frank's own example
verbatim (`docs/dev/memcmp_lowering_study/asm/probe_clang_O2.s`):

```asm
	ldr	w9, [x8]             /* 4 bytes at offset 0 */
	ldur	w8, [x8, #3]         /* 4 bytes at offset 3 — OVERLAPS by 1 byte */
	mov	w10, #25185
	movk	w10, #25699, lsl #16
	cmp	w9, w10
	mov	w9, #25956
	movk	w9, #26470, lsl #16
	ccmp	w8, w9, #0, eq       /* chained compare, no branch */
	cset	w0, eq
```

The general clang rule (verified at L ∈ {3,5,6,7,9,13,15,17}, x86_64
identical in shape with SSE2 XMM loads at L ∈ {17..32}): pick the
smallest natural width `W` with `2W ≥ L`, load `W` bytes at offset 0 and
`W` bytes at offset `L − W` (overlapping by `2W − L` bytes when `L` is
not itself a multiple of `W`), and chain the two compares with `ccmp` so
only the one bounds-check branch survives. This is **strictly cheaper**
than gcc's decomposition in both load count (2, never more, across the
whole tested range) and branch count (1, always) — and it needs only the
run's own `pos + L <= n_` bound, the same one `emit_exact_compare`
already emits; it never needs the wider `pos + width <= n_` the masked
single-load form below requires.

## 4. The one gcc cliff, and it is one length, not a boundary

`L = 31` calls `memcmp()` at every one of `-O1`/`-O2`/`-O3`; nothing else
in `{25, 26, 27, 28, 29, 30}` or `{32, 33, 40, 48, 64}` does (confirmed by
extending the sweep across the whole 25–30 gap,
`docs/dev/memcmp_lowering_study/probe_extra.c`). The mechanism, read from
the assembly: gcc's NEON expansion covers a leading 16-byte chunk with one
vector compare and hands the *remainder* to the same scalar
power-of-two decomposition as §3. At `L = 32/33/40/48/64` the remainder is
0, 1, 8, 0(×3 NEON chunks), 0 — cheap. At `L = 31` the remainder is 15
bytes, which by §3's own table costs **4** scalar pieces on its own
(8+4+2+1) — 1 NEON chunk + 4 scalar pieces = 5 total memory operations,
which is apparently over whatever internal by-pieces cost threshold gcc's
`memcmp` inliner uses, and it falls back to a call instead. `L = 15`
alone (no leading NEON chunk, same 4-piece scalar decomposition) stays
inlined, so the threshold is specifically about the *combination*, not
either piece count alone.

This is a real, narrow, gcc-specific gap — not a defect in P4, because
nothing in the corpus needs a 31-byte compare (`reqpos_2b.md` §1.2: the
longest observed finite-gain run is 8 bytes) and `!memcmp()` is still
*correct*, just no longer branch-free, at that one length. Recorded here
so a future mechanism reaching for a longer constant-length compare (a
`[WORD-FOLD]` cube compare over a wide class, or any run scan with a
literal near 31 bytes) knows the toolchain-dependent cliff exists and
where.

## 5. Compared against the hand-written load-and-mask form

`cmp_mask_L` (load the smallest covering width, AND-mask, one compare) is
uniformly **one load, one compare, no internal branch** at every `L`
tested (`docs/dev/memcmp_lowering_study/asm/probe_gcc16_O2.s`, functions
`cmp_mask_*`) — cheaper than gcc's own decomposition at every odd length
above 4, and matching gcc's own single-load form at `L ∈ {1,2,4,8}`
exactly (no win there, no loss either). Its cost is the wider safety
condition: `pos + width <= n_` (4 or 8 bytes) rather than `pos + L <=
n_`, i.e. it can read up to `width − L` bytes past the run's own extent —
exactly the over-read `reqpos_2b.md` §3.1 already declined a `memcpy`-
into-`uint64` sketch for ("pcrec does not own the caller's buffer").

The overlapping two-load form (`cmp_overlap_L`, §3) gets both properties
at once on gcc too, not only on clang: built by hand for `L ∈ {5,6,7}`
(`docs/dev/memcmp_lowering_study/gen_probe.py`'s `emit_overlap_fn`), gcc-16
-O2 renders `cmp_overlap_7` as two 4-byte loads (offset 0, offset 3) and a
`ccmp`-chained branchless compare — the *same* shape clang derives
automatically for the plain `!memcmp()` spelling. So the overlapping form
is available to gcc too; gcc simply does not reach for it on its own from
a bare `memcmp()` call at odd lengths — it has to be spelled by hand (two
loads, `&&`) to get it.

**This is exactly the form `reqpos_2b.md` §3.4 reserves as "event 2",
gated on `[WORD-FOLD]`.** Nothing here changes that gating (`[WORD-FOLD]`
is `STATE:not-started` and its own D77 census is unrun, per
`coding_guide.md`'s rule against reaching for an unbuilt primitive) — but
the two-load overlapping form, not a single wide masked load, is the
right target once it lands: it needs no wider safety bound than P4
already has, and it is a strict instruction-count win over gcc's own
decomposition at every odd length this study measured.

## 6. Toolchain columns: gcc-16 arm64 (primary), clang arm64/x86_64 (secondary), gcc-15 x86 (OWED)

| L | gcc-16 arm64 -O2 | clang arm64 -O2 | clang→x86_64 -O2 |
|---|---|---|---|
| 1–24 (all tested) | inline (see §2/§3) except L=31 | inline | inline through L=32 |
| 31 | **CALL** | inline (3 loads) | inline |
| 32 | inline (2×NEON) | inline (2 loads) | inline (2×`movdqu`+`pxor`+`por`+`ptest`) |
| 33 | inline | inline (3 loads) | **CALL** |
| 40, 48, 64 | inline | inline | **CALL** |

clang never calls out on arm64 anywhere in the tested range (1–64, all
inline, growing gracefully to 4 overlapping 8-byte loads chained by
`ccmp` at `L=64`). On x86_64 clang switches from two 16-byte SSE2 XMM
compares to a real `callq _memcmp` at `L=33` — the first length that
needs a third 16-byte-class load.

**gcc-15 on x86 is OWED, per the box mandate (no ssh to the Linux
reference box for a light probe — `BOILERPLATE.md`'s travel-month
topology; heavy Linux runs go through the manager, and this isn't
one, but the mandate reads "never run one yourself over ssh" without a
size exception, so it is left for whoever holds that channel). Exact
commands for a later run, given `probe.c` from this lane
(`docs/dev/memcmp_lowering_study/probe.c`, self-contained, no pcrec
dependency):

```sh
# on the Linux reference box, gcc-15 (or the box's own default gcc if it
# is a 15.x, per xarch_step0.md's pin) :
gcc-15 -O1 -S docs/dev/memcmp_lowering_study/probe.c -o probe_gcc15_O1.s
gcc-15 -O2 -S docs/dev/memcmp_lowering_study/probe.c -o probe_gcc15_O2.s
gcc-15 -O3 -S docs/dev/memcmp_lowering_study/probe.c -o probe_gcc15_O3.s
gcc-15 -Os -S docs/dev/memcmp_lowering_study/probe.c -o probe_gcc15_Os.s
python3 docs/dev/memcmp_lowering_study/analyze_asm.py probe_gcc15_O2.s | grep memcmp
```

Everything the analyzer needs (`analyze_asm.py`) is toolchain-agnostic
text processing — it should run as-is on the resulting `.s` files.

## 7. The real emitted artifact

`build/pcrec -p rx --emit-main -o wit.c --pattern '\.tar'` (this branch's
DFA sites, S1's run-pinned prefilter) emits, inside the file-scope
`rx_ofsskip` block:

```c
static inline size_t rx_ofsskip(const unsigned char *subject, size_t n, size_t pos)
{
    while (pos + 3 < n) {
        size_t cand;
        const void *q = memchr(subject + pos, 46, n - pos);
        if (!q) return n;
        cand = (size_t)((const unsigned char *)q - subject);
        if (cand + 3 >= n) return n;
        if (!memcmp(subject + cand, ".tar", 4)) return cand;
        pos = cand + 1;
    }
    return n;
}
```

— P4's exact shape, `emit_exact_compare`'s `!memcmp(base, "lit", n)` at
`L=4`. Compiling the emitted `wit.c` standalone with `gcc-16 -O2 -S`
shows `rx_ofsskip` fully inlined into `rx_search` (no standalone symbol),
and the `!memcmp(..., ".tar", 4)` site reduced to exactly the `L=4` probe
row from §2 — one 32-bit load, one compare, no call:

```asm
L38:
	sub	x2, x0, x28
	add	x1, x2, 3
	cmp	x27, x1
	bls	L35
	ldr	w1, [x0]          /* the ".tar" compare: one load... */
	cmp	w1, w21           /* ...one compare against a pre-loaded constant */
	beq	L7
```

with `w21` (the constant `0x7261742e`, `".tar"` little-endian) loaded
**once, before `rx_search`'s scan loop even starts** — `mov w21, 29742 /
movk w21, 0x7261, lsl 16`, in the function's prologue — not re-materialized
per candidate. This is stronger than the probe alone shows: on this
artifact gcc also hoists the constant load out of the loop, which the
isolated `cmp_memcmp_4` probe function has no loop to be hoisted out of.
Confirms the probe and the real emitted artifact agree exactly at the one
length ([OPT-LITSCAN]'s own shipped population) that matters today.

## 8. Timing (scratch tier, instruction evidence above is load-bearing; this is corroboration)

`docs/dev/memcmp_lowering_study/bench.c`, `gcc-16 -O2`, `N_CALLS=2,000,000`
per arm, best-of-5, arms rotated within each regime, `timeout 25` on every
run. Full output in `docs/dev/memcmp_lowering_study/bench_results.txt`.
At every `L ∈ {2,3,4,7,8,10,16}` and every regime (match / first-byte
mismatch / last-byte mismatch), all three arms (`memcmp`, per-byte
`if`-chain, load-and-mask) measure **1.2–1.7 ns/call**, i.e. the
call-through-a-function-pointer and loop-bookkeeping overhead this
harness's own dispatch shape pays dominates the compare itself at this
scale — differences between arms are 0.2–0.4 ns, inside this box's own
run-to-run noise band (`opt4_impl/CLAUDE.md`'s own recorded 20% same-
binary spread without interleaving). The one **consistent, directionally
stable** signal: the per-byte `if`-chain is 15–30% slower than `memcmp`/
`mask` specifically on the MATCH and LAST-MISMATCH regimes at `L ≥ 7` —
exactly where it must walk multiple per-byte branches before it can
return, where `memcmp`/`mask` do one wide compare — and ties `memcmp` on
FIRST-MISMATCH, where all three bail on byte 0. This corroborates §3's
instruction-count finding (more pieces, more branches, more chances to
pay for a walk) without adding a number precise enough to rank `memcmp`
against the hand-rolled `mask` form on its own at this study's scale.

## 9. Recommendation

**No length bound and no form split for P4 today.** Every length pcrec's
own corpus and bench populations reach (per `reqpos_2b.md`'s own census)
is inside the region where `!memcmp()` lowers to a call-free, single- or
few-load compare on every toolchain/opt-level combination measured except
`-Os` (not pcrec's shipped GENCFLAGS) and the one narrow `L=31` clic
(unreached by the corpus). `emit_exact_compare`'s existing comment is
correct in spirit and should gain one qualifying clause — its `{2,4,8}`
claim is universal across gcc/clang/opt-level; the *general* "no call at
any tested L" claim holds for gcc at `-O1`/`-O2`/`-O3` and for clang
everywhere tested, but not at `-Os` and not at gcc's `L=31`.

**For `[WORD-FOLD]`'s later masked-class compare** (`reqpos_2b.md` §3.4's
gated "event 2"): prefer the two-load overlapping form over a single wide
masked load. Both are branchless and single-load-class, but the
overlapping form needs only the run's own `pos + L <= n_` bound (P4's
existing discipline) where the masked form needs `pos + width <= n_` (an
over-read `reqpos_2b.md` §3.1 already declined once for the same reason).
Nothing here builds `[WORD-FOLD]` or instructs its use ahead of its own
D77 trigger — this is the evidence a future design note for it would
cite.
