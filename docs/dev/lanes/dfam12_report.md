# [LIM-2]/dfamin M1+M2 (2026-09-16, lane dfam12, sonnet)

Delivers `docs/dev/dfamin_m1m2.md`, `docs/dev/dfamin_m1m2_evidence/
k25_chain_ladder.rxt`, `studies/lim2_m2/` (a new instrument), and a
measurement-only `[PROBE-M2]` edit to `src/core/internal.h`/`src/ir/nfa.c`/
`src/ir/dfa.c` committed separately per the brief's OPT5M2-PROBE precedent
(does not land — see the memo's §5 and this report's §3).

## What was chartered and what was already done

M1 (the paper's partition-rule yield) was already fully measured by lane
`m1part` on 2026-09-04 (`docs/dev/lim2_m1_partition_measurement.md`), over
119 patterns including the K18 witness and `tests/counterk/`. This lane did
NOT re-measure that — it added the ONE population the brief named that
m1part's own population did not force-include: K25's own chain shapes
(`a{0,N}` and `(?:abcdefghij){N}`), run through m1part's unmodified
instrument. M2 (the dominance prize, candidate B) was never built — the
plan row records it explicitly DORMANT since 2026-09-04 — and is new work
by this lane.

## Headline yields

**M1, K25's chain shapes (new)**: ZERO merge yield anywhere. Every
checkpoint shows `block(T) == T` and `raw_n == min_n` on all seven measured
rows (`a{0,100..25000}`, `(?:abcdefghij){500,1500}`) —
`(?:abcdefghij){3000}` refuses on the 32,000-state cap. Mechanically:
these are strict sequential chains (no epsilon path reaches two different
copies' positions without consuming a byte), so there is genuinely nothing
for ANY compaction candidate (A, A′, B, C, N1, N2) to find. K25's cost is
pure Moore-refinement overhead with zero redundancy behind it.

**M2, the dominance prize (new)**: real but NARROW over the shipped corpus
(1,232 rows measured excluding force files: 14.3% see any drop at all, 4.0%
see real raw-state relief, aggregate K7 charge relief a modest 4.6%), rich
and mixed on `tests/counterk/counterk.rxt` (some rows halve raw state
count; others get up to ~2,000x K7 relief with the raw count completely
UNCHANGED — two separate wins that do not always come together), ZERO on
K25's own chain shapes (same structural reason as M1), and — the sharpest
finding in the whole memo — a REGRESSION on the study's own chartering
witness: `tests/base/k18_cost_gates.rxt:66` goes from a clean 27,575-state
compile to a hard refusal (crosses `PCREC_MAX_DFA_STATES_TABLE`) under the
stand-in. This is `docs/dev/dfa_online_minimization_study.md` §4.3's own
predicted B2 failure mode (the K18 open-loop context breaking a bare-NFA
preorder), now measured concretely rather than argued.

## My B-vs-C read (evidence, not a ruling — see memo §8 for the full argument)

Neither M1 nor M2 supplies a result that would justify building either
candidate now. M1 (both m1part's original population and this lane's K25
addition) confirms candidate C's exact-projection hope stays dead (a
mandatory final Hopcroft pass per M5's own reading of [NF25], regardless of
partition-rule yield). M2 shows candidate B's prize is real only on a
narrow slice of shapes, and is actively harmful — not merely absent-of-benefit,
harmful — on the exact pattern the whole study exists to help, using the
MOST PERMISSIVE possible reading of the mechanism (a stand-in with zero
cost beyond what construction already pays). The honest reading is closer
to the study's own "record a legitimate no" branch than to a B-first
go-ahead; a real verdict on B needs the general context-aware simulation
preorder (never built — forbidden as a landing by the study's own §3.7)
plus the cross-product corpus §4.3 already names as a precondition.

## Disposition of the probe

Committed SEPARATELY (not reverted), clearly marked `[PROBE-M2]`, for the
manager to drop at merge — chosen over reverting because
`studies/lim2_m2/`'s harness links the probe's `extern` counters directly,
and reverting would leave a delivered, non-reproducible study directory.
Byte-identity confirmed: with `PCREC_PROBE_M2` unset (every build this tree
has ever produced), four representative patterns' emitted C
(`--emit-main`) are identical between a scratch build from the exact
probe-free branch point and this lane's tip, modulo the known
same-basename `#include` artifact. `make strict CC=gcc-16` is clean on the
probe-bearing tree.

## Validation

- `make strict CC=gcc-16`: clean.
- M1's own self-check (`lim2_m1 --sabotage-selftest`) still reports
  `honest: 100pct block_count=1010 true_min=1010 MATCH` on this lane's
  rebuilt `libpcrec.a` — the probe's added `NState` fields do not disturb
  it.
- M2's own sanity control: `(?:a|){0,1}` (no coexistence possible) measures
  zero drops; `(?:a|){0,3}` (a hand-argued nullable-body case where three
  copies' leaf positions genuinely coexist in one closure) measures
  nonzero drops in the predicted direction, `raw_n` 4→2. Direction and
  mechanism hand-verified exactly; the tool's own aggregate counters are
  read from the instrument rather than independently re-summed (stated
  explicitly in the memo rather than glossed over).
- No `make test`/`mech`/battery run — out of scope for a measurement-only
  lane touching no shipped behavior.

## Not done / explicitly out of scope

- No timing claims anywhere (D77 — a mechanism is not built here).
- Reverse and anchored machines unmeasured by either M1 or M2 (forward
  only, matching m1part's own precedent).
- The general, context-aware simulation preorder candidate B actually
  specifies was never built — only the study's own named illegitimate
  stand-in, and its K18 regression is evidence against the NAIVE form, not
  a measurement of the general one.

PARKED on `lane/dfam12`. Not merged. END.
