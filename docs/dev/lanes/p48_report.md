# p48 — scan-edge admission and pricing (primed row P4+P8)

Lane p48 (opus), 2026-10-29, worktree `worktrees/p48` (branch `lane/p48`, from
b05ccfc0b). Design and measurement only: no edit under `src/`, `cli/`, `lib/`,
`memfn/`. The twins are scratch compilers (a `git archive` of HEAD with one
patch each) and hand-edited artifacts. Their sources and every raw number are in
`docs/dev/lanes/p48_evidence/` (its README.md says how to rebuild and re-run them).

## Summary

**The four O-111 regressions are not a scan edge on a short class run losing
per byte. Each is a loop-shape cost the edge drags in, and two emitter-side
facts fix them without declining any edge.** All numbers below are user-space
instruction counts per find-all pass from `perf stat` on twins at one pin. They
are deterministic on a shared box. Cycles are shown where they agree, and are
indicative only, because a queue `make test` was running.

1. **base10num (both cells; ~86-95% of the loss): the seeded entry dispatch.**
   `[SCANEDGE-SET]` made the lookbehind's "blocked" state a scan-edge head:
   the state after a byte of `[0-9.+-]` that no match may start behind, whose
   self-loop set is `{+-, ., digit}` and whose every exit goes to `s0`. That
   state is also a SEED target: every find-all call after a number starts in
   it. So the emitter adds the
   loop-entry `goto` into the edge path (`emit_scan_loop`'s `seedhead`).
   That jump into the middle of the loop costs gcc two instructions per byte
   in the candidate-start skip loop (7 -> 9), on bytes no edge ever sees:
   - `t-trim-match-60k`, which holds no candidate byte at all: **+28.5%
     instructions**;
   - `t-1m`: +18.6% instructions and +23% cycles. The bench measured x1.20 on
     this cell.

   The jump is needed only where the head's class cells were KILLED, which is
   a BOUNDED chain. An unbounded head keeps its self-loop cells, so the
   ordinary step reaches it by itself. A twin compiler that asks "bounded
   head" at the four entry sites removes the loss:
   - `t-1m`: +1.0% instructions over pre-SET (it was +18.6%);
   - `t-trim-match-60k`: 0.0%;
   - VM `-grok` `t-1m`: +0.8% (it was +10.7%).
2. **cls-s-uc (`\S+@\S+`): a stay skip re-spelled as a scan edge.**
   - Before SET, the post-`@` state already had a STAY skip, the same cursor
     loop. SET made it an edge head, and an edge head is excluded from the
     stays.
   - The per-byte loop is identical: 6 instructions per byte in both the
     micro-benchmark and the artifact. The edge adds +5 instructions per
     entry plus the edge-path loop shape.
   - On syntax `t-1m`: +5.5% instructions, +17% cycles. The bench measured
     x1.12.
   - On the same text with every `@` removed, where the edge runs once:
     still +5.6% instructions. So the cost is the loop shape, not the scan.
3. **cls-range (`0x[0-9a-fA-F]+`, x0.82 faster) and `\s+$` (I-163, x6) are
   real wins of the same mechanism.**
   - cls-range: the edge replaced table steps on hex runs of mean 2.93 bytes
     after entry (measured), so −12.7% cycles at equal instructions.
   - `\s+$` on `t-trim-match-60k`: −60% instructions, x0.29 cycles.
4. **Break-even, measured (anchored micro-benchmark, 22 run lengths x 3 shapes).**
   - Costs: a table step is 13 instructions (~5.8 cycles) per byte. A range
     or bitmap edge is 6-7 instructions (~2 cycles) per byte, plus a fixed
     14-17 instructions per entry.
   - **Break-even k\* = 2.3-2.4 bytes after the entry byte** in
     instructions (crossing measured at a total run of 4 for both forms),
     and about 1 byte in cycles.
   - Against a stay skip the edge has **no per-byte gain** (6 = 6), so it
     never breaks even.
5. **A context-blind byte prior cannot do the admission.** The default
   byte-rate prior gives E[k] = p/(1−p) under an iid model.
   - It is right where runs are unconditioned: base10num's blocked state
     predicts 0.10 bytes and measures 0.10 on `t-tail-digits-1m`.
   - It is wrong by up to five orders of magnitude where the pattern's
     context sets the run:
     - hex after `0x`: predicts 0.44, measures 2.93;
     - `\s` on a trim subject: predicts 0.16, measures ~61,000.
   - Declining by it would undo both measured wins (x0.82, x0.29 cycles) to
     save 3.5 instructions per entry. A wrong admit costs a bounded fixed
     amount. A wrong decline costs an unbounded amount per entry.
6. **The one-state relaxation is sound.** Precondition (1)'s uniform exit
   exists only for multi-state chains, and an unbounded head deletes nothing.
   Its population is in [Population](#population).

**Design (one table, §Design):**
- Unbounded self-loops are admitted on structure.
- A stay-eligible state stays a STAY.
- A priced row is declared but transparent until a context-aware run
  estimate exists.
- The entry dispatch reads "bounded head".

**Leaning:** build the two loop-shape fixes as one small row (they remove the
measured losses and lose no measured win). Hold the priced row and the
relaxation behind their own triggers.

## Premise test

At HEAD b05ccfc0b, `build/pcrec -p rx --features all --pattern '\S+@\S+'`
stamps `RX_DFA_SCAN_EDGE "bitmap"`, not `"mixed"`.
- It carries one edge per machine (forward, reverse, anchored), on the
  post-`@` accepting self-loop.
- That edge's SET is two byte classes: `\S` without `@`, and `@`. The bench
  wrote "mixed" for the SET; the stamp names the edge's test form.
- The pre-SET singleton twin stamps `"none"` and gives that state a STAY skip
  instead. Trace: forward `skip 3` then `edge 3` (`p48_evidence/census.py`'s
  trace format).

So the premise holds in substance: a set-shaped scan edge was gained. The
stamp value is `"bitmap"`. The two base10num cells stamp `"mixed"` (range +
bitmap) and the pre-SET twin stamps `"range"`, which is the bench's
`range -> mixed`.

## The regressions

Twin arms (all on this box at b05ccfc0b; `p48_evidence/cells_measure.txt`):

- `set`: HEAD.
- `single`: HEAD with `shaped()` admitting singleton sets only, i.e. the
  pre-[SCANEDGE-SET] criterion (`patch_single.py`).
- `none`: HEAD with `-fno-scan-edge`.
- `nogoto`: the `set` artifact with its one `seeded straight onto a scan-edge
  head` line deleted by hand.
- `ng`: a twin compiler whose four entry-head sites test `scan_span > 0`
  (`patch_nogoto.py`). It emits text identical to `nogoto`.

Driver: `drv.c`, find-all with the bench's advance, matcher in its own TU at
`-O2 -fPIC`.

| cell / subject | set | ng | single | none | bench |
|---|---|---|---|---|---|
| base10num-noatomic / cap `t-1m` (ins) | 19.86M | 16.92M | 16.75M | 15.82M | x1.205 |
| same, cycles | 9.0M | 7.26-7.40M | 7.24-7.62M | 6.8-7.1M | |
| base10num-noatomic / `t-trim-match-60k` (ins) | 553.6k | 431.4k | 431.4k | 431.4k | x1.35 |
| base10num-noatomic / `t-hyb-datepath-16k` (ins) | 830.1k | 762.6k | 781.5k | 718.2k | x1.31 |
| base10num-grok (VM) / `t-1m` (ins) | 32.29M | 29.40M | 29.18M | 28.25M | x1.087 |
| base10num-grok / `t-trim-match-60k` (ins) | 554.3k | 431.5k | 431.4k | 431.4k | x1.33 |
| cls-s-uc / syntax `t-1m` (ins) | 14.45M | — | 13.70M | 13.70M | x1.116 |
| cls-s-uc / `t-1m` with no `@` (ins; cycles) | 13.49M; 9.73M | — | 12.78M; 7.70M | 12.78M; 7.58M | |
| cls-range / syntax `t-1m` (ins; cycles) | 1.2571M; 502k | — | 1.2579M; 575k | 1.2579M; 584k | x0.816 |
| `\s+$` / `t-trim-match-60k` (ins; cycles) | 369k; 120k | 369k | 922k; 412k | 922k; 412k | I-163 x0.164 |
| secrets-username-password / `t-hyb-embed-64k` (ins) | 344.6k | — | 347.4k | 353.9k | flat |

**base10num: the mechanism.**
- The forward machine's state 20 is the lookbehind's blocked state. Every
  byte of `[0-9.+-]` keeps it there, every other byte returns to `s0`
  (`rx_forward_next_state` row `0,20,20,20`). That is a uniform exit over a
  three-class set, so SET admitted it as an unbounded edge.
- The machine is `seeded` (`(?<!...)` reads the byte before `search_from`).
  Every find-all call after a match starts with the previous byte a digit,
  i.e. ON state 20. So `dfa_seed_can_be_scan_head` is true, and the emitter
  writes `if (is_stop && !is_dead) goto rx_forward_scan_edge;` in front of
  `for (;;)`.
- That second entry into the loop body is the whole cost. In
  `perf annotate`, the set arm's skip loop is
  `movzbl; cmpb; jne; mov; add; mov $-1,%r9; xor %ecx,%ecx; cmp; jb`:
  - the two constants `last_accept_position = -1` and `state = 0` are
    rematerialized on every skipped byte;
  - the single arm's loop is the same seven instructions without them;
  - deleting that one line (`nogoto`) restores the seven-instruction loop
    byte-identically (431,399 vs 431,396 instructions on the trim subject).
- What the edge itself does on these subjects: on `t-1m`, state 20 is
  entered 49,151 times (once per call) and scans **0 bytes**. The fraction
  state 24 is entered 6,000 times and scans 0 (`run_lengths.txt`).
  - The residual `ng` vs `single` (+170k instructions, +3.5 per entry) is
    the edge's own fixed cost on empty runs. That is +1.0% on the cell,
    inside every noise band.
  - On `t-hyb-datepath-16k` the edge scans 1.1 bytes per entry, and `ng` is
    2.4% FEWER instructions than `single`.
- The VM `-grok` cell has the same DFA (the hybrid's locate machine) and the
  same line, with the same result.

**cls-s-uc: the mechanism.**
- In the single arm, the post-`@` state 9 is the stay skip `stay3` (232
  stay bytes, which is at least the stay rule's 192). In the set arm it is
  the edge head `scan3`.
- The `@`-free control shows the run is not the cost: the edge runs once
  there, yet +0.71M instructions remain (+5.6%). They sit on the per-word
  generic path:
  - an extra bound re-check after the prefilter and the stay loop (`jmp 9f`
    instead of straight into the step);
  - a table-address `lea` rematerialized at the `stay1` entry, from one more
    live table base.

  That is about 4 instructions per word over ~170k words. The edge's own
  per-entry cost is the micro-benchmark's +5.

**What the bench null band means here.**
- The capability ±19.92% band is a statement about the bench's wall-clock
  trials. It does not apply to instruction counts, which are deterministic.
- x1.20 sits on the band edge as a timing. It is nonetheless real: the twin
  reproduces +18.6% instructions and +23% cycles on the same cell, and +28.5%
  on a subject where the edge never runs. A mechanism that reproduces
  structurally is not noise.
- So no one-pass-loss-chasing ruling is needed for base10num or cls-s-uc.
  The residual after the fixes (+1.0%, +0.8%) is the near-noise kind that
  ruling covers, and I do not chase it.

## Break-even

**Method.** `drv_anch.c` calls `rx_match` (anchored) at every `x` of a 256 KiB
subject made of `x` + r class bytes + ` `, for r in {1..6, 8, 12, 16, 24, 32}.
Per-call instructions and cycles are net of a 0-iteration run, from
`perf stat -r 5` (`be_run.sh`, `breakeven_measure.txt`). One machine and one
edge per call; the arms differ only in the edge.

| shape | per byte, table step | per byte, edge | edge fixed (r=1) | ins crossing | cycles crossing |
|---|---|---|---|---|---|
| A `x[0-9]+` (range, singleton) | 13.0 ins, ~5.8 c | 7.1 ins, ~2.0 c | +14 ins | r = 4 (105 = 105) | r ≈ 2-3 |
| B `x[0-9a-z]+` (bitmap, a SET) | 13.0 ins, ~5.9 c | 6.1 ins, ~1.9 c | +17 ins | r = 4 (105 = 105) | r ≈ 3-4 |
| C `x\S+` (bitmap edge vs STAY) | stay 6.0 ins | 6.0 ins | +5 ins | never | equal within noise |

**Derived.** Per entry, Δ(k) = F − k·g, where k is the number of run bytes
after the entry byte, g = c_step − c_edge and F is the edge's fixed cost.
- k\* = F/g = 14/6 = **2.3** (range) and 17/7 = **2.4** (bitmap) in
  instructions.
- In cycles, F ≈ 3-5 and g ≈ 3.8, so k\* ≈ 1. The table step is a
  dependent load chain and the edge's loop is not, so cycles favour the edge
  more than instructions do.
- Against a stay, g = 0, so the edge loses by F (+5 instructions) on every
  entry.

These are measured on this box (Zen 4, gcc 15.2 -O2, loaded). The bench's
quiet-box confirmation is a bench ask below.

**The prior's estimate.**
- Under an iid byte model with p = MASS(set) from the default byte-rate
  prior, E[k] = p/(1−p).
- Admission at break-even would therefore be p > k\*/(1+k\*): **0.70
  (instructions)** or **≈0.5 (cycles)**.
- For comparison, the stay rule's 192/256 = 0.75 is a cardinality version
  of the same inequality, and M2.10's measured regression on a 2-byte
  stay set is what the inequality predicts.

| set | prior p | E[k] prior | measured k (subject) | prior decision (k\* 2.3) | measured outcome |
|---|---|---|---|---|---|
| base10num blocked `[0-9.+-]` | 0.090 | 0.10 | 0.10 (`t-tail-digits-1m`), 0.0 (`t-1m`), 1.1 (`t-hyb-datepath-16k`) | decline | ng: +1.0% / −2.4% — a wash |
| base10num fraction `[0-9]` (pre-SET edge) | 0.075 | 0.08 | 0.0 (`t-1m`) | decline | single vs none +5.9% ins (mostly loop shape) |
| cls-s-uc post-`@` `\S` | 0.862 | 6.25 | 10.0 | admit | but the alternative is a STAY: g = 0 |
| cls-range hex | 0.305 | 0.44 | **2.93** | **decline** | **edge −12.7% cycles (bench x0.82)** |
| `\s+$` `\s` | 0.138 | 0.16 | **~61,000** (trim) | **decline** | **edge x0.29 cycles (I-163 x0.164)** |

**Conclusion for the bench's ask (a).**
- A scan edge on a short class run is a small, bounded loss: F per entry,
  3.5 instructions on base10num's empty runs. It is not the mechanism of
  the x1.07-1.20 cells.
- The break-even run is about 2.3 bytes after the entry byte (instructions)
  or about 1 (cycles).
- No prior available today can say, for an unbounded run, which side of 2.3
  a deployment's runs fall on. The byte-rate prior is context-blind, and the
  reserved `run-rarity` / `markov1` bigram query (findings.md §2¶2) answers
  NONE everywhere. Even a bigram would not see "after `0x`", because that is
  the run's STATE, not its byte.
- So the edge is admitted as insurance (bounded downside F per entry,
  unbounded upside). The losses that were real are fixed where they arise,
  in the loop shape.

## One-state relaxation

**Claim (revwalk R1).** For a ONE-state self-loop, precondition (1)'s uniform
exit is not needed. A self-loop head with ANY exits may carry an unbounded
scan edge, under preconditions (2) and (3) (or [OPT-VEDGE]'s END-view
relaxation), (5) and (7) as today. (6) and (8) are not needed for it.

**Argument.** Precondition (1) exists for one reason, stated in
scanedge.c's own header:
- A multi-state chain's scan may stop early with the emitted state
  variable at the HEAD rather than at the true member u_k.
- The following ordinary step then reads `tr[head][class]` instead of
  `tr[u_k][class]`. Requiring every member to exit to the SAME target E
  makes those two cells equal.

For a one-state self-loop there is no u_k other than the head. The state
variable is exact when the scan stops, and the step reads the head's true
row, whatever its exits. The other obligations, one at a time:

- **(2) accept constant and class-invariant.** Still required: the scan
  passes positions without probing them, and a single state's bit is
  trivially constant across the run. The class-context half (`\b`) is the
  same as today's `member_ok`.
- **(3) no position view, or [OPT-VEDGE]'s END view.** Still required, and
  for the same reason. It is unchanged.
- **(4) the fall-through's accept.** An unbounded edge has no fall-through.
  Vacuous.
- **(5) worth it.** Unbounded heads are exempt today. See the Design for
  pricing.
- **(6) view-target trim and (8) prefilter reseed.** These guard a step that
  reads a KILLED cell. An unbounded head's cells are never killed: the kill
  loop runs `if (ch->span > 0)`. So a head installed without the edge path
  steps through its intact self-loop cell, and the stop test routes it to
  the edge path one byte later. Today the walk applies (6) and (8) to
  unbounded heads too. That is conservative, not needed, and declines
  rather than miscompiles. The relaxation may keep them (no change) or drop
  them (a widening, by the same argument as the entry-dispatch fix).
- **(7) emission order.** Unchanged. It is about a bounded chain whose
  fall-through is another head, and an unbounded head can be that
  fall-through. The `clash` test refuses the bad order exactly as today.
- **Deletion.** Nothing is deleted (`nmembers == 1`), so `indeg` is never
  consulted.
- **The emitted block** (`emit_scan_edge`, `span < 0`) never reads an exit.
  It advances, records A at the stop position if A is set (every passed
  position IS the head and carries A), and rejoins at the views label. The
  emitter's layout checks (heads at the top rows; no state with both a stay
  and an edge) are unaffected.

**The same argument fixes the entry dispatch.** `dfa_seed_can_be_scan_head`,
`dfa_start_is_scan_head` and the two `revend` `entry_head` writers in
`emit_dfa.c` exist so that a state variable installed ONTO a head reaches the
edge path. That matters only if the ordinary step from the head would read a
killed cell, which is a BOUNDED head. For an unbounded head the generic step
lands back on the head through its intact cell and takes the edge path then.
That costs one table step per call, against the entry `goto` that cost two
instructions per skipped byte on base10num.

**Empirical check.** Both twins (`trelax` = HEAD + the relaxation;
`tnogoto` = HEAD + the bounded-only entry) run the answer sections of
`make test`: corpus, counterk, possessify, prefilter, assertions,
anchored-match, search-pinned, revend-twin, compound. Each runs as its own
queue job (`500-p48-relaxcorpus`, `501-p48-nogotocorpus`). The verdicts are
in STATE AT HANDOFF.

**What the relaxation admits.**
- Forward split-exit runs: `\d+-`, `[^<]*</`, revwalk's T3 inner runs, and
  `foo[a-z]*bar`'s `[a-z]*`, which subset construction splits into four
  states because `b`/`ba`/`bar` prefixes re-enter it.
- Literal-alternation restart loops: `oodo|xzxj`'s `o` after `o`, a
  one-byte set. These are runs too, but of a rare byte (p ≈ 0.04).

The census in [Population](#population) counts both.

## Design

### Goals

1. **G1 (bench cells, users of logparse-style and `\S+@\S+`-style patterns).**
   Remove the O-111 losses. Target: instructions within 2% of the pre-SET
   twin on base10num (both) and cls-s-uc, at every subject in
   `cells_measure.txt`.
2. **G2 (no lost win).** Keep cls-range at ≤ 0.90x of pre-SET cycles and
   `\s+$` at ≤ 0.35x of pre-SET instructions on `t-trim-match-60k`.
3. **G3 (one mechanism).** A self-loop run has ONE selector. STAY skip and
   unbounded scan edge are two dispatches of one kit row (the ADVANCE site,
   memfn R4h), chosen in one declared table and never by two predicates in
   two files.
4. **G4 (priced, not guessed).** Every cut-over the table reads is a
   measured row (measure_store) or a declared fact (findings). A missing one
   makes its row transparent and is stamped. It is never presumed.

Priority on conflict: G2 > G1 > G3 > G4. A design that loses a measured
x3-x6 win to save a bounded few percent is wrong. Non-goals:
- SIMD forms of the run loop (the kit's thread);
- the bounded-chain floor (measured by I-82, unchanged);
- P1's landmark walk (see below).

### The table: `SCAN_SITE_ROWS` (scanedge.c, first-match per candidate state)

A candidate is a chain head the existing walk finds (bounded or unbounded),
plus, under the relaxation, every one-state self-loop. Rows are data, with a
name, a deny bit, a predicate and a verdict (memory: decisions as first-match
tables). Each row is listable (`--list-axes` already lists axis H's
candidates; [LIST-TABLES]).

| # | row | applies when | verdict | basis |
|---|---|---|---|---|
| 0 | `deny` | `-fno-scan-edge` | no edge (stays as today) | the soundness gate, byte-identical to today's deny |
| 1 | `bounded` | bounded chain, m ≥ `PCREC_MIN_SCAN_CHAIN`, preconditions (1)-(8) | EDGE, bounded | unchanged. Deletion pays in size; I-82 measured no separation at m = 2-4 |
| 2 | `stay-covered` | one-state self-loop whose stay set passes the STAY admission (today `pick_skip_states`' rule, read from the same predicate, never a copy) | STAY | edge per-byte gain 0 (C: 6 = 6 ins/byte), +5 ins/entry, cls-s-uc +5.5% ins |
| 3 | `priced-out` | one-state self-loop AND a context-aware run estimate E[k] exists AND E[k] < k\* | NONE | k\* = F/g from the loaded measurement set (Measurement card). E[k] from `run-rarity` only. TRANSPARENT while either is NONE, which today is always |
| 4 | `self-loop` | one-state self-loop; (2), (3); (7) at selection | EDGE, unbounded | insurance: downside F per entry (3.5 ins measured), upside g per byte, unbounded (x0.29 on `\s+$`) |
| 5 | `fallback` | — | NONE | |

Row 4's predicate is today's unbounded admission when (1) is kept, and the
relaxation when (1) is dropped for one state. That is one row whose
predicate widens, not a second row. The relaxation is held (Questions).

**Within the 4-slot cap** (`PCREC_MAX_SCAN_EDGES`), today's ranking is
"unbounded first, then longer chains, then lower head". It stays the same,
with one refinement: among unbounded heads, rank by descending prior mass
p, the default byte-rate's MASS over the set. Choosing which admitted edges
fill the slots is a comparison among sound options. Using the prior there
can only reorder edges; it cannot decline a measured win the way an
admission cut would. The ranking matters only once the relaxation lands,
because today no measured machine has more than 4 unbounded candidates.

**The entry rule** is a derivation in the emitter, not a table row: "the
loop-entry dispatch onto a scan-edge head is emitted iff some entry state is
a BOUNDED head (`scan_span > 0`)". It sits at the four sites above. It is
the fix for base10num, and it is general: it asks the question the dispatch
exists for, not a property of base10num.

**Why row 2 is not a special case.**
- STAY and the unbounded EDGE are the same kit ADVANCE row (memfn R4h:
  `stay_advance` / `edge_advance`, one generic ADVANCE). They differ only
  in DISPATCH:
  - STAY: a `state == X` compare on the generic path at each loop top;
  - EDGE: the shared sentinel plus the edge path.
- Row 2 is the dispatch choice, read from the stay rule's own predicate.
  It moves stay selection's AUTHORITY into the one table: scanedge.c
  annotates `run_dispatch`, and `pick_skip_states` reads the annotation
  instead of re-deciding.
- The 192-byte cardinality floor stays as the STAY row's predicate. It is
  an unmeasured constant (memory: suspect tuning constants), and the
  Measurement card is how it gets measured. Retiring it is the follow-up
  (Questions, item 3).

### What pcrec hands the kit (D146/D157: facts, not methods)

No new kit fact is needed for rows 0-2, 4 and 5, or for the entry rule.
- The ADVANCE site already carries the set, the direction, stride 1,
  `MF_SPAN_UNBOUNDED` or the span, the peek/step/cursor texts and the
  member test (`edge_advance`, `stay_advance`).
- The kit owns the loop text, and nothing here changes it. The entry rule
  and row 2 change which site pcrec states and where pcrec's own dispatch
  text sits.

For row 3 (when its trigger fires), pcrec reads the per-entry and per-byte
costs of the ADVANCE site's forms from the loaded measurement set, under
keys the kit owns (the card below). It states no method: pcrec asks "what
does an ADVANCE over this set cost per byte and per entry, against the
walk". The kit answers with its own form's row, in the same way the window
family's phase-1 reply works today. If the kit later serves a SIMD ADVANCE,
the answer changes and k\* moves with it, with no pcrec edit.

### The three standing questions

1. **Measurement regime: relevant.**
   - k\* is per-entry latency-bound work: anchored single calls with
     dependent table steps in the no-edge arm, and branch-predicted run
     loops on fixed-length runs in the edge arm.
   - A regime with mixed run lengths adds a loop-exit mispredict to F
     (both arms take a branch on exit, but only the edge arm's is a tight
     loop's). F is then larger and k\* moves up. The decision rows that
     read k\* (row 3) are transparent today, so no shipped decision flips.
   - Instructions and cycles disagree by a factor of about 2 on k\*. The
     cycles figure is the objective, and it needs the quiet box (bench ask
     b).
2. **The independent control: relevant.**
   - The table is checked against the pre-SET singleton twin and the
     `-fno-scan-edge` twin on the bench's cells. Neither shares a source
     with the predicate under test: one is the old predicate, the other
     the pass removed.
   - The bench's own wall clock on `pcrec-auto-noedge` (ask a) is the
     outside control.
   - Population is counted by the twin trace, not by the stamp
     (`census.py`; the stamp folds machines and cannot count edges, which
     is scan_edge_ladder's lesson 2).
   - Sabotage: rows 2 and 4 each need a witness. Row 2: cls-s-uc's forward
     state 9 must be STAY. Row 4: `\s+$`'s reverse edge. The entry rule
     needs base10num-noatomic's forward machine, a seeded unbounded head
     with no entry jump, and a bounded seeded head WITH one. S213 (the
     criterion loosened) keeps its role.
3. **What moves when the data is regenerated: relevant.**
   - Rows 0-2, 4 and the entry rule read no data. Their movers are a
     one-time abi event: the entry line disappears from seeded-unbounded
     artifacts, and stays return on set-stolen states. That needs readers
     by grep (D76/D94), a `tuning.md` §2.18 hunk for the stay precedence
     and the entry rule (D80), and the `match_api.md` §6.3.4¶10 value-set
     sentence if any stamp value moves.
   - Row 3 reads the measurement set and `run-rarity`. A re-measured set,
     or an analysis carrying a bigram block, moves which self-loops get
     edges. That is a `<PREFIX>_MEASURES` / `<PREFIX>_FINDINGS` stamp
     change by construction (measures.md §4, findings.md §5), not an abi
     event.

### How it interacts with P1 (reverse walk) on cls-s-uc

- P1 (revwalk's T2 walk) replaces cls-s-uc's ROUTE: a landmark `memchr('@')`,
  then a back-scan over `\S` and a forward run, all through the kit's
  ADVANCE (widened to a step sequence).
- This design does not tune for cls-s-uc. Row 2 is general: any
  stay-eligible state keeps its stay. On cls-s-uc it restores the pre-SET
  machine, which is the measured better spelling of the same loop today.
- When P1 lands, cls-s-uc's forward DFA is no longer on its route, so row
  2's choice there stops mattering. P1 cannot be undone by it, because P1
  reads the same ADVANCE row through a different site.
- In the other direction, P1 does not need the relaxation. Its runs are
  kit segments, not DFA states. The relaxation is for forward machines and
  for the T4 reverse DFA, which P1 keeps.
- The two are halves, not competitors: revwalk's question 1, answered from
  this side.

## Population

(filled from the census below)

## Measurement card

**Card `kit-advance@1`** (owner kit; the quantities the priced row reads; method
`measure_sets.md` §7.2's shape). It is added to the canned grid when row 3's
trigger fires. Until then the rows are UNMEASURED and row 3 is transparent.

| owner | quantity | ver | dims | unit | subject | lengths | gate |
|---|---|---|---|---|---|---|---|
| kit | `beta` | 1 | form (ADVANCE-range, ADVANCE-bitmap, ADVANCE-kit); dispatch (EDGE, STAY); dir | ratio to the walk's per-byte cost | streamed, run bytes | r in {1..6, 8, 12, 16, 24, 32} | pair-per-group, as `beta` |
| kit | `f` | 1 | form; dispatch; dir | walkbytes per entry | fresh, k = 0 runs | n/a | as `f` |
| pcrec | `walk` | 1 | dir; table form (premultiplied, indexed) | ns/byte | the unit row (`kit.beta.WALK.DFA_SCAN`) | — | — |

- Derived row: `xover.ADVANCE.<form>.<dispatch>` = f / (1 − beta), in
  walkbytes. That is k\*.
- The method is `be_run.sh`'s, generalized: interleaved arms, rounds per
  measure_sets.md, and cycles on a quiet box.
- Witness subjects:
  - A/B/C above;
  - the reverse direction (a `\s+$` rev-end shape);
  - the STAY-dispatch arm on a machine with 4 stays, so the generic-path
    compare cost of STAY is in the row and not assumed zero.

## Bench asks

a. **Yes to `pcrec-auto-noedge` on the five cells**: both base10num, cls-s-uc,
   secrets, cls-range. Also add `\s+$` (`tail-space-eol`) as the win control.
   The pair at one pin is the clean A/B that O-111 lacked. Prediction from
   the twins (cycles): noedge is faster than auto on base10num (both) by
   about 15-20% and on cls-s-uc by about 10%; slower on cls-range by about
   15%; much slower on `tail-space-eol`.
b. **When a build lands (no build go yet):** run the same five cells at that
   pin. The prediction is that base10num returns to within the null band of
   9ae59f5d4 and cls-s-uc to 9ae59f5d4's figure.
c. **Not asked now:** a quiet-box cycles run of the break-even micro (A/B/C)
   would turn k\* (cycles) into a measured row. It is owed only when row 3's
   trigger fires.

## Questions for Frank

1. **Should we fix the losses where they arise, rather than by pricing the
   edge away?** The measured losses are a loop entry the edge did not need,
   and a stay skip re-spelled as an edge. Both are emitter-side facts with
   a soundness argument, and together they bring every regressed cell back
   within 1% of pre-SET without touching cls-range's or `\s+$`'s wins.
   - Pricing edges by today's byte prior would instead decline exactly the
     two big wins (x0.82, x0.29).
   - My leaning is one small build row: bounded-only entry plus stay
     precedence, an abi event with a spec hunk. The priced row stays
     designed and transparent.
   - Do you see a reason to want the price in the first build?
2. **The one-state relaxation: build it with that row, or hold it?** It is
   sound and small (one predicate in scanedge.c). It admits forward
   split-exit runs (`\d+-`, `[^<]*</`, `foo[a-z]*bar`) and revwalk's inner
   runs. It also admits rare-byte restart loops in literal alternations,
   which only the priced ranking would keep out of the 4 slots (census in
   Population).
   - My leaning is to HOLD it until a measured cell wants it, per
     build-under-measurement. A forward split-exit run cell would be the
     trigger, or P1's T4 path.
   - It would then come with the ranking refinement.
3. **The stay rule's 192-byte floor is a cardinality guess.** Under the
   break-even it is the inequality p > 0.70 with a uniform prior instead of
   the byte-rate one. M2.10's measured regression is what that inequality
   predicts. Should STAY's admission move into the same table as a priced
   row, reading the same card?
   - My leaning is yes, but as its own later row, because it moves stays on
     today's corpus. It is filed, not scheduled.
4. **Do we want a context-aware run estimate at all?** Every pricing row here
   is blind without one. Neither the byte-rate prior nor a bigram can see
   that hex follows `0x`. Only a per-state run profile (PGO-like) can. That
   is a new dataset with no home today (new-dataset lens).
   - My leaning is no, not now: insurance admission is cheap.
   - I file it as a BOONIES row so the idea is not lost.

## STATE AT HANDOFF

(filled at the end)
