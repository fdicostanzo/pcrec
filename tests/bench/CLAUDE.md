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

Budgets are SUPPOSED to be measured-median/1.75 (D12). Four of the nine are not,
and saying otherwise is a claim this project has now made three times and
refuted twice — so here is the actual table, from the budget and the `measured`
comment on the same line of run_bench.sh:

| budget | value | measured | slack |
|---|---|---|---|
| COMPILE_BUDGET_SECS | 0.4 s | 0.111 s | 3.60x |
| GCC_O1 / GCC_O2 | 2 s | 0.219 s | 9.13x |
| NEEDLE (a) | 1200 | 2160 | 1.80x |
| NOMATCH (b) | 12000 | 21910 | 1.83x |
| ALT (c) | 1000 | 1753 | 1.75x |
| BITMAP (d) | 330 | 429 | 1.30x (documented tighter, on purpose) |
| SKIP (e) | 1000 | 1741.8 | 1.74x |
| LINEARITY | 6.0 | 2.883 | 2.08x |

The GCC budgets sit inside the "9x-300,000x loose" band D12 opens by condemning.
Tightening them is [R3.8]; until then, do not describe this suite as "all
median/1.75". Every measurement is pinned (`taskset`) and repeated
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
