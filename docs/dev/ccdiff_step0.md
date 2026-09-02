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
helpers, gated on the frameless stamp pcrec already computes, takes gcc to
clang's shape and past it — **0.611 on the frameless throughput cell against
clang's own 0.817** — is answer-identical over 3,204 comparisons, and leaves
both controls where gcc legitimately wins untouched (0.994 and 0.954).

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
it. The box was never quiet during this lane, so timing uses an interleaved
paired design rather than separated batches; it and the load conditions are
described with the numbers below.

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

### 1. `always_inline` on the emitted VM helpers, GATED ON FRAMELESS (twin V) — RECOMMENDED

**(a) Targets:** the frameless VM artifacts — where the entry's whole working
storage is dead and can be deleted. Corpus reach measured over all four bench
sets: 83 of 180 emitted artifacts have a VM entry chain, and **36 of 90
forced-VM artifacts (40 %) are frameless**. Lane vmfl0's independent census
puts the frameless shape at 35 % of the VM population under ordinary `auto`
selection too (`optvmfl_step0.md`), so this is not a `--engine=vm`-only
population.

**(b) Measured:** `dig-upto-16` thr/vm **0.611**, which BEATS clang's own
0.817 on that cell.

**(c) Effect on the controls: none, and this was the thing most at risk.**
`floor`/thr/vm — gcc's ×2 win — measures **0.994**: gcc's rotated
4-instruction attempt loop is untouched and the frame and canary go away, so
it is a strict improvement, not a trade. `level-context`'s prefilter body is
**byte-identical** before and after (0.954 measured).

**(d) Generality:** one emitter site, `src/gen/emit_vm.c`'s emitted function
headers. The attribute constrains only the compiler that was not already doing
this — clang inlines the same set on its own — so it moves gcc toward clang
rather than pinning either, and every twin compiles clean under both.

**Why the frameless gate, and why it is not a special case.** Two independent
facts force it to the same place. gcc *refuses* `always_inline` on a function
containing a computed goto — a hard error, not a warning — so the matcher can
only take it when the artifact pushes no resume frame. And the measurement
agrees: on the three FRAMED cells the spelling buys nothing (0.990, 0.954,
and `stack-frame` at **1.032**, a mild regression in 11 of 15 rounds), because
there the storage is genuinely live, so inlining deletes nothing and only
inflates the entry. The gate is the `has_push` predicate [CC-CLANG] already
evaluates to decide whether to emit the pop-and-resume dispatch at all — an
existing stamp, not a new condition.

The canary is worth naming to Frank on its own: pcrec is paying a
security-hardening tax on every search call for storage the artifact provably
never touches.

### 1b. REJECTED ALTERNATIVE: elide the buffers without inlining (twin W)

The obvious more-surgical spelling — drop the `rx_run_buffers storage`
declaration and bind NULL/0 when frameless, changing no inlining decision —
**does not work**: measured **0.986**, i.e. nothing. The canary survives,
because `rx_run_state`'s own `slot_values[]` array trips
`-fstack-protector-strong` exactly as the buffers do. Answer-identical, so it
is rejected on its measurement rather than its correctness. Recorded because
it is the first thing a reader will propose.

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

All numbers are **per-round paired ratios**: within one round every variant
runs back to back on the same subject, so a load excursion hits them together
and the statistic is the median of the ratios, not a ratio of medians. 11
rounds each (15 for the `stack-frame` confirmation). The full range is given
because the box was not quiet.

**LOAD CONDITIONS: 4.4–4.7 throughout** (lane opt5i's `make test` held the box
at 4.5–5.8 for the whole lane-day; it never dropped below 1.5, so the
low-load batch the brief asked for could not be taken). The interleaved
paired-ratio design is what makes these numbers usable anyway, and the
controls validate it: `floor`/thr/vm reproduces the ledger's 1.996 as
**1.993**, `stack-frame` its 0.680 as **0.718**, `level-context` its 1.693 as
**1.838**, `cls-upto-4` its 0.407 as **0.338**.

| cell | clang | twin | twin ratio (median) | range |
|---|---|---|---|---|
| `cls-upto-4` thr/auto | 0.338 | **A** (uniform tables) | **0.589** | 0.573–0.653 |
| `cls-upto-4` thr/auto | 0.338 | C (single-IV edge) | 0.849 | 0.809–0.928 |
| `cls-upto-4` thr/auto | 0.338 | A+C | 0.577 | 0.521–0.698 |
| `dig-upto-16` thr/vm (frameless) | 0.817 | **V** (always_inline) | **0.611** | 0.409–0.942 |
| `floor` thr/vm (frameless, CONTROL 1.996) | 1.993 | **V** | **0.994** | 0.727–1.054 |
| `nest3-16` thr/vm (framed, CONTROL) | 1.047 | V | 0.990 | 0.585–2.118 |
| `level-context` search/auto (framed, CONTROL 1.693) | 1.838 | V | 0.954 | 0.843–1.029 |
| `stack-frame` search/vm (framed) | 0.718 | V | **1.032** | 0.907–1.205, 11/15 rounds > 1 |

**Twin V beats clang outright on the frameless throughput cell** (0.611 against
clang's 0.817) and is neutral on the frameless control (0.994) — the control's
entry cost is amortised over 16,384 match attempts, so the entry improvements
correctly do not show there, and gcc's rotated attempt loop is untouched.

### Decomposition: where twin V's win comes from

`dig-upto-16` thr/vm, same paired design:

| variant | ratio | reading |
|---|---|---|
| `art-gcc` | 1.000 | baseline |
| `-fno-stack-protector` on the original | 0.889 | the canary alone is ~11 points |
| twin W (elide `rx_run_buffers` only) | 0.986 | **buys nothing on its own** |
| twin V (always_inline) | **0.611** | the inline, and the dead-code elimination it unlocks |

Twin W is the more surgical spelling — drop the `rx_run_buffers storage`
declaration and bind NULL/0 when frameless — and it **fails**: the canary
survives, because `rx_run_state`'s own `slot_values[]` array triggers
`-fstack-protector-strong` just as the buffers do. Only inlining, which makes
the entire run state dead, removes it. (Answer-identical, so it is rejected on
its measurement, not on correctness.)

### The gate: FRAMELESS ONLY

The three framed cells give 0.990, 0.954 and **1.032** — two neutral and one
mild regression, no measured benefit. On a framed artifact the storage is
genuinely live, so inlining `rx_search_run` deletes nothing and only inflates
the entry (`stack-frame` `rx_search` goes 40 -> 97 instructions for a regime
that calls it once per search). **So the attribute should ride the frameless
stamp and stop there** — which is also the only form gcc will accept on the
matcher, and the more conservative change.

### Compile gate

Every twin compiles clean under **both** gcc and clang at `-O2 -std=gnu11
-Wall -Wextra`. Frank's ruling that clang stays a compile-only gate with an
empty refusal set is unaffected.


---

## Worth chartering / not worth it

**WORTH CHARTERING: twin V, `always_inline` on the emitted VM helpers gated on
the frameless stamp.** Measured **0.611** on the frameless throughput cell,
which beats clang's own 0.817; **0.994** on the ×2 control, so nothing is
traded. It is one emitter site, it rides a stamp pcrec already computes, it is
answer-identical over 3,204 comparisons, and it addresses the ledger's general
signal rather than one cell. The stack-protector canary on provably-dead
storage is a finding in its own right.

**WORTH CHARTERING, second: twin A, uniform-table folding.** Measured
**0.589** on `cls-upto-4`. Narrower reach (24 % of `auto` artifacts) but a
large per-cell effect, and it is a general fact about a table the emitter
already has in hand.

**NOT WORTH IT: twin C (0.849, and gcc still will not unroll), twin W (0.986,
the canary survives), the pragma-unroll variant, applying twin V to FRAMED
artifacts (1.032 on `stack-frame`), and any `GENCFLAGS` flag.**

**CAVEAT ON THE NUMBERS.** The box never dropped below load 4.4 during this
lane, so every ratio above is an interleaved paired median with its full range
printed, not a quiet-box measurement. The design is validated by the controls
reproducing the ledger (`floor`/thr/vm 1.993 against 1.996; `stack-frame`
0.718 against 0.680), and the two recommended spellings' ranges do not cross
1.0. A quiet-box re-run before the implementing lane merges would still be
worth its cost.

**FOR THE BENCH, NOT FOR pcrec: `floor` / match / `auto`.** Its ×2.3 does not
reproduce; clang's absolute number matches the ledger and gcc's is twice what
this lane measures on a byte-identical artifact. It should be re-run before it
is cited again.
