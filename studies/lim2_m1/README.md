# studies/lim2_m1/ — the [NF25] partition-rule measurement

[LIM-2] M1 (lane `m1part`, worktree `worktrees/m1part`, branch `lane/m1part`,
2026-09-04, measurement only — nothing under `src/` or `tests/`). Backs
`docs/dev/lim2_m1_partition_measurement.md`, the memo this data feeds.

## What M1 asks

`docs/dev/dfa_online_minimization_study.md` §6.6 item 4 (the M5 finding)
re-scoped M1: measure the yield of [NF25]'s own intermediate-minimization
rule — Hopcroft/Moore refinement run on the PARTIAL forward DFA with every
state whose row is not yet filled ("unexplored") pinned in its own
permanent singleton block — not the study's original §3.5 "closed subgraph"
quantity, because those are proven different sets (two states each carrying
an *unexplored* successor still merge under the paper's rule when it is the
*same* unexplored successor, which the closed subgraph does not count).

This directory's instrument, `lim2_m1.c`, computes BOTH quantities at five
checkpoints during subset construction (10/25/50/75/100% of the machine's
final raw state count) for pcrec's real DFA-route population, and answers
the two questions the charter asks:

1. **Is the partition-rule count a usable LOWER BOUND for a size projection
   (N2's successor design)?** Checked by monotonicity: does the
   intermediate block count ever *exceed* the true minimized count?
2. **How much cheaper would construction be if merges happened at these
   checkpoints** (the Tier-1/Tier-4 "only these make construction cheaper"
   criterion from the study's §3.2)? Stated as an assumption, not built —
   this instrument measures counts, not a merge mechanism.

## How it measures — read the file's own header first

`lim2_m1.c`'s top comment is the full methodology: **post-hoc
reconstruction**, not live instrumentation. It calls the real, unmodified
`pcrec_build_dfa` exactly once per pattern (matching `lim2_census.c`'s own
methodology) and takes the FINISHED raw (pre-minimize) machine, then
replays its own construction history from that finished structure alone —
possible, and exact rather than approximate, because (1) the worklist's
processing order is literally index order (`src/ir/dfa.c:1284`,
`for (int si = 0; si < d->n; si++)`) and (2) `eolvar`/`endvar` never point
forward (interned strictly before the base state that references them).
The one place this binary reads something other than `tr[]` to reconstruct
history is the exact seed count, read directly off `d->s0`/`d->s1u[]`/
`d->s1g[]` — no approximation, no "assume 1".

The partition rule itself mirrors `src/opt/minimize.c`'s own signature/
hash-and-dedupe shape, restricted to the "explored" state range and with
"unexplored" targets resolved to a fixed, permanently-unique tag (the
paper's pinned singleton). At the 100% checkpoint this computation
degenerates EXACTLY to what `pcrec_minimize_dfa` computes on the same raw
machine — same signature, same fixpoint — so this binary's own self-check
(below) calls the real minimizer and asserts the two counts agree.

## Failing-direction control

`docs/dev/learnings.md` §3's standing rule: a control that shares a source
with what it controls is the project's most-repeated check-design failure.
This binary's self-check (100%-checkpoint block count == the real
`pcrec_minimize_dfa`'s count) is checked in the FAILING direction via
`./lim2_m1 --sabotage-selftest PATTERN`, which runs the SAME pattern three
ways: honest, with the initial accept-bit split disabled
(`SAB_SKIP_ACCEPT`), and with the class-0 transition column corrupted to a
constant (`SAB_DROP_CLASS0`). MEASURED on the lim2 census's own witness
(`tests/base/k18_cost_gates.rxt:66`, `(1{0,30}?[^]abc][^abc]){28,30}0+|a`):

```
$ ./lim2_m1 --sabotage-selftest '(1{0,30}?[^]abc][^abc]){28,30}0+|a'
honest:            100pct block_count=1010  true_min=1010  MATCH (expected)
sab_skip_accept:   100pct block_count=1006  true_min=1010  MISMATCH (self-check caught the planted bug)
sab_drop_class0:   100pct block_count=1010  true_min=1010  MATCH (no effect on this witness)
```

The honest run matches (this binary's algorithm is right on this witness);
`SAB_SKIP_ACCEPT` is caught (1006 != 1010) — the self-check has teeth.
`SAB_DROP_CLASS0` happened not to matter on this particular witness (its
alphabet's class 0 carries no live distinction the machine needs), which is
itself informative about the population rather than a failure of the
control — the check that has teeth on THIS witness is the one reported.

## Population

Two-phase per pattern (see `lim2_m1.c`'s `block_measure`): a cheap raw-only
build decides inclusion (raw table entries `> 65535`, matching
`lim2_census.c`'s own `PREMUL_MAX_ENTRIES` population, **OR** raw states
`> 1000`, the broader "large-DFA tail" cut this lane's brief asks for —
stated here rather than derived from any existing constant, since no such
threshold exists elsewhere in the tree); only patterns crossing one of those
cuts pay the five-checkpoint partition-rule/closed-fraction cost. Two files
are FORCE-included regardless of size, because the charter names them
explicitly: `tests/base/k18_cost_gates.rxt` (the census witness plus the
nested-counted family) and `tests/counterk/counterk.rxt` (the counted-repeat
differential tower). pcrec-bench's `bench/altwide/patterns/*.rx` set is
read on this box at `/Users/fdicostanzo/pcrec-bench` (read-only; the scope
mandate's second repo) and force-included in full — every `.rx` file is one
pattern, matching that set's own convention.

Every population count (seen, refused, VM-only, below-cut, included,
force-included) is printed on stderr (`m1_summary.txt`) so a population that
quietly shrinks to nothing is visible rather than silently green
(`docs/dev/learnings.md` §3).

Forward machine only, matching `lim2_census.c`'s own scope (its README's
own note; the online-minimization study's §4.2 A3 already names the
reverse machine as unmeasured future work). Extending to the reverse
machine is a straightforward re-run of the same instrument against
`build_dfa`'s reverse call (`prune=false`) — not done here for time budget,
named as the natural next step.

## Files

- `lim2_m1.c` — the instrument. Links the repo root's `build/libpcrec.a`
  (Ctx-internal functions, not self-contained, same precedent as
  `lim2_census.c`). `make CC=gcc-16` builds it.
- `Makefile` — `make CC=gcc-16` builds `lim2_m1`; `make selftest` runs the
  failing-direction control on a small hand-picked witness; `make sweep`
  re-runs the full population sweep via `run_m1.sh` and regenerates
  `m1_data.tsv`/`m1_summary.txt` IN PLACE (does not commit them —
  re-measurement is a deliberate act, `studies/CLAUDE.md`'s own rule).
- `run_m1.sh` — finds the corpus + force files + (if reachable) pcrec-bench's
  altwide set, runs the built binary over the union, writes
  `m1_data.tsv`/`m1_summary.txt`.
- `m1_data.tsv` — the COMMITTED data: one row per population member —
  `id`, `raw_n`, `min_n`, then for each of the five checkpoints
  (`frac`/`T`/`block`/`closedfrac`), then `exceeds_final` (0/1) and
  `max_exceed_ratio` (the worst `block(T)/min_n` ratio seen at any
  checkpoint before 100%).
- `m1_summary.txt` — the population-accounting summary (stderr capture).

## Machine/date context (D35 spirit)

Measured on the project box (macOS arm64, gcc-16), 2026-09-04, against
`lane/m1part` at the commit this study was written on. Re-measure before
load-bearing use elsewhere, per `studies/CLAUDE.md`'s standing rule.
