# [LIM-2] M1 — the [NF25] partition-rule measurement

Lane `m1part`, worktree `worktrees/m1part`, branch `lane/m1part`,
**2026-09-04**. MEASUREMENT ONLY: an instrument at `studies/lim2_m1/`
(own Makefile, links `build/libpcrec.a`, never built or run by pcrec's
`make`/`make test`) and this memo. Nothing under `src/` or `tests/` is
written by this lane.

**Disclosure (scope mandate).** My context was injected at spawn with the
session-root `CLAUDE.md` and the memory index. Neither named a fact that
shaped this memo's analysis; the charter and every technical claim below
come from `docs/dev/dfa_online_minimization_study.md`, `docs/dev/plan.md`'s
[LIM-2] row, `studies/lim2_census/`, and this lane's own instrument and
its output, all read or produced in this worktree.

## 0. What M1 was re-scoped to measure, and why

`docs/dev/dfa_online_minimization_study.md` §6 (M5, lane `m5paper`,
2026-09-04) read [NF25] (Nicol & Frohme, "Deconstructing Subset
Construction: Reducing While Determinizing", arXiv:2505.10319, TACAS 2026)
in full and found the study's original §3.5 claim — that a sound periodic
partial minimization's available merges are "precisely the closed
subgraph" — **too pessimistic** (§6.6 item 4). The paper's own
intermediate-minimization rule (Algorithm 1 lines 34-42) pins every
UNEXPLORED state in its own singleton block and runs Hopcroft on the rest;
two explored states each carrying an edge to the *same* unexplored
successor still merge under that rule, which is a strictly larger merge set
than "both endpoints fully closed". M1 was re-scoped from measuring the
closed fraction alone to measuring **both** quantities side by side, on
pcrec's own population — real regexes with counted repeats, a population
[NF25]'s own evaluation contains none of (§6.4 of the study: 52 Walnut
systems and 300 random modular NFAs, no regular expression and no counted
repeat anywhere).

This memo reports what that measurement found.

## 1. Method, in brief (full argument: `studies/lim2_m1/lim2_m1.c`'s header)

The instrument calls the real, unmodified `pcrec_build_dfa` once per
pattern (matching `studies/lim2_census/lim2_census.c`'s own methodology)
and takes the finished raw (pre-minimize) forward machine. It then
**reconstructs its own construction history post-hoc** from that finished
structure alone — not live instrumentation, and exact rather than
approximate, because (1) `pcrec_build_dfa`'s worklist processes states in
strict index order (`src/ir/dfa.c:1284`) and (2) a state's `eolvar`/
`endvar` edges are always interned before the state itself, so they never
point forward (confirmed as an invariant on every population member, not
merely assumed — `assert_eol_end_backward` in the instrument). The one
external fact needed is the exact seed count, read directly off the
finished `Dfa`'s own `s0`/`s1u[]`/`s1g[]` fields.

At five checkpoints (10/25/50/75/100% of the machine's final raw state
count — 10% added beyond the brief's 25/50/75/100% because several
population members' interesting dynamics are front-loaded, and a single
point at 25% cannot distinguish "already ramped by 10%" from "just
starting"), the instrument computes:

- **(a) the partition-rule block count** — [NF25]'s own rule: Moore/Hopcroft
  refinement over the EXPLORED states (rows already filled), with every
  UNEXPLORED state (created but unprocessed) pinned in its own permanent
  singleton block, mirroring `src/opt/minimize.c`'s signature/hash shape
  exactly restricted to the explored set;
- **(b) the closed-subgraph fraction** — the study's original §3.4/§3.5
  quantity: the fraction of existing states from which no unexplored state
  is reachable, computed by one linear BFS over the reverse transition
  graph;
- **(c) at the 100% checkpoint only**, the partition-rule count against the
  TRUE minimized count from the real `pcrec_minimize_dfa`, run on an
  independent snapshot of the same raw machine.

**Self-check.** At 100% every state is explored (no pin survives), so (a)'s
computation degenerates exactly to what `pcrec_minimize_dfa` computes on
the same machine — same signature, same fixpoint. The instrument asserts
these are equal on every population member and hard-fails (nonzero exit) if
not. **This held on all 119 measured patterns, zero exceptions** — see
`studies/lim2_m1/m1_summary.txt`.

**Failing-direction control** (`docs/dev/learnings.md` §3's standing rule:
check the check, in the direction that should fail). `./lim2_m1
--sabotage-selftest PATTERN` runs one pattern three ways — honest, with the
initial accept-bit split disabled, and with the class-0 transition column
corrupted to a constant — and reports the 100%-checkpoint self-check each
way. MEASURED on the lim2 census's own witness
(`(1{0,30}?[^]abc][^abc]){28,30}0+|a`): the honest run matches (1010=1010);
disabling the accept split MISMATCHES (1006 vs 1010) — **the self-check
catches a planted wrong-block-count bug**; corrupting class 0 happened to
have no effect on this particular witness (its alphabet carries no live
distinction on that class), reported rather than hidden.

## 2. Population

Two-phase selection per pattern (`studies/lim2_m1/README.md` "Population"
has the full accounting): a cheap raw-only build decides inclusion — raw
table entries `> 65535` (matching `lim2_census.c`'s own
`PREMUL_MAX_ENTRIES` population, the 12-pattern set STEP 1 measured) **or**
raw states `> 1000` (the broader "large-DFA tail" cut this lane's brief
asks for, stated rather than derived from any existing constant). Two files
are force-included regardless of size because the charter names them
explicitly — `tests/base/k18_cost_gates.rxt` (the census witness plus the
nested-counted family) and `tests/counterk/counterk.rxt` (the counted-repeat
differential tower, 38 blocks) — plus `tests/classes/classes.rxt` as a
control population (ordinary small class patterns, no counted-repeat
blowup; the study's own M1 charter names "20 ordinary corpus patterns as a
control"). pcrec-bench's `bench/altwide/patterns/*.rx` set (33 patterns) is
read on this box at `/Users/fdicostanzo/pcrec-bench` (read-only) and
force-included in full — the actual pattern files, not a reconstruction
from `studies/lim2_census/census_data.tsv`'s aggregate columns (that file
carries no pattern text; reading the real `.rx` files directly, since the
sibling repo is reachable on this box, is strictly better than the brief's
fallback).

**MEASURED, full sweep, `studies/lim2_m1/run_m1.sh`:** 3,383 pattern blocks
seen across the corpus + force files + altwide; 389 refused (K7-class cap),
403 no-DFA-route (VM-only), 433 ENG_ATTEMPT (bot; the bail never applies
there), 2,039 below the size cut and excluded, **119 included** (85 of them
force-included below the size cut). Zero FAIL lines anywhere in the run —
`studies/lim2_m1/m1_summary.txt` is the committed accounting; every count
above is read from it, not asserted.

**Scope: forward machine only**, matching `lim2_census.c`'s own precedent
and the online-minimization study's §4.2 A3, which already names the
reverse machine as unmeasured. Extending to the reverse machine (`prune =
false`) is a straightforward re-run of the same instrument against the
other `pcrec_build_dfa` call and was not done here — box-time budget
("light local testing only") went to breadth of population on the forward
machine instead. Named as the natural next step, not attempted.

## 3. Finding 1 — the monotonicity verdict: REFUTED, with counterexamples

**The charter's question: does the partition-rule intermediate count ever
EXCEED the final minimized count — the property a lower-bound projection
(N2's successor design) needs proven or refuted?**

**REFUTED.** Of the 119 measured patterns, **30 (25.2%)** show the
partition-rule block count exceeding the true minimized count at some
checkpoint before 100%. Restricted to the "large-DFA tail" (raw states
`> 1000`, 34 patterns), **8 (23.5%)** exceed. The excess is not a rounding
margin — on the worst witnesses it is enormous:

| pattern (id) | raw_n | min_n | worst intermediate block count | max ratio over min_n |
|---|---|---|---|---|
| `tests/counterk/counterk.rxt:1845` | 8,002 | 2 | 6,002 (at 75%) | **3,001×** |
| `tests/counterk/counterk.rxt:1725` | 8,002 | 2 | 6,002 (at 75%) | 3,001× |
| `tests/counterk/counterk.rxt:1631` | 4,096 | 2 | 3,072 (at 75%) | 1,536× |
| `tests/counterk/counterk.rxt:1551` | 1,002 | 2 | 752 (at 75%) | 376× |
| `tests/base/k18_cost_gates.rxt:70` | 1,968 | 83 | 1,418 (at 75%) | 17.1× |
| `tests/base/k18_cost_gates.rxt:66` | 27,575 | 1,010 | 10,608 (at 75%) | **10.5×** |

The census witness itself — the pattern that started this whole study
(27,575 raw → 1,010 minimized, lim2's 97.06% shrink) — has a partition-rule
count of 9,169 at the 50% checkpoint and 10,608 at 75%, both **more than
ten times** the true final answer. A size bail reading the intermediate
partition-rule count as a lower bound on the same pattern that motivated
this whole study would have been wrong by an order of magnitude.

**Why, mechanically (confirms [NF25] §3.2's own statement, with numbers).**
Every unexplored state — which for a counted-repeat pattern in the middle
of construction is *most* of the machine (Finding 2, below) — is pinned in
its own singleton block regardless of whether the final machine would ever
distinguish it from its siblings. The k18 shape's whole mechanism (§1.2 of
the online-minimization study) is that many *different* raw states turn out
to have the *same* residual language because the union of their futures
coincides; the partition rule cannot see that until those futures are
explored, so mid-construction it is carrying thousands of blocks the final
pass will fold into one. `[NF25]` §6.3 (the study's own reading) says this
in words — *"two blocks of an intermediate partition may be separated only
by witnesses that run into distinct unexplored states... not proofs of
distinguishability"* — this measurement is the concrete number behind that
sentence, on pcrec's own population.

**Not universal, and the contrast is informative.** On the altwide `w-`/`s-`
family, where the raw-to-minimized shrink is tiny (0.75% on `w-2048`,
3.53% on `s-4096`), the partition-rule count **never** exceeds the true
minimum at any checkpoint (`exceeds_final=0` on all of `w-2048`, `s-4096`,
`sh1-512` and every other altwide row measured) — there is simply very
little false-distinction opportunity when the final machine is already
close to the raw one. The exceeding behaviour is specific to patterns with
substantial shrinkage still ahead of the checkpoint, which is exactly the
population a size-bail margin most needs to get right.

**Verdict for N2's successor design:** the raw partition-rule intermediate
count, taken naively, is **not usable as a sound lower bound**. It is
neither a lower nor an upper bound in general — the online-minimization
study's §6.3 sketch of "pairwise-distinguishability across blocks" as a
possible sharper quantity remains unbuilt and unmeasured here; what this
measurement adds is that the naive reading of [NF25]'s own rule is
concretely, sometimes dramatically, wrong in the size-bail direction on
pcrec's real population.

## 4. Finding 2 — the A/N2 re-ranking comparison: confirmed, and generalizes

**The charter's other question: how does the partition-rule fraction
compare to the closed-subgraph fraction at the same checkpoint — the
comparison that re-ranked candidate A in §6.6?**

**The closed fraction stays near zero for essentially the whole
population, at every checkpoint before 100%.** Across all 119 patterns, the
single highest closed fraction observed at the 50% checkpoint is **14.3%**
(`tests/counterk/counterk.rxt:1054`, a 14-raw-state pattern — small enough
that 50% is only 7 states, and 1 of them happens to be closed). On every
pattern with a large or substantial shrink — the population a bail
mechanism actually cares about — the closed fraction sits at a few
**hundredths of a percent** all the way to the last checkpoint:

| pattern | raw_n | closedfrac@25% | closedfrac@50% | closedfrac@75% |
|---|---|---|---|---|
| k18 census witness (`:66`) | 27,575 | 0.0145% | 0.0073% | 0.0387% |
| k18 `{8,8}` sibling (`:70`) | 1,968 | 0.2033% | 0.2033% | 0.1355% |
| altwide `w-2048` | 9,872 | 0.0000% | 0.0203% | 0.0135% |
| altwide `s-4096` | 8,269 | 0.0000% | 0.0000% | 0.0161% |
| `counterk:1845` (99.98% shrink) | 8,002 | 0.0500% | 0.0250% | 0.0167% |

This **quantitatively confirms**, across the whole measured population and
not only the k18 witness the original study read by hand, the finding
`docs/dev/dfa_online_minimization_study.md` §3.5 and §4.2's A7 predicted
"reasoned, not measured" and M1 was chartered to test: **candidate A
(periodic partial minimization gated on the closed subgraph) finds almost
nothing to merge on this population, until construction is nearly
finished.** The study's own bar (§5.2 M1, as revised by §6.6): "if the
closed fraction stays under 10% until the last 5% of construction, A is
dead for this population and N2 is vacuous." Every non-trivial pattern
measured here stays *two to four orders of magnitude* under that 10% bar
through the 75% checkpoint. **A stays declined, and N2 (the closed-subgraph
lower-bound projection, §3.4) is confirmed vacuous on this population** —
consistent with, and now measured rather than reasoned for, the study's
recommendation to solve lim2's margin problem with N1 instead (§5.1 step 1,
§6.6 item 1).

**The partition rule sees dramatically more than the closed subgraph does
— the numeric form of §6.6 item 4's "too pessimistic".** Reading the SAME
checkpoint two ways on the census witness at 50%: the closed fraction says
0.0073% of states are provably settled; the partition rule's own
"already-merged" fraction — `(T − block_count) / T`, how much of the
existing machine the rule has already folded together — is **33.5%**
(13,788 states existing, 9,169 blocks). At 75% it is **48.7%** (20,681
existing, 10,608 blocks). The gap between "0.007% closed" and "33-49%
already-merged-by-the-rule" is exactly the gap §6.6 item 4 identified in
words — two states each carrying an edge to the *same* unexplored successor
merge under [NF25]'s rule while neither is closed — measured here, on
pcrec's own machine, at two orders of magnitude.

## 5. The B-vs-C implication, stated as evidence (not a recommendation)

Per the manager/Frank ruling this lane's brief quotes, this section states
what the numbers show and stops there — the choice between B and C is the
manager's and Frank's to make, on M2 (the dominance prize, not chartered
for this lane) and the numbers above together.

- **Finding 1 removes one specific hoped-for cheap win**: an intermediate
  partition-rule count cannot, by itself, license a smaller emit-size bail
  the way `docs/dev/dfa_online_minimization_study.md` §3.1 wanted (the
  configuration where "compaction proves equivalence exactly during
  construction" would make raw equal emitted). §6.1/§6.3 already withdrew
  the OTF-specific version of that hope; this measurement shows the
  *naive* reading of the paper's own rule is wrong by up to 3,001× on
  pcrec's population, which is a sharper and more concrete statement than
  "not exact" — it is "not even loosely bounded in the direction a bail
  needs".
- **Finding 2 sharpens, rather than reverses, §6.6's re-ranking of A.** The
  paper's rule genuinely sees more than the closed subgraph (a
  measured 33-49%-vs-0.007% gap on the census witness) — so "A is dead" was
  never quite the right description of what [NF25]'s Algorithm 1 computes;
  what is dead is A **read as this study originally defined it** (closed
  subgraph only). The paper's fuller rule finds real merges early — this
  measurement's own "already-merged fraction" is the concrete evidence for
  it — but Finding 1 shows those early merges are not *trustworthy* ones a
  bail could act on, because the SAME rule that finds 33-49% "merged" at
  midpoint is also the rule whose block count exceeds the truth by 10-3001×
  on other checkpoints of the very same patterns. **A rule that finds real
  structure but cannot be trusted as a bound is exactly the shape [NF25]'s
  own architecture predicts** (§6.2: the merges decided at the interrupt are
  a genuine but non-monotone refinement, not a proof of anything) — the
  paper requires a mandatory final pass for precisely this reason (§6.1),
  and this measurement is the pcrec-side confirmation of why.
- **Candidate B (dominance pruning)** is untouched by anything measured
  here — this lane measured the paper's OTF-family rule (candidate A plus
  the registry generalization, §6.6's Table 1 mapping), not the simulation
  preorder SC-S/candidate B needs. M2 (the dominance prize) remains the
  open measurement that would size B, per §5.1 step 3/§6.6 item 3's
  B-first revision — not chartered for this lane.

## 6. What this measurement does not claim

- That the partition rule is useless — Finding 2 shows it recognizes real
  structure the closed subgraph cannot see. What it lacks, per Finding 1,
  is the MONOTONICITY a size bail specifically needs.
- Any number about the reverse or anchored machines — forward only (§2).
- Any claim about candidate B or the dominance prize (M2) — untouched here.
- That 119 patterns exhausts the corpus's large-DFA tail — the `> 1000`
  cut and the two named force-included files are this lane's own stated
  choice (§2), not a claim of exhaustiveness.
- A recommendation on B vs C — §5 states evidence, the choice is the
  manager's/Frank's per the standing ruling.

## 7. Data and reproduction

`studies/lim2_m1/m1_data.tsv` (119 rows, committed) and
`studies/lim2_m1/m1_summary.txt` (the population accounting, committed).
Reproduce with `cd studies/lim2_m1 && make CC=gcc-16 && bash run_m1.sh`
(after `make CC=gcc-16` in the repo root). Machine/date context (D35
spirit): macOS arm64, gcc-16 16.2.0, measured 2026-09-04 against
`lane/m1part`; the full sweep (3,383 blocks seen, 119 measured) took 58
seconds wall on a quiet box. Re-measure before load-bearing use elsewhere.
