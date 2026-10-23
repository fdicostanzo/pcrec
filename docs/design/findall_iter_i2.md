# [FINDALL-NEXT] I4 — `<prefix>_next_n` and the generic `RX_FOREACH` (DESIGN NOTE, revision 2)

**Revision 2** (lane `i2rev`, 2026-10-21, on `lane/i2design`) applies every disposition of
the light D6 panel r1 (`docs/dev/reviews/2026-10-21-r1-findall-i2.md`: critics `i2crit-chk`,
`i2crit-sem`, `i2crit-fam`; 21 findings, 16 ACCEPT, 1 NOTE, 4 UNLOCK, plus one
SIMPLIFICATION). **Read §R2 first.** Changed text is marked `[r1 <id>]`. The three largest
changes:
- **One body, flipped (fam-2).** I1's `_next` body becomes the static `always_inline`
  `<p>__one`. `_next` is `__one`, and `_next_n` is a loop of `__one` up to `k`. The fold
  prediction and §2.3's fallback are deleted.
- **No new entry (fam-1).** The one `iterate` row of `entry_rows[]` emits both controllers.
  `_next_n` takes `_next`'s linkage, so `.next_n` is NULL exactly where `.next` is.
- **Stage names stay revision 3's (fam-3).** This stage is **I4**. Revision 1 called it "I2"
  and renamed the kit's `st` stage I3; that rename is undone. The file name and the lane name
  keep "i2", and the panel's ids (`U-I2-n`) are kept as stable labels. Frank's build go
  (2026-10-21, "you have a go for" I2) names THIS stage, whatever its number.

Revision 2 also changes the doubling start from 4 to 1 (sem-1). That moves a number Frank
stated in his charter ("4 → 64"), so it is recorded as the manager's call, which Frank may
reverse (§3.3). It settles Q1-Q4 the same way (§11).

**Revision 1** (lane `i2design`, 2026-10-21, branch `lane/i2design` from `lane/i1build` at
`e0139d8c6`, I1 built, abi 83, NOT merged). DESIGN ONLY: nothing under `src/`, `cli/`,
`lib/` or `tests/` changes, and nothing was measured. Every number below is copied from a
named record.

**Inputs this designs TO, not re-opens:** D165 (items 1-6, addenda 1-4), D171 (Frank,
2026-10-21: ~2 ns setup accepted; the batch cell is `off`; `next_n` noted for the next
stage), the I1 build (`findall_iter.md` §12, `docs/spec/match_api.md` §3.8,
`src/gen/emit_iter.c` on `lane/i1build`), the manager's I1 ruling (no batch ABI in I1),
Frank's charter for this stage (the manager's record, `docs/dev/wake.md`, 2026-10-21:
"`next_n` + a generic `RX_FOREACH(info, ...)` over `info->next_n`, with a doubling buffer
4 → 64"; "the generic macro usable without the .h"), Frank 2026-10-21 "build what is needed
and not theoretical needs", and Frank's go for design → critic → build.

**Why a separate note, not revision 4 of `findall_iter.md`.** The house pattern for that
note is in-place revisions with a §R table per revision, plus §12 as the I1 build's
addendum. This stage has its own abi event, and it needs only a small part of the
1,769-line note: §2.1 (STEP), §3 (semantics), §5.3 (the parity harness) and §6.8 (the
sabotage labels). A revision 4 would have to rewrite §2.3, §3.4a, §5.3, §6.9, §8 and §9
around a withdrawal (§1 below) and would bury this design in that rewrite. So this note is
the delta. `findall_iter.md` §12 gets a one-paragraph pointer that names what this note
supersedes (§1.2), and nothing else in it changes.

---

## R2. What revision 2 changed (panel r1 finding → section)

Dispositions are the manager's (review file). "Manager's call, Frank may reverse" marks the
two places where a disposition settles something Frank stated or was asked.

| finding | disposition | what changed | where |
|---|---|---|---|
| chk-1 | ACCEPT | An A/A pair per gated ratio (`I_i1` twice, `F` twice). Each new ratio's floor = max(\|median A/A ratio − 1\|, IQR / median). A re-queue rule for a non-quiet run | §4 |
| chk-2 | ACCEPT | A POSITIVE gain cell: `F/I < 1 − floor` on c3-4k R2 and c3-1m R2, where failing it is a finding. c7 becomes a gated bound. `N4`, `N64` and `I_info` are diagnostics, not gates (D77) | §4 |
| chk-3 | ACCEPT | One objdump of the built artifact before the gate, as a falsifiable hypothesis: is `__find` inlined into `_next_n`'s loop, and does the loop spill? | §4.1 |
| chk-4 | NOTE | §1.1's derived `N64/I` column divides medians of different arms and has no IQR. Said so | §1.1, §9.1 |
| chk-5 | ACCEPT | `entry_shape_driver`'s iterator arm is compared to `_next` AND to libpcre2, not by rung identity | §5.2 |
| chk-6 | ACCEPT | Batch-boundary sabotage (S1319: the retry flag lost on the k-exhausted return, witness `N1`/`N2`/`N3` on `a*`; S1320: a refill one entry early). An `Fstop` break exactly at a batch end. Resuming `_next` on the same iterator after a break is UNDEFINED in the spec, with no arm | §3.4, §5.1, §5.4, §6 |
| chk-7 | ACCEPT | A named witness per sabotage row. S1311's give-up fires mid-batch after ≥ 1 entry. S1313 also runs on a BOUND and an ENDED iterator. Each row has a K35 reach count | §5.4 |
| chk-8 | ACCEPT | A structural compare (objdump): I4's `_next` equals I1's. With fam-2 this holds by construction; the compare stays as the control | §5.3 |
| sem-1 | ACCEPT (manager's call, Frank may reverse) | The doubling starts at 1: 1, 2, 4, …, 64. A sparse early-break cell (one match near the start of a 1 MiB subject) is added to §4 | §0, §3.2, §3.3, §4 |
| sem-2 | ACCEPT | The spec states that `it.rc` is meaningful only when the loop ran to its end; after an early exit it may reflect searches never delivered. §3.1's example is fixed | §3.1, §3.4, §6 |
| sem-3 | ACCEPT | The call-count formula is fixed. `Fcount` builds its expected count by simulating the fills, `kmax` included | §3.3, §5.1 |
| sem-4 | ACCEPT | "`r == k` ⇔ live" holds for `k ≥ 1` only | §2.1 |
| sem-5 | ACCEPT | The spec lists every meaning of `PCREC_ERR_ITER` the macro can leave, and says `lo` is not set on a refusal | §3.4, §6 |
| sem-6 | ACCEPT | The spec states: C99 `for` declarations, `m` must be an identifier, and a note on clang `-Wcomma` | §3.3, §6 |
| sem-7 | UNLOCK | An `rx_info` layout number separate from `abi`. Trigger: the first cross-build record holder ([ART-MGR], U-I2-3) | §10 (U-I2-7) |
| sem unlock (a) | UNLOCK, not built | `RX_FOREACH_IN` over a caller-declared state. Trigger: the first stop-and-resume batching caller | §10 (U-I2-8) |
| fam-1 | ACCEPT | NO new `PcrecEntry`. The one ITERATE row emits both controllers; `next_n` takes `next`'s linkage bit. No `PCREC_ENTRY_PUBLIC_N` move and no change to `compound_drive.c:75` | §2.3, §8 |
| fam-2 | ACCEPT | One body, flipped: `__one` is I1's `_next` body; `_next` = `__one`; `_next_n` = a loop of `__one`. The fold prediction and the fallback are deleted. "`I` unharmed" stays as a measurement | §0, §2.3, §4 |
| fam-3 | ACCEPT | Revision 3's stage numbers are kept: this stage is I4. The rename is undone everywhere. The build commit carries the plan `[FINDALL-NEXT]` next-line rewrite and D171's gloss | header, §6, §7 |
| fam-4 | ACCEPT | The abi-compare question is reworded: an all-or-nothing gate, correct and loud, with no lasting promise, and required for safety in the other direction | §3.4, §11 Q2 |
| fam-5 | UNLOCK | An "rx_info slot" column in `entry_rows[]`, so the record's pointers come from rows. Trigger: a third hand-written `rx_info` pointer, or [V-E] | §10 (U-I2-9) |
| fam SIMPLIFICATION | ACCEPT | The callback entry is DISSOLVED by `RX_FOREACH` (the plan row's title still says "iterator / callback entry"). Unlock (b): retire `match_api.md` §3.1.3's hand loop and make `_next_pos` internal | §1.2, §8, §10 (U-I2-10) |
| Q1-Q4 | manager's call with the panel, Frank may reverse | Q1 refuse past the buffer; Q2 one abi check per loop (fam-4's wording); Q3 an early break skips, stated in the spec; Q4 the internal batch is withdrawn for good and the callback entry dissolved | §11 |
| ids | CONFIRMED | S1309-S1318 for this stage (from I1's range); the two new rows take S1319-S1320 | §5.4 |

### R2a. The build's corrections (lane i2build, 2026-10-21)

| what | finding | ruling | where |
|---|---|---|---|
| §5.3's chk-8 control | I4's `_next` object is NOT identical to I1's on c3, c6 or c4 (gcc 15.2 `-O2`). Pasting I1's literal `_next` text into the I4 artifact gives the same object as `return __one(...)` (c3, c6), so the cause is the TU gaining `_next_n`, a second caller of the shared statics, not `__one`. No text spelling removes it | manager R1: the objdump identity is WITHDRAWN. It is replaced by a TEXT check (the I4 artifact's `__one` body equals the I1 compiler's `_next` body byte for byte, on DFA unanchored, DFA attempt and VM, with a planted control; `tests/findall/run_one_body.sh`) and by gate 1 "`_next` unharmed" as the deciding measurement | §5.3 |
| §4.1 H1-H3 | H1 TRUE on the unanchored DFA (no call in the loop; `__enter` only on the cold bind path). H2 TRUE on c6 (one `call __find` per match, no second copy). H1 FALSE as stated on the VM: the loop calls the hybrid's out-of-line `rx_prefilter` at the same two sites `_next` has in I1. H3 FALSE: `caps` and `k` are spilled and reloaded per match (c3: 2 loads and 1 store per match) | recorded as findings; the timing gates measure their cost | §4.1; `docs/dev/lanes/i2build/objdump/` |

---

## 0. Answers first

1. **`size_t <prefix>_next_n(rx_iter *it, ptrdiff_t (*caps)[2], size_t k)`** writes up to
   `k` matches, each `<PREFIX>_NCAPS` pairs (entry `i` at `caps + i * NCAPS`). It returns
   the count. **A return below `k` means the iterator has ended**, and `it.rc` says why
   (0 done, < 0 the code), exactly as after `_next` returned 0. `k == 0` returns 0 and does
   nothing. `next_n(it, caps, k)` IS `k` calls of `next`: it is a loop over the same
   inlined body (§2.3). The two interleave freely on one iterator (§2).
2. **No `rx_iter` change.** Every fact carried across calls (`lo`, the retry bit, `rc`, the
   ENDED state) is already in I1's struct. `PCREC_ITER_LAYOUT` stays 3, and `sizeof(rx_iter)`
   stays 72 B on LP64.
3. **The internal batch is withdrawn, not deferred** (§1.2): `rx_iter_batch`,
   `PCREC_ITER_OPT_BATCH`, `rc_next`, `bhead`/`bcount`, `__fill`/`__deliver`, the `iterate`
   row's `batch` column. D171 measured it slower than `I` on every dense subcell, and
   `next_n` batches on the caller's side, where the twin measured a gain. §12's "I2 appends
   at layout 4" list shrinks to the kit's `st`, which stays stage I2 with revision 3's rule
   (it lands with the first held row). The callback entry the plan row names is dissolved
   by `RX_FOREACH` `[r1 fam-S]`.
4. **ABI placement.** The shared block gains `rx_nextnfn`, `rx_foreach` (the macro's state),
   `rx_foreach_begin`, `rx_foreach_pull`, `RX_FOREACH` and `RX_FOREACH_PAIRS`. `struct
   rx_info` APPENDS `next_n` after `next`. Per artifact: the exported `<prefix>_next_n`, its
   header declaration, and `.next_n` in `<prefix>_info`. No new `PcrecEntry` `[r1 fam-1]`.
   One abi event, the next number after main's at merge (83 + 1 = 84 if nothing else lands
   first). Its readers are found by grep (D76/D94, §6).
5. **`RX_FOREACH(info, it, m)`** iterates through `info->next_n` with a stack buffer whose
   batch size doubles 1, 2, 4, 8, 16, 32, 64 (capped by the buffer) `[r1 sem-1]`. It needs
   only the shared block (any abi-matching pcrec header), never the artifact's own `.h`. It
   never allocates. Its automatic storage is one `rx_foreach`: `RX_FOREACH_PAIRS` (256)
   pairs plus 72 B, which is 4,168 B on LP64 (computed from the layout, not measured).
   `break`, `continue` and `return` in the body behave as in a plain loop (§3).
6. **One body, flipped** `[r1 fam-2]`. I1's `_next` body becomes the static
   `always_inline` `<p>__one(it, caps)`. `_next` is `return <p>__one(it, caps);` and
   `_next_n` is a loop of `__one` up to `k`. Both are emitted by the existing `iterate` row,
   with `_next`'s linkage `[r1 fam-1]`. `_next` is I1's `_next` by construction, and a
   structural compare keeps that as a control (§5.3).
7. **Checked** (§5): new arms in `tests/findall/iter_drv.c` (`next_n` at k = 1, 2, 3, 64,
   interleaved, `RX_FOREACH`, early `break` including at batch ends, k = 0 in every state,
   call counts, exact-size ASan buffers), all held to libpcre2's global loop (`G`) through
   `I`. The iterator arms owed after I1 go into the three in-tree drivers. Twelve sabotage
   rows, S1309-S1320, each with a named witness and a reach count (§5.4).
8. **Measured** (§4): the parity harness's post-build mode gains arms `I_i1` (twice), `F`
   (twice), `I_info`, `N4` and `N64`. The cell is NAMED here, not run. Gates
   `[r1 chk-1, chk-2]`: "`I` unharmed" (`I` at I4 against `I` at I1); `F/I ≤ 1 + floor` on
   c1, c3, c4 and c6 in both regimes; a POSITIVE gain `F/I < 1 − floor` on c3-4k R2 and
   c3-1m R2; bounds on c7 and on a new sparse early-break cell. An objdump hypothesis is
   checked first (§4.1).

---

## 1. What this stage is, and what it replaces

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

**The derived column is a ratio of two medians taken from different arms, and it has no
IQR of its own** `[r1 chk-4]`. It shows direction and rough size. It is not a measured
ratio, and no gate in this note reads it.

The brief's "0.58x on prose via the PLT" is c3-4k R2, `N64/L_old` = 0.5761. Against the
iterator itself it is 0.74. D171's reading stands: `B64` (the internal cache) lost on every
dense subcell while keeping one exported call per match, so **the gain comes from removing
calls, not from caching**. Three facts constrain the design:
- **c7: a fixed k = 64 is a 26x loss for a caller who stops early.** A doubling start of 1
  answers it `[r1 sem-1]`: a caller who stops after 3 has had fills of 1 and 2, so it pays
  for no search it does not see (§3.3).
- **c6: `N64` loses 1.66-1.95x to `I` on the attempt route's shared static-label body.** It
  is UNEXPLAINED in the record. The twin's `N64` ran `__find` from a second exported
  function, and on this route `__find` is `noinline`. A guess, not a finding: the twin's
  `_next_n` compiled the static body at a different layout. In this design `_next_n` loops
  over the SAME inlined `__one` that `_next` is, and on this route both reach the one
  static `__find` by a call (§2.3). So the built artifact cannot repeat the twin's
  two-copy shape. Cell c6 is in the gate list, and §4.1's objdump states what the loop must
  look like there.
- **c1 and c4: no gain.** Batching is neutral where each match costs little relative to a
  call, or where the VM's per-step binding dominates. The macro must not LOSE there. That is
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
| `__fill`, `__deliver`, the IT2 drained-batch test | rev 3 §2.3 | `next_n` is a loop of `__one` that writes straight into the caller's entries. Nothing is buffered across calls |
| the `iterate` row's `batch` column (`fill` / `off`) and the "batch cell flip" stage | rev 3 §6.9, U1 | no second delivery path exists to select |
| §3.4a "batching is answer- and give-up-identical BY CONSTRUCTION, IF ..." | rev 3 §3.4a | `next_n` IS `k` calls of the one body. Identity holds with no condition (D165 add. 4 made each STEP its own meter) |
| sabotage labels S1009, S1013 (as a batch-region row), S1016, S1038 | rev 3 §6.8 | their sites are not built. S1013's stride question and S1016's exact-size question re-aim at `next_n` (§5.4) |
| the `B64` and `I_fill` parity arms | rev 3 §5.3 | nothing left to time |
| **the callback entry** (the plan row's title: "find-all iterator / callback entry") `[r1 fam-S]` | plan.md `[FINDALL-NEXT]` | DISSOLVED by `RX_FOREACH`. A caller-supplied callback per match was the other way to hide the loop. The macro hides it in the caller's own frame, with no indirect call per match and no closure state. The plan row's title is corrected at the build commit (§6) |

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
  says. **For `k ≥ 1`, `r == k` ⇔ the iterator is still live** `[r1 sem-4]`: a next call
  continues after the k-th match. At `k == 0` the return is 0 whatever the state, so it says
  nothing about liveness (§2.2).
- **Equivalence (the design's one invariant).** For every `k ≥ 1`, `next_n(it, c, k)` leaves
  `*it` and the entries exactly as `k` successive `next(it, c_i)` calls would, stopping at
  the first `next` that returns 0. This is true by construction: both run the one body
  `__one` (§2.3). Calls of the two may be mixed on one iterator. Every §3.8 rule
  (FRESH/BOUND/ENDED, the setters, stickiness, what must not change, copies, concurrency)
  applies unchanged. The STATE between calls is the same five fields `next` already carries
  (`hdr`, `rc`, `flags`, `lo`, the bindings).

### 2.2 The edges

| edge | behaviour | why |
|---|---|---|
| `k == 0` | returns 0 and touches nothing, in EVERY state: a FRESH iterator stays FRESH (its setters still work), a BOUND one does not advance, an ENDED one keeps its `rc`, and an invalid header is not refused. No search runs | the loop's test `i < k` is false before the first `__one` (§2.3). `r < k` is false (0 < 0), so a 0 here never reads as "ended" |
| caller's buffer full mid-subject | returns `k`, BOUND, `lo`/`flags` as after the k-th `next` | §2.1's invariant |
| the k-th match is EMPTY at `q < n` | `flags = PCREC_ITER_F_RETRY`, `lo = q`. The NEXT call (either entry) starts with the anchored NOTEMPTY retry at `q` | the retry bit is iterator state (I1 `__step`), not call state, and nothing on the k-exhausted return touches it. S1319 plants the loss (§5.4). The arm in §5.1 splits a batch at every position (k = 1, 2, 3), so a split falls between an empty match and its retry on every retry cell, and the driver counts those splits (a floor) |
| non-empty match ending at `e` | `lo = __next_pos(s, n, e − 1)`, the K75 aligned end, inside STEP | unchanged. S1300's witness cells (`a\x80a`, `\xc3\xa9\x80a`) run through the new arms too |
| a give-up or refusal after `j` matches | returns `j` (< k), entries `0..j−1` written, `rc` = the code, ENDED, `lo` = the start of the search that gave up | `__one`'s end path, once. No pending code: `j` < `k` already says "and then it ended" |
| done after `j` matches | returns `j` (< k), `rc = 0` | as `_next` |
| ENDED on entry | returns 0, `rc` untouched (§3.8¶7) | `__one` on ENDED |
| FRESH / invalid header | bind (or refuse with `PCREC_ERR_ITER`) on the first call with `k ≥ 1` | `__one`'s `__enter`, unchanged |
| bind-time refusal (startpos, `-futf-check`) | returns 0, `rc` = that code | unchanged |
| the VM's tiered storage | each `__one` runs through `__step_own` (fast tier, deep re-run on a FRAMES give-up) or the bound buffers, per match, as `_next` does | one body (§2.3). Binding the run state once per call is an UNLOCK (§10 U-I2-1) |
| `k * NCAPS` overflows `size_t` | the caller's buffer cannot exist; UNDEFINED like any wrong buffer size | no check (D165 add. 3) |

### 2.3 The emission: one body, two controllers `[r1 fam-1, fam-2]`

`pcrec_emit_iterate` (src/gen/emit_iter.c) is the one emitter of the `iterate` row. Today it
writes `__enter`, `__step` (and `__step_own` on the VM), then `_next`. At I4 it writes the
same three, then I1's `_next` body UNCHANGED under a new name and storage, then the two
controllers:

```c
static inline __attribute__((always_inline)) int <p>__one(rx_iter *it,
                                    ptrdiff_t (*capture_spans)[2])
{ /* I1's `_next` body, text unchanged: __enter on a non-BOUND header, the STEP
     dispatch (it->bufs on the VM, __step on the DFA), the end path */ }

__attribute__((noclone)) int <p>_next(rx_iter *it, ptrdiff_t (*caps)[2])
{ return <p>__one(it, caps); }

__attribute__((noclone)) size_t <p>_next_n(rx_iter *it, ptrdiff_t (*caps)[2], size_t k)
{
    size_t i = 0;
    while (i < k && <p>__one(it, caps ? caps + i * <P>_NCAPS : (ptrdiff_t (*)[2])0))
        ++i;
    return i;
}
```

(`noclone` is written through `pcrec_attr_text(PCREC_ATTR_NOCLONE)`, the guarded spelling
I1 already uses.)

- **`_next` is I1's `_next` by construction.** Its whole body is `__one`, which is I1's
  text. There is no fold to predict and no fallback copy to keep: revision 1's §2.3
  prediction and fallback are deleted. §5.3's structural compare is the control, and §4's
  "`I` unharmed" arm is the measurement.
- **`_next_n` re-tests the header once per match.** `__one` begins with I1's
  `it->hdr != PCREC_ITER_BOUND` test, so the loop pays one load and one predicted branch per
  match. That is the same test `_next` pays per call. Hoisting it out of the loop would need
  a second body, which is what fam-2 removed. §4.1 states what the loop is expected to look
  like.
- **No exported entry calls another** (D163 add. 12 / `compound_entries.md` §3.0 invariant I3, not stage I3): both
  inline the static part.
- **No new entry** `[r1 fam-1]`. `_next_n` is not a `PcrecEntry`. The single `iterate` row
  (`PCREC_ENTRY_NEXT` on `sh_dfa`/`sh_vm`, `PCREC_COMB_ITERATE`, `EM_ITER`) emits both
  controllers. `_next_n` takes `_next`'s linkage, `pcrec_entry_storage(cx,
  PCREC_ENTRY_NEXT)`. So `<prefix>_next_n` exists exactly where `<prefix>_next` does, and
  `.next_n == NULL` ⇔ `.next == NULL`. `PCREC_ENTRY_PUBLIC_N` does not move, and
  `compound_drive.c:75` does not change. Where a request keeps the entries static,
  `rx_info.next_n` still points at `_next_n`, as `.next` does.
- **Scaffold.** Everything above is inside the scaffold bracket
  (`pcrec_sb_scaffold_open`), as I1's iterator is, so no length decision reads it
  (`findall_iter.md` §6.4). The mover census (`tests/findall/mover_census.py`) expects zero
  counted moves.

---

## 3. `RX_FOREACH` — the generic loop

### 3.1 Use

```c
rx_iter it = RX_ITER_INIT(s, n);          /* setters as usual, while FRESH */
int stopped = 0;
RX_FOREACH(&rx_info, &it, m) {            /* any artifact's rx_info; only the shared block is needed */
    report(m[0][0], m[0][1]);             /* m: ptrdiff_t (*)[2], info->ncaps pairs */
    if (enough) { stopped = 1; break; }
}
if (!stopped && it.rc < 0) ...            /* the code that ended it, as after _next */
```

`it.rc` is read only when the loop ran to its end `[r1 sem-2]`. After an early exit, the
last fill may have run into the end of the subject or a give-up while matches were still
buffered, so `it.rc` and ENDED can describe searches the body never saw.

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
    f->k = f->kmax ? 1 : 0;                                /* [r1 sem-1] */
    if (f->k == 0 && it->hdr != PCREC_ITER_ENDED) {        /* refused: Q1, Q2 */
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
- **Language requirements** `[r1 sem-6]`. The macro declares variables in `for`
  initializers, so it needs C99 or later. `m_` must be a plain identifier, because it is
  pasted into the state's names (`rx_fe_##m_`). The inner initializer uses the comma
  operator, so clang's `-Wcomma` warns at every use; the spec says so, and §5.3's compile
  matrix records the warning set rather than suppressing it.
- **Each argument is evaluated once** (in `rx_foreach_begin`). `m_` names the match pointer
  and also suffixes the state's names, so nested `RX_FOREACH` loops with distinct `m_`
  names compile. Two consecutive loops with the same `m_` are separate `for` scopes.
- **It never allocates.** `rx_foreach` is one automatic object, 4,168 B on LP64 at the
  default: 256 × 16 B of buffer + 8 words + the `int` and its padding (computed; the build
  lane measures it with `sizeof`). `begin` writes eight fields and never the buffer (no
  memset). The c2/c5 fixed-cost cells are where a hidden init cost would show (§4).
- **Without the artifact's `.h`.** The macro names only shared-block identifiers
  (`struct rx_info`, `rx_iter`, `rx_nextfn`/`rx_nextnfn`, `PCREC_*`). A translation unit
  that includes ANY pcrec header of the same abi can iterate any artifact whose `rx_info`
  it holds. There is no standalone header. A caller holding a record from a library with
  no pcrec header at all is the trigger for `--emit-abi-header` (§10 U-I2-3), not built.
- **Batch sizes** `[r1 sem-1, sem-3]`. 1, 2, 4, 8, 16, 32, 64, 64, ..., capped at
  `kmax = min(64, RX_FOREACH_PAIRS / ncaps)`. The iterator ends on the first fill that
  returns fewer than it asked for, so for `M` matches the macro makes the smallest number of
  calls `t` whose summed batch sizes reach `M + 1`. At `kmax = 64` that is
  `⌈log2(M + 2)⌉` calls for `M < 127`, and `7 + ⌈(M − 126) / 64⌉` calls for `M ≥ 127`
  (for `M` = 4,096, c1-4k: 70 calls instead of `I`'s 4,097). Revision 1's formula was
  wrong; the `Fcount` arm does not use any closed form, it simulates the fills with the
  group's own `kmax` (§5.1). The constants are LABELLED UNMEASURED DEFAULTS (memory
  `pcrec-suspect-tuning-constants`): 64 is the only k the twin measured (`N64`), 256 =
  64 × 4 is derived from it so that NCAPS ≤ 4 reaches the full k, and the start of 1 is
  the panel's (sem-1) in place of Frank's 4. **The start of 1 is the manager's call, which
  Frank may reverse**: it removes all over-fill for a caller who stops at a batch end, and
  it costs about 2 more calls than a start of 4 on a long find-all (c1-4k: 70 against 68).
  §4's `N4`/`N64` diagnostics show what the doubling costs on the dense cells. None of the
  three moves an answer.
- **Over-fill bound.** With doubling from 1, each batch is one larger than all the batches
  before it. A caller who leaves after `j` matches is inside some batch of size at most
  `j` (during doubling) or 64 (after the cap), and the searches it never sees are at most
  that batch less one. So the total work is at most `2j − 1` searches during doubling, and
  at most `j + 63` after it. c7 (stop after 3): fills of 1 and 2, no search wasted, 2 calls
  against `I`'s 3 and `N64`'s 61 wasted searches. The sparse early-break cell (one match
  near the start of 1 MiB, then `break`): one fill of 1, no wasted scan. A start of 4 would
  scan the whole MiB looking for matches 2-4.

### 3.4 The edges

| edge | behaviour |
|---|---|
| the iterator ends (done / give-up / refusal) | the loop ends after the last match; `it.rc` and `it.lo` as after `_next` returned 0 |
| the body `break`s / `return`s early | the iterator stays BOUND, or is ENDED if the last fill ran into the end, positioned after the last FILLED match. Matches already fetched are never seen: at most `j − 1` during doubling, at most 63 after it. **The spec states it: an iterator handed to `RX_FOREACH` is finished when the loop exits, however it exits.** `it.rc` is meaningful only if the loop ran to its end `[r1 sem-2]`. **Calling `_next`/`_next_n` on that iterator after an early exit is UNDEFINED** `[r1 chk-6]` (Q3). No arm tests it |
| `info->next_n == NULL` (an artifact compiled not to define `next`) | refused: `it.rc = PCREC_ERR_ITER`, ENDED, no body run |
| `info->abi != PCREC_RX_ABI_H` | refused the same way (Q2). `abi` is member 1 in every layout, so reading it is safe, and `next_n` is not read. The compare is an all-or-nothing gate `[r1 fam-4]` (§11 Q2) |
| `info->ncaps > RX_FOREACH_PAIRS` (more than 255 groups at the default) | refused the same way (Q1). The caller raises `RX_FOREACH_PAIRS` before the include, or uses `<prefix>_next`/`_next_n` with its own buffer |
| a refusal at begin | `it.lo` is NOT set `[r1 sem-5]`: the iterator never searched |
| an already-ENDED iterator | no refusal is written (`rc` stays, §3.8¶7); `next_n` returns 0; no body run |
| the body calls `next`/`next_n` on the same iterator | allowed, but those matches are skipped by the macro's next fill. The spec says "the body does not advance the iterator" |
| two TUs with different `RX_FOREACH_PAIRS` | the type differs per TU. It never crosses a call boundary (only `buf` reaches `next_n`, as a pair pointer), so it is harmless. Stated |

**The meanings of `PCREC_ERR_ITER` after `RX_FOREACH`** `[r1 sem-5]`, listed in the spec
§3.8.2: (1) the iterator was written outside its rules (I1's meaning, §3.8¶5: a setter
after bind, an invalid header); (2) the record's `abi` is not the header's; (3) the
record's `ncaps` exceeds `RX_FOREACH_PAIRS`; (4) the record has no `next_n`. The panel's
list had three; (4) is the NULL-pointer row of the table above and is listed with them. On
(2)-(4), `lo` is not set.

---

## 4. What is measured (named, not run)

**Cell:** the parity harness's post-build mode (`docs/design/findall_iter/twin/parity.sh`,
`PARITY_POST=1`) gains `PARITY_I4=1`, which adds these arms over the BUILT artifact
`[r1 chk-1, chk-2]`:

| arm | what | role |
|---|---|---|
| `I_i4` | `<prefix>_next` from this stage's compiler, as today | numerator of "`_next` unharmed", and the `I` of every `F/I` |
| `I_i1`, `I_i1′` | `<prefix>_next` from the I1 compiler (`PCREC_OLD`), twice | the A/A pair for "`_next` unharmed" |
| `F`, `F′` | `RX_FOREACH(&rx_info, ...)`, twice | the A/A pair for every `F/I` ratio |
| `I_info` | `info->next` per match through `&rx_info` (the generic caller with no macro) | DIAGNOSTIC: `(I_info − F) / matches` on c1-4k (4,096 matches) is the pointer's per-call cost |
| `N4`, `N64` | `<prefix>_next_n` direct, fixed k | DIAGNOSTIC: what the doubling costs |

**The floor** `[r1 chk-1]`. Each gated ratio gets its own floor, from the A/A pair of its
new arm: `floor = max(|median(X/X′) − 1|, IQR(X/X′) / median(X/X′))` over the launches,
with `X` = `I_i1` for "`I` unharmed" and `X` = `F` for every `F/I` ratio. No floor is
borrowed from another cell or from `findall_iter.md` §5.3.

**Gates** (D165 item 5: a loss is a FINDING with its numbers, not a tolerance):
1. **"`_next` unharmed":** `I_i4 / I_i1 ≤ 1 + floor` on every cell, R1 and R2.
2. **"never worse":** `F / I ≤ 1 + floor` on c1, c3, c4 and c6, R1 and R2. c6 is here
   because the twin's `N64` lost there (§1.1).
3. **"the reason it exists"** `[r1 chk-2]`: `F / I < 1 − floor` on c3-4k R2 and c3-1m R2.
   Failing it is a finding: the macro does not deliver the gain that motivated it.
4. **"no early-stop penalty"** `[r1 chk-2, sem-1]`: `F / I ≤ 1 + floor` on c7 (stop after
   3), and on a new cell **c8** (sparse early break: one match near the start of a 1 MiB
   subject, the body breaks after it). Both are bounds the doubling start of 1 is designed
   to meet (§3.3).

`N4`, `N64` and `I_info` are reported, never gated (D77: a diagnostic without a named
decision it would move is not a gate). c2 and c5 (fixed cost; D171 accepts ~2 ns) are
reported.

- **The run:** a boxqueue job `6x0-i4build-parity` (owner the build lane, quiet-gated,
  `boxqueue: idle-ok`, pinned to cpu7, 5 launches, arms interleaved, gcc 15.2 `-O2`, R1
  and R2). The answer gate (G2-G4) runs first on every new arm.
- **Re-queue rule** `[r1 chk-1]`. A run is NOT QUIET when its launch record shows a load1
  median above 1.0, or the SMT sibling of cpu7 above 25 % busy in any launch (both
  UNMEASURED DEFAULTS, labelled; the parity slot itself ran at load1 1.71 and a 78.6 %
  sibling peak, §9.1). A not-quiet run is re-queued once. A second not-quiet run is
  reported as it is, with its measured floors and the load record, and the gate verdict is
  read against those floors.
- **A loss on c6** sends the build lane to §4.1's objdump of the attempt route.
- **The PLT per-call cost** is not a separate cell. R2 against R1 on `I` and `F` carries
  it: c3-4k's `L_old` is 4,927 ns in R2 and 3,829 ns in R1, two exported calls per match.

### 4.1 The objdump hypothesis, checked before the gate `[r1 chk-3]`

One objdump of `<prefix>_next_n` in the built artifact, on one DFA unanchored artifact
(c3's `\w+`), one DFA attempt-route artifact (c6's `^a|b`) and one VM artifact (c4's
`(a)`), at gcc 15.2 `-O2`, before the timing job is queued. The hypothesis, stated so it
can fail:

- **H1.** On the unanchored DFA and the VM artifacts, the loop contains no `call` to a
  pcrec function: `__one`, `__step` and the find body are inlined into the loop.
- **H2.** On the attempt route, the loop contains exactly one `call`, to the static
  `<p>__find`, the same call `_next` makes once per match. There is no second copy of
  `__find`.
- **H3.** `i`, `k`, `caps` and `it` stay in callee-saved registers across the loop. There
  is no store of any of them to the stack per iteration.

If H1, H2 or H3 is false, the disassembly excerpt is a finding in the build report, and
the gate still runs. A false H2 is the first explanation to check for any c6 loss.

---

## 5. What is checked

### 5.1 `tests/findall/iter_drv.c`: the new arms

Every arm runs on every subject of every group (`cells.tsv`: 62 byte patterns × 18
subjects, 8 utf8 patterns × 11 subjects × 3 flag sets, auto/vm/dfa; plus the ASan cells).
Each arm's span sequence and final `rc` must equal `I`'s. `I` is already held to `G`.

| arm | what it does | catches |
|---|---|---|
| `N1`, `N2`, `N3`, `N64` | `next_n` at fixed k, entries concatenated | the loop, the count, the stride (on VM groups with NCAPS > 1, every group's pairs are compared, not only the span) |
| `X` | alternates `next` and `next_n(…, 2)` | the shared state; the retry carried across ENTRY kinds |
| `F` | `RX_FOREACH(&rx_info, &it, m)` | the macro, through the record |
| `Fstop` | `RX_FOREACH` with `break` after j = 1, 3, 5, 7 | exactly j delivered, equal to `I`'s first j. j = 1, 3 and 7 are batch ENDS (fills of 1, 2, 4) `[r1 chk-6]`; j = 5 is mid-batch |
| `N0` | `next_n(…, 0)` on a FRESH iterator, then `rx_iter_at(&it, p)`, then `I`; and `next_n(…, 0)` on a BOUND iterator mid-run and on an ENDED one `[r1 chk-7]` | k = 0 inert in every state: on FRESH the setter must still work (the result is `I` from `p`); on BOUND the continuation equals `I`'s; on ENDED it returns 0 with `rc` unchanged |
| `Fcount` | `F` over a COPY of `rx_info` whose `next_n` is a counting wrapper | the call count equals the count got by SIMULATING the fills (1, 2, 4, … capped at the group's own `kmax`) over the match count `I` found `[r1 sem-3]` |
| `Fabi` | `F` over a copy with `abi + 1` | refused: `rc == PCREC_ERR_ITER`, `lo` untouched, no body run (Q2 ruled in) |
| ASan cells | `N3`/`N64` with the entries buffer heap-allocated at exactly `k × NCAPS` pairs; `F` built with `-DRX_FOREACH_PAIRS=8` on a 10-group VM pattern (kmax = 0: refusal) and a 3-group one (kmax = 2) | over-write past `k` entries; the macro exceeding `kmax` (the buffer is the struct's last member, so the over-run leaves the object) |

No arm resumes an iterator after an `RX_FOREACH` break: that is UNDEFINED (§3.4)
`[r1 chk-6]`.

**The oracle and its independence.** `G` is libpcre2's global loop (pcre2demo's, in
iter_drv.c). It shares no source with pcrec. The new arms are held to `I`, and `I` is held
to `G`. That is deliberate. `N`, `X` and `F` run the same body as `I`, so comparing them to
`I` tests the delivery layer, the only new code. The arms compare to `G` too, at no cost (a
DIFF against `G` names the arm), so a defect that touched STEP and the delivery layer in the
same way is still caught.

**Populations (K35).** The section's existing floors (compiled groups, RETRY cells, one
artifact of each retry form) stay. New: **`MIN_SPLIT_RETRY`**, cells where a `next_n` call
returned with `it.flags & PCREC_ITER_F_RETRY` set (a batch boundary between an empty match
and its retry). The driver counts these from the struct, which is visible in the shared
block. The floor is set by the build lane from its first green run, the way the RETRY floor
was. Also new: a `Fcount` population floor (groups with ≥ 63 matches, where the macro's
seventh fill asks for k = 64), and the per-row reach counts of §5.4.

### 5.2 The three in-tree drivers (owed since I1)

Each driver keeps its §3.1.3 loop. It gains ONE iterator arm through `RX_FOREACH` over the
artifact's own `rx_info`. That arm reaches `next_n` and the macro, and §5.1 already holds it
equal to `_next`. Each arm needs its own control, because the loop's answers are not the
iterator's (1,063 corpus pairs differ, `findall_iter.md` §0.4):

| driver | runner | the iterator arm's expectation | independent of pcrec? |
|---|---|---|---|
| `tests/encseam/findall_driver.c` (`iter` argv mode) | `run_encseam_tests.sh` | `want_f`, the runner's existing `re.finditer` spans: python's global iteration, the same oracle `global.rxt` is verified with. The case table's "lossy" class becomes exact under the iterator. That is a positive statement the runner can count (lossy cases agreeing with finditer under `iter`: floor = the lossy count) | yes (python `re`). Where `re` and libpcre2 disagree, the case is marked as `gen_global.py` already marks `pcre2-only` |
| `tests/assertions/gstart_findall.c` (`-i`) | `run_gstart_diff.sh` | the runner's shell oracle loop with pcre2demo's retry: after an empty match at `q`, ask the oracle for an ANCHORED + NOTEMPTY_ATSTART match at `q` before stepping. That is one option word added to the runner's `pcre2_oracle` | yes (libpcre2) |
| `tests/codegen/entry_shape_driver.c` (`iter` mode) `[r1 chk-5]` | `run_entry_shape_identity.sh` | the iterator arm's spans and groups equal (a) the same artifact's `_next` loop, and (b) libpcre2's global loop over the same subject, through the runner's existing libpcre2 access | (b) yes (libpcre2). (a) is the delivery-layer compare. Rung identity is no longer the iterator arm's expectation |

These are the smallest arms that give each driver's population (`\G` patterns, the
encoding seam's cases, the rung ladder) an iterator verdict. Two alternatives are not
proposed: moving those cases into `tests/findall/cells.tsv`, and a `next`-only arm.

### 5.3 Spec and structural checks

- `make test-spec-history` (the new §3.8.1/§3.8.2 anchors; §6 row 31).
- **`_next` is I1's** `[r1 chk-8]`, **as text** (§R2a, ruling R1). The body of `__one` in
  the I4 artifact is compared with the body of `<prefix>_next` that the I1 compiler emitted,
  on one artifact of each body shape (DFA unanchored, DFA attempt, VM): they must be
  byte-identical, and a planted one-token change must fail the compare
  (`tests/findall/run_one_body.sh`; the expectations in `tests/findall/one_body/` were
  written by the I1 compiler). The objdump compare first designed here is withdrawn: the
  object code of `_next` moves once `_next_n` exists, whatever `_next`'s text, so "`_next`
  unharmed" is gate 1's measurement (§4).
- `run_residual_twins.sh` / the relocation check: `_next_n` calls no exported symbol (no
  `R_X86_64_PLT32 <p>_next` from `_next_n` under `-fPIC`), with a population floor of one
  per artifact that defines `next`.
- I1's compile matrix: gcc `-O0/-O2/-O3 -Wall -Wextra -Werror` and clang `-O2` over DFA,
  VM and compound artifacts with a driver that uses `RX_FOREACH`, nested and with `break`.
  I1's clang run found a `-Wtautological-compare`. The macro's comma initializer
  (`-Wcomma` under clang, §3.3) and its uninitialized `rx_foreach` are the likely
  `-Wmaybe-uninitialized` and `-Wshadow` surfaces. The matrix records which warnings a
  caller's `-Wall -Wextra` sees.

### 5.4 Sabotage rows (S1309-S1320, CONFIRMED)

S1309-S1318 are confirmed for this stage from I1's range S1297-S1330; S1319 and S1320 come
from the manager's extension S1319-S1325. Every row names its witness `[r1 chk-7]`, and its
**reach** is a K35 count the driver prints: the number of cells on which the witness ran
with the condition that exposes the plant. A row whose reach is 0 is UNREACHED and fails
the section.

| id | plant | witness (detector) | reach (counted) | old label |
|---|---|---|---|---|
| S1309 | `_next_n`'s loop test `i <= k` (writes entry `k`) | ASan exact-size cell `N3` on a subject with ≥ 4 matches (`a` on a×16) | `N3` ASan cells with ≥ 4 matches | S938 |
| S1310 | entry stride `caps + i`, not `caps + i * NCAPS` | `N2` on a VM group with NCAPS > 1 and ≥ 2 matches (`(a)` on `aaaa`), groups compared | VM cells with NCAPS > 1 and ≥ 2 matches | S1013 |
| S1311 | the loop ignores the end (`while (i < k) { __one(...); ++i; }`) | a `--step-budget` give-up that fires mid-batch, after ≥ 1 entry of the same `N64` call: count and `rc` against `I` | give-up cells where an `N64` call returned ≥ 1 entry and then the code | S939 |
| S1312 | the loop returns `k` on the end path | `N64` and `F` on a subject with 1 to 63 matches that ends by done (the extra entries are stale) | done cells with 1 to 63 matches | new |
| S1313 | the first `__one` runs whatever `k` is (`i < k \|\| i == 0`) | `N0` on FRESH (the following setter poisons the iterator, so `I` from `p` gives `PCREC_ERR_ITER`), on BOUND (the continuation skips a match) and on ENDED | `N0` cells per state, each ≥ 1 | new |
| S1314 | `.next_n = NULL` in `<prefix>_info` | `F`: refused where `I` reports matches | artifacts that define `next` with ≥ 1 match | as S1305 for `next` |
| S1315 | the doubling never grows (k stays 1). ANSWER-EQUIVALENT | `Fcount`: the calls exceed the simulated count | groups with ≥ 2 matches (where the true count first falls below `M + 1`) | new |
| S1316 | the inner increment does not clear `brk` (every body acts as a break) | `F` on any subject with ≥ 2 matches; `Fstop` | `F` cells with ≥ 2 matches | new |
| S1317 | `kmax` not capped by `RX_FOREACH_PAIRS / ncaps` | the ASan `-DRX_FOREACH_PAIRS=8` 3-group cell (NCAPS 4, kmax 2) with ≥ 6 matches (uncapped, the third fill asks for 4 entries, 16 pairs, and its third entry lands past the buffer) | that cell's match count | S1016 |
| S1318 | the abi compare removed from `rx_foreach_begin` | `Fabi` | `Fabi` cells | new (live: Q2 ruled in) |
| S1319 | the retry flag lost on the k-exhausted return (`if (i == k) it->flags &= ~PCREC_ITER_F_RETRY;`) `[r1 chk-6]` | `N1`, `N2`, `N3` on `a*` (and every retry group): spans against `I` | `MIN_SPLIT_RETRY` cells | new |
| S1320 | `rx_foreach_pull` refills one entry early (`f->head + 1 >= f->count`), dropping the last entry of every fill `[r1 chk-6]` | `F` on any subject with ≥ 2 matches; `Fstop` at the batch ends j = 1, 3, 7 | `F` cells with ≥ 2 matches; `Fstop` batch-end cells | new |

S1315 is the one answer-equivalent mutant. Its detector is structural (a call count), as
S934's was.

---

## 6. The abi event and the spec (D76/D94/D80)

**One abi event**, the next number after main's at merge. I1 is 83, so this stage is 84 if
nothing lands between. Every artifact's text moves: the shared block's new type, inlines and
macro, `rx_info`'s appended member and initializer line, `__one` and `_next_n`.
`PCREC_ITER_LAYOUT` does NOT move (rx_iter is unchanged).

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
  `r < k` rule, "`r == k` ⇔ live" for `k ≥ 1` only, the equivalence, the edges table's
  caller-visible rows).
- NEW §3.8.2 `RX_FOREACH`: §3.1's example (with the `stopped` flag), the control-flow
  promise, C99 `for` declarations, `m` an identifier, the clang `-Wcomma` note
  `[r1 sem-6]`, the batch-size sequence stated as UNSPECIFIED beyond "at most 64 entries
  and at most `RX_FOREACH_PAIRS` pairs per call", the stack bound, "finished when the loop
  exits", `it.rc` meaningful only after a loop that ran to its end `[r1 sem-2]`, resuming
  after an early exit UNDEFINED `[r1 chk-6]`, and the four meanings of `PCREC_ERR_ITER`
  with "`lo` is not set on a refusal" `[r1 sem-5]`.
- §4¶9a and the code table's `PCREC_ERR_ITER` row: "only `<prefix>_next` returns it"
  becomes "`<prefix>_next`, `<prefix>_next_n` and `RX_FOREACH` leave it".
- §6: row 31 `next_n` (`rx_nextnfn`; `NULL` exactly where `next` is), and a ¶14c beside
  ¶14b.
- §3.1.3's loop prose: one sentence pointing callers at §3.8/§3.8.2 as the recommended
  find-all. The loop stays documented (the drivers keep it; retiring it is U-I2-10).

**Not moved:** `<prefix>_buffers`, the `_in` entries, the stamps (no new stamp: `next_n`
exists exactly where `next` does, and `<PREFIX>_ITER_RETRY` describes both), `rx_iter`,
`PcrecEntry` and `PCREC_ENTRY_PUBLIC_N` `[r1 fam-1]`.

**Elsewhere, in the build commit** `[r1 fam-3, fam-S]`:
- plan.md `[FINDALL-NEXT]`: the next-line is rewritten to name this stage I4 (revision 3's
  numbering: I2 the kit's `st`, I3 `pair-hits`, I4 `next_n` + `RX_FOREACH`), to record the
  callback entry as DISSOLVED by `RX_FOREACH`, and to correct the row title's "iterator /
  callback entry".
- decisions.md D171: a gloss that "`next_n` noted for I2" means the stage revision 3
  numbers I4. The decision text itself is not edited.
- `src/gen/CLAUDE.md` (emit_iter.c's role), `tests/findall/CLAUDE.md` (the arms),
  `docs/dev/abi_changelog.md`, and the bench relay for main. pcrec-bench's shim could time
  `next_n`/`RX_FOREACH` as a find-all form, through `inbox_from_pcrec.md` (D78) and main's
  call.

---

## 7. Stages (revision 3's numbers, kept) `[r1 fam-3]`

| stage | what | abi |
|---|---|---|
| **I2** (rev 3, unchanged) | R17-b″: the kit's ITER form, `st` and S, `PCREC_ITER_LAYOUT` 3 → 4, S936/S937 | the kit's abi event, unchanged from rev 3 §1.3 |
| **I3** (rev 3, unchanged) | `pair-hits` | one |
| **I4** (this note) | `next_n`, `__one`, `RX_FOREACH`, `rx_info.next_n`; the §5 arms and drivers; S1309-S1320; the spec hunks | one (84 or next) |
| **I4-time** | §4's cell (after §4.1's objdump), queued after I4's `make test`/mech are green | none |

Stage numbers name stages, not their order. I4 lands first: Frank's build go
(2026-10-21) names it, under the name "I2" the manager's record used. Revision 3 §6.9's
I4 row ("`next_n`, if the parity slot filed it; its trigger is its arm beating `I` on a
re-run") is discharged by D171 and the parity slot's `N64` result: the trigger fired on
c3-4k R2. Revision 1 of this note renamed the stages; that rename is withdrawn, and the
plan and D171 are aligned at the build commit (§6).

---

## 8. The sibling-of-a-family lens

**The entry family.** The exported entries form a small grid. On one axis is the operation
(search, match, match_caps, next). On the other is the binding of working storage: a
parameter on the `_in` siblings, a SETTER on the iterator (`<prefix>_iter_buffers`, which
dissolved `_next_in` before it existed). `next_n` adds a COUNT axis, on the iterate
operation only. It is not a new entry and not a new row `[r1 fam-1]`: it is a second
controller emitted by the `iterate` row's one emitter over the same static part. **What
simplifies:**
1. The batch design and its second delivery path are deleted (§1.2): a struct field set,
   a setter, an option bit, two static parts, a row column, a stage, four sabotage labels,
   two parity arms and a conditional section.
2. The callback entry is DISSOLVED `[r1 fam-S]`: the macro is the hidden-loop form, so no
   per-match callback entry is designed.
3. `_next` is I1's body under a new name, so there is no fold to predict and no fallback
   copy (§2.3) `[r1 fam-2]`.
4. "Batching is identical to K = 1" stops being a proof obligation, because it is the
   definition.

**The family that IS growing dispersed: entry pointers in `rx_info`.** `next` (I1) and
`next_n` (I4) are the only entries reachable through the record. `search`, `match` and
`match_caps` are not. A generic caller can iterate an artifact it cannot search. That is
the [V-E] entry-pointer struct and `[RXINFO-REMODEL]`'s "entries" section, both under
`[IFACE-PUSH]`. This note does NOT add `search` (no caller asked; Frank: build what is
needed). The two pointers are hand-written appended members, the D76 ritual. The general
form, the record's pointers derived from an "rx_info slot" column of `entry_rows[]`, is
filed as U-I2-9 with its trigger `[r1 fam-5]`.

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
SMT sibling peaked at 78.6% in launch 5); §4's re-queue rule exists for that reason
`[r1 chk-1]`. Ratios are throughput over whole find-alls (dependent calls, each STEP's `lo`
from the last). §1.1's derived column divides medians of different arms and carries no
IQR `[r1 chk-4]`. What could flip a decision:
- **The twin's `N64` was spans-only** (`mktwin.py`'s `_next_n` copies `c[0]` into one pair
  per entry). Here the entries hold full captures, written in place with no copy. On DFA
  cells (NCAPS = 1) this is the same write. On c4 (VM, NCAPS = 2) the twin copied 2 words
  and this design copies none. The prediction is "no worse", and §4's c4 gate checks it.
- **R1 vs R2.** The gain is largest through the PLT (c3-4k R2 0.74 vs R1 0.84 against `I`).
  The macro calls through a POINTER (`info->next_n`), neither R1's direct call nor exactly a
  PLT stub. The `I_info` diagnostic measures the pointer's per-call cost. If it is ≈ 0, the
  macro is still justified by R2-like deployments (shared objects), but the c1/c4
  neutrality would then be the whole story on static links. That is a reported fact, not a
  gate. Gate 3 (§4) is set on R2 cells for this reason.
- **Zen 1** (the bench box) has costlier indirect branches than Zen 4. A bench run on the
  targeted hardware is the official verdict (D144 add. 4), via main.

### 9.2 The independent control — RELEVANT

§5.1: `G` (libpcre2) is the semantic control and shares no source. The new arms' expectation
is `I`, which is legitimate because their new code is only the delivery layer, and they also
report against `G`. §5.2: python `re`, libpcre2 twice (gstart, and entry_shape's iterator
arm `[r1 chk-5]`). §5.3: `_next`'s identity with I1's is checked against the I1 compiler's
output, not this compiler's. K35: `MIN_SPLIT_RETRY`, the `Fcount` floor and every §5.4 reach
count are counted by the driver from the struct and the call wrapper. They are not derived
from the code under test's own output format. `Fcount`'s expectation is a simulation of the
fills over `I`'s match count, not the macro's own counter. [MECH-REACH]: every row in §5.4
names a witness and a counted reach, and a zero reach fails the section.

### 9.3 What moves when data is regenerated — RELEVANT ONLY AS THE ABI EVENT

This stage adds no table, calibration or generated file. The one constant set (1, 64,
`RX_FOREACH_PAIRS` 256) is caller-side text. Changing a value moves the shared block's bytes
(an abi event, D76) and no answer. The batch sequence is stated as unspecified in the spec
(§6), so tuning it later is not a contract change. The abi event's readers are §6.

---

## 10. UNLOCKS (each with its trigger)

| id | unlock | trigger |
|---|---|---|
| U-I2-1 | `next_n` binds the VM run state once per CALL, not per STEP (the fast-tier stack buffers, then the deep re-run for the failing step only); the header test hoisted with it | §4's `F` loses or merely ties `I` on c4 (VM) while winning on DFA cells |
| U-I2-2 | a per-artifact `<PREFIX>_FOREACH(it, m)` calling `<prefix>_next_n` DIRECTLY, with NCAPS a constant | `I_info` shows the pointer call costing more than the A/A floor per fill on a dense cell, AND a caller who has the header asks |
| U-I2-3 | `pcrec --emit-abi-header`: the shared block alone, for a caller with records but no artifact header (an [ART-MGR] loader) | the first such caller |
| U-I2-4 | `<prefix>_search_n` (many subjects per call) or a count on other entries | a bench cell where the per-call cost of `_search` is a measured share (the many-small-subjects shape) |
| U-I2-5 | `search`/`match` pointers in `rx_info` (the entries section) | a third entry pointer requested: then all of them move in `[IFACE-PUSH]` (§8) |
| U-I2-6 | hoisting variable resolution into bind (I1 §12 left it per search; it needs resolved state in `rx_iter`) | a var-bearing find-all cell where resolution is a measured share. It rides I2's layout event if it arrives first |
| U-I2-7 `[r1 sem-7]` | an `rx_info` LAYOUT number separate from `abi`, so a record from another build whose layout matches can be read (the macro's gate would compare it instead of `abi`) | the first cross-build record holder: an [ART-MGR] loader, or U-I2-3's caller |
| U-I2-8 `[r1 sem (a)]` | `RX_FOREACH_IN(info, it, f, m)` over a CALLER-declared `rx_foreach`, so a loop can stop and later resume with its buffered matches | the first caller who needs to stop and resume a batched loop. NOT built in this stage |
| U-I2-9 `[r1 fam-5]` | an "rx_info slot" column in `entry_rows[]`: the record's entry pointers and their initializer lines come from rows, not hand-written members | a third hand-written `rx_info` pointer, or [V-E] |
| U-I2-10 `[r1 fam-S]` | retire `match_api.md` §3.1.3's hand loop as a documented find-all and make `_next_pos` internal | `[IFACE-PUSH]`, or a user report of the loop's divergence from PCRE2's iteration |

The `U-I2-n` ids are kept from revision 1 because the panel cites them; they belong to this
stage (I4).

---

## 11. Questions — settled (manager's call with the panel, Frank may reverse)

All three critics agreed with each leaning. The manager settled them; each is recorded here
in plain words so Frank can reverse any of them.

**Q1. A pattern with very many capture groups. SETTLED: refuse with the iterator's error
code.** The macro's buffer is a fixed 4 KiB on the stack. It holds 64 matches when a
pattern has up to 3 capture groups, fewer as groups grow, and not even one past 255
groups. Above that, `RX_FOREACH` ends at once with `PCREC_ERR_ITER`. The caller raises the
buffer with one `#define`, or calls the artifact's own entries with a buffer they size. A
variable-length stack array was rejected: it would make the stack use depend on a pattern
the caller may not see.

**Q2. Checking that the record matches the header. SETTLED: one compare per loop, never per
match** `[r1 fam-4]`. The macro exists for code that holds an artifact's record without
that artifact's header, so the record may come from a different pcrec build than the header
the macro was compiled with. The compare is an all-or-nothing gate: any difference in the
version number refuses, even where the two layouts happen to agree. It is correct (it never
calls through a wrong offset) and loud (the iterator ends with its error code). It makes no
lasting promise that records cross builds; that would be U-I2-7's layout number. And it is
required for safety in the other direction too: a newer header reading an older record
would read `next_n` past the end of a struct that has no such member. It is not a check on
the caller's calls, which Frank does not want.

**Q3. Leaving the loop early. SETTLED: an early break skips the fetched matches, and the
spec says so.** The macro fetches matches ahead in batches, so a caller who breaks out has
had some matches fetched that they never saw (none at a batch end, at most `j − 1` while
the batches double, at most 63 after). The spec states that an iterator given to
`RX_FOREACH` is finished when the loop exits, that `it.rc` is meaningful only after a loop
that ran to its end, and that calling `_next` on it afterwards is undefined. No rewind
code. A caller who wants to stop and resume uses `_next` (or, later, U-I2-8).

**Q4. Withdrawing the internal batch for good. SETTLED: withdrawn, and the callback entry
dissolved.** The October 14 ruling put batching inside the iterator (it caches results and
hands them out one per call). The parity run measured that slower on every dense cell, and
the macro puts the cache on the caller's side, where calls are actually removed. The
internal version is withdrawn entirely (it was never built), the macro is how batching is
offered, and the plan row's "callback entry" is recorded as dissolved by it.

**Also the manager's call, Frank may reverse: the doubling starts at 1, not 4** (§3.3).
Frank's charter said "4 → 64". Starting at 1 means a caller who stops after a few matches
pays for no search it does not see, and a caller who reads the whole subject makes about two
more calls (70 instead of 68 on 4,096 matches).

---

## 12. Revision 1's attack list, and where each item landed

| rev 1 item | landed |
|---|---|
| 1. c6 and the guessed cause | still a guess; fam-2's one body removes the twin's two-copy shape by construction; §4.1 H2 states the loop's shape on that route; c6 stays in gate 2 |
| 2. "`_next` folds to I1's code"; is the fallback a second mechanism? | dissolved by fam-2: `_next` IS I1's body (§2.3); chk-8's compare is the control (§5.3) |
| 3. the macro's text and warnings | sem-6 (C99, identifier, `-Wcomma`) in the spec; the compile matrix records the warning set (§5.3) |
| 4. k = 0 inertness | kept; inert in every state, tested on FRESH, BOUND and ENDED (chk-7, §5.1, S1313) |
| 5. holding the new arms to `I` | kept, with `G` beside it; chk-5 adds libpcre2 to entry_shape's arm |
| 6. the drivers' oracles | kept for encseam and gstart; entry_shape changed (chk-5) |
| 7. does anything shipped promise the batch fields? | no finding from the panel |
| 8. the rx_info pointer family | fam-5 → U-I2-9 |
| 9. unlocks | sem-7 → U-I2-7, sem (a) → U-I2-8, fam-5 → U-I2-9, fam (b) → U-I2-10 |
