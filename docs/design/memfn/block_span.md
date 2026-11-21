# The vector span: building job 710's block span at the SIMD layer (R-47, D201)

Status: DESIGN, rev 2 (lane bspan2, 2026-11-21, sonnet). Rev 2 (2026-11-21):
folds in the rulings `scalar-wrap` (option A with a scalar no-loss check),
`scan-scope`, `wrap-deny`, the final census, and the ship-size account.
Rev 1 (lane bspan, opus; R-1..R-4). Design only: no code.
Request R-47 (`memfn/docs/requests.md`); ruling D201 ("build with simd
layer", slug block-build). Order: this note, then a critic round, then the
build. Not gated: every rev 1 question is resolved (§15).

Revision history: rev 1 (2026-11-21): first design, gated on
`scalar-wrap`. rev 2 (2026-11-21): scalar-wrap ruled A, option B retired,
U2b and T-keep added, population record replaced by the final census,
manager calls recorded, §17 ship-size.

Inputs read: D201, D146, D147, D155, D76/D94, D80, D144; integration.md §14,
§15, §17.2, §18; the 710 run's `decision.md` (TABLE, ARMS, THE CLAIM,
CONTROL), `confirm.py`, `spike708.py` (`span_fn`, `nib_blk`, `span_body`);
the 708 reports; the reviews 2026-11-20-memfn-blockconfirm and
-bcfix-recheck (MEASUREMENT-3); `docs/dev/guide/README.md` + `coding.md`.

## 0. Goals (ranked; a conflict goes to the higher one)

| # | goal | who benefits | checkable form |
|---|---|---|---|
| G-1 | **Answer identity.** Every artifact answers exactly as today, at every layer, width and target. | every caller | G2 (§10): 0 differences against python `re` and against the family's own reference, on guard-page subjects; the answer-identity sweep's `span-vector` deny arm agrees with the default on the whole corpus |
| G-2 | **The shipped text is the timed text.** Where the table routes a stretch, the machine code gcc makes for `rxa_search` is identical to 710's `avx2-loop` arm. Where a difference remains, it is named and measured. | the 710 verdict's validity (MEASUREMENT-3) | F2 (§6): `objdump` of `rxa_search` is identical to 710's arm source, after addresses are normalized, on every one of the 710 grid's 130 patterns. Each pattern that differs is listed and goes into card C6's population. |
| G-3 | **No repeated LOSS where it ships.** The SIMD-on movers keep 710's claim: no repeated LOSS against `--memfn=no-span-vector`. | `-fmemfn-simd` users with long one-class spans | the post-build card C6 run (§8) under 710's rule, read the same way: 0 repeated LOSS; on the S-pick cells, WIN on a strict majority |
| G-4 | **Nothing else moves.** At SIMD-off, and at every target that does not admit `w32`, the only bytes that move are the ones §11 lists. The deny restores today's bytes exactly. | default-build users (the scalar layer stays H64, D201) | an identity gate: the `no-span-vector` artifact equals main's artifact byte for byte over the corpus, at both layers. The pcrec-side G1 population (§9.4) equals §11's mover classes, counted. |
| G-5 | **One table, no parallel mechanism.** The span-form choice is one declared first-match table, and these are its rows. | maintainers (Frank's table rule) | `wf_span_head` is retired. One row array exists. A grep for a second span-form decision finds none. |

Non-goals: the scalar layer's own block form (D201: H64 stays; "Revisit
when the scalar layer is measured"); a 16-byte (`w16`) rung; the SWAR rung
of 708's cascade (no table row reaches it, §4.4); a periodic span; the LIBC,
PAIR and floor sites (unmeasured, §3.3); aarch64 (K-4; D147 addendum 8).

### 0.1 Population record (final census; information only, D201 add. 1)

Source: lane/spancensus2 (`docs/dev/lanes/spancensus2_report.md`; it
supersedes the first census, lane/spancensus d0848d0ed). Compiled at
SIMD-on with each pattern's OWN options, `--harness=span-head=0`,
`--window-search-width=4095`.

| set | distinct (text, options) pairs | routed to V |
|---|---|---|
| pcrec test corpus | 6403 (5645 texts) | **1** (1 of 5645 texts): `tests/counterk/counterk.rxt` line 1919, scan k=48 |
| bench catalogue | 363 (356 texts) | **3** (3 of 356 texts): bounded/hex32 and loglines/hex32-id (window k=31), bounded/dig-exact-32 (scan k=31) |

- Only `--encoding=utf8` moved a span site, and only at k ≤ 3; the
  routed set did not move from the first census.
- Not applied: the callout/code-header grants (23 `(?C` blocks refused).
- **At the default window width (32) only k 16-31 (window) / 24-31 (scan)
  is eligible.** The 32-1000 wins need `--window-search-width`; main's owed
  cover-width timing (`cover_cap.md` §11.4 B) decides whether that default
  rises.
- The count is INFORMATION ONLY. It does not gate the build (D201 addendum
  1: "We're here and there's no downside so let's build it."). Under R-4
  rev 2 keeps the smallest form: one V stretch per site (§3.2), a fixed
  guarded bound (§5), no committed fixture set (§6), a bounds-only card
  (§8), four sabotage rows (§10), and the ship-size account in §17.

## 1. Site map: where it lives today (found by grep)

| what | where (command) | today |
|---|---|---|
| the option row | `grep -n 'span-loop' memfn/src/options.def` → 122 | `MF_OPT("span-loop", MF_OPT_PAIR, MF_B_ANY, MF_L_SCALAR, ...)`. Deny = I, force = L |
| the decision | `grep -n WF_SPAN_HEAD memfn/src/window.c` → 1470, 1476, 1483 | `wf_span_head()` (window.c:1477): an IF CHAIN (deny → I, force → L, lever `span-head=N` → H(N), else H(64)), returned as one head `h` per SITE (`plan_of`, :1491) |
| the segmenter | `grep -n 'wf_loop_len\|static int wf_loop\|wf_test_to' memfn/src/window.c` | `wf_test_to` (:3542) walks the plan in offset order. `wf_loop_len` (:3498) finds a ONE-CLASS STRETCH: consecutive core `KIT_POS_WIDE` entries with one set and one table offer, at offsets ≥ h. `wf_loop` (:3517) renders it as one loop |
| who renders it | `wf_test_to`'s callers: `c_find_test` (E-find) and `wf_test` (E-generic, the floor) | the only two renderers of a candidate test |
| 710's "site kind" | `grep -n 'RB_HORS\|RB_WALK' memfn/src/window.c`; `struct wf_plan` field `pick` (:1400) | "window" (`rxa_mf1_sh[` in the text) = E-find with pick `FF_HORS` (row D-hors, renderer B-hors). "scan" = E-find with pick `FF_WALK` (renderer B-walk). Each of 710's four scan classes (dig, hi, upper, num: 10, 64, 26 and 12 members) is a walk |
| the level fact | `grep -n 'art->levels = ' memfn/src/compose.c` → 1102; `memfn/src/levels.def` | `art->levels` = the levels the target admits: `LV_X86_W16` (sse2, x86-64) and `LV_X86_W32` (avx2, x86-64-v3). 0 at `-fno-memfn-simd` |
| the SIMD seam idiom | `memfn/src/vany.c` (`vany_level`, `vany_selector`); `ofsskip.c` (D155) | `<fn>__body`, one bracketed helper `<fn>__<stamp>` per admitted level, and a selector `<fn>` with ONE call to the top helper. `simd_open`/`simd_close` bracket WHOLE LINES (`src/core/sb.c` `pcrec_sb_simd_open`: "a bracket opened mid-line" aborts) |
| the header fact | `memfn/src/includes_c.def` | `MF_INC_LEVEL_W32` = `#include <immintrin.h>`, placed by pcrec at file scope, ahead of the region |

**Premise test (the brief's).** Both greps hit. The 710 TABLE's "site =
window / scan" maps to facts the kit already has at render time: the plan's
frame (`w->skel` is E-find) and its pick (`w->pick` ∈ {`FF_HORS`, `FF_WALK`}).
k is the stretch's length, which `wf_loop_len` computes. The SIMD-on layer
is `art->levels & (1u << LV_X86_W32)`. No pcrec-side fact is needed. All of
these are the kit's own picks, so facts-only (D157) holds.

**One correction to the brief's framing.** There is no separate "scan site"
span. Both 710 site kinds are window.c E-find sites. They differ only in
T-FIND's pick (HORS or WALK).

## 2. THE PREMISE FORK, RESOLVED: the timed text is not a shape the SIMD seam admits

Job 710 timed this replacement: inside the walk's statement expression,
which is ONE line, the span's inline chain is replaced by a call to an
`always_inline` function defined at the top of the region. The SIMD-off
artifact keeps the chain. That diff between OFF and ON is an **inline
expression replaced mid-line**. The contract admits exactly two kinds of
difference:

- **C18 (c)** (`tests/memfn/simd_floor_check.py` docstring): "the raw diff
  OFF -> ON deletes no line but the moved stamps and, per SIMD FUNC, its
  one `return <fn>__body(<args>);`, replaced by the same call to
  `<fn>__w<VW>`".
- **`limits.md` §8.3¶1**: the length every size decision reads is the
  SIMD-off length exactly, so "turning SIMD on cannot rescue or refuse a
  pattern or move a ladder step". `tuning.md` §2.43¶4 states the same
  floor.

A mid-line replacement cannot be bracketed (the sink aborts on a mid-line
bracket). It shortens an unguarded line, so the length decisions would read
a SIMD-dependent length. The 710 shape therefore fails C18 and breaks
§8.3¶1.

**The shape taken (option A, RULED 2026-11-21).** An eligible stretch (§3:
HORS with 16 ≤ k ≤ 1000, or WALK with 24 ≤ k ≤ 64; these are
layer-independent facts) renders **at every layer** as a call
`<p>_mf<h>_vs<j>(S, C)` to a selector, exactly vany's shape:
- `__body` is today's H64 text of that stretch;
- at a target admitting `w32`, a bracketed helper `__w32` is added (the
  710 form) and the selector's one call names it.

This is the standing SIMD organization agreed back when the kit used `#if`
code (D155, addendum 1 Q-R9-10, cited per rulings R-1): a working function
holds no `#if`; a selector picks the level, one call per arm (the CPU `#if`
is gone today, `limits.md` §8.3¶1). Option A is that shape applied to the
span, not a new cost.

OFF and ON then differ only as C18 admits, and the lengths stay those of
SIMD-off. **The cost: SIMD-off bytes move** on eligible stretches. The FORM
is still H64 (D201), but its text sits inside a function.

**The wrapper is code organization in source; the machine code can still
differ.** Frank's ruling (verbatim): "Scalar wrap: the function goes inline
so it's just code organization? If that's true I don't have a problem with
that." The function is `always_inline`, so in source it is only code
organization. gcc's machine code for `rxa_search` is not always the same,
and that is why the check in §2.1 exists:
- 710's control arm Hspk is exactly this wrapper at SIMD-on. On the cells
  the table routes it had 0 standing LOSS and 3 standing WIN (num k=64;
  `decision.md` CONTROL).
- Probes (gcc 15.2 -O2, `objdump -d` of `rxa_search`, today's text against
  the wrapped one): at SIMD-off at the default width 8 of 10 patterns are
  identical; **2 of 10 differ, `\w{20}` and `\w{32}`** (97 lines). At width
  4095, 6 of 8 are identical (§16 item 6).
- At SIMD-off the wrapper has not been timed.

**Why option B was not taken.** B admitted "a replaced inline expression"
as a third diff kind, keeping SIMD-off bytes and 710's exact text, but it
changes C18 (c)/(b), `tuning.md` §2.43¶4 and pcrec's length accounting (a
kit-to-pcrec fact, or a second OFF render): a seam change outside this
design's remit, with its own architecture note. The ruling makes it
unnecessary.

### 2.1 The scalar no-loss check (a build unit, §14 U2b, before landing)

Because the machine code can differ, the build proves the wrapper does not
lose at SIMD-off. Three parts:

- **(a) A NON-TIMING census.** Over the pcrec test corpus and the bench
  catalogue, list the sites whose SIMD-off `rxa_search` machine code
  differs between today's text and the wrapped text. Method: `objdump -d`
  with addresses normalized, at the default window width AND at
  `--window-search-width=4095`. Reuse the census method of
  `docs/dev/lanes/spancensus2_report.md` and its script (`git -C
  /home/pcrec/projects/pcrec show
  lane/spancensus2:docs/dev/lanes/spancensus_census.py`: the `--list-source`
  option reader, the site regexes), and rev 1's `wrapprobe` method (§16
  item 6b).
- **(b) A short SCALAR timing** of ONLY the differing sites, wrapped
  against today, in a window Frank clears. The decision rule and its floor
  are written BEFORE data, using 710's cards/A-A method (floor from the
  A/A repeat rate, re-time, control); the rule's sha is recorded with the
  result.
- **(c) A loser keeps today's text** through a declared row of the same
  first-match table: **T-keep** (§3), which holds for a stretch on a
  declared keep list and renders H(64) unwrapped. Cost to name: T-keep
  drops the selector for that stretch at every layer, so the SIMD win on
  that stretch is forfeited too (the SIMD helper needs the selector); the
  build go decides whether that trade is taken for a given loser.

The step costs nothing where (a) finds zero differing sites: no timing,
no T-keep.

## 3. The selection: THE SPAN FORM TABLE (rows added to the existing choice)

`wf_span_head`'s if chain becomes a declared first-match table. Its rows
are evaluated **per one-class stretch**, at render, in `wf_test_to`. The
facts:

| fact | where it comes from |
|---|---|
| `opt(span-loop)`, `opt(span-vector)` | the site's opts (`kit_opt_state`) |
| `lever` | the art's `KIT_LEVER_SPAN_HEAD`, test-only |
| `frame` | `w->skel` |
| `pick` | `w->pick` |
| `k` | the stretch's length (§3.1) |
| `w32` | `art->levels & (1u << LV_X86_W32)` |

Compile-time facts only; no class name.

| row | holds when (first match) | form | origin |
|---|---|---|---|
| T-deny | `no-span-loop` given | I (every position inline) | today, row 1 of the chain |
| T-force | `span-loop` forced | L (h = 0) | today, row 2 |
| T-lever | test-only `span-head=N` | H(N) | today, row 3 (the cards' instrument) |
| T-keep | the stretch is on the declared keep list (§2.1: a site the scalar no-loss check found losing) | H(64), unwrapped (today's text, no selector) | **NEW**, EMPTY until U2b's census and timing fill it; not built if U2b finds nothing |
| T-vwin | frame E-find, pick HORS, 16 ≤ k ≤ 1000, `span-vector` not denied | V | **NEW**, 710 row 1, MEASURED |
| T-vscan | frame E-find, pick WALK, 24 ≤ k ≤ 64, `span-vector` not denied | V | **NEW**, 710 row 2, MEASURED |
| T-head | always | H(64) | today, the default (`WF_SPAN_HEAD`, MEASURED by cards run fcards-zen4-1) |

**V** is the selector call (§5). Its text is layer-dependent; its
selection is not. That is what keeps C18's diff to one replaced call.

The deny `span-vector` is the V rows' option column, in the
`wf_erows[].opt` idiom (`e_opt`): a row whose option is denied does not
hold. The table rides `kit_table` (`{ "wfS", ..., s_holds, s_opt }`), so
MFTRACE names the deciding row, as Table E's do. T-deny, T-force and
T-lever stay ahead of V, for three reasons:
- the escape hatch still means "the text before the forms";
- the sweep's force arm still exercises L at SIMD-on;
- cards C1-C5 re-run unchanged. Their h-arms would silently become V at
  layer "on" if V came first.

### 3.1 What k is

k is the number of entries one loop would test if L (h = 0) segmented the
plan: `wf_loop_len(w, i, skip)` evaluated with head 0. That is the maximal
run of consecutive core `KIT_POS_WIDE` entries from entry i, all with one
set and one table offer, starting at an offset ≥ 0, never crossing the
search-proven entry `skip` or a C-run compare. This is exactly 710's k:
`parse_span` checked that the span covers k consecutive positions with
one test (the probed position excluded). Measured: at the default width,
`[0-9a-f]{17}` has 16 tested positions plus the probe, and `[0-9]{25}`
has the stop plus 24 (§16 item 5).

Where T-head (or T-lever, T-force, T-deny) decides, the stretch renders
exactly as today: lone tests below h, a loop from h on. So the per-stretch
evaluation reproduces today's bytes for every non-V stretch. `w->head`
retires into the H rows. The build proves the refactor with an identity
gate (unit U1, §14).

### 3.2 Where 710's rows generalize, and how far this note lets them

- **Several stretches in one site.** 710's patterns hold one stretch each,
  and so does every routed site the census found (§0.1). SMALLEST FORM
  (rulings R-4): V renders for the site's FIRST eligible stretch only, and
  any later one falls to T-head (answer-identical). A second stretch needs
  a width above 32, and the census counts 0 such sites.
- **Default width.** 710 ran at `--window-search-width=4095`. At pcrec's
  default width (32) a window site holds at most 32 positions, so k ≤ 31.
  I checked the text: `[0-9a-f]{17}` and `[0-9]{25}` are byte-identical
  at both widths (§16 item 5), so 710's k = 16..31 cells ARE the
  default-width text.

### 3.3 What the rows deliberately exclude

710's harness called every non-HORS site "scan". Every scan cell it timed
was a WALK. The declared table's words ("skips to a member byte") also
cover memchr finds (LIBC, LIBC_BACK) and PAIR. Those were not measured.

T-vscan therefore keys on WALK alone (`scan-scope` RESOLVED, manager
2026-11-21: nothing else was measured; D77).
The floor (E-generic) and the legacy rows (E-func, E-stmt) never reach
`wf_test_to`'s span path with a pick, so T-head holds there.

A target admitting only `w16` (`-fmemfn-simd=x86-64`) gets the selector
calling `__body`. SSE2 has no `pshufb` for the 16-byte rung, and no `w16`
form was measured.

## 4. The form's emitted C text (708's avx2-loop, as 710 timed it)

### 4.1 Per stretch, inside the `w32` bracket

Names follow the family's `<prefix>_mf<handle>_*` rule. `j` is the
stretch's index within the site. `B` = 32 where k ≥ 32, else 16.

```c
static inline __attribute__((always_inline)) int rxa_mf1_vs0__w32_b(const unsigned char *p)
{
    const __m256i x = _mm256_loadu_si256((const __m256i *)p);
    const __m256i b0 = _mm256_shuffle_epi8(_mm256_set_epi8(<lo_t x2, 32 bytes>), x);
    const __m256i b1 = _mm256_shuffle_epi8(_mm256_set_epi8(<hi_t x2>), _mm256_xor_si256(x, _mm256_set1_epi8(-128)));
    const __m256i bm = _mm256_or_si256(b0, b1);
    const __m256i hn = _mm256_and_si256(_mm256_srli_epi16(x, 4), _mm256_set1_epi8(15));
    const __m256i bit = _mm256_shuffle_epi8(_mm256_set_epi8(-128, 64, 32, 16, 8, 4, 2, 1, x4), hn);
    return _mm256_movemask_epi8(_mm256_cmpeq_epi8(_mm256_and_si256(bm, bit), _mm256_setzero_si256())) == 0;
}
static inline __attribute__((always_inline)) int rxa_mf1_vs0__w32(const unsigned char *rxa_mf1_s, size_t rxa_mf1_c)
{
    const unsigned char *p = rxa_mf1_s + rxa_mf1_c + LO;
    size_t i = 0;
    for (; i + B < K; i += B) if (!rxa_mf1_vs0__w32_b(p + i)) return 0;
    return rxa_mf1_vs0__w32_b(p + (K - B));
}
```

- At B = 16 the block helper is `nib_blk`'s `sse` text: `__m128i`, `_mm_`
  names, one table copy each.
- `lo_t[l]` = the bits `1 << h`, for the high nibbles h in 0..7 such that
  `(h << 4 | l)` is in the set. `hi_t` is the same for h in 8..15
  (`spike708.py` `nibble_tables`).
- The kit computes both tables in C from the stretch's 32-byte set
  (`w->set[i]`). It never reads a class name or the C-table offer: an
  offered table's set equals `w->set` (`offer_at` requires it), so the
  answers agree.

**What differs from the timed text, and why it is harmless:**
- the identifiers: renamed;
- the 710 harness's `/* blockconfirm ... */` comment: dropped;
- the `target("avx2")` and `target("ssse3")` attributes: dropped. The
  region supplies the ISA (unit U2, vany's idiom). Dropping them was
  machine-code identical on 6 of 6 probes (§16 item 6);
- the base `rxa_mf1_s + rxa_mf1_c + LO` is computed in the `__w32` helper,
  not in the harness's `rxs_span`.

F2 (§6) checks all of this against the whole 710 grid.

### 4.2 Over-read and boundary argument

The stretch is core. THE HOISTED BOUND (`wf_bound`: `C + chi < N`, plus
the lower half where an offset is < 0) is tested before the candidate test
on every frame. Therefore every byte `S[C + o]` with o in [LO, LO + K) lies
inside the subject. The same fact lets today's loop (`wf_loop`) read them.

The block form reads exactly [p, p + K):
- each loop trip reads [p + i, p + i + B) with i + B < K;
- the final block reads [p + K - B, p + K), and K ≥ B holds by B's choice
  (the largest of 32, 16 that is ≤ K).

There is no partial vector, no read past p + K and none below p, on any
path. Lanes the final block shares with the last trip are re-tested
(idempotent). The proof is the same as vany.c's OVER-READ argument, with
[pos, n) replaced by [p, p + K).

### 4.3 Answer identity

Today's text and V compute the same pure conjunction over the same bytes.
Both are side-effect-free, and every read is in bounds before either runs.
So the order of evaluation (blocks, then the overlapped tail) cannot change
the value.

The nibble test is the universal byte-set test (708's critic: correct for
any set, the empty set and the 255-byte `[^\n]` included). `pshufb` zeroes
a lane whose index has bit 7 set. b0 covers high nibbles 0..7, and b1
covers 8..15 through the XOR. `bit` = `1 << (hn & 7)`. A byte is a member
iff `bm & bit` ≠ 0.

### 4.4 The cascade below 32 B, restricted to what the table reaches

708's avx2-loop cascade is AVX2 32 at k ≥ 32, SSE 16 at k = 16..31, SWAR
8 at k = 8..15 and SWAR 4 below that.

T-vwin starts at k = 16 and T-vscan at k = 24, so **no row reaches a SWAR
rung**. The build emits the 32 and 16 rungs only. That removes dead text,
and with it 708's `SWAR_MAX_RANGES = 8` (an UNMEASURED DEFAULT) and its
bitmap fallback.

The 16-byte rung inside the `w32` helper is an SSSE3 instruction stream
within the x86-64-v3 region, not a `w16` level. 710's MEASUREMENT-9 notes
that its row-1 cells at k = 16..31 and its row-2 cells at k = 24..31
"measure SSE-16, not AVX2". So they measured exactly this.

## 5. The seam shape at both layers (option A)

**At every layer**, for every V stretch:
- the walk's text holds `rxa_mf1_vs0(rxa_mf1_s, rxa_mf1_c)` where the
  stretch's chain stood;
- the E-find define (`wf_find_define`, after the run compares' word loads
  and the stream row's table) writes the functions below at file scope,
  inside the region, after the `_sh` table.

```c
static inline __attribute__((always_inline)) int rxa_mf1_vs0__body(const unsigned char *rxa_mf1_s, size_t rxa_mf1_c)
{
    return <today's H64 text of the stretch: its lone tests, then its loop>;
}
static inline __attribute__((always_inline)) int rxa_mf1_vs0(const unsigned char *rxa_mf1_s, size_t rxa_mf1_c)
{
    return rxa_mf1_vs0__body(rxa_mf1_s, rxa_mf1_c);
}
```

**At a target admitting `w32`:**
- §4.1's two functions are written between `simd_open(LV_X86_W32)` and
  `simd_close`, ahead of the selector;
- the selector's one line becomes the bracketed
  `    return rxa_mf1_vs0__w32(rxa_mf1_s, rxa_mf1_c);`, which is C18 (c)'s
  replaced call verbatim;
- the plan's `includes` gains `MF_INC_LEVEL_W32`, a fact pcrec writes ahead
  of the region, the way 710 placed `<immintrin.h>`;
- the site's `MEMFN_FORMS` token is `span-vector@w32`;
- `<PREFIX>_SIMD_GUARDED_BYTES` counts the bracket.

The `__body` text is today's renderer, unchanged: `wf_pos_test` and
`wf_loop` with the stretch's offsets. The H64 form at the scalar layer is
kept, as D201 says, but moved into a function.

**The guarded bound.** One stretch's bracket is constant per (B, set)
apart from three decimals: about 1.3 KB at B = 32. The 16-B rung is
smaller (UNMEASURED; the build measures the largest instance and records
it).

V renders at most once per site (§3.2), so one site's bracket is one
stretch's text. That makes it constant apart from the decimals in LO and
K, and so it is a fixed bound, not a cap with a decline path.
`guarded_max` is the largest instance plus a small headroom, CHOSEN and
labelled so. It gets a row `span-vector-w32` in
`tests/memfn/simd_bounds.tsv`, and a `limits.md` §8.3¶3 sentence names
it.

## 6. MEASUREMENT-3: how the shipped text is matched to the timed text

The reviews' premise: "rxs_span always_inline + immintrin.h IS the text the
kit would ship". The build closes it in two steps. The first needs no timing.
(Rev 1 under R-4: the committed spike708 fixture set was cut. F2
compares machine code, which is stricter and needs nothing committed.)

| step | how | what it closes |
|---|---|---|
| **F2, machine-code fidelity** (a delivery check, run once by the build lane and recorded in its report; not a committed test) | for each of 710's 130 patterns, `objdump -d` of `rxa_search`, addresses normalized: the shipped `-fmemfn-simd=x86-64-v3` artifact at width 4095 against 710's arm source (`work/src/<pat>.avx2-loop.c`, or `.H64` where the table picked H64), same gcc and flags. IDENTICAL is the expectation. Each DIFFERS is listed with its diff | the inlined machine code is what was timed. **Probe evidence:** the selector shape adds one more inline level. Dropping the harness's `rxs_span` wrapper changed one `cmp`'s operand order on dig24 and num64. Keeping a two-argument `(s, c)` entry, as §4.1/§5 do, is the timed shape |
| **F3, timing** | card C6 (§8) times the SHIPPED compile (default vs `no-span-vector`, both from one binary) | anything F2 cannot see: layout, I-cache, the wrapper at SIMD-off |

If F2 shows a residual DIFFERS on routed cells, the build lane lists them.
C6 gives them their own population line, so a gap is visible and measured,
never inherited from 710.

## 7. The deny row

Proposal for the build lane to take:

```
MF_OPT("span-vector", MF_OPT_DENY, MF_B_ANY, MF_L_SCALAR,
       "long window spans of one byte set are tested by a function that, under -fmemfn-simd at a "
       "target with 32-byte vectors, tests 32 (or 16) bytes per step; denied, the span is tested "
       "inline as before, at every setting")
```

- **The name.** It says what the caller sees (D174): a span tested by
  vector. The `span-` prefix groups it with `span-loop`.
- **The layer is `scalar`** on purpose, under option A. The deny is LIVE
  at both settings (manager 2026-11-21, `wrap-deny` RESOLVED): it un-wraps
  the stretch too, so `--memfn=no-span-vector` restores main's bytes
  exactly at every layer and target. That gives G1's SIMD-off reading a
  population (G-4), and gives the wrapper an escape hatch, since it can
  move machine code (§2).
- **Off by default** follows from `-fmemfn-simd` being OFF by default: the
  vector helper renders only at a `w32` target.
- **Spec:** `registry.md` §6¶8a gains the row. §6¶8b's `memfn` section
  floor goes from 14 to 15.

## 8. The measurement card (same change; Frank 2026-10-23)

**Card C6 `span_vector`** in `memfn/tests/span_forms/cards.py`, and the
append-only row `kit span_vector 8 form;pat;regime;layer ratio cards.py C6
...` in `memfn/data/cards/kit-grid.tsv` (`kit-grid@8`). The row is visibly
UNMEASURED until a box runs it.

- **Arms.** On ONE binary, at `-fmemfn-simd=x86-64-v3`: `V` (default) and
  `H64@on` (`--memfn=no-span-vector`). The layer-off wrapper arms of rev 1
  moved to §14 U2b (rev 2, R-4: one timing of the wrapper, not two).
- **Patterns.** Each table bound, from both sides:
  - the four routed census patterns (§0.1);
  - window k ∈ {15, 16, 31, 32, 1000, 1001};
  - scan k ∈ {23, 24, 64, 65};
  - plus every F2 DIFFERS pattern.

  710 already timed the interior. The card re-times the shipped text at
  the bounds and on the real population, and adds nothing beyond that
  (R-4).
- **Regimes and rule.** The cards' six regimes, plus near-miss-in at the
  window sites, under 710's rule unchanged (floor, re-time, control). The
  rule sha is recorded.
- **`deps`.** `kit:form.span-vector=<hash>`: a new `formhash.c` ENTRY, the
  canonical instance `[0-9a-f]{41}` at x86-64-v3, so a later text change
  stales the row.


**What it settles.** G-3 on the shipped text. The SIMD-off wrapper's cost
is NOT read here: rev 2 moves it to the scalar no-loss check (§14 U2b), so
it is timed once. A Zen 1 run of C6 (ubuntubudu: AVX2 split into 2x128) is
the D144 addendum 4 reading on other hardware; it is unmeasured and may
move the lower bounds.

## 9. The same-commit abi package (D76/D94, D146/D147)

### 9.1 The bump

"The next number at landing" (`docs/design/CLAUDE.md`): main is at **109**
today (§16 item 1). Lane L3 (`2026-11-20-r65-l3feat`) is taking
109 → 110, so this build is likely **111**. The build lane re-greps at its
landing base.

### 9.2 The re-pins, readers found by grep at the landing base

The command:

`git grep -n -w <N> -- src tests docs/spec docs/testing.md memfn` (abi lines)

At 109 today the readers are:
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
- `docs/spec/match_api.md` §1's K80 guard, its three lines (`!= N`, the
  `#error` text, `#define PCREC_RX_ABI_H N`);
- `match_api.md` §6's `abi` table row;
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT`;
- `tests/mech/sabotages/S693_abi_not_bumped.sh` `SAB_BEFORE`, re-aimed;
- `tests/codegen/run_recursion_identity.sh` FILEPIN/ABASEPIN, the (B) pin,
  self-pinned to the lane's last src commit (the r65 CONTRACT-1 lesson);
- `docs/dev/history/abi_changelog.md`.

Then run the suites that count: registry, codegen, rxtsource
(the D94 addendum).

### 9.3 Stamps and pins

- `MEMFN_FORMS` gains the token `span-vector@w32` (opaque to pcrec).
- `SIMD_GUARDED_BYTES` rises on SIMD-on movers.
- `simd_bounds.tsv` gains a row.
- `emit_sweep.py`'s `DIFFER_PINS` gains floors for the deny arm at both
  layers.
- The start-set and size tripwires move only if a corpus artifact's size
  moves. The wrapper adds bytes at SIMD-off, so `make test` is owed in
  full, not just one section (BOILERPLATE's delivery bar).

`MF_SITE_ABI`: unchanged, since the site carries no new field.
`MF_CLASS_V`: unchanged, since the plan class's `includes` already carries
a level header bit. The build confirms the plan class's reader accepts a
level include on a window site.

### 9.4 G1 alpha, at both layers (integration.md §17.2)

- **Population.** pcrec-side: a script diffs each artifact's default
  compile against its `--memfn=no-span-vector` compile, over the corpus
  and the bench patterns, at `-fno-memfn-simd` AND at `-fmemfn-simd`. It
  never reads the kit's `moved`. The manifest is written before any
  timing, with its count.
- **Bins** (op, length decade), floor 8, under the declared regime.
- **Timing** is owed to main's Frank-cleared window, not the build lane.
  The build delivers the population and the dry run.

### 9.5 The spec hunk, the same change (D80)

| file and section | change |
|---|---|
| `registry.md` §6¶8a, ¶8b | the row; the floor |
| `tuning.md` §2.43¶3a | "What On renders" gains the vector span |
| `tuning.md` §2.43¶3b | its switch |
| `tuning.md` §2.43¶3d | the window search's denies: the wrapper at both settings, under A |
| `limits.md` §8.3¶3 | the per-form bound |
| `match_api.md` §6 | through the abi ritual |

`docs/guide/` points at the spec and does not restate it.

## 10. G2 and the checks (each control independent of the generator)

| check | subject | control (shares no source with the kit) | population count (K35) |
|---|---|---|---|
| **G2-V unit** (new section of `run_g2_win.sh`, x86-64-v3 arts) | every V rendering over a generated space: sets of 1..8 ranges in both polarities, sets with bytes ≥ 0x80, the empty set, a 255-member set, single-byte-removed sets; k at every rung edge (16, 17, 31, 32, 33, 63, 64, 65, 999, 1000) and random interior k | python: `all(re.fullmatch(cls, bytes([b])) for b in window)` with the class written in the TEST, never the kit's set. Windows flush against a `PROT_NONE` page at both ends (708's `check_tu`), so a read past p + K or below p faults | per rung, per row: literal floors |
| **G2-V whole** | `cls{k+1}` and mixed patterns (a literal run plus a stretch, two stretches, a stretch beside a non-core position) compiled at SIMD-on and SIMD-off, find-all | python `re` over the cards' regimes, plus forced near-miss staircases (a failing index at each of 0..k-1, at the first window and after a match: 710's FIDELITY-1) | per site kind: literal floors |
| **T-table pins** | the row bounds | a literal flip list in the test, (HORS 15/16, 1000/1001; WALK 23/24, 64/65), read off the rendered text (the `__w32` call present or absent), never off window.c | 8 flip cells, every one reached |
| **Identity gate** (G-4) | `--memfn=no-span-vector` artifact vs main's binary's artifact | byte diff, both layers, the corpus | count printed; 0 expected |
| **C18 / simdfloor** | unchanged; it now meets `vs<j>` selectors | its own rule (C18 (c)) | its per-target SIMD FUNC floor rises: the build re-pins it |
| **F2** (delivery check) | §6 | 710's arm sources | 130 patterns |

**Sabotage rows** (mech, each with a REACH witness, [MECH-REACH]):

| plant | what it breaks | caught by |
|---|---|---|
| (a) | a nibble table drops a member (708 `nib_drop`) | G2-V unit |
| (b) | the final block reads 1 B past (708 `past`) | the guard page |
| (c) | T-vwin's lower bound becomes 15 | T-table pins |
| (d) | the deny is ignored at SIMD-off | identity gate |

Rev 1 under R-4 cuts two plants. C18's own controls already plant a level
leak, and G2-V whole already covers a `__body` that drops a test.

`REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` runs before delivery,
since a new row fires in new places (BOILERPLATE).

## 11. Expected movers (which sites' bytes change)

| setting | moves | does not move |
|---|---|---|
| every artifact | the abi number lines | — |
| `-fno-memfn-simd` (the default build), default width | artifacts whose window site is E-find HORS with a one-class stretch of 16..31 positions, or E-find WALK with a stretch of 24..31 (e.g. `[0-9a-f]{17}`..`{32}`, `\w{17}`..`{32}`, `[^\n]{17}`.., `[0-9]{25}`..`{32}`, `[A-Z]{25}`..`{32}`). The walk calls `vs<j>`; file scope gains `__body` and the selector | `[0-9a-f]{16}` (k 15), `[0-9]{24}` (k 23), any 33+ position pattern (no window site at the default width), LIBC/PAIR finds (`a[0-9a-f]{20}`), floor and legacy sites, every VM/DFA body text |
| `-fmemfn-simd=x86-64-v3` | the same artifacts, plus the bracketed `__w32` helpers, the selector's replaced call, `<immintrin.h>` ahead of the region, `MEMFN_FORMS` `span-vector@w32`, `SIMD_GUARDED_BYTES` | as above |
| `-fmemfn-simd=x86-64` (w16 only), `generic` | as `-fno-memfn-simd` (wrapper, no helper) | — |
| `--window-search-width=W` > 32 | HORS with 16 ≤ k ≤ min(1000, W - 1); WALK with 24 ≤ k ≤ 64 | k > 1000 (HORS), k > 64 (WALK): H64 |
| `--memfn=no-span-vector` | nothing: main's bytes, every setting | — |

The corpus counts are OWED to the build lane's G1 population script. This
lane runs no sweep (§16).

## 12. Constants register (Frank: unroll widths, block sizes, cut-overs are suspect)

| constant | label | source |
|---|---|---|
| 16, 1000 (HORS); 24, 64 (WALK) | MEASURED | 710, rule `6351bff3901e3955` |
| 64 (H's head) | MEASURED | cards run fcards-zen4-1, unchanged |
| B ∈ {32, 16} | DERIVED: the level's vector width and its half; the largest that fits in k, so no read leaves the span | §4.2 |
| the loop shape (not unrolled) | MEASURED as a form: 710 timed `loop`. 708's `unr` and `loop2` were other arms, not shipped | 708/710 |
| `guarded_max` (`span-vector-w32`) | CHOSEN, UNMEASURED DEFAULT, a cap by construction | §5 |
| `SWAR_MAX_RANGES` | not shipped (no row reaches SWAR) | §4.4 |

## 13. The three standing questions

1. **The measurement regime (RELEVANT).**
   - **710's regime:** Zen 4 7700X (the dev box), gcc 15.2, glibc, CPU 15
     pinned with a quiet sample, throughput (ns/B, find-all, 1 MiB
     subjects), six regimes plus near-miss-in, x86-64-v3,
     `--window-search-width=4095`, fresh layout pools, A/A 6/448.
   - **What could flip a row:**
     - Zen 1 (2x128 AVX2) could raise the k at which V wins, near the
       lower bounds;
     - another compiler (clang: unmeasured, its region is a different
       pragma);
     - a latency regime (one short call) is not what 710 timed: its
       not-warm and short-subject regimes are the cards' approximations,
       void by method.
   - The default width is not a regime change: the text is identical
     (§3.2).
   - The official verdict is the planned bench run on the targeted
     hardware, via main (D144 addendum 4).
2. **The independent control (RELEVANT).** §10:
   - the answers are checked against python `re` and python per-byte
     membership, never the kit's set;
   - the row bounds against a literal flip list, read from the text;
   - the population comes from pcrec's diff (default vs deny), never
     `moved`;
   - fidelity against a different generator (spike708) and 710's own arm
     sources;
   - every sabotage plant has a reach witness.
3. **What moves when the data is regenerated (RELEVANT).**
   - The table's bounds are constants in window.c, not a data file. A
     re-measure that moves them (a C6 run on other hardware, a re-run of
     710's rule) moves emitted bytes. That is a kit byte move, so it is a
     pcrec abi event plus a spec check (the registry row's doc names no
     bound, so it stays).
   - `kit-grid@8` is append-only.
   - The `span-vector` form hash moves with any change to §4.1's text,
     staling the C6 row.
   - No calibration or measure-set row prices V. It is a rule row, not a
     priced choice.

## 14. The build units, in order

| unit | what it does | moves bytes? |
|---|---|---|
| **U1** | The table refactor: `wf_span_head` becomes THE SPAN FORM TABLE (T-deny, T-force, T-lever, T-head), evaluated per stretch; `w->head` retired. An identity gate: every corpus artifact byte-identical to main at both layers, both engines. A refactor gets no flag (Frank 2026-10-29) | no |
| **U2** | The wrapper (option A): `vs<j>` + `__body` + selector for eligible stretches at every layer, and the deny row `span-vector` (both layers). The identity gate against main for the deny arm. The first abi event lands here | yes |
| **U2b** | **The scalar no-loss check, before landing** (§2.1): (a) the non-timing census of sites whose SIMD-off `rxa_search` machine code differs, wrapped against today's; (b) a short SCALAR timing of only those sites, in a window Frank clears; (c) any loser is kept on today's text by row T-keep. Costs nothing where (a) finds zero sites | no (decides T-keep's contents) |
| **U3** | The `w32` helper: §4.1's text bracketed, the selector's replaced call, the `includes` fact, the form token, the guarded bound and `simd_bounds.tsv`, the `limits.md`/`tuning.md`/`registry.md` hunks. F2 recorded before anything else | yes (SIMD-on) |
| **U4** | G2-V (unit, whole), T-table pins, sabotage rows (a)-(d) with reach, simdfloor re-pin, `DIFFER_PINS` floors | no |
| **U5** | Card C6 + `kit-grid@8` + the formhash entry; `cards.py plan`/`dry` green, with no timing | no |
| **U6** | The abi package at the landing base (§9.2), `make test` async, `make test-axes`, REACH_ONLY. Then G1's population dry run, and the C6 and G1 timing owed to main's window | — |

The design round (critics) precedes U1. The code round precedes the
landing (Frank 2026-11-15). U2 and U3 may share one abi event if they land
together; the number is taken once.

## 15. Open questions

All four rev 1 questions are RESOLVED.

1. **`scalar-wrap`: RESOLVED, option A with a scalar no-loss check
   (Frank 2026-11-21; manager's reading, which Frank was told).** Frank's
   words: "Scalar wrap: the function goes inline so it's just code
   organization? If that's true I don't have a problem with that." See §2
   and §14 U2b.
2. **`scan-scope`: RESOLVED, WALK only, not LIBC/PAIR (manager
   2026-11-21).** Nothing else was measured (D77). Widen when a C6 cell
   measures a memchr scan with a long stretch.
3. **`wrap-deny`: RESOLVED, `span-vector` is LIVE at both layers
   (manager 2026-11-21).** It un-wraps the stretch, so
   `--memfn=no-span-vector` restores main's bytes everywhere; it is the
   wrapper's only control and population.
4. **`ship-size`: RESOLVED into §17** (information for the critic round).

Open, owed to main: the cover-width timing (`cover_cap.md` §11.4 B) decides
whether the default window width (32) rises, which widens the eligible
range from k 16-31 / 24-31 to the 710 table's 16-1000 / 24-64.

## 16. TODAY NUMBERS (each with the command that produced it; 2026-11-21, main 051e78af2)

1. **abi 109.** `git -C /home/pcrec/projects/pcrec grep -n 'define PCREC_ARTIFACT_ABI' main -- src/gen/emit_dfa.c` → `src/gen/emit_dfa.c:55:#define PCREC_ARTIFACT_ABI 109`. Its readers: `git -C /home/pcrec/projects/pcrec grep -n -w 109 main -- src tests docs/spec docs/testing.md memfn/src memfn/tests | grep -i abi` (§9.2 lists them).
2. **`memfn` section floor 14.** `git -C /home/pcrec/projects/pcrec grep -n 'memfn. section floor' main -- docs/spec/registry.md` → `[6¶8b] ... floor: 14`.
3. **Head 64, the if chain.** `grep -n WF_SPAN_HEAD memfn/src/window.c` → 1470 (`enum { WF_SPAN_HEAD = 64 }`), 1476, 1483. The chain is `wf_span_head`, window.c:1477-1484.
4. **Levels.** `grep -n '^MF_LEVEL' memfn/src/levels.def` → `LV_X86_W16` (sse2, x86-64) and `LV_X86_W32` (avx2, x86-64-v3); no others.
5. **Site kind and positions at the default width** (lane build of this branch, SIMD on). The command: `for cls in '[0-9a-f]' '[0-9]' '\w' '[^\n]'; do for n in 9 16 17 24 25 32 33 34 40 65 66; do build/pcrec -p rxa --features all -fmemfn-simd=x86-64-v3 -o - --pattern "$cls{$n}"` | classify by `rxa_mf1_sh[` (HORS) / `rxa_mf1_c = rxa_mf1_lo` (a window site) and count distinct `rxa_mf1_s[rxa_mf1_c + N]`. Results:
   - every class has a window site up to n = 32 and none from n = 33;
   - `[0-9a-f]`, `\w` and `[^\n]` are HORS; `[0-9]` is WALK;
   - the positions tested = n.

   The width identity: `[0-9a-f]{17}` and `[0-9]{25}` have byte-identical walk lines at the default width and at `--window-search-width=4095` (a `diff` of their `rxa_mf1` lines).
6. **Machine-code probes** (gcc 15.2.0, -O2, `objdump -d` of `rxa_search`, addresses normalized; scripts and outputs in `$PCREC_TMPDIR/scratch/bspan/`):
   - **(a)** On 710's timed `avx2-loop` sources, with the `target()` attributes dropped: IDENTICAL on 6/6 (hex16, hex40, hex1000, dig24, num64, word500). With the harness's `rxs_span` wrapper also removed (a direct call): hex16, hex40, hex1000 and word500 are IDENTICAL; dig24 and num64 differ in one `cmp` operand order.
   - **(b)** `wrapprobe.py` (today's text against the span as an `always_inline` function: option A's `__body`). At the default width, OFF and ON alike, 8 of 10 are IDENTICAL; `\w{20}` and `\w{32}` DIFFER (97 lines). At width 4095, OFF and ON alike, 6 of 8 are IDENTICAL; `[+.0-9]{65}` differs by 440 lines and `\w{501}` by 1 line.
7. **Job 710's verdict** (`$PCREC_TMPDIR/scratch/memfn/blockconfirm/run-20261120T212920/decision.md`): CONFIRMED.
   - Cells: 840 cells, 112 N/A.
   - The claim: the verdict population is 144, with 127 WIN, 17 TIE and 0 LOSS. Over all counted cells: 295 W, 427 T, 0 L.
   - Per row: row 1 is 255/140/0 (W/T/L) and row 2 is 40/37/0.
   - Replication: 104 of 115.
   - The A/A line: 6/448 repeated.
   - The Hspk control: 9 WIN and 2 LOSS standing (the two LOSSes are hi k=8, a cell no table row routes).
8. **The C18 rule (c).** The docstring of `tests/memfn/simd_floor_check.py`: one `return <fn>__body(...)` replaced per SIMD FUNC. The bracket's whole-line rule: `src/core/sb.c` `pcrec_sb_simd_open` / `_close`.

## 17. SHIP-SIZE (R-4's lens, for the critic round; information, not a ruling)

What the build adds, under option A with the scalar no-loss check. Counts
marked UNMEASURED are estimates the build lane replaces with `git diff
--stat` at its landing; nothing here was built.

| surface | added |
|---|---|
| table | 3 rows (T-vwin, T-vscan, T-keep) plus the 4 H/I/L rows reshaped from the if chain; `wf_span_head` and `w->head` retire |
| code, `memfn/src` | the block-text renderer (§4.1, two widths), the selector/`__body` writer, the per-stretch table evaluation: UNMEASURED, expected a few hundred lines in `window.c` (and a `window.h` fact), no new file |
| emitted text per site | scalar layer (every layer): the `vs<j>` selector and `__body` (one `return` each, about 0.4 KB, UNMEASURED). SIMD layer (`w32`): the bracket, about 1.3 KB at B = 32 (§5), less at B = 16 (UNMEASURED) |
| deny | 1 row (`span-vector`), live at both layers; 1 `registry.md` row, floor 14 to 15 |
| card | 1 (C6), 1 `kit-grid@8` row, 1 formhash entry. Rev 2 moves the scalar-wrapper arms out of C6 into the scalar no-loss check (§14 U2b), so they are timed once |
| checks | 1 G2 unit section, 1 G2 whole section, 8 flip cells, 1 identity gate, 4 sabotage rows; F2 and the U2b census are delivery steps, not committed tests |
| spec | `registry.md` §6¶8a/8b, `tuning.md` §2.43¶3a/3b/3d, `limits.md` §8.3¶3, `match_api.md` §6 (abi): 6 hunks |
| abi | 1 event (the number taken at landing, §9.1) |

Against the population: 4 (text, options) pairs route today (§0.1), by
information only (D201 add. 1: "We're here and there's no downside so
let's build it."). At the default window width only k 16-31 (window) and
24-31 (scan) is eligible, so the 4 are all the default build can show.

**Rev 2's check of rev 1 against R-4 (smallest form that serves the 710
table).** Cut: C6's size-record bullet (nothing in the table reads it) and
C6's scalar-wrapper arms (they move to U2b, which the ruling adds). Kept
because the 710 table needs them: both bounds from both sides, the
deny, the one-stretch-per-site rule, the 32 and 16 rungs only, no SWAR,
no unrolled form, no knob beyond the deny row. The one NEW surface this
revision adds is U2b plus T-keep, both required by the scalar-wrap ruling;
where U2b's census finds zero differing sites, T-keep is not built.
