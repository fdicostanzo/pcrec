# l3mechtri report

## Summary
Cloud mech run 45034890369 (shard 64/90, job 137246542483) went red on ONE row,
S501-walk-look-consumes: BUILD-FAILED, an ANOMALY. Cause (b)-family but NOT an
L3 effect: the plant's replacement text was stale since the K147 landing
(04ad1e0ca, already on main), which made `ss_walk` return void with an in/out
accumulator. src/facts/startset.c is byte-identical between main and this branch,
so main fails the same way. Re-aimed the plant (test-only, no C change); S501
reads DETECTED locally. Gather failed only as a consequence.

## Diagnosis
- The shard's test step failed (not infra, not a timeout); its matrix shows 15
  rows DETECTED, S525 UNDETECTED (EXPECTED), and S501 `BUILD-FAILED / ANOMALY`.
- tests/mech/sabotages/S501_walk_look_consumes.sh SAB_AFTER used the old
  by-value form (`StartSet b = ss_walk(cx, a->l, ss_empty()); ... ss_cat(b, &acc)`),
  which no longer compiles against the void `ss_walk(cx, a, StartSet *acc)`.
- `git diff main HEAD -- src/facts/startset.c` is empty: not L3's.

## Fix
tests/mech/sabotages/S501_walk_look_consumes.sh: SAB_AFTER now uses the in/out
signature; a RE-AIMED comment records why. Local proof: build `make -j16` rc=0;
`scripts/boxlock run -- bash tests/mech/run_sabotage_matrix.sh S501` ->
DETECTED (reach ok 1/1, startset 2fail/1pass, vmhat 192fail/18pass, dfahat
23fail/0pass), unexpected 0, anomalies 0, at 3deaa80ff. No allowlist row added.
Note: main carries the same stale row until this commit is merged.

## STATE AT HANDOFF
Branch lane/l3mechtri, committed. Cloud mech dispatched on the tip (owed:
verdict only, via the usual monitors; not waited on). Rulings file empty at the
last re-read.
