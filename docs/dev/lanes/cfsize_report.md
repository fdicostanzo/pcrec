# cfsize: why NEST8 moved from K=1 to K=2 after K128 (STOPPED under the stop rule)

Lane cfsize (opus, 2026-10-22), on `lane/corefix` @ 1a7ae633c. Rulings read:
R1, R2 (`corefix_rulings.md`). **No source or test file changed.** The stop
rule fired: the model is right, and K=1 is excluded by a measure the spec
values, the declared-capacity floor (`docs/design/artifact_size_term.md`
§3.3a). It is not excluded by the node count.

## 1. Premise reproduced

NEST8 = `((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}`.
- Branch: `RX_UNROLL_K 2`, why `size-model`.
- Main 22ef344ce: `RX_UNROLL_K 1`, why `size-model`.

## 2. The node accounting is NOT the cause

`vm_emitted_nodes` (`nlabel`) ranks the rungs the same way as the bytes do, on
both trees. Labels and bytes per K:

| K | main labels | main bytes | lane labels | lane bytes |
|---|---|---|---|---|
| 8 | 1471 | 279,115 | 1567 | 290,474 |
| 4 | 799 | 152,825 | 847 | 158,380 |
| 2 | 498 | 92,184 | 522 | 94,953 |
| 1 | 262 | 48,940 | 270 | 50,035 |

K=1 is still the node argmin (`best_free`).

## 3. The cause: the capacity floor removes K=1

`subject_ceiling` per K is 18 on every rung on both trees, except **lane K=1,
which declares 17**. `size_term_choose` applies the floor first, so K=1 is no
candidate. The next node argmin, K=2, passes the 25% bar (94,953 <= 0.75 x
290,474) and ships with why `size-model`.

The ceiling is min(2048 / pf, 3072 / pt). An instrumented scratch copy of
`vm_plan_capacities` (built in `build/cfsize/`, not committed) printed the
whole-pattern Cost. pf = 111 on every row, so 2048 / pf = 18.

| K | base trail | base pt | lane trail | lane pt | lane 3072 / pt |
|---|---|---|---|---|---|
| 8, 6 | 102 | 56 | 150 | 81 | 37 |
| 4, 3 | 108 | 59 | 156 | 84 | 36 |
| 2 | 134 | 73 | 182 | 98 | 31 |
| 1 | 287 | 149 | 335 | **174** | **17** |

K128 adds ONE trailed write per entry to the nullable `+` (the seed of the
last mandatory iteration's guard), on every rung. Through the enclosing
bounded repeats (`pt = body.trail + body.pt`), that one entry becomes +25 pt at
every K. Only K=1 crosses 3072 / 18 = 170.7, because K=1 was already 93 pt
heavier than K=8 on main.

Why K=1 was heavier: at K=1, `vm_counter_fits` sends the `+` (rmin 1 >= K 1)
to the COUNTER rung. Its init write and one per-trip write add 2 trail entries
per entry to the `+`.

## 4. The model prices the seed correctly

The seed must be trailed. Take the `+` nested in an outer loop, with an
UNtrailed seed:
1. Outer iteration 2's seed overwrites the slot.
2. A backtrack returns into outer iteration 1's last mandatory copy, after
   its star ran no iteration.
3. Unwinding leaves the slot at iteration 2's value.
4. The star's entry test then reads the wrong position.

So each entry to the `+` costs one trail entry, and that is exactly what the
model charges:
- frames rung: +1;
- counter rung: one per trip, `mm / K` with no residue, else 1. At m = 1,
  K = 1 that is 1, matching the one trip the emitter writes.

K=1 really does declare less capacity (17 < the default's 18). Under §3.3a it
is not a candidate. K=2 is the smallest rung that keeps capacity.

## 5. A general fix exists, but it is outside R1's movers and needs a ruling

`vm_counter_fits`' own comment says "`X*` and `X+` therefore never reach this
rung — their rmin is 0 or 1". The predicate `rmin >= unroll_k` breaks that
claim at K=1, so at K=1 every `X+` takes a one-trip counter. That costs 2 trail
entries and buys no size.

I measured an unbounded clause `rmin >= K && rmin >= 2` in the scratch copy:

| tree | K=1 pt | K=1 ceiling | chosen K | bytes |
|---|---|---|---|---|
| lane | 124 | 18 | **1** | 48,303 |
| main | 99 | — | — | 47,385 |

On the lane this beats the current K=1 (50,035) and main's 48,940.

It moves bytes on every K=1 artifact with an unbounded rmin=1 repeat (`--unroll=1`
or ladder-chosen), on main too. That is outside R1's K128/K129 shapes, so it was
NOT built. If ruled in, it is a small emitter change plus a census job. S191 and
run_size_term §3 would then pass unchanged.

## 6. Reach job (R2's second half): prepared, not queued

`build/cf/jobs/712-cfsize-reach` (gitignored) is the corrected job:
- Base: a real git worktree `worktrees/cfsize-base` at a53296894. The script
  header has the `git worktree add --detach` and build lines; wtprune target
  `cfsize-base`. Not created yet.
- Count: the matrix's own "NOT declared UNREACHED" list, cross-checked against
  the trailer's `unreached=`. On the old lane log it yields exactly S191.

Not queued: until the K question is ruled, it can only re-report S191.

## 7. State at handoff

- Rulings: last entry applied is R2 (stop rule).
- Queue at handoff:
  - 704-corefix-test was RUNNING when this lane started, so it was left alone.
    Expect red in test-codegen (run_size_term §3).
  - 704-corefix-mech is pending and still valid; it does not depend on the K
    question.
- Nothing re-queued: no fix to validate.
- Owed after a ruling:
  - (a) Option of §5: build, census, then queue 712-cfsize-test, -mech (+S191)
    and -reach.
  - (b) Accept K=2: re-pin run_size_term §3, S191's REACH_EXPECT / DOC_FIGURE,
    and the docs of S192/S701 that name NEST8's K.
