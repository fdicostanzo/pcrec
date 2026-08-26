# [OPT-3] STEP 2 — the PRE-MULTIPLIED DFA transition table

Lane `srPremul`, 2026-08-26. Written BEFORE the code and committed first, on
`docs/design/two_tier_entry.md`'s model: this note is the shape of the change,
its rule, its sentinel, its bound and its failure modes. Frank ruled the design
on 2026-08-26 ("agree with solution"); what is decided *here* rather than there
is named as such in each section.

The measurement this implements is `docs/dev/opt3_dfa_scan_measurement.md`
(lane `srOpt3`, STEP 1). That memo is not restated below — §5 and §7 are its
load-bearing sections and are cited by number.

## 0. The answer in five lines

1. The DFA scan's cost is its loop-carried dependency chain, not its work
   (STEP 1 §5: 7 cycles of `lea, lea, movslq, load`; 10.7 cycles/byte measured;
   two independent streams nearly halve it).
2. Store `next_state * stride` in the transition table instead of `next_state`,
   so the emitted step is `state = table[state + class]` and the chain is
   `add, load`.
3. Every OTHER per-state table the loop consults on the hot path is then indexed
   by that same premultiplied value, so nothing on the chain un-multiplies.
4. The dead state becomes the reserved value `65535`, tested with a `cmp`
   against the loaded value — a predicted branch, not an input to the next load.
5. Measured by STEP 1 on a patched copy of the real artifact: **1.276x** on the
   bench's three throughput subjects, answer-identical over 40,469 answer lines
   across 91 subjects.

## 1. The rule

For a DFA whose transition table has `n` states and `ncls` byte classes:

- **Premultiplied form** (new default, when §7's bound holds): the table has
  `n * ncls` entries of type `unsigned short`; the entry at `[i * ncls + cl]`
  holds `tr(i, cl) * ncls`, or `65535` when `tr(i, cl)` is dead. The emitted
  state variable holds a premultiplied value throughout, and every emitted
  state CONSTANT (the start state, a skip state's guard, a seed cell, a view
  cell) is premultiplied at generation time.
- **Indexed form** (what pcrec emits today; retained above the bound and under
  `-fno-premul-table`): the table has `n * ncls` entries of type `short` holding
  `tr(i, cl)`, or `-1` when dead; the state variable holds a state index.

The two forms are the same machine. Nothing about the DFA changes — not the
states, not the classes, not the minimization, not the class map. This is a
representation change in the emitter and nowhere else: `src/ir/dfa.c` is not
touched, and no `Dfa` field is added.

## 2. The emitted step, both forms

Indexed (today, forward loop, `orig` with `ncls == 18`):

```c
    static const short rx_forward_next_state[4482];   /* -1 = dead */
    static const unsigned char rx_forward_is_accepting[249];
    int forward_state = 0;
    ...
        if (rx_forward_is_accepting[forward_state]) last_accept_position = scan_position;
        forward_state = rx_forward_next_state[forward_state * 18 + rx_forward_byte_class[subject[scan_position++]]];
        if (forward_state < 0) break;   // dead: no match can continue
```

Premultiplied:

```c
    static const unsigned short rx_forward_next_state[4482];  /* 65535 = dead */
    static const unsigned char rx_forward_is_accepting[4482];
    unsigned forward_state = 0;
    ...
        if (rx_forward_is_accepting[forward_state]) last_accept_position = scan_position;
        forward_state = rx_forward_next_state[forward_state + rx_forward_byte_class[subject[scan_position++]]];
        if (forward_state == 65535) break;   // dead: no match can continue
```

The loop-carried chain, `gcc -O2` on x86-64. **MEASURED on the emitted
artifact for the bench's own `orig` pattern, both forms compiled from the
shipped emitter** (`gcc -O2 -c`, `objdump -d`, 2026-08-26 — not predicted):

```
   indexed (17-instruction loop)              pre-multiplied (14-instruction loop)
4d movzbl (%rdi,%rax,1),%edx   LOAD 1     4d movzbl (%rdi,%rax,1),%edx   LOAD 1
51 movzbl (%rbx,%rdx,1),%edx   LOAD 2     51 movzbl (%rbx,%rdx,1),%edx   LOAD 2
55 lea    (%rcx,%rcx,8),%ecx   CHAIN      55 add    %ecx,%edx            CHAIN
58 lea    (%rdx,%rcx,2),%edx   CHAIN      57 mov    %edx,%edx            CHAIN (zero-extend)
5b movslq %edx,%rdx            CHAIN      59 movzwl 0x0(%rbp,%rdx,2),%ecx CHAIN + LOAD 3
5e movswl 0x0(%rbp,%rdx,2),%ecx CHAIN+L3  5e cmp    $0xffff,%ecx
63 test   %ecx,%ecx                       64 je     <exit>
65 js     <exit>                          66 mov    %ecx,%edx
67 movslq %ecx,%rdx                       68 add    $0x1,%rax
6a add    $0x1,%rax                       6c movzbl (%r12,%rdx,1),%edx  LOAD 4
6e movzbl (%r12,%rdx,1),%edx  LOAD 4      71 test   %dl,%dl
73 test   %dl,%dl                         73 cmovne %rax,%r8
75 cmovne %rax,%r8                        77 test   %ecx,%ecx
79 test   %ecx,%ecx                       79 jne    <top>
7b jne    <top>
```

| | indexed | pre-multiplied |
|---|---|---|
| scale state by stride | `lea (%rcx,%rcx,8),%ecx` (1) | — |
| add class | `lea (%rdx,%rcx,2),%edx` (1) | `add %ecx,%edx` (1) |
| widen to an index | `movslq %edx,%rdx` (1) | `mov %edx,%edx` (0-1; a 32-bit register move, eliminated at rename on this core) |
| load | `movswl 0x0(%rbp,%rdx,2),%ecx` (4) | `movzwl 0x0(%rbp,%rdx,2),%ecx` (4) |
| **chain** | **7 cycles** | **5 cycles** |

Two things in the measured listing that the prediction did not have, both
worth keeping:

- **The `mov %edx,%edx` is the 32-bit index being zero-extended for the
  addressing mode**, and it is there because the state variable is `unsigned`
  (32-bit) rather than pointer-width. It is a register-to-register move on a
  core with move elimination, so it is expected to cost nothing — but "expected
  to cost nothing" is a claim, and §13 measures a `size_t` state variable
  against the `unsigned` one rather than arguing about it. What the
  measurement must NOT do is take the `int` form: with a SIGNED state the
  `movslq` comes straight back and the transform buys nothing (§11).
- **The accept probe reads the NEW state, not the index** (`mov %ecx,%edx` at
  `0x66` before `movzbl (%r12,%rdx,1)`). Worth stating because the surrounding
  instructions make it look otherwise at a glance: gcc rotates the loop so the
  probe at the top of iteration N+1 is scheduled after the transition of
  iteration N, and it reuses `%rdx` — which held the OLD index one instruction
  earlier. Reading `is_accepting[state + class]` there would be a wrong answer
  on most inputs; the emitted code does not.

STEP 1 §5 measured the two chains end to end on `t-c`: 10.714 vs 7.751
cycles/byte, a 2.96 cycle/byte difference against the 2 cycles of chain the
table above removes. The remainder is the second-order effect the table cannot
show (the shorter chain leaves more of the ~2x spare issue width for the
off-chain accept probe and the loop's own branches).

**The accept flag is NOT fused into the table entry.** STEP 1 §5 measured that
variant (v2, 8.095 cycles/byte) and it is WORSE than premultiplying alone
(v1, 7.751): unpacking the flag puts an `and` back on the chain. The accept
probe stays a separate table read, off the chain, where the core absorbs it —
§5 measured the whole accept bookkeeping at 0.05 cycles/byte.

## 3. The dead-state sentinel

THREE candidates, and Frank's 2026-08-26 input added the third. The ruling
asked for the choice to be argued ON THE EMITTED INSTRUCTION SEQUENCE, so each
is stated as one, measured on the bench's own `orig` pattern (`gcc -O2`,
`objdump -d`) rather than predicted:

- **(a) a reserved value, `65535`, tested `state == 65535`** — CHOSEN.
- **(b) a self-mapping DEAD row appended at index `n`**, tested against its
  premultiplied value — rejected.
- **(c) `DEAD = 0`, with the states renumbered so the START state is 1** (its
  premultiplied value is `stride`), the dead row self-mapping at index 0 —
  Frank's input; rejected on the balance below, not on speed.

### The two sequences, side by side

Both were BUILT: (a) is what the emitter ships, (c) is a patched scratch copy
of the same artifact (`scratchpad/srPremul/meas/mk_dead0.py`, STEP 1's own
methodology — the transform renumbers every cell and every emitted constant,
prepends the dead row to the transition and accept tables, and rewrites the
two tests), **answer-gated at 91 subjects / 40,470 answer lines / 0
differences before any time was taken**.

```
   (a) DEAD = 65535, start = 0            (c) DEAD = 0, start = stride (18)
   16 instructions                        16 instructions
55 add    %ecx,%edx      CHAIN          5d add    %ecx,%edx      CHAIN
57 mov    %edx,%edx      CHAIN          5f mov    %edx,%edx      CHAIN
59 movzwl (%rbp,%rdx,2),%ecx CHAIN+LD   61 movzwl (%rbp,%rdx,2),%ecx CHAIN+LD
5e cmp    $0xffff,%ecx   (6 bytes)      66 test   %ecx,%ecx      (2 bytes)
64 je     <dead>                        68 je     <dead>
66 mov    %ecx,%edx                     6a mov    %ecx,%edx
68 add    $0x1,%rax                     6c add    $0x1,%rax
6c movzbl (%r12,%rdx,1),%edx  ACCEPT    70 movzbl (%r12,%rdx,1),%edx  ACCEPT
71 test   %dl,%dl                       75 test   %dl,%dl
73 cmovne %rax,%r8                      77 cmovne %rax,%r8
77 test   %ecx,%ecx      (2 bytes)      7b cmp    $0x12,%ecx     (3 bytes)
79 jne    <top>                         7e jne    <top>
```

**The two tests SWAP, and nothing else moves.** Same instruction count, same
loop-carried chain (`add, mov, load`), same two macro-fused compare+branch
pairs, both off the chain. (a) spends 6 bytes on the dead test and gets the
start test free; (c) spends 2 on the dead test and 3 on the start test. **Net:
(c) is 3 bytes smaller per loop.** STEP 1 §5 already priced this class of
bookkeeping at 0.05 cycles/byte, so no speed difference is expected and §13
reports the measured one rather than asserting it.

### Why (a) anyway

The choice therefore falls entirely to what the two cost ELSEWHERE, and (c)'s
3 bytes are paid for in four places:

1. **The start state stops being index 0.** Twelve sites assume it is, and all
   twelve move together: the emitted start constant (both the seeded and
   unseeded initializers, forward and reverse — four sites), the prefilter's
   `state == fs` guard, each self-loop skip's `state == K` guard (forward and
   reverse), `emit_seed_table`'s cells, `emit_eol_table`'s and
   `emit_end_table`'s cells, and `emit_state_legend`'s correspondence between
   a legend row and the constant a reader finds in the loop.
2. **The view tables' INDEX gains a `- 1`.** §6's one un-multiplying site
   becomes `rx_forward_eol_view[forward_state / 18 - 1]`, which is the
   emitted line hardest to read in the whole scan.
3. **Three tables gain a row.** The transition table, the accept table and the
   class-indexed accept table all go to `(n + 1) * ncls`, and §7's range bound
   tightens by one row to match.
4. **`state == 0` stops being the cheap test.** It is currently the loop's own
   back-edge condition (`test %ecx,%ecx; jne <top>` above), which is the
   emitted loop's single hottest branch; (c) makes the back-edge a `cmp` and
   the cold dead test the `test`.

What (c) buys, and it is real: the cell invariant loses its carve-out. Under
(a) a cell is "the dead sentinel, or a multiple of the stride inside the
table"; under (c) it is just "a multiple of the stride inside the table",
because the dead value IS a real index. §12's check states the (a) form and is
one clause longer for it.

**Weighing those, (a) stays.** Three bytes and one clause of a check against
twelve sites, a `- 1` in the emitted view read, a row on three tables and the
back-edge losing its free test. A reviewer who weighs the carve-out more
heavily than the twelve sites should reach the opposite answer — the facts
above are what the disagreement would be about, and (c) is built and
answer-gated, so adopting it later is a mechanical change rather than a
re-derivation.

### And why not (b)

(b) needs the extra row like (c) AND keeps the high sentinel's 6-byte compare,
so it is dominated by both. It also needs the accept and view tables to have a
DEAD row, or a proof that DEAD is never used as an index — a proof the loop's
current order makes true and a future reordering would silently invalidate,
which is exactly the shape `docs/dev/learnings.md` §3 warns about.

Sign is now available for nothing, which is the point of all three: today's
`-1` sentinel is tested with `js` after a sign-extending `movswl`, and that
sign bit is the ONLY reason the load must sign-extend. Every candidate above
replaces it with a zero-extending load and an ordinary compare.

`65535` is emitted as a literal, in the loop line and in the table's block
comment, the way `-1` is today. It is not a `#define`: the artifact's emitted
constants are literals with a legend beside them (`emit_state_legend`), and a
macro would be a second place for the number to live.

## 3a. The loop exits, and the `__builtin_expect` layout hint — MEASURED, NOT KEPT

Frank asked (2026-08-26) whether wrapping the transition loops' two exits — the
dead-state exit and the start-state exit into the candidate-start skip — in
`__builtin_expect(..., 0)` would let gcc lay the hot body out as a straight
fall-through with one backward taken jump and the exits out of line. It is a
LAYOUT question, not a predictor one (x86 has no usable hint prefix and every
one of these branches is already perfectly predicted), so it is answered by
the emitted instruction ORDER. **It was built three ways and is NOT kept.**

| variant | what is hinted | emitted loop |
|---|---|---|
| **H0** (shipped) | nothing | 16 instructions, ONE taken branch per iteration (the back-edge `jne <top>`); the skip block already out of line |
| **H1** | the dead exit only | **byte-identical to H0** — gcc's own heuristic already ranks that edge unlikely, so the hint says nothing it did not already believe |
| **H2** | the dead exit, the prefilter's `state == start` guard, and each self-loop skip's `state == K` guard | 18 instructions, of which 16 are on the hot path, and **TWO taken branches per iteration** — the hint pulled the prefilter's second conjunct INLINE (`cmp $-1,%rsi; je` jumped over every iteration) and moved the dead test onto the back-edge |

H2's listing is the answer: the hot path is not straighter, it is one taken
forward branch longer, because hinting the `state == start` guard is what tells
gcc to stop using it as the loop's back-edge condition — and that guard is
false 82-99% of the time on the bench's own subjects (STEP 1 §3: the skip is
entered 190,651 times in 1,048,576 bytes on `t-b`, 80,661 on `t-a`, once on
`t-c`), which is "unlikely" by a margin gcc was already exploiting better than
the hint does.

§13 reports H2's measured time beside the others so the listing's reading is
checked rather than trusted. **The shipped emitter carries no hint**, and
`unlikely_cond`, written for this experiment, is not in it — a helper whose
only caller was removed is a second thing to keep in step for nothing.

**Per-K-byte exit-check unrolling is NOT built** (Frank's other idea, D77): it
is named in `docs/dev/plan.md` with its current number and waits for a subject
that makes it move. After pre-multiplying, `t-b` and `t-c` are within 1.3% of
each other, which is the gap that idea would have to beat.

## 4. Which loops

`src/gen/emit_dfa.c` owns three emitted shapes. The transform reaches every one
that has a numeric transition table, which is one of them:

| shape | emitter | has a numeric transition table? | takes the transform? |
|---|---|---|---|
| ENG_UNANCH forward scan | `emit_unanchored` | yes | **yes** |
| ENG_UNANCH reverse (match-start) pass | `emit_unanchored` | yes | **yes** |
| ENG_ATTEMPT per-start loop | `emit_attempt` | **no** | nothing to take (below) |
| the empty engine | both | no loop at all | n/a |

and the same emitted text reaches every artifact kind and every variant of it,
because they are all `emit_unanchored` output:

- the DFA-only artifact (`RX_DFA_SCAN "unanchored"`);
- **the VM HYBRID's inlined prefilter** — `pcrec_emit_dfa_engine` at emit_vm.c's
  prefilter site is literally the same function, emitted as
  `static <prefix>_prefilter` ([DD-13c] made the hybrid stamp the same two
  `_DFA_*` macros for this reason). [OPT-4]/K39 is about that scan's DFA
  scaling with a bounded-repeat count; it is the SAME emitted loop and it takes
  the transform through the same code path, with no clause of its own;
- the `-bounded` prefilter forms, the memchr and byte-class candidate-start
  arms, the `views`/`viewsel` (`$`/`\Z`/`\z`) shapes and the class-indexed
  accept (`facc2`/`racc2`) shapes — all of these are branches WITHIN
  `emit_unanchored` that vary the surrounding lines, not the transition line.

**ENG_ATTEMPT has nothing to premultiply, and this is a property rather than an
exemption.** Its states are LABELS, not table rows: a step is
`goto *rx_targets_K[rx_byte_class[subject[scan_position++]]]`, one
`ncls`-entry array of code addresses per state, indexed by class alone. There
is no state variable, no multiply, and no address arithmetic to shorten — the
"entry" is already the thing the hardware consumes. Its one per-state table
that IS indexed two-dimensionally, `is_accepting_by_class[K * ncls + cl]`, has
`K` as a compile-time constant at each label, so its base is folded by gcc into
the addressing mode and never computed at run time. The premultiplied form
would be a no-op there, so ENG_ATTEMPT stamps `RX_DFA_TABLE "none"` (§8) and
its emitted text does not move.

## 5. The tables, one by one

Every per-state table in `emit_unanchored`, and what the transform does to it.
"Hot" means the forward or reverse loop reads it once per byte.

| table | today | premultiplied form | size change |
|---|---|---|---|
| `<p>_forward_byte_class[256]` | `unsigned char`, indexed by byte | unchanged | — |
| `<p>_forward_next_state[n*ncls]` | `short`, cell = `tr`, `-1` dead | `unsigned short`, cell = `tr * ncls`, `65535` dead | none |
| `<p>_forward_is_accepting[n]` | `unsigned char`, indexed by state | `unsigned char[n*ncls]`, indexed by the premultiplied state | **`n` -> `n*ncls` bytes** |
| `<p>_forward_is_accepting_by_class[n*ncls]` | `unsigned char`, indexed `[state*ncls + cl]` | **unchanged, contents and size** — the emitted INDEX becomes `[state + cl]` and computes the same cell | — |
| `<p>_forward_seed_state[ncls]` | `short`, cell = a state | `unsigned short`, cell = `state * ncls` | — |
| `<p>_forward_eol_view[n]`, `_end_view[n]` | `short`, indexed by state, cell = a state or `-1` | `unsigned short`, **still indexed by state index** (§6), cell = `state * ncls` or `65535` | — |
| `<p>_forward_stay<K>[256]` | `unsigned char`, indexed by byte | unchanged; the emitted GUARD `state == K` becomes `state == K*ncls` | — |
| `<p>_can_begin_match[256]` | `unsigned char`, indexed by byte | unchanged | — |

and the same seven for the reverse machine, with `rd->ncls` as the stride. The
two machines are independent and are decided independently (§7).

**The accept table's growth is the transform's one real cost**, and it is the
cost STEP 1's 1.276x already includes. On `orig`: forward `249 -> 4,482` bytes,
reverse `75 -> 1,350` bytes, about +5.5 KB of `.rodata`. The cells that are not
at a multiple of `ncls` are never read; they are filled with the row's own
accept bit rather than with zero, so that the table is correct under ANY index
in the row and the loop does not silently depend on the premultiplied value's
low bits being zero. (Filling them with zero would make an off-by-one index a
LOST MATCH — silent — rather than a wrong-but-loud one. Neither is a check;
§12's is.)

## 6. The one place a premultiplied value is un-multiplied

`emit_view_select` (the `$`/`\Z`/`\z` three-way position rule) maps a state to
its EOL or END view. Under the transform its cells hold premultiplied values,
but its INDEX stays the state index, and the emitted read divides:

```c
    unsigned forward_view_state = forward_state;
    if (__builtin_expect(scan_position + 1 >= subject_length, 0) &&
        rx_forward_eol_view[forward_state / 18] != 65535 && ...)
        forward_view_state = rx_forward_eol_view[forward_state / 18];
```

This is the ONE site where the premultiplied value is converted back, and it is
deliberate:

- **It is off the chain, and provably.** The table read is the second operand of
  a `&&` whose first operand is `__builtin_expect(pos + 1 >= n, 0)`. C
  short-circuits, so on a subject of length `n` the division executes at most
  twice per search (the last two positions), never per byte. gcc puts it in the
  cold block.
- **Indexing it by the premultiplied value instead would multiply these two
  tables by the stride** — `n -> n * ncls` cells of `unsigned short`, 498 B ->
  8,964 B for each of the two views on an `orig`-sized machine, and about 1,100
  more emitted source lines — for a table that a search touches at most twice.
  The `(?:P)\z` idiom is the bench's own 85 compliance subjects' spelling, so
  this is the common case and not a corner.
- The divisor is a compile-time constant; gcc emits a multiply-shift, not a
  `div`.

The general rule §1 states is "nothing ON THE CHAIN un-multiplies", and this
site satisfies it. Stating it as "nothing anywhere un-multiplies" would have
bought a uniformity the artifact pays 18x in cold table bytes for.

## 7. The bound, and what happens above it

The premultiplied form is chosen PER MACHINE at generation time (the forward
and reverse DFAs of one artifact are decided separately; they have different
`n` and different `ncls`, and each table's own dimensions are what the rule is
about). One predicate, two conjuncts:

**(i) RANGE — a correctness condition.** Every emitted cell must fit
`unsigned short` and be distinguishable from the sentinel: `n * ncls <= 65535`
gives a largest cell of `(n - 1) * ncls < 65535`. Hard, machine-independent,
and asserted by the check in §12 rather than assumed.

**(ii) SIZE — a budget.** `n * ncls <= 16384`. The premultiplied form triples
the per-state table bytes (§5) and, at `16,384` entries, the transition table
alone is 32 KB. Above that the loop is bound by memory rather than by its
dependency chain, so the chain shortening is moot while the accept table's
growth is real — an artifact that got bigger and no faster. STEP 1 §7's own
reading of the state-explosion family reaches the same place from the other
side ("the honest gate is L1 residency (~16,384 entries), which binds *before*
`short` overflow does").

`16384` is a MEASURED constant, not a round number, and this note is written
before the measurement that sets it. What is committed here is the SHAPE — a
two-conjunct rule with one tunable — and the measurement that fixes the
tunable: the `[01]*1[01]{k}` family at `k = 10, 11, 12` (9,216 / 18,432 /
36,864 entries, bracketing 16,384), timed in both forms through
`tests/bench/fdriver.c`. If the premultiplied form still wins at 36,864 the
constant moves up to the range bound and (ii) disappears into (i); if it loses
below 16,384 the constant moves down. **§13 records the number that was
measured and what moved.**

**Above the bound the artifact keeps the indexed form, byte for byte.** Not a
degraded premultiplied form and not a widening to premultiplied `int` — STEP 1
§7 is explicit that an unconditional widening doubles the table and this loop is
only fast while the tables are cache-resident. A premultiplied-`int` third rung
is NOT built (D77): the measurement that would charter it is a pattern from the
state-explosion family, above the bound, where premultiplied `int` beats the
indexed form end to end. This lane measures that point (§13) precisely so the
rung is not built on a hunch.

The corpus's own numbers, so both sides of the rule have witnesses that are not
invented for the check: over the 1,256 corpus patterns that compile under
`--features all`, the largest emitted transition table is **40,010 entries** —
above (ii), below (i) — and the median is far below both. So the rule switches
in both directions on patterns that already exist.

## 8. The stamp

`<PREFIX>_DFA_TABLE`, in the house style of `<PREFIX>_DFA_SCAN` /
`<PREFIX>_DFA_PREFILTER` and emitted from the same place (`emit_dfa_stamps` ->
`pcrec_emit_dfa_scan_stamps`), so the [DD-13c] IFF governs it unchanged: it is
on **every artifact that CONTAINS a DFA scan** — every DFA artifact and every
VM hybrid — and on no other. Value set:

| value | meaning |
|---|---|
| `"premultiplied"` | every numeric transition table in this artifact's DFA scan holds `next * stride` |
| `"indexed"` | every one holds `next` (the pre-[OPT-3] form) |
| `"mixed"` | the forward and reverse machines took different forms |
| `"none"` | the scan has no numeric transition table — ENG_ATTEMPT's computed-goto rows (§4), or the empty engine |

`"mixed"` is a real value and not defensive padding: §7 decides per machine, and
a pattern whose forward DFA is above the bound and whose reverse DFA is below it
gets one of each. Naming it is cheaper than a rule that says it cannot happen.

The value is read off the SAME predicate the emitter branches on — ONE
derivation, THREE readers (the emitted loop, this stamp, and the orientation
block's "READING THE TABLES" paragraph), this file's standing rule
(`unanch_start`, `attempt_cand` and `dfa_engine_is_empty` all state it) — so
the stamp cannot disagree with the loop unless the predicate itself is wrong,
in which case the loop is wrong too.

**Is a runtime mirror in `rx_info` owed? Decided here: NO, with a named
trigger.** `docs/spec/match_api.md` §6.3's (a)/(b) split is a rule about
MACROS: (a) selection facts are unconditional (scoped to the mechanism that owns
them), (b) capacity and activity macros stay VM-only. `RX_DFA_TABLE` is
squarely (a), and §6.3 makes the macro owed. It says nothing about the struct.
The two `rx_info` mirrors that DO exist (`scan`, `prefilter`) were a SEPARATE
decision at [DD-13c] under Frank's D40 addendum, justified by a header-less
consumer — a harness that `dlopen`s an artifact, an FFI binding, a tool walking
several `<prefix>_info` symbols. **Measured 2026-08-26: no such consumer exists
in the mandated repositories.** `pcrec-bench` links its artifact and reads
`rx_info` through `testees/pcrec/shim.c`'s 40 `pb_*` accessors, and there is no
accessor for `scan` or `prefilter` — the two fields added at abi 6 are still
unread. A third unread mirror is D77's "built ahead of a measured need".

The trigger, stated so the next lane does not have to re-derive it: **the first
consumer that reads `rx_info.scan` or `rx_info.prefilter` at run time makes
`table` owed too.** It is an append at the end of the struct at that point — no
existing member's offset moves — which is exactly the shape [DD-13c] used.

## 9. The deny flag

`-fno-premul-table` / `PCREC_NO_PREMUL_TABLE` (bit 15), in
`docs/spec/tuning.md` §2's house style and specifically `-fno-tiered-entry`'s
(§2.12) shape: **deny-only**, no force half. There is one table form per machine
and the generation-time rule picks it, so there is nothing to address and
nothing to force.

- **ANSWER-IDENTITY-preserving**, which is the whole reason it exists: the
  denied build is the control the premultiplied build is compared against
  (§10), and it is also the bisect lever for the optimization.
- Under the denial `emit_unanchored` emits the indexed form **byte for byte as
  it shipped before [OPT-3]** — this is a requirement on the implementation,
  not a hope: the emitter's premultiplied branch is written so that the
  `!premul` arm reproduces today's strings character for character, the way
  `emit_view_select`'s `!has_end` branch reproduces its pre-[M6.2] text.
  `run_recursion_identity.sh`'s comparison (A) is what proves it (§10).
- **MASKED out of `rx_info.flags`** (`emit_info_def`'s `strategy_denials`), for
  the mask's own reason: it changes no answer, so two artifacts that behave
  identically must not differ in their reflection surface over it, and what the
  emitter DID is already reported by `RX_DFA_TABLE`.

## 10. The identity argument — and it is a CONTROL, not an argument

The transform is answer-preserving by construction (it changes the ENCODING of
a state, not the machine), and that sentence is worth exactly nothing on its
own. What is claimed is checked, on three populations, comparing every answer
byte — match/nomatch, spans, captures, give-up codes — not counts:

1. **The corpus.** `make test` in full. Every `.rxt` case is an answer.
2. **The bench's 91 subjects**, STEP 1 §7's own answer gate rebuilt in this
   lane's scratch dir: 85 compliance `s-*.bin` under the whole-subject
   `(?:P)\z` spelling, 3 throughput `t-*.bin` under find-all, and 3 synthetic.
   Three arms compared pairwise: the premultiplied artifact, the
   `-fno-premul-table` artifact, and the artifact from the PRE-CHANGE compiler.
3. **The emitted text of the denied build against the pre-change compiler**,
   byte for byte (`run_recursion_identity.sh` (A), plus the identity scripts
   that already sweep the corpus).

(2) is the population that matters most and it is the one furthest from the
code: the bench's subjects were chosen by a different project for a different
purpose, and the `(?:P)\z` spelling exercises exactly the `views`/`endv` shapes
§6's division lives in.

**MEASURED 2026-08-26 (the gate is `scratchpad/srPremul/ag/`, rebuilt in this
lane from STEP 1 §7's description; `agdriver.c` prints every match's span AND
every capture slot AND the terminal return, so a difference in any answer byte
is a difference):**

| | |
|---|---|
| arms | premultiplied / `-fno-premul-table` / the PRE-CHANGE compiler at `7b5b27b`, pairwise |
| patterns | 11, chosen for the shapes the transform touches — `orig` and its `(?:P)\z` spelling, a capture-bearing one, a `\b` one, a `(?m)^` one (`"none"`), the `"mixed"` witness `[01]*1[01]{11}`, an ENG_ATTEMPT one (`"none"`), a `\z` one |
| subjects | 91 — the bench's 85 compliance `s-*.bin`, its 3 throughput `t-*.bin`, 3 synthetic (a match-bearing line, the EMPTY subject, 4 KB of random bytes) |
| regimes | whole-subject for a `\z` pattern on the compliance set, find-all everywhere else — the bench's own two |
| **result** | **11 patterns, 1,001 subject cells, 122,135 answer lines per arm, ZERO differences** |

`orig` alone contributes **40,470 answer lines**, which is STEP 1 §7's own
population reproduced against a compiler rather than against a patched
artifact. The `"none"` rows are included deliberately: they are the artifacts
the transform must leave UNTOUCHED, and an arm that only compared the ones it
changes could not say so.

## 11. What could go wrong

Each of these is a failure mode with a site, not a worry:

- **The sentinel colliding with a real premultiplied value.** `65535` is a legal
  cell content iff `(n - 1) * ncls >= 65535`, which §7 (i) forbids and §12's
  check asserts. The failure would be a state that reads as dead: a LOST MATCH,
  silent, on exactly the large machines nobody has a small reproducer for.
- **Unsigned arithmetic on the class add.** `state + class` must not wrap and
  must not sign-extend. The state variable is `unsigned`; the class comes from
  an `unsigned char` table through an `unsigned` temporary. If the state
  variable were left `int`, gcc reinstates the `movslq` and the transform buys
  nothing while still being correct — a SILENT PERFORMANCE regression that no
  answer check can see. §12's check reads the emitted declaration.
- **A negative state value reaching the state variable.** `emit_seed_table`'s
  cells come from `d->s1u[]`, which can in principle be `-1` (a dead interior
  start state). Today that would index `is_accepting[-1]`; premultiplied it
  would index `[65535]`, a much wilder read. **Measured over the 1,256
  compiling corpus patterns: no seed table has a negative cell** (the only
  negative cells anywhere are the eol/end views' documented `-1`, 42 and 64
  artifacts respectively). Rather than rest on that sweep, a negative seed cell
  is made a PRECONDITION of the transform: the predicate refuses the
  premultiplied form for a machine that has one, so the wilder read is
  unreachable by construction and the pre-existing `[-1]` question is left
  exactly as it was — it is not this lane's to answer, and it is recorded here
  so the next lane finds it.
- **The accept table's growth.** `n -> n * ncls` bytes. Bounded by §7 (ii) and
  included in STEP 1's measured 1.276x.
  **MEASURED IN EMITTED LINES, 2026-08-26, and it is not nothing on one
  family**: `tests/codegen/run_ir_listing.sh`'s informational [ENG-BREP] row
  reads `{0,400}` **869 -> 962 lines** and `{0,4000}` **1,994 -> 2,762** for
  `((a)|b){0,N}c` — the VM hybrid whose inlined prefilter DFA is K39's, where
  the machine is large and the accept table triples with it. The check itself
  stays green because what it asserts is COUNT-INDEPENDENCE by comparison with
  the prefilter denied (573 / 573, delta 0), which this change does not touch;
  the growth is real and is the cost §7 (ii) exists to bound. It is also the
  clearest statement of what [OPT-4] would buy: shrink that prefilter's DFA
  and this cost shrinks with it.
- **A table that fits `unsigned short` but not L1.** Exactly what §7 (ii) is
  for, and the reason the bound is not the range bound alone.
- **The eol/end view division drifting onto the hot path.** If a future change
  hoists the view select above its `__builtin_expect` guard, or evaluates the
  table read unconditionally, the division lands on the per-byte path. §6's
  short-circuit is the load-bearing property; it is stated in the emitted
  comment beside the line.
- **The denied form drifting from the pre-change text.** The reason (A) is run.

## 12. `abi` 6 -> 7, and the checks

This change moves emitted PROGRAM bytes (the loop lines and the table
declarations), which no previous `abi` event did — [DD-13], [OPT-1] and
[DD-13c] were all scaffolding, and each said so in `emit_info_def`'s comment.
D76's ritual is the same either way, and its FOUR sites are all in this one
change:

1. `src/gen/emit_dfa.c` — `.abi = 7`, with the paragraph saying which bytes move.
2. `tests/codegen/run_codegen_tests.sh` — the [DD-14.FB] §10.4 `ABI_EXPECT`.
3. `docs/spec/match_api.md` §6 — the "`rx_info.abi` is `7`" sentence (two sites:
   the §1 note and §6's bullet).
4. `tests/codegen/run_recursion_identity.sh` — comparison (B)'s `FILEPIN`,
   re-pinned to this change's last `src`/`lib`/`cli` commit.

Comparison **(A)** (the pre-module program-region pin) is expected to stay
byte-identical and is a real check here rather than a formality: `prog_region`
is `goto <p>_L0;` through `<p>_accept:`, i.e. the VM program, and the hybrid's
inlined `static <prefix>_prefilter` is emitted ABOVE `goto <p>_L0;` — verified
on a current hybrid artifact (`rx_prefilter` at line 250, `goto rx_L0;` at 396).
So (A) sees no DFA scan bytes at all and must not move.

The checks this change adds are `tests/codegen/run_premul_table.sh`, its own
section (`make test-premul-table`, part of `make test` and deliberately NOT of
`make smoke` — it sweeps the whole corpus and compiles matchers, the same
reason `run_endvar_identity.sh` runs under `test-assertions`). Six sections,
and every verdict is derived from the EMITTED MATCHER TEXT with the stamp
compared against it (`docs/dev/learnings.md` §3: the obvious wrong check reads
`RX_DFA_TABLE` and asserts it is one of four strings, which measures whether
the emitter can print):

- **§1 named witnesses, one per documented value**, entry counts read off the
  emitted declarations — including the two adjacent members of the
  state-explosion family that STRADDLE the bound, which is what gives
  `"mixed"` a witness nobody invented for it.
- **§2 the bound, on both sides**, plus a NON-VACUITY assertion that the swept
  family really does straddle it. Without that, a bound that moved would leave
  the section passing on one side.
- **§3 the corpus sweep**: the [DD-13c] iff both ways, stamp against emitted
  declarations, the bound on every machine, the ACCEPT TABLE'S LENGTH as an
  independent second witness of the form (it comes from a different emitter
  function than the transition table's type), and the SHAPE — `unsigned` state
  variable, add-only index. **§3's shape arm is the one that catches §11's
  silent `int` regression**, which no answer comparison and no self-comparing
  byte-identity gate can see.
- **§5 the cell invariant** on every premultiplied table: each cell is the
  dead sentinel or a multiple of the class count, strictly inside the table.
  The class count is read from `rx_*_byte_class` — a different table from a
  different emitter function — because taking the stride from the transition
  table would make the invariant a tautology.
- **§6 the deny flag**: answer-identical over a subject set, with every pair
  required to differ in `RX_DFA_TABLE`. A pattern whose scan carries no
  numeric table is EXCLUDED, not tolerated as an equal pair.

**THE PLANTED-BUG DEMONSTRATIONS** (learnings §3: a check must be SHOWN to
detect). Three plants, each made in the emitter, rebuilt, run and reverted;
the clean baseline is 15 passed / 0 failed. Recorded here rather than only in
the check's header because one of them refuted a sentence of §7's:

- **PLANT 1 — the table is not premultiplied while the loop assumes it is**
  (`emit_tr_table`'s premultiplied arm emits `t` where it should emit
  `t * ncls`). **13 passed / 19 failed**: §5 red on 14,387 of 39,787 cells and
  §6 red on nine subject cells; the ordinary corpus red at 65 of 100 cases on
  three `.rxt` files. §1, §2 and §3 stay GREEN, correctly — they read
  DECLARATIONS and the plant changes CELLS, so the red localises to the axis
  that broke rather than going uniformly red.
- **PLANT 2 — the sentinel collides.** Raising `PREMUL_MAX_ENTRIES` past the
  range bound is NOT ENOUGH: the RANGE conjunct still refuses, which is the
  measured demonstration that §7's (i) is not redundant with (ii) even though
  (ii) is tighter. **Breaking BOTH** produces a 73,728-entry premultiplied
  table whose cells overflow `unsigned short` (gcc emits 5,460 overflow
  warnings, so the artifact does not build clean) and in which 65535 is a real
  cell. **12 passed / 5 failed**: §1's straddling witness, §2's two
  above-bound rows AND its non-vacuity guard ("the swept family did not
  STRADDLE the bound"), and §3's bound arm on 4 machines.
  **§5 STAYS GREEN, and that is the honest reading**: the corpus's largest
  machine is 40,010 entries, so no corpus artifact can carry a collided cell —
  the CELL check cannot see this defect, and what makes a collision
  unreachable is the BOUND check, not the cell one.
- **PLANT 3 — the state variable left `int`** (the silent regression §11
  names). Confirmed at the instruction level first: with `int`, `movslq
  %edx,%rdx` is back ON the chain at `0x57` and a second `movslq` off it,
  while every answer is unchanged. §3's shape arm is the detector.


The [SABANCHOR] tripwire is run: this change edits the emitted loop lines, which
is where `tests/mech`'s sabotage anchors live, and a moved anchor is re-anchored
per `tests/mech/CLAUDE.md` with the row proved to detect solo afterwards.

## 13. Measurement

**Filled in after the measurement runs** (the manager's battery owns the box
until it prints `== BATTERY DONE`; no timed number is taken before then). What
goes here: `tests/bench/fdriver.c` on `t-a`/`t-b`/`t-c` with `orig.rx`,
baseline (`-fno-premul-table`) against the default, `taskset -c 3`, median of 5,
>= 1 s per trial, `load1` beside every number; STEP 1's figures to reproduce are
6.21 / 3.27 / 3.27 -> 4.92 / 2.55 / 2.52 ns/byte, set 1.276x. Plus the
`[01]*1[01]{k}` bracket that sets §7 (ii)'s constant, and one pattern each side
of the final bound showing the artifact form differs and the answers do not.
