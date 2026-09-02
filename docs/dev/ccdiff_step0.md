# [CC-DIFF] STEP 0 — where clang optimizes the emitted C better than gcc

Lane `ccdiff`, 2026-09-02. Chartered by Frank: *"I would be interested in some
investigation of where clang is optimizing better for purposes of considering
making the same move in emitted code to make it more general. I don't want to
go too deep down the asm optimization path (there be dragons) but there might
be some low hanging fruit."* One lane-day, no inline asm, no intrinsics, no
per-arch work.

Explaining bench ledger `2026-09-02-full-suite-1989c62.md` §5, whose headline
is that clang beat gcc by ×2.4–2.6 on some cells from the same emitted C and
lost by ×2 on others.

**Verdict up front: the fruit hangs LOW, and it is one transformation, not
seven.** On the forced-VM arm — the ledger's general signal, a median of 0.599
over 43 throughput cells — clang inlines pcrec's VM entry chain and gcc does
not, so every `<prefix>_search` call under gcc builds a 152-byte frame, pays a
stack-protector canary and makes an out-of-line call for working storage that
a frameless artifact never touches. One attribute on the emitted static
helpers takes gcc to clang's shape, is answer-identical, and does not disturb
either control where gcc legitimately wins.

## Method

Artifacts emitted with the bench's own argv (`pcrec -p rx --features all
[--engine=vm] -o artifact.c -- '<pattern>'`; the `match-compliance` regime
uses the whole-subject text `(?:<pattern>)\z`, per pcrecbench
`record.whole_subject_text`) and compiled through the bench's own
`testees/pcrec/shim.c` with its exact flags, `-O2 -std=gnu11 -fPIC -shared`,
no `-march`. **gcc 15.2.0** (Ubuntu 15.2.0-16ubuntu1), **clang 21.1.8**
(Ubuntu 6ubuntu1).

`git log 1989c62..22a6775 -- src/` is empty, so the emitter has not moved
since the ledger's pin and every artifact here is byte-identical to the one
the bench measured.

Timing harness reproduces `testees/pcrec/driver.c`'s three regime loops
verbatim and calls through `dlsym` exactly as the bench does, so neither
toolchain gets cross-translation-unit inlining the bench would not have given
it. Five process launches per point, medians. Load conditions are stated with
the numbers below.

---

## 1. `cls-upto-4` (`[a-z]{0,4}`) / large-subject-throughput / `auto` — ledger 0.407

**NAMED: uniform-table constant folding.**

Every one of this artifact's six DFA tables is uniform — `rx_forward_next_state[4]`
is all `65535` (dead), `rx_forward_is_accepting[4]` all `1`, and the reverse
and anchored pairs the same — because [OPT-5]'s scan edge absorbed every real
transition, which the emitted comment says in as many words ("The class's cell
above reads *dead* because of this").

LLVM folds a load from an all-equal constant object regardless of the index
(`ConstantFoldLoadFromUniformValue`). gcc 15 does not fold a variable-index
load even from an all-equal `static const` array. So clang proves the DFA step
unconditionally dead, deletes the outer `for(;;)`, deletes all three table
base `lea`s, and with the register pressure gone deletes the frame:

```
gcc    rx_search: 142 instructions, 3 callee-saved pushes, 6 table-base leas
clang  rx_search:  76 instructions, 0 pushes,              0 table-base leas
```

Secondary, smaller: clang **fully unrolls the bounded scan-edge run loop**
(trip bound 4) into four straight-line class tests and eliminates the
`scan_run_length` counter; gcc keeps it rolled with a `cmp $0x4` per byte.

## 2. `floor` (`:`) / match-compliance / `auto` — ledger 0.432 — DOES NOT REPRODUCE

Summed over all 49 subjects of `floor`'s compliance set, five interleaved
rounds: **clang's absolute number reproduces the ledger to 1.4 % (214.6 vs
217.6 ns); gcc's does not (median ~307 vs 503.3).** The measured ratio is
~0.79, not 0.432.

And there is no transformation to name. Both `rx_match` bodies are the same
shape and nearly the same length — gcc 53 instructions, clang 48 — both a
bottom-tested rotated loop of 12 instructions per byte, both hoisting the
three table bases into the entry block. If anything gcc's entry is leaner: gcc
pushes one callee-saved register, clang pushes three.

**A layout / i-cache artefact of the ledger's gcc build, not a codegen
difference** — at ~5 ns per call over 49 short calls that is exactly the scale
code alignment moves. Worth a re-run on the bench side; nothing for pcrec to
chase. (Stop rule applied.)

## 3–6. The four VM cells — the general signal, and it is ONE transformation

`dig-upto-16` thr/vm (ledger 0.378), `stack-frame` search/vm (0.680), and the
two controls where clang LOSES, `floor` thr/vm (1.996) and `nest3-16` thr/vm
(1.511).

**NAMED: clang inlines the VM entry chain; gcc stops at the first call
boundary.**

On all four, gcc's `<prefix>_search` is a stub that

1. allocates a **152-byte stack frame** for `rx_run_state run` plus
   `rx_run_buffers storage`,
2. stores the four run-state binding fields,
3. pays a **`-fstack-protector-strong` canary** — read, spill, reload,
   compare, branch to `__stack_chk_fail` — because the arrays in
   `rx_run_buffers` are what trigger it, and Ubuntu's gcc has the flag on by
   default,
4. and then **CALLs `rx_search_run` out of line**,

per search attempt, for storage a frameless artifact never touches.

clang inlines `rx_search_run` into `rx_search` in all four cases; on the two
FRAMELESS artifacts it inlines `rx_match_anchored` too and then proves the
whole run state dead and deletes it — no frame, no canary, no binding stores.

Directly witnessed rather than inferred: `nm` on the loglines `stack-frame`
artifact lists `rx_search_run` as a local symbol in the gcc build and **no
such symbol in the clang build**, with `rx_match_anchored` out of line in
both (it holds the computed goto, which neither compiler will inline).

### The two controls are NOT this transformation, and that matters

**`floor` / thr / vm (1.996 — gcc's biggest win).** Here the entry cost is
amortised over 16,384 match attempts, so it is irrelevant; the hot loop is the
attempt loop, and gcc simply builds it better:

```
gcc   (4 insns, 2 branches)      clang (6 insns, 3 branches)
  cmpb $0x3a,(%rdi,%rdx,1)         cmp  %rsi,%rdx        <- bound test 1
  je   hit                         jae  .skip
  add  $0x1,%rdx                   cmpb $0x3a,(%rdi,%rdx,1)
  cmp  %rsi,%rdx                   je   hit
  jne  loop                      .skip:
                                   cmp  %rdx,%rsi        <- bound test 2, redundant
                                   je   ret
                                   inc  %rdx
                                   jmp  loop             <- unconditional back-edge
```

gcc **rotates the loop and merges the two subject-length comparisons** (one
from `rx_match_anchored`, one from `rx_search_run`'s bump-along); clang leaves
it top-tested, keeps both, and closes with an unconditional jump. 6
instructions and 3 branches per byte against 4 and 2 — the measured ×2.

**`level-context` / search / `auto` (1.693 — the corpus pattern clang builds
worst).** The hot code is the collapsed prefilter's table walk. gcc keeps one
tight 16-instruction loop; clang duplicates the enclosing block and
**recomputes the loop-invariant `scan_position + 1 < subject_length` bound
inside each copy** (`cmp / cmova / dec`, twice) instead of hoisting it, giving
a 48-instruction loop. A missed loop-invariant hoist plus block duplication.
Nothing for pcrec to copy.

Both controls are gcc doing something right that clang does not, and **neither
has anything to do with the entry chain** — which is why the fix for cells 3–6
can be taken without paying for them.

---

## Candidate emitter spellings, ranked

### 1. `always_inline` on the emitted VM helpers (twin V) — RECOMMENDED

**(a) Targets:** every artifact with a VM entry chain — the ledger's forced-VM
large-subject-throughput median of 0.599 over 43 cells, and the `auto`
hybrids. Corpus reach measured over all four bench sets: **83 of 180 emitted
artifacts have the chain; 36 of 90 forced-VM artifacts (40 %) are frameless**
and get the full storage elision as well as the inline.

**(c) Effect on the controls:** none, measured statically and by timing.
`floor`/thr/vm keeps gcc's rotated 4-instruction attempt loop **and** loses
the frame and canary — a strict improvement, not a trade.
`level-context`'s prefilter body is **byte-identical** before and after.

**(d) Generality:** one emitter site, `src/gen/emit_vm.c`'s emitted function
headers. The attribute goes on every emitted static helper except the
matcher; the matcher joins them **only when the artifact is frameless**,
because gcc *refuses* `always_inline` on a function containing a computed goto
(a hard error, not a warning). That gate is not a new condition: it is the
same `has_push` predicate [CC-CLANG] already evaluates to decide whether to
emit the pop-and-resume dispatch at all. And the attribute constrains only the
compiler that was not already doing this — clang inlines the same set on its
own — so it moves gcc toward clang rather than pinning either.

Two independent wins ride in it: the out-of-line call disappears, and on a
frameless artifact so do the 152-byte frame and the stack-protector canary.
The canary is the one worth naming to Frank: pcrec is paying a security-
hardening tax on every search call for a buffer the artifact provably never
writes.

### 2. Uniform-table folding in the emitted step helpers (twin A)

**(a) Targets:** the `cls-upto-*` / `dig-exact-*` / `hex32` / `year4` /
`pw-8-64` family — the bounded patterns whose scan edge has absorbed the whole
machine. This is the ledger's own named win population ("`floor`, `year4`,
`dotted4`, `hex32`, every `cls-upto-4/8/16/32` and every `dig-*`") and the
overlap is close to exact.

**(d) Generality:** measured **22 of 90 `auto` artifacts (24 %)** across
bounded, loglines, altwide and email carry at least one uniform table. The
rule is a general property of a table, not of a pattern: pcrec builds these
tables, so it already knows whether every cell is equal. One emitter site (the
`_step` / `_accepts` helper bodies in `src/gen/emit_dfa.c`); putting it in the
helper body rather than at the call sites means every argument is still
evaluated, so no side effect is lost.

Ranked second only because its reach is a quarter of the corpus where twin V's
is near half, not because the per-cell effect is smaller — it is larger.

### 3. Single-induction-variable scan edge (twin C) — NOT WORTH IT ALONE

Folding the `scan_run_length < N` bound into a cursor limit computed once
before the loop. It does what it says — the counter disappears — but **gcc
still declines to unroll**, and the static result is a rounding error: 138
instructions against the original 142, frame unchanged at 3 pushes. Stacked on
twin A it costs 3 instructions (80 vs 77). It has the attraction of needing no
unroll threshold and being correct for `{0,4}` and `{0,65535}` alike, so it is
worth keeping on the shelf if the edge loop is ever revisited for its own
sake, but it does not earn a charter.

**Explicitly rejected:** `#pragma GCC unroll N` on the edge. It needs a
literal bound and therefore a size threshold policy in the emitter, and it
buys what twin C buys without twin C's generality.

**Explicitly rejected:** any `-f` flag in `GENCFLAGS`. Nothing here needs one.
`-fno-stack-protector` would get part of twin V's benefit and is exactly the
wrong way to get it: it would disable hardening on every artifact including
the ones with real buffers, where twin V removes only the buffer that is
provably dead.

## Answer identity

Every twin checked against **both** the gcc original and the clang build over
all 178 bench subjects (bounded + loglines, compliance and throughput
corpora) in all three regimes, comparing every reported span rather than a
count: **3,204 comparisons, all identical.**

## Measured hand-twin ratios under gcc

<!--TIMINGS-->

---

## Worth chartering / not worth it

**WORTH CHARTERING: twin V, the `always_inline` spelling on the emitted VM
helpers.** It is one emitter site, it rides a stamp pcrec already computes, it
is answer-identical, it leaves both controls where gcc legitimately wins
untouched, and it addresses the ledger's general signal rather than one cell.
The stack-protector canary on provably-dead buffers is a finding in its own
right.

**WORTH CHARTERING, second: twin A, uniform-table folding.** Narrower reach
(a quarter of `auto` artifacts) but a larger per-cell effect, and it is a
general fact about a table the emitter already has in hand.

**NOT WORTH IT: twin C, the pragma-unroll variant, and any `GENCFLAGS` flag.**

**FOR THE BENCH, NOT FOR pcrec: `floor` / match / `auto`.** Its ×2.3 does not
reproduce; clang's absolute number matches the ledger and gcc's is twice what
this lane measures on a byte-identical artifact. It should be re-run before it
is cited again.
