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
5. **[Follow-up, §10] The primary `[WORD-FOLD]`/S4 mask candidate is the
   OVERLAPPING masked form, never the wide single-load over-read** (the
   manager/Frank's scope note: C has no safe over-read and ASan would flag
   it). Timed in a tight loop with the wide form's own bounds guard
   assumed already discharged — the shape most favorable to the "one fewer
   load" argument — the overlapping form is still **17-35% faster**, not
   slower, at every `L ∈ {5,6,7,10,12}` tested, reproducibly. No cap-scale
   argument survives that result; §10 has the numbers and the residual
   open question.

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

**Revised 2026-09-27 per the manager/Frank's scope note** (relayed after
this section's first draft): the wide single-load form's over-read is
deprioritized as a *primary* candidate — C has no safe way to read past
the subject, and `make asan`'s battery would flag exactly this — so the
primary `[WORD-FOLD]`/S4 comparison is the **overlapping MASKED** form,
not a plain wide masked load. §10 below is the full follow-up (a real
ASCII-caseless instantiation, not a trivially-foldable all-ones mask, plus
the hot-loop timing Frank asked for); this section keeps the original
single-wide-load evidence as ONE comparison row, per the note, to show
what the extra latitude costs.

`cmp_mask_L` (load the smallest covering width, AND-mask, one compare) is
uniformly **one load, one compare, no internal branch** at every `L`
tested (`docs/dev/memcmp_lowering_study/asm/probe_gcc16_O2.s`, functions
`cmp_mask_*`) — cheaper *in instruction count* than gcc's own decomposition
at every odd length above 4, and matching gcc's own single-load form at
`L ∈ {1,2,4,8}` exactly (no win there, no loss either). **This is the one
row kept for comparison, labelled with its cost**: the safety condition is
`pos + width <= n_` (4 or 8 bytes) rather than `pos + L <= n_`, i.e. it can
read up to `width − L` bytes past the run's own extent — exactly the
over-read `reqpos_2b.md` §3.1 already declined a `memcpy`-into-`uint64`
sketch for ("pcrec does not own the caller's buffer"), and exactly the
shape an ASan-instrumented artifact would report as a heap-buffer-overflow
read the moment the run sits within `width − L` bytes of the subject's end.

The overlapping two-load form (`cmp_overlap_L`, §3) gets both the
instruction-count win and the safe bound at once on gcc too, not only on
clang: built by hand for `L ∈ {5,6,7}`
(`docs/dev/memcmp_lowering_study/gen_probe.py`'s `emit_overlap_fn`), gcc-16
-O2 renders `cmp_overlap_7` as two 4-byte loads (offset 0, offset 3) and a
`ccmp`-chained branchless compare — the *same* shape clang derives
automatically for the plain `!memcmp()` spelling. So the overlapping form
is available to gcc too; gcc simply does not reach for it on its own from
a bare `memcmp()` call at odd lengths — it has to be spelled by hand (two
loads, `&&`) to get it. **This exact-byte overlap form is what §10's
caseless instantiation extends with real masks.**

**This is exactly the form `reqpos_2b.md` §3.4 reserves as "event 2",
gated on `[WORD-FOLD]`.** Nothing here changes that gating (`[WORD-FOLD]`
is `STATE:not-started` and its own D77 census is unrun, per
`coding_guide.md`'s rule against reaching for an unbuilt primitive) — but
the two-load overlapping form, never the single wide masked load, is the
right target once it lands: it needs no wider safety bound than P4
already has, it never triggers ASan's over-read report, and it is a
strict instruction-count win over gcc's own decomposition at every odd
length this study measured. §10 extends the comparison to the real
caseless-mask shape and the hot-loop timing question.

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
`-Os` (not pcrec's shipped GENCFLAGS) and the one narrow `L=31` cliff
(unreached by the corpus). `emit_exact_compare`'s existing comment is
correct in spirit and should gain one qualifying clause — its `{2,4,8}`
claim is universal across gcc/clang/opt-level; the *general* "no call at
any tested L" claim holds for gcc at `-O1`/`-O2`/`-O3` and for clang
everywhere tested, but not at `-Os` and not at gcc's `L=31`.

**For `[WORD-FOLD]`'s later masked-class compare** (`reqpos_2b.md` §3.4's
gated "event 2"): prefer the two-load OVERLAPPING MASKED form over a
single wide masked load — never the over-read form as a primary
candidate, per the manager/Frank's scope note (§10). Both are single-
load-class per window, but the overlapping form needs only the run's own
`pos + L <= n_` bound (P4's existing discipline, and ASan-clean) where the
masked form needs `pos + width <= n_` (an over-read `reqpos_2b.md` §3.1
already declined once for the same reason, and one `make asan` would
flag). §10 measures the overlapping form's own timing against the wide
form's in a tight loop and finds the overlap form FASTER, not merely
safer — a genuinely counter-intuitive result worth reading before assuming
the extra load costs anything. Nothing here builds `[WORD-FOLD]` or
instructs its use ahead of its own D77 trigger — this is the evidence a
future design note for it would cite.

## 10. Follow-up (manager + Frank, same day): the overlapping MASKED form as primary, and the hot-loop single-wide-load timing

Two notes arrived after §0-§9 were written. Both are answered here rather
than by silently rewriting the sections above (this is the lane's own
memo on its own day, not a ratified design document under D80, but the
original evidence in §3/§5 stays intact and this section is additive).

### 10.1 The overlapping form gets a real mask, not an all-ones one

An AND-mask of all-ones is invisible to the compiler — it constant-folds
away, so `cmp_overlap_L` (§3/§5) was never actually testing a "masked"
compare, only an exact-byte one. `cmp_ovmask_L`
(`docs/dev/memcmp_lowering_study/gen_probe.py`'s `emit_ovmask_fn`) is the
real instantiation the manager asked for: two natural-width overlapping
loads (window width `W`, the smallest power of two with `W < L <= 2W`,
matching §3's own empirical rule for what clang picks), each AND-masked
with the classic ASCII case-fold mask (`0xDF` per byte, clears bit 5 so
`'a'..'z'` folds onto `'A'..'Z'`) and compared against the literal's own
folded value — genuinely non-trivial constants a compiler cannot fold
away. Safety condition unchanged: `pos + L <= n_` only.

**Instruction counts, gcc-16 -O2, arm64** (full table in
`docs/dev/memcmp_lowering_study/asm/probe_gcc16_O2.s`, functions
`cmp_ovmask_*`):

| L | loads | ANDs | compares | branches | shape |
|---|---|---|---|---|---|
| 3 | 2 (2-byte) | 2 | 2 | 1 (short-circuit) | `ldrh@0`, `and`, `cmp`, `beq` → `ldrh@1`, `and`, `cmp` |
| 5,6,7 | 2 (4-byte) | 2 | 2 | 1 (short-circuit) | `ldr@0`, `and`, `cmp`, `beq` → `ldr@(L-4)`, `and`, `cmp` |
| 9–15 | 2 (8-byte) | 2 | 2 | 1 (short-circuit) | `ldr@0`(x), `and`, `cmp`, `beq` → `ldr@(L-8)`(x), `and`, `cmp` |

**gcc regresses to a real branch here, where the exact-byte overlap form
(§3/§5) was branchless.** Verbatim, `cmp_ovmask_7` at -O2:

```asm
	ldr	w2, [x0, x1]
	mov	w3, 16961
	movk	w3, 0x4443, lsl 16
	and	w2, w2, -538976289    /* AND with the 0xDF-per-byte mask */
	cmp	w2, w3
	beq	L197                  /* a REAL branch, not ccmp */
L196:
	mov	w0, 0
	ret
L197:
	add	x0, x0, x1
	mov	w1, 17732
	ldr	w0, [x0, 3]
	movk	w1, 0x4746, lsl 16
	and	w0, w0, -538976289
	cmp	w0, w1
	cset	w0, eq
	ret
```

**clang keeps the branchless `ccmp` chain even with the AND**, unaffected
by the mask (`docs/dev/memcmp_lowering_study/asm/probe_clang_O2.s`,
`cmp_ovmask_7`): two loads, two ANDs, `cmp` + `ccmp`, one `cset`, only the
outer bounds branch. So the masked form costs gcc a branch it didn't pay
for the unmasked overlap — a second gcc-vs-clang asymmetry beyond §3's
odd-length decomposition, worth knowing before assuming the two toolchains
converge once a mask is added.

### 10.2 The hot-loop timing: overlap vs single-wide-load, guard discharged

`docs/dev/memcmp_lowering_study/bench_hotloop.c`: for `L ∈ {5,6,7,10,12}`,
scan a literal at every candidate position of a 1 MiB pseudo-random buffer
(a handful of positions carrying a planted match, ~0.03% of the buffer —
the realistic "mostly absent" regime `reqpos_2b.md` §3.3 already treats as
the dominant real-world case), comparing:

- **overlap**: the `cmp_ovmask_L` shape above (two natural-width masked
  loads, `pos + L <= n_`).
- **wide**: ONE load of the smallest covering natural width (`uint64_t`
  for `L <= 8`, `unsigned __int128` for `L ∈ {10,12}`), masked, compared —
  **with its own wider bounds guard (`pos + W <= n_`) assumed already
  discharged by the caller**, i.e. neither arm does a per-position bounds
  check inside the timed loop; the outer loop bound (established once,
  identical for both arms) plays that role.

Best-of-7 rounds, 300 repeats per round, `timeout 25` on every run, results
reproduced by a second independent run (deltas held to within 0.1-0.2%
across repeats — this signal is far above the earlier per-call bench's
noise band, §8):

| L | overlap (ns/iter) | wide (ns/iter) | delta | delta as % of wide |
|---|---|---|---|---|
| 5 | 0.656 | 1.009 | −0.353 | **−35.0%** |
| 6 | 0.656 | 1.008 | −0.352 | **−34.9%** |
| 7 | 0.656 | 1.003 | −0.347 | **−34.6%** |
| 10 | 0.656 | 0.793 | −0.137 | **−17.3%** |
| 12 | 0.645 | 0.775 | −0.130 | **−16.8%** |

**Above noise, and the opposite sign from the "one fewer load must be
faster" intuition — the overlapping form is faster, not slower, at every
tested `L`.** Reading the generated loop bodies
(`docs/dev/memcmp_lowering_study/bench_hotloop_results.txt` for the raw
numbers; the loop bodies themselves are in `/tmp` scratch during this
session and are not committed, per the box's scratch-file rule — the
excerpt below is transcribed from them) shows the overlap loop's
short-circuit still fires inside the tight loop: `bne L4` skips the
SECOND load+mask+compare entirely on a first-window mismatch, so on this
buffer's ~99.97%-mismatch population the overlap arm executes roughly one
load+AND+cmp per iteration on its fast path — the same per-iteration work
the wide arm always does unconditionally (its own `cmp`+`cinc` sequence is
branchless but pays for load+AND+cmp every time, never skipping).

**A quick control (all-candidate-positions-matching, not committed as a
regime the main table reports) narrows but does not close the gap** — at
`L=7`, all-match measures −23.9% (against −34.6% mostly-absent) and at
`L=12`, −14.9% (against −16.8%). So the short-circuit explains PART of the
advantage (the gap shrinks when it can't fire as often) but not all of
it — something in the wide arm's larger immediate/constant (a 64-bit or
128-bit mask+target, materialized via multiple `movk`s or, for `L ∈
{10,12}`, `__uint128_t` arithmetic that gcc lowers to two 64-bit register
operations rather than one true wide operation) costs real time even when
both arms do the same number of "logical" comparisons. This second
component is not fully instruction-traced here — a `perf`-level
latency/throughput breakdown would be needed and `perf` is denied on this
box (`opt3_dfa_scan_measurement.md`'s own precedent) — so it is reported
as an open residual, not a diagnosed mechanism.

**No recommendation beyond what this number supports, per the ask.** The
single-wide-load form does not appear to win the hot-loop case its own
one-fewer-load argument was made for, on this box, at these lengths, in
this regime. Whether that holds on a different microarchitecture, at a
higher match rate, or with the bounds-check genuinely inlined (rather than
assumed discharged) is unmeasured.

## 11. Second follow-up (team-lead, same day): should P4 spell its own overlap under gcc — three arms in a realistic hot loop

`docs/dev/memcmp_lowering_study/bench_hotloop2.c`: `memcmp` (P4's own
form) vs the hand-written overlap (exact bytes, §3/§5) vs the wide masked
single load (§10.2's guard-discharged shape), all under gcc-16 -O2, at
every candidate position of a 1 MiB buffer whose content is realistic
rather than pure-random: a dense band of NEAR MISSES (the literal with its
last byte flipped, planted every 797 bytes — the shape that forces gcc's
branchy multi-piece `memcmp` decomposition, §3, to walk every piece before
failing) plus a sparse full-match band (every 4001 bytes) over an
otherwise pseudo-random buffer. `L ∈ {5,6,7,10,12,15}`, best-of-7 rounds,
arms interleaved within every round, `timeout 25`, reproduced by a second
run (L=7/L=12 held within 1-3%).

| L | memcmp (ns/iter) | overlap (ns/iter) | overlap vs memcmp | wide (ns/iter) | wide vs memcmp |
|---|---|---|---|---|---|
| 5 | 0.509 | 0.470 | **−7.6%** | 1.014 | +99.3% |
| 6 | 0.497 | 0.467 | **−6.1%** | 1.015 | +104.2% |
| 7 | 0.490 | 0.461 | **−5.9%** | 1.014 | +107.2% |
| 10 | 0.495 | 0.467 | **−5.6%** | 0.798 | +61.4% |
| 12 | 0.509 | 0.477 | **−6.4%** | 0.802 | +57.4% |
| 15 | 0.505 | 0.473 | **−6.5%** | 0.802 | +58.6% |

**Above noise and consistent in sign and rough magnitude across all six
lengths** (5.6-7.6%), unlike §8's per-call bench where 0.2-0.4 ns
differences on a ~1.3 ns base were noise — here the delta is measured
inside a tight loop with no call-through-a-function-pointer overhead, and
it reproduces run to run. **Wide is dramatically worse than both other
arms in this regime** (57-107% slower than `memcmp` itself, not just
slower than overlap), because it pays the same one-load-and-mask cost on
every position including the sparse random background where `memcmp` and
`overlap` both exit after their very first (mismatching) piece — the wide
form has no early exit at all, so a realistic mostly-absent scan is its
worst case, not its best one.

**Answering the two questions directly, on the numbers alone (D77 — no
recommendation beyond what they support):**

- **Should P4 spell its own overlapping-load form for odd `L` under gcc,
  instead of relying on `memcmp()`?** The measured win is real, consistent
  across all six lengths tested, and reproducible — but it is **5.6-7.6%
  per compare call**, not the multiple-times difference the instruction
  counts (§3: gcc's own decomposition needs up to 4 sequential
  loads/compares/branches at `L=15`) might suggest. Whether that is worth
  a second emitted form (more emitter code, a second sabotage-anchor
  surface, `[CC-DIFF]`'s own "one spelling of a constant-length literal
  compare" discipline given up) is a question this measurement answers
  the SIZE of, not the answer to.
- **Is (c)'s (the wide single load's) saving worth pursuing?** No —
  it has no saving in this regime; it is the slowest arm by a wide
  margin, on the realistic subject this section builds specifically
  because it stresses the near-miss case. Combined with the ASan/over-read
  objection §5/§10 already raised, this closes the wide-single-load
  candidate on both correctness-adjacent and performance grounds; nothing
  further makes it worth building.

Every number here is scratch-tier and box-specific (this Mac, gcc-16,
one realistic-but-synthetic subject shape); the qualitative ranking
(overlap ≤ memcmp ≪ wide) held across every length tried and both
regimes measured in §10-§11, which is the strongest claim this study's
scale supports.
