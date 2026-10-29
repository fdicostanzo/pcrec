# Lane l9look: the bench's unusual@0.1 findings (O-112), diagnosed

Lane l9look (opus), 2026-10-29. Diagnosis and measurement only (no build go):
nothing under `src/`, `cli/`, `lib/` or `memfn/` changed. All probes, hand twins
and drivers are throwaway files under `$PCREC_TMPDIR/scratch/l9look/`
(`/var/tmp/pcrec-pcrec/scratch/l9look/`). The bench's checkout was only read.
Worktree HEAD is 020e682c7. The bench pin 614d45eb3 was also built, from a `git
archive` into scratch. Every cost number below is a user-mode instruction or
cycle count from `perf stat` (`instructions:u`, `cycles:u`). Each is taken as the
difference between 11 calls and 1 call in one process, divided by 10, so it is
per call with buffers already resident. No wall-clock claim depends on box load:
the box is shared. Subjects are the bench's own files
(`pcrec-bench/bench/unusual/throughput/*.bin`), and patterns are
`tests/recursion/cscan.rxt` plus the bench's `cscan-onig.rx` /
`wild-json-validate-onig.rx`. Both spellings were compiled with `--features all`,
as the bench's `pcrec-*` testees are.

## Summary

1. **Frames on flat input are TRAIL exhaustion, never resume frames.** Two mechanisms combine:
   - The capture trail is an append-only log, and nothing ever releases an entry
     except a backtrack pop. `RX_CUT` drops frames and does not touch the trail.
   - Each pass of a possessive loop that contains a spliced `(?&sp)` writes 9
     trailed slots: 3 splice saves, PENDING, START/END, then the 3 restores.

   On `idents-1m` the resume stack peaks at **4 frames** while the trail reaches
   **9,096,023 entries (9.1 per byte, 145.5 B/byte)**. That reproduces the bench's
   ~139 B/byte and its 145,536,528-byte `deep_mem`. The retention is not
   deliberate: CUT-INV (atomic_groups_design.md §3.1) forbids the cut from
   *rewinding* the trail, which is right. Nothing ever *compacts* it, though, and
   that is a separate operation that no document considers. **It is a
   correctness-adjacent give-up.** On the same 5 subjects, libpcre2 10.46 answers
   all five at default limits, interp and JIT both, measured here. Those subjects
   are idents-1m, comment-5m, splice-1m, nest-paren-32k and nest-brace-128.
   pcrec's default entry returns `PCREC_ERR_FRAMES` on every one of them.
2. **The general release rule** is that, between two live frames' marks, only the
   OLDEST trail entry per slot is ever read back. A hand twin applies it when the
   trail is full. It compacts each segment between live frame marks down to its
   oldest entry per slot. With that twin, **the default arm answers every flat
   subject** (idents-1m, comment-5m, splice-1m, nest-paren-32k/100k). It was
   answer-identical to the stock artifact on 85 subjects × 4 tiny trail caps
   (159 runs that compacted and answered, 0 differences, `$0` and group 1).
   Nesting still binds early, at about 122 levels of `{`. Each level legitimately
   holds 4 frames and 25 trail entries after compaction (60 before). The extra
   trail per level is the linked call's snapshot of all 19 slots in `W(g)`.
3. **Rates.** Per member, the attribution is:

   | member | pcrec vs pcre2-jit (cycles) | what the cost is |
   |---|---|---|
   | idents-1m | x2.96 | trail writes are ~58 % of cycles; without them x1.24 |
   | nest-paren-32k | x5.4 | 9 failing alternation branches per byte (serial branch try) plus the per-token splice trail |
   | nest-brace-32k | x4.5 | trail 34.5 per byte (call snapshot and restore) plus 10 fails per byte |
   | js-1m, bench's x21.9 | x5.9 in steady state | the bench times ONE call (`iterations: 1`), and that call first-touches 339 MB of fresh frame/trail buffer: 82,908 page faults, ~109 ms of the ~140 ms |

   So yes: **(1)'s mechanism is also most of (2)'s cost**. The trail traffic that
   exhausts the default arm is the single largest per-byte cost on every cscan
   member. On js-1m it is also the storage volume behind the page-fault-dominated
   one-shot number.
4. **Answers to the bench.**
   - (a) `(?(DEFINE)...)` compiles at both 614d45eb3 and HEAD, owned by module
     `recursion` (plus `named-groups` for the names), not by `conditionals`.
     General `(?(n)...)`, `(?(<n>)...)`, `(?(R)...)` and `(?(?=...)...)` are
     refused at both.
   - (b) **No.** `unterminated-5m`'s 145 GB/s is the required-byte-SET dismissal,
     not `RX_REQ_RUN`. The subject starts with `(?{`, so the run check passes.
     The subject contains no `)`, so the `rq_set = { 41 }` memchr rejects it
     before any VM work: 0 pushes, 0.09 instructions/byte.

## Premise test

The premise test was run at worktree HEAD 020e682c7. I compiled
`tests/recursion/cscan.rxt` with `build/pcrec -p rx` and linked it with a scratch
driver (`drv.c`). The driver reads a subject file, calls `rx_search` (the default
arm, tiered entry), and then calls `rx_search_in` with canary-filled buffers to
measure high-water marks. On the bench's flat identifier-only subject
`idents-1m.bin` (1,000,007 bytes, `(?{ ctx_16516 next_66802 ... })`):

| arm | result |
|---|---|
| default `rx_search` | `rc=-3` (`PCREC_ERR_FRAMES`) — **reproduces the bench** |
| `_in`, 2^26-entry buffers | `rc=1`, span 0..1000007; resume high-water **4 frames**, trail high-water **9,096,023 entries**, 145.5 B per subject byte |

The bench's own `cscan-onig.rx` spelling (`(?<n>...){0}` instead of
`(?(DEFINE)...)`) gives byte-identical high-water numbers: 4 frames / 9,096,023
entries on idents-1m, and 4 / 589,941 on nest-paren-32k. Its `deep_mem_bytes` in
the bench's vm-in record (145,536,528 on idents-1m, 9,439,216 on nest-paren-32k,
8,001,928 on comment-5m) matches my canary measure to the byte for the first two.
The third matches to the 500,108-entry trail × 16 B. No difference between
614d45eb3 and HEAD was observed on any probe used here.

## Finding 1 frames on flat input

### What runs out

Default capacities are 2,048 resume frames and 3,072 trail entries
(limits.md §3.2¶1), behind a 37-frame / 56-entry fast tier (§3.2¶3). High-water
marks from the `_in` arm with the stock artifact:

| subject (cscan) | default arm | resume hw | trail hw | trail / byte | bytes/byte |
|---|---|---|---|---|---|
| idents-1m | FRAMES | 4 | 9,096,023 | 9.1 | 145.5 |
| splice-1m | FRAMES | 4 | 3,000,087 | 3.0 | 48.0 |
| comment-5m | FRAMES | 5 | 500,108 | 0.1 | 1.6 |
| nest-paren-32k (cscan: plain bytes) | FRAMES | 4 | 589,941 | 9.0 | 144.0 |
| nest-paren-512 | FRAMES | 4 | 9,333 | 9.0 | 144.4 |
| nest-brace-128 | FRAMES | 516 | 7,797 | — | 544.5 |
| nest-brace-32k | FRAMES | 131,076 | 1,966,197 | — | 559.9 |
| literal-100k | answers | 5 | 136 | 0.001 | 0.02 |

On every flat subject the resume stack stays at 4-5 frames. **Only the trail
grows, and it grows linearly in the subject length.** On nesting, 4 frames and 60
trail entries are spent per level, so the trail (3,072 / 60 ≈ 51 levels) binds
long before the resume stack (2,048 / 4 = 512 levels). That is why the bench saw
a give-up already at nest-brace-128. Its D-2 prediction of "frames from 512" was
reading limits.md §4's specimen, whose trail-per-level ratio is different.

### Why the trail grows: the emitted mechanism

The identifier loop `[A-Za-z_$\x80-\xff] (?: (?&sp) [\w$\x80-\xff] )*+` is a
`frames-unbounded` ATOMIC rung (`--emit-ir` rungs table, label L63). Each pass
runs `RX_CUT(9)` and then `RX_PUSH` to establish one frame for the pass. Then
comes the SPLICED call `(?&sp)`, which is 9 `RX_SET`s:

```
RX_SET(SPLICE_SAVE12, g2.start); RX_SET(SPLICE_SAVE13, g2.end); RX_SET(SPLICE_SAVE14, g2.pending);
RX_SET(G2_PENDING, pos);  <span loop over (\\\n)*+, pushes nothing>
RX_SET(G2_START, pending); RX_SET(G2_END, pos);
RX_SET(G2_START, save12);  RX_SET(G2_END, save13);  RX_SET(G2_PENDING, save14);
```

Every `RX_SET` appends one trail entry (`RX_TRAIL`), because a live frame can
reach the write. The atomic loop's own per-pass frame is that frame, so this is
right for the static rule (engine_m4.md §2.4). But `RX_CUT` is one statement,
`resume_depth = slot`, and **it never touches `trail_depth`**. When the next pass
cuts the previous pass's frame, that pass's 9 entries stay on the trail, and only
the outer frame below the loop can ever unwind them. So the trail is a log of
every write since the last surviving frame, and a possessive loop over n bytes
leaves 9n entries. The counting twin (scratch `tools/cntpatch.py`: a counter
in each macro) gives the same picture per subject byte:

| subject | push | trail | fail | call | ret |
|---|---|---|---|---|---|
| idents-1m | 2.15 | 9.96 | 0.96 | 0 | 0 |
| nest-paren-32k | 11.00 | 9.00 | 9.00 | 0 | 0 |
| splice-1m | 0.33 | 3.00 | 0 | 0 | 0 |
| comment-5m | 0.50 | 1.00 | 0.20 | 0 | 0 |
| nest-brace-32k | 12.00 | 34.50 | 10.00 | 0.5 | 0.5 |
| js-1m (wild-json-onig) | 1.84 | 19.28 | 0.63 | 0.21 | 0.051 |

### Is it intended?

No document intends it. The design of record bounds the *frames* and says the
cut must not *rewind* the trail. atomic_groups_design.md §3.1 (CUT-INV, quoting
`vm_cut`'s comment) says "IT DOES NOT TOUCH THE TRAIL, and must not". That
statement is about correctness: the body's captures must stay undoable by an
outer failure. CUT-INV needs every body entry to stay *above* the surviving
frames' marks. It does not need *every* entry, only the oldest per slot in each
segment. No design, spec or K-row prices the growth: I grepped known_issues,
decisions, plan and docs/design for trail growth, leak or compaction. engine_m4.md
§2.5 promises "overflow is a distinct honest failure", but only where the depth
is truly unbounded. Here the live depth is 4 frames. limits.md §4 describes
nesting, and says nothing about the trail on non-nesting input.

### How PCRE2 bounds it (reference)

PCRE2's interpreter keeps captures INSIDE its heap backtracking frames, which are
copied forward. So there is no separate log: an atomic or possessive close
discards the frames, and with them every capture state they held. Memory is
O(live backtrack points), and a possessive loop over flat input is O(1). The JIT
does the same on its machine stack. Measured here with libpcre2 10.46 (ctypes
driver `tools/p2.py`, DEFAULT match context, no limits raised), on `cscan-onig.rx`:

| subject | interp | jit |
|---|---|---|
| idents-1m | match 0..1000007 | match 0..1000007 |
| comment-5m | match 0..5000011 | match 0..5000011 |
| splice-1m | match 0..1000009 | match 0..1000009 |
| nest-paren-32k | match 0..65547 | match 0..65547 |
| nest-brace-128 | match 0..267 | match 0..267 |

**So this is a correctness-adjacent give-up.** PCRE2 at default configuration
answers every one of these subjects, and pcrec's default entries refuse all of
them with `PCREC_ERR_FRAMES`. The compiler's own call stream (the pattern's real
customer) loses 39-53 % of calls to it. Per the brief, it ranks above (2).

### The general release rule, and a twin that applies it

> **TRAIL-SEG.** Partition the trail at the live frames' `trail_mark`s. An unwind
> to any live frame restores, for each slot, the `saved_value` of the OLDEST entry
> for that slot above the frame's mark. Within one segment, any later entry for a
> slot already present in that segment is therefore never the one that survives
> an unwind. Deleting it, and keeping the segment's order, changes no answer.
> Cut frames are not segment boundaries, so a cut merges their segments into the
> surviving frame's segment. After a merge, the live trail is at most
> `NSLOTS × (live frames + 1)`.

Hand twin (scratch `tools/gcpatch.py`): a 25-line `rx_trail_gc`. When
`RX_TRAIL` finds the trail full, it walks the live frames bottom to top, keeps
the oldest entry per slot in each segment (a `seen[NSLOTS]` byte map per
segment), rewrites each frame's `trail_mark`, and retries. `PCREC_ERR_FRAMES`
is returned only if nothing was freed. It adds nothing to the hot path, because
the code runs only where the stock artifact would already give up.

Results on the DEFAULT arm (`rx_search`, both tiers, stock capacities):

| subject | stock | trail-GC twin |
|---|---|---|
| idents-1m | FRAMES | match 0..1000007 |
| comment-5m | FRAMES | match 0..5000011 |
| splice-1m | FRAMES | match 0..1000009 |
| nest-paren-32k / -100k | FRAMES | match (65547 / 200011) |
| literal-100k | match | match |
| nest-brace-128 / 512 / 2k | FRAMES | **still FRAMES** |

Answer identity (scratch `tools/gccheck.py`): 85 subjects were run through the
twin with trail caps of 20, 40, 64 and 128 entries, which forces compaction
constantly. They were compared with the stock artifact on huge buffers, for `$0`
and group 1. The subjects are all 74 `m`/`n`/`ms` lines of cscan.rxt plus 11
synthesized flat, nested and mixed ones. **0 differences.** 159 runs compacted
and answered; 145 refused because the cap was below the live set. This is a
twin, not a proof. The proof is TRAIL-SEG above. One coupling must be named for
a real build, and it is an invariant the twin relies on: the linked-call return
reads its snapshot *positionally* (`trail[frame[call_top].trail_mark + k]`, the
same reads K36 is about). The snapshot entries are the first entries, and
distinct slots, in their frame's segment, so oldest-first in-order compaction
keeps them at `mark + k`. A build must state this and check it, or replace the
positional read.

Two things the twin also showed:

- **Thrash on the fast tier.** On idents-1m the twin compacted 607,662 times,
  freeing about 15 entries each: the fast tier's 56-entry trail sits just above
  the live set. A real rule needs hysteresis. One option is to compact only if
  compaction frees at least half the capacity, and otherwise escalate or give up
  as today. Another is to compact only on the deep tier.
- **Nesting.** After compaction, nest-brace needs 25 trail entries per level
  against 4 frames per level. The minimum trail that answers is 3,240 entries for
  nest-brace-128, 12,840 for 512 and 51,240 for 2k, so the default 3,072 trail
  answers about 122 levels while the 2,048 frames would allow 512. 19 of those 25
  entries are the linked call's `W(g)` snapshot (subroutines_design.md §5.3a:
  "every slot the emitted region can write"). pcre2-jit's default gives up from
  nest-brace-512 (bench, `-46`), so on nesting pcrec-with-GC would sit at a
  quarter of the JIT's depth. On flat input it would answer everything.

## Finding 3 recursive-member rates

Instruction and cycle counts are per call with resident buffers (11-minus-1 calls).
pcre2-jit was measured with the same method (scratch `p2drv.c`: libpcre2 10.46,
JIT, a 1 GiB JIT stack and heap limit so the deep arm compares like for like).

| member / subject | pcrec instr/call | pcrec cycles | jit instr | jit cycles | cycle ratio | bench ratio |
|---|---|---|---|---|---|---|
| cscan / idents-1m | 188.6 M | 54.6 M | 82.1 M | 18.4 M | x2.96 | x3.0 |
| cscan / nest-paren-32k | 30.7 M | 9.53 M | 10.4 M | 1.77 M | x5.4 | x5.4 |
| cscan / nest-brace-32k | 53.0 M | 18.0 M | 16.5 M | 3.99 M | x4.5 | (100k x4.8) |
| cscan / comment-5m | 220.0 M | 43.0 M | 86.5 M | 18.3 M | x2.35 | x2.4 |
| cscan / splice-1m | 46.8 M | 12.9 M | 23.7 M | 4.69 M | x2.7 | x2.5 |
| wild-json-onig / js-1m | 265.0 M | 95-100 M | 58.6 M | 16.9 M | **x5.9** | **x21.9** |

The cycle ratios reproduce the bench's ratios on every cscan subject, so the
bench's numbers are engine cost, not noise. js-1m is the exception, below.

**Attribution twin: no trail** (scratch `rx_nt.c`, `jonig_nt.c`: `RX_SET`
without `RX_TRAIL`; an upper bound on what trail work costs; not a correct
matcher in general):

| subject | stock cycles | no-trail cycles | trail share | no-trail vs jit | answer |
|---|---|---|---|---|---|
| idents-1m | 54.6 M | 22.8 M | 58 % | x1.24 | identical |
| nest-paren-32k | 9.53 M | 6.50 M | 32 % | x3.7 | identical |
| comment-5m | 43.0 M | 27.3 M | 37 % | x1.49 | identical |
| splice-1m | 12.9 M | 3.71 M | 71 % | x0.79 (faster than JIT) | identical |
| nest-brace-32k | 18.0 M | 8.67 M | (52 %) | — | WRONG (recursion needs the trail), so cost only |
| js-1m | 95.2 M | 30.5 M | 68 % | x1.8 | rc=1 (cost only) |

Mechanism per member:

- **idents-1m (x3.0).** Per identifier byte there is one atomic-loop pass: a cut,
  a push, then the spliced `(?&sp)`'s 9 trailed writes around a span loop that
  consumes nothing on this input. The trail is 58 % of the cycles (perf by
  source line: the `RX_SET` lines of the splice and the fail label lead).
  **Same mechanism as Finding 1.**
- **nest-paren-32k (x5.4, no recursion).** cscan reads each `(` and `)` as a
  plain byte, through the 10-branch token alternation. That alternation is
  emitted as a serial chain (`RX_PUSH` per remaining branch, then try), and a
  `(` or `)` is accepted only by the "everything else" branch. So each byte costs
  **11 pushes and 9 failing branches**, with a trail unwind each (fail label:
  ~28 % of instructions), plus the per-token splice (~40 %). Two mechanisms:
  serial alternation try, and the splice trail.
- **nest-brace (x4.5-4.8).** 0.5 linked calls per byte, each with a 19-slot `W`
  snapshot plus a 19-slot return restore. That gives a trail of 34.5 per byte,
  plus the same 10 fails per byte as nest-paren. Mechanisms: call snapshot width,
  plus serial alternation.
- **js-1m (x21.9).** Three layers:
  1. **The timing method.** The bench's record has `"iterations": 1` for js-1m
     (all cscan subjects have 111). The 1 GiB `_in` buffer is never pre-touched
     ("posix_memalign WITHOUT the memset", driver.c), so the one timed call
     page-faults in the 339 MB it writes. Reproduced: a single call on fresh
     `malloc`ed buffers takes 82,908 page faults, 0.109 s sys and 0.032 s user,
     about 0.14 s, which is 7.1 MB/s against the bench's 7.7. Later calls take
     ~20 ms. So about four fifths of the x21.9 is first-touch of storage that
     scales with the subject.
  2. **The storage volume itself.** The pattern is mostly NOT possessive
     (possessify 2/22), so 1.43 resume frames per byte are legitimately live.
     pcre2-jit's default arm also gives up on js-1m, so this is not a pcrec-only
     refusal. Each live frame carries ~9.5 trail entries even after compaction:
     the trail-GC twin's minimum trail is 13.6 M, against the stock high-water of
     17.6 M. That is ~190 B per live backtrack point.
  3. **Steady-state cycles, x5.9.** The trail is 68 % of that: the linked-call
     snapshots of ~33 slots each, and the splices.
- **cscan short search (x3.6, 296 vs 81 ns).** Not separately profiled. The
  short subjects run the same token loop, so the same per-token splice trail and
  serial alternation apply, plus the per-call `rx_run_state_init` over 83 slots.
  This is inferred, not measured: it would be the first thing to confirm in a
  follow-up.

**Does one general fix cover several?** Yes for the dominant term. The trail
work in the splice and the call snapshot is the largest single cost on idents,
splice, comment and js. It is also part of nest-paren and nest-brace, and it is
the same writes that exhaust the default arm (Finding 1). The second
mechanism, serial alternation try, is separate and independent. It dominates
nest-paren and adds to nest-brace.

## Answers to the bench

- **(a) `(?(DEFINE)...)`.** Supported at **614d45eb3** (built from `git archive`
  into scratch) and at **HEAD 020e682c7**. Both compile `(?(DEFINE)(?<a>x))(?&a)y`,
  the bench's verbatim `cscan.rx` and `wild-json-validate.rx`, and
  tests/recursion/cscan.rxt. The owning module is **`recursion`** (plus
  `named-groups` for the names). With no features it says "(?(...) requires
  module 'recursion'", and the verbatim cscan.rx compiles with the
  `conditionals` module left out. General conditionals are refused at both
  commits with "module 'conditionals' is enabled but (?(...) is not implemented
  yet": `(a)?(?(1)b|c)`, `(?(<n>)b|c)`, `(?(R)a|b)` and `(?(?=a)ab|c)`. So the
  token the bench wants is "DEFINE under recursion", not a conditionals split.
  The `pcrec-*` testees can run the verbatim members as they are.
- **(b) `unterminated-5m`'s 145 GB/s.** **Not** the `RX_REQ_RUN` dismissal. The
  subject begins with `(?{`, so the run check passes. The subject contains **no
  `)` byte at all** (and no `*/`). The search entry's required-byte-SET check
  (`static const unsigned char rq_set[] = { 41 }`, one `memchr` per member,
  `--emit-facts` row `req_set 40,41,63,123`) rejects it before any VM work.
  Counting twin: 0 pushes, 0 trail; 469 k instructions and 188 k cycles for
  5 MB, about 26.6 B/cycle, which is about 143 GB/s at the record's
  5,488 MHz. The mechanism is intended: a subject missing a byte every match
  needs is dismissed by one scan.
- (For the record, not asked.) js-1m's x21.9 is timed over one iteration that
  first-touches 339 MB of untouched caller buffer (Finding 3). Is a one-shot
  timing with first-touch cost the regime the bench means for
  large-subject-throughput? It is a real cost for a caller with a fresh buffer,
  but it is reported beside JIT rows whose stack use is far smaller.

## Candidate fixes

None of these are built (no build go). Each fix is general, not tied to cscan:

| # | fix | what it is | covers | evidence | cost / surface |
|---|---|---|---|---|---|
| A | **trail compaction (TRAIL-SEG)** | when the trail is full, keep the oldest entry per slot per live-frame segment; give up only if too little was freed (hysteresis) | Finding 1 entirely on flat input. Live trail becomes at most `NSLOTS × (frames+1)`, so flat possessive input becomes O(1) | twin: all flat subjects answer on the default arm; 0/85×4 answer differences; zero hot-path instructions | one emitted function per VM artifact: an artifact-size and abi event (D76/D94); limits.md §3.2/§4 hunks (the ceiling becomes "live" state); the positional call-snapshot read must be stated and checked (K36 neighbour) |
| B | **frameless-region write coalescing** (compile time) | inside a region that pushes no frame, (i) a slot needs at most one trail entry, and (ii) a write overwritten before any read is dead. The spliced call to a frameless callee whose captures are reverted on return (PCRE2 semantics) then emits only its span loop | the dominant rate term on idents, splice and comment (the trail is 37-71 % of cycles there; upper bound by the no-trail twin), and most of Finding 1's growth before A ever runs | no-trail twin (an upper bound); the exact saving of B alone is NOT measured | a dataflow fact in emit_vm; neighbour and likely general form of [ART-TRAIL-ELIDE] |
| C | **call snapshot narrowed by liveness** | snapshot and restore only `W(g) ∩ live-in-caller-after-return`, not all of `W(g)` | nesting depth (25 → fewer entries per level; it is what binds nest-brace at ~122 levels) and the js-1m and nest-brace call cost | count: 19 (cscan) / ~33 (json) slots per call and per return | a liveness analysis over the emitted regions; subroutines_design.md §5.3a's `W` rule gains a refinement |
| D | **first-set alternation dispatch** | dispatch on the next byte to the first branch whose first set admits it, and push only the later branches that also admit it | nest-paren x5.4 (9 fails per byte), nest-brace, and the per-token cost on every cscan member | counting twin: 11 pushes and 9 fails per byte on nest-paren; after the no-trail twin, nest-paren is still x3.7 | [ENG-ISL-S2]'s CLASS-MEMBER shape (its trigger, "a real cell losing to serial alternation-try cost", now has a witness) |
| E | larger default capacities for recursive patterns | (the bench's ask) | nothing that A to C do not cover | — | NOT recommended: limits.md §5 ties the deep struct to the stack (K33). A raises flat input to "answers" without a byte more of stack |

Ranking: **A first**, because it removes a refusal of an answer PCRE2 gives.
**B next**, for the largest rate term; it also shrinks what A must ever compact.
C and D are independent rate rows. The js-1m page-fault term moves with storage
volume: B and C shrink it, A does not, because its frames are live.

## Existing rows

- **[ART-TRAIL-ELIDE]** (not-started): "untrailed RX_SET where every read is
  dominated by a write in the same attempt". It already records "the trail FRAMES
  give-up goes" and a limits.md §3.2/§5 hunk. Candidate B is its frameless-region
  generalization, and this report is a measured witness (idents x2.96 → x1.24
  upper bound).
- **[ENG-ISL-S2]** (not-started; trigger "a real cell losing to serial
  alternation-try cost"): nest-paren-32k is such a cell (9 fails per byte, x5.4).
  Candidate D.
- **[SITE-FRAMELESS]**: not this mechanism. That row is about callout and code
  sites costing framelessness; cscan has 0 callout sites and 0 islands.
- **[ENG-DIRECT]** and **[ENG-TACTICS]**: not this mechanism. They are about
  direct-coded automata and search tactics. cscan is `\G`-anchored, so there is
  no search, and its engine is the VM, forced by the linked call.
- **[POSS-CALL-COPY]**: neighbouring (possessify across calls). js-1m's 2/22
  possessified is why its frames are live, but whether more of it is
  possessifiable was not studied here.
- **K36** (known_issues): the call-return restore reads the trail positionally,
  which is the invariant candidate A must preserve. A build of A is a natural
  owner for K36's hoist.
- **limits.md §4 / §3.2**: the worked example gives 2 resume frames and 9 trail
  entries per level for `^(a(?1)?b)$`. Nothing states the trail cost of
  NON-nesting input. If A is not built, that missing sentence is a spec gap.
- **subroutines_design.md §5.3a** (`W` = every slot the region can write): the
  rule candidate C refines.
- No existing K-row or plan row covers trail growth under cuts. I grepped
  known_issues, decisions, plan and docs/design.

## Questions for Frank

1. **Should flat input stop giving up?** Today a long run of identifiers, and
   nothing else, makes the scanner pattern refuse on the default entry, while
   PCRE2 at its default settings answers it. The cause is bookkeeping we keep and
   never read back. The fix I lean to is "compact the bookkeeping when it fills"
   (candidate A). It costs nothing until the moment we would otherwise give up.
   It adds one small function to every backtracking artifact, and therefore an
   abi event. The alternative is to only document the limit, in limits.md, and
   point heavy callers at the `_in` entries. That keeps us refusing answers PCRE2
   gives, which is the kind of gap we usually close. My leaning is to build A
   first, with the hysteresis rule, and to keep the depth limit for real nesting
   as it is. Do you want A as a build row now, or held until B lands, since B
   alone may make flat input fit for this pattern?
2. **Speed first, or storage first?** The single biggest per-byte cost on these
   members is the same bookkeeping (B removes most of it at compile time).
   Separately, a 10-way choice tried one branch at a time costs nesting-heavy
   input 9 failed tries per byte (D). My leaning is B before D, because B helps
   every member and the storage problem, while D helps the paren- and
   brace-heavy ones. I'm open on that order if the bench's call-stream customer
   matters more than the throughput rows.
3. **The json x21.9.** Most of it is the first and only timed call touching
   339 MB of fresh memory. Should we ask the bench whether a one-shot timing is
   the intended regime for that row? It is a real cost, but it reads as a much
   larger engine gap than the x5.9 we measure in steady state. My leaning is to
   ask, not to object: the fix on our side (smaller per-frame storage, B and C)
   is the same either way.

## STATE AT HANDOFF

- STATE: complete (diagnosis and measurement only, as briefed; no build).
- Rulings file `docs/dev/lanes/l9look_rulings.md`: empty at every read (start,
  before commit, before this report). Last entry applied: none.
- Owed runs: none. Box load used: single-process probes only, all before 09:30
  on 2026-10-29, none during a timing job (`scripts/boxqueue status` showed the
  box free).
- Scratch evidence (not committed; reproducible from the descriptions above):
  `/var/tmp/pcrec-pcrec/scratch/l9look/`. The drivers are `drv.c` (pcrec) and
  `p2drv.c` and `tools/p2.py` (libpcre2). The twins are `tools/gcpatch.py`
  (trail compaction), `tools/cntpatch.py` (event counts) and the `*_nt.c` files
  (no trail). The checks and counters are `tools/gccheck.py` (answer identity),
  `icount.sh` and `icount2.sh` (11-minus-1 call counts), and `old/` holds the
  614d45eb3 build.
- Not done: the cscan short-search x3.6 was not profiled separately (inferred
  above). Candidate B's isolated saving is not measured; the no-trail twin is
  its upper bound. Whether js-1m's pattern could be possessified further was not
  studied.
