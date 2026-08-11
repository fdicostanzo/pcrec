# tests/bench

## If subject generation fails, it is DISK and probably not free space

`run_bench.sh` writes ~120 MB of subjects under `mktemp -d` (5x8 MB + 16 MB +
64 MB). Measured 2026-08-11: on this box `/tmp` is a **tmpfs with a per-user
quota**, so the 64 MB file failed with

    OSError: [Errno 122] Disk quota exceeded

while `df` reported **1.6 GB free**. Reproduced directly with `dd`: 72 MB of
writes succeed, the next 64 MB does not. Free space is the wrong thing to look
at; the user's total tmpfs usage is.

**The fix that does not touch anyone else's data:** run bench with `TMPDIR`
pointed at a real filesystem — `TMPDIR=/var/tmp make bench` — which is where
the PARSE-1 numbers were taken. Deleting accumulated scratch under `/tmp` also
works but is somebody else's session data.

This is a HARNESS FAILURE and the script counts it separately from a budget
failure for exactly this reason: `hard errors: 1 / budget failures: 0` means
the benchmark did not run, NOT that performance regressed. Do not read a green
`budget failures: 0` on such a run as a pass.
 — throughput and compile-time budget suite

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

Budgets are SUPPOSED to be measured-median/1.75 (D12). Two of the nine are
not, and saying otherwise is a claim this project has now made three times
and refuted twice — so here is the actual table, from the budget and the
`measured` comment on the same line of run_bench.sh. Refreshed [R3.8]
(2026-08-11) with a real quiet-box multi-run median (six independent
`run_bench.sh` invocations, 1-min load 0.9-2.6 throughout, well under
`LOAD_LIMIT`) for every row that changed:

| budget | value | measured | slack | status |
|---|---|---|---|---|
| COMPILE_BUDGET_SECS | 0.4 s | 0.114 s (median of 6) | 3.51x | loose, deliberately (see below) |
| GCC_O1 | 2 s | 0.214 s (8192-state pattern, the binding one; median of 6) | 9.35x | loose, deliberately (see below) |
| GCC_O2 | 2 s | 0.222 s (8192-state pattern, the binding one; median of 6) | 9.01x | loose, deliberately (see below) |
| NEEDLE (a) | 1200 | 2160 | 1.80x | at target |
| NOMATCH (b) | 12000 | 21910 | 1.83x | at target |
| ALT (c) | 1000 | 1753 | 1.75x | at target |
| BITMAP (d) | 330 | 429 | 1.30x | tighter, on purpose (documented in run_bench.sh) |
| SKIP (e) | 700 | 1258.7 (median of 5 independent runs, 2026-08-11) | 1.80x | RETUNED to target [R3.9] — was 1000/1741.8 (1.74x) against a subject that has since changed |
| LINEARITY | 6.0 | 3.731 (median of 6) | 1.61x | NOT loose — see below |

Two genuine exceptions remain, both explained (not just measured) by [R3.8]:
**COMPILE-SPEED and GCC-TIME are single-sample measurements.** Unlike
THROUGHPUT, which takes `BENCH_TRIALS` (5) trials and judges the median, these
two sections time ONE pcrec/gcc invocation per `run_bench.sh` run. That is not
a theoretical gap: six same-day quiet-box runs measured the 8192-state
pattern's `gcc -O1` compile at 0.119s to 0.223s — a 1.87x swing on a single
sample, with no other trial in that run to average against. Tightening to
/1.75 on data this noisy would trade a documented-but-honest looseness for a
plausibly flaky gate, which the project's own LOAD_LIMIT rationale calls out
as worse (a flaky budget gets widened permanently, not fixed). COMPILE-SPEED's
own six-run spread was much tighter (0.112-0.117s, ~1.04x — plausible, since
it is pure in-process work with no forked toolchain), so it is a better
tightening candidate than GCC-TIME, but neither has been touched: giving both
sections a real `BENCH_TRIALS`-style median is an infrastructure change that
should land BEFORE either budget is tightened, not after.

**LINEARITY turned out not to be an exception at all.** The previous "2.08x
loose" figure came from a "measured 2.883" reference that sits BELOW the
theoretical linear ratio of 4.0 (64MB is 4x the work of 16MB) — that is what a
lucky low sample looks like, not a real baseline. LINEARITY's own check IS
BENCH_TRIALS-protected (it reuses `run_bdriver`), so a fresh six-run median of
3.731 is a genuine median of medians, and 6.0/3.731 = 1.61x sits close to the
1.75x target rather than 2x looser than it.

**SKIP (e) was retuned, not just re-measured**, because [R3.9] changed its
subject: the old design only exercised the FORWARD self-loop skip machine (its
subject never matched, so the REVERSE skip loop — this engine scans forward
for the match end, then backward for the start — never ran at all). The new
subject, `'=' + 'a'*(n-2) + '!'`, forces both directions through their skip
tables almost end to end (verified with a debug counter, not by timing: the
forward and reverse skip loops each iterate 8,388,606 times over the 8 MB
subject), and re-sabotage-tested at 173.1 MB/s (median of 5) against a healthy
1288.7 MB/s (median of 5) — a 7.4x regression, larger than the 4.8x the old
forward-only subject caught, because sabotage now costs both directions.

Every measurement is pinned (`taskset`) and repeated `BENCH_TRIALS` times with
the MEDIAN judged and the max/min spread printed (except COMPILE-SPEED and
GCC-TIME, per the exception above). A budget miss on a box whose 1-minute load
exceeds `LOAD_LIMIT` is reported as INCONCLUSIVE and exits 2 — "clean" and
"not measured" are different results (D14). [R3.10] closed the gap where only
the START-of-run load was sampled: `run_bench.sh` now re-samples load AFTER
the measurements too and retroactively downgrades any live FAIL to
INCONCLUSIVE if either sample was over the limit.

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
