# capability_doubled_word — reviewer rvA07b (dual-review pilot, B side)

Pattern `\b(\w+)\b\s+\1\b`, VM backtracker with captures, find-all over
word-dense text. Scratch (Mac) verdicts only; see confirmed.md for Linux.

## Waste patterns, how to spot them, the twin idea

### 1. Leading assertion not folded into the start filter
- **Spot it**: `rx_search_run` skips with `rx_start_set[256]`, then calls
  the matcher, whose FIRST label (`rx_L0`) tests an assertion (`\b`) that
  needs the PREVIOUS byte. If the start set is a class C and the assertion
  is `\b`, every C byte preceded by a C byte is a guaranteed fail. Count
  start-set hits vs. real candidates on the subject (here 810k vs 185k per
  MB).
- **Twin**: a start skip that tests the predecessor too ("skip the rest of
  the current C run, then skip non-C").
- **Why safe**: the skipped attempt fails at the first label with
  `resume_depth == 0` -> `return -1` before any budget decrement, frame or
  slot write. Check that in `rx_fail` before claiming it.
- **Scratch**: -20%.

### 2. Give-back frames that can never succeed ("possessive by disjointness")
- **Spot it**: a greedy span loop (`while (... bitmapK[...]) cursor++`)
  followed by `RX_PUSH(&&rx_Lnn, cursor)` and a resume label that does
  `cursor -= 1; goto <span check>`. Then look at what FOLLOWS the span: if
  it is `\b` and the span class is the `\b` class, a shorter span puts the
  cursor between two class bytes -> `\b` false. If it is an atom whose first
  byte is in a class disjoint from the span class (here `\s+` then `\1`
  where group 1 is `\w+`), a shorter span leaves a span-class byte where the
  atom must start -> fail at offset 0. Every failed attempt then pops
  len(span) dead frames, each re-pushing and re-trailing.
- **Twin**: delete the push and the resume label.
- **Scratch**: -45% alone; the biggest lead here.

### 3. Trail with no reader
- **Spot it**: `RX_SET` = `RX_TRAIL` + store. Once no frame can resume (after
  #2), the trail only feeds `rx_reset_for_next_attempt`. List each slot's
  first READ in the matcher and check a write precedes it in the same
  attempt (here slots 6,4,2,3,5 all do); reported slots come from a
  successful attempt only.
- **Twin**: `RX_SET` -> plain store. +8 points on top of #2.

### 4. Out-of-line matcher
- **Spot it**: `bl _rx_match_anchored` inside the search loop in the `.s`;
  the matcher takes label addresses (`&&rx_L7`) so gcc keeps it out of line.
  Once #2 removes every `&&label`, `rx_fail` can only `return -1`.
- **Twin**: `rx_fail: return -1;` + `static inline
  __attribute__((always_inline))`. Combined #1-#4: -72%.

### 5. Re-reading what the spans just walked
- **Spot it**: after a failed attempt the search loop restarts at
  `attempt+1` and re-skips the run the matcher's first span already
  classified.
- **Twin**: an internal out-parameter "next possible start" set from the
  span cursors (only past positions proven dead: inside the `\w` run a
  `\b` fails; inside the `\s` run the byte is not in the start set).

### 6. Bitmap class tests in per-byte loops
- **Spot it**: `((bitmap[c>>3] >> (c&7)) & 1)` in a span loop; in asm
  `lsr / and / ldrb / asr / and` per byte. Often a 256-byte table of the same
  class already exists in the artifact (`rx_start_set`).
- **Twin**: generate 256-byte tables from the bitmaps (derived size, not a
  tuning constant).

## Identity pitfalls
- The harness rejects a seal if the arm dir has ANY stray file (a
  `patch` `.orig` backup cost me a counted revision). Edit in place.
- Removing frames/trail changes when a budget or an undersized caller
  buffer gives up — only LATER, never earlier (limits.md; match_api 10.3
  says a FRAMES give-up is retryable). Neither is reachable by the battery
  at default capacities; state the argument in the lead.
- `rx_match`/`rx_match_caps` share the matcher: an L1-style "the start is
  known good" shortcut must not leak into the anchored entries (they can be
  called mid-word).
- A sabotage control (`--control`) that skips the word the search STARTS on
  failed identity immediately: the battery does cover start positions.

## Abandoned / rejected
- Hoisting the backreference compare's bound check: tiny, and its return
  value feeds the work charge.
- Dropping the redundant `\b` tests after the spans: predictable branches.
- Branch-free run-end detection: the remaining cost is ~3 mispredicts per
  word at run ends; would need a table-driven state walk, close to SWAR.

## Scratch verdicts
L1 WIN -20%, L2 WIN -45%, L2+L3 WIN -53%, L1+L2+L3+inline (L4) WIN -72%
(one Mac run, null within 1%). L5 and L6: identity PASS, scratch timing
owed (the gate never opened again that night).
