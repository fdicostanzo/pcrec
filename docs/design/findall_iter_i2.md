# [FINDALL-NEXT] I2 — `<prefix>_next_n` and the generic `RX_FOREACH` (DESIGN NOTE, revision 1)

Lane `i2design` (opus), 2026-10-21, branch `lane/i2design` from `lane/i1build` at
`e0139d8c6` (I1 built, abi 83, NOT merged). DESIGN ONLY: nothing under `src/`, `cli/`,
`lib/` or `tests/` changes, and nothing was measured. Every number below is copied from a
named record. The panel is the next step. The manager launches it.

**Inputs this designs TO, not re-opens:** D165 (items 1-6, addenda 1-4), D171 (Frank,
2026-10-21: ~2 ns setup accepted; the batch cell is `off`; `next_n` noted for I2), the I1
build (`findall_iter.md` §12, `docs/spec/match_api.md` §3.8, `src/gen/emit_iter.c` on
`lane/i1build`), the manager's I1 ruling (no batch ABI in I1), Frank's charter for I2 (the
manager's record, `docs/dev/wake.md`, 2026-10-21: "`next_n` + a generic
`RX_FOREACH(info, ...)` over `info->next_n`, with a doubling buffer 4 → 64"; "the generic
macro usable without the .h"), Frank 2026-10-21 "build what is needed and not theoretical
needs", and Frank's I2 go for design → critic → build.

**Why a separate note, not revision 4 of `findall_iter.md`.** The house pattern for that
note is in-place revisions with a §R table per revision, plus §12 as the I1 build's
addendum. I2 is a later STAGE with its own abi event, and it needs only a small part of the
1,769-line note: §2.1 (STEP), §3 (semantics), §5.3 (the parity harness) and §6.8 (the
sabotage labels). A revision 4 would have to rewrite §2.3, §3.4a, §5.3, §6.9, §8 and §9
around a withdrawal (§1 below) and would bury I2's design in that rewrite. So this note is
the delta. `findall_iter.md` §12 gets a one-paragraph pointer that names what this note
supersedes (§1.2), and nothing else in it changes.

---

## 0. Answers first

1. **`size_t <prefix>_next_n(rx_iter *it, ptrdiff_t (*caps)[2], size_t k)`** writes up to
   `k` matches, each `<PREFIX>_NCAPS` pairs (entry `i` at `caps + i * NCAPS`). It returns
   the count. **A return below `k` means the iterator has ended**, and `it.rc` says why
   (0 done, < 0 the code), exactly as after `_next` returned 0. `k == 0` returns 0 and does
   nothing, so the rule holds there too. `next_n(it, caps, k)` is, by construction, `k`
   calls of `next`. The two interleave freely on one iterator (§2).
2. **No `rx_iter` change.** Every fact carried across calls (`lo`, the retry bit, `rc`, the
   ENDED state) is already in I1's struct. `PCREC_ITER_LAYOUT` stays 3, and `sizeof(rx_iter)`
   stays 72 B on LP64.
3. **The internal batch is withdrawn, not deferred** (§1.2): `rx_iter_batch`,
   `PCREC_ITER_OPT_BATCH`, `rc_next`, `bhead`/`bcount`, `__fill`/`__deliver`, the `iterate`
   row's `batch` column. D171 measured it slower than `I` on every dense subcell, and
   `next_n` batches on the caller's side, where the twin measured a gain. §12's "I2 appends
   at layout 4" list shrinks to the kit's `st`, which keeps revision 3's rule (it lands with
   the first held row) and becomes its own stage (§7).
4. **ABI placement.** The shared block gains `rx_nextnfn`, `rx_foreach` (the macro's state),
   `rx_foreach_begin`, `rx_foreach_pull`, `RX_FOREACH` and `RX_FOREACH_PAIRS`. `struct
   rx_info` APPENDS `next_n` after `next`. Per artifact: the exported `<prefix>_next_n`, its
   header declaration, and `.next_n` in `<prefix>_info`. One abi event, the next number
   after main's at merge (83 + 1 = 84 if nothing else lands first). Its readers are found by
   grep (D76/D94, §6).
5. **`RX_FOREACH(info, it, m)`** iterates through `info->next_n` with a stack buffer whose
   batch size doubles 4, 8, 16, 32, 64 (capped by the buffer). It needs only the shared
   block (any abi-matching pcrec header), never the artifact's own `.h`. It never allocates.
   Its automatic storage is one `rx_foreach`: `RX_FOREACH_PAIRS` (256) pairs plus 72 B, which
   is 4,168 B on LP64 (computed from the layout, not measured). `break`, `continue` and `return` in the body behave as in a plain loop
   (§3).
6. **One body.** `_next` and `_next_n` are two thin exported controllers over ONE static
   `always_inline` `<p>__pull(it, caps, k)`. `_next` passes the constant 1, and gcc folds
   the loop away. The `iterate` row gains a sibling row, not a new mechanism (§8).
7. **Checked** (§5): new arms in `tests/findall/iter_drv.c` (`next_n` at k = 1, 2, 3, 64,
   interleaved, `RX_FOREACH`, early `break`, k = 0, call counts, exact-size ASan buffers),
   all held to libpcre2's global loop (`G`) through `I`. The iterator arms owed after I1
   go into the three in-tree drivers. Ten sabotage rows are PROPOSED as S1309-S1318, free
   inside I1's range S1297-S1330 (§5.4).
8. **Measured** (§4): the parity harness's post-build mode gains arms `I_info`, `N4`, `N64`
   and `F`. The cell is NAMED here, not run. Its gate: `F / I ≤ 1 + floor` on the dense
   cells (c1, c3, c4) in both regimes, plus "the I1 entry unharmed" (`I` at I2 against `I`
   at I1).

---

## 1. What I2 is, and what it replaces

### 1.1 The measurement that motivates it

From the parity slot (`docs/dev/lanes/parity_report.md`, "RESULT (parread)", job
`150-parity-slot`, 2026-10-21; regime in §9.1). The twin stands in for `I` and `N64`:

| cell | regime | `I`/`L_old` | `N64`/`L_old` | `N64`/`I` (derived) |
|---|---|---|---|---|
| c1-4k (`a`, a×4 KiB) | R1 | 0.9384 | 0.9379 | 1.00 |
| c1-4k | R2 | 0.9592 | 0.9420 | 0.98 |
| c3-4k (`\w+`, prose) | R1 | 0.9912 | 0.8354 | 0.84 |
| **c3-4k** | **R2 (PLT)** | **0.7785** | **0.5761** | **0.74** |
| c3-1m | R1 | 1.0082 | 0.9624 | 0.95 |
| c3-1m | R2 | 0.9189 | 0.8198 | 0.89 |
| c4 (`(a)`, VM) | R1 / R2 | 0.9837 / 0.9679 | 0.9789 / 0.9691 | 1.00 / 1.00 |
| c6 (`^a\|b` DFA attempt) | R1 / R2 | 1.1163 / 1.0064 | **2.1802 / 1.6665** | **1.95 / 1.66** |
| c7 (stop after 3) | R1 / R2 | 1.1666 / 1.1423 | **26.4563 / 25.8778** | 22.7 / 22.7 |

The brief's "0.58x on prose via the PLT" is c3-4k R2, `N64/L_old` = 0.5761. Against the
iterator itself it is 0.74. D171's reading stands: `B64` (the internal cache) lost on every
dense subcell while keeping one exported call per match, so **the gain comes from removing
calls, not from caching**. Three facts constrain the design:
- **c7: a fixed k = 64 is a 26x loss for a caller who stops early.** The doubling start of
  4 answers it: a caller who stops after 3 has paid for one extra search (§3.4).
- **c6: `N64` loses 1.66-1.95x to `I` on the attempt route's shared static-label body.** It
  is UNEXPLAINED in the record. The twin's `N64` ran `__find` from a second exported
  function, and on this route `__find` is `noinline`. A guess, not a finding: the twin's
  `_next_n` compiled the static body at a different layout. I2's `next_n` and `next` share
  ONE `__pull`, so the built artifact cannot repeat the twin's two-copy shape. Cell c6 is in
  the I2 timing cell's gate list, so the guess is tested rather than assumed (§4). The panel
  should attack this.
- **c1 and c4: no gain.** Batching is neutral where each match costs little relative to a
  call or where the VM's per-step binding dominates. The macro must not LOSE there. That is
  the gate (§4).

### 1.2 What is withdrawn (the simplification)

D165 addendum 2 Q2 (Frank, 2026-10-14) ruled batching "an internal thing ... caching the
results internally ... then providing them with next calls". Revision 3 §2.3 designed it, and
the parity slot measured it: `off`, with `B64/I` from 1.07 to 1.29 on all ten dense
subcells. D171 records Frank's later idea of a caller-side macro over a local buffer as "that
shape". `RX_FOREACH` keeps addendum 2's intent: the caller writes one loop, and the batching
is hidden in the macro. It moves the cache from the iterator into the caller's stack frame.
That is where the measured gain is, because the cost removed is the call.

Withdrawn, never built (I1 shipped none of it):

| withdrawn | where it was designed | why it can go |
|---|---|---|
| `rx_iter_batch` setter, `PCREC_ITER_OPT_BATCH` (0x80), fields `batch`, `nbatch`, `bhead`, `bcount`, `rc_next` | rev 3 §1.1, §2.3; §12 "I2 appends" | `next_n`'s return count carries "the matches found before the code", so no code waits in the struct |
| `__fill`, `__deliver`, the IT2 drained-batch test | rev 3 §2.3 | `next_n` is a loop of STEPs that writes straight into the caller's entries. Nothing is buffered across calls |
| the `iterate` row's `batch` column (`fill` / `off`) and the "batch cell flip" stage | rev 3 §6.9, U1 | no second delivery path exists to select |
| §3.4a "batching is answer- and give-up-identical BY CONSTRUCTION, IF ..." | rev 3 §3.4a | `next_n` IS `k` STEPs. Identity holds with no condition (D165 add. 4 made each STEP its own meter) |
| sabotage labels S1009, S1013 (as a batch-region row), S1016, S1038 | rev 3 §6.8 | their sites are not built. S1013's stride question and S1016's exact-size question re-aim at `next_n` (§5.4) |
| the `B64` and `I_fill` parity arms | rev 3 §5.3 | nothing left to time |

What stays: the iterator's whole I1 contract (§3.8 of the spec), Q-I4 (full captures per
entry, ruled 2026-10-16), and D165 add. 4 (one meter per logical search).

---

## 2. `<prefix>_next_n`

### 2.1 Signature and contract

```c
typedef size_t (*rx_nextnfn)(struct rx_iter *it, ptrdiff_t (*caps)[2], size_t k);  /* shared block */
size_t <prefix>_next_n(rx_iter *it, ptrdiff_t (*caps)[2], size_t k);                /* header */
```

- **Entries.** Match `i` (0-based within the call) is written to `caps[i * NCAPS ..
  i * NCAPS + NCAPS)`, as `<prefix>_search` writes `caps`. The caller provides
  `k * <PREFIX>_NCAPS` pairs. A generic caller uses `rx_info.ncaps`, which the spec
  guarantees equal to `<PREFIX>_NCAPS` (§6 row 4). `caps` may be NULL: the call then counts
  up to `k` matches and writes nothing, as `_next` with NULL does.
- **Return.** The number of matches written, `0..k`. **`r < k` ⇔ the iterator ended during
  this call** (or before it). `it.rc` is then 0 or the code, and `it.lo` is defined as §3.8¶9
  says. `r == k` ⇔ the iterator is still live. A next call continues after the k-th match.
- **Equivalence (the design's one invariant).** For every `k ≥ 1`, `next_n(it, c, k)` leaves
  `*it` and the entries exactly as `k` successive `next(it, c_i)` calls would, stopping at
  the first `next` that returns 0. Calls of the two may be mixed on one iterator. Every
  §3.8 rule (FRESH/BOUND/ENDED, the setters, stickiness, what must not change, copies,
  concurrency) applies unchanged. The STATE between calls is the same five fields `next`
  already carries (`hdr`, `rc`, `flags`, `lo`, the bindings).

### 2.2 The edges

| edge | behaviour | why |
|---|---|---|
| `k == 0` | returns 0, touches nothing: a FRESH iterator stays FRESH (its setters still work), an invalid header is not refused, no search runs | the `r < k` ⇔ ended rule holds vacuously (0 < 0 is false), so a 0 here never reads as "ended" |
| caller's buffer full mid-subject | returns `k`, BOUND, `lo`/`flags` as after the k-th `next` | §2.1's invariant |
| the k-th match is EMPTY at `q < n` | `flags = PCREC_ITER_F_RETRY`, `lo = q`. The NEXT call (either entry) starts with the anchored NOTEMPTY retry at `q` | the retry bit is iterator state (I1 `__step`), not call state. The arm in §5.1 splits a batch at every position (k = 1, 2, 3), so a split falls between an empty match and its retry on every retry cell, and the driver counts those splits (a floor) |
| non-empty match ending at `e` | `lo = __next_pos(s, n, e − 1)`, the K75 aligned end, inside STEP | unchanged. S1300's witness cells (`a\x80a`, `\xc3\xa9\x80a`) run through the new arms too |
| a give-up or refusal after `j` matches | returns `j` (< k), entries `0..j−1` written, `rc` = the code, ENDED, `lo` = the start of the search that gave up | `_next`'s end path, once. No pending code: `j` < `k` already says "and then it ended" |
| done after `j` matches | returns `j` (< k), `rc = 0` | as `_next` |
| ENDED on entry | returns 0, `rc` untouched (§3.8¶7) | `__enter` on ENDED |
| FRESH / invalid header | bind (or refuse with `PCREC_ERR_ITER`) on the first call with `k ≥ 1` | `__enter`, unchanged |
| bind-time refusal (startpos, `-futf-check`) | returns 0, `rc` = that code | unchanged |
| the VM's tiered storage | each STEP runs through `__step_own` (fast tier, deep re-run on a FRAMES give-up) or the bound buffers, per match, as `_next` does | one body (§2.3). Binding the run state once per call is an UNLOCK (§9) |
| `k * NCAPS` overflows `size_t` | the caller's buffer cannot exist; UNDEFINED like any wrong buffer size | no check (D165 add. 3) |

### 2.3 The emission: one body, two controllers

`pcrec_emit_iterate` (src/gen/emit_iter.c) changes from "emit `_next`" to "emit `__pull`,
then `_next` and `_next_n` over it". The STEP dispatch that I1 writes inline in `_next` (the
`it->bufs` branch on the VM, `__step` on the DFA) moves into `__pull` unchanged:

```c
static inline __attribute__((always_inline)) size_t <p>__pull(rx_iter *it,
                                    ptrdiff_t (*caps)[2], size_t k)
{
    ptrdiff_t local[<P>_NCAPS][2];      /* STEP writes NCAPS pairs whatever caps is */
    size_t i = 0, at = 0;
    int r;
    if (__builtin_expect(it->hdr != PCREC_ITER_BOUND, 0))
        if (!<p>__enter(it)) return 0;  /* bind; or refuse; or ENDED */
    for (;;) {
        ptrdiff_t (*c)[2] = caps ? caps + i * <P>_NCAPS : local;
        r = /* I1's dispatch: __step(it, c, [&run,] &at) or __step_own(it, c, &at) */;
        if (r != 1) break;
        if (++i == k) return i;
    }
    it->lo = at;                        /* the search that ended it */
    it->rc = r;
    it->hdr = PCREC_ITER_ENDED;         /* sticky */
    return i;
}

__attribute__((noclone)) int <p>_next(rx_iter *it, ptrdiff_t (*caps)[2])
{ return (int)<p>__pull(it, caps, 1); }

__attribute__((noclone)) size_t <p>_next_n(rx_iter *it, ptrdiff_t (*caps)[2], size_t k)
{ return k ? <p>__pull(it, caps, k) : 0; }
```

- **`_next` must not get slower.** With `k` the constant 1, `++i == 1` is true after the
  first match, and `i * NCAPS` is 0, so gcc should produce I1's `_next`. That is a
  PREDICTION. Its check is the "`I` unharmed" arm of §4 (`I` at I2 against `I` at I1,
  within the A/A floor). If it fails, the fallback is I1's `_next` text kept verbatim beside
  `__pull`: one more copy of the dispatch, and the cost is stated.
- **No exported entry calls another** (D163 add. 12 / `compound_entries.md` §3.0 I3): both
  are thin over a static part.
- **Linkage** follows `_next`'s: `pcrec_entry_storage(cx, PCREC_ENTRY_NEXT_N)`. Where a
  request keeps the entries static, `rx_info.next_n` still points at it, as `.next` does.
- **`entry_rows[]`** (src/gen/entries.c) gains `PCREC_ENTRY_NEXT_N` rows on `sh_dfa`/`sh_vm`
  with `PCREC_COMB_ITERATE` and the same parts as `NEXT` (§8). `NEXT_N` is emitted exactly
  where `NEXT` is, so `.next_n == NULL` ⇔ `.next == NULL`.
- **Scaffold.** Everything above is inside the scaffold bracket
  (`pcrec_sb_scaffold_open`), as I1's iterator is, so no length decision reads it
  (`findall_iter.md` §6.4). The mover census (`tests/findall/mover_census.py`) expects zero
  counted moves.

---

## 3. `RX_FOREACH` — the generic loop

### 3.1 Use

```c
rx_iter it = RX_ITER_INIT(s, n);          /* setters as usual, while FRESH */
RX_FOREACH(&rx_info, &it, m) {            /* any artifact's rx_info; only the shared block is needed */
    report(m[0][0], m[0][1]);             /* m: ptrdiff_t (*)[2], info->ncaps pairs */
    if (enough) break;
}
if (it.rc < 0) ...                        /* the code that ended it, as after _next */
```

### 3.2 The exact text (shared block, after `rx_iter` and its setters)

```c
#ifndef RX_FOREACH_PAIRS
#define RX_FOREACH_PAIRS 256    /* the macro's buffer, in pairs: 64 entries at NCAPS <= 4 */
#endif
typedef struct rx_foreach {
    rx_nextnfn fn;
    rx_iter   *it;
    ptrdiff_t (*cur)[2];        /* the match being delivered */
    size_t     ncaps, k, kmax, head, count;
    int        brk;             /* 1 while the body runs; left 1 by a break */
    ptrdiff_t  buf[RX_FOREACH_PAIRS][2];   /* last, so an over-run leaves the object */
} rx_foreach;

static inline rx_foreach *rx_foreach_begin(rx_foreach *f, const struct rx_info *info,
                                           rx_iter *it)
{
    size_t nc = 0;
    f->it = it; f->head = f->count = 0; f->brk = 0;
    if (info->abi == PCREC_RX_ABI_H && info->next_n && info->ncaps > 0)  /* Q2 */
        nc = (size_t)info->ncaps;
    f->fn = nc ? info->next_n : (rx_nextnfn)0;
    f->ncaps = nc;
    f->kmax = nc ? RX_FOREACH_PAIRS / nc : 0;
    if (f->kmax > 64) f->kmax = 64;
    f->k = f->kmax < 4 ? f->kmax : 4;
    if (f->k == 0 && it->hdr != PCREC_ITER_ENDED) {    /* refused: Q1, Q2 */
        it->rc = PCREC_ERR_ITER;
        it->hdr = PCREC_ITER_ENDED;
    }
    return f;
}

static inline int rx_foreach_pull(rx_foreach *f)
{
    if (f->head == f->count) {
        size_t k = f->k;
        if (k == 0) return 0;                       /* ended, or refused at begin */
        f->count = f->fn(f->it, f->buf, k);
        f->head = 0;
        if (f->count < k) f->k = 0;                 /* it ended inside this fill */
        else if (k < f->kmax) f->k = 2 * k < f->kmax ? 2 * k : f->kmax;
        if (f->count == 0) return 0;
    }
    f->cur = f->buf + f->head++ * f->ncaps;
    return 1;
}

#define RX_FOREACH(info_, it_, m_)                                                       \
    for (rx_foreach rx_fe_##m_, *rx_fp_##m_ = rx_foreach_begin(&rx_fe_##m_, (info_), (it_)); \
         !rx_fp_##m_->brk && rx_foreach_pull(rx_fp_##m_); )                              \
        for (ptrdiff_t (*m_)[2] = (rx_fp_##m_->brk = 1, rx_fp_##m_->cur);                \
             rx_fp_##m_->brk; rx_fp_##m_->brk = 0)
```

### 3.3 Properties

- **Control flow.** The body runs inside the inner `for` with `brk = 1`. On normal
  completion or `continue`, the inner increment clears `brk`, the inner test fails, and the
  outer test pulls the next match. On `break`, the inner loop exits with `brk` still 1, the
  outer test fails, and the whole loop ends. `return` and `goto` leave both loops. This is
  the standard two-loop idiom. Its witnesses are the `Fstop` arm and S1316 (§5).
- **Each argument is evaluated once** (in `rx_foreach_begin`). `m_` names the match pointer
  and also suffixes the state's names, so nested `RX_FOREACH` loops with distinct `m_`
  names compile. Two consecutive loops with the same `m_` are separate `for` scopes.
- **It never allocates.** `rx_foreach` is one automatic object, 4,168 B on LP64 at the
  default: 256 × 16 B of buffer + 8 words + the `int` and its padding (computed; the build lane measures it with `sizeof`). `begin` writes eight fields
  and never the buffer (no memset). The c2/c5 fixed-cost cells are where a hidden init cost
  would show (§4).
- **Without the artifact's `.h`.** The macro names only shared-block identifiers
  (`struct rx_info`, `rx_iter`, `rx_nextfn`/`rx_nextnfn`, `PCREC_*`). A translation unit
  that includes ANY pcrec header of the same abi can iterate any artifact whose `rx_info`
  it holds. There is no standalone header. A caller holding a record from a library with
  no pcrec header at all is the trigger for `--emit-abi-header` (§9 U-I2-3), not built.
- **Batch sizes.** 4, 8, 16, 32, 64, 64, ... capped at `kmax = min(64, RX_FOREACH_PAIRS /
  ncaps)`. For `M` matches the macro makes about `⌈(M − 60) / 64⌉ + 4` indirect calls once
  `M > 60` (for `M` = 4,096, c1-4k: 68 calls instead of 4,097). The constants are LABELLED
  UNMEASURED DEFAULTS (memory `pcrec-suspect-tuning-constants`): 4 is Frank's start, 64 is
  the only k the twin measured (`N64`), and 256 = 64 × 4 is derived from them so that NCAPS
  ≤ 4 reaches the full k. §4's `N4`/`N64` arms show whether the doubling costs anything on
  the dense cells. None of the three moves an answer.
- **Over-fill bound.** A caller who leaves after `j` matches has paid for fewer than
  `j + 4` searches it never sees. The wasted searches are at most the current batch less
  one, and each batch (4, 8, 16, 32, 64) is no larger than all the batches before it plus
  4. So the total work is at most about twice the delivered work plus 4. c7 (stop after
  3): one extra search, against `N64`'s 61.

### 3.4 The edges

| edge | behaviour |
|---|---|
| the iterator ends (done / give-up / refusal) | the loop ends after the last match; `it.rc` and `it.lo` as after `_next` returned 0 |
| the body `break`s / `return`s early | the iterator stays BOUND, positioned after the last FILLED match. Up to `k − 1` buffered matches are never seen. **The spec states this: an iterator handed to `RX_FOREACH` is finished when the loop exits, however it exits.** Continuing it with `_next` is defined but skips the buffered matches (Q3) |
| `info->next_n == NULL` (an artifact compiled not to define `next`) | refused: `it.rc = PCREC_ERR_ITER`, ENDED, no body run |
| `info->abi != PCREC_RX_ABI_H` | refused the same way (Q2): `abi` is member 1 in every layout, so reading it is safe. `next_n` is not read |
| `info->ncaps > RX_FOREACH_PAIRS` (more than 255 groups at the default) | refused the same way (Q1). The caller raises `RX_FOREACH_PAIRS` before the include, or uses `<prefix>_next`/`_next_n` with its own buffer |
| an already-ENDED iterator | no refusal is written (`rc` stays, §3.8¶7); `next_n` returns 0; no body run |
| the body calls `next`/`next_n` on the same iterator | allowed, but those matches are skipped by the macro's next fill. The spec says "the body does not advance the iterator" |
| two TUs with different `RX_FOREACH_PAIRS` | the type differs per TU. It never crosses a call boundary (only `buf` reaches `next_n`, as a pair pointer), so it is harmless. Stated |

---

## 4. What is measured (named, not run)

**Cell:** the parity harness's post-build mode (`docs/design/findall_iter/twin/parity.sh`,
`PARITY_POST=1`) gains `PARITY_I2=1`, which adds four arms over the BUILT I2 artifact:

| arm | what | its question |
|---|---|---|
| `I` (I2) | `<prefix>_next`, as today | with `I` from the I1 build (`PCREC_OLD` = the I1 compiler): **"`_next` unharmed"**, `I_i2 / I_i1 ≤ 1 + floor` (GATE) |
| `I_info` | `info->next` per match through `&rx_info` (the generic caller with no macro) | the per-call cost through the pointer, REPORTED: `(I_info − F) / matches` on c1-4k (4,096 matches) is that cost in ns per call |
| `N4`, `N64` | `<prefix>_next_n` direct, fixed k | whether doubling costs anything (REPORTED) |
| `F` | `RX_FOREACH(&rx_info, ...)` | **GATE: `F / I ≤ 1 + floor` on c1, c3, c4 and c6, R1 and R2.** c6 is in the gate because the twin's `N64` lost there (§1.1). REPORTED on c2, c5 (fixed cost; D171 accepts ~2 ns) and c7 (predicted ≈ `I` + one search) |

- **The run:** a boxqueue job `6x0-i2build-parity` (owner `i2build`, quiet-gated,
  `boxqueue: idle-ok`, pinned to cpu7, 5 launches, arms interleaved, gcc 15.2 `-O2`, R1
  and R2). It uses the twin harness's verdict script with the floor defined in
  `findall_iter.md` §5.3. The answer gate (G2-G4) runs first on every new arm.
- **A loss is a FINDING with its numbers**, not a tolerance (D165 item 5). A loss on c6
  sends the build lane to compare the `__find` linkage of `_next` and `_next_n`.
- **The PLT per-call cost** is not a separate cell. R2 against R1 on `I` and `F` carries
  it: c3-4k's `L_old` is 4,927 ns in R2 and 3,829 ns in R1, two exported calls per match.

---

## 5. What is checked

### 5.1 `tests/findall/iter_drv.c`: the new arms

Every arm runs on every subject of every group (`cells.tsv`: 62 byte patterns × 18
subjects, 8 utf8 patterns × 11 subjects × 3 flag sets, auto/vm/dfa; plus the ASan cells).
Each arm's span sequence and final `rc` must equal `I`'s. `I` is already held to `G`.

| arm | what it does | catches |
|---|---|---|
| `N1`, `N2`, `N3`, `N64` | `next_n` at fixed k, entries concatenated | the fill loop, the count, the stride (on VM groups with NCAPS > 1, every group's pairs are compared, not only the span) |
| `X` | alternates `next` and `next_n(…, 2)` | the shared state; the retry carried across ENTRY kinds |
| `F` | `RX_FOREACH(&rx_info, &it, m)` | the macro, through the record |
| `Fstop` | `RX_FOREACH` with `break` after j = 1, 3, 5 | exactly j delivered, equal to `I`'s first j |
| `N0` | `next_n(…, 0)` on a FRESH iterator, then `rx_iter_at(&it, p)`, then `I` | k = 0 inert: the setter must still work (the result is `I` from `p`) |
| `Fcount` | `F` over a COPY of `rx_info` whose `next_n` is a counting wrapper | the number of calls equals the doubling formula of §3.3 for that match count (the amortization the macro exists for) |
| `Fabi` | `F` over a copy with `abi + 1` | refused: `rc == PCREC_ERR_ITER`, no body run (if Q2 is ruled in) |
| ASan cells | `N3`/`N64` with the entries buffer heap-allocated at exactly `k × NCAPS` pairs; `F` built with `-DRX_FOREACH_PAIRS=8` on a 10-group VM pattern (kmax = 0: refusal) and a 3-group one (kmax = 2) | over-write past `k` entries; the macro exceeding `kmax` (the buffer is the struct's last member, so the over-run leaves the object) |

**The oracle and its independence.** `G` is libpcre2's global loop (pcre2demo's, in
iter_drv.c). It shares no source with pcrec. The new arms are held to `I`, and `I` is held
to `G`. That is deliberate. `N`, `X` and `F` run the same STEP as `I`, so comparing them to
`I` tests the delivery layer, the only new code. Comparing them to `G` directly would test
STEP a second time. The arms compare to `G` too, at no cost (a DIFF against `G` names the
arm), so a defect that touched STEP and the delivery layer in the same way is still caught.

**Populations (K35).** The section's existing floors (compiled groups, RETRY cells, one
artifact of each retry form) stay. New: **`MIN_SPLIT_RETRY`**, cells where a `next_n` call
returned with `it.flags & PCREC_ITER_F_RETRY` set (a batch boundary between an empty match
and its retry). The driver counts these from the struct, which is visible in the shared
block. The floor is set by the build lane from its first green run, the way the RETRY floor
was. Also new: a `Fcount` population floor (groups with ≥ 61 matches, where the macro
reaches k = 64).

### 5.2 The three in-tree drivers (owed since I1)

Each driver keeps its §3.1.3 loop. It gains ONE iterator arm through `RX_FOREACH` over the
artifact's own `rx_info`. That arm reaches `next_n` and the macro, and §5.1 already holds it
equal to `_next`. Each arm needs its own control, because the loop's answers are not the
iterator's (1,063 corpus pairs differ, `findall_iter.md` §0.4):

| driver | runner | the iterator arm's expectation | independent of pcrec? |
|---|---|---|---|
| `tests/encseam/findall_driver.c` (`iter` argv mode) | `run_encseam_tests.sh` | `want_f`, the runner's existing `re.finditer` spans: python's global iteration, the same oracle `global.rxt` is verified with. The case table's "lossy" class becomes exact under the iterator. That is a positive statement the runner can count (lossy cases agreeing with finditer under `iter`: floor = the lossy count) | yes (python `re`). Where `re` and libpcre2 disagree, the case is marked as `gen_global.py` already marks `pcre2-only` |
| `tests/assertions/gstart_findall.c` (`-i`) | `run_gstart_diff.sh` | the runner's shell oracle loop with pcre2demo's retry: after an empty match at `q`, ask the oracle for an ANCHORED + NOTEMPTY_ATSTART match at `q` before stepping. That is one option word added to the runner's `pcre2_oracle` | yes (libpcre2) |
| `tests/codegen/entry_shape_driver.c` (`iter` mode) | `run_entry_shape_identity.sh` | identity ACROSS RUNGS, the gate's existing rule, applied to the iterator arm's output (every span, every group) | not an oracle check: the gate's question is rung-invariance, and the iterator arm makes the iterator answer it too |

These are the smallest arms that give each driver's population (`\G` patterns, the
encoding seam's cases, the rung ladder) an iterator verdict. Two alternatives are not
proposed: moving those cases into `tests/findall/cells.tsv`, and a `next`-only arm.

### 5.3 Spec and structural checks

- `make test-spec-history` (the new §3.8.1/§3.8.2 anchors; §6 row 31).
- `run_residual_twins.sh` / the relocation check: `_next_n` calls no exported symbol (no
  `R_X86_64_PLT32 <p>_next` from `_next_n` under `-fPIC`), with a population floor of one
  per artifact that defines `next`.
- I1's compile matrix: gcc `-O0/-O2/-O3 -Wall -Wextra -Werror` and clang `-O2` over DFA,
  VM and compound artifacts with a driver that uses `RX_FOREACH`, nested and with `break`.
  I1's clang run found a `-Wtautological-compare`. The macro's comma initializer and its
  uninitialized `rx_foreach` are the likely `-Wmaybe-uninitialized` and `-Wshadow`
  surfaces.

### 5.4 Sabotage rows (PROPOSED: S1309-S1318, from I1's range S1297-S1330)

S1309-S1330 are unused on main, in every worktree and in the kit's reservations (checked
2026-10-21: the kit's ledger says "next free S1331", and S1331/S1332 exist). The manager
confirms the range. Each row's witness reaches its site through `test-findall`.

| id | plant | detector | old label |
|---|---|---|---|
| S1309 | `__pull` writes entry `k` (loop test `i > k`) | ASan exact-size cell (`N3`) | S938 |
| S1310 | entry stride 1 pair, not NCAPS | `N2` on a VM group with NCAPS > 1 (groups compared) | S1013 |
| S1311 | `__pull` keeps going after a give-up (ignores `r < 0`) | the `--step-budget` give-up cells through `N64`: count and `rc` against `I` | S939 |
| S1312 | the end path returns `k` instead of `i` | `N64`/`F` on any subject with fewer than 64 matches (the extra entries are stale) | new |
| S1313 | `k == 0` binds (the `k ?` guard removed) | `N0`: the following setter poisons the iterator, so `I` from `p` gives `PCREC_ERR_ITER` | new |
| S1314 | `.next_n = NULL` in `<prefix>_info` | `F`: refused where `I` reports matches | as S1305 for `next` |
| S1315 | the doubling never grows (k stays 4) — ANSWER-EQUIVALENT | `Fcount`: calls exceed the formula | new |
| S1316 | the inner increment does not clear `brk` (every body acts as a break) | `F` on any subject with 2 or more matches; `Fstop` | new |
| S1317 | `kmax` not capped by `RX_FOREACH_PAIRS / ncaps` | the ASan `-DRX_FOREACH_PAIRS=8` 3-group cell | S1016 |
| S1318 | the abi compare removed from `rx_foreach_begin` | `Fabi` (only if Q2 is ruled in; otherwise the row is withdrawn) | new |

S1315 is the one answer-equivalent mutant. Its detector is structural (a call count), as
S934's was.

---

## 6. The abi event and the spec (D76/D94/D80)

**One abi event**, the next number after main's at merge. I1 is 83, so I2 is 84 if nothing
lands between. Every artifact's text moves: the shared block's new type, inlines and macro,
`rx_info`'s appended member and initializer line, and `_next_n`. `PCREC_ITER_LAYOUT` does
NOT move (rx_iter is unchanged).

**Readers, found by grep at build time** (`grep -rn '\b83\b'` scoped as I1 did, plus every
reader that never cites the number, D94 addendum). The STARTING list is I1's re-pin set
(`docs/dev/lanes/i1build_report.md` §3, i1tri/i1tri2 reports): `PCREC_ARTIFACT_ABI`; the
guard text in match_api.md §1¶7 and the §6 row 1 value; `ABI_EXPECT` + its ledger
(`tests/codegen/run_codegen_tests.sh`); S693's anchor (`S693_abi_not_bumped.sh`);
`tests/codegen/run_cpset_structure.sh`'s EMITTED_BYTES manifest (twelve rows move by
`_next_n` + the block's growth); the K59-PREMUL raw-size rung; `run_recursion_identity.sh`'s
FILEPIN; `docs/dev/abi_changelog.md`; every design note that quotes "abi 83" as current
(reworded only where it claims current, never in history). Then run the suites that count
(registry, codegen, rxtsource, cpset-structure, compound, partlayout, encoding-checks,
memfn-arch): I1's triage rounds found readers of this kind in all of them.

**Spec hunks, in the build's commit** (`docs/spec/match_api.md`):
- §1¶2: the per-artifact list gains `<prefix>_next_n` (§3.8.1).
- §1¶5: the block's types gain `rx_nextnfn` (after `rx_nextfn`) and `rx_foreach`, with
  `rx_foreach_begin`/`rx_foreach_pull`/`RX_FOREACH`/`RX_FOREACH_PAIRS` (§3.8.2).
- §1¶6: `RX_FOREACH_PAIRS` is a caller-overridable default, the only `#ifndef` in the block.
- §1¶7 and §6 row 1: the abi number.
- §1¶8: the split `.h` carries `<prefix>_next_n`'s declaration.
- §2: the block regenerated from `'a(b|c)+d'`.
- §3¶1's entry table: a `_next_n` row.
- NEW §3.8.1 `<prefix>_next_n`: §2.1-§2.2 of this note as contract paragraphs (the
  `r < k` rule, the equivalence, the edges table's caller-visible rows).
- NEW §3.8.2 `RX_FOREACH`: §3.1's example, the control-flow promise, the batch-size
  sequence stated as UNSPECIFIED beyond "at most 64 entries and at most
  `RX_FOREACH_PAIRS` pairs per call", the stack bound, "finished when the loop exits", and
  the three refusals.
- §6: row 31 `next_n` (`rx_nextnfn`; `NULL` exactly where `next` is), and a ¶14c beside
  ¶14b.
- §3.1.3's loop prose: one sentence pointing callers at §3.8/§3.8.2 as the recommended
  find-all. The loop stays documented (the drivers keep it).

**Not moved:** `<prefix>_buffers`, the `_in` entries, the stamps (no new stamp: `next_n`
exists exactly where `next` does, and `<PREFIX>_ITER_RETRY` describes both), `rx_iter`.

**Elsewhere:** `src/gen/CLAUDE.md` (emit_iter.c's role), `tests/findall/CLAUDE.md` (the
arms), `docs/dev/abi_changelog.md`, plan.md `[FINDALL-NEXT]`, and the bench relay for main.
pcrec-bench's shim could time `next_n`/`RX_FOREACH` as a find-all form, through
`inbox_from_pcrec.md` (D78) and main's call.

---

## 7. Stages (and the difference from the design of record)

| stage | what | abi |
|---|---|---|
| **I2** (this note) | `next_n`, `__pull`, `RX_FOREACH`, `rx_info.next_n`; the §5 arms and drivers; S1309-S1318; the spec hunks | one (84 or next) |
| **I2-time** | §4's cell, queued after I2's `make test`/mech are green | none |
| **I3** (was rev 3's I2) | the kit's ITER form with its held row, `st`, S, `PCREC_ITER_LAYOUT` 3 → 4, S936/S937 | the kit's abi event, unchanged from rev 3 §1.3 |
| **I4** (was rev 3's I3) | `pair-hits` | one |

**The difference, reported per the brief's STOP RULE.** `findall_iter.md` rev 3 §6.9 names
**I2 = the kit's `st` stage** and **I4 = `next_n`**, and §12 (the I1 addendum) lists
"I2 appends" the batch fields AND `st`. The manager's later record (plan.md `[FINDALL-NEXT]`
next-line, wake.md, D171's "noted for I2") puts `next_n` + the macro in I2. The two are
compatible in substance: `next_n`'s design matches rev 1's twinned signature, with Q-I4's
full-caps stride. The two records differ only in stage NAMES and in the batch fields, which
§1.2 withdraws. This note follows the manager's record (it is later and Frank-informed), and
the renumbering above is the only change. The rename touches no shipped text. If the manager
prefers rev 3's names, this stage is "I4" and nothing else changes.

---

## 8. The sibling-of-a-family lens

**The entry family.** The exported entries form a small grid. On one axis is the operation
(search, match, match_caps, next). On the other is the binding of working storage: a
parameter on the `_in` siblings, a SETTER on the iterator (`<prefix>_iter_buffers`, which
dissolved `_next_in` before it existed). `next_n` adds a COUNT axis, on the iterate
operation only. It is not a dispersed new member: it is the same `iterate` row's controller
with `k` as a parameter instead of the constant 1, emitted by the same function from the
same static part (§2.3). **What simplifies:**
1. The batch design and its second delivery path are deleted (§1.2): a struct field set,
   a setter, an option bit, two static parts, a row column, a stage, four sabotage labels,
   two parity arms and a conditional section.
2. `_next` becomes a one-line controller over `__pull`, with no separate dispatch text.
3. "Batching is identical to K = 1" stops being a proof obligation, because it is the
   definition.

**The family that IS growing dispersed: entry pointers in `rx_info`.** `next` (I1) and
`next_n` (I2) are the only entries reachable through the record. `search`, `match` and
`match_caps` are not. A generic caller can iterate an artifact it cannot search. That is
the [V-E] entry-pointer struct and `[RXINFO-REMODEL]`'s "entries" section, both under
`[IFACE-PUSH]`. This note does NOT add `search` (no caller asked; Frank: build what is
needed). The third pointer is the trigger: the first request for a generic `search` or
`match` through the record moves all of them into one entries sub-struct in that push.
Until then the two iterator pointers are appended members, the D76 ritual.

**The storage-binding pair.** The `_in` entries (a parameter) and the iterator's setter are
two mechanisms for one fact. Filed as an observation for `[IFACE-PUSH]` (retire the `_in`
entries for a setter on `rx_ctx`?). It is not this note's to change.

**Critic unlock lens.** The general form of "amortize the exported call" is any entry that
takes a COUNT. `<prefix>_search_n` over many subjects is the bench's many-small-subjects
shape. It is filed as U-I2-4 with its trigger, not designed.

---

## 9. The standing questions (docs/design/CLAUDE.md)

### 9.1 The measurement regime — RELEVANT

Every number in §1.1 comes from the twin on the Linux dev box (Ryzen 7 7700X, Zen 4), gcc
15.2 `-O2`, pinned cpu7, 5 launches with arms interleaved, R1 (static, direct calls) and R2
(`-fPIC` shared object through the PLT). The run was NOT fully quiet (load1 median 1.71; the
SMT sibling peaked at 78.6% in launch 5). Ratios are throughput over whole find-alls
(dependent calls, each STEP's `lo` from the last). What could flip a decision:
- **The twin's `N64` was spans-only** (`mktwin.py`'s `_next_n` copies `c[0]` into one pair
  per entry). I2's entries hold full captures, written in place with no copy. On DFA cells
  (NCAPS = 1) this is the same write. On c4 (VM, NCAPS = 2) the twin copied 2 words and I2
  copies none. The prediction is "no worse", and §4's c4 gate checks it.
- **R1 vs R2.** The gain is largest through the PLT (c3-4k R2 0.74 vs R1 0.84 against `I`).
  The macro calls through a POINTER (`info->next_n`), neither R1's direct call nor exactly a
  PLT stub. The `I_info` arm measures the pointer's per-call cost. If it is ≈ 0, the macro
  is still justified by R2-like deployments (shared objects), but the c1/c4 neutrality would
  then be the whole story on static links. That is a reported fact, not a gate.
- **Zen 1** (the bench box) has costlier indirect branches than Zen 4. A bench run on the
  targeted hardware is the official verdict (D144 add. 4), via main.

### 9.2 The independent control — RELEVANT

§5.1: `G` (libpcre2) is the semantic control and shares no source. The new arms' expectation
is `I`, which is legitimate because their new code is only the delivery layer, and they also
report against `G`. §5.2: python `re`, libpcre2, and rung-identity (the last stated as not an
oracle). K35: `MIN_SPLIT_RETRY` and the `Fcount` floor are counted by the driver from the
struct and the call wrapper. They are not derived from the code under test's own output
format. [MECH-REACH]: every row in §5.4 names a witness on an existing population (the
retry cells, the give-up cells, the VM capture groups) or a new arm that runs on every
subject. S1318 is conditional on Q2.

### 9.3 What moves when data is regenerated — RELEVANT ONLY AS THE ABI EVENT

I2 adds no table, calibration or generated file. The one constant set (4, 64,
`RX_FOREACH_PAIRS` 256) is caller-side text. Changing a value moves the shared block's bytes
(an abi event, D76) and no answer. The batch sequence is stated as unspecified in the spec
(§6), so tuning it later is not a contract change. The abi event's readers are §6.

---

## 10. UNLOCKS (each with its trigger)

| id | unlock | trigger |
|---|---|---|
| U-I2-1 | `next_n` binds the VM run state once per CALL, not per STEP (the fast-tier stack buffers, then the deep re-run for the failing step only) | §4's `F` loses or merely ties `I` on c4 (VM) while winning on DFA cells |
| U-I2-2 | a per-artifact `<PREFIX>_FOREACH(it, m)` calling `<prefix>_next_n` DIRECTLY, with NCAPS a constant | `I_info` shows the pointer call costing more than the A/A floor per fill on a dense cell, AND a caller who has the header asks |
| U-I2-3 | `pcrec --emit-abi-header`: the shared block alone, for a caller with records but no artifact header (an [ART-MGR] loader) | the first such caller |
| U-I2-4 | `<prefix>_search_n` (many subjects per call) or a count on other entries | a bench cell where the per-call cost of `_search` is a measured share (the many-small-subjects shape) |
| U-I2-5 | `search`/`match` pointers in `rx_info` (the entries section) | a third entry pointer requested: then all of them move in `[IFACE-PUSH]` (§8) |
| U-I2-6 | hoisting variable resolution into bind (I1 §12 left it per search; it needs resolved state in `rx_iter`) | a var-bearing find-all cell where resolution is a measured share. It rides I3's layout event if it arrives first |

---

## 11. Questions for Frank (plain words, each with a leaning)

**Q1. A pattern with very many capture groups.** The macro's buffer is a fixed 4 KiB on the
stack. It holds 64 matches when a pattern has up to 3 capture groups, fewer matches as
groups grow, and not even one match past 255 groups. Above that the options are to stop
with the iterator's error code (the caller raises the buffer size with one `#define`, or
calls the artifact's own entries with a buffer they size), or to switch to a
variable-length stack array sized from the record. *Leaning: stop with the error code.* It
is rare, it is loud, it keeps the stack bound fixed, and a variable-length array would make
the stack use depend on a pattern the caller may not see.

**Q2. Checking that the record matches the header.** The macro exists for code that holds an
artifact's record without that artifact's header, so the record may come from a different
pcrec build than the header the macro was compiled with. One compare per loop (the
record's version number against the header's) turns that mismatch into the iterator's
error code instead of a call through the wrong offset. You said you do not want
hand-holding on wrong calls. This is not a check on the caller's calls: it is the only
check that the record the generic loop reads is laid out as the loop thinks. *Leaning:
check, once per loop, never per match.*

**Q3. Leaving the loop early.** The macro fetches matches ahead in batches. A caller who
breaks out has had up to 63 matches fetched that they never saw, and the iterator has
moved past them. *Leaning: state it in the spec ("an iterator given to RX_FOREACH is
finished when the loop exits"), and do not add code to rewind or to block further calls.*
A caller who wants to stop and resume uses `_next`.

**Q4. Withdrawing the internal batch for good.** Your October 14 ruling put batching inside
the iterator (it caches results and hands them out one per call). The parity run measured
that slower on every dense cell, and your macro idea puts the cache on the caller's side
instead, where calls are actually removed. *Leaning: withdraw the internal version
entirely (it was never built), and record that the macro is how batching is offered.*

---

## 12. What the panel should attack

1. **c6.** The twin's `N64` lost 1.66-1.95x to `I` on the attempt route (§1.1), and this
   note's explanation is a guess. Is there a structural reason the shared static-label body
   would be slower when called in a loop from `__pull`?
2. **"`_next` folds to I1's code."** Is `__pull(it, caps, 1)` really identical under gcc
   15.2 `-O2`, given the `always_inline` STEP and the VM's `__step_own` stack buffers? The
   gate exists. Is the fallback (keep I1's text) a second mechanism by the house rule?
3. **The macro's text.** Check the two-loop idiom, `continue`, nesting, the comma
   initializer, `-Wall -Wextra -Wshadow -Wmaybe-uninitialized`, clang, `-O0` and the escape
   of `f->buf` (it forces `head`/`count` to memory around each fill, a per-match load and
   store). Is the per-match cost of `rx_foreach_pull` inlined visible on c1?
4. **k = 0 inertness** versus "the first call binds". Is a k = 0 call that leaves an invalid
   header unreported acceptable?
5. **The new arms' expectation is `I`.** Is §5.1's argument (only the delivery layer is
   new) sound, or does a plant in STEP that only `next_n`'s loop reaches exist (for
   example, state carried in a local across STEPs)?
6. **The drivers' oracles** (§5.2): python `re.finditer` as encseam's iterator oracle, and
   the runner-side retry loop as gstart's. Do they agree with libpcre2 on those case tables?
7. **The stage rename** (§7) and the withdrawal (§1.2): does anything shipped on
   `lane/i1build` (spec §3.8, the block's comment, §12) promise the batch fields?
8. **Sibling lens** (§8): the rx_info entry pointers as the dispersed family. Is two
   members the moment to stop, or is this the third case of an "entries reachable by
   record" fact (the `_in` setter pair) already?
9. **Unlock lens:** the general form and what it would unlock, with triggers. §10 is a
   first list.
