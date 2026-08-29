# [OPT-4] — the count-independent hybrid prefilter

STATUS: STEP 3 complete (2026-08-29, lane opt4b). §§1-6 are the design as
built; §7's costs and §8's predictions are now MEASURED on the landed tree and
say so. Numbers in §1's STEP 0 table are the original readings, taken on
lane/opt4 at 6bb0e28 (`--engine=auto --features all`, gcc 15 `-O2`, this box),
and are kept as the record of what the row was chartered on — §8 carries the
before/after taken today, against `-fno-prefilter-collapse` rather than against
that table, for the reason stated there. K39 is the defect; K41 witness 2 is
the pinned exemplar and now COMPILES under the default caps.

## 0. The answer in nine lines

The hybrid's prefilter is a FILTER, and a filter's contract is soundness of
REJECTION, not exactness. `src/ir/nfa.c` already exploits that twice — atomic
groups lower transparently and lookarounds lower to epsilon, so the prefilter
already answers for a strict SUPERSET on those patterns, with the consequences
written down and measured (H1/H2/H3, §2). A counted repeat is a third member of
that family: lowering `X{m,n}` as `X{min(m,1),}` for the prefilter is a
superset, is count-independent, and inherits the whole existing argument. It is
selected per artifact when the exact lowering's NFA exceeds a budget, stamped,
and deniable. It costs 23 of 2,878 corpus artifacts their exact prefilter, and
it makes K41 witness 2 compile under the default caps.

## 1. The measured need

**Where the count enters.** `src/core/compile.c:860-875` builds ONE forward +
reverse DFA pair from `pcrec_build_nfa(cx, root, ...)` and hands it to both
roles: the DFA engine's own machine, and — when the VM is chosen under `auto`
— the hybrid's prefilter. The count enters at `src/ir/nfa.c:686` (`case
A_REP`): `rmin` body copies plus an `rmax - rmin` nested-optional chain. NFA
states are linear in the count; the DFA follows.

**Which machine carries it is shape-dependent**, and K39's one-line diagnosis
undercounts it. For `((a)|b){0,400}c` the `Sigma*` wrap absorbs the bound
(any `c` is accepted with zero repetitions), so the FORWARD machine is 2 states
and only the REVERSE carries the count at 402. Put a literal in front —
`foo((a)|b){0,1000}bar` — and the wrap can no longer absorb it: forward 3,006
states AND reverse 1,007. A fix confined to one direction would miss half the
population, which is why this one acts on the LOWERING, upstream of both.

**STEP 0, before.** Code bytes are comment-excluded (`tests/lib/size_count.sh`).

| shape | fwd/rev DFA states | NFA | code B | .o B | gcc s | `-fno-prefilter` code B |
|---|---|---|---|---|---|---|
| `((a)|b){0,400}c` | 2 / 402 | 2,405 | 45,303 | 12,832 | 0.14 | 22,203 |
| `((a)|b){0,4000}c` | 2 / 4,002 | 24,005 | 199,511 | 56,032 | 0.16 | 22,205 |
| `([ab]{0,500})c` | 1 / 502 | 1,504 | 41,532 | 11,888 | 0.11 | 19,086 |
| `((ab|cd){0,300})x` | 2 / 902 | 2,704 | 87,377 | 24,280 | 0.14 | 22,490 |
| `((a{1,20}){1,50})z` | 3 / 1,002 | 2,004 | 71,840 | 22,144 | 0.26 | 33,388 |
| `foo((a)|b){0,1000}bar` | 3,006 / 1,007 | 6,011 | 238,568 | 80,504 | 0.18 | 23,152 |
| `((ab){300})z` | 602 / 602 | 1,804 | 70,433 | 22,136 | 0.12 | 19,392 |
| `((a)|ab){4000}c` (corpus max) | 8,002 / 8,002 | 24,005 | 651,694 | 202,912 | 0.30 | 29,144 |
| K41 witness 2 | 3,108 (ENG_ATTEMPT) | — | REFUSED, 670,932 > 500,000 | — | — | 146,212 |
| K41 witness 2, caps raised | same | — | 1,220,889 | 1,576,104 | **49.25** | — |

The VM body is count-independent as [ENG-BREP] claims — 22,203 against 22,205
at 400 and 4,000. Everything above it is the prefilter.

**The population, counted (learnings §3 / K35).** Joining
`docs/dev/artifact_size_log.tsv`'s 2,878 rows to the `pattern` line each row's
file:line names: 1,388 carry `prefilter=hybrid`, 1,185 are DFA artifacts with
no VM prefilter decision at all, 305 are `none`. Of the 1,388, **244 (17.6 %)
carry a counted repeat with replication factor >= 2** — 9,652,482 of 39,309,904
hybrid source bytes and 57.12 of 273.32 s of hybrid gcc CPU. Measuring each
artifact's prefilter share directly (`code(auto) - code(auto -fno-prefilter)`,
all 1,388 compiled): prefilters are 10,876,197 bytes in total, of which the 244
hold 3,661,398 — and the top FOUR patterns hold 1,603,622 of that.

**The bench's 14 patterns (read-only).** THIRTEEN select `RX_ENGINE "dfa"` and
have no VM prefilter at all, so they are untouched by construction. The
fourteenth is `level-context`, which today reads `RX_ENGINE_WHY "dfa
overflowed: >32000 states"` / `RX_VM_PREFILTER "none"` — [SEL-1]'s fallback.
Its count-collapsed language determinizes to **319 states**.

## 2. Why a superset prefilter is sound — the argument already exists

`src/gen/emit_vm.c:7546` carries it as ONE predicate read at three sites:

    v.mrl_win = job->fit.prefilter && !pcrec_has_atomic(root)
                                   && !pcrec_has_lookaround(root);

with the invariants stated beside it and measured:

- **H1 — REJECTION is sound.** `L(P) SUBSET L'` means no `L'` match implies no
  `P` match, so `if (prefilter(...) != 1) return 0;` keeps answering — the
  guard `engine_m4.md` §4.7 puts on a measured cliff (bench case (e), 25.4
  GB/subject) is preserved in full.
- **H2 — the span START stays a LOWER BOUND.** `emit_vm.c:9498` seeds
  `attempt_position = window[0][0]`; on failure the loop does
  `attempt_position++` and re-runs the `retry_win` recompute, re-asking the
  prefilter from the new position. So the VM VERIFIES every candidate the
  filter offers — confirmed at the emission site, not assumed.
- **H3 — the span END is NOT an upper bound**, because the forward machine is a
  PRIORITY DFA reporting the leftmost-FIRST end and a superset can prefer a
  shorter alternative: `(?>a|ab)c|abcd` on "abcd" is (0,4), its uncut twin ends
  at 3. Measured at 122 refuting cells for atomic, 8 of 45 for lookaround. So
  `mrl_win` goes off and `RX_VM_PRUNE_CEILING` reads `subject-end`.

A count-collapse is the same shape, so it needs ONE MORE CONJUNCT on that
existing predicate and no new mechanism. That is the whole of §5's emitter work.

## 3. The collapse, and its soundness in one line

**The rule.** For the prefilter's lowering only, an `A_REP` with `rmin > 1` or
`rmax > 1` lowers as `rmin' = (rmin ? 1 : 0)`, `rmax' = -1`. An `A_REP` already
satisfying `rmin <= 1 && rmax <= 1` is untouched (it replicates nothing, so
there is nothing to buy).

**Soundness.** Every word of `X{m,n}` is `k` concatenated copies of `X` with
`m <= k <= n`. If `m = 0` then `k >= 0 = rmin'`; if `m >= 1` then
`k >= m >= 1 = rmin'`. And `k <= infinity`. So `L(X{m,n}) SUBSET
L(X{rmin',})`, at every position, for every `X`. QED — and the proof does not
mention `n`, which is exactly why the result is count-independent.

**Count-independence.** The collapsed `A_REP` emits at most one body copy plus
a star split, so the NFA is a function of the pattern's STRUCTURE alone and the
DFA that follows is too. Measured over seven shapes: the collapsed prefilter
costs **6,798 – 7,447 bytes, flat**, against 23,100 (`{0,400}`), 177,306
(`{0,4000}`), 215,416 (`foo…{0,1000}bar`) and 622,550 (`((a)|ab){4000}c`).

**It covers the whole family by construction**, which is the D75-addendum test:
`{m,n}`, `{n}`, `{m,}`, nested bounds and lazy bounds are all one `A_REP` arm;
a possessive bound is `A_ATOMIC(A_REP(X))` and the atomic wrapper is already
erased by the arm above it. There is no `{0,n}` special case anywhere.

## 4. The selection — WHEN, and the number

Collapsing unconditionally was considered and REFUSED on the measurement. The
exact prefilter is a strictly better filter, and the corpus says most counted
repeats do not need collapsing: of the 244, **203 have an exact NFA under 64
states** and 96 have an exact prefilter SMALLER than a collapsed one would be
(they would GROW by 71,428 bytes in total). Collapsing all 244 would also
strip `prefilter-window` from all 244 (§2 H3) for a size win 96 of them do not
get.

So the collapse is a candidate with an `applies()`, in the [ENG-FORM]/D82
shape. **The prefilter language axis, in preference order:**

| order | candidate | applies |
|---|---|---|
| 1 | `exact` | the machines serve the DFA ENGINE, or no collapsible `A_REP` exists, or the exact NFA is within `PCREC_PREFILTER_EXACT_NFA_STATES` |
| 2 | `count-collapsed` | always (fallback) |

**The budget is measured, not picked.** Over the 1,388 hybrid artifacts, the
exact NFA state count separates cleanly:

| | n | min | median | p90 | p99 | max |
|---|---|---|---|---|---|---|
| replication factor < 2 | 1,144 | 3 | 6 | 10 | 15 | **20** |
| replication factor >= 2 | 244 | 5 | 19 | 107 | 16,005 | 24,005 |

The entire population with nothing to collapse tops out at 20 states, so no
budget in the plausible range can touch it. **`PCREC_PREFILTER_EXACT_NFA_STATES
= 128`** sits above all of that and above the counted population's own p90 of
107, so the rule fires only where the COUNT is what made the machine big:

| budget | artifacts over it | of which factor < 2 |
|---|---|---|
| 64 | 41 | 0 |
| 96 | 25 | 0 |
| 112 | 24 | 0 |
| 120 | 23 | 0 |
| **128** | **23** | **0** |
| 144 | 23 | 0 |
| 160 | 23 | 0 |
| 192 | 22 | 0 |
| 256 | 22 | 0 |
| 512 | 14 | 0 |

**THE VALUE SITS ON A PLATEAU, and that is the reason to trust it rather than
the number itself.** The over-budget count is FLAT at 23 for every budget in
**117..160** — a 44-wide interval with 128 near its middle — so the choice is
not balanced on a threshold that one added corpus pattern would tip. The
plateau's edges are where they are because the 18 counted-repeat artifacts
between 64 and 128 all sit at or below 116 (65, 65, 65, 65, 69, 73, 77, 77, 77,
80, 81, 81, 85, 89, 90, 90, 107, 116) and the next one up is at 161: the gap
from 116 to 161 IS the plateau. And the `of which factor < 2` column is zero at
every budget swept, not only at the chosen one, which is the stronger form of
§4's claim — no budget in the plausible range can touch the population with
nothing to collapse, so the rule is about counts and not about size.

At 128 the largest exact-language artifact has a 116-state exact NFA and the
smallest collapsed one has 161. In reverse-DFA terms the largest factor->= 2
artifact still using the exact language determinizes to 42 states, while the
collapsed ones run from 1 to 8,002 — the low end being four degenerate
`(?:…(){2,3}…)` patterns whose NFAs are large and whose DFAs are trivial, for
which the collapse buys almost nothing in bytes and still costs the pruning
ceiling. They are inside the 23 and are not special-cased; §7's costs are
theirs too. **23 of 2,878 corpus artifacts change; 2,855 are byte-identical.**

**THE PIN.** This table is a measurement and would otherwise rot on the next
corpus change, so the claim it supports is asserted in the suite:
`tests/codegen/run_prefilter_collapse.sh` §5 prints the census
(hybrid / collapsed / exact, and the split by TEXTUAL replication factor) and
asserts (a) zero collapsed artifacts with factor < 2, with its own
non-vacuity control, and (b) the collapsed population inside a pinned band.
That check's population is NOT this table's and its number is 20, not 23: this
table counts rows of `docs/dev/artifact_size_log.tsv` (23 rows, 19 distinct
patterns), while §5 sweeps every `pattern` line under `tests/` and sees one
pattern the log has no row for. Both are right; neither number is copied into
the other's check.

**The measurement is taken, not modelled.** The exact NFA is built first and
`nfa.n` is read off it — no second size model to drift from `compile_ast`
(D24). The wasted work is one NFA build on the 23, bounded by
`PCREC_MAX_NFA_STATES` and cheap since K7; determinization, the expensive step,
never runs on the discarded machine.

**This is a BOUNDED size, not a literally constant one, and the note says so.**
Below the knee an artifact keeps its exact prefilter and its size still moves
with the count — but it is small there by the same measurement that set the
knee. Above it the size is flat. K39's own check (`{0,400}` against
`{0,4000}`, delta <= 2 lines) passes because both are above the knee at 2,405
and 24,005 NFA states. `-fprefilter-collapse` reaches the literal form.

## 5. Where it lives

- **`src/ir/nfa.c`** — `NB` gains a `collapse` bool and `case A_REP` reads
  `rmin`/`rmax` through it. ONE site, in the arm that owns the lowering.
  `pcrec_build_nfa` gains the parameter.
- **`src/core/compile.c`** — at the existing build gate: build the exact
  forward NFA; if `fit.chosen != ENGM_DFA && fit.prefilter` and a collapsible
  `A_REP` exists and `nfa.n > PCREC_PREFILTER_EXACT_NFA_STATES`, reset `nfa.n`
  and rebuild collapsed, recording `job->fit.prefilter_collapsed`. The reverse
  build takes the same flag. Nothing downstream changes shape.
- **`src/opt/select_engine.c`** — `pcrec_has_collapsible_rep(root)`, beside
  `pcrec_has_bref`/`pcrec_has_linked_call`.
- **`src/gen/emit_vm.c`** — the third conjunct on `v.mrl_win`; the stamp; the
  `--emit-ir` `; prefilter` line names the language.
- **NOT in `src/gen/emit_dfa.c`.** The emitter sees a smaller table and nothing
  else. `RX_DFA_TABLE`/`RX_DFA_PREFILTER` keep choosing exactly as they do
  today (D82: a new representation is an object, and this is not one).

**The stamp** (D81, one derivation two readers): `RX_VM_PREFILTER_LANG`,
`"exact"` or `"count-collapsed"`, emitted on VM artifacts beside
`RX_VM_PREFILTER`. **And `RX_VM_PREFILTER_LANG_WHY` beside it** (D81's `_WHY`
convention, `_UNROLL_K_WHY`'s shape): FIVE values, not the three the axis's two
outcomes suggest, because `"exact"` is reached three ways a caller would act on
differently — `"exact nfa N > B"`, `"forced"`, `"exact nfa N <= B"`,
`"no counted repeat"`, `"denied"`. The count is the MEASUREMENT the decision was
taken on and `B` is printed from the budget symbol, so the stamp shows how close
an artifact sits to the knee without a rebuild. Both come off `EngineFit`,
written once at `compile.c`'s gate; `prefilter_lang_why >= PFLW_FORCED` iff
`prefilter_collapsed`, structurally (the ladder branches on the decision rather
than re-walking its conjuncts), so the two lines cannot disagree. **The deny flag**: `PCREC_NO_PREFILTER_COLLAPSE = 1u << 19`
(18 is [ART-SIZE]'s last), `-fno-prefilter-collapse`, a filter on the candidate
list that recovers today's artifact byte-for-byte. **The force flag**:
`PCREC_FORCE_PREFILTER_COLLAPSE = 1u << 20`, `-fprefilter-collapse` — it drops
the budget conjunct, which is what makes literal count-independence reachable
and gives `make test-axes` its deny/force pair on this axis.

**Emitted scaffolding moves** (the stamp), so this is D76's ritual in one
change: abi 11 -> 12 at all FOUR sites — `src/gen/emit_dfa.c`'s `.abi`,
`tests/codegen/run_codegen_tests.sh`'s [DD-14.FB] §10.4 expectation,
`docs/spec/match_api.md` §6's "abi is N" sentence, and
`tests/codegen/run_recursion_identity.sh`'s (B) pin. (STEP 3 correction: this
paragraph originally named `tests/fuzz/run_capturediff_gate.sh` for the fourth
site. That file carries no abi pin at all — it carries the fixed-seed
POPULATION pins, which this row also moves, for a different reason and by a
different mechanism. Both are updated; they are two obligations, not one.)

## 6. Interactions

**[SEL-1]'s overflow fallback.** Today the retry drops the prefilter, on the
stated ground that rebuilding the IDENTICAL machine would overflow again. A
collapsed language is not that machine, so the premise stops holding: the retry
has a different, smaller candidate to try. `level-context` is the measured
case — 319 states against a 32,000 cap. This needs one more rung on
`compile_driver`'s attempt ladder (`dfa_disabled` -> `dfa_disabled +
prefilter_disabled`), so it is a **SEPARABLE SECOND COMMIT** built only after
the size fix is green, and only if the manager wants it: it is a speed change
on one bench row, not part of K39.

**BUILT, STEP 3's second commit, and MEASURED.** The rung is one more attempt
in the SAME retry loop around the SAME single `setjmp` — `dfa_disabled +
prefilter_collapse_retry` first, then today's `dfa_disabled` alone if the
COLLAPSED machine overflows too. Each rung is offered at most once, so the
fallback is bounded at two extra builds however many caps a pattern overflows,
and `-fno-prefilter-collapse` skips the new rung entirely (a caller who denied
the axis is not given it by the back door — verified: the witness still stamps
`RX_VM_PREFILTER "none"` under the flag).

`level-context` before and after, `--features all`, find-all over the bench's
own throughput subjects, match counts identical in every cell:

| subject | before (no prefilter) | after (collapsed hybrid) | |
|---|---|---|---|
| `t-1024k-hit` | 10.75 ns/B | **4.56** | 2.36x |
| `t-1024k-fail` | 11.13 | **3.30** | 3.37x |
| `t-1024k-syslog` | 9.76 | **3.87** | 2.52x |
| `t-256k-hit` | 15.90 | **6.69** | 2.38x |

Confirmed against this box's noise by five interleaved rounds on
`t-1024k-fail`: after 2.80-4.49, before 9.82-11.40 — the bands do not overlap
(§8's warning about three-iteration readings applies, and this is what
clearing it looks like).

**THE COST IS SIZE, and it is the opposite sign to the rest of this row.**
`level-context`'s artifact goes from 22,907 to 69,360 code bytes in the split
`.c`+`.h` form (`artifact_size_term.md` §4.3a records the 22,905 that number
continues), or 29,217 to 75,670 in the self-contained `-o -` form the bench
probe measures — same event, two conventions, and the note gives both because
the two documents quote different ones. It is a 3.0x artifact for a 2.4-3.4x
throughput win, and the ONLY place in [OPT-4] where an artifact grows.
Recorded plainly rather than netted against the corpus's -1,874,322: they are
different trades on different patterns.

**COMPILE TIME DOES NOT MOVE**, which is the part the cost bound's arithmetic
would not tell you: 0.512 s against 0.509 s per compile (mean of five). The
bound goes from one refused DFA build to two, but the second build is the
COLLAPSED machine — 462 NFA states determinizing to 319 — next to an exact
build that overflowed at more than 32,000. The extra rung is free on the case
it exists for.

**The stamps say which rung won.** `RX_ENGINE_WHY` still reads
`"dfa overflowed: >32000 states at pattern offset 0"` — the engine choice's
reason is unchanged — beside `RX_VM_PREFILTER "hybrid"`,
`RX_VM_PREFILTER_LANG "count-collapsed"` and a `_LANG_WHY` of
`"dfa overflow retry, exact nfa 462"`, which is its own value precisely so a
reader can tell an artifact that GAINED a prefilter from one that merely
shrank. `run_prefilter_collapse.sh` §6 asserts all three, with the deny flag's
`"none"` as its non-vacuity control.

**The [ART-SIZE] ladder (D84).** Independent by construction, and the reason is
one sentence: the ladder chooses `K` for the VM's counter-rung body
replication, and this changes only the DFA the prefilter is built from. They
compose in one direction — a smaller prefilter lowers the byte total the
ladder's cap sees, so the term declines to act more often and `K` moves toward
the default. It never moves the other way.

**The caps.** K41 witness 2's collapsed prefilter measures 12,389 bytes against
524,720 today, so the predicted artifact is ~158,601 code bytes against a
500,000 limit. D84's revisit clause looks satisfiable; STEP 2 re-derives it
from a gate RUN, never from this arithmetic.

## 7. What this COSTS — predicted before building (D77), MEASURED in STEP 3

Both costs fall only on the 23 artifacts that collapse, and both are what
`-fno-prefilter-collapse` exists to recover.

1. **More candidate starts.** The exact reverse machine seeds the VM at the
   true leftmost start; the collapsed one seeds a lower bound and the retry
   loop walks forward, re-asking the prefilter per attempt. Named worst case:
   `((a)|b){0,400}c` on 100,000 `a` then `c` — exact seeds attempt 99,600,
   collapsed seeds 0. PREDICTION: quadratic where the exact prefilter is
   linear; STEP 3 measures it and reports the number honestly.

   **MEASURED, and it is worse than the sentence above reads.** 9.241166 s and
   **99,601 VM attempts** collapsed, against 0.000011 s and **one attempt**
   exact — the same answer both ways (start 99,600, end 100,001). That is a
   factor of ~840,000 in wall time on the named case. Two real corpus
   artifacts show the same cost at everyday scale: `(ab){300}` find-all over
   64 KB of `ab` runs 44× slower (246 against 109 attempts per search), and
   over a 66 KB subject that never matches it runs 14.5× slower because the
   exact prefilter rejects the whole subject **without one VM attempt** while
   the collapsed one hands the VM every position. Both of those artifacts read
   `RX_VM_PRUNE_CEILING "none"` under either language, so they isolate this
   cost from cost 2 below.

2. **The lost pruning ceiling.** §2 H3 forces `mrl_win` off. A second,
   independent match-time cost — and why the budget exists: 221 of the 244
   counted-repeat artifacts keep their ceiling.

   **MEASURED, ISOLATED.** `((a)|ab){0,100}c` find-all over a 64 KB matching
   subject takes 0.028 s collapsed against 0.019 s exact at an **identical
   1,300 attempts per iteration**, so the whole 1.49× is the ceiling and none
   of it is candidate starts. It is the smaller of the two costs by a wide
   margin.

3. **AND A CREDIT THE PREDICTION MISSED.** On a subject the prefilter rejects
   outright, the collapsed artifact is FASTER — `((a)|ab){0,100}c` over 64 KB
   of `a` with no `c`: 0.000006 s collapsed against 0.000016 s exact, both at
   zero VM attempts, because the smaller DFA scans the subject quicker. §7 was
   written as two costs and no benefits; the trade is not one-directional, and
   a caller whose traffic is mostly non-matching may prefer the default even
   where a matching subject would favour the exact machine. Recorded here
   rather than quietly folded into the win, because a prediction that was
   incomplete in the favourable direction is still a prediction that was
   incomplete.

## 8. Predictions, CHECKED in STEP 3

STATUS: measured 2026-08-29 on the landed tree, gcc 15 `-O2`, this box. Every
prediction held or was beaten; none was revised after the fact. "before" is the
same compiler under `-fno-prefilter-collapse`, which is the honest control — the
STEP 0 column was taken at 6bb0e28 and has since drifted by unrelated
scaffolding (the abi 11 -> 12 stamps among it), so quoting it as "before" would
credit this row with other rows' bytes.

| prediction | actual | verdict |
|---|---|---|
| `((a)\|b){0,4000}c` 199,511 -> ~29,035 code B | 193,210 -> **22,731** | beaten |
| `((a)\|b){0,400}c` 45,303 -> ~29,033 code B | 39,001 -> **22,728** | beaten |
| the two AUTO artifacts within 2 lines | **1,026 lines each, delta 0** | held |
| `((a)\|ab){4000}c` 651,694 -> ~36,098 (-94.5 %) | 645,387 -> **29,788 (-95.4 %)** | beaten |
| K41 witness 2 refused -> ~158,601 code B under default caps | **152,302, ACCEPTED**; gcc -O2 2.04 s (was 66.92 s) | held, within 4 % |
| corpus ~2,000,000 B off, all from 23 patterns | **-1,874,322 B** over exactly those 23 | held, within 6.3 % |
| the rest byte-identical | **60-artifact control sample: 0 changed, delta 0** | held |
| bench: stamps byte-identical | **54 of 54 emits byte-identical over 18 patterns** at the size fix; **52 of 54 after the [SEL-1] rung**, the two being `level-context` under the two flag sets that give it a prefilter | held, then deliberately broken by §6's own commit |

**THE FULL SIZE-LOG FIGURE IS THE MERGE BATTERY'S TO CONFIRM.** The corpus
number above is measured over the 23 over-budget artifacts plus a 60-artifact
control drawn from the 1,365 under it, because regenerating
`docs/dev/artifact_size_log.tsv` requires a full `make test` and this lane may
not run one (box rule: one heavy suite at a time). Against the 39,309,904
hybrid bytes the log records, -1,874,322 is **-4.8 %**, against a predicted
5.1 %. The battery is what should confirm it end to end.

**The bench line was wrong in its population, not in its claim.** It said "13
of 14"; [ART-SIZE] had already established that the right population is 18
pattern files across three pinned flag sets, not 14
(`docs/design/artifact_size_term.md` §4.3a). Re-run over that population by
`docs/design/opt4_impl/probes/bench_identity.sh`: **54 of 54 emits
byte-identical**, none moved. `level-context` is among the identical ones and
remains `RX_VM_PREFILTER "none"` after `dfa overflowed: >32000 states` — the
SIZE fix does not reach it, exactly as §6 says.

**AND THEN THE [SEL-1] RUNG MOVED IT, ON PURPOSE.** After STEP 3's second
commit the same probe reads **52 of 54 byte-identical, 2 moved**, both of them
`level-context` — under `--features all` and under
`--features all --no-captures`, but NOT under `--features all --engine=vm`,
where the prefilter is off by that flag's own side effect (R21 E-6) and there
is nothing for the rung to do. That is the rung's entire intended footprint on
the bench: one pattern, two flag sets, every other emit still identical to the
byte. A probe reading 54 of 54 after the second commit would mean the rung had
not fired.

**TIMING ON THE BENCH'S OWN THROUGHPUT SUBJECTS, and a warning about reading
it.** `tests/bench/fdriver.c` find-all over `t-a-valid-addrs`, `t-b-no-at` and
`t-c-long-atom-run` for all three email patterns: match counts identical in
every cell (40,330 on `t-a`, 0 on the others). Timing is identical BY
CONSTRUCTION here, because the artifacts are byte-identical — there is no code
to be slower. The first reading nonetheless showed apparent 2× "regressions",
and they were entirely box noise: the SAME binary re-timed five times on
`t-b-no-at` ran 1.81 / 1.81 / 2.13 / 2.15 / 2.17 ns/byte, a 20 % spread, while
interleaved after/before runs converged to 1.803 against 1.807. Recorded
because a lane reading three-iteration numbers off a shared box would have
reported a regression that does not exist.
