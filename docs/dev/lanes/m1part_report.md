# m1part — [LIM-2] M1, the partition-rule measurement — delivery report

Lane `m1part`, worktree `worktrees/m1part`, branch `lane/m1part`,
2026-09-04. MEASUREMENT ONLY: nothing under `src/` or `tests/` written, no
`make test` run, no merge performed by this lane (per brief: "do not merge,
do not push, do not touch docs/dev/plan.md").

## Disclosure (scope mandate)

Context injected at spawn: the session-root `CLAUDE.md` (project
instructions) and the memory index (no memory summaries were actually
surfaced in this session beyond the index itself — none named a fact that
shaped the analysis). Everything else the analysis rests on was read from
files in this worktree, named with `path:line` or file path throughout the
memo and this report.

## What was measured

`docs/dev/dfa_online_minimization_study.md` §6.6 (the M5 finding) re-scoped
[LIM-2]'s M1 measurement away from the study's original "closed subgraph"
reading toward measuring [NF25]'s own intermediate-minimization rule
directly (unexplored states pinned as singleton, Hopcroft over the rest).
This lane built `studies/lim2_m1/lim2_m1.c`, an instrument that:

1. Calls the real, unmodified `pcrec_build_dfa` once per pattern (matching
   `lim2_census.c`'s own methodology) and takes the finished raw forward
   machine.
2. **Reconstructs the exact construction timeline post-hoc** from that
   finished structure alone — no live instrumentation, no changes to
   `src/ir/dfa.c` — because the worklist's processing order is provably
   index order (`src/ir/dfa.c:1284`) and `eolvar`/`endvar` provably never
   point forward (checked as a runtime invariant on every population
   member, not merely assumed).
3. At five checkpoints (10/25/50/75/100% of final raw state count) computes
   both the partition-rule block count and the closed-subgraph fraction,
   and at 100% cross-checks its own partition-rule computation against the
   real `pcrec_minimize_dfa`.
4. Ships a failing-direction control (`--sabotage-selftest`) that plants two
   different wrong-block-count bugs and demonstrates the self-check catches
   one of them on the lim2 census's own witness.

Swept over 3,383 pattern blocks (the pcrec `.rxt` corpus + two files named
explicitly by the charter — `tests/base/k18_cost_gates.rxt`,
`tests/counterk/counterk.rxt` — plus a control file
`tests/classes/classes.rxt` + pcrec-bench's `bench/altwide` set, read
directly at `/Users/fdicostanzo/pcrec-bench`, reachable on this box).
**119 patterns** crossed the population's size cuts (raw table entries
`> 65535`, matching lim2_census's own population, **or** raw states
`> 1000`, the broader cut this lane's brief asked for) or were
force-included by name. Full sweep: 58 seconds wall on a quiet box, zero
FAIL lines.

## Findings (full detail: `docs/dev/lim2_m1_partition_measurement.md`)

1. **Monotonicity: REFUTED.** 30/119 patterns (25.2%; 8/34 restricted to
   the large-DFA tail) show the partition-rule intermediate block count
   *exceeding* the true minimized count at some checkpoint before 100%, by
   up to **3,001×** on one witness. The census witness itself
   (`k18_cost_gates.rxt:66`, 27,575 raw → 1,010 minimized) exceeds by over
   10× at both the 50% and 75% checkpoints. **The raw partition-rule count
   is not usable as a naive lower bound for N2's successor design.**
2. **A/N2 re-ranking: confirmed, quantitatively, across the whole
   population.** The closed-subgraph fraction never exceeds 14.3% at any
   checkpoint before 100% anywhere in the 119-pattern population, and stays
   under a few hundredths of a percent on every pattern with substantial
   shrinkage — confirming candidate A is dead and N2 (closed-subgraph lower
   bound) is vacuous on this population, per the study's own stated bar. At
   the same time, the partition rule's own "already-merged" fraction reaches
   33-49% on the census witness at the same checkpoints where the closed
   fraction reads under 0.01% — the measured, numeric form of §6.6 item 4's
   "too pessimistic" finding about the study's original A/N2 reasoning.
3. **The B-vs-C implication is stated as evidence, not a recommendation**
   (§5 of the memo), per the manager/Frank ruling the brief quotes: the
   choice is theirs, on this measurement plus M2 (not chartered here).

## Escalations / open items

- **M2 (the dominance prize, candidate B) was not chartered for this lane**
  and nothing here measures it. §5.1 step 3/§6.6 item 3's B-first revision
  of the recommendation still needs M2 to size B.
- **Reverse and anchored machines are unmeasured** — this lane, matching
  `lim2_census.c`'s own scope, measured the forward machine only. A
  straightforward re-run of the same instrument against `pcrec_build_dfa`'s
  reverse call (`prune=false`) would extend it; not done here (box-time
  budget went to population breadth on the forward machine).
- **No rulings file appeared during the run**
  (`docs/dev/lanes/m1part_rulings.md` was polled twice, before the sweep and
  after the memo draft — absent both times); nothing needed a mid-run
  course correction.
- **No sabotage witness was found for `SAB_DROP_CLASS0`** among the
  patterns this lane happened to try — it demonstrated no effect on the k18
  witness. `SAB_SKIP_ACCEPT` demonstrably catches a planted bug on the same
  witness, which discharges the "checked in the failing direction" method
  rule; `SAB_DROP_CLASS0` is left in the instrument as a second control that
  simply did not bite on the witnesses tried, reported rather than removed.

## Deliverables, all on `lane/m1part`

- `studies/lim2_m1/` — `lim2_m1.c` (the instrument), `Makefile`, `README.md`,
  `CLAUDE.md`, `run_m1.sh`, `m1_data.tsv` (119 rows), `m1_summary.txt`
  (population accounting).
- `docs/dev/lim2_m1_partition_measurement.md` — the memo.
- `docs/dev/nf25_notes_for_authors.md` — dated bullet appended in the same
  change as the memo.
- `studies/CLAUDE.md` — updated for the new directory.
- `.gitignore` — one line added (`studies/lim2_m1/lim2_m1`, matching the
  existing `studies/lim2_census/lim2_census` precedent) so the built binary
  is not accidentally tracked.
- This file.

Not touched: `docs/dev/plan.md` (the manager owns STATE tags, per the
brief), anything under `src/` or `tests/`, anything in pcrec-bench (read
only, via its own real files at `/Users/fdicostanzo/pcrec-bench`).
