# docs/dev/utf8_attrib_twin — the [OPT-HYB-RESEED] re-seed twin, packaged for the bench

Lane `reseedtwin`, 2026-09-27. `docs/dev/utf8_attrib.md`'s (A) rows 1/10/11
found ONE algorithmic defect (the VM hybrid's retry never re-seeds from its
prefilter without an MRL clamp) behind three of the twelve utf8@0.1 losses.
The bench dev cannot read pcrec's tree, so the reproduction has to travel as
self-contained text rather than as a diff against a checkout.

## Files

- `I-114.md` — the whole package: the pcrec pin (`a32bc86e`), the exact
  `pcrec` compile commands for the three patterns (`asr-lb-varwidth`,
  `asr-lb-neg`, `asr-lb-fixed`), the three hand-twin diffs INLINE (each
  8 lines — the same re-seed block `src/gen/emit_vm.c`'s `retry_win` already
  emits at the search entry, moved to the retry unconditionally), a
  self-contained find-all driver, a deterministic subject generator
  (Python, fixed seed, inline), the Mac scratch numbers (answer-identical
  on every cell; the SIZE of the speedup is subject-composition dependent,
  down to a measured 0.81x/0.90x SLOWER twin on two cells where the
  candidate byte is dense — read that section before citing a number), and
  what the bench should measure on x86.

Nothing here is built or run by `make`; the artifacts and binaries this
lane produced live in the session scratchpad and were never committed. A
reader who wants to re-derive them regenerates from `I-114.md`'s own
inline text at the pinned commit.
