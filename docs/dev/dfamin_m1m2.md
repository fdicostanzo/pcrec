# [LIM-2]/dfamin M1 + M2 — the two measurements the study's §5.2 owed

Lane `dfam12`, worktree `worktrees/dfam12`, branch `lane/dfam12`,
**2026-09-16**, chartered by Frank. MEASUREMENT + a probe instrument that
DOES NOT LAND (disposition: §5). Nothing under `tests/` is written.

**Disclosure (scope mandate).** My context was injected at spawn with the
session-root `CLAUDE.md` and the memory index; the parts that shaped this
work are the situation-index rows on `D77` and on scaffolding/abi changes,
and `pcrec-check-design-lessons`. Everything technical below comes from
`docs/dev/dfa_online_minimization_study.md`, `docs/dev/lim2_m1_partition_
measurement.md`, `docs/dev/known_issues.md` K25, `docs/dev/plan.md`'s
[LIM-2] row, and this lane's own reading of `src/ir/nfa.c`/`src/ir/dfa.c`
and its own instrument's output, all in this worktree.

## 0. What was already measured, and what this lane adds

`docs/dev/lim2_m1_partition_measurement.md` (lane `m1part`, 2026-09-04)
already measured M1 as the study's §6.6 RE-SCOPED it: the paper [NF25]'s own
partition rule (Hopcroft/Moore over the explored states, every unexplored
state pinned singleton), not the closed-subgraph fraction. That memo is
**not repeated here** — its Finding 1 (REFUTED: the rule's intermediate
block count exceeds the true minimum on 30/119 patterns, up to 3,001×) and
Finding 2 (candidate A confirmed dead: closed fraction never exceeds 14.3%
pre-100%) stand as measured. What this lane adds to M1, per its own brief,
is a **third named population m1part's did not force-include**: K25's own
chain shapes (`a{0,N}` and `(?:abcdefghij){N}`, §2 below) — run through
m1part's own already-validated, unmodified instrument
(`studies/lim2_m1/lim2_m1.c`), zero changes to that binary. M2 (the
dominance prize, candidate B) was **never measured** — the plan row records
it explicitly DORMANT since 2026-09-04 ("we may never need to measure it")
— and is built fresh here (§3).

## 1. Method — M1 (reused, extended by one population)

`studies/lim2_m1/lim2_m1.c` is unmodified (its self-check still passes:
`make CC=gcc-16 && ./lim2_m1 --sabotage-selftest '(1{0,30}?[^]abc][^abc]){28,30}0+|a'`
reports `honest: 100pct block_count=1010 true_min=1010 MATCH` on this lane's
own rebuilt `build/libpcrec.a` — the M2 probe's added `NState` fields do not
disturb it). The only new artifact is a population file,
`docs/dev/dfamin_m1m2_evidence/k25_chain_ladder.rxt`: K25's own witness
(`a{0,25000}`), a ladder around it (`a{0,100..10000}`), and K25's own
"second, unattributed case" (`(?:abcdefghij){500,1500,3000}`,
`known_issues.md` K25's own text), force-included via `lim2_m1`'s existing
`--force` convention. Output: `studies/lim2_m1/../lim2_m2` is a SEPARATE
binary (§3); this file's own K25 run is `/tmp`-scratch, reproduced by
`cd studies/lim2_m1 && ./lim2_m1 --force ../../docs/dev/dfamin_m1m2_evidence/k25_chain_ladder.rxt`.

## 2. M1 results

### (a) The shipped corpus's DFA-route constructions

Already measured and committed: `studies/lim2_m1/m1_data.tsv` (119
patterns after the size cut — see that memo's §2 for the population
accounting) and `m1_summary.txt`. Not re-run here (D77: the instrument and
its population are unchanged; re-running would reproduce, not add,
numbers). Headline restated for this memo's own completeness: 30/119
(25.2%) show the partition rule's intermediate block count EXCEEDING the
true minimum, up to 3,001× on `tests/counterk/counterk.rxt:1845`; the
census witness itself hits 10.5× at its 75% checkpoint.

### (b) The K18 witness

Same source. The census witness
(`tests/base/k18_cost_gates.rxt:66`, `(1{0,30}?[^]abc][^abc]){28,30}0+|a`)
is already in population (a)'s 119 and is the sharpest single row: 27,575
raw → 1,010 minimized, partition-rule block count 10,608 at 75% (10.5× the
truth), "already-merged fraction" 33.5%→48.7% between the 50% and 75%
checkpoints against a closed-subgraph fraction that never exceeds 0.04% at
the same points.

### (c) K25's own chain shapes — NEW, this lane

| pattern | raw_n | min_n | block@10% | block@25% | block@50% | block@75% | block@100% |
|---|---|---|---|---|---|---|---|
| `a{0,100}` | 101 | 101 | 10 | 25 | 51 | 76 | 101 |
| `a{0,1000}` | 1,001 | 1,001 | 100 | 250 | 501 | 751 | 1,001 |
| `a{0,5000}` | 5,001 | 5,001 | 500 | 1,250 | 2,501 | 3,751 | 5,001 |
| `a{0,10000}` | 10,001 | 10,001 | 1,000 | 2,500 | 5,001 | 7,501 | 10,001 |
| `a{0,25000}` (K25's own witness) | 25,001 | 25,001 | 2,500 | 6,250 | 12,501 | 18,751 | 25,001 |
| `(?:abcdefghij){500}` | 5,001 | 5,001 | 500 | 1,250 | 2,501 | 3,751 | 5,001 |
| `(?:abcdefghij){1500}` | 15,001 | 15,001 | 1,500 | 3,750 | 7,501 | 11,251 | 15,001 |
| `(?:abcdefghij){3000}` | refused | — | — | — | — | — | — |

**Every row shows `block(T) == T` at EVERY checkpoint — the partition rule
merges NOTHING, anywhere, on any of these patterns, and `raw_n == min_n`:
these machines are already minimal before minimization ever runs.**
`(?:abcdefghij){3000}` is `known_issues.md` K25's own "second case ... not
attributed" — this instrument refuses it (`PCREC_MAX_DFA_STATES_TABLE` /
32,000 lies between the 15,001-state and the would-be 30,001-state rows),
which does not change the answer for the two smaller rows in the same
family: zero merges either way.

**Why, mechanically, and it is the reason M2 finds the same thing (§4b
below) independently.** Both shapes are STRICT SEQUENTIAL CHAINS: `a{0,N}`
lowers to the nested-optional tail `(a(a(a...)?)?)?` (`src/ir/nfa.c`'s
`A_REP` arm, rmin=0), and copy *i+1*'s entry position is reachable ONLY by
CONSUMING copy *i*'s literal byte first — there is no epsilon path that
reaches two different copies' positions from the same closure without an
intervening byte. So every raw state genuinely has a DIFFERENT residual
language (state *k* = "have matched exactly *k* so far, up to *N-k* more
allowed" — for *k* != *k'*, `N-k != N-k'`, a real distinguishing
continuation exists), and there is nothing for minimization, the partition
rule, OR dominance pruning (§4) to find. **This is the opposite mechanism
from the K18/counterk shapes** (§2b, §4a): there, the redundancy is that
DIFFERENT subsets converge to the SAME residual language because a
NULLABLE or lazily-optional sub-structure lets several "how many copies
remain" configurations coexist or collapse; a plain literal-body counted
chain has no such structure and stays genuinely `N+1`-state throughout.
K25's own cost (Moore refinement paying O(n) ROUNDS with nothing to merge)
is therefore PURE OVERHEAD on this shape, with zero yield from any
compaction mechanism this study or its two candidates propose — a fact
worth stating plainly since it means **no candidate examined by this study
family (A, A′, B, C, N1, N2) offers K25 any relief at all**; K25 stays
exactly what `known_issues.md` already calls it, a Moore-refinement
complexity cost with no redundancy behind it.

## 3. Method — M2, the dominance prize (candidate B, Tier 1)

**Approximation named up front, per the study's own §3.7 "one tempting
shortcut" and this lane's brief**: this instrument uses the study's
DELIBERATELY ILLEGITIMATE stand-in — "drop a position when an earlier copy
of the same unrolled repeat is present in the list" — NOT the general
simulation preorder candidate B actually specifies. §3.7 sanctions this
stand-in for exactly one purpose, sizing the win, and forbids it as a
landing; §6's finding below is a measurement of the STAND-IN, and its
failure modes (§4b) are not automatically candidate B's failure modes,
though §4's own brittleness table already predicted the SHAPE of the
hazard this stand-in reproduces (B2, the K18 open-loop context).

**Implementation — a real, measurement-only edit to THIS WORKTREE's
`src/`, gated on `getenv("PCREC_PROBE_M2")` so one binary drives both the
baseline and the pruned measurement (does not land — §5):**

1. `src/core/internal.h`: `NState` gains `probe_rep_id`/`probe_copy_idx`
   (both `-1` by default, set in `src/ir/nfa.c`'s `nst()`).
2. `src/ir/nfa.c`'s `A_REP` arm, the `X{m,n}` NESTED tail loop only (the
   `rmax < 0` infinite-star branch is untouched — a `*`/`+` loop is a single
   NFA cycle already, not a family of copies to compare): each iteration's
   body span `[probe_seg_start, nfa->n)` is tagged `(probe_rep_id,
   copy_idx)` for every node NOT already tagged by a NESTED repeat's own
   tagging pass (`if (rep_id < 0)`) — so a repeat nested inside another
   keeps ITS OWN tag, and the outer repeat's tag reaches only the nodes the
   inner one did not claim (the shared trailing literal atoms after an
   inner sub-repeat, if any).
3. `src/ir/dfa.c`'s `make_state`, the site where `closure()`'s freshly
   filled `buf[0..nout)` becomes a `DView`'s `list`/`nlist` — the EARLIEST
   point downstream of the closure where a list can be edited before
   `intern()`'s K7 charge, `dhash` and `view_same` ever see it. A new
   function `probe_m2_prune` (no-op unless the env var is set) keeps, among
   positions sharing a `probe_rep_id`, only the one with the SMALLEST
   `probe_copy_idx` (§1.2/§3.7: the earliest copy has the largest residual
   language and dominates); process-global counters
   `pcrec_probe_m2_dropped`/`pcrec_probe_m2_total` accumulate every
   closure's contribution.

**Cost model, stated honestly**: `probe_m2_prune` is O(nout²) per closure —
acceptable for measurement (`nout` is a position-list width the
construction already pays to build and is bounded by the same caps every
other row here reads), and is NOT a claim about what a shipped mechanism's
cost would be (§7).

**Reproduction**: `studies/lim2_m2/lim2_m2.c` (a fresh, small harness,
modeled on `studies/lim2_m1/lim2_m1.c`'s own `measure_raw` pipeline prefix
— parse → altcls → discharge_atomic → callgraph_build → select_engine →
postresolve → build_nfa → wrap_unanchored → build_dfa → minimize_dfa, under
DEFAULT options) reads `pcrec_probe_m2_dropped`/`_total` as `extern`s and
reports, per pattern, `raw_n min_n subset_elems probe_total probe_dropped`.
`studies/lim2_m2/run_m2.sh` runs it TWICE over the same file list —
`PCREC_PROBE_M2` unset (baseline) then `=1` (pruned) — because
`probe_m2_enabled()`'s cache is a function-static, correctly ONE mode per
process (matching every other axis flag in this tree; not something this
harness works around). `studies/lim2_m2/m2_baseline.tsv` /
`m2_pruned.tsv` are the committed raw output; §4's tables are read from
them by the join in this section's own footnote command:
`join -t$'\t' -j1 <(sort m2_baseline.tsv) <(sort m2_pruned.tsv)`.

## 4. M2 results

### Sanity control — the hand-derivable pair (D77/brief obligation)

`(?:a|){0,1}` — ONE optional copy of a NULLABLE body (`a` or empty). No
second copy exists to dominate or be dominated: **hand-predicted zero
drops, MEASURED zero** (`probe_total=probe_dropped=0`, `raw_n`/`subset_elems`
unchanged between baseline and pruned).

`(?:a|){0,3}` — THREE copies of the same nullable body, chained
`(B(B(B)?)?)?` where `B = (?:a|)`. Because `B`'s "empty" branch is a bare
alternation (NOT a nested `A_REP`, so it is never claimed by an inner tag),
the epsilon closure from the very START reaches THREE live leaf positions
at once — copy 0's `a`, copy 1's `a`, copy 2's `a` — because each copy's
empty branch is a pure epsilon edge straight into the NEXT copy's own
choice point, with zero bytes consumed anywhere along the way. **Hand
argument: copy 0's `a` dominates copies 1 and 2's (§1.2: earlier copy has
strictly more remaining language), so the correct prune keeps exactly ONE
of the three at the start state.** MEASURED: `raw_n` 4→2, `subset_elems`
6→1, `probe_total=12` (positions examined across the whole build),
`probe_dropped=8` — nonzero, in the predicted direction, on the pattern
where coexistence is structurally possible and NOT on the one where it is
not. This is the "hand-derivable tiny chain" the brief asks for: the
DIRECTION and the MECHANISM (which specific positions get dropped, and
why) are argued by hand and confirmed exactly; the instrument's own
aggregate counters are read from the tool rather than independently
re-summed, stated so the distinction is not glossed over.

### (a) The shipped corpus's DFA-route constructions

`studies/lim2_m2/run_m2.sh`'s full sweep (every `.rxt` under `tests/`
except `known_fail/`, minus the three force files below, measured
unfiltered — no size cut, unlike M1's own instrument): **1,232 rows**
measured both ways.

| | count | % of 1,232 |
|---|---|---|
| any drop at all (`probe_dropped > 0` under pruning) | 176 | 14.3% |
| raw state count REDUCED (`pruned_raw < base_raw`) | 49 | 4.0% |
| raw state count INCREASED (`pruned_raw > base_raw`) | 2 | 0.16% |

Aggregate K7 charge (`subset_elems`, summed over all 1,232 rows):
**896,210 (baseline) → 856,495 (pruned), a 4.6% net reduction** — most of
the corpus carries no counted-repeat redundancy at all, so the aggregate is
dominated by the ~86% of patterns the stand-in never touches.

**The two regressions**, both in `tests/possessify/possessify.rxt`
(lines 1241 and 2934, the same shape twice): `raw_n` 7→8 (+1 state) while
`subset_elems` still IMPROVES slightly (42→39) and `min_n` is unchanged at
3 either way — a SMALL instance of the same non-monotone hazard the census
witness shows catastrophically (below), on an ordinary corpus pattern
nobody would have flagged as a counted-repeat stress case.

### (b) The K18 witness — the sharpest finding in this memo

**The stand-in makes the census witness (`tests/base/k18_cost_gates.rxt:66`)
REFUSE outright.** Baseline: 27,575 raw states, `subset_elems` 11,317,001,
minimizes cleanly to 1,010. Under `PCREC_PROBE_M2=1`: `cx.dfa_overflowed=1`,
`dfa_overflow_why="dfa overflowed: >32,000 states"`, `subset_elems` at the
point of refusal 2,650,608 (still climbing when the cap fires). **The
pattern that motivated this entire study — the one candidate B's own §3.7
argument says "this shape could crush" — is the one pattern in this memo
where the naive stand-in turns a clean compile into a hard refusal.**

This is exactly `docs/dev/dfa_online_minimization_study.md` §3.7 condition
2, now measured rather than argued: *"the K18 open-loop context breaks
context-freeness of the future... a preorder computed on the bare NFA may
fail under some contexts."* This instrument's tagging is purely structural
(which unrolled copy a node belongs to) and carries NO notion of the
open-loop context `src/ir/dfa.c:207`'s memo is keyed on — so it drops a
position whenever ITS COPY INDEX says to, regardless of whether the two
positions being compared are reachable under the SAME open-loop
configuration or different ones. On the census witness's own nested lazy
structure (`1{0,30}?` inside `(...){28,30}`), that unsoundness does not
merely fail to help — **it manufactures MORE distinct raw states than the
correct construction would, past the point where the state-count cap that
never fires on the unmodified pipeline starts firing.**

### (c) K25's own chain shapes

Consistent with M1 (§2c) and predicted by the SAME structural argument
(sequential, single-copy-per-subset reachability — §2c's mechanical
explanation applies word for word here, since the domination test and the
minimization merge test are both blind on a shape with no coexistence to
find): **every row shows `probe_dropped = 0`.** `probe_total` is nonzero
(positions ARE examined — the tags are present and the comparison runs),
confirming the zero is a genuine "nothing found," not "nothing looked."
`raw_n`/`subset_elems` are identical between baseline and pruned on all
seven rows measured (the ladder plus the two `(?:abcdefghij){N}` rows).

### `tests/counterk/counterk.rxt` — the study's own force-included population, and the one with real, MIXED wins

Not one of the brief's three named populations, but m1part's own precedent
force-includes it and it is where this memo's clearest POSITIVE evidence
for candidate B's mechanism lives (35 rows measured, several excerpted):

| pattern id | base raw→pruned raw | base subset→pruned subset | what moved |
|---|---|---|---|
| `counterk.rxt:1725` | 8,002 → 4,003 | 24,030,001 → 12,006 | raw roughly halves, K7 charge ~2,001× down |
| `counterk.rxt:1631` | 4,096 → 2,050 | 6,300,667 → 6,147 | raw halves, K7 charge ~1,025× down |
| `counterk.rxt:1551` | 1,002 → 503 | 378,751 → 1,506 | raw halves, K7 charge ~251× down |
| `counterk.rxt:1845` | 8,002 → **8,002 (unchanged)** | 24,038,002 → 28,006 | **K7 relief with ZERO state-count benefit**, 858× |
| `counterk.rxt:1807` | 8,002 → 8,002 | 24,022,002 → 24,022,002 | **zero effect** — a same-family shape the stand-in cannot touch |

**The `:1845`/`:1725` contrast is the general lesson.** Two patterns from
the same differential tower, structurally close, land on opposite sides of
whether dominance pruning buys STATE COUNT or only MEMORY: on `:1725` fewer
positions per list means fewer DISTINCT lists get interned (raw states
drop); on `:1845` the pruned lists are still all pairwise distinct from
each other (the dropped positions were not what made two states equal),
so `intern()` still creates all 8,002 of them — but each one now COSTS far
fewer `subset_elems`, because K7's charge (`sum(nlist)` at intern time,
`src/ir/dfa.c`'s comment on the charge site) is paid on the PRUNED list,
not the raw one. **This confirms, with a number, the study's own §1.4
observation that compaction and K7 relief are separate questions**: here,
even where state-count compaction gives nothing, the SAME mechanism still
discharges most of K7's charge on this specific pattern — a real, if
narrow, benefit the corpus-wide 4.6% aggregate (§4a) understates for this
one shape and overstates for the ~86% the mechanism never touches.

## 5. Disposition of the probe

**The src/ probe was COMMITTED SEPARATELY, clearly marked measurement-only,
for the manager to drop at merge** — the OPT5M2-PROBE precedent's second
option (`docs/dev/opt5_step2_premeasure.md`'s own note), chosen over
reverting because `studies/lim2_m2/`'s harness links the probe's
`extern`s directly; reverting the `src/` edit would leave that harness
non-reproducible from the delivered branch. The commit
(`[PROBE-M2] ...` — see the branch log) touches exactly
`src/core/internal.h`, `src/ir/nfa.c`, `src/ir/dfa.c`, each hunk carrying
the `[PROBE-M2]` marker inline (§3 above quotes the comments verbatim).
**Byte-identity confirmed by default** (§6) — the probe changes nothing
about a build with `PCREC_PROBE_M2` unset, which is every build this tree
has ever produced or will produce until someone deliberately sets the
variable.

## 6. Validation

- `make strict CC=gcc-16` on this lane's tip (probe present): **clean**
  (`strict: whole tree compiles clean with -Werror -Wshadow`).
- **Emitted-C byte identity, `PCREC_PROBE_M2` unset**: four representative
  patterns (`a{0,50}`, the K18 census witness, `a(b|c)+d`, `(?:abc){3,7}`)
  compiled with `--emit-main` under (1) a scratch build from the exact
  probe-free branch point (`git stash` of the three probe files, rebuild)
  and (2) this lane's probe-instrumented build — **byte-identical** modulo
  the `#include "<basename>.h"` line, which differs only because the two
  runs used different `-o` basenames (the same same-basename methodology
  note `opt5_step2_premeasure.md` already records once in this tree).
- M1's self-check (`--sabotage-selftest`) still reports
  `honest: 100pct block_count=1010 true_min=1010 MATCH` on this lane's
  rebuilt `libpcrec.a` — the added `NState` fields do not perturb it.
- M2's own sanity control: §4's hand-derived pair, verified exactly in
  direction and mechanism (§4, "Sanity control").

## 7. What this does NOT license

- **No timing claims anywhere in this memo.** Neither M1 nor M2 measures
  wall time or CPU; `probe_m2_prune`'s O(nout²) cost is named as a
  measurement-tool cost, not a claim about what a shipped mechanism would
  cost (D77 — a mechanism is not built here, only sized).
- **No mechanism is proposed for landing.** The `[PROBE-M2]` edit is
  disposed of per §5 and is not a draft of candidate B; candidate B's own
  §3.7 three soundness conditions (assertion-boundary domination, the K18
  open-loop context, the reverse machine's no-prune rule) are UNTOUCHED by
  anything measured here — §4b's regression on the K18 witness is evidence
  the NAIVE stand-in is unsafe on exactly the shape condition 2 names, not
  a measurement of what a context-aware simulation preorder would do.
- **Forward machine only**, matching M1's own precedent (`lim2_m1.c`'s
  scope note) and this lane's M2 harness (§3) — the reverse and anchored
  machines are unmeasured by either M1 or M2 here.
- **The corpus sweep is unfiltered by size** in M2 (unlike M1's own
  `>65535`/`>1000` cuts) but still excludes `tests/known_fail/`; it is not
  claimed to be the WHOLE corpus in every sense M1's own population
  section qualifies (M1's §2 "not a claim of exhaustiveness" applies here
  too).
- **`counterk.rxt`'s rich, mixed results are not this lane's chartered
  population** — included because m1part's own precedent force-includes
  it and because it is where this memo's clearest POSITIVE evidence for
  the mechanism lives; the brief's three named populations are §2c/§4b/§4c
  and the shipped-corpus rows in §2a/§4a.

## 8. The B-vs-C decision input (§5.1-as-revised's own ask)

Stated as evidence, per the standing ruling this lane's brief quotes (the
manager's/Frank's to decide, not this lane's):

**Does M1's yield justify C's complexity?** No new evidence changes M5's
own answer (§6.1 of the study): the paper's mechanism REQUIRES a mandatory
final minimization regardless of the partition rule's intermediate yield,
so no size projection becomes exact under candidate C in any configuration
this or the prior M1 memo has found. This lane's K25 addition sharpens
WHERE the yield is zero (a whole shape family — sequential, non-nullable
counted chains — contributes nothing to justify C on, beyond what m1part's
119-pattern population already showed).

**Does M2's prize make B-first the end of the story?** No, on the evidence
here, and more sharply NO than the study's own §3.7 aspiration
anticipated: the prize is REAL but NARROW (14.3% of the corpus touched at
all, 4.0% get real state-count relief, aggregate K7 relief a modest 4.6%,
concentrated almost entirely in `counterk.rxt`-shaped patterns this memo's
three chartered populations do not include), and it is ACTIVELY HARMFUL —
not merely absent, HARMFUL — on the pattern that chartered the whole
study. `docs/dev/dfa_online_minimization_study.md` §4.3's brittleness
table already predicted this exact failure mode (B2: "the K18 open-loop
context makes 'the language of a position' context-dependent... a preorder
computed on the bare NFA may fail under some contexts") and named the
missing safeguard (a cross-product corpus of counted-repeat × assertion ×
machine-direction shapes, oracle-verified, BEFORE the mechanism lands).
This measurement is that prediction made concrete on the study's own
witness, using the most permissive possible reading of the mechanism (a
stand-in with NO cost at all beyond what construction already pays) — and
even that permissive reading regresses the witness from a clean 27,575-state
compile to a hard refusal. **The honest reading is that neither M1 nor M2
supplies a result that would justify building either candidate now** —
closer to §5.1's original "record a legitimate no as a legitimate outcome"
branch than to a B-first go-ahead. A real verdict on candidate B specifically
would need the general, context-aware simulation preorder (never built
here, and forbidden as a landing by the study's own §3.7) plus the
cross-product corpus §4.3 already specifies as a precondition — both
unbuilt, and this memo's own K18 regression is a concrete argument for
building the SAFEGUARD before the MECHANISM, not after.

## 9. Data and reproduction

- `docs/dev/dfamin_m1m2_evidence/k25_chain_ladder.rxt` — the K25 population
  file (§2c).
- `studies/lim2_m2/lim2_m2.c`, `Makefile`, `run_m2.sh` — the M2 harness
  (§3), and `m2_baseline.tsv`/`m2_baseline.summary.txt`/
  `m2_pruned.tsv`/`m2_pruned.summary.txt` — the committed raw output
  (§4a/§4b/§4c/counterk data all read from these two TSVs).
- The `[PROBE-M2]` src/ commit — see §5 for its disposition and the
  branch's own commit message for the exact diff.
- Reproduce: `make CC=gcc-16` at the repo root (builds the probe-bearing
  `build/libpcrec.a`), then `cd studies/lim2_m2 && make CC=gcc-16 && bash
  run_m2.sh` (re-derives `m2_*.tsv`; ~1-2 minutes on a quiet box, two full
  passes over 1,235 patterns each). The K25 M1 run:
  `cd studies/lim2_m1 && make CC=gcc-16 && ./lim2_m1 --force
  ../../docs/dev/dfamin_m1m2_evidence/k25_chain_ladder.rxt`. Machine/date
  context: macOS arm64, gcc-16, measured 2026-09-16 against `lane/dfam12`.
  Re-measure before load-bearing use elsewhere (D35 spirit).
