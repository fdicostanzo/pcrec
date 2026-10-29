# Lane vmbc: design of candidates B (dead slot writes) and C (call restore narrowed by liveness)

Lane vmbc (opus), 2026-10-29. This lane did design and measurement only (no build go).
Nothing under `src/`, `cli/`, `lib/` or `memfn/` changed. The base is lane/trailgc
(D183, trail compaction at checkpoints), read only. The worktree is at main
8fcc15669. Every twin was built from lane/trailgc's emitted C
(`worktrees/trailgc/build/pcrec`, head 801ad1214) and lives in scratch
`/var/tmp/pcrec-pcrec/scratch/vmbc/`. The twin generator, the checkers and the raw
numbers are copied to `docs/dev/lanes/vmbc_evidence/` for the build lane. The
bench checkout was only read.

## Summary

- **One analysis covers both candidates.** The VM's trail makes backtracking
  behave like ordinary control flow: on a resume, every slot holds the value it
  had at the matching push. So the emitted program can be treated as a flow
  graph. Each push gets an edge to its resume label, and each region exit gets
  an edge to its callers' return labels. On that graph, classic slot liveness
  plus available copies do the following:
  - **B (dead writes).** A slot write that nothing reads before the next write
    is deleted, together with its trail entry. A write of a value the slot
    already holds is also deleted. A spliced call whose captures are restored
    before anything reads them (the `(?&sp)` in cscan, nine trailed writes per
    byte on idents) collapses to its span loop.
  - **C (call restore narrowed).** The linked call's restore moves from the
    shared region exit to each call site's return label. Each site then
    restores only `W(g) ∩ live-after-return`. The snapshot keeps only those
    entries, renumbered by rank, so K36's positional read survives.
- **Measured on hand twins** (instructions per call, warm, (11-1)/10, `_in`
  NF=4M NT=64M; cycles are the minimum of 5 at box load 3.2-3.5):

  | subject | stock (D183) | B | C | **B+C** | pcre2-jit | cycles stock -> B+C vs jit |
  |---|---|---|---|---|---|---|
  | idents-1m | 191.67 M | 90.02 | 191.53 | **91.73** | 82.09 | x3.00 -> **x1.21** |
  | nest-brace-100k | 162.72 | 124.62 | 138.52 | **91.02** | 50.40 | x5.33 -> **x1.89** |
  | splice-1m | 47.76 | 19.76 | 47.42 | **20.42** | 23.66 | x2.79 -> **x0.80** |
  | js-1m | 260.71 | 204.50 | 163.93 | **72.63** | 58.58 | x5.73 -> **x1.40** |
  | nest-paren-32k | 31.07 | 25.04 | 31.00 | 25.04 | 10.35 | x5.70 -> x3.56 (D's residual) |
  | comment-5m | 220.97 | 133.47 | 222.97 | 133.47 | 86.50 | x2.45 -> x1.52 |

  - **Trail entries per subject byte**, stock -> B+C: idents 9.95 -> 0.09,
    nest-brace 34.5 -> 1.5, splice 3.0 -> 0, js 19.3 -> 0.49, nest-paren 9.0 -> 0.
  - **Default-arm depth.** nest-brace goes 85 -> **511** levels (pcre2-jit 176);
    JSON arrays go 19 -> **291** (jit 150). Both now bind on resume frames
    (2048 of 2048), not on the trail.
  - **The specimen `^(a(?1)?b)$`.** Its trail becomes a constant 5 entries
    (from `4n + 17`), and its default reach goes 763 -> 1024.
  - **js-1m one-shot.** First-touch storage goes 339 -> 64 B/byte. Page faults
    go 82,907 -> 15,666 and the one call takes 142 -> 29 ms task-clock. This is
    the bench's x21.9 regime.
- **Answers.** Twins are answer-identical to stock on 99 cscan and 161 JSON
  subjects, every capture, at 7 capacities each (5,460 cells; 0 differences).
  At small trail caps the twin answers wherever stock answers, and it also
  answers 498 / 484 cells where stock gives up. A harness sample of 50 corpus
  patterns from tests/recursion, run with the twin rewriting every generated
  matcher, gave 345/0 under default flags and 345/0 under
  `-fno-splice-calls --engine=vm`.
- **One build, in two stages** (see Questions). The rule-(iii) idea, skipping a
  trail entry when the slot was already trailed since the last push, is
  measured at **zero** extra on top of B+C (identical instructions and depth).
  I recommend not building it.
- **Not run: the full corpus census and corpus-wide twin run.** The box lock
  refused at 10:55 (queue jobs ready), so this is the build's STEP 0, with its
  command in Measurement cards.

Goals (who benefits, measurable form, in priority order):

1. **No answer moves.** Every corpus cell is identical, captures included,
   under the twin and then the build.
2. **The recursive and scanner members' rate.** Bench callers of cscan / JSON
   / sexp-like patterns get cycles per call within x2 of pcre2-jit on idents,
   splice, nest-brace and js (B+C twin: x1.21 / x0.80 / x1.89 / x1.40).
3. **Default-arm depth at or above pcre2-jit's** on nest-brace and JSON
   (511 vs 176, 291 vs 150).
4. **Less working storage** for one-shot callers (js-1m 5.3x less).

Non-goals: fewer resume frames (that is D); changing default capacities.

## Premise test

**Holds.** lane/trailgc's `trailgc2_report.md` exists (head 801ad1214), and its
"Remaining gap to pcre2-jit" table gives trail shares of 56 / 38 / 63 / 73 /
35 / 64 % on idents / nest-paren / nest-brace / splice / comment / js. That is
35-73 %. Its call-entry shares are 55 % (nest-brace) and 65 % (js), and the
depths are 85 / 19 (pcrec default) against 176 / 150 (jit).

My stock numbers reproduce trailgc2's instruction counts exactly: idents 191.67 M,
splice 47.76 M, nest-paren 31.07 M. The pcre2-jit cycle numbers are lower than
trailgc2's because the box was quieter (load 3.5 vs 16-27): idents 18.3 M vs
23.7 M.

## B design

### What B is, as one general statement

> **SLOT-FLOW.** Take the VM program as a flow graph. Its edges are
> fall-through and gotos, plus `PUSH(L) -> L` (the resume) and
> `region exit -> every return label of that region`. Then:
>
> - **DEAD.** A slot write whose slot is not live after it is deleted, together
>   with its trail entry.
> - **COPY.** A write `s := slot[t]` where `s == t` provably holds on every path
>   is deleted.
>
> Repeat both to a fixpoint.

It is not tied to frameless regions or to splices. Those are where it fires
most, because a splice parks, writes and restores the same capture slots inside
one pass.

### The lemma that makes it sound: TRAIL-EQ

**At a resume of frame F, every slot holds the value it had when F was pushed.**

- **Stock VM.** This holds by construction. Every write is trailed (P7: the old
  value is saved unconditionally), and the unwind restores each slot from its
  oldest entry above F's mark.
- **Under B.** It still holds, because a deleted write never changed its slot
  and took its entry with it.
- **Under C.** It still holds, because not restoring is not a write.
- **Under D183's compaction.** It still holds, because compaction keeps the
  oldest entry per slot per segment.
- **CUT.** A cut only removes frames, which are never resumed.

So the resume is a control-flow edge that carries the push-time state. On that
graph, the usual invariant goes through by induction over the run: at every
point, every slot live there holds the same value in the stock run and the
transformed run, and both runs take the same path.

- **A deleted write** targets a dead slot.
- **A push.** It reads `live-in(L)` (see the table), so those slots agreed at
  the push. They agree again at the resume, by TRAIL-EQ in both runs.
- **A failing unwind.** It is not a read. It only re-establishes push-time
  values.

### The declared rule table (first match per emitted statement)

| row | statement (emitter primitive) | reads | writes | copies (must) | notes |
|---|---|---|---|---|---|
| 1 | snapshot self-write after `RX_CALL` (`vm_call`) | **none** (see C) | storage only | unchanged | B never deletes it alone; C decides it with its restore |
| 2 | return-label restore (C's moved restore) | trail only | `s` | kills `s`; label starts with no facts | kept per site by C |
| 3 | `SET(s, e)` (`vm_set`) | slots named in `e` | `s` | kill facts on `s`; add `s == t` if `e` is `slot[t]` | the general write |
| 4 | `PUSH(L)` / `RX_CALL` frame | `live-in(L)` (resume) | — | `L` inherits the facts at the push | TRAIL-EQ |
| 5 | `CUT(m)` | `m` | — | unchanged | CUT-INV: the cut only merges segments |
| 6 | backreference, `CHARGE_WORK`, prune, revdet and lookaround compares, any `slot_values[x]` read | the slots named | — | unchanged | via `vm_slot_ref` |
| 7 | callout / code site ([INLINE-C]) | every capture slot, and every slot it publishes | its publish writes | kill all | conservative. The twin refused these artifacts (direct `slot_values[0] =` publish) |
| 8 | region exit `goto *call_ret` | live-in of every return label of this region | — | none at return labels | |
| 9 | accept | capture slots `0 .. 2*NCAPS-1` (slot 0 carries `\K`) | — | — | |
| 10 | fail / give-up `return` | nothing | — | — | the unwind is row 4's edge |
| 11 | anything unrecognised | **every slot** | **every slot** | kill all | refuse-to-optimise default |

Liveness is the least fixpoint. Copies is a must-analysis with "no facts" at
the function entry and at every return label.

### What the trap cases do under the table

- **Captures.** Accept reads the capture slots, so a capture write survives
  unless something overwrites it before accept. A splice's restore is such an
  overwrite, and the spliced body's capture writes die. That is PCRE2's
  capture-transparent call semantics, already emitted by the stock code.
  Groups that are only called (`{0}` / DEFINE) end UNSET, so all their writes
  die.
- **Backreferences.** Row 6 reads `(2g, 2g+1)`, so a group referenced later
  keeps its writes. `captures.rxt`'s `^(a)(b\1)(?2)$` passed under the twin.
- **Publish-at-close `PENDING` and the cut marks.** These are §5.3b's two
  refutations of a capture-only W: a lost match, and six false matches. Both
  are reads after a return, so both stay live. The cscan twin keeps exactly
  `CUT_MARK0` at the recursive site, because the items loop's next cut reads
  it. The specimen keeps `G1_PENDING` at the outer site. `slotfamilies.rxt`
  passed.
- **Recursion and backtracking into a returned call.** These follow from
  TRAIL-EQ plus the push edge. A retreat into a callee frame resumes with that
  frame's values. The second return re-runs the site's restores from the
  intact snapshot. `atomicity.rxt` and `bothlinkage.rxt` passed.
- **CUT-INV.** B never reorders a mark write against a push. A mark is read by
  its CUT and stays live while its loop runs, and B never rewinds the trail.
- **R25 E5** (`(?:a|bc){3}+`, the counter turned into an untrailed local).
  That miscompile came from making a write UNTRAILED. B never does that: it
  deletes write and entry together, and only when the slot is dead, and the
  push edge makes a counter read after a resume a live use.
- **`\K`.** Slot 0 stays outside every W (§3.4(b), measured). Its write is a
  capture write read at accept. `kreset.rxt` passed.

### Rule (iii), untrailed writes: measured, not recommended

The l9look idea was "inside a region with no push, a slot needs at most one
trail entry" (the static form of TRAIL-SEG). The twin implements it as a
must-analysis: a push starts a segment, a resume continues the pushing
segment, and a cut only merges. The write becomes an untrailed `RX_SETU`.

- It is sound for the same reason D183's compaction is.
- On top of DEAD+COPY it changed nothing measurable. B+C with (iii) and B+C
  without it give **identical instructions** on all six subjects, and the same
  depths (511 / 291).
- Alone it is weak: idents goes 191.7 -> 162.4 M with (iii) alone, against
  88.6 M with DEAD+COPY alone.

Building it would add a second write primitive, a second analysis, and a new
spelling the D183 checker must learn. So D77 and the simplification lens both
say no. Revisit it if the census finds cost-bearing re-trailed writes that
survive B+C.

## C design

### The rule

Today, `vm_region` restores all of `W(g)` (§5.3a: every slot the region can
write, minus 0/1) at the shared exit. It reads `trail[frame[call_top].mark + j]`
and then jumps through `call_ret`.

C changes the linkage as follows:

1. **The restore moves to each call site's return label.** The exit records the
   frame index in a matcher-local `<p>_ret_frame` before the `goto *`. The
   return label reads `trail[frame[<p>_ret_frame].mark + rank]`.
2. **Site `c` restores only `K_c = W(g) ∩ LIVE-AFTER(R_c)`.** Its snapshot parks
   only `K_c`, in the same order, so a slot's offset is its rank in `K_c`. If
   `K_c` is empty, the site writes no snapshot. The call frame itself stays,
   because it carries `call_ret` and makes the call backtrackable (§3.2).
3. **`LIVE-AFTER` is computed in the stock-restore model.** In that model,
   every return label kills all of `W(g)`. The snapshot is not a read.
   Instead, the call statement reads `LIVE-AFTER(R_c) ∩ W(g)`, because the
   parked value travels around the callee on the trail.

### Why the model is sound (and the two traps the prototype hit)

**Claim.** Let P(K) be the program with the per-site sets K. Then no read in
P(K) sees a value the stock program would not.

**Proof sketch.** Take a read of `s` reached from a return `R_c` with `s` not
in `K_c`, along a path with no write of `s`.

- **Case 1: no other return on the path would have restored `s` in the model.**
  Then `s` is live after `R_c` in the model, so `s` is in `K_c`.
  Contradiction.
- **Case 2: some return on the path would have.** Take the last one, `R_d`. In
  P(K) it did not restore `s` (otherwise the path would have a write). The
  suffix after `R_d` makes `s` live after `R_d` in the model, so `s` is in
  `K_d`. Contradiction.
- **Snapshot reads.** The snapshot reads in P(K) are covered, because the call
  reads `LIVE-AFTER(R_c) ∩ W` in the model.
- **Backtracking into a returned callee.** This is TRAIL-EQ again. The
  snapshot is below every callee frame, so it is intact for the second return.

**Trap 1: computing liveness on the program with its own snapshots as reads.**
The next nested call's snapshot reads every W slot, so every site keeps
everything; this is a greatest fixpoint that props itself up. The cscan
recursive site kept all 19.

**Trap 2: growing the keep sets from empty.** This is not monotone, because a
kept restore is also a kill. The JSON inner sites overshot to keeping every
capture, because no outer restore killed them yet.

The stock-restore model has neither problem. It is one ordinary liveness pass,
and `K_c` is read off it. A build must use it, and a sabotage row should plant
trap 2's iteration (it over-keeps; it is not unsound) only as a REACH witness,
not a soundness one.

### What it keeps on the members

- **cscan (19-slot W).** The outer site keeps 4 (groups 2/3 start/end, which
  accept reads). The recursive site keeps **1** (`CUT_MARK0`).
- **JSON.** The main site keeps 16 (every capture, reset to unset for accept;
  once per match). **All 7 inner sites keep 0.**
- **The specimen.** Outer 1 (`G1_PENDING`), inner 0.

C also **fixes K36 by construction.** The positional reads now run at the
return label, after the exit's `call_frame >= resume_cap` guard, not three
lines before it.

### Expected default-depth gain from C

| arm | stock (D183) | C alone | B alone | **B+C** | pcre2-jit |
|---|---|---|---|---|---|
| default, nest-brace levels | 85 | 205 | 125 | **511** (frames: 2048 of 2048) | 176 |
| default, JSON `[[..1..]]` | 19 | 49 | 21 | **291** (frames: 2043 of 2048) | 150 |
| large (NF=13,421,772, NT=33,554,432), nest-brace | 1,062,545 | — | — | **3,355,442** (= NF/4) | 909,088 |
| large, JSON | 220,857 | — | — | **1,917,395** | 666,665 |
| `^(a(?1)?b)$` default n | 763 | — | — | **1024** (= 2048/2) | — |

After B+C the trail at the deepest default answer is 1,545 of 3,072 (nest-brace)
and 909 (JSON). Resume frames now set the depth: 4 per level on nest-brace, 7 on
JSON, 2 on the specimen. More depth from here is D's business (fewer pushes per
level), not the trail's.

## Interaction with D183 compaction

B+C build on D183 and leave it in place. Specifically:

1. **What D183 still does.** Compaction is TRAIL-SEG at run time, for writes
   that are live but repeat across cut-merged segments: a capture inside a
   possessive loop is trailed once per pass, and only a cut merges those
   segments. B+C cannot remove those, because the writes are live. Compaction
   still answers them. B+C only shrink what it has to walk.
2. **The checkpoint placement rule should count surviving writes.**
   `vm_jump_closes_trail_cycle` asks whether a SET was written since the label.
   After B, many loops write nothing; on idents the whole splice died.
   Measured with the greedy pruner (`prunechk.py`, which uses trail_checkpoints.py
   as its oracle): it drops 4 of 8 cscan checkpoints and 5 of 10 JSON ones.
   That takes idents 91.73 -> 86.21 M and splice 20.42 -> 18.42 M. This is
   D183's own +1.6-2.1 % coming back, at the same depths (511 / 291) and
   answer-identical.
3. **The margin shrinks.** The floor function's emitted `margin` (D183's M = SET
   sites) becomes the count of surviving sites. That is an emitted-constant
   move, inside the same abi event.
4. **K36 under compaction.** The positional read keeps D183's invariant: the
   kept snapshot entries are the first entries of the call frame's segment,
   distinct slots, in rank order. Compaction keeps them and moves the mark.
   The exit's checkpoint runs before the `goto *`, so the return label reads
   the moved mark.
5. **The return checkpoint still covers chains of returns.** The restores now
   run after the exit's checkpoint, at the return label. Every cycle through a
   return still passes that checkpoint, and each restore site runs at most
   once between two checkpoints. trail_checkpoints.py passes on all three B+C
   twins (cscan heaviest path 9 / margin 255, JSON 22 / 520, specimen 3 / 15).
6. **D183's "revisit when" fires, and the answer is no change.** It reads "or
   candidate B ... lands and changes what the trail holds". B changes how much
   the trail holds, not how compaction works.
7. **limits.md §4's worked example moves again.** `4n + 17` becomes constant,
   and the reach becomes 1024, frames-bound. match_api §10.6's 64 MB table and
   its `min(nframes / 2, (ntrail - 17) / 4)` become `nframes / 2`. These are
   the same spec readers trailgc2 re-pinned (limits §4¶1-3, §5¶6, match_api
   §10.1¶1, §10.6¶2-3, tuning §2.11¶2, guide tuning-and-limits). Land B+C after
   lane/trailgc merges, and re-pin them once.

## Population

| set | patterns | VM artifacts with a slot write | movers under B+C | of which narrowed calls | note |
|---|---|---|---|---|---|
| bench `unusual/` (all 25 `.rx`) | 25 | 20 | **5**: cscan, cscan-onig, wild-json-validate(-onig), wild-sexp-balanced | 5 | 4 `co-*-twin` artifacts have 2 live capture writes (no move). The 11 callout artifacts were refused by the twin (direct publish write, table row 7); a build analyses them conservatively |
| corpus sample, default flags (tests/recursion: cscan, nocaptures, rebind, slotfamilies, whole, bothlinkage, atomicity, captures, kreset) | 50 | 47 | **47** | 27 of 27 with linked calls | every artifact has a spliced call or a capture write that a later restore overwrites |
| same 50, `-fno-splice-calls --engine=vm` | 50 | 50 | **50** | 50 | |
| upper bound ([ART-TRAIL-ELIDE] filing) | — | 66 bench / 1,454 corpus with `RX_SET` | not counted | — | |

Population is counted by `census.py` and the harness wrapper's per-artifact log
(`vmbc_evidence/*.vmopt.log`). The full bench (400 `.rx`) and the full corpus are
not counted (the box lock refused). That count is the build's STEP 0 (card
below).

Expected movers are every VM artifact with a spliced or linked call and every
capture write overwritten before accept. Every such artifact's emitted bytes
move, so this is an abi event with an identity-gate re-pin and a mover census
(trailgc2's `movers.py` shape).

**Remodel overlap.**

- **[SITE-FRAMELESS]: adjacent, not overlapping.** It decides framelessness per
  path for callout and code sites, while B+C never add or remove pushes. B+C's
  row 7 treats a code site as reading every capture. If [SITE-FRAMELESS]
  later goes per-path, row 7 can narrow the same way. **[INLINE-C] is open and
  defines what a code site may read and publish.** Since builds are one at a
  time until [INLINE-C] closes, B+C land after it and write row 7 once,
  against its final contract.
- **[ENG-DIRECT]: none.** It re-codes frames-1 artifacts as direct automata,
  and B+C change no frame count.
- **[DD-11.5]: none.** It covers anchor and span-context facts, not slots.
- **[ART-TRAIL-ELIDE]: subsumed.** Its "untrailed SET where every read is
  dominated by a write in the same attempt" is B's DEAD rule. B deletes the
  write; it does not untrail it. Fold the row into the B+C row.
- **[POSS-CALL-COPY]: neighbour, no conflict.** It concerns possessify
  verdicts; B+C read whatever was emitted.

## Twins and measurements

**Method.** l9look and trailgc2's method:

- `perf stat -e instructions:u` (and `cycles:u`, minimum of 5), per call as
  (11 calls - 1 call) / 10, through drv.c's `r` mode (`_in`, NF=4,194,304,
  NT=67,108,864).
- gcc -O2. The box was shared: kit job 622 held the lock, and loadavg was
  3.2-3.5 during the cycle runs.
- pcre2-jit is `gap/p2 ... jg`: libpcre2 10.46, 1 GiB JIT stack and heap limit.

**The twins.** They are generated mechanically, not hand-edited, by
`vmopt.py`, a scratch prototype of the analysis. It reads the emitted matcher,
builds the line flow graph (push and return edges included), applies the rules,
and rewrites the text. Modes:

| mode | rules |
|---|---|
| `B` | DEAD + COPY + (iii); the linkage pinned |
| `Bd` | DEAD + COPY |
| `Bt` | (iii) only |
| `C` | the linkage move and narrowing only |
| `BC` | everything |
| `BCd` | the recommendation: B+C without (iii) |
| `BCdP` | BCd plus D183 checkpoints pruned where no surviving write closes the cycle |

Anything it does not recognise makes it refuse the artifact.

| subject | stock | Bd | Bt | B | C | **BCd** | BCdP | jit |
|---|---|---|---|---|---|---|---|---|
| idents-1m instr | 191.67 | 88.63 | 162.39 | 90.02 | 191.53 | **91.73** | 86.21 | 82.09 |
| nest-brace-100k | 162.72 | 126.02 | 150.32 | 124.62 | 138.52 | **91.02** | 90.92 | 50.40 |
| splice-1m | 47.76 | 19.42 | 39.76 | 19.76 | 47.42 | **20.42** | 18.42 | 23.66 |
| js-1m (warm) | 260.71 | 209.09 | 248.91 | 204.50 | 163.93 | **72.63** | 72.30 | 58.58 |
| nest-paren-32k | 31.07 | 24.97 | 29.30 | 25.04 | 31.00 | **25.04** | 25.17 | 10.35 |
| comment-5m | 220.97 | 134.47 | 192.97 | 133.47 | 222.97 | **133.47** | 134.47 | 86.50 |

Cycles, minimum of 5:

| subject | stock | B | C | BCd | jit |
|---|---|---|---|---|---|
| idents | 54.99 | 21.28 | 46.38 | 22.11 | 18.30 |
| nest-brace | 67.58 | 38.44 | 40.44 | 24.00 | 12.67 |
| splice | 12.87 | 3.37 | 12.95 | 3.71 | 4.62 |
| js | 96.69 | 73.69 | 51.47 | 23.65 | 16.86 |
| nest-paren | 10.09 | 6.76 | 9.15 | 6.31 | 1.77 |
| comment | 43.91 | 26.87 | 44.41 | 27.28 | 17.89 |

C alone on idents shows fewer cycles with unchanged instructions. That is layout
or noise: one earlier B run read 33.6 M and its rerun 21.3 M. Read the
instruction column for decisions.

**B and C compound.** On js-1m, B alone is -22 % and C alone -37 %, but B+C is
-72 %. On nest-brace it is -23 %, -15 % and -44 %. The reason is that B deletes
the callee-internal reads (a group close reading its PENDING, the dead capture
closes) that would otherwise keep slots live after a return. That empties C's
keep sets: the JSON inner sites keep 0 only with B. This is the main argument
for one build.

**Storage and one-shot.** High-water, canary measure (`drv i`), bytes per
subject byte:

| subject | stock | B+C |
|---|---|---|
| js-1m | 339.1 | 63.9 |
| idents-1m | 145.5 | 1.5 |
| nest-brace-100k | 560.0 | 104.0 |

js-1m one call on fresh `malloc` buffers (the bench's `iterations: 1` regime):

| | stock | B+C |
|---|---|---|
| page faults | 82,907 | 15,666 |
| task-clock | 142.2 ms | 29.1 ms |

**Answer identity.**

- `ident.py` compares stock with each twin. For each subject it runs the
  default arm and the `_in` arm at NF=200,000 with trail caps 8, 16, 32, 64,
  256 and 4,000,000, and prints rc plus every capture span.
- The subjects are:
  - cscan: lane/trailgc's `cscan.rxt` lines (75 of 99 match), synthesized
    flat, nested and unbalanced ones, and 200 KB prefixes of the bench
    subjects;
  - JSON: 150 seeded random valid and corrupted JSON texts, deep arrays, and
    `js-near-1m`.
- Result:
  - B, C and BC: 2,079 cscan cells and 3,381 JSON cells;
  - BCd and BCdP: 1,386 and 2,254 cells;
  - all with **0 differences**;
  - twins answer 331-498 cells where stock gives up at a small cap, and never
    give up where stock answered.
- The harness sample ran `tests/harness/run.sh` on the 9 recursion files,
  with `CC=ccwrap.sh` (runs `vmopt.py -m BC` on every generated matcher before
  gcc) and `PCREC` = lane/trailgc's binary. Results: 345 passed / 0 failed
  (47 artifacts rewritten); with `RXTFLAGS="-fno-splice-calls --engine=vm"`,
  345 / 0 (50 rewritten). BC is a superset of the recommended BCd's rewrites,
  since it also untrails.

The specimen: `mint` gives a minimal trail of 5 at n = 10, 50, 100 and 200 (stock
57 / 217 / 417 / 817 = `4n + 17`). Its answers are identical to stock for
n in {1, 2, 3, 7, 30, 200} x {exact, +a, +b, +x}.

## Measurement cards

All under `/var/tmp/pcrec-pcrec/scratch/vmbc/` (copies in
`docs/dev/lanes/vmbc_evidence/`). The stock C is lane/trailgc's emitted
`scratch/trailgc2/gap/{cscan,json}/rx.c`.

| card | command | reads | result file |
|---|---|---|---|
| twin build | `mk.sh {cscan\|json} {stock\|B\|Bd\|Bt\|C\|BC\|BCd}`; `mkc.sh b/K_M` | `b/K_M/{drv,cdrv}`, `vmopt.log` | — |
| rates | `rate.sh` (`MODES=`, `SUBJ=`, `NOCYC=1`) | instructions per call, minimum-of-5 cycles | `rate1.txt`, `rate_bcd.txt`; jit in `jit1.txt` |
| trail per byte | counting twins `b/K_M_cnt/drv SUBJ r` (`REPS=1`) | trail writes / subject length | `trail_per_byte.txt` |
| default depth | `depth.sh K M pd 100000` | largest nesting that answers | in this report |
| large depth | `NF=13421772 NT=33554432 depth.sh K BC pl 8000000` | same | `depth_large.txt` |
| specimen | `b/spec_M/mint 10 50 100 200`; default bisect | min trail per n; default n | in this report |
| one-shot storage | `perf stat -e page-faults,task-clock`, `REPS=1`, json drv | first touch | in this report |
| answer identity | `MODES="BCd BCdP" python3 -I tools/ident.py {cscan\|json}` | 0 differences | in this report |
| harness sample | `CC=ccwrap.sh VMOPT_MODE=BC PCREC=... tests/harness/run.sh FILES` (`RXTFLAGS=` axis) | passed / failed | `harness_*.summary` |
| checkpoint prune | `tools/prunechk.py IN OUT` | droppable D183 checkpoints | in this report |
| **build STEP 0 (not run)** | `scripts/boxlock run --label vmbc-census -- python3 -I tools/census.py worktrees/trailgc/build/pcrec BCd --corpus worktrees/trailgc` and `... --rx pcrec-bench/bench/*/patterns/*.rx` | movers, dead writes, narrowed calls, refusals | — |
| **build STEP 0b (not run)** | `scripts/boxlock run --label vmbc-twin -- env CC=ccwrap.sh VMOPT_MODE=BCd PCREC=... make test-corpus` (or `run.sh` over every `.rxt`), plus `RXTFLAGS="-fno-splice-calls --engine=vm"` | corpus answer identity of the twin before a line of `src/` | — |

Not a find/scan/skip/verify method, so the measurement script's method cards do
not apply. The gap card (`rate.sh` against jit) is the one to re-run at landing.

### Standing questions

1. **Measurement regime (relevant).**
   - Warm repeated calls, resident buffers: the throughput regime.
   - One box (7700X), gcc 15.2 -O2.
   - Instruction counts carry the decisions. Cycles were taken at load 3.2-3.5
     and move by ±10 %. The one-shot regime is measured separately (page
     faults).
   - No decision flips between regimes: B+C win in both, and win more in the
     one-shot regime.
2. **Independent control (relevant).**
   - The twins are checked against the stock artifact's answers, not against
     the analysis. ident.py runs both binaries; the harness checks
     oracle-verified `.rxt` expectations.
   - vmopt.py reads the emitted TEXT. A build's analysis will read the
     emitter's event stream. So vmopt.py (or its successor) is the build's
     independent dead-write checker: it recomputes liveness from the text, so
     it shares no source with the emitter. It must verify every write the
     build deleted is dead in the stock text, and every kept restore set
     equals its own.
   - Population is counted by census.py, which reports refusals (K35).
   - Sabotage witnesses to carry into the build:
     - §5.3b's `^(a(?1)?b)\1$` on aabbaabb (PENDING);
     - `^((?>a(?1)?))a$` (CUT_MARK);
     - `^((a)(?1)?(b))$` g lines;
     - `^(a\Kb)(?1)$` (3,4);
     - `(?:a|bc){3}+` (R25 E5, the push edge);
     - §3.2's backtrack-into-returned-call cells.
3. **What moves on regeneration (relevant).**
   - The emitted bytes of every mover: deleted SET lines, the moved restores,
     the `<p>_ret_frame` local, D183's margin constant and fewer checkpoints.
     That is an abi bump with readers found by grep.
   - limits.md §4 and §5, match_api §10.1 and §10.6, tuning §2.11 and the
     guide's numbers; the specimen re-aims trailgc2 touched
     (`fb_exact_driver.c`'s trail formula, `framebuffer.rxt`, `sr_depth`,
     `ts4`).
   - The PROGRAM listing (`--emit-ir`, S10). Elided writes must leave the
     event stream too, or the listing lies.

## Questions for Frank

1. **One build for B and C, or two?**
   - **Problem.** B (delete bookkeeping writes nobody reads) and C (a recursive
     call puts back only what its caller will read) look like two
     optimizations. They are really one analysis applied in two places, and
     they feed each other. On the JSON row, B alone saves 22 % of
     instructions and C alone 37 %, but together they save 72 %. On the
     nesting depth, B alone takes us from 85 to 125 levels and C alone to 205,
     but together to 511.
   - **Forces.** One build is larger to review. Two builds would ship a C
     whose keep sets are bloated by writes B would have deleted. They would
     also pay the emitted-text version bump and the spec-number re-pin twice.
   - **Leaning.** One build, done in two internal stages, each checked for
     identical answers before the next: first the dead-write deletion with
     calls untouched, then moving the call's restore to each call site.
   - **Open.** Is there a reason you would rather see C land alone first? It
     is the smaller emitter change, but alone it is worth less than half.
2. **Skip the third rule?** The idea "don't record a slot twice since the last
   choice point" turned out to add nothing once dead writes are gone
   (identical instruction counts and depths). **Leaning:** do not build it.
   Record it as measured and unneeded, with a revisit if the full census shows
   writes it would catch.
3. **The trail buffer is now mostly idle on these patterns.** After B+C the
   deepest nesting is limited by the choice-point stack, not the trail.
   Stock-default answers now use at most half the trail. We could shrink the
   default trail allocation and give the stack space back. **Leaning:** not in
   this build. Capacities are a spec-level contract (limits §3.2, §5), and the
   trail still matters for captures inside possessive loops. File a row
   triggered by the post-landing census of trail high-water marks.
4. **Ordering.** The next big gap after B+C is the 10-way choice tried one
   branch at a time (nest-paren is still x3.6 of the JIT, all of it from
   that), and every remaining depth limit is choice-point count. **Leaning:**
   B+C next after the one-build-at-a-time gate lifts (it lands after
   [INLINE-C], whose code-site contract it reads), then D.

## STATE AT HANDOFF

- STATE: complete (design and measurement, as briefed; no build).
- Rulings file `docs/dev/lanes/vmbc_rulings.md`: empty at every read (start,
  before the commit, before this report). Last entry applied: none.
- OWED none. The full corpus census and the corpus-wide twin run were NOT
  run: `scripts/boxlock` refused at 10:55 (queue jobs 680/681/690 ready behind
  kit job 622). The brief says not to queue and wait, so they are recorded as
  the build's STEP 0 / 0b with exact commands (Measurement cards), not as
  owed lane runs.
- Box use: single-process probes and two 50-compile harness samples (light;
  no timing window was running; the box held a kit heavy job, and loadavg was
  3-5 during my runs). No box load after 19:00.
- Evidence:
  - copies in `docs/dev/lanes/vmbc_evidence/`: the generator, checkers,
    drivers, raw rate/depth/trail tables and harness logs;
  - full scratch in `/var/tmp/pcrec-pcrec/scratch/vmbc/`: twins under `b/`,
    subjects under `subj/`.
- Not done:
  - the B+C rates on wild-sexp-balanced (its `sx-1m` subject matches early,
    so the per-call count is ~0);
  - B+C on the 11 callout bench artifacts (the twin refuses them; a build
    models them with row 7).
