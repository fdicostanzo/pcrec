# Lane altd: design of candidate D, first-byte dispatch of VM choice points

Lane altd (opus), 2026-10-29. Design and measurement only (no build go).
Nothing under `src/`, `cli/`, `lib/` or `memfn/` changed. The worktree is at main
13056c942. The base for every twin is lane/trailgc's emitted C (D183, head
801ad1214, `worktrees/trailgc/build/pcrec`) and lane vmbc's B+C twin of it
(`scratch/vmbc/b/*_BCd`), both read only. Twins, subjects and logs are in
`/var/tmp/pcrec-pcrec/scratch/altd/`. The generator, the checkers and the raw
numbers are copied to `docs/dev/lanes/altd_evidence/`. The bench checkout was
only read.

## Summary

- **What D is.** One rule for every VM choice point, not only alternations: *a
  continuation whose first consumed byte cannot be the next subject byte is not
  tried, and no frame is pushed for it*. The emitted form is a `switch` on
  `subject[scan_position]`. Each byte class (bytes with the same candidate list)
  jumps to its own chain. That chain pushes only between its candidates, in the
  ORIGINAL order. One candidate means no push. No candidate means fail.
- **Where it sits.** It is a pass over the emitted VM PROGRAM, the same flow
  graph B+C's SLOT-FLOW pass builds (push -> resume edges, region exit -> return
  labels). FIRST+ is one backward least-fixpoint dataflow over that graph. It
  is not an AST pass and not a new branch inside `vm_alt`. The alternation
  island ([ENG-ISL] STEP 1) stays as it is, and D takes the choice points the
  island declines. The DFA route has no choice points, so it has no stake. The
  kit has no stake either (D is not a search site).
- **Measured on twins.** Instructions per call, M, warm, `_in` NF=4M NT=64M.
  Cycles are the minimum of 5 at load 6.8-7.0.

  | subject | stock | B+C | **B+C+D** | pcre2-jit | cycles B+C+D vs jit (B+C was) |
  |---|---|---|---|---|---|
  | nest-paren-32k | 31.07 | 25.04 | **3.73** | 10.35 | **x0.52** (x3.89) |
  | nest-brace-100k | 162.72 | 91.02 | **16.71** | 50.40 | **x0.25** (x1.91) |
  | js-1m | 260.71 | 72.63 | **42.65** | 58.58 | **x0.89** (x1.39) |
  | idents-1m | 191.67 | 91.73 | **57.78** | 82.09 | x0.70 (x1.17) |
  | splice-1m | 47.76 | 20.42 | 19.76 | 23.66 | x0.73 (x0.79) |
  | comment-5m | 220.97 | 133.47 | **103.96** | 86.50 | x1.15 (x1.46) |

  - **Default depth.** Nest-brace goes 511 -> **2046** levels (frames bound:
    1 per level, the linked call). JSON goes 291 -> **408**. The specimen
    `^(a(?1)?b)$` goes 1024 -> **2049**.
  - **Pushes per subject byte**, B+C -> B+C+D: nest-paren 11.0 -> 0,
    nest-brace 12.0 -> 0, js 1.84 -> 0.44, idents 2.15 -> 0.90.
- **Answers.** The twins are answer-identical to stock on 99 cscan and 161 JSON
  subjects, every capture, at 7 capacities each (7,280 cells, 0 differences).
  They never give up where stock answered. Two harness samples with a
  soundness-maximal twin rewriting every generated matcher gave 103/0 and
  1,269/0. **The first sample found a real trap** (see Soundness: commit
  opacity). It was fixed in the rule, and the numbers above are after the fix.
- **One general rule needs one declared exception, for loop iterations.** A
  loop's iteration choice is re-entered on every iteration. So a dispatch that
  saves nothing on the body's own bytes costs a `switch` per iteration. Rewriting
  every choice point regardless of kind cost idents +11 % and splice +19 %
  instructions. The admission table's loop row removes that cost (see Design).
  It has no tuning constant.
- **Not run (box lock refused, queue jobs ready): the full census and the
  corpus-wide twin run.** They are the build's STEP 0 / 0b, with commands in
  Measurement card. That follows vmbc's precedent; this lane owes no run.

Goals, in priority order:

1. **No answer moves.** Every corpus cell is identical, captures included,
   under the twin and then under the build.
2. **The recursive and scanner bench members get within x1 of pcre2-jit.**
   Measured on the B+C+D twin: nest-paren x0.52, nest-brace x0.25, js x0.89.
3. **Depth bound by call frames, not choice points.** Nest-brace 2046, JSON
   408, specimen 2049.

Non-goals: no change to capacities, the DFA route, the island, or the kit.

## Premise test

**Holds.** On the B+C twin, nest-paren-32k pushes **11.0 frames per subject
byte**. Every `(` and `)` falls to arm 8 of the 11-way `items` alternation
(`[^\w$\x80-\xff"'/{}<%]`). Arms 1-7 are pushed and fail first, and two of
them (pp-number, nested block) push an inner frame of their own.

Dispatching only the alternation chains (twin `BCd_A`) takes 25.04 -> 4.72 M
instructions. That is **81 % of the B+C program**, and the pushes drop to 1.0 per
byte. The last push is the possessive items loop's own iteration frame, which
stage 2 removes (3.73 M, 0 pushes).

So vmbc_report's reading (the post-B+C gap is the 10-way alternation tried one
branch at a time) is confirmed, with one correction: the alternation is
11-way. vmbc's other claim also holds: every remaining default-depth limit was
the choice-point count. After D, nest-brace binds on call frames alone.

## Existing mechanisms

What already exists, and what D takes from each:

| mechanism | where | relation to D |
|---|---|---|
| [ENG-ISL] STEP 1, the alternation island | `src/gen/emit_vm.c` `vm_isl_build`/`vm_isl_emit`, `tests/island/`, tuning §2.20, `VM_ISL_MIN_BRANCHES` | Literal-only alternations become a byte trie. Its root `switch (subject[scan_position + 0])` IS D's dispatch for singleton-byte arms. It declines classed arms, calls, captures and empty arms, which is exactly D's population (cscan's 11-way, JSON's 5-way). **Kept; D takes what it declines.** The `switch` emitter should be ONE primitive shared by both (Build plan, stage 1). |
| [ENG-ISL-S2] (filed): tail form, CLASS-MEMBER expansion | plan.md | D is the general form of the class-member shape (classed first bytes). Its D77 trigger ("a real cell losing to serial alternation-try cost") is met by nest-paren (x3.9 of jit). **Fold the class-member half into D.** The tail form (`ab[cd]|abx`) stays with the island. |
| `alt_dispatch_study.md` algorithm (b), first-byte grouping | `studies/alt_dispatch/` | (b) is D for literal arms without resume. Study §5 items 5 and 9 left open what continuation backtracking costs; D answers it (a class chain is `vm_alt`'s chain over a subsequence, so resume is unchanged). |
| START SET fact `pcrec_start_set` | `src/facts/startset.c` (D148) | A whole-pattern superset of first bytes on the lowered tree. **Not reusable as-is.** It treats a callout as zero-width (text ZERO), does not model cuts, and does not follow calls. D asks a different question: "can this continuation succeed with this next byte, with no visible effect if not". |
| the kind row's PATH column | `src/core/kindrow.def` | **D is a PATH reader**, the column's stated client ("backtracking here cannot change the outcome"). OPAQUE (`A_BREF`, `A_CALL`, `A_VAR`, `A_CALLOUT`) and GATE (`A_LOOK`) are exactly D's non-droppable kinds. D needs no new column. |
| possessify's `first_of` / follow-set test | `src/opt/possessify.c` | A sibling path reader (code points, pre-lowering, D148 Q4). It drops a loop's frames for good when body and follow are disjoint; D drops them per byte. They do not overlap at run time (a possessified loop has no exit frame to dispatch). |
| B+C's SLOT-FLOW program graph | vmbc_report.md (P3, the next VM build) | **D's host.** The same graph (fall-through, gotos, `PUSH(L) -> L`, region exit -> every return label) carries FIRST+ as a second dataflow. |
| [ENG-DIRECT], [DD-11.5], kindrow/selector tables | plan.md | [ENG-DIRECT] re-codes frames-1 artifacts as automata: D can move artifacts INTO frames-1, which grows its population (it does not overlap). [DD-11.5] covers anchor and span context: none. |
| DFA route | `src/ir/dfa.c`, `emit_dfa.c` | No choice points: a DFA state already dispatches on the byte. No stake. |
| memfn kit | `memfn/` | Not a find/scan/skip/verify site and no delegation, so D157 is not engaged. No stake. |

## Design

### The rule

> **FIRST-DISPATCH.** At a choice point with continuations `c1 .. cn`, in
> preference order, let `F(c)` be a superset of the bytes `c` can consume first
> when it succeeds, and `E(c)` say whether `c` can succeed at the end of the
> subject. For a next byte `b`, the candidates are `[ci : b ∈ F(ci)]` in the
> original order (at the end: `[ci : E(ci)]`). Try only those, pushing a frame
> only between them.

An n-way alternation is `n` continuations. An optional `X?` is `[X, skip]`. A
loop iteration is `[body, exit]` (lazy: `[exit, body]`). Cursor-rung retreat
frames and lookaround frames are not choices between continuations at one
position, so D leaves them alone.

### FIRST+ on the program graph (where it sits)

`F` and `E` are one backward least fixpoint over the VM program graph. This is
the graph B+C build, read from the emitter's event stream, not from text:

| row | program statement (event) | contributes |
|---|---|---|
| 1 | consuming class test (`consume C L`) | `F ∪= C` (the lowered BYTE class: UTF-8 lead bytes, caseless already folded at parse). Its fail path is `fail`, so nothing more. |
| 2 | island switch / single-child compare at depth 0 | `F ∪=` the case bytes |
| 3 | cursor-rung span (`while (C(subject[cur]))`) | `F ∪= C`, then continue as if it ran zero times. If its reach test demands at least 1 iteration, stop. |
| 4 | `PUSH(L)` | continue AND fork to `L` (both are tried at this position) |
| 5 | non-consuming conditional goto (anchors, `\G`, `PRUNE_TOO_SHORT`, reach tests) | fork to the target, continue |
| 6 | slot write, mark write, work charge, trail checkpoint, call frame entry | continue (trailed or undone on the failure path, so not an effect) |
| 7 | **CUT** | **OPAQUE** (`F = all bytes`, `E = true`): the commit-opacity rule below |
| 8 | callout / code site ([INLINE-C]) | **OPAQUE**: running it is visible (kind row PATH = OPAQUE) |
| 9 | backreference compare, `${var}`, lookbehind read (`subject[pos - k]`) | **OPAQUE** (kind row PATH = OPAQUE / GATE; stage 3 may refine lookbehind) |
| 10 | region exit `goto *call_ret` | fork to every return label of the region (FOLLOW through returns; the union is a superset) |
| 11 | accept | `F = all bytes`, `E = true` |
| 12 | `fail` | nothing |
| 13 | anything unrecognised | **OPAQUE** (refuse to optimise) |

A future verb ((*COMMIT), (*PRUNE), (*SKIP), (*THEN), (*MARK); REJECTED or
OUT-OF-SCOPE today) arrives as a new event. Row 13 makes it OPAQUE until
someone writes its row. Leaving it OPAQUE is the correct row: a verb before the
first byte is an effect.

### The admission and emission table (first match per choice point)

| row | site (emitter role) | admit when | emit |
|---|---|---|---|
| 1 | flat alternation the island admits | the island's own rules | island trie (unchanged) |
| 2 | alternation chain, n >= 2 (`vm_alt`) | some byte class drops a continuation | `switch` -> per-class chains |
| 3 | optional `X?` / `X??` | same | same |
| 4 | loop iteration (`the loop's ONLY frame`, `another iteration preferred`, lazy mirror) | **some byte of `F(body)` drops the exit**, so the iterating path itself gets cheaper | same |
| 5 | otherwise | — | the stock push chain |

Row 4 is the measured exception. Re-entering a loop pays the `switch` once per
iteration, but a dispatch that drops a continuation only on the exit's bytes
saves a push only once per loop.

- **Measured.** Rewriting every choice point instead of using row 4 costs
  idents +11 % (60.37 -> 67.13 M) and splice +19 % (19.76 -> 23.42 M).
- **Applying row 4's test to optionals is also wrong.** That loses js
  42.65 -> 44.34 M, because an optional's common bytes are the ones that skip
  it.
- So the row is keyed by the KIND of site, a structural fact, and carries no
  threshold.

### Emission

The emitted text for one dispatched site:

```c
    if (scan_position >= subject_length) goto <eos chain>;
    switch (subject[scan_position]) {
    case 48 ... 57: goto <chain {2}>;          /* GNU case ranges */
    case 46: goto <chain {2,8}>;
    ...
    default: goto <chain of the largest class>;
    }
<chain {2,8}>:  PUSH(<chain {2,8}>_1, scan_position); goto <arm 2>;
<chain {2,8}>_1: goto <arm 8>;
```

- **Arm bodies are emitted once.** Chains share them through their labels.
- **The frame discipline is unchanged.** At most one frame is live per site at
  any instant, so `vm_count_slots`'s frame requirement never grows.
- **The push count is per class.** The static push-site count becomes the sum
  over classes of (candidates − 1). It must be counted by the same
  `vm_count_slots` walk that emits the sites, as the island's `isl.pushes`
  already is.
- **gcc lowers the `switch`** (jump table or compare tree). The class-index
  table + computed goto alternative was not measured. The island already emits
  this `switch` shape.
- **Deny flag:** `-fno-first-byte-dispatch` (name per D174: says what the
  caller sees). It gives byte identity wherever the table declines, and it is
  the build's A/B control.
- **Observability:** `--emit-ir` roles ("dispatch: byte class {..} tries
  branches 2, 8"). No new header stamp now; [IFACE-PUSH] batches stamps.

### Interaction with B+C (P3) and D183

- **B+C first, then D**, per Frank's ruling, and D is easier for it. D is a
  second dataflow on B+C's program graph. It needs that graph, its event-stream
  reader, and its rewrite step. Built alone, it would have to build them
  itself.
- **They compose.** Order matters only slightly. D removes pushes, so it
  removes push-edge reads, and B can find a few more dead writes if it runs
  after D. Run D then B+C in one pipeline; the twins ran B+C then D and still
  measured the table above.
- **D alone also wins** (twin `stock_ALkf`): nest-paren 31.07 -> 9.37 M,
  nest-brace 162.72 -> 68.82, js 260.71 -> 199.93. But on stock, the JSON and
  specimen depths stay trail-bound (19, 763). D's depth gain needs B+C.
- **D183 (trail compaction) is unchanged.** D adds no backward edge and no
  slot write. `tests/vm/trail_checkpoints.py` passes on all six D twins (cscan
  heaviest path 9 / margin 255 on B+C+D; JSON 22 / 520).
- **Fewer pushes mean longer trail segments.** That helps compaction (TRAIL-SEG
  keeps the oldest entry per slot per segment).
- **K36 is unaffected.** D does not touch call linkage.

## Soundness

**Claim.** For a byte `b ∉ F(c)` (or the end of the subject with `¬E(c)`),
running `c` at this position fails, and its failure has no observable effect
beyond popping back to the frame below. Dropping `c` (no push, go to the next
candidate) is therefore indistinguishable from stock, except in work counters
and frame high-water.

**Proof sketch.** Every path from `c`'s entry, until its first consumed byte,
passes only rows 4-6 and 10. Those are pushes it pops itself, conditional
forks, trailed or undone slot writes, and calls. Its first consuming test
reads `b` and fails, because `F(c)` contains every class such a test or span
admits. Spans are modelled at zero iterations, which is exact when `b` is not
in their class.

So `c`'s whole run is non-consuming steps followed by fail. The unwind restores
every slot (TRAIL-EQ) and the position, and lands on the frame below `c`'s.
That is exactly where the dispatch jumps directly. Rows 7-9 and 13 make every
other kind of path OPAQUE, so no such `c` is ever dropped.

The traps, one by one:

- **Arm ORDER (leftmost-first).** Each class chain is a subsequence of the
  original order, and a dropped arm would have failed anyway. So the first arm
  to succeed, and every later retry order on backtracking, are stock's. A
  resume goes to the next candidate in the same chain. The class is a function
  of `subject[entry]`, which the frame's saved position makes identical on
  resume.
- **Empty-matching arms.** These are covered by `E`, and by FIRST+ walking
  through to the continuation (FOLLOW, row 10). A nullable arm whose
  continuation is unknown is OPAQUE. `(|a)b`-style arms stay candidates on
  every byte the continuation can take.
- **Captures.** Writes before the first byte are trailed (P7) and undone on the
  failure the dispatch skips. Dropping them changes no slot that any later
  read sees.
- **Commit opacity: the trap the twin hit, and the reason for row 7.** The
  first harness sample went red on `^(?(DEFINE)(?<g>a|ab))(?>(?&g))c$` against
  `abc`: expected no match, the twin matched. The factored arm `a(|b)` has an
  empty sub-arm whose walk crossed the atomic group's exit CUT and reached `c`.
  So on `b` the twin dropped the empty arm and took `ab`. In stock, the empty
  arm runs first, the cut commits, and the failure on `c` cannot reach back to
  `ab`.

  A continuation that can reach a cut before its first byte is therefore not a
  "fails harmlessly" continuation: its failure happens after a commit that may
  delete the very frame the dispatch would have pushed. The same rule fixed
  `^(?!)(?<g>a|ab)|^(?&g)c$` (a negative lookahead's body-success cut).

  The twin treats EVERY cut as OPAQUE. The exact rule only needs it for cuts
  whose mark predates the choice point (an enclosing atomic, possessive or
  lookaround). A cut whose mark is set inside the continuation only removes
  the continuation's own frames. That refinement is stage 3; the measured
  numbers already include the conservative rule.
- **Lookarounds.** Positive: `F` includes the body's first bytes, and an
  assertion that holds still needs a consuming continuation. Negative: `F`
  includes both the body-fails continuation and the body (row 4 forks it). A
  nullable body reaches its cut, which is OPAQUE. Lookbehind reads are
  OPAQUE (row 9).
- **Backreferences** are OPAQUE (row 9).
- **Atomic and possessive groups.** Their cuts are row 7. A choice point inside
  them dispatches normally, because its continuations' first bytes come before
  the group's exit cut. The items loop in cscan is `*+`, and its 11-way
  alternation is rewritten.
- **Recursion and calls.** A call frame entry is row 6 (the walk enters the
  callee). A return forks to every return label (row 10, a superset). The JSON
  5-way's arms are linked calls to `array` and `object`, and are dispatched
  through them.
- **Callouts and code sites** are OPAQUE (row 8). An arm that would run a
  callout before failing is never dropped. That matters because PCRE2 runs the
  callout (the co-* bench artifacts emit no pushes, so nothing there moves).
  Row 8 is written once, against [INLINE-C]'s final site contract, the same
  ordering B+C use for their row 7.
- **Verbs** are not implemented today. Row 13 covers them when they are (see
  Design).
- **Caseless, UTF and UCP.** D reads the LOWERED byte classes the emitter
  consumes. Caseless is folded at parse (D23), and a UTF-8 class's first test
  is its lead-byte class. No encoding-specific rule is needed.
- **Limits.** Work charges, step counts (`steps_left` per resume) and frame
  high-water only go DOWN. So D, like B+C, answers some cells where stock gives
  up: 510 cscan cells and 496 JSON cells at small caps, and 0 the other way.
  This needs a spec check that limits.md and match_api §10 promise a ceiling,
  not a count. The island already set this precedent.

**Stop rule check.** Arm order is kept in the general form (each class chain
is a subsequence), so the stop rule did not fire.

## Population

| set | patterns | VM with pushes | movers under D (stages 1+2) | sites rewritten (alt / loop+opt) | note |
|---|---|---|---|---|---|
| bench `unusual/` (all 25 `.rx`) | 25 | 7 | **6**: cscan, cscan-onig, wild-json-validate(-onig), wild-sexp-balanced, va-route | 35 / 26 (6 declined by row 4) | `census_unusual.tsv`; the 15 co-* and va-* DFA/frameless artifacts have no push |
| corpus, random 50 of 4,984 unique patterns (seed 29) | 50 | 16 (3 refused by the twin: two VM bodies in one file) | **8** (16 % of the sample; 8 of 13 analysable VM artifacts) | 14 / 4 | `census_s50.tsv`; a sample, wide interval |
| harness sample 1 (leftmost_semantics, alternation, sr_atomicity) | 12 artifacts | 12 | 10 | — | 103 cases / 0 failed |
| harness sample 2 (empty_iteration, participation_and_zerowidth, atomic_basic) | 60 artifacts | 60 | 51 (9 refused, the same two-body shape) | — | 1,269 / 0 |

- **Expected movers:** every VM artifact with an alternation, optional or
  iterated choice that some byte rules out. That is most VM artifacts with a
  push. Every mover's emitted bytes move, so the build is an abi event with an
  identity re-pin and a mover census.
- **Full counts (bench 400 `.rx`, corpus 4,984) are STEP 0** (Measurement card).
- **Remodel overlap:**
  - **B+C (P3): host, not overlap.** D is built on its program graph after it
    lands.
  - **[ENG-ISL-S2]: subsumed in part** (fold the class-member half).
  - **[ENG-ISL] island: neighbour.** It keeps its rows. The shared `switch`
    emitter is stage 1's simplification.
  - **[SITE-FRAMELESS] / [INLINE-C]: row 8 reads their final code-site
    contract.** One build at a time until [INLINE-C] closes, so D lands after it
    anyway.
  - **[ENG-DIRECT]: grows its population** (more frames-1 artifacts), no
    conflict.
  - **possessify: sibling path reader**, no conflict.
  - **[OPT-ALTHASH]: unaffected** (wide literal sets stay the island's).
- **Artifact size.**
  - **Object `.text`:** cscan B+C 16,320 -> B+C+D 16,523 (+1.2 %); JSON
    15,411 -> 15,605 (+1.3 %).
  - **Emitted C:** the twin's bytes grow +9.8 % (cscan) and +9.1 % (JSON).
    That is an upper bound, because the twin keeps the dead old chains in the
    text. A build replaces them. `RX_VM_PROGRAM_BYTES` moves, and the emitted
    code cap must be checked on the census.

## Twins and measurements

**Method.** l9look, trailgc2 and vmbc's method:

- `perf stat -e instructions:u` (and `cycles:u`, minimum of 5), per call as
  (11 calls − 1 call)/10, through drv.c's `r` mode (`_in`, NF=4,194,304,
  NT=67,108,864).
- gcc -O2.
- pcre2-jit is `gap/p2 ... jg`: libpcre2 10.46, 1 GiB JIT stack.
- The box was shared: kit job 622 held the lock, and load was 5.6-9.8.
  Instruction counts carry the decisions; cycles are indicative (±10 %).

**The generator.** `altd.py` is a scratch prototype of the pass, run
mechanically, not hand-edited. It reads the emitted C and the same pattern's
`--emit-ir` listing (for each push's role, zipped by order and checked by
count), and does the following:

- builds the label/statement graph;
- computes FIRST+ by rows 1-13, by a per-query flow walk;
- evaluates every class expression by compiling it against the artifact's own
  class helpers for all 256 bytes;
- rewrites the selected choice points.

Anything it cannot read is OPAQUE, and a file it cannot parse is refused.

| mode | rules |
|---|---|
| `A` | alternation chains only (stage 1) |
| `AL` | + optionals and loop iterations, every byte-dropping site admitted |
| `ALp` / `ALpf` | `AL` with row 4's test applied to EVERY 2-way site (rejected: loses js) |
| **`ALkf`** | **the recommendation:** rows 2-4 as tabled, FOLLOW through returns (row 10) |
| `Af` | `A` with FOLLOW (identical to `A` on these members) |

**Instructions per call, M** (`rate_instr*.txt`):

| subject | stock | D alone | B+C | B+C+D stage 1 (`A`) | **B+C+D (`ALkf`)** | B+C+D rule-all (`AL`) | jit |
|---|---|---|---|---|---|---|---|
| nest-paren-32k | 31.07 | 9.37 | 25.04 | 4.72 | **3.73** | 5.05 | 10.35 |
| nest-brace-100k | 162.72 | 68.82 | 91.02 | 23.91 | **16.71** | 18.21 | 50.40 |
| js-1m | 260.71 | 199.93 | 72.63 | 52.14 | **42.65** | 42.65 | 58.58 |
| idents-1m | 191.67 | 159.01 | 91.73 | 60.37 | **57.78** | 67.13 | 82.09 |
| splice-1m | 47.76 | 47.42 | 20.42 | 19.76 | **19.76** | 23.42 | 23.66 |
| comment-5m | 220.97 | 193.97 | 133.47 | 113.46 | **103.96** | 103.96 | 86.50 |

**Cycles per call, M, minimum of 5** (`rate_cyc.txt`, `jit.txt`):

| subject | stock | B+C | B+C+D `A` | **B+C+D `ALkf`** | D alone | jit |
|---|---|---|---|---|---|---|
| nest-paren-32k | 10.11 | 6.38 | 0.78 | **0.85** | 2.05 | 1.64 |
| nest-brace-100k | 77.91 | 24.93 | 4.75 | **3.21** | 46.40 | 13.07 |
| js-1m | 106.24 | 23.55 | 18.00 | **15.12** | 88.94 | 16.92 |
| idents-1m | 56.12 | 21.78 | 14.06 | **12.95** | 45.73 | 18.54 |
| splice-1m | 13.28 | 3.75 | 3.61 | **3.43** | 13.58 | 4.72 |
| comment-5m | 44.80 | 27.64 | 21.84 | **21.89** | 36.58 | 18.98 |

**Pushes per subject byte** (`push_per_byte.txt`; stock = B+C, since B+C move
no push):

| subject | stock / B+C | `A` | `ALkf` |
|---|---|---|---|
| nest-paren-32k | 11.00 | 1.00 | **0** |
| nest-brace-100k | 12.00 | 1.00 | **0** |
| js-1m | 1.84 | 1.01 | 0.44 |
| idents-1m | 2.15 | 1.10 | 0.90 |
| splice-1m | 0.33 | 0.33 | 0.33 |
| comment-5m | 0.50 | 0.30 | 0.20 |

**The dispatch partitions themselves** (`altd_*_BCd_ALkf.log`):

- **cscan's 11-way** splits into 11 classes: identifier bytes (182) -> arm 1
  only; 56 "other" bytes -> arm 8 only; digits -> 2; `.` -> {2, 8}; `/` ->
  {5, 6, 9}; `<` -> {7, 10}; `{` -> 7; `"`, `'`, `%` -> one arm each; `}` ->
  none.
- **JSON's 5-way value alternation** is fully disjoint: `-0-9` -> number,
  `tfn` -> boolean, `"` -> string, `[` -> array, `{` -> object, everything
  else -> fail.

**Expected depth gain** (`depth_default.txt`, `spec_reach.txt`; default arm,
2048 frames):

| arm | stock (D183) | B+C | D alone | B+C+D `A` | **B+C+D `ALkf`** | pcre2-jit |
|---|---|---|---|---|---|---|
| nest-brace levels | 85 | 511 | 92 | 1022 | **2046** | 176 |
| JSON `[[..1..]]` | 19 | 291 | 19 | 340 | **408** | 150 |
| `^(a(?1)?b)$` n | 763 | 1024 | 763 | — | **2049** | — |

- **The choice points no longer pushed:** nest-brace's 4 frames per level
  become 1 (the call). The specimen's 2 become 1, because its `(?1)?` is
  `[a-call | b-follow]`, which is disjoint.
- **What binds JSON now:** its ~5 per level is call frames plus cursor-rung
  retreat frames for `(?&ws)`. Those are not choice points, so they are an
  unlock, not D.

**Answer identity.**

- **Bench twins.** `ident.py` (vmbc's, pointed at these twins) runs the
  default arm and the `_in` arm at NF=200,000 with trail caps 8 to 4,000,000,
  and prints rc plus every capture span.
  - Subjects: cscan 99, JSON 161.
  - Modes: `stock_A`, `stock_ALkf`, `BCd_A`, `BCd_ALkf`.
  - Result: 2,772 + 4,508 cells, **0 differences**. The twins answer 510 / 496
    cells where stock gives up, and never give up where stock answered.
- **Harness samples.** `tests/harness/run.sh` ran with `CC=ccwrap.sh`, which
  rewrites EVERY generated matcher before gcc, using no listing.
  - That makes it the soundness-maximal twin: every `scan_position` choice
    point is eligible, lookaround frames included, with rule `all`.
  - `PCREC` = lane/trailgc's binary.
  - Sample 1: 103 / 0 (10 of 12 artifacts rewritten). Sample 2: 1,269 / 0
    (51 rewritten, 9 refused as two-body files).
  - Before the commit-opacity rule, sample 1 was 97 / 6 on
    `sr_atomicity.rxt`, and stock was 56 / 0 on that file. That is the trap
    recorded in Soundness.
- **D183 checker.** `trail_checkpoints.py` passes on all six bench twins.

## Measurement card

Not a find/scan/skip/verify method, so the measurement script's method cards
do not apply. These are the cards a build re-runs. Everything is under
`/var/tmp/pcrec-pcrec/scratch/altd/`, with copies in
`docs/dev/lanes/altd_evidence/`.

| card | command | reads | result file |
|---|---|---|---|
| twin build | `mk.sh {cscan\|json} {stock\|BCd} {none\|A\|AL\|ALkf\|...}` (needs `{cscan,json}.ir` from `pcrec --features all -p rx --emit-ir --pattern "$(cat PATTERN.rx)"` on `cscan-onig.rx` / `wild-json-validate-onig.rx`) | `b/K_B_M/{drv,cdrv,pdrv}`, `altd.log` | — |
| rates | `rate.sh` (`MODES=`, `SUBJ=`, `NOCYC=1`), `jit.sh` | instructions per call, minimum-of-5 cycles, pushes per byte | `rate_instr*.txt`, `rate_cyc.txt`, `jit.txt`, `push_per_byte.txt` |
| default depth | `depth.sh K MODE pd 100000` (it writes subjects under `scratch/vmbc/subj`) | largest nesting that answers | `depth_default.txt` |
| specimen | the bisect in this lane's log over `a^n b^n` with `drv d` | default reach n | `spec_reach.txt` |
| answer identity | `MODES="..." python3 -I tools/ident.py {cscan\|json}` | 0 differences | `ident_final_*.txt` |
| harness sample | `ALTD_LOG=.. TMPDIR=.. CC=ccwrap.sh PCREC=worktrees/trailgc/build/pcrec bash tests/harness/run.sh FILES` | passed / failed / rewritten | `harness*.summary` |
| D183 | `python3 -I worktrees/trailgc/tests/vm/trail_checkpoints.py b/*/rx.c` | heaviest path within margin | in this report |
| size | `gcc -O2 -c` + `size` on each twin | `.text` | `size.txt` |
| **build STEP 0 (not run)** | `scripts/boxlock run --label altd-census -- python3 -I tools/census.py worktrees/trailgc/build/pcrec OUT --list corpus_all.tsv` (4,984 patterns; and `--rx pcrec-bench/bench/*/patterns/*.rx`) | movers, sites per kind, row-4 declines, refusals | — |
| **build STEP 0b (not run)** | `scripts/boxlock run --label altd-twin -- env CC=ccwrap.sh PCREC=... bash tests/harness/run.sh` (every `.rxt`), then again with `RXTFLAGS="-fno-splice-calls --engine=vm"` | corpus answer identity before a line of `src/` | — |

**Standing questions** (docs/design/CLAUDE.md):

1. **Measurement regime (relevant).**
   - Warm repeated calls, resident buffers, one box (7700X), gcc 15.2 -O2.
   - Instruction counts decide; cycles were taken under load 6.8-7.0.
   - The one-shot regime was not measured. D touches no storage beyond frames,
     which it only lowers.
2. **Independent control (relevant).**
   - The twin reads the emitted TEXT. The build reads the event stream. So
     `altd.py` is the build's independent FIRST+ checker: it shares no source
     with the emitter (learnings §3).
   - The checker has two duties: for every site the build dispatched, every
     dropped (class, continuation) pair must also be dropped by the text
     walk; and the build must never keep a continuation the text walk proves
     droppable only where the build says OPAQUE for a stated row.
   - Answers are checked against stock's answers (`ident.py`) and against the
     oracle-verified `.rxt` expectations (harness).
   - Population: `census.py` reports refusals (K35).
3. **What moves on regeneration (relevant).**
   - The emitted bytes of every mover: the `switch`, the class chains, fewer
     push sites. That is an abi bump with readers found by grep (D76/D94).
   - The `--emit-ir` listing (new roles).
   - `RX_VM_PROGRAM_BYTES`.
   - limits.md §4 (the specimen's reach: 1024 after B+C becomes 2049, now
     bound by `nframes`) and §5¶6.
   - match_api §10.1¶1 and §10.6¶2-3 (the default-depth table).
   - tuning §2.20 (a new row beside the island) and the guide's numbers.
   - These are the same readers B+C re-pin; land D's re-pins as one more
     revision of the same paragraphs.

**Sabotage witnesses to carry into the build:**

- `^(?(DEFINE)(?<g>a|ab))(?>(?&g))c$` on `abc` (commit opacity: drop row 7 and
  it matches);
- `^(?!)(?<g>a|ab)|^(?&g)c$` on `abc` / `ac` (lookaround cut);
- an arm-order cell `(a|ab)(c|bcd)(d*)` on `abcd`;
- a nullable arm `(|a)b` / `(a|)+?$`;
- a callout arm `(?C1)a|b` on `b` (row 8: the callout must fire);
- an end-of-subject arm `(a|$)`;
- a caseless arm `(?i)(k|z)` on `K`;
- UTF-8 lead bytes `(é|e)` under `-e utf8`;
- row 4's REACH witness: idents' items loop declines;
- the JSON number optional admits.

## Build plan

**Prerequisite:** B+C (P3) landed, with its program graph and rewrite step.
That follows Frank's ruling: one build at a time until [INLINE-C] closes, B+C
next, D after it.

0. **STEP 0 / 0b** (the two boxlock commands above). Do this before any `src/`.
   - The census sizes the population and the size cap.
   - The corpus-wide twin run is the answer gate.
   - A red there is a design defect: stop and report.
1. **Stage 1: alternation chains (rows 1, 2, 5).**
   - FIRST+ as a second dataflow on the B+C graph, rows 1-13.
   - The `switch` emitter is ONE primitive shared with the island's root
     switch. A simplification: the island's depth-0 `switch` and D's class
     switch become one function.
   - `vm_count_slots` counts per-class push sites site-for-site.
   - The deny flag, `--emit-ir` roles, the abi bump with its identity re-pin,
     and the spec hunks (D80) go in the same change.
   - Gate: answer-identical to `-fno-first-byte-dispatch` corpus-wide, plus
     `altd.py` as the independent checker.
   - Witnesses: cscan, JSON, the sabotage rows.
   - Expected: nest-paren 25.0 -> 4.7 M, nest-brace 91 -> 24, js 73 -> 52.
2. **Stage 2: optionals and loop iterations (rows 3, 4).**
   - The same pass. Only the site roles it accepts grow.
   - Run REACH_ONLY for moved witnesses.
   - Expected: nest-paren -> 3.7, nest-brace -> 16.7, js -> 42.7, idents ->
     57.8. Nest-brace depth -> 2046, specimen -> 2049.
   - Stages 1 and 2 are one build in two internal stages, each checked for
     identical answers before the next.
3. **Unlocks, filed, not scheduled (D77 triggers named):**
   - **(a) Precise commit opacity** (only cuts whose mark predates the site).
     Trigger: the STEP 0 census shows row-7 declines on a losing bench cell.
   - **(b) Lookbehind as a GATE** read instead of OPAQUE. Trigger: the same,
     for row 9.
   - **(c) FOLLOW-through-returns as a possessify input.** It would possessify
     cursor rungs whose follow lies past a call return, e.g. JSON's `(?&ws)`,
     the remaining ~5 frames per JSON level. Trigger: a bench cell bound by
     cursor-rung frames, so JSON depth would be the witness if a caller ever
     needs more than 408 at default.
   - **(d) Skip the re-test.** A single-candidate class re-tests the byte the
     dispatch already proved. Entering past that test is a small saving, and
     only where the arm's first statement is that test. Trigger: a twin
     showing it at or above noise on the bench members.
   - **(e) The island's root as D.** Literal arms with more than one candidate
     per first byte would then go on into the island trie, unifying the two
     mechanisms. Trigger: [ENG-ISL-S2]'s tail form reopening.

**Estimate.** Stage 1: M, given B+C's graph (the dataflow is about 150 lines,
the rewrite and emitter share about 150 more, plus the checks). Stage 2: S.

## Questions for Frank

1. **Should D be a pass over the finished VM program rather than a change to
   how alternations are emitted?**
   - **Problem.** D needs to know, for each place the VM tries alternatives in
     turn, which alternatives can start with the next character.
   - **Forces.** At the program level that knowledge is one walk over what was
     actually emitted. Inlined calls, linked calls, islands, loops and
     lookarounds are all just program statements there. The program is also
     the same graph B+C build their analysis on.
   - **The alternative.** Doing it while emitting each alternation needs a
     second "first characters" walk over the pattern tree. That walk would
     have to know how calls, splices, possessive loops and lookarounds will
     later be emitted. That duplicates the emitter's knowledge, and the
     duplicate can go stale.
   - **Leaning:** the program pass, built right after B+C on their graph.
   - **Cost.** D cannot ship before B+C. Your ordering already says B+C
     first, so nothing is lost.
2. **Loops and optionals in the same build as alternations?**
   - **Problem.** Alternations alone give most of the win: nest-paren 25 ->
     4.7 M instructions. Optionals and loop iterations take it further (3.7,
     and nest-brace 24 -> 16.7). They are also what takes nest-brace's default
     depth from 1022 to 2046.
   - **The catch.** A loop re-enters its choice every iteration. Dispatching a
     loop whose exit can start with almost any byte costs a `switch` per
     iteration for nothing: +11 % instructions on idents. The fix is a
     structural row in the table (admit a loop only when the iterating path
     itself gets cheaper). It is not a tuned number, and it is measured to
     remove the loss everywhere.
   - **Leaning:** one build, two internal stages (alternations first, each
     stage answer-gated).
   - **Open.** Would you rather see stage 2 as its own later build so stage
     1's numbers stand alone on the bench first?
3. **Fold the island's filed "class-member" follow-up into D?**
   - The filed row waited for "a real cell losing to trying alternatives one
     at a time". nest-paren is that cell, and D covers its class-member shape
     in general.
   - **Leaning:** yes. Fold that half into D, and leave the island's
     literal-tail half filed as it is.

## STATE AT HANDOFF

- STATE: complete (design and measurement, as briefed; no build).
- Rulings file `docs/dev/lanes/altd_rulings.md`: empty at every read (start,
  before the WIP commit, before this report). Last entry applied: none.
- OWED none. The full census and the corpus-wide twin run were not run:
  `scripts/boxlock` refused at 11:40 (YIELDING to ready queue jobs 680/681/690
  behind kit job 622). The brief says do not queue and wait, so they are the
  build's STEP 0 / 0b with exact commands (Measurement card), not owed lane
  runs.
- Box use:
  - single-process perf runs and twin builds (no timing window was running;
    load 5.6-9.8 from the kit's heavy job);
  - a 50-pattern census, a 25-pattern bench census, and two harness samples of
    12 and 60 compiles (the second is slightly above the 50-compile sweep cap;
    recorded);
  - nothing after 19:00.
- The vmbc scratch was read. `depth.sh` (vmbc's, adapted) creates subject
  files under `scratch/vmbc/subj/`, inside the temp root.
- Evidence:
  - `docs/dev/lanes/altd_evidence/`: the generator `altd.py`, `census.py`,
    `ident.py`, `mk.sh`, `rate.sh`, `jit.sh`, `depth.sh`, `pdrv.c`,
    `ccwrap.sh`, the raw rate/depth/size/push tables, the bench census, the
    50-sample census, identity results, and the harness summaries and logs;
  - full scratch in `/var/tmp/pcrec-pcrec/scratch/altd/` (twins under `b/`).
- Not done:
  - the large-arm (NF=13M) depth;
  - the one-shot (page-fault) regime;
  - cycles for the rule-all and `ALp` variants (their instruction counts
    decided);
  - the class-index-table emission alternative to `switch`.
