# D164 — the MATCH-END MARK (`END_MARK`): design note

**Status: PROPOSED, design + hand-twin; nothing under `src/` changes.** Lane
`endmark`, 2026-10-12, from main `885eccff`, abi 76. Ruling: D164
(`../dev/decisions.md`). Instruments and transcripts: `endmark/` (own CLAUDE.md).
The `.rxt`/pcrec checks this note asks for are build work (§6). Read §0, then §1.3
(the rule) and §2.3 (where D164's own wording is too strong).

## 0. Answers first

1. **The lowering is exact.** It fires where a POSITIVE lookahead ends its path, and
   `$`, `\Z` and `(?m)$` count as lookaheads (`(?=\n?\z)`, `(?=\n?\z)`, `(?=\n|\z)`).
   It replaces `X(?=Y)` with `X END_MARK Y`. libpcre2 10.46 was run on the original
   and on the lowered spelling, with an empty capture group `()` standing in for the
   mark. Both were compared at every start position of every subject over a
   4-letter alphabet up to length 5, plus find-all. The comparison covered group 0,
   every capture and the find-all sequence: **3,527 patterns, 28,237,887 cells, 0
   differences** (`endmark/results/diff_all_len5.txt`). Six deliberately wrong
   variants each go red (§1.5).
2. **Two consequences D164 did not name.** First, a capture that ENCLOSES the mark
   (`(\d+(?=px))`, `(foo$)`) must close at the mark, not after Y. A report-time rule
   handles it, and dropping that rule is one of the planted failures. Second, a
   negative lookahead never lowers: `(?!Y)` is not a concatenation.
3. **The forward DFA needs nothing new beyond an accept offset.** Each lowered
   path's accept node carries `back` = Y's consumed length. D3's accept-pruning
   (`src/ir/dfa.c`'s header) already picks the first accept in priority order, so
   the scan reports `pos − back`. Fixed-width Y needs no state splitting. Variable
   bounded Y splits by distance up to `maxw(Y)`. Unbounded Y keeps its lookahead,
   and the pattern stays on the VM as today. A priority-NFA twin over the lowered
   NFA agrees with libpcre2 on **120,304 / 120,304** cells (`endmark/twin.py`
   part A).
4. **The reverse walk is one walk from `n`, and the tie is not gone.** D164 says "no
   two seeds, no tags, no tie special case". The first holds. The other two are too
   strong. A reverse DFA cannot see priority, so when both ends (`n` and `n−1`) can
   be reached from the leftmost start, the pattern's priority must still choose.
   What the mark changes is that the tie becomes the GENERAL case of "a reverse
   accept carrying more than one mark distance", the reverse half of the forward
   mechanism, and stops being a `$`-specific two-seed special case. It is resolved
   by a static fact (`mark_prio`, §2.3) on every common shape, and by today's FINISH
   rows otherwise.
5. **B3, counted** (the twin is answer-checked against libpcre2; loads are subject
   bytes; k = 16,000):

   | cell | today | mark, `mark_prio` constant | mark, no fact (forward run on every possible tie) |
   |---|---|---|---|
   | `\s+$` on `Q·\t^k·\n` | 48,004 (3.00×) | **16,002 (1.00×)** | 32,003 (2.00×) |
   | `\s*?$` on `q·␠^k·\n` | 48,004 (3.00×) | **16,002 (1.00×)** | 32,003 (2.00×) |
   | `(?:\s+\|x\s*?)$` (priority depends on the state) | 48,005 (3.00×) | 32,004 (2.00×): FINISH | 32,004 (2.00×) |
   | `\d+$`, `[a-z]+\.txt$`, `\s+$` with no final `\n` | 1.00× | 1.00× | 1.00× |

   The twin's "today" reproduces compound.md §B.5's 48,007 measurement to 3 loads.
   G3's bound for the final-newline shape becomes **1.00× where `mark_prio` is
   constant** (true for `\s+$`, `\s*?$`, `[\s\w]*$` and the bench's
   `tail-space-eol`) and 2.00× where it is not.
6. **The census is small and concentrated** (§3; `endmark/results/census.txt`).
   - 2 bench and 22 corpus patterns go VM → DFA because the only thing forcing the
     VM was a bounded path-final lookahead. The bench pair is `syntax/lka-pos` and
     `lka-verb`: `item(?= done)`, the cell `ctx_prefilter_joint.md` found losing
     per-byte on the VM.
   - 4 corpus patterns gain an exact hybrid prefilter (captures keep them on the VM).
   - The rev-end `$`/`\Z` artifacts move: 9 bench and 257 corpus. Of those, 1 bench
     (`capability/tail-space-eol`, `\s+$`) and 42 corpus carry tie code today.
   - If `$` lowers on every consumer (§6, Q1), every path-final-`$` artifact moves:
     37 bench and 851 corpus, plus 54 path-final `(?m)$` DFA artifacts.
7. **It is one AST pass and one new node kind** (§4). `src/opt/endmark.c` runs after
   `pcrec_discharge_atomic` and before `pcrec_callgraph_build`, and it rewrites in
   place. The new node is `A_ENDMARK`, `\K`'s mirror. One invariant keeps it small:
   **everything inside the engine speaks CONSUMPTION, and only the report speaks the
   mark.** Group 0's caller-visible end does not change meaning, so no `match_api`
   hunk is needed. The changes are abi events, a `facts_listing`/`ir_listing` hunk,
   and one harness-only lever.

## 1. Semantics

### 1.1 What "ends its path" means

A node is in TAIL position when nothing consumes or asserts after it before the
match is accepted. The tail positions, as the walk that defines them:

- the root;
- the LAST element of a concatenation (trailing empty `(?:)` elements skipped);
- every arm of an alternation in a tail;
- the body of a capture or an atomic group in a tail;
- the body of a repeat in a tail **whose maximum is 1** (`?`, `??`, `?+`, `{0,1}`,
  `{1}`).

That is all. A repeat with max > 1 is NOT a tail for its body, because the body
re-enters at the mark, not after Y. This is the planted failure `through-rep`
(`(?:a(?=a))+`). A conditional's arms are declined (not walked) until a census
shows one. The tail walk is `endmark/tail_probe.c`'s `tail_walk`.

### 1.2 Why it is exact

PCRE2's `(?=Y)` is atomic and zero-width. At position `m` it succeeds iff Y matches
at `m`, its captures come from Y's first (priority) match, and the cursor returns to
`m`. Take `X(?=Y)` in tail position:

- **Same starts, same order.** Any start that has a match of `X(?=Y)` has a match
  of `X·Y` and the reverse. So the leftmost start is the same.
- **Same end.** At that start, backtracking enumerates X's candidate ends `m` in
  X's priority order. In the original, the first `m` where Y succeeds is the match,
  ending at `m`. In `X END_MARK Y` the same enumeration tries Y, as consumption, at
  each `m`, and the first success is the same `m`. The mark records `m`.
- **Same captures.** Inside Y, the first success in Y's priority order is the same
  match in both spellings. Captures in X were set by the same path.
- **The lookahead's atomicity is unobservable.** Atomicity would cut backtracking
  INTO Y when something after the lookahead failed, and in tail position nothing
  comes after. For the same reason, an atomic group or a possessive `?+` around a
  tail is transparent, and PCRE2's non-atomic `(?*Y)` lowers identically.
- **Alternation.** Each arm is tried independently, and an arm without a mark
  reports its consumed end (no mark was crossed, exactly as `\K`'s
  `PCREC_UNSET`).
- **Optional groups** (`(?:X(?=Y))?`, `??`): the group is entered once or skipped,
  with no re-entry.

`$` and `\Z` are exactly `(?=\n?\z)` (pcre2pattern). `X$` therefore lowers to
`X END_MARK \n? \z`. At a given `m`, the tail `\n?\z` succeeds in at most one way
(m = n, or m = n−1 with s[n−1] = '\n'), so the tail adds no priority of its own.
`(?m)$` is `(?=\n|\z)`. `\z` consumes nothing (rule L6 below). `\b` is not a
lookahead: it is two-sided and half of it is negative. It is already a context node
(`A_CTX`), and the mark leaves it alone.

### 1.3 The rule, as a first-match table

For a lookahead-like node `N` in tail position, with body Y: let
`Y' = plain(Y)` be Y with its own tail positive lookaheads replaced by their bodies
(no second mark: the first mark already set the end) and its tail `$`/`\Z`/`(?m)$`
replaced by their consuming bodies. Then:

| # | row | applies when | becomes |
|---|---|---|---|
| L1 | `negative` | `(?!`, `(?<!`, `(*nla:` … | unchanged (an assertion) |
| L2 | `behind` | a lookbehind | unchanged |
| L3 | `called` | N lies inside a group that is a subroutine-call target, or the root under `(?R)`/`(?0)`, or Y' contains a call | unchanged (a call site re-enters the body with another continuation; K93's lesson) |
| L4 | `unbounded` | `cwmax(Y')` unbounded | unchanged (the VM, as today; §2.2) |
| L5 | `ctx` | N was born `A_CTX` (one-character language, `src/parse/ctxnode.c`) | unchanged: answer-free, no movers |
| L6 | `zero-width` | `maxw(Y') = 0` (`\z`, `(?=)`, `(?=\b)`) | `Y'` alone (a mark would equal the consumed end) |
| L7 | `mark` | otherwise | `END_MARK · Y'` |

The rows are data (`start_table.md` §0a's rule), listable under `--list-axes` as a
sub-axis of the pass (the listing is not a deny surface: §5.4). L4 is a D77 choice.
Lowering an unbounded Y would buy only an exact hybrid prefilter, on 3 corpus
patterns (§3.1). The trigger to revisit it is a bench cell.

### 1.4 Captures that enclose the mark

`(\d+(?=px))` reports group 1 = `\d+`'s span. After lowering, the group's close is
reached AFTER Y. The rule: a capture that is an ANCESTOR of a lowered mark (static,
known when the pass runs) reports its end at the mark when the winning path crossed
a mark, and at its own close otherwise. It is applied at report time
(`<prefix>_report_captures`), with no change to how `vm_cap` writes. This is exact,
because tail position puts the capture's close after the mark on the same path. A
mark crossed outside the capture cannot occur: if the capture were in that mark's
Y, it would hold no mark node, since inner tails lower without one.
Captures INSIDE Y are set by ordinary consumption and need nothing (`a(?=(b)(c)?)`
in the families; PCRE2 sets them, §1.2).

### 1.5 The differential (`endmark/diff_lowering.py`)

Patterns are generated from a small AST, so each capture's identity is known in both
spellings:

- X: 17 shapes, greedy/lazy/possessive/atomic, alternations in both orders,
  captures inside;
- Y: 16 shapes, including alternations, captures, a nested positive and a negative
  lookahead, `$`, and `\n?\z`;
- 12 wrappers: plain, `(?*`, enclosing capture, `?`/`??`, alternation either side,
  a non-tail control, an atomic group, `\K` before, and a capture before the
  lookahead;
- an anchor family (`$ \Z (?m)$ \z` × 17 X × plain/capture/alternation, plus a
  mix);
- 21 curated cases (below);
- four UTF-8 patterns over `{a, é, b, \n}`.

The curated cases include find-all where the consumed context passes the next match
(`a(?=aa)` on `aaaa` must report `(0,1),(1,2)`), the empty match `(?=ab)`, `\K`
plus a mark, nested tails, captures inside alternating Y, enclosing captures across
arms, the greedy/lazy variable-Y pair `a+(?=a?b)` / `a+?(?=a?b)`, the tie
`q|a$|a\n$`, and the non-tail controls.

**Result: 3,527 patterns, 28,237,887 cells, 0 differences** (libpcre2 10.46; byte
subjects ≤ 5 over `{a,b,c,\n}`, UTF subjects ≤ 4 over `{a,é,b,\n}`, every start
position, find-all under `match_api.md` §3.1.3's protocol on REPORTED spans).

**The controls**, each a deliberately wrong variant (`endmark/results/diff_plants.txt`,
curated set):

| plant | what it does wrong | differences |
|---|---|---|
| `consumed-end` | reports the consumed end, not the mark | 54,054 |
| `no-close-at-mark` | drops §1.4's capture rule | 2,858 |
| `lower-negative` | lowers `(?!b)` like a positive | 23,090 |
| `lower-nontail` | lowers lookaheads that are not path-final | 4,904 |
| `through-rep` | treats a looping repeat as a tail | 296 |
| `findall-consumed` | resumes find-all at the consumed end | 2,476 |

## 2. Engines

### 2.1 The VM

`A_ENDMARK` is `vm_set(v, 1, "(ptrdiff_t)scan_position", …)`: `\K`'s arm with
slot 1 instead of slot 0 (`src/gen/emit_vm.c`'s `A_KRESET` case). It is trailed, it
is rewound by `<prefix>_unwind`, and it shows in the listing as a slot write. Slot 1
is group 0's end, reserved by `nstate`'s `2 * ncaps` and written by nothing today.
`<prefix>_report_captures` writes
`capture_spans[0][1] = slot_values[1] != PCREC_UNSET ? slot_values[1] : match_start + match_length`,
plus §1.4's ancestor list, on an artifact that has a mark. A mark-free artifact
keeps its text byte for byte, as `\K`'s `nkreset` predicate does. The anchored
entries return the REPORTED length.

**Give-up posture.** At a tail, `X·Y` does the same work as `X(?=Y)`: Y's
alternatives are tried until the first success, and on total failure the VM
backtracks into X. Frame use differs, though. The lookahead's sub-match pops its
frames on success, while consumed Y's choice points stay on the stack until accept.
So a FRAMES give-up can move at the capacity boundary. D158 asks for a give-up
differential across the lever (§5.5), not an argument.

### 2.2 The forward DFA

The NFA builder (`src/ir/nfa.c`) gives each lowered path its own accept node
`ACC(b)`, where `b` is Y′'s consumed BYTE length:

- **Fixed-width Y′** (`minw = maxw`, measured in bytes): one `ACC(L)` per distinct
  length. There is no state splitting, because a thread's distance to its accept
  is fixed by the node.
- **Variable bounded Y′:** Y′ is built as the product with a distance counter
  `0..maxw(Y′)`, so each length lands on its own `ACC(l)`. The bound comes from
  `maxw`. No constant is introduced: the product is charged to the existing
  NFA/DFA state caps, and overflow takes the existing `fit_rungs[]` path to the VM.
- **Unbounded Y′:** L4 keeps the lookahead.

**Priority among different ends uses the existing mechanism, unchanged.** It is
D3's priority subset construction with accept-pruning: "closure walks split edges
in preference order and stops the instant ACCEPT is reached — lower-priority threads
are pruned and the state is marked accepting" (`src/ir/dfa.c`'s header). An
accepting DFA state therefore carries the `b` of the first `ACC` reached in priority
order. The scan's last-accept rule records `pos − b[state]`, and a later accept from
a higher-priority thread overwrites it. This is leftmost-first exactly, because the
end is decided by which thread accepts, and that thread knows its distance. The
emitted change is one per-state `back` table beside the accept table, or a constant
when every accepting state has the same `b`. It is a new emitted table, so it is an
abi event.

Measured in the twin, the unanchored leftmost-first scan over the lowered NFA,
reporting `pos − d`, agrees with libpcre2 at every start position. The cases are
`\d+(?=px)`, `a+(?=a?b)`, `a+?(?=a?b)` (variable Y, both preferences), an
alternation with marks in some arms, `foo(?=bar|ba)`, `(?=ab)`, `[ab]*$` and
`[ab\n]*?$`. Result: **120,304 cells, 0 differences.** The plant `fwd-consumed-end`
gives 3,811.

**What reads the consumed end, unchanged.** These all speak consumption, which is
correct:

- the D7 reverse pass seeds at the forward scan's accept position. The reverse
  machine over the lowered language finds the leftmost start: any start that has a
  match has a consumed match, by the §1.2 argument;
- `[START-LANDING]`'s `end-minus-width` (start = consumed end − consumed width);
- W1's end window;
- the necessary byte/run pre-checks (Y's bytes become necessary, a free gain);
- the VM hybrid's window ceiling.

The hybrid's prefilter language becomes exact. The body records no
`NFA_ERASED_LOOK` for a lowered tail, so `pcrec_cand_lang_exact` holds and
`Vm.mrl_win` can arm. **Obligation:** the ceiling handed to the VM is the CONSUMED
end, never the reported one. A ceiling at the mark would starve Y and lose matches
(§5.6's sabotage row S-EM4).

### 2.3 The reverse walk (rev-end): this is B3

After lowering, a path-final `$` reads `X END_MARK \n? \z`. The `end_pin` fact sees
`\z` at every path end and answers `z`. There is ONE seed, at `n`. The walk reads the
reversed lowered language: optionally the final `'\n'` (the tail), then the mark,
then X reversed.

**Why the tie does not disappear.** At the smallest accepting position `s*`, two
reverse paths may both have reached it. One has X consuming the final `'\n'` (mark
at `n`); the other has the tail consuming it (mark at `n−1`). Both are real matches
starting at `s*`. Leftmost-first priority chooses between them, and priority is a
forward property the reverse walk cannot see (`\s+$` → `n`, `\s*?$` → `n−1`,
compound.md's `lazy tie` cell). An untagged walk merges the two paths into one
subset state and loses which ends are possible. So the walk needs to know the
DISTANCE at which each reverse thread crossed the mark. That is the reverse half of
§2.2's mechanism: forward threads carry their distance from the mark to the accept,
and reverse threads carry their distance from the seed to the mark. It is general,
not `$`-specific. A bounded trailing context of length ≤ L gives distances
`0..L`, and `$` is L = 1. The reverse machine is built with prune off, as D7's
already is, and its accepting states carry the SET of distances that reach them. At
`s*`:

- **one distance `d`** → end = `n − d`. No forward pass.
- **several distances (a tie)** → the static fact `mark_prio`:
  - **constant `c`** (in every reachable situation where several distances accept,
    priority picks `c`) → end = `n − c`. No forward pass.
  - **otherwise** → FINISH's ENDSET rows as today: `verify-at` is one anchored run
    from `s*`, and `search-from` is the relocate.

**`mark_prio`, the fact.** It is computed at compile time by exploring the anchored
forward NFA closure lists of the lowered pattern WITHOUT pruning, each thread
carrying its mark distance. At the subject end (with `\z` true), it lists the
accepting distances in priority order. Wherever two or more distances appear, it
records the first. If one value is recorded, the fact is `const c`; if none, `none`
(no tie is possible); otherwise `state-dependent`. It is asked only when the built
reverse machine has an accepting state with two or more distances (the old
`nl_last`, generalized). Its exploration is charged to the existing DFA state cap,
and overflow answers `state-dependent`, the safe direction. Twin results
(`endmark/results/twin_k16000.txt`):

| X in `X$` | `mark_prio` | answers vs libpcre2 (today / tagged+fact / untagged+forward) |
|---|---|---|
| `\s+` | const 0 | 0 / 0 / 0 wrong of 4,005 random subjects |
| `\s*?` | const 1 | 0 / 0 / 0 |
| `\d+`, `[a-z]+\.txt` | none (no tie possible) | 0 / 0 / 0 |
| `a\|a\n` | const 1 | 0 / 0 / 0 |
| `a\n\|a` | const 0 | 0 / 0 / 0 |
| `\s+\|x\s*?` | **state-dependent** | 0 / 0 / 0 |
| `[\s\w]*` | const 0 | 0 / 0 / 0 |
| `a\n{0,2}?`, `a\n{0,2}` | const 1 / const 0 | 0 / 0 / 0 |

The controls (`endmark/results/twin_plants.txt`):

| plant | wrong answers |
|---|---|
| tags dropped | 36 to 383 per pattern, on 7 of 10 patterns |
| the fact flipped | 42 to 383 per pattern |
| the untagged walk skipping its forward run | 42 to 383 |

**Reverse machine size** (reachable subset states, twin part C):

| X | today `rev(X)` | mark, untagged | mark, tagged |
|---|---|---|---|
| `\s+` | 2 | 3 | 4 |
| `[a-z]+\.txt` | 6 | 7 | 12 |
| `\d+\.\d{1,3}` | 6 | 7 | 12 |
| `[a-z]+=[^\n]*` | 3 | 4 | 7 |

Tagging at most doubles the machine for L = 1. That is the price of one walk.

**When is a forward finish still needed?**

1. A tie whose priority is state-dependent (above).
2. Captures. The VM hybrid's stage 2 hands the VM `s*` with ceiling `n`, and the
   VM's own leftmost-first run sets the mark, so the hybrid needs neither the tags
   nor the fact.

**What is deleted.** The second seed, `revend_tie`'s bookkeeping, and the `eol ? 2 :
1` seed count in `emit_rev_end`. `PCREC_EPIN_EOL` loses every producer on a path
lowered by L7 (§4.3).

**Compound's G3.** compound.md §B.5's final-newline cells read 1.00× where
`mark_prio` is constant (both measured shapes) and 2.00× where it is
state-dependent. That is the bound B3's gate states for G3.

## 3. Census (`endmark/census.py`, `endmark/results/census.txt`)

The populations are `docs/dev/optloop/revend/census.py`'s builders, imported:

- the bench: 367 rows, 351 parsed, compiled as pcrec-auto does;
- the corpus: 5,645 rows, 5,236 parsed, with each block's encoding and `-i`.

The probe is `tail_probe.c`, which runs the real parser and the pre-selection
rewrites with captures requested. FACTS is `pcrec --emit-facts`. On the
VM → DFA set, the probe's verdict and the shipped engine stamp disagree **0 times**.

### 3.1 Path-final positive lookaheads (multi-character; one-character ones are `A_CTX` today)

| population | today → after the lowering | patterns |
|---|---|---|
| bench | **VM → DFA** (only a bounded tail lookahead forced the VM) | **2**: `syntax/lka-pos` `item(?= done)`, `syntax/lka-verb` `item(*pla: done)` |
| corpus | **VM → DFA** | **22** (`abc(?=def)`, `a(?=\n?\z)`, `z(?=ab\|cd)`, `z(?*abc)`, `z(?=a(?!b))`, …) |
| corpus | VM, captures: DFA under `--no-captures`; the hybrid prefilter becomes exact | 4 |
| corpus | VM, another VM-only construct (`(?<=`, `\1`) | 6 |
| corpus | VM, call-bearing (L3) | 1 |

Y widths: the bench pair is fixed at L = 5. The corpus has fixed L = 0..3 (22
patterns), variable L ≤ 2 (8) and unbounded (3, all already VM for another reason).
So the forward machine needs distance splitting on at most 8 corpus patterns, all
with L ≤ 2.

**Prediction for the bench pair.** `item(?= done)` moves from the VM to the DFA
route. The necessary run grows from `item` to `item done` (9 bytes), because Y is
now necessary consumption. The cells today read auto == forced-VM at 1.21 ns/B
(`ctx_prefilter_joint.md`). After the change they should read like the corpus's
other literal-run DFA patterns. That is a direction, not a number: the bench window
measures it.

### 3.2 `$` / `\Z` rev-end artifacts: the B3 movers

| population | rev-end artifacts with `end_pin = eol` | with tie code today | without |
|---|---|---|---|
| bench | **9** | 1 (`capability/tail-space-eol`, `\s+$`) | 8 |
| corpus | **257** | 42 (`[^c]{1,3}\Z`, `\s*?$`, `(?:a\|a\n)$`, `(\s+){2}$`, …) | 215 |

All 266 lose their second seed. The 43 with tie code are the ones whose cost
changes (3.00× → 1.00× or 2.00×). The other 223 cost the same, because seed `n−1`
died at once.

### 3.3 Every path-final `$`: the movers if `$` lowers on every consumer

| population | route today | patterns |
|---|---|---|
| bench | rev-end / attempt / VM | 9 / 27 / 1 |
| corpus | rev-end / attempt / VM / unanchored (`end_pin none`) | 257 / 298 / 296 / 22 |

In addition, path-final `(?m)$` appears on 2 bench and 52 corpus DFA artifacts and
14 corpus VM artifacts. Path-final negative lookaheads (which never lower) appear on
1 bench and 11 corpus patterns, all VM.

### 3.4 What could get worse

- **Forward `$` machines** (§3.3), only if Q1 picks the uniform form. The views
  (`eolvar`) become a mark accept with `back` 0/1. The state count should stay about
  the same: one "after the final `\n`" state replaces one EOL-variant state. This is
  unmeasured on pcrec itself, and it is E3's gate (§6).
- **VM frame use** on the roughly 30 corpus patterns whose tail lookahead becomes consumption (33 carry one; L3/L4 keep about 3)
  (§2.1): the give-up differential.
- **Compile time** of `mark_prio`: bounded by the DFA state cap, and asked only of
  tie-capable reverse machines (43 artifacts today).
- **No answer**, by §1.5.

## 4. Where it sits

### 4.1 The pass

`pcrec_endmark_lower(Ctx *, Ast *)` goes in a new `src/opt/endmark.c`, called from
`src/core/compile.c` **after `pcrec_discharge_atomic` and before
`pcrec_callgraph_build`**:

- **Before the call graph**, so that every fact the graph derives
  (lookaround-held calls joining TOP, K93) is derived from the final tree. L3 needs
  only the set of call targets, which is a scan of `A_CALL` nodes' `u.call.target`
  (and `(?R)`/`(?0)` for the root). It does not need the graph.
- **Before the E1 seal and `pcrec_select_engine`**, so that the kind mask, the
  widths and the engine choice all see the lowered tree. A lowered tail carries no
  `A_LOOK`, so `forces_registry`'s walk no longer finds its VM_ONLY stamp. No new
  `analyses[]` row is needed.

**In place, and never reallocating a group root** (`pcrec_lower_enc`'s discipline,
utf8s1 R2). The `A_LOOK` node is rewritten to `A_CAT(A_ENDMARK, body)`, so parent
pointers and `u.call.body` stay valid, and captures inside Y keep their identity.
The node's `reg` stamp is cleared.

### 4.2 The node

`A_ENDMARK` is a zero-width leaf with no payload. That puts it with `A_KRESET`'s
arms in the ~73 exhaustive-switch sites over 27 files that list `A_KRESET`, and the
`-Wswitch` alarm (mrl.c's rule) enumerates them. It is NOT a bare anchor for
`pcrec_is_bare_anchor`, because the user never writes it. Repeats never contain one,
since L7 only fires at max-1 tails. It is not repeatable by construction.

### 4.3 The facts it must update

The rule is the invariant in §0 item 7: facts speak consumption.

| fact | after the lowering |
|---|---|
| `end_pin` (`src/facts/endwin.c`) | a lowered `$` path ends in `\z`, so the pin is `z`. `PCREC_EPIN_EOL` keeps producers only where `$` did not lower (a mid-path `$` followed by `\z`). Its 5 readers are re-derived (§5.3). |
| `end_window` (W1) | consumed width = X's plus the tail's 1 = today's `EW_EOL_SLACK`. Same numbers. |
| `width` / `minw` / `nullable` / `empty_admits` | consumption. `(?=ab)` stops being nullable. That is right for every reader (the prefilter's nullable decline, the attempt bound), because the match cannot begin without reading `ab`. The reported span is empty, and only the caller's find-all reads that, from `caps`. |
| `kinds` (E1) | gains an `ENDMARK` bit. `LOOK` clears where every lookahead lowered. |
| `start_*` | unchanged. |
| the stamp offset `Ctx.first_vmonly_pos` | **a hazard, already live on main for the free atomic discharge (F4).** It is first-wins at parse time. If the first VM-only construct was a lowered lookahead and another remains, `RX_ENGINE_WHY` would point at a construct the tree no longer has. The fix is general: the stamp record becomes per node (an arena list of `(node, offset)`), and select_engine reads the offset of the node its walk found. That keeps "the `engine_why` text and its offset come from one place" (`mod_assertions.c`'s note). |

### 4.4 The sibling check

**The position-pin family** (compound.md's U3, D163's derivation hook) is
`start_anchor`, `end_pin`, `pin_split` and the startpos facts. After the lowering,
`end_pin` has two values that matter, `z` and `none`. That simplifies the family
rather than adding to it.

**The compound tool.** Q's derivation (P with `^`/`\A`/`\G` killed) runs on the
lowered tree, so Q's rev-end is the one-seed walk, and B4 (the compound driver)
inherits G3's 1.00×/2.00×. Captures on demand (compound.md §D,
`select-by-arg`) needs nothing new: the VM arm reports the mark (§2.1), and the
DFA arm reports `pos − back`.

**FINISH's ENDSET hand** survives, only for the state-dependent tie.
`locate_finish.md`'s `(I, e, D)` result keeps `D` = the end set. One-seed rev-end
hands `D = {n − d}` or `{n, n−1}`, so no type changes.

## 5. Interface and checks

### 5.1 Stamps and routes

No new stamp. These values move:

- `RX_ENGINE` and `RX_ENGINE_WHY` on the VM → DFA set;
- `RX_VM_PREFILTER_LANG` on the 4 captures cases (`exact`);
- `RX_REQ_RUN` (Y's bytes become necessary).

None of these adds vocabulary. `RX_DFA_SCAN "rev-end"` is unchanged. The mark is
visible in pcrec's own output, as D164 requires. In `--emit-ir`, the VM listing
shows the slot-1 write (`END_MARK`) and the DFA listing shows the back table. In
`--emit-facts`, a new pattern fact `end_mark` gives the count of lowered tails and
their `back` range, with owner `src/opt/endmark.c`.

### 5.2 abi and spec (D76/D94, D80)

**abi.** Each build step that moves emitted text is an abi event, with readers found
by grep (§5.3):

- E2: the VM's report text, the VM → DFA artifacts and the back table;
- E3: the rev-end walk, plus the forward `$` machines if Q1 picks the uniform form.

**Spec.** `match_api.md` needs no hunk: group 0's end is PCRE2's end before and
after, the find-all protocol reads `caps`, and the `_match` entries already return
"the match length". The spec hunks are:

- `facts_listing.md`: the `end_mark` row;
- `ir_listing.md`: the slot-1 write and the back table;
- `tuning.md`: one sentence that path-final lookaheads lower, so a route can change,
  with no axis row (§5.4).

The rows table (§1.3) is listed beside the `ctx-node` rows in
`src/dump/axes_dump.c`.

### 5.3 Readers by grep of the names that move

Found at `885eccff`. Each count is files / hits over `src tests scripts docs/spec`.

| name | files / hits | what happens |
|---|---|---|
| `revend_tie` | 4 / 18 | deleted; S765/S766 re-aimed at the tag-set arm |
| `revend_seed` | 15 / 23 | the loop goes; S758/S759/S760 re-aimed |
| `nl_last` (`revend_nl_last`) | 4 / 10 | becomes "an accepting reverse state carries ≥ 2 distances"; S767 re-aimed |
| `PCREC_EPIN_EOL` | 4 / 5 | re-derived (§4.3) |
| `CAND_HAND_ENDSET` | 4 / 17 | survives; its population shrinks |
| `report_captures` | 3 / 16 | gains the slot-1 arm (mark artifacts only) |
| `last_accept_position` | 15 / 64 | gains `− back[state]` where a back table exists |
| `emit_search_success` | 5 / 12 | reads the reported end |
| `NFA_ERASED_LOOK` | 6 / 6 | not set for a lowered tail |
| `pcrec_has_lookaround` | 12 / 20 | false where every lookahead lowered (`mrl_win` arms) |
| `first_vmonly_pos` | 8 / 13 | per-node (§4.3) |

`tests/codegen/run_rev_end.sh`, `run_dfa_stamps.sh` and `run_premul_table.sh` read
the rev-end text. The byte-count reader class must be run, not grepped:
`cpset`'s EMITTED_BYTES manifest, the resource rungs, the recursion-identity FILEPIN,
emit_sweep's pins, and the startset manifests (`k7980`/`revtri`/`sltri` precedent).

### 5.4 The lever (D163 addendum 2's shape)

There is no flags bit and no `-fno-…`. One internal, harness-only force-off
(`--harness=no-endmark` on `build/pcrec-harness`, which compound's B0 builds)
compiles today's tree: no pass, no mark. The artifact self-marks `"forced-off"` in
its facts listing. `make test-axes` runs it as a declared internal arm (answer
identity over the whole corpus), and bisects use it. This is the control that does
not share a source with the pass: the same compiler with the pass skipped.

### 5.5 Checks

1. **The libpcre2 differential, standing.** `tests/endmark/` runs §1.5's
   generators through pcrec, not through PCRE2 with `()`. It compiles each pattern
   (default, `--engine=vm`, `--no-captures`, `-e utf8`) and compares pcrec at every
   start position, plus find-all, against libpcre2 on the ORIGINAL pattern. The
   oracle reads the original pattern, the subject reads the lowered tree, and they
   share nothing.
2. **The lever arm.** Answer identity, and the give-up differential: the set of
   cells that give up must not grow in either direction (D158).
3. **Structural.** A `"rev-end"` artifact with `end_pin = z` emits one seed, the tag
   arm exactly when the reverse machine has a multi-distance accept, and no forward
   run when `mark_prio` is constant. A mark artifact's `report_captures` reads
   slot 1. The back table is present iff some accepting state has `b > 0`.
4. **Corpus witnesses** (`tests/endmark/*.rxt`, oracle-first, green on today's
   compiler before the build: the `rev2corp` precedent). These are the curated
   cells, the enclosing-capture cells, `a(?=aa)` find-all, the bench pair's
   shapes, `\s+$`/`\s*?$`/`(?:\s+|x\s*?)$` on final-newline subjects, and a UTF-8
   block.
5. **Census floors.** VM → DFA ≥ 2 bench and ≥ 20 corpus; rev-end-eol → one-seed
   ≥ 260. The floors are re-counted by the probe (K35), never copied.

### 5.6 Sabotage rows (ids NOT taken; **12 needed**; every row's witness is named, and its reach is proved by the witness file carrying the shape)

| row | plant | detector |
|---|---|---|
| S-EM1 | the report uses the consumed end | `tests/endmark` find-all + group 0 |
| S-EM2 | §1.4's ancestor list dropped | enclosing-capture cells |
| S-EM3 | L1 deleted (negatives lower) | `a(?!b)` cells |
| S-EM4 | the hybrid ceiling is the mark, not the consumed end | the 4 captures cases (match lost) |
| S-EM5 | the tail walk passes a max > 1 repeat | `(?:a(?=a))+` |
| S-EM6 | the tail walk passes a non-last CAT element | `a(?=b)b` |
| S-EM7 | `back` read as 0 | the bench pair |
| S-EM8 | tags merged in the reverse machine | `\s*?$` final-newline cells |
| S-EM9 | `mark_prio` returns the second accepting distance | `\s+$` / `\s*?$` |
| S-EM10 | `mark_prio` says `const` on a state-dependent shape | `(?:\s+|x\s*?)$` |
| S-EM11 | L3 deleted | a call-target tail (`(?(DEFINE)(?<n>a(?=bc)))x(?&n)`) |
| S-EM12 | the lever ignored | test-axes' internal arm reads movers where it must read none |

Re-aims: S758–S760 and S765–S767 (§5.3), plus S771 if the `-fno-rev-end` plumbing
moves. Their re-aim sites are derived by `scripts/sabotage_anchors.py --step` on
each commit's diff, not hand-listed.

## 6. Build plan

| step | content | movers / abi |
|---|---|---|
| **E0** | `tests/endmark/*.rxt` (oracle-first) and the probe promoted to a census check | none |
| **E1** | `A_ENDMARK` with every switch arm; the pass behind the lever, default OFF; VM slot 1, report and ancestor rule; NFA `ACC(b)`; the DFA back table | zero movers: emit_sweep, every stream and variant, against main |
| **E2** | the pass ON for L7 over `A_LOOK` (the multi-character lookaheads) | the VM → DFA set, about 30 corpus and 2 bench lowered programs, Y-run gains. abi event |
| **E3** | `$`/`\Z`/`(?m)$` lowered; rev-end's one tagged walk; `mark_prio`; the second seed and `revend_tie` deleted (B3) | 266 rev-end artifacts (Q1: plus the forward `$` machines). abi event. Gate: the forward state counts on §3.3's population do not grow by more than one per machine |
| **E4** | the per-node stamp offset (§4.3) | none if folded into E2 |

E2 and E3 are separable. E3 is what compound's B4 waits for.

## 7. Questions for Frank (discussion)

**Q1: should `$` lower on every consumer, or does the forward machine keep its
views?**

- *The problem.* `$` IS a lookahead (`(?=\n?\z)`), and the general rule lowers
  every path-final positive lookahead. Applied to `$` everywhere, the forward
  machines of about 890 corpus and bench artifacts move. Today they handle `$` with
  the `eolvar` view, and nothing measured says the view is slow.
- *The forces.* The house rule against parallel mechanisms says one rule, uniformly
  applied. D77 says not to move 890 artifacts without a measured gain. The views
  stay in any case, for mid-path `$`. Lowering only for the reverse walk would make
  `$` mean two things depending on which machine reads it. That is the quirky shape
  Frank's ruling rejected.
- *My leaning:* uniform, as E3's own abi event, gated on a state-count and size
  census of the moved forward machines that shows no growth. If the census shows
  growth, it is a finding to bring back, not a reason to special-case.
- *Room to disagree:* the reverse-only form is smaller and ships B3 sooner.

**Q2: should D164's "no tags, no tie special case" be amended?**

- *The problem.* §2.3 shows a reverse walk cannot see priority, so a tie must still
  be decided.
- *The forces.* Frank disliked revb3's tagged two-seed walk. The tags here are not a
  `$` fix. They are the mark's distance in the reverse direction, the same
  mechanism the forward machine uses for any bounded context, and the second seed
  is gone.
- *My leaning:* amend D164's consequence sentence to say "one seed; mark distances
  in the reverse machine; ties decided by the static priority fact or by FINISH",
  and keep the ruling's direction.

**Q3: should unbounded Y stay a lookahead (L4)?**

- *The problem.* Lowering unbounded Y gives the VM hybrid an exact prefilter. The
  DFA cannot carry an unbounded distance, so it would gain nothing there.
- *The forces.* Three corpus patterns, none bench. D77.
- *My leaning:* keep L4, and file the trigger: a bench cell with a path-final
  unbounded lookahead on a hybrid.

**Q4: should the lowered structure be visible beyond facts and IR?** D164 says
visible in pcrec's output only.

- *My leaning:* the `end_mark` fact and the IR listing, with no stamp until a
  consumer asks.

## 8. Standing questions (`docs/design/CLAUDE.md`)

1. **The measurement regime.** Relevant. Every number here is COUNTED or
   ORACLE-CHECKED; no clock was read:
   - subject-byte loads in a priority-NFA twin (exact by construction; "today"
     reproduces compound.md's measured 48,007 to 3 loads);
   - compile-side stamps on this box's build at `885eccff`;
   - libpcre2 10.46 on this box.

   The bench pair's improvement is a direction, owed to a bench window. No decision
   here would flip in a different timing regime, because none rests on timing.
2. **The independent control.** Relevant.
   - The lowering's exactness is checked against libpcre2 on the ORIGINAL pattern,
     with the mark spelled as a PCRE2 capture group. The expectation comes from
     PCRE2's lookahead semantics; the subject is the rewrite.
   - The twin's answers are checked against libpcre2 too.
   - Six plus four plants go red.
   - The census's probe is cross-checked against the shipped engine stamp (0
     disagreements on the VM → DFA set). The populations are counted by the probe,
     and the floors (§5.5) are re-counted, not copied (K35).
   - The build-time control is the lever: the same compiler with the pass skipped.
3. **What moves when data is regenerated.** Relevant only as emitted text. There is
   no data table or calibration. `mark_prio` and `back` are derived per compile
   from the pattern. The emitted bytes move at E2/E3 (abi events, readers in
   §5.3), and the spec hunks are in §5.2.

## 9. Findings

- **F1. D164's consequence sentence over-claims (§2.3).** One seed, yes. "No tags,
  no tie special case" cannot hold for a reverse walk, because priority is forward.
  What is true: the tie stops being a `$` special case and the second walk goes.
- **F2. Enclosing captures need a rule D164 did not state (§1.4).** Planted, it
  costs 2,858 cells.
- **F3. The hybrid ceiling must be the consumed end (§2.2).** This is the one place
  where reading the mark would lose matches.
- **F4. `Ctx.first_vmonly_pos` goes stale under any tree rewrite that removes a
  stamped node (§4.3), and it is ALREADY LIVE on main.** It is first-wins at parse
  time, and `Ast` carries no position. The free atomic discharge already removes a
  stamped node: `--features all 'a++b(?<=ab)'` stamps
  `RX_ENGINE_WHY "(\?<=...) at pattern offset 2"`. Offset 2 is the discharged
  possessive `+`; the lookbehind is at offset 4. The same text appears on
  `a++bc(?=de)x(?<=dex)` (lookbehind at 12). This is a stamp-value defect, not an
  answer defect, and it is worth a K entry. The per-node record in §4.3 fixes both
  the existing case and this pass's.
- **F5. The unlock is narrow (§3.1).** 2 bench and 22 corpus patterns. Most
  path-final lookaheads are one character, and those have been DFA since [UCP] U2's
  context node. The bench pair is the population that matters.
- **F6. `z(?=)` and `(?=\b)`-style tails are zero-width (L6).** They need no mark,
  and the empty lookahead disappears.
