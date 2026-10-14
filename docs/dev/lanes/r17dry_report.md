# r17dry — R-17 revision 2 harness: compile, check, dry run (2026-10-12)

Branch lane/r17dry (from lane/memfn-r17). All runs pinned `taskset -c 12-15`,
under `gnutimeout`, scratch in `build/scratch/`. No timing was taken (one
format smoke of the timer at n=4096, R=1, -m 1; numbers discarded).

## Result: ready to run; no design finding

## Compile
- `gen_twins_r2.py` renders `twins_r2_gen.h` (7548 lines), rc 0.
- `check_r2.c`, `check_r2.c -DPLANT_STALE`, `time_r2.c`: `gcc -O2 -fPIC -Wall
  -Wextra` clean, zero warnings (the script itself uses no -Wall/-Werror).
  `summarize_r2.py` runs on a smoke `times.tsv`.

## Fixes (harness source only)
1. `check_r2.c:56-61` — `NMAX` below 129 overflows `buf` in F2 (n = 129
   subjects; glibc fortify aborted `-DNMAX=70`). Added `#if NMAX < 129 #error`.
   The default 160 was never wrong.
2. `check_r2.c` `wanted()` + `main(argc, argv)` — OPTIONAL argv cell names
   restrict the run to those cells (reduced run for the sanitizers). No args =
   all, so `run_time_r2.sh` is unchanged.
No script bugs found in `run_time_r2.sh`.

## Sequence check (full size; it is only ~1.6 min, so NMAX stayed 160)
- check: `R17R2 CHECK: twins=190 calls=4037733349 mismatches=0`, rc 0, 98 s;
  every population (cache/fill/back/walk) non-zero for every twin that has the
  mechanism (adapt_swar/avx2 cache=fill=0 by design, walk > 0).
- planted: `mismatches=559914856 (PLANTED stale state)`,
  `R17R2 PLANT: cache twins caught = 152 of 152`, rc 0, 94 s. The control
  detects stale state on every cache twin; the run is valid.
- No stateful-vs-stateless-vs-byte-loop mismatch: no finding.

## ASan+UBSan (`-O1 -g -fsanitize=address,undefined
-fno-sanitize-recover=undefined`, `check_r2_san adl syn4 x80`)
`twins=30 calls=684637800 mismatches=0`, rc 0, 75 s, zero sanitizer reports
(guard pages on both sides are in the check, so a read-overrun would fault).

## Dry run (`DRYRUN=1 L=<scratch> CORE=12 bash run_time_r2.sh`)
rc 0; prints the three gcc lines, the two check lines, 619 `time_r2`
invocations, one perf line (126 runs), and
`R17R2 TIMING COMPLETE rc=0 rows=0 void=0 perf=dryrun`.
Invocations: 14 real cells (adl qdm alt2 alt2r bkn bpr sig tki kel hbr hbrc
u8l dig lc) x 41 = 574, + 5 synthetic x 9 = 45, = 619.
Every flag used (-c -r -n -p -k -g -L -A -R -m) is accepted by `time_r2`; every
one of the 19 cell names runs; the output header is `cell form regime n ppm
span reset g align calls_per_iter ns_per_call_min ns_per_call_med
ns_per_byte_min d_floor_ns_min ppm_meas run_mean ck`, 15-16 rows per
invocation (floor + 14-15 forms; adl 16). No `VOID` in the smoke. Note: the
dry run skips rendering the twins (the `run` wrapper), so it proves the
enumeration, not the compile; the compile is above.

## Full-run command and completion line
    L=$PWD/build/scratch/r17full CORE=<cpu> nohup bash \
      docs/design/memfn/probes/r17/run_time_r2.sh > $L.log 2>&1 &
(`SUBJ_TSV=<file>` optional for real subjects.) Last line:
`R17R2 TIMING COMPLETE rc=N rows=K void=V perf=P` — expect rows ~ 619 x 15.4
= ~9.5k, void=0, perf=126. rc 3/4 = check red / planted check missed.

## Wall estimate (arithmetic, no timing)
Per row: calibration (doubling to >= 50 ms, ~<= 100 ms) + 7 x 50 ms ~ 0.45-0.5
s; per invocation 15.4 rows ~ 7.2 s; 619 x 7.2 = ~74 min (60-90). Plus check
98 s + planted 94 s + perf 126 short runs (~3 min) -> ~80 min total
(65-100), below the design's 1 h 45 min, which stands as the upper bound.
R=5 MIN_MS=30 would be ~35 min.

## Blockers
None. perf is installed; `perf_event_paranoid` = 2 and `perf stat -e branch-misses
true` counts (`branch-misses:u`), so the branch pass will run.
