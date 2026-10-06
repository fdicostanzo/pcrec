# A07 capability_doubled_word — blind review (reviewer rvA07a)

Artifact: `\b(\w+)\b\s+\1\b`, VM engine with captures (backreference), pin
57db5152, abi 62, gcc-16 16.2.0 on the Mac M1. Cell: the bench's
large-subject-throughput find-all over t-64k / t-256k / t-1m.

## 1. What the artifact does, as read

**Subjects.** Log/code-like ASCII text: ~78% of bytes are `\w`, average word
4.4 bytes, mostly single spaces between words; 140 / 519 / 1909 matches in
64 KiB / 256 KiB / 1 MiB. So the find-all is almost entirely FAILED attempts
(about one match per 550 bytes) and the restart cost per match is irrelevant.

**Search loop (`rx_search_run`).** Start set = a 256-byte table equal to `\w`.
Skip non-`\w` bytes, then for EVERY `\w` byte: an out-of-line call to
`rx_match_anchored` (not inlined: it has 4 other callers and computed gotos),
then a chain of 5 compares on the result code, `rx_reset_for_next_attempt`
(trail unwind), `++`, rescan. That is ~0.77 calls per subject byte.

**Attempt (`rx_match_anchored`).** A goto-threaded backtracking VM:
- `rx_L0`: `\b` at the start (two 32-byte-bitmap bit extractions). At an
  inner-word byte both sides are `\w` and the attempt fails here, before any
  side effect — that is ~78% of all calls.
- `rx_L2/L4`: trailed SETs (group-1 pending, span low), the `\w+` span,
  clamped one byte short of the window end (a min-remaining prune: `\s+`
  needs a byte).
- `rx_L6`: PUSH a give-back frame (`rx_L7`), then `rx_L5` trails group 1
  start/end, `rx_L3` `\b`.
- `rx_L8/L10`: trailed SET, the `\s+` span, PUSH a give-back frame
  (`rx_L11`).
- `rx_L9`: `rx_span_match` (inlined) compares the reference; work charged.
- `rx_L12`: final `\b`, accept.
- `rx_fail`: pop, step-budget decrement, trail unwind, `goto *label`.

On a failed word-start attempt (the common case) the backreference fails,
then the VM backtracks: `\s+` gives back k-1 times (each retry runs the
backreference against a `\s` byte), then `\w+` gives back L-1 times (each
retry re-trails group 1 and re-tests a `\b` that cannot pass). About 0.89
pops per subject byte, each with a trail unwind.

**asm.** Every run counter lives in memory: the slot stores are `ptrdiff_t`
and `resume_depth`/`trail_depth` are `size_t` (aliasing-compatible), so
every SET/PUSH/pop re-loads and re-stores `[x1,88]`, `[x1,96]`, `[x1,104]`
(55 memory ops through `run` in the 302-instruction function). Class tests
are 6 instructions each (ldrb, lsr, and, ldrb, asr, and).

**Setup/teardown.** `rx_run_state_init` once per search call (7 slots, two
budgets) and stack buffers (3 frames, 6 trail entries) that are never
initialized — cheap, and paid only ~1900 times per MiB. Not a lead.

## 2. Leads

All six are sealed at r1, identity PASS plain and under ASan+UBSan (3
subjects, 0 corpus cases, 3000-case battery, block 16; 14915 cases, 79700
transcript lines over S M C SI MI CI N V + find-all F/FC FSI; libpcre2 10.48
sample 1500/0 disagreements). **Timing: scratch timing owed for every lead**
(see §4). The deterministic work counts below are computed from the subjects,
not timed.

### L1 — start at word starts only (control-flow)
The attempt's first op is `\b` and the start set is `\w`, so a `\w` byte
preceded by `\w` can never begin a match, and failing there has no side
effect (the `resume_depth == 0` return is before the step decrement). Twin:
the start scan also requires the predecessor to be non-`\w`; after a failed
attempt (always at a word start) skip the rest of the word, then the gap.
Calls drop from ~0.77 to ~0.18 per subject byte (809,635 -> 184,595 on t-1m).
The `\b` reads `subject[p-1]` even before `search_from`, and so does the
filter (a mid-word `search_from` is covered by the battery: see the ctlskip
control under L4). Patch `L1.r1.patch`, 12 lines.

### L2 — the two span give-backs are dead (algorithmic)
A shorter `\w+` leaves `\w` on both sides of the `\b` after it; a shorter
`\s+` puts `\1` (non-empty, all `\w`) against a `\s` byte. Twin: delete the
two `RX_PUSH` lines — the spans become possessive (PCRE2's
auto-possessification would do the same at compile time). The attempt
function shrinks from 302 to 248 instructions; ~0.89 pops per byte vanish.
**Identity pitfall:** the step budget is charged per backtrack, so the twin
spends fewer steps; a search that would exhaust the 500M budget can answer
instead (the repair direction the spec allows for start-set proofs;
unreachable here: ~1M steps per MiB search). Patch `L2.r1.patch`, 4 lines.

### L3 — the attempt as straight-line code (redundant-work)
Given L2 the attempt has one path, so the VM machinery is pure overhead.
Twin: word-start test, word span (same clamp), `\b` by the stop byte, `\s`
span, `rx_span_match`, final `\b`; capture slots 2/3 written once on accept;
work charge kept. Slots 4-6 are internal and never reported.
Revision story: my first draft (never sealed) guarded only `p < window_end`
and read `subject[len]` for a word starting on the last byte. The sealed r1
uses `word_start + 1 >= window_end`. A deliberately re-broken control
(`ctlclamp`, uncounted) PASSES plain identity and FAILS under `--san` — the
answers were identical, only ASan saw the over-read. Patch `L3.r1.patch`.

### L4 — the search walks words, attempt inline (loop-structure)
L1 + L3, fused: the search loop scans to a word start, measures the word and
the `\s` run, compares the reference, and on failure resumes at the end of
the `\s` run (bytes inside the word are not word starts; `\s` bytes are not
in the start set). One pass over each byte, no call per word, no
result-code chain, no reset. Mid-word `search_from` is pre-skipped; the
control `ctlskip` (L4 without the pre-skip, uncounted) FAILS identity with
81 differing lines, so the battery reaches that edge. Same steps pitfall as
L2. Patch `L4.r1.patch`.

### L5 — byte-table class tests (data-layout), on top of L4
A 256-byte table (bit 0 `\w`, bit 1 `\s`) generated from the two bitmaps:
a load and a test instead of the 6-instruction bit extraction. Measured on
top of L4 because there the per-byte class loops are the whole hot path; on
the original the attempts dominate. The artifact already carries a 256-byte
`\w` table (`rx_start_set`) next to the bitmap for the same set. Patch
`L5.r1.patch`.

### L6 — run counters in locals (compiler-hint), on the ORIGINAL VM
The general VM lead: copy `resume_depth`, `trail_depth`, `steps_left`,
`work_left`, the stack/trail pointers and capacities into locals for the
attempt and write them back on every return (`RX_RET`). The asm loses the
per-SET/PUSH/pop counter traffic (counters loaded once at entry, stored at
each return). Same operations in the same order, so no budget pitfall.
Patch `L6.r1.patch`.

## 3. Ideas checked and rejected

- **Find-all restart cost** (`rx_run_state_init`, stack buffers, the
  search-from bounds check): ~1900 searches per MiB; negligible.
- **`rx_span_match`'s per-byte `at + i >= n` check**: runs once per word
  start and nearly always fails on the first byte; not hot.
- **The 5-compare result chain and `rx_reset_for_next_attempt` per failed
  attempt**: real waste, but L1 cuts their count ~4x and L3/L4 remove them;
  not worth a separate lead.
- **A required-byte / literal prefilter**: the pattern has no literal.
- **Skip ahead by the reference length after a failure**: wrong — the next
  word can begin right after the `\s` run; L4's resume at the run's end is
  the maximal sound skip.
- **memchr / word-at-a-time scanning of the gaps**: excluded (SIMD /
  SWAR-over-wide-registers rule), not attempted.
- **The `\w+` clamp at window_end - 1**: looked like an off-by-one, is a
  correct min-remaining prune; kept (and it is the L3 pitfall).

## 4. Timing

The Mac refused timing both times I tried: at 00:28 because another
reviewer held `build-artrev/.timing.lock`, and at 00:44 because
`worktrees/.mac-suite.lock` existed (load1 was 12.35). At that point the
manager ruled that timing would not open tonight and that a later lane will
time these twins. No override flag was used, and no timing ran outside the
harness. All leads: **scratch timing owed**.
Expected order (from work counts and asm, NOT measured): L4/L5 >> L1 > L3 >
L2 > L6 > null.

## 5. Disclosure (injected context)

The session-root CLAUDE.md and the memory index were injected before I
started. What may have influenced leads: the memory line about
"general mechanisms, not special cases" and "decisions as first-match
tables" nudged me to add L6 as a general VM lead rather than only
pattern-specific twins; the CLAUDE.md mention of START-SET (abi 62) and the
spec's start-set paragraph framed L1 as a start-set refinement. The memory
title "suspect tuning constants" made me check the `RX_UNROLL_K 8` stamp
(unused in this artifact's code; no lead). Nothing else in them names this
artifact or its emitter. One procedural slip: I ran a single `ls` on the
main checkout's `worktrees/.mac-suite.lock` path (outside the cell) to see
whether the suite lock was held; it does not reveal source or design, and I
did not repeat it.
