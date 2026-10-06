# capability_doubled_word (`\b(\w+)\b\s+\1\b`, VM + backref) — rvA07a

Scratch verdicts: NONE timed (the Mac refused timing all night: another
reviewer's timing lock, then load). Every lead below is identity-verified
(plain + ASan/UBSan) and "scratch timing owed". Work counts are computed from
the subjects, not timed.

## Waste patterns and how to spot them

1. **Start set wider than the first assertion allows.** Spot: the search
   loop's start table (`rx_start_set[256]`) equals a class C, and the first
   op of `rx_match_anchored` (`rx_L0`) is a `\b` test. Every C byte preceded
   by a C byte is called, fails at `rx_L0`, and pays the out-of-line call +
   the result-code compare chain + `rx_reset_for_next_attempt`. On text
   (~78% `\w`, 4.4-byte words) that is ~3/4 of all calls. Twin: also require
   the predecessor to be non-C; after a failed attempt skip the rest of the
   run. Sound because the `\b` failure happens before any SET/PUSH/budget
   charge. (Lead L1.)
2. **Give-back frames that can never succeed (missing auto-possessify).**
   Spot: a span loop followed by `RX_PUSH(&&rx_Lk, rx_span_cursor)` whose
   resume label just decrements the cursor; then ask what the NEXT op needs.
   If it is `\b` after a `\w` span, or an item whose first byte is disjoint
   from the span class (here `\1`, all `\w`, after `\s+`), every give-back
   fails. Twin: delete the PUSH. (L2.)
3. **A VM running a one-path program.** Once 2 holds for every span, the
   attempt has a single path; trailed SETs, frames and the unwind are pure
   overhead. Twin: straight-line rewrite, captures written on accept. (L3.)
   Then fuse it into the search loop and resume a failed attempt at the end
   of what it already scanned (here: the `\s` run after the word). (L4.)
4. **Run counters stuck in memory.** Spot in asm: `ldr/str [x1, 88/96/104]`
   (resume_depth, trail_depth, steps_left) around every SET/PUSH/pop. Cause:
   `slot_values` is `ptrdiff_t*`, the depths `size_t` — aliasing-compatible
   types, so every slot store clobbers them for the optimizer. Twin: locals,
   written back at every return. General to the VM shape. (L6.)
5. **Bitmap class tests in per-byte loops.** `(bm[c>>3] >> (c&7)) & 1` is 6
   instructions; a 256-byte table is 2, and the artifact often already
   carries a 256-byte table for the same set (the start set). (L5.)

## Identity pitfalls met

- **The span clamp.** The `\w+` span stops at `window_end - 1` (a
  min-remaining prune for the `\s+` after it). A straight-line rewrite that
  guards only `p < window_end` reads `subject[len]` when a word starts on the
  last byte. Plain identity PASSES that bug (answers equal); only `--san`
  FAILS it (control `ctlclamp`). Always run `--san`.
- **Mid-word `search_from`.** A word-start skip must still pre-skip when the
  search begins inside a word; the battery catches dropping that (control
  `ctlskip`: FAIL, 81 lines).
- **Step budget.** Removing dead backtracks spends fewer steps: a search that
  would give up on 500M steps can answer. Only the repair direction, and
  unreachable on these subjects (~1M steps/MiB), but say it in the lead.
- `\b` looks behind `search_from`; keep the lookbehind byte in any filter.

## Abandoned / rejected

- Restart cost per find-all match (init, stack buffers): ~1900 calls/MiB,
  negligible. `rx_span_match`'s per-byte bounds check: runs once per word,
  fails on byte 0. Literal prefilter: no literal. Skipping by the reference
  length after a failure: unsound (next word starts right after the gap).
  Word-at-a-time gap scanning: excluded by the no-SIMD/SWAR rule.
