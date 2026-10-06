# loglines_level_context (`\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|...)\b`, hybrid DFA prefilter + VM) — rvA09

Scratch verdicts: none timed (no timing that night). Every lead is identity-verified (plain and
ASan/UBSan) and "scratch timing owed". Effects are ordered from work counts.

## First: count DFA steps, not skip-loop bytes

On this artifact the forward prefilter DFA stepped **every byte**: 1.0M steps/MiB on all three
subject groups. That is despite an emitted state-0 skip loop and an after-level `stay` loop. The
skip loops key on ONE state's self-loop. The real "searching" set is a **two-state component**:
state 0 (after `\W`) goes to 29 (in a word) on a word byte, and back on `\W`. So the skip only
covers runs of two or more non-word bytes.

How to spot it in 10 minutes:
1. Dump the DFA rows with the most-common next state and its exceptions. A ~25-line Python
   script that regex-parses the `static const` tables works (A09 `tools/dfa_dump.py`).
2. Look for a set of states that map to each other on almost every class.
3. Compare that set with the state(s) the skip loop's `if (forward_state == K)` covers.
4. Instrument a scratch copy and count the step line against the skip line. If steps ≈ bytes,
   the skip is dead weight.

Any `\b(?:LIT|LIT)` start gives this {after-\W, in-word} pair. Any `.*`/`.{m,n}` middle under
a count-collapsed prefilter gives a second pair after the first literal.

## Waste patterns, twins, expected effect

1. **Component skip (L1/L2/L3).** Exits from {0,29} are the first bytes of the literals, read
   in state 0, i.e. at position 0 or after a `\W` byte.
   - Twin L2 (scalar): a table loop over the exit bytes, then a predecessor test.
   - Twin L1: jump to the next WHOLE literal at a word start, found with memchr on each
     literal's rarest byte. That byte is not necessarily the first byte; this artifact used
     `O`@3 for ERROR and `T`@2/@3 for FATAL/CRIT, two streams covering three literals. Verify
     with 2/4-byte compares, enter the DFA in state 0 there, and return 0 when no stream finds
     one.
   - Why the jump is exact: an incomplete prefix walk returns to the component with no accept,
     and a walk is all word bytes, so it cannot straddle a `\W` predecessor.
   - L3 is the same as L2 for the after-level pair (exit set `\n` + keyword first letters).
   - Expected: fail/syslog DFA steps 1.0M → 0 per MiB (L1).
2. **Reverse pass recovering a start the forward pass walked through (L4 r1).** The last time
   the forward DFA sat in the "whole first literal read" state before the accept marks the
   leftmost start. The after-literal region is entered only from there and left only by `\n` or
   death. Record `p - len(literal)` there; the last byte names the literal.
3. **VM re-proving the DFA's window (L4 r2/r3).** For a count-collapsed hybrid
   (`RX_VM_PREFILTER_LANG "count-collapsed"`), the window end is the first keyword after the
   start. Check the collapsed count yourself (here: gap ≤ 200), then report [start, end)
   without the VM.
4. **Frame per lazy position (L5).** This is rvA07a's one-path pattern. The lazy step pushes a
   frame that is always popped straight back. Drop the PUSH, keep its capacity check and the
   pop's `--steps_left`, and send the tail's failures to the step label.

## Identity pitfalls met (read these)

- **Harness identity uses only the stamped default buffers.** A twin that skips the VM must
  keep the VM's FRAMES give-up for `_in` callers with 0 frames or 0 trail. L4 r2 PASSED harness
  identity and was wrong on 284k calls of my capacity differential. Build orig and twin with
  shrunk `RX_STEP_BUDGET`/`RX_WORK_BUDGET` (sed the `#define`s in scratch copies) and drive
  `_search_in`/`_match_in` with 0/1 frames × 0/1 trail. A09 `tools/budget_*` does this.
- **Prefilter-start differential.** A start that is too EARLY is invisible to answers, because
  the VM just retries. It can also livelock `rx_search_run` (prefilter from s returns s-1,
  forever); the harness then fails only by a 15-minute driver timeout. Diff the prefilter's
  return and window START at every `search_from` against the original. Do it by including
  each arm's artifact.c in a wrapper TU with the exported names `#define`d apart (A09
  `tools/pfdiff_*`).
- **Exact count bounds need hand-made subjects.** The battery never produced a 200/201 gap.
  The off-by-one control PASSED until I added gaps of 199-202 for every literal pair.
- **Bounds on look-ahead verification.** A dropped `x+3<=n` passes plain and fails only under
  ASan, and only once a subject ENDS in a truncated literal (`...FAT`). The identity driver
  mallocs subjects to exact size, so add such endings.
- **Edge subjects pull weight.** A token soup made of literal fragments (`xERROR`, `ERRORS`,
  `CRITICAL`, `timed  out`, `0refused`, separators including `\n`, `\x00`, `\xe9`) caught two
  controls the battery missed.

## Abandoned / rejected

- **Tightening the per-step DFA loop.** It does not run once the component is skipped.
- **The `'e'` required-byte memchr per call.** Finds an `e` within about 15 bytes; negligible.
- **One memchr stream.** No byte is common to the three literals.
- **First-byte streams (L1 r1).** Three streams scan 3 MiB/MiB with more calls; superseded by
  rare-byte streams (r2).
- **VM run counters in memory.** Real, but the VM is about 2% of the work here.
- **Find-all restart.** About 200 calls/MiB; negligible, agreeing with rvA01 and rvA07a.
