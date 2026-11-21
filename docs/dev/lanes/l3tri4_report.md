# l3tri4 report

## Summary
Cloud run 44883167489 (l3tri3-test @ 0375a8bae) red on shard 6 only: `delegated` row MLINE never rendered
(rule 2 reach) and rule 5 (MLINE lists DFA_ATTEMPT, nothing stated it). Class (a), but NOT a shard-partition
artifact: the failure reproduces locally, unsharded (`make test-memfn-manifest`, rc=2, same two FAILs). No src/ edit.

## Cause
`tests/memfn/site_census.py` `corpus_patterns` samples the corpus by position (every Nth unique pattern, N =
count // 300). The new `l3d27_witnesses.rxt` added patterns, shifting N and the alignment, and the sample dropped
its last MLINE-reaching pattern. Whole-corpus scan with the traced binary: 33 unique patterns reach MLINE
(e.g. `(?m)^item` in tests/litscan/handoff.rxt, `(?m)^a+b` in tests/possessify, `(?m)^ERROR(?:(?=\n)|\z)` in
tests/ucp/ctxnode.rxt); none were in the new sample, so MLINE was reached before only by stride luck.
Same cause as l1tri2's DFA_HAT fix (3e23df7e3, one prior patch in 14 days; that commit added the
CORPUS_WITNESSES mechanism for exactly this). The shard-partition lead was wrong: shard 6 runs the whole
check; the other shards do not run it.

## Fix
One row in `CORPUS_WITNESSES`: `(?m)^item` (MLINE/DFA_ATTEMPT). Result: `make test-memfn-manifest` rc=0, 302
patterns sampled, 552 compiled. Tried and discarded: hash-of-text sampling (stable against edits) still missed
MLINE and newly missed PRE/DFA_ATTEMPT, so it only moves the luck; not kept. Scope note for the manager: any
manifest kind with few witnesses is exposed to the same shift; each such kind needs a witness row when it
goes red, or a deliberate redesign (witness per kind derived from the manifest) if it recurs a third time.

## Validation dispatched
Local: `make test-memfn-manifest` green after the fix (red before). Cloud run l3tri4-test dispatched as the
last act (see handoff).

## STATE AT HANDOFF
Rulings file: none present (no R-n applied). Branch lane/l3tri4 off 517e56d81. Owed: none beyond the cloud
verdict (key l3tri4-test).

OWED: none
