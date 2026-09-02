# [OPT-VMFL] STEP 0 — MEASUREMENT: the census, the direct-branch-dispatcher
D77 trigger, and the stamp proposal (also [ENG-DIRECT]'s own STEP 0)

Lane `vmfl0`, 2026-09-02. Measurement only: **nothing under `src/`, `tests/`
or `docs/spec/` changed.** Filed here for the same reason
`opt5_step0_profile.md`/`opt3_dfa_scan_measurement.md` are — a measurement
memo, not a compiled-checkpoint critic panel.

**RULING R1 (manager → lane, from Frank, 2026-09-02 ~18:5x), applied
throughout**: `[OPT-VMFL]` is not a new idea — a VM program with no resume
frame is a DIRECT-CODED automaton by construction (program counter = state,
no state-transition table, no dispatch), which is `plan.md`'s
`[ENG-DIRECT]` row (line 880, filed 2026-08-18, STATE:not-started). This
memo is `[ENG-DIRECT]`'s own STEP 0 as well as `[OPT-VMFL]`'s: §3's
hand-twin is exactly the kind of evidence `[ENG-DIRECT]`'s own text asks
for ("`[BENCH-CEIL]` is this row's instrument... the address-taken-label
pinning largely disappears" under direct coding — §3.1's `jmp *` count
table is a small-scale, VM-side instance of that same claim, not the
DFA-side direct emission `[ENG-DIRECT]` itself proposes), and §4's stamp
proposal addresses Frank's 2026-08-18 ruling that a landed direct-coded
engine is a THIRD roster member (table-DFA / DIRECT-DFA / VM, not a
same-day DFA variant) by recommending, not deciding, which of the two
shapes the frameless fact should end up taking.

## 0. The answer in six lines

1. **`has_push` (the emitted text) and `RX_RESUME_FRAMES` (the pre-pass
   estimate) diverge on 198 of 2,603 VM-compiled artifacts (7.6 %), and the
   divergence runs in exactly ONE direction: `frames > 1` with NO push
   emitted (the estimate OVER-counted). Zero artifacts show the opposite
   divergence (`frames == 1` with a push emitted, the UNDER-count I-32
   flagged as the theoretically live direction). Every one of the 198 is a
   lookaround construct whose body has no internal choice point** (`(?=a)`,
   `(?<=abc)`, `(?*[ab])`, the verb-name spellings, and their nested/`\K`/
   `(?&name)` relatives) — `vm_cost`'s uniform "+1 frame" (lookahead) /
   "+`m`" (lookbehind, `m` branches) charge for the lookaround mechanism
   itself is a safe-direction over-charge, and it over-charges completely
   when the body is a single deterministic literal/class/empty match: the
   body emits no `RX_PUSH`, and the positive arm's mark/cut (`vm_atomic`'s
   shape) uses `RX_SET`, never `RX_PUSH`, so the whole lookaround pushes
   nothing. Zero divergent artifacts came from the bench's four sets —
   none of them contain lookaround patterns.
2. **`resume_frames == 1` does NOT equal `has_push == false` by
   construction** (I-32's own caveat, confirmed rather than merely
   repeated): the equality holds on 100 % of THIS census's population
   (1,090 of 1,090 `frames == 1` artifacts are frameless) only because the
   only divergence direction present here moves artifacts OUT of the
   `frames > 1` cell, never INTO the `frames == 1` cell from the dispatch
   side.
3. **The frameless shape reaches `auto`, not only `--engine=vm`-forced
   builds.** Of the 1,090 forced-VM artifacts that are genuinely frameless,
   recompiling the SAME patterns under `auto` sends 703 (64.5 %) to the DFA
   engine (no VM body exists, so the mechanism is moot there), but 290
   (26.6 %) land on a VM hybrid and 95 (8.7 %) on a plain auto-selected VM
   artifact — both carry the identical frameless VM body forced compilation
   showed. The `×9` mechanism is not confined to the forced-VM population
   the bench measured; roughly a third of the naturally-frameless
   population reaches it through ordinary `auto` selection too (for
   reasons other than frame count — a named group, a backreference, a
   capture that forces the VM `auto` would have chosen anyway).
4. **The direct-branch-dispatcher hand-twin is answer-identical on all
   three chosen artifacts and three subject regimes each (15/15 cells)**,
   but the timing verdict is **mixed, not a clean win**: `nest2-64` (128
   stamped frames, 24 distinct resume labels — by far the largest dispatch
   set of the three) measures **1.03-1.04× faster** on both the match and
   find-all regimes; `csv5` (5 frames, 4 labels) and `ctx-lazy-256` (7
   frames, 6 labels) measure **flat to slightly worse** — `ctx-lazy-256`'s
   fast-matching regime measures the twin **2.9 % SLOWER**. Read together
   with the mechanism (§4.3): the win, where it exists, tracks the SIZE of
   the resume-label set, and three data points is not enough to fit a
   curve to that — it is enough to say the effect is real but small and
   not uniform, nowhere near the ×9 the frameless (zero-dispatch) case
   measures.
5. **This is the finding the brief asked to be able to report: the D77
   trigger for building a real direct-branch dispatcher is NOT clearly
   met.** A `+1-4 %` win on one of three artifacts, with a `-3 %` result on
   another, is not the kind of number that justifies landing a codegen
   change with its own abi bump, identity-gate re-pin and regression
   corpus. What WOULD move this is a larger, more scan-loop-shaped
   population (§4.4 explains why `nest2-64`'s digit-run body sees more of
   the effect than `csv5`'s field-scan or `ctx-lazy-256`'s literal-chain
   bodies do) — named as the measurement to run before proposing STEP 1,
   not built here.
6. **The stamp is a straightforward (b)-family macro and needs no
   `rx_info` mirror today** (§5): `RX_VM_FRAMELESS`, `.c`-private,
   unconditional on every VM artifact (never absent, per the [OPT-1]
   precedent), read directly off `has_push` at the same site the fail
   label's own comment already branches on — one predicate, two readers,
   never re-derived.

## 1. Method

- Box: same one `opt5_step0_profile.md`/`opt3_dfa_scan_measurement.md`
  measured on (AMD Ryzen 5 1600, 12 cores). `perf` is unavailable here
  (`perf_event_paranoid=4`, scope mandate forbids lowering it) — this
  measurement does not need cycle counters, only wall-clock ns/call
  ratios, so that limitation does not bite the way it did for opt3/opt5.
- Worktree `worktrees/vmfl0`, built once (`make -j4`) at branch point
  `5496ca6`. `build/pcrec` used throughout.
- Load checked before every timed batch: 0.33-1.10 across the whole run
  (lane opt5i's concurrent `make test` runs are the box's other heavy
  occupant this session; no `.hold` file was ever set and no batch was
  deferred). Every timed run below is admitted.
- Every timing binary compiled `gcc -O2 -std=gnu11 -Wall -Wextra -Werror`
  directly (not through `tests/harness/run.sh`, whose default `GENCFLAGS`
  is `-O1`) — the same choice `opt5_step0_profile.md` §1 made and for the
  same reason: a timing measurement wants the same optimization level the
  bench's own `-O2` build uses, and the harness's `-O1` default is a
  compile-speed/warning-surface choice, not a performance one.
- Scratch: `/tmp/claude-1001/-home-duxevents-pcrec/dcce9a31-e3ae-41e3-8913-a4a918af3f32/scratchpad/vmfl0/`
  (census script + artifacts) and its `handtwin/` subdirectory (the STEP 0
  (b) driver sources, generated artifacts, timing logs) — session
  scratchpad, not committed, per the scope mandate.

## 2. Measurement (a): the `has_push` vs `RX_RESUME_FRAMES` census

**Population.** Every `pattern` line in `tests/**/*.rxt` (2,825 distinct
pattern texts after dedup) plus every `.rx` file in the bench's four sets
(`bounded` 43, `loglines` 11, `email` 3, `altwide` 20 — 77 total) = 2,902
items. Each compiled twice: `--engine=vm --features all` (forced VM, the
population this census tabulates) and `--engine=auto --features all` (to
read which engine/prefilter form `auto` actually picks for the same
pattern). `--features all` maximizes how much of the corpus compiles at
all — the census is about the VM emitter's fail-label shape, which is
orthogonal to which modules are enabled.

**Extraction.** For each `--engine=vm` artifact that compiled: `RX_RESUME_FRAMES`
read from the paired `.h` (`[DD-14.FB]` moved it there; a self-contained
`-o -` build has no `.h`, so every compile here used a real `-o FILE`), and
`has_push` read directly off the emitted `.c` text — the presence of the
literal substring `goto *run->resume_stack` (the fail label's dispatch,
verbatim from `emit_vm.c:9556`) versus the frameless comment's own marker
text, `NO RESUME FRAME AT ALL`. The two markers were checked for mutual
exclusivity on every compiled artifact (`marker_consistent`) and found
exclusive on all 2,603 — never both present, never both absent, so the
extraction is reading a real either/or rather than a substring that
happens to coincide.

**Results — the four cells:**

| cell | count | % of 2,603 | reading |
|---|---|---|---|
| `frames == 1` ∧ frameless | 1,090 | 41.9 % | the estimate is exact and minimal — the common case |
| `frames == 1` ∧ dispatch present | **0** | 0.0 % | the UNDER-count I-32 named as theoretically live (a resume point admitted despite the minimal stamp) — absent from this population |
| `frames > 1` ∧ frameless | 198 | 7.6 % | the OVER-count — every one a lookaround with a choice-point-free body (below) |
| `frames > 1` ∧ dispatch present | 1,315 | 50.5 % | frames stamped and a real dispatch exists — the expected/consistent majority |

`vm_compiled_ok = 2,603`, `vm_refused = 299` (patterns pcrec's parser or
VM pre-pass declines outright under `--features all --engine=vm` — a
`(bad` unparseable fragment, a few resource-cap refusals; not itself part
of this census). `inconsistent_marker_count = 0` (the sanity check above).

**Where the divergent 198 came from**, by group:

| group | frames>1∧frameless | frames>1∧dispatch | frames==1∧frameless |
|---|---|---|---|
| corpus | 198 | 1,286 | 1,054 |
| bench-bounded | 0 | 12 | 31 |
| bench-loglines | 0 | 8 | 3 |
| bench-email | 0 | 2 | 1 |
| bench-altwide | 0 | 7 | 1 |

Every divergent artifact is from the corpus. The bench's four sets contain
no lookaround construct at all (confirmed by `bench/*/CLAUDE.md`'s own
pattern-family descriptions, §1), which is exactly the population the
divergence is confined to — so the bench's own O-14 measurement never saw
this direction, and had no way to.

### 2.1 The mechanism, read off the artifacts directly (not asserted)

`(?=a)` — a positive lookahead over a single literal — and `(?<=abc)` — a
positive lookbehind over a fixed literal — both stamp `RX_RESUME_FRAMES 2`
(lookahead) / `3` (lookbehind, `m`-branch charge) and carry ZERO `RX_PUSH`
call sites in the emitted `.c`, verified directly:

```
$ build/pcrec --engine=vm --features all -o /tmp/la2.c -- '((?=a)z)'
$ grep -n 'RX_PUSH(\|NO RESUME FRAME AT ALL\|define RX_RESUME_FRAMES' /tmp/la2.c /tmp/la2.h
/tmp/la2.h:175:#define RX_RESUME_FRAMES 2
/tmp/la2.c:256:     * NO RESUME FRAME AT ALL (no RX_PUSH site, no linked
```

`emit_vm.c`'s own record of the mechanism (§ "the VM engine joins",
"THE POSITIVE ATOMIC ARM IS `vm_atomic` PLUS A SAVED CURSOR"): the mark
taken before the lookaround's body is a plain local (or `RX_SET`, the
TRAILED writer — never `RX_PUSH`), and the cut on the body's first success
discards frames rather than allocating one. If the body itself has no
choice point — a single literal, a single class, an empty match, a
disjoint single-character alternation like `[ab]` — the body ALSO emits no
`RX_PUSH`. So the entire construct pushes nothing, while `vm_cost`'s
pre-pass (documented at `emit_vm.c:1269` and the "vm_cost's +1 frame / +2
trail were RE-CHECKED against `vm_look`" note) charges the lookaround
mechanism a flat `+1`/`+m` **regardless of whether the body needs it** —
a safe-direction over-charge, by design, that this census shows firing to
completion (down to a fully-unused stamp) on exactly the choice-point-free
body population.

**All 198 patterns are exactly this family** — verified by classifying
every divergent pattern's leading construct:

| kind | count |
|---|---|
| positive lookahead `(?=` | 5 |
| positive lookbehind `(?<=` | 5 |
| non-atomic lookahead `(?*` | 5 |
| non-atomic lookbehind `(?<*` | 5 |
| verb-name lookaround (`(*pla:`, `(*naplb:`, …) | 12 |
| every other spelling — nested lookarounds, `\K`-bearing bodies, `(?(DEFINE)…)` callees, back-referenced bodies, negative lookahead/lookbehind (`(?!`, `(?<!`) combined with the same choice-point-free shape | 166 |

No non-lookaround construct appears anywhere in the 198. This is a clean,
single-mechanism population — not a grab-bag of unrelated over-estimates.

### 2.2 What this does NOT show, stated so it is not over-read

Zero `frames == 1 ∧ dispatch` artifacts in a 2,603-artifact corpus-plus-bench
census is evidence the under-count direction is rare or corpus-absent
**on this population**, not evidence it cannot happen — I-32's own
citation (`+105 B`, "benign since `ae3e6ca`") says it has been observed
before, elsewhere, on a population this corpus does not happen to
contain. The census answers "how often, and in which direction, on the
tree's own tests plus the bench's four sets" — it is not a proof that the
under-count direction is unreachable.

## 3. Measurement (b): the direct-branch dispatcher, hand-twinned

**Method.** Three `frames >= 2` artifacts from `bench/bounded/patterns/`,
compiled `--engine=vm --features all` (library form, no `--emit-main`, so a
custom driver links against `<prefix>_search` directly):

| artifact | pattern | `RX_RESUME_FRAMES` | distinct resume labels |
|---|---|---|---|
| `csv5` | `(?:[^,\n]{0,32},){4}[^,\n]{0,32}` | 5 | 4 (`rx_L8,13,18,23`) |
| `ctx-lazy-256` | `\b(?:fail\|abort\|panic)\b.{0,256}?\b(?:disk\|memory\|socket\|quota)\b` | 7 | 6 (`rx_L7,8,23,30,31,32`) |
| `nest2-64` | `(?:\d{1,64}){1,64}` | 128 | 24 (`rx_L6,9,14,...,74,77`) |

None of the three carry a subroutine call (`RX_CALL`), so every push in
each is a plain `RX_PUSH(&&rx_LN, …)` — confirmed by grep before writing
the transform, since a call frame's `resume_label` is the fail label
ITSELF (`emit_vm.c`'s DD-14 wave B+C note) and would need a different
case arm the transform below does not build.

**The transform** (`handtwin/make_twin.py`, applied to each artifact's
own `.c` — three lines of substitution, nothing re-emitted):

1. `rx_frame.resume_label`'s type: `const void *` → `int`.
2. Every `RX_PUSH(&&rx_LN, …)` call site's first argument: `&&rx_LN` → the
   bare integer `N` (the label's own numeric suffix, already unique per
   artifact).
3. The fail label's dispatch line,
   `goto *run->resume_stack[frame_index].resume_label;`, replaced by
   `switch (run->resume_stack[frame_index].resume_label) { case N: goto
   rx_LN; ... default: __builtin_unreachable(); }` over exactly the label
   set step 2 found in THIS artifact.

Nothing else in the artifact changes — this is a targeted substitution
over the artifact's own text, not a second emitter path. All three twins
compile clean under the same `-O2 -std=gnu11 -Wall -Wextra -Werror` the
originals do (no new warnings from the added `switch`/`default` arm).

**Answer identity.** A driver (`handtwin/correctness_driver.c`) runs each
artifact once per subject and prints span/nomatch/giveup; diffed textually
between the orig and twin binary on the subject sets below. **15/15
subject cells identical**, csv5 and ctx-lazy-256 against the bench's own
subjects (`f-csv-5`/`f-csv-4`/`l-03` for csv5; `l-00`..`l-07` for
ctx-lazy-256 — the full ctx family), nest2-64 against `d-01024.bin` (1,024
random digits) plus the two digit throughput subjects
(`t-digits-004k`/`016k.bin`).

**Timing.** Two regimes per artifact, 5 trials each (process-launch
median, not intra-process — the same discipline `opt5_step0_profile.md`
used, so page-fault/cache warmup is identical between orig and twin):
"match" (a fixed subject, `rx_search` called repeatedly with no advance —
the short-subject match loop) and "findall" (the bench's own find-all
advance rule, `pos = (end>pos) ? end : pos+1`, repeated over a subject —
the large-subject throughput loop). Findall subjects: `csv5_large.bin`
(csv5's own `f-csv-5` content tiled to 64 KB — generated, no bench
large-subject exists for this pattern), `ctx_large2.bin` (ctx-lazy-256's
`l-00`, the fast-matching subject, tiled to 8 KB — **not** `l-03` tiled:
that first attempt (worst-case "no context word anywhere" content tiled
to 64 KB) did not finish a single find-all pass in 120 s and was killed;
every position in a tiled `l-03` re-triggers the full 256-byte lazy-gap
walk, which is genuinely quadratic-shaped at that scale and was the wrong
instrument for a timing comparison, so the regime was re-targeted at a
realistic mostly-matching subject instead), and `t-digits-016k.bin` (the
bench's own real throughput subject, for `nest2-64`).

| artifact | regime | subject | orig median ns/call | twin median ns/call | twin/orig |
|---|---|---|---|---|---|
| csv5 | match | f-csv-5 (32 B, matches) | 47.462 | 47.878 | 1.009 (slower) |
| csv5 | findall | csv5_large (64 KB, tiled matches) | 59.987 | 60.359 | 1.006 (slower) |
| ctx-lazy-256 | match | l-00 (50 B, fast match) | 387.201 | 398.387 | **1.029 (slower)** |
| ctx-lazy-256 | match | l-03 (251 B, worst-case no-match) | 3964.448 | 3949.487 | 0.996 (flat) |
| ctx-lazy-256 | findall | ctx_large2 (8 KB, tiled fast matches) | 369.495 | 367.875 | 0.996 (flat) |
| nest2-64 | match | d-01024 (1,024 digits, matches) | 886.950 | 861.081 | **0.971 (faster)** |
| nest2-64 | findall | t-digits-016k (16 KB digits) | 4935.975 | 4728.167 | **0.958 (faster)** |

(Full 5-trial spreads in `handtwin/trials.log`/`trials2.log`; every
`min`/`max` pair is within 2 % of its own median, so the medians above are
not single-outlier artifacts.)

### 3.1 Reading the result: real, small, and not uniform

`nest2-64` — 128 stamped frames, 24 distinct resume labels, the largest
dispatch set of the three — is the only artifact where the twin wins
CONSISTENTLY, on both regimes, by **3-4 %**. `csv5` (4 labels) and
`ctx-lazy-256` (6 labels) are flat to worse; `ctx-lazy-256`'s fast-matching
regime is the one cell that is unambiguously slower under the twin
(**2.9 %**, outside every trial's spread on both sides).

**A partial mechanism read, from the object code, not asserted as the full
explanation:**

| artifact | orig `jmp *` count | twin `jmp *` count |
|---|---|---|
| csv5 (4 labels) | 2 | **0** — gcc compiled the 4-case switch as a compare chain |
| ctx-lazy-256 (6 labels) | 1 | 1 — gcc still emitted a jump table |
| nest2-64 (24 labels) | 2 | 1 |

Even where the twin's switch still lowers to a jump table (`ctx-lazy-256`,
one arm of `nest2-64`), that is a DIFFERENT thing to GCC's front-end CFG
builder than a computed goto over an arbitrary `void*`: I-31's own
mechanism argument is that a computed goto forces the CFG to admit the
indirect jump as a possible edge into EVERY address-taken label in the
function, which is a GIMPLE-level, early-lowering fact; a `switch`'s
jump-table lowering happens later (RTL expansion) over a bounded,
statically-known case set, and does not carry the same "any label" CFG
conservatism. That is consistent with the transform helping at all (all
three twins removed the artifact's only `&&label`-taking expressions, full
stop), but it does not by itself explain why `nest2-64` benefits and the
other two do not.

**The more likely discriminator, stated as a hypothesis this measurement
does not confirm or refute further**: `nest2-64`'s body — a bounded repeat
of a bounded digit-repeat — is dominated by REPLICATED SCAN LOOPS (the
kind `opt5_step0_profile.md` already showed the VM's own possessified span
loop takes, and the kind the frameless-VM ×9 witness is built from
entirely); `csv5`'s body is a class-scan-then-literal-comma chain and
`ctx-lazy-256`'s is a literal-byte-chain plus a lazy retry loop — neither
is dominated by a single tight scalar scan the way `nest2-64`'s replicated
digit runs are. If the CFG-inhibition mechanism's payoff scales with how
much of the function IS a tight address-only scan loop (exactly what the
frameless case's own ×9 showed), a body with less of that shape has less
to gain and more surface (the switch's own bounds-check/table-load
overhead) to lose it to. **This is a candidate explanation for the
direction of the three results, not a fourth measurement** — testing it
would mean hand-twinning a `frames >= 2` artifact whose body IS
scan-loop-dominated (a bounded class repeat that still needs one resume
frame for some outer reason) against one that is dispatch-dominated, which
is a STEP 1 question if STEP 1 is chartered at all.

### 3.2 The D77 verdict

**Not met.** A 3-4 % win on one of three artifacts, alongside a flat
result and a 2.9 % loss on the other two, is not the number that licenses
a codegen change carrying its own `abi` bump, an identity-gate re-pin
(D76/D94), and a new regression population — the exact cost D77 exists to
weigh against. The frameless case's own ×9 came from removing an ENTIRE
mechanism (dispatch, trail rewind, budget decrement — everything past the
`has_push`-gated return) from bodies where that mechanism's very presence
was inhibiting an otherwise-tight scan loop; the direct-branch dispatcher
removes only the FINAL jump's shape while every other part of the pop-and-
resume machinery stays, on bodies that are not scan-loop-dominated to
begin with. If a future measurement finds a `frames >= 2` population that
IS scan-loop-dominated and shows a bigger, more consistent number, THAT
is the trigger to revisit — named rather than built here, per D77.

## 4. Measurement (c): the stamp proposal (drafted, not landed)

### 4.1 Classification under §6.3's (a)/(b) split

`docs/spec/match_api.md` §6.3 ([DD-13], [DD-13c]) splits the D46 macro
family: **(a) SELECTION FACTS**, unconditional on every artifact,
answering "which mechanism did this artifact's COMPILATION choose" (engine,
scan form, table encoding); **(b) CAPACITY/ACTIVITY macros**, VM-only,
answering "what did the VM's EMITTED PROGRAM turn out to contain" (rungs,
strategies, prune clamps, call linkage, fast-tier capacities).

The frameless property is (b), not (a), for the same reason
`RX_VM_CALL_SPLICED`/`RX_VM_CALL_LINKED` are (b) rather than a selection
fact: it is not a decision the compiler MADE before emitting (there is no
"frameless mode" flag anywhere upstream of `emit_vm.c` — `has_push` is
read off `v.emitted_push`, set by `vm_push_at`, "the ONE primitive that
writes a push, in EITHER tracing spelling", DISCOVERED BY EMITTING, the
same discipline `Job.enc_mask` and the cursor local already follow). It
answers "did the emitted program end up containing any resume mechanism at
all" — an activity fact about the artifact's own text, exactly the
question `RX_VM_RUNGS`/`_STRATS`/`_PRUNES`/`_CALL_SPLICED`/`_LINKED`
already answer for their own mechanisms. A DFA artifact has no resume
stack at all, so the macro is VM-only by the same argument that keeps the
whole (b) family VM-only.

### 4.2 The proposed macro

```c
#define RX_VM_FRAMELESS 1   /* or 0 */
```

- **Placement**: `.c`-private, in the same block as `RX_VM_RUNGS`/
  `_STRATS`/`_PRUNES`/`_PRUNE_CEILING` (the (b) capacity/activity block
  `emit_vm.c` already writes immediately after the shared prologue) —
  not in the `.h`, on the same reasoning §6.3 already states for that
  whole family ("the observability macros of §6.3 are emitted into the
  `.c` only, never into the `.h`" — a caller does not need this fact in
  order to CALL the artifact, only a diagnostic reader does).
- **Unconditional on every VM artifact, never absent** — the [OPT-1]
  precedent for `RX_FAST_FRAMES`/`_FAST_TRAIL`: "a fact readable by a
  macro's ABSENCE is the discriminator [DD-13] had to go back and remove
  from two checks." `RX_VM_FRAMELESS 0` on a pushing artifact,
  `RX_VM_FRAMELESS 1` on a frameless one — both spelled, never one
  omitted.
- **Read off `has_push` at its own definition site** (`emit_vm.c`, right
  where `const bool has_push = v.emitted_push || v.has_linked_calls;` is
  computed, immediately before the fail-label `sb_printf` that already
  branches on it) — the SAME predicate the dispatch omission itself uses,
  never a second derivation. `RX_VM_FRAMELESS` is the literal boolean
  `!has_push`, not a re-reading of the emitted comment text or a strstr
  over the artifact (the two failure modes the `[CC-CLANG fix,
  2026-09-01]` note in `emit_vm.c` already records and rejected for the
  dispatch gate itself — the same argument applies to a stamp reading the
  same fact).
- **No `rx_info` mirror**, on the `RX_DFA_TABLE`/`_VM_PREFILTER_LANG`
  precedent exactly: "It has no `rx_info` mirror, deliberately... a third
  unread mirror would be built ahead of a measured need (D77)." No
  existing consumer reads `rx_info` at run time to bucket on this fact
  today — the bench's own O-14/I-32 exchange READ THE ARTIFACT TEXT
  directly (the `NO RESUME FRAME AT ALL` comment, `goto *`'s presence),
  which is exactly the mirror-avoidance precedent's own point: a
  diagnostic reader can already answer this question from the `.c`, so a
  struct field is not owed until a caller needs the fact at RUN time
  rather than at BUILD/DIAGNOSTIC time. The append-if-needed trigger is
  the same one `RX_DFA_TABLE`'s entry names: "the first consumer that
  reads `rx_info.scan` or `rx_info.prefilter` at run time" already made
  `table` owed; an analogous first RUN-TIME consumer of the frameless fact
  would make this one owed too, at that point, as a struct append moving
  no existing offset (`abi` bump, D76 ritual).

### 4.3 R1: a stamp on the VM route, or a preview of a third engine value — RECOMMENDATION, not a decision

Frank's 2026-08-18 ruling (recorded on `[ENG-DIRECT]`, `plan.md:920-925`)
is that a landed direct-coded engine is a THIRD roster member — `table-DFA`
/ `DIRECT-DFA` / `VM` — joining the ENGINE SELECTION axis itself
(`select_engine` picks per pattern, `ENGM_*` gains a member, `RX_ENGINE`
stamps a third value), not a same-day variant folded into an existing
macro's value set. `RX_VM_FRAMELESS` is proposed under TODAY's two-engine
roster, where it is unambiguous: `has_push` is a fact about the VM
emitter's own output, so the macro is VM-route-only by construction and
absent from every DFA artifact, exactly like every other (b) macro.

**What is worth naming for whoever charters `[ENG-DIRECT]`'s build,
without deciding it here**: the frameless population this census measures
(§2 — 1,090 corpus+bench patterns compile to a VM body with zero
`RX_PUSH` sites, PLUS the 198 lookaround artifacts whose stamped frame
count over-counts a body that is ALSO push-free once the lookaround's own
charge is set aside) is *by definition* exactly the population
`[ENG-DIRECT]`'s own text describes as its target — "the program counter
IS the state... no dispatch" is precisely what a frameless VM body already
is, minus the resume-stack scaffolding around it that a true direct-coded
emission would never allocate in the first place. Two shapes are live
candidates once `[ENG-DIRECT]` is chartered for real, and this memo takes
neither position:

1. **`RX_VM_FRAMELESS` ships now, as proposed, and is later read as one of
   `[ENG-DIRECT]`'s own sizing inputs** — a VM artifact stamping
   `RX_VM_FRAMELESS 1` is a candidate for re-routing to `DIRECT-DFA`
   entirely (or for the VM to carry it as a direct-coded ISLAND, the
   `[ENG-ISL]` cross-link `[ENG-DIRECT]`'s own row already names), and the
   macro's population becomes a measured worklist rather than a fresh
   census `[ENG-DIRECT]`'s own STEP 0 would otherwise have to re-run.
2. **The frameless fact is subsumed by `RX_ENGINE`'s own third value**
   once `DIRECT-DFA` exists, and `RX_VM_FRAMELESS` is retired or narrowed
   to describe only the VM bodies that STILL end up on the VM route after
   `[ENG-DIRECT]`'s own selection axis has first pulled every eligible
   frameless region onto `DIRECT-DFA` — in which case a VM artifact
   stamping `RX_VM_FRAMELESS 1` post-`[ENG-DIRECT]` would name a residual
   case the selection axis declined (irreducible automaton shape, code-size
   cap, or similar), a materially different population from today's.

Both are legitimate; which one is right depends on decisions
`[ENG-DIRECT]`'s own charter has not made yet (whether it subsumes whole
patterns or islands first, D46's stamp+force obligations "as a new
selection axis when built" per that row's own text). Recommending one over
the other is `[ENG-DIRECT]`'s STEP 1 or 2 question, not this STEP 0's.

### 4.4 Why not a bitmask like `_VM_RUNGS`/`_STRATS`/`_PRUNES`

Those three are masks because the rung/strategy/clamp decision is made
PER `A_REP` NODE and a scalar would lie on a mixed artifact
([M4.5e]'s own corrected-design lesson). `has_push` is a WHOLE-ARTIFACT
fact — "did ANY site in this program emit a push" — with no per-quantifier
axis to mix; it is already the same shape `<PREFIX>_VM_PREFILTER` and the
`abi`-15 `name`/`nentries` pair take (one verdict for the whole artifact),
so a scalar boolean is the honest shape, not an economy.

## 5. Reproduction

```
build/pcrec --engine=vm --features all -o /tmp/x.c -- 'PATTERN'
grep -n 'RX_PUSH(\|NO RESUME FRAME AT ALL\|define RX_RESUME_FRAMES' /tmp/x.c /tmp/x.h
```

Census script (`census.py`), hand-twin transform (`make_twin.py`), timing
drivers and raw trial logs are under
`/tmp/claude-1001/-home-duxevents-pcrec/dcce9a31-e3ae-41e3-8913-a4a918af3f32/scratchpad/vmfl0/`
(session scratchpad, not committed, per the scope mandate). Full
per-pattern divergence list: `census_result.json` in that directory.
