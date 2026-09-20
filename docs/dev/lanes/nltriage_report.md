# nltriage — TRIAGE of the Linux battery's `[OPT-4.1] -fprefilter` red at 05499cba

Lane `nltriage`, branch `lane/nltriage`, 2026-09-20, opus. Triage +
targeted fix. No ssh to ubuntubudu (a battery held it); every number below
is measured on the Mac dev box (M1 Max, darwin, gcc-16).

## Verdict

**MARGINAL CPU BUDGET on the slower box. Not introduced by any commit in
the suspect range.** The `test`-stage red

```
FAIL: [OPT-4.1] '(a|b){0,30000}' under -fprefilter no longer COMPILES — this is
limits.md §3.3's 'no pattern that compiles today stops compiling' going false: ...
watchdog: sizecap-fprefilter alternation: CPU limit exceeded (limit 45s of CPU time)
(TERM->KILL), peak rss 26796 kB
```

is the check's own `K7_CPU` budget expiring, reported through an `else` arm
that could only say one thing. The pattern compiles. Nothing about
limits.md §3.3 went false.

Fixed here on two axes, both validated: the witness is made ~6x cheaper so
the budget is no longer marginal on any box, and the `rc` arm becomes a
`case` so a watchdog kill can never again be reported as a spec violation.

## 1. The timing table — no step between the three trees

The check builds its own lowered-cap reference compiler (`-O1`, all of
`src/`, `-DPCREC_MAX_EMIT_BYTES=500000`) and times this one invocation:

```
<REFCAP> -p rx -fno-scan-edge -fno-start-pinned -fprefilter -o OUT.c '(a|b){0,30000}'
```

Reproduced at three trees via `git archive`, each built identically with
`gcc-16`, run five times round-robin. **User CPU seconds:**

| run | 25b1984f (pre-w5) | 55321f28 (w5 merge) | 05499cba (the red) |
|---|---|---|---|
| 1 | 11.302 | 11.319 | 11.316 |
| 2 | 11.287 | 11.289 | 11.285 |
| 3 | 11.281 | 11.309 | 11.281 |
| 4 | 11.288 | 11.305 | 11.293 |
| 5 | 11.278 | 11.299 | 11.292 |
| **median** | **11.288** | **11.305** | **11.292** |
| emitted artifact | 18,160 B | 18,160 B | 18,160 B |

Spread across all fifteen runs is 11.278-11.322s, **under 0.4%**, and the
three artifacts are byte-identical. There is no step, so the brief's
bisection step (3) is not entered.

Two independent corroborations:

- **The `src/` diff over the range is renames.** `git diff 25b1984f
  05499cba -- src/ir/dfa.c src/opt/minimize.c` is 100% `ctx_fail` ->
  `pcrec_ctx_fail`, `arena_alloc` -> `pcrec_arena_alloc`, `ctx_nomem` ->
  `pcrec_ctx_nomem` — identifier text, in code and in comments. No
  algorithm, no data structure, no allocation shape.
- **The Linux peak RSS matches.** The battery reported `peak rss 26796 kB`;
  this box measures a 29,056 kB peak for the same compile. The killed
  process had reached ~92% of the work's memory high-water mark, so it was
  doing the same work, not stuck in a new phase.

The check's `-O1` reference build is also exonerated as a cost: an `-O2`
build of the same tree runs the same case in 11.36s (the cost is
memory-bound DFA minimization, K25, which `-O2` does not help).

## 2. Why 45s was thin on ubuntubudu and not here

`K7_CPU`'s own calibration comment (`run_resource_tests.sh:90-105`) says
45s is "~3x the measured 15.4 s" and that "CPU is load-RESILIENT but not
load-independent, and that file records a measured >2x inflation under a
real `make -j12` mix."

| | |
|---|---|
| Mac quiet CPU for this case | 11.29s |
| Budget (`K7_CPU`) | 45s |
| Margin on the box that set the budget | 3.99x |
| Documented CPU inflation under a real `-j12` mix | >2x |

A 3.99x margin against a >2x inflation figure is ~2x of real headroom on
*this* box. ubuntubudu is a materially slower single core (Ryzen 5 1600 vs
M1 Max; `xarch_step0.md` measures Mac 1.93x faster on the compile axis),
which consumes that headroom before contention is counted at all. This is
`btriage2_20260918_report.md`'s finding recurring at a second cell in the
same file — that lane fixed Section 1b by widening the budget
(`SIZECAP_CPU`, 180s); this cell sits in a later section and still rode
`K7_CPU`.

The rc=0 result at 25b1984f eight hours earlier is consistent with a
marginal cell rather than contradicting the diagnosis: a cell this close to
its budget is decided by box load, not by the tree.

## 3. The fix (1) — the witness is scaled down, not the budget up

The reference cap is an artificial number this check chooses for itself, so
the witness can be scaled to meet the cap instead of the budget scaled to
meet the witness. The cost is `{0,N}`'s DFA minimization, not anything the
cell asserts. Measured at the reference build:

| N | reference cap | exact prefilter | margin over cap | rescue artifact | CPU |
|---|---|---|---|---|---|
| 30000 (old) | 500,000 | 913,599 B | 1.83x | 18,160 B | 11.29s |
| **12000 (new)** | **100,000** | **373,590 B** | **3.74x** | **18,151 B** | **1.83s** |

The new pair is strictly better on every margin the cell depends on:

- The **exact artifact clears the cap by 3.74x** rather than 1.83x. That is
  the margin whose erosion made this cell vacuous four separate times (the
  comment block above it records all four); it is now the widest it has
  ever been.
- The **decline is still unaffected by the lowering**, which is what makes
  this a test of an OVERRIDE rather than of a compiler that always takes
  the size rung: at N=12000 under the lowered cap the default axis still
  stamps `RX_ENGINE_SEL "declined-nullable-default"` / `RX_VM_PREFILTER
  "none"` at 12,114 B, and the collapsed rescue is 18,151 B — both 5-8x
  under the cap.
- The **CPU margin against `K7_CPU` goes 3.99x -> 24.6x**, wide enough that
  no box's contention reaches it, and `make test` gets ~9.5 CPU-seconds
  cheaper.
- The **rescue artifact is the same artifact**: diffed against the N=30000
  one, the only moving lines are the pattern text, the `-o` basename, the
  cap value and the count digits (16 diff lines, all of them those).

`[OPT-4.2]`'s cell above keeps its own `(a|b){0,30000}` at the real cap and
is untouched.

**No sabotage floor reaches this cell.** The three `SAB_REACH_POP` lines
naming `run_resource_tests.sh` are `^size_rung_cell ` (S206/S207, the
`sizecap_default` pair at lines 710-711, which use `$PCREC` and the real
cap), `bytes of emitted C source` and `size_moved=` (S193, Section 1b).
None greps this cell's pattern text or its cap. S206/S207's canonical
`resource:1fail/28pass` and `2fail/27pass` cell counts are unchanged.

## 4. The fix (2) — the `rc` arm is a `case`, and that is the same finding

The old arm was `if [ $? -eq 0 ] ... else bad "<the §3.3 sentence>"`. It
folded every non-zero outcome — a real refusal, a watchdog CPU kill, a wall
timeout, an RSS kill — into one message asserting that a caller-facing
contract had gone false. Section 1's `compile_case` has distinguished 122 /
123 / 124 since [TT-10] and routes the two outcomes CPU-time inflation can
produce through `load_guard_tripped`; this cell now does the same. Only
`rc 1`, a real refusal, still carries the §3.3 sentence.

This is the house's recurring *a check's FAILURE MESSAGE is a second,
undeclared claim about the space of causes* class (dialimpl, w23impl), in
its sharpest form yet: the message named a spec section by number.

**Both directions validated.**

| control | result |
|---|---|
| `K7_CPU=1` (forces the CPU kill) | `FAIL: ... EXCEEDED 1s of CPU on a quiet box — THIS CELL'S OWN BUDGET, not a compile failure and not a §3.3 event ...` |
| `REFCAP_CAP=9000000` (rung never runs; scratch, reverted) | `FAIL: ... stamps PREFILTER 'hybrid' / LANG_WHY 'exact', expected the size rung's collapsed prefilter` |

The second control is what says the cheap witness did not make the cell
vacuous: it still genuinely requires the rung to fire.

## 5. Is limits.md §3.3 the right tier for a CPU-budgeted compile?

No, and the spec says so in the paragraph immediately after the sentence
the check quoted. §3.3 is titled "Compile-time budgets: two different
things named 'limit'" and exists precisely to keep them apart. Its promise
is about the ACCEPT/REFUSE relation — hard state-count ceilings that make
compilation "FAIL cleanly, naming the ceiling" — and the very next
paragraph reads: "**What pcrec does NOT promise is a bound on wall-clock
compile TIME** for a pattern it accepts. D45 is a TEST HARNESS policy, not
a caller-facing contract ... a guard on the SUITE." A `scripts/watchdog`
CPU kill is that suite guard expiring, which the spec's own text places on
the other side of the line it draws. So the §3.3 sentence is the right tier
for the cell's `rc 1` arm and the wrong tier for every other outcome —
which is exactly what the `case` now encodes. No spec change is owed: the
document was already right and the check was reading it at the wrong
altitude.

## 6. Validation

All on this box, at `lane/nltriage`.

| | |
|---|---|
| `bash tests/resource/run_resource_tests.sh` | **27 passed / 0 failed / 0 inconclusive**, 1 section skipped (the standing darwin `ulimit -v` skip) |
| suite wall / CPU | 147.0s real / 145.6s user |
| `[OPT-4.1]` cell | `PASS: '(a|b){0,12000}' under -fprefilter KEEPS the collapsed prefilter (18151 bytes, 'size cap retry, exact 373590 > 100000')` |
| `make strict CC=gcc-16` | clean |
| failing-direction controls | both fire correctly (§4) |

Nothing owed on this box.

## 7. What the manager should still request on Linux

The fix does not depend on a Linux number — the new margin is 24.6x on the
slowest plausible reading. But if the manager wants the budget question
closed on its own terms rather than dissolved, this is the one quiet-box
measurement that answers it, at the pre-fix tree:

```
git -C <tree> checkout 05499cba
SRCS=$(find src -name '*.c' | LC_ALL=C sort)
gcc -O1 -std=gnu11 -Ilib -Isrc -DPCREC_MAX_EMIT_BYTES=500000 -o /tmp/pcrec_lowcap cli/main.c $SRCS
/usr/bin/time -v /tmp/pcrec_lowcap -p rx -fno-scan-edge -fno-start-pinned \
    -fprefilter -o /tmp/o.c '(a|b){0,30000}'
```

on an **idle** box, reporting user CPU seconds. Against this box's 11.29s
it gives the real Mac/Linux ratio for pcrec's minimization path (as
distinct from `xarch_step0.md`'s gcc-compile ratio of 1.93x), which is the
number every `K7_CPU`-family budget in the tree is implicitly calibrated
against and which no measurement currently pins. If it lands above ~22s the
budget was under water quiet, not merely under contention — worth knowing
for the other eleven `K7_CPU` call sites, none of which this lane touched.

## Commits

On `lane/nltriage`: the `tests/resource/run_resource_tests.sh` fix (witness
+ `case` arm + the measurement recorded in the comment block), and this
report.
