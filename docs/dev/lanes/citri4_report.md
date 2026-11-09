# citri4 — CI timeout on main, run 42542841971 (test 3/3)

## Summary
Not a hang and not a product bug. Shard 3 was killed by the 65-minute step
timeout while running its LAST substantive section (test-subst-d27), with every
earlier section green. Cause: a slow hosted runner on top of a shard that was
already the longest. Fix: table re-balanced from the latest green run's
measured seconds, step timeout 65 -> 75 (job backstop 80 -> 90).

## Timings
Log fetched from job 128921370487 (scratch/citri4/j3.log). Step started
00:56:39, cut 02:01:51 (65.2 min). No FAIL, no `*** [test-` error line; the log
shows normal PASS output until 01:56:15, then the cut inside test-subst-d27
(started 3519.7 s in; it takes 379-417 s when green, so the shard needed
~3950 s).

Shard-3 section walls (s), same code (c857164fe is docs-only on 550e23364):

| section | 42525179207 | 42535444227 (550e) | 42542841971 (cut) |
|---|---|---|---|
| test-codegen | 372 | 405 | 500 |
| test-assertions | 304 | 346 | 432 |
| test-anchored-match | 322 | 347 | 459 |
| test-compound | 482 | 535 | 634 |
| test-subst | 66 | 58 | 75 |
| test-subst-d27 | 396 | 379 | cut at ~392 |
| shard total | 2986 | 3209 | >3912 |

Same-run, other shards: 1/3 finished in 1969 s (green run: 2818 s), 2/3 in
2368 s (green: 3360 s), so the same tree ran 0.7x on two runners and ~1.23x on
the third. Recent shard-3 job wall: 55 / 65 / 54 / 50 min green, then the kill.
Growth is not the cause: 550e (green) and c857 differ only in docs.

## Cause
Runner spread. Shard 3 ran ~1.23x slower than its own previous green run
(every section, uniformly) while shards 1 and 2 ran faster. The table weights
(from run 40465053309) were stale: the actual green walls were 47 / 56 / 53 min
for shards 1/2/3, so shard 3 had little margin under a 65 min cap (53.5 min
green at 550e, i.e. only 1.21x).

## Fix
- tests/ci/shards.tsv re-balanced with tests/ci/shard_rebalance.py --write from
  the three sections.tsv artifacts of the all-complete green run 42535444227:
  3128 s per shard (52.1 min), from a measured 2818/3360/3209. `make
  test-ci-shards` PASS (9 checks).
- .github/workflows/ci.yml: step timeout-minutes 65 -> 75 (about 1.45x on the
  balanced ~52 min; spread seen 1.25-1.3x), backstop 80 -> 90, basis in a
  comment. docs/testing.md "CI" paragraph updated.
No local suite run (evening hold); CI on the push is the check.

## STATE AT HANDOFF
Committed on lane/citri4, not merged or pushed. Last rulings entry applied:
none (file empty). Owed: CI run on the push (watch all three shards finish near
52 min). Scratch: /var/tmp/pcrec-pcrec/scratch/citri4/ (log, artifacts).
