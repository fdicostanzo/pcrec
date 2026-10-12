# docs/design/endmark/b3rev/timing/ — the B3 walk's emitted form, measured

Sub-lane of lane b3rev (2026-10-12): [REVEND-WALK-FORM] (which emitted form the
B3 build's one-seed walk takes) and D164 addendum 4's lowered tie finishers.
Nothing here is built or run by `make`. Run the Python with `python3 -I` and
`PYTHONDONTWRITEBYTECODE=1`. It imports `../../b3meas/gen.py` (never edits it)
for the population, the machine probe, the tagged product, the B3 twin, the
restyled control R, the load instrumentation and the subjects.

Environment (the b3meas import needs all of it; `PROBE` is not used):

    S=build/scratch/b3revtime
    export PCREC=build/pcrec B3PROBE=$S/b3meas_probe OUT=$S TMPDIR=$S/tmp \
           PROBE=/nonexistent BENCH=/home/pcrec/projects/pcrec-bench CORPUS=. JOBS=8 CPU=2
    gcc -O1 -Ilib -Isrc docs/design/endmark/b3meas/probe.c build/libpcrec.a -o $S/b3meas_probe

- `gen.py` — the driver.
  - `ebuild [k,...]` builds per artifact the E arms (T today, A its A/A copy,
    R b3meas's plain-style control, V = R + today's per-byte view probe,
    S = R + today's stay placement, U = today's text with the one-seed rule,
    P = the one-seed rule in R's style, W = P with the first step peeled; on tie artifacts R, B = b3meas's
    tagged twin, Q = B in today's step shape), answer-checks every arm but A
    against libpcre2 10.46 (exhaustive every-startpos cells to length 5 + the
    regime subjects, loads counted) and builds the TIME binary from the arms
    with no wrong answer. Writes `results/echeck.json` (env `EOUT` renames it).
  - `etime [k,...]` times each artifact's arms pinned (`taskset -c $CPU`),
    printing `k regime n iters arm median min` rows (env `CLS` filters
    notie/tie).
  - `abuild [k,...]` builds part A per tie artifact: T/A (`X$`, `_match`),
    L (`X(?:\n)?\z` lowered with b3meas's `cost.rv` rewriter, no mark), and
    N/M/K the same three with `-fno-rev-end` (`_search` from s*), checks them
    (`aharness.c -DCHECK`) and records forward/anchored/reverse state counts
    read off the emitted arrays. Writes `results/acheck.json`.
  - `atime [k,...]` times part A (`atime` rows).
- `harness.c` — the E check (`-DCHECK`, links libpcre2-8) and timing
  (`-DTIME`) driver over the arm list in a generated `vars.h`.
- `aharness.c` — part A's check and timing driver.
- `report.py` — aggregates the JSON and TSVs into `results/report.txt`:
  `python3 -I docs/design/endmark/b3rev/timing/report.py > docs/design/endmark/b3rev/timing/results/report.txt`
  - `e1` writes `results/e1_census.json`: which of today's form elements each
    T walk carries, and R's run-skip coverage.
- `results/` — `echeck.json` (run 2's build, arms incl. W), `run1_echeck.json`
  (run 1's, no W), `acheck.json` (answers, loads, states), `e1_census.json`,
  `run{1,2}_etime_c*.tsv` (E timing: c0-c2 no-tie, c3 tie; rows `k regime n
  iters arm median min`), `run{1,2}_atime.tsv`, `report.txt` (run 2, with run 1
  agreement) and `report_run1.txt` (`RUN=run1`).

Each run was a background chain (`$S/tchain.sh` / `$S/chain2.sh`, logs
`$S/tchain.log` / `$S/chain2.log`): every chunk its own process, under 4 min,
pinned `taskset -c 2`. The box carried other lanes' load (load average 6-18)
during both runs; read every ratio against its A/A column.
