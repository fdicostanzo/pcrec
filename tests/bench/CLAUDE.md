# tests/bench — throughput and compile-time budget suite

`make bench`. Guards R1 A-2 (linearity) and A-3 (compile time) plus the
optimizations whose removal is behavior-preserving and therefore invisible to
`make test`. Budgets are absolute pcrec numbers, not ratios against other
engines — the cross-engine matrix lives in compare/.

## Files

- **run_bench.sh** — the suite: COMPILE-SPEED, KEYWORD-SCALE (and a classes
  variant), GCC-TIME, THROUGHPUT cases (a)-(e) + the linearity check. Every
  budget and timeout is env-overridable; the block near the top records the
  measured median behind each default.
- **bdriver.c** — driver compiled against the generated matcher; prints
  `bytes= iters= secs= mbps=` and the match span.
- **compare/** — cross-engine comparison matrix vs PCRE2 (interp and JIT) and
  python `re`, plus its own ratchet. Slow (tens of minutes); not part of
  `make bench`.

## Conventions

Budgets are measured-median/1.75 (D12) unless the case documents a tighter
number and says why. Every measurement is pinned (`taskset`) and repeated
`BENCH_TRIALS` times with the MEDIAN judged and the max/min spread printed. A
budget miss on a box whose 1-minute load exceeds `LOAD_LIMIT` is reported as
INCONCLUSIVE and exits 2 — "clean" and "not measured" are different results
(D14).

**Every case must exercise something no other case does, and that has to be
demonstrated by sabotage, not asserted** (D15). Two cases here exist only
because a critic proved the suite was blind: (d) covers the BITMAP half of the
start prefilter — (a)-(c) all take the memchr branch — and (e) covers self-loop
skip states, which had no throughput coverage anywhere, all four earlier
patterns emitting zero skip tables. Case (e) additionally hard-errors if its
pattern stops emitting a skip table, so it cannot decay into a second
prefilter measurement.

Watch for the R2-B4 trap when adding a case: a pattern that MATCHES early exits
early, and then "MB/s" is exit latency rather than scan rate. `.*=.*` over
key=value text reads 32 GB/s for exactly this reason and is why case (e) uses a
pattern that cannot match.

Maintenance: update this file when cases or budgets are added/removed.
