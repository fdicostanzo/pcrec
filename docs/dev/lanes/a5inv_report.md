# a5inv: is A5 (the "no scan means 10^6 ppm" branch of `pcrec_dfa_cand_ppm`) a bug or intent?

Lane a5inv (2026-10-12, sonnet; read-only analysis, stamps and a code-path
probe only, no timing; nothing under `src/`, `tests/` or `docs/spec/` touched).
Chunk 1 of `docs/dev/chunks_2026-10-11.md`. Read at main `35b78793`, abi 75.

## Verdict

**DELIBERATE-BUT-UNRECORDED, and over-weighted by the summary.**

1. The 10^6 is the definitional answer to "how often does this scan stop":
   a scan that tests nothing stops at every position. That was the author's
   stated reason, in the code comment of the commit that introduced the
   function (`eeab6527`): "1,000,000 when it tests none (every position is
   then a candidate)". The parenthetical was dropped when the function was
   rewritten onto `cand_rows[]` (`1f284904`, `7d2cd2bc`, `7ad018d2`), and
   `hyb_reseed.md` §4 kept only the fact. The reason exists and is correct;
   it is just not in the tree any more.
2. The summary's weight is wrong. Of the 16 artifacts counted as A5, only 12
   take a 10^6 branch, and of those 6 have a dead retry loop. Exactly **6 of
   35 corpus `adaptive-dense` artifacts (17%; 6 of 19 = 32% under `-e utf8`)
   have any run-time consequence of the branch, 3 distinct patterns, and the
   bench has 0**. Not 46%.
3. Answers are unaffected either way (D158 holds; see "Run time" below). The
   only open question, whether `dense` is the better START for the 3
   ATTEMPT-route patterns, is clock-only, bounded (at most one step block per
   call), and has no D77 trigger (bench reach 0, corpus population
   synthetic). Measurement named below; NOT run.
4. A separate small finding the investigation surfaced: the 4 `rev-end`
   artifacts are not A5 at all. They read a real mass (807,006 ppm) off the
   FORWARD candidate set, a scan the artifact does not emit (F1 below).

No fix is proposed for A5. Changing the answer moves 12 stamps and is an abi
event (the `RX_VM_RESEED` value and the emitted initial constants), for a
population with no measured need.

## 1. The code and its history

`pcrec_dfa_cand_ppm` (`src/gen/emit_dfa.c:7427`) is read by exactly one
caller: R4, `cand_rs_dense_applies` (`:8740`), the `adaptive-dense` row of the
hybrid retry table: `ppm * reseed_gap > 1,000,000` (the gap is the class's
crossover: 4 framed, 16 frameless). It returns the prior's MASS over the byte
set the emitted candidate scan tests, through three paths:

| path | when | value |
|---|---|---|
| byte | `dfa_cand_scan` found a single-byte scan (memchr, an offset/run row's scan byte, or the ATTEMPT route's predecessor `memchr`) | that byte's rate |
| set | the route is DFA, the selected `dfa_pfs` row's `scan == PF_SCAN_SET` | the set's mass |
| **branch 1** | `!pcrec_artifact_has_dfa_scan(cx)` or `cand_route_of == CAND_ROUTE_ATTEMPT` (and no predecessor byte) | **1,000,000** |
| **branch 2** | route DFA, but the selected row's `scan != PF_SCAN_SET` | **1,000,000** |

History (`git log -S`): introduced in `eeab6527` (lane reseed, 2026-09-29)
with the comment above. Its sources of record say nothing more:
`docs/dev/lanes/reseed_report.md` §1 item 3 argues only that the predicate must
not test the prior's NONE (D126 Q4); `docs/dev/reviews/2026-09-30-r1-hyb-reseed-*.md`
(sem/checks) never ask about the no-scan value (checks F2 is about the prior
under `-e byte`/`-e utf8`). So the single recorded reason is the one comment.

## 2. The 16 artifacts (stamps, never emitted comments)

Reproduction: `docs/dev/summaries/prior_cost_inputs/reach_probe.py` unchanged
(4 workers instead of 8), `build/pcrec` at main `35b78793`, `-p rx --features
all`, `-e byte`. It reproduces the summary exactly: 5,194 compiled, 476
`adaptive*`, 35 `adaptive-dense`, 16 with `RX_DFA_PREFILTER none`.

The path column is not a stamp: it was read by running an `-O0` scratch build
of `emit_dfa.c` under gdb (breakpoints on the four exits of
`pcrec_dfa_cand_ppm`) and cross-checked with the function's returned value
(`finish`). The stamps alone cannot split the 16.

| file (tests/) | pattern | `RX_DFA_SCAN` | `RX_DFA_PREFILTER` | `RX_VM_RESEED` | path / value |
|---|---|---|---|---|---|
| litscan/handoff.rxt (2 blocks) | `(?:\Gab\|x)(cat)(?=dog)` | attempt | none | adaptive-dense | branch 1, 10^6 |
| atomic_groups/atomic_assert.rxt | `(?>\Ga\|b)c` | attempt | none | adaptive-dense | branch 1, 10^6 |
| atomic_groups/d27/interactions.rxt (2 blocks) | `(?>\Ga\|b)c` | attempt | none | adaptive-dense | branch 1, 10^6 |
| atomic_groups/atomic_assert.rxt | `(?m)(?>^a\|b)c` | attempt | none | adaptive-dense | branch 1, 10^6 |
| lookaround/d27/matrix.rxt | `(?>(?*[ab])z)` | empty | none | adaptive-dense | branch 2, 10^6 |
| lookaround/d27/matrix.rxt | `(?>(?*a)z)` | empty | none | adaptive-dense | branch 2, 10^6 |
| lookaround/d27/matrix.rxt | `(?>(?=[ab])z)` | empty | none | adaptive-dense | branch 2, 10^6 |
| lookaround/d27/matrix.rxt | `(?>(?=a)z)` | empty | none | adaptive-dense | branch 2, 10^6 |
| atomic_groups/atomic_assert.rxt | `(?>a\b)c` | empty | none | adaptive-dense | branch 2, 10^6 |
| atomic_groups/atomic_assert.rxt | `(?>a\|ab)\bc` | empty | none | adaptive-dense | branch 2, 10^6 |
| revend/stage2_captures.rxt | `(?<=^\|,)(\w+)$` | rev-end | none | adaptive-dense | set path, **807,006 ppm** |
| assertions/rev_end.rxt | `(\w{1,2})(?:(?=)\|)$` | rev-end | none | adaptive-dense | set path, 807,006 |
| assertions/rev_end.rxt | `\w{1,2}(?:(?=)\|)$` | rev-end | none | adaptive-dense | set path, 807,006 |
| possessify/composition_d27.rxt | `\w{1,2}(?:(?=)\|)$` | rev-end | none | adaptive-dense | set path, 807,006 |

(Patterns are shown with single backslashes. The rows total 16 corpus lines:
6 ATTEMPT, 6 empty, 4 rev-end; 12 distinct patterns: 3 + 6 + 3.)

Control population, same probe: the ATTEMPT route also yields 3 `adaptive`
(non-dense) artifacts, e.g. `(?m)^(?>a+)$`, because there `attempt_cand`
supplies a predecessor `memchr` byte and the byte path prices it. So the table
already separates "ATTEMPT with a scan byte" (priced) from "ATTEMPT without"
(every position). Under `-e utf8` (prior NONE, cardinality) the same probe
gives 490 `adaptive*`, 19 dense, and the 12 branch-1/2 artifacts are 12 of 19
(63%); the 4 rev-end flip to `adaptive`. The bench (339 `bench/*/patterns/*.rx`
compiling at `-e byte --features all`; `RX_VM_RESEED`: 284 none, 31 exact, 12
adaptive, 11 clamped, 1 anchored) has **0** `adaptive-dense`.

## 3. What the verdict means at run time, per class

R4 only chooses the retry's STARTING state; `adaptive-dense` and `adaptive`
run the same arm (`CAND_RS_A_ADAPT`, `emit_vm.c`). Emitted constants, from the
artifacts above: framed dense `reseed_steps = 64, reseed_block = 16` (cap 64),
frameless dense `1024 / 64` (cap 1024); adaptive starts at the class's `first`
(framed 2, frameless 64) with block 0. After each failed attempt the loop
steps while `reseed_steps` is nonzero, then re-seeds from the prefilter and
reads the gap (a gap >= the class crossover disarms the block). Each block
ends in exactly one re-seed (the probe), so a wrong start costs at most one
block per call.

**EMPTY (6 artifacts): behaviourally nil.** `rx_prefilter` is emitted as
`return 0;` (the language is empty: `a\bc`, `(?=a)z`, ...), and `rx_search_run`
calls it before the retry loop and returns 0 on `!= 1`. The loop, and so the
verdict, is dead text. Dense, adaptive and fixed are the same program in
effect. (These are also artifacts that need no VM at all; a separate
observation, not this lane's.)

**ATTEMPT (6 artifacts, 3 patterns): the only class where the branch decides
anything, and 10^6 is literally right about the scan.** The prefilter is an
attempt loop (`for (start = search_from; start <= start_max; start++)` running
the anchored DFA at each start), so the "scan" stops at every position. What
that class does NOT share with a scanned prefilter is the cost premise of the
crossover: a re-seed there costs gap x (one DFA attempt per position), not a
constant ~25 ns (`reseed_report.md` §1 item 1), so re-seeding is no cheaper
than stepping when the VM step is cheap (frameless, 1.6 ns/position) and
clearly cheaper when it is expensive (framed, 8.6 ns/position against a DFA
attempt of the order of 1-3 ns, which is an estimate, not a measurement). All
3 patterns are framed. So for them `dense` plausibly starts in the slower mode
for up to 64 steps (about 0.4-0.5 us, same estimate) on a sparse subject, once
per call, against `adaptive`'s 2 steps before its first re-seed; on a
candidate-dense subject the dense start is right. Direction and size are
subject-dependent and the effect is bounded; this is the one clock-only
residual.

**rev-end (4 artifacts): not this branch** (F1).

**Answers.** D158 ("adaptation may never turn an answer into a give-up") is
untouched by the choice. The retry-table argument (`hyb_reseed.md` §4, sem
review F2/F5) is that past rows 1-2 every adaptive artifact is clamp-free, and
on those today's retry (`-fno-hyb-reseed`) steps EVERY position after a
failure, so both starting states attempt a subset of today's attempts, in the
same order. Dense vs adaptive can differ from each other only in how many
non-matching attempts they charge to the shared budgets (more steps charge
more), never beyond today's. The rev-end and EMPTY classes cannot differ at all
(rev-end's attempts are bounded by the trailing window; EMPTY never reaches the
loop). For ATTEMPT, an attempt at a position the DFA rejects is a VM attempt
that fails at its first byte; sem review F2 measured such attempts as ~0 work.

## 4. Alternatives, and their consequence

- Answer `adaptive` ("decline to call it dense") for the no-scan branches: 12
  corpus stamps move (6 ATTEMPT `adaptive-dense` -> `adaptive`, 6 EMPTY, whose
  retry is dead); the emitted `reseed_steps`/`reseed_block` initialisers move
  on all 12; this is an emitted-scaffolding change, so an abi event with the
  D76/D94 ritual (every reader of the number by grep, identity re-pin). Run time:
  the 6 EMPTY unchanged; the 6 ATTEMPT change only their first block per call.
  No answer moves. It would also contradict the prior-cost design's own NONE
  rule (rev 2 keeps 10^6 "because its own NONE (zero stops) would flip R4",
  per the summary's A5 row).
- Keep 10^6 and record the reason: comment-only plus doc hunks, no abi event.
  This is the recommendation.

## 5. What to record, and where

(a) `src/gen/emit_dfa.c`, header of `pcrec_dfa_cand_ppm` (comment only, not an
abi event, but `make test-codegen` and the comment-gate readers are the usual
suites): restore the reason with its two cases: "a scan that tests nothing
stops at every position: the ATTEMPT route runs a DFA attempt at each start,
and the `empty` row's prefilter never answers (its retry loop is
unreachable)". (b) `docs/design/hyb_reseed.md` §4 (the sentence at
"It is 1,000,000 when the scan tests nothing"): add the same two-case reason
and the population note (ATTEMPT-without-memchr and `empty` only; `rev-end`
reads a mass, F1). (c) `docs/design/prior_cost_unify.md` rev 2 and the
`pcureport` summary's A5 row: correct "16 of 35 / 46%" to 12 of 35, 6 with
run-time consequence (17%), and reclassify A5 from INCIDENTAL to DELIBERATE
(stated in the original comment). These are the manager's edits; this lane
made none.

## 6. The clock-only residual: measurement, not run

Question: for the ATTEMPT class, is the `dense` start slower than the
`adaptive` start, and where does the crossover sit? Cells: the 3 ATTEMPT
patterns (`(?>\Ga|b)c`, `(?m)(?>^a|b)c`, `(?:\Gab|x)(cat)(?=dog)`), each at
`-p rx --features all`, `-e byte`. Arms (one program each, interleaved
round-robin, same box, pinned core): (1) as emitted (`adaptive-dense`); (2)
the emitted artifact with the two initialisers edited by hand to the framed
`first` start (`reseed_steps = 2, reseed_block = 0`), which is a twin by text
edit, since no deny selects `adaptive` over `adaptive-dense`; (3)
`-fno-hyb-reseed` (`fixed`). Subjects: sparse (candidates every >= 256 B, so
the dense block of 64 steps is pure waste), match-dense (candidate every 1-2
bytes), and bursty; regimes: one long call (throughput) and find-all with one
call per match (per-call, where `reseed_report.md` §5 already shows the start
matters, `item(?= done)` x0.62). Each pair gets its own null band (two copies
of one program). Answer identity checked on every cell first. D77: not
triggered (bench reach 0, corpus population synthetic and 3 patterns), so
this is a filing, not a request.

## 7. Findings beyond the question

- **F1: `rev-end` artifacts are priced off a scan they do not carry.** With
  `RX_DFA_SCAN rev-end` the prefilter is the end-anchored reverse walk
  (`RX_DFA_PREFILTER none`), but `pcrec_dfa_cand_ppm` falls through to
  `unanch_start`/`dfa_pf_read` and prices the FORWARD row's candidate set
  (`\w`, 807,006 ppm under the default byte prior), contradicting the
  function's own header ("so it cannot price a scan the artifact does not
  carry"). The summary counted these 4 as A5 because it keyed on the
  `RX_DFA_PREFILTER none` stamp. They answer `dense` here and `adaptive`
  under `-e utf8` (cardinality), so the stamp already depends on a number
  nothing emitted uses. The right answer is not obvious: the rev-end
  prefilter's re-seed re-walks from `n` back to the new position (cost grows
  with the trailing window, not constant), which argues for stepping (dense)
  structurally, and candidates exist only in the trailing window, so the
  subject bounds the damage either way. Making the branch say "no forward scan
  emitted" (10^6) would move 0 stamps at `-e byte` and 4 at `-e utf8`. Not an
  answer defect. Filed here as an input to [PRIOR-COST-UNIFY]'s adapter list,
  not a bug row (D77: no measured need).
- **F2: a method note for the next count.** `RX_DFA_PREFILTER none` is not a
  stamp for "branch 1/2": it also stamps `rev-end`. The population needs the
  code path or a stamp that names the selected row's `scan`, which `--emit-facts`
  or the trace build could provide. Scratch `-O0` plus gdb finish values were
  used here and are not committed.

## Reproduction (scratch only, uncommitted)

All in `worktrees/a5inv/build/a5/` (gitignored): `probe.py` = the summary's
`reach_probe.py` with 4 workers; `probe8.py` adds `-e utf8`;
`benchprobe.py` compiles `pcrec-bench/bench/*/patterns/*.rx` read-only;
`pcrec0` = `cli/main.c` linked against an `-O0 -g` build of
`src/gen/emit_dfa.c` and `build/libpcrec.a`; `g.cmd` = the gdb breakpoint
script, run per pattern. Compile parallelism was at most 4; no suite, no
timing.
