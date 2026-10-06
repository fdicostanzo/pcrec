# A07 capability_doubled_word — blind review (reviewer rvA07b)

Pattern `\b(\w+)\b\s+\1\b`, VM engine, captures (group 1), pin 57db5152,
abi 62, gcc-16 16.2.0 -O2 on the Mac M1. Cell: the bench's
large-subject-throughput find-all over t-64k / t-256k / t-1m. All numbers
below are SCRATCH (Mac, loaded box); they steer and are never reported.

## 1. What the artifact does, as read

**Find-all driver** (`bench_t.c`): `rx_search(s, n, pos, caps)` from the
previous match end; 1,909 matches on t-1m, so per-call setup
(`rx_run_state_init`, the stack `rx_run_buffers`) is negligible.

**`rx_search_run`** (artifact.c:278): skip bytes not in `rx_start_set`
(a 256-byte table == `\w`), then loop: call `rx_match_anchored` (an
out-of-line call — artifact.s:447 `bl _rx_match_anchored`), check five
give-up codes, on failure `rx_reset_for_next_attempt` (unwind the trail),
`attempt_position++`, skip non-start bytes again.

**`rx_match_anchored`** (artifact.c:161), a computed-goto backtracker:

- `rx_L0`: `\b` (two bitmap lookups).
- `rx_L2`/`rx_L4`: trailed `RX_SET` of the pending group start and the span
  low mark; `\w+` as a greedy span clamped to `window_end-1` (something must
  follow).
- `rx_L6`: push a give-back frame (`rx_L7` retries one byte shorter).
- `rx_L5`: trailed set of group 1 start/end; `rx_L3`: `\b`.
- `rx_L8`: `\s+` greedy span; `rx_L10` pushes a give-back frame (`rx_L11`).
- `rx_L9`: `\1` through `rx_span_match` (byte compare, per-byte bound
  check), charging the work budget with the compared length.
- `rx_L12`: `\b`; accept.
- `rx_fail`: pop a frame (step budget), unwind the trail to its mark,
  `goto *label`.

Class tests everywhere are `(bitmap[c>>3] >> (c&7)) & 1` over 32-byte
bitmaps (`rx_class_bitmap0` = `\w`, `rx_class_bitmap1` = `\s`).

**Subject shape** (t-1m): log/code-like English text; 809,635 `\w` bytes
(77%), 184,595 words (avg 4.4 bytes), 118,706 words followed by `\s`.

## 2. Where the time goes (as read, before timing)

1. ~810k start-set hits per MB, but the leading `\b` can only pass at a
   word START (184,595). ~625k calls per MB are a call + `\b` + fail +
   reset. (L1)
2. Every word-start attempt that fails (almost all) unwinds BOTH give-back
   frames byte by byte: ~931k dead pops per MB, each re-pushing a frame,
   setting two trailed slots and unwinding them. None can succeed: `\w` and
   `\s` are disjoint and the spans are followed by `\b` / `\1`. (L2)
3. Five trailed slot writes per attempt plus the reset unwind, protecting
   values no later code reads. (L3)
4. The call boundary and the `run->` state round-trips. (L4)
5. After a failed attempt the start skip re-reads the word the spans just
   walked. (L5)
6. Bitmap class tests: 6 dependent ops per byte. (L6)

## 3. Leads (details in leads.tsv; patches next to this file)

Identity for every sealed revision: PASS, zero differences, over the three
subjects + 3,000 battery subjects (14,915 cases, 79,700 transcript lines,
shapes S M C SI MI CI N V + find-all F/FC FSI), libpcre2 10.48 sample
1,500 OK, and again under ASan+UBSan. `--corpus` finds 0 cases (as the
cell recipe says).

Sensitivity control (uncounted, `--control`): `sabL1`, an L1 that skips a
word even when the search STARTS at its first byte. Identity FAILED it at
once (680 differing transcript lines, first at a battery subject searched
from 0). The battery does exercise the start-position logic L1/L5 touch.

### L1 — fold the leading `\b` into the start filter (algorithmic) — rev 1

`rx_next_word_start()`: inside a word, skip its `\w` bytes; then skip
non-`\w` bytes. Both start skips in `rx_search_run` use it. Correctness: a
skipped `\w`-after-`\w` attempt fails at `rx_L0` with no frame, no slot
write, no budget charge. Scratch timing run 001: **-20%** on all three
subjects (WIN past null/IQR).

### L2 — drop the dead give-back frames (redundant-work) — rev 1

Remove `RX_PUSH(&&rx_L7)`/`rx_L7` and `RX_PUSH(&&rx_L11)`/`rx_L11`.
Correctness: a shorter `\w+` leaves `\w|\w` at the cursor, `\b` false; a
shorter `\s+` leaves `\s` where `\1` (non-empty, all `\w`) must start,
`rx_span_match` fails at offset 0 charging 0 work. Only the step budget and
the frame capacity saw those retries; their give-ups can only move later.
Scratch 001: **-45%** alone (the biggest single lead).

### L3 — untrailed slot writes (redundant-work) — rev 1, on top of L2

`RX_SET` becomes a plain store. Every slot is written before it is read
within an attempt; only a successful attempt's slots 2/3 are reported.
Scratch 001: **-53%** (L2+L3), i.e. ~8 points over L2.

### L4 — inline the now-straight-line matcher (call-boundary) — rev 2

L1+L2+L3, `rx_fail` reduced to `return -1` (no frame can exist), matcher
`static inline __attribute__((always_inline))`. Rev 1 was REJECTED by the
harness for a stray `artifact.c.orig` (my patch tool's backup) — a counted
revision with no code difference; rev 2 is the same code. The compiled
search loop becomes a tight scan with the spans inlined and the state in
registers (asm read). Scratch 001: **-72%** on all three subjects.

### L5 — restart after the failed spans (algorithmic) — rev 1, on top of L4

The matcher reports, through an internal out-parameter, the furthest
position proven dead (the `\w+` span end, then the `\s+` span end); the
search loop restarts the word-start skip there instead of at attempt+1.
Default is attempt+1 (the original progression), so `rx_match`/`_caps`
are untouched (they pass a dummy).

### L6 — byte tables instead of bitmaps (data-layout) — rev 1, on top of L5

Two 256-byte tables generated bit-for-bit from the bitmaps; every class
test becomes one indexed load.

### Timing record (scratch, Mac)

- Run 001 (00:27, the gate happened to be open): orig, orig2, null, L1-L4,
  11 rounds, all three subjects. null within 0.04-1.1% of orig (noise
  floor); orig2 within 0.5%. Medians, ns/B, t64k / t256k / t1m:
  orig 9.41 / 9.28 / 9.30; L1 7.60 / 7.43 / 7.39 (-19 to -21%);
  L2 5.21 / 5.09 / 5.09 (-45%); L3 4.42 / 4.41 / 4.41 (-53%);
  L4 2.51 / 2.63 / 2.63 (-72%). All WIN past max(null dev, IQR).
- L5 and L6 (sealed and identity-verified after run 001) were never timed:
  four tries for orig,null,L4,L5,L6 were refused (00:33 load gate, 00:48
  suite lock, 01:03 and 01:22 load gate, 01:42 suite lock); I stopped
  after 60+ minutes of cumulative refusals, as briefed. **L5 and L6:
  scratch timing owed.** No override flag was used; nothing unlogged was
  timed.
- Expectation for L5/L6 (unmeasured): L4's loop is now bound by
  data-dependent run-end branches (~3-4 per word) more than by
  instruction count. L5 removes one run scan per word (one
  mispredicting exit); L6 shortens each class test from 6 ops to 2
  (search-loop asm 331 -> 276 instructions). I would not be surprised if
  L6 lands in the noise and L5 shows a few percent.

### Iteration ledger summary

Counted revisions: L1 r1, L2 r1, L3 r1, L4 r1 (REJECTED, stray file) + r2,
L5 r1, L6 r1. Timing runs: one (001) covering L1-L4 rev 1/2. Uncounted:
null r1, control sabL1 r1 (identity FAIL as intended).

The leads stack (L3 on L2; L4 = L1+L3+inline; L5 on L4; L6 on L5); each
patch is against the pinned artifact. The confirmer should time each
cumulatively AND, if budget allows, L1 and L2 alone (as in run 001) so the
per-mechanism shares are visible: from run 001, roughly
start filter 20%, dead frames 45%, trail 8 pts more, inline ~19 pts more.

## 4. Ideas checked and rejected (not twinned)

- **Hoist `rx_span_match`'s per-byte `at+i >= n` check.** The compare
  almost always fails at byte 0 (different first letters), and the return
  value feeds the work charge, so a rewrite must reproduce `-i-1` exactly.
  Tiny gain, real identity risk: rejected.
- **`RX_PRUNE_CLAMP_SPAN`'s division.** `w_` is the constant 1; gcc folds
  it (no `udiv` in artifact.s). Not waste.
- **The redundant `\b` tests** at `rx_L0` (true after L1), `rx_L3` (equal to
  the span's stop reason) and `rx_L12` (the byte before is the last byte of
  `\1`, a `\w`). Each is a well-predicted branch and ~2 loads per word
  start, and the matcher is shared with `rx_match`/`rx_match_caps`, which
  need `rx_L0`. Not worth a lead slot.
- **Per-call setup** (`rx_run_state_init`, the 168-byte stack buffers, the
  five give-up compares): once per `rx_search` call, 1,909 calls per MB.
  Negligible.
- **`rx_reset_for_next_attempt` after L3**: trail_depth is always 0, one
  compare. Negligible.
- **A branch-free class-transition scan** to kill the remaining
  run-end mispredicts (the L5/L6 hot loop is mispredict-bound: ~3 run ends
  per word). Would need a table-driven multi-state walk; speculative and
  close to the SWAR line. Not tried.
- **Word-at-a-time skipping / memchr-style scans**: SIMD/SWAR, forbidden.

## 5. Disclosure (charter 3: spawn-time injections)

Injected before I started: the project CLAUDE.md (pcrec process rules,
situation index, mentions of DFA/VM engines, "prefilter", "memfn" search
kit, budgets/frames, abi bumps) and a memory index (one-line titles,
including "SIMD LAST", "suspect tuning constants", "decisions as
first-match tables"). What I believe influenced me:

- "suspect tuning constants" made me check `RX_UNROLL_K`/the clamp
  arithmetic for waste (nothing found) and label the L6 table size: 256
  entries is DERIVED (one per byte value), not a tuning constant.
- The CLAUDE.md's description of give-up codes and frames as retryable
  resources primed me to argue "give-up moves later" for L2/L3; I verified
  that argument only from `docs/spec/limits.md` and `match_api.md` §10.3
  inside the cell.
- Nothing in the injected text named this pattern, the span/frame shapes,
  or any of the six leads.

Process slip: L4 rev 1 was built with a diff written to `/tmp` (outside the
cell) and `patch`; the `.orig` backup got the revision rejected. The temp
file held only my own L1 diff and was deleted at once; later revisions
were built inside the cell.
